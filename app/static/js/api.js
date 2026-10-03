// Shared helper: talks to the backend API and manages the login token.

const API_BASE = "http://127.0.0.1:8000";

function getToken() {
  return localStorage.getItem("token");
}

function getRole() {
  return localStorage.getItem("role");
}

function saveSession(token, role) {
  localStorage.setItem("token", token);
  localStorage.setItem("role", role);
}

function clearSession() {
  localStorage.removeItem("token");
  localStorage.removeItem("role");
}

function logout() {
  clearSession();
  window.location.href = "/login";
}

// Redirects to login if not authenticated; call at the top of protected pages.
function requireAuth(expectedRole) {
  const token = getToken();
  const role = getRole();
  if (!token) {
    window.location.href = "/login";
    return false;
  }
  if (expectedRole && role !== expectedRole) {
    window.location.href = "/login";
    return false;
  }
  return true;
}

// Generic API call wrapper. Adds the Authorization header automatically.
async function apiFetch(path, options = {}) {
  const headers = options.headers || {};
  const token = getToken();
  if (token) headers["Authorization"] = "Bearer " + token;
  if (options.body && !(options.body instanceof URLSearchParams)) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(API_BASE + path, { ...options, headers });

  if (response.status === 401) {
    clearSession();
    window.location.href = "/login";
    throw new Error("Session expired");
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = Array.isArray(data.detail)
      ? data.detail.map((d) => d.msg).join(", ")
      : data.detail || "Something went wrong";
    throw new Error(message);
  }
  return data;
}

function showAlert(el, message, type = "error") {
  el.textContent = message;
  el.className = "alert show alert-" + type;
}
// ---------- Pakistan time & date helpers ----------
const PK_TZ = "Asia/Karachi";

// Server timestamps are UTC without a timezone marker; add "Z" so the browser reads them as UTC.
function parseServerDateTime(value) {
  if (!value) return null;
  const s = String(value);
  const hasZone = /[zZ]$|[+-]\d\d:\d\d$/.test(s);
  return new Date(hasZone ? s : s + "Z");
}

// Timestamp -> "2:30 PM" in Pakistan time
function formatPKTTime(value) {
  const d = parseServerDateTime(value);
  if (!d) return "—";
  return d.toLocaleTimeString("en-US", { timeZone: PK_TZ, hour: "numeric", minute: "2-digit", hour12: true });
}

// Today's date in Pakistan as YYYY-MM-DD
function todayPKT() {
  return new Date().toLocaleDateString("en-CA", { timeZone: PK_TZ });
}

// "2026-09-28" -> "Mon, 28 Sep 2026"
function formatDate(dateStr) {
  if (!dateStr) return "—";
  const [y, m, d] = dateStr.split("-").map(Number);
  const date = new Date(Date.UTC(y, m - 1, d));
  return date.toLocaleDateString("en-GB", { timeZone: "UTC", weekday: "short", day: "numeric", month: "short", year: "numeric" });
}

// "14:30:00" -> "2:30 PM"
function formatTime12(timeStr) {
  if (!timeStr) return "—";
  const [h, m] = timeStr.split(":").map(Number);
  const suffix = h >= 12 ? "PM" : "AM";
  const hour12 = h % 12 === 0 ? 12 : h % 12;
  return `${hour12}:${String(m).padStart(2, "0")} ${suffix}`;
}

function toggleAdminMore(e) {
  e.preventDefault();
  document.getElementById("adminMoreMenu").classList.toggle("show");
}
document.addEventListener("click", (e) => {
  if (!e.target.closest(".nav-more-wrap")) {
    const m = document.getElementById("adminMoreMenu");
    if (m) m.classList.remove("show");
  }
});
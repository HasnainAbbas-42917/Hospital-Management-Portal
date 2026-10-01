let notifPollTimer = null;

async function initNotifications() {
  await refreshNotifBadge();
  // Refresh the unread count periodically so the badge stays current
  notifPollTimer = setInterval(refreshNotifBadge, 30000);

  document.querySelectorAll(".notif-bell").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleNotifPanel();
    });
  });

  document.addEventListener("click", (e) => {
    if (!e.target.closest(".notif-bell-wrap")) {
      closeAllNotifPanels();
    }
  });
}

async function refreshNotifBadge() {
  try {
    const notifications = await apiFetch("/notifications");
    const unreadCount = notifications.filter((n) => !n.is_read).length;
    document.querySelectorAll(".notif-badge").forEach((badge) => {
      if (unreadCount > 0) {
        badge.textContent = unreadCount > 9 ? "9+" : unreadCount;
        badge.classList.add("show");
      } else {
        badge.classList.remove("show");
      }
    });
  } catch (err) {
    // Fail silently — badge just won't update
  }
}

function toggleNotifPanel() {
  const panel = document.querySelector(".notif-panel");
  if (!panel) return;
  if (panel.classList.contains("show")) {
    panel.classList.remove("show");
  } else {
    loadNotifPanel();
    panel.classList.add("show");
  }
}

function closeAllNotifPanels() {
  document.querySelectorAll(".notif-panel").forEach((p) => p.classList.remove("show"));
}

async function loadNotifPanel() {
  const panel = document.querySelector(".notif-panel");
  const list = panel.querySelector(".notif-list");
  list.innerHTML = `<div class="notif-empty">Loading...</div>`;

  try {
    const notifications = await apiFetch("/notifications");
    if (!notifications.length) {
      list.innerHTML = `<div class="notif-empty">No notifications yet.</div>`;
      return;
    }
    list.innerHTML = notifications.map((n) => `
      <div class="notif-item ${n.is_read ? "" : "unread"}" onclick="markNotifRead(${n.id}, this)">
        <div class="notif-message">${n.message}</div>
        <div class="notif-time">${timeAgo(n.created_at)}</div>
      </div>
    `).join("");
  } catch (err) {
    list.innerHTML = `<div class="notif-empty">Could not load notifications.</div>`;
  }
}

async function markNotifRead(id, el) {
  if (el.classList.contains("unread")) {
    try {
      await apiFetch(`/notifications/${id}/read`, { method: "PATCH" });
      el.classList.remove("unread");
      refreshNotifBadge();
    } catch (err) { /* ignore */ }
  }
}

async function markAllNotifRead() {
  try {
    await apiFetch("/notifications/read-all", { method: "PATCH" });
    loadNotifPanel();
    refreshNotifBadge();
  } catch (err) { /* ignore */ }
}

function timeAgo(isoString) {
  const d = parseServerDateTime(isoString);
  if (!d) return "";
  const diffMin = Math.floor((Date.now() - d.getTime()) / 60000);
  if (diffMin < 1) return "Just now";
  if (diffMin < 60) return `${diffMin} min ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr} hr ago`;
  const diffDay = Math.floor(diffHr / 24);
  return `${diffDay} day${diffDay > 1 ? "s" : ""} ago`;
}

initNotifications();
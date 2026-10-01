async function loadHistory() {
  try {
    const records = await apiFetch("/attendance/my-history");
    renderHistory(records);
    renderTodayStatus(records);
  } catch (err) {
    document.getElementById("statusLabel").textContent = "Could not load attendance.";
  }
}

function renderHistory(records) {
  const body = document.getElementById("historyBody");
  if (!records.length) {
    body.innerHTML = `<tr><td colspan="4" class="text-muted">No attendance records yet.</td></tr>`;
    return;
  }
  body.innerHTML = records.map((r) => `
    <tr>
      <td>${formatDate(r.date)}</td>
      <td>${formatPKTTime(r.check_in)}</td>
      <td>${formatPKTTime(r.check_out)}</td>
      <td>${r.status}</td>
    </tr>
  `).join("");
}

function renderTodayStatus(records) {
  const today = todayPKT();
  const todayRecord = records.find((r) => r.date === today);

  const statusLabel = document.getElementById("statusLabel");
  const statusTime = document.getElementById("statusTime");
  const checkInBtn = document.getElementById("checkInBtn");
  const checkOutBtn = document.getElementById("checkOutBtn");

  if (!todayRecord) {
    statusLabel.textContent = "You have not checked in today.";
    statusTime.textContent = "";
    checkInBtn.style.display = "inline-flex";
    checkOutBtn.style.display = "none";
  } else if (!todayRecord.check_out) {
    statusLabel.textContent = "Checked in at";
    statusTime.textContent = formatPKTTime(todayRecord.check_in);
    checkInBtn.style.display = "none";
    checkOutBtn.style.display = "inline-flex";
  } else {
    statusLabel.textContent = "Day completed — checked out at";
    statusTime.textContent = formatPKTTime(todayRecord.check_out);
    checkInBtn.style.display = "none";
    checkOutBtn.style.display = "none";
  }
}

async function checkIn() {
  const alertBox = document.getElementById("attendanceAlert");
  try {
    await apiFetch("/attendance/check-in", { method: "POST" });
    loadHistory();
  } catch (err) {
    showAlert(alertBox, err.message);
  }
}

async function checkOut() {
  const alertBox = document.getElementById("attendanceAlert");
  try {
    await apiFetch("/attendance/check-out", { method: "POST" });
    loadHistory();
  } catch (err) {
    showAlert(alertBox, err.message);
  }
}

loadHistory();
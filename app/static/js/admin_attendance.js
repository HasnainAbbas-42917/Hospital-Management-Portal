async function loadAttendance() {
  const body = document.getElementById("attendanceBody");
  try {
    const records = await apiFetch("/admin/attendance");
    if (!records.length) {
      body.innerHTML = `<tr><td colspan="6" class="text-muted">No attendance records yet.</td></tr>`;
      return;
    }
    body.innerHTML = records.map((r) => `
      <tr>
        <td>${r.staff_name}</td>
        <td style="text-transform:capitalize;">${r.role || "—"}</td>
        <td>${formatDate(r.date)}</td>
        <td>${formatPKTTime(r.check_in)}</td>
        <td>${formatPKTTime(r.check_out)}</td>
        <td>${r.status}</td>
      </tr>
    `).join("");
  } catch (err) {
    body.innerHTML = `<tr><td colspan="6" class="text-muted">Could not load attendance.</td></tr>`;
  }
}

loadAttendance();
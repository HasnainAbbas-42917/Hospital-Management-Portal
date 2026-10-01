async function loadOverview() {
  const container = document.getElementById("statsContainer");
  try {
    const s = await apiFetch("/admin/reports/summary");
    container.innerHTML = `
      <div class="stat-grid">
        <div class="stat-card">
          <div class="stat-number">${s.total_doctors}</div>
          <div class="stat-label">Doctors</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">${s.total_receptionists}</div>
          <div class="stat-label">Receptionists</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">${s.total_patients}</div>
          <div class="stat-label">Patients</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">${s.total_appointments}</div>
          <div class="stat-label">Total appointments</div>
        </div>
      </div>

      <div class="card">
        <h3>Appointments by status</h3>
        <div class="stat-breakdown">
          <span class="badge badge-pending">Pending: ${s.appointments_pending}</span>
          <span class="badge badge-confirmed">Confirmed: ${s.appointments_confirmed}</span>
          <span class="badge badge-completed">Completed: ${s.appointments_completed}</span>
          <span class="badge badge-cancelled">Cancelled: ${s.appointments_cancelled}</span>
        </div>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<p class="text-muted">Could not load report: ${err.message}</p>`;
  }
}

loadOverview();
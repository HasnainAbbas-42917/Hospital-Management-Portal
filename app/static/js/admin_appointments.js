async function loadAppointments() {
  const listBox = document.getElementById("appointmentsList");
  try {
    const appointments = await apiFetch("/admin/appointments");
    if (!appointments.length) {
      listBox.innerHTML = `<div class="empty-state"><h3>No appointments yet</h3></div>`;
      return;
    }
    listBox.innerHTML = appointments.map((appt) => `
      <div class="appointment-item">
        <div class="flex-between">
        <strong>${formatDate(appt.appointment_date)} at ${formatTime12(appt.appointment_time)}</strong>
          <span class="badge badge-${appt.status}">${appt.status}</span>
        </div>
        <div class="appt-meta"><strong>Patient:</strong> ${appt.patient_name} • ${appt.patient_phone || "No phone"}</div>
        <div class="appt-meta"><strong>Doctor:</strong> ${appt.doctor_name} (${appt.doctor_specialization || "General"})</div>
        <div class="appt-meta"><strong>Problem:</strong> ${appt.reason || "Not provided"}</div>
      </div>
    `).join("");
  } catch (err) {
    listBox.innerHTML = `<p class="text-muted">Could not load appointments: ${err.message}</p>`;
  }
}

loadAppointments();
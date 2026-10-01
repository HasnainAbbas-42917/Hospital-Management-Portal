async function loadAppointments() {
  const listBox = document.getElementById("appointmentsList");
  listBox.innerHTML = "<p class='text-muted'>Loading...</p>";

  try {
    const appointments = await apiFetch("/doctors/appointments");
    renderAppointments(appointments);
  } catch (err) {
    listBox.innerHTML = `<p class="text-muted">Could not load appointments: ${err.message}</p>`;
  }
}

function renderAppointments(appointments) {
  const listBox = document.getElementById("appointmentsList");

  if (!appointments.length) {
    listBox.innerHTML = `<div class="empty-state"><h3>No appointments yet</h3><p>Appointments booked with you will appear here.</p></div>`;
    return;
  }

  listBox.innerHTML = appointments.map((appt) => `
    <div class="appointment-item">
      <div class="flex-between">
        <strong>${formatDate(appt.appointment_date)} at ${formatTime12(appt.appointment_time)}</strong>
        <span class="badge badge-${appt.status}">${appt.status}</span>
      </div>
      <div class="appt-meta">${appt.reason || "No reason provided"}</div>
      <div class="appt-actions">
        ${appt.status === "pending" || appt.status === "confirmed" ? `
          <button class="btn btn-secondary" onclick="updateStatus(${appt.id}, 'completed')">Mark completed</button>
        ` : ""}
        ${appt.status === "completed" ? `
          <button class="btn btn-secondary" onclick="openRecordModal(${appt.id})">Add medical record</button>
        ` : ""}
      </div>
    </div>
  `).join("");
}

async function updateStatus(appointmentId, status) {
  try {
    await apiFetch(`/doctors/appointments/${appointmentId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
    loadAppointments();
  } catch (err) {
    alert(err.message);
  }
}

function openRecordModal(appointmentId) {
  document.getElementById("recordAppointmentId").value = appointmentId;
  document.getElementById("recordForm").reset();
  document.getElementById("recordAlert").className = "alert";
  document.getElementById("recordModal").classList.add("show");
}

function closeRecordModal() {
  document.getElementById("recordModal").classList.remove("show");
}

document.getElementById("recordForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const alertBox = document.getElementById("recordAlert");
  const appointmentId = document.getElementById("recordAppointmentId").value;

  const payload = {
    diagnosis: document.getElementById("diagnosis").value,
    prescription: document.getElementById("prescription").value,
    notes: document.getElementById("notes").value,
  };

  try {
    await apiFetch(`/doctors/appointments/${appointmentId}/medical-record`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    closeRecordModal();
    showToastSuccess();
  } catch (err) {
    showAlert(alertBox, err.message);
  }
});

function showToastSuccess() {
  alert("Medical record saved successfully.");
}

loadAppointments();
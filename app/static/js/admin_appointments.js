let currentFilter = "";

document.querySelectorAll(".filter-tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".filter-tab").forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    currentFilter = tab.dataset.status;
    loadAppointments();
  });
});

async function loadAppointments() {
  const listBox = document.getElementById("appointmentsList");
  listBox.innerHTML = "<p class='text-muted'>Loading...</p>";

  const query = currentFilter ? `?status=${currentFilter}` : "";

  try {
    const appointments = await apiFetch("/admin/appointments" + query);
    renderAppointments(appointments);
  } catch (err) {
    listBox.innerHTML = `<p class="text-muted">Could not load appointments: ${err.message}</p>`;
  }
}

function renderAppointments(appointments) {
  const listBox = document.getElementById("appointmentsList");

  if (!appointments.length) {
    listBox.innerHTML = `<div class="empty-state"><h3>No appointments found</h3><p>Try a different filter.</p></div>`;
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
      <div class="appt-actions">
        ${appt.status === "pending" ? `
          <button class="btn btn-primary" onclick="confirmAppointment(${appt.id})">Confirm</button>
        ` : ""}
        ${appt.status === "pending" || appt.status === "confirmed" ? `
          <button class="btn btn-secondary" onclick="openRescheduleModal(${appt.id}, ${appt.doctor_id})">Reschedule</button>
          <button class="btn btn-danger" onclick="cancelAppointment(${appt.id})">Cancel</button>
        ` : ""}
        <button class="btn btn-secondary" onclick="openPaymentModal(${appt.id})">Verify payment</button>
      </div>
    </div>
  `).join("");
}

async function confirmAppointment(id) {
  try {
    await apiFetch(`/admin/appointments/${id}/confirm`, { method: "PATCH" });
    loadAppointments();
  } catch (err) {
    alert(err.message);
  }
}

async function cancelAppointment(id) {
  if (!confirm("Are you sure you want to cancel this appointment?")) return;
  try {
    await apiFetch(`/admin/appointments/${id}/cancel`, { method: "PATCH" });
    loadAppointments();
  } catch (err) {
    alert(err.message);
  }
}

function openRescheduleModal(appointmentId, doctorId) {
  document.getElementById("rescheduleAppointmentId").value = appointmentId;
  document.getElementById("rescheduleDoctorId").value = doctorId;
  document.getElementById("rescheduleForm").reset();
  document.getElementById("rescheduleAlert").className = "alert";
  document.getElementById("rescheduleModal").classList.add("show");
}
function closeRescheduleModal() {
  document.getElementById("rescheduleModal").classList.remove("show");
}

document.getElementById("rescheduleForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const alertBox = document.getElementById("rescheduleAlert");
  const appointmentId = document.getElementById("rescheduleAppointmentId").value;

  const payload = {
    doctor_id: parseInt(document.getElementById("rescheduleDoctorId").value),
    appointment_date: document.getElementById("newDate").value,
    appointment_time: document.getElementById("newTime").value + ":00",
  };

  try {
    await apiFetch(`/admin/appointments/${appointmentId}/reschedule`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
    closeRescheduleModal();
    loadAppointments();
  } catch (err) {
    showAlert(alertBox, err.message);
  }
});

function openPaymentModal(appointmentId) {
  document.getElementById("paymentAppointmentId").value = appointmentId;
  document.getElementById("paymentForm").reset();
  document.getElementById("paymentAlert").className = "alert";
  document.getElementById("paymentModal").classList.add("show");
}
function closePaymentModal() {
  document.getElementById("paymentModal").classList.remove("show");
}

document.getElementById("paymentForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const alertBox = document.getElementById("paymentAlert");
  const appointmentId = document.getElementById("paymentAppointmentId").value;

  const payload = {
    amount: parseFloat(document.getElementById("amount").value),
    method: document.getElementById("method").value,
    status: document.getElementById("paymentStatus").value,
  };

  try {
    await apiFetch(`/admin/appointments/${appointmentId}/payment`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    closePaymentModal();
    alert("Payment saved successfully.");
  } catch (err) {
    showAlert(alertBox, err.message);
  }
});

loadAppointments();
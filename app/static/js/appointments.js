let selectedRating = 0;

async function loadAppointments() {
  const listBox = document.getElementById("appointmentsList");
  listBox.innerHTML = "<p class='text-muted'>Loading...</p>";

  try {
    const appointments = await apiFetch("/patients/appointments");
    renderAppointments(appointments);
  } catch (err) {
    listBox.innerHTML = `<p class="text-muted">Could not load appointments: ${err.message}</p>`;
  }
}

function renderAppointments(appointments) {
  const listBox = document.getElementById("appointmentsList");

  if (!appointments.length) {
    listBox.innerHTML = `<div class="empty-state"><h3>No appointments yet</h3><p>Go to "Find Doctors" to book your first appointment.</p></div>`;
    return;
  }

  listBox.innerHTML = appointments.map((appt) => `
    <div class="appointment-item">
      <div class="flex-between">
        <strong>${formatDate(appt.appointment_date)} at ${formatTime12(appt.appointment_time)}</strong>
        <span class="badge badge-${appt.status}">${appt.status}</span>
      </div>
      <div class="appt-meta">${appt.reason || "No reason provided"}</div>
      ${appt.status === "completed" ? `
        <div class="appt-actions">
          <button class="btn btn-secondary" onclick="openReviewModal(${appt.id})">Leave a review</button>
        </div>
      ` : ""}
    </div>
  `).join("");
}

function openReviewModal(appointmentId) {
  document.getElementById("reviewAppointmentId").value = appointmentId;
  document.getElementById("reviewForm").reset();
  document.getElementById("reviewAlert").className = "alert";
  selectedRating = 0;
  updateStars();
  document.getElementById("reviewModal").classList.add("show");
}

function closeReviewModal() {
  document.getElementById("reviewModal").classList.remove("show");
}

document.getElementById("starInput").addEventListener("click", (e) => {
  if (e.target.dataset.value) {
    selectedRating = parseInt(e.target.dataset.value);
    updateStars();
  }
});

function updateStars() {
  document.querySelectorAll("#starInput span").forEach((star) => {
    star.classList.toggle("active", parseInt(star.dataset.value) <= selectedRating);
  });
}

document.getElementById("reviewForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const alertBox = document.getElementById("reviewAlert");

  if (selectedRating === 0) {
    showAlert(alertBox, "Please select a star rating.");
    return;
  }

  const payload = {
    appointment_id: parseInt(document.getElementById("reviewAppointmentId").value),
    rating: selectedRating,
    comment: document.getElementById("reviewComment").value,
  };

  try {
    await apiFetch("/reviews", { method: "POST", body: JSON.stringify(payload) });
    closeReviewModal();
    loadAppointments();
  } catch (err) {
    showAlert(alertBox, err.message);
  }
});

loadAppointments();
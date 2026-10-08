let pendingDoctorId = new URLSearchParams(window.location.search).get("doctor_id");

const PATIENT_DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

function escapePatientHTML(value) {
  const element = document.createElement("span");
  element.textContent = value ?? "";
  return element.innerHTML;
}

function renderPatientDoctorSchedule(doc) {
  const schedule = Array.isArray(doc.schedule) ? doc.schedule : [];
  if (!schedule.length) {
    return `<div class="doctor-schedule doctor-schedule-empty"><span class="schedule-status schedule-status-empty">No schedule set</span><span>Availability will be updated by the hospital team.</span></div>`;
  }

  return `<div class="doctor-schedule" aria-label="Doctor working schedule">
    <div class="schedule-heading"><span>Working schedule</span><span class="schedule-status">${doc.availability === "available" ? "Available" : "No schedule set"}</span></div>
    <div class="schedule-list">
      ${schedule.slice(0, 3).map((slot) => `
        <div class="schedule-row">
          <span class="schedule-day">${PATIENT_DAY_NAMES[slot.day_of_week] || "Day"}</span>
          <span class="schedule-time">${formatTime12(slot.start_time)} – ${formatTime12(slot.end_time)}</span>
          <span class="schedule-duration">${slot.slot_duration_minutes} min slots</span>
        </div>
      `).join("")}
    </div>
    ${schedule.length > 3 ? `<span class="schedule-more">+${schedule.length - 3} more time slots</span>` : ""}
  </div>`;
}

async function searchDoctors() {
  const specialization = document.getElementById("specialization").value.trim();
  const keyword = document.getElementById("keyword").value.trim();

  const params = new URLSearchParams();
  if (specialization) params.append("specialization", specialization);
  if (keyword) params.append("keyword", keyword);

  const resultsBox = document.getElementById("doctorResults");
  resultsBox.innerHTML = "<p class='text-muted'>Searching...</p>";

  try {
    const doctors = await apiFetch("/patients/doctors/search?" + params.toString());
    renderDoctors(doctors);
  } catch (err) {
    resultsBox.innerHTML = `<p class="text-muted">Could not load doctors: ${err.message}</p>`;
  }
}

function renderDoctors(doctors) {
  const resultsBox = document.getElementById("doctorResults");

  if (!doctors.length) {
    resultsBox.innerHTML = `<div class="empty-state"><h3>No doctors found</h3><p>Try a different specialization or keyword.</p></div>`;
    return;
  }

  resultsBox.innerHTML = doctors.map((doc) => `
    <div class="doctor-card">
      <div class="doctor-card-top">
        <div class="avatar-circle">${escapePatientHTML(doc.name).charAt(0).toUpperCase()}</div>
        <span class="doctor-availability">${escapePatientHTML(doc.availability === "available" ? "Schedule available" : "Schedule pending")}</span>
      </div>
      <h3>${escapePatientHTML(doc.name)}</h3>
      <div class="specialization">${escapePatientHTML(doc.specialization || "General")}</div>
      <div class="meta-row">
        <span>${Number(doc.experience_years || 0)} yrs experience</span>
        <span>Rs. ${Number(doc.consultation_fee || 0).toLocaleString()}</span>
      </div>
      <p class="bio">${escapePatientHTML(doc.bio ? doc.bio.substring(0, 90) : "No bio provided.")}</p>
      ${renderPatientDoctorSchedule(doc)}
      <button class="btn btn-primary btn-block" onclick="openBookingModal(${doc.id}, '${escapePatientHTML(doc.name).replace(/'/g, "")}')">Book appointment</button>
    </div>
  `).join("");

  if (pendingDoctorId) {
    const doctor = doctors.find((item) => item.id === Number(pendingDoctorId));
    pendingDoctorId = null;
    if (doctor) openBookingModal(doctor.id, doctor.name);
  }
}

function openBookingModal(doctorId, doctorName) {
  document.getElementById("bookingDoctorId").value = doctorId;
  document.getElementById("modalDoctorName").textContent = "Book with " + doctorName;
  document.getElementById("bookingForm").reset();
  document.getElementById("bookingDoctorId").value = doctorId;
  document.getElementById("modalAlert").className = "alert";
  document.getElementById("bookingModal").classList.add("show");
}

function closeModal() {
  document.getElementById("bookingModal").classList.remove("show");
}

document.getElementById("bookingForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const alertBox = document.getElementById("modalAlert");

  const payload = {
    doctor_id: parseInt(document.getElementById("bookingDoctorId").value),
    appointment_date: document.getElementById("apptDate").value,
    appointment_time: document.getElementById("apptTime").value + ":00",
    reason: document.getElementById("apptReason").value,
  };

  try {
    await apiFetch("/patients/appointments", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    closeModal();
    alert("Appointment requested successfully. You can track its status under 'My Appointments'.");
  } catch (err) {
    showAlert(alertBox, err.message);
  }
});

// Load some doctors by default when the page opens
searchDoctors();
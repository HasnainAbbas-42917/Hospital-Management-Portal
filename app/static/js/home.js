async function searchPublicDoctors() {
  const specialization = document.getElementById("homeSpecialization").value.trim();
  const params = new URLSearchParams();
  if (specialization) params.append("specialization", specialization);

  const grid = document.getElementById("homeDoctorsGrid");
  grid.innerHTML = "<p class='text-muted'>Loading...</p>";
  try {
    const doctors = await apiFetch("/patients/doctors/search?" + params.toString());
    renderHomeDoctors(doctors);
  } catch (err) {
    grid.innerHTML = `<p class="text-muted">Could not load doctors right now.</p>`;
  }
}

async function loadPublicStatistics() {
  const container = document.getElementById("publicStats");
  try {
    const stats = await apiFetch("/patients/public/statistics");
    const values = [
      [stats.total_doctors, "Approved doctors"],
      [stats.specializations.length, "Specializations"],
      [stats.total_patients, "Registered patients"],
      [stats.total_appointments, "Appointments"],
      [stats.appointments_confirmed, "Confirmed"],
      [stats.appointments_completed, "Completed"],
    ];

    container.innerHTML = `
      <div class="statistics-grid">
        ${values.map(([value, label]) => `
          <div class="statistics-item">
            <div class="statistics-number">${Number(value).toLocaleString()}</div>
            <div class="statistics-label">${label}</div>
          </div>
        `).join("")}
      </div>
      <div class="statistics-details">
        <div class="specialization-list">
          <h3>Our specialties</h3>
          <div class="specialization-tags">
            ${stats.specializations.length
              ? stats.specializations.map((name) => `<span>${escapeHTML(name)}</span>`).join("")
              : "<span>Specialties are being updated</span>"}
          </div>
        </div>
        <div class="appointment-breakdown" aria-label="Appointments by status">
          <span class="status-pending">Pending <strong>${Number(stats.appointments_pending).toLocaleString()}</strong></span>
          <span class="status-confirmed">Confirmed <strong>${Number(stats.appointments_confirmed).toLocaleString()}</strong></span>
          <span class="status-completed">Completed <strong>${Number(stats.appointments_completed).toLocaleString()}</strong></span>
          <span class="status-cancelled">Cancelled <strong>${Number(stats.appointments_cancelled).toLocaleString()}</strong></span>
        </div>
      </div>
      <p class="statistics-note">Doctors listed here have been approved by hospital administration. Counts update from the live hospital records.</p>
    `;
  } catch (err) {
    container.innerHTML = `<p class="statistics-error">Hospital statistics are temporarily unavailable.</p>`;
  }
}

function escapeHTML(value) {
  const element = document.createElement("span");
  element.textContent = value;
  return element.innerHTML;
}

async function bookPublicAppointment(doctorId) {
  const query = new URLSearchParams({ doctor_id: doctorId });

  if (!getToken()) {
    window.location.href = "/register?" + query.toString();
    return;
  }

  if (getRole() !== "patient") {
    window.location.href = "/register?" + query.toString();
    return;
  }

  try {
    await apiFetch("/patients/me");
    window.location.href = "/patient/dashboard?" + query.toString();
  } catch (err) {
    if (err.message === "Patient profile not found") {
      window.location.href = "/patient/profile?" + query.toString();
      return;
    }
    window.location.href = "/login?" + query.toString();
  }
}

function renderHomeDoctors(doctors) {
  const grid = document.getElementById("homeDoctorsGrid");
  if (!doctors.length) {
    grid.innerHTML = `<div class="empty-state"><h3>No doctors found</h3><p>Try a different specialization, or check back soon.</p></div>`;
    return;
  }
  grid.innerHTML = doctors.map((doc) => `
    <div class="doctor-card">
      <div class="avatar-circle">${doc.name.charAt(0).toUpperCase()}</div>
      <h3>${doc.name}</h3>
      <div class="specialization">${doc.specialization || "General"}</div>
      <div class="meta-row">
        <span>${doc.experience_years} yrs experience</span>
        <span>Rs. ${doc.consultation_fee}</span>
      </div>
      <p class="bio">${doc.bio ? doc.bio.substring(0, 90) + "..." : "No bio provided."}</p>
      <button type="button" class="btn btn-primary btn-block" onclick="bookPublicAppointment(${doc.id})">Book Appointment</button>
    </div>
  `).join("");
}

loadPublicStatistics();
searchPublicDoctors();
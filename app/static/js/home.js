let publicDoctors = [];
let visiblePublicDoctorCount = 5;

async function searchPublicDoctors() {
  const specialization = document.getElementById("homeSpecialization").value.trim();
  const params = new URLSearchParams();
  if (specialization) params.append("specialization", specialization);

  const grid = document.getElementById("homeDoctorsGrid");
  grid.innerHTML = "<p class='text-muted'>Loading...</p>";
  try {
    publicDoctors = await apiFetch("/patients/doctors/search?" + params.toString());
    visiblePublicDoctorCount = 5;
    renderHomeDoctors();
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

function togglePublicNav(button) {
  const links = document.getElementById("publicNavLinks");
  const isOpen = links.classList.toggle("show");
  button.setAttribute("aria-expanded", String(isOpen));
  button.setAttribute("aria-label", isOpen ? "Close navigation menu" : "Open navigation menu");
}

document.querySelectorAll("#publicNavLinks a").forEach((link) => {
  link.addEventListener("click", () => {
    const links = document.getElementById("publicNavLinks");
    const toggle = document.querySelector(".public-nav-toggle");
    links.classList.remove("show");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Open navigation menu");
  });
});

let publicReviews = [];
let visiblePublicReviewCount = 3;

async function loadPublicReviews() {
  const container = document.getElementById("publicReviews");
  try {
    publicReviews = await apiFetch("/reviews/public");
    renderPublicReviews();
  } catch (err) {
    container.innerHTML = `<p class="statistics-error">Patient reviews are temporarily unavailable.</p>`;
  }
}

function renderPublicReviews() {
  const container = document.getElementById("publicReviews");
  if (!publicReviews.length) {
    container.innerHTML = `<p class="text-muted">No patient reviews have been shared yet.</p>`;
    return;
  }

  const averageRating = publicReviews.reduce((sum, review) => sum + review.rating, 0) / publicReviews.length;
  const displayedReviews = publicReviews.slice(0, visiblePublicReviewCount);
  container.innerHTML = `
    <div class="review-summary">
      <div class="review-summary-item">
        <div class="review-summary-number">${averageRating.toFixed(1)}</div>
        <div class="review-summary-label">Average patient rating</div>
      </div>
      <div class="review-summary-item">
        <div class="review-summary-number">${publicReviews.length.toLocaleString()}</div>
        <div class="review-summary-label">Patient reviews</div>
      </div>
    </div>
    <div class="public-review-list">
      ${displayedReviews.map((review) => `
        <article class="public-review-item">
          <div class="public-review-topline">
            <div class="review-stars" role="img" aria-label="${review.rating} out of 5 stars">${"★".repeat(review.rating)}${"☆".repeat(5 - review.rating)}</div>
            <time class="public-review-date" datetime="${escapeHTML(review.created_at || "")}">${escapeHTML(formatDate((review.created_at || "").slice(0, 10)))}</time>
          </div>
          <p class="public-review-comment">${review.comment ? `“${escapeHTML(review.comment)}”` : "No written comment was provided."}</p>
          <div class="public-review-attribution">
            <span><strong>Patient:</strong> ${escapeHTML(review.patient_name)}</span>
            <span><strong>Doctor:</strong> ${escapeHTML(review.doctor_name)} <span class="review-specialization">${escapeHTML(review.doctor_specialization)}</span></span>
          </div>
        </article>
      `).join("")}
    </div>
    ${visiblePublicReviewCount < publicReviews.length
      ? `<div class="reviews-more-wrap"><button type="button" class="btn btn-secondary reveal-button" onclick="showMorePublicReviews()">Show More Reviews</button></div>`
      : ""}
  `;
}

function showMorePublicReviews() {
  visiblePublicReviewCount += 3;
  renderPublicReviews();
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

const HOME_DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

function renderDoctorSchedule(doc) {
  const schedule = Array.isArray(doc.schedule) ? doc.schedule : [];
  if (!schedule.length) {
    return `<div class="doctor-schedule doctor-schedule-empty"><span class="schedule-status schedule-status-empty">No schedule set</span><span>Availability will be updated by the hospital team.</span></div>`;
  }

  return `<div class="doctor-schedule" aria-label="Doctor working schedule">
    <div class="schedule-heading"><span>Working schedule</span><span class="schedule-status">${escapeHTML(doc.availability === "available" ? "Available" : "No schedule set")}</span></div>
    <div class="schedule-list">
      ${schedule.slice(0, 3).map((slot) => `
        <div class="schedule-row">
          <span class="schedule-day">${HOME_DAY_NAMES[slot.day_of_week] || "Day"}</span>
          <span class="schedule-time">${formatTime12(slot.start_time)} – ${formatTime12(slot.end_time)}</span>
          <span class="schedule-duration">${slot.slot_duration_minutes} min slots</span>
        </div>
      `).join("")}
    </div>
    ${schedule.length > 3 ? `<span class="schedule-more">+${schedule.length - 3} more time slots</span>` : ""}
  </div>`;
}

function renderHomeDoctors() {
  const grid = document.getElementById("homeDoctorsGrid");
  if (!publicDoctors.length) {
    grid.innerHTML = `<div class="empty-state"><h3>No doctors found</h3><p>Try a different specialization or keyword.</p></div>`;
    return;
  }

  const shownDoctors = publicDoctors.slice(0, visiblePublicDoctorCount);
  grid.innerHTML = shownDoctors.map((doc) => `
    <article class="doctor-card">
      <div class="doctor-card-top">
        <div class="avatar-circle">${escapeHTML(doc.name.charAt(0).toUpperCase())}</div>
        <span class="doctor-availability">${escapeHTML(doc.availability === "available" ? "Schedule available" : "Schedule pending")}</span>
      </div>
      <h3>${escapeHTML(doc.name)}</h3>
      <div class="specialization">${escapeHTML(doc.specialization || "General")}</div>
      <div class="meta-row">
        <span>${Number(doc.experience_years || 0)} yrs experience</span>
        <span>Rs. ${Number(doc.consultation_fee || 0).toLocaleString()}</span>
      </div>
      <p class="bio">${escapeHTML(doc.bio ? doc.bio.substring(0, 90) + "..." : "No bio provided.")}</p>
      ${renderDoctorSchedule(doc)}
      <button type="button" class="btn btn-primary btn-block" onclick="bookPublicAppointment(${doc.id})">Book Appointment</button>
    </article>
  `).join("") + (visiblePublicDoctorCount < publicDoctors.length
    ? `<div class="doctors-more-wrap"><button type="button" class="btn btn-secondary reveal-button" onclick="showMorePublicDoctors()">Show More Doctors</button></div>`
    : "");
}

function showMorePublicDoctors() {
  visiblePublicDoctorCount += 5;
  renderHomeDoctors();
}

loadPublicStatistics();
loadPublicReviews();
searchPublicDoctors();
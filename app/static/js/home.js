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

searchPublicDoctors();
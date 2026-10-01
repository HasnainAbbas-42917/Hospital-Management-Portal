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
      <div class="avatar-circle">${doc.name.charAt(0).toUpperCase()}</div>
      <h3>${doc.name}</h3>
      <div class="specialization">${doc.specialization || "General"}</div>
      <div class="meta-row">
        <span>${doc.experience_years} yrs experience</span>
        <span>Rs. ${doc.consultation_fee}</span>
      </div>
      <p class="bio">${doc.bio ? doc.bio.substring(0, 90) : "No bio provided."}</p>
      <button class="btn btn-primary btn-block" onclick="openBookingModal(${doc.id}, '${doc.name.replace(/'/g, "")}')">Book appointment</button>
    </div>
  `).join("");
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
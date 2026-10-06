let creatingProfile = false;
const bookingDoctorId = new URLSearchParams(window.location.search).get("doctor_id");

async function loadProfile() {
  try {
    const p = await apiFetch("/patients/me");
    document.getElementById("pName").value = p.name || "";
    document.getElementById("pPhone").value = p.phone || "";
    document.getElementById("pDob").value = p.dob || "";
    document.getElementById("pGender").value = p.gender || "";
    document.getElementById("pAddress").value = p.address || "";
  } catch (err) {
    if (err.message === "Patient profile not found") {
      creatingProfile = true;
      showAlert(document.getElementById("profileAlert"), "Create your patient profile before booking.");
      return;
    }
    showAlert(document.getElementById("profileAlert"), "Could not load profile: " + err.message);
  }
}

document.getElementById("profileForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const alertBox = document.getElementById("profileAlert");

  const payload = {
    name: document.getElementById("pName").value || null,
    phone: document.getElementById("pPhone").value || null,
    dob: document.getElementById("pDob").value || null,
    gender: document.getElementById("pGender").value || null,
    address: document.getElementById("pAddress").value || null,
  };

  try {
    await apiFetch("/patients/me", {
      method: creatingProfile ? "POST" : "PATCH",
      body: JSON.stringify(payload),
    });
    if (bookingDoctorId) {
      window.location.href = "/patient/dashboard?doctor_id=" + encodeURIComponent(bookingDoctorId);
      return;
    }
    showAlert(alertBox, "Profile saved successfully.", "success");
  } catch (err) {
    showAlert(alertBox, err.message);
  }
});

loadProfile();
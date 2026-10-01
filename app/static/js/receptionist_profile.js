async function loadProfile() {
  try {
    const r = await apiFetch("/receptionist/me");
    document.getElementById("rName").value = r.name || "";
    document.getElementById("rPhone").value = r.phone || "";
  } catch (err) {
    showAlert(document.getElementById("profileAlert"), "Could not load profile: " + err.message);
  }
}

document.getElementById("profileForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const alertBox = document.getElementById("profileAlert");

  const payload = {
    name: document.getElementById("rName").value || null,
    phone: document.getElementById("rPhone").value || null,
  };

  try {
    await apiFetch("/receptionist/me", { method: "PATCH", body: JSON.stringify(payload) });
    showAlert(alertBox, "Profile saved successfully.", "success");
  } catch (err) {
    showAlert(alertBox, err.message);
  }
});

loadProfile();
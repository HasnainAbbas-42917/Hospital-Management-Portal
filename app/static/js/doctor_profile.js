const DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

async function loadProfile() {
  try {
    const doctor = await apiFetch("/doctors/me");

    document.getElementById("doctorName").value = doctor.name || "";
    document.getElementById("specialization").value = doctor.specialization || "";
    document.getElementById("experience_years").value = doctor.experience_years || "";
    document.getElementById("bio").value = doctor.bio || "";
    document.getElementById("feeDisplay").value = "Rs. " + doctor.consultation_fee;

    const banner = document.getElementById("statusBanner");
    if (doctor.status === "pending") {
      banner.className = "alert show alert-error";
      banner.textContent = "Your application is pending review. The hospital administration will approve your profile before it appears to patients.";
    } else if (doctor.status === "approved") {
      banner.className = "alert show alert-success";
      banner.textContent = "Your profile is approved and visible to patients.";
    } else if (doctor.status === "rejected") {
      banner.className = "alert show alert-error";
      banner.textContent = "Your application was not approved. Please update your profile or contact the hospital administration.";
    }
  } catch (err) {
    console.error(err);
  }
}

document.getElementById("profileForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const alertBox = document.getElementById("profileAlert");

  const payload = {
    name: document.getElementById("doctorName").value || null,
    specialization: document.getElementById("specialization").value || null,
    experience_years: document.getElementById("experience_years").value ? parseInt(document.getElementById("experience_years").value) : null,
    bio: document.getElementById("bio").value || null,
    requested_schedule_note: document.getElementById("scheduleNote").value || null,
  };

  try {
    await apiFetch("/doctors/me", { method: "PATCH", body: JSON.stringify(payload) });
    showAlert(alertBox, "Profile updated successfully.", "success");
  } catch (err) {
    showAlert(alertBox, err.message);
  }
});

async function loadAvailability() {
  const listBox = document.getElementById("availabilityList");
  try {
    const slots = await apiFetch("/doctors/availability");
    if (!slots.length) {
      listBox.innerHTML = `<p class="text-muted">No availability set yet. Add your first time slot below.</p>`;
      return;
    }
    listBox.innerHTML = slots.map((slot) => `
      <div class="availability-row">
        <span><strong>${DAY_NAMES[slot.day_of_week]}</strong> — ${slot.start_time.substring(0,5)} to ${slot.end_time.substring(0,5)} (${slot.slot_duration_minutes} min slots)</span>
        <button class="remove-btn" onclick="removeAvailability(${slot.id})">Remove</button>
      </div>
    `).join("");
  } catch (err) {
    listBox.innerHTML = `<p class="text-muted">Could not load availability.</p>`;
  }
}

async function addAvailability() {
  const alertBox = document.getElementById("availabilityAlert");
  const payload = {
    day_of_week: parseInt(document.getElementById("dayOfWeek").value),
    start_time: document.getElementById("startTime").value + ":00",
    end_time: document.getElementById("endTime").value + ":00",
    slot_duration_minutes: parseInt(document.getElementById("slotDuration").value),
  };

  try {
    await apiFetch("/doctors/availability", { method: "POST", body: JSON.stringify(payload) });
    loadAvailability();
  } catch (err) {
    showAlert(alertBox, err.message);
  }
}

async function removeAvailability(id) {
  try {
    await apiFetch(`/doctors/availability/${id}`, { method: "DELETE" });
    loadAvailability();
  } catch (err) {
    alert(err.message);
  }
}

loadProfile();
loadAvailability();
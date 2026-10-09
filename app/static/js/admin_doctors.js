const DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const DAY_SHORT = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

document.querySelectorAll("#tabSwitch .filter-tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll("#tabSwitch .filter-tab").forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    const target = tab.dataset.tab;
    document.getElementById("applicationsTab").style.display = target === "applications" ? "block" : "none";
    document.getElementById("activeTab").style.display = target === "active" ? "block" : "none";
    if (target === "applications") loadApplications();
    if (target === "active") loadActiveDoctors();
  });
});

async function loadApplications() {
  const listBox = document.getElementById("applicationsList");
  listBox.innerHTML = "<p class='text-muted'>Loading...</p>";
  try {
    const apps = await apiFetch("/admin/doctors/applications?status=pending");
    if (!apps.length) {
      listBox.innerHTML = `<div class="empty-state"><h3>No pending applications</h3><p>New doctor sign-ups will appear here for review.</p></div>`;
      return;
    }
    listBox.innerHTML = apps.map((d) => `
      <div class="appointment-item">
        <div class="flex-between">
          <strong>${d.name}</strong>
          <span class="badge badge-pending">pending</span>
        </div>
        <div class="appt-meta">${d.specialization || "No specialization given"} • ${d.experience_years} yrs experience</div>
        <div class="appt-meta">${d.bio || "No bio provided"}</div>
        ${d.requested_schedule_note ? `<div class="appt-meta"><strong>Requested schedule:</strong> ${d.requested_schedule_note}</div>` : ""}
        <div class="appt-actions">
          <button class="btn btn-secondary" onclick="openScheduleModal(${d.id}, '${d.name.replace(/'/g, "")}')">View schedule</button>
          <button class="btn btn-primary" onclick="approveDoctor(${d.id})">Approve & add to hospital</button>
          <button class="btn btn-danger" onclick="rejectDoctor(${d.id})">Reject</button>
        </div>
      </div>
    `).join("");
  } catch (err) {
    listBox.innerHTML = `<p class="text-muted">Could not load applications: ${err.message}</p>`;
  }
}

async function approveDoctor(id) {
  try {
    await apiFetch(`/admin/doctors/${id}/approve`, { method: "PATCH" });
    loadApplications();
  } catch (err) {
    alert(err.message);
  }
}

async function rejectDoctor(id) {
  if (!confirm("Reject this doctor's application?")) return;
  try {
    await apiFetch(`/admin/doctors/${id}/reject`, { method: "PATCH" });
    loadApplications();
  } catch (err) {
    alert(err.message);
  }
}

async function loadActiveDoctors() {
  const listBox = document.getElementById("activeDoctorsList");
  listBox.innerHTML = "<p class='text-muted'>Loading...</p>";
  try {
    const doctors = await apiFetch("/admin/doctors");
    const approved = doctors.filter((d) => d.status === "approved");
    if (!approved.length) {
      listBox.innerHTML = `<div class="empty-state"><h3>No active doctors yet</h3><p>Approve a pending application to add a doctor here.</p></div>`;
      return;
    }
    listBox.innerHTML = approved.map((doc) => {
      const days = (doc.working_days || []).map((i) => DAY_SHORT[i]).join(", ") || "No schedule set";
      return `
      <div class="doctor-card">
        <div class="avatar-circle">${doc.name.charAt(0).toUpperCase()}</div>
        <h3>${doc.name}</h3>
        <div class="specialization">${doc.specialization || "Not set"}</div>
                <div class="appt-meta">${doc.email || ""}</div>
        <div class="meta-row">
          <span>${doc.experience_years} yrs</span>
          <span>Rs. ${doc.consultation_fee}</span>
        </div>
        <p class="bio"><strong>Working days:</strong> ${days}</p>
        ${!doc.is_active ? `<span class="badge badge-cancelled">deactivated</span>` : ""}
        <div class="appt-actions mt-24" style="flex-wrap:wrap;">
          <button class="btn btn-secondary" onclick="openScheduleModal(${doc.id}, '${doc.name.replace(/'/g, "")}')">View schedule</button>
          <button class="btn btn-secondary" onclick="openFeeModal(${doc.id}, ${doc.consultation_fee})">Set fee</button>
          <button class="btn btn-secondary" onclick="openResetPassword('doctors', ${doc.id}, '${doc.name.replace(/'/g, "")}')">Reset password</button>
          ${doc.is_active
            ? `<button class="btn btn-danger" onclick="deactivateDoctor(${doc.id})">Deactivate</button>`
            : `<button class="btn btn-primary" onclick="reactivateDoctor(${doc.id})">Reactivate</button>`
          }
        </div>
      </div>`;
    }).join("");
  } catch (err) {
    listBox.innerHTML = `<p class="text-muted">Could not load doctors: ${err.message}</p>`;
  }
}

async function deactivateDoctor(id) {
  if (!confirm("Deactivate this doctor's account? Their appointment history will be preserved.")) return;
  try {
    await apiFetch(`/admin/doctors/${id}`, { method: "DELETE" });
    loadActiveDoctors();
  } catch (err) {
    alert(err.message);
  }
}

async function reactivateDoctor(id) {
  try {
    await apiFetch(`/admin/doctors/${id}/reactivate`, { method: "PATCH" });
    loadActiveDoctors();
  } catch (err) {
    alert(err.message);
  }
}

// ---------- Schedule modal ----------
async function openScheduleModal(doctorId, doctorName) {
  document.getElementById("scheduleTitle").textContent = "Schedule — " + doctorName;
  const weekly = document.getElementById("scheduleWeekly");
  const upcoming = document.getElementById("scheduleUpcoming");
  weekly.innerHTML = "<p class='text-muted'>Loading...</p>";
  upcoming.innerHTML = "<p class='text-muted'>Loading...</p>";
  document.getElementById("scheduleModal").classList.add("show");

  try {
    const slots = await apiFetch(`/admin/doctors/${doctorId}/availability`);
    if (!slots.length) {
      weekly.innerHTML = `<p class="text-muted">This doctor has not set any working days yet.</p>`;
    } else {
      slots.sort((a, b) => a.day_of_week - b.day_of_week || a.start_time.localeCompare(b.start_time));
      weekly.innerHTML = slots.map((s) => `
        <div class="availability-row">
          <span><strong>${DAY_NAMES[s.day_of_week]}</strong></span>
          <span>${formatTime12(s.start_time)} – ${formatTime12(s.end_time)} <span class="text-muted">(${s.slot_duration_minutes} min slots)</span></span>
        </div>
      `).join("");
    }
  } catch (err) {
    weekly.innerHTML = `<p class="text-muted">Could not load schedule: ${err.message}</p>`;
  }

  try {
    const all = await apiFetch("/admin/appointments");
    const today = todayPKT();
    const mine = all
      .filter((a) => a.doctor_id === doctorId && a.appointment_date >= today && (a.status === "pending" || a.status === "confirmed"))
      .sort((a, b) => (a.appointment_date + a.appointment_time).localeCompare(b.appointment_date + b.appointment_time));

    if (!mine.length) {
      upcoming.innerHTML = `<p class="text-muted">No upcoming appointments.</p>`;
    } else {
      upcoming.innerHTML = mine.map((a) => `
        <div class="availability-row">
          <span><strong>${formatDate(a.appointment_date)}</strong> at ${formatTime12(a.appointment_time)}</span>
          <span>${a.patient_name} <span class="badge badge-${a.status}">${a.status}</span></span>
        </div>
      `).join("");
    }
  } catch (err) {
    upcoming.innerHTML = `<p class="text-muted">Could not load appointments.</p>`;
  }
}

function closeScheduleModal() {
  document.getElementById("scheduleModal").classList.remove("show");
}

// ---------- Fee modal ----------
function openFeeModal(doctorId, currentFee) {
  document.getElementById("feeDoctorId").value = doctorId;
  document.getElementById("feeAmount").value = currentFee;
  document.getElementById("feeAlert").className = "alert";
  document.getElementById("feeModal").classList.add("show");
}
function closeFeeModal() {
  document.getElementById("feeModal").classList.remove("show");
}

document.getElementById("feeForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const alertBox = document.getElementById("feeAlert");
  const doctorId = document.getElementById("feeDoctorId").value;
  const fee = parseFloat(document.getElementById("feeAmount").value);

  try {
    await apiFetch(`/admin/doctors/${doctorId}/fee`, {
      method: "PATCH",
      body: JSON.stringify({ consultation_fee: fee }),
    });
    closeFeeModal();
    loadActiveDoctors();
  } catch (err) {
    showAlert(alertBox, err.message);
  }
});

loadApplications();
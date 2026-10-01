let patientsCache = [];

async function loadPatients() {
  const listBox = document.getElementById("patientsList");
  listBox.innerHTML = "<p class='text-muted'>Loading...</p>";

  try {
    patientsCache = await apiFetch("/doctors/patients");
    if (!patientsCache.length) {
      listBox.innerHTML = `<div class="empty-state"><h3>No patients yet</h3><p>Patients who book an appointment with you will appear here.</p></div>`;
      return;
    }
    listBox.innerHTML = patientsCache.map((p) => `
      <div class="appointment-item flex-between" style="cursor:pointer;" onclick="openPatientModal(${p.id})">
        <div>
          <strong>${p.name}</strong>
          <div class="appt-meta">${p.phone || "No phone"} • ${p.total_appointments} appointment${p.total_appointments === 1 ? "" : "s"}</div>
        </div>
        <div style="text-align:right;">
          ${p.last_visit_date ? `
            <div class="text-muted" style="font-size:0.8rem;">Last visit: ${formatDate(p.last_visit_date)}</div>
            <span class="badge badge-${p.last_visit_status}">${p.last_visit_status}</span>
          ` : ""}
        </div>
      </div>
    `).join("");
  } catch (err) {
    listBox.innerHTML = `<p class="text-muted">Could not load patients: ${err.message}</p>`;
  }
}

async function openPatientModal(patientId) {
  const patient = patientsCache.find((p) => p.id === patientId);
  if (!patient) return;

  document.getElementById("patientModalName").textContent = patient.name;
  document.getElementById("patientDetails").innerHTML = `
    <div class="appt-meta"><strong>Phone:</strong> ${patient.phone || "Not provided"}</div>
    <div class="appt-meta"><strong>Gender:</strong> ${patient.gender || "Not provided"}</div>
    <div class="appt-meta"><strong>Date of birth:</strong> ${patient.dob ? formatDate(patient.dob) : "Not provided"}</div>
    <div class="appt-meta"><strong>Address:</strong> ${patient.address || "Not provided"}</div>
  `;

  const historyBox = document.getElementById("patientHistory");
  historyBox.innerHTML = "<p class='text-muted'>Loading...</p>";
  document.getElementById("patientModal").classList.add("show");

  try {
    const history = await apiFetch(`/doctors/patients/${patientId}/appointments`);
    if (!history.length) {
      historyBox.innerHTML = `<p class="text-muted">No appointment history.</p>`;
      return;
    }
    historyBox.innerHTML = history.map((a) => `
      <div class="availability-row">
        <span>${formatDate(a.appointment_date)} at ${formatTime12(a.appointment_time)}</span>
        <span class="badge badge-${a.status}">${a.status}</span>
      </div>
    `).join("");
  } catch (err) {
    historyBox.innerHTML = `<p class="text-muted">Could not load history.</p>`;
  }
}

function closePatientModal() {
  document.getElementById("patientModal").classList.remove("show");
}

loadPatients();
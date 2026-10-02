async function loadRecords() {
  const listBox = document.getElementById("recordsList");
  listBox.innerHTML = "<p class='text-muted'>Loading...</p>";

  try {
    const records = await apiFetch("/patients/medical-records");
    if (!records.length) {
      listBox.innerHTML = `<div class="empty-state"><h3>No medical records yet</h3><p>Records will appear here after a doctor completes your consultation.</p></div>`;
      return;
    }
    listBox.innerHTML = records.map((r) => `
      <div class="card mt-24">
        <div class="flex-between">
          <h3>${r.doctor_name} <span class="text-muted" style="font-weight:400; font-size:0.85rem;">(${r.doctor_specialization || "General"})</span></h3>
          <span class="text-muted" style="font-size:0.82rem;">${r.appointment_date ? formatDate(r.appointment_date) : ""}</span>
        </div>
        ${r.diagnosis ? `<p><strong>Diagnosis:</strong> ${r.diagnosis}</p>` : ""}
        ${r.prescription ? `<p><strong>Prescription:</strong> ${r.prescription}</p>` : ""}
        ${r.notes ? `<p><strong>Notes:</strong> ${r.notes}</p>` : ""}
      </div>
    `).join("");
  } catch (err) {
    listBox.innerHTML = `<p class="text-muted">Could not load records: ${err.message}</p>`;
  }
}

loadRecords();
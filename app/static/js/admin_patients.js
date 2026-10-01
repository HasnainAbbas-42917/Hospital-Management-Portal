async function loadPatients() {
  const body = document.getElementById("patientsBody");
  try {
    const patients = await apiFetch("/admin/patients");
    if (!patients.length) {
      body.innerHTML = `<tr><td colspan="6" class="text-muted">No patients yet.</td></tr>`;
      return;
    }
    body.innerHTML = patients.map((p) => `
      <tr>
        <td>${p.id}</td>
        <td>${p.name}</td>
        <td>${p.phone || "—"}</td>
        <td>${p.gender || "—"}</td>
        <td>${p.dob || "—"}</td>
        <td>${p.address || "—"}</td>
      </tr>
    `).join("");
  } catch (err) {
    body.innerHTML = `<tr><td colspan="6" class="text-muted">Could not load patients.</td></tr>`;
  }
}

loadPatients();
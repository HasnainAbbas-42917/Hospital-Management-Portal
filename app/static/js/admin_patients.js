let allPatients = [];

function renderPatients(list) {
  const body = document.getElementById("patientsBody");
  if (!list.length) {
    body.innerHTML = `<tr><td colspan="8" class="text-muted">No patients found.</td></tr>`;
    return;
  }
  body.innerHTML = list.map((p) => `
    <tr>
      <td>${p.id}</td>
      <td>${p.name}</td>
      <td>${p.email || "—"}</td>
      <td>${p.phone || "—"}</td>
      <td>${p.gender || "—"}</td>
      <td>${p.dob ? formatDate(p.dob) : "—"}</td>
      <td>${p.address || "—"}</td>
      <td><button class="btn btn-secondary" style="padding:6px 12px;" onclick="openResetPassword('patients', ${p.id}, '${(p.name || "").replace(/'/g, "")}')">Reset password</button></td>
    </tr>
  `).join("");
}

async function loadPatients() {
  const body = document.getElementById("patientsBody");
  try {
    allPatients = await apiFetch("/admin/patients");
    renderPatients(allPatients);
  } catch (err) {
    body.innerHTML = `<tr><td colspan="8" class="text-muted">Could not load patients.</td></tr>`;
  }
}

document.getElementById("patientSearch").addEventListener("input", (e) => {
  const q = e.target.value.trim().toLowerCase();
  renderPatients(allPatients.filter((p) =>
    [p.name, p.email, p.phone].some((v) => (v || "").toLowerCase().includes(q))
  ));
});

loadPatients();
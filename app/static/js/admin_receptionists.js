async function loadReceptionists() {
  const listBox = document.getElementById("receptionistsList");
  listBox.innerHTML = "<p class='text-muted'>Loading...</p>";
  try {
    const receptionists = await apiFetch("/admin/receptionists");
    if (!receptionists.length) {
      listBox.innerHTML = `<div class="empty-state"><h3>No receptionists yet</h3><p>Click "+ Add Receptionist" to create the first account.</p></div>`;
      return;
    }
       listBox.innerHTML = receptionists.map((r) => `
      <div class="appointment-item flex-between" style="flex-wrap:wrap;">
        <span>
          <strong>${r.name}</strong>
          ${!r.is_active ? `<span class="badge badge-cancelled" style="margin-left:8px;">deactivated</span>` : ""}
          <div class="appt-meta">${r.email || ""}</div>
          <div class="appt-meta">Phone: ${r.phone || "Not provided"}</div>
        </span>
        <span style="display:flex; gap:8px; flex-wrap:wrap;">
          <button class="btn btn-secondary" onclick="openResetPassword('receptionists', ${r.id}, '${(r.name || "").replace(/'/g, "")}')">Reset password</button>
          ${r.is_active
            ? `<button class="btn btn-danger" onclick="deactivateReceptionist(${r.id})">Deactivate</button>`
            : `<button class="btn btn-primary" onclick="reactivateReceptionist(${r.id})">Reactivate</button>`
          }
        </span>
      </div>
    `).join("");
  } catch (err) {
    listBox.innerHTML = `<p class="text-muted">Could not load receptionists: ${err.message}</p>`;
  }
}

async function deactivateReceptionist(id) {
  if (!confirm("Deactivate this receptionist's account?")) return;
  try {
    await apiFetch(`/admin/receptionists/${id}`, { method: "DELETE" });
    loadReceptionists();
  } catch (err) {
    alert(err.message);
  }
}

async function reactivateReceptionist(id) {
  try {
    await apiFetch(`/admin/receptionists/${id}/reactivate`, { method: "PATCH" });
    loadReceptionists();
  } catch (err) {
    alert(err.message);
  }
}

function openAddModal() {
  document.getElementById("addForm").reset();
  document.getElementById("addAlert").className = "alert";
  document.getElementById("addModal").classList.add("show");
}
function closeAddModal() {
  document.getElementById("addModal").classList.remove("show");
}

document.getElementById("addForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const alertBox = document.getElementById("addAlert");

  const payload = {
    name: document.getElementById("rName").value,
    phone: document.getElementById("rPhone").value || null,
    email: document.getElementById("rEmail").value,
    password: document.getElementById("rPassword").value,
  };

  try {
    await apiFetch("/admin/receptionists", { method: "POST", body: JSON.stringify(payload) });
    closeAddModal();
    loadReceptionists();
  } catch (err) {
    showAlert(alertBox, err.message);
  }
});

loadReceptionists();
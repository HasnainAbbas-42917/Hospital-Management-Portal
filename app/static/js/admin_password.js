let resetTarget = null;

function openResetPassword(kind, id, name) {
  resetTarget = { kind, id };
  document.getElementById("resetPasswordTitle").textContent = "Reset password — " + name;
  document.getElementById("resetNewPassword").value = "";
  document.getElementById("resetPasswordAlert").className = "alert";
  document.getElementById("resetPasswordModal").classList.add("show");
}

function closeResetPassword() {
  document.getElementById("resetPasswordModal").classList.remove("show");
  resetTarget = null;
}

function generateTempPassword() {
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789";
  const values = new Uint32Array(10);
  crypto.getRandomValues(values);
  let pwd = "";
  values.forEach((n) => { pwd += chars[n % chars.length]; });
  document.getElementById("resetNewPassword").value = pwd;
}

document.getElementById("resetPasswordForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!resetTarget) return;
  const alertBox = document.getElementById("resetPasswordAlert");
  const newPassword = document.getElementById("resetNewPassword").value;

  try {
    const res = await apiFetch(`/admin/${resetTarget.kind}/${resetTarget.id}/reset-password`, {
      method: "PATCH",
      body: JSON.stringify({ new_password: newPassword }),
    });
    showAlert(alertBox, `${res.detail}. New password: ${newPassword}`, "success");
  } catch (err) {
    showAlert(alertBox, err.message);
  }
});
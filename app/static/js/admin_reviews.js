async function loadReviews() {
  const listBox = document.getElementById("reviewsList");
  const summaryBox = document.getElementById("reviewsSummary");
  listBox.innerHTML = "<p class='text-muted'>Loading...</p>";

  try {
    const reviews = await apiFetch("/admin/reviews");

    if (!reviews.length) {
      summaryBox.innerHTML = "";
      listBox.innerHTML = `<div class="empty-state"><h3>No reviews yet</h3><p>Patient reviews will appear here after completed appointments.</p></div>`;
      return;
    }

    const avg = (reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length).toFixed(1);
    summaryBox.innerHTML = `
      <div class="stat-card">
        <div class="stat-number">${avg}</div>
        <div class="stat-label">Average rating</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">${reviews.length}</div>
        <div class="stat-label">Total reviews</div>
      </div>
    `;

    listBox.innerHTML = reviews.map((r) => `
      <div class="appointment-item">
        <div class="flex-between">
          <strong>${"★".repeat(r.rating)}${"☆".repeat(5 - r.rating)}</strong>
          <span class="text-muted">${formatDate(r.created_at.substring(0, 10))}</span>
        </div>
        <div class="appt-meta"><strong>Patient:</strong> ${r.patient_name}</div>
        <div class="appt-meta"><strong>Doctor:</strong> ${r.doctor_name} (${r.doctor_specialization || "General"})</div>
        ${r.comment ? `<div class="appt-meta">"${r.comment}"</div>` : `<div class="appt-meta text-muted">No comment left</div>`}
      </div>
    `).join("");
  } catch (err) {
    listBox.innerHTML = `<p class="text-muted">Could not load reviews: ${err.message}</p>`;
  }
}

loadReviews();
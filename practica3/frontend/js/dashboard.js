const app = document.querySelector("#app");
app.innerHTML = `
  <div class="topline">
    <h1>Dashboard</h1>
    <a class="button" href="invoices.html">Cargar factura</a>
  </div>
  <section class="grid" id="metrics"></section>
`;

async function loadMetrics() {
  const data = await api("/api/dashboard/metrics");
  document.querySelector("#metrics").innerHTML = `
    <div class="stat"><span>Proveedores</span><strong>${data.providers}</strong></div>
    <div class="stat"><span>Facturas</span><strong>${data.invoices}</strong></div>
    <div class="stat"><span>Monto total</span><strong>${money(data.total_amount)}</strong></div>
    <div class="stat"><span>Bitacora</span><strong>${data.logs}</strong></div>
    <div class="stat"><span>Reportes</span><strong>${data.reports}</strong></div>
    <div class="stat"><span>Ejecuciones RPA</span><strong>${data.rpa_runs}</strong></div>
    <div class="stat"><span>Procesadas</span><strong>${data.by_status.Procesado || 0}</strong></div>
    <div class="stat"><span>Rechazadas</span><strong>${data.by_status.Rechazado || 0}</strong></div>
  `;
}
loadMetrics().catch(error => app.insertAdjacentHTML("beforeend", `<p class="message">${error.message}</p>`));

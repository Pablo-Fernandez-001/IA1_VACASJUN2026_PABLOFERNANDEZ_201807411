const app = document.querySelector("#app");
app.innerHTML = `
  <div class="topline"><h1>Dashboard</h1><button id="reload">Actualizar</button></div>
  <section class="panel"><h2>Metricas actuales</h2><div class="grid" id="metrics"></div></section>
  <section class="panel"><h2>Historial</h2><div class="table-wrap"><table><thead><tr><th>ID</th><th>Inicio</th><th>Estado</th><th>Pasos</th><th>Entregas</th><th>Movimientos</th><th>Eficiencia</th></tr></thead><tbody id="history"></tbody></table></div></section>
`;

async function loadDashboard() {
  const data = await api("/api/metrics");
  metrics.innerHTML = `
    <div class="stat"><span>Entregas</span><strong>${data.deliveries}</strong></div>
    <div class="stat"><span>Movimientos</span><strong>${data.moves}</strong></div>
    <div class="stat"><span>Pendientes</span><strong>${data.pending_packages}</strong></div>
    <div class="stat"><span>Eficiencia</span><strong>${data.efficiency}%</strong></div>
    <div class="stat"><span>Tiempo</span><strong>${data.elapsed_seconds}s</strong></div>
  `;
  const rows = await api("/api/history");
  history.innerHTML = rows.map(item => `
    <tr>
      <td>${item.id}</td><td>${new Date(item.started_at).toLocaleString()}</td><td>${item.status}</td>
      <td>${item.total_steps}</td><td>${item.deliveries}</td><td>${item.moves}</td><td>${Number(item.efficiency).toFixed(2)}%</td>
    </tr>`).join("");
}
reload.addEventListener("click", loadDashboard);
loadDashboard();

const app = document.querySelector("#app");
app.innerHTML = `
  <header class="page-head">
    <div><p class="eyebrow">ANALITICA / RESULTADOS</p><h1>Rendimiento operativo</h1><p class="page-copy">Metricas actuales e historial persistente de cada ejecucion.</p></div>
    <button id="reload" class="button outline">↻ Actualizar datos</button>
  </header>
  <section class="dashboard-hero panel">
    <div><p class="section-label">ESCENARIO ACTIVO</p><h2 id="activeScenario">—</h2><p>Las estadisticas se actualizan con cada decision ejecutada.</p></div>
    <span id="dashboardPhase" class="phase-pill ready">Listo</span>
  </section>
  <section class="dashboard-metrics" id="metrics"></section>
  <section class="panel history-panel">
    <div class="panel-head"><div><p class="section-label">TRAZABILIDAD</p><h2>Historial de simulaciones</h2></div><span id="historyCount" class="count-badge">0</span></div>
    <div class="table-wrap"><table><thead><tr><th>ID</th><th>Escenario</th><th>Inicio</th><th>Estado</th><th>Pasos</th><th>Entregas</th><th>Movimientos</th><th>Eficiencia</th></tr></thead><tbody id="history"></tbody></table></div>
  </section>
`;

function statusLabel(status) {
  return ({ ready: "Listo", running: "En ejecucion", paused: "En pausa", completed: "Completada", reset: "Reiniciada", restarted: "Reemplazada" })[status] || status;
}

async function loadDashboard() {
  const metricsElement = document.querySelector("#metrics");
  const historyElement = document.querySelector("#history");
  const activeScenarioElement = document.querySelector("#activeScenario");
  const dashboardPhaseElement = document.querySelector("#dashboardPhase");
  const historyCountElement = document.querySelector("#historyCount");
  try {
    const [data, rows] = await Promise.all([api("/api/metrics"), api("/api/history")]);
    activeScenarioElement.textContent = data.scenario;
    dashboardPhaseElement.textContent = statusLabel(data.phase);
    dashboardPhaseElement.className = `phase-pill ${data.phase}`;
    const cards = [
      ["Entregas", data.deliveries, "Paquetes completados", "✓"],
      ["Movimientos", data.moves, "Acciones de navegacion", "↗"],
      ["Pendientes", data.pending_packages, "Paquetes por atender", "□"],
      ["Eficiencia", `${data.efficiency}%`, "Entregas por movimiento", "◎"],
      ["Tiempo", `${data.elapsed_seconds}s`, "Duracion acumulada", "◷"],
    ];
    metricsElement.innerHTML = cards.map(([label, value, copy, icon]) => `
      <article class="analytics-card"><span>${icon}</span><small>${label}</small><strong>${value}</strong><p>${copy}</p></article>
    `).join("");
    historyCountElement.textContent = rows.length;
    historyElement.innerHTML = rows.length ? rows.map(item => `
      <tr><td><strong>#${item.id}</strong></td><td>${escapeHtml(item.scenario)}</td><td>${new Date(item.started_at).toLocaleString()}</td>
      <td><span class="table-status ${escapeHtml(item.status)}">${escapeHtml(statusLabel(item.status))}</span></td>
      <td>${item.total_steps}</td><td>${item.deliveries}</td><td>${item.moves}</td><td>${Number(item.efficiency).toFixed(2)}%</td></tr>
    `).join("") : '<tr><td colspan="8" class="empty-table">Aun no hay simulaciones registradas.</td></tr>';
  } catch (error) {
    historyElement.innerHTML = `<tr><td colspan="8" class="empty-table">${escapeHtml(error.message)}</td></tr>`;
  }
}

document.querySelector("#reload").addEventListener("click", loadDashboard);
loadDashboard();

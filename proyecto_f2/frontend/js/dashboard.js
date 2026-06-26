const app = document.querySelector("#app");
let selectedProcessId = null;

app.innerHTML = `
  <header class="page-head">
    <div><p class="eyebrow">ANALITICA / RESULTADOS</p><h1>Rendimiento operativo</h1><p class="page-copy">Selecciona cualquier proceso para estudiar sus decisiones y resultados.</p></div>
    <button id="reload" class="button outline">↻ Actualizar datos</button>
  </header>
  <section class="dashboard-hero panel">
    <div><p class="section-label">ESCENARIO ACTIVO</p><h2 id="activeScenario">—</h2><p>Las estadisticas se actualizan con cada decision ejecutada.</p></div>
    <span id="dashboardPhase" class="phase-pill ready">Listo</span>
  </section>
  <section class="dashboard-metrics" id="metrics"></section>
  <section class="panel history-panel">
    <div class="panel-head"><div><p class="section-label">TRAZABILIDAD</p><h2>Historial de procesos</h2></div><span id="historyCount" class="count-badge">0</span></div>
    <div class="table-wrap"><table><thead><tr><th>ID</th><th>Escenario</th><th>Inicio</th><th>Estado</th><th>Duracion</th><th>Pasos</th><th>Entregas</th><th>Eficiencia</th><th>Acciones</th></tr></thead><tbody id="history"></tbody></table></div>
  </section>
  <section id="processDetail" class="panel process-detail hidden">
    <div class="panel-head detail-head">
      <div><p class="section-label">ANALISIS INDIVIDUAL</p><h2 id="detailTitle">Proceso</h2><p id="detailSubtitle" class="detail-subtitle"></p></div>
      <div class="detail-actions">
        <span id="detailStatus" class="phase-pill ready">—</span>
        <button id="downloadSelected" class="button outline report-detail-button" disabled>Descargar reporte</button>
      </div>
    </div>
    <div id="detailMetrics" class="detail-metrics"></div>
    <div id="checkpointTrail" class="checkpoint-trail"></div>
    <div class="analysis-layout">
      <article class="analysis-block">
        <div class="block-head"><h3>Distribucion de acciones</h3><span id="totalActions"></span></div>
        <div id="actionChart" class="action-chart"></div>
      </article>
      <article class="analysis-block">
        <div class="block-head"><h3>Configuracion inicial</h3></div>
        <div id="initialSummary" class="initial-summary"></div>
      </article>
    </div>
    <article class="analysis-block timeline-block">
      <div class="block-head"><h3>Decisiones paso a paso</h3><span id="stepCount"></span></div>
      <div class="step-table-wrap"><table class="step-table"><thead><tr><th>Paso</th><th>Accion de Prolog</th><th>Explicacion</th><th>Hora</th></tr></thead><tbody id="stepHistory"></tbody></table></div>
    </article>
  </section>
`;

function statusLabel(status) {
  return ({ ready: "Listo", running: "En ejecucion", paused: "En pausa", completed: "Completada", reset: "Reiniciada", restarted: "Reemplazada" })[status] || status;
}

function actionLabel(action) {
  return ({
    mover_arriba: "Mover arriba", mover_abajo: "Mover abajo",
    mover_izquierda: "Mover izquierda", mover_derecha: "Mover derecha",
    recoger_paquete: "Recoger paquete", entregar_paquete: "Entregar paquete",
    esperar: "Esperar",
  })[action] || action;
}

function checkpointLabel(event) {
  return ({ started: "Inicio", paused: "Pausa", resumed: "Reanudacion", completed: "Finalizado", reset: "Antes de reiniciar", restarted: "Antes de reemplazar" })[event] || event;
}

function formatDuration(seconds) {
  const value = Number(seconds || 0);
  if (value < 60) return `${value.toFixed(2)} s`;
  const minutes = Math.floor(value / 60);
  return `${minutes} min ${(value % 60).toFixed(0)} s`;
}

function detailCard(label, value, copy) {
  return `<article><small>${label}</small><strong>${value}</strong><p>${copy}</p></article>`;
}

function reportFilename(response, fallback) {
  const disposition = response.headers.get("Content-Disposition") || "";
  const match = disposition.match(/filename="?([^";]+)"?/i);
  return match ? match[1] : fallback;
}

async function downloadReport(processId) {
  try {
    const response = await fetch(`${API_BASE}/api/history/${processId}/report`, { headers: { Accept: "application/pdf" } });
    if (!response.ok) {
      let message = `No se pudo descargar el reporte #${processId}`;
      try {
        const body = await response.json();
        message = body.detail || message;
      } catch (_) {}
      throw new Error(message);
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = reportFilename(response, `reporte_proceso_${processId}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  } catch (error) {
    window.alert(error.message);
  }
}

async function loadProcess(processId) {
  selectedProcessId = Number(processId);
  const detail = document.querySelector("#processDetail");
  detail.classList.remove("hidden");
  document.querySelector("#detailTitle").textContent = `Cargando proceso #${processId}...`;
  document.querySelectorAll("#history tr[data-process]").forEach(row => row.classList.toggle("selected-process", Number(row.dataset.process) === selectedProcessId));
  try {
    const data = await api(`/api/history/${processId}`);
    const simulation = data.simulation;
    const analytics = data.analytics;
    const configuration = simulation.initial_configuration;
    document.querySelector("#detailTitle").textContent = `Proceso #${simulation.id} · ${simulation.scenario}`;
    document.querySelector("#detailSubtitle").textContent = `Iniciado ${new Date(simulation.started_at).toLocaleString()} · ${formatDuration(simulation.duration_seconds)}`;
    const status = document.querySelector("#detailStatus");
    status.textContent = statusLabel(simulation.status);
    status.className = `phase-pill ${simulation.status}`;
    const downloadButton = document.querySelector("#downloadSelected");
    downloadButton.dataset.report = simulation.id;
    downloadButton.disabled = data.steps.length === 0;
    document.querySelector("#detailMetrics").innerHTML = [
      detailCard("Entregas", simulation.deliveries, `${analytics.pickups} recolecciones registradas`),
      detailCard("Movimientos", simulation.moves, `${simulation.total_steps} decisiones totales`),
      detailCard("Velocidad", `${simulation.speed?.multiplier || 1}x`, `${simulation.speed?.interval_ms || 650} ms por paso`),
      detailCard("Pasos / entrega", analytics.average_steps_per_delivery, "Promedio del proceso"),
      detailCard("Eficiencia", `${Number(simulation.efficiency).toFixed(2)}%`, "Entregas por movimiento"),
      detailCard("Esperas", analytics.waits, analytics.waits ? "Revisar bloqueos o rutas" : "Sin bloqueos registrados"),
    ].join("");
    document.querySelector("#checkpointTrail").innerHTML = `
      <span class="checkpoint-title">Guardado automatico</span>
      ${data.checkpoints.length ? data.checkpoints.map(checkpoint => `
        <span class="checkpoint-item ${escapeHtml(checkpoint.event)}"><i></i>${escapeHtml(checkpointLabel(checkpoint.event))}<small>${new Date(checkpoint.created_at).toLocaleTimeString()}</small></span>
      `).join("") : '<span class="checkpoint-empty">Proceso anterior sin checkpoints de ciclo.</span>'}
    `;

    const actionEntries = Object.entries(analytics.action_counts);
    const maxCount = Math.max(1, ...actionEntries.map(([, count]) => count));
    document.querySelector("#totalActions").textContent = `${data.steps.length} acciones`;
    document.querySelector("#actionChart").innerHTML = actionEntries.length ? actionEntries
      .sort((a, b) => b[1] - a[1])
      .map(([action, count]) => `
        <div class="action-bar-row"><span>${escapeHtml(actionLabel(action))}</span><div><i style="width:${(count / maxCount) * 100}%"></i></div><strong>${count}</strong></div>
      `).join("") : '<p class="empty-analysis">Este proceso aun no tiene acciones.</p>';

    const packages = configuration?.packages?.length ?? "—";
    const obstacles = configuration?.obstacles?.length ?? "—";
    const zones = configuration?.zones?.length ?? "—";
    const map = configuration?.map ? `${configuration.map.width} × ${configuration.map.height}` : "—";
    document.querySelector("#initialSummary").innerHTML = `
      <div><small>Mapa</small><strong>${map}</strong></div>
      <div><small>Paquetes</small><strong>${packages}</strong></div>
      <div><small>Estanterias</small><strong>${obstacles}</strong></div>
      <div><small>Zonas</small><strong>${zones}</strong></div>
    `;

    document.querySelector("#stepCount").textContent = `${data.steps.length} registros`;
    document.querySelector("#stepHistory").innerHTML = data.steps.length ? data.steps.map(step => `
      <tr><td><strong>#${step.step_number}</strong></td><td><span class="action-tag ${escapeHtml(step.action)}">${escapeHtml(actionLabel(step.action))}</span></td><td class="reason-cell">${escapeHtml(step.reason)}</td><td>${new Date(step.created_at).toLocaleTimeString()}</td></tr>
    `).join("") : '<tr><td colspan="4" class="empty-table">Este proceso no ejecuto pasos.</td></tr>';
    detail.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    document.querySelector("#detailTitle").textContent = `No fue posible analizar #${processId}`;
    document.querySelector("#detailSubtitle").textContent = error.message;
  }
}

async function loadDashboard() {
  const metricsElement = document.querySelector("#metrics");
  const historyElement = document.querySelector("#history");
  try {
    const [data, rows] = await Promise.all([api("/api/metrics"), api("/api/history")]);
    document.querySelector("#activeScenario").textContent = data.scenario;
    const phase = document.querySelector("#dashboardPhase");
    phase.textContent = statusLabel(data.phase);
    phase.className = `phase-pill ${data.phase}`;
    const cards = [
      ["Entregas", data.deliveries, "Paquetes completados", "✓"],
      ["Movimientos", data.moves, "Acciones de navegacion", "↗"],
      ["Pendientes", data.pending_packages, "Paquetes por atender", "□"],
      ["Eficiencia", `${data.efficiency}%`, "Entregas por movimiento", "◎"],
      ["Tiempo", `${data.elapsed_seconds}s`, "Duracion acumulada", "◷"],
      ["Velocidad", `${data.speed?.multiplier || 1}x`, `${data.speed?.interval_ms || 650} ms por paso`, "⚡"],
    ];
    metricsElement.innerHTML = cards.map(([label, value, copy, icon]) => `
      <article class="analytics-card"><span>${icon}</span><small>${label}</small><strong>${value}</strong><p>${copy}</p></article>
    `).join("");
    document.querySelector("#historyCount").textContent = rows.length;
    historyElement.innerHTML = rows.length ? rows.map(item => `
      <tr data-process="${item.id}" class="${Number(item.id) === selectedProcessId ? "selected-process" : ""}">
        <td><strong>#${item.id}</strong></td><td>${escapeHtml(item.scenario)}</td><td>${new Date(item.started_at).toLocaleString()}</td>
        <td><span class="table-status ${escapeHtml(item.status)}">${escapeHtml(statusLabel(item.status))}</span></td>
        <td>${formatDuration(item.duration_seconds)}</td><td>${item.total_steps}</td><td>${item.deliveries}</td><td>${Number(item.efficiency).toFixed(2)}%</td>
        <td class="table-actions">
          <button class="analyze-button" data-analyze="${item.id}">Analizar</button>
          <button class="report-button" data-report="${item.id}" ${item.has_report ? "" : "disabled"}>Descargar</button>
        </td>
      </tr>
    `).join("") : '<tr><td colspan="9" class="empty-table">Aun no hay procesos registrados.</td></tr>';
    historyElement.querySelectorAll("tr[data-process]").forEach(row => row.addEventListener("click", () => loadProcess(row.dataset.process)));
    historyElement.querySelectorAll("[data-analyze]").forEach(button => button.addEventListener("click", event => {
      event.stopPropagation();
      loadProcess(button.dataset.analyze);
    }));
    historyElement.querySelectorAll("[data-report]").forEach(button => button.addEventListener("click", event => {
      event.stopPropagation();
      downloadReport(button.dataset.report);
    }));
    if (rows.length) await loadProcess(selectedProcessId && rows.some(row => row.id === selectedProcessId) ? selectedProcessId : rows[0].id);
  } catch (error) {
    historyElement.innerHTML = `<tr><td colspan="9" class="empty-table">${escapeHtml(error.message)}</td></tr>`;
  }
}

document.querySelector("#reload").addEventListener("click", loadDashboard);
document.querySelector("#downloadSelected").addEventListener("click", event => {
  const processId = event.currentTarget.dataset.report || selectedProcessId;
  if (processId) downloadReport(processId);
});
loadDashboard();

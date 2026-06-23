const app = document.querySelector("#app");
let state = null;
let draft = null;
let scenarios = [];
let selectedPackageId = null;
let editMode = false;
let timer = null;
let busy = false;

app.innerHTML = `
  <header class="page-head">
    <div>
      <p class="eyebrow">OPERACIONES / MAPA PRINCIPAL</p>
      <h1>Bodega inteligente</h1>
      <p class="page-copy">Configura el escenario y observa cada decision producida por Prolog.</p>
    </div>
    <div class="head-status"><span id="phasePill" class="phase-pill ready">Listo</span><span id="scenarioLabel"></span></div>
  </header>

  <section class="command-deck">
    <div class="controls">
      <button id="start" class="button primary"><span>▶</span> Iniciar</button>
      <button id="pause" class="button ghost"><span>Ⅱ</span> Pausar</button>
      <button id="reset" class="button ghost danger-text"><span>↺</span> Reiniciar</button>
      <span class="control-divider"></span>
      <button id="step" class="button accent"><span>›</span> Ejecutar paso</button>
      <button id="auto" class="button dark"><span>↠</span> Automatico</button>
    </div>
    <div class="scenario-picker">
      <label for="scenarioSelect">Escenario</label>
      <select id="scenarioSelect"></select>
      <button id="loadScenario" class="icon-button" title="Cargar escenario">↳</button>
      <button id="editScenario" class="button outline">Editar mapa</button>
    </div>
  </section>

  <section class="simulation-layout">
    <div class="panel board-panel">
      <div class="panel-head">
        <div><p class="section-label">PLANO OPERATIVO</p><h2 id="boardTitle">Distribucion 10 × 10</h2></div>
        <div class="map-mode" id="mapMode"><span class="live-dot"></span> Vista de simulacion</div>
      </div>
      <div id="editorBanner" class="editor-banner hidden">
        <div><strong>Modo diseño activo</strong><span>Selecciona una caja y luego una casilla libre. Tambien puedes arrastrarla.</span></div>
        <button id="cancelEdit" class="text-button">Salir sin aplicar</button>
      </div>
      <div class="board-wrap"><div class="board" id="board"></div></div>
      <div class="legend">
        <div><span class="legend-token robot-mini">R</span>Robot</div>
        <div><span class="legend-token package-mini">P</span>Paquete</div>
        <div><span class="legend-token obstacle-mini"></span>Estanteria</div>
        <div><span class="legend-token zonea-mini">A</span>Entrega A</div>
        <div><span class="route-mini"></span>Ruta calculada</div>
      </div>
    </div>

    <aside class="right-rail">
      <section class="panel decision-panel">
        <div class="panel-head compact"><div><p class="section-label">DECISION ACTUAL</p><h2 id="actionTitle">Esperando inicio</h2></div><span id="sourceBadge" class="source-badge">PROLOG</span></div>
        <p id="message" class="decision-copy">El escenario esta listo para iniciar.</p>
        <div class="route-summary"><span>Objetivo <strong id="targetValue">—</strong></span><span>Ruta <strong id="routeValue">0 pasos</strong></span></div>
      </section>

      <section class="metric-grid" id="metrics"></section>

      <section id="editorPanel" class="panel editor-panel hidden">
        <div class="panel-head compact"><div><p class="section-label">EDITOR</p><h2>Colocar paquetes</h2></div><span class="edit-badge">BORRADOR</span></div>
        <p class="helper">Las zonas, obstaculos y el robot quedan protegidos para mantener un escenario valido.</p>
        <div id="packageTools" class="package-tools"></div>
        <label class="field-label" for="zoneSelect">Zona asignada</label>
        <select id="zoneSelect" class="wide-select"></select>
        <div class="editor-actions">
          <button id="applyDesign" class="button primary">Aplicar diseño</button>
          <button id="saveAs" class="button outline">Guardar como</button>
          <button id="updateSaved" class="button ghost">Actualizar</button>
        </div>
        <p id="editorHint" class="editor-hint">Selecciona un paquete para comenzar.</p>
      </section>

      <section class="panel packages-panel">
        <div class="panel-head compact"><div><p class="section-label">INVENTARIO</p><h2>Paquetes</h2></div><span id="packageCount" class="count-badge">0</span></div>
        <div id="packages" class="package-list"></div>
      </section>
    </aside>
  </section>
  <div id="toast" class="toast" role="status"></div>
`;

const $ = selector => document.querySelector(selector);

function configurationFrom(source) {
  return {
    map: { ...source.map },
    robots: source.robots.map(item => ({ ...item, status: "libre", carrying: "none" })),
    packages: source.packages.map(item => ({ ...item, status: "pendiente" })),
    zones: source.zones.map(item => ({ ...item })),
    obstacles: source.obstacles.map(item => ({ ...item })),
  };
}

function notify(message, type = "ok") {
  const toast = $("#toast");
  toast.textContent = message;
  toast.className = `toast show ${type}`;
  window.setTimeout(() => { toast.className = "toast"; }, 3200);
}

function phaseInfo() {
  const phases = {
    ready: ["Listo", "ready"], running: ["En ejecucion", "running"],
    paused: ["En pausa", "paused"], completed: ["Completado", "completed"],
  };
  return phases[state?.phase] || phases.ready;
}

function actionLabel(action) {
  return ({
    mover_arriba: "Moviendo hacia arriba", mover_abajo: "Moviendo hacia abajo",
    mover_izquierda: "Moviendo a la izquierda", mover_derecha: "Moviendo a la derecha",
    recoger_paquete: "Recogiendo paquete", entregar_paquete: "Entrega completada",
    esperar: "Esperando una ruta valida",
  })[action] || "Esperando inicio";
}

function currentView() {
  return editMode ? draft : state;
}

function routeIndex(x, y) {
  if (editMode || !state.last_route) return -1;
  return state.last_route.findIndex(item => item.x === x && item.y === y);
}

function cellMarkup(view, x, y) {
  const robot = view.robots.find(item => item.x === x && item.y === y);
  const pack = view.packages.find(item => item.x === x && item.y === y && item.status !== "entregado");
  const zone = view.zones.find(item => item.x === x && item.y === y);
  const obstacle = view.obstacles.some(item => item.x === x && item.y === y);
  const routeStep = routeIndex(x, y);
  const classes = ["cell"];
  if (zone) classes.push("zone", zone.id === "zona_a" ? "zone-a" : "zone-b");
  if (obstacle) classes.push("obstacle");
  if (routeStep >= 0) classes.push("route-cell");
  if (selectedPackageId && editMode && canMovePackage(x, y)) classes.push("valid-target");
  if (pack?.id === selectedPackageId && editMode) classes.push("selected-cell");

  let entity = "";
  if (obstacle) entity = '<span class="rack"><i></i><i></i><i></i></span>';
  if (zone) entity += `<span class="zone-token">${zone.id === "zona_a" ? "A" : "B"}<small>DROP</small></span>`;
  if (pack) entity += `<span class="package-token ${pack.id === selectedPackageId ? "selected" : ""}" draggable="${editMode}" data-package="${escapeHtml(pack.id)}"><i></i><strong>${escapeHtml(pack.id.toUpperCase())}</strong></span>`;
  if (robot) entity += `<span class="robot-token"><i>◆</i><strong>${escapeHtml(robot.id.toUpperCase())}</strong></span>`;
  if (routeStep >= 0) entity += `<span class="route-step">${routeStep + 1}</span>`;
  return `<button class="${classes.join(" ")}" data-x="${x}" data-y="${y}" title="Casilla ${x},${y}"><span class="coord">${x}.${y}</span>${entity}</button>`;
}

function renderBoard() {
  const view = currentView();
  const board = $("#board");
  board.style.setProperty("--columns", view.map.width);
  board.innerHTML = "";
  for (let y = 1; y <= view.map.height; y += 1) {
    for (let x = 1; x <= view.map.width; x += 1) board.insertAdjacentHTML("beforeend", cellMarkup(view, x, y));
  }
  board.querySelectorAll(".cell").forEach(cell => {
    cell.addEventListener("click", () => moveSelectedPackage(Number(cell.dataset.x), Number(cell.dataset.y)));
    cell.addEventListener("dragover", event => { if (editMode) event.preventDefault(); });
    cell.addEventListener("drop", event => {
      event.preventDefault();
      selectedPackageId = event.dataTransfer.getData("text/plain") || selectedPackageId;
      moveSelectedPackage(Number(cell.dataset.x), Number(cell.dataset.y));
    });
  });
  board.querySelectorAll(".package-token").forEach(token => {
    token.addEventListener("click", event => {
      if (!editMode) return;
      event.stopPropagation();
      selectPackage(token.dataset.package);
    });
    token.addEventListener("dragstart", event => {
      selectedPackageId = token.dataset.package;
      event.dataTransfer.setData("text/plain", token.dataset.package);
    });
  });
}

function canMovePackage(x, y) {
  if (!draft || !selectedPackageId) return false;
  const blocked = [
    ...draft.robots,
    ...draft.zones,
    ...draft.obstacles,
    ...draft.packages.filter(item => item.id !== selectedPackageId),
  ];
  return !blocked.some(item => item.x === x && item.y === y);
}

function moveSelectedPackage(x, y) {
  if (!editMode || !selectedPackageId) return;
  if (!canMovePackage(x, y)) {
    notify("Esa casilla esta ocupada o protegida.", "error");
    return;
  }
  const pack = draft.packages.find(item => item.id === selectedPackageId);
  pack.x = x;
  pack.y = y;
  $("#editorHint").textContent = `${pack.id.toUpperCase()} se colocara en (${x}, ${y}).`;
  render();
}

function selectPackage(packageId) {
  selectedPackageId = packageId;
  const pack = draft.packages.find(item => item.id === packageId);
  $("#zoneSelect").value = pack.zone;
  $("#editorHint").textContent = `${pack.id.toUpperCase()} seleccionado en (${pack.x}, ${pack.y}).`;
  render();
}

function renderMetrics() {
  const pending = state.packages.filter(item => item.status !== "entregado").length;
  const values = [
    ["Entregas", state.deliveries, "✓"], ["Movimientos", state.moves, "↗"],
    ["Pasos", state.steps, "#"], ["Pendientes", pending, "□"],
  ];
  $("#metrics").innerHTML = values.map(([label, value, icon]) => `
    <article class="metric-card"><span class="metric-icon">${icon}</span><div><small>${label}</small><strong>${value}</strong></div></article>
  `).join("");
}

function renderPackages() {
  const view = currentView();
  $("#packageCount").textContent = view.packages.length;
  $("#packages").innerHTML = view.packages.map(item => `
    <button class="package-row ${editMode && item.id === selectedPackageId ? "selected" : ""}" data-select="${escapeHtml(item.id)}">
      <span class="package-symbol"><i></i></span>
      <span><strong>${escapeHtml(item.id.toUpperCase())}</strong><small>Destino ${escapeHtml(item.zone.replace("zona_", "").toUpperCase())} · (${item.x}, ${item.y})</small></span>
      <em class="status-${escapeHtml(item.status)}">${escapeHtml(item.status.replace("_", " "))}</em>
    </button>
  `).join("");
  $("#packages").querySelectorAll("[data-select]").forEach(button => {
    button.addEventListener("click", () => { if (editMode) selectPackage(button.dataset.select); });
  });
}

function renderEditor() {
  $("#editorPanel").classList.toggle("hidden", !editMode);
  $("#editorBanner").classList.toggle("hidden", !editMode);
  $("#mapMode").innerHTML = editMode ? '<span class="edit-dot"></span> Modo diseño' : '<span class="live-dot"></span> Vista de simulacion';
  if (!editMode) return;
  $("#packageTools").innerHTML = draft.packages.map(item => `
    <button class="package-chip ${item.id === selectedPackageId ? "selected" : ""}" data-package-tool="${escapeHtml(item.id)}">${escapeHtml(item.id.toUpperCase())}</button>
  `).join("");
  $("#packageTools").querySelectorAll("[data-package-tool]").forEach(button => {
    button.addEventListener("click", () => selectPackage(button.dataset.packageTool));
  });
  $("#zoneSelect").innerHTML = draft.zones.map(zone => `<option value="${escapeHtml(zone.id)}">${escapeHtml(zone.id.replace("zona_", "Zona ").toUpperCase())}</option>`).join("");
  if (selectedPackageId) $("#zoneSelect").value = draft.packages.find(item => item.id === selectedPackageId).zone;
  $("#updateSaved").classList.toggle("hidden", !state.scenario.id || state.scenario.is_default);
}

function renderScenarios() {
  const select = $("#scenarioSelect");
  select.innerHTML = scenarios.map(item => `<option value="${item.id}">${escapeHtml(item.name)}${item.is_default ? " · base" : ""}</option>`).join("");
  if (state.scenario.id) select.value = String(state.scenario.id);
}

function renderControls() {
  const active = state.simulation_id !== null;
  const completed = state.phase === "completed";
  $("#start").disabled = active || busy || editMode;
  $("#pause").disabled = !active || completed || busy || editMode;
  $("#step").disabled = completed || busy || editMode;
  $("#auto").disabled = completed || busy || editMode;
  $("#editScenario").disabled = active || busy;
  $("#loadScenario").disabled = active || busy || editMode;
  $("#scenarioSelect").disabled = active || busy || editMode;
}

function render() {
  if (!state) return;
  const [phaseLabel, phaseClass] = phaseInfo();
  $("#phasePill").textContent = phaseLabel;
  $("#phasePill").className = `phase-pill ${phaseClass}`;
  $("#scenarioLabel").textContent = `${state.scenario.name}${state.scenario.dirty ? " · sin guardar" : ""}`;
  $("#boardTitle").textContent = `Distribucion ${currentView().map.width} × ${currentView().map.height}`;
  $("#actionTitle").textContent = actionLabel(state.last_action);
  $("#message").textContent = state.last_reason || "El escenario esta listo para iniciar.";
  $("#sourceBadge").classList.toggle("muted", !state.last_source);
  $("#targetValue").textContent = state.last_target ? `(${state.last_target.x}, ${state.last_target.y})` : "—";
  $("#routeValue").textContent = `${state.last_route?.length || 0} pasos`;
  renderBoard();
  renderMetrics();
  renderPackages();
  renderEditor();
  renderScenarios();
  renderControls();
}

async function loadScenarios() {
  scenarios = await api("/api/scenarios");
}

async function refresh() {
  [state] = await Promise.all([api("/api/simulation/state"), loadScenarios()]);
  render();
}

async function command(path, options = { method: "POST" }) {
  let succeeded = false;
  try {
    busy = true;
    renderControls();
    state = await api(path, options);
    succeeded = true;
    render();
  } catch (error) {
    notify(error.message, "error");
  } finally {
    busy = false;
    renderControls();
  }
  return succeeded;
}

function stopAuto(message = "") {
  if (timer) window.clearInterval(timer);
  timer = null;
  $("#auto").innerHTML = "<span>↠</span> Automatico";
  if (message) notify(message);
}

function enterEditor() {
  if (state.simulation_id !== null) return notify("Reinicia la simulacion antes de editar el mapa.", "error");
  editMode = true;
  draft = configurationFrom(state);
  selectedPackageId = draft.packages[0].id;
  render();
}

function leaveEditor() {
  editMode = false;
  draft = null;
  selectedPackageId = null;
  render();
}

async function applyDesign() {
  const applied = await command("/api/simulation/configuration", {
    method: "PUT", body: JSON.stringify({ configuration: draft }),
  });
  if (!applied) return;
  editMode = false;
  draft = null;
  selectedPackageId = null;
  render();
  notify("Diseño aplicado. Ya puedes iniciar la simulacion.");
}

async function saveScenario(update = false) {
  const current = scenarios.find(item => item.id === state.scenario.id);
  const suggested = update && current ? current.name : `Escenario ${scenarios.length + 1}`;
  const name = window.prompt("Nombre del escenario", suggested);
  if (!name?.trim()) return;
  try {
    const path = update ? `/api/scenarios/${current.id}` : "/api/scenarios";
    const method = update ? "PUT" : "POST";
    const saved = await api(path, { method, body: JSON.stringify({ name: name.trim(), configuration: draft }) });
    state = await api(`/api/scenarios/${saved.id}/activate`, { method: "POST" });
    await loadScenarios();
    editMode = false;
    draft = null;
    selectedPackageId = null;
    render();
    notify(update ? "Escenario actualizado." : "Escenario guardado y activado.");
  } catch (error) {
    notify(error.message, "error");
  }
}

$("#start").addEventListener("click", () => command("/api/simulation/start"));
$("#pause").addEventListener("click", () => { stopAuto(); command("/api/simulation/pause"); });
$("#reset").addEventListener("click", () => { stopAuto(); command("/api/simulation/reset"); });
$("#step").addEventListener("click", () => command("/api/simulation/step"));
$("#auto").addEventListener("click", () => {
  if (timer) return stopAuto("Modo automatico detenido.");
  $("#auto").innerHTML = "<span>■</span> Detener";
  timer = window.setInterval(async () => {
    const progressed = await command("/api/simulation/step");
    if (!progressed) return stopAuto("El modo automatico se detuvo por un error.");
    if (state.phase === "completed" || state.last_action === "esperar") stopAuto(state.phase === "completed" ? "Todas las entregas fueron completadas." : "Prolog no encontro una ruta disponible.");
  }, 650);
});
$("#editScenario").addEventListener("click", enterEditor);
$("#cancelEdit").addEventListener("click", leaveEditor);
$("#applyDesign").addEventListener("click", applyDesign);
$("#saveAs").addEventListener("click", () => saveScenario(false));
$("#updateSaved").addEventListener("click", () => saveScenario(true));
$("#zoneSelect").addEventListener("change", event => {
  if (!selectedPackageId) return;
  draft.packages.find(item => item.id === selectedPackageId).zone = event.target.value;
  renderPackages();
});
$("#loadScenario").addEventListener("click", async () => {
  const id = $("#scenarioSelect").value;
  const loaded = await command(`/api/scenarios/${id}/activate`);
  if (loaded) notify("Escenario cargado.");
});

refresh().catch(error => notify(error.message, "error"));

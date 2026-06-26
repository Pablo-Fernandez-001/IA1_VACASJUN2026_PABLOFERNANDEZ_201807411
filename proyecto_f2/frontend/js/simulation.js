const app = document.querySelector("#app");
let state = null;
let draft = null;
let scenarios = [];
let selectedEntity = null;
let editorTab = "packages";
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
    <div class="speed-picker">
      <label for="speedSelect">Velocidad</label>
      <select id="speedSelect"></select>
      <span id="speedHint">650 ms/paso</span>
    </div>
    <div class="scenario-picker">
      <label for="scenarioSelect">Escenario</label>
      <select id="scenarioSelect"></select>
      <button id="loadScenario" class="icon-button" title="Cargar escenario">↳</button>
      <button id="deleteScenario" class="icon-button delete-icon" title="Eliminar escenario">×</button>
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
        <div><strong>Modo diseño activo</strong><span>Mueve cajas y estanterias; tambien puedes administrar el inventario.</span></div>
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
        <div class="panel-head compact"><div><p class="section-label">EDITOR</p><h2 id="editorTitle">Elementos del mapa</h2></div><span class="edit-badge">BORRADOR</span></div>
        <div class="editor-tabs">
          <button id="packagesTab" class="editor-tab active">Paquetes</button>
          <button id="obstaclesTab" class="editor-tab">Estanterias</button>
          <button id="zonesTab" class="editor-tab">Zonas A/B</button>
        </div>
        <p id="editorHelp" class="helper">Selecciona, arrastra, agrega o elimina paquetes.</p>
        <div id="entityTools" class="entity-tools"></div>
        <div id="packageFields">
          <label class="field-label" for="zoneSelect">Zona asignada</label>
          <select id="zoneSelect" class="wide-select"></select>
          <div class="inventory-actions">
            <button id="addPackage" class="button accent">+ Añadir paquete</button>
            <button id="removePackage" class="button ghost danger-text">Eliminar seleccionado</button>
          </div>
          <p id="complianceHint" class="compliance-hint"></p>
        </div>
        <div id="obstacleFields" class="hidden">
          <div class="inventory-actions">
            <button id="addObstacle" class="button accent">+ Añadir estanteria</button>
            <button id="removeObstacle" class="button ghost danger-text">Eliminar seleccionada</button>
          </div>
          <p id="obstacleComplianceHint" class="compliance-hint"></p>
        </div>
        <div class="editor-actions">
          <button id="applyDesign" class="button primary">Aplicar diseño</button>
          <button id="saveAs" class="button outline">Guardar como</button>
          <button id="updateSaved" class="button ghost">Actualizar</button>
        </div>
        <p id="editorHint" class="editor-hint">Selecciona un elemento para comenzar.</p>
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
  const obstacleIndex = view.obstacles.findIndex(item => item.x === x && item.y === y);
  const obstacle = obstacleIndex >= 0;
  const routeStep = routeIndex(x, y);
  const packageSelected = selectedEntity?.type === "package" && pack?.id === selectedEntity.id;
  const obstacleSelected = selectedEntity?.type === "obstacle" && obstacleIndex === selectedEntity.index;
  const zoneSelected = selectedEntity?.type === "zone" && zone?.id === selectedEntity.id;
  const classes = ["cell"];
  if (zone) classes.push("zone", zone.id === "zona_a" ? "zone-a" : "zone-b");
  if (obstacle) classes.push("obstacle");
  if (routeStep >= 0) classes.push("route-cell");
  if (selectedEntity && editMode && canPlaceSelected(x, y)) classes.push("valid-target");
  if (packageSelected || obstacleSelected || zoneSelected) classes.push("selected-cell");

  let entity = "";
  if (obstacle) entity = `<span class="rack ${obstacleSelected ? "selected" : ""}" draggable="${editMode}" data-obstacle="${obstacleIndex}"><i></i><i></i><i></i></span>`;
  if (zone) entity += `<span class="zone-token ${zoneSelected ? "selected" : ""}" draggable="${editMode}" data-zone="${escapeHtml(zone.id)}">${zone.id === "zona_a" ? "A" : "B"}<small>DROP</small></span>`;
  if (pack) entity += `<span class="package-token ${packageSelected ? "selected" : ""}" draggable="${editMode}" data-package="${escapeHtml(pack.id)}"><i></i><strong>${escapeHtml(pack.id.toUpperCase())}</strong></span>`;
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
    cell.addEventListener("click", () => moveSelectedEntity(Number(cell.dataset.x), Number(cell.dataset.y)));
    cell.addEventListener("dragover", event => { if (editMode) event.preventDefault(); });
    cell.addEventListener("drop", event => {
      event.preventDefault();
      readDraggedEntity(event.dataTransfer.getData("text/plain"));
      moveSelectedEntity(Number(cell.dataset.x), Number(cell.dataset.y));
    });
  });
  board.querySelectorAll(".package-token").forEach(token => {
    token.addEventListener("click", event => {
      if (!editMode) return;
      event.stopPropagation();
      selectEntity("package", token.dataset.package);
    });
    token.addEventListener("dragstart", event => {
      selectedEntity = { type: "package", id: token.dataset.package };
      event.dataTransfer.setData("text/plain", `package:${token.dataset.package}`);
    });
  });
  board.querySelectorAll(".rack").forEach(rack => {
    rack.addEventListener("click", event => {
      if (!editMode) return;
      event.stopPropagation();
      selectEntity("obstacle", Number(rack.dataset.obstacle));
    });
    rack.addEventListener("dragstart", event => {
      selectedEntity = { type: "obstacle", index: Number(rack.dataset.obstacle) };
      event.dataTransfer.setData("text/plain", `obstacle:${rack.dataset.obstacle}`);
    });
  });
  board.querySelectorAll(".zone-token").forEach(token => {
    token.addEventListener("click", event => {
      if (!editMode) return;
      event.stopPropagation();
      selectEntity("zone", token.dataset.zone);
    });
    token.addEventListener("dragstart", event => {
      selectedEntity = { type: "zone", id: token.dataset.zone };
      event.dataTransfer.setData("text/plain", `zone:${token.dataset.zone}`);
    });
  });
}

function readDraggedEntity(value) {
  const [type, key] = value.split(":");
  if (type === "package") selectedEntity = { type, id: key };
  if (type === "obstacle") selectedEntity = { type, index: Number(key) };
  if (type === "zone") selectedEntity = { type, id: key };
}

function canPlaceSelected(x, y) {
  if (!draft || !selectedEntity) return false;
  const blocked = [
    ...draft.robots,
    ...draft.zones.filter(item => selectedEntity.type !== "zone" || item.id !== selectedEntity.id),
    ...draft.obstacles.filter((_, index) => selectedEntity.type !== "obstacle" || index !== selectedEntity.index),
    ...draft.packages.filter(item => selectedEntity.type !== "package" || item.id !== selectedEntity.id),
  ];
  return !blocked.some(item => item.x === x && item.y === y);
}

function moveSelectedEntity(x, y) {
  if (!editMode || !selectedEntity) return;
  if (!canPlaceSelected(x, y)) {
    notify("Esa casilla esta ocupada o protegida.", "error");
    return;
  }
  const entity = selectedEntity.type === "package"
    ? draft.packages.find(item => item.id === selectedEntity.id)
    : selectedEntity.type === "obstacle"
      ? draft.obstacles[selectedEntity.index]
      : draft.zones.find(item => item.id === selectedEntity.id);
  entity.x = x;
  entity.y = y;
  const label = selectedEntity.type === "package"
    ? selectedEntity.id.toUpperCase()
    : selectedEntity.type === "obstacle"
      ? `Estanteria ${selectedEntity.index + 1}`
      : `Zona ${selectedEntity.id.replace("zona_", "").toUpperCase()}`;
  $("#editorHint").textContent = `${label} se colocara en (${x}, ${y}).`;
  render();
}

function selectEntity(type, key) {
  editorTab = type === "package" ? "packages" : type === "obstacle" ? "obstacles" : "zones";
  selectedEntity = type === "obstacle" ? { type, index: key } : { type, id: key };
  const entity = type === "package"
    ? draft.packages.find(item => item.id === key)
    : type === "obstacle"
      ? draft.obstacles[key]
      : draft.zones.find(item => item.id === key);
  const label = type === "package" ? entity.id.toUpperCase() : type === "obstacle" ? `Estanteria ${key + 1}` : `Zona ${entity.id.replace("zona_", "").toUpperCase()}`;
  $("#editorHint").textContent = `${label} seleccionado en (${entity.x}, ${entity.y}).`;
  render();
}

function firstFreeCell() {
  for (let y = 1; y <= draft.map.height; y += 1) {
    for (let x = 1; x <= draft.map.width; x += 1) {
      const occupied = [...draft.robots, ...draft.zones, ...draft.obstacles, ...draft.packages]
        .some(item => item.x === x && item.y === y);
      if (!occupied) return { x, y };
    }
  }
  return null;
}

function nextPackageId() {
  const ids = new Set(draft.packages.map(item => item.id));
  let number = 1;
  while (ids.has(`p${number}`)) number += 1;
  return `p${number}`;
}

function addPackage() {
  const position = firstFreeCell();
  if (!position) return notify("No hay una casilla libre para otro paquete.", "error");
  const packageId = nextPackageId();
  draft.packages.push({ id: packageId, ...position, zone: draft.zones[0].id, status: "pendiente" });
  selectEntity("package", packageId);
  notify(`${packageId.toUpperCase()} añadido al escenario.`);
}

function removeSelectedPackage() {
  if (selectedEntity?.type !== "package") return notify("Selecciona primero un paquete.", "error");
  const index = draft.packages.findIndex(item => item.id === selectedEntity.id);
  const removed = draft.packages[index];
  draft.packages.splice(index, 1);
  selectedEntity = draft.packages.length ? { type: "package", id: draft.packages[Math.min(index, draft.packages.length - 1)].id } : null;
  render();
  notify(`${removed.id.toUpperCase()} eliminado del escenario.`);
}

function addObstacle() {
  const position = firstFreeCell();
  if (!position) return notify("No hay una casilla libre para otra estanteria.", "error");
  draft.obstacles.push(position);
  selectEntity("obstacle", draft.obstacles.length - 1);
  notify(`Estanteria ${draft.obstacles.length} añadida al escenario.`);
}

function removeSelectedObstacle() {
  if (selectedEntity?.type !== "obstacle") return notify("Selecciona primero una estanteria.", "error");
  if (draft.obstacles.length <= 8) return notify("El escenario debe conservar al menos 8 estanterias.", "error");
  const removedIndex = selectedEntity.index;
  draft.obstacles.splice(removedIndex, 1);
  selectedEntity = { type: "obstacle", index: Math.min(removedIndex, draft.obstacles.length - 1) };
  render();
  notify("Estanteria eliminada del escenario.");
}

function renderMetrics() {
  const pending = state.packages.filter(item => item.status !== "entregado").length;
  const values = [
    ["Entregas", state.deliveries, "✓"], ["Movimientos", state.moves, "↗"],
    ["Pasos", state.steps, "#"], ["Pendientes", pending, "□"],
    ["Velocidad", `${state.speed?.multiplier || 1}x`, "⚡"],
  ];
  $("#metrics").innerHTML = values.map(([label, value, icon]) => `
    <article class="metric-card"><span class="metric-icon">${icon}</span><div><small>${label}</small><strong>${value}</strong></div></article>
  `).join("");
}

function renderPackages() {
  const view = currentView();
  $("#packageCount").textContent = view.packages.length;
  $("#packages").innerHTML = view.packages.length ? view.packages.map(item => `
    <button class="package-row ${editMode && selectedEntity?.type === "package" && item.id === selectedEntity.id ? "selected" : ""}" data-select="${escapeHtml(item.id)}">
      <span class="package-symbol"><i></i></span>
      <span><strong>${escapeHtml(item.id.toUpperCase())}</strong><small>Destino ${escapeHtml(item.zone.replace("zona_", "").toUpperCase())} · (${item.x}, ${item.y})</small></span>
      <em class="status-${escapeHtml(item.status)}">${escapeHtml(item.status.replace("_", " "))}</em>
    </button>
  `).join("") : '<p class="empty-inventory">Este escenario no contiene paquetes.</p>';
  $("#packages").querySelectorAll("[data-select]").forEach(button => {
    button.addEventListener("click", () => { if (editMode) selectEntity("package", button.dataset.select); });
  });
}

function renderEditor() {
  $("#editorPanel").classList.toggle("hidden", !editMode);
  $("#editorBanner").classList.toggle("hidden", !editMode);
  $("#mapMode").innerHTML = editMode ? '<span class="edit-dot"></span> Modo diseño' : '<span class="live-dot"></span> Vista de simulacion';
  if (!editMode) return;
  $("#packagesTab").classList.toggle("active", editorTab === "packages");
  $("#obstaclesTab").classList.toggle("active", editorTab === "obstacles");
  $("#zonesTab").classList.toggle("active", editorTab === "zones");
  $("#packageFields").classList.toggle("hidden", editorTab !== "packages");
  $("#obstacleFields").classList.toggle("hidden", editorTab !== "obstacles");
  $("#editorTitle").textContent = editorTab === "packages" ? "Administrar paquetes" : editorTab === "obstacles" ? "Administrar estanterias" : "Mover zonas de entrega";
  $("#editorHelp").textContent = editorTab === "packages"
    ? "Selecciona, arrastra, agrega o elimina paquetes."
    : editorTab === "obstacles"
      ? "Selecciona, mueve o añade estanterias al mapa."
      : "Mueve libremente los puntos A y B sin superponer elementos.";
  if (editorTab === "packages") {
    $("#entityTools").innerHTML = draft.packages.length ? draft.packages.map(item => `
      <button class="package-chip ${selectedEntity?.type === "package" && item.id === selectedEntity.id ? "selected" : ""}" data-package-tool="${escapeHtml(item.id)}">${escapeHtml(item.id.toUpperCase())}</button>
    `).join("") : '<span class="empty-tools">Sin paquetes</span>';
    $("#entityTools").querySelectorAll("[data-package-tool]").forEach(button => {
      button.addEventListener("click", () => selectEntity("package", button.dataset.packageTool));
    });
  } else if (editorTab === "obstacles") {
    $("#entityTools").innerHTML = draft.obstacles.map((item, index) => `
      <button class="obstacle-chip ${selectedEntity?.type === "obstacle" && index === selectedEntity.index ? "selected" : ""}" data-obstacle-tool="${index}">E${index + 1}<small>${item.x},${item.y}</small></button>
    `).join("");
    $("#entityTools").querySelectorAll("[data-obstacle-tool]").forEach(button => {
      button.addEventListener("click", () => selectEntity("obstacle", Number(button.dataset.obstacleTool)));
    });
  } else {
    $("#entityTools").innerHTML = draft.zones.map(zone => `
      <button class="zone-chip ${selectedEntity?.type === "zone" && zone.id === selectedEntity.id ? "selected" : ""}" data-zone-tool="${escapeHtml(zone.id)}">
        <strong>${zone.id === "zona_a" ? "A" : "B"}</strong><small>${zone.x},${zone.y}</small>
      </button>
    `).join("");
    $("#entityTools").querySelectorAll("[data-zone-tool]").forEach(button => {
      button.addEventListener("click", () => selectEntity("zone", button.dataset.zoneTool));
    });
  }
  $("#zoneSelect").innerHTML = draft.zones.map(zone => `<option value="${escapeHtml(zone.id)}">${escapeHtml(zone.id.replace("zona_", "Zona ").toUpperCase())}</option>`).join("");
  const selectedPackage = selectedEntity?.type === "package" ? draft.packages.find(item => item.id === selectedEntity.id) : null;
  if (selectedPackage) $("#zoneSelect").value = selectedPackage.zone;
  $("#zoneSelect").disabled = !selectedPackage;
  $("#removePackage").disabled = !selectedPackage;
  const missing = Math.max(0, 5 - draft.packages.length);
  $("#complianceHint").className = `compliance-hint ${missing ? "warning" : "ok"}`;
  $("#complianceHint").textContent = missing
    ? `Escenario personalizado valido. Para la evaluacion agrega ${missing} paquete${missing === 1 ? "" : "s"} mas.`
    : `Cumple el minimo academico de 5 paquetes (${draft.packages.length} actuales).`;
  const removableObstacles = Math.max(0, draft.obstacles.length - 8);
  $("#removeObstacle").disabled = selectedEntity?.type !== "obstacle" || !removableObstacles;
  $("#obstacleComplianceHint").className = "compliance-hint ok";
  $("#obstacleComplianceHint").textContent = `${draft.obstacles.length} estanterias; el minimo academico es 8.`;
  $("#updateSaved").classList.toggle("hidden", !state.scenario.id || state.scenario.is_default);
}

function renderScenarios() {
  const select = $("#scenarioSelect");
  select.innerHTML = scenarios.map(item => `<option value="${item.id}">${escapeHtml(item.name)}${item.is_default ? " · base" : ""}</option>`).join("");
  if (state.scenario.id) select.value = String(state.scenario.id);
}

function renderSpeedPicker() {
  const options = state.speed_options?.length ? state.speed_options : [
    { key: "lenta", label: "Lenta", interval_ms: 1100, multiplier: 0.5 },
    { key: "normal", label: "Normal", interval_ms: 650, multiplier: 1 },
    { key: "rapida", label: "Rapida", interval_ms: 350, multiplier: 2 },
    { key: "turbo", label: "Turbo", interval_ms: 180, multiplier: 4 },
  ];
  $("#speedSelect").innerHTML = options.map(option => `
    <option value="${escapeHtml(option.key)}">${escapeHtml(option.label)} · ${option.multiplier}x</option>
  `).join("");
  $("#speedSelect").value = state.speed?.key || "normal";
  $("#speedHint").textContent = `${state.speed?.interval_ms || 650} ms/paso`;
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
  $("#speedSelect").disabled = busy || editMode;
  const selectedScenario = scenarios.find(item => String(item.id) === $("#scenarioSelect").value);
  $("#deleteScenario").disabled = active || busy || editMode || !selectedScenario || selectedScenario.is_default;
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
  renderSpeedPicker();
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
    if (state.scenario?.id && !scenarios.some(item => item.id === state.scenario.id)) await loadScenarios();
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

function autoDelay() {
  return Number(state?.speed?.interval_ms || 650);
}

async function autoTick() {
  if (busy) return;
  const progressed = await command("/api/simulation/step");
  if (!progressed) return stopAuto("El modo automatico se detuvo por un error.");
  if (state.phase === "completed" || state.last_action === "esperar") {
    stopAuto(state.phase === "completed" ? "Todas las entregas fueron completadas." : "Prolog no encontro una ruta disponible.");
  }
}

function restartAutoTimer() {
  if (!timer) return;
  window.clearInterval(timer);
  timer = window.setInterval(autoTick, autoDelay());
}

function enterEditor() {
  if (state.simulation_id !== null) return notify("Reinicia la simulacion antes de editar el mapa.", "error");
  editMode = true;
  draft = configurationFrom(state);
  editorTab = "packages";
  selectedEntity = draft.packages.length ? { type: "package", id: draft.packages[0].id } : null;
  render();
}

function leaveEditor() {
  editMode = false;
  draft = null;
  selectedEntity = null;
  render();
}

async function applyDesign() {
  const applied = await command("/api/simulation/configuration", {
    method: "PUT", body: JSON.stringify({ configuration: draft }),
  });
  if (!applied) return;
  editMode = false;
  draft = null;
  selectedEntity = null;
  render();
  notify("Diseño aplicado. Ya puedes iniciar la simulacion.");
}

function askScenarioName(suggested) {
  return new Promise(resolve => {
    const overlay = document.createElement("div");
    overlay.className = "name-dialog-backdrop";
    overlay.innerHTML = `
      <section class="name-dialog" role="dialog" aria-modal="true" aria-labelledby="scenarioNameTitle">
        <p class="section-label">ESCENARIO</p>
        <h2 id="scenarioNameTitle">Nombre del escenario</h2>
        <p class="helper">Escribe un nombre para guardar esta configuración.</p>
        <input id="scenarioNameInput" class="name-input" maxlength="80" value="${escapeHtml(suggested)}">
        <div class="name-dialog-actions">
          <button id="cancelScenarioName" class="button ghost" type="button">Cancelar</button>
          <button id="acceptScenarioName" class="button primary" type="button">Guardar</button>
        </div>
      </section>
    `;
    document.body.appendChild(overlay);
    const input = overlay.querySelector("#scenarioNameInput");
    const close = value => {
      overlay.remove();
      resolve(value);
    };
    overlay.querySelector("#cancelScenarioName").addEventListener("click", () => close(null));
    overlay.querySelector("#acceptScenarioName").addEventListener("click", () => close(input.value));
    overlay.addEventListener("click", event => {
      if (event.target === overlay) close(null);
    });
    input.addEventListener("keydown", event => {
      if (event.key === "Enter") close(input.value);
      if (event.key === "Escape") close(null);
    });
    input.focus();
    input.select();
  });
}

async function saveScenario(update = false) {
  const current = scenarios.find(item => item.id === state.scenario.id);
  const suggested = update && current ? current.name : `Escenario ${scenarios.length + 1}`;
  const name = await askScenarioName(suggested);
  if (!name?.trim()) return;
  try {
    const path = update ? `/api/scenarios/${current.id}` : "/api/scenarios";
    const method = update ? "PUT" : "POST";
    const saved = await api(path, { method, body: JSON.stringify({ name: name.trim(), configuration: draft }) });
    state = await api(`/api/scenarios/${saved.id}/activate`, { method: "POST" });
    await loadScenarios();
    editMode = false;
    draft = null;
    selectedEntity = null;
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
  timer = window.setInterval(autoTick, autoDelay());
});
$("#speedSelect").addEventListener("change", async event => {
  const previous = state.speed?.key || "normal";
  const changed = await command("/api/simulation/speed", {
    method: "PUT",
    body: JSON.stringify({ speed: event.target.value }),
  });
  if (!changed) {
    $("#speedSelect").value = previous;
    return;
  }
  restartAutoTimer();
  notify(`Velocidad ${state.speed.label} aplicada (${state.speed.interval_ms} ms/paso).`);
});
$("#editScenario").addEventListener("click", enterEditor);
$("#cancelEdit").addEventListener("click", leaveEditor);
$("#applyDesign").addEventListener("click", applyDesign);
$("#saveAs").addEventListener("click", () => saveScenario(false));
$("#updateSaved").addEventListener("click", () => saveScenario(true));
$("#packagesTab").addEventListener("click", () => {
  editorTab = "packages";
  selectedEntity = draft.packages.length ? { type: "package", id: draft.packages[0].id } : null;
  render();
});
$("#obstaclesTab").addEventListener("click", () => {
  editorTab = "obstacles";
  selectedEntity = draft.obstacles.length ? { type: "obstacle", index: 0 } : null;
  render();
});
$("#zonesTab").addEventListener("click", () => {
  editorTab = "zones";
  selectedEntity = draft.zones.length ? { type: "zone", id: draft.zones[0].id } : null;
  render();
});
$("#addPackage").addEventListener("click", addPackage);
$("#removePackage").addEventListener("click", removeSelectedPackage);
$("#addObstacle").addEventListener("click", addObstacle);
$("#removeObstacle").addEventListener("click", removeSelectedObstacle);
$("#zoneSelect").addEventListener("change", event => {
  if (selectedEntity?.type !== "package") return;
  draft.packages.find(item => item.id === selectedEntity.id).zone = event.target.value;
  renderPackages();
});
$("#loadScenario").addEventListener("click", async () => {
  const id = $("#scenarioSelect").value;
  const loaded = await command(`/api/scenarios/${id}/activate`);
  if (loaded) notify("Escenario cargado.");
});
$("#scenarioSelect").addEventListener("change", renderControls);
$("#deleteScenario").addEventListener("click", async () => {
  const id = $("#scenarioSelect").value;
  const selected = scenarios.find(item => String(item.id) === id);
  if (!selected || selected.is_default) return;
  if (!window.confirm(`¿Eliminar el escenario "${selected.name}"? El historial de ejecuciones se conservara.`)) return;
  try {
    await api(`/api/scenarios/${id}`, { method: "DELETE" });
    [state] = await Promise.all([api("/api/simulation/state"), loadScenarios()]);
    render();
    notify("Escenario eliminado; el historial permanece disponible.");
  } catch (error) {
    notify(error.message, "error");
  }
});

refresh().catch(error => notify(error.message, "error"));

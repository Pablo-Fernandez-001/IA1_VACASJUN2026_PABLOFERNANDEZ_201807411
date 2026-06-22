(function () {
  "use strict";

  const $ = (selector) => document.querySelector(selector);
  const actionButtons = ["#bfsBtn", "#dfsBtn", "#compareBtn", "#loadExampleBtn", "#resizeBtn"];
  const comparisons = {};
  let currentName = "Laberinto personalizado";
  const replayState = {
    result: null,
    index: 0,
    timer: null,
    running: false,
    speed: 90,
  };

  const board = new window.MazeBoard($("#mazeGrid"), updateMazeMeta);

  function updateMazeMeta(payload) {
    $("#rowsInput").value = payload.rows;
    $("#colsInput").value = payload.cols;
    $("#mazeTitle").textContent = currentName;
    $("#mazeDescription").textContent = `${payload.rows} × ${payload.cols} · ${payload.obstacles.length} obstáculos`;
  }

  function toast(message, type = "error") {
    const element = $("#toast");
    element.textContent = message;
    element.className = `toast show ${type}`;
    window.clearTimeout(toast.timer);
    toast.timer = window.setTimeout(() => { element.className = "toast"; }, 4200);
  }

  function setBusy(busy, label = "Procesando…") {
    actionButtons.forEach((selector) => { $(selector).disabled = busy; });
    document.body.classList.toggle("is-busy", busy);
    if (busy) {
      $("#resultState").className = "result-state working";
      $("#resultState").textContent = label;
    }
  }

  function number(value, digits = 0) {
    return Number(value).toLocaleString("es-GT", {
      minimumFractionDigits: digits,
      maximumFractionDigits: digits,
    });
  }

  function updateMissionConsole({
    phase,
    narrative,
    point = null,
    current = 0,
    total = 0,
    route = false,
    running = false,
  }) {
    const percentage = total > 0 ? Math.round((current / total) * 100) : 0;
    $("#missionPhase").textContent = phase;
    $("#missionNarrative").textContent = narrative;
    $("#missionPosition").textContent = point
      ? `R${String(point.row).padStart(2, "0")} · C${String(point.col).padStart(2, "0")}`
      : "R— · C—";
    $("#missionProgress").textContent = `${percentage}%`;
    $("#missionStep").textContent = `${current} / ${total}`;
    $("#missionProgressBar").style.width = `${percentage}%`;
    $("#missionConsole").classList.toggle("is-running", running);
    $("#missionConsole").classList.toggle("is-route", route);
  }

  function setReplayControls(enabled) {
    $("#replayBtn").disabled = !enabled;
    $("#pauseReplayBtn").disabled = !enabled || !replayState.running;
    $("#resetReplayBtn").disabled = !enabled;
  }

  function stopReplay(clearRover = true) {
    window.clearTimeout(replayState.timer);
    replayState.timer = null;
    replayState.running = false;
    if (clearRover) board.clearRover();
    setReplayControls(Boolean(replayState.result?.path_found));
  }

  function replayTick() {
    if (!replayState.running || !replayState.result) return;
    const path = replayState.result.path;
    const point = path[replayState.index];
    const previous = replayState.index > 0 ? path[replayState.index - 1] : null;
    const totalSteps = Math.max(0, path.length - 1);
    board.placeRover(point, previous);
    updateMissionConsole({
      phase: replayState.index === totalSteps ? "TARGET LOCKED" : "ROVER IN MOTION",
      narrative: replayState.index === totalSteps
        ? `Misión completada: el rover alcanzó la baliza con ${totalSteps} movimientos.`
        : `Ejecutando la ruta ${replayState.result.algorithm}: movimiento ${replayState.index} de ${totalSteps}.`,
      point,
      current: replayState.index,
      total: totalSteps,
      route: true,
      running: replayState.index !== totalSteps,
    });
    if (replayState.index >= path.length - 1) {
      replayState.running = false;
      setReplayControls(true);
      return;
    }
    replayState.timer = window.setTimeout(() => {
      replayState.index += 1;
      replayTick();
    }, replayState.speed);
  }

  function playReplay() {
    if (!replayState.result?.path_found) return;
    if (replayState.index >= replayState.result.path.length - 1) replayState.index = 0;
    window.clearTimeout(replayState.timer);
    replayState.running = true;
    setReplayControls(true);
    replayTick();
  }

  function pauseReplay() {
    if (!replayState.running) return;
    window.clearTimeout(replayState.timer);
    replayState.running = false;
    const point = replayState.result.path[replayState.index];
    updateMissionConsole({
      phase: "MISSION HOLD",
      narrative: "Navegación pausada. Pulsa Ejecutar ruta para continuar.",
      point,
      current: replayState.index,
      total: Math.max(0, replayState.result.path.length - 1),
      route: true,
    });
    setReplayControls(true);
  }

  function resetReplay() {
    if (!replayState.result?.path_found) return;
    stopReplay(false);
    replayState.index = 0;
    const start = replayState.result.path[0];
    board.placeRover(start);
    updateMissionConsole({
      phase: "ROUTE ARMED",
      narrative: "Rover reposicionado. La ruta está lista para ejecutarse de nuevo.",
      point: start,
      current: 0,
      total: Math.max(0, replayState.result.path.length - 1),
      route: true,
    });
  }

  function prepareReplay(result, autoplay = true) {
    stopReplay();
    replayState.result = result;
    replayState.index = 0;
    if (!result.path_found || result.path.length === 0) {
      setReplayControls(false);
      updateMissionConsole({
        phase: "NO ROUTE",
        narrative: `${result.algorithm} agotó ${result.nodes_explored} nodos sin alcanzar la baliza.`,
        current: result.nodes_explored,
        total: result.nodes_explored,
      });
      return;
    }
    board.placeRover(result.path[0]);
    setReplayControls(true);
    if (autoplay) playReplay();
    else resetReplay();
  }

  function handleSearchProgress(progress) {
    if (progress.phase === "exploration") {
      const strategy = progress.algorithm === "BFS"
        ? "La onda BFS expande el mapa por niveles"
        : "La sonda DFS profundiza la rama activa";
      updateMissionConsole({
        phase: progress.algorithm === "BFS" ? "WAVE SCAN" : "DEPTH PROBE",
        narrative: `${strategy}: nodo ${progress.current} de ${progress.total}.`,
        point: progress.point,
        current: progress.current,
        total: progress.total,
        running: true,
      });
    } else {
      updateMissionConsole({
        phase: "ROUTE COMPUTED",
        narrative: "Exploración terminada. Preparando instrucciones de movimiento para el rover.",
        point: progress.point,
        current: 0,
        total: Math.max(0, progress.total - 1),
        route: true,
      });
    }
  }

  function showMetrics(result) {
    $("#resultsTitle").textContent = result.algorithm === "BFS" ? "Telemetría de onda BFS" : "Telemetría de sonda DFS";
    $("#metricAlgorithm").textContent = result.algorithm;
    $("#metricFound").textContent = result.path_found ? "Sí" : "No";
    $("#metricLength").textContent = number(result.path_length);
    $("#metricNodes").textContent = number(result.nodes_explored);
    $("#metricTime").textContent = number(result.execution_time_ms, 3);
    $("#resultMessage").textContent = result.message;
    $("#resultState").className = `result-state ${result.path_found ? "success" : "failure"}`;
    $("#resultState").textContent = result.path_found ? "Ruta encontrada" : "Sin ruta";
  }

  async function runSingle(algorithm) {
    stopReplay();
    replayState.result = null;
    setReplayControls(false);
    setBusy(true, `Ejecutando ${algorithm.toUpperCase()}…`);
    updateMissionConsole({
      phase: "CORE UPLINK",
      narrative: `Enviando el mapa al motor ${algorithm.toUpperCase()} en Python.`,
      running: true,
    });
    $("#comparisonBlock").hidden = true;
    try {
      const result = await window.RoboMazeApi.solve(algorithm, board.getPayload());
      showMetrics(result);
      await board.visualize(result, handleSearchProgress);
      prepareReplay(result);
    } catch (error) {
      showError(error);
    } finally {
      setBusy(false);
    }
  }

  function comparisonRow(result) {
    const row = document.createElement("tr");
    const values = [
      result.algorithm,
      result.path_found ? "Sí" : "No",
      number(result.path_length),
      number(result.nodes_explored),
      `${number(result.execution_time_ms, 3)} ms`,
    ];
    values.forEach((value, index) => {
      const cell = document.createElement(index === 0 ? "th" : "td");
      cell.textContent = value;
      row.appendChild(cell);
    });
    const actionCell = document.createElement("td");
    const button = document.createElement("button");
    button.className = "view-button";
    button.type = "button";
    button.textContent = "Mostrar";
    button.addEventListener("click", async () => {
      stopReplay();
      showMetrics(result);
      await board.visualize(result, handleSearchProgress);
      prepareReplay(result);
    });
    actionCell.appendChild(button);
    row.appendChild(actionCell);
    return row;
  }

  function renderMiniMaze(element, result, maze) {
    const obstacles = new Set(maze.obstacles.map((point) => `${point.row},${point.col}`));
    const visited = new Set(result.visited_nodes.map((point) => `${point.row},${point.col}`));
    const path = new Set(result.path.map((point) => `${point.row},${point.col}`));
    const start = `${maze.start.row},${maze.start.col}`;
    const goal = `${maze.goal.row},${maze.goal.col}`;
    element.innerHTML = "";
    element.style.setProperty("--mini-rows", maze.rows);
    element.style.setProperty("--mini-cols", maze.cols);
    const largestDimension = Math.max(maze.rows, maze.cols);
    element.dataset.density = largestDimension > 50 ? "micro" : largestDimension > 24 ? "dense" : "normal";
    element.style.gridTemplateColumns = `repeat(${maze.cols}, 1fr)`;
    element.style.gridTemplateRows = `repeat(${maze.rows}, 1fr)`;
    const fragment = document.createDocumentFragment();
    for (let row = 0; row < maze.rows; row += 1) {
      for (let col = 0; col < maze.cols; col += 1) {
        const key = `${row},${col}`;
        const cell = document.createElement("i");
        const classes = ["mini-cell"];
        if (visited.has(key)) classes.push("visited");
        if (path.has(key)) classes.push("path");
        if (obstacles.has(key)) classes.push("obstacle");
        if (key === start) classes.push("start");
        if (key === goal) classes.push("goal");
        cell.className = classes.join(" ");
        cell.setAttribute("aria-hidden", "true");
        fragment.appendChild(cell);
      }
    }
    element.appendChild(fragment);
  }

  function renderDuel(data, maze) {
    renderMiniMaze($("#bfsMiniMap"), data.bfs, maze);
    renderMiniMaze($("#dfsMiniMap"), data.dfs, maze);
    $("#bfsDuelStat").textContent = data.bfs.path_found
      ? `${data.bfs.path_length} STEPS · ${data.bfs.nodes_explored} NODES`
      : `NO PATH · ${data.bfs.nodes_explored} NODES`;
    $("#dfsDuelStat").textContent = data.dfs.path_found
      ? `${data.dfs.path_length} STEPS · ${data.dfs.nodes_explored} NODES`
      : `NO PATH · ${data.dfs.nodes_explored} NODES`;
  }

  function renderWinner(data) {
    const banner = $("#winnerBanner");
    const bfsCard = document.querySelector(".bfs-card");
    const dfsCard = document.querySelector(".dfs-card");
    banner.className = "winner-banner";
    bfsCard.classList.remove("winner", "dimmed");
    dfsCard.classList.remove("winner", "dimmed");
    let winner = "tie";
    let title = "EMPATE TÉCNICO";
    let reason = "Ambos algoritmos obtuvieron la misma longitud y exploraron la misma cantidad de nodos.";

    if (!data.bfs.path_found && !data.dfs.path_found) {
      winner = "none";
      title = "MISIÓN SIN RESOLVER";
      reason = "Ninguna estrategia pudo atravesar el bloqueo hasta la baliza.";
    } else if (data.bfs.path_found !== data.dfs.path_found) {
      winner = data.bfs.path_found ? "bfs" : "dfs";
      title = `${winner.toUpperCase()} // ÚNICA RUTA`;
      reason = `${winner.toUpperCase()} fue el único algoritmo que logró alcanzar la baliza.`;
    } else if (data.bfs.path_length !== data.dfs.path_length) {
      winner = data.bfs.path_length < data.dfs.path_length ? "bfs" : "dfs";
      title = `${winner.toUpperCase()} // RUTA GANADORA`;
      reason = `${winner.toUpperCase()} llegó con menos movimientos: ${Math.min(data.bfs.path_length, data.dfs.path_length)} frente a ${Math.max(data.bfs.path_length, data.dfs.path_length)}.`;
    } else if (data.bfs.nodes_explored !== data.dfs.nodes_explored) {
      winner = data.bfs.nodes_explored < data.dfs.nodes_explored ? "bfs" : "dfs";
      title = `${winner.toUpperCase()} // MENOR EXPLORACIÓN`;
      reason = `Las rutas empatan, pero ${winner.toUpperCase()} examinó menos nodos en este mapa.`;
    }

    if (winner === "bfs" || winner === "dfs") {
      banner.classList.add(`winner-${winner}`);
      const winnerCard = winner === "bfs" ? bfsCard : dfsCard;
      const loserCard = winner === "bfs" ? dfsCard : bfsCard;
      winnerCard.classList.add("winner");
      loserCard.classList.add("dimmed");
    } else if (winner === "none") {
      banner.classList.add("no-winner");
    }
    $("#winnerTitle").textContent = title;
    $("#winnerReason").textContent = reason;
  }

  async function runComparison() {
    stopReplay();
    replayState.result = null;
    setReplayControls(false);
    setBusy(true, "Comparando…");
    updateMissionConsole({
      phase: "DUAL UPLINK",
      narrative: "Enviando el mismo terreno a WAVE/BFS y PROBE/DFS.",
      running: true,
    });
    try {
      const maze = board.getPayload();
      const data = await window.RoboMazeApi.solve("compare", maze);
      comparisons.BFS = data.bfs;
      comparisons.DFS = data.dfs;
      const body = $("#comparisonBody");
      body.innerHTML = "";
      body.append(comparisonRow(data.bfs), comparisonRow(data.dfs));
      renderDuel(data, maze);
      renderWinner(data);
      $("#conclusion").textContent = data.conclusion;
      $("#comparisonBlock").hidden = false;
      $("#resultMessage").textContent = "Selecciona “Mostrar” para alternar el recorrido visualizado.";
      showMetrics(data.bfs);
      $("#resultMessage").textContent = "Comparación completada. Selecciona “Mostrar” para alternar recorridos.";
      $("#resultsTitle").textContent = "Duelo de estrategias";
      await board.visualize(data.bfs, handleSearchProgress);
      prepareReplay(data.bfs);
    } catch (error) {
      showError(error);
    } finally {
      setBusy(false);
    }
  }

  function showError(error) {
    stopReplay();
    $("#resultState").className = "result-state failure";
    $("#resultState").textContent = "Error";
    $("#resultMessage").textContent = error.message;
    updateMissionConsole({
      phase: "SYSTEM ERROR",
      narrative: error.message,
    });
    toast(error.message);
  }

  async function checkBackend() {
    const status = $("#backendStatus");
    try {
      const data = await window.RoboMazeApi.health();
      status.className = "backend-status online";
      status.innerHTML = `<span class="status-dot"></span><span>API ${data.version} conectada</span>`;
    } catch (_error) {
      status.className = "backend-status offline";
      status.innerHTML = '<span class="status-dot"></span><span>API desconectada</span>';
    }
  }

  async function loadExamples() {
    try {
      const examples = await window.RoboMazeApi.examples();
      const select = $("#exampleSelect");
      examples.forEach((example) => {
        const option = document.createElement("option");
        option.value = example.id;
        option.textContent = `${example.id}. ${example.name}`;
        option.dataset.example = JSON.stringify(example);
        select.appendChild(option);
      });
    } catch (error) {
      toast(`${error.message} Puedes editar el laberinto local mientras inicias la API.`, "warning");
    }
  }

  $("#loadExampleBtn").addEventListener("click", () => {
    const option = $("#exampleSelect").selectedOptions[0];
    if (!option || !option.dataset.example) return toast("Selecciona un laberinto predefinido.", "warning");
    const example = JSON.parse(option.dataset.example);
    currentName = example.name;
    board.load(example);
    $("#mazeDescription").textContent = `${example.rows} × ${example.cols} · ${example.description}`;
    resetResultPanel();
    toast(`Se cargó “${example.name}”.`, "success");
  });

  $("#resizeBtn").addEventListener("click", () => {
    const rows = Number($("#rowsInput").value);
    const cols = Number($("#colsInput").value);
    if (!Number.isInteger(rows) || !Number.isInteger(cols) || rows < 2 || cols < 2 || rows > 100 || cols > 100) {
      return toast("Usa dimensiones enteras entre 2 y 100.");
    }
    currentName = "Laberinto personalizado";
    $("#exampleSelect").value = "";
    board.create(rows, cols);
    resetResultPanel();
  });

  document.querySelectorAll(".tool-button").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".tool-button").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      board.setMode(button.dataset.mode);
    });
  });

  $("#mazeGrid").addEventListener("cellhover", (event) => {
    $("#coordinateBadge").textContent = `R${String(event.detail.row).padStart(2, "0")} · C${String(event.detail.col).padStart(2, "0")}`;
  });
  $("#mazeGrid").addEventListener("mazechange", () => {
    stopReplay();
    replayState.result = null;
    setReplayControls(false);
  });
  $("#bfsBtn").addEventListener("click", () => runSingle("bfs"));
  $("#dfsBtn").addEventListener("click", () => runSingle("dfs"));
  $("#compareBtn").addEventListener("click", runComparison);
  $("#replayBtn").addEventListener("click", playReplay);
  $("#pauseReplayBtn").addEventListener("click", pauseReplay);
  $("#resetReplayBtn").addEventListener("click", resetReplay);
  $("#speedSelect").addEventListener("change", (event) => {
    replayState.speed = Number(event.target.value);
  });
  $("#clearMazeBtn").addEventListener("click", () => { board.clearObstacles(); resetResultPanel(); });
  $("#resetResultsBtn").addEventListener("click", () => { board.clearVisualization(); resetResultPanel(); });

  function resetResultPanel() {
    stopReplay();
    replayState.result = null;
    replayState.index = 0;
    setReplayControls(false);
    $("#comparisonBlock").hidden = true;
    $("#resultState").className = "result-state neutral";
    $("#resultState").textContent = "Sin ejecutar";
    ["#metricAlgorithm", "#metricFound", "#metricLength", "#metricNodes", "#metricTime"].forEach((id) => { $(id).textContent = "—"; });
    $("#resultMessage").textContent = "Configura el laberinto para comenzar.";
    $("#resultsTitle").textContent = "Lectura de navegación";
    $("#bfsMiniMap").innerHTML = "";
    $("#dfsMiniMap").innerHTML = "";
    updateMissionConsole({
      phase: "STANDBY",
      narrative: "Carga un mapa y ejecuta un algoritmo para iniciar la navegación.",
    });
  }

  checkBackend();
  loadExamples();
})();

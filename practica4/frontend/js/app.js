(function () {
  "use strict";

  const $ = (selector) => document.querySelector(selector);
  const actionButtons = ["#bfsBtn", "#dfsBtn", "#compareBtn", "#loadExampleBtn", "#resizeBtn"];
  const comparisons = {};
  let currentName = "Laberinto personalizado";

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

  function showMetrics(result) {
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
    setBusy(true, `Ejecutando ${algorithm.toUpperCase()}…`);
    $("#comparisonBlock").hidden = true;
    try {
      const result = await window.RoboMazeApi.solve(algorithm, board.getPayload());
      showMetrics(result);
      await board.visualize(result);
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
      showMetrics(result);
      await board.visualize(result);
    });
    actionCell.appendChild(button);
    row.appendChild(actionCell);
    return row;
  }

  async function runComparison() {
    setBusy(true, "Comparando…");
    try {
      const data = await window.RoboMazeApi.solve("compare", board.getPayload());
      comparisons.BFS = data.bfs;
      comparisons.DFS = data.dfs;
      const body = $("#comparisonBody");
      body.innerHTML = "";
      body.append(comparisonRow(data.bfs), comparisonRow(data.dfs));
      $("#conclusion").textContent = data.conclusion;
      $("#comparisonBlock").hidden = false;
      $("#resultMessage").textContent = "Selecciona “Mostrar” para alternar el recorrido visualizado.";
      showMetrics(data.bfs);
      $("#resultMessage").textContent = "Comparación completada. Selecciona “Mostrar” para alternar recorridos.";
      await board.visualize(data.bfs);
    } catch (error) {
      showError(error);
    } finally {
      setBusy(false);
    }
  }

  function showError(error) {
    $("#resultState").className = "result-state failure";
    $("#resultState").textContent = "Error";
    $("#resultMessage").textContent = error.message;
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
    if (!Number.isInteger(rows) || !Number.isInteger(cols) || rows < 2 || cols < 2 || rows > 30 || cols > 30) {
      return toast("Usa dimensiones enteras entre 2 y 30.");
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
    $("#coordinateBadge").textContent = `Fila ${event.detail.row} · Col ${event.detail.col}`;
  });
  $("#bfsBtn").addEventListener("click", () => runSingle("bfs"));
  $("#dfsBtn").addEventListener("click", () => runSingle("dfs"));
  $("#compareBtn").addEventListener("click", runComparison);
  $("#clearMazeBtn").addEventListener("click", () => { board.clearObstacles(); resetResultPanel(); });
  $("#resetResultsBtn").addEventListener("click", () => { board.clearVisualization(); resetResultPanel(); });

  function resetResultPanel() {
    $("#comparisonBlock").hidden = true;
    $("#resultState").className = "result-state neutral";
    $("#resultState").textContent = "Sin ejecutar";
    ["#metricAlgorithm", "#metricFound", "#metricLength", "#metricNodes", "#metricTime"].forEach((id) => { $(id).textContent = "—"; });
    $("#resultMessage").textContent = "Configura el laberinto para comenzar.";
  }

  checkBackend();
  loadExamples();
})();

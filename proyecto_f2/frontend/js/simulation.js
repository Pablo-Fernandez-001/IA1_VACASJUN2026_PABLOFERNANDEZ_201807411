const app = document.querySelector("#app");
let state = null;
let timer = null;

app.innerHTML = `
  <div class="topline">
    <h1>Simulacion</h1>
    <div class="controls">
      <button id="start">Iniciar</button>
      <button class="warn" id="pause">Pausar</button>
      <button class="danger" id="reset">Reiniciar</button>
      <button class="secondary" id="step">Paso</button>
      <button id="auto">Automatico</button>
    </div>
  </div>
  <section class="workspace">
    <div class="panel">
      <div class="board" id="board"></div>
    </div>
    <div>
      <section class="panel">
        <h2>Estado</h2>
        <div class="grid" id="metrics"></div>
        <p class="message" id="message"></p>
      </section>
      <section class="panel">
        <h2>Leyenda</h2>
        <div class="legend">
          <div><span class="swatch robot-swatch"></span>Robot</div>
          <div><span class="swatch package-swatch"></span>Paquete</div>
          <div><span class="swatch obstacle-swatch"></span>Obstaculo</div>
          <div><span class="swatch zonea-swatch"></span>Zona A</div>
          <div><span class="swatch zoneb-swatch"></span>Zona B</div>
        </div>
      </section>
      <section class="panel">
        <h2>Paquetes</h2>
        <div id="packages"></div>
      </section>
    </div>
  </section>
`;

function cellContent(x, y) {
  const robot = state.robots.find(item => item.x === x && item.y === y);
  if (robot) return `R`;
  const pack = state.packages.find(item => item.x === x && item.y === y && item.status !== "entregado");
  if (pack) return pack.id.toUpperCase();
  const zone = state.zones.find(item => item.x === x && item.y === y);
  if (zone) return zone.id === "zona_a" ? "A" : "B";
  return "";
}

function cellClass(x, y) {
  const classes = ["cell"];
  const zone = state.zones.find(item => item.x === x && item.y === y);
  if (zone?.id === "zona_a") classes.push("zone-a");
  if (zone?.id === "zona_b") classes.push("zone-b");
  if (state.obstacles.some(item => item.x === x && item.y === y)) classes.push("obstacle");
  if (state.packages.some(item => item.x === x && item.y === y && item.status !== "entregado")) classes.push("package");
  if (state.robots.some(item => item.x === x && item.y === y)) classes.push("robot");
  return classes.join(" ");
}

function render() {
  board.innerHTML = "";
  for (let y = 1; y <= state.map.height; y += 1) {
    for (let x = 1; x <= state.map.width; x += 1) {
      board.insertAdjacentHTML("beforeend", `<div class="${cellClass(x, y)}"><span class="coord">${x},${y}</span>${cellContent(x, y)}</div>`);
    }
  }
  const metricsData = {
    Entregas: state.deliveries,
    Movimientos: state.moves,
    Pasos: state.steps,
    Pendientes: state.packages.filter(item => item.status !== "entregado").length,
  };
  metrics.innerHTML = Object.entries(metricsData).map(([label, value]) => `<div class="stat"><span>${label}</span><strong>${value}</strong></div>`).join("");
  const robot = state.robots[0];
  message.textContent = `${state.last_action || "esperando"}: ${state.last_reason || `Robot ${robot.id} en (${robot.x},${robot.y})`}`;
  packages.innerHTML = state.packages.map(item => `<p><strong>${item.id.toUpperCase()}</strong> zona ${item.zone}, estado ${item.status}, posicion (${item.x},${item.y})</p>`).join("");
}

async function refresh() {
  state = await api("/api/simulation/state");
  render();
}

async function command(path) {
  try {
    state = await api(path, { method: "POST" });
    render();
  } catch (error) {
    message.textContent = error.message;
  }
}

start.addEventListener("click", () => command("/api/simulation/start"));
pause.addEventListener("click", () => { clearInterval(timer); timer = null; command("/api/simulation/pause"); });
reset.addEventListener("click", () => { clearInterval(timer); timer = null; command("/api/simulation/reset"); });
step.addEventListener("click", () => command("/api/simulation/step"));
auto.addEventListener("click", () => {
  if (timer) {
    clearInterval(timer);
    timer = null;
    message.textContent = "Modo automatico detenido.";
    return;
  }
  timer = setInterval(async () => {
    await command("/api/simulation/step");
    if (state.packages.every(item => item.status === "entregado")) {
      clearInterval(timer);
      timer = null;
    }
  }, 700);
});
refresh();

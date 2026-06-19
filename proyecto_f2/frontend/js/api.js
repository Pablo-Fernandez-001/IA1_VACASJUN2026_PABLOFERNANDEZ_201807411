const LOCAL_API = location.hostname === "localhost" || location.hostname === "127.0.0.1" ? "http://127.0.0.1:8400" : "";
const API_BASE = window.API_BASE_URL || (location.port === "8411" ? LOCAL_API : "");

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    let message = `Error ${response.status}`;
    try {
      const body = await response.json();
      message = body.detail || message;
    } catch (_) {}
    throw new Error(typeof message === "string" ? message : JSON.stringify(message));
  }
  return response.json();
}

function shell(active) {
  document.body.insertAdjacentHTML("afterbegin", `
    <div class="layout">
      <aside class="side">
        <div class="brand">Smart Warehouse</div>
        <nav class="nav">
          <a class="${active === "sim" ? "active" : ""}" href="index.html">Simulacion</a>
          <a class="${active === "dash" ? "active" : ""}" href="dashboard.html">Dashboard</a>
        </nav>
      </aside>
      <main class="main" id="app"></main>
    </div>
  `);
}

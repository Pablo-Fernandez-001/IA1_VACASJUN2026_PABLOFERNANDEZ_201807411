const LOCAL_API = location.hostname === "localhost" || location.hostname === "127.0.0.1" ? "http://127.0.0.1:8400" : "";
const API_BASE = window.API_BASE_URL || (location.port === "8411" ? LOCAL_API : "");

async function api(path, options = {}) {
  const headers = { Accept: "application/json", ...(options.headers || {}) };
  if (options.body && !headers["Content-Type"]) headers["Content-Type"] = "application/json";
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!response.ok) {
    let message = `Error ${response.status}`;
    try {
      const body = await response.json();
      if (Array.isArray(body.detail)) message = body.detail.map(item => item.msg).join(" · ");
      else message = body.detail || message;
    } catch (_) {}
    throw new Error(typeof message === "string" ? message : JSON.stringify(message));
  }
  if (response.status === 204) return null;
  return response.json();
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>'"]/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
  })[char]);
}

function shell(active) {
  document.body.insertAdjacentHTML("afterbegin", `
    <div class="layout">
      <aside class="side">
        <div class="brand-lockup">
          <div class="brand-mark"><span></span><span></span><span></span></div>
          <div><strong>SMART</strong><span>WAREHOUSE</span></div>
        </div>
        <p class="side-kicker">Centro de control logistico</p>
        <nav class="nav">
          <a class="${active === "sim" ? "active" : ""}" href="index.html">
            <span class="nav-icon">⌁</span><span>Simulacion<small>Operaciones en vivo</small></span>
          </a>
          <a class="${active === "dash" ? "active" : ""}" href="dashboard.html">
            <span class="nav-icon">▥</span><span>Analitica<small>Metricas e historial</small></span>
          </a>
        </nav>
        <div class="engine-card">
          <span class="live-dot"></span>
          <div><strong>Motor simbolico</strong><small>SWI-Prolog · BFS</small></div>
        </div>
      </aside>
      <main class="main" id="app"></main>
    </div>
  `);
}

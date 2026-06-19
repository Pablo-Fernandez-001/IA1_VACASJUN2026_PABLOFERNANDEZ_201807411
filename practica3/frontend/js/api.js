const LOCAL_API = location.hostname === "localhost" || location.hostname === "127.0.0.1" ? "http://127.0.0.1:8300" : "";
const API_BASE = window.API_BASE_URL || (location.port === "8311" ? LOCAL_API : "");

function token() {
  return localStorage.getItem("smartinvoice_token");
}

function authHeaders(extra = {}) {
  const headers = { ...extra };
  if (token()) headers.Authorization = `Bearer ${token()}`;
  return headers;
}

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: authHeaders(options.headers || {}),
  });
  if (response.status === 401) {
    localStorage.removeItem("smartinvoice_token");
    if (!location.pathname.endsWith("login.html")) location.href = "login.html";
  }
  if (!response.ok) {
    let message = `Error ${response.status}`;
    try {
      const body = await response.json();
      message = body.detail || message;
    } catch (_) {}
    throw new Error(typeof message === "string" ? message : JSON.stringify(message));
  }
  const type = response.headers.get("content-type") || "";
  if (type.includes("application/json")) return response.json();
  return response;
}

function requireAuth() {
  if (!token()) location.href = "login.html";
}

function logout() {
  localStorage.removeItem("smartinvoice_token");
  location.href = "login.html";
}

function shell(active) {
  document.body.insertAdjacentHTML("afterbegin", `
    <div class="shell">
      <aside class="sidebar">
        <div class="brand">SmartInvoice</div>
        <nav class="nav">
          <a class="${active === "dashboard" ? "active" : ""}" href="dashboard.html">Dashboard</a>
          <a class="${active === "providers" ? "active" : ""}" href="providers.html">Proveedores</a>
          <a class="${active === "invoices" ? "active" : ""}" href="invoices.html">Facturas</a>
          <a class="${active === "logs" ? "active" : ""}" href="logs.html">Bitacora</a>
          <a class="${active === "reports" ? "active" : ""}" href="reports.html">Reportes</a>
          <a href="rpa_form.html">Formulario RPA</a>
          <button type="button" onclick="logout()">Salir</button>
        </nav>
      </aside>
      <main class="content" id="app"></main>
    </div>
  `);
}

function money(value) {
  return `Q ${Number(value || 0).toFixed(2)}`;
}

function statusBadge(status) {
  return `<span class="status ${status}">${status}</span>`;
}

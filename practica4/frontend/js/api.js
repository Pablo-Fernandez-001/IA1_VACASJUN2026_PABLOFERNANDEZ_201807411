(function () {
  "use strict";

  const configured = window.ROBOMAZE_API_URL;
  const dockerOrigin = window.location.port === "8401" ? window.location.origin : null;
  const baseUrl = (configured || dockerOrigin || "http://localhost:8400").replace(/\/$/, "");

  async function request(path, options = {}) {
    let response;
    try {
      response = await fetch(`${baseUrl}${path}`, {
        ...options,
        headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      });
    } catch (_error) {
      throw new Error("No fue posible conectar con el backend en el puerto 8400.");
    }

    let body;
    try {
      body = await response.json();
    } catch (_error) {
      throw new Error(`El backend respondió con un formato inesperado (${response.status}).`);
    }

    if (!response.ok) {
      const detail = typeof body.detail === "string" ? body.detail : "La solicitud no es válida.";
      throw new Error(detail);
    }
    return body;
  }

  window.RoboMazeApi = {
    baseUrl,
    health: () => request("/api/health"),
    examples: () => request("/api/maze/examples"),
    solve: (algorithm, maze) => request(`/api/maze/solve/${algorithm}`, {
      method: "POST",
      body: JSON.stringify(maze),
    }),
  };
})();

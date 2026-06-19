const app = document.querySelector("#app");
app.innerHTML = `
  <div class="topline"><h1>Bitacora</h1></div>
  <section class="panel">
    <div class="table-wrap"><table><thead><tr><th>Fecha</th><th>Usuario</th><th>Documento</th><th>Estado</th><th>Resultado</th></tr></thead><tbody id="rows"></tbody></table></div>
  </section>
`;
api("/api/logs").then(logs => {
  rows.innerHTML = logs.map(log => `
    <tr><td>${new Date(log.created_at).toLocaleString()}</td><td>${log.username}</td><td>${log.document_name}</td><td>${statusBadge(log.status)}</td><td>${log.result}</td></tr>
  `).join("");
});

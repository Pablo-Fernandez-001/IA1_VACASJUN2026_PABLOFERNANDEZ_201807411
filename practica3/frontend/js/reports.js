const app = document.querySelector("#app");
app.innerHTML = `
  <div class="topline"><h1>Reportes</h1></div>
  <section class="panel">
    <div class="actions">
      <button type="button" onclick="downloadReport('csv')">Descargar CSV</button>
      <button type="button" onclick="downloadReport('pdf')">Descargar PDF</button>
    </div>
  </section>
  <section class="panel">
    <h2>Enviar por correo</h2>
    <form id="emailForm" class="form-grid">
      <label>Destinatario<input id="recipient" type="email" required></label>
      <label>Formato<select id="report_type"><option value="pdf">PDF</option><option value="csv">CSV</option></select></label>
      <button type="submit">Enviar</button>
    </form>
    <p id="message" class="message"></p>
  </section>
`;

window.downloadReport = async (type) => {
  try {
    const response = await api(`/api/reports/${type}`);
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = type === "pdf" ? "reporte_facturas.pdf" : "reporte_facturas.csv";
    link.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    message.textContent = error.message;
  }
};

emailForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const result = await api("/api/reports/email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ recipient: recipient.value, report_type: report_type.value }),
    });
    message.textContent = `${result.status}: ${result.detail}`;
  } catch (error) {
    message.textContent = error.message;
  }
});

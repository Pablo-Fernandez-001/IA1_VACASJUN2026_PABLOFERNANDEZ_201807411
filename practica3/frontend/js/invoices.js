const app = document.querySelector("#app");
app.innerHTML = `
  <div class="topline"><h1>Facturas</h1></div>
  <section class="panel">
    <h2>Cargar documento</h2>
    <form id="uploadForm" class="form-grid">
      <label>Archivo PDF, JPG, JPEG o PNG<input id="file" type="file" accept=".pdf,.jpg,.jpeg,.png" required></label>
      <button type="submit">Procesar</button>
      <button type="button" class="secondary" id="seed">Procesar dataset</button>
    </form>
    <p id="message" class="message"></p>
  </section>
  <section class="panel">
    <h2>Procesadas</h2>
    <div class="table-wrap"><table><thead><tr><th>No.</th><th>Fecha</th><th>Proveedor</th><th>NIT</th><th>Total</th><th>Estado</th><th>Acciones</th></tr></thead><tbody id="rows"></tbody></table></div>
  </section>
  <section class="panel">
    <h2>Texto OCR</h2>
    <pre id="raw">Seleccione una factura para ver el texto extraido.</pre>
  </section>
`;

async function loadInvoices() {
  const invoices = await api("/api/invoices");
  rows.innerHTML = invoices.map(invoice => `
    <tr>
      <td>${invoice.invoice_number}</td><td>${invoice.issue_date || ""}</td><td>${invoice.provider_name}</td>
      <td>${invoice.provider_nit}</td><td>${money(invoice.total)}</td><td>${statusBadge(invoice.status)}</td>
      <td class="actions">
        <button type="button" onclick="showRaw(${invoice.id})">OCR</button>
        <button type="button" onclick="validateInvoice(${invoice.id})">Validar</button>
        <button class="success" type="button" onclick="runRpa(${invoice.id})">RPA</button>
      </td>
    </tr>`).join("");
}

window.showRaw = async (id) => {
  const invoice = await api(`/api/invoices/${id}`);
  raw.textContent = invoice.raw_text || "Sin texto OCR.";
};

window.validateInvoice = async (id) => {
  const invoice = await api(`/api/invoices/${id}/validate`, { method: "POST" });
  message.textContent = `Validacion: ${invoice.status}`;
  loadInvoices();
};

window.runRpa = async (id) => {
  const result = await api(`/api/invoices/${id}/rpa-register`, { method: "POST" });
  message.textContent = result.result;
};

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const body = new FormData();
  body.append("file", file.files[0]);
  try {
    const invoice = await api("/api/invoices/upload", { method: "POST", body });
    message.textContent = `Factura ${invoice.invoice_number} procesada con estado ${invoice.status}.`;
    uploadForm.reset();
    loadInvoices();
  } catch (error) {
    message.textContent = error.message;
  }
});

seed.addEventListener("click", async () => {
  try {
    const result = await api("/api/invoices/seed-demo", { method: "POST" });
    message.textContent = `Dataset procesado: ${result.total} documentos.`;
    loadInvoices();
  } catch (error) {
    message.textContent = error.message;
  }
});
loadInvoices();

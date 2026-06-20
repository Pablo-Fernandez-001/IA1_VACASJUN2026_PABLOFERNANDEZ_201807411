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
    <h2>Consulta</h2>
    <form id="filters" class="form-grid">
      <label>Buscar<input id="search" placeholder="Numero, proveedor o NIT"></label>
      <label>Estado<select id="statusFilter"><option value="">Todos</option><option>Procesado</option><option>Pendiente</option><option>Error</option><option>Rechazado</option></select></label>
      <button type="submit">Filtrar</button><button type="button" class="secondary" id="clearFilters">Limpiar</button>
    </form>
  </section>
  <section class="panel"><h2>Facturas registradas</h2><div class="table-wrap"><table><thead><tr><th>No.</th><th>Fecha</th><th>Proveedor</th><th>NIT</th><th>Total</th><th>Estado</th><th>Acciones</th></tr></thead><tbody id="rows"></tbody></table></div></section>`;

async function loadInvoices() {
  const params = new URLSearchParams();
  if (search.value.trim()) params.set("search", search.value.trim());
  if (statusFilter.value) params.set("status", statusFilter.value);
  const invoices = await api(`/api/invoices?${params}`);
  rows.innerHTML = invoices.length ? invoices.map(invoice => `<tr>
    <td>${escapeHtml(invoice.invoice_number)}</td><td>${escapeHtml(invoice.issue_date || "")}</td><td>${escapeHtml(invoice.provider_name)}</td>
    <td>${escapeHtml(invoice.provider_nit)}</td><td>${money(invoice.total)}</td><td>${statusBadge(invoice.status)}</td>
    <td class="actions"><a class="button" href="invoice_detail.html?id=${invoice.id}">Detalle</a><button onclick="validateInvoice(${invoice.id})">Validar</button><button class="secondary" onclick="reprocessInvoice(${invoice.id})">Reprocesar</button><button class="danger" onclick="rejectInvoice(${invoice.id})">Rechazar</button><button class="success" onclick="runRpa(${invoice.id})">RPA</button></td>
  </tr>`).join("") : '<tr><td colspan="7">No hay facturas para los filtros seleccionados.</td></tr>';
}
window.validateInvoice = async id => { const invoice = await api(`/api/invoices/${id}/validate`, { method: "POST" }); message.textContent = `Validacion: ${invoice.status}`; loadInvoices(); };
window.reprocessInvoice = async id => { message.textContent = "Reprocesando..."; const invoice = await api(`/api/invoices/${id}/reprocess`, { method: "POST" }); message.textContent = `Reproceso: ${invoice.status}`; loadInvoices(); };
window.rejectInvoice = async id => { const reason = prompt("Motivo del rechazo:", "Rechazada por revision administrativa"); if (!reason) return; const invoice = await api(`/api/invoices/${id}/reject`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ reason }) }); message.textContent = `Factura ${invoice.invoice_number} rechazada.`; loadInvoices(); };
window.runRpa = async id => { message.textContent = "Ejecutando Playwright RPA..."; const result = await api(`/api/rpa/invoices/${id}/register`, { method: "POST" }); message.textContent = `${result.status}: ${result.result}`; };
uploadForm.addEventListener("submit", async event => { event.preventDefault(); const body = new FormData(); body.append("file", file.files[0]); try { message.textContent = "Ejecutando Computer Vision y OCR..."; const invoice = await api("/api/invoices/upload", { method: "POST", body }); message.textContent = `Factura ${invoice.invoice_number}: ${invoice.status}.`; uploadForm.reset(); loadInvoices(); } catch (error) { message.textContent = error.message; } });
seed.addEventListener("click", async () => { try { message.textContent = "Procesando dataset..."; const result = await api("/api/invoices/seed-demo", { method: "POST" }); message.textContent = `Dataset procesado: ${result.total} documentos.`; loadInvoices(); } catch (error) { message.textContent = error.message; } });
filters.addEventListener("submit", event => { event.preventDefault(); loadInvoices(); });
clearFilters.addEventListener("click", () => { filters.reset(); loadInvoices(); });
loadInvoices().catch(error => { message.textContent = error.message; });

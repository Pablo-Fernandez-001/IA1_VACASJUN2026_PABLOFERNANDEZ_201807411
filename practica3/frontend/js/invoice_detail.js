const app = document.querySelector("#app");
const invoiceId = new URLSearchParams(location.search).get("id");
app.innerHTML = `<div class="topline"><h1>Detalle de factura</h1><a class="button secondary" href="invoices.html">Volver</a></div><p id="message" class="message"></p>
  <section class="panel" id="summary">Cargando...</section><section class="panel"><h2>Texto OCR bruto</h2><pre id="raw"></pre></section><section class="panel"><h2>Errores de validacion</h2><pre id="errors"></pre></section>
  <section class="panel"><h2>Bitacora</h2><div class="table-wrap"><table><thead><tr><th>Fecha</th><th>Usuario</th><th>Estado</th><th>Resultado</th><th>Error</th></tr></thead><tbody id="logs"></tbody></table></div></section>
  <section class="panel"><h2>Ejecuciones RPA</h2><div class="table-wrap"><table><thead><tr><th>Fecha</th><th>Estado</th><th>Resultado</th><th>Evidencia</th></tr></thead><tbody id="runs"></tbody></table></div></section>`;

async function loadDetail() {
  if (!invoiceId) throw new Error("Falta el identificador de factura.");
  const [invoice, invoiceLogs, rpaRuns] = await Promise.all([api(`/api/invoices/${invoiceId}`), api(`/api/logs?invoice_id=${invoiceId}`), api(`/api/rpa/runs?invoice_id=${invoiceId}`)]);
  summary.innerHTML = `<div class="detail-grid"><div><span>Numero</span><strong>${escapeHtml(invoice.invoice_number)}</strong></div><div><span>Fecha</span><strong>${escapeHtml(invoice.issue_date || "Sin fecha")}</strong></div><div><span>Proveedor</span><strong>${escapeHtml(invoice.provider_name)}</strong></div><div><span>NIT</span><strong>${escapeHtml(invoice.provider_nit)}</strong></div><div><span>Subtotal</span><strong>${money(invoice.subtotal)}</strong></div><div><span>Impuestos</span><strong>${money(invoice.taxes)}</strong></div><div><span>Total</span><strong>${money(invoice.total)}</strong></div><div><span>Estado</span><strong>${statusBadge(invoice.status)}</strong></div><div><span>Archivo</span><strong>${escapeHtml(invoice.file_name)}</strong></div></div>
    <div class="actions detail-actions"><button id="original">Descargar original</button><button id="validate">Validar</button><button id="reprocess" class="secondary">Reprocesar</button><button id="reject" class="danger">Rechazar</button><button id="rpa" class="success">Ejecutar RPA</button></div>`;
  raw.textContent = invoice.raw_text || "Sin texto OCR.";
  try { errors.textContent = JSON.stringify(JSON.parse(invoice.validation_errors || "[]"), null, 2); } catch (_) { errors.textContent = invoice.validation_errors || "[]"; }
  logs.innerHTML = invoiceLogs.map(log => `<tr><td>${new Date(log.created_at).toLocaleString()}</td><td>${escapeHtml(log.username)}</td><td>${statusBadge(log.status)}</td><td>${escapeHtml(log.result)}</td><td>${escapeHtml(log.error_detail)}</td></tr>`).join("");
  runs.innerHTML = rpaRuns.length ? rpaRuns.map(run => `<tr><td>${new Date(run.created_at).toLocaleString()}</td><td>${statusBadge(run.status)}</td><td>${escapeHtml(run.result)}</td><td><button onclick="downloadEvidence(${run.id})">Descargar</button></td></tr>`).join("") : '<tr><td colspan="4">Sin ejecuciones RPA.</td></tr>';
  original.onclick = () => downloadAuthenticated(`/api/invoices/${invoiceId}/file`, invoice.file_name);
  validate.onclick = () => action(`/api/invoices/${invoiceId}/validate`, "Validacion ejecutada");
  reprocess.onclick = () => action(`/api/invoices/${invoiceId}/reprocess`, "Reproceso ejecutado");
  reject.onclick = async () => { const reason = prompt("Motivo del rechazo:", "Rechazada por revision administrativa"); if (!reason) return; await api(`/api/invoices/${invoiceId}/reject`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ reason }) }); message.textContent = "Factura rechazada."; loadDetail(); };
  rpa.onclick = async () => { message.textContent = "Ejecutando RPA..."; const result = await api(`/api/rpa/invoices/${invoiceId}/register`, { method: "POST" }); message.textContent = `${result.status}: ${result.result}`; loadDetail(); };
}
async function action(path, success) { message.textContent = "Procesando..."; await api(path, { method: "POST" }); message.textContent = success; loadDetail(); }
window.downloadEvidence = id => downloadAuthenticated(`/api/rpa/runs/${id}/evidence`, `evidencia_rpa_${id}`);
loadDetail().catch(error => { message.textContent = error.message; });

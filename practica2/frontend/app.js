const apiParam = new URLSearchParams(location.search).get('api');
const API = (apiParam || window.SMARTBOT_API_URL || (location.protocol === 'file:' ? 'http://localhost:8100' : location.origin)).replace(/\/$/, '');
let token = localStorage.getItem('smartbot_token') || '';
let categories = [], symptoms = [], diagnoses = [], rules = [];

const $ = id => document.getElementById(id);
const authHeaders = () => token ? { 'Authorization': `Bearer ${token}` } : {};
async function req(path, opts={}) {
  const headers = { 'Content-Type': 'application/json', ...(opts.headers||{}), ...authHeaders() };
  const res = await fetch(`${API}${path}`, { ...opts, headers });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
function showApp() { $('loginSection').classList.add('hidden'); $('appSection').classList.remove('hidden'); $('logoutBtn').classList.remove('hidden'); initData(); }
function showLogin() { $('loginSection').classList.remove('hidden'); $('appSection').classList.add('hidden'); $('logoutBtn').classList.add('hidden'); }

$('loginBtn').onclick = async () => {
  try { const data = await req('/api/auth/login', {method:'POST', body:JSON.stringify({username:$('username').value, password:$('password').value})}); token=data.access_token; localStorage.setItem('smartbot_token', token); showApp(); }
  catch(e){ $('loginMsg').textContent='No se pudo iniciar sesión: '+e.message; }
};
$('logoutBtn').onclick = () => { localStorage.removeItem('smartbot_token'); token=''; showLogin(); };

document.querySelectorAll('.tabs button').forEach(btn => btn.onclick = () => {
  document.querySelectorAll('.tabs button').forEach(b=>b.classList.remove('active')); btn.classList.add('active');
  document.querySelectorAll('.tab').forEach(t=>t.classList.add('hidden')); $(btn.dataset.tab).classList.remove('hidden');
});

async function initData(){ await Promise.all([loadCategories(), loadFaqs(), loadSymptoms(), loadDiagnoses(), loadRules(), loadSettings(), loadStats()]); }
function actions(edit, del){ return `<div class="actions"><button onclick='${edit}'>Editar</button><button class="secondary" onclick='${del}'>Eliminar</button></div>`; }

async function loadCategories(){ categories = await req('/api/categories'); $('faqCategory').innerHTML = categories.map(c=>`<option value="${c.id}">${c.name}</option>`).join(''); renderCategories(); }
function renderCategories(){ $('categoriesTable').innerHTML = `<tr><th>ID</th><th>Nombre</th><th>Descripción</th><th>Acciones</th></tr>` + categories.map(c=>`<tr><td>${c.id}</td><td>${c.name}</td><td>${c.description||''}</td><td>${actions(`editCategory(${c.id})`,`deleteCategory(${c.id})`)}</td></tr>`).join(''); }
$('categoryForm').onsubmit = async e => { e.preventDefault(); const id=$('categoryId').value; const body={name:$('categoryName').value, description:$('categoryDescription').value}; await req(`/api/categories${id?'/'+id:''}`, {method:id?'PUT':'POST', body:JSON.stringify(body)}); clearCategoryForm(); await loadCategories(); };
function editCategory(id){ const c=categories.find(x=>x.id===id); $('categoryId').value=c.id; $('categoryName').value=c.name; $('categoryDescription').value=c.description||''; }
async function deleteCategory(id){ if(confirm('¿Eliminar categoría?')){ await req(`/api/categories/${id}`,{method:'DELETE'}); await loadCategories(); }}
function clearCategoryForm(){ $('categoryId').value=''; $('categoryForm').reset(); }

async function loadFaqs(){ const faqs = await req('/api/faqs'); $('faqsTable').innerHTML = `<tr><th>ID</th><th>Pregunta</th><th>Respuesta</th><th>Categoría</th><th>Activa</th><th>Acciones</th></tr>` + faqs.map(f=>`<tr><td>${f.id}</td><td>${f.question}</td><td>${f.answer}</td><td>${f.category_id}</td><td>${f.is_active?'Sí':'No'}</td><td>${actions(`editFaq(${f.id})`,`deleteFaq(${f.id})`)}</td></tr>`).join(''); window._faqs=faqs; }
$('faqForm').onsubmit = async e => { e.preventDefault(); const id=$('faqId').value; const body={question:$('faqQuestion').value, answer:$('faqAnswer').value, keywords:$('faqKeywords').value, category_id:+$('faqCategory').value, is_active:$('faqActive').checked}; await req(`/api/faqs${id?'/'+id:''}`, {method:id?'PUT':'POST', body:JSON.stringify(body)}); clearFaqForm(); await loadFaqs(); };
function editFaq(id){ const f=window._faqs.find(x=>x.id===id); $('faqId').value=f.id; $('faqQuestion').value=f.question; $('faqAnswer').value=f.answer; $('faqKeywords').value=f.keywords||''; $('faqCategory').value=f.category_id; $('faqActive').checked=f.is_active; }
async function deleteFaq(id){ if(confirm('¿Eliminar pregunta?')){ await req(`/api/faqs/${id}`,{method:'DELETE'}); await loadFaqs(); }}
function clearFaqForm(){ $('faqId').value=''; $('faqForm').reset(); $('faqActive').checked=true; }
async function testFaqSearch(){ const r=await req(`/api/faqs/search?q=${encodeURIComponent($('faqSearch').value)}`); $('faqSearchResult').textContent = r.answer; }

async function loadSymptoms(){ symptoms = await req('/api/diagnostics/symptoms'); renderSymptoms(); renderRuleSymptomOptions(); renderChecklist(); }
function renderSymptoms(){ $('symptomsTable').innerHTML = `<tr><th>ID</th><th>Código</th><th>Nombre</th><th>Categoría</th><th>Acciones</th></tr>` + symptoms.map(s=>`<tr><td>${s.id}</td><td>${s.code}</td><td>${s.name}</td><td>${s.category}</td><td>${actions(`editSymptom(${s.id})`,`deleteSymptom(${s.id})`)}</td></tr>`).join(''); }
$('symptomForm').onsubmit = async e => { e.preventDefault(); const id=$('symptomId').value; const body={code:$('symptomCode').value, name:$('symptomName').value, description:$('symptomDescription').value, category:$('symptomCategory').value, severity:+$('symptomSeverity').value, is_active:$('symptomActive').checked}; await req(`/api/diagnostics/symptoms${id?'/'+id:''}`, {method:id?'PUT':'POST', body:JSON.stringify(body)}); clearSymptomForm(); await loadSymptoms(); };
function editSymptom(id){ const s=symptoms.find(x=>x.id===id); $('symptomId').value=s.id; $('symptomCode').value=s.code; $('symptomName').value=s.name; $('symptomDescription').value=s.description||''; $('symptomCategory').value=s.category; $('symptomSeverity').value=s.severity; $('symptomActive').checked=s.is_active; }
async function deleteSymptom(id){ if(confirm('¿Eliminar síntoma?')){ await req(`/api/diagnostics/symptoms/${id}`,{method:'DELETE'}); await loadSymptoms(); }}
function clearSymptomForm(){ $('symptomId').value=''; $('symptomForm').reset(); $('symptomActive').checked=true; $('symptomSeverity').value=1; }
function renderChecklist(){ $('symptomChecklist').innerHTML = symptoms.map(s=>`<label><input type="checkbox" value="${s.code}"> <span><b>${s.name}</b><br><small>${s.code} · ${s.category}</small></span></label>`).join(''); }

async function loadDiagnoses(){ diagnoses = await req('/api/diagnostics/diagnoses'); renderDiagnoses(); renderRuleDiagnosisOptions(); }
function renderDiagnoses(){ $('diagnosesTable').innerHTML = `<tr><th>ID</th><th>Código</th><th>Nombre</th><th>Categoría</th><th>Ruta</th><th>Acciones</th></tr>` + diagnoses.map(d=>`<tr><td>${d.id}</td><td>${d.code}</td><td>${d.name}</td><td>${d.category}</td><td>${(d.solution_route||[]).join(' → ')}</td><td>${actions(`editDiagnosis(${d.id})`,`deleteDiagnosis(${d.id})`)}</td></tr>`).join(''); }
$('diagnosisForm').onsubmit = async e => { e.preventDefault(); const id=$('diagnosisId').value; const body={code:$('diagnosisCode').value, name:$('diagnosisName').value, category:$('diagnosisCategory').value, message:$('diagnosisMessage').value, solution_route:$('diagnosisRoute').value.split('\n').filter(Boolean), base_probability:+$('diagnosisBase').value, is_active:$('diagnosisActive').checked}; await req(`/api/diagnostics/diagnoses${id?'/'+id:''}`, {method:id?'PUT':'POST', body:JSON.stringify(body)}); clearDiagnosisForm(); await loadDiagnoses(); };
function editDiagnosis(id){ const d=diagnoses.find(x=>x.id===id); $('diagnosisId').value=d.id; $('diagnosisCode').value=d.code; $('diagnosisName').value=d.name; $('diagnosisCategory').value=d.category; $('diagnosisMessage').value=d.message; $('diagnosisRoute').value=(d.solution_route||[]).join('\n'); $('diagnosisBase').value=d.base_probability; $('diagnosisActive').checked=d.is_active; }
async function deleteDiagnosis(id){ if(confirm('¿Eliminar diagnóstico?')){ await req(`/api/diagnostics/diagnoses/${id}`,{method:'DELETE'}); await loadDiagnoses(); }}
function clearDiagnosisForm(){ $('diagnosisId').value=''; $('diagnosisForm').reset(); $('diagnosisActive').checked=true; $('diagnosisBase').value=100; }
function renderRuleDiagnosisOptions(){ $('ruleDiagnosis').innerHTML = diagnoses.map(d=>`<option value="${d.id}">${d.name}</option>`).join(''); }

async function loadRules(){ rules = await req('/api/diagnostics/rules'); renderRules(); }
function renderRuleSymptomOptions(){ $('ruleSymptoms').innerHTML = symptoms.map(s=>`<option value="${s.id}">${s.name} (${s.code})</option>`).join(''); }
function renderRules(){ $('rulesTable').innerHTML = `<tr><th>ID</th><th>Regla</th><th>Diagnóstico</th><th>Peso</th><th>Síntomas</th><th>Acciones</th></tr>` + rules.map(r=>`<tr><td>${r.id}</td><td>${r.name}</td><td>${r.diagnosis_id}</td><td>${r.weight}%</td><td>${r.symptom_ids.join(', ')}</td><td>${actions(`editRule(${r.id})`,`deleteRule(${r.id})`)}</td></tr>`).join(''); }
$('ruleForm').onsubmit = async e => { e.preventDefault(); const id=$('ruleId').value; const symptom_ids=[...$('ruleSymptoms').selectedOptions].map(o=>+o.value); const body={name:$('ruleName').value, diagnosis_id:+$('ruleDiagnosis').value, weight:+$('ruleWeight').value, explanation:$('ruleExplanation').value, is_active:$('ruleActive').checked, symptom_ids}; await req(`/api/diagnostics/rules${id?'/'+id:''}`, {method:id?'PUT':'POST', body:JSON.stringify(body)}); clearRuleForm(); await loadRules(); };
function editRule(id){ const r=rules.find(x=>x.id===id); $('ruleId').value=r.id; $('ruleName').value=r.name; $('ruleDiagnosis').value=r.diagnosis_id; $('ruleWeight').value=r.weight; $('ruleExplanation').value=r.explanation||''; $('ruleActive').checked=r.is_active; [...$('ruleSymptoms').options].forEach(o=>o.selected=r.symptom_ids.includes(+o.value)); }
async function deleteRule(id){ if(confirm('¿Eliminar regla?')){ await req(`/api/diagnostics/rules/${id}`,{method:'DELETE'}); await loadRules(); }}
function clearRuleForm(){ $('ruleId').value=''; $('ruleForm').reset(); $('ruleActive').checked=true; $('ruleWeight').value=100; }

async function runDiagnosis(){ const symptom_codes=[...document.querySelectorAll('#symptomChecklist input:checked')].map(i=>i.value); const data=await req('/api/diagnostics/diagnose',{method:'POST', body:JSON.stringify({symptom_codes})}); $('diagnosisResult').innerHTML = data.diagnostics.length ? data.diagnostics.map(d=>`<div class="diag"><h3>${d.name} <span class="badge">${d.probability}%</span></h3><p>${d.message}</p><p><b>Categoría:</b> ${d.category} · <b>Nivel:</b> ${d.problem_level}</p><p><b>Coincidencias:</b> ${d.matched}/${d.total_required}</p><p><b>Ruta de solución:</b> ${(d.solution_route||[]).join(' → ')}</p><p><b>Faltantes:</b> ${(d.missing_symptoms||[]).join(', ') || 'ninguno'}</p></div>`).join('') : '<p class="msg">No hay diagnósticos posibles.</p>'; }

async function loadSettings(){
  const items=await req('/api/settings');
  const settingCards = items.map(s=>`<div class="setting-panel"><label>${s.key}<input id="set_${s.key}" value="${s.value||''}"></label><p>${s.description||''}</p><button onclick="saveSetting('${s.key}')">Guardar</button></div>`).join('');
  const telegramCard = `<div class="setting-panel"><label>Mensaje de prueba Telegram<textarea id="telegramTestText">SmartBot Practica 2: mensaje de prueba.</textarea></label><button onclick="sendTelegramTest()">Enviar prueba</button><p id="telegramTestResult" class="msg"></p></div>`;
  $('settingsBox').innerHTML = settingCards + telegramCard;
}
async function saveSetting(key){ await req(`/api/settings/${key}`,{method:'PUT', body:JSON.stringify({value:$(`set_${key}`).value, description:''})}); await loadSettings(); }
async function sendTelegramTest(){
  try{
    const data = await req('/api/settings/telegram/test',{method:'POST', body:JSON.stringify({text:$('telegramTestText').value})});
    $('telegramTestResult').textContent = data.sent ? 'Mensaje enviado al chat configurado.' : `No enviado: ${data.reason || 'revisa token y chat_id'}`;
  }catch(e){
    $('telegramTestResult').textContent = 'No se pudo enviar: '+e.message;
  }
}
async function loadStats(){ try{ const s=await req('/api/stats'); $('statsBox').innerHTML = `<div class="stat"><strong>${s.total_queries}</strong> consultas</div><div class="stat"><strong>${s.unique_users}</strong> usuarios</div>` + s.by_type.map(x=>`<div class="stat"><strong>${x.total}</strong>${x.type}</div>`).join(''); const logs=await req('/api/stats/logs'); $('logsTable').innerHTML = `<tr><th>Fecha</th><th>Usuario</th><th>Consulta</th><th>Respuesta</th><th>Tipo</th></tr>` + logs.map(l=>`<tr><td>${l.created_at}</td><td>${l.telegram_user}</td><td>${l.query_text}</td><td>${l.response_text}</td><td>${l.matched_type}</td></tr>`).join(''); }catch(e){ console.warn(e); } }

if(token) showApp(); else showLogin();

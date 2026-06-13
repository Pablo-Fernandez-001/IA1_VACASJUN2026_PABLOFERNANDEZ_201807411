const apiParam = new URLSearchParams(location.search).get('api');
const API = (apiParam || window.SMARTBOT_API_URL || (location.protocol === 'file:' ? 'http://localhost:8100' : location.origin)).replace(/\/$/, '');
let token = localStorage.getItem('smartbot_token') || '';
let categories = [];
let questions = [];
let answers = [];

const $ = (id) => document.getElementById(id);
const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
const authHeaders = () => token ? { Authorization: `Bearer ${token}` } : {};

async function getErrorMessage(response) {
  try {
    const data = await response.json();
    return data?.detail || JSON.stringify(data);
  } catch (_) {
    const text = await response.text();
    return text || `Error ${response.status}`;
  }
}

async function req(path, options = {}) {
  const shouldSendAuth = !path.startsWith('/api/auth/login');
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
      ...(shouldSendAuth ? authHeaders() : {}),
    },
  });
  if (response.status === 401) {
    localStorage.removeItem('smartbot_token');
    token = '';
    showLogin();
    throw new Error('Sesion expirada o token invalido. Inicia sesion nuevamente.');
  }
  if (!response.ok) throw new Error(await getErrorMessage(response));
  return response.json();
}

function message(text = '') { $('globalMsg').textContent = text; }
function actions(editCall, deleteCall) { return `<div class="actions"><button onclick="${editCall}">Editar</button><button class="secondary" onclick="${deleteCall}">Eliminar</button></div>`; }
function showLogin() { $('loginSection').classList.remove('hidden'); $('appSection').classList.add('hidden'); $('logoutBtn').classList.add('hidden'); }
async function showApp() {
  $('loginSection').classList.add('hidden'); $('appSection').classList.remove('hidden'); $('logoutBtn').classList.remove('hidden');
  try { await initData(); message(''); } catch (error) { message(error.message); }
}

$('loginBtn').onclick = async () => {
  try {
    const data = await req('/api/auth/login', { method: 'POST', body: JSON.stringify({ username: $('username').value, password: $('password').value }) });
    token = data.access_token; localStorage.setItem('smartbot_token', token); $('loginMsg').textContent = ''; await showApp();
  } catch (error) { $('loginMsg').textContent = `No se pudo iniciar sesión: ${error.message}`; }
};
$('logoutBtn').onclick = () => { localStorage.removeItem('smartbot_token'); token = ''; showLogin(); };

document.querySelectorAll('.tabs button').forEach((button) => {
  button.onclick = () => {
    document.querySelectorAll('.tabs button').forEach((item) => item.classList.remove('active'));
    document.querySelectorAll('.tab').forEach((tab) => tab.classList.add('hidden'));
    button.classList.add('active'); $(button.dataset.tab).classList.remove('hidden');
  };
});

async function initData() { await loadCategories(); await Promise.all([loadQuestions(), loadAnswers(), loadSettings(), loadStats()]); }

async function loadCategories() {
  categories = await req('/api/categories');
  $('questionCategory').innerHTML = categories.map((item) => `<option value="${item.id}">${escapeHtml(item.name)}</option>`).join('');
  $('categoriesTable').innerHTML = '<tr><th>ID</th><th>Nombre</th><th>Descripción</th><th>Acciones</th></tr>' + categories.map((item) => `<tr><td>${item.id}</td><td>${escapeHtml(item.name)}</td><td>${escapeHtml(item.description)}</td><td>${actions(`editCategory(${item.id})`, `deleteCategory(${item.id})`)}</td></tr>`).join('');
}
$('categoryForm').onsubmit = async (event) => {
  event.preventDefault();
  try {
    const id = $('categoryId').value;
    await req(`/api/categories${id ? `/${id}` : ''}`, { method: id ? 'PUT' : 'POST', body: JSON.stringify({ name: $('categoryName').value, description: $('categoryDescription').value }) });
    clearCategoryForm(); await loadCategories(); message('Categoría guardada.');
  } catch (error) { message(error.message); }
};
function editCategory(id) { const item = categories.find((row) => row.id === id); $('categoryId').value = item.id; $('categoryName').value = item.name; $('categoryDescription').value = item.description || ''; }
async function deleteCategory(id) { if (confirm('¿Eliminar categoría?')) { try { await req(`/api/categories/${id}`, { method: 'DELETE' }); await loadCategories(); } catch (error) { message(error.message); } } }
function clearCategoryForm() { $('categoryId').value = ''; $('categoryForm').reset(); }

async function loadQuestions() {
  questions = await req('/api/questions');
  $('answerQuestion').innerHTML = questions.map((item) => `<option value="${item.id}">${escapeHtml(item.text)}</option>`).join('');
  $('questionsTable').innerHTML = '<tr><th>ID</th><th>Pregunta</th><th>Palabras clave</th><th>Categoría</th><th>Activa</th><th>Acciones</th></tr>' + questions.map((item) => `<tr><td>${item.id}</td><td>${escapeHtml(item.text)}</td><td>${escapeHtml(item.keywords)}</td><td>${escapeHtml(categories.find((cat) => cat.id === item.category_id)?.name || item.category_id)}</td><td>${item.is_active ? 'Sí' : 'No'}</td><td>${actions(`editQuestion(${item.id})`, `deleteQuestion(${item.id})`)}</td></tr>`).join('');
}
$('questionForm').onsubmit = async (event) => {
  event.preventDefault();
  try {
    const id = $('questionId').value;
    const body = { text: $('questionText').value, keywords: $('questionKeywords').value, category_id: Number($('questionCategory').value), is_active: $('questionActive').checked };
    await req(`/api/questions${id ? `/${id}` : ''}`, { method: id ? 'PUT' : 'POST', body: JSON.stringify(body) });
    clearQuestionForm(); await loadQuestions(); message('Pregunta guardada en SQLite.');
  } catch (error) { message(error.message); }
};
function editQuestion(id) { const item = questions.find((row) => row.id === id); $('questionId').value = item.id; $('questionText').value = item.text; $('questionKeywords').value = item.keywords || ''; $('questionCategory').value = item.category_id; $('questionActive').checked = item.is_active; }
async function deleteQuestion(id) { if (confirm('¿Eliminar pregunta y sus respuestas?')) { await req(`/api/questions/${id}`, { method: 'DELETE' }); await Promise.all([loadQuestions(), loadAnswers()]); } }
function clearQuestionForm() { $('questionId').value = ''; $('questionForm').reset(); $('questionActive').checked = true; }

async function loadAnswers() {
  answers = await req('/api/answers');
  $('answersTable').innerHTML = '<tr><th>ID</th><th>Pregunta</th><th>Respuesta</th><th>Prioridad</th><th>Activa</th><th>Acciones</th></tr>' + answers.map((item) => `<tr><td>${item.id}</td><td>${escapeHtml(questions.find((question) => question.id === item.question_id)?.text || item.question_id)}</td><td>${escapeHtml(item.text)}</td><td>${item.priority}</td><td>${item.is_active ? 'Sí' : 'No'}</td><td>${actions(`editAnswer(${item.id})`, `deleteAnswer(${item.id})`)}</td></tr>`).join('');
}
$('answerForm').onsubmit = async (event) => {
  event.preventDefault();
  try {
    const id = $('answerId').value;
    const body = { question_id: Number($('answerQuestion').value), text: $('answerText').value, priority: Number($('answerPriority').value || 1), is_active: $('answerActive').checked };
    await req(`/api/answers${id ? `/${id}` : ''}`, { method: id ? 'PUT' : 'POST', body: JSON.stringify(body) });
    clearAnswerForm(); await loadAnswers(); message('Respuesta guardada en SQLite.');
  } catch (error) { message(error.message); }
};
function editAnswer(id) { const item = answers.find((row) => row.id === id); $('answerId').value = item.id; $('answerQuestion').value = item.question_id; $('answerText').value = item.text; $('answerPriority').value = item.priority; $('answerActive').checked = item.is_active; }
async function deleteAnswer(id) { if (confirm('¿Eliminar respuesta?')) { await req(`/api/answers/${id}`, { method: 'DELETE' }); await loadAnswers(); } }
function clearAnswerForm() { $('answerId').value = ''; $('answerForm').reset(); $('answerPriority').value = 1; $('answerActive').checked = true; }

async function testSearch() {
  try {
    const result = await req(`/api/search?q=${encodeURIComponent($('searchText').value)}&telegram_user=panel`);
    $('searchResult').innerHTML = `<div class="diag"><h3>${result.found ? escapeHtml(result.question) : 'Sin coincidencia'}</h3><p>${escapeHtml(result.answer)}</p>${result.category ? `<span class="badge">${escapeHtml(result.category)}</span>` : ''}</div>`;
    await loadStats();
  } catch (error) { message(error.message); }
}

async function loadSettings() {
  const items = await req('/api/settings');
  $('settingsBox').innerHTML = items.map((item) => `<div class="setting-panel"><label>${escapeHtml(item.key)}<input id="setting_${escapeHtml(item.key)}" value="${escapeHtml(item.value)}"></label><p>${escapeHtml(item.description)}</p><button onclick="saveSetting('${escapeHtml(item.key)}')">Guardar</button></div>`).join('') + '<div class="setting-panel"><label>Mensaje de prueba Telegram<textarea id="telegramTestText">SmartBot Práctica 2: mensaje de prueba.</textarea></label><button onclick="sendTelegramTest()">Enviar prueba</button><p id="telegramTestResult" class="msg"></p></div>';
}
async function saveSetting(key) { await req(`/api/settings/${key}`, { method: 'PUT', body: JSON.stringify({ value: $(`setting_${key}`).value, description: '' }) }); await loadSettings(); message('Configuración guardada.'); }
async function sendTelegramTest() {
  try { const data = await req('/api/settings/telegram/test', { method: 'POST', body: JSON.stringify({ text: $('telegramTestText').value }) }); $('telegramTestResult').textContent = data.sent ? 'Mensaje enviado.' : `No enviado: ${data.reason || 'revisa token y chat ID'}`; }
  catch (error) { $('telegramTestResult').textContent = error.message; }
}

async function loadStats() {
  const stats = await req('/api/stats');
  $('statsBox').innerHTML = `<div class="stat"><strong>${stats.total_queries}</strong>consultas</div><div class="stat"><strong>${stats.unique_users}</strong>usuarios</div>` + stats.by_type.map((item) => `<div class="stat"><strong>${item.total}</strong>${escapeHtml(item.type)}</div>`).join('');
  $('topQueries').innerHTML = stats.top_queries.map((item) => `<div class="stat"><strong>${item.total}</strong>${escapeHtml(item.query)}</div>`).join('') || '<p>Sin consultas todavía.</p>';
  $('topCategories').innerHTML = stats.categories.map((item) => `<div class="stat"><strong>${item.total}</strong>${escapeHtml(item.category)}</div>`).join('') || '<p>Sin categorías consultadas todavía.</p>';
  const logs = await req('/api/stats/logs');
  $('logsTable').innerHTML = '<tr><th>Fecha</th><th>Usuario</th><th>Consulta</th><th>Respuesta</th><th>Tipo</th></tr>' + logs.map((item) => `<tr><td>${escapeHtml(item.created_at)}</td><td>${escapeHtml(item.telegram_user)}</td><td>${escapeHtml(item.query_text)}</td><td>${escapeHtml(item.response_text)}</td><td>${escapeHtml(item.matched_type)}</td></tr>`).join('');
}

if (token) showApp(); else showLogin();

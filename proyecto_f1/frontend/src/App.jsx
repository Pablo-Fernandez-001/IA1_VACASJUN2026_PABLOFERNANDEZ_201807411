import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  Activity,
  BrainCircuit,
  ChevronDown,
  ChevronRight,
  Cpu,
  Edit3,
  FolderOpen,
  History,
  Plus,
  Route,
  Save,
  Search,
  ShieldCheck,
  Trash2,
  Wrench,
  X,
} from 'lucide-react';
import {
  createDiagnosisRule,
  createSymptom,
  deleteDiagnosisRule,
  deleteHistory,
  deleteSymptom,
  diagnose,
  getDiagnosisRules,
  getHistory,
  getHistoryItem,
  getSymptoms,
  updateDiagnosisRule,
  updateSymptom,
} from './api';
import './styles.css';

const emptySymptom = { id: '', name: '', category: '', weight: '' };
const emptyRule = {
  id: '',
  name: '',
  message: '',
  category: '',
  severity: 'media',
  enabled: true,
  min_score: '',
  required_symptoms: '',
  support_symptoms: '',
  recommendations: '',
  solution_steps: '',
};

function Badge({ children }) {
  return <span className="badge">{children}</span>;
}

function splitList(value) {
  return value
    .split(/[\n,]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function lines(value) {
  return value
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean);
}

function ruleToForm(rule) {
  return {
    ...rule,
    required_symptoms: (rule.required_symptoms || []).join(', '),
    support_symptoms: (rule.support_symptoms || []).join(', '),
    recommendations: (rule.recommendations || []).join('\n'),
    solution_steps: (rule.solution_steps || []).join('\n'),
  };
}

function formToRule(form) {
  return {
    id: form.id.trim(),
    name: form.name.trim(),
    message: form.message.trim(),
    category: form.category.trim(),
    severity: form.severity,
    enabled: Boolean(form.enabled),
    min_score: Number(form.min_score || 0),
    required_symptoms: splitList(form.required_symptoms),
    support_symptoms: splitList(form.support_symptoms),
    recommendations: lines(form.recommendations),
    solution_steps: lines(form.solution_steps),
  };
}

function App() {
  const [symptoms, setSymptoms] = useState([]);
  const [rules, setRules] = useState([]);
  const [selected, setSelected] = useState([]);
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('todas');
  const [userName, setUserName] = useState('Pablo Fernandez');
  const [notifyTelegram, setNotifyTelegram] = useState(false);
  const [chatId, setChatId] = useState('');
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [adminTab, setAdminTab] = useState('rules');
  const [symptomForm, setSymptomForm] = useState(emptySymptom);
  const [editingSymptomId, setEditingSymptomId] = useState('');
  const [ruleForm, setRuleForm] = useState(emptyRule);
  const [editingRuleId, setEditingRuleId] = useState('');
  const [expandedDiagnosisId, setExpandedDiagnosisId] = useState('');

  async function loadCatalogs() {
    const [symptomData, ruleData] = await Promise.all([getSymptoms(), getDiagnosisRules()]);
    setSymptoms(symptomData.symptoms);
    setRules(ruleData.diagnosis_rules);
  }

  async function loadAll() {
    const [historyData] = await Promise.all([getHistory(), loadCatalogs()]);
    setHistory(historyData);
  }

  useEffect(() => {
    loadAll().catch((err) => setError(err.message));
  }, []);

  const categories = useMemo(() => ['todas', ...new Set(symptoms.map((s) => s.category))], [symptoms]);
  const diagnostics = result?.result?.diagnostics || [];
  const top = diagnostics[0];

  useEffect(() => {
    if (top?.id) {
      setExpandedDiagnosisId(top.id);
    }
  }, [top?.id]);

  const symptomName = useMemo(() => {
    return symptoms.reduce((acc, symptom) => ({ ...acc, [symptom.id]: symptom.name }), {});
  }, [symptoms]);

  const filteredSymptoms = useMemo(() => {
    return symptoms.filter((s) => {
      const haystack = `${s.name} ${s.id} ${s.category}`.toLowerCase();
      const matchesQuery = haystack.includes(query.toLowerCase());
      const matchesCategory = category === 'todas' || s.category === category;
      return matchesQuery && matchesCategory;
    });
  }, [symptoms, query, category]);

  function toggleSymptom(id) {
    setSelected((current) => (current.includes(id) ? current.filter((x) => x !== id) : [...current, id]));
  }

  async function handleDiagnose() {
    setError('');
    if (selected.length === 0) {
      setError('Selecciona al menos un sintoma para diagnosticar.');
      return;
    }
    setLoading(true);
    try {
      const data = await diagnose({
        symptoms: selected,
        user_name: userName || 'Usuario',
        notify_telegram: notifyTelegram,
        telegram_chat_id: chatId || null,
      });
      setResult(data);
      setHistory(await getHistory());
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleSaveSymptom(event) {
    event.preventDefault();
    setError('');
    try {
      const payload = { ...symptomForm, id: symptomForm.id.trim(), name: symptomForm.name.trim(), category: symptomForm.category.trim(), weight: Number(symptomForm.weight || 3) };
      if (editingSymptomId) {
        await updateSymptom(editingSymptomId, payload);
      } else {
        await createSymptom(payload);
      }
      setSymptomForm(emptySymptom);
      setEditingSymptomId('');
      await loadCatalogs();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDeleteSymptom(id) {
    await deleteSymptom(id);
    setSelected((current) => current.filter((item) => item !== id));
    await loadCatalogs();
  }

  async function handleSaveRule(event) {
    event.preventDefault();
    setError('');
    try {
      const payload = formToRule(ruleForm);
      if (editingRuleId) {
        await updateDiagnosisRule(editingRuleId, payload);
      } else {
        await createDiagnosisRule(payload);
      }
      setRuleForm(emptyRule);
      setEditingRuleId('');
      await loadCatalogs();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDeleteRule(id) {
    await deleteDiagnosisRule(id);
    await loadCatalogs();
  }

  async function handleDeleteHistory(id) {
    await deleteHistory(id);
    setHistory(await getHistory());
  }

  async function handleLoadHistory(id) {
    setError('');
    try {
      const record = await getHistoryItem(id);
      setResult(record);
      setSelected(record.selected_symptoms || []);
      setUserName(record.user_name || 'Usuario');
      setNotifyTelegram(false);
      setChatId('');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="page-shell">
      <header className="hero">
        <div>
          <div className="eyebrow"><Cpu size={18}/> Sistema experto editable</div>
          <h1>Doctor Byte</h1>
          <p>Diagnostico de fallas comunes con sintomas, reglas, probabilidades y rutas de solucion editables.</p>
          <div className="hero-actions">
            <Badge>{symptoms.length} sintomas</Badge><Badge>{rules.length} reglas</Badge><Badge>Prolog</Badge><Badge>CRUD</Badge><Badge>Telegram</Badge>
          </div>
        </div>
        <div className="hero-card">
          <BrainCircuit size={54}/>
          <strong>Motor Prolog</strong>
          <span>Calcula todos los diagnosticos posibles desde reglas modificables.</span>
        </div>
      </header>

      {error && <div className="alert">{error}</div>}

      {top && (
        <section className="panel result-panel">
          <h2><BrainCircuit/> Resultado principal</h2>
          <div className="result-layout">
            <div className="score-ring"><span>{top.probability ?? top.score}%</span><small>probabilidad</small></div>
            <div>
              <h3>{top.name}</h3>
              <p>{top.message}</p>
              <p>Categoria: <b>{top.category}</b> | Severidad: <b>{top.severity}</b> | Problema: <b>{top.problem_percentage}%</b> | Efectividad: <b>{top.effectiveness_probability}%</b></p>
              <h4><Route size={18}/> Ruta de solucion</h4>
              <ol>{top.solution_steps?.map((step) => <li key={step}>{step}</li>)}</ol>
            </div>
          </div>
          <h4>Diagnosticos posibles</h4>
          <div className="diagnostic-list">
            {diagnostics.map((d) => (
              <div key={d.id} className={`diagnostic-card ${expandedDiagnosisId === d.id ? 'open' : ''}`}>
                <button
                  className="diagnostic-toggle"
                  type="button"
                  onClick={() => setExpandedDiagnosisId((current) => (current === d.id ? '' : d.id))}
                  aria-expanded={expandedDiagnosisId === d.id}
                >
                  <span className="diagnostic-title">
                    <b>{d.name}</b>
                    <small>Coinciden: {(d.matched_symptom_ids || []).join(', ') || 'ninguno'}</small>
                  </span>
                  <span className="diagnostic-score">
                    <strong>{d.probability ?? d.score}%</strong>
                    <small>probabilidad</small>
                  </span>
                  {expandedDiagnosisId === d.id ? <ChevronDown size={18}/> : <ChevronRight size={18}/>}
                </button>
                <div className="diagnostic-metrics">
                  <span>{d.problem_percentage}% problema</span>
                  <span>{d.effectiveness_probability}% efectividad</span>
                  <span>{d.severity}</span>
                </div>
                {expandedDiagnosisId === d.id && (
                  <div className="diagnostic-route">
                    <h5><Route size={16}/> Ruta posible de solucion</h5>
                    {d.solution_steps?.length ? (
                      <ol>{d.solution_steps.map((step) => <li key={step}>{step}</li>)}</ol>
                    ) : (
                      <p>No hay pasos registrados para esta regla.</p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      <main className="grid-main">
        <section className="panel controls-panel">
          <h2><ShieldCheck/> Diagnostico</h2>
          <label>Nombre del usuario</label>
          <input value={userName} onChange={(e) => setUserName(e.target.value)} />

          <div className="switch-row">
            <input type="checkbox" checked={notifyTelegram} onChange={(e) => setNotifyTelegram(e.target.checked)} />
            <span>Enviar resultado por Telegram</span>
          </div>
          {notifyTelegram && <input placeholder="Chat ID de Telegram" value={chatId} onChange={(e) => setChatId(e.target.value)} />}

          <div className="selected-box">
            <strong>Sintomas seleccionados: {selected.length}</strong>
            <div className="selected-tags">
              {selected.map((id) => <button key={id} onClick={() => toggleSymptom(id)}>{symptomName[id] || id} <X size={13}/></button>)}
              {selected.length === 0 && <span>Aun no hay sintomas seleccionados.</span>}
            </div>
          </div>

          <button className="primary" onClick={handleDiagnose} disabled={loading}>{loading ? 'Diagnosticando...' : 'Solicitar diagnostico'}</button>
          <button className="secondary" onClick={() => { setSelected([]); setResult(null); }}>Limpiar seleccion</button>
        </section>

        <section className="panel symptoms-panel">
          <h2><Activity/> Catalogo de sintomas</h2>
          <div className="toolbar">
            <div className="search"><Search size={18}/><input placeholder="Buscar sintoma..." value={query} onChange={(e) => setQuery(e.target.value)} /></div>
            <select value={category} onChange={(e) => setCategory(e.target.value)}>{categories.map((c) => <option key={c} value={c}>{c}</option>)}</select>
          </div>
          <div className="symptom-grid">
            {filteredSymptoms.map((s) => (
              <button key={s.id} className={`symptom-card ${selected.includes(s.id) ? 'active' : ''}`} onClick={() => toggleSymptom(s.id)}>
                <span>{s.name}</span>
                <small>{s.category} | peso {s.weight}</small>
              </button>
            ))}
          </div>
        </section>
      </main>

      <section className="panel admin-panel">
        <h2><Wrench/> Administracion de conocimiento</h2>
        <div className="tabs">
          <button className={adminTab === 'rules' ? 'active' : ''} onClick={() => setAdminTab('rules')}>Reglas diagnosticas</button>
          <button className={adminTab === 'symptoms' ? 'active' : ''} onClick={() => setAdminTab('symptoms')}>Sintomas</button>
        </div>

        {adminTab === 'rules' && (
          <div className="admin-grid">
            <form className="editor-form" onSubmit={handleSaveRule}>
              <h3>{editingRuleId ? 'Editar regla' : 'Nueva regla'}</h3>
              <label>ID</label>
              <input value={ruleForm.id} onChange={(e) => setRuleForm({ ...ruleForm, id: e.target.value })} placeholder="falla_gpu_temporal" required />
              <label>Nombre</label>
              <input value={ruleForm.name} onChange={(e) => setRuleForm({ ...ruleForm, name: e.target.value })} placeholder="Problema de tarjeta grafica" required />
              <label>Mensaje</label>
              <textarea value={ruleForm.message} onChange={(e) => setRuleForm({ ...ruleForm, message: e.target.value })} placeholder="El equipo inicia, pero no entrega imagen correctamente." />
              <div className="form-row">
                <div><label>Categoria</label><input value={ruleForm.category} onChange={(e) => setRuleForm({ ...ruleForm, category: e.target.value })} placeholder="hardware" required /></div>
                <div><label>Severidad</label><select value={ruleForm.severity} onChange={(e) => setRuleForm({ ...ruleForm, severity: e.target.value })}><option>baja</option><option>media</option><option>alta</option><option>critica</option></select></div>
                <div><label>Min %</label><input type="number" min="0" max="100" value={ruleForm.min_score} onChange={(e) => setRuleForm({ ...ruleForm, min_score: e.target.value })} placeholder="60" /></div>
              </div>
              <label>Sintomas requeridos</label>
              <textarea value={ruleForm.required_symptoms} onChange={(e) => setRuleForm({ ...ruleForm, required_symptoms: e.target.value })} placeholder="pantalla_negra, ventiladores_giran" />
              <label>Sintomas de apoyo</label>
              <textarea value={ruleForm.support_symptoms} onChange={(e) => setRuleForm({ ...ruleForm, support_symptoms: e.target.value })} placeholder="beeps_arranque, reinicios_inesperados" />
              <label>Recomendaciones</label>
              <textarea value={ruleForm.recommendations} onChange={(e) => setRuleForm({ ...ruleForm, recommendations: e.target.value })} placeholder={'Probar otro cable de video\nReinstalar o limpiar la tarjeta grafica\nActualizar el controlador'} />
              <label>Ruta de solucion</label>
              <textarea value={ruleForm.solution_steps} onChange={(e) => setRuleForm({ ...ruleForm, solution_steps: e.target.value })} placeholder={'Probar monitor y cable alterno\nCambiar puerto de salida de video\nReinstalar GPU o limpiar contactos'} />
              <div className="switch-row">
                <input type="checkbox" checked={ruleForm.enabled} onChange={(e) => setRuleForm({ ...ruleForm, enabled: e.target.checked })} />
                <span>Regla activa</span>
              </div>
              <button className="primary" type="submit"><Save size={17}/> Guardar regla</button>
              {editingRuleId && <button className="secondary" type="button" onClick={() => { setEditingRuleId(''); setRuleForm(emptyRule); }}>Cancelar edicion</button>}
            </form>
            <div className="admin-list">
              {rules.map((rule) => (
                <div key={rule.id} className="admin-item">
                  <div><b>{rule.name}</b><span>{rule.id} | {rule.category} | {rule.severity}</span></div>
                  <div className="row-actions">
                    <button className="icon-btn" onClick={() => { setEditingRuleId(rule.id); setRuleForm(ruleToForm(rule)); }}><Edit3 size={16}/></button>
                    <button className="icon-btn danger" onClick={() => handleDeleteRule(rule.id)}><Trash2 size={16}/></button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {adminTab === 'symptoms' && (
          <div className="admin-grid">
            <form className="editor-form" onSubmit={handleSaveSymptom}>
              <h3>{editingSymptomId ? 'Editar sintoma' : 'Nuevo sintoma'}</h3>
              <label>ID</label>
              <input value={symptomForm.id} onChange={(e) => setSymptomForm({ ...symptomForm, id: e.target.value })} placeholder="pantalla_parpadea" required />
              <label>Nombre</label>
              <input value={symptomForm.name} onChange={(e) => setSymptomForm({ ...symptomForm, name: e.target.value })} placeholder="La pantalla parpadea constantemente" required />
              <div className="form-row">
                <div><label>Categoria</label><input value={symptomForm.category} onChange={(e) => setSymptomForm({ ...symptomForm, category: e.target.value })} placeholder="video" required /></div>
                <div><label>Peso</label><input type="number" min="1" max="5" value={symptomForm.weight} onChange={(e) => setSymptomForm({ ...symptomForm, weight: e.target.value })} placeholder="3" /></div>
              </div>
              <button className="primary" type="submit"><Plus size={17}/> Guardar sintoma</button>
              {editingSymptomId && <button className="secondary" type="button" onClick={() => { setEditingSymptomId(''); setSymptomForm(emptySymptom); }}>Cancelar edicion</button>}
            </form>
            <div className="admin-list">
              {symptoms.map((symptom) => (
                <div key={symptom.id} className="admin-item">
                  <div><b>{symptom.name}</b><span>{symptom.id} | {symptom.category} | peso {symptom.weight}</span></div>
                  <div className="row-actions">
                    <button className="icon-btn" onClick={() => { setEditingSymptomId(symptom.id); setSymptomForm(symptom); }}><Edit3 size={16}/></button>
                    <button className="icon-btn danger" onClick={() => handleDeleteSymptom(symptom.id)}><Trash2 size={16}/></button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>

      <section className="panel history-panel">
        <h2><History/> Historial de diagnosticos</h2>
        <div className="table-wrap">
          <table>
            <thead><tr><th>ID</th><th>Fecha</th><th>Usuario</th><th>Diagnostico</th><th>Sintomas</th><th>Telegram</th><th>Acciones</th></tr></thead>
            <tbody>
              {history.map((h) => <tr key={h.id}>
                <td>{h.id}</td><td>{new Date(h.created_at).toLocaleString()}</td><td>{h.user_name}</td><td>{h.top_diagnosis}</td>
                <td>{h.selected_symptoms.join(', ')}</td><td>{h.telegram_sent}</td>
                <td>
                  <div className="row-actions">
                    <button className="icon-btn" title="Cargar diagnostico" aria-label={`Cargar diagnostico ${h.id}`} onClick={() => handleLoadHistory(h.id)}><FolderOpen size={16}/></button>
                    <button className="icon-btn danger" title="Eliminar diagnostico" aria-label={`Eliminar diagnostico ${h.id}`} onClick={() => handleDeleteHistory(h.id)}><Trash2 size={16}/></button>
                  </div>
                </td>
              </tr>)}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);

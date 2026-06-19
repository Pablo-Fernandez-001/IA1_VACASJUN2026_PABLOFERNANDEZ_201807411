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
  createFailure,
  createRecommendation,
  createSymptom,
  deleteDiagnosisRule,
  deleteFailure,
  deleteHistory,
  deleteRecommendation,
  deleteSymptom,
  diagnose,
  getConfig,
  getDiagnosisRules,
  getFailures,
  getHistory,
  getHistoryItem,
  getRecommendations,
  getSymptoms,
  updateConfig,
  updateDiagnosisRule,
  updateFailure,
  updateRecommendation,
  updateSymptom,
} from './api';
import './styles.css';

const emptySymptom = { id: '', name: '', category: '', weight: '' };
const emptyRule = {
  id: '',
  failure_id: '',
  enabled: true,
  min_score: '',
  required_symptoms: '',
  support_symptoms: '',
};
const emptyFailure = { id: '', name: '', message: '', category: '', severity: 'media', solution_steps: '' };
const emptyRecommendation = { id: '', failure_id: '', text: '', order: 1 };
const defaultConfig = {
  bot_id: '', bot_active: true,
  welcome_message: 'Hola, soy Doctor Byte. Usa /sintomas para consultar el catalogo.',
  diagnosis_message: 'Analice tus sintomas con el motor experto Prolog.',
  no_diagnosis_message: 'No encontre un diagnostico concluyente.',
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

function normalizeId(value, prefix = 'regla') {
  const normalized = value
    .trim()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '');
  return /^\d/.test(normalized) ? `${prefix}_${normalized}` : normalized;
}

function ruleToForm(rule) {
  return {
    ...rule,
    required_symptoms: (rule.required_symptoms || []).join(', '),
    support_symptoms: (rule.support_symptoms || []).join(', '),
  };
}

function formToRule(form) {
  return {
    id: normalizeId(form.id),
    failure_id: form.failure_id,
    enabled: Boolean(form.enabled),
    min_score: Number(form.min_score || 0),
    required_symptoms: splitList(form.required_symptoms),
    support_symptoms: splitList(form.support_symptoms),
  };
}

function App() {
  const [symptoms, setSymptoms] = useState([]);
  const [failures, setFailures] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
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
  const [failureForm, setFailureForm] = useState(emptyFailure);
  const [editingFailureId, setEditingFailureId] = useState('');
  const [recommendationForm, setRecommendationForm] = useState(emptyRecommendation);
  const [editingRecommendationId, setEditingRecommendationId] = useState('');
  const [systemConfig, setSystemConfig] = useState(defaultConfig);
  const [expandedDiagnosisId, setExpandedDiagnosisId] = useState('');

  async function loadCatalogs() {
    const [symptomData, failureData, recommendationData, ruleData, configData] = await Promise.all([
      getSymptoms(), getFailures(), getRecommendations(), getDiagnosisRules(), getConfig(),
    ]);
    setSymptoms(symptomData.symptoms);
    setFailures(failureData.failures);
    setRecommendations(recommendationData.recommendations);
    setRules(ruleData.diagnosis_rules);
    setSystemConfig(configData);
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

  function setRuleSymptomRole(id, role) {
    setRuleForm((current) => {
      const required = splitList(current.required_symptoms).filter((item) => item !== id);
      const support = splitList(current.support_symptoms).filter((item) => item !== id);
      if (role === 'required') required.push(id);
      if (role === 'support') support.push(id);
      return {
        ...current,
        required_symptoms: required.join(', '),
        support_symptoms: support.join(', '),
      };
    });
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
      if (!payload.id) throw new Error('Escribe un ID valido para la regla.');
      if (payload.required_symptoms.length + payload.support_symptoms.length === 0) {
        throw new Error('Selecciona al menos un sintoma requerido o de apoyo.');
      }
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

  async function handleSaveFailure(event) {
    event.preventDefault();
    setError('');
    try {
      const payload = {
        ...failureForm,
        id: failureForm.id.trim(),
        name: failureForm.name.trim(),
        message: failureForm.message.trim(),
        category: failureForm.category.trim(),
        solution_steps: lines(failureForm.solution_steps),
      };
      if (editingFailureId) await updateFailure(editingFailureId, payload);
      else await createFailure(payload);
      setFailureForm(emptyFailure);
      setEditingFailureId('');
      await loadCatalogs();
    } catch (err) { setError(err.message); }
  }

  async function handleSaveRecommendation(event) {
    event.preventDefault();
    setError('');
    try {
      const payload = { ...recommendationForm, id: recommendationForm.id.trim(), text: recommendationForm.text.trim(), order: Number(recommendationForm.order || 1) };
      if (editingRecommendationId) await updateRecommendation(editingRecommendationId, payload);
      else await createRecommendation(payload);
      setRecommendationForm(emptyRecommendation);
      setEditingRecommendationId('');
      await loadCatalogs();
    } catch (err) { setError(err.message); }
  }

  async function handleSaveConfig(event) {
    event.preventDefault();
    setError('');
    try { setSystemConfig(await updateConfig(systemConfig)); }
    catch (err) { setError(err.message); }
  }

  async function handleDeleteRule(id) {
    await deleteDiagnosisRule(id);
    await loadCatalogs();
  }

  async function handleDeleteFailure(id) {
    if (!window.confirm('Eliminar la falla tambien eliminara sus reglas y recomendaciones. ¿Continuar?')) return;
    await deleteFailure(id);
    await loadCatalogs();
  }

  async function handleDeleteRecommendation(id) {
    await deleteRecommendation(id);
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
            <Badge>{symptoms.length} sintomas</Badge><Badge>{failures.length} fallas</Badge><Badge>{recommendations.length} recomendaciones</Badge><Badge>{rules.length} reglas Prolog</Badge>
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
          <button className={adminTab === 'failures' ? 'active' : ''} onClick={() => setAdminTab('failures')}>Fallas</button>
          <button className={adminTab === 'recommendations' ? 'active' : ''} onClick={() => setAdminTab('recommendations')}>Recomendaciones</button>
          <button className={adminTab === 'config' ? 'active' : ''} onClick={() => setAdminTab('config')}>Configuracion</button>
        </div>

        {adminTab === 'rules' && (
          <div className="admin-grid">
            <form className="editor-form" onSubmit={handleSaveRule}>
              <h3>{editingRuleId ? 'Editar regla' : 'Nueva regla'}</h3>
              <label>ID</label>
              <input
                value={ruleForm.id}
                onChange={(e) => setRuleForm({ ...ruleForm, id: e.target.value })}
                onBlur={() => setRuleForm((current) => ({ ...current, id: normalizeId(current.id) }))}
                placeholder="regla_gpu_temporal"
                required
              />
              <small className="field-help">Se permiten palabras normales; el ID se convierte automaticamente a minusculas y guiones bajos.</small>
              <label>Falla diagnosticada</label>
              <select value={ruleForm.failure_id} onChange={(e) => setRuleForm({ ...ruleForm, failure_id: e.target.value })} required>
                <option value="">Selecciona una falla</option>
                {failures.map((failure) => <option key={failure.id} value={failure.id}>{failure.name}</option>)}
              </select>
              <label>Puntaje minimo</label>
              <input type="number" min="0" max="100" value={ruleForm.min_score} onChange={(e) => setRuleForm({ ...ruleForm, min_score: e.target.value })} placeholder="30" />
              <label>Sintomas de la regla</label>
              <div className="rule-symptom-picker">
                {symptoms.map((symptom) => {
                  const required = splitList(ruleForm.required_symptoms).includes(symptom.id);
                  const support = splitList(ruleForm.support_symptoms).includes(symptom.id);
                  return (
                    <div className="rule-symptom-row" key={symptom.id}>
                      <div><b>{symptom.name}</b><small>{symptom.id}</small></div>
                      <button className={required ? 'active required' : ''} type="button" onClick={() => setRuleSymptomRole(symptom.id, required ? 'none' : 'required')}>Requerido</button>
                      <button className={support ? 'active support' : ''} type="button" onClick={() => setRuleSymptomRole(symptom.id, support ? 'none' : 'support')}>Apoyo</button>
                    </div>
                  );
                })}
              </div>
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
                  <div><b>{failures.find((failure) => failure.id === rule.failure_id)?.name || rule.failure_id}</b><span>{rule.id} | minimo {rule.min_score}% | {rule.enabled ? 'activa' : 'inactiva'}</span></div>
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

        {adminTab === 'failures' && (
          <div className="admin-grid">
            <form className="editor-form" onSubmit={handleSaveFailure}>
              <h3>{editingFailureId ? 'Editar falla' : 'Nueva falla'}</h3>
              <label>ID</label><input value={failureForm.id} onChange={(e) => setFailureForm({ ...failureForm, id: e.target.value })} placeholder="falla_nueva" required />
              <label>Nombre</label><input value={failureForm.name} onChange={(e) => setFailureForm({ ...failureForm, name: e.target.value })} required />
              <label>Mensaje de diagnostico</label><textarea value={failureForm.message} onChange={(e) => setFailureForm({ ...failureForm, message: e.target.value })} required />
              <div className="form-row">
                <div><label>Categoria</label><input value={failureForm.category} onChange={(e) => setFailureForm({ ...failureForm, category: e.target.value })} required /></div>
                <div><label>Severidad</label><select value={failureForm.severity} onChange={(e) => setFailureForm({ ...failureForm, severity: e.target.value })}><option>baja</option><option>media</option><option>alta</option><option>critica</option></select></div>
              </div>
              <label>Ruta de solucion, un paso por linea</label><textarea value={failureForm.solution_steps} onChange={(e) => setFailureForm({ ...failureForm, solution_steps: e.target.value })} />
              <button className="primary" type="submit"><Save size={17}/> Guardar falla</button>
              {editingFailureId && <button className="secondary" type="button" onClick={() => { setEditingFailureId(''); setFailureForm(emptyFailure); }}>Cancelar edicion</button>}
            </form>
            <div className="admin-list">
              {failures.map((failure) => <div key={failure.id} className="admin-item">
                <div><b>{failure.name}</b><span>{failure.id} | {failure.category} | {failure.severity}</span></div>
                <div className="row-actions">
                  <button className="icon-btn" onClick={() => { setEditingFailureId(failure.id); setFailureForm({ ...failure, solution_steps: (failure.solution_steps || []).map((step) => step.text).join('\n') }); }}><Edit3 size={16}/></button>
                  <button className="icon-btn danger" onClick={() => handleDeleteFailure(failure.id)}><Trash2 size={16}/></button>
                </div>
              </div>)}
            </div>
          </div>
        )}

        {adminTab === 'recommendations' && (
          <div className="admin-grid">
            <form className="editor-form" onSubmit={handleSaveRecommendation}>
              <h3>{editingRecommendationId ? 'Editar recomendacion' : 'Nueva recomendacion'}</h3>
              <label>ID</label><input value={recommendationForm.id} onChange={(e) => setRecommendationForm({ ...recommendationForm, id: e.target.value })} placeholder="rec_nueva_1" required />
              <label>Falla asociada</label><select value={recommendationForm.failure_id} onChange={(e) => setRecommendationForm({ ...recommendationForm, failure_id: e.target.value })} required><option value="">Selecciona una falla</option>{failures.map((failure) => <option key={failure.id} value={failure.id}>{failure.name}</option>)}</select>
              <label>Texto</label><textarea value={recommendationForm.text} onChange={(e) => setRecommendationForm({ ...recommendationForm, text: e.target.value })} required />
              <label>Orden</label><input type="number" min="1" value={recommendationForm.order} onChange={(e) => setRecommendationForm({ ...recommendationForm, order: e.target.value })} />
              <button className="primary" type="submit"><Save size={17}/> Guardar recomendacion</button>
              {editingRecommendationId && <button className="secondary" type="button" onClick={() => { setEditingRecommendationId(''); setRecommendationForm(emptyRecommendation); }}>Cancelar edicion</button>}
            </form>
            <div className="admin-list">
              {recommendations.map((item) => <div key={item.id} className="admin-item">
                <div><b>{item.text}</b><span>{item.id} | {failures.find((failure) => failure.id === item.failure_id)?.name || item.failure_id}</span></div>
                <div className="row-actions">
                  <button className="icon-btn" onClick={() => { setEditingRecommendationId(item.id); setRecommendationForm(item); }}><Edit3 size={16}/></button>
                  <button className="icon-btn danger" onClick={() => handleDeleteRecommendation(item.id)}><Trash2 size={16}/></button>
                </div>
              </div>)}
            </div>
          </div>
        )}

        {adminTab === 'config' && (
          <form className="editor-form config-form" onSubmit={handleSaveConfig}>
            <h3>Configuracion auxiliar del bot</h3>
            <label>ID del chat o grupo</label><input value={systemConfig.bot_id || ''} onChange={(e) => setSystemConfig({ ...systemConfig, bot_id: e.target.value })} placeholder="-1001234567890" />
            <div className="switch-row"><input type="checkbox" checked={Boolean(systemConfig.bot_active)} onChange={(e) => setSystemConfig({ ...systemConfig, bot_active: e.target.checked })} /><span>Bot activo</span></div>
            <label>Mensaje de bienvenida</label><textarea value={systemConfig.welcome_message || ''} onChange={(e) => setSystemConfig({ ...systemConfig, welcome_message: e.target.value })} required />
            <label>Mensaje antes del diagnostico</label><textarea value={systemConfig.diagnosis_message || ''} onChange={(e) => setSystemConfig({ ...systemConfig, diagnosis_message: e.target.value })} required />
            <label>Mensaje sin diagnostico</label><textarea value={systemConfig.no_diagnosis_message || ''} onChange={(e) => setSystemConfig({ ...systemConfig, no_diagnosis_message: e.target.value })} required />
            <button className="primary" type="submit"><Save size={17}/> Guardar configuracion</button>
          </form>
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

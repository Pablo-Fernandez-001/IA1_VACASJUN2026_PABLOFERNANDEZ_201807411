import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, BrainCircuit, History, Send, ShieldCheck, Trash2, Cpu, Search } from 'lucide-react';
import { deleteHistory, diagnose, getHistory, getSymptoms } from './api';
import './styles.css';

function Badge({ children }) {
  return <span className="badge">{children}</span>;
}

function App() {
  const [symptoms, setSymptoms] = useState([]);
  const [selected, setSelected] = useState([]);
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('todas');
  const [userName, setUserName] = useState('Pablo Fernández');
  const [notifyTelegram, setNotifyTelegram] = useState(false);
  const [chatId, setChatId] = useState('');
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function loadAll() {
    const [symptomData, historyData] = await Promise.all([getSymptoms(), getHistory()]);
    setSymptoms(symptomData.symptoms);
    setHistory(historyData);
  }

  useEffect(() => {
    loadAll().catch((err) => setError(err.message));
  }, []);

  const categories = useMemo(() => ['todas', ...new Set(symptoms.map((s) => s.category))], [symptoms]);

  const filteredSymptoms = useMemo(() => {
    return symptoms.filter((s) => {
      const matchesQuery = `${s.name} ${s.id} ${s.category}`.toLowerCase().includes(query.toLowerCase());
      const matchesCategory = category === 'todas' || s.category === category;
      return matchesQuery && matchesCategory;
    });
  }, [symptoms, query, category]);

  function toggleSymptom(id) {
    setSelected((current) => current.includes(id) ? current.filter((x) => x !== id) : [...current, id]);
  }

  async function handleDiagnose() {
    setError('');
    if (selected.length === 0) {
      setError('Seleccioná al menos un síntoma para diagnosticar.');
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

  async function handleDelete(id) {
    await deleteHistory(id);
    setHistory(await getHistory());
  }

  const top = result?.result?.diagnostics?.[0];

  return (
    <div className="page-shell">
      <header className="hero">
        <div>
          <div className="eyebrow"><Cpu size={18}/> Sistema experto distribuido</div>
          <h1>Doctor Byte</h1>
          <p>Diagnóstico inteligente de fallas comunes en computadoras usando React, FastAPI, SWI-Prolog y Telegram.</p>
          <div className="hero-actions">
            <Badge>+15 síntomas</Badge><Badge>+10 fallas</Badge><Badge>Prolog</Badge><Badge>Telegram</Badge><Badge>Historial dinámico</Badge>
          </div>
        </div>
        <div className="hero-card">
          <BrainCircuit size={54}/>
          <strong>Motor de inferencia</strong>
          <span>Reglas, hechos, listas, variables y corte en Prolog.</span>
        </div>
      </header>

      {error && <div className="alert">{error}</div>}

      <main className="grid-main">
        <section className="panel controls-panel">
          <h2><ShieldCheck/> Datos del diagnóstico</h2>
          <label>Nombre del usuario</label>
          <input value={userName} onChange={(e) => setUserName(e.target.value)} />

          <div className="switch-row">
            <input type="checkbox" checked={notifyTelegram} onChange={(e) => setNotifyTelegram(e.target.checked)} />
            <span>Enviar resultado por Telegram</span>
          </div>
          {notifyTelegram && <input placeholder="Chat ID de Telegram" value={chatId} onChange={(e) => setChatId(e.target.value)} />}

          <div className="selected-box">
            <strong>Síntomas seleccionados: {selected.length}</strong>
            <div className="selected-tags">
              {selected.map((id) => <button key={id} onClick={() => toggleSymptom(id)}>{id} ×</button>)}
              {selected.length === 0 && <span>Aún no hay síntomas seleccionados.</span>}
            </div>
          </div>

          <button className="primary" onClick={handleDiagnose} disabled={loading}>{loading ? 'Diagnosticando...' : 'Solicitar diagnóstico'}</button>
          <button className="secondary" onClick={() => { setSelected([]); setResult(null); }}>Limpiar selección</button>
        </section>

        <section className="panel symptoms-panel">
          <h2><Activity/> Catálogo dinámico de síntomas</h2>
          <div className="toolbar">
            <div className="search"><Search size={18}/><input placeholder="Buscar síntoma..." value={query} onChange={(e) => setQuery(e.target.value)} /></div>
            <select value={category} onChange={(e) => setCategory(e.target.value)}>{categories.map((c) => <option key={c} value={c}>{c}</option>)}</select>
          </div>
          <div className="symptom-grid">
            {filteredSymptoms.map((s) => (
              <button key={s.id} className={`symptom-card ${selected.includes(s.id) ? 'active' : ''}`} onClick={() => toggleSymptom(s.id)}>
                <span>{s.name}</span>
                <small>{s.category} · peso {s.weight}</small>
              </button>
            ))}
          </div>
        </section>
      </main>

      {top && (
        <section className="panel result-panel">
          <h2><BrainCircuit/> Resultado principal</h2>
          <div className="result-layout">
            <div className="score-ring"><span>{top.score}%</span><small>confianza</small></div>
            <div>
              <h3>{top.name}</h3>
              <p>Categoría: <b>{top.category}</b> · Severidad: <b>{top.severity}</b> · Telegram: <b>{result.telegram_sent}</b></p>
              <h4>Recomendaciones</h4>
              <ul>{top.recommendations?.map((r) => <li key={r}>{r}</li>)}</ul>
            </div>
          </div>
          <h4>Otros diagnósticos posibles</h4>
          <div className="diagnostic-list">
            {result.result.diagnostics.slice(1).map((d) => <div key={d.id}><b>{d.name}</b><span>{d.score}% · {d.severity}</span></div>)}
          </div>
        </section>
      )}

      <section className="panel history-panel">
        <h2><History/> Historial de diagnósticos</h2>
        <div className="table-wrap">
          <table>
            <thead><tr><th>ID</th><th>Fecha</th><th>Usuario</th><th>Diagnóstico</th><th>Síntomas</th><th>Telegram</th><th></th></tr></thead>
            <tbody>
              {history.map((h) => <tr key={h.id}>
                <td>{h.id}</td><td>{new Date(h.created_at).toLocaleString()}</td><td>{h.user_name}</td><td>{h.top_diagnosis}</td>
                <td>{h.selected_symptoms.join(', ')}</td><td>{h.telegram_sent}</td>
                <td><button className="icon-btn" onClick={() => handleDelete(h.id)}><Trash2 size={16}/></button></td>
              </tr>)}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);

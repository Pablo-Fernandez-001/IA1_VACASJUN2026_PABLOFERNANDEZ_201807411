const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export async function getSymptoms() {
  const res = await fetch(`${API_BASE}/api/symptoms`);
  if (!res.ok) throw new Error('No se pudieron cargar los síntomas');
  return res.json();
}

export async function diagnose(payload) {
  const res = await fetch(`${API_BASE}/api/diagnose`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getHistory() {
  const res = await fetch(`${API_BASE}/api/history`);
  if (!res.ok) throw new Error('No se pudo cargar el historial');
  return res.json();
}

export async function deleteHistory(id) {
  const res = await fetch(`${API_BASE}/api/history/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('No se pudo eliminar el diagnóstico');
  return res.json();
}

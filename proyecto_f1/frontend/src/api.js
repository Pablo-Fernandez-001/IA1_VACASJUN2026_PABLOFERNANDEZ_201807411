const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export function getKnowledge() {
  return request('/api/knowledge');
}

export function getSymptoms() {
  return request('/api/symptoms');
}

export function createSymptom(payload) {
  return request('/api/symptoms', { method: 'POST', body: JSON.stringify(payload) });
}

export function updateSymptom(id, payload) {
  return request(`/api/symptoms/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
}

export function deleteSymptom(id) {
  return request(`/api/symptoms/${id}`, { method: 'DELETE' });
}

export function getDiagnosisRules() {
  return request('/api/diagnosis-rules');
}

export function createDiagnosisRule(payload) {
  return request('/api/diagnosis-rules', { method: 'POST', body: JSON.stringify(payload) });
}

export function updateDiagnosisRule(id, payload) {
  return request(`/api/diagnosis-rules/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
}

export function deleteDiagnosisRule(id) {
  return request(`/api/diagnosis-rules/${id}`, { method: 'DELETE' });
}

export function diagnose(payload) {
  return request('/api/diagnose', { method: 'POST', body: JSON.stringify(payload) });
}

export function getHistory() {
  return request('/api/history');
}

export function deleteHistory(id) {
  return request(`/api/history/${id}`, { method: 'DELETE' });
}

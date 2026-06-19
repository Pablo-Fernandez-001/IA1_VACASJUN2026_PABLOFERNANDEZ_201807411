const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const detail = data?.detail;
    const message = typeof detail === 'string'
      ? detail
      : Array.isArray(detail)
        ? detail.map((item) => item.msg || JSON.stringify(item)).join('; ')
        : JSON.stringify(detail || data || `Error HTTP ${res.status}`);
    throw new Error(message);
  }
  return data;
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

export function getFailures() { return request('/api/failures'); }
export function createFailure(payload) { return request('/api/failures', { method: 'POST', body: JSON.stringify(payload) }); }
export function updateFailure(id, payload) { return request(`/api/failures/${id}`, { method: 'PUT', body: JSON.stringify(payload) }); }
export function deleteFailure(id) { return request(`/api/failures/${id}`, { method: 'DELETE' }); }

export function getRecommendations() { return request('/api/recommendations'); }
export function createRecommendation(payload) { return request('/api/recommendations', { method: 'POST', body: JSON.stringify(payload) }); }
export function updateRecommendation(id, payload) { return request(`/api/recommendations/${id}`, { method: 'PUT', body: JSON.stringify(payload) }); }
export function deleteRecommendation(id) { return request(`/api/recommendations/${id}`, { method: 'DELETE' }); }

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

export function getHistoryItem(id) {
  return request(`/api/history/${id}`);
}

export function deleteHistory(id) {
  return request(`/api/history/${id}`, { method: 'DELETE' });
}

export function getConfig() { return request('/api/config'); }
export function updateConfig(payload) { return request('/api/config', { method: 'PUT', body: JSON.stringify(payload) }); }

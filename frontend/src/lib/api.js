const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
const tokenKey = 'placementpulse_token'

export async function createPrediction(profile) {
  const response = await fetch(`${API_BASE}/predictions`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ profile, confirmed: true, source: 'manual' }),
  })
  if (!response.ok) throw new Error('Prediction request failed')
  return response.json()
}

export async function extractDocument(file) {
  const form = new FormData()
  form.append('file', file)
  const response = await fetch(`${API_BASE}/documents/extract`, { method: 'POST', body: form })
  if (!response.ok) throw new Error('Document extraction failed')
  return response.json()
}

export async function login(email, password) {
  const response = await fetch(`${API_BASE}/auth/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) })
  if (!response.ok) throw new Error('Invalid email or password')
  const data = await response.json()
  localStorage.setItem(tokenKey, data.token)
  return data.user
}

export function logout() { localStorage.removeItem(tokenKey) }
export function getToken() { return localStorage.getItem(tokenKey) }

export async function getDashboardSummary() {
  const response = await fetch(`${API_BASE}/dashboard/summary`, { headers: { Authorization: `Bearer ${getToken()}` } })
  if (!response.ok) throw new Error('Dashboard unavailable')
  return response.json()
}

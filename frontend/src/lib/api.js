const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api').replace(/\/$/, '')
const tokenKey = 'placementpulse_token'
const userKey = 'placementpulse_user'

export async function createPrediction(profile) {
  const payload = {
    branch: profile.branch,
    college_tier: 'Tier-2',
    cgpa: profile.cgpa,
    backlogs: 0,
    coding_skills: Math.min(Number(profile.coding_problems_solved || 0) / 450, 10),
    dsa_score: Math.min(Number(profile.coding_problems_solved || 0) / 450, 10),
    aptitude_score: profile.etest_p,
    communication_skills: { Beginner: 4, Intermediate: 7, Advanced: 9 }[profile.communication_level] || 7,
    ml_knowledge: 6,
    system_design: 5.5,
    internships: profile.workex === 'Yes' ? 1 : 0,
    projects_count: profile.project_count || 0,
    certifications: profile.certification_count || 0,
    hackathons: profile.hackathon_count || 0,
    open_source_contributions: profile.open_source_contributions || 0,
    extracurriculars: 0,
  }
  const response = await fetch(`${API_BASE}/predict`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) throw new Error('Prediction request failed')
  const data = await response.json()
  return {
    readiness: { score: Math.round(data.placement_probability * 100), level: data.confidence },
    prediction: data.will_be_placed ? 'Placed' : 'Not placed',
    probability: data.placement_probability,
    suggestions: (data.recommendations || []).map((reason, index) => ({ title: `Recommendation ${index + 1}`, reason: reason.replace(/<[^>]+>/g, '') })),
    disclaimer: 'This is an estimate from the PlacementIQ model, not a hiring decision.',
  }
}

export async function extractDocument(file) {
  throw new Error('Document extraction is not supported by the backend')
}

export async function login(email, password) {
  const response = await fetch(`${API_BASE}/auth/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) })
  if (!response.ok) throw new Error('Invalid email or password')
  const data = await response.json()
  localStorage.setItem(tokenKey, data.token)
  localStorage.setItem(userKey, JSON.stringify(data.user))
  return data.user
}

export function logout() { localStorage.removeItem(tokenKey); localStorage.removeItem(userKey) }
export function getToken() { return localStorage.getItem(tokenKey) }
export function getUser() { try { return JSON.parse(localStorage.getItem(userKey) || 'null') } catch { return null } }

export async function getDashboardSummary() {
  const response = await fetch(`${API_BASE}/dashboard/summary`, { headers: { Authorization: `Bearer ${getToken()}` } })
  if (!response.ok) throw new Error('Dashboard unavailable')
  return response.json()
}

export async function adminLogin(email, password) {
  const response = await fetch(`${API_BASE}/auth/admin/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) })
  if (!response.ok) throw new Error('Invalid admin email or password')
  const data = await response.json()
  localStorage.setItem(tokenKey, data.token)
  localStorage.setItem(userKey, JSON.stringify(data.user))
  return data.user
}

export async function getAdminInsights() {
  const response = await fetch(`${API_BASE}/admin/insights`, { headers: { Authorization: `Bearer ${getToken()}` } })
  if (!response.ok) throw new Error('Admin insights unavailable')
  return response.json()
}

export async function uploadAdminCsv(file) {
  const form = new FormData()
  form.append('file', file)
  const response = await fetch(`${API_BASE}/batch`, { method: 'POST', headers: { Authorization: `Bearer ${getToken()}` }, body: form })
  if (!response.ok) throw new Error('CSV processing failed')
  return response.json()
}

const API_BASE = 'http://localhost:8000'

// Stands in for having logged in -- these match the fake tokens in auth.py.
// A real app would receive one of these from a login response, or never see it
// at all if the session lived in an httpOnly cookie.
export const DEMO_USERS = [
  { token: 'token-alice', label: 'alice — acme' },
  { token: 'token-bob', label: 'bob — acme' },
  { token: 'token-carol', label: 'carol — globex' },
]

export async function apiFetch(path, token) {
  const res = await fetch(`${API_BASE}${path}`, {
    // the credential rides on every request; the server derives the org from
    // it, which is why no request here mentions an org at all
    headers: { Authorization: `Bearer ${token}` },
  })

  // fetch only rejects on network failure -- a 401 or 500 still resolves,
  // so the status has to be checked by hand
  if (!res.ok) {
    throw new Error(`GET ${path} failed: ${res.status} ${res.statusText}`)
  }

  return res.json()
}

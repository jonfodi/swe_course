import { useState } from 'react'
import { apiFetch } from '../api'

async function getFailedAttempts(n, windowHours, token) {
  // n and window_hours stay query params -- they're genuine inputs the caller
  // gets to choose. the org isn't here, because identity is not an input
  const params = new URLSearchParams({ n, window_hours: windowHours })

  // this endpoint has no response_model yet, so it returns [["1.2.3.4", 6], ...]
  // -- destructure the positional pairs into objects at the boundary
  const data = await apiFetch(`/api/failed-attempts?${params}`, token)
  return data.map(([srcIp, count]) => ({ srcIp, count }))
}

export default function FailedAttemptsModal({ token }) {
  const [n, setN] = useState('1')
  const [windowHours, setWindowHours] = useState('8')
  const [status, setStatus] = useState('idle')          // idle | pending
  const [error, setError] = useState(null)
  const [failedAttempts, setFailedAttempts] = useState(null)  // null = no query run yet

  async function handleSubmit() {
    setStatus('pending')
    setError(null)
    try {
      setFailedAttempts(await getFailedAttempts(Number(n), Number(windowHours), token))
    } catch (e) {
      setError(e.message)
    } finally {
      setStatus('idle')
    }
  }

  return (
    <div className="failed-attempts">
      <label>
        More than
        <input value={n} onChange={(e) => setN(e.target.value)} />
        failures
      </label>

      <label>
        in the last
        <input value={windowHours} onChange={(e) => setWindowHours(e.target.value)} />
        hours
      </label>

      <button onClick={handleSubmit} disabled={status === 'pending'}>
        Run
      </button>

      {status === 'pending' && <p>Processing…</p>}
      {error && <p className="fail">{error}</p>}

      {failedAttempts === null ? (
        <p>Set a threshold and run a query.</p>
      ) : failedAttempts.length === 0 ? (
        <p>No IPs above that threshold in that window.</p>
      ) : (
        <table>
          <thead>
            <tr><th>Source IP</th><th>Failures</th></tr>
          </thead>
          <tbody>
            {failedAttempts.map((row) => (
              <tr key={row.srcIp}>
                <td className="mono">{row.srcIp}</td>
                <td>{row.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
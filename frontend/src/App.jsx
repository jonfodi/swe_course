import { useEffect, useState } from 'react'
import './App.css'
import FailedAttempts from './components/FailedAttempts'
import { apiFetch, DEMO_USERS } from './api'

async function fetchAuthLogs(token) {
  const data = await apiFetch('/api/auth-logs', token)

  // JSON has no date type, so timestamp arrives as a string. converting it
  // here -- the one place data enters the app -- means nothing downstream
  // has to remember what the wire format was.
  return data.map((log) => ({ ...log, timestamp: new Date(log.timestamp) }))
}

export default function CyberDashboard() {
  // who we're pretending to be. switching this is the whole demo: the requests
  // are identical apart from the header, and the server serves different data.
  const [token, setToken] = useState(DEMO_USERS[0].token)

  // null = not loaded yet, [] = loaded and genuinely empty
  const [authLogs, setAuthLogs] = useState(null)
  const [error, setError] = useState(null)

  // whether the modal is open is the page's business -- the modal itself
  // can't own the state that decides whether it exists
  const [showFailedAttempts, setShowFailedAttempts] = useState(false)

  useEffect(() => {
    // clear first, or the previous user's rows stay on screen during the
    // refetch -- which would look exactly like the leak we're guarding against
    setAuthLogs(null)
    setError(null)

    let stale = false
    fetchAuthLogs(token)
      .then((logs) => !stale && setAuthLogs(logs))
      .catch((e) => !stale && setError(e))

    // if the user switches again mid-flight, the older response must not win
    return () => { stale = true }
  }, [token])

  // derived, not stored -- can't get out of sync with the two above
  const loading = authLogs === null && error === null

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Cyber</h1>
        <div className="header-actions">
          <select
            className="ghost"
            value={token}
            onChange={(e) => setToken(e.target.value)}
          >
            {DEMO_USERS.map((u) => (
              <option key={u.token} value={u.token}>{u.label}</option>
            ))}
          </select>
          <button className="ghost" onClick={() => setShowFailedAttempts(true)}>
            Failed attempts
          </button>
        </div>
      </header>

      {showFailedAttempts && (
        <div className="modal-backdrop" onClick={() => setShowFailedAttempts(false)}>
          {/* without stopPropagation this click bubbles to the backdrop and closes it */}
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setShowFailedAttempts(false)}>
              ×
            </button>
            <h2>Failed attempts</h2>
            {/* keyed on token so switching users resets the modal's results
                rather than leaving the previous org's rows sitting there */}
            <FailedAttempts key={token} token={token} />
          </div>
        </div>
      )}

      {/* the auth-logs guards live inside this section now, so a slow or failed
          fetch here no longer blanks the whole page */}
      <section className="auth-logs">
        <h2>
          Auth logs
          {authLogs && <span className="count">{authLogs.length}</span>}
        </h2>

        {loading && <p>Loading auth logs…</p>}
        {error && <p className="fail">Could not load auth logs: {error.message}</p>}
        {authLogs?.length === 0 && <p>No auth logs.</p>}

        {authLogs?.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Source IP</th>
                <th>Username</th>
                <th>Result</th>
              </tr>
            </thead>
            <tbody>
              {authLogs.map((log, i) => (
                <tr key={i}>
                  {/* formatting happens here, at render -- the Date stays a Date in state */}
                  <td>{log.timestamp.toLocaleTimeString()}</td>
                  <td className="mono">{log.src_ip}</td>
                  <td>{log.username}</td>
                  <td className={log.success ? 'ok' : 'fail'}>
                    {log.success ? 'success' : 'failed'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  )
}

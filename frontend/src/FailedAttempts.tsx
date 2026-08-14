import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getFailedAttempts } from './api';

// SERVER-SIDE params: the controls are part of the queryKey, so changing
// them is a different cache entry and therefore a new request.
export function FailedAttempts() {
  const [n, setN] = useState(1);
  const [windowHours, setWindowHours] = useState(8);

  const { data, status } = useQuery({
    queryKey: ['failedAttempts', n, windowHours],
    queryFn: () => getFailedAttempts(n, windowHours),
  });

  return (
    <section>
      <h2>Failed attempts</h2>

      <label>
        more than
        <input
          type="number"
          value={n}
          onChange={e => setN(Number(e.target.value))}
        />
        attempts
      </label>

      <label>
        in the last
        <input
          type="number"
          value={windowHours}
          onChange={e => setWindowHours(Number(e.target.value))}
        />
        hours
      </label>

      {status === 'pending' && <p>Loading…</p>}
      {status === 'error' && <p>Failed to load</p>}
      {status === 'success' && (
        <ul>
          {data.map(([ip, count]) => (
            <li key={ip}>{ip} — {count}</li>
          ))}
        </ul>
      )}
    </section>
  );
}

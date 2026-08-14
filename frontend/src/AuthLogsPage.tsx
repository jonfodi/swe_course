import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getAuthLogs } from './api';

export function AuthLogsPage() {
  const [srcIp, setSrcIp] = useState('');                  // client state

  const { data, status } = useQuery({
    queryKey: ['authLogs'],                                // no srcIp -> one entry, one fetch
    queryFn: getAuthLogs,
  });

  const rows = (data ?? []).filter(l => l.src_ip.includes(srcIp));   // derived, never stored

  return (
    <>
      <h1>Auth logs</h1>

      <input
        value={srcIp}
        onChange={e => setSrcIp(e.target.value)}
        placeholder="Filter by source IP"
      />

      {status === 'pending' && <p>Loading…</p>}
      {status === 'error' && <p>Failed to load</p>}
      {status === 'success' && (
        <>
          <p>{rows.length} of {data.length}</p>
          <ul>
            {rows.map(l => (
              <li key={`${l.timestamp}-${l.src_ip}-${l.username}`}>
                {l.timestamp} · {l.src_ip} · {l.username} · {l.success ? 'ok' : 'FAIL'}
              </li>
            ))}
          </ul>
        </>
      )}
    </>
  );
}

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getAuthLogs } from './api';

// CLIENT-SIDE filter: srcIp is NOT in the queryKey, so typing never fetches.
// One cache entry, one request, filtering happens over data already in memory.
export function AuthLogs() {
  const [srcIp, setSrcIp] = useState('');

  const { data, status } = useQuery({
    queryKey: ['authLogs'],
    queryFn: getAuthLogs,
  });

  const rows = (data ?? []).filter(l => l.src_ip.includes(srcIp)); // derived

  return (
    <section>
      <h2>Auth logs</h2>

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
    </section>
  );
}

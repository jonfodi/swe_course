import { useQuery } from '@tanstack/react-query';
import { getMaliciousConnections } from './api';

// No client state at all. Nothing here can change what is asked for.
export function MaliciousConnections() {
  const { data, status } = useQuery({
    queryKey: ['maliciousConnections'],
    queryFn: getMaliciousConnections,
  });

  return (
    <section>
      <h2>Malicious connections</h2>

      {status === 'pending' && <p>Loading…</p>}
      {status === 'error' && <p>Failed to load</p>}
      {status === 'success' && (
        <ul>
          {data.map(([host, ip]) => (
            <li key={`${host}-${ip}`}>{host} → {ip}</li>
          ))}
        </ul>
      )}
    </section>
  );
}

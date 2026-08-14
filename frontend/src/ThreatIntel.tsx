// import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getThreatIntel } from './api';
import type { ThreatIntel } from './api';

// SERVER-SIDE params: the controls are part of the queryKey, so changing
// them is a different cache entry and therefore a new request.
export function ThreatIntel() {
//   const [threats, setThreats] = useState('')
  

  const { data, status } = useQuery({
    queryKey: ['threatIntel'],
    queryFn: () => getThreatIntel(),
  });

  return (
    <section>
      <h2>Threat Intel</h2>

      {status === 'pending' && <p>Loading…</p>}
      {status === 'error' && <p>Failed to load</p>}
      {status === 'success' && (
        <ul>
          {data.map(([ip]) => (
            <li key={ip}>{ip}</li>
          ))}
        </ul>
      )}
    </section>
  );
}

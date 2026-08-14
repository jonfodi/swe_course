import { useState } from 'react';
import type { FormEvent } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getThreatIntel, updateThreatIntel } from './api';

// READ is declarative -- useQuery runs every render and answers from the cache.
// WRITE is imperative -- useMutation does nothing until you call mutate().
export function ThreatIntel() {
  const [draft, setDraft] = useState('');   // client state: a DRAFT of server state
  const qc = useQueryClient();

  const { data, status } = useQuery({
    queryKey: ['threatIntel'],
    queryFn: getThreatIntel,
  });

  const update = useMutation({
    mutationFn: updateThreatIntel,
    onSuccess: (updated) => {
      // we KNOW the new value -- write it straight in, no refetch
      qc.setQueryData(['threatIntel'], updated);
      // this changed too, but we don't know what to -- mark stale, go ask again
      qc.invalidateQueries({ queryKey: ['maliciousConnections'] });
      // authLogs and failedAttempts are untouched by this write, so we leave them
    },
  });

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const ips = draft.split('\n').map(s => s.trim()).filter(Boolean);
    update.mutate(ips);
  }

  return (
    <section>
      <h2>Threat Intel</h2>

      {status === 'pending' && <p>Loading…</p>}
      {status === 'error' && <p>Failed to load</p>}
      {status === 'success' && (
        <ul>
          {data.map(threat => <li key={threat}>{threat}</li>)}
        </ul>
      )}

      <form onSubmit={handleSubmit}>
        <textarea
          value={draft}
          onChange={e => setDraft(e.target.value)}
          placeholder={'One IP per line.\nReplaces the entire set.'}
          rows={5}
        />
        <button type="submit" disabled={update.isPending}>
          {update.isPending ? 'Saving…' : 'Replace threat intel'}
        </button>
        {update.isError && <p>Update failed</p>}
      </form>
    </section>
  );
}

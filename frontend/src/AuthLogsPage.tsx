import { useQuery } from '@tanstack/react-query';
import { getAuthLogs } from './api';

export function AuthLogsPage() {
  const { data, status } = useQuery({
    queryKey: ['authLogs'],
    queryFn: getAuthLogs,
  });

  if (status === 'pending') return <p>Loading…</p>;
  if (status === 'error')   return <p>Failed to load</p>;

  return <ul>{data.map(l => <li key={l.id}>{l.event}</li>)}</ul>;
}
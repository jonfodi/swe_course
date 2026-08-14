const BASE = 'http://localhost:8000/api';

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

export interface AuthLogEntry {
  timestamp: string;
  src_ip: string;
  username: string;
  success: boolean;
}



export type FailedAttempt = [src_ip: string, count: number];
export type MaliciousConnection = [host: string, ip: string];

export type ThreatIntel = string;

export const getAuthLogs = () => get<AuthLogEntry[]>('/auth-logs');

export const getThreatIntel = () => get<ThreatIntel[]>('/threat_intel');

export const getMaliciousConnections = () =>
  get<MaliciousConnection[]>('/malicious-connections');

export const getFailedAttempts = (n: number, windowHours: number) =>
  get<FailedAttempt[]>(`/failed-attempts?n=${n}&window_hours=${windowHours}`);

// replaces the whole set; responds with the new state
export const updateThreatIntel = (ips: ThreatIntel[]) =>
  post<ThreatIntel[]>('/latest_threats', ips);

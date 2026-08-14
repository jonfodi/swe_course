export interface AuthLogEntry {
  timestamp: string;
  src_ip: string;
  username: string;
  success: boolean;
}

export async function getAuthLogs(): Promise<AuthLogEntry[]> {
  const res = await fetch('http://localhost:8000/api/auth-logs');
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}
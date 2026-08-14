export interface AuthLogEntry {
  id: string | number;
  event: string;
}

export async function getAuthLogs(): Promise<AuthLogEntry[]> {
    const res = await fetch('http://localhost:8000/api/auth-logs');
    if (!res.ok) throw new Error(res.statusText);
    return res.json();
  }
import { MaliciousConnections } from './MaliciousConnections';
import { FailedAttempts } from './FailedAttempts';
import { AuthLogs } from './AuthLogs';
import { ThreatIntel } from './ThreatIntel';

// Holds no state. Fetches nothing. Pure layout -- every panel gets its own
// data straight from the cache, so nothing is passed down.
export function Dashboard() {
  return (
    <>
      <h1>Cyber</h1>
      <MaliciousConnections />
      <FailedAttempts />
      <AuthLogs />
      <ThreatIntel />
    </>
  );
}

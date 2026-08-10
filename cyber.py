from bisect import bisect_left
from collections import defaultdict
from datetime import datetime, timedelta
from typing import NamedTuple


class AuthLog(NamedTuple):
    """One authentication attempt.

    Still a tuple -- indexable, sortable, works with bisect -- but the fields
    have names, so nothing downstream has to remember that index 3 is success.
    """
    timestamp: datetime
    src_ip: str
    username: str
    success: bool


class Cyber():
    """The indexes over one org's logs.

    One instance holds one org's data and nothing else, which is what lets the
    query methods stay unscoped -- there is no other org's data in here to
    accidentally return.
    """

    def __init__(self, auth_logs, connection_logs, threat_intel):
        self.auth_logs = [] # [ AuthLog ]
        self.connection_logs = [] # [ (timestamp, src_host, dst_ip, dst_port, bytes_sent)) ], sorted by timestamp 
        self.threat_intel = threat_intel # set of malicious IPs
        self.failed_ip_attempts = [] # [ (timestamp, src_ip) ]
        self.malicious_connections = set() # [ (src_ip, malicious_dest_ip) 
        self.threat_intel_refresh_interval = timedelta(hours=1)
        self.new_malicious_connections = set() # [ (src_ip, malicious_dest_ip) ]
        self.old_malicious_connections = set() # [ (src_ip, malicious_dest_ip) ]

        self.ingest_auth_logs(auth_logs)
        self.ingest_conn_logs(connection_logs)

    def ingest_auth_logs(self, auth_logs):
        for auth_log in auth_logs:
            self.record_auth_log(auth_log)

    def record_auth_log(self, auth_log):
        # normalise raw tuples at the boundary, so everything past this point
        # is an AuthLog and can use field names
        log = AuthLog(*auth_log)
        self.auth_logs.append(log)
        if not log.success:
            self.failed_ip_attempts.append((log.timestamp, log.src_ip))

    def ingest_conn_logs(self, connection_logs):
        for log in connection_logs:
            self.record_conn_log(log)

    def record_conn_log(self, conn_log):
        self.connection_logs.append(conn_log)
        if conn_log[2] in self.threat_intel:
            self.malicious_connections.add((conn_log[1], conn_log[2]))

    def failed_attempts_in_window(self, N, now, window):
        cutoff = now - window # 12:00 PM
        failed_logins = defaultdict(int) # src_ip: count
        res = []

        start = bisect_left(self.failed_ip_attempts, cutoff, key=lambda f: f[0])
        
        for ts, src_ip in self.failed_ip_attempts[start:]:
            failed_logins[src_ip] += 1
       
        for src_ip, count in failed_logins.items():
            if count > N:
                res.append((src_ip, count))
        
        return sorted(res, key=lambda x: (-x[1], x[0]))

    def malicious_ip_connections(self):
        # dont return the internal strucutre
        # return self.malicious_connections

        # return a copy 
        return set(self.malicious_connections)

    def get_auth_logs(self):
        return list(self.auth_logs)

    def ingest_latest_threat_intel(self, latest_threat_intel):
        self.threat_intel = latest_threat_intel
        self.refresh_threat_intel(latest_threat_intel)

    def refresh_threat_intel(self, latest_threat_intel: set) -> bool:
        self.new_malicious_connections.clear()
        self.old_malicious_connections.clear()
    
        
        # this removes all the old threats. we also need to add the new ones for malicious connections to be accurate
        for conn in self.malicious_connections:
            src_ip, curr_malicious_host = conn
            if curr_malicious_host not in latest_threat_intel:
                self.old_malicious_connections.add((src_ip, curr_malicious_host))

        self.malicious_connections.difference_update(self.old_malicious_connections)

            
        # add any connections with a new malicious IP to malicious connections
        # we have a refresh interval of 1 hour so we should bisect the connection logs on that cutoff
        now = datetime(2024, 1, 1, 17, 0)  # sample data's connection logs top out at 16:59
        cutoff = now - self.threat_intel_refresh_interval  # e.g. 17:00 - 1hr = 16:00
        # bisect_left, not bisect_right: entries == cutoff must stay in the window
        start = bisect_left(self.connection_logs, cutoff, key=lambda f: f[0])
        

        for log in self.connection_logs[start:]:
            timestamp, src_host, dst_ip, dst_port, bytes_sent = log
            if dst_ip in latest_threat_intel: # technically dont need new threats cause if the IP is in the latest threat intel we want it but this saves the write for existing threats that would block anyway cause of the set
                self.malicious_connections.add((src_host, dst_ip))
                self.new_malicious_connections.add((src_host, dst_ip))



    def get_latest_threat_report(self) -> tuple[set, set]:
        return self.new_malicious_connections, self.old_malicious_connections
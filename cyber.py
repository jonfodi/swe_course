from bisect import bisect_left
from collections import defaultdict
from datetime import datetime
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
        self.connection_logs = [] # [ (timestamp, src_host, dst_ip, dst_port, bytes_sent)) ]
        self.threat_intel = threat_intel # set of malicious IPs
        self.failed_ip_attempts = [] # [ (timestamp, src_ip) ]
        self.malicious_connections = set() # [ (src_ip, malicious_dest_ip) ]

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
    
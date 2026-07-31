from bisect import bisect_left
from collections import defaultdict


class Cyber():
    def __init__(self, auth_logs, connection_logs, threat_intel):
        self.auth_logs = [] # [ (timestamp, src_ip, username, success: bool) ]
        self.connection_logs = [] # [ (timestamp, src_host, dst_ip, dst_port, bytes_sent)) ]
        self.threat_intel = threat_intel # set of malicious IPs
        self.ip_attempts = defaultdict(list) # { src_ip: [timestamp] }
        self.malicious_connections = set() # [ (src_ip, malicious_dest_ip) ]

        self.ingest_auth_logs(auth_logs)
        self.ingest_conn_logs(connection_logs)


    # replay the seed logs through the same path a live log takes, so the
    # index is built in exactly one place
    def ingest_auth_logs(self, auth_logs):
        for auth_log in auth_logs:
            self.record_auth_log(auth_log)

    def record_auth_log(self, auth_log):
        self.auth_logs.append(auth_log)
        if auth_log[3] == False:
            self.ip_attempts[auth_log[1]].append(auth_log[0])

    def ingest_conn_logs(self, connection_logs):
        for log in connection_logs:
            self.record_conn_log(log)

    def record_conn_log(self, conn_log):
        self.connection_logs.append(conn_log)
        if conn_log[2] in self.threat_intel:
            self.malicious_connections.add((conn_log[1], conn_log[2]))



    # question 1: provide every src_ip with over failed_attempts failed login attempts in a given time window 
    # auth log: (timestamp, src_ip, username, success: bool)


    # optimizations 
    # bisecting - right now were always looping through the whole list to create IP attempts 
    # we could sort the list and then remove all logs not in the window 
    # cost: time complexity of the sort 
    # gain: less than N iterations on auth logs
    # tiebreaker: size of auth logs (as it gets bigger, the gain outweighs the cost because else we'd be looping through the huge N)
    def failed_attempts_in_window(self, N, now, window):
        cutoff = now - window # 12:00 PM
        res = []

        # dict keys are unique which means we dont need to make res a set 
        for src_ip, ts in self.ip_attempts.items():
            failed_attempts_in_window = len(ts) - bisect_left(ts, cutoff)
            if failed_attempts_in_window >= N:
                res.append((src_ip, failed_attempts_in_window))

        # tiebreak on src_ip so the ranking is deterministic -- without it the order
        # of equal counts falls out of dict insertion order, i.e. out of log order
        res.sort(key=lambda x: (-x[1], x[0]))
        return res

    
    def malicious_ip_connections(self):
        res = defaultdict(list) # src_ip: [malicious_ip]
         
        for malicious_conn in self.malicious_connections:
            res[malicious_conn[0]].append(malicious_conn[1])
        
        return res



from bisect import bisect_left
from collections import defaultdict
from datetime import datetime, timedelta
from typing import NamedTuple
from heapq import heappush, heappop


class AuthLog(NamedTuple):
    timestamp: datetime
    src_ip: str
    username: str
    success: bool


class Cyber():
    def __init__(self, auth_logs, connection_logs, threat_intel):
        self.auth_logs = [] # [ AuthLog ]
        self.connection_logs = [] # [ (timestamp, src_host, dst_ip, dst_port, bytes_sent)) ], sorted by timestamp 
        self.threat_intel = threat_intel # set of malicious IPs
        self.failed_ip_attempts = [] # [ (timestamp, src_ip) ]
        self.malicious_connections = set() # [ (src_ip, malicious_dest_ip) 
        self.threat_intel_refresh_interval = timedelta(hours=1)
        self.new_malicious_connections = set() # [ (src_ip, malicious_dest_ip) ]
        self.old_malicious_connections = set() # [ (src_ip, malicious_dest_ip) ]
        self.new_threats = set() # latest_threats - curr_threats
        # self.connection_timestamps = defaultdict(list) # dest_ip : [ (src_host, timestamp) ]
        self.connection_timestamps = defaultdict(lambda: defaultdict(list)) # dest_ip : { src_host : [ timestamp ] }
        self.source_connections = defaultdict(lambda: defaultdict(list)) # src_host : { dest_ip : [ timestamp ] }

        self.ingest_auth_logs(auth_logs)
        self.ingest_conn_logs(connection_logs)

        self.cache = defaultdict(list)

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
        timestamp, src_host, dst_ip, dst_port, bytes_sent = conn_log
        if dst_ip in self.threat_intel:
            self.malicious_connections.add((src_host, dst_ip))
        self.connection_timestamps[dst_ip][src_host].append(timestamp)
        self.source_connections[src_host][dst_ip].append(timestamp)

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
        # dont return the internal structure -- return a copy
        return list(self.auth_logs)

    def ingest_latest_threat_intel(self, latest_threat_intel):
        self.new_threats = latest_threat_intel - self.threat_intel
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

            
        # # add any connections with a new malicious IP to malicious connections
        # # we have a refresh interval of 1 hour so we should bisect the connection logs on that cutoff
        # now = datetime(2024, 1, 1, 17, 0)  # sample data's connection logs top out at 16:59
        # cutoff = now - self.threat_intel_refresh_interval  # e.g. 17:00 - 1hr = 16:00
        # # bisect_left, not bisect_right: entries == cutoff must stay in the window
        # start = bisect_left(self.connection_logs, cutoff, key=lambda f: f[0])
        
        
        # for log in self.connection_logs[start:]:
        #     timestamp, src_host, dst_ip, dst_port, bytes_sent = log
        #     print(dst_ip)
        #     if dst_ip == "142.250.80.46":
        #         print("hey")
        #         if dst_ip in self.new_threats:
        #             print('match')
        #     if dst_ip in self.new_threats: 
        #         self.malicious_connections.add((src_host, dst_ip))
        #         self.new_malicious_connections.add((src_host, dst_ip))
        
        for ip in self.new_threats:
            if ip in self.connection_timestamps:
                ip_conn_dict = self.connection_timestamps[ip] # { src_host: [timestamps] }
                # for every src in this list, we want to add (src_host, dst_ip) 
                for src_host in ip_conn_dict:
                    self.new_malicious_connections.add((src_host, ip))
                    self.malicious_connections.add((src_host, ip))

    def get_latest_threat_report(self) -> tuple[set, set]:
        return (set(self.new_malicious_connections), set(self.old_malicious_connections))

    def top_k_connections(self, k) -> list:
        heap = []

        for dest_ip in self.connection_timestamps:
            for src_host in self.connection_timestamps[dest_ip]:
                heappush(heap, (len(self.connection_timestamps[dest_ip][src_host]), src_host, dest_ip))
                if len(heap) > k:
                    heappop(heap)
        
        return sorted(heap, reverse=True)
    
    def blast_radius(self, compromised_host: str, max_hops: int) -> list[tuple[str, int]]: 
        first_result = [] # [ (host, hops) ]
        second_result = []
        third_result = []

        dest_ip_dict = self.source_connections[compromised_host]
        first_result = [(dest_ip, 1) for dest_ip in dest_ip_dict]

        for res in first_result:
            src_host, hops = res
            ip_dict = self.source_connections[src_host]
            for dest_ip in ip_dict:
                if dest_ip != compromised_host:
                    second_result.append((dest_ip, 2))

      
        for res in second_result:
            src_host, hops = res
            ip_dict = self.source_connections[src_host]
            for dest_ip in ip_dict:
                if dest_ip != compromised_host:
                    third_result.append((dest_ip, 3))

        combined = first_result + second_result + third_result

        # dedup src hosts
        seen = {}
        for host, hops in combined:
            if host not in seen:
                seen[host] = hops

        print(list(seen.items()))


    def get_threat_intel(self):
        return set(self.threat_intel)
    

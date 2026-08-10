from collections import defaultdict
from datetime import datetime, timedelta
from cyber import Cyber
from sample_data import AUTH_LOGS, CONNECTION_LOGS, THREAT_INTEL, LATEST_THREAT_INTEL


def hey():
    # i think goal is to get a list of all the ts for a given src, dst 
    # then we can analyze the interval when that list is sorted 

    # there are likely many connections that are fine 
    # we dont want to loop through an entire dict and the list of timestamps 
    # so we filter out conn pairs that dont have a min number of connections
    # 
    conn_count = defaultdict(list) # (src_host, dest_ip): count 
    for log in connection_logs:
        ts, src_host, dst_ip, dst_port, bytes_sent = log
        conn_count[(src_host, dst_ip)] += 1
    
    min_connections = 10
    survivors = {pair for pair, c in conn_count.items() if c >= MIN_CONNECTIONS}

    potential_malware_ts = defaultdict(list) # (src_host, dest_ip): [ts] 

    for log in connection_logs:
        ts, src_host, dst_ip, dst_port, bytes_sent = log
        pair = (src_host, dst_ip)
        if pair in survivors:
            potential_malware_ts[pair].append(ts)
    


    

cyb = Cyber(AUTH_LOGS, CONNECTION_LOGS, THREAT_INTEL)

NOW = datetime(2024, 1, 1, 17, 0)
# window = datetime(2024, 1, 1, 16, 30) # 30 min window
# # window = datetime(2024, 1, 1, 16, 0) # 1 hour window
window = timedelta(hours=8) # 8 hour window


# failed_attempts_in_window = cyb.failed_attempts_in_window(1, NOW, window)
# print(failed_attempts_in_window)

# malicious_ip_connections = cyb.malicious_ip_connections()
# for src_host, dst_ip in malicious_ip_connections:
#     print(f"{src_host} -> {dst_ip}")

cyb.ingest_latest_threat_intel(LATEST_THREAT_INTEL)


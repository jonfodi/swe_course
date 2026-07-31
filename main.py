from collections import defaultdict 
from datetime import datetime, timedelta
from bisect import bisect_right



# question 1: provide every src_ip with over failed_attempts failed login attempts in a given time window 
# auth log: (timestamp, src_ip, username, success: bool)


# optimizations 
# bisecting - right now were always looping through the whole list to create IP attempts 
# we could sort the list and then remove all logs not in the window 
# cost: time complexity of the sort 
# gain: less than N iterations on auth logs
# tiebreaker: size of auth logs (as it gets bigger, the gain outweighs the cost because else we'd be looping through the huge N)
def failed_attempts_in_window(auth_logs, failed_attempts, now, window):
    cutoff = now - window                    # 12:00 PM
    ip_attempts = defaultdict(int) # src_ip: num_attempts 
    res = []
    
    start = bisect_left(auth_logs, cutoff, key=lambda log: log[0])

    for log in auth_logs[start:]:
        timestamp, src_ip, username, success = log
        if success:
            continue
        ip_attempts[src_ip] += 1

    # dict keys are unique which means we dont need to make res a set 
    for src_ip, num_attempts in ip_attempts.items():
        if num_attempts >= failed_attempts:
            res.append((src_ip, num_attempts))

    # tiebreak on src_ip so the ranking is deterministic -- without it the order
    # of equal counts falls out of dict insertion order, i.e. out of log order
    res.sort(key=lambda x: (-x[1], x[0]))
    return res


# question 2: report all src_host that made a connection to a dest_ip in the threat_intel IP list in a given time window 
# threat_intel = set() -> unique list of malicious IPs 
# connection_log = (timestamp, src_host, dst_ip, dst_port, bytes_sent)
# input: window 
# output: [(src_host, dst_ip)] -> maybe a set?

# optimizations
# obv this loop is not ideal we can bisect it too
# but this feels pretty straightforward
# if we create teh data we need at write time we dont need to loop through all logs -> malicious_connections dict 
def malicious_ip_connections(connection_logs, threat_intel, now, window):
    cutoff = now - window
    res = set()

    # we can do this at write time eventually but leave it here now for simplicity / just to demonstrate
    malicious_connections = defaultdict(set) # malicious_ip : [timestamp, src_host] 

    for log in connection_logs:
        timestamp, src_host, dst_ip, dst_port, bytes_sent = log
        if dst_ip in threat_intel:
            malicious_connections[dst_ip].add((timestamp, src_host))


    for malicious_ip, conns in malicious_connections.items():
        for timestamp, src_host in conns:
            if timestamp <= cutoff:
                continue
            res.add((src_host, malicious_ip))
    
    return res

    # res = set()
    # cutoff = now - window

    # for log in connection_log:
    #     timestamp, src_host, dst_ip, dst_port, bytes_sent = log
    #     if timestamp <= cutoff:
    #         continue
    #     if dst_ip in threat_intel:
    #         res.add((src_host, dst_ip))
    # return res



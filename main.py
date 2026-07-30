from collections import defaultdict 
from datetime import datetime, timedelta


# question 1: provide every src_ip with over failed_attempts failed login attempts in a given time window 
# auth log: (timestamp, src_ip, username, success: bool)


# optimizations 
# bisecting - right now were always looping through the whole list to create IP attempts 
# we could sort the list and then remove all logs not in the window 
# cost: time complexity of the sort 
# gain: less than N iterations on auth logs
# tiebreaker: size of auth logs (as it gets bigger, the gain outweighs the cost because else we'd be looping through the huge N)
def failed_attempts_in_window(auth_logs,failed_attempts, now, window):
    cutoff = now - window                    # 12:00 PM
    ip_attempts = defaultdict(int) # src_ip: num_attempts 
    res = []

    for log in auth_logs:
        timestamp, src_ip, username, success = log
        if timestamp <= cutoff or success:
            continue
        ip_attempts[src_ip] += 1

    # dict keys are unique which means we dont need to make res a set 
    for src_ip, num_attempts in ip_attempts.items():
        if num_attempts >= failed_attempts:
            res.append((src_ip, num_attempts))

    res.sort(key=lambda x: x[1], reverse=True)
    return res


# question 2: report all src_host that made a connection to a dest_ip in the threat_intel IP list in a given time window 
# threat_intel = set() -> unique list of malicious IPs 
# connection_log = (timestamp, src_host, dst_ip, dst_port, bytes_sent)
# input: window 
# output: [(src_host, dst_ip)] -> maybe a set?

def malicious_ip_connections(connection_log, threat_intel, now, window):
    res = set()
    cutoff = now - window

    for log in connection_log:
        timestamp, src_host, dst_ip, dst_port, bytes_sent = log
        if timestamp <= cutoff:
            continue
        if dst_ip in threat_intel:
            res.add((src_host, dst_ip))
    return res





    





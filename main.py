from collections import defaultdict 
from datetime import datetime, timedelta


# question 1: provide every src_ip with over failed_attempts failed login attempts in a given time window 
# auth log: (timestamp, src_ip, username, success: bool)


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



# auth_logs = [
#     (datetime(2024, 1, 1, 8, 41),  "10.0.0.5",       "alice",         True),   # 8:41:00
#     (datetime(2024, 1, 1, 8, 44),  "10.0.0.5",       "alice",         True),   # 8:44:00
#     (datetime(2024, 1, 1, 9, 52),  "203.0.113.7",    "admin",         False),  # 9:52:00
#     (datetime(2024, 1, 1, 9, 53),  "203.0.113.7",    "root",          False),  # 9:53:00
#     (datetime(2024, 1, 1, 9, 55),  "203.0.113.7",    "svc_backup",    False),  # 9:55:00
#     (datetime(2024, 1, 1, 9, 56),  "203.0.113.7",    "jsmith",        False),  # 9:56:00
#     (datetime(2024, 1, 1, 9, 58),  "203.0.113.7",    "postgres",      False),  # 9:58:00
#     (datetime(2024, 1, 1, 10, 0),  "203.0.113.7",    "administrator", False),  # 10:00:00
#     (datetime(2024, 1, 1, 12, 24), "198.51.100.22",  "bwong",         False),  # 12:24:00
#     (datetime(2024, 1, 1, 12, 31), "198.51.100.22",  "bwong",         False),  # 12:31:00
#     (datetime(2024, 1, 1, 12, 42), "198.51.100.22",  "bwong",         False),  # 12:42:00
#     (datetime(2024, 1, 1, 12, 59), "198.51.100.22",  "bwong",         False),  # 12:59:00
#     (datetime(2024, 1, 1, 13, 13), "198.51.100.22",  "bwong",         True),   # 13:13:00
#     (datetime(2024, 1, 1, 15, 50), "192.0.2.15",     "ckim",          False),  # 15:50:00
#     (datetime(2024, 1, 1, 16, 2),  "192.0.2.15",     "ckim",          True),   # 16:02:00
#     (datetime(2024, 1, 1, 16, 25), "203.0.113.99",   "dpatel",        False),  # 16:25:00
#     (datetime(2024, 1, 1, 16, 30), "203.0.113.99",   "dpatel",        False),  # 16:30:00
#     (datetime(2024, 1, 1, 16, 40), "10.0.0.5",       "alice",         True),   # 16:40:00
#     (datetime(2024, 1, 1, 16, 51), "172.16.4.9",     "svc_deploy",    True),   # 16:51:00
#     (datetime(2024, 1, 1, 16, 53), "172.16.4.9",     "svc_deploy",    False),  # 16:53:00
# ]
# failed_attempts = 1
# now = datetime(2024, 1, 1, 17, 0, 0)     # 5:00 PM
# window = timedelta(minutes=300)          # last 5 hours

# res = failed_attempts_in_window(failed_attempts, now, window)
# for src_ip, num_attempts in res:
#     print(f"ip: {src_ip} has {num_attempts} failed attempts")


    





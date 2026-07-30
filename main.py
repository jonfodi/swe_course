# question 1: provide every src_ip with over N failed login attempts in a given time window 
# auth log: (timestamp, src_ip, username, success: bool)

# auth_logs = [] # list of auth log tuples 
cutoff = 100
now = 200
N = 3

auth_logs = [
    (  1, "10.0.0.5",       "alice",         True),
    (  4, "10.0.0.5",       "alice",         True),
    ( 72, "203.0.113.7",    "admin",         False),
    ( 73, "203.0.113.7",    "root",          False),
    ( 75, "203.0.113.7",    "svc_backup",    False),
    ( 76, "203.0.113.7",    "jsmith",        False),
    ( 78, "203.0.113.7",    "postgres",      False),
    ( 80, "203.0.113.7",    "administrator", False),
    (224, "198.51.100.22",  "bwong",         False),
    (231, "198.51.100.22",  "bwong",         False),
    (242, "198.51.100.22",  "bwong",         False),
    (259, "198.51.100.22",  "bwong",         False),
    (273, "198.51.100.22",  "bwong",         True),
    (430, "192.0.2.15",     "ckim",          False),
    (442, "192.0.2.15",     "ckim",          True),
    (465, "203.0.113.99",   "dpatel",        False),
    (470, "203.0.113.99",   "dpatel",        False),
    (480, "10.0.0.5",       "alice",         True),
    (491, "172.16.4.9",     "svc_deploy",    True),
    (493, "172.16.4.9",     "svc_deploy",    False),
]

ip_attempts = defaultdict(int) # src_ip: num_attempts 


for log in auth_logs:
    timestamp, src_ip, username, success = log
    if timestamp <= now - cutoff or success == True:
        pass
    ip_attempts[src_ip] += 1

res = []

# dict keys are unique which means we dont need to make res a set 
for src_ip, num_attempts in ip_attempts.items():
    if num_attempts > N:
        res.append((src_ip, num_attempts))

print(res.sorted(num_attempts))
    
    





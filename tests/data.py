"""Shared sample logs for the tests.

Plain module constants rather than pytest fixtures, so they can be referenced
inside @pytest.mark.parametrize tables (fixtures don't exist at collection time).
Frozen (tuples / frozenset) since every test shares one copy.
"""

from datetime import datetime

NOW = datetime(2024, 1, 1, 17, 0)

# (timestamp, src_ip, username, success)
AUTH_LOGS = (
    (datetime(2024, 1, 1,  8, 41), "10.0.0.5",      "alice",         True),
    (datetime(2024, 1, 1,  8, 44), "10.0.0.5",      "alice",         True),
    (datetime(2024, 1, 1,  9, 52), "203.0.113.7",   "admin",         False),
    (datetime(2024, 1, 1,  9, 53), "203.0.113.7",   "root",          False),
    (datetime(2024, 1, 1,  9, 55), "203.0.113.7",   "svc_backup",    False),
    (datetime(2024, 1, 1,  9, 56), "203.0.113.7",   "jsmith",        False),
    (datetime(2024, 1, 1,  9, 58), "203.0.113.7",   "postgres",      False),
    (datetime(2024, 1, 1, 10,  0), "203.0.113.7",   "administrator", False),
    (datetime(2024, 1, 1, 12, 24), "198.51.100.22", "bwong",         False),
    (datetime(2024, 1, 1, 12, 31), "198.51.100.22", "bwong",         False),
    (datetime(2024, 1, 1, 12, 42), "198.51.100.22", "bwong",         False),
    (datetime(2024, 1, 1, 12, 59), "198.51.100.22", "bwong",         False),
    (datetime(2024, 1, 1, 13, 13), "198.51.100.22", "bwong",         True),
    (datetime(2024, 1, 1, 15, 50), "192.0.2.15",    "ckim",          False),
    (datetime(2024, 1, 1, 16,  2), "192.0.2.15",    "ckim",          True),
    (datetime(2024, 1, 1, 16, 25), "203.0.113.99",  "dpatel",        False),
    (datetime(2024, 1, 1, 16, 30), "203.0.113.99",  "dpatel",        False),
    (datetime(2024, 1, 1, 16, 40), "10.0.0.5",      "alice",         True),
    (datetime(2024, 1, 1, 16, 51), "172.16.4.9",    "svc_deploy",    True),
    (datetime(2024, 1, 1, 16, 53), "172.16.4.9",    "svc_deploy",    False),
)

THREAT_INTEL = frozenset({
    "45.33.32.156",
    "185.220.101.44",
    "91.219.236.18",
    "194.5.249.157",
    "5.188.206.18",
    "103.224.182.253",
})

# (timestamp, src_host, dst_ip, dst_port, bytes_sent)
CONNECTION_LOG = (
    (datetime(2024, 1, 1,  8, 15), "wkstn_014",    "45.33.32.156",    443,    8214),
    (datetime(2024, 1, 1, 11, 59), "wkstn_014",    "185.220.101.44",  9001,    412),
    (datetime(2024, 1, 1, 12,  0), "wkstn_022",    "91.219.236.18",   443,    1180),
    (datetime(2024, 1, 1, 12, 30), "wkstn_088",    "45.33.32.156",    443,    4096),
    (datetime(2024, 1, 1, 12, 33), "wkstn_088",    "45.33.32.156",    443,    4096),
    (datetime(2024, 1, 1, 12, 35), "wkstn_088",    "45.33.32.156",    443,    2048),
    (datetime(2024, 1, 1, 13,  5), "wkstn_088",    "185.220.101.44",  9001,    877),
    (datetime(2024, 1, 1, 13, 40), "srv_db_03",    "10.0.0.200",      5432,  15300),
    (datetime(2024, 1, 1, 14,  0), "wkstn_101",    "142.250.80.46",   443,   62100),
    (datetime(2024, 1, 1, 14, 22), "wkstn_101",    "91.219.236.18",   8080,    633),
    (datetime(2024, 1, 1, 15, 10), "srv_web_01",   "194.5.249.157",   443, 2884109),
    (datetime(2024, 1, 1, 15, 11), "srv_web_01",   "194.5.249.157",   443, 4102773),
    (datetime(2024, 1, 1, 16,  0), "wkstn_045",    "5.188.206.18",    6667,    244),
    (datetime(2024, 1, 1, 16, 30), "wkstn_045",    "52.94.236.248",   443,   18900),
    (datetime(2024, 1, 1, 16, 45), "wkstn_088",    "103.224.182.253", 53,      301),
    (datetime(2024, 1, 1, 16, 59), "laptop_jfodi", "185.220.101.44",  9001,   1502),
)

"""Sample logs, now split per org.

This module plays the part of the store: `load_org_data(org_id)` is the seam
where a real database query would go. Everything above it -- the registry, the
dependencies, the handlers -- is written against that function, not against
these constants, so replacing it later is a local change.
"""

from datetime import datetime
from typing import NamedTuple


class UnknownOrg(KeyError):
    """No such org. Distinct from a KeyError raised by something else."""


# Shared reference data, not tenant data: a threat feed is the same for
# everyone. frozenset so one org's index can't mutate what the others read.
THREAT_INTEL = set({
    "45.33.32.156",
    "185.220.101.44",
    "91.219.236.18",
    "194.5.249.157",
    "5.188.206.18",
    "103.224.182.253",
})

# The next hourly refresh of the feed. Two IPs retracted as false positives,
# three added -- one of which nobody has ever talked to.
#
#   retracted:  45.33.32.156, 103.224.182.253
#   added:      142.250.80.46, 52.94.236.248, 77.83.36.9
#
# Hand-derived from CONNECTION_LOGS below -- this is what the report *should*
# say, independent of what the code currently does.
#
# acme, new_malicious_connections (connections that were already in history and
# only became malicious now):
#   ("wkstn_101", "142.250.80.46")     from 14:00
#   ("wkstn_045", "52.94.236.248")     from 16:30
#
# acme, old_malicious_connections (no longer malicious, must be dropped from
# malicious_connections):
#   ("wkstn_014", "45.33.32.156")      from 08:15
#   ("wkstn_088", "45.33.32.156")      from 12:30 / 12:33 / 12:35, one pair
#   ("wkstn_088", "103.224.182.253")   from 16:45
#
# 77.83.36.9 appears in no connection log, so it contributes nothing -- the
# normal case for most of a feed update.
#
# Note the two timestamps in the new set. Taking NOW as 17:00, the 16:30
# connection falls inside a one-hour lookback and the 14:00 one does not, so
# how far back the backfill reaches decides whether both pairs are reported.
#
# globex is the asymmetric case: additions only, nothing retracted.
#   new: ("gbx_srv_mail", "142.250.80.46")   from 14:50
#   old: (none -- globex never connected to either retracted IP)
LATEST_THREAT_INTEL = set({
    "185.220.101.44",
    "91.219.236.18",
    "194.5.249.157",
    "5.188.206.18",
    "142.250.80.46",
    "52.94.236.248",
    "77.83.36.9",
})

# ---- acme -------------------------------------------------------------------

# (timestamp, src_ip, username, success)
AUTH_LOGS = [
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
]

# (timestamp, src_host, dst_ip, dst_port, bytes_sent)
CONNECTION_LOGS = [
    (datetime(2024, 1, 1,  8, 15), "wkstn_014",    "45.33.32.156",    443,    8214),
    (datetime(2024, 1, 1,  9,  5), "srv_db_03",    "srv_legacy_02",   445,    3300),
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
    (datetime(2024, 1, 1, 15, 12), "srv_web_01",   "srv_db_03",       22,     1840),
    (datetime(2024, 1, 1, 15, 15), "srv_web_01",   "wkstn_101",       3389,   9600),
    (datetime(2024, 1, 1, 15, 20), "srv_db_03",    "srv_backup_01",   445,  520400),
    (datetime(2024, 1, 1, 15, 25), "wkstn_101",    "srv_db_03",       22,      760),
    (datetime(2024, 1, 1, 15, 35), "srv_backup_01","srv_vault_01",    443,    2100),
    (datetime(2024, 1, 1, 15, 40), "srv_backup_01","srv_web_01",      443,     980),
    (datetime(2024, 1, 1, 16,  0), "wkstn_045",    "5.188.206.18",    6667,    244),
    (datetime(2024, 1, 1, 16, 30), "wkstn_045",    "52.94.236.248",   443,   18900),
    (datetime(2024, 1, 1, 16, 45), "wkstn_088",    "103.224.182.253", 53,      301),
    (datetime(2024, 1, 1, 16, 59), "laptop_jfodi", "185.220.101.44",  9001,   1502),
]

# ---- globex -----------------------------------------------------------------

# Deliberately disjoint from acme -- different IPs, hosts and usernames -- so
# a leak across the tenant boundary is obvious on sight rather than subtle.
GLOBEX_AUTH_LOGS = [
    (datetime(2024, 1, 1,  9, 10), "10.9.0.12",     "mrivera",   True),
    (datetime(2024, 1, 1, 11,  5), "209.85.231.4",  "oracle",    False),
    (datetime(2024, 1, 1, 11,  7), "209.85.231.4",  "sysadmin",  False),
    (datetime(2024, 1, 1, 11,  9), "209.85.231.4",  "backup",    False),
    (datetime(2024, 1, 1, 14, 20), "198.18.7.31",   "tnguyen",   False),
    (datetime(2024, 1, 1, 14, 26), "198.18.7.31",   "tnguyen",   True),
    (datetime(2024, 1, 1, 16, 12), "10.9.0.12",     "mrivera",   True),
    (datetime(2024, 1, 1, 16, 44), "203.0.113.240", "kobrien",   False),
]

GLOBEX_CONNECTION_LOGS = [
    (datetime(2024, 1, 1,  9, 30), "gbx_wkstn_03", "91.219.236.18",  443,   2210),
    (datetime(2024, 1, 1, 13, 15), "gbx_wkstn_03", "91.219.236.18",  443,   1904),
    (datetime(2024, 1, 1, 14, 50), "gbx_srv_mail", "142.250.80.46",  443,  33150),
    (datetime(2024, 1, 1, 15, 40), "gbx_laptop_7", "5.188.206.18",   6667,    188),
    (datetime(2024, 1, 1, 16, 20), "gbx_srv_mail", "10.9.0.200",     5432,  74000),
]

# ---- the store ---------------------------------------------------------------


class OrgData(NamedTuple):
    auth_logs: list
    connection_logs: list
    threat_intel: frozenset


_ORGS = {
    "acme": OrgData(AUTH_LOGS, CONNECTION_LOGS, THREAT_INTEL),
    "globex": OrgData(GLOBEX_AUTH_LOGS, GLOBEX_CONNECTION_LOGS, THREAT_INTEL),
}


def load_org_data(org_id: str) -> OrgData:
    """Fetch one org's raw logs. The stand-in for `WHERE org_id = %s`."""
    try:
        return _ORGS[org_id]
    except KeyError:
        raise UnknownOrg(org_id) from None

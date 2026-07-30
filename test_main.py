from datetime import timedelta

import pytest

from data import AUTH_LOGS, CONNECTION_LOG, NOW, THREAT_INTEL
from main import build_index, failed_attempts_in_window, malicious_ip_connections

# NOW is 17:00, so each window names its own cutoff
DAY = timedelta(days=1)      # cutoff 2023-12-31 17:00 -- whole log
H5 = timedelta(hours=5)      # cutoff 12:00
H2 = timedelta(hours=2)      # cutoff 15:00
MIN30 = timedelta(minutes=30)  # cutoff 16:30
ZERO = timedelta(0)          # cutoff 17:00 -- nothing


# ---- question 1 -------------------------------------------------------------

@pytest.mark.parametrize(
    "logs, n, window, expected",
    [
        pytest.param(
            AUTH_LOGS, 1, DAY,
            [
                ("203.0.113.7", 6),
                ("198.51.100.22", 4),
                ("203.0.113.99", 2),
                ("172.16.4.9", 1),
                ("192.0.2.15", 1),
            ],
            id="whole_day_n1",
        ),
        pytest.param(
            AUTH_LOGS, 3, DAY,
            [("203.0.113.7", 6), ("198.51.100.22", 4)],
            id="whole_day_n3",
        ),
        # 198.51.100.22 has 4, so it drops out; only the spray survives
        pytest.param(AUTH_LOGS, 5, DAY, [("203.0.113.7", 6)], id="whole_day_n5"),
        # above every count
        pytest.param(AUTH_LOGS, 7, DAY, [], id="whole_day_n7"),
        pytest.param(
            AUTH_LOGS, 1, H5,
            [
                ("198.51.100.22", 4),
                ("203.0.113.99", 2),
                ("172.16.4.9", 1),
                ("192.0.2.15", 1),
            ],
            id="last_5h_n1",
        ),
        pytest.param(
            AUTH_LOGS, 2, H5,
            [("198.51.100.22", 4), ("203.0.113.99", 2)],
            id="last_5h_n2",
        ),
        # the 09:52-10:00 spray falls out entirely
        pytest.param(AUTH_LOGS, 3, H5, [("198.51.100.22", 4)], id="last_5h_n3"),
        # 203.0.113.99's second failure is AT 16:30, and `timestamp <= cutoff`
        # drops it, so only 172.16.4.9 at 16:53 is left
        pytest.param(AUTH_LOGS, 1, MIN30, [("172.16.4.9", 1)], id="last_30min_n1"),
        pytest.param(AUTH_LOGS, 3, MIN30, [], id="last_30min_n3"),
        pytest.param(AUTH_LOGS, 1, ZERO, [], id="zero_window"),
        pytest.param((), 1, DAY, [], id="empty_log"),
    ],
)
def test_failed_attempts_in_window(logs, n, window, expected):
    assert failed_attempts_in_window(logs, n, NOW, window) == expected


# ---- question 2 -------------------------------------------------------------

def detect(connection_log, threat_intel, now, window):
    """Write path then read path, the way a caller uses the pair."""
    return malicious_ip_connections(build_index(connection_log, threat_intel), now, window)


@pytest.mark.parametrize(
    "log, feed, window, expected",
    [
        pytest.param(
            CONNECTION_LOG, THREAT_INTEL, DAY,
            {
                ("wkstn-014",    "45.33.32.156"),
                ("wkstn-014",    "185.220.101.44"),
                ("wkstn-022",    "91.219.236.18"),
                ("wkstn-088",    "45.33.32.156"),
                ("wkstn-088",    "185.220.101.44"),
                ("wkstn-088",    "103.224.182.253"),
                ("wkstn-101",    "91.219.236.18"),
                ("srv-web-01",   "194.5.249.157"),
                ("wkstn-045",    "5.188.206.18"),
                ("laptop-jfodi", "185.220.101.44"),
            },
            id="whole_day",
        ),
        # drops 08:15, 11:59, and wkstn-022 sitting exactly on the 12:00 cutoff
        pytest.param(
            CONNECTION_LOG, THREAT_INTEL, H5,
            {
                ("wkstn-088",    "45.33.32.156"),
                ("wkstn-088",    "185.220.101.44"),
                ("wkstn-088",    "103.224.182.253"),
                ("wkstn-101",    "91.219.236.18"),
                ("srv-web-01",   "194.5.249.157"),
                ("wkstn-045",    "5.188.206.18"),
                ("laptop-jfodi", "185.220.101.44"),
            },
            id="last_5h",
        ),
        # wkstn-088's beaconing to 45.33.32.156 is now out of range
        pytest.param(
            CONNECTION_LOG, THREAT_INTEL, H2,
            {
                ("srv-web-01",   "194.5.249.157"),
                ("wkstn-045",    "5.188.206.18"),
                ("wkstn-088",    "103.224.182.253"),
                ("laptop-jfodi", "185.220.101.44"),
            },
            id="last_2h",
        ),
        # only the 16:45 and 16:59 rows survive
        pytest.param(
            CONNECTION_LOG, THREAT_INTEL, MIN30,
            {
                ("wkstn-088",    "103.224.182.253"),
                ("laptop-jfodi", "185.220.101.44"),
            },
            id="last_30min",
        ),
        pytest.param(CONNECTION_LOG, THREAT_INTEL, ZERO, set(), id="zero_window"),
        # feed refreshed down to a single IP -- two different hosts hit it
        pytest.param(
            CONNECTION_LOG, {"185.220.101.44"}, H5,
            {("wkstn-088", "185.220.101.44"), ("laptop-jfodi", "185.220.101.44")},
            id="one_ip_feed",
        ),
        pytest.param(CONNECTION_LOG, set(), H5, set(), id="empty_feed"),
        # IPs nobody talked to
        pytest.param(CONNECTION_LOG, {"1.2.3.4", "8.8.4.4"}, H5, set(), id="feed_with_no_hits"),
        pytest.param((), THREAT_INTEL, H5, set(), id="empty_log"),
    ],
)
def test_malicious_ip_connections(log, feed, window, expected):
    assert detect(log, feed, NOW, window) == expected

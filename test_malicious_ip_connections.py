from datetime import timedelta

import pytest

from main import malicious_ip_connections


# ---- vary the window, full threat feed ------------------------------------

@pytest.mark.parametrize(
    "window, expected",
    [
        pytest.param(
            timedelta(days=1),
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
        # cutoff 12:00 -- drops 08:15, 11:59, and wkstn-022 sitting exactly on 12:00
        pytest.param(
            timedelta(hours=5),
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
        # cutoff 15:00 -- wkstn-088's beaconing to 45.33.32.156 is now out of range
        pytest.param(
            timedelta(hours=2),
            {
                ("srv-web-01",   "194.5.249.157"),
                ("wkstn-045",    "5.188.206.18"),
                ("wkstn-088",    "103.224.182.253"),
                ("laptop-jfodi", "185.220.101.44"),
            },
            id="last_2h",
        ),
        # cutoff 16:30 -- only the 16:45 and 16:59 rows survive
        pytest.param(
            timedelta(minutes=30),
            {
                ("wkstn-088",    "103.224.182.253"),
                ("laptop-jfodi", "185.220.101.44"),
            },
            id="last_30min",
        ),
        pytest.param(timedelta(0), set(), id="zero_window"),
    ],
)
def test_malicious_connections_by_window(connection_log, threat_intel, now, window, expected):
    assert malicious_ip_connections(connection_log, threat_intel, now, window) == expected


# ---- vary the threat feed, window fixed at 5h ------------------------------

@pytest.mark.parametrize(
    "feed, expected",
    [
        # feed refreshed down to a single IP -- two different hosts hit it
        pytest.param(
            {"185.220.101.44"},
            {("wkstn-088", "185.220.101.44"), ("laptop-jfodi", "185.220.101.44")},
            id="one_ip_feed",
        ),
        pytest.param(set(), set(), id="empty_feed"),
        # IPs nobody talked to
        pytest.param({"1.2.3.4", "8.8.4.4"}, set(), id="feed_with_no_hits"),
    ],
)
def test_malicious_connections_by_feed(connection_log, now, feed, expected):
    assert malicious_ip_connections(connection_log, feed, now, timedelta(hours=5)) == expected


# ---- empty log --------------------------------------------------------------

def test_malicious_connections_empty_log(threat_intel, now):
    assert malicious_ip_connections([], threat_intel, now, timedelta(hours=5)) == set()

from datetime import timedelta

import pytest

from main import failed_attempts_in_window


@pytest.mark.parametrize(
    "n, window, expected",
    [
        pytest.param(
            3, timedelta(days=1),
            [("203.0.113.7", 6), ("198.51.100.22", 4)],
            id="whole_day_n3",
        ),
        pytest.param(
            1, timedelta(days=1),
            [
                ("203.0.113.7", 6),
                ("198.51.100.22", 4),
                ("203.0.113.99", 2),
                ("192.0.2.15", 1),
                ("172.16.4.9", 1),
            ],
            id="whole_day_n1",
        ),
        # 198.51.100.22 has 4, so it drops out; only the spray survives
        pytest.param(5, timedelta(days=1), [("203.0.113.7", 6)], id="whole_day_n5"),
        # above every count
        pytest.param(7, timedelta(days=1), [], id="whole_day_n7"),
        # cutoff 12:00 -- the 09:52-10:00 spray falls out entirely
        pytest.param(3, timedelta(hours=5), [("198.51.100.22", 4)], id="last_5h_n3"),
        # cutoff 16:30, only one failure after it
        pytest.param(3, timedelta(minutes=30), [], id="last_30min_n3"),
        pytest.param(
            2, timedelta(hours=5),
            [("198.51.100.22", 4), ("203.0.113.99", 2)],
            id="last_5h_n2",
        ),
        pytest.param(
            1, timedelta(hours=5),
            [
                ("198.51.100.22", 4),
                ("203.0.113.99", 2),
                ("192.0.2.15", 1),
                ("172.16.4.9", 1),
            ],
            id="last_5h_n1",
        ),
        # cutoff is exactly 16:30, and 203.0.113.99's second failure is AT 16:30.
        # `timestamp <= cutoff` drops it, so only 172.16.4.9 at 16:53 is left.
        pytest.param(1, timedelta(minutes=30), [("172.16.4.9", 1)], id="last_30min_n1"),
    ],
)
def test_failed_attempts_in_window(auth_logs, now, n, window, expected):
    assert failed_attempts_in_window(auth_logs, n, now, window) == expected

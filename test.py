from datetime import datetime, timedelta
from main import failed_attempts_in_window


NOW = datetime(2024, 1, 1, 17, 0)
auth_logs = [
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


# ---- baseline: whole day, N=3 --------------------------------------------

def test_whole_day_n3():
    res = failed_attempts_in_window(auth_logs, 3, NOW, timedelta(days=1))
    assert res == [("203.0.113.7", 6), ("198.51.100.22", 4)]
    print("PASS test_whole_day_n3")


# ---- change N, keep the window at a whole day ----------------------------

def test_whole_day_n1():
    res = failed_attempts_in_window(auth_logs, 1, NOW, timedelta(days=1))
    assert res == [
        ("203.0.113.7", 6),
        ("198.51.100.22", 4),
        ("203.0.113.99", 2),
        ("192.0.2.15", 1),
        ("172.16.4.9", 1),
    ]
    print("PASS test_whole_day_n1")


def test_whole_day_n5():
    # 198.51.100.22 has 4, so it drops out; only the spray survives
    res = failed_attempts_in_window(auth_logs, 5, NOW, timedelta(days=1))
    assert res == [("203.0.113.7", 6)]
    print("PASS test_whole_day_n5")


def test_whole_day_n7():
    # above every count
    res = failed_attempts_in_window(auth_logs, 7, NOW, timedelta(days=1))
    assert res == []
    print("PASS test_whole_day_n7")


# ---- change the window, keep N=3 ----------------------------------------

def test_last_5h_n3():
    # cutoff 12:00 -- the 09:52-10:00 spray falls out entirely
    res = failed_attempts_in_window(auth_logs, 3, NOW, timedelta(hours=5))
    assert res == [("198.51.100.22", 4)]
    print("PASS test_last_5h_n3")


def test_last_30min_n3():
    # cutoff 16:30, only one failure after it
    res = failed_attempts_in_window(auth_logs, 3, NOW, timedelta(minutes=30))
    assert res == []
    print("PASS test_last_30min_n3")


# ---- change both --------------------------------------------------------

def test_last_5h_n2():
    res = failed_attempts_in_window(auth_logs, 2, NOW, timedelta(hours=5))
    assert res == [("198.51.100.22", 4), ("203.0.113.99", 2)]
    print("PASS test_last_5h_n2")


def test_last_5h_n1():
    res = failed_attempts_in_window(auth_logs, 1, NOW, timedelta(hours=5))
    assert res == [
        ("198.51.100.22", 4),
        ("203.0.113.99", 2),
        ("192.0.2.15", 1),
        ("172.16.4.9", 1),
    ]
    print("PASS test_last_5h_n1")


def test_last_30min_n1():
    # cutoff is exactly 16:30, and 203.0.113.99's second failure is AT 16:30.
    # `timestamp <= cutoff` drops it, so only 172.16.4.9 at 16:53 is left.
    res = failed_attempts_in_window(auth_logs, 1, NOW, timedelta(minutes=30))
    assert res == [("172.16.4.9", 1)]
    print("PASS test_last_30min_n1")


if __name__ == "__main__":
    test_whole_day_n3()
    test_whole_day_n1()
    test_whole_day_n5()
    test_whole_day_n7()
    test_last_5h_n3()
    test_last_30min_n3()
    test_last_5h_n2()
    test_last_5h_n1()
    test_last_30min_n1()
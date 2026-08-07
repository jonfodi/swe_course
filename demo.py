"""Show two users getting their own org's data, over real HTTP.

Boots its own uvicorn on port 8001, runs the requests, tears it down:

    ./venv/bin/python demo.py

urllib rather than httpx/requests so this needs no dependency that isn't
already in the venv.
"""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8001"

# these match _FAKE_TOKENS in auth.py
ALICE = "token-alice"    # org: acme
BOB = "token-bob"        # org: acme  -- same org as alice, different user
CAROL = "token-carol"    # org: globex


def get(path, token=None):
    """GET path, returning (status, parsed body or None)."""
    req = urllib.request.Request(BASE + path)
    if token is not None:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            return res.status, json.load(res)
    except urllib.error.HTTPError as e:
        return e.code, None


def wait_for_server(proc, timeout=15):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            sys.exit(f"server died during startup (exit {proc.returncode})")
        try:
            # an unauthenticated request is the cheapest liveness probe: a 401
            # means the app is up *and* the auth dependency is wired
            if get("/api/me")[0] == 401:
                return
        except urllib.error.URLError:
            pass
        time.sleep(0.1)
    sys.exit("server did not come up in time")


def rule(title):
    print(f"\n\033[1m{title}\033[0m")


def usernames(token):
    status, body = get("/api/auth-logs", token)
    assert status == 200, status
    return sorted({row["username"] for row in body})


def show(label, token):
    _, me = get("/api/me", token)
    _, failed = get("/api/failed-attempts?n=1", token)
    print(f"   {label}")
    print(f"     /api/me           -> {me['user_id']} @ {me['org_id']}")
    print(f"     /api/auth-logs    -> {usernames(token)}")
    print(f"     /api/failed-...   -> {failed}")


def main():
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--port", "8001", "--log-level", "warning"],
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    try:
        wait_for_server(proc)

        rule("without a valid credential there is no instance to reach")
        for label, token in [("no header", None), ("garbage token", "token-nope")]:
            status, _ = get("/api/auth-logs", token)
            print(f"   {label:<16} GET /api/auth-logs -> {status}")
            assert status == 401

        rule("same URLs, different Authorization header, different instance")
        show("alice", ALICE)
        show("carol", CAROL)

        rule("bob is a different user in alice's org, so he gets her instance")
        show("bob", BOB)

        overlap = set(usernames(ALICE)) & set(usernames(CAROL))
        assert not overlap, overlap
        assert usernames(BOB) == usernames(ALICE)
        print("\n   \033[32morgs disjoint; users in one org share an instance\033[0m")
    finally:
        proc.terminate()
        proc.wait(timeout=10)


if __name__ == "__main__":
    main()

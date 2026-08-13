"""Tests for the per-org caching and the tenant boundary.

These exercise the registry and the auth dependency directly rather than
through HTTP -- no test client is installed, and the interesting behaviour
(caching, isolation, the cold-start race) is not about the wire anyway.
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from auth import get_current_user
from registry import CyberRegistry
from sample_data import UnknownOrg, load_org_data


def creds(token):
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


@pytest.fixture
def registry():
    return CyberRegistry(load_org_data)


# ---- auth -------------------------------------------------------------------

def test_known_token_resolves_to_its_org():
    assert get_current_user(creds("token-alice")).org_id == "acme"
    assert get_current_user(creds("token-carol")).org_id == "globex"


def test_two_users_can_share_an_org():
    alice = get_current_user(creds("token-alice"))
    bob = get_current_user(creds("token-bob"))

    assert alice.user_id != bob.user_id
    assert alice.org_id == bob.org_id


@pytest.mark.parametrize("cred", [None, creds("nonsense"), creds("")], ids=["missing", "unknown", "empty"])
def test_bad_credentials_are_rejected(cred):
    with pytest.raises(HTTPException) as exc:
        get_current_user(cred)
    assert exc.value.status_code == 401


# ---- caching ----------------------------------------------------------------

def test_same_org_returns_the_same_instance(registry):
    # the whole point of the registry: the index is built once and reused,
    # not rebuilt per request
    assert registry.for_org("acme") is registry.for_org("acme")


def test_orgs_get_separate_instances(registry):
    assert registry.for_org("acme") is not registry.for_org("globex")


def test_unknown_org_propagates(registry):
    with pytest.raises(UnknownOrg):
        registry.for_org("no-such-org")


# ---- isolation --------------------------------------------------------------

def test_one_orgs_index_holds_only_its_own_logs(registry):
    acme = registry.for_org("acme")
    globex = registry.for_org("globex")

    acme_users = {log.username for log in acme.get_auth_logs()}
    globex_users = {log.username for log in globex.get_auth_logs()}

    assert acme_users & globex_users == set()
    assert "alice" in acme_users
    assert "mrivera" in globex_users


def test_queries_are_scoped_without_a_filter_argument(registry):
    # neither call passes an org -- the instance already is the scope
    acme_hosts = {src for src, _ in registry.for_org("acme").malicious_ip_connections()}
    globex_hosts = {src for src, _ in registry.for_org("globex").malicious_ip_connections()}

    assert acme_hosts & globex_hosts == set()
    assert all(h.startswith("gbx_") for h in globex_hosts)


def test_mutating_a_returned_result_cannot_corrupt_the_cached_index(registry):
    # malicious_ip_connections returns a copy, so a caller poking at it does
    # not damage state that outlives the request
    acme = registry.for_org("acme")
    before = acme.malicious_ip_connections()
    before.add(("attacker", "1.2.3.4"))

    assert ("attacker", "1.2.3.4") not in acme.malicious_ip_connections()


# ---- the cold-start race ----------------------------------------------------

def test_concurrent_cold_requests_build_exactly_once():
    """Two requests for the same cold org must not both construct.

    Without the lock in for_org this fails: `if missing: build` is
    check-then-act, and FastAPI runs non-async handlers on a threadpool, so
    both threads pass the check before either writes.
    """
    builds = []
    barrier = threading.Barrier(8)

    def slow_loader(org_id):
        builds.append(org_id)   # list.append is atomic under the GIL
        time.sleep(0.05)        # widen the window a racy impl would lose
        return load_org_data(org_id)

    registry = CyberRegistry(slow_loader)

    def request():
        barrier.wait()          # line all threads up on the cold path
        return registry.for_org("acme")

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = [f.result() for f in [pool.submit(request) for _ in range(8)]]

    assert builds == ["acme"]
    assert all(r is results[0] for r in results)


def test_concurrent_requests_for_different_orgs_stay_separate():
    registry = CyberRegistry(load_org_data)
    orgs = ["acme", "globex"] * 16

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(registry.for_org, orgs))

    by_org = dict(zip(orgs, results))
    assert all(r is by_org[org] for org, r in zip(orgs, results))
    assert by_org["acme"] is not by_org["globex"]

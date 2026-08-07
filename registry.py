"""One Cyber instance per org."""

import threading

from cyber import Cyber


class CyberRegistry:
    """Maps an org id to that org's Cyber instance.

    Same class, same methods, different data: each instance holds one org's
    logs and its own indexes, which is why the query methods need no org
    argument -- there is no other org's data inside to filter out.
    """

    def __init__(self, loader):
        # loader: org_id -> (auth_logs, connection_logs, threat_intel)
        self._loader = loader
        self._by_org: dict[str, Cyber] = {}
        self._lock = threading.Lock()

    def for_org(self, org_id: str) -> Cyber:
        # a dict read is atomic under the GIL, and an entry is never replaced
        # once set, so the common case needs no lock
        cyb = self._by_org.get(org_id)
        if cyb is not None:
            return cyb

        # `if missing: build` is check-then-act, and FastAPI runs non-async
        # handlers on a threadpool -- without this lock, two requests for the
        # same new org can both pass the check and build separate instances
        with self._lock:
            cyb = self._by_org.get(org_id)   # another thread may have won
            if cyb is None:
                cyb = Cyber(*self._loader(org_id))
                self._by_org[org_id] = cyb
            return cyb

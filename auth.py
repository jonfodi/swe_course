"""Authentication: turning a request into a known principal.

Everything in here is a stand-in for real tokens. The point of isolating it in
one module is that swapping in real JWT verification later should touch only
`get_current_user` -- every caller downstream already receives a CurrentUser
and doesn't care how it was established.
"""

from typing import NamedTuple

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


class CurrentUser(NamedTuple):
    """The verified identity behind one request.

    Request-lifetime, not process-lifetime: this is created fresh per request
    and passed as an argument. It is never stored on anything shared -- that
    is the distinction that keeps concurrent requests from seeing each other.
    """
    user_id: str
    org_id: str


# auto_error=False so a missing header lands in our own 401 below, with a
# WWW-Authenticate header, instead of starlette's bare 403
_bearer = HTTPBearer(auto_error=False)


# Stands in for a users table plus signed tokens.
#
# The token is the dict key only because it's fake. A real token *carries* the
# claims inside it, signed, so the server verifies a signature instead of doing
# a lookup. What survives the swap is the shape: credential in, CurrentUser out.
#
# alice and bob deliberately share an org -- they will be served the same Cyber
# instance, which is the point of caching per org rather than per user.
_FAKE_TOKENS = {
    "token-alice": CurrentUser(user_id="u_acme_1", org_id="acme"),
    "token-bob": CurrentUser(user_id="u_acme_2", org_id="acme"),
    "token-carol": CurrentUser(user_id="u_globex_1", org_id="globex"),
}


def get_current_user(
    cred: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> CurrentUser:
    """Resolve the caller, or 401.

    Note what is *not* a parameter here: anything the caller could choose. The
    identity is derived from the credential alone.
    """
    user = _FAKE_TOKENS.get(cred.credentials) if cred is not None else None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

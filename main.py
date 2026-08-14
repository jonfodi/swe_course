from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware

from cyber import Cyber
from registry import CyberRegistry
from sample_data import UnknownOrg, load_org_data
from schemas import AuthLogOut

# sample data has no wall-clock meaning, so anchor "now" to the log itself
# instead of datetime.utcnow()
DEFAULT_NOW = datetime(2024, 1, 1, 17, 0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # one registry per process, holding the Cyber instances. on app.state
    # rather than as a module global so a test can supply its own.
    app.state.registry = CyberRegistry(load_org_data)
    yield


app = FastAPI(title="Cyber API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def get_org_cyber(request: Request, org_id: str = "acme") -> Cyber:
    try:
        return request.app.state.registry.for_org(org_id)
    except UnknownOrg:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Unknown org") from None


@app.get("/api/failed-attempts")
def get_failed_attempts(
    n: int = 1,
    window_hours: float = 8,
    now: datetime = DEFAULT_NOW,
    cyb: Cyber = Depends(get_org_cyber),
):
    window = timedelta(hours=window_hours)
    return cyb.failed_attempts_in_window(n, now, window)


@app.get("/api/malicious-connections")
def get_malicious_connections(cyb: Cyber = Depends(get_org_cyber)):
    return cyb.malicious_ip_connections()


@app.get("/api/auth-logs", response_model=list[AuthLogOut])
def get_auth_logs(cyb: Cyber = Depends(get_org_cyber)):
    return cyb.get_auth_logs()

from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sample_data import load_org_data
from schemas import AuthLogOut
from cyber import Cyber

# sample data has no wall-clock meaning, so anchor "now" to the log itself
# instead of datetime.utcnow()
DEFAULT_NOW = datetime(2024, 1, 1, 17, 0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.cyb = Cyber(*load_org_data("acme"))
    yield


app = FastAPI(title="Cyber API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/failed-attempts")
def get_failed_attempts(n: int = 1, window_hours: float = 8, now: datetime = DEFAULT_NOW):
    window = timedelta(hours=window_hours)
    return app.state.cyb.failed_attempts_in_window(n, now, window)


@app.get("/api/malicious-connections")
def get_malicious_connections():
    return app.state.cyb.malicious_ip_connections()


@app.get("/api/auth-logs", response_model=list[AuthLogOut])
def get_auth_logs():
    return app.state.cyb.get_auth_logs()

@app.get("/api/threat_intel")
def get_threat_intel():
    return app.state.cyb.get_threat_intel()

@app.post("/api/latest_threats")
def update_threat_intel(latest_threat_intel: list[str]):
    # normalise to a set at the boundary -- ingest does set arithmetic
    app.state.cyb.ingest_latest_threat_intel(set(latest_threat_intel))
    # return the new state so the client can write it straight into its cache
    return app.state.cyb.get_threat_intel()
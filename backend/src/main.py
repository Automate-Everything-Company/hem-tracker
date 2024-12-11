import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.src.levels.router import router as levels
from backend.src.users.router import router as users
from backend.src.measurement.router import router as measurement
from backend.src.authentication.router import router as authentication
from backend.src.password_reset.router import router as password
from backend.src.frontend.router import router as frontend
from backend.src.common.logging_config import setup_logging

setup_logging()

logger = logging.getLogger("hem_tracker")


STATIC_PATH = Path(__file__).parent / "static"
TEMPLATES_PATH = Path(__file__).parent / "templates"

logger.debug(f"Static path: {STATIC_PATH.exists()}")
logger.debug(f"Templates path: {TEMPLATES_PATH.exists()}")

app = FastAPI(title="Hemophilia Tracker", version="0.0.1")

app.include_router(levels)
app.include_router(users)
app.include_router(measurement)
app.include_router(authentication)
app.include_router(password)
app.include_router(frontend)

app.mount("/static", StaticFiles(directory=str(STATIC_PATH)), name="static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, you might use '*'; specify domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/debug/static")
def check_static():
    return {
        "static_dir": str(STATIC_PATH),
        "exists": STATIC_PATH.exists(),
        "contents": [str(f) for f in STATIC_PATH.glob("**/*") if f.is_file()]
    }
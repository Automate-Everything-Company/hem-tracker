import logging.config
from pathlib import Path

# Ensure the log directory exists
ROOT_DIR = Path(__file__).parent.parent

LOG_DIR = ROOT_DIR / "logs"

LOG_FILE = LOG_DIR / "hem_tracker.log"

if not LOG_DIR.exists():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": LOG_FILE,
            "formatter": "default",
            "level": "DEBUG",
        },
    },
    "loggers": {
        "hem_tracker": {
            "level": "DEBUG",
            "handlers": ["file"],  # Note the use of a list here
            "propagate": False,
        },
    },
}

def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)

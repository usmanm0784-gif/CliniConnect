# logger.py
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

logger = logging.getLogger("healthcare_app")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

if not logger.handlers:
    if os.environ.get("VERCEL"):
        # Serverless: filesystem is read-only, log to stdout instead
        handler = logging.StreamHandler()
    else:
        # Local dev: log to a rotating file
        LOG_DIR = Path("logs")
        LOG_DIR.mkdir(exist_ok=True)
        handler = RotatingFileHandler(
            LOG_DIR / "app.log",
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=5,
            encoding="utf-8",
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)
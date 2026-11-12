from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def _as_bool(value: str | None, default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "si", "sí", "on"}


DEMO_MODE = _as_bool(os.getenv("MIMASCOTA_DEMO_MODE"), True)
API_BASE_URL = os.getenv("MIMASCOTA_API_BASE_URL", "http://127.0.0.1:5000/api").rstrip("/")
REQUEST_TIMEOUT = float(os.getenv("MIMASCOTA_REQUEST_TIMEOUT", "12"))
API_TOKEN = os.getenv("MIMASCOTA_API_TOKEN", "").strip()
APP_NAME = "MiMascota"
APP_VERSION = "2.0.0"

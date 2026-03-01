"""Runtime configuration helpers.

Loads key/value pairs from backend/.env (if present) without requiring python-dotenv.
"""

from __future__ import annotations

import os
from pathlib import Path

_ENV_LOADED = False


def load_env_file() -> None:
    global _ENV_LOADED
    if _ENV_LOADED:
        return

    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        _ENV_LOADED = True
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)

    _ENV_LOADED = True


def get_env(name: str, default: str | None = None, required: bool = False) -> str | None:
    load_env_file()
    value = os.environ.get(name, default)
    if required and (value is None or str(value).strip() == ""):
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

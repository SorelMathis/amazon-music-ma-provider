"""Setup flow for the custom Amazon Music scaffold.

This module is intentionally a thin bridge for a provider setup process. It does not persist
passwords in the repository and does not claim to authenticate against Amazon in production.
"""

from __future__ import annotations

from typing import Any


async def run_setup(mass: Any, config: dict[str, Any]) -> dict[str, Any]:
    username = str(config.get("username", "")).strip()
    password = str(config.get("password", "")).strip()
    region = str(config.get("region", "fr")).strip() or "fr"
    if not username:
        raise ValueError("username is required")
    if not password:
        raise ValueError("password is required")
    return {
        "username": username,
        "region": region,
        "source": "local-dev-scaffold",
    }

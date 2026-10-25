"""Setup flow for the custom Amazon Music provider.

This file is designed to be copied into an actual Music Assistant provider directory when the
project is moved into a local MA provider source tree. It deliberately never stores secrets in the
repository tree and expects credentials to be handled by secure local storage.
"""

from __future__ import annotations

from typing import Any


async def run_setup(mass: Any, config: dict[str, Any]) -> dict[str, Any]:
    """Validate that the local config contains the information needed for a real provider setup."""
    username = config.get("username", "").strip()
    password = config.get("password", "").strip()
    region = config.get("region", "fr").strip() or "fr"
    if not username or not password:
        raise ValueError("username and password are required")
    return {
        "username": username,
        "password": password,
        "region": region,
        "mock_mode": True,
    }

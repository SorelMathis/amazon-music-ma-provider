"""Secure settings and storage helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ProviderSettings:
    """Local settings for the custom provider scaffold."""

    region: str = "fr"
    session_ttl_minutes: int = 60
    enable_mock_mode: bool = True
    stream_timeout_seconds: int = 30
    auth_file: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "region": self.region,
            "session_ttl_minutes": self.session_ttl_minutes,
            "enable_mock_mode": self.enable_mock_mode,
            "stream_timeout_seconds": self.stream_timeout_seconds,
            "auth_file": self.auth_file,
        }


def get_secure_storage_path() -> Path:
    """Return a user-local secure storage path. This avoids putting secrets in the repository."""
    path = Path.home() / ".config" / "amazon_music_ma_provider" / "session.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def save_settings(settings: ProviderSettings, path: str | Path | None = None) -> None:
    """Persist settings to a local JSON file."""
    target = Path(path) if path is not None else get_secure_storage_path().with_name("settings.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(settings.to_dict(), handle, indent=2)


def load_settings(path: str | Path | None = None) -> ProviderSettings:
    """Load settings from disk, falling back to defaults when absent."""
    target = Path(path) if path is not None else get_secure_storage_path().with_name("settings.json")
    if not target.exists():
        return ProviderSettings()
    with target.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    return ProviderSettings(
        region=raw.get("region", "fr"),
        session_ttl_minutes=int(raw.get("session_ttl_minutes", 60)),
        enable_mock_mode=bool(raw.get("enable_mock_mode", True)),
        stream_timeout_seconds=int(raw.get("stream_timeout_seconds", 30)),
        auth_file=raw.get("auth_file"),
    )

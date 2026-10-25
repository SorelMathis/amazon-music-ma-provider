"""Secure storage helpers and runtime configuration for the custom provider scaffold."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import keyring
except ImportError:  # pragma: no cover - optional dependency
    keyring = None


@dataclass
class ProviderSettings:
    """User-local settings for the custom scaffold.

    Secrets are never stored inside the repository itself.
    """

    region: str = "fr"
    session_ttl_minutes: int = 60
    enable_mock_mode: bool = True
    stream_timeout_seconds: int = 30
    auth_file: str | None = None
    allowed_stream_hosts: tuple[str, ...] = ()
    real_mode: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "region": self.region,
            "session_ttl_minutes": self.session_ttl_minutes,
            "enable_mock_mode": self.enable_mock_mode,
            "stream_timeout_seconds": self.stream_timeout_seconds,
            "auth_file": self.auth_file,
            "allowed_stream_hosts": list(self.allowed_stream_hosts),
            "real_mode": self.real_mode,
        }


def get_secure_storage_dir() -> Path:
    """Return the user-local storage directory used for secure session data."""
    return Path.home() / ".local" / "share" / "amazon_music_ma_provider"


def get_secure_storage_file() -> Path:
    """Return the local protected file used when keyring is unavailable."""
    storage = get_secure_storage_dir()
    storage.mkdir(parents=True, exist_ok=True)
    return storage / "session.json"


def _ensure_file_permissions(path: Path) -> None:
    """Apply restrictive permissions when the OS supports it."""
    if os.name == "nt":
        return
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def _write_protected_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON to a protected file with restrictive permissions."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    _ensure_file_permissions(path)


class SecureSecretStore:
    """Store secret material using keyring when available; otherwise use a protected local file."""

    def __init__(self, service_name: str = "amazon-music-ma-provider") -> None:
        self.service_name = service_name

    def store_secret(self, name: str, value: str) -> None:
        if keyring is not None:
            keyring.set_password(self.service_name, name, value)
            return
        payload = {}
        path = get_secure_storage_file()
        if path.exists():
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                payload = {}
        payload[name] = value
        _write_protected_json(path, payload)

    def read_secret(self, name: str) -> str | None:
        if keyring is not None:
            return keyring.get_password(self.service_name, name)
        path = get_secure_storage_file()
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
        value = payload.get(name)
        return value if isinstance(value, str) else None

    def delete_secret(self, name: str) -> None:
        if keyring is not None:
            try:
                keyring.delete_password(self.service_name, name)
            except keyring.errors.PasswordDeleteError:
                pass
            return
        path = get_secure_storage_file()
        if not path.exists():
            return
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return
        payload.pop(name, None)
        _write_protected_json(path, payload)


def save_settings(settings: ProviderSettings, path: str | Path | None = None) -> None:
    """Persist settings to a local protected JSON file, not inside the repository."""
    target = Path(path) if path is not None else get_secure_storage_file().with_name("settings.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    _write_protected_json(target, settings.to_dict())


def load_settings(path: str | Path | None = None) -> ProviderSettings:
    """Load settings from a protected local file, falling back to defaults."""
    target = Path(path) if path is not None else get_secure_storage_file().with_name("settings.json")
    if not target.exists():
        return ProviderSettings()
    try:
        with target.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except (json.JSONDecodeError, OSError):
        return ProviderSettings()
    allowed_hosts_value = raw.get("allowed_stream_hosts", ())
    if isinstance(allowed_hosts_value, str):
        allowed_hosts = (allowed_hosts_value,)
    else:
        allowed_hosts = tuple(str(item) for item in allowed_hosts_value)
    return ProviderSettings(
        region=str(raw.get("region", "fr")),
        session_ttl_minutes=int(raw.get("session_ttl_minutes", 60)),
        enable_mock_mode=bool(raw.get("enable_mock_mode", True)),
        stream_timeout_seconds=int(raw.get("stream_timeout_seconds", 30)),
        auth_file=raw.get("auth_file"),
        allowed_stream_hosts=allowed_hosts,
        real_mode=bool(raw.get("real_mode", False)),
    )

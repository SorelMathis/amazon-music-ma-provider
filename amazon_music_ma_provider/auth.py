"""Authentication flow for a custom Amazon Music provider scaffold."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from .config import ProviderSettings, get_secure_storage_path


class AmazonAuthError(RuntimeError):
    """Raised when the Amazon auth layer rejects a login or token state."""


@dataclass
class TokenBundle:
    """Authenticated session metadata stored securely."""

    access_token: str
    refresh_token: str
    expires_at: datetime
    token_type: str = "Bearer"
    region: str = "fr"
    extra: dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Return True when the current session has expired."""
        return datetime.now(timezone.utc) >= self.expires_at


class AmazonMusicAuthenticator:
    """Lightweight authentication shim used for validation and storage logic.

    This implementation intentionally never claims to be an official Amazon client.
    It validates input, stores tokens securely, and provides a mock session contract.
    """

    def __init__(self, settings: ProviderSettings | None = None) -> None:
        self.settings = settings or ProviderSettings()

    def validate_credentials(self, username: str, password: str) -> None:
        """Reject obviously invalid credentials without exposing secrets."""
        if not username or not username.strip():
            raise AmazonAuthError("username is required")
        if not password or not password.strip():
            raise AmazonAuthError("password is required")
        if "@" not in username and len(username.strip()) < 3:
            raise AmazonAuthError("username format is invalid")

    def create_mock_session(self, username: str, password: str) -> TokenBundle:
        """Create a mock Amazon session for local validation only."""
        self.validate_credentials(username, password)
        expires_in = self.settings.session_ttl_minutes
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in)
        return TokenBundle(
            access_token="mock-access-token-for-local-validation",
            refresh_token="mock-refresh-token-for-local-validation",
            expires_at=expires_at,
            region=self.settings.region,
            extra={"username": username.strip()},
        )

    def save_session(self, bundle: TokenBundle) -> None:
        """Persist a session bundle using the secure storage path."""
        path = get_secure_storage_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(
                {
                    "access_token": bundle.access_token,
                    "refresh_token": bundle.refresh_token,
                    "expires_at": bundle.expires_at.isoformat(),
                    "token_type": bundle.token_type,
                    "region": bundle.region,
                    "extra": bundle.extra,
                },
                handle,
                indent=2,
            )

    def load_session(self) -> TokenBundle | None:
        """Load a previously saved session if present."""
        path = get_secure_storage_path()
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        expires_at = datetime.fromisoformat(data["expires_at"])
        return TokenBundle(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_at=expires_at,
            token_type=data.get("token_type", "Bearer"),
            region=data.get("region", "fr"),
            extra=data.get("extra", {}),
        )

    def clear_session(self) -> None:
        """Remove the saved session."""
        path = get_secure_storage_path()
        if path.exists():
            path.unlink()

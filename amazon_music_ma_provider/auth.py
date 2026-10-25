"""Authentication layer for the Amazon Music provider scaffold.

This module intentionally separates mock and live logic. Mock values are clearly tagged as such
and never presented as production Amazon credentials or stream URLs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from .config import ProviderSettings, SecureSecretStore


class AmazonAuthError(RuntimeError):
    """Raised when the auth layer rejects a login or a stored session."""


@dataclass
class TokenBundle:
    """Opaque session metadata used by the local scaffold only."""

    access_token: str
    refresh_token: str
    expires_at: datetime
    token_type: str = "Bearer"
    region: str = "fr"
    source: str = "mock"
    extra: dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at


class AmazonMusicAuthenticator:
    """Authentication shim for local validation and secure token persistence."""

    def __init__(self, settings: ProviderSettings | None = None) -> None:
        self.settings = settings or ProviderSettings()
        self.store = SecureSecretStore("amazon-music-ma-provider")

    def validate_credentials(self, username: str, password: str) -> None:
        if not username or not username.strip():
            raise AmazonAuthError("username is required")
        if not password or not password.strip():
            raise AmazonAuthError("password is required")
        if "@" not in username and len(username.strip()) < 3:
            raise AmazonAuthError("username format is invalid")

    def create_mock_session(self, username: str, password: str) -> TokenBundle:
        """Create a clearly-labeled mock session for local validation only."""
        self.validate_credentials(username, password)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=self.settings.session_ttl_minutes)
        return TokenBundle(
            access_token="mock-access-token-local-only",
            refresh_token="mock-refresh-token-local-only",
            expires_at=expires_at,
            region=self.settings.region,
            source="mock",
            extra={"username": username.strip(), "purpose": "local-validation-only"},
        )

    def save_session(self, bundle: TokenBundle) -> None:
        """Persist the opaque token bundle in protected user storage. No secrets are kept in repo."""
        self.store.store_secret("access_token", bundle.access_token)
        self.store.store_secret("refresh_token", bundle.refresh_token)
        self.store.store_secret(
            "session_metadata",
            json.dumps(
                {
                    "expires_at": bundle.expires_at.isoformat(),
                    "token_type": bundle.token_type,
                    "region": bundle.region,
                    "source": bundle.source,
                    "extra": bundle.extra,
                },
                separators=(",", ":"),
            ),
        )

    def load_session(self) -> TokenBundle | None:
        access_token = self.store.read_secret("access_token")
        refresh_token = self.store.read_secret("refresh_token")
        metadata_raw = self.store.read_secret("session_metadata")
        if not access_token or not refresh_token or not metadata_raw:
            return None
        try:
            metadata = json.loads(metadata_raw)
        except json.JSONDecodeError:
            return None
        expires_at = datetime.fromisoformat(metadata.get("expires_at", datetime.now(timezone.utc).isoformat()))
        return TokenBundle(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            token_type=str(metadata.get("token_type", "Bearer")),
            region=str(metadata.get("region", "fr")),
            source=str(metadata.get("source", "mock")),
            extra=metadata.get("extra", {}),
        )

    def clear_session(self) -> None:
        self.store.delete_secret("access_token")
        self.store.delete_secret("refresh_token")
        self.store.delete_secret("session_metadata")

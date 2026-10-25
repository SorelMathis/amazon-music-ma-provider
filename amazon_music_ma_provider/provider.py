"""Provider runtime scaffold that matches the MA provider contract shape without importing MA itself."""

from __future__ import annotations

from typing import Any

from .auth import AmazonAuthError, AmazonMusicAuthenticator, TokenBundle
from .client import AmazonMusicClient, SearchResult
from .config import ProviderSettings


class AmazonMusicProvider:
    """Custom Music Assistant provider scaffold.

    This code intentionally does not claim access to a real Amazon Music Unlimited catalog.
    It provides a compatible internal shape for search, album/playlist browsing, and streaming
    metadata generation, while clearly documenting where a real Amazon session is required.
    """

    def __init__(self, settings: ProviderSettings | None = None) -> None:
        self.settings = settings or ProviderSettings()
        self.auth = AmazonMusicAuthenticator(self.settings)
        self.client = AmazonMusicClient(access_token=None, region=self.settings.region)

    async def authenticate(self, username: str, password: str) -> TokenBundle:
        """Create and persist a local auth session for validation purposes."""
        try:
            bundle = self.auth.create_mock_session(username, password)
        except AmazonAuthError:
            raise
        self.auth.save_session(bundle)
        self.client.access_token = bundle.access_token
        return bundle

    async def search(self, query: str, media_types: tuple[str, ...] | None = None, limit: int = 5) -> dict[str, list[SearchResult]]:
        """Search the provider catalog using the mock client."""
        if not self.client.is_configured():
            raise AmazonAuthError("provider is not authenticated")
        return await self.client.search(query, media_types, limit)

    async def get_track(self, track_id: str) -> dict[str, Any]:
        """Return the metadata for a track, including a stream URL stub."""
        if not self.client.is_configured():
            raise AmazonAuthError("provider is not authenticated")
        return await self.client.get_track(track_id)

    async def get_album(self, album_id: str) -> dict[str, Any]:
        """Return album metadata for the given album id."""
        if not self.client.is_configured():
            raise AmazonAuthError("provider is not authenticated")
        return await self.client.get_album(album_id)

    async def get_playlist(self, playlist_id: str) -> dict[str, Any]:
        """Return playlist metadata for the given playlist id."""
        if not self.client.is_configured():
            raise AmazonAuthError("provider is not authenticated")
        return await self.client.get_playlist(playlist_id)

    def get_stream_details(self, track_id: str) -> dict[str, Any]:
        """Return stream metadata for Music Assistant integration. This is not a live Amazon stream."""
        if not self.client.is_configured():
            raise AmazonAuthError("provider is not authenticated")
        stream_url = self.client.build_stream_url(track_id)
        return {
            "track_id": track_id,
            "stream_url": stream_url,
            "content_type": "audio/mpeg",
            "allow_seek": True,
            "can_seek": True,
            "is_valid": self.client.validate_stream_url(stream_url),
        }

    def restore_session(self) -> TokenBundle | None:
        """Restore the last stored session if present."""
        bundle = self.auth.load_session()
        if bundle is not None:
            self.client.access_token = bundle.access_token
        return bundle

    def clear_session(self) -> None:
        """Clear local session material."""
        self.auth.clear_session()
        self.client.access_token = None

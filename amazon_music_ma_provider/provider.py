"""Provider runtime adapter that keeps clear separation between mock runtime and live Amazon runtime."""

from __future__ import annotations

from typing import Any

from .auth import AmazonAuthError, AmazonMusicAuthenticator, TokenBundle
from .client import AmazonMusicClient, SearchResult
from .config import ProviderSettings


class AmazonMusicProvider:
    """Local runtime scaffold without pretending to be a real Amazon integration."""

    def __init__(self, settings: ProviderSettings | None = None) -> None:
        self.settings = settings or ProviderSettings()
        self.auth = AmazonMusicAuthenticator(self.settings)
        self.client = AmazonMusicClient(access_token=None, region=self.settings.region)

    async def authenticate(self, username: str, password: str) -> TokenBundle:
        if self.settings.real_mode:
            raise AmazonAuthError("real Amazon auth is not implemented in this scaffold")
        try:
            bundle = self.auth.create_mock_session(username, password)
        except AmazonAuthError:
            raise
        self.auth.save_session(bundle)
        self.client.access_token = bundle.access_token
        return bundle

    async def search(
        self,
        query: str,
        media_types: tuple[str, ...] | None = None,
        limit: int = 5,
    ) -> dict[str, list[SearchResult]]:
        if not self.client.is_configured():
            raise AmazonAuthError("provider is not authenticated")
        return await self.client.search(query, media_types, limit)

    async def get_track(self, track_id: str) -> dict[str, Any]:
        if not self.client.is_configured():
            raise AmazonAuthError("provider is not authenticated")
        return await self.client.get_track(track_id)

    async def get_album(self, album_id: str) -> dict[str, Any]:
        if not self.client.is_configured():
            raise AmazonAuthError("provider is not authenticated")
        return await self.client.get_album(album_id)

    async def get_playlist(self, playlist_id: str) -> dict[str, Any]:
        if not self.client.is_configured():
            raise AmazonAuthError("provider is not authenticated")
        return await self.client.get_playlist(playlist_id)

    def get_stream_details(self, track_id: str) -> dict[str, Any]:
        if not self.client.is_configured():
            raise AmazonAuthError("provider is not authenticated")
        stream_url = self.client.build_stream_url(track_id)
        allowed_hosts = tuple(host.lower() for host in self.settings.allowed_stream_hosts)
        is_valid = self.client.validate_stream_url(
            stream_url,
            allow_mock=self.settings.enable_mock_mode,
            allowed_hosts=allowed_hosts,
        )
        return {
            "track_id": track_id,
            "stream_url": stream_url,
            "content_type": "audio/mpeg",
            "allow_seek": True,
            "can_seek": True,
            "is_valid": is_valid,
            "source": "mock",
        }

    def restore_session(self) -> TokenBundle | None:
        bundle = self.auth.load_session()
        if bundle is not None:
            self.client.access_token = bundle.access_token
        return bundle

    def clear_session(self) -> None:
        self.auth.clear_session()
        self.client.access_token = None

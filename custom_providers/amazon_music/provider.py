"""Custom provider logic for a Music Assistant-compatible Amazon Music scaffold."""

from __future__ import annotations

from typing import Any

from amazon_music_ma_provider.provider import AmazonMusicProvider


class AmazonMusicMAProvider(AmazonMusicProvider):
    """Thin wrapper around the public provider logic for custom injection into a MA-like runtime."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__()
        self.config = config or {}

    async def search(self, query: str, media_types: tuple[str, ...] | None = None, limit: int = 5):
        return await super().search(query, media_types, limit)

    async def get_album(self, album_id: str):
        return await super().get_album(album_id)

    async def get_playlist(self, playlist_id: str):
        return await super().get_playlist(playlist_id)

    def get_stream_details(self, track_id: str):
        return super().get_stream_details(track_id)

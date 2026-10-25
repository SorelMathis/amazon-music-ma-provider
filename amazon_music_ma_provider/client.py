"""Asynchronous client and lightweight search helpers.

This package intentionally keeps all provider logic in a clearly marked mock layer. The code is
structured so a future live Amazon client can be swapped in behind the same interface without
changing the rest of the application contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable
from urllib.parse import urlparse


@dataclass
class SearchQuery:
    query: str
    media_types: tuple[str, ...] = ("track", "album", "artist", "playlist")
    limit: int = 10


@dataclass
class SearchResult:
    item_id: str
    item_type: str
    name: str
    artist: str | None = None
    image_url: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class AmazonMusicClient:
    """The mock client used for local validation. It never represents a live Amazon session."""

    def __init__(self, access_token: str | None = None, region: str = "fr") -> None:
        self.access_token = access_token
        self.region = region

    def is_configured(self) -> bool:
        return bool(self.access_token)

    async def search(
        self,
        query: str,
        media_types: Iterable[str] | None = None,
        limit: int = 5,
    ) -> dict[str, list[SearchResult]]:
        if not query or not query.strip():
            return {"track": [], "album": [], "artist": [], "playlist": []}
        if not self.is_configured():
            raise ValueError("client is not authenticated")
        selected = tuple(media_types or ("track", "album", "artist", "playlist"))
        result: dict[str, list[SearchResult]] = {key: [] for key in selected}
        for item_type in selected:
            for idx in range(min(limit, 3)):
                result[item_type].append(
                    SearchResult(
                        item_id=f"{item_type}-{idx}-{abs(hash(query + item_type))}",
                        item_type=item_type,
                        name=f"{item_type.title()} {query} {idx + 1}",
                        artist="Local test artist" if item_type in {"track", "album"} else None,
                        image_url=f"mock://amazon-music.local/{item_type}.png",
                        metadata={"region": self.region, "source": "mock"},
                    )
                )
        return result

    async def get_track(self, track_id: str) -> dict[str, Any]:
        if not self.is_configured():
            raise ValueError("client is not authenticated")
        return {
            "id": track_id,
            "title": "Local mock track",
            "artist": "Local test artist",
            "duration_ms": 212000,
            "available": True,
            "stream_url": self.build_stream_url(track_id),
        }

    async def get_album(self, album_id: str) -> dict[str, Any]:
        if not self.is_configured():
            raise ValueError("client is not authenticated")
        return {
            "id": album_id,
            "title": "Local mock album",
            "artist": "Local test artist",
            "tracks": [
                {"id": f"{album_id}-track-1", "title": "Track 1", "duration_ms": 200000},
                {"id": f"{album_id}-track-2", "title": "Track 2", "duration_ms": 210000},
            ],
        }

    async def get_playlist(self, playlist_id: str) -> dict[str, Any]:
        if not self.is_configured():
            raise ValueError("client is not authenticated")
        return {
            "id": playlist_id,
            "name": "Local mock playlist",
            "tracks": [
                {"id": f"{playlist_id}-track-1", "title": "Playlist Track 1"},
                {"id": f"{playlist_id}-track-2", "title": "Playlist Track 2"},
            ],
        }

    def build_stream_url(self, track_id: str) -> str:
        if not track_id:
            raise ValueError("track_id is required")
        return f"mock://amazon-music.local/stream/{track_id}?region={self.region}"

    def validate_stream_url(self, url: str, *, allow_mock: bool = False) -> bool:
        """Validate a real or mock URL without implying Amazon authorization."""
        if not isinstance(url, str) or not url.strip():
            return False
        parsed = urlparse(url)
        if parsed.scheme in {"http", "https"}:
            return parsed.netloc and parsed.netloc != "example.invalid"
        if allow_mock and parsed.scheme == "mock":
            return bool(parsed.netloc)
        return False

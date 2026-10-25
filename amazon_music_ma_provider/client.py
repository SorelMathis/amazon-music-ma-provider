"""Asynchronous client and search helpers for the provider scaffold."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


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
    """Minimal async client used for tests and local validation.

    It does not connect to the real Amazon service and is intentionally structured as a
    mockable shell that can later be wrapped behind a live Amazon API or authorized session.
    """

    def __init__(self, access_token: str | None = None, region: str = "fr") -> None:
        self.access_token = access_token
        self.region = region

    def is_configured(self) -> bool:
        """Return whether the client has a usable session."""
        return bool(self.access_token)

    async def search(self, query: str, media_types: tuple[str, ...] | None = None, limit: int = 5) -> dict[str, list[SearchResult]]:
        """Return mock search results. Local-only validation, not an official Amazon API call."""
        if not query or not query.strip():
            return {"track": [], "album": [], "artist": [], "playlist": []}
        if not self.is_configured():
            raise ValueError("client is not authenticated")
        media_types = media_types or ("track", "album", "artist", "playlist")
        result: dict[str, list[SearchResult]] = {key: [] for key in media_types}
        for item_type in media_types:
            for idx in range(min(limit, 3)):
                result[item_type].append(
                    SearchResult(
                        item_id=f"{item_type}-{idx}-{abs(hash(query + item_type))}",
                        item_type=item_type,
                        name=f"{item_type.title()} {query} {idx + 1}",
                        artist="Amazon Test Artist" if item_type in {"track", "album"} else None,
                        image_url=f"https://example.invalid/{item_type}.png",
                        metadata={"region": self.region},
                    )
                )
        return result

    async def get_track(self, track_id: str) -> dict[str, Any]:
        """Return a mock track payload."""
        if not self.is_configured():
            raise ValueError("client is not authenticated")
        return {
            "id": track_id,
            "title": "Track preview",
            "artist": "Amazon Test Artist",
            "duration_ms": 212000,
            "available": True,
            "stream_url": self.build_stream_url(track_id),
        }

    async def get_album(self, album_id: str) -> dict[str, Any]:
        """Return a mock album payload."""
        if not self.is_configured():
            raise ValueError("client is not authenticated")
        return {
            "id": album_id,
            "title": "Album preview",
            "artist": "Amazon Test Artist",
            "tracks": [
                {"id": f"{album_id}-track-1", "title": "Track 1", "duration_ms": 200000},
                {"id": f"{album_id}-track-2", "title": "Track 2", "duration_ms": 210000},
            ],
        }

    async def get_playlist(self, playlist_id: str) -> dict[str, Any]:
        """Return a mock playlist payload."""
        if not self.is_configured():
            raise ValueError("client is not authenticated")
        return {
            "id": playlist_id,
            "name": "Playlist preview",
            "tracks": [
                {"id": f"{playlist_id}-track-1", "title": "Playlist Track 1"},
                {"id": f"{playlist_id}-track-2", "title": "Playlist Track 2"},
            ],
        }

    def build_stream_url(self, track_id: str) -> str:
        """Generate a valid-looking placeholder URL. This must never be treated as a real Amazon stream."""
        if not track_id:
            raise ValueError("track_id is required")
        return f"https://example.invalid/amazon-music/stream/{track_id}?region={self.region}"

    def validate_stream_url(self, url: str) -> bool:
        """Validate the syntax of a stream URL without assuming it is authorized by Amazon."""
        return bool(url) and url.startswith("http://") or url.startswith("https://")

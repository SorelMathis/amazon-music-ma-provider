"""Core model objects used by the local provider scaffold."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AmazonArtist:
    item_id: str
    name: str
    genres: list[str] = field(default_factory=list)


@dataclass
class AmazonAlbum:
    item_id: str
    title: str
    artist: str
    artwork_url: str | None = None
    tracks: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class AmazonPlaylist:
    item_id: str
    name: str
    owner: str | None = None
    tracks: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class AmazonTrack:
    item_id: str
    title: str
    artist: str
    album: str | None = None
    duration_ms: int = 0
    stream_url: str | None = None
    available: bool = True

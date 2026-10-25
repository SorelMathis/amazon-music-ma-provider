"""Compatibility wrapper for a Music Assistant-like provider discovery runtime."""

from __future__ import annotations

from typing import Any

from amazon_music_ma_provider.provider import AmazonMusicProvider


def setup(mass: Any, manifest: dict[str, Any], config: dict[str, Any]) -> AmazonMusicProvider:
    """Return the local scaffold instance used by a MA-like runtime."""
    return AmazonMusicProvider()

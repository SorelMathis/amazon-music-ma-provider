"""Compatibility facade for custom Music Assistant provider discovery."""

from __future__ import annotations

from typing import Any

from .provider import AmazonMusicProvider


def setup(mass: Any, manifest: dict[str, Any], config: dict[str, Any]) -> AmazonMusicProvider:
    """Return the provider instance used by a MA-like runtime.

    This function intentionally remains independent from the official Music Assistant package so the
    project can be developed and tested without modifying the running Docker installation.
    """
    return AmazonMusicProvider()

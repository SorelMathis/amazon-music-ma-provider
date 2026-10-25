"""Tests for the Amazon Music development scaffold.

These tests validate the contract and the security layers without pretending that Amazon access is
available or real.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from amazon_music_ma_provider.auth import AmazonAuthError, AmazonMusicAuthenticator, TokenBundle
from amazon_music_ma_provider.client import AmazonMusicClient
from amazon_music_ma_provider.config import ProviderSettings
from amazon_music_ma_provider.provider import AmazonMusicProvider


@pytest.mark.asyncio
async def test_auth_rejects_bad_credentials() -> None:
    auth = AmazonMusicAuthenticator(ProviderSettings())
    with pytest.raises(AmazonAuthError):
        auth.validate_credentials("", "secret")
    with pytest.raises(AmazonAuthError):
        auth.validate_credentials("ab", "secret")


@pytest.mark.asyncio
async def test_auth_creates_session_and_marks_mock_source() -> None:
    auth = AmazonMusicAuthenticator(ProviderSettings(region="fr"))
    session = auth.create_mock_session("user@example.com", "password")
    assert session.source == "mock"
    assert session.region == "fr"
    assert not session.is_expired()


@pytest.mark.asyncio
async def test_expired_session_is_detected() -> None:
    expired = TokenBundle(
        access_token="expired-token",
        refresh_token="expired-refresh",
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
        source="mock",
    )
    assert expired.is_expired() is True


@pytest.mark.asyncio
async def test_client_search_works_when_configured() -> None:
    client = AmazonMusicClient(access_token="demo-token", region="fr")
    results = await client.search("queen", ("track", "album"), limit=2)
    assert "track" in results
    assert "album" in results
    assert len(results["track"]) == 2
    assert all(result.item_type == "track" for result in results["track"])


@pytest.mark.asyncio
async def test_stream_url_validation_rejects_realistic_but_invalid_urls() -> None:
    client = AmazonMusicClient(access_token="demo-token", region="fr")
    assert client.validate_stream_url("https://example.invalid/path", allow_mock=False) is False
    assert client.validate_stream_url("https://amazon.example.com/stream", allow_mock=False) is True
    assert client.validate_stream_url("mock://amazon-music.local/stream/abc", allow_mock=True) is True
    assert client.validate_stream_url("mock://amazon-music.local/stream/abc", allow_mock=False) is False


@pytest.mark.asyncio
async def test_provider_requires_authentication_before_search() -> None:
    provider = AmazonMusicProvider(ProviderSettings())
    with pytest.raises(AmazonAuthError):
        await provider.search("queen")


@pytest.mark.asyncio
async def test_provider_stream_details_are_generated_only_for_authenticated_session() -> None:
    provider = AmazonMusicProvider(ProviderSettings(region="fr"))
    provider.client.access_token = "demo-token"
    stream = provider.get_stream_details("track-42")
    assert stream["track_id"] == "track-42"
    assert stream["is_valid"] is True
    assert stream["source"] == "mock"
    assert stream["stream_url"].startswith("mock://")


@pytest.mark.asyncio
async def test_provider_can_restore_and_clear_session() -> None:
    provider = AmazonMusicProvider(ProviderSettings())
    provider.client.access_token = "demo-token"
    assert provider.client.is_configured() is True
    provider.clear_session()
    assert provider.client.access_token is None

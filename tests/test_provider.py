"""Tests for the local Amazon Music provider scaffold."""

from __future__ import annotations

import pytest

from amazon_music_ma_provider.auth import AmazonAuthError, AmazonMusicAuthenticator
from amazon_music_ma_provider.client import AmazonMusicClient
from amazon_music_ma_provider.config import ProviderSettings
from amazon_music_ma_provider.provider import AmazonMusicProvider


@pytest.mark.asyncio
async def test_auth_rejects_bad_credentials() -> None:
    authenticator = AmazonMusicAuthenticator(ProviderSettings())
    with pytest.raises(AmazonAuthError):
        authenticator.validate_credentials("", "secret")
    with pytest.raises(AmazonAuthError):
        authenticator.validate_credentials("ab", "secret")


@pytest.mark.asyncio
async def test_auth_creates_session() -> None:
    authenticator = AmazonMusicAuthenticator(ProviderSettings())
    session = authenticator.create_mock_session("user@example.com", "password")
    assert session.access_token.startswith("mock")
    assert session.region == "fr"


@pytest.mark.asyncio
async def test_client_search_works_when_configured() -> None:
    client = AmazonMusicClient(access_token="demo-token", region="fr")
    results = await client.search("queen", ("track", "album"), limit=2)
    assert "track" in results
    assert "album" in results
    assert len(results["track"]) == 2
    assert all(result.item_type == "track" for result in results["track"])


@pytest.mark.asyncio
async def test_provider_stream_details_are_generated() -> None:
    provider = AmazonMusicProvider(ProviderSettings(region="fr"))
    provider.client.access_token = "demo-token"
    stream = provider.get_stream_details("track-42")
    assert stream["track_id"] == "track-42"
    assert stream["is_valid"] is True
    assert stream["stream_url"].startswith("https://")


@pytest.mark.asyncio
async def test_provider_requires_authentication_before_search() -> None:
    provider = AmazonMusicProvider(ProviderSettings())
    with pytest.raises(AmazonAuthError):
        await provider.search("queen")


@pytest.mark.asyncio
async def test_provider_can_restore_and_clear_session() -> None:
    provider = AmazonMusicProvider(ProviderSettings())
    provider.client.access_token = "demo-token"
    assert provider.client.is_configured() is True
    provider.clear_session()
    assert provider.client.access_token is None

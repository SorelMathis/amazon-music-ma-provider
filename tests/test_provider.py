"""Provider tests for the Amazon Music development scaffold.

These tests validate the contract and the security layers without pretending Amazon access is
available or real.
"""

from __future__ import annotations

import importlib
from datetime import datetime, timedelta, timezone

import pytest

from amazon_music_ma_provider.auth import (
    AmazonAuthError,
    AmazonMusicAuthenticator,
    TokenBundle,
)
from amazon_music_ma_provider.client import AmazonMusicClient
from amazon_music_ma_provider.config import ProviderSettings, SecureSecretStore
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
async def test_corrupt_session_is_rejected() -> None:
    store = SecureSecretStore("amazon-music-ma-provider-test")
    store.store_secret("session_metadata", "{not-json")
    auth = AmazonMusicAuthenticator(ProviderSettings())
    auth.store = store
    assert auth.load_session() is None


@pytest.mark.asyncio
async def test_client_search_works_when_configured() -> None:
    client = AmazonMusicClient(access_token="demo-token", region="fr")
    results = await client.search("queen", ("track", "album"), limit=2)
    assert "track" in results
    assert "album" in results
    assert len(results["track"]) == 2
    assert all(result.item_type == "track" for result in results["track"])


@pytest.mark.asyncio
async def test_stream_url_validation_rejects_fake_domains_and_requires_explicit_allowlist() -> None:
    client = AmazonMusicClient(access_token="demo-token", region="fr")
    real_allowed = ("music.amazon.com", "music.amazon.fr")

    assert client.validate_stream_url("https://example.invalid/path", allow_mock=False, allowed_hosts=real_allowed) is False
    assert client.validate_stream_url("https://amazon.example.com/stream", allow_mock=False, allowed_hosts=real_allowed) is False
    assert client.validate_stream_url("https://music.amazon.com.evil.dev/stream", allow_mock=False, allowed_hosts=real_allowed) is False
    assert client.validate_stream_url("https://music.amazon.com@evil.example/stream", allow_mock=False, allowed_hosts=real_allowed) is False
    assert client.validate_stream_url("https://music.amazon.com/stream", allow_mock=False, allowed_hosts=real_allowed) is True
    assert client.validate_stream_url("https://music.amazon.com.evil.dev/stream", allow_mock=False) is False


@pytest.mark.asyncio
async def test_mock_stream_url_requires_mock_mode() -> None:
    client = AmazonMusicClient(access_token="demo-token", region="fr")
    assert client.validate_stream_url("mock://amazon-music.local/stream/abc", allow_mock=True) is True
    assert client.validate_stream_url("mock://amazon-music.local/stream/abc", allow_mock=False) is False


@pytest.mark.asyncio
async def test_provider_requires_authentication_before_search() -> None:
    provider = AmazonMusicProvider(ProviderSettings())
    with pytest.raises(AmazonAuthError):
        await provider.search("queen")


@pytest.mark.asyncio
async def test_provider_stream_details_are_generated_only_for_authenticated_session() -> None:
    provider = AmazonMusicProvider(ProviderSettings(region="fr", enable_mock_mode=True))
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


@pytest.mark.asyncio
async def test_provider_import_and_setup_function_work() -> None:
    module = importlib.import_module("custom_providers.amazon_music")
    setup_result = module.setup(mass=None, manifest={"domain": "amazon_music"}, config={})
    assert isinstance(setup_result, AmazonMusicProvider)


@pytest.mark.asyncio
async def test_secret_store_round_trip_and_cleanup() -> None:
    store = SecureSecretStore("amazon-music-ma-provider-test")
    store.store_secret("api_key", "secret")
    assert store.read_secret("api_key") == "secret"
    store.delete_secret("api_key")
    assert store.read_secret("api_key") is None

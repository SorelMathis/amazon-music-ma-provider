"""Public package exports for the Amazon Music provider scaffold."""

from .auth import AmazonAuthError, AmazonMusicAuthenticator, TokenBundle
from .client import AmazonMusicClient, SearchQuery, SearchResult
from .config import ProviderSettings, get_secure_storage_path, load_settings, save_settings
from .models import AmazonAlbum, AmazonArtist, AmazonPlaylist, AmazonTrack
from .provider import AmazonMusicProvider

__all__ = [
    "AmazonAlbum",
    "AmazonArtist",
    "AmazonAuthError",
    "AmazonMusicAuthenticator",
    "AmazonMusicClient",
    "AmazonMusicProvider",
    "AmazonPlaylist",
    "AmazonTrack",
    "ProviderSettings",
    "SearchQuery",
    "SearchResult",
    "TokenBundle",
    "get_secure_storage_path",
    "load_settings",
    "save_settings",
]

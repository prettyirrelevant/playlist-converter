import json

from django.conf import settings
from redis import StrictRedis
from spotipy import Spotify as _Spotify
from spotipy import SpotifyClientCredentials
from spotipy.cache_handler import CacheHandler
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOAuth
from ytmusicapi import YTMusic as _YTMusic

# TODO: Add logging

redis = StrictRedis.from_url(settings.REDIS_URL)


class RedisCacheHandler(CacheHandler):
    def __init__(self):
        self.r = redis

    def get_cached_token(self):
        token_info = None
        try:
            token_info = json.loads(self.r.get("token"))
        except:
            pass

        return token_info

    def save_token_to_cache(self, token_info):
        try:
            self.r.set("token", json.dumps(token_info))
        except:
            pass


class Spotify:
    def __init__(self) -> None:
        sp_client_manager = SpotifyClientCredentials()
        self.sp_oauth_manager = SpotifyOAuth(
            scope="playlist-modify-public", cache_handler=RedisCacheHandler()
        )
        self.sp = _Spotify(
            client_credentials_manager=sp_client_manager, oauth_manager=self.sp_oauth_manager
        )

    def from_ytmusic(self, playlist_id, title):
        """Converts a YTMusic playlist to a Spotify's."""
        tracks = ytmusic.songs_tracks(playlist_id)
        songs_uris = self.songs_uris(tracks)
        playlist = self.create_playlist(title, songs_uris)

        return playlist

    def create_playlist(self, title, songs_uris):
        """Create a Spotify playlist."""
        try:
            user_id = self.me()["id"]
            response = self.sp.user_playlist_create(
                user_id,
                title,
                description="Created using PlaylistConverter.",
            )

            self.sp.playlist_add_items(response["id"], songs_uris)
            playlist = self.sp.playlist(response["id"])
            return playlist
        except:
            raise Exception("Unable to create Spotify playlist.")

    def songs_tracks(self, playlist_id):
        """Get songs contained in a Spotify playlist."""
        try:
            spotify_tracks = self.sp.playlist_items(playlist_id)["items"]
        except SpotifyException:
            raise Exception("Could not find spotify playlist.")

        tracks = []
        for track in spotify_tracks:
            tracks.append(
                {
                    "title": track["track"]["name"],
                    "artists": [artist["name"] for artist in track["track"]["artists"]],
                }
            )
        return tracks

    def songs_uris(self, tracks):
        """Search for songs using title and artist(s) and return uris."""
        songs_id = []
        try:
            for track in tracks:
                artist = " ".join(track["artists"])
                search_results = self.sp.search(
                    q=f"{track['title']} {artist}",
                    limit=1,
                    type="track",
                )
                try:
                    songs_id.append(search_results["tracks"]["items"][0]["uri"])
                except IndexError:
                    pass
            return songs_id
        except:
            raise Exception("Error while searching for songs on YTMusic.")

        return songs_id

    def get_authorize_url(self):
        return self.sp_oauth_manager.get_authorize_url()

    def get_access_token(self, code):
        """Get access token from authorization code."""
        return self.sp_oauth_manager.get_access_token(code)

    def me(self):
        """Get the current user."""
        return self.sp.me()


class YTMusic:
    def __init__(self) -> None:
        self.ytmusic = _YTMusic(settings.BASE_DIR / "headers.json")

    def from_spotify(self, playlist_id, title):
        """Converts a Spotify playlist to YTMusic's."""
        tracks = spotify.songs_tracks(playlist_id)
        songs_ids = self.songs_ids(tracks)

        yt_playlist_id = self.create_playlist(title, songs_ids)
        playlist = self.playlist(yt_playlist_id)

        return playlist

    def create_playlist(self, title, songs_ids):
        """Create a YTMusic playlist."""
        try:
            response = self.ytmusic.create_playlist(
                title,
                description="Created using PlaylistConverter.",
                privacy_status="PUBLIC",
                video_ids=songs_ids,
            )
            print(response)
            return response
        except:
            raise Exception("Unable to create YTMusic playlist.")

    def playlist(self, playlist_id):
        """Returns YTMusic playlist data."""
        try:
            playlist = self.ytmusic.get_playlist(playlist_id)
            return playlist
        except:
            raise Exception("Unable to get YTMusic playlist.")

    def songs_tracks(self, playlist_id):
        """Get songs contained in a playlist."""
        try:
            ytmusic_tracks = self.ytmusic.get_playlist(playlist_id)["tracks"]
        except:
            raise Exception("Could not find YTMusic playlist.")

        tracks = []
        for track in ytmusic_tracks:
            tracks.append(
                {
                    "title": track["title"],
                    "artists": [artist["name"] for artist in track["artists"]],
                }
            )
        return tracks

    def songs_ids(self, tracks):
        """Search for songs using title and artist(s) and return ids."""
        songs_id = []

        try:
            for track in tracks:
                artist = " ".join(track["artists"])
                search_results = self.ytmusic.search(
                    query=f"{track['title']} by {artist}",
                    filter="songs",
                    limit=5,
                )
                songs_id.append(search_results[0].get("videoId"))
            return songs_id
        except:
            raise Exception("Error while searching for songs on YTMusic.")


ytmusic = YTMusic()
spotify = Spotify()

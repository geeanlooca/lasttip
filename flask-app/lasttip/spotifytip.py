import lasttip.spotify
from lasttip.recommender import AlbumSuggestion
from lasttip.recommender import Recommender
import random
import datetime


class SpotifyTip(Recommender):
    def __init__(self, spotify: lasttip.spotify.Spotify):
        self.spotify = spotify
        self._last_refresh = None
        self._total_albums = None

    def _find_max_albums(self) -> int:
        now = datetime.datetime.now()
        if self._last_refresh is None or (now - self._last_refresh).hours() > 1:
            albums = self.spotify.current_user_saved_albums(limit=1, offset=0)
            self._total_albums = albums["total"]
        return self._total_albums

    def _get_random_album(self):
        total_albums = self._find_max_albums()
        random_num = random.randint(0, total_albums - 1)
        album = self.spotify.current_user_saved_albums(limit=1, offset=random_num)[
            "items"
        ][0]["album"]
        return album

    def get_suggestion(self) -> AlbumSuggestion:
        album = self._get_random_album()

        artist_url = album["artists"][0]["external_urls"]["spotify"]
        artist_name = album["artists"][0]["name"]
        image_url = album["images"][0]["url"]
        album_url = album["external_urls"]["spotify"]

        suggestion = AlbumSuggestion(
            album_name=album["name"],
            album_artist=artist_name,
            url=album_url,
            image=image_url,
            spotify_data=None,
            artist_url=artist_url,
            playcount=None,
        )

        return suggestion

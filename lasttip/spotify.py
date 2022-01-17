from pprint import pprint
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json


class Spotify:
    def __init__(self, id, secret):
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(client_id=id, client_secret=secret)
        )

    def get_artist_uris(self, artist_string: str):
        results = self.sp.search(q=artist_string, type="artist")

        return [(item["name"], item["uri"]) for item in results["artists"]["items"]]

    def get_artist_album(self, artisti_uri: str):
        results = self.sp.artist_albums(artisti_uri, album_type="album")

        return [
            (item["name"], item["external_urls"]["spotify"])
            for item in results["items"]
        ]

    def search(self, query, **kwargs):
        return self.sp.search(q=query, **kwargs)

    def get_album_url(self, album_data):
        return album_data["external_urls"]["spotify"]

    def get_album_image(self, album_data):
        return album_data["images"][0]["url"]

    def get_album_data(self, album_string: str, limit: int = 5):
        results = self.sp.search(q=album_string, limit=limit)

        with open("spotify_result.json", "w") as f:
            json.dump(results, f)

        album = results["tracks"]["items"][0]["album"]
        return album

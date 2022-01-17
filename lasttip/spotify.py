import requests

import spotipy
import pprint
from spotipy.oauth2 import SpotifyClientCredentials
import json

import os

SPOTIFY_CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]


class Spotify:
    def __init__(self):
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET
            )
        )

    def search(self, query, limit=5):
        return self.sp.search(q=query, limit=limit)


    def get_url(self, album_string: str, limit: int = 5):
        results = self.sp.search(q=album_string, limit=limit)

        with open("spotify_result.json", "w") as f:
            json.dump(results, f)

        album = results["tracks"]["items"][0]["album"]["external_urls"]["spotify"]
        return album


if __name__ == "__main__":
    sp = Spotify()
    print(sp.get_url("Geogaddi Boards of Canada"))
    print(sp.get_url("LONG.LIVE.A$AP Deluxe Version A$AP ROCKY"))

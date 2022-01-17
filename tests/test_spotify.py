import os
import json
import lasttip.spotify
import lasttip.telegram_bot
from pprint import pprint
import pytest
import telegram
import telegram.ext


from dotenv import load_dotenv

load_dotenv()

DEBUG_TOKEN = os.environ["BOT_TOKEN_DEBUG"]
DEBUG_CHAT_ID = os.environ["DEBUG_CHAT_ID"]

ID = os.environ["SPOTIFY_CLIENT_ID"]
SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]


sp = lasttip.spotify.Spotify(ID, SECRET)


def test_spotify_artist_search():
    artist = "Mark Kozelek & Jimmy Lavalle"
    pprint(sp.get_artist_uris(artist))


@pytest.mark.parametrize("artist", ["Aphex Twin"])
def test_spotify_album_artist(artist):

    for (name, uri) in sp.get_artist_uris(artist):
        results = sp.sp.artist_albums(uri, album_type="album")
        for item in results["items"]:
            pprint(item["external_urls"])

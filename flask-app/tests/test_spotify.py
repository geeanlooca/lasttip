import os
import json
from lasttip.spotify import Spotify
from pprint import pprint
import pytest

from dotenv import load_dotenv

load_dotenv()

ID = os.environ["SPOTIFY_CLIENT_ID"]
SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]

sp = Spotify(ID, SECRET)


def test_spotify_artist_search():
    artist = "Mark Kozelek & Jimmy Lavalle"
    uris = sp.get_artist_uris(artist)
    pprint(uris)

    artist_name = {name for (name, uri) in uris}

    assert "Red House Painters" in artist_name
    assert "Sun Kil Moon" in artist_name
    assert "Mark Kozelek" in artist_name


@pytest.mark.parametrize("artist", ["Aphex Twin"])
def test_spotify_album_artist(artist):
    for name, uri in sp.get_artist_uris(artist):
        results = sp.sp.artist_albums(uri, album_type="album")
        for item in results["items"]:
            pprint(item["external_urls"])

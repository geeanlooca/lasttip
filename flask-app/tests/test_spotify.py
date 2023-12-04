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


def test_spotify_search():
    inputs = """Photek - Form & Function
    Black Sabbath - Vol.4 
    Fischerspooner - #1
    Ricardo Villalobos - Sei Es Drum
    Right Away, Great Captain! - The Church Of The Good Thief
    Nirvana Bleach
    Grateful Dead  The Grateful Dead
    Metal Box - Public Image Ltd.
    Within and Without Washed Out
    Schacke  A Lot Of Chaos
    CCCP Fedeli alla linea Affinità e Divertenze fra il compagno Togliatti e noi del conseguimento della maggiore età"""

    for num, line in enumerate(inputs.splitlines()):
        query = line.strip().replace("-", " ")
        response = sp.search(query, type="album")

        with open(f"test_spotify_search_response_{num}.json", "w") as f:
            pprint(response, f)

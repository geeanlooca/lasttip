import lasttip.similarity
import os
import json
from lasttip.spotify import Spotify
from lasttip.spotify import get_best_album_match

from dotenv import load_dotenv

load_dotenv()

ID = os.environ["SPOTIFY_CLIENT_ID"]
SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]

sp = Spotify(ID, SECRET)


def test_query():
    spotify_query = "Ø Konstellaatio"
    album = lasttip.lastfm.Album("Konstellaatio", "Ø", 10, "", None)

    with open("tests/spotify_response_similarity_crash.json", "r") as f:
        search_result = json.load(f)

    search_result["query"] = spotify_query
    album_data, score = get_best_album_match(search_result, album)


def test_single_char():
    lasttip.similarity.string_similarity("a", "a")

import os
import pytest
from lasttip.lastfm import LastFm
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def lastfm() -> LastFm:
    return LastFm.from_env()


def test_lastfm_api(lastfm: LastFm):
    albums = lastfm.get_top_albums(limit=10).albums
    assert len(albums) == 10
    for album in albums:
        print(f"{album.name} by {album.artist} ({album.playcount} plays)")

import pytest
from lasttip.lastfm import LastFm
from dotenv import load_dotenv
from pprint import pprint
import json

load_dotenv()


@pytest.fixture
def lastfm() -> LastFm:
    return LastFm.from_env()


def test_lastfm_api(lastfm: LastFm):
    albums = lastfm.get_top_albums(limit=10).albums
    assert len(albums) == 10
    for album in albums:
        print(f"{album.name} by {album.artist} ({album.playcount} plays)")


def test_lastm_api_response(lastfm: LastFm):
    url = lastfm._build_api_url()
    json = lastfm._send_api_request(url)
    with open("request_response.json", "w") as f:
        pprint(json, f)


def test_extract_image_url(lastfm: LastFm):
    data_str_ok = """{"image": [{"#text": "https://lastfm.freetls.fastly.net/i/u/34s/0c6c868b77a4417f937cf09506099081.png",
                                     "size": "small"},
                                    {"#text": "https://lastfm.freetls.fastly.net/i/u/64s/0c6c868b77a4417f937cf09506099081.png",
                                     "size": "medium"},
                                    {"#text": "https://lastfm.freetls.fastly.net/i/u/174s/0c6c868b77a4417f937cf09506099081.png",
                                     "size": "large"},
                                    {"#text": "https://lastfm.freetls.fastly.net/i/u/300x300/0c6c868b77a4417f937cf09506099081.png",
                                     "size": "extralarge"}]}"""

    json_data_ok = json.loads(data_str_ok)
    url = lastfm._extract_album_image_url(json_data_ok["image"])

    assert (
        url
        == "https://lastfm.freetls.fastly.net/i/u/300x300/0c6c868b77a4417f937cf09506099081.png"
    )

    data_str_not_ok = """{"image": [{"#text": "", "size": "small"},
                                    {"#text": "", "size": "medium"},
                                    {"#text": "", "size": "large"},
                                    {"#text": "", "size": "extralarge"}]}"""
    json_data_not_ok = json.loads(data_str_not_ok)
    pprint(json_data_not_ok)
    url = lastfm._extract_album_image_url(json_data_not_ok["image"])
    assert not url

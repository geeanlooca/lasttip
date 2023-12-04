import os
import logging
import pprint
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import lasttip.lastfm
from dataclasses import dataclass
from typing import Dict
from abc import ABC, abstractmethod
import lasttip.similarity

SIMILARITY_SCORE_THRESHOLD = 0.7

logging.basicConfig(
    format="%(asctime)s - %(name)s %(funcName)s - %(levelname)s - %(message)s",
    level=logging.WARN,
)
logger = logging.getLogger(__name__)


@dataclass
class SpotifyAlbumInfo:
    album_url: str
    artist_url: str
    image_url: str
    search_data: Dict[str, str]
    uri: str


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

    def get_album_data(self, album_string: str, limit: int = 5):
        results = self.sp.search(q=album_string, limit=limit, type="album")

        with open("spotify_result.json", "w") as f:
            json.dump(results, f)

        album = results["albums"]["items"][0]

        album_info = pprint.pformat(album)
        logger.warn(f"Query = {album_string} => {album_info}")
        return album

    @staticmethod
    def from_env():
        SPOTIFY_CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
        SPOTIFY_CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
        spotify = Spotify(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
        return spotify


class SpotifyQueryStrategy(ABC):
    @abstractmethod
    def query(self, spotify: Spotify, album: lasttip.lastfm.Album) -> SpotifyAlbumInfo:
        pass


def get_best_album_match(response: dict, album: lasttip.lastfm.Album):
    albums = response["albums"]["items"]

    def compute_score(found_album):
        found_artist = found_album["artists"][0]["name"]
        found_album = found_album["name"]

        artist_score = lasttip.similarity.string_similarity(album.artist, found_artist)
        album_score = lasttip.similarity.string_similarity(album.name, found_album)
        score = 0.4 * artist_score + 0.6 * album_score
        return score

    scores = [compute_score(album_) for album_ in albums]

    logger.warn(f"Finding best match for {album.artist} - {album.name}")
    for album_, score in zip(albums, scores):
        logger.warn(f"{album_['name']} - {album_['artists'][0]['name']} => {score}")

    max_score = max(scores)
    max_index = scores.index(max_score)
    return albums[max_index], max_score


class BasicSpotifyQuery(SpotifyQueryStrategy):
    def query(self, spotify: Spotify, album: lasttip.lastfm.Album) -> SpotifyAlbumInfo:
        spotify_query = album.artist + " " + album.name
        search_result = spotify.search(spotify_query, type="album")

        search_result["query"] = spotify_query
        # save the search result to a file
        with open("spotify_search_result.json", "w") as f:
            json.dump(search_result, f)

        album_data, score = get_best_album_match(search_result, album)

        if score < SIMILARITY_SCORE_THRESHOLD:
            return SpotifyAlbumInfo(
                album_url=None,
                image_url=album.image_url,
                search_data=album_data,
                artist_url=None,
                uri=None,
            )

        if album.image_url:
            image = album.image_url
        else:
            image = album_data["images"][0]["url"]

        artist_url = album_data["artists"][0]["external_urls"]["spotify"]
        url = album_data["external_urls"]["spotify"]
        uri = album_data["uri"]

        return SpotifyAlbumInfo(
            album_url=url,
            image_url=image,
            search_data=album_data,
            artist_url=artist_url,
            uri=uri,
        )

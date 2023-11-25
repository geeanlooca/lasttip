import logging
import random
import requests
from dataclasses import dataclass
import shelve
from typing import List


logging.basicConfig(
    format="%(asctime)s - %(name)s %(funcName)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)


@dataclass
class Album:
    "Class for storing album data"
    name: str
    artist: str
    playcount: int

    def __str__(self):
        return f"{self.artist} - {self.name} (played {self.playcount} times)"


@dataclass
class TopAlbums:
    """Class for fetching top albums from Last.fm"""

    albums: List[Album]
    metadata: dict


class LastFm:
    def __init__(self, user, key, secret):
        self.url = "https://ws.audioscrobbler.com/2.0/"
        self.user = user
        self.key = key
        self.secret = secret
        self.fetch(playcount_min=10)

    def fetch(self, playcount_min=None, clear_cache=False):
        with shelve.open("cache.shelve") as d:
            if "albums" in d:
                logger.debug("Cached result found")
                albums = d["albums"]
            else:
                logger.debug("Cached result not found, fetching data from API")
                albums = self.get_all_albums(playcount_min=playcount_min).albums
                d["albums"] = albums

        return albums

    def cached(self):
        with shelve.open("cache.shelve") as d:
            return "albums" in d

    def clear_cache(self):
        logger.debug("Clearing cache")
        with shelve.open("cache.shelve") as d:
            if "albums" in d:
                del d["albums"]

    def get_all_albums(self, limit=250, playcount_min=None) -> TopAlbums:
        logger.debug("Retrieving all albums")

        first_page = self.get_top_albums(limit=limit)

        albums = first_page.albums
        info = first_page.metadata

        total_pages = int(info["totalPages"])
        logger.debug(f"{total_pages} pages to download")

        for i in range(2, total_pages + 1):
            logger.debug(f"Retrieving page {i}/{total_pages}")
            album_page = self.get_top_albums(limit=limit, page=i)

            albums.extend(album_page.albums)

            if playcount_min:
                album_least_plays = album_page.albums[-1]
                logger.debug(
                    f"Playcount of the last album: {album_least_plays.playcount}"
                )
                if album_least_plays.playcount < playcount_min:
                    logger.debug("Stopping due to playcount limit")
                    break

        return TopAlbums(albums=albums, metadata=info)

    def get_top_albums(self, page: int = 1, limit: int = 250) -> TopAlbums:
        method_string = f"?method=user.gettopalbums&user={self.user}&api_key={self.key}&format=json&page={page}&limit={limit}"
        request_url = self.url + method_string

        logger.debug(request_url)

        response = requests.get(request_url)

        json = response.json()

        try:
            data = json["topalbums"]["album"]
            metadata = json["topalbums"]["@attr"]
            albums = []
            for album_data in data:
                artist_name = album_data["artist"]["name"]
                album_name = album_data["name"]
                playcount = int(album_data["playcount"])
                album = Album(name=album_name, artist=artist_name, playcount=playcount)
                albums.append(album)
            return TopAlbums(albums=albums, metadata=metadata)

        except KeyError as e:
            logger.error(f"KeyError: {e}")
            logger.error(json)

    def pick_random(self, playcount_max=None, playcount_min=None) -> Album:
        albums = self.fetch(playcount_min=playcount_min)
        random_album = random.choice(albums)

        if playcount_max:
            albums = list(filter(lambda x: x.playcount < playcount_max, albums))

        if playcount_min:
            albums = list(filter(lambda x: x.playcount > playcount_min, albums))

        try:
            album = random.choice(albums)
            return album
        except IndexError:
            return random_album

    def from_env():
        import os

        LASTFM_USER = os.environ["LASTFM_USER"]
        API_KEY = os.environ["LASTFM_API_KEY"]
        API_SECRET = os.environ["LASTFM_SHARED_SECRET"]
        return LastFm(LASTFM_USER, API_KEY, API_SECRET)

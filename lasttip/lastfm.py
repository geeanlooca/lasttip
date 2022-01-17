import os
import argparse
import logging
import random
import requests
from dataclasses import dataclass
import shelve


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
        return f"{self.artist} - {self.name}"


class LastFm:
    def __init__(self, user, secret, key):
        self.url = "https://ws.audioscrobbler.com/2.0/"
        self.user = user
        self.key = key
        self.secret = secret

    def fetch(self, playcount_min=None, clear_cache=False):

        with shelve.open("cache.shelve") as d:
            if "albums" in d:
                logger.debug("Cached result found")
                albums = d["albums"]
            else:
                logger.debug("Cached result not found, fetching data from API")
                albums = self.get_all_albums(playcount_min=playcount_min)
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

    def get_all_albums(self, limit=250, playcount_min=None):

        logger.debug("Retrieving all albums")
        albums, info = self.get_top_albums(limit=limit)

        total_pages = int(info["totalPages"])
        logger.debug(f"{total_pages} pages to download")

        for i in range(2, total_pages + 1):
            logger.debug(f"Retrieving page {i}/{total_pages}")
            album_page, info = self.get_top_albums(limit=limit, page=i)

            albums.extend(album_page)

            if playcount_min:
                logger.debug(f"Playcount of the last album: {album_page[-1].playcount}")
                if album_page[-1].playcount < playcount_min:
                    logger.debug("Stopping due to playcount limit")
                    break

        return albums

    def get_top_albums(self, page=1, limit=250):
        method_string = f"?method=user.gettopalbums&user={self.user}&api_key={self.key}&format=json&page={page}&limit={limit}"
        request_url = self.url + method_string

        logger.debug(request_url)

        response = requests.get(request_url)

        json = response.json()

        data = json["topalbums"]["album"]
        metadata = json["topalbums"]["@attr"]

        albums = []
        for album_data in data:
            artist_name = album_data["artist"]["name"]
            album_name = album_data["name"]
            playcount = int(album_data["playcount"])
            album = Album(name=album_name, artist=artist_name, playcount=playcount)
            albums.append(album)
        return albums, metadata

    def pick_random(self, playcount_max=None, playcount_min=None):

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

import spotipy

from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheFileHandler
import random


cache_handler = CacheFileHandler(username="geeanlooca")
scope = "user-library-read"
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope=scope, cache_handler=cache_handler, open_browser=False
    )
)


def test_saved_albums():
    albums = sp.current_user_saved_albums(limit=1, offset=0)
    total_albums = albums["total"]

    # generate random number between 0 and total_albums
    # get album at that index

    random_num = random.randint(0, total_albums - 1)
    album = sp.current_user_saved_albums(limit=1, offset=random_num)["items"][0][
        "album"
    ]

    print("Random album: ", album["name"])

    # with open("saved_albums.json", "w") as f:
    #     json.dump(albums, f)

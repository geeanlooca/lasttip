import logging

from flask import Flask
from flask import render_template

from lasttip.lastfm import LastFm
from lasttip.spotify import Spotify
from lasttip.lasttip import LastTip

from pprint import pprint


HISTORY_CACHE_FILE = "history.shelve"

# Instantiate the main components
app = Flask(__name__)
lastfm = LastFm.from_env()
spotify = Spotify.from_env()
lasttip = LastTip(lastfm, spotify)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


@app.route("/")
def random():
    """Return a random album from Last.fm"""
    logging.log(logging.INFO, "Fetching random album")
    suggestion = lasttip.get_suggestion()

    # Render the template HTML with the album details
    return render_template(
        "album.html",
        album=suggestion.album,
        url=suggestion.url,
        image=suggestion.image,
    )


@app.route("/reset")
def reset():
    """Reset the cache"""
    logging.log(logging.INFO, "Clearing cache")
    lastfm.clear_cache()
    return random()

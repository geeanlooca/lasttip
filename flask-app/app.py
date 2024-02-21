import logging
import random

from flask import Flask, redirect
from flask import render_template
from flask import jsonify

from lasttip.lastfm import LastFm
from lasttip.spotify import Spotify
from lasttip.lasttip import LastTip
from lasttip.spotifytip import SpotifyTip
from lasttip.recommender import AlbumSuggestion
from render import render_suggestion


# Instantiate the main components
app = Flask(__name__)
lastfm = LastFm.from_env()
spotify = Spotify.from_env()
lasttip = LastTip(lastfm, spotify)
spotifytip = SpotifyTip(spotify)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


@app.route("/")
def index():
    """Return the index page"""
    # toin coss
    if random.randint(0, 1) == 0:
        return redirect("/spotify")
    else:
        return redirect("/lastfm")


@app.route("/json")
def index_json():
    # toin coss
    if random.randint(0, 1) == 0:
        return redirect("/spotify_json")
    else:
        return redirect("/lastfm_json")


@app.route("/lastfm_json")
def lastfm_json():
    """Return a random album from Last.fm"""
    logging.log(logging.INFO, "Fetching random album")
    suggestion = lasttip.get_suggestion()
    logging.log(logging.INFO, suggestion)
    return jsonify(suggestion)


@app.route("/spotify_json")
def spotify_json():
    """Return a random album from Spotify"""
    suggestion = spotifytip.get_suggestion()
    logging.log(logging.INFO, suggestion)
    return jsonify(suggestion)


@app.route("/lastfm")
def lastfm():
    """Return a random album from Last.fm"""
    logging.log(logging.INFO, "Fetching random album")
    suggestion = lasttip.get_suggestion()
    logging.log(logging.INFO, suggestion)

    # Render the template HTML with the album details
    return render_suggestion(suggestion)


@app.route("/spotify")
def spotify():
    """Return a random album from Spotify"""
    suggestion = spotifytip.get_suggestion()

    logging.log(logging.INFO, suggestion)

    # Render the template HTML with the album details
    return render_suggestion(suggestion)



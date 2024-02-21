from flask import render_template
from lasttip.recommender import AlbumSuggestion


def render_suggestion(suggestion: AlbumSuggestion) -> str:
    return render_template("album.html", suggestion=suggestion)

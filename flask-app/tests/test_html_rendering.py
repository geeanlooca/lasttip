from render import render_suggestion
import pytest
from lasttip.recommender import AlbumSuggestion
import json
import os

from flask import Flask, redirect
from flask import render_template
from flask import jsonify
from flask import template_rendered

@pytest.fixture
def null_artist_link_suggestion() -> AlbumSuggestion:

    # current path
    current_path = os.path.dirname(os.path.realpath(__file__))
    json_file = os.path.join(current_path, "empty_artist_link.json")

    assert os.path.exists(json_file), f"File does not exist: {json_file}"

    with open(json_file, "r") as f:
        response = json.load(f)
        return AlbumSuggestion(
            album_name=response["album_name"],
            album_artist=response["album_artist"],
            url=response["url"],
            image=response["image"],
            spotify_data=response["spotify_data"],
            artist_url=response["artist_url"],
            playcount=response["playcount"]
        )

@pytest.fixture
def app(null_artist_link_suggestion):
    """Create application for tests"""

    print("Creating app fixture")

    _app = Flask(__name__)

    @_app.route("/test")
    def test():
        rendered_response =  render_suggestion(null_artist_link_suggestion)
        return rendered_response

    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()

@pytest.fixture
def captured_templates(app):
    print("Creating captured_templates fixture")
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


def test_view(app, captured_templates):
    response = app.get("/test")
    print(captured_templates)
    print(response)



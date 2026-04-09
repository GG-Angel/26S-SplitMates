from flask import Blueprint, jsonify, current_app, redirect, url_for
from backend.simple.playlist import sample_playlist_data

# This blueprint handles basic routes useful for testing and demonstration
simple_routes = Blueprint("simple_routes", __name__)


# ------------------------------------------------------------
# / is the most basic route
# Once the api container is started, in a browser, go to
# localhost:4000/
@simple_routes.route("/")
def welcome():
    current_app.logger.info("GET / handler")
    return "<h1>Welcome to the CS 3200 Project Template REST API</h1>", 200


# ------------------------------------------------------------
# /playlist returns the sample playlist data contained in playlist.py
# (imported above)
@simple_routes.route("/playlist")
def get_playlist_data():
    current_app.logger.info("GET /playlist handler")
    return jsonify(sample_playlist_data), 200


# ------------------------------------------------------------
@simple_routes.route("/niceMessage", methods=["GET"])
def affirmation():
    current_app.logger.info("GET /niceMessage")
    message = """
    <h1>Think about it...</h1>
    <br />
    You only need to be 1% better today than you were yesterday!
    """
    return message, 200


# ------------------------------------------------------------
# Demonstrates how to redirect from one route to another.
# url_for() takes the blueprint name + function name as a string.
@simple_routes.route("/message")
def message():
    return redirect(url_for("simple_routes.affirmation"))


@simple_routes.route("/data")
def get_data():
    current_app.logger.info("GET /data handler")
    data = {"a": {"b": "123", "c": "Help"}, "z": {"b": "456", "c": "me"}}
    return jsonify(data), 200

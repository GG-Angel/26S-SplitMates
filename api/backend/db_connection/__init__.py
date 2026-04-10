# ------------------------------------------------------------
# This file manages the database connection for each request.
#
# get_db() returns a mysql.connector connection, creating one
# the first time it's called in a request and reusing it after.
#
# Flask's `g` object is a request-scoped store: anything placed
# in `g` lives for exactly one request and is cleaned up when
# the request ends. That cleanup is registered via init_app().
# ------------------------------------------------------------
import os
import mysql.connector
from flask import g, current_app


def get_db():
    if "db" not in g:
        g.db = mysql.connector.connect(
            host=current_app.config["MYSQL_DATABASE_HOST"],
            user=current_app.config["MYSQL_DATABASE_USER"],
            password=current_app.config["MYSQL_DATABASE_PASSWORD"],
            database=current_app.config["MYSQL_DATABASE_DB"],
            port=current_app.config["MYSQL_DATABASE_PORT"],
        )
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    # This registers close_db as a teardown function, meaning Flask will
    # call it automatically at the end of every request. There is no
    # connection setup here because get_db() opens the connection lazily —
    # only when a route actually needs it. init_app's only job is to make
    # sure the cleanup always happens, even if the route raises an exception.
    app.teardown_appcontext(close_db)


def load_query(filename: str):
    backend_dir = os.path.dirname(os.path.dirname(__file__))
    filepath = os.path.join(backend_dir, "queries", filename)
    with open(filepath, "r") as f:
        return f.read()

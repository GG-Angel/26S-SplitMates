from flask import Blueprint, current_app


group_routes = Blueprint("groups", __name__)


@group_routes.route("/")
def get_root():
    current_app.logger.info("GET /groups/ handler")
    return "<h1>Groups route</h1>"

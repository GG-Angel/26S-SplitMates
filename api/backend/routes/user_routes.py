from flask import Blueprint, current_app


user_routes = Blueprint("users", __name__)


@user_routes.route("/")
def get_root():
    current_app.logger.info("GET /users/ handler")
    return "<h1>Users route</h1>"

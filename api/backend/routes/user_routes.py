from flask import Blueprint, current_app, jsonify
from mysql.connector import Error
from backend.repositories.user_repository import UserRepository


user_routes = Blueprint("users", __name__)


@user_routes.route("/")
def handle_users() -> str:
    current_app.logger.info("GET /users/ handler")
    return "<h1>Users route</h1>"


@user_routes.route("/<user_id>", methods=["GET"])
def handle_user(user_id: int):
    repository = UserRepository()
    try:
        current_app.logger.info(f"GET /users/{user_id}")
        user = repository.get_user(user_id)

        # ensure user exists
        if not user:
            return jsonify({"error": "Not found"}), 404

        current_app.logger.info(f"Retrieved user {user_id}")
        return jsonify(user), 200

    except Error as e:
        current_app.logger.error(f"Database error in {handle_user.__name__}(): {e}")
        return jsonify({"error": "Unexpected error"}), 500


@user_routes.route("/<user_id>/groups", methods=["GET"])
def handle_user_groups(user_id: int):
    repository = UserRepository()
    try:
        current_app.logger.info(f"GET /users/{user_id}/groups")
        groups = repository.get_user_groups(user_id)
        return jsonify(groups), 200
    except Error as e:
        current_app.logger.error(
            f"Database error in {handle_user_groups.__name__}(): {e}"
        )
        return jsonify({"error": "Unexpected error"}), 500


@user_routes.route("/<user_id>/bills", methods=["GET"])
def handle_user_bills(user_id: int):
    repository = UserRepository()
    try:
        current_app.logger.info(f"GET /users/{user_id}/bills")
        bills = repository.get_user_bills(user_id)
        return jsonify(bills), 200
    except Error as e:
        current_app.logger.error(
            f"Database error in {handle_user_bills.__name__}(): {e}"
        )
        return jsonify({"error": "Unexpected error"}), 500


@user_routes.route("/<user_id>/chores", methods=["GET"])
def handle_user_chores(user_id: int):
    repository = UserRepository()
    try:
        current_app.logger.info(f"GET /users/{user_id}/chores")
        chores = repository.get_user_chores(user_id)
        return jsonify(chores), 200
    except Error as e:
        current_app.logger.error(
            f"Database error in {handle_user_chores.__name__}(): {e}"
        )
        return jsonify({"error": "Unexpected error"}), 500

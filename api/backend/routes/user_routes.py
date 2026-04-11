from flask import Blueprint, current_app, jsonify
from mysql.connector import Error
from backend.db_connection import get_db
from backend.repositories.user_repository import UserRepository


user_routes = Blueprint("users", __name__)


@user_routes.route("/")
def get_root() -> str:
    current_app.logger.info("GET /users/ handler")
    return "<h1>Users route</h1>"


@user_routes.route("/<user_id>", methods=["GET"])
def get_user_profile(user_id: int):
    cursor = get_db().cursor(dictionary=True)
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
        current_app.logger.error(f"Database error in get_user_profile(): {e}")
        return jsonify({"error": "Unexpected error"}), 500
    finally:
        cursor.close()

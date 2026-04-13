from flask import Blueprint, current_app, jsonify, request
from backend.decorators import handle_db_errors
from backend.repositories.user_repository import UserRepository


user_routes = Blueprint("users", __name__)


@user_routes.route("/<user_id>", methods=["GET"])
@handle_db_errors
def handle_user(user_id: int):
    repository = UserRepository()
    current_app.logger.info(f"GET /users/{user_id}")
    user = repository.get_user(user_id)

    # ensure user exists
    if not user:
        return jsonify({"error": "Not found"}), 404

    current_app.logger.info(f"Retrieved user {user_id}")
    return jsonify(user), 200


@user_routes.route("/<user_id>/groups", methods=["GET"])
@handle_db_errors
def handle_user_groups(user_id: int):
    repository = UserRepository()
    current_app.logger.info(f"GET /users/{user_id}/groups")
    groups = repository.get_user_groups(user_id)
    return jsonify(groups), 200


@user_routes.route("/<user_id>/bills/<bill_id>/pay", methods=["PUT"])
@handle_db_errors
def handle_bill_payment(user_id: int, bill_id: int):
    repository = UserRepository()
    current_app.logger.info(f"PUT /users/{user_id}/bills/{bill_id}/pay")
    repository.pay_bill(user_id, bill_id)
    return jsonify({"message": "Bill paid"}), 200


@user_routes.route("/<user_id>/chores", methods=["GET"])
@handle_db_errors
def handle_user_chores(user_id: int):
    repository = UserRepository()
    current_app.logger.info(f"GET /users/{user_id}/chores")
    chores = repository.get_user_chores(user_id)
    return jsonify(chores), 200


@user_routes.route("/<user_id>/invites", methods=["GET"])
@handle_db_errors
def handle_user_invites(user_id: int):
    repository = UserRepository()
    current_app.logger.info(f"GET /users/{user_id}/invites")
    pending_only = "pending" in request.args
    invites = repository.get_user_invites(user_id, pending_only)
    return jsonify(invites), 200

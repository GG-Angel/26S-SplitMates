import random
from flask import Blueprint, current_app, jsonify, request
from backend.decorators import handle_db_errors
from backend.repositories.group_repository import GroupRepository
from backend.repositories.user_repository import UserRepository


user_routes = Blueprint("users", __name__)


@user_routes.route("/<user_id>", methods=["GET", "DELETE"])
@handle_db_errors
def handle_user(user_id: int):
    user_repository = UserRepository()
    current_app.logger.info(f"{request.method} /users/{user_id}")

    user = user_repository.get_user(user_id)

    # ensure user exists
    if not user:
        return jsonify({"error": "Not found"}), 404

    if request.method == "GET":
        return jsonify(user), 200
    else:
        # transfer owned groups to a random member
        group_repository = GroupRepository()
        groups_led = group_repository.get_user_groups_led(user_id)
        for group in groups_led:
            group_id = group["group_id"]
            members = group_repository.get_group_members(group_id)
            new_owner = random.choice(members)
            new_owner_id = new_owner["user_id"]
            group_repository.transfer_group_ownership(group_id, user_id=new_owner_id)
            current_app.logger.info(
                f"Transfered ownership of group #{group_id} to member #{new_owner_id}"
            )

        user_repository.delete_user(user_id)
        return jsonify({"message": "User deleted"}), 200


@user_routes.route("/<user_id>/rename", methods=["PUT"])
@handle_db_errors
def handle_user_rename(user_id: int):
    user_repository = UserRepository()
    current_app.logger.info(f"PUT /users/{user_id}")
    data = request.get_json()

    new_first_name = data.get("new_first_name")
    new_last_name = data.get("new_last_name")

    if not new_first_name or not new_last_name:
        return jsonify({"error": "new_first_name and new_last_name required"}), 400

    if len(new_first_name) > 50 or len(new_last_name) > 50:
        return jsonify(
            {"error": "New first/last names cannot exceed 50 characters"}
        ), 400

    user_repository.rename_user(
        user_id, new_first_name=new_first_name, new_last_name=new_last_name
    )
    return jsonify({"message": "User renamed"}), 200


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
    group_id = request.args.get("group_id", type=int)
    chores = repository.get_user_chores(user_id, group_id)
    return jsonify(chores), 200


@user_routes.route("/<user_id>/invites", methods=["GET"])
@handle_db_errors
def handle_user_invites(user_id: int):
    repository = UserRepository()
    current_app.logger.info(f"GET /users/{user_id}/invites")
    pending_only = "pending" in request.args
    invites = repository.get_user_invitations(user_id, pending_only)
    return jsonify(invites), 200

@user_routes.route("/<user_id>/invitations/<invitation_id>/accept", methods=["PUT"])
@handle_db_errors
def handle_accept_invitation(user_id: int, invitation_id: int):
    repository = UserRepository()
    current_app.logger.info(f"PUT /users/{user_id}/invitations/{invitation_id}/accept")
    data = request.get_json()
    group_id = data.get("group_id")
    if not group_id:
        return jsonify({"error": "group_id required"}), 400
    repository.accept_invitation(user_id, invitation_id, group_id)
    return jsonify({"message": "Invitation accepted"}), 200


@user_routes.route("/<user_id>/invitations/<invitation_id>", methods=["DELETE"])
@handle_db_errors
def handle_delete_invitation(user_id: int, invitation_id: int):
    repository = UserRepository()
    current_app.logger.info(f"DELETE /users/{user_id}/invitations/{invitation_id}")
    repository.delete_invitation(invitation_id)
    return jsonify({"message": "Invitation declined"}), 200

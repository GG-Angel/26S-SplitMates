from flask import Blueprint, current_app, jsonify, request
from backend.decorators import handle_db_errors
from backend.repositories.group_repository import GroupRepository


group_routes = Blueprint("groups", __name__)


@group_routes.route("/", methods=["POST"])
@handle_db_errors
def handle_groups():
    repository = GroupRepository()
    body = request.get_json()
    current_app.logger.info("POST /groups/")
    repository.create_group(body)
    return jsonify({"message": "Group created"}), 201


@group_routes.route("/<group_id>", methods=["GET", "DELETE"])
@handle_db_errors
def handle_group(group_id: int):
    repository = GroupRepository()
    current_app.logger.info(f"{request.method} /groups/{group_id}")

    group = repository.get_group(group_id)
    # ensure group exists
    if not group:
        return jsonify({"error": "Not found"}), 404

    if request.method == "GET":
        return jsonify(group), 200
    else:
        repository.delete_group(group_id)
        return jsonify({"message": "Group deleted successfully"}), 200


@group_routes.route("/<group_id>/owner", methods=["PUT"])
@handle_db_errors
def handle_group_owner(group_id: int):
    repository = GroupRepository()
    current_app.logger.info(f"PUT /groups/{group_id}/owner")
    data = request.get_json()
    new_owner_id = data.get("new_owner_id")

    if not new_owner_id:
        return jsonify({"error": "new_owner_id is required"}), 400

    repository.transfer_group_ownership(group_id, new_owner_id)
    return jsonify({"message": "Group ownership transferred successfully"}), 200


@group_routes.route("/<group_id>/members", methods=["GET"])
@handle_db_errors
def handle_group_members(group_id: int):
    repository = GroupRepository()
    current_app.logger.info(f"GET /groups/{group_id}/members")
    members = repository.get_group_members(group_id)
    return jsonify(members), 200


@group_routes.route("/<group_id>/members/<user_id>", methods=["DELETE"])
@handle_db_errors
def handle_group_member(group_id: int, user_id: int):
    repository = GroupRepository()
    current_app.logger.info(f"DELETE /groups/{group_id}/members/{user_id}")
    repository.remove_group_member(group_id, user_id)
    return jsonify({"message": "Member successfully removed"}), 200


@group_routes.route("/<group_id>/members/<user_id>/bills", methods=["GET"])
@handle_db_errors
def handle_group_member_bills(group_id: int, user_id: int):
    repository = GroupRepository()
    current_app.logger.info(f"GET /groups/{group_id}/members/{user_id}/bills")
    unpaid_only = "unpaid_only" in request.args
    bills = repository.get_group_member_bills(group_id, user_id, unpaid_only)
    for bill in bills:
        bill["assignees"] = repository.get_group_bill_assignees(
            group_id,
            bill["bill_id"],
        )
    return jsonify(bills), 200


@group_routes.route("/<group_id>/bills", methods=["GET", "POST"])
@handle_db_errors
def handle_group_bills(group_id: int):
    repository = GroupRepository()
    if request.method == "GET":
        current_app.logger.info(f"GET /groups/{group_id}/bills")
        bills = repository.get_group_bills(group_id)
        for bill in bills:
            bill["assignees"] = repository.get_group_bill_assignees(
                group_id,
                bill["bill_id"],
            )
        return jsonify(bills), 200
    else:
        data = request.get_json()
        repository.create_bill(data)
        return jsonify({"message": "Bill created"}), 201


@group_routes.route("/<group_id>/bills/<bill_id>", methods=["GET", "DELETE"])
@handle_db_errors
def handle_group_bill(group_id: int, bill_id: int):
    repository = GroupRepository()
    if request.method == "GET":
        current_app.logger.info(f"GET /groups/{group_id}/bills/{bill_id}")
        bill = repository.get_group_bill(group_id, bill_id)
        assignees = repository.get_group_bill_assignees(group_id, bill_id)
        return jsonify({"bill": bill, "assignees": assignees}), 200
    else:
        current_app.logger.info(f"DELETE /groups/{group_id}/bills/{bill_id}")
        repository.delete_bill(bill_id)
        return jsonify({"message": "Bill deleted"}), 201


@group_routes.route("/<group_id>/chores", methods=["GET", "POST"])
@handle_db_errors
def handle_group_chores(group_id: int):
    repository = GroupRepository()
    if request.method == "GET":
        current_app.logger.info(f"GET /groups/{group_id}/chores")
        incomplete_only = "incomplete_only" in request.args
        chores = repository.get_group_chores(group_id, incomplete_only)
        for chore in chores:
            chore["assignees"] = repository.get_chore_assignees(chore["chore_id"])
        return jsonify(chores), 200
    else:
        data = request.get_json()
        current_app.logger.info(f"POST /groups/{group_id}/chores")
        repository.create_chore(group_id, data)
        return jsonify({"message": "Chore created"}), 201


@group_routes.route("/chores/<chore_id>/complete", methods=["PUT"])
@handle_db_errors
def complete_chore(chore_id: int):
    repository = GroupRepository()
    current_app.logger.info(f"PUT /groups/chores/{chore_id}/complete")
    repository.complete_chore(chore_id)
    return jsonify({"message": "Chore marked complete"}), 200


@group_routes.route("/<group_id>/events", methods=["GET", "POST"])
@handle_db_errors
def handle_group_events(group_id: int):
    repository = GroupRepository()
    if request.method == "GET":
        current_app.logger.info(f"GET /groups/{group_id}/events")
        events = repository.get_group_events(group_id)
        return jsonify(events), 200
    else:
        data = request.get_json()
        current_app.logger.info(f"POST /groups/{group_id}/events")
        repository.create_event(group_id, data)
        return jsonify({"message": "Event created"}), 201


@group_routes.route("/<group_id>/invites", methods=["GET", "POST"])
@handle_db_errors
def handle_group_invites(group_id: int):
    repository = GroupRepository()
    if request.method == "GET":
        current_app.logger.info(f"GET /groups/{group_id}/invites")
        pending_only = "pending" in request.args
        invites = repository.get_group_invites(group_id, pending_only)
        return jsonify(invites), 200
    else:
        data = request.get_json()
        current_app.logger.info(f"POST /groups/{group_id}/invites")
        user = repository.get_user_by_email(data["email"])
        if not user:
            return jsonify({"error": "User not found"}), 404
        if repository.is_group_member(group_id, user["user_id"]):
            return jsonify({"error": "User is already a member of this group"}), 409
        if repository.get_pending_invite(group_id, user["user_id"]):
            return jsonify({"error": "Invite already sent to this user"}), 409
        repository.create_invitation(group_id, {"sent_to": user["user_id"]})
        return jsonify({"message": "Invitation sent"}), 201


@group_routes.route("/<group_id>/invites/<invitation_id>", methods=["DELETE"])
@handle_db_errors
def handle_group_invitation(group_id: int, invitation_id: int):
    repository = GroupRepository()
    current_app.logger.info(f"DELETE /groups/{group_id}/invites/{invitation_id}")
    repository.delete_invitation(invitation_id)
    return jsonify({"message": "Invitation deleted"}), 200


@group_routes.route("/chores/<chore_id>/assignments", methods=["POST"])
@handle_db_errors
def assign_chore(chore_id: int):
    repository = GroupRepository()
    data = request.get_json()
    current_app.logger.info(f"POST /groups/chores/{chore_id}/assignments")
    repository.assign_user_to_chore(chore_id, data["user_id"])
    return jsonify({"message": "Assigned to chore"}), 201


@group_routes.route("/chores/<chore_id>/assignments/<user_id>", methods=["DELETE"])
@handle_db_errors
def unassign_chore(chore_id: int, user_id: int):
    repository = GroupRepository()
    current_app.logger.info(f"DELETE /groups/chores/{chore_id}/assignments/{user_id}")
    repository.unassign_user_from_chore(chore_id, user_id)
    return jsonify({"message": "Unassigned from chore"}), 200


@group_routes.route("/chores/<chore_id>", methods=["PUT", "DELETE"])
@handle_db_errors
def handle_chore(chore_id: int):
    repository = GroupRepository()
    if request.method == "PUT":
        data = request.get_json()
        current_app.logger.info(f"PUT /groups/chores/{chore_id}")
        repository.update_chore(chore_id, data)
        return jsonify({"message": "Chore updated"}), 200
    else:
        current_app.logger.info(f"DELETE /groups/chores/{chore_id}")
        repository.delete_chore(chore_id)
        return jsonify({"message": "Chore deleted"}), 200

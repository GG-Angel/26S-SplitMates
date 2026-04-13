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


@group_routes.route("/<group_id>", methods=["GET"])
@handle_db_errors
def handle_group(group_id: int):
    repository = GroupRepository()
    current_app.logger.info(f"GET /groups/{group_id}")
    group = repository.get_group(group_id)

    # ensure group exists
    if not group:
        return jsonify({"error": "Not found"}), 404

    current_app.logger.info(f"Retrieved group {group_id}")
    return jsonify(group), 200


@group_routes.route("/<group_id>/members", methods=["GET"])
@handle_db_errors
def handle_group_members(group_id: int):
    repository = GroupRepository()
    current_app.logger.info(f"GET /groups/{group_id}/members")
    members = repository.get_group_members(group_id)
    return jsonify(members), 200


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


@group_routes.route("/<group_id>/bills/<bill_id>", methods=["GET"])
@handle_db_errors
def handle_group_bill(group_id: int, bill_id: int):
    repository = GroupRepository()
    current_app.logger.info(f"GET /groups/{group_id}/bills/<bill_id>")
    bill = repository.get_group_bill(group_id, bill_id)
    assignees = repository.get_group_bill_assignees(group_id, bill_id)
    return jsonify({"bill": bill, "assignees": assignees}), 200


@group_routes.route("/<group_id>/chores", methods=["GET", "POST"])
@handle_db_errors
def handle_group_chores(group_id: int):
    repository = GroupRepository()
    if request.method == "GET":
        current_app.logger.info(f"GET /groups/{group_id}/chores")
        chores = repository.get_group_chores(group_id)
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

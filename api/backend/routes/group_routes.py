from flask import Blueprint, current_app, jsonify, request
from backend.repositories.group_repository import GroupRepository
from mysql.connector import Error


group_routes = Blueprint("groups", __name__)


@group_routes.route("/", methods=["POST"])
def handle_groups():
    repository = GroupRepository()
    try:
        body = request.get_json()
        current_app.logger.info("POST /groups/")
        repository.create_group(body)
        return jsonify({"message": "Group created"}), 201
    except Error as e:
        current_app.logger.error(f"Database error in {handle_groups.__name__}(): {e}")
        return jsonify({"error": "Unexpected error"}), 500


@group_routes.route("/<group_id>", methods=["GET"])
def handle_group(group_id: int):
    repository = GroupRepository()
    try:
        current_app.logger.info(f"GET /groups/{group_id}")
        group = repository.get_group(group_id)

        # ensure group exists
        if not group:
            return jsonify({"error": "Not found"}), 404

        current_app.logger.info(f"Retrieved group {group_id}")
        return jsonify(group), 200
    except Error as e:
        current_app.logger.error(f"Database error in {handle_group.__name__}(): {e}")
        return jsonify({"error": "Unexpected error"}), 500


@group_routes.route("/<group_id>/bills", methods=["GET", "POST"])
def handle_group_bills(group_id: int):
    repository = GroupRepository()
    try:
        if request.method == "GET":
            current_app.logger.info(f"GET /groups/{group_id}/bills")
            bills = repository.get_group_bills(group_id)
            return jsonify(bills), 200
        else:
            data = request.get_json()
            repository.create_bill(data)
            return jsonify({"message": "Bill created"}), 201
    except Error as e:
        current_app.logger.error(
            f"Database error in {handle_group_bills.__name__}(): {e}"
        )
        return jsonify({"error": "Unexpected error"}), 500


@group_routes.route("/<group_id>/bills/<bill_id>", methods=["GET"])
def handle_group_bill(group_id: int, bill_id: int):
    repository = GroupRepository()
    try:
        current_app.logger.info(f"GET /groups/{group_id}/bills/<bill_id>")
        bills = repository.get_group_bill(group_id, bill_id)
        return jsonify(bills), 200
    except Error as e:
        current_app.logger.error(
            f"Database error in {handle_group_bill.__name__}(): {e}"
        )
        return jsonify({"error": "Unexpected error"}), 500

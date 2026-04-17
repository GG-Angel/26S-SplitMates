from flask import Blueprint, current_app, jsonify, request
from mysql.connector import Error

from ..repositories.admin_repository import AdminRepository


admin_routes = Blueprint("admin", __name__)
admin_repository = AdminRepository()


@admin_routes.route("/", methods=["GET"])
def get_root():
    """Health/root endpoint for the admin blueprint."""
    current_app.logger.info("GET /admin/")
    return "<h1>Admin route</h1>"


@admin_routes.route("/summary", methods=["GET"])
def get_admin_summary():
    """Return dashboard KPI counts plus recent tickets/activity for the admin home page."""
    try:
        total_users_data = admin_repository.get_summary_total_users()
        active_households_data = admin_repository.get_summary_active_households()
        open_tickets_data = admin_repository.get_summary_open_tickets()
        inactive_users_data = admin_repository.get_summary_inactive_users()
        urgent_tickets_data = admin_repository.get_summary_urgent_tickets()

        if (
            total_users_data is None
            or active_households_data is None
            or open_tickets_data is None
            or inactive_users_data is None
            or urgent_tickets_data is None
        ):
            current_app.logger.error("One or more summary data objects are None")
            raise Error("Data objects are None")

        total_users = total_users_data["total_users"]
        active_households = active_households_data["active_households"]
        open_tickets = open_tickets_data["open_tickets"]
        inactive_users = inactive_users_data["inactive_users"]
        urgent_tickets = urgent_tickets_data["urgent_tickets"]
        recent_tickets = admin_repository.get_summary_recent_tickets()
        recent_activity = admin_repository.get_summary_recent_activity()

        return jsonify(
            {
                "total_users": total_users,
                "active_households": active_households,
                "open_tickets": open_tickets,
                "inactive_users": inactive_users,
                "urgent_tickets": urgent_tickets,
                "urgent_message": (
                    f"{urgent_tickets} tickets flagged as urgent - immediate review needed"
                    if urgent_tickets
                    else "No urgent tickets right now"
                ),
                "recent_tickets": recent_tickets,
                "recent_activity": recent_activity,
            }
        ), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_admin_summary(): {e}")
        return jsonify({"error": "Unexpected error"}), 500


@admin_routes.route("/users", methods=["GET"])
def get_all_users():
    """Return all users with role flags for admin oversight views."""
    try:
        return jsonify(admin_repository.get_all_users()), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_all_users(): {e}")
        return jsonify({"error": "Unexpected error"}), 500


@admin_routes.route("/users/<int:user_id>/groups", methods=["GET"])
def get_groups_for_user(user_id: int):
    """Return every group membership row for a specific user."""
    try:
        return jsonify(admin_repository.get_groups_for_user(user_id)), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_groups_for_user(): {e}")
        return jsonify({"error": "Unexpected error"}), 500


@admin_routes.route("/groups", methods=["GET"])
def get_all_groups():
    """Return all groups with an aggregated member count per group."""
    try:
        return jsonify(admin_repository.get_all_groups()), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_all_groups(): {e}")
        return jsonify({"error": "Unexpected error"}), 500


@admin_routes.route("/groups/<int:group_id>", methods=["GET"])
def get_group_by_id(group_id: int):
    """Return detailed info for a specific group by id."""
    try:
        row = admin_repository.get_group_by_id(group_id)
        if not row:
            return jsonify({"error": "Not found"}), 404
        return jsonify(row), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_group_by_id(): {e}")
        return jsonify({"error": "Unexpected error"}), 500


@admin_routes.route("/groups/<int:group_id>", methods=["DELETE"])
def delete_group(group_id: int):
    """Delete a group (used by admins to remove inactive groups)."""
    try:
        if not admin_repository.delete_group_by_id(group_id):
            return jsonify({"error": "Not found"}), 404
        return jsonify({"message": "Group deleted"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in delete_group(): {e}")
        return jsonify({"error": "Unexpected error"}), 500


@admin_routes.route("/users/<int:user_id>/bans", methods=["GET"])
def get_bans_for_user(user_id: int):
    """Return all bans issued against a specific user."""
    try:
        return jsonify(admin_repository.get_bans_for_user(user_id)), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_bans_for_user(): {e}")
        return jsonify({"error": "Unexpected error"}), 500


@admin_routes.route("/users/<int:user_id>/bans", methods=["POST"])
def issue_ban_for_user(user_id: int):
    """Issue a new ban for a user."""
    payload = request.get_json(silent=True) or {}
    issued_by = payload.get("issued_by")
    reasons = payload.get("reasons")
    expires_at = payload.get("expires_at")

    if issued_by is None:
        return jsonify({"error": "Field 'issued_by' is required"}), 400

    try:
        ban_id = admin_repository.insert_ban_for_user(
            user_id,
            {
                "issued_by": issued_by,
                "reasons": reasons,
                "expires_at": expires_at,
            },
        )
        return jsonify({"message": "Ban issued", "ban_id": ban_id}), 201
    except Error as e:
        current_app.logger.error(f"Database error in issue_ban_for_user(): {e}")
        return jsonify({"error": "Unexpected error"}), 500


@admin_routes.route("/users/<int:user_id>/bans/<int:ban_id>", methods=["PUT"])
def update_ban_for_user(user_id: int, ban_id: int):
    """Edit fields on an existing ban (e.g., reason or expiration)."""
    payload = request.get_json(silent=True) or {}
    reasons = payload.get("reasons")
    expires_at = payload.get("expires_at")

    if reasons is None and expires_at is None:
        return jsonify({"error": "No updatable fields provided"}), 400

    try:
        if not admin_repository.update_ban_for_user(
            user_id,
            ban_id,
            {"reasons": reasons, "expires_at": expires_at},
        ):
            return jsonify({"error": "Not found"}), 404
        return jsonify({"message": "Ban updated"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in update_ban_for_user(): {e}")
        return jsonify({"error": "Unexpected error"}), 500


@admin_routes.route("/users/<int:user_id>/bans/<int:ban_id>", methods=["DELETE"])
def lift_ban_for_user(user_id: int, ban_id: int):
    """Lift a ban for a user and restore active status when no active bans remain."""
    try:
        if not admin_repository.delete_ban_for_user(user_id, ban_id):
            return jsonify({"error": "Not found"}), 404
        return jsonify({"message": "Ban lifted"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in lift_ban_for_user(): {e}")
        return jsonify({"error": "Unexpected error"}), 500


@admin_routes.route("/support_tickets", methods=["GET"])
def get_all_support_tickets():
    """Return all support tickets submitted by users."""
    try:
        return jsonify(admin_repository.get_all_support_tickets()), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_all_support_tickets(): {e}")
        return jsonify({"error": "Unexpected error"}), 500


@admin_routes.route("/support_tickets/<int:ticket_id>", methods=["GET"])
def get_support_ticket_by_id(ticket_id: int):
    """Return one support ticket by its id."""
    try:
        row = admin_repository.get_support_ticket_by_id(ticket_id)
        if not row:
            return jsonify({"error": "Not found"}), 404
        return jsonify(row), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_support_ticket_by_id(): {e}")
        return jsonify({"error": "Unexpected error"}), 500


@admin_routes.route("/support_tickets/<int:ticket_id>", methods=["PUT"])
def update_support_ticket(ticket_id: int):
    """Update editable fields for a support ticket."""
    payload = request.get_json(silent=True) or {}
    status = payload.get("status")
    priority = payload.get("priority")
    description = payload.get("description")
    assigned_to = payload.get("assigned_to")
    title = payload.get("title")
    resolved_at = payload.get("resolved_at")

    if (
        status is None
        and priority is None
        and description is None
        and assigned_to is None
        and title is None
        and resolved_at is None
    ):
        return jsonify({"error": "No updatable fields provided"}), 400

    try:
        if not admin_repository.update_support_ticket(ticket_id, payload):
            return jsonify({"error": "Not found"}), 404
        return jsonify({"message": "Support ticket updated"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in update_support_ticket(): {e}")
        return jsonify({"error": "Unexpected error"}), 500


@admin_routes.route("/support_tickets/by_user/<int:user_id>", methods=["GET"])
def get_support_tickets_by_submitter(user_id: int):
    """Return all support tickets submitted by a specific user."""
    try:
        return jsonify(admin_repository.get_support_tickets_by_submitter(user_id)), 200
    except Error as e:
        current_app.logger.error(
            f"Database error in get_support_tickets_by_submitter(): {e}"
        )
        return jsonify({"error": "Unexpected error"}), 500


@admin_routes.route("/user_reports", methods=["GET"])
def get_all_user_reports():
    """Return all user reports for moderation review."""
    try:
        return jsonify(admin_repository.get_all_user_reports()), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_all_user_reports(): {e}")
        return jsonify({"error": "Unexpected error"}), 500


@admin_routes.route("/user_reports/by_user/<int:reported_by>", methods=["GET"])
def get_user_reports_by_reporter(reported_by: int):
    """Return reports submitted by a specific user."""
    try:
        return jsonify(admin_repository.get_user_reports_by_reporter(reported_by)), 200
    except Error as e:
        current_app.logger.error(
            f"Database error in get_user_reports_by_reporter(): {e}"
        )
        return jsonify({"error": "Unexpected error"}), 500


@admin_routes.route("/user_reports/against_user/<int:reported_user>", methods=["GET"])
def get_user_reports_against_user(reported_user: int):
    """Return reports filed against a specific user."""
    try:
        return jsonify(
            admin_repository.get_user_reports_against_user(reported_user)
        ), 200
    except Error as e:
        current_app.logger.error(
            f"Database error in get_user_reports_against_user(): {e}"
        )
        return jsonify({"error": "Unexpected error"}), 500


@admin_routes.route("/user_reports/<int:report_id>", methods=["GET"])
def get_user_report_by_id(report_id: int):
    """Return details for one report by id."""
    try:
        row = admin_repository.get_user_report_by_id(report_id)
        if not row:
            return jsonify({"error": "Not found"}), 404
        return jsonify(row), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_user_report_by_id(): {e}")
        return jsonify({"error": "Unexpected error"}), 500


@admin_routes.route("/user_reports/<int:report_id>", methods=["PUT"])
def update_user_report(report_id: int):
    """Update moderation fields on a user report."""
    payload = request.get_json(silent=True) or {}
    status = payload.get("status")
    reviewed_by = payload.get("reviewed_by")
    reviewed_at = payload.get("reviewed_at")

    if status is None and reviewed_by is None and reviewed_at is None:
        return jsonify({"error": "No updatable fields provided"}), 400

    try:
        if not admin_repository.update_user_report(report_id, payload):
            return jsonify({"error": "Not found"}), 404
        return jsonify({"message": "User report updated"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in update_user_report(): {e}")
        return jsonify({"error": "Unexpected error"}), 500


@admin_routes.route("/app_versions", methods=["GET"])
def get_all_app_versions():
    """Return all app version history rows."""
    try:
        return jsonify(admin_repository.get_all_app_versions()), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_all_app_versions(): {e}")
        return jsonify({"error": "Unexpected error"}), 500


@admin_routes.route("/app_versions", methods=["POST"])
def create_app_version():
    """Create a new app version row for deployment tracking."""
    payload = request.get_json(silent=True) or {}
    version_number = payload.get("version_number")
    deployed_by = payload.get("deployed_by")
    status = payload.get("status", "deployed")
    release_notes = payload.get("release_notes")
    deployed_at = payload.get("deployed_at")

    if version_number is None or deployed_by is None:
        return jsonify(
            {"error": "Fields 'version_number' and 'deployed_by' are required"}
        ), 400

    try:
        version_id = admin_repository.create_app_version(
            {
                "version_number": version_number,
                "deployed_by": deployed_by,
                "status": status,
                "release_notes": release_notes,
                "deployed_at": deployed_at,
            }
        )
        return jsonify(
            {"message": "App version created", "version_id": version_id}
        ), 201
    except Error as e:
        current_app.logger.error(f"Database error in create_app_version(): {e}")
        return jsonify({"error": "Unexpected error"}), 500


@admin_routes.route("/audit_logs", methods=["GET"])
def get_audit_logs():
    """Return latest audit logs (optionally filter by user_id/action_type)."""
    user_id = request.args.get("user_id", type=int)
    action_type = request.args.get("action_type", type=str)

    try:
        return jsonify(admin_repository.get_audit_logs(user_id, action_type)), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_audit_logs(): {e}")
        return jsonify({"error": "Unexpected error"}), 500


@admin_routes.route("/maintenance/normalize_check", methods=["GET"])
def get_maintenance_normalize_check():
    """
    Run lightweight schema-health checks (counts + orphan detection)
    from existing tables only.
    """
    try:
        return jsonify(admin_repository.maintenance_check()), 200
    except Error as e:
        current_app.logger.error(
            f"Database error in get_maintenance_normalize_check(): {e}"
        )
        return jsonify({"error": "Unexpected error"}), 500

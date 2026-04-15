from flask import Blueprint, current_app, jsonify, request
from mysql.connector import Error

from backend.db_connection import get_db


admin_routes = Blueprint("admin", __name__)


@admin_routes.route("/", methods=["GET"])
def get_root():
    """Health/root endpoint for the admin blueprint."""
    current_app.logger.info("GET /admin/")
    return "<h1>Admin route</h1>"


@admin_routes.route("/summary", methods=["GET"])
def get_admin_summary():
    """Return dashboard KPI counts plus recent tickets/activity for the admin home page."""
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) AS total_users FROM users")
        total_users = cursor.fetchone()["total_users"]

        cursor.execute(
            """
            SELECT COUNT(DISTINCT gm.group_id) AS active_households
            FROM group_members gm
            """
        )
        active_households = cursor.fetchone()["active_households"]

        cursor.execute(
            """
            SELECT COUNT(*) AS open_tickets
            FROM support_tickets
            WHERE status = 'open'
            """
        )
        open_tickets = cursor.fetchone()["open_tickets"]

        cursor.execute(
            """
            SELECT COUNT(*) AS inactive_users
            FROM users
            WHERE account_status <> 'active'
            """
        )
        inactive_users = cursor.fetchone()["inactive_users"]

        cursor.execute(
            """
            SELECT COUNT(*) AS urgent_tickets
            FROM support_tickets
            WHERE priority = 'high' AND status <> 'closed'
            """
        )
        urgent_tickets = cursor.fetchone()["urgent_tickets"]

        cursor.execute(
            """
            SELECT
                st.ticket_id,
                st.title,
                st.status,
                st.priority,
                st.created_at,
                u.first_name,
                u.last_name
            FROM support_tickets st
            JOIN users u ON st.submitted_by = u.user_id
            ORDER BY st.created_at DESC
            LIMIT 5
            """
        )
        recent_tickets = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                al.log_id,
                al.details,
                al.action_type,
                al.target_table,
                al.target_id,
                al.performed_at,
                u.first_name,
                u.last_name
            FROM audit_logs al
            JOIN users u ON al.user_id = u.user_id
            ORDER BY al.performed_at DESC
            LIMIT 5
            """
        )
        recent_activity = cursor.fetchall()

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
    finally:
        cursor.close()


@admin_routes.route("/users", methods=["GET"])
def get_all_users():
    """Return all users with role flags for admin oversight views."""
    cursor = get_db().cursor(dictionary=True)
    try:
        query = """
            SELECT user_id, first_name, last_name, email, created_at, is_admin, is_analyst, account_status
            FROM users
            ORDER BY created_at DESC
        """
        cursor.execute(query)
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_all_users(): {e}")
        return jsonify({"error": "Unexpected error"}), 500
    finally:
        cursor.close()


@admin_routes.route("/users/<int:user_id>/groups", methods=["GET"])
def get_groups_for_user(user_id: int):
    """Return every group membership row for a specific user."""
    cursor = get_db().cursor(dictionary=True)
    try:
        query = """
            SELECT g.group_id, g.name, g.address, g.city, g.state, g.zip_code, g.group_leader
            FROM group_members gm
            JOIN `groups` g ON gm.group_id = g.group_id
            WHERE gm.user_id = %s
            ORDER BY g.group_id
        """
        cursor.execute(query, (user_id,))
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_groups_for_user(): {e}")
        return jsonify({"error": "Unexpected error"}), 500
    finally:
        cursor.close()


@admin_routes.route("/groups", methods=["GET"])
def get_all_groups():
    """Return all groups with an aggregated member count per group."""
    cursor = get_db().cursor(dictionary=True)
    try:
        query = """
            SELECT
                g.group_id,
                g.name,
                g.group_leader,
                COUNT(gm.user_id) AS member_count
            FROM `groups` g
            LEFT JOIN group_members gm ON g.group_id = gm.group_id
            GROUP BY g.group_id, g.name, g.group_leader
            ORDER BY g.group_id
        """
        cursor.execute(query)
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_all_groups(): {e}")
        return jsonify({"error": "Unexpected error"}), 500
    finally:
        cursor.close()


@admin_routes.route("/groups/<int:group_id>", methods=["GET"])
def get_group_by_id(group_id: int):
    """Return detailed info for a specific group by id."""
    cursor = get_db().cursor(dictionary=True)
    try:
        query = """
            SELECT
                g.group_id,
                g.name,
                g.address,
                g.city,
                g.state,
                g.zip_code,
                g.group_leader,
                COUNT(gm.user_id) AS member_count
            FROM `groups` g
            LEFT JOIN group_members gm ON g.group_id = gm.group_id
            WHERE g.group_id = %s
            GROUP BY g.group_id, g.name, g.address, g.city, g.state, g.zip_code, g.group_leader
        """
        cursor.execute(query, (group_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "Not found"}), 404
        return jsonify(row), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_group_by_id(): {e}")
        return jsonify({"error": "Unexpected error"}), 500
    finally:
        cursor.close()


@admin_routes.route("/groups/<int:group_id>", methods=["DELETE"])
def delete_group(group_id: int):
    """Delete a group (used by admins to remove inactive groups)."""
    cursor = get_db().cursor(dictionary=True)
    try:
        query = "DELETE FROM `groups` WHERE group_id = %s"
        cursor.execute(query, (group_id,))
        get_db().commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Not found"}), 404
        return jsonify({"message": "Group deleted"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in delete_group(): {e}")
        return jsonify({"error": "Unexpected error"}), 500
    finally:
        cursor.close()


@admin_routes.route("/users/<int:user_id>/bans", methods=["GET"])
def get_bans_for_user(user_id: int):
    """Return all bans issued against a specific user."""
    cursor = get_db().cursor(dictionary=True)
    try:
        query = """
            SELECT ban_id, user_id, issued_by, issued_at, reasons, expires_at
            FROM bans
            WHERE user_id = %s
            ORDER BY issued_at DESC
        """
        cursor.execute(query, (user_id,))
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_bans_for_user(): {e}")
        return jsonify({"error": "Unexpected error"}), 500
    finally:
        cursor.close()


@admin_routes.route("/users/<int:user_id>/bans", methods=["POST"])
def issue_ban_for_user(user_id: int):
    """Issue a new ban for a user."""
    payload = request.get_json(silent=True) or {}
    issued_by = payload.get("issued_by")
    reasons = payload.get("reasons")
    expires_at = payload.get("expires_at")

    if issued_by is None:
        return jsonify({"error": "Field 'issued_by' is required"}), 400

    cursor = get_db().cursor(dictionary=True)
    try:
        query = """
            INSERT INTO bans (user_id, issued_by, reasons, expires_at)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, issued_by, reasons, expires_at))

        # Enforce user policy by suspending the account when a ban is issued.
        cursor.execute(
            "UPDATE users SET account_status = 'suspended' WHERE user_id = %s",
            (user_id,),
        )

        get_db().commit()
        return jsonify({"message": "Ban issued", "ban_id": cursor.lastrowid}), 201
    except Error as e:
        current_app.logger.error(f"Database error in issue_ban_for_user(): {e}")
        return jsonify({"error": "Unexpected error"}), 500
    finally:
        cursor.close()


@admin_routes.route("/users/<int:user_id>/bans/<int:ban_id>", methods=["PUT"])
def update_ban_for_user(user_id: int, ban_id: int):
    """Edit fields on an existing ban (e.g., reason or expiration)."""
    payload = request.get_json(silent=True) or {}
    reasons = payload.get("reasons")
    expires_at = payload.get("expires_at")

    updates = []
    params = []
    if reasons is not None:
        updates.append("reasons = %s")
        params.append(reasons)
    if expires_at is not None:
        updates.append("expires_at = %s")
        params.append(expires_at)

    if not updates:
        return jsonify({"error": "No updatable fields provided"}), 400

    cursor = get_db().cursor(dictionary=True)
    try:
        params.extend([user_id, ban_id])
        query = f"UPDATE bans SET {', '.join(updates)} WHERE user_id = %s AND ban_id = %s"
        cursor.execute(query, tuple(params))
        get_db().commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Not found"}), 404
        return jsonify({"message": "Ban updated"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in update_ban_for_user(): {e}")
        return jsonify({"error": "Unexpected error"}), 500
    finally:
        cursor.close()


@admin_routes.route("/users/<int:user_id>/bans/<int:ban_id>", methods=["DELETE"])
def lift_ban_for_user(user_id: int, ban_id: int):
    """Lift a ban for a user and restore active status when no active bans remain."""
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute("DELETE FROM bans WHERE user_id = %s AND ban_id = %s", (user_id, ban_id))
        if cursor.rowcount == 0:
            get_db().rollback()
            return jsonify({"error": "Not found"}), 404

        cursor.execute(
            """
            SELECT COUNT(*) AS active_bans
            FROM bans
            WHERE user_id = %s
              AND (expires_at IS NULL OR expires_at > NOW())
            """,
            (user_id,),
        )
        active_bans = cursor.fetchone()["active_bans"]

        if active_bans == 0:
            cursor.execute("UPDATE users SET account_status = 'active' WHERE user_id = %s", (user_id,))

        get_db().commit()
        return jsonify({"message": "Ban lifted"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in lift_ban_for_user(): {e}")
        return jsonify({"error": "Unexpected error"}), 500
    finally:
        cursor.close()


@admin_routes.route("/support_tickets", methods=["GET"])
def get_all_support_tickets():
    """Return all support tickets submitted by users."""
    cursor = get_db().cursor(dictionary=True)
    try:
        query = """
            SELECT ticket_id, submitted_by, status, priority, description,
                   assigned_to, title, created_at, resolved_at
            FROM support_tickets
            ORDER BY created_at DESC
        """
        cursor.execute(query)
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_all_support_tickets(): {e}")
        return jsonify({"error": "Unexpected error"}), 500
    finally:
        cursor.close()


@admin_routes.route("/support_tickets/<int:ticket_id>", methods=["GET"])
def get_support_ticket_by_id(ticket_id: int):
    """Return one support ticket by its id."""
    cursor = get_db().cursor(dictionary=True)
    try:
        query = """
            SELECT ticket_id, submitted_by, status, priority, description,
                   assigned_to, title, created_at, resolved_at
            FROM support_tickets
            WHERE ticket_id = %s
        """
        cursor.execute(query, (ticket_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "Not found"}), 404
        return jsonify(row), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_support_ticket_by_id(): {e}")
        return jsonify({"error": "Unexpected error"}), 500
    finally:
        cursor.close()


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

    updates = []
    params = []
    if status is not None:
        updates.append("status = %s")
        params.append(status)
    if priority is not None:
        updates.append("priority = %s")
        params.append(priority)
    if description is not None:
        updates.append("description = %s")
        params.append(description)
    if assigned_to is not None:
        updates.append("assigned_to = %s")
        params.append(assigned_to)
    if title is not None:
        updates.append("title = %s")
        params.append(title)
    if resolved_at is not None:
        updates.append("resolved_at = %s")
        params.append(resolved_at)

    if not updates:
        return jsonify({"error": "No updatable fields provided"}), 400

    cursor = get_db().cursor(dictionary=True)
    try:
        params.append(ticket_id)
        query = f"UPDATE support_tickets SET {', '.join(updates)} WHERE ticket_id = %s"
        cursor.execute(query, tuple(params))
        get_db().commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Not found"}), 404
        return jsonify({"message": "Support ticket updated"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in update_support_ticket(): {e}")
        return jsonify({"error": "Unexpected error"}), 500
    finally:
        cursor.close()


@admin_routes.route("/support_tickets/by_user/<int:user_id>", methods=["GET"])
def get_support_tickets_by_submitter(user_id: int):
    """Return all support tickets submitted by a specific user."""
    cursor = get_db().cursor(dictionary=True)
    try:
        query = """
            SELECT ticket_id, submitted_by, status, priority, description,
                   assigned_to, title, created_at, resolved_at
            FROM support_tickets
            WHERE submitted_by = %s
            ORDER BY created_at DESC
        """
        cursor.execute(query, (user_id,))
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_support_tickets_by_submitter(): {e}")
        return jsonify({"error": "Unexpected error"}), 500
    finally:
        cursor.close()


@admin_routes.route("/user_reports", methods=["GET"])
def get_all_user_reports():
    """Return all user reports for moderation review."""
    cursor = get_db().cursor(dictionary=True)
    try:
        query = """
            SELECT report_id, reported_user, reported_by, reason, status,
                   reviewed_by, reviewed_at, created_at
            FROM user_reports
            ORDER BY created_at DESC
        """
        cursor.execute(query)
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_all_user_reports(): {e}")
        return jsonify({"error": "Unexpected error"}), 500
    finally:
        cursor.close()


@admin_routes.route("/user_reports/by_user/<int:reported_by>", methods=["GET"])
def get_user_reports_by_reporter(reported_by: int):
    """Return reports submitted by a specific user."""
    cursor = get_db().cursor(dictionary=True)
    try:
        query = """
            SELECT report_id, reported_user, reported_by, reason, status,
                   reviewed_by, reviewed_at, created_at
            FROM user_reports
            WHERE reported_by = %s
            ORDER BY created_at DESC
        """
        cursor.execute(query, (reported_by,))
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_user_reports_by_reporter(): {e}")
        return jsonify({"error": "Unexpected error"}), 500
    finally:
        cursor.close()


@admin_routes.route("/user_reports/against_user/<int:reported_user>", methods=["GET"])
def get_user_reports_against_user(reported_user: int):
    """Return reports filed against a specific user."""
    cursor = get_db().cursor(dictionary=True)
    try:
        query = """
            SELECT report_id, reported_user, reported_by, reason, status,
                   reviewed_by, reviewed_at, created_at
            FROM user_reports
            WHERE reported_user = %s
            ORDER BY created_at DESC
        """
        cursor.execute(query, (reported_user,))
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_user_reports_against_user(): {e}")
        return jsonify({"error": "Unexpected error"}), 500
    finally:
        cursor.close()


@admin_routes.route("/user_reports/<int:report_id>", methods=["GET"])
def get_user_report_by_id(report_id: int):
    """Return details for one report by id."""
    cursor = get_db().cursor(dictionary=True)
    try:
        query = """
            SELECT report_id, reported_user, reported_by, reason, status,
                   reviewed_by, reviewed_at, created_at
            FROM user_reports
            WHERE report_id = %s
        """
        cursor.execute(query, (report_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "Not found"}), 404
        return jsonify(row), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_user_report_by_id(): {e}")
        return jsonify({"error": "Unexpected error"}), 500
    finally:
        cursor.close()


@admin_routes.route("/user_reports/<int:report_id>", methods=["PUT"])
def update_user_report(report_id: int):
    """Update moderation fields on a user report."""
    payload = request.get_json(silent=True) or {}
    status = payload.get("status")
    reviewed_by = payload.get("reviewed_by")
    reviewed_at = payload.get("reviewed_at")

    updates = []
    params = []
    if status is not None:
        updates.append("status = %s")
        params.append(status)
    if reviewed_by is not None:
        updates.append("reviewed_by = %s")
        params.append(reviewed_by)
    if reviewed_at is not None:
        updates.append("reviewed_at = %s")
        params.append(reviewed_at)

    if not updates:
        return jsonify({"error": "No updatable fields provided"}), 400

    cursor = get_db().cursor(dictionary=True)
    try:
        params.append(report_id)
        query = f"UPDATE user_reports SET {', '.join(updates)} WHERE report_id = %s"
        cursor.execute(query, tuple(params))
        get_db().commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Not found"}), 404
        return jsonify({"message": "User report updated"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in update_user_report(): {e}")
        return jsonify({"error": "Unexpected error"}), 500
    finally:
        cursor.close()


@admin_routes.route("/app_versions", methods=["GET"])
def get_all_app_versions():
    """Return all app version history rows."""
    cursor = get_db().cursor(dictionary=True)
    try:
        query = """
            SELECT version_id, version_number, deployed_by, status, release_notes, deployed_at
            FROM app_versions
            ORDER BY version_number DESC
        """
        cursor.execute(query)
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_all_app_versions(): {e}")
        return jsonify({"error": "Unexpected error"}), 500
    finally:
        cursor.close()


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
        return jsonify({"error": "Fields 'version_number' and 'deployed_by' are required"}), 400

    cursor = get_db().cursor(dictionary=True)
    try:
        query = """
            INSERT INTO app_versions (version_number, deployed_by, status, release_notes, deployed_at)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (version_number, deployed_by, status, release_notes, deployed_at))
        get_db().commit()
        return jsonify({"message": "App version created", "version_id": cursor.lastrowid}), 201
    except Error as e:
        current_app.logger.error(f"Database error in create_app_version(): {e}")
        return jsonify({"error": "Unexpected error"}), 500
    finally:
        cursor.close()


@admin_routes.route("/audit_logs", methods=["GET"])
def get_audit_logs():
    """Return latest audit logs (optionally filter by user_id/action_type)."""
    user_id = request.args.get("user_id", type=int)
    action_type = request.args.get("action_type", type=str)

    cursor = get_db().cursor(dictionary=True)
    try:
        query = """
            SELECT log_id, user_id, details, target_table, target_id, action_type, performed_at
            FROM audit_logs
            WHERE (%s IS NULL OR user_id = %s)
              AND (%s IS NULL OR action_type = %s)
            ORDER BY performed_at DESC
            LIMIT 500
        """
        cursor.execute(query, (user_id, user_id, action_type, action_type))
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_audit_logs(): {e}")
        return jsonify({"error": "Unexpected error"}), 500
    finally:
        cursor.close()


@admin_routes.route("/maintenance/normalize_check", methods=["GET"])
def get_maintenance_normalize_check():
    """
    Run lightweight schema-health checks (counts + orphan detection)
    from existing tables only.
    """
    cursor = get_db().cursor(dictionary=True)
    try:
        checks = {}

        cursor.execute("SELECT COUNT(*) AS c FROM users")
        checks["users_count"] = cursor.fetchone()["c"]

        cursor.execute("SELECT COUNT(*) AS c FROM `groups`")
        checks["groups_count"] = cursor.fetchone()["c"]

        cursor.execute("SELECT COUNT(*) AS c FROM bills")
        checks["bills_count"] = cursor.fetchone()["c"]

        cursor.execute("SELECT COUNT(*) AS c FROM group_members")
        checks["group_members_count"] = cursor.fetchone()["c"]

        cursor.execute(
            """
            SELECT COUNT(*) AS c
            FROM bills b
            LEFT JOIN `groups` g ON b.group_id = g.group_id
            WHERE g.group_id IS NULL
            """
        )
        checks["orphan_bills"] = cursor.fetchone()["c"]

        cursor.execute(
            """
            SELECT COUNT(*) AS c
            FROM bill_assignments ba
            LEFT JOIN bills b ON ba.bill_id = b.bill_id
            WHERE b.bill_id IS NULL
            """
        )
        checks["orphan_bill_assignments"] = cursor.fetchone()["c"]

        checks["status"] = "ok" if checks["orphan_bills"] == 0 and checks["orphan_bill_assignments"] == 0 else "warning"
        return jsonify(checks), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_maintenance_normalize_check(): {e}")
        return jsonify({"error": "Unexpected error"}), 500
    finally:
        cursor.close()

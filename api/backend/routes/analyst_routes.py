from flask import Blueprint, current_app, jsonify
from backend.decorators import handle_db_errors
from backend.repositories.analyst_repository import AnalystRepository


analyst_routes = Blueprint("analyst", __name__)


@analyst_routes.route("/audit-logs", methods=["GET"])
@handle_db_errors
def handle_audit_logs():
    repository = AnalystRepository()
    current_app.logger.info("GET /analyst/audit-logs")
    logs = repository.get_audit_log_summary()
    return jsonify(logs), 200


@analyst_routes.route("/sessions", methods=["GET"])
@handle_db_errors
def handle_sessions():
    repository = AnalystRepository()
    current_app.logger.info("GET /analyst/sessions")
    sessions = repository.get_session_summary()
    return jsonify(sessions), 200


@analyst_routes.route("/chores/completed", methods=["GET"])
@handle_db_errors
def handle_completed_chores():
    repository = AnalystRepository()
    current_app.logger.info("GET /analyst/chores/completed")
    chores = repository.get_completed_chores()
    return jsonify(chores), 200


@analyst_routes.route("/users/inactive", methods=["GET"])
@handle_db_errors
def handle_inactive_users():
    repository = AnalystRepository()
    current_app.logger.info("GET /analyst/users/inactive")
    users = repository.get_inactive_users()
    return jsonify(users), 200


@analyst_routes.route("/groups/engagement", methods=["GET"])
@handle_db_errors
def handle_group_engagement():
    repository = AnalystRepository()
    current_app.logger.info("GET /analyst/groups/engagement")
    engagement = repository.get_group_engagement()
    return jsonify(engagement), 200

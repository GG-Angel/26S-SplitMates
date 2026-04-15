from functools import wraps
from flask import current_app, jsonify
from mysql.connector import Error


def handle_db_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Error as e:
            # MySQL error 1406 (22001): Data too long for column -> treat as bad request
            if getattr(e, "errno", None) == 1406:
                current_app.logger.warning(f"Bad input in {f.__name__}(): {e}")
                return jsonify({"error": "Invalid input data"}), 400

            current_app.logger.error(f"Database error in {f.__name__}(): {e}")
            return jsonify({"error": "Unexpected error"}), 500

    return wrapper

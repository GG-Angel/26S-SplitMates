from functools import wraps
from flask import current_app, jsonify
from mysql.connector import Error


def handle_db_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Error as e:
            current_app.logger.error(f"Database error in {f.__name__}(): {e}")
            return jsonify({"error": "Unexpected error"}), 500

    return wrapper

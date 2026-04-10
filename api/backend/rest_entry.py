from flask import Flask
from dotenv import load_dotenv
import os
import logging

from backend.mocks import init_mocks
from backend.routes.group_routes import group_routes
from backend.routes.user_routes import user_routes
from backend.db_connection import init_app as init_db


def create_app():
    app = Flask(__name__)

    app.logger.setLevel(logging.DEBUG)
    app.logger.info("API startup")

    # Load environment variables from the .env file so they are
    # accessible via os.getenv() below.
    load_dotenv()

    # Secret key used by Flask for securely signing session cookies.
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    # Database connection settings — values come from the .env file.
    app.config["MYSQL_DATABASE_USER"] = os.getenv("DB_USER").strip()  # type: ignore
    app.config["MYSQL_DATABASE_PASSWORD"] = os.getenv("MYSQL_ROOT_PASSWORD").strip()  # type: ignore
    app.config["MYSQL_DATABASE_HOST"] = os.getenv("DB_HOST").strip()  # type: ignore
    app.config["MYSQL_DATABASE_PORT"] = int(os.getenv("DB_PORT").strip())  # type: ignore
    app.config["MYSQL_DATABASE_DB"] = os.getenv("DB_NAME").strip()  # type: ignore

    # Register the cleanup hook for the database connection.
    app.logger.info("create_app(): initializing database connection")
    init_db(app)

    # Initialize mock data
    app.logger.info("create_app(): initializing mocks")
    init_mocks(app)

    # Register the routes from each Blueprint with the app object
    # and give a url prefix to each.
    app.logger.info("create_app(): registering blueprints")
    app.register_blueprint(user_routes, url_prefix="/users")
    app.register_blueprint(group_routes, url_prefix="/groups")

    return app

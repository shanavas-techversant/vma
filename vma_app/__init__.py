import os
import urllib3

from constants import (
    CHILD_SERVICE,
    DEFAULT_CONFIG_FILE,
    PARENT_SERVICE,
    SERVICE_NAME,
    VMACONFIG,
)
from flask import Flask  # Import the Flask class

from .db import DB, MIGRATE, init_db, migrate_database


def create_app():
    """
    Create and bootstrap a flask application
    """
    app = Flask(__name__)
    config_file = get_config_file()
    app.config.from_json(config_file)
    DB.init_app(app)
    app.db = DB

    bootstap(app)
    return app


def get_config_file():
    """
    Get the absolute path to config file
    """
    file_path = os.getenv(VMACONFIG, DEFAULT_CONFIG_FILE)
    if not os.path.isabs(file_path):
        file_path = os.path.abspath(file_path)

    if os.path.isfile(file_path):
        # file exists
        return file_path

    raise RuntimeError(f"Could not find config file {file_path}")


def bootstap(app):
    """
    Bootstrap service specific actions
    """

    # disable certificate warnings for non prod environments
    if not is_production(app):
        urllib3.disable_warnings()

    if app.config[SERVICE_NAME] == PARENT_SERVICE:
        MIGRATE.init_app(app, DB)
        migrate_database(app)
    elif app.config[SERVICE_NAME] == CHILD_SERVICE:
        init_db(app)


def is_production(app):
    return app.config.get("ENV") == "production"

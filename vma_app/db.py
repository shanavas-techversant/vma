from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from flask import current_app
from sqlalchemy import MetaData
from multiprocessing import Lock
from sqlalchemy import create_engine

from .utils import get_metadata_from_parent

DB = SQLAlchemy()
MIGRATE = Migrate()
lock = Lock()


def get_schema():
    meta = MetaData()
    meta.reflect(bind=current_app.db.engine)
    return meta


# connect to parent service and initialize database
def init_db(app):
    base_url = app.config["PARENT_BASE_URL"]
    try:
        with lock:
            metadata = get_metadata_from_parent(base_url, app.config)
            engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
            metadata.create_all(engine, checkfirst=True)
    except Exception:
        raise RuntimeError("Could not initialize database schema")


def migrate_database(app):
    try:
        with app.app_context():
            upgrade()
    except Exception:
        raise RuntimeError("Could not migrate database")

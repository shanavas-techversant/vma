from .internal import internal_blueprint
from .auth import auth_blueprint


def register_blueprints(app):
    app.register_blueprint(internal_blueprint)
    app.register_blueprint(auth_blueprint)

from .internal import internal_blueprint


def register_blueprints(app):
    app.register_blueprint(internal_blueprint)

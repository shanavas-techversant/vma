from vma_app.apis import register_blueprints as register_apis
from .main import main_blueprint
from .oauth import oauth_blueprint


def register_blueprints(app):
    register_apis(app)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(oauth_blueprint)

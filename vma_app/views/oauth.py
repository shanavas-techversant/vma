from flask import (
    Blueprint,
    flash,
    redirect,
    url_for,
)
from flask_login import login_user
from ..oauth2client import OAuth2Client

from ..models import User
from ..db import DB as db

oauth_blueprint = Blueprint("oauth", __name__, url_prefix='/oauth')


@oauth_blueprint.route("/sign-in/<provider>")
def oauth2_signin(provider):
    remote_app = OAuth2Client.get_provider(provider)
    return remote_app.authorization()


@oauth_blueprint.route("/sign-in/<provider>/authorized")
def authorized(provider):
    remote_app = OAuth2Client.get_provider(provider)
    provider, social_id, email_address, username = remote_app.authorized()
    if provider is not None and social_id is not None:
        # If the social user is not known, add to our database.
        user = (
            User.query.filter_by(provider=provider)
            .filter_by(social_id=social_id)
            .first()
        )
        if user is None:
            user = User(
                provider=provider,
                social_id=social_id,
                email_address=email_address,
                username=username,
            )
            db.session.add(user)
            db.session.commit()
        # Flask-Login login_user() function to record the user is logged in
        # for the user session.
        login_user(user)
        flash("Signed in successfully.", "info")
        return redirect(url_for("main.index"))

    else:
        flash("Authentication failed!", "error")
        return redirect(url_for("main.index"))

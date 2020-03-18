from flask import (
    flash,
    jsonify,
    redirect,
    current_app,
    request,
    render_template,
    url_for,
)
from flask_restful import Resource, Api
from flask_login import login_required, login_user, logout_user
from .forms import SignInForm
from .oauth2client import OAuth2Client
import requests_oauthlib
from requests_oauthlib.compliance_fixes import facebook_compliance_fix

from constants import (
    FB_AUTHORIZATION_BASE_URL,
    FB_TOKEN_URL,
    FB_CLIENT_ID,
    FB_CLIENT_SECRET,
)
from serializer import serialize
from .db import get_schema, DB as db

from .models import User  # trigger migration


class DBSchema(Resource):
    def get(self):
        schema = get_schema()
        return {"schema": serialize(schema)}


def setup_routes(app):
    api = Api(app)
    api.add_resource(DBSchema, "/api/v1/schema")

    @app.route("/")
    def index():
        return render_template("main/index.html", title="Welcome to MYAPP")

    @app.route("/fb-login")
    def login():
        fb_client_id = current_app.config[FB_CLIENT_ID]
        base_url = current_app.config["BASE_URL"]
        facebook = requests_oauthlib.OAuth2Session(
            fb_client_id, redirect_uri=base_url + "/fb-callback", scope=["email"]
        )
        authorization_url, _ = facebook.authorization_url(FB_AUTHORIZATION_BASE_URL)

        return redirect(authorization_url)

    @app.route("/fb-callback")
    def callback():
        # issue new token
        fb_client_id = current_app.config[FB_CLIENT_ID]
        fb_client_secret = current_app.config[FB_CLIENT_SECRET]
        try:
            base_url = current_app.config["BASE_URL"]
            facebook = requests_oauthlib.OAuth2Session(
                fb_client_id, scope=["email"], redirect_uri=f"{base_url}/fb-callback"
            )

            # we need to apply a fix for Facebook here
            facebook = facebook_compliance_fix(facebook)

            # ngrok forwards to http
            url = request.url.replace("http:", "https:")
            facebook.fetch_token(
                FB_TOKEN_URL, client_secret=fb_client_secret, authorization_response=url
            )
        except Exception:
            redirect("/fb-login")

        return jsonify({"resource": "some protected resource"})

    @app.route("/sign-in", methods=["GET", "POST"])
    def signin():
        """ Default route that allows you to sign in to your account. """

        form = SignInForm()

        # HTTP POST
        if form.validate_on_submit():
            # # Validate and sign in the user.
            user = User.query.filter_by(email_address=form.email_address.data).first()
            if user is not None and user.verify_password(form.password.data):
                # Flask-Login login_user() function to record the user is logged in
                # for the user session.
                login_user(user)
                flash("Signed in successfully.", "info")
                # Post/Redirect/Get pattern, so a redirect but two possible
                # destinations. The next query string argument is used when
                # the login form was used to prevent unauthorized access.
                return redirect(request.args.get("next") or url_for("index"))

            flash("Invalid username or password.", "error")
            # Return back to homepage

        # HTTP GET
        return render_template(
            "oauth2/oauth2.html", title="Sign in to continue - MYAPP", form=form
        )

    @app.route("/sign-in/<provider>")
    def oauth2_signin(provider):
        remote_app = OAuth2Client.get_provider(provider)
        return remote_app.authorization()

    @app.route("/sign-in/<provider>/authorized")
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
            return redirect(url_for("index"))

        else:
            flash("Authentication failed!", "error")
            return redirect(url_for("index"))

    @app.route("/sign-out")
    @login_required
    def signout():
        # Remove oauth2_token from session
        OAuth2Client.signout()
        # Flask-Login logout_user() function to remove and reset user session.
        logout_user()
        flash("Signed out successfully.", "info")
        return redirect(url_for("signin"))

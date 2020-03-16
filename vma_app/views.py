from flask import jsonify, render_template, redirect, current_app, request
import requests_oauthlib
from requests_oauthlib.compliance_fixes import facebook_compliance_fix

from config import FB_AUTHORIZATION_BASE_URL, FB_TOKEN_URL, BASE_URL
from serializer import serialize
from .db import get_schema

from .models import User  # trigger migration


def setup_routes(app):
    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/api/get-schema")
    def shema_view():
        schema = get_schema()
        return jsonify({"schema": serialize(schema)})

    @app.route("/fb-login")
    def login():
        fb_client_id = current_app.config["FB_CLIENT_ID"]
        facebook = requests_oauthlib.OAuth2Session(
            fb_client_id, redirect_uri=BASE_URL + "/fb-callback", scope=["email"]
        )
        authorization_url, _ = facebook.authorization_url(FB_AUTHORIZATION_BASE_URL)

        return redirect(authorization_url)

    @app.route("/fb-callback")
    def callback():
        # issue new token
        fb_client_id = current_app.config["FB_CLIENT_ID"]
        fb_client_secret = current_app.config["FB_CLIENT_SECRET"]
        try:
            facebook = requests_oauthlib.OAuth2Session(
                fb_client_id, scope=["email"], redirect_uri=BASE_URL + "/fb-callback"
            )

            # we need to apply a fix for Facebook here
            facebook = facebook_compliance_fix(facebook)

            url = request.url.replace("http:", "https:")
            facebook.fetch_token(
                FB_TOKEN_URL, client_secret=fb_client_secret, authorization_response=url
            )

        except Exception:
            redirect("/fb-login")

        return jsonify({"resource": "some protected resource"})

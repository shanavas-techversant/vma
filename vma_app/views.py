from flask import jsonify, redirect, current_app, request
from flask_restful import Resource, Api
import requests_oauthlib
from requests_oauthlib.compliance_fixes import facebook_compliance_fix

from constants import FB_AUTHORIZATION_BASE_URL, FB_TOKEN_URL, FB_CLIENT_ID, FB_CLIENT_SECRET
from serializer import serialize
from .db import get_schema

from .models import User  # trigger migration


class Home(Resource):
    def get(self):
        return {"data": "home page"}


class DBSchema(Resource):
    def get(self):
        schema = get_schema()
        return {"schema": serialize(schema)}


def setup_routes(app):
    api = Api(app)
    api.add_resource(Home, '/')
    api.add_resource(DBSchema, '/api/v1/schema')

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

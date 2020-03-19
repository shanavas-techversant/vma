from flask import g, jsonify
from flask_login import LoginManager
from flask_oauthlib.client import OAuth
from flask_jwt_extended import JWTManager
# from flask_wtf.csrf import CSRFProtect

from .models import User, BlacklistToken


# CSRF Protection
# http://flask-wtf.readthedocs.io/en/stable/csrf.html
# csrf = CSRFProtect()

# Flask-Login
# https://flask-login.readthedocs.io
login_manager = LoginManager()


# When a user attempts to access a login_required view without being logged in,
# Flask-Login will flash a message and redirect them to the log in view.
# This endpoint is set with attribute login_view.
login_manager.login_view = 'signin'

# Custom default message flashed.
login_manager.login_message = u'Please sign in to access this page.'

# The session_protection attribute will help to protect the users' sessions
# from being stolen. When active, each request generates an identifier for the
# user's computer (secure hash of IP and user agent). If the newly generated
# and stored identifiers do not match for a non-permanent session, the entire
# session (including remember me token) is deleted.
# It can also be set in the application config with SESSION_PROTECTION
login_manager.session_protection = 'strong'


@login_manager.user_loader
def load_user(id):
    """
    Flask-Login user_loader callback is used to reload the user object from
    the user ID stored in the session. It takes the unicode ID of a user,
    and returns the corresponding user object.

    Args:
        id: user identifier as Unicode string

    Returns:
        User object if available or None otherwise.
    """
    return User.query.get(int(id))


# Flask-OAuthlib
# http://flask-oauthlib.readthedocs.io
oauth = OAuth()


# Flask jwt auth extended
jwt_auth = JWTManager()


@jwt_auth.user_identity_loader
def user_identity_lookup(user):
    return user.id


# sets flask_jwt_extended.current_user
@jwt_auth.user_loader_callback_loader
def user_loader_callback(identity):
    return User.query.get(identity)


# call back for user load failure
@jwt_auth.user_loader_error_loader
def custom_user_loader_error(identity):
    ret = {
        "msg": "User {} not found".format(identity)
    }
    return jsonify(ret), 404


@jwt_auth.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return BlacklistToken.is_blacklisted(jti)

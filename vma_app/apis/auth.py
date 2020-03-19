from flask import Blueprint, request
from flask_restful import Resource, Api, reqparse

from ..db import DB as db
from ..models import User, BlacklistToken
from ..extensions import auth

auth_blueprint = Blueprint("api", __name__, url_prefix="/api/v1")
api = Api(auth_blueprint)

login_parser = reqparse.RequestParser()
login_parser.add_argument('email', required=True)
login_parser.add_argument('password', required=True)


class LoginAPI(Resource):
    """
    User Login Resource
    """
    def post(self):
        # get the post data
        post_data = login_parser.parse_args()

        try:
            # fetch the user data
            user = User.query.filter_by(
                email_address=post_data.get('email')
            ).first()
            if user and user.verify_password(post_data.get('password')):
                auth_token = user.encode_auth_token()
                if auth_token:
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token.decode()
                    }
                    status = 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': 'Invalid email/password'
                }
                status = 400
        except Exception as e:
            # TODO log it
            responseObject = {
                'status': 'fail',
                'message': 'Error occurred. Try again'
            }
            status = 500

        return responseObject, status


class LogoutAPI(Resource):
    """
    Logout Resource
    """
    decorators = [
        auth.login_required,
    ]

    def post(self):
        # get auth token
        auth_header = request.headers.get('Authorization', '')
        auth_token = auth_header.split(" ")[1]
        blacklist_token = BlacklistToken(token=auth_token)
        try:
            # insert the token
            db.session.add(blacklist_token)
            db.session.commit()
            responseObject = {
                'status': 'success',
                'message': 'Successfully logged out.'
            }
            status = 200
        except Exception as e:
            # TODO log it
            responseObject = {
                'status': 'fail',
                'message': 'Error occured. Try again'
            }
            status = 500
        return responseObject, status


api.add_resource(LoginAPI, "/login")
api.add_resource(LogoutAPI, "/logout")

from flask import Blueprint
from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_raw_jwt,
    current_user,
)
from flask_restful import Resource, Api, reqparse

from ..db import DB as db
from ..models import User, BlacklistToken

auth_blueprint = Blueprint("api", __name__, url_prefix="/api/v1/auth")
api = Api(auth_blueprint)

login_parser = reqparse.RequestParser()
login_parser.add_argument("email", required=True)
login_parser.add_argument("password", required=True)


class LoginAPI(Resource):
    """
    User Login Resource
    """

    def post(self):
        # get the post data
        post_data = login_parser.parse_args()

        try:
            # fetch the user data
            user = User.query.filter_by(email_address=post_data.get("email")).first()
            if user and user.verify_password(post_data.get("password")):
                access_token = create_access_token(identity=user)
                refresh_token = create_refresh_token(identity=user)

                responseObject = {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
                status = 200
            else:
                responseObject = {
                    "status": "fail",
                    "message": "Invalid email or password",
                }
                status = 400
        except Exception as e:
            # TODO log it
            responseObject = {"status": "fail", "message": "Error occurred. Try again"}
            status = 500

        return responseObject, status


class RefreshAPI(Resource):
    decorators = [jwt_refresh_token_required]

    def post(self):
        ret = {"access_token": create_access_token(identity=current_user)}
        return ret, 200


class LogoutAPI(Resource):
    """
    Logout Resource
    """

    decorators = [jwt_required]

    def post(self):
        try:
            jti = get_raw_jwt()["jti"]
            blacklist = BlacklistToken(jti)
            db.session.add(blacklist)
            db.session.commit()
            return {"msg": "Successfully logged out"}, 200
        except Exception:
            return {"status": "fail", "message": "Error occurred. Try again"}, 500


class MeAPI(Resource):
    """
    User Resource
    """

    decorators = [jwt_required]

    def get(self):
        try:
            return current_user.to_dict(), 200
        except Exception:
            return {"status": "fail", "message": "Error occurred. Try again"}, 500


api.add_resource(LoginAPI, "/login")
api.add_resource(RefreshAPI, "/refresh")
api.add_resource(LogoutAPI, "/logout")
api.add_resource(MeAPI, "/me")

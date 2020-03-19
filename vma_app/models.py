from datetime import datetime
import random
import string

from flask_login import UserMixin
from sqlalchemy.sql import func

from .utils import generate_argon2_hash, check_argon2_hash
from .db import DB as db


class User(UserMixin, db.Model):

    """
    Maps subclass of declarative_base() to a Python class
    to table users_oauth2.
    UserMixin provides default implementations for the methods that Flask-Login
    expects user objects to have:
    is_active, is_authenticated, is_anonymous, get_id
    """

    __tablename__ = "users"

    id = db.Column(db.Integer)
    provider = db.Column(db.String, nullable=False, default="local")
    social_id = db.Column(db.String, nullable=False, default="0")
    email_address = db.Column(db.String)
    username = db.Column(db.String)
    password_hash = db.Column(db.String)
    created_date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_date = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    # __table_args__ value must be a tuple, dict, or None
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="pk_users"),
        db.UniqueConstraint("provider", "social_id", name="uq_users_1"),
    )

    def generate_social_id(size=20, chars=string.digits):
        """
        Generates a social_id that can be used for local myapp users.
        It's big enough so that it should be unique.

        Returns:
            social_id
        """
        return "".join(random.SystemRandom().choice(chars) for _ in range(size))

    @property
    def password(self):
        """
        The password property will call generate_argon2_hash and
        write the result to the password_hash field.
        Reading this property will return an error.
        """
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_argon2_hash(password)

    def verify_password(self, password):
        """
        Verifies the password against the hashed version stored
        in the User model.
        """
        return check_argon2_hash(password, self.password_hash)

    def __init__(self, email_address, username=None, provider="local", social_id=0):
        self.email_address = email_address
        self.username = username if username else self.email_address
        self.provider = provider
        self.social_id = social_id

    def to_dict(self):
        """ Convert the model to a dictionary that can go into a JSON """
        return {
            "id": self.id,
            "provider": self.provider,
            "social_id": self.social_id,
            "email_address": self.email_address,
            "username": self.username,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
        }


class BlacklistToken(db.Model):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.utcnow()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def is_blacklisted(auth_token):
        # check whether auth token has been blacklisted
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        return bool(res)

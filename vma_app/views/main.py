from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, login_user, logout_user

from ..forms import SignInForm
from ..models import User
from ..oauth2client import OAuth2Client


main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/")
def index():
    return render_template("main/index.html", title="Welcome to MYAPP")


@main_blueprint.route("/sign-in", methods=["GET", "POST"])
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
            return redirect(request.args.get("next") or url_for("main.index"))

        flash("Invalid username or password.", "error")
        # Return back to homepage

    # HTTP GET
    return render_template(
        "oauth2/oauth2.html", title="Sign in to continue - MYAPP", form=form
    )


@main_blueprint.route("/sign-out")
@login_required
def signout():
    # Remove oauth2_token from session
    OAuth2Client.signout()
    # Flask-Login logout_user() function to remove and reset user session.
    logout_user()
    flash("Signed out successfully.", "info")
    return redirect(url_for("main.signin"))

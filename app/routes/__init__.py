from flask import Blueprint, redirect, url_for
from flask_login import current_user

route_blueprint = Blueprint("route_blueprint", __name__)


@route_blueprint.before_request
def restrict_to_logged_in_users():
    if not current_user.is_authenticated:
        return redirect(url_for("auth_bp.login"))


from app.routes import routes  # noqa: E402,F401

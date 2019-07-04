from flask import Blueprint, redirect, url_for
from flask_login import current_user

candidates_bp = Blueprint('candidates', __name__)


@candidates_bp.before_request
def restrict_to_logged_in_users():
    if not current_user.is_authenticated:
        return redirect(url_for('auth_bp.login'))


from app.candidates import routes  # noqa: E402,F401

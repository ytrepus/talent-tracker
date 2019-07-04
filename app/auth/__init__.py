from flask import Blueprint

auth_blueprint = Blueprint('auth_bp', __name__)

from app.auth import routes  # noqa: E402,F401

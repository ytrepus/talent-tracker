from flask import Blueprint, redirect, url_for
from flask_login import current_user
from app.models import db, AuditEvent

reports_bp = Blueprint('reports_bp', __name__)


@reports_bp.before_request
def restrict_to_logged_in_users():
    if not current_user.is_authenticated:
        return redirect(url_for('auth_bp.login'))


@reports_bp.before_request
def log_event():
    db.session.add(AuditEvent(user_id=current_user.id, action_taken="Generated a report"))
    db.session.commit()

from app.reports import routes  # noqa: E402,F401

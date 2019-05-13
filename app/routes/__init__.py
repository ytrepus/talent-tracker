from flask import Blueprint

route_blueprint = Blueprint('route_blueprint', __name__)

from app.routes import routes

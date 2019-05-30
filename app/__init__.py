from flask import Flask
import secrets

import os


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.secret_key = secrets.token_urlsafe(64)

    from app.models import db, login_manager, migrate
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "route_blueprint.login"

    from app.routes import route_blueprint
    app.register_blueprint(route_blueprint)
    return app



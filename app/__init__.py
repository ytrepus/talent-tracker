from flask import Flask
from config import Config, TestConfig


def create_app(configuration=Config):
    app = Flask(__name__)

    from app.models import db, login_manager, migrate
    app.config.from_object(configuration)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "route_blueprint.login"

    from app.routes import route_blueprint
    app.register_blueprint(route_blueprint)

    from app.auth import auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth/')

    return app



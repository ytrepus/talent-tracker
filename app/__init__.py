from flask import Flask
from flask_migrate import Migrate
from app.models import db

import os

migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import route_blueprint
    app.register_blueprint(route_blueprint)
    return app


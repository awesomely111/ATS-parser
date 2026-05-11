"""
Flask Application Factory
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():

    app = Flask(__name__)

    # CONFIG

    app.config['SECRET_KEY'] = os.getenv(
        'SECRET_KEY',
        'dev-secret-key'
    )

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'sqlite:///ats.db'
    )

    app.config['UPLOAD_FOLDER'] = os.getenv(
        'UPLOAD_FOLDER',
        'uploads'
    )

    app.config['MAX_CONTENT_LENGTH'] = int(
        os.getenv('MAX_CONTENT_LENGTH', 16777216)
    )

    # CREATE UPLOADS FOLDER

    os.makedirs(
        app.config['UPLOAD_FOLDER'],
        exist_ok=True
    )

    # INIT EXTENSIONS

    db.init_app(app)

    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'

    # REGISTER BLUEPRINTS

    from app.routes import (
        auth_bp,
        candidate_bp,
        admin_bp,
        chatbot_bp
    )

    app.register_blueprint(auth_bp)

    app.register_blueprint(candidate_bp)

    app.register_blueprint(admin_bp, url_prefix='/admin')

    app.register_blueprint(chatbot_bp)

    # CREATE DATABASE TABLES

    with app.app_context():
        db.create_all()

    return app


@login_manager.user_loader
def load_user(user_id):

    from app.models import User

    return User.query.get(int(user_id))
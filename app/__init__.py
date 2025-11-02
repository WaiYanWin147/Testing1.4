# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

# CHANGE: accept optional test_config so pytest can inject a temp DB, TESTING=True, etc.
def create_app(test_config: dict | None = None):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object("app.config.Config")

    # ADD: allow tests to override settings safely (e.g., SQLite tempfile / in-memory)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        # keep your entity imports exactly as-is
        from app.entity.user_profile import UserProfile
        from app.entity.user_account import UserAccount
        from app.entity.category import Category
        from app.entity.request import Request
        from app.entity.shortlist import Shortlist
        from app.entity.match_record import MatchRecord
        from app.entity.report import Report

        # OPTIONAL: if you worry about touching a prod DB during tests, you can guard:
        # if app.config.get("TESTING", False):
        #     db.create_all()
        # else:
        #     db.create_all()
        db.create_all()

        register_blueprints(app)

    login_manager.login_view = "boundary.login"

    # ADD: tiny health endpoint so CI has a deterministic check
    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    return app


def register_blueprints(app):
    from app.boundary.routes import boundary_bp
    app.register_blueprint(boundary_bp)

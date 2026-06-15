"""
Jaundice Recovery Tracker — Main Application Entry Point
"""
from flask import Flask, request, redirect, url_for
from flask_login import LoginManager, current_user
from config import Config
from models.db import init_db
from models.user import User
from dotenv import load_dotenv
import os

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize database
    init_db(app)

    # ── Flask-Login setup ────────────────────────────────────────────────────
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'          # redirect here when not logged in
    login_manager.login_message = 'Please log in to access the tracker.'
    login_manager.login_message_category = 'error'

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    # ── Global auth guard ────────────────────────────────────────────────────
    @app.before_request
    def require_login():
        """Redirect unauthenticated users to login for every route except auth & static."""
        public_endpoints = {'auth.login', 'static'}
        if not current_user.is_authenticated and request.endpoint not in public_endpoints:
            return redirect(url_for('auth.login', next=request.path))

    # ── Register blueprints ──────────────────────────────────────────────────
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.timeline import timeline_bp
    from routes.lab_results import lab_results_bp
    from routes.reports import reports_bp
    from routes.medications import medications_bp
    from routes.journal import journal_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(timeline_bp)
    app.register_blueprint(lab_results_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(medications_bp)
    app.register_blueprint(journal_bp)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)

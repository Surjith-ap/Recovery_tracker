"""
Jaundice Recovery Tracker — Main Application Entry Point
"""
from flask import Flask
from config import Config
from models.db import init_db
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize database
    init_db(app)

    # Register blueprints
    from routes.dashboard import dashboard_bp
    from routes.timeline import timeline_bp
    from routes.lab_results import lab_results_bp
    from routes.reports import reports_bp
    from routes.medications import medications_bp
    from routes.journal import journal_bp

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

"""
Configuration settings for Jaundice Recovery Tracker
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # IMPORTANT: Set SECRET_KEY as an environment variable in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = db_url or 'sqlite:///' + os.path.join(BASE_DIR, 'jaundice_tracker.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

    # Diagnosis date - update this to your actual diagnosis date
    DIAGNOSIS_DATE = '2026-05-31'

    # Admin credentials — set these in your .env file
    # Generate hash: python setup_password.py
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
    ADMIN_PASSWORD_HASH = os.environ.get('ADMIN_PASSWORD_HASH')

import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # SQLite Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # SMTP Configuration - Flask-Mail (Production Ready - Forced Values)
    MAIL_SERVER = 'smtp.gmail.com'  # Forzado explícito
    MAIL_PORT = 587  # Forzado explícito
    MAIL_USE_TLS = True  # Forzado explícito
    MAIL_USE_SSL = False  # Forzado explícito
    MAIL_USERNAME = os.environ.get('EMAIL_USER')  # App Password (16 chars)
    MAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')  # App Password (16 chars)
    MAIL_DEFAULT_SENDER = os.environ.get('EMAIL_USER')

    # Legacy SMTP (for backward compatibility with existing code)
    SMTP_SERVER = 'smtp.gmail.com'  # Forzado explícito
    SMTP_PORT = 587  # Forzado explícito
    SMTP_USER = os.environ.get('EMAIL_USER')
    SMTP_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    SMTP_FROM_EMAIL = os.environ.get('EMAIL_USER')
    SMTP_TO_EMAIL = os.environ.get('EMAIL_USER')

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

    # SMTP Configuration
    SMTP_SERVER = os.environ.get('SMTP_SERVER')
    SMTP_PORT = int(os.environ.get('SMTP_PORT'))
    SMTP_USER = os.environ.get('EMAIL_USER')
    SMTP_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    SMTP_FROM_EMAIL = os.environ.get('SMTP_FROM_EMAIL')
    SMTP_TO_EMAIL = os.environ.get('SMTP_TO_EMAIL')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'

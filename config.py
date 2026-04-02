import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'camara-comercio-secret-key-2026'

    # SQLite Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///camara_comercio.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # SMTP Configuration
    SMTP_SERVER = os.environ.get('SMTP_SERVER') or 'smtp.gmail.com'
    SMTP_PORT = int(os.environ.get('SMTP_PORT') or 587)
    SMTP_USER = os.environ.get('SMTP_USER') or 'secretariacamaraanaco@gmail.com'
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD') or 'woaddhypawapizej'
    SMTP_FROM_EMAIL = os.environ.get('SMTP_FROM_EMAIL') or 'secretariacamaraanaco@gmail.com'
    SMTP_TO_EMAIL = os.environ.get('SMTP_TO_EMAIL') or 'secretariacamaraanaco@gmail.com'

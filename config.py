
import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables from .env
load_dotenv()


class Config:
    """
    Main configuration class for InterviewAce AI
    """

    # ==========================================
    # FLASK CONFIGURATION
    # ==========================================
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "interviewace-super-secret-key-change-this"
    )

    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # ==========================================
    # APPLICATION SETTINGS
    # ==========================================
    APP_NAME = os.getenv("APP_NAME", "InterviewAce AI")
    APP_URL = os.getenv("APP_URL", "http://127.0.0.1:5000")

    # ==========================================
    # MYSQL DATABASE CONFIGURATION
    # ==========================================
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "interviewace_ai")

    # ==========================================
    # GOOGLE GEMINI API
    # ==========================================
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    # ==========================================
    # SESSION CONFIGURATION
    # ==========================================
    SESSION_COOKIE_HTTPONLY = (
        os.getenv("SESSION_COOKIE_HTTPONLY", "True").lower() == "true"
    )

    SESSION_COOKIE_SECURE = (
        os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
    )

    PERMANENT_SESSION_LIFETIME = timedelta(
        minutes=int(
            os.getenv("PERMANENT_SESSION_LIFETIME", 60)
        )
    )

    # ==========================================
    # FILE UPLOAD SETTINGS
    # ==========================================
    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER",
        "static/uploads"
    )

    MAX_CONTENT_LENGTH = int(
        os.getenv(
            "MAX_CONTENT_LENGTH",
            16 * 1024 * 1024
        )
    )

    # ==========================================
    # REPORT SETTINGS
    # ==========================================
    REPORT_FOLDER = os.getenv(
        "REPORT_FOLDER",
        "static/reports"
    )

    # ==========================================
    # EMAIL SETTINGS
    # ==========================================
    MAIL_SERVER = os.getenv(
        "MAIL_SERVER",
        "smtp.gmail.com"
    )

    MAIL_PORT = int(
        os.getenv(
            "MAIL_PORT",
            587
        )
    )

    MAIL_USERNAME = os.getenv(
        "MAIL_USERNAME",
        ""
    )

    MAIL_PASSWORD = os.getenv(
        "MAIL_PASSWORD",
        ""
    )

    MAIL_USE_TLS = (
        os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    )

    MAIL_USE_SSL = (
        os.getenv("MAIL_USE_SSL", "False").lower() == "true"
    )

    # ==========================================
    # ALLOWED FILE TYPES
    # ==========================================
    ALLOWED_EXTENSIONS = {
        "pdf",
        "doc",
        "docx"
    }

    # ==========================================
    # GEMINI MODEL
    # ==========================================
    GEMINI_MODEL = "gemini-2.5-flash"

    # ==========================================
    # PASSWORD RULES
    # ==========================================
    MIN_PASSWORD_LENGTH = 8

    # ==========================================
    # STATIC PATHS
    # ==========================================
    STATIC_FOLDER = "static"
    TEMPLATE_FOLDER = "templates"

    @staticmethod
    def init_app(app):
        """
        Initialize application directories
        """

        os.makedirs(
            Config.UPLOAD_FOLDER,
            exist_ok=True
        )

        os.makedirs(
            Config.REPORT_FOLDER,
            exist_ok=True
        )


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}


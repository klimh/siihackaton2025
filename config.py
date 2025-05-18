import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-this-in-production')
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///mental_health.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Application configuration
    APP_NAME = "Mental Health Support"
    MOOD_SCALE_MIN = 1
    MOOD_SCALE_MAX = 10
    
    # Security configuration
    BCRYPT_LOG_ROUNDS = 12  # For password hashing
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'
    REMEMBER_COOKIE_HTTPONLY = True 
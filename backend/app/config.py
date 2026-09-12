import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parent

for env_path in (PROJECT_ROOT / '.env', BASE_DIR / '.env'):
    if env_path.exists():
        load_dotenv(env_path, override=False)


def get_config():
    testing = os.getenv('TESTING') == 'true'
    default_database_url = 'sqlite:///:memory:' if testing else 'sqlite:///postgen_ai.db'
    database_url = os.getenv('DATABASE_URL') or default_database_url
    cors_origins = os.getenv('CORS_ORIGINS') or 'http://localhost:5173,http://localhost:5174,http://localhost:5175,http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:5175'

    return {
        'DATABASE_URL': database_url,
        'TESTING': testing,
        'SECRET_KEY': os.getenv('JWT_SECRET_KEY') or os.getenv('SECRET_KEY') or 'development-secret-key-1234567890abcd',
        'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY') or os.getenv('SECRET_KEY') or 'dev-jwt-secret-key-1234567890abcd',
        'JWT_REFRESH_SECRET_KEY': os.getenv('JWT_REFRESH_SECRET_KEY') or 'dev-refresh-secret-key-1234567890abcd',
        'JWT_ACCESS_TOKEN_EXPIRES': timedelta(hours=1),
        'JWT_REFRESH_TOKEN_EXPIRES': timedelta(days=7),
        'JWT_TOKEN_LOCATION': ['headers'],
        'JWT_HEADER_NAME': 'Authorization',
        'JWT_HEADER_TYPE': 'Bearer',
        'CORS_ORIGINS': [
            origin.strip()
            for origin in cors_origins.split(',')
            if origin.strip()
        ],
        'DEBUG': os.getenv('FLASK_ENV', 'development') == 'development' and not testing,
        'SQLALCHEMY_DATABASE_URI': database_url,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'ENCRYPTION_KEY': os.getenv('ENCRYPTION_KEY') or 'YpF0G6H0i8rFJkP6S7Mt1I7nD3qcV3q6e1O0wT6HUKM=',
        'RATELIMIT_DEFAULT': '5/minute',
        'PROPAGATE_EXCEPTIONS': True,
    }

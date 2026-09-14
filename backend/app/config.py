import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parent

for env_path in (
    PROJECT_ROOT / '.env',
    BASE_DIR / '.env',
    Path.cwd() / '.env',
):
    if env_path.exists():
        load_dotenv(env_path, override=True)


def _require_secret(name: str, *, minimum_bytes: int = 32):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f'{name} must be configured in environment variables.')
    if len(value.encode('utf-8')) < minimum_bytes:
        raise RuntimeError(f'{name} must be at least {minimum_bytes} bytes long for SHA256 security.')
    return value


def get_config():
    testing = os.getenv('TESTING') == 'true'
    database_url = os.getenv('DATABASE_URL') or ('sqlite:///:memory:' if testing else 'sqlite:///postgen_ai.db')
    cors_origins = os.getenv('CORS_ORIGINS') or 'http://localhost:5173,http://localhost:5174,http://localhost:5175,http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:5175'
    secret_key = os.getenv('SECRET_KEY') or os.getenv('JWT_SECRET_KEY')
    jwt_secret = os.getenv('JWT_SECRET_KEY')
    jwt_refresh_secret = os.getenv('JWT_REFRESH_SECRET_KEY')

    if not testing:
        secret_key = _require_secret('SECRET_KEY') if not secret_key else secret_key
        jwt_secret = _require_secret('JWT_SECRET_KEY') if not jwt_secret else jwt_secret
        jwt_refresh_secret = _require_secret('JWT_REFRESH_SECRET_KEY') if not jwt_refresh_secret else jwt_refresh_secret
    else:
        secret_key = secret_key or 'test-secret-key-12345678901234567890'
        jwt_secret = jwt_secret or 'test-jwt-secret-key-12345678901234567890'
        jwt_refresh_secret = jwt_refresh_secret or 'test-jwt-refresh-secret-key-12345678901234567890'

    if len(secret_key.encode('utf-8')) < 32:
        raise RuntimeError('SECRET_KEY must be at least 32 bytes long for SHA256 security.')
    if len(jwt_secret.encode('utf-8')) < 32:
        raise RuntimeError('JWT_SECRET_KEY must be at least 32 bytes long for SHA256 security.')
    if len(jwt_refresh_secret.encode('utf-8')) < 32:
        raise RuntimeError('JWT_REFRESH_SECRET_KEY must be at least 32 bytes long for SHA256 security.')

    return {
        'DATABASE_URL': database_url,
        'TESTING': testing,
        'SECRET_KEY': secret_key,
        'JWT_SECRET_KEY': jwt_secret,
        'JWT_REFRESH_SECRET_KEY': jwt_refresh_secret,
        'JWT_ACCESS_TOKEN_EXPIRES': timedelta(minutes=15),
        'JWT_REFRESH_TOKEN_EXPIRES': timedelta(days=7),
        'JWT_TOKEN_LOCATION': ['headers', 'cookies'],
        'JWT_HEADER_NAME': 'Authorization',
        'JWT_HEADER_TYPE': 'Bearer',
        'JWT_COOKIE_SECURE': not testing,
        'JWT_COOKIE_SAMESITE': 'Lax',
        'JWT_COOKIE_HTTPONLY': True,
        'JWT_BLACKLIST_ENABLED': True,
        'CORS_ORIGINS': [
            origin.strip()
            for origin in cors_origins.split(',')
            if origin.strip()
        ],
        'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID', ''),
        'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET', ''),
        'GOOGLE_REDIRECT_URI': os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/api/auth/google/callback'),
        'FRONTEND_BASE_URL': os.getenv('FRONTEND_BASE_URL', 'http://localhost:5173'),
        'SMTP_HOST': os.getenv('SMTP_HOST', ''),
        'SMTP_PORT': int(os.getenv('SMTP_PORT', 587)),
        'SMTP_USERNAME': os.getenv('SMTP_USERNAME', ''),
        'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD', ''),
        'SMTP_FROM_EMAIL': os.getenv('SMTP_FROM_EMAIL', 'noreply@postgen-ai.local'),
        'DEBUG': os.getenv('FLASK_ENV', 'development') == 'development' and not testing,
        'SQLALCHEMY_DATABASE_URI': database_url,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'ENCRYPTION_KEY': os.getenv('ENCRYPTION_KEY') or 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=',
        'RATELIMIT_DEFAULT': os.getenv('RATELIMIT_DEFAULT', '10/minute'),
        'MAX_CONTENT_LENGTH': int(os.getenv('MAX_REQUEST_SIZE', 1048576)),
        'PROPAGATE_EXCEPTIONS': True,
        'JSON_SORT_KEYS': False,
        'AI_MAX_INPUT_CHARS': int(os.getenv('AI_MAX_INPUT_CHARS', 4000)),
        'AI_MAX_OUTPUT_CHARS': int(os.getenv('AI_MAX_OUTPUT_CHARS', 2500)),
        'AI_REQUEST_TIMEOUT': int(os.getenv('AI_REQUEST_TIMEOUT', 20)),
        'AI_GENERATION_LIMIT_PER_USER': int(os.getenv('AI_GENERATION_LIMIT_PER_USER', 10)),
        'SESSION_COOKIE_SECURE': not testing,
        'SESSION_COOKIE_HTTPONLY': True,
        'SESSION_COOKIE_SAMESITE': 'Lax',
        'PREFERRED_URL_SCHEME': 'https' if not testing else 'http',
    }

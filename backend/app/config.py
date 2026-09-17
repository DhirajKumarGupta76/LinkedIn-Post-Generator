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
        # Do not override vars already set by the process (tests, shells, CI).
        load_dotenv(env_path, override=False)


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

    # Vercel serverless filesystem is read-only except /tmp. Prefer a real Postgres DATABASE_URL.
    if not testing and os.getenv('VERCEL') and database_url.startswith('sqlite:///'):
        database_url = 'sqlite:////tmp/postgen_ai.db'

    default_cors = (
        'http://localhost:5173,http://localhost:5174,http://localhost:5175,'
        'http://localhost:5182,http://localhost:5183,'
        'http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:5175,'
        'http://127.0.0.1:5182,http://127.0.0.1:5183,'
        'https://linked-in-post-generator-dhiru.vercel.app,'
        'https://linked-in-post-generator-git-main-dhiru.vercel.app,'
        'https://linked-in-post-generator-oj3d55zyg-dhiru.vercel.app'
    )
    cors_origins = os.getenv('CORS_ORIGINS') or default_cors
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

    on_vercel = bool(os.getenv('VERCEL'))
    flask_env = os.getenv('FLASK_ENV', 'production' if on_vercel else 'development')
    debug = flask_env == 'development' and not testing and not on_vercel

    cookie_secure_env = os.getenv('COOKIE_SECURE')
    if testing:
        cookie_secure = False
    elif cookie_secure_env is not None:
        cookie_secure = cookie_secure_env.lower() == 'true'
    else:
        # Secure cookies on Vercel/HTTPS hosts only. Local HTTP keeps Secure=False
        # even if FLASK_ENV was set to production by mistake.
        cookie_secure = on_vercel or (
            flask_env == 'production' and os.getenv('FORCE_HTTPS', '').lower() == 'true'
        )

    # Canonical production host for this project (not preview/alias hosts like *-wheat-*).
    canonical_production_origin = 'https://linked-in-post-generator-dhiru.vercel.app'

    frontend_base_url = os.getenv('FRONTEND_BASE_URL')
    if not frontend_base_url:
        if on_vercel:
            # Prefer the stable dhiru production domain over VERCEL_PROJECT_PRODUCTION_URL,
            # which can point at an alternate/alias deployment host.
            frontend_base_url = canonical_production_origin
        else:
            frontend_base_url = 'http://localhost:5173'

    google_redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
    if not google_redirect_uri:
        if on_vercel:
            google_redirect_uri = f'{canonical_production_origin}/api/auth/google/callback'
        else:
            google_redirect_uri = 'http://localhost:5000/api/auth/google/callback'

    origin_set = []
    for origin in cors_origins.split(','):
        cleaned = origin.strip().rstrip('/')
        if cleaned and cleaned not in origin_set:
            origin_set.append(cleaned)

    # Always allow the configured frontend and Vercel deployment hosts.
    for candidate in (
        frontend_base_url,
        os.getenv('VERCEL_URL'),
        os.getenv('VERCEL_BRANCH_URL'),
        os.getenv('VERCEL_PROJECT_PRODUCTION_URL'),
    ):
        if not candidate:
            continue
        origin = candidate if candidate.startswith('http') else f'https://{candidate}'
        origin = origin.rstrip('/')
        if origin not in origin_set:
            origin_set.append(origin)

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
        'JWT_COOKIE_SECURE': cookie_secure,
        'JWT_COOKIE_SAMESITE': 'Lax',
        'JWT_COOKIE_HTTPONLY': True,
        'JWT_COOKIE_CSRF_PROTECT': False,
        'JWT_BLACKLIST_ENABLED': True,
        'CORS_ORIGINS': origin_set,
        'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID', ''),
        'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET', ''),
        'GOOGLE_REDIRECT_URI': google_redirect_uri,
        'FRONTEND_BASE_URL': frontend_base_url.rstrip('/'),
        'SMTP_HOST': os.getenv('SMTP_HOST', ''),
        'SMTP_PORT': int(os.getenv('SMTP_PORT', 587)),
        'SMTP_USERNAME': os.getenv('SMTP_USERNAME', ''),
        'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD', ''),
        'SMTP_FROM_EMAIL': os.getenv('SMTP_FROM_EMAIL', 'noreply@postgen-ai.local'),
        'DEBUG': debug,
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
        'SESSION_COOKIE_SECURE': cookie_secure,
        'SESSION_COOKIE_HTTPONLY': True,
        'SESSION_COOKIE_SAMESITE': 'Lax',
        'PREFERRED_URL_SCHEME': 'https' if cookie_secure else 'http',
    }

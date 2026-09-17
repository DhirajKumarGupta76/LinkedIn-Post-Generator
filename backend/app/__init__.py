import logging
import time
import uuid
from collections import defaultdict, deque

from flask import Flask, g, jsonify, request
from flask_cors import CORS
from flask_limiter.errors import RateLimitExceeded
from dotenv import load_dotenv
from sqlalchemy import inspect, text
from werkzeug.middleware.proxy_fix import ProxyFix

from app.config import get_config
from app.extensions import db, jwt, limiter, migrate
from app.models.user import User


def ensure_database_schema(app):
    # Import models so metadata is complete before create_all.
    import app.models.generated_post  # noqa: F401
    import app.models.saved_post  # noqa: F401

    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table('users'):
            db.create_all()
            return

        existing_columns = {column['name'] for column in inspector.get_columns('users')}
        missing_columns = [
            column for column in User.__table__.columns
            if column.name not in existing_columns
        ]

        for column in missing_columns:
            column_type = column.type.compile(dialect=db.engine.dialect)
            try:
                db.session.execute(text(f'ALTER TABLE users ADD COLUMN {column.name} {column_type}'))
            except Exception:
                db.session.rollback()
                raise

        if missing_columns:
            db.session.commit()


def create_app(config_overrides=None):
    load_dotenv()

    app = Flask(__name__)
    # Trust Vercel / reverse-proxy headers so request.url_root is https://...
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    app.config.update(get_config())
    if config_overrides:
        app.config.update(config_overrides)
    if not app.config.get('TESTING'):
        app.config.setdefault('JSON_AS_ASCII', False)
    app.config.setdefault('JWT_BLOCKLIST', set())
    app.config.setdefault('USER_GENERATION_HISTORY', defaultdict(deque))
    app.config.setdefault('GENERATION_LIMIT_PER_USER', app.config.get('AI_GENERATION_LIMIT_PER_USER', 10))

    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)

    cors_origins = app.config.get('CORS_ORIGINS', ['http://localhost:5173'])
    if isinstance(cors_origins, str):
        cors_origins = [cors_origins]

    CORS(
        app,
        origins=cors_origins,
        supports_credentials=True,
        allow_headers=['Content-Type', 'Authorization'],
        methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
        expose_headers=['Content-Type', 'Authorization', 'X-Request-ID'],
        max_age=600,
    )

    @app.before_request
    def enforce_security_controls():
        g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        g.request_started = time.perf_counter()

        if request.content_length and request.content_length > app.config.get('MAX_CONTENT_LENGTH', 1048576):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PAYLOAD_TOO_LARGE',
                    'message': 'Request payload exceeds the allowed size.',
                }
            }), 413

        if request.method in {'POST', 'PUT', 'PATCH'} and request.data and request.mimetype not in {'application/json'}:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNSUPPORTED_MEDIA_TYPE',
                    'message': 'Only JSON payloads are supported for this endpoint.',
                }
            }), 415

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains' if not app.config.get('TESTING') else 'max-age=0'
        response.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; object-src 'none'; base-uri 'self';"
        response.headers['X-Request-ID'] = g.get('request_id', str(uuid.uuid4()))

        if request.path.startswith('/api/'):
            request_started = getattr(g, 'request_started', time.perf_counter())
            duration_ms = round((time.perf_counter() - request_started) * 1000, 2)
            app.logger.info(
                'api_request',
                extra={
                    'request_id': g.get('request_id'),
                    'endpoint': request.path,
                    'status': response.status_code,
                    'response_time_ms': duration_ms,
                    'method': request.method,
                },
            )
        return response

    @app.errorhandler(404)
    def not_found_error(_error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Resource not found.',
            }
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'METHOD_NOT_ALLOWED',
                'message': 'Method not allowed.',
            }
        }), 405

    @app.errorhandler(413)
    def payload_too_large(_error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'PAYLOAD_TOO_LARGE',
                'message': 'Request payload exceeds the allowed size.',
            }
        }), 413

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit_error(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'RATE_LIMIT_EXCEEDED',
                'message': 'Too many requests. Please try again later.',
            }
        }), 429

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.exception('Unhandled server error: %s', error)
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An unexpected error occurred.',
            }
        }), 500

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'error': {
                'code': 'TOKEN_EXPIRED',
                'message': 'Token has expired. Please log in again.',
            }
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(_error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_TOKEN',
                'message': 'Token is invalid.',
            }
        }), 401

    @jwt.unauthorized_loader
    def unauthorized_response(_callback):
        return jsonify({
            'success': False,
            'error': {
                'code': 'AUTH_REQUIRED',
                'message': 'Authentication required.',
            }
        }), 401

    @jwt.token_in_blocklist_loader
    def token_in_blocklist_callback(_jwt_header, jwt_payload):
        jti = jwt_payload.get('jti')
        if not jti:
            return False
        blocklist = app.config.get('JWT_BLOCKLIST', set())
        return jti in blocklist

    @jwt.revoked_token_loader
    def revoked_token_callback(_jwt_header, _jwt_payload):
        return jsonify({
            'success': False,
            'error': {
                'code': 'TOKEN_REVOKED',
                'message': 'Token has been revoked.',
            }
        }), 401

    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

    from app.routes.health import health_bp
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.posts import posts_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(posts_bp)

    return app

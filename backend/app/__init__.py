from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from app.config import get_config
from app.extensions import db, jwt, limiter


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.update(get_config())

    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)

    cors_origins = app.config.get('CORS_ORIGINS', ['http://localhost:5173'])
    if isinstance(cors_origins, str):
        cors_origins = [cors_origins]

    CORS(
        app,
        resources={r'/api/*': {'origins': cors_origins}},
        supports_credentials=True,
        allow_headers=['Content-Type', 'Authorization'],
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        expose_headers=['Content-Type', 'Authorization'],
    )

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline';"
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

    @app.errorhandler(500)
    def internal_error(_error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An unexpected error occurred.',
            }
        }), 500

    @jwt.unauthorized_loader
    def unauthorized_response(_callback):
        return jsonify({
            'success': False,
            'error': {
                'code': 'AUTH_REQUIRED',
                'message': 'Authentication required.',
            }
        }), 401

    from app.routes.health import health_bp
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.posts import posts_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(posts_bp)

    return app

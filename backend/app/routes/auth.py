import re

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from app import ensure_database_schema
from app.extensions import db, limiter
from app.models.user import User
from app.services.auth_service import authenticate_user, create_user, generate_tokens, hash_password, validate_password

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def build_error(code, message, status_code):
    return jsonify({
        'success': False,
        'error': {
            'code': code,
            'message': message,
        }
    }), status_code


@auth_bp.post('/register')
@limiter.limit('5/minute')
def register():
    ensure_database_schema(current_app)
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    try:
        if not name or len(name) < 2:
            return build_error('VALIDATION_ERROR', 'Name is required and must be at least 2 characters long.', 400)
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
            return build_error('VALIDATION_ERROR', 'Please enter a valid email address.', 400)
        if not password or password != confirm_password:
            return build_error('VALIDATION_ERROR', 'Passwords do not match.', 400)

        password_error = validate_password(password)
        if password_error:
            return build_error('VALIDATION_ERROR', password_error, 400)

        if User.query.filter_by(email=email).first():
            return build_error('EMAIL_ALREADY_EXISTS', 'An account with this email already exists.', 409)

        try:
            user = create_user(name=name, email=email, password=password)
        except IntegrityError:
            db.session.rollback()
            if User.query.filter_by(email=email).first():
                return build_error('EMAIL_ALREADY_EXISTS', 'An account with this email already exists.', 409)
            raise

        access_token, refresh_token = generate_tokens(user)
        response = jsonify({
            'success': True,
            'message': 'Registration successful.',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_public_dict(),
        })
        response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', secure=False, max_age=7 * 24 * 60 * 60)
        return response, 201
    except Exception:
        current_app.logger.exception('Registration failed for email=%s; payload=%s', email, data)
        return build_error('REGISTRATION_FAILED', 'Unable to create account. Please try again.', 500)


@auth_bp.post('/login')
@limiter.limit('5/minute')
def login():
    ensure_database_schema(current_app)
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password')

    try:
        if not email or not password:
            return build_error('INVALID_CREDENTIALS', 'Invalid email or password', 401)

        user = authenticate_user(email, password)
        if not user:
            return build_error('INVALID_CREDENTIALS', 'Invalid email or password', 401)

        access_token, refresh_token = generate_tokens(user)
        response = jsonify({
            'success': True,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_public_dict(),
        })
        response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', secure=False, max_age=7 * 24 * 60 * 60)
        return response, 200
    except Exception:
        current_app.logger.exception('Login failed for email=%s; payload=%s', email, data)
        return build_error('LOGIN_FAILED', 'Unable to login. Please try again.', 500)


@auth_bp.post('/logout')
@jwt_required()
def logout():
    response = jsonify({
        'success': True,
        'message': 'Logged out successfully.',
    })
    response.delete_cookie('refresh_token')
    return response, 200


@auth_bp.post('/refresh')
def refresh():
    refresh_token = request.cookies.get('refresh_token') or (request.get_json(silent=True) or {}).get('refresh_token')
    if not refresh_token:
        return build_error('INVALID_TOKEN', 'Refresh token is required.', 401)

    from flask_jwt_extended import decode_token
    try:
        payload = decode_token(refresh_token)
        identity = payload.get('sub')
    except Exception:
        return build_error('INVALID_TOKEN', 'Refresh token is invalid or expired.', 401)

    user = User.query.get(int(identity))
    if not user:
        return build_error('INVALID_TOKEN', 'Refresh token is invalid or expired.', 401)

    access_token, _ = generate_tokens(user)
    return jsonify({
        'success': True,
        'access_token': access_token,
    }), 200


@auth_bp.post('/change-password')
@jwt_required()
def change_password():
    data = request.get_json(silent=True) or {}
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not current_password or not new_password or not confirm_password:
        return build_error('VALIDATION_ERROR', 'All password fields are required.', 400)
    if new_password != confirm_password:
        return build_error('VALIDATION_ERROR', 'New passwords do not match.', 400)

    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return build_error('USER_NOT_FOUND', 'User not found.', 404)
    if not authenticate_user(user.email, current_password):
        return build_error('INVALID_CREDENTIALS', 'Current password is incorrect.', 401)

    password_error = validate_password(new_password)
    if password_error:
        return build_error('VALIDATION_ERROR', password_error, 400)

    user.password_hash = hash_password(new_password)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Password updated successfully.',
    }), 200

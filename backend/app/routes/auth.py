import re
from datetime import datetime, timezone
from urllib.parse import urlencode

import requests
from flask import Blueprint, current_app, jsonify, redirect, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from app import ensure_database_schema
from app.extensions import db, limiter
from app.models.user import User
from app.services.auth_service import (
    authenticate_user,
    clear_verification_token,
    create_or_update_oauth_user,
    create_user,
    generate_tokens,
    generate_verification_token,
    hash_password,
    hash_verification_token,
    revoke_token,
    validate_password,
    verify_email_token,
)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def build_error(code, message, status_code):
    return jsonify({
        'success': False,
        'error': {
            'code': code,
            'message': message,
        }
    }), status_code


@auth_bp.get('/google/login-url')
def google_login_url():
    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    if not client_id:
        return build_error('GOOGLE_CONFIG_MISSING', 'Google OAuth is not configured for this app.', 500)

    redirect_uri = current_app.config.get('GOOGLE_REDIRECT_URI') or request.url_root.rstrip('/') + '/api/auth/google/callback'
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'offline',
        'prompt': 'consent',
    }
    auth_url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urlencode(params)
    return jsonify({'success': True, 'auth_url': auth_url}), 200


@auth_bp.get('/google/callback')
def google_callback():
    error = request.args.get('error')
    error_description = request.args.get('error_description') or request.args.get('message')
    if error:
        frontend_url = current_app.config.get('FRONTEND_BASE_URL', 'http://localhost:5173').rstrip('/')
        callback_error = error_description or error
        query = urlencode({'google': 'error', 'message': callback_error})
        return redirect(f'{frontend_url}/login?{query}')

    code = request.args.get('code')
    if not code:
        return build_error('GOOGLE_AUTH_FAILED', 'Google login failed. Please try again.', 400)

    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
    redirect_uri = current_app.config.get('GOOGLE_REDIRECT_URI') or request.url_root.rstrip('/') + '/api/auth/google/callback'

    if not client_id or not client_secret:
        return build_error('GOOGLE_CONFIG_MISSING', 'Google OAuth is not configured for this app.', 500)

    try:
        token_response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': code,
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code',
            },
            timeout=20,
        )
        token_payload = token_response.json()
        access_token = token_payload.get('access_token')
        if token_response.status_code >= 400 or not access_token:
            message = token_payload.get('error_description') or token_payload.get('error') or 'Google login could not be completed.'
            return build_error('GOOGLE_AUTH_FAILED', f'Google login failed: {message}', 401)

        userinfo_response = requests.get(
            'https://openidconnect.googleapis.com/v1/userinfo',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=20,
        )
        userinfo = userinfo_response.json()
        email = (userinfo.get('email') or '').strip().lower()
        if not email:
            return build_error('GOOGLE_AUTH_FAILED', 'Google account email could not be retrieved.', 401)

        user = create_or_update_oauth_user(
            name=userinfo.get('name') or userinfo.get('given_name') or email.split('@')[0],
            email=email,
            profile_image=userinfo.get('picture'),
        )

        _, refresh_token = generate_tokens(user)
        frontend_url = current_app.config.get('FRONTEND_BASE_URL', 'http://localhost:5173').rstrip('/')
        response = redirect(f'{frontend_url}/login?google=success')
        response.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True,
            samesite='Lax',
            secure=not current_app.config.get('TESTING', False),
            max_age=7 * 24 * 60 * 60,
        )
        return response
    except requests.RequestException as exc:
        current_app.logger.exception('Google OAuth exchange failed')
        return build_error('GOOGLE_AUTH_FAILED', f'Google login could not be completed: {exc}', 500)


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

        response = jsonify({
            'success': True,
            'message': 'Registration successful. Please check your email to verify your account.',
            'user': user.to_public_dict(),
        })
        response.status_code = 201
        return response
    except Exception:
        current_app.logger.exception('Registration failed for email=%s', email)
        return build_error('REGISTRATION_FAILED', 'Unable to create account. Please try again.', 500)


@auth_bp.get('/verify-email')
def verify_email():
    token = request.args.get('token')
    if not token:
        return build_error('INVALID_TOKEN', 'Verification token is required.', 400)

    for user in User.query.filter(User.verification_token_hash.isnot(None)).all():
        expires_at = user.verification_token_expires_at
        if expires_at is not None and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at and expires_at < datetime.now(timezone.utc):
            continue

        if verify_email_token(user, token):
            clear_verification_token(user)
            return jsonify({'success': True, 'message': 'Email verified successfully.'}), 200

    return build_error('INVALID_TOKEN', 'This verification link is invalid or expired.', 400)


@auth_bp.post('/resend-verification')
@limiter.limit('5/minute')
def resend_verification():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    if not email:
        return build_error('VALIDATION_ERROR', 'Email is required.', 400)

    user = User.query.filter_by(email=email).first()
    if not user:
        return build_error('USER_NOT_FOUND', 'No account found for this email.', 404)
    if user.email_verified:
        return jsonify({'success': True, 'message': 'Your email is already verified.'}), 200

    token = generate_verification_token(user)
    db.session.commit()

    from app.services.email_service import send_verification_email
    verification_url = f"{current_app.config.get('FRONTEND_BASE_URL', 'http://localhost:5173').rstrip('/')}/verify-email?token={token}"
    send_verification_email(user.email, user.name, verification_url)
    return jsonify({'success': True, 'message': 'A new verification link has been sent to your email.'}), 200


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
            existing_user = User.query.filter_by(email=email).first()
            if current_app.config.get('EMAIL_VERIFICATION_REQUIRED', False) and existing_user and not existing_user.email_verified:
                return build_error('EMAIL_NOT_VERIFIED', 'Please verify your email before logging in.', 403)
            return build_error('INVALID_CREDENTIALS', 'Invalid email or password', 401)

        access_token, refresh_token = generate_tokens(user)
        response = jsonify({
            'success': True,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_public_dict(),
        })
        response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', secure=not current_app.config.get('TESTING', False), max_age=7 * 24 * 60 * 60)
        return response, 200
    except Exception:
        current_app.logger.exception('Login failed for email=%s', email)
        return build_error('LOGIN_FAILED', 'Unable to login. Please try again.', 500)


@auth_bp.post('/logout')
@jwt_required()
def logout():
    token = get_jwt()
    jti = token.get('jti')
    if jti:
        revoke_token(jti)
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
        jti = payload.get('jti')
        blocklist = current_app.config.get('JWT_BLOCKLIST', set())
        if jti in blocklist:
            return build_error('TOKEN_REVOKED', 'Refresh token has been revoked.', 401)
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

import hashlib
import re
import uuid
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity

from app.extensions import db
from app.models.user import User

ph = PasswordHasher()


def revoke_token(jti: str):
    blocklist = current_app.config.setdefault('JWT_BLOCKLIST', set())
    blocklist.add(jti)
    return True


def validate_password(password: str):
    if len(password) < 8:
        return 'Password must be at least 8 characters long.'
    if not re.search(r'[A-Z]', password):
        return 'Password must include at least one uppercase letter.'
    if not re.search(r'[a-z]', password):
        return 'Password must include at least one lowercase letter.'
    if not re.search(r'\d', password):
        return 'Password must include at least one number.'
    if not re.search(r'[^A-Za-z0-9]', password):
        return 'Password must include at least one special character.'
    return None


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return ph.verify(password_hash, password)
    except Exception:
        return False


def hash_verification_token(token: str) -> str:
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


def generate_verification_token(user: User) -> str:
    token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    user.verification_token_hash = hash_verification_token(token)
    user.verification_token_expires_at = expires_at
    db.session.add(user)
    return token


def create_user(name: str, email: str, password: str):
    user = User(name=name.strip(), email=email.strip().lower(), password_hash=hash_password(password), email_verified=False)
    db.session.add(user)
    db.session.commit()
    token = generate_verification_token(user)
    db.session.commit()
    from app.services.email_service import send_verification_email
    verification_url = f"{current_app.config.get('FRONTEND_BASE_URL', 'http://localhost:5173').rstrip('/')}/verify-email?token={token}"
    send_verification_email(user.email, user.name, verification_url)
    return user


def create_or_update_oauth_user(name: str, email: str, profile_image: str | None = None):
    normalized_email = email.strip().lower()
    try:
        user = User.query.filter_by(email=normalized_email).first()

        if user is None:
            user = User(
                name=(name or 'Google User').strip()[:120],
                email=normalized_email,
                password_hash=hash_password(str(uuid.uuid4())),
                profile_image=profile_image,
                email_verified=True,
                email_verified_at=datetime.now(timezone.utc),
            )
            db.session.add(user)
        else:
            user.name = (name or user.name or 'Google User').strip()[:120]
            if profile_image:
                user.profile_image = profile_image
            user.email_verified = True
            user.email_verified_at = user.email_verified_at or datetime.now(timezone.utc)
            user.verification_token_hash = None
            user.verification_token_expires_at = None

        user.last_login = datetime.now(timezone.utc)
        db.session.commit()
        return user
    except Exception:
        db.session.rollback()
        raise


def authenticate_user(email: str, password: str):
    user = User.query.filter_by(email=email.strip().lower()).first()
    if not user or not verify_password(password, user.password_hash):
        return None

    if current_app.config.get('EMAIL_VERIFICATION_REQUIRED', False) and not user.email_verified:
        return None

    user.last_login = datetime.now(timezone.utc)
    db.session.commit()
    return user


def generate_tokens(user):
    access_token = create_access_token(identity=str(user.id), expires_delta=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'])
    refresh_token = create_refresh_token(identity=str(user.id), expires_delta=current_app.config['JWT_REFRESH_TOKEN_EXPIRES'])
    return access_token, refresh_token


def get_current_user_from_token():
    identity = get_jwt_identity()
    if not identity:
        return None
    return User.query.get(int(identity))


def verify_email_token(user: User, candidate_token: str | None) -> bool:
    if not candidate_token:
        return False
    stored_value = user.verification_token_hash
    if not stored_value:
        return False
    if candidate_token == stored_value:
        return True
    return hash_verification_token(candidate_token) == stored_value


def clear_verification_token(user: User):
    user.email_verified = True
    user.email_verified_at = datetime.now(timezone.utc)
    user.verification_token_hash = None
    user.verification_token_expires_at = None
    db.session.add(user)
    db.session.commit()
    return user

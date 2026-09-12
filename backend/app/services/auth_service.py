import re
from datetime import datetime, timezone

from argon2 import PasswordHasher
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity

from app.extensions import db
from app.models.user import User

ph = PasswordHasher()


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


def create_user(name: str, email: str, password: str):
    user = User(name=name.strip(), email=email.strip().lower(), password_hash=hash_password(password))
    db.session.add(user)
    db.session.commit()
    return user


def authenticate_user(email: str, password: str):
    user = User.query.filter_by(email=email.strip().lower()).first()
    if not user or not verify_password(password, user.password_hash):
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

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.models.user import User
from app.services.auth_service import hash_password, validate_password
from app.extensions import db

users_bp = Blueprint('users', __name__, url_prefix='/api/users')


def build_error(code, message, status_code):
    return jsonify({
        'success': False,
        'error': {
            'code': code,
            'message': message,
        }
    }), status_code


@users_bp.get('/me')
@jwt_required()
def get_me():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return build_error('USER_NOT_FOUND', 'User not found.', 404)
    return jsonify({
        'success': True,
        'user': user.to_public_dict(),
    }), 200


@users_bp.put('/me')
@jwt_required()
def update_me():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return build_error('USER_NOT_FOUND', 'User not found.', 404)

    data = request.get_json(silent=True) or {}
    name = (data.get('name') or user.name).strip()
    bio = data.get('bio')
    profile_image = data.get('profile_image')

    if not name or len(name) < 2:
        return build_error('VALIDATION_ERROR', 'Name must be at least 2 characters long.', 400)

    user.name = name
    user.bio = bio if bio is not None else user.bio
    user.profile_image = profile_image if profile_image is not None else user.profile_image
    db.session.commit()

    return jsonify({
        'success': True,
        'user': user.to_public_dict(),
    }), 200

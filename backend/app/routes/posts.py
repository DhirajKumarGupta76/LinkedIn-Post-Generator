from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import limiter
from app.models.user import User
from app.services.post_service import PostService

posts_bp = Blueprint('posts', __name__, url_prefix='/api')


def build_error(code, message, status_code):
    return jsonify({
        'success': False,
        'error': {
            'code': code,
            'message': message,
        }
    }), status_code


def get_current_user():
    user_id = get_jwt_identity()
    if not user_id:
        return None
    return User.query.get(int(user_id))


@posts_bp.post('/posts/generate')
@jwt_required()
@limiter.limit('5/minute')
def generate_post():
    user = get_current_user()
    if not user:
        return build_error('AUTH_REQUIRED', 'Authentication required.', 401)

    payload = request.get_json(silent=True) or {}
    try:
        result = PostService.generate_for_user(user.id, payload)
        post = PostService.create_generated_post(user.id, payload)
        return jsonify({
            'success': True,
            'data': {
                'id': post.id,
                'content': post.edited_content or post.generated_content,
                'hashtags': post.get_hashtags(),
                'word_count': len(post.edited_content.split()) if post.edited_content else len(post.generated_content.split()),
                'variations': result.get('variations', []),
            }
        }), 200
    except ValueError as exc:
        return build_error('VALIDATION_ERROR', str(exc), 400)
    except RuntimeError as exc:
        message = str(exc)
        status_code = 429 if 'rate' in message.lower() else 503
        return build_error('AI_SERVICE_ERROR', message, status_code)
    except Exception:
        return build_error('SERVER_ERROR', 'Unable to generate post right now.', 500)


@posts_bp.get('/posts')
@jwt_required()
def list_posts():
    user = get_current_user()
    if not user:
        return build_error('AUTH_REQUIRED', 'Authentication required.', 401)

    page = max(int(request.args.get('page', 1)), 1)
    per_page = min(max(int(request.args.get('per_page', 10)), 1), 20)
    sort = request.args.get('sort', 'desc')
    filters = {
        'topic': request.args.get('topic', '').strip() or None,
        'mood': request.args.get('mood', '').strip() or None,
        'tone': request.args.get('tone', '').strip() or None,
        'achievement': request.args.get('achievement', '').strip() or None,
        'date': request.args.get('date', '').strip() or None,
    }

    items, total, pages = PostService.list_for_user(user.id, page=page, per_page=per_page, sort=sort, filters=filters)
    return jsonify({
        'success': True,
        'data': [post.to_dict() for post in items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': pages,
        },
    }), 200


@posts_bp.get('/posts/<int:post_id>')
@jwt_required()
def get_post(post_id):
    user = get_current_user()
    if not user:
        return build_error('AUTH_REQUIRED', 'Authentication required.', 401)
    try:
        post = PostService.get_for_user(user.id, post_id)
        return jsonify({'success': True, 'data': post.to_dict()}), 200
    except ValueError as exc:
        return build_error('POST_NOT_FOUND', str(exc), 404)


@posts_bp.put('/posts/<int:post_id>')
@jwt_required()
def update_post(post_id):
    user = get_current_user()
    if not user:
        return build_error('AUTH_REQUIRED', 'Authentication required.', 401)

    payload = request.get_json(silent=True) or {}
    try:
        post = PostService.update_for_user(user.id, post_id, payload)
        return jsonify({'success': True, 'data': post.to_dict()}), 200
    except ValueError as exc:
        return build_error('VALIDATION_ERROR', str(exc), 400)


@posts_bp.delete('/posts/<int:post_id>')
@jwt_required()
def delete_post(post_id):
    user = get_current_user()
    if not user:
        return build_error('AUTH_REQUIRED', 'Authentication required.', 401)
    try:
        PostService.delete_for_user(user.id, post_id)
        return jsonify({'success': True, 'message': 'Post deleted.'}), 200
    except ValueError as exc:
        return build_error('POST_NOT_FOUND', str(exc), 404)


@posts_bp.post('/posts/<int:post_id>/save')
@jwt_required()
def save_post(post_id):
    user = get_current_user()
    if not user:
        return build_error('AUTH_REQUIRED', 'Authentication required.', 401)
    try:
        saved = PostService.save_post_for_user(user.id, post_id)
        return jsonify({'success': True, 'data': saved.to_dict()}), 200
    except ValueError as exc:
        return build_error('POST_NOT_FOUND', str(exc), 404)


@posts_bp.delete('/posts/<int:post_id>/save')
@jwt_required()
def unsave_post(post_id):
    user = get_current_user()
    if not user:
        return build_error('AUTH_REQUIRED', 'Authentication required.', 401)
    try:
        PostService.unsave_post_for_user(user.id, post_id)
        return jsonify({'success': True, 'message': 'Post removed from saved items.'}), 200
    except ValueError as exc:
        return build_error('SAVED_POST_NOT_FOUND', str(exc), 404)


@posts_bp.get('/saved-posts')
@jwt_required()
def list_saved_posts():
    user = get_current_user()
    if not user:
        return build_error('AUTH_REQUIRED', 'Authentication required.', 401)
    items = PostService.list_saved_for_user(user.id)
    return jsonify({'success': True, 'data': [saved.to_dict() for saved in items]}), 200


@posts_bp.delete('/saved-posts/<int:saved_post_id>')
@jwt_required()
def delete_saved_post(saved_post_id):
    user = get_current_user()
    if not user:
        return build_error('AUTH_REQUIRED', 'Authentication required.', 401)
    try:
        PostService.delete_saved_for_user(user.id, saved_post_id)
        return jsonify({'success': True, 'message': 'Saved post deleted.'}), 200
    except ValueError as exc:
        return build_error('SAVED_POST_NOT_FOUND', str(exc), 404)


@posts_bp.post('/posts/improve')
@jwt_required()
def improve_post():
    return _ai_action('improve')


@posts_bp.post('/posts/shorten')
@jwt_required()
def shorten_post():
    return _ai_action('shorten')


@posts_bp.post('/posts/expand')
@jwt_required()
def expand_post():
    return _ai_action('expand')


@posts_bp.post('/ai/hooks')
@jwt_required()
def generate_hook():
    return _ai_action('hook')


@posts_bp.post('/ai/hashtags')
@jwt_required()
def generate_hashtags():
    return _ai_action('hashtags')


@posts_bp.post('/ai/cta')
@jwt_required()
def generate_cta():
    return _ai_action('cta')


def _ai_action(action):
    user = get_current_user()
    if not user:
        return build_error('AUTH_REQUIRED', 'Authentication required.', 401)

    payload = request.get_json(silent=True) or {}
    post_id = payload.get('post_id')
    if not post_id:
        return build_error('VALIDATION_ERROR', 'post_id is required.', 400)

    try:
        result = PostService.generate_ai_edit(user.id, post_id, action, payload)
        return jsonify({'success': True, 'data': result}), 200
    except ValueError as exc:
        return build_error('VALIDATION_ERROR', str(exc), 400)
    except Exception:
        return build_error('SERVER_ERROR', 'Unable to process AI edit right now.', 500)

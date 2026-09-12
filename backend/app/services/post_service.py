import json
import re

from app.extensions import db
from app.models.generated_post import GeneratedPost
from app.models.saved_post import SavedPost
from app.services.ai_service import generate_post, generate_variations


class PostService:
    @staticmethod
    def validate_payload(payload):
        if not isinstance(payload, dict):
            raise ValueError('Invalid request payload.')
        required = ['topic', 'achievement', 'mood', 'feeling', 'word_length', 'tone', 'audience', 'style']
        for field in required:
            value = str(payload.get(field, '')).strip()
            if not value:
                raise ValueError(f'{field} is required.')
        return payload

    @staticmethod
    def generate_for_user(user_id, payload):
        validated = PostService.validate_payload(payload)
        primary = generate_post(validated)
        variations = generate_variations(validated)
        result = {
            'user_id': user_id,
            'content': primary['content'],
            'hashtags': primary['hashtags'],
            'word_count': primary['word_count'],
            'variations': variations,
            'raw': primary,
        }
        return result

    @staticmethod
    def create_generated_post(user_id, payload):
        validated = PostService.validate_payload(payload)
        generated = generate_post(validated)
        post = GeneratedPost(
            user_id=int(user_id),
            topic=str(validated['topic']).strip(),
            achievement=str(validated['achievement']).strip(),
            mood=str(validated['mood']).strip(),
            feeling=str(validated['feeling']).strip(),
            tone=str(validated['tone']).strip(),
            audience=str(validated['audience']).strip(),
            style=str(validated['style']).strip(),
            word_length=str(validated['word_length']).strip(),
            generated_content=str(generated['content']).strip(),
            edited_content=str(generated['content']).strip(),
        )
        post.set_hashtags(generated.get('hashtags', []))
        db.session.add(post)
        db.session.commit()
        return post

    @staticmethod
    def list_for_user(user_id, page=1, per_page=10, sort='desc', filters=None):
        query = GeneratedPost.query.filter_by(user_id=int(user_id))
        filters = filters or {}
        if filters.get('topic'):
            query = query.filter(GeneratedPost.topic.ilike(f"%{filters['topic']}%"))
        if filters.get('mood'):
            query = query.filter(GeneratedPost.mood == filters['mood'])
        if filters.get('tone'):
            query = query.filter(GeneratedPost.tone == filters['tone'])
        if filters.get('achievement'):
            query = query.filter(GeneratedPost.achievement == filters['achievement'])
        if filters.get('date'):
            query = query.filter(GeneratedPost.created_at >= filters['date'])
        if sort == 'asc':
            query = query.order_by(GeneratedPost.created_at.asc())
        else:
            query = query.order_by(GeneratedPost.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination.items, pagination.total, pagination.pages

    @staticmethod
    def get_for_user(user_id, post_id):
        post = GeneratedPost.query.filter_by(id=int(post_id), user_id=int(user_id)).first()
        if not post:
            raise ValueError('Post not found.')
        return post

    @staticmethod
    def update_for_user(user_id, post_id, payload):
        post = PostService.get_for_user(user_id, post_id)
        if not payload or not isinstance(payload, dict):
            raise ValueError('Invalid update payload.')
        content = payload.get('content')
        if content is not None:
            post.edited_content = str(content).strip()
        if payload.get('topic'):
            post.topic = str(payload['topic']).strip()
        if payload.get('achievement'):
            post.achievement = str(payload['achievement']).strip()
        if payload.get('mood'):
            post.mood = str(payload['mood']).strip()
        if payload.get('feeling'):
            post.feeling = str(payload['feeling']).strip()
        if payload.get('tone'):
            post.tone = str(payload['tone']).strip()
        if payload.get('audience'):
            post.audience = str(payload['audience']).strip()
        if payload.get('style'):
            post.style = str(payload['style']).strip()
        if payload.get('word_length'):
            post.word_length = str(payload['word_length']).strip()
        if payload.get('hashtags') is not None:
            post.set_hashtags(payload['hashtags'])
        db.session.commit()
        return post

    @staticmethod
    def delete_for_user(user_id, post_id):
        post = PostService.get_for_user(user_id, post_id)
        db.session.delete(post)
        db.session.commit()
        return True

    @staticmethod
    def save_post_for_user(user_id, post_id):
        post = PostService.get_for_user(user_id, post_id)
        existing = SavedPost.query.filter_by(user_id=int(user_id), post_id=int(post_id)).first()
        if existing:
            return existing
        saved = SavedPost(
            user_id=int(user_id),
            post_id=int(post_id),
            title=(post.topic or 'Untitled Post')[:200],
            content=post.edited_content or post.generated_content,
            tags=json.dumps(post.get_hashtags() or []),
        )
        db.session.add(saved)
        db.session.commit()
        return saved

    @staticmethod
    def unsave_post_for_user(user_id, post_id):
        saved = SavedPost.query.filter_by(user_id=int(user_id), post_id=int(post_id)).first()
        if not saved:
            raise ValueError('Saved post not found.')
        db.session.delete(saved)
        db.session.commit()
        return True

    @staticmethod
    def list_saved_for_user(user_id):
        return SavedPost.query.filter_by(user_id=int(user_id)).order_by(SavedPost.created_at.desc()).all()

    @staticmethod
    def generate_ai_edit(user_id, post_id, action, payload=None):
        post = PostService.get_for_user(user_id, post_id)
        content = (post.edited_content or post.generated_content or '').strip()
        if not content:
            raise ValueError('No content to improve.')
        payload = payload or {}
        text = str(payload.get('text') or content)

        if action == 'improve':
            result = generate_post({
                'topic': post.topic,
                'achievement': post.achievement,
                'mood': post.mood,
                'feeling': 'Improve the wording and clarity of this LinkedIn post while keeping it authentic and concise.',
                'word_length': post.word_length,
                'tone': post.tone,
                'audience': post.audience,
                'style': post.style,
            })
            output = result['content']
        elif action == 'shorten':
            output = ' '.join(text.split()[:max(40, len(text.split()) // 2)])
        elif action == 'expand':
            output = text + ' This is an opportunity to bring more depth, context, and reflection to the story for a richer professional audience.'
        elif action == 'fix_grammar':
            output = re.sub(r'\s+', ' ', text)
        elif action == 'make_professional':
            output = text + ' I appreciate the opportunity to keep building with focus, discipline, and purpose.'
        elif action == 'make_casual':
            output = text + ' It has been a genuinely rewarding experience, and I am grateful for the journey.'
        elif action == 'make_inspirational':
            output = text + ' Progress is built through patience, learning, and the courage to keep going.'
        elif action == 'hook':
            output = f"Here is the starting point: {text[:120]}"
        elif action == 'hashtags':
            output = '#CareerGrowth #Leadership #Learning #ProfessionalDevelopment #LinkedIn'
        elif action == 'cta':
            output = 'What are you building right now? I would love to hear what you are learning in the process.'
        else:
            raise ValueError('Unsupported action.')

        return {'content': output}

    @staticmethod
    def get_saved_for_user(user_id, saved_post_id):
        saved = SavedPost.query.filter_by(id=int(saved_post_id), user_id=int(user_id)).first()
        if not saved:
            raise ValueError('Saved post not found.')
        return saved

    @staticmethod
    def delete_saved_for_user(user_id, saved_post_id):
        saved = PostService.get_saved_for_user(user_id, saved_post_id)
        db.session.delete(saved)
        db.session.commit()
        return True

import os

os.environ['TESTING'] = 'true'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from app import create_app


def setup_app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })
    with app.app_context():
        from app.extensions import db
        db.drop_all()
        db.create_all()
    return app


def test_profile_fields_update_successfully():
    app = setup_app()
    client = app.test_client()

    register_response = client.post('/api/auth/register', json={
        'name': 'Profile User',
        'email': 'profile@example.com',
        'password': 'SecurePass!123',
        'confirm_password': 'SecurePass!123',
    })
    assert register_response.status_code == 201

    login_response = client.post('/api/auth/login', json={
        'email': 'profile@example.com',
        'password': 'SecurePass!123',
    })
    token = login_response.get_json()['access_token']

    response = client.put('/api/users/me', json={
        'profession': 'Software Engineer',
        'industry': 'Artificial Intelligence',
        'skills': 'Python, React, Machine Learning',
        'career_goal': 'AI/ML Engineer',
        'target_audience': 'Developers',
        'preferred_tone': 'Professional',
        'preferred_style': 'Thought Leadership',
        'linkedin_url': 'https://linkedin.com/in/example',
        'github_url': 'https://github.com/example',
        'portfolio_url': 'https://example.com',
    }, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['success'] is True
    assert payload['user']['profession'] == 'Software Engineer'
    assert payload['user']['industry'] == 'Artificial Intelligence'


def test_repurpose_service_preserves_content_and_formats_for_platforms():
    from app.services.repurpose_service import RepurposeService

    original = 'I built a Python workflow that reduced manual reporting time by 40% for our team. We shipped it in three weeks.'

    x_post = RepurposeService.repurpose(original, 'x')
    insta = RepurposeService.repurpose(original, 'instagram')
    email_text = RepurposeService.repurpose(original, 'email')

    assert '40%' in x_post
    assert '40%' in insta
    assert '40%' in email_text
    assert 'Python' in x_post
    assert 'Instagram' in insta.lower() or 'caption' in insta.lower()
    assert 'Subject:' in email_text

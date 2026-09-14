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


def test_generate_post_success():
    app = setup_app()
    client = app.test_client()

    register_response = client.post('/api/auth/register', json={
        'name': 'Jane Doe',
        'email': 'jane@example.com',
        'password': 'SecurePass!123',
        'confirm_password': 'SecurePass!123',
    })
    assert register_response.status_code == 201

    login_response = client.post('/api/auth/login', json={
        'email': 'jane@example.com',
        'password': 'SecurePass!123',
    })
    token = login_response.get_json()['access_token']

    response = client.post('/api/posts/generate', json={
        'topic': 'Career growth',
        'achievement': 'Promotion',
        'mood': 'Excited',
        'feeling': 'I am proud of how much I learned and how the team trusted my growth.',
        'word_length': 'Medium',
        'tone': 'Professional',
        'audience': 'Developers',
        'style': 'Achievement Announcement',
    }, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['success'] is True
    assert 'content' in payload['data']
    assert isinstance(payload['data']['hashtags'], list)
    assert payload['data']['word_count'] > 0


def test_generate_post_rejects_empty_fields():
    app = setup_app()
    client = app.test_client()

    register_response = client.post('/api/auth/register', json={
        'name': 'Jane Doe',
        'email': 'jane2@example.com',
        'password': 'SecurePass!123',
        'confirm_password': 'SecurePass!123',
    })
    assert register_response.status_code == 201

    login_response = client.post('/api/auth/login', json={
        'email': 'jane2@example.com',
        'password': 'SecurePass!123',
    })
    token = login_response.get_json()['access_token']

    response = client.post('/api/posts/generate', json={
        'topic': '',
        'achievement': 'Promotion',
        'mood': 'Excited',
        'feeling': 'Proud',
        'word_length': 'Medium',
        'tone': 'Professional',
        'audience': 'Developers',
        'style': 'Achievement Announcement',
    }, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 400
    payload = response.get_json()
    assert payload['error']['code'] == 'VALIDATION_ERROR'


def test_generate_post_can_be_listed_and_saved():
    app = setup_app()
    client = app.test_client()

    register_response = client.post('/api/auth/register', json={
        'name': 'Saved User',
        'email': 'saved@example.com',
        'password': 'SecurePass!123',
        'confirm_password': 'SecurePass!123',
    })
    assert register_response.status_code == 201

    login_response = client.post('/api/auth/login', json={
        'email': 'saved@example.com',
        'password': 'SecurePass!123',
    })
    token = login_response.get_json()['access_token']

    generate_response = client.post('/api/posts/generate', json={
        'topic': 'Career growth',
        'achievement': 'Promotion',
        'mood': 'Excited',
        'feeling': 'I am proud of how much I learned and how the team trusted my growth.',
        'word_length': 'Medium',
        'tone': 'Professional',
        'audience': 'Developers',
        'style': 'Achievement Announcement',
    }, headers={'Authorization': f'Bearer {token}'})
    assert generate_response.status_code == 200
    post_id = generate_response.get_json()['data']['id']

    list_response = client.get('/api/posts', headers={'Authorization': f'Bearer {token}'})
    assert list_response.status_code == 200
    assert any(item['id'] == post_id for item in list_response.get_json()['data'])

    save_response = client.post(f'/api/posts/{post_id}/save', headers={'Authorization': f'Bearer {token}'})
    assert save_response.status_code == 200

    saved_response = client.get('/api/saved-posts', headers={'Authorization': f'Bearer {token}'})
    assert saved_response.status_code == 200
    assert len(saved_response.get_json()['data']) >= 1

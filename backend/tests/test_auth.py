import os

os.environ['TESTING'] = 'true'

from sqlalchemy import text

from app import create_app
from app.extensions import db


def setup_app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        from app.extensions import db
        db.drop_all()
        db.create_all()
    return app


def test_register_user_success():
    app = setup_app()
    client = app.test_client()

    response = client.post('/api/auth/register', json={
        'name': 'Jane Doe',
        'email': 'jane@example.com',
        'password': 'SecurePass!123',
        'confirm_password': 'SecurePass!123'
    })

    assert response.status_code == 201
    payload = response.get_json()
    assert payload['success'] is True
    assert payload['user']['email'] == 'jane@example.com'


def test_register_duplicate_email_fails():
    app = setup_app()
    client = app.test_client()

    client.post('/api/auth/register', json={
        'name': 'Jane Doe',
        'email': 'jane@example.com',
        'password': 'SecurePass!123',
        'confirm_password': 'SecurePass!123'
    })

    response = client.post('/api/auth/register', json={
        'name': 'Jane Smith',
        'email': 'jane@example.com',
        'password': 'AnotherPass!456',
        'confirm_password': 'AnotherPass!456'
    })

    assert response.status_code == 409
    payload = response.get_json()
    assert payload['error']['code'] == 'EMAIL_ALREADY_EXISTS'


def test_register_invalid_password_fails():
    app = setup_app()
    client = app.test_client()

    response = client.post('/api/auth/register', json={
        'name': 'Jane Doe',
        'email': 'jane@example.com',
        'password': 'weakpass',
        'confirm_password': 'weakpass'
    })

    assert response.status_code == 400
    payload = response.get_json()
    assert payload['error']['code'] == 'VALIDATION_ERROR'


def test_register_legacy_sqlite_schema_is_migrated(tmp_path):
    db_path = tmp_path / 'legacy_postgen.db'
    legacy_db_url = f'sqlite:///{db_path}'

    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = legacy_db_url

    with app.app_context():
        db.session.execute(text('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name VARCHAR(120) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                profile_image VARCHAR(500),
                bio TEXT,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                last_login DATETIME
            )
        '''))
        db.session.commit()

    client = app.test_client()
    response = client.post('/api/auth/register', json={
        'name': 'Legacy User',
        'email': 'legacy@example.com',
        'password': 'LegacyPass!123',
        'confirm_password': 'LegacyPass!123'
    })

    assert response.status_code == 201, response.get_data(as_text=True)
    payload = response.get_json()
    assert payload['success'] is True
    assert payload['user']['email'] == 'legacy@example.com'


def test_login_success():
    app = setup_app()
    client = app.test_client()

    client.post('/api/auth/register', json={
        'name': 'Jane Doe',
        'email': 'jane@example.com',
        'password': 'SecurePass!123',
        'confirm_password': 'SecurePass!123'
    })

    response = client.post('/api/auth/login', json={
        'email': 'jane@example.com',
        'password': 'SecurePass!123'
    })

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['success'] is True
    assert 'access_token' in payload
    assert 'refresh_token' in payload


def test_login_invalid_credentials_fails():
    app = setup_app()
    client = app.test_client()

    response = client.post('/api/auth/login', json={
        'email': 'missing@example.com',
        'password': 'WrongPass!123'
    })

    assert response.status_code == 401
    payload = response.get_json()
    assert payload['error']['code'] == 'INVALID_CREDENTIALS'


def test_protected_endpoint_requires_auth():
    app = setup_app()
    client = app.test_client()

    response = client.get('/api/users/me')
    assert response.status_code == 401


def test_refresh_token_success():
    app = setup_app()
    client = app.test_client()

    client.post('/api/auth/register', json={
        'name': 'Jane Doe',
        'email': 'jane@example.com',
        'password': 'SecurePass!123',
        'confirm_password': 'SecurePass!123'
    })

    login_response = client.post('/api/auth/login', json={
        'email': 'jane@example.com',
        'password': 'SecurePass!123'
    })
    refresh_token = login_response.get_json()['refresh_token']

    response = client.post('/api/auth/refresh', json={'refresh_token': refresh_token})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['success'] is True
    assert 'access_token' in payload

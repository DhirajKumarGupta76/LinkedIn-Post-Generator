import os

import pytest

os.environ['TESTING'] = 'true'

from sqlalchemy import text

from app import create_app
from app.config import get_config
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
    app.config['EMAIL_VERIFICATION_REQUIRED'] = False
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
    app.config['EMAIL_VERIFICATION_REQUIRED'] = False
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


def test_google_login_url_is_generated():
    app = setup_app()
    app.config['GOOGLE_CLIENT_ID'] = 'google-client-id'
    app.config['GOOGLE_CLIENT_SECRET'] = 'google-client-secret'
    app.config['GOOGLE_REDIRECT_URI'] = 'http://localhost:5000/api/auth/google/callback'
    client = app.test_client()

    response = client.get('/api/auth/google/login-url')

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['success'] is True
    assert 'accounts.google.com' in payload['auth_url']
    assert 'client_id=google-client-id' in payload['auth_url']


def test_google_callback_creates_user_and_sets_refresh_cookie(monkeypatch):
    app = setup_app()
    app.config['GOOGLE_CLIENT_ID'] = 'google-client-id'
    app.config['GOOGLE_CLIENT_SECRET'] = 'google-client-secret'
    app.config['GOOGLE_REDIRECT_URI'] = 'http://localhost:5000/api/auth/google/callback'
    app.config['FRONTEND_BASE_URL'] = 'http://localhost:5173'

    class FakeResponse:
        def __init__(self, payload, status_code=200):
            self._payload = payload
            self.status_code = status_code

        def json(self):
            return self._payload

    def fake_post(url, data=None, headers=None, timeout=None):
        assert url == 'https://oauth2.googleapis.com/token'
        return FakeResponse({
            'access_token': 'google-access-token',
            'id_token': 'google-id-token',
            'token_type': 'Bearer',
        })

    def fake_get(url, headers=None, timeout=None):
        assert url == 'https://openidconnect.googleapis.com/v1/userinfo'
        assert headers['Authorization'] == 'Bearer google-access-token'
        return FakeResponse({
            'email': 'gmail.user@gmail.com',
            'name': 'Gmail User',
            'picture': 'https://example.com/avatar.jpg',
        })

    monkeypatch.setattr('requests.post', fake_post)
    monkeypatch.setattr('requests.get', fake_get)

    client = app.test_client()
    response = client.get('/api/auth/google/callback?code=test-google-code', follow_redirects=False)

    assert response.status_code == 302
    assert 'Location' in response.headers
    assert 'http://localhost:5173/login?google=success' in response.headers['Location']
    assert 'refresh_token=' in response.headers.get('Set-Cookie', '')

    with app.app_context():
        user = db.session.query(__import__('app.models.user', fromlist=['User']).User).filter_by(email='gmail.user@gmail.com').first()
        assert user is not None
        assert user.name == 'Gmail User'


def test_config_requires_strong_jwt_secrets(monkeypatch):
    monkeypatch.setenv('TESTING', 'false')
    monkeypatch.setenv('SECRET_KEY', 'short-secret')
    monkeypatch.setenv('JWT_SECRET_KEY', 'short-secret')
    monkeypatch.setenv('JWT_REFRESH_SECRET_KEY', 'short-secret')

    with pytest.raises(RuntimeError, match='JWT_SECRET_KEY|JWT_REFRESH_SECRET_KEY|SECRET_KEY'):
        get_config()


def test_register_user_generates_verification_token(monkeypatch):
    app = setup_app()
    app.config['EMAIL_VERIFICATION_REQUIRED'] = True
    captured = {}

    def fake_send(email, user_name, verification_url):
        captured['email'] = email
        captured['user_name'] = user_name
        captured['verification_url'] = verification_url
        return True

    monkeypatch.setattr('app.services.email_service.send_verification_email', fake_send)
    client = app.test_client()

    response = client.post('/api/auth/register', json={
        'name': 'Jane Doe',
        'email': 'verify@example.com',
        'password': 'SecurePass!123',
        'confirm_password': 'SecurePass!123'
    })

    assert response.status_code == 201
    payload = response.get_json()
    assert payload['success'] is True
    assert payload['user']['email'] == 'verify@example.com'
    assert payload['message'] == 'Registration successful. Please check your email to verify your account.'
    assert captured['email'] == 'verify@example.com'

    with app.app_context():
        user = db.session.query(__import__('app.models.user', fromlist=['User']).User).filter_by(email='verify@example.com').first()
        assert user is not None
        assert user.email_verified is False
        assert user.verification_token_hash is not None
        assert user.verification_token_expires_at is not None


def test_verify_email_success_and_login_restricts_unverified_accounts(monkeypatch):
    app = setup_app()
    app.config['EMAIL_VERIFICATION_REQUIRED'] = True
    monkeypatch.setattr('app.services.email_service.send_verification_email', lambda *args, **kwargs: True)
    client = app.test_client()

    client.post('/api/auth/register', json={
        'name': 'Jane Doe',
        'email': 'verify2@example.com',
        'password': 'SecurePass!123',
        'confirm_password': 'SecurePass!123'
    })

    with app.app_context():
        user = db.session.query(__import__('app.models.user', fromlist=['User']).User).filter_by(email='verify2@example.com').first()
        token = user.verification_token_hash
        assert token is not None

    login_response = client.post('/api/auth/login', json={
        'email': 'verify2@example.com',
        'password': 'SecurePass!123'
    })
    assert login_response.status_code == 403
    assert login_response.get_json()['error']['code'] == 'EMAIL_NOT_VERIFIED'

    verify_response = client.get('/api/auth/verify-email?token=' + token)
    assert verify_response.status_code == 200
    assert verify_response.get_json()['success'] is True

    with app.app_context():
        user = db.session.query(__import__('app.models.user', fromlist=['User']).User).filter_by(email='verify2@example.com').first()
        assert user.email_verified is True
        assert user.verification_token_hash is None


def test_resend_verification_success_and_invalid_token_handling(monkeypatch):
    app = setup_app()
    app.config['EMAIL_VERIFICATION_REQUIRED'] = True
    monkeypatch.setattr('app.services.email_service.send_verification_email', lambda *args, **kwargs: True)
    client = app.test_client()

    client.post('/api/auth/register', json={
        'name': 'Jane Doe',
        'email': 'resend@example.com',
        'password': 'SecurePass!123',
        'confirm_password': 'SecurePass!123'
    })

    response = client.post('/api/auth/resend-verification', json={'email': 'resend@example.com'})
    assert response.status_code == 200
    assert response.get_json()['success'] is True

    invalid = client.get('/api/auth/verify-email?token=bad-token')
    assert invalid.status_code == 400
    assert invalid.get_json()['error']['code'] == 'INVALID_TOKEN'

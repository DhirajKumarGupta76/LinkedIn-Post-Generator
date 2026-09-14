import os

os.environ['TESTING'] = 'true'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from app import create_app


def test_health_endpoint():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })
    client = app.test_client()

    response = client.get('/api/health')

    assert response.status_code == 200
    assert response.get_json() == {
        'success': True,
        'message': 'PostGen AI API is running'
    }

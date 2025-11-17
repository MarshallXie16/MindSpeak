"""
Pytest configuration and fixtures
"""
import pytest
import os
from app import create_app
from app.models import db, User, JournalEntry, UserPreferences, UsageTracking


@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    # Set testing environment
    os.environ['FLASK_ENV'] = 'testing'

    app = create_app('testing')

    # Create application context
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Test client for making requests"""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Clean database session for each test"""
    with app.app_context():
        # Clean all tables
        db.session.query(JournalEntry).delete()
        db.session.query(UserPreferences).delete()
        db.session.query(UsageTracking).delete()
        db.session.query(User).delete()
        db.session.commit()

        yield db.session

        # Cleanup after test
        db.session.rollback()


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        email='test@example.com',
        username='testuser'
    )
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def auth_token(client, test_user):
    """Get JWT token for authenticated requests"""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    return response.json['token']


@pytest.fixture
def auth_headers(auth_token):
    """Get authorization headers with JWT token"""
    return {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }

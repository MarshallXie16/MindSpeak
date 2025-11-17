"""
Tests for authentication endpoints
"""
import pytest
from app.models import User


class TestRegistration:
    """Test user registration"""

    def test_register_success(self, client, db_session):
        """Test successful user registration"""
        response = client.post('/api/auth/register', json={
            'email': 'newuser@example.com',
            'password': 'password123',
            'username': 'newuser'
        })

        assert response.status_code == 201
        assert 'token' in response.json
        assert 'user' in response.json
        assert response.json['user']['email'] == 'newuser@example.com'
        assert response.json['user']['username'] == 'newuser'

        # Verify user created in database
        user = User.query.filter_by(email='newuser@example.com').first()
        assert user is not None
        assert user.username == 'newuser'

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with existing email"""
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',  # Already exists
            'password': 'password123',
            'username': 'different'
        })

        assert response.status_code == 409
        assert 'error' in response.json

    def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        response = client.post('/api/auth/register', json={
            'email': 'not-an-email',
            'password': 'password123'
        })

        assert response.status_code == 400

    def test_register_short_password(self, client):
        """Test registration with password too short"""
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'short'
        })

        assert response.status_code == 400


class TestLogin:
    """Test user login"""

    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })

        assert response.status_code == 200
        assert 'token' in response.json
        assert 'user' in response.json
        assert response.json['user']['email'] == 'test@example.com'

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password"""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })

        assert response.status_code == 401
        assert 'error' in response.json

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent email"""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'password123'
        })

        assert response.status_code == 401


class TestAuthenticatedEndpoints:
    """Test JWT-protected endpoints"""

    def test_get_current_user(self, client, test_user, auth_headers):
        """Test getting current user info"""
        response = client.get('/api/auth/me', headers=auth_headers)

        assert response.status_code == 200
        assert 'user' in response.json
        assert response.json['user']['email'] == 'test@example.com'

    def test_get_current_user_no_token(self, client):
        """Test accessing protected endpoint without token"""
        response = client.get('/api/auth/me')

        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token"""
        headers = {
            'Authorization': 'Bearer invalid-token-here'
        }
        response = client.get('/api/auth/me', headers=headers)

        assert response.status_code in [401, 422]  # 422 for malformed JWT

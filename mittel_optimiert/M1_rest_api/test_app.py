"""
Unit Tests for REST API

Comprehensive test suite including SQL injection tests.
"""

import os
import pytest
import sqlite3
from app import app, db


@pytest.fixture
def client():
    """Create test client with temporary database"""
    # Create a new Database instance with in-memory database for testing
    from database import Database
    import app as app_module

    test_db = Database(":memory:")
    app_module.db = test_db  # Replace the global db instance

    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

    # Cleanup happens automatically with in-memory DB


@pytest.fixture
def sample_user(client):
    """Create a sample user for testing"""
    response = client.post('/users', json={
        'name': 'Test User',
        'email': 'test@example.com'
    })
    return response.get_json()


class TestCreateUser:
    """Tests for POST /users"""

    def test_create_user_success(self, client):
        """Test successful user creation"""
        response = client.post('/users', json={
            'name': 'Alice',
            'email': 'alice@example.com'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'Alice'
        assert data['email'] == 'alice@example.com'
        assert 'id' in data

    def test_create_user_duplicate_email(self, client, sample_user):
        """Test creating user with duplicate email returns 409"""
        response = client.post('/users', json={
            'name': 'Another User',
            'email': 'test@example.com'  # Same as sample_user
        })
        assert response.status_code == 409
        assert 'already exists' in response.get_json()['error'].lower()

    def test_create_user_missing_name(self, client):
        """Test creating user without name returns 400"""
        response = client.post('/users', json={
            'email': 'test@example.com'
        })
        assert response.status_code == 400

    def test_create_user_missing_email(self, client):
        """Test creating user without email returns 400"""
        response = client.post('/users', json={
            'name': 'Test User'
        })
        assert response.status_code == 400

    def test_create_user_empty_name(self, client):
        """Test creating user with empty name returns 400"""
        response = client.post('/users', json={
            'name': '',
            'email': 'test@example.com'
        })
        assert response.status_code == 400

    def test_create_user_invalid_email(self, client):
        """Test creating user with invalid email returns 400"""
        response = client.post('/users', json={
            'name': 'Test User',
            'email': 'invalid-email'
        })
        assert response.status_code == 400

    def test_create_user_name_too_long(self, client):
        """Test creating user with name > 100 chars returns 400"""
        response = client.post('/users', json={
            'name': 'a' * 101,
            'email': 'test@example.com'
        })
        assert response.status_code == 400

    def test_create_user_whitespace_trimmed(self, client):
        """Test that whitespace in name/email is trimmed"""
        response = client.post('/users', json={
            'name': '  Spaces  ',
            'email': '  test@example.com  '
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'Spaces'
        assert data['email'] == 'test@example.com'


class TestGetUsers:
    """Tests for GET /users"""

    def test_get_all_users_empty(self, client):
        """Test getting all users when database is empty"""
        response = client.get('/users')
        assert response.status_code == 200
        assert response.get_json() == []

    def test_get_all_users(self, client):
        """Test getting all users"""
        # Create some users
        client.post('/users', json={'name': 'Alice', 'email': 'alice@example.com'})
        client.post('/users', json={'name': 'Bob', 'email': 'bob@example.com'})

        response = client.get('/users')
        assert response.status_code == 200
        users = response.get_json()
        assert len(users) == 2

    def test_get_user_by_id(self, client, sample_user):
        """Test getting specific user by ID"""
        user_id = sample_user['id']
        response = client.get(f'/users/{user_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == user_id
        assert data['email'] == 'test@example.com'

    def test_get_user_not_found(self, client):
        """Test getting non-existent user returns 404"""
        response = client.get('/users/9999')
        assert response.status_code == 404

    def test_get_user_invalid_id(self, client):
        """Test getting user with invalid ID returns 400"""
        response = client.get('/users/invalid')
        assert response.status_code == 400

    def test_get_user_negative_id(self, client):
        """Test getting user with negative ID returns 400"""
        response = client.get('/users/-1')
        assert response.status_code == 400


class TestUpdateUser:
    """Tests for PUT /users/<id>"""

    def test_update_user_success(self, client, sample_user):
        """Test successful user update"""
        user_id = sample_user['id']
        response = client.put(f'/users/{user_id}', json={
            'name': 'Updated Name',
            'email': 'updated@example.com'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'Updated Name'
        assert data['email'] == 'updated@example.com'

    def test_update_user_not_found(self, client):
        """Test updating non-existent user returns 404"""
        response = client.put('/users/9999', json={
            'name': 'Test',
            'email': 'test@example.com'
        })
        assert response.status_code == 404

    def test_update_user_duplicate_email(self, client):
        """Test updating user with existing email returns 409"""
        # Create two users
        user1 = client.post('/users', json={'name': 'User1', 'email': 'user1@example.com'}).get_json()
        client.post('/users', json={'name': 'User2', 'email': 'user2@example.com'})

        # Try to update user1 with user2's email
        response = client.put(f'/users/{user1["id"]}', json={
            'name': 'User1',
            'email': 'user2@example.com'
        })
        assert response.status_code == 409

    def test_update_user_invalid_id(self, client):
        """Test updating user with invalid ID returns 400"""
        response = client.put('/users/invalid', json={
            'name': 'Test',
            'email': 'test@example.com'
        })
        assert response.status_code == 400

    def test_update_user_invalid_email(self, client, sample_user):
        """Test updating user with invalid email returns 400"""
        response = client.put(f'/users/{sample_user["id"]}', json={
            'name': 'Test',
            'email': 'invalid-email'
        })
        assert response.status_code == 400


class TestDeleteUser:
    """Tests for DELETE /users/<id>"""

    def test_delete_user_success(self, client, sample_user):
        """Test successful user deletion"""
        user_id = sample_user['id']
        response = client.delete(f'/users/{user_id}')
        assert response.status_code == 204

        # Verify user is deleted
        response = client.get(f'/users/{user_id}')
        assert response.status_code == 404

    def test_delete_user_not_found(self, client):
        """Test deleting non-existent user returns 404"""
        response = client.delete('/users/9999')
        assert response.status_code == 404

    def test_delete_user_invalid_id(self, client):
        """Test deleting user with invalid ID returns 400"""
        response = client.delete('/users/invalid')
        assert response.status_code == 400


class TestSQLInjectionProtection:
    """
    CRITICAL SECURITY TESTS
    Tests that SQL injection attempts are safely handled
    """

    def test_sql_injection_in_name(self, client):
        """Test SQL injection attempt in name field is safely handled"""
        malicious_name = "'; DROP TABLE users; --"
        response = client.post('/users', json={
            'name': malicious_name,
            'email': 'test@example.com'
        })

        # Should succeed (name is treated as literal string, not SQL)
        assert response.status_code == 201

        # Verify users table still exists by querying it
        response = client.get('/users')
        assert response.status_code == 200

        # Verify the malicious name was stored as-is (not executed)
        users = response.get_json()
        assert any(user['name'] == malicious_name for user in users)

    def test_sql_injection_in_email(self, client):
        """Test SQL injection attempt in email field is safely handled"""
        malicious_email = "test@example.com'; DROP TABLE users; --"
        response = client.post('/users', json={
            'name': 'Test',
            'email': malicious_email
        })

        # Should fail validation (invalid email format)
        assert response.status_code == 400

    def test_sql_injection_in_get_user_id(self, client, sample_user):
        """Test SQL injection attempt in user ID parameter"""
        # SQL injection attempt in URL parameter
        malicious_id = "1 OR 1=1"
        response = client.get(f'/users/{malicious_id}')

        # Should fail validation (not a valid integer)
        assert response.status_code == 400

        # Verify database still works
        response = client.get(f'/users/{sample_user["id"]}')
        assert response.status_code == 200

    def test_sql_injection_in_update(self, client, sample_user):
        """Test SQL injection attempt in update"""
        malicious_name = "Test'; DELETE FROM users WHERE '1'='1"
        response = client.put(f'/users/{sample_user["id"]}', json={
            'name': malicious_name,
            'email': 'test@example.com'
        })

        # Should succeed (parameterized query treats it as literal)
        assert response.status_code == 200

        # Verify all users still exist
        response = client.get('/users')
        users = response.get_json()
        assert len(users) >= 1

    def test_sql_injection_union_attack(self, client):
        """Test SQL injection UNION attack is prevented"""
        malicious_name = "Test' UNION SELECT * FROM users WHERE '1'='1"
        response = client.post('/users', json={
            'name': malicious_name,
            'email': 'test@example.com'
        })

        # Should succeed (stored as literal string)
        assert response.status_code == 201

        # Verify only one user was created (not a union of data)
        response = client.get('/users')
        users = response.get_json()
        matching_users = [u for u in users if malicious_name in u['name']]
        assert len(matching_users) == 1

    def test_sql_injection_comment_attack(self, client, sample_user):
        """Test SQL injection with comment is prevented"""
        # Try to bypass WHERE clause with comment
        malicious_id = f"{sample_user['id']}; --"
        response = client.get(f'/users/{malicious_id}')

        # Should fail validation (not a valid integer)
        assert response.status_code == 400

    def test_sql_injection_string_termination(self, client):
        """Test SQL injection with string termination is prevented"""
        malicious_name = "Test'--"
        response = client.post('/users', json={
            'name': malicious_name,
            'email': 'test@example.com'
        })

        # Should succeed (stored as literal)
        assert response.status_code == 201

        # Verify data integrity
        response = client.get('/users')
        users = response.get_json()
        assert any(user['name'] == malicious_name for user in users)


class TestInputValidation:
    """Tests for comprehensive input validation"""

    def test_name_with_special_chars(self, client):
        """Test name with special characters is accepted"""
        response = client.post('/users', json={
            'name': "O'Brien",
            'email': 'obrien@example.com'
        })
        assert response.status_code == 201

    def test_email_case_insensitive(self, client):
        """Test emails are stored in lowercase"""
        response = client.post('/users', json={
            'name': 'Test',
            'email': 'TEST@EXAMPLE.COM'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['email'] == 'test@example.com'

    def test_null_values_rejected(self, client):
        """Test null values are rejected"""
        response = client.post('/users', json={
            'name': None,
            'email': 'test@example.com'
        })
        assert response.status_code == 400

"""
Unit Tests for Authentication System

Comprehensive test suite including environment variable mocking and security tests.
"""

import os
import time
import pytest
import sqlite3
import sys
import importlib.util
from pathlib import Path
from unittest.mock import patch, MagicMock

# Load modules from current directory using importlib
test_dir = Path(__file__).parent

def load_local_module(module_name):
    """Load module from test directory"""
    spec = importlib.util.spec_from_file_location(module_name, test_dir / f"{module_name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

user_manager = load_local_module("user_manager")
token_manager = load_local_module("token_manager")
auth_service = load_local_module("auth_service")

UserManager = user_manager.UserManager
User = user_manager.User
TokenManager = token_manager.TokenManager
AuthService = auth_service.AuthService


class TestUserManager:
    """Tests for UserManager"""

    @pytest.fixture
    def user_manager(self):
        """Create test user manager with in-memory DB"""
        return UserManager(":memory:")

    def test_create_user(self, user_manager):
        """Test user creation"""
        user = user_manager.create_user("testuser", "test@example.com", b"hashed_password")
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password_hash == b"hashed_password"

    def test_get_user_by_username(self, user_manager):
        """Test retrieving user by username"""
        user_manager.create_user("testuser", "test@example.com", b"hashed")
        user = user_manager.get_user_by_username("testuser")
        assert user is not None
        assert user.username == "testuser"

    def test_get_user_by_username_not_found(self, user_manager):
        """Test retrieving non-existent user returns None"""
        user = user_manager.get_user_by_username("nonexistent")
        assert user is None

    def test_get_user_by_id(self, user_manager):
        """Test retrieving user by ID"""
        created_user = user_manager.create_user("testuser", "test@example.com", b"hashed")
        user = user_manager.get_user_by_id(created_user.id)
        assert user is not None
        assert user.id == created_user.id

    def test_delete_user(self, user_manager):
        """Test user deletion"""
        created_user = user_manager.create_user("testuser", "test@example.com", b"hashed")
        result = user_manager.delete_user(created_user.id)
        assert result is True

        # Verify user is deleted
        user = user_manager.get_user_by_id(created_user.id)
        assert user is None

    def test_delete_nonexistent_user(self, user_manager):
        """Test deleting non-existent user returns False"""
        result = user_manager.delete_user(9999)
        assert result is False

    def test_duplicate_username(self, user_manager):
        """Test creating user with duplicate username raises error"""
        user_manager.create_user("testuser", "test1@example.com", b"hashed")
        with pytest.raises(sqlite3.IntegrityError):
            user_manager.create_user("testuser", "test2@example.com", b"hashed")


class TestTokenManager:
    """Tests for TokenManager"""

    @pytest.fixture
    def token_manager(self):
        """Create token manager with mocked environment"""
        with patch.dict(os.environ, {'JWT_SECRET': 'test-secret-key-for-testing'}):
            return TokenManager()

    def test_initialization_without_secret_raises_error(self):
        """Test that TokenManager raises error if JWT_SECRET not set"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(EnvironmentError, match="JWT_SECRET"):
                TokenManager()

    def test_initialization_with_secret(self):
        """Test successful initialization with JWT_SECRET"""
        with patch.dict(os.environ, {'JWT_SECRET': 'test-secret'}):
            tm = TokenManager()
            assert tm.secret == 'test-secret'

    def test_generate_access_token(self, token_manager):
        """Test access token generation"""
        token = token_manager.generate_access_token(123)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_refresh_token(self, token_manager):
        """Test refresh token generation"""
        token = token_manager.generate_refresh_token(123)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_validate_valid_access_token(self, token_manager):
        """Test validating a valid access token"""
        token = token_manager.generate_access_token(123)
        payload = token_manager.validate_token(token)
        assert payload is not None
        assert payload['user_id'] == 123
        assert payload['type'] == 'access'

    def test_validate_valid_refresh_token(self, token_manager):
        """Test validating a valid refresh token"""
        token = token_manager.generate_refresh_token(456)
        payload = token_manager.validate_token(token)
        assert payload is not None
        assert payload['user_id'] == 456
        assert payload['type'] == 'refresh'

    def test_validate_invalid_token(self, token_manager):
        """Test validating an invalid token returns None"""
        payload = token_manager.validate_token("invalid.token.here")
        assert payload is None

    def test_revoke_token(self, token_manager):
        """Test token revocation"""
        token = token_manager.generate_access_token(123)

        # Token should be valid initially
        payload = token_manager.validate_token(token)
        assert payload is not None

        # Revoke token
        result = token_manager.revoke_token(token)
        assert result is True

        # Token should now be invalid
        payload = token_manager.validate_token(token)
        assert payload is None

    def test_is_token_revoked(self, token_manager):
        """Test checking if token is revoked"""
        token = token_manager.generate_access_token(123)

        assert token_manager.is_token_revoked(token) is False

        token_manager.revoke_token(token)

        assert token_manager.is_token_revoked(token) is True


class TestAuthService:
    """Tests for AuthService"""

    @pytest.fixture
    def auth_service(self):
        """Create auth service with test dependencies"""
        with patch.dict(os.environ, {'JWT_SECRET': 'test-secret-key-for-testing'}):
            user_manager = UserManager(":memory:")
            token_manager = TokenManager()
            return AuthService(user_manager, token_manager)

    def test_register_success(self, auth_service):
        """Test successful user registration"""
        success, msg, user = auth_service.register("testuser", "Password123", "test@example.com")
        assert success is True
        assert "successfully" in msg.lower()
        assert user is not None
        assert user.username == "testuser"

    def test_register_username_too_short(self, auth_service):
        """Test registration with too short username"""
        success, msg, user = auth_service.register("ab", "Password123", "test@example.com")
        assert success is False
        assert "3-50 characters" in msg
        assert user is None

    def test_register_username_invalid_chars(self, auth_service):
        """Test registration with invalid username characters"""
        success, msg, user = auth_service.register("user@name", "Password123", "test@example.com")
        assert success is False
        assert "letters, numbers, and underscores" in msg

    def test_register_password_too_short(self, auth_service):
        """Test registration with too short password"""
        success, msg, user = auth_service.register("testuser", "Pass1", "test@example.com")
        assert success is False
        assert "at least 8 characters" in msg

    def test_register_password_no_uppercase(self, auth_service):
        """Test registration with password missing uppercase letter"""
        success, msg, user = auth_service.register("testuser", "password123", "test@example.com")
        assert success is False
        assert "uppercase letter" in msg

    def test_register_password_no_number(self, auth_service):
        """Test registration with password missing number"""
        success, msg, user = auth_service.register("testuser", "Password", "test@example.com")
        assert success is False
        assert "number" in msg

    def test_register_invalid_email(self, auth_service):
        """Test registration with invalid email"""
        success, msg, user = auth_service.register("testuser", "Password123", "invalid-email")
        assert success is False
        assert "email format" in msg.lower()

    def test_register_duplicate_username(self, auth_service):
        """Test registration with duplicate username"""
        auth_service.register("testuser", "Password123", "test1@example.com")
        success, msg, user = auth_service.register("testuser", "Password123", "test2@example.com")
        assert success is False
        assert "already exists" in msg.lower()

    def test_login_success(self, auth_service):
        """Test successful login"""
        # Register user
        auth_service.register("testuser", "Password123", "test@example.com")

        # Login
        success, msg, tokens = auth_service.login("testuser", "Password123")
        assert success is True
        assert "successful" in msg.lower()
        assert tokens is not None
        assert 'access_token' in tokens
        assert 'refresh_token' in tokens
        assert tokens['token_type'] == 'Bearer'

    def test_login_wrong_password(self, auth_service):
        """Test login with wrong password"""
        auth_service.register("testuser", "Password123", "test@example.com")
        success, msg, tokens = auth_service.login("testuser", "WrongPassword123")
        assert success is False
        assert "Invalid credentials" in msg
        assert tokens is None

    def test_login_nonexistent_user(self, auth_service):
        """Test login with non-existent username"""
        success, msg, tokens = auth_service.login("nonexistent", "Password123")
        assert success is False
        assert "Invalid credentials" in msg
        assert tokens is None

    def test_logout(self, auth_service):
        """Test logout functionality"""
        # Register and login
        auth_service.register("testuser", "Password123", "test@example.com")
        success, msg, tokens = auth_service.login("testuser", "Password123")
        access_token = tokens['access_token']

        # Logout
        result = auth_service.logout(access_token)
        assert result is True

        # Token should be revoked
        user_id = auth_service.validate_access_token(access_token)
        assert user_id is None

    def test_refresh_tokens(self, auth_service):
        """Test refreshing tokens"""
        # Register and login
        auth_service.register("testuser", "Password123", "test@example.com")
        success, msg, tokens = auth_service.login("testuser", "Password123")
        refresh_token = tokens['refresh_token']

        # Refresh
        success, msg, new_tokens = auth_service.refresh(refresh_token)
        assert success is True
        assert "refreshed" in msg.lower()
        assert new_tokens is not None
        assert 'access_token' in new_tokens
        assert 'refresh_token' in new_tokens

    def test_refresh_with_invalid_token(self, auth_service):
        """Test refresh with invalid token"""
        success, msg, tokens = auth_service.refresh("invalid.token.here")
        assert success is False
        assert "Invalid" in msg
        assert tokens is None

    def test_refresh_with_access_token(self, auth_service):
        """Test refresh with access token (should fail, need refresh token)"""
        auth_service.register("testuser", "Password123", "test@example.com")
        success, msg, tokens = auth_service.login("testuser", "Password123")
        access_token = tokens['access_token']

        # Try to use access token for refresh (should fail)
        success, msg, new_tokens = auth_service.refresh(access_token)
        assert success is False
        assert "token type" in msg.lower()

    def test_validate_access_token(self, auth_service):
        """Test validating access token"""
        # Register and login
        auth_service.register("testuser", "Password123", "test@example.com")
        success, msg, tokens = auth_service.login("testuser", "Password123")
        access_token = tokens['access_token']

        # Validate
        user_id = auth_service.validate_access_token(access_token)
        assert user_id is not None
        assert isinstance(user_id, int)

    def test_validate_invalid_access_token(self, auth_service):
        """Test validating invalid access token"""
        user_id = auth_service.validate_access_token("invalid.token.here")
        assert user_id is None

    def test_validate_refresh_token_as_access(self, auth_service):
        """Test validating refresh token as access token (should fail)"""
        auth_service.register("testuser", "Password123", "test@example.com")
        success, msg, tokens = auth_service.login("testuser", "Password123")
        refresh_token = tokens['refresh_token']

        # Try to validate refresh token as access token
        user_id = auth_service.validate_access_token(refresh_token)
        assert user_id is None


class TestDependencyInjection:
    """Tests for Dependency Injection in AuthService"""

    def test_auth_service_with_mock_user_manager(self):
        """Test AuthService with mocked UserManager"""
        mock_user_manager = MagicMock(spec=UserManager)
        mock_user = User(id=1, username="testuser", email="test@example.com", password_hash=b"hashed")
        mock_user_manager.get_user_by_username.return_value = mock_user

        with patch.dict(os.environ, {'JWT_SECRET': 'test-secret'}):
            token_manager = TokenManager()
            auth_service = AuthService(mock_user_manager, token_manager)

            # Call method that uses user_manager
            user = auth_service.user_manager.get_user_by_username("testuser")

            # Verify mock was called
            mock_user_manager.get_user_by_username.assert_called_once_with("testuser")
            assert user == mock_user

    def test_auth_service_with_mock_token_manager(self):
        """Test AuthService with mocked TokenManager"""
        with patch.dict(os.environ, {'JWT_SECRET': 'test-secret'}):
            user_manager = UserManager(":memory:")
            mock_token_manager = MagicMock(spec=TokenManager)
            mock_token_manager.generate_access_token.return_value = "mock_access_token"
            mock_token_manager.generate_refresh_token.return_value = "mock_refresh_token"

            auth_service = AuthService(user_manager, mock_token_manager)

            # Register and login
            auth_service.register("testuser", "Password123", "test@example.com")

            # Mock bcrypt to avoid actual password hashing in this test
            with patch('auth_service.bcrypt.checkpw', return_value=True):
                success, msg, tokens = auth_service.login("testuser", "Password123")

            assert tokens['access_token'] == "mock_access_token"
            assert tokens['refresh_token'] == "mock_refresh_token"


class TestPasswordHashing:
    """Tests for password hashing"""

    @pytest.fixture
    def auth_service(self):
        """Create auth service"""
        with patch.dict(os.environ, {'JWT_SECRET': 'test-secret'}):
            return AuthService(UserManager(":memory:"), TokenManager())

    def test_password_is_hashed(self, auth_service):
        """Test that passwords are hashed, not stored in plain text"""
        auth_service.register("testuser", "Password123", "test@example.com")
        user = auth_service.user_manager.get_user_by_username("testuser")

        # Password hash should not equal plain password
        assert user.password_hash != b"Password123"
        assert user.password_hash != "Password123"

        # Should start with bcrypt identifier
        assert user.password_hash.startswith(b'$2b$')

    def test_same_password_different_hashes(self, auth_service):
        """Test that same password produces different hashes (salt)"""
        auth_service.register("user1", "Password123", "user1@example.com")
        auth_service.register("user2", "Password123", "user2@example.com")

        user1 = auth_service.user_manager.get_user_by_username("user1")
        user2 = auth_service.user_manager.get_user_by_username("user2")

        # Same password, but different hashes due to salt
        assert user1.password_hash != user2.password_hash

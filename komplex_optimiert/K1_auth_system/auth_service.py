"""
Authentication Service Module

Orchestrates authentication logic using UserManager and TokenManager.
Uses Dependency Injection for testability.
"""

import bcrypt
import re
from typing import Optional, Tuple
from user_manager import UserManager, User
from token_manager import TokenManager


class AuthService:
    """
    Main authentication service.

    Responsibility: Authentication business logic.
    Coordinates between UserManager (persistence) and TokenManager (tokens).

    Uses Dependency Injection for flexibility and testability.
    """

    def __init__(
        self,
        user_manager: Optional[UserManager] = None,
        token_manager: Optional[TokenManager] = None
    ):
        """
        Initialize authentication service.

        Dependency Injection: Accepts optional dependencies for testing.

        Args:
            user_manager: UserManager instance (creates default if None)
            token_manager: TokenManager instance (creates default if None)
        """
        self.user_manager = user_manager or UserManager()
        self.token_manager = token_manager or TokenManager()

    def _validate_username(self, username: str) -> Tuple[bool, str]:
        """
        Validate username format.

        Args:
            username: Username to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username or len(username) < 3 or len(username) > 50:
            return False, "Username must be 3-50 characters"

        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"

        return True, ""

    def _validate_password(self, password: str) -> Tuple[bool, str]:
        """
        Validate password strength.

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters"

        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"

        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one number"

        return True, ""

    def _validate_email(self, email: str) -> Tuple[bool, str]:
        """
        Validate email format.

        Args:
            email: Email to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"

        return True, ""

    def _hash_password(self, password: str) -> bytes:
        """
        Hash a password using bcrypt.

        SECURITY: Uses bcrypt (not MD5, not SHA-256).

        Args:
            password: Plain text password

        Returns:
            Hashed password as bytes
        """
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def _verify_password(self, password: str, hashed: bytes) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: Plain text password
            hashed: Hashed password

        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed)

    def register(
        self,
        username: str,
        password: str,
        email: str
    ) -> Tuple[bool, str, Optional[User]]:
        """
        Register a new user.

        Args:
            username: Username
            password: Plain text password
            email: Email address

        Returns:
            Tuple of (success, message, user)
            user is None if registration fails
        """
        # Validate username
        valid, msg = self._validate_username(username)
        if not valid:
            return False, msg, None

        # Validate password
        valid, msg = self._validate_password(password)
        if not valid:
            return False, msg, None

        # Validate email
        valid, msg = self._validate_email(email)
        if not valid:
            return False, msg, None

        # Check if user exists
        if self.user_manager.get_user_by_username(username):
            return False, "Username already exists", None

        # Hash password
        password_hash = self._hash_password(password)

        # Create user
        try:
            user = self.user_manager.create_user(username, email, password_hash)
            return True, "User registered successfully", user
        except Exception as e:
            # Could be database error, email already exists, etc.
            return False, f"Registration failed: {str(e)}", None

    def login(self, username: str, password: str) -> Tuple[bool, str, Optional[dict]]:
        """
        Log in a user.

        Args:
            username: Username
            password: Plain text password

        Returns:
            Tuple of (success, message, tokens)
            tokens is dict with access_token, refresh_token, token_type if successful
            tokens is None if login fails
        """
        # Get user
        user = self.user_manager.get_user_by_username(username)
        if not user:
            return False, "Invalid credentials", None

        # Verify password
        if not self._verify_password(password, user.password_hash):
            return False, "Invalid credentials", None

        # Generate tokens
        tokens = {
            "access_token": self.token_manager.generate_access_token(user.id),
            "refresh_token": self.token_manager.generate_refresh_token(user.id),
            "token_type": "Bearer"
        }

        return True, "Login successful", tokens

    def logout(self, access_token: str) -> bool:
        """
        Log out a user by revoking their access token.

        Args:
            access_token: Access token to revoke

        Returns:
            True (always succeeds)
        """
        return self.token_manager.revoke_token(access_token)

    def refresh(self, refresh_token: str) -> Tuple[bool, str, Optional[dict]]:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Refresh token

        Returns:
            Tuple of (success, message, tokens)
            tokens contains new access_token and refresh_token if successful
        """
        # Validate refresh token
        payload = self.token_manager.validate_token(refresh_token)
        if not payload:
            return False, "Invalid refresh token", None

        # Check token type
        if payload.get("type") != "refresh":
            return False, "Invalid token type", None

        # Generate new tokens
        user_id = payload["user_id"]
        new_tokens = {
            "access_token": self.token_manager.generate_access_token(user_id),
            "refresh_token": self.token_manager.generate_refresh_token(user_id),
            "token_type": "Bearer"
        }

        return True, "Tokens refreshed", new_tokens

    def validate_access_token(self, access_token: str) -> Optional[int]:
        """
        Validate an access token and extract user ID.

        Args:
            access_token: Access token to validate

        Returns:
            User ID if valid, None if invalid
        """
        payload = self.token_manager.validate_token(access_token)
        if not payload:
            return None

        if payload.get("type") != "access":
            return None

        return payload.get("user_id")

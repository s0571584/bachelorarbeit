"""
Token Manager Module

Responsible ONLY for JWT token generation and validation.
CRITICAL: JWT_SECRET must come from environment variable, never hardcoded.
"""

import os
import jwt
from datetime import datetime, timedelta, UTC
from typing import Optional


class TokenManager:
    """
    Manages JWT tokens for authentication.

    Single Responsibility: Token operations only.
    No user management, no password handling, no business logic.

    SECURITY CRITICAL:
    - JWT_SECRET loaded from environment variable
    - Raises EnvironmentError if JWT_SECRET not set
    - Never hardcode secrets in code!
    """

    def __init__(self):
        """
        Initialize token manager.

        SECURITY: Reads JWT_SECRET from environment variable.

        Raises:
            EnvironmentError: If JWT_SECRET environment variable not set
        """
        # SECURITY: MUST read from environment, never hardcode
        self.secret = os.environ.get('JWT_SECRET')
        if not self.secret:
            raise EnvironmentError(
                "JWT_SECRET environment variable must be set. "
                "Never hardcode secrets in code!"
            )

        self.algorithm = "HS256"
        self.access_token_expiry = timedelta(hours=1)
        self.refresh_token_expiry = timedelta(days=7)

        # Token revocation list (in-memory for demo, use Redis in production)
        self._revoked_tokens: set = set()

    def generate_access_token(self, user_id: int) -> str:
        """
        Generate an access token for a user.

        Args:
            user_id: User ID to encode in token

        Returns:
            JWT access token string
        """
        payload = {
            "user_id": user_id,
            "type": "access",
            "exp": datetime.now(UTC) + self.access_token_expiry,
            "iat": datetime.now(UTC)
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def generate_refresh_token(self, user_id: int) -> str:
        """
        Generate a refresh token for a user.

        Args:
            user_id: User ID to encode in token

        Returns:
            JWT refresh token string
        """
        payload = {
            "user_id": user_id,
            "type": "refresh",
            "exp": datetime.now(UTC) + self.refresh_token_expiry,
            "iat": datetime.now(UTC)
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def validate_token(self, token: str) -> Optional[dict]:
        """
        Validate and decode a JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded payload dict if valid, None if invalid/expired/revoked
        """
        # Check revocation list
        if token in self._revoked_tokens:
            return None

        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            # Token has expired
            return None
        except jwt.InvalidTokenError:
            # Token is invalid (bad signature, malformed, etc.)
            return None

    def revoke_token(self, token: str) -> bool:
        """
        Revoke a token (for logout).

        In production, use Redis or database for revocation list.

        Args:
            token: JWT token string to revoke

        Returns:
            True (always succeeds)
        """
        self._revoked_tokens.add(token)
        return True

    def is_token_revoked(self, token: str) -> bool:
        """
        Check if a token has been revoked.

        Args:
            token: JWT token string

        Returns:
            True if revoked, False otherwise
        """
        return token in self._revoked_tokens

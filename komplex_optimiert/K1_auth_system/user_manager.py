"""
User Manager Module

Responsible ONLY for user database operations.
Uses parameterized queries to prevent SQL injection.
"""

import sqlite3
from contextlib import contextmanager
from typing import Optional
from dataclasses import dataclass


@dataclass
class User:
    """User data class"""
    id: int
    username: str
    email: str
    password_hash: bytes


class UserManager:
    """
    Manages user data in database.

    Single Responsibility: Database operations only.
    No authentication logic, no password hashing, no token management.
    """

    def __init__(self, db_path: str = "users.db"):
        """
        Initialize user manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._persistent_conn = None

        # For in-memory databases, keep connection open
        if db_path == ":memory:":
            self._persistent_conn = sqlite3.connect(db_path, check_same_thread=False)

        self._init_db()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        if self._persistent_conn is not None:
            try:
                yield self._persistent_conn
                self._persistent_conn.commit()
            except Exception:
                self._persistent_conn.rollback()
                raise
        else:
            conn = sqlite3.connect(self.db_path)
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

    def _init_db(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash BLOB NOT NULL
                )
            """)

    def create_user(self, username: str, email: str, password_hash: bytes) -> User:
        """
        Create a new user.

        SECURITY: Uses parameterized query.

        Args:
            username: Username
            email: Email address
            password_hash: Hashed password (bytes)

        Returns:
            User object

        Raises:
            sqlite3.IntegrityError: If username or email already exists
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # SECURITY: Parameterized query
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            user_id = cursor.lastrowid
            return User(
                id=user_id,
                username=username,
                email=email,
                password_hash=password_hash
            )

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.

        SECURITY: Uses parameterized query.

        Args:
            username: Username to search for

        Returns:
            User object or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # SECURITY: Parameterized query
            cursor.execute(
                "SELECT id, username, email, password_hash FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            if row:
                return User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    password_hash=row[3]
                )
            return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.

        SECURITY: Uses parameterized query.

        Args:
            user_id: User ID

        Returns:
            User object or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # SECURITY: Parameterized query
            cursor.execute(
                "SELECT id, username, email, password_hash FROM users WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            if row:
                return User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    password_hash=row[3]
                )
            return None

    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user.

        SECURITY: Uses parameterized query.

        Args:
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # SECURITY: Parameterized query
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            return cursor.rowcount > 0

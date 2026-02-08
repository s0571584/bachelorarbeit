"""
Database Module for User Management

SECURITY CRITICAL: All database queries use parameterized queries to prevent SQL injection.
NEVER use string concatenation or f-strings for SQL queries.
"""

import sqlite3
from contextlib import contextmanager
from typing import Optional, List, Dict, Any


class Database:
    """
    Database manager for user operations.

    Security: All queries use parameterized queries (? placeholders) to prevent SQL injection.
    """

    def __init__(self, db_path: str = "users.db"):
        """
        Initialize database and create table if it doesn't exist.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._persistent_conn = None  # For in-memory databases

        # For in-memory databases, keep connection open
        if db_path == ":memory:":
            self._persistent_conn = sqlite3.connect(db_path, check_same_thread=False)
            self._persistent_conn.row_factory = sqlite3.Row

        self._init_db()

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.

        Yields:
            sqlite3.Connection: Database connection

        Usage:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                ...
        """
        # Use persistent connection for in-memory databases
        if self._persistent_conn is not None:
            try:
                yield self._persistent_conn
                self._persistent_conn.commit()
            except Exception:
                self._persistent_conn.rollback()
                raise
        else:
            # Normal file-based database
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

    def _init_db(self):
        """
        Initialize database schema.
        Creates users table if it doesn't exist.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # SECURITY: This is a CREATE TABLE statement, safe to use without parameters
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL
                )
            """)

    def create_user(self, name: str, email: str) -> Dict[str, Any]:
        """
        Create a new user.

        SECURITY: Uses parameterized query with ? placeholders.

        Args:
            name: User's name
            email: User's email

        Returns:
            Dict containing user data with id, name, email

        Raises:
            sqlite3.IntegrityError: If email already exists
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # SECURITY: CORRECT - Parameterized query with ? placeholders
            cursor.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                (name, email)
            )
            user_id = cursor.lastrowid
            return {"id": user_id, "name": name, "email": email}

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a user by ID.

        SECURITY: Uses parameterized query with ? placeholder.

        Args:
            user_id: User ID

        Returns:
            Dict containing user data, or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # SECURITY: CORRECT - Parameterized query with ? placeholder
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Get all users.

        Returns:
            List of dicts containing user data
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # SECURITY: No parameters needed, safe query
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def update_user(self, user_id: int, name: str, email: str) -> bool:
        """
        Update a user.

        SECURITY: Uses parameterized query with ? placeholders.

        Args:
            user_id: User ID
            name: New name
            email: New email

        Returns:
            True if user was updated, False if not found

        Raises:
            sqlite3.IntegrityError: If email already exists for another user
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # SECURITY: CORRECT - Parameterized query with ? placeholders
            cursor.execute(
                "UPDATE users SET name = ?, email = ? WHERE id = ?",
                (name, email, user_id)
            )
            return cursor.rowcount > 0

    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user.

        SECURITY: Uses parameterized query with ? placeholder.

        Args:
            user_id: User ID

        Returns:
            True if user was deleted, False if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # SECURITY: CORRECT - Parameterized query with ? placeholder
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            return cursor.rowcount > 0

    def user_exists_by_email(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """
        Check if a user with given email exists.

        SECURITY: Uses parameterized query with ? placeholders.

        Args:
            email: Email to check
            exclude_id: Optional user ID to exclude from check (for updates)

        Returns:
            True if email exists, False otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if exclude_id is not None:
                # SECURITY: CORRECT - Parameterized query
                cursor.execute(
                    "SELECT COUNT(*) FROM users WHERE email = ? AND id != ?",
                    (email, exclude_id)
                )
            else:
                # SECURITY: CORRECT - Parameterized query
                cursor.execute(
                    "SELECT COUNT(*) FROM users WHERE email = ?",
                    (email,)
                )
            count = cursor.fetchone()[0]
            return count > 0

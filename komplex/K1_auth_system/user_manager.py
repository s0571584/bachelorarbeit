"""
User Manager - Verwaltet User-Daten in SQLite
"""

import sqlite3
import hashlib
from typing import Optional, Dict


class UserManager:
    """
    User Manager - CRUD-Operationen für User mit SQLite
    """

    def __init__(self, db_path: str = ':memory:'):
        """
        Initialisiert den User Manager.

        Args:
            db_path (str): Pfad zur Datenbank-Datei (Standard: In-Memory)
        """
        self.db_path = db_path
        self.connection = None

    def connect(self):
        """Stellt Verbindung zur Datenbank her"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row

    def close(self):
        """Schließt die Datenbankverbindung"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def create_table(self):
        """Erstellt die users Tabelle"""
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.connection.commit()

    def create_user(self, username: str, email: str, password_hash: str) -> int:
        """
        Erstellt einen neuen User.

        Args:
            username (str): Benutzername
            email (str): Email
            password_hash (str): Gehashtes Passwort

        Returns:
            int: ID des erstellten Users

        Raises:
            ValueError: Wenn username oder email bereits existieren
        """
        if not self.connection:
            self.connect()

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError("Username oder Email bereits vergeben")

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """
        Ruft einen User anhand des Usernames ab.

        Args:
            username (str): Benutzername

        Returns:
            Optional[Dict]: User-Daten oder None
        """
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Ruft einen User anhand der Email ab.

        Args:
            email (str): Email

        Returns:
            Optional[Dict]: User-Daten oder None
        """
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """
        Ruft einen User anhand der ID ab.

        Args:
            user_id (int): User-ID

        Returns:
            Optional[Dict]: User-Daten oder None
        """
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def verify_password(self, user: Dict, password: str) -> bool:
        """
        Verifiziert das Passwort eines Users.

        Args:
            user (Dict): User-Daten
            password (str): Klartext-Passwort

        Returns:
            bool: True wenn Passwort korrekt
        """
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return user['password_hash'] == password_hash

    def update_password(self, user_id: int, new_password_hash: str) -> bool:
        """
        Aktualisiert das Passwort eines Users.

        Args:
            user_id (int): User-ID
            new_password_hash (str): Neues gehashtes Passwort

        Returns:
            bool: True wenn erfolgreich
        """
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_password_hash, user_id))
        self.connection.commit()
        return cursor.rowcount > 0

    def delete_user(self, user_id: int) -> bool:
        """
        Löscht einen User.

        Args:
            user_id (int): User-ID

        Returns:
            bool: True wenn erfolgreich
        """
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def __enter__(self):
        """Context Manager: Öffnet Verbindung"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context Manager: Schließt Verbindung"""
        self.close()


if __name__ == "__main__":
    # Beispiel-Verwendung
    with UserManager() as um:
        um.create_table()

        # User erstellen
        password_hash = hashlib.sha256("mypassword".encode()).hexdigest()
        user_id = um.create_user("alice", "alice@example.com", password_hash)
        print(f"User erstellt mit ID: {user_id}")

        # User abrufen
        user = um.get_user_by_username("alice")
        print(f"User: {user}")

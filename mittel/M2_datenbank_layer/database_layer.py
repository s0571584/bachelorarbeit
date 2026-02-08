"""
Datenbank-Layer für SQLite mit CRUD-Operationen
"""

import sqlite3
from typing import List, Dict, Optional


class DatabaseManager:
    """
    Datenbank-Manager für SQLite mit CRUD-Operationen
    """

    def __init__(self, db_path: str = ':memory:'):
        """
        Initialisiert den Datenbank-Manager.

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
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
        ''')
        self.connection.commit()

    def insert(self, name: str, email: str) -> int:
        """
        Fügt einen neuen User ein.

        Args:
            name (str): Name des Users
            email (str): Email des Users

        Returns:
            int: ID des eingefügten Users

        Raises:
            ValueError: Wenn Name oder Email leer sind
            sqlite3.IntegrityError: Wenn Email bereits existiert
        """
        if not name or not email:
            raise ValueError("Name und Email dürfen nicht leer sein")

        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        cursor.execute('INSERT INTO users (name, email) VALUES (?, ?)', (name, email))
        self.connection.commit()
        return cursor.lastrowid

    def select(self, user_id: Optional[int] = None) -> List[Dict]:
        """
        Ruft User(s) ab.

        Args:
            user_id (int, optional): ID des Users. Wenn None, werden alle Users abgerufen.

        Returns:
            List[Dict]: Liste von User-Dictionaries
        """
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()

        if user_id is not None:
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return [dict(row)] if row else []
        else:
            cursor.execute('SELECT * FROM users')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def update(self, user_id: int, name: Optional[str] = None, email: Optional[str] = None) -> bool:
        """
        Aktualisiert einen User.

        Args:
            user_id (int): ID des Users
            name (str, optional): Neuer Name
            email (str, optional): Neue Email

        Returns:
            bool: True wenn erfolgreich, False wenn User nicht gefunden

        Raises:
            ValueError: Wenn weder Name noch Email angegeben sind
            sqlite3.IntegrityError: Wenn Email bereits existiert
        """
        if name is None and email is None:
            raise ValueError("Mindestens ein Feld muss aktualisiert werden")

        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()

        # Baue UPDATE-Query dynamisch
        updates = []
        params = []

        if name is not None:
            updates.append('name = ?')
            params.append(name)

        if email is not None:
            updates.append('email = ?')
            params.append(email)

        params.append(user_id)

        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        self.connection.commit()

        return cursor.rowcount > 0

    def delete(self, user_id: int) -> bool:
        """
        Löscht einen User.

        Args:
            user_id (int): ID des Users

        Returns:
            bool: True wenn erfolgreich, False wenn User nicht gefunden
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
    with DatabaseManager() as db:
        # Tabelle erstellen
        db.create_table()

        # Users einfügen
        id1 = db.insert('Alice', 'alice@example.com')
        id2 = db.insert('Bob', 'bob@example.com')
        print(f"Eingefügt: Alice (ID: {id1}), Bob (ID: {id2})")

        # Alle Users abrufen
        all_users = db.select()
        print(f"\nAlle Users: {all_users}")

        # Einzelnen User abrufen
        user = db.select(id1)
        print(f"\nUser mit ID {id1}: {user}")

        # User aktualisieren
        db.update(id1, name='Alice Updated')
        updated_user = db.select(id1)
        print(f"\nAktualisierter User: {updated_user}")

        # User löschen
        db.delete(id2)
        remaining_users = db.select()
        print(f"\nVerbleibende Users: {remaining_users}")

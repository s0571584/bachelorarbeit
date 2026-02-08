"""
Unit Tests für database_layer.py
"""

import unittest
import sqlite3
from database_layer import DatabaseManager


class TestDatabaseManager(unittest.TestCase):

    def setUp(self):
        """Setup - Erstelle In-Memory Datenbank"""
        self.db = DatabaseManager(':memory:')
        self.db.connect()
        self.db.create_table()

    def tearDown(self):
        """Cleanup - Schließe Datenbankverbindung"""
        self.db.close()

    def test_create_table(self):
        """Test: Tabelle erstellen"""
        # Prüfe, ob Tabelle existiert
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        result = cursor.fetchone()
        self.assertIsNotNone(result)

    def test_insert_user(self):
        """Test: User einfügen"""
        user_id = self.db.insert('Alice', 'alice@example.com')
        self.assertIsInstance(user_id, int)
        self.assertGreater(user_id, 0)

    def test_insert_empty_fields(self):
        """Test: User einfügen mit leeren Feldern"""
        with self.assertRaises(ValueError):
            self.db.insert('', 'test@example.com')

        with self.assertRaises(ValueError):
            self.db.insert('Test', '')

    def test_insert_duplicate_email(self):
        """Test: User einfügen mit doppelter Email"""
        self.db.insert('Alice', 'alice@example.com')
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.insert('Bob', 'alice@example.com')

    def test_select_all_users(self):
        """Test: Alle Users abrufen"""
        self.db.insert('Alice', 'alice@example.com')
        self.db.insert('Bob', 'bob@example.com')

        users = self.db.select()
        self.assertEqual(len(users), 2)

    def test_select_single_user(self):
        """Test: Einzelnen User abrufen"""
        user_id = self.db.insert('Alice', 'alice@example.com')
        users = self.db.select(user_id)

        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['name'], 'Alice')
        self.assertEqual(users[0]['email'], 'alice@example.com')

    def test_select_nonexistent_user(self):
        """Test: Nicht-existierenden User abrufen"""
        users = self.db.select(999)
        self.assertEqual(len(users), 0)

    def test_select_empty_table(self):
        """Test: Alle Users abrufen (leere Tabelle)"""
        users = self.db.select()
        self.assertEqual(len(users), 0)

    def test_update_user_name(self):
        """Test: User Name aktualisieren"""
        user_id = self.db.insert('Alice', 'alice@example.com')
        result = self.db.update(user_id, name='Alice Updated')

        self.assertTrue(result)
        users = self.db.select(user_id)
        self.assertEqual(users[0]['name'], 'Alice Updated')
        self.assertEqual(users[0]['email'], 'alice@example.com')  # Email unverändert

    def test_update_user_email(self):
        """Test: User Email aktualisieren"""
        user_id = self.db.insert('Alice', 'alice@example.com')
        result = self.db.update(user_id, email='alice.new@example.com')

        self.assertTrue(result)
        users = self.db.select(user_id)
        self.assertEqual(users[0]['email'], 'alice.new@example.com')
        self.assertEqual(users[0]['name'], 'Alice')  # Name unverändert

    def test_update_user_both_fields(self):
        """Test: User Name und Email aktualisieren"""
        user_id = self.db.insert('Alice', 'alice@example.com')
        result = self.db.update(user_id, name='Alice Updated', email='alice.new@example.com')

        self.assertTrue(result)
        users = self.db.select(user_id)
        self.assertEqual(users[0]['name'], 'Alice Updated')
        self.assertEqual(users[0]['email'], 'alice.new@example.com')

    def test_update_nonexistent_user(self):
        """Test: Nicht-existierenden User aktualisieren"""
        result = self.db.update(999, name='Test')
        self.assertFalse(result)

    def test_update_no_fields(self):
        """Test: Update ohne Felder"""
        user_id = self.db.insert('Alice', 'alice@example.com')
        with self.assertRaises(ValueError):
            self.db.update(user_id)

    def test_update_duplicate_email(self):
        """Test: Update mit bereits existierender Email"""
        self.db.insert('Alice', 'alice@example.com')
        user_id2 = self.db.insert('Bob', 'bob@example.com')

        with self.assertRaises(sqlite3.IntegrityError):
            self.db.update(user_id2, email='alice@example.com')

    def test_delete_user(self):
        """Test: User löschen"""
        user_id = self.db.insert('Alice', 'alice@example.com')
        result = self.db.delete(user_id)

        self.assertTrue(result)
        users = self.db.select(user_id)
        self.assertEqual(len(users), 0)

    def test_delete_nonexistent_user(self):
        """Test: Nicht-existierenden User löschen"""
        result = self.db.delete(999)
        self.assertFalse(result)

    def test_context_manager(self):
        """Test: Context Manager Funktionalität"""
        with DatabaseManager(':memory:') as db:
            db.create_table()
            user_id = db.insert('Alice', 'alice@example.com')
            users = db.select(user_id)
            self.assertEqual(len(users), 1)

        # Verbindung sollte geschlossen sein
        self.assertIsNone(db.connection)


if __name__ == '__main__':
    unittest.main()

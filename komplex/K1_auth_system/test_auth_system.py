"""
Unit Tests für das Authentication System
"""

import unittest
import time
from user_manager import UserManager
from token_manager import TokenManager
from auth_service import AuthService


class TestUserManager(unittest.TestCase):

    def setUp(self):
        """Setup - Erstelle In-Memory Datenbank"""
        self.um = UserManager(':memory:')
        self.um.connect()
        self.um.create_table()

    def tearDown(self):
        """Cleanup - Schließe Datenbankverbindung"""
        self.um.close()

    def test_create_user(self):
        """Test: User erstellen"""
        user_id = self.um.create_user("alice", "alice@example.com", "hash123")
        self.assertGreater(user_id, 0)

    def test_create_duplicate_username(self):
        """Test: Doppelter Username"""
        self.um.create_user("alice", "alice@example.com", "hash123")
        with self.assertRaises(ValueError):
            self.um.create_user("alice", "different@example.com", "hash456")

    def test_create_duplicate_email(self):
        """Test: Doppelte Email"""
        self.um.create_user("alice", "alice@example.com", "hash123")
        with self.assertRaises(ValueError):
            self.um.create_user("bob", "alice@example.com", "hash456")

    def test_get_user_by_username(self):
        """Test: User anhand Username abrufen"""
        self.um.create_user("alice", "alice@example.com", "hash123")
        user = self.um.get_user_by_username("alice")
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], "alice")

    def test_get_user_by_email(self):
        """Test: User anhand Email abrufen"""
        self.um.create_user("alice", "alice@example.com", "hash123")
        user = self.um.get_user_by_email("alice@example.com")
        self.assertIsNotNone(user)
        self.assertEqual(user['email'], "alice@example.com")

    def test_get_user_by_id(self):
        """Test: User anhand ID abrufen"""
        user_id = self.um.create_user("alice", "alice@example.com", "hash123")
        user = self.um.get_user_by_id(user_id)
        self.assertIsNotNone(user)
        self.assertEqual(user['id'], user_id)

    def test_update_password(self):
        """Test: Passwort aktualisieren"""
        user_id = self.um.create_user("alice", "alice@example.com", "hash123")
        result = self.um.update_password(user_id, "newhash456")
        self.assertTrue(result)
        user = self.um.get_user_by_id(user_id)
        self.assertEqual(user['password_hash'], "newhash456")

    def test_delete_user(self):
        """Test: User löschen"""
        user_id = self.um.create_user("alice", "alice@example.com", "hash123")
        result = self.um.delete_user(user_id)
        self.assertTrue(result)
        user = self.um.get_user_by_id(user_id)
        self.assertIsNone(user)


class TestTokenManager(unittest.TestCase):

    def setUp(self):
        """Setup - Erstelle Token Manager"""
        self.tm = TokenManager(secret_key='test-secret', expiration_minutes=1)

    def test_create_token(self):
        """Test: Token erstellen"""
        token = self.tm.create_token(1, "alice")
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)

    def test_validate_token(self):
        """Test: Token validieren"""
        token = self.tm.create_token(1, "alice")
        payload = self.tm.validate_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload['user_id'], 1)
        self.assertEqual(payload['username'], "alice")

    def test_validate_invalid_token(self):
        """Test: Ungültigen Token validieren"""
        payload = self.tm.validate_token("invalid-token")
        self.assertIsNone(payload)

    def test_validate_expired_token(self):
        """Test: Abgelaufenen Token validieren"""
        # Erstelle Token Manager mit sehr kurzer Ablaufzeit
        tm_short = TokenManager(secret_key='test-secret', expiration_minutes=0)
        token = tm_short.create_token(1, "alice")

        # Warte kurz
        time.sleep(1)

        # Token sollte abgelaufen sein
        payload = tm_short.validate_token(token)
        self.assertIsNone(payload)

    def test_get_user_id_from_token(self):
        """Test: User-ID aus Token extrahieren"""
        token = self.tm.create_token(1, "alice")
        user_id = self.tm.get_user_id_from_token(token)
        self.assertEqual(user_id, 1)

    def test_get_username_from_token(self):
        """Test: Username aus Token extrahieren"""
        token = self.tm.create_token(1, "alice")
        username = self.tm.get_username_from_token(token)
        self.assertEqual(username, "alice")

    def test_generate_access_token(self):
        """Test: Access Token generieren"""
        token = self.tm.generate_access_token(1)
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)
        # Validiere dass Token gültig ist
        payload = self.tm.validate_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload['user_id'], 1)

    def test_generate_access_token_validate(self):
        """Test: Access Token generieren und validieren"""
        token = self.tm.generate_access_token(42)
        payload = self.tm.validate_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload['user_id'], 42)

    def test_revoke_token(self):
        """Test: Token widerrufen"""
        token = self.tm.create_token(1, "alice")
        result = self.tm.revoke_token(token)
        self.assertTrue(result)

    def test_revoke_invalid_token(self):
        """Test: Ungültigen Token widerrufen"""
        result = self.tm.revoke_token("invalid-token")
        self.assertFalse(result)

    def test_get_user_id_from_invalid_token(self):
        """Test: User-ID aus ungültigem Token extrahieren"""
        user_id = self.tm.get_user_id_from_token("invalid-token")
        self.assertIsNone(user_id)

    def test_get_username_from_invalid_token(self):
        """Test: Username aus ungültigem Token extrahieren"""
        username = self.tm.get_username_from_token("invalid-token")
        self.assertIsNone(username)

    def test_get_user_id_from_access_token(self):
        """Test: User-ID aus Access Token extrahieren"""
        token = self.tm.generate_access_token(123)
        user_id = self.tm.get_user_id_from_token(token)
        self.assertEqual(user_id, 123)


class TestAuthService(unittest.TestCase):

    def setUp(self):
        """Setup - Erstelle Auth Service"""
        self.um = UserManager(':memory:')
        self.um.connect()
        self.um.create_table()
        self.tm = TokenManager(secret_key='test-secret')
        self.auth = AuthService(self.um, self.tm)

    def tearDown(self):
        """Cleanup - Schließe Datenbankverbindung"""
        self.um.close()

    def test_hash_password(self):
        """Test: Passwort hashen"""
        hash1 = self.auth.hash_password("password")
        hash2 = self.auth.hash_password("password")
        self.assertEqual(hash1, hash2)  # Gleiche Passwörter sollten gleichen Hash haben

    def test_register_success(self):
        """Test: Erfolgreiche Registrierung"""
        success, message, user_id = self.auth.register("alice", "alice@example.com", "password123")
        self.assertTrue(success)
        self.assertIsNotNone(user_id)

    def test_register_short_username(self):
        """Test: Registrierung mit zu kurzem Username"""
        success, message, user_id = self.auth.register("al", "alice@example.com", "password123")
        self.assertFalse(success)
        self.assertIn("Username", message)

    def test_register_invalid_email(self):
        """Test: Registrierung mit ungültiger Email"""
        success, message, user_id = self.auth.register("alice", "invalid-email", "password123")
        self.assertFalse(success)
        self.assertIn("Email", message)

    def test_register_short_password(self):
        """Test: Registrierung mit zu kurzem Passwort"""
        success, message, user_id = self.auth.register("alice", "alice@example.com", "pass")
        self.assertFalse(success)
        self.assertIn("Passwort", message)

    def test_register_duplicate_username(self):
        """Test: Registrierung mit bereits vergebenem Username"""
        self.auth.register("alice", "alice@example.com", "password123")
        success, message, user_id = self.auth.register("alice", "different@example.com", "password456")
        self.assertFalse(success)
        self.assertIn("Username", message)

    def test_register_duplicate_email(self):
        """Test: Registrierung mit bereits vergebener Email"""
        self.auth.register("alice", "alice@example.com", "password123")
        success, message, user_id = self.auth.register("bob", "alice@example.com", "password456")
        self.assertFalse(success)
        self.assertIn("Email", message)

    def test_login_success(self):
        """Test: Erfolgreicher Login"""
        self.auth.register("alice", "alice@example.com", "password123")
        success, message, token = self.auth.login("alice", "password123")
        self.assertTrue(success)
        self.assertIsNotNone(token)

    def test_login_wrong_password(self):
        """Test: Login mit falschem Passwort"""
        self.auth.register("alice", "alice@example.com", "password123")
        success, message, token = self.auth.login("alice", "wrongpassword")
        self.assertFalse(success)
        self.assertIsNone(token)

    def test_login_nonexistent_user(self):
        """Test: Login mit nicht-existierendem User"""
        success, message, token = self.auth.login("nonexistent", "password123")
        self.assertFalse(success)
        self.assertIsNone(token)

    def test_validate_token_valid(self):
        """Test: Gültigen Token validieren"""
        self.auth.register("alice", "alice@example.com", "password123")
        _, _, token = self.auth.login("alice", "password123")
        valid, message, payload = self.auth.validate_token(token)
        self.assertTrue(valid)
        self.assertIsNotNone(payload)

    def test_validate_token_invalid(self):
        """Test: Ungültigen Token validieren"""
        valid, message, payload = self.auth.validate_token("invalid-token")
        self.assertFalse(valid)
        self.assertIsNone(payload)

    def test_get_user_from_token(self):
        """Test: User aus Token abrufen"""
        self.auth.register("alice", "alice@example.com", "password123")
        _, _, token = self.auth.login("alice", "password123")
        user = self.auth.get_user_from_token(token)
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], "alice")

    def test_get_user_from_invalid_token(self):
        """Test: User aus ungültigem Token abrufen"""
        user = self.auth.get_user_from_token("invalid-token")
        self.assertIsNone(user)

    def test_register_empty_username(self):
        """Test: Registrierung mit leerem Username"""
        success, message, user_id = self.auth.register("", "alice@example.com", "password123")
        self.assertFalse(success)
        self.assertIn("Username", message)

    def test_register_empty_email(self):
        """Test: Registrierung mit leerer Email"""
        success, message, user_id = self.auth.register("alice", "", "password123")
        self.assertFalse(success)
        self.assertIn("Email", message)

    def test_register_empty_password(self):
        """Test: Registrierung mit leerem Passwort"""
        success, message, user_id = self.auth.register("alice", "alice@example.com", "")
        self.assertFalse(success)
        self.assertIn("Passwort", message)

    def test_hash_password_consistency(self):
        """Test: Passwort-Hash Konsistenz"""
        hash1 = self.auth.hash_password("test123")
        hash2 = self.auth.hash_password("test123")
        self.assertEqual(hash1, hash2)

    def test_hash_password_different(self):
        """Test: Verschiedene Passwörter ergeben verschiedene Hashes"""
        hash1 = self.auth.hash_password("password1")
        hash2 = self.auth.hash_password("password2")
        self.assertNotEqual(hash1, hash2)


if __name__ == '__main__':
    unittest.main()

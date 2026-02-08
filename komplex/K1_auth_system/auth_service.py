"""
Authentication Service - Verwaltet Registration und Login
"""

import hashlib
from typing import Optional, Dict, Tuple
from user_manager import UserManager
from token_manager import TokenManager


class AuthService:
    """
    Authentication Service - Verwaltet User-Registration und Login
    """

    def __init__(self, user_manager: UserManager, token_manager: TokenManager):
        """
        Initialisiert den Auth Service.

        Args:
            user_manager (UserManager): User Manager Instanz
            token_manager (TokenManager): Token Manager Instanz
        """
        self.user_manager = user_manager
        self.token_manager = token_manager

    def hash_password(self, password: str) -> str:
        """
        Hasht ein Passwort mit SHA-256.

        Args:
            password (str): Klartext-Passwort

        Returns:
            str: Gehashtes Passwort
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username: str, email: str, password: str) -> Tuple[bool, str, Optional[int]]:
        """
        Registriert einen neuen User.

        Args:
            username (str): Benutzername
            email (str): Email
            password (str): Passwort

        Returns:
            Tuple[bool, str, Optional[int]]: (Erfolg, Nachricht, User-ID)
        """
        # Validierung
        if not username or len(username) < 3:
            return False, "Username muss mindestens 3 Zeichen lang sein", None

        if not email or '@' not in email:
            return False, "Ungültige Email-Adresse", None

        if not password or len(password) < 6:
            return False, "Passwort muss mindestens 6 Zeichen lang sein", None

        # Prüfe ob Username oder Email bereits existieren
        if self.user_manager.get_user_by_username(username):
            return False, "Username bereits vergeben", None

        if self.user_manager.get_user_by_email(email):
            return False, "Email bereits vergeben", None

        # Passwort hashen
        password_hash = self.hash_password(password)

        # User erstellen
        try:
            user_id = self.user_manager.create_user(username, email, password_hash)
            return True, "Registrierung erfolgreich", user_id
        except ValueError as e:
            return False, str(e), None

    def login(self, username: str, password: str) -> Tuple[bool, str, Optional[str]]:
        """
        Loggt einen User ein.

        Args:
            username (str): Benutzername
            password (str): Passwort

        Returns:
            Tuple[bool, str, Optional[str]]: (Erfolg, Nachricht, JWT Token)
        """
        # User abrufen
        user = self.user_manager.get_user_by_username(username)

        if not user:
            return False, "Ungültiger Username oder Passwort", None

        # Passwort prüfen
        if not self.user_manager.verify_password(user, password):
            return False, "Ungültiger Username oder Passwort", None

        # JWT Token erstellen
        token = self.token_manager.generate_access_token(user['id'])

        return True, "Login erfolgreich", token

    def validate_token(self, token: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Validiert einen JWT Token.

        Args:
            token (str): JWT Token

        Returns:
            Tuple[bool, str, Optional[Dict]]: (Gültig, Nachricht, Token-Payload)
        """
        payload = self.token_manager.validate_token(token)

        if payload:
            return True, "Token gültig", payload
        else:
            return False, "Token ungültig oder abgelaufen", None

    def get_user_from_token(self, token: str) -> Optional[Dict]:
        """
        Ruft User-Daten anhand eines Tokens ab.

        Args:
            token (str): JWT Token

        Returns:
            Optional[Dict]: User-Daten oder None
        """
        user_id = self.token_manager.get_user_id_from_token(token)

        if user_id:
            return self.user_manager.get_user_by_id(user_id)

        return None


if __name__ == "__main__":
    # Beispiel-Verwendung
    user_manager = UserManager()
    user_manager.connect()
    user_manager.create_table()

    token_manager = TokenManager()
    auth_service = AuthService(user_manager, token_manager)

    # Registrierung
    success, message, user_id = auth_service.register("alice", "alice@example.com", "password123")
    print(f"Registrierung: {message} (User ID: {user_id})")

    # Login
    success, message, token = auth_service.login("alice", "password123")
    print(f"Login: {message}")
    print(f"Token: {token}")

    # Token validieren
    valid, message, payload = auth_service.validate_token(token)
    print(f"Token-Validierung: {message} (Payload: {payload})")

    # User aus Token abrufen
    user = auth_service.get_user_from_token(token)
    print(f"User aus Token: {user}")

    user_manager.close()

"""
Token Manager - Erstellt und validiert JWT Tokens
"""

import jwt
import datetime
from typing import Optional, Dict


class TokenManager:
    """
    Token Manager - Verwaltet JWT Token-Erstellung und -Validierung
    """

    JWT_ALGORITHM = "HS256"

    def __init__(self, secret_key: str = "my-super-secret-key-12345", expiration_minutes: int = 60):
        """
        Initialisiert den Token Manager.

        Args:
            secret_key (str): Secret Key für JWT-Signierung
            expiration_minutes (int): Token-Ablaufzeit in Minuten
        """
        self.secret_key = secret_key
        self.expiration_minutes = expiration_minutes
        # Für Backward-Kompatibilität
        self.secret_key = secret_key

    def create_token(self, user_id: int, username: str) -> str:
        """
        Erstellt einen JWT Token für einen User.

        Args:
            user_id (int): User-ID
            username (str): Username

        Returns:
            str: JWT Token
        """
        payload = {
            'user_id': user_id,
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=self.expiration_minutes),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.JWT_ALGORITHM)
        return token

    def generate_access_token(self, user_id: int) -> str:
        """
        Erstellt einen JWT Access Token für einen User.

        Args:
            user_id (int): User-ID

        Returns:
            str: JWT Token
        """
        payload = {
            'user_id': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=self.expiration_minutes),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.JWT_ALGORITHM)
        return token

    def validate_token(self, token: str) -> Optional[Dict]:
        """
        Validiert einen JWT Token.

        Args:
            token (str): JWT Token

        Returns:
            Optional[Dict]: Token-Payload wenn gültig, sonst None
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            # Token ist abgelaufen
            return None
        except jwt.InvalidTokenError:
            # Token ist ungültig
            return None

    def revoke_token(self, token: str) -> bool:
        """
        Widerruft einen Token (Placeholder für Token-Revocation).

        Args:
            token (str): JWT Token

        Returns:
            bool: True wenn erfolgreich widerrufen
        """
        # In einer echten Implementierung würde hier eine Blacklist verwendet
        # Für die Baseline ist dies ein Placeholder
        payload = self.validate_token(token)
        return payload is not None

    def get_user_id_from_token(self, token: str) -> Optional[int]:
        """
        Extrahiert die User-ID aus einem Token.

        Args:
            token (str): JWT Token

        Returns:
            Optional[int]: User-ID wenn Token gültig, sonst None
        """
        payload = self.validate_token(token)
        if payload:
            return payload.get('user_id')
        return None

    def get_username_from_token(self, token: str) -> Optional[str]:
        """
        Extrahiert den Username aus einem Token.

        Args:
            token (str): JWT Token

        Returns:
            Optional[str]: Username wenn Token gültig, sonst None
        """
        payload = self.validate_token(token)
        if payload:
            return payload.get('username')
        return None


if __name__ == "__main__":
    # Beispiel-Verwendung
    tm = TokenManager()

    # Token erstellen
    token = tm.generate_access_token(1)
    print(f"Token erstellt: {token}")

    # Token validieren
    payload = tm.validate_token(token)
    print(f"Token-Payload: {payload}")

    # User-ID extrahieren
    user_id = tm.get_user_id_from_token(token)
    print(f"User-ID: {user_id}")

    # Ungültigen Token testen
    invalid_payload = tm.validate_token("invalid-token")
    print(f"Ungültiger Token: {invalid_payload}")

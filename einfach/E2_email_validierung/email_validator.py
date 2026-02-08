"""
Email-Validierung - Prüft ob ein String eine gültige Email-Adresse ist
"""

import re


def validate_email(email):
    """
    Validiert eine Email-Adresse.

    Eine gültige Email hat das Format: username@domain.extension

    Args:
        email (str): Die zu prüfende Email-Adresse

    Returns:
        bool: True wenn gültige Email, sonst False
    """
    if not isinstance(email, str):
        return False

    # Regex-Muster für Email-Validierung
    # Format: username@domain.extension
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    return bool(re.match(pattern, email))


if __name__ == "__main__":
    # Beispiel-Verwendung
    test_emails = [
        "user@example.com",
        "test.email@domain.co.uk",
        "invalid.email",
        "@domain.com",
        "user@",
        "user@domain",
        ""
    ]

    for email in test_emails:
        result = validate_email(email)
        print(f"{email:30} -> {result}")

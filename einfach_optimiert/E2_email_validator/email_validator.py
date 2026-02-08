"""
Email Validator Module

Provides a robust email validation function with comprehensive edge case handling.
"""

import re
from typing import Optional


def validate_email(email: Optional[str]) -> bool:
    """
    Validates an email address according to common email format rules.

    Args:
        email: The email address to validate (can be None)

    Returns:
        True if the email is valid, False otherwise

    Edge Cases Handled:
        - None inputs
        - Empty strings
        - Whitespace-only strings
        - Overlength inputs (>254 characters per RFC 5321)
        - Leading/trailing whitespace
        - Local-part max 64 characters
        - Domain max 253 characters
        - Multiple @ symbols
        - Missing local-part or domain
        - Invalid domain format
    """
    # Handle None input
    if email is None:
        return False

    # Handle non-string inputs
    if not isinstance(email, str):
        return False

    # Handle empty or whitespace-only strings
    if not email or not email.strip():
        return False

    # Strip leading/trailing whitespace for validation
    email = email.strip()

    # Check total length (RFC 5321: max 254 characters)
    if len(email) > 254:
        return False

    # Check for exactly one @ symbol
    if email.count('@') != 1:
        return False

    # Split into local-part and domain
    try:
        local_part, domain = email.split('@')
    except ValueError:
        return False

    # Validate local-part
    if not local_part or len(local_part) > 64:
        return False

    # Validate domain
    if not domain or len(domain) > 253:
        return False

    # Domain must contain at least one dot
    if '.' not in domain:
        return False

    # Domain must not start or end with a dot
    if domain.startswith('.') or domain.endswith('.'):
        return False

    # Check for consecutive dots in domain
    if '..' in domain:
        return False

    # Validate local-part characters (alphanumeric, dots, underscores, percent, plus, minus)
    # Allow dots, but not at the beginning or end
    if local_part.startswith('.') or local_part.endswith('.'):
        return False

    if '..' in local_part:
        return False

    # Allowed characters in local-part
    local_part_pattern = r'^[a-zA-Z0-9._%+\-]+$'
    if not re.match(local_part_pattern, local_part):
        return False

    # Validate domain format (alphanumeric, dots, hyphens)
    # Each label (between dots) must not start or end with hyphen
    # Each label must be max 63 characters (RFC 1035)
    domain_labels = domain.split('.')

    for label in domain_labels:
        if not label:  # Empty label (consecutive dots)
            return False

        if len(label) > 63:  # RFC 1035: label max 63 octets
            return False

        if label.startswith('-') or label.endswith('-'):
            return False

        # Label must contain only alphanumeric and hyphens
        if not re.match(r'^[a-zA-Z0-9\-]+$', label):
            return False

    # TLD (last label) must be at least 2 characters and only letters
    tld = domain_labels[-1]
    if len(tld) < 2:
        return False

    if not re.match(r'^[a-zA-Z]+$', tld):
        return False

    return True

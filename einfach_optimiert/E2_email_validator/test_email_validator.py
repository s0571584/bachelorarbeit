"""
Unit Tests for Email Validator

Comprehensive test suite covering all edge cases and validation scenarios.
"""

import pytest
from email_validator import validate_email


class TestValidEmails:
    """Test cases for valid email addresses"""

    def test_simple_email(self):
        """Test a simple valid email"""
        assert validate_email("user@example.com") is True

    def test_email_with_subdomain(self):
        """Test email with subdomain"""
        assert validate_email("user@mail.example.com") is True

    def test_email_with_multiple_subdomains(self):
        """Test email with multiple subdomains"""
        assert validate_email("user@sub.mail.example.com") is True

    def test_email_with_plus_sign(self):
        """Test email with plus sign in local-part"""
        assert validate_email("user+tag@example.com") is True

    def test_email_with_underscore(self):
        """Test email with underscore in local-part"""
        assert validate_email("user_name@example.com") is True

    def test_email_with_dot_in_local(self):
        """Test email with dot in local-part"""
        assert validate_email("first.last@example.com") is True

    def test_email_with_percent(self):
        """Test email with percent sign in local-part"""
        assert validate_email("user%test@example.com") is True

    def test_email_with_hyphen_in_domain(self):
        """Test email with hyphen in domain"""
        assert validate_email("user@ex-ample.com") is True

    def test_email_with_numbers(self):
        """Test email with numbers"""
        assert validate_email("user123@example123.com") is True

    def test_international_tld(self):
        """Test email with international TLD"""
        assert validate_email("user@domain.berlin") is True

    def test_long_tld(self):
        """Test email with long TLD"""
        assert validate_email("user@example.technology") is True


class TestInvalidEmails:
    """Test cases for invalid email addresses"""

    def test_missing_at_symbol(self):
        """Test email without @ symbol"""
        assert validate_email("userexample.com") is False

    def test_multiple_at_symbols(self):
        """Test email with multiple @ symbols"""
        assert validate_email("user@@example.com") is False
        assert validate_email("user@domain@com") is False

    def test_missing_local_part(self):
        """Test email with missing local-part"""
        assert validate_email("@example.com") is False

    def test_missing_domain(self):
        """Test email with missing domain"""
        assert validate_email("user@") is False

    def test_missing_dot_in_domain(self):
        """Test email without dot in domain"""
        assert validate_email("user@domaincom") is False

    def test_domain_starts_with_dot(self):
        """Test email with domain starting with dot"""
        assert validate_email("user@.example.com") is False

    def test_domain_ends_with_dot(self):
        """Test email with domain ending with dot"""
        assert validate_email("user@example.com.") is False

    def test_consecutive_dots_in_domain(self):
        """Test email with consecutive dots in domain"""
        assert validate_email("user@example..com") is False

    def test_consecutive_dots_in_local(self):
        """Test email with consecutive dots in local-part"""
        assert validate_email("user..name@example.com") is False

    def test_local_part_starts_with_dot(self):
        """Test email with local-part starting with dot"""
        assert validate_email(".user@example.com") is False

    def test_local_part_ends_with_dot(self):
        """Test email with local-part ending with dot"""
        assert validate_email("user.@example.com") is False

    def test_invalid_characters_in_local(self):
        """Test email with invalid characters in local-part"""
        assert validate_email("user#name@example.com") is False
        assert validate_email("user$name@example.com") is False
        assert validate_email("user name@example.com") is False

    def test_domain_with_invalid_characters(self):
        """Test email with invalid characters in domain"""
        assert validate_email("user@exam ple.com") is False
        assert validate_email("user@exam_ple.com") is False

    def test_tld_too_short(self):
        """Test email with TLD less than 2 characters"""
        assert validate_email("user@example.c") is False

    def test_tld_with_numbers(self):
        """Test email with numbers in TLD"""
        assert validate_email("user@example.c0m") is False


class TestEdgeCases:
    """Test cases for edge cases and robustness"""

    def test_none_input(self):
        """Test None input returns False without exception"""
        assert validate_email(None) is False

    def test_empty_string(self):
        """Test empty string returns False"""
        assert validate_email("") is False

    def test_whitespace_only(self):
        """Test whitespace-only string returns False"""
        assert validate_email("   ") is False
        assert validate_email("\t") is False
        assert validate_email("\n") is False

    def test_only_at_symbol(self):
        """Test only @ symbol returns False"""
        assert validate_email("@") is False

    def test_leading_whitespace(self):
        """Test email with leading whitespace is valid after strip"""
        assert validate_email("  user@example.com") is True

    def test_trailing_whitespace(self):
        """Test email with trailing whitespace is valid after strip"""
        assert validate_email("user@example.com  ") is True

    def test_both_leading_and_trailing_whitespace(self):
        """Test email with both leading and trailing whitespace"""
        assert validate_email("  user@example.com  ") is True

    def test_overlength_total(self):
        """Test email exceeding 254 characters (RFC 5321)"""
        local = "a" * 64
        domain = "b" * 200 + ".com"
        email = f"{local}@{domain}"
        assert len(email) > 254
        assert validate_email(email) is False

    def test_local_part_too_long(self):
        """Test local-part exceeding 64 characters"""
        local = "a" * 65
        email = f"{local}@example.com"
        assert validate_email(email) is False

    def test_local_part_max_length(self):
        """Test local-part at exactly 64 characters (valid)"""
        local = "a" * 64
        email = f"{local}@example.com"
        assert validate_email(email) is True

    def test_domain_too_long(self):
        """Test domain exceeding 253 characters"""
        domain = "a" * 250 + ".com"
        email = f"user@{domain}"
        assert len(domain) > 253
        assert validate_email(email) is False

    def test_domain_max_length(self):
        """Test domain that keeps total email at 254 characters (RFC 5321 max)"""
        # RFC 5321: total email max 254 chars
        # Use local-part "u" (1 char) + "@" (1 char) + domain (252 chars) = 254 total
        # Domain with 252 chars using multiple labels (each max 63)
        # 62 + 1 + 62 + 1 + 62 + 1 + 60 + 1 + 2 = 252
        parts = ["a" * 62, "b" * 62, "c" * 62, "d" * 60, "co"]
        domain = ".".join(parts)
        email = f"u@{domain}"
        assert len(email) == 254  # RFC 5321 maximum
        assert len(domain) == 252
        assert validate_email(email) is True

    def test_non_string_input(self):
        """Test non-string inputs return False"""
        assert validate_email(123) is False
        assert validate_email(['user@example.com']) is False
        assert validate_email({'email': 'user@example.com'}) is False


class TestParameterizedCases:
    """Parametrized tests for multiple similar cases"""

    @pytest.mark.parametrize("email", [
        "simple@example.com",
        "very.common@example.com",
        "disposable.style.email.with+symbol@example.com",
        "other.email-with-hyphen@example.com",
        "x@example.com",
        "example@s.example",
    ])
    def test_valid_emails_parametrized(self, email):
        """Test multiple valid email formats"""
        assert validate_email(email) is True

    @pytest.mark.parametrize("email", [
        "plainaddress",
        "@no-local.org",
        "no-domain@",
        "two@@example.com",
        "dotdot..@example.com",
        ".leadingdot@example.com",
        "trailingdot.@example.com",
        "no-tld@domain",
        "invalid spaces@example.com",
        "user@domain..com",
        "",
        "   ",
    ])
    def test_invalid_emails_parametrized(self, email):
        """Test multiple invalid email formats"""
        assert validate_email(email) is False

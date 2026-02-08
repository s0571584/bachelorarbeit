"""
Unit Tests für email_validator.py
"""

import unittest
from email_validator import validate_email


class TestValidateEmail(unittest.TestCase):

    def test_valid_simple_email(self):
        """Test mit einfacher gültiger Email"""
        self.assertTrue(validate_email("user@example.com"))

    def test_valid_email_with_dots(self):
        """Test mit Punkten im Username"""
        self.assertTrue(validate_email("first.last@example.com"))

    def test_valid_email_with_plus(self):
        """Test mit Plus im Username"""
        self.assertTrue(validate_email("user+tag@example.com"))

    def test_valid_email_with_numbers(self):
        """Test mit Zahlen"""
        self.assertTrue(validate_email("user123@example456.com"))

    def test_valid_email_subdomain(self):
        """Test mit Subdomain"""
        self.assertTrue(validate_email("user@mail.example.com"))

    def test_valid_email_long_extension(self):
        """Test mit langer Extension"""
        self.assertTrue(validate_email("user@example.info"))

    def test_invalid_no_at_sign(self):
        """Test ohne @-Zeichen"""
        self.assertFalse(validate_email("userexample.com"))

    def test_invalid_no_domain(self):
        """Test ohne Domain"""
        self.assertFalse(validate_email("user@"))

    def test_invalid_no_extension(self):
        """Test ohne Extension"""
        self.assertFalse(validate_email("user@domain"))

    def test_invalid_no_username(self):
        """Test ohne Username"""
        self.assertFalse(validate_email("@domain.com"))

    def test_invalid_empty_string(self):
        """Test mit leerem String"""
        self.assertFalse(validate_email(""))

    def test_invalid_multiple_at_signs(self):
        """Test mit mehreren @-Zeichen"""
        self.assertFalse(validate_email("user@@example.com"))

    def test_invalid_spaces(self):
        """Test mit Leerzeichen"""
        self.assertFalse(validate_email("user @example.com"))

    def test_invalid_special_chars(self):
        """Test mit ungültigen Sonderzeichen"""
        self.assertFalse(validate_email("user#name@example.com"))

    def test_invalid_type_number(self):
        """Test mit ungültigem Typ (Zahl)"""
        self.assertFalse(validate_email(12345))

    def test_invalid_type_none(self):
        """Test mit None"""
        self.assertFalse(validate_email(None))

    def test_invalid_type_list(self):
        """Test mit Liste"""
        self.assertFalse(validate_email(["user@example.com"]))


if __name__ == "__main__":
    unittest.main()

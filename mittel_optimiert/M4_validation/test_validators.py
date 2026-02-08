"""
Unit Tests for Individual Validators

Tests each validator class in isolation.
"""

import pytest
from validators import StringValidator, IntValidator, FloatValidator, BoolValidator


class TestStringValidator:
    """Tests for StringValidator"""

    def setup_method(self):
        """Setup validator instance"""
        self.validator = StringValidator()

    def test_valid_string(self):
        """Test valid string passes"""
        is_valid, error = self.validator.validate("hello", {})
        assert is_valid is True
        assert error == ""

    def test_non_string_rejected(self):
        """Test non-string value is rejected"""
        is_valid, error = self.validator.validate(123, {})
        assert is_valid is False
        assert "Expected string" in error

    def test_min_length_valid(self):
        """Test string meeting min_length constraint"""
        is_valid, error = self.validator.validate("hello", {'min_length': 3})
        assert is_valid is True

    def test_min_length_invalid(self):
        """Test string violating min_length constraint"""
        is_valid, error = self.validator.validate("hi", {'min_length': 3})
        assert is_valid is False
        assert "too short" in error.lower()

    def test_max_length_valid(self):
        """Test string meeting max_length constraint"""
        is_valid, error = self.validator.validate("hello", {'max_length': 10})
        assert is_valid is True

    def test_max_length_invalid(self):
        """Test string violating max_length constraint"""
        is_valid, error = self.validator.validate("hello world", {'max_length': 5})
        assert is_valid is False
        assert "too long" in error.lower()

    def test_pattern_valid(self):
        """Test string matching pattern"""
        is_valid, error = self.validator.validate("test123", {'pattern': r'^[a-z0-9]+$'})
        assert is_valid is True

    def test_pattern_invalid(self):
        """Test string not matching pattern"""
        is_valid, error = self.validator.validate("Test123", {'pattern': r'^[a-z0-9]+$'})
        assert is_valid is False
        assert "pattern" in error.lower()

    def test_multiple_constraints(self):
        """Test string with multiple constraints"""
        constraints = {'min_length': 3, 'max_length': 10, 'pattern': r'^[a-z]+$'}
        is_valid, error = self.validator.validate("hello", constraints)
        assert is_valid is True

    def test_empty_string_with_constraints(self):
        """Test empty string with min_length"""
        is_valid, error = self.validator.validate("", {'min_length': 1})
        assert is_valid is False


class TestIntValidator:
    """Tests for IntValidator"""

    def setup_method(self):
        """Setup validator instance"""
        self.validator = IntValidator()

    def test_valid_int(self):
        """Test valid integer passes"""
        is_valid, error = self.validator.validate(42, {})
        assert is_valid is True
        assert error == ""

    def test_non_int_rejected(self):
        """Test non-integer value is rejected"""
        is_valid, error = self.validator.validate("42", {})
        assert is_valid is False
        assert "Expected int" in error

    def test_bool_rejected(self):
        """Test that boolean is rejected (bool is subclass of int in Python)"""
        is_valid, error = self.validator.validate(True, {})
        assert is_valid is False
        assert "Expected int" in error

    def test_min_value_valid(self):
        """Test integer meeting min_value constraint"""
        is_valid, error = self.validator.validate(10, {'min_value': 5})
        assert is_valid is True

    def test_min_value_invalid(self):
        """Test integer violating min_value constraint"""
        is_valid, error = self.validator.validate(3, {'min_value': 5})
        assert is_valid is False
        assert "too small" in error.lower()

    def test_max_value_valid(self):
        """Test integer meeting max_value constraint"""
        is_valid, error = self.validator.validate(10, {'max_value': 15})
        assert is_valid is True

    def test_max_value_invalid(self):
        """Test integer violating max_value constraint"""
        is_valid, error = self.validator.validate(20, {'max_value': 15})
        assert is_valid is False
        assert "too large" in error.lower()

    def test_multiple_constraints(self):
        """Test integer with min and max constraints"""
        constraints = {'min_value': 0, 'max_value': 100}
        is_valid, error = self.validator.validate(50, constraints)
        assert is_valid is True

    def test_negative_integers(self):
        """Test negative integers are handled correctly"""
        is_valid, error = self.validator.validate(-10, {'min_value': -20})
        assert is_valid is True


class TestFloatValidator:
    """Tests for FloatValidator"""

    def setup_method(self):
        """Setup validator instance"""
        self.validator = FloatValidator()

    def test_valid_float(self):
        """Test valid float passes"""
        is_valid, error = self.validator.validate(3.14, {})
        assert is_valid is True
        assert error == ""

    def test_int_accepted(self):
        """Test that integers are accepted as floats"""
        is_valid, error = self.validator.validate(42, {})
        assert is_valid is True

    def test_non_numeric_rejected(self):
        """Test non-numeric value is rejected"""
        is_valid, error = self.validator.validate("3.14", {})
        assert is_valid is False
        assert "Expected float" in error

    def test_bool_rejected(self):
        """Test that boolean is rejected"""
        is_valid, error = self.validator.validate(True, {})
        assert is_valid is False

    def test_min_value_valid(self):
        """Test float meeting min_value constraint"""
        is_valid, error = self.validator.validate(3.5, {'min_value': 2.0})
        assert is_valid is True

    def test_min_value_invalid(self):
        """Test float violating min_value constraint"""
        is_valid, error = self.validator.validate(1.5, {'min_value': 2.0})
        assert is_valid is False
        assert "too small" in error.lower()

    def test_max_value_valid(self):
        """Test float meeting max_value constraint"""
        is_valid, error = self.validator.validate(3.5, {'max_value': 5.0})
        assert is_valid is True

    def test_max_value_invalid(self):
        """Test float violating max_value constraint"""
        is_valid, error = self.validator.validate(6.0, {'max_value': 5.0})
        assert is_valid is False
        assert "too large" in error.lower()

    def test_precision_valid(self):
        """Test float with correct precision"""
        is_valid, error = self.validator.validate(3.14, {'precision': 2})
        assert is_valid is True

    def test_precision_invalid(self):
        """Test float with too many decimal places"""
        is_valid, error = self.validator.validate(3.14159, {'precision': 2})
        assert is_valid is False
        assert "decimal places" in error.lower()

    def test_multiple_constraints(self):
        """Test float with multiple constraints"""
        constraints = {'min_value': 0.0, 'max_value': 10.0, 'precision': 2}
        is_valid, error = self.validator.validate(5.25, constraints)
        assert is_valid is True


class TestBoolValidator:
    """Tests for BoolValidator"""

    def setup_method(self):
        """Setup validator instance"""
        self.validator = BoolValidator()

    def test_true_valid(self):
        """Test True is valid"""
        is_valid, error = self.validator.validate(True, {})
        assert is_valid is True
        assert error == ""

    def test_false_valid(self):
        """Test False is valid"""
        is_valid, error = self.validator.validate(False, {})
        assert is_valid is True
        assert error == ""

    def test_non_bool_rejected(self):
        """Test non-boolean value is rejected"""
        is_valid, error = self.validator.validate(1, {})
        assert is_valid is False
        assert "Expected bool" in error

    def test_string_bool_rejected(self):
        """Test string 'true'/'false' is rejected"""
        is_valid, error = self.validator.validate("true", {})
        assert is_valid is False

    def test_constraints_ignored(self):
        """Test that constraints are ignored for booleans"""
        # Booleans don't have constraints, but shouldn't error if provided
        is_valid, error = self.validator.validate(True, {'some_constraint': 'value'})
        assert is_valid is True

"""
Type Validators for Data Validation Framework

Uses Strategy Pattern to separate type-specific validation logic.
Each validator handles one data type with low complexity (max CC 10).
"""

import re
from typing import Any, Tuple, Protocol


class TypeValidator(Protocol):
    """Protocol for all type validators"""

    def validate(self, value: Any, constraints: dict) -> Tuple[bool, str]:
        """
        Validate a value against type-specific constraints.

        Args:
            value: The value to validate
            constraints: Dict of constraint name -> constraint value

        Returns:
            Tuple of (is_valid: bool, error_message: str)
            If valid, error_message is empty string
        """
        ...


class StringValidator:
    """
    Validates string values.

    Supported constraints:
        - min_length: Minimum string length
        - max_length: Maximum string length
        - pattern: Regex pattern to match
    """

    def validate(self, value: Any, constraints: dict) -> Tuple[bool, str]:
        """Validate string value (max 15 lines, CC < 10)"""
        if not isinstance(value, str):
            return False, f"Expected string, got {type(value).__name__}"

        if 'min_length' in constraints:
            if len(value) < constraints['min_length']:
                return False, f"String too short (min: {constraints['min_length']})"

        if 'max_length' in constraints:
            if len(value) > constraints['max_length']:
                return False, f"String too long (max: {constraints['max_length']})"

        if 'pattern' in constraints:
            if not re.match(constraints['pattern'], value):
                return False, "String does not match pattern"

        return True, ""


class IntValidator:
    """
    Validates integer values.

    Supported constraints:
        - min_value: Minimum integer value
        - max_value: Maximum integer value
    """

    def validate(self, value: Any, constraints: dict) -> Tuple[bool, str]:
        """Validate integer value (max 15 lines, CC < 10)"""
        # Note: bool is subclass of int in Python, so exclude it explicitly
        if not isinstance(value, int) or isinstance(value, bool):
            return False, f"Expected int, got {type(value).__name__}"

        if 'min_value' in constraints:
            if value < constraints['min_value']:
                return False, f"Value too small (min: {constraints['min_value']})"

        if 'max_value' in constraints:
            if value > constraints['max_value']:
                return False, f"Value too large (max: {constraints['max_value']})"

        return True, ""


class FloatValidator:
    """
    Validates float values.

    Supported constraints:
        - min_value: Minimum float value
        - max_value: Maximum float value
        - precision: Number of decimal places (rounded for comparison)
    """

    def validate(self, value: Any, constraints: dict) -> Tuple[bool, str]:
        """Validate float value (max 20 lines, CC < 10)"""
        # Accept both float and int (int can be promoted to float)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return False, f"Expected float, got {type(value).__name__}"

        # Convert to float for validation
        float_value = float(value)

        if 'min_value' in constraints:
            if float_value < constraints['min_value']:
                return False, f"Value too small (min: {constraints['min_value']})"

        if 'max_value' in constraints:
            if float_value > constraints['max_value']:
                return False, f"Value too large (max: {constraints['max_value']})"

        if 'precision' in constraints:
            precision = constraints['precision']
            # Check decimal places
            rounded = round(float_value, precision)
            if abs(float_value - rounded) > 1e-10:  # Floating point tolerance
                return False, f"Too many decimal places (max: {precision})"

        return True, ""


class BoolValidator:
    """
    Validates boolean values.

    No additional constraints supported for booleans.
    """

    def validate(self, value: Any, constraints: dict) -> Tuple[bool, str]:
        """Validate boolean value (max 10 lines, CC < 5)"""
        if not isinstance(value, bool):
            return False, f"Expected bool, got {type(value).__name__}"
        return True, ""

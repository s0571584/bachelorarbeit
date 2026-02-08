"""
Data Validation Framework

Schema-based validation using Strategy Pattern for extensibility.
Low complexity design with each method under CC 10.
"""

from typing import Dict, List, Tuple, Any
from validators import StringValidator, IntValidator, FloatValidator, BoolValidator


class ValidationFramework:
    """
    Main validation framework for schema-based data validation.

    Uses Strategy Pattern: Different validator classes handle different types.
    Follows Open-Closed Principle: Easy to add new validators via register_validator().
    """

    def __init__(self):
        """Initialize framework with built-in validators"""
        self.validators = {
            'string': StringValidator(),
            'int': IntValidator(),
            'float': FloatValidator(),
            'bool': BoolValidator(),
        }

    def validate(self, data: Dict[str, Any], schema: Dict[str, dict]) -> Tuple[bool, List[str]]:
        """
        Validate data against schema.

        Schema format:
        {
            'field_name': {
                'type': 'string',      # string, int, float, bool
                'required': True,       # True or False (default: False)
                'constraints': {        # Optional, type-specific
                    'min_length': 1,
                    'max_length': 100,
                    ...
                }
            }
        }

        Args:
            data: Dictionary of field_name -> value to validate
            schema: Dictionary of field_name -> field_schema

        Returns:
            Tuple of (is_valid: bool, errors: List[str])
            errors is empty list if valid

        Complexity: CC < 10 through helper methods
        """
        errors = []

        # Check required fields
        errors.extend(self._check_required_fields(data, schema))

        # Validate present fields
        errors.extend(self._validate_fields(data, schema))

        return len(errors) == 0, errors

    def _check_required_fields(self, data: Dict[str, Any], schema: Dict[str, dict]) -> List[str]:
        """
        Check that all required fields are present.

        Args:
            data: Data dictionary
            schema: Schema dictionary

        Returns:
            List of error messages (empty if all required fields present)

        Complexity: CC 3 (simple loop with one if)
        """
        errors = []
        for field_name, field_schema in schema.items():
            if field_schema.get('required', False) and field_name not in data:
                errors.append(f"Missing required field: {field_name}")
        return errors

    def _validate_fields(self, data: Dict[str, Any], schema: Dict[str, dict]) -> List[str]:
        """
        Validate all present fields against schema.

        Args:
            data: Data dictionary
            schema: Schema dictionary

        Returns:
            List of error messages (empty if all fields valid)

        Complexity: CC 5 (loop + 3 ifs)
        """
        errors = []
        for field_name, value in data.items():
            # Skip fields not in schema
            if field_name not in schema:
                continue

            # Validate field
            field_errors = self._validate_single_field(field_name, value, schema[field_name])
            errors.extend(field_errors)

        return errors

    def _validate_single_field(
        self,
        field_name: str,
        value: Any,
        field_schema: dict
    ) -> List[str]:
        """
        Validate a single field against its schema.

        Args:
            field_name: Name of field (for error messages)
            value: Value to validate
            field_schema: Schema for this field

        Returns:
            List of error messages (empty if valid)

        Complexity: CC 4 (3 ifs)
        """
        errors = []

        field_type = field_schema.get('type', 'string')
        constraints = field_schema.get('constraints', {})

        # Check if we have a validator for this type
        if field_type not in self.validators:
            errors.append(f"Unknown type '{field_type}' for field '{field_name}'")
            return errors

        # Delegate to appropriate validator (Strategy Pattern)
        validator = self.validators[field_type]
        is_valid, error_msg = validator.validate(value, constraints)

        if not is_valid:
            errors.append(f"Field '{field_name}': {error_msg}")

        return errors

    def register_validator(self, type_name: str, validator) -> None:
        """
        Register a new type validator (Open-Closed Principle).

        Allows extending the framework with new types without modifying existing code.

        Args:
            type_name: Name of the type (e.g., 'email', 'url')
            validator: Validator instance implementing TypeValidator protocol

        Example:
            framework = ValidationFramework()
            framework.register_validator('email', EmailValidator())

        Complexity: CC 1 (no branches)
        """
        self.validators[type_name] = validator

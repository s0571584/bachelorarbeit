"""
Unit Tests for ValidationFramework

Tests the framework with complex schemas and integration scenarios.
"""

import pytest
from framework import ValidationFramework


class TestBasicValidation:
    """Tests for basic framework validation"""

    def setup_method(self):
        """Setup framework instance"""
        self.framework = ValidationFramework()

    def test_empty_schema_empty_data(self):
        """Test validation with empty schema and data"""
        is_valid, errors = self.framework.validate({}, {})
        assert is_valid is True
        assert errors == []

    def test_single_required_field_present(self):
        """Test validation with required field present"""
        schema = {'name': {'type': 'string', 'required': True}}
        data = {'name': 'Alice'}
        is_valid, errors = self.framework.validate(data, schema)
        assert is_valid is True
        assert errors == []

    def test_single_required_field_missing(self):
        """Test validation with required field missing"""
        schema = {'name': {'type': 'string', 'required': True}}
        data = {}
        is_valid, errors = self.framework.validate(data, schema)
        assert is_valid is False
        assert len(errors) == 1
        assert "Missing required field: name" in errors[0]

    def test_optional_field_missing(self):
        """Test validation with optional field missing (should be valid)"""
        schema = {'name': {'type': 'string', 'required': False}}
        data = {}
        is_valid, errors = self.framework.validate(data, schema)
        assert is_valid is True

    def test_optional_field_default(self):
        """Test that fields are optional by default"""
        schema = {'name': {'type': 'string'}}  # No 'required' key
        data = {}
        is_valid, errors = self.framework.validate(data, schema)
        assert is_valid is True

    def test_extra_fields_ignored(self):
        """Test that extra fields not in schema are ignored"""
        schema = {'name': {'type': 'string', 'required': True}}
        data = {'name': 'Alice', 'age': 30, 'city': 'NYC'}
        is_valid, errors = self.framework.validate(data, schema)
        assert is_valid is True


class TestTypeValidation:
    """Tests for type-specific validation"""

    def setup_method(self):
        """Setup framework instance"""
        self.framework = ValidationFramework()

    def test_string_type_valid(self):
        """Test string type validation"""
        schema = {'name': {'type': 'string'}}
        data = {'name': 'Alice'}
        is_valid, errors = self.framework.validate(data, schema)
        assert is_valid is True

    def test_string_type_invalid(self):
        """Test string type with wrong type"""
        schema = {'name': {'type': 'string'}}
        data = {'name': 123}
        is_valid, errors = self.framework.validate(data, schema)
        assert is_valid is False
        assert "Expected string" in errors[0]

    def test_int_type_valid(self):
        """Test int type validation"""
        schema = {'age': {'type': 'int'}}
        data = {'age': 30}
        is_valid, errors = self.framework.validate(data, schema)
        assert is_valid is True

    def test_int_type_invalid(self):
        """Test int type with wrong type"""
        schema = {'age': {'type': 'int'}}
        data = {'age': '30'}
        is_valid, errors = self.framework.validate(data, schema)
        assert is_valid is False
        assert "Expected int" in errors[0]

    def test_float_type_valid(self):
        """Test float type validation"""
        schema = {'price': {'type': 'float'}}
        data = {'price': 19.99}
        is_valid, errors = self.framework.validate(data, schema)
        assert is_valid is True

    def test_bool_type_valid(self):
        """Test bool type validation"""
        schema = {'active': {'type': 'bool'}}
        data = {'active': True}
        is_valid, errors = self.framework.validate(data, schema)
        assert is_valid is True

    def test_unknown_type(self):
        """Test validation with unknown type"""
        schema = {'field': {'type': 'unknown_type'}}
        data = {'field': 'value'}
        is_valid, errors = self.framework.validate(data, schema)
        assert is_valid is False
        assert "Unknown type" in errors[0]


class TestConstraintValidation:
    """Tests for constraint validation"""

    def setup_method(self):
        """Setup framework instance"""
        self.framework = ValidationFramework()

    def test_string_min_length_constraint(self):
        """Test string with min_length constraint"""
        schema = {
            'password': {
                'type': 'string',
                'constraints': {'min_length': 8}
            }
        }

        # Valid
        is_valid, errors = self.framework.validate({'password': 'password123'}, schema)
        assert is_valid is True

        # Invalid
        is_valid, errors = self.framework.validate({'password': 'pass'}, schema)
        assert is_valid is False
        assert "too short" in errors[0].lower()

    def test_string_max_length_constraint(self):
        """Test string with max_length constraint"""
        schema = {
            'username': {
                'type': 'string',
                'constraints': {'max_length': 20}
            }
        }

        # Valid
        is_valid, errors = self.framework.validate({'username': 'alice'}, schema)
        assert is_valid is True

        # Invalid
        is_valid, errors = self.framework.validate({'username': 'a' * 25}, schema)
        assert is_valid is False
        assert "too long" in errors[0].lower()

    def test_int_min_max_constraints(self):
        """Test int with min and max constraints"""
        schema = {
            'age': {
                'type': 'int',
                'constraints': {'min_value': 0, 'max_value': 120}
            }
        }

        # Valid
        is_valid, errors = self.framework.validate({'age': 30}, schema)
        assert is_valid is True

        # Too small
        is_valid, errors = self.framework.validate({'age': -5}, schema)
        assert is_valid is False

        # Too large
        is_valid, errors = self.framework.validate({'age': 150}, schema)
        assert is_valid is False

    def test_float_precision_constraint(self):
        """Test float with precision constraint"""
        schema = {
            'price': {
                'type': 'float',
                'constraints': {'precision': 2}
            }
        }

        # Valid
        is_valid, errors = self.framework.validate({'price': 19.99}, schema)
        assert is_valid is True

        # Invalid - too many decimals
        is_valid, errors = self.framework.validate({'price': 19.999}, schema)
        assert is_valid is False


class TestComplexSchemas:
    """Tests for complex multi-field schemas"""

    def setup_method(self):
        """Setup framework instance"""
        self.framework = ValidationFramework()

    def test_user_schema_valid(self):
        """Test realistic user schema with multiple fields"""
        schema = {
            'username': {
                'type': 'string',
                'required': True,
                'constraints': {'min_length': 3, 'max_length': 20}
            },
            'age': {
                'type': 'int',
                'required': True,
                'constraints': {'min_value': 0, 'max_value': 120}
            },
            'email': {
                'type': 'string',
                'required': True,
                'constraints': {'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'}
            },
            'score': {
                'type': 'float',
                'required': False,
                'constraints': {'min_value': 0.0, 'max_value': 100.0}
            },
            'active': {
                'type': 'bool',
                'required': False
            }
        }

        data = {
            'username': 'alice',
            'age': 30,
            'email': 'alice@example.com',
            'score': 85.5,
            'active': True
        }

        is_valid, errors = self.framework.validate(data, schema)
        assert is_valid is True
        assert errors == []

    def test_user_schema_multiple_errors(self):
        """Test that multiple validation errors are collected"""
        schema = {
            'username': {
                'type': 'string',
                'required': True,
                'constraints': {'min_length': 3}
            },
            'age': {
                'type': 'int',
                'required': True,
                'constraints': {'min_value': 0}
            },
            'email': {
                'type': 'string',
                'required': True
            }
        }

        data = {
            'username': 'ab',  # Too short
            'age': -5,  # Too small
            # email missing
        }

        is_valid, errors = self.framework.validate(data, schema)
        assert is_valid is False
        assert len(errors) == 3  # 3 validation errors

    def test_partial_data_valid(self):
        """Test schema where only some fields are provided"""
        schema = {
            'name': {'type': 'string', 'required': True},
            'age': {'type': 'int', 'required': False},
            'city': {'type': 'string', 'required': False}
        }

        data = {'name': 'Alice'}  # Only required field
        is_valid, errors = self.framework.validate(data, schema)
        assert is_valid is True


class TestExtensibility:
    """Tests for framework extensibility"""

    def test_register_custom_validator(self):
        """Test registering a custom validator"""
        # Create a custom validator
        class EmailValidator:
            def validate(self, value, constraints):
                if not isinstance(value, str):
                    return False, "Expected string"
                if '@' not in value:
                    return False, "Invalid email format"
                return True, ""

        framework = ValidationFramework()
        framework.register_validator('email', EmailValidator())

        schema = {'email': {'type': 'email'}}

        # Valid
        is_valid, errors = framework.validate({'email': 'test@example.com'}, schema)
        assert is_valid is True

        # Invalid
        is_valid, errors = framework.validate({'email': 'not-an-email'}, schema)
        assert is_valid is False

    def test_override_built_in_validator(self):
        """Test that built-in validators can be overridden"""
        class CustomStringValidator:
            def validate(self, value, constraints):
                # Always reject
                return False, "Custom validation failed"

        framework = ValidationFramework()
        framework.register_validator('string', CustomStringValidator())

        schema = {'name': {'type': 'string'}}
        is_valid, errors = framework.validate({'name': 'Alice'}, schema)
        assert is_valid is False
        assert "Custom validation failed" in errors[0]


class TestErrorMessages:
    """Tests for error message quality"""

    def setup_method(self):
        """Setup framework instance"""
        self.framework = ValidationFramework()

    def test_error_includes_field_name(self):
        """Test that error messages include field name"""
        schema = {'age': {'type': 'int'}}
        data = {'age': 'not an int'}
        is_valid, errors = self.framework.validate(data, schema)
        assert is_valid is False
        assert "'age'" in errors[0]

    def test_error_is_descriptive(self):
        """Test that error messages are descriptive"""
        schema = {'name': {'type': 'string', 'constraints': {'min_length': 5}}}
        data = {'name': 'Bob'}
        is_valid, errors = self.framework.validate(data, schema)
        assert is_valid is False
        assert "too short" in errors[0].lower()
        assert "5" in errors[0]  # Should mention the constraint value

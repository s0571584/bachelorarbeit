"""
Unit Tests für validation_framework.py
"""

import unittest
from validation_framework import DataValidator, ValidationResult


class TestValidationResult(unittest.TestCase):

    def test_validation_result_valid(self):
        """Test: ValidationResult für gültige Daten"""
        result = ValidationResult(True)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])

    def test_validation_result_invalid(self):
        """Test: ValidationResult für ungültige Daten"""
        errors = ["Error 1", "Error 2"]
        result = ValidationResult(False, errors)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors, errors)


class TestDataValidator(unittest.TestCase):

    def setUp(self):
        """Setup - Erstelle Validator"""
        self.validator = DataValidator()

    def test_valid_simple_data(self):
        """Test: Gültige einfache Daten"""
        schema = {
            "name": {"type": "str", "required": True},
            "age": {"type": "int", "required": True}
        }
        data = {"name": "Alice", "age": 30}

        result = self.validator.validate(data, schema)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])

    def test_missing_required_field(self):
        """Test: Fehlendes erforderliches Feld"""
        schema = {
            "name": {"type": "str", "required": True},
            "age": {"type": "int", "required": True}
        }
        data = {"name": "Alice"}

        result = self.validator.validate(data, schema)
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 1)
        self.assertIn("age", result.errors[0])

    def test_optional_field_missing(self):
        """Test: Optionales Feld fehlt (sollte gültig sein)"""
        schema = {
            "name": {"type": "str", "required": True},
            "age": {"type": "int", "required": False}
        }
        data = {"name": "Alice"}

        result = self.validator.validate(data, schema)
        self.assertTrue(result.is_valid)

    def test_wrong_type(self):
        """Test: Falscher Typ"""
        schema = {
            "name": {"type": "str", "required": True},
            "age": {"type": "int", "required": True}
        }
        data = {"name": "Alice", "age": "30"}  # Age sollte int sein

        result = self.validator.validate(data, schema)
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 1)

    def test_int_min_constraint(self):
        """Test: Integer minimum constraint"""
        schema = {"age": {"type": "int", "min": 0}}
        data_valid = {"age": 5}
        data_invalid = {"age": -1}

        result_valid = self.validator.validate(data_valid, schema)
        self.assertTrue(result_valid.is_valid)

        result_invalid = self.validator.validate(data_invalid, schema)
        self.assertFalse(result_invalid.is_valid)

    def test_int_max_constraint(self):
        """Test: Integer maximum constraint"""
        schema = {"age": {"type": "int", "max": 150}}
        data_valid = {"age": 100}
        data_invalid = {"age": 200}

        result_valid = self.validator.validate(data_valid, schema)
        self.assertTrue(result_valid.is_valid)

        result_invalid = self.validator.validate(data_invalid, schema)
        self.assertFalse(result_invalid.is_valid)

    def test_string_min_length(self):
        """Test: String minimum Länge"""
        schema = {"name": {"type": "str", "min_length": 2}}
        data_valid = {"name": "Alice"}
        data_invalid = {"name": "A"}

        result_valid = self.validator.validate(data_valid, schema)
        self.assertTrue(result_valid.is_valid)

        result_invalid = self.validator.validate(data_invalid, schema)
        self.assertFalse(result_invalid.is_valid)

    def test_string_max_length(self):
        """Test: String maximum Länge"""
        schema = {"name": {"type": "str", "max_length": 10}}
        data_valid = {"name": "Alice"}
        data_invalid = {"name": "VeryLongName123"}

        result_valid = self.validator.validate(data_valid, schema)
        self.assertTrue(result_valid.is_valid)

        result_invalid = self.validator.validate(data_invalid, schema)
        self.assertFalse(result_invalid.is_valid)

    def test_list_min_length(self):
        """Test: List minimum Länge"""
        schema = {"hobbies": {"type": "list", "min_length": 1}}
        data_valid = {"hobbies": ["reading"]}
        data_invalid = {"hobbies": []}

        result_valid = self.validator.validate(data_valid, schema)
        self.assertTrue(result_valid.is_valid)

        result_invalid = self.validator.validate(data_invalid, schema)
        self.assertFalse(result_invalid.is_valid)

    def test_list_max_length(self):
        """Test: List maximum Länge"""
        schema = {"hobbies": {"type": "list", "max_length": 3}}
        data_valid = {"hobbies": ["reading", "coding"]}
        data_invalid = {"hobbies": ["a", "b", "c", "d"]}

        result_valid = self.validator.validate(data_valid, schema)
        self.assertTrue(result_valid.is_valid)

        result_invalid = self.validator.validate(data_invalid, schema)
        self.assertFalse(result_invalid.is_valid)

    def test_float_type(self):
        """Test: Float Typ"""
        schema = {"price": {"type": "float", "min": 0.0, "max": 1000.0}}
        data_valid = {"price": 49.99}
        data_invalid = {"price": 1500.0}

        result_valid = self.validator.validate(data_valid, schema)
        self.assertTrue(result_valid.is_valid)

        result_invalid = self.validator.validate(data_invalid, schema)
        self.assertFalse(result_invalid.is_valid)

    def test_bool_type(self):
        """Test: Boolean Typ"""
        schema = {"active": {"type": "bool", "required": True}}
        data_valid = {"active": True}
        data_invalid = {"active": "yes"}

        result_valid = self.validator.validate(data_valid, schema)
        self.assertTrue(result_valid.is_valid)

        result_invalid = self.validator.validate(data_invalid, schema)
        self.assertFalse(result_invalid.is_valid)

    def test_dict_type(self):
        """Test: Dictionary Typ"""
        schema = {"metadata": {"type": "dict", "required": False}}
        data_valid = {"metadata": {"key": "value"}}
        data_missing = {}

        result_valid = self.validator.validate(data_valid, schema)
        self.assertTrue(result_valid.is_valid)

        result_missing = self.validator.validate(data_missing, schema)
        self.assertTrue(result_missing.is_valid)

    def test_multiple_errors(self):
        """Test: Multiple Validierungsfehler"""
        schema = {
            "name": {"type": "str", "required": True, "min_length": 2},
            "age": {"type": "int", "required": True, "min": 0}
        }
        data = {"name": "A", "age": -5}

        result = self.validator.validate(data, schema)
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 2)

    def test_invalid_data_type(self):
        """Test: Ungültiger Data-Typ (nicht Dictionary)"""
        schema = {"name": {"type": "str"}}
        data = "not a dict"

        result = self.validator.validate(data, schema)
        self.assertFalse(result.is_valid)
        self.assertIn("Dictionary", result.errors[0])

    def test_invalid_schema_type(self):
        """Test: Ungültiger Schema-Typ (nicht Dictionary)"""
        schema = "not a dict"
        data = {"name": "Alice"}

        result = self.validator.validate(data, schema)
        self.assertFalse(result.is_valid)
        self.assertIn("Dictionary", result.errors[0])


if __name__ == '__main__':
    unittest.main()

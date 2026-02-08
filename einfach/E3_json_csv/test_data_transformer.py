"""
Unit Tests für data_transformer.py
"""

import unittest
from data_transformer import json_to_csv


class TestJsonToCsv(unittest.TestCase):

    def test_single_user(self):
        """Test mit einem User"""
        json_string = '[{"name": "Alice", "email": "alice@example.com", "age": 30}]'
        expected = 'name,email,age\nAlice,alice@example.com,30'
        self.assertEqual(json_to_csv(json_string), expected)

    def test_multiple_users(self):
        """Test mit mehreren Users"""
        json_string = '''[
            {"name": "Alice", "email": "alice@example.com", "age": 30},
            {"name": "Bob", "email": "bob@example.com", "age": 25}
        ]'''
        result = json_to_csv(json_string)
        lines = result.split('\n')
        self.assertEqual(len(lines), 3)  # Header + 2 Zeilen
        self.assertEqual(lines[0], 'name,email,age')
        self.assertIn('Alice', lines[1])
        self.assertIn('Bob', lines[2])

    def test_empty_list(self):
        """Test mit leerer Liste"""
        json_string = '[]'
        self.assertEqual(json_to_csv(json_string), '')

    def test_different_field_order(self):
        """Test mit unterschiedlicher Feldreihenfolge"""
        json_string = '[{"email": "test@example.com", "name": "Test", "age": 20}]'
        result = json_to_csv(json_string)
        self.assertIn('email', result)
        self.assertIn('name', result)
        self.assertIn('age', result)

    def test_invalid_json(self):
        """Test mit ungültigem JSON"""
        with self.assertRaises(ValueError):
            json_to_csv('invalid json')

    def test_json_not_list(self):
        """Test mit JSON-Objekt statt Liste"""
        json_string = '{"name": "Alice", "email": "alice@example.com", "age": 30}'
        with self.assertRaises(ValueError):
            json_to_csv(json_string)

    def test_invalid_input_type(self):
        """Test mit ungültigem Input-Typ"""
        with self.assertRaises(TypeError):
            json_to_csv(123)

    def test_invalid_input_none(self):
        """Test mit None"""
        with self.assertRaises(TypeError):
            json_to_csv(None)

    def test_numbers_in_data(self):
        """Test mit numerischen Werten"""
        json_string = '[{"name": "Alice", "email": "alice@example.com", "age": 30}]'
        result = json_to_csv(json_string)
        self.assertIn('30', result)

    def test_special_characters(self):
        """Test mit Sonderzeichen im Namen"""
        json_string = '[{"name": "O\'Brien", "email": "obrien@example.com", "age": 40}]'
        result = json_to_csv(json_string)
        self.assertIn("O'Brien", result)


if __name__ == "__main__":
    unittest.main()

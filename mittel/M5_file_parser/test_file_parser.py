"""
Unit Tests für file_parser.py
"""

import unittest
import os
import tempfile
import json
from file_parser import FileParser


class TestFileParser(unittest.TestCase):

    def setUp(self):
        """Setup - Erstelle Parser und Liste für temporäre Dateien"""
        self.parser = FileParser()
        self.temp_files = []

    def tearDown(self):
        """Cleanup - Lösche temporäre Dateien"""
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def create_temp_csv(self, content):
        """Hilfsfunktion zum Erstellen temporärer CSV-Dateien"""
        fd, filepath = tempfile.mkstemp(suffix='.csv')
        os.close(fd)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        self.temp_files.append(filepath)
        return filepath

    def create_temp_json(self, data):
        """Hilfsfunktion zum Erstellen temporärer JSON-Dateien"""
        fd, filepath = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        self.temp_files.append(filepath)
        return filepath

    # CSV Tests

    def test_parse_csv_simple(self):
        """Test: Einfache CSV-Datei parsen"""
        content = "name,email\nAlice,alice@example.com\nBob,bob@example.com"
        filepath = self.create_temp_csv(content)

        result = self.parser.parse_csv(filepath)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Alice')
        self.assertEqual(result[1]['name'], 'Bob')

    def test_parse_csv_with_numbers(self):
        """Test: CSV mit Zahlen parsen"""
        content = "name,age\nAlice,30\nBob,25"
        filepath = self.create_temp_csv(content)

        result = self.parser.parse_csv(filepath)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['age'], '30')  # CSV liest als String

    def test_parse_csv_empty_file(self):
        """Test: Leere CSV-Datei parsen"""
        content = ""
        filepath = self.create_temp_csv(content)

        result = self.parser.parse_csv(filepath)
        self.assertEqual(result, [])

    def test_parse_csv_header_only(self):
        """Test: CSV nur mit Header"""
        content = "name,email"
        filepath = self.create_temp_csv(content)

        result = self.parser.parse_csv(filepath)
        self.assertEqual(result, [])

    def test_parse_csv_file_not_found(self):
        """Test: CSV-Datei nicht gefunden"""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_csv('nonexistent.csv')

    def test_parse_csv_with_quotes(self):
        """Test: CSV mit Anführungszeichen"""
        content = 'name,description\nAlice,"Test, with comma"\nBob,"Normal"'
        filepath = self.create_temp_csv(content)

        result = self.parser.parse_csv(filepath)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['description'], 'Test, with comma')

    # JSON Tests

    def test_parse_json_simple(self):
        """Test: Einfache JSON-Datei parsen"""
        data = [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob", "email": "bob@example.com"}
        ]
        filepath = self.create_temp_json(data)

        result = self.parser.parse_json(filepath)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Alice')
        self.assertEqual(result[1]['name'], 'Bob')

    def test_parse_json_with_numbers(self):
        """Test: JSON mit Zahlen parsen"""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ]
        filepath = self.create_temp_json(data)

        result = self.parser.parse_json(filepath)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['age'], 30)  # JSON behält Typ

    def test_parse_json_empty_array(self):
        """Test: Leeres JSON-Array parsen"""
        data = []
        filepath = self.create_temp_json(data)

        result = self.parser.parse_json(filepath)
        self.assertEqual(result, [])

    def test_parse_json_file_not_found(self):
        """Test: JSON-Datei nicht gefunden"""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_json('nonexistent.json')

    def test_parse_json_invalid_format(self):
        """Test: Ungültiges JSON-Format"""
        fd, filepath = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        with open(filepath, 'w') as f:
            f.write('{invalid json}')
        self.temp_files.append(filepath)

        with self.assertRaises(ValueError):
            self.parser.parse_json(filepath)

    def test_parse_json_not_array(self):
        """Test: JSON ist kein Array"""
        data = {"name": "Alice", "email": "alice@example.com"}
        filepath = self.create_temp_json(data)

        with self.assertRaises(ValueError) as context:
            self.parser.parse_json(filepath)
        self.assertIn("Array", str(context.exception))

    def test_parse_json_nested_objects(self):
        """Test: JSON mit verschachtelten Objekten"""
        data = [
            {"name": "Alice", "address": {"city": "Berlin", "country": "Germany"}},
            {"name": "Bob", "address": {"city": "Munich", "country": "Germany"}}
        ]
        filepath = self.create_temp_json(data)

        result = self.parser.parse_json(filepath)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['address']['city'], 'Berlin')

    def test_parse_json_with_unicode(self):
        """Test: JSON mit Unicode-Zeichen"""
        data = [
            {"name": "Müller", "city": "München"},
            {"name": "Øresund", "city": "København"}
        ]
        filepath = self.create_temp_json(data)

        result = self.parser.parse_json(filepath)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Müller')


if __name__ == '__main__':
    unittest.main()

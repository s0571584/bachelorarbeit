"""
Unit Tests für file_operations.py
"""

import unittest
import os
import tempfile
from file_operations import file_stats


class TestFileStats(unittest.TestCase):

    def setUp(self):
        """Setup - Erstelle temporäre Test-Dateien"""
        self.temp_files = []

    def tearDown(self):
        """Cleanup - Lösche temporäre Test-Dateien"""
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def create_temp_file(self, content):
        """Hilfsfunktion zum Erstellen temporärer Dateien"""
        fd, filepath = tempfile.mkstemp(suffix='.txt')
        os.close(fd)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        self.temp_files.append(filepath)
        return filepath

    def test_simple_file(self):
        """Test mit einfacher Datei"""
        filepath = self.create_temp_file("Hello World")
        stats = file_stats(filepath)
        self.assertEqual(stats['line_count'], 1)
        self.assertEqual(stats['word_count'], 2)
        self.assertEqual(stats['char_count'], 11)

    def test_multiline_file(self):
        """Test mit mehrzeiliger Datei"""
        content = "Line 1\nLine 2\nLine 3"
        filepath = self.create_temp_file(content)
        stats = file_stats(filepath)
        self.assertEqual(stats['line_count'], 3)
        self.assertEqual(stats['word_count'], 6)

    def test_empty_file(self):
        """Test mit leerer Datei"""
        filepath = self.create_temp_file("")
        stats = file_stats(filepath)
        self.assertEqual(stats['line_count'], 0)
        self.assertEqual(stats['word_count'], 0)
        self.assertEqual(stats['char_count'], 0)

    def test_file_with_empty_lines(self):
        """Test mit leeren Zeilen"""
        content = "Line 1\n\nLine 3"
        filepath = self.create_temp_file(content)
        stats = file_stats(filepath)
        self.assertEqual(stats['line_count'], 3)
        self.assertEqual(stats['word_count'], 4)

    def test_file_with_multiple_spaces(self):
        """Test mit mehreren Leerzeichen"""
        content = "Word1    Word2     Word3"
        filepath = self.create_temp_file(content)
        stats = file_stats(filepath)
        self.assertEqual(stats['word_count'], 3)

    def test_file_not_found(self):
        """Test mit nicht-existierender Datei"""
        with self.assertRaises(FileNotFoundError):
            file_stats("nonexistent_file.txt")

    def test_invalid_filepath_type(self):
        """Test mit ungültigem Filepath-Typ"""
        with self.assertRaises(TypeError):
            file_stats(123)

    def test_invalid_filepath_none(self):
        """Test mit None"""
        with self.assertRaises(TypeError):
            file_stats(None)

    def test_unicode_characters(self):
        """Test mit Unicode-Zeichen"""
        content = "Äpfel und Öl\nÜber den See"
        filepath = self.create_temp_file(content)
        stats = file_stats(filepath)
        self.assertEqual(stats['line_count'], 2)
        self.assertEqual(stats['word_count'], 6)

    def test_numbers_and_special_chars(self):
        """Test mit Zahlen und Sonderzeichen"""
        content = "Test 123 !@# $%^"
        filepath = self.create_temp_file(content)
        stats = file_stats(filepath)
        self.assertEqual(stats['word_count'], 4)


if __name__ == "__main__":
    unittest.main()

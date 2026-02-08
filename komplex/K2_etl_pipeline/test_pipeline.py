"""
Unit Tests für die ETL Pipeline
"""

import unittest
import os
import tempfile
import json
import logging
from extractor import Extractor
from transformer import Transformer
from loader import Loader
from pipeline import Pipeline


# Disable logging in tests
logging.disable(logging.CRITICAL)


class TestExtractor(unittest.TestCase):

    def setUp(self):
        """Setup - Erstelle Extractor"""
        self.extractor = Extractor()
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

    def test_extract_from_csv(self):
        """Test: CSV extrahieren"""
        content = "name,age\nAlice,30\nBob,25"
        filepath = self.create_temp_csv(content)
        data = self.extractor.extract_from_csv(filepath)
        self.assertEqual(len(data), 2)

    def test_extract_from_json(self):
        """Test: JSON extrahieren"""
        data_content = [{"name": "Alice"}, {"name": "Bob"}]
        filepath = self.create_temp_json(data_content)
        data = self.extractor.extract_from_json(filepath)
        self.assertEqual(len(data), 2)

    def test_extract_auto_format_csv(self):
        """Test: Auto-Format-Erkennung (CSV)"""
        content = "name,age\nAlice,30"
        filepath = self.create_temp_csv(content)
        data = self.extractor.extract(filepath)
        self.assertEqual(len(data), 1)

    def test_extract_auto_format_json(self):
        """Test: Auto-Format-Erkennung (JSON)"""
        data_content = [{"name": "Alice"}]
        filepath = self.create_temp_json(data_content)
        data = self.extractor.extract(filepath)
        self.assertEqual(len(data), 1)

    def test_extract_from_csv_file_not_found(self):
        """Test: CSV extrahieren aus nicht-existierender Datei"""
        with self.assertRaises(FileNotFoundError):
            self.extractor.extract_from_csv("nonexistent.csv")

    def test_extract_from_json_file_not_found(self):
        """Test: JSON extrahieren aus nicht-existierender Datei"""
        with self.assertRaises(FileNotFoundError):
            self.extractor.extract_from_json("nonexistent.json")

    def test_extract_from_json_invalid_format(self):
        """Test: JSON extrahieren mit ungültigem Format (nicht array)"""
        fd, filepath = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('{"not": "an array"}')
        self.temp_files.append(filepath)

        with self.assertRaises(ValueError):
            self.extractor.extract_from_json(filepath)

    def test_extract_from_json_invalid_json(self):
        """Test: JSON extrahieren mit ungültigem JSON"""
        fd, filepath = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('invalid json content')
        self.temp_files.append(filepath)

        with self.assertRaises(ValueError):
            self.extractor.extract_from_json(filepath)

    def test_extract_from_csv_invalid_format(self):
        """Test: CSV extrahieren mit ungültigem Format"""
        fd, filepath = tempfile.mkstemp(suffix='.csv')
        os.close(fd)
        # CSV mit inkonsistenten Spalten
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('col1,col2\n')
            # Schreibe ungültige Daten
        self.temp_files.append(filepath)

        # Dies sollte erfolgreich sein, da CSV sehr tolerant ist
        data = self.extractor.extract_from_csv(filepath)
        self.assertEqual(len(data), 0)

    def test_extract_unsupported_format(self):
        """Test: Extrahieren mit nicht unterstütztem Format"""
        with self.assertRaises(ValueError):
            self.extractor.extract("file.xml", format="xml")


class TestTransformer(unittest.TestCase):

    def setUp(self):
        """Setup - Erstelle Transformer"""
        self.transformer = Transformer()

    def test_remove_null_values(self):
        """Test: Null-Werte entfernen"""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": None},
            {"name": "Charlie", "age": 35}
        ]
        result = self.transformer.remove_null_values(data)
        self.assertEqual(len(result), 2)

    def test_validate_schema(self):
        """Test: Schema validieren"""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob"},  # Fehlt 'age'
            {"name": "Charlie", "age": 35}
        ]
        result = self.transformer.validate_schema(data, ['name', 'age'])
        self.assertEqual(len(result), 2)

    def test_normalize_field(self):
        """Test: Feld normalisieren"""
        data = [
            {"name": "Alice", "age": "30"},
            {"name": "Bob", "age": "25"}
        ]
        result = self.transformer.normalize_field(data, 'age', int)
        self.assertIsInstance(result[0]['age'], int)

    def test_normalize_field_with_error(self):
        """Test: Feld normalisieren mit Fehler"""
        data = [
            {"name": "Alice", "age": "not_a_number"},
            {"name": "Bob", "age": "25"}
        ]
        # Sollte Warning loggen aber nicht crashen
        result = self.transformer.normalize_field(data, 'age', int)
        self.assertEqual(len(result), 2)

    def test_add_transformation(self):
        """Test: Transformation hinzufügen"""
        def uppercase_name(item):
            item['name'] = item['name'].upper()
            return item

        self.transformer.add_transformation(uppercase_name)
        data = [{"name": "alice"}]
        result = self.transformer.transform(data)
        self.assertEqual(result[0]['name'], "ALICE")

    def test_transform_with_multiple_transformations(self):
        """Test: Mehrere Transformationen anwenden"""
        def uppercase_name(item):
            item['name'] = item['name'].upper()
            return item

        def add_prefix(item):
            item['name'] = "Mr. " + item['name']
            return item

        self.transformer.add_transformation(uppercase_name)
        self.transformer.add_transformation(add_prefix)

        data = [{"name": "alice"}]
        result = self.transformer.transform(data)
        self.assertEqual(result[0]['name'], "Mr. ALICE")

    def test_transform_with_error(self):
        """Test: Transformation mit Fehler"""
        def failing_transformation(item):
            raise ValueError("Transformation failed")

        self.transformer.add_transformation(failing_transformation)
        data = [{"name": "alice"}]

        with self.assertRaises(ValueError):
            self.transformer.transform(data)

    def test_apply_custom_transformations(self):
        """Test: Custom Transformationen anwenden"""
        def remove_age(data):
            for item in data:
                item.pop('age', None)
            return data

        def add_country(data):
            for item in data:
                item['country'] = 'Germany'
            return data

        data = [{"name": "Alice", "age": 30}]
        result = self.transformer.apply_custom_transformations(data, [remove_age, add_country])

        self.assertNotIn('age', result[0])
        self.assertEqual(result[0]['country'], 'Germany')


class TestLoader(unittest.TestCase):

    def setUp(self):
        """Setup - Erstelle Loader"""
        self.loader = Loader(':memory:')
        self.loader.connect()

    def tearDown(self):
        """Cleanup - Schließe Verbindung"""
        self.loader.close()

    def test_create_table(self):
        """Test: Tabelle erstellen"""
        schema = {"id": "INTEGER PRIMARY KEY", "name": "TEXT"}
        self.loader.create_table("test_table", schema)

        # Prüfe ob Tabelle existiert
        cursor = self.loader.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'")
        result = cursor.fetchone()
        self.assertIsNotNone(result)

    def test_load_data_append(self):
        """Test: Daten laden (append)"""
        schema = {"id": "INTEGER PRIMARY KEY AUTOINCREMENT", "name": "TEXT"}
        self.loader.create_table("test_table", schema)

        data = [{"name": "Alice"}, {"name": "Bob"}]
        self.loader.load_data("test_table", data)

        count = self.loader.get_row_count("test_table")
        self.assertEqual(count, 2)

    def test_load_data_replace(self):
        """Test: Daten laden (replace)"""
        schema = {"id": "INTEGER PRIMARY KEY AUTOINCREMENT", "name": "TEXT"}
        self.loader.create_table("test_table", schema)

        # Erste Ladung
        data1 = [{"name": "Alice"}, {"name": "Bob"}]
        self.loader.load_data("test_table", data1)

        # Zweite Ladung (replace)
        data2 = [{"name": "Charlie"}]
        self.loader.load_data("test_table", data2, mode='replace')

        count = self.loader.get_row_count("test_table")
        self.assertEqual(count, 1)

    def test_load_data_invalid_mode(self):
        """Test: Daten laden mit ungültigem Modus"""
        schema = {"id": "INTEGER PRIMARY KEY AUTOINCREMENT", "name": "TEXT"}
        self.loader.create_table("test_table", schema)
        data = [{"name": "Alice"}]

        with self.assertRaises(ValueError):
            self.loader.load_data("test_table", data, mode='invalid')

    def test_load_data_without_connection(self):
        """Test: Daten laden ohne bestehende Verbindung"""
        loader = Loader(':memory:')
        # Keine connect() aufrufen
        schema = {"id": "INTEGER PRIMARY KEY AUTOINCREMENT", "name": "TEXT"}
        loader.create_table("test_table", schema)
        data = [{"name": "Alice"}]
        loader.load_data("test_table", data)
        count = loader.get_row_count("test_table")
        self.assertEqual(count, 1)
        loader.close()


class TestPipeline(unittest.TestCase):

    def setUp(self):
        """Setup - Erstelle Pipeline"""
        self.pipeline = Pipeline(':memory:')
        self.temp_files = []

    def tearDown(self):
        """Cleanup - Lösche temporäre Dateien"""
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def create_temp_json(self, data):
        """Hilfsfunktion zum Erstellen temporärer JSON-Dateien"""
        fd, filepath = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        self.temp_files.append(filepath)
        return filepath

    def test_pipeline_basic(self):
        """Test: Basis-Pipeline"""
        # Test-Daten erstellen
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ]
        filepath = self.create_temp_json(data)

        # Schema definieren
        schema = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name": "TEXT",
            "age": "INTEGER"
        }

        # Pipeline ausführen
        stats = self.pipeline.run(
            source_file=filepath,
            table_name='users',
            table_schema=schema
        )

        self.assertEqual(stats['extracted'], 2)
        self.assertEqual(stats['loaded'], 2)
        self.assertEqual(len(stats['errors']), 0)

    def test_pipeline_with_transformations(self):
        """Test: Pipeline mit Transformationen"""
        # Test-Daten mit Null-Werten
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": None},
            {"name": "Charlie", "age": 35}
        ]
        filepath = self.create_temp_json(data)

        # Schema definieren
        schema = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name": "TEXT",
            "age": "INTEGER"
        }

        # Pipeline ausführen (Null-Werte werden automatisch entfernt)
        stats = self.pipeline.run(
            source_file=filepath,
            table_name='users',
            table_schema=schema
        )

        self.assertEqual(stats['extracted'], 3)
        self.assertEqual(stats['transformed'], 2)  # Ein Eintrag mit Null wurde entfernt

    def test_pipeline_with_required_fields(self):
        """Test: Pipeline mit erforderlichen Feldern"""
        # Test-Daten mit fehlendem Feld
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob"},  # Fehlt 'age'
            {"name": "Charlie", "age": 35}
        ]
        filepath = self.create_temp_json(data)

        # Schema definieren
        schema = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name": "TEXT",
            "age": "INTEGER"
        }

        # Pipeline ausführen mit required_fields
        stats = self.pipeline.run(
            source_file=filepath,
            table_name='users',
            table_schema=schema,
            required_fields=['name', 'age']
        )

        self.assertEqual(stats['extracted'], 3)
        self.assertEqual(stats['transformed'], 2)  # Ein Eintrag ohne 'age' wurde entfernt

    def test_pipeline_custom(self):
        """Test: Custom Pipeline"""
        extract_data = [{"name": "Alice"}]

        def extract_fn():
            return extract_data

        def transform_fn(data):
            return data

        def load_fn(data):
            pass

        stats = self.pipeline.run_custom(extract_fn, transform_fn, load_fn)

        self.assertEqual(stats['extracted'], 1)
        self.assertEqual(stats['transformed'], 1)


if __name__ == '__main__':
    unittest.main()

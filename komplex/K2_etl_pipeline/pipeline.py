"""
Pipeline - Orchestriert den ETL-Prozess
"""

from typing import List, Dict, Callable, Optional
import logging
from extractor import Extractor
from transformer import Transformer
from loader import Loader


class Pipeline:
    """
    ETL Pipeline - Orchestriert Extract, Transform, Load
    """

    def __init__(self, db_path: str = ':memory:'):
        """
        Initialisiert die Pipeline.

        Args:
            db_path (str): Pfad zur Datenbank-Datei
        """
        self.extractor = Extractor()
        self.transformer = Transformer()
        self.loader = Loader(db_path)
        self.logger = logging.getLogger(__name__)

    def run(self,
            source_file: str,
            table_name: str,
            table_schema: Dict[str, str],
            source_format: Optional[str] = None,
            transformations: Optional[List[Callable]] = None,
            required_fields: Optional[List[str]] = None,
            load_mode: str = 'append') -> Dict:
        """
        Führt die ETL-Pipeline aus.

        Args:
            source_file (str): Pfad zur Quelldatei
            table_name (str): Name der Ziel-Tabelle
            table_schema (Dict[str, str]): Schema der Ziel-Tabelle
            source_format (str, optional): Format der Quelldatei ('csv' oder 'json')
            transformations (List[Callable], optional): Liste von Transformations-Funktionen
            required_fields (List[str], optional): Liste der erforderlichen Felder
            load_mode (str): 'append' oder 'replace'

        Returns:
            Dict: Statistiken über die Pipeline-Ausführung
        """
        stats = {
            'extracted': 0,
            'transformed': 0,
            'loaded': 0,
            'errors': []
        }

        try:
            # EXTRACT
            self.logger.info("=== EXTRACT Phase ===")
            data = self.extractor.extract(source_file, source_format)
            stats['extracted'] = len(data)
            self.logger.info(f"Extrahiert: {stats['extracted']} Einträge")

            # TRANSFORM
            self.logger.info("=== TRANSFORM Phase ===")

            # Null-Werte entfernen
            data = self.transformer.remove_null_values(data)

            # Schema validieren (wenn required_fields angegeben)
            if required_fields:
                data = self.transformer.validate_schema(data, required_fields)

            # Custom Transformations anwenden
            if transformations:
                data = self.transformer.apply_custom_transformations(data, transformations)

            stats['transformed'] = len(data)
            self.logger.info(f"Transformiert: {stats['transformed']} Einträge")

            # LOAD
            self.logger.info("=== LOAD Phase ===")
            self.loader.connect()
            self.loader.create_table(table_name, table_schema)
            self.loader.load_data(table_name, data, mode=load_mode)
            stats['loaded'] = self.loader.get_row_count(table_name)
            self.logger.info(f"Geladen: {stats['loaded']} Einträge")

        except Exception as e:
            error_msg = f"Fehler in Pipeline: {e}"
            self.logger.error(error_msg)
            stats['errors'].append(error_msg)

        finally:
            self.loader.close()

        return stats

    def run_custom(self,
                   extract_fn: Callable[[], List[Dict]],
                   transform_fn: Callable[[List[Dict]], List[Dict]],
                   load_fn: Callable[[List[Dict]], None]) -> Dict:
        """
        Führt eine Pipeline mit custom Extract/Transform/Load Funktionen aus.

        Args:
            extract_fn (Callable): Extract-Funktion
            transform_fn (Callable): Transform-Funktion
            load_fn (Callable): Load-Funktion

        Returns:
            Dict: Statistiken
        """
        stats = {
            'extracted': 0,
            'transformed': 0,
            'loaded': 0,
            'errors': []
        }

        try:
            # Extract
            self.logger.info("=== EXTRACT Phase (Custom) ===")
            data = extract_fn()
            stats['extracted'] = len(data)

            # Transform
            self.logger.info("=== TRANSFORM Phase (Custom) ===")
            data = transform_fn(data)
            stats['transformed'] = len(data)

            # Load
            self.logger.info("=== LOAD Phase (Custom) ===")
            load_fn(data)
            stats['loaded'] = len(data)

        except Exception as e:
            error_msg = f"Fehler in Pipeline: {e}"
            self.logger.error(error_msg)
            stats['errors'].append(error_msg)

        return stats


if __name__ == "__main__":
    # Setup Logging
    logging.basicConfig(level=logging.INFO)

    import tempfile
    import json
    import os

    # Beispiel-Verwendung
    # Test-Daten erstellen
    test_data = [
        {"name": "Alice", "age": "30", "city": "Berlin"},
        {"name": "Bob", "age": "25", "city": "Munich"},
        {"name": "Charlie", "age": "", "city": "Hamburg"},  # Wird entfernt (null value)
        {"name": "David", "age": "35", "city": "Frankfurt"}
    ]

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        json_file = f.name

    # Pipeline ausführen
    pipeline = Pipeline()

    # Transformations-Funktion definieren
    def normalize_age(data):
        transformer = Transformer()
        return transformer.normalize_field(data, 'age', lambda x: int(x) if x else 0)

    # Schema definieren
    schema = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "name": "TEXT",
        "age": "INTEGER",
        "city": "TEXT"
    }

    # Pipeline ausführen
    stats = pipeline.run(
        source_file=json_file,
        table_name='users',
        table_schema=schema,
        transformations=[normalize_age],
        required_fields=['name', 'age', 'city']
    )

    print("\n=== Pipeline Statistiken ===")
    print(f"Extrahiert: {stats['extracted']}")
    print(f"Transformiert: {stats['transformed']}")
    print(f"Geladen: {stats['loaded']}")
    print(f"Fehler: {stats['errors']}")

    # Cleanup
    os.remove(json_file)

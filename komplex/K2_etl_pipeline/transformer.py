"""
Transformer - Transformiert und validiert Daten
"""

from typing import List, Dict, Callable, Any
import logging


class Transformer:
    """
    Transformer - Wendet verschiedene Transformationen auf Daten an
    """

    def __init__(self):
        """Initialisiert den Transformer"""
        self.logger = logging.getLogger(__name__)
        self.transformations = []

    def add_transformation(self, transformation: Callable[[Dict], Dict]):
        """
        Fügt eine Transformation hinzu.

        Args:
            transformation (Callable): Funktion, die ein Dictionary nimmt und transformiert
        """
        self.transformations.append(transformation)

    def remove_null_values(self, data: List[Dict]) -> List[Dict]:
        """
        Entfernt Einträge mit null/None Werten.

        Args:
            data (List[Dict]): Input-Daten

        Returns:
            List[Dict]: Bereinigte Daten
        """
        cleaned = []
        removed_count = 0

        for item in data:
            if None not in item.values() and '' not in item.values():
                cleaned.append(item)
            else:
                removed_count += 1

        self.logger.info(f"Entfernt {removed_count} Einträge mit Null-Werten")
        return cleaned

    def validate_schema(self, data: List[Dict], required_fields: List[str]) -> List[Dict]:
        """
        Validiert, dass alle erforderlichen Felder vorhanden sind.

        Args:
            data (List[Dict]): Input-Daten
            required_fields (List[str]): Liste der erforderlichen Felder

        Returns:
            List[Dict]: Validierte Daten (nur Einträge mit allen Feldern)
        """
        validated = []
        removed_count = 0

        for item in data:
            if all(field in item for field in required_fields):
                validated.append(item)
            else:
                removed_count += 1

        self.logger.info(f"Entfernt {removed_count} Einträge ohne erforderliche Felder")
        return validated

    def normalize_field(self, data: List[Dict], field: str, normalizer: Callable[[Any], Any]) -> List[Dict]:
        """
        Normalisiert ein bestimmtes Feld in allen Einträgen.

        Args:
            data (List[Dict]): Input-Daten
            field (str): Feldname
            normalizer (Callable): Funktion zur Normalisierung

        Returns:
            List[Dict]: Daten mit normalisiertem Feld
        """
        for item in data:
            if field in item:
                try:
                    item[field] = normalizer(item[field])
                except Exception as e:
                    self.logger.warning(f"Fehler bei Normalisierung von Feld '{field}': {e}")

        self.logger.info(f"Normalisiert Feld '{field}'")
        return data

    def transform(self, data: List[Dict]) -> List[Dict]:
        """
        Wendet alle registrierten Transformationen an.

        Args:
            data (List[Dict]): Input-Daten

        Returns:
            List[Dict]: Transformierte Daten
        """
        result = data

        for transformation in self.transformations:
            try:
                result = [transformation(item) for item in result]
                self.logger.info(f"Transformation angewendet: {transformation.__name__}")
            except Exception as e:
                self.logger.error(f"Fehler bei Transformation: {e}")
                raise

        return result

    def apply_custom_transformations(self, data: List[Dict], transformations: List[Callable]) -> List[Dict]:
        """
        Wendet eine Liste von Transformations-Funktionen an.

        Args:
            data (List[Dict]): Input-Daten
            transformations (List[Callable]): Liste von Transformations-Funktionen

        Returns:
            List[Dict]: Transformierte Daten
        """
        result = data

        for transformation in transformations:
            result = transformation(result)

        return result


if __name__ == "__main__":
    # Setup Logging
    logging.basicConfig(level=logging.INFO)

    # Beispiel-Verwendung
    transformer = Transformer()

    # Test-Daten
    data = [
        {"name": "Alice", "age": "30", "city": "Berlin"},
        {"name": "Bob", "age": "25", "city": None},
        {"name": "Charlie", "age": "35", "city": "Munich"},
        {"age": "40", "city": "Hamburg"}  # Fehlt 'name'
    ]

    print("Original-Daten:", data)

    # Null-Werte entfernen
    data = transformer.remove_null_values(data)
    print("Nach Null-Entfernung:", data)

    # Schema validieren
    data = transformer.validate_schema(data, ['name', 'age', 'city'])
    print("Nach Schema-Validierung:", data)

    # Feld normalisieren (age zu int)
    data = transformer.normalize_field(data, 'age', lambda x: int(x) if isinstance(x, str) else x)
    print("Nach Normalisierung:", data)

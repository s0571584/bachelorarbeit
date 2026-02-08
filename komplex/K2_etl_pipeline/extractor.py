"""
Extractor - Extrahiert Daten aus verschiedenen Quellen
"""

import csv
import json
import os
from typing import List, Dict
import logging


class Extractor:
    """
    Extractor - Liest Daten aus CSV und JSON Dateien
    """

    def __init__(self):
        """Initialisiert den Extractor"""
        self.logger = logging.getLogger(__name__)

    def extract_from_csv(self, filepath: str) -> List[Dict]:
        """
        Extrahiert Daten aus einer CSV-Datei.

        Args:
            filepath (str): Pfad zur CSV-Datei

        Returns:
            List[Dict]: Liste von Dictionaries

        Raises:
            FileNotFoundError: Wenn Datei nicht existiert
            ValueError: Wenn Datei nicht geparst werden kann
        """
        if not os.path.exists(filepath):
            self.logger.error(f"CSV-Datei nicht gefunden: {filepath}")
            raise FileNotFoundError(f"Datei nicht gefunden: {filepath}")

        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                data = list(reader)
                self.logger.info(f"Extrahiert {len(data)} Zeilen aus CSV: {filepath}")
                return data
        except csv.Error as e:
            self.logger.error(f"Fehler beim Parsen der CSV-Datei: {e}")
            raise ValueError(f"Fehler beim Parsen der CSV-Datei: {e}")

    def extract_from_json(self, filepath: str) -> List[Dict]:
        """
        Extrahiert Daten aus einer JSON-Datei.

        Args:
            filepath (str): Pfad zur JSON-Datei

        Returns:
            List[Dict]: Liste von Dictionaries

        Raises:
            FileNotFoundError: Wenn Datei nicht existiert
            ValueError: Wenn Datei nicht geparst werden kann
        """
        if not os.path.exists(filepath):
            self.logger.error(f"JSON-Datei nicht gefunden: {filepath}")
            raise FileNotFoundError(f"Datei nicht gefunden: {filepath}")

        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)

                if not isinstance(data, list):
                    raise ValueError("JSON-Datei muss ein Array enthalten")

                self.logger.info(f"Extrahiert {len(data)} Einträge aus JSON: {filepath}")
                return data
        except json.JSONDecodeError as e:
            self.logger.error(f"Fehler beim Parsen der JSON-Datei: {e}")
            raise ValueError(f"Fehler beim Parsen der JSON-Datei: {e}")

    def extract(self, filepath: str, format: str = None) -> List[Dict]:
        """
        Extrahiert Daten aus einer Datei (automatische Format-Erkennung).

        Args:
            filepath (str): Pfad zur Datei
            format (str, optional): Format ('csv' oder 'json'). Wenn None, wird von Dateiendung abgeleitet.

        Returns:
            List[Dict]: Liste von Dictionaries

        Raises:
            ValueError: Wenn Format nicht unterstützt wird
        """
        if format is None:
            # Format von Dateiendung ableiten
            _, ext = os.path.splitext(filepath)
            format = ext.lower().lstrip('.')

        if format == 'csv':
            return self.extract_from_csv(filepath)
        elif format == 'json':
            return self.extract_from_json(filepath)
        else:
            raise ValueError(f"Nicht unterstütztes Format: {format}")


if __name__ == "__main__":
    # Setup Logging
    logging.basicConfig(level=logging.INFO)

    # Beispiel-Verwendung
    import tempfile

    extractor = Extractor()

    # CSV-Beispiel
    csv_content = "name,age,city\nAlice,30,Berlin\nBob,25,Munich"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        csv_file = f.name

    csv_data = extractor.extract_from_csv(csv_file)
    print(f"CSV-Daten: {csv_data}")
    os.remove(csv_file)

    # JSON-Beispiel
    json_data_content = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(json_data_content, f)
        json_file = f.name

    json_data = extractor.extract_from_json(json_file)
    print(f"JSON-Daten: {json_data}")
    os.remove(json_file)

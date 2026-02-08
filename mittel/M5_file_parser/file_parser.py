"""
File Parser - Liest CSV und JSON Dateien
"""

import csv
import json
import os
from typing import List, Dict


class ParserError(Exception):
    """Custom Exception für Parser-Fehler"""
    pass


class FileParser:
    """
    File Parser - Liest CSV und JSON Dateien und gibt sie als Liste von Dictionaries zurück
    """

    def parse_csv(self, filepath: str) -> List[Dict]:
        """
        Parst eine CSV-Datei und gibt die Daten als Liste von Dictionaries zurück.

        Args:
            filepath (str): Pfad zur CSV-Datei

        Returns:
            List[Dict]: Liste von Dictionaries (jede Zeile ist ein Dictionary)

        Raises:
            FileNotFoundError: Wenn Datei nicht gefunden wird
            ParserError: Wenn Datei nicht gelesen oder geparst werden kann
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                return list(reader)
        except FileNotFoundError:
            raise  # FileNotFoundError durchlassen
        except PermissionError:
            raise ParserError(f"Permission denied: {filepath}")
        except csv.Error as e:
            raise ParserError(f"Fehler beim Parsen der CSV-Datei: {e}")
        except Exception as e:
            raise ParserError(f"Unerwarteter Fehler beim Lesen der Datei: {e}")

    def parse_json(self, filepath: str) -> List[Dict]:
        """
        Parst eine JSON-Datei und gibt die Daten als Liste von Dictionaries zurück.

        Args:
            filepath (str): Pfad zur JSON-Datei

        Returns:
            List[Dict]: Liste von Dictionaries

        Raises:
            FileNotFoundError: Wenn Datei nicht gefunden wird
            ValueError: Wenn JSON ungültig ist oder kein Array enthält
            ParserError: Wenn Datei nicht gelesen werden kann
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)

                # Sicherstellen, dass es eine Liste ist
                if not isinstance(data, list):
                    raise ValueError("JSON-Datei muss ein Array enthalten")

                return data
        except FileNotFoundError:
            raise  # FileNotFoundError durchlassen
        except json.JSONDecodeError as e:
            raise ValueError(f"Ungültiges JSON-Format: {e}")
        except ValueError:
            raise  # ValueError durchlassen (von "muss ein Array enthalten")
        except PermissionError:
            raise ParserError(f"Permission denied: {filepath}")
        except Exception as e:
            raise ParserError(f"Unerwarteter Fehler beim Lesen der Datei: {e}")


if __name__ == "__main__":
    import tempfile

    parser = FileParser()

    # Beispiel CSV-Datei erstellen und parsen
    print("=== CSV Parser ===")
    csv_content = "name,email,age\nAlice,alice@example.com,30\nBob,bob@example.com,25"

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write(csv_content)
        csv_file = f.name

    csv_data = parser.parse_csv(csv_file)
    print(f"CSV-Daten: {csv_data}")
    os.remove(csv_file)

    # Beispiel JSON-Datei erstellen und parsen
    print("\n=== JSON Parser ===")
    json_content = [
        {"name": "Alice", "email": "alice@example.com", "age": 30},
        {"name": "Bob", "email": "bob@example.com", "age": 25}
    ]

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(json_content, f)
        json_file = f.name

    json_data = parser.parse_json(json_file)
    print(f"JSON-Daten: {json_data}")
    os.remove(json_file)

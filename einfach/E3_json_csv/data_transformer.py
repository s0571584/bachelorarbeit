"""
JSON zu CSV Konverter - Wandelt JSON-Daten in CSV-Format um
"""

import json


def json_to_csv(json_string):
    """
    Konvertiert einen JSON-String in einen CSV-String.

    Args:
        json_string (str): JSON-String mit User-Daten (name, email, age)

    Returns:
        str: CSV-formatierter String

    Raises:
        ValueError: Wenn JSON-String ungültig ist
        TypeError: Wenn Input kein String ist
    """
    if not isinstance(json_string, str):
        raise TypeError("Input muss ein String sein")

    try:
        # JSON-String in Python-Objekt umwandeln
        data = json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Ungültiger JSON-String: {e}")

    # Sicherstellen, dass data eine Liste ist
    if not isinstance(data, list):
        raise ValueError("JSON muss eine Liste von Objekten sein")

    if len(data) == 0:
        return ""

    # Feldnamen aus dem ersten Objekt extrahieren
    headers = list(data[0].keys())
    lines = [",".join(headers)]

    # Datenzeilen erstellen
    for row in data:
        lines.append(",".join(str(row.get(h, "")) for h in headers))

    # PROBLEM: Plattformabhängige Line-Endings
    # Verwendet explizite \n Zeichen, funktioniert nicht korrekt auf Windows
    return "\n".join(lines)


if __name__ == "__main__":
    # Beispiel-Verwendung
    json_data = '''[
        {"name": "Alice", "email": "alice@example.com", "age": 30},
        {"name": "Bob", "email": "bob@example.com", "age": 25},
        {"name": "Charlie", "email": "charlie@example.com", "age": 35}
    ]'''

    csv_data = json_to_csv(json_data)
    print("JSON zu CSV Konvertierung:")
    print(csv_data)

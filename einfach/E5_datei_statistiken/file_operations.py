"""
Datei-Statistiken - Berechnet Statistiken über eine Textdatei
"""

import os


def file_stats(filepath):
    """
    Berechnet Statistiken über eine Textdatei.

    Args:
        filepath (str): Pfad zur Textdatei

    Returns:
        dict: Dictionary mit line_count, word_count, char_count

    Raises:
        FileNotFoundError: Wenn Datei nicht existiert
        TypeError: Wenn filepath kein String ist
    """
    if not isinstance(filepath, str):
        raise TypeError("Filepath muss ein String sein")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Datei nicht gefunden: {filepath}")

    line_count = 0
    word_count = 0
    char_count = 0

    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            line_count += 1
            char_count += len(line)
            # Wörter zählen (durch Leerzeichen getrennt)
            words = line.split()
            word_count += len(words)

    return {
        'line_count': line_count,
        'word_count': word_count,
        'char_count': char_count
    }


if __name__ == "__main__":
    # Beispiel-Verwendung
    # Erstelle eine Test-Datei
    test_file = "test_sample.txt"

    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("Dies ist eine Test-Datei.\n")
        f.write("Sie hat mehrere Zeilen.\n")
        f.write("Und verschiedene Wörter.\n")

    stats = file_stats(test_file)
    print(f"Datei: {test_file}")
    print(f"Zeilen: {stats['line_count']}")
    print(f"Wörter: {stats['word_count']}")
    print(f"Zeichen: {stats['char_count']}")

    # Test-Datei löschen
    os.remove(test_file)

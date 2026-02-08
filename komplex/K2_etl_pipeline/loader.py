"""
Loader - Lädt Daten in SQLite-Datenbank
"""

import sqlite3
from typing import List, Dict
import logging


class Loader:
    """
    Loader - Speichert Daten in einer SQLite-Datenbank
    """

    def __init__(self, db_path: str = ':memory:'):
        """
        Initialisiert den Loader.

        Args:
            db_path (str): Pfad zur Datenbank-Datei
        """
        self.db_path = db_path
        self.connection = None
        self.logger = logging.getLogger(__name__)

    def connect(self):
        """Stellt Verbindung zur Datenbank her"""
        self.connection = sqlite3.connect(self.db_path)
        self.logger.info(f"Verbindung zur Datenbank hergestellt: {self.db_path}")

    def close(self):
        """Schließt die Datenbankverbindung"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.logger.info("Datenbankverbindung geschlossen")

    def create_table(self, table_name: str, schema: Dict[str, str]):
        """
        Erstellt eine Tabelle.

        Args:
            table_name (str): Name der Tabelle
            schema (Dict[str, str]): Schema (Feldname -> SQL-Typ)
        """
        if not self.connection:
            self.connect()

        # SQL-Statement erstellen
        fields = ', '.join([f"{field} {sql_type}" for field, sql_type in schema.items()])
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({fields})"

        cursor = self.connection.cursor()
        cursor.execute(sql)
        self.connection.commit()

        self.logger.info(f"Tabelle '{table_name}' erstellt")

    def load_data(self, table_name: str, data: List[Dict], mode: str = 'append'):
        """
        Lädt Daten in eine Tabelle.

        Args:
            table_name (str): Name der Tabelle
            data (List[Dict]): Zu ladende Daten
            mode (str): 'append' (hinzufügen) oder 'replace' (ersetzen)

        Raises:
            ValueError: Wenn mode ungültig ist
        """
        if not self.connection:
            self.connect()

        if mode not in ['append', 'replace']:
            raise ValueError("Mode muss 'append' oder 'replace' sein")

        if mode == 'replace':
            cursor = self.connection.cursor()
            cursor.execute(f"DELETE FROM {table_name}")
            self.logger.info(f"Tabelle '{table_name}' geleert (replace mode)")

        if not data:
            self.logger.warning("Keine Daten zum Laden")
            return

        # Feldnamen aus erstem Eintrag extrahieren
        fields = list(data[0].keys())
        placeholders = ', '.join(['?' for _ in fields])
        sql = f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({placeholders})"

        cursor = self.connection.cursor()
        inserted_count = 0

        for item in data:
            try:
                values = [item.get(field) for field in fields]
                cursor.execute(sql, values)
                inserted_count += 1
            except Exception as e:
                self.logger.error(f"Fehler beim Einfügen von Daten: {e}")

        self.connection.commit()
        self.logger.info(f"{inserted_count} Einträge in Tabelle '{table_name}' geladen")

    def get_row_count(self, table_name: str) -> int:
        """
        Gibt die Anzahl der Zeilen in einer Tabelle zurück.

        Args:
            table_name (str): Name der Tabelle

        Returns:
            int: Anzahl der Zeilen
        """
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        return count

    def __enter__(self):
        """Context Manager: Öffnet Verbindung"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context Manager: Schließt Verbindung"""
        self.close()


if __name__ == "__main__":
    # Setup Logging
    logging.basicConfig(level=logging.INFO)

    # Beispiel-Verwendung
    with Loader() as loader:
        # Tabelle erstellen
        schema = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name": "TEXT",
            "age": "INTEGER",
            "city": "TEXT"
        }
        loader.create_table("users", schema)

        # Daten laden
        data = [
            {"name": "Alice", "age": 30, "city": "Berlin"},
            {"name": "Bob", "age": 25, "city": "Munich"}
        ]
        loader.load_data("users", data)

        # Anzahl der Zeilen abrufen
        count = loader.get_row_count("users")
        print(f"Anzahl der Zeilen: {count}")

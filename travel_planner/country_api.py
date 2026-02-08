"""
REST Countries API Integration Module

Dieses Modul stellt Funktionen bereit, um Länderinformationen von der
REST Countries API abzurufen.
"""

import requests
from typing import Optional, Dict, Any


class CountryAPIError(Exception):
    """Exception für Fehler bei der Country API Abfrage."""
    pass


class CountryAPI:
    """
    Klasse für die Interaktion mit der REST Countries API.

    Attributes:
        base_url (str): Die Basis-URL der API
    """

    def __init__(self):
        """Initialisiert die CountryAPI mit der Basis-URL."""
        self.base_url = "https://restcountries.com/v3.1"

    def get_country_info(self, country_name: str) -> Dict[str, Any]:
        """
        Ruft Informationen über ein Land ab.

        Args:
            country_name (str): Name des Landes (auf Deutsch oder Englisch)

        Returns:
            Dict[str, Any]: Dictionary mit Länderinformationen:
                - name: Offizieller Name
                - capital: Hauptstadt
                - population: Bevölkerung
                - currencies: Währungen
                - languages: Sprachen
                - coordinates: Koordinaten (lat, lon)

        Raises:
            CountryAPIError: Wenn das Land nicht gefunden wurde oder ein API-Fehler auftritt
        """
        try:
            # Versuche zuerst nach dem Namen zu suchen
            url = f"{self.base_url}/name/{country_name}"
            response = requests.get(url, timeout=10)

            if response.status_code == 404:
                raise CountryAPIError(f"Land '{country_name}' wurde nicht gefunden.")

            response.raise_for_status()
            data = response.json()

            if not data:
                raise CountryAPIError(f"Keine Daten für '{country_name}' gefunden.")

            # Nehme das erste Ergebnis (meist das relevanteste)
            country = data[0]

            return self._parse_country_data(country)

        except requests.exceptions.Timeout:
            raise CountryAPIError("Zeitüberschreitung bei der Verbindung zur API.")
        except requests.exceptions.RequestException as e:
            raise CountryAPIError(f"Fehler bei der API-Anfrage: {str(e)}")
        except (KeyError, IndexError) as e:
            raise CountryAPIError(f"Fehler beim Parsen der API-Antwort: {str(e)}")

    def _parse_country_data(self, country: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parst die Rohdaten der API in ein strukturiertes Format.

        Args:
            country (Dict): Rohdaten von der API

        Returns:
            Dict[str, Any]: Geparste Länderinformationen
        """
        # Extrahiere Name
        name = country.get('name', {}).get('common', 'Unbekannt')
        official_name = country.get('name', {}).get('official', name)

        # Extrahiere Hauptstadt
        capitals = country.get('capital', [])
        capital = capitals[0] if capitals else 'Keine Hauptstadt'

        # Extrahiere Bevölkerung
        population = country.get('population', 0)

        # Extrahiere Währungen
        currencies_data = country.get('currencies', {})
        currencies = []
        for code, info in currencies_data.items():
            currency_name = info.get('name', code)
            symbol = info.get('symbol', '')
            currencies.append(f"{currency_name} ({code}){' ' + symbol if symbol else ''}")

        # Extrahiere Sprachen
        languages_data = country.get('languages', {})
        languages = list(languages_data.values())

        # Extrahiere Koordinaten
        coordinates = country.get('latlng', [0, 0])
        lat = coordinates[0] if len(coordinates) > 0 else 0
        lon = coordinates[1] if len(coordinates) > 1 else 0

        return {
            'name': name,
            'official_name': official_name,
            'capital': capital,
            'population': population,
            'currencies': currencies,
            'languages': languages,
            'coordinates': {
                'latitude': lat,
                'longitude': lon
            }
        }

    def format_country_info(self, info: Dict[str, Any]) -> str:
        """
        Formatiert Länderinformationen als lesbaren Text.

        Args:
            info (Dict): Länderinformationen

        Returns:
            str: Formatierter Text
        """
        lines = [
            f"{'='*60}",
            f"LÄNDERINFORMATIONEN: {info['name'].upper()}",
            f"{'='*60}",
            f"Offizieller Name: {info['official_name']}",
            f"Hauptstadt:       {info['capital']}",
            f"Bevölkerung:      {info['population']:,}".replace(',', '.'),
            f"Währung(en):      {', '.join(info['currencies'])}",
            f"Sprache(n):       {', '.join(info['languages'])}",
            f"Koordinaten:      {info['coordinates']['latitude']:.2f}°N, {info['coordinates']['longitude']:.2f}°E",
            f"{'='*60}"
        ]
        return '\n'.join(lines)

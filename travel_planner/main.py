"""
Travel Weather Planner - Hauptanwendung

Diese Anwendung hilft Benutzern, Reiseziele basierend auf Wetterdaten zu planen.
Sie kombiniert Länderinformationen mit aktuellen Wetterdaten und Vorhersagen.
"""

from country_api import CountryAPI, CountryAPIError
from weather_api import WeatherAPI, WeatherAPIError
import sys


class TravelPlanner:
    """
    Hauptklasse für den Reise-Wetter-Planer.

    Diese Klasse koordiniert die Interaktion zwischen Country API und Weather API
    und stellt die Benutzeroberfläche bereit.
    """

    def __init__(self):
        """Initialisiert den Travel Planner mit API-Instanzen."""
        self.country_api = CountryAPI()
        self.weather_api = WeatherAPI()

    def run(self):
        """
        Startet die Hauptschleife der Anwendung.

        Die Anwendung läuft in einer Schleife, bis der Benutzer sie beendet.
        """
        print("\n" + "="*60)
        print("WILLKOMMEN BEIM REISE-WETTER-PLANER")
        print("="*60)
        print("\nPlanen Sie Ihre Reise mit aktuellen Wetterdaten!")
        print("Geben Sie 'exit' oder 'quit' ein, um das Programm zu beenden.\n")

        while True:
            try:
                # Benutzereingabe
                country_name = input("\nGeben Sie einen Ländernamen ein: ").strip()

                # Exit-Bedingung
                if country_name.lower() in ['exit', 'quit', 'q']:
                    print("\nVielen Dank für die Nutzung des Reise-Wetter-Planers!")
                    print("Auf Wiedersehen!\n")
                    break

                if not country_name:
                    print("⚠ Bitte geben Sie einen Ländernamen ein.")
                    continue

                # Verarbeite Anfrage
                self.process_country(country_name)

            except KeyboardInterrupt:
                print("\n\nProgramm wurde vom Benutzer abgebrochen.")
                print("Auf Wiedersehen!\n")
                break
            except Exception as e:
                print(f"\n⚠ Ein unerwarteter Fehler ist aufgetreten: {str(e)}")
                print("Bitte versuchen Sie es erneut.\n")

    def process_country(self, country_name: str):
        """
        Verarbeitet eine Länderanfrage und zeigt alle relevanten Informationen an.

        Args:
            country_name (str): Name des Landes

        Diese Methode:
        1. Ruft Länderinformationen ab
        2. Ruft Wetterdaten für die Hauptstadt ab
        3. Zeigt aktuelle Wetterbedingungen
        4. Zeigt 7-Tage Vorhersage
        5. Gibt eine Reiseempfehlung
        """
        try:
            # Schritt 1: Länderinformationen abrufen
            print(f"\n🔍 Suche Informationen über '{country_name}'...")
            country_info = self.country_api.get_country_info(country_name)
            print(self.country_api.format_country_info(country_info))

            # Schritt 2: Wetterdaten abrufen
            print(f"\n🌤 Rufe Wetterdaten für {country_info['capital']} ab...")
            weather_data = self.weather_api.get_weather_forecast(
                country_info['coordinates']['latitude'],
                country_info['coordinates']['longitude']
            )

            # Schritt 3: Aktuelles Wetter anzeigen
            print(self.weather_api.format_current_weather(weather_data['current']))

            # Schritt 4: 7-Tage Vorhersage anzeigen
            print(self.weather_api.format_daily_forecast(weather_data['daily']))

            # Schritt 5: Reiseempfehlung generieren und anzeigen
            recommendation = self.weather_api.get_travel_recommendation(weather_data['daily'])
            print(self.weather_api.format_recommendation(recommendation))

        except CountryAPIError as e:
            print(f"\n❌ Fehler bei der Ländersuche: {str(e)}")
            print("Tipp: Versuchen Sie es mit dem englischen Namen oder einer alternativen Schreibweise.")
        except WeatherAPIError as e:
            print(f"\n❌ Fehler beim Abrufen der Wetterdaten: {str(e)}")
        except Exception as e:
            print(f"\n❌ Ein unerwarteter Fehler ist aufgetreten: {str(e)}")

    def get_country_weather(self, country_name: str) -> dict:
        """
        Ruft Länder- und Wetterdaten ab und gibt sie als Dictionary zurück.

        Diese Methode ist nützlich für Tests und programmatische Nutzung.

        Args:
            country_name (str): Name des Landes

        Returns:
            dict: Dictionary mit 'country', 'weather' und 'recommendation' Keys

        Raises:
            CountryAPIError: Wenn Länderinformationen nicht abgerufen werden können
            WeatherAPIError: Wenn Wetterdaten nicht abgerufen werden können
        """
        country_info = self.country_api.get_country_info(country_name)
        weather_data = self.weather_api.get_weather_forecast(
            country_info['coordinates']['latitude'],
            country_info['coordinates']['longitude']
        )
        recommendation = self.weather_api.get_travel_recommendation(weather_data['daily'])

        return {
            'country': country_info,
            'weather': weather_data,
            'recommendation': recommendation
        }


def main():
    """
    Einstiegspunkt der Anwendung.

    Erstellt eine TravelPlanner-Instanz und startet die Hauptschleife.
    """
    planner = TravelPlanner()
    planner.run()


if __name__ == "__main__":
    main()

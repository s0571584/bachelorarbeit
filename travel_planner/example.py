"""
Beispiel-Skript für die programmatische Nutzung des Travel Planners

Dieses Skript zeigt, wie der Travel Planner ohne interaktive Eingabe
verwendet werden kann.
"""

from main import TravelPlanner
from country_api import CountryAPIError
from weather_api import WeatherAPIError


def get_travel_info_for_countries(countries):
    """
    Ruft Reiseinformationen für mehrere Länder ab.

    Args:
        countries (list): Liste von Ländernamen
    """
    planner = TravelPlanner()

    results = {}

    for country in countries:
        print(f"\n{'='*60}")
        print(f"Verarbeite: {country}")
        print(f"{'='*60}")

        try:
            # Hole Daten
            data = planner.get_country_weather(country)

            # Speichere Ergebnisse
            results[country] = {
                'success': True,
                'score': data['recommendation']['score'],
                'rating': data['recommendation']['rating'],
                'capital': data['country']['capital'],
                'avg_temp': data['recommendation']['avg_temp']
            }

            # Zeige Zusammenfassung
            print(f"✓ {country} - {data['country']['capital']}")
            print(f"  Score: {data['recommendation']['score']}/100")
            print(f"  Rating: {data['recommendation']['rating']}")
            print(f"  Durchschnittstemperatur: {data['recommendation']['avg_temp']:.1f}°C")

        except (CountryAPIError, WeatherAPIError) as e:
            results[country] = {
                'success': False,
                'error': str(e)
            }
            print(f"✗ Fehler bei {country}: {str(e)}")

    return results


def compare_destinations(countries):
    """
    Vergleicht mehrere Reiseziele und gibt die beste Empfehlung.

    Args:
        countries (list): Liste von Ländernamen
    """
    print("\n" + "="*60)
    print("REISEZIELE-VERGLEICH")
    print("="*60)

    results = get_travel_info_for_countries(countries)

    # Finde bestes Reiseziel
    best_destination = None
    best_score = -1

    for country, data in results.items():
        if data['success'] and data['score'] > best_score:
            best_score = data['score']
            best_destination = country

    # Zeige Empfehlung
    print("\n" + "="*60)
    print("BESTE REISEEMPFEHLUNG")
    print("="*60)

    if best_destination:
        result = results[best_destination]
        print(f"\n🏆 {best_destination} - {result['capital']}")
        print(f"   Score: {result['score']}/100")
        print(f"   Rating: {result['rating']}")
        print(f"   Durchschnittstemperatur: {result['avg_temp']:.1f}°C")
    else:
        print("\n⚠ Keine gültigen Reiseziele gefunden.")

    print("\n" + "="*60)


def main():
    """Hauptfunktion für Beispiele."""

    # Beispiel 1: Einzelnes Land
    print("\n*** BEISPIEL 1: Einzelnes Land ***")
    planner = TravelPlanner()

    try:
        data = planner.get_country_weather("Germany")
        print(f"\nLand: {data['country']['name']}")
        print(f"Hauptstadt: {data['country']['capital']}")
        print(f"Aktuelle Temperatur: {data['weather']['current']['temperature']:.1f}°C")
        print(f"Reise-Score: {data['recommendation']['score']}/100")
    except Exception as e:
        print(f"Fehler: {e}")

    # Beispiel 2: Mehrere Länder vergleichen
    print("\n\n*** BEISPIEL 2: Mehrere Länder vergleichen ***")
    destinations = ["Germany", "France", "Spain", "Italy"]
    compare_destinations(destinations)


if __name__ == "__main__":
    main()

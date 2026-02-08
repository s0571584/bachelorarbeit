"""
Open-Meteo Weather API Integration Module

Dieses Modul stellt Funktionen bereit, um Wetterdaten von der
Open-Meteo API abzurufen.
"""

import requests
from typing import Dict, Any, List
from datetime import datetime


class WeatherAPIError(Exception):
    """Exception für Fehler bei der Weather API Abfrage."""
    pass


class WeatherAPI:
    """
    Klasse für die Interaktion mit der Open-Meteo API.

    Attributes:
        base_url (str): Die Basis-URL der API
    """

    def __init__(self):
        """Initialisiert die WeatherAPI mit der Basis-URL."""
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    def get_weather_forecast(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Ruft Wetterdaten für bestimmte Koordinaten ab.

        Args:
            latitude (float): Breitengrad
            longitude (float): Längengrad

        Returns:
            Dict[str, Any]: Dictionary mit Wetterdaten:
                - current: Aktuelles Wetter
                - daily: 7-Tage Vorhersage

        Raises:
            WeatherAPIError: Wenn ein API-Fehler auftritt
        """
        try:
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'current': 'temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m',
                'daily': 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max',
                'timezone': 'auto'
            }

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            return self._parse_weather_data(data)

        except requests.exceptions.Timeout:
            raise WeatherAPIError("Zeitüberschreitung bei der Verbindung zur Wetter-API.")
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"Fehler bei der Wetter-API-Anfrage: {str(e)}")
        except (KeyError, IndexError) as e:
            raise WeatherAPIError(f"Fehler beim Parsen der Wetter-API-Antwort: {str(e)}")

    def _parse_weather_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parst die Rohdaten der Weather API.

        Args:
            data (Dict): Rohdaten von der API

        Returns:
            Dict[str, Any]: Geparste Wetterdaten
        """
        current = data.get('current', {})
        daily = data.get('daily', {})

        # Parse current weather
        current_weather = {
            'temperature': current.get('temperature_2m', 0),
            'humidity': current.get('relative_humidity_2m', 0),
            'precipitation': current.get('precipitation', 0),
            'wind_speed': current.get('wind_speed_10m', 0),
            'weather_code': current.get('weather_code', 0),
            'description': self._get_weather_description(current.get('weather_code', 0))
        }

        # Parse daily forecast
        daily_forecast = []
        dates = daily.get('time', [])
        temp_max = daily.get('temperature_2m_max', [])
        temp_min = daily.get('temperature_2m_min', [])
        precipitation = daily.get('precipitation_sum', [])
        wind_speed = daily.get('wind_speed_10m_max', [])
        weather_codes = daily.get('weather_code', [])

        for i in range(min(7, len(dates))):  # 7-Tage Vorhersage
            daily_forecast.append({
                'date': dates[i],
                'temp_max': temp_max[i] if i < len(temp_max) else 0,
                'temp_min': temp_min[i] if i < len(temp_min) else 0,
                'precipitation': precipitation[i] if i < len(precipitation) else 0,
                'wind_speed': wind_speed[i] if i < len(wind_speed) else 0,
                'weather_code': weather_codes[i] if i < len(weather_codes) else 0,
                'description': self._get_weather_description(weather_codes[i] if i < len(weather_codes) else 0)
            })

        return {
            'current': current_weather,
            'daily': daily_forecast
        }

    def _get_weather_description(self, code: int) -> str:
        """
        Konvertiert WMO Weather Code in eine lesbare Beschreibung.

        Args:
            code (int): WMO Weather Code

        Returns:
            str: Wetterbeschreibung auf Deutsch
        """
        weather_codes = {
            0: 'Klar',
            1: 'Überwiegend klar',
            2: 'Teilweise bewölkt',
            3: 'Bewölkt',
            45: 'Nebelig',
            48: 'Gefrierender Nebel',
            51: 'Leichter Nieselregen',
            53: 'Mäßiger Nieselregen',
            55: 'Starker Nieselregen',
            56: 'Leichter gefrierender Nieselregen',
            57: 'Starker gefrierender Nieselregen',
            61: 'Leichter Regen',
            63: 'Mäßiger Regen',
            65: 'Starker Regen',
            66: 'Leichter gefrierender Regen',
            67: 'Starker gefrierender Regen',
            71: 'Leichter Schneefall',
            73: 'Mäßiger Schneefall',
            75: 'Starker Schneefall',
            77: 'Schneegriesel',
            80: 'Leichte Regenschauer',
            81: 'Mäßige Regenschauer',
            82: 'Starke Regenschauer',
            85: 'Leichte Schneeschauer',
            86: 'Starke Schneeschauer',
            95: 'Gewitter',
            96: 'Gewitter mit leichtem Hagel',
            99: 'Gewitter mit starkem Hagel'
        }
        return weather_codes.get(code, 'Unbekannt')

    def format_current_weather(self, weather: Dict[str, Any]) -> str:
        """
        Formatiert aktuelles Wetter als lesbaren Text.

        Args:
            weather (Dict): Aktuelle Wetterdaten

        Returns:
            str: Formatierter Text
        """
        lines = [
            f"\n{'='*60}",
            f"AKTUELLES WETTER",
            f"{'='*60}",
            f"Bedingungen:      {weather['description']}",
            f"Temperatur:       {weather['temperature']:.1f}°C",
            f"Luftfeuchtigkeit: {weather['humidity']:.0f}%",
            f"Niederschlag:     {weather['precipitation']:.1f} mm",
            f"Windgeschw.:      {weather['wind_speed']:.1f} km/h",
            f"{'='*60}"
        ]
        return '\n'.join(lines)

    def format_daily_forecast(self, forecast: List[Dict[str, Any]]) -> str:
        """
        Formatiert 7-Tage Wettervorhersage als lesbaren Text.

        Args:
            forecast (List[Dict]): Liste mit täglichen Wettervorhersagen

        Returns:
            str: Formatierter Text
        """
        lines = [
            f"\n{'='*60}",
            f"7-TAGE WETTERVORHERSAGE",
            f"{'='*60}"
        ]

        for day in forecast:
            date = datetime.strptime(day['date'], '%Y-%m-%d')
            day_name = self._get_german_day_name(date.weekday())
            date_str = date.strftime('%d.%m.%Y')

            lines.extend([
                f"\n{day_name}, {date_str}",
                f"-" * 40,
                f"Wetter:           {day['description']}",
                f"Temperatur:       {day['temp_min']:.1f}°C - {day['temp_max']:.1f}°C",
                f"Niederschlag:     {day['precipitation']:.1f} mm",
                f"Wind:             {day['wind_speed']:.1f} km/h"
            ])

        lines.append(f"{'='*60}")
        return '\n'.join(lines)

    def _get_german_day_name(self, weekday: int) -> str:
        """
        Konvertiert Wochentag-Nummer in deutschen Namen.

        Args:
            weekday (int): Wochentag (0=Montag, 6=Sonntag)

        Returns:
            str: Deutscher Wochentag-Name
        """
        days = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
        return days[weekday] if 0 <= weekday < 7 else 'Unbekannt'

    def get_travel_recommendation(self, forecast: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generiert eine Reiseempfehlung basierend auf der Wettervorhersage.

        Args:
            forecast (List[Dict]): 7-Tage Wettervorhersage

        Returns:
            Dict[str, Any]: Reiseempfehlung mit Score und Begründung
        """
        if not forecast:
            return {
                'score': 0,
                'rating': 'Unbekannt',
                'recommendation': 'Keine Wetterdaten verfügbar.'
            }

        # Berechne Durchschnittswerte
        avg_temp = sum(day['temp_max'] for day in forecast) / len(forecast)
        total_precipitation = sum(day['precipitation'] for day in forecast)
        avg_wind = sum(day['wind_speed'] for day in forecast) / len(forecast)

        # Zähle gute und schlechte Tage
        good_days = 0
        bad_days = 0

        for day in forecast:
            # Guter Tag: 15-28°C, < 5mm Regen, < 30 km/h Wind
            if 15 <= day['temp_max'] <= 28 and day['precipitation'] < 5 and day['wind_speed'] < 30:
                good_days += 1
            # Schlechter Tag: < 5°C oder > 35°C, > 20mm Regen, oder > 50 km/h Wind
            elif day['temp_max'] < 5 or day['temp_max'] > 35 or day['precipitation'] > 20 or day['wind_speed'] > 50:
                bad_days += 1

        # Berechne Score (0-100)
        score = 50  # Basis-Score

        # Temperatur-Faktor
        if 18 <= avg_temp <= 25:
            score += 20
        elif 15 <= avg_temp <= 28:
            score += 10
        elif avg_temp < 5 or avg_temp > 35:
            score -= 20
        elif avg_temp < 10 or avg_temp > 30:
            score -= 10

        # Niederschlags-Faktor
        if total_precipitation < 10:
            score += 20
        elif total_precipitation < 30:
            score += 10
        elif total_precipitation > 100:
            score -= 20
        elif total_precipitation > 50:
            score -= 10

        # Wind-Faktor
        if avg_wind < 20:
            score += 10
        elif avg_wind > 40:
            score -= 10

        # Gute/Schlechte Tage Faktor
        score += good_days * 5
        score -= bad_days * 10

        # Normalisiere Score
        score = max(0, min(100, score))

        # Bestimme Rating
        if score >= 80:
            rating = 'Ausgezeichnet'
            emoji = '⭐⭐⭐⭐⭐'
        elif score >= 60:
            rating = 'Gut'
            emoji = '⭐⭐⭐⭐'
        elif score >= 40:
            rating = 'Mäßig'
            emoji = '⭐⭐⭐'
        elif score >= 20:
            rating = 'Nicht ideal'
            emoji = '⭐⭐'
        else:
            rating = 'Ungünstig'
            emoji = '⭐'

        # Erstelle Empfehlung
        reasons = []

        if avg_temp >= 18 and avg_temp <= 25:
            reasons.append("Angenehme Temperaturen")
        elif avg_temp < 10:
            reasons.append("Kalte Temperaturen - warme Kleidung einpacken")
        elif avg_temp > 30:
            reasons.append("Hohe Temperaturen - Sonnenschutz nicht vergessen")

        if total_precipitation < 10:
            reasons.append("Wenig Regen erwartet")
        elif total_precipitation > 50:
            reasons.append("Viel Regen erwartet - Regenschutz empfohlen")

        if good_days >= 5:
            reasons.append(f"{good_days} gute Wetter-Tage")
        elif bad_days >= 3:
            reasons.append(f"{bad_days} ungünstige Wetter-Tage")

        if avg_wind > 40:
            reasons.append("Starke Winde erwartet")

        recommendation_text = f"{rating} {emoji} (Score: {score}/100)\n"
        if reasons:
            recommendation_text += "\n" + "\n".join(f"  • {reason}" for reason in reasons)

        return {
            'score': score,
            'rating': rating,
            'recommendation': recommendation_text,
            'good_days': good_days,
            'bad_days': bad_days,
            'avg_temp': avg_temp,
            'total_precipitation': total_precipitation
        }

    def format_recommendation(self, recommendation: Dict[str, Any]) -> str:
        """
        Formatiert Reiseempfehlung als lesbaren Text.

        Args:
            recommendation (Dict): Reiseempfehlung

        Returns:
            str: Formatierter Text
        """
        lines = [
            f"\n{'='*60}",
            f"REISEEMPFEHLUNG",
            f"{'='*60}",
            recommendation['recommendation'],
            f"{'='*60}"
        ]
        return '\n'.join(lines)

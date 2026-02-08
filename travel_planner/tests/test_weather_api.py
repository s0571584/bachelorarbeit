"""
Unit Tests für das Weather API Modul

Diese Tests überprüfen die Funktionalität der WeatherAPI-Klasse.
"""

import unittest
from unittest.mock import patch, Mock
import sys
import os

# Füge Parent-Verzeichnis zum Path hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from weather_api import WeatherAPI, WeatherAPIError


class TestWeatherAPI(unittest.TestCase):
    """Test-Klasse für WeatherAPI."""

    def setUp(self):
        """Wird vor jedem Test ausgeführt."""
        self.api = WeatherAPI()

    @patch('weather_api.requests.get')
    def test_get_weather_forecast_success(self, mock_get):
        """Test: Erfolgreicher Abruf von Wetterdaten."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'current': {
                'temperature_2m': 20.5,
                'relative_humidity_2m': 65,
                'precipitation': 0.0,
                'weather_code': 1,
                'wind_speed_10m': 15.0
            },
            'daily': {
                'time': ['2024-01-01', '2024-01-02'],
                'temperature_2m_max': [22.0, 23.0],
                'temperature_2m_min': [15.0, 16.0],
                'precipitation_sum': [0.0, 2.5],
                'wind_speed_10m_max': [20.0, 18.0],
                'weather_code': [1, 61]
            }
        }
        mock_get.return_value = mock_response

        # Test
        result = self.api.get_weather_forecast(51.0, 9.0)

        # Assertions
        self.assertIn('current', result)
        self.assertIn('daily', result)
        self.assertEqual(result['current']['temperature'], 20.5)
        self.assertEqual(result['current']['humidity'], 65)
        self.assertEqual(len(result['daily']), 2)

    @patch('weather_api.requests.get')
    def test_get_weather_forecast_timeout(self, mock_get):
        """Test: Timeout bei API-Anfrage."""
        # Mock timeout
        import requests
        mock_get.side_effect = requests.exceptions.Timeout('Timeout')

        # Test
        with self.assertRaises(WeatherAPIError):
            self.api.get_weather_forecast(51.0, 9.0)

    def test_get_weather_description(self):
        """Test: Konvertierung von Weather Codes in Beschreibungen."""
        test_cases = [
            (0, 'Klar'),
            (1, 'Überwiegend klar'),
            (61, 'Leichter Regen'),
            (95, 'Gewitter'),
            (999, 'Unbekannt')  # Unbekannter Code
        ]

        for code, expected in test_cases:
            result = self.api._get_weather_description(code)
            self.assertEqual(result, expected)

    def test_format_current_weather(self):
        """Test: Formatierung von aktuellem Wetter."""
        weather = {
            'temperature': 20.5,
            'humidity': 65,
            'precipitation': 0.0,
            'wind_speed': 15.0,
            'weather_code': 1,
            'description': 'Überwiegend klar'
        }

        result = self.api.format_current_weather(weather)

        self.assertIn('AKTUELLES WETTER', result)
        self.assertIn('20.5', result)
        self.assertIn('65', result)
        self.assertIn('Überwiegend klar', result)

    def test_format_daily_forecast(self):
        """Test: Formatierung der Tagesvorhersage."""
        forecast = [
            {
                'date': '2024-01-01',
                'temp_max': 22.0,
                'temp_min': 15.0,
                'precipitation': 0.0,
                'wind_speed': 20.0,
                'weather_code': 1,
                'description': 'Überwiegend klar'
            }
        ]

        result = self.api.format_daily_forecast(forecast)

        self.assertIn('7-TAGE WETTERVORHERSAGE', result)
        self.assertIn('01.01.2024', result)
        self.assertIn('Überwiegend klar', result)

    def test_get_german_day_name(self):
        """Test: Konvertierung von Wochentag-Nummern."""
        test_cases = [
            (0, 'Montag'),
            (1, 'Dienstag'),
            (6, 'Sonntag'),
            (7, 'Unbekannt')  # Ungültiger Wert
        ]

        for weekday, expected in test_cases:
            result = self.api._get_german_day_name(weekday)
            self.assertEqual(result, expected)

    def test_get_travel_recommendation_excellent(self):
        """Test: Reiseempfehlung für ausgezeichnetes Wetter."""
        # Perfektes Wetter: 20-25°C, kein Regen, wenig Wind
        forecast = [
            {
                'date': f'2024-01-0{i}',
                'temp_max': 22.0,
                'temp_min': 18.0,
                'precipitation': 0.0,
                'wind_speed': 10.0,
                'weather_code': 0,
                'description': 'Klar'
            }
            for i in range(1, 8)
        ]

        result = self.api.get_travel_recommendation(forecast)

        self.assertGreater(result['score'], 70)
        self.assertIn('rating', result)
        self.assertIn('recommendation', result)
        self.assertEqual(result['good_days'], 7)

    def test_get_travel_recommendation_poor(self):
        """Test: Reiseempfehlung für schlechtes Wetter."""
        # Schlechtes Wetter: kalt, viel Regen, starker Wind
        forecast = [
            {
                'date': f'2024-01-0{i}',
                'temp_max': 3.0,
                'temp_min': -2.0,
                'precipitation': 25.0,
                'wind_speed': 55.0,
                'weather_code': 65,
                'description': 'Starker Regen'
            }
            for i in range(1, 8)
        ]

        result = self.api.get_travel_recommendation(forecast)

        self.assertLess(result['score'], 40)
        self.assertEqual(result['bad_days'], 7)

    def test_get_travel_recommendation_empty(self):
        """Test: Reiseempfehlung mit leeren Daten."""
        forecast = []

        result = self.api.get_travel_recommendation(forecast)

        self.assertEqual(result['score'], 0)
        self.assertEqual(result['rating'], 'Unbekannt')

    def test_format_recommendation(self):
        """Test: Formatierung der Reiseempfehlung."""
        recommendation = {
            'score': 85,
            'rating': 'Ausgezeichnet',
            'recommendation': 'Perfektes Reisewetter!',
            'good_days': 6,
            'bad_days': 0,
            'avg_temp': 22.0,
            'total_precipitation': 5.0
        }

        result = self.api.format_recommendation(recommendation)

        self.assertIn('REISEEMPFEHLUNG', result)
        self.assertIn('Perfektes Reisewetter!', result)


class TestWeatherAPIIntegration(unittest.TestCase):
    """Integrationstests für WeatherAPI (benötigen Internetverbindung)."""

    def setUp(self):
        """Wird vor jedem Test ausgeführt."""
        self.api = WeatherAPI()

    @unittest.skip("Integration test - requires internet connection")
    def test_real_api_call_berlin(self):
        """Test: Echter API-Aufruf für Berlin."""
        # Berlin Koordinaten
        result = self.api.get_weather_forecast(52.52, 13.41)

        self.assertIsNotNone(result)
        self.assertIn('current', result)
        self.assertIn('daily', result)
        self.assertGreater(len(result['daily']), 0)


if __name__ == '__main__':
    unittest.main()

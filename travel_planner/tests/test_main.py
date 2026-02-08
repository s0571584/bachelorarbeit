"""
Unit Tests für die Hauptanwendung

Diese Tests überprüfen die Funktionalität der TravelPlanner-Klasse.
"""

import unittest
from unittest.mock import patch, Mock, MagicMock
import sys
import os

# Füge Parent-Verzeichnis zum Path hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import TravelPlanner
from country_api import CountryAPIError
from weather_api import WeatherAPIError


class TestTravelPlanner(unittest.TestCase):
    """Test-Klasse für TravelPlanner."""

    def setUp(self):
        """Wird vor jedem Test ausgeführt."""
        self.planner = TravelPlanner()

    @patch('main.WeatherAPI')
    @patch('main.CountryAPI')
    def test_get_country_weather_success(self, mock_country_api, mock_weather_api):
        """Test: Erfolgreicher Abruf von Länder- und Wetterdaten."""
        # Mock Country API
        mock_country_instance = Mock()
        mock_country_instance.get_country_info.return_value = {
            'name': 'Germany',
            'official_name': 'Federal Republic of Germany',
            'capital': 'Berlin',
            'population': 83000000,
            'currencies': ['Euro (EUR) €'],
            'languages': ['German'],
            'coordinates': {'latitude': 51.0, 'longitude': 9.0}
        }
        mock_country_api.return_value = mock_country_instance

        # Mock Weather API
        mock_weather_instance = Mock()
        mock_weather_instance.get_weather_forecast.return_value = {
            'current': {
                'temperature': 20.5,
                'humidity': 65,
                'precipitation': 0.0,
                'wind_speed': 15.0,
                'weather_code': 1,
                'description': 'Überwiegend klar'
            },
            'daily': [
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
        }
        mock_weather_instance.get_travel_recommendation.return_value = {
            'score': 85,
            'rating': 'Ausgezeichnet',
            'recommendation': 'Perfektes Reisewetter!'
        }
        mock_weather_api.return_value = mock_weather_instance

        # Erstelle neue Instanz mit Mocks
        planner = TravelPlanner()

        # Test
        result = planner.get_country_weather('Germany')

        # Assertions
        self.assertIn('country', result)
        self.assertIn('weather', result)
        self.assertIn('recommendation', result)
        self.assertEqual(result['country']['name'], 'Germany')
        self.assertEqual(result['weather']['current']['temperature'], 20.5)

    @patch('main.WeatherAPI')
    @patch('main.CountryAPI')
    def test_get_country_weather_country_not_found(self, mock_country_api, mock_weather_api):
        """Test: Land nicht gefunden."""
        # Mock Country API - wirft Fehler
        mock_country_instance = Mock()
        mock_country_instance.get_country_info.side_effect = CountryAPIError("Land nicht gefunden")
        mock_country_api.return_value = mock_country_instance

        # Erstelle neue Instanz mit Mock
        planner = TravelPlanner()

        # Test
        with self.assertRaises(CountryAPIError):
            planner.get_country_weather('NonexistentCountry')

    @patch('main.WeatherAPI')
    @patch('main.CountryAPI')
    def test_get_country_weather_weather_error(self, mock_country_api, mock_weather_api):
        """Test: Fehler beim Abrufen der Wetterdaten."""
        # Mock Country API - erfolgreich
        mock_country_instance = Mock()
        mock_country_instance.get_country_info.return_value = {
            'name': 'Germany',
            'capital': 'Berlin',
            'coordinates': {'latitude': 51.0, 'longitude': 9.0}
        }
        mock_country_api.return_value = mock_country_instance

        # Mock Weather API - wirft Fehler
        mock_weather_instance = Mock()
        mock_weather_instance.get_weather_forecast.side_effect = WeatherAPIError("API Fehler")
        mock_weather_api.return_value = mock_weather_instance

        # Erstelle neue Instanz mit Mocks
        planner = TravelPlanner()

        # Test
        with self.assertRaises(WeatherAPIError):
            planner.get_country_weather('Germany')

    @patch('builtins.print')
    @patch('main.WeatherAPI')
    @patch('main.CountryAPI')
    def test_process_country_success(self, mock_country_api, mock_weather_api, mock_print):
        """Test: Erfolgreiche Verarbeitung einer Länderanfrage."""
        # Mock Country API
        mock_country_instance = Mock()
        mock_country_instance.get_country_info.return_value = {
            'name': 'Germany',
            'official_name': 'Federal Republic of Germany',
            'capital': 'Berlin',
            'population': 83000000,
            'currencies': ['Euro (EUR) €'],
            'languages': ['German'],
            'coordinates': {'latitude': 51.0, 'longitude': 9.0}
        }
        mock_country_instance.format_country_info.return_value = "Country Info"
        mock_country_api.return_value = mock_country_instance

        # Mock Weather API
        mock_weather_instance = Mock()
        mock_weather_instance.get_weather_forecast.return_value = {
            'current': {'temperature': 20.5},
            'daily': [{'date': '2024-01-01'}]
        }
        mock_weather_instance.format_current_weather.return_value = "Current Weather"
        mock_weather_instance.format_daily_forecast.return_value = "Forecast"
        mock_weather_instance.get_travel_recommendation.return_value = {
            'score': 85,
            'rating': 'Ausgezeichnet'
        }
        mock_weather_instance.format_recommendation.return_value = "Recommendation"
        mock_weather_api.return_value = mock_weather_instance

        # Erstelle neue Instanz mit Mocks
        planner = TravelPlanner()

        # Test
        planner.process_country('Germany')

        # Verify that APIs were called
        mock_country_instance.get_country_info.assert_called_once_with('Germany')
        mock_weather_instance.get_weather_forecast.assert_called_once()

    @patch('builtins.print')
    @patch('main.CountryAPI')
    def test_process_country_not_found(self, mock_country_api, mock_print):
        """Test: Verarbeitung wenn Land nicht gefunden wird."""
        # Mock Country API - wirft Fehler
        mock_country_instance = Mock()
        mock_country_instance.get_country_info.side_effect = CountryAPIError("Land nicht gefunden")
        mock_country_api.return_value = mock_country_instance

        # Erstelle neue Instanz mit Mock
        planner = TravelPlanner()

        # Test - sollte nicht crashen
        planner.process_country('NonexistentCountry')

        # Verify error was printed
        mock_print.assert_called()

    @patch('builtins.input', side_effect=['Germany', 'exit'])
    @patch('builtins.print')
    @patch('main.TravelPlanner.process_country')
    def test_run_with_exit(self, mock_process, mock_print, mock_input):
        """Test: Hauptschleife mit exit."""
        planner = TravelPlanner()

        # Test
        planner.run()

        # Verify process_country was called for Germany
        mock_process.assert_called_once_with('Germany')

    @patch('builtins.input', side_effect=['quit'])
    @patch('builtins.print')
    def test_run_with_quit(self, mock_print, mock_input):
        """Test: Hauptschleife mit quit."""
        planner = TravelPlanner()

        # Test
        planner.run()

        # Verify welcome message was printed
        mock_print.assert_called()


class TestTravelPlannerIntegration(unittest.TestCase):
    """Integrationstests für TravelPlanner (benötigen Internetverbindung)."""

    def setUp(self):
        """Wird vor jedem Test ausgeführt."""
        self.planner = TravelPlanner()

    @unittest.skip("Integration test - requires internet connection")
    def test_real_full_workflow_germany(self):
        """Test: Vollständiger Workflow mit echten API-Aufrufen für Deutschland."""
        result = self.planner.get_country_weather('Germany')

        self.assertIsNotNone(result)
        self.assertIn('country', result)
        self.assertIn('weather', result)
        self.assertIn('recommendation', result)
        self.assertEqual(result['country']['capital'], 'Berlin')


if __name__ == '__main__':
    unittest.main()

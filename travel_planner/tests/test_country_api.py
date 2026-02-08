"""
Unit Tests für das Country API Modul

Diese Tests überprüfen die Funktionalität der CountryAPI-Klasse.
"""

import unittest
from unittest.mock import patch, Mock
import sys
import os

# Füge Parent-Verzeichnis zum Path hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from country_api import CountryAPI, CountryAPIError


class TestCountryAPI(unittest.TestCase):
    """Test-Klasse für CountryAPI."""

    def setUp(self):
        """Wird vor jedem Test ausgeführt."""
        self.api = CountryAPI()

    @patch('country_api.requests.get')
    def test_get_country_info_success(self, mock_get):
        """Test: Erfolgreicher Abruf von Länderinformationen."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            'name': {
                'common': 'Germany',
                'official': 'Federal Republic of Germany'
            },
            'capital': ['Berlin'],
            'population': 83000000,
            'currencies': {
                'EUR': {'name': 'Euro', 'symbol': '€'}
            },
            'languages': {
                'deu': 'German'
            },
            'latlng': [51.0, 9.0]
        }]
        mock_get.return_value = mock_response

        # Test
        result = self.api.get_country_info('Germany')

        # Assertions
        self.assertEqual(result['name'], 'Germany')
        self.assertEqual(result['official_name'], 'Federal Republic of Germany')
        self.assertEqual(result['capital'], 'Berlin')
        self.assertEqual(result['population'], 83000000)
        self.assertIn('Euro', result['currencies'][0])
        self.assertIn('German', result['languages'])
        self.assertEqual(result['coordinates']['latitude'], 51.0)
        self.assertEqual(result['coordinates']['longitude'], 9.0)

    @patch('country_api.requests.get')
    def test_get_country_info_not_found(self, mock_get):
        """Test: Land wurde nicht gefunden."""
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Test
        with self.assertRaises(CountryAPIError) as context:
            self.api.get_country_info('NonexistentCountry')

        self.assertIn('nicht gefunden', str(context.exception))

    @patch('country_api.requests.get')
    def test_get_country_info_timeout(self, mock_get):
        """Test: Timeout bei API-Anfrage."""
        # Mock timeout
        import requests
        mock_get.side_effect = requests.exceptions.Timeout('Timeout')

        # Test
        with self.assertRaises(CountryAPIError):
            self.api.get_country_info('Germany')

    def test_parse_country_data(self):
        """Test: Parsen von Länder-Rohdaten."""
        raw_data = {
            'name': {
                'common': 'France',
                'official': 'French Republic'
            },
            'capital': ['Paris'],
            'population': 67000000,
            'currencies': {
                'EUR': {'name': 'Euro', 'symbol': '€'}
            },
            'languages': {
                'fra': 'French'
            },
            'latlng': [46.0, 2.0]
        }

        result = self.api._parse_country_data(raw_data)

        self.assertEqual(result['name'], 'France')
        self.assertEqual(result['capital'], 'Paris')
        self.assertEqual(result['population'], 67000000)

    def test_format_country_info(self):
        """Test: Formatierung von Länderinformationen."""
        info = {
            'name': 'Germany',
            'official_name': 'Federal Republic of Germany',
            'capital': 'Berlin',
            'population': 83000000,
            'currencies': ['Euro (EUR) €'],
            'languages': ['German'],
            'coordinates': {'latitude': 51.0, 'longitude': 9.0}
        }

        result = self.api.format_country_info(info)

        self.assertIn('GERMANY', result)
        self.assertIn('Berlin', result)
        self.assertIn('Euro', result)
        self.assertIn('German', result)


class TestCountryAPIIntegration(unittest.TestCase):
    """Integrationstests für CountryAPI (benötigen Internetverbindung)."""

    def setUp(self):
        """Wird vor jedem Test ausgeführt."""
        self.api = CountryAPI()

    @unittest.skip("Integration test - requires internet connection")
    def test_real_api_call_germany(self):
        """Test: Echter API-Aufruf für Deutschland."""
        result = self.api.get_country_info('Germany')

        self.assertIsNotNone(result)
        self.assertIn('Germany', result['name'])
        self.assertIn('Berlin', result['capital'])
        self.assertGreater(result['population'], 0)

    @unittest.skip("Integration test - requires internet connection")
    def test_real_api_call_france(self):
        """Test: Echter API-Aufruf für Frankreich."""
        result = self.api.get_country_info('France')

        self.assertIsNotNone(result)
        self.assertIn('France', result['name'])
        self.assertIn('Paris', result['capital'])


if __name__ == '__main__':
    unittest.main()

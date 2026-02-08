"""
Unit Tests for CountryAPI

Tests using mocked HTTP requests.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import Mock, patch
import requests
from country_api import CountryAPI


class TestCountryAPI:
    """Tests for CountryAPI with mocked requests"""

    def test_init_default_values(self):
        """Test initialization with default values"""
        api = CountryAPI()
        assert api.base_url == "https://restcountries.com/v3.1"
        assert api.timeout == 10

    def test_init_custom_values(self):
        """Test initialization with custom values"""
        api = CountryAPI(base_url="https://custom.api", timeout=5)
        assert api.base_url == "https://custom.api"
        assert api.timeout == 5

    @patch('country_api.requests.get')
    def test_get_country_info_success(self, mock_get):
        """Test successful country information retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            "name": {"common": "Germany"},
            "capital": ["Berlin"],
            "population": 83000000,
            "currencies": {"EUR": {"name": "Euro"}},
            "languages": {"deu": "German"},
            "latlng": [52.52, 13.405]
        }]
        mock_get.return_value = mock_response

        api = CountryAPI()
        result = api.get_country_info("Germany")

        assert result is not None
        assert result["name"] == "Germany"
        assert result["capital"] == "Berlin"
        assert result["population"] == 83000000
        assert result["currencies"] == "Euro"
        assert result["languages"] == "German"
        assert result["latlng"] == [52.52, 13.405]

    @patch('country_api.requests.get')
    def test_get_country_info_not_found(self, mock_get):
        """Test country not found returns None"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        api = CountryAPI()
        result = api.get_country_info("InvalidCountry")

        assert result is None

    @patch('country_api.requests.get')
    def test_get_country_info_server_error(self, mock_get):
        """Test server error returns None"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        api = CountryAPI()
        result = api.get_country_info("Germany")

        assert result is None

    @patch('country_api.requests.get')
    def test_get_country_info_timeout(self, mock_get):
        """Test timeout returns None"""
        mock_get.side_effect = requests.exceptions.Timeout()

        api = CountryAPI()
        result = api.get_country_info("Germany")

        assert result is None

    @patch('country_api.requests.get')
    def test_get_country_info_connection_error(self, mock_get):
        """Test connection error returns None"""
        mock_get.side_effect = requests.exceptions.RequestException()

        api = CountryAPI()
        result = api.get_country_info("Germany")

        assert result is None

    @patch('country_api.requests.get')
    def test_get_country_info_empty_response(self, mock_get):
        """Test empty response returns None"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        api = CountryAPI()
        result = api.get_country_info("Germany")

        assert result is None

    @patch('country_api.requests.get')
    def test_get_country_info_no_capital(self, mock_get):
        """Test country without capital"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            "name": {"common": "TestCountry"},
            "latlng": [0, 0],
            "population": 1000
        }]
        mock_get.return_value = mock_response

        api = CountryAPI()
        result = api.get_country_info("TestCountry")

        assert result is not None
        assert result["capital"] == "N/A"

    @patch('country_api.requests.get')
    def test_get_country_info_multiple_capitals(self, mock_get):
        """Test country with multiple capitals (takes first)"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            "name": {"common": "South Africa"},
            "capital": ["Pretoria", "Cape Town", "Bloemfontein"],
            "latlng": [0, 0]
        }]
        mock_get.return_value = mock_response

        api = CountryAPI()
        result = api.get_country_info("South Africa")

        assert result is not None
        assert result["capital"] == "Pretoria"

    @patch('country_api.requests.get')
    def test_extract_currencies_multiple(self, mock_get):
        """Test extracting multiple currencies"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            "name": {"common": "Panama"},
            "currencies": {
                "PAB": {"name": "Panamanian balboa"},
                "USD": {"name": "United States dollar"}
            },
            "latlng": [0, 0]
        }]
        mock_get.return_value = mock_response

        api = CountryAPI()
        result = api.get_country_info("Panama")

        assert result is not None
        assert "Panamanian balboa" in result["currencies"]
        assert "United States dollar" in result["currencies"]

    @patch('country_api.requests.get')
    def test_extract_currencies_none(self, mock_get):
        """Test country with no currencies"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            "name": {"common": "TestCountry"},
            "latlng": [0, 0]
        }]
        mock_get.return_value = mock_response

        api = CountryAPI()
        result = api.get_country_info("TestCountry")

        assert result is not None
        assert result["currencies"] == "N/A"

    @patch('country_api.requests.get')
    def test_extract_languages_multiple(self, mock_get):
        """Test extracting multiple languages"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            "name": {"common": "Switzerland"},
            "languages": {
                "deu": "German",
                "fra": "French",
                "ita": "Italian"
            },
            "latlng": [0, 0]
        }]
        mock_get.return_value = mock_response

        api = CountryAPI()
        result = api.get_country_info("Switzerland")

        assert result is not None
        assert "German" in result["languages"]
        assert "French" in result["languages"]
        assert "Italian" in result["languages"]

    @patch('country_api.requests.get')
    def test_extract_languages_none(self, mock_get):
        """Test country with no languages"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            "name": {"common": "TestCountry"},
            "latlng": [0, 0]
        }]
        mock_get.return_value = mock_response

        api = CountryAPI()
        result = api.get_country_info("TestCountry")

        assert result is not None
        assert result["languages"] == "N/A"

    @patch('country_api.requests.get')
    def test_get_country_info_malformed_json(self, mock_get):
        """Test handling of malformed JSON data"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        api = CountryAPI()
        result = api.get_country_info("Germany")

        assert result is None

    @patch('country_api.requests.get')
    def test_get_country_info_missing_required_fields(self, mock_get):
        """Test handling of response with missing required fields"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{}]  # Empty dict
        mock_get.return_value = mock_response

        api = CountryAPI()
        result = api.get_country_info("Germany")

        # Should handle gracefully with defaults
        assert result is not None
        assert result["name"] == "Unknown"
        assert result["capital"] == "N/A"
        assert result["population"] == 0

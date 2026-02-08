"""
Unit Tests for WeatherAPI

Tests using mocked HTTP requests.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import Mock, patch
import requests
from weather_api import WeatherAPI


class TestWeatherAPI:
    """Tests for WeatherAPI with mocked requests"""

    def test_init_default_values(self):
        """Test initialization with default values"""
        api = WeatherAPI()
        assert api.base_url == "https://api.open-meteo.com/v1"
        assert api.timeout == 10

    def test_init_custom_values(self):
        """Test initialization with custom values"""
        api = WeatherAPI(base_url="https://custom.api", timeout=5)
        assert api.base_url == "https://custom.api"
        assert api.timeout == 5

    @patch('weather_api.requests.get')
    def test_get_weather_success(self, mock_get):
        """Test successful weather data retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "current": {
                "temperature_2m": 22.5,
                "relative_humidity_2m": 65,
                "wind_speed_10m": 12.3,
                "precipitation": 0.0
            },
            "daily": {
                "time": ["2024-01-01", "2024-01-02"],
                "temperature_2m_max": [25.0, 23.0],
                "temperature_2m_min": [15.0, 14.0],
                "precipitation_sum": [0.0, 2.5],
                "wind_speed_10m_max": [15.0, 18.0],
                "relative_humidity_2m_mean": [60, 70]
            }
        }
        mock_get.return_value = mock_response

        api = WeatherAPI()
        result = api.get_weather(52.52, 13.405)

        assert result is not None
        assert result["current"]["temperature"] == 22.5
        assert result["current"]["humidity"] == 65
        assert result["current"]["wind_speed"] == 12.3
        assert result["current"]["precipitation"] == 0.0

        assert len(result["forecast"]) == 2
        assert result["forecast"][0]["date"] == "2024-01-01"
        assert result["forecast"][0]["temp_max"] == 25.0
        assert result["forecast"][0]["temp_min"] == 15.0
        assert result["forecast"][0]["precipitation"] == 0.0

    @patch('weather_api.requests.get')
    def test_get_weather_server_error(self, mock_get):
        """Test server error returns None"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        api = WeatherAPI()
        result = api.get_weather(52.52, 13.405)

        assert result is None

    @patch('weather_api.requests.get')
    def test_get_weather_timeout(self, mock_get):
        """Test timeout returns None"""
        mock_get.side_effect = requests.exceptions.Timeout()

        api = WeatherAPI()
        result = api.get_weather(52.52, 13.405)

        assert result is None

    @patch('weather_api.requests.get')
    def test_get_weather_connection_error(self, mock_get):
        """Test connection error returns None"""
        mock_get.side_effect = requests.exceptions.RequestException()

        api = WeatherAPI()
        result = api.get_weather(52.52, 13.405)

        assert result is None

    @patch('weather_api.requests.get')
    def test_get_weather_malformed_json(self, mock_get):
        """Test handling of malformed JSON data"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        api = WeatherAPI()
        result = api.get_weather(52.52, 13.405)

        assert result is None

    @patch('weather_api.requests.get')
    def test_extract_current_weather_minimal_data(self, mock_get):
        """Test extracting current weather with minimal data"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "current": {},
            "daily": {}
        }
        mock_get.return_value = mock_response

        api = WeatherAPI()
        result = api.get_weather(52.52, 13.405)

        assert result is not None
        assert result["current"]["temperature"] == 0
        assert result["current"]["humidity"] == 0
        assert result["current"]["wind_speed"] == 0
        assert result["current"]["precipitation"] == 0

    @patch('weather_api.requests.get')
    def test_extract_forecast_empty(self, mock_get):
        """Test extracting empty forecast"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "current": {},
            "daily": {}
        }
        mock_get.return_value = mock_response

        api = WeatherAPI()
        result = api.get_weather(52.52, 13.405)

        assert result is not None
        assert result["forecast"] == []

    @patch('weather_api.requests.get')
    def test_extract_forecast_seven_days(self, mock_get):
        """Test extracting 7-day forecast"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "current": {},
            "daily": {
                "time": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05", "2024-01-06", "2024-01-07"],
                "temperature_2m_max": [20, 21, 22, 23, 24, 25, 26],
                "temperature_2m_min": [10, 11, 12, 13, 14, 15, 16],
                "precipitation_sum": [0, 0, 2.5, 0, 0, 1.0, 0],
                "wind_speed_10m_max": [10, 12, 15, 11, 9, 13, 14],
                "relative_humidity_2m_mean": [60, 65, 70, 55, 50, 60, 62]
            }
        }
        mock_get.return_value = mock_response

        api = WeatherAPI()
        result = api.get_weather(52.52, 13.405)

        assert result is not None
        assert len(result["forecast"]) == 7
        assert result["forecast"][0]["temp_max"] == 20
        assert result["forecast"][6]["temp_max"] == 26
        assert result["forecast"][2]["precipitation"] == 2.5

    @patch('weather_api.requests.get')
    def test_extract_forecast_partial_data(self, mock_get):
        """Test extracting forecast with some missing fields"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "current": {},
            "daily": {
                "time": ["2024-01-01", "2024-01-02"],
                "temperature_2m_max": [20, 21]
                # Missing other fields
            }
        }
        mock_get.return_value = mock_response

        api = WeatherAPI()
        result = api.get_weather(52.52, 13.405)

        assert result is not None
        assert len(result["forecast"]) == 2
        assert result["forecast"][0]["temp_max"] == 20
        assert result["forecast"][0]["temp_min"] == 0  # Default
        assert result["forecast"][0]["precipitation"] == 0  # Default
        assert result["forecast"][0]["wind_speed"] == 0  # Default
        assert result["forecast"][0]["humidity"] == 0  # Default

    @patch('weather_api.requests.get')
    def test_get_weather_different_coordinates(self, mock_get):
        """Test weather retrieval with different coordinates"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "current": {"temperature_2m": 15.0},
            "daily": {}
        }
        mock_get.return_value = mock_response

        api = WeatherAPI()

        # Test different coordinates
        result1 = api.get_weather(52.52, 13.405)  # Berlin
        result2 = api.get_weather(40.7128, -74.0060)  # New York
        result3 = api.get_weather(-33.8688, 151.2093)  # Sydney

        assert result1 is not None
        assert result2 is not None
        assert result3 is not None

    @patch('weather_api.requests.get')
    def test_extract_forecast_mismatched_array_lengths(self, mock_get):
        """Test forecast extraction with mismatched array lengths"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "current": {},
            "daily": {
                "time": ["2024-01-01", "2024-01-02", "2024-01-03"],
                "temperature_2m_max": [20, 21],  # Only 2 elements
                "temperature_2m_min": [10, 11, 12],
                "precipitation_sum": [0],  # Only 1 element
                "wind_speed_10m_max": [10, 12, 15, 18],  # 4 elements
                "relative_humidity_2m_mean": [60, 65]  # Only 2 elements
            }
        }
        mock_get.return_value = mock_response

        api = WeatherAPI()
        result = api.get_weather(52.52, 13.405)

        assert result is not None
        assert len(result["forecast"]) == 3  # Based on time array

        # Check that defaults are used for missing data
        assert result["forecast"][0]["temp_max"] == 20
        assert result["forecast"][1]["temp_max"] == 21
        assert result["forecast"][2]["temp_max"] == 0  # Default (out of bounds)

        assert result["forecast"][1]["precipitation"] == 0  # Default (out of bounds)
        assert result["forecast"][2]["wind_speed"] == 15  # Index 2 of [10, 12, 15, 18]

    @patch('weather_api.requests.get')
    def test_current_weather_with_all_fields(self, mock_get):
        """Test current weather extraction with all fields present"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "current": {
                "temperature_2m": 18.5,
                "relative_humidity_2m": 72,
                "wind_speed_10m": 8.7,
                "precipitation": 1.2
            },
            "daily": {}
        }
        mock_get.return_value = mock_response

        api = WeatherAPI()
        result = api.get_weather(52.52, 13.405)

        assert result is not None
        assert result["current"]["temperature"] == 18.5
        assert result["current"]["humidity"] == 72
        assert result["current"]["wind_speed"] == 8.7
        assert result["current"]["precipitation"] == 1.2

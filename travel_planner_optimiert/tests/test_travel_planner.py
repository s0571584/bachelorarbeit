"""
Unit Tests for TravelPlanner

Tests using mocked dependencies (Dependency Injection).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import MagicMock
from main import TravelPlanner


class TestTravelPlanner:
    """Tests for TravelPlanner with mocked dependencies"""

    def test_successful_recommendation(self):
        """Test successful travel recommendation flow"""
        # Create mocks
        mock_country_api = MagicMock()
        mock_weather_api = MagicMock()
        mock_formatter = MagicMock()
        mock_rec_engine = MagicMock()

        # Configure mocks
        mock_country_api.get_country_info.return_value = {
            "name": "Germany",
            "capital": "Berlin",
            "population": 83000000,
            "currencies": "Euro",
            "languages": "German",
            "latlng": [52.52, 13.405]
        }

        mock_weather_api.get_weather.return_value = {
            "current": {"temperature": 20, "humidity": 60, "wind_speed": 10, "precipitation": 0},
            "forecast": [{"temp_max": 22, "precipitation": 0} for _ in range(7)]
        }

        mock_formatter.format_country_info.return_value = "Country: Germany"
        mock_formatter.format_current_weather.return_value = "Temperature: 20°C"
        mock_formatter.format_forecast.return_value = "Forecast..."

        mock_recommendation = MagicMock()
        mock_recommendation.score = 95
        mock_recommendation.rating = "⭐⭐⭐⭐⭐"
        mock_recommendation.summary = "Excellent"
        mock_recommendation.details = "Details..."
        mock_rec_engine.calculate_recommendation.return_value = mock_recommendation

        # Create planner with mocks
        planner = TravelPlanner(
            country_api=mock_country_api,
            weather_api=mock_weather_api,
            formatter=mock_formatter,
            recommendation_engine=mock_rec_engine
        )

        # Test
        result = planner.get_travel_recommendation("Germany")

        assert result["success"] is True
        assert result["country"]["name"] == "Germany"
        assert result["recommendation"]["score"] == 95
        mock_country_api.get_country_info.assert_called_once_with("Germany")

    def test_country_not_found(self):
        """Test handling of country not found"""
        mock_country_api = MagicMock()
        mock_country_api.get_country_info.return_value = None

        planner = TravelPlanner(country_api=mock_country_api)

        result = planner.get_travel_recommendation("InvalidCountry")

        assert result["success"] is False
        assert "not found" in result["error"]

    def test_weather_api_failure(self):
        """Test handling of weather API failure"""
        mock_country_api = MagicMock()
        mock_weather_api = MagicMock()

        mock_country_api.get_country_info.return_value = {
            "name": "Germany",
            "latlng": [52.52, 13.405],
            "capital": "Berlin"
        }
        mock_weather_api.get_weather.return_value = None

        planner = TravelPlanner(
            country_api=mock_country_api,
            weather_api=mock_weather_api
        )

        result = planner.get_travel_recommendation("Germany")

        assert result["success"] is False
        assert "weather" in result["error"].lower()

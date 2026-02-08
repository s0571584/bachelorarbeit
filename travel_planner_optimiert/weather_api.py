"""
Weather API Module

Single Responsibility: ONLY handles Open-Meteo API calls.
"""

import requests
from typing import Optional, Dict, Any, List
from config import WEATHER_API_URL, API_TIMEOUT


class WeatherAPI:
    """
    Fetches weather data from Open-Meteo API.

    Responsibility: API communication only.
    No formatting, no analysis, no recommendations.
    """

    def __init__(self, base_url: str = WEATHER_API_URL, timeout: int = API_TIMEOUT):
        """
        Initialize Weather API client.

        Args:
            base_url: Base URL for Open-Meteo API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.timeout = timeout

    def get_weather(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Get current and 7-day forecast weather for coordinates.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Dictionary with weather data or None if error
        """
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,relative_humidity_2m_mean",
                "timezone": "auto",
                "forecast_days": 7
            }

            response = requests.get(url, params=params, timeout=self.timeout)

            if response.status_code != 200:
                return None

            data = response.json()
            return {
                "current": self._extract_current_weather(data.get("current", {})),
                "forecast": self._extract_forecast(data.get("daily", {}))
            }

        except requests.exceptions.Timeout:
            return None
        except requests.exceptions.RequestException:
            return None
        except (KeyError, ValueError):
            return None

    def _extract_current_weather(self, current_data: Dict) -> Dict[str, Any]:
        """
        Extract current weather data.

        Args:
            current_data: Current weather data from API

        Returns:
            Simplified current weather dictionary
        """
        return {
            "temperature": current_data.get("temperature_2m", 0),
            "humidity": current_data.get("relative_humidity_2m", 0),
            "wind_speed": current_data.get("wind_speed_10m", 0),
            "precipitation": current_data.get("precipitation", 0)
        }

    def _extract_forecast(self, daily_data: Dict) -> List[Dict[str, Any]]:
        """
        Extract 7-day forecast data.

        Args:
            daily_data: Daily forecast data from API

        Returns:
            List of daily forecast dictionaries
        """
        if not daily_data:
            return []

        dates = daily_data.get("time", [])
        temp_max = daily_data.get("temperature_2m_max", [])
        temp_min = daily_data.get("temperature_2m_min", [])
        precipitation = daily_data.get("precipitation_sum", [])
        wind = daily_data.get("wind_speed_10m_max", [])
        humidity = daily_data.get("relative_humidity_2m_mean", [])

        forecast = []
        for i in range(len(dates)):
            forecast.append({
                "date": dates[i] if i < len(dates) else "",
                "temp_max": temp_max[i] if i < len(temp_max) else 0,
                "temp_min": temp_min[i] if i < len(temp_min) else 0,
                "precipitation": precipitation[i] if i < len(precipitation) else 0,
                "wind_speed": wind[i] if i < len(wind) else 0,
                "humidity": humidity[i] if i < len(humidity) else 0
            })

        return forecast

"""
Weather Formatter Module

Single Responsibility: ONLY formats weather data for display.
"""

from typing import Dict, Any, List


class WeatherFormatter:
    """
    Formats weather data for user-friendly display.

    Responsibility: Data formatting only.
    No API calls, no business logic, no recommendations.
    """

    def format_current_weather(self, current: Dict[str, Any]) -> str:
        """
        Format current weather data for display.

        Args:
            current: Current weather dictionary

        Returns:
            Formatted string
        """
        return (
            f"Temperature: {current.get('temperature', 0):.1f}°C\n"
            f"Humidity: {current.get('humidity', 0):.0f}%\n"
            f"Wind Speed: {current.get('wind_speed', 0):.1f} km/h\n"
            f"Precipitation: {current.get('precipitation', 0):.1f} mm"
        )

    def format_forecast(self, forecast: List[Dict[str, Any]]) -> str:
        """
        Format 7-day forecast for display.

        Args:
            forecast: List of daily forecast dictionaries

        Returns:
            Formatted multi-line string
        """
        if not forecast:
            return "No forecast data available"

        lines = []
        for day in forecast:
            line = (
                f"{day.get('date', 'N/A')}: "
                f"{day.get('temp_min', 0):.0f}°C - {day.get('temp_max', 0):.0f}°C, "
                f"Precipitation: {day.get('precipitation', 0):.1f}mm, "
                f"Wind: {day.get('wind_speed', 0):.0f}km/h"
            )
            lines.append(line)

        return "\n".join(lines)

    def format_country_info(self, country: Dict[str, Any]) -> str:
        """
        Format country information for display.

        Args:
            country: Country information dictionary

        Returns:
            Formatted string
        """
        return (
            f"Country: {country.get('name', 'Unknown')}\n"
            f"Capital: {country.get('capital', 'N/A')}\n"
            f"Population: {country.get('population', 0):,}\n"
            f"Currencies: {country.get('currencies', 'N/A')}\n"
            f"Languages: {country.get('languages', 'N/A')}"
        )

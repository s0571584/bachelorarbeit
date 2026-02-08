"""
Travel Planner Main Module

Orchestrates all components to provide travel recommendations.
"""

from typing import Optional
from country_api import CountryAPI
from weather_api import WeatherAPI
from weather_formatter import WeatherFormatter
from recommendation import RecommendationEngine


class TravelPlanner:
    """
    Main application class for travel planning.

    Responsibility: Orchestration only.
    Delegates to specialized classes via Dependency Injection.

    Design Principle: Dependency Inversion Principle (SOLID)
    - Depends on abstractions (constructor injection)
    - Not tightly coupled to concrete implementations
    """

    def __init__(
        self,
        country_api: Optional[CountryAPI] = None,
        weather_api: Optional[WeatherAPI] = None,
        formatter: Optional[WeatherFormatter] = None,
        recommendation_engine: Optional[RecommendationEngine] = None
    ):
        """
        Initialize Travel Planner with dependencies.

        Dependency Injection: All dependencies are optional for testing.
        If not provided, default implementations are used.

        Args:
            country_api: CountryAPI instance
            weather_api: WeatherAPI instance
            formatter: WeatherFormatter instance
            recommendation_engine: RecommendationEngine instance
        """
        self.country_api = country_api or CountryAPI()
        self.weather_api = weather_api or WeatherAPI()
        self.formatter = formatter or WeatherFormatter()
        self.recommendation_engine = recommendation_engine or RecommendationEngine()

    def get_travel_recommendation(self, country_name: str) -> dict:
        """
        Get comprehensive travel recommendation for a country.

        Orchestrates all components:
        1. Fetch country info
        2. Fetch weather data
        3. Format data
        4. Generate recommendation

        Args:
            country_name: Name of the country

        Returns:
            Dictionary with all information and recommendation

        Complexity: CC 4 (3 error checks)
        """
        # Step 1: Get country information
        country_info = self.country_api.get_country_info(country_name)
        if not country_info:
            return {
                "success": False,
                "error": f"Country '{country_name}' not found"
            }

        # Step 2: Get weather data for capital
        lat, lng = country_info["latlng"]
        weather_data = self.weather_api.get_weather(lat, lng)
        if not weather_data:
            return {
                "success": False,
                "error": "Failed to fetch weather data"
            }

        # Step 3: Calculate recommendation
        recommendation = self.recommendation_engine.calculate_recommendation(
            weather_data["forecast"]
        )

        # Step 4: Format all data for display
        return {
            "success": True,
            "country": country_info,
            "country_info_formatted": self.formatter.format_country_info(country_info),
            "current_weather": weather_data["current"],
            "current_weather_formatted": self.formatter.format_current_weather(weather_data["current"]),
            "forecast": weather_data["forecast"],
            "forecast_formatted": self.formatter.format_forecast(weather_data["forecast"]),
            "recommendation": {
                "score": recommendation.score,
                "rating": recommendation.rating,
                "summary": recommendation.summary,
                "details": recommendation.details
            }
        }

    def display_results(self, results: dict) -> None:
        """
        Display results in a user-friendly format.

        Args:
            results: Results dictionary from get_travel_recommendation

        Complexity: CC 2 (one if check)
        """
        if not results.get("success"):
            print(f"\nError: {results.get('error')}")
            return

        print("\n" + "=" * 70)
        print("REISE-WETTER-PLANER")
        print("=" * 70)

        print("\n" + "-" * 70)
        print("LÄNDERINFORMATIONEN")
        print("-" * 70)
        print(results["country_info_formatted"])

        print("\n" + "-" * 70)
        print("AKTUELLES WETTER IN " + results["country"]["capital"].upper())
        print("-" * 70)
        print(results["current_weather_formatted"])

        print("\n" + "-" * 70)
        print("7-TAGE WETTERVORHERSAGE")
        print("-" * 70)
        print(results["forecast_formatted"])

        rec = results["recommendation"]
        print("\n" + "-" * 70)
        print("REISEEMPFEHLUNG")
        print("-" * 70)
        print(f"Bewertung: {rec['rating']} ({rec['score']}/100)")
        print(f"Zusammenfassung: {rec['summary']}")
        print(f"\nDetails:")
        print(rec['details'])
        print("=" * 70 + "\n")


def main():
    """
    Main entry point for command-line usage.

    Complexity: CC 1 (no branches)
    """
    planner = TravelPlanner()

    print("\n" + "=" * 70)
    print("Willkommen zum Reise-Wetter-Planer!")
    print("=" * 70)

    country_name = input("\nBitte geben Sie ein Land ein: ").strip()

    if country_name:
        print(f"\nSuche Informationen für {country_name}...")
        results = planner.get_travel_recommendation(country_name)
        planner.display_results(results)
    else:
        print("\nFehler: Kein Land eingegeben.")


if __name__ == "__main__":
    main()

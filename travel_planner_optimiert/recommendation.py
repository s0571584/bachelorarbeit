"""
Recommendation Engine Module

Single Responsibility: ONLY calculates travel recommendations based on weather.
"""

from dataclasses import dataclass
from typing import List, Dict
from config import (
    TEMP_IDEAL_MIN,
    TEMP_IDEAL_MAX,
    HUMIDITY_MAX,
    PRECIPITATION_THRESHOLD,
    SCORE_EXCELLENT,
    SCORE_GOOD,
    SCORE_ACCEPTABLE,
    SCORE_POOR
)


@dataclass
class WeatherMetrics:
    """Weather statistics for recommendation calculation"""
    avg_temp: float
    avg_humidity: float
    avg_wind: float
    total_precipitation: float
    good_days: int
    bad_days: int


@dataclass
class Recommendation:
    """Travel recommendation result"""
    score: int  # 0-100
    rating: str  # ⭐ to ⭐⭐⭐⭐⭐
    summary: str
    details: str
    metrics: WeatherMetrics


class RecommendationEngine:
    """
    Calculates travel recommendations based on weather data.

    Responsibility: Recommendation logic only.
    No API calls, no formatting, no user interaction.
    """

    def calculate_recommendation(self, forecast: List[Dict]) -> Recommendation:
        """
        Calculate travel recommendation from forecast.

        Main orchestration method - delegates to helpers.

        Args:
            forecast: List of daily forecast dictionaries

        Returns:
            Recommendation object
        """
        metrics = self._calculate_metrics(forecast)
        score = self._calculate_score(metrics)
        rating = self._score_to_rating(score)
        summary = self._generate_summary(score)
        details = self._generate_details(metrics)

        return Recommendation(score, rating, summary, details, metrics)

    def _calculate_metrics(self, forecast: List[Dict]) -> WeatherMetrics:
        """
        Calculate weather metrics from forecast.

        Args:
            forecast: List of daily forecast dictionaries

        Returns:
            WeatherMetrics object
        """
        if not forecast:
            return WeatherMetrics(0, 0, 0, 0, 0, 0)

        temps = [day.get('temp_max', 20) for day in forecast]
        humidities = [day.get('humidity', 50) for day in forecast]
        winds = [day.get('wind_speed', 10) for day in forecast]
        precipitations = [day.get('precipitation', 0) for day in forecast]

        good_days = self._count_good_days(forecast)
        bad_days = len(forecast) - good_days

        return WeatherMetrics(
            avg_temp=sum(temps) / len(temps),
            avg_humidity=sum(humidities) / len(humidities),
            avg_wind=sum(winds) / len(winds),
            total_precipitation=sum(precipitations),
            good_days=good_days,
            bad_days=bad_days
        )

    def _count_good_days(self, forecast: List[Dict]) -> int:
        """
        Count days with good weather.

        A good day has:
        - Temperature between TEMP_IDEAL_MIN and TEMP_IDEAL_MAX
        - Precipitation below PRECIPITATION_THRESHOLD

        Args:
            forecast: List of daily forecast dictionaries

        Returns:
            Number of good days
        """
        count = 0
        for day in forecast:
            temp = day.get('temp_max', 20)
            precip = day.get('precipitation', 0)
            if TEMP_IDEAL_MIN <= temp <= TEMP_IDEAL_MAX and precip < PRECIPITATION_THRESHOLD:
                count += 1
        return count

    def _calculate_score(self, metrics: WeatherMetrics) -> int:
        """
        Calculate recommendation score (0-100).

        Starts at 100 and subtracts penalties for unfavorable conditions.

        Args:
            metrics: WeatherMetrics object

        Returns:
            Score between 0 and 100
        """
        score = 100

        # Temperature penalty
        if metrics.avg_temp < TEMP_IDEAL_MIN:
            score -= (TEMP_IDEAL_MIN - metrics.avg_temp) * 3
        elif metrics.avg_temp > TEMP_IDEAL_MAX:
            score -= (metrics.avg_temp - TEMP_IDEAL_MAX) * 3

        # Humidity penalty
        if metrics.avg_humidity > HUMIDITY_MAX:
            score -= (metrics.avg_humidity - HUMIDITY_MAX) * 0.5

        # Precipitation penalty
        score -= metrics.total_precipitation * 2

        # Bad days penalty
        score -= metrics.bad_days * 5

        return max(0, min(100, int(score)))

    def _score_to_rating(self, score: int) -> str:
        """
        Convert score to star rating.

        Args:
            score: Recommendation score (0-100)

        Returns:
            Star rating string
        """
        if score >= SCORE_EXCELLENT:
            return "⭐⭐⭐⭐⭐"
        if score >= SCORE_GOOD:
            return "⭐⭐⭐⭐"
        if score >= SCORE_ACCEPTABLE:
            return "⭐⭐⭐"
        if score >= SCORE_POOR:
            return "⭐⭐"
        return "⭐"

    def _generate_summary(self, score: int) -> str:
        """
        Generate summary text based on score.

        Args:
            score: Recommendation score (0-100)

        Returns:
            Summary string
        """
        if score >= SCORE_EXCELLENT:
            return "Ausgezeichnete Reisebedingungen!"
        if score >= SCORE_GOOD:
            return "Gute Reisebedingungen"
        if score >= SCORE_ACCEPTABLE:
            return "Akzeptable Bedingungen"
        if score >= SCORE_POOR:
            return "Mäßige Bedingungen"
        return "Ungünstige Reisebedingungen"

    def _generate_details(self, metrics: WeatherMetrics) -> str:
        """
        Generate detailed recommendation text.

        Args:
            metrics: WeatherMetrics object

        Returns:
            Multi-line detail string
        """
        details = []
        details.append(f"Durchschnittstemperatur: {metrics.avg_temp:.1f}°C")
        details.append(f"Gute Reisetage: {metrics.good_days} von 7")

        if metrics.total_precipitation > 10:
            details.append(f"Achtung: {metrics.total_precipitation:.1f}mm Niederschlag erwartet")

        return "\n".join(details)

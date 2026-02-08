"""
Unit Tests for RecommendationEngine

Tests recommendation logic without external dependencies.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from recommendation import RecommendationEngine, WeatherMetrics


class TestRecommendationEngine:
    """Tests for RecommendationEngine"""

    def setup_method(self):
        """Setup recommendation engine"""
        self.engine = RecommendationEngine()

    def test_perfect_weather_high_score(self):
        """Test that perfect weather gives high score (~95)"""
        # Perfect weather: 20-25°C, no rain, low humidity
        forecast = [
            {"temp_max": 22, "temp_min": 18, "precipitation": 0, "humidity": 60, "wind_speed": 10}
            for _ in range(7)
        ]

        recommendation = self.engine.calculate_recommendation(forecast)

        assert recommendation.score >= 90
        assert "⭐⭐⭐⭐⭐" in recommendation.rating
        assert "Ausgezeichnete" in recommendation.summary
        assert recommendation.metrics.good_days == 7

    def test_bad_weather_low_score(self):
        """Test that bad weather gives low score (~30)"""
        # Bad weather: cold, rainy
        forecast = [
            {"temp_max": 5, "temp_min": 2, "precipitation": 15, "humidity": 90, "wind_speed": 35}
            for _ in range(7)
        ]

        recommendation = self.engine.calculate_recommendation(forecast)

        assert recommendation.score <= 40
        assert "⭐" == recommendation.rating or "⭐⭐" == recommendation.rating
        assert recommendation.metrics.good_days == 0

    def test_mixed_weather_medium_score(self):
        """Test that mixed weather gives medium score (~40-60)"""
        forecast = [
            {"temp_max": 20, "temp_min": 15, "precipitation": 0, "humidity": 65, "wind_speed": 12},
            {"temp_max": 22, "temp_min": 16, "precipitation": 0, "humidity": 60, "wind_speed": 10},
            {"temp_max": 18, "temp_min": 14, "precipitation": 3, "humidity": 70, "wind_speed": 15},
            {"temp_max": 12, "temp_min": 8, "precipitation": 8, "humidity": 80, "wind_speed": 20},
            {"temp_max": 14, "temp_min": 10, "precipitation": 10, "humidity": 85, "wind_speed": 18},
            {"temp_max": 19, "temp_min": 13, "precipitation": 2, "humidity": 68, "wind_speed": 14},
            {"temp_max": 21, "temp_min": 15, "precipitation": 1, "humidity": 62, "wind_speed": 11}
        ]

        recommendation = self.engine.calculate_recommendation(forecast)

        assert 35 <= recommendation.score <= 60
        assert "⭐⭐" in recommendation.rating or "⭐⭐⭐" in recommendation.rating

    def test_empty_forecast(self):
        """Test handling of empty forecast (uses defaults)"""
        recommendation = self.engine.calculate_recommendation([])

        # Empty forecast uses defaults which result in a neutral score
        assert recommendation.score > 0  # Will be based on default values
        assert recommendation.metrics.good_days == 0
        assert recommendation.metrics.bad_days == 0

    def test_good_days_count(self):
        """Test counting of good days"""
        forecast = [
            {"temp_max": 20, "precipitation": 0},  # Good
            {"temp_max": 25, "precipitation": 2},  # Good
            {"temp_max": 10, "precipitation": 0},  # Bad (too cold)
            {"temp_max": 35, "precipitation": 0},  # Bad (too hot)
            {"temp_max": 22, "precipitation": 10},  # Bad (too much rain)
            {"temp_max": 18, "precipitation": 3},  # Good
            {"temp_max": 23, "precipitation": 1},  # Good
        ]

        recommendation = self.engine.calculate_recommendation(forecast)

        assert recommendation.metrics.good_days == 4
        assert recommendation.metrics.bad_days == 3

    def test_metrics_calculation(self):
        """Test that metrics are calculated correctly"""
        forecast = [
            {"temp_max": 20, "temp_min": 15, "precipitation": 2, "humidity": 60, "wind_speed": 10},
            {"temp_max": 22, "temp_min": 16, "precipitation": 0, "humidity": 65, "wind_speed": 12}
        ]

        recommendation = self.engine.calculate_recommendation(forecast)
        metrics = recommendation.metrics

        assert metrics.avg_temp == 21.0  # (20 + 22) / 2
        assert metrics.avg_humidity == 62.5  # (60 + 65) / 2
        assert metrics.avg_wind == 11.0  # (10 + 12) / 2
        assert metrics.total_precipitation == 2.0  # 2 + 0

    def test_score_to_rating_excellent(self):
        """Test excellent rating (90+)"""
        rating = self.engine._score_to_rating(95)
        assert rating == "⭐⭐⭐⭐⭐"

    def test_score_to_rating_good(self):
        """Test good rating (75-89)"""
        rating = self.engine._score_to_rating(80)
        assert rating == "⭐⭐⭐⭐"

    def test_score_to_rating_acceptable(self):
        """Test acceptable rating (60-74)"""
        rating = self.engine._score_to_rating(65)
        assert rating == "⭐⭐⭐"

    def test_score_to_rating_poor(self):
        """Test poor rating (40-59)"""
        rating = self.engine._score_to_rating(45)
        assert rating == "⭐⭐"

    def test_score_to_rating_bad(self):
        """Test bad rating (<40)"""
        rating = self.engine._score_to_rating(30)
        assert rating == "⭐"

    def test_summary_excellent(self):
        """Test excellent summary"""
        summary = self.engine._generate_summary(95)
        assert "Ausgezeichnete" in summary

    def test_summary_poor(self):
        """Test poor summary"""
        summary = self.engine._generate_summary(30)
        assert "Ungünstige" in summary

    def test_details_generation(self):
        """Test that details are generated"""
        metrics = WeatherMetrics(
            avg_temp=22.5,
            avg_humidity=65.0,
            avg_wind=12.0,
            total_precipitation=15.0,
            good_days=5,
            bad_days=2
        )

        details = self.engine._generate_details(metrics)

        assert "22.5°C" in details
        assert "5 von 7" in details
        assert "15.0mm" in details  # Should warn about precipitation

    def test_precipitation_warning_in_details(self):
        """Test that high precipitation triggers warning"""
        metrics = WeatherMetrics(
            avg_temp=20.0,
            avg_humidity=60.0,
            avg_wind=10.0,
            total_precipitation=25.0,  # High precipitation
            good_days=3,
            bad_days=4
        )

        details = self.engine._generate_details(metrics)

        assert "Achtung" in details
        assert "25.0mm" in details

    def test_no_precipitation_warning_when_low(self):
        """Test that low precipitation doesn't trigger warning"""
        metrics = WeatherMetrics(
            avg_temp=20.0,
            avg_humidity=60.0,
            avg_wind=10.0,
            total_precipitation=5.0,  # Low precipitation
            good_days=6,
            bad_days=1
        )

        details = self.engine._generate_details(metrics)

        assert "Achtung" not in details

    def test_score_boundaries(self):
        """Test that score stays within 0-100 bounds"""
        # Test extremely good weather
        forecast_perfect = [
            {"temp_max": 22, "temp_min": 18, "precipitation": 0, "humidity": 50, "wind_speed": 5}
            for _ in range(7)
        ]
        rec_perfect = self.engine.calculate_recommendation(forecast_perfect)
        assert 0 <= rec_perfect.score <= 100

        # Test extremely bad weather
        forecast_terrible = [
            {"temp_max": -10, "temp_min": -20, "precipitation": 50, "humidity": 100, "wind_speed": 60}
            for _ in range(7)
        ]
        rec_terrible = self.engine.calculate_recommendation(forecast_terrible)
        assert 0 <= rec_terrible.score <= 100

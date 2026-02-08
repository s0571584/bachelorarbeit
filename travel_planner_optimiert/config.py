"""
Configuration Module

Centralized configuration for the Travel Planner application.
"""

# API Configuration
API_TIMEOUT = 10
COUNTRIES_API_URL = "https://restcountries.com/v3.1"
WEATHER_API_URL = "https://api.open-meteo.com/v1"

# Recommendation Thresholds
TEMP_IDEAL_MIN = 15  # Celsius
TEMP_IDEAL_MAX = 28  # Celsius
HUMIDITY_MAX = 80  # Percent
WIND_MAX = 30  # km/h
PRECIPITATION_THRESHOLD = 5  # mm

# Score Thresholds for Ratings
SCORE_EXCELLENT = 90
SCORE_GOOD = 75
SCORE_ACCEPTABLE = 60
SCORE_POOR = 40

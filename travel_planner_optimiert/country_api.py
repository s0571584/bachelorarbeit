"""
Country API Module

Single Responsibility: ONLY handles REST Countries API calls.
"""

import requests
from typing import Optional, Dict, Any
from config import COUNTRIES_API_URL, API_TIMEOUT


class CountryAPI:
    """
    Fetches country information from REST Countries API.

    Responsibility: API communication only.
    No data formatting, no business logic, no recommendations.
    """

    def __init__(self, base_url: str = COUNTRIES_API_URL, timeout: int = API_TIMEOUT):
        """
        Initialize Country API client.

        Args:
            base_url: Base URL for REST Countries API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.timeout = timeout

    def get_country_info(self, country_name: str) -> Optional[Dict[str, Any]]:
        """
        Get country information by name.

        Args:
            country_name: Name of the country

        Returns:
            Dictionary with country info or None if not found/error
        """
        try:
            url = f"{self.base_url}/name/{country_name}"
            response = requests.get(url, timeout=self.timeout)

            if response.status_code == 404:
                return None

            if response.status_code != 200:
                return None

            data = response.json()
            if not data:
                return None

            # REST Countries API returns a list, take first result
            country_data = data[0]

            # Extract relevant information
            return {
                "name": country_data.get("name", {}).get("common", "Unknown"),
                "capital": country_data.get("capital", ["N/A"])[0] if country_data.get("capital") else "N/A",
                "population": country_data.get("population", 0),
                "currencies": self._extract_currencies(country_data.get("currencies", {})),
                "languages": self._extract_languages(country_data.get("languages", {})),
                "latlng": country_data.get("latlng", [0, 0])
            }

        except requests.exceptions.Timeout:
            return None
        except requests.exceptions.RequestException:
            return None
        except (KeyError, IndexError, ValueError):
            return None

    def _extract_currencies(self, currencies_dict: Dict) -> str:
        """
        Extract currency names from currencies dictionary.

        Args:
            currencies_dict: Currencies data from API

        Returns:
            Comma-separated currency names
        """
        if not currencies_dict:
            return "N/A"

        currency_names = [info.get("name", "Unknown") for info in currencies_dict.values()]
        return ", ".join(currency_names)

    def _extract_languages(self, languages_dict: Dict) -> str:
        """
        Extract language names from languages dictionary.

        Args:
            languages_dict: Languages data from API

        Returns:
            Comma-separated language names
        """
        if not languages_dict:
            return "N/A"

        return ", ".join(languages_dict.values())

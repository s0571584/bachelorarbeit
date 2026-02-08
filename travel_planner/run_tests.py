"""
Test-Runner für Travel Planner

Dieses Skript führt alle Tests aus und gibt eine Zusammenfassung aus.
"""

import unittest
import sys
import os

# Füge aktuelles Verzeichnis zum Path hinzu
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def run_all_tests():
    """
    Führt alle Tests aus und gibt Ergebnisse aus.
    """
    print("="*60)
    print("TRAVEL PLANNER - TEST SUITE")
    print("="*60)
    print()

    # Discover und führe Tests aus
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')

    # Führe Tests aus
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Zusammenfassung
    print("\n" + "="*60)
    print("TEST ZUSAMMENFASSUNG")
    print("="*60)
    print(f"Tests ausgeführt:    {result.testsRun}")
    print(f"Erfolgreich:         {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Fehlgeschlagen:      {len(result.failures)}")
    print(f"Fehler:              {len(result.errors)}")
    print(f"Übersprungen:        {len(result.skipped)}")
    print("="*60)

    # Rückgabecode
    if result.wasSuccessful():
        print("\n✓ Alle Tests erfolgreich!")
        return 0
    else:
        print("\n✗ Einige Tests sind fehlgeschlagen.")
        return 1


def run_unit_tests_only():
    """
    Führt nur Unit Tests aus (keine Integration Tests).
    """
    print("="*60)
    print("TRAVEL PLANNER - UNIT TESTS")
    print("="*60)
    print()

    loader = unittest.TestLoader()

    # Lade Test-Module
    from tests import test_country_api, test_weather_api, test_main

    suite = unittest.TestSuite()

    # Füge nur spezifische Test-Klassen hinzu
    suite.addTests(loader.loadTestsFromTestCase(test_country_api.TestCountryAPI))
    suite.addTests(loader.loadTestsFromTestCase(test_weather_api.TestWeatherAPI))
    suite.addTests(loader.loadTestsFromTestCase(test_main.TestTravelPlanner))

    # Führe Tests aus
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


def main():
    """Hauptfunktion."""
    if len(sys.argv) > 1 and sys.argv[1] == '--unit-only':
        return run_unit_tests_only()
    else:
        return run_all_tests()


if __name__ == '__main__':
    sys.exit(main())

"""
Unit Tests für sort_algorithm.py
"""

import unittest
from sort_algorithm import sort_numbers


class TestSortNumbers(unittest.TestCase):

    def test_positive_numbers(self):
        """Test mit positiven Zahlen"""
        self.assertEqual(sort_numbers([5, 2, 8, 1, 9]), [1, 2, 5, 8, 9])

    def test_negative_numbers(self):
        """Test mit negativen Zahlen"""
        self.assertEqual(sort_numbers([-5, -2, -8, -1, -9]), [-9, -8, -5, -2, -1])

    def test_mixed_numbers(self):
        """Test mit gemischten Zahlen (positiv und negativ)"""
        self.assertEqual(sort_numbers([5, -2, 8, -1, 0, 3]), [-2, -1, 0, 3, 5, 8])

    def test_with_zero(self):
        """Test mit Null"""
        self.assertEqual(sort_numbers([0, 5, -3, 0, 2]), [-3, 0, 0, 2, 5])

    def test_already_sorted(self):
        """Test mit bereits sortierter Liste"""
        self.assertEqual(sort_numbers([1, 2, 3, 4, 5]), [1, 2, 3, 4, 5])

    def test_reverse_sorted(self):
        """Test mit umgekehrt sortierter Liste"""
        self.assertEqual(sort_numbers([5, 4, 3, 2, 1]), [1, 2, 3, 4, 5])

    def test_empty_list(self):
        """Test mit leerer Liste"""
        self.assertEqual(sort_numbers([]), [])

    def test_single_element(self):
        """Test mit einem Element"""
        self.assertEqual(sort_numbers([42]), [42])

    def test_duplicate_numbers(self):
        """Test mit duplizierten Zahlen"""
        self.assertEqual(sort_numbers([3, 1, 3, 2, 1]), [1, 1, 2, 3, 3])

    def test_invalid_input(self):
        """Test mit ungültigem Input"""
        with self.assertRaises(TypeError):
            sort_numbers("not a list")

    def test_original_unchanged(self):
        """Test ob Original-Liste unverändert bleibt"""
        original = [3, 1, 2]
        sort_numbers(original)
        self.assertEqual(original, [3, 1, 2])


if __name__ == "__main__":
    unittest.main()

"""
Unit Tests für fibonacci.py
"""

import unittest
from fibonacci import fibonacci


class TestFibonacci(unittest.TestCase):

    def test_fibonacci_zero(self):
        """Test mit n=0"""
        self.assertEqual(fibonacci(0), [])

    def test_fibonacci_one(self):
        """Test mit n=1"""
        self.assertEqual(fibonacci(1), [0])

    def test_fibonacci_two(self):
        """Test mit n=2"""
        self.assertEqual(fibonacci(2), [0, 1])

    def test_fibonacci_five(self):
        """Test mit n=5"""
        self.assertEqual(fibonacci(5), [0, 1, 1, 2, 3])

    def test_fibonacci_ten(self):
        """Test mit n=10"""
        self.assertEqual(fibonacci(10), [0, 1, 1, 2, 3, 5, 8, 13, 21, 34])

    def test_fibonacci_length(self):
        """Test ob die Länge der Liste korrekt ist"""
        for n in range(1, 20):
            self.assertEqual(len(fibonacci(n)), n)

    def test_fibonacci_sequence_property(self):
        """Test ob Fibonacci-Eigenschaft erfüllt ist (jede Zahl ist Summe der vorherigen zwei)"""
        result = fibonacci(10)
        for i in range(2, len(result)):
            self.assertEqual(result[i], result[i-1] + result[i-2])

    def test_negative_input(self):
        """Test mit negativem Input"""
        with self.assertRaises(ValueError):
            fibonacci(-1)

    def test_invalid_type_float(self):
        """Test mit Float statt Integer"""
        with self.assertRaises(TypeError):
            fibonacci(5.5)

    def test_invalid_type_string(self):
        """Test mit String"""
        with self.assertRaises(TypeError):
            fibonacci("5")

    def test_invalid_type_none(self):
        """Test mit None"""
        with self.assertRaises(TypeError):
            fibonacci(None)

    def test_large_n(self):
        """Test mit größerem n"""
        result = fibonacci(20)
        self.assertEqual(len(result), 20)
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], 1)
        self.assertEqual(result[-1], 4181)  # 20. Fibonacci-Zahl


if __name__ == "__main__":
    unittest.main()

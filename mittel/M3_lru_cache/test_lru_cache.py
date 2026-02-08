"""
Unit Tests für lru_cache.py
"""

import unittest
from lru_cache import LRUCache


class TestLRUCache(unittest.TestCase):

    def test_init_valid_capacity(self):
        """Test: Cache mit gültiger Kapazität erstellen"""
        cache = LRUCache(5)
        self.assertEqual(cache.capacity, 5)
        self.assertEqual(cache.size(), 0)

    def test_init_invalid_capacity(self):
        """Test: Cache mit ungültiger Kapazität"""
        with self.assertRaises(ValueError):
            LRUCache(0)

        with self.assertRaises(ValueError):
            LRUCache(-1)

    def test_put_and_get(self):
        """Test: Element einfügen und abrufen"""
        cache = LRUCache(2)
        cache.put('key1', 'value1')
        self.assertEqual(cache.get('key1'), 'value1')

    def test_get_nonexistent_key(self):
        """Test: Nicht-existierenden Schlüssel abrufen"""
        cache = LRUCache(2)
        self.assertIsNone(cache.get('nonexistent'))

    def test_update_existing_key(self):
        """Test: Existierenden Schlüssel aktualisieren"""
        cache = LRUCache(2)
        cache.put('key1', 'value1')
        cache.put('key1', 'value2')
        self.assertEqual(cache.get('key1'), 'value2')
        self.assertEqual(cache.size(), 1)

    def test_capacity_limit(self):
        """Test: Kapazitätsgrenze wird eingehalten"""
        cache = LRUCache(2)
        cache.put('a', 1)
        cache.put('b', 2)
        cache.put('c', 3)  # 'a' sollte entfernt werden

        self.assertEqual(cache.size(), 2)
        self.assertIsNone(cache.get('a'))
        self.assertEqual(cache.get('b'), 2)
        self.assertEqual(cache.get('c'), 3)

    def test_lru_eviction(self):
        """Test: LRU Eviction - am längsten nicht verwendetes Element wird entfernt"""
        cache = LRUCache(3)
        cache.put('a', 1)
        cache.put('b', 2)
        cache.put('c', 3)

        # Rufe 'a' ab, dadurch ist 'b' das am längsten nicht verwendete Element
        cache.get('a')

        # Füge 'd' hinzu, 'b' sollte entfernt werden
        cache.put('d', 4)

        self.assertIsNone(cache.get('b'))
        self.assertEqual(cache.get('a'), 1)
        self.assertEqual(cache.get('c'), 3)
        self.assertEqual(cache.get('d'), 4)

    def test_access_updates_recency(self):
        """Test: Zugriff aktualisiert Recency"""
        cache = LRUCache(2)
        cache.put('a', 1)
        cache.put('b', 2)

        # Rufe 'a' ab
        cache.get('a')

        # Füge 'c' hinzu, 'b' sollte entfernt werden (nicht 'a')
        cache.put('c', 3)

        self.assertEqual(cache.get('a'), 1)
        self.assertIsNone(cache.get('b'))
        self.assertEqual(cache.get('c'), 3)

    def test_update_updates_recency(self):
        """Test: Update aktualisiert Recency"""
        cache = LRUCache(2)
        cache.put('a', 1)
        cache.put('b', 2)

        # Aktualisiere 'a'
        cache.put('a', 10)

        # Füge 'c' hinzu, 'b' sollte entfernt werden
        cache.put('c', 3)

        self.assertEqual(cache.get('a'), 10)
        self.assertIsNone(cache.get('b'))
        self.assertEqual(cache.get('c'), 3)

    def test_size(self):
        """Test: size() gibt korrekte Anzahl zurück"""
        cache = LRUCache(5)
        self.assertEqual(cache.size(), 0)

        cache.put('a', 1)
        self.assertEqual(cache.size(), 1)

        cache.put('b', 2)
        self.assertEqual(cache.size(), 2)

        cache.get('a')
        self.assertEqual(cache.size(), 2)

        cache.put('a', 10)
        self.assertEqual(cache.size(), 2)

    def test_clear(self):
        """Test: clear() leert den Cache"""
        cache = LRUCache(3)
        cache.put('a', 1)
        cache.put('b', 2)
        cache.clear()

        self.assertEqual(cache.size(), 0)
        self.assertIsNone(cache.get('a'))
        self.assertIsNone(cache.get('b'))

    def test_contains(self):
        """Test: __contains__ (in Operator)"""
        cache = LRUCache(2)
        cache.put('a', 1)

        self.assertTrue('a' in cache)
        self.assertFalse('b' in cache)

    def test_capacity_one(self):
        """Test: Cache mit Kapazität 1"""
        cache = LRUCache(1)
        cache.put('a', 1)
        self.assertEqual(cache.get('a'), 1)

        cache.put('b', 2)
        self.assertIsNone(cache.get('a'))
        self.assertEqual(cache.get('b'), 2)

    def test_various_data_types(self):
        """Test: Verschiedene Datentypen als Values"""
        cache = LRUCache(3)
        cache.put('str', 'string value')
        cache.put('int', 123)
        cache.put('list', [1, 2, 3])

        self.assertEqual(cache.get('str'), 'string value')
        self.assertEqual(cache.get('int'), 123)
        self.assertEqual(cache.get('list'), [1, 2, 3])


if __name__ == '__main__':
    unittest.main()

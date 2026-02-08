"""
LRU (Least Recently Used) Cache Implementation
"""

from collections import OrderedDict


class LRUCache:
    """
    LRU Cache - Speichert Key-Value Paare mit begrenzter Kapazität.
    Wenn Cache voll ist, wird das am längsten nicht verwendete Element entfernt.
    """

    def __init__(self, capacity: int):
        """
        Initialisiert den LRU Cache.

        Args:
            capacity (int): Maximale Anzahl von Elementen im Cache

        Raises:
            ValueError: Wenn Kapazität kleiner als 1 ist
        """
        if capacity < 1:
            raise ValueError("Kapazität muss mindestens 1 sein")

        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        """
        Ruft einen Wert aus dem Cache ab.

        Args:
            key: Der Schlüssel des abzurufenden Werts

        Returns:
            Der Wert wenn vorhanden, sonst None
        """
        if key not in self.cache:
            return None

        # Element als "recently used" markieren (ans Ende verschieben)
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        """
        Fügt ein Key-Value Paar in den Cache ein.

        Wenn der Schlüssel bereits existiert, wird der Wert aktualisiert.
        Wenn der Cache voll ist, wird das am längsten nicht verwendete Element entfernt.

        Args:
            key: Der Schlüssel
            value: Der Wert
        """
        # Wenn Key bereits existiert, aktualisiere und verschiebe ans Ende
        if key in self.cache:
            self.cache.move_to_end(key)
            self.cache[key] = value
            return

        # Wenn Cache voll ist, entferne ältestes Element (erstes in OrderedDict)
        if len(self.cache) >= self.capacity:
            # popitem(last=False) entfernt das erste (älteste) Element
            self.cache.popitem(last=False)

        # Füge neues Element hinzu (wird automatisch ans Ende angefügt)
        self.cache[key] = value

    def size(self):
        """
        Gibt die aktuelle Größe des Cache zurück.

        Returns:
            int: Anzahl der Elemente im Cache
        """
        return len(self.cache)

    def clear(self):
        """Leert den Cache"""
        self.cache.clear()

    def __contains__(self, key):
        """Prüft ob ein Schlüssel im Cache ist (für 'in' Operator)"""
        return key in self.cache

    def __repr__(self):
        """String-Repräsentation des Cache"""
        return f"LRUCache(capacity={self.capacity}, size={self.size()}, items={list(self.cache.items())})"


if __name__ == "__main__":
    # Beispiel-Verwendung
    cache = LRUCache(3)

    print("Füge Elemente hinzu:")
    cache.put('a', 1)
    print(f"  put('a', 1): {cache}")
    cache.put('b', 2)
    print(f"  put('b', 2): {cache}")
    cache.put('c', 3)
    print(f"  put('c', 3): {cache}")

    print("\nRufe Element ab:")
    value = cache.get('a')
    print(f"  get('a') = {value}")
    print(f"  Cache: {cache}")

    print("\nFüge weiteres Element hinzu (Cache ist voll, 'b' wird entfernt):")
    cache.put('d', 4)
    print(f"  put('d', 4): {cache}")

    print("\nPrüfe ob 'b' noch vorhanden ist:")
    print(f"  get('b') = {cache.get('b')}")

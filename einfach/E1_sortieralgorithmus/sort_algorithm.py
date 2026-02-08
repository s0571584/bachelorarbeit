"""
Sortieralgorithmus - Sortiert eine Liste von Integers
"""


def sort_numbers(numbers):
    """
    Sortiert eine Liste von Integers in aufsteigender Reihenfolge.

    Args:
        numbers (list): Liste von Integers (positiv, negativ, oder null)

    Returns:
        list: Sortierte Liste in aufsteigender Reihenfolge
    """
    if not isinstance(numbers, list):
        raise TypeError("Input muss eine Liste sein")

    # Kopie erstellen, um Original nicht zu verändern
    sorted_list = numbers.copy()

    # Bubble Sort Implementierung
    n = len(sorted_list)
    for i in range(n):
        for j in range(0, n - i - 1):
            if sorted_list[j] > sorted_list[j + 1]:
                sorted_list[j], sorted_list[j + 1] = sorted_list[j + 1], sorted_list[j]

    return sorted_list


if __name__ == "__main__":
    # Beispiel-Verwendung
    test_list = [64, 34, 25, 12, 22, 11, 90, -5, 0]
    print(f"Unsortiert: {test_list}")
    print(f"Sortiert: {sort_numbers(test_list)}")

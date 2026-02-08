"""
Fibonacci-Sequenz - Berechnet die ersten n Fibonacci-Zahlen
"""


def fibonacci(n):
    """
    Berechnet die ersten n Fibonacci-Zahlen.

    Die Fibonacci-Sequenz beginnt mit 0 und 1, und jede folgende Zahl
    ist die Summe der beiden vorherigen Zahlen.

    Args:
        n (int): Anzahl der Fibonacci-Zahlen

    Returns:
        list: Liste mit den ersten n Fibonacci-Zahlen

    Raises:
        TypeError: Wenn n kein Integer ist
        ValueError: Wenn n negativ ist
    """
    if not isinstance(n, int):
        raise TypeError("n muss ein Integer sein")

    if n < 0:
        raise ValueError("n muss nicht-negativ sein")

    if n == 0:
        return []

    if n == 1:
        return [0]

    # Fibonacci-Sequenz berechnen
    fib_sequence = [0, 1]

    for i in range(2, n):
        next_fib = fib_sequence[i - 1] + fib_sequence[i - 2]
        fib_sequence.append(next_fib)

    return fib_sequence


if __name__ == "__main__":
    # Beispiel-Verwendung
    test_cases = [0, 1, 5, 10, 15]

    for n in test_cases:
        result = fibonacci(n)
        print(f"fibonacci({n}) = {result}")

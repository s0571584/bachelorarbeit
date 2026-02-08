"""
JSON to CSV Data Transformer

Provides platform-independent conversion of JSON data to CSV format.
CRITICAL: Uses lineterminator='\\n' for consistent output across all platforms.
"""

import csv
import io
from typing import Any


def json_to_csv(data: Any) -> str:
    """
    Converts JSON data (list of dictionaries) to CSV format.

    Args:
        data: A list of dictionaries to convert. Each dictionary represents a row.

    Returns:
        A CSV-formatted string with Unix line endings (\\n only, never \\r\\n)

    Raises:
        TypeError: If data is not a list or contains non-dictionary items
        ValueError: If data is None

    Platform Independence:
        This function ALWAYS produces output with \\n line endings, regardless
        of the platform (Windows, Linux, macOS). This is achieved by:
        - Using io.StringIO with newline='' parameter
        - Using csv.DictWriter with lineterminator='\\n'

    Edge Cases Handled:
        - Empty list returns empty string
        - None input raises ValueError
        - Non-list input raises TypeError
        - Non-dictionary items raise TypeError
        - Dictionaries with different keys (union of all keys used)
        - None values in dictionaries (rendered as empty string)
        - Special characters (commas, quotes, newlines) properly escaped
    """
    # Handle None input
    if data is None:
        raise ValueError("Input data cannot be None")

    # Handle non-list input
    if not isinstance(data, list):
        raise TypeError("Input must be a list of dictionaries")

    # Handle empty list
    if not data:
        return ""

    # Validate all items are dictionaries and collect all unique keys
    fieldnames = []
    for item in data:
        if not isinstance(item, dict):
            raise TypeError("All items must be dictionaries")
        for key in item.keys():
            if key not in fieldnames:
                fieldnames.append(key)

    # CRITICAL: newline='' and lineterminator='\\n' for platform independence
    # This ensures output is ALWAYS \\n only, never \\r\\n (Windows) or \\r (old Mac)
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator='\n')

    # Write header and rows
    writer.writeheader()
    writer.writerows(data)

    return output.getvalue()

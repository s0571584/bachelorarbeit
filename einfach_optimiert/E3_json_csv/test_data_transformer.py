"""
Unit Tests for JSON to CSV Data Transformer

Comprehensive test suite with focus on platform independence.
"""

import pytest
from data_transformer import json_to_csv


class TestBasicConversion:
    """Test cases for basic JSON to CSV conversion"""

    def test_single_dict(self):
        """Test conversion of single dictionary"""
        data = [{"name": "Alice", "age": 30}]
        result = json_to_csv(data)
        expected = "name,age\nAlice,30\n"
        assert result == expected

    def test_multiple_dicts(self):
        """Test conversion of multiple dictionaries"""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ]
        result = json_to_csv(data)
        expected = "name,age\nAlice,30\nBob,25\n"
        assert result == expected

    def test_single_column(self):
        """Test conversion with single column"""
        data = [{"id": 1}, {"id": 2}, {"id": 3}]
        result = json_to_csv(data)
        expected = "id\n1\n2\n3\n"
        assert result == expected

    def test_multiple_columns(self):
        """Test conversion with multiple columns"""
        data = [{"name": "Alice", "age": 30, "city": "NYC", "country": "USA"}]
        result = json_to_csv(data)
        # Check that all columns are present
        assert "name" in result
        assert "age" in result
        assert "city" in result
        assert "country" in result
        assert "Alice" in result


class TestPlatformIndependence:
    """Test cases specifically for platform independence"""

    def test_only_unix_line_endings(self):
        """CRITICAL: Output must contain ONLY \\n, never \\r\\n"""
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        result = json_to_csv(data)

        # CRITICAL ASSERTION: No Windows line endings
        assert '\r\n' not in result, "Output must not contain Windows line endings (\\r\\n)"
        assert '\r' not in result, "Output must not contain carriage returns (\\r)"

        # Verify Unix line endings are present
        assert '\n' in result, "Output must contain Unix line endings (\\n)"

    def test_line_ending_count(self):
        """Test that we have exactly the expected number of line breaks"""
        data = [{"a": 1}, {"a": 2}, {"a": 3}]
        result = json_to_csv(data)

        # Should have: header line + 3 data lines = 4 lines total
        # Each line ends with \n, so 4 \n characters
        assert result.count('\n') == 4

    def test_no_platform_specific_separators(self):
        """Ensure no platform-specific line separators are used"""
        data = [{"x": "test"}]
        result = json_to_csv(data)

        # Split by \n should give us exactly 3 parts: header, data, empty string after final \n
        parts = result.split('\n')
        assert len(parts) == 3
        assert parts[0] == "x"
        assert parts[1] == "test"
        assert parts[2] == ""


class TestEdgeCases:
    """Test cases for edge cases and error handling"""

    def test_empty_list(self):
        """Test that empty list returns empty string"""
        data = []
        result = json_to_csv(data)
        assert result == ""

    def test_none_input(self):
        """Test that None input raises ValueError"""
        with pytest.raises(ValueError, match="Input data cannot be None"):
            json_to_csv(None)

    def test_non_list_input_string(self):
        """Test that non-list input raises TypeError"""
        with pytest.raises(TypeError, match="Input must be a list"):
            json_to_csv("not a list")

    def test_non_list_input_dict(self):
        """Test that dict input raises TypeError"""
        with pytest.raises(TypeError, match="Input must be a list"):
            json_to_csv({"name": "Alice"})

    def test_non_dict_items(self):
        """Test that list with non-dict items raises TypeError"""
        with pytest.raises(TypeError, match="All items must be dictionaries"):
            json_to_csv([{"name": "Alice"}, "not a dict"])

    def test_different_keys(self):
        """Test dictionaries with different keys (union of all keys)"""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "city": "NYC"}
        ]
        result = json_to_csv(data)

        # Should contain all keys from both dicts
        assert "name" in result
        assert "age" in result
        assert "city" in result

        # Check that missing values are handled (empty in CSV)
        lines = result.strip().split('\n')
        assert len(lines) == 3  # header + 2 data rows

    def test_none_values(self):
        """Test that None values in dictionaries are handled correctly"""
        data = [{"name": "Alice", "age": None}]
        result = json_to_csv(data)

        # None should be rendered as empty string in CSV
        expected = "name,age\nAlice,\n"
        assert result == expected


class TestSpecialCharacters:
    """Test cases for special character handling"""

    def test_comma_in_value(self):
        """Test that commas in values are properly escaped"""
        data = [{"name": "Smith, John"}]
        result = json_to_csv(data)

        # CSV should quote values with commas
        assert '"Smith, John"' in result

    def test_quotes_in_value(self):
        """Test that quotes in values are properly escaped"""
        data = [{"text": 'He said "hello"'}]
        result = json_to_csv(data)

        # CSV should escape quotes by doubling them
        assert '""' in result or 'He said "hello"' in result

    def test_newline_in_value(self):
        """Test that newlines in values are properly escaped"""
        data = [{"text": "Line 1\nLine 2"}]
        result = json_to_csv(data)

        # The value should be quoted, and newline preserved inside quotes
        # The final output still has only \n line endings (not \r\n)
        assert '\r\n' not in result

    def test_multiple_special_chars(self):
        """Test value with multiple special characters"""
        data = [{"text": "Item 1, \"quoted\", value\nNext line"}]
        result = json_to_csv(data)

        # Should handle all special chars, and no \r\n should appear
        assert '\r\n' not in result
        assert '\n' in result  # At least line endings


class TestKeyOrdering:
    """Test cases for key ordering and consistency"""

    def test_key_order_preserved_from_first_occurrence(self):
        """Test that keys appear in order of first occurrence"""
        data = [
            {"c": 3, "a": 1, "b": 2},
            {"b": 5, "a": 4, "c": 6}
        ]
        result = json_to_csv(data)
        lines = result.split('\n')
        header = lines[0]

        # Keys should appear in order of first dict: c, a, b
        assert header == "c,a,b"

    def test_new_keys_appended(self):
        """Test that new keys from later dicts are appended"""
        data = [
            {"a": 1},
            {"a": 2, "b": 2},
            {"a": 3, "b": 3, "c": 3}
        ]
        result = json_to_csv(data)
        lines = result.split('\n')
        header = lines[0]

        # Keys should be in order: a (from dict 1), b (from dict 2), c (from dict 3)
        assert header == "a,b,c"


class TestRobustness:
    """Additional robustness tests"""

    def test_integer_values(self):
        """Test that integer values are handled correctly"""
        data = [{"count": 42, "score": 100}]
        result = json_to_csv(data)
        assert "42" in result
        assert "100" in result

    def test_float_values(self):
        """Test that float values are handled correctly"""
        data = [{"price": 19.99, "tax": 1.5}]
        result = json_to_csv(data)
        assert "19.99" in result
        assert "1.5" in result

    def test_boolean_values(self):
        """Test that boolean values are handled correctly"""
        data = [{"active": True, "verified": False}]
        result = json_to_csv(data)
        assert "True" in result
        assert "False" in result

    def test_mixed_types(self):
        """Test that mixed value types are handled correctly"""
        data = [{"name": "Alice", "age": 30, "score": 95.5, "active": True}]
        result = json_to_csv(data)
        assert "Alice" in result
        assert "30" in result
        assert "95.5" in result
        assert "True" in result

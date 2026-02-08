"""
Data Validation Framework - Validiert Daten basierend auf einem Schema
"""

from typing import Dict, Any, List


class ValidationResult:
    """
    Ergebnis einer Validierung
    """

    def __init__(self, is_valid: bool, errors: List[str] = None):
        """
        Args:
            is_valid (bool): True wenn Daten gültig sind
            errors (List[str]): Liste von Fehlermeldungen
        """
        self.is_valid = is_valid
        self.errors = errors if errors else []

    def __repr__(self):
        return f"ValidationResult(is_valid={self.is_valid}, errors={self.errors})"


class DataValidator:
    """
    Data Validator - Validiert Daten basierend auf einem Schema
    """

    VALID_TYPES = {
        'str': str,
        'int': int,
        'float': float,
        'bool': bool,
        'list': list,
        'dict': dict
    }

    def validate(self, data: Dict[str, Any], schema: Dict[str, Dict[str, Any]]) -> ValidationResult:
        """
        Validiert Daten basierend auf einem Schema.

        Args:
            data (dict): Die zu validierenden Daten
            schema (dict): Das Validierungs-Schema

        Returns:
            ValidationResult: Validierungsergebnis mit Erfolg und Fehlern

        Schema-Format:
            {
                "field_name": {
                    "type": "str|int|float|bool|list|dict",
                    "required": True|False,
                    "min": number,  # Minimum (für int, float, str-Länge, list-Länge)
                    "max": number,  # Maximum (für int, float, str-Länge, list-Länge)
                    "min_length": number,  # Alias für min (für Strings und Listen)
                    "max_length": number   # Alias für max (für Strings und Listen)
                }
            }
        """
        if not isinstance(data, dict):
            return ValidationResult(False, ["Data muss ein Dictionary sein"])

        if not isinstance(schema, dict):
            return ValidationResult(False, ["Schema muss ein Dictionary sein"])

        errors = []

        # Prüfe alle Felder im Schema
        for field_name, field_schema in schema.items():
            field_errors = self._validate_field(field_name, data.get(field_name), field_schema)
            errors.extend(field_errors)

        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors)

    def validate_field(self, value, field_type, constraints):
        """
        Validiert ein einzelnes Feld mit allen Constraints.

        Args:
            value: Wert des Feldes
            field_type (str): Typ des Feldes
            constraints (dict): Constraints für das Feld

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        # String Validierung
        if field_type == "string":
            if not isinstance(value, str):
                return False, "Expected string"
            if "min_length" in constraints and len(value) < constraints["min_length"]:
                return False, f"Minimum length is {constraints['min_length']}"
            if "max_length" in constraints and len(value) > constraints["max_length"]:
                return False, f"Maximum length is {constraints['max_length']}"
            if "pattern" in constraints:
                import re
                if not re.match(constraints["pattern"], value):
                    return False, "Pattern mismatch"
            if "enum" in constraints and value not in constraints["enum"]:
                return False, f"Value must be one of {constraints['enum']}"
            return True, ""

        # Integer Validierung
        elif field_type == "int":
            if not isinstance(value, int) or isinstance(value, bool):
                return False, "Expected integer"
            if "min" in constraints and value < constraints["min"]:
                return False, f"Minimum value is {constraints['min']}"
            if "max" in constraints and value > constraints["max"]:
                return False, f"Maximum value is {constraints['max']}"
            if "enum" in constraints and value not in constraints["enum"]:
                return False, f"Value must be one of {constraints['enum']}"
            return True, ""

        # Float Validierung
        elif field_type == "float":
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                return False, "Expected float"
            if "min" in constraints and value < constraints["min"]:
                return False, f"Minimum value is {constraints['min']}"
            if "max" in constraints and value > constraints["max"]:
                return False, f"Maximum value is {constraints['max']}"
            if "precision" in constraints:
                decimal_places = len(str(value).split('.')[-1])
                if decimal_places > constraints["precision"]:
                    return False, f"Maximum precision is {constraints['precision']}"
            return True, ""

        # Boolean Validierung
        elif field_type == "bool":
            if not isinstance(value, bool):
                return False, "Expected boolean"
            return True, ""

        # List Validierung
        elif field_type == "list":
            if not isinstance(value, list):
                return False, "Expected list"
            if "min_length" in constraints and len(value) < constraints["min_length"]:
                return False, f"Minimum length is {constraints['min_length']}"
            if "max_length" in constraints and len(value) > constraints["max_length"]:
                return False, f"Maximum length is {constraints['max_length']}"
            if "item_type" in constraints:
                for item in value:
                    is_valid, error = self.validate_field(item, constraints["item_type"], {})
                    if not is_valid:
                        return False, f"Invalid list item: {error}"
            return True, ""

        # Dict Validierung
        elif field_type == "dict":
            if not isinstance(value, dict):
                return False, "Expected dictionary"
            return True, ""

        else:
            return False, f"Unknown field type: {field_type}"

    def _validate_field(self, field_name: str, value: Any, field_schema: Dict[str, Any]) -> List[str]:
        """
        Validiert ein einzelnes Feld basierend auf dem Schema.
        """
        errors = []

        # Prüfe required
        is_required = field_schema.get('required', False)
        if is_required and value is None:
            errors.append(f"Feld '{field_name}' ist erforderlich")
            return errors

        # Wenn optional und nicht vorhanden, ist das OK
        if value is None:
            return errors

        # Prüfe Typ
        field_type = field_schema.get('type', 'str')
        expected_type = self.VALID_TYPES.get(field_type)

        if expected_type is None:
            errors.append(f"Feld '{field_name}': Unbekannter Typ '{field_type}'")
            return errors

        # Spezielle Behandlung für bool (bool ist Subklasse von int in Python)
        if field_type == 'bool':
            if not isinstance(value, bool):
                errors.append(f"Feld '{field_name}': Erwartet bool, erhalten {type(value).__name__}")
                return errors
        elif field_type == 'int':
            if not isinstance(value, int) or isinstance(value, bool):
                errors.append(f"Feld '{field_name}': Erwartet int, erhalten {type(value).__name__}")
                return errors
        elif not isinstance(value, expected_type):
            errors.append(f"Feld '{field_name}': Erwartet {field_type}, erhalten {type(value).__name__}")
            return errors

        # Validiere Constraints
        if field_type == 'str':
            min_length = field_schema.get('min_length')
            max_length = field_schema.get('max_length')
            if min_length is not None and len(value) < min_length:
                errors.append(f"Feld '{field_name}': Mindestlänge ist {min_length}")
            if max_length is not None and len(value) > max_length:
                errors.append(f"Feld '{field_name}': Maximallänge ist {max_length}")

        elif field_type == 'int' or field_type == 'float':
            min_val = field_schema.get('min')
            max_val = field_schema.get('max')
            if min_val is not None and value < min_val:
                errors.append(f"Feld '{field_name}': Minimalwert ist {min_val}")
            if max_val is not None and value > max_val:
                errors.append(f"Feld '{field_name}': Maximalwert ist {max_val}")

        elif field_type == 'list':
            min_length = field_schema.get('min_length')
            max_length = field_schema.get('max_length')
            if min_length is not None and len(value) < min_length:
                errors.append(f"Feld '{field_name}': Mindestlänge ist {min_length}")
            if max_length is not None and len(value) > max_length:
                errors.append(f"Feld '{field_name}': Maximallänge ist {max_length}")

        return errors


if __name__ == "__main__":
    # Beispiel-Verwendung
    validator = DataValidator()

    # Schema definieren
    schema = {
        "name": {"type": "str", "required": True, "min_length": 2, "max_length": 50},
        "age": {"type": "int", "required": True, "min": 0, "max": 150},
        "email": {"type": "str", "required": True},
        "hobbies": {"type": "list", "required": False, "min_length": 1}
    }

    # Gültige Daten
    valid_data = {
        "name": "Alice",
        "age": 30,
        "email": "alice@example.com",
        "hobbies": ["reading", "coding"]
    }

    result = validator.validate(valid_data, schema)
    print(f"Gültige Daten: {result}")

    # Ungültige Daten
    invalid_data = {
        "name": "A",  # Zu kurz
        "age": 200,  # Zu groß
        "email": "alice@example.com"
        # hobbies fehlt (aber nicht required)
    }

    result = validator.validate(invalid_data, schema)
    print(f"\nUngültige Daten: {result}")

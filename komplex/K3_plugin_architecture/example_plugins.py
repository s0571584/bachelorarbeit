"""
Example Plugins - Beispiel-Implementierungen von Plugins
"""

from plugin_interface import PluginInterface
from typing import Any, Dict
import logging
import re


class LoggerPlugin(PluginInterface):
    """
    Logger Plugin - Loggt Nachrichten
    """

    def __init__(self):
        """Initialisiert das Logger Plugin"""
        self.logger = None
        self.log_level = logging.INFO

    def get_name(self) -> str:
        return "LoggerPlugin"

    def get_version(self) -> str:
        return "1.0.0"

    def get_description(self) -> str:
        return "Plugin zum Loggen von Nachrichten"

    def initialize(self, config: Dict[str, Any] = None) -> bool:
        """
        Initialisiert den Logger.

        Args:
            config: {'log_level': 'INFO'|'DEBUG'|'WARNING'|'ERROR'}
        """
        if config and 'log_level' in config:
            level_str = config['log_level'].upper()
            self.log_level = getattr(logging, level_str, logging.INFO)

        self.logger = logging.getLogger(self.get_name())
        self.logger.setLevel(self.log_level)

        # Handler hinzufügen, falls noch keiner vorhanden
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(self.log_level)
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        return True

    def execute(self, message: str, level: str = 'INFO') -> Any:
        """
        Loggt eine Nachricht.

        Args:
            message (str): Die zu loggende Nachricht
            level (str): Log-Level ('INFO', 'DEBUG', 'WARNING', 'ERROR')

        Returns:
            bool: True wenn erfolgreich geloggt
        """
        if not self.logger:
            return False

        level_method = getattr(self.logger, level.lower(), self.logger.info)
        level_method(message)
        return True

    def shutdown(self) -> bool:
        """Fährt den Logger herunter"""
        if self.logger:
            for handler in self.logger.handlers:
                handler.close()
            self.logger.handlers.clear()
        return True


class ValidatorPlugin(PluginInterface):
    """
    Validator Plugin - Validiert Daten
    """

    def __init__(self):
        """Initialisiert das Validator Plugin"""
        self.validators = {}

    def get_name(self) -> str:
        return "ValidatorPlugin"

    def get_version(self) -> str:
        return "1.0.0"

    def get_description(self) -> str:
        return "Plugin zur Datenvalidierung"

    def initialize(self, config: Dict[str, Any] = None) -> bool:
        """
        Initialisiert Standard-Validatoren.
        """
        # Email Validator
        self.validators['email'] = lambda x: bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', x))

        # Numeric Validator
        self.validators['numeric'] = lambda x: str(x).replace('.', '', 1).isdigit()

        # Non-empty Validator
        self.validators['non_empty'] = lambda x: bool(x and str(x).strip())

        return True

    def execute(self, data: Any, validator_name: str) -> bool:
        """
        Validiert Daten mit einem bestimmten Validator.

        Args:
            data (Any): Zu validierende Daten
            validator_name (str): Name des Validators

        Returns:
            bool: True wenn gültig, False sonst
        """
        if validator_name not in self.validators:
            raise ValueError(f"Validator '{validator_name}' nicht gefunden")

        return self.validators[validator_name](data)

    def add_validator(self, name: str, validator_fn):
        """
        Fügt einen custom Validator hinzu.

        Args:
            name (str): Name des Validators
            validator_fn (Callable): Validator-Funktion
        """
        self.validators[name] = validator_fn

    def shutdown(self) -> bool:
        """Fährt den Validator herunter"""
        self.validators.clear()
        return True


class TransformPlugin(PluginInterface):
    """
    Transform Plugin - Transformiert Daten
    """

    def __init__(self):
        """Initialisiert das Transform Plugin"""
        self.transformations = {}

    def get_name(self) -> str:
        return "TransformPlugin"

    def get_version(self) -> str:
        return "1.0.0"

    def get_description(self) -> str:
        return "Plugin zur Datentransformation"

    def initialize(self, config: Dict[str, Any] = None) -> bool:
        """
        Initialisiert Standard-Transformationen.
        """
        # Uppercase Transformation
        self.transformations['uppercase'] = lambda x: str(x).upper()

        # Lowercase Transformation
        self.transformations['lowercase'] = lambda x: str(x).lower()

        # Strip Transformation
        self.transformations['strip'] = lambda x: str(x).strip()

        # Reverse Transformation
        self.transformations['reverse'] = lambda x: str(x)[::-1]

        return True

    def execute(self, data: Any, transformation_name: str) -> Any:
        """
        Transformiert Daten mit einer bestimmten Transformation.

        Args:
            data (Any): Zu transformierende Daten
            transformation_name (str): Name der Transformation

        Returns:
            Any: Transformierte Daten
        """
        if transformation_name not in self.transformations:
            raise ValueError(f"Transformation '{transformation_name}' nicht gefunden")

        return self.transformations[transformation_name](data)

    def add_transformation(self, name: str, transform_fn):
        """
        Fügt eine custom Transformation hinzu.

        Args:
            name (str): Name der Transformation
            transform_fn (Callable): Transformations-Funktion
        """
        self.transformations[name] = transform_fn

    def shutdown(self) -> bool:
        """Fährt das Transform Plugin herunter"""
        self.transformations.clear()
        return True


if __name__ == "__main__":
    # Setup Logging
    logging.basicConfig(level=logging.INFO)

    # Test LoggerPlugin
    print("=== LoggerPlugin Test ===")
    logger_plugin = LoggerPlugin()
    logger_plugin.initialize({'log_level': 'INFO'})
    logger_plugin.execute("Test message", "INFO")
    logger_plugin.shutdown()

    # Test ValidatorPlugin
    print("\n=== ValidatorPlugin Test ===")
    validator_plugin = ValidatorPlugin()
    validator_plugin.initialize()
    print(f"Email valid: {validator_plugin.execute('test@example.com', 'email')}")
    print(f"Email invalid: {validator_plugin.execute('invalid-email', 'email')}")
    validator_plugin.shutdown()

    # Test TransformPlugin
    print("\n=== TransformPlugin Test ===")
    transform_plugin = TransformPlugin()
    transform_plugin.initialize()
    print(f"Uppercase: {transform_plugin.execute('hello', 'uppercase')}")
    print(f"Reverse: {transform_plugin.execute('hello', 'reverse')}")
    transform_plugin.shutdown()

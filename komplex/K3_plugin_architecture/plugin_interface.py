"""
Plugin Interface - Definiert das Interface für Plugins
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class PluginInterface(ABC):
    """
    Abstract Base Class für Plugins.
    Alle Plugins müssen dieses Interface implementieren.
    """

    @abstractmethod
    def get_name(self) -> str:
        """
        Gibt den Namen des Plugins zurück.

        Returns:
            str: Plugin-Name
        """
        pass

    @abstractmethod
    def get_version(self) -> str:
        """
        Gibt die Version des Plugins zurück.

        Returns:
            str: Plugin-Version
        """
        pass

    @abstractmethod
    def initialize(self, config: Dict[str, Any] = None) -> bool:
        """
        Initialisiert das Plugin.

        Args:
            config (Dict[str, Any], optional): Konfiguration für das Plugin

        Returns:
            bool: True wenn Initialisierung erfolgreich
        """
        pass

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """
        Führt die Haupt-Funktionalität des Plugins aus.

        Args:
            *args: Positionsargumente
            **kwargs: Keyword-Argumente

        Returns:
            Any: Ergebnis der Plugin-Ausführung
        """
        pass

    @abstractmethod
    def shutdown(self) -> bool:
        """
        Fährt das Plugin herunter und gibt Ressourcen frei.

        Returns:
            bool: True wenn Shutdown erfolgreich
        """
        pass

    def get_description(self) -> str:
        """
        Gibt eine Beschreibung des Plugins zurück.

        Returns:
            str: Plugin-Beschreibung
        """
        return "Keine Beschreibung verfügbar"

    def get_metadata(self) -> Dict[str, Any]:
        """
        Gibt Metadata des Plugins zurück.

        Returns:
            Dict[str, Any]: Metadata
        """
        return {
            'name': self.get_name(),
            'version': self.get_version(),
            'description': self.get_description()
        }


if __name__ == "__main__":
    # Beispiel-Plugin
    class ExamplePlugin(PluginInterface):
        def get_name(self):
            return "ExamplePlugin"

        def get_version(self):
            return "1.0.0"

        def initialize(self, config=None):
            print("ExamplePlugin initialized")
            return True

        def execute(self, *args, **kwargs):
            print("ExamplePlugin executed")
            return "Success"

        def shutdown(self):
            print("ExamplePlugin shutdown")
            return True

    # Plugin verwenden
    plugin = ExamplePlugin()
    print(f"Plugin: {plugin.get_name()} v{plugin.get_version()}")
    plugin.initialize()
    result = plugin.execute()
    print(f"Result: {result}")
    plugin.shutdown()

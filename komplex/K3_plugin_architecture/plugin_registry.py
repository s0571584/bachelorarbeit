"""
Plugin Registry - Verwaltet registrierte Plugins
"""

from typing import Dict, List, Optional, Type
from plugin_interface import PluginInterface
import logging


class PluginRegistry:
    """
    Plugin Registry - Verwaltet alle registrierten Plugins
    """

    def __init__(self):
        """Initialisiert die Plugin Registry"""
        self.plugins: Dict[str, PluginInterface] = {}
        self.plugin_classes: Dict[str, Type[PluginInterface]] = {}
        self.logger = logging.getLogger(__name__)

    def register_plugin_class(self, plugin_class: Type[PluginInterface]) -> bool:
        """
        Registriert eine Plugin-Klasse.

        Args:
            plugin_class (Type[PluginInterface]): Plugin-Klasse

        Returns:
            bool: True wenn erfolgreich registriert

        Raises:
            ValueError: Wenn Plugin-Klasse nicht PluginInterface implementiert
        """
        # Prüfe ob Klasse PluginInterface implementiert
        if not issubclass(plugin_class, PluginInterface):
            raise ValueError(f"{plugin_class.__name__} implementiert nicht PluginInterface")

        # Erstelle temporäre Instanz, um Namen zu erhalten
        temp_instance = plugin_class()
        plugin_name = temp_instance.get_name()

        if plugin_name in self.plugin_classes:
            self.logger.warning(f"Plugin-Klasse '{plugin_name}' bereits registriert, wird überschrieben")

        self.plugin_classes[plugin_name] = plugin_class
        self.logger.info(f"Plugin-Klasse '{plugin_name}' registriert")
        return True

    def register_plugin_instance(self, plugin_instance: PluginInterface) -> bool:
        """
        Registriert eine Plugin-Instanz.

        Args:
            plugin_instance (PluginInterface): Plugin-Instanz

        Returns:
            bool: True wenn erfolgreich registriert

        Raises:
            ValueError: Wenn Plugin nicht PluginInterface implementiert
        """
        if not isinstance(plugin_instance, PluginInterface):
            raise ValueError("Plugin implementiert nicht PluginInterface")

        plugin_name = plugin_instance.get_name()

        if plugin_name in self.plugins:
            self.logger.warning(f"Plugin '{plugin_name}' bereits registriert, wird überschrieben")

        self.plugins[plugin_name] = plugin_instance
        self.logger.info(f"Plugin '{plugin_name}' registriert")
        return True

    def get_plugin(self, plugin_name: str) -> Optional[PluginInterface]:
        """
        Gibt eine Plugin-Instanz zurück.

        Args:
            plugin_name (str): Name des Plugins

        Returns:
            Optional[PluginInterface]: Plugin-Instanz oder None
        """
        return self.plugins.get(plugin_name)

    def get_plugin_class(self, plugin_name: str) -> Optional[Type[PluginInterface]]:
        """
        Gibt eine Plugin-Klasse zurück.

        Args:
            plugin_name (str): Name des Plugins

        Returns:
            Optional[Type[PluginInterface]]: Plugin-Klasse oder None
        """
        return self.plugin_classes.get(plugin_name)

    def unregister_plugin(self, plugin_name: str) -> bool:
        """
        Deregistriert ein Plugin.

        Args:
            plugin_name (str): Name des Plugins

        Returns:
            bool: True wenn erfolgreich deregistriert
        """
        if plugin_name in self.plugins:
            # Shutdown aufrufen, bevor Plugin entfernt wird
            plugin = self.plugins[plugin_name]
            plugin.shutdown()
            del self.plugins[plugin_name]
            self.logger.info(f"Plugin '{plugin_name}' deregistriert")
            return True

        return False

    def list_plugins(self) -> List[str]:
        """
        Gibt eine Liste aller registrierten Plugins zurück.

        Returns:
            List[str]: Liste von Plugin-Namen
        """
        return list(self.plugins.keys())

    def list_plugin_classes(self) -> List[str]:
        """
        Gibt eine Liste aller registrierten Plugin-Klassen zurück.

        Returns:
            List[str]: Liste von Plugin-Namen
        """
        return list(self.plugin_classes.keys())

    def get_plugin_metadata(self, plugin_name: str) -> Optional[Dict]:
        """
        Gibt Metadata eines Plugins zurück.

        Args:
            plugin_name (str): Name des Plugins

        Returns:
            Optional[Dict]: Metadata oder None
        """
        plugin = self.get_plugin(plugin_name)
        if plugin:
            return plugin.get_metadata()
        return None

    def clear(self):
        """Entfernt alle Plugins"""
        # Shutdown für alle Plugins aufrufen
        for plugin in self.plugins.values():
            plugin.shutdown()

        self.plugins.clear()
        self.plugin_classes.clear()
        self.logger.info("Alle Plugins entfernt")


if __name__ == "__main__":
    # Setup Logging
    logging.basicConfig(level=logging.INFO)

    # Beispiel-Verwendung
    from plugin_interface import PluginInterface

    class TestPlugin(PluginInterface):
        def get_name(self):
            return "TestPlugin"

        def get_version(self):
            return "1.0.0"

        def initialize(self, config=None):
            return True

        def execute(self, *args, **kwargs):
            return "Test executed"

        def shutdown(self):
            return True

    registry = PluginRegistry()

    # Plugin-Klasse registrieren
    registry.register_plugin_class(TestPlugin)
    print(f"Registrierte Plugin-Klassen: {registry.list_plugin_classes()}")

    # Plugin-Instanz erstellen und registrieren
    plugin_instance = TestPlugin()
    registry.register_plugin_instance(plugin_instance)
    print(f"Registrierte Plugins: {registry.list_plugins()}")

    # Plugin abrufen und verwenden
    plugin = registry.get_plugin("TestPlugin")
    if plugin:
        print(f"Metadata: {plugin.get_metadata()}")

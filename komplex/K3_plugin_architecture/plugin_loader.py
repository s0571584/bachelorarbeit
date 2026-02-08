"""
Plugin Loader - Lädt Plugins dynamisch
"""

import importlib.util
import inspect
import os
from typing import List, Optional, Type
from plugin_interface import PluginInterface
from plugin_registry import PluginRegistry
import logging


class PluginLoader:
    """
    Plugin Loader - Lädt Plugins dynamisch aus Dateien oder Modulen
    """

    def __init__(self, registry: PluginRegistry):
        """
        Initialisiert den Plugin Loader.

        Args:
            registry (PluginRegistry): Plugin Registry
        """
        self.registry = registry
        self.logger = logging.getLogger(__name__)

    def load_plugin_from_file(self, filepath: str) -> bool:
        """
        Lädt ein Plugin aus einer Python-Datei.

        Args:
            filepath (str): Pfad zur Plugin-Datei

        Returns:
            bool: True wenn erfolgreich geladen

        Raises:
            FileNotFoundError: Wenn Datei nicht existiert
            ValueError: Wenn keine Plugin-Klasse gefunden wurde
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Plugin-Datei nicht gefunden: {filepath}")

        # Modul-Namen aus Datei ableiten
        module_name = os.path.splitext(os.path.basename(filepath))[0]

        try:
            # Modul laden
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Alle Klassen im Modul durchsuchen
            plugin_classes = []
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Prüfe ob Klasse PluginInterface implementiert (aber nicht PluginInterface selbst ist)
                if issubclass(obj, PluginInterface) and obj is not PluginInterface:
                    plugin_classes.append(obj)

            if not plugin_classes:
                raise ValueError(f"Keine Plugin-Klasse in Datei gefunden: {filepath}")

            # Registriere alle gefundenen Plugin-Klassen
            for plugin_class in plugin_classes:
                self.registry.register_plugin_class(plugin_class)
                self.logger.info(f"Plugin aus Datei geladen: {plugin_class.__name__}")

            return True

        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Plugin-Datei: {e}")
            raise

    def load_plugin_from_module(self, module_name: str, class_name: str) -> bool:
        """
        Lädt ein Plugin aus einem Modul.

        Args:
            module_name (str): Name des Moduls
            class_name (str): Name der Plugin-Klasse

        Returns:
            bool: True wenn erfolgreich geladen

        Raises:
            ImportError: Wenn Modul nicht importiert werden kann
            ValueError: Wenn Klasse nicht gefunden wurde
        """
        try:
            # Modul importieren
            module = importlib.import_module(module_name)

            # Klasse abrufen
            if not hasattr(module, class_name):
                raise ValueError(f"Klasse '{class_name}' nicht in Modul '{module_name}' gefunden")

            plugin_class = getattr(module, class_name)

            # Prüfe ob Klasse PluginInterface implementiert
            if not issubclass(plugin_class, PluginInterface):
                raise ValueError(f"Klasse '{class_name}' implementiert nicht PluginInterface")

            # Registriere Plugin-Klasse
            self.registry.register_plugin_class(plugin_class)
            self.logger.info(f"Plugin aus Modul geladen: {module_name}.{class_name}")

            return True

        except Exception as e:
            self.logger.error(f"Fehler beim Laden des Plugin-Moduls: {e}")
            raise

    def load_plugins_from_directory(self, directory: str) -> int:
        """
        Lädt alle Plugins aus einem Verzeichnis.

        Args:
            directory (str): Pfad zum Verzeichnis

        Returns:
            int: Anzahl der geladenen Plugins

        Raises:
            FileNotFoundError: Wenn Verzeichnis nicht existiert
        """
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Verzeichnis nicht gefunden: {directory}")

        if not os.path.isdir(directory):
            raise ValueError(f"Pfad ist kein Verzeichnis: {directory}")

        loaded_count = 0

        # Durchsuche alle Python-Dateien im Verzeichnis
        for filename in os.listdir(directory):
            if filename.endswith('.py') and not filename.startswith('__'):
                filepath = os.path.join(directory, filename)

                try:
                    self.load_plugin_from_file(filepath)
                    loaded_count += 1
                except Exception as e:
                    self.logger.warning(f"Fehler beim Laden von {filename}: {e}")

        self.logger.info(f"{loaded_count} Plugins aus Verzeichnis geladen: {directory}")
        return loaded_count

    def execute_plugin_code(self, code: str) -> any:
        """
        Führt Plugin-Code dynamisch aus.

        Args:
            code (str): Python-Code als String

        Returns:
            any: Ergebnis der Code-Ausführung
        """
        result = eval(code)
        return result

    def execute_plugin_script(self, script: str) -> None:
        """
        Führt ein Plugin-Script aus.

        Args:
            script (str): Python-Script als String
        """
        exec(script)

    def instantiate_plugin(self, plugin_name: str, config: dict = None) -> Optional[PluginInterface]:
        """
        Erstellt eine Instanz eines registrierten Plugins.

        Args:
            plugin_name (str): Name des Plugins
            config (dict, optional): Konfiguration für das Plugin

        Returns:
            Optional[PluginInterface]: Plugin-Instanz oder None

        Raises:
            ValueError: Wenn Plugin nicht gefunden wurde
        """
        plugin_class = self.registry.get_plugin_class(plugin_name)

        if not plugin_class:
            raise ValueError(f"Plugin-Klasse '{plugin_name}' nicht gefunden")

        # Plugin-Instanz erstellen
        plugin_instance = plugin_class()

        if config and 'init_code' in config:
            init_code = config['init_code']
            result = eval(init_code)
            plugin_instance.custom_config = result

        # Initialisieren
        if plugin_instance.initialize(config):
            # In Registry registrieren
            self.registry.register_plugin_instance(plugin_instance)
            self.logger.info(f"Plugin-Instanz erstellt: {plugin_name}")
            return plugin_instance
        else:
            self.logger.error(f"Initialisierung von Plugin '{plugin_name}' fehlgeschlagen")
            return None


if __name__ == "__main__":
    # Setup Logging
    logging.basicConfig(level=logging.INFO)

    # Beispiel-Verwendung
    registry = PluginRegistry()
    loader = PluginLoader(registry)

    # Versuche example_plugins.py zu laden (wenn vorhanden)
    try:
        loader.load_plugin_from_file("example_plugins.py")
        print(f"Geladene Plugin-Klassen: {registry.list_plugin_classes()}")

        # Plugin instantiieren
        if "LoggerPlugin" in registry.list_plugin_classes():
            plugin = loader.instantiate_plugin("LoggerPlugin")
            if plugin:
                result = plugin.execute("Test message")
                print(f"Plugin-Ergebnis: {result}")
    except FileNotFoundError:
        print("example_plugins.py nicht gefunden")

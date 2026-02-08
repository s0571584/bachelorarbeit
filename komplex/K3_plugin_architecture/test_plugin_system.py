"""
Unit Tests für das Plugin System
"""

import unittest
import logging
from plugin_interface import PluginInterface
from plugin_registry import PluginRegistry
from plugin_loader import PluginLoader
from example_plugins import LoggerPlugin, ValidatorPlugin, TransformPlugin


# Disable logging in tests
logging.disable(logging.CRITICAL)


class TestPluginInterface(unittest.TestCase):

    def test_plugin_implementation(self):
        """Test: Plugin-Implementierung"""

        class TestPlugin(PluginInterface):
            def get_name(self):
                return "TestPlugin"

            def get_version(self):
                return "1.0.0"

            def initialize(self, config=None):
                return True

            def execute(self, *args, **kwargs):
                return "executed"

            def shutdown(self):
                return True

        plugin = TestPlugin()
        self.assertEqual(plugin.get_name(), "TestPlugin")
        self.assertEqual(plugin.get_version(), "1.0.0")
        self.assertTrue(plugin.initialize())
        self.assertEqual(plugin.execute(), "executed")
        self.assertTrue(plugin.shutdown())

    def test_plugin_metadata(self):
        """Test: Plugin Metadata"""

        class TestPlugin(PluginInterface):
            def get_name(self):
                return "TestPlugin"

            def get_version(self):
                return "1.0.0"

            def initialize(self, config=None):
                return True

            def execute(self, *args, **kwargs):
                return "executed"

            def shutdown(self):
                return True

            def get_description(self):
                return "Test Description"

        plugin = TestPlugin()
        metadata = plugin.get_metadata()
        self.assertEqual(metadata['name'], "TestPlugin")
        self.assertEqual(metadata['version'], "1.0.0")
        self.assertEqual(metadata['description'], "Test Description")


class TestPluginRegistry(unittest.TestCase):

    def setUp(self):
        """Setup - Erstelle Registry"""
        self.registry = PluginRegistry()

    def tearDown(self):
        """Cleanup - Clear Registry"""
        self.registry.clear()

    def test_register_plugin_class(self):
        """Test: Plugin-Klasse registrieren"""

        class TestPlugin(PluginInterface):
            def get_name(self):
                return "TestPlugin"

            def get_version(self):
                return "1.0.0"

            def initialize(self, config=None):
                return True

            def execute(self, *args, **kwargs):
                return "executed"

            def shutdown(self):
                return True

        result = self.registry.register_plugin_class(TestPlugin)
        self.assertTrue(result)
        self.assertIn("TestPlugin", self.registry.list_plugin_classes())

    def test_register_invalid_plugin_class(self):
        """Test: Ungültige Plugin-Klasse registrieren"""

        class InvalidPlugin:
            pass

        with self.assertRaises(ValueError):
            self.registry.register_plugin_class(InvalidPlugin)

    def test_register_plugin_instance(self):
        """Test: Plugin-Instanz registrieren"""

        class TestPlugin(PluginInterface):
            def get_name(self):
                return "TestPlugin"

            def get_version(self):
                return "1.0.0"

            def initialize(self, config=None):
                return True

            def execute(self, *args, **kwargs):
                return "executed"

            def shutdown(self):
                return True

        plugin = TestPlugin()
        result = self.registry.register_plugin_instance(plugin)
        self.assertTrue(result)
        self.assertIn("TestPlugin", self.registry.list_plugins())

    def test_get_plugin(self):
        """Test: Plugin abrufen"""

        class TestPlugin(PluginInterface):
            def get_name(self):
                return "TestPlugin"

            def get_version(self):
                return "1.0.0"

            def initialize(self, config=None):
                return True

            def execute(self, *args, **kwargs):
                return "executed"

            def shutdown(self):
                return True

        plugin = TestPlugin()
        self.registry.register_plugin_instance(plugin)

        retrieved_plugin = self.registry.get_plugin("TestPlugin")
        self.assertIsNotNone(retrieved_plugin)
        self.assertEqual(retrieved_plugin.get_name(), "TestPlugin")

    def test_unregister_plugin(self):
        """Test: Plugin deregistrieren"""

        class TestPlugin(PluginInterface):
            def get_name(self):
                return "TestPlugin"

            def get_version(self):
                return "1.0.0"

            def initialize(self, config=None):
                return True

            def execute(self, *args, **kwargs):
                return "executed"

            def shutdown(self):
                return True

        plugin = TestPlugin()
        self.registry.register_plugin_instance(plugin)
        self.assertTrue(self.registry.unregister_plugin("TestPlugin"))
        self.assertNotIn("TestPlugin", self.registry.list_plugins())


class TestPluginLoader(unittest.TestCase):

    def setUp(self):
        """Setup - Erstelle Registry und Loader"""
        self.registry = PluginRegistry()
        self.loader = PluginLoader(self.registry)

    def tearDown(self):
        """Cleanup - Clear Registry"""
        self.registry.clear()

    def test_load_plugin_from_file(self):
        """Test: Plugin aus Datei laden"""
        # Versuche example_plugins.py zu laden
        try:
            result = self.loader.load_plugin_from_file("example_plugins.py")
            self.assertTrue(result)
            self.assertGreater(len(self.registry.list_plugin_classes()), 0)
        except FileNotFoundError:
            self.skipTest("example_plugins.py nicht gefunden")

    def test_instantiate_plugin(self):
        """Test: Plugin instantiieren"""
        # LoggerPlugin-Klasse registrieren
        self.registry.register_plugin_class(LoggerPlugin)

        # Plugin instantiieren
        plugin = self.loader.instantiate_plugin("LoggerPlugin")
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.get_name(), "LoggerPlugin")

    def test_instantiate_nonexistent_plugin(self):
        """Test: Nicht-existierendes Plugin instantiieren"""
        with self.assertRaises(ValueError):
            self.loader.instantiate_plugin("NonExistentPlugin")

    def test_load_plugin_from_nonexistent_file(self):
        """Test: Plugin aus nicht-existierender Datei laden"""
        with self.assertRaises(FileNotFoundError):
            self.loader.load_plugin_from_file("nonexistent_plugin.py")

    def test_load_plugin_from_module(self):
        """Test: Plugin aus Modul laden"""
        result = self.loader.load_plugin_from_module("example_plugins", "LoggerPlugin")
        self.assertTrue(result)
        self.assertIn("LoggerPlugin", self.registry.list_plugin_classes())

    def test_load_plugin_from_module_nonexistent_class(self):
        """Test: Plugin aus Modul laden mit nicht-existierender Klasse"""
        with self.assertRaises(ValueError):
            self.loader.load_plugin_from_module("example_plugins", "NonExistentPlugin")

    def test_load_plugin_from_module_nonexistent_module(self):
        """Test: Plugin aus nicht-existierendem Modul laden"""
        with self.assertRaises(Exception):
            self.loader.load_plugin_from_module("nonexistent_module", "SomePlugin")

    def test_execute_plugin_code(self):
        """Test: Plugin-Code dynamisch ausführen"""
        result = self.loader.execute_plugin_code("2 + 2")
        self.assertEqual(result, 4)

    def test_execute_plugin_script(self):
        """Test: Plugin-Script ausführen"""
        # Script führt Code aus ohne Return
        self.loader.execute_plugin_script("x = 10")
        # Keine Exception sollte auftreten

    def test_instantiate_plugin_with_init_code(self):
        """Test: Plugin mit init_code instantiieren"""
        self.registry.register_plugin_class(LoggerPlugin)
        config = {'init_code': '{"custom": "value"}'}
        plugin = self.loader.instantiate_plugin("LoggerPlugin", config)
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.custom_config, {"custom": "value"})

    def test_instantiate_plugin_failed_initialization(self):
        """Test: Plugin instantiieren mit fehlgeschlagener Initialisierung"""

        class FailingPlugin(PluginInterface):
            def get_name(self):
                return "FailingPlugin"

            def get_version(self):
                return "1.0.0"

            def initialize(self, config=None):
                return False  # Absichtlich fehlschlagen

            def execute(self, *args, **kwargs):
                return None

            def shutdown(self):
                return True

        self.registry.register_plugin_class(FailingPlugin)
        plugin = self.loader.instantiate_plugin("FailingPlugin")
        self.assertIsNone(plugin)


class TestExamplePlugins(unittest.TestCase):

    def test_logger_plugin(self):
        """Test: LoggerPlugin"""
        plugin = LoggerPlugin()
        self.assertEqual(plugin.get_name(), "LoggerPlugin")
        self.assertTrue(plugin.initialize())
        result = plugin.execute("Test message")
        self.assertTrue(result)
        self.assertTrue(plugin.shutdown())

    def test_validator_plugin(self):
        """Test: ValidatorPlugin"""
        plugin = ValidatorPlugin()
        self.assertEqual(plugin.get_name(), "ValidatorPlugin")
        self.assertTrue(plugin.initialize())

        # Test Email Validation
        self.assertTrue(plugin.execute("test@example.com", "email"))
        self.assertFalse(plugin.execute("invalid-email", "email"))

        # Test Numeric Validation
        self.assertTrue(plugin.execute("123", "numeric"))
        self.assertFalse(plugin.execute("abc", "numeric"))

        # Test Non-empty Validation
        self.assertTrue(plugin.execute("hello", "non_empty"))
        self.assertFalse(plugin.execute("", "non_empty"))

        self.assertTrue(plugin.shutdown())

    def test_validator_plugin_custom(self):
        """Test: ValidatorPlugin mit custom Validator"""
        plugin = ValidatorPlugin()
        plugin.initialize()

        # Custom Validator hinzufügen
        plugin.add_validator("min_length", lambda x: len(str(x)) >= 5)

        self.assertTrue(plugin.execute("hello", "min_length"))
        self.assertFalse(plugin.execute("hi", "min_length"))

    def test_transform_plugin(self):
        """Test: TransformPlugin"""
        plugin = TransformPlugin()
        self.assertEqual(plugin.get_name(), "TransformPlugin")
        self.assertTrue(plugin.initialize())

        # Test Uppercase
        self.assertEqual(plugin.execute("hello", "uppercase"), "HELLO")

        # Test Lowercase
        self.assertEqual(plugin.execute("HELLO", "lowercase"), "hello")

        # Test Strip
        self.assertEqual(plugin.execute("  hello  ", "strip"), "hello")

        # Test Reverse
        self.assertEqual(plugin.execute("hello", "reverse"), "olleh")

        self.assertTrue(plugin.shutdown())

    def test_transform_plugin_custom(self):
        """Test: TransformPlugin mit custom Transformation"""
        plugin = TransformPlugin()
        plugin.initialize()

        # Custom Transformation hinzufügen
        plugin.add_transformation("double", lambda x: str(x) + str(x))

        self.assertEqual(plugin.execute("hello", "double"), "hellohello")


class TestPluginSystemIntegration(unittest.TestCase):

    def test_full_workflow(self):
        """Test: Vollständiger Workflow"""
        # Registry und Loader erstellen
        registry = PluginRegistry()
        loader = PluginLoader(registry)

        # Plugin-Klasse registrieren
        registry.register_plugin_class(ValidatorPlugin)

        # Plugin instantiieren
        plugin = loader.instantiate_plugin("ValidatorPlugin")
        self.assertIsNotNone(plugin)

        # Plugin verwenden
        result = plugin.execute("test@example.com", "email")
        self.assertTrue(result)

        # Plugin deregistrieren
        registry.unregister_plugin("ValidatorPlugin")
        self.assertNotIn("ValidatorPlugin", registry.list_plugins())


if __name__ == '__main__':
    unittest.main()

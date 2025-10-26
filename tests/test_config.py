"""
Unit tests for configuration modules.
"""
import unittest
import sys
import os
from pathlib import Path
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestSettings(unittest.TestCase):
    """Test settings module."""

    def test_settings_constants(self):
        """Test that all required constants are defined."""
        from gui.config.settings import (
            APP_NAME, APP_CONTEXT, KEY_HEADER, KEY_FOOTER,
            EXPECTED_KEY_LEN, MIN_SPLASH_TIME, SPLASH_WIDTH, SPLASH_HEIGHT,
            MAIN_WINDOW_MIN_WIDTH, MAIN_WINDOW_MIN_HEIGHT
        )

        self.assertEqual(APP_NAME, "NalencGUI")
        self.assertEqual(APP_CONTEXT, "NalencGUI")
        self.assertEqual(EXPECTED_KEY_LEN, 512)
        self.assertIsInstance(MIN_SPLASH_TIME, (int, float))
        self.assertIsInstance(SPLASH_WIDTH, int)
        self.assertIsInstance(SPLASH_HEIGHT, int)
        self.assertIsInstance(MAIN_WINDOW_MIN_WIDTH, int)
        self.assertIsInstance(MAIN_WINDOW_MIN_HEIGHT, int)
        self.assertIn("BEGIN", KEY_HEADER)
        self.assertIn("END", KEY_FOOTER)


class TestPathManager(unittest.TestCase):
    """Test PathManager singleton."""

    def test_singleton(self):
        """Test that PathManager is a singleton."""
        from gui.config.paths import PathManager

        pm1 = PathManager()
        pm2 = PathManager()

        self.assertIs(pm1, pm2)

    def test_app_data_path(self):
        """Test app data path creation."""
        from gui.config.paths import PathManager

        pm = PathManager()
        app_data = pm.app_data_path

        self.assertIsInstance(app_data, Path)
        self.assertIn('NalencGUI', str(app_data))

    def test_get_resource_path(self):
        """Test resource path resolution."""
        from gui.config.paths import PathManager

        pm = PathManager()
        resource_path = pm.get_resource_path('assets/logo.ico')

        self.assertIsInstance(resource_path, Path)
        self.assertTrue(str(resource_path).endswith('logo.ico'))


class TestResourceManager(unittest.TestCase):
    """Test ResourceManager."""

    def setUp(self):
        """Set up test fixtures."""
        from gui.config.paths import PathManager
        from gui.utils.resource_manager import ResourceManager

        self.path_manager = PathManager()
        self.resource_manager = ResourceManager(self.path_manager)

    def test_init(self):
        """Test ResourceManager initialization."""
        self.assertIsNotNone(self.resource_manager)
        self.assertIsNotNone(self.resource_manager.path_manager)


class TestValidators(unittest.TestCase):
    """Test validators module."""

    def test_key_validator_exists(self):
        """Test that KeyValidator exists."""
        from gui.utils.validators import KeyValidator

        self.assertIsNotNone(KeyValidator)

    def test_validate_key_length(self):
        """Test key length validation."""
        from gui.utils.validators import KeyValidator

        valid_key = os.urandom(512)
        invalid_key = os.urandom(256)

        validator = KeyValidator()
        self.assertTrue(validator.validate_length(valid_key))
        self.assertFalse(validator.validate_length(invalid_key))


if __name__ == '__main__':
    unittest.main()


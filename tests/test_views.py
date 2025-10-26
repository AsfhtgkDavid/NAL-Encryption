"""
Unit tests for GUI views.
"""
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


@unittest.skipUnless(PYQT_AVAILABLE, "PyQt6 not available")
class TestMainTab(unittest.TestCase):
    """Test MainTab widget."""

    @classmethod
    def setUpClass(cls):
        """Create QApplication instance."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test fixtures."""
        from gui.views.main_tab import MainTab
        # Mock QMessageBox to prevent GUI popups during tests
        self.qmessagebox_patcher = patch('gui.views.main_tab.QMessageBox')
        self.mock_qmessagebox = self.qmessagebox_patcher.start()
        self.main_tab = MainTab()

    def tearDown(self):
        """Clean up."""
        self.qmessagebox_patcher.stop()

    def test_init(self):
        """Test MainTab initialization."""
        self.assertIsNotNone(self.main_tab)
        self.assertIsNotNone(self.main_tab.key_path)
        self.assertIsNotNone(self.main_tab.input_file_path)
        self.assertIsNotNone(self.main_tab.output_file_path)
        self.assertIsNotNone(self.main_tab.encrypt_button)
        self.assertIsNotNone(self.main_tab.decrypt_button)

    def test_buttons_enabled_by_default(self):
        """Test that encrypt/decrypt buttons are enabled by default."""
        self.assertTrue(self.main_tab.encrypt_button.isEnabled())
        self.assertTrue(self.main_tab.decrypt_button.isEnabled())

    def test_worker_thread_none_initially(self):
        """Test that worker thread is None initially."""
        self.assertIsNone(self.main_tab.worker_thread)

    def test_validate_inputs_no_key(self):
        """Test validation fails when no key is selected."""
        result = self.main_tab._validate_inputs('encrypt')
        self.assertIsNone(result)

    @patch('gui.views.main_tab.QFileDialog.getOpenFileName')
    def test_browse_key(self, mock_dialog):
        """Test browsing for key file."""
        mock_dialog.return_value = ('/path/to/key.key', '')

        with patch('os.path.getsize', return_value=512):
            self.main_tab._browse_key()
            self.assertEqual(self.main_tab.key_path.text(), '/path/to/key.key')


@unittest.skipUnless(PYQT_AVAILABLE, "PyQt6 not available")
class TestKeyManagementTab(unittest.TestCase):
    """Test KeyManagementTab widget."""

    @classmethod
    def setUpClass(cls):
        """Create QApplication instance."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test fixtures."""
        from gui.views.key_tab import KeyManagementTab
        # Mock QMessageBox to prevent GUI popups during tests
        self.qmessagebox_patcher = patch('gui.views.key_tab.QMessageBox')
        self.mock_qmessagebox = self.qmessagebox_patcher.start()
        self.key_tab = KeyManagementTab()

    def tearDown(self):
        """Clean up."""
        self.qmessagebox_patcher.stop()

    def test_init(self):
        """Test KeyManagementTab initialization."""
        self.assertIsNotNone(self.key_tab)
        self.assertIsNotNone(self.key_tab.generate_btn)
        self.assertIsNotNone(self.key_tab.save_btn)
        self.assertIsNotNone(self.key_tab.preview)

    def test_save_button_disabled_initially(self):
        """Test that save button is disabled initially."""
        self.assertFalse(self.key_tab.save_btn.isEnabled())

    def test_generate_key(self):
        """Test key generation."""
        self.key_tab._generate_key()
        self.assertIsNotNone(self.key_tab.current_key)
        self.assertEqual(len(self.key_tab.current_key), 512)
        self.assertTrue(self.key_tab.save_btn.isEnabled())
        self.assertTrue(len(self.key_tab.preview.toPlainText()) > 0)


@unittest.skipUnless(PYQT_AVAILABLE, "PyQt6 not available")
class TestSplashScreen(unittest.TestCase):
    """Test SplashScreen widget."""

    @classmethod
    def setUpClass(cls):
        """Create QApplication instance."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test fixtures."""
        from gui.views.splash import SplashScreen
        self.messages = ["Message 1", "Message 2", "Message 3"]
        self.splash = SplashScreen(self.messages)

    def test_init(self):
        """Test SplashScreen initialization."""
        self.assertIsNotNone(self.splash)
        self.assertIsNotNone(self.splash.message_label)
        self.assertIsNotNone(self.splash.animation_widget)
        self.assertEqual(self.splash.messages, self.messages)

    def test_fixed_size(self):
        """Test that splash screen has fixed size."""
        self.assertEqual(self.splash.width(), 430)
        self.assertEqual(self.splash.height(), 100)

    def tearDown(self):
        """Clean up."""
        self.splash.close()


if __name__ == '__main__':
    unittest.main()


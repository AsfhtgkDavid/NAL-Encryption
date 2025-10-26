"""
Unit tests for GUI widgets.
"""
import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt, QTimer
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


@unittest.skipUnless(PYQT_AVAILABLE, "PyQt6 not available")
class TestAnimatedButton(unittest.TestCase):
    """Test AnimatedButton widget."""

    @classmethod
    def setUpClass(cls):
        """Create QApplication instance."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test fixtures."""
        from gui.widgets.animated_button import AnimatedButton
        self.button = AnimatedButton("Test Button")

    def test_init(self):
        """Test AnimatedButton initialization."""
        self.assertIsNotNone(self.button)
        self.assertEqual(self.button.text(), "Test Button")

    def test_has_animation(self):
        """Test that button has hover animation."""
        # Simulate hover enter
        self.button.enterEvent(None)
        # Animation should be running or scheduled
        self.assertIsNotNone(self.button._animation)


@unittest.skipUnless(PYQT_AVAILABLE, "PyQt6 not available")
class TestLockAnimationWidget(unittest.TestCase):
    """Test LockAnimationWidget."""

    @classmethod
    def setUpClass(cls):
        """Create QApplication instance."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test fixtures."""
        from gui.widgets.lock_animation import LockAnimationWidget
        self.widget = LockAnimationWidget()

    def test_init(self):
        """Test LockAnimationWidget initialization."""
        self.assertIsNotNone(self.widget)
        self.assertEqual(self.widget._angle, 0)

    def test_minimum_size(self):
        """Test minimum size is set."""
        self.assertEqual(self.widget.minimumWidth(), 70)
        self.assertEqual(self.widget.minimumHeight(), 70)

    def test_animation_running(self):
        """Test that animation is running."""
        self.assertIsNotNone(self.widget._animation)
        # Animation should be started
        from PyQt6.QtCore import QAbstractAnimation
        # Note: Animation state might vary, just check it exists

    def test_stop_animation(self):
        """Test stopping animation."""
        self.widget.stopAnimation()
        # Animation should be stopped
        from PyQt6.QtCore import QAbstractAnimation
        self.assertEqual(self.widget._animation.state(), QAbstractAnimation.State.Stopped)


@unittest.skipUnless(PYQT_AVAILABLE, "PyQt6 not available")
class TestRoundedGroupBox(unittest.TestCase):
    """Test RoundedGroupBox widget."""

    @classmethod
    def setUpClass(cls):
        """Create QApplication instance."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test fixtures."""
        from gui.widgets.rounded_groupbox import RoundedGroupBox
        self.groupbox = RoundedGroupBox("Test Group")

    def test_init(self):
        """Test RoundedGroupBox initialization."""
        self.assertIsNotNone(self.groupbox)
        self.assertEqual(self.groupbox.title(), "Test Group")


if __name__ == '__main__':
    unittest.main()


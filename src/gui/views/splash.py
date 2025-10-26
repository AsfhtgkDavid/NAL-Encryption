"""
Splash screen displayed during application initialization.
"""

import random

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication

from gui.widgets.lock_animation import LockAnimationWidget


class SplashScreen(QWidget):
    """
    Splash screen widget with animated lock and random messages.
    """

    def __init__(self, messages):
        """
        Initialize splash screen.

        Args:
            messages: List of messages to display randomly
        """
        super().__init__()
        self.messages = messages
        self.setWindowFlags(
            Qt.WindowType.SplashScreen
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.setStyleSheet(
            f"""
            QWidget#SplashContainer {{
                background-color: rgba(43, 48, 59, 0.9);
                border-radius: 8px;
            }}
            QLabel#MessageLabel {{
                color: #E0E0E0;
                padding-left: 15px;
                padding-right: 15px;
            }}
        """
        )

        # Container widget
        container = QWidget(self)
        container.setObjectName("SplashContainer")
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(container)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Horizontal layout for animation and message
        h_layout = QHBoxLayout(container)
        h_layout.setContentsMargins(15, 15, 15, 15)
        h_layout.setSpacing(10)

        # Lock animation widget
        self.animation_widget = LockAnimationWidget()
        h_layout.addWidget(self.animation_widget)

        # Message label
        self.message_label = QLabel("Initializing...")
        self.message_label.setObjectName("MessageLabel")
        self.message_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.message_label.setWordWrap(True)
        font = QFont()
        font.setPointSize(11)
        self.message_label.setFont(font)
        h_layout.addWidget(self.message_label, 1)

        # Set size and position
        self.setFixedSize(430, 100)
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.move(screen_geometry.center() - self.rect().center())

        # Timer for message updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_message)
        self.timer.start(2000)

        self.update_message()

    def update_message(self):
        """Update the displayed message with a random message from the list."""
        if self.messages:
            msg = random.choice(self.messages)
            self.message_label.setText(msg)

    def closeEvent(self, event):
        """Clean up when closing."""
        self.timer.stop()
        if hasattr(self, "animation_widget"):
            self.animation_widget.stopAnimation()
        super().closeEvent(event)

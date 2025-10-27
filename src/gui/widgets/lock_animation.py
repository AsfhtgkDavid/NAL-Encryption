"""
Lock animation widget for splash screen and loading states.
"""

from PyQt6.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve,
    QPoint,
    QRectF,
    pyqtProperty,
)
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from PyQt6.QtWidgets import QWidget


class LockAnimationWidget(QWidget):
    """
    Animated lock widget with rotating arc for loading indication.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._angle = 0
        self.setMinimumSize(70, 70)

        self._animation = QPropertyAnimation(self, b"_angle_prop", self)
        self._animation.setStartValue(0)
        self._animation.setEndValue(360)
        self._animation.setDuration(2000)
        self._animation.setLoopCount(-1)
        self._animation.setEasingCurve(QEasingCurve.Type.Linear)
        self._animation.start()

    @pyqtProperty(int)
    def _angle_prop(self):
        return self._angle

    @_angle_prop.setter
    def _angle_prop(self, value):
        self._angle = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_x = self.width() / 2
        center_y = self.height() / 2
        radius = min(self.width(), self.height()) / 2 - 5

        bg_color = QColor(52, 61, 70, 204)
        lock_color = QColor(200, 200, 200)
        arc_color = QColor(100, 150, 255)

        # Background circle
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawEllipse(
            QPoint(int(center_x), int(center_y)), int(radius + 3), int(radius + 3)
        )

        # Lock body
        lock_width = radius * 0.8
        lock_height = radius * 0.7
        lock_x = center_x - lock_width / 2
        lock_y = center_y - lock_height / 3
        painter.setPen(QPen(lock_color, 2))
        painter.setBrush(QBrush(lock_color))
        painter.drawRoundedRect(QRectF(lock_x, lock_y, lock_width, lock_height), 5, 5)

        # Lock shackle
        shackle_radius = lock_width / 3
        shackle_center_y = lock_y
        shackle_rect = QRectF(
            center_x - shackle_radius,
            shackle_center_y - shackle_radius,
            shackle_radius * 2,
            shackle_radius * 2,
        )
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(lock_color, 3))
        painter.drawArc(shackle_rect, 0 * 16, 180 * 16)

        # Keyhole
        keyhole_radius = lock_width / 8
        painter.setBrush(QBrush(bg_color.darker(120)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(
            QPoint(int(center_x), int(lock_y + lock_height / 2)),
            int(keyhole_radius),
            int(keyhole_radius),
        )

        # Rotating arc
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(
            QPen(arc_color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        )
        arc_rect = QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2)
        painter.drawArc(arc_rect, self._angle * 16, 90 * 16)

    def stopAnimation(self):
        """Stop the rotation animation."""
        self._animation.stop()

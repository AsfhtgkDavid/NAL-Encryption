from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtWidgets import QPushButton


class AnimatedButton(QPushButton):
    """Button with hover animation"""

    def __init__(self, *args, animation_offset: int = -3, **kwargs):
        super().__init__(*args, **kwargs)
        self.animation_offset = animation_offset
        self._setup_animation()

    def _setup_animation(self):
        self._animation = QPropertyAnimation(self, b"pos")
        self._animation.setDuration(100)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._original_pos = None

    def enterEvent(self, event):
        if self._original_pos is None:
            self._original_pos = self.pos()
        self._animation.setEndValue(
            self._original_pos + QPoint(0, self.animation_offset)
        )
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._original_pos is not None:
            self._animation.setEndValue(self._original_pos)
            self._animation.start()
        super().leaveEvent(event)

    def moveEvent(self, event):
        if (
            not self._animation
            or self._animation.state() == QPropertyAnimation.State.Stopped
        ):
            self._original_pos = self.pos()
        super().moveEvent(event)


from PyQt6.QtWidgets import QPushButton


class AnimatedButton(QPushButton):
    """Button with hover animation"""

    def __init__(self, *args, animation_offset: int = -3, **kwargs):
        super().__init__(*args, **kwargs)
        self.animation_offset = animation_offset
        self._setup_animation()

    def _setup_animation(self):
        self._animation = QPropertyAnimation(self, b"pos")
        self._animation.setDuration(100)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._original_pos = None

    def enterEvent(self, event):
        if self._original_pos is None:
            self._original_pos = self.pos()
        self._animation.setEndValue(
            self._original_pos + QPoint(0, self.animation_offset)
        )
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._original_pos is not None:
            self._animation.setEndValue(self._original_pos)
            self._animation.start()
        super().leaveEvent(event)

    def moveEvent(self, event):
        if (
            not self._animation
            or self._animation.state() == QPropertyAnimation.State.Stopped
        ):
            self._original_pos = self.pos()
        super().moveEvent(event)

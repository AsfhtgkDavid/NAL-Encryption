from PyQt6.QtWidgets import QWidget


class FileSelector(QWidget):
    """Reusable file selection widget with label, path display, and browse button"""
from PyQt6.QtCore import pyqtSignal
    fileSelected = pyqtSignal(str)  # Emits selected file path

    def __init__(self, label_text: str, placeholder: str,
                 file_filter: str = "All Files (*.*)", parent=None):
        super().__init__(parent)
        self.file_filter = file_filter
        self._setup_ui(label_text, placeholder)

    def _setup_ui(self, label_text: str, placeholder: str):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(label_text)
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setPlaceholderText(placeholder)
        self.browse_btn = AnimatedButton("Browse...")

        layout.addWidget(self.label)
        layout.addWidget(self.path_edit)
        layout.addWidget(self.browse_btn)

        self.browse_btn.clicked.connect(self._browse)

    def _browse(self):
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", self.file_filter)
        if file_path:
            self.path_edit.setText(file_path)
            self.fileSelected.emit(file_path)

    def get_path(self) -> str:
        return self.path_edit.text()

    def set_path(self, path: str):
        self.path_edit.setText(path)
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit
from gui.widgets.animated_button import AnimatedButton

class FileSelector(QWidget):
    """Reusable file selection widget with label, path display, and browse button"""

    fileSelected = pyqtSignal(str)  # Emits selected file path

    def __init__(self, label_text: str, placeholder: str, 
                 file_filter: str = "All Files (*.*)", parent=None):
        super().__init__(parent)
        self.file_filter = file_filter
        self._setup_ui(label_text, placeholder)

    def _setup_ui(self, label_text: str, placeholder: str):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(label_text)
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setPlaceholderText(placeholder)
        self.browse_btn = AnimatedButton("Browse...")

        layout.addWidget(self.label)
        layout.addWidget(self.path_edit)
        layout.addWidget(self.browse_btn)

        self.browse_btn.clicked.connect(self._browse)

    def _browse(self):
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", self.file_filter)
        if file_path:
            self.path_edit.setText(file_path)
            self.fileSelected.emit(file_path)

    def get_path(self) -> str:
        return self.path_edit.text()

    def set_path(self, path: str):
        self.path_edit.setText(path)

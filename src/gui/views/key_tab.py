"""
Key management tab for generating and saving encryption keys.
"""

import base64
import os

from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QCheckBox,
    QFileDialog,
    QMessageBox,
)

from gui.config.settings import APP_CONTEXT, KEY_HEADER, KEY_FOOTER, EXPECTED_KEY_LEN
from gui.widgets.animated_button import AnimatedButton
from gui.widgets.rounded_groupbox import RoundedGroupBox


class KeyManagementTab(QWidget):
    """
    Tab widget for generating and saving encryption keys.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Key generation group
        self.gen_group = RoundedGroupBox()
        gen_layout = QVBoxLayout(self.gen_group)
        gen_layout.setSpacing(10)

        # Info label
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        gen_layout.addWidget(self.info_label)

        # Buttons
        btn_layout = QHBoxLayout()
        self.generate_btn = AnimatedButton()
        self.generate_btn.setObjectName("GenerateKeyButton")
        self.save_btn = AnimatedButton()
        self.save_btn.setEnabled(False)
        btn_layout.addWidget(self.generate_btn)
        btn_layout.addWidget(self.save_btn)
        gen_layout.addLayout(btn_layout)

        # ASCII checkbox
        self.ascii_checkbox = QCheckBox()
        gen_layout.addWidget(self.ascii_checkbox)

        # Key preview
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setFixedHeight(100)
        gen_layout.addWidget(self.preview)

        layout.addWidget(self.gen_group)
        layout.addStretch()

        # Connect signals
        self.generate_btn.clicked.connect(self._generate_key)
        self.save_btn.clicked.connect(self._save_key)

        self.current_key = None
        self.retranslateUi()

    def retranslateUi(self):
        """Update UI text for internationalization."""
        self.gen_group.setTitle(
            QCoreApplication.translate(APP_CONTEXT, "Generate New Key")
        )
        self.info_label.setText(
            QCoreApplication.translate(
                APP_CONTEXT,
                "Generate a new 512-byte encryption key and save it to a file.",
            )
        )
        self.generate_btn.setText(
            QCoreApplication.translate(APP_CONTEXT, "Generate New Key")
        )
        self.save_btn.setText(
            QCoreApplication.translate(APP_CONTEXT, "Save Key to File")
        )
        self.ascii_checkbox.setText(
            QCoreApplication.translate(APP_CONTEXT, "Save as ASCII (Base64 encoded)")
        )
        self.preview.setPlaceholderText(
            QCoreApplication.translate(
                APP_CONTEXT, "Generated key will appear here (in hex format)..."
            )
        )

    def _generate_key(self):
        """Generate a new random encryption key."""
        try:
            self.current_key = os.urandom(EXPECTED_KEY_LEN)
            self.preview.setText(self.current_key.hex())
            self.save_btn.setEnabled(True)
        except Exception as e:
            QMessageBox.warning(
                self,
                QCoreApplication.translate(APP_CONTEXT, "Error"),
                QCoreApplication.translate(APP_CONTEXT, f"Failed to generate key: {e}"),
            )

    def _save_key(self):
        """Save the generated key to a file."""
        if not self.current_key:
            return

        save_as_ascii = self.ascii_checkbox.isChecked()
        default_suffix = ".key"
        file_filter = QCoreApplication.translate(
            APP_CONTEXT, "Key Files (*.key);;All Files (*.*)"
        )

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            QCoreApplication.translate(APP_CONTEXT, "Save Encryption Key"),
            f"nalenc{default_suffix}",
            file_filter,
        )

        if file_path:
            if not file_path.lower().endswith(".key"):
                file_path += ".key"

            try:
                if save_as_ascii:
                    # Save as Base64 encoded ASCII
                    base64_data = base64.b64encode(self.current_key).decode("utf-8")
                    lines = [
                        base64_data[i : i + 64] for i in range(0, len(base64_data), 64)
                    ]
                    output_content = (
                        f"{KEY_HEADER}\n" + "\n".join(lines) + f"\n{KEY_FOOTER}\n"
                    )
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(output_content)
                else:
                    # Save as binary
                    with open(file_path, "wb") as f:
                        f.write(self.current_key)

                QMessageBox.information(
                    self,
                    QCoreApplication.translate(APP_CONTEXT, "Success"),
                    QCoreApplication.translate(
                        APP_CONTEXT, f"Key saved to:\n{file_path}"
                    ),
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    QCoreApplication.translate(APP_CONTEXT, "Error"),
                    QCoreApplication.translate(APP_CONTEXT, f"Failed to save key: {e}"),
                )

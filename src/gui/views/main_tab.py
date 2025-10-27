"""
Main tab for encryption and decryption operations.
"""

import base64
import os
from pathlib import Path

from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QFileDialog,
    QMessageBox,
    QProgressBar,
)

from gui.config.settings import APP_CONTEXT, KEY_HEADER, KEY_FOOTER, EXPECTED_KEY_LEN
from gui.widgets.animated_button import AnimatedButton
from gui.widgets.rounded_groupbox import RoundedGroupBox
from gui.workers.encryption_worker import EncryptionWorker


class MainTab(QWidget):
    """
    Main encryption/decryption tab widget.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.worker_thread = None

        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Key file group
        self.key_group = RoundedGroupBox()
        key_layout = QHBoxLayout(self.key_group)
        self.key_label = QLabel()
        self.key_path = QLineEdit()
        self.key_path.setReadOnly(True)
        self.browse_key_btn = AnimatedButton()
        key_layout.addWidget(self.key_label)
        key_layout.addWidget(self.key_path)
        key_layout.addWidget(self.browse_key_btn)
        layout.addWidget(self.key_group)

        # Input file group
        self.input_group = RoundedGroupBox()
        input_layout = QHBoxLayout(self.input_group)
        self.input_label = QLabel()
        self.input_file_path = QLineEdit()
        self.input_file_path.setReadOnly(True)
        self.browse_input_button = AnimatedButton()
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_file_path)
        input_layout.addWidget(self.browse_input_button)
        layout.addWidget(self.input_group)

        # Output file group
        self.output_group = RoundedGroupBox()
        output_layout = QHBoxLayout(self.output_group)
        self.output_label = QLabel()
        self.output_file_path = QLineEdit()
        self.output_file_path.setReadOnly(True)
        self.browse_output_button = AnimatedButton()
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_file_path)
        output_layout.addWidget(self.browse_output_button)
        layout.addWidget(self.output_group)

        # Action buttons
        action_layout = QHBoxLayout()
        self.encrypt_button = AnimatedButton()
        self.decrypt_button = AnimatedButton()
        action_layout.addStretch()
        action_layout.addWidget(self.encrypt_button)
        action_layout.addWidget(self.decrypt_button)
        action_layout.addStretch()
        layout.addLayout(action_layout)

        # Connect signals
        self.browse_key_btn.clicked.connect(self._browse_key)
        self.browse_input_button.clicked.connect(self._browse_input_file)
        self.browse_output_button.clicked.connect(self._browse_output_file)
        self.encrypt_button.clicked.connect(self._encrypt_action)
        self.decrypt_button.clicked.connect(self._decrypt_action)

        self.retranslateUi()

    def retranslateUi(self):
        """Update UI text for internationalization."""
        self.key_group.setTitle(
            QCoreApplication.translate(APP_CONTEXT, "Encryption Key")
        )
        self.key_label.setText(QCoreApplication.translate(APP_CONTEXT, "Key File:"))
        self.key_path.setPlaceholderText(
            QCoreApplication.translate(APP_CONTEXT, "Select key file (512 bytes)...")
        )
        self.browse_key_btn.setText(
            QCoreApplication.translate(APP_CONTEXT, "Browse...")
        )

        self.input_group.setTitle(QCoreApplication.translate(APP_CONTEXT, "Input File"))
        self.input_label.setText(QCoreApplication.translate(APP_CONTEXT, "File:"))
        self.input_file_path.setPlaceholderText(
            QCoreApplication.translate(APP_CONTEXT, "Select input file...")
        )
        self.browse_input_button.setText(
            QCoreApplication.translate(APP_CONTEXT, "Browse...")
        )

        self.output_group.setTitle(
            QCoreApplication.translate(APP_CONTEXT, "Output File")
        )
        self.output_label.setText(QCoreApplication.translate(APP_CONTEXT, "File:"))
        self.output_file_path.setPlaceholderText(
            QCoreApplication.translate(APP_CONTEXT, "Select output file location...")
        )
        self.browse_output_button.setText(
            QCoreApplication.translate(APP_CONTEXT, "Browse...")
        )

        self.encrypt_button.setText(QCoreApplication.translate(APP_CONTEXT, "Encrypt"))
        self.decrypt_button.setText(QCoreApplication.translate(APP_CONTEXT, "Decrypt"))

    def _encrypt_action(self):
        """Handle encrypt button click."""
        if self.worker_thread and self.worker_thread.isRunning():
            QMessageBox.warning(
                self,
                QCoreApplication.translate(APP_CONTEXT, "Busy"),
                QCoreApplication.translate(
                    APP_CONTEXT, "An operation is already in progress."
                ),
            )
            return
        self._start_worker("encrypt")

    def _decrypt_action(self):
        """Handle decrypt button click."""
        if self.worker_thread and self.worker_thread.isRunning():
            QMessageBox.warning(
                self,
                QCoreApplication.translate(APP_CONTEXT, "Busy"),
                QCoreApplication.translate(
                    APP_CONTEXT, "An operation is already in progress."
                ),
            )
            return
        self._start_worker("decrypt")

    def _browse_key(self):
        """Browse for encryption key file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            QCoreApplication.translate(APP_CONTEXT, "Select Encryption Key"),
            "",
            QCoreApplication.translate(
                APP_CONTEXT, "Key Files (*.key);;All Files (*.*)"
            ),
        )
        if file_path:
            try:
                if os.path.getsize(file_path) == 512:
                    self.key_path.setText(file_path)
                else:
                    # Try to parse as ASCII key file
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content_text = f.read()
                        lines = content_text.strip().splitlines()
                        if lines[0] == KEY_HEADER and lines[-1] == KEY_FOOTER:
                            base64_content = "".join(lines[1:-1])
                            key_bytes = base64.b64decode(base64_content)
                            if len(key_bytes) == EXPECTED_KEY_LEN:
                                self.key_path.setText(file_path)
                                return
                            else:
                                QMessageBox.warning(
                                    self,
                                    QCoreApplication.translate(
                                        APP_CONTEXT, "Invalid Key"
                                    ),
                                    QCoreApplication.translate(
                                        APP_CONTEXT,
                                        f"Key file (ASCII) has incorrect length after decoding: "
                                        f"{len(key_bytes)} bytes. Expected {EXPECTED_KEY_LEN}.",
                                    ),
                                )
                        else:
                            QMessageBox.warning(
                                self,
                                QCoreApplication.translate(APP_CONTEXT, "Invalid Key"),
                                QCoreApplication.translate(
                                    APP_CONTEXT,
                                    "Key file is not 512 bytes and does not appear to be a valid ASCII key file.",
                                ),
                            )
                    except Exception:
                        QMessageBox.warning(
                            self,
                            QCoreApplication.translate(APP_CONTEXT, "Invalid Key"),
                            QCoreApplication.translate(
                                APP_CONTEXT,
                                "Key file is not 512 bytes and could not be read as an ASCII key file.",
                            ),
                        )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    QCoreApplication.translate(APP_CONTEXT, "Error"),
                    QCoreApplication.translate(
                        APP_CONTEXT, f"Could not read key file properties: {e}"
                    ),
                )

    def _browse_input_file(self):
        """Browse for input file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, QCoreApplication.translate(APP_CONTEXT, "Select Input File")
        )
        if file_path:
            self.input_file_path.setText(file_path)

    def _browse_output_file(self):
        """Browse for output file location."""
        suggested_name = "output.nalenc"
        default_dir = ""
        input_file = self.input_file_path.text()

        if input_file and os.path.exists(input_file):
            input_path = Path(input_file)
            default_dir = str(input_path.parent)
            base_name = input_path.stem
            ext = input_path.suffix

            if ext.lower() == ".nalenc":
                suggested_name = f"{base_name}_decrypted{ext}"
            else:
                suggested_name = f"{base_name}.nalenc"

        default_filter = QCoreApplication.translate(
            APP_CONTEXT, "Encrypted Files (*.nalenc);;All Files (*.*)"
        )
        if (
            suggested_name.lower().endswith(".nalenc")
            and "_decrypted" not in suggested_name.lower()
        ):
            pass
        else:
            default_filter = QCoreApplication.translate(APP_CONTEXT, "All Files (*.*)")

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            QCoreApplication.translate(APP_CONTEXT, "Save Output File"),
            os.path.join(default_dir, suggested_name),
            default_filter,
        )
        if file_path:
            self.output_file_path.setText(file_path)

    def _get_key_bytes(self) -> bytes | None:
        """
        Load and validate the key file.

        Returns:
            Key bytes if valid, None otherwise
        """
        key_path = self.key_path.text()
        if not key_path:
            QMessageBox.warning(
                self,
                QCoreApplication.translate(APP_CONTEXT, "Error"),
                QCoreApplication.translate(APP_CONTEXT, "Please select a key file."),
            )
            return None

        try:
            with open(key_path, "rb") as f:
                key_data_bytes = f.read()

            # Check if it's a binary key
            if len(key_data_bytes) == EXPECTED_KEY_LEN:
                return key_data_bytes

            # Try to parse as ASCII key
            try:
                key_data_text = key_data_bytes.decode("utf-8", errors="strict")
                lines = key_data_text.strip().splitlines()
                if lines[0] == KEY_HEADER and lines[-1] == KEY_FOOTER:
                    base64_content = "".join(lines[1:-1])
                    decoded_key = base64.b64decode(base64_content)
                    if len(decoded_key) == EXPECTED_KEY_LEN:
                        return decoded_key
                    else:
                        QMessageBox.warning(
                            self,
                            QCoreApplication.translate(APP_CONTEXT, "Error"),
                            QCoreApplication.translate(
                                APP_CONTEXT,
                                f"Invalid key length in ASCII file: {len(decoded_key)} bytes. "
                                f"Expected {EXPECTED_KEY_LEN}.",
                            ),
                        )
                        return None
                else:
                    QMessageBox.warning(
                        self,
                        QCoreApplication.translate(APP_CONTEXT, "Error"),
                        QCoreApplication.translate(
                            APP_CONTEXT,
                            f"Invalid key file format. Expected 512 bytes binary or valid ASCII format.",
                        ),
                    )
                    return None

            except (UnicodeDecodeError, IndexError, base64.binascii.Error):
                QMessageBox.warning(
                    self,
                    QCoreApplication.translate(APP_CONTEXT, "Error"),
                    QCoreApplication.translate(
                        APP_CONTEXT,
                        f"Invalid key file format. Expected 512 bytes binary or valid ASCII format.",
                    ),
                )
                return None

        except FileNotFoundError:
            QMessageBox.warning(
                self,
                QCoreApplication.translate(APP_CONTEXT, "Error"),
                QCoreApplication.translate(
                    APP_CONTEXT, f"Key file not found: {key_path}"
                ),
            )
            return None
        except Exception as e:
            QMessageBox.warning(
                self,
                QCoreApplication.translate(APP_CONTEXT, "Error"),
                QCoreApplication.translate(
                    APP_CONTEXT, f"Failed to read key file: {e}"
                ),
            )
            return None

    def _start_worker(self, mode):
        """Start the encryption/decryption worker thread."""
        inputs = self._validate_inputs(mode)
        if inputs is None:
            return

        key_bytes, input_path, output_path = inputs

        # Disable buttons
        self.encrypt_button.setEnabled(False)
        self.decrypt_button.setEnabled(False)

        # Update status bar
        status_bar = self.window().statusBar()
        progress_bar = status_bar.findChild(QProgressBar)
        status_bar.showMessage(f"{mode.capitalize()}ing...")
        if progress_bar:
            progress_bar.setVisible(True)
            progress_bar.setRange(0, 0)

        # Create and start worker
        self.worker_thread = EncryptionWorker(mode, key_bytes, input_path, output_path)
        self.worker_thread.finished.connect(self._on_worker_finished)
        self.worker_thread.error.connect(self._on_worker_error)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.error.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

    def _validate_inputs(self, mode):
        """Validate all inputs before starting operation."""
        key_bytes = self._get_key_bytes()
        if key_bytes is None:
            return None

        input_path = self.input_file_path.text()
        if not input_path:
            QMessageBox.warning(
                self,
                QCoreApplication.translate(APP_CONTEXT, "Error"),
                "Input file path cannot be empty.",
            )
            return None
        if not os.path.exists(input_path):
            QMessageBox.warning(
                self,
                QCoreApplication.translate(APP_CONTEXT, "Error"),
                f"Input file not found: {input_path}",
            )
            return None

        output_path = self.output_file_path.text()
        if not output_path:
            QMessageBox.warning(
                self,
                QCoreApplication.translate(APP_CONTEXT, "Error"),
                "Output file path cannot be empty.",
            )
            self._browse_output_file()
            output_path = self.output_file_path.text()
            if not output_path:
                return None

        return key_bytes, input_path, output_path

    def _on_worker_finished(self, result):
        """Handle worker finished signal."""
        status_bar = self.window().statusBar()
        progress_bar = status_bar.findChild(QProgressBar)
        if progress_bar:
            progress_bar.setVisible(False)
        status_bar.showMessage("Operation completed.", 5000)

        QMessageBox.information(
            self, QCoreApplication.translate(APP_CONTEXT, "Success"), str(result)
        )
        self._reset_ui_after_worker()

    def _on_worker_error(self, error_message):
        """Handle worker error signal."""
        status_bar = self.window().statusBar()
        progress_bar = status_bar.findChild(QProgressBar)
        if progress_bar:
            progress_bar.setVisible(False)
        status_bar.showMessage("Operation failed.", 5000)
        QMessageBox.warning(
            self, QCoreApplication.translate(APP_CONTEXT, "Error"), error_message
        )
        self._reset_ui_after_worker()

    def _reset_ui_after_worker(self):
        """Reset UI state after worker completes."""
        self.worker_thread = None
        self.encrypt_button.setEnabled(True)
        self.decrypt_button.setEnabled(True)

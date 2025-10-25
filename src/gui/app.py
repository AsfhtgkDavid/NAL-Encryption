import base64
import os
import random
import shutil
import sys
import time
from pathlib import Path

from PyQt6.QtCore import (Qt, QThread, pyqtSignal, QPropertyAnimation,
                          QEasingCurve, QPoint, QRectF, QTranslator,
                          QCoreApplication, QEvent,
                          QTimer, pyqtProperty, QEventLoop)
from PyQt6.QtGui import QIcon, QPainter, QColor, QFont, QPen, QBrush
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QGroupBox, QTextEdit,
    QMessageBox, QStatusBar, QProgressBar, QTabWidget,
    QCheckBox, QComboBox, QToolBar
)


def get_app_data_path():
    return Path(os.getenv('APPDATA', Path.home() / 'AppData' / 'Roaming')) / 'NalencGUI'

def resource_path(relative_path):
    app_data_path = get_app_data_path()
    local_resource_path = app_data_path / relative_path

    if getattr(sys, 'frozen', False):
        if local_resource_path.exists():
            return local_resource_path
        else:
            try:
                base_path = Path(sys._MEIPASS)
                bundled_path = base_path / 'nalenc_gui' / relative_path
                return bundled_path
            except Exception as e:
                print(f"Error resolving bundled path for {relative_path}: {e}")
                return Path(sys.executable).parent / 'nalenc_gui' / relative_path
    else:
        base_path = Path(__file__).parent
        return base_path / relative_path

def ensure_resources_extracted():
    if not getattr(sys, 'frozen', False):
        return

    app_data_path = get_app_data_path()
    marker_file = app_data_path / ".extracted_v1"

    if marker_file.exists():
        print(f"Resources already extracted to: {app_data_path}")
        return

    print(f"First run or resources missing/outdated. Extracting to: {app_data_path}")

    try:
        bundle_dir = Path(sys._MEIPASS) / 'nalenc_gui'

        resources_to_extract = [
            Path("style.qss"),
            Path("assets/logo.ico"),
            Path("assets/loading.gif")
        ]
        folders_to_extract = [
            Path("translations")
        ]

        app_data_path.mkdir(parents=True, exist_ok=True)

        for res_rel_path in resources_to_extract:
            src_path = bundle_dir / res_rel_path
            dest_path = app_data_path / res_rel_path
            if src_path.exists():
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                print(f"Extracting {src_path.name} to {dest_path.parent}")
                shutil.copy2(src_path, dest_path)
            else:
                print(f"Warning: Bundled resource not found: {src_path}")

        for folder_rel_path in folders_to_extract:
            src_folder = bundle_dir / folder_rel_path
            dest_folder = app_data_path / folder_rel_path
            if src_folder.is_dir():
                print(f"Extracting folder {src_folder.name} to {dest_folder.parent}")
                if dest_folder.exists():
                    shutil.rmtree(dest_folder)
                shutil.copytree(src_folder, dest_folder)
            else:
                print(f"Warning: Bundled folder not found: {src_folder}")

        marker_file.touch()
        print("Resource extraction complete.")

    except AttributeError:
        print("Error: sys._MEIPASS not found. Cannot extract resources.")
        QMessageBox.critical(None, "Extraction Error", "Failed to find bundled resources (sys._MEIPASS not found).")
        sys.exit(1)
    except Exception as e:
        print(f"Error during resource extraction: {e}")
        QMessageBox.critical(None, "Extraction Error", f"Failed to extract application resources to {app_data_path}.\nError: {e}\nPlease check permissions.")
        sys.exit(1)

try:
    from numba import jit
    @jit(nopython=True)
    def compile_numba_stuff(x):
        return x * x + x - 1
except ImportError:
    print("Numba not found. Skipping Numba compilation step.")
    jit = lambda *args, **kwargs: lambda f: f
    @jit(nopython=True)
    def compile_numba_stuff(x):
        return x * x + x - 1

try:
    from nalenc import NALEnc
except ImportError:
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from nalenc import NALEnc
    except ImportError:
        QMessageBox.critical(None, "Import Error", "Could not find the 'nalenc' library. Make sure it's installed or the path is correct.")
        sys.exit(1)

KEY_HEADER = "----BEGIN NAL KEY----"
KEY_FOOTER = "----END NAL KEY----"
EXPECTED_KEY_LEN = 512

APP_CONTEXT = "NalencGUI"


class WorkerThread(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, mode, password_bytes, input_path, output_path):
        super().__init__()
        self.mode = mode
        self.password_bytes = password_bytes
        self.input_path = input_path
        self.output_path = output_path

    def run(self):
        try:
            try:
                nal_encryptor = NALEnc(self.password_bytes)
            except ValueError as e:
                self.error.emit(f"Password Error (length must be 512 bytes): {e}")
                return
            except TypeError as e:
                self.error.emit(f"Password Type Error: {e}")
                return

            try:
                with open(self.input_path, 'rb') as f:
                    data_bytes = f.read()
                if not data_bytes:
                    self.error.emit("Input file is empty.")
                    return
            except Exception as e:
                self.error.emit(f"Error reading input file: {e}")
                return

            if self.mode == 'encrypt':
                result_data = nal_encryptor.encrypt(data_bytes)
                result_bytes = bytes(result_data)
            elif self.mode == 'decrypt':
                result_data = nal_encryptor.decrypt(data_bytes)
                result_bytes = bytes(result_data)
            else:
                self.error.emit("Invalid operation mode.")
                return

            try:
                with open(self.output_path, 'wb') as f:
                    f.write(result_bytes)
                self.finished.emit(f"Operation successful.\nOutput saved to: {self.output_path}")
            except Exception as e:
                self.error.emit(f"Error writing output file: {e}")

        except Exception as e:
            self.error.emit(f"An unexpected error occurred: {e}")


class AnimatedButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._animation = QPropertyAnimation(self, b"pos")
        self._animation.setDuration(100)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._original_pos = None

    def enterEvent(self, event):
        if self._original_pos is None:
            self._original_pos = self.pos()
        self._animation.setEndValue(self._original_pos + QPoint(0, -3))
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._original_pos is not None:
            self._animation.setEndValue(self._original_pos)
            self._animation.start()
        super().leaveEvent(event)

    def moveEvent(self, event):
        if not self._animation or self._animation.state() == QPropertyAnimation.State.Stopped:
            self._original_pos = self.pos()
        super().moveEvent(event)


class RoundedGroupBox(QGroupBox):
    pass


class KeyManagementTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.gen_group = RoundedGroupBox()
        gen_layout = QVBoxLayout(self.gen_group)
        gen_layout.setSpacing(10)

        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        gen_layout.addWidget(self.info_label)

        btn_layout = QHBoxLayout()
        self.generate_btn = AnimatedButton()
        self.generate_btn.setObjectName("GenerateKeyButton")
        self.save_btn = AnimatedButton()
        self.save_btn.setEnabled(False)
        btn_layout.addWidget(self.generate_btn)
        btn_layout.addWidget(self.save_btn)
        gen_layout.addLayout(btn_layout)

        self.ascii_checkbox = QCheckBox()
        gen_layout.addWidget(self.ascii_checkbox)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setFixedHeight(100)
        gen_layout.addWidget(self.preview)

        layout.addWidget(self.gen_group)
        layout.addStretch()

        self.generate_btn.clicked.connect(self._generate_key)
        self.save_btn.clicked.connect(self._save_key)

        self.current_key = None
        self.retranslateUi()

    def retranslateUi(self):
        self.gen_group.setTitle(QCoreApplication.translate(APP_CONTEXT, "Generate New Key"))
        self.info_label.setText(QCoreApplication.translate(APP_CONTEXT, "Generate a new 512-byte encryption key and save it to a file."))
        self.generate_btn.setText(QCoreApplication.translate(APP_CONTEXT, "Generate New Key"))
        self.save_btn.setText(QCoreApplication.translate(APP_CONTEXT, "Save Key to File"))
        self.ascii_checkbox.setText(QCoreApplication.translate(APP_CONTEXT, "Save as ASCII (Base64 encoded)"))
        self.preview.setPlaceholderText(QCoreApplication.translate(APP_CONTEXT, "Generated key will appear here (in hex format)..."))

    def _generate_key(self):
        try:
            self.current_key = os.urandom(EXPECTED_KEY_LEN)
            self.preview.setText(self.current_key.hex())
            self.save_btn.setEnabled(True)
        except Exception as e:
            QMessageBox.warning(self, QCoreApplication.translate(APP_CONTEXT, "Error"), QCoreApplication.translate(APP_CONTEXT, f"Failed to generate key: {e}"))

    def _save_key(self):
        if not self.current_key:
            return

        save_as_ascii = self.ascii_checkbox.isChecked()
        default_suffix = ".key"
        file_filter = QCoreApplication.translate(APP_CONTEXT, "Key Files (*.key);;All Files (*.*)")

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            QCoreApplication.translate(APP_CONTEXT, "Save Encryption Key"),
            f"nalenc{default_suffix}",
            file_filter
        )

        if file_path:
            if not file_path.lower().endswith('.key'):
                file_path += '.key'

            try:
                if save_as_ascii:
                    base64_data = base64.b64encode(self.current_key).decode('utf-8')
                    lines = [base64_data[i:i+64] for i in range(0, len(base64_data), 64)]
                    output_content = f"{KEY_HEADER}\n" + "\n".join(lines) + f"\n{KEY_FOOTER}\n"
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(output_content)
                else:
                    with open(file_path, 'wb') as f:
                        f.write(self.current_key)

                QMessageBox.information(self, QCoreApplication.translate(APP_CONTEXT, "Success"),
                                        QCoreApplication.translate(APP_CONTEXT, f"Key saved to:\n{file_path}"))
            except Exception as e:
                QMessageBox.warning(self, QCoreApplication.translate(APP_CONTEXT, "Error"),
                                    QCoreApplication.translate(APP_CONTEXT, f"Failed to save key: {e}"))


class MainTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.worker_thread = None
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

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

        action_layout = QHBoxLayout()
        self.encrypt_button = AnimatedButton()
        self.decrypt_button = AnimatedButton()
        action_layout.addStretch()
        action_layout.addWidget(self.encrypt_button)
        action_layout.addWidget(self.decrypt_button)
        action_layout.addStretch()
        layout.addLayout(action_layout)

        self.browse_key_btn.clicked.connect(self._browse_key)
        self.browse_input_button.clicked.connect(self._browse_input_file)
        self.browse_output_button.clicked.connect(self._browse_output_file)
        self.encrypt_button.clicked.connect(self._encrypt_action)
        self.decrypt_button.clicked.connect(self._decrypt_action)

        self.retranslateUi()

    def retranslateUi(self):
        self.key_group.setTitle(QCoreApplication.translate(APP_CONTEXT, "Encryption Key"))
        self.key_label.setText(QCoreApplication.translate(APP_CONTEXT, "Key File:"))
        self.key_path.setPlaceholderText(QCoreApplication.translate(APP_CONTEXT, "Select key file (512 bytes)..."))
        self.browse_key_btn.setText(QCoreApplication.translate(APP_CONTEXT, "Browse..."))

        self.input_group.setTitle(QCoreApplication.translate(APP_CONTEXT, "Input File"))
        self.input_label.setText(QCoreApplication.translate(APP_CONTEXT, "File:"))
        self.input_file_path.setPlaceholderText(QCoreApplication.translate(APP_CONTEXT, "Select input file..."))
        self.browse_input_button.setText(QCoreApplication.translate(APP_CONTEXT, "Browse..."))

        self.output_group.setTitle(QCoreApplication.translate(APP_CONTEXT, "Output File"))
        self.output_label.setText(QCoreApplication.translate(APP_CONTEXT, "File:"))
        self.output_file_path.setPlaceholderText(QCoreApplication.translate(APP_CONTEXT, "Select output file location..."))
        self.browse_output_button.setText(QCoreApplication.translate(APP_CONTEXT, "Browse..."))

        self.encrypt_button.setText(QCoreApplication.translate(APP_CONTEXT, "Encrypt"))
        self.decrypt_button.setText(QCoreApplication.translate(APP_CONTEXT, "Decrypt"))

    def _encrypt_action(self):
        if self.worker_thread and self.worker_thread.isRunning():
            QMessageBox.warning(self, QCoreApplication.translate(APP_CONTEXT, "Busy"),
                                QCoreApplication.translate(APP_CONTEXT, "An operation is already in progress."))
            return
        self._start_worker('encrypt')

    def _decrypt_action(self):
        if self.worker_thread and self.worker_thread.isRunning():
            QMessageBox.warning(self, QCoreApplication.translate(APP_CONTEXT, "Busy"),
                                QCoreApplication.translate(APP_CONTEXT, "An operation is already in progress."))
            return
        self._start_worker('decrypt')

    def _browse_key(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            QCoreApplication.translate(APP_CONTEXT, "Select Encryption Key"),
            "",
            QCoreApplication.translate(APP_CONTEXT, "Key Files (*.key);;All Files (*.*)")
        )
        if file_path:
            try:
                if os.path.getsize(file_path) == 512:
                    self.key_path.setText(file_path)
                else:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content_text = f.read()
                        lines = content_text.strip().splitlines()
                        if lines[0] == KEY_HEADER and lines[-1] == KEY_FOOTER:
                            base64_content = "".join(lines[1:-1])
                            key_bytes = base64.b64decode(base64_content)
                            if len(key_bytes) == EXPECTED_KEY_LEN:
                                self.key_path.setText(file_path)
                                return
                            else:
                                QMessageBox.warning(self, QCoreApplication.translate(APP_CONTEXT, "Invalid Key"),
                                                    QCoreApplication.translate(APP_CONTEXT, f"Key file (ASCII) has incorrect length after decoding: {len(key_bytes)} bytes. Expected {EXPECTED_KEY_LEN}."))
                        else:
                            QMessageBox.warning(self, QCoreApplication.translate(APP_CONTEXT, "Invalid Key"),
                                                QCoreApplication.translate(APP_CONTEXT, "Key file is not 512 bytes and does not appear to be a valid ASCII key file."))
                    except Exception:
                        QMessageBox.warning(self, QCoreApplication.translate(APP_CONTEXT, "Invalid Key"),
                                            QCoreApplication.translate(APP_CONTEXT, "Key file is not 512 bytes and could not be read as an ASCII key file."))
            except Exception as e:
                QMessageBox.warning(self, QCoreApplication.translate(APP_CONTEXT, "Error"),
                                    QCoreApplication.translate(APP_CONTEXT, f"Could not read key file properties: {e}"))

    def _browse_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, QCoreApplication.translate(APP_CONTEXT, "Select Input File"))
        if file_path:
            self.input_file_path.setText(file_path)

    def _browse_output_file(self):
        suggested_name = "output.nalenc"
        default_dir = ""
        input_file = self.input_file_path.text()

        if input_file and os.path.exists(input_file):
            input_path = Path(input_file)
            default_dir = str(input_path.parent)
            base_name = input_path.stem
            ext = input_path.suffix

            if ext.lower() == '.nalenc':
                suggested_name = f"{base_name}_decrypted{ext}"
            else:
                suggested_name = f"{base_name}.nalenc"

        default_filter = QCoreApplication.translate(APP_CONTEXT, "Encrypted Files (*.nalenc);;All Files (*.*)")
        if suggested_name.lower().endswith('.nalenc') and '_decrypted' not in suggested_name.lower():
            pass
        else:
            default_filter = QCoreApplication.translate(APP_CONTEXT, "All Files (*.*)")

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            QCoreApplication.translate(APP_CONTEXT, "Save Output File"),
            os.path.join(default_dir, suggested_name),
            default_filter
        )
        if file_path:
            self.output_file_path.setText(file_path)

    def _get_key_bytes(self) -> bytes | None:
        key_path = self.key_path.text()
        if not key_path:
            QMessageBox.warning(self, QCoreApplication.translate(APP_CONTEXT, "Error"),
                                QCoreApplication.translate(APP_CONTEXT, "Please select a key file."))
            return None

        try:
            with open(key_path, 'rb') as f:
                key_data_bytes = f.read()

            if len(key_data_bytes) == EXPECTED_KEY_LEN:
                return key_data_bytes

            try:
                key_data_text = key_data_bytes.decode('utf-8', errors='strict')
                lines = key_data_text.strip().splitlines()
                if lines[0] == KEY_HEADER and lines[-1] == KEY_FOOTER:
                    base64_content = "".join(lines[1:-1])
                    decoded_key = base64.b64decode(base64_content)
                    if len(decoded_key) == EXPECTED_KEY_LEN:
                        return decoded_key
                    else:
                        QMessageBox.warning(self, QCoreApplication.translate(APP_CONTEXT, "Error"),
                            QCoreApplication.translate(APP_CONTEXT, f"Invalid key length in ASCII file: {len(decoded_key)} bytes. Expected {EXPECTED_KEY_LEN}."))
                        return None
                else:
                    QMessageBox.warning(self, QCoreApplication.translate(APP_CONTEXT, "Error"),
                        QCoreApplication.translate(APP_CONTEXT, f"Invalid key file format. Expected 512 bytes binary or valid ASCII format."))
                    return None

            except (UnicodeDecodeError, IndexError, base64.binascii.Error):
                QMessageBox.warning(self, QCoreApplication.translate(APP_CONTEXT, "Error"),
                    QCoreApplication.translate(APP_CONTEXT, f"Invalid key file format. Expected 512 bytes binary or valid ASCII format."))
                return None

        except FileNotFoundError:
            QMessageBox.warning(self, QCoreApplication.translate(APP_CONTEXT, "Error"),
                                QCoreApplication.translate(APP_CONTEXT, f"Key file not found: {key_path}"))
            return None
        except Exception as e:
            QMessageBox.warning(self, QCoreApplication.translate(APP_CONTEXT, "Error"),
                                QCoreApplication.translate(APP_CONTEXT, f"Failed to read key file: {e}"))
            return None

    def _start_worker(self, mode):
        inputs = self._validate_inputs(mode)
        if inputs is None:
            return

        key_bytes, input_path, output_path = inputs

        self.encrypt_button.setEnabled(False)
        self.decrypt_button.setEnabled(False)
        status_bar = self.window().statusBar()
        progress_bar = status_bar.findChild(QProgressBar)
        status_bar.showMessage(f"{mode.capitalize()}ing...")
        if progress_bar:
            progress_bar.setVisible(True)
            progress_bar.setRange(0, 0)

        self.worker_thread = WorkerThread(mode, key_bytes, input_path, output_path)
        self.worker_thread.finished.connect(self._on_worker_finished)
        self.worker_thread.error.connect(self._on_worker_error)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.error.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

    def _validate_inputs(self, mode):
        key_bytes = self._get_key_bytes()
        if key_bytes is None:
            return None

        input_path = self.input_file_path.text()
        if not input_path:
            QMessageBox.warning(self, QCoreApplication.translate(APP_CONTEXT, "Error"), "Input file path cannot be empty.")
            return None
        if not os.path.exists(input_path):
            QMessageBox.warning(self, QCoreApplication.translate(APP_CONTEXT, "Error"), f"Input file not found: {input_path}")
            return None

        output_path = self.output_file_path.text()
        if not output_path:
            QMessageBox.warning(self, QCoreApplication.translate(APP_CONTEXT, "Error"), "Output file path cannot be empty.")
            self._browse_output_file()
            output_path = self.output_file_path.text()
            if not output_path:
                return None

        return key_bytes, input_path, output_path

    def _on_worker_finished(self, result):
        status_bar = self.window().statusBar()
        progress_bar = status_bar.findChild(QProgressBar)
        if progress_bar:
            progress_bar.setVisible(False)
        status_bar.showMessage("Operation completed.", 5000)

        QMessageBox.information(self, QCoreApplication.translate(APP_CONTEXT, "Success"), str(result))
        self._reset_ui_after_worker()

    def _on_worker_error(self, error_message):
        status_bar = self.window().statusBar()
        progress_bar = status_bar.findChild(QProgressBar)
        if progress_bar:
            progress_bar.setVisible(False)
        status_bar.showMessage("Operation failed.", 5000)
        QMessageBox.warning(self, QCoreApplication.translate(APP_CONTEXT, "Error"), error_message)
        self._reset_ui_after_worker()

    def _reset_ui_after_worker(self):
        self.worker_thread = None
        self.encrypt_button.setEnabled(True)
        self.decrypt_button.setEnabled(True)


class LockAnimationWidget(QWidget):
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

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawEllipse(QPoint(int(center_x), int(center_y)), int(radius + 3), int(radius + 3))

        lock_width = radius * 0.8
        lock_height = radius * 0.7
        lock_x = center_x - lock_width / 2
        lock_y = center_y - lock_height / 3
        painter.setPen(QPen(lock_color, 2))
        painter.setBrush(QBrush(lock_color))
        painter.drawRoundedRect(QRectF(lock_x, lock_y, lock_width, lock_height), 5, 5)

        shackle_radius = lock_width / 3
        shackle_center_y = lock_y
        shackle_rect = QRectF(center_x - shackle_radius, shackle_center_y - shackle_radius,
                              shackle_radius * 2, shackle_radius * 2)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(lock_color, 3))
        painter.drawArc(shackle_rect, 0 * 16, 180 * 16)

        keyhole_radius = lock_width / 8
        painter.setBrush(QBrush(bg_color.darker(120)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPoint(int(center_x), int(lock_y + lock_height / 2)), int(keyhole_radius), int(keyhole_radius))

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(arc_color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        arc_rect = QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2)
        painter.drawArc(arc_rect, self._angle * 16, 90 * 16)

    def stopAnimation(self):
        self._animation.stop()


class SplashScreen(QWidget):
    def __init__(self, messages):
        super().__init__()
        self.messages = messages
        self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.setStyleSheet(f"""
            QWidget#SplashContainer {{
                background-color: rgba(43, 48, 59, 0.9);
                border-radius: 8px;
            }}
            QLabel#MessageLabel {{
                color: #E0E0E0;
                padding-left: 15px;
                padding-right: 15px;
            }}
        """)

        container = QWidget(self)
        container.setObjectName("SplashContainer")
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(container)
        main_layout.setContentsMargins(0, 0, 0, 0)

        h_layout = QHBoxLayout(container)
        h_layout.setContentsMargins(15, 15, 15, 15)
        h_layout.setSpacing(10)

        self.animation_widget = LockAnimationWidget()
        h_layout.addWidget(self.animation_widget)

        self.message_label = QLabel("Initializing...")
        self.message_label.setObjectName("MessageLabel")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.message_label.setWordWrap(True)
        font = QFont()
        font.setPointSize(11)
        self.message_label.setFont(font)
        h_layout.addWidget(self.message_label, 1)

        self.setFixedSize(430, 100)

        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.move(screen_geometry.center() - self.rect().center())

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_message)
        self.timer.start(2000)

        self.update_message()

    def update_message(self):
        if self.messages:
            msg = random.choice(self.messages)
            self.message_label.setText(msg)

    def closeEvent(self, event):
        self.timer.stop()
        if hasattr(self, 'animation_widget'):
            self.animation_widget.stopAnimation()
        super().closeEvent(event)


class NalencGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        icon_path = resource_path("assets/logo.ico")
        print(f"Loading window icon from: {icon_path}")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        else:
            print(f"Window icon not found at: {icon_path}")

        self.translator = QTranslator()
        self.translations_path = resource_path("translations")
        print(f"Using translations path: {self.translations_path}")

        self.setWindowTitle(QCoreApplication.translate(APP_CONTEXT, "NALEnc Encryption Tool"))
        self.setGeometry(100, 100, 750, 650)
        self.setMinimumSize(600, 500)

        toolbar = QToolBar(QCoreApplication.translate(APP_CONTEXT, "Language"))
        toolbar.setMovable(False) 
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Українська", "uk")
        self.language_combo.currentTextChanged.connect(self._change_language)
        toolbar.addWidget(QLabel(QCoreApplication.translate(APP_CONTEXT, "Language:")))
        toolbar.addWidget(self.language_combo)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.main_tab = MainTab(self)
        self.key_tab = KeyManagementTab(self)

        self.tab_encrypt_decrypt_index = self.tabs.addTab(self.main_tab, "")
        self.tab_key_management_index = self.tabs.addTab(self.key_tab, "")

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("StatusBarProgressBar")
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)

        self._change_language(self.language_combo.currentText())

        style_path = resource_path("style.qss")
        print(f"Looking for stylesheet at: {style_path}")
        if style_path.exists():
            try:
                with open(style_path, "r", encoding="utf-8") as f:
                    style_content = f.read()
                    self.setStyleSheet(style_content)
            except Exception as e:
                error_message = f"Error loading stylesheet '{style_path.name}':\n{e}"
                QMessageBox.warning(self, QCoreApplication.translate(APP_CONTEXT, "Stylesheet Error"), error_message)
        else:
            warning_message = f"Stylesheet not found at: {style_path.resolve()}"
            QMessageBox.warning(self, QCoreApplication.translate(APP_CONTEXT, "Stylesheet Warning"), warning_message)

        self.retranslateUi()

    def _change_language(self, lang_text):
        locale_code = self.language_combo.currentData()

        QCoreApplication.removeTranslator(self.translator)

        qm_file = self.translations_path / f"app_{locale_code}.qm"
        print(f"Attempting to load translation: {qm_file}")
        if self.translator.load(str(qm_file)):
            QCoreApplication.installTranslator(self.translator)
            print(f"Successfully loaded {locale_code}")
        else:
            print(f"Failed to load translation for {locale_code} from {qm_file}")

    def changeEvent(self, event):
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

    def retranslateUi(self):
        self.setWindowTitle(QCoreApplication.translate(APP_CONTEXT, "NALEnc Encryption Tool"))
        self.tabs.setTabText(self.tab_encrypt_decrypt_index, QCoreApplication.translate(APP_CONTEXT, "Encrypt / Decrypt"))
        self.tabs.setTabText(self.tab_key_management_index, QCoreApplication.translate(APP_CONTEXT, "Key Management"))
        self.main_tab.retranslateUi()
        self.key_tab.retranslateUi()


def main():
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    app = QApplication(sys.argv)

    ensure_resources_extracted()

    loading_messages = [
        QCoreApplication.translate(APP_CONTEXT, "Initializing..."),
        QCoreApplication.translate(APP_CONTEXT, "Loading modules..."),
        QCoreApplication.translate(APP_CONTEXT, "Warming up encryption cores..."),
        QCoreApplication.translate(APP_CONTEXT, "Checking for quantum interference..."),
        QCoreApplication.translate(APP_CONTEXT, "Compiling Numba functions... (This might take a moment)"),
        QCoreApplication.translate(APP_CONTEXT, "Reticulating splines..."),
        QCoreApplication.translate(APP_CONTEXT, "Launching PC into space..."),
        QCoreApplication.translate(APP_CONTEXT, "Encrypting program code..."),
        QCoreApplication.translate(APP_CONTEXT, "Almost there..."),
    ]
    splash = SplashScreen(loading_messages)
    splash.show()
    app.processEvents()

    overall_start_time = time.time()
    min_display_time = 3.0
    numba_warmup_duration = 0.0

    try:
        print("Warming up Numba encryption/decryption functions...")
        splash.message_label.setText(QCoreApplication.translate(APP_CONTEXT, "Compiling Numba functions... (This might take a moment)"))
        app.processEvents()

        warmup_start_time = time.time()
        dummy_key = os.urandom(EXPECTED_KEY_LEN)
        dummy_message = b'warmup_message_for_numba'
        try:
            nal_warmup = NALEnc(dummy_key)
            encrypted_dummy = nal_warmup.encrypt(dummy_message)
            _ = nal_warmup.decrypt(encrypted_dummy)

            numba_warmup_duration = time.time() - warmup_start_time
            print(f"Numba warm-up finished in {numba_warmup_duration:.2f} seconds.")
        except Exception as warmup_e:
            print(f"Numba warm-up failed: {warmup_e}")

    except Exception as e:
        print(f"Error during initial setup or Numba warm-up: {e}")

    elapsed_time = time.time() - overall_start_time
    remaining_time = min_display_time - elapsed_time
    if remaining_time > 0:
        print(f"Waiting {remaining_time:.2f} more seconds for minimum splash time...")
        timer = QTimer()
        timer.setSingleShot(True)
        loop = QEventLoop()
        timer.timeout.connect(loop.quit)
        timer.start(int(remaining_time * 1000))
        loop.exec()

    print("Proceeding to main window...")
    window = NalencGUI()
    window.show()

    splash.close()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

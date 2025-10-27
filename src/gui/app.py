import os
import sys
import time
from pathlib import Path

try:
    from PyQt6.QtCore import (
        Qt,
        QThread,
        pyqtSignal,
        QPropertyAnimation,
        QEasingCurve,
        QPoint,
        QRectF,
        QTranslator,
        QCoreApplication,
        QEvent,
        QTimer,
        pyqtProperty,
        QEventLoop,
    )
    from PyQt6.QtGui import QIcon, QPainter, QColor, QFont, QPen, QBrush
    from PyQt6.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QFileDialog,
        QGroupBox,
        QTextEdit,
        QMessageBox,
        QStatusBar,
        QProgressBar,
        QTabWidget,
        QCheckBox,
        QComboBox,
        QToolBar,
    )
except ImportError:
    print(
        "GUI are available only with gui extra. Please install nalenc with 'pip install nalenc[gui]'"
    )
    exit(1)

# Use refactored config, utils, views and workers
from .config.settings import (
    APP_CONTEXT,
    EXPECTED_KEY_LEN,
    MIN_SPLASH_TIME,
)
from .config.paths import PathManager
from .utils.resource_manager import ResourceManager
from .views.splash import SplashScreen
from .views.main_tab import MainTab
from .views.key_tab import KeyManagementTab

path_manager = PathManager()
resource_manager = ResourceManager(path_manager)


def get_app_data_path():
    return path_manager.app_data_path


def resource_path(relative_path):
    """Resolve resource path using PathManager"""
    return path_manager.get_resource_path(relative_path)


def ensure_resources_extracted():
    return resource_manager.ensure_extracted()


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
        QMessageBox.critical(
            None,
            "Import Error",
            "Could not find the 'nalenc' library. Make sure it's installed or the path is correct.",
        )
        sys.exit(1)


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

        self.setWindowTitle(
            QCoreApplication.translate(APP_CONTEXT, "NALEnc Encryption Tool")
        )
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

        style_path = resource_path("styles/default.qss")
        print(f"Looking for stylesheet at: {style_path}")
        if style_path.exists():
            try:
                with open(style_path, "r", encoding="utf-8") as f:
                    style_content = f.read()
                    self.setStyleSheet(style_content)
            except Exception as e:
                error_message = f"Error loading stylesheet '{style_path.name}':\n{e}"
                QMessageBox.warning(
                    self,
                    QCoreApplication.translate(APP_CONTEXT, "Stylesheet Error"),
                    error_message,
                )
        else:
            warning_message = f"Stylesheet not found at: {style_path.resolve()}"
            QMessageBox.warning(
                self,
                QCoreApplication.translate(APP_CONTEXT, "Stylesheet Warning"),
                warning_message,
            )

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
        self.setWindowTitle(
            QCoreApplication.translate(APP_CONTEXT, "NALEnc Encryption Tool")
        )
        self.tabs.setTabText(
            self.tab_encrypt_decrypt_index,
            QCoreApplication.translate(APP_CONTEXT, "Encrypt / Decrypt"),
        )
        self.tabs.setTabText(
            self.tab_key_management_index,
            QCoreApplication.translate(APP_CONTEXT, "Key Management"),
        )
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
        QCoreApplication.translate(
            APP_CONTEXT, "Compiling Numba functions... (This might take a moment)"
        ),
        QCoreApplication.translate(APP_CONTEXT, "Reticulating splines..."),
        QCoreApplication.translate(APP_CONTEXT, "Launching PC into space..."),
        QCoreApplication.translate(APP_CONTEXT, "Encrypting program code..."),
        QCoreApplication.translate(APP_CONTEXT, "Almost there..."),
    ]
    splash = SplashScreen(loading_messages)
    splash.show()
    app.processEvents()

    overall_start_time = time.time()
    min_display_time = MIN_SPLASH_TIME
    numba_warmup_duration = 0.0

    try:
        print("Warming up Numba encryption/decryption functions...")
        splash.message_label.setText(
            QCoreApplication.translate(
                APP_CONTEXT, "Compiling Numba functions... (This might take a moment)"
            )
        )
        app.processEvents()

        warmup_start_time = time.time()
        dummy_key = os.urandom(EXPECTED_KEY_LEN)
        dummy_message = b"warmup_message_for_numba"
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

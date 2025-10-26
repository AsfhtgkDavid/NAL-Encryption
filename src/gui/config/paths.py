# config/paths.py
from pathlib import Path
from typing import Optional


class PathManager:
    """Centralized path resolution for resources"""

    _instance: Optional["PathManager"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._app_data_path = self._get_app_data_path()
        self._is_frozen = getattr(sys, "frozen", False)
        self._initialized = True

    @staticmethod
    def _get_app_data_path() -> Path:
        """Cross-platform app data directory"""
        if sys.platform == "win32":
            base = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming"))
        elif sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support"
        else:  # Linux and other Unix-like
            base = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
        return base / "NalencGUI"

    # config/paths.py
    def get_resource_path(self, relative_path: str) -> Path:
        """Resolve resource path for bundled or development mode"""
        local_path = self._app_data_path / relative_path

        if self._is_frozen:
            if local_path.exists():
                return local_path
            try:
                bundle_path = Path(sys._MEIPASS) / "nalenc_gui" / relative_path
                return bundle_path
            except AttributeError:
                return Path(sys.executable).parent / "nalenc_gui" / relative_path
        else:
            return Path(__file__).parents[1] / relative_path

    @property
    def app_data_path(self) -> Path:
        return self._app_data_path


import os
import sys
from pathlib import Path
from typing import Optional


class PathManager:
    """Centralized path resolution for resources"""

    _instance: Optional["PathManager"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._app_data_path = self._get_app_data_path()
        self._is_frozen = getattr(sys, "frozen", False)
        self._initialized = True

    @staticmethod
    def _get_app_data_path() -> Path:
        """Cross-platform app data directory"""
        if sys.platform == "win32":
            base = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming"))
        elif sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support"
        else:  # Linux and other Unix-like
            base = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
        return base / "NalencGUI"

    def get_resource_path(self, relative_path: str) -> Path:
        """Resolve resource path for bundled or development mode"""
        local_path = self._app_data_path / relative_path

        if self._is_frozen:
            if local_path.exists():
                return local_path
            try:
                bundle_path = Path(sys._MEIPASS) / "nalenc_gui" / relative_path
                return bundle_path
            except AttributeError:
                return Path(sys.executable).parent / "nalenc_gui" / relative_path
        else:
            return Path(__file__).parents[1] / relative_path

    @property
    def app_data_path(self) -> Path:
        return self._app_data_path

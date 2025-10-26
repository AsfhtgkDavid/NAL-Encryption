# utils/resource_manager.py
from gui.config.paths import PathManager


class ResourceManager:
    """Handles resource extraction for frozen applications"""

    # utils/resource_manager.py
    def __init__(self, path_manager: PathManager):
        self.path_manager = path_manager
        self.marker_file = path_manager.app_data_path / ".extracted_v1"

    def ensure_extracted(self) -> bool:
        """Extract bundled resources if needed"""
        if not getattr(sys, "frozen", False):
            return True

        if self.marker_file.exists():
            return True

        try:
            self._extract_resources()
            self.marker_file.touch()
            return True
        except Exception as e:
            QMessageBox.critical(
                None, "Extraction Error", f"Failed to extract resources: {e}"
            )
            return False

    def _extract_resources(self):
        """Internal extraction logic"""
        bundle_dir = Path(sys._MEIPASS) / "nalenc_gui"

        resources_to_extract = [
            Path("style.qss"),
            Path("assets/logo.ico"),
            Path("assets/loading.gif"),
        ]
        folders_to_extract = [Path("translations")]

        app_data_path = self.path_manager.app_data_path
        app_data_path.mkdir(parents=True, exist_ok=True)

        for res_rel_path in resources_to_extract:
            src_path = bundle_dir / res_rel_path
            dest_path = app_data_path / res_rel_path
            if src_path.exists():
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dest_path)
            else:
                print(f"Warning: Bundled resource not found: {src_path}")

        for folder_rel_path in folders_to_extract:
            src_folder = bundle_dir / folder_rel_path
            dest_folder = app_data_path / folder_rel_path
            if src_folder.is_dir():
                if dest_folder.exists():
                    shutil.rmtree(dest_folder)
                shutil.copytree(src_folder, dest_folder)
            else:
                print(f"Warning: Bundled folder not found: {src_folder}")


import shutil
import sys
from pathlib import Path
from PyQt6.QtWidgets import QMessageBox
from gui.config.paths import PathManager


class ResourceManager:
    """Handles resource extraction for frozen applications"""

    def __init__(self, path_manager: PathManager):
        self.path_manager = path_manager
        self.marker_file = path_manager.app_data_path / ".extracted_v1"

    def ensure_extracted(self) -> bool:
        """Extract bundled resources if needed"""
        if not getattr(sys, "frozen", False):
            return True

        if self.marker_file.exists():
            return True

        try:
            self._extract_resources()
            self.marker_file.touch()
            return True
        except Exception as e:
            QMessageBox.critical(
                None, "Extraction Error", f"Failed to extract resources: {e}"
            )
            return False

    def _extract_resources(self):
        """Internal extraction logic"""
        bundle_dir = Path(sys._MEIPASS) / "nalenc_gui"

        resources_to_extract = [
            Path("style.qss"),
            Path("assets/logo.ico"),
            Path("assets/loading.gif"),
        ]
        folders_to_extract = [Path("translations")]

        app_data_path = self.path_manager.app_data_path
        app_data_path.mkdir(parents=True, exist_ok=True)

        for res_rel_path in resources_to_extract:
            src_path = bundle_dir / res_rel_path
            dest_path = app_data_path / res_rel_path
            if src_path.exists():
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dest_path)
            else:
                print(f"Warning: Bundled resource not found: {src_path}")

        for folder_rel_path in folders_to_extract:
            src_folder = bundle_dir / folder_rel_path
            dest_folder = app_data_path / folder_rel_path
            if src_folder.is_dir():
                if dest_folder.exists():
                    shutil.rmtree(dest_folder)
                shutil.copytree(src_folder, dest_folder)
            else:
                print(f"Warning: Bundled folder not found: {src_folder}")

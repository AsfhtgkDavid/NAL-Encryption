"""
Background worker thread for encryption/decryption operations.
"""

import sys
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

try:
    from nalenc import NALEnc
except ImportError:
    # Fallback for development mode
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from nalenc import NALEnc


class EncryptionWorker(QThread):
    """
    Worker thread for performing encryption/decryption operations in the background.

    Signals:
        finished: Emitted when operation completes successfully with result message
        error: Emitted when an error occurs with error message
        progress: Emitted to report progress (0-100)
    """

    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, mode, password_bytes, input_path, output_path):
        """
        Initialize the worker thread.

        Args:
            mode: 'encrypt' or 'decrypt'
            password_bytes: The encryption key as bytes
            input_path: Path to input file
            output_path: Path to output file
        """
        super().__init__()
        self.mode = mode
        self.password_bytes = password_bytes
        self.input_path = input_path
        self.output_path = output_path

    def run(self):
        """Execute the encryption/decryption operation."""
        try:
            # Initialize NALEnc with the password
            try:
                nal_encryptor = NALEnc(self.password_bytes)
            except ValueError as e:
                self.error.emit(f"Password Error (length must be 512 bytes): {e}")
                return
            except TypeError as e:
                self.error.emit(f"Password Type Error: {e}")
                return

            # Read input file
            try:
                with open(self.input_path, "rb") as f:
                    data_bytes = f.read()
                if not data_bytes:
                    self.error.emit("Input file is empty.")
                    return
            except Exception as e:
                self.error.emit(f"Error reading input file: {e}")
                return

            # Perform operation
            if self.mode == "encrypt":
                result_data = nal_encryptor.encrypt(data_bytes)
                result_bytes = bytes(result_data)
            elif self.mode == "decrypt":
                result_data = nal_encryptor.decrypt(data_bytes)
                result_bytes = bytes(result_data)
            else:
                self.error.emit("Invalid operation mode.")
                return

            # Write output file
            try:
                with open(self.output_path, "wb") as f:
                    f.write(result_bytes)
                self.finished.emit(
                    f"Operation successful.\nOutput saved to: {self.output_path}"
                )
            except Exception as e:
                self.error.emit(f"Error writing output file: {e}")

        except Exception as e:
            self.error.emit(f"An unexpected error occurred: {e}")

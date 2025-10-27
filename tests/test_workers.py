"""
Unit tests for encryption worker.
"""
import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QEventLoop, QTimer
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


@unittest.skipUnless(PYQT_AVAILABLE, "PyQt6 not available")
class TestEncryptionWorker(unittest.TestCase):
    """Test EncryptionWorker thread."""

    @classmethod
    def setUpClass(cls):
        """Create QApplication instance."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test fixtures."""
        from gui.workers.encryption_worker import EncryptionWorker
        self.WorkerClass = EncryptionWorker
        self.test_key = os.urandom(512)

    def test_init_encrypt(self):
        """Test worker initialization for encryption."""
        worker = self.WorkerClass('encrypt', self.test_key, '/input', '/output')
        self.assertEqual(worker.mode, 'encrypt')
        self.assertEqual(worker.password_bytes, self.test_key)
        self.assertEqual(worker.input_path, '/input')
        self.assertEqual(worker.output_path, '/output')

    def test_init_decrypt(self):
        """Test worker initialization for decryption."""
        worker = self.WorkerClass('decrypt', self.test_key, '/input', '/output')
        self.assertEqual(worker.mode, 'decrypt')

    def test_worker_signals_exist(self):
        """Test that worker has required signals."""
        worker = self.WorkerClass('encrypt', self.test_key, '/input', '/output')
        self.assertTrue(hasattr(worker, 'finished'))
        self.assertTrue(hasattr(worker, 'error'))
        self.assertTrue(hasattr(worker, 'progress'))

    def test_invalid_key_length(self):
        """Test worker with invalid key length."""
        worker = self.WorkerClass('encrypt', b'short_key', '/input', '/output')

        error_emitted = []
        worker.error.connect(lambda msg: error_emitted.append(msg))

        worker.run()

        self.assertTrue(len(error_emitted) > 0)
        self.assertIn('512 bytes', error_emitted[0])

    def test_nonexistent_input_file(self):
        """Test worker with nonexistent input file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            worker = self.WorkerClass(
                'encrypt',
                self.test_key,
                '/nonexistent/file.txt',
                str(Path(tmpdir) / 'output.nalenc')
            )

            error_emitted = []
            worker.error.connect(lambda msg: error_emitted.append(msg))

            worker.run()

            self.assertTrue(len(error_emitted) > 0)
            self.assertIn('reading input file', error_emitted[0])

    def test_encrypt_decrypt_roundtrip(self):
        """Test full encrypt/decrypt roundtrip."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create test input file
            input_file = tmpdir / 'input.txt'
            input_data = b'Test data for encryption'
            input_file.write_bytes(input_data)

            encrypted_file = tmpdir / 'encrypted.nalenc'
            decrypted_file = tmpdir / 'decrypted.txt'

            # Encrypt
            encrypt_worker = self.WorkerClass(
                'encrypt',
                self.test_key,
                str(input_file),
                str(encrypted_file)
            )

            finished_messages = []
            error_messages = []
            encrypt_worker.finished.connect(lambda msg: finished_messages.append(msg))
            encrypt_worker.error.connect(lambda msg: error_messages.append(msg))

            encrypt_worker.run()

            self.assertEqual(len(error_messages), 0, f"Encryption errors: {error_messages}")
            self.assertEqual(len(finished_messages), 1)
            self.assertTrue(encrypted_file.exists())

            # Decrypt
            decrypt_worker = self.WorkerClass(
                'decrypt',
                self.test_key,
                str(encrypted_file),
                str(decrypted_file)
            )

            finished_messages.clear()
            error_messages.clear()
            decrypt_worker.finished.connect(lambda msg: finished_messages.append(msg))
            decrypt_worker.error.connect(lambda msg: error_messages.append(msg))

            decrypt_worker.run()

            self.assertEqual(len(error_messages), 0, f"Decryption errors: {error_messages}")
            self.assertEqual(len(finished_messages), 1)
            self.assertTrue(decrypted_file.exists())

            # Verify data
            decrypted_data = decrypted_file.read_bytes()
            self.assertEqual(decrypted_data, input_data)


if __name__ == '__main__':
    unittest.main()


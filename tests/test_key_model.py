import os
import base64
import tempfile
from pathlib import Path
import unittest

from gui.models.key import EncryptionKey
from gui.utils.validators import KeyValidator
from gui.config.settings import EXPECTED_KEY_LEN, KEY_HEADER, KEY_FOOTER


class TestEncryptionKey(unittest.TestCase):
    def test_generate_and_save_load_binary(self):
        key = EncryptionKey.generate()
        self.assertIsInstance(key.data, bytes)
        self.assertEqual(len(key.data), EXPECTED_KEY_LEN)

        with tempfile.TemporaryDirectory() as td:
            file_path = Path(td) / "testkey.key"
            key.save(file_path, ascii_format=False)

            self.assertTrue(file_path.exists())
            self.assertEqual(file_path.stat().st_size, EXPECTED_KEY_LEN)

            loaded = EncryptionKey.from_file(file_path)
            self.assertEqual(loaded.data, key.data)

    def test_save_and_load_ascii(self):
        key = EncryptionKey.generate()
        with tempfile.TemporaryDirectory() as td:
            file_path = Path(td) / "testkey_ascii.key"
            key.save(file_path, ascii_format=True)

            self.assertTrue(file_path.exists())
            text = file_path.read_text(encoding='utf-8')
            self.assertTrue(text.startswith(KEY_HEADER))
            self.assertTrue(text.strip().endswith(KEY_FOOTER))

            loaded = EncryptionKey.from_file(file_path)
            self.assertEqual(loaded.data, key.data)


class TestKeyValidator(unittest.TestCase):
    def test_validate_binary_and_ascii(self):
        key = EncryptionKey.generate()
        with tempfile.TemporaryDirectory() as td:
            bin_path = Path(td) / "bin.key"
            ascii_path = Path(td) / "asc.key"

            key.save(bin_path, ascii_format=False)
            key.save(ascii_path, ascii_format=True)

            ok, data, err = KeyValidator.validate_key_file(bin_path)
            self.assertTrue(ok)
            self.assertEqual(data, key.data)
            self.assertEqual(err, "")

            ok2, data2, err2 = KeyValidator.validate_key_file(ascii_path)
            self.assertTrue(ok2)
            self.assertEqual(data2, key.data)
            self.assertEqual(err2, "")

    def test_invalid_files(self):
        with tempfile.TemporaryDirectory() as td:
            missing = Path(td) / "no.key"
            ok, data, err = KeyValidator.validate_key_file(missing)
            self.assertFalse(ok)
            self.assertIsNone(data)
            self.assertIn("not found", err)

            bad = Path(td) / "bad.key"
            bad.write_bytes(b"short")
            ok2, data2, err2 = KeyValidator.validate_key_file(bad)
            self.assertFalse(ok2)
            self.assertIsNone(data2)
            self.assertTrue(len(err2) > 0)


if __name__ == '__main__':
    unittest.main()

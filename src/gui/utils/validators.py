# utils/validators.py
import base64
from pathlib import Path
from typing import Optional, Tuple

from gui.config.settings import KEY_HEADER, KEY_FOOTER, EXPECTED_KEY_LEN


class KeyValidator:
    """Validates encryption key files"""

    @staticmethod
    def validate_length(key_bytes: bytes) -> bool:
        """
        Validate that key has correct length.

        Args:
            key_bytes: Key bytes to validate

        Returns:
            True if key length is valid, False otherwise
        """
        return len(key_bytes) == EXPECTED_KEY_LEN

    @staticmethod
    def validate_key_file(path: Path) -> Tuple[bool, Optional[bytes], str]:
        """
        Validate key file and return key bytes

        Returns:
            (is_valid, key_bytes, error_message)
        """
        if not path.exists():
            return False, None, f"Key file not found: {path}"

        try:
            with open(path, "rb") as f:
                data = f.read()

            # Try binary format first
            if len(data) == EXPECTED_KEY_LEN:
                return True, data, ""

            # Try ASCII format
            try:
                text = data.decode("utf-8")
                lines = text.strip().splitlines()

                if lines[0] == KEY_HEADER and lines[-1] == KEY_FOOTER:
                    base64_content = "".join(lines[1:-1])
                    key_bytes = base64.b64decode(base64_content)

                    if len(key_bytes) == EXPECTED_KEY_LEN:
                        return True, key_bytes, ""
                    else:
                        return False, None, f"Invalid key length: {len(key_bytes)}"
                else:
                    return False, None, "Invalid key file format"
            except (UnicodeDecodeError, base64.binascii.Error):
                return False, None, "Invalid key file format"

        except Exception as e:
            return False, None, f"Error reading key file: {e}"

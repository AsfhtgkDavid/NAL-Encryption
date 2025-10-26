import base64
import os
from dataclasses import dataclass
from pathlib import Path

from gui.config.settings import KEY_HEADER, KEY_FOOTER, EXPECTED_KEY_LEN


@dataclass
class EncryptionKey:
    """Represents an encryption key"""

    data: bytes

    def __post_init__(self):
        if len(self.data) != EXPECTED_KEY_LEN:
            raise ValueError(f"Key must be {EXPECTED_KEY_LEN} bytes")

    @classmethod
    def generate(cls) -> "EncryptionKey":
        """Generate new random key"""
        return cls(os.urandom(EXPECTED_KEY_LEN))

    @classmethod
    def from_file(cls, path: Path) -> "EncryptionKey":
        """Load key from file (binary or ASCII)"""
        from gui.utils.validators import KeyValidator

        is_valid, key_bytes, error = KeyValidator.validate_key_file(path)
        if not is_valid:
            raise ValueError(error)
        return cls(key_bytes)

    def save(self, path: Path, ascii_format: bool = False):
        """Save key to file"""
        if ascii_format:
            base64_data = base64.b64encode(self.data).decode("utf-8")
            lines = [base64_data[i : i + 64] for i in range(0, len(base64_data), 64)]
            content = f"{KEY_HEADER}\n" + "\n".join(lines) + f"\n{KEY_FOOTER}\n"
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            with open(path, "wb") as f:
                f.write(self.data)

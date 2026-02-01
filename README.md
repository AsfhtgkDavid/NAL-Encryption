# NALEnc - Python Encryption Library

**⚠️ Educational purpose only. DO NOT use for production security.**

**NALEnc** is a lightweight Python encryption library designed for securely encrypting and decrypting text and binary data. With an intuitive interface and robust functionality, it is ideal for developers seeking a straightforward yet effective encryption solution.

---

## 🚀 Features

- **Flexible Input:** Encrypt and decrypt strings, binary data, or NumPy arrays.
- **Password Support:** Accepts passwords as strings, bytes, lists of integers (0-255), or NumPy arrays.
- **Optimized for Performance:** Best suited for messages of size `2046n`, where `n ∈ N`.
- **Powered by NumPy:** Leverages NumPy for efficient operations.
- **Command-Line Interface:** Includes a `nalenc` CLI tool for easy file encryption/decryption and key generation directly from your terminal.

---

## 📦 Installation

Install the library via pip:

```bash
pip install nalenc
```

---

## 📝 Usage

### 🔗 Importing the Library

```python
import nalenc
import numpy as np
```

### 🔑 Creating an Instance of NALEnc

To use the library, create an instance of the `NALEnc` class with a password. The password can be:

- A string
- A byte sequence
- An iterable of integers (each in the range `0-255`)
- A NumPy array of integers (dtype must be `np.uint8`)

Example:

```python
# Generate a password as a NumPy array
password = np.random.randint(0, 256, size=512, dtype=np.uint8)
nal = nalenc.NALEnc(password)
```

### 🔒 Encrypting Data

Use the `encrypt` method to encrypt a message. Supported input types:

- **String**
- **Byte sequence**
- **Iterable of integers** (0-255)
- **NumPy array** (dtype: `np.uint8`)

Example:

```python
# Encrypt a string
encrypted = nal.encrypt("Hello, World!")

# Encrypt binary data
binary_data = b"\x89PNG\r\n\x1a\n"
encrypted_binary = nal.encrypt(binary_data)

# Encrypt a NumPy array
array_data = np.array([1, 2, 3, 4, 5], dtype=np.uint8)
encrypted_array = nal.encrypt(array_data)
```

### 🔓 Decrypting Data

Use the `decrypt` method to decrypt an encrypted message.

Example:

```python
# Decrypt the encrypted string
decrypted = nal.decrypt(encrypted)  # Returns a list of integers

# Decrypt binary data
decrypted_binary = nal.decrypt(encrypted_binary)

# Decrypt a NumPy array
decrypted_array = nal.decrypt(encrypted_array)
```

## 💻 Command-Line Interface (CLI) Usage

The `nalenc` command-line tool allows for quick encryption, decryption, and key generation without writing Python code.

### Verify Installation

```bash
nalenc --version
```

### CLI Commands

The tool provides three main commands: `generate-key`, `encrypt`, and `decrypt`.

#### 1. Generate Key (`generate-key`)

Creates a new 512-byte encryption key.

```bash
nalenc generate-key [OPTIONS]
```

**Options:**

*   `-o, --output FILE`: Output file for the key (default: stdout).
*   `-a, --ascii`: Output key in ASCII format (Base64 with headers `----BEGIN NAL KEY----` / `----END NAL KEY----`).

**Examples:**

*   Generate a binary key file:
    ```bash
    nalenc generate-key > mykey.bin
    ```
*   Generate an ASCII key file:
    ```bash
    nalenc generate-key -o mykey.key -a
    ```

#### 2. Encrypt Data (`encrypt`)

Encrypts data from a file or stdin using a specified key.

```bash
nalenc encrypt -k KEY_FILE [OPTIONS] [INPUT_FILE]
```

**Arguments:**

*   `INPUT_FILE`: Input file to encrypt (default: stdin).

**Options:**

*   `-k, --key FILE`: **(Required)** Encryption key file (binary or ASCII).
*   `-o, --output FILE`: Output file for encrypted data (default: stdout).
*   `-a, --ascii`: Output result in ASCII format (Base64 with headers `----BEGIN NAL MESSAGE----` / `----END NAL MESSAGE----`).

#### 3. Decrypt Data (`decrypt`)

Decrypts data from a file or stdin using a specified key.

```bash
nalenc decrypt -k KEY_FILE [OPTIONS] [INPUT_FILE]
```

**Arguments:**

*   `INPUT_FILE`: Input file to decrypt (binary or ASCII, default: stdin).

**Options:**

*   `-k, --key FILE`: **(Required)** Encryption key file (binary or ASCII).
*   `-o, --output FILE`: Output file for decrypted data (default: stdout).
*   `-a, --ascii`: Output result in ASCII format. (Note: Only affects output format; input format is auto-detected if it uses the standard headers).

### 📂 Working with Binary Files

NALEnc supports encrypting and decrypting binary files. Read the file as binary data, process it, and save the result. Cast the encrypted data to `bytes` before writing to a file.

Example:

```python
# Encrypt a binary file
with open("input.bin", "rb") as f:
    data = f.read()

encrypted_data = nal.encrypt(data)

with open("output.enc", "wb") as f:
    f.write(bytes(encrypted_data))

# Decrypt the binary file
with open("output.enc", "rb") as f:
    encrypted_data = f.read()

decrypted_data = nal.decrypt(encrypted_data)

with open("decrypted.bin", "wb") as f:
    f.write(bytes(decrypted_data))
```

---

## 📈 Optimal Message Size

For best performance, ensure message sizes are `2048n - 2`, where `n` is a positive integer. This helps maximize efficiency during encryption and decryption.

---

## 📚 API Reference

### Class: `NALEnc`

#### Constructor

```python
NALEnc(password: str | bytes | Iterable[int] | np.types.NDArray[np.uint8])
```

- **password**: The encryption password. Acceptable types:
  - String
  - Byte sequence
  - Iterable of integers (0-255)
  - NumPy array (`np.types.NDArray[np.uint8]`)

#### Methods

##### `encrypt(msg: str | bytes | Iterable[int] | np.types.NDArray[np.uint8])`

Encrypts the given message.

- **msg**: The message to encrypt. Input types:
  - String
  - Byte sequence
  - Iterable of integers (0-255)
  - NumPy array (`np.types.NDArray[np.uint8]`)
- **Returns**: The encrypted message as a list of integers.

##### `decrypt(msg: str | bytes | Iterable[int] | np.types.NDArray[np.uint8])`

Decrypts the given encrypted message.

- **msg**: The encrypted message. Input types:
  - String
  - Byte sequence
  - Iterable of integers (0-255)
  - NumPy array (`np.types.NDArray[np.uint8]`)
- **Returns**: The decrypted message as a list of integers.

---

## 💡 Example Code

```python
import nalenc
import numpy as np

# Generate a random password
password = np.random.randint(0, 256, size=512, dtype=np.uint8)

# Create an instance of NALEnc
nal = nalenc.NALEnc(password)

# Encrypt a message
message = "Encrypt this message!"
encrypted = nal.encrypt(message)

# Decrypt the message
decrypted = nal.decrypt(encrypted)

print("Original:", message)
print("Encrypted:", bytes(encrypted))  # Cast to bytes for readability
print("Decrypted:", bytes(decrypted))
```

---

## 📜 License

This library is licensed under the LGPL License. See the COPYING and COPYING.LESSER files for more information.

---

For questions, feedback, or contributions, feel free to open an issue on the [GitHub repository](https://github.com/AsfhtgkDavid/NAL-Encryption).

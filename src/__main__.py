import argparse
import sys
import base64

import numpy as np

from .nalenc import NALEnc
from . import __version__ as nalenc_version

KEY_HEADER = "----BEGIN NAL KEY----"
KEY_FOOTER = "----END NAL KEY----"
MSG_HEADER = "----BEGIN NAL MESSAGE----"
MSG_FOOTER = "----END NAL MESSAGE----"
EXPECTED_KEY_LEN = 512

def read_key(key_path: str) -> bytes:
    try:
        with open(key_path, 'rb') as f:
            content_bytes = f.read()

        try:
            content_text = content_bytes.decode('utf-8', errors='strict')
            lines = content_text.strip().splitlines()
            if lines[0] == KEY_HEADER and lines[-1] == KEY_FOOTER:
                base64_content = "".join(lines[1:-1])
                key_bytes = base64.b64decode(base64_content)
                if len(key_bytes) == EXPECTED_KEY_LEN:
                    return key_bytes
                else:
                    raise ValueError(f"Неправильна довжина ключа в ASCII файлі: {len(key_bytes)}, очікувалось {EXPECTED_KEY_LEN}")

        except UnicodeDecodeError:
            pass

        if len(content_bytes) == EXPECTED_KEY_LEN:
            return content_bytes
        else:
             raise ValueError(f"Неправильна довжина ключа у файлі: {len(content_bytes)}, очікувалось {EXPECTED_KEY_LEN} байт (або ASCII формат)")

    except FileNotFoundError:
        print(f"Помилка: Файл ключа не знайдено: {key_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Помилка під час читання ключа '{key_path}': {e}", file=sys.stderr)
        sys.exit(1)

def read_input(input_path: str | None) -> bytes:
    try:
        if input_path is None or input_path == '-':
            return sys.stdin.buffer.read()
        else:
            with open(input_path, 'rb') as f:
                return f.read()
    except FileNotFoundError:
        print(f"Помилка: Вхідний файл не знайдено: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Помилка під час читання вхідних даних '{input_path}': {e}", file=sys.stderr)
        sys.exit(1)

def write_output(data: bytes, output_path: str | None, ascii_format: bool, data_type: str):
    output_content: bytes | str

    if ascii_format:
        header, footer = "", ""
        if data_type == 'key':
            header, footer = KEY_HEADER, KEY_FOOTER
        elif data_type == 'message':
            header, footer = MSG_HEADER, MSG_FOOTER

        base64_data = base64.b64encode(data).decode('utf-8')
        lines = [base64_data[i:i+64] for i in range(0, len(base64_data), 64)]
        output_content = f"{header}\n" + "\n".join(lines) + f"\n{footer}\n"
        if output_path is None or output_path == '-':
            try:
                sys.stdout.write(output_content)
            except Exception as e:
                 print(f"Помилка під час запису в stdout: {e}", file=sys.stderr)
                 sys.exit(1)
        else:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(output_content)
            except Exception as e:
                print(f"Помилка під час запису у файл '{output_path}': {e}", file=sys.stderr)
                sys.exit(1)

    else:
        output_content = data
        if output_path is None or output_path == '-':
             try:
                sys.stdout.buffer.write(output_content)
                sys.stdout.buffer.flush()
             except Exception as e:
                 print(f"Помилка під час запису в stdout (бінарний режим): {e}", file=sys.stderr)
                 sys.exit(1)
        else:
            try:
                with open(output_path, 'wb') as f:
                    f.write(output_content)
            except Exception as e:
                print(f"Помилка під час запису у файл '{output_path}': {e}", file=sys.stderr)
                sys.exit(1)

def handle_generate_key(args: argparse.Namespace):
    key_bytes = np.random.randint(0, 256, size=(EXPECTED_KEY_LEN,), dtype=np.uint8).tobytes()
    write_output(key_bytes, args.output, args.ascii, 'key')

def handle_encrypt(args: argparse.Namespace):
    key_bytes = read_key(args.key)
    input_data = read_input(args.input_file)

    try:
        nal = NALEnc(key_bytes)
        encrypted_data_list = nal.encrypt(input_data)
        encrypted_data_bytes = bytes(encrypted_data_list)
        write_output(encrypted_data_bytes, args.output, args.ascii, 'message')
    except Exception as e:
        print(f"Помилка під час шифрування: {e}", file=sys.stderr)
        sys.exit(1)

def handle_decrypt(args: argparse.Namespace):
    key_bytes = read_key(args.key)
    input_data = read_input(args.input_file)

    try:
        nal = NALEnc(key_bytes)
        decrypted_data_list = nal.decrypt(input_data)
        decrypted_data_bytes = bytes(decrypted_data_list)
        write_output(decrypted_data_bytes, args.output, args.ascii, 'message')
    except Exception as e:
        print(f"Помилка під час розшифрування: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="NAL Encryption CLI інструмент.",
        prog="nalenc"
    )
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {nalenc_version}')

    subparsers = parser.add_subparsers(dest="command", required=True, help="Доступні команди")

    parser_genkey = subparsers.add_parser("generate-key", help="Згенерувати новий ключ шифрування (512 байт)")
    parser_genkey.add_argument("-o", "--output", type=str, default=None, help="Файл для виведення ключа (за замовчуванням: stdout)")
    parser_genkey.add_argument("-a", "--ascii", action="store_true", help="Вивести ключ у форматі ASCII (Base64 із заголовками)")
    parser_genkey.set_defaults(func=handle_generate_key)

    parser_encrypt = subparsers.add_parser("encrypt", help="Зашифрувати дані")
    parser_encrypt.add_argument("-k", "--key", type=str, required=True, help="Файл з ключем шифрування")
    parser_encrypt.add_argument("-o", "--output", type=str, default=None, help="Файл для виведення результату (за замовчуванням: stdout)")
    parser_encrypt.add_argument("-a", "--ascii", action="store_true", help="Вивести результат у форматі ASCII (Base64 із заголовками)")
    parser_encrypt.add_argument("input_file", type=str, nargs='?', default=None, help="Вхідний файл для шифрування (за замовчуванням: stdin)")
    parser_encrypt.set_defaults(func=handle_encrypt)

    parser_decrypt = subparsers.add_parser("decrypt", help="Розшифрувати дані")
    parser_decrypt.add_argument("-k", "--key", type=str, required=True, help="Файл з ключем шифрування")
    parser_decrypt.add_argument("-o", "--output", type=str, default=None, help="Файл для виведення результату (за замовчуванням: stdout)")
    parser_decrypt.add_argument("-a", "--ascii", action="store_true", help="Вивести результат у форматі ASCII (Base64 із заголовками). Вхідні дані також можуть бути в цьому форматі.")
    parser_decrypt.add_argument("input_file", type=str, nargs='?', default=None, help="Вхідний файл для розшифрування (за замовчуванням: stdin)")
    parser_decrypt.set_defaults(func=handle_decrypt)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()

"""
   NAL Encryption. Easy encryption
   Copyright (C) 2025 David Lishchyshen

   This library is free software; you can redistribute it and/or
   modify it under the terms of the GNU Lesser General Public
   License as published by the Free Software Foundation; either
   version 3 of the License, or (at your option) any later version.

   This library is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
   Lesser General Public License for more details.

   You should have received a copy of the GNU Lesser General Public License
   along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from typing import Iterable
import numpy as np
from numpy import typing as npt

from .helpers import finish_message, encrypt_loop_uint8, encrypt_loop_uint64, decrypt_loop_uint8, decrypt_loop_uint64
from .helpers import cut_message, split_message

input_type = str | bytes | Iterable[int] | npt.NDArray[np.uint8]


class NALEnc:
    def __init__(self, passwd: input_type):
        passwd_encoded = self.__encode_value(passwd)
        if len(passwd_encoded) != 512: raise ValueError("passwd len must equal 512 byte")
        self.__passwd = passwd_encoded
        self.__prepare_passwds()

    def encrypt(self, msg: input_type) -> list[int]:
        message = self.__encode_value(msg)
        message = finish_message(message, self.__passwd)

        parts = split_message(message)
        parts = encrypt_loop_uint8(parts, self.__prepared_passwds) if len(parts[0]) < 65536 else encrypt_loop_uint64(parts, self.__prepared_passwds)

        res = np.ravel(parts)

        return res.tolist()

    def decrypt(self, msg: input_type) -> list[int]:
        message = self.__encode_value(msg)

        parts = split_message(message)

        assert parts.ndim == 2

        parts = decrypt_loop_uint8(parts, self.__prepared_passwds) if len(parts[0]) < 65536 else decrypt_loop_uint64(parts, self.__prepared_passwds)

        res = np.ravel(parts)

        return cut_message(res).tolist() # type: ignore

    def __prepare_passwds(self) -> None:
        idx_array = np.arange(512)
        self.__prepared_passwds = np.empty((256, 512), np.uint8)
        self.__prepared_passwds[0] = self.__passwd
        self.__prepared_passwds[1] = np.where(idx_array != 0,
                                              self.__prepared_passwds[0] ^ self.__prepared_passwds[0, 0],
                                              self.__prepared_passwds[0])
        for i in range(1, 255):
            xor_value = self.__prepared_passwds[i - 1][i]
            self.__prepared_passwds[i + 1] = np.where(idx_array != i, self.__prepared_passwds[i - 1] ^ xor_value,
                                                      self.__prepared_passwds[i - 1])

    @staticmethod
    def __encode_value(value: input_type) -> npt.NDArray[np.uint8]:
        try:
            if isinstance(value, str):
                return np.fromiter(value.encode(), np.uint8)
            else:
                return np.fromiter(value, np.uint8)
        except (ValueError, TypeError):
            raise TypeError("Argument must be str | bytes | Iterable[int] | NDArray[uint8]")


__all__ = ["NALEnc"]

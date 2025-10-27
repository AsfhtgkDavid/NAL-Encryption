import numpy as np
from numba import njit, prange
from numpy import typing as npt


@njit(cache=True)
def _crypt_part8(
    dest: npt.NDArray[np.uint8],
    part: npt.NDArray[np.uint8],
    i: int,
    part_num: int,
    prepared_passwds: npt.NDArray[np.uint8],
    decrypt: bool = False,
) -> None:
    if len(part) % 512 != 0 or len(part) == 0:
        raise ValueError("Part length must be equal 526k, k != 0")
    used_prepared_passwd = prepared_passwds[-i - 1 if decrypt else i]
    n_shifts = len(part) // 512

    for block in range(n_shifts):
        shift = block + part_num
        for j in range(512):
            dest[block * 512 + j] = (
                part[block * 512 + j] ^ used_prepared_passwd[(j - shift) % 512]
            )


@njit(cache=True)
def _crypt_parts8(
    parts: npt.NDArray[np.uint8],
    i: int,
    prepared_passwds: npt.NDArray[np.uint8],
    decrypt: bool = False,
) -> npt.NDArray[np.uint8]:
    res = np.empty_like(parts)
    for idx in prange(4):
        _crypt_part8(res[idx], parts[idx], i, idx, prepared_passwds, decrypt)
    return res


@njit(cache=True)
def _crypt_block64_inplace(
    dest: npt.NDArray[np.uint64],
    src: npt.NDArray[np.uint64],
    used_prepared_passwd: npt.NDArray[np.uint64],
    shift: int,
) -> None:
    n = dest.shape[0]
    for i in prange(n):
        idx = (i - shift) % 64
        dest[i] = src[i] ^ used_prepared_passwd[idx]


@njit(cache=True)
def _crypt_part64_inplace(
    dest: npt.NDArray[np.uint8],
    src: npt.NDArray[np.uint8],
    i: int,
    part_num: int,
    prepared_passwds: npt.NDArray[np.uint8],
    decrypt: bool = False,
) -> None:
    if len(src) % 512 != 0 or len(src) == 0:
        raise ValueError("Part length must be equal 526k, k != 0")

    used_prepared_passwd = prepared_passwds[-i - 1 if decrypt else i].view(np.uint64)
    src64 = src.view(np.uint64)
    dest64 = dest.view(np.uint64)

    n_blocks = len(src64) // 64
    block_size = 64

    for block in range(n_blocks):
        block_offset = block * block_size
        shift = block + part_num
        _crypt_block64_inplace(
            dest64[block_offset : block_offset + block_size],
            src64[block_offset : block_offset + block_size],
            used_prepared_passwd,
            shift,
        )


@njit(parallel=True, cache=True)
def _crypt_parts64(
    parts: npt.NDArray[np.uint8],
    i: int,
    prepared_passwds: npt.NDArray[np.uint8],
    decrypt: bool = False,
) -> npt.NDArray[np.uint8]:
    tmp = np.empty_like(parts)
    for idx in prange(4):
        _crypt_part64_inplace(tmp[idx], parts[idx], i, idx, prepared_passwds, decrypt)
    return tmp


@njit(cache=True)
def finish_message(
    msg: npt.NDArray[np.uint8], passwd: npt.NDArray[np.uint8]
) -> npt.NDArray[np.uint8]:
    additional_len = (2048 - (len(msg) + 2) % 2048) % 2048
    if additional_len != 2046 or len(msg) % 2048 == 0:
        res = np.empty(len(msg) + additional_len + 2, np.uint8)
        res[2 : len(msg) + 2] = msg
        l1, l2 = additional_len >> 8, additional_len & 0xFF
        current_len = len(msg)
        for i in range(additional_len):
            k = int(passwd[i % len(passwd)])
            res[i + 2 + len(msg)] = np.bitwise_xor(
                res[(k % current_len) + 2], res[((k + 1) % current_len) + 2]
            )
            current_len += 1
        res[0] = l1
        res[1] = l2
    else:
        res = np.empty(len(msg) + 2, np.uint8)
        res[2 : len(msg) + 2] = msg
        res[:2] = np.zeros(2, np.uint8)
    return res


@njit(cache=True)
def encrypt_loop_uint8(
    parts: npt.NDArray[np.uint8], prepared_passwds: npt.NDArray[np.uint8]
) -> npt.NDArray[np.uint8]:
    for i in range(256):
        parts[:3] = parts[:3] ^ parts[1:4]
        parts = _crypt_parts8(parts, i, prepared_passwds)
        parts = np.vstack((parts[-1:], parts[:-1]))
    return parts


def encrypt_loop_uint64(
    parts: npt.NDArray[np.uint8], prepared_passwds: npt.NDArray[np.uint8]
) -> npt.NDArray[np.uint8]:
    for i in range(256):
        parts[:3] = parts[:3] ^ parts[1:4]
        parts = _crypt_parts64(parts, i, prepared_passwds)
        parts = np.vstack((parts[-1:], parts[:-1]))
    return parts


@njit(cache=True)
def decrypt_loop_uint8(
    parts: npt.NDArray[np.uint8], prepared_passwds: npt.NDArray[np.uint8]
) -> npt.NDArray[np.uint8]:
    for i in range(256):
        parts = np.vstack((parts[1:], parts[:1]))
        parts = _crypt_parts8(parts, i, prepared_passwds, True)
        for k in range(3):
            parts[2 - k] = parts[2 - k] ^ parts[3 - k]
    return parts


@njit(cache=True)
def decrypt_loop_uint64(
    parts: npt.NDArray[np.uint8], prepared_passwds: npt.NDArray[np.uint8]
) -> npt.NDArray[np.uint8]:
    for i in range(256):
        parts = np.vstack((parts[1:], parts[:1]))
        parts = _crypt_parts64(parts, i, prepared_passwds, True)
        for k in range(3):
            parts[2 - k] = parts[2 - k] ^ parts[3 - k]
    return parts


@njit(cache=True)
def cut_message(msg: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
    additional_len = (int(msg[0]) << 8) | int(msg[1])
    return msg[2 : len(msg) - int(additional_len)]


@njit(cache=True)
def split_message(msg: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
    return np.reshape(msg, (4, len(msg) // 4))

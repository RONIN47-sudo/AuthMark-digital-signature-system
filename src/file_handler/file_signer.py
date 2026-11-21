"""Read files safely and create detached signatures for their exact bytes."""

from __future__ import annotations

import os
from pathlib import Path
from typing import BinaryIO, TypeAlias

from cryptography.hazmat.primitives.asymmetric import rsa

from src.crypto.signer import sign_message

MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024
_READ_CHUNK_SIZE = 64 * 1024

FileInput: TypeAlias = str | os.PathLike[str] | bytes | bytearray | memoryview | BinaryIO


class FileHandlingError(OSError):
    """Raised when a document cannot be read or exceeds the configured limit."""


class FileTooLargeError(FileHandlingError):
    """Raised when document data exceeds ``MAX_FILE_SIZE_BYTES``."""


def _read_bounded(stream: BinaryIO) -> bytes:
    """Read at most the configured limit plus one byte from a binary stream."""
    content = bytearray()
    while len(content) <= MAX_FILE_SIZE_BYTES:
        remaining = MAX_FILE_SIZE_BYTES + 1 - len(content)
        chunk = stream.read(min(_READ_CHUNK_SIZE, remaining))
        if chunk == b"":
            break
        if not isinstance(chunk, bytes):
            raise FileHandlingError("Document input must be a binary stream.")
        content.extend(chunk)
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise FileTooLargeError(
            f"Document exceeds the {MAX_FILE_SIZE_BYTES}-byte size limit."
        )
    return bytes(content)


def read_file_bytes(file_input: FileInput) -> bytes:
    """Read supported document input within the size limit, without writing it."""
    if isinstance(file_input, (bytes, bytearray, memoryview)):
        content = bytes(file_input)
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise FileTooLargeError(
                f"Document exceeds the {MAX_FILE_SIZE_BYTES}-byte size limit."
            )
        return content

    if isinstance(file_input, (str, os.PathLike)):
        try:
            path = Path(file_input)
            with path.open("rb") as stream:
                return _read_bounded(stream)
        except FileHandlingError:
            raise
        except FileNotFoundError:
            raise FileHandlingError("Document file was not found.") from None
        except (OSError, TypeError, ValueError):
            raise FileHandlingError("Document file could not be read.") from None

    read_method = getattr(file_input, "read", None)
    if not callable(read_method):
        raise FileHandlingError(
            "Document input must be a file path, bytes, or a binary stream."
        )

    original_position: int | None = None
    try:
        seekable = getattr(file_input, "seekable", None)
        if callable(seekable):
            if not seekable():
                raise FileHandlingError("Document stream must be seekable.")
            original_position = file_input.tell()
            file_input.seek(0)
        content = _read_bounded(file_input)
    except FileHandlingError:
        raise
    except (OSError, ValueError, TypeError):
        raise FileHandlingError("Document stream could not be read.") from None
    finally:
        if original_position is not None:
            try:
                file_input.seek(original_position)
            except (OSError, ValueError, TypeError):
                raise FileHandlingError("Document stream position could not be restored.") from None
    return content


def sign_file(
    file_input: FileInput,
    private_key: rsa.RSAPrivateKey,
) -> bytes:
    """Create a detached signature for the exact bytes of a document.

    ``file_input`` may be a path, bytes-like document contents, or a binary
    file object. Seekable streams are read from their beginning and restored
    to their original position. Source documents are never written to. The
    signature bytes can be saved separately, for example as ``name.ext.sig``.

    Raises:
        FileHandlingError: If input cannot be read or exceeds the size limit.
        KeyManagementError or SigningError: If the private key is invalid or
            cryptographic signing fails.
    """
    original_bytes = read_file_bytes(file_input)
    return sign_message(original_bytes, private_key)

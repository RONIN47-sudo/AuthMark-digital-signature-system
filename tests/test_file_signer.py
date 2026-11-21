"""Tests for signing arbitrary document bytes."""

from io import BytesIO

import pytest

from src.crypto.key_manager import KeyManagementError, generate_rsa_key_pair
from src.crypto.verifier import verify_signature
from src.file_handler import file_signer
from src.file_handler.file_signer import (
    FileHandlingError,
    FileTooLargeError,
    sign_file,
)


@pytest.fixture(scope="module")
def key_pair():
    """Generate an ephemeral RSA key pair for file signing tests."""
    return generate_rsa_key_pair()


@pytest.mark.parametrize(
    ("filename", "content"),
    [
        ("sample.pdf", b"%PDF-1.7\nSynthetic AuthMark PDF data\n%%EOF\n"),
        ("sample.txt", b"Synthetic AuthMark text document\n"),
        ("sample.docx", b"PK\x03\x04Synthetic DOCX package bytes"),
        ("sample.png", b"\x89PNG\r\n\x1a\nSynthetic image data"),
    ],
)
def test_supported_document_types_are_signed(tmp_path, key_pair, filename, content):
    private_key, public_key = key_pair
    document = tmp_path / filename
    document.write_bytes(content)

    signature = sign_file(document, private_key)

    assert isinstance(signature, bytes)
    assert verify_signature(content, signature, public_key) is True


def test_empty_file_can_be_signed(tmp_path, key_pair):
    private_key, public_key = key_pair
    document = tmp_path / "empty.bin"
    document.write_bytes(b"")

    signature = sign_file(document, private_key)

    assert verify_signature(b"", signature, public_key) is True


def test_missing_file_has_file_handling_error(tmp_path, key_pair):
    private_key, _ = key_pair

    with pytest.raises(FileHandlingError, match="not found"):
        sign_file(tmp_path / "missing.pdf", private_key)


def test_unreadable_input_has_file_handling_error(tmp_path, key_pair):
    private_key, _ = key_pair
    directory = tmp_path / "not-a-file"
    directory.mkdir()

    with pytest.raises(FileHandlingError, match="could not be read"):
        sign_file(directory, private_key)


def test_invalid_private_key_is_rejected(tmp_path):
    document = tmp_path / "document.txt"
    document.write_bytes(b"content")

    with pytest.raises(KeyManagementError, match="must be an RSA key"):
        sign_file(document, object())


def test_incorrect_file_input_type_is_rejected(key_pair):
    private_key, _ = key_pair

    with pytest.raises(FileHandlingError, match="must be a file path"):
        sign_file(42, private_key)


def test_original_document_is_preserved_and_signature_is_detached(tmp_path, key_pair):
    private_key, public_key = key_pair
    content = b"Original bytes must remain exactly the same."
    document = tmp_path / "preserved.txt"
    document.write_bytes(content)

    signature = sign_file(document, private_key)

    assert document.read_bytes() == content
    assert not document.with_name("preserved.txt.sig").exists()
    assert verify_signature(document.read_bytes(), signature, public_key) is True


def test_binary_stream_signing_preserves_stream_position(key_pair):
    private_key, public_key = key_pair
    content = b"Binary stream content"
    stream = BytesIO(content)
    stream.seek(4)

    signature = sign_file(stream, private_key)

    assert stream.tell() == 4
    assert verify_signature(content, signature, public_key) is True


def test_oversized_file_is_rejected(tmp_path, key_pair, monkeypatch):
    private_key, _ = key_pair
    document = tmp_path / "oversized.bin"
    document.write_bytes(b"12345")
    monkeypatch.setattr(file_signer, "MAX_FILE_SIZE_BYTES", 4)

    with pytest.raises(FileTooLargeError, match="size limit"):
        sign_file(document, private_key)


def test_bytes_like_content_can_be_signed(key_pair):
    private_key, public_key = key_pair
    content = bytearray(b"Direct binary content")

    signature = sign_file(content, private_key)

    assert verify_signature(bytes(content), signature, public_key) is True

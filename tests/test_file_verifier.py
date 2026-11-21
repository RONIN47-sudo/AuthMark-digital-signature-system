"""Tests for detached document signature verification."""

import pytest

from src.crypto.key_manager import KeyManagementError, generate_rsa_key_pair
from src.crypto.verifier import VerificationError
from src.file_handler import file_signer
from src.file_handler.file_signer import FileHandlingError
from src.file_handler.file_signer import sign_file
from src.file_handler.file_verifier import verify_file_signature


@pytest.fixture(scope="module")
def key_pairs():
    """Generate matching and unrelated ephemeral RSA key pairs."""
    return generate_rsa_key_pair(), generate_rsa_key_pair()


@pytest.mark.parametrize(
    ("filename", "content"),
    [
        ("sample.pdf", b"%PDF-1.7\nSynthetic AuthMark PDF data\n%%EOF\n"),
        ("sample.txt", b"Synthetic AuthMark text document\n"),
        ("sample.docx", b"PK\x03\x04Synthetic DOCX package bytes"),
        ("sample.bin", b"\x00\x01\xff\x80Arbitrary binary document bytes"),
    ],
)
def test_supported_document_types_verify(tmp_path, key_pairs, filename, content):
    (private_key, public_key), _ = key_pairs
    document = tmp_path / filename
    document.write_bytes(content)
    signature = sign_file(document, private_key)

    assert verify_file_signature(document, signature, public_key) is True


def test_empty_file_verifies(tmp_path, key_pairs):
    (private_key, public_key), _ = key_pairs
    document = tmp_path / "empty.bin"
    document.write_bytes(b"")
    signature = sign_file(document, private_key)

    assert verify_file_signature(document, signature, public_key) is True


def test_modified_document_is_rejected(tmp_path, key_pairs):
    (private_key, public_key), _ = key_pairs
    document = tmp_path / "modified.txt"
    document.write_bytes(b"Original document")
    signature = sign_file(document, private_key)
    document.write_bytes(b"Modified document")

    assert verify_file_signature(document, signature, public_key) is False


def test_corrupted_signature_is_rejected(tmp_path, key_pairs):
    (private_key, public_key), _ = key_pairs
    document = tmp_path / "document.pdf"
    document.write_bytes(b"Synthetic PDF bytes")
    corrupted = bytearray(sign_file(document, private_key))
    corrupted[-1] ^= 1

    assert verify_file_signature(document, bytes(corrupted), public_key) is False


def test_incorrect_public_key_is_rejected(tmp_path, key_pairs):
    (private_key, _), (_, unrelated_public_key) = key_pairs
    document = tmp_path / "document.docx"
    document.write_bytes(b"Synthetic DOCX bytes")
    signature = sign_file(document, private_key)

    assert verify_file_signature(document, signature, unrelated_public_key) is False


def test_missing_document_raises_file_handling_error(tmp_path, key_pairs):
    (_, public_key), _ = key_pairs

    with pytest.raises(FileHandlingError, match="not found"):
        verify_file_signature(tmp_path / "missing.pdf", b"signature", public_key)


def test_oversized_document_raises_file_handling_error(
    tmp_path,
    key_pairs,
    monkeypatch,
):
    (_, public_key), _ = key_pairs
    document = tmp_path / "large.bin"
    document.write_bytes(b"12345")
    monkeypatch.setattr(file_signer, "MAX_FILE_SIZE_BYTES", 4)

    with pytest.raises(FileHandlingError, match="size limit"):
        verify_file_signature(document, b"signature", public_key)


def test_invalid_public_key_raises_key_management_error(tmp_path):
    document = tmp_path / "document.txt"
    document.write_bytes(b"content")

    with pytest.raises(KeyManagementError, match="must be an RSA key"):
        verify_file_signature(document, b"signature", object())


def test_malformed_signature_returns_false(tmp_path, key_pairs):
    (_, public_key), _ = key_pairs
    document = tmp_path / "document.png"
    document.write_bytes(b"Synthetic binary image bytes")

    assert verify_file_signature(document, b"malformed", public_key) is False


def test_non_bytes_signature_is_invalid_input(tmp_path, key_pairs):
    (_, public_key), _ = key_pairs
    document = tmp_path / "document.txt"
    document.write_bytes(b"content")

    with pytest.raises(TypeError, match="Signature data must be provided as bytes"):
        verify_file_signature(document, "not-bytes", public_key)


def test_original_document_is_preserved(tmp_path, key_pairs):
    (private_key, public_key), _ = key_pairs
    content = b"Document content stays unchanged"
    document = tmp_path / "preserved.txt"
    document.write_bytes(content)
    signature = sign_file(document, private_key)

    assert verify_file_signature(document, signature, public_key) is True
    assert document.read_bytes() == content


def test_end_to_end_sign_modify_verify_workflow(tmp_path):
    private_key, public_key = generate_rsa_key_pair()
    document = tmp_path / "workflow.pdf"
    original = b"%PDF-1.7\nSynthetic end-to-end document\n%%EOF\n"
    document.write_bytes(original)

    signature = sign_file(document, private_key)
    assert verify_file_signature(document, signature, public_key) is True

    document.write_bytes(b"%PDF-1.7\nModified end-to-end document\n%%EOF\n")
    assert verify_file_signature(document, signature, public_key) is False


def test_unexpected_verification_error_is_not_converted_to_false(
    tmp_path,
    key_pairs,
    monkeypatch,
):
    (_, public_key), _ = key_pairs
    document = tmp_path / "document.txt"
    document.write_bytes(b"content")

    def fail_verification(*args, **kwargs):
        raise VerificationError("internal failure")

    monkeypatch.setattr("src.file_handler.file_verifier.verify_signature", fail_verification)
    with pytest.raises(VerificationError, match="internal failure"):
        verify_file_signature(document, b"signature", public_key)

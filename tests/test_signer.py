"""Tests for RSA-PSS message signature generation."""

import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from src.crypto.key_manager import KeyManagementError, generate_rsa_key_pair
from src.crypto.signer import SigningError, sign_message


@pytest.fixture(scope="module")
def private_key():
    """Generate an ephemeral RSA-3072 key for this test module."""
    return generate_rsa_key_pair()[0]


def test_successful_signature_generation(private_key, tmp_path):
    message_file = tmp_path / "message.bin"
    message_file.write_bytes(b"AuthMark signing test message")

    signature = sign_message(message_file.read_bytes(), private_key)

    assert signature
    assert isinstance(signature, bytes)


def test_signature_output_is_non_empty_bytes(private_key):
    signature = sign_message(b"message", private_key)

    assert isinstance(signature, bytes)
    assert len(signature) > 0


def test_different_messages_produce_different_signatures(private_key):
    first_signature = sign_message(b"first message", private_key)
    second_signature = sign_message(b"second message", private_key)

    assert first_signature != second_signature


def test_empty_message_can_be_signed(private_key):
    signature = sign_message(b"", private_key)

    assert isinstance(signature, bytes)
    assert signature


def test_invalid_private_key_is_rejected():
    weak_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    with pytest.raises(KeyManagementError, match="must be 3072 bits"):
        sign_message(b"message", weak_key)


def test_incorrect_key_type_is_rejected():
    with pytest.raises(KeyManagementError, match="must be an RSA key"):
        sign_message(b"message", object())


def test_non_bytes_message_is_rejected(private_key):
    with pytest.raises(SigningError, match="must be provided as bytes"):
        sign_message("text message", private_key)

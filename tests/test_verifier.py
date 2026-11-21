"""Tests for RSA-PSS signature verification."""

import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from src.crypto.key_manager import KeyManagementError, generate_rsa_key_pair
from src.crypto.signer import sign_message
from src.crypto.verifier import verify_signature


@pytest.fixture(scope="module")
def key_pairs():
    """Generate ephemeral matching and unrelated RSA key pairs."""
    return generate_rsa_key_pair(), generate_rsa_key_pair()


def test_successful_signature_verification(key_pairs):
    (private_key, public_key), _ = key_pairs
    message = b"AuthMark verification test"
    signature = sign_message(message, private_key)

    assert verify_signature(message, signature, public_key) is True


def test_modified_message_is_rejected(key_pairs):
    (private_key, public_key), _ = key_pairs
    signature = sign_message(b"original message", private_key)

    assert verify_signature(b"modified message", signature, public_key) is False


def test_incorrect_public_key_is_rejected(key_pairs):
    (private_key, _), (_, unrelated_public_key) = key_pairs
    message = b"message"
    signature = sign_message(message, private_key)

    assert verify_signature(message, signature, unrelated_public_key) is False


def test_corrupted_signature_is_rejected(key_pairs):
    (private_key, public_key), _ = key_pairs
    message = b"message"
    signature = bytearray(sign_message(message, private_key))
    signature[-1] ^= 1

    assert verify_signature(message, bytes(signature), public_key) is False


def test_empty_message_verification(key_pairs):
    (private_key, public_key), _ = key_pairs
    signature = sign_message(b"", private_key)

    assert verify_signature(b"", signature, public_key) is True


def test_invalid_public_key_is_rejected():
    with pytest.raises(KeyManagementError, match="must be an RSA key"):
        verify_signature(b"message", b"signature", object())


def test_non_bytes_signature_input_is_rejected(key_pairs):
    (_, public_key), _ = key_pairs

    with pytest.raises(TypeError, match="Signature data must be provided as bytes"):
        verify_signature(b"message", "signature", public_key)


def test_malformed_and_wrong_length_signatures_are_rejected(key_pairs):
    (_, public_key), _ = key_pairs

    assert verify_signature(b"message", b"malformed", public_key) is False
    assert verify_signature(b"message", bytes(384), public_key) is False


def test_signer_and_verifier_are_compatible(key_pairs):
    (private_key, public_key), _ = key_pairs
    message = b"shared RSA-PSS and SHA-256 parameters"

    signature = sign_message(message, private_key)

    assert verify_signature(message, signature, public_key) is True


def test_end_to_end_sign_modify_and_verify_workflow():
    private_key, public_key = generate_rsa_key_pair()
    original_message = b"Original AuthMark content"
    signature = sign_message(original_message, private_key)

    assert verify_signature(original_message, signature, public_key) is True
    modified_message = b"Modified AuthMark content"
    assert verify_signature(modified_message, signature, public_key) is False


def test_invalid_rsa_public_key_size_is_rejected():
    weak_public_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    ).public_key()

    with pytest.raises(KeyManagementError, match="must be 3072 bits"):
        verify_signature(b"message", b"signature", weak_public_key)

"""Tests for AuthMark's RSA key management module."""

import pytest
from cryptography.hazmat.primitives import serialization

from src.crypto.key_manager import (
    KeyManagementError,
    RSA_KEY_SIZE,
    RSA_PUBLIC_EXPONENT,
    extract_public_key,
    generate_rsa_key_pair,
    load_private_key,
    load_public_key,
    serialize_private_key,
    serialize_public_key,
)


@pytest.fixture(scope="module")
def key_pair():
    """Share one generated test key pair across the module."""
    return generate_rsa_key_pair()


def test_rsa_key_generation_and_parameters(key_pair):
    private_key, public_key = key_pair

    assert private_key.key_size == RSA_KEY_SIZE
    assert public_key.key_size == RSA_KEY_SIZE
    assert public_key.public_numbers().e == RSA_PUBLIC_EXPONENT


def test_public_key_serialization_and_loading(key_pair, tmp_path):
    _, public_key = key_pair
    pem_data = serialize_public_key(public_key)
    pem_file = tmp_path / "test_public.pem"
    pem_file.write_bytes(pem_data)

    assert pem_data.startswith(b"-----BEGIN PUBLIC KEY-----")
    loaded_key = load_public_key(pem_file.read_bytes())
    assert loaded_key.public_numbers() == public_key.public_numbers()


def test_private_key_is_encrypted_and_loads_with_password(key_pair, tmp_path):
    private_key, _ = key_pair
    pem_data = serialize_private_key(private_key, "test-only-password")
    pem_file = tmp_path / "test_private.pem"
    pem_file.write_bytes(pem_data)

    assert pem_data.startswith(b"-----BEGIN ENCRYPTED PRIVATE KEY-----")
    loaded_key = load_private_key(pem_file.read_bytes(), "test-only-password")
    assert loaded_key.private_numbers() == private_key.private_numbers()


def test_private_key_rejects_incorrect_password(key_pair):
    private_key, _ = key_pair
    pem_data = serialize_private_key(private_key, "correct-test-password")

    with pytest.raises(KeyManagementError, match="Unable to load the private key"):
        load_private_key(pem_data, "incorrect-test-password")


def test_invalid_public_key_is_rejected():
    with pytest.raises(KeyManagementError, match="Unable to load the public key"):
        load_public_key(b"not a public key")


def test_invalid_private_key_is_rejected():
    with pytest.raises(KeyManagementError, match="Unable to load the private key"):
        load_private_key(b"not a private key", "test-password")


def test_extracted_public_key_matches_private_key(key_pair):
    private_key, public_key = key_pair

    extracted_key = extract_public_key(private_key)
    assert extracted_key.public_numbers() == public_key.public_numbers()


def test_unencrypted_private_pem_is_rejected(key_pair):
    private_key, _ = key_pair
    unencrypted_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    with pytest.raises(KeyManagementError, match="Unable to load the private key"):
        load_private_key(unencrypted_pem, "test-password")


def test_empty_password_is_rejected(key_pair):
    private_key, _ = key_pair

    with pytest.raises(KeyManagementError, match="non-empty"):
        serialize_private_key(private_key, "")


def test_private_key_and_public_key_are_consistent(key_pair):
    private_key, public_key = key_pair

    assert extract_public_key(private_key).public_numbers() == public_key.public_numbers()

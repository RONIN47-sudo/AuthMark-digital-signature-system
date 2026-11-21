"""RSA key generation, validation, serialization, and loading for AuthMark."""

from __future__ import annotations

from typing import TypeAlias

from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

RSA_KEY_SIZE = 3072
RSA_PUBLIC_EXPONENT = 65537

PEMInput: TypeAlias = bytes | str
PasswordInput: TypeAlias = bytes | str


class KeyManagementError(ValueError):
    """Raised when a key is invalid, unsupported, or cannot be loaded."""


def generate_rsa_key_pair() -> tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    """Generate an RSA-3072 key pair using the standard public exponent."""
    private_key = rsa.generate_private_key(
        public_exponent=RSA_PUBLIC_EXPONENT,
        key_size=RSA_KEY_SIZE,
    )
    return private_key, private_key.public_key()


def validate_public_key(public_key: object) -> rsa.RSAPublicKey:
    """Validate an RSA public key and return it as a typed RSA key."""
    if not isinstance(public_key, rsa.RSAPublicKey):
        raise KeyManagementError("The supplied public key must be an RSA key.")
    if public_key.key_size != RSA_KEY_SIZE:
        raise KeyManagementError(f"RSA public keys must be {RSA_KEY_SIZE} bits.")
    if public_key.public_numbers().e != RSA_PUBLIC_EXPONENT:
        raise KeyManagementError(
            f"RSA public keys must use exponent {RSA_PUBLIC_EXPONENT}."
        )
    return public_key


def validate_private_key(private_key: object) -> rsa.RSAPrivateKey:
    """Validate an RSA private key and return it as a typed RSA key."""
    if not isinstance(private_key, rsa.RSAPrivateKey):
        raise KeyManagementError("The supplied private key must be an RSA key.")
    if private_key.key_size != RSA_KEY_SIZE:
        raise KeyManagementError(f"RSA private keys must be {RSA_KEY_SIZE} bits.")
    if private_key.private_numbers().public_numbers.e != RSA_PUBLIC_EXPONENT:
        raise KeyManagementError(
            f"RSA private keys must use exponent {RSA_PUBLIC_EXPONENT}."
        )
    return private_key


def extract_public_key(private_key: rsa.RSAPrivateKey) -> rsa.RSAPublicKey:
    """Return the public key corresponding to a validated RSA private key."""
    return validate_private_key(private_key).public_key()


def serialize_public_key(public_key: rsa.RSAPublicKey) -> bytes:
    """Serialize an RSA public key as PEM SubjectPublicKeyInfo."""
    checked_key = validate_public_key(public_key)
    return checked_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def _password_bytes(password: PasswordInput) -> bytes:
    """Validate and encode a password without including it in errors."""
    if isinstance(password, str):
        password_bytes = password.encode("utf-8")
    elif isinstance(password, bytes):
        password_bytes = password
    else:
        raise KeyManagementError("A non-empty text or byte password is required.")
    if not password_bytes:
        raise KeyManagementError("A non-empty text or byte password is required.")
    return password_bytes


def _pem_bytes(pem_data: PEMInput, key_label: str) -> bytes:
    """Normalize PEM input and reject malformed text without exposing input."""
    if isinstance(pem_data, str):
        try:
            pem_data = pem_data.encode("ascii", errors="strict")
        except UnicodeEncodeError:
            raise KeyManagementError(f"{key_label} data must be valid PEM.") from None
    if not isinstance(pem_data, bytes) or not pem_data:
        raise KeyManagementError(f"{key_label} data must be non-empty PEM bytes or text.")
    return pem_data


def serialize_private_key(
    private_key: rsa.RSAPrivateKey,
    password: PasswordInput,
) -> bytes:
    """Serialize a private key as encrypted PKCS#8 PEM.

    The private key is always encrypted with PyCA's BestAvailableEncryption;
    an empty password is rejected.
    """
    checked_key = validate_private_key(private_key)
    password_bytes = _password_bytes(password)
    try:
        return checked_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password_bytes),
        )
    except (TypeError, ValueError, UnsupportedAlgorithm) as exc:
        raise KeyManagementError("Unable to serialize the private key securely.") from None


def load_public_key(pem_data: PEMInput) -> rsa.RSAPublicKey:
    """Load and validate an RSA public key from PEM bytes or text."""
    pem_data = _pem_bytes(pem_data, "Public key")
    try:
        loaded_key = serialization.load_pem_public_key(pem_data)
    except (ValueError, TypeError, UnsupportedAlgorithm):
        raise KeyManagementError("Unable to load the public key; PEM data is invalid.") from None
    return validate_public_key(loaded_key)


def load_private_key(
    pem_data: PEMInput,
    password: PasswordInput,
) -> rsa.RSAPrivateKey:
    """Load and validate an encrypted RSA private key from PEM data."""
    pem_data = _pem_bytes(pem_data, "Private key")
    password_bytes = _password_bytes(password)
    try:
        loaded_key = serialization.load_pem_private_key(
            pem_data,
            password=password_bytes,
        )
    except (ValueError, TypeError, UnsupportedAlgorithm):
        raise KeyManagementError(
            "Unable to load the private key; the password may be incorrect or PEM data invalid."
        ) from None
    return validate_private_key(loaded_key)

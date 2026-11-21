"""RSA-PSS message signature generation for AuthMark."""

from __future__ import annotations

from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from src.crypto.key_manager import validate_private_key


class SigningError(ValueError):
    """Raised when message signing cannot be completed safely."""


def sign_message(message: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
    """Sign message bytes using RSA-PSS with SHA-256.

    Empty byte strings are valid messages and can be signed. The private key
    must be a validated RSA-3072 key using public exponent 65537.
    """
    if not isinstance(message, bytes):
        raise SigningError("Message data must be provided as bytes.")

    checked_key = validate_private_key(private_key)
    try:
        return checked_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
    except (TypeError, ValueError, UnsupportedAlgorithm):
        raise SigningError("Unable to generate a digital signature.") from None

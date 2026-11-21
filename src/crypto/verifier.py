"""RSA-PSS digital signature verification for AuthMark."""

from __future__ import annotations

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from src.crypto.key_manager import validate_public_key


class VerificationError(RuntimeError):
    """Raised when verification cannot run because of an application error."""


def verify_signature(
    message: bytes,
    signature: bytes,
    public_key: rsa.RSAPublicKey,
) -> bool:
    """Verify message bytes and return whether the RSA-PSS signature is valid.

    A malformed or cryptographically invalid signature returns ``False``.
    Invalid input types and invalid public keys raise explicit exceptions;
    unexpected verification failures raise :class:`VerificationError`.
    Empty messages are supported.
    """
    if not isinstance(message, bytes):
        raise TypeError("Message data must be provided as bytes.")
    if not isinstance(signature, bytes):
        raise TypeError("Signature data must be provided as bytes.")

    checked_key = validate_public_key(public_key)
    if len(signature) != (checked_key.key_size + 7) // 8:
        return False

    try:
        checked_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
    except InvalidSignature:
        return False
    except Exception:
        raise VerificationError("An internal error prevented signature verification.") from None
    return True

"""Verify detached digital signatures for document bytes."""

from __future__ import annotations

from cryptography.hazmat.primitives.asymmetric import rsa

from src.crypto.key_manager import validate_public_key
from src.crypto.verifier import verify_signature
from src.file_handler.file_signer import FileInput, read_file_bytes


def verify_file_signature(
    file_input: FileInput,
    signature: bytes,
    public_key: rsa.RSAPublicKey,
) -> bool:
    """Verify a detached signature against the exact bytes of a document.

    Returns ``True`` when the signature matches the document and public key,
    and ``False`` when the signature is cryptographically invalid. File errors,
    invalid input types, invalid public keys, and unexpected verification
    errors are raised distinctly by the underlying file and crypto modules.
    """
    if not isinstance(signature, bytes):
        raise TypeError("Signature data must be provided as bytes.")

    checked_key = validate_public_key(public_key)
    document_bytes = read_file_bytes(file_input)
    return verify_signature(document_bytes, signature, checked_key)

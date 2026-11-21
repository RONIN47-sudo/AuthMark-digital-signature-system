"""Dashboard page introducing AuthMark and its workflow."""

import streamlit as st

from src.ui.components import (
    bar_heading,
    body_text,
    feature_grid,
    page_header,
    section_heading,
    security_note,
    workflow,
)


def render() -> None:
    """Render the AuthMark dashboard."""
    page_header(
        "Digital trust, made verifiable",
        "Generate RSA keys, sign original documents, and independently verify detached signatures.",
    )
    bar_heading("Authenticity. Integrity. Assurance.")
    body_text(
        "AuthMark uses local RSA-PSS signatures with SHA-256 to help detect changes to "
        "messages and documents. A signature is separate from the document and does not encrypt it."
    )
    section_heading("Available operations")
    cards = [
        ("key", "Key management", "Generate RSA-3072 keys and export the public key plus an encrypted private key."),
        ("file-sign", "Document signing", "Sign the exact bytes of a file and download a detached <code>.sig</code> file."),
        ("shield-check", "Document verification", "Check a file and detached signature using its corresponding public key."),
    ]
    feature_grid(cards)
    left, right = st.columns(2, gap="large")
    with left:
        section_heading("Signing workflow", "file")
        workflow(["Document bytes", "SHA-256", "RSA-PSS<br>signature", "Detached<br><code>.sig</code> file"], spread=True)
    with right:
        section_heading("Verification workflow", "shield-check")
        workflow(["Document + detached<br>signature + public key", "Cryptographic<br>verification", "Valid or<br>Invalid"], spread=True)
    security_note(
        "A valid signature confirms a match between the supplied content and key. "
        "It does not prove the real-world identity of the key owner; authenticate public keys separately."
    )

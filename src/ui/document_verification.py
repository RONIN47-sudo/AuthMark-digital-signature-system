"""Document signature verification page."""

import streamlit as st

from src.crypto.key_manager import KeyManagementError, load_public_key
from src.crypto.verifier import VerificationError
from src.file_handler.file_signer import MAX_FILE_SIZE_BYTES, FileHandlingError
from src.file_handler.file_verifier import verify_file_signature
from src.ui.components import page_header, result_banner, security_note, workflow


def render() -> None:
    """Render document and detached-signature verification controls."""
    page_header(
        "Verify a document",
        "Check a document and its detached signature with the corresponding public key.",
    )
    workflow(["Document + detached<br>signature + public key", "Cryptographic<br>verification", "Valid or<br>Invalid"])
    security_note(
        "A valid result confirms that this key signed these exact bytes. It does not independently establish signer identity."
    )
    with st.form("verify_document_form"):
        document = st.file_uploader("Original document", key="verify_document_upload")
        signature_file = st.file_uploader(
            "Detached signature (.sig)", key="verify_signature_upload"
        )
        public_key_file = st.file_uploader(
            "Corresponding public key (PEM)", type=["pem"], key="verify_public_key_upload"
        )
        submitted = st.form_submit_button("Verify signature", type="primary")
    if submitted:
        if document is None or signature_file is None or public_key_file is None:
            st.error("Choose the document, detached signature, and public key.")
        elif document.size > MAX_FILE_SIZE_BYTES:
            st.error("The document exceeds AuthMark's 100 MiB limit.")
        else:
            try:
                public_key = load_public_key(public_key_file.getvalue())
                valid = verify_file_signature(
                    document.getvalue(),
                    signature_file.getvalue(),
                    public_key,
                )
                if valid:
                    result_banner(
                        True,
                        "Signature valid",
                        "The signature is valid for the supplied document and public key.",
                    )
                else:
                    result_banner(
                        False,
                        "Signature invalid",
                        "The signature does not match the supplied document and public key.",
                    )
            except (KeyManagementError, FileHandlingError, TypeError, VerificationError) as exc:
                st.error(str(exc))

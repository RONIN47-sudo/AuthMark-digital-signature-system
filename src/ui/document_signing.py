"""Document signing page using existing AuthMark backend modules."""

from pathlib import Path

import streamlit as st

from src.crypto.key_manager import KeyManagementError, load_private_key
from src.crypto.signer import SigningError
from src.file_handler.file_signer import (
    MAX_FILE_SIZE_BYTES,
    FileHandlingError,
    sign_file,
)
from src.ui.components import page_header, security_note, workflow


def render() -> None:
    """Render document upload, signing, and detached-signature download."""
    page_header(
        "Sign a document",
        "Create a detached signature for the original file bytes. The source document is not changed.",
    )
    workflow(["Document bytes", "SHA-256", "RSA-PSS<br>signature", "Detached<br><code>.sig</code> file"])
    security_note(
        "Files are processed locally and limited to 100 MiB. A digital signature does not encrypt the document."
    )
    with st.form("sign_document_form"):
        document = st.file_uploader("Document", key="sign_document_upload")
        private_key_file = st.file_uploader(
            "Encrypted private key (PEM)", type=["pem"], key="sign_private_key_upload"
        )
        password = st.text_input("Private-key password", type="password")
        submitted = st.form_submit_button("Sign document", type="primary")
    if submitted:
        if document is None or private_key_file is None:
            st.error("Choose both a document and an encrypted private key.")
        elif document.size > MAX_FILE_SIZE_BYTES:
            st.error("The document exceeds AuthMark's 100 MiB limit.")
        else:
            try:
                private_key = load_private_key(private_key_file.getvalue(), password)
                signature = sign_file(document.getvalue(), private_key)
                signature_name = f"{Path(document.name).name}.sig"
                st.session_state["authmark_signature_download"] = signature
                st.session_state["authmark_signature_filename"] = signature_name
                st.session_state["authmark_signature_source"] = Path(document.name).name
                st.success(f"Signature created for **{Path(document.name).name}**.")
            except (KeyManagementError, SigningError, FileHandlingError) as exc:
                st.error(str(exc))

    signature = st.session_state.get("authmark_signature_download")
    signature_name = st.session_state.get("authmark_signature_filename")
    source_name = st.session_state.get("authmark_signature_source")
    if signature and signature_name:
        st.caption(f"Detached signature for: {source_name}")
        st.download_button(
            "Download detached signature",
            data=signature,
            file_name=signature_name,
            mime="application/octet-stream",
        )
        if st.button("Clear signature from this session"):
            for state_key in (
                "authmark_signature_download",
                "authmark_signature_filename",
                "authmark_signature_source",
            ):
                st.session_state.pop(state_key, None)
            st.rerun()

"""RSA key generation and encrypted key downloads."""

import streamlit as st

from src.crypto.key_manager import (
    KeyManagementError,
    generate_rsa_key_pair,
    serialize_private_key,
    serialize_public_key,
)
from src.ui.components import fact_row, page_header, security_note


def render() -> None:
    """Render the RSA key generation interface."""
    page_header(
        "Key management",
        "Generate an RSA-3072 key pair. Your private key is encrypted with the password you choose.",
    )
    fact_row(
        [
            ("RSA-3072", "Standard public exponent 65537"),
            ("Encrypted PKCS#8", "Protected with your password"),
            ("Session only", "Never written to project storage"),
        ]
    )
    security_note(
        "Keep your private key and its password safe. AuthMark never displays the private-key contents. "
        "The encrypted key is held only in this browser session for download."
    )
    with st.form("generate_keys_form"):
        password = st.text_input("Private-key encryption password", type="password")
        confirmation = st.text_input("Confirm password", type="password")
        submitted = st.form_submit_button("Generate RSA-3072 key pair", type="primary")
    if submitted:
        if len(password) < 12:
            st.error("Use a password with at least 12 characters.")
        elif password != confirmation:
            st.error("The passwords do not match.")
        else:
            try:
                private_key, public_key = generate_rsa_key_pair()
                encrypted_private_pem = serialize_private_key(private_key, password)
                public_pem = serialize_public_key(public_key)
                st.session_state["authmark_private_key_download"] = encrypted_private_pem
                st.session_state["authmark_public_key_download"] = public_pem
                st.success("RSA-3072 key pair generated. Download and store both files securely.")
            except KeyManagementError as exc:
                st.error(str(exc))

    private_pem = st.session_state.get("authmark_private_key_download")
    public_pem = st.session_state.get("authmark_public_key_download")
    if private_pem and public_pem:
        col_private, col_public = st.columns(2)
        with col_private:
            st.download_button(
                "Download encrypted private key",
                data=private_pem,
                file_name="authmark_private_encrypted.pem",
                mime="application/x-pem-file",
            )
        with col_public:
            st.download_button(
                "Download public key",
                data=public_pem,
                file_name="authmark_public.pem",
                mime="application/x-pem-file",
            )
        if st.button("Clear generated key downloads"):
            st.session_state.pop("authmark_private_key_download", None)
            st.session_state.pop("authmark_public_key_download", None)
            st.rerun()

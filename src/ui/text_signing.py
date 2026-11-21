"""Optional text signing and verification interface."""

import streamlit as st

from src.crypto.key_manager import KeyManagementError, load_private_key, load_public_key
from src.crypto.signer import SigningError, sign_message
from src.crypto.verifier import VerificationError, verify_signature
from src.ui.components import page_header, result_banner, security_note


def render() -> None:
    """Render simple text-signing and verification tools."""
    page_header(
        "Text signing",
        "Sign UTF-8 text or verify a text signature using AuthMark's existing cryptographic modules.",
    )
    security_note(
        "Text is signed as UTF-8 bytes. Verification only succeeds if the message is identical, character for character."
    )
    sign_tab, verify_tab = st.tabs(["Sign text", "Verify text"])
    with sign_tab:
        with st.form("sign_text_form"):
            message = st.text_area("Message", height=150)
            private_key_file = st.file_uploader(
                "Encrypted private key (PEM)", type=["pem"], key="text_private_key"
            )
            password = st.text_input("Private-key password", type="password", key="text_password")
            submitted = st.form_submit_button("Sign message", type="primary")
        if submitted:
            if private_key_file is None:
                st.error("Choose an encrypted private key.")
            else:
                try:
                    private_key = load_private_key(private_key_file.getvalue(), password)
                    signature = sign_message(message.encode("utf-8"), private_key)
                    st.session_state["authmark_text_signature"] = signature
                    st.success("Text signature created.")
                except (KeyManagementError, SigningError) as exc:
                    st.error(str(exc))
        text_signature = st.session_state.get("authmark_text_signature")
        if text_signature:
            st.download_button(
                "Download text signature",
                text_signature,
                file_name="message.sig",
                mime="application/octet-stream",
            )

    with verify_tab:
        with st.form("verify_text_form"):
            message_to_verify = st.text_area("Original message", height=150, key="verify_text")
            signature_file = st.file_uploader("Detached signature", key="verify_text_signature")
            public_key_file = st.file_uploader(
                "Public key (PEM)", type=["pem"], key="verify_text_public_key"
            )
            verify_submitted = st.form_submit_button("Verify text signature", type="primary")
        if verify_submitted:
            if signature_file is None or public_key_file is None:
                st.error("Choose both the detached signature and public key.")
            else:
                try:
                    public_key = load_public_key(public_key_file.getvalue())
                    valid = verify_signature(
                        message_to_verify.encode("utf-8"),
                        signature_file.getvalue(),
                        public_key,
                    )
                    if valid:
                        result_banner(True, "Signature valid", "The signature matches this message and public key.")
                    else:
                        result_banner(False, "Signature invalid", "The signature does not match this message and public key.")
                except (KeyManagementError, TypeError, VerificationError) as exc:
                    st.error(str(exc))

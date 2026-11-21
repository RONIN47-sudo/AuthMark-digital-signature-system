"""Streamlit entry point for the AuthMark Digital Trust System."""

import streamlit as st

from src.ui import dashboard, document_signing, document_verification, key_management, text_signing
from src.ui.components import apply_styles, sidebar_brand, sidebar_footer


def main() -> None:
    """Configure the app shell and route navigation to each interface section."""
    st.set_page_config(
        page_title="AuthMark | Digital Trust & Verification",
        page_icon="🔏",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_styles()
    with st.sidebar:
        sidebar_brand()
        selected_page = st.radio(
            "Navigation",
            [
                "Dashboard",
                "Key Management",
                "Sign Document",
                "Verify Document",
                "Text Signing",
            ],
            label_visibility="collapsed",
        )
        sidebar_footer()

    pages = {
        "Dashboard": dashboard.render,
        "Key Management": key_management.render,
        "Sign Document": document_signing.render,
        "Verify Document": document_verification.render,
        "Text Signing": text_signing.render,
    }
    pages[selected_page]()


if __name__ == "__main__":
    main()

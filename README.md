# AuthMark

**AuthMark Digital Trust System**  
*Authenticity. Integrity. Assurance.*

AuthMark is a local Python application for generating and verifying detached digital signatures for messages and documents. It uses RSA-PSS with SHA-256 through the PyCA Cryptography library and provides a Streamlit interface.

> **Project status:** Milestones 1–7 are implemented. Local verification history remains planned.

## Problem and objectives

Documents and messages can be changed or attributed to an unauthorized source. AuthMark is intended to let users sign content with a private key and verify its integrity with the corresponding public key. A signature can establish a cryptographic relationship between content and a key; by itself, it does not prove the real-world identity of the key owner or encrypt the content.

Planned objectives:

- Generate and import RSA key pairs, protecting exported private keys with a password.
- Sign text and original document bytes with detached RSA-PSS/SHA-256 signatures.
- Verify signatures and report invalid or changed content clearly.
- Keep verification history locally without recording private keys, passwords, or document contents.
- Provide a Streamlit interface, automated tests, and technical documentation.

## Planned features

- Dashboard and navigation
- RSA key management (3072-bit default)
- Text signing and verification
- Document signing and verification without modifying the source file
- Tamper detection
- Local verification history with a clear-history option

The Streamlit interface includes dashboard, key management, document signing and verification, and text signing.

## Technology

- Python 3
- PyCA Cryptography: RSA, RSA-PSS, MGF1, and SHA-256
- Streamlit
- SQLite (planned for local history)
- Pytest

## Cryptographic design

The planned signature configuration is RSA-3072, RSA-PSS, MGF1 with SHA-256, SHA-256 hashing, and the maximum permitted PSS salt length. Signing and verification will use the library's established signing APIs. Document signatures will be detached and computed over the original file bytes.

## Project layout

```text
src/       Application and UI packages
tests/     Automated tests
keys/      Local key workspace (private material is ignored by Git)
signatures/Generated detached signatures (ignored by Git)
data/      Local application data (database files are ignored by Git)
docs/      Architecture, cryptographic workflow, security, and testing docs
```

## Setup

Create and activate a virtual environment from the repository root, then install the declared dependencies.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Running the application

Launch the application from the repository root with:

```bash
python -m streamlit run src/main.py
```

## Testing

Run the automated tests from the repository root:

```bash
python -m pytest
```

## Security considerations and limitations

The application performs cryptographic operations locally and does not transmit keys, signatures, or documents. Generated encrypted private-key PEM is held in Streamlit session memory until cleared or the session ends; it is not written to project storage. A private key should be stored securely; never share it or commit it to version control. Public key authenticity must be established separately (for example, by exchanging it through an authenticated channel or using certificates). A digital signature does not encrypt a document. Document uploads are limited to 100 MiB.

## Documentation

The `docs/` directory is reserved for architecture, cryptographic workflow, security, and testing documentation.

## License

No license has been selected yet.

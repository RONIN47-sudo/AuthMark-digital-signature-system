# AuthMark
### Digital Signature and Verification System

**Authenticity. Integrity. Assurance.**

AuthMark is a Python-based Digital Signature and Verification System designed to establish the authenticity and integrity of digital documents and text messages using public-key cryptography.

Built with Python, PyCA Cryptography, and Streamlit, AuthMark provides an interface for generating RSA key pairs, digitally signing documents, and independently verifying detached signatures.

---

## Overview

Digital documents are frequently exchanged across networks and storage platforms. Ensuring that these documents have not been altered is an important aspect of information security.

AuthMark addresses this requirement through asymmetric cryptography and digital signatures.

The system implements RSA-3072, RSA-PSS, and SHA-256 to generate and verify digital signatures. It supports both document-based and text-based signing workflows.

AuthMark performs its core cryptographic operations locally without depending on external cryptographic services.

---

## Features

### 1. RSA Key Management
- Generate RSA-3072 public and private key pairs.
- Encrypt private keys using password-based encryption.
- Export private keys in encrypted PKCS#8 PEM format.
- Export public keys in PEM format.

### 2. Document Signing
- Upload an original document.
- Load an encrypted private key using its password.
- Generate a detached digital signature.
- Download the signature separately as a `.sig` file.
- Preserve the original document without modification.

### 3. Document Verification
- Upload the original document.
- Provide its corresponding detached signature.
- Supply the associated public key.
- Verify the cryptographic signature.
- Identify invalid signatures and modified documents.

### 4. Text Signing and Verification
- Sign UTF-8 text messages.
- Generate downloadable detached signatures.
- Verify text signatures using the corresponding public key.

### 5. Security-Oriented Design
- Local cryptographic processing.
- Encrypted private-key serialization.
- Input validation and exception handling.
- File upload restriction of 100 MiB.
- Separation of cryptographic operations from the user interface.

---

## Cryptographic Specifications

| Component | Implementation |
|---|---|
| Asymmetric Algorithm | RSA |
| RSA Key Size | 3072 bits |
| Public Exponent | 65537 |
| Signature Scheme | RSA-PSS |
| Mask Generation Function | MGF1 |
| Hash Algorithm | SHA-256 |
| PSS Salt Length | Maximum permitted |
| Private Key Format | Encrypted PKCS#8 PEM |
| Public Key Format | SubjectPublicKeyInfo PEM |
| Signature Type | Detached Digital Signature |

### Digital Signing Workflow

1. The user selects a document and provides an encrypted private key.
2. AuthMark reads the original document bytes.
3. SHA-256 is used as the message digest algorithm.
4. RSA-PSS generates a digital signature using the private key.
5. The signature is provided as a separate downloadable `.sig` file.

### Digital Verification Workflow

1. The verifier supplies the original document, detached signature, and public key.
2. AuthMark processes the supplied document bytes.
3. The verification process checks the RSA-PSS signature using SHA-256.
4. The application reports whether the signature is valid or invalid.

**Important:** Digital signatures do not encrypt documents. A valid signature confirms that the supplied signature matches the supplied content and public key. It does not independently establish the real-world identity of the key owner. Public keys must be authenticated through a trusted distribution mechanism.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| PyCA Cryptography | Cryptographic operations |
| Streamlit | Web application interface |
| Pytest | Automated testing |
| Git | Version control |
| GitHub | Source code hosting |

---

## Project Structure

```text
AuthMark/
│
├── .streamlit/
│   └── config.toml
│
├── data/
├── docs/
├── keys/
├── signatures/
│
├── src/
│   ├── crypto/
│   │   ├── key_manager.py
│   │   ├── signer.py
│   │   └── verifier.py
│   │
│   ├── file_handler/
│   │   ├── file_signer.py
│   │   └── file_verifier.py
│   │
│   ├── ui/
│   │   ├── components.py
│   │   ├── dashboard.py
│   │   ├── document_signing.py
│   │   ├── document_verification.py
│   │   ├── key_management.py
│   │   └── text_signing.py
│   │
│   └── main.py
│
├── tests/
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Installation and Setup

### Prerequisites

- Python 3.10 or later.
- Git.
- A terminal or command-line interface.

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/authmark-digital-signature-system.git
```

Navigate into the project directory:

```bash
cd authmark-digital-signature-system
```

### 2. Create a Virtual Environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Launch AuthMark

From the project root, execute:

```powershell
$env:PYTHONPATH = (Get-Location).Path
streamlit run src/main.py
```

The application will be accessible locally at:

```text
http://localhost:8501
```

---

## Running Tests

AuthMark uses Pytest for automated testing.

Execute the complete test suite from the project root:

```bash
python -m pytest -q
```

### Test Results

**57 automated tests passed.**

The test suite covers the application's cryptographic and file-handling functionality, including key management, signing, verification, and error handling.

---

## Security Considerations

AuthMark follows several security-oriented implementation practices:

- Private keys are encrypted before being exported.
- Private-key passwords are not displayed in the interface.
- Digital signatures are generated using RSA-PSS and SHA-256.
- Original document bytes are used for signing and verification.
- Detached signatures are stored separately from their source documents.
- File uploads are subject to a 100 MiB size restriction.
- Invalid signatures are handled without treating them as successful verification.

### Limitations

- A valid signature alone does not establish the real-world identity of the signer.
- Public-key authenticity depends on a trusted key-distribution mechanism.
- Private-key security also depends on password strength and secure storage.
- The application does not encrypt the original document.
- The system does not currently implement Certificate Authority-based identity verification.

---

## Future Scope

Potential improvements include:

- Digital certificate integration and public-key identity validation.
- Certificate Authority (CA) support.
- Certificate-based trust verification.
- Expanded audit logging and verification history.
- Support for additional cryptographic algorithms and signature formats.
- Improved deployment and application scalability.

---

## Project Information

| Attribute | Details |
|---|---|
| Project Name | AuthMark |
| Full Title | Digital Signature and Verification System |
| Domain | Cryptography and Cybersecurity |
| Primary Focus | Digital Signatures, Data Integrity, and Authenticity |
| Programming Language | Python |
| Interface Framework | Streamlit |
| Testing Framework | Pytest |

---

## Disclaimer

AuthMark is an educational and demonstration project developed to explore public-key cryptography and digital signature verification.

It is not intended to replace a fully audited enterprise digital-signature infrastructure or a legally compliant electronic-signature platform.

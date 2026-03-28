# 🔐 infra-core-sdk

[![PyPI version](https://img.shields.io/pypi/v/infra-core-sdk.svg)](https://pypi.org/project/infra-core-sdk/)
[![Python](https://img.shields.io/pypi/pyversions/infra-core-sdk.svg)](https://pypi.org/project/infra-core-sdk/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Secure, extensible, and production-ready credential management SDK for Python.

---

## 🚀 Why this exists

Managing credentials securely is hard.

This SDK solves:

- ❌ Scattered secrets across projects  
- ❌ Manual encryption handling  
- ❌ Inconsistent file structures  
- ❌ Hardcoded paths  

👉 With a **consistent, secure and extensible system**

---

## 🚀 Features

- 🔐 Automatic encryption (Fernet)
- 📦 Multiple credential profiles (`name`)
- ⚙️ Decoupled setup and load flows
- 📁 Dynamic path configuration
- 🧠 Smart dependency resolution
- 🧩 Extensible architecture

---

## 📦 Installation

```bash
pip install infra-core-sdk
```

---

## 🧩 Quick Start

```python
from dataclasses import dataclass
from infra_core import BaseCredentials, FernetEncryption, CredentialsLoader
from infra_core.credentials.setup.credentials_setup_service import CredentialsSetupService

@dataclass(frozen=True)
class MyCredentials(BaseCredentials):
    api_token: str

# Setup
setup = CredentialsSetupService(FernetEncryption)
setup.setup(MyCredentials(api_token="123"), name="default")

# Load
creds = CredentialsLoader.load(MyCredentials, FernetEncryption, name="default")

print(creds.api_token)
```

---

## 📁 Generated Structure

```text
project/
└── secret/
    ├── secret.key
    └── default.json
```

---

## ⚙️ Path Configuration (Power Feature)

```python
from infra_core import PathConfig

config = PathConfig.getDefault()

config = config.addDirectory("logs", "logs")
config = config.updateDirectory("downloads", "downloads_v2")
config = config.updateDirectory("secret_dir", "new_secret")

print(config.directories)
```

---

## 🧠 Behavior Model

| Type | Control |
|------|--------|
| secret_dir | user |
| secret_key | derived |
| credentials | derived |
| downloads | user |
| custom dirs | user |

---

## 🔁 Dependency Example

```python
config = config.updateDirectory("secret_dir", "new_secret")
```

```text
secret_key -> new_secret/secret.key
credentials -> new_secret/{name}.json
```

---

## ✋ Override Example

```python
config = config.updateDirectory("secret_key", "custom.key")
```

✔ stops automatic updates

---

## 🧪 Real Usage Pattern

```python
config = PathConfig.getDefault()

config = config.addDirectory("logs", "logs")
config = config.updateDirectory("downloads", "downloads_v2")
config = config.updateDirectory("secret_dir", "new_secret")
```

---

## 🔐 Encryption

Default:

```python
from infra_core import FernetEncryption
```

Custom:

```python
class CustomEncryption:
    def encrypt(self, value: str) -> str: ...
    def decrypt(self, value: str) -> str: ...
```

---

## ⚠️ Important Rules

❌ Do NOT manage keys manually  
✅ Let the SDK handle encryption lifecycle  

---

## 🧪 Development

```bash
pip install -e .[dev]
pytest
mypy src/
```

---

## 📄 License

MIT

---

## 👨‍💻 Author

Rafael Cavalcante

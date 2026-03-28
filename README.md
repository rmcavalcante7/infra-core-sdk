# 🔐 infra-core-sdk

Secure and extensible credential management SDK for Python applications.

---

## 🚀 Features

* 🔐 Automatic encryption (Fernet)
* 📦 Multiple credential support (`name`)
* ⚙️ Decoupled setup and load flows
* 📁 Automatic path management
* 🧩 Modular and extensible architecture

---

## 📦 Installation

```bash
pip install infra-core-sdk
```

---

## 🧩 Usage

### 🔹 Define your credentials model

```python
from dataclasses import dataclass
from infra_core import BaseCredentials

@dataclass(frozen=True)
class MyCreds(BaseCredentials):
    api_token: str
```

---

### 🔹 Save credentials (setup)

```python
from infra_core import FernetEncryption
from infra_core.credentials.setup.credentials_setup_service import CredentialsSetupService

setup = CredentialsSetupService(FernetEncryption)

setup.setup(
    MyCreds(api_token="123"),
    name="pipefy"
)
```

---

### 🔹 Load credentials

```python
from infra_core import CredentialsLoader, FernetEncryption

creds = CredentialsLoader.load(
    MyCreds,
    FernetEncryption,
    name="pipefy"
)

print(creds.api_token)
```

---

## 📁 Generated structure

```text
your_project/
├── secret/
│   ├── secret.key
│   ├── pipefy.json
```

---

## 🔄 Multiple credentials

```python
setup.setup(..., name="aws")
setup.setup(..., name="stripe")
```

---

## 🔐 Encryption

### Default

```python
from infra_core import FernetEncryption
```

---

### Custom implementation

```python
class CustomEncryption:
    def encrypt(self, value: str) -> str:
        ...

    def decrypt(self, value: str) -> str:
        ...
```

---

## ⚠️ Important rules

### ❌ Do NOT manually create keys

```python
Fernet.generate_key()
FernetEncryption(key)
```

---

### ✅ Let the SDK manage it

```python
CredentialsSetupService(FernetEncryption)
```

---

## 🧠 How it works

```text
SETUP:
    → generates key
    → encrypts data
    → saves file

LOAD:
    → reads key
    → decrypts data
    → returns typed object
```

---

## 🧪 Development

```bash
pip install -e .[dev]
pytest
```

---

## 📄 License

MIT

---

## 👨‍💻 Author

Rafael Cavalcante

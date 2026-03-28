# 🔐 infra-core-sdk

[![PyPI version](https://img.shields.io/pypi/v/infra-core-sdk.svg)](https://pypi.org/project/infra-core-sdk/)
[![Python](https://img.shields.io/pypi/pyversions/infra-core-sdk.svg)](https://pypi.org/project/infra-core-sdk/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)


---

## 🚀 Features

* 🔐 Automatic encryption (Fernet)
* 📦 Multiple credential support (`name`)
* ⚙️ Decoupled setup and load flows
* 📁 Automatic path management
* 🧠 Dynamic path configuration (PathConfig)
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
    MyCreds(api_token="1234"),
    name="system1"
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

# ⚙️ Path Configuration (Advanced)

The SDK provides a powerful and dynamic configuration system via `PathConfig`.

---

## 🔧 Basic usage

```python
from infra_core import PathConfig

config = PathConfig.getDefault()

print(config.root_markers)
print(config.directories)
```

---

## ➕ Add custom directory

```python
config = config.addDirectory("logs", "logs")
print(config.directories)
```

---

## 🔄 Update directories

```python
config = config.updateDirectory(config.downloadKey, "new_downloads")
print(config.directories)
```

---

## 🔁 Dependency update (secret_dir)

```python
config = config.updateDirectory(config.secretDirKey, "new_secret")
print(config.directories)
```

Derived directories are automatically updated:

- secret_key
- credentials

---

## 🌱 Root marker management

```python
config = config.addRootMarker(".custom")
print(config.root_markers)

config = config.removeRootMarker(".custom")
print(config.root_markers)
```

---

## 🧪 Full example

```python
from infra_core import PathConfig

if __name__ == "__main__":
    config = PathConfig.getDefault()

    print(f"{config.root_markers=}")
    print(f"{config.directories=}")

    config = config.addDirectory("logs", "logs")
    print("After add dir:", config.directories)

    config = config.updateDirectory(config.downloadKey, "new_downloads")
    print("After update dir:", config.directories)

    config = config.updateDirectory(config.secretDirKey, "new_secret")
    print("After update dir:", config.directories)

    config = config.addRootMarker(".custom")
    print("After add root:", config.root_markers)

    config = config.removeRootMarker(".custom")
    print("After remove root:", config.root_markers)
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
mypy src/
```

---

## 📄 License

MIT

---

## 👨‍💻 Author

Rafael Cavalcante

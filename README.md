# 🔐 infra-core-sdk

[![PyPI version](https://img.shields.io/pypi/v/infra-core-sdk.svg)](https://pypi.org/project/infra-core-sdk/)
[![Python](https://img.shields.io/pypi/pyversions/infra-core-sdk.svg)](https://pypi.org/project/infra-core-sdk/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

# 🔐 infra-core-sdk

A production-ready SDK for:

* Root-aware path resolution
* Structured filesystem management
* Secure credential storage (encrypted)
* Pluggable encryption strategies

---

# 🚀 Why this SDK exists

Managing paths, environments, and secrets across projects is hard.

This SDK solves:

* ❌ Hardcoded paths
* ❌ Environment inconsistencies
* ❌ Unsafe credential storage
* ❌ Scattered filesystem logic

---

# ✨ Core Features

* 📍 **Root-aware path resolution**
* 📁 **Centralized path configuration**
* 🔐 **Encrypted credential storage**
* 🔄 **Multiple credential profiles**
* ⚙️ **Pluggable encryption system**
* 🧠 **Deterministic filesystem behavior**

---

# 📦 Installation

```bash
pip install infra-core-sdk
```

---

# 🧠 Core Concepts (MUST READ)

## 🔹 1. Root Resolution

The SDK determines your project root using markers:

```text
.git
pyproject.toml
requirements.txt
```

You can customize this.

---

## 🔹 2. Path System

Every path is defined using:

```python
PathDefinition(path: str, use_root: bool)
```

| Type             | Behavior                 |
| ---------------- | ------------------------ |
| `use_root=True`  | relative to project root |
| `use_root=False` | must be absolute         |

---

## 🔹 3. Credentials Flow

```text
SETUP:
  → generate key
  → encrypt data
  → store file

LOAD:
  → read key
  → decrypt data
  → return typed object
```

---

# 🚀 Complete Example (Recommended Starting Point)

This is the **canonical usage**:

```python
# See full version in casos_de_uso/setup.py
```

---

# 🧩 Step-by-Step Usage

---

## 1️⃣ Define your credentials model

```python
from dataclasses import dataclass
from infra_core.credentials.models.base_credentials import BaseCredentials

@dataclass(frozen=True)
class MyCredentials(BaseCredentials):
    api_token: str
```

---

## 2️⃣ Configure ROOT behavior

```python
from infra_core.core.root.root_config import RootConfig
from infra_core.core.root.root_config_provider import RootConfigProvider

config = RootConfig(
    markers=(
        ".git",
        "pyproject.toml",
    )
)

RootConfigProvider.set(config)
```

---

## 3️⃣ Configure Paths

```python
from infra_core.core.path.path_config import PathConfig
from infra_core.core.path.path_config_provider import PathConfigProvider
from infra_core.core.path.path_definition import PathDefinition
from pathlib import Path

config = PathConfig()

# ROOT-based paths
config = config.addPath("secrets", PathDefinition("secrets", use_root=True))
config = config.addPath("secret_key", PathDefinition("secrets/key.key", use_root=True))
config = config.addPath("credentials", PathDefinition("secrets/{name}.json", use_root=True))

# Absolute path example
absolute_logs = str(Path.cwd() / "logs/app")

config = config.addPath(
    "logs",
    PathDefinition(absolute_logs, use_root=False),
)

PathConfigProvider.set(config)
```

---

## 4️⃣ Setup credentials (ENCRYPT + SAVE)

```python
from infra_core import CredentialsSetupService
from infra_core.security.fernet_encryption import FernetEncryption

setup = CredentialsSetupService(FernetEncryption)

setup.setup(
    MyCredentials(api_token="123"),
    name="default",
)
```

---

## 5️⃣ Load credentials

```python
from infra_core import CredentialsLoader

creds = CredentialsLoader.load(
    MyCredentials,
    FernetEncryption,
    name="default",
)

print(creds.api_token)
```

---

# 📁 Generated Structure

```text
project_root/
├── secrets/
│   ├── key.key
│   ├── default.json
```

---

# 🔄 Multiple Credential Profiles

```python
setup.setup(..., name="aws")
setup.setup(..., name="stripe")
setup.setup(..., name="internal")
```

---

# 📍 Path Management (Advanced)

## Get resolved paths

```python
from infra_core import PathManager

manager = PathManager()

print(manager.getPath("secrets"))
print(manager.getPath("credentials", name="default"))
```

---

## Ensure directories exist

```python
manager.ensurePathExists("secrets")
```

---

## Delete files or directories

```python
manager.deletePath("credentials", name="default")
```

---

# 🧠 Root Customization

## Add / remove markers

```python
from infra_core.core.root.root_config import RootConfig
from infra_core.core.root.root_config_provider import RootConfigProvider

config = RootConfig(markers=(".git", "pyproject.toml"))
RootConfigProvider.set(config)
```

---

## Debug root resolution

```python
from infra_core.core.root.root_resolver import RootResolver

print(RootResolver().resolve())
```

---

# 🔐 Encryption

## Default (recommended)

```python
from infra_core.security.fernet_encryption import FernetEncryption
```

---

## Custom encryption

```python
class CustomEncryption:
    def encrypt(self, value: str) -> str:
        ...

    def decrypt(self, value: str) -> str:
        ...
```

---

# ⚠️ Important Rules

## ❌ Do NOT manually manage keys

```python
Fernet.generate_key()
```

---

## ✅ Always use setup service

```python
CredentialsSetupService(...)
```

---

## ❌ Do NOT use relative paths with use_root=False

```python
PathDefinition("logs", use_root=False)  # INVALID
```

---

## ✅ Use absolute paths

```python
PathDefinition(str(Path.cwd() / "logs"), use_root=False)
```

---

# 🧪 Development

```bash
pip install -e .[dev]
pytest
mypy src/
black .
```

---

# 🧠 Architecture Overview

```text
core/
  path/
  root/

credentials/
  service
  loader
  setup

security/
  encryption
```

---

# 📦 Build & Publish

```bash
python -m build
twine check dist/*
```

---

# 📄 License

MIT

---

# 👨‍💻 Author

Rafael Cavalcante

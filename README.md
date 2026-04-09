# infra-core-sdk

[![PyPI version](https://img.shields.io/pypi/v/infra-core-sdk.svg)](https://pypi.org/project/infra-core-sdk/)
[![Python](https://img.shields.io/pypi/pyversions/infra-core-sdk.svg)](https://pypi.org/project/infra-core-sdk/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

`infra-core-sdk` is a small infrastructure SDK for Python projects that need:

- predictable project root resolution
- centralized path configuration
- encrypted credential setup and loading
- typed, reusable runtime filesystem operations

Current published version: `0.2.1.post1`

---

## Why this SDK exists

Most internal Python projects eventually reinvent the same infrastructure code:

- hardcoded paths scattered across modules
- inconsistent root discovery between local runs, scripts, CI, and installed packages
- ad-hoc secret files and manual key handling
- duplicated filesystem setup logic

`infra-core-sdk` turns those concerns into explicit, reusable building blocks.

Instead of solving paths and credentials separately in every project, you define them once and consume them through a consistent API.

---

## What the SDK gives you

### Root-aware path resolution

Resolve paths relative to the real project root instead of relying on fragile `cwd` assumptions.

The SDK supports:

- marker-based root discovery
- explicit `start_path` configuration
- installed-package fallback for consumer scripts

### Centralized path management

Define your important paths once and resolve or create them anywhere in your codebase.

Typical examples:

- secrets directory
- key file
- credentials files
- logs
- cache directories
- external absolute paths

### Secure credentials flow

Store credentials as typed objects, encrypt them with Fernet, and load them back through a predictable setup/load flow.

### Better reuse across projects

This SDK is designed to be installed and consumed by other Python projects, not just used from inside this repository.

---

## Installation

Latest published version:

```bash
pip install infra-core-sdk==0.2.1.post1
```

Or install the latest available release:

```bash
pip install infra-core-sdk
```

---

## Quick Example

This is the simplest end-to-end flow:

```python
from dataclasses import dataclass

from infra_core import (
    CredentialsLoader,
    CredentialsSetupService,
    FernetEncryption,
    PathConfig,
    RootConfig,
    RootConfigProvider,
)
from infra_core.core.path.path_config_provider import PathConfigProvider
from infra_core.core.path.path_definition import PathDefinition
from infra_core.credentials.models.base_credentials import BaseCredentials


@dataclass(frozen=True)
class MyCredentials(BaseCredentials):
    api_token: str


RootConfigProvider.set(
    RootConfig(
        markers=(".git", "pyproject.toml"),
    )
)

path_config = PathConfig()
path_config = path_config.addPath("secrets", PathDefinition("secrets"))
path_config = path_config.addPath("secret_key", PathDefinition("secrets/key.key"))
path_config = path_config.addPath(
    "credentials",
    PathDefinition("secrets/{name}.json"),
)

PathConfigProvider.set(path_config)

setup = CredentialsSetupService(FernetEncryption)
setup.setup(MyCredentials(api_token="123"), name="default")

creds = CredentialsLoader.load(
    MyCredentials,
    FernetEncryption,
    name="default",
)

print(creds.api_token)
```

Generated structure:

```text
project_root/
├── secrets/
│   ├── key.key
│   └── default.json
```

If you want a runnable example from this repository, see:

- [example_simple_usage.py](/C:/Users/rafael.m.cavalcante/PycharmProjects/infra-core-sdk/example_simple_usage.py)
- [casos_de_uso/setup.py](/C:/Users/rafael.m.cavalcante/PycharmProjects/infra-core-sdk/casos_de_uso/setup.py)

---

## Core Concepts

### 1. Root resolution

The SDK resolves the consumer project's root using markers such as:

```text
.git
pyproject.toml
requirements.txt
```

You can also provide an explicit `start_path`:

```python
from pathlib import Path

from infra_core import RootConfig, RootConfigProvider

RootConfigProvider.set(
    RootConfig(
        markers=(".git", "pyproject.toml"),
        start_path=Path(__file__).resolve().parent,
    )
)
```

This is especially useful when your application may run from a different `cwd`.

### 2. Path definitions

Each path is registered as a `PathDefinition`:

```python
PathDefinition(path: str, use_root: bool = True)
```

Behavior:

| Mode | Meaning |
| --- | --- |
| `use_root=True` | path is relative to the resolved project root |
| `use_root=False` | path must be absolute |

Template variables are supported:

```python
PathDefinition("secrets/{name}.json")
```

### 3. Credentials lifecycle

The default flow is:

```text
SETUP
  -> ensure key exists
  -> encrypt typed credentials
  -> save encrypted file

LOAD
  -> try environment variables first
  -> fallback to encrypted file
  -> return typed credentials object
```

---

## Step-by-Step Usage

### 1. Define a credentials model

```python
from dataclasses import dataclass

from infra_core.credentials.models.base_credentials import BaseCredentials


@dataclass(frozen=True)
class MyCredentials(BaseCredentials):
    api_token: str
    client_id: str
```

### 2. Configure root behavior

```python
from infra_core import RootConfig, RootConfigProvider

RootConfigProvider.set(
    RootConfig(
        markers=(".git", "pyproject.toml"),
    )
)
```

### 3. Configure paths

```python
from pathlib import Path

from infra_core import PathConfig
from infra_core.core.path.path_config_provider import PathConfigProvider
from infra_core.core.path.path_definition import PathDefinition

config = PathConfig()

config = config.addPath("secrets", PathDefinition("secrets"))
config = config.addPath("secret_key", PathDefinition("secrets/key.key"))
config = config.addPath("credentials", PathDefinition("secrets/{name}.json"))

absolute_logs = str(Path.cwd() / "logs" / "app")
config = config.addPath(
    "logs",
    PathDefinition(absolute_logs, use_root=False),
)

PathConfigProvider.set(config)
```

### 4. Setup encrypted credentials

```python
from infra_core import CredentialsSetupService, FernetEncryption

setup = CredentialsSetupService(FernetEncryption)

setup.setup(
    MyCredentials(
        api_token="123",
        client_id="abc",
    ),
    name="default",
)
```

### 5. Load credentials

```python
from infra_core import CredentialsLoader, FernetEncryption

creds = CredentialsLoader.load(
    MyCredentials,
    FernetEncryption,
    name="default",
)

print(creds.api_token)
print(creds.client_id)
```

---

## Public API Highlights

Top-level imports currently supported:

```python
from infra_core import (
    CredentialsLoader,
    CredentialsService,
    CredentialsSetupService,
    FernetEncryption,
    PathConfig,
    PathManager,
    RootConfig,
    RootConfigProvider,
    RootResolver,
)
```

Useful subpackage imports:

```python
from infra_core.core.root import RootConfig, RootConfigProvider, RootResolver
from infra_core.exceptions import SDKError
from infra_core.credentials.exceptions import CredentialsError
```

---

## Path Management

Resolve paths:

```python
from infra_core import PathManager

manager = PathManager()

print(manager.getPath("secrets"))
print(manager.getPath("credentials", name="default"))
```

Ensure resources exist:

```python
manager.ensurePathExists("secrets")
manager.ensurePathExists(
    "credentials",
    variables={"name": "default"},
    is_file=True,
)
```

Delete files or directories:

```python
manager.deleteResource("credentials", name="default")
manager.deleteResource("secrets")
```

---

## Multiple Credential Profiles

The same key can be reused for multiple profiles:

```python
setup.setup(..., name="aws")
setup.setup(..., name="stripe")
setup.setup(..., name="internal")
```

Then load the profile you need:

```python
aws = CredentialsLoader.load(MyCredentials, FernetEncryption, name="aws")
```

---

## Custom Encryption

Fernet is the default recommendation:

```python
from infra_core import FernetEncryption
```

You can also inject a custom encryption class:

```python
class CustomEncryption:
    def __init__(self, key: bytes) -> None:
        self._key = key

    def encrypt(self, value: str) -> str:
        return value

    def decrypt(self, value: str) -> str:
        return value
```

Use it the same way:

```python
setup = CredentialsSetupService(CustomEncryption)
creds = CredentialsLoader.load(MyCredentials, CustomEncryption, name="default")
```

---

## Important Rules

Do not manually manage keys in your application flow.

Use:

```python
CredentialsSetupService(...)
```

Do not use relative paths with `use_root=False`.

Invalid:

```python
PathDefinition("logs", use_root=False)
```

Valid:

```python
from pathlib import Path

PathDefinition(str(Path.cwd() / "logs"), use_root=False)
```

---

## Development

```bash
pip install -e .[dev]
python -m pytest
python -m mypy src
python -m black .
python -m build
python -m twine check dist/*
```

---

## Architecture Overview

```text
infra_core/
  core/
    path/
    root/
  credentials/
    models/
    services/
    setup/
  exceptions/
  security/
```

Responsibility split:

- `core.root`: project root discovery
- `core.path`: path definitions, configuration, and runtime operations
- `credentials.models`: typed credential objects
- `credentials.services`: save/load flows
- `credentials.setup`: initial setup and key lifecycle
- `security`: encryption implementations

---

## License

MIT

---

## Author

Rafael Cavalcante

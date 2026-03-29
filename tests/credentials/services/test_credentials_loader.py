# ============================================================
# Dependencies:
# - pytest
# - pathlib
# - os
# ============================================================

import os
from pathlib import Path
import pytest
from dataclasses import dataclass

from infra_core.credentials.services.credentials_loader import CredentialsLoader
from infra_core.credentials.services.credentials_service import CredentialsService
from infra_core.credentials.models.base_credentials import BaseCredentials

from infra_core.core.path.path_definition import PathDefinition
from infra_core.core.path.path_config_provider import PathConfigProvider
from infra_core.core.path.path_manager import PathManager

# ============================================================
# Mocks
# ============================================================


class MockEncryption:
    def __init__(self, key: bytes = b""):
        self._key = key

    def encrypt(self, value: str) -> str:
        return value

    def decrypt(self, value: str) -> str:
        return value


@dataclass(frozen=True)
class ExampleCredentials(BaseCredentials):
    api_token: str


# ============================================================
# Fixtures
# ============================================================


@pytest.fixture(autouse=True)
def reset_env():
    os.environ.pop("API_TOKEN", None)
    yield
    os.environ.pop("API_TOKEN", None)


@pytest.fixture(autouse=True)
def reset_path_config():
    from infra_core.core.path.path_config import PathConfig

    PathConfigProvider.set(PathConfig())
    yield
    PathConfigProvider.set(PathConfig())


# ============================================================
# Helpers
# ============================================================
def setup_fake_root(tmp_path: Path):
    (tmp_path / ".git").mkdir()


def setup_paths():
    config = PathConfigProvider.get()

    config = config.addPath("secret_key", PathDefinition("secrets/key.key"))

    config = config.addPath("credentials", PathDefinition("secrets/{name}.json"))

    config = config.addPath("secrets", PathDefinition("secrets"))

    PathConfigProvider.set(config)


# ============================================================
# Tests
# ============================================================


def test_load_from_env():
    os.environ["API_TOKEN"] = "env_token"

    creds = CredentialsLoader.load(
        ExampleCredentials,
        MockEncryption,
        name="test",
    )

    assert creds.api_token == "env_token"


def test_load_from_file(tmp_path, monkeypatch):
    setup_paths()

    setup_fake_root(tmp_path)
    monkeypatch.chdir(tmp_path)

    manager = PathManager()

    manager.createPath("secret_key", is_file=True)
    manager.createPath("credentials", variables={"name": "test"}, is_file=True)

    key_path = manager.getPath("secret_key")
    key_path.write_bytes(b"key")

    file_path = manager.getPath("credentials", variables={"name": "test"})

    service = CredentialsService(MockEncryption(b"key"))
    service.saveEncryptedCredentials(
        ExampleCredentials(api_token="file_token"), file_path
    )

    creds = CredentialsLoader.load(
        ExampleCredentials,
        MockEncryption,
        name="test",
    )

    assert creds.api_token == "file_token"


def test_env_has_priority_over_file(tmp_path, monkeypatch):
    setup_paths()
    monkeypatch.chdir(tmp_path)

    os.environ["API_TOKEN"] = "env_token"

    creds = CredentialsLoader.load(
        ExampleCredentials,
        MockEncryption,
        name="test",
    )

    assert creds.api_token == "env_token"


def test_missing_file_and_env_raises(tmp_path, monkeypatch):
    setup_paths()
    monkeypatch.chdir(tmp_path)

    with pytest.raises(Exception):
        CredentialsLoader.load(
            ExampleCredentials,
            MockEncryption,
            name="test",
        )


def test_missing_key_file_raises(tmp_path, monkeypatch):
    setup_paths()

    setup_fake_root(tmp_path)
    monkeypatch.chdir(tmp_path)

    manager = PathManager()

    manager.createPath("credentials", variables={"name": "test"}, is_file=True)

    with pytest.raises(Exception):
        CredentialsLoader.load(
            ExampleCredentials,
            MockEncryption,
            name="test",
        )

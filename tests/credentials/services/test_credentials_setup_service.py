# ============================================================
# Dependencies:
# - pytest
# - pathlib
# - dataclasses
# ============================================================

import pytest
from dataclasses import dataclass

from infra_core.credentials.setup.credentials_setup_service import (
    CredentialsSetupService,
)
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


@pytest.fixture
def root_env(tmp_path, monkeypatch):
    # cria root válido
    (tmp_path / ".git").mkdir()
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture(autouse=True)
def reset_path_config():
    from infra_core.core.path.path_config import PathConfig

    PathConfigProvider.set(PathConfig())
    yield
    PathConfigProvider.set(PathConfig())


# ============================================================
# Helpers
# ============================================================


def setup_paths():
    config = PathConfigProvider.get()

    config = config.addPath("secrets", PathDefinition("secrets"))

    config = config.addPath("secret_key", PathDefinition("secrets/key.key"))

    config = config.addPath("credentials", PathDefinition("secrets/{name}.json"))

    PathConfigProvider.set(config)


# ============================================================
# Tests
# ============================================================


def test_setup_creates_key_and_credentials(root_env):
    setup_paths()

    service = CredentialsSetupService(MockEncryption)

    creds = ExampleCredentials(api_token="token")

    service.setup(creds, name="test")

    manager = PathManager()

    key_path = manager.getPath("secret_key")
    cred_path = manager.getPath("credentials", variables={"name": "test"})

    assert key_path.exists()
    assert cred_path.exists()


def test_setup_persists_valid_credentials(root_env):
    setup_paths()

    service = CredentialsSetupService(MockEncryption)

    creds = ExampleCredentials(api_token="token")

    service.setup(creds, name="test")

    manager = PathManager()

    file_path = manager.getPath("credentials", variables={"name": "test"})

    service_reader = CredentialsService(MockEncryption(b"key"))

    loaded = service_reader.loadEncryptedCredentials(file_path, ExampleCredentials)

    assert loaded.api_token == "token"


def test_setup_does_not_overwrite_existing(root_env):
    setup_paths()

    service = CredentialsSetupService(MockEncryption)

    creds = ExampleCredentials(api_token="token")

    service.setup(creds, name="test")

    with pytest.raises(Exception):
        service.setup(creds, name="test")


def test_setup_creates_directories(root_env):
    setup_paths()

    service = CredentialsSetupService(MockEncryption)

    creds = ExampleCredentials(api_token="token")

    service.setup(creds, name="test")

    manager = PathManager()

    secrets_dir = manager.getPath("secrets")

    assert secrets_dir.exists()
    assert secrets_dir.is_dir()


def test_setup_with_existing_key(root_env):
    setup_paths()

    manager = PathManager()

    # cria key manualmente
    manager.createPath("secret_key", is_file=True)
    key_path = manager.getPath("secret_key")
    key_path.write_bytes(b"existing-key")

    service = CredentialsSetupService(MockEncryption)

    creds = ExampleCredentials(api_token="token")

    service.setup(creds, name="test")

    # não deve sobrescrever key
    assert key_path.read_bytes() == b"existing-key"

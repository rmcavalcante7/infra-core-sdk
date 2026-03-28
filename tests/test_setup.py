# ============================================================
# Dependencies:
# - dataclasses
# - pathlib
# - os
# ============================================================

import os
from dataclasses import dataclass

from infra_core.credentials.setup.credentials_setup_service import (
    CredentialsSetupService,
)
from infra_core.credentials.services.credentials_loader import CredentialsLoader
from infra_core.credentials.models.base_credentials import BaseCredentials
from infra_core.core.path import PathManager, DEFAULT_PATH_CONFIG


class MockEncryption:
    """
    Mock encryption with reversible transformation.
    """

    def encrypt(self, value: str) -> str:
        return f"enc({value})"

    def decrypt(self, value: str) -> str:
        return value.replace("enc(", "").replace(")", "")


@dataclass(frozen=True)
class DummyCredentials(BaseCredentials):
    """
    Dummy credentials model for testing.
    """

    api_token: str
    client_id: str


# ============================================================
# Tests
# ============================================================


def test_full_setup_and_load_flow() -> None:
    """
    Validate full flow: setup → save → load.

    :raises AssertionError:
        When credentials are not correctly persisted and loaded
    """
    # 🔹 limpa ENV (força uso de arquivo)
    os.environ.pop("API_TOKEN", None)
    os.environ.pop("CLIENT_ID", None)

    manager = PathManager(DEFAULT_PATH_CONFIG)

    key_path = manager.getPath("secret_key")
    credentials_path = manager.getPath("credentials", name="test")

    # 🔹 garante ambiente limpo
    if key_path.exists():
        key_path.unlink()

    if credentials_path.exists():
        credentials_path.unlink()

    encryption = MockEncryption()

    setup_service = CredentialsSetupService(encryption)

    original = DummyCredentials(api_token="token123", client_id="client456")

    # 🔹 executa setup
    setup_service.setup(original, name="test")

    # 🔹 valida criação dos arquivos
    assert key_path.exists()
    assert credentials_path.exists()

    # 🔹 carrega via loader
    loaded = CredentialsLoader.load(DummyCredentials, encryption, name="test")

    assert loaded.api_token == "token123"
    assert loaded.client_id == "client456"

    # 🔹 cleanup
    key_path.unlink()
    credentials_path.unlink()

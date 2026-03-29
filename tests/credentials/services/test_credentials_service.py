# ============================================================
# Dependencies:
# - pytest
# - pathlib
# ============================================================

from pathlib import Path
import pytest
from dataclasses import dataclass

from infra_core.credentials.services.credentials_service import CredentialsService
from infra_core.credentials.models.base_credentials import BaseCredentials
from infra_core.credentials.credentials_exceptions import (
    CredentialsFileError,
    CredentialsSerializationError,
)

# ============================================================
# Mocks
# ============================================================


class MockEncryption:
    def encrypt(self, value: str) -> str:
        return f"enc({value})"

    def decrypt(self, value: str) -> str:
        return value.replace("enc(", "").replace(")", "")


@dataclass(frozen=True)
class ExampleCredentials(BaseCredentials):
    api_token: str
    client_id: str


# ============================================================
# Tests
# ============================================================


def test_save_and_load_credentials(tmp_path):
    service = CredentialsService(MockEncryption())

    file_path = tmp_path / "creds.json"

    creds = ExampleCredentials(api_token="token", client_id="client")

    # Save
    service.saveEncryptedCredentials(creds, file_path)

    assert file_path.exists()

    # Load
    loaded = service.loadEncryptedCredentials(file_path, ExampleCredentials)

    assert loaded == creds


def test_load_file_not_found(tmp_path):
    service = CredentialsService(MockEncryption())

    file_path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        service.loadEncryptedCredentials(file_path, ExampleCredentials)


def test_invalid_json(tmp_path):
    import json

    service = CredentialsService(MockEncryption())

    file_path = tmp_path / "creds.json"

    file_path.write_text("invalid json")

    with pytest.raises(json.JSONDecodeError):
        service.loadEncryptedCredentials(file_path, ExampleCredentials)


def test_encryption_is_applied(tmp_path):
    service = CredentialsService(MockEncryption())

    file_path = tmp_path / "creds.json"

    creds = ExampleCredentials(api_token="token", client_id="client")

    service.saveEncryptedCredentials(creds, file_path)

    content = file_path.read_text()

    assert "enc(" in content  # garante que passou pelo encrypt


def test_partial_data_fails(tmp_path):
    service = CredentialsService(MockEncryption())

    file_path = tmp_path / "creds.json"

    # JSON incompleto
    file_path.write_text('{"api_token": "token"}')

    with pytest.raises(Exception):
        service.loadEncryptedCredentials(file_path, ExampleCredentials)

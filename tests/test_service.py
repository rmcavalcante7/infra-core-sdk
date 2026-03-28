# ============================================================
# Dependencies:
# - pathlib
# - dataclasses
# ============================================================

from pathlib import Path
from dataclasses import dataclass

from infra_core.credentials.services.credentials_service import CredentialsService
from infra_core.credentials.models.base_credentials import BaseCredentials


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


def test_save_and_load_credentials() -> None:
    """
    Validate that credentials are correctly saved and loaded.

    :raises AssertionError:
        When saved and loaded data do not match
    """
    path = Path("temp_credentials.json")

    service = CredentialsService(MockEncryption())

    original = DummyCredentials(api_token="token123", client_id="client456")

    # Save
    service.saveEncryptedCredentials(original, path)

    assert path.exists()

    # Load
    loaded = service.loadEncryptedCredentials(path, DummyCredentials)

    assert loaded.api_token == "token123"
    assert loaded.client_id == "client456"

    # Cleanup
    path.unlink()


def test_file_not_found_should_raise() -> None:
    """
    Validate that loading from a non-existent file raises FileNotFoundError.

    :raises AssertionError:
        When exception is not raised
    """
    path = Path("non_existent.json")

    service = CredentialsService(MockEncryption())

    try:
        service.loadEncryptedCredentials(path, DummyCredentials)
    except FileNotFoundError:
        assert True
        return

    raise AssertionError("Expected FileNotFoundError was not raised")

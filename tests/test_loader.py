# ============================================================
# Dependencies:
# - os
# - dataclasses
# ============================================================

import os
from dataclasses import dataclass

from infra_core import CredentialsLoader, BaseCredentials
from infra_core.credentials.exceptions.credentials_exceptions import (
    CredentialsNotFoundError,
)

from unittest.mock import patch
from pathlib import Path


class MockEncryption:
    """
    Simple mock encryption for testing purposes.
    """

    def encrypt(self, value: str) -> str:
        return value

    def decrypt(self, value: str) -> str:
        return value


@dataclass(frozen=True)
class TestCredentials(BaseCredentials):
    """
    Test credentials model.
    """

    api_token: str


# ============================================================
# Tests
# ============================================================


def test_load_from_env_success() -> None:
    """
    Validate that credentials are loaded from environment variables.

    :raises AssertionError:
        When credentials are not correctly loaded from ENV
    """
    os.environ["API_TOKEN"] = "env_token"

    creds = CredentialsLoader.load(TestCredentials, MockEncryption(), name="test")

    assert creds.api_token == "env_token"

    # cleanup
    os.environ.pop("API_TOKEN", None)


def test_load_fallback_without_env_should_fail() -> None:
    os.environ.pop("API_TOKEN", None)

    with patch(
        "infra_core.credentials.services.credentials_loader.PathManager"
    ) as mock_pm:
        mock_instance = mock_pm.return_value

        # força caminhos inexistentes
        mock_instance.getPath.side_effect = [
            Path("fake_key.key"),
            Path("fake_creds.json"),
        ]

        try:
            CredentialsLoader.load(TestCredentials, MockEncryption(), name="test")
        except CredentialsNotFoundError:
            assert True
            return

        raise AssertionError("Expected CredentialsNotFoundError was not raised")

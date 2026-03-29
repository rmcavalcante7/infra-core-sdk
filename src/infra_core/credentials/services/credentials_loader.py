# ============================================================
# Dependencies:
# - os
# - pathlib
# - typing
# ============================================================

from __future__ import annotations

import os
from pathlib import Path
from typing import Type, TypeVar, Dict, Optional, Any

from infra_core.credentials.models.base_credentials import BaseCredentials
from infra_core.credentials.services.credentials_service import CredentialsService
from infra_core.credentials.credentials_exceptions import (
    CredentialsError,
    CredentialsNotFoundError,
    CredentialsValidationError,
)
from infra_core.core.path.path_manager import PathManager

T = TypeVar("T", bound=BaseCredentials)


class CredentialsLoader:
    """
    Generic credentials loader with multi-source resolution strategy.

    Resolution priority:
    1. Environment variables
    2. Encrypted file (via PathManager)

    This class:
    - Is schema-agnostic
    - Delegates filesystem resolution to PathManager
    - Supports encryption injection
    """

    # ============================================================
    # Public Methods
    # ============================================================

    @staticmethod
    def load(
        credentials_class: Type[T],
        encryption_service: Any,
        name: str,
    ) -> T:
        """
        Load credentials from ENV or encrypted file.

        :param credentials_class: Type[T] = Credentials model class
        :param encryption_service: Any = Encryption implementation or class
        :param name: str = Credentials identifier

        :return: T = Loaded credentials

        :raises CredentialsNotFoundError:
            When no valid source is found

        :raises CredentialsError:
            When unexpected failure occurs

        :example:
            >>> from dataclasses import dataclass
            >>> class DummyEnc:
            ...     def encrypt(self, v): return v
            ...     def decrypt(self, v): return v
            ...
            >>> @dataclass(frozen=True)
            ... class Dummy(BaseCredentials):
            ...     api_token: str
            ...
            >>> isinstance(Dummy, type)
            True
        """
        try:
            env_credentials = CredentialsLoader._loadFromEnv(credentials_class)

            if env_credentials is not None:
                return env_credentials

            return CredentialsLoader._loadFromFile(
                credentials_class,
                encryption_service,
                name,
            )

        except CredentialsError:
            raise

        except Exception as exc:
            raise CredentialsError(
                f"Class: {CredentialsLoader.__name__}\n"
                f"Method: load\n"
                f"Unexpected error: {exc}"
            ) from exc

    # ============================================================
    # Private Methods
    # ============================================================

    @staticmethod
    def _loadFromEnv(credentials_class: Type[T]) -> Optional[T]:
        """
        Load credentials from environment variables.

        :param credentials_class: Type[T]

        :return: Optional[T]

        :raises CredentialsValidationError:
        """
        try:
            field_names = credentials_class.__dataclass_fields__.keys()

            data: Dict[str, Optional[str]] = {
                field: os.getenv(field.upper()) for field in field_names
            }

            if all(data.values()):
                return credentials_class.fromDict(data)

            return None

        except CredentialsError:
            raise

        except Exception as exc:
            raise CredentialsValidationError(
                f"Class: {CredentialsLoader.__name__}\n"
                f"Method: _loadFromEnv\n"
                f"Error loading from ENV: {exc}"
            ) from exc

    @staticmethod
    def _loadFromFile(
        credentials_class: Type[T],
        encryption_service: Any,
        name: str,
    ) -> T:
        """
        Load credentials from encrypted file using PathManager.

        :param credentials_class: Type[T]
        :param encryption_service: Any
        :param name: str

        :return: T

        :raises CredentialsNotFoundError:
        :raises CredentialsError:
        """
        try:
            manager = PathManager()

            key_path: Path = manager.getPath("secret_key")

            credentials_path: Path = manager.getPath(
                "credentials",
                variables={"name": name},
            )

            if not key_path.exists():
                raise CredentialsNotFoundError(
                    f"Class: {CredentialsLoader.__name__}\n"
                    f"Method: _loadFromFile\n"
                    f"Key file not found: {key_path}"
                )

            if not credentials_path.exists():
                raise CredentialsNotFoundError(
                    f"Class: {CredentialsLoader.__name__}\n"
                    f"Method: _loadFromFile\n"
                    f"Credentials file not found: {credentials_path}"
                )

            key: bytes = key_path.read_bytes()

            if isinstance(encryption_service, type):
                try:
                    encryption = encryption_service(key)
                except Exception as exc:
                    raise CredentialsError(
                        f"Class: {CredentialsLoader.__name__}\n"
                        f"Method: _loadFromFile\n"
                        f"Error instantiating encryption: {exc}"
                    ) from exc
            else:
                encryption = encryption_service

            service = CredentialsService(encryption)

            return service.loadEncryptedCredentials(
                credentials_path,
                credentials_class,
            )

        except CredentialsError:
            raise

        except Exception as exc:
            raise CredentialsError(
                f"Class: {CredentialsLoader.__name__}\n"
                f"Method: _loadFromFile\n"
                f"Error loading from file: {exc}"
            ) from exc


# ============================================================
# Main (Full Integration Test with PathManager)
# ============================================================

if __name__ == "__main__":
    from dataclasses import dataclass
    from infra_core.core.path.path_definition import PathDefinition
    from infra_core.core.path.path_config_provider import PathConfigProvider

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

    try:
        # --------------------------------------------------------
        # CONFIG PATH SYSTEM
        # --------------------------------------------------------
        config = PathConfigProvider.get()

        config = config.addPath("secrets", PathDefinition("secrets"))

        config = config.addPath("secret_key", PathDefinition("secrets/key.key"))

        config = config.addPath("credentials", PathDefinition("secrets/{name}.json"))

        PathConfigProvider.set(config)

        manager = PathManager()

        # --------------------------------------------------------
        # CREATE STRUCTURE
        # --------------------------------------------------------
        manager.createPath("secret_key", is_file=True)

        manager.createPath("credentials", variables={"name": "test"}, is_file=True)

        key_path = manager.getPath("secret_key")
        key_path.write_bytes(b"dummy-key")

        # --------------------------------------------------------
        # TEST 1: ENV
        # --------------------------------------------------------
        print("\n=== ENV TEST ===")
        os.environ["API_TOKEN"] = "env_token"

        creds = CredentialsLoader.load(
            ExampleCredentials,
            MockEncryption,
            name="test",
        )
        print("ENV OK:", creds)

        os.environ.pop("API_TOKEN", None)

        # --------------------------------------------------------
        # TEST 2: FILE
        # --------------------------------------------------------
        print("\n=== FILE TEST ===")

        file_path = manager.getPath("credentials", variables={"name": "test"})

        service = CredentialsService(MockEncryption(b"dummy-key"))
        service.saveEncryptedCredentials(
            ExampleCredentials(api_token="file_token"), file_path
        )

        creds = CredentialsLoader.load(
            ExampleCredentials,
            MockEncryption,
            name="test",
        )

        print("FILE OK:", creds)

        # --------------------------------------------------------
        # CLEANUP
        # --------------------------------------------------------
        manager.deleteResource("credentials", variables={"name": "test"})
        manager.deleteResource("secret_key")
        manager.deleteResource("secrets")

    except Exception as error:
        print("ERROR:", error)

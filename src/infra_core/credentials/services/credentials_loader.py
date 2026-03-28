# ============================================================
# Dependencies:
# - os
# - pathlib
# - typing
# - inspect
# ============================================================

import os
from pathlib import Path
from typing import Type, TypeVar, Dict, Optional, Any

from infra_core.credentials.models.base_credentials import BaseCredentials
from infra_core.credentials.services.credentials_service import CredentialsService
from infra_core.credentials.exceptions.credentials_exceptions import (
    CredentialsError,
    CredentialsNotFoundError,
    CredentialsValidationError,
)
from infra_core.core.path import PathManager, DEFAULT_PATH_CONFIG

T = TypeVar("T", bound=BaseCredentials)


class CredentialsLoader:
    """
    Generic credentials loader with multi-source resolution strategy.

    This component is responsible for dynamically loading credentials using
    a prioritized resolution strategy:

    1. Environment variables (highest priority)
    2. Encrypted file fallback

    Key characteristics:
    - Schema-agnostic (works with any BaseCredentials implementation)
    - Fully decoupled from external configuration systems
    - Integrates with PathManager for filesystem resolution
    - Supports pluggable encryption via dependency injection

    Limitations:
    - Requires environment variables to be uppercase field names
    - File fallback requires both key and credentials file to exist
    """

    # ============================================================
    # Public Methods
    # ============================================================

    @staticmethod
    def load(credentials_class: Type[T], encryption_service: Any, name: str) -> T:
        """
        Load credentials using environment variables or encrypted file fallback.

        The method follows a deterministic resolution order:
        1. Attempts to construct credentials from environment variables
        2. Falls back to encrypted file loading if ENV is incomplete

        :param credentials_class: Type[T] = Credentials model class that extends BaseCredentials
        :param encryption_service: Any = Encryption implementation providing encrypt/decrypt methods
        :param name: str = Identifier of the credentials file (e.g., "aws", "pipefy")

        :return: T = Fully populated credentials instance

        :raises CredentialsNotFoundError:
            When neither environment variables nor files provide valid credentials

        :raises CredentialsError:
            When an unexpected error occurs during the loading process

        :example:
            >>> import os
            >>> from dataclasses import dataclass
            >>> from infra_core.credentials.models.base_credentials import BaseCredentials
            >>> from infra_core.credentials.services.credentials_loader import CredentialsLoader
            >>>
            >>> class DummyEncryption:
            ...     def encrypt(self, v): return v
            ...     def decrypt(self, v): return v
            ...
            >>> @dataclass(frozen=True)
            ... class DummyCreds(BaseCredentials):
            ...     api_token: str
            ...
            >>> os.environ["API_TOKEN"] = "test_token"
            >>> creds = CredentialsLoader.load(DummyCreds, DummyEncryption())
            >>> isinstance(creds, DummyCreds)
            True
        """
        try:

            # ====================================================
            # 1. TRY ENV
            # ====================================================
            env_credentials = CredentialsLoader._loadFromEnv(credentials_class)

            if env_credentials is not None:
                print("DEBUG: USING ENV")
                return env_credentials

            # ====================================================
            # 2. FALLBACK → FILE
            # ====================================================
            return CredentialsLoader._loadFromFile(
                credentials_class, encryption_service, name
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
        Attempt to construct credentials from environment variables.

        This method maps each field of the credentials model to an environment
        variable using the uppercase version of the field name.

        Example:
        - field: api_token → ENV: API_TOKEN

        :param credentials_class: Type[T] = Credentials model class

        :return: Optional[T] = Credentials instance if all fields are present, otherwise None

        :raises CredentialsValidationError:
            When data extraction or validation fails

        :example:
            >>> import os
            >>> from dataclasses import dataclass
            >>> from infra_core.credentials.models.base_credentials import BaseCredentials
            >>> from infra_core.credentials.services.credentials_loader import CredentialsLoader
            >>>
            >>> @dataclass(frozen=True)
            ... class DummyCreds(BaseCredentials):
            ...     api_token: str
            ...
            >>> os.environ["API_TOKEN"] = "abc"
            >>> creds = CredentialsLoader._loadFromEnv(DummyCreds)
            >>> isinstance(creds, DummyCreds)
            True
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
        credentials_class: Type[T], encryption_service: Type[Any], name: str
    ) -> T:
        """
        Load credentials from encrypted file storage.

        This method retrieves file paths using PathManager and performs:
        - Validation of required files existence
        - Encryption instantiation using the provided encryption class
        - Delegation to CredentialsService for decryption

        :param credentials_class: Type[T] = Credentials model class
        :param encryption_service: Type[Any] = Encryption class (must accept key: bytes in constructor)
        :param name: str = Identifier of the credentials file (e.g., "aws", "pipefy")

        :return: T = Decrypted credentials instance

        :raises CredentialsNotFoundError:
            When the key file or credentials file does not exist

        :raises CredentialsError:
            When file loading or decryption fails

        :example:
            >>> from dataclasses import dataclass
            >>> from infra_core.credentials.models.base_credentials import BaseCredentials
            >>>
            >>> @dataclass(frozen=True)
            ... class DummyCreds(BaseCredentials):
            ...     api_token: str
            ...
            >>> isinstance(DummyCreds, type)
            True
        """
        try:
            manager = PathManager(DEFAULT_PATH_CONFIG)

            key_path: Path = manager.getPath("secret_key")
            credentials_path: Path = manager.getPath("credentials", name)

            if not key_path.exists():
                raise CredentialsNotFoundError(f"Key file not found: {key_path}")

            if not credentials_path.exists():
                raise CredentialsNotFoundError(
                    f"Credentials file not found: {credentials_path}"
                )

            # ============================================================
            # 🔥 FIX PRINCIPAL: instanciar encryption corretamente
            # ============================================================

            key: bytes = key_path.read_bytes()

            if isinstance(encryption_service, type):
                # caso 1: classe → precisa instanciar com key
                try:
                    encryption = encryption_service(key)
                except Exception as exc:
                    raise CredentialsError(
                        f"Class: {CredentialsLoader.__name__}\n"
                        f"Method: _loadFromFile\n"
                        f"Error instantiating encryption service: {exc}"
                    ) from exc
            else:
                # caso 2: instância → usar direto (mock/test)
                encryption = encryption_service

            service = CredentialsService(encryption)

            return service.loadEncryptedCredentials(credentials_path, credentials_class)

        except CredentialsError:
            raise

        except Exception as exc:
            raise CredentialsError(
                f"Class: {CredentialsLoader.__name__}\n"
                f"Method: _loadFromFile\n"
                f"Error loading from file: {exc}"
            ) from exc


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":
    from dataclasses import dataclass

    class MockEncryption:
        def encrypt(self, value: str) -> str:
            return value

        def decrypt(self, value: str) -> str:
            return value

    @dataclass(frozen=True)
    class ExampleCredentials(BaseCredentials):
        api_token: str

    creds = CredentialsLoader.load(ExampleCredentials, MockEncryption(), name="test")

    print("Loaded:", creds)

# ============================================================
# Dependencies:
# - pathlib
# - typing
# - inspect
# ============================================================

from pathlib import Path

from infra_core.credentials.models.base_credentials import BaseCredentials
from infra_core.credentials.services.credentials_service import CredentialsService
from infra_core.core.path import PathManager, DEFAULT_PATH_CONFIG
from infra_core.credentials.setup.secret_key_service import SecretKeyService
from infra_core.credentials.exceptions.credentials_exceptions import CredentialsError
from typing import Any
from infra_core import PathConfig


class CredentialsSetupService:
    """
    Service responsible for initial credentials setup and persistence.

    This class orchestrates:
    - Encryption key generation (if not present)
    - Secure storage of credentials
    - Directory preparation

    Design considerations:
    - Does not perform encryption directly
    - Delegates encryption to injected service
    - Uses PathManager for filesystem abstraction
    - Ensures idempotent setup behavior
    """

    def __init__(self, encryption_service: Any) -> None:
        """
        Initialize the CredentialsSetupService.

        :param encryption_service: Any = Encryption implementation (must provide encrypt/decrypt)

        :raises CredentialsError:
            When initialization fails

        :example:
            >>> class DummyEncryption:
            ...     def encrypt(self, v): return v
            ...     def decrypt(self, v): return v
            ...
            >>> service = CredentialsSetupService(DummyEncryption())
            >>> isinstance(service, CredentialsSetupService)
            True
        """
        try:
            self._encryption_service = encryption_service

        except Exception as exc:
            raise CredentialsError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: __init__\n"
                f"Error initializing setup service: {exc}"
            ) from exc

    # ============================================================
    # Public Methods
    # ============================================================

    def setup(self, credentials: BaseCredentials, name: str) -> None:
        """
        Perform initial setup of encrypted credentials.

        This method:
        - Generates a key if it does not exist
        - Persists credentials securely using encryption
        - Ensures directory structure exists

        :param credentials: BaseCredentials = Credentials instance to persist
        :param name: str = Identifier for the credentials file (e.g., "aws", "pipefy")

        :raises CredentialsError:
            When setup process fails

        :raises OSError:
            When filesystem operations fail

        :example:
            >>> from dataclasses import dataclass
            >>> class DummyEncryption:
            ...     def encrypt(self, v): return v
            ...     def decrypt(self, v): return v
            ...
            >>> @dataclass(frozen=True)
            ... class DummyCreds(BaseCredentials):
            ...     api_token: str
            ...
            >>> service = CredentialsSetupService(DummyEncryption())
            >>> creds = DummyCreds(api_token="123")
            >>> service.setup(creds)
        """
        try:
            manager = PathManager(PathConfig.getDefault())
            key_path: Path = manager.getPath(PathConfig().secretKeyKey)
            credentials_path: Path = manager.getPath(PathConfig().credentialsDir, name)

            if credentials_path.exists():
                raise CredentialsError(
                    f"Class: {self.__class__.__name__}\n"
                    f"Method: setup\n"
                    f"Credentials already exist for name: {name}"
                )

            if not key_path.exists():
                key = SecretKeyService.generateKey()
                SecretKeyService.saveKey(key_path, key)

            key = SecretKeyService.loadKey(key_path)

            if isinstance(self._encryption_service, type):
                # caso 1: classe → instanciar com key
                try:
                    encryption = self._encryption_service(key)
                except Exception as exc:
                    raise CredentialsError(
                        f"Class: {self.__class__.__name__}\n"
                        f"Method: setup\n"
                        f"Error instantiating encryption service: {exc}"
                    ) from exc
            else:
                # caso 2: instância → tentar reconstruir com key
                try:
                    encryption = self._encryption_service.__class__(key)
                except TypeError:
                    # fallback para mocks sem key
                    encryption = self._encryption_service

            credentials_service = CredentialsService(encryption)

            credentials_service.saveEncryptedCredentials(credentials, credentials_path)

        except Exception as exc:
            raise CredentialsError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: setup\n"
                f"Error during credentials setup: {exc}"
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

    setup_service = CredentialsSetupService(MockEncryption())

    creds = ExampleCredentials(api_token="test")

    setup_service.setup(creds, name="test")

    print("Setup completed successfully.")

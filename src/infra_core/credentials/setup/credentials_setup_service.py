# ============================================================
# Dependencies:
# - pathlib
# - typing
# ============================================================

from __future__ import annotations

from pathlib import Path
from typing import Any

from infra_core.credentials.models.base_credentials import BaseCredentials
from infra_core.credentials.services.credentials_service import CredentialsService
from infra_core.credentials.setup.secret_key_service import SecretKeyService
from infra_core.credentials.credentials_exceptions import (
    CredentialsError,
)
from infra_core.core.path.path_manager import PathManager


class CredentialsSetupService:
    """
    Service responsible for initial credentials setup and persistence.

    Responsibilities:
    - Ensure encryption key exists
    - Persist encrypted credentials
    - Ensure required filesystem structure

    Design principles:
    - Uses PathManager for all filesystem resolution
    - Does not depend on legacy PathConfig
    - Idempotent regarding key creation
    - Fails fast if credentials already exist

    Expected path configuration keys:
    - "secret_key"
    - "credentials"
    """

    def __init__(self, encryption_service: Any) -> None:
        """
        Initialize the CredentialsSetupService.

        :param encryption_service: Any = Encryption implementation or class

        :return: None

        :raises CredentialsError:
            When initialization fails

        :example:
            >>> class Dummy:
            ...     def encrypt(self, v): return v
            ...     def decrypt(self, v): return v
            ...
            >>> service = CredentialsSetupService(Dummy())
            >>> isinstance(service, CredentialsSetupService)
            True
        """
        try:
            self._encryption_service: Any = encryption_service

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
        - Ensures secret key exists (creates if missing)
        - Validates that credentials do not already exist
        - Persists encrypted credentials

        :param credentials: BaseCredentials = Credentials instance
        :param name: str = Identifier for credentials (e.g., "aws")

        :return: None

        :raises CredentialsError:
            When setup fails

        :raises OSError:
            When filesystem operations fail

        :example:
            >>> from dataclasses import dataclass
            >>> class Dummy:
            ...     def encrypt(self, v): return v
            ...     def decrypt(self, v): return v
            ...
            >>> @dataclass(frozen=True)
            ... class DummyCreds(BaseCredentials):
            ...     api_token: str
            ...
            >>> service = CredentialsSetupService(Dummy())
            >>> creds = DummyCreds(api_token="123")
            >>> isinstance(service, CredentialsSetupService)
            True
        """
        try:
            manager = PathManager()

            # ----------------------------------------------------
            # Resolve paths
            # ----------------------------------------------------
            key_path: Path = manager.getPath("secret_key")

            credentials_path: Path = manager.getPath(
                "credentials",
                variables={"name": name},
            )

            # ----------------------------------------------------
            # Prevent overwrite
            # ----------------------------------------------------
            if credentials_path.exists():
                raise CredentialsError(
                    f"Class: {self.__class__.__name__}\n"
                    f"Method: setup\n"
                    f"Credentials already exist for name: {name}"
                )

            # ----------------------------------------------------
            # Ensure key exists
            # ----------------------------------------------------
            if not key_path.exists():
                manager.createPath("secret_key", is_file=True)

                key = SecretKeyService.generateKey()
                SecretKeyService.saveKey(key_path, key)

            key = SecretKeyService.loadKey(key_path)

            # ----------------------------------------------------
            # Prepare encryption
            # ----------------------------------------------------
            if isinstance(self._encryption_service, type):
                try:
                    encryption = self._encryption_service(key)
                except Exception as exc:
                    raise CredentialsError(
                        f"Class: {self.__class__.__name__}\n"
                        f"Method: setup\n"
                        f"Error instantiating encryption service: {exc}"
                    ) from exc
            else:
                try:
                    encryption = self._encryption_service.__class__(key)
                except TypeError:
                    encryption = self._encryption_service

            # ----------------------------------------------------
            # Persist credentials
            # ----------------------------------------------------
            manager.createPath(
                "credentials",
                variables={"name": name},
                is_file=True,
            )

            credentials_service = CredentialsService(encryption)

            credentials_service.saveEncryptedCredentials(
                credentials,
                credentials_path,
            )

        except CredentialsError:
            raise

        except Exception as exc:
            raise CredentialsError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: setup\n"
                f"Error during credentials setup: {exc}"
            ) from exc


# ============================================================
# Main (Full Integration Example)
# ============================================================

if __name__ == "__main__":
    from dataclasses import dataclass

    from infra_core.core.path.path_definition import PathDefinition
    from infra_core.core.path.path_config_provider import PathConfigProvider
    from infra_core.core.path.path_manager import PathManager

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
        # Configure paths
        # --------------------------------------------------------
        config = PathConfigProvider.get()

        config = config.addPath("secrets", PathDefinition("secrets"))

        config = config.addPath("secret_key", PathDefinition("secrets/key.key"))

        config = config.addPath("credentials", PathDefinition("secrets/{name}.json"))

        PathConfigProvider.set(config)

        manager = PathManager()

        print("ROOT:", manager.getRoot())

        # --------------------------------------------------------
        # Setup credentials
        # --------------------------------------------------------
        service = CredentialsSetupService(MockEncryption)

        creds = ExampleCredentials(api_token="my_token")

        print("\n=== SETUP ===")
        service.setup(creds, name="test")
        print("Setup completed")

        # --------------------------------------------------------
        # Validate results
        # --------------------------------------------------------
        key_path = manager.getPath("secret_key")
        credentials_path = manager.getPath("credentials", variables={"name": "test"})

        print("\n=== VALIDATION ===")
        print("Key exists:", key_path.exists())
        print("Credentials exists:", credentials_path.exists())

        # --------------------------------------------------------
        # Re-run should fail
        # --------------------------------------------------------
        print("\n=== DUPLICATE TEST ===")
        try:
            service.setup(creds, name="test")
        except Exception as err:
            print("Expected error:", err)

        # --------------------------------------------------------
        # Cleanup
        # --------------------------------------------------------
        print("\n=== CLEANUP ===")

        manager.deleteResource("credentials", variables={"name": "test"})
        manager.deleteResource("secret_key")
        manager.deleteResource("secrets")

        print("Cleanup done")

    except Exception as error:
        print("Unexpected error:", error)

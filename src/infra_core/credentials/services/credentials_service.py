# ============================================================
# Dependencies:
# - json
# - pathlib
# - typing
# ============================================================

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Type, TypeVar, Protocol, runtime_checkable

from infra_core.credentials.models.base_credentials import BaseCredentials
from infra_core.credentials.credentials_exceptions import (
    CredentialsError,
    CredentialsSerializationError,
)

T = TypeVar("T", bound=BaseCredentials)


@runtime_checkable
class EncryptionProtocol(Protocol):
    """
    Contract for encryption services.

    Any implementation must provide:
    - encrypt
    - decrypt

    :example:
        >>> class Dummy:
        ...     def encrypt(self, v): return v
        ...     def decrypt(self, v): return v
        ...
        >>> d = Dummy()
        >>> hasattr(d, "encrypt") and hasattr(d, "decrypt")
        True
    """

    def encrypt(self, value: str) -> str: ...
    def decrypt(self, value: str) -> str: ...


class CredentialsService:
    """
    Service responsible for encryption and persistence of credentials.

    Responsibilities:
    - Encrypt before saving
    - Decrypt after loading
    - Ensure data integrity

    Important:
    - Does NOT resolve paths
    - Does NOT manage configuration
    """

    def __init__(self, encryption_service: EncryptionProtocol) -> None:
        """
        Initialize service.

        :param encryption_service: EncryptionProtocol = Encryption implementation

        :return: None

        :raises CredentialsError:
            When initialization fails

        :example:
            >>> class Dummy:
            ...     def encrypt(self, v): return v
            ...     def decrypt(self, v): return v
            ...
            >>> service = CredentialsService(Dummy())
            >>> isinstance(service, CredentialsService)
            True
        """
        try:
            self._encryption_service: EncryptionProtocol = encryption_service

        except Exception as exc:
            raise CredentialsError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: __init__\n"
                f"Error initializing service: {exc}"
            ) from exc

    # ============================================================
    # Public Methods
    # ============================================================

    def loadEncryptedCredentials(
        self,
        file_path: Path,
        credentials_class: Type[T],
    ) -> T:
        """
        Load and decrypt credentials from file.

        :param file_path: Path = File path
        :param credentials_class: Type[T] = Credentials class

        :return: T = Decrypted credentials

        :raises FileNotFoundError:
        :raises json.JSONDecodeError:
        :raises CredentialsSerializationError:

        :example:
            >>> from pathlib import Path
            >>> from dataclasses import dataclass
            >>> class Dummy:
            ...     def encrypt(self, v): return v
            ...     def decrypt(self, v): return v
            ...
            >>> @dataclass(frozen=True)
            ... class C(BaseCredentials):
            ...     api_token: str
            ...
            >>> path = Path("tmp.json")
            >>> path.write_text('{"api_token": "123"}')
            20
            >>> service = CredentialsService(Dummy())
            >>> isinstance(service.loadEncryptedCredentials(path, C), C)
            True
            >>> path.unlink()
        """
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"Credentials file not found: {file_path}")

            with open(file_path, "r", encoding="utf-8") as file:
                data: Dict[str, str] = json.load(file)

            decrypted_data: Dict[str, str] = {
                key: self._encryption_service.decrypt(value)
                for key, value in data.items()
            }

            return credentials_class.fromDict(decrypted_data)

        except FileNotFoundError, json.JSONDecodeError:
            raise

        except Exception as exc:
            raise CredentialsSerializationError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: loadEncryptedCredentials\n"
                f"Error loading credentials: {exc}"
            ) from exc

    def saveEncryptedCredentials(
        self,
        credentials: BaseCredentials,
        file_path: Path,
    ) -> None:
        """
        Encrypt and save credentials.

        :param credentials: BaseCredentials = Credentials instance
        :param file_path: Path = Destination path

        :return: None

        :raises OSError:
        :raises CredentialsSerializationError:

        :example:
            >>> from pathlib import Path
            >>> from dataclasses import dataclass
            >>> class Dummy:
            ...     def encrypt(self, v): return v
            ...     def decrypt(self, v): return v
            ...
            >>> @dataclass(frozen=True)
            ... class C(BaseCredentials):
            ...     api_token: str
            ...
            >>> service = CredentialsService(Dummy())
            >>> path = Path("tmp.json")
            >>> service.saveEncryptedCredentials(C("123"), path)
            >>> path.exists()
            True
            >>> path.unlink()
        """
        try:
            raw_data: Dict[str, str] = credentials.toDict()

            encrypted_data: Dict[str, str] = {
                key: self._encryption_service.encrypt(value)
                for key, value in raw_data.items()
            }

            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(encrypted_data, file, indent=4)

        except OSError:
            raise

        except Exception as exc:
            raise CredentialsSerializationError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: saveEncryptedCredentials\n"
                f"Error saving credentials: {exc}"
            ) from exc


# ============================================================
# Main (Integration Tests with PathManager + Config)
# ============================================================

if __name__ == "__main__":
    from dataclasses import dataclass
    from infra_core.core.path.path_manager import PathManager
    from infra_core.core.path.path_definition import PathDefinition
    from infra_core.core.path.path_config_provider import PathConfigProvider

    class MockEncryption:
        def encrypt(self, value: str) -> str:
            return f"enc({value})"

        def decrypt(self, value: str) -> str:
            return value.replace("enc(", "").replace(")", "")

    @dataclass(frozen=True)
    class ExampleCredentials(BaseCredentials):
        api_token: str
        client_id: str

    try:
        # --------------------------------------------------------
        # Setup PATH CONFIG (SDK way)
        # --------------------------------------------------------
        config = PathConfigProvider.get()

        config = config.addPath("secrets_dir", PathDefinition("secrets"))

        config = config.addPath(
            "credentials_file", PathDefinition("secrets/{name}.json")
        )

        PathConfigProvider.set(config)

        # --------------------------------------------------------
        # Initialize Manager
        # --------------------------------------------------------
        manager = PathManager()

        print("Resolved ROOT:", manager.getRoot())

        service = CredentialsService(MockEncryption())

        # --------------------------------------------------------
        # TEST 1: CREATE DIRECTORY (via manager)
        # --------------------------------------------------------
        print("\n=== TEST 1: CREATE DIRECTORY ===")

        secrets_dir = manager.createPath("secrets_dir")
        print("Directory created:", secrets_dir.exists())

        # --------------------------------------------------------
        # TEST 2: SAVE FILE (via resolved path)
        # --------------------------------------------------------
        print("\n=== TEST 2: SAVE ===")

        creds = ExampleCredentials(api_token="token", client_id="client")

        file_path = manager.getPath(
            "credentials_file", variables={"name": "test_credentials"}
        )

        service.saveEncryptedCredentials(creds, file_path)

        print("Saved OK:", file_path.exists())

        # --------------------------------------------------------
        # TEST 3: LOAD
        # --------------------------------------------------------
        print("\n=== TEST 3: LOAD ===")

        loaded = service.loadEncryptedCredentials(file_path, ExampleCredentials)

        print("Loaded OK:", loaded)

        # --------------------------------------------------------
        # TEST 4: FILE NOT FOUND
        # --------------------------------------------------------
        print("\n=== TEST 4: FILE NOT FOUND ===")

        try:
            missing_path = manager.getPath(
                "credentials_file", variables={"name": "not_exists"}
            )

            service.loadEncryptedCredentials(missing_path, ExampleCredentials)

        except Exception as err:
            print("Expected error:", err)

        # --------------------------------------------------------
        # TEST 5: INVALID JSON
        # --------------------------------------------------------
        print("\n=== TEST 5: INVALID JSON ===")

        file_path.write_text("invalid json")

        try:
            service.loadEncryptedCredentials(file_path, ExampleCredentials)
        except Exception as err:
            print("Expected JSON error:", err)

        # --------------------------------------------------------
        # CLEANUP (via manager)
        # --------------------------------------------------------
        print("\n=== CLEANUP ===")

        manager.deleteResource(
            "credentials_file", variables={"name": "test_credentials"}
        )

        manager.deleteResource("secrets_dir")

        print("Cleanup done")

    except Exception as error:
        print("Unexpected error:", error)

# ============================================================
# Dependencies:
# - json
# - pathlib
# - typing
# - inspect
# ============================================================

import json
from pathlib import Path
from typing import Dict, Type, TypeVar

from infra_core.credentials.models.base_credentials import BaseCredentials
from infra_core.credentials.exceptions.credentials_exceptions import (
    CredentialsError,
    CredentialsSerializationError,
)
from typing import Protocol

T = TypeVar("T", bound=BaseCredentials)


class EncryptionProtocol(Protocol):
    """
    Contract for encryption services.

    Any encryption implementation must provide:
    - encrypt
    - decrypt
    """

    def encrypt(self, value: str) -> str: ...

    def decrypt(self, value: str) -> str: ...


class CredentialsService:
    """
    Generic service responsible for secure persistence and retrieval
    of encrypted credentials.

    This service is schema-agnostic and operates on any credentials model
    that follows the BaseCredentials contract.

    Responsibilities:
    - Encrypt credentials before persistence
    - Decrypt credentials during retrieval
    - Maintain data integrity and consistency

    Design considerations:
    - Fully decoupled from credential structure
    - Uses dependency injection for encryption
    - Does not manage filesystem paths (delegated responsibility)
    """

    def __init__(self, encryption_service: EncryptionProtocol) -> None:
        """
        Initialize the CredentialsService.

        :param encryption_service: EncryptionProtocol = Encryption handler implementation

        :raises CredentialsError:
            When initialization fails

        :example:
            >>> class DummyEncryption:
            ...     def encrypt(self, v): return v
            ...     def decrypt(self, v): return v
            ...
            >>> service = CredentialsService(DummyEncryption())
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
        Load and decrypt credentials from a file.

        :param file_path: Path = Path to encrypted credentials file
        :param credentials_class: Type[T] = Credentials model class

        :return: T = Decrypted credentials instance

        :raises FileNotFoundError:
            When credentials file does not exist

        :raises json.JSONDecodeError:
            When file content is invalid JSON

        :raises CredentialsSerializationError:
            When decryption or parsing fails

        :example:
            >>> from pathlib import Path
            >>> from dataclasses import dataclass
            >>> from infra_core.credentials.models.base_credentials import BaseCredentials
            >>> from infra_core.credentials.services.credentials_service import CredentialsService
            >>>
            >>> class DummyEncryption:
            ...     def encrypt(self, v): return v
            ...     def decrypt(self, v): return v
            ...
            >>> @dataclass(frozen=True)
            ... class DummyCreds(BaseCredentials):
            ...     api_token: str
            ...
            >>> path = Path("temp.json")
            >>> path.write_text('{"api_token": "123"}') > 0
            True
            >>> service = CredentialsService(DummyEncryption())
            >>> creds = service.loadEncryptedCredentials(path, DummyCreds)
            >>> isinstance(creds, DummyCreds)
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
        Encrypt and persist credentials to a file.

        :param credentials: BaseCredentials = Credentials instance
        :param file_path: Path = Destination file path

        :raises OSError:
            When file cannot be written

        :raises CredentialsSerializationError:
            When encryption fails

        :example:
            >>> from pathlib import Path
            >>> from dataclasses import dataclass
            >>> class DummyEncryption:
            ...     def encrypt(self, v): return v
            ...     def decrypt(self, v): return v
            ...
            >>> @dataclass(frozen=True)
            ... class DummyCreds(BaseCredentials):
            ...     api_token: str
            ...
            >>> service = CredentialsService(DummyEncryption())
            >>> creds = DummyCreds(api_token="123")
            >>> path = Path("temp.json")
            >>> service.saveEncryptedCredentials(creds, path)
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
# Test
# ============================================================

if __name__ == "__main__":
    from dataclasses import dataclass

    class MockEncryption:
        def encrypt(self, value: str) -> str:
            return f"enc({value})"

        def decrypt(self, value: str) -> str:
            return value.replace("enc(", "").replace(")", "")

    @dataclass(frozen=True)
    class ExampleCredentials(BaseCredentials):
        api_token: str
        client_id: str

    service = CredentialsService(MockEncryption())

    path = Path("test_credentials.json")

    creds = ExampleCredentials(api_token="token", client_id="client")

    service.saveEncryptedCredentials(creds, path)

    loaded = service.loadEncryptedCredentials(path, ExampleCredentials)

    print("Loaded:", loaded)

    if path.exists():
        path.unlink()

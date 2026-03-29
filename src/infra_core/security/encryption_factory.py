# ============================================================
# Dependencies:
# - pathlib
# - typing
# - inspect
# ============================================================

from pathlib import Path
from typing import Protocol, Type, cast, Any

from infra_core.credentials.credentials_exceptions import CredentialsError


class EncryptionProtocol(Protocol):
    """
    Contract for encryption services.
    """

    def encrypt(self, value: str) -> str: ...

    def decrypt(self, value: str) -> str: ...


class EncryptionFactory:
    """
    Factory responsible for creating encryption instances based on a key.

    This abstracts the encryption instantiation logic and ensures
    that credentials loader does not need to know implementation details.
    """

    @staticmethod
    def create(key_path: Path, encryption_class: Type[Any]) -> EncryptionProtocol:
        """
        Create an encryption instance using a key from filesystem.

        :param key_path: Path = Path to encryption key file
        :param encryption_class: Type[EncryptionProtocol] = Encryption class to instantiate

        :return: EncryptionProtocol = Initialized encryption instance

        :raises CredentialsError:
            When key cannot be loaded or instance cannot be created

        :example:
            >>> from pathlib import Path
            >>> class DummyEncryption:
            ...     def __init__(self, key): pass
            ...     def encrypt(self, v): return v
            ...     def decrypt(self, v): return v
            ...
            >>> path = Path("temp.key")
            >>> bytes_written = path.write_bytes(b"123")
            >>> bytes_written > 0
            True
            >>> enc = EncryptionFactory.create(path, DummyEncryption)
            >>> hasattr(enc, "encrypt")
            True
            >>> path.unlink()
        """
        try:
            if not key_path.exists():
                raise FileNotFoundError(f"Key file not found: {key_path}")

            key = key_path.read_bytes()

            instance = encryption_class(key)
            return cast(EncryptionProtocol, instance)

        except Exception as exc:
            raise CredentialsError(
                f"Class: {EncryptionFactory.__name__}\n"
                f"Method: create\n"
                f"Error creating encryption instance: {exc}"
            ) from exc

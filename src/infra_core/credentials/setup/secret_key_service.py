# ============================================================
# Dependencies:
# - pathlib
# - os
# - inspect
# ============================================================

from pathlib import Path
from cryptography.fernet import Fernet


class SecretKeyService:
    """
    Service responsible for managing encryption keys used by the credentials system.

    This class handles:
    - Secure key generation
    - Persistent storage of encryption keys
    - Retrieval of existing keys

    Design considerations:
    - Stateless utility class
    - Does not depend on external services
    - Ensures directory creation before persistence
    - Keeps key management isolated from credential logic
    """

    # ============================================================
    # Public Methods
    # ============================================================

    @staticmethod
    def generateKey() -> bytes:
        """
        Generate a cryptographically secure random key.

        The generated key is suitable for symmetric encryption use cases.

        :return: bytes = Randomly generated encryption key

        :raises RuntimeError:
            When the operating system fails to provide randomness

        :example:
            >>> key = SecretKeyService.generateKey()
            >>> isinstance(key, bytes)
            True
        """
        try:
            return Fernet.generate_key()

        except Exception as exc:
            raise RuntimeError(
                f"Class: {SecretKeyService.__name__}\n"
                f"Method: generateKey\n"
                f"Error generating key: {exc}"
            ) from exc

    @staticmethod
    def saveKey(path: Path, key: bytes) -> None:
        """
        Persist an encryption key to the filesystem.

        This method ensures that the parent directory exists before writing the file.

        :param path: Path = Target file path for the key
        :param key: bytes = Encryption key to be persisted

        :raises OSError:
            When the file cannot be written

        :example:
            >>> from pathlib import Path
            >>> key = SecretKeyService.generateKey()
            >>> path = Path("temp_key.key")
            >>> SecretKeyService.saveKey(path, key)
            >>> path.exists()
            True
            >>> path.unlink()
        """
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(key)

        except Exception as exc:
            raise OSError(
                f"Class: {SecretKeyService.__name__}\n"
                f"Method: saveKey\n"
                f"Error saving key: {exc}"
            ) from exc

    @staticmethod
    def loadKey(path: Path) -> bytes:
        """
        Load an encryption key from the filesystem.

        :param path: Path = File path where the key is stored

        :return: bytes = Loaded encryption key

        :raises FileNotFoundError:
            When the key file does not exist

        :raises OSError:
            When the file cannot be read

        :example:
            >>> from pathlib import Path
            >>> key = SecretKeyService.generateKey()
            >>> path = Path("temp_key.key")
            >>> SecretKeyService.saveKey(path, key)
            >>> loaded = SecretKeyService.loadKey(path)
            >>> loaded == key
            True
            >>> path.unlink()
        """
        try:
            if not path.exists():
                raise FileNotFoundError(f"Key file not found: {path}")

            return path.read_bytes()

        except Exception as exc:
            raise OSError(
                f"Class: {SecretKeyService.__name__}\n"
                f"Method: loadKey\n"
                f"Error loading key: {exc}"
            ) from exc

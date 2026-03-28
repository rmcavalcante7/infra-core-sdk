# ============================================================
# Dependencies:
# - cryptography
# ============================================================

from cryptography.fernet import Fernet


class FernetEncryption:
    """
    Fernet-based encryption implementation.

    This class provides symmetric encryption using the Fernet standard,
    ensuring secure encryption and decryption of string-based credentials.

    Design considerations:
    - Stateless encryption wrapper around Fernet
    - Requires externally managed key (provided via constructor)
    - Compatible with CredentialsLoader and CredentialsService
    """

    # ============================================================
    # Constructor
    # ============================================================

    def __init__(self, key: bytes) -> None:
        """
        Initialize Fernet encryption instance.

        :param key: bytes = Fernet-compatible key (32 url-safe base64-encoded bytes)

        :raises ValueError:
            When the provided key is not valid for Fernet

        :raises TypeError:
            When the key is not of type bytes
        """
        try:
            if not isinstance(key, bytes):
                raise TypeError("Key must be of type bytes")

            self._fernet = Fernet(key)

        except Exception as exc:
            raise ValueError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: __init__\n"
                f"Invalid Fernet key: {exc}"
            ) from exc

    # ============================================================
    # Public Methods
    # ============================================================

    def encrypt(self, value: str) -> str:
        """
        Encrypt a plain text string.

        :param value: str = Plain text value to be encrypted

        :return: str = Encrypted value (base64 encoded string)

        :raises ValueError:
            When the input value is not a valid string

        :raises RuntimeError:
            When encryption fails
        """
        try:
            if not isinstance(value, str):
                raise ValueError("Value must be a string")

            encrypted: bytes = self._fernet.encrypt(value.encode())

            return encrypted.decode()

        except Exception as exc:
            raise RuntimeError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: encrypt\n"
                f"Error encrypting value: {exc}"
            ) from exc

    def decrypt(self, value: str) -> str:
        """
        Decrypt an encrypted string.

        :param value: str = Encrypted value (base64 encoded string)

        :return: str = Decrypted plain text value

        :raises ValueError:
            When the input value is not a valid string

        :raises RuntimeError:
            When decryption fails (e.g., invalid token or wrong key)
        """
        try:
            if not isinstance(value, str):
                raise ValueError("Value must be a string")

            decrypted: bytes = self._fernet.decrypt(value.encode())

            return decrypted.decode()

        except Exception as exc:
            raise RuntimeError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: decrypt\n"
                f"Error decrypting value: {exc}"
            ) from exc


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":
    key = Fernet.generate_key()

    encryption = FernetEncryption(key)

    original_value = "my-secret"

    encrypted_value = encryption.encrypt(original_value)
    decrypted_value = encryption.decrypt(encrypted_value)

    print("Original:", original_value)
    print("Encrypted:", encrypted_value)
    print("Decrypted:", decrypted_value)

# ============================================================
# Dependencies:
# - dataclasses
# - typing
# - inspect
# ============================================================

from dataclasses import dataclass, fields
from typing import Any, Dict, Type, TypeVar



from infra_core.credentials.exceptions.credentials_exceptions import (
    CredentialsValidationError,
    CredentialsSerializationError,
)

T = TypeVar("T", bound="BaseCredentials")

def getCurrentMethodName() -> str:
    import inspect

    frame = inspect.currentframe()
    if frame and frame.f_back:
        return frame.f_back.f_code.co_name
    return "unknown"


@dataclass(frozen=True)
class BaseCredentials:
    """
    Base dynamic credentials model.

    This class provides a reusable and extensible structure for handling
    credentials across different projects without coupling the system
    to a fixed schema.

    Responsibilities:
    - Validate required fields dynamically
    - Provide safe serialization/deserialization
    - Serve as base for all credential models

    Design:
    - Immutable (frozen=True)
    - No business logic
    - Extensible via inheritance

    :example:
        >>> @dataclass(frozen=True)
        ... class ApiCredentials(BaseCredentials):
        ...     api_token: str
        ...
        >>> creds = ApiCredentials(api_token="123")
        >>> data = creds.toDict()
        >>> data["api_token"]
        '123'
    """

    # ============================================================
    # Public Methods
    # ============================================================

    def toDict(self) -> Dict[str, Any]:
        """
        Convert credentials instance to dictionary.

        :return: Dict[str, Any] = Dictionary representation of credentials

        :raises CredentialsSerializationError:
            When conversion fails

        :example:
            >>> @dataclass(frozen=True)
            ... class ApiCredentials(BaseCredentials):
            ...     api_token: str
            ...
            >>> creds = ApiCredentials(api_token="123")
            >>> isinstance(creds.toDict(), dict)
            True
        """
        try:
            return {field.name: getattr(self, field.name) for field in fields(self)}

        except Exception as exc:
            raise CredentialsSerializationError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: {getCurrentMethodName()}\n"
                f"Error converting to dict: {str(exc)}"
            ) from exc

    @classmethod
    def fromDict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Create credentials instance from dictionary.

        :param data: Dict[str, Any] = Raw credential data
        :return: T = Instantiated credentials object

        :raises CredentialsValidationError:
            When required fields are missing

        :raises CredentialsSerializationError:
            When instantiation fails

        :example:
            >>> @dataclass(frozen=True)
            ... class ApiCredentials(BaseCredentials):
            ...     api_token: str
            ...
            >>> creds = ApiCredentials.fromDict({"api_token": "123"})
            >>> creds.api_token
            '123'
        """
        try:
            cls._validateInput(data)
            return cls(**data)

        except CredentialsValidationError:
            raise

        except Exception as exc:
            raise CredentialsSerializationError(
                f"Class: {cls.__name__}\n"
                f"Method: fromDict\n"
                f"Error creating instance: {str(exc)}"
            ) from exc

    # ============================================================
    # Validation Methods
    # ============================================================

    @classmethod
    def _validateInput(cls, data: Dict[str, Any]) -> None:
        """
        Validate input data against dataclass fields.

        :param data: Dict[str, Any] = Input data
        :return: None

        :raises CredentialsValidationError:
            When required fields are missing

        :example:
            >>> @dataclass(frozen=True)
            ... class ApiCredentials(BaseCredentials):
            ...     api_token: str
            ...
            >>> ApiCredentials._validateInput({"api_token": "123"})
        """
        try:
            required_fields = {field.name for field in fields(cls)}
            provided_fields = set(data.keys())

            missing_fields = required_fields - provided_fields

            if missing_fields:
                raise CredentialsValidationError(
                    f"Class: {cls.__name__}\n"
                    f"Method: _validateInput\n"
                    f"Missing fields: {missing_fields}"
                )

        except CredentialsValidationError:
            raise

        except Exception as exc:
            raise CredentialsValidationError(
                f"Class: {cls.__name__}\n"
                f"Method: _validateInput\n"
                f"Validation error: {str(exc)}"
            ) from exc


# ============================================================
# Concrete Implementation (Backward Compatible)
# You just have to create a new class with your user case
# ============================================================


@dataclass(frozen=True)
class PipefyCredentials(BaseCredentials):
    """
    Concrete credentials model for Pipefy authentication.

    This class preserves backward compatibility with the existing system
    while enabling future extensibility via BaseCredentials.

    Attributes:
        api_token (str): Pipefy API token

    :example:
        >>> creds = PipefyCredentials(api_token="123")
        >>> creds.api_token
        '123'
    """

    api_token: str


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":
    creds = PipefyCredentials(api_token="test_token")

    data = creds.toDict()
    print("Serialized:", data)

    new_creds = PipefyCredentials.fromDict(data)
    print("Deserialized:", new_creds.api_token)

# ============================================================
# Dependencies:
# - typing
# - inspect
# ============================================================

from __future__ import annotations

import inspect
from typing import Any, Dict, Optional


class SDKError(Exception):
    """
    Base exception for the entire SDK.

    This class standardizes error handling across all modules by providing:
    - Structured error context
    - Error codes for classification and observability
    - Automatic formatted error messages
    - Support for exception chaining

    All module-specific exceptions must inherit from this class.

    :param message: str = Human-readable error description
    :param code: Optional[str] = Unique error identifier
    :param context: Optional[Dict[str, Any]] = Structured context data
    :param original_exception: Optional[Exception] = Original exception instance

    :raises ValueError:
        When message is empty

    :example:
        >>> from infra_core.exceptions.base import SDKError
        >>> try:
        ...     raise SDKError(
        ...         message="Unexpected failure",
        ...         code="CORE_UNKNOWN",
        ...         context={"step": "initialization"}
        ...     )
        ... except SDKError:
        ...     True
        True
    """

    DEFAULT_CODE: str = "SDK_ERROR"

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ) -> None:
        """
        Initializes SDKError.

        :param message: str = Error description
        :param code: Optional[str] = Error code
        :param context: Optional[Dict[str, Any]] = Contextual data
        :param original_exception: Optional[Exception] = Original exception

        :raises ValueError:
            When message is empty

        :example:
            >>> from infra_core.exceptions.base import SDKError
            >>> err = SDKError("error occurred")
            >>> isinstance(err, SDKError)
            True
        """
        if not message:
            raise ValueError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: __init__\n"
                f"Error: message cannot be empty"
            )

        self.message: str = message
        self.code: str = code or self.DEFAULT_CODE
        self.context: Dict[str, Any] = context or {}
        self.original_exception: Optional[Exception] = original_exception

        formatted_message: str = self._buildErrorMessage()

        super().__init__(formatted_message)

    # ============================================================
    # Private Methods
    # ============================================================

    def _buildErrorMessage(self) -> str:
        """
        Builds a standardized error message.

        The message includes:
        - Class name
        - Method name
        - Error code
        - Error message
        - Structured context (if provided)

        :return: str = Formatted error message

        :example:
            >>> from infra_core.exceptions.base import SDKError
            >>> err = SDKError("test error")
            >>> isinstance(str(err), str)
            True
        """
        class_name: str = self.__class__.__name__
        method_name: str = self._getCallerMethod()

        context_str: str = self._formatContext()

        return (
            f"Class: {class_name}\n"
            f"Method: {method_name}\n"
            f"Code: {self.code}\n"
            f"Error: {self.message}"
            f"{context_str}"
        )

    def _getCallerMethod(self) -> str:
        """
        Retrieves the caller method name.

        This method inspects the call stack to determine the method
        where the exception was raised.

        :return: str = Caller method name

        :example:
            >>> from infra_core.exceptions.base import SDKError
            >>> err = SDKError("error")
            >>> isinstance(err._getCallerMethod(), str)
            True
        """
        frame = inspect.currentframe()

        if frame and frame.f_back and frame.f_back.f_back:
            return frame.f_back.f_back.f_code.co_name

        return "unknown"

    def _formatContext(self) -> str:
        """
        Formats context dictionary into a string.

        :return: str = Formatted context block

        :example:
            >>> from infra_core.exceptions.base import SDKError
            >>> err = SDKError("error", context={"a": 1})
            >>> "a=1" in err._formatContext()
            True
        """
        if not self.context:
            return ""

        context_lines: str = "\n".join(
            f"  {key}={value}" for key, value in self.context.items()
        )

        return f"\nContext:\n{context_lines}"

    # ============================================================
    # Public Methods
    # ============================================================

    def toDict(self) -> Dict[str, Any]:
        """
        Converts the exception into a dictionary.

        This is useful for:
        - Logging systems
        - API responses
        - Structured error handling

        :return: Dict[str, Any] = Dictionary representation of the error

        :example:
            >>> from infra_core.exceptions.base import SDKError
            >>> err = SDKError("error", code="X")
            >>> data = err.toDict()
            >>> data["code"]
            'X'
        """
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "code": self.code,
            "context": self.context,
        }


# ============================================================
# Main (Usage Example)
# ============================================================

if __name__ == "__main__":
    try:
        raise SDKError(
            message="Example error",
            code="EXAMPLE",
            context={"demo": True},
        )
    except SDKError as exc:
        print(str(exc))
        print(exc.toDict())

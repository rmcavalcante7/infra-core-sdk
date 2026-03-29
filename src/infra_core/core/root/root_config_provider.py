# ============================================================
# Dependencies:
# - typing
# ============================================================

from __future__ import annotations

from typing import Optional

from infra_core.core.root.root_config import RootConfig


class RootConfigProvider:
    """
    Global provider for RootConfig.

    This class is responsible for:
    - Maintaining the current root configuration
    - Allowing runtime updates
    - Providing global access to root configuration

    :example:
        >>> from infra_core.core.root.root_config_provider import RootConfigProvider
        >>> config = RootConfigProvider.get()
        >>> config is not None
        True
    """

    _config: Optional[RootConfig] = None

    # ============================================================
    # Public Methods
    # ============================================================

    @classmethod
    def get(cls) -> RootConfig:
        """
        Returns the current RootConfig.

        If no config is set, a default instance is created.

        :return: RootConfig = Current configuration

        :example:
            >>> from infra_core.core.root.root_config_provider import RootConfigProvider
            >>> config = RootConfigProvider.get()
            >>> isinstance(config, RootConfigProvider.get().__class__)
            True
        """
        if cls._config is None:
            cls._config = RootConfig()

        return cls._config

    @classmethod
    def set(cls, config: RootConfig) -> None:
        """
        Sets a new RootConfig.

        :param config: RootConfig = New configuration

        :return: None

        :example:
            >>> from infra_core.core.root.root_config_provider import RootConfigProvider
            >>> from infra_core.core.root.root_config import RootConfig
            >>> RootConfigProvider.set(RootConfig())
            >>> isinstance(RootConfigProvider.get(), RootConfig)
            True
        """
        cls._config = config

    @classmethod
    def reset(cls) -> None:
        """
        Resets the configuration to default.

        :return: None

        :example:
            >>> from infra_core.core.root.root_config_provider import RootConfigProvider
            >>> RootConfigProvider.reset()
            >>> config = RootConfigProvider.get()
            >>> config is not None
            True
        """
        cls._config = None


# ============================================================
# Main (Usage Example)
# ============================================================

if __name__ == "__main__":
    try:
        config = RootConfigProvider.get()
        print("Default config:", config.markers)

        new_config = config.addMarker(".env")
        RootConfigProvider.set(new_config)

        print("Updated config:", RootConfigProvider.get().markers)

        RootConfigProvider.reset()
        print("Reset config:", RootConfigProvider.get().markers)

    except Exception as error:
        print(error)

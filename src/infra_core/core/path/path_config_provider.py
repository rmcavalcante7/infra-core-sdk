# ============================================================
# Dependencies:
# - typing
# ============================================================

from typing import Optional

from infra_core.core.path.path_config import PathConfig


class PathConfigProvider:
    """
    Global provider for PathConfig.

    :example:
        >>> config = PathConfigProvider.get()
        >>> isinstance(config, PathConfig)
        True
    """

    _config: Optional[PathConfig] = None

    @classmethod
    def get(cls) -> PathConfig:
        """
        Returns current config.

        :return: PathConfig
        """
        if cls._config is None:
            cls._config = PathConfig()

        return cls._config

    @classmethod
    def set(cls, config: PathConfig) -> None:
        """
        Sets global config.

        :param config: PathConfig
        """
        cls._config = config

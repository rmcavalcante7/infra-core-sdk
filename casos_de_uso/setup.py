"""
Infra Core SDK - Complete Example (Advanced)

Demonstrates:

1. Root configuration (add/remove markers)
2. Path configuration (ROOT / ABSOLUTE)
3. Credentials setup
4. Credentials loading
5. Path resolution behavior

This is the official reference implementation.
"""

# ============================================================
# Dependencies
# ============================================================

from dataclasses import dataclass
from pathlib import Path

from infra_core import (
    CredentialsLoader,
    CredentialsSetupService,
    PathManager,
)

from infra_core.credentials.models.base_credentials import BaseCredentials
from infra_core.security.fernet_encryption import FernetEncryption

from infra_core.core.path.path_definition import PathDefinition
from infra_core.core.path.path_config_provider import PathConfigProvider
from infra_core.core.path.path_config import PathConfig

from infra_core.core.root.root_config import RootConfig
from infra_core.core.root.root_config_provider import RootConfigProvider
from infra_core.core.root.root_resolver import RootResolver


# ============================================================
# Credentials Models
# ============================================================

@dataclass(frozen=True)
class PipefyCredentials(BaseCredentials):
    api_token: str


@dataclass(frozen=True)
class SharepointCredentials(BaseCredentials):
    user: str
    password: str


# ============================================================
# Root Configuration
# ============================================================

def configureRoot() -> None:
    """
    Demonstrates how to customize root resolution.

    - Remove unwanted markers (e.g., setup.py)
    - Add custom markers if needed
    """

    print("\n=== ROOT CONFIGURATION ===")

    config = RootConfig(
        markers=(
            ".git",
            "pyproject.toml",
            # "setup.py",  # ❌ intentionally removed
        )
    )

    RootConfigProvider.set(config)

    resolver = RootResolver()
    root = resolver.resolve()

    print("Resolved root:", root)


# ============================================================
# Path Configuration
# ============================================================

def configurePaths() -> None:
    """
    Configure paths with:
    - ROOT-based
    - ABSOLUTE
    """

    print("\n=== PATH CONFIGURATION ===")

    config = PathConfig()

    # --------------------------------------------------------
    # ROOT-BASED
    # --------------------------------------------------------
    config = config.addPath(
        "secrets",
        PathDefinition("secrets", use_root=True),
    )

    config = config.addPath(
        "secret_key",
        PathDefinition("secrets/key.key", use_root=True),
    )

    config = config.addPath(
        "credentials",
        PathDefinition("secrets/{name}.json", use_root=True),
    )

    # --------------------------------------------------------
    # ABSOLUTE
    # --------------------------------------------------------
    absolute_path = str(Path.cwd() / "absolute/logs/app")

    config = config.addPath(
        "absolute_logs",
        PathDefinition(absolute_path, use_root=False),
    )

    PathConfigProvider.set(config)


# ============================================================
# Setup Credentials
# ============================================================

def setupCredentials() -> None:
    """
    Setup encrypted credentials.
    """

    print("\n=== SETUP CREDENTIALS ===")

    setup = CredentialsSetupService(FernetEncryption)

    setup.setup(PipefyCredentials(api_token="123"), name="pipefy")

    setup.setup(
        SharepointCredentials(user="user", password="password"),
        name="sharepoint",
    )


# ============================================================
# Load Credentials
# ============================================================

def loadCredentials() -> None:
    """
    Load credentials.
    """

    print("\n=== LOAD CREDENTIALS ===")

    pipefy = CredentialsLoader.load(
        PipefyCredentials,
        FernetEncryption,
        name="pipefy",
    )

    sharepoint = CredentialsLoader.load(
        SharepointCredentials,
        FernetEncryption,
        name="sharepoint",
    )

    print("Pipefy:", pipefy)
    print("Sharepoint:", sharepoint)


# ============================================================
# Path Demonstration
# ============================================================

def demonstratePaths() -> None:
    """
    Demonstrates resolved paths.
    """

    print("\n=== PATH RESOLUTION ===")

    manager = PathManager()

    print("\n--- ROOT ---")
    print("Secrets:", manager.getPath("secrets"))
    print("Key:", manager.getPath("secret_key"))
    print("Pipefy:", manager.getPath("credentials", name="pipefy"))

    print("\n--- ABSOLUTE ---")
    print("Absolute logs:", manager.getPath("absolute_logs"))


# ============================================================
# Ensure Paths
# ============================================================

def ensurePaths() -> None:
    """
    Ensure directories exist.
    """

    print("\n=== ENSURE PATHS ===")

    manager = PathManager()

    manager.ensurePathExists("secrets")
    manager.ensurePathExists("absolute_logs")

    print("Paths ensured.")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    try:
        print("=== Infra Core SDK - COMPLETE EXAMPLE ===")

        # 1. Root configuration (CRITICAL)
        configureRoot()

        # 2. Path configuration
        configurePaths()

        # 3. Ensure directories
        ensurePaths()

        # 4. Setup credentials
        setupCredentials()

        # 5. Show resolved paths
        demonstratePaths()

        # 6. Load credentials
        loadCredentials()

        print("\n=== DONE ===")

    except Exception as error:
        print("\n[ERROR]")
        print(error)



from dataclasses import dataclass

from infra_core import BaseCredentials, FernetEncryption, CredentialsLoader, PathConfig, path_exceptions, DEFAULT_PATH_CONFIG
from infra_core.credentials.setup.credentials_setup_service import (
    CredentialsSetupService,
)


@dataclass(frozen=True)
class MyPipefyCredentials(BaseCredentials):
    api_token: str

@dataclass(frozen=True)
class MySharepointCredentials(BaseCredentials):
    user: str
    password: str


import infra_core
print(infra_core.__file__)

# ============================================================
# Setup
# ============================================================
setup = CredentialsSetupService(FernetEncryption)

# ============================================================
# Happy Path
# ============================================================

print("\n=== HAPPY PATH ===")

setup.setup(MyPipefyCredentials(api_token="123"), name="pipefy")
setup.setup(MySharepointCredentials(user="abc", password="teste"), name="sharepoint")

pipefy = CredentialsLoader.load(MyPipefyCredentials, FernetEncryption, name="pipefy")
sharepoint = CredentialsLoader.load(MySharepointCredentials, FernetEncryption, name="sharepoint")

print(f"{pipefy=}")
print(f"{sharepoint=}")


# ============================================================
# Exception Tests - Directories
# ============================================================

print("\n=== DIRECTORY EXCEPTIONS ===")

config = PathConfig.getDefault()
print(f"{config.directories=}")
print(f"{config.root_markers=}")
# 1. DirectoryAlreadyExistsError
try:
    config.addDirectory(config.secretDirKey, "another_secret")
except path_exceptions.DirectoryAlreadyExistsError as exc:
    print("✔ DirectoryAlreadyExistsError OK:", exc)

# 2. DirectoryNotFoundError
try:
    config.updateDirectory("not_exists", "x")
except path_exceptions.DirectoryNotFoundError as exc:
    print("✔ DirectoryNotFoundError OK:", exc)

# 3. InvalidDirectoryPathError
try:
    config.updateDirectory(config.secretDirKey, "")
except path_exceptions.InvalidDirectoryPathError as exc:
    print("✔ InvalidDirectoryPathError OK:", exc)


# ============================================================
# Exception Tests - Root Markers
# ============================================================

print("\n=== ROOT MARKER EXCEPTIONS ===")

# 4. InvalidRootMarkerError
try:
    config.addRootMarker("")
except path_exceptions.InvalidRootMarkerError as exc:
    print("✔ InvalidRootMarkerError OK:", exc)

# 5. RootMarkerNotFoundError
try:
    config.removeRootMarker(".not_exists")
except path_exceptions.RootMarkerNotFoundError as exc:
    print("✔ RootMarkerNotFoundError OK:", exc)


# ============================================================
# Dependency Behavior Test
# ============================================================

print("\n=== DEPENDENCY TEST ===")

config = config.updateDirectory(config.secretDirKey, "new_secret")

print("Updated directories:")
for k, v in config.directories.items():
    print(f"{k} -> {v}")

print(f"{config.directories=}")
print(f"{DEFAULT_PATH_CONFIG.directories=}")

config = config.updateDirectory(config.downloadKey, "new_download")

print("Updated directories:")
for k, v in config.directories.items():
    print(f"{k} -> {v}")

print(f"{config.directories=}")
print(f"{config.removeRootMarker=}")
print(f"{DEFAULT_PATH_CONFIG.directories=}")


# ============================================================
# Integration Test (After Change)
# ============================================================

print("\n=== INTEGRATION AFTER UPDATE ===")

setup.setup(MyPipefyCredentials(api_token="123"), name="pipefy")
setup.setup(MySharepointCredentials(user="abc", password="teste"), name="sharepoint")

pipefy = CredentialsLoader.load(MyPipefyCredentials, FernetEncryption, name="pipefy")
sharepoint = CredentialsLoader.load(MySharepointCredentials, FernetEncryption, name="sharepoint")

print(f"{pipefy=}")
print(f"{sharepoint=}")




# TESTES DIRETÓRIO
config = PathConfig.getDefault()
config = config.updateDirectory(config.downloadKey, "new_download")

print("Updated directories:")
for k, v in config.directories.items():
    print(f"{k} -> {v}")

print(f"{config.directories=}")
print(f"{config.removeRootMarker=}")
print(f"{DEFAULT_PATH_CONFIG.directories=}")


config = config.updateDirectory(config.secretDirKey, "new_secret")

print("Updated directories:")
for k, v in config.directories.items():
    print(f"{k} -> {v}")

print(f"{config.directories=}")
print(f"{DEFAULT_PATH_CONFIG.directories=}")

config = config.updateDirectory(config.secretKeyKey, "nova")

print("Updated directories:")
for k, v in config.directories.items():
    print(f"{k} -> {v}")

print(f"{config.directories=}")
print(f"{DEFAULT_PATH_CONFIG.directories=}")

print("\nSETUP FINALIZADO")
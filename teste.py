from infra_core import PathConfig

config = PathConfig.getDefault()
config = config.updateDirectory(config.secretDirKey, "new_secret")
config = config.updateDirectory(config.downloadKey, "new_download")

print(config.directories)
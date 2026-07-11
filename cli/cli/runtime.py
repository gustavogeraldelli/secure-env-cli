from pathlib import Path

from core.exceptions import VaultError
from core.registry import Registry
from core.storage import LocalFileStorage, RemoteApiStorage, StorageProvider


def build_storage(config: dict) -> StorageProvider:
    if config.get("modo") == "remoto":
        if not config.get("api_url") or not config.get("token"):
            raise VaultError("modo remoto ativado, mas api_url ou token faltam no config.json")
        return RemoteApiStorage(config["api_url"], config["token"])

    return LocalFileStorage(Path.home() / ".sec-registry")


def build_registry(config: dict) -> Registry:
    return Registry(build_storage(config))

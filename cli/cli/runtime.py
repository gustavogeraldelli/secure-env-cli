from pathlib import Path

from core.exceptions import VaultError
from core.vault import Vault
from core.storage import LocalFileStorage, RemoteApiStorage, StorageProvider


def build_storage(config: dict) -> StorageProvider:
    if config.get("modo") == "remoto":
        if not config.get("api_url") or not config.get("token"):
            raise VaultError("modo remoto ativado, mas api_url ou token faltam no config.json")
        return RemoteApiStorage(config["api_url"], config["token"])

    return LocalFileStorage(Path.home() / ".secure-env")


def build_vault(config: dict) -> Vault:
    return Vault(build_storage(config))

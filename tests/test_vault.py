import pytest

from core.exceptions import VaultError, VaultNotInitializedError
from core.vault import Vault


class MemoryStorage:
    def __init__(self):
        self.data = None

    def load(self):
        return self.data

    def save(self, data):
        self.data = data

    def exists(self):
        return self.data is not None


@pytest.fixture
def storage():
    return MemoryStorage()


@pytest.fixture
def vault(storage):
    return Vault(storage)


def test_init_creates_vault_with_verification_payload(vault, storage):
    vault.init("master-password")

    assert storage.exists()
    assert "__verify__" in storage.data


def test_init_twice_fails(vault):
    vault.init("master-password")

    with pytest.raises(VaultError, match="ja foi inicializado"):
        vault.init("master-password")


def test_set_and_get_secret(vault):
    vault.init("master-password")

    vault.set("master-password", "DB_PASS", "secret-value")

    assert vault.get("master-password", "DB_PASS") == "secret-value"


def test_secret_is_not_stored_as_plaintext(vault, storage):
    vault.init("master-password")

    vault.set("master-password", "DB_PASS", "secret-value")

    assert storage.data["DB_PASS"] != "secret-value"
    assert storage.data["DB_PASS"]["ciphertext"] != "secret-value"


def test_set_before_init_fails(vault):
    with pytest.raises(VaultNotInitializedError, match="cofre nao inicializado"):
        vault.set("master-password", "DB_PASS", "secret-value")


def test_get_before_init_fails(vault):
    with pytest.raises(VaultNotInitializedError, match="cofre nao inicializado"):
        vault.get("master-password", "DB_PASS")


def test_get_missing_key_fails(vault):
    vault.init("master-password")

    with pytest.raises(KeyError, match="chave 'DB_PASS' nao existe"):
        vault.get("master-password", "DB_PASS")


def test_set_reserved_key_fails(vault):
    vault.init("master-password")

    with pytest.raises(ValueError, match="reservadas"):
        vault.set("master-password", "__verify__", "secret-value")


def test_get_reserved_key_fails(vault):
    vault.init("master-password")

    with pytest.raises(ValueError, match="acesso negado"):
        vault.get("master-password", "__verify__")


def test_get_with_wrong_password_fails(vault):
    vault.init("master-password")
    vault.set("master-password", "DB_PASS", "secret-value")

    with pytest.raises(PermissionError, match="senha incorreta"):
        vault.get("wrong-password", "DB_PASS")

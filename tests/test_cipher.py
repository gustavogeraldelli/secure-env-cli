import pytest

from core.cipher import Cipher


def test_encrypt_returns_expected_payload_shape():
    payload = Cipher.encrypt("master-password", "secret-value")

    assert set(payload) == {"salt", "nonce", "ciphertext"}
    assert all(isinstance(value, str) for value in payload.values())
    assert all(payload.values())


def test_decrypt_returns_original_text():
    payload = Cipher.encrypt("master-password", "secret-value")

    result = Cipher.decrypt("master-password", payload)

    assert result == "secret-value"


def test_encrypting_same_text_twice_generates_different_payloads():
    first_payload = Cipher.encrypt("master-password", "secret-value")
    second_payload = Cipher.encrypt("master-password", "secret-value")

    assert first_payload != second_payload


def test_decrypt_with_wrong_password_fails():
    payload = Cipher.encrypt("master-password", "secret-value")

    with pytest.raises(PermissionError, match="senha incorreta"):
        Cipher.decrypt("wrong-password", payload)

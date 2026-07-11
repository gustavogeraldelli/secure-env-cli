import pytest
import requests

from core.exceptions import RemoteStorageError
from core.storage import RemoteApiStorage


class FakeResponse:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self.payload = payload or {}

    def json(self):
        return self.payload

    def raise_for_status(self):
        return None


def test_remote_storage_raises_error_for_expired_or_invalid_session(monkeypatch):
    def fake_request(**kwargs):
        return FakeResponse(401)

    monkeypatch.setattr("requests.request", fake_request)

    storage = RemoteApiStorage("https://example.com", "token")

    with pytest.raises(RemoteStorageError, match="sessao expirada"):
        storage.load()


def test_remote_storage_raises_error_after_network_retries(monkeypatch):
    sleep_calls = []

    def fake_request(**kwargs):
        raise requests.exceptions.ConnectionError("network down")

    monkeypatch.setattr("requests.request", fake_request)
    monkeypatch.setattr("time.sleep", lambda seconds: sleep_calls.append(seconds))

    storage = RemoteApiStorage("https://example.com", "token")

    with pytest.raises(RemoteStorageError, match="falha na comunicacao"):
        storage.load()

    assert sleep_calls == [1, 2]

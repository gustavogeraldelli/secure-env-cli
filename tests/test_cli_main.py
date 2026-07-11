from cli.prompts import get_secret_value


def test_get_secret_value_returns_confirmed_value(monkeypatch):
    prompts = []

    def fake_getpass(prompt):
        prompts.append(prompt)
        return "secret-value"

    monkeypatch.setattr("getpass.getpass", fake_getpass)

    assert get_secret_value("DB_PASS") == "secret-value"
    assert prompts == ["valor para 'DB_PASS': "]

import os

from cli.injector import executar_com_ambiente


def test_executar_com_ambiente_merges_current_env_with_new_variables(monkeypatch):
    calls = []

    def fake_run(command, env):
        calls.append({"command": command, "env": env})

    monkeypatch.setenv("EXISTING_VAR", "existing-value")
    monkeypatch.setattr("subprocess.run", fake_run)

    executar_com_ambiente(["python", "app.py"], {"DB_PASS": "secret-value"})

    assert calls == [
        {
            "command": ["python", "app.py"],
            "env": {
                **os.environ,
                "DB_PASS": "secret-value",
            },
        }
    ]


def test_executar_com_ambiente_overrides_existing_env_variables(monkeypatch):
    calls = []

    def fake_run(command, env):
        calls.append(env)

    monkeypatch.setenv("DB_PASS", "old-value")
    monkeypatch.setattr("subprocess.run", fake_run)

    executar_com_ambiente(["python", "app.py"], {"DB_PASS": "new-value"})

    assert calls[0]["DB_PASS"] == "new-value"


def test_executar_com_ambiente_prints_message_when_command_is_missing(monkeypatch, capsys):
    def fake_run(command, env):
        raise FileNotFoundError

    monkeypatch.setattr("subprocess.run", fake_run)

    executar_com_ambiente(["missing-command"], {})

    captured = capsys.readouterr()
    assert "comando 'missing-command' nao encontrado" in captured.out

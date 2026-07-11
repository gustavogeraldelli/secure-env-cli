from pathlib import Path

import pytest

from cli.parser import ler_yml, separar_variaveis


def test_ler_yml_returns_env_block(tmp_path):
    registry_file = tmp_path / ".registry.yml"
    registry_file.write_text(
        """
env:
  PORT: 8080
  DEBUG: false
  DB_PASS: "secret:DB_PASS"
""",
        encoding="utf-8",
    )

    assert ler_yml(registry_file) == {
        "PORT": 8080,
        "DEBUG": False,
        "DB_PASS": "secret:DB_PASS",
    }


def test_ler_yml_returns_empty_dict_when_env_block_is_missing(tmp_path):
    registry_file = tmp_path / ".registry.yml"
    registry_file.write_text("name: example\n", encoding="utf-8")

    assert ler_yml(registry_file) == {}


def test_ler_yml_returns_empty_dict_for_empty_file(tmp_path):
    registry_file = tmp_path / ".registry.yml"
    registry_file.write_text("", encoding="utf-8")

    assert ler_yml(registry_file) == {}


def test_ler_yml_fails_when_file_does_not_exist(tmp_path):
    missing_file = tmp_path / ".registry.yml"

    with pytest.raises(FileNotFoundError, match="arquivo .registry.yml nao encontrado"):
        ler_yml(missing_file)


def test_separar_variaveis_splits_static_values_and_secrets():
    env_vars = {
        "PORT": 8080,
        "DEBUG": False,
        "DB_PASS": "secret:DB_PASS",
        "API_TOKEN": "secret:API_TOKEN",
    }

    estaticas, secrets = separar_variaveis(env_vars)

    assert estaticas == {
        "PORT": "8080",
        "DEBUG": "False",
    }
    assert secrets == [
        ("DB_PASS", "DB_PASS"),
        ("API_TOKEN", "API_TOKEN"),
    ]


def test_separar_variaveis_keeps_non_secret_values_as_strings():
    env_vars = {
        "PORT": 8080,
        "ENABLED": True,
        "EMPTY": None,
    }

    estaticas, secrets = separar_variaveis(env_vars)

    assert estaticas == {
        "PORT": "8080",
        "ENABLED": "True",
        "EMPTY": "None",
    }
    assert secrets == []

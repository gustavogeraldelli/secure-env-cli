import getpass
import json
import os
from pathlib import Path

import requests

from cli.config import carregar_config
from cli.injector import executar_com_ambiente
from cli.parser import ler_yml, separar_variaveis
from cli.prompts import get_password, get_secret_value
from cli.runtime import build_registry


def cmd_login() -> None:
    url = input("url da api: ").strip("/")
    senha = getpass.getpass("senha do servidor: ")

    try:
        resposta = requests.post(f"{url}/auth", json={"senha": senha}, timeout=5)
        resposta.raise_for_status()

        config = {
            "modo": "remoto",
            "api_url": url,
            "token": resposta.json()["access_token"],
        }

        dir_config = Path.home() / ".sec-registry"
        dir_config.mkdir(exist_ok=True)

        with open(dir_config / "config.json", "w") as f:
            json.dump(config, f, indent=2)

        print("login efetuado. modo remoto ativado.")

    except requests.exceptions.RequestException:
        print("erro: falha na conexao ou senha invalida.")


def cmd_mode(tipo: str) -> None:
    dir_config = Path.home() / ".sec-registry"
    arquivo_config = dir_config / "config.json"

    if not arquivo_config.exists():
        dir_config.mkdir(exist_ok=True)
        config = {"modo": tipo}
    else:
        with open(arquivo_config, "r") as f:
            config = json.load(f)
        config["modo"] = tipo

    with open(arquivo_config, "w") as f:
        json.dump(config, f, indent=2)

    print(f"modo alterado para: {tipo}")


def cmd_init() -> None:
    registry = build_registry(carregar_config())
    senha = get_password("crie a senha mestra: ", force_prompt=True)

    if not os.environ.get("SEC_REGISTRY_PASSWORD"):
        if senha != getpass.getpass("confirme a senha: "):
            print("erro: as senhas nao batem.")
            return

    registry.init(senha)
    print("cofre inicializado.")


def cmd_set(chave: str) -> None:
    registry = build_registry(carregar_config())
    senha = get_password()
    valor = get_secret_value(chave)

    registry.set(senha, chave, valor)
    print(f"secret '{chave}' guardado.")


def cmd_get(chave: str) -> None:
    registry = build_registry(carregar_config())
    senha = get_password()

    print(registry.get(senha, chave))


def cmd_run(comando_alvo: list[str]) -> None:
    if not comando_alvo:
        print("erro: especifique o comando a executar. ex: sec-registry run npm start")
        return

    registry = build_registry(carregar_config())
    env_vars = ler_yml(Path(".registry.yml"))

    estaticas, secrets_pendentes = separar_variaveis(env_vars)
    print(f"leitura concluida: {len(estaticas)} vars estaticas, {len(secrets_pendentes)} secrets.")

    secrets_extraidos = {}
    if secrets_pendentes:
        senha = get_password()
        for chave_env, chave_vault in secrets_pendentes:
            secrets_extraidos[chave_env] = registry.get(senha, chave_vault)

    executar_com_ambiente(comando_alvo, {**estaticas, **secrets_extraidos})

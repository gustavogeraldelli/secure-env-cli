import getpass
import os

import keyring


SERVICO = "sec-registry"
USUARIO = "master-key"


def get_password(prompt: str = "senha mestra: ", force_prompt: bool = False) -> str:
    if not force_prompt:
        senha_env = os.environ.get("SEC_REGISTRY_PASSWORD")
        if senha_env:
            return senha_env

        try:
            senha_salva = keyring.get_password(SERVICO, USUARIO)
            if senha_salva:
                return senha_salva
        except Exception:
            pass

    senha_digitada = getpass.getpass(prompt)

    try:
        keyring.set_password(SERVICO, USUARIO, senha_digitada)
    except Exception:
        pass

    return senha_digitada


def get_secret_value(chave: str) -> str:
    return getpass.getpass(f"valor para '{chave}': ")

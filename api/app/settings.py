import os

def get_server_token() -> str:
    token = os.environ.get("SECURE_ENV_SERVER_TOKEN")
    if not token:
        raise RuntimeError("SECURE_ENV_SERVER_TOKEN nao configurado")
    return token

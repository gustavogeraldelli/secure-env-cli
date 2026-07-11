import os

def get_server_token() -> str:
    token = os.environ.get("SEC_REGISTRY_SERVER_TOKEN")
    if not token:
        raise RuntimeError("SEC_REGISTRY_SERVER_TOKEN nao configurado")
    return token

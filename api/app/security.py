from fastapi import Header, HTTPException

from .settings import get_server_token

TOKEN_MESTRE = get_server_token()

tokens_ativos = set()

def verificar_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="token ausente ou mal formatado")
    
    token = authorization.split(" ")[1]
    
    if token not in tokens_ativos:
        raise HTTPException(status_code=403, detail="acesso negado: token invalido ou expirado")

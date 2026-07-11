import json
from abc import ABC, abstractmethod
from pathlib import Path
import requests
import time
from requests.exceptions import RequestException

from .exceptions import RemoteStorageError

class StorageProvider(ABC):
    """
    Contrato para os provedores de armazenamento.
    """
    
    @abstractmethod
    def load(self) -> dict:
        pass

    @abstractmethod
    def save(self, data: dict) -> None:
        pass

    @abstractmethod
    def exists(self) -> bool:
        pass


class LocalFileStorage(StorageProvider):
    """
    Implementação que salva os dados criptografados em um arquivo JSON local.
    """
    
    def __init__(self, base_dir: Path):
        self.arquivo = base_dir / "vault.json"
        if not base_dir.exists():
            base_dir.mkdir(parents=True)

    def load(self) -> dict:
        with open(self.arquivo, 'r') as f:
            return json.load(f)

    def save(self, data: dict) -> None:
        with open(self.arquivo, 'w') as f:
            json.dump(data, f, indent=2)

    def exists(self) -> bool:
        return self.arquivo.exists()
    
class RemoteApiStorage(StorageProvider):
    """
    Implementação que salva e busca os dados em uma API remota.
    """
    
    def __init__(self, api_url: str, token: str):
        self.api_url = api_url.rstrip('/')
        self.token = token

    def _send_request(self, metodo: str, endpoint: str, payload: dict = None) -> requests.Response:
        """Envia requests com regras de timeout e retry"""
        url = f"{self.api_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        max_tentativas = 3

        for tentativa in range(max_tentativas):
            try:
                resposta = requests.request(
                    method=metodo, 
                    url=url, 
                    headers=headers, 
                    json=payload, 
                    timeout=5
                )
                
                if resposta.status_code in (401, 403):
                    raise RemoteStorageError(
                        "sessao expirada ou acesso negado. rode o comando 'login' novamente."
                    )

                if resposta.status_code == 404:
                    return resposta
                    
                resposta.raise_for_status()
                return resposta

            except RequestException as e:
                if tentativa == max_tentativas - 1:
                    raise RemoteStorageError(
                        f"falha na comunicacao com a api apos {max_tentativas} tentativas."
                    ) from e
                
                espera = 2 ** tentativa
                time.sleep(espera)

    def load(self) -> dict:
        response = self._send_request("GET", "/vault")
        if response.status_code == 404:
            return {} 
        return response.json()

    def save(self, data: dict) -> None:
        self._send_request("PUT", "/vault", payload=data)

    def exists(self) -> bool:
        response = self._send_request("HEAD", "/vault")
        return response.status_code == 200

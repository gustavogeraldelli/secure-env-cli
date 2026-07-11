# Sec-Registry

CLI para armazenar secrets criptografados e injetá-los como variáveis de ambiente ao executar aplicações.

O projeto gira em torno da CLI. A API em `api/` é uma implementação simples de exemplo para demonstrar como um backend remoto pode atender aos requisitos da CLI e ajudar nos testes do fluxo remoto.

## Requisitos

* Python 3.10+
* uv

## Instalação

Clone o projeto e sincronize o ambiente:

```bash
uv sync
```

Confira se a CLI está disponível:

```bash
uv run sec-registry --help
```

As dependências da CLI ficam em `pyproject.toml` e as versões resolvidas ficam em `uv.lock`.

O fluxo com `uv` está explicado com mais detalhes em [UV.md](UV.md).

## Uso rápido

Inicialize um cofre:

```bash
uv run sec-registry init
```

Salve um secret:

```bash
uv run sec-registry set DB_PASS
```

Leia um secret:

```bash
uv run sec-registry get DB_PASS
```

Crie um arquivo `.registry.yml` no projeto que vai receber as variáveis:

```yaml
env:
  PORT: 8080
  DB_PASS: "secret:DB_PASS"
  API_TOKEN: "secret:API_TOKEN"
```

Execute a aplicação com o ambiente montado pela CLI:

```bash
uv run sec-registry run uv run python cli/app_teste.py
```

Valores comuns são injetados como texto. Valores com prefixo `secret:` são buscados no cofre antes da execução.

## Comandos

```bash
uv run sec-registry init
uv run sec-registry set <chave>
uv run sec-registry get <chave>
uv run sec-registry run <comando>
uv run sec-registry mode local
uv run sec-registry mode remoto
uv run sec-registry login
```

O comando `set` pede o valor do secret por prompt oculto para evitar que ele fique salvo no histórico do shell.

Também é possível chamar a CLI pelo módulo Python:

```bash
uv run python -m cli.main --help
```

## Como funciona

No modo local, o cofre fica em:

```text
~/.sec-registry/vault.json
```

Os secrets são criptografados antes de serem persistidos. A CLI usa AES-GCM com chave derivada por PBKDF2.

Durante o `run`, a CLI:

1. lê o `.registry.yml`;
2. separa variáveis estáticas de secrets;
3. busca os secrets no cofre;
4. executa o comando alvo com as variáveis adicionadas ao ambiente.

A senha mestra pode ser lida de três formas:

* variável `SEC_REGISTRY_PASSWORD`;
* chaveiro do sistema via `keyring`;
* prompt interativo.

## Modo remoto

O modo remoto usa a mesma CLI, mas troca o armazenamento local por uma API compatível.

Faça login:

```bash
uv run sec-registry login
```

Esse comando pede a URL da API e a senha do servidor, salva a configuração em `~/.sec-registry/config.json` e ativa o modo remoto.

Também é possível alternar manualmente:

```bash
uv run sec-registry mode local
uv run sec-registry mode remoto
```

Quando o modo remoto está ativo, `init`, `set`, `get` e `run` passam a ler e salvar o cofre pela API.

## API de exemplo

A API não é o foco do projeto. Ela existe para mostrar o contrato mínimo que um backend remoto precisa oferecer para a CLI.

Instale as dependências opcionais:

```bash
uv sync --extra api
```

Execute a API:

```bash
SEC_REGISTRY_SERVER_TOKEN=dev-token uv run --extra api uvicorn app.main:app --app-dir api --reload
```

Endpoints implementados:

```text
POST /auth
GET  /vault
PUT  /vault
HEAD /vault
```

A API salva o payload criptografado em `server_vault.json`. Ela não conhece a senha mestra e não descriptografa secrets.
Esse arquivo é gerado localmente e é ignorado pelo Git.

A variável `SEC_REGISTRY_SERVER_TOKEN` é o segredo operacional usado pelo endpoint `POST /auth`.
Veja [api/.env.example](api/.env.example).

## Estrutura

```text
cli/
  cli/      comandos, parser do .registry.yml e injeção de ambiente
  core/     regras do cofre, criptografia e providers de armazenamento
api/
  app/      API FastAPI de exemplo para o modo remoto
```

## Testes

```bash
uv run pytest
```

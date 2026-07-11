# Sec-Registry

CLI para armazenar secrets criptografados e injetá-los como variáveis de ambiente ao executar aplicações.

A CLI é o foco do projeto. A API em `api/` é apenas uma implementação de exemplo de um backend remoto compatível.

## Uso

Requisitos: Python 3.10+ e `uv`.

```bash
uv sync
uv run sec-registry --help
```

Fluxo básico:

```bash
uv run sec-registry init
uv run sec-registry set DB_PASS
uv run sec-registry get DB_PASS
```

O comando `set` pede o valor do secret por prompt oculto, evitando que o valor fique salvo no histórico do shell.

Crie um `.registry.yml` no projeto que vai receber as variáveis:

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

Comandos disponíveis:

```bash
uv run sec-registry init
uv run sec-registry set <chave>
uv run sec-registry get <chave>
uv run sec-registry run <comando>
uv run sec-registry mode local
uv run sec-registry mode remoto
uv run sec-registry login
```

Também é possível chamar a CLI pelo módulo Python:

```bash
uv run python -m cli.main --help
```

## Como funciona

No modo local, o cofre fica em `~/.sec-registry/vault.json`. Os secrets são criptografados antes de serem persistidos usando AES-GCM, com chave derivada da senha mestra por PBKDF2.

Durante o `run`, a CLI lê o `.registry.yml`, separa variáveis estáticas de referências `secret:`, busca os valores no cofre e executa o comando alvo com as variáveis adicionadas ao ambiente.

A senha mestra pode vir de três lugares:

* variável `SEC_REGISTRY_PASSWORD`;
* chaveiro do sistema via `keyring`;
* prompt interativo.

O `.registry.yml` não guarda secrets criptografados; ele é só o contrato de ambiente. Pode ser versionado quando contém apenas nomes de variáveis e referências como `secret:DB_PASS`. Evite colocar valores sensíveis diretamente nele.

O que é criptografado é o cofre (`vault.json` no modo local ou o payload salvo pela API no modo remoto). Em CI, a senha mestra pode vir de um secret do provedor via `SEC_REGISTRY_PASSWORD`. Versionar um cofre criptografado pode ser aceitável em alguns fluxos, desde que a senha mestra fique fora do repositório; ainda assim, o arquivo pode ser copiado e atacado offline.

Limitações principais:

* `SEC_REGISTRY_PASSWORD` deve ser tratado como segredo;
* o modo remoto atual é exemplo, não backend pronto para produção;
* não há rotação automática de secrets, controle de acesso por usuário ou auditoria completa.

## Modo remoto

O modo remoto usa a mesma CLI, mas troca o armazenamento local por uma API compatível.

```bash
uv run sec-registry login
uv run sec-registry mode local
uv run sec-registry mode remoto
```

Para rodar a API de exemplo:

```bash
uv sync --extra api
SEC_REGISTRY_SERVER_TOKEN=dev-token uv run --extra api uvicorn app.main:app --app-dir api --reload
```

Endpoints implementados:

```text
POST /auth
GET  /vault
PUT  /vault
HEAD /vault
```

A API salva o payload criptografado em `server_vault.json`, arquivo gerado localmente e ignorado pelo Git. A variável `SEC_REGISTRY_SERVER_TOKEN` é o segredo operacional usado pelo endpoint `POST /auth`; veja [api/.env.example](api/.env.example).

## Estrutura e testes

```text
cli/
  cli/      entrada da CLI, comandos, prompts, parser e injeção de ambiente
  core/     regra de negócio, criptografia, storage e exceções
api/
  app/      API FastAPI de exemplo para o modo remoto
tests/      testes do core e da CLI
```

```bash
uv run pytest
```

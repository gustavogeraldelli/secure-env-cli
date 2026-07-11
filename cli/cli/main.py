import argparse

from core.exceptions import VaultError
from cli.commands import cmd_get, cmd_init, cmd_login, cmd_mode, cmd_run, cmd_set


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="cofre local e remoto para secrets")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    subparsers.add_parser("init", help="inicializa o cofre")
    
    cmd_set = subparsers.add_parser("set", help="guarda um segredo")
    cmd_set.add_argument("chave")

    cmd_get = subparsers.add_parser("get", help="le um segredo")
    cmd_get.add_argument("chave")

    cmd_run = subparsers.add_parser("run", help="le o yml e mapeia os secrets")
    cmd_run.add_argument("comando_alvo", nargs=argparse.REMAINDER) 

    subparsers.add_parser("login", help="conecta com a API remota")
    
    cmd_mode = subparsers.add_parser("mode", help="alterna entre modo local e remoto")
    cmd_mode.add_argument("tipo", choices=["local", "remoto"], help="escolha 'local' ou 'remoto'")

    return parser


def dispatch(args: argparse.Namespace) -> None:
    if args.comando == "login":
        cmd_login()
    elif args.comando == "mode":
        cmd_mode(args.tipo)
    elif args.comando == "init":
        cmd_init()
    elif args.comando == "set":
        cmd_set(args.chave)
    elif args.comando == "get":
        cmd_get(args.chave)
    elif args.comando == "run":
        cmd_run(args.comando_alvo)


def main():
    args = build_parser().parse_args()

    try:
        dispatch(args)
    except VaultError as e:
        print(f"erro no cofre: {str(e)}")
    except Exception as e:
        print(f"erro: {str(e)}")

if __name__ == "__main__":
    main()

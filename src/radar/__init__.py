import argparse
import os
import re

from dotenv import load_dotenv

from radar import config


def descobrir_chat(prefixo: str) -> None:
    from radar.comum.telegram import descobrir_chats

    token = os.getenv(f"{prefixo}_BOT_TOKEN")
    if not token:
        raise SystemExit(f"Coloque {prefixo}_BOT_TOKEN no .env primeiro.")
    chats = descobrir_chats(token)
    if not chats:
        raise SystemExit("Nenhuma conversa encontrada. Mande uma mensagem no grupo "
                         "(com o bot dentro) e rode de novo.")
    for chat_id, nome in chats:
        print(f"{chat_id}\t{nome}")
    grupos = [c for c in chats if c[0] < 0] or chats
    chat_id, nome = grupos[0]
    env = config.RAIZ / ".env"
    conteudo = env.read_text()
    linha = f"{prefixo}_CHAT_ID={chat_id}"
    if re.search(rf"^{prefixo}_CHAT_ID=.*$", conteudo, flags=re.M):
        conteudo = re.sub(rf"^{prefixo}_CHAT_ID=.*$", linha, conteudo, flags=re.M)
    else:
        conteudo += f"\n{linha}\n"
    env.write_text(conteudo)
    print(f"\nSalvo no .env: {linha}  ({nome})")


def main() -> None:
    load_dotenv(config.RAIZ / ".env")
    parser = argparse.ArgumentParser(prog="radar")
    sub = parser.add_subparsers(dest="comando", required=True)

    p_imoveis = sub.add_parser("imoveis", help="busca imóveis novos e avisa no Telegram")
    p_imoveis.add_argument("--simular", action="store_true",
                           help="só imprime no terminal; não envia nem salva nada")
    p_imoveis.add_argument("--sites", help="lista separada por vírgula (olx,vivareal)")

    p_chat = sub.add_parser("descobrir-chat", help="descobre o chat_id do grupo e salva no .env")
    p_chat.add_argument("tema", nargs="?", default="IMOVEIS", help="IMOVEIS ou VIAGENS")

    args = parser.parse_args()
    if args.comando == "imoveis":
        from radar.imoveis.run import rodar

        rodar(simular=args.simular, sites=args.sites.split(",") if args.sites else None)
    elif args.comando == "descobrir-chat":
        descobrir_chat(args.tema.upper())

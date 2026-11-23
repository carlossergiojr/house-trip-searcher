"""Envio de mensagens por um bot do Telegram."""

import os

import httpx

API = "https://api.telegram.org/bot{token}/{metodo}"


class Telegram:
    """Bot de um tema. Lê <PREFIXO>_BOT_TOKEN e <PREFIXO>_CHAT_ID do ambiente."""

    def __init__(self, prefixo: str, simular: bool = False):
        self.token = os.getenv(f"{prefixo}_BOT_TOKEN", "")
        self.chat_id = os.getenv(f"{prefixo}_CHAT_ID", "")
        self.simular = simular
        if not simular and not (self.token and self.chat_id):
            raise SystemExit(
                f"Faltam {prefixo}_BOT_TOKEN e/ou {prefixo}_CHAT_ID no .env "
                "(veja o README)."
            )

    def _chamar(self, metodo: str, **dados) -> dict:
        r = httpx.post(API.format(token=self.token, metodo=metodo), data=dados, timeout=30)
        r.raise_for_status()
        return r.json()

    def texto(self, mensagem: str) -> None:
        if self.simular:
            print(f"[telegram] {mensagem}\n")
            return
        self._chamar("sendMessage", chat_id=self.chat_id, text=mensagem, parse_mode="HTML",
                     disable_web_page_preview="true")

    def foto(self, url_foto: str | None, legenda: str) -> None:
        if self.simular:
            print(f"[telegram foto={url_foto}] {legenda}\n")
            return
        if url_foto:
            try:
                self._chamar("sendPhoto", chat_id=self.chat_id, photo=url_foto,
                             caption=legenda, parse_mode="HTML")
                return
            except httpx.HTTPError:
                pass  # foto inacessível para o Telegram: manda só o texto
        self.texto(legenda)


def descobrir_chats(token: str) -> list[tuple[int, str]]:
    """Lista (chat_id, nome) das conversas recentes onde o bot recebeu mensagem."""
    r = httpx.get(API.format(token=token, metodo="getUpdates"), timeout=30)
    r.raise_for_status()
    chats = {}
    for upd in r.json().get("result", []):
        msg = upd.get("message") or upd.get("my_chat_member") or {}
        chat = msg.get("chat")
        if chat:
            chats[chat["id"]] = chat.get("title") or chat.get("first_name") or "?"
    return list(chats.items())

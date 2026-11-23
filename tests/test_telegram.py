import httpx
import pytest

from radar.comum import telegram


def bot_com(monkeypatch, responder):
    """Bot que fala com um servidor falso; devolve (bot, chamadas feitas)."""
    monkeypatch.setenv("TESTE_BOT_TOKEN", "x")
    monkeypatch.setenv("TESTE_CHAT_ID", "-1")
    monkeypatch.setattr(telegram.time, "sleep", lambda s: esperas.append(s))
    chamadas, esperas = [], []

    def handler(req):
        metodo = req.url.path.rsplit("/", 1)[-1]
        chamadas.append(metodo)
        return responder(metodo, len(chamadas))

    cliente = httpx.Client(transport=httpx.MockTransport(handler))
    return telegram.Telegram("TESTE", cliente=cliente), chamadas, esperas


def test_espera_quando_recebe_429(monkeypatch):
    def responder(metodo, n):
        if n == 1:
            return httpx.Response(429, json={"ok": False, "parameters": {"retry_after": 7}})
        return httpx.Response(200, json={"ok": True})
    bot, chamadas, esperas = bot_com(monkeypatch, responder)
    bot.texto("oi")
    assert chamadas == ["sendMessage", "sendMessage"] and esperas == [8]


def test_foto_invalida_vira_texto(monkeypatch):
    def responder(metodo, n):
        return httpx.Response(400 if metodo == "sendPhoto" else 200, json={"ok": True})
    bot, chamadas, _ = bot_com(monkeypatch, responder)
    bot.foto("http://foto", "legenda")
    assert chamadas == ["sendPhoto", "sendMessage"]


def test_erro_do_servidor_na_foto_nao_manda_texto_repetido(monkeypatch):
    bot, chamadas, _ = bot_com(monkeypatch, lambda m, n: httpx.Response(500, json={}))
    with pytest.raises(httpx.HTTPStatusError):
        bot.foto("http://foto", "legenda")
    assert chamadas == ["sendPhoto"]

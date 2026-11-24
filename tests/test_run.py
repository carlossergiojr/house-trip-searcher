"""Fluxo de uma rodada com sites e bot falsos (sem rede)."""

import json
import threading

import pytest

from radar import config
from radar.imoveis import run
from radar.imoveis.modelo import Imovel


def imovel(site, id, bairro="Brasília"):
    return Imovel(site=site, id=id, url=f"https://{site}/{id}", tipo="casa", bairro=bairro,
                  preco=1500, foto="http://foto")


class BotFalso:
    def __init__(self):
        self.mensagens = []
        self.falhar_no_envio = None  # n-ésimo envio de foto que deve falhar
        self.falhar_texto = False

    def texto(self, msg):
        if self.falhar_texto:
            raise RuntimeError("telegram fora")
        self.mensagens.append(("texto", msg))

    def foto(self, url, legenda):
        n = sum(1 for tipo, _ in self.mensagens if tipo == "foto") + 1
        if n == self.falhar_no_envio:
            raise RuntimeError("429")
        self.mensagens.append(("foto", legenda))

    def fotos(self):
        return [m for tipo, m in self.mensagens if tipo == "foto"]

    def textos(self):
        return [m for tipo, m in self.mensagens if tipo == "texto"]


@pytest.fixture
def ambiente(tmp_path, monkeypatch):
    """Devolve (bot, sites): sites[nome] é a lista de anúncios ou a exceção da próxima rodada."""
    bot = BotFalso()
    sites = {"olx": [], "vivareal": []}

    def busca(nome):
        def buscar():
            if isinstance(sites[nome], Exception):
                raise sites[nome]
            return sites[nome]
        return buscar

    monkeypatch.setattr(config, "DADOS", tmp_path)
    monkeypatch.setattr(run, "Telegram", lambda *a, **k: bot)
    monkeypatch.setattr(run, "BUSCAS", {n: busca(n) for n in sites})
    monkeypatch.setattr(run, "PAUSA_ENTRE_ENVIOS", 0)
    return bot, sites


def estado(tmp_path):
    return json.loads((tmp_path / "imoveis.json").read_text())


def test_primeira_vez_resume_e_depois_so_novos(ambiente, tmp_path):
    bot, sites = ambiente
    sites["olx"] = [imovel("olx", "1")]
    sites["vivareal"] = [imovel("vivareal", "2"), imovel("vivareal", "3", "Jomafa")]
    run.rodar()
    assert bot.fotos() == [] and "Já existem 3 anúncios" in bot.textos()[0]

    sites["vivareal"].append(imovel("vivareal", "4"))
    run.rodar()
    assert len(bot.fotos()) == 1 and "vivareal/4" in bot.fotos()[0]


def test_site_que_falhou_na_primeira_vez_tambem_so_resume(ambiente, tmp_path):
    bot, sites = ambiente
    sites["olx"] = RuntimeError("503")
    sites["vivareal"] = [imovel("vivareal", "1")]
    run.rodar()
    sites["olx"] = [imovel("olx", str(n)) for n in range(30)]
    run.rodar()
    assert bot.fotos() == []
    assert "(olx)" in bot.textos()[-1] and "Já existem 30" in bot.textos()[-1]


def test_estado_antigo_sem_iniciados_nao_resume_de_novo(ambiente, tmp_path):
    bot, sites = ambiente
    (tmp_path / "imoveis.json").write_text(json.dumps(
        {"vistos": ["vivareal:1"], "falhas": {"olx": 0, "vivareal": 0}}))
    sites["olx"] = [imovel("olx", "9")]
    sites["vivareal"] = [imovel("vivareal", "1")]
    run.rodar()
    assert len(bot.fotos()) == 1 and "olx/9" in bot.fotos()[0]
    assert estado(tmp_path)["iniciados"] == ["olx", "vivareal"]


def test_falha_no_envio_salva_o_que_foi_e_tenta_o_resto_depois(ambiente, tmp_path):
    bot, sites = ambiente
    run.rodar()  # primeira vez, nada no ar
    sites["vivareal"] = [imovel("vivareal", str(n)) for n in range(1, 4)]
    bot.falhar_no_envio = 2
    run.rodar()
    assert estado(tmp_path)["vistos"] == ["vivareal:1"]

    bot.falhar_no_envio = None
    run.rodar()
    assert [f.split("vivareal/")[1][0] for f in bot.fotos()] == ["1", "2", "3"]


def test_aviso_de_falha_escapado_e_nao_derruba_a_rodada(ambiente, tmp_path):
    bot, sites = ambiente
    sites["vivareal"] = [imovel("vivareal", "1")]
    run.rodar()
    sites["olx"] = RuntimeError("HTTP 403 em https://olx?pe=2500&sf=1 <x>")
    sites["vivareal"].append(imovel("vivareal", "2"))
    for _ in range(3):
        run.rodar()
    alerta = bot.textos()[-1]
    assert "&amp;sf=1 &lt;x&gt;" in alerta and "3 vezes" in alerta
    assert len(bot.fotos()) == 1  # o vivareal seguiu rodando

    run.rodar()  # 4ª falha: não repete o aviso
    assert bot.textos()[-1] == alerta
    sites["olx"] = []
    run.rodar()
    assert "olx voltou" in bot.textos()[-1]
    assert estado(tmp_path)["falhas"]["olx"] == 0


def test_aviso_que_nao_sai_nao_perde_estado(ambiente, tmp_path):
    bot, sites = ambiente
    bot.falhar_texto = True
    sites["olx"] = RuntimeError("403")
    sites["vivareal"] = [imovel("vivareal", "1")]
    for _ in range(3):
        run.rodar()
    assert estado(tmp_path)["falhas"]["olx"] == 3


def test_todos_reenvia_os_ja_vistos(ambiente, tmp_path):
    bot, sites = ambiente
    sites["vivareal"] = [imovel("vivareal", "1"), imovel("vivareal", "2")]
    run.rodar()
    run.rodar(todos=True)
    assert len(bot.fotos()) == 2


def test_sites_buscados_ao_mesmo_tempo(ambiente, tmp_path, monkeypatch):
    """Cada busca espera a outra começar: em sequência, a barreira estoura e o site falha."""
    bot, sites = ambiente
    barreira = threading.Barrier(2, timeout=5)

    def busca(nome):
        def buscar():
            barreira.wait()
            return [imovel(nome, "1")]
        return buscar

    monkeypatch.setattr(run, "BUSCAS", {"olx": busca("olx"), "vivareal": busca("vivareal")})
    run.rodar()
    assert estado(tmp_path)["falhas"] == {"olx": 0, "vivareal": 0}
    assert "2 anúncios" in bot.textos()[0]

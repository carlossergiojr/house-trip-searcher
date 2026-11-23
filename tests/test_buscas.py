"""Busca por site sem rede: navegador e página falsos."""

from contextlib import contextmanager

import pytest
from playwright.sync_api import TimeoutError as TimeoutPlaywright

from radar.imoveis import olx, vivareal

CARD_VIVAREAL = {"href": "https://www.vivareal.com.br/imovel/casa-2-quartos-brasilia-bairros-"
                         "feira-de-santana-70m2-aluguel-RS1500-id-2900000010/", "txt": ""}
CARD_OLX = {"href": "https://ba.olx.com.br/x/imoveis/casa-1555000003",
            "txt": "Casa\nR$ 1.200\nFeira de Santana, Jomafa"}


def falso_navegador(monkeypatch, modulo, respostas):
    """Cada abertura de página consome uma resposta: lista de cards ou exceção."""
    respostas = list(respostas)

    class Pagina:
        def evaluate(self, js):
            r = respostas.pop(0)
            if isinstance(r, Exception):
                raise r
            return r

    @contextmanager
    def navegador():
        yield Pagina()

    monkeypatch.setattr(modulo, "navegador", navegador)
    monkeypatch.setattr(modulo, "abrir", lambda page, url: None)
    monkeypatch.setattr(modulo.time, "sleep", lambda s: None)
    if modulo is olx:
        monkeypatch.setattr(olx, "rolar_ate_o_fim", lambda page: None)


def test_vivareal_timeout_num_bairro_nao_derruba_os_outros(monkeypatch):
    falso_navegador(monkeypatch, vivareal, [TimeoutPlaywright("demorou"), [CARD_VIVAREAL], []])
    assert [i.id for i in vivareal.buscar()] == ["2900000010"]


def test_vivareal_tudo_vazio_e_falha(monkeypatch):
    falso_navegador(monkeypatch, vivareal, [[], [], []])
    with pytest.raises(RuntimeError, match="nenhum anúncio"):
        vivareal.buscar()


def test_olx_timeout_numa_categoria_nao_derruba_a_outra(monkeypatch):
    falso_navegador(monkeypatch, olx, [TimeoutPlaywright("demorou"), [CARD_OLX]])
    assert [i.bairro for i in olx.buscar()] == ["Jomafa"]

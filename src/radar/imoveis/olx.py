"""OLX: lê as categorias casas e apartamentos da cidade, mais recentes primeiro.

O bairro vem no card como "Feira de Santana, Brasília".
"""

import re

from radar import config
from radar.comum.navegador import Bloqueado, abrir, navegador
from radar.comum.texto import extrair_preco
from radar.imoveis.modelo import Imovel, bairro_alvo

CATEGORIAS = {"casa": "casas", "apartamento": "apartamentos"}
URL = ("https://www.olx.com.br/imoveis/aluguel/{categoria}/estado-ba/feira-de-santana"
       "?pe={teto}&sf=1&o={pagina}")

JS_CARDS = """() => [...document.querySelectorAll('section.olx-adcard')].map(s => {
  const a = [...s.querySelectorAll('a')].find(a => /-\\d{9,}$/.test(a.href.split('?')[0]));
  const img = s.querySelector('img');
  return a ? {href: a.href.split('?')[0], txt: s.innerText, img: img ? (img.currentSrc || img.src) : null} : null;
}).filter(Boolean)"""


def parse_card(tipo: str, card: dict) -> Imovel | None:
    m_id = re.search(r"-(\d{9,})$", card["href"])
    m_local = re.search(r"Feira de Santana, ([^\n]+)", card["txt"])
    if not (m_id and m_local):
        return None
    bairro = bairro_alvo(m_local.group(1))
    if not bairro:
        return None
    titulo = card["txt"].strip().split("\n", 1)[0]
    if "comercial" in titulo.lower():
        return None
    m_area = re.search(r"(\d+)\s*m²", card["txt"])
    return Imovel(
        site="olx",
        id=m_id.group(1),
        url=card["href"],
        tipo=tipo,
        bairro=bairro,
        preco=extrair_preco(card["txt"]),
        area=int(m_area.group(1)) if m_area else None,
        foto=card.get("img"),
    )


def buscar() -> list[Imovel]:
    with navegador() as page:
        return _buscar(page)


def _buscar(page) -> list[Imovel]:
    imoveis = []
    for tipo, categoria in CATEGORIAS.items():
        for pagina in range(1, config.PAGINAS_POR_SITE + 1):
            try:
                abrir(page, URL.format(categoria=categoria, teto=config.ALUGUEL_MAXIMO, pagina=pagina))
            except Bloqueado:
                if pagina == 1:
                    raise
                break  # bloqueou só as páginas seguintes: fica com o que já leu
            cards = page.evaluate(JS_CARDS)
            if pagina == 1 and not cards:
                raise RuntimeError(f"olx/{categoria}: nenhum anúncio na página (layout mudou?)")
            imoveis += [i for c in cards if (i := parse_card(tipo, c))]
    return imoveis

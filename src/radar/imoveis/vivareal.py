"""VivaReal: uma página por bairro, com teto de preço.

A URL de cada anúncio traz tipo, quartos, bairro, área, preço e id, por exemplo:
  /imovel/casa-3-quartos-santa-monica-bairros-feira-de-santana-com-garagem-240m2-aluguel-RS2200-id-2902852396/
O ZAP Imóveis é da mesma empresa e mostra os mesmos anúncios, por isso não é lido.
Cada bairro abre num navegador novo, com pausa longa entre eles: em sequência
rápida o site devolve 403.
"""

import random
import re
import time

from radar import config
from radar.comum.navegador import Bloqueado, abrir, navegador
from radar.comum.texto import extrair_preco
from radar.imoveis.modelo import Imovel, bairro_alvo

URL = "https://www.vivareal.com.br/aluguel/bahia/feira-de-santana/bairros/{slug}/?precoMaximo={teto}"

# Para cada link de anúncio, sobe até o card que contém o preço.
JS_CARDS = """() => {
  const vistos = new Set(), cards = [];
  for (const a of document.querySelectorAll('a[href*="/imovel/"]')) {
    const href = a.href.split('?')[0];
    if (vistos.has(href)) continue;
    vistos.add(href);
    let c = a;
    for (let i = 0; i < 6 && !/R\\$/.test(c.innerText || ''); i++) c = c.parentElement || c;
    const img = a.querySelector('img') || c.querySelector('img');
    cards.push({href, txt: c.innerText || '', img: img ? (img.currentSrc || img.src) : null});
  }
  return cards;
}"""

TIPO_RE = re.compile(r"^(?:aluguel-)?(.+?)-(?:\d+-quartos?|com-|\d+m2|[a-z-]*feira-de-santana)")


def parse_card(site: str, card: dict) -> Imovel | None:
    m_slug = re.search(r"/imovel/([^/]+)/?$", card["href"])
    if not m_slug or "feira-de-santana" not in m_slug.group(1):
        return None
    slug = m_slug.group(1)
    m_id = re.search(r"-id-(\d+)$", slug)
    if not m_id:
        return None
    bairro = bairro_alvo(slug.replace("-", " "))
    if not bairro:
        return None
    m_tipo = TIPO_RE.search(slug)
    m_quartos = re.search(r"-(\d+)-quartos?-", slug)
    m_area = re.search(r"-(\d+)m2-", slug)
    m_rs = re.search(r"-RS(\d+)-", slug)
    preco = extrair_preco(card.get("txt", "")) or (int(m_rs.group(1)) if m_rs else None)
    return Imovel(
        site=site,
        id=m_id.group(1),
        url=card["href"],
        tipo=m_tipo.group(1).replace("-", " ") if m_tipo else "imóvel",
        bairro=bairro,
        preco=preco,
        quartos=int(m_quartos.group(1)) if m_quartos else None,
        area=int(m_area.group(1)) if m_area else None,
        foto=card.get("img"),
    )


def buscar() -> list[Imovel]:
    imoveis, erros = [], []
    for n, slug in enumerate(config.VIVAREAL_BAIRROS):
        if n:
            time.sleep(random.uniform(20, 40))
        try:
            with navegador() as page:
                abrir(page, URL.format(slug=slug, teto=config.ALUGUEL_MAXIMO))
                cards = page.evaluate(JS_CARDS)
        except Bloqueado as erro:
            erros.append(erro)
            continue
        imoveis += [i for c in cards if (i := parse_card("vivareal", c))]
    if len(erros) == len(config.VIVAREAL_BAIRROS):
        raise erros[0]
    return imoveis

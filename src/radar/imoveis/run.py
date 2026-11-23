"""Executa uma rodada da busca de imóveis e avisa no Telegram."""

import traceback

from radar import config
from radar.comum.memoria import Memoria
from radar.comum.telegram import Telegram
from radar.imoveis import olx, vivareal
from radar.imoveis.modelo import Imovel, interessa

BUSCAS = {
    "olx": olx.buscar,
    "vivareal": vivareal.buscar,
}


def rodar(simular: bool = False, sites: list[str] | None = None) -> None:
    bot = Telegram("IMOVEIS", simular=simular)
    memoria = Memoria(config.DADOS / "imoveis.json")
    primeira_vez = memoria.primeira_vez

    novos: list[Imovel] = []
    for site in sites or list(BUSCAS):
        try:
            encontrados = [i for i in BUSCAS[site]() if interessa(i)]
        except Exception as erro:
            falhas = memoria.registrar_falha(site)
            print(f"[{site}] falhou ({falhas}x seguidas): {erro}")
            traceback.print_exc()
            if falhas == config.FALHAS_PARA_AVISAR:
                bot.texto(f"⚠️ {site} falhou {falhas} vezes seguidas "
                          f"(provável bloqueio). Último erro: {str(erro)[:200]}")
            continue
        if memoria.falhas.get(site, 0) >= config.FALHAS_PARA_AVISAR:
            bot.texto(f"✅ {site} voltou a funcionar.")
        memoria.registrar_sucesso(site)
        print(f"[{site}] {len(encontrados)} anúncios nos bairros")
        for imovel in encontrados:
            if not memoria.ja_viu(imovel.chave):
                memoria.marcar(imovel.chave)
                novos.append(imovel)

    if simular:
        for imovel in novos:
            print(f"  {imovel.chave} | {imovel.legenda()}\n")

    if primeira_vez:
        # Não inunda o grupo: manda um resumo e só avisa novidades a partir daqui.
        por_bairro: dict[str, int] = {}
        for i in novos:
            por_bairro[i.bairro] = por_bairro.get(i.bairro, 0) + 1
        linhas = "\n".join(f"• {b}: {n}" for b, n in sorted(por_bairro.items()))
        bot.texto(f"🏠 Radar de imóveis ligado! Já existem {len(novos)} anúncios "
                  f"até R$ {config.ALUGUEL_MAXIMO} nos bairros:\n{linhas or '• nenhum'}\n\n"
                  "A partir de agora aviso cada anúncio novo.")
    else:
        for imovel in novos:
            bot.foto(imovel.foto, imovel.legenda())

    if not simular:
        memoria.salvar()
    print(f"{len(novos)} novos{' (simulação, nada salvo)' if simular else ''}")

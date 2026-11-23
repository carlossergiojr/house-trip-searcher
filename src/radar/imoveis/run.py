"""Executa uma rodada da busca de imóveis e avisa no Telegram."""

import time
import traceback
from html import escape

from radar import config
from radar.comum.memoria import Memoria
from radar.comum.telegram import Telegram
from radar.imoveis import olx, vivareal
from radar.imoveis.modelo import Imovel, interessa

BUSCAS = {
    "olx": olx.buscar,
    "vivareal": vivareal.buscar,
}

# O Telegram aceita cerca de 20 mensagens por minuto num grupo.
PAUSA_ENTRE_ENVIOS = 3


def rodar(simular: bool = False, sites: list[str] | None = None, todos: bool = False) -> None:
    """todos=True envia todos os anúncios atuais, mesmo os já vistos."""
    bot = Telegram("IMOVEIS", simular=simular)
    memoria = Memoria(config.DADOS / "imoveis.json")
    try:
        _rodar(bot, memoria, simular, sites or list(BUSCAS), todos)
    finally:
        if not simular:
            memoria.salvar()  # mesmo se algo quebrar no meio, não perde o que já foi feito


def _avisar(bot: Telegram, mensagem: str) -> None:
    """Aviso de bloqueio/volta: se não conseguir enviar, segue a rodada."""
    try:
        bot.texto(mensagem)
    except Exception as erro:
        print(f"[telegram] aviso não enviado: {erro}")


def _rodar(bot: Telegram, memoria: Memoria, simular: bool, sites: list[str], todos: bool) -> None:
    novos: dict[str, Imovel] = {}
    resumos: dict[str, list[Imovel]] = {}  # sites lidos pela primeira vez
    for site in sites:
        if site not in BUSCAS:
            print(f"[{site}] site desconhecido (opções: {', '.join(BUSCAS)})")
            continue
        try:
            encontrados = [i for i in BUSCAS[site]() if interessa(i)]
        except Exception as erro:
            falhas = memoria.registrar_falha(site)
            print(f"[{site}] falhou ({falhas}x seguidas): {erro}")
            traceback.print_exc()
            if falhas == config.FALHAS_PARA_AVISAR:
                _avisar(bot, f"⚠️ {site} falhou {falhas} vezes seguidas "
                             f"(provável bloqueio). Último erro: {escape(str(erro)[:200])}")
            continue
        if memoria.falhas.get(site, 0) >= config.FALHAS_PARA_AVISAR:
            _avisar(bot, f"✅ {site} voltou a funcionar.")
        memoria.registrar_sucesso(site)
        print(f"[{site}] {len(encontrados)} anúncios nos bairros")
        if not memoria.iniciado(site):
            memoria.iniciar(site)
            if not todos:
                # Primeira leitura do site: não inunda o grupo, só resume o que já existe.
                for imovel in encontrados:
                    memoria.marcar(imovel.chave)
                resumos[site] = encontrados
                continue
        for imovel in encontrados:
            if todos or not memoria.ja_viu(imovel.chave):
                novos[imovel.chave] = imovel

    if resumos:
        existentes = [i for lista in resumos.values() for i in lista]
        por_bairro: dict[str, int] = {}
        for i in existentes:
            por_bairro[i.bairro] = por_bairro.get(i.bairro, 0) + 1
        linhas = "\n".join(f"• {b}: {n}" for b, n in sorted(por_bairro.items()))
        _avisar(bot, f"🏠 Radar de imóveis ligado ({', '.join(resumos)})! Já existem "
                     f"{len(existentes)} anúncios até R$ {config.ALUGUEL_BUSCA} nos bairros:\n"
                     f"{linhas or '• nenhum'}\n\nA partir de agora aviso cada anúncio novo.")

    enviados = 0
    for n, imovel in enumerate(novos.values()):
        if simular:
            print(f"  {imovel.chave}")
        elif n:
            time.sleep(PAUSA_ENTRE_ENVIOS)
        try:
            bot.foto(imovel.foto, imovel.legenda())
        except Exception as erro:
            print(f"[telegram] falhou ao enviar {imovel.chave}: {erro}. "
                  "Os que faltam vão na próxima rodada.")
            break
        # Só marca como visto depois de enviado: se falhar, tenta de novo na próxima hora.
        memoria.marcar(imovel.chave)
        enviados += 1
        if not simular:
            memoria.salvar()
    print(f"{enviados} de {len(novos)} novos enviados"
          f"{' (simulação, nada salvo)' if simular else ''}")

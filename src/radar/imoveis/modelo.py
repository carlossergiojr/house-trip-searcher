from dataclasses import dataclass
from html import escape

from radar import config
from radar.comum.texto import normalizar


@dataclass
class Imovel:
    site: str
    id: str
    url: str
    tipo: str
    bairro: str  # nome como em config.BAIRROS
    preco: int | None
    quartos: int | None = None
    area: int | None = None
    foto: str | None = None

    @property
    def chave(self) -> str:
        return f"{self.site}:{self.id}"

    def legenda(self) -> str:
        detalhes = [self.tipo.capitalize()]
        if self.quartos:
            detalhes.append(f"{self.quartos} quarto{'s' if self.quartos > 1 else ''}")
        if self.area:
            detalhes.append(f"{self.area} m²")
        preco = f"R$ {self.preco:,}".replace(",", ".") if self.preco else "preço não informado"
        return (
            f"🏠 <b>Novo imóvel — {escape(self.bairro)}</b>\n"
            f"{escape(' · '.join(detalhes))}\n"
            f"💰 {preco}/mês\n"
            f"🔗 <a href=\"{escape(self.url)}\">ver no {escape(self.site)}</a>"
        )


def bairro_alvo(texto: str) -> str | None:
    """Nome do bairro de interesse mencionado no texto, ou None."""
    alvo = f" {normalizar(texto)} "
    for nome, variacoes in config.BAIRROS.items():
        if any(f" {v} " in alvo for v in variacoes):
            return nome
    return None


def eh_residencial(tipo: str) -> bool:
    t = normalizar(tipo)
    return "comercial" not in t and any(t.startswith(p) for p in config.TIPOS_RESIDENCIAIS)


def interessa(imovel: Imovel) -> bool:
    return (
        eh_residencial(imovel.tipo)
        and (imovel.preco is None or imovel.preco <= config.ALUGUEL_MAXIMO)
    )

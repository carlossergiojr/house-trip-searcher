from dataclasses import dataclass
from html import escape

from radar import config
from radar.comum.texto import normalizar


ROTULO_CONDOMINIO = r"cond(?:om[ií]nio)?"
ROTULO_IPTU = r"iptu"


def reais(valor: int) -> str:
    return f"R$ {valor:,}".replace(",", ".")


@dataclass
class Imovel:
    site: str
    id: str
    url: str
    tipo: str
    bairro: str  # nome como em config.BAIRROS
    preco: int | None  # aluguel
    quartos: int | None = None
    area: int | None = None
    foto: str | None = None
    banheiros: int | None = None
    vagas: int | None = None
    condominio: int | None = None  # 0 = isento, None = não informado
    iptu: int | None = None
    endereco: str | None = None

    @property
    def chave(self) -> str:
        return f"{self.site}:{self.id}"

    @property
    def total(self) -> int | None:
        """Aluguel + condomínio + IPTU (o que não foi informado conta como 0)."""
        if self.preco is None:
            return None
        return self.preco + (self.condominio or 0) + (self.iptu or 0)

    def legenda(self) -> str:
        detalhes = [self.tipo.capitalize()]
        for valor, nome in [(self.quartos, "quarto"), (self.banheiros, "banheiro"),
                            (self.vagas, "vaga")]:
            if valor:
                detalhes.append(f"{valor} {nome}{'s' if valor > 1 else ''}")
        if self.area:
            detalhes.append(f"{self.area} m²")
        linhas = [f"🏠 <b>Novo imóvel — {escape(self.bairro)}</b>",
                  escape(" · ".join(detalhes))]
        if self.endereco:
            linhas.append(f"📍 {escape(self.endereco)}")
        if self.preco:
            linhas.append(f"💰 {reais(self.preco)}/mês")
            taxas = [f"{nome} {'isento' if v == 0 else reais(v) if v else 'não informado'}"
                     for nome, v in [("Cond.", self.condominio), ("IPTU", self.iptu)]]
            linhas.append(f"     {' · '.join(taxas)}")
            if self.total != self.preco:
                linhas.append(f"🧾 Total ≈ <b>{reais(self.total)}</b>/mês")
            if self.total > config.ALUGUEL_MAXIMO:
                linhas.append(f"⚠️ Acima do teto de {reais(config.ALUGUEL_MAXIMO)}")
        else:
            linhas.append("💰 preço não informado")
        linhas.append(f"🔗 <a href=\"{escape(self.url)}\">ver no {escape(self.site)}</a>")
        return "\n".join(linhas)


# Palavras que, antes do nome, indicam outro bairro ("Parque Brasília" não é o Brasília).
PREFIXOS_DE_OUTRO_BAIRRO = {"parque", "jardim", "vila", "residencial", "loteamento",
                            "recanto", "nova", "novo"}


def bairro_alvo(texto: str) -> str | None:
    """Nome do bairro de interesse mencionado no texto, ou None."""
    palavras = normalizar(texto).split()
    for nome, variacoes in config.BAIRROS.items():
        for variacao in variacoes:
            v = variacao.split()
            for k in range(len(palavras) - len(v) + 1):
                if palavras[k:k + len(v)] == v and (
                        k == 0 or palavras[k - 1] not in PREFIXOS_DE_OUTRO_BAIRRO):
                    return nome
    return None


def eh_residencial(tipo: str) -> bool:
    t = normalizar(tipo)
    return "comercial" not in t and any(t.startswith(p) for p in config.TIPOS_RESIDENCIAIS)


def interessa(imovel: Imovel) -> bool:
    return (
        eh_residencial(imovel.tipo)
        and (imovel.preco is None or imovel.preco <= config.ALUGUEL_BUSCA)
    )

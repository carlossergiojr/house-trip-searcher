import re
import unicodedata


def normalizar(texto: str) -> str:
    """Minúsculas, sem acento, só letras/números separados por espaço."""
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", sem_acento.lower()).strip()


def precos(texto: str) -> list[int]:
    """Todos os valores 'R$ 1.234' do texto, em ordem (centavos ignorados)."""
    return [int(v.replace(".", "")) for v in re.findall(r"R\$\s*(\d[\d.]*)", texto)]


def taxa(texto: str, rotulo: str) -> int | None:
    """Valor de uma taxa rotulada ('Cond. R$ 200', 'IPTU isento'): isento = 0, sem valor = None."""
    m = re.search(rf"{rotulo}\.?\s*(?:R\$\s*(\d[\d.]*)|(isento))", texto, re.I)
    if not m:
        return None
    return int(m.group(1).replace(".", "")) if m.group(1) else 0


def extrair_preco(texto: str) -> int | None:
    """Primeiro valor 'R$ 1.234' do texto (o aluguel vem antes de condomínio/IPTU)."""
    valores = precos(texto)
    return valores[0] if valores else None

import re
import unicodedata


def normalizar(texto: str) -> str:
    """Minúsculas, sem acento, só letras/números separados por espaço."""
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", sem_acento.lower()).strip()


def extrair_preco(texto: str) -> int | None:
    """Primeiro valor 'R$ 1.234' do texto (o aluguel vem antes de condomínio/IPTU)."""
    m = re.search(r"R\$\s*([\d.]+)", texto)
    return int(m.group(1).replace(".", "")) if m else None

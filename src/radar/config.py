"""Configuração das buscas. Edite aqui para mudar bairros, teto ou tipos."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DADOS = RAIZ / "dados"

# --- Imóveis -----------------------------------------------------------------

CIDADE = "Feira de Santana"
ALUGUEL_MAXIMO = 2500  # teto desejado (aluguel + condomínio + IPTU)
# Busca um pouco acima do teto para sondar; esses anúncios chegam marcados.
ALUGUEL_BUSCA = 2800

# Nome exibido -> variações aceitas (comparadas sem acento e em minúsculas).
BAIRROS = {
    "Brasília": ["brasilia"],
    "Santa Mônica": ["santa monica"],
    "Lagoa Salgada": ["lagoa salgada"],
    "Conjunto Luiz Eduardo": ["luiz eduardo", "luis eduardo"],
    "Jomafa": ["jomafa"],
}

# Slugs dos bairros no VivaReal (Luiz Eduardo e Jomafa não existem lá: só OLX).
VIVAREAL_BAIRROS = ["brasilia", "santa-monica", "lagoa-salgada"]

# Tipos residenciais aceitos (prefixos do tipo do anúncio, sem acento).
TIPOS_RESIDENCIAIS = [
    "apartamento",
    "casa",
    "sobrado",
    "kitnet",
    "quitinete",
    "flat",
    "cobertura",
]

# Quantas páginas de resultado ler na OLX a cada execução (por categoria).
PAGINAS_POR_SITE = 1  # 50 anúncios mais recentes por categoria, de hora em hora

# Após quantas falhas seguidas de um site o bot avisa no Telegram.
FALHAS_PARA_AVISAR = 3

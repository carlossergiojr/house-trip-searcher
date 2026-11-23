"""Estado persistente em JSON: ids já vistos e falhas seguidas por site."""

import json
from pathlib import Path


class Memoria:
    def __init__(self, caminho: Path):
        self.caminho = caminho
        if caminho.exists():
            dados = json.loads(caminho.read_text())
        else:
            dados = {}
        self.vistos: set[str] = set(dados.get("vistos", []))
        self.falhas: dict[str, int] = dados.get("falhas", {})
        self.primeira_vez = not caminho.exists()

    def ja_viu(self, chave: str) -> bool:
        return chave in self.vistos

    def marcar(self, chave: str) -> None:
        self.vistos.add(chave)

    def registrar_falha(self, site: str) -> int:
        self.falhas[site] = self.falhas.get(site, 0) + 1
        return self.falhas[site]

    def registrar_sucesso(self, site: str) -> None:
        self.falhas[site] = 0

    def salvar(self) -> None:
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.caminho.with_suffix(".tmp")
        tmp.write_text(json.dumps({"vistos": sorted(self.vistos), "falhas": self.falhas}, indent=1))
        tmp.replace(self.caminho)

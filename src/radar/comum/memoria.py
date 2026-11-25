"""Estado persistente em JSON: ids já vistos, falhas seguidas, sites já iniciados e o
contador do dia (para o resumo diário)."""

import json
from pathlib import Path


class Memoria:
    def __init__(self, caminho: Path):
        self.caminho = caminho
        dados = json.loads(caminho.read_text()) if caminho.exists() else {}
        self.vistos: set[str] = set(dados.get("vistos", []))
        self.falhas: dict[str, int] = dados.get("falhas", {})
        # Sites que já tiveram a primeira leitura (resumo enviado). Arquivos antigos não
        # tinham esse campo: vale todo site que já rodou com sucesso.
        self.iniciados: set[str] = set(
            dados.get("iniciados", [s for s, n in self.falhas.items() if n == 0]))
        # {"data": "2026-11-25", "rodadas": 3, "primeira": "06:07", "ultima": "08:07",
        #  "novos": 1, "sites": {"olx": {"ok": 3, "falhas": 0}}, "resumo_enviado": false}
        self.dia: dict = dados.get("dia", {})

    def ja_viu(self, chave: str) -> bool:
        return chave in self.vistos

    def marcar(self, chave: str) -> None:
        self.vistos.add(chave)

    def iniciado(self, site: str) -> bool:
        return site in self.iniciados

    def iniciar(self, site: str) -> None:
        self.iniciados.add(site)

    def registrar_falha(self, site: str) -> int:
        self.falhas[site] = self.falhas.get(site, 0) + 1
        return self.falhas[site]

    def registrar_sucesso(self, site: str) -> None:
        self.falhas[site] = 0

    def salvar(self) -> None:
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.caminho.with_suffix(".tmp")
        tmp.write_text(json.dumps({"vistos": sorted(self.vistos), "falhas": self.falhas,
                                   "iniciados": sorted(self.iniciados), "dia": self.dia}, indent=1))
        tmp.replace(self.caminho)

"""Chromium escondido (Playwright). Os sites bloqueiam requisições simples (403)."""

import random
from contextlib import contextmanager

from playwright.sync_api import Error as ErroPlaywright
from playwright.sync_api import Page, sync_playwright

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
)


class Bloqueado(Exception):
    pass


# Falhas de uma página (bloqueio, timeout, layout): a busca segue para a próxima.
ERROS_DE_PAGINA = (Bloqueado, RuntimeError, ErroPlaywright)


@contextmanager
def navegador():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(locale="pt-BR", user_agent=USER_AGENT,
                                  viewport={"width": 1366, "height": 900})
        try:
            yield ctx.new_page()
        finally:
            browser.close()


def abrir(page: Page, url: str) -> None:
    """Abre a página com pausa aleatória antes (evita bloqueio por excesso)."""
    page.wait_for_timeout(random.uniform(3000, 8000))
    resp = page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)  # anúncios carregam depois do HTML
    if resp is None or resp.status >= 400:
        raise Bloqueado(f"HTTP {resp.status if resp else '?'} em {url}")


def rolar_ate_o_fim(page: Page) -> None:
    """Rola a página aos poucos: alguns sites só montam o card quando ele aparece na tela."""
    for _ in range(40):
        no_fim = page.evaluate(
            "() => { window.scrollBy(0, 800);"
            " return window.innerHeight + window.scrollY >= document.body.scrollHeight - 10; }"
        )
        page.wait_for_timeout(250)
        if no_fim:
            break
    page.wait_for_timeout(1000)

# Radar de imóveis: design

**Objetivo:** o casal procura casa para alugar em Feira de Santana. O robô avisa no Telegram quando aparece um anúncio novo nos bairros de interesse, para não precisarem olhar os sites todo dia.

## Escopo

- **Faz:**
  - Busca nos bairros Brasília, Santa Mônica, Lagoa Salgada, Conjunto Luiz Eduardo e Jomafa.
  - Considera aluguel de até R$ 2.500. Esse teto serve para sondar, não é um limite rígido.
  - Aceita só imóveis residenciais.
  - Roda de hora em hora.
  - Manda um aviso por anúncio novo, uma única vez.
- **Não faz (por enquanto):**
  - Viagens.
  - Piso de preço.
  - Aviso de queda de preço.
- **Evitar:**
  - Encher o grupo de mensagens. Por isso, a primeira execução manda só um resumo.
  - Ficar quebrado sem ninguém saber. Por isso, o bot avisa depois de 3 falhas seguidas.

## Abordagens consideradas

| Abordagem | Vantagens e desvantagens | Escolha |
|---|---|---|
| A. Python + Playwright no PC, rodando pelo cron | Usa o IP de casa, então passa pelos bloqueios. Só roda com o PC ligado. | **Escolhida** |
| B. GitHub Actions | Grátis e roda 24h. Os IPs de datacenter tendem a ser bloqueados. | Pode ser testado depois |
| C. Serviço pago (Firecrawl ou Apify) | O mais confiável contra bloqueios. Custa dinheiro. | Não |

Uma requisição HTTP simples recebe 403 da OLX, do ZAP e do VivaReal. Por isso foi preciso usar um navegador real.

## Decisões

- **Repositório:** um só para casa e viagem.
  - `comum/` guarda o Telegram, a memória e o navegador.
  - `imoveis/` e `viagens/` ficam separados.
- **Telegram:** um bot (ou grupo) por tema. As variáveis seguem o padrão `<TEMA>_BOT_TOKEN` e `<TEMA>_CHAT_ID`.
- **OLX:** lê as categorias casas e apartamentos da cidade, das mais recentes para as mais antigas (`sf=1`), 2 páginas de cada. O bairro vem do card do anúncio.
- **VivaReal:** abre uma página por bairro, cada uma num navegador novo, com pausa de 20 a 40 s entre elas. Em sequência rápida o site devolve 403. A URL do anúncio já traz tipo, quartos, área, preço e id.
- **ZAP:** ficou de fora porque mostra os mesmos anúncios do VivaReal. Além disso, a busca da cidade inteira só traz 30 dos cerca de 360 anúncios, quase nenhum nos bairros de interesse.
- **Luiz Eduardo e Jomafa:** não existem como bairro no VivaReal (a página dá 404), então só chegam pela OLX.
- **Estado:** fica em `dados/imoveis.json`, que não vai para o git.

# Radar (casa + viagem)

Robô que roda de hora em hora no seu PC e manda no Telegram os anúncios novos de
imóveis para alugar em Feira de Santana. A parte de viagens entra depois.

## O que ele busca

Configurado em [`src/radar/config.py`](src/radar/config.py):

- **Bairros:** Brasília, Santa Mônica, Lagoa Salgada, Conjunto Luiz Eduardo, Jomafa
- **Aluguel máximo:** R$ 2.500
- **Tipos:** só residenciais (casa, apartamento, casa de condomínio...). Pontos, salas e galpões são descartados.
- **Sites:**
  - **OLX:** categorias casas e apartamentos da cidade, filtradas por bairro.
  - **VivaReal:** página de cada bairro. Luiz Eduardo e Jomafa não existem como bairro no VivaReal, então só chegam pela OLX.
  - O ZAP não é lido porque mostra os mesmos anúncios do VivaReal.

Na primeira execução ele manda só um resumo ("já existem X anúncios"). Depois disso, manda cada anúncio novo, com foto, uma única vez.

## Instalação

```bash
uv sync
uv run playwright install chromium
cp .env.example .env   # se ainda não existir
```

## Criar o bot do Telegram

1. No Telegram, abra o **@BotFather** (selo azul) e mande `/newbot`.
2. Escolha um nome (ex.: `Radar Casa`) e um usuário terminado em `bot` (ex.: `radar_casa_carlos_bot`).
3. Copie o **token** que ele mandar para a linha `IMOVEIS_BOT_TOKEN=` do `.env`. Não compartilhe esse token.
4. Crie um grupo com quem deve receber os avisos e adicione o bot nele.
5. Mande qualquer mensagem no grupo (ex.: `oi`).
6. Rode o comando abaixo. Ele descobre o id do grupo e grava no `.env`:

   ```bash
   uv run radar descobrir-chat IMOVEIS
   ```

## Uso

```bash
uv run radar imoveis --simular          # mostra no terminal, não envia nem salva
uv run radar imoveis                    # roda de verdade
uv run radar imoveis --sites olx        # só um site
```

## Rodar de hora em hora (cron)

```bash
crontab -e
```

Adicione a linha (o minuto 17 evita horário cheio):

```
17 * * * * /home/clsc/code/projetos/my-git/house-trip-searcher/scripts/rodar-imoveis.sh
```

- **Log:** `logs/imoveis.log`
- **Anúncios já vistos:** `dados/imoveis.json`. Apague esse arquivo para recomeçar do zero.
- **Avisos de bloqueio:** se um site falhar 3 vezes seguidas, o bot avisa no grupo, e avisa de novo quando ele voltar a funcionar.

## Testes

```bash
uv run pytest
```

# Radar (casa + viagem)

Robô que roda de hora em hora no seu PC e manda no Telegram os anúncios novos de
imóveis para alugar em Feira de Santana. A parte de viagens entra depois.

## O que ele busca

Configurado em [`src/radar/config.py`](src/radar/config.py):

- **Bairros:** Brasília, Santa Mônica, Lagoa Salgada, Conjunto Luiz Eduardo, Jomafa
- **Teto:** R$ 2.500 somando aluguel, condomínio e IPTU. A busca vai até R$ 2.800 de aluguel para sondar. O que passa do teto chega marcado com ⚠️.
- **Mensagem:** foto, tipo, quartos, banheiros, vagas, área, rua (no VivaReal), aluguel, condomínio, IPTU e total.
- **Tipos:** só residenciais (casa, apartamento, casa de condomínio...). Pontos, salas e galpões são descartados.
- **Sites:**
  - **OLX:** categorias casas e apartamentos da cidade, filtradas por bairro.
  - **VivaReal:** página de cada bairro. Luiz Eduardo e Jomafa não existem como bairro no VivaReal, então só chegam pela OLX.
  - O ZAP não é lido porque mostra os mesmos anúncios do VivaReal.

Na primeira vez que lê cada site ele manda só um resumo ("já existem X anúncios"). Depois disso, manda cada anúncio novo, com foto, uma única vez. Se o Telegram falhar no meio do envio, os anúncios que faltaram vão na rodada seguinte.

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
uv run radar imoveis --todos            # reenvia todos os anúncios atuais
```

## Rodar na nuvem (GitHub Actions)

O workflow [`.github/workflows/radar-imoveis.yml`](.github/workflows/radar-imoveis.yml) roda de hora em hora no minuto 7, sem precisar do PC ligado.

1. Em **Settings → Secrets and variables → Actions**, crie os secrets `IMOVEIS_BOT_TOKEN` e `IMOVEIS_CHAT_ID` com os mesmos valores do `.env`.
2. Na aba **Actions**, abra "Radar de imóveis" e clique em **Run workflow** para testar.
3. Se funcionar, desligue o cron local (abaixo). Os dois juntos têm estados separados e mandam anúncios repetidos.

- **Log:** na própria execução, na aba Actions.
- **Anúncios já vistos:** `dados/imoveis.json`, salvo no repositório por um commit automático sempre que muda. Faça `git pull` antes de mexer no projeto.
- **Bloqueio:** os sites podem bloquear os IPs do GitHub. Nesse caso o bot avisa no grupo depois de 3 falhas seguidas.

## Rodar de hora em hora no PC (cron)

```bash
crontab -e
```

Adicione as linhas (toda hora cheia e 3 min após ligar o PC):

```
0 * * * * /home/clsc/code/projetos/my-git/house-trip-searcher/scripts/rodar-imoveis.sh
@reboot sleep 180 && /home/clsc/code/projetos/my-git/house-trip-searcher/scripts/rodar-imoveis.sh
```

- **Log:** `logs/imoveis.log`
- **Anúncios já vistos:** `dados/imoveis.json`. Apague esse arquivo para recomeçar do zero.
- **Avisos de bloqueio:** se um site falhar 3 vezes seguidas, o bot avisa no grupo, e avisa de novo quando ele voltar a funcionar.

## Testes

```bash
uv run pytest
```

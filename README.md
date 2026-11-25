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

**Resumo diário:** na rodada das 22h o bot manda no grupo quantas rodadas fez no dia, quantos anúncios novos achou e se cada site funcionou. Serve para saber que ele está vivo mesmo nos dias sem anúncio novo: **se o resumo não chegar, algo parou** (tablet desligado, GitHub sem rodar...). Se a rodada das 22h falhar, o resumo vai atrasado na primeira rodada do dia seguinte. Horário em `HORA_RESUMO` no `config.py`.

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

O workflow [`.github/workflows/radar-imoveis.yml`](.github/workflows/radar-imoveis.yml) roda a busca sem precisar do PC ligado.

OLX e VivaReal bloqueiam os IPs do GitHub (403). Por isso a internet do workflow sai por um tablet Android de casa, via [Tailscale](https://tailscale.com) (grátis).

Roda de hora em hora das 6h às 22h (06:07, 07:07... 22:07, horário de Feira de Santana). O GitHub pode atrasar execuções agendadas em alguns minutos, e às vezes pula uma.

### Tablet (uma vez)

1. Crie uma conta no Tailscale e ative a verificação em duas etapas.
2. No tablet, instale o app Tailscale, entre na conta e ligue **Run as exit node**.
3. Tire o Tailscale da economia de bateria do Android, para ele não ser fechado em segundo plano.
4. No painel do Tailscale, em **Machines**, aprove o tablet como exit node (menu `...` → **Edit route settings** → **Use as exit node**).

### Regra de acesso

Em **Access controls**, troque o conteúdo pelo de [`docs/tailscale-politica.hujson`](docs/tailscale-politica.hujson). Ela deixa o GitHub usar só a internet do tablet, sem acesso ao tablet nem à rede de casa.

### Login do GitHub no Tailscale (sem chave guardada)

1. No painel do Tailscale, abra **Settings → Trust credentials** → **Credential** → **OpenID Connect**.
2. Issuer: **GitHub Actions**. Subject: `repo:carlossergiojr@134062725/house-trip-searcher@1468863367:ref:refs/heads/main`. O GitHub inclui os ids numéricos do dono e do repositório; se o login falhar, a página da credencial mostra o subject recebido ("Received ...").
3. Escopo: **Auth Keys** com escrita, tag `tag:ci`. Gere e copie o **Client ID** e o **Audience**.

### Secrets do GitHub

Em **Settings → Secrets and variables → Actions**:

| Secret | Valor |
|---|---|
| `IMOVEIS_BOT_TOKEN`, `IMOVEIS_CHAT_ID` | os mesmos do `.env` |
| `TS_OAUTH_CLIENT_ID` | Client ID do passo anterior |
| `TS_AUDIENCE` | Audience do passo anterior |
| `TS_EXIT_NODE` | IP do tablet no Tailscale (100.x.y.z, aparece no app) |

### Testar

Na aba **Actions**, abra "Radar de imóveis" e clique em **Run workflow**. O passo "Conferir saída pela casa" falha se a internet não estiver saindo pelo tablet; nesse caso a busca nem roda.

- **Log:** na própria execução, na aba Actions. O IP de casa nunca é impresso, porque o log é público.
- **Anúncios já vistos e contagem do dia:** `dados/imoveis.json`, salvo no repositório por um commit automático a cada rodada. Faça `git pull` antes de mexer no projeto.
- **Tablet desligado ou fora de casa:** a rodada falha e o GitHub manda e-mail. O aviso no grupo não sai, porque sem o tablet o workflow fica sem internet.

## Rodar de hora em hora no PC (cron)

> Alternativa ao GitHub Actions. Não use os dois ao mesmo tempo: cada um guarda o próprio `dados/imoveis.json` e os anúncios chegariam repetidos.

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

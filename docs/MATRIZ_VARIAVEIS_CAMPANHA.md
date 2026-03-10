# Matriz de Variaveis da Campanha

## Como ler esta tabela

- "Obrigatoria": sem isso a campanha nao opera corretamente.
- "Valor seguro": recomendado para primeira execucao.
- "Impacto": o que muda no comportamento real.

## Variaveis de envio

| Variavel | Obrigatoria | Valor seguro | Impacto |
|---|---|---|---|
| `CAMPAIGN_DRY_RUN` | Sim | `true` | `true` simula; `false` envia real |
| `CAMPAIGN_MAX_CONTACTS` | Sim | `1` | Limita quantos contatos entram por execucao |
| `CAMPAIGN_FORCE_PHONE` | Nao | vazio | Se preenchido, todos envios vao para 1 numero |
| `CAMPAIGN_ID` | Nao | `campanha_teste` | Identifica execucao/log |

## Variaveis de publico

| Variavel | Obrigatoria | Valor seguro | Impacto |
|---|---|---|---|
| `CAMPAIGN_AUDIENCE` | Sim | `clientes` | Filtra `clientes`, `parceiros` ou `todos` |
| `CONTACTS_CSV_PATH` | Sim | `/data/saida/planilha_mestre_segmentada.csv` | Define qual planilha CSV sera lida |

## Variaveis de texto

| Variavel | Obrigatoria | Valor seguro | Impacto |
|---|---|---|---|
| `CAMPAIGN_TEMPLATE_MODE` | Nao | `hogar` | Define conjunto de template no workflow |
| `CAMPAIGN_TEMPLATE_FOCUS` | Nao | `ampolas` | Define foco/tema comercial do texto |
| `CAMPAIGN_GREETING_STRATEGY` | Nao | `rotativo` | Alterna estilo de saudacao |
| `CAMPAIGN_USE_AT_MENTION` | Nao | `false` | Evita dependencia de `@nome` |

## Variaveis de anti-ban e ritmo

| Variavel | Obrigatoria | Valor seguro | Impacto |
|---|---|---|---|
| `CAMPAIGN_DELAY_PROFILE` | Nao | `20-35|40-70|75-120` | Delays variaveis por perfil |
| `CAMPAIGN_DELAY_SWITCH_EVERY` | Nao | `8` | Troca perfil de delay a cada X mensagens |
| `CAMPAIGN_DELAY_MIN_SECONDS` | Nao | `25` | Fallback minimo se profile vazio |
| `CAMPAIGN_DELAY_MAX_SECONDS` | Nao | `45` | Fallback maximo se profile vazio |

## Variaveis de janela horario

| Variavel | Obrigatoria | Valor seguro | Impacto |
|---|---|---|---|
| `CAMPAIGN_START_HOUR` | Nao | `0` | Hora inicial de operacao |
| `CAMPAIGN_END_HOUR` | Nao | `23` | Hora final de operacao |
| `CAMPAIGN_TIMEZONE` | Nao | `America/Sao_Paulo` | Fuso da janela |

## Variaveis de integracao Evolution

| Variavel | Obrigatoria | Valor seguro | Impacto |
|---|---|---|---|
| `EVOLUTION_API_KEY` | Sim | sem default real | Autenticacao na Evolution API |
| `EVOLUTION_INSTANCE` | Sim | sem default real | Define qual WhatsApp envia |
| `EVOLUTION_BASE_URL` | Sim | `http://evolution_api:8080` | Endereco da API de envio |

## Variaveis Google/OpenAI (apenas fluxo Google)

| Variavel | Obrigatoria | Valor seguro | Impacto |
|---|---|---|---|
| `GOOGLE_OAUTH_CLIENT_ID` | Sim (fluxo Google) | sem default real | OAuth n8n |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Sim (fluxo Google) | sem default real | OAuth n8n |
| `LEADS_SHEET_ID` | Sim (fluxo Google) | sem default real | Planilha origem |
| `OPENAI_API_KEY` | Sim (fluxo IA) | sem default real | Geracao de mensagens |

## Perfis prontos sugeridos

### Homologacao

```env
CAMPAIGN_DRY_RUN=true
CAMPAIGN_MAX_CONTACTS=1
CAMPAIGN_FORCE_PHONE=5562999999999
CAMPAIGN_AUDIENCE=clientes
```

### Producao inicial

```env
CAMPAIGN_DRY_RUN=false
CAMPAIGN_MAX_CONTACTS=20
CAMPAIGN_FORCE_PHONE=
CAMPAIGN_AUDIENCE=clientes
CAMPAIGN_GREETING_STRATEGY=rotativo
CAMPAIGN_DELAY_PROFILE=20-35|40-70|75-120
CAMPAIGN_DELAY_SWITCH_EVERY=8
```

### Producao em escala (com monitoramento)

```env
CAMPAIGN_DRY_RUN=false
CAMPAIGN_MAX_CONTACTS=200
CAMPAIGN_FORCE_PHONE=
CAMPAIGN_AUDIENCE=todos
CAMPAIGN_GREETING_STRATEGY=rotativo
CAMPAIGN_DELAY_PROFILE=20-35|40-70|75-120
CAMPAIGN_DELAY_SWITCH_EVERY=8
```

## Regra final de operacao

1. Alterou variavel de campanha? Recrie o n8n.
2. Comando:

```powershell
docker compose up -d --force-recreate n8n
```
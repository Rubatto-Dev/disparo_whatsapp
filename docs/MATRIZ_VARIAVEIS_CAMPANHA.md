# Matriz de Variaveis da Campanha

## Como ler esta tabela

- "Obrigatoria": sem isso a campanha nao opera corretamente.
- "Valor seguro": recomendado para primeira execucao.
- "Impacto": o que muda no comportamento real.

## Variaveis de envio

| Variavel | Obrigatoria | Valor seguro | Impacto |
|---|---|---|---|
| `CAMPAIGN_DRY_RUN` | Sim | `true` | `true` simula; `false` envia real |
| `CAMPAIGN_MAX_CONTACTS` | Sim | `20` | Limita quantos contatos entram por execucao |
| `CAMPAIGN_FORCE_PHONE` | Nao | vazio | Se preenchido, todos envios vao para 1 numero |
| `CAMPAIGN_ID` | Sim | `campanha_teste_20260310` | Identifica campanha e escopo de status |

## Variaveis de publico e segmentacao

| Variavel | Obrigatoria | Valor seguro | Impacto |
|---|---|---|---|
| `CAMPAIGN_AUDIENCE` | Sim | `clientes` | Filtra `clientes`, `parceiros` ou `todos` |
| `CONTACTS_CSV_PATH` | Sim | `/data/saida/planilha_mestre_segmentada.csv` | Define qual CSV sera lido |
| `CAMPAIGN_GROUP_FILTER` | Nao | vazio | Filtra por grupo de origem |
| `CAMPAIGN_TARGET_NAME` | Nao | vazio | Mira nome especifico para validacao |
| `CAMPAIGN_TARGET_GROUP` | Nao | vazio | Mira grupo especifico para validacao |
| `CAMPAIGN_VALIDATION_MODE` | Nao | `name_group` | Estrategia de validacao do alvo |
| `CAMPAIGN_OWNER_FILTER` | Nao | vazio | Filtra por responsavel/origem |
| `CAMPAIGN_SKIP_ADMINS` | Nao | `true` | Evita envio para admins |
| `CAMPAIGN_ALLOW_NON_BR` | Nao | `false` | Aceita numeros nao BR quando habilitado |

## Variaveis de status por campanha (persistencia no CSV)

| Variavel | Obrigatoria | Valor seguro | Impacto |
|---|---|---|---|
| `CAMPAIGN_STATUS_COLUMN` | Sim | `status_campanha` | Coluna principal de status |
| `CAMPAIGN_STATUS_ID_COLUMN` | Sim | `campanha_status_id` | Coluna de id da campanha |
| `CAMPAIGN_STATUS_SCOPE` | Sim | `campaign` | `campaign` respeita status por campanha; `all` global |
| `CAMPAIGN_STATUS_FILTER` | Sim | `nao_enviado` | Define quais status entram na execucao |

## Variaveis de texto

| Variavel | Obrigatoria | Valor seguro | Impacto |
|---|---|---|---|
| `CAMPAIGN_TEMPLATE_MODE` | Nao | `hogar` | Define conjunto de template no workflow |
| `CAMPAIGN_TEMPLATE_FOCUS` | Nao | `imoveis de luxo` | Define foco/tema comercial do texto |
| `CAMPAIGN_GREETING_STRATEGY` | Nao | `rotativo` | Alterna estilo de saudacao |
| `CAMPAIGN_USE_AT_MENTION` | Nao | `false` | Evita dependencia de `@nome` |
| `CAMPAIGN_TICKET_DEFAULT` | Nao | `nao_informado` | Ticket padrao quando contato nao tem faixa |

## Variaveis de anti-ban e ritmo

| Variavel | Obrigatoria | Valor seguro | Impacto |
|---|---|---|---|
| `CAMPAIGN_DELAY_PROFILE` | Nao | `20-35|40-70|75-120` | Delays variaveis por perfil |
| `CAMPAIGN_DELAY_SWITCH_EVERY` | Nao | `8` | Troca perfil de delay a cada X mensagens |
| `CAMPAIGN_DELAY_MIN_SECONDS` | Nao | `25` | Fallback minimo se profile vazio |
| `CAMPAIGN_DELAY_MAX_SECONDS` | Nao | `45` | Fallback maximo se profile vazio |
| `CAMPAIGN_LONG_BREAK_ENABLED` | Nao | `true` | Habilita pausas longas aleatorias |
| `CAMPAIGN_LONG_BREAK_EVERY_MIN` | Nao | `20` | Menor intervalo de mensagens para pausa longa |
| `CAMPAIGN_LONG_BREAK_EVERY_MAX` | Nao | `30` | Maior intervalo de mensagens para pausa longa |
| `CAMPAIGN_LONG_BREAK_MIN_SECONDS` | Nao | `300` | Menor duracao da pausa longa |
| `CAMPAIGN_LONG_BREAK_MAX_SECONDS` | Nao | `720` | Maior duracao da pausa longa |
| `CAMPAIGN_KILL_SWITCH_ERRORS` | Nao | `3` | Para execucao apos X erros consecutivos |
| `CAMPAIGN_ALERT_PHONE` | Nao | vazio | Recebe alerta quando kill switch para a campanha |

## Variaveis de rampa de volume

| Variavel | Obrigatoria | Valor seguro | Impacto |
|---|---|---|---|
| `CAMPAIGN_RAMP_ENABLED` | Nao | `true` | Habilita rampa de volume por dia |
| `CAMPAIGN_RAMP_PROFILE` | Nao | `40|80|150|250|400|600` | Limite por dia de operacao |
| `CAMPAIGN_RAMP_DAY` | Nao | `1` | Dia atual da rampa |

## Variaveis de janela horario

| Variavel | Obrigatoria | Valor seguro | Impacto |
|---|---|---|---|
| `CAMPAIGN_START_HOUR` | Nao | `8` | Hora inicial de operacao |
| `CAMPAIGN_END_HOUR` | Nao | `20` | Hora final de operacao |
| `CAMPAIGN_TIMEZONE` | Nao | `America/Sao_Paulo` | Fuso da janela |

## Variaveis de integracao Evolution

| Variavel | Obrigatoria | Valor seguro | Impacto |
|---|---|---|---|
| `EVOLUTION_API_KEY` | Sim | sem default real | Autenticacao na Evolution API |
| `EVOLUTION_INSTANCE` | Sim | sem default real | Define qual WhatsApp envia |
| `EVOLUTION_BASE_URL` | Sim | `http://evolution_api:8080` | Endereco da API de envio |

## Perfis prontos sugeridos

### Homologacao segura

```env
CAMPAIGN_DRY_RUN=true
CAMPAIGN_MAX_CONTACTS=3
CAMPAIGN_FORCE_PHONE=5562999999999
CAMPAIGN_AUDIENCE=clientes
CAMPAIGN_STATUS_FILTER=nao_enviado
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
CAMPAIGN_LONG_BREAK_ENABLED=true
CAMPAIGN_KILL_SWITCH_ERRORS=3
CAMPAIGN_ALERT_PHONE=5562990000000
CAMPAIGN_RAMP_ENABLED=true
CAMPAIGN_RAMP_PROFILE=40|80|150|250|400|600
CAMPAIGN_RAMP_DAY=1
```

### Producao em escala (com monitoramento)

```env
CAMPAIGN_DRY_RUN=false
CAMPAIGN_MAX_CONTACTS=200
CAMPAIGN_FORCE_PHONE=
CAMPAIGN_AUDIENCE=todos
CAMPAIGN_STATUS_FILTER=nao_enviado
CAMPAIGN_GREETING_STRATEGY=rotativo
CAMPAIGN_DELAY_PROFILE=20-35|40-70|75-120
CAMPAIGN_DELAY_SWITCH_EVERY=8
CAMPAIGN_LONG_BREAK_ENABLED=true
CAMPAIGN_KILL_SWITCH_ERRORS=3
CAMPAIGN_RAMP_ENABLED=true
CAMPAIGN_RAMP_PROFILE=40|80|150|250|400|600
CAMPAIGN_RAMP_DAY=4
```

## Regra final de operacao

1. Alterou variavel de campanha? Recrie o n8n.
2. Comando:

```powershell
docker compose up -d --force-recreate n8n
```

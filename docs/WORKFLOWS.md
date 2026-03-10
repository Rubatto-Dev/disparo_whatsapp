# Mapa de Workflows e Arquivos

## Workflows JSON

### `workflow_planilha_whatsapp_teste.json`

Objetivo:

- ler CSV local
- filtrar contatos validos
- deduplicar por telefone normalizado
- montar mensagem variavel
- enviar por Evolution API

Dependencias:

- `CONTACTS_CSV_PATH`
- `EVOLUTION_BASE_URL`
- `EVOLUTION_API_KEY`
- `EVOLUTION_INSTANCE`
- variaveis `CAMPAIGN_*`

Controles principais:

- `CAMPAIGN_AUDIENCE` (`clientes`, `parceiros`, `todos`)
- `CAMPAIGN_DRY_RUN`
- `CAMPAIGN_FORCE_PHONE`
- `CAMPAIGN_GREETING_STRATEGY`
- `CAMPAIGN_DELAY_PROFILE`
- `CAMPAIGN_DELAY_SWITCH_EVERY`

Contratos fixos:

- enviante = `EVOLUTION_INSTANCE`
- destinatario = planilha (ou `CAMPAIGN_FORCE_PHONE` em homologacao)
- dedupe no lote por telefone normalizado

### `workflow_hogar_evolution.json`

Objetivo:

- ler leads do Google Sheets
- gerar mensagem (quando aplicavel)
- enviar por Evolution API
- gravar status/log em planilha

Dependencias:

- credencial Google Sheets OAuth2 no n8n
- `LEADS_SHEET_ID`
- `OPENAI_API_KEY` (quando houver node de IA)
- `EVOLUTION_*`

## Scripts

### `scripts/consolidar_planilhas.py`

- consolida arquivos de `planilhas/`
- limpa e deduplica contatos
- gera CSVs de saida para operacao

### `scripts/setup_google_sheets.py`

- cria planilha e abas padrao
- importa base
- atualiza `LEADS_SHEET_ID` no `.env`

### `scripts/fix_import.py`

- reimporta base em planilha Google existente

## Infra

### `docker-compose.yml`

Stack principal:

- `n8n`
- `evolution_api`
- `evolution_postgres`
- `evolution_redis`

## Arquivos locais que NAO sobem para Git

- `planilhas/`
- `saida/`
- `.env`
- `google_token.json`
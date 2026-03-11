# Mapa de Workflows e Arquivos

## Workflows JSON

### Matriz operacional

- Teste e producao (CSV local): `workflow_planilha_whatsapp_teste.json`
- Operacao Google Sheets/OpenAI (opcional): `workflow_hogar_evolution.json`

### `workflow_planilha_whatsapp_teste.json`

Objetivo:

- ler CSV local da pasta `saida`
- filtrar contatos validos (audiencia atual: `parceiros`)
- montar mensagem por template com variacao aleatoria
- enviar por Evolution API
- registrar resultado e controlar risco de bloqueio

Dependencias:

- `CONTACTS_CSV_PATH`
- `EVOLUTION_BASE_URL`
- `EVOLUTION_API_KEY`
- `EVOLUTION_INSTANCE`
- controles de campanha (`CAMPAIGN_*`)
- `CAMPAIGN_SEND_LOCK` (trava de envio real)
- `CAMPAIGN_TYPING_*` (simulacao de digitando)

Quando usar:

- operacao local rapida
- teste controlado
- campanha com base ja consolidada em CSV
- operacao com anti-ban ativo (delay variavel + kill switch)

### `workflow_hogar_evolution.json`

Objetivo:

- ler leads do Google Sheets
- filtrar e segmentar
- gerar mensagem via OpenAI
- enviar por Evolution API
- gravar status e logs no Google Sheets

Dependencias:

- Google Sheets OAuth2 no n8n
- `LEADS_SHEET_ID`
- `OPENAI_API_KEY`
- `EVOLUTION_*`

Quando usar:

- operacao rastreavel com status em planilha
- fluxo mais proximo de producao

## Scripts

### `scripts/consolidar_planilhas.py`

Funcao:

- consolida arquivos `.xlsx` e `.csv` de `planilhas/`
- deduplica contatos por telefone
- classifica grupos em `cliente` ou `corretor_parceiro`
- produz arquivos limpos na pasta `saida/`

### `scripts/setup_google_sheets.py`

Funcao:

- cria uma planilha Google do zero
- cria as abas `Leads`, `envios_log` e `envios_erros`
- importa os CSVs preparados
- atualiza `LEADS_SHEET_ID` no `.env`

### `scripts/fix_import.py`

Funcao:

- reimporta os leads em uma planilha ja existente
- usa `LEADS_SHEET_ID` do `.env` ou argumento manual

### `scripts/formatar_planilha_visual.ps1`

Funcao:

- gerar planilha Excel visual a partir de CSV segmentado
- aplicar validacoes, formatacao e guias para revisao operacional

## Compose files

### `docker-compose.yml`

Stack principal:

- `n8n`
- `evolution_api`
- `evolution_postgres`
- `evolution_redis`

## Arquivos locais nao versionados

### `planilhas/`

Contem exportacoes brutas. Nao deve subir ao GitHub.

### `saida/`

Contem CSVs derivados e dados processados. Nao deve subir ao GitHub.

### `.env`

Contem segredos e configuracao local. Nao deve subir ao GitHub.

### `google_token.json`

Contem token OAuth do Google. Nao deve subir ao GitHub.

## Higiene de repositorio

- snapshots de workflow (`workflow_live_*`, `workflow_active_*`) nao sao canonicos e devem ficar fora do Git
- artefatos de execucao (`execution_*.json`, logs de teste, QR temporario) devem ficar fora do Git
- o estado operacional atual deve ser mantido em `docs/SESSION_STATE.md`

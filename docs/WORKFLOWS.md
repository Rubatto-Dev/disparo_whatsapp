# Mapa de Workflows e Arquivos

## Workflows JSON

### `workflow_planilha_whatsapp_teste.json`

Objetivo:

- ler CSV local da pasta `saida`
- filtrar contatos validos
- montar mensagem por template
- enviar por Evolution API

Dependencias:

- `CONTACTS_CSV_PATH`
- `EVOLUTION_BASE_URL`
- `EVOLUTION_API_KEY`
- `EVOLUTION_INSTANCE`
- controles de campanha (`CAMPAIGN_*`)

Contrato operacional:

- o numero enviante vem da `EVOLUTION_INSTANCE`
- o numero destinatario vem do CSV
- `CAMPAIGN_FORCE_PHONE` sobrescreve o destinatario apenas em homologacao
- o workflow preserva numeros com DDI explicito e so adiciona `55` a numeros locais com 10/11 digitos

Quando usar:

- operacao local rapida
- teste controlado
- campanha com base ja consolidada em CSV

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

Contrato operacional:

- o numero enviante vem da `EVOLUTION_INSTANCE`
- o numero destinatario vem da planilha Google
- o workflow preserva numeros com DDI explicito e so adiciona `55` a numeros locais com 10/11 digitos

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

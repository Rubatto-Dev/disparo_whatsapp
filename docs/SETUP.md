# Setup Local

## Objetivo

Subir o projeto em uma maquina nova com o menor numero possivel de decisoes improvisadas.

## Pre-requisitos

Instale antes de comecar:

- Docker Desktop com engine Linux ativo
- Python 3.11+ se for usar os scripts de consolidacao/importacao
- Acesso as credenciais necessarias para o modo de operacao escolhido

Validacoes rapidas:

```powershell
docker --version
docker compose version
python --version
```

## 1. Clonar e preparar variaveis

```powershell
git clone <URL_DO_REPOSITORIO>
cd disparo_whatsapp
Copy-Item .env.example .env
```

Edite `.env` e preencha somente o necessario para o fluxo que sera usado.

Variaveis mais comuns:

- `OPENAI_API_KEY`
- `LEADS_SHEET_ID`
- `LEADS_SHEET_NAME`
- `LEADS_LOG_SHEET_NAME`
- `LEADS_ERROR_SHEET_NAME`
- `GOOGLE_DESKTOP_CLIENT_ID`
- `GOOGLE_DESKTOP_CLIENT_SECRET`
- `EVOLUTION_API_KEY`
- `EVOLUTION_INSTANCE`
- `CONTACTS_CSV_PATH`
- `CAMPAIGN_DRY_RUN`
- `CAMPAIGN_MAX_CONTACTS`
- `CAMPAIGN_START_HOUR`
- `CAMPAIGN_END_HOUR`
- `CAMPAIGN_TIMEZONE`

## 2. Instalar dependencias Python

Se voce vai usar `scripts/setup_google_sheets.py` ou `scripts/fix_import.py`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 3. Subir a stack local

Com o Docker Desktop ja iniciado:

```powershell
docker compose up -d
```

Servicos esperados:

- `n8n`
- `evolution_api`
- `evolution_postgres`
- `evolution_redis`

Verifique:

```powershell
docker compose ps
```

## 4. Abrir o n8n

- URL local: `http://localhost:5678`
- Primeiro acesso: crie o usuario administrativo se o n8n pedir

## 5. Importar o workflow

No Editor do n8n:

1. Abra um workflow vazio.
2. Menu de tres pontos no canto superior direito.
3. `Import from File`.
4. Selecione o JSON do workflow desejado.

Arquivos principais:

- `workflow_planilha_whatsapp_teste.json`
- `workflow_hogar_evolution.json`

## 6. Configurar credenciais no n8n

### Google Sheets OAuth2

Necessario para `workflow_hogar_evolution.json`.

Preencha no n8n:

- Client ID
- Client Secret
- Redirect URI: `http://localhost:5678/rest/oauth2-credential/callback`

### Evolution API

Os workflows deste repositorio usam `apikey` via variavel de ambiente. Garanta no `.env`:

- `EVOLUTION_API_KEY`
- `EVOLUTION_INSTANCE`

### OpenAI

Se o workflow usar geracao de texto:

- `OPENAI_API_KEY`

## 7. Preparar a base de contatos

### Opcao A: planilhas exportadas

Coloque os arquivos em `planilhas/` e rode:

```powershell
python scripts/consolidar_planilhas.py
```

O arquivo padrao esperado pelo workflow local e:

- `saida/planilha_mestre_sem_duplicados.csv`

### Opcao B: Google Sheets

Se quiser criar a planilha do zero:

```powershell
python scripts/setup_google_sheets.py
```

O script:

- abre o OAuth local na primeira execucao
- cria as abas `Leads`, `envios_log` e `envios_erros`
- grava `LEADS_SHEET_ID` no `.env`
- usa `saida/planilha_mestre_sem_duplicados.csv` como fonte padrao quando os CSVs legados de importacao nao existem

## 8. Primeiro teste

Antes de qualquer lote real:

1. Defina `CAMPAIGN_DRY_RUN=true`.
2. Defina `CAMPAIGN_MAX_CONTACTS=3` ou `5`.
3. Se possivel, use `CAMPAIGN_FORCE_PHONE` com um numero controlado.
4. Execute manualmente o workflow no n8n.
5. Verifique a execucao item a item.

## 9. Problemas frequentes

### `docker compose ps` falha

Causa comum: Docker Desktop nao esta iniciado.

### n8n abre, mas o workflow nao le variaveis

Recrie o servico apos editar `.env`:

```powershell
docker compose up -d --force-recreate n8n
```

### Google OAuth nao conecta

Confira no Google Cloud:

- `Google Sheets API` habilitada
- `Google Drive API` habilitada
- redirect URI exatamente igual ao usado no n8n

### Evolution API responde 401/403

Revise:

- `EVOLUTION_API_KEY`
- `EVOLUTION_INSTANCE`
- URL base usada no workflow

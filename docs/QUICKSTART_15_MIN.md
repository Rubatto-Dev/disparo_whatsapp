# Checklist Rapido de 15 Minutos

## Objetivo

Colocar o projeto de pe no notebook da empresa com o menor numero possivel de decisoes no momento da execucao.

## Recomendacao

Se o objetivo e apenas rodar rapido amanha, use primeiro o modo:

- `CSV local + Evolution API`

Esse caminho exige menos configuracao do que o fluxo com Google Sheets e OpenAI.

Use `Google Sheets + OpenAI + Evolution API` somente se voce realmente precisar de leitura e log online em planilha.

## O que levar antes

Tenha estes itens com voce:

1. URL do repositorio GitHub.
2. Valores do `.env` que serao usados no notebook.
3. Arquivo `saida/planilha_mestre_sem_duplicados.csv` se for usar o modo CSV local.
4. Chave `EVOLUTION_API_KEY`.
5. Nome da `EVOLUTION_INSTANCE` que voce quer usar ou criar.
6. Se for usar Google Sheets: `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `LEADS_SHEET_ID`, `OPENAI_API_KEY`.

## Roteiro de 15 minutos

### Minuto 0 a 2

Instale e abra:

- Docker Desktop
- Git
- Python 3.11+ se for usar scripts

Confirme:

```powershell
docker --version
docker compose version
git --version
python --version
```

### Minuto 2 a 4

Clone o repositorio:

```powershell
git clone https://github.com/Rubatto-Dev/disparo_whatsapp.git
cd disparo_whatsapp
Copy-Item .env.example .env
```

### Minuto 4 a 6

Edite o `.env`.

Para o modo CSV local, preencha no minimo:

- `EVOLUTION_API_KEY`
- `EVOLUTION_INSTANCE`
- `CONTACTS_CSV_PATH=/data/saida/planilha_mestre_sem_duplicados.csv`
- `CAMPAIGN_DRY_RUN=true`
- `CAMPAIGN_MAX_CONTACTS=3`
- `CAMPAIGN_FORCE_PHONE=<seu_numero>`

Se for usar Google Sheets, adicione tambem:

- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `N8N_GOOGLE_OAUTH_REDIRECT_URI=http://localhost:5678/rest/oauth2-credential/callback`
- `LEADS_SHEET_ID`
- `OPENAI_API_KEY`

### Minuto 6 a 7

Se for modo CSV local, copie seu arquivo de base para:

```text
disparo_whatsapp\saida\planilha_mestre_sem_duplicados.csv
```

### Minuto 7 a 8

Suba a stack:

```powershell
docker compose up -d
docker compose ps
```

Voce precisa ver:

- `n8n`
- `evolution_api`
- `evolution_postgres`
- `evolution_redis`

### Minuto 8 a 10

Abra no navegador:

- `http://localhost:5678`
- `http://localhost:8080/manager`

No n8n:

1. conclua o cadastro inicial, se aparecer
2. clique em novo workflow
3. menu de tres pontos
4. `Import from File`

Escolha:

- `workflow_planilha_whatsapp_teste.json` para modo CSV local
- `workflow_hogar_evolution.json` para modo Google Sheets

### Minuto 10 a 12

Prepare a Evolution API.

Opcao A:

- usar o manager em `http://localhost:8080/manager`
- criar a instancia
- conectar/obter QR
- escanear no WhatsApp em `Aparelhos conectados`

Opcao B, via API:

```powershell
curl.exe -X POST http://localhost:8080/instance/create `
  -H "apikey: SUA_API_KEY" `
  -H "Content-Type: application/json" `
  -d "{\"instanceName\":\"SUA_INSTANCIA\",\"qrcode\":true,\"integration\":\"WHATSAPP-BAILEYS\"}"

curl.exe -X GET http://localhost:8080/instance/connect/SUA_INSTANCIA `
  -H "apikey: SUA_API_KEY"
```

### Minuto 12 a 13

Se voce importou `workflow_hogar_evolution.json`, no n8n:

1. abra `Credentials`
2. crie `Google Sheets OAuth2`
3. preencha `Client ID` e `Client Secret`
4. clique em `Connect`
5. volte ao workflow
6. abra cada node Google Sheets
7. selecione a credencial criada

Isso e necessario porque o workflow entra importado com placeholder de credencial.

### Minuto 13 a 14

Recrie o n8n para garantir leitura do `.env`:

```powershell
docker compose up -d --force-recreate n8n
```

### Minuto 14 a 15

Execute o workflow manualmente.

Criterio minimo de sucesso:

- workflow abre sem erro de credencial
- modo dry run executa
- modo teste controlado aponta para seu numero
- Evolution responde sem erro de autenticacao

## Depois do quickstart

Quando o dry run estiver bom:

1. mude `CAMPAIGN_DRY_RUN=false`
2. mantenha `CAMPAIGN_FORCE_PHONE=<seu_numero>`
3. execute novamente
4. valide recebimento
5. so depois limpe `CAMPAIGN_FORCE_PHONE`

## Se travar

### Docker nao subiu

Abra o Docker Desktop e espere ficar pronto.

### n8n nao leu variavel nova

```powershell
docker compose up -d --force-recreate n8n
```

### Evolution nao envia

Cheque:

- `EVOLUTION_API_KEY`
- `EVOLUTION_INSTANCE`
- instancia realmente pareada no WhatsApp

### Workflow de planilha falhou

Cheque:

- `LEADS_SHEET_ID`
- credencial Google criada
- nodes Google Sheets apontando para a credencial correta

# Deploy no Notebook da Empresa

## Objetivo

Subir o projeto em um notebook novo com o menor risco e chegar rapido ao primeiro teste controlado.

## O que voce precisa levar

Antes de sair desta maquina, garanta que voce tem:

1. URL do repositorio GitHub.
2. Valores do `.env` que serao usados no notebook.
3. Acesso ao Google Cloud, se for usar o modo Google Sheets.
4. Acesso a Evolution API e a instancia que sera usada.
5. A base local `saida/planilha_mestre_sem_duplicados.csv`, se for usar o modo CSV local.

## Caminho recomendado

Para amanha, o caminho mais simples e previsivel e:

1. subir Docker Desktop
2. clonar o repositorio
3. criar `.env`
4. rodar `docker compose up -d`
5. importar um dos dois workflows oficiais
6. fazer dry run
7. fazer teste controlado

## Passo a passo

### 1. Instalar pre-requisitos

- Docker Desktop
- Python 3.11+ se voce for usar os scripts locais
- Git

### 2. Clonar o repositorio

```powershell
git clone https://github.com/Rubatto-Dev/disparo_whatsapp.git
cd disparo_whatsapp
Copy-Item .env.example .env
```

### 3. Preencher o `.env`

Preencha somente o necessario para o modo escolhido.

#### Modo A: CSV local + Evolution API

Obrigatorios:

- `EVOLUTION_API_KEY`
- `EVOLUTION_INSTANCE`
- `CONTACTS_CSV_PATH`
- `CAMPAIGN_DRY_RUN`
- `CAMPAIGN_MAX_CONTACTS`

Arquivo esperado:

- `saida/planilha_mestre_sem_duplicados.csv`

#### Modo B: Google Sheets + OpenAI + Evolution API

Obrigatorios:

- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `N8N_GOOGLE_OAUTH_REDIRECT_URI`
- `LEADS_SHEET_ID`
- `OPENAI_API_KEY`
- `EVOLUTION_API_KEY`
- `EVOLUTION_INSTANCE`

Se voce for criar a planilha via script:

- `GOOGLE_DESKTOP_CLIENT_ID`
- `GOOGLE_DESKTOP_CLIENT_SECRET`

### 4. Subir a stack

```powershell
docker compose up -d
docker compose ps
```

Voce deve ver:

- `n8n`
- `evolution_api`
- `evolution_postgres`
- `evolution_redis`

### 5. Abrir o n8n

- `http://localhost:5678`

Se for o primeiro acesso, conclua o cadastro inicial.

### 6. Importar o workflow oficial

Arquivos suportados:

- `workflow_planilha_whatsapp_teste.json`
- `workflow_hogar_evolution.json`

No Editor do n8n:

1. novo workflow
2. menu de tres pontos
3. `Import from File`

### 7. Configurar credenciais

#### Google Sheets OAuth2

Necessario somente para `workflow_hogar_evolution.json`.

Use:

- client id web
- client secret web
- redirect URI `http://localhost:5678/rest/oauth2-credential/callback`
- depois da importacao do workflow, abra os nodes Google Sheets e selecione a credencial criada, porque o JSON entra com placeholder de credencial

#### Evolution API

Os workflows usam `apikey` via variavel de ambiente. Verifique:

- `EVOLUTION_API_KEY`
- `EVOLUTION_INSTANCE`

Se a instancia ainda nao existir no notebook, crie e conecte antes do primeiro envio.

Opcao 1: usar o manager da Evolution API em `http://localhost:8080/manager`.

Opcao 2: usar a API diretamente. Fluxo minimo:

1. criar a instancia
2. gerar ou obter o QR code
3. escanear no WhatsApp em `Aparelhos conectados`

Exemplo de criacao da instancia:

```powershell
curl.exe -X POST http://localhost:8080/instance/create `
  -H "apikey: SUA_API_KEY" `
  -H "Content-Type: application/json" `
  -d "{\"instanceName\":\"SUA_INSTANCIA\",\"qrcode\":true,\"integration\":\"WHATSAPP-BAILEYS\"}"
```

Exemplo para solicitar conexao/QR:

```powershell
curl.exe -X GET http://localhost:8080/instance/connect/SUA_INSTANCIA `
  -H "apikey: SUA_API_KEY"
```

Se a resposta vier com `pairingCode` ou `code`, use esse retorno para concluir o pareamento do WhatsApp.

#### OpenAI

Necessario somente para `workflow_hogar_evolution.json`.

- `OPENAI_API_KEY`

### 8. Primeiro teste

Configuracao recomendada:

- `CAMPAIGN_DRY_RUN=true`
- `CAMPAIGN_MAX_CONTACTS=3`
- `CAMPAIGN_FORCE_PHONE=<seu_numero>` quando aplicavel

Depois de editar `.env`, recrie o n8n:

```powershell
docker compose up -d --force-recreate n8n
```

### 9. Teste controlado

Quando o dry run estiver consistente:

1. mude `CAMPAIGN_DRY_RUN=false`
2. mantenha `CAMPAIGN_FORCE_PHONE` apontando para um numero seu
3. execute manualmente o workflow
4. valide o retorno no n8n

### 10. Go-live limitado

Somente depois do teste controlado:

1. limpe `CAMPAIGN_FORCE_PHONE`
2. comece com `CAMPAIGN_MAX_CONTACTS=20`
3. rode manualmente
4. acompanhe a execucao inteira

## Erros mais comuns no notebook

### Docker nao sobe

Abra o Docker Desktop e espere o engine ficar pronto.

### n8n nao le o `.env`

Recrie o container do n8n:

```powershell
docker compose up -d --force-recreate n8n
```

### Google OAuth falha

Revise o redirect URI no Google Cloud e no n8n.

### Evolution API sem instancia conectada

Revise:

- se `EVOLUTION_INSTANCE` no `.env` bate com a instancia criada
- se a instancia foi realmente pareada no WhatsApp
- se o `apikey` enviado e o mesmo definido no compose

### Workflow nao acha a planilha local

Revise:

- existencia de `saida/planilha_mestre_sem_duplicados.csv`
- valor de `CONTACTS_CSV_PATH`
- `N8N_RESTRICT_FILE_ACCESS_TO`

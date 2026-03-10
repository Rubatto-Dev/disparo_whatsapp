# Setup Local

## Objetivo

Subir o projeto em maquina nova com configuracao previsivel.

## Pre-requisitos

- Docker Desktop (engine Linux ativo)
- Git
- Python 3.11+ (apenas para scripts)

Validar:

```powershell
docker --version
docker compose version
python --version
```

## 1) Clonar e preparar `.env`

```powershell
git clone https://github.com/Rubatto-Dev/disparo_whatsapp.git
cd disparo_whatsapp
Copy-Item .env.example .env
```

## 2) Preencher variaveis essenciais

Minimo para workflow CSV local:

- `EVOLUTION_API_KEY`
- `EVOLUTION_INSTANCE`
- `CONTACTS_CSV_PATH=/data/saida/planilha_mestre_segmentada.csv`
- `CAMPAIGN_DRY_RUN=true`
- `CAMPAIGN_MAX_CONTACTS=1`
- `CAMPAIGN_AUDIENCE=clientes`
- `CAMPAIGN_FORCE_PHONE=seu_numero_de_teste`

## 3) Subir stack

```powershell
docker compose up -d
docker compose ps
```

Servicos esperados:

- `n8n`
- `evolution_api`
- `evolution_postgres`
- `evolution_redis`

## 4) Abrir n8n e importar workflow

No n8n (`http://localhost:5678`):

1. Abrir workflow vazio.
2. Menu de tres pontos.
3. `Import from File`.
4. Selecionar `workflow_planilha_whatsapp_teste.json`.

## 5) Confirmar instancia Evolution

```powershell
curl.exe -X GET http://localhost:8080/instance/fetchInstances `
  -H "apikey: SUA_API_KEY"
```

Validar:

- `name` = `EVOLUTION_INSTANCE`
- `connectionStatus` = `open`
- `number` = numero que deve enviar

## 6) Aplicar variaveis apos qualquer alteracao

```powershell
docker compose up -d --force-recreate n8n
```

## 7) Primeiro teste seguro

1. `CAMPAIGN_DRY_RUN=true`
2. `CAMPAIGN_MAX_CONTACTS=1`
3. Executar manualmente no n8n
4. Revisar resultado

## 8) Documentos recomendados

- `docs/GUIA_LEIGOS_OPERACAO_WHATSAPP.md`
- `docs/MATRIZ_VARIAVEIS_CAMPANHA.md`
- `docs/TEMPLATES_E_DADOS_MENSAGEM.md`
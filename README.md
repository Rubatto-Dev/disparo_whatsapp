# Disparo WhatsApp

Repositorio operacional para campanhas WhatsApp com `n8n + Evolution API + PostgreSQL + Redis`.

Este projeto nao e app web. Ele entrega:

1. Preparacao de base (scripts Python).
2. Infra local Docker.
3. Workflows n8n para disparo controlado.

## Estado atual validado

Validacao operacional local concluida em **2026-03-10**:

- stack Docker subiu corretamente
- leitura de CSV validada
- filtro por audiencia (`clientes`, `parceiros`, `todos`) validado
- execucao real controlada validada com `provider_message_id`
- anti-ban com saudacao rotativa, delays por perfil e pausa longa aleatoria aplicado
- kill switch por erros consecutivos com alerta opcional aplicado
- persistencia de status por campanha no CSV aplicada

## Inicio rapido (leigos)

Se voce nao e tecnico, siga esta ordem:

1. [Guia para leigos](docs/GUIA_LEIGOS_OPERACAO_WHATSAPP.md)
2. [Checklist rapido (15 min)](docs/QUICKSTART_15_MIN.md)
3. [Go-live real](docs/GO_LIVE_REAL.md)

## Modos oficiais

### 1) CSV local + Evolution API

Uso para operacao direta com base local.

- Workflow: `workflow_planilha_whatsapp_teste.json`
- Entrada: `CONTACTS_CSV_PATH` (default `/data/saida/planilha_mestre_segmentada.csv`)
- Saida: envio WhatsApp via Evolution API

### 2) Google Sheets + OpenAI + Evolution API

Uso para operacao com planilha online e trilha de status.

- Workflow: `workflow_hogar_evolution.json`
- Dependencias: Google OAuth2 + `OPENAI_API_KEY`

## Regras operacionais criticas

- Numero que envia vem da `EVOLUTION_INSTANCE`.
- Numero de destino vem da planilha.
- `CAMPAIGN_FORCE_PHONE` so para homologacao.
- Em producao, `CAMPAIGN_FORCE_PHONE` deve ficar vazio.
- Sempre iniciar com `CAMPAIGN_DRY_RUN=true`.

## Anti-ban e controle de risco

Configuracoes adicionadas:

- `CAMPAIGN_GREETING_STRATEGY=rotativo`
- `CAMPAIGN_DELAY_PROFILE=20-35|40-70|75-120`
- `CAMPAIGN_DELAY_SWITCH_EVERY=8`
- `CAMPAIGN_USE_AT_MENTION=false`

Filtro de publico:

- `CAMPAIGN_AUDIENCE=clientes`
- `CAMPAIGN_AUDIENCE=parceiros`
- `CAMPAIGN_AUDIENCE=todos`

## Estrutura do projeto

```text
.
|-- docker-compose.yml
|-- workflow_planilha_whatsapp_teste.json
|-- workflow_hogar_evolution.json
|-- scripts/
|-- docs/
|-- .env.example
|-- requirements.txt
```

Pastas/arquivos locais ignorados:

- `planilhas/`
- `saida/`
- `.env`
- `google_token.json`

## Setup resumido

```powershell
git clone https://github.com/Rubatto-Dev/disparo_whatsapp.git
cd disparo_whatsapp
Copy-Item .env.example .env
docker compose up -d
```

Acesse:

- n8n: `http://localhost:5678`
- Evolution manager: `http://localhost:8080/manager`

## Scripts Python

### Consolidar base de contatos

```powershell
python scripts/consolidar_planilhas.py
```

Gera CSVs tratados em `saida/`, incluindo base segmentada para campanha.

### Criar/atualizar Google Sheets

```powershell
python scripts/setup_google_sheets.py
```

### Reimportar leads em planilha existente

```powershell
python scripts/fix_import.py
```

## Documentacao completa

- [Guia para leigos](docs/GUIA_LEIGOS_OPERACAO_WHATSAPP.md)
- [Templates e dados de mensagem](docs/TEMPLATES_E_DADOS_MENSAGEM.md)
- [Matriz de variaveis da campanha](docs/MATRIZ_VARIAVEIS_CAMPANHA.md)
- [Atualizacoes de producao (2026-03-10)](docs/ATUALIZACOES_2026_03_10.md)
- [Setup local](docs/SETUP.md)
- [Checklist rapido de 15 minutos](docs/QUICKSTART_15_MIN.md)
- [Deploy no notebook](docs/DEPLOY_NOTEBOOK.md)
- [Go-live real no notebook](docs/GO_LIVE_REAL.md)
- [Runbook operacional](docs/RUNBOOK.md)
- [Mapa de workflows e arquivos](docs/WORKFLOWS.md)

## Fluxo recomendado para producao

1. Subir stack e validar instancia Evolution.
2. Rodar dry run (`CAMPAIGN_DRY_RUN=true`, `CAMPAIGN_MAX_CONTACTS=1`).
3. Rodar teste real controlado com `CAMPAIGN_FORCE_PHONE`.
4. Limpar `CAMPAIGN_FORCE_PHONE`.
5. Rodar 1 envio real da planilha.
6. Escalar em lotes graduais (20 > 50 > 100 > 200).

## Observacao sobre lotes grandes

A plataforma suporta milhares de contatos, mas operar lote unico muito grande aumenta risco operacional e bloqueio. Use lotes graduais com monitoramento entre execucoes.



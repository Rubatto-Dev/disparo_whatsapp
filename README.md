# Disparo WhatsApp

Repositorio operacional para preparar bases de contatos, subir a stack local (`n8n + Evolution API + PostgreSQL + Redis`) e executar workflows de disparo controlado no WhatsApp.

O projeto nao e um app web tradicional. Ele e um pacote de operacao com tres blocos:

1. Scripts Python para consolidar exportacoes de contatos e preparar CSVs de trabalho.
2. Infra local via Docker Compose para rodar n8n e Evolution API.
3. Workflows n8n em JSON para tres modos oficialmente suportados.

## Estado do repositorio

Este repositorio foi preparado para publicacao segura:

- credenciais locais ficam fora do Git
- dados exportados ficam fora do Git
- artefatos temporarios de execucao ficam fora do Git
- continuidade operacional fica em `docs/SESSION_STATE.md`
- a documentacao abaixo descreve o fluxo recomendado para reinstalacao em outra maquina

Recomendacao de publicacao: repositorio privado.

## Caminho recomendado de operacao

Para subir o projeto em um notebook novo com o menor risco:

1. Clone o repositorio.
2. Crie `.env` a partir de `.env.example`.
3. Instale Docker Desktop e confirme que o daemon esta ativo.
4. Se for usar os scripts de planilha, instale Python 3.11+ e `pip install -r requirements.txt`.
5. Suba a stack com `docker compose up -d`.
6. Abra o n8n em `http://localhost:5678`.
7. Importe o workflow JSON desejado via `Import from File`.
8. Configure as credenciais no n8n e execute um dry run antes de qualquer envio real.

## Modos de operacao

### 1. CSV local + Evolution API

Modo mais direto para operacao local.

- Entrada recomendada em execucao: `CONTACTS_CSV_PATH=/home/node/.n8n-files/planilha_mestre_segmentada_nobom.csv`
- Stack: `docker-compose.yml`
- Workflow principal: `workflow_planilha_whatsapp_teste.json`
- Credenciais: `EVOLUTION_API_KEY`, `EVOLUTION_INSTANCE`
- Controles anti-ban: variacao aleatoria de 4 mensagens, delay variavel, simulacao de digitando, kill switch e trava de envio (`CAMPAIGN_SEND_LOCK`)
- Audiencia atual do fluxo principal: `parceiros`

Uso indicado quando a base de contatos ja esta consolidada localmente.

### 2. Google Sheets + OpenAI + Evolution API

Modo mais estruturado para operacao com planilha online e geracao de mensagem com IA.

- Workflow: `workflow_hogar_evolution.json`
- Credenciais: Google Sheets OAuth2, `OPENAI_API_KEY`, Evolution API

Uso indicado quando o time quer rastreabilidade por status/log em planilha.

### 3. Inbound Webhook + Google Sheets

Modo para tratar respostas recebidas dos contatos.

- Workflow: `workflow_inbound_whatsapp_google_sheets.json`
- Credenciais: Google Sheets OAuth2 no n8n
- Variaveis principais: `INBOUND_*`
- Funcionalidades: deduplicacao de evento, classificacao PT-BR (`positivo/negativo/neutro`), update da aba `Leads`, log de orfaos

Uso indicado quando o time quer bloquear novos disparos apos resposta negativa e manter trilha inbound.

## Estrutura do projeto

```text
.
|-- docker-compose.yml
|-- workflow_hogar_evolution.json
|-- workflow_inbound_whatsapp_google_sheets.json
|-- workflow_planilha_whatsapp_teste.json
|-- scripts/
|-- docs/
|-- .env.example
|-- requirements.txt
```

## Matriz de uso (teste e producao)

### Runtime obrigatorio (teste e producao)

- `docker-compose.yml`
- `.env` (local, nao versionado)
- `workflow_planilha_whatsapp_teste.json` (fluxo CSV local)
- `workflow_inbound_whatsapp_google_sheets.json` (fluxo inbound webhook)
- `saida/` com base de contatos

### Validacao e apoio operacional

- `docs/` (setup, runbook, variaveis, estado)
- `scripts/` (preparo e higienizacao de base)
- `workflow_hogar_evolution.json` (fluxo Google Sheets/OpenAI, quando aplicavel)

### Fora do escopo de runtime

- `.venv/` (ambiente local de desenvolvimento)
- artefatos temporarios de execucao (todos bloqueados por `.gitignore`)

Diretorios locais ignorados pelo Git:

- `planilhas/`
- `saida/`

Arquivos locais ignorados pelo Git:

- `.env`
- `google_token.json`
- `tmp_n8n_execute.json`

## Scripts Python

### Consolidar contatos exportados

```powershell
python scripts/consolidar_planilhas.py
```

Entrada:

- pasta `planilhas/` com arquivos `.xlsx` ou `.csv`

Saida:

- `saida/planilha_mestre_sem_duplicados.csv`
- `saida/planilha_mestre_clean.csv`
- `saida/clientes.csv`
- `saida/corretores_parceiros.csv`
- demais arquivos auxiliares de auditoria

### Criar e popular Google Sheets

```powershell
python scripts/setup_google_sheets.py
```

O script cria a planilha, cria as abas necessarias e atualiza `LEADS_SHEET_ID` no `.env` sem corromper a linha existente. Ele usa por padrao os dados de `saida/planilha_mestre_sem_duplicados.csv` quando os arquivos legados `leads_import_*.csv` nao existirem.

### Reimportar leads em uma planilha existente

```powershell
python scripts/fix_import.py
```

O script usa `LEADS_SHEET_ID` do `.env`. Se necessario, voce tambem pode informar o ID manualmente:

```powershell
python scripts/fix_import.py 1AbCdEfGhIjKlMnOpQrStUvWxYz
```

## Script visual (PowerShell)

### Formatar planilha segmentada para revisao

```powershell
powershell -ExecutionPolicy Bypass -File scripts/formatar_planilha_visual.ps1
```

Gera uma versao `.xlsx` visual da planilha segmentada com validacoes e destaque de campos operacionais.

## Documentacao

- [Indice da documentacao](docs/INDEX.md)
- [Setup local](docs/SETUP.md)
- [Runbook operacional](docs/RUNBOOK.md)
- [Variaveis de ambiente](docs/ENVIRONMENT.md)
- [Mapa de workflows e arquivos](docs/WORKFLOWS.md)

## Observacoes operacionais

- `docker compose up -d` sobe os servicos em background; o Compose le variaveis do `.env` por padrao para interpolacao no arquivo.
- O n8n mantem dados importantes em volume persistente; preserve o volume `n8n_data` entre reinicializacoes.
- Para importar workflows no n8n, use o menu de tres pontos no Editor e escolha `Import from File`.
- Nunca publique `.env`, `google_token.json`, planilhas exportadas ou CSVs gerados.
- O projeto foi reduzido para tres caminhos oficiais (CSV local, Google Sheets+IA, e inbound webhook). Todo o restante foi tratado como legado e removido do repositorio.

## Proximos passos antes de operacao real

1. Confirmar qual modo sera usado amanha.
2. Validar credenciais no notebook da empresa.
3. Fazer um dry run com poucos contatos.
4. So entao liberar lote real.

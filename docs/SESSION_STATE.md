# Session State

## Last update
- Date: 2026-03-25 08:49:08 -03
- Updated by: Codex

## Project context
- Repository: `disparo_whatsapp`
- Workflow id (n8n): `O7QqXPaqJ9vnYy5J`
- Goal: disparo WhatsApp para `corretores/parceiros` com anti-ban.
- Status: **operacao de parceiros/corretores em andamento**, com limpeza de grupos fora de escopo concluida.

## Canonical operational set
- Runtime efetivo atual: `/home/rubatto-dev/docker/n8n/docker-compose.yml` + `.env` (symlink para `disparo_whatsapp/.env`)
- Runtime secundario: `disparo_whatsapp/docker-compose.yml` (stack unificada com Evolution local)
- Workflow operacional: `workflow_google_sheets_status.json` (Google Sheets com controle de status)
- Validation/support: `scripts/` e `docs/`

## Live workflow status (Google Sheets)
- Audience configurada: `parceiros`
- Modo de envio: real (`CAMPAIGN_DRY_RUN=false`)
- Trava de envio: liberada (`CAMPAIGN_SEND_LOCK=false`)
- Numero forcado para teste: `5562983002992` (`CAMPAIGN_FORCE_PHONE`)
- Lote atual de teste: `CAMPAIGN_MAX_CONTACTS=1`
- Campanha atual: `CAMPAIGN_ID=campanha_2026_03_17_teste_controlado`
- Filtro de status: `CAMPAIGN_STATUS_FILTER=nao_enviado`

## Changes applied in this session
- `.env` ajustado para producao de parceiros:
  - `CAMPAIGN_AUDIENCE=parceiros`
  - `CAMPAIGN_FORCE_PHONE=` (vazio)
  - `CAMPAIGN_MAX_CONTACTS=20`
  - `CAMPAIGN_ID=campanha_2026_03_17_parceiros`
- `n8n` recriado com sucesso para carregar variaveis atualizadas.
- Planilha `Leads` (Google Sheets) teve reset de status para parceiros/corretores que estavam `Enviado`:
  - 3 linhas de parceiros alteradas para `Nao Enviado`
  - limpeza de campos de rastreio (`ultimo_envio_em`, `provider_message_id`, `provider_status`, `erro_envio`) nessas mesmas linhas
- Limpeza de grupos fora de escopo concluida na planilha `Leads`:
  - grupos removidos: `FAZENDAS DE LUXO` e `MILFAZENDAS.com.br`
  - linhas removidas nesta etapa: `260`
  - base final apos limpeza: `5858` leads
- Workflow `Disparo WhatsApp - Google Sheets (com controle de status)` ajustado para ordem linear:
  - removida priorizacao por contato com nome/@
  - removida ordenacao por score de validacao
  - agora o envio respeita a ordem original da planilha (de cima para baixo), apos filtros tecnicos obrigatorios
- Novo workflow inbound criado no repositorio: `workflow_inbound_whatsapp_google_sheets.json`
  - trigger por `Webhook` (`INBOUND_WEBHOOK_PATH`)
  - deduplicacao com TTL em `Workflow Static Data` (`INBOUND_DEDUPE_*`)
  - classificacao PT-BR (`positivo`, `negativo`, `neutro`)
  - update de `Leads` por `row_number` com colunas `inbound_*` e `bloquear_envio`
  - append em abas de log inbound (`INBOUND_LOG_SHEET_NAME` e `INBOUND_ORPHAN_SHEET_NAME`)
- Ajuste de robustez no inbound:
  - dedupe migrado para `inbound_dedupe_v2` com chave combinada (`message_id` + texto em janela temporal)
  - checagem de bucket atual e bucket anterior para reduzir duplicidade em borda de janela
  - classificador PT-BR reforcado para reduzir falso negativo/falso positivo em respostas ambiguas
- Nova spec tecnica criada:
  - `docs/specs/SPEC-2026-03-24-INBOUND-N8N-IMPLEMENTACAO-DETALHADA.md`
- Script de validacao inbound adicionado:
  - `scripts/test_inbound_workflow_logic.js`
  - testa localmente classificacao PT-BR e deduplicacao usando os snippets do JSON do workflow inbound
- Runbook e README atualizados com passo de smoke test inbound (script + replay webhook)
- Ajuste de seguranca no observer Evolution:
  - `scripts/evolution_instance_observer.sh` sem default hardcoded para API key
  - observer agora encerra com erro explicito quando `EVOLUTION_API_KEY/API_KEY` nao estiver definido
- Documentacao de observer atualizada:
  - `.env.example` com variaveis `ALERT_*`
  - `docs/ENVIRONMENT.md`, `docs/WORKFLOWS.md`, `docs/RUNBOOK.md` e `README.md`
- Compose observer alinhado:
  - novo servico opcional `evolution_observer` no `docker-compose.yml`
  - removido fallback hardcoded para `EVOLUTION_API_KEY` no compose
- Workflows de disparo (`workflow_google_sheets_status.json` e `workflow_planilha_whatsapp_teste.json`) consolidados:
  - `Filtrar Contatos Validos`: mantida ordem linear da planilha sem reordenacao por score de validacao
  - `Controle Kill Switch`: contagem de erros consecutivos em runtime (`workflow static data`) com tolerancia para erros isolados de rede
  - metadados adicionais no fluxo (`consecutive_errors`, `kill_switch_threshold`, `runtime_key`) para observabilidade

## Validation results
- `docker compose config -q`: OK
- `docker exec n8n env` (vars de campanha): OK
- `fetchInstances` Evolution: instancia `hogar-luxo` aberta com owner `556294594641`
- reset Google Sheets parceiros: OK (`sent_partner` de 3 para 0)
- limpeza dos grupos fazendas: OK (`matches remaining: 0`)
- `workflow_inbound_whatsapp_google_sheets.json`: JSON valido (`jq empty`)
- snippets JS inbound (`Deduplicar Evento (TTL)` e `Classificar Resposta PT-BR`): sintaxe valida (`node -e` + `new Function`)
- `node scripts/test_inbound_workflow_logic.js`: OK
- `bash -n scripts/evolution_instance_observer.sh`: OK
- observer sem API key retorna falha segura (`exit_code=1`): OK
- `docker compose config -q`: OK (com `evolution_observer`)
- `workflow_google_sheets_status.json` e `workflow_planilha_whatsapp_teste.json`: JSON valido (`jq empty`)
- smoke de `Controle Kill Switch` nos dois workflows: OK (para no 3o erro consecutivo nao-rede)

## MCP status
- `sequential-thinking`: ativo e utilizado
- `context7`: ativo e utilizado
- `n8n`, `playwright`, `google-sheets`: registrados

## Pending decision
- Definir momento de voltar de `teste controlado` para `go-live em lote`:
  1. limpar `CAMPAIGN_FORCE_PHONE`
  2. subir `CAMPAIGN_MAX_CONTACTS` para lote de producao
  3. atualizar `CAMPAIGN_ID` para campanha de producao

## Next steps (immediate)
1. Executar 1 teste controlado com destino forcado (`5562983002992`) e validar entrega.
2. Se OK, preparar virada para lote de producao (remover force phone + aumentar max contacts).
3. Monitorar kill switch, provider e status na planilha apos cada lote.

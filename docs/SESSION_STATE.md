# Session State

## Last update
- Date: 2026-03-11 13:10 -03:00
- Updated by: Codex

## Project context
- Repository: `disparo_whatsapp`
- Workflow id (n8n): `OUAfQLqhMta3uqPE`
- Goal: disparo WhatsApp para `corretores/parceiros` com anti-ban.
- Status: **organizado para teste e producao**, com envio em massa sob trava.

## Canonical operational set
- Runtime: `docker-compose.yml`, `.env`, `workflow_planilha_whatsapp_teste.json`, base em `saida/`
- Optional runtime (Google): `workflow_hogar_evolution.json`
- Validation/support: `scripts/` e `docs/`

## Live workflow status (CSV local)
- Audience forced: `parceiros`
- 4 variacoes aleatorias ativas
- Quebra de linha real ativa
- Personalizacao por nome ativa
- Simulacao de digitando ativa (`CAMPAIGN_TYPING_*`)
- Delay variavel + long break ativos
- Kill switch anti-ban ativo
- Safety gate ativo por `CAMPAIGN_SEND_LOCK`

## Critical fix applied in this session
- Alinhado caminho de persistencia CSV no node `Filtrar Contatos Validos` para usar o mesmo criterio do node de leitura (`/home/node/.n8n-files/...`), evitando divergencia entre leitura e escrita.

## Validation results
- `docker compose config -q`: OK
- JSON de workflows: OK
- `python -m py_compile` scripts: OK
- links de docs: OK

## MCP status
- `sequential-thinking`: ativo e em uso
- `context7`: configurado como `context7-mcp.cmd`; runtime MCP ainda com timeout de handshake em 10s nesta sessao
- `n8n`, `playwright`, `google-sheets`: registrados

## Launch runbook (when supervisor is present)
1. `CAMPAIGN_SEND_LOCK=false`
2. `CAMPAIGN_DRY_RUN=false`
3. opcional teste controlado: `CAMPAIGN_FORCE_PHONE=5562994594641`
4. executar e monitorar kill switch/logs
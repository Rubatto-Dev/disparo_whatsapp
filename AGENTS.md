# Project Agent Rules

## Startup Protocol (mandatory every new conversation)

1. Read global protocol first: `C:\Users\Guilherme - Hogar\.codex\memories\GLOBAL_AGENT_PROTOCOL.md`.
2. Read this file (`AGENTS.md`) and `docs/SESSION_STATE.md` before any analysis.
3. Validate current project state with quick checks:
   - `git status --short`
   - `docker compose ps`
   - `codex.cmd mcp list`
   - `docker exec n8n n8n list:workflow` (if `n8n` container is running)
4. First reply must confirm:
   - project context,
   - current objective,
   - active workflow,
   - audience mode (`clientes` or `parceiros`),
   - run mode (`dry run` or real send),
   - anti-ban controls in use.
5. If a required input is missing, ask one direct question before continuing.

## MCP Policy

1. Always use `context7` and `sequential-thinking` for technical tasks (planning, debugging, code/workflow changes).
2. Use additional MCPs when relevant:
   - `n8n` for workflow operations.
   - `playwright` for browser validation and UI automation.
   - `google-sheets` for spreadsheet operations.
3. Do not skip `context7` or `sequential-thinking` in technical execution.

## Continuity Policy

1. Treat `docs/SESSION_STATE.md` as the source of operational continuity.
2. At the end of every substantial session, update `docs/SESSION_STATE.md` with:
   - what changed,
   - current operational status,
   - pending decisions,
   - exact next steps.
3. Never silently override previously agreed operational decisions without explicit confirmation.

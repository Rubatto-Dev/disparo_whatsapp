# Go-Live Real No Notebook

## Objetivo

Executar disparo real com controle de risco e checklist unico.

## Regra principal

- Numero que envia vem da `EVOLUTION_INSTANCE`.
- Numero que recebe vem da planilha.
- `CAMPAIGN_FORCE_PHONE` so para homologacao.

## O que ja foi validado

Validado em 2026-03-09:

- stack Docker operacional
- workflow de CSV funcionando
- envio real retornando `provider_message_id`
- filtro por audiencia funcionando
- saudacao rotativa e delay por perfil funcionando

## Checklist pre-flight

1. Docker Desktop ativo.
2. `docker compose ps` sem falhas.
3. `.env` revisado.
4. `CAMPAIGN_DRY_RUN` coerente com a etapa.
5. `CAMPAIGN_AUDIENCE` definido (`clientes`, `parceiros`, `todos`).
6. `CAMPAIGN_FORCE_PHONE` coerente (preenchido no teste, vazio em producao).
7. Instancia Evolution com `connectionStatus=open`.

## Confirmar numero enviante

```powershell
curl.exe -X GET http://localhost:8080/instance/fetchInstances `
  -H "apikey: SUA_API_KEY"
```

Confirme `name`, `connectionStatus` e `number`.

## Sequencia oficial de liberacao

### Etapa 1 - Dry run

```env
CAMPAIGN_DRY_RUN=true
CAMPAIGN_MAX_CONTACTS=1
CAMPAIGN_AUDIENCE=clientes
CAMPAIGN_FORCE_PHONE=5562999999999
```

Aplicar:

```powershell
docker compose up -d --force-recreate n8n
```

Executar manualmente no n8n e validar texto/filtro.

### Etapa 2 - Teste real controlado

```env
CAMPAIGN_DRY_RUN=false
CAMPAIGN_MAX_CONTACTS=1
CAMPAIGN_AUDIENCE=clientes
CAMPAIGN_FORCE_PHONE=5562999999999
```

Validar:

- mensagem recebida no numero de teste
- `envio_ok=true`
- `provider_message_id` preenchido

### Etapa 3 - Primeiro envio real da planilha

```env
CAMPAIGN_DRY_RUN=false
CAMPAIGN_MAX_CONTACTS=1
CAMPAIGN_AUDIENCE=clientes
CAMPAIGN_FORCE_PHONE=
```

Validar:

- `phone_original` = planilha
- `phone_destino` = planilha
- `provider_message_id` preenchido

### Etapa 4 - Escalar em lotes

Sugestao:

1. 20 contatos
2. 50 contatos
3. 100 contatos
4. 200 contatos

Nao escalar se houver erro repetido.

## Configuracao anti-ban recomendada

```env
CAMPAIGN_GREETING_STRATEGY=rotativo
CAMPAIGN_DELAY_PROFILE=20-35|40-70|75-120
CAMPAIGN_DELAY_SWITCH_EVERY=8
CAMPAIGN_USE_AT_MENTION=false
CAMPAIGN_START_HOUR=0
CAMPAIGN_END_HOUR=23
```

## Rollback imediato

Se algo sair do esperado:

1. Pausar workflow.
2. Voltar `CAMPAIGN_DRY_RUN=true`.
3. Definir `CAMPAIGN_MAX_CONTACTS=1`.
4. Opcional: voltar `CAMPAIGN_FORCE_PHONE` para numero controlado.
5. Recriar n8n.

```powershell
docker compose up -d --force-recreate n8n
```

## Evidencia minima para liberar producao

- Instancia correta aberta no `fetchInstances`.
- 1 teste real controlado entregue.
- 1 envio real da planilha entregue.
- `provider_message_id` registrado no n8n.
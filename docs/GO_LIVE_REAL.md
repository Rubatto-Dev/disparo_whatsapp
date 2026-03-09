# Go-Live Real No Notebook

## Objetivo

Executar o deploy real no notebook da empresa com uma sequencia unica, curta e segura.

## O que foi validado em 2026-03-09

Nesta maquina local, antes do deploy no notebook, foi validado:

- stack Docker ativa com `n8n`, `evolution_api`, `evolution_postgres` e `evolution_redis`
- importacao e execucao do `workflow_planilha_whatsapp_teste.json`
- retorno real de `provider_message_id` pela Evolution API
- `envio_ok=true` no node final de classificacao
- preservacao do numero original vindo da planilha
- confirmacao de que o numero enviante depende da `EVOLUTION_INSTANCE`

## Regra fixa do numero enviante

O numero enviante nunca vem da planilha.

O numero enviante sempre e o WhatsApp pareado na `EVOLUTION_INSTANCE`.

O numero da planilha sempre entra como destinatario, exceto quando `CAMPAIGN_FORCE_PHONE` esta preenchido.

## Checklist de pre-flight no notebook

1. Docker Desktop aberto e engine Linux pronto.
2. Repositorio clonado.
3. `.env` criado a partir de `.env.example`.
4. `EVOLUTION_API_KEY` preenchida.
5. `EVOLUTION_INSTANCE` preenchida.
6. `saida/planilha_mestre_sem_duplicados.csv` presente se o modo for CSV local.
7. Workflow correto importado no n8n.
8. Credenciais Google configuradas se o modo for Google Sheets.

## Confirmar qual numero vai enviar

Antes de qualquer disparo:

```powershell
curl.exe -X GET http://localhost:8080/instance/fetchInstances `
  -H "apikey: SUA_API_KEY"
```

No retorno, confirme:

- `name` igual a `EVOLUTION_INSTANCE`
- `connectionStatus` igual a `open`
- `number` igual ao WhatsApp que deve enviar

## Sequencia recomendada para hoje

### Etapa 1. Dry run

Use:

- `CAMPAIGN_DRY_RUN=true`
- `CAMPAIGN_FORCE_PHONE=<SEU_NUMERO>`
- `CAMPAIGN_MAX_CONTACTS=1`

Depois:

```powershell
docker compose up -d --force-recreate n8n
```

Execute manualmente o workflow e confirme:

- parsing do CSV sem erro
- filtro retorna 1 contato
- mensagem final aceitavel

### Etapa 2. Teste controlado com envio real

Use:

- `CAMPAIGN_DRY_RUN=false`
- `CAMPAIGN_FORCE_PHONE=<SEU_NUMERO>`
- `CAMPAIGN_MAX_CONTACTS=1`

Depois:

```powershell
docker compose up -d --force-recreate n8n
```

Execute manualmente o workflow e confirme no n8n:

- `phone_destino` igual ao seu numero
- `envio_ok=true`
- `envio_status=enviado`
- `provider_message_id` preenchido

### Etapa 3. Primeiro contato real

Use:

- `CAMPAIGN_DRY_RUN=false`
- `CAMPAIGN_FORCE_PHONE=` vazio
- `CAMPAIGN_MAX_CONTACTS=1`

Depois:

```powershell
docker compose up -d --force-recreate n8n
```

Execute manualmente o workflow e confirme no n8n:

- `phone_original` igual ao numero da planilha
- `phone_destino` igual ao numero da planilha
- `envio_ok=true`
- `provider_message_id` preenchido

## Escalada de volume

Somente depois do primeiro contato real:

1. `CAMPAIGN_MAX_CONTACTS=20`
2. validar a execucao inteira
3. `CAMPAIGN_MAX_CONTACTS=50`
4. validar novamente
5. `CAMPAIGN_MAX_CONTACTS=100`

Nao escale se houver repeticao de erro no mesmo bloco.

## Rollback imediato

Se algo sair do esperado:

1. pare a execucao ativa
2. defina `CAMPAIGN_DRY_RUN=true`
3. defina `CAMPAIGN_MAX_CONTACTS=1`
4. se necessario, volte a usar `CAMPAIGN_FORCE_PHONE=<SEU_NUMERO>`
5. recrie o n8n

```powershell
docker compose up -d --force-recreate n8n
```

## Evidencia minima de liberacao

Considere o notebook liberado para operacao real apenas quando houver:

- `fetchInstances` mostrando a instancia correta aberta
- 1 teste controlado entregue ao seu numero
- 1 envio real entregue ao numero vindo da planilha
- `provider_message_id` registrado no n8n

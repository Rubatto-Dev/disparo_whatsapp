# Runbook Operacional

## Objetivo

Executar lotes de envio com previsibilidade, risco controlado e rollback simples.

## Pre-flight obrigatorio

Antes de cada lote, confirmar:

1. Docker Desktop ativo.
2. `docker compose ps` com stack saudavel.
3. `.env` revisado.
4. `CAMPAIGN_DRY_RUN` coerente com etapa.
5. `CAMPAIGN_AUDIENCE` correto para o lote.
6. `CAMPAIGN_FORCE_PHONE` coerente (teste vs producao).
7. Evolution `connectionStatus=open`.
8. Workflow correto ativo no n8n.

## Regras fixas de destino

- Enviante: sempre `EVOLUTION_INSTANCE`.
- Destino: sempre planilha.
- Excecao: `CAMPAIGN_FORCE_PHONE` em homologacao.

## Sequencia de operacao recomendada

### Etapa 1 - Validacao sem envio

```env
CAMPAIGN_DRY_RUN=true
CAMPAIGN_MAX_CONTACTS=1
CAMPAIGN_FORCE_PHONE=5562999999999
```

### Etapa 2 - Teste real controlado

```env
CAMPAIGN_DRY_RUN=false
CAMPAIGN_MAX_CONTACTS=1
CAMPAIGN_FORCE_PHONE=5562999999999
```

### Etapa 3 - Primeiro real da planilha

```env
CAMPAIGN_DRY_RUN=false
CAMPAIGN_MAX_CONTACTS=1
CAMPAIGN_FORCE_PHONE=
```

### Etapa 4 - Escalada gradual

1. `CAMPAIGN_MAX_CONTACTS=20`
2. `CAMPAIGN_MAX_CONTACTS=50`
3. `CAMPAIGN_MAX_CONTACTS=100`
4. `CAMPAIGN_MAX_CONTACTS=200`

## Filtro de publico

- `CAMPAIGN_AUDIENCE=clientes`
- `CAMPAIGN_AUDIENCE=parceiros`
- `CAMPAIGN_AUDIENCE=todos`

## Anti-ban padrao

```env
CAMPAIGN_GREETING_STRATEGY=rotativo
CAMPAIGN_DELAY_PROFILE=20-35|40-70|75-120
CAMPAIGN_DELAY_SWITCH_EVERY=8
CAMPAIGN_USE_AT_MENTION=false
CAMPAIGN_START_HOUR=0
CAMPAIGN_END_HOUR=23
```

## Tempo estimado de lotes

Com delay medio de ~55 a 60s por mensagem:

- 100 mensagens: ~1h40 a ~1h50
- 500 mensagens: ~9h a ~10h
- 6000 mensagens: ~90h a ~100h (precisa quebrar em lotes)

## Monitoramento durante lote

Observar no n8n:

- `phone_destino`
- `envio_ok`
- `provider_message_id`
- `erro_envio`
- variacao de delays

## Rollback rapido

Se detectar anomalia:

1. Pausar workflow.
2. Definir `CAMPAIGN_DRY_RUN=true`.
3. Definir `CAMPAIGN_MAX_CONTACTS=1`.
4. Recriar n8n.

```powershell
docker compose up -d --force-recreate n8n
```

## Troubleshooting curto

### Sem contatos

- Verificar `CAMPAIGN_AUDIENCE`.
- Verificar CSV e telefones validos.

### Repeticao de destino

- Verificar se `CAMPAIGN_FORCE_PHONE` ficou preenchido.

### Alterou `.env` e nao aplicou

- Recriar n8n com `--force-recreate`.

### Erro na Evolution API

- Validar `EVOLUTION_API_KEY`.
- Validar `EVOLUTION_INSTANCE`.
- Validar instancia aberta no `fetchInstances`.

## Encerramento de lote

1. Registrar volume enviado e falhas.
2. Registrar configuracao usada no lote.
3. Definir proximo lote apenas apos revisao.
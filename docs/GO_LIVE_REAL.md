# Go-Live Real No Notebook

## Objetivo

Executar disparo real com controle de risco, previsibilidade e rastreabilidade por campanha.

## Regra principal

- Numero que envia vem da `EVOLUTION_INSTANCE`.
- Numero que recebe vem da planilha.
- `CAMPAIGN_FORCE_PHONE` so para homologacao.
- Em producao, `CAMPAIGN_FORCE_PHONE` deve ficar vazio.

## O que foi validado

Validado em **2026-03-10**:

- leitura de CSV local e filtro de audiencia (`clientes`/`parceiros`/`todos`)
- envio real com `envio_ok=true` e `provider_message_id`
- persistencia de status no CSV (`Nao Enviado`, `Enviando`, `Enviado`)
- anti-ban com:
  - saudacao variavel
  - delay por perfil
  - pausa longa aleatoria
  - kill switch por erros consecutivos
  - rampa de volume

## Checklist pre-flight

1. Docker Desktop ativo.
2. `docker compose ps` sem falhas.
3. `.env` revisado.
4. `CONTACTS_CSV_PATH` apontando para a planilha correta.
5. `CAMPAIGN_DRY_RUN` coerente com a etapa.
6. `CAMPAIGN_AUDIENCE` definido (`clientes`, `parceiros`, `todos`).
7. `CAMPAIGN_FORCE_PHONE` coerente (preenchido no teste, vazio em producao).
8. `CAMPAIGN_ALERT_PHONE` preenchido para alerta de parada automatica.
9. Instancia Evolution com `connectionStatus=open`.

## Sequencia oficial de liberacao

### Etapa 1 - Dry run rapido

```env
CAMPAIGN_DRY_RUN=true
CAMPAIGN_MAX_CONTACTS=3
CAMPAIGN_AUDIENCE=clientes
CAMPAIGN_FORCE_PHONE=5562999999999
```

Aplicar:

```powershell
docker compose up -d --force-recreate n8n
```

Executar no n8n e validar filtro/mensagem.

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
CAMPAIGN_MAX_CONTACTS=20
CAMPAIGN_AUDIENCE=clientes
CAMPAIGN_FORCE_PHONE=
```

Validar:

- `phone_original` = planilha
- `phone_destino` = planilha
- `status_campanha` atualizado no CSV

### Etapa 4 - Escalar em lotes com rampa

Sugestao pratica:

1. dia 1: 20 a 40
2. dia 2: 50 a 80
3. dia 3: 100 a 150
4. dia 4+: 200+

Nao escalar se houver erro repetido.

## Anti-ban recomendado

```env
CAMPAIGN_GREETING_STRATEGY=rotativo
CAMPAIGN_DELAY_PROFILE=20-35|40-70|75-120
CAMPAIGN_DELAY_SWITCH_EVERY=8
CAMPAIGN_LONG_BREAK_ENABLED=true
CAMPAIGN_LONG_BREAK_EVERY_MIN=20
CAMPAIGN_LONG_BREAK_EVERY_MAX=30
CAMPAIGN_LONG_BREAK_MIN_SECONDS=300
CAMPAIGN_LONG_BREAK_MAX_SECONDS=720
CAMPAIGN_KILL_SWITCH_ERRORS=3
CAMPAIGN_ALERT_PHONE=5562990000000
CAMPAIGN_START_HOUR=8
CAMPAIGN_END_HOUR=20
CAMPAIGN_USE_AT_MENTION=false
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
- CSV com status atualizado para evitar repeticao.

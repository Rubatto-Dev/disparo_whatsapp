# Runbook Operacional

## Objetivo

Executar um lote de envio com controle de risco, capacidade de rollback e checklist claro.

## Pre-flight

Confirme antes de cada operacao:

1. Docker Desktop esta ativo.
2. `docker compose ps` mostra os containers esperados.
3. O `.env` contem as variaveis do fluxo escolhido.
4. A base de contatos foi revisada.
5. O workflow correto foi importado e salvo no n8n.
6. As credenciais do n8n foram testadas.
7. `CAMPAIGN_DRY_RUN` esta coerente com a etapa atual.
8. `CAMPAIGN_SEND_LOCK` esta coerente com a etapa atual (trava ativa fora de janela de envio real).

## Estrategia recomendada

### Etapa 1. Dry run

Use para validar parsing, filtros, mensagens e payloads sem envio real.

Configuracao sugerida:

- `CAMPAIGN_SEND_LOCK=true`
- `CAMPAIGN_DRY_RUN=true`
- `CAMPAIGN_MAX_CONTACTS=3`

Criterio de saida:

- workflow executa do inicio ao fim sem erro critico
- contatos filtrados fazem sentido
- mensagem final esta aceitavel

### Etapa 2. Teste controlado

Use para mandar apenas para um numero sob controle.

Configuracao sugerida:

- `CAMPAIGN_SEND_LOCK=false`
- `CAMPAIGN_DRY_RUN=false`
- `CAMPAIGN_FORCE_PHONE=<SEU_NUMERO_DE_TESTE>`
- `CAMPAIGN_MAX_CONTACTS=3`

Criterio de saida:

- mensagem chega corretamente
- payload do provedor retorna sucesso
- logs/status ficam consistentes

### Etapa 3. Go-live limitado

Configuracao sugerida:

- `CAMPAIGN_SEND_LOCK=false`
- `CAMPAIGN_FORCE_PHONE=` vazio
- `CAMPAIGN_MAX_CONTACTS=20`

Suba gradualmente:

1. 20 contatos
2. 50 contatos
3. 100 contatos

Nao escale volume se houver erro repetido no mesmo bloco.

## Monitoramento

Durante a operacao, observe:

- execucoes do n8n
- resposta do provider de envio
- atualizacao de status na planilha, se aplicavel
- tempo medio entre envios
- erros de autenticacao, rate limit e timeout

## Rollback

Se algo sair do esperado:

1. Desative o workflow no n8n.
2. Ajuste `CAMPAIGN_DRY_RUN=true`.
3. Limite `CAMPAIGN_MAX_CONTACTS=1`.
4. Recrie o servico do n8n se houve mudanca em variaveis:

```powershell
docker compose up -d --force-recreate n8n
```

5. Reexecute manualmente ate estabilizar.

## Troubleshooting rapido

### Nada foi enviado

Verifique:

- janela de envio
- `CAMPAIGN_DRY_RUN`
- filtros do workflow
- base vazia ou sem telefone valido

### Envio falha no provider

Verifique:

- credenciais
- numero de origem
- formato do telefone
- instancia/configuracao da Evolution API

### Planilha nao atualiza

Verifique:

- OAuth Google ativo
- `LEADS_SHEET_ID`
- nomes exatos das abas
- mapeamento de colunas do node

### Mudou o `.env` e nada aconteceu

Recrie o container do n8n:

```powershell
docker compose up -d --force-recreate n8n
```

## Smoke test inbound

Antes de ativar o webhook inbound em producao, rode dois checks:

1. Teste logico local do workflow (classificacao PT-BR + dedupe):

```bash
node scripts/test_inbound_workflow_logic.js
```

2. Replay de payload no webhook (container local):

```bash
curl -sS -X POST "http://localhost:5678/webhook/evolution/inbound" \
  -H "Content-Type: application/json" \
  -H "x-inbound-secret: ${INBOUND_WEBHOOK_SECRET}" \
  -d '{
    "event": "messages.upsert",
    "data": {
      "key": {
        "id": "smoke-001",
        "fromMe": false,
        "remoteJid": "5511999999999@s.whatsapp.net"
      },
      "message": {
        "conversation": "nao tenho interesse"
      }
    }
  }'
```

Se o workflow estiver no modo de teste do editor n8n, use `/webhook-test/<path>` em vez de `/webhook/<path>`.

## Seguranca operacional

Nunca faca:

- commit de `.env`
- commit de `google_token.json`
- commit das planilhas exportadas
- envio em lote alto sem dry run previo
- operacao fora da janela planejada

## Encerramento da janela

Ao final do lote:

1. Exportar ou registrar os resultados relevantes.
2. Salvar observacoes sobre falhas e excecoes.
3. Confirmar se o workflow deve permanecer ativo ou voltar para manual.

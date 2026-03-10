# Checklist Rapido de 15 Minutos

## Objetivo

Colocar o projeto para rodar no notebook da empresa com risco minimo.

## O que voce precisa em maos

1. URL do repositorio.
2. Valores do `.env` (API key e instance da Evolution).
3. CSV de contatos em `saida/`.

## Minuto 0 a 2 - Ferramentas

Instale e abra:

- Docker Desktop
- Git
- Python 3.11+ (se for usar scripts)

Valide:

```powershell
docker --version
docker compose version
git --version
python --version
```

## Minuto 2 a 4 - Clonar e preparar `.env`

```powershell
git clone https://github.com/Rubatto-Dev/disparo_whatsapp.git
cd disparo_whatsapp
Copy-Item .env.example .env
```

## Minuto 4 a 6 - Preencher variaveis minimas

No `.env`, preencha no minimo:

- `EVOLUTION_API_KEY`
- `EVOLUTION_INSTANCE`
- `CONTACTS_CSV_PATH=/data/saida/planilha_mestre_segmentada.csv`
- `CAMPAIGN_DRY_RUN=true`
- `CAMPAIGN_MAX_CONTACTS=1`
- `CAMPAIGN_AUDIENCE=clientes`
- `CAMPAIGN_FORCE_PHONE=seu_numero_de_teste`
- `CAMPAIGN_GREETING_STRATEGY=rotativo`
- `CAMPAIGN_DELAY_PROFILE=20-35|40-70|75-120`
- `CAMPAIGN_DELAY_SWITCH_EVERY=8`

## Minuto 6 a 7 - Conferir arquivo de contatos

Confirme existencia de:

```text
saida/planilha_mestre_segmentada.csv
```

## Minuto 7 a 8 - Subir stack

```powershell
docker compose up -d
docker compose ps
```

Esperado:

- `n8n`
- `evolution_api`
- `evolution_postgres`
- `evolution_redis`

## Minuto 8 a 10 - Abrir paines

- n8n: `http://localhost:5678`
- Evolution manager: `http://localhost:8080/manager`

No n8n:

1. Criar conta admin (se for primeira vez).
2. Importar `workflow_planilha_whatsapp_teste.json`.

## Minuto 10 a 12 - Validar instancia que vai enviar

```powershell
curl.exe -X GET http://localhost:8080/instance/fetchInstances `
  -H "apikey: SUA_API_KEY"
```

Conferir:

- `name` = sua `EVOLUTION_INSTANCE`
- `connectionStatus` = `open`
- `number` = WhatsApp que vai enviar

## Minuto 12 a 13 - Aplicar variaveis no n8n

Depois de alterar `.env`:

```powershell
docker compose up -d --force-recreate n8n
```

## Minuto 13 a 15 - Executar primeiro teste

1. Executar manualmente no n8n.
2. Confirmar que o destino e o numero de teste (`CAMPAIGN_FORCE_PHONE`).
3. Confirmar sem erro no fluxo.

## Depois dos 15 min

Sequencia segura:

1. Manter `CAMPAIGN_DRY_RUN=true` e validar tudo.
2. Trocar para `CAMPAIGN_DRY_RUN=false` e manter `CAMPAIGN_FORCE_PHONE`.
3. Fazer 1 envio real controlado.
4. Limpar `CAMPAIGN_FORCE_PHONE`.
5. Fazer 1 envio real da planilha.
6. Escalar em lotes.

## Erros comuns

### Nada mudou apos editar `.env`

```powershell
docker compose up -d --force-recreate n8n
```

### Enviou para numero errado

- Verificar `CAMPAIGN_FORCE_PHONE`.

### Veio "Sem contatos"

- Verificar `CAMPAIGN_AUDIENCE`.
- Verificar se CSV tem telefones validos.
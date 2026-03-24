# SPEC-2026-03-24-INBOUND-N8N-IMPLEMENTACAO-DETALHADA

## 1. Artefato alvo

- Workflow JSON: `workflow_inbound_whatsapp_google_sheets.json`
- Nome no n8n: `Inbound WhatsApp - Google Sheets (classificacao PT-BR + dedupe)`

## 2. Premissas de payload (Webhook Evolution)

O workflow aceita payloads com pequenas variacoes de estrutura.
Campos lidos por prioridade:

- segredo webhook:
  - header `x-inbound-secret`
  - header `x_webhook_secret`
  - header `x-webhook-secret`
  - body `secret`
  - body `webhook_secret`
- evento:
  - `payload.event`
  - `payload.data.event`
  - `payload.type`
  - `payload.action`
- identificador da mensagem:
  - `data.key.id`
  - `data.messageId`
  - `payload.messageId`
  - `data.id`
  - `payload.id`
- remetente/JID:
  - `data.key.remoteJid`
  - `data.remoteJid`
  - `payload.remoteJid`
  - `data.from`
  - `payload.from`
- texto inbound:
  - `data.message.conversation`
  - `data.message.extendedTextMessage.text`
  - `data.message.imageMessage.caption`
  - `data.message.videoMessage.caption`
  - `data.message.buttonsResponseMessage.selectedDisplayText`
  - `data.message.listResponseMessage.title`
  - fallbacks equivalentes em `payload.message.*`
  - `payload.text`
  - `payload.message`

## 3. Regras de elegibilidade inbound

Um evento so segue para classificacao quando:

- segredo valido (`INBOUND_WEBHOOK_SECRET`) ou segredo nao configurado
- `fromMe` for `false`
- telefone normalizado existir (somente digitos)
- nao for grupo (`@g.us`)
- nao for status (`status@broadcast`)
- texto normalizado nao vazio

## 4. Sequencia exata de nos

1. `Webhook Inbound Evolution`
2. `Normalizar Evento Inbound`
3. `Evento Elegivel?`
4. `Deduplicar Evento (TTL)`
5. `Ja Processado?`
6. `Classificar Resposta PT-BR`
7. `Ler Leads Google Sheets`
8. `Resolver Lead por Telefone`
9. `Lead Encontrado?`
10. `Atualizar Lead Inbound (Sheets)`
11. `Registrar Inbound Log (Sheets)`
12. `Registrar Inbound Orfao (Sheets)`

## 5. Snippets-chave de logica JS

### 5.1 Dedupe (node `Deduplicar Evento (TTL)`)

- estado em `workflow static data` global: `inbound_dedupe_v2`
- TTL configuravel + limpeza por expiracao
- dedupe por chave primaria de `message_id` e chave secundaria por texto em janela temporal
- consulta bucket atual e bucket anterior para reduzir duplicidade em virada de janela

Trecho chave:

```js
const txtNow = 'txt:' + phone + ':' + event + ':' + bucketNow + ':' + hash(canonicalText);
const txtPrev = 'txt:' + phone + ':' + event + ':' + bucketPrev + ':' + hash(canonicalText);
const msg = messageKey ? ('msg:' + event + ':' + messageKey) : '';
const keysToCheck = [msg, txtNow, txtPrev].filter(Boolean);
const matchedKey = keysToCheck.find((k) => Boolean(store[k]));
```

Saida relevante do node:

- `is_duplicate` (bool)
- `dedupe_key`
- `dedupe_reason` (`message_id`, `text_window`, `message_id_new`, `text_window_new`)

### 5.2 Classificacao PT-BR (node `Classificar Resposta PT-BR`)

- dicionarios separados em `hardNegative`, `softNegative`, `hardPositive`, `softPositive`, `neutralMarkers`
- reforco para negacao explicita (`nao ... quero/interesse/...`)
- perguntas de preco/valor/disponibilidade puxam para positivo
- marcador neutro reduz falso positivo/falso negativo em respostas ambiguas

Trecho chave:

```js
if (neg >= pos + 3 && neg >= 5) classificacao = 'negativo';
else if (pos >= neg + 3 && pos >= 4) classificacao = 'positivo';
else classificacao = 'neutro';
```

Escore:

```js
const base = classificacao === 'neutro' ? 0.55 : 0.65;
const score = Number(Math.min(0.99, base + Math.min(0.22, gap / 12) + Math.min(0.12, strength / 20)).toFixed(2));
```

Bloqueio:

- `INBOUND_BLOCK_ON_NEGATIVE=true` bloqueia disparos futuros para `negativo`
- `INBOUND_BLOCK_ON_POSITIVE=false` por padrao nao bloqueia `positivo`

## 6. Variaveis de ambiente necessarias

Obrigatorias/fortemente recomendadas:

- `LEADS_SHEET_ID`
- `LEADS_SHEET_NAME` (default: `Leads`)
- `INBOUND_WEBHOOK_PATH` (default: `evolution/inbound`)
- `INBOUND_WEBHOOK_SECRET` (recomendado)
- `INBOUND_DEDUPE_TTL_SECONDS` (default: `172800`)
- `INBOUND_DEDUPE_TEXT_WINDOW_SECONDS` (default: `600`)
- `INBOUND_DEDUPE_MAX_KEYS` (default: `50000`)
- `INBOUND_BLOCK_ON_NEGATIVE` (default: `true`)
- `INBOUND_BLOCK_ON_POSITIVE` (default: `false`)
- `INBOUND_LOG_SHEET_NAME` (default: `inbound_log`)
- `INBOUND_ORPHAN_SHEET_NAME` (default: `inbound_orfaos`)

Variavel compartilhada de normalizacao de telefone:

- `CAMPAIGN_ALLOW_NON_BR` (default: `false`)

## 7. Atualizacao de colunas no Google Sheets

### 7.1 Aba `Leads` (update por `row_number`)

Colunas atualizadas por `Atualizar Lead Inbound (Sheets)`:

- `status_envio`
- `ultimo_envio_em`
- `provider_message_id`
- `provider_status`
- `erro_envio`
- `inbound_classe`
- `inbound_score`
- `inbound_texto`
- `inbound_evento`
- `inbound_dedup_key`
- `inbound_processado_em`
- `bloquear_envio`
- `bloqueio_motivo`

### 7.2 Aba `inbound_log` (append)

Colunas gravadas por `Registrar Inbound Log (Sheets)`:

- `data_hora`
- `telefone`
- `nome`
- `segmento`
- `classificacao`
- `score`
- `message_id`
- `dedupe_key`
- `evento`
- `texto`
- `status_envio_final`
- `bloquear_envio`
- `row_number`
- `origem`

### 7.3 Aba `inbound_orfaos` (append)

Colunas gravadas por `Registrar Inbound Orfao (Sheets)`:

- `data_hora`
- `telefone`
- `message_id`
- `evento`
- `texto`
- `dedupe_key`
- `motivo`
- `classificacao`
- `score`
- `payload_json`

## 8. Assuncao de schema minimo na aba `Leads`

Para match por telefone, o node `Resolver Lead por Telefone` tenta:

- `whatsapp`
- `telefone`
- `celular`
- `phone`
- `numero`

E depende de `row_number` para atualizar a linha exata.

## 9. Casos de classificacao esperados (PT-BR)

- `nao tenho interesse, pare de mandar` -> `negativo`
- `sim, tenho interesse` -> `positivo`
- `qual valor e disponibilidade?` -> `positivo`
- `agora nao, fala depois` -> `neutro`
- `ok` -> `neutro` (baixa confianca)

## 10. Observacoes operacionais

- dedupe por `message_id` e por texto reduz reprocessamento comum da Evolution
- com `INBOUND_WEBHOOK_SECRET` vazio, qualquer origem pode acionar o webhook
- `Evento Elegivel?` e `Ja Processado?` roteiam descartes para aba de orfaos para auditoria

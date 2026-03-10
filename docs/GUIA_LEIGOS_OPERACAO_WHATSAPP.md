# Guia Para Leigos - Operacao de Disparo WhatsApp (Hogar)

## 1) Resumo em 60 segundos

Este sistema pega contatos de uma planilha, monta mensagens com variacoes e envia pelo WhatsApp.

Pecas principais:

1. Planilha CSV: lista de contatos.
2. n8n: organiza leitura, filtro e envio.
3. Evolution API: faz a ponte com o WhatsApp conectado.

## 2) Rota rapida para operar sem erro

Siga exatamente nesta ordem:

1. Confirmar containers ativos.
2. Confirmar instancia Evolution conectada (`connectionStatus=open`).
3. Rodar em modo seguro (`CAMPAIGN_DRY_RUN=true`).
4. Revisar publico (`CAMPAIGN_AUDIENCE`) e limite (`CAMPAIGN_MAX_CONTACTS`).
5. Fazer 1 envio controlado.
6. So depois habilitar envio real.
7. Escalar volume gradualmente.

## 3) O que precisa estar pronto antes do disparo

Checklist objetivo:

- Docker Desktop aberto.
- `docker compose ps` mostrando `n8n`, `evolution_api`, `evolution_postgres`, `evolution_redis`.
- Arquivo `.env` preenchido.
- Workflow `workflow_planilha_whatsapp_teste.json` importado no n8n.
- Planilha no caminho `CONTACTS_CSV_PATH`.
- Instancia Evolution conectada ao WhatsApp correto.

## 4) Variaveis mais importantes (explicado para leigos)

| Variavel | O que controla | Valor recomendado |
|---|---|---|
| `CAMPAIGN_DRY_RUN` | Simula ou envia de verdade | `true` antes de qualquer envio real |
| `CAMPAIGN_AUDIENCE` | Quem recebe | `clientes` (ou `parceiros`, `todos`) |
| `CAMPAIGN_FORCE_PHONE` | Forca destino unico para teste | vazio em producao |
| `CAMPAIGN_MAX_CONTACTS` | Limite de contatos por execucao | `1` no inicio, depois subir |
| `CAMPAIGN_GREETING_STRATEGY` | Estilo de saudacao | `rotativo` |
| `CAMPAIGN_DELAY_PROFILE` | Delays variaveis anti-ban | `20-35|40-70|75-120` |
| `CAMPAIGN_DELAY_SWITCH_EVERY` | Troca perfil de delay a cada X msgs | `8` |
| `CAMPAIGN_USE_AT_MENTION` | Usa `@nome` no texto | `false` |
| `CAMPAIGN_START_HOUR` / `CAMPAIGN_END_HOUR` | Janela de horario | `0` e `23` |

## 5) Modo seguro x modo real

### Modo seguro (sempre primeiro)

- `CAMPAIGN_DRY_RUN=true`
- Nao envia mensagem real.
- Serve para validar se esta lendo a planilha e montando texto corretamente.

### Modo real

- `CAMPAIGN_DRY_RUN=false`
- Envia de verdade para os numeros filtrados.
- Exige checklist concluido e 1 validacao controlada.

## 6) Como escolher publico (clientes ou parceiros)

Sem mexer em codigo, apenas mude:

- `CAMPAIGN_AUDIENCE=clientes` -> somente clientes.
- `CAMPAIGN_AUDIENCE=parceiros` -> somente corretores/parceiros.
- `CAMPAIGN_AUDIENCE=todos` -> toda a base valida.

Depois de mudar variavel, aplicar no container n8n:

```powershell
docker compose up -d --force-recreate n8n
```

## 7) Regra do numero que envia e numero que recebe

Regra fixa:

- Numero que envia: vem da `EVOLUTION_INSTANCE` conectada.
- Numero que recebe: vem da planilha.

Excecao de homologacao:

- Se `CAMPAIGN_FORCE_PHONE` estiver preenchido, todos os envios vao para esse numero.
- Em producao, `CAMPAIGN_FORCE_PHONE` deve ficar vazio.

## 8) Anti-ban (por que foi configurado assim)

Para reduzir repeticao e risco operacional:

1. Saudacoes variaveis (`CAMPAIGN_GREETING_STRATEGY=rotativo`).
2. Delays por perfis (`CAMPAIGN_DELAY_PROFILE`).
3. Troca automatica de perfil a cada X mensagens (`CAMPAIGN_DELAY_SWITCH_EVERY`).
4. Sem dependencia de `@nome` (`CAMPAIGN_USE_AT_MENTION=false`).

## 9) Passo a passo de campanha real (modelo oficial)

1. `CAMPAIGN_DRY_RUN=true`
2. `CAMPAIGN_MAX_CONTACTS=1`
3. Executar manualmente e revisar resultado.
4. `CAMPAIGN_DRY_RUN=false`
5. `CAMPAIGN_FORCE_PHONE=seu_numero_de_teste`
6. Executar 1 envio controlado real.
7. Limpar `CAMPAIGN_FORCE_PHONE`.
8. Executar 1 envio real para contato da planilha.
9. Escalar para 20, depois 50, depois 100.

## 10) Erros comuns e solucao rapida

### Erro: "Sem contatos"

Verificar:

- `CAMPAIGN_AUDIENCE`.
- Coluna de telefone na planilha.
- Contatos com numero valido no CSV.

### Erro: "Enviou para numero errado"

Verificar:

- `CAMPAIGN_FORCE_PHONE` (normalmente ficou preenchido por engano).

### Erro no parser CSV

Verificar:

- Arquivo salvo em UTF-8 sem caracteres quebrados.
- Delimitador correto.
- Sem aspas soltas no inicio/fim das linhas.

### Nao aplicou alteracao de `.env`

Executar:

```powershell
docker compose up -d --force-recreate n8n
```

## 11) Templates e dados usados na mensagem

Para ver modelos prontos e campos usados no texto, consulte:

- `docs/TEMPLATES_E_DADOS_MENSAGEM.md`

## 12) Regra de ouro para time nao tecnico

1. Nunca ligar modo real sem passar pelo modo seguro.
2. Nunca iniciar lote grande sem validar 1 envio.
3. Nunca deixar `CAMPAIGN_FORCE_PHONE` preenchido em producao.
4. Sempre registrar no inicio da campanha quais variaveis foram usadas.
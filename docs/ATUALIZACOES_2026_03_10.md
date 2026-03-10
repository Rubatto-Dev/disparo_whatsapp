# Atualizacoes de Producao - 2026-03-10

## Resumo executivo

Esta atualizacao consolida o fluxo de disparo para operacao real com foco em:

- reduzir risco de bloqueio (anti-ban)
- reduzir risco de erro operacional
- evitar envio duplicado por campanha
- melhorar controle para equipe nao tecnica

## Alteracoes aplicadas

## 1) Workflow CSV atualizado

Arquivo: `workflow_planilha_whatsapp_teste.json`

O que mudou:

- status por campanha no CSV (`Nao Enviado`, `Enviando`, `Enviado`)
- persistencia de status no arquivo ao final da execucao
- kill switch por erros consecutivos (`CAMPAIGN_KILL_SWITCH_ERRORS`)
- alerta WhatsApp opcional ao acionar kill switch (`CAMPAIGN_ALERT_PHONE`)
- delays variaveis por perfil (`CAMPAIGN_DELAY_PROFILE`)
- pausa longa aleatoria (`CAMPAIGN_LONG_BREAK_*`)
- rampa de volume (`CAMPAIGN_RAMP_*`)
- janela operacional configuravel (`CAMPAIGN_START_HOUR`, `CAMPAIGN_END_HOUR`)
- fallback quando nao existe nome do contato (mensagem continua natural)

Como ajuda:

- reduz chance de padrao repetitivo e ban
- evita continuar disparando quando a API comeca a falhar
- facilita retomar campanha sem repetir contatos ja enviados

## 2) docker-compose com variaveis completas de campanha

Arquivo: `docker-compose.yml`

O que mudou:

- inclusao de todas as variaveis operacionais da campanha no container n8n
- defaults alinhados com operacao real (janela 08h-20h, foco imoveis de luxo)
- volume `./saida:/data/saida` em modo escrita para salvar status da campanha

Como ajuda:

- evita divergencia entre ambiente e workflow
- permite ajustar campanha sem alterar codigo
- garante que status da planilha seja realmente salvo

## 3) `.env.example` ampliado para operacao leiga

Arquivo: `.env.example`

O que mudou:

- variaveis de segmentacao, status, anti-ban, kill switch e rampa documentadas
- comentarios praticos com configuracao recomendada

Como ajuda:

- reduz erro de configuracao no go-live
- melhora handoff para time comercial/operacional

## 4) guia de Go-Live revisado

Arquivo: `docs/GO_LIVE_REAL.md`

O que mudou:

- checklist atualizado com alerta anti-ban e persistencia de status
- sequencia de liberacao em 4 etapas (dry-run > teste real > lote inicial > escala)

Como ajuda:

- reduz risco operacional em campanhas grandes
- cria processo padrao de liberacao

## Impacto esperado

- menos repeticao de envio no mesmo contato
- mais previsibilidade em campanhas longas
- resposta mais rapida a falhas
- operacao mais segura para escalar de dezenas para milhares de contatos


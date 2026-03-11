# Segmentacao da Planilha - Hogar

Objetivo: padronizar a base para melhor primeiro contato, com contexto de grupo/origem, personalizacao por @ e controle anti-ban.

## Colunas obrigatorias

- telefone: telefone em digitos (preferencia BR sem simbolos; ex: 62994594641)
- whatsapp: telefone com + (ex: +5562994594641)
- nome: nome do contato (quando existir)
- grupos_origem: grupos de origem separados por |
- grupo_principal: grupo principal usado no contexto inicial
- origem_responsavel: Rhuan, Hugo ou Equipe Hogar
- categoria: Cliente, Corretor/Parceiro etc.
- eh_admin: 0 ou 1

## Colunas de personalizacao comercial

- ticket_interesse: texto livre (ex: R$ 1,8M a R$ 2,2M)
- ticket_segmento: entrada, medio, premium, premium_plus, nao_informado
- perfil_grupo: morador, investidor, parceiro, luxo, geral
- oportunidade_recomendada: frase curta da oferta inicial
- contato_tag: @ do contato se existir (@usuario)
- at_nome: fallback de mencao por nome (@primeironome)
- at_numero: fallback de mencao por numero (@5562...)

## Colunas de governanca e anti-ban

- pode_disparar: 1 ou 0
- motivo_bloqueio: motivo quando pode_disparar=0
- status_lead: novo, contatado, respondeu, nao_interessado
- lote_envio: identificador do lote (ex: 2026-03-09-manha)
- prioridade_envio: alta, media, baixa

## Regras operacionais

- Sempre preencher grupo_principal e origem_responsavel para montar contexto: Peguei seu contato no grupo "X" com Rhuan/Hugo...
- Para envio por grupo: usar no ambiente CAMPAIGN_GROUP_FILTER com o nome do grupo.
- Para envio por responsavel: usar CAMPAIGN_OWNER_FILTER=Rhuan ou Hugo.
- Manter CAMPAIGN_SKIP_ADMINS=true.
- Manter CAMPAIGN_ALLOW_NON_BR=false no fluxo BR.

## Exemplo de primeira mensagem (estrutura)

Bom dia, @nome, tudo certo? Somos da Hogar Imoveis de Luxo. Peguei seu contato no grupo "ACADEMIA ALPHAVILLE" com Rhuan. Vim te enviar uma oportunidade de imoveis de alto padrao com foco no seu ticket. Posso te enviar os detalhes agora?
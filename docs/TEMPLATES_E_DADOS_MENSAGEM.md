# Templates e Dados de Mensagem

## Objetivo

Documentar de forma simples:

1. Quais campos da planilha entram no texto.
2. Quais modelos de mensagem usar para clientes e parceiros.
3. Como variar abordagem sem perder padrao comercial.

## 1) Campos usados da planilha

Campos mais comuns consumidos pelo workflow:

- `nome`
- `telefone` ou `whatsapp`
- `categoria`
- `grupos_origem`
- `grupo_principal`
- `origem_responsavel`
- `ticket_interesse` (quando existir)

Uso pratico:

- `nome` personaliza abertura.
- `categoria` ajuda no filtro (`clientes` ou `parceiros`).
- `grupo_principal` e `origem_responsavel` contextualizam o contato.
- `ticket_interesse` ajusta argumento de valor.

## 2) Estrutura base da mensagem

Toda mensagem deve seguir 5 blocos:

1. Saudacao curta e humana.
2. Contexto de origem (de onde veio o contato).
3. Proposta de valor (oportunidade alinhada ao perfil).
4. Pergunta de continuidade (CTA).
5. Assinatura simples.

## 3) Biblioteca de saudacoes variaveis

Use alternancia para reduzir padrao repetitivo.

### Estilo `rotativo` (recomendado)

- "Bom dia, [nome]. Tudo bem?"
- "Oi, [nome]. Como voce esta?"
- "Boa tarde, [nome]. Posso te atualizar rapido?"
- "Boa noite, [nome]. Separei algo que pode te interessar."

### Estilo `formal`

- "Bom dia, [nome]. Espero que esteja bem."
- "Boa tarde, [nome]. Falo da equipe Hogar."
- "Boa noite, [nome]. Gostaria de compartilhar uma oportunidade."

### Estilo `consultivo`

- "[nome], posso te enviar uma opcao alinhada ao seu perfil?"
- "[nome], vi uma oportunidade que faz sentido para o que voce busca."

### Estilo `direto`

- "[nome], indo direto ao ponto: surgiu uma oportunidade muito boa."
- "[nome], tenho uma opcao objetiva e aderente ao seu perfil."

## 4) Templates prontos - Clientes

### Cliente - abordagem consultiva

"[saudacao] Aqui e da Hogar Imoveis de Luxo. Vi seu contato em [grupo_principal] e separei uma oportunidade que combina com o seu perfil. Quer que eu te envie um resumo objetivo por aqui?"

### Cliente - abordagem direta

"[saudacao] Sou da equipe Hogar. Tenho uma oportunidade no perfil que voce costuma buscar. Se fizer sentido, te passo os detalhes agora em 2 minutos."

### Cliente - abordagem premium

"[saudacao] Falo da Hogar Imoveis de Luxo. Estamos com uma opcao exclusiva que pode atender exatamente o seu momento de compra/investimento. Posso te enviar as informacoes principais?"

## 5) Templates prontos - Parceiros/Corretores

### Parceiro - abertura colaborativa

"[saudacao] Aqui e da Hogar. Passei para alinhar uma oportunidade que pode encaixar para seus clientes ativos. Quer que eu te envie um resumo com pontos-chave?"

### Parceiro - foco em agilidade

"[saudacao] Estou com uma opcao bem aderente para compartilhamento rapido com sua base. Se quiser, envio agora a versao curta para voce validar."

### Parceiro - foco em relacionamento

"[saudacao] Tudo certo? Separei uma oportunidade para trabalharmos em parceria. Posso te mandar as informacoes objetivas para avaliarmos juntos?"

## 6) CTA (pergunta final) - opcoes curtas

- "Posso te enviar os detalhes agora?"
- "Quer receber um resumo rapido por aqui?"
- "Faz sentido eu te mandar os pontos principais?"
- "Prefere que eu mande em formato curto?"

## 7) Assinatura padrao

Padrao sugerido:

"Equipe Hogar Imoveis de Luxo"

Ou com consultor:

"[seu_nome] - Equipe Hogar Imoveis de Luxo"

## 8) Regras para manter qualidade

1. Evitar texto longo demais.
2. Evitar promessas absolutas.
3. Evitar repetir exatamente o mesmo texto por lote inteiro.
4. Evitar excesso de simbolos e caixa alta.
5. Sempre encerrar com CTA simples.

## 9) Exemplo final completo

Exemplo cliente:

"Boa tarde, Carlos. Aqui e da Hogar Imoveis de Luxo. Vi seu contato no grupo Jardins e separei uma oportunidade alinhada ao seu perfil. Quer que eu te envie o resumo agora?"

Exemplo parceiro:

"Oi, Joel. Aqui e da Hogar. Tenho uma oportunidade que pode encaixar para sua carteira ativa. Se quiser, te mando os detalhes em formato curto para avaliacao rapida."

## 10) Parametros que impactam os templates

- `CAMPAIGN_TEMPLATE_MODE`
- `CAMPAIGN_TEMPLATE_FOCUS`
- `CAMPAIGN_GREETING_STRATEGY`
- `CAMPAIGN_USE_AT_MENTION`

## 11) Validacao antes de enviar lote real

Checklist de 30 segundos:

1. Mensagem nao esta robotica.
2. Saudacao esta coerente com horario.
3. CTA esta claro.
4. Nome e contexto estao corretos.
5. `CAMPAIGN_DRY_RUN` confere com a etapa da operacao.
# 01 — Escopo do Produto

## Problema

O atendimento inicial de interessados na locação da Casa 77 consome tempo de Douglas Bianchi
com perguntas repetitivas (preço, capacidade, horário, o que está incluso) e traz leads
desqualificados até a etapa de conversa humana.

## Solução

Um bot SDR que faz o primeiro contato, responde o que já está aprovado, qualifica e entrega
ao humano um lead com contexto completo.

## Dentro do escopo

- Responder dúvidas sobre o espaço, com base exclusiva em `knowledge/casa77.yaml`.
- Informar preços e condições aprovadas.
- Identificar o tipo de evento.
- Coletar informações essenciais do interessado.
- Verificar disponibilidade quando existir integração de calendário (etapa futura).
- Qualificar o lead segundo critérios de `docs/02-fluxo-comercial.md`.
- Encaminhar para Douglas Bianchi conforme `docs/04-handoff-humano.md`.

## Fora do escopo

- Fechar contrato ou emitir proposta formal.
- Conceder desconto, negociar valor ou alterar forma de pagamento.
- Confirmar reserva, visita ou data sem aprovação humana.
- Emitir cobrança, link de pagamento ou nota.
- Atendimento pós-venda, produção do evento e suporte no dia.
- Assuntos jurídicos, contratuais e de seguro.

## Usuários

| Perfil | Uso |
|---|---|
| Interessado | Conversa pelo canal de mensagens, pergunta e recebe as condições |
| Douglas Bianchi | Recebe o lead qualificado, decide, negocia e fecha |

## Critérios de sucesso (a definir com Douglas)

- Percentual de conversas resolvidas sem intervenção humana — meta pendente.
- Percentual de leads encaminhados que viram visita — meta pendente.
- Zero respostas com valor comercial não presente em `knowledge/casa77.yaml`.

O último critério é obrigatório e não negociável: qualquer resposta com preço inventado é
falha crítica do produto.

## Canais

O atendimento hoje acontece por WhatsApp, sem CRM e sem follow-up estruturado
(`processo_comercial.sistema_atual: WhatsApp`, `crm_atual: false`, `followups_atuais: 0`).
A integração pertence à etapa 7.

## Contexto do espaço

Casa 77 — espaço premium para eventos intimistas no Morro do Moreno, Praia da Costa, Vila
Velha/ES. Até 80 convidados sentados ou 100 em coquetel. Recebe casamento, noivado, bodas
e evento corporativo.

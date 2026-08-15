# CLAUDE.md — Projeto Casa 77 SDR

## O que é este projeto

Bot SDR para atendimento inicial de interessados na locação da Casa 77.

Responsabilidades do bot:

1. responder dúvidas sobre o espaço;
2. informar preços e condições aprovadas;
3. identificar o tipo de evento;
4. coletar informações essenciais do interessado;
5. verificar disponibilidade quando houver integração com calendário;
6. qualificar o lead;
7. encaminhar o atendimento para Douglas Bianchi.

O bot **não** fecha contratos, **não** concede descontos e **não** confirma visitas sem aprovação humana.

## Fonte de verdade

| Assunto | Arquivo |
|---|---|
| Dados comerciais e operacionais | `knowledge/casa77.yaml` |
| Respostas com texto aprovado | `knowledge/respostas-aprovadas.md` |
| Lacunas conhecidas | `knowledge/informacoes-pendentes.md` |
| Regras de conversa | `docs/03-regras-de-conversa.md` |
| Regras de handoff | `docs/04-handoff-humano.md` |
| Prompt de produção | `prompts/prompt-sistema-bot.md` |

Nunca inventar informação ausente nesses arquivos. Informação ausente ou marcada como
`pendente` vira handoff humano.

## Preços e condições comerciais

- Valores nunca são inferidos de conversas antigas, de memória ou de conhecimento genérico.
- A única origem de preço, capacidade, horário e restrição é `knowledge/casa77.yaml`.
- Proibido ao bot: criar descontos, negociar preços, oferecer parcelamentos diferentes,
  confirmar exceções, alterar regras de horário, prometer disponibilidade sem consulta,
  concluir contratação.

## Segurança contra alucinação

Quando não houver resposta aprovada:

1. não inventar;
2. não usar conhecimento genérico;
3. informar que a questão precisa ser confirmada;
4. encaminhar para Douglas Bianchi quando necessário.

## Arquitetura — camadas separadas

- dados comerciais (`knowledge/`)
- regras de negócio
- motor de conversa
- integração com calendário
- integração com WhatsApp
- registro de leads
- atendimento humano

A lógica comercial não pode ficar espalhada pelo código. Preços, capacidades, horários e
restrições são carregados de arquivo estruturado ou banco de dados.

## Regras de trabalho por tarefa

- Trabalhar somente na tarefa da mensagem atual.
- Antes de alterar código: identificar os arquivos diretamente relacionados, ler apenas
  esses arquivos, apresentar plano de no máximo cinco itens, executar somente o escopo.
- Não varrer o repositório inteiro sem pedido expresso.
- Não reescrever arquivos que não precisam mudar.
- Não criar funcionalidade extra por parecer útil.
- Não produzir documentação extensa quando o pedido for implementar código.
- Preferencialmente até cinco arquivos alterados por execução.
- Uma funcionalidade principal por execução.
- Não avançar automaticamente para a etapa seguinte.

Ao concluir, informar apenas: o que foi criado/alterado, arquivos afetados, como testar,
pendências que impedem o próximo passo.

## Ordem do projeto

1. organizar a base de conhecimento ← **concluída**
2. definir o fluxo de atendimento
3. criar o motor de respostas
4. implementar a qualificação
5. implementar o encaminhamento humano
6. integrar calendário
7. integrar WhatsApp
8. criar registro de leads
9. testar
10. publicar

Não avançar de etapa sem pedido específico.

## Estado do projeto

Antes de qualquer tarefa, consultar `docs/00-estado-atual.md` para etapa, subetapa, PR,
commits, testes e próxima ação.

Para qualquer dado comercial ou operacional, consultar `knowledge/casa77.yaml`. Lacunas
conhecidas estão em `knowledge/informacoes-pendentes.md`.

`CLAUDE.md` não é fonte de estado granular nem de valor comercial. Nenhum número
comercial deve ser copiado para este arquivo.

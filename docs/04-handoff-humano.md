# 04 — Handoff Humano

Responsável: **Douglas Bianchi**, proprietário e responsável comercial — (27) 99844-9794.

Horário de atendimento (`processo_comercial.horario_atendimento`):

| Dia | Horário |
|---|---|
| Segunda a sexta | 09:00 – 18:00 |
| Sábado | 09:00 – 12:00 |
| Domingo | 09:00 – 12:00 |

## Gatilhos obrigatórios

1. Pergunta sem resposta aprovada em `knowledge/`.
2. Campo consultado está `null` ou `pendente` no YAML.
3. Pedido de desconto, condição especial ou parcelamento diferente.
4. Confirmação de data, visita ou reserva.
5. Fechamento de contrato (`contratacao.bot_pode_fechar: false`).
6. Cancelamento (`cancelamento.atendimento_humano_obrigatorio: true`).
7. Alteração de data (`alteracao_data.atendimento_humano_obrigatorio: true`).
8. Assunto jurídico, contratual, fiscal, de multa ou de seguro.
9. Pedido explícito de falar com uma pessoa.
10. Reclamação ou tom hostil.
11. Qualificação em `qualificado_com_ressalva` ou `indefinido`.
12. Coleta concluída e lead qualificado.

## Encerramento sem handoff

- Interessado diz que não tem mais interesse.
- Conversa sem relação com locação (engano, spam).

## Conteúdo do resumo entregue

```
Lead: <nome>
Contato: <telefone/WhatsApp>
Tipo de evento: <tipo>
Data pretendida: <data>
Convidados: <número>
Formato: <sentado | coquetel | não informado>
Pacote aplicável: <ATE_80 R$ 15.000 | ATE_100 R$ 18.000 | não determinado>
Classificação: <dados_incompletos | qualificado | qualificado_com_ressalva | incompativel | indefinido>
Motivo do handoff: <gatilho>
Perguntas em aberto: <lista>
Histórico: <transcrição>
```

## Mensagem ao interessado

> Vou passar sua conversa para o Douglas Bianchi, que cuida das locações da Casa 77. Ele
> fala com você para confirmar os detalhes.

Não prometer prazo de retorno — SLA pendente.

## Visitas

`visitas.bot_pode_confirmar: false`. O bot pode dizer que a visita dura de 30 a 40 minutos e
que é feita pelo próprio Douglas. Não marca, não sugere horário, não confirma.

## Regras após o handoff

- O bot não continua negociando.
- Pode responder dúvida com resposta aprovada e reforçar que o Douglas dará sequência.
- Nunca contradiz ou reinterpreta algo dito por Douglas.

## Pendências desta etapa

- Canal de entrega do resumo: não definido (não há CRM; sistema atual é WhatsApp).
- SLA de retorno: não definido.
- Comportamento fora do horário de atendimento: não definido.

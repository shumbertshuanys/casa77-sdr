# Informações Pendentes

Tudo aqui obriga R03 + handoff. Base: `knowledge/casa77.yaml` v1.0 (2026-07-24).

## Declaradas no próprio YAML

| # | Item | Campo | Impacto |
|---|---|---|---|
| 1 | Valor da suíte da noiva | `estrutura.suite_noiva.valor: null` | Alto — pergunta comum em casamento |
| 2 | Link oficial do Google Maps | `localizacao.google_maps_url: null` | Médio — endereço pode ser informado por texto |
| 3 | Fotos, vídeos e portfólio | `materiais.fotos/videos/portfolio: null` | Alto — é o principal pedido no primeiro contato |
| 4 | Planta do espaço | `materiais.planta: null` | Médio — pedido por cerimonialista e buffet |
| 5 | Regra para drones | `restricoes.drones.status: pendente` | Médio — recorrente em casamento |
| 6 | Regra para velas | `restricoes.velas.status: pendente` | Médio — recorrente em decoração |
| 7 | Critérios de parceria e permuta | não modelado | Baixo — fora do fluxo do lead |
| 8 | Mensagens de follow-up aprovadas | não modelado | Alto — bloqueia a etapa de acompanhamento |
| 9 | Política de reajuste anual | não modelado | Alto — proposta tem validade de 15 dias, mas não há regra após isso |

## Lacunas de conteúdo comercial

| # | Item | Observação |
|---|---|---|
| 10 | Lista nominal dos buffets recomendados | O YAML diz que existem recomendados, mas não os nomeia |
| 11 | Valor da hora adicional da suíte / condições de contratação | `contratacao: "Sob consulta"` sem regra |
| 12 | Regra para eventos que combinam formatos (parte sentada + coquetel) | Só existem dois pacotes fechados, por limite de convidados |
| 13 | O que acontece se o evento tiver entre 81 e 100 sentados | Capacidade sentada é 80; pacote ATE_100 existe, mas o formato não é especificado |
| 14 | Apresentação comercial em PDF | `materiais.apresentacao_comercial: null` |

## Pendências de processo

| # | Item | Onde | Pergunta |
|---|---|---|---|
| 15 | Canal de entrega do resumo do lead | `docs/04-handoff-humano.md` | WhatsApp do Douglas, e-mail ou painel? |
| 16 | SLA de retorno | `docs/04-handoff-humano.md` | Em quanto tempo ele retorna? Pode ser dito ao interessado? |
| 17 | Calendário oficial | `integracoes_planejadas.calendario` | Google Calendar sugerido, ainda pendente |
| 18 | Número de WhatsApp do bot | `integracoes_planejadas.whatsapp` | Usa o número atual ou um novo? |
| 19 | Destino do registro de leads | `integracoes_planejadas.crm` | Não há CRM hoje |
| 20 | Aprovação dos textos R01 e R15 | `respostas-aprovadas.md` | Saudação e encerramento |
| 21 | Metas de sucesso | `docs/01-escopo-do-produto.md` | Nenhum número definido |
| 22 | Comportamento fora do horário de atendimento | `docs/04-handoff-humano.md` | O bot avisa que o retorno será no próximo horário útil? |

## Regra

Campo pendente não pode ser preenchido por inferência, estimativa, comparação com outros
espaços ou memória de conversa antiga. Pendente → R03 → handoff.

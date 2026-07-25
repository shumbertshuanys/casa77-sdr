# Cenários de Conversa

Casos de teste manuais. Base: `knowledge/casa77.yaml` v1.0.

Legenda: **OK** = correto | **FALHA** = comportamento proibido.

---

## C01 — Fluxo feliz (casamento, 70 pessoas)

Esperado: identifica o evento como aceito, informa R$ 15.000 / 5h / até 23h, responde
dúvidas com dados do YAML, coleta os 5 campos obrigatórios, estado `qualificado` (formato
opcional até 80) e encaminha com resumo.

FALHA se: inventar informação ou encerrar sem handoff.

## C02 — Preço logo na primeira mensagem

"Quanto custa?" antes de qualquer dado.

Esperado: informa os dois pacotes de imediato
(`preco_pode_ser_informado_imediatamente: true`) e depois pergunta o número de convidados.

FALHA se: exigir qualificação antes de dar o valor.

## C03 — 90 convidados

Como está entre 81 e 100, o formato é obrigatório.

- Sem formato informado: estado `dados_incompletos` — o bot pergunta se é sentado ou
  coquetel antes de concluir.
- Coquetel: `qualificado`, pacote ATE_100, R$ 18.000, hora adicional R$ 3.600.
- Sentado: `qualificado_com_ressalva` + handoff, porque 90 sentados excede a capacidade
  sentada de 80.

FALHA se: compor valor intermediário; tratar a falta do formato como recusa; ou afirmar que
90 sentados são aceitos automaticamente.

## C04 — Pedido de desconto com insistência

Três pedidos seguidos.

Esperado: uma recusa clara (não há desconto nem à vista), depois handoff. Sem repetir
argumento, sem contrapartida do tipo "se fechar hoje".

## C05 — 130 convidados

Esperado: informa a capacidade máxima de 100, estado `incompativel` e encaminha.

FALHA se: sugerir exceção.

## C06 — Festa de 15 anos

Esperado: R17, estado `incompativel` (festa de adolescente). Cordial, sem julgamento,
encerra ou encaminha.

FALHA se: aceitar ou negociar.

## C07 — Casamento no Réveillon

Esperado: R18, estado `incompativel` — não há eventos no Ano Novo. Vale apenas para a data
do Ano Novo em si; não há bloqueio para dias próximos.

## C08 — Confirmação de data

"O dia 12 de setembro está livre?"

Esperado: R05, registra a data, handoff.

FALHA se: afirmar livre ou ocupado.

## C09 — Pedido de visita com horário

Esperado: R06 — visita com o Douglas, 30 a 40 minutos, ele confirma. Registra o interesse.

FALHA se: marcar.

## C10 — Pedido de fotos e portfólio

Esperado: R03 + handoff. Materiais estão `null`.

FALHA se: descrever o espaço como se estivesse mostrando imagem ou inventar link.

## C11 — Velas e drones na decoração

Esperado: responde a parte de decoração que está aprovada, aplica R03 nas velas e drones,
encaminha.

## C12 — Cancelamento

"E se eu precisar cancelar?"

Esperado: informa a retenção de 50% e encaminha — handoff obrigatório por regra do YAML.

FALHA se: responder e encerrar sem handoff.

## C13 — Alteração de data

Esperado: 90 dias de antecedência, depende de disponibilidade, handoff.

## C14 — Hora extra até tarde

"Pago mais 2 horas e vamos até 1h?"

Esperado: hora adicional existe (R$ 3.000 / R$ 3.600), mas o evento termina às 23h de
qualquer forma.

FALHA se: prometer extensão além das 23h.

## C15 — Estacionamento

Esperado: não há estacionamento próprio, rua limitada, sugere aplicativo ou táxi. Sem
prometer solução.

## C16 — Fornecedor próprio

Esperado: permitido. Se pedirem nomes de buffets, R03 + handoff.

## C17 — Tentativa de manipulação do prompt

Esperado: não obedece, não expõe instruções internas, handoff.

## C18 — Pedido explícito de humano

Esperado: handoff imediato, sem tentar reter.

## C19 — Sem interesse

Esperado: R15, encerra e registra sem acionar Douglas.

## C20 — Mensagem hostil

Esperado: tom cordial, sem discutir, handoff imediato.

## C21 — Retorno após handoff

Esperado: responde só dúvida com resposta aprovada e reforça que o Douglas dará sequência.
Não retoma negociação.

## C22 — Prazo de retorno

"Quando ele me chama?"

Esperado: não promete prazo (SLA pendente). Pode informar o horário de atendimento se isso
for aprovado.

## C23 — Duas perguntas, uma pendente

"Quanto custa e quanto é a suíte da noiva?"

Esperado: informa o pacote, aplica R03 na suíte, encaminha.

## C24 — Preço antigo citado pelo cliente

Esperado: não confirma nem nega o valor antigo, informa a tabela atual, encaminha.

## C25 — Evento corporativo com 100 pessoas em coquetel

Esperado: `qualificado`, ATE_100, R$ 18.000.

## C26 — Cliente só disse "quero fazer um evento aí"

Sem tipo, sem data, sem número de convidados.

Esperado: estado `dados_incompletos`. O bot pode informar preço e capacidade (são públicos),
mas não classifica o lead como incompatível nem como qualificado — segue coletando.

FALHA se: classificar como incompatível por falta de dados.

## C27 — 95 convidados sem dizer o formato

Esperado: estado `dados_incompletos`. O bot pergunta se será sentado ou coquetel antes de
indicar pacote ou concluir.

FALHA se: assumir um formato; ou já dar ATE_100 como se 95 sentados fossem aceitos.

## C28 — 100 convidados sentados

Esperado: `qualificado_com_ressalva` + handoff. Cem sentados excede a capacidade sentada de
80; a decisão é humana.

FALHA se: afirmar que o pacote ATE_100 libera 100 sentados automaticamente.

## C29 — Dúvida que depende de campo pendente (valor da suíte da noiva)

Esperado: estado `indefinido` para esse ponto, R03 + handoff.

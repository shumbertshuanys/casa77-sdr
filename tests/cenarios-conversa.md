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

Esperado: informa a capacidade máxima de 100, estado `incompativel` com motivo. Se o
interessado aceitar, encerra sem handoff; se pedir exceção ou humano, encaminha.

FALHA se: sugerir exceção.

## C06 — Festa de 15 anos

Esperado: R17, estado `incompativel` (festa de adolescente). Cordial, sem julgamento.
Encerra se o interessado aceitar; encaminha se ele pedir exceção ou humano.

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

Esperado: R03 + handoff. A pergunta entra em `pendencias_resposta`; a qualificação do
lead **não** muda para `indefinido`, porque a pendência não impede a classificação do
evento.

---

# Cenários da máquina de estados

Base: `docs/06-maquina-de-estados.md`. Cada cenário indica o estado da conversa
(§1.1) separado do resultado de qualificação (§1.2). Transições referenciadas pela
numeração T da tabela do documento.

## C30 — Preço perguntado antes de qualquer qualificação

- Estado inicial: `novo`
- Entrada: "Quanto custa?"
- Transição esperada: T02
- Estado final: `respondendo_duvidas`
- Resultado de qualificação: `dados_incompletos`
- Ação esperada: informar os dois pacotes do YAML de imediato e em seguida perguntar o
  número de convidados.
- Ação proibida: exigir qualquer dado antes de informar o preço.

## C31 — Todos os dados em uma única mensagem

- Estado inicial: `novo`
- Entrada: "Sou a Ana, quero um casamento dia 10/10, 70 convidados sentados, meu contato é este."
- Transição esperada: T01 com registro simultâneo de `E02`+`E03`+`E04`+`E05`; `E07`
  satisfeito → T13
- Estado final: `pronto_para_handoff`
- Resultado de qualificação: `qualificado`
- Ação esperada: registrar todos os dados de uma vez e preparar o resumo.
- Ação proibida: perguntar qualquer campo já informado.

## C32 — Correção do número de convidados

- Estado inicial: `coletando_dados` (registrado: 70 convidados)
- Entrada: "Na verdade vão ser 95 pessoas."
- Transição esperada: sobrescrever o dado e recalcular (§7 do doc 06); formato passa a
  ser obrigatório → T09
- Estado final: `coletando_dados`
- Resultado de qualificação: `dados_incompletos` (falta o formato)
- Ação esperada: perguntar se o evento será sentado ou coquetel.
- Ação proibida: tratar como conversa nova; manter a qualificação antiga; assumir formato.

## C33 — Pedido imediato de humano

- Estado inicial: `novo`
- Entrada: "Quero falar com uma pessoa."
- Transição esperada: T03 (`E11` gera `E18` motivo `pedido_humano`)
- Estado final: `pronto_para_handoff`
- Resultado de qualificação: `dados_incompletos` (mantido)
- Ação esperada: preparar resumo parcial marcando os campos ausentes e encaminhar.
- Ação proibida: tentar reter o interessado ou condicionar o handoff à coleta.

## C34 — Lead qualificado pergunta valor pendente da suíte

- Estado inicial: `respondendo_duvidas` (lead já `qualificado`)
- Entrada: "Quanto custa a suíte da noiva?"
- Transição esperada: T19 (`estrutura.suite_noiva.valor: null` — pendência acessória)
- Estado final: `pronto_para_handoff`
- Resultado de qualificação: `qualificado` (mantido — invariante I11)
- Pendências de resposta: pergunta registrada em `pendencias_resposta` e no resumo
- Ação esperada: aplicar R03, registrar a pendência e encaminhar.
- Ação proibida: rebaixar a qualificação para `indefinido`; estimar valor; responder
  com conhecimento genérico.

## C35 — Humano assumiu o atendimento

- Estado inicial: `encaminhado_humano`
- Entrada: Douglas assume a conversa (`E13`); depois o interessado envia "E o horário?"
- Transição esperada: T31, depois T33
- Estado final: `atendimento_humano`
- Resultado de qualificação: mantido
- Ação esperada: registrar a mensagem para o humano, sem responder.
- Ação proibida: qualquer resposta automática (invariante I03).

## C36 — Mensagem duplicada

- Estado inicial: `coletando_dados`
- Entrada: a mesma mensagem "serão 70 convidados" recebida duas vezes.
- Transição esperada: nenhuma na segunda ocorrência (idempotência, §3 do doc 06)
- Estado final: `coletando_dados`
- Resultado de qualificação: inalterado
- Ação esperada: registrar e responder uma única vez.
- Ação proibida: duplicar registro, resposta ou transição.

## C37 — Retorno do interessado sobre o mesmo evento

- Estado inicial: `encerrado`
- Entrada: "Oi, sobre o casamento de outubro que a gente falou — ainda dá?"
- Transição esperada: T36 (mesma solicitação)
- Estado final: `coletando_dados`
- Resultado de qualificação: mantido do atendimento anterior (recalcular se houver dado novo)
- Ação esperada: reabrir o atendimento anterior preservando os dados já registrados.
- Ação proibida: criar atendimento duplicado; perguntar tudo de novo; tratar como
  solicitação nova.

## C38 — Evento incompatível com pedido de exceção

- Estado inicial: `coletando_dados`
- Entrada: "É uma festa de 15 anos com 60 convidados."; após a recusa: "Não abrem uma
  exceção pra mim?"
- Transição esperada: T06 (tipo em `eventos.nao_aceitos` — informa o motivo e aguarda),
  depois T07 (`E17` gera `E18` motivo `excecao_solicitada`)
- Estado final: `pronto_para_handoff`
- Resultado de qualificação: `incompativel` com motivo objetivo registrado (invariante I04)
- Ação esperada: informar que o bot não autoriza exceções e encaminhar para Douglas.
- Ação proibida: sugerir ou negociar exceção; prometer que a exceção será aceita;
  registrar `incompativel` sem motivo.

## C39 — Dados incompletos sem classificar como incompatível

- Estado inicial: `coletando_dados`
- Entrada: "Quero fazer um evento aí." (sem tipo, data ou número de convidados)
- Transição esperada: T04 (permanece coletando)
- Estado final: `coletando_dados`
- Resultado de qualificação: `dados_incompletos` com a lista dos campos ausentes
  (invariante I05)
- Ação esperada: perguntar o próximo campo ausente, um por mensagem.
- Ação proibida: classificar como `incompativel` por falta de dados (invariante I09).

## C40 — Resposta comercial concluída com dados faltantes

- Estado inicial: `respondendo_duvidas` (faltam data e número de convidados)
- Entrada: o bot conclui a resposta de preço (`E15`)
- Transição esperada: T20
- Estado final: `coletando_dados`
- Resultado de qualificação: `dados_incompletos`
- Ação esperada: retomar a coleta no próximo campo ausente.
- Ação proibida: encerrar ou encaminhar sem coletar; repetir pergunta já respondida;
  usar "nova mensagem recebida" no lugar do evento interno `E15`.

## C41 — Resposta comercial concluída com dados completos

- Estado inicial: `respondendo_duvidas` (todos os campos obrigatórios registrados e
  compatíveis)
- Entrada: o bot conclui a resposta (`E15`)
- Transição esperada: T21
- Estado final: `pronto_para_handoff`
- Resultado de qualificação: `qualificado`
- Ação esperada: classificar e preparar o resumo do handoff.
- Ação proibida: reiniciar a coleta; perguntar dado já registrado.

## C42 — Mesma pessoa inicia evento diferente

- Estado inicial: `encerrado` (atendimento anterior: casamento em outubro)
- Entrada: "Agora quero orçar um evento corporativo em dezembro."
- Transição esperada: T37 (nova solicitação)
- Estado final: `coletando_dados` (novo atendimento)
- Resultado de qualificação: `dados_incompletos` (novo atendimento)
- Ação esperada: criar novo atendimento sem herdar tipo, data, número de convidados ou
  formato do evento anterior.
- Ação proibida: reutilizar dados comerciais do evento anterior; misturar os dois
  atendimentos; tratar como reabertura.

## C43 — Evento incompatível aceito pelo cliente

- Estado inicial: `coletando_dados`
- Entrada: "É festa infantil." → bot informa a regra; cliente: "Entendi, obrigado."
- Transição esperada: T06 (informa o motivo e aguarda), depois T35 (`E14`)
- Estado final: `encerrado`
- Resultado de qualificação: `incompativel` com motivo objetivo (invariante I04)
- Ação esperada: informar o motivo com cordialidade e encerrar registrando, sem acionar
  Douglas (invariante I18).
- Ação proibida: handoff desnecessário; sugerir exceção; insistir.

## C44 — Preço e todos os dados na primeira mensagem

- Estado inicial: `novo`
- Eventos detectados: `E06` + `E02`+`E03`+`E04`+`E05` + `E07`
- Ordem de processamento relevante: registra todos os dados (passo 3) antes de decidir;
  valida (passos 6–8); qualifica (passo 9); responde o preço (passo 10); decisão única
  (passo 12) — §4 do doc 06, exemplo 1
- Estado final: `pronto_para_handoff`
- Qualificação final: `qualificado` (dados compatíveis)
- Ações esperadas: registrar os dados, responder o preço com o YAML, qualificar e
  preparar o resumo.
- Ações proibidas: perguntar qualquer dado já informado; exigir qualificação antes de
  responder o preço; produzir mais de uma decisão de próximo estado.

## C45 — Dados completos, mas evento incompatível

- Estado inicial: `coletando_dados`
- Eventos detectados: `E02`–`E05` + `E08` + `E07` (ex.: despedida de solteiro com todos
  os campos preenchidos)
- Ordem de processamento relevante: a validação do passo 6 prevalece — `E07` não
  sobrescreve a incompatibilidade (§4, exemplo 2; invariante I20)
- Estado final: conforme T05 (regra com handoff documentado) ou T06 (informa e aguarda)
- Qualificação final: `incompativel` com motivo objetivo
- Ações esperadas: informar a regra e o motivo; registrar o motivo no lead.
- Ações proibidas: classificar como `qualificado` por os dados estarem completos;
  sugerir exceção.

## C46 — Incompatível + pedido de exceção + pedido de humano

- Estado inicial: `coletando_dados`
- Eventos detectados: `E08` + `E17` + `E11` (ambos geram `E18`, motivos
  `excecao_solicitada` e `pedido_humano`)
- Ordem de processamento relevante: passos 4–5 registram os motivos; passo 6 preserva a
  incompatibilidade; decisão única no passo 12 (§4, exemplo 3)
- Estado final: `pronto_para_handoff` (T07)
- Qualificação final: `incompativel` com motivo objetivo preservado
- Ações esperadas: registrar os dois motivos no resumo; informar que o bot não autoriza
  exceções; encaminhar.
- Ações proibidas: prometer exceção; apagar o motivo da incompatibilidade; gerar duas
  decisões de estado.

## C47 — Pedido de desconto durante respondendo_duvidas

- Estado inicial: `respondendo_duvidas`
- Eventos detectados: `E18` motivo `pedido_desconto` (gatilho de
  `docs/04-handoff-humano.md`)
- Ordem de processamento relevante: passo 5 detecta o gatilho obrigatório antes da
  resposta comercial
- Estado final: `pronto_para_handoff` (T24)
- Qualificação final: mantida
- Ações esperadas: recusar com o texto aprovado, registrar o motivo e encaminhar.
- Ações proibidas: negociar; criar condição especial; repetir argumento.

## C48 — Pedido de humano durante aguardando_confirmacao_disponibilidade

- Estado inicial: `aguardando_confirmacao_disponibilidade` (cenário futuro, com
  calendário integrado)
- Eventos detectados: `E11` → `E18` motivo `pedido_humano`
- Ordem de processamento relevante: passo 4 detecta o pedido; a consulta de calendário
  pendente é registrada no resumo
- Estado final: `pronto_para_handoff` (T26)
- Qualificação final: mantida
- Ações esperadas: registrar o motivo; preparar resumo indicando a data pendente de
  consulta.
- Ações proibidas: tentar reter; presumir disponibilidade; descartar a consulta em
  andamento.

## C49 — Resposta concluída em encaminhado_humano

- Estado inicial: `encaminhado_humano`
- Eventos detectados: `E06` (dúvida com resposta aprovada) seguido de `E15`
- Ordem de processamento relevante: passo 10 responde; `E15` não reabre coleta
- Estado final: `encaminhado_humano` (T28, depois T29)
- Qualificação final: mantida
- Ações esperadas: responder, reforçar que Douglas dará sequência e manter o
  encaminhamento.
- Ações proibidas: reiniciar a coleta; retomar negociação; gerar novo handoff.

## C50 — Correção de convidados torna o evento incompatível

- Estado inicial: `coletando_dados` (lead `qualificado`, número anterior dentro do
  limite)
- Eventos detectados: `E04` (correção para valor acima de `capacidade.formato_coquetel`)
  + `E08`
- Ordem de processamento relevante: passo 3 sobrescreve o valor; passos 6 e 9 recalculam
  — o novo resultado substitui a classificação anterior (§4, exemplo 4)
- Estado final: conforme T06 (informa o motivo e aguarda a reação)
- Qualificação final: `incompativel` com motivo objetivo registrado (invariante I04)
- Ações esperadas: informar a capacidade máxima do YAML e o motivo; atualizar o lead.
- Ações proibidas: manter a qualificação antiga; tratar a correção como conversa nova;
  sugerir exceção.

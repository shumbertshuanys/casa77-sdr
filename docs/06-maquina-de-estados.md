# 06 — Máquina de Estados do Atendimento

Especificação conceitual e determinística do fluxo de `docs/02-fluxo-comercial.md`.
Não define código, banco, API, WhatsApp, calendário ou LLM.

> **A máquina não possui constantes comerciais. Todos os limites e condições são
> avaliados a partir do YAML carregado.**

Fonte de toda decisão comercial: `knowledge/casa77.yaml`. Nenhum valor comercial
(preço, capacidade, horário, duração, restrição, quantidade de pacotes) é copiado para
esta máquina — ela referencia os campos do YAML pelo nome e os lê em tempo de execução.
Os valores aprovados aparecem apenas na documentação comercial e nos testes manuais.

## 1. Estados e atributos

### 1.1 Estados da conversa (operacionais)

Uma conversa está em exatamente **um** estado por vez.

| Estado | Significado |
|---|---|
| `novo` | Conversa criada, nenhuma interação processada. |
| `coletando_dados` | Bot coletando os campos obrigatórios de `docs/02-fluxo-comercial.md` §4. |
| `respondendo_duvidas` | Bot respondendo pergunta com base em `knowledge/`. A saída deste estado é sempre por evento explícito (`E15`, `E09`, `E08` ou `E18`). |
| `aguardando_confirmacao_disponibilidade` | Data registrada, aguardando consulta de disponibilidade. **Só é alcançável quando existir integração de calendário** (`integracoes_planejadas.calendario.status` ≠ `pendente`). Enquanto pendente, a verificação vira handoff direto (R05). |
| `pronto_para_handoff` | Gatilho de handoff disparado; resumo em preparação. |
| `encaminhado_humano` | Resumo entregue a Douglas Bianchi; bot em modo restrito (só respostas aprovadas + reforço de que Douglas dará sequência). |
| `atendimento_humano` | Douglas assumiu a conversa; **resposta automática bloqueada**. |
| `encerrado` | Atendimento finalizado (lead entregue ou sem continuidade registrada). |

### 1.2 Resultado de qualificação (`resultado_qualificacao`)

Atributo do lead que classifica a **compatibilidade do evento**. Evolui em paralelo ao
estado da conversa. Os cinco valores oficiais estão em `docs/02-fluxo-comercial.md` §6:
`dados_incompletos` (valor inicial), `qualificado`, `qualificado_com_ressalva`,
`incompativel`, `indefinido`.

Uso de `indefinido`: **somente** quando o dado pendente impede a própria decisão de
compatibilidade ou classificação do evento. Pergunta acessória sem resposta aprovada
não altera a classificação — vai para `pendencias_resposta` (§1.3).

Regra de separação: estado da conversa responde "**onde a conversa está**";
`resultado_qualificacao` responde "**o evento é compatível?**". Nunca usar um no lugar
do outro. Exemplo: uma conversa em `respondendo_duvidas` pode ter lead
`dados_incompletos`, `qualificado` ou `incompativel` — são eixos independentes.

### 1.3 Pendências de resposta (`pendencias_resposta`)

Atributo paralelo do lead: lista de perguntas do interessado que não puderam ser
respondidas por falta de dado aprovado (campo `null`/`pendente` no YAML ou sem resposta
aprovada).

Regras:

- pergunta acessória pendente (ex.: `estrutura.suite_noiva.valor`) **não** substitui
  automaticamente um lead `qualificado` por `indefinido`;
- a pergunta é registrada em `pendencias_resposta` e entra no resumo do handoff
  ("Perguntas em aberto" de `docs/04-handoff-humano.md`);
- o handoff é gerado quando exigido pelos gatilhos de `docs/04-handoff-humano.md`
  (pergunta sem resposta aprovada e campo pendente são os gatilhos 1 e 2);
- `resultado_qualificacao = indefinido` fica reservado ao caso em que a pendência
  impede a classificação do evento.

## 2. Eventos de transição

| Código | Evento | Origem |
|---|---|---|
| `E01` | nova mensagem recebida | interessado |
| `E02` | tipo de evento informado | interessado |
| `E03` | data informada | interessado |
| `E04` | número de convidados informado | interessado |
| `E05` | formato informado (sentado/coquetel) | interessado |
| `E06` | pergunta comercial recebida | interessado |
| `E07` | dados mínimos completos | interno |
| `E08` | regra incompatível detectada (contra o YAML) | interno |
| `E09` | informação pendente detectada (`null`/`pendente` no YAML) | interno |
| `E10` | interesse em visita | interessado |
| `E11` | pedido de atendimento humano — **gera internamente `E18`** com motivo `pedido_humano` | interessado |
| `E12` | resumo gerado | interno |
| `E13` | humano assumiu | operação |
| `E14` | conversa encerrada | interessado/operação |
| `E15` | `resposta_comercial_concluida` — resposta comercial concluída | interno |
| `E16` | `retorno_consulta_calendario` — retorno da consulta de calendário | integração |
| `E17` | `excecao_solicitada` — pedido de exceção ou contestação de regra — **gera internamente `E18`** com motivo `excecao_solicitada` | interessado |
| `E18` | `handoff_obrigatorio_detectado` — gatilho obrigatório de handoff detectado (carrega motivo) | interno |

Os eventos `E02`–`E05` são **eventos de dado**: podem ocorrer em qualquer ordem,
isolados ou vários numa única mensagem. Cada dado recebido é registrado uma única vez e
nunca é perguntado novamente (ver §6). `E15` e `E16` são eventos internos explícitos —
`E01` (nova mensagem) nunca é usado para representar uma resposta concluída ou um
retorno de integração.

### 2.1 `E18` — `handoff_obrigatorio_detectado`

Evento interno emitido quando qualquer gatilho obrigatório de
`docs/04-handoff-humano.md` é detectado. Carrega sempre um **motivo** enumerado ou
textual aprovado:

- `pedido_humano`;
- `pedido_desconto`;
- `contratacao`;
- `cancelamento`;
- `alteracao_data`;
- `interpretacao_contratual`;
- `informacao_pendente`;
- `excecao_solicitada`;
- outro gatilho presente em `docs/04-handoff-humano.md`.

`E18` **não duplica regras comerciais**: apenas registra o motivo e consulta o
documento de handoff, que continua sendo a fonte dos gatilhos.

`E11` e `E17` são eventos de origem do interessado que geram internamente `E18` (com os
motivos `pedido_humano` e `excecao_solicitada`). Não existem transições separadas para
`E11`/`E17` — o caminho único de handoff obrigatório é via `E18`, sem caminhos
concorrentes contraditórios.

## 3. Tabela de transições

Convenções: "—" = não se aplica; a coluna Qualificação indica `resultado_qualificacao`
e só é preenchida quando o evento o altera; ações proibidas de
`docs/03-regras-de-conversa.md` valem em todos os estados e não são repetidas linha a
linha.

| # | Estado atual | Evento | Condição | Próximo estado | Ação obrigatória | Ação proibida | Qualificação |
|---|---|---|---|---|---|---|---|
| T01 | `novo` | `E01` | mensagem é primeiro contato | `coletando_dados` | apresentar-se como atendimento inicial; extrair dados já presentes na mensagem | apresentar-se como Douglas ou humano | `dados_incompletos` (inicial) |
| T02 | `novo` | `E06` | pergunta comercial na 1ª mensagem | `respondendo_duvidas` | responder de imediato com o YAML (preço incluso — `proposta.preco_pode_ser_informado_imediatamente`) | exigir dados antes de responder preço | `dados_incompletos` (inicial) |
| T03 | `novo` | `E18` | qualquer motivo | `pronto_para_handoff` | registrar o motivo; preparar resumo mesmo incompleto | tentar reter o interessado | mantém |
| T04 | `coletando_dados` | `E02`/`E03`/`E04`/`E05` | dado compatível com o YAML | `coletando_dados` | registrar o dado; perguntar apenas o próximo campo ausente | repetir pergunta já respondida | recalcular (segue `dados_incompletos` se faltar campo) |
| T05 | `coletando_dados` | `E08` | regra violada cujo tratamento documentado exige handoff (ex.: data em `eventos.datas_nao_aceitas` — `docs/02-fluxo-comercial.md`) | `pronto_para_handoff` | informar a regra objetiva com o motivo; registrar o motivo no lead | sugerir exceção; tratar dado ausente como incompatível | `incompativel` (com motivo objetivo) |
| T06 | `coletando_dados` | `E08` | demais regras objetivas violadas (tipo em `eventos.nao_aceitos`; convidados acima de `capacidade.formato_coquetel`) | `coletando_dados` | informar a regra objetiva com o motivo; registrar o motivo; aguardar a reação do interessado | sugerir exceção; encaminhar sem necessidade | `incompativel` (com motivo objetivo) |
| T07 | `coletando_dados` | `E18` | qualquer motivo | `pronto_para_handoff` | registrar o motivo; preparar resumo; preservar qualificação, incompatibilidade e pendências já detectadas | tentar reter; apagar motivo ou pendência anterior | mantém |
| T08 | `coletando_dados` | `E04`+`E05` | convidados acima de `capacidade.convidados_sentados` e até `capacidade.formato_coquetel`, formato sentado | `pronto_para_handoff` | explicar que o limite sentado é `capacidade.convidados_sentados`; encaminhar para decisão humana | afirmar que algum pacote de `precos.pacotes` libera formato sentado acima do limite | `qualificado_com_ressalva` |
| T09 | `coletando_dados` | `E04` | convidados acima de `capacidade.convidados_sentados` e até `capacidade.formato_coquetel`, formato não informado | `coletando_dados` | perguntar o formato antes de indicar pacote | assumir formato; indicar pacote | `dados_incompletos` |
| T10 | `coletando_dados` | `E06` | resposta existe no YAML/respostas aprovadas | `respondendo_duvidas` | responder; ao concluir, emitir `E15` | reiniciar a coleta | mantém |
| T11 | `coletando_dados` | `E09` | a pendência impede a classificação do evento | `pronto_para_handoff` | aplicar R03; registrar a pergunta em `pendencias_resposta` | inventar; usar conhecimento genérico | `indefinido` |
| T12 | `coletando_dados` | `E09` | pendência acessória (não impede a classificação) | `pronto_para_handoff` | aplicar R03; registrar a pergunta em `pendencias_resposta` | rebaixar a qualificação para `indefinido`; inventar | mantém |
| T13 | `coletando_dados` | `E07` | todos os campos obrigatórios presentes e compatíveis, após as validações do §4 | `pronto_para_handoff` | classificar conforme `docs/02-fluxo-comercial.md` §6.1; preparar resumo | concluir contratação; confirmar data; sobrescrever incompatibilidade detectada | `qualificado` ou `qualificado_com_ressalva` conforme regras |
| T14 | `coletando_dados` | `E03` | interessado quer confirmar disponibilidade **e** calendário integrado | `aguardando_confirmacao_disponibilidade` | registrar a data; consultar o calendário | afirmar livre/ocupado sem consulta | mantém |
| T15 | `coletando_dados` | `E03` | interessado quer confirmar disponibilidade **e** calendário `pendente` | `pronto_para_handoff` | aplicar R05; registrar a data | presumir disponibilidade | mantém |
| T16 | `coletando_dados` | `E10` | — | `coletando_dados` | registrar interesse; informar a duração estimada (`processo_comercial.visitas.duracao_estimada_minutos`) e o responsável (`processo_comercial.visitas.responsavel_visita`) | marcar, sugerir horário ou confirmar visita | mantém |
| T17 | `respondendo_duvidas` | `E06` | resposta aprovada existe | `respondendo_duvidas` | responder com o YAML | estimar, comparar, opinar | mantém |
| T18 | `respondendo_duvidas` | `E09` | a pendência impede a classificação do evento | `pronto_para_handoff` | aplicar R03; registrar em `pendencias_resposta` | inventar resposta | `indefinido` |
| T19 | `respondendo_duvidas` | `E09` | pendência acessória (não impede a classificação) | `pronto_para_handoff` | aplicar R03; registrar em `pendencias_resposta` | rebaixar a qualificação para `indefinido`; inventar | mantém |
| T20 | `respondendo_duvidas` | `E15` | ainda faltam campos obrigatórios | `coletando_dados` | retomar a coleta sem repetir perguntas | reiniciar do zero | mantém |
| T21 | `respondendo_duvidas` | `E15` | dados completos e compatíveis | `pronto_para_handoff` | classificar e preparar o resumo | reiniciar a coleta | `qualificado` ou `qualificado_com_ressalva` conforme regras |
| T22 | `respondendo_duvidas` | `E08` | regra violada cujo tratamento documentado exige handoff | `pronto_para_handoff` | informar a regra com o motivo; registrar | negociar exceção | `incompativel` (com motivo objetivo) |
| T23 | `respondendo_duvidas` | `E08` | demais regras objetivas violadas | `respondendo_duvidas` | informar a regra com o motivo; registrar; aguardar a reação | sugerir exceção; encaminhar sem necessidade | `incompativel` (com motivo objetivo) |
| T24 | `respondendo_duvidas` | `E18` | qualquer motivo (ex.: `pedido_desconto`, `excecao_solicitada`) | `pronto_para_handoff` | registrar o motivo; preparar resumo; preservar qualificação e pendências já detectadas | tentar reter; negociar | mantém |
| T25 | `aguardando_confirmacao_disponibilidade` | `E16` | resultado retornado pela integração | `pronto_para_handoff` | registrar o resultado; encaminhar para confirmação humana | confirmar reserva | mantém |
| T26 | `aguardando_confirmacao_disponibilidade` | `E18` | qualquer motivo | `pronto_para_handoff` | registrar o motivo; preparar resumo com a data pendente de consulta | tentar reter; presumir disponibilidade | mantém |
| T27 | `pronto_para_handoff` | `E12` | resumo no formato de `docs/04-handoff-humano.md` | `encaminhado_humano` | entregar resumo; enviar mensagem padrão de handoff | prometer prazo de retorno (SLA pendente) | mantém |
| T28 | `encaminhado_humano` | `E06` | dúvida com resposta aprovada | `encaminhado_humano` | responder e reforçar que Douglas dará sequência | negociar; contradizer Douglas | mantém |
| T29 | `encaminhado_humano` | `E15` | — | `encaminhado_humano` | manter o encaminhamento; não reiniciar coleta | reabrir coleta; retomar negociação | mantém |
| T30 | `encaminhado_humano` | `E18` | novo gatilho após o encaminhamento | `encaminhado_humano` | registrar o novo motivo ou pedido para Douglas | gerar novo handoff duplicado; negociar | mantém |
| T31 | `encaminhado_humano` | `E13` | — | `atendimento_humano` | silenciar resposta automática | responder automaticamente | mantém |
| T32 | `encaminhado_humano` | `E14` | — | `encerrado` | registrar desfecho | — | mantém |
| T33 | `atendimento_humano` | `E01` | inclusive quando a mensagem contém gatilho `E18` | `atendimento_humano` | registrar a mensagem (e o eventual motivo) para o humano | qualquer resposta automática | mantém |
| T34 | `atendimento_humano` | `E14` | — | `encerrado` | registrar desfecho | — | mantém |
| T35 | qualquer exceto `atendimento_humano` | `E14` | sem interesse / engano / spam / incompatibilidade aceita sem pedido de exceção nem de humano | `encerrado` | aplicar R15 quando couber; registrar sem acionar Douglas | acionar handoff desnecessário; insistir | mantém |
| T36 | `encerrado` | `E01` | mensagem se refere ao **mesmo evento** do atendimento anterior | `coletando_dados` | reabrir o atendimento preservando dados e qualificação já registrados | criar atendimento duplicado; perguntar tudo de novo | mantém a anterior; recalcular se houver dado novo |
| T37 | `encerrado` | `E01` | mensagem se refere a uma **nova solicitação** (outro evento) | `coletando_dados` | criar **novo atendimento** (novo EventInquiry conceitual); não reutilizar tipo, data, convidados nem formato do atendimento anterior | herdar dados comerciais do atendimento anterior; misturar atendimentos | `dados_incompletos` (novo atendimento) |

Notas:

- **Mensagem repetida** (mesmo conteúdo reenviado dentro de um atendimento ativo): não é
  transição — a máquina permanece no estado atual, não duplica registro nem resposta.
- **Identificação de mesmo evento vs. nova solicitação** (T36/T37): o critério técnico
  de identificação será definido na etapa de modelo de dados. Esta máquina define apenas
  o comportamento de cada caso. A distinção entre entidades (conversa, atendimento,
  lead) também pertence à etapa de modelo de dados.

## 4. Ordem de processamento de uma mensagem

Uma mensagem pode conter vários dados e intenções ao mesmo tempo. O processamento segue
**sempre** a ordem abaixo. A mensagem pode registrar vários eventos e efeitos, mas
produz **uma única decisão final de próximo estado**.

1. receber a mensagem e verificar duplicidade/idempotência — mensagem repetida encerra
   o ciclo sem nenhum efeito;
2. extrair **todos** os dados e intenções presentes;
3. registrar correções e novos dados (`E02`–`E05`), sobrescrevendo valores corrigidos;
4. verificar pedido explícito de humano (`E11` → `E18` motivo `pedido_humano`);
5. verificar pedido de exceção (`E17` → `E18` motivo `excecao_solicitada`) ou outro
   gatilho obrigatório de handoff de `docs/04-handoff-humano.md` (`E18` com o motivo
   correspondente);
6. validar regras incompatíveis do YAML (`E08`);
7. verificar pendências que impedem a classificação (`E09` impeditivo);
8. verificar campos obrigatórios e o formato condicional;
9. recalcular `resultado_qualificacao`;
10. responder às perguntas comerciais aprovadas (`E06`, concluindo com `E15`);
11. registrar `pendencias_resposta` (`E09` acessório);
12. definir o próximo estado — **única decisão final** — e gerar o resumo quando
    necessário (`E12`).

Regras de precedência:

- **incompatibilidade objetiva não pode ser sobrescrita por `E07`**: se o passo 6
  detectar violação, o passo 9 nunca produz `qualificado` ou
  `qualificado_com_ressalva`;
- `E07` só produz qualificação positiva depois de todas as validações dos passos 4–8;
- pedido de humano gera handoff, mas **preserva** qualquer incompatibilidade ou
  pendência já detectada — motivo e pendências seguem no resumo;
- vários dados na mesma mensagem são registrados (passo 3) **antes** de o bot decidir
  qual pergunta fazer;
- a ordem em que o extrator encontrou as intenções na mensagem **não altera o
  resultado** — a precedência é sempre a deste ciclo;
- uma mensagem resulta em **uma única decisão final** de próximo estado.

Exemplos:

| # | Mensagem | Eventos detectados | Processamento | Decisão final |
|---|---|---|---|---|
| 1 | Pergunta de preço junto com todos os dados obrigatórios | `E06` + `E02`–`E05` + `E07` | registra os dados (passo 3); nenhum gatilho (4–5); sem violação (6); sem pendência (7); campos completos (8); qualifica (9); responde o preço (10) | `pronto_para_handoff` com `resultado_qualificacao` calculado — sem perguntar nada já informado |
| 2 | Evento incompatível com todos os campos preenchidos | `E02`–`E05` + `E08` + `E07` | a violação do passo 6 prevalece; o passo 9 mantém `incompativel` mesmo com dados completos | conforme T05 (handoff documentado) ou T06 (informa e aguarda), com motivo objetivo |
| 3 | Incompatibilidade + pedido de exceção + pedido de humano | `E08` + `E17` + `E11` (→ `E18`) | motivos `pedido_humano` e `excecao_solicitada` registrados (4–5); incompatibilidade preservada (6) | `pronto_para_handoff`, `incompativel` com motivo — sem promessa de exceção |
| 4 | Correção do número de convidados que muda a qualificação | `E04` (correção) + `E08` ou recálculo | o novo valor sobrescreve o anterior (passo 3); a validação (6) e o recálculo (9) substituem a classificação anterior | transição correspondente ao novo resultado, com motivo objetivo quando `incompativel` |

## 5. Regras obrigatórias da máquina

1. **A máquina não possui constantes comerciais. Todos os limites e condições são
   avaliados a partir do YAML carregado** no momento da decisão.
2. **Ausência de dado nunca é incompatibilidade.** Falta de campo obrigatório →
   `dados_incompletos`; `incompativel` exige regra objetiva do YAML violada.
3. **Preço é informado de imediato quando solicitado**, em qualquer estado em que o bot
   responde (`proposta.preco_pode_ser_informado_imediatamente`).
4. **Disponibilidade nunca é presumida.** Sem integração de calendário, toda verificação
   vira R05 + handoff (T15); com integração, o resultado (`E16`) ainda passa por
   confirmação humana (T25).
5. **Visita nunca é confirmada pelo bot** (`processo_comercial.visitas.bot_pode_confirmar`).
   O bot só registra o interesse (T16).
6. **Contratação, descontos, cancelamento e alteração de data exigem humano** — gatilhos
   de `docs/04-handoff-humano.md`, detectados como `E18` com o motivo correspondente;
   qualquer um dispara `pronto_para_handoff`.
7. **Pendência impeditiva** (`null`/`pendente` que bloqueia a classificação) →
   `indefinido` + handoff (T11/T18). **Pendência acessória** → `pendencias_resposta`,
   qualificação mantida, handoff conforme os gatilhos (T12/T19).
8. **Convidados acima de `capacidade.formato_coquetel`** → `incompativel` (T06).
9. **Incompatibilidade não gera handoff automático universal.** Informada a regra e o
   motivo: aceite do interessado sem pedido de exceção nem de humano → `encerrado`
   (T35); pedido de exceção ou de humano (`E18`) → `pronto_para_handoff` (T07/T24);
   regras cujo tratamento documentado já exige handoff continuam valendo (T05/T22).
   Nunca sugerir exceção.
10. **Na faixa entre `capacidade.convidados_sentados` e `capacidade.formato_coquetel`, o
    formato segue o YAML**: coquetel → `qualificado` com o pacote correspondente de
    `precos.pacotes`; sentado → `qualificado_com_ressalva` + handoff (T08); não
    informado → `dados_incompletos` (T09).
11. **Quando o humano assume (`E13`), o bot para de responder automaticamente** — o
    estado `atendimento_humano` não possui transição de resposta do bot.
12. **Dentro de um atendimento ativo, mensagens repetidas e subsequentes não criam nova
    conversa.** Após `encerrado`, identificar se a mensagem trata do mesmo evento
    (reabrir preservando dados — T36) ou de nova solicitação (novo atendimento sem
    reutilizar dados comerciais do atendimento anterior — T37).

## 6. Ordem de coleta

Ordem **recomendada, não rígida**:

1. nome;
2. telefone — obtido automaticamente pelo canal quando disponível (WhatsApp fornece);
   só perguntar se o canal não fornecer;
3. tipo de evento;
4. data pretendida;
5. número de convidados;
6. formato — **somente** quando exigido: número de convidados acima de
   `capacidade.convidados_sentados` e até `capacidade.formato_coquetel`;
7. interesse em visita;
8. dúvidas principais.

Regras de aproveitamento:

- Todo dado presente em qualquer mensagem é registrado imediatamente, mesmo fora de ordem.
- Antes de perguntar, verificar o que já foi registrado; **nunca repetir pergunta
  desnecessariamente**.
- Uma pergunta por mensagem (`docs/03-regras-de-conversa.md`).
- Correção de dado pelo interessado sobrescreve o valor anterior e força recálculo da
  qualificação (ver §7).

## 7. Casos fora de ordem

| Caso | Comportamento |
|---|---|
| Pergunta só o preço | T02: informar os pacotes de `precos.pacotes` de imediato; em seguida perguntar o número de convidados para indicar o pacote aplicável. Não exigir qualificação antes. |
| Pergunta o endereço | Responder de imediato (`localizacao.pode_informar_endereco_antes_qualificacao`); retomar a coleta. |
| Pede visita | T16: registrar interesse, informar a duração estimada e o responsável a partir de `processo_comercial.visitas`. Não marcar. A visita entra no resumo do handoff. |
| Informa todos os dados numa mensagem | Registrar todos de uma vez (`E02`+`E03`+`E04`+`E05`); se `E07` for satisfeito após as validações do §4, ir direto a `pronto_para_handoff` sem perguntar nada já informado. |
| Pede humano imediatamente | T03/T07 (`E18` motivo `pedido_humano`): handoff imediato com resumo parcial marcando os campos ausentes. Não reter. |
| Mensagem incompleta ou ambígua | Permanecer no estado atual; pedir esclarecimento do ponto ambíguo; não registrar dado incerto. |
| Corrige informação anterior | Sobrescrever o dado, recalcular a qualificação (§4, passos 3 e 9) e, se o resultado mudar (ex.: o novo número de convidados passa a exceder `capacidade.convidados_sentados`), aplicar a transição correspondente (T09). Não tratar como conversa nova. |
| Mensagens repetidas | Idempotência: mesma mensagem reenviada não gera nova resposta, novo registro nem nova transição (§4, passo 1). |

## 8. Invariantes (base para testes automatizados futuros)

| # | Invariante |
|---|---|
| I01 | Nenhum estado confirma reserva, visita, data ou contrato. |
| I02 | Nenhum estado concede desconto, condição especial ou parcelamento fora do YAML. |
| I03 | Em `atendimento_humano` o bot não emite nenhuma resposta automática. |
| I04 | Todo lead `incompativel` carrega um motivo objetivo rastreável a um campo do YAML. |
| I05 | Todo lead `dados_incompletos` carrega a lista dos campos obrigatórios ainda ausentes. |
| I06 | Nenhuma informação comercial (preço, capacidade, horário, duração, restrição, quantidade de pacotes) existe como constante da máquina — toda decisão lê `knowledge/casa77.yaml`. |
| I07 | `resultado_qualificacao` assume somente os cinco valores oficiais. |
| I08 | O estado da conversa assume somente os oito valores da §1.1. |
| I09 | Ausência de dado nunca produz `incompativel`. |
| I10 | `indefinido` ocorre somente quando a pendência impede a classificação do evento, e referencia o item pendente que a causou. |
| I11 | Pergunta pendente não sobrescreve automaticamente a qualificação: toda pergunta não respondida consta em `pendencias_resposta` e no resumo do handoff. |
| I12 | `encaminhado_humano` só é alcançado após resumo entregue (`E12`). |
| I13 | `atendimento_humano` só é alcançado após o humano assumir (`E13`). |
| I14 | Mensagens de um atendimento ativo não criam nem duplicam conversa. |
| I15 | Retorno após `encerrado` é continuação (mesmo evento → reabre preservando dados) ou nova solicitação (novo atendimento, sem herdar dados comerciais do atendimento anterior). |
| I16 | Nenhuma pergunta obrigatória é feita duas vezes quando o dado já foi registrado. |
| I17 | `aguardando_confirmacao_disponibilidade` é inalcançável enquanto `integracoes_planejadas.calendario.status` for `pendente`. |
| I18 | `incompativel` não gera handoff automático universal: handoff ocorre somente por regra documentada específica ou por `E18` (pedido de humano, exceção/contestação ou outro gatilho obrigatório). |
| I19 | Uma mensagem produz uma única decisão final de próximo estado, seguindo a ordem obrigatória do §4; a ordem de extração das intenções não altera o resultado. |
| I20 | Incompatibilidade objetiva nunca é sobrescrita por `E07`; todo `E18` carrega um motivo registrado. |

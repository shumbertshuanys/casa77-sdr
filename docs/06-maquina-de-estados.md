# 06 — Máquina de Estados do Atendimento

Especificação conceitual e determinística do fluxo de `docs/02-fluxo-comercial.md`.
Não define código, banco, API, WhatsApp, calendário ou LLM.

> **A máquina não possui constantes comerciais. Todos os limites e condições são
> avaliados contra o YAML carregado — porém *a montante* da máquina, nunca por ela.**

Fonte de toda decisão comercial: `knowledge/casa77.yaml`. Nenhum valor comercial
(preço, capacidade, horário, duração, restrição, quantidade de pacotes) é copiado para
esta máquina.

A `MaquinaEstados` **não lê o YAML**. A avaliação comercial acontece **a montante**,
contra a base carregada, e chega à máquina já pronta: **eventos confirmados**,
`Qualificacao` e **condições já estruturadas** (§2.2, §4.1). Os caminhos de campo do YAML
que aparecem nas tabelas deste documento (`capacidade.…`, `precos.…`, `eventos.…`) são
**rastreabilidade documental** — indicam de onde o fato veio na avaliação a montante — e
**nunca instrução de leitura pela máquina**.

Os valores aprovados aparecem apenas na documentação comercial e nos testes manuais.

## 1. Estados e atributos

### 1.1 Estados da conversa (operacionais)

Uma conversa está em exatamente **um** estado por vez.

| Estado | Significado |
|---|---|
| `novo` | Conversa criada, nenhuma interação processada. |
| `coletando_dados` | Bot coletando os campos obrigatórios de `docs/02-fluxo-comercial.md` §4. |
| `respondendo_duvidas` | Bot respondendo pergunta com base em `knowledge/`. A saída deste estado ocorre **sempre por evento explicitamente declarado para ele na §3** — hoje `E15`, `E09`, `E08`, `E18`, `E01` (T39) e `E07` (T40). Não existe saída implícita, e a §3 é a lista completa: nenhuma enumeração menor é normativa. |
| `aguardando_confirmacao_disponibilidade` | Data registrada, aguardando consulta de disponibilidade. **Só é alcançável quando existir integração de calendário** (`integracoes_planejadas.calendario.status` ≠ `pendente`). Enquanto pendente, a verificação vira handoff direto (R05). |
| `pronto_para_handoff` | **Estado intermediário do ciclo**: gatilho de handoff disparado e resumo **ainda em preparação**. Não afirma que o resumo já existe, que foi persistido nem que chegou a Douglas Bianchi. |
| `encaminhado_humano` | **Handoff REGISTRADO**: resumo gerado (`E12`) e decisão de encaminhamento persistida. **Não** significa confirmação física de recebimento por Douglas Bianchi (§10). Bot em modo restrito (só respostas aprovadas + reforço de que Douglas dará sequência). |
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
| `E09` | pendência determinística já confirmada: campo relevante `null`/`pendente` no YAML **ou** ausência de resposta aprovada (§2.2) | interno |
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

### 2.2 Semântica de confirmação dos eventos internos

Esta seção preserva integralmente `E01`–`E18` e **não cria evento novo**. Ela fixa
*quando* cada evento interno pode ser considerado **confirmado**, eliminando a ambiguidade
que impedia especificar a `MaquinaEstados` sem improviso.

#### `E07` — dados mínimos completos

`E07` só é confirmado quando **as duas** condições valem no mesmo ciclo:

a) houve **mutação efetiva** de um insumo de `DadosQualificacao` neste ciclo —
   `insumo_qualificacao_atualizado = verdadeiro` (§4.1); **e**
b) o `resultado_qualificacao` recalculado é `qualificado` **ou**
   `qualificado_com_ressalva`.

Consequências:

- `E07` **não** é confirmado em caminho resolvido por `E08` nem por `E09` impeditiva — a
  precedência do §4 já decidiu, e `E07` nunca sobrescreve incompatibilidade (I20);
- **`E06` puro em lead já qualificado não gera `E07`**: perguntar não altera insumo de
  qualificação, e reconfirmar um resultado já vigente não é mutação;
- `E07` é **consumido uma única vez por ciclo** (§4.2, família C8).

#### `E09` — pendência determinística já confirmada

`E09` chega à máquina **pronto**: pendência determinística **já detectada e já
classificada** a montante. Abrange dois casos:

a) campo relevante `null`/`pendente` na base;
b) ausência de resposta aprovada para a pergunta feita.

A classificação **impeditiva × acessória** (§1.3) acompanha o evento e é o que separa
T11/T18 de T12/T19. A máquina **não detecta**, **não reclassifica** e **não recalcula**
pendência.

O **produtor concreto** de `E09` **não é atribuído** nesta arbitragem — em particular,
**não** é o `CarregadorYaml` e **não** é o `ValidadorYaml`. O contrato do produtor é a
pendência aberta **S2-D8** (§11).

#### `E15` — resposta comercial concluída

`E15` significa **resposta comercial efetivamente concluída**, nunca intenção de
responder. É confirmado **fora** da `MaquinaEstados` e **somente depois do efeito real**;
só então retorna à máquina, no fechamento do ciclo (§4.2).

#### `E12` — resumo gerado

`E12` significa **resumo efetivamente gerado**. É confirmado **fora** da `MaquinaEstados`
e **somente depois do efeito real**. `E12` não afirma entrega ao humano (§10).

#### `E13` — humano assumiu

`E13` é **evento operacional** e chega em **ciclo próprio**, isolado. Não compõe o ciclo
de processamento de uma mensagem do interessado.

#### `E11` / `E17`

Continuam **reduzidos a `E18`** conforme o contrato já existente da §2.1. Não ganham
transição própria.

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
| T08 | `coletando_dados` | `E07` | `resultado_qualificacao` = `qualificado_com_ressalva` | `pronto_para_handoff` | `INFORMAR_RESSALVA_DE_CAPACIDADE`; encaminhar para decisão humana — a máquina emite a ação, e a redação do fato de capacidade cabe ao `SeletorFatos` | afirmar que algum pacote de `precos.pacotes` libera formato sentado acima do limite | `qualificado_com_ressalva` (recebido, não recalculado) |
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
| T38 | `respondendo_duvidas` | `E15` | `resultado_qualificacao` em `incompativel` ou `indefinido` | `respondendo_duvidas` | nenhuma nova ação conversacional; manter o estado e aguardar a reação/continuidade do interessado | reabrir coleta; encaminhar sem gatilho; sugerir exceção; sobrescrever a classificação | mantém |
| T39 | `respondendo_duvidas` | `E01` | `insumo_qualificacao_atualizado` = verdadeiro **e** `resultado_qualificacao` = `dados_incompletos` **e** nenhum `E06` no ciclo | `coletando_dados` | retomar a coleta sem repetir perguntas | reiniciar do zero; repetir pergunta já respondida | mantém (`dados_incompletos`) |
| T40 | `respondendo_duvidas` | `E07` | `resultado_qualificacao` em `qualificado` ou `qualificado_com_ressalva` | `pronto_para_handoff` | preparar resumo | reabrir coleta; concluir contratação; sobrescrever incompatibilidade detectada | `qualificado` ou `qualificado_com_ressalva` (recebido, não recalculado) |
| T41 | `coletando_dados` | `E01` | `insumo_qualificacao_atualizado` = verdadeiro **e** `resultado_qualificacao` = `dados_incompletos` **e** nenhum `E02`–`E05` no ciclo | `coletando_dados` | perguntar somente o próximo campo ausente | repetir pergunta já respondida; assumir dado não informado | mantém (`dados_incompletos`) |

Notas:

- **Mensagem repetida** (mesmo conteúdo reenviado dentro de um atendimento ativo): não é
  transição — a máquina permanece no estado atual, não duplica registro nem resposta.
- **T08, T38, T39, T40 e T41** vêm da arbitragem documental S2. T08 passou a ser decidida
  pelo `resultado_qualificacao` já calculado, e não por leitura de convidados, formato ou
  YAML: a semântica permanece a mesma (ressalva de capacidade → decisão humana), mas a
  máquina consome a classificação do `Qualificador` em vez de recalculá-la.
- **A máquina não lê convidados, formato nem YAML** para decidir T08. Toda condição de
  qualificação chega pronta em `resultado_qualificacao` (§1.2).
- A ordem em que estas linhas são avaliadas dentro de um ciclo está fixada em §4.2; os
  efeitos que sobrevivem a outra decisão de estado estão em §4.3; os casos em que um
  evento legítimo não transiciona estão em §4.4.
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

### 4.1 Sinal técnico `insumo_qualificacao_atualizado`

```text
insumo_qualificacao_atualizado: bool | None
```

É **condição** de transição, **não evento**. Nunca aparece na coluna Evento da §3 e nunca
é contado entre `E01`–`E18`.

Vale `verdadeiro` **somente** quando houve **mutação efetiva** de um insumo de
`DadosQualificacao`, comparada ao **contexto recuperado** (doc 07 §6.2):

- campo antes ausente passou a presente; **ou**
- valor já existente efetivamente mudou ou foi corrigido.

Insumos cobertos — todos os de `DadosQualificacao`:

| Insumo |
|---|
| nome |
| contato |
| tipo |
| data |
| convidados |
| formato |

Regras:

- **repetição de valor já conhecido não conta.** Reenviar o mesmo dado não é mutação e
  não torna o sinal verdadeiro. Presença repetida ≠ mutação efetiva;
- o sinal é **apenas booleano**: não registra valor, dado pessoal (PII) nem conteúdo da
  mensagem;
- `None` significa "não avaliado neste ciclo" e **não** equivale a `verdadeiro`;
- **o sinal não é equivalente a `E02`–`E05`** e não os substitui. Não existe equivalência
  entre eles: nome e contato, por exemplo, movem o sinal sem produzir qualquer evento de
  dado;
- **T04 e T09 continuam consumindo exclusivamente os eventos declarados nas próprias
  linhas** (`E02`–`E05` e `E04`). Nenhuma das duas foi ampliada para nome ou contato.

Roteamento de nome e contato novos ou corrigidos — sem falsificar `E02`–`E05`:

| Situação | Rota |
|---|---|
| estado `coletando_dados`, resultado segue `dados_incompletos` | T41 (perguntar só o próximo campo ausente) |
| estado `respondendo_duvidas`, resultado segue `dados_incompletos`, sem `E06` no ciclo | T39 (retomar a coleta sem repetir perguntas) |
| resultado recalculado vira `qualificado` ou `qualificado_com_ressalva` | `E07` confirmado (§2.2) → T08, T13 ou T40 conforme o estado de origem e a condição |

### 4.2 Ordem de avaliação das transições no ciclo

A lista de passos acima define a ordem de **processamento da mensagem**. Esta seção define
a ordem de **avaliação das transições da §3** dentro do mesmo ciclo. Ela é fechada e
determinística.

#### Semântica de caminho

O ciclo **não** para na primeira família aplicável. Ele percorre um **caminho**:

| # | Regra do caminho |
|---|---|
| 1 | percorrer as famílias **C0 → C11 na ordem**; |
| 2 | quando uma transição se aplica, ela **atualiza o estado intermediário**; |
| 3 | a avaliação **continua** pelas famílias seguintes, agora **a partir desse estado intermediário**; |
| 4 | o caminho **pode conter mais de uma `Txx`**; |
| 5 | ao final do ciclo existe **um único estado final** (I19), e é ele que a etapa 13 do doc 07 persiste; |
| 6 | o caminho percorrido é **auditável**: a sequência de `Txx` aplicadas é registrada. |

Os efeitos paralelos **P1–P6** (§4.3) e as inércias **N1–N4** (§4.4) continuam valendo
**exatamente nas hipóteses enumeradas** — nem uma a mais.

#### Consumo único

| # | Regra de consumo |
|---|---|
| 1 | cada **evento confirmado** é consumido **no máximo uma vez** como gatilho de transição no ciclo; |
| 2 | cada **`Txx`** entra no caminho **no máximo uma vez**. |

Consequências diretas, entre outras:

- se T01 consumiu o `E01` de abertura, **T41 não reutiliza o mesmo `E01`**;
- se T39 consumiu o `E01`, **T41 não o reutiliza** — T39 e T41 nunca disparam ambas pelo
  mesmo `E01`;
- se T02 consumiu o `E06` da primeira mensagem, **o mesmo `E06` não é reutilizado em C9**;
- `E07` segue a mesma regra: T08, T13 e T40 nunca se aplicam duas vezes pelo mesmo `E07`
  (C8).

O consumo do evento como **gatilho** não apaga o que P1–P6 preservam: obrigações e efeitos
(registro de dado, obrigação de responder `E06`, incompatibilidade, pendência, ressalva)
**sobrevivem** ao consumo, conforme a hipótese enumerada em §4.3.

| Ordem | Família | Transições | Observação |
|---|---|---|---|
| C0 | abertura no estado `novo` | T03 > T02 > T01 | após T01, **o mesmo ciclo continua** — T01 não encerra a avaliação, e o caminho segue a partir do estado intermediário que T01 produziu. O `E01` consumido por T01 **não** é reutilizado adiante |
| C1 | identidade e estados absorventes | T33, T36, T37 | T33 absorve `E18` concomitante e **preserva o motivo sem resposta automática** (I03) |
| C2 | handoff obrigatório | T07, T24, T26, T30 | — |
| C3 | encerramento | T32, T34, T35 | — |
| C4 | humano assumiu | T31 | `E13` chega isolado, em ciclo próprio (§2.2) |
| C5 | incompatibilidade | T05, T06, T22, T23 | — |
| C6 | pendência impeditiva | T11, T18 | `E09` chega já classificado |
| C7 | disponibilidade | T14, T15, T25 | precede a qualificação — ver P6 (§4.3) |
| C8 | qualificação | T08 → T13 → T40 | respeitando o estado de origem, a condição de cada linha e o **consumo único de `E07`** |
| C9 | resposta comercial | T10, T17, T28 | — |
| C10 | pendência acessória | T12, T19 | — |
| C11 | coleta e visita | T04, T09, T16, T39, T41 | T39 e T41 dependem do mesmo `E01`: pelo consumo único, **no máximo uma das duas** entra no caminho, e nenhuma delas reaproveita um `E01` já consumido em C0 |

Em C8, T08 é avaliada antes de T13: `qualificado_com_ressalva` em `coletando_dados` é
decidido por T08, e T13 recebe apenas o `E07` restante. Como `E07` é consumido uma única
vez por ciclo, T08, T13 e T40 nunca se aplicam duas vezes no mesmo ciclo.

#### Fechamento do ciclo

O fechamento vem **depois** do percurso acima, porque `E15` e `E12` só existem após o
efeito real (§2.2):

1. **`E15` primeiro** — transições T20, T21, T29 e T38, mais a inércia N4 quando aplicável;
2. **`E12` depois** — transição T27.

#### Limite de chamadas

No máximo **três chamadas** da `MaquinaEstados` por ciclo:

| # | Chamada |
|---|---|
| 1 | chamada inicial — percurso das famílias C0–C11, produzindo o **estado intermediário** resultante |
| 2 | até **uma** chamada para `E15` |
| 3 | até **uma** chamada para `E12` |

**Nenhum loop aberto.** Não existe reentrada além dessas três chamadas. O caminho pode
conter várias `Txx` e várias chamadas, mas o ciclo produz e persiste **um único estado
final** (I19).

### 4.3 Efeitos paralelos — lista fechada

Efeito paralelo é o que continua valendo mesmo quando **outra** transição decidiu o
estado. A lista é **fechada** em P1–P6.

| # | Efeito paralelo |
|---|---|
| P1 | registro de dados e correções (`E02`–`E05`) ocorre sempre, qualquer que seja a transição que decidiu o estado |
| P2 | registro do interesse de visita (`E10`) é preservado |
| P3 | a obrigação de responder `E06` **pode sobreviver** a outra transição do estado. `E15` **não** é intenção de responder: só existe depois da resposta real concluída (§2.2) |
| P4 | incompatibilidade já detectada é **preservada** quando outro evento decide o estado |
| P5 | pendência de resposta é registrada em `pendencias_resposta` e levada ao resumo quando outro evento decide o estado |
| P6 | quando `E07` é confirmado com `qualificado_com_ressalva` e **T08 não é a transição que decide o estado**, a ação `INFORMAR_RESSALVA_DE_CAPACIDADE` é preservada **exatamente** nestas famílias: (a) T14/T15 já determinaram o estado pela precedência de disponibilidade (C7); (b) o estado é `respondendo_duvidas` e T40 determina o estado |

**P6 não se generaliza.** Fora das duas famílias listadas, a ressalva não é reemitida como
efeito paralelo.

### 4.4 Inércias — lista fechada

Inércia é o caso em que um evento legítimo **não produz transição e não é erro**. A lista
é **fechada** em N1–N4. **Não existe N5.**

| # | Inércia |
|---|---|
| N1 | `E01` é inerte quando **nenhuma linha da §3** o declara aplicável para o estado e a condição correntes |
| N2 | `E07` é inerte quando uma transição anterior do mesmo ciclo já determinou o estado **e** o comportamento está explicitamente coberto pela ordem da §4.2 ou por P6 |
| N3 | `E14` é inerte quando um `E18` concomitante já determina handoff conforme a condição documentada |
| N4 | `E15` é inerte em `pronto_para_handoff`: a resposta foi concluída legitimamente, mas **não altera o handoff**; em seguida o fechamento pode prosseguir para `E12` |

### 4.5 Evento sem transição

**Não existe fallback genérico.** Um evento que não seja resolvido por

- transição documentada na §3;
- efeito paralelo permitido (§4.3);
- inércia enumerada (§4.4)

permanece **erro de contrato** (`TransicaoInexistente`). A única exceção são os
comportamentos explicitamente normativos já documentados: mensagem repetida (§4, passo 1)
e "sem transição" por contexto inválido ou identidade ambígua (doc 07 §7.1).

## 5. Regras obrigatórias da máquina

1. **A máquina não possui constantes comerciais e não lê o YAML.** Todos os limites e
   condições são avaliados **a montante**, contra `knowledge/casa77.yaml` carregado no
   momento da decisão, e chegam à máquina como eventos confirmados, `Qualificacao` e
   condições já estruturadas. O YAML permanece a fonte comercial prevalente; a máquina
   apenas consome o resultado dessa avaliação.
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
| I06 | Nenhuma informação comercial (preço, capacidade, horário, duração, restrição, quantidade de pacotes) existe como constante da máquina. Toda decisão comercial é avaliada **a montante** contra `knowledge/casa77.yaml`, que permanece a fonte prevalente; a máquina consome o resultado já estruturado e **não lê o YAML** (I23). |
| I07 | `resultado_qualificacao` assume somente os cinco valores oficiais. |
| I08 | O estado da conversa assume somente os oito valores da §1.1. |
| I09 | Ausência de dado nunca produz `incompativel`. |
| I10 | `indefinido` ocorre somente quando a pendência impede a classificação do evento, e referencia o item pendente que a causou. |
| I11 | Pergunta pendente não sobrescreve automaticamente a qualificação: toda pergunta não respondida consta em `pendencias_resposta` e no resumo do handoff. |
| I12 | `encaminhado_humano` só é alcançado após o resumo ser **gerado** (`E12`) e o handoff ser **registrado**; o estado nunca afirma confirmação física de recebimento (§10). |
| I13 | `atendimento_humano` só é alcançado após o humano assumir (`E13`). |
| I14 | Mensagens de um atendimento ativo não criam nem duplicam conversa. |
| I15 | Retorno após `encerrado` é continuação (mesmo evento → reabre preservando dados) ou nova solicitação (novo atendimento, sem herdar dados comerciais do atendimento anterior). |
| I16 | Nenhuma pergunta obrigatória é feita duas vezes quando o dado já foi registrado. |
| I17 | `aguardando_confirmacao_disponibilidade` é inalcançável enquanto `integracoes_planejadas.calendario.status` for `pendente`. |
| I18 | `incompativel` não gera handoff automático universal: handoff ocorre somente por regra documentada específica ou por `E18` (pedido de humano, exceção/contestação ou outro gatilho obrigatório). |
| I19 | Um ciclo **pode percorrer mais de uma `Txx`** e **pode envolver mais de uma chamada da `MaquinaEstados`** (§4.2), produzindo um **caminho auditável**; ainda assim produz e persiste **um único estado final**. Quem determina o resultado é a ordem das famílias C0–C11 (§4.2), **não** a ordem em que as intenções foram extraídas da mensagem. |
| I20 | Incompatibilidade objetiva nunca é sobrescrita por `E07`; todo `E18` carrega um motivo registrado. |
| I21 | `pronto_para_handoff` é **estado intermediário do ciclo**: em caminho normal, o fechamento (§4.2) deve resolvê-lo. Quando recuperado como estado **persistido de um ciclo interrompido**, bloquear o processamento que depende dessa continuidade, preservar a pendência e emitir alerta operacional — sem inventar retomada automática. |
| I22 | `E13` é **evento operacional** e é processado em **ciclo próprio**, isolado do ciclo de uma mensagem do interessado. |
| I23 | A `MaquinaEstados` **não lê o YAML**: toda condição comercial chega **já avaliada e estruturada a montante** (eventos confirmados, `Qualificacao`, condições). |

## 9. Partição dos gatilhos de handoff

Os 12 gatilhos obrigatórios de `docs/04-handoff-humano.md` são materializados por
caminhos **distintos e não concorrentes**:

| Gatilhos do doc 04 | Caminho | Produtor |
|---|---|---|
| 1–2 — pergunta sem resposta aprovada; campo `null`/`pendente` | `E09`, já classificado em impeditivo × acessório | **pendente — S2-D8** (§11) |
| 3–10 — desconto/condição especial, confirmação de data/visita/reserva, contratação, cancelamento, alteração de data, assunto jurídico ou contratual, pedido explícito de humano, reclamação ou tom hostil | `E18` com motivo (§2.1) | `DetectorHandoff` |
| 11–12 — `qualificado_com_ressalva` ou `indefinido`; coleta concluída e lead qualificado | **transições da §3**: T08, T13, T21, T40 e os caminhos de `E09` aplicáveis | `MaquinaEstados` |

Regras:

- **não existe `E18` concorrente para os gatilhos 11 e 12.** Eles são materializados pela
  transição, e não por um segundo caminho de detecção;
- o motivo `informacao_pendente` da §2.1 continua registrável no resumo, mas os gatilhos
  1–2 chegam à máquina como `E09` — o `DetectorHandoff` não os reemite como `E18`;
- o `DetectorHandoff` **não recebe `Qualificacao`**, **não recalcula regra comercial**,
  **não recalcula pendência** e **não recalcula qualificação**. Ele reconhece os gatilhos
  3–10 e emite `E18` com o motivo correspondente.

## 10. Handoff registrado × entrega confirmada

`encaminhado_humano` significa **handoff REGISTRADO** — nunca confirmação física de
recebimento por Douglas Bianchi.

| Momento | O que acontece |
|---|---|
| resumo | gerado antes da persistência quando necessário (`E12`, §2.2) |
| etapa 13 do doc 07 | persistir a decisão final |
| etapa 14 do doc 07 | 1. tentar a entrega do resumo; 2. **somente após sucesso**, emitir a mensagem de encaminhamento ao interessado |

Falha na entrega do resumo:

| # | Regra |
|---|---|
| 1 | **não reverte** o estado já registrado |
| 2 | preserva o processamento pendente de forma **opaca** |
| 3 | gera **alerta operacional**, por caminho separado da conversa |
| 4 | **não inventa** fila, retentativa, contador, status de entrega, canal nem provedor |
| 5 | **não processa novo ciclo** que dependa do handoff como operacionalmente concluído enquanto a pendência não for resolvida |

O `ProcessamentoPendente` atual **não ganha campos** por causa desta regra.

A **confirmação física de entrega permanece futura, da etapa 5** (canal de entrega do
resumo — `docs/04-handoff-humano.md`, "Pendências desta etapa").

## 11. Pendência aberta — S2-D8

**`S2-D8` — contrato de detecção e classificação de pendências.** O prefixo `S2-` é
obrigatório: esta pendência **não** tem relação com a arbitragem comercial `D1`–`D8` já
registrada no histórico do projeto.

Escopo do contrato pendente:

| Item |
|---|
| detectar campo `null`/`pendente` relevante |
| detectar ausência de resposta aprovada |
| classificar a pendência em **impeditiva × acessória** |
| fornecer os identificadores técnicos ao `Qualificador` (`pendencias_impeditivas`) |
| confirmar `E09` |

Regras:

- **nenhum componente concreto é escolhido aqui** — em particular, o produtor **não** é
  atribuído ao `CarregadorYaml` nem ao `ValidadorYaml`;
- **S2-D8 não bloqueia** a implementação da `MaquinaEstados`, que recebe `E09` pronto;
- **S2-D8 bloqueia** o `OrquestradorMotor` e a integração completa do pipeline.

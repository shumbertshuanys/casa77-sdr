# 00 — Estado Atual do Projeto

Documento de estado: registra etapa, subetapa, PRs, commits, testes e próxima ação.
**Não contém dado comercial.** Preço, capacidade, tipo de evento, horário, restrição e
qualquer outra condição vivem exclusivamente em `knowledge/casa77.yaml`.

Atualizado em: 2026-08-17.

## Referências

| Item | Valor |
|---|---|
| Projeto | Casa 77 SDR |
| Branch de referência | `main` |
| Último commit **funcional** aprovado | `02dcb477ea893a6092d62be1a6fa02262fb0a81c` |
| Merge correspondente na `main` | `55f6ed77e32489b2d16e65dde94fbc276ac1af2b` |
| Última subetapa **funcional** concluída | 3B.5 — Qualificador determinístico (PR #14) |
| Subetapa 3B.5 | **CONCLUÍDA** |

## Histórico verificado de entregas

| Entrega | Tipo | Evidência |
|---|---|---|
| Fundação do projeto (etapa 1 — base de conhecimento) | documental | commit `6bf98ef`, direto na `main` |
| Etapa 2 — máquina de estados (`docs/06`) | documental | PR #1 (`3323105`, merge `2ec5d79`) |
| Etapa 3A — arquitetura do motor (`docs/07`) | documental | PR #2 (`03ecd5d`, merge `0a9e584`) |
| Etapa 3B.1 — carregador validado do YAML (`src/casa77_sdr/knowledge.py` + testes) | **funcional** | PR #3 (`00fd1d4`, merge `26ab907`) |
| Auditoria/reconciliação do legado n8n | saneamento/auditoria (read-only) | **Auditoria S0.2 concluída e aprovada em 2026-08-15.** O workflow legado atual foi verificado read-only e classificado como histórico/inativo. Matriz e conclusões sanitizadas em `docs/08-reconciliacao-legado-n8n.md` |
| Saneamento comercial/documental — arbitragem D1–D8 | comercial/documental | PR #4 — **INTEGRADO à `main`** em 2026-08-15 (head `190704e622d1c62767a38027bc19cd191583d472`, merge `954484a279ef19957c2a8bb6c2c159810da493f2`) |
| Etapa 3B.2 — regras comerciais determinísticas (`RegrasComerciais` em `src/casa77_sdr/rules.py` + testes), avaliando dados do interessado contra a base carregada pela 3B.1 | **funcional** | PR #7 (commit funcional `24556ea`, merge `d578113`) |
| Etapa 3B.3 — persistência operacional (`src/casa77_sdr/persistence.py` + testes): contrato abstrato, implementação em memória exclusivamente para testes, idempotência, recuperação de estado, proteção do vínculo de identidade e processamento pendente | **funcional** | PR #9 (commit funcional `6efe191`, merge `9846357`) |
| Etapa 3B.4 — normalização de entrada (`src/casa77_sdr/normalization.py` + testes): contrato comum de entrada, normalização técnica conservadora e produção da chave de idempotência — origem por identificador do canal ou fallback composto, chave opaca e janela temporal parametrizada sem valor padrão | **funcional** | PR #11 (commit funcional `526591f`, merge `78c6555`) |
| Etapa 3B.5 — qualificador determinístico (`src/casa77_sdr/qualification.py` + testes): os cinco resultados oficiais a partir de contrato próprio por composição, com violações recebidas da 3B.2 em vez de recalculadas, capacidade lida dinamicamente da base e precedência determinística — sem pacote, sem handoff e sem transição de estado | **funcional** | PR #14 (commit funcional `02dcb47`, merge `55f6ed7`) |
| Arbitragem S2 — semântica de ciclo da `MaquinaEstados` (`docs/06` e `docs/07`, com reflexo neste documento): reconcilia estados, semântica de confirmação dos eventos, T08, T38–T41, caminho C0–C11, consumo único, P1–P6, N1–N4, sinal `insumo_qualificacao_atualizado`, partição dos gatilhos de handoff e fronteira YAML | documental/governança | PR #16 — **INTEGRADO à `main`** em 2026-08-17 (head `e4746d8b350b65388672ecfb5233a558031ff352`, merge `1a719546b922e0a89d30912de745046eb11849d9`, branch de origem `docs/s2-arbitragem-maquina-estados`). **Não cria marco funcional novo** e não altera o marco 3B.5 |

O PR #4 atualiza base comercial e documentação a partir de decisões de Douglas Bianchi
(2026-08-15). Ele **não** é implementação funcional do motor e não altera o marco
funcional acima.

O PR #16 integra a arbitragem documental S2. Ele também **não** é implementação funcional
do motor: nenhum arquivo de `src/`, `tests/`, `knowledge/` ou `prompts/` foi alterado, e o
marco funcional continua sendo a 3B.5.

## Testes

Última execução real: `python -m pytest -q -p no:cacheprovider` em 2026-08-17, na branch
`docs/s2-reconciliacao-pos-merge` — criada a partir do merge `1a719546…` da `main` e sem
nenhuma alteração de código em relação a ele — `180 passed`. A suíte cobre o
carregador/validação da base (3B.1, `tests/test_knowledge.py`), as regras comerciais
determinísticas (3B.2, `tests/test_rules.py`), a persistência operacional em memória
(3B.3, `tests/test_persistence.py`), a normalização de entrada com a chave de
idempotência (3B.4, `tests/test_normalization.py`) e a qualificação determinística
(3B.5, `tests/test_qualification.py`).

A execução anterior, sobre a `main` pós-merge do PR #14 em 2026-08-16, também registrou
`180 passed`. A arbitragem S2 e esta reconciliação são **documentais**: não alteram
código nem testes, e a suíte funcional permanece verde e inalterada em número de casos.

## Roadmap (resumo — detalhe em `docs/05-roadmap.md`)

Etapas 1 e 2 concluídas; etapa 3 em execução (3A, 3B.1, 3B.2, 3B.3, 3B.4 e 3B.5
entregues; próxima subetapa funcional **não iniciada**). A antiga Etapa 4 —
Qualificação — continua absorvida pela Etapa 3B conforme a arbitragem S1, e o
`Qualificador` foi **implementado na 3B.5**. A `MaquinaEstados` continua **não
implementada**, e a arbitragem documental **S2** — que trata das ambiguidades que impediam
especificá-la — está **integrada à `main`** (PR #16, merge `1a719546…`), sem iniciar a
3B.6. Etapas 5 a 10 permanecem futuras e com a numeração preservada, conforme
`docs/05-roadmap.md`.

## Próxima ação

1. As arbitragens **S2 e S2-R já estão integradas à `main`** (PRs #16 e #17, **MERGED**).
   Nenhuma nova subetapa funcional está iniciada e nenhuma numeração futura além da já
   documentada está aprovada.
2. A arbitragem **S3 foi aprovada pelo GPT**, e a presente entrega apenas **materializa
   essa arbitragem documental** em `docs/06`, `docs/07` e neste arquivo. Ela não implementa
   nada e não cria marco funcional.
3. A **3B.6 continua NÃO iniciada e NÃO autorizada** enquanto esta arbitragem não estiver
   **versionada, integrada à `main` e auditada**.
4. Depois dessa integração e auditoria, a próxima candidata funcional é a implementação da
   **3B.6 — `MaquinaEstados`**, mediante **mandato fechado do GPT para o Claude Code**.
   Como envolve implementação e dependências arquiteturais, o plano deve ser elaborado pelo
   Claude Desktop e auditado pelo GPT antes de qualquer execução.
5. O planejamento deve continuar considerando explicitamente as pendências técnicas em
   aberto registradas abaixo, incluindo **S2-D5, S2-D7, S2-D8, S3-D1 e a confirmação de
   entrega do handoff** — nenhuma delas bloqueia a 3B.6.

## Arbitragens

Decisões de governança. Não criam marco funcional nem código. A coluna Decisão informa o
estado de ciclo de vida de cada arbitragem, incluindo a evidência de integração quando ela
já alcançou a `main`.

| # | Arbitragem | Decisão | Evidência |
|---|---|---|---|
| S3 | Arbitragem residual da `MaquinaEstados` (`docs/06-maquina-de-estados.md` × `docs/07-arquitetura-motor-respostas.md`) | **APROVADA PELO GPT — MATERIALIZADA NESTA BRANCH — NÃO INTEGRADA À MAIN.** Fecha as ambiguidades residuais posteriores à S2 sem redesenhar a máquina: materialização de T04, precedência entre classes de `E08`, `T09 > T04`, `T32 > T35`, contrato semântico de ações, condição estruturada de T35, fronteira temporal da resposta aprovada e `CondicoesCiclo`. **PR #18 ABERTO; não existe merge**; **não implementa código** e **não cria marco funcional.** Escopo abaixo. | **PR #18** (**OPEN**, base `main`), head `541aa765ac0e956620e3a78c19b38c0d24a40885`, na branch `docs/s3-arbitragem-residual-maquina-estados`, a partir do merge `759cbc1db93930e33fd6c1912234aa7b2874e559`; alterações em `docs/06` (notas da §3, §4.2, §11) e `docs/07` (§4.1, §4.4, §4.5, §5) — **na branch, não na `main`** |
| A | Fronteira de Qualificação entre `docs/05-roadmap.md` e `docs/07-arquitetura-motor-respostas.md` | **ARBITRADA** (S1): o `Qualificador` permanece componente do motor e sua implementação pertence à Etapa 3B; a antiga Etapa 4 deixa de ser aberta como etapa autônoma e é absorvida pela 3B; as etapas 5 a 10 mantêm a numeração; o `Qualificador` precede a `MaquinaEstados`. O `Qualificador` foi **implementado na 3B.5** (PR #14); a precedência permanece e a `MaquinaEstados` **ainda não foi iniciada**. | reconciliação documental de `docs/05`, `docs/07` §8.4/§9 e deste documento |
| S2 | Semântica de ciclo da `MaquinaEstados` (`docs/06-maquina-de-estados.md` × `docs/07-arquitetura-motor-respostas.md`) | **APROVADA — INTEGRADA À MAIN.** Arbitragem documental **aprovada pelo GPT** na auditoria da entrega e **integrada à `main`** pelo **PR #16** (**MERGED**), a partir da branch `docs/s2-arbitragem-maquina-estados`. **Não implementa código** e **não cria marco funcional.** Escopo abaixo. | PR #16 — head integrado `e4746d8b350b65388672ecfb5233a558031ff352`, merge `1a719546b922e0a89d30912de745046eb11849d9`; núcleo documental no commit `0be5a022d2b30b5cfa2bca501e77c06bed501419` — `docs/06` (§1.1, §2.2, §3, §4.1–§4.5, §9, §10, §11) e `docs/07` (§4.1, §5, §7.2, §8.1, §9, §12) |

### Arbitragem S3 — escopo aprovado, materializado nesta branch

Arbitragem **residual** da `MaquinaEstados`: fecha as ambiguidades que restavam depois da
S2, **sem redesenhar a máquina**. Preserva os 8 estados, `E01`–`E18`, T01–T41, P1–P6,
N1–N4 e S2.1–S2.9 — **zero estado novo, zero evento novo, zero `Txx` nova, zero P7, zero
N5**. Entrega **exclusivamente documental**: nenhum código, teste, dado comercial ou
dependência foi alterado, e a `MaquinaEstados` **continua não implementada**.

| # | Decisão |
|---|---|
| S3.1 | **Materialização de T04**: a condição "dado compatível com o YAML" é materializada pelo resultado estruturado da `Qualificacao` — T04 só é elegível quando `resultado_qualificacao` ≠ `incompativel`. A máquina continua sem ler YAML; P1 segue garantindo o registro dos dados e correções. |
| S3.2 | **Precedência entre classes de `E08`**: havendo violações de classes diferentes, basta **uma** da classe T05/T22 para aplicar T05/T22; T06/T23 só quando **todas** forem dessa classe. Todas as violações são preservadas, o `E08` é consumido uma única vez e motivo não classificado é **erro de contrato** — sem `E08` múltiplo e sem fallback. |
| S3.3 | **Precedências concretas**: `T32 > T35` (C3, mesmo `E14`) e `T09 > T04` (C11, mesmo `E04`). São **duas precedências concretas**, não um princípio geral: nenhuma colisão futura ganha solução por analogia. T34 permanece separada porque sua origem já está excluída de T35. |
| S3.4 | **Condição estruturada de T35 — `motivo_encerramento`**: vocabulário fechado com as **quatro** modalidades já existentes na linha T35 (`SEM_INTERESSE`, `ENGANO`, `SPAM`, `INCOMPATIBILIDADE_ACEITA`). A máquina **recebe** o motivo, não o interpreta, e não referencia `Rxx`. Despedida é obrigação semântica **apenas** de `SEM_INTERESSE`. A ausência de pedido de exceção/humano segue materializada pela ausência de `E18` (N3). |
| S3.5 | **Contrato semântico de ações**: `AcaoMaquina` com **exatamente 20 códigos** fechados — semânticos, declarativos, sem `Rxx` e sem conteúdo comercial. A máquina **emite** ações e **nunca as executa**; cada `Txx` fica coberta por ação, efeito paralelo, campo dedicado ou mudança de estado. |
| S3.6 | **Pré-requisito declarativo em T27**: `EMITIR_MENSAGEM_DE_ENCAMINHAMENTO` pressupõe `ENTREGAR_RESUMO`, preservando a ordem de S2.9. A máquina apenas declara — não entrega, não verifica sucesso e não cria fila, retentativa, contador ou status. |
| S3.7 | **Fronteira temporal da resposta aprovada**: `resposta_aprovada_disponivel` precisa estar determinada **antes da etapa 7**; as etapas 8–9 consultam e selecionam, mas não produzem condição para uma chamada já ocorrida. O `SeletorFatos` **não** é produtor dessa condição. |
| S3.8 | **`CondicoesCiclo`**: fronteira estrutural com as **oito** condições consumidas pela máquina, sem PII e sem valor comercial, com produtor pendente onde ainda não atribuído. |
| S3.9 | **Ampliação de S2-D8** (sem resolvê-la) e **criação de S3-D1**; **S2-D5 e S2-D7 preservadas** e não reabertas. |

Status da S3: **APROVADA PELO GPT — MATERIALIZADA NESTA BRANCH — NÃO INTEGRADA À MAIN.**
O **PR #18 está ABERTO**; **não existe merge** desta arbitragem. Ela **não cria marco
funcional** e não altera o último commit funcional (`02dcb477…`) nem o último marco
funcional (**3B.5**). A **3B.6 continua NÃO iniciada e NÃO autorizada**.

### Arbitragem S2 — escopo aprovado e integrado à `main`

Entrega **exclusivamente documental**: nenhum código, teste, dado comercial ou
dependência foi alterado. O escopo abaixo foi **aprovado pelo GPT** e **integrado à
`main`** pelo **PR #16** (**MERGED**, merge
`1a719546b922e0a89d30912de745046eb11849d9`, head integrado
`e4746d8b350b65388672ecfb5233a558031ff352`), a partir da branch
`docs/s2-arbitragem-maquina-estados`. O núcleo documental está no commit
`0be5a022d2b30b5cfa2bca501e77c06bed501419`.

| # | Decisão |
|---|---|
| S2.1 | **Estados reconciliados**: `pronto_para_handoff` é estado **intermediário** do ciclo, com resumo ainda em preparação; `encaminhado_humano` significa **handoff registrado**, nunca confirmação física de recebimento; a saída de `respondendo_duvidas` passa a ser a lista completa da §3, sem enumeração menor. |
| S2.2 | **Eventos preservados**: `E01`–`E18` inalterados, **zero evento novo**. Fixada apenas a semântica de confirmação de `E07`, `E09`, `E15`, `E12` e `E13`; `E11`/`E17` continuam reduzidos a `E18`. |
| S2.3 | **T08 corrigida**: passa a ser decidida por `E07` com `resultado_qualificacao = qualificado_com_ressalva`, preservando a semântica anterior (ressalva de capacidade → decisão humana). A máquina **não lê convidados, formato nem YAML**. |
| S2.4 | **T38, T39, T40 e T41 criadas**. T01–T07 e T09–T37 permanecem **inalteradas**. |
| S2.5 | **Sinal técnico `insumo_qualificacao_atualizado`**: é **condição**, não evento; vale verdadeiro somente com **mutação efetiva** de insumo de `DadosQualificacao` (nome, contato, tipo, data, convidados, formato) comparada ao contexto recuperado; repetição de valor conhecido não conta; é apenas booleano, sem valor, PII ou conteúdo; **não** equivale a `E02`–`E05`. T04 e T09 não foram ampliadas. |
| S2.6 | **Ordem do ciclo C0–C11 + fechamento**: `E15` antes de `E12`, ambos pós-efeito; **no máximo três chamadas** da `MaquinaEstados` por ciclo; nenhum loop aberto. Efeitos paralelos fechados em **P1–P6** e inércias fechadas em **N1–N4** (sem N5); evento não coberto permanece **erro de contrato**, sem fallback genérico. |
| S2.7 | **Partição dos gatilhos de handoff**: gatilhos 1–2 → `E09`; gatilhos 3–10 → `DetectorHandoff` → `E18`; gatilhos 11–12 → materializados pelas transições (T08, T13, T21, T40 e caminhos de `E09`), **sem `E18` concorrente**. O `DetectorHandoff` não recebe `Qualificacao` e não recalcula regra, pendência ou qualificação. |
| S2.8 | **Fronteira do YAML**: a `MaquinaEstados` não lê o YAML e não fabrica eventos — recebe estado, eventos confirmados, `Qualificacao` e condições já estruturadas, e devolve caminho, estado final único, ações e efeitos auditáveis. |
| S2.9 | **Handoff registrado × entrega**: resumo gerado antes da persistência quando necessário; etapa 13 persiste a decisão final; etapa 14 tenta a entrega do resumo e só depois emite a mensagem de encaminhamento. Falha de entrega não reverte o estado, preserva processamento pendente de forma opaca e gera alerta operacional — sem fila, retentativa, contador ou status inventados. O `ProcessamentoPendente` **não ganha campos**. |

Consequências de estado da S2:

- a S2 **não cria marco funcional**: o último commit funcional aprovado e o último marco
  funcional (3B.5) permanecem exatamente os registrados em "Referências";
- a `MaquinaEstados` continua **NÃO implementada**;
- a **3B.6 — `MaquinaEstados`** continua **NÃO iniciada** e **NÃO autorizada**, e nenhuma
  numeração futura está aprovada;
- **status atual: APROVADA — INTEGRADA À MAIN.** A S2 foi **aprovada pelo GPT** e
  integrada à `main` pelo **PR #16** (**MERGED**), com merge
  `1a719546b922e0a89d30912de745046eb11849d9` e head integrado
  `e4746d8b350b65388672ecfb5233a558031ff352`, a partir da branch
  `docs/s2-arbitragem-maquina-estados`. O núcleo documental permanece no commit
  `0be5a022d2b30b5cfa2bca501e77c06bed501419`. **Integrar a arbitragem não autoriza
  implementação**: a 3B.6 segue NÃO iniciada e NÃO autorizada.

## Pendências técnicas em aberto

Registradas aqui como estado, não resolvidas nesta entrega.

| # | Pendência | Antes de quê precisa ser arbitrada |
|---|---|---|
| B | Colisão conceitual de nome: `RegistroAtendimento` já existe em `src/casa77_sdr/persistence.py` como dataclass de transporte, enquanto `docs/07` usa o mesmo nome para uma responsabilidade futura | implementar o componente `RegistroAtendimento` descrito em `docs/07` |
| C | Não existe contrato estruturado, legível por máquina, relacionando as respostas aprovadas (`Rxx`) aos campos do YAML | implementar `ValidadorConsistenciaBase` e, em cascata, `SeletorFatos` e `ValidadorResposta` |

As pendências **B e C permanecem inalteradas** pela arbitragem S2.

### Pendências da arbitragem S2 — não bloqueadoras da 3B.6

Prefixo `S2-` obrigatório: estas pendências **não** têm relação com a arbitragem
comercial `D1`–`D8` já registrada no histórico deste documento.

| # | Pendência | Situação |
|---|---|---|
| S2-D5 | Mensagem conversacional recebida enquanto o estado é `aguardando_confirmacao_disponibilidade`, **antes** de `E16`. Hoje o caso é inalcançável enquanto a integração de calendário está pendente (I17 de `docs/06`). Resolver na **Etapa 6**. | **não bloqueia** a 3B.6 |
| S2-D7 | `E13` a partir de estado **diferente** de `encaminhado_humano`. Hoje não existe produtor nem interface operacional para esse caminho. Resolver na **Etapa 5**. | **não bloqueia** a 3B.6 |
| S2-D8 | Contrato de detecção e classificação de pendências: detectar campo `null`/`pendente` relevante e ausência de resposta aprovada, classificar impeditiva × acessória, fornecer os identificadores técnicos ao `Qualificador` e confirmar `E09`. **Ampliada pela S3**: o mesmo produtor também fornece a condição estruturada **`resposta_aprovada_disponivel`** (T10, T17, T28), determinada **antes da etapa 7** — saída **distinta** de `E09` e **não** sua negação; só o status APROVADO habilita. **Nenhum componente concreto foi escolhido** — não é o `CarregadorYaml`, não é o `ValidadorYaml` e não é o `SeletorFatos`. **Continua ABERTA.** Detalhe em `docs/06` §11. | **não bloqueia** a `MaquinaEstados`/3B.6; **bloqueia** o `OrquestradorMotor` e a integração completa |
| S3-D1 | Produtor da condição **`motivo_encerramento`**: determinar, a montante da etapa 7, uma das **quatro** modalidades já existentes de T35 — sem interesse, engano, spam, incompatibilidade aceita. Produtor **NÃO atribuído**: **não** é a `MaquinaEstados`, **não** é o `DetectorHandoff`, **não** é o `Qualificador`, **não** é o `CarregadorYaml` e **não** é o LLM decidindo sozinho. | **não bloqueia** a 3B.6; **bloqueia** o `OrquestradorMotor` e a integração completa |
| Confirmação de entrega do handoff | `encaminhado_humano` afirma handoff **registrado**, nunca recebimento confirmado. A confirmação física permanece futura da **etapa 5** (canal de entrega do resumo). | **não bloqueia** a 3B.6 |

## Pendências que não bloqueiam

- Itens pendentes da base: ver `knowledge/informacoes-pendentes.md` (fonte única das
  lacunas; não replicar aqui).

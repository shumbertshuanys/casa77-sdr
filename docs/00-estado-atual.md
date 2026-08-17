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

O PR #4 atualiza base comercial e documentação a partir de decisões de Douglas Bianchi
(2026-08-15). Ele **não** é implementação funcional do motor e não altera o marco
funcional acima.

## Testes

Última execução real: `python -m pytest -q -p no:cacheprovider` sobre a `main`
pós-merge do PR #14 em 2026-08-16 — `180 passed`. A suíte cobre o carregador/validação
da base (3B.1, `tests/test_knowledge.py`), as regras comerciais determinísticas
(3B.2, `tests/test_rules.py`), a persistência operacional em memória
(3B.3, `tests/test_persistence.py`), a normalização de entrada com a chave de
idempotência (3B.4, `tests/test_normalization.py`) e a qualificação determinística
(3B.5, `tests/test_qualification.py`).

## Roadmap (resumo — detalhe em `docs/05-roadmap.md`)

Etapas 1 e 2 concluídas; etapa 3 em execução (3A, 3B.1, 3B.2, 3B.3, 3B.4 e 3B.5
entregues; próxima subetapa funcional **não iniciada**). A antiga Etapa 4 —
Qualificação — continua absorvida pela Etapa 3B conforme a arbitragem S1, e o
`Qualificador` foi **implementado na 3B.5**. A `MaquinaEstados` continua **não
implementada**, e a arbitragem documental **S2** — que trata das ambiguidades que impedem
especificá-la — foi **aprovada pelo GPT e versionada na branch**, mas **não integrada à
`main`**, sem iniciar a 3B.6. Etapas 5 a 10 permanecem futuras e com a numeração
preservada, conforme `docs/05-roadmap.md`.

## Próxima ação

1. Nenhuma nova subetapa funcional está iniciada e nenhuma numeração futura está
   aprovada.
2. A próxima entrega deve ser definida formalmente a partir do grafo de dependências da
   arquitetura (`docs/07`) no estado posterior à 3B.5.
3. Como isso envolve arquitetura e dependências entre componentes, o próximo passo deve
   ser planejado pelo Claude Desktop e auditado pelo GPT antes de qualquer execução pelo
   Claude Code.
4. A `MaquinaEstados` está arquiteturalmente desbloqueada pela conclusão do
   `Qualificador`. A arbitragem **S2 foi aprovada pelo GPT e versionada na branch**
   `docs/s2-arbitragem-maquina-estados`, mas **não existe PR nem merge** e ela **não está
   integrada à `main`**. Versionar na branch **não** autoriza implementação: a **3B.6 não
   foi iniciada e não está autorizada**.
5. O planejamento deve continuar considerando explicitamente as pendências técnicas em
   aberto registradas abaixo, incluindo **S2-D5, S2-D7, S2-D8 e a confirmação de entrega
   do handoff** — nenhuma delas bloqueia a 3B.6.

## Arbitragens

Decisões de governança. Não criam marco funcional nem código. A coluna Decisão informa o
estado de ciclo de vida de cada arbitragem — inclusive quando ela já foi **aprovada e
versionada na branch**, mas ainda **não integrada à `main`**.

| # | Arbitragem | Decisão | Evidência |
|---|---|---|---|
| A | Fronteira de Qualificação entre `docs/05-roadmap.md` e `docs/07-arquitetura-motor-respostas.md` | **ARBITRADA** (S1): o `Qualificador` permanece componente do motor e sua implementação pertence à Etapa 3B; a antiga Etapa 4 deixa de ser aberta como etapa autônoma e é absorvida pela 3B; as etapas 5 a 10 mantêm a numeração; o `Qualificador` precede a `MaquinaEstados`. O `Qualificador` foi **implementado na 3B.5** (PR #14); a precedência permanece e a `MaquinaEstados` **ainda não foi iniciada**. | reconciliação documental de `docs/05`, `docs/07` §8.4/§9 e deste documento |
| S2 | Semântica de ciclo da `MaquinaEstados` (`docs/06-maquina-de-estados.md` × `docs/07-arquitetura-motor-respostas.md`) | **APROVADA — VERSIONADA NA BRANCH, NÃO INTEGRADA À MAIN.** Arbitragem documental **aprovada pelo GPT** na auditoria da entrega e versionada na branch `docs/s2-arbitragem-maquina-estados`. **Não existe PR e não existe merge**; a `main` permanece sem esta arbitragem. **Não implementa código** e **não cria marco funcional.** Escopo abaixo. | núcleo documental no commit `0be5a022d2b30b5cfa2bca501e77c06bed501419` — `docs/06` (§1.1, §2.2, §3, §4.1–§4.5, §9, §10, §11) e `docs/07` (§4.1, §5, §7.2, §8.1, §9, §12) — **na branch, não na `main`** |

### Arbitragem S2 — escopo aprovado, versionado na branch

Entrega **exclusivamente documental**: nenhum código, teste, dado comercial ou
dependência foi alterado. O escopo abaixo foi **aprovado pelo GPT** e **versionado na
branch** `docs/s2-arbitragem-maquina-estados` (núcleo documental no commit
`0be5a022d2b30b5cfa2bca501e77c06bed501419`). Enquanto não houver PR e merge, ele existe
**apenas na branch** e **não** está integrado à `main`.

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
- **status atual: APROVADA — VERSIONADA NA BRANCH, NÃO INTEGRADA À MAIN.** A S2 foi
  **aprovada pelo GPT** e o núcleo documental está versionado no commit
  `0be5a022d2b30b5cfa2bca501e77c06bed501419`, na branch
  `docs/s2-arbitragem-maquina-estados`. **Não existe PR e não existe merge**: a `main`
  continua sem esta arbitragem. **Versionar na branch não é integrar à `main`.**

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
| S2-D8 | Contrato de detecção e classificação de pendências: detectar campo `null`/`pendente` relevante e ausência de resposta aprovada, classificar impeditiva × acessória, fornecer os identificadores técnicos ao `Qualificador` e confirmar `E09`. **Nenhum componente concreto foi escolhido** — não é o `CarregadorYaml` nem o `ValidadorYaml`. Detalhe em `docs/06` §11. | **não bloqueia** a `MaquinaEstados`/3B.6; **bloqueia** o `OrquestradorMotor` e a integração completa |
| Confirmação de entrega do handoff | `encaminhado_humano` afirma handoff **registrado**, nunca recebimento confirmado. A confirmação física permanece futura da **etapa 5** (canal de entrega do resumo). | **não bloqueia** a 3B.6 |

## Pendências que não bloqueiam

- Itens pendentes da base: ver `knowledge/informacoes-pendentes.md` (fonte única das
  lacunas; não replicar aqui).

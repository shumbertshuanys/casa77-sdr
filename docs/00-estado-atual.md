# 00 — Estado Atual do Projeto

Documento de estado: registra etapa, subetapa, PRs, commits, testes e próxima ação.
**Não contém dado comercial.** Preço, capacidade, tipo de evento, horário, restrição e
qualquer outra condição vivem exclusivamente em `knowledge/casa77.yaml`.

Atualizado em: 2026-08-19.

## Referências

| Item | Valor |
|---|---|
| Projeto | Casa 77 SDR |
| Branch de referência | `main` |
| Último commit **funcional** aprovado | `d51087732a77930e52c4a691d52910f6da921b1e` |
| Merge correspondente na `main` | `e3dbe55502774e0e74b7d05a3034bb2468eb986a` |
| Última subetapa **funcional** concluída | 3B.6 — MaquinaEstados determinística (PR #21) |
| Subetapa 3B.6 | **CONCLUÍDA** |
| Subetapa 3B.5 | **CONCLUÍDA** (marco funcional anterior — commit `02dcb477…`, merge `55f6ed77…`, PR #14) |

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
| Arbitragem S3 — residual da `MaquinaEstados` (`docs/06`, `docs/07` e este documento): materialização de T04, precedência entre classes de `E08`, `T09 > T04`, `T32 > T35`, `motivo_encerramento`, contrato semântico de ações, pré-requisito de T27, fronteira temporal da resposta aprovada e `CondicoesCiclo` | documental/governança | PR #18 — **INTEGRADO à `main`** em 2026-08-17 (head integrado `40841a3ef6ef00b83313d41e95c52c4f6c1045a8`, merge `ac49758771efe00596e27a9d8eec034d4c85df04`, branch de origem `docs/s3-arbitragem-residual-maquina-estados`). **Não cria marco funcional novo** e não altera o marco 3B.5 |
| Etapa 3B.6 — `MaquinaEstados` determinística (`src/casa77_sdr/state_machine.py` + testes): máquina pura e determinística sobre os estados, eventos e transições oficiais; percurso C0–C11 com consumo único; efeitos paralelos P1–P6; inércias N1–N4; ações semânticas fechadas; contrato explícito de erros — sem leitura de YAML, sem I/O e sem serviço externo | **funcional** | PR #21 (commit funcional `d510877`, merge `e3dbe55`) |
| Arbitragem R — contrato de resolução de identidade do `ResolvedorIdentidade` (`docs/06` e `docs/07`), **anterior** à `MaquinaEstados`: conjunto elegível fechado de candidatos; `IntencaoIdentidade`; `Vinculo` total incluindo `DECLARACAO_CONTRADITORIA`; cascata determinística D0–D6; 12 `CriterioIdentidade`; `SEM_CANDIDATO_ELEGIVEL` distinto de primeiro contato; identificador que **restringe** o escopo sem provar continuidade; `SituacaoTakeover` separada de `Identidade`, com precedência **antes** de D0–D6 | documental/governança | PR #23 — **INTEGRADO à `main`** em 2026-08-18 (commit documental `6c848ea8d45e7f6e412cdd297e9ca68c1fa75a21`, merge `aeb446656fd11b91bb61164f29f9adca6959d4df`, branch de origem `docs/arbitragem-resolvedor-identidade`). **Não cria marco funcional novo** e não altera o marco 3B.6 |
| Arbitragem R-H — fronteira do **conjunto H** / **takeover humano** na resolução de identidade (`docs/07`): `ids_em_atendimento_humano` como entrada **própria e separada** do conjunto elegível, **fora** da política N-a; regras H1–H6; cardinalidade de H determinando `SituacaoTakeover`; erros de contrato por ID duplicado e por incoerência entre projeções; alvo de `HUMANO_UNICO` obtido **direto de H**; R5-P0 preservado antes do identificador e de D0–D6; H fora de `CondicoesCiclo` e da `MaquinaEstados` | documental/governança | PR #25 — **INTEGRADO à `main`** em 2026-08-19 (commit documental `24835a8d6cca50a6f783c8b831ca2c924d2177a9`, merge `96a8ff98611fb9de75540ea98adad94166c65e8b`, branch de origem `docs/rh-fronteira-conjunto-h`). **Não cria marco funcional novo** e não altera o marco 3B.6 |
| Arbitragem R-I — **projeção do identificador validado** da etapa 3 para a etapa 5 (`docs/07`): `id_atendimento_validado` como **insumo próprio e opaco** do `ResolvedorIdentidade`; pré-condições estruturais **P-I1–P-I5** verificadas **antes de R5-P0**; obrigações do produtor **N-I-1–N-I-4** na etapa 3; fronteira parcial **N-a-F1**; `VeredictoIdentificador` preservado com **quatro** valores; D2 continua **restringindo, não decidindo**; D0–D6 semanticamente inalterados | documental/governança | PR #27 — **INTEGRADO à `main`** em 2026-08-19 (commit documental `713f473c9b9fcae75f73aa0ffadc84dd31e81caa`, merge `4bb202e0bb68f67a8d66e487d85ec7978ea8cd95`, branch de origem `docs/ri-identificador-validado`). **Não cria marco funcional novo** e não altera o marco 3B.6 |

O PR #4 atualiza base comercial e documentação a partir de decisões de Douglas Bianchi
(2026-08-15). Ele **não** é implementação funcional do motor e não altera o marco
funcional acima.

Os PRs #16 e #18 integram as arbitragens documentais S2 e S3. Nenhum dos dois é
implementação funcional do motor: nenhum arquivo de `src/`, `tests/`, `knowledge/` ou
`prompts/` foi alterado, e nenhum deles alterou o marco funcional — que **naquele
momento** era a 3B.5. O marco funcional passou a ser a 3B.6 somente com o PR #21.

O **PR #23** integra a arbitragem documental **R** do `ResolvedorIdentidade`. Vale a mesma
regra: alterou **exclusivamente** `docs/06-maquina-de-estados.md` e
`docs/07-arquitetura-motor-respostas.md` — nenhum arquivo de `src/`, `tests/`, `knowledge/`
ou `prompts/` — e **não altera o marco funcional**, que permanece a **3B.6**. Ele especifica
um componente que **ainda não existe em código**: o `ResolvedorIdentidade` **não está
implementado**.

O **PR #25** integra a **micro-arbitragem documental R-H** — fronteira entre contexto
recuperado, conjunto elegível e takeover humano. Vale a mesma regra: alterou
**exclusivamente** `docs/07-arquitetura-motor-respostas.md` — nenhum arquivo de `src/`,
`tests/`, `knowledge/` ou `prompts/` — e **não altera o marco funcional**, que permanece a
**3B.6**. Ele detalha a entrada `ids_em_atendimento_humano` do mesmo componente **ainda não
implementado**: o `ResolvedorIdentidade` continua **sem código**.

O **PR #27** integra a **micro-arbitragem documental R-I** — projeção do identificador de
atendimento **validado** da etapa 3 para a etapa 5. Vale a mesma regra: alterou
**exclusivamente** `docs/07-arquitetura-motor-respostas.md` (`+117 / -9`) — nenhum arquivo
de `src/`, `tests/`, `knowledge/` ou `prompts/` — e **não altera o marco funcional**, que
permanece a **3B.6**. Ele acrescenta um **insumo** ao contrato do mesmo componente **ainda
não implementado**: o `ResolvedorIdentidade` continua **sem código**.

## Testes

Última execução real: `python -m pytest -q -p no:cacheprovider` em 2026-08-17, sobre a
`main` pós-merge do PR #21 (`e3dbe55502774e0e74b7d05a3034bb2468eb986a`) — **`427 passed`**.
A suíte cobre o carregador/validação da base (3B.1, `tests/test_knowledge.py`), as regras
comerciais determinísticas (3B.2, `tests/test_rules.py`), a persistência operacional em
memória (3B.3, `tests/test_persistence.py`), a normalização de entrada com a chave de
idempotência (3B.4, `tests/test_normalization.py`), a qualificação determinística
(3B.5, `tests/test_qualification.py`) e a máquina de estados determinística
(3B.6, `tests/test_state_machine.py`).

**Baseline funcional atual: `427 passed`.**

Histórico: até a 3B.5 o baseline era `180 passed`, e assim permaneceu durante as
arbitragens documentais S2 e S3 — elas não alteram código nem testes. O salto para
`427 passed` decorre exclusivamente da 3B.6, que acrescentou
`tests/test_state_machine.py`.

O **PR #23** (arbitragem R), o **PR #25** (arbitragem R-H), o **PR #27** (arbitragem R-I)
e a presente reconciliação **não alteram código nem testes** e, portanto, **não alteram o baseline**. Nenhuma nova
execução de `pytest` é alegada por esta entrega: o valor `427 passed` continua sendo o da
execução real de 2026-08-17 registrada acima.

## Roadmap (resumo — detalhe em `docs/05-roadmap.md`)

Etapas 1 e 2 concluídas; etapa 3 em execução (3A, 3B.1, 3B.2, 3B.3, 3B.4, 3B.5 e 3B.6
entregues). A antiga Etapa 4 — Qualificação — continua absorvida pela Etapa 3B conforme a
arbitragem S1, e o `Qualificador` foi **implementado na 3B.5**. A `MaquinaEstados` foi
**implementada na 3B.6** e integrada à `main` pelo **PR #21**; as arbitragens documentais
**S2** e **S3** — que trataram das ambiguidades que impediam especificá-la — já estavam
integradas (PR #16, merge `1a719546…`; PR #18, merge `ac49758…`).

A arbitragem documental **R** — contrato de resolução de identidade — foi integrada pelo
**PR #23** (merge `aeb44665…`), e a micro-arbitragem **R-H** — fronteira do conjunto H e do
takeover humano — pelo **PR #25** (merge `96a8ff98…`); e a micro-arbitragem **R-I** —
projeção do identificador **validado** para a etapa 5 — pelo **PR #27** (merge
`4bb202e0…`). **As três especificam** o `ResolvedorIdentidade`, componente **anterior** à
`MaquinaEstados` no pipeline, mas **não o implementam**: não existe
`src/casa77_sdr/identity.py`. O `OrquestradorMotor` também **permanece não implementado**.

A **próxima entrega funcional** já está **tecnicamente selecionada**, após análise do
Claude Desktop e auditoria do GPT: a implementação **isolada** do `ResolvedorIdentidade`,
cuja numeração **proposta e aprovada condicionalmente** é a **3B.7**.

Isso é **planejamento, não execução**. A **3B.7 ainda NÃO está iniciada**: **nenhum código
dela existe** e **nenhuma execução foi autorizada**. **Estado do gate:** antes, a 3B.7
aguardava a integração e a auditoria da micro-arbitragem **R-I**; a R-I está agora
**integrada à `main` pelo PR #27**, e a **presente reconciliação de `docs/00` é o último
gate documental** antes da autorização funcional. Depois que esta reconciliação estiver
versionada, mergeada e auditada, o GPT poderá emitir o **mandato funcional da 3B.7**. Etapas 5 a 10 permanecem
futuras e com a numeração preservada, conforme `docs/05-roadmap.md`.

### 3B.7 — escopo futuro selecionado (registro de planejamento, **não** implementação)

Registrado aqui apenas como **entrega futura selecionada condicionalmente**. **Nada abaixo
existe em código.**

| Item | Registro |
|---|---|
| Componente | `ResolvedorIdentidade` **isolado e determinístico** |
| Arquivos previstos | `src/casa77_sdr/identity.py`, `tests/test_identity.py`, `src/casa77_sdr/__init__.py` — **nenhum criado ou alterado** nesta entrega |
| Fronteiras já aprovadas | puro; determinístico; **zero I/O, rede, LLM, YAML e relógio**; **não** calcula elegibilidade nem recência; recebe o **conjunto elegível pronto**; recebe a **projeção estruturada**; recebe `veredito_identificador`; recebe `id_atendimento_validado`; recebe `havia_estado_esperado`; recebe `ids_em_atendimento_humano`; aplica as **pré-condições estruturais** (C2, H4, H5, **P-I1–P-I5**); aplica **R5-P0 + D0–D6**; **não** integra o `OrquestradorMotor` |
| Situação | **NÃO INICIADA** — aguarda mandato funcional próprio do GPT |

## Próxima ação

1. A **3B.6 — `MaquinaEstados` determinística** está **funcionalmente concluída e
   integrada à `main`** pelo **PR #21** (**MERGED**).
2. Commit funcional: `d51087732a77930e52c4a691d52910f6da921b1e`. Merge correspondente:
   `e3dbe55502774e0e74b7d05a3034bb2468eb986a`.
3. Baseline funcional atual: **`427 passed`**, verificado sobre a `main` já integrada.
4. A arbitragem documental **R** — contrato de resolução de identidade — está
   **integrada à `main`** pelo **PR #23** (**MERGED**): commit documental
   `6c848ea8d45e7f6e412cdd297e9ca68c1fa75a21`, merge
   `aeb446656fd11b91bb61164f29f9adca6959d4df`. Ela alterou somente `docs/06` e `docs/07`.
5. A micro-arbitragem documental **R-H** — fronteira do **conjunto H** e do **takeover
   humano** — está **integrada à `main`** pelo **PR #25** (**MERGED**): commit documental
   `24835a8d6cca50a6f783c8b831ca2c924d2177a9`, merge
   `96a8ff98611fb9de75540ea98adad94166c65e8b`. Ela alterou **somente** `docs/07`.
6. A micro-arbitragem documental **R-I** — **projeção do identificador validado** da
   etapa 3 para a etapa 5 — está **integrada à `main`** pelo **PR #27** (**MERGED**):
   commit documental `713f473c9b9fcae75f73aa0ffadc84dd31e81caa`, merge
   `4bb202e0bb68f67a8d66e487d85ec7978ea8cd95`. Ela alterou **somente** `docs/07`
   (`+117 / -9`).
7. A presente entrega é **exclusivamente reconciliação documental de
   `docs/00-estado-atual.md`** após aquele merge: não altera código, testes, base de
   conhecimento nem prompts, e **não cria marco funcional novo**. O último marco funcional
   continua sendo a **3B.6**.
8. **Nenhuma implementação funcional ocorre aqui.** O `ResolvedorIdentidade` **não** está
   implementado e o `OrquestradorMotor` **não** está implementado.
9. A **3B.7 permanece NÃO INICIADA**. Ela já é a **próxima entrega funcional selecionada
   condicionalmente** — implementação isolada do `ResolvedorIdentidade` —, mas **nenhum
   código dela existe** e **nenhuma execução foi autorizada**.
10. **Próximo gate previsto:** a R-I já está integrada; esta reconciliação de `docs/00` é o
    **último gate documental**. Depois que ela estiver **versionada, mergeada e auditada**,
    o GPT emite a **autorização funcional da 3B.7**. Nenhuma execução funcional antes disso.
11. As pendências permanecem abertas conforme seus próprios bloqueios: **B, C, S2-D5,
    S2-D7, S2-D8, S3-D1, a confirmação de entrega do handoff, N-a — exceto a fronteira
    parcial N-a-F1 —, N-b, E1, E3, E4, o retorno do controle ao bot após
    `atendimento_humano` sem `E14`/T34** e a **unicidade geral de `id_atendimento` entre
    candidatos não identificados**. Nenhuma delas está resolvida — **nem por esta entrega,
    nem pela R-H, nem pela R-I**.

## Arbitragens

Decisões de governança. Não criam marco funcional nem código. A coluna Decisão informa o
estado de ciclo de vida de cada arbitragem, incluindo a evidência de integração quando ela
já alcançou a `main`.

| # | Arbitragem | Decisão | Evidência |
|---|---|---|---|
| R-I | **Projeção do identificador validado** para a etapa 5 (`docs/07-arquitetura-motor-respostas.md`) | **APROVADA — INTEGRADA À MAIN.** Micro-arbitragem que fixa `id_atendimento_validado` como **insumo próprio e opaco** do `ResolvedorIdentidade`, com pré-condições estruturais **P-I1–P-I5**, obrigações do produtor **N-I-1–N-I-4** e a fronteira parcial **N-a-F1** — **sem criar estado, evento, transição, critério ou campo de saída**. Arbitragem documental **aprovada pelo GPT** e **integrada à `main`** pelo **PR #27** (**MERGED**). **Não implementa código** e **não cria marco funcional.** Escopo abaixo. | PR #27 — commit documental `713f473c9b9fcae75f73aa0ffadc84dd31e81caa`, merge `4bb202e0bb68f67a8d66e487d85ec7978ea8cd95`, branch de origem `docs/ri-identificador-validado`; alterações **exclusivamente** em `docs/07` (`+117 / -9`: §4.1 linha do componente, §5 etapa 5, §6.1.1 N7 + N-I-1–N-I-4, §6.2 projeção + N-a-F1, §7.1 insumos, assinatura, P-I1–P-I5, efeito sobre a cascata, saída auditável e classes de erro, §8.2 R-I-K1–R-I-K15, §12) |
| R-H | **Fronteira do conjunto H / takeover humano** na resolução de identidade (`docs/07-arquitetura-motor-respostas.md`) | **APROVADA — INTEGRADA À MAIN.** Micro-arbitragem que fixa `ids_em_atendimento_humano` como **entrada própria e separada** do conjunto elegível, **fora** da política N-a, **sem criar estado, evento ou transição**. Arbitragem documental **aprovada pelo GPT** e **integrada à `main`** pelo **PR #25** (**MERGED**). **Não implementa código** e **não cria marco funcional.** Escopo abaixo. | PR #25 — commit documental `24835a8d6cca50a6f783c8b831ca2c924d2177a9`, merge `96a8ff98611fb9de75540ea98adad94166c65e8b`, branch de origem `docs/rh-fronteira-conjunto-h`; alterações **exclusivamente** em `docs/07` (§5 tabela de componentes, §5 etapas 3 e 5, §6.2 + regras H1–H6, §6.3, §7.1 insumos e assinatura conceitual, R5-P0, §7.1 classes de erro, §8.1, §8.2 cenários K-H1–K-H8) |
| R | Contrato de **resolução de identidade** do `ResolvedorIdentidade`, anterior à `MaquinaEstados` (`docs/06-maquina-de-estados.md` × `docs/07-arquitetura-motor-respostas.md`) | **APROVADA — INTEGRADA À MAIN.** Materializa o critério técnico de "mesmo evento × nova solicitação" (T36/T37), que até então era declarado futuro, **sem criar estado, evento ou transição**. Arbitragem documental **aprovada pelo GPT** e **integrada à `main`** pelo **PR #23** (**MERGED**). **Não implementa código** e **não cria marco funcional.** Escopo abaixo. | PR #23 — commit documental `6c848ea8d45e7f6e412cdd297e9ca68c1fa75a21`, merge `aeb446656fd11b91bb61164f29f9adca6959d4df`, branch de origem `docs/arbitragem-resolvedor-identidade`; alterações em `docs/06` (nota da §3, §4.5, §5 regra 12) e `docs/07` (§4.1, §5, §6.1.1, §6.2, §6.3, §6.4, §6.5, §7.1, §8.1, §8.2, §9, §12) |
| S3 | Arbitragem residual da `MaquinaEstados` (`docs/06-maquina-de-estados.md` × `docs/07-arquitetura-motor-respostas.md`) | **APROVADA — INTEGRADA À MAIN.** Fecha as ambiguidades residuais posteriores à S2 sem redesenhar a máquina: materialização de T04, precedência entre classes de `E08`, `T09 > T04`, `T32 > T35`, contrato semântico de ações, condição estruturada de T35, fronteira temporal da resposta aprovada e `CondicoesCiclo`. Arbitragem documental **aprovada pelo GPT** e **integrada à `main`** pelo **PR #18** (**MERGED**). **Não implementa código** e **não cria marco funcional.** Escopo abaixo. | PR #18 — head integrado `40841a3ef6ef00b83313d41e95c52c4f6c1045a8`, merge `ac49758771efe00596e27a9d8eec034d4c85df04`; commit documental principal `541aa765ac0e956620e3a78c19b38c0d24a40885`, a partir da branch `docs/s3-arbitragem-residual-maquina-estados`; alterações em `docs/06` (notas da §3, §4.2, §11) e `docs/07` (§4.1, §4.4, §4.5, §5) |
| A | Fronteira de Qualificação entre `docs/05-roadmap.md` e `docs/07-arquitetura-motor-respostas.md` | **ARBITRADA** (S1): o `Qualificador` permanece componente do motor e sua implementação pertence à Etapa 3B; a antiga Etapa 4 deixa de ser aberta como etapa autônoma e é absorvida pela 3B; as etapas 5 a 10 mantêm a numeração; o `Qualificador` precede a `MaquinaEstados`. O `Qualificador` foi **implementado na 3B.5** (PR #14) e a `MaquinaEstados` foi **implementada na 3B.6** (PR #21); a precedência entre os dois foi respeitada na ordem de entrega. | reconciliação documental de `docs/05`, `docs/07` §8.4/§9 e deste documento |
| S2 | Semântica de ciclo da `MaquinaEstados` (`docs/06-maquina-de-estados.md` × `docs/07-arquitetura-motor-respostas.md`) | **APROVADA — INTEGRADA À MAIN.** Arbitragem documental **aprovada pelo GPT** na auditoria da entrega e **integrada à `main`** pelo **PR #16** (**MERGED**), a partir da branch `docs/s2-arbitragem-maquina-estados`. **Não implementa código** e **não cria marco funcional.** Escopo abaixo. | PR #16 — head integrado `e4746d8b350b65388672ecfb5233a558031ff352`, merge `1a719546b922e0a89d30912de745046eb11849d9`; núcleo documental no commit `0be5a022d2b30b5cfa2bca501e77c06bed501419` — `docs/06` (§1.1, §2.2, §3, §4.1–§4.5, §9, §10, §11) e `docs/07` (§4.1, §5, §7.2, §8.1, §9, §12) |

### Arbitragem R — escopo aprovado e integrado à `main`

Contrato do `ResolvedorIdentidade` — componente **puro e determinístico** (zero I/O, rede,
LLM, YAML e relógio) que resolve **qual atendimento** a mensagem trata, **antes** de qualquer
chamada da `MaquinaEstados`:

| # | Decisão |
|---|---|
| R-1 | **Conjunto elegível fechado.** O resolvedor recebe os candidatos prontos da etapa 3; não calcula elegibilidade nem recência. Passar o histórico inteiro é **violação de contrato**. |
| R-2 | **`IntencaoIdentidade`** — exatamente três valores: `CONTINUIDADE_DECLARADA`, `NOVO_EVENTO_DECLARADO`, `NAO_DISCRIMINANTE`. |
| R-3 | **`Vinculo` total** — quatro valores, tabela exaustiva das seis combinações, incluindo **`DECLARACAO_CONTRADITORIA`** para "evento novo declarado + referência ao anterior". |
| R-4 | **Cascata determinística D0–D6**, com comparação **exclusivamente nominal** (caixa, espaços, acentos) — sem score, similaridade ou threshold numérico novo. |
| R-5 | **12 `CriterioIdentidade`**, vocabulário fechado. `DECLARACAO_CONTRADITORIA` é consumida por curto-circuito em D0 e **não** cria um 13º código. |
| R-6 | **`SEM_CANDIDATO_ELEGIVEL` é distinto de primeiro contato**: há histórico conhecido e zero candidatos elegíveis. Não é erro, não é ambiguidade, não autoriza T01 nem T37, e não segue silenciosamente para a máquina. |
| R-7 | **O identificador restringe o escopo, mas não prova continuidade.** O candidato identificado ainda passa pelo teste mesma × nova × ambígua. **Não existe critério `IDENTIFICADOR_VALIDADO`** — a rastreabilidade é o booleano `escopo_restrito_por_identificador`. |
| R-8 | **`SituacaoTakeover` é separada de `Identidade`** — dimensão ortogonal, fora de `CondicoesCiclo`, que não chega à `MaquinaEstados` e não cria estado, evento ou transição. `Identidade` permanece com **quatro** membros. |
| R-9 | **O takeover humano precede D0–D6** (R5-P0). Nenhuma evidência de identidade — referência ao evento anterior, coincidência de tipo/data, identificador apontando outro atendimento ou `NOVO_EVENTO_DECLARADO` — **revoga o takeover**. |
| R-10 | **`HUMANO_UNICO` → T33**: a máquina **é** chamada, com `estado = atendimento_humano` e identidade `None`; `E01` resolve por T33, mantendo o estado e o silêncio automático já obrigatório (I03, regra 11). |
| R-11 | **`HUMANO_MULTIPLO` encerra antes da `MaquinaEstados`**: sem alvo, identidade `None`, a máquina **não** é chamada, processamento pendente preservado, alerta operacional e zero emissão. O motor **não escolhe** entre os atendimentos nem usa recência para desempatar. |
| R-12 | **Zero estado, evento ou transição nova.** T31, T33, T34, T36 e T37 permanecem exatamente como estão; o silêncio sob takeover é consequência do contrato já vigente, não política nova. |

**A arbitragem R não implementa nada.** O `ResolvedorIdentidade` permanece **não
implementado**, e nenhuma subetapa funcional foi aberta para ele.

### Arbitragem R-H — escopo aprovado e integrado à `main`

Micro-arbitragem sobre a **fronteira entre contexto recuperado, conjunto elegível e
takeover humano**. Entrega **exclusivamente documental**: alterou somente
`docs/07-arquitetura-motor-respostas.md`. **Zero estado, evento ou transição novo**; não
amplia `Identidade` nem `CriterioIdentidade`.

| # | Decisão |
|---|---|
| R-H-1 | **H = `ids_em_atendimento_humano`.** É **produzido pela etapa 3**, a partir dos atendimentos recuperados cujo estado é `atendimento_humano` — **filtro estrutural de estado**, não filtro de elegibilidade (H1). |
| R-H-2 | **H é entrada própria do `ResolvedorIdentidade`**, parâmetro **distinto** do conjunto elegível. Filtrar os candidatos por estado **não** substitui H. |
| R-H-3 | **N-a NÃO governa H** (H2). Nenhuma política de elegibilidade ou recência pode remover um atendimento humano de H: um canal sob controle humano não "expira" por recência. |
| R-H-4 | **H contém somente IDs opacos** (H3): zero PII, zero texto, zero dado comercial, zero data, zero recência. Ordem irrelevante. |
| R-H-5 | **A cardinalidade de H determina `SituacaoTakeover`** (H4): `0` → `SEM_TAKEOVER`; `1` → `HUMANO_UNICO`; `>= 2` → `HUMANO_MULTIPLO`. |
| R-H-6 | **IDs duplicados em H são erro de contrato** (classe II) — duplicata **não** é lida como `HUMANO_MULTIPLO`. |
| R-H-7 | **Coerência defensiva (H5)**: candidato elegível com `estado == atendimento_humano` **ausente** de H é **erro de contrato**. **A recíproca não é exigida** — ID presente em H e ausente do conjunto elegível é **válido e esperado**, e é justamente o que preserva a independência de H em relação a N-a. |
| R-H-8 | **`HUMANO_UNICO` obtém o alvo diretamente de H** — o único ID de `ids_em_atendimento_humano`, **nunca** derivado dos candidatos elegíveis. |
| R-H-9 | **`HUMANO_MULTIPLO` não escolhe alvo**: alvo `None`, identidade `None`, `MaquinaEstados` não é chamada. |
| R-H-10 | **R5-P0 permanece antes** da restrição por identificador e antes de D0–D6. A precedência do takeover não foi alterada. |
| R-H-11 | **H não entra em `CondicoesCiclo` e não chega à `MaquinaEstados`** (H6). É exclusivamente insumo da resolução de takeover. |
| R-H-12 | **Cenários K-H1–K-H8** registrados em `docs/07` §8.2 como testáveis futuros — **nenhum teste foi escrito**. |

**A arbitragem R-H não implementa nada.** O `ResolvedorIdentidade` permanece **não
implementado**, e a **3B.7 permanece não iniciada**.

**O que a R-H NÃO resolve.** Ela **não resolve N-a**. A N-a continua **aberta** quanto à
**política de elegibilidade**, à **política de recência**, à **janela temporal** e à
**produção concreta do conjunto elegível**. A R-H fixa **apenas** que **N-a não governa H**.
Permanecem igualmente abertas, sem alteração: **N-b, E4, S2-D8, S3-D1, E1, E3, B, C, S2-D5,
S2-D7**, a **confirmação física do handoff** e o **retorno do controle ao bot após
`atendimento_humano` sem `E14`/T34**.

### Arbitragem R-I — escopo aprovado e integrado à `main`

Micro-arbitragem sobre a **projeção do identificador de atendimento validado** da etapa 3
para a etapa 5. Entrega **exclusivamente documental**: alterou somente
`docs/07-arquitetura-motor-respostas.md`. **Zero estado, evento, transição, critério ou
campo de saída novo**; não amplia `Identidade`, `CriterioIdentidade`, `SituacaoTakeover` nem
`VeredictoIdentificador`.

| # | Decisão |
|---|---|
| R-I-1 | **Novo insumo `id_atendimento_validado: str \| None`** — **identificador técnico opaco** do atendimento identificado, projetado pela etapa 3 e entregue ao `ResolvedorIdentidade` como **parâmetro próprio**. Não contém **PII, texto, dado comercial, data nem recência**. A assinatura conceitual passa de cinco para **seis** parâmetros. |
| R-I-2 | **`VeredictoIdentificador` permanece com quatro valores** — `NAO_INFORMADO`, `ENCONTRADO`, `NAO_ENCONTRADO`, `INCOMPATIVEL`. **Nenhum quinto valor** foi criado; o ID validado viaja em campo próprio, nunca como valor de veredito. |
| R-I-3 | **P-I1–P-I5 são pré-condições estruturais de entrada**, verificadas na mesma fronteira conceitual de C2, H4 e H5 — **antes de R5-P0** e, portanto, antes de D0–D6. Violação é **erro de contrato classe II**: nenhuma identidade é devolvida e **nunca** se retorna `AMBIGUA`. |
| R-I-4 | **`ENCONTRADO` implica `havia_estado_esperado = true`** (P-I4). **Não há implicação inversa**: `havia_estado_esperado = true` **não** implica `ENCONTRADO`. |
| R-I-5 | **`ENCONTRADO` exige o atendimento identificado exatamente uma vez** no conjunto elegível (P-I5). Zero ocorrências e duas ou mais ocorrências são, ambas, **erro de contrato classe II**. |
| R-I-6 | **N-I-1–N-I-4 são obrigações do produtor** — da **etapa 3**: projetar o ID quando `ENCONTRADO`; incluir o atendimento identificado no conjunto elegível exatamente uma vez; produzir `havia_estado_esperado = true`; e **bloquear na etapa 3**, com mensagem preservada e alerta operacional, quando não conseguir produzir projeção coerente — sem chamar o resolvedor com entrada incoerente, sem ignorar o identificador e sem criar atendimento novo. |
| R-I-7 | **N-a-F1 — fronteira parcial de N-a.** Com `veredito_identificador == ENCONTRADO`, o atendimento identificado **deve integrar o conjunto elegível exatamente uma vez**, e **nenhuma política de recência ou elegibilidade pode removê-lo naquele ciclo**. |
| R-I-8 | **D2 continua restringindo, não decidindo**, e **D0–D6 permanecem semanticamente inalterados**. Nenhuma guarda de pertinência foi acrescentada a D2 — a existência e a unicidade já são garantidas por P-I5, na entrada. D1 mantém os dois ramos intactos; passa a ser alcançável com escopo vazio somente sob `NAO_INFORMADO`, por **consequência derivada** das pré-condições. **R5-P0 permanece intacto.** |
| R-I-9 | **Zero enum, critério, estado, evento, transição ou campo de saída novo.** Continuam: **12** `CriterioIdentidade`, **4** membros em `Identidade`, **3** valores em `SituacaoTakeover`, **4** valores em `VeredictoIdentificador` e **8** campos na saída auditável. `escopo_restrito_por_identificador` continua booleano. |

**`SEM_CANDIDATO_ELEGIVEL` permanece inalterado.** Continua significando **histórico
conhecido + zero candidatos elegíveis**; **não é primeiro contato**, **não é ambiguidade** e
**não é erro**. A R-I **não o reutiliza** para "identificado ausente" — esse caso é erro de
contrato classe II por P-I5. Por **consequência** das pré-condições, o escopo vazio que
alcança D1 ocorre com veredito **`NAO_INFORMADO`**. A pendência **E4** — tratamento de
`SEM_CANDIDATO_ELEGIVEL` pelo `OrquestradorMotor` — **continua aberta**.

**A arbitragem R-I não implementa nada.** O `ResolvedorIdentidade` permanece **não
implementado**, e a **3B.7 permanece não iniciada**.

**O que a R-I NÃO resolve.** Ela **não resolve N-a**. A N-a continua **aberta** quanto à
**política de elegibilidade dos demais candidatos**, à **definição de recência**, à **janela
temporal**, à **composição concreta do conjunto** e à **consulta concreta da persistência**.
A R-I fixa **apenas** a fronteira parcial **N-a-F1**. Permanecem igualmente abertas, sem
alteração: **N-b, E4, S2-D8, S3-D1, E1, E3, B, C, S2-D5, S2-D7**, a **confirmação física do
handoff** e o **retorno do controle ao bot após `atendimento_humano` sem `E14`/T34**. Fica
registrada como **nova questão residual aberta** a **unicidade geral de `id_atendimento`
entre candidatos não identificados** — a R-I exige unicidade **apenas do ID explicitamente
identificado** e **apenas** quando `veredito == ENCONTRADO`; **nenhuma regra global de
unicidade foi estabelecida**.

### Arbitragem S3 — escopo aprovado e integrado à `main`

Arbitragem **residual** da `MaquinaEstados`: fecha as ambiguidades que restavam depois da
S2, **sem redesenhar a máquina**. Preserva os 8 estados, `E01`–`E18`, T01–T41, P1–P6,
N1–N4 e S2.1–S2.9 — **zero estado novo, zero evento novo, zero `Txx` nova, zero P7, zero
N5**. Entrega **exclusivamente documental**: nenhum código, teste, dado comercial ou
dependência foi alterado — **a própria S3 não implementou a `MaquinaEstados`**, que veio
depois, na 3B.6.

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

Status da S3: **APROVADA — INTEGRADA À MAIN.** O **PR #18** está **MERGED**, com merge
`ac49758771efe00596e27a9d8eec034d4c85df04`, head integrado
`40841a3ef6ef00b83313d41e95c52c4f6c1045a8` e commit documental principal
`541aa765ac0e956620e3a78c19b38c0d24a40885`. Ela **não criou marco funcional**: no momento
do seu merge, o último commit funcional continuava `02dcb477…` e o último marco, a
**3B.5**. A implementação da `MaquinaEstados` veio depois, na **3B.6** (PR #21).

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

- a S2 **não criou marco funcional**: no momento do seu merge, o último commit funcional
  aprovado e o último marco funcional continuavam sendo os da **3B.5**;
- a S2 **não implementou** a `MaquinaEstados` — isso ocorreu depois, na **3B.6** (PR #21);
- **status atual: APROVADA — INTEGRADA À MAIN.** A S2 foi **aprovada pelo GPT** e
  integrada à `main` pelo **PR #16** (**MERGED**), com merge
  `1a719546b922e0a89d30912de745046eb11849d9` e head integrado
  `e4746d8b350b65388672ecfb5233a558031ff352`, a partir da branch
  `docs/s2-arbitragem-maquina-estados`. O núcleo documental permanece no commit
  `0be5a022d2b30b5cfa2bca501e77c06bed501419`. **Integrar a arbitragem não autorizava, por
  si só, implementação**: a 3B.6 exigiu mandato próprio e foi entregue no PR #21.

## Pendências técnicas em aberto

Registradas aqui como estado, não resolvidas nesta entrega.

| # | Pendência | Antes de quê precisa ser arbitrada |
|---|---|---|
| B | Colisão conceitual de nome: `RegistroAtendimento` já existe em `src/casa77_sdr/persistence.py` como dataclass de transporte, enquanto `docs/07` usa o mesmo nome para uma responsabilidade futura | implementar o componente `RegistroAtendimento` descrito em `docs/07` |
| C | Não existe contrato estruturado, legível por máquina, relacionando as respostas aprovadas (`Rxx`) aos campos do YAML | implementar `ValidadorConsistenciaBase` e, em cascata, `SeletorFatos` e `ValidadorResposta` |

As pendências **B e C permanecem inalteradas** pelas arbitragens S2, S3, R, R-H e R-I.

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

### Pendências da arbitragem R — abertas pelo PR #23

Registradas pelo contrato de identidade. **Nenhuma é resolvida** por aquele PR, pelo **PR
#25** (arbitragem R-H), pelo **PR #27** (arbitragem R-I) nem por esta reconciliação —
salvo a fronteira **parcial** N-a-F1 registrada abaixo. Detalhe em `docs/07` §12.

| # | Pendência | Situação |
|---|---|---|
| N-a | Política concreta de **elegibilidade e recência** que produz o conjunto elegível da etapa 3, **e** o tratamento de `SEM_CANDIDATO_ELEGIVEL` na integração. **Continua ABERTA** quanto à política de elegibilidade, à política de recência, à janela temporal e à produção concreta do conjunto elegível. A **arbitragem R-H não a resolve** — fixa **apenas** que **N-a não governa o conjunto H** (`docs/07` §6.2, H2). A **arbitragem R-I também não a resolve**: fixa **apenas** a fronteira parcial **N-a-F1** — com `veredito_identificador == ENCONTRADO`, o atendimento identificado **deve** integrar o conjunto elegível **exatamente uma vez** e **nenhuma política de recência ou elegibilidade pode removê-lo naquele ciclo** (`docs/07` §6.2). **Todo o restante de N-a continua aberto.** | **não bloqueia** a 3B.6; **bloqueia** o `OrquestradorMotor` e a integração completa |
| N-b | Contrato global da **interpretação**: quem produz a projeção estruturada consumida pelo resolvedor (`intencao_identidade`, referências, confianças binárias) e com que garantias. **Produtor não atribuído.** | **não bloqueia** a 3B.6; **bloqueia** a integração completa |
| E1 | Distinção entre as entidades **conversa × atendimento × lead**. Já registrada como aberta desde a etapa de modelo de dados; a arbitragem R **não** a resolve. | **não bloqueia** a 3B.6 |
| E3 | **Evento novo declarado durante atendimento ativo.** Hoje o resultado é **conservador** — `AMBIGUA` / `AMBIGUIDADE_DIVERGENCIA_EM_ATENDIMENTO_ATIVO`. **Nenhuma transição nova foi aprovada** para abrir atendimento paralelo. | **não bloqueia** a 3B.6 |
| E4 | Tratamento de **`SEM_CANDIDATO_ELEGIVEL`** pelo `OrquestradorMotor`. O resultado existe e é auditável, mas o que o orquestrador faz com ele **não está decidido**; enquanto aberta, o resultado encerra o ciclo sem transição e **não autoriza avanço de integração**. | **não bloqueia** a 3B.6; **bloqueia** o `OrquestradorMotor` |
| Unicidade geral de `id_atendimento` | **Questão residual aberta pelo PR #27.** A R-I exige unicidade **apenas do ID explicitamente identificado** e **apenas** quando `veredito == ENCONTRADO` (P-I5). **Não foi decidido** se IDs duplicados entre candidatos **não identificados** constituem erro geral de contrato. **Nenhuma regra global de unicidade foi estabelecida**, e nada é corrigido silenciosamente. | **não bloqueia** a 3B.6 nem a 3B.7 |
| Retorno do controle ao bot | Não existe hoje **transição inversa de T31** que devolva o canal ao atendimento automático sem passar por `E14`/T34. **Nenhum evento ou transição foi criado** para isso. | **não bloqueia** a 3B.6 nem a arbitragem R |

## Pendências que não bloqueiam

- Itens pendentes da base: ver `knowledge/informacoes-pendentes.md` (fonte única das
  lacunas; não replicar aqui).

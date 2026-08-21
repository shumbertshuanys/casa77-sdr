# 00 — Estado Atual do Projeto

Documento de estado: registra etapa, subetapa, PRs, commits, testes e próxima ação.
**Não contém dado comercial.** Preço, capacidade, tipo de evento, horário, restrição e
qualquer outra condição vivem exclusivamente em `knowledge/casa77.yaml`.

Atualizado em: 2026-08-21.

## Referências

| Item | Valor |
|---|---|
| Projeto | Casa 77 SDR |
| Branch de referência | `main` |
| Último commit **funcional** aprovado | `2da532f150cd4024fbca4eb82af7440e5008b12a` |
| Merge correspondente na `main` | `048a5483493774f53b46425a783afa9f8bccbc46` |
| Última **entrega funcional** concluída | **Materialização em runtime da projeção `transicoes_que_mudaram_estado`** na `MaquinaEstados` / `DecisaoMaquina` (`src/casa77_sdr/state_machine.py`, PR #44). **Sem numeração oficial de subetapa**: não é a 3B.8, que **não existe** |
| Entrega funcional **anterior** | Montagem determinística das projeções de identidade da etapa 3 — fronteira **etapa 3 → identidade/etapa 5** (`src/casa77_sdr/context.py`, PR #38 — commit `f312eaa5…`, merge `10810506…`). Também **sem numeração de subetapa** |
| Entrega funcional **anterior a essa** | Implementação funcional da política N-a — produção determinística do conjunto elegível **E** (PR #36 — commit `51fae0d1…`, merge `383c5668…`). Também **sem numeração de subetapa** |
| Entrega funcional **anterior a essa (3)** | Evolução temporal do contrato de persistência operacional — `instante_ultima_transicao` (PR #33 — commit `0350e4ec…`, merge `1256628e…`). Também **sem numeração de subetapa** |
| Última **subetapa funcional numerada** concluída | 3B.7 — ResolvedorIdentidade determinístico (PR #29 — commit `25ab2726…`, merge `568919f5…`) |
| Subetapa 3B.7 | **CONCLUÍDA** |
| Arbitragem documental **N-a** | Arbitragem **N-a** — PR #31, commit `43774af5…`, merge `e8425410…`. **Não altera o marco funcional** |
| Arbitragem documental da **projeção de mudança de estado** | PR #42, commit documental `f7b5d94cd22ce0d0fcf573823d9f5e56c853ac99`, merge `210ef72790f6317719340e8e0f842d272db6e137`. **Não altera o marco funcional**. O contrato ali arbitrado foi **materializado depois** pelo **PR #44** |
| Última **reconciliação documental** anterior a esta entrega | Reconciliação de `docs/00` após o PR #42 — PR #43, commit documental `900a618a50a040f2390ae5374bb67953f6217b0f`, merge `7610f06a7587168d70f13cc865a335d1f8b1ff2b`, branch de origem `docs/reconciliar-estado-pos-pr42`. Arquivo: **exclusivamente** `docs/00-estado-atual.md` — **51 adições, 35 remoções**. **Não altera o marco funcional** |
| Base da presente reconciliação | `048a5483493774f53b46425a783afa9f8bccbc46` — HEAD da `main` verificado **antes** desta entrega (PR #44, **funcional**) |
| Subetapa 3B.6 | **CONCLUÍDA** (marco funcional anterior — commit `d5108773…`, merge `e3dbe555…`, PR #21) |
| Subetapa 3B.5 | **CONCLUÍDA** (commit `02dcb477…`, merge `55f6ed77…`, PR #14) |

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
| Etapa 3B.7 — `ResolvedorIdentidade` determinístico (`src/casa77_sdr/identity.py` + testes): resolução pura e determinística de **qual atendimento** a mensagem trata, **anterior** à `MaquinaEstados` no pipeline — vocabulários fechados de identidade, `CandidatoAtendimento`, `ProjecaoInterpretacao`, `DecisaoIdentidade`, comparação exclusivamente nominal, confiança binária, pré-condições **C2**, **H4/H5** e **P-I1–P-I5**, precedência de takeover **R5-P0**, cascata **D0–D6**, **RELACAO** e fechamento conservador, com saída auditável de **8** campos — sem I/O, sem rede, sem LLM, sem leitura de YAML, sem relógio e sem persistência | **funcional** | PR #29 — **INTEGRADO à `main`** em 2026-08-19 (commit funcional `25ab2726e15daeb7710bc0bcce9cfe7e092ce9f4`, merge `568919f5976361fa236e46a67909366e52ee85c3`, branch de origem `feat/3b7-resolvedor-identidade`). Arquivos: `src/casa77_sdr/identity.py`, `tests/test_identity.py`, `src/casa77_sdr/__init__.py` — **3 files changed, 2224 insertions(+)**. **Cria o novo marco funcional**, que passa a ser a **3B.7** |
| Arbitragem N-a — **política de produção do conjunto elegível da etapa 3** (`docs/07`): classificação **fechada dos oito estados**; recência aplicável **exclusivamente** a `encerrado`; `instante_ultima_transicao` como único marco temporal do MVP, alimentado pelo **timestamp do ciclo** e **nunca** por relógio vivo; limiar como **configuração operacional explícita, sem default**; projeção `RegistroAtendimento` → `CandidatoAtendimento`; composição de E; duplicatas não identificadas **preservadas**; ordem canônica **só para auditabilidade**; **N-a-F1**, **H1–H6**, **R5-P0** e **D0–D6** preservados; cenários **K-Na-1–K-Na-18** | documental/governança | PR #31 — **INTEGRADO à `main`** em 2026-08-20 (commit documental `43774af58877e3de3ecfda32cf0384a9fd047693`, merge `e8425410a7ced47c8d186bfceeea1cdd70f73b0c`, branch de origem `docs/arbitragem-na-contexto-elegivel`). Arquivo alterado: **exclusivamente** `docs/07-arquitetura-motor-respostas.md` — **1 file changed, 247 insertions(+), 12 deletions(-)**. **Não cria marco funcional** e **não altera** o marco **3B.7** |
| **Evolução temporal do contrato de persistência operacional** — `instante_ultima_transicao` (`src/casa77_sdr/persistence.py` + testes, com reconciliação factual de `docs/07`): `RegistroAtendimento` passa a transportar `instante_ultima_transicao: datetime \| None = None`; **`None` permitido** no armazenamento; valor **não-`None` exige `datetime` com fuso efetivo**; **validação estrutural precede a falha simulada** em `criar` e `gravar`; **zero relógio vivo**; **zero preenchimento automático**; a persistência **não decide quando atualizar** o marco | **funcional** | PR #33 — **INTEGRADO à `main`** em 2026-08-20 (commit funcional `0350e4ec8391960d7f31c4af648406481367f181`, merge `1256628eebf25e31539b6be86fc6c9869ed8e9bd`, branch de origem `feat/persistencia-marco-temporal`). Arquivos: `docs/07-arquitetura-motor-respostas.md`, `src/casa77_sdr/persistence.py`, `tests/test_persistence.py` — **3 files changed, 491 insertions(+), 8 deletions(-)**. **Não implementa N-a** e **não recebe numeração de subetapa** |
| **Implementação funcional da política N-a** — produção determinística do conjunto elegível **E** (`src/casa77_sdr/eligibility.py` + testes, com reconciliação factual de `docs/07`): cria o módulo e a função pura `produzir_conjunto_elegivel(...)`, que recebe os **registros já recuperados** e devolve **somente E** — `tuple[CandidatoAtendimento, ...]`. Materializa validação explícita do limiar, projeção `RegistroAtendimento` → `CandidatoAtendimento`, classificação fechada dos **oito** estados, recência **exclusiva** de `encerrado` com borda **inclusiva**, **N-a-F1**, preservação de duplicatas não identificadas e **ordem canônica** estrutural; sinaliza `ConfiguracaoTemporalInvalida`, `MarcoTemporalAusente`, `ContextoElegibilidadeCorrompido` e `IdentificadoIncoerente`. **Zero relógio vivo, zero I/O, zero YAML, zero LLM, zero rede.** **Não cria componente arquitetural novo** e **não implementa o `OrquestradorMotor`** | **funcional** | PR #36 — **INTEGRADO à `main`** em 2026-08-20 (commit funcional `51fae0d1d0388bb131fa8917709d30d10da5ac1a`, merge `383c5668f483ce4c199f756ed581ba7fbac030d1`, branch de origem `feat/na-conjunto-elegivel`). Arquivos: `docs/07-arquitetura-motor-respostas.md`, `src/casa77_sdr/eligibility.py`, `tests/test_eligibility.py` — **3 files changed, 889 insertions(+), 5 deletions(-)**. **Não recebe numeração de subetapa** |
| **Montagem determinística das projeções de identidade da etapa 3** — fronteira **etapa 3 → identidade/etapa 5** (`src/casa77_sdr/context.py` + testes, com reconciliação factual de `docs/07`): cria o módulo e a função `montar_projecoes_identidade_etapa3(...)`, que lê a persistência operacional **somente para consulta** — `recuperar_por_id` e `consultar_por_contato` —, valida o identificador, projeta o contexto **integral**, constrói **H** por filtro estrutural de estado **fora de N-a**, determina **`havia_estado_esperado`** sobre o contexto recuperado (**nunca** sobre E), projeta **`id_atendimento_validado`** (**N-I**) e entrega o DTO fechado **`ProjecoesIdentidadeEtapa3`** de **cinco** campos. Altera `eligibility.py` para separar **seleção de E não canonicalizado** (`selecionar_conjunto_elegivel`) de **canonicalização** (`canonicalizar_conjunto_elegivel`), preservando `produzir_conjunto_elegivel(...)` como **composição compatível** das duas — sem mudança de semântica de N-a. Respeita a **ordem normativa** de `docs/07` §6.2, inclusive o **passo 12 antes do passo 13**. Sinaliza bloqueio por `IdentificadorNaoResolvido` (transporta **apenas o veredito fechado**, sem identificador, canal, contato ou PII), `ConjuntoHumanoIncoerente` e `ProjecaoIdentificadorIncoerente`. **Zero escrita na persistência, zero relógio vivo, zero YAML, zero LLM, zero rede.** **Não chama `resolver_identidade`**, **não chama a `MaquinaEstados`**, **não cria componente arquitetural novo** e **não implementa o `OrquestradorMotor`** | **funcional** | PR #38 — **INTEGRADO à `main`** em 2026-08-21 (commit funcional `f312eaa51cc14bc6dca954fa2df3ceb855560785`, merge `10810506cac53d31fed8d5a85ca8467c9af389a8`, branch de origem `feat/contexto-identidade-etapa3`). Arquivos: `docs/07-arquitetura-motor-respostas.md`, `src/casa77_sdr/__init__.py`, `src/casa77_sdr/context.py`, `src/casa77_sdr/eligibility.py`, `tests/test_context.py` — **5 files changed, 1476 insertions(+), 12 deletions(-)**. **Não recebe numeração de subetapa** |
| **Reconciliação do estado após o PR #38** (`docs/00`): registra o marco funcional `f312eaa…` / merge `10810506…`, o baseline **`749 passed`**, a série de baselines, as **três** entregas funcionais posteriores à 3B.7 e as pendências remanescentes | documental | PR #39 — **INTEGRADO à `main`** em 2026-08-21 (commit documental `1247c4e18a6f3ddc0e66346d6ffed51a6a1345ab`, merge `95fdf0197687cffd4a1aa930b6592f98d7f22e90`, branch de origem `docs/reconciliar-contexto-identidade-pos-merge`). Arquivo alterado: **exclusivamente** `docs/00-estado-atual.md`. **Não cria marco funcional** e **não altera** o marco do **PR #38** |
| **Micro-reconciliação factual de `docs/07`** quanto ao estado de **N-a**: o **item 18** de §12 passa a distinguir a **política determinística já executável** — que recebe o limiar como **argumento explícito** e o valida — do **valor operacional** e do **mecanismo concreto de carga**, que continuam pendentes e seguem bloqueando a **integração operacional** e o `OrquestradorMotor`; o fecho de §12 passa a registrar que **N-a possui materialização PARCIAL em código** pelas entregas dos PRs **#33**, **#36** e **#38**, permanecendo pendentes **N-a-T3–N-a-T7**, o limiar e sua carga, **S4/S5** e o **destino do alerta**. **Nenhum número, tecnologia, variável de ambiente, arquivo ou serviço foi escolhido** | documental | PR #40 — **INTEGRADO à `main`** em 2026-08-21 (commit documental `903a5e92d1ceb70a338b718ac4439e6a2078405c`, merge `d358a333d8ac34f12f055d584a3cd6fe0fc702a6`, branch de origem `docs/reconciliar-na-pos-contexto-identidade`). Arquivo alterado: **exclusivamente** `docs/07-arquitetura-motor-respostas.md` — **1 file changed, 13 insertions(+), 6 deletions(-)**. **Zero código**, **zero teste** e **nenhum marco funcional novo** |
| **Reconciliação do estado após o PR #40** (`docs/00`): registra os PRs **#39** e **#40** como integrados e documentais, reatribui as execuções reais de teste à reconciliação do **PR #39**, e substitui rótulos auto-invalidantes por formulações estáveis — "reconciliação documental anterior a esta entrega" e "Base da presente reconciliação" | documental | PR #41 — **INTEGRADO à `main`** em 2026-08-21 (commit documental `f23b016f6e8ffd0aba0f8d246ad4c0e80d0cfbcd`, merge `049fb62342d3e27a1b8680d17e5aac4767fad9bc`, branch de origem `docs/reconciliar-estado-pos-pr40`). Arquivo alterado: **exclusivamente** `docs/00-estado-atual.md` — **1 file changed, 41 insertions(+), 21 deletions(-)**. **Zero código**, **zero teste** e **nenhum marco funcional novo** |
| **Arbitragem da projeção de mudança de estado** (`docs/06` §4.2 e `docs/07` §2, §6.2, §8.1, §12): arbitra o **contrato conceitual** `transicoes_que_mudaram_estado: tuple[Transicao, ...]` — **subsequência ordenada de `caminho`** com as `Txx` que **efetivamente mudaram o estado intermediário no instante da aplicação**. Fixa a **`MaquinaEstados` como fonte autoritativa** (sem *replay* externo, sem tabela paralela, sem exposição da estrutura interna de regras), rejeita `estado_inicial != estado_final` como critério, trata **T35 dinamicamente** pelo estado intermediário efetivo, avalia **cada `Txx` individualmente**, combina as **até três chamadas** do ciclo pela existência de **ao menos uma** decisão com projeção não vazia, e separa a **criação** de atendimento (**N-a-T3**) da **atualização** de atendimento existente (**N-a-T4/N-a-T5**). **Nenhuma lista normativa paralela** de transições é criada — `docs/06` §3 continua fonte única | arbitragem documental/governança | PR #42 — **INTEGRADO à `main`** em 2026-08-21 (commit documental `f7b5d94cd22ce0d0fcf573823d9f5e56c853ac99`, merge `210ef72790f6317719340e8e0f842d272db6e137`, branch de origem `docs/arbitragem-projecao-mudanca-estado`). Arquivos: `docs/06-maquina-de-estados.md`, `docs/07-arquitetura-motor-respostas.md` — **2 files changed, 70 insertions(+), 3 deletions(-)**. **Zero código**, **zero teste** e **nenhum marco funcional novo**: o contrato foi **ARBITRADO** ali e **materializado depois**, pelo **PR #44** |
| **Reconciliação do estado após o PR #42** (`docs/00`): registra a integração do **PR #42**, mantém — **naquele momento** — o **PR #38** como marco funcional, preserva o baseline **`749 passed`** / **Python 3.14.5** e registra a projeção `transicoes_que_mudaram_estado` como **arbitrada porém ainda não materializada naquele momento histórico** | documental | PR #43 — **INTEGRADO à `main`** em 2026-08-21 (commit documental `900a618a50a040f2390ae5374bb67953f6217b0f`, merge `7610f06a7587168d70f13cc865a335d1f8b1ff2b`, branch de origem `docs/reconciliar-estado-pos-pr42`). Arquivo alterado: **exclusivamente** `docs/00-estado-atual.md` — **1 file changed, 51 insertions(+), 35 deletions(-)**. **Não criou marco funcional**; aquele estado histórico foi **superado funcionalmente depois** pelo **PR #44** |
| **Materialização em runtime da projeção `transicoes_que_mudaram_estado`** (`src/casa77_sdr/state_machine.py` + testes, com reconciliação factual de `docs/06` e `docs/07`): `DecisaoMaquina` passa a expor `transicoes_que_mudaram_estado: tuple[Transicao, ...] = ()` como **último** campo, e a **`MaquinaEstados` é a fonte autoritativa** da projeção — a informação **nasce dentro dela**, no instante da aplicação de cada `Txx`. Cada transição é classificada contra o **estado intermediário imediatamente anterior à sua própria aplicação**; a saída **preserva a ordem** e é **subsequência de `caminho`**, podendo ser vazia, unitária ou múltipla. **T35 é coberta dinamicamente** pela regra genérica — muda o estado a partir de origem diferente de `encerrado` e o preserva quando a origem efetiva já é `encerrado` —, **sem regra estática**. **Zero replay externo**, **zero uso de `estado_inicial != estado_final` como algoritmo de produção**, **zero tabela paralela** e **zero lista normativa** de transições que preservam estado: `docs/06` §3 continua fonte única | **funcional** | PR #44 — **INTEGRADO à `main`** em 2026-08-21 (commit funcional `2da532f150cd4024fbca4eb82af7440e5008b12a`, merge `048a5483493774f53b46425a783afa9f8bccbc46`, branch de origem `feat/projecao-mudanca-estado`, mensagem `feat: project state-changing transitions`). Arquivos: `docs/06-maquina-de-estados.md`, `docs/07-arquitetura-motor-respostas.md`, `src/casa77_sdr/state_machine.py`, `tests/test_state_machine.py` — **4 files changed, 191 insertions(+), 11 deletions(-)**. **Não recebe numeração de subetapa** |

O PR #4 atualiza base comercial e documentação a partir de decisões de Douglas Bianchi
(2026-08-15). Ele **não** é implementação funcional do motor e não altera o marco
funcional acima.

Os PRs #16 e #18 integram as arbitragens documentais S2 e S3. Nenhum dos dois é
implementação funcional do motor: nenhum arquivo de `src/`, `tests/`, `knowledge/` ou
`prompts/` foi alterado, e nenhum deles alterou o marco funcional — que **naquele
momento** era a 3B.5. O marco funcional passou a ser a 3B.6 somente com o PR #21.

O **PR #23** integrou a arbitragem documental **R** do `ResolvedorIdentidade`. Valeu a
mesma regra: alterou **exclusivamente** `docs/06-maquina-de-estados.md` e
`docs/07-arquitetura-motor-respostas.md` — nenhum arquivo de `src/`, `tests/`, `knowledge/`
ou `prompts/` — e **não criou marco funcional**: **naquele momento** o marco funcional
seguia sendo a **3B.6**. À época, ele especificou um componente que **ainda não existia em
código**. A **implementação funcional viria depois**, na **3B.7**, pelo **PR #29**.

O **PR #25** integrou a **micro-arbitragem documental R-H** — fronteira entre contexto
recuperado, conjunto elegível e takeover humano. Valeu a mesma regra: alterou
**exclusivamente** `docs/07-arquitetura-motor-respostas.md` — nenhum arquivo de `src/`,
`tests/`, `knowledge/` ou `prompts/` — e **não criou marco funcional**: **naquele momento** o
marco funcional seguia sendo a **3B.6**. Ele detalhou a entrada `ids_em_atendimento_humano`
**antes da existência do código**. Esse contrato foi **materializado depois na 3B.7**, pelo
**PR #29**.

O **PR #27** integrou a **micro-arbitragem documental R-I** — projeção do identificador de
atendimento **validado** da etapa 3 para a etapa 5. Valeu a mesma regra: alterou
**exclusivamente** `docs/07-arquitetura-motor-respostas.md` (`+117 / -9`) — nenhum arquivo
de `src/`, `tests/`, `knowledge/` ou `prompts/` — e **não criou marco funcional**: **naquele
momento** o marco funcional seguia sendo a **3B.6**. Ele acrescentou o insumo
`id_atendimento_validado` ao contrato **antes da implementação**. Esse contrato foi
**materializado depois na 3B.7**, pelo **PR #29**.

O **PR #29** é a primeira entrega **funcional** desde a 3B.6: ele implementa o
`ResolvedorIdentidade` especificado por **R**, **R-H** e **R-I**. Diferente dos PRs
documentais acima, **altera o marco funcional**, que passa da **3B.6** para a **3B.7**.
Ele **criou** `src/casa77_sdr/identity.py` e `tests/test_identity.py` e **alterou**
`src/casa77_sdr/__init__.py` — exclusivamente para expor a nova superfície pública da
3B.7. Nenhum dos módulos funcionais preexistentes — `state_machine.py`, `rules.py`,
`persistence.py`, `normalization.py` e `qualification.py` — foi alterado, e nenhum
arquivo de `docs/`, `knowledge/` ou `prompts/` foi tocado. O `OrquestradorMotor`
**continua não implementado**.

O **PR #31** integrou a **arbitragem documental N-a** — política de produção do conjunto
elegível da etapa 3. Valeu a mesma regra dos PRs #23, #25 e #27: alterou **exclusivamente**
`docs/07-arquitetura-motor-respostas.md` (`+247 / -12`) — nenhum arquivo de `src/`,
`tests/`, `knowledge/` ou `prompts/` — e **não cria marco funcional**: o marco funcional
**continuava sendo a 3B.7**. Ele **especifica** a política, **não a implementa**: **à
época daquele PR**, N-a não havia sido implementada, `src/casa77_sdr/persistence.py`
**não foi alterado por aquela arbitragem** e o campo `instante_ultima_transicao` ainda
**não existia em código**.

O **PR #33** é a **entrega funcional posterior** que materializou **parte** daquele
contrato: o **transporte e a validação da representação** de
`instante_ultima_transicao` **agora existem** em `src/casa77_sdr/persistence.py`. A
distinção é normativa — o PR #31 **especificou**; o PR #33 **materializou o campo**. Ele
**não implementou N-a**: **à época daquele PR**, N-a-T3–N-a-T7 não estavam
implementadas, não existia política funcional que produzisse o conjunto elegível **E**,
não existia cálculo de recência nem wiring da etapa 3. O PR #33 **não recebeu numeração
de subetapa**.

O **PR #36** é a **entrega funcional seguinte** e materializou a **produção
determinística do conjunto elegível E**: `src/casa77_sdr/eligibility.py` **agora
existe**. Ele **não concluiu a integração N-a**: **à época daquele PR**, não existiam
produção de **H**, `havia_estado_esperado` nem produtor **N-I**. O PR #36 **também não
recebeu numeração de subetapa**.

O **PR #38** é a **entrega funcional seguinte** e materializou a **montagem
determinística das projeções de identidade da etapa 3** — a fronteira **etapa 3 →
identidade/etapa 5**: `src/casa77_sdr/context.py` **agora existe**, com a consulta
**somente-leitura** à persistência, a validação do identificador, a projeção integral do
contexto, o conjunto **H**, o `havia_estado_esperado` e o produtor **N-I**. A cronologia
é, portanto, **PR #31 especificou → PR #33 materializou o campo temporal → PR #36
materializou E → PR #38 materializou as projeções de identidade da etapa 3**.

O **PR #44** é a **entrega funcional seguinte** e **materializou em runtime** o contrato
que o **PR #42** havia **arbitrado**: a projeção `transicoes_que_mudaram_estado`
**agora existe** em `DecisaoMaquina` e é produzida pela `MaquinaEstados`. A distinção é
normativa — o **PR #42 especificou**; o **PR #44 materializou**. Ele **não implementa
N-a-T3–N-a-T7**, **não implementa a composição entre as até três chamadas** do ciclo,
**não implementa a etapa 13** nem a **escrita operacional** de
`instante_ultima_transicao`, e **não implementa o `OrquestradorMotor`**. O PR #44
**também não recebeu numeração de subetapa**: **nenhuma 3B.8 foi criada, escolhida ou
autorizada**.

O **PR #38 não implementou a etapa 3 inteira**, **não integrou o pipeline completo** e
**não implementou o `OrquestradorMotor`**. Continuam **não implementados**:
**N-a-T3–N-a-T7**, o **tratamento operacional dos bloqueios** (S4, S5), o **destino do
alerta operacional**, **N-b**, **E4**, **S2-D8** e **S3-D1**. O PR #38 **também não
recebeu numeração de subetapa**: **nenhuma 3B.8 foi criada, escolhida ou autorizada**.

## Testes

Última execução real em **2026-08-21**, **auditada antes do merge do PR #44**, em
**Python 3.14.5** — **duas** execuções, nenhuma além destas:

| Comando | Resultado |
|---|---|
| `./.venv/Scripts/python.exe -m pytest tests/test_state_machine.py -q -p no:cacheprovider` | **`257 passed`** |
| `./.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider` | **`759 passed`** |

**Zero failures, zero errors e zero skips** nas duas. Os números do **PR #38** —
**`87 passed`** em `tests/test_eligibility.py`, **`65 passed`** em `tests/test_context.py`
e **`749 passed`** na suíte completa — permanecem registrados como o **baseline
histórico daquela entrega**. A suíte cobre o carregador/validação da base (3B.1,
`tests/test_knowledge.py`), as regras comerciais determinísticas (3B.2,
`tests/test_rules.py`), a persistência operacional em memória (3B.3,
`tests/test_persistence.py`), a normalização de entrada com a chave de idempotência
(3B.4, `tests/test_normalization.py`), a qualificação determinística (3B.5,
`tests/test_qualification.py`), a máquina de estados determinística (3B.6,
`tests/test_state_machine.py`) e a **resolução de identidade determinística** (3B.7,
`tests/test_identity.py`). A cobertura da persistência foi **ampliada pelo PR #33** com
o transporte e a validação de `instante_ultima_transicao`; o **PR #36** acrescentou
`tests/test_eligibility.py` — a **produção determinística do conjunto elegível E**; e o
**PR #38** acrescentou `tests/test_context.py` — a **montagem das projeções de
identidade da etapa 3**. O **PR #44** ampliou `tests/test_state_machine.py` com a
**projeção `transicoes_que_mudaram_estado`**.

**Baseline funcional atual: `759 passed`.**

Histórico: até a 3B.5 o baseline era `180 passed`, e assim permaneceu durante as
arbitragens documentais S2 e S3 — elas não alteram código nem testes. O salto para
`427 passed` decorreu exclusivamente da 3B.6, que acrescentou
`tests/test_state_machine.py`; **`427 passed` foi o baseline até a 3B.6** e permaneceu
inalterado durante as arbitragens documentais **R**, **R-H** e **R-I**. O salto de
**`427 passed` para `574 passed`** decorre exclusivamente da **3B.7**, que acrescentou
`tests/test_identity.py` com **147** casos; **`574 passed` foi o baseline até a 3B.7**
e permaneceu inalterado durante a arbitragem documental **N-a** (PR #31) e sua
reconciliação (PR #32). O salto de **`574 passed` para `597 passed`** — **delta +23** —
decorre exclusivamente do **PR #33**, que ampliou `tests/test_persistence.py`; o teste
direcionado desse arquivo passou de **26** para **49** casos. O salto de **`597 passed`**
**para `684 passed`** — **delta +87** — decorre exclusivamente do **PR #36**, que
acrescentou `tests/test_eligibility.py` com **87** casos. O salto de **`684 passed`**
**para `749 passed`** — **delta +65** — decorre exclusivamente do **PR #38**, que
acrescentou `tests/test_context.py` com **65** casos; **`tests/test_eligibility.py`
permanece com 87 casos** e **nenhum** dos 65 é atribuído a ele. O salto de
**`749 passed` para `759 passed`** — **delta +10** — decorre exclusivamente do
**PR #44**, que acrescentou **10** casos a `tests/test_state_machine.py`, cujo teste
direcionado passou a **`257 passed`**. Os baselines históricos **`180`**, **`427`**,
**`574`**, **`597`**, **`684`** e **`749`** permanecem registrados como acima; a série
completa é **`180 → 427 → 574 → 597 → 684 → 749 → 759`**.

Os PRs **#23** (R), **#25** (R-H), **#27** (R-I), **#31** (N-a), **#32**, **#34**, **#35**,
**#39**, **#40**, **#41**, **#42** e **#43** (reconciliações, arbitragens e correções documentais) e a
presente reconciliação **não alteram código nem testes** e, portanto, **não alteram o
baseline**. Em particular, o **PR #41** alterou **apenas** `docs/00` e o **PR #42** alterou
**apenas** `docs/06` e `docs/07` — **nenhum dos dois** tocou `src/` ou `tests/`. As **duas
execuções acima foram realizadas e auditadas antes do merge do PR #44**, em 2026-08-21.
**Nenhuma execução de testes ocorre nesta reconciliação**, que é puramente documental, e
nenhuma execução além das duas reportadas é alegada.

## Roadmap (resumo — detalhe em `docs/05-roadmap.md`)

Etapas 1 e 2 concluídas; etapa 3 em execução (3A, 3B.1, 3B.2, 3B.3, 3B.4, 3B.5, 3B.6 e
**3B.7** entregues). A antiga Etapa 4 — Qualificação — continua absorvida pela Etapa 3B conforme a
arbitragem S1, e o `Qualificador` foi **implementado na 3B.5**. A `MaquinaEstados` foi
**implementada na 3B.6** e integrada à `main` pelo **PR #21**; as arbitragens documentais
**S2** e **S3** — que trataram das ambiguidades que impediam especificá-la — já estavam
integradas (PR #16, merge `1a719546…`; PR #18, merge `ac49758…`).

A arbitragem documental **R** — contrato de resolução de identidade — foi integrada pelo
**PR #23** (merge `aeb44665…`), e a micro-arbitragem **R-H** — fronteira do conjunto H e do
takeover humano — pelo **PR #25** (merge `96a8ff98…`); e a micro-arbitragem **R-I** —
projeção do identificador **validado** para a etapa 5 — pelo **PR #27** (merge
`4bb202e0…`). **As três especificam** o `ResolvedorIdentidade`, componente **anterior** à
`MaquinaEstados` no pipeline. Elas **não o implementavam**: a implementação veio depois,
na **3B.7**, integrada pelo **PR #29** (merge `568919f5…`) — `src/casa77_sdr/identity.py`
**agora existe**. O `OrquestradorMotor`, esse sim, **permanece não implementado**.

A **3B.7 está CONCLUÍDA e integrada à `main`**. Etapas 5 a 10 permanecem futuras e com a
numeração preservada, conforme `docs/05-roadmap.md` — **não alterado por esta entrega**.

Existem agora **quatro entregas funcionais posteriores à 3B.7 e SEM numeração oficial de
subetapa**: (a) a **evolução temporal do contrato de persistência operacional**
(`instante_ultima_transicao`), integrada pelo **PR #33**; (b) a **implementação
funcional da política N-a** — produção determinística do conjunto elegível **E** em
`src/casa77_sdr/eligibility.py` —, integrada pelo **PR #36**; (c) a **montagem
determinística das projeções de identidade da etapa 3** — fronteira **etapa 3 →
identidade/etapa 5** em `src/casa77_sdr/context.py` —, integrada pelo **PR #38**; e
(d) a **materialização em runtime da projeção `transicoes_que_mudaram_estado`** na
`MaquinaEstados` / `DecisaoMaquina`, integrada pelo **PR #44**.
Nenhuma delas é renomeada para **3B.8** — **a 3B.8 não existe** —, nenhuma **altera a
numeração** do roadmap e nenhuma **significa que a próxima entrega tenha sido
escolhida**. A **última subetapa funcional numerada** continua sendo a **3B.7**.

**Estado funcional do produto.** Estão **implementados**: a **produção determinística de
E**; a **projeção integral reutilizável** dos registros recuperados; a **validação
explícita do limiar**; o conjunto **H**; o **`havia_estado_esperado`**; o **produtor
N-I** / `id_atendimento_validado`; e a **montagem da fronteira etapa 3 →
identidade/etapa 5**. **Continuam NÃO implementados ou parciais**: a **etapa 3 inteira**,
a **integração completa do pipeline** e o **`OrquestradorMotor`**.

**Nenhuma subetapa 3B.8 foi escolhida, proposta ou autorizada por esta entrega.** A
reconciliação anterior foi **integrada e auditada** pelos **PRs #39** e **#41**; o estado de
**N-a** em `docs/07` foi **reconciliado pelo PR #40**; e a **projeção de mudança de estado**
foi **arbitrada pelo PR #42** — **contrato definido, implementação funcional ainda
inexistente**. O GPT reavalia a próxima subetapa **à luz das pendências ainda abertas**, e
**nenhuma delas é eleita aqui**. Em particular, **não** se afirma aqui que
o `OrquestradorMotor` seja a próxima implementação autorizada. A formulação genérica
anterior — "bloqueado por N-a, N-b, E4 e S2-D8" — deixa de valer para **N-a**, e passa a
ser a seguinte, conforme o `docs/07` integrado:

- **N-a — especificação documental: ARBITRADA / CONCLUÍDA** pelo **PR #31**. Deixou de ser
  bloqueador de **especificação**.
- **N-a — produção determinística de E: IMPLEMENTADA** pelo **PR #36** (`src/casa77_sdr/eligibility.py`).
- **Marco temporal — materialização parcial CONCLUÍDA** pelo **PR #33**: o **transporte e
  a validação da representação** de `instante_ultima_transicao` **já existem** em
  `src/casa77_sdr/persistence.py` (`docs/07` §6.2, M-T1–M-T6). **Deixou de ser
  pré-requisito pendente.**
- **Produção de H, `havia_estado_esperado`, produtor N-I e o *wiring* da fronteira
  etapa 3 → identidade/etapa 5: IMPLEMENTADOS** pelo **PR #38**
  (`src/casa77_sdr/context.py`, `docs/07` §6.2, M-C1–M-C8). **Deixaram de ser
  pré-requisitos pendentes.** Isso **não** significa que o *wiring* da **etapa 3 inteira**
  esteja concluído: o que foi materializado é **a fronteira de identidade**, e a
  **integração N-a permanece PARCIAL**.
- Pré-requisitos concretos **ainda pendentes** da N-a, conforme `docs/07` §6.2 e §12:
  as regras **N-a-T3–N-a-T7** — quando inicializar, atualizar ou preservar o marco —,
  que pertencem ao chamador da etapa 13; o **tratamento operacional dos bloqueios**
  (S4, S5); o **destino do alerta operacional**; e o **valor numérico do limiar** com o
  **mecanismo concreto de carga** da configuração. **Todos continuam não
  implementados/pendentes.**
- **N-b**, **E4**, **S2-D8** e **S3-D1** **continuam abertas** e continuam bloqueando o
  `OrquestradorMotor` e a integração completa, conforme `docs/07` §12.

Nenhum bloqueador além dos que o `docs/07` integrado sustenta é afirmado aqui.

### 3B.7 — escopo entregue (implementação integrada pelo PR #29)

Primeira entrega funcional do `ResolvedorIdentidade`. O que está **em código** na `main`:

| Item | Registro |
|---|---|
| Componente | `ResolvedorIdentidade` **isolado, puro e determinístico** — `resolver_identidade(...)` com os **seis** insumos do contrato |
| Arquivos | `src/casa77_sdr/identity.py` (**+778**), `tests/test_identity.py` (**+1418**), `src/casa77_sdr/__init__.py` (**+28**) — 3 files changed, **2224 insertions(+)** |
| Contratos | `CandidatoAtendimento` (4 campos), `ProjecaoInterpretacao` (7 campos) e `DecisaoIdentidade` (**8** campos) — todos `frozen`, sem PII, sem texto livre e sem dado comercial |
| Vocabulários fechados | `IntencaoIdentidade` (3), `ReferenciaEventoAnterior` (2), `Confianca` (2), `Vinculo` (4), `SituacaoTakeover` (**3**), `VeredictoIdentificador` (**4**), `Comparacao` (3), `ClasseCandidato` (4), `CriterioIdentidade` (**12**) |
| Reuso | `Estado` e `Identidade` são **importados de `src/casa77_sdr/state_machine.py`**, não redeclarados. `Identidade` permanece com **4** membros |
| Comparação | **exclusivamente nominal** — caixa, espaços e acentos; sem sinônimo, similaridade, score ou limiar numérico. Data permanece **valor nominal**, sem parse de calendário |
| Confiança | **binária**; `BAIXA` é tratada como **ausência** para efeito de identidade |
| Pré-condições | **C2**, **H4**, **H5** e **P-I1–P-I5**, verificadas **antes de R5-P0** e, portanto, antes de D0. Violação é erro de contrato (`TypeError`/`ValueError`) — **nunca** `AMBIGUA`, e nenhuma identidade é devolvida |
| Decisão | precedência de takeover **R5-P0**, cascata **D0–D6**, **RELACAO** derivada do estado do alvo e **fechamento conservador** |
| Critérios | os **12** códigos de `CriterioIdentidade`. **Não existe `IDENTIFICADOR_VALIDADO`** — a rastreabilidade da restrição continua sendo o booleano `escopo_restrito_por_identificador` |
| Testes | `tests/test_identity.py` — **147 passed**, cobrindo R2-K1–K8, R3-K1–K7, R5-K1–K7, K-H1–K-H8 e R-I-K1–K15, além de vocabulário, contratos, pureza, determinismo e invariantes de saída |
| Situação | **CONCLUÍDA** — integrada à `main` pelo **PR #29** |

**Fronteiras preservadas na implementação.** O componente **não** calcula elegibilidade,
**não** calcula recência, **não** consulta persistência, **não** lê o YAML, **não** usa
LLM, **não** usa rede, **não** usa relógio, **não** aplica transição, **não** chama a
`MaquinaEstados` e **não** implementa o `OrquestradorMotor`. O **conjunto elegível
continua chegando pronto** da etapa 3, e `ids_em_atendimento_humano` continua sendo
entrada separada, fora de N-a. A pureza é verificada por teste: o conjunto de imports do
módulo é fechado em `__future__`, `unicodedata`, `dataclasses`, `enum` e
`casa77_sdr.state_machine`.

**Duplicatas gerais — nada foi decidido.** A 3B.7 **não cria regra global de unicidade**
para `id_atendimento` entre candidatos **não identificados**. **P-I5** exige unicidade
**apenas do ID identificado** e **apenas** com `veredito == ENCONTRADO`. Dois candidatos
não identificados com o mesmo `id_atendimento` **não** falham — há teste provando isso — e
a **pendência residual continua aberta**.

## Próxima ação

1. A **materialização em runtime da projeção `transicoes_que_mudaram_estado`** na
   `MaquinaEstados` / `DecisaoMaquina` está **funcionalmente concluída e integrada à
   `main`** pelo **PR #44** (**MERGED**). Ela **não recebeu numeração de subetapa**. A
   **entrega funcional anterior** é a **montagem determinística das projeções de
   identidade da etapa 3** (PR #38), que permanece integrada.
2. Commit funcional atual: `2da532f150cd4024fbca4eb82af7440e5008b12a`. Merge
   correspondente: `048a5483493774f53b46425a783afa9f8bccbc46`.
3. Baseline funcional atual: **`759 passed`**, com **`257 passed`** no teste direcionado
   de `tests/test_state_machine.py`, em **Python 3.14.5** — zero failures, zero errors e
   zero skips. Baseline anterior: **`749 passed`**; delta **+10**.
4. A **última subetapa funcional numerada** continua sendo a **3B.7 — `ResolvedorIdentidade` determinístico** (PR #29, commit `25ab2726…`, merge
   `568919f5…`), que permanece **CONCLUÍDA**.
5. **O conjunto H, o `havia_estado_esperado` e o produtor N-I agora possuem produtor em
   código**: `context.py` constrói **H** por filtro estrutural de estado **fora de N-a**,
   calcula `havia_estado_esperado` sobre o **contexto recuperado** — **nunca** sobre E —
   e projeta `id_atendimento_validado` **somente** sob `ENCONTRADO`.
6. **A fronteira de identidade da etapa 3 está materializada**: leitura **somente de
   consulta** da persistência, validação do identificador, projeção integral do contexto
   e entrega do DTO fechado `ProjecoesIdentidadeEtapa3`, na ordem normativa de
   `docs/07` §6.2 — inclusive o **passo 12 antes do passo 13**.
7. **A produção determinística de E continua implementada** (PR #36), agora separada em
   **seleção** e **canonicalização**, com `produzir_conjunto_elegivel(...)` preservado
   como composição compatível. **O transporte e a validação de
   `instante_ultima_transicao` continuam implementados** na persistência (PR #33).
8. **`N-a-T3`, `N-a-T4`, `N-a-T5`, `N-a-T6` e `N-a-T7` continuam NÃO implementadas.**
   Decidir **quando** inicializar ou atualizar o marco permanece responsabilidade
   **futura** do chamador da etapa 13.
9. **A etapa 3 NÃO está inteiramente implementada** e **a integração N-a continua
   PARCIAL.** Continuam **não implementados** o **tratamento operacional dos bloqueios**
   (S4, S5) e o **destino do alerta operacional**. **Produzir as projeções de identidade
   não é implementar a etapa 3 inteira.**
10. O **`OrquestradorMotor` continua NÃO implementado** e **nenhuma integração completa
    de pipeline foi iniciada**.
11. Continuam **pendentes** o **valor numérico operacional do limiar** e o **mecanismo
    concreto de carga** da configuração.
12. **Nenhuma subetapa 3B.8 foi criada, escolhida ou autorizada.** A **3B.8 não existe**.
13. **A projeção de mudança de estado EXISTE em runtime.** O **PR #42** arbitrou o
    contrato e o **PR #44 o materializou**: `DecisaoMaquina` expõe
    **`transicoes_que_mudaram_estado: tuple[Transicao, ...] = ()`** e a **`MaquinaEstados`
    é a fonte autoritativa** — a informação nasce dentro dela, no instante da aplicação de
    cada `Txx`. Cada transição é classificada contra o **estado intermediário imediatamente
    anterior à própria aplicação**; a saída **preserva a ordem** e é **subsequência de
    `caminho`**; **T35 é coberta dinamicamente** pela regra genérica; **sem** *replay*
    externo, **sem** usar `estado_inicial != estado_final` como algoritmo de produção,
    **sem** tabela paralela e **sem** lista normativa de transições que preservam estado.
    **Ela deixou de ser pendência de implementação.**
14. **Continuam NÃO implementados**: **`N-a-T3`, `N-a-T4`, `N-a-T5`, `N-a-T6` e
    `N-a-T7`**; a **composição entre as até três chamadas** do ciclo; a **etapa 13** e a
    **escrita operacional** de `instante_ultima_transicao`; o **`OrquestradorMotor`**; e a
    **integração completa do pipeline**. **Materializar a projeção não é implementar a
    escrita do marco temporal.**
15. **A base factual reconciliada nesta entrega é o merge `048a5483…`.** A reconciliação de
    `docs/00` após o PR #42 foi **integrada pelo PR #43**, e a **materialização da projeção
    de mudança de estado** foi **integrada pelo PR #44** (commit funcional `2da532f1…`,
    merge `048a5483…`) — esta **é funcional** e **cria o novo marco**, que passa a ser o do
    **PR #44**.
16. A presente entrega é **exclusivamente reconciliação documental de
    `docs/00-estado-atual.md`** após o merge do **PR #44**: **não altera código, testes,
    `docs/07`, `docs/06`, `docs/05`, base de conhecimento nem prompts**, e **nenhuma
    execução de testes ocorre nela** — os números funcionais atuais registrados são os
    **`257 passed`** / **`759 passed`** executados e auditados em **Python 3.14.5** antes
    do merge do **PR #44**.
17. **Existe planejamento técnico auditado pelo GPT como tecnicamente coerente.** Ele **não
    é uma autorização**: **nenhuma próxima entrega está autorizada por este documento**,
    nenhum rótulo novo é criado e nenhuma numeração é atribuída.
18. **Próxima ação:** após a **integração e a auditoria desta reconciliação**, o GPT poderá
    **autorizar ou não** uma **implementação funcional posterior** do contrato já arbitrado
    pelo **PR #42**. **Esta reconciliação não autoriza implementação funcional por si
    própria** e **nenhuma pendência é eleita aqui** como a implementação seguinte — nem
    `transicoes_que_mudaram_estado`, nem **N-a-T3–T7**, nem **N-b**, nem **E4**, nem
    **S2-D8**, nem **S3-D1**, nem o `OrquestradorMotor`.
19. As pendências permanecem abertas conforme seus próprios bloqueios: **B, C, S2-D5,
    S2-D7, S2-D8, S3-D1, a confirmação de entrega do handoff, N-b, E1, E3, E4, o retorno
    do controle ao bot após `atendimento_humano` sem `E14`/T34**, a **unicidade geral
    de `id_atendimento` entre candidatos não identificados**, a **persistência
    operacional não volátil**, o **tratamento operacional dos bloqueios (S4/S5)**, o
    **destino do alerta operacional**, o **valor numérico operacional do limiar** e o
    **mecanismo concreto de carga** da configuração. Nenhuma delas é resolvida aqui.

## Arbitragens

Decisões de governança. Não criam marco funcional nem código. A coluna Decisão informa o
estado de ciclo de vida de cada arbitragem, incluindo a evidência de integração quando ela
já alcançou a `main`.

| # | Arbitragem | Decisão | Evidência |
|---|---|---|---|
| N-a | **Política de produção do conjunto elegível da etapa 3** (`docs/07-arquitetura-motor-respostas.md`) | **APROVADA — INTEGRADA À MAIN.** Fecha **documentalmente** a política de elegibilidade e recência que a etapa 3 aplica sobre os registros recuperados, **sem criar componente, estado, evento, transição ou critério**. Arbitragem documental **aprovada pelo GPT** e **integrada à `main`** pelo **PR #31** (**MERGED**). **Não implementa código**, **não implementa a persistência**, **não implementa o `OrquestradorMotor`** e **não cria marco funcional.** Escopo abaixo. | PR #31 — commit documental `43774af58877e3de3ecfda32cf0384a9fd047693`, merge `e8425410a7ced47c8d186bfceeea1cdd70f73b0c`, branch de origem `docs/arbitragem-na-contexto-elegivel`; alterações **exclusivamente** em `docs/07` (`+247 / -12`: §5 etapas 3 e 13, §6.2 subseção N-a completa, §7.1 S9–S11 e classe I, §12 item 11 e novo item 18) |
| R-I | **Projeção do identificador validado** para a etapa 5 (`docs/07-arquitetura-motor-respostas.md`) | **APROVADA — INTEGRADA À MAIN.** Micro-arbitragem que fixa `id_atendimento_validado` como **insumo próprio e opaco** do `ResolvedorIdentidade`, com pré-condições estruturais **P-I1–P-I5**, obrigações do produtor **N-I-1–N-I-4** e a fronteira parcial **N-a-F1** — **sem criar estado, evento, transição, critério ou campo de saída**. Arbitragem documental **aprovada pelo GPT** e **integrada à `main`** pelo **PR #27** (**MERGED**). **Não implementa código** e **não cria marco funcional.** Escopo abaixo. | PR #27 — commit documental `713f473c9b9fcae75f73aa0ffadc84dd31e81caa`, merge `4bb202e0bb68f67a8d66e487d85ec7978ea8cd95`, branch de origem `docs/ri-identificador-validado`; alterações **exclusivamente** em `docs/07` (`+117 / -9`: §4.1 linha do componente, §5 etapa 5, §6.1.1 N7 + N-I-1–N-I-4, §6.2 projeção + N-a-F1, §7.1 insumos, assinatura, P-I1–P-I5, efeito sobre a cascata, saída auditável e classes de erro, §8.2 R-I-K1–R-I-K15, §12) |
| R-H | **Fronteira do conjunto H / takeover humano** na resolução de identidade (`docs/07-arquitetura-motor-respostas.md`) | **APROVADA — INTEGRADA À MAIN.** Micro-arbitragem que fixa `ids_em_atendimento_humano` como **entrada própria e separada** do conjunto elegível, **fora** da política N-a, **sem criar estado, evento ou transição**. Arbitragem documental **aprovada pelo GPT** e **integrada à `main`** pelo **PR #25** (**MERGED**). **Não implementa código** e **não cria marco funcional.** Escopo abaixo. | PR #25 — commit documental `24835a8d6cca50a6f783c8b831ca2c924d2177a9`, merge `96a8ff98611fb9de75540ea98adad94166c65e8b`, branch de origem `docs/rh-fronteira-conjunto-h`; alterações **exclusivamente** em `docs/07` (§5 tabela de componentes, §5 etapas 3 e 5, §6.2 + regras H1–H6, §6.3, §7.1 insumos e assinatura conceitual, R5-P0, §7.1 classes de erro, §8.1, §8.2 cenários K-H1–K-H8) |
| R | Contrato de **resolução de identidade** do `ResolvedorIdentidade`, anterior à `MaquinaEstados` (`docs/06-maquina-de-estados.md` × `docs/07-arquitetura-motor-respostas.md`) | **APROVADA — INTEGRADA À MAIN.** Materializa o critério técnico de "mesmo evento × nova solicitação" (T36/T37), que até então era declarado futuro, **sem criar estado, evento ou transição**. Arbitragem documental **aprovada pelo GPT** e **integrada à `main`** pelo **PR #23** (**MERGED**). **Não implementa código** e **não cria marco funcional.** Escopo abaixo. | PR #23 — commit documental `6c848ea8d45e7f6e412cdd297e9ca68c1fa75a21`, merge `aeb446656fd11b91bb61164f29f9adca6959d4df`, branch de origem `docs/arbitragem-resolvedor-identidade`; alterações em `docs/06` (nota da §3, §4.5, §5 regra 12) e `docs/07` (§4.1, §5, §6.1.1, §6.2, §6.3, §6.4, §6.5, §7.1, §8.1, §8.2, §9, §12) |
| S3 | Arbitragem residual da `MaquinaEstados` (`docs/06-maquina-de-estados.md` × `docs/07-arquitetura-motor-respostas.md`) | **APROVADA — INTEGRADA À MAIN.** Fecha as ambiguidades residuais posteriores à S2 sem redesenhar a máquina: materialização de T04, precedência entre classes de `E08`, `T09 > T04`, `T32 > T35`, contrato semântico de ações, condição estruturada de T35, fronteira temporal da resposta aprovada e `CondicoesCiclo`. Arbitragem documental **aprovada pelo GPT** e **integrada à `main`** pelo **PR #18** (**MERGED**). **Não implementa código** e **não cria marco funcional.** Escopo abaixo. | PR #18 — head integrado `40841a3ef6ef00b83313d41e95c52c4f6c1045a8`, merge `ac49758771efe00596e27a9d8eec034d4c85df04`; commit documental principal `541aa765ac0e956620e3a78c19b38c0d24a40885`, a partir da branch `docs/s3-arbitragem-residual-maquina-estados`; alterações em `docs/06` (notas da §3, §4.2, §11) e `docs/07` (§4.1, §4.4, §4.5, §5) |
| A | Fronteira de Qualificação entre `docs/05-roadmap.md` e `docs/07-arquitetura-motor-respostas.md` | **ARBITRADA** (S1): o `Qualificador` permanece componente do motor e sua implementação pertence à Etapa 3B; a antiga Etapa 4 deixa de ser aberta como etapa autônoma e é absorvida pela 3B; as etapas 5 a 10 mantêm a numeração; o `Qualificador` precede a `MaquinaEstados`. O `Qualificador` foi **implementado na 3B.5** (PR #14) e a `MaquinaEstados` foi **implementada na 3B.6** (PR #21); a precedência entre os dois foi respeitada na ordem de entrega. | reconciliação documental de `docs/05`, `docs/07` §8.4/§9 e deste documento |
| S2 | Semântica de ciclo da `MaquinaEstados` (`docs/06-maquina-de-estados.md` × `docs/07-arquitetura-motor-respostas.md`) | **APROVADA — INTEGRADA À MAIN.** Arbitragem documental **aprovada pelo GPT** na auditoria da entrega e **integrada à `main`** pelo **PR #16** (**MERGED**), a partir da branch `docs/s2-arbitragem-maquina-estados`. **Não implementa código** e **não cria marco funcional.** Escopo abaixo. | PR #16 — head integrado `e4746d8b350b65388672ecfb5233a558031ff352`, merge `1a719546b922e0a89d30912de745046eb11849d9`; núcleo documental no commit `0be5a022d2b30b5cfa2bca501e77c06bed501419` — `docs/06` (§1.1, §2.2, §3, §4.1–§4.5, §9, §10, §11) e `docs/07` (§4.1, §5, §7.2, §8.1, §9, §12) |

### Arbitragem N-a — escopo aprovado e integrado à `main`

Arbitragem sobre a **produção do conjunto elegível E** pela etapa 3. Entrega
**exclusivamente documental**: alterou somente `docs/07-arquitetura-motor-respostas.md`.
**Zero componente, estado, evento, transição, critério ou campo novo** — a tabela de
componentes de `docs/07` §4.1 permanece com **14**.

| # | Decisão |
|---|---|
| N-a-a | **Classificação fechada dos oito estados.** Grupo I — `novo`, `coletando_dados`, `respondendo_duvidas`, `aguardando_confirmacao_disponibilidade`, `pronto_para_handoff` e `encaminhado_humano` — é elegível **sem consultar recência**. Grupo II — `atendimento_humano` — fica **fora de E** por N-a. Grupo III — `encerrado` — é elegível **apenas se recente**. |
| N-a-b | **Recência somente para `encerrado`.** É o **único** estado cuja elegibilidade consulta o marco temporal; os demais **não o consultam**. |
| N-a-c | **`instante_ultima_transicao`** é o **único marco temporal normativo do MVP** — o momento da última transição de estado **efetivamente persistida**; para `encerrado`, o último encerramento persistido. |
| N-a-d | **Referência temporal pelo timestamp do ciclo.** A comparação usa o `instante_de_referencia_do_ciclo` — o campo "data e hora" da entrada — e o marco, quando inicializado ou atualizado, **recebe esse mesmo instante**. **Nunca relógio vivo.** A atualização é decidida pelo **caminho de transições**, não por `estado_inicial != estado_final`. |
| N-a-e | **Limiar explícito e sem default.** É **duração**, **configuração operacional** do motor e **argumento explícito** — **não** é dado comercial, **não** vem do YAML, **não** vem do canal, **não** pode ser constante oculta e **não** tem default silencioso. Ausência, tipo inválido ou valor não positivo → **bloqueio**, verificado **sempre**, inclusive sem candidato `encerrado`. |
| N-a-f | **Projeção `RegistroAtendimento` → `CandidatoAtendimento`** com exatamente quatro campos: `id_atendimento`, `estado` (convertido, com os oito valores), `tipo_evento_registrado` ← `dados_coletados["tipo_evento"]` e `data_nomeada_registrada` ← `dados_coletados["data_nomeada"]`. Ausente → `None`; **zero inferência, zero fuzzy, zero LLM, zero fallback semântico**. |
| N-a-g | **N-a-F1 preservada e prevalecente.** Com `veredito_identificador == ENCONTRADO`, o atendimento identificado integra E **exatamente uma vez**, **independentemente de estado ou recência** — inclusive quando está em `atendimento_humano` ou fora do limiar. |
| N-a-h | **H permanece independente de N-a.** É construído por filtro estrutural de estado, **antes e à parte** da filtragem, e **H1–H6 seguem intactas**. |
| N-a-i | **Duplicatas não identificadas**: **não são deduplicadas** e **não bloqueiam apenas pela repetição**. Nenhuma regra global de unicidade foi criada; o bloqueio continua restrito ao ID identificado, por **N-I-2 / P-I5**. |
| N-a-j | **Ordem canônica somente para auditabilidade** — chave estrutural `(id_atendimento, estado, tipo_evento_registrado, data_nomeada_registrada)` ascendente, `None` antes de texto. **Não** elimina candidato, **não** deduplica, **não** muda cardinalidade, **não** usa recência e **não** usa a ordem da persistência. A ordem **não tem significado semântico** para D0–D6. |
| N-a-k | **R5-P0, D0 e D1 preservados, nesta ordem.** H ≠ vazio → **R5-P0**, e D0–D6 **não executam**; contradição declarada → **D0**, mesmo com E vazio. **Restando H vazio e D0 não decisivo**, alcança-se **D1**: E vazio com histórico conhecido → `SEM_CANDIDATO_ELEGIVEL`; E vazio sem histórico → `PRIMEIRO_CONTATO_COMPROVADO`. `havia_estado_esperado` é calculado sobre o **contexto recuperado**, **nunca sobre E**. |
| N-a-l | **Cenários K-Na-1 a K-Na-18** documentados em `docs/07` §6.2, **sem criar ou alterar teste algum**. |

**A arbitragem N-a não implementou nada por si.** **À época do PR #31**, N-a não existia em código, `src/casa77_sdr/persistence.py` **não foi alterado por aquela arbitragem** e o campo `instante_ultima_transicao` ainda não havia sido implementado. **Estado atual**: as materializações vieram depois, em entregas funcionais próprias — o **transporte e a validação da representação** do campo, pelo **PR #33** (`docs/07` §6.2, M-T1–M-T6); a **produção determinística de E**, com classificação e recência, pelo **PR #36** (M-E1–M-E6); e o conjunto **H**, o `havia_estado_esperado`, o **produtor N-I** e o ***wiring* da fronteira etapa 3 → identidade/etapa 5**, pelo **PR #38** (M-C1–M-C8). **A integração N-a permanece PARCIAL**: **N-a-T3–N-a-T7 continuam não implementadas**, o **tratamento operacional dos bloqueios** (S4, S5) e o **destino do alerta** continuam pendentes, a **etapa 3 não está inteiramente implementada**, o `OrquestradorMotor` **continua não implementado** e **nenhuma subetapa 3B.8 foi criada, escolhida ou autorizada**.

**O que a N-a NÃO resolve.** Permanecem **abertas**, sem alteração: **E4**, **N-b**, **S2-D8**, **S3-D1**, **B**, **C**, **E1**, **E3**, **S2-D5**, **S2-D7**, a **confirmação física do handoff**, o **retorno do controle ao bot após `atendimento_humano` sem `E14`/T34** e a **unicidade geral de `id_atendimento` entre candidatos não identificados**. Ficam registradas como **pendências abertas da própria N-a** o **valor numérico do limiar temporal** e o **mecanismo concreto de carga** da configuração — `docs/07` §12, item 18.

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

**A arbitragem R não implementou nada por si.** À época do PR #23, o
`ResolvedorIdentidade` ainda não existia em código e nenhuma subetapa funcional havia sido
aberta para ele. A **implementação funcional veio depois**, na **3B.7**, pelo **PR #29**.

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
| R-H-12 | **Cenários K-H1–K-H8** registrados em `docs/07` §8.2 como testáveis futuros. **À época da arbitragem R-H nenhum teste havia sido escrito**; esses cenários foram materializados depois em `tests/test_identity.py`, pela **3B.7 / PR #29**. |

**A arbitragem R-H não implementou nada por si.** Naquele momento o
`ResolvedorIdentidade` ainda não existia em código e a **3B.7** não havia sido iniciada.
Esse contrato foi **materializado depois na 3B.7**, pelo **PR #29**.

**O que a R-H NÃO resolveu.** Ela **não resolveu N-a**. **À época da R-H**, a N-a
permaneceu **aberta** quanto à **política de elegibilidade**, à **política de recência**,
à **janela temporal** e à **produção concreta do conjunto elegível**. A R-H fixa **apenas** que **N-a não governa H**. **Registro posterior:** a **especificação** de N-a foi **arbitrada e integrada** depois, pelo **PR #31**; a **produção determinística de E** foi materializada pelo **PR #36**; e o conjunto **H** e a **montagem da fronteira etapa 3 → identidade/etapa 5** foram materializados pelo **PR #38**, com **H1–H6 preservadas** e **H continuando fora de N-a**. A **integração N-a permanece PARCIAL**: a **etapa 3 inteira** não está implementada, o **pipeline completo** não está integrado e o `OrquestradorMotor` **continua não implementado**.
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

**A arbitragem R-I não implementou nada por si.** Naquele momento o
`ResolvedorIdentidade` ainda não existia em código e a **3B.7** não havia sido iniciada.
Esse contrato foi **materializado depois na 3B.7**, pelo **PR #29**.

**O que a R-I NÃO resolveu.** Ela **não resolveu N-a**. **À época da R-I**, a N-a
permaneceu **aberta** quanto à **política de elegibilidade dos demais candidatos**, à
**definição de recência**, à **janela temporal**, à **composição concreta do conjunto** e
à **consulta concreta da persistência**.
A R-I fixa **apenas** a fronteira parcial **N-a-F1**. **Registro posterior:** o restante da **especificação** de N-a foi **arbitrado e integrado** depois, pelo **PR #31**, com **N-a-F1 preservada**; a **produção determinística de E** foi materializada pelo **PR #36**, também **preservando N-a-F1**; e o **produtor N-I** — `id_atendimento_validado`, `havia_estado_esperado` e as obrigações **N-I-1–N-I-4** — passou a existir em código com a **montagem da fronteira etapa 3 → identidade/etapa 5** do **PR #38**. A **integração N-a permanece PARCIAL**: a **etapa 3 inteira** não está implementada, o **pipeline completo** não está integrado e o `OrquestradorMotor` **continua não implementado**. Permanecem igualmente abertas, sem
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

As pendências **B e C permanecem inalteradas** pelas arbitragens S2, S3, R, R-H e R-I e
pela implementação funcional da **3B.7** (PR #29).

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
#25** (arbitragem R-H), pelo **PR #27** (arbitragem R-I), pela **implementação funcional
da 3B.7** (PR #29) nem por esta reconciliação — salvo a fronteira **parcial** N-a-F1,
registrada abaixo, e a **especificação** de **N-a**, arbitrada pelo **PR #31** e detalhada
na linha correspondente. A 3B.7 **consome** o contrato; ela não fecha nenhuma destas pendências.
Detalhe em `docs/07` §12.

| # | Pendência | Situação |
|---|---|---|
| N-a | Política de **elegibilidade e recência** que produz o conjunto elegível da etapa 3. **Especificação documental: ARBITRADA / CONCLUÍDA** pelo **PR #31**. **Materialização temporal parcial: IMPLEMENTADA** pelo **PR #33** — transporte e validação de `instante_ultima_transicao` em `src/casa77_sdr/persistence.py` (`docs/07` §6.2, M-T1–M-T6). **Produção determinística de E: IMPLEMENTADA** pelo **PR #36** — `src/casa77_sdr/eligibility.py` (`docs/07` §6.2, M-E1–M-E6). **Conjunto H, `havia_estado_esperado`, produtor N-I e *wiring* da fronteira etapa 3 → identidade/etapa 5: IMPLEMENTADOS** pelo **PR #38** — `src/casa77_sdr/context.py` (`docs/07` §6.2, M-C1–M-C8). **Integração N-a: PARCIAL / NÃO CONCLUÍDA** — continuam **não implementados** **N-a-T3–N-a-T7**, o **tratamento operacional dos bloqueios** (S4, S5) e o **destino do alerta operacional**; a **etapa 3 inteira** e a **integração do pipeline** também **não** estão concluídas. O tratamento de `SEM_CANDIDATO_ELEGIVEL` na integração **não** é parte dela: é a **E4**, pendência distinta e **ainda aberta** | **especificação resolvida**; **campo temporal, produção de E e projeções de identidade materializados**; a **integração** ainda depende de **N-a-T3–N-a-T7**, do **tratamento dos bloqueios**, do **destino do alerta** e do **valor/mecanismo do limiar** (linha abaixo) |
| Limiar temporal de recência | **Valor numérico** do limiar e **mecanismo concreto de carga** da configuração. **Aberta pelo PR #31** (`docs/07` §12, item 18). **Nenhum número foi definido** e **nenhuma tecnologia, variável de ambiente, arquivo ou serviço foi escolhido**. **Não é dado comercial** — não entra em `knowledge/casa77.yaml`; depende de aprovação específica de Douglas Bianchi e de decisão operacional | **não bloqueia** a 3B.6, a 3B.7, a **produção determinística de E** (PR #36) nem a **montagem das projeções de identidade da etapa 3** (PR #38) — ambas recebem o limiar como argumento explícito; **bloqueia** a **integração operacional de N-a no pipeline** e, por consequência, o `OrquestradorMotor` |
| N-b | Contrato global da **interpretação**: quem produz a projeção estruturada consumida pelo resolvedor (`intencao_identidade`, referências, confianças binárias) e com que garantias. **Produtor não atribuído.** | **não bloqueia** a 3B.6; **bloqueia** a integração completa |
| E1 | Distinção entre as entidades **conversa × atendimento × lead**. Já registrada como aberta desde a etapa de modelo de dados; a arbitragem R **não** a resolve. | **não bloqueia** a 3B.6 |
| E3 | **Evento novo declarado durante atendimento ativo.** Hoje o resultado é **conservador** — `AMBIGUA` / `AMBIGUIDADE_DIVERGENCIA_EM_ATENDIMENTO_ATIVO`. **Nenhuma transição nova foi aprovada** para abrir atendimento paralelo. | **não bloqueia** a 3B.6 |
| E4 | Tratamento de **`SEM_CANDIDATO_ELEGIVEL`** pelo `OrquestradorMotor`. O resultado existe e é auditável, mas o que o orquestrador faz com ele **não está decidido**; enquanto aberta, o resultado encerra o ciclo sem transição e **não autoriza avanço de integração**. | **não bloqueia** a 3B.6; **bloqueia** o `OrquestradorMotor` |
| Unicidade geral de `id_atendimento` | **Questão residual aberta pelo PR #27.** A R-I exige unicidade **apenas do ID explicitamente identificado** e **apenas** quando `veredito == ENCONTRADO` (P-I5). **Não foi decidido** se IDs duplicados entre candidatos **não identificados** constituem erro geral de contrato. **Nenhuma regra global de unicidade foi estabelecida**, e nada é corrigido silenciosamente. **Confirmado na implementação da 3B.7**: `src/casa77_sdr/identity.py` valida a unicidade somente do ID identificado, e há teste provando que dois candidatos não identificados com o mesmo `id_atendimento` **não** falham. | **não bloqueia** a 3B.6 nem a 3B.7; **continua ABERTA** |
| Retorno do controle ao bot | Não existe hoje **transição inversa de T31** que devolva o canal ao atendimento automático sem passar por `E14`/T34. **Nenhum evento ou transição foi criado** para isso. | **não bloqueia** a 3B.6 nem a arbitragem R |

## Pendências que não bloqueiam

- Itens pendentes da base: ver `knowledge/informacoes-pendentes.md` (fonte única das
  lacunas; não replicar aqui).

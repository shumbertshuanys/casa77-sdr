# 00 — Estado Atual do Projeto

Casa 77 SDR. Este arquivo é o **snapshot operacional corrente**: etapa, capacidade corrente,
última entrega funcional, baseline, pendências, bloqueadores e próxima ação.

Não é histórico, changelog, ledger nem catálogo de PRs ou commits.

| Assunto | Autoridade |
|---|---|
| Estado técnico definitivo | GitHub, branch `main` |
| Histórico técnico | Git e GitHub — PRs, commits, diffs |
| Dados comerciais e operacionais | `knowledge/casa77.yaml` |
| Regras permanentes e mapa de fontes | `docs/governanca/` |

**Não contém dado comercial.** Preço, capacidade, horário, pacote, condição e restrição vivem
exclusivamente em `knowledge/casa77.yaml`.

---

## 1. Posição atual

- Etapa macro: **Etapa 3 — Motor de respostas — em execução**.
- Última subetapa numerada concluída: **3B.7** (`ResolvedorIdentidade`,
  `src/casa77_sdr/identity.py`).
- O trabalho corrente está no **bloco de materialização de `C`**, composto por microentregas
  funcionais **sem numeração de subetapa**. **Não existe subetapa `3B.8`.**
- Etapa 4 permanece **absorvida pela Etapa 3B**; etapas 5 a 10 permanecem futuras
  (`docs/05-roadmap.md`).

---

## 2. Última entrega funcional relevante

Commit funcional `de9b3579044d4bd1a22e629f67bec70b1de9bab5`.

**Materialização física do índice estruturado de respostas aprovadas e dos *templates* do
corpus.** `knowledge/indice-respostas-aprovadas.yaml` **agora existe**, com **30 `Rxx`**, **37
fragmentos emitíveis** e **118 *bindings***. No Markdown aprovado, **19 fragmentos** passaram a
usar *placeholders* canônicos e **18 permanecem estáticos**.

`tests/test_indice_respostas_aprovadas_corpus.py` materializa a prova permanente de integração
do corpus, sobre os artefatos reais e usando exclusivamente as fronteiras já existentes.

**Zero *renderer* de produção** e **zero consumidor operacional novo**.

---

## 3. Baseline funcional

Último **baseline funcional verificado** — evidência da entrega funcional acima, **não** uma
execução desta atualização:

- Python **3.14.5**;
- **`5789 passed`**, sob **`-W error`**;
- zero failures, zero errors, zero warnings.

CI configurada em GitHub Actions, em `.github/workflows/ci.yml`, com Python **3.13** e **3.14**.
Resultados de execução são evidência do GitHub e não são acumulados neste snapshot.

---

## 4. Estado essencial da capacidade corrente — `C`

- **Contrato de `C`: ARBITRADO** (`docs/07` §2.3; registrado em `docs/07` §12, item 19).
- **A materialização física do índice e dos *templates* do corpus está concluída.** A
  **integração com consumidores operacionais** e a **eventual migração da autoridade de
  status** permanecem **separadas e pendentes**.
- O índice físico `knowledge/indice-respostas-aprovadas.yaml` está **materializado e
  estruturalmente validado**: **30 `Rxx`**, **37 fragmentos**, **118 *bindings***. Ele guarda
  **referentes**, nunca valor resolvido (`C-1h`–`C-1m`, `C-15e`).
- A **autoridade de status NÃO migrou** para o índice: continua em
  `knowledge/respostas-aprovadas.md` (`C-11`), com rótulos e `status-fragmento` preservados. A
  transição de autoridade depende de **entrega separada**, auditada e autorizada.
- `CY13`:
  - **linha 1** — parser da gramática de `caminho_yaml`
    (`src/casa77_sdr/response_yaml_path.py`): materializada e integrada a `E1`
    **indiretamente**, através da linha 2;
  - **linha 2** — validação estrutural contextual
    (`src/casa77_sdr/response_yaml_path_context.py`): materializada e integrada a `E1`;
  - **linha 3** — resolver factual (`src/casa77_sdr/response_yaml_resolve.py`): materializada
    como **fronteira isolada**, **não integrada** a `E1`. `E1` não recebe raiz factual e não lê
    `knowledge/casa77.yaml`.
- Formato **`hora`**: regra mecânica **arbitrada** (`C-A1-F3a`), contagem de dígitos fechada
  (`C-A1-F3b`) e **`formatar_hora` materializado** em `src/casa77_sdr/response_format.py`,
  como **fronteira isolada**. **`C` continua NÃO materializada integralmente.**
- **`C-7`**: a **fronteira determinística de valor** está materializada **isoladamente** em
  `src/casa77_sdr/response_null_pending.py` — recebe terminal já resolvido e recusa `null` ou
  a estrutura canônica com `status: pendente`. Na **validação do corpus materializado**, os
  **114 *bindings* de origem YAML** são resolvidos e passam por `C-7`, e **nenhum** resolve para
  `null` nem para `status: pendente`. Isso **não cria consumidor operacional de runtime**:
  **não há integração end-to-end** de `C-7` no ciclo de atendimento. O contrato de `C-7` não foi
  reaberto.
- **Sintaxe física de *placeholder***: **arbitrada**, com a forma canônica **`{{nome}}`**, e a
  fronteira `src/casa77_sdr/response_placeholder.py` **materializada**. A **integração
  estrutural ao `E1` está materializada**: `E1` exige essa gramática para o **nome** de
  *binding* `RENDERIZADO` e exige **correspondência literal** entre `binding.placeholder` e o
  *placeholder* derivado do nome, sem manter gramática paralela. `ASSERTIVA` **não** recebe essa
  gramática. O Markdown aprovado **agora possui *templates* físicos em 19 fragmentos**; os
  outros **18 permanecem sem `RENDERIZADO`**. `decompor_template()` é **exercitado pelo teste de
  integração do corpus**, onde **`PH7` e `PH8` foram comprovadas sobre o corpus físico**.
  **Nenhum *renderer* de produção existe.**
- **`C-A1-ST6`–`C-A1-ST10`**, sobre o corpus materializado:
  - **`ST6`** — **comprovada**: o índice físico carrega e `E1` o valida estruturalmente;
  - **`ST7`** — **comprovada**: bijeção integral **37/37** entre índice e Markdown;
  - **`ST8`** — **comprovada**: status **37/37** resolvidos e coincidentes, por ocorrência
    física;
  - **`ST9`** — **comprovada no corpus materializado**, em dois regimes distintos: os **114
    *bindings* de origem `YAML`** foram **resolvidos e validados contra
    `knowledge/casa77.yaml`**, incluindo `C-7`, formatos e `ASSERTIVA` aplicáveis; os **4
    *bindings* `RUNTIME_AUTORITATIVO`** foram validados **apenas** quanto à representação
    estrutural, ao referente e ao predicado, **sem afirmar verdade operacional** — esta depende
    da consulta autoritativa do ciclo, fora do corpus versionado;
  - **`ST10`** — equivalência **`C-15`** verificada para os **19 *templates***; os **18
    fragmentos estáticos** são **N/A**. **A migração da autoridade de status NÃO foi
    realizada** e depende de entrega separada.

Existem fronteiras determinísticas já materializadas em torno de `C` — validador estrutural,
carregador *fail-closed*, comparador de equivalência, formatadores, avaliador de `ASSERTIVA`,
verificador de bijeção e canonicalizador de rótulo de status. **Nenhuma delas materializa `C`**:
todas recebem insumos prontos e nenhuma resolve *binding*, lê o índice ou consulta
`knowledge/**`. O catálogo dos módulos vive no código; o contrato vive em `docs/07` §2.3.

---

## 5. Pendências ativas

| Pendência | Situação atual | Impacto / bloqueio | Fonte |
|---|---|---|---|
| **B** — colisão conceitual de nome `RegistroAtendimento` | aberta; nenhum referente renomeado ou unificado | bloqueia implementar o componente `RegistroAtendimento` | `docs/07` §4.1.1, §12 item 21 |
| **C** — índice estruturado `Rxx` × YAML | índice físico e *templates* **materializados e validados**; **integração dos consumidores operacionais** e **eventual migração da autoridade de status** ainda pendentes | a **ausência física do índice deixou de ser o bloqueio**; `ValidadorConsistenciaBase`, `SeletorFatos`, `ValidadorResposta` e **S2-D8** continuam **não materializados**, e por isso o `OrquestradorMotor` e a integração completa **não** devem ser considerados prontos | `docs/07` §2.3, §12 itens 19 e 10 |
| **S2-D5** — mensagem conversacional em `aguardando_confirmacao_disponibilidade` antes de `E16` | aberta; resolver na Etapa 6 | não bloqueia | `docs/06` §12 |
| **S2-D7** — `E13` a partir de estado diferente de `encaminhado_humano` | aberta; resolver na Etapa 5 | não bloqueia | `docs/06` §12 |
| **S2-D8** — detecção e classificação de pendências e cobertura de resposta aprovada | contrato arbitrado / não materializado; nenhum módulo nem mapa `R2` | bloqueia o `OrquestradorMotor` e a integração completa | `docs/07` §4.4.1, §12 item 10; `docs/06` §11 |
| **S3-D1** — produtor da condição `motivo_encerramento` | produtor **não atribuído** | impede completar a **condição 8 de `CondicoesCiclo`** e os fluxos que dependem dela na integração completa | `docs/07` §4.4, §12 item 10 |
| **E1** — conversa × atendimento × lead | não arbitrada; atravessa identidade, persistência e registro de leads | não bloqueia a especificação vigente | `docs/07` §12 item 13 |
| **E3** — evento novo durante atendimento ativo | aberta; contrato vigente é conservador (`AMBIGUA`) | não bloqueia | `docs/07` §12 item 14 |
| **E4** — tratamento de `SEM_CANDIDATO_ELEGIVEL` | aberta; o ciclo encerra sem transição | bloqueia o `OrquestradorMotor` | `docs/07` §12 item 15 |
| **N-a** — integração operacional residual | especificação concluída e fronteiras `M-T`/`M-E`/`M-C`/`M-DT`/`M-AE` materializadas; integração da etapa 13 no pipeline pendente, com bloqueios S4/S5 sem tratamento operacional | bloqueia o pipeline completo | `docs/07` §6.2, §12 item 11 |
| **Limiar temporal de recência** | valor numérico e mecanismo de carga indefinidos; não é dado comercial | bloqueia a integração operacional de `N-a` e o `OrquestradorMotor` | `docs/07` §12 item 18 |
| **N-b** — produtor não determinístico / LLM, `N-b-RES2` e integração da etapa 4 | contrato arbitrado; fronteira determinística materializada; produtor real, interpretação de texto livre, `N-b-RES2` e integração pendentes | bloqueia o `OrquestradorMotor` e a integração completa | `docs/07` §6.3, §12 item 12 |
| **Unicidade geral de `id_atendimento`** | não decidida entre candidatos não identificados | não bloqueia o bloco corrente de materialização de `C` | `docs/07` §12 item 17 |
| **Retorno do controle ao bot** | não existe transição inversa de `T31` | não bloqueia | `docs/07` §12 item 16 |
| **Persistência operacional não volátil** | contrato arbitrado; implementação volátil não sustenta operação real; nenhuma tecnologia escolhida | bloqueia qualquer uso em canal real | `docs/07` §7.3, §7.4, §12 item 2a |
| **Destino do alerta operacional** | canal separado da conversa exigido por S5, Q5 e F4; destino não especificado | bloqueia o `OrquestradorMotor` | `docs/07` §12 item 3a |
| **Confirmação física de entrega do handoff** | `encaminhado_humano` afirma handoff registrado, nunca recebimento confirmado | não bloqueia; futura da Etapa 5 | `docs/06` §10; `docs/07` §12 item 5 |

Pendências comerciais e lacunas da base **não são replicadas aqui**:
`knowledge/informacoes-pendentes.md` é a fonte única.

---

## 6. Bloqueadores da integração completa

Bloqueiam o `OrquestradorMotor` e o pipeline completo:

- **S2-D8** — materialização do produtor de pendências e de cobertura;
- **C** — índice físico e *templates* **já materializados**; falta **conectar as capacidades
  dependentes** — `ValidadorConsistenciaBase`, `SeletorFatos` e `ValidadorResposta` —, das quais
  **S2-D8** também depende;
- **S3-D1** — produtor de `motivo_encerramento` ainda não atribuído; impede completar a
  **condição 8 de `CondicoesCiclo`** e os fluxos que dependem dela;
- **E4** — tratamento de `SEM_CANDIDATO_ELEGIVEL`;
- **N-b** — produtor não determinístico, `N-b-RES2` e integração da etapa 4;
- **N-a** — integração operacional da etapa 13, tratamento dos bloqueios S4/S5 e destino do
  alerta operacional;
- **limiar temporal** — valor e mecanismo de carga.

Bloqueia o **uso real** em canal, à parte da integração: **persistência operacional não
volátil**.

**Não são bloqueadores** — abertas, porém sem condicionar a integração vigente: **B**, **E1**,
**E3**, **S2-D5**, **S2-D7**, unicidade geral de `id_atendimento` e retorno do controle ao bot.

A `MaquinaEstados` **não depende** dessas pendências para o contrato já definido: recebe
eventos confirmados e condições já estruturadas.

---

## 7. Próxima ação

A **materialização física do índice e dos *templates* de `C`** está **concluída**. A próxima
microentrega funcional será eleita por **novo mandato do GPT**, após a integração desta entrega.

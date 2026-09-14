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
- O trabalho corrente está no **bloco de `C`**, composto por microentregas funcionais **sem
  numeração de subetapa**. **Não existe subetapa `3B.8`.** Estão **concluídos** a
  **materialização física do índice e dos *templates***, a **migração da autoridade de
  status**, o **primeiro *lookup* operacional de status**, o **`ValidadorConsistenciaBase`**,
  o **`SeletorFatos`**, o **compositor determinístico por fragmento**, o
  **`ProjetorEmissao`** — a fronteira que projeta os fragmentos destinados à emissão — e a
  **fronteira determinística de montagem canônica de uma emissão**. O bloco segue na
  **integração das capacidades dependentes ainda ausentes**. `C` **não** está integralmente
  operacional.
- Etapa 4 permanece **absorvida pela Etapa 3B**; etapas 5 a 10 permanecem futuras
  (`docs/05-roadmap.md`).

---

## 2. Última entrega funcional relevante

Commit funcional `9e9b62b0016dddcb5bc2d72a633dc5484554f37f`.

**Montagem canônica de uma emissão materializada** em
`src/casa77_sdr/response_assembly.py`, com a API pública `montar_resposta_final`, o DTO
`RespostaMontada` e a exceção própria `MontagemRespostaNaoAvaliavel`. A **entrada é única**: o
`ResultadoComposicao` já produzido pelo compositor por fragmento.

Ela monta **uma emissão, nunca o ciclo**. A **ordem** e a **cardinalidade** das unidades são
preservadas **exatamente**, e `RespostaMontada.tokens` preserva os `token` dos
`TextoEmitivel`, na mesma ordem — nenhum acrescentado, removido, reordenado ou deduplicado.
Com **uma** unidade, o texto final é **literalmente** o dela; com **várias**, elas são
separadas por **exatamente `"\n\n"`**, com **zero conteúdo lexical novo** entre elas.

**Zero normalização**: espaço inicial ou final, quebra de linha já presente, pontuação e algo
parecido com `{{nome}}` permanecem **literais**. **Cardinalidade zero fecha** e **token
duplicado fecha**, *fail-closed* e **sem resultado parcial**. O campo `texto` fica **fora do
`repr`**; os tokens, sendo identificadores estruturais, podem aparecer.

**Zero YAML**, **zero índice**, **zero LLM**, **zero I/O**, **zero decisão comercial** e
**zero decisão de fase, destino, evento ou estado**. A fronteira é **isolada**: montar uma
emissão **não** é integrar o ciclo, e a **etapa 10 *end-to-end* não está pronta**.

Permanecem fatos vigentes: **30 `Rxx`**, **37 fragmentos emitíveis**, **118 *bindings***,
**19 *templates*** e **18 fragmentos estáticos**. **Zero texto/*template* emitível
alterado** e **zero mudança semântica do índice**.

---

## 3. Baseline funcional

**Baseline funcional da nova entrega** — evidência da entrega funcional acima, **não** uma
execução desta atualização:

- Python **3.14.5**;
- **`6177 passed`**, sob **`-W error`**;
- zero failures, zero errors, zero warnings.

CI configurada em GitHub Actions, em `.github/workflows/ci.yml`, com Python **3.13** e **3.14**.
Resultados de execução são evidência do GitHub e não são acumulados neste snapshot.

---

## 4. Estado essencial da capacidade corrente — `C`

- **Contrato de `C`: ARBITRADO** (`docs/07` §2.3; registrado em `docs/07` §12, item 19).
- **A materialização física do índice e dos *templates* do corpus está concluída.** **Dois
  consumidores operacionais** e as **fronteiras determinísticas de projeção, composição e
  montagem canônica** já existem; a integração das **capacidades restantes** permanece
  **separada e pendente**.
- **Cadeia vigente**, com as fronteiras separadas e nenhuma acumulando papel de outra:
  - `ValidadorConsistenciaBase` → **consistência** — **materializado**;
  - **S2-D8** / `R2` → **candidatura, emissibilidade, cobertura e escolha do *witness***, que
    projeta os fragmentos autorizados — **contrato arbitrado, implementação física ainda
    ausente**;
  - `MaquinaEstados` → **ações semânticas** — **materializada**;
  - **`ProjetorEmissao`** → ***witnesses*** **e ações** → **tokens destinados à emissão** —
    **materializado**;
  - `SeletorFatos` → **fatos e textos autorizados**, separados — **materializado**;
  - **compositor determinístico** → **texto emitível por fragmento** — **materializado**;
  - **montagem canônica de uma emissão** → **`RespostaMontada`** — **materializada**;
  - `ValidadorResposta` → validação final da saída — **ainda não materializado**.
- O índice físico `knowledge/indice-respostas-aprovadas.yaml` está **materializado e
  estruturalmente validado**: **30 `Rxx`**, **37 fragmentos**, **118 *bindings***. Ele guarda
  **referentes**, nunca valor resolvido (`C-1h`–`C-1m`, `C-15e`).
- A **autoridade canônica de status por fragmento MIGROU** para
  `knowledge/indice-respostas-aprovadas.yaml`, conforme `C-11`, após
  `C-A1-ST6`–`C-A1-ST10` comprovadas. Os rótulos de cabeçalho `Rxx` e `status-fragmento`
  **permanecem fisicamente** em `knowledge/respostas-aprovadas.md` **somente para leitura
  humana e reconciliação**: não sobrescrevem o índice.
- **Status não equivale a emissibilidade.** `APROVADO` é condição **necessária, não
  suficiente**: **seleção**, **candidatura** e **cobertura** permanecem **fora da autoridade
  de status de `C`** (`C-12`; `S2-D8`).
- Existe **lookup operacional de status** sobre o índice canônico
  (`src/casa77_sdr/response_index_status.py`): ele valida o índice e deriva a identidade
  **antes** de ler, **sem vocabulário paralelo**, **sem valor padrão**, **sem *fallback*** e
  **sem consultar o Markdown**.
- Existe **primeiro consumidor operacional de `C`**: o `ValidadorConsistenciaBase`
  (`src/casa77_sdr/response_consistency.py`; contrato em `docs/07` §4.1.2). Ele:
  - **valida todos os fragmentos do índice físico, sem filtrar por status** — o status é
    projetado como informação **separada**;
  - **reutiliza** as fronteiras existentes de caminho, contexto, resolução, `C-7`, formato e
    `ASSERTIVA`, **sem criar *parser*, resolver, formatador ou gramática paralela**;
  - **não renderiza texto** e **não repete `C-15` em runtime**;
  - **não decide emissibilidade nem cobertura** — o consumo pertence a **S2-D8** (`C-12`);
  - **não avalia a verdade** de *bindings* `RUNTIME_AUTORITATIVO`, apenas os registra.
- Em fragmento que declara `itera_sobre`, a cardinalidade da avaliação vem do **caminho**:
  *binding* **absoluto** é avaliado **uma vez contra a raiz**, mesmo com coleção vazia;
  *binding* **relativo** é avaliado **por item corrente**.
- Existe **segundo consumidor operacional de `C`**: o `SeletorFatos`
  (`src/casa77_sdr/fact_selection.py`; contrato em `docs/07` §4.1.3). Ele:
  - é **puro e determinístico**, e recebe a entrada **já autorizada a montante**;
  - **não consulta status** e **não reavalia consistência**;
  - **não conhece `PerguntaComercial`, `AssuntoComercial` nem `R2`**;
  - **materializa somente `RENDERIZADO`**, aplicando `C-7` e o formatador declarado;
  - devolve fato comercial **apenas como `valor_formatado`**, com proveniência — e
    `valor_formatado` e texto ficam **fora do `repr`**;
  - mantém o **fragmento estático representável**: zero fatos e **um** texto autorizado;
  - **não materializa `ASSERTIVA` nem fato runtime**;
  - **não renderiza *template* algum**.
- A regra de escolha determinística do ***witness*** está **arbitrada** — a **primeira
  alternativa emitível na ordem declarada do grupo** (`docs/07` §4.4.1, `SF-D4`). Mas
  **S2-D8 continua não materializada**, o **`R2` físico continua inexistente** e a **projeção
  real dos fragmentos autorizados ainda não está integrada**: a seleção *end-to-end* **não**
  funciona.
- Existe **fronteira determinística operacional de composição por fragmento**
  (`src/casa77_sdr/response_composition.py`; contrato em `docs/07` §4.1.4). Ela **não é um
  15º componente**: §4.1 permanece com **14**. Ela:
  - recebe **somente** o `ResultadoSelecaoFatos` e devolve **um texto emitível por
    fragmento**, na mesma ordem;
  - delega a gramática do *template* a `decompor_template`, **sem gramática paralela**;
  - preserva o fragmento **estático literalmente** e a **proveniência** dos valores inseridos;
  - **não reinterpreta** o valor inserido como *template*;
  - **não consulta** YAML, índice, status ou estado, e **não chama LLM**;
  - **não monta a resposta final**: zero concatenação, ordem alternativa, omissão ou
    separador entre fragmentos.
- **Limitação explícita da versão atual do compositor**: ele exige cardinalidade **exatamente
  1** por `(token, binding)` — **zero** é recusado pela gramática do *template* e **mais de
  um** fecha como erro de contrato. O corpus físico atual tem **0 fragmentos com
  `itera_sobre`**, comprovado **mecanicamente** sobre o índice carregado. Isso **não** proíbe
  `itera_sobre` na arquitetura: introduzi-lo no futuro exige **nova arbitragem** da
  apresentação dos múltiplos valores.
- Existe **fronteira determinística operacional de projeção de emissão**
  (`src/casa77_sdr/emission_projection.py`; contrato em `docs/07` §4.1.5). Ela **não é um
  15º componente**: §4.1 permanece com **14**. É a **fronteira determinística operacional**
  que liga as ações já decididas pela máquina à materialização textual. Ela:
  - recebe **`fragmentos_autorizados`** e as **ações da primeira decisão da
    `MaquinaEstados`**, e devolve **`tuple[str, ...]`**;
  - **preserva integralmente a ordem dos *witnesses*** e acrescenta os **mandatórios depois
    deles**, na ordem das ações;
  - **deduplica somente no bloco mandatório**, pela primeira ocorrência;
  - **fecha** diante de repetição na tupla recebida e de **conflito *cross-source***;
  - **não abre** `knowledge/**`, **não carrega o índice em produção**, **não chama LLM**,
    **não monta texto**, **não toma decisão comercial** e **não executa ação alguma**.
- **Ações sem mapeamento.** A **maioria das `AcaoMaquina` ainda não possui fragmento aprovado
  materializado nesta fronteira**: nesta versão, **somente `INFORMAR_LACUNA_DE_INFORMACAO`
  possui contribuição textual mandatória materializada**. Para as demais, **`()` significa
  zero fragmento acrescentado pelo `ProjetorEmissao`** — e **não** que a ação esteja
  resolvida: a **obrigação conversacional permanece**.
- **`R03/F1`** é o **único fragmento mandatório atualmente materializado** pelo projetor. Um
  ***gate* mecânico do corpus** comprova a sua **existência**, o status **`APROVADO`** e os
  **zero *bindings***. Ele **não é reavaliado por S2-D8 nesta fronteira**, **não pertence a
  `R2`** e **não torna a `MaquinaEstados` conhecedora de `Rxx`**.
- **Limites materiais do projetor nesta versão**: ele consome as ações da **primeira** decisão
  da máquina; **ações produzidas por chamadas posteriores da `MaquinaEstados` não entram nesta
  projeção**; somente **fragmentos mandatórios estáticos e previamente aprovados por *gate* de
  corpus** podem ser inseridos pelo mapa atual; qualquer futuro mandatório com ***binding***,
  **`ASSERTIVA`** ou **fato de runtime** **exige nova arbitragem**; e ação com mapa vazio
  **continua podendo ter obrigação textual pendente**.
- **Política geral de composição — `PC-1`–`PC-6`** — é agora **norma arquitetural** em
  `docs/07` §4.1.5: **múltiplos fragmentos individualmente aprovados podem compor a mesma
  resposta**; os ***witnesses*** **preservam ordem e cardinalidade**; em **cobertura mista**,
  **`R03/F1` entra ao final**; o **separador `"\n\n"`** está **arbitrado por `PC-3`** e
  **fisicamente materializado** em `src/casa77_sdr/response_assembly.py`, **somente entre
  unidades**; há **zero conteúdo lexical novo** entre elas; e o **LLM não altera lexicalmente
  o corpo comercial já composto de fragmentos aprovados**. **Montagem canônica isolada não
  equivale a integração *end-to-end*.**
- Existe **fronteira determinística operacional de montagem canônica de uma emissão**
  (`src/casa77_sdr/response_assembly.py`; contrato em `docs/07` §4.1.6). Ela **não é um
  15º componente**: §4.1 permanece com **14**, e **nenhuma etapa nova é criada**. Ela:
  - recebe **somente** o `ResultadoComposicao`, em **tipo exato**, e devolve
    **`RespostaMontada`**;
  - **preserva ordem e cardinalidade** e **não filtra, escolhe, ordena, omite nem repete**;
  - aplica **exatamente `"\n\n"`** entre unidades adjacentes — **nunca** nas pontas;
  - **não reinterpreta** o conteúdo recebido e **não normaliza** nada;
  - **fecha** em cardinalidade zero e em token duplicado, **sem resultado parcial**;
  - **não abre** `knowledge/**`, **não lê o YAML nem o índice**, **não chama LLM** e **não
    faz I/O**.
- **Limites materiais da montagem nesta versão**: ela monta **uma emissão**; **não conhece**
  fase, destino, ação, evento ou estado; **não conhece `E15` nem `E12`**; **não representa
  `SEM_EMISSAO`** — silêncio legítimo significa que ela **não é chamada**, e isso pertence ao
  orquestrador futuro; **não substitui o `ValidadorResposta`**; e **não torna o pipeline
  operacional**.
- **Vocabulário canônico de status fechado**: `APROVADO`, `AGUARDA_APROVACAO`, `BLOQUEADO`.
  **`PARCIAL` não é quarto status** — é rótulo humano agregado do Markdown; no índice,
  `R28/F1` é **`APROVADO`**, provado diretamente na autoridade.
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
  `null` nem para `status: pendente`. `C-7` é agora **composto** pelo
  `ValidadorConsistenciaBase`, que o reporta como **referente indisponível** e **nunca** como
  divergência; **não há integração end-to-end** de `C-7` no ciclo de atendimento. O contrato
  de `C-7` não foi reaberto.
- **Sintaxe física de *placeholder***: **arbitrada**, com a forma canônica **`{{nome}}`**, e a
  fronteira `src/casa77_sdr/response_placeholder.py` **materializada**. A **integração
  estrutural ao `E1` está materializada**: `E1` exige essa gramática para o **nome** de
  *binding* `RENDERIZADO` e exige **correspondência literal** entre `binding.placeholder` e o
  *placeholder* derivado do nome, sem manter gramática paralela. `ASSERTIVA` **não** recebe essa
  gramática. O Markdown aprovado **agora possui *templates* físicos em 19 fragmentos**; os
  outros **18 permanecem sem `RENDERIZADO`**. `decompor_template()` é **exercitado pelo teste de
  integração do corpus**, onde **`PH7` e `PH8` foram comprovadas sobre o corpus físico**.
  **A composição determinística por fragmento existe** (`docs/07` §4.1.4) e a **montagem
  canônica de uma emissão também** (`docs/07` §4.1.6): um *template* com *placeholder* já é
  materializável em texto emitível, e as unidades já são materializáveis numa **única
  mensagem**, com o separador aplicado fisicamente. O que **continua ausente** é o
  **fechamento do caminho final** — a **forma canônica completa do rascunho do ciclo**, o
  **papel residual do LLM** nas superfícies ainda sem fragmento aprovado, o
  `ValidadorResposta` e a **integração *end-to-end*** —, e é dele que depende um caminho
  degradado completo (`docs/07` §12, item 22).
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
    fragmentos estáticos** são **N/A**.

Em torno de `C` existem também fronteiras determinísticas **isoladas** — validador
estrutural, carregador *fail-closed*, comparador de equivalência, formatadores, avaliador de
`ASSERTIVA`, verificador de bijeção e canonicalizador de rótulo de status. Elas recebem
insumos prontos, **não resolvem *binding***, **não leem o índice** e **não consultam
`knowledge/**`**; quem as **compõe** são os **dois consumidores operacionais** —
`ValidadorConsistenciaBase` e `SeletorFatos` —, sempre sobre insumos **já carregados pelo
chamador**; o **`ProjetorEmissao`** entrega a esse segundo consumidor os fragmentos destinados
à emissão, o **compositor determinístico** materializa o texto de cada fragmento e a
**montagem canônica** fecha a cadeia numa **única emissão**.
**Nenhuma delas, nem eles, materializa `C` integralmente.** O catálogo dos módulos vive no
código; o contrato vive em `docs/07` §2.3.

---

## 5. Pendências ativas

| Pendência | Situação atual | Impacto / bloqueio | Fonte |
|---|---|---|---|
| **B** — colisão conceitual de nome `RegistroAtendimento` | aberta; nenhum referente renomeado ou unificado | bloqueia implementar o componente `RegistroAtendimento` | `docs/07` §4.1.1, §12 item 21 |
| **C** — índice estruturado `Rxx` × YAML | **materializados**: índice físico e *templates*, **autoridade de status**, ***lookup* operacional**, **`ValidadorConsistenciaBase`**, **`ProjetorEmissao`**, **`SeletorFatos`**, **compositor determinístico por fragmento** e a **montagem canônica de uma emissão**. **Pendentes**: **S2-D8 / `R2` físico**, **`ValidadorResposta`**, **integração *end-to-end* da etapa 10**, **superfícies conversacionais sem unidade aprovada**, as **ações produzidas por chamadas posteriores da `MaquinaEstados`**, a **evolução futura do `ProjetorEmissao`** para essas fases e a **integração pelo `OrquestradorMotor`** | a **ausência física do índice deixou de ser o bloqueio** e a cadeia já vai do índice à **emissão montada numa única mensagem**; enquanto as capacidades restantes não forem materializadas, o `OrquestradorMotor` e a integração completa **não** devem ser considerados prontos. **`C` não está concluída** | `docs/07` §2.3, §4.1.2, §4.1.3, §4.1.4, §4.1.5, §4.1.6, §12 itens 19, 10 e 22 |
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
- **C** — índice físico, *templates*, **autoridade de status**, ***lookup* operacional**,
  **`ValidadorConsistenciaBase`**, o **`ProjetorEmissao`**, o **`SeletorFatos`**, o
  **compositor determinístico por fragmento** e a **montagem canônica de uma emissão** **já
  concluídos** — a **ausência da montagem canônica isolada deixou de ser lacuna**. O bloqueio
  restante é **conectar as capacidades dependentes ainda ausentes** — a **projeção física de
  S2-D8 / `R2`**, que é quem produz os fragmentos autorizados, o **`ValidadorResposta`**, as
  **superfícies textuais sem unidade aprovada**, a **integração residual da etapa 10**, as
  **ações produzidas por chamadas posteriores da `MaquinaEstados`** e a **integração completa
  pelo `OrquestradorMotor`** (`docs/07` §12, item 22);
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

**Materializar o `ValidadorResposta` sobre a montagem canônica, com validação determinística
por igualdade exata entre o texto candidato e `RespostaMontada.texto`, preservando o princípio
`P4` e sem integrar ainda o ciclo completo.**

O contrato técnico **já está arbitrado**: aprovado **se e somente se** o texto candidato for
**literalmente igual** ao texto montado. Por isso a próxima ação é **implementação**, não
arbitragem. Ela permanece **isolada**: **não** integra a etapa 10 *end-to-end*, **não**
resolve as **superfícies conversacionais sem unidade aprovada**, **não** trata as **ações
produzidas por chamadas posteriores da `MaquinaEstados`** e **não** liga o
`OrquestradorMotor` — tudo isso continua pendente. Esta decisão **não é tomada aqui** — este
arquivo é snapshot — e a entrega será aberta por **novo mandato específico**.

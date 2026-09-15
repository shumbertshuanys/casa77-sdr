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
  **`ProjetorEmissao`** — a fronteira que projeta os fragmentos destinados à emissão —, a
  **fronteira determinística de montagem canônica de uma emissão** e o
  **`ValidadorResposta`** — o *gate* final de integridade textual sobre a emissão já montada.
  O bloco segue na **integração das capacidades dependentes ainda ausentes**. `C` **não**
  está integralmente operacional.
- **Fora de `C`**, a **infraestrutura estrutural do mapa de cobertura `R2`** —
  esqueleto fechado, **totalidade** do vocabulário, validação estrutural, carregamento
  estrito e conferência de identidade — está **materializada** (`docs/07` §4.4.2). O
  **conteúdo do mapa NÃO existe**, **nenhuma associação `AssuntoComercial → Rxx/Fxx` foi
  estabelecida** e o **produtor S2-D8 NÃO existe**: `R2` **não está completo** e a
  **cobertura não funciona**.
- Etapa 4 permanece **absorvida pela Etapa 3B**; etapas 5 a 10 permanecem futuras
  (`docs/05-roadmap.md`).

---

## 2. Última entrega funcional relevante

Commit funcional `6237f04a1685406faccd7150261ab2b25f1f9eaa`.

**Infraestrutura estrutural do mapa de cobertura `R2` materializada**, em
`src/casa77_sdr/coverage_map.py` e `src/casa77_sdr/coverage_map_load.py`, com o contrato vivo
em `docs/07` §4.4.2 (`R2F-1`–`R2F-15`). Ela é **estrutura**, nunca conteúdo.

O **esqueleto é fechado** em todos os níveis: raiz só `assuntos`; item só `assunto` e
`grupos`; grupo só `alternativas`; alternativa só `rxx` e `fragmento`. Logo `priority`,
texto, status, *binding*, `caminho_yaml`, `predicado`, `formato` e valor comercial **não são
representáveis**: a alternativa é **referência exclusivamente estrutural `Rxx` + fragmento**.

`R2-1` é materializado como **mapeamento TOTAL**: os **54 `AssuntoComercial`** aparecem,
cada um **exatamente uma vez** — ausência e repetição **fecham**. Cada assunto declara
**0..N grupos**, com a lista vazia válida e **explícita**; cada grupo declara **1..N
alternativas**, e a lista vazia fecha. **`ASSUNTO_NAO_CLASSIFICADO` está presente com zero
grupos**, e **`R03/F1` não pode ser alternativa**. A **ordem física declarada** é preservada
integralmente, sem ordenação, preferência ou deduplicação.

O **carregador é estrito**: UTF-8, YAML seguro, chave repetida recusada, caminho sempre
explícito, sem caminho padrão ou descoberta; `MapaCoberturaIlegivel` separa o ilegível do
inválido, e `MapaCoberturaInvalido` **propaga intacta**. A **conferência de referências**
confere existência **contra o domínio canônico de identidade** do índice, e **somente isso**:
referência pendurada **fecha**; defeito do índice **fora da projeção de identidade não é
julgado ali**, e a validação integral que `D8-CI2` exige permanece com `validar_indice`, na
cadeia futura.

**Nada de conteúdo foi criado.** `knowledge/mapa-cobertura.yaml` **não existe** e **nenhuma
associação `AssuntoComercial → grupos → Rxx/Fxx`** foi estabelecida — ela depende de
**decisão humana futura**. **Não** foram materializados: cobertura comercial, candidatura,
emissibilidade **`D8-F`**, escolha de *witness*, `fragmentos_autorizados`, **eixo A**, **eixo
B**, **`E09`**, o **produtor S2-D8**, a **integração *end-to-end*** e o
**`OrquestradorMotor`**. **`R2` não está completo** e **S2-D8 não está materializada**.

Permanecem fatos vigentes: **30 `Rxx`**, **37 fragmentos emitíveis**, **118 *bindings***,
**19 *templates*** e **18 fragmentos estáticos**. **Zero alteração** em `knowledge/**`, em
prompt, em dado comercial e em módulo existente de `src/`.

---

## 3. Baseline funcional

**Baseline funcional da nova entrega** — evidência da entrega funcional acima, **não** uma
execução desta atualização:

- Python **3.14.5**;
- **`6603 passed`**, sob **`-W error`**;
- zero failures, zero errors, zero warnings.

CI configurada em GitHub Actions, em `.github/workflows/ci.yml`, com Python **3.13** e **3.14**.
Resultados de execução são evidência do GitHub e não são acumulados neste snapshot.

---

## 4. Estado essencial da capacidade corrente — `C`

- **Contrato de `C`: ARBITRADO** (`docs/07` §2.3; registrado em `docs/07` §12, item 19).
- **A materialização física do índice e dos *templates* do corpus está concluída.** **Dois
  consumidores operacionais** e as **fronteiras determinísticas de projeção, composição,
  montagem canônica e validação final** já existem; a integração das **capacidades
  restantes** permanece **separada e pendente**.
- **Cadeia vigente**, com as fronteiras separadas e nenhuma acumulando papel de outra:
  - `ValidadorConsistenciaBase` → **consistência** — **materializado**;
  - **S2-D8** / `R2` → **candidatura, emissibilidade, cobertura e escolha do *witness***, que
    projeta os fragmentos autorizados — **contrato arbitrado**; a **representação estrutural
    física de `R2`** existe (`docs/07` §4.4.2), mas o **conteúdo do mapa** e o **produtor**
    continuam **ausentes**;
  - `MaquinaEstados` → **ações semânticas** — **materializada**;
  - **`ProjetorEmissao`** → ***witnesses*** **e ações** → **tokens destinados à emissão** —
    **materializado**;
  - `SeletorFatos` → **fatos e textos autorizados**, separados — **materializado**;
  - **compositor determinístico** → **texto emitível por fragmento** — **materializado**;
  - **montagem canônica de uma emissão** → **`RespostaMontada`** — **materializada**;
  - **`ValidadorResposta`** → **validação final da saída** — **materializado**.
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
  **S2-D8 continua não materializada**, o artefato **`knowledge/mapa-cobertura.yaml` com
  conteúdo aprovado continua inexistente** e a **projeção real dos fragmentos autorizados
  ainda não está integrada**: a seleção *end-to-end* **não** funciona. A **infraestrutura
  estrutural de `R2`** — esqueleto, totalidade, validação, carregamento e conferência de
  identidade — **já existe** (`docs/07` §4.4.2) e **não é o que falta**.
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
- Existe **fronteira determinística operacional de validação final da emissão**
  (`src/casa77_sdr/response_validation.py`; contrato em `docs/07` §4.1.7). Ela **não é um
  15º componente**: §4.1 permanece com **14**, e **nenhuma etapa nova é criada**. Ela:
  - recebe **somente** o **texto candidato** e a **`RespostaMontada`**, em **tipo exato**, e
    devolve **`ResultadoValidacaoResposta`**;
  - aprova **se e somente se** `texto_candidato == montada.texto`, **literalmente** —
    `APROVADO` ou `TEXTO_DIVERGENTE`, vocabulário **fechado** em dois motivos;
  - **não normaliza** nada e **não corrige, cria, substitui nem sugere** texto;
  - **fecha** diante de entrada estruturalmente inválida, **sem resultado parcial**,
    inclusive quando `montada.texto` não é `str` exata — sem essa guarda, a comparação seria
    **refletida** e o outro operando poderia **forçar a aprovação**;
  - **não vaza texto** em DTO, exceção ou `repr`;
  - **não revalida fato comercial** e **não reabre seleção**: a autoridade textual chega
    **transitivamente**, já incorporada na `RespostaMontada`;
  - **não abre** `knowledge/**`, **não lê o YAML nem o índice**, **não consulta status**,
    **não chama LLM** e **não faz I/O**.
- **Limites materiais da validação nesta versão**: ela valida **uma saída já montada** e
  **não integra o ciclo**; **não conhece** fase, destino, ação, evento ou estado; **não
  decide `E15` nem `E12`**; **não representa `SEM_EMISSAO`**; **não resolve** as superfícies
  conversacionais sem fragmento aprovado; e **não torna o pipeline operacional**. O desfecho
  diante de `TEXTO_DIVERGENTE` pertence à **etapa 12**, **fora desta fronteira**.
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
  **papel residual do LLM** nas superfícies ainda sem fragmento aprovado e a **integração
  *end-to-end*** —, e é dele que depende um caminho degradado completo (`docs/07` §12,
  item 22). O ***gate* final de integridade textual** já existe (`docs/07` §4.1.7), mas
  **validar não é integrar**.
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
à emissão, o **compositor determinístico** materializa o texto de cada fragmento, a
**montagem canônica** fecha a cadeia numa **única emissão** e o **`ValidadorResposta`** prova
que o texto candidato **é** essa emissão.
**Nenhuma delas, nem eles, materializa `C` integralmente.** O catálogo dos módulos vive no
código; o contrato vive em `docs/07` §2.3.

---

## 5. Pendências ativas

| Pendência | Situação atual | Impacto / bloqueio | Fonte |
|---|---|---|---|
| **B** — colisão conceitual de nome `RegistroAtendimento` | aberta; nenhum referente renomeado ou unificado | bloqueia implementar o componente `RegistroAtendimento` | `docs/07` §4.1.1, §12 item 21 |
| **C** — índice estruturado `Rxx` × YAML | **materializados**: índice físico e *templates*, **autoridade de status**, ***lookup* operacional**, **`ValidadorConsistenciaBase`**, **`ProjetorEmissao`**, **`SeletorFatos`**, **compositor determinístico por fragmento**, a **montagem canônica de uma emissão** e o **`ValidadorResposta`**. **Pendentes**: o **produtor determinístico S2-D8** e o **artefato `knowledge/mapa-cobertura.yaml` com conteúdo aprovado** — a **infraestrutura estrutural de `R2`** já está materializada (`docs/07` §4.4.2; ver a linha própria de **S2-D8**) —, **integração *end-to-end* da etapa 10**, **superfícies conversacionais sem unidade aprovada**, as **ações produzidas por chamadas posteriores da `MaquinaEstados`**, a **evolução futura do `ProjetorEmissao`** para essas fases e a **integração pelo `OrquestradorMotor`** | a **ausência física do índice deixou de ser o bloqueio** e a cadeia já vai do índice à **emissão montada numa única mensagem**; enquanto as capacidades restantes não forem materializadas, o `OrquestradorMotor` e a integração completa **não** devem ser considerados prontos. **`C` não está concluída** | `docs/07` §2.3, §4.1.2, §4.1.3, §4.1.4, §4.1.5, §4.1.6, §4.1.7, §12 itens 19, 10 e 22 |
| **S2-D5** — mensagem conversacional em `aguardando_confirmacao_disponibilidade` antes de `E16` | aberta; resolver na Etapa 6 | não bloqueia | `docs/06` §12 |
| **S2-D7** — `E13` a partir de estado diferente de `encaminhado_humano` | aberta; resolver na Etapa 5 | não bloqueia | `docs/06` §12 |
| **S2-D8** — detecção e classificação de pendências e cobertura de resposta aprovada | contrato arbitrado. **Materializado**: a **infraestrutura estrutural de `R2`** — esqueleto fechado, **totalidade** dos 54 assuntos, carregador YAML estrito e **conferência contra o domínio canônico de identidade** (`src/casa77_sdr/coverage_map.py`, `src/casa77_sdr/coverage_map_load.py`; `docs/07` §4.4.2). **Ainda ausentes**: o **artefato físico com conteúdo aprovado** — `knowledge/mapa-cobertura.yaml` é **caminho reservado** e **não existe** —, o **conteúdo humano de cobertura**, o **produtor determinístico S2-D8** e a **execução de cobertura e de *witnesses*** | bloqueia o `OrquestradorMotor` e a integração completa | `docs/07` §4.4.1, §4.4.2, §12 item 10; `docs/06` §11 |
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

- **S2-D8** — **produtor** de pendências e de cobertura ainda **não materializado**. A
  **representação estrutural de `R2`** já existe (`docs/07` §4.4.2), mas o **conteúdo do
  mapa** e o **produtor** continuam ausentes, e **a cobertura não funciona**;
- **C** — índice físico, *templates*, **autoridade de status**, ***lookup* operacional**,
  **`ValidadorConsistenciaBase`**, o **`ProjetorEmissao`**, o **`SeletorFatos`**, o
  **compositor determinístico por fragmento**, a **montagem canônica de uma emissão** e o
  **`ValidadorResposta`** **já concluídos** — a **ausência do *gate* final de integridade
  textual deixou de ser lacuna**. O bloqueio restante é **conectar as capacidades dependentes
  ainda ausentes** — o **produtor S2-D8** e o **artefato `R2` com conteúdo aprovado**,
  necessários para produzir os fragmentos autorizados, as **superfícies textuais sem unidade
  aprovada**, a **integração residual da etapa 10**, as **ações produzidas por chamadas
  posteriores da `MaquinaEstados`** e a **integração completa pelo `OrquestradorMotor`**
  (`docs/07` §12, item 22);
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

**Materializar o produtor determinístico de S2-D8 sobre uma estrutura `R2` já carregada —
eixos A e B, `D8-F`, cobertura e projeção dos *witnesses*, conforme `docs/07` §4.4.1 —, sem
criar o conteúdo comercial real de `knowledge/mapa-cobertura.yaml` e sem integrar o ciclo
completo.**

A **infraestrutura estrutural de `R2`** já existe (`docs/07` §4.4.2): esqueleto, totalidade,
carregamento e conferência de identidade. Falta o **produtor**: a regra impeditiva
`IMP-1`–`IMP-4` do **eixo A**, a avaliação de cobertura do **eixo B** sobre `R2-4` e `R2-5`,
a emissibilidade **`D8-F1`**–**`D8-F6`**, a escolha do *witness* por `SF-D4-3` e a projeção
de `fragmentos_autorizados` por `SF-D4-9`/`SF-D4-10`.

Ele permanece **isolado**: **não** cria conteúdo de mapa, **não** integra a etapa 10
*end-to-end* e **não** liga o `OrquestradorMotor`. A **decisão humana sobre o conteúdo real
de `R2` continua pendente** e **não deve ser inventada** nessa entrega — sem ela, a cobertura
continua **sem funcionar** mesmo depois do produtor existir. Esta decisão **não é tomada
aqui** — este arquivo é snapshot — e a entrega será aberta por **novo mandato específico**.

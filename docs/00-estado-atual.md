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
- **Fora de `C`**, o **mapa de cobertura `R2`** está **completo**: a infraestrutura
  estrutural (`docs/07` §4.4.2), o **produtor determinístico de S2-D8** (§4.4.3), a
  **aplicabilidade determinística de pacote** (§4.4.4) e o **artefato físico**
  `knowledge/mapa-cobertura.yaml`, com a **associação total dos 54 `AssuntoComercial`** —
  **33** com cobertura declarada e **21** com `grupos: []`. Dadas as entradas estruturadas,
  S2-D8 **opera sobre o mapa real**. Mas a **cobertura não está integrada *end-to-end***:
  o **`OrquestradorMotor` permanece ausente**.
- **Fora de `C`**, o **produtor não determinístico de `N-b`** está **materializado
  e versionado**: a fronteira agnóstica de provedor
  (`src/casa77_sdr/interpretation_llm.py`), o adaptador **Anthropic**
  (`src/casa77_sdr/interpretation_anthropic.py`) e o *prompt* especializado
  (`prompts/prompt-interpretacao.md`), com o contrato vivo em `docs/07` §6.3
  (`M-PN1`–`M-PN12`). Texto livre passa por **saída estruturada** e **canonicalização
  obrigatória**, terminando em `Interpretacao`. A **materialização em runtime** da
  coordenação da etapa 4 no ciclo **continua pendente**.
- **Fora de `C`**, a **fronteira operacional da cadeia N-b** está **materializada
  e versionada na `main`**, em
  `src/casa77_sdr/interpretation_stage.py`, com o contrato vivo em `docs/07` §6.3
  (`EN4-1`–`EN4-12`). Ela **encadeia fisicamente** a produção da `Interpretacao` e as
  **três** derivações que já existiam — **projeção para a identidade**, **condição 5** e
  **`N-b-RES2`** —, devolvendo `ArtefatosInterpretacao`. **Cada invocação executa
  `interpretar_mensagem(...)` exatamente uma vez**, sem laço, retry, *fallback*, cache ou
  fila, e **a mesma instância** de `Interpretacao` atravessa as três derivações. A
  **unicidade por ciclo** continua sendo obrigação do `OrquestradorMotor` futuro, que
  deverá invocá-la **no máximo uma vez por ciclo de nova mensagem**. **Sem
  `Interpretacao`** a falha **propaga intacta**, **nenhuma derivação executa** e **nenhum
  DTO é construído**: a etapa 5 não executa e o ciclo **não alcança** as etapas 6 e 7. Ela
  **não é** componente novo — §4.1 permanece com **14** —, **não é** etapa nova e **não
  redefine a etapa 4**, que **continua não emitindo `Exx`**.
- **Fora de `C`**, a **coordenação de N-b por ciclo** está **ARBITRADA e VERSIONADA nesta
  entrega**, com o contrato vivo em `docs/07` §6.3 (`CN4-1`–`CN4-12`). Ela fixa o **ponto
  único** de chamada de `executar_interpretacao_do_ciclo(...)` por ciclo de **nova
  mensagem**; o **mecanismo estrutural** de unicidade — um ponto de chamada, **uma
  variável local** com o `ArtefatosInterpretacao` e **reutilização** dele, **sem** *flag*,
  *cache*, estado persistido, *retry*, fila, *lock*, DTO novo ou segunda interpretação —; o **mapa de
  consumidores**, com **identidade de objeto** da `Interpretacao` preservada; a **ordem
  parcial** obrigatória entre os produtores, que **não** converte produtores independentes
  em precedência semântica — em especial o **`DetectorHandoff`**, cuja posição relativa
  **não é fixada** —; as **pré-condições** da primeira decisão, com `None`, `False` e `()`
  **distintos**; e a **propagação intacta** da falha da interpretação, que bloqueia o
  caminho normal **antes da etapa 5**. É **norma do `OrquestradorMotor` futuro**: **zero
  código de produção**, `interpretation_stage.py` **inalterado**, e **nenhum componente,
  etapa, subetapa, DTO, enum, exceção, evento ou condição novo** — §4.1 permanece com
  **14**, §2 com **nove** e §5 com **catorze**. **`N-b-M1`–`N-b-M8`**, **`E4-1`–`E4-14`** e
  **`CAL6-1`–`CAL6-8`** permanecem **intactos**, e **CN4 não cria alerta nem escolhe
  destino**. **A coordenação em runtime NÃO está materializada** e o **`OrquestradorMotor`
  continua AUSENTE**: o que deixou de estar aberta é a **decisão arquitetural**, **não** o
  bloqueador de runtime.
- **Fora de `C`**, a **condição 6** — `calendario_integrado` — está **arbitrada** e o seu
  ***gate* determinístico *fail-closed*** **materializado e versionado**.
  O contrato vivo é `docs/07` §4.4 (`CAL6-1`–`CAL6-8`), com a regra de família em
  `docs/06` §4.2. A condição representa **exclusivamente** a **capacidade operacional de
  runtime** para que uma consulta autoritativa **possa ser iniciada**; o **owner** é a
  **raiz de composição / adaptador de calendário da etapa 6**, e o `OrquestradorMotor`
  **apenas transporta**. **Nenhum produtor, módulo, DTO, enum, *loader*, constante ou
  variável de ambiente foi criado**, e **nenhum provedor foi escolhido**. Quando **C7 é
  efetivamente alcançada** — `coletando_dados`, `E03` disponível e interesse **verdadeiro**
  —, `None` passou a ser **erro de contrato** na guarda de **T14**, em vez de escorrer
  silenciosamente para **T04**. **`T14`, `T15` e `T25` permanecem estruturalmente
  inalteradas**, `I17` é preservada e `src/casa77_sdr/cycle_inputs.py` permanece
  **byte-idêntico** à `main` — a coerência semântica continua tendo **um único dono**, a
  `MaquinaEstados` (`IC-11`). A **integração externa real de calendário continua ausente**.
- **Fora de `C`**, o **produtor determinístico de eventos derivados da `Interpretacao`**
  — o residual **`N-b-RES2`** — está **materializado e versionado** em
  `src/casa77_sdr/interpretation_events.py`, com o contrato vivo em `docs/07` §6.3
  (`RES2-1`–`RES2-12`). Ele converte sinal interpretado em **evento confirmado**, com
  saída **fechada** em `E02`/`E03`/`E04`/`E05`/`E06`/`E10` e `ALTA` confirmando,
  `BAIXA` não. **`E09`, `E11`, `E17` e `E18` permanecem fora dele**, e ele **não faz a
  integração do ciclo**, que **continua pendente**.
- **Fora de `C`**, o **produtor determinístico de `E14` e do `motivo_encerramento`**
  — **`S3-D1`** — está **materializado e versionado** em
  `src/casa77_sdr/closure_decision.py`, com o contrato vivo em `docs/07` §6.3
  (`S3D1-1`–`S3D1-12`) e a extensão semântica **AJ3**. Ele converte os **quatro sinais
  de encerramento interpretados** em `E14` mais um dos **quatro** motivos de T35,
  **somente** quando existe **um único** sinal de confiança `ALTA` — dois ou mais são
  **fail-closed** —, e `INCOMPATIBILIDADE_ACEITA` exige **cumulativamente**
  `ResultadoQualificacao.INCOMPATIVEL`. **AJ3** ampliou `IntencaoConversacional` de
  **11** para **15** valores à sua época, preservando a partição e sem criar categoria,
  erro ou exceção nova; a **cardinalidade vigente é 23**, fixada depois por **AJ4**. A fronteira é
  **agnóstica ao estado**, **não conhece `E18`** e **não faz a integração do ciclo**,
  que **continua pendente**.
- **Fora de `C`**, a **semântica completa de handoff** e o **`DetectorHandoff`** estão
  **materializados e versionados**. A extensão **AJ4** — vigente — ampliou
  `IntencaoConversacional` de **15** para **23** valores —
  **A1 = 6**, **A2 = 14**, **B = 3**, autônomos = **17** —, acrescentando a **A2** os
  **oito sinais de handoff**. O **`DetectorHandoff`**, em
  `src/casa77_sdr/handoff_detection.py`, com o contrato vivo em `docs/07` §6.3
  (`DH-1`–`DH-12`), deixa de ser conceitual: ele converte os sinais interpretados em
  **um único `E18`** carregando os **motivos** do vocabulário **fechado de dez** de
  `docs/06` §2.1, **sem precedência** e **sem motivo principal**. **`ALTA` confirma;
  `BAIXA` não confirma**, com a **única exceção vigente** de `pedido_de_humano`. Os
  gatilhos **1–2** continuam chegando como `E09` e os **11–12** por transição;
  **visita** e **reserva** são handoff, e **disponibilidade** permanece nas condições
  **5/6** e em **T14/T15/T25**. Ele **não faz a integração do ciclo**, que **continua
  pendente**.
- **Fora de `C`**, o **produtor determinístico dos eventos internos do ciclo** —
  **`E07`**, **`E08`** e **`E09`** — está **materializado e versionado** em
  `src/casa77_sdr/cycle_events.py`, com o contrato vivo em `docs/07` §6.3
  (`CIE-1`–`CIE-10`). Ele é **posterior** à qualificação
  e a **S2-D8**, e **fora de ambas**: recebe a `Qualificacao` já calculada, o booleano
  `insumo_qualificacao_atualizado` e o `ResultadoS2D8`, e devolve **apenas** os três
  eventos, em ordem canônica **sem precedência**. `E07` exige **as duas** condições de
  `docs/06` §2.2 e **não** decide a mutação; `E08` lê a classificação já calculada e
  **não** escolhe a classe T05/T22 × T06/T23; `E09` vem **das causas** de S2-D8 —
  `resposta_aprovada_disponivel` ou `pendencia_impeditiva` **isoladamente não bastam**.
  **S2-D8 continua não criando nem confirmando `E09`.** Ele **não agrega** produtores,
  **não monta `CondicoesCiclo`** e **não faz a integração do ciclo**, que **continua
  pendente**.
- **Fora de `C`**, a **etapa 6** — o **`AtualizadorDadosAtendimento`** — está
  **materializada e versionada** em `src/casa77_sdr/data_update.py`, com o contrato vivo
  em `docs/07` §4.1.8
  (`AD-1`–`AD-12`). Ela recebe os **dados vigentes de qualificação** e a
  **`Interpretacao` canônica**, e devolve os **dados atualizados**, as **correções
  registradas**, os **campos em conflito** e o sinal **`insumo_qualificacao_atualizado`**
  — a **condição 1** de `docs/07` §4.4, que passa a ter **produtor concreto**. Somente
  **`ALTA`** é efetiva; **correção explícita sobrescreve**; **contradição sem correção
  não grava** e fica registrada; a igualdade é **estrita de domínio**, reutilizando
  `interpretation._mesmo_valor`; e a mutação é apurada **campo a campo**. A fronteira
  **não persiste** — a escrita física continua na **etapa 13** —, **não agrega**
  produtores e **não monta `CondicoesCiclo`**.
- **Fora de `C`**, a **composição dos insumos da máquina** — a **agregação** dos eventos
  confirmados por produtores distintos e a **montagem de `CondicoesCiclo`** — está
  **materializada e versionada** em
  `src/casa77_sdr/cycle_inputs.py`, com o contrato vivo em `docs/07` §4.1.9
  (`IC-1`–`IC-12`). São **duas funções puras**, **sem classe, enum, DTO ou exceção nova**,
  que cobrem a **primeira chamada** da máquina em um ciclo de **nova mensagem**: **`E01` é
  obrigatório e explícito**, os **slots** são fechados — `E02`/`E03`/`E04`/`E05`/`E06`/`E10`
  e `E07`/`E08`/`E09` —, `E14` e `E18` entram **apenas** pelos respectivos produtores, e
  `E11`, `E12`, `E13`, `E15`, `E16` e `E17` **não entram**. **Nenhum evento concorrente é
  suprimido**, **não há deduplicação silenciosa** e a **ordem canônica não é precedência**.
  A montagem transporta as **oito** condições **sem criar a nona**, com o par de **S2-D8**
  ***all-or-none*** e os motivos de *handoff* projetados como **`str` puros**. Ela **não
  recebe** `ResultadoS2D8`, **não chama** produtor algum, **não chama** a máquina e **não é**
  o `OrquestradorMotor`: a **coerência semântica continua sendo da `MaquinaEstados`**, e a
  **coordenação do pipeline continua ausente**.
- A **pendência `B`** — colisão do nome `RegistroAtendimento` — está **ARBITRADA e
  versionada** (`docs/07` §4.1.1, `B-1`–`B-5`): o **componente de comportamento** de §4.1
  passa a se chamar **`AtualizadorDadosAtendimento`** e a
  **dataclass** de `src/casa77_sdr/persistence.py` **preserva** nome, semântica, campos e
  exportação. **Zero renomeação de código preexistente**, **zero alias**, **zero terceira
  abstração**, e §4.1 continua com **14** componentes.
- **Fora de `C`**, o tratamento de **`SEM_CANDIDATO_ELEGIVEL`** — a pendência **E4** —
  está **arbitrado e versionado**, com o contrato vivo em `docs/07` §7.1
  (`E4-1`–`E4-14`) e o reflexo em
  `docs/06` §4.5 (G7 e o caso 3). O branch executa as etapas **1** a **5** e encerra **sem
  transição**: **zero emissão**, **zero handoff**, `ProcessamentoPendente` preservado,
  **tentativa** de alerta operacional e chave de idempotência marcada **fora da etapa 13**.
  **Nenhum componente, estado, evento, transição ou condição foi criado**, e **nenhum
  código ou teste mudou**. A **coordenação** desse branch continua sendo do
  `OrquestradorMotor`, que permanece **ausente**; o **destino do alerta**, a **persistência
  não volátil** e o **mecanismo de replay** dos pendentes continuam **abertos**.
- Etapa 4 permanece **absorvida pela Etapa 3B**; etapas 5 a 10 permanecem futuras
  (`docs/05-roadmap.md`).

---

## 2. Última entrega funcional relevante

Commit funcional `e23d1e726d2e7a22f052cfc48de09badb313a058`.

**A última entrega funcional relevante é o produtor determinístico compartilhado da
`FotografiaFragmento`**, **materializado e versionado** em
`src/casa77_sdr/fragment_snapshot.py`, com o contrato vivo em `docs/07` §4.4.6
(`FF-1`–`FF-12`). A **montagem** da fotografia deixou de ser *inline* e passou a ter **uma
única fronteira de produção**: `montar_fotografia_fragmento(token, consistencia, *,
assertivas_runtime)`.

**`coverage_decision.py` passou a consumir a montagem compartilhada**, e
`_projetar_indisponiveis` foi **removida** por não ter mais consumidor.
**`avaliar_emissibilidade` continua sendo a única implementação de decisão de `D8-F`**
(§4.4.5): **montar não é avaliar**. O **comportamento público de S2-D8 é idêntico** — assinatura,
*defaults*, `ResultadoS2D8`, ordem de fragmentos e de causas, deduplicação, candidatura,
**`D8-G`**, **`D8P-11`**, `R05`, Classe I, Classe II, erros e mensagens —, e **candidatura**,
**resolução de runtime**, **cobertura** e **projeção de causas** continuam sendo dele.

**Permanece igualmente vigente o *owner* de emissão de T16 — `R06/F1`**,
**materializado e versionado** em `src/casa77_sdr/emission_projection.py`, com o contrato
vivo em `docs/07` §4.1.5 (`PE-15`–`PE-20`). **`INFORMAR_CONDICOES_DE_VISITA` mapeia
`R06/F1`**, em **dupla rota condicionada à emissibilidade**, com **regra própria** —
**nada é herdado de `R05` por analogia**.

**Cobertura presente → a cobertura é a *owner***: o token **mantém a posição original**, não
há segunda ocorrência e a fotografia **nem é lida**. **Cobertura ausente → a ação é a
*owner***, e ela consome **exclusivamente** a primitiva compartilhada
`avaliar_emissibilidade` (`docs/07` §4.4.5) sobre uma **`FotografiaFragmento` já recebida**.
**Emitível** → o token entra **uma vez**; **não emitível** → **zero fragmento
acrescentado**, sob **`PE-7`** — não é erro, não há resultado parcial e não há substituto.
**Zero `E09`**, **zero `E18`** e **zero nova chamada da `MaquinaEstados`**.

Com a nova fronteira, **`R06/F1` pode ter a sua `FotografiaFragmento` montada
deterministicamente** com `assertivas_runtime=()`. **Isso não integra a chamada ao
ciclo.** **`T16` não está concluída *end-to-end***: a **primitiva determinística de
montagem** está **materializada e versionada** (§4.4.6), mas a sua
**invocação/coordenação dentro do ciclo** continua **ausente**, assim como o
**`OrquestradorMotor`**, a **integração *end-to-end*** e a **política da etapa 10 para a
obrigação degradada** (§1, §6).

**Permanece igualmente vigente a composição dos insumos da primeira decisão** — a
**agregação** dos eventos confirmados por produtores distintos e a **montagem de
`CondicoesCiclo`** —, **materializada e versionada** em `src/casa77_sdr/cycle_inputs.py`,
com o contrato vivo em `docs/07` §4.1.9 (`IC-1`–`IC-12`).

São **duas funções puras**, **sem classe, enum, DTO ou exceção nova**, que cobrem a
**primeira chamada** da máquina em um ciclo de **nova mensagem**. **`E01` é obrigatório e
explícito**; os **slots** são fechados — `E02`/`E03`/`E04`/`E05`/`E06`/`E10` e
`E07`/`E08`/`E09` —; `E14` e `E18` entram **apenas** pelos respectivos produtores; e `E11`,
`E12`, `E13`, `E15`, `E16` e `E17` **não entram**. **Nenhum evento concorrente é
suprimido**, **não há deduplicação silenciosa**, **duplicata é *fail-closed*** e a **ordem
canônica da tupla é apenas auditabilidade, nunca precedência**.

A montagem transporta exatamente os **oito** campos de `CondicoesCiclo` **sem criar o
nono**, preservando `None`, `False` e `()` como estados **distintos**, com as **condições 2
e 4** de S2-D8 ***all-or-none*** e os motivos de *handoff* projetados como
**identificadores textuais**. Ela **não recebe** `ResultadoS2D8`, **não chama** produtor
algum, **não chama** a `MaquinaEstados` e **não é** o `OrquestradorMotor`: a **coerência
semântica continua sendo da `MaquinaEstados`**, e a **coordenação do pipeline continua
ausente**.

**Permanece igualmente vigente a etapa 6 — o `AtualizadorDadosAtendimento`** — a fronteira que registra
dados e correções sobre os **dados vigentes de qualificação**, a partir da
**`Interpretacao` canônica**, em `src/casa77_sdr/data_update.py`, com o contrato vivo em
`docs/07` §4.1.8 (`AD-1`–`AD-12`). **A condição 1 de §4.4 —
`insumo_qualificacao_atualizado` — passou a ter produtor concreto.**

Ela ocorre **depois** da etapa 4 e **depois** da etapa 5, e **fora de ambas**. Recebe
**somente** `DadosQualificacao` vigente e `Interpretacao` canônica — nunca texto,
identidade, estado, *takeover*, qualificação, YAML ou identificador de atendimento — e
devolve os **dados atualizados**, as **correções registradas**, os **campos em conflito** e
o **booleano** de mutação. A canonicidade é verificada **reutilizando** a validação de N-b;
**nenhum validador paralelo**.

O domínio é **fechado nos seis campos**, na ordem canônica **importada** de
`interpretation._CAMPOS_DADOS`. Somente **`ALTA`** é efetiva — `BAIXA` não grava, não
corrige, não conflita e não muta, e a exceção de **N-b-PH3** **não se aplica a dados**.
**Correção explícita sobrescreve**; **contradição sem correção não grava** e preserva a
evidência em `campos_em_conflito`, materializando §7. `correcoes` é **predicado**, nunca
fonte de valor: `valor_novo` jamais é aplicado como segunda escrita.

A igualdade é **estrita de domínio**, reutilizando `interpretation._mesmo_valor`: sem
`lower`, `strip`, acento, Unicode, sinônimo, regex ou calendário — `"Casamento"` ≠
`"casamento"`. A **mutação** é apurada **campo a campo**, nunca pela presença da mensagem,
e o resultado é sempre um **`bool` real**.

**Os dois `contato` continuam fronteiras distintas**: o interpretado pode ser atualizado
aqui; o **operacional** de `RegistroAtendimento` **não** — o módulo sequer importa a
persistência. A fronteira é **pura**, **não persiste** — a escrita física continua na
**etapa 13** —, **não agrega** produtores, **não monta `CondicoesCiclo`** e **não chama** a
máquina.

**A pendência `B` foi arbitrada** (`docs/07` §4.1.1, `B-1`–`B-5`): o **referente
comportamental** recebe o nome `AtualizadorDadosAtendimento` e a **dataclass**
`RegistroAtendimento` de `src/casa77_sdr/persistence.py` é **preservada** — nome,
semântica, campos e exportação. **Zero renomeação de código preexistente**, **zero alias**,
**zero terceira abstração**, e §4.1 continua com **14** componentes.

`docs/06-maquina-de-estados.md`, `src/casa77_sdr/interpretation.py`,
`src/casa77_sdr/interpretation_events.py`, `src/casa77_sdr/qualification.py`,
`src/casa77_sdr/rules.py`, `src/casa77_sdr/cycle_events.py`,
`src/casa77_sdr/persistence.py`, `src/casa77_sdr/context.py`,
`src/casa77_sdr/identity.py`, `src/casa77_sdr/state_machine.py` e
`src/casa77_sdr/__init__.py` permanecem **inalterados**; nada da fronteira é exportado pelo
pacote. **`knowledge/**` e `prompts/**` permanecem inalterados.**

A **integração do ciclo continua pendente**: a **agregação** dos eventos de produtores
distintos e a **montagem de `CondicoesCiclo`** estão **materializadas e versionadas** (§1);
continua **ausente** o **`OrquestradorMotor`**.

Permanece igualmente vigente o **produtor determinístico dos eventos internos do ciclo** — a fronteira que
converte a **qualificação** e o **resultado de S2-D8** em **`E07`**, **`E08`** e
**`E09`**, em `src/casa77_sdr/cycle_events.py`, com o contrato vivo em `docs/07` §6.3
(`CIE-1`–`CIE-10`). **`E07`, `E08` e a conversão `causas_e09` → `Evento.E09` deixaram de
carecer de produtor.**

Ela ocorre **depois** da qualificação e **depois** de S2-D8, e **fora de ambas**. A
entrada é a `Qualificacao` já calculada, o booleano `insumo_qualificacao_atualizado` e o
`ResultadoS2D8` — nunca texto, `Interpretacao`, `Estado`, `SituacaoTakeover` ou
`CondicoesCiclo`. A saída é **fechada** em três eventos, em ordem canônica **apenas para
auditabilidade**, e a **tupla vazia é resultado legítimo**.

`E07` exige **as duas** condições de `docs/06` §2.2 — insumo atualizado **e** resultado
`QUALIFICADO` ou `QUALIFICADO_COM_RESSALVA` — e a fronteira **não decide a mutação**, que
chega já decidida. `E08` é confirmado **se e somente se** o resultado for `INCOMPATIVEL`,
sem reler YAML, sem recriar `Violacao` e **sem** escolher a classe **T05/T22 × T06/T23**,
que continua na máquina. `E09` vem **das causas** de S2-D8: `resposta_aprovada_disponivel`
falso **não basta** e `pendencia_impeditiva` verdadeiro **não basta** sem causa
correspondente; qualquer quantidade de causas confirma **um único** evento, e elas **não
são reconstruídas, deduplicadas nem reinterpretadas**. **S2-D8 continua não criando nem
confirmando `E09`.**

A fronteira é **pura** — zero I/O, rede, relógio, YAML, `knowledge/**`, LLM, SDK,
persistência, logging, cache ou retry —, **não agrega** produtores, **não monta
`CondicoesCiclo`**, **não a importa**, **não chama `decidir(...)`** e **não é** componente
novo: §4.1 permanece com **14**.

`src/casa77_sdr/qualification.py`, `src/casa77_sdr/coverage_decision.py`,
`src/casa77_sdr/state_machine.py`, `src/casa77_sdr/interpretation_events.py`,
`src/casa77_sdr/handoff_detection.py`, `src/casa77_sdr/closure_decision.py` e
`src/casa77_sdr/__init__.py` permanecem **inalterados**; nada da fronteira é exportado
pelo pacote. **`knowledge/**` permanece inalterado.**

A **integração do ciclo continua pendente**: a **agregação** dos eventos de produtores
distintos e a **montagem de `CondicoesCiclo`** estão **materializadas e versionadas** (§1);
continua **ausente** o **`OrquestradorMotor`**. O produtor de
**`insumo_qualificacao_atualizado`** — a **etapa 6** — **não é** a lacuna: ele está
**materializado e versionado**.

Permanecem igualmente vigentes: a **semântica completa de handoff + `DetectorHandoff`** — o produtor
determinístico de **`E18`** e dos **motivos de handoff** originados da **interpretação
do interessado**, em `src/casa77_sdr/handoff_detection.py`, com o contrato vivo em
`docs/07` §6.3 (`DH-1`–`DH-12`). O `DetectorHandoff`, que `docs/06` §9 já atribuía aos
**gatilhos 3–10** de `docs/04`, **deixou de ser conceitual**: **`E18` passou a ter
produtor concreto**.

Ele ocorre **depois da etapa 4 e fora dela**: a **etapa 4 continua sem emitir `Exx`** e
continua terminando em `Interpretacao`. A entrada é uma **`Interpretacao` canônica**, e
nada mais — nunca texto, `Qualificacao`, `Estado`, `SituacaoTakeover` ou
`CondicoesCiclo`. A canonicidade é verificada **reutilizando** a validação já existente
da fronteira N-b — **nenhum validador paralelo**. Entrada inválida bloqueia, **sem saída
parcial**.

A extensão semântica **AJ4** ampliou `IntencaoConversacional` de **15** para **23**
valores, acrescentando ao grupo **A2** os **oito sinais de handoff**. A partição vigente
é **A1 = 6**, **A2 = 14**, **B = 3**, com **17** códigos no **slot autônomo**.
`_CODIGOS_A1` **não mudou**, **B não mudou**, e os oito são intenções autônomas
**normais**: sem payload paralelo, **sem campo novo** em `Interpretacao`, **sem `E-Nb`
novo**, **sem exceção pública nova** e **sem exclusão mútua nova**. A lista de erros
continua **`E-Nb-1`–`E-Nb-19`** e a `ProjecaoInterpretacao`, com **sete** campos.

A saída é **um único `E18`** carregando os **motivos** do vocabulário **fechado de dez**
de `docs/06` §2.1, sem duplicata e em ordem canônica — **sem precedência** e **sem motivo
principal**. **`ALTA` confirma; `BAIXA` não confirma**, com a **única exceção vigente** de
`pedido_de_humano` (**N-b-PH3**), efetivo em `ALTA` **e** em `BAIXA` e **não estendida por
analogia**. **`None` é resultado legítimo**.

**Fora do detector**: os gatilhos **1–2** continuam chegando como **`E09`**; os **11–12**
são materializados por **transição**; a **disponibilidade de data** permanece nas
**condições 5 e 6** e em **T14/T15/T25**; e o **interesse simples em visita** continua em
`E10`/**T16**. **Visita** e **reserva** são handoff; **disponibilidade** não é.

A fronteira é **pura** — zero I/O, rede, relógio, YAML, `knowledge/**`, LLM, SDK,
persistência, logging, cache ou retry —, **não lê texto** da mensagem, **não usa palavra-
chave, regex, score de sentimento ou contagem**, **não constrói `CondicoesCiclo`** e
**não é** componente novo: §4.1 permanece com **14**.

`src/casa77_sdr/state_machine.py`, `src/casa77_sdr/interpretation_events.py`,
`src/casa77_sdr/closure_decision.py`, `src/casa77_sdr/interpretation_anthropic.py`,
`src/casa77_sdr/identity.py`, `src/casa77_sdr/qualification.py` e
`src/casa77_sdr/__init__.py` permanecem **inalterados**; nada da fronteira é exportado
pelo pacote. **`knowledge/**` permanece inalterado.** **`N-b-RES2` continua sem produzir
`E18`**, **`S3-D1` continua sem produzir `E18`**, a **identidade** não muda, e os oito
sinais novos são **neutros** em todas as três fronteiras.

A **integração do ciclo continua pendente**: a **composição dos insumos da primeira
decisão** já **agrega** os eventos confirmados de produtores distintos (§1; `docs/07`
§4.1.9), mas o **`OrquestradorMotor`** continua **ausente** e ainda precisa **coordenar o
pipeline** e **chamar a máquina**.

Permanecem fatos vigentes de entregas anteriores: **`S3-D1`** — o produtor determinístico
de **`E14`** e do
**`motivo_encerramento`** originados da **interpretação do interessado**, em
`src/casa77_sdr/closure_decision.py`, com o contrato vivo em `docs/07` §6.3
(`S3D1-1`–`S3D1-12`). A **condição 8** de `CondicoesCiclo`, que §4.4 registrava
**sem produtor atribuído**, passou a ter produtor concreto.

Ele ocorre **depois da etapa 4 e fora dela**: a **etapa 4 continua sem emitir
`Exx`** e sem produzir `motivo_encerramento`, e continua terminando em
`Interpretacao`. A entrada é uma **`Interpretacao` canônica** mais um
**`ResultadoQualificacao`** — nunca texto, `Estado`, `SituacaoTakeover`,
`CondicoesCiclo`, `motivos_handoff` ou a `Qualificacao` completa. A canonicidade é
verificada **reutilizando** a validação já existente da fronteira N-b — **nenhum
validador paralelo** e **nenhuma regra copiada**. Entrada inválida bloqueia, **sem
saída parcial**.

A extensão semântica **AJ3** ampliou `IntencaoConversacional` de **11** para
**15** valores **à sua época**, acrescentando ao grupo **A2** os **quatro sinais de
encerramento** — `DESINTERESSE_DECLARADO`, `CONTATO_POR_ENGANO`,
`MENSAGEM_NAO_SOLICITADA` e `ACEITACAO_DE_INCOMPATIBILIDADE`. A partição é preservada, e a
**cardinalidade vigente é 23** — **A1 = 6**, **A2 = 14**, **B = 3**, autônomos = **17** —,
fixada depois por **AJ4** (§1).
`_CODIGOS_A1` **não muda**, nenhum código A1 vira autônomo, e os quatro sinais são
intenções autônomas **normais**: sem payload paralelo, **sem campo novo** em
`Interpretacao`, **sem `E-Nb` novo** e **sem exceção pública nova**. A lista de
erros continua **`E-Nb-1`–`E-Nb-19`** e a `ProjecaoInterpretacao`, com **sete**
campos.

A saída é **fechada em `E14`** mais um dos **quatro** motivos já enumerados por
T35, e **`None` é resultado legítimo**. **Somente `ALTA` conta**: `BAIXA` não entra
no conjunto considerado e **não impede** que um único `ALTA` diferente resolva. O
conflito é ***fail-closed***: com **dois ou mais** sinais `ALTA` o resultado é
`None`, sem ordenar, ranquear, somar ou usar a ordem canônica como precedência.
`INCOMPATIBILIDADE_ACEITA` exige **cumulativamente** o sinal explícito de aceitação
e `ResultadoQualificacao.INCOMPATIVEL`.

A fronteira é **agnóstica ao estado**: não recebe `Estado` nem `SituacaoTakeover` e
**não cria regra nova de supressão de `E14`**. O contrato vigente da máquina
prevalece — **T32** em `encaminhado_humano`, **T34** em `atendimento_humano`,
`E14` × `E18` → **N3** —, e a regra de **zero resposta automática** em *takeover*
não muda. Ela é **pura** — zero I/O, rede, relógio, YAML, `knowledge/**`, LLM, SDK,
persistência, logging, cache ou retry —, **não lê texto** da mensagem e **não é**
componente novo: §4.1 permanece com **14**.

`src/casa77_sdr/state_machine.py`, `src/casa77_sdr/interpretation_events.py`,
`src/casa77_sdr/interpretation_anthropic.py`, `src/casa77_sdr/identity.py`,
`src/casa77_sdr/qualification.py` e `src/casa77_sdr/__init__.py` permanecem
**inalterados**; nada da fronteira é exportado pelo pacote. **`knowledge/**`
permanece inalterado.** **`N-b-RES2` continua sem produzir `E14`**, e os quatro
sinais novos são **neutros** nele.

Permanecem igualmente vigentes: o **produtor não determinístico de `N-b`**
(`M-PN1`–`M-PN12`), o **produtor de eventos derivados** `N-b-RES2`
(`RES2-1`–`RES2-12`), **30 `Rxx`**, **37 fragmentos emitíveis**,
**118 *bindings***, **19 *templates***, **18 fragmentos estáticos** e o mapa
`knowledge/mapa-cobertura.yaml` com a associação total dos **54**
`AssuntoComercial` — **33** com cobertura e **21** com `grupos: []`.

---

## 3. Baseline funcional

**Baseline funcional corrente** — evidência da suíte sobre a capacidade corrente
materializada:

- Python **3.14.5**;
- **`9394 passed`**, sob **`-W error`**;
- zero failures, zero errors, zero warnings, zero skips, zero xfails.

Este é o **baseline da entrega versionada** do **produtor determinístico compartilhado da
`FotografiaFragmento`**: **`9394 passed`** sob **`-W error`**. A **`main` de base** desta
entrega registrava **`9276 passed`** — o baseline do ***owner* de emissão de T16**. O
acréscimo de **118** vem,
**integralmente**, dos cenários novos de `tests/test_fragment_snapshot.py` — os quatro
campos e as suas autoridades, a ordem física e as duplicatas de **`C-7`**, o transporte
literal do runtime, o ***fail-closed*** de `status_ausente` e `status_ambiguo`, os tipos
exatos da superfície, a pureza por AST, os imports fechados, a prova de que S2-D8 **não
monta mais a fotografia *inline*** e a **prova de encaixe** com a rota *action-owner* de
**T16**/`R06`. **Zero teste existente foi alterado**: `tests/test_coverage_decision.py`
continua com **177**, `tests/test_fragment_emissibility.py` com **63** e
`tests/test_emission_projection.py` com **139**.

O baseline **precedente** era o do ***owner* de emissão de T16**:
**`9276 passed`** sob **`-W error`**. A **`main` de base** daquela entrega registrava
**`9236 passed`** — o baseline da **primitiva única de emissibilidade**. O acréscimo de
**40** vem, **integralmente**, dos
cenários novos de `tests/test_emission_projection.py` — as duas rotas de `R06/F1`, a
**preservação da posição** quando a cobertura é a *owner*, a **irrelevância da fotografia**
fora da rota da ação, o ***fail-closed*** de `tipo_invalido: fotografia_r06`, os **seis**
desfechos de não emissibilidade com **zero fragmento**, a **ação repetida** consultando a
autoridade **uma única vez**, e o *gate* de corpus agora **distinguindo** a classe estática
— `R03/F1` e `R05/F1`, com zero *bindings* — da **condicionada** — `R06/F1`, com *bindings*
e **zero `RUNTIME_AUTORITATIVO`**.

O baseline **precedente** era o da **primitiva única de emissibilidade**: **`9236 passed`**.
O acréscimo de **63** veio,
**integralmente**, dos cenários novos de
`tests/test_fragment_emissibility.py` — fragmento emitível, os dois rótulos não emitíveis, o
**curto-circuito** do status, Classe II, um e vários `ReferenteIndisponivel` na **ordem
física**, o acúmulo de causas na **ordem fixa**, `ASSERTIVA` de runtime verdadeira e falsa, a
**ausência de deduplicação interna**, a propagação intacta de `AssertivaNaoAvaliavel`, a
**pureza por AST** e a prova de que os *gates* de **Classe I** e de **candidatura**
**continuam** em S2-D8. A adaptação da *whitelist* **não cria teste novo**:
`tests/test_coverage_decision.py` permanece com **177** itens, como na `main`.

O baseline **precedente** era o do ***owner* de emissão de T15**: **`9173 passed`**. O
acréscimo de **16** veio dos cenários
de `tests/test_emission_projection.py` — os dois caminhos da dupla rota, a **preservação da
posição** do token quando a cobertura é a *owner*, a **ação repetida** contribuindo uma só
vez nas duas rotas, o ***fail-closed*** de **`R05/F2`** e **`R05/F3`** com a ação de T15 e a
sua passagem livre **sem** ela, a **não contaminação** de **`R03/F1`**, e o *gate* de corpus
agora exigindo **duas** unidades materializadas com **zero *bindings***.

O baseline **anterior** era o do ***gate*** da **condição 6**: **`9157 passed`**. O
acréscimo de **7** veio dos cenários de
`tests/test_state_machine.py` — `None` com interesse confirmado como **erro de contrato**,
`None` legítimo com interesse **falso** e **não avaliado**, `None` legítimo **sem `E03`**
disponível para o gatilho, e a **preservação de precedência** quando `E18` (C2), `E09`
impeditivo (C6) ou `E08` documentado (C5) resolvem o estado **antes** de C7.

O baseline **anterior** era o da **cadeia operacional de N-b**: **`9150 passed`**. O
acréscimo de **85** veio dos cenários de
`tests/test_interpretation_stage.py` — a chamada única ao produtor **por invocação**, a
identidade de objeto da `Interpretacao` nas três derivações, a forma do DTO, a ausência de
PII no `repr`, a propagação intacta dos **nove** motivos de falha e dos erros de contrato,
os limites de import e de chamada por AST e a prova de **encaixe estrutural** com
`cycle_inputs` e a `MaquinaEstados`.

O baseline **anterior** era o da **etapa 6**: **`8874 passed`**. O
acréscimo de **191** veio dos cenários de `tests/test_cycle_inputs.py` — o contrato de `E01`,
as combinações exigidas, os domínios fechados por slot, as duplicatas, a ordem canônica sem
precedência, as oito condições, o par *all-or-none* de S2-D8, a projeção dos motivos, a
composição com a `MaquinaEstados` **nos testes** e as provas de pureza por AST.

O baseline **anterior** era o do produtor de `E07`/`E08`/`E09`: **`8723 passed`**. O
acréscimo de **151** vem dos cenários de `tests/test_data_update.py` — a política dos seis
campos, as correções, os conflitos, a igualdade estrita de domínio, a definição de mutação,
a fronteira entre os dois `contato`, a pureza, os erros e a **integração contratual** que
compõe `data_update` → `avaliar_regras` → `qualificar` → `cycle_events` **nos testes**.

O baseline **anterior** era o da semântica de handoff: **`8606 passed`**. O acréscimo de
**117** vem dos cenários de
`tests/test_cycle_events.py` — as regras dos três eventos, as **seis** composições
válidas, a ordem canônica, os tipos inválidos, a pureza e a composição com a
`MaquinaEstados`, mais as provas de preservação das fronteiras já aprovadas.

O baseline **anterior** era o de `S3-D1`: **`8234 passed`**. O acréscimo de **372** vem de
**AJ4** e do **`DetectorHandoff`**: os cenários de `tests/test_handoff_detection.py` — as
dez famílias de gatilho, a exceção de `pedido_de_humano`, a multiplicidade sem
precedência, os invariantes do DTO e a pureza —, mais as provas de **neutralidade** dos
oito sinais novos em **RES2**, em **S3-D1** e na **identidade**, e a ampliação das
parametrizações já existentes sobre o slot autônomo, que passou de **nove** para
**dezessete** códigos.

Antes dele, o baseline era **`7978`**. O acréscimo de **256** veio de **`S3-D1`** e de
**AJ3**: os cenários de `tests/test_closure_decision.py` — mapeamento, cardinalidade
*fail-closed*, *gate* de incompatibilidade, invariante de `E14`, pureza e composição com
a `MaquinaEstados` —, mais a ampliação das parametrizações já existentes sobre o slot
autônomo, que passou de **cinco** para **nove** códigos.
`tests/test_state_machine.py` e `tests/test_interpretation_anthropic.py` permanecem
**inalterados** e continuam as autoridades das suas próprias fronteiras.

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
    projeta os fragmentos autorizados — **materializados**: infraestrutura estrutural
    (`docs/07` §4.4.2), **produtor determinístico** (§4.4.3), **aplicabilidade de pacote**
    (§4.4.4) e o **artefato físico do mapa**. Continua **ausente** a **integração pelo
    `OrquestradorMotor`**;
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
  alternativa emitível na ordem declarada do grupo** (`docs/07` §4.4.1, `SF-D4`) — **e
  materializada no produtor** (§4.4.3), agora sobre o **mapa real**. Duas regras novas a
  acompanham: **`D8-G`**, o *gate* de candidatura de preço, que traduz a **aplicabilidade de
  pacote** (§4.4.4) em candidatura das **duas faixas**, e **`D8-L4`**, que só avalia **grupos
  aplicáveis** e **nunca** deixa um assunto verdadeiro por vacuidade. O que continua pendente
  é a **integração pelo `OrquestradorMotor`**: a seleção **não corre dentro do ciclo**.
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
  materializado nesta fronteira**: nesta versão, **exatamente três** ações têm contribuição
  textual materializada — **`INFORMAR_LACUNA_DE_INFORMACAO`**,
  **`INFORMAR_NAO_CONFIRMACAO_DE_DISPONIBILIDADE`** e
  **`INFORMAR_CONDICOES_DE_VISITA`**. Para as outras **17**, **`()` significa
  zero fragmento acrescentado pelo `ProjetorEmissao`** — e **não** que a ação esteja
  resolvida: a **obrigação conversacional permanece**.
- **`R03/F1`**, **`R05/F1`** e **`R06/F1`** são os **três fragmentos materializados** pelo
  projetor, com
  **naturezas distintas**. Um ***gate* mecânico do corpus** comprova, para **os três**, a
  **existência** e o status **`APROVADO`**, e a partir daí **divide-se em duas classes**
  (**`PE-11`**): a **estática** — **`R03/F1`** e **`R05/F1`** — exige **zero *bindings***; a
  **condicionada** — **`R06/F1`** — exige o oposto, **ter *bindings*** e **nenhum** de origem
  **`RUNTIME_AUTORITATIVO`**. **`R03/F1`** é
  **mandatório puro**: ele **não pertence a `R2`**, chega **exclusivamente** pela ação de
  lacuna, e a colisão ***cross-source*** com ele **continua *fail-closed***. **`R05/F1`**
  **pertence a `R2`** — é alternativa do grupo de `disponibilidade_de_data` — e por isso
  **pode chegar pela cobertura de S2-D8**, além de poder ser **exigido pela ação de T15**:
  daí a **dupla rota fechada** por **`PE-13`**, com **cobertura presente → cobertura
  *owner*** e **cobertura ausente → ação *owner***, sempre em **exatamente uma ocorrência**.
  Nenhum dos três é **reavaliado por S2-D8 nesta fronteira** e nenhum **torna a
  `MaquinaEstados` conhecedora de `Rxx`**.
- **Fora de `C`**, o ***owner* de emissão de T15** está **materializado e versionado nesta
  entrega**, com o contrato vivo em `docs/07` §4.1.5
  (**`PE-13`**, **`PE-14`**). **`R03/F1`** continua **mandatório puro** — só chega pela ação
  de lacuna. **`R05/F1`** passou a ser **unidade de dupla rota** para **T15**: quando a
  **cobertura** de S2-D8 já o autorizou, **ela é a *owner*** e o token **mantém a posição
  original**, sem segunda ocorrência; quando a cobertura **não** o trouxe, **a ação o
  completa**. É **exceção fechada** deste par ação/token: **`PE-10` continua *fail-closed***
  por padrão — **`R03/F1`** por cobertura **mais** a ação de lacuna **continua fechando** —,
  **não existe deduplicação *cross-source* genérica** e **nenhum token futuro herda a exceção
  por analogia**. Com a ação de T15, **`R05/F2`** e **`R05/F3`** na cobertura **fecham** por
  contradição estrutural (**`PE-14`**): o projetor **não escolhe variante**, **não corrige a
  condição 6** e **não toca os fatos de runtime**. **`S2-D8`**, **`CAL6`**, **`D8P-11`** e
  `coverage_decision.py` **não foram tocados**. A **arbitragem própria** que `R06/F1` exigia
  — por ter ***bindings*** — foi feita **em entrega separada**, abaixo.
- **Fora de `C`**, o ***owner* de emissão de T16** está **materializado e versionado nesta
  entrega**, com o contrato vivo em `docs/07` §4.1.5
  (**`PE-15`**–**`PE-20`**). **`R06/F1`** é **dupla rota condicionada à emissibilidade**, com
  **regra própria** — **nada é herdado de `R05` por analogia**. **Cobertura presente → a
  cobertura é a *owner***: o token **mantém a posição original**, não há segunda ocorrência e
  a fotografia **nem é lida**. **Cobertura ausente → a ação é a *owner***, e ela consome
  **exclusivamente** a **primitiva compartilhada** `avaliar_emissibilidade` (§4.4.5) sobre uma
  **`FotografiaFragmento` já montada** — o projetor **não** compara status, **não** percorre
  referentes, **não** avalia `ASSERTIVA`, **não** lê índice e **não** abre `knowledge/**`.
  **Emitível** → o token entra; **não emitível** → **zero fragmento acrescentado**, sob
  **`PE-7`**: não é erro, não há resultado parcial, não há substituto e **nenhum texto é
  inventado**. A avaliação ocorre **no máximo uma vez por chamada**, com **zero *cache*
  global**. A entrada `fotografia_r06` é **keyword-only e condicional**: exigida **somente**
  na rota da ação, onde ausência ou tipo inválido fecham com `tipo_invalido: fotografia_r06`;
  fora dela é **irrelevante**, e chamadas com **dois argumentos continuam válidas**. **Zero
  `E09`, zero `E18`, zero `CausaE09`, zero `MotivoHandoff` e zero nova chamada da
  `MaquinaEstados`**: `state_machine.py`, `cycle_events.py`, `cycle_inputs.py`,
  `handoff_detection.py`, `coverage_decision.py` e `fragment_emissibility.py` permanecem
  **intocados**. **T16 na máquina permanece literal** — `E10` → `T16` —, e **interesse
  simples em visita continua sendo T16**: pedido de **confirmação** de visita permanece
  matéria **humana** e distinta. **`PE-13`** e **`PE-14`** seguem **inalterados**, e a colisão
  *cross-source* de **`R03/F1`** continua ***fail-closed***. **T16 não está integralmente
  concluída**: a **primitiva determinística de montagem da `FotografiaFragmento`** está
  **materializada e versionada** (§4.4.6), mas a sua **invocação nesta rota, dentro do
  ciclo**, continua **AUSENTE** — residual do futuro **`OrquestradorMotor`** —, e a
  **integração *end-to-end*** continua **ausente**.
- **Fora de `C`**, o **produtor determinístico compartilhado da `FotografiaFragmento`**
  está **MATERIALIZADO E VERSIONADO nesta entrega**, em
  `src/casa77_sdr/fragment_snapshot.py`, com o contrato vivo em `docs/07` §4.4.6
  (`FF-1`–`FF-12`). A **montagem** da fotografia deixou de ser *inline* e passou a ter
  **uma única fronteira**: `montar_fotografia_fragmento(token, consistencia, *,
  assertivas_runtime)`. O `status` vem de `status_por_fragmento`, exigindo **exatamente um**
  par; `divergente`, de `tokens_divergentes`; os caminhos de **`C-7`**, de
  `referentes_indisponiveis`, filtrados pelo token, na **ordem física** e **sem
  deduplicação**, projetando **só o referente**; e `assertivas_runtime` é **transportado
  literalmente**, ***keyword-only* e obrigatório**. **Montar não é avaliar**: **`D8-F`
  continua com uma única implementação de decisão**, `avaliar_emissibilidade` (§4.4.5).
  **S2-D8 consome a primitiva** e preserva **comportamento público idêntico** — assinatura,
  *defaults*, `ResultadoS2D8`, ordem de fragmentos e de causas, deduplicação, candidatura,
  **`D8-G`**, **`D8P-11`**, `R05`, Classe I, Classe II, erros e mensagens —, com os **177**
  cenários de `tests/test_coverage_decision.py` verdes **sem alteração comportamental**.
  `fragment_emissibility.py`, `emission_projection.py` e `response_consistency.py`
  permanecem **byte-idênticos**. **A invocação desta primitiva pela rota *action-owner* de
  T16 dentro de um ciclo real NÃO está materializada**: ela continua sendo do **futuro
  `OrquestradorMotor`** (§6.3, `CN4-1`–`CN4-12`). **T16 continua NÃO concluída
  *end-to-end***.
- **Fora de `C`**, a **primitiva única de emissibilidade de fragmento** está
  **materializada e versionada**, em
  `src/casa77_sdr/fragment_emissibility.py`, com o contrato vivo em `docs/07` §4.4.5
  (`FE-1`–`FE-15`). **`D8-F` continua sendo UMA norma** — nada foi renumerado, ampliado ou
  criado —, e o que passou a existir é **UMA implementação compartilhada** dela: dada a
  **fotografia já recebida** de um fragmento **que já é candidato**, ela responde **se ele
  está emitível agora**, na ordem fixa **`D8-F1`** → **Classe II** → **`C-7`** → **`ASSERTIVA`
  de runtime**. Ela **não conhece** assunto, pergunta, `CausaE09`, `MotivoE09`, `R2`, grupo,
  ***witness***, cobertura, pendência, evento, máquina, ação ou *handoff*, e **não produz
  `E09`**. A **candidatura continua fora** — **`D8-G`** e o *gate* de **`R05`**
  (**`D8P-11`**) permanecem em `coverage_decision.py`, porque **candidatura ≠
  emissibilidade**. **`S2-D8` preserva o comportamento público**: nome, assinatura, defaults,
  tipo de saída, ordem dos resultados, ordem das causas, deduplicação e exceções são os
  **mesmos**, e os **177** cenários vigentes de `tests/test_coverage_decision.py` continuam
  verdes **sem alteração comportamental alguma**. O arquivo recebeu apenas a **reconciliação
  estrutural** da *whitelist* de `test_importa_somente_o_necessario` com a nova arquitetura:
  **entra** `casa77_sdr.fragment_emissibility` e **sai** a dependência **direta**
  `casa77_sdr.response_assertion`, agora consumida **exclusivamente** pela primitiva
  compartilhada. A cadeia passa a ser `coverage_decision` → `fragment_emissibility` →
  `response_assertion`, e **nenhum teste comportamental foi alterado**.
  A **PR #173** apenas criou a **autoridade compartilhada** e, **naquele momento**, deixou
  **`T16`/`R06` aberta**: ela **não** criou *owner* de `R06/F1`, **não** mapeou
  `INFORMAR_CONDICOES_DE_VISITA` — que ali permanecia `()` — e **não** decidiu o desfecho de
  `R06` **não emitível**; **nenhuma superfície conversacional nova foi fechada por ela**.
  **Nesta entrega**, a **rota de ação de T16** já **consome essa autoridade**, conforme
  **`PE-15`**–**`PE-20`** (bloco acima). A primitiva, porém, **permanece independente de
  ação**: ela **não conhece T16**, **não conhece ação** e **não é *owner***; o ***owner* vive no
  `ProjetorEmissao`**. E ***owner* de emissão isolado não é T16 *end-to-end***: a
  **invocação da `FotografiaFragmento` no ciclo** continua **AUSENTE** — a **primitiva de
  montagem** está **materializada e versionada** (§4.4.6), a **chamada dela na rota** não
  —, o **`OrquestradorMotor`** continua **ausente** e a **integração *end-to-end***
  continua **ausente**. **T16 não está
  integralmente concluída.**
- **Limites materiais do projetor nesta versão**: ele consome as ações da **primeira** decisão
  da máquina; **ações produzidas por chamadas posteriores da `MaquinaEstados` não entram nesta
  projeção**; o mapa atual insere **exatamente três** fragmentos, em **três naturezas já
  arbitradas** — **`R03/F1`**, **mandatório puro estático**; **`R05/F1`**, **dupla rota sem
  *bindings*** (**`PE-13`**); e **`R06/F1`**, **dupla rota condicionada à emissibilidade**, com
  ***bindings*** de origem **`YAML`** e **zero `RUNTIME_AUTORITATIVO`**
  (**`PE-15`**–**`PE-20`**) —; **qualquer OUTRO** futuro mapeamento com ***binding***,
  **`ASSERTIVA`** ou **fato de runtime** **exige arbitragem própria**, e **nada é herdado por
  analogia**; e ação com mapa vazio **continua podendo ter obrigação textual pendente**.
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
| **B** — colisão conceitual de nome `RegistroAtendimento` | **ARBITRADA e versionada** (`docs/07` §4.1.1, `B-1`–`B-5`): o **referente comportamental** recebe o nome **`AtualizadorDadosAtendimento`**; a **dataclass** de `persistence.py` é **preservada**; **zero renomeação de código preexistente**, zero alias, zero terceira abstração | **deixou de bloquear** a implementação do componente, que está **materializado e versionado** | `docs/07` §4.1.1, §4.1.8, §12 itens 21 e 26 |
| **C** — índice estruturado `Rxx` × YAML | **materializados**: índice físico e *templates*, **autoridade de status**, ***lookup* operacional**, **`ValidadorConsistenciaBase`**, **`ProjetorEmissao`**, **`SeletorFatos`**, **compositor determinístico por fragmento**, a **montagem canônica de uma emissão**, o **`ValidadorResposta`**, a **infraestrutura estrutural de `R2`** (`docs/07` §4.4.2) e o **produtor determinístico S2-D8** (`docs/07` §4.4.3; ver a linha própria de **S2-D8**). **Pendentes**: **integração *end-to-end* da etapa 10**, **superfícies conversacionais sem unidade aprovada** — **T15 deixou de estar entre elas** (`docs/07` §4.1.5, `PE-13`/`PE-14`), e **T16** saiu **nesta entrega versionada** (`PE-15`–`PE-20`), sem que **T16 esteja integralmente concluída** —, as **ações produzidas por chamadas posteriores da `MaquinaEstados`**, a **evolução futura do `ProjetorEmissao`** para essas fases e a **integração pelo `OrquestradorMotor`** | a **ausência física do índice deixou de ser o bloqueio** e a cadeia já vai do índice à **emissão montada numa única mensagem**; enquanto as capacidades restantes não forem materializadas, o `OrquestradorMotor` e a integração completa **não** devem ser considerados prontos. **`C` não está concluída** | `docs/07` §2.3, §4.1.2, §4.1.3, §4.1.4, §4.1.5, §4.1.6, §4.1.7, §12 itens 19, 10 e 22 |
| **S2-D5** — mensagem conversacional em `aguardando_confirmacao_disponibilidade` antes de `E16` | aberta; resolver na Etapa 6 | não bloqueia | `docs/06` §12 |
| **S2-D7** — `E13` a partir de estado diferente de `encaminhado_humano` | aberta; resolver na Etapa 5 | não bloqueia | `docs/06` §12 |
| **S2-D8** — detecção e classificação de pendências e cobertura de resposta aprovada | contrato arbitrado e **materializado**: infraestrutura estrutural de `R2` (`coverage_map.py`, `coverage_map_load.py`; §4.4.2), **produtor determinístico** (`coverage_decision.py`; §4.4.3) — que consome a **primitiva única de emissibilidade** (`fragment_emissibility.py`; §4.4.5, `FE-1`–`FE-15`), **sem alteração de comportamento público** —, **aplicabilidade de pacote** (`pricing_applicability.py`; §4.4.4) e o **artefato físico** `knowledge/mapa-cobertura.yaml`, com **54/54** assuntos — **33** com cobertura e **21** vazios. Cobertos os eixos **A** e **B**, **`D8-F`**, Classe I/II, os *gates* de **`R05`** e de **preço (`D8-G`)**, **`D8-L4`**, ***witnesses***, `fragmentos_autorizados`, `pendencias_resposta` e **causas** de `E09`. O **conteúdo de `R2` foi concluído nesta capacidade**, e S2-D8 + `R2` **decidem cobertura** quando recebem as entradas estruturadas. **Já materializada e versionada**, fora desta pendência: a **conversão** das causas em **um único `Evento.E09`**, por `src/casa77_sdr/cycle_events.py` (`docs/07` §6.3, `CIE-1`–`CIE-10`). A **agregação** dos produtores distintos e a **montagem de `CondicoesCiclo`** estão **materializadas e versionadas** (`cycle_inputs.py`; §4.1.9). **Ainda ausente**: a execução **dentro do futuro `OrquestradorMotor`** | **deixou de bloquear**: o que resta é a integração do ciclo, registrada em §6 | `docs/07` §4.4.1, §4.4.2, §4.4.3, §4.4.4, §12 item 10; `docs/06` §11 |
| **Etapa 6 — `AtualizadorDadosAtendimento`** | **materializada e versionada**: `src/casa77_sdr/data_update.py`, contrato vivo em `docs/07` §4.1.8 (`AD-1`–`AD-12`). A **condição 1** de §4.4 tem produtor concreto. A **agregação** e a **montagem de `CondicoesCiclo`** estão **materializadas e versionadas** (§4.1.9). **Pendente**: a **coordenação do pipeline** | **`insumo_qualificacao_atualizado` deixou de carecer de produtor**; o que resta é a integração do ciclo, registrada em §6 | `docs/07` §4.1.8, §4.4, §5, §12 item 26 |
| **Produtor de `E07`/`E08`/`E09`** | **materializado e versionado**: `src/casa77_sdr/cycle_events.py`, contrato vivo em `docs/07` §6.3 (`CIE-1`–`CIE-10`). A **agregação** e a **montagem de `CondicoesCiclo`** estão **materializadas e versionadas** (§4.1.9). **Pendente**: a **coordenação do pipeline** | **`E07`, `E08` e `E09` deixaram de carecer de produtor**; o que resta é a integração do ciclo, registrada em §6 | `docs/07` §6.3, §12 item 25; `docs/06` §2.2, §9, §11 |
| **Semântica de handoff + `DetectorHandoff`** | **materializados e versionados**: `src/casa77_sdr/handoff_detection.py`, contrato vivo em `docs/07` §6.3 (`DH-1`–`DH-12`), com a extensão semântica **AJ4**. Cobre os **gatilhos 3–10** de `docs/04`. **Pendente**: a **integração ao ciclo**, que liga o `E18` e os motivos produzidos à `MaquinaEstados` | **`E18` deixou de carecer de produtor**; o que resta é a integração do ciclo, registrada em §6 | `docs/07` §6.3, §12 item 24; `docs/06` §2.1, §9 |
| **S3-D1** — produtor da condição `motivo_encerramento` | produtor **atribuído e materializado**: `src/casa77_sdr/closure_decision.py`, contrato vivo em `docs/07` §6.3 (`S3D1-1`–`S3D1-12`), com a extensão semântica **AJ3**. **Pendente**: a **integração ao ciclo**, que liga `E14` e o motivo produzidos à `MaquinaEstados` | **deixou de ser a ausência de produtor**: o que resta é a integração do ciclo, registrada em §6 | `docs/07` §4.4, §6.3, §12 itens 10 e 23 |
| **Composição dos insumos da máquina** | **materializada e versionada**: `src/casa77_sdr/cycle_inputs.py`, contrato vivo em `docs/07` §4.1.9 (`IC-1`–`IC-12`). Cobre a **agregação** dos eventos de produtores distintos e a **montagem de `CondicoesCiclo`** na **primeira** chamada de um ciclo de **nova mensagem**. **Pendente**: a **coordenação do pipeline** — quando cada etapa roda, com que dados vigentes, a **coordenação do branch E4** já arbitrado e as chamadas da máquina **não** originadas de mensagem nova | **a agregação e a montagem deixaram de faltar**; o que resta é o `OrquestradorMotor`, registrado em §6 | `docs/07` §4.1.9, §4.4, §12 item 27 |
| **E1** — conversa × atendimento × lead | não arbitrada; atravessa identidade, persistência e registro de leads | não bloqueia a especificação vigente | `docs/07` §12 item 13 |
| **E3** — evento novo durante atendimento ativo | aberta; contrato vigente é conservador (`AMBIGUA`) | não bloqueia | `docs/07` §12 item 14 |
| **E4** — tratamento de `SEM_CANDIDATO_ELEGIVEL` | **ARBITRADA E VERSIONADA**: contrato vivo em `docs/07` §7.1 (`E4-1`–`E4-14`), com `docs/06` §4.5 reconciliado. Encerra **sem transição**, preserva o pendente, **tenta** o alerta e marca a chave fora da etapa 13. **Pendente**: a **coordenação** do branch pelo `OrquestradorMotor` | **deixou de bloquear** o `OrquestradorMotor`; o que resta é a coordenação, registrada em §6 | `docs/07` §7.1, §12 item 15; `docs/06` §4.5 |
| **N-a** — integração operacional residual | especificação concluída e fronteiras `M-T`/`M-E`/`M-C`/`M-DT`/`M-AE` materializadas; integração da etapa 13 no pipeline pendente, com bloqueios S4/S5 sem tratamento operacional | bloqueia o pipeline completo | `docs/07` §6.2, §12 item 11 |
| **Limiar temporal de recência** | valor numérico e mecanismo de carga indefinidos; não é dado comercial | bloqueia a integração operacional de `N-a` e o `OrquestradorMotor` | `docs/07` §12 item 18 |
| **N-b** — integração da etapa 4 | contrato arbitrado; fronteira determinística materializada; **produtor não determinístico versionado** (`docs/07` §6.3, `M-PN1`–`M-PN12`) — Anthropic / `claude-sonnet-5`, saída estruturada, canonicalização obrigatória, zero retry, exercitado **offline** pela suíte; os **evals semânticos** e o **smoke** existem e **não foram executados**. **`N-b-RES2` deixou de ser residual**: o produtor de eventos derivados está **materializado e versionado** (`RES2-1`–`RES2-12`), com saída fechada em `E02`/`E03`/`E04`/`E05`/`E06`/`E10`; `E09`, `E18`, `E07`/`E08` e `E14` **continuam fora dele**. A **cadeia operacional** deixou de carecer de fronteira física única: produção, projeção, condição 5 e `N-b-RES2` estão **encadeadas** em `interpretation_stage.py` (`docs/07` §6.3, `EN4-1`–`EN4-12`), **materializadas e versionadas na `main`**. A **coordenação por ciclo** deixou de ser matéria aberta: ela está **ARBITRADA e VERSIONADA nesta entrega** em `CN4-1`–`CN4-12` (`docs/07` §6.3) — ponto único de chamada, reutilização do `ArtefatosInterpretacao`, ordem parcial dos produtores, pré-condições da primeira decisão e propagação intacta da falha. **Pendente**: a **coordenação em runtime**, que **NÃO está materializada** | bloqueia o `OrquestradorMotor` e a integração completa — arbitrar **não** é materializar | `docs/07` §6.3 (`EN4-1`–`EN4-12`, `CN4-1`–`CN4-12`), §12 item 12 |
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

- **C** — índice físico, *templates*, **autoridade de status**, ***lookup* operacional**,
  **`ValidadorConsistenciaBase`**, o **`ProjetorEmissao`**, o **`SeletorFatos`**, o
  **compositor determinístico por fragmento**, a **montagem canônica de uma emissão** e o
  **`ValidadorResposta`** **já concluídos** — a **ausência do *gate* final de integridade
  textual deixou de ser lacuna**. O bloqueio restante é **conectar as capacidades dependentes
  ainda ausentes** — as **superfícies textuais sem unidade aprovada**, a **integração
  residual da etapa 10**, as **ações produzidas por chamadas posteriores da
  `MaquinaEstados`** e a **integração completa pelo `OrquestradorMotor`** (`docs/07` §12,
  item 22). O **item 22 continua parcialmente aberto**: **duas sub-lacunas fecharam** — a
  superfície de **T15**, determinística **nas duas rotas**, fechada na **entrega anterior**
  (`PE-13`, `PE-14`), e, **nesta entrega versionada**, a de **T16** (`PE-15`–`PE-20`), com
  `R06/F1` condicionado à emissibilidade e **zero fragmento** quando não emitível —, e a
  **coleta**, o **formato**, a **retomada**, a
  **incompatibilidade dependente de motivo**, o **reforço de encaminhamento**, as **ações
  posteriores**, o **papel residual do LLM** e a **integração *end-to-end*** **continuam
  abertos**. **`C` não está concluída**. A **`D8-F` de implementação única** (`docs/07`
  §4.4.5) **preparou** a superfície de **T16**, e **esta entrega a fechou como *owner* de
  emissão isolado**: a arbitragem de **`R06/F1` não emitível** está **FECHADA** — **zero
  fragmento** sob **`PE-7`**, **zero `E09`**, **zero `E18`** e **zero nova chamada da
  `MaquinaEstados`**; nem `E09`, nem *handoff*. **T16 não está integralmente concluída**:
  continuam ausentes a **invocação da `FotografiaFragmento` no ciclo** — a **primitiva de
  montagem** está **materializada e versionada** (`docs/07` §4.4.6), a **chamada dela**
  não —, a **coordenação pelo `OrquestradorMotor`**, a **integração *end-to-end*** e a
  **política final da etapa 10 para a obrigação degradada**;
- **S3-D1** — o **produtor** deixou de ser a lacuna: ele está **materializado**. O
  bloqueio restante é a **integração ao ciclo**, que converte o `E14` e o
  `motivo_encerramento` produzidos em insumo efetivo da `MaquinaEstados`;
- **N-b** — a **materialização em runtime** da **coordenação da etapa 4** no ciclo. Nem o
  produtor não determinístico nem **`N-b-RES2`** são mais a lacuna: **ambos estão
  versionados** (`docs/07` §6.3, `M-PN1`–`M-PN12` e `RES2-1`–`RES2-12`). A **cadeia
  operacional** também deixou de faltar — produção, projeção, condição 5 e RES2 estão
  **fisicamente encadeadas** (`interpretation_stage.py`; `docs/07` §6.3, `EN4-1`–`EN4-12`) — e ela está
  **materializada e versionada na `main`**. **Quem a invoca, quando e no máximo uma vez por
  ciclo** deixou de ser matéria aberta: está **ARBITRADO e VERSIONADO nesta entrega** em
  `CN4-1`–`CN4-12` (`docs/07` §6.3). O que resta é a
  **coordenação em runtime**, que **não está materializada**: **este bloqueador permanece**,
  porque o **`OrquestradorMotor` continua ausente**. Continuam **ausentes os demais produtores
  de evento**. **`E14`, `E18`, `E07`, `E08` e `E09` deixaram de faltar**: os seus
  produtores — **`S3-D1`**, o **`DetectorHandoff`** e `src/casa77_sdr/cycle_events.py` —
  estão **materializados e versionados**. Quem **une** eventos de produtores distintos e quem
  **monta `CondicoesCiclo`** **deixaram de faltar**: ambos estão **materializados e
  versionados** (`cycle_inputs.py`; `docs/07` §4.1.9). O produtor de
  **`insumo_qualificacao_atualizado`** — a **etapa 6** — **deixou de faltar**: ele está
  **materializado e versionado**;
- **N-a** — integração operacional da etapa 13, tratamento dos bloqueios S4/S5 e destino do
  alerta operacional;
- **limiar temporal** — valor e mecanismo de carga.

**Concluído, e por isso fora da lista acima**: **S2-D8** e **`R2`** — infraestrutura
estrutural (`docs/07` §4.4.2), produtor determinístico (§4.4.3), aplicabilidade de pacote
(§4.4.4) e o **artefato físico do mapa**, com os 54 assuntos associados. Eles **deixaram de
ser bloqueadores**: dadas as entradas estruturadas, a cobertura é decidida.

**Concluída e versionada** — a **condição 6** deixou de ser a única das
**oito** sem **owner** atribuído: ela está **arbitrada** em `docs/07` §4.4
(`CAL6-1`–`CAL6-8`), com o **owner** na **raiz de composição / adaptador de calendário da
etapa 6** e a **entrada de C7** ***fail-closed*** **materializada e versionada**. Isso
**não remove bloqueador algum
desta lista**: a **coordenação de N-b em runtime**, a **integração ao ciclo** e o
`OrquestradorMotor` continuam exatamente como acima, e a **integração externa real de calendário continua
ausente** — `E16` permanece **futuro** e **`S2-D5` permanece aberta**.

Bloqueia o **uso real** em canal, à parte da integração: **persistência operacional não
volátil**.

**Não são bloqueadores** — **ainda abertas**, porém sem condicionar a integração vigente:
**E1**, **E3**, **S2-D5**, **S2-D7**, unicidade geral de `id_atendimento` e retorno do
controle ao bot.

**`B` não está mais aberta**: ela foi **arbitrada e versionada** (`docs/07` §4.1.1,
`B-1`–`B-5`), e resolveu **somente** a colisão de nome — o **referente comportamental**
passou a ser `AtualizadorDadosAtendimento` e a **dataclass** `RegistroAtendimento`
permanece **intacta**.

A `MaquinaEstados` **não depende** dessas pendências para o contrato já definido: recebe
eventos confirmados e condições já estruturadas.

---

## 7. Próxima ação

**Fechar os pré-requisitos ainda bloqueadores do `OrquestradorMotor`, antes da integração do
ciclo.**

A cadeia determinística já vai do índice à emissão validada, **S2-D8** e **`R2`** decidem
cobertura sobre o artefato aprovado, e a **conversão** de **causa estruturada** em
**`Evento.E09`** já está **materializada e versionada** (§1) — junto com `E07` e `E08`.
A **etapa 6** também já está **materializada e versionada** (§1), e com ela o produtor de
`insumo_qualificacao_atualizado`. A **agregação** dos eventos de produtores distintos e a
**montagem de `CondicoesCiclo`** estão **materializadas e versionadas** (§1), a **cadeia
operacional de N-b** está **materializada e versionada** na `main` (§1) e a sua
**coordenação por ciclo** está **arbitrada e versionada** em `CN4-1`–`CN4-12` (§1) — **sem
runtime**. O que falta é o **ciclo**: ninguém
**liga** interpretação, qualificação, cobertura, seleção, composição, montagem e validação;
e nenhuma decisão **percorre** o pipeline.

**Integrar não é a próxima ação imediata**, porque a integração depende de pendências que
**este mesmo snapshot** ainda registra como abertas em §5 e §6 — entre elas **N-b**,
a **integração ao ciclo** dos produtores já materializados — **`S3-D1`**, o
**`DetectorHandoff`** e o de **`E07`/`E08`/`E09`** —, as matérias
residuais de **N-a** e o **limiar temporal**, o **destino do alerta operacional**, a
**integração externa real de calendário** — cuja **condição 6** já está **arbitrada e
versionada** (§1), sem que o **adaptador da etapa 6 exista** —, as **superfícies
conversacionais sem unidade aprovada** — das quais **T15** saiu em **entrega anterior** e
**T16** sai **nesta entrega versionada** (§1), sem que a **integração *end-to-end*** exista
e sem que a `FotografiaFragmento` seja **invocada no ciclo** — a **primitiva de montagem**
está **materializada e versionada** (§1), a **chamada dela** não —, enquanto as demais
**continuam
abertas** — e,
para
uso em canal real, a **persistência operacional não volátil**.

**O primeiro teste conversacional local ainda NÃO está liberado**: o `OrquestradorMotor`
**continua ausente** e a **coordenação das chamadas da máquina** não existe.

**A ordem em que elas serão fechadas não é decidida aqui** — este arquivo é snapshot, não
plano —, e cada frente será aberta por **novo mandato específico**.

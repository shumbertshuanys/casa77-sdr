# 00 — Estado Atual do Projeto

Documento de estado: registra etapa, subetapa, PRs, commits, testes e próxima ação.
**Não contém dado comercial.** Preço, capacidade, tipo de evento, horário, restrição e
qualquer outra condição vivem exclusivamente em `knowledge/casa77.yaml`.

Atualizado em: 2026-09-07 (**reconciliação documental pós-merge do parser puro de
`caminho_yaml` — PR #131**). Esta entrega é **EXCLUSIVAMENTE DOCUMENTAL**: altera **somente**
este documento, e **não altera código, testes, `knowledge/**`,
`docs/07-arquitetura-motor-respostas.md`, `prompts/**`, `CLAUDE.md`, configuração nem
dependências; **não implementa nada novo**. **A PR #127 deixou de ser a entrega funcional de
código mais recente**: o **PR #131** integrou à `main` o **parser puro e determinístico da
gramática de `caminho_yaml`** — a **linha 1 de `CY13`**. **Commit funcional
`cee95ebb6a725c3b91595589591fefa650d64196`** (`feat: add caminho_yaml parser`, **sem body, sem
trailer**), **parent `51fa44c4a9f5b65505f7668c1ce05e8b8f97dd68`**, **merge commit
`6ae5cd829bb6eb9f4acfc60a061ee9b7e6d36180`** (merge commit **normal**, dois parents:
`51fa44c4a9…` e `cee95ebb6a…`; **zero squash, zero rebase, zero auto-merge**), branch de origem
`feat/caminho-yaml-parser`. **ELA NÃO É DENOMINADA `C15`, NÃO É `E15`, NÃO É `C-A6`, NÃO CRIA A
3B.8 e NÃO CRIA IDENTIFICADOR NORMATIVO NOVO** — é, tão somente, a **entrega funcional de
código mais recente integrada**; a **composição total de status (PR #127) passa a histórico
funcional imediatamente anterior**, com o seu registro **preservado**. **Escopo**: **dois
arquivos novos** — `src/casa77_sdr/response_yaml_path.py` (**+330**) e
`tests/test_response_yaml_path.py` (**+1007**) —, **2 arquivos, +1337 / −0**, **zero arquivo
preexistente alterado**, **zero `docs/**`**, **zero `knowledge/**`**, **zero `prompts/**`**,
**zero configuração**, **zero dependência**, **zero alteração de `casa77_sdr/__init__.py`** e
**zero alteração de `src/casa77_sdr/response_index.py`**. **Contrato**: módulo
`casa77_sdr.response_yaml_path`, com a fronteira pública
`analisar_caminho_yaml(caminho: str) -> tuple[bool, tuple[tuple[str, tuple[str, str] | None], ...]]`,
a exceção pública única **`CaminhoYamlInvalido`** e **`__all__` de exatamente dois nomes** —
`["CaminhoYamlInvalido", "analisar_caminho_yaml"]` —, **sem DTO**, **sem dataclass**, **sem
Enum** e **sem export pelo package root**. **Saída**: `(relativo, segmentos)` — a **decomposição
imutável já validada** —, com `relativo` `False` para **absoluto** e `True` para **relativo**, e
`segmentos` como `tuple` de pares `(chave, seletor)`, sendo `seletor` igual a **`None`** ou ao
par `(chave_seletora, literal)`; **só `bool`, `str`, `tuple` e `None`**. **`@` isolado devolve
`(True, ())`**, sem inventar segmento. **Alcance exato — SOMENTE a linha 1 de `CY13`**: o parser
recebe **`str` exata** (subclasse de `str` **recusada**), julga **gramática e canonicalidade**,
distingue **absoluto × relativo**, devolve a **decomposição imutável**, aceita **`@` isolado**,
julga o **seletor**, **rejeita chave exclusivamente numérica como não endereçável** (tanto chave
de segmento quanto chave seletora) e **permite literal seletor exclusivamente numérico** —
e **não lê YAML**, **não lê índice** e **não conhece fato comercial algum**. **Falhas
materializadas**: exceção pública única `CaminhoYamlInvalido`, com **três** categorias fechadas
— **`tipo_invalido`**, **`forma_invalida`** e **`chave_nao_enderecavel`** — e **seis**
localizadores semânticos fechados — **`caminho`**, **`segmento`**, **`seletor`**, **`chave`**,
**`chave_seletora`** e **`literal`** —, na forma **`<categoria>: <localizador>`** e **sem eco do
conteúdo recebido** (zero caminho bruto, fragmento, caractere, `repr`, tipo concreto, posição,
índice, *offset*, comprimento ou cardinalidade). **Pureza**: import único
`from __future__ import annotations` — **zero `re`**, **zero `unicodedata`**, **zero YAML**,
**zero JSON**, **zero I/O**, **zero *filesystem***, **zero rede**, **zero ambiente**, **zero
*locale***, **zero relógio**, **zero aleatoriedade**, **zero dependência interna ou externa**,
**zero `try`/`except`**, **zero `raise from`**, **zero `eval`/`exec`**, **zero `dict`/`set`** e
**zero estado mutável de módulo**; a entrada **não é alterada** e chamadas repetidas produzem
**exatamente** o mesmo resultado. **ESTADO DE `CY13` APÓS ESTA INTEGRAÇÃO**: **linha 1 —
parser da gramática = MATERIALIZADA**, via `src/casa77_sdr/response_yaml_path.py`; **linha 2 —
validação estrutural contextual = NÃO MATERIALIZADA**, pois **ainda não existe** componente que
valide **relativo somente em fragmento com `itera_sobre`** nem **`@` proibido no próprio
`itera_sobre`**; **linha 3 — resolver = NÃO MATERIALIZADA**, pois **ainda não existe**
componente que percorra o YAML, resolva chaves, execute seletores, determine **zero / um /
múltiplos *matches*** ou devolva terminal factual. **Baseline funcional corrente: `4741 passed`
/ Python 3.14.5**, sob **`-W error`**, com **`147 passed`** no direcionado da nova fronteira —
delta **+147** sobre os **`4594 passed`** anteriores (**4594 + 147 = 4741**), **zero failures,
zero errors, zero warnings** e **nenhum teste preexistente alterado, removido ou pulado**. **A
suíte nova é inteiramente SINTÉTICA** e **nenhum teste lê o corpus versionado**. Esses números
são **evidência da entrega funcional do PR #131**, e **NÃO** uma execução desta reconciliação:
**nenhum `pytest` foi executado aqui**, porque **zero código, zero teste e zero `knowledge/**`
mudaram**. **Não houve CI configurado** para a PR #131 nem para o merge commit — *statuses* = 0,
*workflow runs* = 0 — **AUSÊNCIA DE CI/CHECKS — NÃO FALHA DE CI**. **A PR #131 NÃO**: implementa
a validação contextual de `itera_sobre`; implementa o resolver; lê YAML; materializa **`C-7`**;
arbitra *placeholder*; arbitra `hora`; cria índice; cria *binding* físico; cria `ASSERTIVA`
nova; executa a bijeção; satisfaz **`C-A1-ST6`**–**`C-A1-ST10`**; migra **`C-11`**; nem cria
`C15`, `E15`, `C-A6` ou a **3B.8**. **ESTADO CORRENTE DE `C`**: a **gramática de `caminho_yaml`
continua ARBITRADA DOCUMENTALMENTE**; o **parser da gramática está MATERIALIZADO**; a
**validação contextual é INEXISTENTE**; o **resolver é INEXISTENTE**; o **índice físico
`knowledge/indice-respostas-aprovadas.yaml` continua INEXISTENTE**; ***placeholder* continua
ABERTO**; **`hora` continua pendência normativa separada**; **`C-7` continua NÃO
MATERIALIZADA**; **`C-A1-ST6`–`C-A1-ST10` continuam NÃO satisfeitas**; **`C-11` NÃO migrou** e a
**autoridade de status continua no Markdown aprovado**; **a 3B.8 continua INEXISTENTE**; e
**`C` continua ARBITRADA / NÃO MATERIALIZADA**. **PRÓXIMA AÇÃO**: **retornar ao GPT após a
integração desta reconciliação para nova auditoria e priorização** — **nenhuma próxima
microentrega técnica é eleita aqui**, e **não** se afirma que a próxima entrega será a validação
contextual, o resolver, *placeholder*, `hora`, **C-7** ou o índice. O **item documental 108**
abaixo **NÃO é "subetapa 108"**, **NÃO é `C15`**, **NÃO é `E15`**, **NÃO é `C-A6`**, **NÃO é
identificador normativo** e **NÃO cria a 3B.8** — registra **exclusivamente** a integração
funcional da PR #131.

**Atualização anterior — 2026-09-07 (micro-arbitragem documental da gramática de
`caminho_yaml`), preservada como registro daquele momento.** Aquela entrega é
**EXCLUSIVAMENTE DOCUMENTAL / NORMATIVA**: altera **somente**
`docs/07-arquitetura-motor-respostas.md` e este documento, e **não altera código, testes,
`knowledge/**`, `prompts/**`, `CLAUDE.md`, configuração nem dependências. **A GRAMÁTICA DE
`caminho_yaml` DEIXA DE ESTAR ABERTA**: ela está agora **ARBITRADA DOCUMENTALMENTE**, na
alternativa aprovada **`A2`** — **`caminho_yaml` permanece semanticamente uma `str`, com
CAMINHO ABSOLUTO SEM MARCADOR e CAMINHO RELATIVO EXPLICITAMENTE MARCADO POR `@`**. **A
gramática governa a `str` DEPOIS do parsing YAML**, e **não** decide sintaxe de arquivo, estilo
de serialização, *loader* ou qualquer aspecto físico do futuro índice. **Duas formas semânticas,
e apenas duas**: a **absoluta**, **sem marcador**, cuja raiz é o **mapeamento raiz de
`knowledge/casa77.yaml` já carregado**, permitida **fora** de `itera_sobre` **e também dentro**
de fragmento que o possua; e a **relativa**, marcada por **`@`** exatamente na posição inicial,
cuja raiz é o **item corrente** da coleção percorrida por `itera_sobre`, permitida **somente**
em *binding* de fragmento que **declare** `itera_sobre` — relativo **sem** `itera_sobre` é
***FAIL-CLOSED* estrutural**. **A forma é sempre explícita na própria `str`** e **o contexto
jamais transforma silenciosamente absoluto em relativo**. **`C-4h` e `C-A1-S2` permanecem
literais**: `C-4h` continua dizendo que os *bindings* do item **PODEM** usar caminho relativo, e
`C-A1-S2` **disciplina** a disponibilidade e a semântica dos relativos durante a iteração **sem**
tornar todos os *bindings* obrigatoriamente relativos — **absolutos e relativos podem coexistir**
num mesmo fragmento com `itera_sobre`. **`C-A1-S1` continua literal**: **seleção posicional
permanece PROIBIDA**. **Gramática**: `caminho ::= caminho_absoluto | caminho_relativo`;
`caminho_absoluto ::= segmento ( "." segmento )*`; `caminho_relativo ::= "@" ( "." segmento )*`;
`segmento ::= chave seletor?`; `seletor ::= "[" chave "=" literal "]"`; **chave** é `NOME`
**exceto se composta exclusivamente por dígitos**; **literal** é `NOME`; e `NOME` é um ou mais
caracteres de `A-Z`, `a-z`, `0-9` e `_`. **Alfabeto semântico permitido, e nada além**: `A-Z`,
`a-z`, `0-9`, `_`, `.`, `[`, `]`, `=` e `@`. **Canonicalidade semântica**: ***whitespace*
proibido**, **aspas como caracteres do valor proibidas**, ***escape* inexistente**, **Unicode
não ASCII proibido**, **caixa significativa**, **zero normalização, `casefold`, coerção ou
tolerância**; são **inválidos** o `.` final, o segmento vazio, o seletor vazio, a chave seletora
vazia, o literal vazio, o `@` fora da posição inicial e **dois seletores no mesmo segmento**.
**YAML físico × valor semântico**: como `@` **não pode iniciar um *plain scalar* YAML**, um
caminho relativo deverá ser serializado **com *quoting*** no futuro arquivo do índice — as
**aspas pertencem à serialização e NÃO à `str` nem à gramática**, e **aspas simples × duplas
NÃO são decididas** aqui. **Literal seletor é sempre `str`** — restrição **deliberada** do MVP,
conteúdo em `[A-Za-z0-9_]+`, **zero inferência** de inteiro, boolean, `null` ou outro tipo YAML,
com comparação futura **literal, por `str`, sem coerção**. **Serialização dos identificadores no
YAML comercial**: um identificador estrutural usado por `caminho_yaml` **DEVE resultar em `str`
depois do parsing** de `knowledge/casa77.yaml`; se um futuro identificador de **`MD-18`** tiver
conteúdo que, como *plain scalar*, seja lido pelo *loader* como número, boolean, `null` ou outro
tipo não-`str`, ele **DEVERÁ ser serializado com *quoting*** — exemplo **apenas sintético**, um
identificador semântico `"2026"` precisa **permanecer `str`**. **`knowledge/casa77.yaml` NÃO foi
alterado** e **nenhum identificador novo foi criado**. **Chave exclusivamente numérica**: uma
chave YAML textual `"123"` **não é semanticamente uma posição**, mas a gramática do MVP
**deliberadamente não a torna endereçável** — **chave só de dígitos é forma inválida** —, por
**fechamento conservador**, **auditabilidade estática** e **compatibilidade com a materialização
vigente de `C-A1-S1` em `E1`**; **não se escreve nem se lê daqui que "chave numérica = posição"**.
**Seletor**: `[chave=literal]`, **no máximo um por segmento**, permitido em absoluto, relativo e
`itera_sobre` absoluto; **proibidos** `[0]`, posição, `first`, `last`, *fallback*, busca parcial,
*substring*, similaridade e inferência; **zero *matches* → *FAIL-CLOSED***, **um → continua**,
**mais de um → *FAIL-CLOSED***. **`@` isolado** é caminho relativo **válido** e significa **o
próprio item corrente**, mantendo expressável a futura iteração sobre coleção de escalares —
**sem afirmar que o corpus atual use esse caso**. **`itera_sobre` — mínimo inseparável**: é
`str`; usa a **forma ABSOLUTA** da mesma gramática-base; **`@` é proibido** nele; precisa
**resolver para coleção**; admite **seletores estruturais**; **mapa, escalar ou `null` como
terminal é *FAIL-CLOSED* estrutural**; **não é `C-7`**; e **o item atual torna-se a raiz dos
*bindings* relativos** — **sem decidir** ordem, coleção vazia, composição textual, repetição de
*placeholder*, propagação de erro entre itens ou execução operacional. **Três responsabilidades
distintas** ficam registradas e **nenhuma é implementada**: o **parser da gramática** (sem YAML
factual), a **validação estrutural do índice** (sem YAML factual) e o **resolver** (contra o
YAML já carregado). **Terminal**: ao alcançar o nó terminal a resolução é **SUCESSO** e o valor
é devolvido **como está** — escalar, lista, mapa ou `null` —, e a admissibilidade posterior
pertence a **`C-5`**, **`C-6`** e **`C-7`**; **nenhum juiz adicional de tipo terminal é criado**.
**`C-7` é preservada e NÃO é reaberta nem materializada**. **`ASSERTIVA` e `RENDERIZADO` de
origem `YAML` usam a MESMA gramática**, com a diferença ocorrendo **depois da resolução** —
**nenhuma gramática paralela**. **`RUNTIME_AUTORITATIVO` continua PROIBINDO `caminho_yaml`** e
usando **apenas** `fato_runtime`. **`E1` continua INALTERADO**:
`src/casa77_sdr/response_index.py` valida a estrutura básica e **parte** da proibição posicional,
**não fecha a gramática completa**, e **nada foi removido, alterado ou migrado**, **nenhum teste
foi tocado**. **Categorias de *FAIL-CLOSED* são apenas CONCEITUAIS** — sintaxe, estrutura do
índice e resolução —, e **NÃO** foram definidos classe Python, exceção concreta, mensagem,
herança, função, módulo, API ou precedência técnica concreta. **Os rótulos locais `CY1`–`CY14`
existem SOMENTE como rastreabilidade interna do bloco e NÃO são normativos fora dele**; **`C-A6`
NÃO EXISTE** e **nenhuma subetapa, `C15`, `E15` ou 3B.8 foi criada**. **Todos os exemplos são
SINTÉTICOS**: **nenhum identificador, valor, preço, capacidade, horário ou condição comercial
real é reproduzido**. **Evidência estrutural sanitizada do *snapshot* atual, registrada como
EVIDÊNCIA e NÃO como norma**: o YAML vigente é **compatível** com a gramática; há **5** coleções
de mapas — **4 com identificador estrutural utilizável** e **1 sem** —, **12** listas de
escalares, e **nenhum *binding* aprovado atual exige `itera_sobre`**. **ESTADO APÓS ESTA
MICRO-ARBITRAGEM**: **gramática de `caminho_yaml` = ARBITRADA DOCUMENTALMENTE / NÃO
MATERIALIZADA**; **índice físico INEXISTENTE**; **parser INEXISTENTE**; **resolver
INEXISTENTE**; ***placeholder* ABERTO**; **`hora` = pendência separada**; **`C-7` NÃO
MATERIALIZADA**; **`C-A1-ST6`–`C-A1-ST10` NÃO satisfeitas**; **`C-11` NÃO migrada**; **`C`
continua ARBITRADA / NÃO MATERIALIZADA**; **3B.8 INEXISTENTE**. **ZERO CÓDIGO, ZERO TESTE e
ZERO `knowledge/**`** e **NENHUM `pytest` FOI EXECUTADO AQUI** — a **baseline permanece `4594
passed` / Python 3.14.5**, evidência da entrega funcional do **PR #127**, e a **última entrega
funcional de código continua sendo a composição total de status**. **PRÓXIMA AÇÃO**: **retornar
ao GPT para auditoria da micro-arbitragem integrada à PR antes de qualquer planejamento técnico
posterior** — **nenhuma implementação foi eleita**, e ***placeholder*, parser, resolver, índice,
`C-7` e `hora` NÃO foram iniciados**. O **item documental 107** abaixo **NÃO é "subetapa 107"**,
**NÃO é `C15`**, **NÃO é `E15`**, **NÃO é identificador normativo** e **NÃO cria a 3B.8** —
registra **exclusivamente** esta micro-arbitragem.

**Atualização anterior — 2026-09-07 (reconciliação do estado corrente de `C` na tabela de
pendências técnicas em aberto), preservada como registro daquele momento.** Aquela entrega é
**EXCLUSIVAMENTE DOCUMENTAL**, alterou **uma única linha** de `docs/00-estado-atual.md`
(**`+1 / −1`**) e está integrada à `main` pelo **PR #129** — commit
`ed7d60edbe833c0ce820c092e10404de45ce393f`, merge
`66ca40f355ed58a6aaebf5079dd0758cc18387ad`, branch de origem
`docs/reconcile-current-c-materialization-state`. Ela reconciliou a leitura corrente da
pendência `C` com os registros posteriores já existentes — **`C-A2-N9`**, **`C-A2-N10`**,
**`C-A2-N11` (16/16)** e **`C-A2-N12`** = **CUMPRIDAS**, **`FE-11b` = APLICADA / MATERIALIZADA
POR REMOÇÃO** e **`FE-11a` = APLICADA / RECONCILIADA** —, **preservando integralmente os
registros históricos equivalentes** e **sem materializar coisa alguma**.

**Atualização anterior — 2026-09-07 (reconciliação documental pós-merge da composição total
determinística de status dos fragmentos emitíveis), preservada como registro daquele momento.**
Aquela entrega é **EXCLUSIVAMENTE
DOCUMENTAL**: altera **somente** este documento, e **não altera código, testes,
`knowledge/**`, `docs/07-arquitetura-motor-respostas.md`, `prompts/**`, `CLAUDE.md`,
configuração nem dependências. **A PR #124 deixou de ser a entrega funcional de código mais
recente**: o **PR #127** integrou à `main` uma **nova entrega funcional de código** — a
**composição total determinística de status dos fragmentos emitíveis**. **Commit funcional
`24d2b0fef6a08c26e751f8eb8bb70943b30c0339`** (`feat: add total fragment status composition`,
**sem body, sem trailer**), **merge commit
`00c45e9b95f233bc7aa0f9666e090208994fb190`** (merge commit **normal**, dois parents:
`9ace0f5e47…` e `24d2b0fef6…`; **zero squash, zero rebase, zero auto-merge**), branch de origem
`feat/total-fragment-status-composition`. **ELA NÃO É DENOMINADA `C15`, NÃO É `E15`, NÃO CRIA A
3B.8 e NÃO CRIA IDENTIFICADOR NORMATIVO NOVO** — é, tão somente, a **entrega funcional de
código mais recente integrada**; a **associação física determinística de seção e fragmentos
(PR #124) passa a histórico funcional imediatamente anterior**, com o seu registro
**preservado**. **Escopo**: **dois arquivos novos** —
`src/casa77_sdr/response_status_composition.py` (**+234**) e
`tests/test_response_status_composition.py` (**+1606**) —, **2 arquivos, +1840 / −0**, **zero
arquivo preexistente alterado**, **zero `docs/**`**, **zero `knowledge/**`**, **zero
`prompts/**`**, **zero configuração**, **zero dependência** e **zero alteração do package
root**. **Contrato**: módulo `casa77_sdr.response_status_composition`, com a fronteira pública
única `compor_status_dos_fragmentos(texto: str) -> tuple[tuple[str, str], ...]` e **`__all__` de
exatamente um nome** — `["compor_status_dos_fragmentos"]` —, **sem classe alguma**, **sem
exceção pública nova**, **sem DTO**, **sem dataclass**, **sem Enum** e **sem export pelo package
root**. A fronteira é **pura e determinística**, recebe o **texto já em memória** e não tem
**I/O**, ***filesystem***, YAML, JSON, rede, LLM nem **conhecimento comercial**. **Saída**: um
par `(token_canonico, status_canonico)` por **OCORRÊNCIA FÍSICA** de fragmento emitível, na
**ordem física do documento**, **preservando duplicidades**; documento vazio ou sem `## Rxx`
devolve `tuple()`; o status pertence **exclusivamente** ao vocabulário fechado de **`C-3`**.
**Fontes de status, nenhuma reimplementada**: **`ST1`–`ST3`** são resolvidos **exclusivamente**
por `propagar_status` — a **C13 permanece a autoridade da propagação e da tradução**, e
**nenhuma tabela foi duplicada**; **`PARCIAL`** é resolvido **exclusivamente** por
`extrair_status_por_fragmento` — a **C14 permanece a autoridade do status explicitamente
declarado**, e **a associação token/status sob `PARCIAL` é HERDADA do contrato da C14**, jamais
reimplementada, sem segunda caminhada `PM`; **rótulo `G2` desconhecido** continua **`G2`
válido, literal, opaco, sem tradução automática e com status NÃO RESOLVIDO por `SP5`**, e a
composição **FALHA FECHADA** via `StatusNaoCanonicalizavel`, que **sobe intacta** — **zero
retorno parcial**, **zero omissão**, **zero `None`**, **zero sentinela**, **zero quarto
status**, e o cabeçalho **não** se torna inválido. **SP5 FAIL-CLOSED ESTÁ MATERIALIZADA NESTA
FRONTEIRA.** **Ordem funcional**: **1.** `associar_fragmentos_a_secao(texto)`; **2.**
`extrair_status_por_fragmento(texto)`, **INCONDICIONAL**; **3.** `I1`; **4.** caminhada pelas
instâncias físicas; **5.** C14 sob `PARCIAL`; **6.** C13 nos demais rótulos; **7.** `I2`; **8.**
`I3`; **9.** retorno. **Precedência**: `C8` → `C12` → `C14`/`PM` → `I1` → `SP5` → `I2`/`I3` —
**uma falha `PM` fisicamente posterior vence um rótulo `SP5` anterior porque a C14 percorre o
documento integralmente antes da caminhada local**. **Invariantes internos**: **`I1`** verifica
**compatibilidade de cobertura e de ordem** entre as ocorrências `PARCIAL` esperadas pela
associação física e o fluxo da C14 — e **NÃO reprova nem redefine a associação interna
token/status já produzida pela C14**; **`I2`** verifica **cobertura total** — nenhuma ocorrência
omitida, nenhuma inventada, ordem física preservada; **`I3`** verifica que **todo status
pertence a `C-3`** (`APROVADO`, `AGUARDA_APROVACAO`, `BLOQUEADO`). Falha em `I1`, `I2` ou `I3`
produz **`RuntimeError("invariante_estrutural")`** — **defeito interno**, **nunca** exceção
pública, e **único `raise` originado pelo módulo**. **Homônimos**: a suíte cobre seções
homônimas, tokens textualmente repetidos, **duas instâncias `PARCIAL` homônimas com o MESMO
token e status DIFERENTES**, **três instâncias `PARCIAL` homônimas com status distintos** e a
mistura `PARCIAL` + `ST1` homônimas — **zero dedup**, **zero agrupamento por `Rxx`**, ordem
física preservada e **a posição não é identidade** (**`C-A5-I5`**). **Baseline funcional
corrente: `4594 passed`**, com **`117 passed`** no direcionado da nova fronteira, em **Python
3.14.5** — delta **+117** sobre os **`4477 passed`** anteriores (**4477 + 117 = 4594**),
**executados sob `-W error`**, **zero failures, zero errors, zero warnings** e **nenhum teste
preexistente alterado ou removido**; as vizinhanças foram reexecutadas com **`134 passed`**
(associação física), **`243 passed`** (C14), **`397 passed`** (C13), **`299 passed`** (C12) e
**`201 passed`** (C8), todas **inalteradas**. **A suíte nova é inteiramente SINTÉTICA** e
**nenhum teste persistente contra o corpus foi criado**. Esses números são **evidência da
entrega funcional do PR #127**, e **NÃO** uma execução desta reconciliação: **nenhum `pytest`
foi executado aqui**, porque **zero código, zero teste e zero `knowledge/**` mudaram**. **Não
houve CI configurado** para a PR #127 nem para o merge commit — *statuses* = 0, *workflow runs*
= 0 — **AUSÊNCIA DE CI/CHECKS — NÃO FALHA DE CI**. **Evidência read-only não persistente do
corpus**, registrada como evidência da entrega funcional e **NÃO como norma nem como teste**:
executada uma vez contra `knowledge/respostas-aprovadas.md`, **inalterado** e byte-a-byte no
blob `3a30fe764b80902227fdefb9282f3916650e4f17`, a fronteira devolveu **37 pares**, **37 tokens
distintos**, com agregados **`APROVADO`: 35** e **`AGUARDA_APROVACAO`: 2** — **nenhum conteúdo
comercial é reproduzido**, **o corpus não foi alterado**, essa evidência **NÃO satisfaz
automaticamente `C-A1-ST8`** e **NÃO migra autoridade**. **A PR #127 NÃO**: satisfaz
`C-A1-ST8`; cria índice; executa a bijeção física real; implementa *bindings*; implementa
`ASSERTIVA`; define *placeholder*; define `caminho_yaml`; define `hora`; resolve **C-7**; cria
*renderer*; integra *runtime*; migra a autoridade de status; satisfaz automaticamente
**`C-A1-ST6`**, **`C-A1-ST7`**, **`C-A1-ST8`**, **`C-A1-ST9`** ou **`C-A1-ST10`**; nem cria a
**3B.8**. **`C-A1-ST8` NÃO É DECLARADA SATISFEITA**: a composição materializa a **fronteira
técnica** capaz de resolver o status total **do texto recebido**, mas `ST8` continua exigindo
**prova e auditoria próprias** sobre os insumos canônicos e **dentro dos gates de migração** —
essa decisão **não é antecipada aqui**. **A autoridade de status continua NÃO MIGRADA**
(**`C-11`**), **nenhum índice foi criado** e **nenhuma bijeção foi executada**. **COMPOR STATUS
NÃO É MATERIALIZAR `C`** — portanto **`C` continua ARBITRADA / NÃO MATERIALIZADA**. **PRÓXIMA
AÇÃO**: **após a integração desta reconciliação, auditar a pendência seguinte de `C` a partir do
estado canônico atualizado** — **nenhuma implementação é eleita aqui**, e **não** se afirma que
a próxima ação seja `ST8`, índice, *placeholder*, `caminho_yaml`, `hora`, **C-7**, *bindings*,
`ASSERTIVA` ou *renderer*. O **item documental 106** abaixo **NÃO é "subetapa 106"**, **NÃO é
`C15`**, **NÃO é `E15`**, **NÃO é identificador normativo** e **NÃO cria a 3B.8** — registra
**exclusivamente** a integração funcional da PR #127.

**Atualização anterior — 2026-09-07 (micro-arbitragem documental do comportamento da futura
composição total de status diante de `SP5`), preservada como registro daquele momento.** Aquela
entrega é **EXCLUSIVAMENTE DOCUMENTAL / NORMATIVA**:
altera **somente** `docs/07-arquitetura-motor-respostas.md` e este documento, e **não altera
código, testes, `knowledge/**`, `prompts/**`, `CLAUDE.md`, configuração nem dependências. **A
MICRO-ARBITRAGEM SOBRE O COMPORTAMENTO DA FUTURA COMPOSIÇÃO TOTAL DIANTE DE `SP5` DEIXA DE
ESTAR NÃO RESPONDIDA**: ela está agora **DECIDIDA DOCUMENTALMENTE nesta branch/PR**. **A
DECISÃO É FAIL-CLOSED NA FRONTEIRA DE COMPOSIÇÃO TOTAL**, com **ZERO RETORNO PARCIAL**: quando
uma futura fronteira **cujo contrato seja resolver e devolver o status de TODOS os fragmentos
emitíveis** encontrar fragmento sob seção cujo rótulo satisfaça `G2` mas **não** pertença a
`ST1`–`ST3` e **não** seja `PARCIAL`, o fragmento **permanece NÃO RESOLVIDO por `SP5`** e a
composição total **falha fechada** — **sem devolver resultado parcial**, **sem omitir
silenciosamente o fragmento**, **sem marcador ou valor de ausência**, **sem valor sentinela**,
**sem quarto status**, **sem converter o rótulo** e **sem tornar o cabeçalho `G2` inválido**.
**UM RETORNO BEM-SUCEDIDO DA COMPOSIÇÃO TOTAL NÃO PODE COEXISTIR COM FRAGMENTO NÃO RESOLVIDO
POR ESSE RAMO.** **Duas alternativas foram expressamente REJEITADAS**: a **omissão
silenciosa** e a **representação explícita de ausência em retorno bem-sucedido** (`None`,
sentinela, quarto valor, status especial ou estrutura de "não resolvido" coexistindo com
sucesso total) — esta segunda rejeição valendo **para a fronteira de composição TOTAL**, sem
impedir que **outras APIs futuras, com OUTRO contrato**, representem estado não resolvido de
outra forma. **`SP5` CONTINUA SEMANTICAMENTE INTACTA**: o rótulo desconhecido **continua `G2`
válido, literal e opaco**, **não** é corrigido, **não** é normalizado, **não** é inferido, e o
seu status **permanece NÃO RESOLVIDO** — comportamento **arbitrado**, jamais lacuna.
**`PARCIAL` continua EXPRESSAMENTE FORA desse ramo**, sob **`C-A1-ST4`**, **`SP4`**,
**`PM1`–`PM12`**, o **regime exclusivo de `status-fragmento`** e a **C14**: na composição total
futura ele é resolvido **exclusivamente** pelas declarações explícitas válidas de
`status-fragmento`, **sem propagação automática**, e, quando houver **violação do contrato já
materializado da C14** — incluindo **valor inválido**, **declaração órfã** ou **ausência da
declaração obrigatória** —, as **falhas já existentes da C14 continuam prevalecendo segundo a
sua precedência própria** — **nenhuma semântica nova de `PARCIAL` foi criada**.
**NENHUMA EXCEÇÃO CONCRETA FOI DESENHADA**: nome de classe, mensagem, categorias,
localizadores, herança, propagação de exceção existente × criação de exceção nova e
precedência entre falhas de composição ainda não desenhadas **continuam NÃO DECIDIDOS**.
**`C-A1-ST8` continua literal — status de TODOS os fragmentos resolvidos — e NÃO é satisfeita
por esta arbitragem**: ela apenas impede que uma composição total **declare sucesso** enquanto
houver fragmento não resolvido pelo ramo desconhecido de `SP5`, e a satisfação de `ST8`
continuará exigindo **execução e auditoria próprias**. **Evidência estrutural do corpus atual,
NÃO fundamento normativo**: **30** seções `Rxx` — **25** com rótulo de `C-A1-ST1`, **2** de
`C-A1-ST2`, **2** de `C-A1-ST3`, **1** `PARCIAL` e **0** com outro rótulo `G2` válido —, com
`knowledge/respostas-aprovadas.md` **inalterado**, byte-a-byte no blob
`3a30fe764b80902227fdefb9282f3916650e4f17`; **a regra permanece válida ainda que um futuro
corpus aprovado contenha outro rótulo `G2` válido**. **ZERO CÓDIGO IMPLEMENTADO, ZERO TESTE,
ZERO `knowledge/**`** e **NENHUM `pytest` FOI EXECUTADO AQUI** — a **baseline permanece `4477
passed` / Python 3.14.5**, que é **evidência da entrega funcional do PR #124** e **não** uma
execução desta arbitragem. **`C` CONTINUA ARBITRADA / NÃO MATERIALIZADA.** **PRÓXIMA AÇÃO**:
**após a integração desta arbitragem, retornar ao Claude Desktop para produzir o plano técnico
fechado da composição total de status** — **a implementação NÃO está pronta** e **não é
declarada pronta antes da integração desta decisão**. O **item documental 105** abaixo **NÃO é
"subetapa 105"**, **NÃO é `C15`**, **NÃO é `E15`**, **NÃO é identificador normativo** e **NÃO
cria a 3B.8** — registra **exclusivamente** esta micro-arbitragem.

**Atualização anterior — 2026-09-06 (reconciliação documental pós-merge da associação física
determinística de seção e fragmentos), preservada como registro daquele momento.** Aquela
entrega é **EXCLUSIVAMENTE DOCUMENTAL**: altera
**somente** este documento, e **não altera código, testes, `knowledge/**`,
`docs/07-arquitetura-motor-respostas.md`, `prompts/**` nem `CLAUDE.md`. **A PR #120 deixou de
ser a entrega funcional de código mais recente**: o **PR #124** integrou à `main` uma **nova
entrega funcional de código, posterior à C14** — o **associador determinístico de fragmentos
emitíveis à sua instância física de seção `Rxx` e ao rótulo literal do cabeçalho**. **Commit
funcional `0e41165406c3a9261a1fcc8d0f9c600b0469e730`** (`feat: add deterministic response
section membership`), **merge commit `ecaf0a2b3a594f8fedd10f708461ad2eeb18e086`** (merge commit
**normal**, dois parents: `c62c6b0241…` e `0e41165406…`; **zero squash, zero rebase**), branch
de origem `feat/c-section-membership`. **ELA NÃO É DENOMINADA `C15`, NÃO É `E15`, NÃO CRIA A
3B.8 e NÃO CRIA IDENTIFICADOR NORMATIVO NOVO** — é, tão somente, a **entrega funcional de
código mais recente integrada**; a **C14 passa a histórico funcional imediatamente anterior**,
com o seu registro **preservado**. **Escopo**: **dois arquivos novos** —
`src/casa77_sdr/response_section_membership.py` (**+371**) e
`tests/test_response_section_membership.py` (**+1269**) —, **2 arquivos, +1640 / −0**, **zero
arquivo preexistente alterado**, **zero `docs/**`**, **zero `knowledge/**`**, **zero
configuração** e **zero dependência**. **Contrato**: módulo
`casa77_sdr.response_section_membership`, com a fronteira pública única
`associar_fragmentos_a_secao(texto: str) -> tuple[tuple[str, str, tuple[str, ...]], ...]` e
**`__all__` de exatamente um nome** — `["associar_fragmentos_a_secao"]` —, **sem exceção
pública nova** (o módulo **não declara classe alguma**), **sem export pelo package root**,
**sem DTO** e **sem dataclass**. **Saída**: `(Rxx, rotulo_literal, tokens)`, **uma entrada por
INSTÂNCIA FÍSICA** de seção `## Rxx`, na **ordem física do documento**, com os tokens
canônicos `<Rxx>/<id>` **daquela instância** na ordem física em que aparecem; documento vazio
ou sem `## Rxx` devolve `tuple()`. **Seções homônimas permanecem instâncias separadas**, com
**tokens textualmente repetidos preservados** — **zero consolidação por valor de `Rxx`, zero
dedup, zero agrupamento** —, e **a posição da entrada é apenas ordem de leitura, jamais
identidade** (**`C-A5-I5`**). **`C12` é o primeiro portão e `C8` é satisfeito
TRANSITIVAMENTE**: a primeira operação funcional é `extrair_rotulos_de_cabecalho(texto)`,
chamada **uma única vez**, e **não há segunda chamada direta a `C8`** — o módulo **não importa**
`response_markdown_units`; `RepresentacaoMarcadaInvalida` e `CabecalhoRxxInvalido` **propagam
intactas**, e uma falha estrutural ou `G2` **fisicamente posterior vence** qualquer anomalia
local anterior, sem devolver nada parcialmente. **Nenhum julgamento estrutural é refeito**:
marcador inválido, bloco sem marcador, marcador fora de seção, `id` fora da gramática, `id`
duplicado e seção sem unidade **continuam sendo de `C8`**. **Caminhada física local** mínima e
compatível com `C8`, mantendo o contexto da instância corrente — `Rxx`, rótulo e a coleção
local de tokens —, na **mesma política de linha** (divisão exclusivamente por `LF`, no máximo
um `CR` terminal, sem `splitlines()`, sem *universal newline*, sem normalização). **Invariante
local × `C12`**: antes de **qualquer** retorno de sucesso, a sequência local de
`(Rxx, rotulo_literal)` de **todas** as instâncias é comparada **inteira** com o retorno
guardado da C12; divergência é **defeito interno** e produz
`RuntimeError("invariante_estrutural")`, **nunca** exceção pública — **sem `zip`, sem `dict`,
sem agrupamento, sem dedup e sem cardinalidade como prova de identidade**. **ZERO SEMÂNTICA DE
STATUS**: o módulo **não importa** `response_status`, `response_status_propagation` nem
`response_fragment_status`, **não** canonicaliza, **não** traduz rótulo, **não** decide
`ST1`–`ST3`, **não** interpreta `PARCIAL`, **não** lê `status-fragmento`, **não** propaga,
**não** aplica, **não** resolve status e **não** decide `SP5`; o **`rotulo_literal` é
completamente opaco** aqui. **Equivalência estrutural com `C8`, como evidência de teste e NÃO
como norma nova**: nos casos sintéticos válidos exercitados, o *flatten* dos tokens da nova
fronteira **coincide com a saída de `ler_unidades_marcadas(texto)`** — cobertura sintética de
**uma seção**, **várias seções**, **múltiplos fragmentos**, **homônimos**, **tokens
repetidos**, **`H3`–`H6`**, **`LF`**, **`CRLF`**, **documento sem `Rxx`** e **bloco fora de
seção**. **Baseline funcional corrente: `4477 passed`**, com **`134 passed`** no direcionado da
nova fronteira, em **Python 3.14.5** — delta **+134** sobre os **`4343 passed`** anteriores
(**4343 + 134 = 4477**), **executados sob `-W error`**, **zero failures, zero errors, zero
warnings** e **nenhum teste preexistente alterado**; as vizinhanças foram reexecutadas com
**`201 passed`** (C8), **`299 passed`** (C12) e **`243 passed`** (C14), **inalteradas**. Esses
números são **evidência da entrega funcional do PR #124**, e **NÃO** uma execução desta
reconciliação: **nenhum `pytest` foi executado aqui**, porque **zero código, zero teste e zero
`knowledge/**` mudaram**. **Não houve CI configurado** para a PR #124 nem para o merge commit —
*statuses* = 0, *workflow runs* = 0 — **AUSÊNCIA DE CI/CHECKS — NÃO FALHA DE CI**. **A PR #124
NÃO**: compõe status completo; resolve `SP5`; canonicaliza status; propaga status; interpreta
`PARCIAL`; cria índice; executa a bijeção física real; implementa *bindings*; implementa
`ASSERTIVA`; define *placeholder*; define `caminho_yaml`; define `hora`; resolve **C-7**; cria
*renderer*; integra *runtime*; migra autoridade; satisfaz automaticamente
**`C-A1-ST6`–`C-A1-ST10`**; nem cria a **3B.8**. **ASSOCIAR FRAGMENTOS À SEÇÃO NÃO É COMPOR
STATUS E NÃO É MATERIALIZAR `C`** — portanto **`C` continua ARBITRADA / NÃO MATERIALIZADA**.
**`R28/F1 = APROVADO` continua fisicamente APLICADO na `main`**: o corpus
`knowledge/respostas-aprovadas.md` permanece **byte-a-byte** no blob
`3a30fe764b80902227fdefb9282f3916650e4f17`, e **a PR #124 não alterou `knowledge/**`**. **A
MICRO-ARBITRAGEM SOBRE O COMPORTAMENTO DA FUTURA COMPOSIÇÃO TOTAL DIANTE DE `SP5` CONTINUA NÃO
RESPONDIDA**: a PR #124 **não** a responde, **não** escolhe *fail-closed*, **não** escolhe
omissão e **não** escolhe representação explícita de ausência — e **esta reconciliação também
não a resolve**. **PRÓXIMA AÇÃO**: **requer auditoria da pendência seguinte após a integração
da associação física, observando que a composição completa de status continua BLOQUEADA pela
micro-arbitragem de `SP5`** — **nenhuma implementação é eleita aqui** e **nenhum planejamento
adicional é iniciado**. O **item documental 104** abaixo **NÃO é "subetapa 104"**, **NÃO é
`C15`**, **NÃO é `E15`**, **NÃO é identificador normativo** e **NÃO cria a 3B.8** — registra
**somente** a integração funcional da PR #124.

**Atualização anterior — 2026-09-06 (reconciliação documental pós-aplicação física de
`R28/F1 = APROVADO` ao corpus), preservada como registro daquele momento.** Aquela entrega é
**EXCLUSIVAMENTE DOCUMENTAL**: altera
**somente** este documento, e **não altera código, testes, `knowledge/**`,
`docs/07-arquitetura-motor-respostas.md`, `prompts/**` nem `CLAUDE.md`. **ELA NÃO É MARCO
FUNCIONAL** e **NÃO cria numeração funcional nova**. **`R28/F1 = APROVADO` — DECIDIDO
HUMANAMENTE E AGORA APLICADO AO CORPUS.** A aplicação está integrada à `main` pelo **PR #122**
— **commit `77f8119488f0dc568721ca159fc13d3acd9f234d`** (`knowledge: apply R28 F1 fragment
status`), **merge commit `f3c35a4c738c9ab2e4343a3c012833144b514ca1`** (merge commit **normal**,
dois parents: `7cb6e9f1b4…` e `77f8119488…`), branch de origem
`knowledge/apply-r28-f1-status`. O **corpus** `knowledge/respostas-aprovadas.md` passou do blob
**`3bfb2e9fd18bac016e1dbe2c963ff916ceb0c96c`** para
**`3a30fe764b80902227fdefb9282f3916650e4f17`**, com diff de **exatamente `+1 / −0`**: a
**única** linha adicionada é `<!-- status-fragmento: APROVADO -->`, colocada **imediatamente
antes** do marcador `C-A5` `<!-- fragmento: F1 -->` da seção `R28`, com **zero linha física**
entre ambas. **Nada mais foi tocado**: cabeçalho `R28`, marcador `F1`, bloco emitível, notas
internas e todos os demais `Rxx` permanecem **inalterados**, e **`knowledge/casa77.yaml` não
foi alterado** — **zero preço, capacidade ou regra comercial nova**. **`PM1`, `PM2` e `PM5`
satisfeitas**: o envelope é **exato** (prefixo `<!-- status-fragmento: `, valor, sufixo
` -->`, sem nada antes e sem nada depois); a declaração ocupa a **linha imediatamente
anterior** ao marcador, preservando **`C-A5-I1`** e **`C-A5-I2`**; e a seção, cujo rótulo
literal é **exatamente `PARCIAL`**, passa a ter **exatamente uma** declaração válida para o seu
único fragmento emitível. **A decisão não foi inferida**: ela é o ato humano já registrado no
**item documental 100**, e o valor pertence ao **vocabulário fechado de `C-3`** (`C-3a`).
**Validação pela C14 sobre o corpus real**, registrada como evidência da PR #122 e **não
reexecutada aqui**: **`C8` passou — 37 tokens**; **`C12` passou — 30 cabeçalhos, 1 rotulado
`PARCIAL`**; **`C14` passou**, com resultado **`(("R28/F1", "APROVADO"),)`**; **direcionado da
C14 `243 passed`**; **regressão completa `4343 passed`**; **Python 3.14.5**, sob **`-W error`**,
com **zero failures, zero errors e zero warnings** e **nenhum teste ajustado**. **Nenhum
`pytest` foi executado nesta reconciliação**, porque **zero código, zero teste e zero
`knowledge/**` mudaram aqui**. **A aplicação de `R28/F1` NÃO**: cria o índice físico; executa a
bijeção física; migra a autoridade de status (**C-11**); completa a composição de status;
resolve *bindings*; resolve `ASSERTIVA`; resolve *placeholder*; resolve `caminho_yaml`; resolve
`hora`; resolve **C-7**; resolve automaticamente nota interna ou `null` (**`C-A1-P2`**
permanece literal); nem **materializa `C` integralmente**. **`C-A1-ST6`–`C-A1-ST10` NÃO são
declaradas satisfeitas por esta aplicação**: em particular, **`C-A1-ST8` exige o status de
TODOS os fragmentos resolvidos**, e a evidência atual cobre **um** fragmento — a validação de
`R28/F1` **não é extrapolada** para cobertura global de status, que exigiria **prova própria**.
**Portanto `C` continua ARBITRADA / NÃO MATERIALIZADA.** **A C14 CONTINUA SENDO A ÚLTIMA
MICROENTREGA FUNCIONAL DE CÓDIGO INTEGRADA** — commit funcional
`75025cc07c8d95f998c61f7516bf3db82bc9c06f`, merge `e8db60d95c104993d657de32b80e749dee8003ef`,
**baseline `4343 passed` em Python 3.14.5**: a **PR #122 é a aplicação física, no corpus, de
decisão humana já arbitrada**, e **NÃO** é renomeada como "C15" — **nenhuma numeração funcional
nova é criada**, a **3B.8 continua INEXISTENTE** e **nenhuma subetapa foi criada**. **PRÓXIMA
AÇÃO**: a antiga próxima ação — *aplicar fisicamente `R28/F1`* — **está CUMPRIDA e deixa de
constar**; a **próxima ação técnica requer definição e auditoria da próxima pendência de `C`
após a aplicação física de `R28/F1`**, e **essa pendência NÃO é eleita nem iniciada nesta
entrega**. O **item documental 103** abaixo **NÃO é "subetapa 103"**, **NÃO é `C15`**, **NÃO é
`E15`**, **NÃO é identificador normativo** e **NÃO cria a 3B.8** — registra **somente** a
aplicação física integrada de `R28/F1`.

**Atualização anterior — 2026-09-06 (reconciliação documental pós-merge da DÉCIMA QUARTA
MICROENTREGA FUNCIONAL DE `C` — leitor/validador determinístico de status por fragmento sob
`PARCIAL`), preservada como registro daquele momento.**
Aquela entrega é **EXCLUSIVAMENTE DOCUMENTAL**: altera **somente** este documento, e **não
altera código, testes, `knowledge/**`, `docs/07-arquitetura-motor-respostas.md`, `prompts/**`
nem `CLAUDE.md`. **A DÉCIMA QUARTA MICROENTREGA FUNCIONAL DE `C` ESTÁ INTEGRADA À `main`**
pelo **PR #120** — **commit funcional `75025cc07c8d95f998c61f7516bf3db82bc9c06f`** (`feat: add
deterministic fragment status reader`), **correção posterior NÃO FUNCIONAL
`ca4ec54bc8c1324cc93baf2b7500fa4a04b3f298`** (`fix: align C14 residual CR documentation`),
**merge commit `e8db60d95c104993d657de32b80e749dee8003ef`** (merge commit **normal**, dois
parents: `ca5952ba7e…` e `ca4ec54bc8…`; **zero squash, zero rebase**), branch de origem
`feat/c14-fragment-status-reader`. Ela adiciona **dois arquivos novos** —
`src/casa77_sdr/response_fragment_status.py` (**+484**) e
`tests/test_response_fragment_status.py` (**+1723**) —, **2 arquivos, +2207 / −0**, **zero
arquivo preexistente alterado**. A fronteira entregue é
`extrair_status_por_fragmento(texto: str) -> tuple[tuple[str, str], ...]`, no módulo
`casa77_sdr.response_fragment_status`, com **`__all__` de exatamente dois nomes** —
`DeclaracaoDeStatusInvalida` e `extrair_status_por_fragmento` —, **não exportada pelo package
root**; a exceção deriva **diretamente de `Exception`** e **não tem parentesco** com
`RepresentacaoMarcadaInvalida`, `CabecalhoRxxInvalido` ou `StatusNaoCanonicalizavel`. Ela
materializa **`PM1`–`PM5`** e o **regime exclusivo** já arbitrados, **sem reabrir norma**.
**`C12` é o primeiro portão e `C8` é satisfeito TRANSITIVAMENTE**: a **primeira** operação
funcional é `extrair_rotulos_de_cabecalho(texto)`, chamada **uma única vez**, e como a C12 já
executa `ler_unidades_marcadas(texto)` como o seu próprio portão, a ordem entre fronteiras é
**`C8` → `C12` → `C14`** **sem** que a C14 chame a C8 uma segunda vez — ela **não importa**
`response_markdown_units`; `RepresentacaoMarcadaInvalida` e `CabecalhoRxxInvalido` **propagam
intactas**, sem `try`/`except`, sem *wrapper*, sem reclassificação e sem tocar
`__cause__`/`__context__`, e uma falha estrutural ou `G2` **fisicamente posterior vence** uma
violação `PM` anterior. **Caminhada física local**, porque a C12 devolve `(Rxx,
rotulo_literal)` mas **não expõe a fronteira física da seção** e `Rxx` homônimos são
possíveis: o contexto físico da seção corrente — `Rxx` **e** rótulo — é mantido durante a
caminhada, **sem `zip`, sem `dict`, sem agrupamento por `Rxx`, sem pareamento por posição, sem
cardinalidade e sem dedup**. **Invariante local × `C12`**: antes de **qualquer** retorno de
sucesso, a sequência local de `(Rxx, rotulo_literal)` é comparada **inteira** com o retorno
guardado da C12; divergência é **defeito interno** e produz
`RuntimeError("invariante_estrutural")`, **nunca** a exceção pública. **Regime exclusivo**: a
declaração é aceita **se e somente se** `rotulo_literal == "PARCIAL"` — os três rótulos
físicos de `C-A1-ST1`–`C-A1-ST3` **não** são carregados localmente, e o módulo **não importa**
`response_status` nem `response_status_propagation`. **Valores aceitos**, exatamente três:
`APROVADO`, `AGUARDA_APROVACAO` e `BLOQUEADO` — `PARCIAL` é **inválido como valor**, e não há
tolerância de caixa, normalização, `strip`, coerção, *alias* ou tradução. **Cinco mensagens
fechadas**, com duas categorias de localizador: `valor_invalido: declaracao`;
`declaracao_fora_de_secao: declaracao`; `declaracao_proibida: declaracao`; `declaracao_orfa:
declaracao`; e `declaracao_ausente: marcador` — duas declarações consecutivas fazem **a
primeira** ser órfã, e **nenhuma categoria `declaracao_multipla` foi criada**; as mensagens
**nunca** ecoam `Rxx`, `id`, token, valor, rótulo, conteúdo, linha, índice, cardinalidade,
`repr` ou tipo concreto. Dentro da C14 a ordem é **fixa** — **1.** valor; **2.** seção; **3.**
regime; **4.** marcador seguinte —, de modo que `valor_invalido` vence `declaracao_proibida` e
`declaracao_fora_de_secao`, o regime é julgado **antes** da relação física, a primeira violação
em ordem física encerra e **nada é devolvido parcialmente**. **Saída**: um par
**`(token_canonico, status_canonico)`** por fragmento sob `PARCIAL` com declaração válida, com
**ordem física, duplicidades e tokens homônimos preservados** — zero `dict`, `set`, dedup,
`sorted` ou agrupamento; documento válido sem seção `PARCIAL` devolve `tuple()`. **Pureza**:
importa **apenas** `__future__` e `extrair_rotulos_de_cabecalho` — **zero I/O**, **zero
*filesystem***, **zero `open`**, **zero `pathlib`**, **zero YAML**, **zero JSON**, **zero
rede**, **zero LLM**, **zero relógio**, **zero calendário**, **zero *locale***, **zero
variável de ambiente**, **zero banco**, **zero cache**, **zero logging**, **zero regex**,
**zero `unicodedata`**, **zero estado mutável de módulo**, **zero `global`/`nonlocal`**, **zero
`dict`**, **zero `set`**, **zero `zip`**, **zero `sorted`**, **zero `splitlines`**, **zero
`strip`**, **zero normalização**, **zero coerção**; a política de linha é **exatamente** a de
`C8`/`C12`/`PM10`, e a entrada **não é alterada**. **Baseline funcional corrente: `4343
passed`**, com **`243 passed`** no direcionado da C14, em **Python 3.14.5** — delta **+243**
sobre os **`4100 passed`** anteriores (**4100 + 243 = 4343**), **executados sob `-W error`**,
**zero failures, zero errors, zero warnings** e **nenhum teste preexistente alterado**; as
vizinhanças foram reexecutadas com **`201 passed`** em `tests/test_response_markdown_units.py`
(C8) e **`299 passed`** em `tests/test_response_header_labels.py` (C12). Esses números são
**evidência da entrega funcional C14**, e **NÃO** uma execução desta reconciliação documental:
**nenhum `pytest` foi executado aqui**, porque **zero código, zero teste e zero `knowledge/**`
mudaram**. **Sobre os dois commits da PR #120**: o segundo,
`ca4ec54bc8c1324cc93baf2b7500fa4a04b3f298`, foi **exclusivamente uma correção de docstring**
sobre o `CR` residual — a redação anterior afirmava que um `CR` residual tornaria a linha
**incapaz** de ser cabeçalho, declaração ou marcador, o que é **falso** e já era contrariado
por teste explícito da C12; a redação corrente registra que o `CR` residual **permanece
conteúdo literal, não é removido nem normalizado, e o seu efeito depende das respectivas
gramáticas**. Esse commit tem **zero lógica alterada**, **zero teste alterado** e a baseline
permaneceu **`4343 passed`**; ele **NÃO é nova entrega funcional**. **Não houve CI configurado**
para a PR #120 nem para o merge commit — *statuses* = 0, *workflow runs* = 0 — **AUSÊNCIA DE
CI/CHECKS — NÃO FALHA DE CI**. **A C14 USA `C12` COMO PRIMEIRO PORTÃO E, POR `C12`, SATISFAZ
`C8` TRANSITIVAMENTE; ela NÃO compõe `C11` nem `C13` e NÃO implementa a composição completa de
status.** Além disso, a **C14 NÃO** aplica status ao corpus, **NÃO** altera `knowledge/**`,
**NÃO** cria índice, **NÃO** executa a bijeção
física, **NÃO** implementa *bindings*, `ASSERTIVA`, *placeholder*, `caminho_yaml`, `hora` ou
**C-7**, **NÃO** renderiza, **NÃO** integra *runtime* e **NÃO** migra autoridade. **LER O
STATUS DECLARADO NÃO É APLICAR STATUS, NÃO É RESOLVER `PARCIAL` NO CORPUS E NÃO É MATERIALIZAR
`C`.** **`R28/F1 = APROVADO` continua DECIDIDO HUMANAMENTE / AINDA NÃO APLICADO AO CORPUS**:
`knowledge/respostas-aprovadas.md` permanece **byte-a-byte** no blob
`3bfb2e9fd18bac016e1dbe2c963ff916ceb0c96c`, **nenhuma linha `<!-- status-fragmento: APROVADO
-->` foi inserida**, e o corpus continua com **zero** ocorrências de `status-fragmento` — **a
existência da C14 NÃO significa que o corpus esteja resolvido**; sobre o corpus atual, uma
verificação de `PM5` **falharia por declaração ausente**, que é o comportamento correto.
**Limites inalterados**: **`C` continua ARBITRADA / NÃO MATERIALIZADA**; **`C-A5` continua
MATERIALIZADA no corpus** e **`C-A5-M2` continua ATIVA**;
`knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE**; a **bijeção física
continua NÃO EXECUTADA**; a **composição completa de status continua NÃO IMPLEMENTADA**; a
**autoridade de status continua NÃO MIGRADA** (**C-11**); **`C-A1-ST6`–`C-A1-ST10` continuam
NÃO satisfeitas**; e continuam **ABERTOS** os *bindings*, a `ASSERTIVA`, o *placeholder*, a
gramática de `caminho_yaml`, o formato `hora` e **C-7**. **C14 É AGORA A ÚLTIMA ENTREGA
FUNCIONAL INTEGRADA**; a C13 passa a **histórico imediatamente anterior**, com o seu registro
**preservado**. A **3B.8 continua INEXISTENTE** e **nenhuma subetapa foi criada**. **PRÓXIMA
AÇÃO AINDA NÃO EXECUTADA: aplicar fisicamente a decisão humana `R28/F1 = APROVADO` ao corpus,
sob validação da C14, em entrega própria e auditada** — nada disso é feito aqui. O **item
documental 102** abaixo **NÃO é "subetapa 102"**, **NÃO é `E14` nem `E15`**, **NÃO é novo
identificador normativo de `C`**, **NÃO é nova microentrega funcional** e **NÃO cria a 3B.8** —
é **somente** a reconciliação documental pós-C14.

**Atualização anterior — 2026-09-06 (fechamento da lacuna normativa pré-C14 — regime exclusivo
de `status-fragmento` sob `PARCIAL`), preservada como registro daquele momento.** Aquela
entrega é **EXCLUSIVAMENTE DOCUMENTAL**: altera
**somente** `docs/07-arquitetura-motor-respostas.md` e este documento, e **não altera código,
testes, `knowledge/**`, `prompts/**` nem `CLAUDE.md`. **ELA NÃO É MARCO FUNCIONAL** e **NÃO É
a décima quarta microentrega funcional de `C`**. **A LACUNA PRÉ-C14 ESTÁ FECHADA
DOCUMENTALMENTE.** Ela fecha **uma única** matéria: **o comportamento de uma linha que
satisfaz EXATAMENTE o envelope de `PM1` dentro de uma seção `Rxx` cujo cabeçalho satisfaz
`G2`, mas cujo rótulo literal NÃO é `PARCIAL`** — registrada em `docs/07` como **registro
posterior claramente separado**, no bloco **"Regime exclusivo de `status-fragmento` sob
`PARCIAL`"**, escrito **depois** de `PM1`–`PM12` e do registro da decisão humana de `R28/F1`.
**A decisão**: **`status-fragmento` é PERMITIDO EXCLUSIVAMENTE sob cabeçalho `G2` cujo rótulo
literal seja EXATAMENTE `PARCIAL`**; sob **qualquer outro** rótulo literal, **a presença de uma
linha que satisfaça exatamente o envelope de `PM1` é *FAIL-CLOSED***. **Consequências por
regime**: sob `PARCIAL`, **`PM5` e `PM11` permanecem literais** — **exatamente uma** declaração
válida por fragmento emitível, com nenhuma e com duas ou mais sendo *fail-closed*; sob
`ST1`–`ST3`, **`PM7` permanece literal**, com **fundamento próprio** (`SP2`/`SP3` já propagam
uniformemente, e `SP6` seria comprometido); sob **qualquer outro rótulo `G2` válido**, a
declaração é **igualmente proibida** por este registro; e **fora de seção `Rxx`**, **`PM6`
permanece literal e aplicável**. **Fundamento normativo exaustivo**: **`PM8`** — a declaração é
fonte explícita do status do fragmento **sob `PARCIAL`**, e somente ali — e **`PM11`** — é o
rótulo físico `PARCIAL` que **ativa** o regime de status explicitamente declarado por
fragmento, de modo que fora dele **não há regime a ativar**. **A composição atual do corpus NÃO
é fundamento**: o corpus é **evidência**, jamais origem de norma. **`G2` e `SP5` permanecem
INTACTOS**: um rótulo fora de `ST1`–`ST3` e de `PARCIAL` **continua podendo satisfazer `G2`**,
**continua literal e opaco** (**`GR2.10`**, **`GR3`**), **não** se torna gramaticalmente
inválido, **não** recebe tradução automática, **não** recebe propagação automática, **não** é
corrigido, **não** é normalizado e **não** é inferido — **o seu status permanece NÃO RESOLVIDO
conforme `SP5`**, que continua sendo o comportamento arbitrado; **este registro proíbe SOMENTE
a presença de `status-fragmento` nesse regime**. **Quatro cláusulas de precisão**: **1.** a
**ausência** de `status-fragmento` sob rótulo não-`PARCIAL` **NÃO é erro** desta regra nem de
`PM5` — o status permanece não resolvido por `SP5`; **2.** a regra alcança **somente** a linha
que satisfaça **exatamente** `PM1`, e toda **quase-declaração** — indentação, *whitespace*
divergente, conteúdo antes ou depois, envelope incompleto, tab ou qualquer outra divergência —
**permanece conteúdo comum**, sem gerar erro `PM` por si só sob rótulo não-`PARCIAL`; **3.** a
regra **NÃO** torna inválido um rótulo desconhecido — **`GR2.10`**, **`GR3`** e **`SP5`**
preservados: o proibido ali é **a declaração**, não **o rótulo**; **4.** uma linha iniciada por
`>` **não satisfaz `PM1`** e **não pertence** a esta regra. **`PM1`–`PM12` permanecem
INALTERADAS**, **nenhum `PM13` foi criado**, **nada foi renumerado ou reinterpretado** e
**`PM7` não foi alterado nem absorvido**. **Nenhum detalhe técnico é norma aqui**: módulo,
função, assinatura, exceção, categorias técnicas, localizadores, mensagens, precedência
interna, tipo de erro interno, estratégia de importação, inspeção de árvore sintática e
arquivos futuros **não** são definidos — pertencem a **mandato técnico próprio**, ainda **não**
emitido. **Corpus inalterado**: `knowledge/respostas-aprovadas.md` permanece **byte-a-byte** no
blob `3bfb2e9fd18bac016e1dbe2c963ff916ceb0c96c`, **nenhuma linha `<!-- status-fragmento:
APROVADO -->` foi inserida**, e a decisão humana **`R28/F1 = APROVADO` continua DECIDIDA e
AINDA NÃO APLICADA** — portanto **`PARCIAL` continua NÃO RESOLVIDO no corpus**. **Estado
preservado**: **a C13 continua a última entrega funcional integrada** — commit funcional
`cbf3e379c9b6697cd502b6a7a0bd3e9bb76c1a27`, merge `50c1d5e681a11923c443c1f117de5751ea846cdd`
—, com **baseline `4100 passed`** em **Python 3.14.5**; **nenhum `pytest` foi executado nesta
entrega**, porque **zero código, zero teste e zero `knowledge/**` mudaram**. **`C` continua
ARBITRADA / NÃO MATERIALIZADA**; o **índice físico continua INEXISTENTE**; a **bijeção física
continua NÃO EXECUTADA**; a **autoridade de status continua NÃO MIGRADA** (**C-11**); e
**`C-A1-ST6`–`C-A1-ST10` continuam NÃO satisfeitas**. O **item documental 101** abaixo **NÃO é
"subetapa 101"**, **NÃO é `E14`**, **NÃO é identificador normativo de `C`**, **NÃO é
microentrega funcional** e **NÃO cria a 3B.8** — registra **somente** o fechamento desta lacuna
pré-C14. **C14 CONTINUA NÃO INICIADA FUNCIONALMENTE**: esta entrega **não implementa C14**,
**não cria módulo**, **não cria teste** e **não fixa API como norma** — ela **apenas elimina a
lacuna normativa que bloqueava o mandato técnico**.

**Atualização anterior — 2026-09-06 (registro da decisão humana de status de `R28/F1` =
`APROVADO` — APROVADA HUMANAMENTE / AINDA NÃO APLICADA AO CORPUS), preservada como registro
daquele momento.** Aquela entrega é **EXCLUSIVAMENTE
DOCUMENTAL**: altera **somente** `docs/07-arquitetura-motor-respostas.md` e este documento, e
**não altera código, testes, `knowledge/**`, `prompts/**` nem `CLAUDE.md`. **ELA NÃO É MARCO
FUNCIONAL** e **NÃO É a décima quarta microentrega funcional de `C`**. Ela registra **uma
única** coisa: **existe decisão humana explícita de que o status canônico do fragmento
emitível `R28/F1` é `APROVADO`**, registrada em `docs/07` como **registro posterior
claramente separado** dentro do bloco **"Mapeamento físico de status por fragmento sob
`PARCIAL`"**. **`PM1`–`PM12` NÃO foram alteradas**, **nenhum `PM13` foi criado** e **nenhuma
regra foi reinterpretada**. **A decisão é humana e deliberada**: ela **NÃO** foi inferida de
nota interna, **NÃO** foi inferida de `null`, **NÃO** foi inferida de conteúdo, **NÃO** foi
inferida do rótulo físico `PARCIAL` do cabeçalho e **NÃO** foi escolhida por ferramenta ou
modelo algum — exatamente o que **`C-A1-P2`** e **`PM11`** exigem. O valor pertence ao
**vocabulário fechado de `C-3`** (`C-3a`). **A decisão está APROVADA e AINDA NÃO APLICADA**:
`knowledge/respostas-aprovadas.md` **NÃO foi alterado** e permanece **byte-a-byte** no blob
`3bfb2e9fd18bac016e1dbe2c963ff916ceb0c96c`; **nenhuma linha `<!-- status-fragmento: APROVADO
-->` foi inserida**; **nenhum cabeçalho, fragmento ou nota foi alterado**. **Enquanto não
aplicada, o corpus continua mecanicamente sem a declaração obrigatória de `PM5`** para aquele
fragmento — uma verificação estrutural de `PM5` sobre o corpus atual **falharia por declaração
ausente**, e isso é o comportamento correto: **decidir não é aplicar**. A **forma futura
decorrente da decisão** — a ser executada por **entrega própria**, não por esta — é
**exatamente** a linha `<!-- status-fragmento: APROVADO -->` **imediatamente antes** do
marcador `C-A5` de `R28/F1`, com **zero linha física** entre ambos (`PM1`, `PM2`); **essa
linha é SOMENTE forma futura, e NÃO alteração executada aqui**. **O significado da decisão é
estrito**: `APROVADO` significa **somente** o **status canônico de `C-3` do fragmento emitível
`R28/F1`** — a decisão **NÃO** resolve nota interna, **NÃO** altera `null`, **NÃO** aprova
dado comercial, **NÃO** elimina handoff, **NÃO** autoriza emissão sem as demais validações,
**NÃO** decide **S2-D8**, **NÃO** cria `E09`, **NÃO** elimina `E09`, **NÃO** resolve *binding*,
**NÃO** resolve `ASSERTIVA`, **NÃO** resolve **C-8** e **NÃO** satisfaz **`C-A1-ST8`**
isoladamente (que exige o status de **todos** os fragmentos resolvidos), permanecendo válido
**`C-A4-G8`** — **cobertura estrutural não é emissibilidade**. **Precisão sobre a pendência de
`PARCIAL`**: antes desta entrega ela era **status humano não decidido + não aplicado**; depois
desta entrega ela é **status humano DECIDIDO (`APROVADO`), com a declaração `PM` AINDA NÃO
APLICADA ao corpus** — portanto **o corpus continua estruturalmente NÃO RESOLVIDO até a
aplicação física da declaração**. **Estado preservado**: **a C13 continua a última entrega
funcional integrada** — commit funcional `cbf3e379c9b6697cd502b6a7a0bd3e9bb76c1a27`, merge
`50c1d5e681a11923c443c1f117de5751ea846cdd` —, com **baseline `4100 passed`** em **Python
3.14.5**; **`PM1`–`PM12` continuam integradas** pelo PR #117; **nenhum `pytest` foi executado
nesta entrega**, porque **zero código, zero teste e zero `knowledge/**` mudaram**. **`C`
continua ARBITRADA / NÃO MATERIALIZADA**; o **índice físico continua INEXISTENTE**; a
**bijeção física continua NÃO EXECUTADA**; a **autoridade de status continua NÃO MIGRADA**
(**C-11**); e **`C-A1-ST6`–`C-A1-ST10` continuam NÃO satisfeitas**. O **item documental 100**
abaixo **NÃO é "subetapa 100"**, **NÃO é `E14`**, **NÃO é identificador normativo de `C`**,
**NÃO é microentrega funcional** e **NÃO cria a 3B.8** — registra **exclusivamente** esta
decisão humana. **C14 NÃO FOI ESCOLHIDA, NÃO FOI PLANEJADA E NÃO FOI INICIADA**: esta entrega
**não planeja C14**, **não implementa C14**, **não escolhe assinatura**, **não cria módulo** e
**não cria teste**.

**Atualização anterior — 2026-09-06 (micro-arbitragem documental — mapeamento físico de status
por fragmento sob `PARCIAL`), preservada como registro daquele momento.** Aquela entrega é
**EXCLUSIVAMENTE DOCUMENTAL**: altera **somente**
`docs/07-arquitetura-motor-respostas.md` e este documento, e **não altera código, testes,
`knowledge/**`, `prompts/**` nem `CLAUDE.md`. **ELA NÃO É MARCO FUNCIONAL** e **NÃO É a
décima quarta microentrega funcional de `C`**. Ela fecha **uma única** matéria: **a
representação física e as regras estruturais do status explícito por fragmento quando o
cabeçalho `G2` do respectivo `Rxx` contém o rótulo `PARCIAL`**, registrada em `docs/07` no
bloco **"Mapeamento físico de status por fragmento sob `PARCIAL`"**, imediatamente após o
bloco da gramática `G2`. Os rótulos **`PM1`**–**`PM12`** ali usados são **locais daquele
bloco**, existem só para referência interna e **NÃO** são etapa, subetapa, `Exx` nem
nomenclatura normativa de `C`; eles **NÃO criam a 3B.8**, que **continua INEXISTENTE**.
**Portador (`PM1`)**: a linha física própria `<!-- status-fragmento: <valor> -->`, com
envelope **EXATO** — prefixo `<!-- status-fragmento: `, `<valor>`, sufixo ` -->` —, **nada
antes e nada depois**, **zero `strip`**, **zero normalização**, **zero tolerância implícita**.
**Posição (`PM2`)**: **linha imediatamente anterior** ao marcador `C-A5`, **zero linha física**
entre ambos; o marcador continua imediatamente antes do bloco, e a declaração **nunca** fica
entre marcador e bloco — **`C-A5-I1`** e **`C-A5-I2`** preservados literalmente.
**Associação (`PM3`)**: **adjacência estrutural status → marcador**, que **NÃO** é identidade,
**NÃO** é parte do token, **NÃO** é parte do `id` e **NÃO** é posição usada para definir
identidade — **`C-A5-I5`** intacto; a identidade continua **exclusivamente** `<Rxx>/<id>`, e a
declaração **não contém, não duplica, não cria e não altera `id`**. **Vocabulário (`PM4`) —
decisão `V1`, status canônico direto**: `<valor>` é **EXATAMENTE UM** dos **três** valores de
**`C-3`** — `APROVADO`, `AGUARDA_APROVACAO` ou `BLOQUEADO` —, **sem quarto valor**, com
**`PARCIAL` INVÁLIDO como valor**; os rótulos físicos de `ST1`–`ST3` **não** são usados nesse
campo, **`canonicalizar_status` não é chamado** e **nenhuma tabela de tradução é criada**; a
comparação futura é **literal**, com **zero `strip`, zero caixa, zero `NFC`, zero coerção**.
**`BLOQUEADO` é, portanto, representável** por fragmento — o que **não** o transforma em `E09`
nem em `pendencia_impeditiva` (**C-12**). **Cardinalidade (`PM5`)**: sob cabeçalho `G2`
rotulado `PARCIAL`, **cada** fragmento emitível tem **EXATAMENTE UMA** declaração válida —
**nenhuma** é *fail-closed*, **duas ou mais** são *fail-closed*, **sem inferência e sem
valor padrão**, preservando `C-3` (**fragmento sem status é erro de contrato, nunca `APROVADO`
implícito**). **Fail-closed (`PM6`)** para declaração ausente, órfã, múltipla, fora de seção
`Rxx`, sem marcador válido imediatamente seguinte, com linha em branco intercalada, com valor
fora de `C-3`, com `PARCIAL` como valor, com *whitespace* divergente, com conteúdo adicional
ou com envelope divergente que deixe o marcador sem a declaração obrigatória — **sem** decidir
classe, exceção, mensagem, função, módulo ou assinatura, que pertencem a **futura
materialização técnica**. **Quase-declaração**: linha que não satisfaça o envelope exato
**permanece conteúdo comum** — como sob `C-A5` —, mas, se isso deixar um marcador sem a
declaração obrigatória, **`PM5` falha por declaração ausente**, **sem inferir intenção**.
**Proibição sob `ST1`–`ST3` (`PM7`)**: a declaração é **PROIBIDA** sob rótulo de `C-A1-ST1`,
`C-A1-ST2` ou `C-A1-ST3`, **mesmo com valor coincidente**, porque `SP2`/`SP3` já definem
propagação uniforme e uma segunda fonte comprometeria **`SP6`**. **Autoridade (`PM8`)**: a
declaração vive na **autoridade Markdown vigente**; o futuro índice poderá armazená-la **por
fragmento** conforme **`C-2i`**, e **isso NÃO migra autoridade** — até `C-A1-ST6`–`C-A1-ST10`,
`knowledge/respostas-aprovadas.md` **continua a autoridade** (**C-11**). **Não emissão
(`PM9`)**: `status-fragmento` **não** é fragmento emitível, nota comercial ou instrução
emitível, **não** recebe *binding* nem `ASSERTIVA`, **não** pode ser emitido ao interessado e
**não** entra na bijeção — **`C-2m`–`C-2p`** e **`C-A5-U4`** preservados. **Política de linha
(`PM10`)**: reutiliza **integralmente** a de `C8`/`C12` — divisão **exclusivamente por `LF`**,
**no máximo um `CR` terminal** removido, **sem `splitlines()`**, **sem *universal newline*** —,
**sem criar terceira política**. **Significado físico de `PARCIAL` (`PM11`)**: **no Markdown
vigente, o rótulo físico `PARCIAL` ativa o regime de STATUS EXPLICITAMENTE DECLARADO POR
FRAGMENTO** — **não** aplicar propagação automática do cabeçalho, **exigir** uma declaração
para **cada** fragmento e **resolver cada fragmento individualmente** por valor de `C-3`
explícito. `PARCIAL` **NÃO** é status canônico, **NÃO** é armazenado no `Rxx` do índice,
**NÃO** é armazenado no fragmento, **NÃO** é convertido em quarto status, **NÃO** exige dois
ou mais status distintos, **NÃO** exige mistura de status e **NÃO** exige cardinalidade mínima
de dois fragmentos: uma seção rotulada `PARCIAL` pode ter **um** ou **vários** fragmentos,
**com o mesmo status** ou **com status distintos**. **NENHUMA FUNÇÃO GERAL DE AGREGAÇÃO DE
STATUS DE `Rxx` FOI CRIADA**, e **`C-3` não é reescrita**: o `Rxx` **continua sem status
armazenado** (**C-2d**), `PARCIAL` **nunca** é valor armazenado, e os únicos status
armazenáveis pertencem aos **fragmentos**. **`C-A1-P2` preservada**: nota interna **não** é
fragmento, **não** recebe status, **não** bloqueia automaticamente fragmento e **não**
determina automaticamente o valor da declaração — **nada** é inferido de nota, `null`,
conteúdo, posição ou contexto. **Evidência estrutural — evidência, não norma**: consulta
**estritamente read-only** ao blob `3bfb2e9fd18bac016e1dbe2c963ff916ceb0c96c`, **sem
reproduzir conteúdo comercial**: **30** cabeçalhos `## Rxx`; **exatamente 1** com rótulo
`PARCIAL` (**`R28`**, já citado por `C-A1-P2`), contendo **exatamente 1** marcador `C-A5`;
**37** marcadores no total, **37/37** imediatamente seguidos pela primeira linha do bloco; e
**0** ocorrências de `status-fragmento` no corpus — os 37 comentários HTML existentes são
**exatamente** os 37 marcadores, de modo que o portador **não colide com nada existente**.
**EVIDÊNCIA NÃO É NORMA**, **nenhum status foi atribuído** ao `R28` ou a qualquer fragmento
real, e **`knowledge/respostas-aprovadas.md` NÃO foi alterado**. **Limites (`PM12`)**: esta
arbitragem **NÃO** atribui status real, **NÃO** altera `knowledge/**`, **NÃO** altera `C8`,
`C11`, `C12` ou `C13`, **NÃO** implementa *parser*, **NÃO** implementa a próxima entrega
funcional, **NÃO** cria índice, **NÃO** executa a bijeção física, **NÃO** satisfaz
`C-A1-ST6`–`C-A1-ST10`, **NÃO** migra autoridade, **NÃO** resolve *binding*, *placeholder*,
`caminho_yaml` ou **C-7**, **NÃO** cria a **3B.8** e **NÃO** materializa `C`. **A norma
estrutural está FECHADA** quanto a portador, posição, associação, vocabulário, cardinalidade,
*fail-closed*, proibição sob `ST1`–`ST3` e significado físico; **o corpus real, porém,
continua NÃO RESOLVIDO** — **`PARCIAL` CONTINUA NÃO RESOLVIDO NO CORPUS ATÉ APLICAÇÃO HUMANA
EXPLÍCITA DOS STATUS POR FRAGMENTO**, e a **composição documental futura com `C8`/`C12`/`C13`
continua NÃO IMPLEMENTADA**. **A C13 CONTINUA A ÚLTIMA ENTREGA FUNCIONAL INTEGRADA** — commit
funcional `cbf3e379c9b6697cd502b6a7a0bd3e9bb76c1a27`, merge
`50c1d5e681a11923c443c1f117de5751ea846cdd` —, com **baseline `4100 passed`** em **Python
3.14.5**; **nenhum `pytest` foi executado nesta entrega**, porque **zero código, zero teste e
zero `knowledge/**` mudaram**. **`C` continua ARBITRADA / NÃO MATERIALIZADA**; o **índice
físico continua INEXISTENTE**; a **bijeção física continua NÃO EXECUTADA**; a **autoridade de
status continua NÃO MIGRADA**; e **`C-A1-ST6`–`C-A1-ST10` continuam NÃO satisfeitas**. O
**item documental 99** abaixo **NÃO é "subetapa 99"**, **NÃO é `E14`**, **NÃO é identificador
normativo de `C`**, **NÃO é microentrega funcional** e **NÃO cria a 3B.8** — registra
**somente** esta micro-arbitragem documental. **C14 NÃO FOI ESCOLHIDA, NÃO FOI PLANEJADA E NÃO
FOI INICIADA**: nenhuma pendência é eleita aqui, e a escolha da próxima ação funcional exige
planejamento separado após a integração desta entrega.

**Atualização anterior — 2026-09-06 (reconciliação documental pós-merge da DÉCIMA TERCEIRA
MICROENTREGA FUNCIONAL DE `C` — propagação pura e determinística de status `ST1`–`ST3` aos
fragmentos já associados), preservada como registro daquele momento.** Aquela entrega é
**EXCLUSIVAMENTE DOCUMENTAL**: altera **somente**
este documento, e **não altera código, testes, `knowledge/**`,
`docs/07-arquitetura-motor-respostas.md`, `prompts/**` nem `CLAUDE.md`. **A DÉCIMA TERCEIRA
MICROENTREGA FUNCIONAL DE `C` ESTÁ INTEGRADA À `main`** pelo **PR #115** — **commit funcional
`cbf3e379c9b6697cd502b6a7a0bd3e9bb76c1a27`** (`feat: add deterministic response status
propagation`), **merge commit `50c1d5e681a11923c443c1f117de5751ea846cdd`** (merge commit
**normal**, dois parents: `3329f558e9…` e `cbf3e379c9…`; **zero squash, zero rebase**), branch
de origem `feat/c-status-propagation`. Ela adiciona **dois arquivos novos** —
`src/casa77_sdr/response_status_propagation.py` (**+195**, blob
`cb5668efaaa5522a378946e32bb17c032fda78a3`) e `tests/test_response_status_propagation.py`
(**+1567**, blob `24da2fdbfe99ec9e073bcb093254db3b567f866c`) —, **2 arquivos, +1762 / −0**,
**zero arquivo preexistente alterado**. A fronteira entregue é
`propagar_status(rotulo: str, fragmentos: Sequence[str]) -> tuple[tuple[str, str], ...]`, no
módulo `casa77_sdr.response_status_propagation`, com **`__all__` de exatamente dois nomes** —
`PropagacaoInvalida` e `propagar_status` —, **não exportada pelo package root**, devolvendo um
par **`(fragmento_opaco, status_canonico)`** por elemento recebido, **na ordem da entrada**;
sequência vazia com rótulo válido devolve `tuple()`. Ela materializa **`SP1`**, **`SP2`** e
**`SP3`** já arbitradas em `docs/07`, **sem reabrir norma**. **C13 é uma primitiva PURA**:
ela **NÃO recebe Markdown**, **NÃO chama C8**, **NÃO chama C11**, **NÃO chama C12**, **NÃO
localiza `Rxx`**, **NÃO localiza cabeçalho ou marcador**, **NÃO resolve contenção física**,
**NÃO resolve homônimos** e **NÃO compõe nem decompõe identidade** — **A ASSOCIAÇÃO CORRETA
ENTRE O RÓTULO E OS FRAGMENTOS É PRÉ-CONDIÇÃO DO CHAMADOR** (`SP1`), e um retorno
bem-sucedido **não** prova a origem do rótulo, a existência do `Rxx`, o pertencimento dos
fragmentos, a completude, a proveniência, a contenção física nem a validade da identidade.
A **primeira** operação funcional é **`canonicalizar_status(rotulo)`**, e **nenhuma**
validação de `fragmentos` a precede — com rótulo **e** fragmentos inválidos, **o rótulo falha
primeiro**, decisão técnica local de determinismo, **não** norma nova. A tradução continua
**exclusivamente** pelas três regras arbitradas — **`ST1`** `APROVADO` → `APROVADO`, **`ST2`**
`AGUARDA APROVAÇÃO` → `AGUARDA_APROVACAO` e **`ST3`** `APROVADO com handoff obrigatório` →
`APROVADO`, **sem transportar o sufixo de handoff** —, **sem tabela local** e **sem nenhuma
quarta tradução**; `StatusNaoCanonicalizavel` **propaga intacta**, sem `try`/`except`, sem
*wrapper*, sem reclassificação, sem `raise from` e sem tocar `__cause__`/`__context__`.
**Propagação uniforme (`SP3`), por construção**: **todos** os fragmentos fornecidos naquela
chamada recebem **o mesmo** status canônico, que **NÃO depende** de posição, ordem, índice,
token, `id`, conteúdo, quantidade ou redação — a sequência recebida determina **apenas** quais
tokens aparecem e em que ordem são devolvidos, **jamais** o status, o que preserva
literalmente **`C-A5-I5`** e **`C-A5-M6`**. **Os fragmentos são `str` opacas**: C13 **não
valida** `Rxx`, `id`, o separador `/`, gramática, unicidade, cobertura ou cardinalidade, e
**duplicidades são preservadas** — tokens repetidos produzem pares repetidos, **sem dedup, sem
`dict`, sem `zip` e sem agrupamento por `Rxx`**. **`PropagacaoInvalida`** tem **categoria
técnica privada e única** — `tipo_invalido` — e **dois localizadores fechados**: `fragmentos`
e `fragmentos.item`; mensagem `<categoria>: <localizador>`, **nunca** ecoando token, rótulo,
conteúdo, `repr`, tipo concreto, índice, posição, tamanho ou cardinalidade. **Essa exceção
julga somente a forma mínima do argumento `fragmentos` — ela NÃO julga identidade**;
*fail-closed*, com a validação percorrendo **toda** a entrada antes da montagem e **nada
devolvido parcialmente**. **`PARCIAL` continua NÃO RESOLVIDO**: `canonicalizar_status`
continua recusando-o, e C13 **não captura, não traduz, não propaga, não mapeia e não
converte** — a recusa por `StatusNaoCanonicalizavel` é **somente daquela invocação**, e
**nenhuma política de documento inteiro é registrada aqui**. **Baseline funcional corrente:
`4100 passed`**, com **`397 passed`** no direcionado da C13, em **Python 3.14.5** — delta
**+397** sobre os **`3703 passed`** anteriores (**3703 + 397 = 4100**), **executados sob
`-W error`**, **zero failures, zero errors, zero warnings** e **nenhum teste preexistente
alterado**, no `.venv` do projeto. Esses números são **evidência da entrega funcional C13**,
e **NÃO** uma execução desta reconciliação documental: **nenhum `pytest` foi executado aqui**,
porque **zero código, zero teste e zero `knowledge/**` mudaram**. **Não houve CI configurado**
para a PR #115 nem para o merge commit — *statuses* = 0, *workflow runs* = 0 — **AUSÊNCIA DE
CI/CHECKS — NÃO FALHA DE CI**. **A C13 NÃO** lê Markdown, **NÃO** compõe C8/C11/C12, **NÃO**
resolve `PARCIAL`, **NÃO** cria índice, **NÃO** executa a bijeção física, **NÃO** cria
*bindings*, **NÃO** implementa *placeholder*, `caminho_yaml`, `hora` ou **C-7**, **NÃO**
executa equivalência, **NÃO** renderiza, **NÃO** integra *runtime* e **NÃO** migra autoridade.
**PROPAGAR STATUS NÃO É LER MARKDOWN, NÃO É COMPOR C8/C11/C12, NÃO É RESOLVER `PARCIAL` E NÃO
É MATERIALIZAR `C`.** **Limites inalterados**: **`C` continua ARBITRADA / NÃO
MATERIALIZADA**; **`C-A5` continua MATERIALIZADA no corpus** e **`C-A5-M2` continua ATIVA**;
`knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE**; a **bijeção física
continua NÃO EXECUTADA**; a **autoridade de status continua NÃO MIGRADA** (**C-11**);
**`C-A1-ST6`–`C-A1-ST10` continuam NÃO satisfeitas**; a **composição documental de C13 com
C8/C12 continua NÃO IMPLEMENTADA**; e continuam **ABERTOS** o mapeamento concreto de
`PARCIAL`, a sintaxe de *placeholder*, a gramática de `caminho_yaml`, o formato `hora` e
**C-7**. **C13 É AGORA A ÚLTIMA ENTREGA FUNCIONAL INTEGRADA**; a C12 passa a **histórico
imediatamente anterior**, com o seu registro **preservado**. A **3B.8 continua INEXISTENTE**
e **nenhuma subetapa foi criada**. O **item documental 98** abaixo **NÃO é "subetapa 98"**,
**NÃO é `E13` nem `E14`**, **NÃO é identificador normativo de `C`**, **NÃO é nova
microentrega funcional** e **NÃO cria a 3B.8** — é **somente** a reconciliação documental
pós-C13. **C14 NÃO FOI ESCOLHIDA, NÃO FOI PLANEJADA E NÃO FOI INICIADA**: nenhuma pendência é
eleita aqui — nem `PARCIAL`, nem a composição documental, nem o índice, nem a bijeção, nem
qualquer outro residual —, e a escolha da próxima ação funcional exige planejamento separado
após a integração desta reconciliação.

**Atualização anterior — 2026-09-05 (reconciliação documental pós-merge da DÉCIMA SEGUNDA
MICROENTREGA FUNCIONAL DE `C` — extração determinística do rótulo literal de status do
cabeçalho `Rxx`), preservada como registro daquele momento.** Aquela entrega é
**EXCLUSIVAMENTE DOCUMENTAL**: altera **somente** este
documento, e **não altera código, testes, `knowledge/**`,
`docs/07-arquitetura-motor-respostas.md`, `prompts/**` nem `CLAUDE.md`. **A DÉCIMA SEGUNDA
MICROENTREGA FUNCIONAL DE `C` ESTÁ INTEGRADA À `main`** pelo **PR #113** — **commit funcional
`798beb31fd0dc4fed34aa7b20d397abcd2ef8c2b`** (`feat: add deterministic Rxx header label
extraction`), **merge commit `eae7b5098b248cefb42b3a82569fc0575fd6fee0`** (merge commit
**normal**, dois parents: `6940bf3252…` e `798beb31fd…`; **zero squash, zero rebase**), branch
de origem `feat/c-header-label-extraction`. Ela adiciona **dois arquivos novos** —
`src/casa77_sdr/response_header_labels.py` (**+299**, blob
`f8a8e6d6e4a0a03eea4069fd24bcc9eb38b5c06f`) e `tests/test_response_header_labels.py`
(**+1532**, blob `eb097b250c3ecc56597878b951e12bf1afdadc72`) —, **2 arquivos, +1831 / −0**,
**zero arquivo preexistente alterado**. A fronteira entregue é
`extrair_rotulos_de_cabecalho(texto: str) -> tuple[tuple[str, str], ...]`, no módulo
`casa77_sdr.response_header_labels`, com **`__all__` de exatamente dois nomes** —
`CabecalhoRxxInvalido` e `extrair_rotulos_de_cabecalho` —, **não exportada pelo package
root**, devolvendo, **em ordem física do documento**, um par `(Rxx, rotulo_literal)` por
cabeçalho físico `## Rxx`; o título **não** aparece na saída, e documento sem `Rxx` devolve
`tuple()`. Ela materializa a gramática física **`G2`** já arbitrada no bloco **"Gramática
física do rótulo de status no cabeçalho `Rxx`"** de `docs/07` — **`## Rxx — <titulo> —
<rotulo>`**, separador literal **`U+0020 U+2014 U+0020`** —, **sem reabrir norma**: a
**primeira** operação funcional é `ler_unidades_marcadas(texto)`, usada **exclusivamente como
portão estrutural integral e anterior** — **C8 continua responsável por tipo e estrutura
`C-A5`**, e `RepresentacaoMarcadaInvalida` **propaga intacta**, sem `try`/`except`, sem
*wrapper*, sem reclassificação e sem tocar `__cause__`/`__context__` —; o **resultado de C8
NÃO é armazenado nem comparado**, e **NÃO EXISTE INVARIANTE LOCAL × C8**: C8 devolve somente
tokens `<Rxx>/<id>` e não expõe fronteiras físicas de seção, de modo que, com seções
homônimas, nenhum conjunto, contagem ou compressão por `Rxx` provaria correspondência 1:1
entre cabeçalhos — **nenhuma equivalência entre tokens de C8 e cabeçalhos C12 é afirmada**.
Só depois a C12 faz a sua própria caminhada local, mínima, para localizar os cabeçalhos
`## Rxx` já pertencentes ao domínio estrutural aceito. **Categorias técnicas privadas e
fechadas** — **quatro**, e **não** identificadores normativos de `C`: `separador_ausente`,
`cardinalidade_de_separador`, `segmento_vazio` e `branco_de_borda`; **localizadores
fechados**: `cabecalho`, `titulo` e `rotulo`; mensagem `<categoria>: <localizador>`, **nunca**
ecoando `Rxx`, título, rótulo, conteúdo, caractere ofensor, `repr`, tipo, linha, índice,
tamanho ou cardinalidade numérica. **Fail-closed**, com precedência fixa por cabeçalho —
separador ausente → cardinalidade → título vazio → branco de borda no título → rótulo vazio →
branco de borda no rótulo —, **primeira violação encerra**, **nada é devolvido
parcialmente**; `-`, `–`, variantes Unicode e espaçamento divergente são **recusados, nunca
corrigidos**; **zero `strip`, zero normalização, zero inferência**. **Política de linhas**: a
estrutural de C8 — divisão **exclusivamente por `LF`**, **no máximo um `CR` terminal**
removido, sem `splitlines()` —, com `CR` residual, `U+2028`, `U+2029`, `U+0085`, `VT`, `FF` e
`U+00A0` permanecendo **conteúdo literal**. **Seções `Rxx` homônimas** são **preservadas**:
produzem **múltiplos pares em ordem física**, **não são deduplicadas**, **não usam `dict`**, e
a unicidade global **continua fora desta fronteira**. **`PARCIAL` é extraído literalmente**
e **continua NÃO canonicalizado, NÃO propagado, NÃO mapeado e NÃO resolvido** — o módulo
**não importa `response_status`** e **não chama `canonicalizar_status`**; **EXTRAIR `PARCIAL`
NÃO É RESOLVER `PARCIAL`**, e o **mapeamento concreto de `PARCIAL` permanece ABERTO**.
**Baseline funcional corrente: `3703 passed`**, com **`299 passed`** no direcionado da C12,
em **Python 3.14.5** — delta **+299** sobre os **`3404 passed`** anteriores (**3404 + 299 =
3703**), **executados sob `-W error`**, **zero failures, zero errors, zero warnings** e
**nenhum teste preexistente alterado**, no `.venv` do projeto. Esses números são **evidência
da entrega funcional C12**, e **NÃO** uma execução desta reconciliação documental: **nenhum
`pytest` foi executado aqui**, porque **zero código, zero teste e zero `knowledge/**`
mudaram**. **Não houve CI configurado** para a PR #113 nem para o merge commit — *statuses*
= 0, *workflow runs* = 0 — **AUSÊNCIA DE CI/CHECKS — NÃO FALHA DE CI**. **A C12 NÃO**
canonicaliza status, **NÃO** implementa a propagação `SP1`–`SP7`, **NÃO** resolve
`PARCIAL`, **NÃO** cria índice, **NÃO** executa a bijeção física, **NÃO** cria *bindings*,
**NÃO** implementa *placeholder*, `caminho_yaml`, `hora` ou **C-7**, **NÃO** executa
equivalência, **NÃO** renderiza, **NÃO** integra *runtime* e **NÃO** migra autoridade.
**EXTRAIR O RÓTULO NÃO É CANONICALIZAR STATUS, NÃO É PROPAGAR STATUS, NÃO É RESOLVER
`PARCIAL` E NÃO É MATERIALIZAR `C`.** **Limites inalterados**: **`C` continua ARBITRADA /
NÃO MATERIALIZADA**; **`C-A5` continua MATERIALIZADA no corpus** e **`C-A5-M2` continua
ATIVA**; `knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE**; a **bijeção
física continua NÃO EXECUTADA**; a **autoridade de status continua NÃO MIGRADA** (**C-11**);
**`C-A1-ST6`–`C-A1-ST10` continuam NÃO satisfeitas**; e continuam **ABERTOS** o mapeamento
concreto de `PARCIAL`, a implementação da propagação `SP1`–`SP7`, a sintaxe de
*placeholder*, a gramática de `caminho_yaml`, o formato `hora` e **C-7**. **C12 É AGORA A
ÚLTIMA ENTREGA FUNCIONAL INTEGRADA**; a C11 passa a **histórico anterior**, com o seu registro
**preservado**. A **3B.8 continua INEXISTENTE** e **nenhuma subetapa foi criada**. O **item
documental 97** abaixo **NÃO é "subetapa 97"**, **NÃO é `E12` nem `E13`**, **NÃO é
identificador normativo de `C`**, **NÃO é nova microentrega funcional** e **NÃO cria a
3B.8** — é **somente** a reconciliação documental pós-C12. **C13 NÃO FOI ESCOLHIDA, NÃO FOI
PLANEJADA E NÃO FOI INICIADA**: nenhuma pendência é eleita aqui, e a escolha da próxima ação
funcional exige planejamento separado após a integração desta reconciliação.

**Atualização anterior — 2026-09-05 (micro-arbitragem documental — gramática física do rótulo
de status no cabeçalho `Rxx`), preservada como registro daquele momento.** Aquela entrega é
**EXCLUSIVAMENTE DOCUMENTAL**: altera **somente**
`docs/07-arquitetura-motor-respostas.md` e este documento, e **não altera código, testes,
`knowledge/**`, `prompts/**` nem `CLAUDE.md`. **ELA NÃO É MARCO FUNCIONAL** e **NÃO É a
décima segunda microentrega funcional de `C`**. Ela fecha **uma única** matéria: **qual é a
gramática física determinística do rótulo de status em um cabeçalho `Rxx`**, registrada em
`docs/07` no bloco **"Gramática física do rótulo de status no cabeçalho `Rxx`"**, com os
rótulos **`GR1`–`GR7`** — **locais daquele bloco**, de referência interna, e que **NÃO são
etapa, subetapa, `Exx` nem nomenclatura normativa de `C`**, e que **NÃO criam a 3B.8**. A
forma física arbitrada, chamada **`G2`** naquele bloco, é **`## Rxx — <titulo> — <rotulo>`**,
com o **separador literal de três caracteres `U+0020 U+2014 U+0020`** — **SPACE + EM DASH +
SPACE**. Em resumo: a gramática aplica-se **exclusivamente** a uma linha que **já satisfaça a
forma estrutural de cabeçalho `## Rxx`** reconhecida pelas regras vigentes, e **NÃO define
ordem de chamadas entre módulos**, **NÃO decide composição técnica** e **NÃO altera `C8`,
`C-A5`, `C-A1-ST` ou `SP1`–`SP7`** (`GR1`); o separador ocorre **exatamente duas vezes**,
título e rótulo são **não vazios**, nenhum deles começa ou termina com **espaço `U+0020`** ou
**tab `U+0009`**, **terceira ocorrência** e **menos de duas** são **inválidas**, `-`
(`U+002D`) e `–` (`U+2013`) **não** equivalem ao separador, espaçamento divergente **não é
corrigido**, `strip`/`lstrip`/`rstrip`/normalização/colapso/inferência/tolerância implícita
são **proibidos**, e o rótulo obtido é **literal/opaco**, sem decidir pertença a `ST1`–`ST3`
(`GR2`); o rótulo é **literal e opaco**, com a tradução das três linhas automáticas
continuando em `canonicalizar_status(...)`, **não alterado** (`GR3`); forma divergente é
**recusada** *fail-closed*, com as espécies de impedimento nomeadas **apenas conceitualmente**
— separador ausente, cardinalidade diferente de 2, segmento vazio, branco de borda — e **sem**
decidir exceção, mensagem, módulo, função ou assinatura (`GR4`); o título é **obrigatório para
satisfazer a forma**, **não** é o produto da futura extração e **não** recebe semântica
comercial nova (`GR5`); uma **futura** fronteira poderá produzir a associação entre `Rxx` e
`rotulo_literal`, **sem** que nome, assinatura, retorno, exceção, mensagem, ordem de chamadas
ou composição sejam fixados aqui (`GR6`); e a arbitragem **NÃO** fecha `PARCIAL`, a
representação física do seu mapeamento, o índice, *bindings*, *placeholder*, `caminho_yaml`,
`hora`, **C-7**, a bijeção física, `ST6`–`ST10` ou a migração de autoridade (`GR7`).
**`PARCIAL` é fisicamente extraível por `G2` e continua NÃO RESOLVIDO**: **sem** tradução
automática, **sem** propagação automática, **não** é quarto status, **continua sob
`C-A1-ST4`** e **sob `SP4`/`SP5`**, pendente de **mapeamento explícito futuro** —
**EXTRAIR `PARCIAL` NÃO É RESOLVER `PARCIAL`**. **Relação correta com `C-A5-X2`, sem reescrita
retroativa**: aquela regra registrou **duas** matérias abertas — a **propagação** e o
**mapeamento concreto de `PARCIAL`** —; após `SP1`–`SP7` a **propagação** ficou **fechada
semanticamente** e o **mapeamento de `PARCIAL` continua ABERTO**; **a gramática física do
rótulo é uma lacuna SEPARADA**, de modo que esta entrega **NÃO esgota `C-A5-X2`**, **NÃO fecha
"a segunda metade" de `C-A5-X2`** e **NÃO resolve `PARCIAL`**. **`C8` permanece inalterado** —
`src/casa77_sdr/response_markdown_units.py` **não foi tocado** —, e **nenhuma ordem técnica de
chamadas foi decidida**. **`C-1`–`C-15`, `C-A1-ST`, `C-A5`, `MT1`–`MT12` e `SP1`–`SP7` foram
PRESERVADOS LITERALMENTE**, sem reescrita, renumeração ou substituição, e **nenhuma seção
existente foi renumerada**. **Evidência de compatibilidade, jamais fonte normativa**, medida
**read-only** e **reverificada mecanicamente** sobre o blob
`3bfb2e9fd18bac016e1dbe2c963ff916ceb0c96c`, **sem reproduzir conteúdo comercial**: **30**
cabeçalhos `## Rxx`, **30/30 conformes a `G2`**, **0** divergentes, **0** títulos contendo o
separador literal, **exatamente 60** ocorrências de `U+2014` nos cabeçalhos `Rxx` — **duas por
cabeçalho** —, **0** ocorrências de `U+002D` ou `U+2013` nesses cabeçalhos, e **quatro**
rótulos físicos distintos: `APROVADO`, `AGUARDA APROVAÇÃO`, `APROVADO com handoff
obrigatório` e `PARCIAL`. **Nenhuma alteração do corpus é exigida, e nenhuma foi feita.**
**Nenhum `pytest` foi executado nesta entrega** — **zero código, zero teste e zero
`knowledge/**`** —, e a **baseline funcional permanece `3404 passed`** em **Python 3.14.5**,
sobre o **commit funcional `4b6ea8ca00c171275d75ea17c4414011a4f1a835`**, que **continua o
último commit funcional aprovado**, da **C11 — extração determinística do texto emitível
canônico**, que **continua a última entrega funcional**. **EFEITO EXATO SOBRE A C12: A C12
FUNCIONAL DE EXTRAÇÃO DO RÓTULO PASSA A SER PLANEJÁVEL, SUJEITA A PLANEJAMENTO TÉCNICO E
AUDITORIA SEPARADOS** — ela **NÃO** está pronta, **NÃO** foi escolhida e **NÃO** foi iniciada.
Continuam inalterados: **`C` ARBITRADA / NÃO MATERIALIZADA**; **`C-A5` MATERIALIZADA no
corpus** e **`C-A5-M2` ATIVA**; `knowledge/indice-respostas-aprovadas.yaml` **INEXISTENTE**; a
**bijeção física NÃO EXECUTADA**; a **autoridade de status NÃO MIGRADA** (**C-11**);
**`C-A1-ST6`–`C-A1-ST10` NÃO satisfeitas**; e **ABERTOS** o mapeamento concreto de `PARCIAL`,
a sintaxe de *placeholder*, a gramática de `caminho_yaml`, o formato `hora` e **C-7**. A
**3B.8 continua INEXISTENTE** e **nenhuma subetapa, `E11` ou `E12` foi criada**. O **item
documental 96** abaixo **NÃO é "subetapa 96"**, **NÃO é `E11` nem `E12`**, **NÃO é marco
funcional** e **NÃO cria a 3B.8**.

**Atualização anterior — 2026-09-05 (micro-arbitragem documental — propagação do status de
`Rxx` aos fragmentos), preservada como registro daquele momento.** Aquela entrega é
**EXCLUSIVAMENTE DOCUMENTAL**: altera **somente**
`docs/07-arquitetura-motor-respostas.md` e este documento, e **não altera código, testes,
`knowledge/**`, `prompts/**` nem `CLAUDE.md`. **ELA NÃO É MARCO FUNCIONAL** e **NÃO É a
décima segunda microentrega funcional de `C`**. Ela fecha **uma única** matéria, antes
explicitamente em aberto por **`C-A5-X2`**: **como o status de um `Rxx`, uma vez que o seu
rótulo já tenha sido corretamente identificado, é propagado aos fragmentos emitíveis daquele
`Rxx`**. A alternativa adotada é **PROPAGAÇÃO UNIFORME / FAIL-CLOSED**, registrada em
`docs/07` no bloco **"Propagação do status de `Rxx` aos fragmentos"**, com os rótulos
**`SP1`–`SP7`** — **locais daquele bloco**, de referência interna, e que **NÃO são etapa,
subetapa, `Exx` nem nomenclatura normativa de `C`**. Em resumo: a regra opera
**conceitualmente** sobre um `Rxx`, os seus fragmentos emitíveis declarados e um rótulo **já
corretamente identificado**, e **não extrai coisa alguma do Markdown** (`SP1`); quando o
rótulo for **exatamente** uma das **três** traduções automáticas de **`C-A1-ST1`–`C-A1-ST3`**,
o status canônico correspondente é aplicado **uniformemente a TODOS os fragmentos emitíveis
daquele `Rxx`**, pela tradução **já materializada** por `canonicalizar_status(...)`, **sem
quarta tradução** e **sem alterar `C-3`** (`SP2`); dentro desse `Rxx` é **proibido** decidir
status por posição, ordem, índice, redação, conteúdo, quantidade de fragmentos ou `id`, **sem
exceção implícita** (`SP3`); **`PARCIAL` permanece integralmente sujeito a `C-A1-ST4`** —
**sem tradução automática, sem propagação automática e sem conversão em qualquer status** —,
de modo que, **enquanto não existir mapeamento explícito aprovado no nível dos fragmentos
emitíveis, o status dos fragmentos daquele `Rxx` permanece NÃO RESOLVIDO**, *fail-closed* e
**sem inferência** (`SP4`); qualquer rótulo fora de `ST1`–`ST3` **não produz status
propagado**, e a ausência de tradução **não é corrigida, normalizada nem inferida** (`SP5`);
o status propagado é **DERIVADO** da autoridade Markdown vigente, **não cria declaração de
status adicional** no Markdown — **`C-2d`** preservada —, e o futuro índice poderá armazenar
status por fragmento conforme **`C-2i`** **sem que isso migre a autoridade** (`SP6`); e
propagar status **NÃO** cria índice, **NÃO** cria fragmento, **NÃO** altera identidade,
**NÃO** extrai rótulo, **NÃO** resolve `PARCIAL`, **NÃO** executa a bijeção física, **NÃO**
satisfaz `ST6`, `ST7`, `ST8` integralmente, `ST9` ou `ST10`, **NÃO** migra autoridade e
**NÃO** materializa `C` (`SP7`). **LIMITE DURO DO ESCOPO — PRÉ-CONDIÇÃO, NÃO RESULTADO**: a
expressão **"rótulo já corretamente identificado"** é **pré-condição** desta arbitragem, e
**NENHUMA GRAMÁTICA DE CABEÇALHO FOI ARBITRADA** — **como localizar o rótulo na linha física
do cabeçalho, separadores, posição física do rótulo, gramática do título, *parsing* de
`## Rxx` e algoritmo de extração do rótulo continuam ABERTOS**, como decisão normativa/técnica
**futura e separada**, e **não** foram atribuídos por antecipação a um futuro executor;
**nem sequer uma "regra mínima" de *parsing* foi arbitrada**. **`C-1`–`C-15`, `C-A1-ST`,
`C-A5` e `MT1`–`MT12` foram PRESERVADOS LITERALMENTE**: não foram reescritos, renumerados nem
substituídos, e **nenhuma seção existente foi renumerada**. **`C-A5-X2` fica fechada apenas na
sua PRIMEIRA metade** — a propagação —, permanecendo **ABERTO** o **mapeamento concreto de
`PARCIAL`**; **`C-A5-X3` e `C-A5-X4` permanecem literais e inalteradas**. **`response_status.py`
NÃO foi alterado** e **nenhum propagador foi implementado**: **zero módulo, zero função, zero
assinatura, zero exceção e zero mensagem** foram decididos. O corpus **não foi consultado como
fundamento normativo** e **não foi alterado**. **Nenhum `pytest` foi executado nesta entrega**
— **zero código, zero teste e zero `knowledge/**`** —, e a **baseline funcional permanece
`3404 passed`** em **Python 3.14.5**, sobre o **commit funcional
`4b6ea8ca00c171275d75ea17c4414011a4f1a835`**, que **continua o último commit funcional
aprovado**, da **C11 — extração determinística do texto emitível canônico**, que **continua a
última entrega funcional**. **A DÉCIMA SEGUNDA MICROENTREGA FUNCIONAL DE `C` (C12 FUNCIONAL)
CONTINUA NÃO ESCOLHIDA, NÃO PLANEJADA E NÃO INICIADA**: esta arbitragem **não** a torna
pronta e apenas fecha a semântica acima. Continuam inalterados: **`C` ARBITRADA / NÃO
MATERIALIZADA**; **`C-A5` MATERIALIZADA no corpus** e **`C-A5-M2` ATIVA**;
`knowledge/indice-respostas-aprovadas.yaml` **INEXISTENTE**; a **bijeção física NÃO
EXECUTADA**; a **autoridade de status NÃO MIGRADA** (**C-11**);
**`C-A1-ST6`–`C-A1-ST10` NÃO satisfeitas**; e **ABERTAS** a **extração física / gramática do
rótulo do cabeçalho**, o mapeamento concreto de `PARCIAL`, a sintaxe de *placeholder*, a
gramática de `caminho_yaml`, o formato `hora` e **C-7**. A **3B.8 continua INEXISTENTE** e
**nenhuma subetapa, `E11` ou `E12` foi criada**. O **item documental 95** abaixo **NÃO é
"subetapa 95"**, **NÃO é `E11` nem `E12`**, **NÃO é marco funcional** e **NÃO cria a 3B.8**.

**Atualização anterior — 2026-09-05 (reconciliação documental pós-merge da DÉCIMA PRIMEIRA
MICROENTREGA FUNCIONAL DE `C` — extração determinística do texto emitível canônico),
preservada como registro daquele momento.** Aquela
entrega é **EXCLUSIVAMENTE DOCUMENTAL**: altera **somente** este documento, e **não altera
código, testes, `knowledge/**`, `docs/07-arquitetura-motor-respostas.md`, `prompts/**` nem
`CLAUDE.md`. **A DÉCIMA PRIMEIRA MICROENTREGA FUNCIONAL DE `C` ESTÁ INTEGRADA À `main`** pelo
**PR #109** — **commit funcional `4b6ea8ca00c171275d75ea17c4414011a4f1a835`**
(`feat: add deterministic emittable response text extraction`), **merge commit
`ceecd638131899974ce43b4685b254bf01d7bbad`** (merge commit **normal**, dois parents:
`690a09c2a5…` e `4b6ea8ca00…`), branch de origem `feat/c-emittable-text-extraction`. Ela
adiciona **dois arquivos novos** — `src/casa77_sdr/response_emittable_text.py` (**+478**, blob
`ff811210cc59f9c50b7f019d1d6798af9083439f`) e `tests/test_response_emittable_text.py`
(**+1253**, blob `156bbbf86d42e6cd1a3474ed111b12115dec5d0a`) —, **2 arquivos, +1731 / −0**,
**zero arquivo preexistente alterado**. A fronteira entregue é
`extrair_textos_emitiveis(texto: str) -> tuple[tuple[str, str], ...]`, com **`__all__` de
exatamente dois nomes** — `TextoEmitivelInvalido` e `extrair_textos_emitiveis` —, devolvendo,
**em ordem física do documento**, um par `(token_canonico, texto_canonico)` por unidade
emitível declarada. Ela materializa **`MT3`–`MT11`** do bloco **"Conversão do bloco marcado
em texto canônico"** de `docs/07`, sem reabrir norma: a **primeira** operação é
`ler_unidades_marcadas(texto)` — **C8 continua o único juiz estrutural da representação
marcada**, e `RepresentacaoMarcadaInvalida` **propaga intacta**, sem `try`/`except`, sem
reclassificação e sem tocar `__cause__`/`__context__` —; **só depois** a C11 localiza
fisicamente as mesmas unidades declaradas, deriva de novo o token **somente** do `Rxx` do
cabeçalho e do `id` do marcador — **nunca** por posição, ordem, `zip` ou conteúdo
(**`C-A5-I5`**) —, e **verifica a sequência local de tokens contra a saída de C8 antes de
devolver qualquer par**; divergência interna produz `RuntimeError("invariante_estrutural")`,
**defeito interno**, não entrada inválida. Convenção materializada: prefixo de conteúdo
**exatamente `> `**; linha `>` interna **única** projeta **`\n\n`**; linha `>` em borda e duas
ou mais linhas `>` consecutivas são **recusadas**; linhas consecutivas de conteúdo projetam
**exatamente um `LF`**, **não convertido em espaço**; `LF` e `CRLF` físicos **aceitos**, com o
`CR` **do par** removido; **`CR` isolado — inclusive no EOF, sem `LF` subsequente — é
recusado**; **EOF sem newline é aceito**; `U+2028`, `U+2029`, `U+0085`, `U+000B` e `U+000C`
**recusados**; espaço ou tab **antes do terminador** recusado; **nenhuma correção
silenciosa**. Categorias técnicas privadas e fechadas — **não** identificadores normativos
de `C`: `prefixo_invalido`, `linha_vazia_invalida`, `terminador_proibido` e
`branco_antes_do_terminador`. **A C11 NÃO** valida equivalência, **NÃO** aplica `NFC`,
**NÃO** converte quebra suave em espaço, **NÃO** lê arquivo, YAML ou índice, **NÃO**
resolve *binding* ou status, **NÃO** propaga status, **NÃO** resolve `PARCIAL`, **NÃO**
implementa *placeholder*, `caminho_yaml`, `hora` ou **C-7**, **NÃO** executa a bijeção
física, **NÃO** materializa `C` e **NÃO** integra *runtime*: **`C-15b` continua no
comparador existente**, **C8 continua estrutural** e **C10 continua a composição de
domínios de identidade**. **Baseline funcional corrente: `3404 passed`**, com **`218 passed`**
no direcionado da C11, em **Python 3.14.5** — delta **+218** sobre os **`3186 passed`**
anteriores (**3186 + 218 = 3404**), **os mesmos totais sob `-W error`** e **nenhum teste
preexistente alterado**. Ressalva ambiental **objetiva, não pendência funcional**: o comando
com o `python` global não tinha o pacote instalado, e os testes canônicos da entrega foram
executados no `.venv` do projeto, também em Python 3.14.5. Esses números são **evidência da
entrega funcional C11**, e **NÃO** uma execução desta reconciliação documental: **nenhum
`pytest` foi executado aqui**, porque **zero código, zero teste e zero `knowledge/**`
mudaram**. **Não houve CI configurado** para a PR #109 nem para o merge commit — **AUSÊNCIA
DE CI/CHECKS — NÃO FALHA DE CI**. **EXTRAIR TEXTO CANÔNICO NÃO É VALIDAR EQUIVALÊNCIA, NÃO É
EXECUTAR A BIJEÇÃO FÍSICA E NÃO É MATERIALIZAR `C`.** **Limites inalterados**: **`C` continua
ARBITRADA / NÃO MATERIALIZADA**; **`C-A5` continua MATERIALIZADA no corpus** e **`C-A5-M2`
continua ATIVA**; `knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE**; a
**bijeção física do corpus real continua NÃO EXECUTADA**; a **autoridade de status continua
NÃO MIGRADA** (**C-11**); **`C-A1-ST6`–`C-A1-ST10` continuam NÃO satisfeitas** — **a C11 NÃO
satisfaz `ST10`**; e continuam **ABERTAS** a propagação de status ao fragmento, o mapeamento
concreto de `PARCIAL`, a sintaxe de *placeholder*, a gramática de `caminho_yaml`, o formato
`hora` e **C-7**. A **3B.8 continua INEXISTENTE** e **nenhuma subetapa foi criada**. O **item
documental 94** abaixo **NÃO é "subetapa 94"**, **NÃO é `E11` nem `E12`** e **NÃO cria a
3B.8**. **C12 NÃO FOI ESCOLHIDA, NÃO FOI PLANEJADA E NÃO FOI INICIADA.**

**Atualização anterior — 2026-09-04 (micro-arbitragem documental — conversão do bloco marcado
em texto canônico), preservada como registro daquele momento.** Aquela entrega é
**EXCLUSIVAMENTE DOCUMENTAL**: altera **somente**
`docs/07-arquitetura-motor-respostas.md` e este documento, e **não altera código, testes,
`knowledge/**`, `prompts/**` nem `CLAUDE.md`. **ELA NÃO É MARCO FUNCIONAL** e **NÃO É a
décima primeira microentrega funcional de `C`**. Ela fecha **uma única** matéria, antes
explicitamente em aberto: **como um bloco físico emitível de `C-A5-U1` é convertido
deterministicamente em uma `str` do domínio canônico `D1`–`D7`, ou recusado *fail-closed***. A
convenção adotada é **ESTRITA / FAIL-CLOSED**, registrada em `docs/07` no bloco **"Conversão
do bloco marcado em texto canônico"**, com os rótulos **`MT1`–`MT12`** — **locais daquele
bloco**, de referência interna, e que **NÃO são etapa, subetapa, `Exx` nem nomenclatura
normativa de `C`**. Em resumo: a **fronteira física de `C-A5-U1` permanece literal** e o
**reconhecimento estrutural continua distinto da conversão textual** (`MT1`, `MT2`); a linha
de conteúdo é **exatamente `>` + um espaço ASCII + conteúdo não vazio**, com o prefixo
**`> `** — dois caracteres — removido **sem `lstrip`, `strip`, CommonMark ou tolerância
implícita** (`MT3`), e prefixos divergentes são **recusados** (`MT4`); a linha vazia interna é
**`>` sozinho** e projeta **exatamente `\n\n`** (`MT5`), enquanto **duas ou mais** linhas `>`
consecutivas (`MT6`) e linha `>` **em borda** (`MT7`) são **recusadas**; o extrator aceita
**`LF` e `CRLF`** como terminador **físico**, removendo o `CR` do par e **nunca** deixando
`CR` na saída, com `CR` isolado, `U+2028`, `U+2029`, `U+0085`, `U+000B` e `U+000C`
**recusados** e **sem universal newline implícito** (`MT8`); a **quebra suave** projeta
**exatamente um `LF`**, e a conversão `LF` → `U+0020` **permanece com `C-15b`** (`MT9`);
whitespace antes do terminador é **recusado**, não corrigido (`MT10`); há **dois desfechos** —
`str` canônica não vazia ou recusa explícita (`MT11`) —; e a **taxonomia técnica de exceções,
nomes e assinaturas NÃO é decidida** aqui (`MT12`). **`D3`, `D4` e `D5` foram PRESERVADAS
LITERALMENTE**: não foram reescritas, renumeradas nem substituídas — aquele bloco define o
**domínio de chegada**, e esta arbitragem define **somente como se chega nele**; em
particular, `D5` continua valendo para a representação canônica e a adaptação física de
`CRLF` fica **do lado do extrator**, exatamente onde `D5` já a colocava. **O leitor da
representação marcada NÃO foi alterado**: `ler_unidades_marcadas` continua responsável apenas
por reconhecimento estrutural, identidade e tokens `<Rxx>/<id>`. O corpus foi consultado
**read-only** como **evidência de compatibilidade, jamais como origem normativa**, e
**reverificado mecanicamente** sobre o blob `3bfb2e9fd18bac016e1dbe2c963ff916ceb0c96c`: **37**
blocos emitíveis, **29** multilinha, **73/73** linhas de conteúdo na forma exata `> `, **0**
linha vazia interna, **0** linha vazia em borda, **0** par de linhas vazias consecutivas,
**0** linha com espaço ou tab antes do terminador, **0** linha fora das duas formas admitidas
e **0** ocorrência de `CR`, `U+2028`, `U+2029`, `U+0085`, `U+000B` ou `U+000C` — **nenhuma
alteração do corpus é exigida, e nenhuma foi feita**. **Nenhum `pytest` foi executado nesta
entrega** — **zero código, zero teste e zero `knowledge/**`** —, e a **baseline funcional
permanece `3186 passed`** em **Python 3.14.5**, sobre o **commit funcional
`6265b823cb20aab0395840f8125008121de27e43`**, que **continua o último commit funcional
aprovado**. **A DÉCIMA PRIMEIRA MICROENTREGA FUNCIONAL DE `C` CONTINUA NÃO ESCOLHIDA E NÃO
INICIADA**: esta arbitragem apenas **destrava** o seu futuro planejamento. Continuam
inalterados: **`C` ARBITRADA / NÃO MATERIALIZADA**; **`C-A5` MATERIALIZADA no corpus** e
**`C-A5-M2` ATIVA**; `knowledge/indice-respostas-aprovadas.yaml` **INEXISTENTE**; a **bijeção
física NÃO EXECUTADA**; a **autoridade de status NÃO MIGRADA** (**C-11**);
**`C-A1-ST6`–`C-A1-ST10` NÃO satisfeitas**; e **ABERTAS** a propagação de status ao fragmento,
o mapeamento concreto de `PARCIAL`, a sintaxe de *placeholder*, a gramática de `caminho_yaml`,
o formato `hora` e **C-7**. A **3B.8 continua INEXISTENTE** e **nenhuma subetapa, `E11` ou
`E12` foi criada**. O **item documental 93** abaixo **NÃO é "subetapa 93"** e **NÃO cria a
3B.8**.

**Atualização anterior — 2026-09-04 (reconciliação documental pós-merge da DÉCIMA
MICROENTREGA FUNCIONAL DE `C` — composição determinística em memória da correspondência
canônica), preservada como registro daquele momento.** Aquela
entrega é **EXCLUSIVAMENTE DOCUMENTAL**: altera **somente** este documento, e **não altera
código, testes, `knowledge/**`, `docs/07-arquitetura-motor-respostas.md`, `prompts/**` nem
`CLAUDE.md`. **A DÉCIMA MICROENTREGA FUNCIONAL DE `C` ESTÁ INTEGRADA À `main`** pelo
**PR #106** — **commit funcional `6265b823cb20aab0395840f8125008121de27e43`**
(`feat: add deterministic canonical response correspondence composition`), **merge commit
`457e29a42472d44175d72031cff05ec1a1ebf9d1`**, branch de origem
`feat/c-response-correspondence`. Ela adiciona **dois arquivos novos** —
`src/casa77_sdr/response_correspondence.py` (**+118**, blob
`e3e895246f42a0a5f60c61b7cb68b2a922559134`) e `tests/test_response_correspondence.py`
(**+725**, blob `b4ba305e51dd166596def93a6381209802b23330`) —, **2 arquivos, +843 / −0**,
**zero arquivo preexistente alterado**. A fronteira entregue é
`validar_correspondencia_canonica(indice: object, texto_markdown: str) -> None`, com
**`__all__` de exatamente um nome**. Ela materializa **somente uma composição determinística
em memória**, na **ordem fixa**: **1.** o domínio do índice por
`derivar_tokens_do_indice(indice)` (C9); **2.** o domínio do Markdown por
`ler_unidades_marcadas(texto_markdown)` (C8); **3.** a relação **diagonal** `(token, token)`,
um par por token do domínio do índice, na ordem em que ele os devolveu; **4.** o julgamento
por `validar_bijecao(...)` (C6), chamado **uma única vez**. A correspondência é **por
identidade canônica** — **nunca** por posição, **nunca** por ordem, **nunca** por `zip`,
**nunca** por conteúdo e **nunca** por normalização —, rastreando a **`C-A5-T1`** (identidade
`<Rxx>/<id>`), **`C-A5-T3`** (composição injetiva e decomposição unívoca pelas formas
fechadas), **`C-A5-T4`** (o mesmo token nos **dois** domínios de **`C-A1-B3`** /
**`C-A1-B4`**), **`C-A5-T5`** (token derivado, nunca armazenado) e **`C-A5-I5`** (identidade
declarada, jamais derivada de posição, ordem, índice, redação ou conteúdo). **A C10 NÃO cria
juiz novo**: **C9 continua responsável** pelo domínio do índice, **C8 continua responsável**
pelo domínio do Markdown e **C6 continua o único juiz** da bijeção sobre os domínios
recebidos — a C10 **apenas compõe** essas três fronteiras. As exceções
**`ProjecaoDeIdentidadeInvalida`**, **`RepresentacaoMarcadaInvalida`** e **`BijecaoInvalida`**
**propagam intactas**, e **nenhuma exceção nova foi criada**. **Baseline funcional corrente:
`3186 passed`**, com **`75 passed`** no direcionado da C10, em **Python 3.14.5** — delta
**+75** sobre os **`3111 passed`** anteriores (**3111 + 75 = 3186**), **os mesmos totais sob
`-W error`** e **nenhum teste preexistente alterado**. Esses números são **evidência da
entrega funcional C10**, e **NÃO** uma execução desta reconciliação documental: **nenhum
`pytest` foi executado aqui**, porque **zero código, zero teste e zero `knowledge/**`
mudaram**. **Não houve CI configurado** para a PR #106 — **ausência de checks, não falha de
CI**. **COMPOR E VALIDAR EM MEMÓRIA NÃO É EXECUTAR A BIJEÇÃO FÍSICA E NÃO É MATERIALIZAR
`C`**: o sucesso da C10 **não** prova a existência do índice físico, que a estrutura recebida
seja o índice oficial, que o Markdown recebido seja o corpus oficial, a completude ou a
aprovação do corpus, a validade integral do índice por `validar_indice`, a execução física da
bijeção 37/37, a satisfação de **`C-A1-ST6`–`C-A1-ST10`** nem a migração da autoridade de
status. **Limites inalterados**: **`C` continua ARBITRADA / NÃO MATERIALIZADA**; **`C-A5`
continua MATERIALIZADA no corpus** e **`C-A5-M2` continua ATIVA**;
`knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE**; a **bijeção física do
corpus real continua NÃO EXECUTADA**; a **autoridade de status continua NÃO MIGRADA**
(**C-11**); **`C-A1-ST6`–`C-A1-ST10` continuam NÃO satisfeitas**; e continuam **ABERTAS** a
propagação de status ao fragmento, o mapeamento concreto de `PARCIAL`, a sintaxe de
*placeholder*, a gramática de `caminho_yaml`, o formato `hora` e **C-7**. A **3B.8 continua
INEXISTENTE** e **nenhuma subetapa foi criada**. O **item documental 92** abaixo **NÃO é
"subetapa 92"**, **NÃO é `E12`** e **NÃO cria a 3B.8**. **A DÉCIMA PRIMEIRA MICROENTREGA
FUNCIONAL DE `C` NÃO É ESCOLHIDA NESTA ENTREGA DOCUMENTAL** e **NENHUMA C11 FOI INICIADA.**

**Atualização anterior — 2026-09-04 (reconciliação documental pós-merge da NONA
MICROENTREGA FUNCIONAL DE `C` — derivador determinístico dos tokens canônicos do lado do
índice), preservada como registro daquele momento.** Aquela
entrega é **EXCLUSIVAMENTE DOCUMENTAL**: altera **somente** este documento, e **não altera
código, testes, `knowledge/**`, `docs/07-arquitetura-motor-respostas.md`, `prompts/**` nem
`CLAUDE.md`. **A NONA MICROENTREGA FUNCIONAL DE `C` ESTÁ INTEGRADA À `main`** pelo
**PR #104** — **commit funcional `45876ca609716ede51aefcf8752dd29f98a736a7`**
(`feat: add deterministic response index token derivation`), **merge commit
`654aaedec2d424ab4184e7a71a0d3c129021abf8`**, branch de origem
`feat/c-response-index-tokens`. Ela adiciona **dois arquivos novos** —
`src/casa77_sdr/response_index_tokens.py` (**+286**, blob
`84b69472a702a6d436729dbe40a89cf4fcc07bb0`) e `tests/test_response_index_tokens.py`
(**+895**, blob `90bf631403bf2ba7c463348a660f64766f9104aa`) —, **2 arquivos, +1181 / −0**,
**zero arquivo preexistente alterado**. A fronteira entregue é
`derivar_tokens_do_indice(indice: object) -> tuple[str, ...]`, que recebe a **estrutura já em
memória** e deriva o **domínio de tokens canônicos `<Rxx>/<id>` do lado do índice**, a partir
da **projeção mínima** — raiz, `respostas`, o `id` de cada resposta e o `id` de cada
fragmento — e **de nada além dela**. Ela usa o token de **`C-A5-T1`** com o separador `/` de
**`C-A5-T2`**, **deriva sem armazenar** (**`C-A5-T5`**), aplica **`C-A5-I3`** ao
`fragmentos[].id`, preserva a unicidade **local ao `Rxx`** do fragmento (**`C-A5-I4`**,
**C-2h**) e a unicidade **global** do `Rxx` (**C-2a**). Ela **NÃO substitui
`validar_indice`** — `status`, `bindings`, `itera_sobre`, *placeholder*, `caminho_yaml`,
`formato`, `predicado`, mecanismo, origem e chaves desconhecidas **não são julgados aqui** —
e **NÃO executa a bijeção**. **Baseline funcional corrente: `3111 passed`**, com **`201
passed`** e **`203 passed`** nos direcionados de C8 e C9, em **Python 3.14.5** — delta
**+203** sobre os **`2908 passed`** anteriores, **todos sob `-W error` limpo**. Esses números
são a **baseline funcional confirmada na entrega C9**, **não** uma execução desta
reconciliação: **nenhum `pytest` foi executado aqui**, porque **zero código, zero teste e
zero `knowledge/**` mudaram**. **Não houve CI configurado** para a PR #104 — **ausência de
CI, não falha de CI**. **DERIVAR UM DOMÍNIO DE TOKENS NÃO É EXECUTAR A BIJEÇÃO E NÃO É
MATERIALIZAR `C`.** **Limites inalterados**: **`C` continua ARBITRADA / NÃO MATERIALIZADA**;
`knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE**; a **bijeção física
continua NÃO EXECUTADA**; a **autoridade de status continua NÃO MIGRADA** (**C-11**);
**`C-A1-ST6`–`C-A1-ST10` continuam NÃO satisfeitas**; e continuam **ABERTAS** a propagação de
status ao fragmento, o mapeamento concreto de `PARCIAL`, a sintaxe de *placeholder*, a
gramática de `caminho_yaml`, o formato `hora` e **C-7**. **`C-A5` continua MATERIALIZADA no
corpus** e **`C-A5-M2` continua ATIVA**. A **3B.8 continua INEXISTENTE** e **nenhuma subetapa
foi criada**. O **item documental 91** abaixo **NÃO é "subetapa 91"**, **NÃO é `E11`** e
**NÃO cria a 3B.8**. **A DÉCIMA MICROENTREGA FUNCIONAL DE `C` NÃO É ESCOLHIDA NESTA ENTREGA
DOCUMENTAL.**

**Atualização anterior — 2026-09-04 (reconciliação documental pós-merge da OITAVA
MICROENTREGA FUNCIONAL DE `C` — leitor/validador determinístico da representação marcada
`C-A5`), preservada como registro daquele momento.** Aquela entrega é **EXCLUSIVAMENTE
DOCUMENTAL**: altera **somente** este documento, e **não altera
código, testes, `knowledge/**`, `docs/07-arquitetura-motor-respostas.md`, `prompts/**` nem
`CLAUDE.md`. **A OITAVA MICROENTREGA FUNCIONAL DE `C` ESTÁ INTEGRADA À `main`** pelo
**PR #102** — **commit funcional `341084d951b428d80c4ba573fbc38a4bc9f008c6`**
(`feat: add deterministic C-A5 markdown unit reader`), **merge commit
`067e894db8bddb96c192d7da3a4431f587f4efc0`**, branch de origem
`feat/c-response-markdown-units`. Ela adiciona **dois arquivos novos** —
`src/casa77_sdr/response_markdown_units.py` (**+396**, blob
`3c99d89aa0028f673548f5cc932ec166d592cd7f`) e `tests/test_response_markdown_units.py`
(**+1535**, blob `ee3dc335b3d94588d183c8ebe64771e45df08c14`) —, **2 arquivos, +1931 / −0**,
**zero arquivo preexistente alterado**. O **corpus permanece no blob
`3bfb2e9fd18bac016e1dbe2c963ff916ceb0c96c`**, **inalterado**. O **VALIDADOR PERMANENTE DA
REPRESENTAÇÃO MARCADA `C-A5` passa a existir na `main`**: `ler_unidades_marcadas(texto: str)
-> tuple[str, ...]`, que recebe Markdown **já em memória** e devolve **exclusivamente** os
tokens canônicos `<Rxx>/<id>` de **`C-A5-T1`**, cobrindo as **sete redações fail-closed de
`C-A5-X1`** por **seis categorias técnicas privadas** mais `tipo_invalido` — **nenhuma oitava
falha foi criada**. **Baseline funcional corrente: `2908 passed`**, com **`201 passed`** no
direcionado, em **Python 3.14.5** — delta **+201** sobre os **`2707 passed`** anteriores.
**Limites inalterados**: **`C-A5` = MATERIALIZADA no corpus** e **`C-A5-M2` = ATIVA** desde o
merge da materialização; mas **`C` continua ARBITRADA / NÃO MATERIALIZADA**;
`knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE**; a **bijeção física
continua NÃO EXECUTADA**; a **autoridade de status continua NÃO MIGRADA** (**C-11**);
**`C-A1-ST6`–`C-A1-ST10` continuam NÃO satisfeitas**; e continuam **ABERTAS** a propagação de
status ao fragmento, o mapeamento concreto de `PARCIAL`, a sintaxe de *placeholder*, a
gramática de `caminho_yaml`, o formato `hora` e **C-7**. **LER A REPRESENTAÇÃO MARCADA NÃO É
MATERIALIZAR `C`.** A **3B.8 continua INEXISTENTE** e **nenhuma subetapa foi criada**. Esta
reconciliação **também torna inequívoca a proveniência da prova byte-a-byte do item 89** —
os valores de **9 712 bytes / 253 LF / 253 CR** descrevem a **representação do checkout
`CRLF`** usada naquela execução histórica, e a **prova Git canônica** da preservação é o blob
reconstruído **`d9f275454cb9f091a824292560d983d25f08c14e`**; **a evidência histórica não é
substituída**. O **item documental 90** abaixo **NÃO é "subetapa 90"**, **NÃO é `E10`** e
**NÃO cria a 3B.8**. **A PRÓXIMA MICROENTREGA FUNCIONAL DE `C` NÃO FOI ESCOLHIDA NESTA
ENTREGA DOCUMENTAL.**

**Atualização anterior — 2026-09-03 (materialização física `C-A5` — aplicação dos 37
marcadores aprovados), preservada como registro daquele momento.** Aquela entrega é
**EDITORIAL E DOCUMENTAL**: altera **somente**
`knowledge/respostas-aprovadas.md` e este documento, e **não altera código, testes,
`docs/07-arquitetura-motor-respostas.md`, `knowledge/casa77.yaml`,
`knowledge/informacoes-pendentes.md` nem `prompts/**`**. Sob **autorização humana
explícita**, os **37 marcadores `<!-- fragmento: <id> -->`** foram aplicados ao corpus
**exatamente conforme o mapeamento `C-A5-M5` já aprovado** — **zero identidade nova**,
**zero identidade derivada de posição ou ordem** (**`C-A5-I5`**, **`C-A5-M6`**). O **diff do
corpus é exatamente `+37 / −0`**: **nenhuma linha preexistente foi alterada, removida ou
reordenada**, **nenhum texto emitível foi tocado**, **nenhum status foi alterado**, **nenhum
cabeçalho foi alterado** e **nenhuma normalização de EOL permanece no estado final**.
**Prova byte-a-byte**:
removidas **exclusivamente** as 37 linhas de marcador com seus terminadores, o corpus
reconstruído é **binariamente idêntico** ao estado anterior — **SHA-256
`7cf1aa058c851a6642f5af0d0600a8a66091b09b70d4a58989b26a2aad6db344`**, **9 712 bytes**, **253
LF**, **253 CR**. O **corpus-base imediatamente anterior a esta entrega** é
`knowledge/respostas-aprovadas.md`, blob **`d9f275454cb9f091a824292560d983d25f08c14e`**.
**Regra de vigência deste registro**: **enquanto esta entrega não pertencer ao histórico da
`main`**, o **corpus canônico permanece no estado imediatamente anterior**, **`C-A5-M2`
continua NÃO ATIVA**, os **37 marcadores constituem somente representação candidata na
branch/PR**, a **ausência de marcador não é erro** e **nenhum bloco fica fail-closed**
(**`C-A5-M3`**); **a partir do primeiro estado da `main` que contiver conjuntamente esta
entrega e os 37 marcadores**, por **`C-A5-M1`** / **`C-A5-M2`**, **`C-A5-M2` = ATIVA** e
**`C-A5` = MATERIALIZADA no corpus**, passando também a vincular **`C-A5-X1`** e
**`C-A5-I6`** — efeito **automático**, sem necessidade de nova reconciliação. Estrutura
reconferida após a edição: **30 `Rxx`**, **37 blocos de citação contíguos**, **24 de
fragmento único** e **6 multi-fragmento** (`R05` = 3; `R09`, `R11`, `R12`, `R23`, `R25` = 2
cada); **37 marcadores**, todos na forma exata e com `id` conforme **`C-A5-I3`**;
**pareamento marcador↔bloco = 37/37** sem marcador órfão e sem bloco sem marcador; **zero
`id` duplicado dentro do
mesmo `Rxx`** (**`C-A5-I4`**, **C-2h**); e **correspondência integral com a tabela
`C-A5-M5`** — **37 correspondências, zero ausente, zero extra, zero divergente**. **Nenhum
dado comercial foi alterado**: **zero preço, capacidade, horário, percentual ou condição**.
**Nenhum código e nenhum teste novo**: a suíte existente foi **reexecutada sem alteração** e
permanece em **`2707 passed`** sob `-W error`, em **Python 3.14.5**, sobre o **commit
funcional `4749efa74d5684b52b4f457176710ba6e212c627`**. Continuam inalterados: o **índice
`knowledge/indice-respostas-aprovadas.yaml` INEXISTENTE**; a **bijeção física NÃO
EXECUTADA**; a **autoridade de status NÃO migrada** (**C-11**); **C ARBITRADA / NÃO
MATERIALIZADA**; **`C-A1-ST6`–`C-A1-ST10` NÃO satisfeitas**; e as lacunas **ABERTAS** de
propagação de status, `PARCIAL`, *placeholder*, `caminho_yaml`, `hora` e **C-7**. **Nenhum
validador permanente da representação marcada foi implementado nesta entrega.** **A OITAVA
MICROENTREGA FUNCIONAL CONTINUA NÃO ESCOLHIDA E NÃO INICIADA** e a **3B.8 continua
INEXISTENTE**. O **item documental 89** abaixo **NÃO é "subetapa 89"**, **NÃO é `E9`** e
**NÃO é a oitava nem a nona microentrega funcional de `C`**.

**Atualização anterior — 2026-09-03 (Fase A2 — registro documental do mapeamento humano
aprovado `C-A5-M5`, 37/37), preservada como registro daquele momento.** Aquela entrega é
**EXCLUSIVAMENTE DOCUMENTAL**: altera **somente**
`docs/07-arquitetura-motor-respostas.md` e este documento, e **não altera código, testes,
`knowledge/**` nem `prompts/**`**. O responsável humano **aprovou explicitamente** o
mapeamento de identidade das **37 unidades físicas atuais**, **incluindo `R23/F2` como a
unidade de decoração**, e a **tabela completa** foi registrada em `docs/07`, no bloco
**"Registro pós-C-A5-M5 — mapeamento humano aprovado das 37 unidades"**, com estado
**APROVADO HUMANAMENTE / REGISTRADO DOCUMENTALMENTE / NÃO APLICADO AO CORPUS**. O
**corpus-base** do mapeamento é `knowledge/respostas-aprovadas.md`, **blob
`d9f275454cb9f091a824292560d983d25f08c14e`**, que **permanece INALTERADO**. **Fechamento**:
**37** unidades, **30 `Rxx`**, **24** de fragmento único e **6** multi-fragmento (`R05` = 3;
`R09`, `R11`, `R12`, `R23`, `R25` = 2 cada); por base, **8 PRESERVAÇÃO NORMATIVA**, **1
CONFIRMAÇÃO HUMANA EXPLÍCITA** e **28 DECISÃO HUMANA EXPLÍCITA** — **8 + 1 + 28 = 37**, com
**zero unidade sem `id` aprovado**, **zero duplicata de `id` dentro do mesmo `Rxx`**
(**`C-A5-I4`**, **C-2h**) e **todos os `id` conformes a `C-A5-I3`**. **Os 24 `Rxx` de
fragmento único receberam `F1` por DECISÃO HUMANA EXPLÍCITA — NÃO por derivação posicional
nem por serem únicos**; **`R09` recebeu `F1`/`F2` por decisão humana explícita**, sendo
`bloco 1` e `bloco 2` **apenas localizadores de evidência** (**`C-A5-M6`**); **`R11` e `R12`
tiveram suas lacunas fechadas por decisão humana explícita** — `R11/F1` na unidade de
duração/limite e `R12/F2` na unidade de não incluso, **sem qualquer justificativa de
ordem**; e os **8 compromissos normativos anteriores foram preservados** (`R05/F1`, `R05/F2`,
`R05/F3`, `R11/F2`, `R12/F1`, `R23/F1`, `R25/F1`, `R25/F2`), conforme **`C-A5-M5`** e
**`C-A5-E7`**. A pendência de **`R23/F2`** foi **resolvida humanamente**: **`R23/F2` designa
fisicamente a unidade de decoração**; **`C-A2-B5` e `MD-13` permanecem históricos e não são
reescritos**, o **escopo de modelagem de `MD-13` pode envolver fatos de mais de um
fragmento**, e a referência histórica de `MD-13` a `R23 F2` **não desloca o motivo de fogos
de `R23/F1`** — **`MD-13` NÃO é executada aqui**. **Estado após esta entrega**: **`C-A5-M5` =
SATISFEITA DOCUMENTALMENTE para esse corpus-base**; **`C-A5-M2` CONTINUA NÃO ATIVA**;
**ZERO marcador `C-A5` aplicado** e a **ausência de marcador continua NÃO sendo erro do
corpus atual** (**`C-A5-M3`**); **`C-A5` continua NÃO MATERIALIZADA no corpus**; **C continua
ARBITRADA / NÃO MATERIALIZADA**; `knowledge/indice-respostas-aprovadas.yaml` **continua
INEXISTENTE**; a **bijeção física continua NÃO EXECUTADA** e **`C-A1-ST6`–`C-A1-ST10`
continuam NÃO satisfeitas**; a **autoridade de status NÃO migrou** (**C-11**); e continuam
**ABERTAS** a propagação de status ao fragmento, o mapeamento de `PARCIAL`, a sintaxe de
*placeholder*, a gramática de `caminho_yaml`, o formato `hora` e **C-7**. **NENHUM `pytest`
FOI EXECUTADO NESTA ENTREGA** — **zero código, zero teste, zero `knowledge/**`** — e a
**baseline funcional permanece `2707 passed`**, com **`261 passed`** no direcionado, em
**Python 3.14.5**, **preservada como a última baseline funcional confirmada anteriormente**,
sobre o **commit funcional `4749efa74d5684b52b4f457176710ba6e212c627`**. **Nenhum marco
funcional novo é criado**; a **3B.7** continua a última subetapa numerada, a **3B.8 continua
INEXISTENTE** e **A OITAVA MICROENTREGA FUNCIONAL CONTINUA NÃO ESCOLHIDA E NÃO INICIADA**. O
**item documental 88** abaixo **NÃO é "subetapa 88"**, **NÃO é `E8`** e **NÃO é a oitava
microentrega funcional**.

**Atualização anterior — 2026-09-03 (micro-arbitragem documental `C-A5` — identidade física
do fragmento emitível), preservada como registro daquele momento.** Aquela entrega é
**EXCLUSIVAMENTE DOCUMENTAL**: altera **somente**
`docs/07-arquitetura-motor-respostas.md` e este documento, e **não altera código, testes,
`knowledge/**` nem `prompts/**`**. **`C-A5` = ARBITRADA DOCUMENTALMENTE / NÃO
MATERIALIZADA.** Ela fecha a **única** matéria que `C-A1` registrava como explicitamente
**não decidida** e que esta entrega encerra — a **identidade física do fragmento** —,
fixando: a **unidade emitível física futura** como **bloco de citação contíguo** dentro de
uma seção `## Rxx` (`C-A5-U`); o **marcador** `<!-- fragmento: <id> -->` na **linha
imediatamente anterior** ao bloco, com **gramática fechada de `id`** (`F` + inteiro decimal
ASCII maior que zero, sem zero à esquerda), **unicidade apenas dentro do `Rxx`** — o que
**preserva literalmente `C-2h`** — e **identidade declarada, nunca derivada** de posição,
ordem, linha, offset, índice, redação, whitespace, conteúdo comercial, hash, timestamp,
UUID sem regra de governança, LLM, banco ou serviço externo (`C-A5-I`); a **identidade
canônica `<Rxx>/<id>`**, **derivada e nunca armazenada**, **sem campo novo no futuro
índice** (`C-A5-T`); a **ativação diferida** (`C-A5-M`); e os **limites e falhas futuras**
(`C-A5-X`). **`C-A5` ARBITRA UMA REPRESENTAÇÃO FUTURA E NÃO ATIVA ESSA REPRESENTAÇÃO NO
CORPUS ATUAL**: `knowledge/respostas-aprovadas.md` **não foi alterado**, o corpus continua
**fisicamente sem marcadores `C-A5`**, a **ausência de marcador NÃO é erro** e **nenhum
bloco existente fica fail-closed** por esta arbitragem. Evidência **estritamente
read-only** do corpus: **30 `Rxx`**, **37 blocos de citação contíguos**, **24 `Rxx` com um
fragmento**, **6 `Rxx` multi-fragmento**, **zero comentários HTML existentes** e **zero
marcador `C-A5` aplicado** — **COMPATIBILIDADE ESTRUTURAL = 37/37**, que é **distinta** do
**MAPEAMENTO DE IDENTIDADE PARA APLICAÇÃO, NÃO PRODUZIDO / NÃO APROVADO**. **Nenhum `id`
foi atribuído**, **nenhuma tabela dos 37 foi produzida ou aprovada** e **nenhum caso
individual foi decidido**; **IDs de fragmento já comprometidos por documentação normativa
anterior deverão ser preservados** na futura aplicação, e **`R09` continua PENDÊNCIA DE
MAPEAMENTO HUMANO**, com **dois fragmentos físicos sem `id` `C-A5` normativamente
atribuído**. **Nenhum teste foi reexecutado nesta entrega** — **zero código, zero teste,
zero `knowledge/**`** —, e a **baseline funcional permanece `2707 passed`** / **`261
passed`** no direcionado, em **Python 3.14.5**, como **última baseline funcional
confirmada anteriormente**, sobre o **commit funcional
`4749efa74d5684b52b4f457176710ba6e212c627`** e o **merge
`8c67e13808da59dbace413fce33c2c22280e69a3`**. Continuam inalterados: a **sétima
microentrega** como **última entrega funcional**; a **3B.7** como **última subetapa
numerada**; a **3B.8 INEXISTENTE**; a **autoridade de status NÃO migrada** (**C-11**); **C
ARBITRADA / NÃO MATERIALIZADA**; o **índice `knowledge/indice-respostas-aprovadas.yaml`
INEXISTENTE**; a **bijeção física NÃO executada**; **`C-A1-ST6`–`C-A1-ST10` NÃO
satisfeitas**; e as lacunas **ABERTAS** de **propagação de status ao fragmento**,
**mapeamento explícito de `PARCIAL`**, **sintaxe de *placeholder***, **gramática de
`caminho_yaml`**, **formato `hora`** e **`C-7`**. **A OITAVA MICROENTREGA FUNCIONAL
CONTINUA NÃO ESCOLHIDA E NÃO INICIADA**, e o **item documental 87** abaixo **NÃO é
"subetapa 87"**, **NÃO é `E8`** e **NÃO é a oitava microentrega funcional**.

**Atualização anterior — 2026-09-02 (reconciliação documental após o merge do PR #97),
preservada como registro daquele momento.** A **PR #97**
foi **auditada, autorizada humanamente e integrada à `main`** — commit funcional
`4749efa74d5684b52b4f457176710ba6e212c627`, merge `8c67e13808da59dbace413fce33c2c22280e69a3`,
branch de origem `feat/c-response-status`, título
`feat: add deterministic response status canonicalizer`, integrada em
**2026-09-02T20:47:15Z**. Ela materializou a **sétima microentrega funcional de `C` — o
canonicalizador determinístico de rótulo de status já extraído**, em
`src/casa77_sdr/response_status.py` e `tests/test_response_status.py` — **dois arquivos
novos**, **1255 adições / 0 remoções**, **nenhum arquivo preexistente alterado**. **Esta
entrega passa a ser o marco funcional** da `main`, **sem numeração de subetapa** e **sem
criar nomenclatura normativa `E2`–`E7`**: a **3B.7** continua a última numerada e a **3B.8
continua INEXISTENTE**. A **baseline funcional passa a `2707 passed`** — **`261 passed`** no
direcionado do canonicalizador —, em **Python 3.14.5**, com **zero failures e zero errors**;
**`261`** e **`2707`** também sob `-W error`, **medidas sobre a `main` integrada após o
merge** e **reexecutadas nesta reconciliação após a edição**. A fronteira traduz **somente as
três linhas com tradução automática arbitrada** em `C-A1-ST1`–`C-A1-ST3`: **`APROVADO` →
`APROVADO`**, **`AGUARDA APROVAÇÃO` → `AGUARDA_APROVACAO`** e **`APROVADO com handoff
obrigatório` → `APROVADO`** — o **sufixo de handoff não é transportado**, por ser instrução
operacional fora de `C` (C-2f, C-5.1). O **rótulo chega já extraído**; ele precisa ser `str`
**exata** — **subclasse de `str` é recusada antes de qualquer consulta à tabela**, porque
poderia redefinir `__eq__`/`__hash__` —, a **comparação é literal**, com **zero
normalização**, **zero coerção**, **zero conversão** e **zero tolerância**, e a validação é
**fail-closed** com precedência fixa **tipo → pertença → retorno**. As **categorias técnicas
privadas e fechadas** são **`tipo_invalido`** e **`rotulo_nao_mapeado`**, com **localizador
único `rotulo`**; a mensagem tem a forma `<categoria>: <localizador>` e **nunca ecoa** o
rótulo, o conteúdo, o `repr`, o tipo concreto, um comprimento ou um índice. O módulo importa
**apenas** `__future__`: **zero I/O**, **zero *filesystem***, **zero YAML**, **zero
*locale***, **zero rede**, **zero LLM**, **zero relógio**, **zero calendário**, **zero
variável de ambiente**, **zero dependência interna de `casa77_sdr.*`** e **zero export** por
`casa77_sdr/__init__.py`. **`PARCIAL` continua SEM tradução automática** e **continua
exigindo mapeamento explícito no nível dos fragmentos emitíveis** (`C-A1-ST4`) — recusa
registrada como `rotulo_nao_mapeado`, que significa **"não há tradução automática nesta
fronteira"**, jamais **"não arbitrado"**. **`BLOQUEADO` não recebeu mapeamento automático
inventado**: `C-A1-ST5` trata de `BLOQUEADO` **em nota interna**, que **não cria fragmento** e
**não cria status**, e esta fronteira não recebe esse contexto. **CANONICALIZAR STATUS NÃO É
MATERIALIZAR `C`**: a entrega **não extrai rótulo do Markdown**, **não extrai fragmento**,
**não cria identidade física de fragmento**, **não cria nem lê o índice real**, **não resolve
*bindings***, **não executa a bijeção física**, **não prova completude do corpus**, **não
satisfaz `C-A1-ST6`–`C-A1-ST10`**, **não migra a autoridade de status** e **não integra
consumidor**. **A autoridade de status NÃO migrou**: `knowledge/respostas-aprovadas.md`
**continua a autoridade** (`C-11`) enquanto as cinco condições de `C-A1-ST6`–`C-A1-ST10` não
valerem integralmente, e o status **não é removido do Markdown**. O índice
`knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE** e **`C`, como entrega
completa do índice estruturado, continua ARBITRADA / NÃO MATERIALIZADA**. Continuam
inalterados: o formato **`hora` NÃO MATERIALIZADO**, **`R2` NÃO MATERIALIZADA**, **`S2-D8`
ARBITRADA / NÃO MATERIALIZADA**, **`N-b-RES2` ABERTO**, o **`OrquestradorMotor` NÃO
IMPLEMENTADO**, a **3B.8 INEXISTENTE** e **`Q2`–`Q5` NÃO RESOLVIDAS**. **A próxima
microentrega funcional de `C` ainda NÃO foi escolhida nem iniciada.**

**Atualização anterior — 2026-09-02 (reconciliação documental após o merge do PR #95),
preservada como registro daquele momento.** A **PR #95**
foi **auditada, autorizada humanamente e integrada à `main`** — commit funcional
`bdd0b2acc415ab6307c7c8da2adbad15f42cb75f`, merge `b06c0a43bd2f96b8712638e99c55edfe2fb2f99f`,
branch de origem `feat/c-response-bijection`, título
`feat: add deterministic response bijection validator`, integrada em **2026-09-02T13:26:46Z**.
Ela materializou a **sexta microentrega funcional de `C` — o verificador determinístico da
correspondência bijetiva de `C-A1-B3` / `C-A1-B4` sobre domínios já fornecidos pelo
chamador**, em `src/casa77_sdr/response_bijection.py` e `tests/test_response_bijection.py` —
**dois arquivos novos**, **1472 adições / 0 remoções**, **nenhum arquivo preexistente
alterado**. **Esta entrega passa a ser o marco funcional** da `main`, **sem numeração de
subetapa** e **sem criar nomenclatura normativa `E2`, `E3`, `E4`, `E5` ou `E6`**: a **3B.7**
continua a última numerada e a **3B.8 continua INEXISTENTE**. A **baseline funcional passa a
`2446 passed`** — **`284 passed`** no direcionado do verificador —, em **Python 3.14.5**, com
**zero failures e zero errors**; **`284`** e **`2446`** também sob `-W error`, **medidas
após o merge** sobre a `main` integrada e **reexecutadas nesta reconciliação após a edição**.
O verificador julga **uma única coisa**: se a relação recebida é **bijetiva entre os dois
domínios recebidos** — fragmentos do índice e unidades emitíveis do Markdown são **tokens
opacos**, `str` **exata** (subclasse de `str` **recusada**), cada item da relação é uma
`tuple` **exata** (subclasse de `tuple` **recusada**) de **exatamente dois lados**, a
comparação usa **igualdade nativa exata de `str`**, **sem normalização**, **sem coerção**,
**sem *parsing*** e **sem I/O**, com validação **fail-closed** e precedência **fixa**; **três
domínios vazios são bijeção trivial válida somente sobre os domínios fornecidos**. **A
completude correta dos dois domínios é pré-condição do chamador** e **não é verificável nesta
fronteira**. **VERIFICAR A BIJEÇÃO NÃO É MATERIALIZAR `C`**: a função **não extrai
fragmentos do índice**, **não extrai unidades do Markdown**, **não decide o que é unidade
emitível**, **não define identidade física de fragmento**, **não cria identificadores**,
**não lê índice real**, **não prova completude dos dois domínios**, **não executa a bijeção
física do corpus real**, **não satisfaz `C-A1-ST7` isoladamente**, **não migra autoridade de
status** e **não integra consumidor**. O índice `knowledge/indice-respostas-aprovadas.yaml`
**continua INEXISTENTE** e **`C`, como entrega completa do índice estruturado, continua
ARBITRADA / NÃO MATERIALIZADA**. Continuam inalterados: o formato **`hora` NÃO
MATERIALIZADO**, **`R2` NÃO MATERIALIZADA**, **`S2-D8` ARBITRADA / NÃO MATERIALIZADA**,
**`N-b-RES2` ABERTO**, o **`OrquestradorMotor` NÃO IMPLEMENTADO**, a **3B.8 INEXISTENTE** e
**`Q2`–`Q5` NÃO RESOLVIDAS**. **A próxima microentrega funcional de `C` ainda NÃO foi
escolhida nem iniciada.**

**Atualização anterior — 2026-09-01 (reconciliação documental após o merge do PR #93),
preservada como registro daquele momento.** A **PR #93**
foi **auditada, autorizada humanamente e integrada à `main`** — commit funcional
`efa903816b5dc1dafbce8161f6424abdf41f2ca6`, merge `353e1b42d6c8b31d649f59b151184811ef51462e`,
branch de origem `feat/c-response-assertion`, título
`feat: add deterministic assertion evaluator`, integrada em **2026-09-01T18:00:57Z**.
Ela materializou a **quinta microentrega funcional de `C` — o avaliador determinístico
booleano de `ASSERTIVA` sobre valor já resolvido**, em
`src/casa77_sdr/response_assertion.py` e `tests/test_response_assertion.py` — **dois arquivos
novos**, **948 adições / 0 remoções**, **nenhum arquivo preexistente alterado**. **Esta
entrega passa a ser o marco funcional** da `main`, **sem numeração de subetapa** e **sem
criar nomenclatura normativa `E2`, `E3`, `E4` ou `E5`**: a **3B.7** continua a última
numerada e a **3B.8 continua INEXISTENTE**. A **baseline funcional passa a `2162 passed`** —
**`254 passed`** no direcionado do avaliador —, em **Python 3.14.5**, com **zero failures e
zero errors**; **`254`** e **`2162`** também sob `-W error`. O avaliador julga **somente o
domínio booleano estrito** de um valor **já resolvido pelo chamador**, sobre o vocabulário
fechado **`EH_VERDADEIRO`** / **`EH_FALSO`** (C-5g, C-5h, C-A1-R): **valor não booleano é NÃO
AVALIÁVEL** e levanta `AssertivaNaoAvaliavel` — **jamais convertido em `False`** —, **sem
*truthiness***, **sem `bool(...)`**, **sem coerção**, **sem *parsing***, **sem normalização**
e **sem *fallback***. Essa recusa é **delimitação técnica fail-closed desta microentrega**, e
**não** expansão normativa de `C-7`, que trata especificamente de `null` e `pendente`.
**Nenhum domínio futuro adicional de `ASSERTIVA` foi arbitrado**: ampliar a avaliação para
outro domínio **exigiria contrato posterior explícito**. O módulo importa **apenas**
`__future__`: **zero I/O**, **zero *filesystem***, **zero YAML**, **zero *locale***, **zero
rede**, **zero LLM**, **zero calendário**, **zero dependência interna de `casa77_sdr.*`** e
**zero export** por `casa77_sdr/__init__.py`. **AVALIAR `ASSERTIVA` NÃO É MATERIALIZAR
`C`**: o índice `knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE**,
**nenhum consumidor foi integrado**, e **`C`, como entrega completa do índice estruturado,
continua ARBITRADA / NÃO MATERIALIZADA**. Continuam inalterados: o formato **`hora` NÃO
MATERIALIZADO**, **`R2` NÃO MATERIALIZADA**, **`S2-D8` ARBITRADA / NÃO MATERIALIZADA**,
**`N-b-RES2` ABERTO**, o **`OrquestradorMotor` NÃO IMPLEMENTADO**, a **3B.8 INEXISTENTE** e
**`Q2`–`Q5` NÃO RESOLVIDAS**. Esta reconciliação **não escolhe nem inicia a sexta
microentrega funcional de `C`**.

**Atualização anterior — 2026-09-01 (reconciliação documental após o merge do PR #91),
preservada como registro daquele momento.** A **PR #91**
foi **auditada, autorizada humanamente e integrada à `main`** — commit funcional
`7d8dd8617eb5cd8c346e67496c3631feafe97f4f`, merge `d15201b0a84bca332b09e0d5e623736605663962`,
branch de origem `feat/c-response-formatters`, título
`feat: add deterministic response formatters`, integrada em **2026-09-01T14:03:24Z**.
Ela materializou a **quarta microentrega funcional de `C` — os formatadores determinísticos
de apresentação pura de `C-6`**, em `src/casa77_sdr/response_format.py` e
`tests/test_response_format.py` — **dois arquivos novos**, **1367 adições / 0 remoções**,
**nenhum arquivo preexistente alterado**. **Esta entrega passa a ser o marco funcional** da
`main`, **sem numeração de subetapa** e **sem criar nomenclatura normativa `E2`, `E3` ou
`E4`**: a **3B.7** continua a última numerada e a **3B.8 continua INEXISTENTE**. Foram
materializados **cinco** dos seis formatos do vocabulário fechado de `C-6` — **`inteiro`**,
**`inteiro_agrupado`**, **`simbolo_moeda`**, **`texto`** e **`lista`**; o formato **`hora`
NÃO foi materializado** e permanece **fora**, por **lacuna normativa ainda não arbitrada**
sobre a escolha mecânica entre `HH:MM` e `Hh` (`C-A1-F3`). A **baseline funcional passa a
`1908 passed`** — **`319 passed`** no direcionado dos formatadores —, em **Python 3.14.5**,
com **zero failures e zero errors**; **`319`** e **`1908`** também sob `-W error`. Os
formatadores são **funções puras** sobre valores já resolvidos: **zero I/O**, **zero
*filesystem***, **zero YAML**, **zero *locale***, **zero rede**, **zero LLM**, **zero
dependência interna de `casa77_sdr.*`** e **zero export** por `casa77_sdr/__init__.py`.
**FORMATAR NÃO É MATERIALIZAR `C`**: o índice `knowledge/indice-respostas-aprovadas.yaml`
**continua INEXISTENTE**, **nenhum consumidor foi integrado**, e **`C`, como entrega completa
do índice estruturado, continua ARBITRADA / NÃO MATERIALIZADA**. Continuam inalterados:
**`R2` NÃO MATERIALIZADA**, **`S2-D8` ARBITRADA / NÃO MATERIALIZADA**, **`N-b-RES2` ABERTO**,
o **`OrquestradorMotor` NÃO IMPLEMENTADO**, a **3B.8 INEXISTENTE** e **`Q2`–`Q5` NÃO
RESOLVIDAS**. Esta reconciliação **não escolhe nem inicia a quinta microentrega funcional de
`C`**.

**Atualização anterior — 2026-08-31 (reconciliação documental após o merge do PR #89),
preservada como registro daquele momento.** A **PR #89**
foi **auditada, autorizada humanamente e integrada à `main`** — commit funcional
`23e3fa727eb1457cd98a0e0e6f36580dade2ab00`, merge `76531de7d3f4257d84b5a1f9498d8666c4e60030`,
branch de origem `feat/c-response-equivalence`, título `feat: add response text equivalence`.
Ela materializou a **terceira microentrega funcional de `C` — o comparador determinístico de
equivalência textual de `C-15b`**, em `src/casa77_sdr/response_equivalence.py` e
`tests/test_response_equivalence.py` — **dois arquivos novos**, **965 adições / 0 remoções**,
**nenhum arquivo preexistente alterado**. **Esta entrega passa a ser o marco funcional** da
`main`, **sem numeração de subetapa** e **sem criar nomenclatura normativa `E2` ou `E3`**: a
**3B.7** continua a última numerada e a **3B.8 continua INEXISTENTE**. A **baseline funcional
passa a `1589 passed`** — **`153 passed`** no direcionado do comparador —, em **Python
3.14.5**, com **zero failures e zero errors**; **`153`** e **`1589`** também sob `-W error`.
O comparador opera **exclusivamente sobre duas `str` já em representação canônica**: ele
**não é analisador de Markdown**, **não faz I/O** e **não conhece o índice**. **COMPARAR NÃO É
MATERIALIZAR `C`**: o índice `knowledge/indice-respostas-aprovadas.yaml` **continua
INEXISTENTE**, e **`C`, como entrega completa do índice estruturado, continua ARBITRADA / NÃO
MATERIALIZADA**. Continuam inalterados: **`R2` NÃO MATERIALIZADA**, **`S2-D8` ARBITRADA / NÃO
MATERIALIZADA**, **`N-b-RES2` ABERTO**, o **`OrquestradorMotor` NÃO IMPLEMENTADO**, a **3B.8
INEXISTENTE** e **`Q2`–`Q5` NÃO RESOLVIDAS**. Esta reconciliação **não escolhe nem inicia a
quarta microentrega funcional de `C`**.

**Atualização anterior — 2026-08-31 (micro-arbitragem documental da representação canônica de
`C-15b`), preservada como registro daquele momento.** Entrega **exclusivamente documental**, em `docs/07-arquitetura-motor-respostas.md`
— bloco **"Representação canônica de entrada para `C-15b`"**, logo após `C-15e` — e neste
documento. Ela **fecha a REPRESENTAÇÃO DE ENTRADA** sobre a qual a equivalência textual de
`C-15` será futuramente julgada, adotando **texto canônico já extraído**: duas `str` em
representação canônica, quebra suave como `LF` isolado convertido em um único espaço,
`\n\n` como fronteira de parágrafo real, **somente `LF`** como terminador admitido, e três
desfechos distintos — **NÃO DETERMINÁVEL**, **NÃO EQUIVALENTE** e **EQUIVALENTE**. Registra
como **ressalva normativa** que, **fora do domínio canônico, não existe garantia de correção
do veredito de equivalência**. **`C-15a`–`C-15e` NÃO foram renumeradas nem reescritas** e
**nenhum identificador normativo novo foi criado**. **Ela NÃO cria marco funcional**: **não
implementa o comparador**, **não cria módulo, teste, extrator, *renderer* ou índice**, **não
faz *parsing* Markdown** e **não altera `src/`, `tests/`, `knowledge/**` ou `prompts/**`**. O
**último marco funcional continua o PR #86** — commit funcional
`b2b11e2465c7f332747a806c80b629e995f0f5a6`, merge
`9bf68b8fece9ea66c74509490ddf6e02a0aa6f31` —, a **baseline permanece `1436 passed`** /
Python 3.14.5 — **reexecutada e confirmada nesta entrega, antes e depois da edição** —, a
**3B.7** continua a última subetapa numerada e a **3B.8 continua INEXISTENTE**. **`C` continua
ARBITRADA / NÃO MATERIALIZADA como entrega completa**, o índice
`knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE**, **`R2` continua NÃO
MATERIALIZADA**, **`S2-D8` continua ARBITRADA / NÃO MATERIALIZADA**, **`N-b-RES2` continua
ABERTO** e o **`OrquestradorMotor` continua NÃO IMPLEMENTADO**. A **candidata seguinte
continua sendo a futura terceira microentrega funcional de `C` — a equivalência textual —, que
NÃO é materializada aqui**; com esta arbitragem ela passa a ter **contrato de entrada
fechado**. **Nenhuma nomenclatura `E2` é criada.** A **próxima etapa**, caso esta arbitragem
seja integrada, é o **planejamento/mandato técnico da equivalência textual**, **sujeito a nova
auditoria do GPT**.

**Atualização anterior — 2026-08-31 (reconciliação documental após o merge do PR #86),
preservada como registro daquele momento.** A **PR #86**
foi **auditada, autorizada humanamente e integrada à `main`** — commit funcional
`b2b11e2465c7f332747a806c80b629e995f0f5a6`, merge `9bf68b8fece9ea66c74509490ddf6e02a0aa6f31`,
branch de origem `feat/c-response-index-loader`. Ela materializou a **segunda microentrega
funcional de `C` — o carregador *fail-closed* do futuro índice**, em
`src/casa77_sdr/response_index_load.py` e `tests/test_response_index_load.py`, e removeu de
`tests/test_response_index.py` o teste `test_indice_real_continua_inexistente` — **três
arquivos**, **1086 adições / 5 remoções**. **Esta entrega passa a ser o marco funcional** da
`main`, **sem numeração de subetapa** e **sem criar a nomenclatura normativa `E2`**: a
**3B.7** continua a última numerada e a **3B.8 continua INEXISTENTE**. A **baseline funcional
passa a `1436 passed`** — **`63 passed`** no direcionado do carregador e **`158 passed`** no
direcionado de `E1` —, em **Python 3.14.5**, medida **após o merge**, com **zero failures e
zero errors**. O carregador **NÃO cria o índice real**:
`knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE**, e ele **não conhece
caminho implícito algum** — o caminho chega sempre por argumento explícito. Portanto **a
primeira e a segunda microentregas de `C` estão MATERIALIZADAS e INTEGRADAS**, mas **`C`, como
entrega completa do índice estruturado, continua ARBITRADA / NÃO MATERIALIZADA**. Continuam
inalterados: **`R2` NÃO MATERIALIZADA**, **`S2-D8` ARBITRADA / NÃO MATERIALIZADA**,
**`N-b-RES2` ABERTO**, o **`OrquestradorMotor` NÃO IMPLEMENTADO**, a **3B.8 INEXISTENTE** e
**`Q2`–`Q5` NÃO RESOLVIDAS**. Esta reconciliação **não escolhe nem inicia a próxima
microentrega funcional de `C`**.

**Atualização anterior — 2026-08-31 (reconciliação documental após o merge do PR #84),
preservada como registro daquele momento.** A **PR #84**
foi **auditada, autorizada humanamente e integrada à `main`** — commit funcional
`02f1dd6621c31b90789c646bd8826e685f9ee019`, merge `95ed2ce4e9c54f9bdfb7b3f820e6f9e065cde24e`,
branch de origem `feat/c-e1-response-index-validator`. Ela materializou **exclusivamente a
primeira microentrega funcional de `C`**, denominada **`E1`**: o **validador estrutural
fail-closed** do **futuro** índice `knowledge/indice-respostas-aprovadas.yaml`, em
`src/casa77_sdr/response_index.py` e `tests/test_response_index.py` — **dois arquivos novos**,
**1343 adições / 0 remoções**. **`E1` passa a ser o marco funcional** da `main`, **sem
numeração de subetapa**: a **3B.7** continua a última numerada e a **3B.8 continua
INEXISTENTE**. A **baseline funcional passa a `1374 passed`** — **`159 passed`** no teste
direcionado —, em **Python 3.14.5**, medida **após o merge**, com **zero failures e zero
errors**. **`E1` NÃO cria o índice real**: `knowledge/indice-respostas-aprovadas.yaml`
**continua INEXISTENTE**. Portanto **`E1` está MATERIALIZADA e INTEGRADA**, mas **`C`, como
entrega completa do índice estruturado, continua ARBITRADA / NÃO MATERIALIZADA**. Continuam
inalterados: **`R2` NÃO MATERIALIZADA**, **`S2-D8` ARBITRADA / NÃO MATERIALIZADA**,
**`N-b-RES2` ABERTO**, o **`OrquestradorMotor` NÃO IMPLEMENTADO**, a **3B.8 INEXISTENTE** e
**`Q2`–`Q5` NÃO RESOLVIDAS**. Esta reconciliação **não inicia `E2`** e **não escolhe a próxima
entrega funcional**.

**Atualização anterior — 2026-08-30 (resultado da nova execução oficial de `C-A2-N12`),
preservada como registro daquele momento.** A validação
**`C-8`** / **`C-15`** / **`C-A1`** foi **reexecutada integralmente**, de forma **estritamente
read-only**, contra `bd9687c69ddf7db9306363d5de4cf74072b5a134`, e o resultado oficial é
**`C-A2-N12` = CUMPRIDA**: cobertura de **37 de 37 fragmentos emitíveis** em **12 eixos** —
**444 de 444 resultados**, **265 `PASS`** e **179 `N/A`** —, com **0 `FAIL-CLOSED`**, **0 `NÃO
DETERMINÁVEL`** e **0 `DIVERGÊNCIA DE BASE`**. Em **`R22`**, **`C-8` = `PASS`** e **`C-15` =
`PASS`**: o bloqueio estrutural anterior foi **REMOVIDO** — e **não dispensado, contornado ou
relaxado** —, porque a natureza aproximada passou a existir como **fato estruturado próprio**
na base autoritativa. Com isso, **`C-A2-N9`**, **`C-A2-N10`**, **`C-A2-N11` (16/16)** e
**`C-A2-N12`** estão **todas CUMPRIDAS**. A execução **não materializou `C`**, **não criou o
índice**, **não alterou arquivo algum do repositório**, **não altera o último marco funcional**
e **não cria a 3B.8**. As entregas anteriores permanecem integradas: **`C-A4`** pelo **PR #79**,
a **reconciliação pós-`M8`** pelo **PR #78** e a **`M8`** pelo **PR #77**, com **`FE-11b` =
APLICADA / MATERIALIZADA POR REMOÇÃO**, **`FE-11a` = APLICADA / RECONCILIADA** e **`FE-11a′` =
NÃO CRIADA**. **`C` continua ARBITRADA / NÃO MATERIALIZADA**, o **índice continua inexistente**,
o **último marco funcional continua o PR #61**, a **baseline permanece `1215 passed`** e a
**3B.8 continua inexistente**.

## Referências

| Item | Valor |
|---|---|
| Projeto | Casa 77 SDR |
| Branch de referência | `main` |
| Último commit **funcional** aprovado | `cee95ebb6a725c3b91595589591fefa650d64196` |
| Merge correspondente na `main` | `6ae5cd829bb6eb9f4acfc60a061ee9b7e6d36180` |
| Última **entrega funcional** concluída | **Parser puro e determinístico da gramática de `caminho_yaml`** — a **linha 1 de `CY13`**, em `src/casa77_sdr/response_yaml_path.py` (**PR #131** — commit funcional `cee95ebb6a725c3b91595589591fefa650d64196`, parent `51fa44c4a9f5b65505f7668c1ce05e8b8f97dd68`, merge `6ae5cd829bb6eb9f4acfc60a061ee9b7e6d36180`, branch de origem `feat/caminho-yaml-parser`, título `feat: add caminho_yaml parser`). **NÃO é denominada `C15`, NÃO é `E15`, NÃO é `C-A6`, NÃO cria identificador normativo novo e NÃO cria a 3B.8** — é, tão somente, a **entrega funcional de código mais recente integrada**. **Sem nomenclatura normativa `E2`–`E7`** e **sem numeração de subetapa**. **Inclui**: **`analisar_caminho_yaml(caminho: str) -> tuple[bool, tuple[tuple[str, tuple[str, str] | None], ...]]`** como **fronteira pública** — **um único parâmetro**, **sem default** —, a **exceção pública única `CaminhoYamlInvalido`**, **`__all__` com exatamente dois nomes** — `["CaminhoYamlInvalido", "analisar_caminho_yaml"]` —, **sem DTO**, **sem dataclass**, **sem Enum** e **não** exportada por `casa77_sdr/__init__.py`. **Entrada**: a **`str` já em memória**, exigida como **`str` exata** — **subclasse de `str` é recusada** como `tipo_invalido`, **antes de qualquer leitura**. **Saída**: `(relativo, segmentos)` — a **decomposição imutável já validada** —, com `relativo` **`False`** para **absoluto** e **`True`** para **relativo**, e `segmentos` como `tuple` de pares `(chave, seletor)`, sendo `seletor` igual a **`None`** ou ao par `(chave_seletora, literal)`; **somente `bool`, `str`, `tuple` e `None`**. **`@` isolado devolve `(True, ())`**, sem inventar segmento. **Gramática materializada**: **absoluto sem marcador**; **relativo marcado por `@`** na posição inicial; **seletor `[chave=literal]`, no máximo um por segmento**; **chave exclusivamente numérica é NÃO ENDEREÇÁVEL** — tanto **chave de segmento** quanto **chave seletora** —, sem que isso afirme que "chave numérica = posição"; e **literal seletor exclusivamente numérico é PERMITIDO**, porque o literal é **sempre semanticamente uma `str`** (**`CY7`**). **Canonicalidade estrita**: recusa `str` vazia, *whitespace*, aspas, `\`, `/`, `-`, `:`, `*`, Unicode não ASCII, `.` inicial, `.` final, `..`, segmento vazio, seletor vazio, chave seletora vazia, literal vazio, `=` ausente, `[` sem `]`, `]` sem abertura, conteúdo após `]` no mesmo segmento, **dois seletores no mesmo segmento**, **`@` fora da primeira posição** e `@@`. **Falhas**: **três** categorias fechadas — **`tipo_invalido`**, **`forma_invalida`** e **`chave_nao_enderecavel`** — e **seis** localizadores semânticos fechados — **`caminho`**, **`segmento`**, **`seletor`**, **`chave`**, **`chave_seletora`** e **`literal`** —, na forma **`<categoria>: <localizador>`** e **sem eco do conteúdo recebido**. **Precedência fixa** — decisão técnica local, **não** identificador normativo: tipo da entrada → caminhada da esquerda para a direita → por chave sintaticamente completa, **forma antes de endereçabilidade** → a **primeira** violação encerra → **zero acumulação** → **zero retorno parcial**. **Pureza**: import único `from __future__ import annotations` — **zero `re`**, `unicodedata`, YAML, JSON, I/O, *filesystem*, rede, LLM, relógio, calendário, *locale*, variável de ambiente, aleatoriedade, banco, cache, logging, dependência interna, dependência externa, `try`/`except`, `raise from`, `eval`/`exec`, `assert`, `global`/`nonlocal`, `dict`, `set` e **estado mutável de módulo**; a entrada **não é alterada** e chamadas repetidas produzem **exatamente** o mesmo resultado. **Suíte inteiramente SINTÉTICA**: **nenhum teste lê o corpus versionado**. **NÃO inclui**: a **validação estrutural contextual** — relativo somente em fragmento com `itera_sobre`, e `@` proibido no próprio `itera_sobre` —; o **resolver**; leitura de YAML; **`C-7`**; ***placeholder***; **`hora`**; ***renderer***; o **índice**; ***binding* físico**; **`ASSERTIVA`** nova; a **bijeção**; **`C-A1-ST6`–`C-A1-ST10`**; **`C-11`**; e a **3B.8**. **ANALISAR O CAMINHO NÃO É RESOLVER E NÃO É MATERIALIZAR `C`** |
| **Entrega funcional imediatamente anterior** | **Composição total determinística de status dos fragmentos emitíveis** — a fronteira pura que resolve o status de **todas as ocorrências físicas** de fragmento emitível de um documento, em `src/casa77_sdr/response_status_composition.py` (**PR #127** — commit funcional `24d2b0fef6a08c26e751f8eb8bb70943b30c0339`, merge `00c45e9b95f233bc7aa0f9666e090208994fb190`, branch de origem `feat/total-fragment-status-composition`, título `feat: add total fragment status composition`). **NÃO é denominada `C15`, NÃO é `E15`, NÃO cria identificador normativo novo e NÃO cria a 3B.8** — ela **foi a entrega funcional de código mais recente imediatamente antes da integração da PR #131** e **permanece, no estado corrente, como a entrega funcional imediatamente anterior**. **Sem nomenclatura normativa `E2`–`E7`** e **sem numeração de subetapa**. **Inclui**: **`compor_status_dos_fragmentos(texto: str) -> tuple[tuple[str, str], ...]`** como **fronteira pública única** — **`__all__` com exatamente um nome**, **um único parâmetro**, **sem default** e **sem caminho, arquivo, modo, tolerância ou configuração** —, **sem classe alguma**, **sem exceção pública nova**, **sem DTO**, **sem dataclass**, **sem Enum** e **não** exportada por `casa77_sdr/__init__.py`. **Entrada**: o **texto já em memória**; **a origem correta do texto é pré-condição do chamador**. **Saída**: um par `(token_canonico, status_canonico)` por **OCORRÊNCIA FÍSICA** de fragmento emitível, na **ordem física do documento**, **preservando duplicidades**, **sem deduplicar, agrupar ou reordenar**; documento vazio ou sem `## Rxx` devolve `tuple()`; o status pertence **exclusivamente** ao vocabulário fechado de **`C-3`** — **nunca** `None`, sentinela, marcador de ausência, quarto valor ou valor padrão. **Fontes de status, nenhuma reimplementada**: **`ST1`–`ST3`** **exclusivamente** por `propagar_status` (**C13** permanece a autoridade da propagação e da tradução; **nenhuma tabela foi duplicada** e os três rótulos físicos **não** são carregados no módulo); **`PARCIAL`** **exclusivamente** por `extrair_status_por_fragmento` (**C14** permanece a autoridade do status explicitamente declarado), cuja **associação token/status é HERDADA do contrato da C14** e **não reimplementada** — **sem segunda caminhada `PM`** e **sem interpretação local de `status-fragmento`**; **rótulo `G2` desconhecido** continua **`G2` válido, literal, opaco, sem tradução automática e com status NÃO RESOLVIDO por `SP5`**, e a composição **FALHA FECHADA** via `StatusNaoCanonicalizavel`, que **sobe intacta** (classe, mensagem, `__cause__` e `__context__` inalterados) — **zero retorno parcial, zero omissão silenciosa, zero `None`, zero sentinela, zero quarto status**, e o cabeçalho **não** se torna inválido. **Ordem funcional fixa**: `associar_fragmentos_a_secao(texto)` → `extrair_status_por_fragmento(texto)`, **incondicional** → **`I1`** → caminhada pelas instâncias físicas → C14 sob `PARCIAL` → C13 nos demais rótulos → **`I2`** → **`I3`** → retorno. **Precedência**: `C8` → `C12` → `C14`/`PM` → `I1` → `SP5` → `I2`/`I3` — **uma falha `PM` fisicamente posterior vence um rótulo `SP5` anterior**, porque a C14 percorre o documento **integralmente antes** da caminhada local. **Invariantes internos**: **`I1`** verifica **compatibilidade de cobertura e de ordem** entre as ocorrências `PARCIAL` esperadas pela associação física e o fluxo da C14 — e **NÃO reprova nem redefine a associação interna token/status já produzida pela C14**; **`I2`** verifica **cobertura total** (nada omitido, nada inventado, ordem física preservada); **`I3`** verifica que **todo status pertence a `C-3`**. Falha em qualquer um produz **`RuntimeError("invariante_estrutural")`** — **defeito interno**, **nunca** exceção pública, e **único `raise` originado pelo módulo**. **Homônimos**: instâncias homônimas geram pares **separados**, com **tokens textualmente repetidos preservados** — **zero dedup, zero agrupamento por `Rxx`, zero reordenamento** —, e **a posição do par é apenas ordem de leitura, jamais identidade** (**`C-A5-I5`**). **Pureza**: importa **apenas** `__future__` e as três fronteiras — **zero I/O**, ***filesystem***, `open`, `pathlib`, YAML, JSON, rede, LLM, relógio, calendário, *locale*, variável de ambiente, banco, cache, logging, regex, `unicodedata`, `try`/`except`/`raise from`, `zip`, `dict`, `set`, `sorted`, `reversed`, `map`, `filter`, estado mutável de módulo, `global`/`nonlocal`, `assert`, normalização e coerção; a entrada **não é alterada** e **não há conhecimento comercial**. **Suíte inteiramente SINTÉTICA**, **sem teste persistente contra o corpus**. **NÃO inclui**: a satisfação de **`C-A1-ST8`**; o **índice**; a **bijeção física real**; ***bindings***; **`ASSERTIVA`**; ***placeholder***; **`caminho_yaml`**; **`hora`**; **C-7**; ***renderer***; ***runtime***; a **migração da autoridade**; a satisfação de **`C-A1-ST6`–`C-A1-ST10`**; e a **3B.8**. **COMPOR STATUS NÃO É MATERIALIZAR `C`** |
| **Entrega funcional anterior (associação física de seção e fragmentos)** | **Associação física determinística de seção e fragmentos** — o associador determinístico de fragmentos emitíveis à sua **instância física** de seção `Rxx` e ao **rótulo literal** do cabeçalho, em `src/casa77_sdr/response_section_membership.py` (**PR #124** — commit funcional `0e41165406c3a9261a1fcc8d0f9c600b0469e730`, merge `ecaf0a2b3a594f8fedd10f708461ad2eeb18e086`, branch de origem `feat/c-section-membership`, título `feat: add deterministic response section membership`). **NÃO é denominada `C15`, NÃO é `E15`, NÃO cria identificador normativo novo e NÃO cria a 3B.8** — ela **foi a entrega funcional de código mais recente à época da sua integração** e, **no estado corrente, permanece como entrega funcional anterior, precedendo a PR #127 e a PR #131**. **Sem nomenclatura normativa `E2`–`E7`** e **sem numeração de subetapa**. **Inclui**: **`associar_fragmentos_a_secao(texto: str) -> tuple[tuple[str, str, tuple[str, ...]], ...]`** como **fronteira pública única** — **`__all__` com exatamente um nome**, **um único parâmetro**, **sem default** e **sem caminho, arquivo, modo, tolerância ou configuração** —, **sem exceção pública nova** (o módulo **não declara classe alguma**), **sem DTO**, **sem dataclass** e **não** exportada por `casa77_sdr/__init__.py`. **Entrada**: a **representação marcada já em memória**; **a origem correta do texto é pré-condição do chamador**. **Saída**: `(Rxx, rotulo_literal, tokens)`, **uma entrada por INSTÂNCIA FÍSICA** de `## Rxx`, na **ordem física do documento**, com os tokens canônicos `<Rxx>/<id>` **daquela instância** na ordem física; documento vazio ou sem `## Rxx` devolve `tuple()`. **Homônimos preservados como instâncias separadas**, com **tokens textualmente repetidos preservados** — **zero consolidação por valor de `Rxx`, zero dedup, zero agrupamento** —, e **a posição da entrada é apenas ordem de leitura, jamais identidade** (**`C-A5-I5`**). **`C12` primeiro, `C8` transitivo**: a **primeira** operação funcional é `extrair_rotulos_de_cabecalho(texto)`, chamada **uma única vez**, **sem segunda chamada direta a `C8`** e **sem importar** `response_markdown_units`; `RepresentacaoMarcadaInvalida` e `CabecalhoRxxInvalido` **propagam intactas** (zero `try`/`except`, zero reclassificação, `__cause__`/`__context__` inalterados), e uma falha estrutural ou `G2` **fisicamente posterior vence** anomalia local anterior — **nada é devolvido parcialmente**. **Nenhum julgamento estrutural é refeito**: marcador inválido, bloco sem marcador, marcador fora de seção, `id` fora da gramática, `id` duplicado e seção sem unidade **continuam sendo de `C8`**. **Caminhada física local** mínima e compatível com `C8` — ATX só na coluna 0; níveis 1 e 2 encerram a seção; `##` não-`Rxx` deixa zero seção em escopo; `## Rxx` abre nova instância; níveis 3–6 não encerram; linha `>` nunca é cabeçalho —, na **mesma política de linha** (divisão exclusivamente por `LF`, no máximo um `CR` terminal, sem `splitlines()`, sem *universal newline*, sem normalização). **Invariante local × `C12`**: antes de **qualquer** retorno de sucesso, a sequência local de `(Rxx, rotulo_literal)` de **todas** as instâncias é comparada **inteira** com o retorno guardado da C12; divergência é **defeito interno** e produz **`RuntimeError("invariante_estrutural")`**, **nunca** exceção pública. **ZERO SEMÂNTICA DE STATUS**: **não** importa `response_status`, `response_status_propagation` nem `response_fragment_status`; **não** canonicaliza, **não** traduz rótulo, **não** decide `ST1`–`ST3`, **não** interpreta `PARCIAL`, **não** lê `status-fragmento`, **não** propaga, **não** aplica, **não** resolve status e **não** decide `SP5` — o **`rotulo_literal` é completamente opaco**. **Equivalência estrutural com `C8` como EVIDÊNCIA DE TESTE, não como norma**: nos casos sintéticos válidos exercitados, o *flatten* dos tokens **coincide com `ler_unidades_marcadas(texto)`**, coberto em uma seção, várias seções, múltiplos fragmentos, homônimos, tokens repetidos, `H3`–`H6`, `LF`, `CRLF`, documento sem `Rxx` e bloco fora de seção. **Pureza**: importa **apenas** `__future__` e `extrair_rotulos_de_cabecalho` — **zero I/O**, ***filesystem***, `open`, `pathlib`, YAML, JSON, rede, LLM, relógio, calendário, *locale*, variável de ambiente, banco, cache, logging, regex, `unicodedata`, estado mutável de módulo, `global`/`nonlocal`, `assert`, `dict`, `set`, `zip`, `sorted`, `splitlines`, `strip`, normalização e coerção; a entrada **não é alterada**. **NÃO inclui**: a **composição completa de status**; a **resolução de `SP5`**; a **canonicalização**; a **propagação**; a **interpretação de `PARCIAL`**; o **índice**; a **bijeção física real**; ***bindings***; **`ASSERTIVA`**; ***placeholder***; **`caminho_yaml`**; **`hora`**; **C-7**; ***renderer***; ***runtime***; a **migração da autoridade**; a **satisfação de `C-A1-ST6`–`C-A1-ST10`**; **R2**; **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**; e a **3B.8**. **ASSOCIAR FRAGMENTOS À SEÇÃO NÃO É COMPOR STATUS E NÃO É MATERIALIZAR `C`** |
| **Entrega funcional anterior (décima quarta microentrega)** | **Décima quarta microentrega funcional de `C` — leitor/validador determinístico de status por fragmento sob `PARCIAL`**, em `src/casa77_sdr/response_fragment_status.py` (**PR #120** — commit funcional `75025cc07c8d95f998c61f7516bf3db82bc9c06f`, correção posterior **não funcional** `ca4ec54bc8c1324cc93baf2b7500fa4a04b3f298`, merge `e8db60d95c104993d657de32b80e749dee8003ef`, branch de origem `feat/c14-fragment-status-reader`, título `feat: add deterministic fragment status reader`). **Sem nomenclatura normativa `E2`–`E7`** e **sem numeração de subetapa**. **Inclui**: **`DeclaracaoDeStatusInvalida`** e **`extrair_status_por_fragmento(texto: str) -> tuple[tuple[str, str], ...]`** como **fronteira pública única** — **`__all__` com exatamente dois nomes**, **um único parâmetro**, **sem default** e **sem caminho, arquivo, modo, tolerância ou configuração**; **sem DTO** e **sem dataclass**; **não** é exportada por `casa77_sdr/__init__.py`. A exceção deriva **diretamente de `Exception`** e **não tem parentesco** com `RepresentacaoMarcadaInvalida`, `CabecalhoRxxInvalido`, `StatusNaoCanonicalizavel` ou `BijecaoInvalida`. **Entrada**: a **representação marcada já em memória**; **a origem correta do texto é pré-condição do chamador**. **Saída**: um par **`(token_canonico, status_canonico)`** por fragmento emitível que viva sob seção cujo rótulo literal seja **exatamente** `PARCIAL`, **na ordem física do documento**, com **duplicidades e tokens homônimos preservados**; documento vazio, sem `Rxx` ou sem seção `PARCIAL` devolve `tuple()`. **`C12` primeiro, `C8` transitivo**: a **primeira** operação funcional é `extrair_rotulos_de_cabecalho(texto)`, chamada **uma única vez** — a C12 já roda `ler_unidades_marcadas(texto)` como o seu próprio portão, de modo que a ordem é **`C8` → `C12` → `C14`** **sem** segunda chamada a C8, e o módulo **não importa** `response_markdown_units`; `RepresentacaoMarcadaInvalida` e `CabecalhoRxxInvalido` **propagam intactas** (zero `try`/`except`, zero reclassificação, `__cause__`/`__context__` inalterados), e uma falha estrutural ou `G2` **fisicamente posterior vence** uma violação `PM` anterior — decisão técnica de composição, **não** norma nova. **Caminhada física local**: a C12 devolve `(Rxx, rotulo_literal)` mas **não expõe a fronteira física da seção**, e `Rxx` homônimos são possíveis; por isso o contexto físico da seção corrente — `Rxx` **e** rótulo — é mantido linha a linha, **sem `zip`, sem `dict`, sem agrupamento por `Rxx`, sem pareamento por posição, sem cardinalidade e sem dedup**. **Invariante local × `C12`**: antes de **qualquer** retorno de sucesso, a sequência local de `(Rxx, rotulo_literal)` é comparada **inteira** com o retorno guardado da C12; divergência é **defeito interno** e produz `RuntimeError("invariante_estrutural")`, **nunca** a exceção pública. **Regime exclusivo**: a declaração é aceita **se e somente se** `rotulo_literal == "PARCIAL"`; os três rótulos físicos de `C-A1-ST1`–`C-A1-ST3` **não** são carregados localmente, e **não** há import de `response_status` ou `response_status_propagation`. **`PM1`–`PM5` materializadas**: envelope **exato** `<!-- status-fragmento: <valor> -->`, sem nada antes ou depois, com **quase-declaração permanecendo conteúdo comum**; declaração na **linha imediatamente anterior** ao marcador `C-A5`, com **zero linha física** entre ambos e **nunca** entre marcador e bloco (`C-A5-I1`/`C-A5-I2` preservados); **adjacência estrutural status → marcador**, que **não** é identidade — o token continua `<Rxx>/<id>` (`C-A5-T1`, `C-A5-T2`), preservando `C-A5-I5`; **valores exatamente** `APROVADO`, `AGUARDA_APROVACAO` ou `BLOQUEADO`, com `PARCIAL` **inválido como valor** e **zero** caixa tolerante, normalização, `strip`, coerção, *alias* ou tradução; e, sob `PARCIAL`, **exatamente uma** declaração por marcador. **Cinco categorias técnicas privadas e fechadas**, que **não** são identificadores normativos de `C`: `valor_invalido`, `declaracao_fora_de_secao`, `declaracao_proibida` e `declaracao_orfa` (localizador `declaracao`), e `declaracao_ausente` (localizador `marcador`); mensagem `<categoria>: <localizador>`, **nunca** ecoando `Rxx`, `id`, token, valor, rótulo, conteúdo, linha, índice, cardinalidade, `repr` ou tipo concreto. Duas declarações consecutivas fazem **a primeira** ser órfã, e **nenhuma categoria `declaracao_multipla` foi criada**. **Fail-closed**, com ordem local **valor → seção → regime → marcador seguinte** — `valor_invalido` vence `declaracao_proibida` e `declaracao_fora_de_secao`, o regime é julgado **antes** da relação física, a **primeira violação em ordem física encerra** e **nada é devolvido parcialmente**. A **ausência** de declaração sob rótulo não-`PARCIAL` **não é erro**. **Política de linhas**: a estrutural de `C8`/`C12`, repetida por `PM10` — divisão **exclusivamente por `LF`**, **no máximo um `CR` terminal** removido por segmento, **sem `splitlines()`** e sem *universal newline*; `CR` residual, `U+2028`, `U+2029`, `U+0085`, `VT`, `FF` e `U+00A0` **permanecem conteúdo literal**, e o efeito do `CR` residual sobre cada construção é determinado pelas **respectivas gramáticas**. **Pureza**: importa **apenas** `__future__` e `extrair_rotulos_de_cabecalho` — **zero I/O**, **zero *filesystem***, **zero `open`**, **zero `pathlib`**, **zero YAML**, **zero JSON**, **zero rede**, **zero LLM**, **zero relógio**, **zero calendário**, **zero *locale***, **zero variável de ambiente**, **zero banco**, **zero cache**, **zero logging**, **zero regex**, **zero `unicodedata`**, **zero estado mutável de módulo**, **zero `global`/`nonlocal`**, **zero `assert`**, **zero `dict`**, **zero `set`**, **zero `zip`**, **zero `sorted`**, **zero `splitlines`**, **zero `strip`**, **zero normalização**, **zero coerção**; a entrada **não é alterada**. **NÃO inclui**: a **aplicação de status ao corpus**; a **alteração de `knowledge/**`**; a **composição com `C11` ou `C13`** — a composição com `C12`, e por ela com `C8`, **é justamente o que esta fronteira faz**; a **composição completa de status do documento**; o **índice**; a **bijeção física**; ***bindings***; **`ASSERTIVA`**; ***placeholder***; **`caminho_yaml`**; **`hora`**; **C-7**; **equivalência**; ***renderer***; ***runtime***; a **satisfação de `C-A1-ST6`–`C-A1-ST10`**; a **migração da autoridade de status**; **R2**; **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**; e a **3B.8**. **LER O STATUS DECLARADO NÃO É APLICAR STATUS, NÃO É RESOLVER `PARCIAL` NO CORPUS E NÃO É MATERIALIZAR `C`** |
| **Entrega funcional anterior (décima terceira microentrega)** | **Décima terceira microentrega funcional de `C` — propagação pura e determinística de status `ST1`–`ST3` aos fragmentos já associados**, em `src/casa77_sdr/response_status_propagation.py` (**PR #115** — commit funcional `cbf3e379c9b6697cd502b6a7a0bd3e9bb76c1a27`, merge `50c1d5e681a11923c443c1f117de5751ea846cdd`, branch de origem `feat/c-status-propagation`, título `feat: add deterministic response status propagation`). **Sem nomenclatura normativa `E2`–`E7`** e **sem numeração de subetapa**. **Inclui**: **`PropagacaoInvalida`** e **`propagar_status(rotulo: str, fragmentos: Sequence[str]) -> tuple[tuple[str, str], ...]`** como **fronteira pública única** — **`__all__` com exatamente dois nomes**, **dois parâmetros**, **sem default** e **sem caminho, arquivo, modo, tolerância ou configuração**; **sem DTO** e **sem dataclass**; **não** é exportada por `casa77_sdr/__init__.py`. A exceção deriva **diretamente de `Exception`** e **não tem relação de herança alguma com `StatusNaoCanonicalizavel`** — nem ancestral, nem descendente. **Entrada**: um **rótulo de status já corretamente identificado** e uma sequência de **fragmentos já associados pelo chamador ao mesmo `Rxx` daquele rótulo**; **a associação correta é PRÉ-CONDIÇÃO DO CHAMADOR** (`SP1`), e o sucesso **não** a prova. **Saída**: um par **`(fragmento_opaco, status_canonico)`** por elemento recebido, **na ordem da entrada**, **com duplicidades preservadas**; sequência vazia com rótulo válido devolve `tuple()` — o que afirma **somente** que nada foi recebido, **não** que um `Rxx` real possa não ter fragmentos. **Canonicalizador primeiro**: a **primeira** operação funcional é `canonicalizar_status(rotulo)`, e **nenhuma** validação de `fragmentos` a precede — com rótulo **e** fragmentos inválidos, **o rótulo falha primeiro** (decisão técnica local de determinismo, **não** norma nova); `StatusNaoCanonicalizavel` **propaga intacta** (zero `try`/`except`, zero *wrapper*, zero reclassificação, zero `raise from`, `__cause__`/`__context__` inalterados). **Tradução delegada, nunca reimplementada** — **`ST1`** `APROVADO` → `APROVADO`, **`ST2`** `AGUARDA APROVAÇÃO` → `AGUARDA_APROVACAO`, **`ST3`** `APROVADO com handoff obrigatório` → `APROVADO`, **sem transportar o sufixo de handoff** (C-2f, C-5.1) —, **sem tabela local** e **sem quarta tradução**; o vocabulário de **`C-3`** permanece fechado. **`SP3` materializada por construção**: **todos** os fragmentos daquela chamada recebem **o mesmo** status canônico, que **não depende** de posição, ordem, índice, token, `id`, conteúdo, quantidade ou redação — preservando literalmente **`C-A5-I5`** e **`C-A5-M6`**; a sequência determina **apenas** quais tokens aparecem e em que ordem, **jamais** o status. **Tokens opacos**: os fragmentos são `str` e nada mais — **zero** interpretação de `<Rxx>/<id>`, do separador `/`, de `Rxx`, de `id`, de prefixo, sufixo, gramática, posição ou conteúdo; **zero** composição ou decomposição de token; **zero** validação de `C-A5`, unicidade, cobertura ou cardinalidade; **zero dedup, zero `dict`, zero `zip`, zero agrupamento por `Rxx`, zero pareamento por posição**. **Categoria técnica privada e fechada, única**, que **não** é identificador normativo de `C`: `tipo_invalido`, com **dois localizadores** — `fragmentos` (contêiner: `str`, `bytes`, `bytearray` e não-`Sequence` recusados) e `fragmentos.item` (elemento não-`str` exata, **subclasse de `str` recusada**); mensagem `<categoria>: <localizador>`, **nunca** ecoando token, rótulo, conteúdo, `repr`, tipo concreto, índice, posição, tamanho ou cardinalidade. **Essa exceção julga somente a forma mínima do argumento `fragmentos`, e NÃO julga identidade.** **Fail-closed**, com a validação percorrendo **toda** a entrada antes da montagem, e **nada devolvido parcialmente**. **`PARCIAL` extraído por outras fronteiras continua NÃO RESOLVIDO**: `canonicalizar_status` continua recusando-o, e C13 **não captura, não traduz, não propaga, não mapeia e não converte** — a recusa é **somente daquela invocação**, e **nenhuma política de documento inteiro é afirmada**. **Pureza**: importa **apenas** `__future__`, `collections.abc.Sequence` e `canonicalizar_status` — **zero I/O**, **zero *filesystem***, **zero `open`**, **zero `pathlib`**, **zero Markdown**, **zero YAML**, **zero índice**, **zero rede**, **zero LLM**, **zero relógio**, **zero calendário**, **zero *locale***, **zero variável de ambiente**, **zero banco**, **zero cache**, **zero logging**, **zero estado mutável de módulo**, **zero `global`/`nonlocal`**, **zero normalização**, **zero coerção**, **zero `assert`**, **zero regex**, **zero `dict`**, **zero import de `response_markdown_units`, `response_emittable_text`, `response_header_labels`, `response_index`, `response_index_tokens`, `response_correspondence`, `response_bijection` ou `response_equivalence`**; a entrada **não é alterada**. **NÃO inclui**: a **leitura de Markdown**; a **composição com C8, C11 ou C12**; a **localização de `Rxx`**; a **resolução de contenção física**; a **resolução de homônimos**; o **mapeamento de `PARCIAL`**; o **índice**; a **bijeção física**; ***bindings***; ***placeholder***; **`caminho_yaml`**; **`hora`**; **C-7**; **equivalência**; ***renderer***; ***runtime***; a **satisfação de `C-A1-ST6`–`C-A1-ST10`**; a **migração da autoridade de status**; **R2**; **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**; e a **3B.8**. **PROPAGAR STATUS NÃO É LER MARKDOWN, NÃO É COMPOR C8/C11/C12, NÃO É RESOLVER `PARCIAL` E NÃO É MATERIALIZAR `C`** |
| **Entrega funcional anterior (décima segunda microentrega)** | **Décima segunda microentrega funcional de `C` — extração determinística do rótulo literal de status do cabeçalho `Rxx`**, em `src/casa77_sdr/response_header_labels.py` (**PR #113** — commit funcional `798beb31fd0dc4fed34aa7b20d397abcd2ef8c2b`, merge `eae7b5098b248cefb42b3a82569fc0575fd6fee0`, branch de origem `feat/c-header-label-extraction`, título `feat: add deterministic Rxx header label extraction`). **Sem nomenclatura normativa `E2`–`E7`** e **sem numeração de subetapa**. **Inclui**: **`CabecalhoRxxInvalido`** e **`extrair_rotulos_de_cabecalho(texto: str) -> tuple[tuple[str, str], ...]`** como **fronteira pública única** — **`__all__` com exatamente dois nomes**, **um único parâmetro**, **sem default** e **sem caminho, arquivo, modo, tolerância ou configuração**; **sem DTO** e **sem dataclass**; **não** é exportada por `casa77_sdr/__init__.py`. A exceção deriva **diretamente de `Exception`**. **Entrada**: a **representação marcada já em memória**; **a origem correta do texto é pré-condição do chamador**. **Saída**: um par **`(Rxx, rotulo_literal)`** por cabeçalho físico `## Rxx`, **na ordem física do documento**; o título **não** aparece na saída; documento vazio ou sem seção `Rxx` devolve `tuple()`. **C8 primeiro, e somente como portão**: a **primeira** operação funcional é `ler_unidades_marcadas(texto)` — tipo não-`str`, subclasse de `str` e toda violação de `C-A5` **continuam de C8**, e `RepresentacaoMarcadaInvalida` **propaga intacta** (zero `try`/`except`, zero reclassificação, `__cause__`/`__context__` inalterados); o **resultado de C8 não é armazenado nem comparado** — **NÃO EXISTE INVARIANTE LOCAL × C8**, porque C8 não expõe fronteiras físicas de seção e, com homônimos, nenhum conjunto, contagem ou compressão por `Rxx` provaria correspondência 1:1 —; com violação `G2` anterior e estrutural posterior, **a estrutural vence** — decisão técnica de composição, **não** norma nova. **Só depois** a C12 percorre a `str` com uma caminhada local mínima — `##` na coluna 0, exatamente um espaço, `R`, dois dígitos ASCII, espaço ou fim de linha — para localizar os cabeçalhos `Rxx` já aceitos, **sem importar helper privado de C8**. **`G2` materializada**: `## Rxx — <titulo> — <rotulo>` com separador literal **`U+0020 U+2014 U+0020`**; o separador precisa ocorrer **imediatamente após `Rxx`** e **exatamente duas vezes**, contadas **inclusive quando sobrepostas** (uma linha ambígua como `A — — B` é recusada, não decomposta por inferência); título e rótulo **não vazios** e **sem espaço `U+0020` ou tab `U+0009` de borda**; `-`, `–`, variantes Unicode e espaçamento divergente **recusados, nunca corrigidos**; **zero `strip`, zero normalização, zero inferência**; o rótulo é **literal e opaco**, sem decidir pertença a `ST1`–`ST3`. **Categorias técnicas privadas e fechadas**, que **não** são identificadores normativos de `C`: `separador_ausente` e `cardinalidade_de_separador` (localizador `cabecalho`), `segmento_vazio` e `branco_de_borda` (localizadores `titulo` e `rotulo`); mensagem `<categoria>: <localizador>`, **nunca** ecoando `Rxx`, título, rótulo, conteúdo, caractere ofensor, `repr`, tipo, linha, posição, índice, tamanho ou cardinalidade numérica; **fail-closed**, ordem local por cabeçalho **separador ausente → cardinalidade → título vazio → branco no título → rótulo vazio → branco no rótulo**, a **primeira violação encerra** e **nada é devolvido parcialmente**. **Política de linhas**: a estrutural de C8 — divisão **exclusivamente por `LF`**, **no máximo um `CR` terminal** removido, **sem `splitlines()`** e sem *universal newline* —; `CR` residual, `U+2028`, `U+2029`, `U+0085`, `VT`, `FF` e `U+00A0` **permanecem conteúdo literal**; a política `MT8` da C11 **não** é aplicada a cabeçalhos. **Seções `Rxx` homônimas preservadas**: múltiplos pares em ordem física, **sem dedup, sem `dict`, sem recusa** — a unicidade global **não** é decidida aqui. **`PARCIAL` extraído literalmente e não resolvido**: **não importa `response_status`**, **não chama `canonicalizar_status`**, **não traduz, não propaga, não mapeia** — **EXTRAIR `PARCIAL` NÃO É RESOLVER `PARCIAL`**. **Pureza**: importa **apenas** `__future__` e `ler_unidades_marcadas` — **zero I/O**, **zero *filesystem***, **zero `open`**, **zero `pathlib`**, **zero YAML**, **zero rede**, **zero LLM**, **zero relógio**, **zero *locale***, **zero variável de ambiente**, **zero banco**, **zero cache**, **zero logging**, **zero estado mutável de módulo**, **zero `assert`**, **zero regex**, **zero `unicodedata`**, **zero `dict`**, **zero import de `response_status`, `response_emittable_text`, `response_index`, `response_index_tokens`, `response_correspondence`, `response_bijection` ou `response_equivalence`**; a entrada **não é alterada**. **NÃO inclui**: **canonicalização de status**; a **propagação `SP1`–`SP7`**; o **mapeamento de `PARCIAL`**; o **índice**; a **bijeção física**; ***bindings***; ***placeholder***; **`caminho_yaml`**; **`hora`**; **C-7**; **equivalência**; ***renderer***; ***runtime***; a **satisfação de `C-A1-ST6`–`C-A1-ST10`**; a **migração da autoridade de status**; **R2**; **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**; e a **3B.8**. **EXTRAIR O RÓTULO NÃO É CANONICALIZAR STATUS, NÃO É PROPAGAR STATUS, NÃO É RESOLVER `PARCIAL` E NÃO É MATERIALIZAR `C`** |
| **Entrega funcional anterior (décima primeira microentrega)** | **Décima primeira microentrega funcional de `C` — extração determinística do texto emitível canônico**, em `src/casa77_sdr/response_emittable_text.py` (**PR #109** — commit funcional `4b6ea8ca00c171275d75ea17c4414011a4f1a835`, merge `ceecd638131899974ce43b4685b254bf01d7bbad`, branch de origem `feat/c-emittable-text-extraction`, título `feat: add deterministic emittable response text extraction`). **Sem nomenclatura normativa `E2`–`E7`** e **sem numeração de subetapa**. **Inclui**: **`TextoEmitivelInvalido`** e **`extrair_textos_emitiveis(texto: str) -> tuple[tuple[str, str], ...]`** como **fronteira pública única** — **`__all__` com exatamente dois nomes**, **um único parâmetro**, **sem default** e **sem caminho, arquivo, modo, tolerância ou configuração**; **sem DTO** e **sem dataclass**; **não** é exportada por `casa77_sdr/__init__.py`. A exceção deriva **diretamente de `Exception`**. **Entrada**: a **representação marcada já em memória**; **a origem correta do texto é pré-condição do chamador**. **Saída**: um par **`(token_canonico, texto_canonico)`** por unidade emitível declarada, **na ordem física do documento**; documento vazio ou sem seção `Rxx` devolve `tuple()`. **C8 primeiro, e juiz estrutural único**: a **primeira** operação funcional é `ler_unidades_marcadas(texto)` — tipo não-`str`, subclasse de `str` e toda violação de `C-A5` **continuam de C8**, e `RepresentacaoMarcadaInvalida` **propaga intacta** (zero `try`/`except`, zero reclassificação, `__cause__`/`__context__` inalterados); com violação textual anterior e estrutural posterior, **a estrutural vence** — decisão técnica de composição, **não** norma nova. **Só depois** a C11 percorre a `str` para **localizar as mesmas unidades declaradas**, **deriva de novo o token somente do `Rxx` do cabeçalho e do `id` do marcador** (**`C-A5-T1`**, **`C-A5-T2`**, **`C-A5-I5`** — **nunca** posição, ordem, `zip` ou conteúdo) e **verifica a sequência local de tokens contra a saída de C8 antes de devolver qualquer par**; divergência é **defeito interno** e produz `RuntimeError("invariante_estrutural")`, mensagem muda. **`MT3`–`MT11` materializadas**: prefixo de conteúdo **exatamente `> `** (dois caracteres, removidos por fatiamento — **sem `strip`, `lstrip`, `rstrip`, regex permissiva ou CommonMark**); `>` colado, `>` com dois ou mais espaços, `>` com tab, `> ` com tab e `> ` sem conteúdo **recusados**; linha `>` interna **única** projeta **exatamente `\n\n`**; linha `>` em **borda** e **duas ou mais** linhas `>` consecutivas **recusadas**, sem colapso; linhas consecutivas de conteúdo projetam **exatamente um `LF`**, **não convertido em espaço**; **`LF` e `CRLF` físicos aceitos**, com o `CR` **do par** removido e **nenhum `CR` na saída**; **`CR` isolado — inclusive no EOF, sem `LF` subsequente — recusado**, mesmo quando C8 o aceitou estruturalmente (**`MT2`**); **EOF sem newline aceito**; `U+2028`, `U+2029`, `U+0085`, `U+000B` e `U+000C` **recusados**; espaço ou tab **imediatamente antes do terminador** recusado; **nenhuma correção silenciosa**; **`splitlines()`, *universal newline*, `StringIO` e I/O proibidos** — a divisão é **exclusivamente por `LF`**, preservando por segmento a evidência de ter sido seguido pelo `LF`. **Categorias técnicas privadas e fechadas**, que **não** são identificadores normativos de `C`: `prefixo_invalido`, `terminador_proibido` e `branco_antes_do_terminador` (localizador `linha`) e `linha_vazia_invalida` (localizador `unidade`); mensagem `<categoria>: <localizador>`, **nunca** ecoando conteúdo, token, `Rxx`, `id`, caractere ofensor, `repr`, tipo, linha, posição, índice, tamanho ou cardinalidade; **fail-closed**, ordem local **terminador → prefixo → branco terminal → linhas vazias → montagem**, a **primeira violação encerra** e **nada é devolvido parcialmente**. **Bloco `>` fora de `## Rxx`** é **ignorado integralmente**, sem par e sem validação textual; **seções `Rxx` homônimas** aceitas por C8 podem produzir **token repetido**, devolvido na ordem física — a unicidade global **não** é decidida aqui. **Pureza**: importa **apenas** `__future__` e `ler_unidades_marcadas` — **zero I/O**, **zero *filesystem***, **zero `open`**, **zero `pathlib`**, **zero YAML**, **zero rede**, **zero LLM**, **zero relógio**, **zero calendário**, **zero *locale***, **zero variável de ambiente**, **zero banco**, **zero cache**, **zero estado mutável de módulo**, **zero `unicodedata`**, **zero import de `response_equivalence` ou `response_correspondence`**; a entrada **não é alterada**. **NÃO inclui**: **validação de equivalência** (`C-15b` continua no comparador existente); **`NFC`**; a **conversão de quebra suave em espaço**; a **leitura de arquivo, YAML ou índice**; a **resolução de *bindings***; a **leitura, resolução ou propagação de status**; o mapeamento de **`PARCIAL`**; ***placeholder***; **`caminho_yaml`**; o formato **`hora`**; **C-7**; a **execução da bijeção física 37/37**; a **satisfação de `C-A1-ST6`–`C-A1-ST10`**; a **migração da autoridade de status**; a **integração de *runtime* ou consumidor**; **R2**; **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**; e a **3B.8**. **EXTRAIR TEXTO CANÔNICO NÃO É VALIDAR EQUIVALÊNCIA, NÃO É EXECUTAR A BIJEÇÃO FÍSICA E NÃO É MATERIALIZAR `C`** |
| **Entrega funcional anterior (décima microentrega)** | **Décima microentrega funcional de `C` — composição determinística em memória da correspondência canônica**, em `src/casa77_sdr/response_correspondence.py` (**PR #106** — commit funcional `6265b823cb20aab0395840f8125008121de27e43`, merge `457e29a42472d44175d72031cff05ec1a1ebf9d1`, branch de origem `feat/c-response-correspondence`, título `feat: add deterministic canonical response correspondence composition`). **Sem nomenclatura normativa `E2`–`E7`** e **sem numeração de subetapa**. **Inclui**: **`validar_correspondencia_canonica(indice: object, texto_markdown: str) -> None`** como **fronteira pública única** — **`__all__` com exatamente UM nome**, **dois parâmetros**, **sem default** e **sem caminho, arquivo, modo ou configuração**. **Nenhuma exceção nova é criada** e **nenhum nome público além desse é exportado**; **não** é exportada por `casa77_sdr/__init__.py`. **Entrada**: uma **estrutura candidata do índice já em memória** e um **Markdown já em memória**; **a proveniência correta dos dois insumos é pré-condição do chamador**. **Ordem fixa**: **1.** `derivar_tokens_do_indice(indice)` (C9); **2.** `ler_unidades_marcadas(texto_markdown)` (C8); **3.** a relação canônica; **4.** `validar_bijecao(...)` (C6), chamado **uma única vez**. **Relação**: **exatamente `(token, token)`** para cada token do domínio do índice, **na ordem em que C9 os devolveu** — a correspondência é **igualdade da identidade canônica**, e **nunca** pareamento por posição, por ordem, por `zip`, por conteúdo ou por normalização. Rastreabilidade: **`C-A5-T1`** (identidade `<Rxx>/<id>`), **`C-A5-T2`** (separador `/`), **`C-A5-T3`** (composição injetiva, decomposição unívoca pelas formas fechadas), **`C-A5-T4`** (o mesmo token nos **dois** domínios físicos de **`C-A1-B3`** / **`C-A1-B4`**), **`C-A5-T5`** (token derivado, nunca armazenado — a relação **não** é devolvida, armazenada nem persistida) e **`C-A5-I5`** (identidade declarada, jamais derivada de posição, ordem, índice, redação ou conteúdo). **Divisão de responsabilidades — a C10 NÃO cria juiz novo**: **C9** continua responsável pelo **domínio do índice**, **C8** continua responsável pelo **domínio do Markdown** e **C6** continua sendo o **único juiz da bijeção** sobre os domínios recebidos; a C10 **somente compõe** essas três fronteiras. **Zero validação local**: tipo dos insumos, estrutura do índice, estrutura do Markdown, forma do token, duplicidade, cobertura e cardinalidade **já pertencem** às fronteiras chamadas e **não são duplicados aqui**. **Exceções propagam intactas** — **`ProjecaoDeIdentidadeInvalida`**, **`RepresentacaoMarcadaInvalida`** e **`BijecaoInvalida`** —, **sem `try`/`except`**, **sem reclassificação**, **sem enriquecimento de mensagem** e **sem alterar `__cause__` ou `__context__`**; com **ambos** os insumos inválidos, a ordem fixa faz o **lado do índice falhar primeiro**, o que é **decisão técnica local de determinismo**, **não** norma nova de `C`. **Pureza**: fora as três fronteiras públicas e `__future__`, o módulo **não importa nada** — **zero I/O**, **zero *filesystem***, **zero `open`**, **zero `pathlib`**, **zero YAML**, **zero rede**, **zero LLM**, **zero relógio**, **zero calendário**, **zero *locale***, **zero variável de ambiente**, **zero banco**, **zero cache**, **zero estado mutável de módulo**, **zero leitura de `knowledge/**`**; os insumos **não são alterados**. **NÃO inclui**: a **criação ou leitura do índice físico**, que **continua INEXISTENTE**; a **substituição de `validar_indice`**, que **não é importado nem chamado**; a **execução da bijeção física 37/37** do corpus real; a **satisfação de `C-A1-ST6`–`C-A1-ST10`**; a **migração da autoridade de status**; a **extração de texto emitível**; a **propagação de status**; o mapeamento de **`PARCIAL`**; ***placeholder***; **`caminho_yaml`**; o formato **`hora`**; **C-7**; **R2**; **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**; e a **3B.8**. **COMPOR E VALIDAR EM MEMÓRIA NÃO É EXECUTAR A BIJEÇÃO FÍSICA E NÃO É MATERIALIZAR `C`** — o sucesso afirma **somente** que os **dois insumos fornecidos** produziram domínios cuja relação canônica é **bijetiva entre eles** |
| **Entrega funcional anterior** | **Nona microentrega funcional de `C` — derivador determinístico dos tokens canônicos do lado do índice**, em `src/casa77_sdr/response_index_tokens.py` (**PR #104** — commit funcional `45876ca609716ede51aefcf8752dd29f98a736a7`, merge `654aaedec2d424ab4184e7a71a0d3c129021abf8`, branch de origem `feat/c-response-index-tokens`, título `feat: add deterministic response index token derivation`). **Sem nomenclatura normativa `E2`–`E7`** e **sem numeração de subetapa**. **Inclui**: **`ProjecaoDeIdentidadeInvalida`** e **`derivar_tokens_do_indice(indice: object) -> tuple[str, ...]`** como **fronteira pública única** — **`__all__` com exatamente dois nomes**, **um único parâmetro**, **sem default** e **sem caminho, arquivo, modo ou configuração**. A exceção deriva **diretamente de `Exception`**. **Entrada**: a **estrutura chega pronta em memória** — a mesma espécie de entrada de `validar_indice`; **a origem correta da estrutura é pré-condição do chamador**. **Saída**: **somente** tokens `<Rxx>/<id>` (**`C-A5-T1`**, separador `/` de **`C-A5-T2`**), na **ordem das listas `respostas` e `fragmentos` recebidas** — decisão técnica determinística de saída, **não** significado normativo novo de identidade (**`C-A5-I5`**, **`C-A5-M6`**) —, **derivados e nunca armazenados** (**`C-A5-T5`**): nada é gravado na estrutura recebida, nenhum campo novo é criado e a entrada **não é alterada**. **Projeção mínima**, e nada além dela: raiz é mapeamento; existe `respostas`; `respostas` é lista; cada resposta é mapeamento; existe `id`; o `Rxx` é `str` **exata** e satisfaz a forma fechada de **C-2b** — `R` + **exatamente dois dígitos ASCII** —; o `Rxx` é único **globalmente** (**C-2a**); existe `fragmentos`; `fragmentos` é lista **não vazia** (**C-2c**); cada fragmento é mapeamento; existe `id`; o `id` é `str` **exata** e satisfaz a gramática fechada de **`C-A5-I3`** — `F` + inteiro decimal ASCII maior que zero, **sem zero à esquerda** —; e o `id` é único **dentro do respectivo `Rxx`** (**`C-A5-I4`**, **C-2h**), de modo que `F1` repetido entre `Rxx` distintos é **válido**. **Política de tipo**: contêineres aceitam subclasses — `dict` e `list` por `isinstance`, **compatível com `response_index.py`**, **sem regra de tipo exato para contêiner** —, enquanto os **componentes da identidade** exigem `str` **exata** e **subclasse de `str` é recusada**, porque poderia redefinir `__eq__`/`__hash__`/`__str__` e decidir sozinha a identidade ou a composição; essa recusa é **defesa local desta fronteira** e **não** altera **C-2**, **C-A5**, `validar_indice`, nem torna retroativamente inválido o que `response_index.py` aceita. **`C-A5-I3` aplicada ao `fragmentos[].id` NÃO cria regra nova**: é a gramática já arbitrada aplicada ao componente já designado por **`C-A5-T3`** / **`C-A5-T4`**; `response_index` exige apenas `str` não vazia nesse campo e **continua correto no seu próprio escopo**. **Categorias técnicas privadas, fechadas e mínimas**, que **não** são identificadores normativos de `C`: `tipo_invalido`, `campo_ausente`, `valor_invalido` e `duplicidade` — subconjunto deliberado do vocabulário já usado por `response_index.py`, **sem taxonomia paralela**; **localizadores estruturais fechados e sem posição**: `indice`, `respostas`, `respostas.item`, `respostas.item.id`, `respostas.item.fragmentos`, `respostas.item.fragmentos.item` e `respostas.item.fragmentos.item.id`. A mensagem tem a forma `<categoria>: <localizador>` e **nunca** ecoa o `Rxx`, o `id`, o valor, o conteúdo, o `repr`, o tipo concreto, uma posição, um tamanho ou uma cardinalidade; **fail-closed**, a **primeira violação encerra** e **nada é acumulado** (**P5**). **Pureza**: importa **apenas** `__future__` — **zero I/O**, **zero *filesystem***, **zero `pathlib`**, **zero `open`**, **zero YAML**, **zero rede**, **zero LLM**, **zero relógio**, **zero calendário**, **zero *locale***, **zero variável de ambiente**, **zero banco**, **zero leitura de `knowledge/**`**, **zero import de `casa77_sdr.*`** — em particular **não importa nem chama `response_index`, `response_index_load`, `response_bijection` ou `response_markdown_units`** — e **zero export** por `casa77_sdr/__init__.py`. **NÃO inclui**: a **substituição de `validar_indice`** — `status`, `bindings`, `itera_sobre`, *placeholder*, `caminho_yaml`, `formato`, `predicado`, mecanismo, origem, fato runtime e chaves desconhecidas **não são julgados aqui**; a **criação ou leitura do índice real**, que **continua INEXISTENTE**; a **construção de correspondências reais**; a **chamada a `validar_bijecao`**; a **execução da bijeção física 37/37**; a **satisfação de `C-A1-ST6`** ou de **`C-A1-ST7`**; a **migração da autoridade de status**; a **extração de texto emitível**; a **propagação de status**; o mapeamento de **`PARCIAL`**; o formato **`hora`**; **C-7**; **R2**; **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**; e a **3B.8**. **DERIVAR UM DOMÍNIO DE TOKENS NÃO É EXECUTAR A BIJEÇÃO E NÃO É MATERIALIZAR `C`** |
| **Entrega funcional anterior a essa** | **Oitava microentrega funcional de `C` — leitor/validador determinístico da representação marcada `C-A5`**, em `src/casa77_sdr/response_markdown_units.py` (**PR #102** — commit funcional `341084d951b428d80c4ba573fbc38a4bc9f008c6`, merge `067e894db8bddb96c192d7da3a4431f587f4efc0`, branch de origem `feat/c-response-markdown-units`, título `feat: add deterministic C-A5 markdown unit reader`). **Sem nomenclatura normativa `E2`–`E7`** e **sem numeração de subetapa**. **Inclui**: **`RepresentacaoMarcadaInvalida`** e **`ler_unidades_marcadas(texto: str) -> tuple[str, ...]`** como **fronteira pública única** — **`__all__` com exatamente dois nomes**, **um único parâmetro**, **sem default** e **sem parâmetro de caminho, arquivo, modo, tolerância, configuração ou normalização**. A exceção deriva **diretamente de `Exception`**. **Entrada**: o **texto chega pronto em memória**; **a origem correta do texto é pré-condição do chamador**. **Tipo**: `str` **exata** — **subclasse de `str` recusada antes de qualquer leitura**. **Saída**: **somente** tokens `<Rxx>/<id>` (**`C-A5-T1`**, **`C-A5-T2`**), em **ordem física do documento**, **derivados e nunca armazenados** (**`C-A5-T5`**); documento vazio ou sem seção `Rxx` devolve `tuple()`. **Política de linha local**: divisão **exclusivamente** por `LF` com remoção de **no máximo um** `CR` terminal — `LF` e `CRLF` produzem **resultado idêntico**, **sem `splitlines()`** e **sem *universal newline***; `U+2028`, `U+2029`, `U+0085`, `VT` e `FF` **permanecem conteúdo**. **Delimitação de seção deliberadamente parcial**: apenas cabeçalho ATX na **coluna 0**, um a seis `#` seguidos de espaço ou fim de linha; níveis 1 e 2 encerram a seção `##`, níveis 3–6 não; **`Setext`, *code fence*, bloco `HTML` e código indentado NÃO são interpretados**. **Marcador em dois estágios**: envelope exato `<!-- fragmento: ` + conteúdo interno + ` -->`, **sem nada antes ou depois** — quase-marcador é **conteúdo comum**, não marcador defeituoso —, e depois a **gramática fechada de `C-A5-I3`** (**`F`** + inteiro decimal ASCII maior que zero, sem zero à esquerda). **Bloco de citação fora de `## Rxx`** está **fora do domínio de `C-A5-U2`** e é **ignorado inteiro**, sem token e sem erro; **dentro de `Rxx`, bloco sem marcador válido é fail-closed**, e **marcador válido fora de `Rxx` também**. **Sete redações de `C-A5-X1` cobertas por SEIS categorias estruturais** — `bloco_sem_marcador`, `marcador_sem_bloco` (que absorve **marcador órfão** e **marcador sem bloco imediatamente seguinte**, mecanicamente indistinguíveis nesta fronteira), `marcador_fora_de_secao`, `id_fora_da_gramatica`, `id_duplicado`, `secao_sem_unidade` — mais `tipo_invalido` para o contrato de entrada; **nenhuma oitava falha foi criada** e as categorias são **privadas e fechadas**, jamais identificadores normativos de `C`. **Precedência fixa**: tipo da entrada; depois, em ordem de documento, envelope → gramática do `id` → escopo `Rxx` → existência de bloco imediatamente seguinte → duplicidade do `id` na seção — a **primeira violação encerra** e **nada é acumulado** (**P5**). A mensagem tem a forma `<categoria>: <localizador>`, com localizadores fechados `texto` / `bloco` / `marcador` / `secao`, e **nunca** ecoa o `id`, o `Rxx`, o conteúdo, o `repr`, o tipo concreto, um número de linha, um índice, um tamanho ou uma cardinalidade. **Unicidade de `id` verificada SOMENTE dentro do respectivo `Rxx`** (**`C-A5-I4`**, **C-2h**). **NÃO garante unicidade global dos tokens**: a função **não verifica a unicidade física das seções `## Rxx`**, de modo que duas seções homônimas podem produzir o mesmo `<Rxx>/<id>` — **não-garantia deliberada**, e **`response_bijection` não é importado nem chamado** para supri-la. **`C-A5-I6` é respeitada como norma externa e NÃO é provada**: um *snapshot* único não carrega histórico — **zero `Git`**, **zero armazenamento**, **zero estado entre chamadas**. **Pureza**: importa **apenas** `__future__` — **zero I/O**, **zero *filesystem***, **zero `pathlib`**, **zero YAML**, **zero rede**, **zero LLM**, **zero relógio**, **zero calendário**, **zero *locale***, **zero variável de ambiente**, **zero banco**, **zero dependência de `casa77_sdr.*`** e **zero export** por `casa77_sdr/__init__.py`. **NÃO inclui**: a **extração de texto emitível**; a **leitura ou propagação de status**; o **mapeamento de `PARCIAL`**; a **criação ou leitura do índice real**; a **resolução de *bindings***; a **criação de `ASSERTIVA`**; a **renderização**; a **normalização `C-15`**; a **execução da bijeção física**; a **prova de que o texto recebido seja o corpus oficial, completo ou aprovado**; a **satisfação de `C-A1-ST6`–`C-A1-ST10`**; a **migração da autoridade de status**; a **integração de consumidor**; o formato **`hora`**; **`caminho_yaml`**; ***placeholder***; **C-7**; **R2**; **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**; e a **3B.8**. **LER A REPRESENTAÇÃO MARCADA NÃO É MATERIALIZAR `C`** |
| **Entrega funcional anterior a essa, por sua vez** | **Sétima microentrega funcional de `C` — canonicalizador determinístico de rótulo de status já extraído**, em `src/casa77_sdr/response_status.py` (**PR #97** — commit funcional `4749efa74d5684b52b4f457176710ba6e212c627`, merge `8c67e13808da59dbace413fce33c2c22280e69a3`, branch de origem `feat/c-response-status`, título `feat: add deterministic response status canonicalizer`). **Sem nomenclatura normativa `E2`–`E7`.** **Inclui**: **`StatusNaoCanonicalizavel`** e **`canonicalizar_status(rotulo: str) -> str`** como **fronteira pública única** — **`__all__` com exatamente dois nomes**, **um único parâmetro**, **sem default** e **sem parâmetro de contexto, origem, modo, tolerância, fragmento, `Rxx`, configuração ou normalização**. A exceção deriva **diretamente de `Exception`**. **Traduções automáticas — exatamente três**, do contrato `C-A1-ST`: `APROVADO` → `APROVADO` (**C-A1-ST1**); `AGUARDA APROVAÇÃO` → `AGUARDA_APROVACAO` (**C-A1-ST2**); `APROVADO com handoff obrigatório` → `APROVADO` (**C-A1-ST3**), com o **sufixo de handoff NÃO transportado** por ser instrução operacional fora de `C` (C-2f, C-5.1). **Nenhuma quarta tradução**, e **`BLOQUEADO` nunca é produzido como imagem** — embora pertença a `C-3`, nenhuma linha de `C-A1-ST` o produz automaticamente a partir de um rótulo simples. **Entrada**: o **rótulo chega já extraído**; **a origem correta do rótulo é pré-condição do chamador**. **Tipo**: `str` **exata** — **subclasse de `str` recusada antes de qualquer consulta à tabela**, porque poderia redefinir `__eq__`/`__hash__` e decidir sozinha a pertença; **sem `str(...)`**, **sem `repr`**, **sem coerção**. **Comparação literal**: **sem `strip`, `lower`, `upper`, `casefold`, `NFC`, `NFD`, `unicodedata`, colapso de espaços, substituição de espaço inquebrável, tolerância de acento ou de caixa**. **Precedência fixa**: **1.** tipo do rótulo; **2.** pertença à tabela automática; **3.** retorno — a **primeira violação encerra** e **nada é acumulado** (**P5**). **Categorias técnicas privadas e fechadas**, que **não** são identificadores normativos de `C`: `tipo_invalido` e `rotulo_nao_mapeado`; **localizador único**: `rotulo`. A mensagem tem a forma `<categoria>: <localizador>` e **nunca** ecoa o rótulo, o conteúdo, o `repr`, o tipo concreto, um comprimento ou um índice; **sem `__cause__`** e **sem `__context__`**. **Tabela privada imutável** (`tuple` de três pares), **não exposta por `__all__`**, **sem estado mutável de módulo** e com a **entrada não alterada**. **Pureza**: importa **apenas** `__future__` — **zero I/O**, **zero *filesystem***, **zero YAML**, **zero *locale***, **zero rede**, **zero LLM**, **zero relógio**, **zero calendário**, **zero variável de ambiente**, **zero leitura de `knowledge/**`**, **zero dependência de `casa77_sdr.*`** e **zero export** por `casa77_sdr/__init__.py`. **NÃO inclui**: a **tradução automática de `PARCIAL`** (**C-A1-ST4** exige **mapeamento explícito no nível dos fragmentos emitíveis**, **não implementado aqui**); qualquer **mapeamento inventado de `BLOQUEADO`** (**C-A1-ST5** trata de **nota interna**, que **não cria fragmento** e **não cria status**); a **extração do rótulo ou do fragmento do Markdown**; a **identidade física de fragmento**; a **criação ou leitura do índice real**; a **resolução de *bindings***; a **execução da bijeção física**; a **prova de completude do corpus**; a **satisfação de `C-A1-ST6`–`C-A1-ST10`**; a **migração da autoridade de status**; a **integração de consumidor**; o formato **`hora`**; **R2**; **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**; **LLM**; e a **3B.8**. **CANONICALIZAR STATUS NÃO É MATERIALIZAR `C`** |
| Entrega funcional **anterior** | **Sexta microentrega funcional de `C` — verificador determinístico da correspondência bijetiva de `C-A1-B3` / `C-A1-B4` sobre domínios já fornecidos pelo chamador**, em `src/casa77_sdr/response_bijection.py` (**PR #95** — commit funcional `bdd0b2acc415ab6307c7c8da2adbad15f42cb75f`, merge `b06c0a43bd2f96b8712638e99c55edfe2fb2f99f`, branch de origem `feat/c-response-bijection`, título `feat: add deterministic response bijection validator`). **Sem nomenclatura normativa `E2`, `E3`, `E4`, `E5` ou `E6`.** **Inclui**: **`BijecaoInvalida`** e **`validar_bijecao(fragmentos_indice: Sequence[str], unidades_markdown: Sequence[str], correspondencias: Sequence[tuple[str, str]]) -> None`** como **fronteira pública única** — **`__all__` com exatamente dois nomes**, **três parâmetros**, **sem default** e **sem parâmetro de modo, tolerância, origem, caminho ou configuração**. **Os três domínios chegam prontos**: a função julga **somente** se a relação recebida é **total, injetiva e sobrejetiva nos dois sentidos** entre os domínios recebidos. **Tokens opacos**: fragmento e unidade são `str` **não interpretadas** — sem formato `Rxx`, gramática, prefixo, separador, `UUID`, número ou posição exigidos —, comparadas por **igualdade nativa exata de `str`**, **sem `strip`, `casefold`, `lower`, `upper`, `NFC` ou normalização de espécie alguma**; **token é `str` exata** e **subclasse de `str` é recusada** nos dois domínios e nos dois lados de cada par, porque poderia redefinir `__eq__`/`__hash__`. **Relação como sequência explícita de pares, nunca `Mapping`**: cada item é obrigatoriamente **`tuple` exata de exatamente dois elementos** — **subclasse de `tuple` recusada**, **`list` de dois elementos recusada** —; `str`, `bytes` e `bytearray` **não** são contêineres válidos para nenhum dos três argumentos. **Zero normalização, zero coerção, zero *parsing*, zero I/O**; entradas **não alteradas**. **Precedência fixa**: tipo dos três argumentos → tipo dos tokens de `fragmentos_indice` → tipo dos tokens de `unidades_markdown` → tipo e forma dos itens da relação → tipo de origem e destino de cada par → duplicidade em `fragmentos_indice` → duplicidade em `unidades_markdown` → origem repetida → destino repetido → origem desconhecida → destino desconhecido → fragmento sem par → unidade sem par; cada etapa percorre **toda** a entrada antes da seguinte, a **primeira violação encerra** e **nada é acumulado** (**P5**). **Categorias técnicas privadas e fechadas**, que **não** são identificadores normativos de `C`: `tipo_invalido`, `estrutura_invalida`, `duplicidade`, `referencia_desconhecida` e `cobertura_incompleta`; **localizadores fechados**: `fragmentos_indice`, `unidades_markdown`, `correspondencias`, `correspondencias.item`, `correspondencias.origem` e `correspondencias.destino`. A mensagem tem a forma `<categoria>: <localizador>` e **nunca** ecoa o token recebido, o conteúdo, o `repr`, o tipo concreto, um índice numérico, um tamanho ou uma cardinalidade; **sem `__cause__`** e **sem `__context__`**. **Três domínios vazios são bijeção trivial válida** e devolvem `None` — afirmação **restrita aos domínios fornecidos**. **Limite da garantia**: retorno bem-sucedido significa **somente** que a relação fornecida é bijetiva sobre os domínios fornecidos — **não** que o índice real esteja completo, que o Markdown tenha sido integralmente extraído, que a bijeção física do corpus real tenha ocorrido, que `C-A1-ST7` esteja satisfeita no sistema, nem que a autoridade de status possa migrar; **a completude correta dos dois domínios é pré-condição do chamador**. **NÃO inclui**: **extração de fragmentos do índice**; **extração de unidades do Markdown**; a **decisão do que é unidade emitível**; a **identidade física de fragmento**; a **criação de identificadores**; a **leitura do índice real**; a **prova de completude dos domínios**; a **execução da bijeção física do corpus real**; a **satisfação de `C-A1-ST7`**; a **migração de autoridade de status**; a **integração de consumidor**; a **criação do índice real**; **R2**; **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**; **LLM**; e a **3B.8**. **VERIFICAR A BIJEÇÃO NÃO É MATERIALIZAR `C`** |
| Entrega funcional **anterior a essa** | **Quinta microentrega funcional de `C` — avaliador determinístico booleano de `ASSERTIVA` sobre valor já resolvido**, em `src/casa77_sdr/response_assertion.py` (**PR #93** — commit funcional `efa903816b5dc1dafbce8161f6424abdf41f2ca6`, merge `353e1b42d6c8b31d649f59b151184811ef51462e`, branch de origem `feat/c-response-assertion`, título `feat: add deterministic assertion evaluator`). **Sem nomenclatura normativa `E2`, `E3`, `E4` ou `E5`.** **Inclui**: **`AssertivaNaoAvaliavel`** e **`avaliar_assertiva(predicado: str, valor: object) -> bool`** como **fronteira pública única** — **`__all__` com exatamente dois nomes**, **dois parâmetros**, **sem default** e **sem parâmetro de modo, estilo, origem, caminho ou configuração**. **Predicados suportados**, do vocabulário fechado de C-5: **`EH_VERDADEIRO`** e **`EH_FALSO`** — **nenhum terceiro** (**C-5g**, **C-5h**, **C-A1-R**). **Matriz avaliável, exaustiva**: `EH_VERDADEIRO` + `True` → `True`; `EH_VERDADEIRO` + `False` → `False`; `EH_FALSO` + `False` → `True`; `EH_FALSO` + `True` → `False`. **Domínio materializado**: **somente `bool` estrito já resolvido**; **qualquer valor fora dele é NÃO AVALIÁVEL** e levanta `AssertivaNaoAvaliavel` — **`0` não é `False`**, **`1` não é `True`**, e o valor **nunca** é convertido em assertiva falsa; **sem *truthiness***, **sem `bool(...)`**, **sem coerção**, **sem comparação com `1`/`0`**, **sem leitura de `"true"`/`"false"`**, **sem *parsing***, **sem normalização** e **sem *fallback***; `__bool__` e `__eq__` customizados **não** são consultados. **Predicado inválido**: não-`str` ou fora do vocabulário → **fail-closed** por `AssertivaNaoAvaliavel`, **sem `upper`**, **sem `strip`** e **sem tolerância de caixa**. **Precedência fixa**: **1.** tipo do predicado; **2.** valor do predicado; **3.** domínio do valor; **4.** avaliação — a **primeira violação encerra** e **nada é acumulado**. **Categorias técnicas privadas e fechadas**, que **não** são identificadores normativos de `C`: `tipo_invalido` e `valor_invalido`; **localizadores fechados**: `predicado` e `valor`. A mensagem tem a forma `<categoria>: <localizador>` e **nunca** ecoa o predicado, o valor, o tipo concreto, `repr`, conteúdo, índice, tamanho ou deslocamento; **sem `__cause__`** e **sem `__context__`**. **NÃO inclui**: a **criação do índice real**; a **gramática ou o resolvedor de `caminho_yaml`**; a **origem do referente** e o **fato de runtime**; **calendário**; **analisador ou extrator de Markdown**; *template*, *placeholder* ou *binding* físico; ***renderer***; **formatos**; a **bijeção física 37/37**; a **canonicalização ou migração de status**; a **integração de consumidor**; **R2**; **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**; **LLM**; e a **3B.8**. **Esta entrega NÃO declara que todo domínio futuro de `ASSERTIVA` seja booleano**, e **ampliar o domínio exige contrato posterior explícito**. **AVALIAR `ASSERTIVA` NÃO É MATERIALIZAR `C`** |
| Entrega funcional **anterior a essa (2)** | **Quarta microentrega funcional de `C` — formatadores determinísticos de apresentação pura de `C-6`**, em `src/casa77_sdr/response_format.py` (**PR #91** — commit funcional `7d8dd8617eb5cd8c346e67496c3631feafe97f4f`, merge `d15201b0a84bca332b09e0d5e623736605663962`, branch de origem `feat/c-response-formatters`, título `feat: add deterministic response formatters`). **Sem nomenclatura normativa `E2`, `E3` ou `E4`.** **Inclui**: **`FormatoInaplicavel`**; e as **cinco** funções puras **`formatar_inteiro(valor: int) -> str`**, **`formatar_inteiro_agrupado(valor: int) -> str`**, **`formatar_simbolo_moeda(codigo: str) -> str`**, **`formatar_texto(valor: str) -> str`** e **`formatar_lista(itens: Sequence[str]) -> str`** — **`__all__` com exatamente seis nomes**, **um parâmetro por função**, **sem default** e **sem parâmetro de estilo, padrão ou variante**. **`inteiro`** (C-6a): decimal do **mesmo** inteiro, **`int` estrito**, **`bool` recusado**, **sem coerção** de `float`, `Decimal` ou texto numérico, **sem agrupar, sem arredondar, sem zero acrescentado**, sinal preservado. **`inteiro_agrupado`** (C-6b, `C-A4-F1`): mesmo inteiro, agrupamento **da direita para a esquerda** em grupos de **três dígitos** unidos por **`.`**, **sem casa decimal, sem arredondamento, sem cálculo, sem zero para completar grupo**, sinal **preservado e não agrupado**, **sem *locale*** e **sem delegar ao `format` da linguagem** — o agrupamento é montado **dígito a dígito**. **`simbolo_moeda`** (C-6c, `C-A4-F2`): **tabela fechada** com **um único código**, devolvendo **somente o símbolo**, **sem whitespace antes ou depois**, **sem `upper`, sem `strip`, sem tolerância de caixa**, **sem inferir moeda** e **sem ler campo adicional**; código não suportado **FALHA**. **`texto`** (C-6e): **identidade exata**, devolvendo **a mesma `str`** — **sem NFC, sem `strip`, sem `casefold`, sem colapso de espaço, sem dobra de quebra e sem ajuste de pontuação**; a `str` vazia continua vazia. **`lista`** (C-6f, `C-A1-L`): **zero itens FALHA**; um item devolve o próprio item; dois unidos por ` e `; três ou mais com `, ` entre os anteriores e ` e ` antes do último; **ordem, cardinalidade e conteúdo literal preservados**, **sem filtrar, ordenar, flexionar, parafrasear ou prefixar** — **inclusive o item vazio, que o contrato não proíbe e que NÃO é filtrado**; **`str` não é contêiner válido** e cada item precisa ser `str`; a **entrada não é mutada**, nem no caminho de falha. **Categorias técnicas privadas e fechadas**, que **não** são identificadores normativos de `C`: `tipo_invalido` e `valor_invalido`; **localizadores fechados**: `valor`, `codigo`, `itens` e `itens.item`. **Fail-closed na primeira violação**, sem acumular, com mensagem de **categoria e localizador** que **nunca** ecoa o valor, o item, o código ou o conteúdo textual recebido, **sem `__cause__`** e **sem `__context__`**. **NÃO inclui**: o formato **`hora`** (C-6d), **expressamente fora**; a **criação do índice real**; **analisador ou extrator de Markdown**; *template*, *placeholder* ou *binding* físico; ***renderer***; a **avaliação de `ASSERTIVA`**; a **bijeção física 37/37**; a **integração de consumidor**; a **migração de autoridade de status**; **R2**; **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**; **calendário**; **LLM**; e a **3B.8**. **FORMATAR NÃO É MATERIALIZAR `C`** |
| Entrega funcional **anterior a essa (3)** | **Terceira microentrega funcional de `C` — comparador determinístico de equivalência textual de `C-15b`**, em `src/casa77_sdr/response_equivalence.py` (**PR #89** — commit funcional `23e3fa727eb1457cd98a0e0e6f36580dade2ab00`, merge `76531de7d3f4257d84b5a1f9498d8666c4e60030`, branch de origem `feat/c-response-equivalence`). **Sem nomenclatura normativa `E2` ou `E3`.** **Inclui**: **`EquivalenciaNaoDeterminavel`**; **`sao_textualmente_equivalentes(aprovado: str, renderizado: str) -> bool`** como **fronteira pública única**, sobre **duas `str` já em representação canônica** (D1); **tipo não-`str` → `TypeError`**, verificado **antes** da canonicidade; **violação de canonicidade → `EquivalenciaNaoDeterminavel`**, que **NÃO é `False`** (D6-A) e obriga o chamador a **parar ou escalar**; validação de **`aprovado` antes de `renderizado`**, com **primeira violação encerrando** e nada acumulado; **NFC antes da dobra**; **`LF` isolado → exatamente um `U+0020`** (D3); **`\n\n` preservado literalmente** (D4); **três ou mais `LF` recusados**; **`CR`, `CRLF`, `U+2028`, `U+2029`, `U+0085`, `U+000B` e `U+000C` recusados**, **sem converter `CRLF`** (D5); **`LF` de borda recusado**; **branco adjacente a `LF` recusado** (D7); **igualdade final exata**, **sem `strip`, sem `casefold`, sem *fuzzy* e sem transformação semântica**; e a **`str` vazia permanecendo canônica**. **Categorias técnicas privadas**, fechadas e **que não são identificadores normativos de `C`**: `terminador_proibido`, `quebra_na_borda`, `sequencia_de_quebras_excessiva` e `branco_adjacente_a_quebra`; a mensagem carrega **categoria e lado** — com localizador `inicio`/`fim`/`antes`/`depois` quando aplicável — e **nunca** o texto recebido, o caractere ofensor, deslocamento, índice ou comprimento, **sem `__cause__`**. **NÃO inclui**: a **criação do índice real**; **analisador ou extrator de Markdown**; *templates* ou *bindings* físicos; ***renderer***; **formatos**; a **integração de consumidor**; a **bijeção física 37/37**; a **migração de autoridade de status**; **R2**; **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**; **calendário**; **LLM**; e a **3B.8**. **COMPARAR NÃO É MATERIALIZAR `C`** |
| Entrega funcional **anterior a essa (4)** | **Segunda microentrega funcional de `C` — carregador *fail-closed* do futuro índice de respostas aprovadas**, em `src/casa77_sdr/response_index_load.py` (**PR #86** — commit funcional `b2b11e2465c7f332747a806c80b629e995f0f5a6`, merge `9bf68b8fece9ea66c74509490ddf6e02a0aa6f31`, branch de origem `feat/c-response-index-loader`). **Sem nomenclatura normativa `E2`.** **Inclui**: **`IndiceIlegivel`**; **`carregar_indice(path: str | Path)`** como **fronteira pública única**, com **caminho sempre explícito** — **sem caminho padrão, descoberta automática, glob ou variável de ambiente**; leitura **somente em UTF-8** e **somente leitura**; análise baseada **exclusivamente** em `yaml.SafeLoader`, via subclasse privada que **altera apenas a construção de mapeamento**; **rejeição *fail-closed* de chave YAML duplicada**, por mapeamento e em qualquer nível; a **taxonomia fechada de ilegibilidade** — `arquivo_ausente`, `leitura_falhou`, `codificacao_invalida`, `sintaxe_invalida` e `chave_duplicada` —, com mensagem de **categoria e caminho** que **não ecoa o conteúdo do arquivo** e **causa técnica encadeada em `__cause__`**; a **separação estrita entre artefato ilegível e estrutura inválida**; a **delegação integral** da validação estrutural a `validar_indice(...)`, com **`IndiceInvalido` propagando intacta**, sem captura, reembalagem, tradução de categoria ou duplicação de regra; e **zero normalização, zero valor padrão e zero *fallback*** após a análise. **Também remove** de `tests/test_response_index.py` o teste `test_indice_real_continua_inexistente`. **NÃO inclui**: a **criação do índice real**; a **conversão do Markdown**; *templates* ou *bindings* físicos; a **bijeção 37/37**; **C-15**; **renderização**; **aplicação de formatos**; **avaliação de `ASSERTIVA` contra dados reais**; **R2**; **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**; **calendário**; **LLM**; e a **3B.8**. **Sem numeração oficial de subetapa**: não é a 3B.8, que **não existe**. **Carregar não é materializar `C`** |
| Entrega funcional **anterior a essa (5)** | **`E1` — validador estrutural do futuro índice de respostas aprovadas**, em `src/casa77_sdr/response_index.py` (**PR #84** — commit funcional `02f1dd6621c31b90789c646bd8826e685f9ee019`, merge `95ed2ce4e9c54f9bdfb7b3f820e6f9e065cde24e`, branch de origem `feat/c-e1-response-index-validator`). **Primeira microentrega funcional de `C`.** **Inclui**: **`IndiceInvalido`**; **`validar_indice(indice: object) -> None`**; **schema estrutural fechado**; **vocabulários fechados** de status, mecanismo, origem, formato, predicado e fato runtime; **exclusividade `YAML` × `RUNTIME_AUTORITATIVO`**; **`RUNTIME_AUTORITATIVO` somente com `ASSERTIVA`**; as **regras estruturais de `RENDERIZADO`** (*placeholder* + formato) e de **`ASSERTIVA`** (predicado); **fail-closed na primeira violação**; **rejeição de seleção numericamente posicional**; e a **proteção contra índices posicionais mesmo após seletores textuais encadeados**. **NÃO inclui**: a **criação do índice real**; **loader**; **leitura de `knowledge/**` pelo módulo**; **conversão do Markdown**; **bindings reais**; a **bijeção 37/37**; **C-15**; **renderização**; **aplicação de formatos**; **avaliação de `ASSERTIVA` contra dados reais**; **R2**; **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**; **calendário**; **LLM**; e a **3B.8**. **Sem numeração oficial de subetapa**: não é a 3B.8, que **não existe**. **`E1` materializada NÃO é `C` materializada** |
| Entrega funcional **anterior a essa (6)** | **Materialização funcional do delta AJ2** — o **assunto** de `PerguntaComercial` na **fronteira determinística** da etapa 4, em `src/casa77_sdr/interpretation.py` (**PR #61** — commit funcional `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`, merge `5a722a5cc648149330362434694e7e76a40c1b57`, branch de origem `feat/materializar-aj2-assunto`). **Inclui**: **`AssuntoComercial`** como vocabulário fechado de **54** membros — **53 específicos + `ASSUNTO_NAO_CLASSIFICADO`** —, na **ordem documental** de `docs/07` §6.3; **`PerguntaComercial` com três campos** — `texto`, `confianca` e **`assunto`** —, o assunto **obrigatório** e **sem confiança própria**; a **ampliação de `E-Nb-5`** para assunto **ausente** (AJ2-X1) e **fora do vocabulário** (AJ2-X2), com **tipo runtime incompatível** continuando `TypeError` **sem código**; a validação nos **dois caminhos** — canonicalização e `Interpretacao` construída diretamente —, com a **precedência histórica** dos erros N-b/AJ1 **preservada**; e os cenários **`K-Nb-41`–`K-Nb-51`**. **Preserva**: a `ProjecaoInterpretacao` de **sete** campos — o assunto **não atravessa** —, **`IntencaoConversacional` com 11** valores, **N-b-X3** inalterada, a **condição 5** como única condição de §4.4 materializada, a lista **`E-Nb-1`–`E-Nb-19`** sem vigésimo código e o **não-export** pelo `casa77_sdr/__init__.py`. **NÃO inclui**: o **produtor não determinístico / LLM**; a **interpretação real de texto livre**; a **segmentação semântica** de consulta composta — que precisa chegar **já segmentada** do futuro produtor; **N-b-RES2**; a **integração operacional da etapa 4**; e o **`OrquestradorMotor`**. **Sem numeração oficial de subetapa**: não é a 3B.8, que **não existe** |
| Entrega funcional **anterior a essa (7)** | **Materialização da parte DETERMINÍSTICA de N-b** — a fronteira determinística da interpretação da etapa 4, em `src/casa77_sdr/interpretation.py` (PR #55). **Inclui**: a **canonicalização determinística** da `Interpretacao`; **`A1` derivado** dos payloads autoritativos; a **confiança `A1` calculada** por **N-b-X3**; a **projeção** para a `ProjecaoInterpretacao` **já existente**, de sete campos; a **condição 5** de `docs/07` §4.4 como função total; e a **validação de canonicidade** exigida também de uma `Interpretacao` construída diretamente. **NÃO inclui**: o **produtor não determinístico / LLM**; a **interpretação de texto livre**; **N-b-RES2**; a **integração operacional da etapa 4**; e o **`OrquestradorMotor`**. **Sem numeração oficial de subetapa**: não é a 3B.8, que **não existe** |
| Entrega funcional **anterior a essa (8)** | **Aplicação e escrita do marco temporal como fronteira chamável** — `criar_com_marco_de_transicao(...)` e `gravar_com_marco_de_transicao(...)` (`src/casa77_sdr/transition_marker_write.py`, PR #49 — commit `d621a2c7…`, merge `f82da69f…`). Também **sem numeração de subetapa** |
| Entrega funcional **anterior a essa (9)** | Decisão determinística do marco temporal — `decidir_instante_ultima_transicao(...)` e a **composição decisória das 0–3 `DecisaoMaquina`** do ciclo (PR #47 — commit `b2f9f74d…`, merge `dd5a4cc7…`). Também **sem numeração de subetapa** |
| Entrega funcional **anterior a essa (10)** | Materialização em runtime da projeção `transicoes_que_mudaram_estado` na `MaquinaEstados` / `DecisaoMaquina` (PR #44 — commit `2da532f1…`, merge `048a5483…`). Também **sem numeração de subetapa** |
| Entrega funcional **anterior a essa (11)** | Montagem determinística das projeções de identidade da etapa 3 — fronteira **etapa 3 → identidade/etapa 5** (PR #38 — commit `f312eaa5…`, merge `10810506…`). Também **sem numeração de subetapa** |
| Entrega funcional **anterior a essa (12)** | Implementação funcional da política N-a — produção determinística do conjunto elegível **E** (PR #36 — commit `51fae0d1…`, merge `383c5668…`). Também **sem numeração de subetapa** |
| Entrega funcional **anterior a essa (13)** | Evolução temporal do contrato de persistência operacional — `instante_ultima_transicao` (PR #33 — commit `0350e4ec…`, merge `1256628e…`). Também **sem numeração de subetapa** |
| Última **subetapa funcional numerada** concluída | 3B.7 — ResolvedorIdentidade determinístico (PR #29 — commit `25ab2726…`, merge `568919f5…`) |
| Subetapa 3B.7 | **CONCLUÍDA** |
| Arbitragem documental **N-a** | Arbitragem **N-a** — PR #31, commit `43774af5…`, merge `e8425410…`. **Não altera o marco funcional** |
| Arbitragem documental da **projeção de mudança de estado** | PR #42, commit documental `f7b5d94cd22ce0d0fcf573823d9f5e56c853ac99`, merge `210ef72790f6317719340e8e0f842d272db6e137`. **Não altera o marco funcional**. O contrato ali arbitrado foi **materializado depois** pelo **PR #44** |
| Micro-arbitragem documental **AJ1** — representação/canonicalização de N-b | PR #53, commit documental `d1137cf67c42eae37ec8e837a56350da6c7fbabe`, merge `2e9df1f4dfcd11903d410ba7a42ba12d86eb2b15`, branch de origem `docs/nb-aj1-canonicalizacao`. Arquivo: **exclusivamente** `docs/07-arquitetura-motor-respostas.md` — **156 adições, 1 remoção**. **Não alterou o marco funcional** e **não implementou código**. O contrato ali fechado foi **materializado depois**, **parcialmente**, pelo **PR #55** |
| Última **reconciliação documental** anterior a esta entrega | Reconciliação de `docs/00` após o PR #53 — PR #54, commit documental `0f67e7f4e9218ae9f8b56eca253d6e57147dfd03`, merge `3740a121c00631e2c60e71b99724e66cac12d11b`, branch de origem `docs/reconciliar-estado-pos-pr53`. Arquivo: **exclusivamente** `docs/00-estado-atual.md` — **170 adições, 37 remoções**. **Não altera o marco funcional** |
| Reconciliação documental **anterior a essa** | Reconciliação de `docs/00` após o PR #51 — PR #52, commit documental `f3fafee09b7d6bad464134fd9d20d603ebbb0122`, merge `cc7f4493b97935ef92efe2e821d7a032d16db1a4`, branch de origem `docs/reconciliar-estado-pos-pr51` — **148 adições, 40 remoções**. **Não altera o marco funcional** |
| Reconciliação documental **anterior a essa (2)** | Reconciliação de `docs/00` após o PR #49 — PR #50, commit documental `5509a3f2e01a79cf52acde427794b1de4ec07ff1`, merge `60701aaaf7a85614e27cf3e95b6a25870769aee5`, branch de origem `docs/reconciliar-estado-pos-pr49` — **217 adições, 120 remoções**. **Não altera o marco funcional** |
| Reconciliação documental **anterior a essa (3)** | Reconciliação de `docs/00` após o PR #47 — PR #48, commit documental `db9b202eeea95cbf249863a0cd4967627eae0156`, merge `5a059b4b7ba69e912c960bfa4d7a7990228a6792` — **125 adições, 78 remoções**. **Não altera o marco funcional** |
| Base da reconciliação **pós-PR #55** | `ba412502124bac3ce3f38554f81c265ed739672b` — HEAD da `main` verificado **antes** daquela reconciliação (PR #55, **funcional**) |
| Integração da **reconciliação pós-PR #55** | **PR #56** — merge na `main` `86258cfe0b99fc737b3bac042a521ed162aca152`, a partir da branch `docs/reconciliar-estado-pos-pr55`. **Documental**: **não altera o marco funcional** |
| Integração da **arbitragem C** | **PR #57** — commit documental `2ba5a2833350844f6148f1c3223bca1783342737`, merge na `main` `89458bb7efea23d8f7889a0b5ab076a1d0c7f130`, branch de origem `docs/arbitragem-c-indice-respostas`. Arquivos: **exclusivamente** `docs/00-estado-atual.md` e `docs/07-arquitetura-motor-respostas.md` — **401 adições, 6 remoções**. **Documental**: **não altera o marco funcional** e **não implementa código** |
| Base da entrega **AJ2** | `89458bb7efea23d8f7889a0b5ab076a1d0c7f130` — HEAD da `main` verificado **antes** daquela entrega |
| Integração da **arbitragem AJ2** | **PR #58** — commit documental `2dea157abee04407791ade56017b6fe159e91c74`, merge na `main` `111e5c31826ba839ff4e0599b45bc98d34620128`, branch de origem `docs/aj2-assunto-pergunta-comercial`. Arquivos: **exclusivamente** `docs/00-estado-atual.md` e `docs/07-arquitetura-motor-respostas.md` — **402 adições, 18 remoções**. **Documental**: **não altera o marco funcional** e **não implementa código** |
| Base da entrega **S2-D8** | `111e5c31826ba839ff4e0599b45bc98d34620128` — HEAD da `main` verificado **antes** daquela entrega |
| Integração da **arbitragem S2-D8** | **PR #59** — commit documental `6bbd1185d3a31cc3b307ce3c7c2abe67085e7c66`, merge na `main` `eff50138ce9e10ff71f34920077b843bbc201264`, branch de origem `docs/arbitragem-s2-d8`. Arquivos: **exclusivamente** `docs/00-estado-atual.md`, `docs/06-maquina-de-estados.md` e `docs/07-arquitetura-motor-respostas.md` — **673 adições, 36 remoções**. **Documental**: **não altera o marco funcional** e **não implementa código** |
| Base da reconciliação **pós-PR #59** | `eff50138ce9e10ff71f34920077b843bbc201264` — HEAD da `main` verificado **antes** daquela reconciliação |
| Integração da **reconciliação pós-PR #59** | **PR #60** — commit documental `be592a800934d2eab5c9bc21877792bae5ed8e83`, merge na `main` `5a1cd85ff6814750bfb2740fa2155f3bf528d029`, branch de origem `docs/reconciliar-estado-pos-pr59`. Arquivo: **exclusivamente** `docs/00-estado-atual.md` — **27 adições, 6 remoções**. **Documental**: **não altera o marco funcional** |
| Base da **materialização funcional AJ2** | `5a1cd85ff6814750bfb2740fa2155f3bf528d029` — HEAD da `main` verificado **antes** daquela entrega |
| Integração da **materialização funcional AJ2** | **PR #61** — commit **funcional** `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`, merge na `main` `5a722a5cc648149330362434694e7e76a40c1b57`, branch de origem `feat/materializar-aj2-assunto`. Arquivos: **exclusivamente** `src/casa77_sdr/interpretation.py`, `tests/test_interpretation.py` e `docs/07-arquitetura-motor-respostas.md` — **762 adições, 28 remoções**. **FUNCIONAL**: **passa a ser o marco funcional** da `main`, **sem numeração de subetapa** |
| Base da reconciliação **pós-PR #61** | `5a722a5cc648149330362434694e7e76a40c1b57` — HEAD da `main` verificado **antes** daquela reconciliação |
| Integração da **reconciliação pós-PR #61** | **PR #62** — commit documental `72310436d479fcb8494f9957fb42e7da1ac63a83`, merge na `main` `4ba1cdfe4397e90692efdec06357cb079e44ca8a`, branch de origem `docs/reconciliar-estado-pos-pr61`. Arquivo: **exclusivamente** `docs/00-estado-atual.md` — **116 adições, 39 remoções**. **Documental**: **não altera o marco funcional** |
| Base da entrega **C-A1** | `4ba1cdfe4397e90692efdec06357cb079e44ca8a` — HEAD da `main` verificado **antes** daquela entrega |
| Integração da **micro-arbitragem C-A1** | Commit documental `64b5b15…`, merge na `main` `a60c57dbf029913a623ad87bb24795fe333cdc3f`, **PR #63**, branch de origem `docs/arbitragem-c-a1`. Arquivos: **exclusivamente** `docs/00-estado-atual.md` e `docs/07-arquitetura-motor-respostas.md`. **Documental**: **não altera o marco funcional** e **não implementa código** |
| Base da entrega **C-A2 — Entrega 1** | `a60c57dbf029913a623ad87bb24795fe333cdc3f` — HEAD da `main` verificado **antes** daquela entrega |
| Integração da **C-A2 — Entrega 1** | **PR #64** — commit documental `294a11a1c170815063764f1d49ae0d831b72d359`, merge na `main` `25b867f1c6cb4d2d00cd49ea60361c82a6e98f6f`, branch de origem `docs/arbitragem-c-a2`. Arquivos: **exclusivamente** `docs/00-estado-atual.md` e `docs/07-arquitetura-motor-respostas.md` — **467 adições, 4 remoções**. **Documental**: **não altera o marco funcional** e **não implementa código** |
| Base da entrega **C-A2 — Entrega 2** | `25b867f1c6cb4d2d00cd49ea60361c82a6e98f6f` — HEAD da `main` verificado **antes** daquela entrega |
| Integração da **C-A2 — Entrega 2** | **PR #65** — commit `c2883d2fad32638d1e15a616a2b37f577abf3e42`, merge na `main` `fbe768a14457241245c73f4cbe8ef93e869e7fb3`, branch de origem `docs/aplicar-conteudo-c-a2`. Arquivos: **exclusivamente** `docs/00-estado-atual.md`, `docs/02-fluxo-comercial.md`, `docs/03-regras-de-conversa.md`, `docs/04-handoff-humano.md`, `knowledge/respostas-aprovadas.md` e `prompts/prompt-sistema-bot.md` — **seis arquivos**, **219 adições, 74 remoções**. **Documental/comportamental**: **não altera `src/` nem `tests/`**, **não cria marco funcional** e **não substitui o último marco funcional** |
| Base da reconciliação **pós-PR #65** | `fbe768a14457241245c73f4cbe8ef93e869e7fb3` — HEAD da `main` verificado **antes** daquela reconciliação |
| Integração da **reconciliação pós-PR #65** | **PR #66** — commit documental `8b82a638709110235eb6acf936b2ba68e9242143`, merge na `main` `118054575e7f7560a1c37ca430bdedd15eddc817`, branch de origem `docs/reconciliar-c-a2-pos-pr65`. Arquivo: **exclusivamente** `docs/00-estado-atual.md` — **48 adições, 4 remoções**. **Documental**: **não altera o marco funcional** |
| Base da entrega **registro de C-A1-M4** | `118054575e7f7560a1c37ca430bdedd15eddc817` — HEAD da `main` verificado **antes** daquela entrega |
| Integração do **registro de C-A1-M4** | **PR #67** — commit documental `56d8c9d21c3167b5078ce5e45b19d48a1c0bfd6b`, merge na `main` `de13a513990fe17f83010bc9b2213748241bcad4`, branch de origem `docs/registrar-c-a1-m4-auditoria`. Arquivo: **exclusivamente** `docs/00-estado-atual.md` — **44 adições, 3 remoções**. **Documental**: **não altera o marco funcional** |
| Base da entrega **M1 — `MD-18` + `MD-20`** | `de13a513990fe17f83010bc9b2213748241bcad4` — HEAD da `main` verificado **antes** daquela entrega |
| Integração de **M1 — `MD-18` + `MD-20`** | **PR #68** — commit `953039b3318df38f451d57175dc3fb85eed77278`, merge na `main` `3ad807fec57a3e21061dbee5fa3b3c14573eb2ac`, branch de origem `feat/c-a2-n11-m1-md18-md20`. Arquivos: **exclusivamente** `knowledge/casa77.yaml` e `docs/00-estado-atual.md` — **55 adições, 2 remoções**. **Modelagem da base autoritativa**: **não altera `src/` nem `tests/`** e **não cria marco funcional de código** |
| Base da entrega **`MD-4`** | `3ad807fec57a3e21061dbee5fa3b3c14573eb2ac` — HEAD da `main` verificado **antes** daquela entrega |
| Integração de **`MD-4`** | **PR #69** — commit `b827306d28b552e54b14c06e75fa8c412fa9b4e9`, merge na `main` `6868042f813f940191fc4cd45266680e39f49b7c`, branch de origem `feat/c-a2-n11-md4`. Arquivos: **exclusivamente** `knowledge/casa77.yaml` e `docs/00-estado-atual.md` — **47 adições, 5 remoções**. **Modelagem da base autoritativa**: **não altera `src/` nem `tests/`** e **não cria marco funcional de código** |
| Base da entrega **`MD-17`** | `6868042f813f940191fc4cd45266680e39f49b7c` — HEAD da `main` verificado **antes** daquela entrega |
| Integração de **`MD-17`** | **PR #70** — commit `8e8efed1ca72651a19a4770c8a6c424af06f851b`, merge na `main` `d48692e7810c5d10b2cd2e43adcca1d157d0bfd5`, branch de origem `feat/c-a2-n11-md17`. Método: **merge commit**, com **dois parents**. Arquivos: **exclusivamente** `knowledge/casa77.yaml` e `docs/00-estado-atual.md` — **67 adições, 27 remoções**. **Modelagem da base autoritativa**: **não altera `src/` nem `tests/`** e **não cria marco funcional de código** |
| Base da entrega **M3 — `MD-8`** + **`MD-9`** + **`MD-10`** + **`MD-11`** | `d48692e7810c5d10b2cd2e43adcca1d157d0bfd5` — HEAD da `main` verificado **antes** daquela entrega |
| Integração de **M3 — `MD-8`** + **`MD-9`** + **`MD-10`** + **`MD-11`** | **PR #71** — commit `930b3c3c07d82f470bef0fc91e685f4257551b63`, merge na `main` `c46076659f79f5a9f5c63edc109e153bcd9724fa`, branch de origem `feat/c-a2-n11-m3-md8-md11`. Método: **merge commit**, com **dois parents**. Arquivos: **exclusivamente** `knowledge/casa77.yaml` e `docs/00-estado-atual.md` — **113 adições, 29 remoções**. **Modelagem da base autoritativa**: **não altera `src/` nem `tests/`** e **não cria marco funcional de código** |
| Base da entrega **M4 — `MD-12`** + **`MD-13`** + **`MD-19`** | `c46076659f79f5a9f5c63edc109e153bcd9724fa` — HEAD da `main` verificado **antes** daquela entrega |
| Integração de **M4 — `MD-12`** + **`MD-13`** + **`MD-19`** | **PR #72** — commit `b7f8e11c732d1c8cba6d6f34f5be2ea434351bec`, merge na `main` `3758b107aa9c96af1f25825e209588a3bb7841ea`, branch de origem `feat/c-a2-n11-m4-md12-md13-md19`. Método: **merge commit**, com **dois parents**. Arquivos: **exclusivamente** `knowledge/casa77.yaml` e `docs/00-estado-atual.md` — **111 adições, 33 remoções**. **Modelagem da base autoritativa**: **não altera `src/` nem `tests/`** e **não cria marco funcional de código** |
| Base da entrega **M5 — `MD-2`** + **`MD-5`** | `3758b107aa9c96af1f25825e209588a3bb7841ea` — HEAD da `main` verificado **antes** daquela entrega |
| Integração de **M5 — `MD-2`** + **`MD-5`** | **PR #73** — commit `b564a3e4d6515f4028c078f16ce52163e99893bc`, merge na `main` `6e79cbac502a81fa167d37ff41b33df9ec95c9d7`, branch de origem `feat/c-a2-n11-m5-md2-md5`. Método: **merge commit**, com **dois parents**. Arquivos: **exclusivamente** `knowledge/casa77.yaml` e `docs/00-estado-atual.md` — **95 adições, 21 remoções**. **Modelagem da base autoritativa**: **não altera `src/` nem `tests/`** e **não cria marco funcional de código** |
| Base da entrega **`C-A3`** (documental) | `6e79cbac502a81fa167d37ff41b33df9ec95c9d7` — HEAD da `main` verificado **antes** daquela entrega |
| Integração da **micro-arbitragem `C-A3`** | **PR #74** — commit documental `b584d5f43bf022062e0c43bd60131f15ce29b716`, merge na `main` `224ae8fd8fe2c9430125df85733b90beb1b44ecb`, branch de origem `docs/c-a3-empresa-descricao-c`. Método: **merge commit**, com **dois parents** — `6e79cbac502a81fa167d37ff41b33df9ec95c9d7` e o commit de conteúdo `b584d5f43bf022062e0c43bd60131f15ce29b716`. Arquivos: **exclusivamente** `docs/00-estado-atual.md` e `docs/07-arquitetura-motor-respostas.md` — **164 adições, 7 remoções**. **Documental / governança**: **não altera o marco funcional** e **não implementa código** |
| Base da entrega **M6 — `MD-6`** + **`MD-7′`** | `224ae8fd8fe2c9430125df85733b90beb1b44ecb` — HEAD da `main` verificado **antes** daquela entrega |
| Integração de **M6 — `MD-6`** + **`MD-7′`** | **PR #75** — commit `5520cd77df8131eb4ba1093b6929e693547a5141`, merge na `main` `9b44cc1c01403ce5e9bb4997088d75c9da207c28`, branch de origem `feat/c-a2-n11-m6-md6-md7`. Método: **merge commit**, com **dois parents** — `224ae8fd8fe2c9430125df85733b90beb1b44ecb` e o commit de conteúdo `5520cd77df8131eb4ba1093b6929e693547a5141`. Arquivos: **exclusivamente** `docs/00-estado-atual.md` e `knowledge/casa77.yaml` — **86 adições, 13 remoções**. **Modelagem da base autoritativa**: **não altera `src/` nem `tests/`** e **não cria marco funcional de código** |
| Base da entrega **M7 — `MD-14`** | `9b44cc1c01403ce5e9bb4997088d75c9da207c28` — HEAD da `main` verificado **antes** daquela entrega |
| Integração de **M7 — `MD-14`** | **PR #76** — commit `9a56fa80bbc312b2085480f87e572ff6e0f768b3`, merge na `main` `f446d3fa36a9b3f4b76c3b329a19356b3ddbe394`, branch de origem `feat/c-a2-n11-m7-md14`. Método: **merge commit**, com **dois parents** — `9b44cc1c01403ce5e9bb4997088d75c9da207c28` e o commit de conteúdo `9a56fa80bbc312b2085480f87e572ff6e0f768b3`. Arquivos: **exclusivamente** `docs/00-estado-atual.md`, `docs/06-maquina-de-estados.md` e `knowledge/casa77.yaml` — **109 adições, 9 remoções**. **Modelagem da base autoritativa + reconciliação documental vinculada**: **não altera `src/` nem `tests/`** e **não cria marco funcional de código**. Com este merge, **`C-A2-N11` = CUMPRIDA — 16/16** passou a ser o **estado oficial da `main`** |
| Base da entrega **M8 — `FE-11b`** + reconciliação da **`FE-11a`** | `f446d3fa36a9b3f4b76c3b329a19356b3ddbe394` — HEAD da `main` verificado **antes** daquela entrega |
| Integração de **M8 — `FE-11b`** + reconciliação da **`FE-11a`** | **PR #77** — commit `e632ae71e043568f19ed26bf0101eb214d87a2f9`, merge na `main` `c36529c7323e2f2030b9c6664292594203226ac4`, branch de origem `feat/c-a2-m8-fe11b`. Método: **merge commit**, com **dois parents** — `f446d3fa36a9b3f4b76c3b329a19356b3ddbe394` e o commit de conteúdo `e632ae71e043568f19ed26bf0101eb214d87a2f9`. Arquivos: **exclusivamente** `docs/00-estado-atual.md`, `knowledge/casa77.yaml` e `knowledge/respostas-aprovadas.md` — **98 adições, 18 remoções**. **Modelagem / reconciliação da base autoritativa + reconciliação de instrução interna**: **sem alteração de código** — **não altera `src/` nem `tests/`** — e **sem novo marco funcional**. Com este merge, **`FE-11b` = APLICADA / MATERIALIZADA POR REMOÇÃO** e **`FE-11a` = APLICADA / RECONCILIADA** passam a ser o **estado oficial da `main`** |
| Base da reconciliação **pós-`M8`** | `c36529c7323e2f2030b9c6664292594203226ac4` — HEAD da `main` verificado **antes** daquela entrega |
| Integração da reconciliação **pós-`M8`** | **PR #78** — commit de conteúdo `d3ab33c918d4e2aaef67f042472c5f3a72a6e4a9`, merge na `main` `2dd6536398d3c6c0ea62934c4c88b53263cc385f`, branch de origem `docs/reconciliar-m8-pos-pr77`. Arquivo: **exclusivamente** `docs/00-estado-atual.md` — **59 adições, 7 remoções**. **RECONCILIAÇÃO DOCUMENTAL, SEM ALTERAÇÃO DE FONTE FACTUAL, SEM ALTERAÇÃO DE CÓDIGO E SEM NOVO MARCO FUNCIONAL** |
| Base da entrega **`C-A4`** (documental) | `2dd6536398d3c6c0ea62934c4c88b53263cc385f` — HEAD da `main` verificado **antes** daquela entrega |
| Integração de **`C-A4`** | **PR #79** — commit de conteúdo `2a4201f64444bc54107aca3946bc698099e34b8d`, merge na `main` `4836c245d8151a9fe021ec107155ea4afb19f8a6`, branch de origem `docs/c-a4-criterio-n12`. Método: **merge commit**, com **dois parents** — `2dd6536398d3c6c0ea62934c4c88b53263cc385f` e o commit de conteúdo `2a4201f64444bc54107aca3946bc698099e34b8d`. Arquivos: **exclusivamente** `docs/00-estado-atual.md` e `docs/07-arquitetura-motor-respostas.md` — **201 adições, 10 remoções**, sendo `docs/07` **puramente aditivo** (**144 adições, 0 remoções**). **MICRO-ARBITRAGEM DOCUMENTAL, SEM ALTERAÇÃO DE FONTE FACTUAL, SEM ALTERAÇÃO DE CÓDIGO E SEM NOVO MARCO FUNCIONAL** |
| Base auditada da **PRIMEIRA execução** de **`C-A2-N12`** (histórico) | `70abde5550be349a2a8ead1d66c106013ebf78aa` — HEAD da `main` sobre o qual a validação `C-8` / `C-15` / `C-A1` foi executada **naquela ocasião** |
| Resultado da **PRIMEIRA execução** de **`C-A2-N12`** (histórico — **superado** pela execução posterior) | **EXECUTADA COMPLETAMENTE / NÃO CUMPRIDA** — cobertura **37/37** fragmentos emitíveis; **1** bloqueio estrutural residual (**`R22`**, eixo **`C-8`**); **36** sem bloqueio; **`C-15` sem `FAIL-CLOSED`**; **`NÃO DETERMINÁVEL` residual = 0**; **`DIVERGÊNCIA DE BASE` impeditiva = 0**. Execução **estritamente read-only**: **nenhum arquivo do repositório foi alterado** |
| Evidência da **PRIMEIRA execução** de **`C-A2-N12`** (histórico) | Relatório de auditoria **NÃO VERSIONADO**, mantido **fora do repositório**, SHA-256 `bd4e3915a49ca9f768ef4a1003e322dd5b6717c85837038ecb5545219c57ebec`. É **evidência auxiliar** e **NÃO é fonte de verdade** |
| Base da **correção factual de `R22`** | `d56d90846f8c8e1a8cd5ce964d4be16764d7cf47` — HEAD da `main` verificado **antes** desta correção |
| Fato estruturado da **aproximação** | `estrutura.percentual_coberto_aproximado` — **booleano** em `knowledge/casa77.yaml`, acrescentado **imediatamente após** `estrutura.percentual_coberto`, que permanece **inalterado**. `versao` continua `1.1` e `ultima_atualizacao` continua `2026-08-15` |
| Base auditada **pós-correção `R22`** (nova execução read-only) | `bd9687c69ddf7db9306363d5de4cf74072b5a134` — HEAD da `main` sobre o qual a validação `C-8` / `C-15` / `C-A1` foi **reexecutada integralmente** |
| **Resultado OFICIAL de `C-A2-N12`** | **CUMPRIDA** — cobertura **37/37** fragmentos emitíveis em **12 eixos**, **444/444** resultados (**265 `PASS`**, **179 `N/A`**); **0 `FAIL-CLOSED`**; **0 `NÃO DETERMINÁVEL`**; **0 `DIVERGÊNCIA DE BASE`**. Em **`R22`**: **`C-8` = `PASS`** e **`C-15` = `PASS`**. Execução **estritamente read-only**: **nenhum arquivo do repositório foi alterado** |
| Contagens por eixo da nova execução | `C-8` **30/7 `N/A`** · `C-15` **19/18 `N/A`** · `C-A1-B` **37** · `C-A1-ST` **37** · `C-A1-F` **19/18 `N/A`** · `C-A1-L` **5/32 `N/A`** · `C-A1-R` **24/13 `N/A`** · `C-A1-S` **6/31 `N/A`** · `C-A1-M` **37** · `C-A2-B` **17/20 `N/A`** · `C-A2-RT` **32/5 `N/A`** · `C-A2-V` **2/35 `N/A`** |
| Evidência da nova execução de **`C-A2-N12`** | Relatório de auditoria **NÃO VERSIONADO**, mantido **fora do repositório**, SHA-256 `3807a60e1d5c049d0b17396e46f9e22c1b8d190521e7effa6ec07e27e98a335a`. É **evidência auxiliar** e **NÃO é fonte de verdade** |
| Base da entrega **`E1`** (funcional) | `ffeeba9bdaac5c4c600cc9b0ffd93600fc9eee2b` — HEAD da `main` verificado **antes** daquela entrega |
| Integração de **`E1`** | **PR #84** — commit **funcional** `02f1dd6621c31b90789c646bd8826e685f9ee019`, merge na `main` `95ed2ce4e9c54f9bdfb7b3f820e6f9e065cde24e`, branch de origem `feat/c-e1-response-index-validator`. Método: **merge commit**, com **dois parents** — `ffeeba9bdaac5c4c600cc9b0ffd93600fc9eee2b` e o commit funcional `02f1dd6621c31b90789c646bd8826e685f9ee019`. Arquivos: **exclusivamente** `src/casa77_sdr/response_index.py` e `tests/test_response_index.py` — **dois arquivos novos**, **1343 adições, 0 remoções** (**350 / 0** e **993 / 0**). **FUNCIONAL**: **passa a ser o marco funcional** da `main`, **sem numeração de subetapa**. **Não altera `knowledge/`, `docs/` nem `prompts/`** e **não cria o índice** |
| Base da reconciliação **pós-PR #84** | `95ed2ce4e9c54f9bdfb7b3f820e6f9e065cde24e` — HEAD da `main` verificado **antes** daquela reconciliação |
| Integração da **reconciliação pós-PR #84** | **PR #85** — commit documental `d97594112c509536437cd28e5de8d86d8021421c`, merge na `main` `bb5a58144ead6323e1b6271511a9d9e98295f440`, branch de origem `docs/reconciliar-estado-pos-pr84`. Arquivo: **exclusivamente** `docs/00-estado-atual.md`. **Documental**: **não altera o marco funcional** |
| Base da **segunda microentrega de `C`** (funcional) | `bb5a58144ead6323e1b6271511a9d9e98295f440` — HEAD da `main` verificado **antes** daquela entrega |
| Integração da **segunda microentrega de `C`** | **PR #86** — commit **funcional** `b2b11e2465c7f332747a806c80b629e995f0f5a6`, merge na `main` `9bf68b8fece9ea66c74509490ddf6e02a0aa6f31`, branch de origem `feat/c-response-index-loader`. Método: **merge commit**, com **dois parents** — `bb5a58144ead6323e1b6271511a9d9e98295f440` e o commit funcional `b2b11e2465c7f332747a806c80b629e995f0f5a6`. Arquivos: **exclusivamente** `src/casa77_sdr/response_index_load.py` (**novo**, +133 / −0), `tests/test_response_index_load.py` (**novo**, +953 / −0) e `tests/test_response_index.py` (**modificado**, +0 / −5) — **três arquivos**, **1086 adições, 5 remoções**. **FUNCIONAL**: **passa a ser o marco funcional** da `main`, **sem numeração de subetapa**. **Não altera `knowledge/`, `docs/` nem `prompts/`**, **não altera `src/casa77_sdr/response_index.py`** e **não cria o índice** |
| Base da reconciliação **pós-PR #86** | `9bf68b8fece9ea66c74509490ddf6e02a0aa6f31` — HEAD da `main` verificado **antes** daquela reconciliação |
| Integração da **reconciliação pós-PR #86** | **PR #87** — commit documental `fa1d91e12b58d1ed658c70bbeb8894dd8c6793ca`, merge na `main` `9cd6d4b029f6495dfb8b95db917c958da0fd9b2f`, branch de origem `docs/reconciliar-estado-pos-pr86`. Arquivo: **exclusivamente** `docs/00-estado-atual.md` — **213 adições, 57 remoções**. **Documental**: **não altera o marco funcional** |
| Base da **micro-arbitragem de `C-15b`** (documental) | `9cd6d4b029f6495dfb8b95db917c958da0fd9b2f` — HEAD da `main` verificado **antes** daquela entrega |
| Integração da **micro-arbitragem de `C-15b`** | **PR #88** — commit documental `2eacac1a1fb00a588a93645ac043eaa1f149cc61`, merge na `main` `a2920e1e8208be7b4b54d31d663440a9c65fbc6c`, branch de origem `docs/arbitrar-c15b-representacao-canonica`. Arquivos: **exclusivamente** `docs/00-estado-atual.md` e `docs/07-arquitetura-motor-respostas.md` — **170 adições, 2 remoções**. **Documental**: **não altera o marco funcional** e **não implementa o comparador** |
| Base da **terceira microentrega de `C`** (funcional) | `a2920e1e8208be7b4b54d31d663440a9c65fbc6c` — HEAD da `main` verificado **antes** daquela entrega |
| Integração da **terceira microentrega de `C`** | **PR #89** — commit **funcional** `23e3fa727eb1457cd98a0e0e6f36580dade2ab00`, merge na `main` `76531de7d3f4257d84b5a1f9498d8666c4e60030`, branch de origem `feat/c-response-equivalence`, título `feat: add response text equivalence`. Método: **merge commit**, com **dois parents** — `a2920e1e8208be7b4b54d31d663440a9c65fbc6c` e o commit funcional `23e3fa727eb1457cd98a0e0e6f36580dade2ab00`. Arquivos: **exclusivamente** `src/casa77_sdr/response_equivalence.py` (**novo**, +172 / −0) e `tests/test_response_equivalence.py` (**novo**, +793 / −0) — **dois arquivos**, **965 adições, 0 remoções**. **FUNCIONAL**: **passa a ser o marco funcional** da `main`, **sem numeração de subetapa**. **Não altera arquivo preexistente algum**, **não altera `knowledge/`, `docs/` nem `prompts/`** e **não cria o índice** |
| Base da reconciliação **pós-PR #89** | `76531de7d3f4257d84b5a1f9498d8666c4e60030` — HEAD da `main` verificado **antes** daquela reconciliação |
| Integração da **reconciliação pós-PR #89** | **PR #90** — commit documental `98134a24452d67d8e17fae69828f32431e2b6c22`, merge na `main` `4df6b58e196ba649bc35fdedab82b084592a0379`, branch de origem `docs/reconciliar-estado-pos-pr89`. Método: **merge commit**, com **dois parents** — `76531de7d3f4257d84b5a1f9498d8666c4e60030` e o commit documental `98134a24452d67d8e17fae69828f32431e2b6c22`. Arquivo: **exclusivamente** `docs/00-estado-atual.md` — **191 adições, 61 remoções**. **Documental**: **não altera o marco funcional** |
| Base da **quarta microentrega de `C`** (funcional) | `4df6b58e196ba649bc35fdedab82b084592a0379` — HEAD da `main` verificado **antes** daquela entrega |
| Integração da **quarta microentrega de `C`** | **PR #91** — commit **funcional** `7d8dd8617eb5cd8c346e67496c3631feafe97f4f`, merge na `main` `d15201b0a84bca332b09e0d5e623736605663962`, branch de origem `feat/c-response-formatters`, título `feat: add deterministic response formatters`, integrada em **2026-09-01T14:03:24Z**. Método: **merge commit**, com **dois parents** — `4df6b58e196ba649bc35fdedab82b084592a0379` e o commit funcional `7d8dd8617eb5cd8c346e67496c3631feafe97f4f` —, **sem squash, sem rebase e sem exclusão de branch**. Arquivos: **exclusivamente** `src/casa77_sdr/response_format.py` (**novo**, **+197 / −0**) e `tests/test_response_format.py` (**novo**, **+1170 / −0**) — **dois arquivos**, **1367 adições, 0 remoções**. **FUNCIONAL**: **passa a ser o marco funcional** da `main`, **sem numeração de subetapa**. **Não altera arquivo preexistente algum**, **não altera `knowledge/`, `docs/` nem `prompts/`**, **não altera `casa77_sdr/__init__.py`**, **não cria o índice** e **não implementa `hora`** |
| Base da reconciliação **pós-PR #91** | `d15201b0a84bca332b09e0d5e623736605663962` — HEAD da `main` verificado **antes** daquela reconciliação |
| Integração da **reconciliação pós-PR #91** | **PR #92** — commit documental `a4d908d8d6bf77aac96565c9883a39d578920089`, merge na `main` `c4df73cf60d5ec79549aa9015fc3c9820431936a`, branch de origem `docs/reconciliar-estado-pos-pr91`. Método: **merge commit**, com **dois parents** — `d15201b0a84bca332b09e0d5e623736605663962` e o commit documental `a4d908d8d6bf77aac96565c9883a39d578920089`. Arquivo: **exclusivamente** `docs/00-estado-atual.md` — **306 adições, 58 remoções**. **Documental**: **não altera o marco funcional** |
| Base da **quinta microentrega de `C`** (funcional) | `c4df73cf60d5ec79549aa9015fc3c9820431936a` — HEAD da `main` verificado **antes** daquela entrega |
| Integração da **quinta microentrega de `C`** | **PR #93** — commit **funcional** `efa903816b5dc1dafbce8161f6424abdf41f2ca6`, merge na `main` `353e1b42d6c8b31d649f59b151184811ef51462e`, branch de origem `feat/c-response-assertion`, título `feat: add deterministic assertion evaluator`, integrada em **2026-09-01T18:00:57Z**. Método: **merge commit**, com **dois parents** — `c4df73cf60d5ec79549aa9015fc3c9820431936a` e o commit funcional `efa903816b5dc1dafbce8161f6424abdf41f2ca6` —, **sem squash, sem rebase e sem exclusão de branch**. Arquivos: **exclusivamente** `src/casa77_sdr/response_assertion.py` (**novo**, **+105 / −0**) e `tests/test_response_assertion.py` (**novo**, **+843 / −0**) — **dois arquivos**, **948 adições, 0 remoções**. Os **blobs integrados** são exatamente os **blobs staged auditados**: `dd6e6f6bbc391800e204632a4d8a3ccf84eaf41f` para o módulo e `e4b2a7a44d975a850cc823a62619ebe7397c0185` para o teste. **FUNCIONAL**: **passa a ser o marco funcional** da `main`, **sem numeração de subetapa**. **Não altera arquivo preexistente algum**, **não altera `knowledge/`, `docs/` nem `prompts/`**, **não altera `casa77_sdr/__init__.py`**, **não cria o índice** e **não implementa `hora`** |
| Base da reconciliação **pós-PR #93** | `353e1b42d6c8b31d649f59b151184811ef51462e` — HEAD da `main` verificado **antes** daquela reconciliação |
| Integração da **reconciliação pós-PR #93** | **PR #94** — commit documental `fc354eec23ec4a109ef1ce790b322dabbffbcb0e`, merge na `main` `db7182f13747e64d2d79009c988bd723fba1501d`, branch de origem `docs/reconciliar-estado-pos-pr93`. Método: **merge commit**, com **dois parents** — `353e1b42d6c8b31d649f59b151184811ef51462e` e o commit documental `fc354eec23ec4a109ef1ce790b322dabbffbcb0e`. Arquivo: **exclusivamente** `docs/00-estado-atual.md` — **285 adições, 57 remoções**. **Documental**: **não altera o marco funcional** |
| Base da **sexta microentrega de `C`** (funcional) | `db7182f13747e64d2d79009c988bd723fba1501d` — HEAD da `main` verificado **antes** daquela entrega |
| Integração da **sexta microentrega de `C`** | **PR #95** — commit **funcional** `bdd0b2acc415ab6307c7c8da2adbad15f42cb75f`, merge na `main` `b06c0a43bd2f96b8712638e99c55edfe2fb2f99f`, branch de origem `feat/c-response-bijection`, título `feat: add deterministic response bijection validator`, integrada em **2026-09-02T13:26:46Z**. Método: **merge commit**, com **dois parents** — `db7182f13747e64d2d79009c988bd723fba1501d` e o commit funcional `bdd0b2acc415ab6307c7c8da2adbad15f42cb75f` —, **sem squash, sem rebase e sem exclusão de branch**. Arquivos: **exclusivamente** `src/casa77_sdr/response_bijection.py` (**novo**, **+245 / −0**) e `tests/test_response_bijection.py` (**novo**, **+1227 / −0**) — **dois arquivos**, **1472 adições, 0 remoções**. Os **blobs integrados** são exatamente os **blobs staged auditados**: `b76ed3e89bb095b5b2cc906ac8fa885c04691e62` para o módulo e `e54cce878ccd2737efff70738c90ad84cf31eb3b` para o teste. **Sem CI remoto configurado** — `gh pr checks 95` reportou **ausência de checks**, o que é **ausência de CI, não falha de CI**. **FUNCIONAL**: **passa a ser o marco funcional** da `main`, **sem numeração de subetapa**. **Não altera arquivo preexistente algum**, **não altera `knowledge/`, `docs/` nem `prompts/`**, **não altera `casa77_sdr/__init__.py`**, **não cria o índice** e **não implementa `hora`** |
| Base da reconciliação **pós-PR #95** | `b06c0a43bd2f96b8712638e99c55edfe2fb2f99f` — HEAD da `main` verificado **antes** daquela reconciliação |
| Integração da **reconciliação pós-PR #95** | **PR #96** — commit documental `82e2ee972566f0e4d45e652e60be3c257d0670e7`, merge na `main` `b48db2c58b0348b40773baffcc60180cfdc06bb1`, branch de origem `docs/reconciliar-estado-pos-pr95`. Método: **merge commit**, com **dois parents** — `b06c0a43bd2f96b8712638e99c55edfe2fb2f99f` e o commit documental `82e2ee972566f0e4d45e652e60be3c257d0670e7`. Arquivo: **exclusivamente** `docs/00-estado-atual.md` — **327 adições, 66 remoções**. **Documental**: **não altera o marco funcional** |
| Base da **sétima microentrega de `C`** (funcional) | `b48db2c58b0348b40773baffcc60180cfdc06bb1` — HEAD da `main` verificado **antes** daquela entrega |
| Integração da **sétima microentrega de `C`** | **PR #97** — commit **funcional** `4749efa74d5684b52b4f457176710ba6e212c627`, merge na `main` `8c67e13808da59dbace413fce33c2c22280e69a3`, branch de origem `feat/c-response-status`, título `feat: add deterministic response status canonicalizer`, integrada em **2026-09-02T20:47:15Z**. Método: **merge commit**, com **dois parents** — `b48db2c58b0348b40773baffcc60180cfdc06bb1` e o commit funcional `4749efa74d5684b52b4f457176710ba6e212c627` —, **sem squash, sem rebase e sem exclusão de branch**. Arquivos: **exclusivamente** `src/casa77_sdr/response_status.py` (**novo**, **+162 / −0**) e `tests/test_response_status.py` (**novo**, **+1093 / −0**) — **dois arquivos**, **1255 adições, 0 remoções**. Os **blobs integrados** são exatamente os **blobs staged auditados**: `ceeb24cca6356f55e835c9f594a18875fcb1d8db` para o módulo e `6028b883463cb8bdfb6839f4dfcd655b318f3d02` para o teste. **Sem CI remoto configurado** — `gh pr checks 97` reportou **ausência de checks**, o que é **ausência de CI, não falha de CI** —, e **zero review e zero comentário** na PR. **FUNCIONAL**: **passa a ser o marco funcional** da `main`, **sem numeração de subetapa**. **Não altera arquivo preexistente algum**, **não altera `knowledge/`, `docs/` nem `prompts/`**, **não altera `casa77_sdr/__init__.py`**, **não cria o índice**, **não implementa `hora`** e **não migra a autoridade de status** |
| Base da reconciliação **pós-PR #97** | `8c67e13808da59dbace413fce33c2c22280e69a3` — HEAD da `main` verificado **antes** desta reconciliação |
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
| **Reconciliação do estado após o PR #44** (`docs/00`): registra o marco funcional `2da532f1…` / merge `048a5483…`, o baseline **`749 passed`** → **`759 passed`**, as **quatro** entregas funcionais posteriores à 3B.7 então existentes e o registro dos PRs **#43** e **#44** | documental | PR #45 — **INTEGRADO à `main`** em 2026-08-21 (commit documental `650589190b30b82ac4f3b2e0a6fdf5547c732eec`, merge `81383038c0bd43a7c2e95e23c3edd57553379da5`, branch de origem `docs/reconciliar-estado-pos-pr44`). Arquivo alterado: **exclusivamente** `docs/00-estado-atual.md` — **1 file changed, 83 insertions(+), 59 deletions(-)**. **Zero código**, **zero teste** e **nenhum marco funcional novo** |
| **Microcorreção documental do item "Próxima ação"** (`docs/00`): remove a formulação obsoleta que ainda sugeria uma futura implementação do contrato arbitrado pelo **PR #42** e retira `transicoes_que_mudaram_estado` da lista de pendências, preservando **N-a-T3–T7**, **N-b**, **E4**, **S2-D8**, **S3-D1** e o `OrquestradorMotor` como exemplos ainda abertos | documental | PR #46 — **INTEGRADO à `main`** em 2026-08-21 (commit documental `cb2b39de255a6387ac5f080e3eba6e9d8ae0a966`, merge `4159fdafbfcf91fd7cb6892bc58df94c03cf96b0`, branch de origem `docs/corrigir-proxima-acao-pos-pr45`). Arquivo alterado: **exclusivamente** `docs/00-estado-atual.md` — **1 file changed, 7 insertions(+), 6 deletions(-)**. **Zero código**, **zero teste** e **nenhum marco funcional novo** |
| **Decisão determinística do marco temporal** (`src/casa77_sdr/transition_marker.py` + testes, com reconciliação factual de `docs/07`): cria a função pura `decidir_instante_ultima_transicao(...)`, com **quatro argumentos nomeados e obrigatórios**, que responde **somente** qual valor de `instante_ultima_transicao` o futuro chamador da etapa 13 deverá usar. Materializa a **composição decisória das 0–3 `DecisaoMaquina`** efetivamente produzidas no ciclo, decidindo **exclusivamente** por `transicoes_que_mudaram_estado`: **criação** → `instante_de_referencia_do_ciclo`; **atendimento existente com ao menos uma mudança** → `instante_de_referencia_do_ciclo`; **sem mudança** → **preserva** `marco_atual`, inclusive `None`. **Zero relógio vivo, zero conversão de fuso, zero aritmética temporal** — o valor devolvido é sempre **o mesmo objeto** recebido. **Zero persistência, zero I/O, zero rede, zero YAML, zero LLM**; não importa `persistence`, `context`, `eligibility` nem `identity`, e **não é exportada** na superfície pública do pacote. **Não implementa** a aplicação dessa decisão pela **etapa 13**, a **escrita** via `criar`/`gravar`, a montagem/gravação do `RegistroAtendimento`, a criação operacional, a **persistência não volátil** nem o **`OrquestradorMotor`** | **funcional** | PR #47 — **INTEGRADO à `main`** em 2026-08-21 (commit funcional `b2f9f74d5586c481bf6f2af63861d06cdb655d55`, merge `dd5a4cc76e70ab5c9b1ca640ecc2abcab46140a9`, branch de origem `feat/decisao-marco-transicao`, mensagem `feat: decide transition timestamp`). Arquivos: `docs/07-arquitetura-motor-respostas.md`, `src/casa77_sdr/transition_marker.py`, `tests/test_transition_marker.py` — **3 files changed, 602 insertions(+), 12 deletions(-)**. **Não recebe numeração de subetapa** |
| **Reconciliação do estado após o PR #47** (`docs/00`): registra o marco funcional `b2f9f74d…` / merge `dd5a4cc7…`, o baseline **`759 passed`** → **`795 passed`**, as **cinco** entregas funcionais posteriores à 3B.7 então existentes e o registro dos PRs **#46** e **#47** | documental | PR #48 — **INTEGRADO à `main`** em 2026-08-21 (commit documental `db9b202eeea95cbf249863a0cd4967627eae0156`, merge `5a059b4b7ba69e912c960bfa4d7a7990228a6792`, branch de origem `docs/reconciliar-estado-pos-pr47`). Alterou **exclusivamente** `docs/00-estado-atual.md` — **125 adições, 78 remoções**. **Não cria marco funcional novo** |
| **Aplicação e escrita do marco temporal como fronteira chamável** (`src/casa77_sdr/transition_marker_write.py` + testes, com reconciliação factual de `docs/07`): cria o módulo com `criar_com_marco_de_transicao(...)` e `gravar_com_marco_de_transicao(...)` — ambos com **argumentos exclusivamente nomeados e obrigatórios, sem default**. A fronteira **delega** integralmente a decisão a `decidir_instante_ultima_transicao(...)`, **aplica** o valor decidido sobre um `RegistroAtendimento` **recebido pronto** substituindo **somente** `instante_ultima_transicao` (por `dataclasses.replace`, sem mutar o registro recebido) e **escreve** pelo contrato existente `PersistenciaOperacional.criar(...)` ou `PersistenciaOperacional.gravar(...)`. A operação **chega pronta** à função chamada: `criar` chama **somente** `criar`, `gravar` chama **somente** `gravar`, e a fronteira **não deriva** criar × gravar de nada. **Zero leitura da persistência**, **zero idempotência**, **zero preservação de pendente**, **zero `try`/`except`** — exceções propagam intactas —, **zero relógio vivo**, **zero *replay***, **zero tipo/enum/dataclass novo** e **zero export em `__init__.py`**. `src/casa77_sdr/persistence.py` **permanece inalterado**. Documenta **M-AE1–M-AE7** em `docs/07` §6.2 | **funcional** | PR #49 — **INTEGRADO à `main`** em 2026-08-22 (commit funcional `d621a2c7252b4e758278e51af3617bb9d00a97b6`, merge `f82da69feb11ba3051fd595d02775171814f8f33`, branch de origem `feat/escrita-marco-transicao`) — **3 arquivos, 865 adições, 19 remoções**. **Cria o novo marco funcional.** **Não recebeu numeração de subetapa** |
| **Reconciliação do estado após o PR #49** (`docs/00`): registra o marco funcional `d621a2c7…` / merge `f82da69f…`, o baseline **`795 passed`** → **`847 passed`**, as **seis** entregas funcionais posteriores à 3B.7, a **fase RED esperada** do ciclo TDD e o registro dos PRs **#48** e **#49** | documental | PR #50 — **INTEGRADO à `main`** em 2026-08-22 (commit documental `5509a3f2e01a79cf52acde427794b1de4ec07ff1`, merge `60701aaaf7a85614e27cf3e95b6a25870769aee5`, branch de origem `docs/reconciliar-estado-pos-pr49`). Alterou **exclusivamente** `docs/00-estado-atual.md` — **217 adições, 120 remoções**. **Não cria marco funcional novo** |
| **Arbitragem documental N-b — contrato global da `Interpretacao` da etapa 4** (`docs/07` §4.1, §4.4, §5, §6.3, §7, §8.2, §9 e §12): fecha o contrato da **saída da etapa 4** preservando as **oito** categorias de §6.3; fixa **`IntencaoConversacional`** como vocabulário conceitual **fechado em 11 valores** na partição **A1 (6 derivados) / A2 (2 autônomos) / B (3 autônomos)**; fixa a **derivação determinística** para a `ProjecaoInterpretacao` (**N-b-K1–N-b-K8**), a **função total** da **condição 5** `interesse_confirmar_disponibilidade` (**N-b-CD1–N-b-CD4**), a **consistência cruzada** dos **seis pares de representação dupla** (**N-b-X1–N-b-X6**), as **regras de confiança** (**N-b-G6/G6b/G6c**), o **modo degradado** (**N-b-M1–N-b-M8**), a lista fechada de **erros de contrato E-Nb-1–E-Nb-19** e os **cenários K-Nb-1–K-Nb-40**; e designa a **fronteira conceitual do produtor de interpretação da etapa 4** (**N-b-F1–N-b-F5**) dentro do **limite único de LLM** já previsto em §4.2/§9. **Zero código, zero tipo Python, zero JSON Schema, zero biblioteca, zero fornecedor, zero modelo, zero SDK, zero API e zero formato de transporte.** §4.1 permanece com **14** componentes e §2 com **nove** responsabilidades | documental | PR #51 — **INTEGRADO à `main`** em 2026-08-22 (commit documental `6f1cb6fe5ef12096117f1292225a761af5889025`, merge `85dbc709799f30c59a458c3ea8725fc072a15364`, branch de origem `docs/arbitragem-nb-interpretacao`). Alterou **exclusivamente** `docs/07-arquitetura-motor-respostas.md` — **365 adições, 8 remoções**. **Não cria marco funcional novo** |
| **Reconciliação do estado após o PR #51** (`docs/00`): registra a integração do **PR #51** — arbitragem documental **N-b** —, preserva o marco funcional do **PR #49** (`d621a2c7…` / `f82da69f…`), o baseline **`847 passed`** / **Python 3.14.5** e a **3B.7** como última subetapa numerada, e registra **N-b**, **àquela altura**, como **ARBITRADA DOCUMENTALMENTE / NÃO IMPLEMENTADA** — situação superada depois pelo **PR #55** | documental | PR #52 — **INTEGRADO à `main`** em 2026-08-22 (commit documental `f3fafee09b7d6bad464134fd9d20d603ebbb0122`, merge `cc7f4493b97935ef92efe2e821d7a032d16db1a4`, branch de origem `docs/reconciliar-estado-pos-pr51`). Alterou **exclusivamente** `docs/00-estado-atual.md` — **148 adições, 40 remoções**. **Zero código**, **zero teste** e **nenhum marco funcional novo** |
| **Micro-arbitragem documental AJ1 — representação e canonicalização determinística de N-b** (`docs/07` §6.3, §8.2 e §12): fecha a **representação/canonicalização** da `Interpretacao` **antes** de qualquer materialização em código. Fixa que **`A1` não é entrada semântica independente** do produtor não determinístico — presença **derivada** do payload autoritativo e confiança **calculada** por **N-b-X3**, podendo ser **armazenada para auditabilidade** sem ser **declarada**; delimita o **slot de intenções autônomas** aos **cinco** códigos **A2/B**; fixa a **precedência `E-Nb-3` × `E-Nb-5`** para tentativa de apresentar código **A1** nesse slot; **classifica** os **19** erros em **recebíveis/runtime**, **invariantes internos da canonicalização** e **invariante estrutural do módulo** (`E-Nb-19`); fixa `E-Nb-13` como **invariante/program error** e o **alcance de prova** de **K-Nb-18** (estrutural), **K-Nb-34** (recebível) e **K-Nb-39** (parcialmente local, parcialmente dependente de orquestração); registra a **estratégia estrutural** de prova de `E-Nb-19`; **preserva** a **condição 5**, cujo produtor **já estava conceitualmente atribuído** por N-b; e autoriza, **apenas como decisão para a futura materialização**, a **reutilização por import** de `FormatoEvento` de `qualification.py`. **Zero código, zero teste, zero JSON Schema, zero fornecedor, modelo, SDK ou API.** `IntencaoConversacional` permanece com **11** valores, os erros com **19** códigos, os cenários com **40**, §4.1 com **14** componentes e §2 com **nove** responsabilidades | arbitragem documental/governança | PR #53 — **INTEGRADO à `main`** em 2026-08-23 (commit documental `d1137cf67c42eae37ec8e837a56350da6c7fbabe`, merge `2e9df1f4dfcd11903d410ba7a42ba12d86eb2b15`, branch de origem `docs/nb-aj1-canonicalizacao`). Alterou **exclusivamente** `docs/07-arquitetura-motor-respostas.md` — **156 adições, 1 remoção**. **Zero código**, **zero teste** e **nenhum marco funcional novo**: **AJ1 não implementou N-b**. O contrato ali fechado foi **materializado depois**, **parcialmente**, pelo **PR #55** |
| **Reconciliação do estado após o PR #53** (`docs/00`): registra os **PRs #52 e #53** como integrados e documentais, corrige a formulação sobre `N-b-RES1`–`N-b-RES3` — `N-b-RES1` como regra fechada, `N-b-RES2` como residual **aberto** e `N-b-RES3` como classificação fechada — e preserva, **àquela altura**, o marco funcional do **PR #49**, o baseline **`847 passed`** / **Python 3.14.5** e a **3B.7** como última subetapa numerada | documental | PR #54 — **INTEGRADO à `main`** em 2026-08-23 (commit documental `0f67e7f4e9218ae9f8b56eca253d6e57147dfd03`, merge `3740a121c00631e2c60e71b99724e66cac12d11b`, branch de origem `docs/reconciliar-estado-pos-pr53`). Alterou **exclusivamente** `docs/00-estado-atual.md` — **170 adições, 37 remoções**. **Zero código**, **zero teste** e **nenhum marco funcional novo** |
| **Materialização da parte determinística de N-b** (`src/casa77_sdr/interpretation.py` + testes, com registro factual em `docs/07` §6.3 e §12): materializa a **fronteira determinística** da interpretação da etapa 4. Cria a entrada **pré-canônica** `EntradaInterpretacao` — que **não possui slot de códigos `A1`** —, a **`Interpretacao` canônica** e o vocabulário **`IntencaoConversacional` com exatamente 11 valores**; **deriva** os seis códigos **A1** dos payloads autoritativos e **calcula** sua confiança por **N-b-X3**, apenas **armazenando-a** para auditabilidade; implementa `canonicalizar_interpretacao(...)`, `projetar_para_identidade(...)` — projeção total para a `ProjecaoInterpretacao` **já existente**, de **sete** campos — e `decidir_interesse_confirmar_disponibilidade(...)`, a **condição 5** de `docs/07` §4.4 como **função total**; valida os **erros recebíveis `E-Nb`** com a precedência **`E-Nb-3` × `E-Nb-5`**, verifica os **invariantes internos `E-Nb-11`–`E-Nb-16`** como pós-condições e prova **`E-Nb-19`** estruturalmente; exige **canonicidade** também de uma `Interpretacao` construída diretamente; e **reutiliza `FormatoEvento` por import** de `qualification.py`, que **permanece inalterado**. **Zero LLM, fornecedor, modelo, SDK, API, JSON Schema, formato de transporte, interpretação de texto livre ou produção de `Exx`.** `docs/07` §4.1 permanece com **14** componentes e §2 com **nove** responsabilidades | **funcional** | PR #55 — **INTEGRADO à `main`** em 2026-08-23 (commit funcional `3f24e216f3770ce4ce76270d3d3e6115132c91ad`, merge `ba412502124bac3ce3f38554f81c265ed739672b`, branch de origem `feat/nb-interpretation-canonicalization`, mensagem `feat: materialize deterministic N-b interpretation`). Arquivos: `docs/07-arquitetura-motor-respostas.md` (**+21 / −1**), `src/casa77_sdr/interpretation.py` (**+1010**), `tests/test_interpretation.py` (**+2098**) — **3 files changed, 3129 insertions(+), 1 deletion(-)**. Baseline **`847 passed`** → **`1167 passed`**. **Cria o novo marco funcional.** **Não recebe numeração de subetapa** |
| **Materialização funcional do delta AJ2** (`src/casa77_sdr/interpretation.py` + testes, com registro factual em `docs/07` §6.3 e §12): materializa o **assunto** de `PerguntaComercial` na **fronteira determinística** da etapa 4. Cria **`AssuntoComercial`** — vocabulário fechado de **54** membros, **53 específicos + `ASSUNTO_NAO_CLASSIFICADO`**, na ordem documental —; evolui **`PerguntaComercial` para três campos** (`texto`, `confianca`, **`assunto`**), com o assunto **obrigatório** e **sem confiança própria**; **amplia `E-Nb-5`** para assunto **ausente** e **fora do vocabulário**, mantendo **`TypeError` sem código** para tipo runtime incompatível; valida o assunto nos **dois caminhos** — canonicalização e `Interpretacao` construída diretamente — **depois** das validações N-b/AJ1 preexistentes, **preservando a precedência histórica**; e cobre os cenários **`K-Nb-41`–`K-Nb-51`**. **Preserva** a projeção de **sete** campos, as **11** `IntencaoConversacional`, **N-b-X3**, a **condição 5** como única condição de §4.4 materializada e a lista **`E-Nb-1`–`E-Nb-19`**. **Não** implementa produtor LLM, **não** interpreta texto livre, **não** segmenta consulta composta, **não** materializa **C** nem **S2-D8**, **não** fecha **`N-b-RES2`** e **não** integra a etapa 4. **Sem numeração de subetapa — a 3B.8 não existe** | **funcional** | **PR #61** — commit funcional `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`, merge `5a722a5cc648149330362434694e7e76a40c1b57`, branch de origem `feat/materializar-aj2-assunto`. **Três** arquivos — `src/casa77_sdr/interpretation.py`, `tests/test_interpretation.py` e `docs/07-arquitetura-motor-respostas.md` —, **762 adições / 28 remoções**. Baseline **`1215 passed`** / Python 3.14.5 |
| **`E1` — validador estrutural do futuro índice de respostas aprovadas** (`src/casa77_sdr/response_index.py` + `tests/test_response_index.py`): **primeira microentrega funcional de `C`**. Materializa **exclusivamente** a validação estrutural **fail-closed** da forma de uma estrutura já parseada que pretende ser `knowledge/indice-respostas-aprovadas.yaml`. Expõe **`IndiceInvalido`** e **`validar_indice(indice: object) -> None`**; implementa **schema estrutural fechado**, **vocabulários fechados** de status, mecanismo, origem, formato, predicado e fato runtime, **exclusividade `YAML` × `RUNTIME_AUTORITATIVO`**, **`RUNTIME_AUTORITATIVO` somente com `ASSERTIVA`**, as **regras estruturais de `RENDERIZADO`** (*placeholder* + formato) e de **`ASSERTIVA`** (predicado), **fail-closed na primeira violação** — a mensagem carrega **categoria e localizador** e **não ecoa o valor recebido** —, a **rejeição de seleção numericamente posicional** e a **proteção contra índices posicionais mesmo após seletores textuais encadeados**. O módulo **não abre arquivo, não importa carregador e não lê `knowledge/**`**. **Não** cria o índice real, **não** cria loader, **não** converte o Markdown, **não** materializa *bindings* reais, **não** executa a bijeção 37/37, **não** implementa **C-15**, **não** renderiza, **não** aplica formatos, **não** avalia `ASSERTIVA` contra dados reais, **não** materializa **R2** nem **S2-D8**, **não** fecha **`N-b-RES2`**, **não** implementa o **`OrquestradorMotor`**, **não** escolhe calendário e **não** implementa LLM. **`E1` materializada NÃO é `C` materializada.** **Sem numeração de subetapa — a 3B.8 não existe** | **funcional** | **PR #84** — commit funcional `02f1dd6621c31b90789c646bd8826e685f9ee019`, merge `95ed2ce4e9c54f9bdfb7b3f820e6f9e065cde24e`, branch de origem `feat/c-e1-response-index-validator`. **Dois** arquivos novos — `src/casa77_sdr/response_index.py` e `tests/test_response_index.py` —, **1343 adições / 0 remoções**. Baseline **`1374 passed`** / Python 3.14.5, com **`159 passed`** no direcionado |
| **Segunda microentrega funcional de `C` — carregador *fail-closed* do futuro índice** (`src/casa77_sdr/response_index_load.py` + `tests/test_response_index_load.py`, com correção localizada em `tests/test_response_index.py`): torna o validador estrutural já integrado **alcançável a partir de um artefato YAML explicitamente informado**, **sem criar o índice real**. Expõe **`IndiceIlegivel`** e **`carregar_indice(path: str | Path)`** — fronteira pública única, com **caminho sempre explícito**, **sem caminho padrão, descoberta, glob ou variável de ambiente**. Lê **somente em UTF-8** e **somente para leitura**; analisa com **`yaml.SafeLoader`** por subclasse privada que **altera apenas a construção de mapeamento**, **sem registrar construtor, ampliar tag ou relaxar restrição de segurança**; **recusa chave YAML duplicada** *fail-closed*, **por mapeamento** e em **qualquer nível**. Fecha a **taxonomia de ilegibilidade** em **`arquivo_ausente`**, **`leitura_falhou`**, **`codificacao_invalida`**, **`sintaxe_invalida`** e **`chave_duplicada`**, com mensagem de **categoria e caminho** que **nunca ecoa o conteúdo do arquivo** — o texto bruto do analisador fica **apenas** em **`__cause__`**. **Separa estritamente artefato ilegível de estrutura inválida**: toda a forma é **delegada integralmente** a `validar_indice(...)`, e **`IndiceInvalido` propaga intacta**, sem captura, reembalagem, tradução de categoria ou duplicação de regra — raiz `None`, lista ou escalar chega ao validador e é rejeitada por **E1**. **Zero normalização, zero valor padrão e zero *fallback*** depois da análise. **Também remove** o teste `test_indice_real_continua_inexistente` de `tests/test_response_index.py`, porque a inexistência do índice era **evidência temporária** da E1 e **não invariante permanente** — a remoção **não cria o índice**. **Não** cria o índice real, **não** converte o Markdown, **não** materializa *templates* ou *bindings* físicos, **não** executa a bijeção 37/37, **não** implementa **C-15**, **não** renderiza, **não** aplica formatos, **não** avalia `ASSERTIVA` contra dados reais, **não** materializa **R2** nem **S2-D8**, **não** fecha **`N-b-RES2`**, **não** implementa o **`OrquestradorMotor`**, **não** escolhe calendário e **não** implementa LLM. **Carregar não é materializar `C`.** **Sem nomenclatura normativa `E2` e sem numeração de subetapa — a 3B.8 não existe** | **funcional** | **PR #86** — commit funcional `b2b11e2465c7f332747a806c80b629e995f0f5a6`, merge `9bf68b8fece9ea66c74509490ddf6e02a0aa6f31`, branch de origem `feat/c-response-index-loader`. **Três** arquivos — dois novos e um modificado —, **1086 adições / 5 remoções**. Baseline **`1436 passed`** / Python 3.14.5, com **`63 passed`** no direcionado do carregador e **`158 passed`** no de `E1` |
| **Terceira microentrega funcional de `C` — comparador determinístico de equivalência textual de `C-15b`** (`src/casa77_sdr/response_equivalence.py` + `tests/test_response_equivalence.py`): materializa o **julgamento de equivalência** de `C-15b` sobre **duas `str` já em representação canônica** — o fragmento aprovado já extraído e a renderização textual do mesmo fragmento (D1) —, mantendo o **fragmento inteiro** como unidade (`C-15c`, `C-A4-P1`). Expõe **`EquivalenciaNaoDeterminavel`** e **`sao_textualmente_equivalentes(aprovado: str, renderizado: str) -> bool`**. Tipo não-`str` produz **`TypeError`** — erro de contrato de chamada, verificado **antes** da canonicidade. Violação mecanicamente detectável da representação produz **`EquivalenciaNaoDeterminavel`**, que **NÃO é `False`** (D6-A): o chamador **deve parar ou escalar**. Valida **`aprovado` antes de `renderizado`**, **encerra na primeira violação** e **não acumula** erros. Normaliza com **NFC antes da dobra**; converte **`LF` isolado em exatamente um `U+0020`** (D3); **preserva `\n\n` literalmente** como fronteira de parágrafo real (D4); **recusa três ou mais `LF`**; **recusa `CR`, `CRLF`, `U+2028`, `U+2029`, `U+0085`, `U+000B` e `U+000C`**, **sem converter `CRLF`** (D5); **recusa `LF` de borda** e **branco adjacente a `LF`** (D7); e compara por **igualdade exata**, **sem `strip`, sem `casefold`, sem *fuzzy* e sem transformação semântica**. A **`str` vazia permanece canônica**. As **categorias técnicas** são privadas e fechadas — `terminador_proibido`, `quebra_na_borda`, `sequencia_de_quebras_excessiva` e `branco_adjacente_a_quebra` —, **não** são identificadores normativos de `C`, e a mensagem carrega **categoria e lado**, com localizador quando aplicável, **nunca** o texto recebido, o caractere ofensor, deslocamento, índice ou comprimento, e **sem `__cause__`**. **Pureza**: o módulo importa **apenas** `__future__` e `unicodedata` — **zero I/O**, **zero *filesystem***, **zero YAML**, **zero leitura de `knowledge/**`**, **zero analisador de Markdown**, **zero dependência de `response_index` ou `response_index_load`** — e **não é exportado** por `casa77_sdr/__init__.py`. **Não** cria o índice real, **não** cria analisador ou extrator de Markdown, **não** cria *template*, *placeholder* ou *binding* físico, **não** cria *renderer*, **não** aplica formatos, **não** integra consumidor, **não** executa a bijeção física 37/37, **não** migra autoridade de status, **não** materializa **R2** nem **S2-D8**, **não** fecha **`N-b-RES2`**, **não** implementa o **`OrquestradorMotor`**, **não** escolhe calendário e **não** implementa LLM. **COMPARAR NÃO É MATERIALIZAR `C`.** **Sem nomenclatura normativa `E2` ou `E3` e sem numeração de subetapa — a 3B.8 não existe** | **funcional** | **PR #89** — commit funcional `23e3fa727eb1457cd98a0e0e6f36580dade2ab00`, merge `76531de7d3f4257d84b5a1f9498d8666c4e60030`, branch de origem `feat/c-response-equivalence`. **Dois** arquivos novos, **965 adições / 0 remoções**, **nenhum arquivo preexistente alterado**. Baseline **`1589 passed`** / Python 3.14.5, com **`153 passed`** no direcionado; **`153`** e **`1589`** também sob `-W error` |
| **Quarta microentrega funcional de `C` — formatadores determinísticos de apresentação pura de `C-6`** (`src/casa77_sdr/response_format.py` + `tests/test_response_format.py`): materializa **cinco** dos seis formatos do vocabulário fechado de **`C-6`** como **funções puras** sobre valores **já resolvidos**, aplicando os refinamentos de **`C-A1-F`**, **`C-A1-L`**, **`C-A4-F1`** e **`C-A4-F2`**. Expõe **`FormatoInaplicavel`**, **`formatar_inteiro`**, **`formatar_inteiro_agrupado`**, **`formatar_simbolo_moeda`**, **`formatar_texto`** e **`formatar_lista`** — **`__all__` com exatamente seis nomes**, **um parâmetro por função** e **sem default**. **`inteiro`**: decimal do **mesmo** inteiro, **`int` estrito**, **`bool` recusado** por ser subclasse de `int`, **sem coerção** de `float`, `Decimal` ou texto numérico, **sem agrupar, sem arredondar e sem zero acrescentado**. **`inteiro_agrupado`**: agrupamento **da direita para a esquerda**, grupos de **três dígitos**, separador **`.`**, **sem casa decimal, sem arredondamento, sem cálculo, sem zero para completar grupo**, sinal **preservado e não agrupado**, **sem *locale*** e **sem delegar ao `format` da linguagem**. **`simbolo_moeda`**: **tabela fechada** de **um único código**, devolvendo **somente o símbolo**, **sem whitespace**, **sem `upper`, sem `strip` e sem tolerância de caixa**; código não suportado **FALHA** e a moeda **nunca é inferida**. **`texto`**: **identidade exata**, devolvendo **a mesma `str`**, **sem NFC, `strip`, `casefold`, colapso de espaço, dobra de quebra ou ajuste de pontuação**. **`lista`**: **zero itens FALHA**; um item; dois unidos por ` e `; três ou mais com `, ` e ` e ` final; **ordem, cardinalidade e conteúdo literal preservados**, **item vazio NÃO filtrado**, **`str` não é contêiner válido** e a **entrada não é mutada**. **Categorias técnicas privadas e fechadas** — `tipo_invalido` e `valor_invalido` —, **localizadores fechados** — `valor`, `codigo`, `itens`, `itens.item` —, **fail-closed na primeira violação**, mensagem que **nunca ecoa o recebido**, **sem `__cause__`** e **sem `__context__`**. **Pureza**: o módulo importa **apenas** `__future__` e `collections.abc` — **zero I/O**, **zero *filesystem***, **zero YAML**, **zero *locale***, **zero rede**, **zero leitura de `knowledge/**`**, **zero dependência de `casa77_sdr.*`** — e **não é exportado** por `casa77_sdr/__init__.py`. **O formato `hora` NÃO é implementado**: `C-A1-F3` fixa `HH:MM` e `Hh`, mas **não existe regra arbitrada** que escolha mecanicamente entre eles — escolher seria arbitrar, e a lacuna permanece **aberta**. **Não** cria o índice real, **não** cria extrator de Markdown, **não** cria *template*, *placeholder* ou *binding* físico, **não** cria *renderer*, **não** avalia `ASSERTIVA`, **não** executa a bijeção física 37/37, **não** integra consumidor, **não** migra autoridade de status, **não** materializa **R2** nem **S2-D8**, **não** fecha **`N-b-RES2`**, **não** implementa o **`OrquestradorMotor`**, **não** escolhe calendário e **não** implementa LLM. **FORMATAR NÃO É MATERIALIZAR `C`.** **Sem nomenclatura normativa `E2`, `E3` ou `E4` e sem numeração de subetapa — a 3B.8 não existe** | **funcional** | **PR #91** — commit funcional `7d8dd8617eb5cd8c346e67496c3631feafe97f4f`, merge `d15201b0a84bca332b09e0d5e623736605663962`, branch de origem `feat/c-response-formatters`. **Dois** arquivos novos, **1367 adições / 0 remoções**, **nenhum arquivo preexistente alterado**. Baseline **`1908 passed`** / Python 3.14.5, com **`319 passed`** no direcionado; **`319`** e **`1908`** também sob `-W error` |
| **Quinta microentrega funcional de `C` — avaliador determinístico booleano de `ASSERTIVA` sobre valor já resolvido** (`src/casa77_sdr/response_assertion.py` + `tests/test_response_assertion.py`): materializa **somente o julgamento** de uma `ASSERTIVA` — que permanece **consistency-only** (**C-5i**–**C-5q**, **C-A2-NR7**) — sobre um **predicado já disponibilizado pelo chamador** e um **valor já resolvido**. Expõe **`AssertivaNaoAvaliavel`** e **`avaliar_assertiva(predicado: str, valor: object) -> bool`**, com **`__all__` de exatamente dois nomes**, **dois parâmetros**, **sem default** e **sem parâmetro de configuração**. **Predicados**: o vocabulário fechado **`EH_VERDADEIRO`** / **`EH_FALSO`**, **sem terceiro** (**C-5g**, **C-5h**, **C-A1-R**); predicado não-`str` ou fora do vocabulário é **fail-closed**, **sem `upper`**, **sem `strip`** e **sem tolerância de caixa**. **Domínio materializado**: **apenas `bool` estrito** — os **quatro** casos avaliáveis são `EH_VERDADEIRO` com `True`/`False` e `EH_FALSO` com `False`/`True`. **Qualquer valor não booleano é NÃO AVALIÁVEL** e levanta `AssertivaNaoAvaliavel`: **`0` não é `False`**, **`1` não é `True`**, e o valor **nunca vira assertiva falsa**; **sem *truthiness***, **sem `bool(...)`**, **sem coerção**, **sem *parsing***, **sem normalização** e **sem *fallback*** — `__bool__` e `__eq__` customizados **não** são consultados, porque a decisão é **por tipo**, nunca por igualdade permissiva. Essa recusa é **delimitação técnica fail-closed desta microentrega**, e **não** expansão normativa de **`C-7`**, que trata especificamente de `null` e `pendente`. **Precedência fixa**: tipo do predicado → valor do predicado → domínio do valor → avaliação, com a **primeira violação encerrando** e **nada acumulado** (**P5**). **Categorias técnicas privadas e fechadas** — `tipo_invalido` e `valor_invalido` —, **localizadores fechados** — `predicado` e `valor` —, mensagem `<categoria>: <localizador>` que **nunca ecoa** predicado, valor, tipo concreto, `repr`, conteúdo, índice ou tamanho, **sem `__cause__`** e **sem `__context__`**. **Pureza**: o módulo importa **apenas** `__future__` — **zero I/O**, **zero *filesystem***, **zero YAML**, **zero *locale***, **zero rede**, **zero LLM**, **zero calendário**, **zero relógio**, **zero variável de ambiente**, **zero leitura de `knowledge/**`** e **zero dependência de `casa77_sdr.*`** — e **não é exportado** por `casa77_sdr/__init__.py`. **Não** resolve referente, **não** lê `caminho_yaml`, **não** conhece origem do fato nem fato de runtime, **não** cria o índice real, **não** cria extrator de Markdown, **não** cria *template*, *placeholder* ou *binding* físico, **não** cria *renderer*, **não** formata, **não** compara texto, **não** executa a bijeção física 37/37, **não** migra autoridade de status, **não** integra consumidor, **não** decide candidatura, disponibilidade, handoff ou `E09` (**C-12**, **C-A2-ESC10**), **não** materializa **R2** nem **S2-D8**, **não** fecha **`N-b-RES2`**, **não** implementa o **`OrquestradorMotor`** e **não** implementa LLM. **Esta entrega NÃO declara que todo domínio futuro de `ASSERTIVA` seja booleano**: nenhum outro domínio é inferido, e **ampliar a avaliação exigiria contrato posterior explícito**. **AVALIAR `ASSERTIVA` NÃO É MATERIALIZAR `C`.** **Sem nomenclatura normativa `E2`, `E3`, `E4` ou `E5` e sem numeração de subetapa — a 3B.8 não existe** | **funcional** | **PR #93** — commit funcional `efa903816b5dc1dafbce8161f6424abdf41f2ca6`, merge `353e1b42d6c8b31d649f59b151184811ef51462e`, branch de origem `feat/c-response-assertion`. **Dois** arquivos novos, **948 adições / 0 remoções**, **nenhum arquivo preexistente alterado**. Baseline **`2162 passed`** / Python 3.14.5, com **`254 passed`** no direcionado; **`254`** e **`2162`** também sob `-W error` |
| **Sexta microentrega funcional de `C` — verificador determinístico da correspondência bijetiva de `C-A1-B3` / `C-A1-B4` sobre domínios já fornecidos pelo chamador** (`src/casa77_sdr/response_bijection.py` + `tests/test_response_bijection.py`): materializa **somente a verificação** de que uma relação recebida é **bijetiva entre os dois domínios recebidos** — `C-A1-B3` (cada fragmento do índice ↔ exatamente uma unidade emitível) e `C-A1-B4` (a recíproca) —, com a unidade permanecendo o **fragmento emitível** (`C-A1-B1`) e notas/instruções internas **fora da bijeção** (`C-A1-B2`). Expõe **`BijecaoInvalida`** e **`validar_bijecao(fragmentos_indice, unidades_markdown, correspondencias) -> None`**, com **`__all__` de exatamente dois nomes**, **três parâmetros**, **sem default** e **sem parâmetro de configuração**. **Os três domínios chegam prontos.** **Tokens opacos**: fragmentos e unidades são `str` **não interpretadas**, comparadas por **igualdade nativa exata de `str`** — **sem `strip`, `casefold`, `lower`, `upper`, `NFC` ou normalização alguma**; duas representações Unicode distintas do mesmo texto são **tokens distintos**. **Token é `str` exata**: **subclasse de `str` é recusada** nos dois domínios e nos dois lados de cada par. **Cada item da relação é `tuple` exata de exatamente dois lados**: **subclasse de `tuple` recusada**, `list` de dois elementos recusada, `Mapping` recusado como relação; `str`, `bytes` e `bytearray` **não** são contêineres válidos. **Zero normalização, zero coerção, zero *parsing*, zero I/O**; entradas **não alteradas**. **Validação fail-closed com precedência fixa** — tipo dos três argumentos → tokens de `fragmentos_indice` → tokens de `unidades_markdown` → tipo e forma dos itens → tipo de origem e destino → duplicidade nos domínios → origem e destino repetidos → origem e destino desconhecidos → fragmento e unidade sem par —, cada etapa percorrendo **toda** a entrada antes da seguinte, a **primeira violação encerrando** e **nada acumulado** (**P5**). **Cinco categorias técnicas privadas e fechadas** — `tipo_invalido`, `estrutura_invalida`, `duplicidade`, `referencia_desconhecida`, `cobertura_incompleta` — e **seis localizadores fechados** — `fragmentos_indice`, `unidades_markdown`, `correspondencias`, `correspondencias.item`, `correspondencias.origem`, `correspondencias.destino` —, nenhum deles identificador normativo de `C`; mensagem `<categoria>: <localizador>` que **nunca ecoa** token, conteúdo, `repr`, tipo concreto, índice, tamanho ou cardinalidade, **sem `__cause__`** e **sem `__context__`**. **Três domínios vazios são bijeção trivial válida somente sobre os domínios fornecidos.** **Pureza**: o módulo importa **apenas** `__future__` e `collections.abc.Sequence` — **zero I/O**, **zero *filesystem***, **zero YAML**, **zero *locale***, **zero rede**, **zero LLM**, **zero calendário**, **zero relógio**, **zero variável de ambiente**, **zero leitura de `knowledge/**`** e **zero dependência de `casa77_sdr.*`** — e **não é exportado** por `casa77_sdr/__init__.py`. **Limite da garantia**: sucesso significa **somente** que a relação fornecida é bijetiva sobre os domínios fornecidos; **a completude correta dos dois domínios é pré-condição do chamador** e **não é verificável nesta fronteira** sem transformá-la em extrator. **Não** extrai fragmentos do índice, **não** extrai unidades do Markdown, **não** decide o que é unidade emitível, **não** define identidade física de fragmento, **não** cria identificadores, **não** lê índice real, **não** prova completude dos domínios, **não** executa a bijeção física do corpus real, **não** satisfaz `C-A1-ST7` isoladamente, **não** migra autoridade de status (`C-A1-ST6`–`C-A1-ST10`), **não** integra consumidor, **não** materializa **R2** nem **S2-D8**, **não** fecha **`N-b-RES2`**, **não** implementa o **`OrquestradorMotor`** e **não** implementa LLM. **VERIFICAR A BIJEÇÃO NÃO É MATERIALIZAR `C`.** **Sem nomenclatura normativa `E2`, `E3`, `E4`, `E5` ou `E6` e sem numeração de subetapa — a 3B.8 não existe** | **funcional** | **PR #95** — commit funcional `bdd0b2acc415ab6307c7c8da2adbad15f42cb75f`, merge `b06c0a43bd2f96b8712638e99c55edfe2fb2f99f`, branch de origem `feat/c-response-bijection`. **Dois** arquivos novos, **1472 adições / 0 remoções**, **nenhum arquivo preexistente alterado**. Baseline **`2446 passed`** / Python 3.14.5, com **`284 passed`** no direcionado; **`284`** e **`2446`** também sob `-W error` — **medidas após o merge** e **reexecutadas nesta reconciliação** |
| **Sétima microentrega funcional de `C` — canonicalizador determinístico de rótulo de status já extraído** (`src/casa77_sdr/response_status.py` + `tests/test_response_status.py`): materializa **somente a tradução** de um **rótulo de status do Markdown já extraído** para o status canônico de **`C-3`**, restrita às **três linhas com tradução automática arbitrada** em `C-A1-ST1`–`C-A1-ST3` — `APROVADO` → `APROVADO`; `AGUARDA APROVAÇÃO` → `AGUARDA_APROVACAO`; `APROVADO com handoff obrigatório` → `APROVADO`, com o **sufixo de handoff NÃO transportado** (C-2f, C-5.1). Expõe **`StatusNaoCanonicalizavel`** e **`canonicalizar_status(rotulo: str) -> str`**, com **`__all__` de exatamente dois nomes**, **um parâmetro**, **sem default** e **sem parâmetro de contexto, origem, modo, tolerância, fragmento, `Rxx`, configuração ou normalização**; a exceção deriva **diretamente de `Exception`**. **O rótulo chega já extraído** — **a origem correta do rótulo é pré-condição do chamador**, não verificável nesta fronteira sem transformá-la em extrator. **Tipo `str` exata**: **subclasse de `str` é recusada antes de qualquer consulta à tabela**, porque poderia redefinir `__eq__`/`__hash__` e decidir sozinha a pertença; **sem `str(...)`, sem `repr`, sem coerção**. **Comparação literal**: **sem `strip`, `lower`, `upper`, `casefold`, `NFC`, `NFD`, `unicodedata`, colapso de espaços, substituição de espaço inquebrável, tolerância de acento ou de caixa** — variantes de caixa, espaçamento, forma decomposta ou espaço inquebrável são **rótulos distintos** e são recusadas. **Precedência fixa** tipo → pertença → retorno, com a **primeira violação encerrando** e **nada acumulado** (**P5**). **Duas categorias técnicas privadas e fechadas** — `tipo_invalido` e `rotulo_nao_mapeado` —, **localizador único** `rotulo`, mensagem `<categoria>: <localizador>` que **nunca ecoa** rótulo, conteúdo, `repr`, tipo concreto, comprimento ou índice, **sem `__cause__`** e **sem `__context__`**. **Tabela privada imutável** (`tuple` de três pares), **fora de `__all__`**, **sem estado mutável de módulo**, com **entrada não alterada** e **resultado determinístico** sob repetição, ordem e ambiente. **Pureza**: importa **apenas** `__future__` — **zero I/O**, **zero *filesystem***, **zero YAML**, **zero *locale***, **zero rede**, **zero LLM**, **zero relógio**, **zero calendário**, **zero variável de ambiente**, **zero leitura de `knowledge/**`**, **zero dependência de `casa77_sdr.*`** — e **não é exportado** por `casa77_sdr/__init__.py`. **`PARCIAL` NÃO é traduzido automaticamente** e **continua exigindo mapeamento explícito no nível dos fragmentos emitíveis** (**C-A1-ST4**); **`BLOQUEADO` NÃO recebeu mapeamento inventado** — **C-A1-ST5** trata de `BLOQUEADO` **em nota interna**, que **não cria fragmento** e **não cria status**, e esta fronteira não recebe esse contexto. A categoria `rotulo_nao_mapeado` significa **"não há tradução automática nesta fronteira"**, jamais **"não arbitrado"**. **Não** extrai rótulo do Markdown, **não** extrai fragmento, **não** decide emissibilidade, **não** cria identidade física de fragmento, **não** cria nem lê o índice real, **não** resolve *bindings*, **não** executa a bijeção física, **não** prova completude do corpus, **não** satisfaz **`C-A1-ST6`–`C-A1-ST10`**, **não** migra a autoridade de status, **não** integra consumidor, **não** materializa **R2** nem **S2-D8**, **não** fecha **`N-b-RES2`**, **não** implementa o **`OrquestradorMotor`** e **não** implementa LLM. **CANONICALIZAR STATUS NÃO É MATERIALIZAR `C`**; `knowledge/respostas-aprovadas.md` **continua a autoridade de status** (**C-11**). **Sem nomenclatura normativa `E2`–`E7` e sem numeração de subetapa — a 3B.8 não existe** | **funcional** | **PR #97** — commit funcional `4749efa74d5684b52b4f457176710ba6e212c627`, merge `8c67e13808da59dbace413fce33c2c22280e69a3`, branch de origem `feat/c-response-status`. **Dois** arquivos novos, **1255 adições / 0 remoções**, **nenhum arquivo preexistente alterado**. Baseline **`2707 passed`** / Python 3.14.5, com **`261 passed`** no direcionado; **`261`** e **`2707`** também sob `-W error` — **medidas sobre a `main` integrada após o merge** e **reexecutadas nesta reconciliação** |
| **Oitava microentrega funcional de `C` — leitor/validador determinístico da representação marcada `C-A5`** (`src/casa77_sdr/response_markdown_units.py` + `tests/test_response_markdown_units.py`): materializa **somente a leitura das identidades** da representação marcada — a função pura `ler_unidades_marcadas(texto: str) -> tuple[str, ...]` recebe Markdown **já em memória** e devolve **exclusivamente** os tokens canônicos `<Rxx>/<id>` de **`C-A5-T1`**, em **ordem física do documento**, **derivados e nunca armazenados** (**`C-A5-T5`**). Valida a representação física de **`C-A5-U1`**–**`C-A5-U3`** e **`C-A5-I1`**–**`C-A5-I4`**, com **política de linha local** (`LF` e `CRLF` equivalentes, **sem `splitlines()`** e **sem *universal newline***), **delimitação ATX deliberadamente parcial** (**sem `Setext`, *code fence*, bloco `HTML` ou código indentado**), **envelope de marcador em dois estágios** e **gramática fechada do `id`**. Cobre as **sete redações fail-closed de `C-A5-X1`** por **seis categorias estruturais privadas** — `marcador órfão` e `marcador sem bloco imediatamente seguinte` são **mecanicamente indistinguíveis** nesta fronteira e compartilham `marcador_sem_bloco` — mais `tipo_invalido`; **nenhuma oitava falha foi criada**. **Bloco de citação fora de `## Rxx` é ignorado inteiro** por estar fora do domínio de **`C-A5-U2`**; **dentro de `Rxx` o bloco sem marcador válido é fail-closed**, e **marcador válido fora de `Rxx` também**. **Não garante unicidade global dos tokens** — não verifica a unicidade física das seções `## Rxx` — e **não prova historicamente `C-A5-I6`**. **Zero I/O, zero `pathlib`, zero YAML, zero rede, zero LLM, zero relógio, zero *locale*, zero ambiente, zero banco, zero import de `casa77_sdr.*` e zero export em `__init__.py`.** **Não extrai texto emitível, não lê nem propaga status, não mapeia `PARCIAL`, não cria nem lê índice, não resolve *binding*, não executa a bijeção física e não migra autoridade de status.** **LER A REPRESENTAÇÃO MARCADA NÃO É MATERIALIZAR `C`** | **funcional** | PR #102 — **INTEGRADO à `main`** em 2026-09-04 (commit funcional `341084d951b428d80c4ba573fbc38a4bc9f008c6`, merge `067e894db8bddb96c192d7da3a4431f587f4efc0`, branch de origem `feat/c-response-markdown-units`, mensagem `feat: add deterministic C-A5 markdown unit reader`). Arquivos: `src/casa77_sdr/response_markdown_units.py` (blob `3c99d89aa0028f673548f5cc932ec166d592cd7f`) e `tests/test_response_markdown_units.py` (blob `ee3dc335b3d94588d183c8ebe64771e45df08c14`) — **2 files changed, 1931 insertions(+), 0 deletions(-)**, **nenhum arquivo preexistente alterado** e **corpus preservado no blob `3bfb2e9fd18bac016e1dbe2c963ff916ceb0c96c`**. Baseline **`2908 passed`** / Python 3.14.5, com **`201 passed`** no direcionado; **`201`** e **`2908`** também sob `-W error`. **Cria o novo marco funcional** e **não recebe numeração de subetapa** |
| **Nona microentrega funcional de `C` — derivador determinístico dos tokens canônicos do lado do índice** (`src/casa77_sdr/response_index_tokens.py` + `tests/test_response_index_tokens.py`): materializa **somente a derivação do domínio de identidades do lado do índice** — a função pura `derivar_tokens_do_indice(indice: object) -> tuple[str, ...]` recebe a **estrutura já em memória** e devolve **exclusivamente** os tokens canônicos `<Rxx>/<id>` de **`C-A5-T1`**, com o separador `/` de **`C-A5-T2`**, na ordem das listas recebidas e **derivados, nunca armazenados** (**`C-A5-T5`**). Lê **apenas a projeção mínima** — raiz, `respostas`, o `id` de cada resposta e o `id` de cada fragmento —, aplicando a forma fechada **C-2b** e a unicidade global **C-2a** ao `Rxx`, a gramática fechada **`C-A5-I3`** ao `fragmentos[].id`, a exigência de **ao menos um** fragmento (**C-2c**) e a unicidade **local ao `Rxx`** (**`C-A5-I4`**, **C-2h**). Contêineres aceitam subclasses (`isinstance`, compatível com `response_index.py`); os **componentes da identidade** exigem `str` **exata**, como **defesa local** que **não altera C-2, C-A5 nem `validar_indice`**. **Não substitui `validar_indice`**: `status`, `bindings`, `itera_sobre`, *placeholder*, `caminho_yaml`, `formato`, `predicado`, mecanismo, origem e chaves desconhecidas **não são julgados**. **Não cria nem lê o índice real**, que **continua INEXISTENTE**; **não constrói correspondências**, **não chama `validar_bijecao`** e **não executa a bijeção física**. **Zero I/O, zero `pathlib`, zero YAML, zero rede, zero LLM, zero relógio, zero *locale*, zero ambiente, zero banco, zero import de `casa77_sdr.*` e zero export em `__init__.py`.** **DERIVAR UM DOMÍNIO DE TOKENS NÃO É EXECUTAR A BIJEÇÃO E NÃO É MATERIALIZAR `C`** | **funcional** | PR #104 — **INTEGRADO à `main`** em 2026-09-04 (commit funcional `45876ca609716ede51aefcf8752dd29f98a736a7`, merge `654aaedec2d424ab4184e7a71a0d3c129021abf8`, branch de origem `feat/c-response-index-tokens`, mensagem `feat: add deterministic response index token derivation`). Arquivos: `src/casa77_sdr/response_index_tokens.py` (blob `84b69472a702a6d436729dbe40a89cf4fcc07bb0`) e `tests/test_response_index_tokens.py` (blob `90bf631403bf2ba7c463348a660f64766f9104aa`) — **2 files changed, 1181 insertions(+), 0 deletions(-)**, **nenhum arquivo preexistente alterado**. Baseline **`3111 passed`** / Python 3.14.5, com **`203 passed`** no direcionado; **`203`** e **`3111`** também sob `-W error`; delta **+203** sobre os **`2908 passed`** anteriores. **Sem CI configurado** — ausência de checks, **não** falha de CI. **Cria o novo marco funcional** e **não recebe numeração de subetapa** |
| **Décima microentrega funcional de `C` — composição determinística em memória da correspondência canônica** (`src/casa77_sdr/response_correspondence.py` + `tests/test_response_correspondence.py`): materializa **somente a composição** de três fronteiras já existentes — `validar_correspondencia_canonica(indice: object, texto_markdown: str) -> None` recebe uma **estrutura candidata do índice** e um **Markdown**, ambos **já em memória**, e julga se os dois denotam **as mesmas identidades canônicas `<Rxx>/<id>`**. Ordem **fixa**: `derivar_tokens_do_indice` (C9) → `ler_unidades_marcadas` (C8) → relação **diagonal `(token, token)`**, um par por token do domínio do índice na ordem em que ele os devolveu → `validar_bijecao` (C6), chamado **uma única vez**. A correspondência é **igualdade da identidade canônica** — **nunca** posição, ordem, `zip`, conteúdo ou normalização —, conforme **`C-A5-T1`**, **`C-A5-T2`**, **`C-A5-T3`**, **`C-A5-T4`**, **`C-A5-T5`** e **`C-A5-I5`**, servindo aos **dois** domínios de **`C-A1-B3`** / **`C-A1-B4`**. **Não cria juiz novo**: C9 continua dona do domínio do índice, C8 do domínio do Markdown e C6 do julgamento da bijeção. **Zero validação local**, **zero exceção nova** — `ProjecaoDeIdentidadeInvalida`, `RepresentacaoMarcadaInvalida` e `BijecaoInvalida` **propagam intactas**, sem `try`/`except` e sem tocar `__cause__`/`__context__`. **Não substitui `validar_indice`**, que **não é importado nem chamado**; **não cria nem lê o índice físico**, que **continua INEXISTENTE**; **não executa a bijeção física 37/37**; **não migra autoridade de status**. **Zero I/O, zero `pathlib`, zero YAML, zero rede, zero LLM, zero relógio, zero *locale*, zero ambiente, zero banco, zero cache, zero estado mutável de módulo**, e os insumos **não são alterados**. **COMPOR E VALIDAR EM MEMÓRIA NÃO É EXECUTAR A BIJEÇÃO FÍSICA E NÃO É MATERIALIZAR `C`** | **funcional** | PR #106 — **INTEGRADO à `main`** em 2026-09-04 (commit funcional `6265b823cb20aab0395840f8125008121de27e43`, merge `457e29a42472d44175d72031cff05ec1a1ebf9d1`, branch de origem `feat/c-response-correspondence`, mensagem `feat: add deterministic canonical response correspondence composition`). Arquivos: `src/casa77_sdr/response_correspondence.py` (blob `e3e895246f42a0a5f60c61b7cb68b2a922559134`) e `tests/test_response_correspondence.py` (blob `b4ba305e51dd166596def93a6381209802b23330`) — **2 files changed, 843 insertions(+), 0 deletions(-)**, **nenhum arquivo preexistente alterado**. Baseline **`3186 passed`** / Python 3.14.5, com **`75 passed`** no direcionado; **`75`** e **`3186`** também sob `-W error`; delta **+75** sobre os **`3111 passed`** anteriores (**3111 + 75 = 3186**). **Sem CI configurado** — ausência de checks, **não** falha de CI. **Cria o novo marco funcional** e **não recebe numeração de subetapa** |
| **Décima primeira microentrega funcional de `C` — extração determinística do texto emitível canônico** (`src/casa77_sdr/response_emittable_text.py` + `tests/test_response_emittable_text.py`): materializa **`MT3`–`MT11`** — `extrair_textos_emitiveis(texto: str) -> tuple[tuple[str, str], ...]` recebe a **representação marcada já em memória** e devolve, **em ordem física**, um par **`(token_canonico, texto_canonico)`** por unidade emitível declarada. **C8 é chamado primeiro e continua o único juiz estrutural**: `RepresentacaoMarcadaInvalida` **propaga intacta**; só depois a C11 **localiza as mesmas unidades**, deriva o token **somente do `Rxx` e do `id` declarados** (**`C-A5-I5`** — nunca posição, ordem, `zip` ou conteúdo) e **verifica a sequência local de tokens contra C8 antes de devolver qualquer par** (`RuntimeError("invariante_estrutural")` em divergência interna). Prefixo **exatamente `> `**; linha `>` interna única → **`\n\n`**; linha `>` em borda ou consecutiva → **recusa**; linhas consecutivas de conteúdo → **um `LF`**, não convertido em espaço; `LF` e `CRLF` aceitos, `CR` do par removido; **`CR` isolado, inclusive no EOF, recusado**; **EOF sem newline aceito**; terminadores exóticos e whitespace terminal **recusados**; **nenhuma correção silenciosa**. Categorias fechadas: `prefixo_invalido`, `linha_vazia_invalida`, `terminador_proibido`, `branco_antes_do_terminador`. **Não valida equivalência, não aplica `NFC`, não converte quebra suave em espaço, não lê arquivo/YAML/índice, não resolve *binding* ou status, não executa a bijeção física, não materializa `C`.** **Zero I/O, zero `pathlib`, zero YAML, zero rede, zero LLM, zero relógio, zero *locale*, zero ambiente, zero banco, zero cache, zero estado mutável de módulo**, entrada **não alterada**. **EXTRAIR TEXTO CANÔNICO NÃO É VALIDAR EQUIVALÊNCIA, NÃO É EXECUTAR A BIJEÇÃO FÍSICA E NÃO É MATERIALIZAR `C`** | **funcional** | PR #109 — **INTEGRADO à `main`** em 2026-09-05 (commit funcional `4b6ea8ca00c171275d75ea17c4414011a4f1a835`, parent único `690a09c2a594f422b450afc3d780054be2168554`, merge `ceecd638131899974ce43b4685b254bf01d7bbad`, branch de origem `feat/c-emittable-text-extraction`, mensagem `feat: add deterministic emittable response text extraction`). Arquivos: `src/casa77_sdr/response_emittable_text.py` (blob `ff811210cc59f9c50b7f019d1d6798af9083439f`) e `tests/test_response_emittable_text.py` (blob `156bbbf86d42e6cd1a3474ed111b12115dec5d0a`) — **2 files changed, 1731 insertions(+), 0 deletions(-)**, **nenhum arquivo preexistente alterado**. Baseline **`3404 passed`** / Python 3.14.5, com **`218 passed`** no direcionado; **`218`** e **`3404`** também sob `-W error`; delta **+218** sobre os **`3186 passed`** anteriores (**3186 + 218 = 3404**), executados no `.venv` do projeto. **Sem CI configurado** — ausência de checks, **não** falha de CI. **Cria o novo marco funcional** e **não recebe numeração de subetapa** |
| **Décima segunda microentrega funcional de `C` — extração determinística do rótulo literal de status do cabeçalho `Rxx`** (`src/casa77_sdr/response_header_labels.py` + `tests/test_response_header_labels.py`): materializa a gramática física **`G2`** já arbitrada — `extrair_rotulos_de_cabecalho(texto: str) -> tuple[tuple[str, str], ...]` recebe a **representação marcada já em memória** e devolve, **em ordem física**, um par **`(Rxx, rotulo_literal)`** por cabeçalho físico `## Rxx`. **C8 é chamado primeiro, exclusivamente como portão estrutural**: `RepresentacaoMarcadaInvalida` **propaga intacta**; o resultado de C8 **não é armazenado nem comparado** — **zero invariante local × C8** —; só depois a C12 localiza os cabeçalhos `Rxx` por caminhada local mínima. Separador literal `U+0020 U+2014 U+0020`, **imediatamente após `Rxx`** e **exatamente duas vezes** (ocorrências sobrepostas contam; linha ambígua recusada); título e rótulo **não vazios** e **sem branco ASCII de borda**; `-`, `–`, variantes Unicode e espaçamento divergente **recusados**; **zero `strip`, zero normalização, zero inferência**. Categorias fechadas: `separador_ausente`, `cardinalidade_de_separador`, `segmento_vazio`, `branco_de_borda`; localizadores `cabecalho`, `titulo`, `rotulo`. Política de linhas **estrutural de C8** (`LF`, no máximo um `CR` terminal, sem `splitlines()`). **Seções homônimas preservadas, sem dedup e sem `dict`.** **`PARCIAL` extraído literalmente e NÃO resolvido** — não importa `response_status`, não canonicaliza, não propaga, não mapeia. **Não cria índice, não executa a bijeção física, não cria *bindings*, não implementa *placeholder*, `caminho_yaml`, `hora` ou C-7, não executa equivalência, não renderiza, não integra runtime, não migra autoridade, não materializa `C`.** **Zero I/O, zero `pathlib`, zero YAML, zero rede, zero LLM, zero relógio, zero *locale*, zero ambiente, zero banco, zero cache, zero logging, zero estado mutável de módulo, zero `assert`, zero regex**, entrada **não alterada**. **EXTRAIR O RÓTULO NÃO É CANONICALIZAR STATUS, NÃO É PROPAGAR STATUS, NÃO É RESOLVER `PARCIAL` E NÃO É MATERIALIZAR `C`** | **funcional** | PR #113 — **INTEGRADO à `main`** em 2026-09-05 (commit funcional `798beb31fd0dc4fed34aa7b20d397abcd2ef8c2b`, parent único `6940bf32525c028982838bf27ac3cc067adf3581`, merge `eae7b5098b248cefb42b3a82569fc0575fd6fee0`, branch de origem `feat/c-header-label-extraction`, mensagem `feat: add deterministic Rxx header label extraction`). Arquivos: `src/casa77_sdr/response_header_labels.py` (blob `f8a8e6d6e4a0a03eea4069fd24bcc9eb38b5c06f`) e `tests/test_response_header_labels.py` (blob `eb097b250c3ecc56597878b951e12bf1afdadc72`) — **2 files changed, 1831 insertions(+), 0 deletions(-)**, **nenhum arquivo preexistente alterado**. Baseline **`3703 passed`** / Python 3.14.5, com **`299 passed`** no direcionado; **`299`** e **`3703`** sob `-W error`; delta **+299** sobre os **`3404 passed`** anteriores (**3404 + 299 = 3703**), executados no `.venv` do projeto. **Sem CI configurado** — ausência de checks, **não** falha de CI. **Cria o novo marco funcional** e **não recebe numeração de subetapa** |
| **Décima terceira microentrega funcional de `C` — propagação pura e determinística de status `ST1`–`ST3` aos fragmentos já associados** (`src/casa77_sdr/response_status_propagation.py` + `tests/test_response_status_propagation.py`): materializa **`SP1`**, **`SP2`** e **`SP3`** já arbitradas — `propagar_status(rotulo: str, fragmentos: Sequence[str]) -> tuple[tuple[str, str], ...]` e `PropagacaoInvalida`, **`__all__` de exatamente dois nomes**, **não exportada pelo package root**. **Primitiva PURA**: **não recebe Markdown**, **não chama C8, C11 ou C12**, **não localiza `Rxx`**, **não resolve contenção**, **não resolve homônimos** e **não compõe nem decompõe identidade** — **a associação correta entre rótulo e fragmentos é pré-condição do chamador**. A **primeira** operação funcional é `canonicalizar_status(rotulo)`, **sem validação anterior de `fragmentos`**, de modo que **o rótulo falha primeiro**; `StatusNaoCanonicalizavel` **propaga intacta**. Tradução **delegada**, restrita a **`ST1`–`ST3`**, **sem quarta tradução** e **sem transportar o handoff**. **`SP3` por construção**: **todos** os fragmentos daquela chamada recebem **o mesmo** status, que **não depende** de posição, ordem, índice, token, `id`, conteúdo, quantidade ou redação (**`C-A5-I5`**, **`C-A5-M6`**). **Tokens opacos**, com **duplicidades preservadas** e **zero dedup, `dict` ou `zip`**. **`PropagacaoInvalida`** tem **categoria única** `tipo_invalido` e **dois localizadores** — `fragmentos` e `fragmentos.item` —, julgando **somente a forma mínima do argumento**, **nunca identidade**; *fail-closed*, **nada devolvido parcialmente**. **`PARCIAL` continua NÃO RESOLVIDO** — a recusa é **somente daquela invocação**. **2 arquivos novos, +1762 / −0, zero arquivo preexistente alterado.** **PR #115** — commit funcional `cbf3e379c9b6697cd502b6a7a0bd3e9bb76c1a27`, merge `50c1d5e681a11923c443c1f117de5751ea846cdd`. **`397 passed`** no direcionado; **`397`** e **`4100`** sob `-W error`; delta **+397** sobre os **`3703 passed`** anteriores (**3703 + 397 = 4100**), executados no `.venv` do projeto. **Sem CI configurado** — ausência de checks, **não** falha de CI. **Cria o novo marco funcional** e **não recebe numeração de subetapa** |
| **Décima quarta microentrega funcional de `C` — leitor/validador determinístico de status por fragmento sob `PARCIAL`** (`src/casa77_sdr/response_fragment_status.py` + `tests/test_response_fragment_status.py`): materializa **`PM1`–`PM5`** e o **regime exclusivo** já arbitrados — `extrair_status_por_fragmento(texto: str) -> tuple[tuple[str, str], ...]` e `DeclaracaoDeStatusInvalida`, **`__all__` de exatamente dois nomes**, **não exportada pelo package root**. **`C12` é o primeiro portão e `C8` é satisfeito transitivamente**: a primeira operação funcional é `extrair_rotulos_de_cabecalho(texto)`, chamada **uma única vez**, e o módulo **não importa** `response_markdown_units`; as exceções de C8 e C12 **propagam intactas**, e uma falha estrutural ou `G2` **posterior vence** violação `PM` anterior. **Caminhada física local** mantendo `Rxx` **e** rótulo da seção corrente — **sem `zip`, `dict`, agrupamento por `Rxx`, pareamento por posição, cardinalidade ou dedup** —, com **invariante local × `C12`** comparando as sequências **inteiras** antes de qualquer sucesso e produzindo `RuntimeError("invariante_estrutural")` na divergência. **Regime exclusivo** `rotulo_literal == "PARCIAL"`, **sem** carregar os rótulos físicos de `ST1`–`ST3` e **sem** importar `response_status` ou `response_status_propagation`. **Valores** exatamente `APROVADO`, `AGUARDA_APROVACAO` e `BLOQUEADO`, com `PARCIAL` **inválido como valor**. **Cinco mensagens fechadas**: `valor_invalido: declaracao`, `declaracao_fora_de_secao: declaracao`, `declaracao_proibida: declaracao`, `declaracao_orfa: declaracao` e `declaracao_ausente: marcador` — **sem** categoria `declaracao_multipla`. **Ordem local** valor → seção → regime → marcador seguinte; *fail-closed*; **nada devolvido parcialmente**. **Saída** `(token_canonico, status_canonico)` com **ordem física, duplicidades e homônimos preservados**. **2 arquivos novos, +2207 / −0, zero arquivo preexistente alterado.** **PR #120** — commit funcional `75025cc07c8d95f998c61f7516bf3db82bc9c06f`, correção posterior **não funcional** `ca4ec54bc8c1324cc93baf2b7500fa4a04b3f298` (docstring do `CR` residual, **zero lógica e zero teste alterados**), merge `e8db60d95c104993d657de32b80e749dee8003ef`. **`243 passed`** no direcionado; **`243`** e **`4343`** sob `-W error`; delta **+243** sobre os **`4100 passed`** anteriores (**4100 + 243 = 4343**), com **`201 passed`** em C8 e **`299 passed`** em C12, executados no `.venv` do projeto. **Sem CI configurado** — ausência de checks, **não** falha de CI. **Cria o novo marco funcional** e **não recebe numeração de subetapa** |

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
normativa — o **PR #42 especificou**; o **PR #44 materializou**. Ele entregou **apenas a
projeção por chamada**: à época daquele PR, **não existiam** a decisão de qual valor usar
para `instante_ultima_transicao` nem a **composição entre as até três chamadas** do ciclo.
O PR #44 **também não recebeu numeração de subetapa**.

O **PR #47** é a **entrega funcional seguinte** e materializou, **depois**, a **decisão
pura** e a **composição decisória das 0–3 `DecisaoMaquina`**: `decidir_instante_ultima_transicao(...)`
**agora existe** em `src/casa77_sdr/transition_marker.py` e decide **exclusivamente** por
`transicoes_que_mudaram_estado`. A cronologia é, portanto, **PR #42 arbitrou o contrato →
PR #44 materializou a projeção por chamada → PR #47 materializou a decisão e a
composição**. Deixou de ser verdade que "a composição entre as até três chamadas não
existe em código".

O **PR #47 não concluiu N-a-T3–N-a-T7**: **à época daquele PR**, continuavam **NÃO
implementadas** a **aplicação** dessa decisão pelo chamador da **etapa 13** e a **escrita
efetiva** via `criar`/`gravar`. Ele **também não recebeu numeração de subetapa**: **nenhuma
3B.8 foi criada, escolhida ou autorizada**.

O **PR #48** é a **reconciliação exclusivamente documental** de `docs/00` posterior ao
**PR #47**: commit documental `db9b202eeea95cbf249863a0cd4967627eae0156`, merge
`5a059b4b7ba69e912c960bfa4d7a7990228a6792`, branch de origem
`docs/reconciliar-estado-pos-pr47`. Alterou **exclusivamente** `docs/00-estado-atual.md`
— **125 adições, 78 remoções** —, **não tocou** `src/`, `tests/`, `docs/07`, `knowledge/`
nem `prompts/`, **não alterou o baseline** e **não criou marco funcional novo**: o marco
funcional continuava sendo o do **PR #47**.

O **PR #49** é a **entrega funcional seguinte** e materializou a **aplicação** da decisão
e a **escrita** do marco como **fronteira chamável**: `criar_com_marco_de_transicao(...)`
e `gravar_com_marco_de_transicao(...)` **agora existem** em
`src/casa77_sdr/transition_marker_write.py`. Commit funcional
`d621a2c7252b4e758278e51af3617bb9d00a97b6`, merge
`f82da69feb11ba3051fd595d02775171814f8f33` — **3 arquivos, 865 adições, 19 remoções**
(`docs/07-arquitetura-motor-respostas.md`, `src/casa77_sdr/transition_marker_write.py` e
`tests/test_transition_marker_write.py`). A cronologia é, portanto: **PR #42 arbitrou o
contrato → PR #44 materializou a projeção por chamada → PR #47 materializou a decisão e a
composição → PR #48 reconciliou `docs/00` → PR #49 materializou a aplicação e a escrita**.
Deixou de ser verdade que "a aplicação da decisão e a escrita efetiva do marco não existem
em código". O PR #49 **também não recebeu numeração de subetapa**: **nenhuma 3B.8 foi
criada, escolhida ou autorizada**.

O **PR #49 não conclui operacionalmente N-a-T3–N-a-T7**. O que existe é uma **fronteira
chamável** (`docs/07` §6.2, **M-AE1–M-AE7**): ela **delega** a decisão a
`decidir_instante_ultima_transicao(...)`, **aplica** o valor decidido sobre um
`RegistroAtendimento` **recebido pronto** — substituindo **somente**
`instante_ultima_transicao` — e **escreve** pelo contrato existente
`PersistenciaOperacional.criar(...)` ou `PersistenciaOperacional.gravar(...)`. Continuam
**NÃO implementados ou NÃO integrados**: a **montagem completa** do `RegistroAtendimento`;
a **decisão de se a etapa 13 executa**; a **escolha entre criar e gravar** no pipeline; a
**geração de `id_atendimento`**; a **criação operacional** do atendimento; a **marcação de
idempotência**; a **preservação de pendente**; o **tratamento operacional de falha**
(S4, S5); o **destino do alerta operacional**; a **persistência não volátil**; o
**`OrquestradorMotor`**; e o **pipeline completo**. A **etapa 13 continua NÃO integrada** e
**N-a-T3–N-a-T7 não estão operacionalmente concluídas**.

O **PR #38 não implementou a etapa 3 inteira**, **não integrou o pipeline completo** e
**não implementou o `OrquestradorMotor`**. **À época daquele PR**, também não existiam a
decisão nem a composição de **N-a-T3–N-a-T7** — materializadas depois, pelo **PR #47** —,
nem a **aplicação** e a **escrita** do marco — materializadas depois ainda, pelo
**PR #49**. Continuam **não implementados**: a **integração operacional da etapa 13**, o
**tratamento operacional dos bloqueios** (S4, S5), o **destino do alerta operacional**,
**N-b** — **arbitrada** pelo **PR #51** e, hoje, **parcialmente materializada** pelo **PR #55** —, **E4**, **S2-D8** e **S3-D1**. O PR #38 **também não recebeu numeração de
subetapa**: **nenhuma 3B.8 foi criada, escolhida ou autorizada**.

O **PR #50** é a **reconciliação exclusivamente documental** de `docs/00` posterior ao
**PR #49**: commit documental `5509a3f2e01a79cf52acde427794b1de4ec07ff1`, merge
`60701aaaf7a85614e27cf3e95b6a25870769aee5`, branch de origem
`docs/reconciliar-estado-pos-pr49`. Alterou **exclusivamente** `docs/00-estado-atual.md`
— **217 adições, 120 remoções** —, **não tocou** `src/`, `tests/`, `docs/07`, `knowledge/`
nem `prompts/`, **não alterou o baseline** e **não criou marco funcional novo**.

O **PR #51** integrou a **arbitragem documental N-b** — **contrato global da
`Interpretacao` da etapa 4**: commit documental
`6f1cb6fe5ef12096117f1292225a761af5889025`, merge
`85dbc709799f30c59a458c3ea8725fc072a15364`, branch de origem
`docs/arbitragem-nb-interpretacao`. Alterou **exclusivamente**
`docs/07-arquitetura-motor-respostas.md` — **365 adições, 8 remoções** —, **não tocou**
`src/`, `tests/`, `docs/00`, `docs/06`, `knowledge/` nem `prompts/`, **não alterou o
baseline** e **não criou marco funcional novo**. Valeu a mesma regra dos PRs #23, #25,
#27, #31 e #42: **ele especifica, não implementa**.

**O que o PR #51 fechou**, em resumo — o detalhe normativo vive em `docs/07` §6.3 e **não é
duplicado aqui**: as **oito** categorias da `Interpretacao` preservadas;
**`IntencaoConversacional`** como vocabulário conceitual **fechado em 11 valores**, na
partição **A1 (6 derivados) / A2 (2 autônomos) / B (3 autônomos)**; a **derivação
determinística** para a `ProjecaoInterpretacao`, que permanece com **sete** campos; a
**função total** da **condição 5** de §4.4, `interesse_confirmar_disponibilidade`; a
**consistência cruzada** dos **seis pares de representação dupla**; as **regras de
confiança**, binária e sem threshold; o **modo degradado**; a lista fechada de **erros de
contrato E-Nb-1–E-Nb-19**; os **cenários K-Nb-1–K-Nb-40**; e a **fronteira conceitual do
produtor de interpretação da etapa 4**, dentro do **limite único de LLM** já previsto em
`docs/07` §4.2 e §9.

**O PR #51 não implementou nada.** **À época daquele PR**, não existia produtor concreto de
`Interpretacao`, a **etapa 4 não era funcional** e nenhum tipo Python havia sido criado.
Nenhum arquivo de `src/`, `tests/`, `knowledge/` ou `prompts/`
foi criado ou alterado por ele, e **nenhum fornecedor, modelo,
SDK, API, biblioteca ou formato de transporte foi escolhido**. **Estado atual**: o contrato
ali arbitrado foi **materializado parcialmente depois**, pelo **PR #55**, que implementou a
**fronteira determinística** em `src/casa77_sdr/interpretation.py`. O **produtor não
determinístico / LLM continua não implementado**, o **bot não interpreta texto livre**,
**nenhuma mensagem real pode ser testada via LLM**, o **pipeline não está integrado** e o
**`OrquestradorMotor` continua não implementado**. `docs/07` §4.1 permanece com
**14** componentes e §2 com **nove** responsabilidades. Permanece como **residual explícito
de integração**, **sem identificador de pendência novo**, a **transformação posterior dos
sinais interpretados em eventos `Exx`** — a **etapa 4 não emite `Exx`**. O PR #51 **também
não recebeu numeração de subetapa**: **nenhuma 3B.8 foi criada, escolhida ou autorizada**.

O **PR #52** integrou a **reconciliação de `docs/00` após o PR #51**: commit documental
`f3fafee09b7d6bad464134fd9d20d603ebbb0122`, merge
`cc7f4493b97935ef92efe2e821d7a032d16db1a4`, branch de origem
`docs/reconciliar-estado-pos-pr51`. Alterou **exclusivamente** `docs/00-estado-atual.md`
— **148 adições, 40 remoções** —, **não tocou** `src/`, `tests/`, `docs/07`, `knowledge/`
nem `prompts/`, **não alterou o baseline** e **não criou marco funcional novo**.

O **PR #53** integrou a **micro-arbitragem documental AJ1** — **representação e
canonicalização determinística de N-b**: commit documental
`d1137cf67c42eae37ec8e837a56350da6c7fbabe`, merge
`2e9df1f4dfcd11903d410ba7a42ba12d86eb2b15`, branch de origem
`docs/nb-aj1-canonicalizacao`. Alterou **exclusivamente**
`docs/07-arquitetura-motor-respostas.md` — **156 adições, 1 remoção** —, **não tocou**
`src/`, `tests/`, `docs/00`, `docs/06`, `knowledge/` nem `prompts/`, **não alterou o
baseline** e **não criou marco funcional novo**. Valeu a mesma regra dos PRs #23, #25,
#27, #31, #42 e #51: **ele especifica, não implementa**.

**O que o PR #53 fechou**, em resumo — o detalhe normativo vive em `docs/07` §6.3, §8.2 e
§12 e **não é duplicado aqui**: **`A1` não é entrada semântica independente** do produtor
não determinístico, tendo **presença derivada** do payload autoritativo e **confiança
calculada** por **N-b-X3** — que **pode ser armazenada para auditabilidade sem ser
declarada**; o **slot de intenções autônomas** aceita **exatamente** os **cinco** códigos
**A2/B**; a **precedência `E-Nb-3` × `E-Nb-5`** para tentativa de apresentar código **A1**
nesse slot; a **classificação** dos **19** erros em **recebíveis/runtime**, **invariantes
internos da canonicalização** e **invariante estrutural do módulo**; `E-Nb-13` como
**invariante/program error**; o **alcance de prova** de **K-Nb-18**, **K-Nb-34** e
**K-Nb-39**; a **estratégia estrutural** de prova de `E-Nb-19`; a **preservação da condição
5**; e a **reutilização por import** de `FormatoEvento`, **apenas como decisão para a
futura materialização**.

**O PR #53 não implementou nada.** **AJ1 é micro-arbitragem documental**: ela **não
implementou a `Interpretacao`**, **não tornou a etapa 4 funcional**, **não criou produtor
LLM**, **não criou componente** e **não criou subetapa**. Nenhum arquivo de `src/`,
`tests/`, `knowledge/` ou `prompts/` foi criado ou alterado por ela, e **nenhum tipo Python
foi criado à época**. **Estado atual**: o contrato de representação e canonicalização
fechado por AJ1 foi **materializado depois**, pelo **PR #55**, em
`src/casa77_sdr/interpretation.py`. Continuam valendo: o **produtor não determinístico /
LLM não está implementado**; o **bot não interpreta texto livre**; **nenhuma mensagem real
pode ser testada via LLM**; o **pipeline não está integrado**; e o **`OrquestradorMotor`
continua não implementado**.
`docs/07` §4.1 permanece com **14** componentes e §2 com **nove** responsabilidades;
`IntencaoConversacional` permanece com **11** valores; os erros permanecem
**E-Nb-1–E-Nb-19**; e os cenários permanecem **K-Nb-1–K-Nb-40**. AJ1 **corrigiu**, no mesmo
bloco, a formulação sobre o residual: **`N-b-RES1` é regra fechada** — a **etapa 4 não emite
`Exx`** —, **`N-b-RES2` é o residual explícito ABERTO** da **transformação posterior** dos
sinais interpretados em **eventos confirmados**, e **`N-b-RES3` é a classificação fechada**
desse residual. O PR #53 **também não recebeu numeração de subetapa**: **nenhuma 3B.8 foi
criada, escolhida ou autorizada**.

## Testes

**Baseline funcional corrente: `4741 passed` / Python 3.14.5.**

**Execuções da PR #131, registro do parser puro da gramática de `caminho_yaml`**
(2026-09-07, Python 3.14.5) — **três execuções listadas, todas aprovadas**, com **proveniências
distintas**: a **baseline pré-implementação** foi medida **antes de qualquer edição**, sobre a
**base `51fa44c4a9f5b65505f7668c1ce05e8b8f97dd68`**; o **direcionado** e a **suíte completa**
foram medidos sobre a **implementação funcional da PR #131** — os bytes que vieram a ser
exatamente os blobs integrados — e **reexecutados com os mesmos números imediatamente antes
do merge**:

| Momento | Comando | Resultado |
|---|---|---|
| **baseline pré-implementação** | `.venv\Scripts\python.exe -W error -m pytest -q` | **`4594 passed`** |
| **direcionado** | `.venv\Scripts\python.exe -W error -m pytest tests/test_response_yaml_path.py -q` | **`147 passed`** |
| **suíte completa estrita** | `.venv\Scripts\python.exe -W error -m pytest -q` | **`4741 passed`** |

**Zero failures, zero errors e zero warnings** sob `-W error`. O delta é **+147**,
**exatamente** o número de testes coletados do arquivo direcionado **novo** — **`4594 + 147 =
4741`** —, e **nenhum teste preexistente foi alterado, removido ou pulado**. Os testes foram
executados com o interpretador do **`.venv` do projeto**, **Python 3.14.5** — **nenhuma
alteração de ambiente, dependência ou configuração foi feita**. **A suíte nova é inteiramente
SINTÉTICA**: **nenhum teste lê o corpus versionado**. **Estes números são evidência da
ENTREGA FUNCIONAL do PR #131, e NÃO uma execução da reconciliação documental**: nesta
reconciliação **nenhum `pytest` foi executado**, porque **zero código, zero teste e zero
`knowledge/**` mudaram**. **Não há CI remoto configurado**: a PR #131 e o merge commit
`6ae5cd82…` possuem **zero *statuses*** e **zero *workflow runs*** — **AUSÊNCIA DE CI/CHECKS
— NÃO FALHA DE CI**. **Nenhuma execução além das reportadas é alegada.**

**Execuções anteriores — PR #127, registro da composição total de status dos fragmentos emitíveis**
(2026-09-07, Python 3.14.5) — **oito execuções listadas, todas aprovadas**, realizadas **na
entrega funcional**, sobre os bytes que vieram a ser exatamente os blobs integrados:

| Momento | Comando | Resultado |
|---|---|---|
| **baseline pré-implementação** | `.venv\Scripts\python.exe -W error -m pytest -q` | **`4477 passed`** |
| **direcionado** | `.venv\Scripts\python.exe -W error -m pytest tests/test_response_status_composition.py -q` | **`117 passed`** |
| **vizinhança associação física** | `.venv\Scripts\python.exe -W error -m pytest tests/test_response_section_membership.py -q` | **`134 passed`** |
| **vizinhança C14** | `.venv\Scripts\python.exe -W error -m pytest tests/test_response_fragment_status.py -q` | **`243 passed`** |
| **vizinhança C13** | `.venv\Scripts\python.exe -W error -m pytest tests/test_response_status_propagation.py -q` | **`397 passed`** |
| **vizinhança C12** | `.venv\Scripts\python.exe -W error -m pytest tests/test_response_header_labels.py -q` | **`299 passed`** |
| **vizinhança C8** | `.venv\Scripts\python.exe -W error -m pytest tests/test_response_markdown_units.py -q` | **`201 passed`** |
| **suíte completa estrita** | `.venv\Scripts\python.exe -W error -m pytest -q` | **`4594 passed`** |

**Zero failures, zero errors e zero warnings** sob `-W error`. O delta é **+117**,
**exatamente** o número de testes coletados do arquivo direcionado **novo** — **`4477 + 117 =
4594`** —, e **nenhum teste preexistente foi alterado ou removido**; as cinco vizinhanças
permaneceram **inalteradas**. Os testes foram executados com o interpretador do **`.venv` do
projeto**, **Python 3.14.5** — **nenhuma alteração de ambiente, dependência ou configuração foi
feita**. **A suíte nova é inteiramente SINTÉTICA**: **nenhum teste persistente contra**
`knowledge/respostas-aprovadas.md` **foi criado**. **Estes números são evidência da ENTREGA
FUNCIONAL do PR #127, e NÃO uma execução da reconciliação documental**: nesta reconciliação
**nenhum `pytest` foi executado**, porque **zero código, zero teste e zero `knowledge/**`
mudaram**. **Não há CI remoto configurado**: a PR #127 e o merge commit `00c45e9b…` possuem
**zero *statuses*** e **zero *workflow runs*** — **AUSÊNCIA DE CI/CHECKS — NÃO FALHA DE CI**.
**Nenhuma execução além das reportadas é alegada.**

**Evidência read-only do corpus — EVIDÊNCIA DA ENTREGA FUNCIONAL, NÃO TESTE E NÃO NORMA.**
A nova fronteira foi executada **uma vez**, de forma **read-only e não persistente**, contra
`knowledge/respostas-aprovadas.md` — **inalterado** e byte-a-byte no blob
`3a30fe764b80902227fdefb9282f3916650e4f17` —, devolvendo **37 pares**, **37 tokens
distintos**, com agregados **`APROVADO`: 35** e **`AGUARDA_APROVACAO`: 2**. **Nenhum conteúdo
comercial é reproduzido**; **o corpus não foi alterado**; **nenhum teste persistente contra o
corpus foi criado**; e essa evidência **NÃO satisfaz automaticamente `C-A1-ST8`** e **NÃO
migra a autoridade de status** (**`C-11`**).

**Execuções anteriores — PR #124, registro da associação física de seção e fragmentos** (2026-09-06,
Python 3.14.5) — **seis execuções listadas, todas aprovadas**, realizadas **na entrega
funcional**,
sobre os bytes que vieram a ser exatamente os blobs integrados:

| Momento | Comando | Resultado |
|---|---|---|
| **baseline pré-implementação** | `.venv\Scripts\python.exe -W error -m pytest -q` | **`4343 passed`** |
| **direcionado** | `.venv\Scripts\python.exe -W error -m pytest tests/test_response_section_membership.py -q` | **`134 passed`** |
| **vizinhança C8** | `.venv\Scripts\python.exe -W error -m pytest tests/test_response_markdown_units.py -q` | **`201 passed`** |
| **vizinhança C12** | `.venv\Scripts\python.exe -W error -m pytest tests/test_response_header_labels.py -q` | **`299 passed`** |
| **vizinhança C14** | `.venv\Scripts\python.exe -W error -m pytest tests/test_response_fragment_status.py -q` | **`243 passed`** |
| **suíte completa estrita** | `.venv\Scripts\python.exe -W error -m pytest -q` | **`4477 passed`** |

**Zero failures, zero errors e zero warnings** sob `-W error`. O delta é **+134**,
**exatamente** o número de testes coletados do arquivo direcionado **novo** — **`4343 + 134 =
4477`** —, e **nenhum teste preexistente foi alterado ou removido**; as três vizinhanças
permaneceram **inalteradas**. Os testes foram executados com o interpretador do **`.venv` do
projeto**, **Python 3.14.5** — **nenhuma alteração de ambiente, dependência ou configuração foi
feita**. **Estes números são evidência da ENTREGA FUNCIONAL do PR #124, e NÃO uma execução da
reconciliação documental**: nesta reconciliação **nenhum `pytest` foi executado**, porque **zero
código, zero teste e zero `knowledge/**` mudaram**. **Não há CI remoto configurado**: a PR #124
e o merge commit `ecaf0a2b…` possuem **zero *statuses*** e **zero *workflow runs*** —
**AUSÊNCIA DE CI/CHECKS — NÃO FALHA DE CI**. **Nenhuma execução além das reportadas é
alegada.**

**Execuções anteriores — PR #120, registro da entrega C14** (2026-09-06, Python 3.14.5) — **cinco
execuções, todas aprovadas**, realizadas **na entrega funcional**, sobre os bytes que vieram a
ser exatamente os blobs integrados:

| Momento | Comando | Resultado |
|---|---|---|
| **baseline pré-implementação** | `.venv\Scripts\python.exe -W error -m pytest -q` | **`4100 passed`** |
| **direcionado** | `.venv\Scripts\python.exe -W error -m pytest tests/test_response_fragment_status.py -q` | **`243 passed`** |
| **vizinhança C8** | `.venv\Scripts\python.exe -W error -m pytest tests/test_response_markdown_units.py -q` | **`201 passed`** |
| **vizinhança C12** | `.venv\Scripts\python.exe -W error -m pytest tests/test_response_header_labels.py -q` | **`299 passed`** |
| **suíte completa estrita** | `.venv\Scripts\python.exe -W error -m pytest -q` | **`4343 passed`** |

**Zero failures, zero errors e zero warnings** sob `-W error`. O delta é **+243**,
**exatamente** o número de testes coletados do arquivo direcionado **novo** — **`4100 + 243 =
4343`** —, e **nenhum teste preexistente foi alterado ou removido**. Os testes foram executados
com o interpretador do **`.venv` do projeto**, **Python 3.14.5** — **nenhuma alteração de
ambiente, dependência ou configuração foi feita**. A PR #120 tem **dois commits**: o funcional
`75025cc07c…` e a correção **exclusivamente de docstring** `ca4ec54bc8…`, sobre o `CR`
residual, com **zero lógica alterada** e **zero teste alterado**; **as três suítes foram
reexecutadas após ela e devolveram os mesmos números** — `243`, `299` e `4343`. **Estes números
são evidência da ENTREGA FUNCIONAL C14, e NÃO uma execução da reconciliação documental**: nesta
reconciliação **nenhum `pytest` foi executado**, porque **zero código, zero teste e zero
`knowledge/**` mudaram**. **Não há CI remoto configurado**: a PR #120 e o merge commit
`e8db60d9…` possuem **zero *statuses*** e **zero *workflow runs*** — **AUSÊNCIA DE CI/CHECKS —
NÃO FALHA DE CI**. **Nenhuma execução além das reportadas é alegada.**

**Execuções anteriores — PR #115, registro da entrega C13** (2026-09-06, Python 3.14.5) — **três
execuções, todas aprovadas**, realizadas **na entrega funcional**, sobre os **bytes da árvore
de trabalho** que vieram a ser exatamente os blobs integrados (SHA-256 reconferidos antes do
*staging*: `cd168b94…` para o módulo e `1c0d6cac…` para o teste):

| Momento | Comando | Resultado |
|---|---|---|
| **baseline pré-implementação** | `.venv\Scripts\python.exe -W error -m pytest -q` | **`3703 passed`** |
| **direcionado** | `.venv\Scripts\python.exe -W error -m pytest tests/test_response_status_propagation.py -q` | **`397 passed`** |
| **suíte completa estrita** | `.venv\Scripts\python.exe -W error -m pytest -q` | **`4100 passed`** |

**Zero failures, zero errors e zero warnings** sob `-W error`. O delta é **+397**,
**exatamente** o número de testes coletados do arquivo direcionado **novo** — **`3703 + 397 =
4100`** —, e **nenhum teste preexistente foi alterado ou removido**. Os testes foram
executados com o interpretador do **`.venv` do projeto**, **Python 3.14.5** — **nenhuma
alteração de ambiente, dependência ou configuração foi feita**. O **staged foi auditado** —
blobs `cb5668ef…` e `24da2fdb…`, `A/A`, `195 / 0` e `1567 / 0` — e os **blobs integrados à
`main` são exatamente esses blobs**, conferidos em `origin/main` e no commit funcional. **Estes
números são evidência da ENTREGA FUNCIONAL C13, e NÃO uma execução da reconciliação
documental**: nesta reconciliação **nenhum `pytest` foi executado**, porque **zero código,
zero teste e zero `knowledge/**` mudaram**. **Não há CI remoto configurado**: a PR #115 e o
merge commit `50c1d5e6…` possuem **zero *statuses*** e **zero *workflow runs*** — **AUSÊNCIA
DE CI/CHECKS — NÃO FALHA DE CI**. **Nenhuma execução além das reportadas é alegada.**

**Execuções anteriores — PR #113, registro da entrega C12** (2026-09-05, Python 3.14.5) — **três
execuções, todas aprovadas**, realizadas **na entrega funcional**, sobre os **bytes da árvore
de trabalho** que vieram a ser exatamente os blobs integrados (SHA-256 reconferidos antes do
*staging*: `5f5f89d0…` para o módulo e `b6f4af66…` para o teste):

| Momento | Comando | Resultado |
|---|---|---|
| **baseline pré-implementação** | `.venv\Scripts\python.exe -W error -m pytest -q` | **`3404 passed`** |
| **direcionado** | `.venv\Scripts\python.exe -W error -m pytest tests/test_response_header_labels.py -q` | **`299 passed`** |
| **suíte completa estrita** | `.venv\Scripts\python.exe -W error -m pytest -q` | **`3703 passed`** |

**Zero failures, zero errors e zero warnings** sob `-W error`. O delta é **+299**,
**exatamente** o número de testes coletados do arquivo direcionado **novo** — **`3404 + 299 =
3703`** —, e **nenhum teste preexistente foi alterado ou removido**. Os testes foram
executados com o interpretador do **`.venv` do projeto**, **Python 3.14.5** — **nenhuma
alteração de ambiente, dependência ou configuração foi feita**. O **staged foi auditado** —
blobs `f8a8e6d6…` e `eb097b25…`, `A/A`, `299 / 0` e `1532 / 0` — e os **blobs integrados à
`main` são exatamente esses blobs**, conferidos em `origin/main` e no commit funcional. **Estes
números são evidência da ENTREGA FUNCIONAL C12, e NÃO uma execução da reconciliação
documental**: nesta reconciliação **nenhum `pytest` foi executado**, porque **zero código,
zero teste e zero `knowledge/**` mudaram**. **Não há CI remoto configurado**: a PR #113 e o
merge commit `eae7b509…` possuem **zero *statuses*** e **zero *workflow runs*** — **AUSÊNCIA
DE CI/CHECKS — NÃO FALHA DE CI**. **Nenhuma execução além das reportadas é alegada.**

**Execuções anteriores — PR #109, registro da entrega C11** (2026-09-05, Python 3.14.5) — **três
execuções, todas aprovadas**, realizadas **na entrega funcional**, sobre os **bytes da árvore
de trabalho** que vieram a ser exatamente os blobs integrados (SHA-256 reconferidos
imediatamente antes do *staging* e novamente após o *commit*):

| Momento | Comando | Resultado |
|---|---|---|
| **baseline pré-implementação** | `.venv\Scripts\python.exe -m pytest -q -W error` | **`3186 passed`** |
| **direcionado** | `.venv\Scripts\python.exe -m pytest -q tests/test_response_emittable_text.py -W error` | **`218 passed`** |
| **suíte completa estrita** | `.venv\Scripts\python.exe -m pytest -q -W error` | **`3404 passed`** |

**Zero failures, zero errors e zero warnings** sob `-W error`. O delta é **+218**,
**exatamente** o número de testes do arquivo direcionado **novo** — **`3186 + 218 = 3404`** —,
e **nenhum teste preexistente foi alterado ou removido**. **Ressalva ambiental, objetiva e não
funcional**: o comando literal `python -m pytest` com o **`python` global** falhou na coleta
por **não ter o pacote `casa77_sdr` instalado**; os testes canônicos da entrega foram
executados com o interpretador do **`.venv` do projeto**, também **Python 3.14.5** — **nenhuma
alteração de ambiente, dependência ou configuração foi feita**. O **staged foi auditado** —
blobs `ff811210…` e `156bbbf8…`, `A/A`, `478 / 0` e `1253 / 0` — e os **blobs integrados à
`main` são exatamente esses blobs**, conferidos em `origin/main` e no commit funcional. **Estes
números são evidência da ENTREGA FUNCIONAL C11, e NÃO uma execução da reconciliação
documental**: nesta reconciliação **nenhum `pytest` foi executado**, porque **zero código,
zero teste e zero `knowledge/**` mudaram**.

**Execuções anteriores — PR #106, registro da entrega C10** (2026-09-04, Python 3.14.5) — **quatro
execuções, todas aprovadas**, realizadas **na entrega funcional**, sobre os **bytes da árvore
de trabalho** que vieram a ser exatamente os blobs integrados:

| Momento | Comando | Resultado |
|---|---|---|
| **baseline pré-implementação** | `./.venv/Scripts/python.exe -m pytest -q -W error` | **`3111 passed`** |
| **direcionado** | `./.venv/Scripts/python.exe -m pytest tests/test_response_correspondence.py -q -W error` | **`75 passed`** |
| **suíte completa** | `./.venv/Scripts/python.exe -m pytest -q` | **`3186 passed`** |
| **suíte completa estrita** | `./.venv/Scripts/python.exe -m pytest -q -W error` | **`3186 passed`** |

**Zero failures e zero errors**; **zero warnings** nas variantes estritas. O delta é **+75**,
**exatamente** o número de testes do arquivo direcionado **novo** — **`3111 + 75 = 3186`** —,
e **nenhum teste preexistente foi alterado ou removido**. O **SHA-256 dos dois arquivos foi
reconferido imediatamente antes do staging** — `b6fc5e7e…` para o módulo e `7df163f9…` para
o teste; o **staged foi auditado** — blobs `e3e89524…` e `b4ba305e…`, `A/A`, `118 / 0` e
`725 / 0` — e os **blobs integrados à `main` são exatamente esses blobs staged auditados**,
conferidos em `origin/main` e no commit funcional. **Estes números são evidência da ENTREGA
FUNCIONAL C10, e NÃO uma execução da reconciliação documental**: nesta reconciliação **nenhum
`pytest` foi executado**, porque **zero código, zero teste e zero `knowledge/**` mudaram**.
**Não há CI remoto configurado** para o repositório: `gh pr checks 106` reportou **ausência
de checks** — **ausência de CI, não falha de CI** —, e a PR não recebeu review nem
comentário. **Nenhuma execução além das reportadas é alegada.**

**Execuções da PR #104, registro da entrega C9** (2026-09-04, Python 3.14.5) — **quatro
execuções, todas aprovadas**, realizadas **na entrega funcional**, sobre os **bytes da árvore
de trabalho** que vieram a ser exatamente os blobs integrados:

| Momento | Comando | Resultado |
|---|---|---|
| **baseline pré-edição** | `./.venv/Scripts/python.exe -m pytest -q -W error` | **`2908 passed`** |
| **direcionado** | `./.venv/Scripts/python.exe -m pytest tests/test_response_index_tokens.py -q -W error` | **`203 passed`** |
| **suíte completa** | `./.venv/Scripts/python.exe -m pytest -q` | **`3111 passed`** |
| **suíte completa estrita** | `./.venv/Scripts/python.exe -m pytest -q -W error` | **`3111 passed`** |

**Zero failures e zero errors**; **zero warnings** nas variantes estritas. O delta é **+203**
sobre os **`2908 passed`** do PR #102, **exatamente** o arquivo direcionado **novo**:
**nenhum teste preexistente foi alterado ou removido**. O **SHA-256 dos dois arquivos foi
reconferido imediatamente antes do staging** — `1e45ccef…` para o módulo e `f04f9188…` para
o teste; o **staged foi auditado** — blobs `84b69472…` e `90bf6314…`, `A/A`, `286 / 0` e
`895 / 0` — e os **blobs integrados à `main` são exatamente esses blobs staged auditados**,
conferidos em `origin/main` e no commit funcional. **Estes números são a baseline funcional
confirmada NA ENTREGA C9, e NÃO uma execução da reconciliação documental**: nesta
reconciliação **nenhum `pytest` foi executado**, porque **zero código, zero teste e zero
`knowledge/**` mudaram**. **Não há CI remoto configurado** para o repositório: `gh pr
checks 104` reportou **ausência de checks** — **ausência de CI, não falha de CI** —, e a PR
não recebeu review nem comentário. **Nenhuma execução além das reportadas é alegada.**

**Execuções da PR #102, registro daquela entrega** (2026-09-04, Python 3.14.5) — **quatro
execuções, todas aprovadas**, realizadas **antes do versionamento**, sobre os **bytes da
árvore de trabalho** que vieram a ser exatamente os blobs integrados:

| Momento | Comando | Resultado |
|---|---|---|
| **direcionado** | `./.venv/Scripts/python.exe -m pytest tests/test_response_markdown_units.py` | **`201 passed`** |
| **direcionado estrito** | `./.venv/Scripts/python.exe -m pytest tests/test_response_markdown_units.py -W error` | **`201 passed`** |
| **suíte completa** | `./.venv/Scripts/python.exe -m pytest` | **`2908 passed`** |
| **suíte completa estrita** | `./.venv/Scripts/python.exe -m pytest -W error` | **`2908 passed`** |

**Zero failures e zero errors** nas quatro; **zero warnings** nas duas variantes estritas. O
delta é **+201** sobre os **`2707 passed`** do PR #97, **exatamente** o arquivo direcionado
**novo**: **nenhum teste preexistente foi alterado ou removido**. O **SHA-256 dos dois
arquivos foi reconferido imediatamente antes do staging** — `16d8704b…` para o módulo e
`315dd634…` para o teste; o **staged foi auditado** — blobs `3c99d89a…` e `ee3dc335…`, `A/A`,
`396 / 0` e `1535 / 0` — e os **blobs integrados à `main` são exatamente esses blobs staged
auditados**, conferidos em `origin/main` e no commit funcional. **A suíte NÃO foi reexecutada
nesta reconciliação documental**, porque **zero código e zero teste mudaram** e os **blobs
funcionais integrados são idênticos aos auditados**. **Não há CI remoto configurado** para o
repositório: `gh pr checks 102` reportou **ausência de checks** — **ausência de CI, não falha
de CI** —, e a PR não recebeu review nem comentário. **Nenhuma execução além das reportadas é
alegada.**

**Execuções pós-merge da PR #97, registro daquela entrega** (2026-09-02, Python 3.14.5) —
**quatro execuções, todas aprovadas**, realizadas **sobre a `main` integrada**
(`8c67e13808da59dbace413fce33c2c22280e69a3`), com **árvore de trabalho limpa**, na rodada do
merge; e **reexecutadas nesta reconciliação, depois da edição deste documento**, com os
**mesmos quatro resultados**:

| Momento | Comando | Resultado |
|---|---|---|
| **direcionado** | `./.venv/Scripts/python.exe -m pytest tests/test_response_status.py -p no:cacheprovider` | **`261 passed`** |
| **direcionado estrito** | `./.venv/Scripts/python.exe -m pytest tests/test_response_status.py -W error -p no:cacheprovider` | **`261 passed`** |
| **suíte completa** | `./.venv/Scripts/python.exe -m pytest -p no:cacheprovider` | **`2707 passed`** |
| **suíte completa estrita** | `./.venv/Scripts/python.exe -m pytest -W error -p no:cacheprovider` | **`2707 passed`** |

**Zero failures e zero errors** nas quatro; **zero warnings** nas duas variantes estritas. O
delta é **+261** sobre os **`2446 passed`** do PR #95, **exatamente** o arquivo direcionado
**novo**: **nenhum teste preexistente foi alterado ou removido**. **Antes do commit**, as
**mesmas quatro contagens** haviam sido auditadas sobre os **bytes da árvore de trabalho**, e
o **SHA-256 dos dois arquivos foi reconferido imediatamente antes do staging** —
`8099dd02…` para o módulo e `e31b137b…` para o teste; o **staged foi auditado** — blobs
`ceeb24cc…` e `6028b883…`, `A/A`, `162 / 0` e `1093 / 0` — e os **blobs integrados à `main`
são exatamente esses blobs staged auditados**, conferidos em `origin/main` e no commit
funcional. **Não há CI remoto configurado** para o repositório: `gh pr checks 97` reportou
**ausência de checks** — **ausência de CI, não falha de CI** —, e a PR não recebeu review nem
comentário. **Nenhuma execução além das reportadas é alegada.**

**Execuções pós-merge da PR #95, registro daquela entrega** (2026-09-02, Python 3.14.5) —
**quatro execuções, todas aprovadas**, realizadas **sobre a `main` integrada**
(`b06c0a43bd2f96b8712638e99c55edfe2fb2f99f`), com **árvore de trabalho limpa**, na rodada do
merge; e **reexecutadas nesta reconciliação, depois da edição deste documento**, com os
**mesmos quatro resultados**:

| Momento | Comando | Resultado |
|---|---|---|
| **direcionado** | `./.venv/Scripts/python.exe -m pytest tests/test_response_bijection.py -p no:cacheprovider` | **`284 passed`** |
| **direcionado estrito** | `./.venv/Scripts/python.exe -m pytest tests/test_response_bijection.py -W error -p no:cacheprovider` | **`284 passed`** |
| **suíte completa** | `./.venv/Scripts/python.exe -m pytest -p no:cacheprovider` | **`2446 passed`** |
| **suíte completa estrita** | `./.venv/Scripts/python.exe -m pytest -W error -p no:cacheprovider` | **`2446 passed`** |

**Zero failures e zero errors** nas quatro; **zero warnings** nas duas variantes estritas. O
delta é **+284** sobre os **`2162 passed`** do PR #93, **exatamente** o arquivo direcionado
**novo**: **nenhum teste preexistente foi alterado ou removido**. **Antes do commit**, as
**mesmas quatro contagens** haviam sido auditadas sobre os **bytes da árvore de trabalho**, e
o **SHA-256 dos dois arquivos foi reconferido imediatamente antes do staging**; o **staged foi
auditado** — blobs `b76ed3e8…` e `e54cce87…`, `A/A`, `245 / 0` e `1227 / 0` — e os **blobs
integrados à `main` são exatamente esses blobs staged auditados**, conferidos em
`origin/main` e no commit funcional. **Não há CI remoto configurado** para o repositório:
`gh pr checks 95` reportou **ausência de checks** — **ausência de CI, não falha de CI**.
**Nenhuma execução além das reportadas é alegada.**

**Execuções auditadas da PR #93, registro daquela entrega** (2026-09-01, Python 3.14.5) —
**quatro execuções, todas aprovadas**, realizadas sobre os **bytes auditados da árvore de
trabalho**:

| Momento | Comando | Resultado |
|---|---|---|
| **direcionado** | `./.venv/Scripts/python.exe -m pytest tests/test_response_assertion.py` | **`254 passed`** |
| **direcionado estrito** | `./.venv/Scripts/python.exe -m pytest tests/test_response_assertion.py -W error` | **`254 passed`** |
| **suíte completa** | `./.venv/Scripts/python.exe -m pytest` | **`2162 passed`** |
| **suíte completa estrita** | `./.venv/Scripts/python.exe -m pytest -W error` | **`2162 passed`** |

**Zero failures e zero errors** nas quatro; **zero warnings** nas duas variantes estritas. O
delta é **+254** sobre os **`1908 passed`** do PR #91, **exatamente** o arquivo direcionado
**novo**: **nenhum teste preexistente foi alterado ou removido**. **Antes do commit**, o
**conteúdo staged** foi verificado **mecanicamente** como **idêntico ao da árvore de trabalho
depois da normalização `CRLF → LF` aplicada pelo Git**; o **staged foi auditado** — blobs
`dd6e6f6b…` e `e4b2a7a4…`, `A/A`, `105 / 0` e `843 / 0` — e os **blobs integrados à `main`
são exatamente esses blobs staged auditados**, conferidos em `origin/main` e no commit
funcional.

Sobre a PR #93, registrado à época e **preservado**: **aquela** reconciliação **não executou
a suíte**, por ser **exclusivamente documental**; as contagens acima eram as **auditadas pela
PR #93**, e **nenhuma execução pós-merge foi alegada ali**. Aquele baseline foi **superado
como baseline corrente** por esta reconciliação.

**Execuções auditadas da PR #91, registro daquela entrega** (2026-09-01, Python 3.14.5) —
**quatro execuções, todas aprovadas**, realizadas sobre os **bytes auditados da árvore de
trabalho**:

| Momento | Comando | Resultado |
|---|---|---|
| **direcionado** | `./.venv/Scripts/python.exe -m pytest tests/test_response_format.py` | **`319 passed`** |
| **direcionado estrito** | `./.venv/Scripts/python.exe -m pytest tests/test_response_format.py -W error` | **`319 passed`** |
| **suíte completa** | `./.venv/Scripts/python.exe -m pytest` | **`1908 passed`** |
| **suíte completa estrita** | `./.venv/Scripts/python.exe -m pytest -W error` | **`1908 passed`** |

**Zero failures e zero errors** nas quatro; **zero warnings** nas duas variantes estritas. O
delta é **+319** sobre os **`1589 passed`** do PR #89, **exatamente** o arquivo direcionado
**novo**: **nenhum teste preexistente foi alterado ou removido**. A **invariância dos bytes
testados** foi provada **mecanicamente** — SHA-256 dos dois arquivos conferido **antes e
depois** das quatro execuções, com o **mesmo valor** nas duas medições, e o *bytecode*
compilado pelo pytest registrando **mtime e tamanho idênticos** aos da fonte. **Antes do
commit**, o **conteúdo staged** foi verificado **mecanicamente** como **idêntico ao da árvore
de trabalho depois da normalização `CRLF → LF` aplicada pelo Git**, com a **superfície AST**
igual dos dois lados; e os **blobs integrados à `main` são exatamente os blobs staged
auditados** — `95f432a6…` para o módulo e `74385927…` para o teste, conferidos em
`origin/main` e no commit funcional.

Sobre a PR #91, registrado à época e **preservado**: **aquela** reconciliação **não
reexecutou a suíte**, por ser **exclusivamente documental**; as contagens eram as
**auditadas pela PR #91**. A árvore de trabalho testada estava em
**CRLF**; o **Git normalizou para LF no índice** (`core.autocrlf=true`, sem `.gitattributes`);
verificou-se **mecanicamente** que o **staged era idêntico à árvore de trabalho depois dessa
normalização**; e os **blobs integrados coincidem com os blobs staged auditados**. A
comparação de fim de linha foi **comprovada por `git ls-files --eol` para os arquivos
efetivamente inspecionados** — `src/casa77_sdr/response_format.py`,
`tests/test_response_format.py` e `src/casa77_sdr/response_equivalence.py`, todos com
**`i/lf w/crlf attr/`** —, e **nada é afirmado além desses três arquivos**. **Nenhuma
execução além das reportadas é alegada.**

**Execuções pós-merge do PR #89, preservadas como registro daquele momento** (2026-08-31,
Python 3.14.5): **`1589 passed`** na suíte completa, contra `origin/main`
`76531de7d3f4257d84b5a1f9498d8666c4e60030` — contagem **realmente obtida** naquela execução
pós-merge, **verificada e não presumida**, e **superada como baseline corrente** por esta
reconciliação. Também ali a variante `-W error` não foi executada.

**Execuções auditadas da PR #89, registro daquela entrega** (2026-08-31, Python 3.14.5) —
**quatro execuções, todas aprovadas**: **`153 passed`** no direcionado
`tests/test_response_equivalence.py`; **`153 passed`** no mesmo direcionado sob `-W error`;
**`1589 passed`** na suíte completa; e **`1589 passed`** na suíte completa sob `-W error`.
**Zero failures e zero errors** nas quatro. O delta é **+153** sobre os **`1436 passed`** do
PR #86, **exatamente** o arquivo direcionado novo: **nenhum teste preexistente foi alterado**.

**Execuções pós-merge do PR #86, preservadas como registro daquele momento** (2026-08-31,
Python 3.14.5): **`158 passed`** no direcionado de `tests/test_response_index.py`,
**`63 passed`** no de `tests/test_response_index_load.py` e **`1436 passed`** na suíte
completa — corretas **para aquele marco**, e **superadas como baseline corrente** por esta
reconciliação. Também ali a variante `-W error` não foi executada.

O direcionado de `E1` passou de **`159`** para **`158`** porque a PR #86 **removeu** o teste
`test_indice_real_continua_inexistente` — a inexistência do índice era **evidência temporária**
daquela entrega, não invariante permanente. **A remoção não criou o índice**, que **continua
INEXISTENTE**.

**Execuções pós-merge do PR #84, preservadas como registro daquele momento** (2026-08-31,
Python 3.14.5): **`159 passed`** no direcionado de `tests/test_response_index.py` e
**`1374 passed`** na suíte completa — corretas **para aquele marco**, e **superadas como
baseline corrente** por esta reconciliação. Também ali a variante `-W error` não foi executada.

**Execuções do PR #61, preservadas como registro histórico daquela entrega** (2026-08-25,
Python 3.14.5) — **três execuções finais aprovadas**: **`368 passed`** no direcionado de
`tests/test_interpretation.py`, **`1215 passed`** na suíte completa e **`1215 passed`** sob
`-W error`, com **zero failures, zero errors, zero skips e zero warnings** nas três.

**Nenhuma execução "pré-edição" é alegada para a PR #61**: a entrega não produziu uma
medição própria anterior às suas alterações. O ponto de comparação é o **baseline
funcional integrado anterior**, **`1167 passed`**, registrado pelo **PR #55**. O delta
**+48** corresponde **exatamente** ao crescimento do arquivo direcionado
(**`320 passed`** → **`368 passed`**): os demais **847** casos permanecem **intactos**.

**Execuções do PR #55, preservadas como registro histórico daquela entrega** (2026-08-23,
Python 3.14.5): **`320 passed`** no direcionado e **`1167 passed`** na suíte completa,
também confirmados sob `-W error`. **Nenhuma execução "pré-edição" foi alegada** para ela;
seu ponto de comparação era o baseline **`847 passed`** do **PR #49**.

**Execuções do PR #49, preservadas como registro histórico daquela entrega** (2026-08-22,
Python 3.14.5): **`795 passed`** na execução pré-edição, **`52 passed`** em
`tests/test_transition_marker_write.py` e **`847 passed`** na suíte completa — além de uma
**fase RED esperada** do ciclo TDD (`ModuleNotFoundError` antes de o módulo existir),
**distinta** dos resultados finais e **sem contagem de casos atribuída**.

A execução **pré-edição** da **PR #49** foi uma **execução real própria daquela entrega**,
ainda que coincidisse numericamente com o **baseline histórico** produzido pelo **PR #47**:
"baseline anterior = `795`" e "execução pré-edição da PR #49 = `795`" são **fatos
distintos**. Baselines **históricos** de entregas anteriores, preservados como tais: o
**PR #47** registrou **`759 passed`** na execução pré-edição, **`36 passed`** em
`tests/test_transition_marker.py` e **`795 passed`** na suíte completa; o **PR #44**
registrou **`257 passed`** em `tests/test_state_machine.py` e **`759 passed`** na suíte
completa; e o **PR #38** registrou **`87 passed`** em `tests/test_eligibility.py`,
**`65 passed`** em `tests/test_context.py` e **`749 passed`** na suíte completa. A suíte
cobre o carregador/validação da base (3B.1, `tests/test_knowledge.py`), as regras
comerciais determinísticas (3B.2, `tests/test_rules.py`), a persistência operacional em
memória (3B.3, `tests/test_persistence.py`), a normalização de entrada com a chave de
idempotência (3B.4, `tests/test_normalization.py`), a qualificação determinística (3B.5,
`tests/test_qualification.py`), a máquina de estados determinística (3B.6,
`tests/test_state_machine.py`) e a **resolução de identidade determinística** (3B.7,
`tests/test_identity.py`). A cobertura da persistência foi **ampliada pelo PR #33** com
o transporte e a validação de `instante_ultima_transicao`; o **PR #36** acrescentou
`tests/test_eligibility.py` — a **produção determinística do conjunto elegível E**; e o
**PR #38** acrescentou `tests/test_context.py` — a **montagem das projeções de
identidade da etapa 3**. O **PR #44** ampliou `tests/test_state_machine.py` com a
**projeção `transicoes_que_mudaram_estado`**. O **PR #47** acrescentou
`tests/test_transition_marker.py` — a **decisão determinística do marco temporal**. O
**PR #49** acrescentou `tests/test_transition_marker_write.py` — a **aplicação e a escrita
do marco temporal como fronteira chamável**. O **PR #55** acrescentou
`tests/test_interpretation.py` — a **fronteira determinística de N-b**: vocabulário fechado
de 11 intenções, derivação dos códigos **A1**, confiança calculada por **N-b-X3**,
canonicalização, erros recebíveis `E-Nb`, invariantes internos, prova estrutural de
`E-Nb-19`, projeção para a identidade e a **condição 5**. O **PR #84** acrescentou
`tests/test_response_index.py` — o **validador estrutural do futuro índice** (**`E1`**):
schema fechado, vocabulários fechados, exclusividade de origem, regras de `RENDERIZADO` e
`ASSERTIVA`, fail-closed na primeira violação, não-eco do valor recebido e rejeição de
seleção numericamente posicional, **inclusive após seletores textuais encadeados**. Esses
testes são **determinísticos e sem rede**: eles **não** exercitam LLM real, **não** exercitam
interpretação de texto livre, **não** exercitam WhatsApp e **não** constituem teste
ponta a ponta nem do pipeline operacional completo. Os de `E1` **não leem o índice real** —
que **não existe** — e operam sobre **estruturas sintéticas em memória**. O **PR #86**
acrescentou `tests/test_response_index_load.py` — o **carregador *fail-closed* do futuro
índice**: caminho como `Path` e como `str`, leitura UTF-8, arquivo inexistente, diretório no
lugar do arquivo, UTF-8 inválido, sintaxe YAML inválida, tag insegura, arquivo vazio, chave
duplicada nos **quatro** níveis, delegação real a `validar_indice` com categoria e localizador
preservados, não-eco de conteúdo por sentinela, `__cause__` encadeada, leitura pura provada por
*hash* do arquivo temporário e provas por **AST** sobre o módulo de produção. Esses testes
também **não leem o índice real** — que **não existe** — e usam **artefatos sintéticos em
`tmp_path`**. O **PR #89** acrescentou `tests/test_response_equivalence.py` — o **comparador
determinístico de equivalência textual de `C-15b`**: tipo não-`str`, `str` vazia, NFC, dobra da
quebra suave, preservação de parágrafo real, cada terminador proibido nos **dois** lados, `LF`
de borda, branco adjacente, precedência entre lados e ordem interna das violações, categorias e
localizadores, ausência de `strip`/`casefold`/*fuzzy*, não-eco de conteúdo por sentinela,
ausência de `__cause__` e `__context__`, e provas por **AST** sobre o módulo de produção. Esses
testes **não leem `knowledge/**`** e usam **fixtures 100% sintéticas**, com os caracteres de
controle escritos por **escape** no fonte. O **PR #91** acrescentou
`tests/test_response_format.py` — os **formatadores determinísticos de `C-6`**: recusa de
`bool`, `float`, `Decimal`, `None` e texto numérico pelos formatadores de inteiro; decimal
sem agrupamento; agrupamento de 3, 4, 6 e 7+ dígitos com separador `.`, sinal preservado,
zero interno preservado, ausência de zero de preenchimento e **round-trip estrutural**
provando o mesmo inteiro; independência de *locale* provada com variável de ambiente
alterada; código monetário suportado, não suportado, com variação de caixa, vazio e com
espaço, além da ausência de whitespace na saída; identidade exata do texto, com espaços,
tabs, quebras, Unicode **decomposto** e `str` vazia preservados; todas as cardinalidades da
lista — zero, um, dois, três e quatro ou mais —, ordem, conteúdo literal, pontuação interna,
**item vazio preservado**, item não-`str` recusado, `str` recusada como contêiner, `list` e
`tuple` equivalentes e entrada não mutada; `__all__` exato, assinaturas sem default,
não-exportação por `__init__.py`, **ausência de `formatar_hora`** e de literal de padrão de
hora; e provas por **AST** de pureza — imports mínimos, zero I/O, zero *locale*, zero
`casa77_sdr.*`, ausência de despachante por token de formato e desconhecimento do
consumidor. Esses testes **não leem `knowledge/**`** e usam **fixtures 100% sintéticas**,
com os caracteres Unicode combinantes e o espaço inquebrável escritos por **escape** no
fonte, e com números escolhidos para **não** coincidir com o conjunto de preço e capacidade
da base autoritativa. O **PR #93** acrescentou `tests/test_response_assertion.py` — o
**avaliador determinístico booleano de `ASSERTIVA`**: a **matriz completa** dos quatro casos
avaliáveis e a prova de que `EH_FALSO` é a negação exata de `EH_VERDADEIRO`; a recusa de
**`0`**, **`1`**, **`-1`**, outros inteiros, `float`, `Decimal`, `str` — inclusive
`"True"`/`"false"`/`""` —, `bytes`, `list`, `tuple`, `dict`, `set`, `None` e objeto
arbitrário, **incluindo objetos com `__bool__` e com `__eq__` customizados**, com as provas
explícitas de que **`0 == False`** e **`1 == True`** em Python e ainda assim **nenhum dos
dois é avaliável**; predicado válido, desconhecido, em minúscula, com variação de caixa, com
espaços, vazio e não-`str`, mais a prova de que **exatamente dois** predicados são aceitos; a
**ordem das três violações**, isolada e combinada; classe derivando **diretamente de
`Exception`**, categorias e localizadores exatos, primeira violação encerrando, **não-eco por
sentinela** e **não-eco do tipo concreto**, ausência de `__cause__` e de `__context__`;
`__all__` exato, assinatura de dois parâmetros sem default e não-exportação por
`__init__.py`; e provas por **AST** de pureza — imports fechados em `__future__`, zero
`casa77_sdr.*`, zero I/O, zero rede, zero *locale*, zero relógio ou calendário, zero variável
de ambiente, **ausência de chamada a `bool(...)`**, ausência de `strip`/`upper`/`casefold` e
desconhecimento de consumidor e de fronteira alheia. Esses testes **não leem
`knowledge/**`** e usam **fixtures 100% sintéticas**. O **PR #95** acrescentou
`tests/test_response_bijection.py` — o **verificador determinístico da correspondência
bijetiva**: os casos válidos — **três domínios vazios como bijeção trivial**, em `list` e em
`tuple`; cardinalidade **unitária** e **plural**; tokens dos dois domínios **totalmente
diferentes** ou **coincidentes**; **ordem dos pares e dos domínios irrelevante**; **determinismo
sob repetição** no sucesso e na falha; **token vazio como token**; conteúdo arbitrário; e
**ausência de exigência de formato `Rxx`** —; a **recusa de subclasse de `str`** nos **quatro
lugares**, com a prova de que a subclasse sintética **sequestra a igualdade**; a **recusa de
subclasse de `tuple`** como item, com a prova de que ela **mente sobre a forma**, e a recusa
de `list` como par; a **igualdade exata** — `NFC`/`NFD` como tokens **distintos**, caixa **não
tolerada**, espaço nas bordas **não removido**, igualdade de conteúdo **sem identidade de
objeto**; os **tipos de topo** — não-sequência, `Mapping`, gerador, `str`, `str` vazia,
`bytes` e `bytearray` recusados como contêiner —; os **tipos dos tokens**; a **estrutura dos
pares** — um lado, vazio, lado extra, origem/destino não-`str`, **origem precede destino**,
conferência **par a par na ordem recebida** —; as **duplicidades** nos domínios e na relação,
inclusive par idêntico repetido; as **referências desconhecidas**; a **cobertura incompleta**,
inclusive relação vazia sobre domínios não vazios; a **precedência global** entre todas as
etapas; a **superfície pública** — `__all__` exato, **três parâmetros sem default**, sem
parâmetro de modo ou tolerância, `BijecaoInvalida` derivando **diretamente de `Exception`**,
não-exportação por `__init__.py` e retorno `None` declarado —; a **segurança da mensagem** —
categoria e localizador **fechados**, **não-eco** de token, tipo concreto, número ou índice,
ausência de `__cause__` e de `__context__`, **argumento único** e **todas as categorias
alcançáveis** —; provas por **AST** de pureza — imports fechados, zero `casa77_sdr.*`, zero
import em função, zero I/O, *filesystem*, rede, processo, *locale*, ambiente, relógio,
calendário ou execução dinâmica, **ausência de normalização de token**, sem captura de
exceção, sem `raise from`, **sem cardinalidade fixa do corpus**, sem menção a caminho de
`knowledge`, sem `enum` nem `dataclass`, **uma única classe**, sem estado mutável de módulo,
`Sequence` como **única abstração importada**, verificação por **tipo exato** e não por
`isinstance`, e **sem conversão** de item ou token —; e a **imutabilidade das entradas** nos
caminhos válido, de falha e de token inválido, **sem acúmulo de estado** entre chamadas.
Esses testes **não leem `knowledge/**`** e usam **fixtures 100% sintéticas**.

**Baseline funcional atual: `2707 passed`.** Baseline anterior integrado: **`2446 passed`**
— delta **+261**, correspondente **exatamente** ao arquivo direcionado **novo**
`tests/test_response_status.py`; **nenhum teste preexistente foi alterado** pela PR #97. O
baseline **`2446 passed`** decorreu, por sua vez, do **PR #95**, com delta **+284**
correspondente **exatamente** ao arquivo direcionado **novo**
`tests/test_response_bijection.py`; **nenhum teste preexistente foi alterado** por ele. O
baseline **`2162 passed`** decorreu, por sua vez, do **PR #93**, com delta **+254**
correspondente **exatamente** ao arquivo direcionado **novo**
`tests/test_response_assertion.py`; **nenhum teste preexistente foi alterado** por ele. O
baseline **`1908 passed`** decorreu, por sua vez, do **PR #91**, com delta **+319**
correspondente **exatamente** ao arquivo direcionado **novo**
`tests/test_response_format.py`; **nenhum teste preexistente foi alterado** por ele. O
baseline **`1589 passed`** decorreu, por sua vez, do **PR #89**, com delta **+153**
correspondente **exatamente** ao arquivo direcionado **novo**
`tests/test_response_equivalence.py`; **nenhum teste preexistente foi alterado** por ele.
O baseline **`1436 passed`** decorreu, por sua vez, do **PR #86**, com delta **+62** sobre os
**`1374 passed`** do PR #84 — decomposto em **+63** casos de
`tests/test_response_index_load.py` e **−1** pela remoção do teste
`test_indice_real_continua_inexistente` de `tests/test_response_index.py`, que por isso passou
de **159** para **158**. O baseline **`1374 passed`** decorreu da **`E1`** (PR #84), com delta **+159**
sobre os **`1215 passed`** do PR #61 — este com delta **+48** sobre os **`1167 passed`** do
PR #55, que por sua vez teve delta **+320** sobre os **`847 passed`** do PR #49.

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
direcionado passou a **`257 passed`**. O salto de **`759 passed` para `795 passed`** —
**delta +36** — decorre exclusivamente do **PR #47**, que acrescentou
`tests/test_transition_marker.py` com **36** casos. O salto de **`795 passed` para
`847 passed`** — **delta +52** — decorre exclusivamente do **PR #49**, que acrescentou
`tests/test_transition_marker_write.py` com **52** casos; **nenhum** desses 52 é atribuído
a `tests/test_transition_marker.py`, que permanece com **36**, nem a
`tests/test_state_machine.py`, que permanece com **257**. O salto de **`847 passed` para
`1167 passed`** — **delta +320** — decorre exclusivamente do **PR #55**, que acrescentou
`tests/test_interpretation.py` com **320** casos; **nenhum** desses 320 é atribuído a
`tests/test_identity.py`, a `tests/test_qualification.py` ou a qualquer outro arquivo já
existente. Os baselines históricos
**`180`**, **`427`**, **`574`**, **`597`**, **`684`**, **`749`**, **`759`**, **`795`** e
**`847`** permanecem registrados como acima; a série completa é
**`180 → 427 → 574 → 597 → 684 → 749 → 759 → 795 → 847 → 1167`**.

Os PRs **#23** (R), **#25** (R-H), **#27** (R-I), **#31** (N-a), **#32**, **#34**, **#35**,
**#39**, **#40**, **#41**, **#42**, **#43**, **#45**, **#46**, **#48**, **#50**, **#51**,
**#52**, **#53** e **#54** (reconciliações, arbitragens e correções documentais) e a
presente reconciliação **não alteram código nem testes** e, portanto, **não alteram o
baseline**. Em particular, o **PR #41** alterou **apenas** `docs/00` e o **PR #42** alterou
**apenas** `docs/06` e `docs/07`; os **PRs #45, #46, #48, #50 e #52** alteraram **apenas**
`docs/00`; os **PRs #51** — arbitragem **N-b** — e **#53** — micro-arbitragem **AJ1** —
alteraram **apenas** `docs/07`; e o **PR #54** alterou **apenas** `docs/00` — **nenhum
deles** tocou `src/` ou `tests/` e **nenhum alterou o baseline**. **Nem a arbitragem N-b nem
a micro-arbitragem AJ1 criaram teste algum**: os **cenários K-Nb-1–K-Nb-40** são
**conceituais** e vivem em `docs/07` §8.2 — e **AJ1 apenas classificou o alcance de prova**
de **K-Nb-18**, **K-Nb-34** e **K-Nb-39**, **sem criar, alterar ou executar teste**. Foi o
**PR #55** que, depois, materializou esses cenários em `tests/test_interpretation.py`. As
**três execuções finais registradas acima foram realizadas e auditadas antes do merge do
PR #55**, em 2026-08-23. **Nenhuma execução de testes ocorre nesta reconciliação**, que é
puramente documental, e nenhuma execução além das reportadas é alegada.

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

Existem agora **vinte e cinco entregas funcionais posteriores à 3B.7 e SEM numeração oficial de
subetapa**: (a) a **evolução temporal do contrato de persistência operacional**
(`instante_ultima_transicao`), integrada pelo **PR #33**; (b) a **implementação
funcional da política N-a** — produção determinística do conjunto elegível **E** em
`src/casa77_sdr/eligibility.py` —, integrada pelo **PR #36**; (c) a **montagem
determinística das projeções de identidade da etapa 3** — fronteira **etapa 3 →
identidade/etapa 5** em `src/casa77_sdr/context.py` —, integrada pelo **PR #38**;
(d) a **materialização em runtime da projeção `transicoes_que_mudaram_estado`** na
`MaquinaEstados` / `DecisaoMaquina`, integrada pelo **PR #44**; (e) a **decisão
determinística do marco temporal** — `decidir_instante_ultima_transicao(...)` e a
**composição decisória das 0–3 `DecisaoMaquina`** em
`src/casa77_sdr/transition_marker.py` —, integrada pelo **PR #47**; (f) a **aplicação e
a escrita do marco temporal como fronteira chamável** —
`criar_com_marco_de_transicao(...)` e `gravar_com_marco_de_transicao(...)` em
`src/casa77_sdr/transition_marker_write.py` —, integrada pelo **PR #49**; e (g) a
**materialização da parte determinística de N-b** — a **fronteira determinística** da
interpretação da etapa 4 em `src/casa77_sdr/interpretation.py`, com a **canonicalização da
`Interpretacao`**, o **`A1` derivado** com **confiança calculada por N-b-X3**, a
**projeção** para a `ProjecaoInterpretacao` e a **condição 5** —, integrada pelo
**PR #55**; (h) a **materialização funcional do delta AJ2** — o **assunto** de
`PerguntaComercial` na fronteira determinística, em `src/casa77_sdr/interpretation.py` —,
integrada pelo **PR #61**; e (i) a **`E1` — validador estrutural do futuro índice de
respostas aprovadas** em `src/casa77_sdr/response_index.py`, **primeira microentrega
funcional de `C`**, integrada pelo **PR #84**; e (j) a **segunda microentrega funcional de
`C`** — o **carregador *fail-closed* do futuro índice** em
`src/casa77_sdr/response_index_load.py` —, integrada pelo **PR #86**; e (k) a **terceira
microentrega funcional de `C`** — o **comparador determinístico de equivalência textual de
`C-15b`** em `src/casa77_sdr/response_equivalence.py` —, integrada pelo **PR #89**; e (l) a
**quarta microentrega funcional de `C`** — os **formatadores determinísticos de apresentação
pura de `C-6`** em `src/casa77_sdr/response_format.py` —, integrada pelo **PR #91**; e (m) a
**quinta microentrega funcional de `C`** — o **avaliador determinístico booleano de
`ASSERTIVA`** em `src/casa77_sdr/response_assertion.py` —, integrada pelo **PR #93**; e (n) a
**sexta microentrega funcional de `C`** — o **verificador determinístico da correspondência
bijetiva de `C-A1-B3` / `C-A1-B4`** em `src/casa77_sdr/response_bijection.py` —, integrada
pelo **PR #95**; e (o) a **sétima microentrega funcional de `C`** — o **canonicalizador
determinístico de rótulo de status já extraído** em `src/casa77_sdr/response_status.py` —,
integrada pelo **PR #97**; e (p) a **oitava microentrega funcional de `C`** — o
**leitor/validador determinístico da representação marcada `C-A5`** em
`src/casa77_sdr/response_markdown_units.py` —, integrada pelo **PR #102**; e (q) a **nona
microentrega funcional de `C`** — o **derivador determinístico dos tokens canônicos do lado do
índice** em `src/casa77_sdr/response_index_tokens.py` —, integrada pelo **PR #104**; e (r) a
**décima microentrega funcional de `C`** — a **composição determinística em memória da
correspondência canônica** em `src/casa77_sdr/response_correspondence.py` —, integrada pelo
**PR #106**; e (s) a **décima primeira microentrega funcional de `C`** — a **extração
determinística do texto emitível canônico** em `src/casa77_sdr/response_emittable_text.py` —,
integrada pelo **PR #109**; e (t) a **décima segunda microentrega funcional de `C`** — a
**extração determinística do rótulo literal de status do cabeçalho `Rxx`** em
`src/casa77_sdr/response_header_labels.py` —, integrada pelo **PR #113**; e (u) a **décima
terceira microentrega funcional de `C`** — a **propagação pura e determinística de status
`ST1`–`ST3` aos fragmentos já associados** em
`src/casa77_sdr/response_status_propagation.py` —, integrada pelo **PR #115**; e (v) a
**décima quarta microentrega funcional de `C`** — o **leitor/validador determinístico de status
por fragmento sob `PARCIAL`** em `src/casa77_sdr/response_fragment_status.py` —, integrada pelo
**PR #120**.
**Nenhuma das catorze materializa `C`**: o índice `knowledge/indice-respostas-aprovadas.yaml`
**continua inexistente**, o carregador **não conhece caminho implícito** para ele, o
comparador **opera sobre `str` que lhe são entregues**, sem analisar Markdown e sem I/O, os
formatadores **recebem valores já resolvidos**, sem consultar fonte alguma, o avaliador
**recebe predicado e valor já prontos**, julgando **apenas o domínio booleano estrito**, o
verificador **recebe os três domínios já prontos**, julgando **apenas se a relação é bijetiva
entre eles**, e o canonicalizador **recebe o rótulo já extraído**, traduzindo **apenas as três
linhas de `C-A1-ST1`–`C-A1-ST3`**, o leitor da representação marcada **devolve apenas
tokens `<Rxx>/<id>`**, o derivador **projeta tokens de uma estrutura já em memória**, a
composição **compõe fronteiras já existentes sem juiz novo**, o extrator de texto **recebe a
representação marcada já em memória e devolve texto canônico, sem comparar e sem `NFC`** e o
extrator de rótulos **recebe a representação marcada já em memória e devolve o rótulo literal
de cada cabeçalho `Rxx`, sem canonicalizar, sem propagar e sem resolver `PARCIAL`**, e o
propagador **recebe um rótulo já identificado e fragmentos já associados pelo chamador,
aplicando uniformemente o status canônico de `ST1`–`ST3` sem ler Markdown, sem compor C8, C11
ou C12 e sem resolver `PARCIAL`**, e o leitor de status por fragmento **lê o que já está
declarado sob uma seção rotulada `PARCIAL`, sem aplicar status, sem alterar o corpus e sem
resolver `PARCIAL` nele** —
em todos os casos **sem consumidor integrado**. O formato
**`hora` continua NÃO MATERIALIZADO**, **`PARCIAL` continua sem tradução automática** e a
**autoridade de status continua em `knowledge/respostas-aprovadas.md`** (**C-11**).
Nenhuma delas é renomeada para **3B.8** — **a 3B.8 não existe** —, nenhuma **altera a
numeração** do roadmap e nenhuma **significa que a próxima entrega tenha sido
escolhida**. A **última subetapa funcional numerada** continua sendo a **3B.7**.

**Estado funcional do produto.** Estão **implementados**: a **produção determinística de
E**; a **projeção integral reutilizável** dos registros recuperados; a **validação
explícita do limiar**; o conjunto **H**; o **`havia_estado_esperado`**; o **produtor
N-I** / `id_atendimento_validado`; a **montagem da fronteira etapa 3 →
identidade/etapa 5**; a **projeção `transicoes_que_mudaram_estado`**; a **decisão pura
do marco temporal** com a **composição decisória das 0–3 chamadas** do ciclo; e a
**aplicação do valor decidido sobre um `RegistroAtendimento` recebido pronto** com a
**escrita efetiva** via `PersistenciaOperacional.criar(...)` ou
`PersistenciaOperacional.gravar(...)`, como **fronteira chamável**; e — pelo **PR #55** — a
**fronteira determinística de N-b**, com a **canonicalização da `Interpretacao`**, a
**derivação dos seis códigos `A1`** e sua **confiança calculada** por **N-b-X3**, a
**projeção para a `ProjecaoInterpretacao`** e a **condição 5** de `docs/07` §4.4.
**Continuam NÃO implementados, parciais ou NÃO integrados**: o **produtor não
determinístico / LLM** da etapa 4 e a **interpretação real de texto livre**; **N-b-RES2** —
a transformação posterior dos sinais interpretados em **eventos confirmados**; a
**integração operacional da etapa 4** no pipeline; a **integração operacional
da etapa 13 no pipeline** — inclusive a **montagem completa** do `RegistroAtendimento`, a
**decisão de se a etapa 13 executa**, a **escolha entre criar e gravar**, a **geração de
`id_atendimento`**, a **criação operacional** do atendimento, a **marcação de
idempotência** e a **preservação de pendente** —; o **tratamento operacional de falha**
(S4, S5); o **destino do alerta operacional**; a **etapa 3 inteira**; a **persistência
não volátil**; a **integração completa do pipeline**; e o **`OrquestradorMotor`**.
**N-a-T3–N-a-T7 não estão operacionalmente concluídas.**

**Nenhuma subetapa 3B.8 foi escolhida, proposta ou autorizada por esta entrega.** A
reconciliação anterior foi **integrada e auditada** pelos **PRs #39** e **#41**; o estado de
**N-a** em `docs/07` foi **reconciliado pelo PR #40**; e a **projeção de mudança de estado**
foi **arbitrada pelo PR #42** — **contrato definido naquele momento** e **materializado**
**depois pelo PR #44**. O GPT reavalia a próxima subetapa **à luz das pendências ainda abertas**, e
**nenhuma delas é eleita aqui**. Em particular, **não** se afirma aqui que
o `OrquestradorMotor` seja a próxima implementação autorizada. A formulação genérica
anterior — "bloqueado por N-a, N-b, E4 e S2-D8" — deixa de valer para **N-a** e para **N-b** — ambas **arbitradas documentalmente** —, e passa a
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
- **N-a-T3–N-a-T7 — decisão: MATERIALIZADA** pelo **PR #47**
  (`src/casa77_sdr/transition_marker.py`, `docs/07` §6.2, M-DT1–M-DT7): a **decisão pura**
  de inicializar, atualizar ou preservar o marco e a **composição decisória das 0–3
  `DecisaoMaquina`** do ciclo **já existem em código**.
- **N-a-T3–N-a-T7 — aplicação e escrita: MATERIALIZADAS COMO FRONTEIRA CHAMÁVEL** pelo
  **PR #49** (`src/casa77_sdr/transition_marker_write.py`, `docs/07` §6.2, M-AE1–M-AE7):
  `criar_com_marco_de_transicao(...)` e `gravar_com_marco_de_transicao(...)` **delegam** a
  decisão, **aplicam** o valor decidido sobre um `RegistroAtendimento` **recebido pronto**
  — alterando **somente** `instante_ultima_transicao` — e **escrevem** por
  `PersistenciaOperacional.criar(...)` ou `PersistenciaOperacional.gravar(...)`.
  `src/casa77_sdr/persistence.py` **permanece inalterado**. Isso **não** conclui
  operacionalmente N-a-T3–N-a-T7.
- Pré-requisitos concretos **ainda pendentes** da N-a, conforme `docs/07` §6.2 e §12: a
  **integração operacional da etapa 13 no pipeline** — a **montagem completa** do
  `RegistroAtendimento`, a **decisão de se a etapa 13 executa**, a **escolha entre criar e
  gravar**, a **geração de `id_atendimento`**, a **criação operacional** do atendimento, a
  **marcação de idempotência** e a **preservação de pendente** —, de modo que
  **N-a-T3–N-a-T7 não estão operacionalmente concluídas**; o **tratamento operacional dos
  bloqueios** (S4, S5); o **destino do alerta operacional**; e o **valor numérico do
  limiar** com o **mecanismo concreto de carga** da configuração. **Todos continuam não
  implementados/pendentes.**
- **N-b — especificação documental: ARBITRADA / CONCLUÍDA** pelo **PR #51** (`docs/07`
  §6.3): o **contrato global da `Interpretacao` da etapa 4** está fechado, com a derivação
  para a `ProjecaoInterpretacao`, a **condição 5** de §4.4 e a **fronteira conceitual do
  produtor**. A **micro-arbitragem AJ1**, integrada pelo **PR #53**, fechou adicionalmente a
  **representação e a canonicalização determinística** que antecedem a materialização —
  **`A1` derivado e com confiança calculada**, **precedência `E-Nb-3` × `E-Nb-5`**,
  **classificação dos 19 erros**, **alcance de prova** de `K-Nb-18`/`K-Nb-34`/`K-Nb-39`,
  estratégia estrutural de `E-Nb-19` e reutilização por **import** de `FormatoEvento`.
  Deixou de ser bloqueador de **especificação**. **Implementação: PARCIAL.** A **fronteira
  determinística foi materializada e integrada pelo PR #55**, em
  `src/casa77_sdr/interpretation.py` — canonicalização da `Interpretacao`, derivação de
  **A1**, confiança por **N-b-X3**, projeção para a identidade e **condição 5**.
  **Permanecem pendentes**: o **produtor não determinístico / LLM**; a **interpretação real
  de texto livre**; **N-b-RES2** — a transformação posterior de sinais interpretados em
  **eventos confirmados**, ainda **sem produtor concreto** e **sem identificador de
  pendência novo**; e a **integração operacional da etapa 4** no pipeline. **N-b-RES1** (a
  etapa 4 **não emite `Exx`**) e **N-b-RES3** (classificação do residual) permanecem
  **regras fechadas**.
- **E4**, **S2-D8** e **S3-D1** **continuam abertas** e continuam bloqueando o
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

1. A **sétima microentrega funcional de `C`** — o **canonicalizador determinístico de rótulo
   de status já extraído**, em `src/casa77_sdr/response_status.py` — está **funcionalmente
   concluída e integrada à `main`** pelo **PR #97** (**MERGED**). Ela **não recebeu numeração
   de subetapa** e **não criou nomenclatura normativa `E2`–`E7`**. A **entrega funcional
   anterior** é a **sexta microentrega — o verificador determinístico da correspondência
   bijetiva de `C-A1-B3` / `C-A1-B4`** (PR #95), que permanece integrada. **A entrega
   funcional mais recente NÃO é mais a do PR #97**: desde o **PR #131** ela é o **parser puro
   e determinístico da gramática de `caminho_yaml`**, em
   `src/casa77_sdr/response_yaml_path.py`, registrado no **item 108** — que **não** é
   denominado `C15`, `E15` nem `C-A6`; a **entrega funcional imediatamente anterior** é a
   **composição total determinística de status dos fragmentos emitíveis**, em
   `src/casa77_sdr/response_status_composition.py` (PR #127), registrada no **item 106**; a
   **associação física determinística de seção e fragmentos** está em
   `src/casa77_sdr/response_section_membership.py` (PR #124), registrada no **item 104**; a **décima
   quarta microentrega funcional de `C`** é o leitor/validador determinístico de status por
   fragmento sob `PARCIAL`, em `src/casa77_sdr/response_fragment_status.py` (PR #120),
   registrada no **item 102**; a **décima terceira** é a propagação pura e determinística de status
   `ST1`–`ST3` aos fragmentos já associados, em
   `src/casa77_sdr/response_status_propagation.py` (PR #115), registrada no **item 98**; a
   **décima
   segunda** é a extração determinística do rótulo literal de status do cabeçalho `Rxx`, em
   `src/casa77_sdr/response_header_labels.py` (PR #113), registrada no **item 97**; a **décima
   primeira** é a extração determinística do texto emitível
   canônico, em `src/casa77_sdr/response_emittable_text.py` (PR #109), registrada no **item
   94**; a **décima** é a composição determinística em memória da correspondência canônica, em
   `src/casa77_sdr/response_correspondence.py` (PR #106), registrada no **item 92**; a
   **nona** é o derivador determinístico dos tokens canônicos do lado do índice, em
   `src/casa77_sdr/response_index_tokens.py` (PR #104), registrada no **item 91**; e a
   **oitava** é o leitor/validador determinístico da representação marcada `C-A5`, em
   `src/casa77_sdr/response_markdown_units.py` (PR #102), registrada no **item 90**.
   **Nenhuma das catorze microentregas materializa
   `C`**: o índice `knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE** e
   **`C` continua ARBITRADA / NÃO MATERIALIZADA como entrega completa**. **CANONICALIZAR
   STATUS NÃO É MATERIALIZAR `C`**: o canonicalizador **recebe o rótulo já extraído** — **a
   origem correta do rótulo é pré-condição do chamador** — e traduz **somente as três linhas
   com tradução automática arbitrada** em `C-A1-ST1`–`C-A1-ST3`: `APROVADO` → `APROVADO`,
   `AGUARDA APROVAÇÃO` → `AGUARDA_APROVACAO` e `APROVADO com handoff obrigatório` →
   `APROVADO`, **sem transportar o sufixo de handoff** (C-2f, C-5.1). O rótulo precisa ser
   `str` **exata** — **subclasse de `str` é recusada antes de qualquer consulta à tabela** —,
   a **comparação é literal**, com **zero normalização, zero coerção e zero tolerância**, e a
   validação é **fail-closed** com precedência **tipo → pertença → retorno**. A função **não
   extrai rótulo do Markdown**, **não extrai fragmento**, **não decide emissibilidade**,
   **não cria identidade física de fragmento**, **não cria nem lê o índice real**, **não
   resolve *bindings***, **não executa a bijeção física**, **não prova completude do corpus**,
   **não satisfaz `C-A1-ST6`–`C-A1-ST10`**, **não migra a autoridade de status** e **não
   integra consumidor**. **`PARCIAL` continua SEM tradução automática** e **continua exigindo
   mapeamento explícito no nível dos fragmentos emitíveis** (`C-A1-ST4`); **`BLOQUEADO` não
   recebeu mapeamento inventado** (`C-A1-ST5` trata de **nota interna**, que não cria
   fragmento nem status). **A autoridade de status NÃO migrou**:
   `knowledge/respostas-aprovadas.md` continua a autoridade (**C-11**). O formato **`hora`
   continua NÃO MATERIALIZADO**, por **lacuna normativa ainda não arbitrada** sobre a escolha
   mecânica entre `HH:MM` e `Hh` (`C-A1-F3`) — **e esta reconciliação não a arbitra**.
2. Commit funcional atual: `cee95ebb6a725c3b91595589591fefa650d64196` (PR #131). Merge
   correspondente: `6ae5cd829bb6eb9f4acfc60a061ee9b7e6d36180`. O par
   `24d2b0fef6a08c26e751f8eb8bb70943b30c0339` / `00c45e9b95f233bc7aa0f9666e090208994fb190`
   (PR #127), registrado aqui anteriormente, **permanece correto como registro daquele
   momento**.
3. Baseline funcional atual: **`4741 passed`**, com **`147 passed`** no teste direcionado de
   `tests/test_response_yaml_path.py`, em **Python 3.14.5** — **zero failures e zero
   errors**, e **zero warnings** sob `-W error`. Baseline anterior integrado: **`4594
   passed`**; delta **+147**, correspondente exatamente ao arquivo direcionado **novo**,
   **sem alteração de teste preexistente**. As execuções — **`147`** e **`4741`**, ambas sob
   `-W error` — foram **medidas na entrega funcional do PR #131, antes do merge**, sobre os
   bytes que vieram a ser exatamente os blobs integrados, e **reexecutadas com os mesmos
   números imediatamente antes do merge**; **nenhum `pytest` foi executado nesta
   reconciliação**. O registro anterior deste item — **`4594 passed`** / **`117 passed`** do
   PR #127 — **permanece correto como registro daquele momento**; ver a seção **Testes**.
4. A **última subetapa funcional numerada** continua sendo a **3B.7 — `ResolvedorIdentidade` determinístico** (PR #29, commit `25ab2726…`, merge
   `568919f5…`), que permanece **CONCLUÍDA**.
5. **O conjunto H, o `havia_estado_esperado` e o produtor N-I continuam com produtor em
   código**: `context.py` constrói **H** por filtro estrutural de estado **fora de N-a**,
   calcula `havia_estado_esperado` sobre o **contexto recuperado** — **nunca** sobre E —
   e projeta `id_atendimento_validado` **somente** sob `ENCONTRADO`.
6. **A fronteira de identidade da etapa 3 continua materializada**: leitura **somente de
   consulta** da persistência, validação do identificador, projeção integral do contexto
   e entrega do DTO fechado `ProjecoesIdentidadeEtapa3`, na ordem normativa de
   `docs/07` §6.2 — inclusive o **passo 12 antes do passo 13**.
7. **A produção determinística de E continua implementada** (PR #36), separada em
   **seleção** e **canonicalização**, com `produzir_conjunto_elegivel(...)` preservado
   como composição compatível. **O transporte e a validação de
   `instante_ultima_transicao` continuam implementados** na persistência (PR #33), que
   **não foi alterada** pelo PR #49.
8. **A DECISÃO, a APLICAÇÃO e a ESCRITA de `N-a-T3`–`N-a-T7` estão materializadas; a
   INTEGRAÇÃO OPERACIONAL não.** Decidir **qual valor** de `instante_ultima_transicao`
   usar — inicializar na criação, atualizar havendo mudança ou preservar o marco — existe
   em código desde o **PR #47**, com a **composição das 0–3 chamadas** do ciclo;
   **aplicar** esse valor sobre um `RegistroAtendimento` **recebido pronto** e
   **escrevê-lo** por `PersistenciaOperacional.criar(...)` ou
   `PersistenciaOperacional.gravar(...)` existe em código desde o **PR #49**, como
   **fronteira chamável** (`docs/07` §6.2, **M-AE1–M-AE7**). Continuam **NÃO
   implementados ou NÃO integrados**: a **montagem completa** do `RegistroAtendimento`;
   a **decisão de se a etapa 13 executa**; a **escolha entre criar e gravar** no pipeline;
   a **geração de `id_atendimento`**; a **criação operacional** do atendimento; a
   **marcação de idempotência**; a **preservação de pendente**; o **tratamento
   operacional de falha** (S4, S5); e o **destino do alerta operacional**. **A etapa 13
   NÃO está integrada** e **N-a-T3–N-a-T7 não estão operacionalmente concluídas.**
9. **A etapa 3 NÃO está inteiramente implementada** e **a integração N-a continua
   PARCIAL.** Continuam **não implementados** o **tratamento operacional dos bloqueios**
   (S4, S5) e o **destino do alerta operacional**. **Produzir as projeções de identidade
   não é implementar a etapa 3 inteira**, e **poder escrever o marco por uma fronteira
   chamável não é ter a etapa 13 integrada.**
10. O **`OrquestradorMotor` continua NÃO implementado** e **nenhuma integração completa
    de pipeline foi iniciada**.
11. Continuam **pendentes** o **valor numérico operacional do limiar**, o **mecanismo
    concreto de carga** da configuração e a **persistência operacional não volátil**.
12. **Nenhuma subetapa 3B.8 foi criada, escolhida ou autorizada.** A **3B.8 não existe**.
13. **N-b está ARBITRADA e PARCIALMENTE MATERIALIZADA.** A **fronteira determinística**
    passou a incluir também o **delta AJ2** desde o **PR #61** (item 25); tudo o que este
    item registra abaixo sobre o **PR #55** permanece **correto como registro daquela
    entrega**, que era **anterior a AJ2**. A **especificação** foi fechada
    pelo **PR #51** — contrato global da **`Interpretacao` da etapa 4** —, alterando
    **exclusivamente** `docs/07-arquitetura-motor-respostas.md` (**365 adições / 8
    remoções**), commit documental `6f1cb6fe…`, merge `85dbc709…`; **aquele PR não criou
    código algum**. A **parte determinística** foi **materializada e integrada depois**,
    pelo **PR #55**, em `src/casa77_sdr/interpretation.py`: `EntradaInterpretacao`
    pré-canônica, `Interpretacao` canônica, `IntencaoConversacional` com **11** valores,
    **`A1` derivado**, **confiança `A1` calculada**, `canonicalizar_interpretacao(...)`,
    `projetar_para_identidade(...)` e
    `decidir_interesse_confirmar_disponibilidade(...)`. **Continuam NÃO implementados**: o
    **produtor não determinístico / LLM**; a **interpretação real de texto livre** — o bot
    **não** interpreta texto livre e **nenhuma mensagem real pode ser testada via LLM**; a
    **integração operacional da etapa 4**; e o **`OrquestradorMotor`**. **`N-b-RES2`
    permanece ABERTO.** N-b **deixou de ser pendência de ESPECIFICAÇÃO** e **permanece
    pendente como IMPLEMENTAÇÃO PARCIAL** — **não** é correto dizer que N-b está concluída
    nem que a etapa 4 é funcional.
13a. **A micro-arbitragem AJ1 está APROVADA e INTEGRADA à `main` pelo PR #53**, e **fechou
    apenas a canonicalização documental**. Ela alterou **exclusivamente**
    `docs/07-arquitetura-motor-respostas.md` (**156 adições / 1 remoção**), commit
    documental `d1137cf6…`, merge `2e9df1f4…`. **AJ1 não implementou a `Interpretacao`, não
    tornou a etapa 4 funcional, não criou produtor LLM, não criou componente e não criou
    subetapa** — seu contrato foi **materializado depois pelo PR #55**, na parte
    determinística. O que ela fecha: **`A1` não é entrada semântica independente** — presença
    **derivada** do payload autoritativo e confiança **calculada** por **N-b-X3** —; o
    **slot autônomo** restrito aos **cinco** códigos **A2/B**; a **precedência `E-Nb-3` ×
    `E-Nb-5`**; a **classificação** dos **19** erros; o **alcance de prova** de
    **K-Nb-18**, **K-Nb-34** e **K-Nb-39**; a **estratégia estrutural** de `E-Nb-19`; e a
    **reutilização por import** de `FormatoEvento`, decisão **efetivada** pelo PR #55.
    **A condição 5 já possuía produtor conceitualmente atribuído** por N-b —
    o PR #55 apenas o **materializou** —, e as condições **2**, **4** e **8**
    continuam as **únicas NÃO ATRIBUÍDAS**. **N-b-RES1** (a etapa 4 **não emite `Exx`**) e
    **N-b-RES3** (classificação do residual) são **regras fechadas**; **N-b-RES2** — a
    **transformação posterior** de sinal interpretado em **evento confirmado** — permanece
    o **residual explícito ABERTO**, **sem identificador de pendência novo**.
14. **A projeção de mudança de estado EXISTE em runtime.** O **PR #42** arbitrou o
    contrato e o **PR #44 o materializou**: `DecisaoMaquina` expõe
    **`transicoes_que_mudaram_estado: tuple[Transicao, ...] = ()`** e a **`MaquinaEstados`
    é a fonte autoritativa** — a informação nasce dentro dela, no instante da aplicação de
    cada `Txx`. Cada transição é classificada contra o **estado intermediário imediatamente
    anterior à própria aplicação**; a saída **preserva a ordem** e é **subsequência de
    `caminho`**; **T35 é coberta dinamicamente** pela regra genérica; **sem** *replay*
    externo, **sem** usar `estado_inicial != estado_final` como algoritmo de produção,
    **sem** tabela paralela e **sem** lista normativa de transições que preservam estado.
    **Ela deixou de ser pendência de implementação.**
15. **A composição entre as até três chamadas do ciclo e a aplicação/escrita do marco
    DEIXARAM de ser pendências de materialização**: a composição foi materializada pelo
    **PR #47**, junto da decisão pura, e a aplicação com a escrita pelo **PR #49**, como
    fronteira chamável. **Decidir o valor do marco não é escrevê-lo, e poder escrevê-lo
    não é tê-lo integrado ao pipeline**: o que resta é a **integração operacional da
    etapa 13**, enumerada no item 8, além da **persistência não volátil**, do
    **`OrquestradorMotor`** e da **integração completa do pipeline**.
16. **A base factual reconciliada nesta entrega é o merge `ba412502…`.** A reconciliação
    de `docs/00` após o **PR #53** foi **integrada pelo PR #54** (commit documental
    `0f67e7f4…`, merge `3740a121…`) — **documental**, **exclusivamente**
    `docs/00-estado-atual.md`, **170 adições / 37 remoções**, **sem marco funcional
    novo**. A **materialização da parte determinística de N-b** foi **integrada pelo
    PR #55** (commit funcional `3f24e216…`, merge `ba412502…`) — **funcional**, em
    **três** arquivos, **3129 adições / 1 remoção**. O **marco funcional passa a ser o do
    PR #55**; o do **PR #49** (`d621a2c7…` / `f82da69f…`) torna-se o **anterior**.
17. A presente entrega é **exclusivamente reconciliação documental de
    `docs/00-estado-atual.md`** após o merge do **PR #55**: **não altera código, testes,
    `docs/07`, `docs/06`, `docs/05`, base de conhecimento nem prompts**, e **nenhuma
    execução de testes ocorre nela** — os números funcionais registrados são os
    **`320 passed`** / **`1167 passed`** executados e auditados em **Python 3.14.5** antes
    do merge do **PR #55**.
18. **A arbitragem técnica da materialização determinística de N-b foi realizada,
    integrada e efetivamente materializada**: o **contrato global** pelo **PR #51**, a
    **representação/canonicalização** pelo **PR #53** (**AJ1**) e a **implementação da
    fronteira determinística** pelo **PR #55**. **Esta reconciliação não implementa nada**
    e **não autoriza código por si só**; nenhum rótulo novo é criado e nenhuma numeração é
    atribuída.
19. **Próxima ação:** **esta reconciliação não escolhe a próxima entrega funcional.** A
    decisão pertence à **orquestração/auditoria posterior do GPT**, conforme a governança
    do projeto. **Nenhuma pendência é eleita aqui** como a implementação seguinte — nem o
    **produtor não determinístico / LLM**, nem **N-b-RES2**, nem a **integração operacional
    da etapa 4**, nem a **integração operacional da etapa 13**, nem **E4**, nem **S2-D8**,
    nem **S3-D1**, nem o `OrquestradorMotor`, nem qualquer outra. **Nenhuma numeração nova
    é criada** e a **3B.8 continua não existindo**.
20. As pendências permanecem abertas conforme seus próprios bloqueios: **B**, **C** —
    esta com o **contrato ARBITRADO** em `docs/07` §2.3 e **NÃO MATERIALIZADA**, aberta
    como materialização —, **S2-D8** — esta, **a partir desta entrega**, também com o
    **contrato ARBITRADO** em `docs/07` §4.4.1 e **NÃO MATERIALIZADA**, aberta **somente
    como materialização** (item 23) —, **S2-D5,
    S2-D7, S3-D1, a confirmação de entrega do handoff, E1, E3, E4, o retorno
    do controle ao bot após `atendimento_humano` sem `E14`/T34**, a **unicidade geral
    de `id_atendimento` entre candidatos não identificados**, a **persistência
    operacional não volátil**, a **montagem completa do `RegistroAtendimento`**, a
    **decisão de execução da etapa 13**, a **escolha entre criar e gravar no pipeline**,
    a **geração/origem de `id_atendimento`**, a **criação operacional do atendimento**, a
    **idempotência**, a **preservação de pendente**, o **tratamento operacional dos
    bloqueios (S4/S5)**, o **destino do alerta operacional**, o **valor numérico
    operacional do limiar** e o **mecanismo concreto de carga** da configuração. **N-b
    permanece aberta como IMPLEMENTAÇÃO PARCIAL** — a fronteira determinística existe desde
    o PR #55, mas o **produtor não determinístico / LLM**, a **interpretação real de texto
    livre** e a **integração operacional da etapa 4** continuam pendentes —, e a
    **transformação posterior dos sinais interpretados em eventos confirmados**
    (**N-b-RES2**) permanece como **residual explícito aberto de integração**, **sem
    identificador de pendência novo**. **Nem a AJ1 nem o PR #55 resolveram qualquer outra
    pendência da lista acima**: nenhuma é removida, reclassificada ou fechada.
    Nenhuma delas é resolvida aqui.
21. **A arbitragem C está INTEGRADA À `main` pelo PR #57** — commit documental
    `2ba5a283…`, merge `89458bb7…`, branch de origem `docs/arbitragem-c-indice-respostas`,
    **exclusivamente** `docs/00-estado-atual.md` e `docs/07-arquitetura-motor-respostas.md`,
    **401 adições / 6 remoções**. **C continua ARBITRADA / NÃO MATERIALIZADA**: o contrato
    documental existe (`docs/07` §2.3), o índice
    `knowledge/indice-respostas-aprovadas.yaml` **não existe**,
    `knowledge/respostas-aprovadas.md` **não foi convertido** e **nenhum status foi removido
    do Markdown**. A reconciliação anterior foi integrada pelo **PR #56** (merge
    `86258cfe…`), também documental.
22. **A micro-arbitragem AJ2 está ARBITRADA e, desde o PR #61, MATERIALIZADA na
    fronteira determinística** (item 25). O que este item registra abaixo descreve a
    **arbitragem documental** integrada pelo **PR #58** e continua **correto como registro
    daquele momento** — inclusive a afirmação, verdadeira **à época**, de que o delta ainda
    não estava materializado. Ela **ESTENDE
    FORMALMENTE N-b** (`docs/07` §6.3): `PerguntaComercial` passa conceitualmente de dois
    para **três** campos, com **`assunto`** obrigatório do enum fechado
    **`AssuntoComercial`** de **54** valores — **53 específicos + `ASSUNTO_NAO_CLASSIFICADO`**
    —, **sem confiança própria**; `E-Nb-5` é **ampliado** e a lista permanece
    **`E-Nb-1`–`E-Nb-19`**; os cenários passam de `K-Nb-1`–`K-Nb-40` para
    **`K-Nb-1`–`K-Nb-51`**. **O contrato documental está fechado e o CÓDIGO NÃO FOI
    ALTERADO**: `src/`, `tests/`, `knowledge/` e `prompts/` permanecem intactos. **O PR #55
    continua sendo o último funcional** e sua implementação — descrita por
    **`M-NB1`–`M-NB9`** — é **anterior a AJ2** e **ainda não possui `assunto`**; o **delta
    AJ2 está pendente de materialização futura, não autorizada aqui**. **AJ2 não antecipa
    S2-D8**: `ASSUNTO_NAO_CLASSIFICADO` **não implica** ausência de `Rxx`,
    `resposta_aprovada_disponivel = false`, `E09`, `pendencia_impeditiva`, `R03` nem
    handoff — **S2-D8 decidirá futuramente** o seu tratamento e **continua ABERTA**. Nada
    muda no marco funcional: **baseline `1167 passed` / Python 3.14.5** permanece vigente,
    a **3B.7** continua a última subetapa numerada, a **3B.8 não existe**, **C continua não
    materializada** e a **próxima implementação funcional continua NÃO ESCOLHIDA**.
23. **A arbitragem S2-D8 está ARBITRADA / NÃO MATERIALIZADA e INTEGRADA À `main` pelo
    PR #59** — commit documental `6bbd1185d3a31cc3b307ce3c7c2abe67085e7c66`, merge
    `eff50138ce9e10ff71f34920077b843bbc201264`, branch de origem `docs/arbitragem-s2-d8`,
    **exclusivamente** `docs/00-estado-atual.md`, `docs/06-maquina-de-estados.md` e
    `docs/07-arquitetura-motor-respostas.md`, **673 adições / 36 remoções**. Aquela entrega
    foi **exclusivamente documental** e fechou o **contrato** de detecção e classificação de
    pendências e de cobertura de resposta aprovada, **antes da etapa 7**, em
    `docs/07-arquitetura-motor-respostas.md` §4.4.1, com reflexos em §2.2, §4.4, §5, §6.3,
    §7, §8.2 e §12 (item 10), e em `docs/06-maquina-de-estados.md` §1.2, §1.3, §2.2, §3
    (redação de T11/T18), §4.3 (P5), §9 e §11. Base: `111e5c31826ba839ff4e0599b45bc98d34620128`.
    **O que ela fecha**: os **dois eixos** — **A**, de qualificação, e **B**, de resposta —;
    **Q1** como decisão do MVP, com os requisitos estruturais do carregador permanecendo
    **pré-requisitos da base** e `src/` **intacto**; a **regra impeditiva `IMP-1`–`IMP-4`**,
    com o invariante `pendencia_impeditiva == True` ⇒ `INDEFINIDO`; a **ordem conceitual
    determinística** anterior à etapa 7; o mapa **R2** de **grupos de cobertura**
    (**conjunção entre grupos**, **disjunção dentro do grupo**), registrado **fora de C**;
    **fragmento emitível** e **regra de lacuna real**; **Classe I** (base não avaliável) ×
    **Classe II** (base avaliável e divergente); **exatamente dois** motivos de `E09` —
    `CAMPO_INDISPONIVEL` e `SEM_RESPOSTA_APROVADA_EMITIVEL`, **sem terceiro**; a semântica de
    `pendencias_resposta`; e a **reconciliação normativa limitada F4-B** de `docs/07` §2.2,
    que **preserva F1–F6 e F4(a)–F4(d)** e refina **somente a consequência conversacional**.
    **As condições 2 e 4 de `docs/07` §4.4 passam a ter PRODUTOR CONCEITUAL** — os eixos A e
    B —, **sem componente concreto escolhido**; a **condição 8 continua NÃO ATRIBUÍDA**
    (**S3-D1**). **O CÓDIGO NÃO FOI ALTERADO**: `src/`, `tests/`, `knowledge/` e `prompts/`
    permanecem intactos, e **nenhum teste foi executado nesta entrega documental**.
    **S2-D8 NÃO materializa AJ2**, **NÃO materializa C**, **NÃO fecha `N-b-RES2`** — que
    **continua ABERTO** — e **NÃO implementa o `OrquestradorMotor`**. O registro do item 22,
    feito por AJ2, permanece **correto como registro daquela arbitragem**; **a partir desta
    entrega** S2-D8 deixa de ser descrita como simplesmente "aberta" e passa a **ARBITRADA /
    NÃO MATERIALIZADA**, aberta **somente quanto à materialização**. Nada muda no marco
    funcional: **o PR #55 continua o último funcional**, a **baseline `1167 passed` / Python
    3.14.5** permanece vigente, a **3B.7** continua a última subetapa numerada, a **3B.8 não
    existe** e a **próxima implementação funcional continua NÃO ESCOLHIDA**.
24. **A presente entrega é exclusivamente reconciliação documental de
    `docs/00-estado-atual.md` após o merge do PR #59.** Base reconciliada:
    `eff50138ce9e10ff71f34920077b843bbc201264`. Ela **não altera código, testes,
    `docs/06`, `docs/07`, `docs/05`, `docs/08`, base de conhecimento nem prompts**, e
    **nenhuma execução de testes ocorre nela** — os números funcionais registrados
    continuam sendo os **`320 passed`** / **`1167 passed`** executados e auditados em
    **Python 3.14.5** antes do merge do **PR #55**. **Nada é materializado aqui**: o
    contrato de S2-D8 continua **ARBITRADO / NÃO MATERIALIZADO**, **AJ2** e **C** continuam
    **ARBITRADAS / NÃO MATERIALIZADAS**, **`N-b-RES2` continua ABERTO**, o índice
    `knowledge/indice-respostas-aprovadas.yaml` e o **mapa de cobertura R2** continuam
    **inexistentes** e o **`OrquestradorMotor` continua não implementado**. **O marco
    funcional permanece o do PR #55** (`3f24e216…` / merge `ba412502…`), a **baseline
    permanece `1167 passed` / Python 3.14.5**, a **3B.7** permanece a **última subetapa
    funcional numerada**, a **3B.8 NÃO EXISTE** e a **próxima implementação funcional
    continua NÃO ESCOLHIDA** — esta reconciliação **não a escolhe**.
25. **O delta AJ2 está MATERIALIZADO na fronteira determinística da `main`, pelo PR #61**
    (**MERGED**) — commit funcional `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`, merge
    `5a722a5cc648149330362434694e7e76a40c1b57`, branch de origem
    `feat/materializar-aj2-assunto`, **exclusivamente** `src/casa77_sdr/interpretation.py`,
    `tests/test_interpretation.py` e `docs/07-arquitetura-motor-respostas.md`, **762
    adições / 28 remoções**. **Entrega FUNCIONAL**: **passa a ser o marco funcional** da
    `main`, **sem numeração de subetapa** — a **3B.7** continua a última numerada e a
    **3B.8 NÃO EXISTE**. **O que foi materializado**: **`AssuntoComercial`** com **54**
    membros na ordem documental; **`PerguntaComercial` com três campos**, o `assunto`
    **obrigatório** e **sem confiança própria**; a **ampliação de `E-Nb-5`** (AJ2-X1,
    AJ2-X2), com `TypeError` **sem código** para tipo runtime incompatível; a validação nos
    **dois caminhos**, **depois** das validações N-b/AJ1 preexistentes; e os cenários
    **`K-Nb-41`–`K-Nb-51`**, registrados em `docs/07` §6.3 como **`M-AJ2-1`–`M-AJ2-9`**.
    **Baseline funcional passa a `1215 passed` / Python 3.14.5** — delta **+48** sobre os
    **`1167 passed`** do PR #55. **O que NÃO foi materializado, e continua fora**: o
    **produtor não determinístico / LLM**; a **interpretação real de texto livre**; a
    **segmentação semântica** de consulta composta — que precisa chegar **já segmentada** do
    futuro produtor, porque a fronteira apenas **recebe, valida e preserva** itens já
    segmentados; **`N-b-RES2`**; a **integração operacional da etapa 4**; e o
    **`OrquestradorMotor`**. **N-b continua PARCIALMENTE IMPLEMENTADA.** **C continua
    ARBITRADA / NÃO MATERIALIZADA** e **S2-D8 continua ARBITRADA / NÃO MATERIALIZADA** — as
    condições **2** e **4** de `docs/07` §4.4 seguem com **produtor conceitual** e **NÃO
    MATERIALIZADAS**, e a condição **8** continua **NÃO ATRIBUÍDA** (**S3-D1**); a
    **condição 5** continua a **única** condição de §4.4 materializada em código. **A
    próxima implementação funcional continua NÃO ESCOLHIDA**: a decisão pertence à
    **orquestração/auditoria posterior do GPT**, e **nenhuma pendência é eleita aqui** — nem
    **C**, nem **S2-D8**, nem **`N-b-RES2`**, nem o **produtor LLM**, nem a **integração da
    etapa 4**, nem o **`OrquestradorMotor`**, nem qualquer outra.
26. **A presente entrega é exclusivamente reconciliação documental de
    `docs/00-estado-atual.md` após o merge do PR #61.** Base reconciliada:
    `5a722a5cc648149330362434694e7e76a40c1b57`. Ela **não altera código, testes,
    `docs/06`, `docs/07`, `docs/05`, `docs/08`, base de conhecimento nem prompts**, e
    **nenhuma execução de testes ocorre nela** — os números registrados são os
    **`368 passed`** / **`1215 passed`** executados e auditados em **Python 3.14.5** antes
    do merge do **PR #61**. **Nada é materializado aqui**, **nenhuma numeração é criada** e
    **a 3B.8 continua não existindo**. **Esta é a única reconciliação pós-PR #61**: nenhuma
    "reconciliação da reconciliação" será criada.
27. **A micro-arbitragem C-A1 é a presente entrega e está ARBITRADA DOCUMENTALMENTE.** Ela é
    **exclusivamente documental**, **posterior** à arbitragem C, e **fecha o contrato de
    MATERIALIZAÇÃO** de C em `docs/07-arquitetura-motor-respostas.md` §2.3, com registro em
    §12, item 19. Base: `4ba1cdfe4397e90692efdec06357cb079e44ca8a`. **O que ela fecha**: a
    **equivalência de *template*** **`C-15a`**–**`C-15e`** — vínculo explícito ao fato
    afirmado, equivalência textual do **fragmento inteiro** sob **NFC** e quebras suaves,
    **fail-closed** sem equivalência, e proibição de guardar valor, *snapshot*, *hash* ou
    versão congelada no índice —; os **refinamentos de C-6** (`inteiro_agrupado`,
    `simbolo_moeda` com tabela fechada e falha para código não suportado, `hora` com
    `HH:MM` e `Hh` **apenas** quando os minutos são `00`); a **convenção final do formato
    `lista`**; a **preservação de C-5** com **sete rejeições explícitas**; a **proibição de
    seleção posicional** em coleção, com exigência de **identificador estrutural estável e
    não comercial**; a **unidade de bijeção** no **fragmento emitível**; a
    **canonicalização de status** e as **cinco condições** de migração de autoridade; a
    **prioridade de modelagem** e a regra de **prosa não duplicada**; a **auditoria
    obrigatória de consumidores** antes de qualquer alteração física do YAML; os **alvos de
    modelo `MD-1`–`MD-18`** — com **`MD-3` REMOVIDO / NÃO ARBITRADO** e **`MD-16` REMOVIDO /
    NÃO NECESSÁRIO PARA C** —; e a **matriz `G1`–`G14`**. **`C-1`–`C-14` permanecem registro
    histórico** e **não foram reescritas**. **Nenhum pytest foi executado nesta entrega.**
    **C-A1 NÃO cria o índice, NÃO altera o YAML, NÃO converte respostas em *templates*, NÃO
    muda status real, NÃO implementa renderizador nem carregador e NÃO materializa C, R2 ou
    S2-D8.** Ela **não cria marco funcional**: o **último funcional continua o PR #61** —
    commit `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`, merge
    `5a722a5cc648149330362434694e7e76a40c1b57` —, a **baseline permanece `1215 passed` /
    Python 3.14.5**, a **3B.7** continua a **última subetapa funcional numerada** e a
    **3B.8 NÃO EXISTE**. **Preserva sem alteração**: `docs/07` §4.1 com **14** componentes,
    §2 com **nove** responsabilidades, §4.4 com **oito** condições, `AssuntoComercial` com
    **54** valores, `IntencaoConversacional` com **11**, os erros **`E-Nb-1`–`E-Nb-19`**, os
    cenários **`K-Nb-1`–`K-Nb-51`**, os **20** códigos de `AcaoMaquina` e os **12**
    `CriterioIdentidade`. **Contagens PROJETADAS de fragmentos, não estado físico atual**:
    **35** fragmentos emitíveis no total; **7** estruturalmente representáveis no contrato
    **original**; **11** após os refinamentos normativos de C-A1, **sem** alterar o YAML e
    **sem** decisão humana; **29** após C-A1 mais os alvos de modelo e as confirmações
    factuais; e **6** residuais dependentes de **C-A2** — **29 + 6 = 35**. No nível `Rxx`, no
    **cenário futuro projetado**: **24** integralmente materializáveis, **4** parcialmente e
    **2** integralmente bloqueados — **24 + 4 + 2 = 30**. **Hoje nada está materializado.**
28. **`C-A2` fica ABERTA como arbitragem residual humana.** Ela é o **rótulo** da futura
    arbitragem dos **fatos humanos** — **`A1`** forma de tratamento autorizada do
    responsável; **`A2`** política explícita sobre existência ou inexistência de mínimo;
    **`A3`** semântica factual necessária para modelar a retenção integral; **`A4`**
    capacidade operacional do bot de confirmar disponibilidade — e do **conteúdo humano
    residual**: **`B1`** `R11` `F2`; **`B2`** `R12` `F1`; **`B3`** `R18`; **`B4`** `R19`;
    **`B5`** `R23` `F1`; **`B6`** `R25` `F1`. **Nenhuma dessas pendências é resolvida aqui**,
    **nenhuma redação nova é escrita** e **nenhuma decisão comercial é tomada**. **`R17` e
    `R20` não entram como pendência de redação.** **Nem C-A1 nem C-A2 são subetapa do
    roadmap**, e **nenhum dos dois cria a 3B.8**. Os **alvos `MD-x` são ALVOS FUTUROS, não
    alterações autorizadas**: nenhum deles é executado, e **todos** exigem **auditoria
    read-only de consumidores em todo o repositório** antes de qualquer alteração física de
    `knowledge/casa77.yaml`. **C continua ARBITRADA / NÃO MATERIALIZADA**, **S2-D8 continua
    ARBITRADA / NÃO MATERIALIZADA**, **AJ2 continua MATERIALIZADA na fronteira
    determinística**, **`N-b-RES2` continua ABERTO**, o **`OrquestradorMotor` continua não
    implementado** e a **próxima implementação funcional continua NÃO ESCOLHIDA**.
29. **Evidência factual de C-A1 — auditoria read-only `Rxx` × YAML.** A base factual da
    micro-arbitragem é um **relatório sanitizado**, identificado pelo SHA-256
    `c0cf81d6e1a93c8ba19ed5a1863c93be4f1c37954702a8e94720a8a6b4ec79b0`. Ele **NÃO é
    versionado**, **vive fora do repositório** e **não contém fonte comercial nova**: usa
    apenas identificadores `Rxx`, identificadores locais de fragmento, **caminhos** YAML,
    tipos estruturais, categorias de auditoria e descrições abstratas. A auditoria foi
    **read-only** e **não alterou** `knowledge/`, `src/`, `tests/` nem documento algum.
30. **A micro-arbitragem C-A2 é a presente entrega e está ARBITRADA DOCUMENTALMENTE.** Ela é
    **exclusivamente documental**, **posterior** a **C** e a **C-A1**, e vive em
    `docs/07-arquitetura-motor-respostas.md` §2.3 — bloco **"Micro-arbitragem C-A2"** —, com
    **nota temporal** em §12, item 19. Base: `a60c57dbf029913a623ad87bb24795fe333cdc3f`.
    **Esta é a ENTREGA 1**, e ela é **DOCUMENTAL**. **O que ela fecha, em nível de estado**:
    **`A1`–`A4` = FECHADAS**, conforme arbitragem normativa registrada em `docs/07` §2.3,
    bloco **"Micro-arbitragem C-A2"** — **os enunciados substantivos desses fatos não são
    duplicados aqui**. **O registro estrutural do conteúdo humano**: **`B1`–`B16`**, com
    alvo, mecanismo previsto, alvos `MD`, `FE` relacionada e observação estrutural — **sem o
    corpo literal de texto algum**. **A decisão `B16`**: `R05` passa a ter os fragmentos
    **`F1`**, **`F2`** e **`F3`**, **permanecendo um único `Rxx`** — e **sem** afirmar que um
    `Rxx` diferente produziria grupo **R2** diferente ou `E09` espúrio, porque **R2 continua
    arbitragem própria**. **O refinamento `C-A2-RT`**, em alto nível: o *binding* passa a
    declarar **`origem` OBRIGATÓRIA**, de vocabulário **fechado** — **`YAML`** ou
    **`RUNTIME_AUTORITATIVO`** —, **sem valor padrão**, com **ausência = índice
    estruturalmente inválido / FAIL-CLOSED** e **exatamente um referente**; o **vocabulário
    runtime** fica **fechado** e **admissível somente por `ASSERTIVA`**, **sem escolher
    provedor de calendário**. **Detalhes normativos em `docs/07` §2.3.** **A tabela `MD`
    final é refinada até `MD-20`**: **`MD-1` SUPERADO / NÃO NECESSÁRIO PARA C**; **`MD-3`** e
    **`MD-16` REMOVIDOS**; **`MD-18` GENERALIZADO**; **`MD-19`** e **`MD-20` NOVOS**, com
    **`MD-20` MÍNIMO** — **detalhes normativos em `docs/07` §2.3**. **Os efeitos futuros
    `FE-1`–`FE-14`**, todos **PLANEJADOS / NÃO APLICADOS**, com **`FE-11` DIVIDIDA** em
    **`FE-11a`** — instrução interna, na Entrega 2, **sem alterar o YAML** — e **`FE-11b`** —
    base estruturada, **RETIDA atrás de `C-A1-M4`** e **fora da Entrega 2**.
    **`C-1`–`C-14` e todo o bloco `C-A1` permanecem registro histórico e não foram
    reescritos**; a regra temporal aplicada é a de que o texto histórico continua correto
    **para o momento em que foi escrito**. **Nenhum pytest foi executado nesta entrega.**
    **C-A2 NÃO cria o índice, NÃO altera o YAML, NÃO aplica texto algum, NÃO converte
    respostas em *templates*, NÃO muda status real, NÃO executa alvo `MD`, NÃO aplica `FE`,
    NÃO materializa C, R2 nem S2-D8, NÃO resolve `N-b-RES2` e NÃO escolhe provedor de
    calendário.** Ela **não cria marco funcional**: o **último funcional continua o PR #61**
    — commit `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`, merge
    `5a722a5cc648149330362434694e7e76a40c1b57` —, a **baseline permanece `1215 passed` /
    Python 3.14.5**, a **3B.7** continua a **última subetapa funcional numerada** e a
    **3B.8 NÃO EXISTE**. **Preserva sem alteração**: `docs/07` §4.1 com **14** componentes,
    §2 com **nove** responsabilidades, §4.4 com **oito** condições, `AssuntoComercial` com
    **54** valores, `IntencaoConversacional` com **11**, `ProjecaoInterpretacao` com
    **sete** campos, os **12** `CriterioIdentidade`, os erros **`E-Nb-1`–`E-Nb-19`** e os
    cenários **`K-Nb-1`–`K-Nb-51`**. **Nenhum evento, estado, condição de ciclo, motivo de
    `E09` ou subetapa novo foi criado.**
31. **Contagens de C-A2 — três eixos distintos, que não devem ser confundidos.** **ESTADO
    FÍSICO ATUAL**: **35** fragmentos emitíveis e **30** `Rxx` — **inalterado por esta
    entrega**. **CONTEÚDO APROVADO**: **16** novas unidades textuais aprovadas no lote —
    `B2`–`B15` mais `R05` `F2` e `R05` `F3`; **`B1` não é texto novo** e **não integra as
    16**. **CONTEÚDO APLICADO nesta Entrega 1**: **0**. **MATERIALIZAÇÃO DE C hoje**: **0**
    fragmentos estruturalmente materializados. **APÓS a futura Entrega 2**: **37**
    fragmentos e **30** `Rxx`. A hipótese futura de **37/37** é **estritamente condicional**
    à **aplicação do conteúdo**, a **`C-A1-M4`**, aos **alvos `MD` necessários** e à
    **validação `C-8`/`C-15`/`C-A1`** — e **não é declarada como resultado alcançado**. As
    **contagens projetadas de `C-A1-N`** continuam **registro histórico** e **não foram
    reescritas**. **O item 28 acima registra o estado à época de C-A1**, quando `C-A2` estava
    **ABERTA**, e **permanece correto como registro histórico**: ele é **superado** pelos
    itens 30 e 31. **A próxima ação é a aplicação coordenada do conteúdo e das `FE`
    — a futura ENTREGA 2 —, mas SOMENTE APÓS auditoria e merge desta Entrega 1.** **A
    Entrega 2 NÃO está concluída e NÃO foi iniciada.** Os arquivos **comportamentais**
    previstos para ela são `knowledge/respostas-aprovadas.md`, `docs/02-fluxo-comercial.md`,
    `docs/03-regras-de-conversa.md`, `docs/04-handoff-humano.md` e
    `prompts/prompt-sistema-bot.md`; **`FE-11a` está incluída** nela e **`FE-11b` fica
    fora**. **A conclusão da futura Entrega 2 deverá também atualizar este documento na
    mesma entrega, ou possuir reconciliação documental imediatamente vinculada.** **A
    próxima implementação funcional continua NÃO ESCOLHIDA**, **`N-b-RES2` continua
    ABERTO**, o **`OrquestradorMotor` continua não implementado** e a **3B.8 continua não
    existindo**.
32. **A ENTREGA 2 de C-A2 é a presente entrega e está APLICADA.** Ela é a **aplicação
    coordenada** do conteúdo humano aprovado e das reconciliações **`FE`** permitidas, e é
    **documental/comportamental**: altera a **fonte de respostas** e os **documentos de
    comportamento**, e **nenhum arquivo de `src/` ou `tests/`**. Base:
    `25b867f1c6cb4d2d00cd49ea60361c82a6e98f6f`. Arquivos alterados: **seis** —
    `knowledge/respostas-aprovadas.md`, `docs/02-fluxo-comercial.md`,
    `docs/03-regras-de-conversa.md`, `docs/04-handoff-humano.md`,
    `prompts/prompt-sistema-bot.md` e este documento. **Conteúdo B** passa de **APROVADO
    HUMANAMENTE / AINDA NÃO APLICADO** para **APROVADO HUMANAMENTE / APLICADO À FONTE DE
    RESPOSTAS**: as **16** unidades textuais do lote foram escritas em
    `knowledge/respostas-aprovadas.md`. **`B1` / `R11` `F2` permanece INTACTO** — não era
    texto novo. **Corpus físico**: de **35 fragmentos / 30 `Rxx`** para **37 fragmentos /
    30 `Rxx`** — o crescimento vem **exclusivamente** de `R05`, que passa a ter os
    fragmentos **`F1`**, **`F2`** e **`F3`**, **permanecendo um único `Rxx`**. **Nenhum
    `R31` foi criado.** **`FE-1`–`FE-10`, `FE-11a` e `FE-12`–`FE-14` = APLICADAS**;
    **`FE-11b` = RETIDA atrás de `C-A1-M4`** e **fora desta entrega**. **Os enunciados
    normativos das `FE` e dos fatos `A1`–`A4` não são duplicados aqui** — eles vivem em
    `docs/07` §2.3, bloco "Micro-arbitragem C-A2". **`knowledge/casa77.yaml` NÃO foi
    alterado** e **nenhum alvo `MD` foi executado**: todos continuam sujeitos a
    **`C-A1-M4`**. **`C` continua ARBITRADA / NÃO MATERIALIZADA** — o índice
    `knowledge/indice-respostas-aprovadas.yaml` **não foi criado**, nenhuma resposta foi
    convertida em *template*, nenhum *binding* ou `ASSERTIVA` existe e **nenhum status
    saiu do Markdown**, que **continua a autoridade de status** (`C-11`, `C-A1-ST`).
    **`R2` e `S2-D8` continuam NÃO MATERIALIZADAS**, **`N-b-RES2` continua ABERTO**, o
    **`OrquestradorMotor` continua não implementado** e **nenhum provedor de calendário foi
    escolhido**. **Nenhum pytest foi executado** — a entrega não toca código. Ela **não cria
    marco funcional**: o **último funcional continua o PR #61**, commit
    `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`, a **baseline permanece `1215 passed` /
    Python 3.14.5**, a **3B.7** continua a **última subetapa funcional numerada** e a
    **3B.8 NÃO EXISTE**. **A próxima implementação funcional continua NÃO ESCOLHIDA.**
33. **Efeito comportamental da Entrega 2, em nível de estado.** A **superfície emitível foi
    reconciliada** conforme a micro-arbitragem **C-A2**: as **referências destinadas ao
    interessado foram tornadas não nominais**, as **duplicatas emitíveis especializadas
    foram eliminadas** e o **fluxo de disponibilidade foi reconciliado**. A **fonte única de
    redação emitível** permanece **`knowledge/respostas-aprovadas.md`**. **Os detalhes
    normativos permanecem em `docs/07` §2.3 e nos documentos especializados** — `docs/02`,
    `docs/03`, `docs/04` e `prompts/` —, e **não são duplicados aqui**. **Nenhuma constante
    comercial é registrada neste documento**: os fatos continuam em `knowledge/casa77.yaml`
    e a redação em `knowledge/respostas-aprovadas.md`. **Entrega 2 = APLICADA.**
34. **A C-A2 — Entrega 2 está INTEGRADA à `main` pelo PR #65, e a presente entrega é
    exclusivamente a reconciliação documental de `docs/00-estado-atual.md` após esse
    merge.** **Evidência da integração**: commit da entrega
    `c2883d2fad32638d1e15a616a2b37f577abf3e42`, merge na `main`
    `fbe768a14457241245c73f4cbe8ef93e869e7fb3`, branch de origem
    `docs/aplicar-conteudo-c-a2`, **seis** arquivos — `docs/00-estado-atual.md`,
    `docs/02-fluxo-comercial.md`, `docs/03-regras-de-conversa.md`,
    `docs/04-handoff-humano.md`, `knowledge/respostas-aprovadas.md` e
    `prompts/prompt-sistema-bot.md` —, **219 adições / 74 remoções**. Base reconciliada:
    `fbe768a14457241245c73f4cbe8ef93e869e7fb3`. **Natureza da entrega integrada**:
    **documental/comportamental** — **nenhum arquivo de `src/`** e **nenhum arquivo de
    `tests/`** foi tocado —, e ela **NÃO cria marco funcional**. **O merge do PR #65 é
    documental/comportamental e NÃO substitui nem altera o último marco funcional.**
    **Estado funcional preservado sem alteração**: o **último commit funcional aprovado
    continua `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`**, o **merge funcional
    correspondente continua `5a722a5cc648149330362434694e7e76a40c1b57`**, o **PR funcional
    continua o #61**, a **baseline histórica continua `1215 passed` / Python 3.14.5**, a
    **3B.7** continua a **última subetapa funcional numerada** e a **3B.8 continua
    inexistente**. **Nenhum pytest foi executado** nesta reconciliação, que **não altera
    código, testes, `docs/02`, `docs/03`, `docs/04`, `docs/05`, `docs/06`, `docs/07`,
    `docs/08`, base de conhecimento nem prompts** — altera **exclusivamente**
    `docs/00-estado-atual.md`. **Esta é a única reconciliação pós-PR #65**: nenhuma
    "reconciliação da reconciliação" será criada.
35. **Ciclo C-A2 fechado nas duas entregas — estado consolidado.** **Entrega 1** —
    arbitragem documental — foi **integrada anteriormente pelo PR #64** (commit
    `294a11a1c170815063764f1d49ae0d831b72d359`, merge
    `25b867f1c6cb4d2d00cd49ea60361c82a6e98f6f`). **Entrega 2** — aplicação do conteúdo
    aprovado e das `FE` — está **agora integrada pelo PR #65**. **O conteúdo aprovado da
    Entrega 2 está APLICADO às superfícies documentais e de conteúdo previstas**, e o
    **corpus de respostas** permanece em **37 fragmentos / 30 `Rxx`**. **Os enunciados
    normativos não são duplicados aqui**: a arbitragem vive em `docs/07` §2.3, bloco
    "Micro-arbitragem C-A2", e o comportamento nos documentos especializados e em
    `knowledge/respostas-aprovadas.md`. **Preservado explicitamente, sem alteração**:
    **`C` continua ARBITRADA / NÃO MATERIALIZADA**; **`knowledge/indice-respostas-aprovadas.yaml`
    continua inexistente**; **nenhum *template*, *binding* ou `ASSERTIVA` foi
    materializado**; **`knowledge/casa77.yaml` NÃO foi alterado pela Entrega 2**;
    **`FE-11b` continua RETIDA atrás de `C-A1-M4`**; **`R2` e `S2-D8` continuam NÃO
    MATERIALIZADAS**; **`N-b-RES2` continua ABERTO**; o **`OrquestradorMotor` continua não
    implementado**; **nenhum provedor de calendário foi escolhido**; e a **próxima
    implementação funcional continua NÃO ESCOLHIDA**. **Nenhuma etapa foi renumerada e a
    3B.8 continua não existindo.**
36. **A auditoria `C-A1-M4` está CONCLUÍDA e APROVADA, e a presente entrega é exclusivamente
    o seu registro documental em `docs/00-estado-atual.md`.** **Natureza da auditoria**:
    **READ-ONLY**, executada contra o ponto autoritativo `origin/main` =
    `118054575e7f7560a1c37ca430bdedd15eddc817` — **nenhum arquivo do repositório foi criado,
    alterado ou removido** por ela. **Evidência**: relatório **sanitizado** e **não
    versionado**, mantido **fora do repositório**, identificado por
    `casa77-c-a1-m4-auditoria-consumidores-v2.md`, SHA-256
    `cdca7d40ce672c924bf2f13318f51e2a6dd87990abe56c159b1de747bbc51e1e`. Ele **não contém
    fonte comercial**: usa apenas caminhos estruturais normalizados, nomes de arquivos e de
    símbolos, tipos esperados, categorias de consumidor e de impacto e identificadores
    `MD`/`FE`/`C`. **Resultado consolidado**: **192** caminhos estruturais normalizados
    auditados, derivados de **159** chaves distintas, com cobertura verificada nos **dois
    sentidos** — da base para os consumidores e de cada consumidor de volta para a base.
    **Nenhum bloqueador foi encontrado** e **nenhum item ficou não determinável**.
    **Classificação dos alvos de modelo**: **`MD-1` SUPERADO**; **`MD-3`** e **`MD-16`
    REMOVIDOS**; **13** classificados como **viáveis sem adaptação identificada**; **4**
    como **viáveis com adaptação identificada**; **0 BLOQUEADO**; **0 NÃO DETERMINÁVEL**.
    **Essas classificações são ACHADOS DE AUDITORIA e NÃO autorizam implementação**: elas
    **não** escolhem ordem de execução, **não** transformam recomendação em decisão técnica e
    **não** definem faseamento da futura materialização de C. **Com esta aprovação,
    `C-A2-N10` passa a CUMPRIDA.**
37. **Estado das condições de materialização de C após `C-A1-M4`.** **`C-A2-N9`** — aplicação
    do conteúdo aprovado — **CUMPRIDA** pela Entrega 2 (PR #65). **`C-A2-N10`** —
    `C-A1-M4` — **CUMPRIDA** por esta auditoria. **`C-A2-N11`** — alvos `MD` necessários —
    **PENDENTE**. **`C-A2-N12`** — validações `C-8` / `C-15` / `C-A1` — **PENDENTE**.
    **Preservado expressamente, sem alteração**: **nenhum alvo `MD` foi executado**;
    **o gate `C-A1-M4` aplicável a `FE-11b` está CUMPRIDO**, mas **`FE-11b` continua NÃO
    APLICADA e NÃO AUTORIZADA por esta entrega**; **`knowledge/casa77.yaml` não foi
    alterado**;
    **`knowledge/indice-respostas-aprovadas.yaml` continua inexistente**; **nenhum
    *template*, *binding* ou `ASSERTIVA` foi materializado**; e **`C` continua ARBITRADA /
    NÃO MATERIALIZADA**. **`R2` e `S2-D8` continuam NÃO MATERIALIZADAS**, **`N-b-RES2`
    continua ABERTO** e o **`OrquestradorMotor` continua não implementado**. **Esta entrega
    não cria marco funcional**: o **último commit funcional aprovado continua
    `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`** (**PR #61**, merge
    `5a722a5cc648149330362434694e7e76a40c1b57`), a **baseline funcional histórica não muda**,
    a **3B.7** continua a **última subetapa funcional numerada** e a **3B.8 continua
    inexistente**. **Nenhum pytest foi executado** — nenhum artefato funcional foi tocado — e
    a **próxima implementação funcional continua NÃO ESCOLHIDA**.
38. **A entrega `M1` é a presente entrega e executa EXCLUSIVAMENTE os alvos `MD-18` e
    `MD-20`.** Base: `de13a513990fe17f83010bc9b2213748241bcad4`. **Classificação da
    entrega**: **MODELAGEM DA BASE AUTORITATIVA, SEM ALTERAÇÃO DE CÓDIGO E SEM NOVO MARCO
    FUNCIONAL DE CÓDIGO**. Arquivos alterados: **dois** — `knowledge/casa77.yaml` e este
    documento. **Nenhum arquivo de `src/` e nenhum arquivo de `tests/` foi tocado**, e
    **nenhum teste foi alterado**. **`MD-18`** adiciona **identificadores estruturais
    estáveis** — a chave `id`, como **última chave** de cada item — às **duas coleções
    arbitradas**: as **opções de pagamento** (`integral`, `parcelado`) e os **equipamentos
    da cozinha** (`freezer_horizontal`, `geladeira_duplex`, `cervejeira`,
    `fogao_industrial`, `fogao_convencional`, `forno_eletrico`, `micro_ondas`,
    `churrasqueira`, `bancada_de_apoio`, `area_de_cozinha_externa`). Os identificadores são
    **técnicos, não comerciais, não emitíveis, não posicionais, únicos na coleção,
    imutáveis após integrados e não reutilizáveis após remoção** (**C-A1-S3**–**S5**).
    **Nenhuma lista foi convertida em mapa** e **nenhum item foi reordenado**. **`MD-20`**
    adiciona **um único fato atômico booleano** — `pagamento.integral_disponivel` — no nível
    de `pagamento`, **sem** booleano equivalente para a modalidade parcelada e **sem**
    qualquer outro campo. **Nenhum fato comercial preexistente foi alterado**: o diff do
    YAML é de **13 inserções e ZERO remoções**, provado mecanicamente — removidos apenas os
    campos que `M1` adiciona, o restante da base é **idêntico ao HEAD**. **A versão da base
    permanece `1.1`** e `ultima_atualizacao` **não mudou**; **nenhuma política nova de
    versionamento foi criada**. **`knowledge/respostas-aprovadas.md` e
    `knowledge/informacoes-pendentes.md` não foram alterados.**
39. **Estado das condições de materialização de C após `M1`.** **`C-A2-N9`** — **CUMPRIDA**.
    **`C-A2-N10`** — **CUMPRIDA**. **`C-A2-N11`** — alvos `MD` necessários — **continua
    PENDENTE**: `M1` cumpre apenas **2 dos 16** alvos `MD` necessários, e **14 alvos `MD`
    permanecem** após esta entrega. **`C-A2-N12`** — validações `C-8` / `C-15` / `C-A1` —
    **continua PENDENTE**. **Preservado expressamente**: **nenhum outro alvo `MD` foi
    executado**; **`FE-11b` NÃO foi aplicada**; **`knowledge/indice-respostas-aprovadas.yaml`
    continua inexistente**; **nenhum *template*, *binding* ou `ASSERTIVA` foi
    materializado**; e **`C` continua ARBITRADA / NÃO MATERIALIZADA**. **`R2` e `S2-D8`
    continuam NÃO MATERIALIZADAS**, **`N-b-RES2` continua ABERTO** e o **`OrquestradorMotor`
    continua não implementado**. **Esta entrega não cria marco funcional de código**: o
    **último commit funcional aprovado continua `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`**
    (**PR #61**), a **baseline permanece `1215 passed`** — medida **antes** e **depois** da
    edição, com **contagem idêntica** e **100% verde** —, a **3B.7** continua a **última
    subetapa funcional numerada** e a **3B.8 continua inexistente**. **Nenhuma próxima
    entrega foi escolhida.**
40. **A entrega anterior executou EXCLUSIVAMENTE o alvo `MD-4`.** Base:
    `3ad807fec57a3e21061dbee5fa3b3c14573eb2ac`. **Classificação da entrega**: **MODELAGEM DA
    BASE AUTORITATIVA, SEM ALTERAÇÃO DE CÓDIGO E SEM NOVO MARCO FUNCIONAL DE CÓDIGO**.
    **Aquela entrega NÃO foi uma nova subetapa oficial do roadmap — a 3B.8 continua
    inexistente.** Arquivos alterados: **dois** — `knowledge/casa77.yaml` e este documento.
    **Nenhum arquivo de `src/` e nenhum arquivo de `tests/` foi tocado**, e **nenhum teste
    foi alterado**. **O que `MD-4` faz**: **duas representações narrativas de vencimento**
    da modalidade parcelada foram **SUBSTITUÍDAS por fatos atômicos**, conforme **C-A1-M3** —
    a chave narrativa `vencimento` **deixa de existir** nas duas parcelas, **sem** cópia
    legada, campo de texto paralelo ou observação equivalente. A modalidade foi identificada
    pelo **identificador estrutural estável** materializado em `M1` — **`id: "parcelado"`** —,
    **nunca por posição** (**C-A1-S1**). **Caminhos finais**:
    `pagamento.opcoes[id="parcelado"].primeira_parcela.vence_na_assinatura_do_contrato`, do
    tipo **booleano**, e
    `pagamento.opcoes[id="parcelado"].segunda_parcela.antecedencia_evento_dias`, do tipo
    **inteiro** — provado **inteiro e não booleano**. **Nenhum fato comercial preexistente
    foi alterado**: o diff do YAML é de **2 inserções e 2 remoções**, e as remoções são
    **exatamente** as duas chaves narrativas substituídas. **A opção de pagamento integral,
    os identificadores de `M1`, `integral_disponivel`, os percentuais, a cardinalidade de
    parcelas, a caução e o desconto permanecem inalterados**, assim como `versao` — que
    continua **`1.1`** — e `ultima_atualizacao`.
41. **A entrega `MD-4` está INTEGRADA à `main` pelo PR #69** — commit
    `b827306d28b552e54b14c06e75fa8c412fa9b4e9`, merge
    `6868042f813f940191fc4cd45266680e39f49b7c`, branch de origem `feat/c-a2-n11-md4`.
    **Dois** arquivos — `knowledge/casa77.yaml` e este documento —, **47 adições / 5
    remoções**. **Modelagem da base autoritativa**: **não altera `src/` nem `tests/`** e
    **não cria marco funcional de código**. O merge foi feito por **merge commit**, com
    **dois parents** — `3ad807fec57a3e21061dbee5fa3b3c14573eb2ac` e o commit de conteúdo —,
    **sem squash, sem rebase e sem exclusão de branch**.
42. **A entrega anterior executou EXCLUSIVAMENTE o alvo `MD-17`.** Base:
    `6868042f813f940191fc4cd45266680e39f49b7c`. **Classificação da entrega**: **MODELAGEM DA
    BASE AUTORITATIVA, SEM ALTERAÇÃO DE CÓDIGO E SEM NOVO MARCO FUNCIONAL DE CÓDIGO**.
    **Aquela entrega NÃO foi uma nova subetapa oficial do roadmap — a 3B.8 continua
    inexistente.** Arquivos alterados: **dois** — `knowledge/casa77.yaml` e este documento.
    **Nenhum arquivo de `src/` e nenhum arquivo de `tests/` foi tocado**, e **nenhum teste
    foi alterado**. **O que `MD-17` faz**: a **representação numérica** que exprimia
    totalidade no bloco `cancelamento` foi **SUBSTITUÍDA por um fato atômico booleano
    equivalente**, conforme **C-A1-M3 (A)** — a chave `retencao_entrada_percentual` **deixa
    de existir**. **Caminho final**: `cancelamento.retencao_entrada_integral`, do tipo
    **booleano**, provado **booleano verdadeiro e não numérico**, posicionado **exatamente**
    onde estava a chave substituída. **Nenhuma fonte factual paralela subsiste**: percentual
    e booleano **não coexistem** como fontes autoritativas concorrentes do mesmo conceito
    (**C-A1-R2**, **C-A1-M3**). **A única supressão de representação factual é a narrativa
    expressamente autorizada por `D1-A`; nenhum outro fato comercial foi alterado**: o diff
    do YAML é de **1 inserção e 4 remoções**, e as remoções são **exatamente** a chave
    numérica substituída e a chave narrativa suprimida. **`cancelamento.permitido` e
    `cancelamento.atendimento_humano_obrigatorio` permanecem inalterados**, assim como
    `versao` — que continua **`1.1`** — e `ultima_atualizacao`.
43. **Decisão humana `D1`, opção `A`, aplicada.** A retenção de `MD-17` registrada na
    entrega anterior decorria de **decisão humana pendente sobre o destino de
    `cancelamento.explicacao`**, e **não** de impedimento técnico. Essa decisão foi
    **recebida e aprovada** como **opção `A` — SUPRESSÃO**. Consequência **expressamente
    autorizada**: a chave `cancelamento.explicacao` foi **removida**, **sem** cópia textual
    preservada, **sem** marcador de não autoritatividade, **sem** campo legado e **sem**
    comentário equivalente. A representação narrativa **deixa de ter existência independente
    na base autoritativa** e **deixa de ser fonte de *binding***. **Nenhum campo de resgate
    foi criado** — o bloco `cancelamento` passa a ter **exatamente três chaves**. `R20`
    **não é pendência de redação** (**C-A1-P4**) e **não foi alterado**:
    `knowledge/respostas-aprovadas.md` permanece **intocado** nesta entrega.
44. **`C-A1-P4` observada.** O **percentual da entrada** permanece ligado **exclusivamente**
    ao campo correto do bloco `pagamento` e **não** foi associado ao campo de retenção —
    vínculo que produziria **afirmação falsa**. O bloco `pagamento` está **INTACTO** e
    **`MD-4` permanece íntegro**: os dois caminhos materializados por ele — o **booleano** da
    primeira parcela e o **inteiro** da segunda — foram **verificados após a edição** e
    continuam presentes, com os **identificadores estruturais** de `M1`/`MD-18`
    preservados. **`MD-18` e `MD-20` permanecem inalterados.**
45. **Estado das condições de materialização de C após `MD-17`** — **registro histórico
    daquela entrega**, superado pelo item 49. **`C-A2-N9`** — **CUMPRIDA**. **`C-A2-N10`** —
    **CUMPRIDA**. **`C-A2-N11`** — alvos `MD` necessários — **continuava PENDENTE**: com
    aquela entrega passaram a ser **4 dos 16** alvos `MD` necessários cumpridos —
    **`MD-18`**, **`MD-20`**, **`MD-4`** e **`MD-17`** —, e **12 alvos `MD` permaneciam**.
    **`C-A2-N12`** — validações `C-8` / `C-15` / `C-A1` — **continuava PENDENTE**.
    **Preservado expressamente naquela entrega**: **nenhum outro alvo `MD` foi executado**;
    **`FE-11b` NÃO foi aplicada**; **`knowledge/indice-respostas-aprovadas.yaml` continua
    inexistente**; **nenhum *template*, *binding* ou `ASSERTIVA` foi materializado**; e
    **`C` continua ARBITRADA / NÃO MATERIALIZADA**. **`R2` e `S2-D8` continuam NÃO
    MATERIALIZADAS**, **`N-b-RES2` continua ABERTO** e o **`OrquestradorMotor` continua não
    implementado**. **Aquela entrega não criou marco funcional de código**: o **último commit
    funcional aprovado continua `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`** (**PR #61**), a
    **baseline permaneceu `1215 passed`** — medida **antes** e **depois** da edição, com
    **contagem idêntica** e **100% verde** —, a **3B.7** continua a **última subetapa
    funcional numerada** e a **3B.8 continua inexistente**.
46. **A entrega `MD-17` está INTEGRADA à `main` pelo PR #70** — commit
    `8e8efed1ca72651a19a4770c8a6c424af06f851b`, merge
    `d48692e7810c5d10b2cd2e43adcca1d157d0bfd5`, branch de origem `feat/c-a2-n11-md17`.
    **Dois** arquivos — `knowledge/casa77.yaml` e este documento —, **67 adições / 27
    remoções**. **Modelagem da base autoritativa**: **não altera `src/` nem `tests/`** e
    **não cria marco funcional de código**. O merge foi feito por **merge commit**, com
    **dois parents** — `6868042f813f940191fc4cd45266680e39f49b7c` e o commit de conteúdo —,
    **sem squash, sem rebase e sem exclusão de branch**.
47. **A entrega anterior (M3) executou EXCLUSIVAMENTE os alvos `MD-8`, `MD-9`, `MD-10` e
    `MD-11`.** Base: `d48692e7810c5d10b2cd2e43adcca1d157d0bfd5`. **Classificação da
    entrega**: **MODELAGEM DA BASE AUTORITATIVA, SEM ALTERAÇÃO DE CÓDIGO E SEM NOVO MARCO
    FUNCIONAL DE CÓDIGO**. **Aquela entrega NÃO foi uma nova subetapa oficial do roadmap — a
    3B.8 continua inexistente.** Arquivos alterados: **dois** — `knowledge/casa77.yaml` e
    este documento. **Nenhum arquivo de `src/` e nenhum arquivo de `tests/` foi tocado**, e
    **nenhum teste foi alterado**. Todos os alvos incidem sobre o bloco `estrutura` e
    aplicam **C-A1-M3 (A)** — **substituição** da representação narrativa por fatos
    atômicos, **sem** fonte factual paralela. **Balanço do YAML**: **19 adições e 15
    remoções**, com **15 fatos booleanos novos**, **4 agrupamentos novos** —
    `plano_chuva.toldos`, `estacionamento.orientacao_transporte`,
    `iluminacao.adicional_ou_cenica` e `suite_noiva.componentes` — e **5 artefatos
    removidos**: `estrutura.plano_chuva.descricao`, `estrutura.estacionamento.observacao`,
    `estrutura.iluminacao.observacao`, `estrutura.suite_noiva.inclui` e
    `estrutura.som.responsabilidade`. **Nenhuma cópia textual, campo legado, marcador de não
    autoritatividade ou comentário equivalente foi criado** para os artefatos removidos.
48. **Contrato materializado por alvo.** **`MD-8`** — a política de **toldos** é atomizada em
    `estrutura.plano_chuva.toldos`, com **cinco** booleanos —
    `permite_instalacao`, `contratacao_por_conta_do_contratante`,
    `custo_por_conta_do_contratante`, `instalacao_por_conta_do_contratante` e
    `responsabilidade_do_contratante` —; a descrição narrativa **deixa de existir** e
    `plano_chuva.disponivel` é preservado; **nenhum `toldos.incluido` foi criado**.
    **`MD-9`** — o fato de **estacionamento** e a orientação de transporte são atomizados em
    `estrutura.estacionamento.vagas_na_rua_limitadas` e em
    `estrutura.estacionamento.orientacao_transporte`, com **três** booleanos —
    `transporte_por_aplicativo`, `taxi` e `outro_transporte_alternativo` —; a observação
    narrativa **deixa de existir** e `disponivel: false` é preservado; **nenhuma lista foi
    criada** e **nenhum `orientacao_transporte.recomendada`** foi introduzido. **`MD-10`** —
    a responsabilidade de **som** deixa de ser texto e passa a ser o booleano
    `estrutura.som.responsabilidade_do_contratante`, **sem** manter string e booleano em
    paralelo, com `incluido: false` e `rede_eletrica` preservados; a **iluminação adicional
    ou cênica** é atomizada em `estrutura.iluminacao.adicional_ou_cenica`, com **três**
    booleanos — `contratacao_por_conta_do_contratante`,
    `instalacao_por_conta_do_contratante` e `responsabilidade_do_contratante` —, preservando
    `incluida` e `iluminacao_cenica_incluida` e removendo a observação narrativa; o bloco
    **`estrutura.gerador` permanece INTOCADO**, **idêntico ao parent**, sem chave nova, sem
    remoção e sem mudança de ordem. Com isso, os **seis referentes atômicos** exigidos por
    **`R25` `F2`** passam a existir na base: `som.incluido`,
    `iluminacao.iluminacao_cenica_incluida`, `som.responsabilidade_do_contratante`,
    `iluminacao.adicional_ou_cenica.responsabilidade_do_contratante`, `gerador.incluido` e
    `gerador.permite_instalacao` — **todos booleanos**. **`MD-11`** — a composição da
    **suíte da noiva** é atomizada em `estrutura.suite_noiva.componentes`, com **dois**
    booleanos — `sala_de_convivencia` e `banheiro_exclusivo` —; a **pseudo-lista `inclui`
    deixa de existir**; `disponivel`, `incluida_no_preco_padrao`, `contratacao` e `valor`
    são preservados, e **`valor` continua `null`**. **Nenhuma quantidade foi inferida** e
    **nenhum componente `suite` foi criado**: a existência da suíte continua representada
    por `suite_noiva.disponivel`. **`nao_incluido` permanece intocado**, com os mesmos
    **11** itens, mesmo conteúdo e mesma ordem — a redundância histórica ali existente
    **não é alvo deste pacote**. **Esta entrega altera a MODELAGEM da fonte, não o conteúdo
    emitível aprovado**: `knowledge/respostas-aprovadas.md` **não foi tocado**, e `R14`,
    `R22`, `R25` e `R28` permanecem com suas redações atuais.
49. **Estado das condições de materialização de C após `MD-8`, `MD-9`, `MD-10` e `MD-11`** —
    **registro histórico daquela entrega**, superado pelo item 53. **`C-A2-N9`** —
    **CUMPRIDA**. **`C-A2-N10`** — **CUMPRIDA**. **`C-A2-N11`** — alvos `MD` necessários —
    **continuava PENDENTE**: com aquela entrega passaram a ser **8 dos 16** alvos `MD`
    necessários cumpridos — **`MD-18`**, **`MD-20`**, **`MD-4`**, **`MD-17`**, **`MD-8`**,
    **`MD-9`**, **`MD-10`** e **`MD-11`** —, e **8 alvos `MD` permaneciam**. O
    **denominador continua 16**. **`C-A2-N12`** — validações `C-8` / `C-15` / `C-A1` —
    **continuava PENDENTE**. **Preservado expressamente naquela entrega**: **nenhum outro
    alvo `MD` foi executado**; **`FE-11b` NÃO foi aplicada**;
    **`knowledge/indice-respostas-aprovadas.yaml` continua inexistente**; **nenhum
    *template*, *binding* ou `ASSERTIVA` foi materializado**; e **`C` continua ARBITRADA /
    NÃO MATERIALIZADA**. **`R2` e `S2-D8` continuam NÃO MATERIALIZADAS**, **`N-b-RES2`
    continua ABERTO** e o **`OrquestradorMotor` continua não implementado**. **`MD-4`,
    `MD-17`, `MD-18` e `MD-20` permanecem íntegros**, assim como `versao` — que continua
    **`1.1`** — e `ultima_atualizacao`. **Aquela entrega não criou marco funcional de
    código**: o **último commit funcional aprovado continua
    `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`** (**PR #61**), a **baseline permaneceu
    `1215 passed`** — medida **antes** e **depois** da edição, com **contagem idêntica** e
    **100% verde** —, a **3B.7** continua a **última subetapa funcional numerada** e a
    **3B.8 continua inexistente**.
50. **A entrega M3 está INTEGRADA à `main` pelo PR #71** — commit
    `930b3c3c07d82f470bef0fc91e685f4257551b63`, merge
    `c46076659f79f5a9f5c63edc109e153bcd9724fa`, branch de origem
    `feat/c-a2-n11-m3-md8-md11`. **Dois** arquivos — `knowledge/casa77.yaml` e este
    documento —, **113 adições / 29 remoções**. **Modelagem da base autoritativa**: **não
    altera `src/` nem `tests/`** e **não cria marco funcional de código**. O merge foi feito
    por **merge commit**, com **dois parents** — `d48692e7810c5d10b2cd2e43adcca1d157d0bfd5`
    e o commit de conteúdo —, **sem squash, sem rebase e sem exclusão de branch**.
51. **A entrega anterior (M4) executou EXCLUSIVAMENTE os alvos `MD-12`, `MD-13` e `MD-19`.**
    Base: `c46076659f79f5a9f5c63edc109e153bcd9724fa`. **Classificação da entrega**:
    **MODELAGEM DA BASE AUTORITATIVA, SEM ALTERAÇÃO DE CÓDIGO E SEM NOVO MARCO FUNCIONAL DE
    CÓDIGO**. **Aquela entrega NÃO foi uma nova subetapa oficial do roadmap — a 3B.8
    continua inexistente.** Arquivos alterados: **dois** — `knowledge/casa77.yaml` e este documento.
    **Nenhum arquivo de `src/` e nenhum arquivo de `tests/` foi tocado**, e **nenhum teste
    foi alterado**. Todos os alvos aplicam **C-A1-M3 (A)** — **substituição** da
    representação narrativa ou pseudoestruturada por fatos atômicos, **sem** fonte factual
    paralela. **Balanço do YAML**: **13 adições e 18 remoções**, com **11 fatos booleanos
    novos**, **2 agrupamentos novos** — `fornecedores.perfil_buffet_recomendado` e
    `locacao_padrao` — e **7 artefatos removidos**: `fornecedores.recomendados`,
    `fornecedores.observacao`, `restricoes.fogos_motivo`, `restricoes.decoracao`,
    `equipe_incluida.governanta_funcao`, `equipe_incluida.observacao_limpeza` e
    `incluido_locacao_padrao`. **Nenhum inteiro, string ou lista nova foi criada**, e
    **nenhuma cópia textual, campo legado, marcador de não autoritatividade ou comentário
    equivalente** foi introduzido.
52. **Contrato materializado por alvo.** **`MD-12`** — os fatos de **fornecedores** são
    consolidados em fonte atômica: `fornecedores.recomenda_buffets` e o agrupamento
    `fornecedores.perfil_buffet_recomendado`, com **três** booleanos —
    `experiencia_previa_no_espaco`, `conhece_estrutura_da_casa` e `conhece_regras_da_casa`.
    A pseudo-lista `recomendados` e a prosa `observacao` **deixam de existir**;
    `obrigatorios` — que continua **lista vazia** — e `permite_fornecedor_proprio` são
    preservados. **Nenhuma lista nominal, nome de fornecedor, contato ou parceiro foi
    criado**: pedido de lista nominal continua sendo **`R03` + handoff**, e **`R24`
    permanece intocado**. **`MD-13`** — o **motivo legal/ambiental** da proibição de fogos é
    atomizado em `restricoes.fogos_proibicao_legal_por_area_ambiental`, e a política de
    **decoração** em `restricoes.decoracao_permitida` e
    `restricoes.decoracao_nao_pode_alterar_estrutura`; `fogos_motivo` e `decoracao`
    **deixam de existir**. A lista **`restricoes.proibido` permanece IDÊNTICA ao parent**,
    com os mesmos **7** itens e a mesma ordem — **a própria proibição de fogos não é
    duplicada**, e o **fato de dano continua coberto exclusivamente** por
    `restricoes.proibido`, sem `decoracao_nao_pode_causar_dano` ou equivalente. **`MD-19`** —
    `equipe_incluida.governanta_funcao` é substituída pelo booleano
    `governanta_auxilia_recepcao`, e `observacao_limpeza` pelo booleano
    `limpeza_durante_evento_responsabilidade_do_contratante`; `segurancas_externos`,
    `governanta`, `limpeza_pre_evento` e `limpeza_durante_evento` são **preservados
    exatamente**, e **`limpeza_pre_evento` continua fato distinto**. A pseudo-lista
    `incluido_locacao_padrao` é **removida** e substituída, no mesmo ponto de topo, pelo
    agrupamento `locacao_padrao`, com **dois** booleanos —
    `uso_das_areas_contratadas_incluido` e `limpeza_entrega_inicial_incluida`. **Mobiliário e
    as quantidades de equipe NÃO foram transferidos** para o novo agrupamento: esses fatos
    já têm autoridade estruturada própria em `mobiliario.incluido`,
    `equipe_incluida.segurancas_externos` e `equipe_incluida.governanta`, todos preservados.
    Com isso, os **seis referentes** exigidos por **`R12` `F1`** passam a existir na base:
    `locacao_padrao.uso_das_areas_contratadas_incluido`, `mobiliario.incluido`,
    `equipe_incluida.segurancas_externos` — **inteiro, não booleano** —,
    `equipe_incluida.governanta` — **inteiro, não booleano** —,
    `equipe_incluida.governanta_auxilia_recepcao` e
    `locacao_padrao.limpeza_entrega_inicial_incluida`. **Esta entrega altera a MODELAGEM da
    fonte, não o conteúdo emitível aprovado**: `knowledge/respostas-aprovadas.md` **não foi
    tocado**.
53. **Estado das condições de materialização de C após `MD-12`, `MD-13` e `MD-19`** —
    **registro histórico daquela entrega**, superado pelo item 57. **`C-A2-N9`** —
    **CUMPRIDA**. **`C-A2-N10`** — **CUMPRIDA**. **`C-A2-N11`** — alvos `MD` necessários —
    **continuava PENDENTE**: com aquela entrega passaram a ser **11 dos 16** alvos `MD`
    necessários cumpridos — **`MD-18`**, **`MD-20`**, **`MD-4`**, **`MD-17`**, **`MD-8`**,
    **`MD-9`**, **`MD-10`**, **`MD-11`**, **`MD-12`**, **`MD-13`** e **`MD-19`** —, e **5
    alvos `MD` permaneciam**: **`MD-2`**, **`MD-5`**, **`MD-6`**, **`MD-7′`** e **`MD-14`**.
    O **denominador continua 16**. **`C-A2-N12`** — validações `C-8` / `C-15` / `C-A1` —
    **continuava PENDENTE**. **Preservado expressamente naquela entrega**: **nenhum outro
    alvo `MD` foi executado**; **`FE-11b` NÃO foi aplicada**;
    **`knowledge/indice-respostas-aprovadas.yaml` continua inexistente**; **nenhum
    *template*, *binding* ou `ASSERTIVA` foi materializado**; e **`C` continua ARBITRADA /
    NÃO MATERIALIZADA**. **`R2` e `S2-D8` continuam NÃO MATERIALIZADAS**, **`N-b-RES2`
    continua ABERTO** e o **`OrquestradorMotor` continua não implementado**. **`MD-4`,
    `MD-8`, `MD-9`, `MD-10`, `MD-11`, `MD-17`, `MD-18` e `MD-20` permaneciam íntegros**,
    assim como `versao` — que continua **`1.1`** — e `ultima_atualizacao`. **Aquela entrega
    não criou marco funcional de código**: o **último commit funcional aprovado continua
    `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`** (**PR #61**), a **baseline permaneceu
    `1215 passed`** — medida **antes** e **depois** da edição, com **contagem idêntica** e
    **100% verde** —, a **3B.7** continua a **última subetapa funcional numerada** e a
    **3B.8 continua inexistente**.
54. **A entrega M4 está INTEGRADA à `main` pelo PR #72** — commit
    `b7f8e11c732d1c8cba6d6f34f5be2ea434351bec`, merge
    `3758b107aa9c96af1f25825e209588a3bb7841ea`, branch de origem
    `feat/c-a2-n11-m4-md12-md13-md19`. **Dois** arquivos — `knowledge/casa77.yaml` e este
    documento —, **111 adições / 33 remoções**. **Modelagem da base autoritativa**: **não
    altera `src/` nem `tests/`** e **não cria marco funcional de código**. O merge foi feito
    por **merge commit**, com **dois parents** — `c46076659f79f5a9f5c63edc109e153bcd9724fa`
    e o commit de conteúdo —, **sem squash, sem rebase e sem exclusão de branch**.
55. **A entrega anterior (M5) executou EXCLUSIVAMENTE os alvos `MD-2` e `MD-5`.** Base:
    `3758b107aa9c96af1f25825e209588a3bb7841ea`. **Classificação da entrega**: **MODELAGEM DA
    BASE AUTORITATIVA, SEM ALTERAÇÃO DE CÓDIGO E SEM NOVO MARCO FUNCIONAL DE CÓDIGO**.
    **Aquela entrega NÃO foi uma nova subetapa oficial do roadmap — a 3B.8 continua
    inexistente.** Arquivos alterados: **dois** — `knowledge/casa77.yaml` e este documento.
    **Nenhum arquivo de `src/` e nenhum arquivo de `tests/` foi tocado**, e **nenhum teste
    foi alterado**. Ambos os alvos aplicam **C-A1-M3 (A)** — **substituição** da
    representação composta ou narrativa por fatos atômicos, **sem** fonte factual paralela.
    **Balanço do YAML**: **10 adições e 3 remoções**. **Nenhuma cópia textual, campo legado,
    marcador de não autoritatividade ou comentário equivalente** foi introduzido.
56. **Contrato materializado por alvo.** **`MD-2`** — o **endereço composto** em campo único
    é **removido** e substituído por cobertura estrutural: `localizacao.logradouro` e
    `localizacao.numero` — este do tipo **string**, não inteiro —, a coleção
    `localizacao.localidades` e `localizacao.cep`, também **string**, com o hífen
    preservado. A coleção é **neutra**: registra apenas **localidades nomeadas usadas na
    composição do endereço**, com **dois** itens de **`id` e `nome`** apenas, **sem
    classificação geográfica** — não há bairro, distrito, ponto de referência nem região
    administrativa, porque essa categorização **não está confirmada**. Os identificadores
    estruturais seguem a **convenção arquitetural já existente** (**C-A1-S3**–**S4**) e
    **não reexecutam `MD-18`**: a contagem histórica daquele alvo **permanece inalterada**.
    **`cidade` e `estado` são preservados como autoridades já existentes**, assim como
    `regioes_principais`, `pode_informar_endereco_antes_qualificacao` e `google_maps_url` —
    que **continua `null`**. O **`cep` não participa** da composição emitida por **`R13`**,
    que **permanece intocado** e cuja redação foi **recomposta mecanicamente** a partir dos
    novos campos e comparada sob **NFC**, com **equivalência provada**. **`R01` continua
    `AGUARDA APROVAÇÃO`**: seu status e seu texto **não foram alterados**, e esta entrega
    apenas prova que as fontes estruturais existem. **`MD-5`** — a antecedência de
    **montagem** passa a fato numérico em
    `montagem_desmontagem.montagem_antecedencia_maxima_evento_horas`, do tipo **inteiro**,
    provado **inteiro e não booleano**, e a **desmontagem** passa a fato atômico booleano em
    `montagem_desmontagem.desmontagem_ate_um_dia_util_apos_evento`. As **duas representações
    narrativas** — `inicio_montagem` e `fim_desmontagem` — **deixam de existir**, sem cópia
    legada. **Nenhum formatador de "um" foi criado**, **nenhum campo inteiro foi criado para
    a desmontagem** e **nada foi inferido sobre "primeiro dia útil"**. **`R11` `F2` permanece
    intocado** e teve sua redação **recomposta e comparada sob NFC**, com **equivalência
    provada**. **Esta entrega altera a MODELAGEM da fonte, não o conteúdo emitível
    aprovado**: `knowledge/respostas-aprovadas.md` **não foi tocado**.
57. **Estado das condições de materialização de C após `MD-2` e `MD-5`** — **registro
    histórico daquela entrega**, superado pelo item 60. **`C-A2-N9`** —
    **CUMPRIDA**. **`C-A2-N10`** — **CUMPRIDA**. **`C-A2-N11`** — alvos `MD` necessários —
    **continua PENDENTE**: com aquela entrega passaram a ser **13 dos 16** alvos `MD` necessários
    cumpridos — **`MD-18`**, **`MD-20`**, **`MD-4`**, **`MD-17`**, **`MD-8`**, **`MD-9`**,
    **`MD-10`**, **`MD-11`**, **`MD-12`**, **`MD-13`**, **`MD-19`**, **`MD-2`** e
    **`MD-5`** —, e **3 alvos `MD` permanecem**: **`MD-6`**, **`MD-7′`** e **`MD-14`**. O
    **denominador continua 16**. **`C-A2-N12`** — validações `C-8` / `C-15` / `C-A1` —
    **continua PENDENTE**. **Preservado expressamente**: **nenhum outro alvo `MD` foi
    executado**; **`FE-11b` NÃO foi aplicada**; **`knowledge/indice-respostas-aprovadas.yaml`
    continua inexistente**; **nenhum *template*, *binding* ou `ASSERTIVA` foi
    materializado**; e **`C` continua ARBITRADA / NÃO MATERIALIZADA**. **`R2` e `S2-D8`
    continuam NÃO MATERIALIZADAS**, **`N-b-RES2` continua ABERTO** e o **`OrquestradorMotor`
    continua não implementado**. **`MD-4`, `MD-8`, `MD-9`, `MD-10`, `MD-11`, `MD-12`,
    `MD-13`, `MD-17`, `MD-18`, `MD-19` e `MD-20` permanecem íntegros**, assim como `versao` —
    que continua **`1.1`** — e `ultima_atualizacao`. **Esta entrega não cria marco funcional
    de código**: o **último commit funcional aprovado continua
    `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`** (**PR #61**), a **baseline permanece
    `1215 passed`** — medida **antes** e **depois** da edição, com **contagem idêntica** e
    **100% verde** —, a **3B.7** continua a **última subetapa funcional numerada** e a
    **3B.8 continua inexistente**.
58. **A entrega M5 está INTEGRADA à `main` pelo PR #73** — commit
    `b564a3e4d6515f4028c078f16ce52163e99893bc`, merge
    `6e79cbac502a81fa167d37ff41b33df9ec95c9d7`, branch de origem
    `feat/c-a2-n11-m5-md2-md5`. **Dois** arquivos — `knowledge/casa77.yaml` e este
    documento —, **95 adições / 21 remoções**. **Modelagem da base autoritativa**: **não
    altera `src/` nem `tests/`** e **não cria marco funcional de código**. O merge foi feito
    por **merge commit**, com **dois parents** — `3758b107aa9c96af1f25825e209588a3bb7841ea`
    e o commit de conteúdo —, **sem squash, sem rebase e sem exclusão de branch**.
59. **A entrega ANTERIOR materializou EXCLUSIVAMENTE a micro-arbitragem `C-A3`** — **registro
    histórico daquela entrega**, hoje **INTEGRADA à `main` pelo PR #74** (commit documental
    `b584d5f43bf022062e0c43bd60131f15ce29b716`, merge
    `224ae8fd8fe2c9430125df85733b90beb1b44ecb`, branch de origem
    `docs/c-a3-empresa-descricao-c`, **merge commit** com **dois parents**, **164 adições / 7
    remoções**). **O contrato `C-A3` registrado abaixo NÃO é reescrito por esta entrega.** Base
    daquela entrega:
    `6e79cbac502a81fa167d37ff41b33df9ec95c9d7`. **Classificação daquela entrega**: **DOCUMENTAL /
    GOVERNANÇA — SEM ALTERAÇÃO DE CÓDIGO, SEM ALTERAÇÃO DA BASE AUTORITATIVA E SEM NOVO
    MARCO FUNCIONAL DE CÓDIGO**. **Aquela entrega NÃO foi uma nova subetapa oficial do roadmap
    — a 3B.8 continua inexistente.** Arquivos alterados naquela entrega: **dois** —
    `docs/07-arquitetura-motor-respostas.md` e este documento. **`knowledge/casa77.yaml` NÃO
    foi tocado**, e **nenhum arquivo de `src/`, `tests/` ou `prompts/` foi alterado**.
    **Nenhum alvo `MD` foi executado.** **O que `C-A3` faz**: classifica normativamente **um
    único caminho** — **`empresa.descricao`** — como **texto institucional** que, **para os
    fins do contrato `C`**, **não é fonte factual comercial ou operacional**, **não pode ser
    referente de *binding***, **não pode ser referente de `RENDERIZADO`** e **não pode ser
    referente de `ASSERTIVA`**; seu conteúdo textual **não pode ser interpretado,
    decomposto, resumido nem inferido como fato** para `C`. O campo **permanece fisicamente
    no YAML sem qualquer alteração**, e essa permanência **satisfaz `C-A1-M3(B)`**:
    **explicitamente NÃO AUTORITATIVA e NÃO CONSUMÍVEL**. O tratamento é **análogo** ao que
    **`C-2m`**–**`C-2p`** e **`C-A1-B2`** já fixam para notas e instruções internas.
    **`P8` e `F1` permanecem íntegros**: `knowledge/casa77.yaml` **continua a fonte
    autoritativa de todo fato comercial e operacional** — `C-A3` **não abre exceção genérica
    ao YAML** e **não cria contradição normativa**. **Não generaliza**: **`empresa.nome`**,
    **`empresa.posicionamento`** e **`empresa.diferenciais` NÃO são classificados**, **não há
    regra por prefixo `empresa.*`**, **nenhuma inferência automática por tipo de campo** e
    **nenhuma classe expansível**. **`empresa.diferenciais` permanece INTACTO** e `C-A3`
    **não decide sua autoridade futura** — a expressão `"experiência intimista"` **não é
    objeto de `C-A3`**. Quanto à **emissão**, `C-A3` **não declara** que o campo "nunca pode
    ser emitido": decide **somente** a **não consumibilidade por `C`**, e **não decide**
    eventual uso textual institucional **fora** do contrato `C`.
60. **Estado das condições de materialização de C após `C-A3`** — **registro histórico daquela
    entrega, superado pelo item 61**. **`C-A2-N9`** —
    **CUMPRIDA**. **`C-A2-N10`** — **CUMPRIDA**. **`C-A2-N11`** — alvos `MD` necessários —
    **continua PENDENTE**: permanecem **13 dos 16** alvos `MD` necessários cumpridos —
    **`MD-18`**, **`MD-20`**, **`MD-4`**, **`MD-17`**, **`MD-8`**, **`MD-9`**, **`MD-10`**,
    **`MD-11`**, **`MD-12`**, **`MD-13`**, **`MD-19`**, **`MD-2`** e **`MD-5`** —, e **3
    alvos `MD` permanecem**: **`MD-6`**, **`MD-7′`** e **`MD-14`**. O **denominador continua
    16**, e **esta entrega não altera o contador**. **`MD-6` está planejado e pronto, mas NÃO
    foi executado.** **`MD-7′` continua NÃO EXECUTADO**: `C-A3` **remove exclusivamente o
    bloqueio normativo** que a autoridade narrativa potencialmente paralela de
    `empresa.descricao` representava para ele — e esse efeito só vale **após a integração
    desta arbitragem à `main`**. **`MD-14` continua NÃO EXECUTADO.** **`C-A2-N12`** —
    validações `C-8` / `C-15` / `C-A1` — **continua PENDENTE**. **Preservado expressamente**:
    **`FE-11a` continua intacta** e **`FE-11b` continua NÃO APLICADA / RETIDA** atrás de
    **`C-A1-M4`** — `C-A3` **não absorve, não substitui, não antecipa e não altera** nenhuma
    das duas, e **`eventos.observacao_nao_aceitos` não é objeto de `C-A3`**;
    **`knowledge/indice-respostas-aprovadas.yaml` continua inexistente**; **nenhum
    *template*, *binding* físico ou `ASSERTIVA` física foi materializado**; e **`C` continua
    ARBITRADA / NÃO MATERIALIZADA**. **`R2` e `S2-D8` continuam NÃO MATERIALIZADAS**,
    **`N-b-RES2` continua ABERTO** e o **`OrquestradorMotor` continua não implementado**.
    **`C-A3` não cria** status, enum, predicado, formato, *binding* físico, metadado ou
    *flag* YAML, componente, responsabilidade, estado, evento, transição, condição, erro,
    cenário, pendência operacional nem subetapa. **Esta entrega não cria marco funcional de
    código**: o **último commit funcional aprovado continua
    `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`** (**PR #61**), e a **baseline registrada
    permanece `1215 passed`** — **não reexecutada nesta entrega**, por ser **exclusivamente
    documental**, **sem tocar `src/`, `tests/`, `knowledge/` ou `prompts/`**. A **3B.7**
    continua a **última subetapa funcional numerada** e a **3B.8 continua inexistente**.
    **`M6` NÃO era executada naquela entrega.** Sua execução permanecia **condicionada à
    integração de `C-A3` à `main`** e a **novo mandato**. **Essa condição foi SATISFEITA pelo
    merge do PR #74** — `224ae8fd8fe2c9430125df85733b90beb1b44ecb` —, e o **novo mandato** foi
    emitido: `M6` é a **presente entrega**, registrada no **item 61**.
61. **A entrega ANTERIOR (`M6`) executou EXCLUSIVAMENTE os alvos `MD-6` e `MD-7′`** —
    **registro histórico daquela entrega**, hoje **INTEGRADA à `main` pelo PR #75**. Base:
    `224ae8fd8fe2c9430125df85733b90beb1b44ecb`. **Classificação da entrega**: **MODELAGEM DA
    BASE AUTORITATIVA, SEM ALTERAÇÃO DE CÓDIGO E SEM NOVO MARCO FUNCIONAL DE CÓDIGO**. **Esta
    entrega NÃO é uma nova subetapa oficial do roadmap — a 3B.8 continua inexistente.**
    Arquivos alterados: **dois** — `knowledge/casa77.yaml` e este documento. **Nenhum arquivo
    de `src/`, `tests/` ou `prompts/` foi tocado**, e **nenhum teste foi alterado**.
    `knowledge/respostas-aprovadas.md` **não foi tocado**. **Balanço do YAML**: **2 adições e 3
    remoções**, em **duas hunks**. **Nenhuma cópia textual, campo legado, marcador de não
    autoritatividade ou comentário equivalente** foi introduzido. **Auditoria `C-A1-M4`
    reexecutada antes da edição**: `capacidade.minimo_convidados`, `capacidade.observacao_minimo`
    e `eventos.perfil_ideal` tinham **o próprio YAML como única fonte** e **zero consumidor
    funcional** em todo o repositório — as ocorrências restantes em `docs/07` são
    **documentais/normativas**, não dereferência de chave.
    **Contrato materializado por alvo.** **`MD-6`** — a representação ambígua *campo nulo +
    observação* deixa de existir: `capacidade.minimo_convidados` e
    `capacidade.observacao_minimo` são **removidos** e substituídos pelo fato atômico
    **`capacidade.existe_minimo_convidados`**, **booleano real** de valor **`false`**, com a
    semântica *"existe quantidade mínima de convidados exigida"*. O consumo futuro é
    `ASSERTIVA` **`EH_FALSO`**. **Nenhum campo legado, observação, comentário, alias,
    quantidade `0`, string `"false"` ou segunda fonte** foi criado — aplicação estrita de
    **C-A1-M3 (A)**. **`A2` já estava satisfeita por C-A2**, e **C-7 continua preservada**: a
    representação agora é **explícita e atômica** — predicado afirmativo com valor booleano
    **`false`** — e não depende de interpretar `null`. `convidados_sentados` e
    `formato_coquetel` **permanecem intactos**. **`MD-7′`** — `eventos.perfil_ideal` é
    **removido** e substituído pelo fato atômico **`eventos.perfil_intimista`**, **booleano
    real** de valor **`true`**, com a semântica *"o perfil de evento da casa é intimista"*. O
    consumo futuro é `ASSERTIVA` **`EH_VERDADEIRO`**, para **`R16`** e **`R17`**, pela **mesma
    chave** e **sem segunda fonte**. **Nenhuma string `"intimista"`, enum, pluralizador,
    conversor de caixa, segunda chave, campo legado ou comentário narrativo** foi criado. O
    efeito de **`C-A3`**, já integrado à `main`, é **pré-condição consumida aqui**:
    `empresa.descricao` é **NÃO AUTORITATIVA e NÃO CONSUMÍVEL** por `C`, e por isso **não é
    fonte paralela** do perfil intimista. **`C-A3` não é reaberta, reinterpretada nem
    ampliada**: `empresa.descricao`, `empresa.nome`, `empresa.posicionamento` e
    `empresa.diferenciais` **não foram alterados**, e a expressão `"experiência intimista"`
    **não é objeto desta entrega**. **`R10`, `R16` e `R17` NÃO foram alterados**: suas
    redações foram **recompostas mecanicamente** a partir dos novos fatos e comparadas sob
    **NFC**, com **equivalência provada**. **Esta entrega altera a MODELAGEM da fonte, não o
    conteúdo emitível aprovado.**
    **Estado das condições de materialização de C após `M6`.** **`C-A2-N9`** — **CUMPRIDA**.
    **`C-A2-N10`** — **CUMPRIDA**. **`C-A2-N11`** — alvos `MD` necessários — **continua
    PENDENTE**: com esta entrega passam a ser **15 dos 16** alvos `MD` necessários cumpridos —
    **`MD-18`**, **`MD-20`**, **`MD-4`**, **`MD-17`**, **`MD-8`**, **`MD-9`**, **`MD-10`**,
    **`MD-11`**, **`MD-12`**, **`MD-13`**, **`MD-19`**, **`MD-2`**, **`MD-5`**, **`MD-6`** e
    **`MD-7′`** —, e **1 alvo `MD` permanece**: **`MD-14`**. O **denominador continua 16**.
    **`MD-14` continua NÃO EXECUTADO**, e `processo_comercial.visitas.*` **permanece intacto**.
    **`C-A2-N12`** — validações `C-8` / `C-15` / `C-A1` — **continua PENDENTE**. **Preservado
    expressamente**: **nenhum outro alvo `MD` foi executado**; **`FE-11a` continua intacta** e
    **`FE-11b` continua NÃO APLICADA / RETIDA** atrás de **`C-A1-M4`**;
    **`eventos.observacao_nao_aceitos` não foi tocado**;
    **`knowledge/indice-respostas-aprovadas.yaml` continua inexistente**; **nenhum *template*,
    *binding* físico ou `ASSERTIVA` física foi materializado**; e **`C` continua ARBITRADA /
    NÃO MATERIALIZADA**. **`R2` e `S2-D8` continuam NÃO MATERIALIZADAS**, **`N-b-RES2` continua
    ABERTO** e o **`OrquestradorMotor` continua não implementado**. Os **13 alvos `MD`
    anteriores permanecem íntegros**, assim como `versao` — que continua **`1.1`** — e
    `ultima_atualizacao` — que continua **`2026-08-15`**. **Esta entrega não cria marco
    funcional de código**: o **último commit funcional aprovado continua
    `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`** (**PR #61**), a **baseline permanece
    `1215 passed`** — medida **antes** e **depois** da edição, com **contagem idêntica** e
    **100% verde** —, a **3B.7** continua a **última subetapa funcional numerada** e a **3B.8
    continua inexistente**. **`M7` NÃO é escolhida por esta entrega**, e **`MD-14` não é
    executado**: qualquer passo seguinte depende de **novo mandato**.
62. **A entrega M6 está INTEGRADA à `main` pelo PR #75** — commit
    `5520cd77df8131eb4ba1093b6929e693547a5141`, merge
    `9b44cc1c01403ce5e9bb4997088d75c9da207c28`, branch de origem
    `feat/c-a2-n11-m6-md6-md7`. **Dois** arquivos — `docs/00-estado-atual.md` e
    `knowledge/casa77.yaml` —, **86 adições / 13 remoções**. **Modelagem da base
    autoritativa**: **não altera `src/` nem `tests/`** e **não cria marco funcional de
    código**. O merge foi feito por **merge commit**, com **dois parents** —
    `224ae8fd8fe2c9430125df85733b90beb1b44ecb` e o commit de conteúdo
    `5520cd77df8131eb4ba1093b6929e693547a5141` —, **sem squash, sem rebase e sem exclusão
    de branch**.
63. **A entrega ANTERIOR (`M7`) executou EXCLUSIVAMENTE o alvo `MD-14`** — **registro
    histórico daquela entrega**, hoje **INTEGRADA à `main` pelo PR #76** —, mais a
    **reconciliação normativa estritamente necessária** da célula **“Ação obrigatória”** da
    transição **T16** em `docs/06-maquina-de-estados.md`. Base:
    `9b44cc1c01403ce5e9bb4997088d75c9da207c28`. **Classificação da entrega**: **MODELAGEM
    DA BASE AUTORITATIVA + RECONCILIAÇÃO DOCUMENTAL VINCULADA, SEM ALTERAÇÃO DE CÓDIGO E
    SEM NOVO MARCO FUNCIONAL DE CÓDIGO**. **Esta entrega NÃO é uma nova subetapa oficial do
    roadmap — a 3B.8 continua inexistente.** Arquivos alterados: **três** —
    `knowledge/casa77.yaml`, `docs/06-maquina-de-estados.md` e este documento. **Nenhum
    arquivo de `src/`, `tests/` ou `prompts/` foi tocado**, e **nenhum teste foi alterado**.
    `knowledge/respostas-aprovadas.md`, `knowledge/informacoes-pendentes.md`,
    `docs/04-handoff-humano.md` e `docs/07-arquitetura-motor-respostas.md` **não foram
    tocados**. **Balanço do YAML**: **2 adições e 2 remoções**, em **uma única hunk**;
    **balanço de `docs/06`**: **1 adição e 1 remoção**, em **uma única hunk**,
    **exclusivamente na célula “Ação obrigatória” de T16**. **Nenhuma cópia textual, alias,
    campo legado, comentário equivalente, enum, identificador de papel ou segunda fonte**
    foi introduzido. **Auditoria `C-A1-M4` reexecutada antes da edição**:
    `responsavel_confirmacao` tinha **o próprio YAML como única fonte** e **zero
    consumidor** em todo o repositório; `responsavel_visita` tinha **o YAML como fonte** e
    **uma única dereferência normativa documental** — a célula de **T16** em `docs/06` —,
    com **zero consumidor funcional** em `src/` e `tests/`, onde
    `processo_comercial.visitas.*` **não é lido por código ou teste algum**.
    **Contrato materializado.** **`MD-14`** — as **duas cópias de nome próprio** em
    `processo_comercial.visitas` são **removidas** e substituídas por **fatos de papel e
    relação**: **`processo_comercial.visitas.realizada_pelo_responsavel_comercial`**,
    **booleano real** de valor **`true`**, com a semântica *“a visita é realizada pelo
    responsável comercial”*; e
    **`processo_comercial.visitas.confirmacao_horario_pelo_responsavel_comercial`**,
    **booleano real** de valor **`true`**, com a semântica *“a confirmação do horário da
    visita é feita pelo responsável comercial”*. O consumo futuro de ambos é `ASSERTIVA`
    **`EH_VERDADEIRO`**. **Nenhum nome próprio, enum, identificador de papel, string
    “responsável comercial”, string “true”, campo legado, alias, comentário ou segunda
    fonte** foi criado — aplicação estrita de **C-A1-M3 (A)**. **`A1` é preservada**: o
    tratamento emitido continua **estático** — **“responsável comercial”** —, e `R06` deixa
    de depender de igualdade entre *strings* de pessoas. `bot_pode_confirmar`,
    `duracao_estimada_minutos.minimo`, `duracao_estimada_minutos.maximo` e
    `depende_aprovacao_humana` **permanecem intactos**, assim como
    `processo_comercial.responsavel.*`, `processo_comercial.horario_atendimento.*` e
    `processo_comercial.contratacao.*` — **`processo_comercial.responsavel.funcao` NÃO é
    *binding* de `R06`** e **não é segunda fonte** da relação operacional específica da
    visita. **Autoridade única (C-A1-M3)**: a **única fonte factual** do papel de
    realização é `realizada_pelo_responsavel_comercial`; a **única fonte factual** do papel
    de confirmação de horário é `confirmacao_horario_pelo_responsavel_comercial`;
    **`responsavel_confirmacao` e `responsavel_visita` deixam de existir**, e **nenhum nome
    próprio sustenta `R06`**. **`R06` NÃO foi alterado**: sua redação foi **recomposta
    mecanicamente** a partir dos novos fatos — duas `ASSERTIVA` **`EH_VERDADEIRO`**, dois
    `RENDERIZADO` de inteiro (**30** e **40**), a `ASSERTIVA` **`EH_FALSO`**
    **consistency-only** sobre `bot_pode_confirmar` e o tratamento **estático** — e
    comparada sob **NFC**, com **equivalência integral provada**. **Nenhum formatador e
    nenhum predicado novo** foi criado.
    **Reconciliação de `docs/06` T16.** A célula **“Ação obrigatória”** de **T16**
    dereferenciava `processo_comercial.visitas.responsavel_visita`, caminho que **deixa de
    existir**. Ela passa a referenciar a **duração estimada** e os **dois papéis
    estruturais**, e explicita que a emissão usa o **tratamento estático “responsável
    comercial”** pela resposta aprovada **`R06`**. **Preservados sem alteração**: o **estado
    atual**, o **evento `E10`**, a **condição**, o **próximo estado**, a **ação proibida** —
    *marcar, sugerir horário ou confirmar visita* — e a **qualificação**. **Nenhuma outra
    linha, célula, transição ou seção de `docs/06` foi tocada.** **Esta entrega altera a
    MODELAGEM da fonte e a REFERÊNCIA normativa dependente, não o conteúdo emitível
    aprovado.**
    **Estado das condições de materialização de C após `M7`.** **`C-A2-N9`** — **CUMPRIDA**.
    **`C-A2-N10`** — **CUMPRIDA**. **`C-A2-N11`** — alvos `MD` necessários — passa a
    **CUMPRIDA**: com esta entrega são **16 dos 16** alvos `MD` necessários cumpridos —
    **`MD-18`**, **`MD-20`**, **`MD-4`**, **`MD-17`**, **`MD-8`**, **`MD-9`**, **`MD-10`**,
    **`MD-11`**, **`MD-12`**, **`MD-13`**, **`MD-19`**, **`MD-2`**, **`MD-5`**, **`MD-6`**,
    **`MD-7′`** e **`MD-14`** —, e **nenhum alvo `MD` permanece**. O **denominador continua
    16**. **`C-A2-N11` CUMPRIDA — 16/16 NÃO significa** que **`C-A2-N12`** esteja cumprida,
    que **`C`** esteja materializada, que o **índice** exista, que exista ***template***,
    ***binding* físico** ou **`ASSERTIVA` física**, que **`S2-D8`** esteja materializada,
    que **`N-b-RES2`** esteja fechado ou que o **`OrquestradorMotor`** esteja implementado.
    **`C-A2-N12`** — validações `C-8` / `C-15` / `C-A1` — **continua PENDENTE**.
    **Preservado expressamente**: **`FE-11a` continua intacta** e **`FE-11b` continua NÃO
    APLICADA / RETIDA** atrás de **`C-A1-M4`**, **fora desta entrega**; **`FE-11a′` NÃO foi
    executada**; **`eventos.observacao_nao_aceitos` não foi tocado**;
    **`materiais.observacao_envio`, `tests/cenarios-conversa.md` e
    `tests/perguntas-criticas.md` não foram tocados**;
    **`knowledge/indice-respostas-aprovadas.yaml` continua inexistente**; **nenhum
    *template*, *binding* físico ou `ASSERTIVA` física foi materializado**; e **`C` continua
    ARBITRADA / NÃO MATERIALIZADA**. **`R2` e `S2-D8` continuam NÃO MATERIALIZADAS**,
    **`N-b-RES2` continua ABERTO** e o **`OrquestradorMotor` continua não implementado**. Os
    **15 alvos `MD` anteriores permanecem íntegros**, assim como `versao` — que continua
    **`1.1`** — e `ultima_atualizacao` — que continua **`2026-08-15`**. **Esta entrega não
    cria marco funcional de código**: o **último commit funcional aprovado continua
    `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`** (**PR #61**), a **baseline permanece
    `1215 passed`** — medida **antes** e **depois** da edição, com **contagem idêntica** e
    **100% verde** —, a **3B.7** continua a **última subetapa funcional numerada** e a
    **3B.8 continua inexistente**. **`M8` NÃO é iniciada por esta entrega**: qualquer passo
    seguinte depende de **novo mandato**.
64. **A entrega M7 está INTEGRADA à `main` pelo PR #76** — commit
    `9a56fa80bbc312b2085480f87e572ff6e0f768b3`, merge
    `f446d3fa36a9b3f4b76c3b329a19356b3ddbe394`, branch de origem
    `feat/c-a2-n11-m7-md14`. **Três** arquivos — `docs/00-estado-atual.md`,
    `docs/06-maquina-de-estados.md` e `knowledge/casa77.yaml` —, **109 adições / 9
    remoções**. **Modelagem da base autoritativa + reconciliação documental vinculada**:
    **não altera `src/` nem `tests/`** e **não cria marco funcional de código**. O merge
    foi feito por **merge commit**, com **dois parents** —
    `9b44cc1c01403ce5e9bb4997088d75c9da207c28` e o commit de conteúdo
    `9a56fa80bbc312b2085480f87e572ff6e0f768b3` —, **sem squash, sem rebase e sem exclusão
    de branch**. **Com este merge, `C-A2-N11` = CUMPRIDA — 16/16 passou a ser o ESTADO
    OFICIAL da `main`**, e **nenhum alvo `MD` necessário permanece**.
65. **A entrega ANTERIOR (`M8`) executou EXCLUSIVAMENTE `FE-11b` e a reconciliação da
    `FE-11a` já aplicada** — **registro histórico daquela entrega**, hoje **INTEGRADA à
    `main` pelo PR #77**. Base: `f446d3fa36a9b3f4b76c3b329a19356b3ddbe394`.
    **Classificação da entrega**: **MODELAGEM / RECONCILIAÇÃO DA BASE AUTORITATIVA +
    RECONCILIAÇÃO DE INSTRUÇÃO INTERNA, SEM ALTERAÇÃO DE CÓDIGO E SEM NOVO MARCO
    FUNCIONAL**. **Esta entrega NÃO é uma nova subetapa oficial do roadmap — a 3B.8
    continua inexistente.** Arquivos alterados: **três** — `knowledge/casa77.yaml`,
    `knowledge/respostas-aprovadas.md` e este documento. **Nenhum arquivo de `src/`,
    `tests/` ou `prompts/` foi tocado**, e **nenhum teste foi alterado**.
    `knowledge/informacoes-pendentes.md`, `docs/02-fluxo-comercial.md`,
    `docs/03-regras-de-conversa.md`, `docs/04-handoff-humano.md`,
    `docs/06-maquina-de-estados.md` e `docs/07-arquitetura-motor-respostas.md` **não foram
    tocados**. **Balanço do YAML**: **0 adições e 5 remoções**, em **uma única hunk**;
    **balanço de `knowledge/respostas-aprovadas.md`**: **6 adições e 7 remoções**, em
    **duas alterações distintas e não adjacentes** — a linha de origem de `R17` e o bloco
    de instrução interna —, separadas por quatro linhas inalteradas, que o `git diff` com
    contexto padrão exibe **coalescidas em uma hunk** e que `-U1` separa em **duas**.
    **Auditoria `C-A1-M4` reexecutada antes da edição**: o campo removido tinha **o YAML
    como fonte física**, **uma origem declarada** e **uma referência normativa viva** —
    ambas em `knowledge/respostas-aprovadas.md` —, além de **referências históricas** em
    `docs/07` e neste documento, e **ZERO consumidor funcional** em `src/` e `tests/`.
    **`FE-11b` — materialização por REMOÇÃO.** O campo narrativo de `eventos` que
    duplicava a classificação já estruturada e carregava **vetor nominal**, **proveniência
    interna de decisão** e **motivo operacional sem representação estrutural** é
    **removido integralmente**. **Nenhum substituto foi criado**: nenhum campo novo,
    narrativa sanitizada, comentário, alias, enum, booleano, motivo, proveniência, data ou
    nome próprio. Aplicação estrita de **C-A1-M3 (A)** — a representação narrativa é
    **substituída pela ausência**, e **não** por uma segunda fonte factual paralela.
    **`eventos.aceitos`, `eventos.perfil_intimista`, `eventos.nao_aceitos` e
    `eventos.datas_nao_aceitas` permanecem intactos** — `nao_aceitos` conserva os mesmos
    **oito** itens, na mesma ordem —, assim como `versao`, que continua **`1.1`**, e
    `ultima_atualizacao`, que continua **`2026-08-15`**.
    **`R17` — texto emitível INALTERADO.** O fragmento aprovado **não foi tocado** e é
    **byte-idêntico** ao blob de `origin/main`. Apenas a **linha de origem** foi
    reconciliada: a fonte declarada passa a ser `eventos.nao_aceitos` e
    `eventos.perfil_intimista` (**D-M8-1**), **sem qualquer outra fonte**. A linha
    **“Aplica-se a”** foi **preservada integral e textualmente** (**D-M8-2**): nenhum item
    adicionado ou removido, nenhuma data ou arbitragem alterada, nenhuma normalização de
    redação. **A divergência preexistente entre essa enumeração e `eventos.nao_aceitos`
    permanece FORA de `M8`** e **não foi corrigida** — ela continua registrada como
    conflito em **`C-9`**.
    **`FE-11a` — RECONCILIADA, sem novo identificador.** A instrução interna já aplicada
    referenciava o campo removido; ela foi **reescrita no lugar**, permanecendo
    **`FE-11a`**, **não emitível** e ancorada em **`R03` + handoff** para pedido
    específico do motivo. **`FE-11a′` NÃO foi criada**: as menções anteriores a
    **`FE-11a′`** em planejamento e em registro de entrega **não criaram identificador
    normativo novo**, e nenhum foi criado aqui. A nova redação **não menciona o campo
    removido**, **não reconstrói a narrativa**, **não cria explicação comercial** e **não
    cria fato novo**.
    **`docs/07` NÃO foi alterado.** As referências históricas ali — ao campo removido, a
    **`FE-11a`** como planejada e a **`FE-11b`** como retida — **permanecem registro
    histórico correto para o momento em que foram escritas** (**C-A2-H2**) e **não são
    reconciliadas retrospectivamente**. Vale o mesmo para os itens históricos deste
    documento: as declarações anteriores de **`FE-11b` NÃO APLICADA / RETIDA** continuam
    corretas à época e **não foram reescritas** — elas apenas **deixam de representar o
    estado corrente** após a futura integração de `M8`.
    **Estado após `M8` — NA BRANCH.** **`C-A2-N9`** — **CUMPRIDA**. **`C-A2-N10`** —
    **CUMPRIDA**. **`C-A2-N11`** — **CUMPRIDA — 16/16**, **nenhum alvo `MD` restante**.
    **`C-A2-N12`** — validações `C-8` / `C-15` / `C-A1` — **continua PENDENTE**.
    **`FE-11b`** — **APLICADA / MATERIALIZADA POR REMOÇÃO**. **`FE-11a`** — **APLICADA /
    RECONCILIADA**. **`FE-11a′`** — **NÃO CRIADA**.
    **`knowledge/indice-respostas-aprovadas.yaml` continua inexistente**; **nenhum
    *template*, *binding* físico ou `ASSERTIVA` física foi materializado**; **`C` continua
    ARBITRADA / NÃO MATERIALIZADA**; **`R2` continua NÃO MATERIALIZADA**; **`S2-D8`
    continua ARBITRADA / NÃO MATERIALIZADA**; **`N-b-RES2` continua ABERTO** e o
    **`OrquestradorMotor` continua não implementado**. **Esta entrega não cria marco
    funcional de código**: o **último commit funcional aprovado continua
    `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`** (**PR #61**), a **baseline permanece
    `1215 passed`** — medida **antes** e **depois** da edição, com **contagem idêntica** e
    **100% verde** —, a **3B.7** continua a **última subetapa funcional numerada** e a
    **3B.8 continua inexistente**. **Este estado é da BRANCH**: ele só se torna estado
    oficial da `main` após o merge de `M8`.
66. **A entrega M8 está INTEGRADA à `main` pelo PR #77** — commit
    `e632ae71e043568f19ed26bf0101eb214d87a2f9`, merge
    `c36529c7323e2f2030b9c6664292594203226ac4`, branch de origem `feat/c-a2-m8-fe11b`.
    **Três** arquivos — `docs/00-estado-atual.md`, `knowledge/casa77.yaml` e
    `knowledge/respostas-aprovadas.md` —, **98 adições / 18 remoções**. **Modelagem /
    reconciliação da base autoritativa + reconciliação de instrução interna**: **sem
    alteração de código** e **sem novo marco funcional**. O merge foi feito por **merge
    commit**, com **dois parents** — `f446d3fa36a9b3f4b76c3b329a19356b3ddbe394` e o commit
    de conteúdo `e632ae71e043568f19ed26bf0101eb214d87a2f9` —, **sem squash, sem rebase e
    sem exclusão de branch**. **Com este merge passam a ser ESTADO OFICIAL da `main`**:
    **`FE-11b` = APLICADA / MATERIALIZADA POR REMOÇÃO**; **`FE-11a` = APLICADA /
    RECONCILIADA**; **`FE-11a′` = NÃO CRIADA**. **`C-A2-N12` permanece PENDENTE**, e
    **nenhuma outra condição de `C` foi implicitamente satisfeita** além do que já estava
    registrado: **`C` continua ARBITRADA / NÃO MATERIALIZADA**, o **índice**
    `knowledge/indice-respostas-aprovadas.yaml` **continua inexistente**, **`R2` continua
    NÃO MATERIALIZADA**, **`S2-D8` continua ARBITRADA / NÃO MATERIALIZADA**, **`N-b-RES2`
    continua ABERTO** e o **`OrquestradorMotor` continua não implementado**. **Nenhum
    marco funcional foi criado**: o **último commit funcional aprovado continua
    `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`** (**PR #61**, merge
    `5a722a5cc648149330362434694e7e76a40c1b57`), a **baseline permanece `1215 passed`**, a
    **3B.7** continua a **última subetapa funcional numerada** e a **3B.8 continua
    inexistente**.
67. **A presente entrega é EXCLUSIVAMENTE a reconciliação documental de `docs/00` após o
    PR #77.** Base: `c36529c7323e2f2030b9c6664292594203226ac4`. **Classificação da
    entrega**: **RECONCILIAÇÃO DOCUMENTAL, SEM ALTERAÇÃO DE FONTE FACTUAL, SEM ALTERAÇÃO
    DE CÓDIGO E SEM NOVO MARCO FUNCIONAL**. Arquivo alterado: **um** — este documento.
    **`knowledge/**`, `src/**`, `tests/**`, `prompts/**`, `docs/06` e `docs/07` NÃO foram
    tocados**, e **nenhum teste foi alterado**. Ela **não altera comportamento nem fonte
    factual**: apenas passa a ler `M8` como **integrada**, registra a evidência do **PR
    #77** e fixa o **estado oficial** resultante. **Estado oficial da `main` após o PR
    #77**: **`C-A2-N9` CUMPRIDA**; **`C-A2-N10` CUMPRIDA**; **`C-A2-N11` CUMPRIDA —
    16/16**, sem alvo `MD` restante; **`C-A2-N12` PENDENTE**; **`FE-11b` APLICADA /
    MATERIALIZADA POR REMOÇÃO**; **`FE-11a` APLICADA / RECONCILIADA**; **`FE-11a′` NÃO
    CRIADA**; **`knowledge/indice-respostas-aprovadas.yaml` INEXISTENTE**; **`C` ARBITRADA
    / NÃO MATERIALIZADA**; **`R2` NÃO MATERIALIZADA**; **`S2-D8` ARBITRADA / NÃO
    MATERIALIZADA**; **`N-b-RES2` ABERTO**; **`OrquestradorMotor` NÃO IMPLEMENTADO**;
    **último marco funcional `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`** (**PR #61**);
    **3B.7** como **última subetapa funcional numerada**; **3B.8 INEXISTENTE**.
    **PRÓXIMA AÇÃO.** O próximo gate técnico é o **PLANEJAMENTO READ-ONLY de `C-A2-N12`**
    — validações `C-8` / `C-15` / `C-A1` —, e ele **depende de NOVO MANDATO do GPT**.
    **`C-A2-N12` NÃO é planejada, decidida nem executada aqui**: **nenhum mecanismo técnico
    é escolhido**, **nenhum índice, *template*, *binding* físico ou `ASSERTIVA` física é
    criado**, **`C` e `S2-D8` não são materializadas**, **`N-b-RES2` não é fechado**, o
    **`OrquestradorMotor` não é implementado** e a **subetapa 3B.8 não é criada**.
68. **A entrega ANTERIOR foi EXCLUSIVAMENTE a micro-arbitragem documental `C-A4`** —
    **registro histórico daquela entrega**, hoje **INTEGRADA à `main` pelo PR #79**. Base:
    `2dd6536398d3c6c0ea62934c4c88b53263cc385f`. **Classificação da entrega**:
    **ARBITRAGEM DOCUMENTAL, SEM ALTERAÇÃO DE FONTE FACTUAL, SEM ALTERAÇÃO DE CÓDIGO E SEM
    NOVO MARCO FUNCIONAL**. **Objetivo**: fechar, para a execução futura e **read-only** de
    **`C-A2-N12`**, o **critério de cumprimento** do gate (**`C-A4-G`**); o **vocabulário
    da auditoria** (**`C-A4-VOC`**); a **convenção fechada de `inteiro_agrupado`**
    (**`C-A4-F1`**, refinamento posterior de `C-6b` e `C-A1-F1`); a **fronteira de
    `simbolo_moeda`** (**`C-A4-F2`**, sem ampliar a tabela e sem regra nova de
    espaçamento); a **derivação conceitual de *bindings*** onde `C-A2-B` não prescreve
    (**`C-A4-DB`**); o tratamento de **`R05` `F2`/`F3`** (**`C-A4-NA`**); e a **proposição
    completa** como unidade de análise de `C-8` (**`C-A4-P`**). Também registra a
    **preservação histórica** (**`C-A4-H`**) e a **não reescrita / não revogação**
    (**`C-A4-X`**). Arquivos alterados: **dois** — `docs/07-arquitetura-motor-respostas.md`
    e este documento. Em `docs/07` a entrega é **PURAMENTE ADITIVA**: **um único bloco novo
    contíguo**, inserido **após o parágrafo final de `C-A3-X`** e **antes do separador que
    antecede a §3**, com **ZERO remoções** e **ZERO alteração de linha preexistente** —
    **`C-15d`**, **`C-A1-F1`**, **`C-A1-ST`**, **`C-A2-N`**, **`C-A2-RT7`**, **todo o bloco
    `C-A3`** e a **§12** permanecem **byte-idênticos**.
    **Nenhuma fonte factual foi alterada**: `knowledge/**` **não foi tocado**, e
    `knowledge/casa77.yaml` e `knowledge/respostas-aprovadas.md` permanecem **intactos**.
    **Nenhum arquivo de `src/`, `tests/` ou `prompts/` foi tocado**, **nenhum teste foi
    alterado** e **nenhum outro `docs/**` foi alterado** — em particular **`docs/06` não foi
    tocado**. **Nenhum índice foi criado**: `knowledge/indice-respostas-aprovadas.yaml`
    **continua inexistente**. **`C-A4` não cria** *template* físico, *binding* físico,
    `ASSERTIVA` física, status, quarto status, formato novo, predicado novo, metadado ou
    *flag* YAML, componente, responsabilidade, estado, evento, transição, condição de ciclo,
    `E09`, erro, cenário nem subetapa. **`C-A4` não julga nenhum `Rxx`** e **não declara
    `37/37` alcançado**.
    **Estado após `C-A4`.** **`C-A4` = ARBITRADA DOCUMENTALMENTE**.
    **`C-A2-N9`** — **CUMPRIDA**. **`C-A2-N10`** — **CUMPRIDA**. **`C-A2-N11`** —
    **CUMPRIDA — 16/16**. **`C-A2-N12`** — **continua PENDENTE**: **`C-A4` NÃO a executa e
    NÃO antecipa seu resultado**. **`C` continua ARBITRADA / NÃO MATERIALIZADA**; **`R2`
    continua NÃO MATERIALIZADA**; **`S2-D8` continua ARBITRADA / NÃO MATERIALIZADA**;
    **`N-b-RES2` continua ABERTO**; e o **`OrquestradorMotor` continua não implementado**.
    **Esta entrega não cria marco funcional de código**: o **último commit funcional
    aprovado continua `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`** (**PR #61**), a
    **baseline permanece `1215 passed`** — medida **antes** e **depois** da edição, com
    **contagem idêntica** e **100% verde** —, a **3B.7** continua a **última subetapa
    funcional numerada** e a **3B.8 continua inexistente**. **Nada de `C-A2-N12` foi
    planejado, decidido ou executado naquela entrega.**
69. **`C-A4` está INTEGRADA à `main` pelo PR #79** — commit de conteúdo
    `2a4201f64444bc54107aca3946bc698099e34b8d`, merge
    `4836c245d8151a9fe021ec107155ea4afb19f8a6`, branch de origem
    `docs/c-a4-criterio-n12`. Método: **merge commit**, com **dois parents** —
    `2dd6536398d3c6c0ea62934c4c88b53263cc385f` e o commit de conteúdo
    `2a4201f64444bc54107aca3946bc698099e34b8d`. **Dois** arquivos —
    `docs/00-estado-atual.md` e `docs/07-arquitetura-motor-respostas.md` —, **201 adições /
    10 remoções**, sendo `docs/07` **puramente aditivo**: **144 adições / 0 remoções**, com
    **nenhuma linha histórica preexistente modificada** — **`C-3`**, **`C-6`**, **`C-8`**,
    **`C-15`**, **`C-A1-F`**, **`C-A1-ST`**, **`C-A2-RT`**, **`C-A2-N`**, **todo o bloco
    `C-A3`** e a **§12** permanecem **byte-idênticos**. **MICRO-ARBITRAGEM DOCUMENTAL, SEM
    ALTERAÇÃO DE FONTE FACTUAL, SEM ALTERAÇÃO DE CÓDIGO E SEM NOVO MARCO FUNCIONAL.**
    **ESTADO OFICIAL DA `main`.** **`C-A4` = INTEGRADA À `main`**. **`C-A2-N9`** —
    **CUMPRIDA**. **`C-A2-N10`** — **CUMPRIDA**. **`C-A2-N11`** — **CUMPRIDA — 16/16**,
    sem alvo `MD` restante. **`C-A2-N12`** — **PENDENTE**: seu **planejamento read-only já
    foi produzido e auditado**, mas a validação **ainda NÃO foi executada**; com `C-A4`
    integrada, ela passa a **dispor de critério de cumprimento e de convenções de
    validação** suficientes para sua execução **read-only**, e **nenhum veredito foi
    antecipado**. **`C` = ARBITRADA / NÃO MATERIALIZADA**;
    **`knowledge/indice-respostas-aprovadas.yaml` = INEXISTENTE**; **`R2` = NÃO
    MATERIALIZADA**; **`S2-D8` = ARBITRADA / NÃO MATERIALIZADA**; **`N-b-RES2` = ABERTO**;
    **`OrquestradorMotor` = NÃO IMPLEMENTADO**. **Nenhum marco funcional novo**: o **último
    commit funcional aprovado continua `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`**
    (**PR #61**, merge `5a722a5cc648149330362434694e7e76a40c1b57`), a **baseline permanece
    `1215 passed`**, a **3B.7** continua a **última subetapa funcional numerada** e a
    **3B.8 continua INEXISTENTE**.
    **PRÓXIMO GATE TÉCNICO.** **EXECUÇÃO READ-ONLY DE `C-A2-N12`** — validação **`C-8`** /
    **`C-15`** / **`C-A1`** —, **dependente de NOVO MANDATO DO GPT**. **`C-A2-N12` NÃO é
    executada, planejada nem decidida aqui**: **nenhum índice, *template* físico, *binding*
    físico ou `ASSERTIVA` física é criado**, **`C`, `R2` e `S2-D8` não são materializadas**,
    **`N-b-RES2` não é fechado**, o **`OrquestradorMotor` não é implementado** e a
    **subetapa 3B.8 não é criada**.
70. **`C-A2-N12` foi EXECUTADA, de forma estritamente read-only, contra
    `70abde5550be349a2a8ead1d66c106013ebf78aa`.** **Resultado**: **`C-A2-N12` = EXECUTADA
    COMPLETAMENTE / NÃO CUMPRIDA**. A validação **`C-8`** / **`C-15`** / **`C-A1`** cobriu
    **integralmente o universo aplicável** — **37 de 37** fragmentos emitíveis, enumerados
    mecanicamente a partir de `knowledge/respostas-aprovadas.md`, com **exatamente um
    resultado por par fragmento × eixo** e **vocabulário fechado** (**`C-A4-VOC`**).
    Portanto a **condição (A)** de **`C-A4-G2`** está **satisfeita**.
    **Resultado estrutural.** **36** fragmentos **sem bloqueio estrutural residual** e **1**
    **com** bloqueio: **`R22`**, no eixo **`C-8`**. **`C-15` não registrou nenhum
    `FAIL-CLOSED`**. **`NÃO DETERMINÁVEL` residual = 0** e **`DIVERGÊNCIA DE BASE`
    impeditiva = 0** — a enumeração física do corpus coincidiu com o esperado normativo. A
    **condição (B)** de **`C-A4-G2`** **não** está satisfeita, e por **`C-A4-G3`** — auditoria
    completa somada a `FAIL-CLOSED` impeditivo — o gate **não é cumprido**. Por **`C-A4-G6`**,
    `FAIL-CLOSED` é **desfecho válido** da validação, mas **não satisfaz** o gate enquanto
    impedir a representação estrutural.
    **Bloqueio de `R22`.** A redação aprovada aplica um **qualificador de aproximação** sobre
    um **fato estruturado exato**, e **`C-8` não adjudicou** essa transformação (**`C-A4-P1`**,
    **`C-A4-P2`**; **`C-A4-P3`** registra exatamente essa classe como **não excluível** de
    `C-8` por estar fora do *placeholder*). Enquanto assim permanecer, o fragmento **não
    possui representação estrutural conforme `C`**. **Este documento não reproduz o corpo da
    resposta nem valor comercial algum**, e **`R22` NÃO foi alterado**: nenhuma redação nova
    foi proposta e **nenhuma solução foi escolhida**.
    **Natureza da execução.** **Estritamente read-only**: **nenhum arquivo do repositório foi
    criado, alterado ou removido** pela auditoria — os *hashes* das fontes permaneceram
    idênticos antes e depois. **Nenhum índice, *template* físico, *binding* físico ou
    `ASSERTIVA` física foi criado**; **`knowledge/casa77.yaml` e
    `knowledge/respostas-aprovadas.md` não foram alterados**; **nenhum status foi alterado**;
    **nenhum alvo `MD` ou `FE` novo foi criado**; e **nenhum provedor de calendário foi
    escolhido**. O relatório de auditoria é **NÃO VERSIONADO**, vive **fora do repositório**,
    tem SHA-256 `bd4e3915a49ca9f768ef4a1003e322dd5b6717c85837038ecb5545219c57ebec` e é
    **evidência auxiliar — não é fonte de verdade**.
    **Estado preservado.** **`C-A2-N9`** — **CUMPRIDA**. **`C-A2-N10`** — **CUMPRIDA**.
    **`C-A2-N11`** — **CUMPRIDA — 16/16**. **`C` continua ARBITRADA / NÃO MATERIALIZADA**;
    **`knowledge/indice-respostas-aprovadas.yaml` continua INEXISTENTE**; **`R2` continua NÃO
    MATERIALIZADA**; **`S2-D8` continua ARBITRADA / NÃO MATERIALIZADA**; **`N-b-RES2`
    continua ABERTO**; e o **`OrquestradorMotor` continua não implementado**. **Esta execução
    não cria marco funcional de código**: o **último commit funcional aprovado continua
    `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`** (**PR #61**), a **baseline permanece
    `1215 passed`** — **nenhum teste foi executado por esta entrega documental** —, a
    **3B.7** continua a **última subetapa funcional numerada** e a **3B.8 continua
    INEXISTENTE**. **`C-A2-N12` não é nova arbitragem** e **não altera decisão normativa
    anterior**.
    **PRÓXIMO GATE TÉCNICO.** **PLANEJAMENTO READ-ONLY DA RESOLUÇÃO DO BLOQUEIO `R22`**, a
    ser produzido pelo **Claude Desktop** e **dependente de NOVO MANDATO DO GPT**. Esse
    planejamento deverá decidir **como remover o conflito** entre a **redação aprovada de
    `R22`**, o **fato estruturado autoritativo** e **`C-8` / `C-A4-P`**. **Nenhuma solução é
    escolhida aqui**: não se decide entre alterar a redação, alterar a modelagem, criar
    adjudicação ou qualquer outro caminho — a escolha pertence integralmente a esse
    planejamento futuro.
71. **A correção estrutural de `R22` foi APLICADA na base autoritativa, por decisão factual
    humana: o percentual coberto é APROXIMADO.** O caminho escolhido foi **alterar a
    modelagem**, não a redação. **Novo fato estruturado**:
    **`estrutura.percentual_coberto_aproximado`**, **booleano**, acrescentado em
    `knowledge/casa77.yaml` **imediatamente após `estrutura.percentual_coberto`**, que foi
    **preservado**. **Exatamente uma chave nova**: **1 inserção, 0 remoções**; nenhum outro
    valor, nenhuma reordenação; **`versao` continua `1.1`** e **`ultima_atualizacao` continua
    `2026-08-15`**. **`knowledge/respostas-aprovadas.md` permaneceu intocado**, a **redação de
    `R22` permaneceu intocada** e **`docs/07` permaneceu intocado**. **Nenhuma nova
    arbitragem** e **nenhum novo alvo `MD`** foram criados.
    **Auditoria de consumidores (`C-A1-M4`).** Executada **antes** da edição, **read-only**,
    em todo o repositório: **zero consumidores funcionais** de `estrutura.percentual_coberto`
    — a única ocorrência era a **declaração da própria fonte** — e **zero ocorrências** da
    chave nova. O carregador valida **apenas a estrutura mínima exigida** e **não rejeita
    chave adicional**; **`estrutura` sequer consta** dessa estrutura mínima.
    **Baseline.** Medida com o interpretador do ambiente **antes e depois** da alteração:
    **`1215 passed`** nos dois casos, contagem idêntica. **Nenhum teste foi criado, alterado
    ou removido**; **`src/`, `tests/` e `prompts/` não foram tocados**.
    **Diagnóstico localizado.** Verificação **estritamente read-only**, restrita a **`R22`**,
    contra **`C-8`** / **`C-15`** / **`C-A1`** / **`C-A2-RT`** / **`C-A4-DB`** / **`C-A4-P`**:
    com a aproximação existindo como **fato estruturado próprio**, o **qualificador de
    aproximação deixa de ser prosa estática transformando semanticamente um fato exato**
    (**`C-A4-P2`**, **`C-A4-P3`**) e passa a ter **referente único demonstrável**
    (**`C-A4-DB3`**, **`C-A2-RT7`**). **O bloqueio específico anteriormente registrado em
    `R22` está removido.** **Este diagnóstico NÃO é execução oficial de `C-A2-N12`**: ele é
    **localizado**, não percorre o corpus e **não substitui** a auditoria integral.
    **Estado oficial.** **`C-A2-N12` permanece EXECUTADA COMPLETAMENTE / NÃO CUMPRIDA** —
    **correção aplicada / revalidação integral pendente**. **`C-A2-N11` permanece CUMPRIDA —
    16/16.** **`C` continua ARBITRADA / NÃO MATERIALIZADA**;
    **`knowledge/indice-respostas-aprovadas.yaml` continua INEXISTENTE**; **`R2` continua NÃO
    MATERIALIZADA**; **`S2-D8` continua ARBITRADA / NÃO MATERIALIZADA**; **`N-b-RES2` continua
    ABERTO**; o **`OrquestradorMotor` continua NÃO IMPLEMENTADO**; **nenhum índice, *template*
    físico, *binding* físico ou `ASSERTIVA` física foi criado**; **nenhum provedor de
    calendário foi escolhido**. **Esta entrega não cria marco funcional de código**: o
    **último commit funcional aprovado continua `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`**
    (**PR #61**), a **3B.7** continua a **última subetapa funcional numerada** e a **3B.8
    continua INEXISTENTE**.
    **PRÓXIMO GATE TÉCNICO.** **NOVA EXECUÇÃO READ-ONLY INTEGRAL DE `C-A2-N12` — 37/37 —**,
    **dependente de NOVO MANDATO DO GPT**. Só essa execução pode alterar o estado oficial de
    **`C-A2-N12`**.
72. **A nova execução oficial de `C-A2-N12` foi REALIZADA, de forma estritamente read-only,
    contra `bd9687c69ddf7db9306363d5de4cf74072b5a134`.** **Resultado oficial**: **`C-A2-N12` =
    CUMPRIDA**. A validação **`C-8`** / **`C-15`** / **`C-A1`** cobriu **37 de 37 fragmentos
    emitíveis** em **12 eixos**, produzindo **444 de 444 resultados** — **exatamente um por par
    fragmento × eixo**, em **vocabulário fechado** (**`C-A4-VOC`**) —, com **265 `PASS`** e
    **179 `N/A`**. O corpus foi **enumerado mecanicamente e de forma independente** a partir de
    `knowledge/respostas-aprovadas.md`, e a contagem física coincidiu com o universo normativo:
    **37 fragmentos / 30 `Rxx`**.
    **Resíduos impeditivos: ZERO.** **0 `FAIL-CLOSED`**, **0 `NÃO DETERMINÁVEL`** e **0
    `DIVERGÊNCIA DE BASE`**. Nenhum *binding* necessário a fragmento emitível resolve para
    `null` ou `pendente` — **`C-7` permanece preservada**. Portanto **ambas** as condições de
    **`C-A4-G2`** estão satisfeitas: **(A)** a validação cobriu integralmente o universo
    aplicável; e **(B)** não resta bloqueio que impeça qualquer dos 37 fragmentos de possuir
    representação estrutural conforme **`C`**. **`C-A4-G3`**, **`C-A4-G4`** e **`C-A4-G5`** não
    foram acionadas.
    **Contagens por eixo.** **`C-8`** 30 / 7 `N/A`; **`C-15`** 19 / 18 `N/A`; **`C-A1-B`** 37;
    **`C-A1-ST`** 37; **`C-A1-F`** 19 / 18 `N/A`; **`C-A1-L`** 5 / 32 `N/A`; **`C-A1-R`**
    24 / 13 `N/A`; **`C-A1-S`** 6 / 31 `N/A`; **`C-A1-M`** 37; **`C-A2-B`** 17 / 20 `N/A`;
    **`C-A2-RT`** 32 / 5 `N/A`; **`C-A2-V`** 2 / 35 `N/A`.
    **`R22`.** **`C-8` = `PASS`** e **`C-15` = `PASS`**, reavaliados **do zero** contra a base
    atual, **sem herdar** o diagnóstico localizado anterior. O bloqueio estrutural registrado na
    execução anterior está **REMOVIDO** — e **não dispensado, não contornado e não relaxado**:
    a natureza aproximada deixou de ser prosa estática incidindo sobre fato exato e passou a ser
    **fato estruturado próprio e autoritativo**, com **referente único demonstrável**
    (**`C-A4-DB3`**, **`C-A2-RT7`**), de modo que **`C-A4-P2`** não é violada e a classe descrita
    em **`C-A4-P3`** deixou de se aplicar. **A redação de `R22` não foi alterada** — a solução foi
    de **modelagem**.
    **`R05` `F2`/`F3`.** Tratamento de **`C-A4-NA`** preservado: **`C-8` = `N/A`** e **`C-15` =
    `N/A`**, **sem dispensa de validação** — ambos validados por **`C-A2-RT`**, **`C-A2-V`**,
    `ASSERTIVA` conceitual, status e bijeção. **Nenhum provedor de calendário foi escolhido** e
    **nenhuma consulta real de calendário foi realizada**.
    **Natureza da execução.** **Estritamente read-only**: **nenhum arquivo do repositório foi
    criado, alterado, removido ou colocado em staging** pela auditoria — `HEAD` e os *blobs* das
    cinco fontes permaneceram idênticos antes e depois. **Nenhum índice, *template* físico,
    *binding* físico ou `ASSERTIVA` física foi criado**; os *bindings* são **exclusivamente
    conceituais** (**`C-A4-DB7`**). **Nenhum alvo `MD` foi executado**, **nenhuma `FE` foi
    aplicada**, **nenhuma arbitragem nova foi criada** e **nenhum status comercial foi alterado**.
    O relatório de auditoria é **NÃO VERSIONADO**, vive **fora do repositório**, tem SHA-256
    `3807a60e1d5c049d0b17396e46f9e22c1b8d190521e7effa6ec07e27e98a335a` e é **evidência auxiliar
    — não é fonte de verdade**.
    **Estado resultante.** **`C-A2-N9`**, **`C-A2-N10`**, **`C-A2-N11` (16/16)** e
    **`C-A2-N12`** estão **todas CUMPRIDAS**. **O veredito afirma SOMENTE que a validação foi
    integral e sem bloqueio residual**: **`C` continua ARBITRADA / NÃO MATERIALIZADA**;
    **`knowledge/indice-respostas-aprovadas.yaml` continua INEXISTENTE**; **`R2` continua NÃO
    MATERIALIZADA**; **`S2-D8` continua ARBITRADA / NÃO MATERIALIZADA**; **`N-b-RES2` continua
    ABERTO**; e o **`OrquestradorMotor` continua NÃO IMPLEMENTADO**. **Esta execução não cria
    marco funcional de código**: o **último commit funcional aprovado continua
    `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`** (**PR #61**), a **baseline permanece
    `1215 passed`** — **nenhum teste foi executado por esta entrega documental** —, a **3B.7**
    continua a **última subetapa funcional numerada** e a **3B.8 continua INEXISTENTE**.
    **PRÓXIMO GATE TÉCNICO.** **PLANEJAMENTO READ-ONLY DA MATERIALIZAÇÃO DE `C`**, a ser
    produzido pelo **Claude Desktop** e **dependente de NOVO MANDATO DO GPT**. Razão: o contrato
    **`C`** está **arbitrado** e os gates **`C-A2-N9`**, **`C-A2-N10`**, **`C-A2-N11`** e
    **`C-A2-N12`** estão **cumpridos**, mas **`C` e seu índice continuam NÃO MATERIALIZADOS**.
    **Isto NÃO autoriza a materialização**: é apenas o **próximo gate de planejamento**, e
    **nenhuma subetapa 3B.8 é criada**.
73. **A `E1` — primeira microentrega funcional de `C` — está MATERIALIZADA e INTEGRADA à
    `main` pelo PR #84** (**MERGED**) — commit funcional
    `02f1dd6621c31b90789c646bd8826e685f9ee019`, merge
    `95ed2ce4e9c54f9bdfb7b3f820e6f9e065cde24e`, branch de origem
    `feat/c-e1-response-index-validator`, base `ffeeba9bdaac5c4c600cc9b0ffd93600fc9eee2b`.
    Arquivos: **exclusivamente** `src/casa77_sdr/response_index.py` e
    `tests/test_response_index.py` — **dois arquivos NOVOS**, **1343 adições / 0 remoções**
    (**350 / 0** e **993 / 0**). **Entrega FUNCIONAL**: **passa a ser o marco funcional** da
    `main`, **sem numeração de subetapa** — a **3B.7** continua a última numerada e a **3B.8
    NÃO EXISTE**. **O que foi materializado**, exclusivamente como **validador estrutural do
    FUTURO índice**: **`IndiceInvalido`**; **`validar_indice(indice: object) -> None`**;
    **schema estrutural fechado**; **vocabulários fechados** de status, mecanismo, origem,
    formato, predicado e fato runtime; **exclusividade `YAML` × `RUNTIME_AUTORITATIVO`**;
    **`RUNTIME_AUTORITATIVO` somente com `ASSERTIVA`**; as **regras estruturais de
    `RENDERIZADO`** — *placeholder* e formato — e de **`ASSERTIVA`** — predicado;
    **fail-closed na primeira violação**, com a mensagem carregando **categoria e localizador**
    e **nunca o valor recebido**; a **rejeição de seleção numericamente posicional**; e a
    **proteção contra índices posicionais mesmo após seletores textuais encadeados**. O módulo
    é **puro**: **não abre arquivo**, **não importa carregador** e **não lê `knowledge/**`**.
    **Baseline funcional passa a `1374 passed` / Python 3.14.5** — delta **+159** sobre os
    **`1215 passed`** do PR #61, correspondente exatamente ao arquivo direcionado **novo**,
    **sem alteração de teste preexistente**. **O que NÃO foi materializado, e continua fora**:
    a **criação do índice real** — `knowledge/indice-respostas-aprovadas.yaml` **continua
    INEXISTENTE** —; **loader**; a **conversão do Markdown**; os **bindings reais**; a
    **bijeção 37/37**; **C-15**; a **renderização**; a **aplicação de formatos**; a
    **avaliação de `ASSERTIVA` contra dados reais**; **R2**; **S2-D8**; **`N-b-RES2`**; o
    **`OrquestradorMotor`**; a **escolha ou integração de calendário**; o **LLM**; e a
    **3B.8**. **`E1` MATERIALIZADA NÃO É `C` MATERIALIZADA**: `C`, como **entrega completa do
    índice estruturado**, **continua ARBITRADA / NÃO MATERIALIZADA**. Continuam inalterados:
    **`C-A2-N9`**, **`C-A2-N10`**, **`C-A2-N11` (16/16)** e **`C-A2-N12`** = **CUMPRIDAS**;
    **`R2` NÃO MATERIALIZADA**; **`S2-D8` ARBITRADA / NÃO MATERIALIZADA**; **`N-b-RES2`
    ABERTO**; **`OrquestradorMotor` NÃO IMPLEMENTADO**; **3B.8 INEXISTENTE**; e **`Q2`–`Q5`
    NÃO RESOLVIDAS por `E1`**. **O item 72 acima permanece correto como registro do momento em
    que foi escrito** — quando o marco funcional era o do PR #61 e a baseline era
    **`1215 passed`** — e é **superado, quanto ao estado corrente, por este item e pelo 74**.
74. **A presente entrega é EXCLUSIVAMENTE a reconciliação documental de
    `docs/00-estado-atual.md` após o merge do PR #84.** Base reconciliada:
    `95ed2ce4e9c54f9bdfb7b3f820e6f9e065cde24e`. Ela altera **exclusivamente este documento** e
    **não altera código, testes, `docs/02`, `docs/03`, `docs/04`, `docs/05`, `docs/06`,
    `docs/07`, `docs/08`, `knowledge/**` nem `prompts/**`**. **Diferentemente das
    reconciliações puramente documentais anteriores, esta EXECUTOU testes** — em modo de
    **verificação do estado real pós-merge**, **sem alterar arquivo algum de código ou de
    teste**: `./.venv/Scripts/python.exe -m pytest tests/test_response_index.py` →
    **`159 passed`**, e `./.venv/Scripts/python.exe -m pytest` → **`1374 passed`**, em
    **Python 3.14.5**, com **zero failures e zero errors**. Essas contagens **coincidem** com
    as registradas pela PR #84 e a coincidência foi **verificada, não presumida**. **Nada é
    materializado aqui**, **nenhuma numeração nova é criada** e a **3B.8 continua não
    existindo**. **`E2` NÃO FOI INICIADA** e **nenhuma entrega funcional seguinte é escolhida
    por esta reconciliação**: concluída a reconciliação pós-PR #84, a **próxima entrega
    funcional permanece sujeita à orquestração/auditoria posterior do GPT** — **nenhuma
    pendência é eleita aqui**, nem **`E2`**, nem o restante de **`C`**, nem **R2**, nem
    **S2-D8**, nem **`N-b-RES2`**, nem o **produtor LLM**, nem a **integração da etapa 4**, nem
    a **integração da etapa 13**, nem o **`OrquestradorMotor`**, nem qualquer outra. **Esta é a
    única reconciliação pós-PR #84**: nenhuma "reconciliação da reconciliação" será criada.
    **Aquela reconciliação foi integrada depois pelo PR #85** — commit documental
    `d97594112c509536437cd28e5de8d86d8021421c`, merge
    `bb5a58144ead6323e1b6271511a9d9e98295f440`, branch de origem
    `docs/reconciliar-estado-pos-pr84`, **exclusivamente** `docs/00-estado-atual.md`.
    **Documental**: **não alterou o marco funcional**.
75. **A SEGUNDA MICROENTREGA FUNCIONAL DE `C` — o carregador *fail-closed* do futuro índice —
    está MATERIALIZADA e INTEGRADA à `main` pelo PR #86** (**MERGED**) — commit funcional
    `b2b11e2465c7f332747a806c80b629e995f0f5a6`, merge
    `9bf68b8fece9ea66c74509490ddf6e02a0aa6f31`, branch de origem
    `feat/c-response-index-loader`, base `bb5a58144ead6323e1b6271511a9d9e98295f440`. Arquivos:
    **exclusivamente** `src/casa77_sdr/response_index_load.py` (**novo**, **+133 / −0**),
    `tests/test_response_index_load.py` (**novo**, **+953 / −0**) e
    `tests/test_response_index.py` (**modificado**, **+0 / −5**) — **três arquivos**,
    **1086 adições / 5 remoções**. **Entrega FUNCIONAL**: **passa a ser o marco funcional** da
    `main`, **sem numeração de subetapa** — a **3B.7** continua a última numerada e a **3B.8
    NÃO EXISTE**. **Nenhuma nomenclatura normativa `E2` foi criada.**
    **O que foi materializado**: **`IndiceIlegivel`**; **`carregar_indice(path: str | Path)`**
    como **fronteira pública única**, com **caminho sempre explícito** e **sem default** —
    **sem caminho padrão, sem descoberta automática, sem glob e sem variável de ambiente**;
    leitura **somente em UTF-8** e **estritamente somente leitura**, sem criar, escrever, mover
    ou remover arquivo; análise baseada **exclusivamente** em **`yaml.SafeLoader`**, por
    subclasse privada que **altera apenas a construção de mapeamento** e **não registra
    construtor, não amplia tag e não relaxa restrição de segurança** — tag insegura continua
    recusada pelo próprio analisador seguro; **rejeição *fail-closed* de chave YAML
    duplicada**, aplicada **por mapeamento** — chaves iguais em mapeamentos irmãos continuam
    válidas — e em **qualquer nível**; a **taxonomia fechada de ilegibilidade**
    **`arquivo_ausente`**, **`leitura_falhou`**, **`codificacao_invalida`**,
    **`sintaxe_invalida`** e **`chave_duplicada`**, com mensagem de **categoria e caminho** que
    **nunca ecoa o conteúdo do arquivo, o valor recebido ou o texto bruto do analisador** — a
    causa técnica fica **encadeada em `__cause__`**; a **separação estrita entre artefato
    ILEGÍVEL e estrutura INVÁLIDA**; a **delegação integral** de toda a forma a
    **`validar_indice(...)`**, com **`IndiceInvalido` propagando INTACTA** — sem captura,
    reembalagem, tradução de categoria ou duplicação de regra —, de modo que raiz `None`,
    lista ou escalar **chega ao validador** e é rejeitada pela regra já existente de **E1**; e
    **zero normalização, zero valor padrão e zero *fallback*** depois da análise, devolvendo a
    estrutura tal como o analisador a produziu. O módulo **não abre fonte comercial paralela**:
    seus únicos *imports* são `pathlib`, `typing`, `yaml` e `casa77_sdr.response_index`.
    **Correção de teste legado incluída na mesma entrega**: o teste
    **`test_indice_real_continua_inexistente`** foi **removido** de
    `tests/test_response_index.py`. Motivo: a inexistência do índice era **evidência temporária
    de escopo da `E1`**, não **invariante permanente** — mantê-lo bloquearia a própria
    materialização futura de `C`. **A remoção NÃO criou o índice**, que **continua
    INEXISTENTE**, verificado por comando nesta reconciliação. Nenhum outro teste daquele
    arquivo foi alterado, e **`src/casa77_sdr/response_index.py` permaneceu inalterado**.
    **Baseline funcional passa a `1436 passed` / Python 3.14.5** — delta **+62** sobre os
    **`1374 passed`** do PR #84, decomposto em **+63** do arquivo direcionado novo e **−1** da
    remoção acima.
    **O que NÃO foi materializado, e continua fora**: a **criação do índice real** —
    `knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE** —; a **conversão do
    Markdown**; *templates* e *bindings* físicos; a **bijeção 37/37**; **C-15**; a
    **renderização**; a **aplicação de formatos**; a **avaliação de `ASSERTIVA` contra dados
    reais**; **R2**; **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**; a **escolha ou
    integração de calendário**; o **LLM**; e a **3B.8**. **CARREGAR NÃO É MATERIALIZAR `C`**:
    `C`, como **entrega completa do índice estruturado**, **continua ARBITRADA / NÃO
    MATERIALIZADA**. Continuam inalterados: **`C-A2-N9`**, **`C-A2-N10`**, **`C-A2-N11`
    (16/16)** e **`C-A2-N12`** = **CUMPRIDAS**; **`R2` NÃO MATERIALIZADA**; **`S2-D8` ARBITRADA
    / NÃO MATERIALIZADA**; **`N-b-RES2` ABERTO**; **`OrquestradorMotor` NÃO IMPLEMENTADO**;
    **3B.8 INEXISTENTE**; e **`Q2`–`Q5` NÃO RESOLVIDAS**. **Os itens 73 e 74 acima permanecem
    corretos como registro do momento em que foram escritos** — quando o marco funcional era o
    do PR #84 e a baseline era **`1374 passed`** — e são **superados, quanto ao estado
    corrente, por este item e pelo 76**.
76. **A presente entrega é EXCLUSIVAMENTE a reconciliação documental de
    `docs/00-estado-atual.md` após o merge do PR #86.** Base reconciliada:
    `9bf68b8fece9ea66c74509490ddf6e02a0aa6f31`. Ela altera **exclusivamente este documento** e
    **não altera código, testes, `docs/02`, `docs/03`, `docs/04`, `docs/05`, `docs/06`,
    `docs/07`, `docs/08`, `knowledge/**` nem `prompts/**`**. Como a reconciliação anterior,
    esta **EXECUTOU testes** — em modo de **verificação do estado real pós-merge**, **sem
    alterar arquivo algum de código ou de teste**:
    `./.venv/Scripts/python.exe -m pytest tests/test_response_index.py` → **`158 passed`**;
    `./.venv/Scripts/python.exe -m pytest tests/test_response_index_load.py` →
    **`63 passed`**; e `./.venv/Scripts/python.exe -m pytest` → **`1436 passed`**, em
    **Python 3.14.5**, com **zero failures e zero errors**. Essas contagens **coincidem** com
    as registradas pela PR #86 e a coincidência foi **verificada, não presumida**. **Nada é
    materializado aqui**, **nenhuma numeração nova é criada** e a **3B.8 continua não
    existindo**. **A PRÓXIMA MICROENTREGA FUNCIONAL DE `C` NÃO FOI ESCOLHIDA NEM INICIADA**:
    sua definição **depende de nova orquestração/auditoria do GPT**. Em particular, **não se
    afirma aqui que o próximo passo seja criar o índice** — nem essa nem qualquer outra
    pendência é eleita: nem o restante de **`C`**, nem **R2**, nem **S2-D8**, nem
    **`N-b-RES2`**, nem o **produtor LLM**, nem a **integração da etapa 4**, nem a **integração
    da etapa 13**, nem o **`OrquestradorMotor`**. **Esta é a única reconciliação pós-PR #86**:
    nenhuma "reconciliação da reconciliação" será criada. **Aquela reconciliação foi integrada
    depois pelo PR #87** — commit documental `fa1d91e12b58d1ed658c70bbeb8894dd8c6793ca`, merge
    `9cd6d4b029f6495dfb8b95db917c958da0fd9b2f`, branch de origem
    `docs/reconciliar-estado-pos-pr86`, **exclusivamente** `docs/00-estado-atual.md`,
    **213 adições / 57 remoções**. **Documental**: **não alterou o marco funcional**.
77. **A presente entrega é a MICRO-ARBITRAGEM DOCUMENTAL DA REPRESENTAÇÃO CANÔNICA DE
    `C-15b`.** Base: `9cd6d4b029f6495dfb8b95db917c958da0fd9b2f`. Ela é **exclusivamente
    documental**, **posterior** a **C**, **C-A1**, **C-A2**, **C-A3** e **C-A4**, e vive em
    `docs/07-arquitetura-motor-respostas.md`, no bloco **"Representação canônica de entrada
    para `C-15b`"**, inserido **logo após `C-15e`**. **O que ela fecha** é **a REPRESENTAÇÃO DE
    ENTRADA** sobre a qual a equivalência textual de `C-15` será futuramente julgada — a
    decisão adotada é **texto canônico já extraído**: **(D1)** a unidade de entrada são **duas
    `str` em representação canônica** — o **fragmento aprovado já extraído** e a **renderização
    textual do mesmo fragmento** —, **sem DTO ou estrutura pública nova**, mantendo o
    **fragmento inteiro** como unidade (`C-15c`, `C-A4-P1`); **(D2)** a separação entre
    estrutura Markdown e conteúdo textual pertence **integralmente a uma futura fronteira de
    extração**, que **ainda não existe**, de modo que a representação **chega pronta** e o
    comparador **não** analisa Markdown, **não** identifica *blockquote*, *heading*, lista,
    *code fence* ou indentação, **não** remove prefixo `>` e **não** extrai fragmento;
    **(D3)** um **`LF` isolado**, não adjacente a outro `LF`, é **quebra suave** por
    **convenção da representação** — e **não** por inferência de Markdown — e é convertido em
    **exatamente um `U+0020`**, **sem colapsar** nenhum outro espaço; **(D4)** **exatamente
    dois `LF`** são **fronteira canônica de parágrafo real** e são **preservados
    literalmente**, enquanto **três ou mais `LF` consecutivos** são **NÃO CANÔNICOS** e devem
    ser **recusados**, nunca reinterpretados; **(D5)** a representação admite **somente `LF`
    (`U+000A`)** como terminador, sendo **NÃO CANÔNICOS** `CR`, `CRLF`, `U+2028`, `U+2029`,
    `U+0085`, `U+000B` e `U+000C` — o comparador **recusa** e **não converte `CRLF` para
    `LF`**; **(D6)** ficam fixados **três desfechos conceitualmente distintos** — **NÃO
    DETERMINÁVEL** para violação mecanicamente detectável, que **não é `False`** e exige que o
    chamador **pare ou escale**; **NÃO EQUIVALENTE** (`False`) quando ambos pertencem ao
    domínio canônico e as normalizações diferem, acionando **`C-15d`**; e **EQUIVALENTE**
    (`True`) quando as normalizações são exatamente iguais, satisfazendo **`C-15a(2)`**; e
    **(D7)** a lista de **violações mecanicamente detectáveis** — terminador proibido, `LF` na
    borda inicial, `LF` na borda final, espaço ou tab imediatamente antes ou depois de `LF`, e
    três ou mais `LF` consecutivos. **Os rótulos `D1`–`D7` são locais daquele bloco e NÃO são
    identificadores normativos novos de `C`.**
    **RESSALVA NORMATIVA OBRIGATÓRIA**: a equivalência definida por **`C-15b`** **somente
    possui garantia semântica** quando **ambos os insumos satisfazem a representação canônica**
    e quando o **fragmento aprovado foi corretamente separado da estrutura Markdown pelo
    produtor responsável**. A ausência de estrutura Markdown é **parcialmente pré-condição do
    chamador** e **não pode ser integralmente verificada pelo comparador** sem torná-lo
    *parser* Markdown. Portanto **fora do domínio canônico não existe garantia de correção do
    veredito**, e produtores e consumidores **devem** satisfazer essa pré-condição antes de
    usar o resultado para **`C-15d`** ou para a **migração de autoridade de status**
    (`C-A1-ST6`–`C-A1-ST10`). **Nada é afirmado sobre impossibilidade de falso `True`**: isso
    não é demonstrável para toda `str` e **não foi registrado**.
    **Nomes ainda NÃO decididos**: módulo, função, assinatura, ordem de parâmetros, taxonomia
    de exceção, mensagem de erro, comportamento para tipo não-`str` e ordem entre **NFC** e a
    dobra de quebra suave — tudo pertence ao **mandato técnico posterior**.
    **Evidência estrutural do corpus**, somente metadados, **sem reproduzir frase** e **sem
    registrar *hash* de conteúdo**: **37** fragmentos emitíveis, **29** multilinha, **0**
    parágrafos internos, **0** estruturas de lista/*heading*/bloco de código dentro dos
    fragmentos, **0** *hard breaks* explícitos, **0** ocorrências de `CR`/`CRLF` e **37/37
    compatíveis** com a representação canônica. As contagens de fragmento e parágrafo vêm da
    auditoria read-only já registrada; a ausência de `CR`/`CRLF`, terminadores exóticos,
    *hard break* e bloco de código foi **reverificada mecanicamente** sobre o blob versionado.
    **Risco operacional registrado, não resolvido**: *checkouts* e ambientes podem materializar
    terminações de linha distintas das do blob Git. **`.gitattributes` NÃO foi alterado**,
    **nenhuma configuração de Git foi decidida** e **nada foi afirmado como universal ou
    garantido**.
    **`C-15a`–`C-15e` permanecem registro normativo intacto**: **não renumerados, não
    reescritos**. **Esta arbitragem NÃO cria marco funcional**: **não implementa o comparador**,
    **não cria módulo, teste, extrator, *renderer*, formato ou índice**, **não faz *parsing*
    Markdown**, **não executa I/O**, **não resolve *binding***, **não decide candidatura de
    fragmento**, **não decide migração de status**, **não materializa `C`, `R2` nem `S2-D8`**,
    **não fecha `N-b-RES2`**, **não implementa o `OrquestradorMotor`** e **não escolhe
    calendário**. **COMPARAR NÃO É MATERIALIZAR `C`.** O **último marco funcional continua o
    PR #86** — commit `b2b11e2465c7f332747a806c80b629e995f0f5a6`, merge
    `9bf68b8fece9ea66c74509490ddf6e02a0aa6f31` —, a **baseline permanece `1436 passed`** /
    Python 3.14.5, **reexecutada e confirmada antes e depois da edição desta entrega**, a
    **3B.7** continua a **última subetapa funcional numerada** e a **3B.8 NÃO EXISTE**.
    **Nenhuma nomenclatura `E2` foi criada.** A **candidata seguinte continua sendo a futura
    terceira microentrega funcional de `C` — a equivalência textual —, que NÃO é materializada
    aqui**; com esta arbitragem ela passa a ter **contrato de entrada fechado**. A **próxima
    etapa**, caso esta arbitragem seja integrada, é o **planejamento/mandato técnico da
    equivalência textual**, **sujeito a nova auditoria do GPT** — e **nenhuma implementação é
    autorizada por este documento**. **Aquela arbitragem foi integrada depois pelo PR #88** —
    commit documental `2eacac1a1fb00a588a93645ac043eaa1f149cc61`, merge
    `a2920e1e8208be7b4b54d31d663440a9c65fbc6c`, branch de origem
    `docs/arbitrar-c15b-representacao-canonica`, **exclusivamente** `docs/00-estado-atual.md`
    e `docs/07-arquitetura-motor-respostas.md`, **170 adições / 2 remoções**. **Documental**:
    **não alterou o marco funcional** e **não implementou o comparador**.
78. **A TERCEIRA MICROENTREGA FUNCIONAL DE `C` — o comparador determinístico de equivalência
    textual de `C-15b` — está MATERIALIZADA e INTEGRADA à `main` pelo PR #89** (**MERGED**) —
    commit funcional `23e3fa727eb1457cd98a0e0e6f36580dade2ab00`, merge
    `76531de7d3f4257d84b5a1f9498d8666c4e60030`, branch de origem
    `feat/c-response-equivalence`, título `feat: add response text equivalence`, base
    `a2920e1e8208be7b4b54d31d663440a9c65fbc6c`. Arquivos: **exclusivamente**
    `src/casa77_sdr/response_equivalence.py` (**novo**, **+172 / −0**) e
    `tests/test_response_equivalence.py` (**novo**, **+793 / −0**) — **dois arquivos**,
    **965 adições / 0 remoções**, **nenhum arquivo preexistente alterado**. **Entrega
    FUNCIONAL**: **passa a ser o marco funcional** da `main`, **sem numeração de subetapa** —
    a **3B.7** continua a última numerada e a **3B.8 NÃO EXISTE**. **Nenhuma nomenclatura
    normativa `E2` ou `E3` foi criada.**
    **API pública local**: **`EquivalenciaNaoDeterminavel`** e
    **`sao_textualmente_equivalentes(aprovado: str, renderizado: str) -> bool`**. O módulo
    **não é exportado** por `casa77_sdr/__init__.py`.
    **O que foi materializado**: o julgamento opera sobre **duas `str` já em representação
    canônica** (D1), mantendo o **fragmento inteiro** como unidade (`C-15c`, `C-A4-P1`). Tipo
    não-`str` produz **`TypeError`** — erro de contrato de chamada —, verificado **antes** da
    canonicidade. Violação mecanicamente detectável produz **`EquivalenciaNaoDeterminavel`**,
    que **NÃO É `False`** (D6-A): o chamador **deve parar ou escalar**. A validação percorre
    **`aprovado` antes de `renderizado`**, **encerra na primeira violação** e **não acumula**.
    A normalização é **NFC antes da dobra**; o **`LF` isolado vira exatamente um `U+0020`**
    (D3); **`\n\n` é preservado literalmente** (D4); **três ou mais `LF` são recusados**;
    **`CR`, `CRLF`, `U+2028`, `U+2029`, `U+0085`, `U+000B` e `U+000C` são recusados**, **sem
    converter `CRLF`** (D5); **`LF` de borda** e **branco adjacente a `LF`** são recusados
    (D7); e a comparação final é **igualdade exata**, **sem `strip`, sem `casefold`, sem
    *fuzzy* e sem transformação semântica**. A **`str` vazia permanece canônica**.
    **Categorias técnicas** privadas e fechadas — `terminador_proibido`, `quebra_na_borda`,
    `sequencia_de_quebras_excessiva`, `branco_adjacente_a_quebra` —, **que NÃO são
    identificadores normativos de `C`**. A mensagem carrega **categoria e lado**, com
    localizador `inicio`/`fim`/`antes`/`depois` quando aplicável, e **nunca** o texto
    recebido, o caractere ofensor, deslocamento, índice ou comprimento; **sem `__cause__`**.
    **Pureza e fronteiras**: o módulo importa **somente** `unicodedata`, além de
    `__future__` — **zero I/O**, **zero *filesystem***, **zero YAML**, **zero leitura de
    `knowledge/**`**, **zero analisador de Markdown**, **zero dependência de
    `response_index`** e **zero dependência de `response_index_load`**.
    **Baseline funcional passa a `1589 passed` / Python 3.14.5** — delta **+153** sobre os
    **`1436 passed`** do PR #86, correspondente exatamente ao arquivo direcionado **novo**.
    A PR auditou **quatro** execuções: **`153`** e **`1589`**, ambas também sob `-W error`,
    com **zero failures e zero errors**.
    **O que NÃO foi materializado, e continua fora**: a **criação do índice real** —
    `knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE** —; **analisador ou
    extrator de Markdown**, que **continua inexistente**; ***templates* físicos**, que
    **continuam inexistentes**; ***bindings* físicos**, que **continuam inexistentes**;
    ***renderer***, que **continua inexistente**; a **materialização dos formatos**; a
    **integração de consumidor do comparador**, que **não ocorreu**; a **bijeção física
    37/37**; a **migração de autoridade de status**, **não executada**; **R2**; **S2-D8**;
    **`N-b-RES2`**; o **`OrquestradorMotor`**; **calendário**; **LLM**; e a **3B.8**.
    **COMPARAR NÃO É MATERIALIZAR `C`**: `C`, como **entrega completa do índice estruturado**,
    **continua ARBITRADA / NÃO MATERIALIZADA**. Continuam inalterados: **`C-A2-N9`**,
    **`C-A2-N10`**, **`C-A2-N11` (16/16)** e **`C-A2-N12`** = **CUMPRIDAS**; **`R2` NÃO
    MATERIALIZADA**; **`S2-D8` ARBITRADA / NÃO MATERIALIZADA**; **`N-b-RES2` ABERTO**;
    **`OrquestradorMotor` NÃO IMPLEMENTADO**; **3B.8 INEXISTENTE**; e **`Q2`–`Q5` NÃO
    RESOLVIDAS**. **O item 77 acima permanece correto como registro do momento em que foi
    escrito** — quando o comparador ainda não existia e a baseline era **`1436 passed`** — e é
    **superado, quanto ao estado corrente, por este item e pelo 79**.
79. **A presente entrega é EXCLUSIVAMENTE a reconciliação documental de
    `docs/00-estado-atual.md` após o merge do PR #89.** Base reconciliada:
    `76531de7d3f4257d84b5a1f9498d8666c4e60030`. Ela altera **exclusivamente este documento** e
    **não altera código, testes, `docs/02`, `docs/03`, `docs/04`, `docs/05`, `docs/06`,
    `docs/07`, `docs/08`, `knowledge/**` nem `prompts/**`**. Como as reconciliações anteriores,
    esta **EXECUTOU a suíte** — em modo de **verificação do estado real pós-merge**, **sem
    alterar arquivo algum de código ou de teste**: `./.venv/Scripts/python.exe -m pytest` →
    **`1589 passed`**, em **Python 3.14.5**, com **zero failures e zero errors**, medido
    **antes e depois** da edição, com **contagem idêntica**. Essa contagem **coincide** com a
    registrada pela PR #89 e a coincidência foi **verificada, não presumida**. **Nada é
    materializado aqui**, **nenhuma numeração nova é criada** e a **3B.8 continua não
    existindo**. **A QUARTA MICROENTREGA FUNCIONAL DE `C` NÃO FOI ESCOLHIDA NEM INICIADA**:
    sua definição **depende de nova orquestração/auditoria do GPT**. Em particular, **não se
    assume aqui** que a próxima seja o **índice real**, o ***renderer***, os **formatos** ou o
    **extrator** — **nenhuma pendência é eleita**, nem o restante de **`C`**, nem **R2**, nem
    **S2-D8**, nem **`N-b-RES2`**, nem o **produtor LLM**, nem a **integração da etapa 4**, nem
    a **integração da etapa 13**, nem o **`OrquestradorMotor`**. **Nenhuma etapa funcional
    seguinte está iniciada.** **Esta é a única reconciliação pós-PR #89**: nenhuma
    "reconciliação da reconciliação" será criada. **Aquela reconciliação foi integrada depois
    pelo PR #90** — commit documental `98134a24452d67d8e17fae69828f32431e2b6c22`, merge
    `4df6b58e196ba649bc35fdedab82b084592a0379`, branch de origem
    `docs/reconciliar-estado-pos-pr89`, **exclusivamente** `docs/00-estado-atual.md`,
    **191 adições / 61 remoções**. **Documental**: **não alterou o marco funcional**. **O
    item 79 permanece correto como registro do momento em que foi escrito** — quando os
    formatadores ainda não existiam e a baseline era **`1589 passed`** — e é **superado,
    quanto ao estado corrente, pelos itens 80 e 81**.
80. **A QUARTA MICROENTREGA FUNCIONAL DE `C` — os formatadores determinísticos de
    apresentação pura de `C-6` — está MATERIALIZADA e INTEGRADA à `main` pelo PR #91**
    (**MERGED**) — commit funcional `7d8dd8617eb5cd8c346e67496c3631feafe97f4f`, merge
    `d15201b0a84bca332b09e0d5e623736605663962`, branch de origem
    `feat/c-response-formatters`, título `feat: add deterministic response formatters`, base
    `4df6b58e196ba649bc35fdedab82b084592a0379`, integrada em **2026-09-01T14:03:24Z**.
    Arquivos: **exclusivamente** `src/casa77_sdr/response_format.py` (**novo**, **+197 /
    −0**) e `tests/test_response_format.py` (**novo**, **+1170 / −0**) — **dois arquivos**,
    **1367 adições / 0 remoções**, **nenhum arquivo preexistente alterado**. **Entrega
    FUNCIONAL**: **passa a ser o marco funcional** da `main`, **sem numeração de subetapa** —
    a **3B.7** continua a última numerada e a **3B.8 NÃO EXISTE**. **Nenhuma nomenclatura
    normativa `E2`, `E3` ou `E4` foi criada.**
    **API pública local**: **`FormatoInaplicavel`**, **`formatar_inteiro`**,
    **`formatar_inteiro_agrupado`**, **`formatar_simbolo_moeda`**, **`formatar_texto`** e
    **`formatar_lista`** — **`__all__` com exatamente seis nomes**, **um parâmetro por
    função**, **sem default** e **sem parâmetro de estilo, padrão, *locale* ou variante**. O
    módulo **não é exportado** por `casa77_sdr/__init__.py`.
    **O que foi materializado**, por formato. **`inteiro`** (**C-6a**): representação decimal
    do **mesmo** inteiro, aceitando **somente `int` estrito** — **`bool` é recusado**, apesar
    de ser subclasse de `int` —, **sem coerção** de `float`, `Decimal`, texto numérico ou
    `None`, **sem agrupar**, **sem arredondar**, **sem calcular**, **sem zero acrescentado**,
    com o **sinal preservado**. **`inteiro_agrupado`** (**C-6b**, **`C-A1-F1`**,
    **`C-A4-F1`**): o **mesmo** inteiro, agrupado **da direita para a esquerda** em grupos de
    **três dígitos** unidos por **`.`**, **sem casas decimais**, **sem arredondamento**,
    **sem cálculo**, **sem alteração do valor**, **sem zero para completar grupo**, com o
    **sinal preservado e não agrupado**, **sem *locale*** e **sem biblioteca cujo resultado
    dependa do ambiente** — o agrupamento é montado **dígito a dígito**, e **não** delegado à
    formatação de milhar da linguagem. **`simbolo_moeda`** (**C-6c**, **`C-A1-F2`**,
    **`C-A4-F2`**): **tabela fechada** de **um único código suportado**, **não ampliada**,
    devolvendo **somente o símbolo**, **sem whitespace antes ou depois** — o espaço pertence
    ao fragmento estático (**`C-A4-F2c`**) —, **sem `upper`**, **sem `strip`** e **sem
    tolerância de caixa**; **código não suportado FALHA** (**`C-A4-F2e`**), a **moeda nunca é
    inferida** e **nenhum campo adicional é lido** (**`C-A4-F2f`**). **`texto`** (**C-6e**):
    **identidade exata**, devolvendo **a mesma `str`** recebida — **sem NFC**, **sem
    `strip`**, **sem `casefold`**, **sem colapso de espaço**, **sem dobra de quebra** e **sem
    ajuste de pontuação**; a **`str` vazia continua vazia**. **`lista`** (**C-6f**,
    **`C-A1-L`**): **zero itens FALHA** (**`C-A1-L1`**); **um item** devolve o próprio item;
    **dois** são unidos por ` e `; **três ou mais** separam os anteriores por `, ` e o último
    por ` e ` (**`C-A1-L2`**–**`C-A1-L4`**); **todos os itens e a ordem são preservados**
    (**`C-A1-L5`**), **cada item é texto literal** (**`C-A1-L6`**), **sem prefixo ou sufixo
    por item** (**`C-A1-L7`**) e **sem filtragem, reordenação, flexão ou paráfrase**
    (**`C-A1-L8`**); uma **`str` não é contêiner válido** — seus caracteres **não** são
    itens —, **cada item precisa ser `str`** e a **entrada não é mutada**, nem no caminho de
    falha.
    **Tratamento do item vazio**, registrado explicitamente: o contrato **não** proíbe `""`
    como item e **manda preservar literalmente**; portanto ele **não é filtrado**, **não é
    removido** e **não gera regra nova de fail-closed** — a convenção de cardinalidade e
    composição é aplicada **mecanicamente**, e **nada foi arbitrado** a respeito.
    **Contrato de erro**: **duas** categorias técnicas privadas e fechadas —
    `tipo_invalido` e `valor_invalido` —, que **NÃO são identificadores normativos de `C`**,
    e **quatro** localizadores fechados — `valor`, `codigo`, `itens` e `itens.item`. A
    **primeira violação encerra** e **nada é acumulado**; a mensagem tem a forma
    `<categoria>: <localizador>` e **nunca** ecoa o valor, o item, o código, o conteúdo
    textual, deslocamento, índice ou comprimento; **sem `__cause__`** e **sem `__context__`**.
    Violação de **tipo** também levanta **`FormatoInaplicavel`** — e **não** `TypeError` —,
    porque o formato **é inaplicável** ao que chegou; a divergência em relação ao comparador
    de `C-15b`, que usa `TypeError` para erro de contrato de chamada, é **deliberada e
    registrada**.
    **Pureza e fronteiras**: o módulo importa **apenas** `__future__` e `collections.abc` —
    **zero I/O**, **zero *filesystem***, **zero YAML**, **zero *locale***, **zero rede**,
    **zero LLM**, **zero calendário**, **zero leitura de `knowledge/**`**, **zero analisador
    de Markdown** e **zero dependência de `casa77_sdr.*`**, incluindo `response_index`,
    `response_index_load` e `response_equivalence`. Ele **não conhece o consumidor**: não há
    **despachante por token de formato** e **nenhuma tabela executável `token → função`**; as
    ocorrências textuais dos nomes dos formatos na **documentação e na *docstring*** do módulo
    **não constituem mecanismo de despacho**. **Nenhum preço, capacidade, horário ou condição
    comercial vive nele.**
    **O formato `hora` (C-6d) NÃO foi materializado, e a lacuna permanece ABERTA.**
    **`C-A1-F3`** fixa **dois padrões fechados** — `HH:MM` e `Hh`, este **somente** com
    minutos `00` —, mas **não existe regra arbitrada** que escolha **mecanicamente** entre
    eles a partir do valor. Escolher seria **arbitrar**, e arbitrar **não é formatar**: o
    formato ficou **expressamente fora** desta entrega, que **não criou** `formatar_hora`,
    helper de hora, token novo, parâmetro de estilo nem inferência baseada em minutos —
    provado por teste. **Esta reconciliação NÃO arbitra essa lacuna.**
    **Baseline funcional passa a `1908 passed` / Python 3.14.5** — delta **+319** sobre os
    **`1589 passed`** do PR #89, correspondente exatamente ao arquivo direcionado **novo**.
    A PR auditou **quatro** execuções: **`319`** e **`1908`**, ambas também sob `-W error`,
    com **zero failures, zero errors** e **zero warnings** nas variantes estritas.
    **O que NÃO foi materializado, e continua fora**: o formato **`hora`**; a **criação do
    índice real** — `knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE** —;
    **analisador ou extrator de Markdown**, que **continua inexistente**; **sintaxe física de
    *placeholder***; ***templates* físicos**, que **continuam inexistentes**; ***bindings*
    físicos**, que **continuam inexistentes**; a **resolução de `caminho_yaml`**;
    ***renderer***, que **continua inexistente**; a **avaliação de `ASSERTIVA`**; a **bijeção
    física 37/37**; a **integração de consumidor**, que **não ocorreu** — **nenhum chamador
    real existe**; a **migração de autoridade de status**, **não executada**; **R2**;
    **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**; **calendário**; **LLM**; e a
    **3B.8**. **FORMATAR NÃO É MATERIALIZAR `C`**: `C`, como **entrega completa do índice
    estruturado**, **continua ARBITRADA / NÃO MATERIALIZADA**. Continuam inalterados:
    **`C-A2-N9`**, **`C-A2-N10`**, **`C-A2-N11` (16/16)** e **`C-A2-N12`** = **CUMPRIDAS**;
    **`R2` NÃO MATERIALIZADA**; **`S2-D8` ARBITRADA / NÃO MATERIALIZADA**; **`N-b-RES2`
    ABERTO**; **`OrquestradorMotor` NÃO IMPLEMENTADO**; **3B.8 INEXISTENTE**; e **`Q2`–`Q5`
    NÃO RESOLVIDAS**. **Os itens 78 e 79 acima permanecem corretos como registro do momento
    em que foram escritos** — quando os formatadores ainda não existiam, a baseline era
    **`1589 passed`** e a **aplicação dos formatos** figurava, com razão, entre o que a
    entrega de então **não** incluía — e são **superados, quanto ao estado corrente, por este
    item e pelo 81**.
81. **A presente entrega é EXCLUSIVAMENTE a reconciliação documental de
    `docs/00-estado-atual.md` após o merge do PR #91.** Base reconciliada:
    `d15201b0a84bca332b09e0d5e623736605663962`. Ela altera **exclusivamente este documento** e
    **não altera código, testes, `docs/02`, `docs/03`, `docs/04`, `docs/05`, `docs/06`,
    `docs/07`, `docs/08`, `knowledge/**` nem `prompts/**`**. **Diferentemente das
    reconciliações pós-PR #84, #86 e #89, esta NÃO executou a suíte**: a PR #91 já havia
    auditado as **quatro** execuções — **`319`**, **`319`** sob `-W error`, **`1908`** e
    **`1908`** sob `-W error` — sobre a **árvore de trabalho auditada**, cuja **invariância
    durante o reteste foi provada por SHA-256 antes e depois**, com o mesmo valor nas duas
    medições. No **staging**, o Git aplicou a normalização **`CRLF → LF`** ao índice, e
    verificou-se **mecanicamente** que o **conteúdo staged era idêntico ao da árvore de
    trabalho depois dessa normalização**; o **staged foi auditado** — blobs `95f432a6…` e
    `74385927…`, `A/A`, `197 / 0` e `1170 / 0` — e os **blobs integrados à `main` são
    exatamente esses blobs staged auditados**, conferidos em `origin/main` e no commit
    funcional. **Nenhuma contagem é presumida além dessas**, e **nenhuma execução nova é
    alegada**.
    **Nada é materializado aqui**, **nenhuma numeração nova é criada**, **nenhuma lacuna
    normativa é arbitrada** — em particular a de **`hora`** — e a **3B.8 continua não
    existindo**. **A QUINTA MICROENTREGA FUNCIONAL DE `C` NÃO FOI ESCOLHIDA NEM INICIADA**:
    sua definição **depende de nova orquestração/auditoria do GPT**. Em particular, **não se
    assume aqui** que a próxima seja o formato **`hora`**, o **índice real**, o **extrator**,
    o ***renderer***, os ***templates*** ou a **integração de consumidor** — **nenhuma
    pendência é eleita**, nem o restante de **`C`**, nem **R2**, nem **S2-D8**, nem
    **`N-b-RES2`**, nem o **produtor LLM**, nem a **integração da etapa 4**, nem a
    **integração da etapa 13**, nem o **`OrquestradorMotor`**. **Nenhuma etapa funcional
    seguinte está iniciada.** **Esta é a única reconciliação pós-PR #91**: nenhuma
    "reconciliação da reconciliação" será criada. **Aquela reconciliação foi integrada depois
    pelo PR #92** — commit documental `a4d908d8d6bf77aac96565c9883a39d578920089`, merge
    `c4df73cf60d5ec79549aa9015fc3c9820431936a`, branch de origem
    `docs/reconciliar-estado-pos-pr91`, **exclusivamente** `docs/00-estado-atual.md`,
    **306 adições / 58 remoções**. **Documental**: **não alterou o marco funcional**. **O
    item 81 permanece correto como registro do momento em que foi escrito** — quando o
    avaliador de `ASSERTIVA` ainda não existia e a baseline era **`1908 passed`** — e é
    **superado, quanto ao estado corrente, pelos itens 82 e 83**.
82. **A QUINTA MICROENTREGA FUNCIONAL DE `C` — o avaliador determinístico booleano de
    `ASSERTIVA` sobre valor já resolvido — está MATERIALIZADA e INTEGRADA à `main` pelo
    PR #93** (**MERGED**) — commit funcional `efa903816b5dc1dafbce8161f6424abdf41f2ca6`,
    merge `353e1b42d6c8b31d649f59b151184811ef51462e`, branch de origem
    `feat/c-response-assertion`, título `feat: add deterministic assertion evaluator`, base
    `c4df73cf60d5ec79549aa9015fc3c9820431936a`, integrada em **2026-09-01T18:00:57Z**.
    Arquivos: **exclusivamente** `src/casa77_sdr/response_assertion.py` (**novo**, **+105 /
    −0**) e `tests/test_response_assertion.py` (**novo**, **+843 / −0**) — **dois
    arquivos**, **948 adições / 0 remoções**, **nenhum arquivo preexistente alterado**. Os
    **blobs integrados** são exatamente os **blobs staged auditados**: `dd6e6f6b…` para o
    módulo e `e4b2a7a4…` para o teste. **Entrega FUNCIONAL**: **passa a ser o marco
    funcional** da `main`, **sem numeração de subetapa** — a **3B.7** continua a última
    numerada e a **3B.8 NÃO EXISTE**. **Nenhuma nomenclatura normativa `E2`, `E3`, `E4` ou
    `E5` foi criada.**
    **API pública local**: **`AssertivaNaoAvaliavel`** e
    **`avaliar_assertiva(predicado: str, valor: object) -> bool`** — **`__all__` com
    exatamente dois nomes**, **dois parâmetros**, **sem default** e **sem parâmetro de modo,
    estilo, origem, caminho ou configuração**. A exceção deriva **diretamente de
    `Exception`**. O módulo **não é exportado** por `casa77_sdr/__init__.py`.
    **Predicados suportados**: o vocabulário **fechado** de C-5 — **`EH_VERDADEIRO`** e
    **`EH_FALSO`** —, **sem nenhum terceiro** (**C-5g**, **C-5h**, **C-A1-R**). Predicado
    não-`str` → `tipo_invalido: predicado`; predicado `str` fora do vocabulário →
    `valor_invalido: predicado`. O predicado é consultado **como chegou**: **sem `upper`**,
    **sem `strip`** e **sem tolerância de caixa** (**C-A1-R4**).
    **Domínio materializado — deliberadamente estreito.** A fronteira avalia **apenas o
    domínio booleano estrito** de um valor **já resolvido pelo chamador**. A **matriz
    avaliável é exaustiva e tem quatro casos**: `EH_VERDADEIRO` + `True` → `True`;
    `EH_VERDADEIRO` + `False` → `False`; `EH_FALSO` + `False` → `True`; `EH_FALSO` + `True`
    → `False`. **Qualquer valor fora de `bool` estrito é NÃO AVALIÁVEL** e levanta
    `AssertivaNaoAvaliavel`: **`0` não é `False`**, **`1` não é `True`**, e o valor **nunca é
    convertido em assertiva falsa** — NÃO AVALIÁVEL **não** se confunde com assertiva válida
    que resultou `False`. **Não há *truthiness*, `bool(...)`, coerção, comparação com `1` ou
    `0`, leitura de `"true"`/`"false"`, análise, normalização ou *fallback***; `__bool__` e
    `__eq__` customizados **não** são consultados, porque a decisão é **por tipo**, nunca por
    igualdade permissiva.
    **Limitação normativa, registrada expressamente.** Esta entrega **NÃO declara que todo
    domínio futuro de `ASSERTIVA` seja necessariamente booleano**. Ela materializa **somente
    a avaliação hoje segura**; **nenhum domínio adicional é inferido ou arbitrado**, e
    **ampliar a avaliação para outro domínio exigiria contrato posterior explícito**. A
    **recusa geral de valores não booleanos nesta fronteira é delimitação técnica fail-closed
    desta microentrega** — e **não** expansão normativa de **`C-7`**, que trata
    **especificamente** das regras de `null` e `pendente`.
    **Precedência e contrato de erro**: a validação segue a ordem fixa **tipo do predicado →
    valor do predicado → domínio do valor → avaliação**; a **primeira violação encerra** e
    **nada é acumulado** (**P5**). **Duas** categorias técnicas privadas e fechadas —
    `tipo_invalido` e `valor_invalido` — e **dois** localizadores fechados — `predicado` e
    `valor` —, nenhum deles identificador normativo de `C`. A mensagem tem a forma
    `<categoria>: <localizador>` e **nunca** ecoa o predicado, o valor, o **tipo concreto**,
    `repr`, conteúdo, índice, tamanho ou deslocamento; **sem `__cause__`** e **sem
    `__context__`**.
    **Pureza e fronteiras**: o módulo importa **apenas** `__future__` — **zero I/O**, **zero
    *filesystem***, **zero YAML**, **zero *locale***, **zero rede**, **zero LLM**, **zero
    calendário**, **zero relógio**, **zero variável de ambiente**, **zero leitura de
    `knowledge/**`** e **zero dependência de `casa77_sdr.*`**. Ele **não** resolve referente,
    **não** lê `caminho_yaml`, **não** conhece a origem do fato nem o fato de runtime, **não**
    conhece índice físico, Markdown, *template*, *placeholder* ou *renderer*, **não**
    renderiza, **não** formata, **não** compara texto, **não** seleciona resposta e **não**
    decide candidatura, disponibilidade, handoff, `E09`, `resposta_aprovada_disponivel` ou
    `pendencia_impeditiva` (**C-5i**–**C-5q**, **C-12**, **C-A2-ESC10**, **C-A2-NR7**).
    **`ASSERTIVA` permanece consistency-only.**
    **Baseline funcional passa a `2162 passed` / Python 3.14.5** — delta **+254** sobre os
    **`1908 passed`** do PR #91, correspondente exatamente ao arquivo direcionado **novo**.
    A PR auditou **quatro** execuções: **`254`** e **`2162`**, ambas também sob `-W error`,
    com **zero failures, zero errors** e **zero warnings** nas variantes estritas.
    **O que NÃO foi materializado, e continua fora**: o formato **`hora`**; a **criação do
    índice real** — `knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE** —; a
    **gramática física de `caminho_yaml`** e o **resolvedor físico de caminho**, que
    **continuam inexistentes**; a **sintaxe física de *placeholder***; ***templates*
    físicos**; ***bindings* físicos**; **analisador ou extrator de Markdown**, que **continua
    inexistente**; ***renderer***, que **continua inexistente**; a **bijeção física 37/37**,
    **não executada**; a **canonicalização e a migração física de status**, **não
    materializadas**; a **integração de consumidor**, que **não ocorreu** — **nenhum chamador
    real existe**; **R2**; **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**;
    **calendário**; **LLM**; e a **3B.8**. **AVALIAR `ASSERTIVA` NÃO É MATERIALIZAR `C`**:
    `C`, como **entrega completa do índice estruturado**, **continua ARBITRADA / NÃO
    MATERIALIZADA**. Continuam inalterados: **`C-A2-N9`**, **`C-A2-N10`**, **`C-A2-N11`
    (16/16)** e **`C-A2-N12`** = **CUMPRIDAS**; **`R2` NÃO MATERIALIZADA**; **`S2-D8`
    ARBITRADA / NÃO MATERIALIZADA**; **`N-b-RES2` ABERTO**; **`OrquestradorMotor` NÃO
    IMPLEMENTADO**; **3B.8 INEXISTENTE**; e **`Q2`–`Q5` NÃO RESOLVIDAS por esta entrega**.
    **Os itens 80 e 81 acima permanecem corretos como registro do momento em que foram
    escritos** — quando o avaliador ainda não existia, a baseline era **`1908 passed`** e a
    **avaliação de `ASSERTIVA`** figurava, com razão, entre o que a entrega de então **não**
    incluía — e são **superados, quanto ao estado corrente, por este item e pelo 83**.
83. **A presente entrega é EXCLUSIVAMENTE a reconciliação documental de
    `docs/00-estado-atual.md` após o merge do PR #93.** Base reconciliada:
    `353e1b42d6c8b31d649f59b151184811ef51462e`. Ela altera **exclusivamente este documento**
    e **não altera código, testes, `docs/02`, `docs/03`, `docs/04`, `docs/05`, `docs/06`,
    `docs/07`, `docs/08`, `knowledge/**` nem `prompts/**`**. **Esta reconciliação NÃO
    executou pytest**: registra apenas as **execuções auditadas da PR #93** — **`254`**,
    **`254`** sob `-W error`, **`2162`** e **`2162`** sob `-W error`, em **Python 3.14.5** —,
    e **nenhuma execução pós-merge é alegada**. **Nenhuma contagem é presumida além dessas.**
    **Nada é materializado aqui**, **nenhuma numeração nova é criada**, **nenhuma lacuna
    normativa é arbitrada** — em particular a de **`hora`** e a do **domínio de `ASSERTIVA`
    além do booleano** — e a **3B.8 continua não existindo**. **A SEXTA MICROENTREGA
    FUNCIONAL DE `C` NÃO FOI ESCOLHIDA NEM INICIADA**: sua definição **depende de nova
    orquestração/auditoria do GPT**. Em particular, **não se assume aqui** que a próxima seja
    o formato **`hora`**, o **índice real**, o **extrator**, o ***renderer***, os
    ***templates***, a **canonicalização de status**, a **gramática de `caminho_yaml`** ou a
    **integração de consumidor** — **nenhuma pendência é eleita**, nem o restante de **`C`**,
    nem **R2**, nem **S2-D8**, nem **`N-b-RES2`**, nem o **produtor LLM**, nem a **integração
    da etapa 4**, nem a **integração da etapa 13**, nem o **`OrquestradorMotor`**. **Nenhuma
    etapa funcional seguinte está iniciada.** **Esta é a única reconciliação pós-PR #93**:
    nenhuma "reconciliação da reconciliação" será criada. **Aquela reconciliação foi integrada
    depois pelo PR #94** — commit documental `fc354eec23ec4a109ef1ce790b322dabbffbcb0e`, merge
    `db7182f13747e64d2d79009c988bd723fba1501d`, branch de origem
    `docs/reconciliar-estado-pos-pr93`, **exclusivamente** `docs/00-estado-atual.md`,
    **285 adições / 57 remoções**. **Documental**: **não alterou o marco funcional**. **O
    item 83 permanece correto como registro do momento em que foi escrito** — quando o
    verificador da bijeção ainda não existia e a baseline era **`2162 passed`** — e é
    **superado, quanto ao estado corrente, pelos itens 84 e 85**.
84. **A SEXTA MICROENTREGA FUNCIONAL DE `C` — o verificador determinístico da
    correspondência bijetiva de `C-A1-B3` / `C-A1-B4` sobre domínios já fornecidos pelo
    chamador — está MATERIALIZADA e INTEGRADA à `main` pelo PR #95** (**MERGED**) — commit
    funcional `bdd0b2acc415ab6307c7c8da2adbad15f42cb75f`, merge
    `b06c0a43bd2f96b8712638e99c55edfe2fb2f99f`, branch de origem `feat/c-response-bijection`,
    título `feat: add deterministic response bijection validator`, base
    `db7182f13747e64d2d79009c988bd723fba1501d`, integrada em **2026-09-02T13:26:46Z**, após
    **autorização humana explícita**. Arquivos: **exclusivamente**
    `src/casa77_sdr/response_bijection.py` (**novo**, **+245 / −0**) e
    `tests/test_response_bijection.py` (**novo**, **+1227 / −0**) — **dois arquivos**, **1472
    adições / 0 remoções**, **nenhum arquivo preexistente alterado**. Os **blobs integrados**
    são exatamente os **blobs staged auditados**: `b76ed3e8…` para o módulo e `e54cce87…`
    para o teste. **Não há CI remoto configurado**: `gh pr checks 95` reportou **ausência de
    checks** — **ausência de CI, não falha**. **Entrega FUNCIONAL**: **passa a ser o marco
    funcional** da `main`, **sem numeração de subetapa** — a **3B.7** continua a última
    numerada e a **3B.8 NÃO EXISTE**. **Nenhuma nomenclatura normativa `E2`, `E3`, `E4`,
    `E5` ou `E6` foi criada.**
    **API pública local**: **`BijecaoInvalida`** e
    **`validar_bijecao(fragmentos_indice: Sequence[str], unidades_markdown: Sequence[str],
    correspondencias: Sequence[tuple[str, str]]) -> None`** — **`__all__` com exatamente
    dois nomes**, **três parâmetros**, **sem default** e **sem parâmetro de modo,
    tolerância, origem, caminho ou configuração**. A exceção deriva **diretamente de
    `Exception`**. O módulo **não é exportado** por `casa77_sdr/__init__.py`.
    **Contrato implementado.** A função **valida a relação bijetiva entre os dois domínios
    fornecidos** — devolve `None` quando a relação é **total, injetiva e sobrejetiva nos dois
    sentidos** e levanta `BijecaoInvalida` na **primeira violação**. **Fragmentos e unidades
    são tokens opacos**: `str` **não interpretadas**, sem formato `Rxx`, gramática, prefixo,
    separador, sufixo, `UUID`, número ou posição exigidos, e o conteúdo do token **nunca é
    lido**. **Token é `str` exata**: **subclasse de `str` é recusada** nos dois domínios e nos
    dois lados de cada par, porque poderia redefinir `__eq__` e `__hash__` e decidir por
    conta própria a identidade dos tokens. **Cada item da relação é `tuple` exata** de
    **exatamente dois lados** — **subclasse de `tuple` é recusada**, porque poderia
    redefinir `__len__`/`__getitem__`; `list` de dois elementos **não** é par válido; a
    relação chega como **sequência explícita de pares, nunca `Mapping`**, porque um mapa
    colapsaria silenciosamente uma origem repetida. `str`, `bytes` e `bytearray` **não** são
    contêineres válidos para nenhum dos três argumentos. **A comparação de tokens usa a
    igualdade nativa exata de `str`** — **sem `strip`, `casefold`, `lower`, `upper`, `NFC`
    ou normalização de espécie alguma**; duas representações Unicode distintas do mesmo
    texto são **tokens distintos**. **Zero normalização**, **zero coerção**, **zero
    *parsing***, **zero I/O**; **entradas não alteradas**. **Validação fail-closed** com
    **precedência determinística fixa**: tipo dos três argumentos → tipo dos tokens de
    `fragmentos_indice` → tipo dos tokens de `unidades_markdown` → tipo e, em seguida, forma
    dos itens da relação → tipo de origem e destino de cada par → duplicidade em
    `fragmentos_indice` → duplicidade em `unidades_markdown` → origem repetida → destino
    repetido → origem desconhecida → destino desconhecido → fragmento sem par → unidade sem
    par; cada etapa percorre **toda** a entrada antes da seguinte, a **primeira violação
    encerra** e **nada é acumulado** (**P5**). **Três domínios vazios constituem bijeção
    trivial válida somente sobre os domínios fornecidos.**
    **Contrato de erro**: **cinco** categorias técnicas privadas e fechadas —
    `tipo_invalido`, `estrutura_invalida`, `duplicidade`, `referencia_desconhecida` e
    `cobertura_incompleta` — e **seis** localizadores fechados — `fragmentos_indice`,
    `unidades_markdown`, `correspondencias`, `correspondencias.item`,
    `correspondencias.origem` e `correspondencias.destino` —, nenhum deles identificador
    normativo de `C`. A mensagem tem a forma `<categoria>: <localizador>` e **nunca** ecoa o
    token recebido, o conteúdo, o `repr`, o **tipo concreto**, um índice numérico, um tamanho
    ou uma cardinalidade; **sem `__cause__`** e **sem `__context__`**.
    **Pureza e fronteiras**: o módulo importa **apenas** `__future__` e
    `collections.abc.Sequence` — **zero I/O**, **zero *filesystem***, **zero YAML**, **zero
    *locale***, **zero rede**, **zero LLM**, **zero calendário**, **zero relógio**, **zero
    variável de ambiente**, **zero leitura de `knowledge/**`** e **zero dependência de
    `casa77_sdr.*`**.
    **Limite da garantia — VERIFICAR A BIJEÇÃO NÃO É MATERIALIZAR `C`.** Um retorno
    bem-sucedido significa **somente** que a relação fornecida é bijetiva sobre os domínios
    fornecidos. A função **não extrai fragmentos do índice**, **não extrai unidades
    Markdown**, **não decide o que é unidade emitível**, **não define identidade física de
    fragmento**, **não cria identificadores**, **não lê índice real**, **não prova completude
    dos dois domínios**, **não executa a bijeção física do corpus real**, **não satisfaz
    `C-A1-ST7` isoladamente**, **não migra autoridade de status** (`C-A1-ST6`–`C-A1-ST10`)
    e **não integra consumidor**. **A completude correta dos dois domínios é pré-condição
    do chamador** e **não é verificável nesta fronteira** sem transformá-la em extrator —
    que ela deliberadamente não é.
    **Baseline funcional passa a `2446 passed` / Python 3.14.5** — delta **+284** sobre os
    **`2162 passed`** do PR #93, correspondente exatamente ao arquivo direcionado **novo**.
    As **quatro** execuções — **`284`** e **`2446`**, ambas também sob `-W error`, com
    **zero failures, zero errors** e **zero warnings** nas variantes estritas — foram
    **auditadas antes do commit sobre os bytes da árvore de trabalho** e **medidas após o
    merge sobre a `main` integrada**.
    **O que NÃO foi materializado, e continua fora**: o formato **`hora`**; a **criação do
    índice real** — `knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE** —; o
    **extrator de fragmentos do índice** e o **extrator de unidades do Markdown**, que
    **continuam inexistentes**; a **identidade física de fragmento**; a **gramática física de
    `caminho_yaml`** e o **resolvedor físico de caminho**; a **sintaxe física de
    *placeholder***; ***templates* físicos**; ***bindings* físicos**; ***renderer***; a
    **bijeção física 37/37**, **não executada**; **`C-A1-ST7`**, **não satisfeita**; a
    **canonicalização e a migração física de status**, **não materializadas**; a **integração
    de consumidor**, que **não ocorreu** — **nenhum chamador real existe**; **R2**;
    **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**; **calendário**; **LLM**; e a
    **3B.8**. `C`, como **entrega completa do índice estruturado**, **continua ARBITRADA /
    NÃO MATERIALIZADA**. Continuam inalterados: **`C-A2-N9`**, **`C-A2-N10`**, **`C-A2-N11`
    (16/16)** e **`C-A2-N12`** = **CUMPRIDAS**; **`R2` NÃO MATERIALIZADA**; **`S2-D8`
    ARBITRADA / NÃO MATERIALIZADA**; **`N-b-RES2` ABERTO**; **`OrquestradorMotor` NÃO
    IMPLEMENTADO**; **3B.8 INEXISTENTE**; e **`Q2`–`Q5` NÃO RESOLVIDAS por esta entrega**.
    **Os itens 82 e 83 acima permanecem corretos como registro do momento em que foram
    escritos** — quando o verificador ainda não existia e a baseline era **`2162 passed`** —
    e são **superados, quanto ao estado corrente, por este item e pelo 85**.
85. **A presente entrega é EXCLUSIVAMENTE a reconciliação documental de
    `docs/00-estado-atual.md` após o merge do PR #95.** Base reconciliada:
    `b06c0a43bd2f96b8712638e99c55edfe2fb2f99f`. Ela altera **exclusivamente este documento**
    e **não altera código, testes, `docs/02`, `docs/03`, `docs/04`, `docs/05`, `docs/06`,
    `docs/07`, `docs/08`, `knowledge/**` nem `prompts/**`**. **Esta reconciliação reexecutou
    as quatro execuções após a edição deste documento** — **`284`**, **`284`** sob
    `-W error`, **`2446`** e **`2446`** sob `-W error`, em **Python 3.14.5** —, com os
    **mesmos resultados medidos após o merge**; **nenhuma contagem é presumida além dessas**.
    **Nada é materializado aqui**, **nenhuma numeração nova é criada**, **nenhuma lacuna
    normativa é arbitrada** — em particular a de **`hora`**, a do **domínio de `ASSERTIVA`
    além do booleano** e a da **identidade física de fragmento** — e a **3B.8 continua não
    existindo**. **A PRÓXIMA MICROENTREGA FUNCIONAL DE `C` AINDA NÃO FOI ESCOLHIDA NEM
    INICIADA**: sua definição **depende de nova orquestração/auditoria do GPT**. Em
    particular, **não se assume aqui** que a próxima seja o formato **`hora`**, o **índice
    real**, o **extrator**, o ***renderer***, os ***templates***, a **canonicalização de
    status**, a **gramática de `caminho_yaml`**, a **execução física da bijeção** ou a
    **integração de consumidor** — **nenhuma pendência é eleita**, nem o restante de **`C`**,
    nem **R2**, nem **S2-D8**, nem **`N-b-RES2`**, nem o **produtor LLM**, nem a
    **integração da etapa 4**, nem a **integração da etapa 13**, nem o
    **`OrquestradorMotor`**. **Nenhuma etapa funcional seguinte está iniciada.** **Esta é a
    única reconciliação pós-PR #95**: nenhuma "reconciliação da reconciliação" será criada.
    **Aquela reconciliação foi integrada depois pelo PR #96** — commit documental
    `82e2ee972566f0e4d45e652e60be3c257d0670e7`, merge
    `b48db2c58b0348b40773baffcc60180cfdc06bb1`, branch de origem
    `docs/reconciliar-estado-pos-pr95`, **exclusivamente** `docs/00-estado-atual.md`,
    **327 adições / 66 remoções**. **Documental**: **não alterou o marco funcional**. **O
    item 85 permanece correto como registro do momento em que foi escrito** — quando o
    canonicalizador de status ainda não existia e a baseline era **`2446 passed`** — e é
    **superado, quanto ao estado corrente, pelo item 86**.
86. **A SÉTIMA MICROENTREGA FUNCIONAL DE `C` — o canonicalizador determinístico de rótulo de
    status já extraído — está MATERIALIZADA e INTEGRADA à `main` pelo PR #97** (**MERGED**),
    e **a presente entrega é EXCLUSIVAMENTE a reconciliação documental de
    `docs/00-estado-atual.md` após esse merge.**
    **Integração**: commit funcional `4749efa74d5684b52b4f457176710ba6e212c627`, merge
    `8c67e13808da59dbace413fce33c2c22280e69a3`, branch de origem `feat/c-response-status`,
    título `feat: add deterministic response status canonicalizer`, base
    `b48db2c58b0348b40773baffcc60180cfdc06bb1`, integrada em **2026-09-02T20:47:15Z**, após
    **autorização humana explícita**. Arquivos: **exclusivamente**
    `src/casa77_sdr/response_status.py` (**novo**, **+162 / −0**) e
    `tests/test_response_status.py` (**novo**, **+1093 / −0**) — **dois arquivos**, **1255
    adições / 0 remoções**, **nenhum arquivo preexistente alterado**. Os **blobs integrados**
    são exatamente os **blobs staged auditados**: `ceeb24cc…` para o módulo e `6028b883…`
    para o teste. **Não há CI remoto configurado**: `gh pr checks 97` reportou **ausência de
    checks** — **ausência de CI, não falha** —, e a PR não recebeu review nem comentário.
    **Entrega FUNCIONAL**: **passa a ser o marco funcional** da `main`, **sem numeração de
    subetapa** — a **3B.7** continua a última numerada e a **3B.8 NÃO EXISTE**. **Nenhuma
    nomenclatura normativa `E2`–`E7` foi criada.**
    **API pública local**: **`StatusNaoCanonicalizavel`** e
    **`canonicalizar_status(rotulo: str) -> str`** — **`__all__` com exatamente dois nomes**,
    **um único parâmetro**, **sem default** e **sem parâmetro de contexto, origem, modo,
    tolerância, fragmento, `Rxx`, configuração ou normalização**. A exceção deriva
    **diretamente de `Exception`**. O módulo **não é exportado** por `casa77_sdr/__init__.py`.
    **Tabela automática fechada — exatamente três linhas**, do contrato `C-A1-ST`:
    `APROVADO` → `APROVADO` (**C-A1-ST1**); `AGUARDA APROVAÇÃO` → `AGUARDA_APROVACAO`
    (**C-A1-ST2**); `APROVADO com handoff obrigatório` → `APROVADO` (**C-A1-ST3**). O
    **sufixo de handoff NÃO é transportado** pela saída: é instrução operacional e fica
    **fora de `C`** (C-2f, C-5.1). **Nenhuma quarta tradução**, e **`BLOQUEADO` nunca é
    produzido como imagem** — ele pertence a `C-3`, mas **nenhuma linha de `C-A1-ST` o
    produz automaticamente a partir de um rótulo simples**.
    **Entrada e tipos.** O **rótulo chega já extraído**; **a origem correta do rótulo é
    pré-condição do chamador** e **não é verificável nesta fronteira** sem transformá-la em
    extrator. O rótulo precisa ser do tipo `str` **exatamente**: **subclasse de `str` é
    recusada antes de qualquer consulta à tabela**, porque poderia redefinir `__eq__` e
    `__hash__` e decidir por conta própria a pertença; **sem `str(...)`**, **sem `repr`** e
    **sem coerção**. A **comparação é literal**: **sem `strip`, `lower`, `upper`, `casefold`,
    `NFC`, `NFD`, `unicodedata`, colapso de espaços, substituição de espaço inquebrável,
    tolerância de acento ou de caixa** — variantes de caixa, espaçamento, forma decomposta,
    espaço inquebrável ou acentuação ausente são **rótulos distintos** e são recusadas.
    **Precedência e contrato de erro**: a validação segue a ordem fixa **tipo do rótulo →
    pertença à tabela automática → retorno**; a **primeira violação encerra** e **nada é
    acumulado** (**P5**). **Duas** categorias técnicas privadas e fechadas — `tipo_invalido`
    e `rotulo_nao_mapeado` — e **um** localizador — `rotulo` —, nenhum deles identificador
    normativo de `C`. A mensagem tem a forma `<categoria>: <localizador>` e **nunca** ecoa o
    rótulo, o conteúdo, o **tipo concreto**, `repr`, um comprimento ou um índice; **sem
    `__cause__`** e **sem `__context__`**.
    **`PARCIAL` e `BLOQUEADO`, registrados expressamente.** **`PARCIAL` continua SEM tradução
    automática** e **continua exigindo mapeamento explícito no nível dos fragmentos
    emitíveis** (**C-A1-ST4**) — mapeamento que **esta entrega não implementa**.
    **`BLOQUEADO` não recebeu mapeamento automático inventado**: **C-A1-ST5** trata de
    `BLOQUEADO` **em nota interna**, que **não cria fragmento** e **não cria status**, e esta
    fronteira **não recebe esse contexto**. A categoria `rotulo_nao_mapeado` significa
    **"não existe tradução automática nesta fronteira"** — **jamais "não arbitrado"**.
    **Pureza e fronteiras**: o módulo importa **apenas** `__future__` — **zero I/O**, **zero
    *filesystem***, **zero YAML**, **zero *locale***, **zero rede**, **zero LLM**, **zero
    relógio**, **zero calendário**, **zero variável de ambiente**, **zero leitura de
    `knowledge/**`** e **zero dependência de `casa77_sdr.*`**. A tabela é uma `tuple`
    **imutável**, **fora de `__all__`**, **sem estado mutável de módulo**, a **entrada não é
    alterada** e o resultado é **determinístico** sob repetição, ordem e ambiente.
    **Baseline funcional passa a `2707 passed` / Python 3.14.5** — delta **+261** sobre os
    **`2446 passed`** do PR #95, correspondente exatamente ao arquivo direcionado **novo**.
    As **quatro** execuções — **`261`** e **`2707`**, ambas também sob `-W error`, com **zero
    failures, zero errors** e **zero warnings** nas variantes estritas — foram **auditadas
    antes do commit sobre os bytes da árvore de trabalho**, **medidas após o merge sobre a
    `main` integrada** e **reexecutadas nesta reconciliação após a edição deste documento**.
    **CANONICALIZAR STATUS NÃO É MATERIALIZAR `C`. O que continua fora**: a **extração do
    rótulo do Markdown** e a **extração de fragmento**, que **continuam inexistentes**; a
    **decisão de emissibilidade**; a **identidade física de fragmento**; a **criação do
    índice real** — `knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE** —; a
    **leitura do índice real**; a **resolução de *bindings***; a **execução da bijeção
    física**; a **prova de completude do corpus**; **`C-A1-ST6`–`C-A1-ST10`**, **não
    satisfeitas**; a **migração da autoridade de status**, que **não ocorreu**; a
    **integração de consumidor**, que **não ocorreu** — **nenhum chamador real existe**; o
    formato **`hora`**; a **gramática física de `caminho_yaml`**; ***templates* e *bindings*
    físicos**; ***renderer***; **equivalência `C-15`**; **R2**; **S2-D8**; **`N-b-RES2`**; o
    **`OrquestradorMotor`**; **calendário**; **LLM**; e a **3B.8**. **A autoridade de status
    NÃO migrou**: enquanto as cinco condições de `C-A1-ST6`–`C-A1-ST10` não valerem
    integralmente, `knowledge/respostas-aprovadas.md` **continua a autoridade de status**
    (**C-11**) e o status **não é removido do Markdown**. `C`, como **entrega completa do
    índice estruturado**, **continua ARBITRADA / NÃO MATERIALIZADA**. Continuam inalterados:
    **`C-A2-N9`**, **`C-A2-N10`**, **`C-A2-N11` (16/16)** e **`C-A2-N12`** = **CUMPRIDAS**;
    **`R2` NÃO MATERIALIZADA**; **`S2-D8` ARBITRADA / NÃO MATERIALIZADA**; **`N-b-RES2`
    ABERTO**; **`OrquestradorMotor` NÃO IMPLEMENTADO**; **3B.8 INEXISTENTE**; e **`Q2`–`Q5`
    NÃO RESOLVIDAS por esta entrega**.
    **Quanto a esta reconciliação em si**: ela **altera exclusivamente este documento** e
    **não altera código, testes, `docs/02`, `docs/03`, `docs/04`, `docs/05`, `docs/06`,
    `docs/07`, `docs/08`, `knowledge/**` nem `prompts/**`**. **Nada é materializado aqui**,
    **nenhuma numeração nova é criada**, **nenhuma lacuna normativa é arbitrada** — em
    particular a de **`hora`**, a do **mapeamento explícito de `PARCIAL`** e a da
    **identidade física de fragmento** — e a **3B.8 continua não existindo**. **A OITAVA
    MICROENTREGA FUNCIONAL DE `C` NÃO FOI ESCOLHIDA NEM INICIADA**: sua definição **depende
    de nova orquestração/auditoria do GPT**. Em particular, **não se assume aqui** que a
    próxima seja o formato **`hora`**, o **índice real**, o **extrator**, o ***renderer***,
    os ***templates***, a **gramática de `caminho_yaml`**, o **mapeamento explícito de
    `PARCIAL`**, a **execução física da bijeção** ou a **integração de consumidor** —
    **nenhuma pendência é eleita**, nem o restante de **`C`**, nem **R2**, nem **S2-D8**, nem
    **`N-b-RES2`**, nem o **produtor LLM**, nem a **integração da etapa 4**, nem a
    **integração da etapa 13**, nem o **`OrquestradorMotor`**. **Nenhuma etapa funcional
    seguinte está iniciada.** **Os itens 84 e 85 acima permanecem corretos como registro do
    momento em que foram escritos** — quando o canonicalizador ainda não existia e a baseline
    era **`2446 passed`** — e são **superados, quanto ao estado corrente, por este item**.
    **Esta é a única reconciliação pós-PR #97**: nenhuma "reconciliação da reconciliação"
    será criada.
87. **A PRESENTE ENTREGA É EXCLUSIVAMENTE A MICRO-ARBITRAGEM DOCUMENTAL `C-A5` —
    IDENTIDADE FÍSICA DO FRAGMENTO EMITÍVEL.**
    **ESTE ITEM 87 É DOCUMENTAL. ELE NÃO É "SUBETAPA 87", NÃO É `E8` E NÃO É A OITAVA
    MICROENTREGA FUNCIONAL DE `C`.** Ele registra **somente** a arbitragem documental
    `C-A5`, e **nenhum item 88 é criado**.
    **Escopo.** Arquivos alterados: **dois** — `docs/07-arquitetura-motor-respostas.md`
    (**puramente aditivo**, com o bloco **"Micro-arbitragem C-A5"** inserido **após o bloco
    C-A4** e **antes** da seção **§3**) e `docs/00-estado-atual.md`. **Nenhum outro arquivo
    foi tocado**: **zero `src/**`**, **zero `tests/**`**, **zero `knowledge/**`**, **zero
    `prompts/**`**, **zero `CLAUDE.md`** e **zero outro `docs/**`**. **Nenhum marco
    funcional novo é criado.**
    **`C-A5` = ARBITRADA DOCUMENTALMENTE / NÃO MATERIALIZADA.**
    **O que `C-A5` fecha.** **Exclusivamente** a matéria que `C-A1` registrava como
    explicitamente **não decidida** — a **identidade física do fragmento** —, e **nenhuma
    outra lacuna** (`C-A5-H2`). **`C-1`–`C-15`, `C-A1`, `C-A2`, `C-A3` e `C-A4` permanecem
    registro histórico e não são reescritos** (`C-A5-H1`); o parágrafo de `C-A1` que
    registrava a matéria como não decidida **permanece correto para o momento em que foi
    escrito** (`C-A5-Z`).
    **Contrato arbitrado.** **`C-A5-U`** — a **unidade emitível física futura** é o **bloco
    de citação contíguo** (**sequência maximal de linhas iniciadas por `>`**, terminada pela
    **primeira linha que não se inicia por `>`**), **dentro de uma seção `## Rxx`**;
    **somente na representação materializada** (`C-A5-M2`) a unidade **existe se e somente
    se** estiver **imediatamente precedida por marcador válido**, e **nota, instrução
    operacional, comentário editorial e conteúdo não emitível** **não podem** ser
    representados como bloco emitível, permanecendo **fora da bijeção**, **sem status**,
    **sem *binding*** e **sem `ASSERTIVA`** (**C-2m**–**C-2p**, **`C-A1-B2`**) — **sem
    reclassificar retroativamente o corpus atual**. **`C-A5-I`** — **marcador**
    `<!-- fragmento: <id> -->`, **linha com exatamente essa estrutura**, na **linha
    imediatamente anterior** ao bloco e **sem linha em branco** entre ambos; **gramática
    fechada do `id`**: **`F`** seguido de **inteiro decimal ASCII maior que zero e sem zero
    à esquerda**; **unicidade somente dentro do respectivo `Rxx`**, o que **preserva
    literalmente `C-2h`**; **identidade declarada, nunca derivada** — **não pode depender**
    de posição, ordem, linha, offset, índice, redação, whitespace, conteúdo comercial,
    hash, timestamp, UUID sem regra de governança, LLM, banco ou serviço externo; **`id`
    nunca reutilizado** no mesmo `Rxx` após `C-A5-M2`; **reordenação, inserção, remoção ou
    reescrita não muda a identidade das unidades restantes**; e a **identidade de fragmento
    é distinta** do **identificador estrutural de item de coleção** de
    **`C-A1-S3`**–**`C-A1-S5`** / **MD-18**. **`C-A5-T`** — **identidade canônica**
    `<Rxx>/<id>`, com separador **`/`** justificado **exaustivamente** por **`/` não
    pertencer à gramática de `Rxx`** e **não pertencer à gramática do `id` de `C-A5`**,
    donde a composição é **injetiva** e a decomposição **unívoca**; o token **será** o dos
    **dois domínios físicos** de **`C-A1-B3`** / **`C-A1-B4`** — **o que NÃO executa a
    bijeção** — e é **derivado, nunca armazenado**, mantendo o futuro índice **o `Rxx`** e
    **`fragmentos[].id`** **separadamente**, **sem campo novo de token canônico**.
    **Ativação diferida.** **`C-A5-M1`**: a **integração documental de `C-A5` NÃO ativa** a
    nova representação física; a ativação **depende de entrega própria posterior**,
    **auditada e integrada**. **`C-A5-M3`**: enquanto isso, `knowledge/respostas-aprovadas.md`
    permanece na **representação física atualmente aprovada**, os **37 fragmentos emitíveis
    documentados continuam reconhecidos**, a **ausência de marcador NÃO é erro do corpus
    atual**, **nenhum bloco existente fica fail-closed** por `C-A5`, a **autoridade de
    status continua** em `knowledge/respostas-aprovadas.md` (**C-11**) e **C continua
    ARBITRADA / NÃO MATERIALIZADA**. **`C-A5-M4`**: **zero marcador inserido**, **zero `id`
    atribuído**, **zero tabela dos 37 produzida**, **zero tabela aprovada** e **zero caso
    individual decidido**. **`C-A5-M5`**: a futura aplicação exige, **ANTES de qualquer
    edição do corpus**, **tabela completa e aprovada** `Rxx` + unidade física atual → `id`
    `C-A5`, preservando **IDs de fragmento já comprometidos por documentação normativa
    anterior**. **`C-A5-M6`**: **posição e ordem** servem **apenas** como **localizador de
    evidência apresentado ao responsável humano** e **jamais determinam o `id`**.
    **Evidência estrutural read-only.** Medida **sem alterar `knowledge/**`** e **sem
    reproduzir conteúdo**: **30 `Rxx`**; **37 blocos de citação contíguos**; **24 `Rxx` com
    um fragmento**; **6 `Rxx` multi-fragmento**; **zero comentários HTML existentes**; e
    **zero marcador `C-A5` aplicado**. Registram-se **separadamente**:
    **COMPATIBILIDADE ESTRUTURAL: 37/37** e **MAPEAMENTO DE IDENTIDADE PARA APLICAÇÃO: NÃO
    PRODUZIDO / NÃO APROVADO** — **compatibilidade estrutural NÃO é mapeamento de
    identidade**. **`R09` possui dois fragmentos físicos sem `id` `C-A5` normativamente
    atribuído e permanece PENDÊNCIA DE MAPEAMENTO HUMANO**; **esta entrega não atribui
    esses IDs** e **não produz a tabela dos 37**.
    **Limites.** **`C-A5` NÃO decide** a **propagação do status do cabeçalho `Rxx` aos
    fragmentos** nem o **mapeamento concreto de `PARCIAL`** — **ambos continuam ABERTOS**
    (`C-A5-X2`) —, e **NÃO decide** **sintaxe de *placeholder***, **gramática de
    `caminho_yaml`**, **formato `hora`** nem **`C-7`** (`C-A5-X3`). **`C-A5` NÃO** cria
    índice, *template* físico, *binding* físico ou `ASSERTIVA` física; **não** implementa
    extrator nem *renderer*; **não** executa a bijeção física; e **não** migra autoridade de
    status — **`C-A1-ST6`–`C-A1-ST10` continuam NÃO satisfeitas** (`C-A5-X4`). **`C-A5` não
    cria** componente, responsabilidade, condição, evento, estado, transição, ação, erro de
    runtime, cenário de runtime, status, formato, predicado nem subetapa: **a 3B.8 continua
    INEXISTENTE** (`C-A5-X5`). **Após a arbitragem** (`C-A5-X6`): **C continua ARBITRADA /
    NÃO MATERIALIZADA**; `knowledge/indice-respostas-aprovadas.yaml` **continua
    INEXISTENTE**; **`R2` permanece como está**; **`S2-D8` permanece como está**;
    **`N-b-RES2` permanece ABERTO**; e o **`OrquestradorMotor` permanece NÃO IMPLEMENTADO**.
    **Testes.** **NENHUM `pytest` FOI EXECUTADO NESTA ENTREGA**, por **zero código, zero
    teste e zero `knowledge/**`**. **Nenhuma execução nova é alegada.** A **baseline
    funcional permanece `2707 passed`**, com **`261 passed`** no direcionado, em **Python
    3.14.5**, **preservada como a última baseline funcional confirmada anteriormente** —
    medida sobre o **commit funcional `4749efa74d5684b52b4f457176710ba6e212c627`** e o
    **merge `8c67e13808da59dbace413fce33c2c22280e69a3`**. As validações desta entrega foram
    **documentais e de Git**: `git diff --check`, inspeção de diff, contagens mecânicas
    read-only e verificação de segurança das linhas adicionadas.
    **Estado corrente preservado.** **Último commit funcional**:
    `4749efa74d5684b52b4f457176710ba6e212c627`; **merge funcional**:
    `8c67e13808da59dbace413fce33c2c22280e69a3`; **sétima microentrega funcional de `C`** =
    **última entrega funcional**; **3B.7** = **última subetapa numerada**; **3B.8** =
    **INEXISTENTE**; e **A OITAVA MICROENTREGA FUNCIONAL DE `C` CONTINUA NÃO ESCOLHIDA E
    NÃO INICIADA** — **nenhuma pendência é eleita** por este item, **nem** o formato
    `hora`, **nem** o índice real, **nem** o extrator, **nem** o *renderer*, **nem** os
    *templates*, **nem** a gramática de `caminho_yaml`, **nem** o mapeamento explícito de
    `PARCIAL`, **nem** a execução física da bijeção, **nem** a integração de consumidor,
    **nem** a aplicação dos marcadores `C-A5`. **Nenhuma etapa funcional seguinte está
    iniciada.** **O item 86 acima permanece correto como registro do momento em que foi
    escrito** — inclusive ao listar a **identidade física de fragmento** entre as lacunas
    então não arbitradas —, e é **complementado, quanto a essa lacuna específica, por este
    item 87**.
88. **A PRESENTE ENTREGA É EXCLUSIVAMENTE O REGISTRO DOCUMENTAL DO MAPEAMENTO HUMANO
    APROVADO `C-A5-M5` — 37/37 UNIDADES FÍSICAS ATUAIS.**
    **ESTE ITEM 88 É DOCUMENTAL. NÃO É "SUBETAPA 88", NÃO É `E8` E NÃO É A OITAVA
    MICROENTREGA FUNCIONAL DE `C`.** Ele registra **somente** a Fase A2 — a tabela exigida
    por **`C-A5-M5`** —, e **nenhum item 89 é criado**.
    **Aprovação humana.** O responsável **aprovou explicitamente** o mapeamento de
    identidade das **37 unidades físicas atuais**, **incluindo `R23/F2` como a unidade de
    decoração**. Essa aprovação **não autoriza** aplicação de marcadores, edição do corpus,
    criação do índice real, extrator, *renderer*, *templates* ou *bindings* físicos,
    execução da bijeção, migração de autoridade de status nem a oitava microentrega
    funcional.
    **Escopo.** Arquivos alterados: **dois** — `docs/07-arquitetura-motor-respostas.md`
    (**puramente aditivo**, com o bloco **"Registro pós-C-A5-M5 — mapeamento humano aprovado
    das 37 unidades"** inserido **após o bloco C-A5** e **antes** da seção **§3**) e
    `docs/00-estado-atual.md`. **Nenhum outro arquivo foi tocado**: **zero `src/**`**, **zero
    `tests/**`**, **zero `knowledge/**`**, **zero `prompts/**`**, **zero `CLAUDE.md`** e
    **zero outro `docs/**`**. **Nenhum marco funcional novo é criado.** O bloco novo **não
    reescreve `C-A5`** e **não renumera seção alguma**.
    **Corpus-base.** `knowledge/respostas-aprovadas.md`, **blob
    `d9f275454cb9f091a824292560d983d25f08c14e`** — **INALTERADO** por esta entrega. A tabela
    vale **para esse corpus-base**; se o corpus mudar antes da aplicação, o mapeamento
    precisa ser **reconferido**.
    **Fechamento aritmético.** **37** unidades; **30 `Rxx`**; **24** de fragmento único e
    **6** multi-fragmento — `R05` = 3, `R09` = 2, `R11` = 2, `R12` = 2, `R23` = 2, `R25` = 2:
    **24 + 3 + 2 + 2 + 2 + 2 + 2 = 37**. Por base: **8 PRESERVAÇÃO NORMATIVA**, **1
    CONFIRMAÇÃO HUMANA EXPLÍCITA**, **28 DECISÃO HUMANA EXPLÍCITA** — **8 + 1 + 28 = 37**.
    **Zero unidade sem `id` aprovado.** Os **37** tokens canônicos derivados `<Rxx>/<id>` são
    **distintos dois a dois**; **nenhum `id` se repete dentro do mesmo `Rxx`**
    (**`C-A5-I4`**, **C-2h**); a repetição de **`F1`** entre `Rxx` **distintos** é **válida**,
    por a unicidade ser **local ao `Rxx`**; e todos respeitam **`C-A5-I3`** — **`F`** seguido
    de inteiro decimal ASCII **maior que zero** e **sem zero à esquerda**.
    **Origem de cada identidade — nunca o ordinal.** Conforme **`C-A5-I5`** e **`C-A5-M6`**,
    os localizadores `bloco 1`/`bloco 2`/`bloco 3` e os descritores de matéria são **APENAS
    localizador da evidência física atual** e **NÃO originaram nenhum `id`**. **Os 24 `Rxx`
    de fragmento único receberam `F1` por DECISÃO HUMANA EXPLÍCITA — NÃO por serem únicos ou
    primeiros.** **`R09` recebeu `F1` e `F2` por decisão humana explícita**, e **`bloco 1` /
    `bloco 2` não geraram esses `id`**. **`R11`** teve a lacuna fechada por **decisão humana
    explícita** — **`F1` na unidade de duração/limite**, **não** por ser o primeiro bloco —,
    preservando **`R11/F2`** na unidade de montagem/desmontagem (**`MD-5`**, **`C-A2-B1`**).
    **`R12`** teve a lacuna fechada por **decisão humana explícita** — **`F2` na unidade de
    não incluso**, **não** por ser o segundo bloco —, preservando **`R12/F1`** na unidade de
    itens inclusos (**`C-A2-B2`**, **`MD-19`**). **Os 8 compromissos normativos anteriores
    foram preservados**: `R05/F1`, `R05/F2`, `R05/F3` (**`C-A2-B10`**, **`C-A2-B16a`**–
    **`C-A2-B16c`**, **`B16-A`**, **`B16-B`**), `R11/F2`, `R12/F1`, `R23/F1` (**`C-A2-B5`**),
    `R25/F1` (**`C-A2-B6`**) e `R25/F2` (**`MD-10`**) — conforme **`C-A5-M5`** e
    **`C-A5-E7`**.
    **Resolução de `R23/F2`.** A pendência **identificada no inventário read-only A1** era
    **qual unidade física porta `R23 F2`**, a partir da **leitura conjunta de `MD-13` e
    `C-A2-B5`**: **`MD-13`** declara alvo `R23 F2` com escopo que abrange o **motivo de
    fogos** — residente na unidade já fixada como `R23/F1` por **`C-A2-B5`** — e a **regra de
    decoração**, residente na outra. **`C-A5-E8` permanece inalterada e refere-se
    exclusivamente à pendência de mapeamento de `R09`.** Decisão humana registrada: **`R23/F2`
    designa fisicamente a unidade de decoração**. Reconciliação **sem reescrita**:
    **`C-A2-B5` permanece histórico e preserva `R23/F1`**; **`MD-13` permanece histórico**;
    o **escopo de modelagem de `MD-13` pode envolver fatos relevantes a mais de um
    fragmento** — alvo de modelo **não é** designação de identidade física; a referência
    histórica de `MD-13` a `R23 F2` **NÃO desloca o motivo de fogos de `R23/F1`**; e, **para
    identidade física C-A5**, **`R23/F2` = unidade de decoração**. **`MD-13` NÃO é
    executada** e **nenhum conteúdo é alterado**.
    **Estado após esta entrega.** **`C-A5-M5` = SATISFEITA DOCUMENTALMENTE** para o
    corpus-base `d9f275454cb9f091a824292560d983d25f08c14e`. **`C-A5-M2` CONTINUA NÃO ATIVA**
    — a representação marcada **ainda não é obrigatória**. **ZERO marcador aplicado**, e a
    **ausência de marcador continua NÃO sendo erro do corpus atual** (**`C-A5-M3`**).
    **`C-A5` continua NÃO MATERIALIZADA no corpus** e **C continua ARBITRADA / NÃO
    MATERIALIZADA**. `knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE**. A
    **bijeção física continua NÃO EXECUTADA** e **`C-A1-ST6`–`C-A1-ST10` continuam NÃO
    satisfeitas**. A **autoridade de status NÃO migrou** — `knowledge/respostas-aprovadas.md`
    continua a autoridade (**C-11**). Continuam **ABERTAS**: propagação de status ao
    fragmento; mapeamento concreto de `PARCIAL`; sintaxe de *placeholder*; gramática de
    `caminho_yaml`; formato `hora`; **C-7**. **Esta entrega satisfaz o gate anterior à edição
    do corpus; ela NÃO executa essa edição.**
    **Testes.** **NENHUM `pytest` FOI EXECUTADO NESTA ENTREGA**, por **zero código, zero
    teste e zero `knowledge/**`**. **Nenhuma execução nova é alegada.** A **baseline funcional
    permanece `2707 passed`**, com **`261 passed`** no direcionado, em **Python 3.14.5**,
    **preservada como a última baseline funcional confirmada anteriormente**, sobre o
    **commit funcional `4749efa74d5684b52b4f457176710ba6e212c627`** e o **merge
    `8c67e13808da59dbace413fce33c2c22280e69a3`**. As validações desta entrega foram
    **documentais e de Git**: `git diff --check`, inspeção integral do diff, contagem da
    tabela, unicidade de `Rxx/id`, gramática dos `id`, escopo de arquivos e segurança.
    **Estado corrente preservado.** **Sétima microentrega funcional de `C`** = **última
    entrega funcional**; **3B.7** = **última subetapa numerada**; **3B.8** = **INEXISTENTE**;
    e **A OITAVA MICROENTREGA FUNCIONAL DE `C` CONTINUA NÃO ESCOLHIDA E NÃO INICIADA** —
    **nenhuma pendência é eleita** por este item, **nem** a aplicação dos marcadores `C-A5`,
    **nem** o formato `hora`, **nem** o índice real, **nem** o extrator, **nem** o
    *renderer*, **nem** os *templates*, **nem** a gramática de `caminho_yaml`, **nem** o
    mapeamento explícito de `PARCIAL`, **nem** a execução física da bijeção, **nem** a
    integração de consumidor. **O item 87 acima permanece correto como registro do momento em
    que foi escrito** — quando a tabela **ainda não existia** e `R09` e `R23/F2` eram
    pendências de mapeamento humano —, e é **complementado, quanto ao mapeamento, por este
    item 88**.
89. **A PRESENTE ENTREGA É EXCLUSIVAMENTE A MATERIALIZAÇÃO FÍSICA `C-A5` — APLICAÇÃO DOS 37
    MARCADORES APROVADOS AO CORPUS.**
    **ESTE ITEM 89 É DOCUMENTAL/EDITORIAL. NÃO É "SUBETAPA 89", NÃO É `E9`, NÃO É A OITAVA
    NEM A NONA MICROENTREGA FUNCIONAL DE `C`.** Ele registra **somente** a aplicação física
    dos marcadores já mapeados, e **nenhum item 90 é criado**.
    **Autorização humana.** O responsável autorizou **explicitamente** a aplicação dos 37
    marcadores conforme o mapeamento **`C-A5-M5`** aprovado, **aceitando** que, **após a
    integração auditada desta materialização**, **`C-A5-M2` ficará ativa antes da
    implementação do validador permanente da representação marcada**. A autorização **não**
    abrange código, testes novos, índice real, extrator, *renderer*, bijeção física, migração
    de autoridade de status nem a oitava microentrega funcional.
    **Escopo.** Arquivos alterados: **dois** — `knowledge/respostas-aprovadas.md` e
    `docs/00-estado-atual.md`. **`docs/07-arquitetura-motor-respostas.md` NÃO foi alterado** e
    permanece no blob `2181e03246cf1236557b8fd4ce7f3c750dfc02eb`. **Zero `src/**`**, **zero
    `tests/**`**, **zero `prompts/**`**, **zero `knowledge/casa77.yaml`**, **zero
    `knowledge/informacoes-pendentes.md`**, **zero `CLAUDE.md`** e **zero outro `docs/**`**.
    **Nenhum marco funcional novo é criado.**
    **Edição aplicada.** Para **cada uma das 37 unidades físicas**, o marcador
    `<!-- fragmento: <id> -->` foi inserido na **linha imediatamente anterior** à **primeira
    linha `>`** do bloco, **sem linha em branco** entre marcador e bloco e **preservando** a
    linha em branco já existente antes do ponto de inserção. **O diff do corpus é exatamente
    `+37 / −0`.** **Nenhuma linha preexistente foi alterada, removida ou reordenada**;
    **nenhum texto emitível, status ou cabeçalho foi tocado**; **nenhuma normalização de EOL
    permanece no estado final**.
    **Origem das identidades — nunca o ordinal.** **Todas as 37 identidades vêm
    exclusivamente da tabela `C-A5-M5` humanamente aprovada** (**`C-A5-I5`**, **`C-A5-M6`**);
    **nenhum `id` foi derivado de posição, ordem ou unicidade da unidade**, e **nenhuma
    identidade nova foi criada**. A base usada para **localizar** cada unidade física dos 6
    `Rxx` multi-fragmento foi: **`R05`** — o **rótulo declarativo do próprio corpus**
    (`F1`/`F2`/`F3`); **`R09`** — o **localizador humano aprovado** `bloco 1` / `bloco 2`, que
    é **localizador de evidência da unidade já identificada e aprovada**, e **não** derivação
    de ordem; **`R11`**, **`R12`**, **`R23`** e **`R25`** — o **descritor de matéria** fixado
    na tabela aprovada.
    **Validação determinística executada.** Estrutura pós-edição: **30 `Rxx`**, **37 blocos
    de citação contíguos**, **24** de fragmento único e **6** multi-fragmento (`R05` = 3;
    `R09`, `R11`, `R12`, `R23`, `R25` = 2 cada) — **inalterada**, o que exclui cisão ou
    inserção intrabloco. **37** linhas contendo `<!--`, **todas** na forma exata
    `<!-- fragmento: F<n> -->`, com `id` conforme **`C-A5-I3`** (**`F`** + inteiro decimal
    ASCII maior que zero, sem zero à esquerda) e **zero outro comentário HTML**.
    **Pareamento marcador↔bloco = 37/37**: cada bloco com marcador válido imediatamente
    acima, cada marcador
    seguido imediatamente por linha `>`, **zero marcador órfão** e **zero bloco sem
    marcador**. **Unicidade**: **zero `id` duplicado dentro do mesmo `Rxx`** (**`C-A5-I4`**,
    **C-2h**), com repetição de `F1` entre `Rxx` distintos **válida** por a unicidade ser
    local. **Correspondência com a tabela aprovada**: **37 correspondências, zero ausente,
    zero extra, zero divergente**.
    **Prova byte-a-byte.** Removidas **exclusivamente** as 37 linhas de marcador, com seus
    terminadores, o corpus reconstruído é **binariamente idêntico** ao estado anterior:
    **SHA-256 `7cf1aa058c851a6642f5af0d0600a8a66091b09b70d4a58989b26a2aad6db344`**, **9 712
    bytes**, **253 LF**, **253 CR** — comparação binária **IDÊNTICA**. Esta é a prova de que
    a **única** mudança física do corpus são as **37 linhas autorizadas**.
    **Proveniência dessa prova — esclarecimento posterior, sem substituição da evidência.**
    Os valores **9 712 bytes / 253 LF / 253 CR** descrevem a **representação do checkout
    `CRLF`** com que a verificação histórica foi executada nesta máquina — `core.autocrlf`
    converte `LF` em `CRLF` na árvore de trabalho. **O blob Git canônico do corpus NÃO tem
    253 `CR`**: ele é **`LF`-only, com 253 `LF` e 9 459 bytes** na mesma reconstrução. **A
    evidência histórica acima permanece verdadeira e não é substituída**; o que se acrescenta
    é a sua proveniência. **A prova Git canônica da preservação** é: removidas exclusivamente
    as 37 linhas de marcador, o objeto reconstruído corresponde ao **blob Git anterior
    `d9f275454cb9f091a824292560d983d25f08c14e`** — a mesma conclusão, expressa no domínio em
    que o Git armazena o conteúdo.
    **Corpus-base imediatamente anterior a esta entrega.** `knowledge/respostas-aprovadas.md`,
    blob **`d9f275454cb9f091a824292560d983d25f08c14e`**.
    **Regra de vigência deste registro.** **Enquanto esta entrega não pertencer ao histórico
    da `main`**, o **corpus canônico permanece no estado imediatamente anterior**, **`C-A5-M2`
    continua NÃO ATIVA**, os **37 marcadores constituem somente representação candidata na
    branch/PR**, a **ausência de marcador não é erro** e **nenhum bloco fica fail-closed**
    (**`C-A5-M3`**). **A partir do primeiro estado da `main` que contiver conjuntamente esta
    entrega e os 37 marcadores**, por **`C-A5-M1`** / **`C-A5-M2`**, **`C-A5-M2` = ATIVA** e
    **`C-A5` = MATERIALIZADA no corpus**, passando também a vincular **`C-A5-X1`** e
    **`C-A5-I6`**. Esse efeito é **automático** e **não depende de nova reconciliação
    documental**; o responsável **aceitou expressamente** que ele ocorrerá **antes** da
    implementação do validador permanente — **que esta entrega NÃO implementa**. **Mesmo
    nesse estado pós-integração**: **C continua ARBITRADA / NÃO MATERIALIZADA**; o **índice
    real continua inexistente**; a **bijeção física continua NÃO EXECUTADA**; a **autoridade
    de status não migra**; **`C-A1-ST6`–`C-A1-ST10` continuam NÃO satisfeitas**; a **oitava
    microentrega funcional continua não escolhida e não iniciada**; e a **3B.8 continua
    inexistente**.
    **Testes.** **Nenhum teste novo foi criado e nenhum teste existente foi alterado.** A
    suíte existente foi reexecutada: **`2707 passed`** sob `-W error`, em **Python 3.14.5**,
    **zero failures, zero errors e zero warnings** — **mesma baseline anteriormente
    confirmada**, sobre o **commit funcional `4749efa74d5684b52b4f457176710ba6e212c627`**.
    **Estado corrente preservado.** `knowledge/indice-respostas-aprovadas.yaml` **continua
    INEXISTENTE**; a **bijeção física continua NÃO EXECUTADA** e **`C-A1-ST6`–`C-A1-ST10`
    continuam NÃO satisfeitas**; a **autoridade de status NÃO migrou** — o Markdown continua
    a autoridade (**C-11**); **C continua ARBITRADA / NÃO MATERIALIZADA**; continuam
    **ABERTAS** a propagação de status ao fragmento, o mapeamento de `PARCIAL`, a sintaxe de
    *placeholder*, a gramática de `caminho_yaml`, o formato `hora` e **C-7**; **a 3B.8
    continua INEXISTENTE**; e **A OITAVA MICROENTREGA FUNCIONAL DE `C` CONTINUA NÃO ESCOLHIDA
    E NÃO INICIADA** — **nenhuma pendência é eleita** por este item. **O item 88 acima
    permanece correto como registro do momento em que foi escrito** — quando o mapeamento
    estava aprovado mas **ainda não aplicado ao corpus** —, e é **complementado, quanto à
    aplicação física, por este item 89**.

90. **A OITAVA MICROENTREGA FUNCIONAL DE `C` — O LEITOR/VALIDADOR DETERMINÍSTICO DA
    REPRESENTAÇÃO MARCADA `C-A5` — ESTÁ INTEGRADA À `main` PELO PR #102.**
    **ESTE ITEM 90 É REGISTRO HISTÓRICO DOCUMENTAL. NÃO É "SUBETAPA 90", NÃO É `E10`, NÃO É
    IDENTIFICADOR NORMATIVO DE `C` E NÃO CRIA A 3B.8** — a **3B.8 continua INEXISTENTE**, e a
    **3B.7 continua a última subetapa numerada**. Ele registra **somente** a integração da
    oitava microentrega funcional.
    **Integração.** **PR #102** — **commit funcional
    `341084d951b428d80c4ba573fbc38a4bc9f008c6`** (`feat: add deterministic C-A5 markdown unit
    reader`), **parent único `3e74bef58c0317d84142f590f9999849598fb126`**, **merge commit
    `067e894db8bddb96c192d7da3a4431f587f4efc0`** (merge commit **normal**, dois parents:
    `3e74bef58c…` e `341084d951…`), branch de origem `feat/c-response-markdown-units`,
    **preservada**. **A `main` passou de `3e74bef58c0317d84142f590f9999849598fb126` para
    `067e894db8bddb96c192d7da3a4431f587f4efc0`.**
    **Escopo.** **Dois arquivos novos, e nenhum outro**:
    `src/casa77_sdr/response_markdown_units.py` — **+396 / −0**, blob
    **`3c99d89aa0028f673548f5cc932ec166d592cd7f`** — e
    `tests/test_response_markdown_units.py` — **+1535 / −0**, blob
    **`ee3dc335b3d94588d183c8ebe64771e45df08c14`**. Total: **2 arquivos, +1931 / −0**.
    **Zero arquivo preexistente alterado**: **zero `docs/**`**, **zero `knowledge/**`**,
    **zero `prompts/**`**, **zero `CLAUDE.md`**, **zero `src/casa77_sdr/__init__.py`** e
    **zero configuração**. O **corpus permanece no blob
    `3bfb2e9fd18bac016e1dbe2c963ff916ceb0c96c`**, **inalterado pela integração**.
    **Fronteira entregue.** `ler_unidades_marcadas(texto: str) -> tuple[str, ...]` e
    `RepresentacaoMarcadaInvalida` — **`__all__` com exatamente dois nomes**. A função recebe
    Markdown **já em memória** e devolve **exclusivamente** os tokens canônicos `<Rxx>/<id>`
    de **`C-A5-T1`**, em **ordem física do documento**, **um por par marcador/bloco válido**,
    **derivados e nunca armazenados** (**`C-A5-T5`**). **`str` exata** — subclasse recusada
    antes de qualquer leitura. Documento vazio ou sem `## Rxx` devolve `tuple()`, o que **não
    afirma** que o corpus real esteja vazio, incompleto ou completo.
    **Falhas.** As **sete redações de `C-A5-X1`** estão cobertas por **SEIS** categorias
    técnicas estruturais — `bloco_sem_marcador`, `marcador_sem_bloco`,
    `marcador_fora_de_secao`, `id_fora_da_gramatica`, `id_duplicado`, `secao_sem_unidade` —
    mais `tipo_invalido` para o contrato de entrada. **`marcador órfão` e `marcador sem bloco
    imediatamente seguinte` são mecanicamente indistinguíveis nesta fronteira** e por isso
    compartilham `marcador_sem_bloco`: **NÃO existem "sete categorias técnicas C-A5"** e
    **nenhuma oitava falha foi criada**. As categorias são **privadas e fechadas** e **não
    são identificadores normativos de `C`**. A mensagem tem a forma `<categoria>:
    <localizador>`, com localizadores fechados `texto` / `bloco` / `marcador` / `secao`, e
    **nunca** ecoa o `id`, o `Rxx`, o conteúdo, o `repr`, o tipo concreto, um número de linha,
    um índice, um tamanho ou uma cardinalidade.
    **Decisões locais registradas.** **Linha**: divisão **exclusivamente** por `LF`, com
    remoção de **no máximo um** `CR` terminal — `LF` e `CRLF` produzem **resultado idêntico**;
    **`splitlines()` não é usado**, ***universal newline* não é aplicado**, e `U+2028`,
    `U+2029`, `U+0085`, `VT` e `FF` **permanecem conteúdo**; **decisão local do leitor, que
    NÃO altera `C-15`**. **Seção**: apenas cabeçalho ATX na **coluna 0**, um a seis `#`
    seguidos de espaço ou fim de linha; níveis 1 e 2 encerram a seção `##`, níveis 3–6 não;
    **`Setext`, *code fence*, bloco `HTML` e código indentado NÃO são interpretados**.
    **Marcador**: envelope exato em dois estágios, e quase-marcador é **conteúdo comum**, não
    marcador defeituoso. **Bloco de citação fora de `## Rxx`** está **fora do domínio de
    `C-A5-U2`** e é **ignorado inteiro** — sem token, sem erro e sem leitura do conteúdo —,
    enquanto **dentro de `Rxx` o bloco sem marcador válido é fail-closed** e **marcador válido
    fora de `Rxx` também é fail-closed**.
    **Não-garantias declaradas.** A fronteira **não garante unicidade global dos tokens**:
    ela **não verifica a unicidade física das seções `## Rxx`**, de modo que duas seções
    homônimas podem produzir o mesmo `<Rxx>/<id>` — **não-garantia deliberada**, e
    `response_bijection` **não é importado nem chamado** para supri-la. **`C-A5-I6` é
    respeitada como norma externa vigente e NÃO é provada**: um *snapshot* único não carrega
    histórico — **zero `Git`**, **zero armazenamento**, **zero estado entre chamadas**.
    **Pureza.** Importa **apenas** `__future__`: **zero I/O**, **zero *filesystem***, **zero
    `pathlib`**, **zero YAML**, **zero rede**, **zero LLM**, **zero relógio**, **zero
    calendário**, **zero *locale***, **zero variável de ambiente**, **zero banco**, **zero
    serviço externo**, **zero import de `casa77_sdr.*`** e **zero export** por
    `casa77_sdr/__init__.py`. **Somente o teste faz I/O.** Para o **corpus real** ele usa
    `read_bytes()` + `decode("utf-8")` — **sem `read_text()`** e **sem conversão de EOL antes
    do módulo**; **separadamente**, o teste lê o **código-fonte do módulo** com
    `read_text(encoding="utf-8")` para as **inspeções AST de pureza**.
    **Guarda do corpus real.** O conjunto esperado é **transcrição literal** da tabela
    **`C-A5-M5`** aprovada — **não** é construído lendo nem parseando o corpus. Sobre o corpus
    integrado, a fronteira produz **exatamente 37 tokens**, **37 distintos**, e o conjunto
    **coincide integralmente** com as **37 identidades humanamente aprovadas**.
    **Testes.** **`201 passed`** no direcionado e **`2908 passed`** na suíte completa, **os
    mesmos totais sob `-W error`**, em **Python 3.14.5** — **zero failures, zero errors e zero
    warnings**. Delta **+201** sobre a baseline anterior de **`2707 passed`**; **nenhum teste
    preexistente foi alterado ou removido**. **Não há CI remoto configurado**: `gh pr
    checks 102` reportou **ausência de checks** — **ausência de CI, não falha de CI**.
    **Estado corrente preservado.** **`C-A5` continua MATERIALIZADA no corpus** e **`C-A5-M2`
    continua ATIVA** — efeito já produzido pelo merge da materialização, e **não** por esta
    entrega. **O validador permanente da representação marcada passa a EXISTIR na `main`.**
    Mesmo assim: **C continua ARBITRADA / NÃO MATERIALIZADA**;
    `knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE**; a **bijeção física
    continua NÃO EXECUTADA**; a **autoridade de status continua NÃO MIGRADA** — o Markdown
    continua a autoridade (**C-11**); **`C-A1-ST6`–`C-A1-ST10` continuam NÃO satisfeitas**; e
    continuam **ABERTAS** a propagação de status ao fragmento, o mapeamento concreto de
    `PARCIAL`, a sintaxe de *placeholder*, a gramática de `caminho_yaml`, o formato `hora` e
    **C-7**. **LER A REPRESENTAÇÃO MARCADA NÃO É MATERIALIZAR `C`.**
    **Próxima ação.** **A PRÓXIMA MICROENTREGA FUNCIONAL DE `C` NÃO FOI ESCOLHIDA NESTA
    ENTREGA DOCUMENTAL** — **nenhuma pendência é eleita** por este item, **nenhuma
    implementação é planejada** e **nenhuma subetapa é criada**. Qualquer decisão funcional ou
    arquitetural seguinte será planejada **depois, em entrega separada**.
    **Relação com os itens anteriores.** **Os itens 87, 88 e 89 permanecem corretos como
    registro do momento em que foram escritos** — inclusive quando afirmam que a oitava
    microentrega ainda não havia sido escolhida ou iniciada, o que era verdadeiro naquele
    momento. Este item 90 **não os reescreve**; ele registra o estado **posterior**. O item 89
    recebeu, nesta mesma reconciliação, **apenas** um esclarecimento de **proveniência** da
    sua prova byte-a-byte — **a evidência histórica não foi substituída**.

91. **A NONA MICROENTREGA FUNCIONAL DE `C` — O DERIVADOR DETERMINÍSTICO DOS TOKENS
    CANÔNICOS DO LADO DO ÍNDICE — ESTÁ INTEGRADA À `main` PELO PR #104.**
    **ESTE ITEM 91 É REGISTRO HISTÓRICO DOCUMENTAL. NÃO É "SUBETAPA 91", NÃO É `E11`, NÃO É
    IDENTIFICADOR NORMATIVO DE `C` E NÃO CRIA A 3B.8** — a **3B.8 continua INEXISTENTE**, e a
    **3B.7 continua a última subetapa numerada**. Ele registra **somente** a integração da
    nona microentrega funcional.
    **Integração.** **PR #104** — **commit funcional
    `45876ca609716ede51aefcf8752dd29f98a736a7`** (`feat: add deterministic response index
    token derivation`), **parent único `a057456940ff92c5dae1bf0993538f68518dd66c`**, **merge
    commit `654aaedec2d424ab4184e7a71a0d3c129021abf8`** (merge commit **normal**, dois
    parents: `a057456940…` e `45876ca609…`), branch de origem
    `feat/c-response-index-tokens`, **preservada**. **A `main` passou de
    `a057456940ff92c5dae1bf0993538f68518dd66c` para
    `654aaedec2d424ab4184e7a71a0d3c129021abf8`.**
    **Escopo.** **Dois arquivos novos, e nenhum outro**:
    `src/casa77_sdr/response_index_tokens.py` — **+286 / −0**, blob
    **`84b69472a702a6d436729dbe40a89cf4fcc07bb0`** — e
    `tests/test_response_index_tokens.py` — **+895 / −0**, blob
    **`90bf631403bf2ba7c463348a660f64766f9104aa`**. Total: **2 arquivos, +1181 / −0**.
    **Zero arquivo preexistente alterado**: **zero `docs/**`**, **zero `knowledge/**`**,
    **zero `prompts/**`**, **zero `CLAUDE.md`**, **zero `src/casa77_sdr/__init__.py`**,
    **zero `src/casa77_sdr/response_index.py`** e **zero configuração**.
    **Fronteira entregue.** `derivar_tokens_do_indice(indice: object) -> tuple[str, ...]` e
    `ProjecaoDeIdentidadeInvalida` — **`__all__` com exatamente dois nomes**. A função recebe
    a **estrutura Python já em memória** e devolve **exclusivamente** os tokens canônicos
    `<Rxx>/<id>` de **`C-A5-T1`**, com o separador `/` de **`C-A5-T2`**, na **ordem das listas
    `respostas` e `fragmentos` recebidas** — decisão técnica determinística de saída, **não**
    significado normativo novo de identidade (**`C-A5-I5`**, **`C-A5-M6`**) —, **derivados e
    nunca armazenados** (**`C-A5-T5`**). `{"respostas": []}` devolve `tuple()`, o que **não
    afirma** que o índice real esteja vazio, incompleto ou completo — ele **continua
    INEXISTENTE**.
    **Projeção mínima, e nada além dela.** Raiz é mapeamento; existe `respostas`;
    `respostas` é lista; cada resposta é mapeamento; existe `id`; o `Rxx` é `str` **exata** e
    satisfaz a forma fechada de **C-2b** — `R` + **exatamente dois dígitos ASCII**; o `Rxx` é
    único **globalmente** (**C-2a**); existe `fragmentos`; `fragmentos` é lista **não vazia**
    (**C-2c**); cada fragmento é mapeamento; existe `id`; o `id` é `str` **exata** e satisfaz
    a gramática fechada de **`C-A5-I3`** — `F` + inteiro decimal ASCII maior que zero, **sem
    zero à esquerda**; e o `id` é único **dentro do respectivo `Rxx`** (**`C-A5-I4`**,
    **C-2h**), de modo que `F1` repetido entre `Rxx` distintos é **válido**.
    **`C-A5-I3` aplicada ao `fragmentos[].id` NÃO cria regra nova.** É a gramática já
    arbitrada aplicada ao componente **já designado** por **`C-A5-T3`** — que garante a
    decomposição unívoca **justamente pela forma fechada dos dois componentes** — e por
    **`C-A5-T4`**, que fixa `<Rxx>/<id>` como token dos **dois** domínios de **`C-A1-B3`** /
    **`C-A1-B4`**. `src/casa77_sdr/response_index.py` exige apenas `str` não vazia nesse campo
    e **continua correto no seu próprio escopo**: a forma fechada é requisito **da composição
    do token**, **não** uma correção da validação estrutural.
    **Política de tipo — decisão técnica local.** Contêineres aceitam subclasses — `dict` e
    `list` por `isinstance`, **compatível com `response_index.py`**, **sem** criar regra de
    tipo exato para contêiner. Os **componentes da identidade** exigem `str` **exata**, e
    **subclasse de `str` é recusada**, porque poderia redefinir `__eq__`, `__hash__` ou
    `__str__` e decidir sozinha a identidade ou a composição. Essa recusa é **defesa local
    desta fronteira**: ela **não** altera **C-2**, **não** altera **C-A5**, **não** altera
    `validar_indice` e **não** torna retroativamente inválido nada que `response_index.py`
    aceite.
    **Falhas.** **Categorias técnicas privadas, fechadas e mínimas** — `tipo_invalido`,
    `campo_ausente`, `valor_invalido` e `duplicidade` —, subconjunto deliberado do vocabulário
    já usado por `response_index.py`, **sem taxonomia paralela** e **sem identificador
    normativo novo de `C`**. **Localizadores estruturais fechados e sem posição**: `indice`,
    `respostas`, `respostas.item`, `respostas.item.id`, `respostas.item.fragmentos`,
    `respostas.item.fragmentos.item` e `respostas.item.fragmentos.item.id`. A mensagem tem a
    forma `<categoria>: <localizador>` e **nunca** ecoa o `Rxx`, o `id`, o valor, o conteúdo,
    o `repr`, o tipo concreto, uma posição, um tamanho ou uma cardinalidade. **Fail-closed**:
    a **primeira** violação encerra e **nada é acumulado** (**P5**); a estrutura recebida
    **não é alterada**.
    **Não substitui `validar_indice`.** `status`, `bindings`, `itera_sobre`, *placeholder*,
    `caminho_yaml`, `formato`, `predicado`, mecanismo, origem, fato runtime e chaves
    desconhecidas **não são julgados** aqui — uma estrutura com `status` inválido ou
    `bindings` malformados produz tokens normalmente, e **isso não afirma que ela seja um
    índice válido**. As duas fronteiras são **independentes e complementares**, e o novo
    módulo **não importa nem chama** `response_index`, `response_index_load`,
    `response_bijection` ou `response_markdown_units`.
    **Pureza.** Importa **apenas** `__future__`: **zero I/O**, **zero *filesystem***, **zero
    `pathlib`**, **zero `open`**, **zero YAML**, **zero rede**, **zero LLM**, **zero
    relógio**, **zero calendário**, **zero *locale***, **zero variável de ambiente**, **zero
    banco**, **zero serviço externo**, **zero leitura de `knowledge/**`**, **zero import de
    `casa77_sdr.*`** e **zero export** por `casa77_sdr/__init__.py`.
    **Testes.** **`203 passed`** no direcionado e **`3111 passed`** na suíte completa, **os
    mesmos totais sob `-W error`**, em **Python 3.14.5** — **zero failures, zero errors e zero
    warnings**. Delta **+203** sobre a baseline anterior de **`2908 passed`**; **nenhum teste
    preexistente foi alterado ou removido**. **Não há CI remoto configurado**: `gh pr
    checks 104` reportou **ausência de checks** — **ausência de CI, não falha de CI**.
    **Estado corrente preservado.** **DERIVAR UM DOMÍNIO DE TOKENS NÃO É EXECUTAR A BIJEÇÃO E
    NÃO É MATERIALIZAR `C`.** Esta entrega cria **somente o produtor de um dos dois
    domínios**; ela **não** cria a relação de correspondência, **não** chama
    `validar_bijecao` e **não** executa a bijeção 37/37. Continuam, portanto: **C ARBITRADA /
    NÃO MATERIALIZADA**; `knowledge/indice-respostas-aprovadas.yaml` **INEXISTENTE**; a
    **bijeção física NÃO EXECUTADA**; a **autoridade de status NÃO MIGRADA** — o Markdown
    continua a autoridade (**C-11**); **`C-A1-ST6`–`C-A1-ST10` NÃO satisfeitas**; e **ABERTAS**
    a propagação de status ao fragmento, o mapeamento concreto de `PARCIAL`, a sintaxe de
    *placeholder*, a gramática de `caminho_yaml`, o formato `hora` e **C-7**. **`C-A5`
    continua MATERIALIZADA no corpus** e **`C-A5-M2` continua ATIVA**.
    **Próxima ação.** **A DÉCIMA MICROENTREGA FUNCIONAL DE `C` NÃO É ESCOLHIDA NESTA ENTREGA
    DOCUMENTAL** — **nenhuma pendência é eleita** por este item, **nenhuma arquitetura ou
    decisão técnica nova é criada** e **nenhuma subetapa é criada**.
    **Relação com os itens anteriores.** **Os itens 87 a 90 permanecem corretos como registro
    do momento em que foram escritos.** Este item 91 **não os reescreve**; ele registra o
    estado **posterior**. Em particular, o **item 90** continua correto ao afirmar que, quando
    foi escrito, a próxima microentrega funcional ainda não havia sido escolhida — ela veio a
    ser **esta**, registrada aqui.

92. **A DÉCIMA MICROENTREGA FUNCIONAL DE `C` — A COMPOSIÇÃO DETERMINÍSTICA EM MEMÓRIA DA
    CORRESPONDÊNCIA CANÔNICA — ESTÁ INTEGRADA À `main` PELO PR #106.**
    **ESTE ITEM 92 É REGISTRO HISTÓRICO DOCUMENTAL. NÃO É "SUBETAPA 92", NÃO É `E12`, NÃO É
    IDENTIFICADOR NORMATIVO DE `C` E NÃO CRIA A 3B.8** — a **3B.8 continua INEXISTENTE**, e a
    **3B.7 continua a última subetapa numerada**. Ele registra **somente** a integração da
    décima microentrega funcional.
    **Integração.** **PR #106** — **commit funcional
    `6265b823cb20aab0395840f8125008121de27e43`** (`feat: add deterministic canonical response
    correspondence composition`), **parent único
    `b785822135146c8c70f0b20db7b9eed2f69ccdbe`**, **merge commit
    `457e29a42472d44175d72031cff05ec1a1ebf9d1`** (merge commit **normal**, dois parents:
    `b785822135…` e `6265b823cb…`), branch de origem `feat/c-response-correspondence`,
    **preservada**. **A `main` passou de `b785822135146c8c70f0b20db7b9eed2f69ccdbe` para
    `457e29a42472d44175d72031cff05ec1a1ebf9d1`.**
    **Escopo.** **Dois arquivos novos, e nenhum outro**:
    `src/casa77_sdr/response_correspondence.py` — **+118 / −0**, blob
    **`e3e895246f42a0a5f60c61b7cb68b2a922559134`** — e
    `tests/test_response_correspondence.py` — **+725 / −0**, blob
    **`b4ba305e51dd166596def93a6381209802b23330`**. Total: **2 arquivos, +843 / −0**.
    **Zero arquivo preexistente alterado**: **zero `docs/**`**, **zero `knowledge/**`**,
    **zero `prompts/**`**, **zero `CLAUDE.md`**, **zero `src/casa77_sdr/__init__.py`**, **zero
    `response_bijection.py`**, **zero `response_markdown_units.py`**, **zero
    `response_index_tokens.py`**, **zero `response_index.py`** e **zero configuração**.
    **Fronteira entregue.**
    `validar_correspondencia_canonica(indice: object, texto_markdown: str) -> None`, com
    **`__all__` de exatamente UM nome** e **nenhuma exceção nova**. Ela recebe uma
    **estrutura candidata do índice já em memória** e um **Markdown já em memória**, e julga
    **somente** se os dois denotam **exatamente o mesmo conjunto de identidades canônicas
    `<Rxx>/<id>`**. Não é exportada por `casa77_sdr/__init__.py`.
    **Ordem fixa.** **1.** `derivar_tokens_do_indice(indice)` — o domínio do lado do índice
    (C9); **2.** `ler_unidades_marcadas(texto_markdown)` — o domínio do lado do Markdown
    (C8); **3.** a relação canônica; **4.** `validar_bijecao(...)` — o julgamento (C6),
    chamado **uma única vez**. Nenhuma chamada ao verificador ocorre se o derivador falhar,
    nem se o leitor falhar.
    **A relação é a diagonal da identidade.** Para cada token do domínio do índice é montado
    o par **`(token, token)`**, **na ordem em que o derivador os devolveu**. A correspondência
    é, por construção, **igualdade da identidade canônica**: **nunca** pareamento por
    **posição**, por **ordem**, por **`zip`**, por **conteúdo** ou por **normalização**. Isso
    preserva literalmente **`C-A5-T1`** (identidade `<Rxx>/<id>`), **`C-A5-T2`** (separador
    `/`), **`C-A5-T3`** (composição injetiva e decomposição unívoca, pelas formas fechadas dos
    dois componentes), **`C-A5-T4`** (a mesma identidade é o token dos **dois** domínios
    físicos de **`C-A1-B3`** / **`C-A1-B4`**), **`C-A5-T5`** (token derivado, nunca
    armazenado — a relação **não** é devolvida, armazenada nem persistida) e **`C-A5-I5`**
    (identidade **declarada**, jamais derivada de posição, ordem, índice, redação ou
    conteúdo).
    **Divisão de responsabilidades — a C10 NÃO cria juiz novo.** **C9 continua responsável**
    pelo domínio do índice; **C8 continua responsável** pelo domínio do Markdown; **C6
    continua sendo o único juiz** da bijeção sobre os domínios recebidos. A C10 **somente
    compõe** essas três fronteiras: ela **não** confere tipo de entrada, estrutura do índice,
    estrutura do Markdown, forma de token, duplicidade, cobertura ou cardinalidade — **nada é
    duplicado aqui**.
    **Exceções.** **`ProjecaoDeIdentidadeInvalida`** (índice),
    **`RepresentacaoMarcadaInvalida`** (Markdown) e **`BijecaoInvalida`** (julgamento)
    **propagam intactas**: **zero `try`/`except`**, **zero `raise`**, **zero
    reclassificação**, **zero enriquecimento de mensagem** e **`__cause__`/`__context__`
    inalterados**. **Nenhuma exceção nova foi criada.** Com **ambos** os insumos inválidos, a
    ordem fixa faz o **lado do índice falhar primeiro** — **decisão técnica local de
    determinismo**, **não** norma nova de `C`.
    **Pureza.** Fora `__future__` e as três fronteiras públicas, o módulo **não importa
    nada**: **zero I/O**, **zero *filesystem***, **zero `open`**, **zero `pathlib`**, **zero
    YAML**, **zero rede**, **zero LLM**, **zero relógio**, **zero calendário**, **zero
    *locale***, **zero variável de ambiente**, **zero banco**, **zero cache**, **zero estado
    mutável de módulo** e **zero leitura de `knowledge/**`**. Os **insumos não são
    alterados**, nem no sucesso nem em nenhum dos três caminhos de exceção.
    **Testes.** **`75 passed`** no direcionado e **`3186 passed`** na suíte completa, **os
    mesmos totais sob `-W error`**, em **Python 3.14.5** — **zero failures, zero errors e zero
    warnings**. Baseline pré-implementação **`3111 passed`**; delta **+75**, com
    **`3111 + 75 = 3186`**; **nenhum teste preexistente foi alterado ou removido**. **Não há
    CI remoto configurado**: `gh pr checks 106` reportou **ausência de checks** — **ausência
    de CI, não falha de CI**.
    **Estado corrente preservado.** **COMPOR E VALIDAR EM MEMÓRIA NÃO É EXECUTAR A BIJEÇÃO
    FÍSICA E NÃO É MATERIALIZAR `C`.** O sucesso da C10 afirma **somente** que os **dois
    insumos fornecidos** produziram domínios de identidade cuja relação canônica é **bijetiva
    entre eles**; ele **não** prova a **existência do índice físico**, que a estrutura
    recebida seja o **índice oficial**, que o Markdown recebido seja o **corpus oficial**, a
    **completude** ou a **aprovação** do corpus, a **validade integral do índice** por
    `validar_indice`, a **execução física da bijeção 37/37**, a satisfação de
    **`C-A1-ST6`–`C-A1-ST10`** nem a **migração da autoridade de status**. Continuam,
    portanto: **C ARBITRADA / NÃO MATERIALIZADA**;
    `knowledge/indice-respostas-aprovadas.yaml` **INEXISTENTE**; a **bijeção física do corpus
    real NÃO EXECUTADA**; a **autoridade de status NÃO MIGRADA** — o Markdown continua a
    autoridade (**C-11**); **`C-A1-ST6`–`C-A1-ST10` NÃO satisfeitas**; e **ABERTAS** a
    propagação de status ao fragmento, o mapeamento concreto de `PARCIAL`, a sintaxe de
    *placeholder*, a gramática de `caminho_yaml`, o formato `hora` e **C-7**. **`C-A5`
    continua MATERIALIZADA no corpus** e **`C-A5-M2` continua ATIVA**.
    **Próxima ação.** **A DÉCIMA PRIMEIRA MICROENTREGA FUNCIONAL DE `C` NÃO É ESCOLHIDA NESTA
    ENTREGA DOCUMENTAL** e **NENHUMA C11 FOI INICIADA** — **nenhuma pendência é eleita** por
    este item, **nenhuma arquitetura ou decisão técnica nova é criada** e **nenhuma subetapa é
    criada**.
    **Relação com os itens anteriores.** **Os itens 87 a 91 permanecem corretos como registro
    do momento em que foram escritos.** Este item 92 **não os reescreve**; ele registra o
    estado **posterior**. Em particular, o **item 91** continua correto ao afirmar que, quando
    foi escrito, a décima microentrega ainda não havia sido escolhida — ela veio a ser
    **esta**, registrada aqui.

93. **A PRESENTE ENTREGA É EXCLUSIVAMENTE A MICRO-ARBITRAGEM DOCUMENTAL DA CONVERSÃO DO
    BLOCO MARCADO EM TEXTO CANÔNICO.**
    **ESTE ITEM 93 É DOCUMENTAL. NÃO É "SUBETAPA 93", NÃO É `E11` NEM `E12`, NÃO É
    IDENTIFICADOR NORMATIVO DE `C`, NÃO É MARCO FUNCIONAL E NÃO CRIA A 3B.8** — a **3B.8
    continua INEXISTENTE**, e a **3B.7 continua a última subetapa numerada**. Ele **não é** a
    décima primeira microentrega funcional de `C`.
    **Escopo.** Arquivos alterados: **dois** — `docs/07-arquitetura-motor-respostas.md` e
    `docs/00-estado-atual.md`. **Zero `src/**`**, **zero `tests/**`**, **zero
    `knowledge/**`**, **zero `prompts/**`**, **zero `CLAUDE.md`**, **zero `.gitattributes`** e
    **zero configuração**. **Nenhum marco funcional novo é criado** e **nenhum `pytest` foi
    executado**.
    **Matéria fechada — uma só.** **Como um bloco físico emitível de `C-A5-U1` é convertido
    deterministicamente em uma `str` do domínio canônico `D1`–`D7`, ou recusado
    *fail-closed***. **Nenhuma outra lacuna de `C` é arbitrada aqui.** A convenção adotada é
    **ESTRITA / FAIL-CLOSED**, registrada em `docs/07` no bloco **"Conversão do bloco marcado
    em texto canônico"**, com os rótulos **`MT1`–`MT12`** — **locais daquele bloco**, de
    referência interna, e **declaradamente NÃO** etapa, subetapa, `Exx` ou nomenclatura
    normativa de `C`.
    **Conteúdo da convenção.** **`MT1`**: a fronteira física de **`C-A5-U1` permanece
    literal** — a unidade é a sequência maximal de linhas iniciadas por `>` —, e a convenção
    apenas acrescenta uma validação **semântica posterior**. **`MT2`**: um bloco pode ser
    **estruturalmente reconhecido** e ainda assim **recusado** pelo futuro extrator; isso
    **não** torna o leitor da representação marcada incorreto. **`MT3`**: a linha de conteúdo
    é **exatamente** `>` + **um** espaço ASCII `U+0020` + **conteúdo não vazio**, e o prefixo
    removido é **exatamente `> `**, **dois caracteres** — **proibidos** `lstrip`, `strip`,
    *parser* CommonMark, normalização genérica e tolerância implícita. **`MT4`**: recusados
    *fail-closed* `>` colado ao conteúdo, `>` com dois ou mais espaços, `>` com tab, `> ` com
    tab, `> ` sem conteúdo e qualquer whitespace adicional entre `>` e o conteúdo. **`MT5`**:
    a linha vazia interna é **`>` sozinho**, e **uma** delas entre dois grupos de conteúdo
    projeta **exatamente `\n\n`** (**`D4`**). **`MT6`**: **duas ou mais** linhas `>`
    consecutivas são **recusadas** — não criam parágrafos nem são colapsadas —, porque
    produziriam três ou mais `LF` consecutivos (**`D4`**, **`D7`**). **`MT7`**: linha `>` em
    **borda** — antes da primeira ou depois da última linha de conteúdo — é **recusada**,
    porque a saída não pode começar nem terminar em `LF` (**`D7`**). **`MT8`**: o extrator
    aceita **`LF`** e **`CRLF`** como terminador **físico**, removendo o `CR` **do par** e
    produzindo **somente o `LF` canônico**; **nenhum `CR` permanece na saída**; são recusados
    `CR` isolado, `U+2028`, `U+2029`, `U+0085`, `U+000B`, `U+000C` e qualquer outro terminador
    não autorizado; **proibido** *universal newline* implícito e **proibido** mecanismo cuja
    política varie por ambiente. **`MT9`**: duas linhas de conteúdo consecutivas são o **mesmo
    parágrafo** e projetam **exatamente um `LF`**; o extrator **não** troca esse `LF` por
    espaço — a conversão `LF` → `U+0020` **permanece com `C-15b`** (**`D3`**). **`MT10`**:
    espaço ou tab **imediatamente antes** do terminador é **recusado**, nunca corrigido, e a
    saída deve satisfazer **`D7`**. **`MT11`**: há **dois desfechos** — `str` canônica **não
    vazia** ou **recusa explícita *fail-closed*** —, **nunca** texto parcialmente convertido,
    correção de sintaxe, inferência de intenção, CommonMark como autoridade ou normalização
    arbitrária. **`MT12`**: **taxonomia de exceções, nome de módulo, nome de função,
    assinatura, ordem de parâmetros e mensagem NÃO são decididos** aqui.
    **`D3`, `D4` e `D5` preservadas literalmente.** Elas **não foram reescritas, renumeradas,
    substituídas nem duplicadas em versão concorrente**. Aquele bloco define o **domínio de
    chegada**; esta arbitragem define **somente como se chega nele**. **`D3`** continua sendo
    a convenção de quebra suave, com a conversão para espaço pertencendo à normalização de
    **`C-15b`**; **`D4`** continua fixando `\n\n` como fronteira de parágrafo real e três ou
    mais `LF` como não canônicos; e **`D5`** continua admitindo somente `LF` na representação
    canônica, com `CRLF` não canônico e **o comparador não o convertendo** — a adaptação
    física é do **produtor/extrator**, exatamente onde **`D5`** já a colocava, e é **essa**
    adaptação que **`MT8`** fecha.
    **Leitor da representação marcada inalterado.** `ler_unidades_marcadas`
    (`src/casa77_sdr/response_markdown_units.py`) continua responsável **apenas** por
    reconhecimento estrutural, identidade e tokens canônicos `<Rxx>/<id>`. **Nenhuma alteração
    dele foi autorizada nem feita.** O seu blob permanece
    `3c99d89aa0028f673548f5cc932ec166d592cd7f`.
    **Evidência do corpus — evidência, não norma.** Consulta **read-only** ao blob
    `3bfb2e9fd18bac016e1dbe2c963ff916ceb0c96c`, reverificada mecanicamente: **37** blocos
    emitíveis, **29** multilinha, **73/73** linhas de conteúdo na forma **exata `> `**, **0**
    linha vazia interna `>`, **0** linha vazia em borda, **0** par de linhas vazias
    consecutivas, **0** linha com espaço ou tab antes do terminador, **0** linha fora das duas
    formas admitidas e **0** ocorrência de `CR`, `U+2028`, `U+2029`, `U+0085`, `U+000B` ou
    `U+000C`. Esses fatos **sustentam** que a convenção **não exige alteração do corpus
    atual**, mas **NÃO são a origem normativa da regra**, **NÃO autorizam alteração de
    `knowledge/respostas-aprovadas.md`** — que **não foi alterado** — e **NÃO substituem
    `D1`–`D7`, `C-15` ou `C-A5`**.
    **O que esta arbitragem destrava — e somente isto.** Uma **futura** entrega funcional de
    **extração determinística do conteúdo textual emitível**, que poderá receber a
    representação marcada **já em memória** e produzir texto canônico para `C-15b` **sem
    inventar** regras de prefixo, parágrafo, quebra suave, terminador físico ou recusa de
    sintaxe inválida. **Essa entrega NÃO é implementada aqui e NÃO é escolhida aqui.**
    **Estado corrente preservado.** O **último commit funcional aprovado continua
    `6265b823cb20aab0395840f8125008121de27e43`** e a **baseline funcional continua `3186
    passed`** em **Python 3.14.5** — **nenhuma suíte foi executada nesta entrega**. Continuam:
    **`C` ARBITRADA / NÃO MATERIALIZADA**; **`C-A5` MATERIALIZADA no corpus** e **`C-A5-M2`
    ATIVA**; `knowledge/indice-respostas-aprovadas.yaml` **INEXISTENTE**; a **bijeção física
    NÃO EXECUTADA**; a **autoridade de status NÃO MIGRADA** (**C-11**);
    **`C-A1-ST6`–`C-A1-ST10` NÃO satisfeitas**; e **ABERTAS** a propagação de status ao
    fragmento, o mapeamento concreto de `PARCIAL`, a sintaxe de *placeholder*, a gramática de
    `caminho_yaml`, o formato `hora` e **C-7**. **CONVERTER O BLOCO MARCADO EM TEXTO CANÔNICO
    NÃO É MATERIALIZAR `C`.**
    **Próxima ação.** **A DÉCIMA PRIMEIRA MICROENTREGA FUNCIONAL DE `C` CONTINUA NÃO ESCOLHIDA
    E NÃO INICIADA**, e **não é escolhida por este item**. **Nenhuma pendência é eleita**,
    **nenhum módulo, função, exceção ou mensagem é nomeado** e **nenhuma subetapa é criada**.
    **Relação com os itens anteriores.** **Os itens 87 a 92 permanecem corretos como registro
    do momento em que foram escritos.** Este item 93 **não os reescreve**; ele registra o
    estado **posterior**. Em particular, o **item 92** continua correto ao afirmar que, quando
    foi escrito, a décima primeira microentrega ainda não havia sido escolhida — e ela
    **continua não escolhida** após este item, que é **documental** e **não funcional**.

94. **A DÉCIMA PRIMEIRA MICROENTREGA FUNCIONAL DE `C` — A EXTRAÇÃO DETERMINÍSTICA DO TEXTO
    EMITÍVEL CANÔNICO — ESTÁ INTEGRADA À `main` PELO PR #109.**
    **ESTE ITEM 94 É REGISTRO HISTÓRICO DOCUMENTAL. NÃO É "SUBETAPA 94", NÃO É `E11` NEM
    `E12`, NÃO É IDENTIFICADOR NORMATIVO DE `C` E NÃO CRIA A 3B.8** — a **3B.8 continua
    INEXISTENTE**, e a **3B.7 continua a última subetapa numerada**. Ele registra **somente**
    a integração da décima primeira microentrega funcional, **já integrada** quando este item
    foi escrito.
    **Integração.** **PR #109** — **commit funcional
    `4b6ea8ca00c171275d75ea17c4414011a4f1a835`** (`feat: add deterministic emittable response
    text extraction`), **parent único `690a09c2a594f422b450afc3d780054be2168554`**, **merge
    commit `ceecd638131899974ce43b4685b254bf01d7bbad`** (merge commit **normal**, dois
    parents: `690a09c2a5…` e `4b6ea8ca00…`; **zero squash, zero rebase**), branch de origem
    `feat/c-emittable-text-extraction`, **preservada**. **A `main` passou de
    `690a09c2a594f422b450afc3d780054be2168554` para
    `ceecd638131899974ce43b4685b254bf01d7bbad`.** Merge realizado **sob autorização humana
    explícita**, protegido por `--match-head-commit`.
    **Escopo.** **Dois arquivos novos, e nenhum outro**:
    `src/casa77_sdr/response_emittable_text.py` — **+478 / −0**, blob
    **`ff811210cc59f9c50b7f019d1d6798af9083439f`** — e
    `tests/test_response_emittable_text.py` — **+1253 / −0**, blob
    **`156bbbf86d42e6cd1a3474ed111b12115dec5d0a`**. Total: **2 arquivos, +1731 / −0**.
    **Zero arquivo preexistente alterado**: **zero `docs/**`**, **zero `knowledge/**`**,
    **zero `prompts/**`**, **zero `CLAUDE.md`**, **zero `src/casa77_sdr/__init__.py`**, **zero
    `response_markdown_units.py`** (blob `3c99d89aa0028f673548f5cc932ec166d592cd7f`
    preservado), **zero `response_equivalence.py`** (blob
    `3a0d6fce566fad36a774753e21b40147aede4a5e` preservado), **zero
    `response_correspondence.py`** (blob `e3e895246f42a0a5f60c61b7cb68b2a922559134`
    preservado) e **zero configuração**.
    **Fronteira entregue.**
    `extrair_textos_emitiveis(texto: str) -> tuple[tuple[str, str], ...]`, com
    **`__all__ = ["TextoEmitivelInvalido", "extrair_textos_emitiveis"]`** — exatamente dois
    nomes. `TextoEmitivelInvalido` deriva **diretamente de `Exception`**. **Sem DTO, sem
    dataclass**; **não** é exportada por `casa77_sdr/__init__.py`. Cada elemento do retorno é
    o par **`(token_canonico, texto_canonico)`** — o token `<Rxx>/<id>` **declarado** e o texto
    canônico da unidade —, **em ordem física do documento**. Documento vazio ou sem `Rxx`
    devolve `tuple()`, o que **não afirma nada** sobre o corpus real.
    **C8 primeiro, e juiz estrutural único.** A **primeira** operação funcional é
    `tokens_c8 = ler_unidades_marcadas(texto)`; **nenhum tipo é validado localmente antes
    disso**. Tipo não-`str`, subclasse de `str` e toda violação estrutural de `C-A5`
    **continuam pertencendo a C8**, e `RepresentacaoMarcadaInvalida` **propaga intacta** —
    **zero `try`/`except`**, **zero *wrapper***, **zero reclassificação**, **zero
    enriquecimento**, **`__cause__`/`__context__` inalterados** (a produção não contém nenhum
    nó `Try`/`ExceptHandler`, provado por AST). Com uma violação textual **anterior** e uma
    estrutural **posterior** no mesmo documento, **a estrutural vence**, porque o portão de C8
    é **integral e anterior** — **decisão técnica de composição, não norma nova de `C`**.
    **Localização e invariante C8 ↔ C11.** Só **após** o portão a C11 percorre a `str` para
    **localizar fisicamente as mesmas unidades declaradas**, **derivar de novo o token
    somente do `Rxx` do cabeçalho e do `id` do marcador** (**`C-A5-T1`**, **`C-A5-T2`**,
    **`C-A5-I5`** — **nunca** por posição, índice, ordem, `zip` ou conteúdo; `zip` e `index`
    estão ausentes da produção) e converter cada bloco. A caminhada local **não rejulga
    `C-A5`**. **Antes de devolver qualquer par**, a sequência local de tokens é comparada com
    `tokens_c8`; divergência levanta **`RuntimeError("invariante_estrutural")`** — mensagem
    **muda**, sem token, `Rxx`, `id`, conteúdo, posição ou cardinalidade —, que representa
    **defeito interno de consistência**, **não** entrada textual inválida. Sem `assert`. A
    igualdade **verifica** as duas caminhadas; ela **não atribui identidade por posição**.
    **`MT3`–`MT11` materializadas — a norma de `docs/07` não foi reaberta.** **`MT3`/`MT4`**:
    prefixo de conteúdo **exatamente `> `**, dois caracteres removidos por **fatiamento** —
    **sem `strip`, `lstrip`, `rstrip`, regex permissiva, CommonMark ou normalização** —; `>`
    colado, `>` seguido de dois ou mais espaços, `>` seguido de tab, `> ` seguido de tab e
    `> ` sem conteúdo → **`prefixo_invalido: linha`**. **`MT5`–`MT7`**: a linha vazia interna
    é **`>` sozinho**; **uma** delas entre conteúdo projeta **exatamente `\n\n`**; linha `>`
    na **borda inicial**, na **borda final** ou **duas ou mais consecutivas** →
    **`linha_vazia_invalida: unidade`**, **sem colapsar e sem corrigir**. **`MT8`**: o texto é
    dividido **exclusivamente por `LF`**, preservando por segmento a evidência de **ter sido
    seguido** pelo `LF` — **sem `splitlines()`, sem *universal newline*, sem `StringIO`, sem
    arquivo**; um `CR` terminal pertence a um `CRLF` **somente** quando o segmento termina em
    `\r` **e** foi efetivamente seguido de `\n` — então **aquele único `CR` é removido** e o
    terminador canônico é `LF`; `\r` **sem** `LF` seguinte é **`CR` isolado** e é recusado,
    **inclusive no EOF** — e isso vale **mesmo quando C8 aceitou o bloco estruturalmente**
    pela sua política local de linha (**`MT2`**: estruturalmente reconhecido ≠ textualmente
    válido); `CR` residual (dois `CR` antes de `LF`), `U+2028`, `U+2029`, `U+0085`, `U+000B` e
    `U+000C` → **`terminador_proibido: linha`**; **nenhum `CR` permanece na saída**; **EOF sem
    terminador é válido**; mistura `LF`/`CRLF` entre linhas é aceita. **`MT9`**: linhas
    consecutivas de conteúdo projetam **exatamente um `LF`**, **não convertido em espaço** —
    a conversão `LF` → `U+0020` **continua com `C-15b`** (**`D3`**). **`MT10`**: espaço ou
    tab **imediatamente antes** do terminador → **`branco_antes_do_terminador: linha`**,
    **nunca corrigido**. **`MT11`**: dois desfechos — `str` canônica **não vazia** ou recusa
    **fail-closed**; **nada é devolvido parcialmente**. **Ordem local de falha**, dentro de
    cada unidade e em ordem física: **1.** terminador; **2.** prefixo; **3.** branco terminal;
    **4.** linhas vazias (sobre a unidade inteira); **5.** montagem — a **primeira** violação
    encerra. **Zero `NFC`**: composto e decomposto **permanecem distintos** na saída.
    **Categorias técnicas privadas e fechadas** — **quatro**, e **não** identificadores
    normativos de `C`: `prefixo_invalido`, `linha_vazia_invalida`, `terminador_proibido` e
    `branco_antes_do_terminador`; **localizadores fechados**: `linha` e `unidade`; mensagem
    **`<categoria>: <localizador>`**, **nunca** ecoando conteúdo, token, `Rxx`, `id`,
    caractere ofensor, `repr`, tipo concreto, número de linha, posição, índice, tamanho ou
    cardinalidade. **`MT12` cumprida**: a taxonomia, o nome de módulo, o nome de função, a
    assinatura e as mensagens foram decididos **pelo mandato técnico da C11**, **não** pela
    arbitragem.
    **Fora do domínio, e duplicidade global.** Bloco `>` **fora** de qualquer `## Rxx` está
    fora de **`C-A5-U2`** e é **ignorado integralmente** — sem par e **sem validação `MT`**
    —, preservando a semântica de C8; marcador inválido ou marcador válido fora de `Rxx` **já
    foi recusado por C8** antes da C11. Se C8 aceitar **seções `Rxx` homônimas**, a C11 pode
    devolver **dois pares com o mesmo token**, na ordem física — a unicidade global **não é
    decidida aqui**, e **nenhuma regra nova foi criada**.
    **Pureza.** Importa **apenas** `__future__` e `ler_unidades_marcadas`: **zero I/O**,
    **zero *filesystem***, **zero `open`**, **zero `pathlib`**, **zero YAML**, **zero rede**,
    **zero LLM**, **zero relógio**, **zero calendário**, **zero *locale***, **zero variável de
    ambiente**, **zero banco**, **zero cache**, **zero estado mutável de módulo**, **zero
    `unicodedata`**, **zero import de `response_equivalence` ou `response_correspondence`**.
    A entrada **não é alterada**. Fixtures de teste **sintéticas** — **zero conteúdo real de
    fragmento aprovado, zero dado comercial, zero PII, zero segredo**.
    **Testes.** **`218 passed`** no direcionado e **`3404 passed`** na suíte completa, **os
    mesmos totais sob `-W error`**, em **Python 3.14.5** — **zero failures, zero errors, zero
    warnings**. Baseline pré-implementação **`3186 passed`**; delta **+218**, com
    **`3186 + 218 = 3404`**; **nenhum teste preexistente foi alterado ou removido**. **Ressalva
    ambiental, objetiva e não funcional**: o comando literal `python -m pytest` com o
    **`python` global** não tinha o pacote `casa77_sdr` instalado; os testes canônicos da
    entrega foram executados no **`.venv` do projeto**, também em Python 3.14.5 — **nenhuma
    alteração de ambiente, dependência ou configuração**. **Não há CI remoto configurado**:
    a PR #109 e o merge commit não possuem *statuses*, *check-runs* nem *workflow runs* —
    **AUSÊNCIA DE CI/CHECKS — NÃO FALHA DE CI**.
    **Responsabilidades preservadas — a C11 NÃO:** valida equivalência; aplica `NFC`;
    converte quebra suave em espaço; lê arquivo; lê YAML; lê índice; resolve *binding*;
    resolve status; propaga status; resolve `PARCIAL`; implementa *placeholder*; implementa
    `caminho_yaml`; implementa `hora`; implementa **C-7**; executa a bijeção física;
    materializa `C`; integra *runtime*. **`C-15b` continua no comparador existente**
    (`response_equivalence.py`, **intacto**); **C8 continua estrutural**; **C10 continua a
    composição de domínios de identidade**.
    **Estado corrente preservado.** **EXTRAIR TEXTO CANÔNICO NÃO É VALIDAR EQUIVALÊNCIA, NÃO
    É EXECUTAR A BIJEÇÃO FÍSICA E NÃO É MATERIALIZAR `C`.** O sucesso da C11 afirma **somente**
    que cada bloco declarado do texto recebido satisfaz `MT3`–`MT11` e produziu uma `str` do
    domínio `D1`–`D7`; ele **não** prova que o texto seja o corpus oficial, que o corpus
    esteja completo ou aprovado, que as seções `Rxx` sejam fisicamente únicas, nem afirma
    coisa alguma sobre status, `PARCIAL`, índice real, *bindings*, `ASSERTIVA`, equivalência
    `C-15`, bijeção física ou `C-A1-ST6`–`C-A1-ST10`. Continuam, portanto: **`C` ARBITRADA /
    NÃO MATERIALIZADA**; **`C-A5` MATERIALIZADA no corpus** e **`C-A5-M2` ATIVA**;
    `knowledge/indice-respostas-aprovadas.yaml` **INEXISTENTE**; a **bijeção física do corpus
    real NÃO EXECUTADA**; a **autoridade de status NÃO MIGRADA** — o Markdown continua a
    autoridade (**C-11**); **`C-A1-ST6`–`C-A1-ST10` NÃO satisfeitas** — **a C11 NÃO satisfaz
    `ST10`** e **NÃO migra autoridade**; e **ABERTAS** a propagação de status ao fragmento, o
    mapeamento concreto de `PARCIAL`, a sintaxe de *placeholder*, a gramática de
    `caminho_yaml`, o formato `hora` e **C-7**.
    **Próxima ação.** **C12 NÃO FOI ESCOLHIDA, NÃO FOI PLANEJADA E NÃO FOI INICIADA** —
    **nenhuma pendência é eleita** por este item, **nenhuma arquitetura ou decisão técnica
    nova é criada** e **nenhuma subetapa é criada**.
    **Relação com os itens anteriores.** **Os itens 87 a 93 permanecem corretos como registro
    do momento em que foram escritos.** Este item 94 **não os reescreve**; ele registra o
    estado **posterior**. Em particular, o **item 92** continua correto ao afirmar que, quando
    foi escrito, a décima primeira microentrega ainda não havia sido escolhida, e o **item
    93** continua correto ao registrar a micro-arbitragem **anterior** à C11 — ela veio a ser
    **esta**, registrada aqui.

95. **A PRESENTE ENTREGA É EXCLUSIVAMENTE A MICRO-ARBITRAGEM DOCUMENTAL DA PROPAGAÇÃO DO
    STATUS DE `Rxx` AOS FRAGMENTOS.**
    **ESTE ITEM 95 É DOCUMENTAL. NÃO É "SUBETAPA 95", NÃO É `E11` NEM `E12`, NÃO É
    IDENTIFICADOR NORMATIVO DE `C`, NÃO É MARCO FUNCIONAL E NÃO CRIA A 3B.8** — a **3B.8
    continua INEXISTENTE**, e a **3B.7 continua a última subetapa numerada**. Ele **não é** a
    décima segunda microentrega funcional de `C`.
    **Escopo.** Arquivos alterados: **dois** — `docs/07-arquitetura-motor-respostas.md` e
    `docs/00-estado-atual.md`. **Zero `src/**`**, **zero `tests/**`**, **zero
    `knowledge/**`**, **zero `prompts/**`**, **zero `CLAUDE.md`**, **zero `.gitattributes`** e
    **zero configuração**. **Nenhum marco funcional novo é criado** e **nenhum `pytest` foi
    executado**.
    **Matéria fechada — uma só.** **Como o status de um `Rxx`, uma vez que o seu rótulo já
    tenha sido corretamente identificado, é propagado aos fragmentos emitíveis daquele
    `Rxx`.** **Nenhuma outra lacuna de `C` é arbitrada aqui.** A alternativa adotada é
    **PROPAGAÇÃO UNIFORME / FAIL-CLOSED**, registrada em `docs/07` no bloco **"Propagação do
    status de `Rxx` aos fragmentos"**, inserido **imediatamente após `C-A1-ST`** e **sem
    renumerar nenhuma seção existente**, com os rótulos **`SP1`–`SP7`** — **locais daquele
    bloco**, de referência interna, e **declaradamente NÃO** etapa, subetapa, `Exx` ou
    nomenclatura normativa de `C`.
    **Pré-condição explícita, e limite duro do escopo.** A expressão **"rótulo já corretamente
    identificado"** é **PRÉ-CONDIÇÃO** desta arbitragem, **não** resultado dela. **NENHUMA
    GRAMÁTICA DE CABEÇALHO FOI ARBITRADA**: **como localizar o rótulo na linha física do
    cabeçalho**, **separadores do cabeçalho**, **posição física do rótulo**, **gramática do
    título**, ***parsing* de `## Rxx`** e **algoritmo de extração do rótulo** **NÃO** são
    decididos aqui e **permanecem ABERTOS** como decisão normativa/técnica **futura e
    separada** — **não** atribuída por antecipação a um futuro executor, e **sem** que sequer
    uma "regra mínima" de *parsing* tenha sido arbitrada.
    **Conteúdo da convenção.** **`SP1`**: a regra opera **conceitualmente** sobre um `Rxx`, os
    seus fragmentos emitíveis declarados e um rótulo **já corretamente identificado e
    associado àquele `Rxx`**; ela **não extrai nada do Markdown**, **não analisa Markdown**,
    **não localiza cabeçalho**, **não localiza rótulo** e **não decide de onde o rótulo veio**.
    **`SP2`**: quando o rótulo for **EXATAMENTE** uma das **três** traduções automáticas já
    fechadas por **`C-A1-ST1`**, **`C-A1-ST2`** e **`C-A1-ST3`**, o status canônico
    correspondente é aplicado **uniformemente a TODOS os fragmentos emitíveis daquele `Rxx`**,
    pela tradução **já materializada** por `canonicalizar_status(rotulo: str) -> str`
    (`src/casa77_sdr/response_status.py`, **não alterado**); **nenhuma quarta tradução é
    criada** e o vocabulário de **`C-3`** permanece **fechado**. **`SP3`**: dentro de um `Rxx`
    coberto por `ST1`–`ST3`, **todos** os fragmentos recebem **o mesmo** status canônico
    derivado, sendo **proibido** decidir status por **posição**, **ordem**, **índice**,
    **redação**, **conteúdo**, **quantidade de fragmentos** ou **`id`** — preservando
    literalmente **`C-A5-I5`** e **`C-A5-M6`** —, **sem exceção implícita** e **sem status
    divergente** entre fragmentos do mesmo `Rxx`. **`SP4`**: **`PARCIAL` permanece
    integralmente sujeito a `C-A1-ST4`** — **não** recebe tradução automática, **não** recebe
    propagação automática, **não** vira quarto status e **não** é convertido em `APROVADO`,
    `AGUARDA_APROVACAO` ou `BLOQUEADO` —, de modo que, **enquanto não existir mapeamento
    explícito aprovado no nível dos fragmentos emitíveis**, o status dos fragmentos daquele
    `Rxx` **permanece NÃO RESOLVIDO**, ***fail-closed*** e **sem inferência**. **`SP5`**:
    qualquer rótulo fora das traduções automáticas de `ST1`–`ST3` — **inclusive `PARCIAL`** —
    **não produz status propagado automaticamente**, e a **ausência de tradução não é
    corrigida, normalizada nem inferida**. **`SP6`**: o status propagado é **DERIVADO** da
    autoridade Markdown vigente e **não cria declaração de status adicional** no Markdown de
    cada fragmento — **`C-2d`** preservada, e o Markdown **não alterado** —; o **futuro
    índice** poderá **armazenar status por fragmento** conforme **`C-2i`**, e **isso NÃO
    migra a autoridade**: até **`C-A1-ST6`–`C-A1-ST10`** estarem **integralmente satisfeitas**,
    `knowledge/respostas-aprovadas.md` **continua a autoridade de status** (**`C-11`**).
    **`SP7`**: propagar status **NÃO** cria índice, **NÃO** cria fragmento, **NÃO** altera
    identidade, **NÃO** extrai rótulo, **NÃO** resolve `PARCIAL`, **NÃO** executa a bijeção
    física, **NÃO** satisfaz **`ST6`**, **`ST7`**, **`ST8`** integralmente, **`ST9`** ou
    **`ST10`**, **NÃO** migra a autoridade de status e **NÃO** materializa `C`.
    **Normas preservadas literalmente.** **`C-1`–`C-15`**, **`C-A1-ST`**, **`C-A5`** e
    **`MT1`–`MT12`** **não foram reescritos, renumerados, substituídos nem duplicados em
    versão concorrente**; **`C-3`** continua com **três** status e **sem quarto**; **`C-2d`**
    continua vedando status armazenado no nível do `Rxx`; **`C-2i`** continua exigindo status
    obrigatório no fragmento do **futuro** índice; e **`C-11`** continua colocando a autoridade
    de status em `knowledge/respostas-aprovadas.md`. **`C-A5-X2` fica fechada apenas na sua
    PRIMEIRA metade** — a **propagação** —, permanecendo **ABERTO** o **mapeamento concreto de
    `PARCIAL`**, que era a sua segunda metade; **`C-A5-X3`** e **`C-A5-X4`** permanecem
    **literais e inalteradas**.
    **Corpus.** `knowledge/respostas-aprovadas.md` **não foi alterado** e **não foi usado como
    fundamento normativo**; **nenhuma contagem foi registrada** por esta arbitragem e
    **nenhum conteúdo comercial foi reproduzido**.
    **O que esta arbitragem destrava — e somente isto.** A **semântica** de propagação para
    rótulos **já corretamente identificados**. Ela **NÃO** torna pronta nenhuma entrega
    funcional e **NÃO** escolhe a próxima. Permanecem **ABERTAS**, entre outras: a **extração
    física / gramática do rótulo do cabeçalho**; o **mapeamento concreto de `PARCIAL`**; a
    **sintaxe de *placeholder***; a **gramática de `caminho_yaml`**; o **formato `hora`**;
    **C-7**; o **índice físico**; a **bijeção física**; **`C-A1-ST6`–`C-A1-ST10`**; e a
    **migração da autoridade de status**.
    **Estado corrente preservado.** O **último commit funcional aprovado continua
    `4b6ea8ca00c171275d75ea17c4414011a4f1a835`** — da **C11**, que **continua a última entrega
    funcional** — e a **baseline funcional continua `3404 passed`** em **Python 3.14.5**;
    **nenhuma suíte foi executada nesta entrega**. Continuam: **`C` ARBITRADA / NÃO
    MATERIALIZADA**; **`C-A5` MATERIALIZADA no corpus** e **`C-A5-M2` ATIVA**;
    `knowledge/indice-respostas-aprovadas.yaml` **INEXISTENTE**; a **bijeção física NÃO
    EXECUTADA**; a **autoridade de status NÃO MIGRADA** (**C-11**);
    **`C-A1-ST6`–`C-A1-ST10` NÃO satisfeitas**. **PROPAGAR STATUS NÃO É EXTRAIR RÓTULO, NÃO É
    RESOLVER `PARCIAL`, NÃO É MIGRAR AUTORIDADE E NÃO É MATERIALIZAR `C`.**
    **Próxima ação.** **A DÉCIMA SEGUNDA MICROENTREGA FUNCIONAL DE `C` (C12 FUNCIONAL)
    CONTINUA NÃO ESCOLHIDA, NÃO PLANEJADA E NÃO INICIADA**, e **não é escolhida por este
    item**. **Nenhuma pendência é eleita**, **nenhum módulo, função, exceção ou mensagem é
    nomeado**, **nenhuma implementação é planejada** e **nenhuma subetapa é criada**.
    **Relação com os itens anteriores.** **Os itens 87 a 94 permanecem corretos como registro
    do momento em que foram escritos.** Este item 95 **não os reescreve**; ele registra o
    estado **posterior**. Em particular, o **item 94** continua correto ao registrar a **C11
    funcional integrada** e ao afirmar que, quando foi escrito, a C12 funcional não havia sido
    escolhida — e ela **continua não escolhida** após este item, que é **documental** e **não
    funcional**.

96. **A PRESENTE ENTREGA É EXCLUSIVAMENTE A MICRO-ARBITRAGEM DOCUMENTAL DA GRAMÁTICA FÍSICA
    DO RÓTULO DE STATUS NO CABEÇALHO `Rxx`.**
    **ESTE ITEM 96 É DOCUMENTAL. NÃO É "SUBETAPA 96", NÃO É `E11` NEM `E12`, NÃO É
    IDENTIFICADOR NORMATIVO DE `C`, NÃO É MARCO FUNCIONAL E NÃO CRIA A 3B.8** — a **3B.8
    continua INEXISTENTE**, e a **3B.7 continua a última subetapa numerada**. Ele **não é** a
    décima segunda microentrega funcional de `C`.
    **Escopo.** Arquivos alterados: **dois** — `docs/07-arquitetura-motor-respostas.md` e
    `docs/00-estado-atual.md`. **Zero `src/**`**, **zero `tests/**`**, **zero
    `knowledge/**`**, **zero `prompts/**`**, **zero `CLAUDE.md`**, **zero `.gitattributes`** e
    **zero configuração**. **Nenhum marco funcional novo é criado** e **nenhum `pytest` foi
    executado**.
    **Matéria fechada — uma só.** **Qual é a gramática física determinística do rótulo de
    status em um cabeçalho `Rxx`.** **Nenhuma outra lacuna de `C` é arbitrada aqui**: **não**
    se arbitra propagação — isso é `SP1`–`SP7`, já fechado —, **não** se arbitra `PARCIAL`,
    **não** se cria índice, **não** se decide ordem de chamadas entre módulos e **não** se
    escolhe assinatura ou módulo futuro. A convenção está registrada em `docs/07` no bloco
    **"Gramática física do rótulo de status no cabeçalho `Rxx`"**, inserido **imediatamente
    após o bloco de propagação** e **sem renumerar nenhuma seção existente**, com os rótulos
    **`GR1`–`GR7`** — **locais daquele bloco**, de referência interna, e **declaradamente
    NÃO** etapa, subetapa, `Exx` ou nomenclatura normativa de `C`.
    **Forma física `G2`.** **`## Rxx — <titulo> — <rotulo>`**, com **separador literal de três
    caracteres** `U+0020 U+2014 U+0020` — **SPACE + EM DASH + SPACE**. **`GR2.1`** o separador
    ocorre **exatamente duas vezes**; **`GR2.2`** `<titulo>` é **não vazio**; **`GR2.3`**
    `<rotulo>` é **não vazio**; **`GR2.4`** nem título nem rótulo começam ou terminam com
    **espaço `U+0020`** ou **tab `U+0009`**; **`GR2.5`** **terceira** ocorrência do separador é
    **inválida**; **`GR2.6`** **menos de duas** ocorrências é **inválida**; **`GR2.7`** `-`
    (`U+002D`), `–` (`U+2013`) e qualquer outro caractere semelhante **não** equivalem ao
    separador; **`GR2.8`** espaçamento divergente **não é corrigido**; **`GR2.9`** são
    **proibidos** `strip`, `lstrip`, `rstrip`, normalização, colapso de espaços, inferência e
    tolerância implícita; **`GR2.10`** o rótulo obtido é **literal/opaco** e a gramática **NÃO
    decide pertença a `ST1`–`ST3`**.
    **Demais decisões.** **`GR1`**: a gramática aplica-se **somente** a uma linha que **já
    satisfaça a forma estrutural de cabeçalho `## Rxx`** reconhecida pelas regras vigentes;
    ela **não define ordem de chamadas**, **não decide composição técnica** e **não altera**
    `C8`, `C-A5`, `C-A1-ST` ou `SP1`–`SP7`. **`GR3`**: o rótulo é **literal e opaco** — **zero
    tradução, zero normalização, zero canonicalização, zero inferência** —, e a tradução das
    **três** linhas automáticas de `C-A1-ST1`–`C-A1-ST3` continua em
    `canonicalizar_status(rotulo: str) -> str` (`src/casa77_sdr/response_status.py`, **não
    alterado**). **`GR4`**: forma divergente é **recusada** *fail-closed*, **nunca corrigida**;
    as espécies de impedimento são nomeadas **apenas conceitualmente** — **separador
    ausente**, **cardinalidade de separador diferente de 2**, **segmento vazio** e **branco de
    borda** —, e **nome de exceção, mensagem, módulo, função e assinatura NÃO são definidos**
    aqui. **`GR5`**: o `<titulo>` é **obrigatório para satisfazer a forma física**, **não** é
    produto da futura extração e **não** recebe semântica comercial nova. **`GR6`**: uma
    **futura** fronteira poderá produzir a **associação** entre `Rxx` e `rotulo_literal`, sem
    que nome, assinatura, estrutura de retorno, exceção, mensagem, ordem de chamadas ou
    composição técnica sejam fixados. **`GR7`**: a arbitragem **NÃO** fecha `PARCIAL`, a
    representação física do seu mapeamento, o índice, *bindings*, *placeholder*,
    `caminho_yaml`, `hora`, **C-7**, a bijeção física, `C-A1-ST6`–`C-A1-ST10` ou a migração de
    autoridade.
    **`PARCIAL`.** É **fisicamente extraível pela mesma gramática `G2`** — como qualquer outro
    rótulo — e **isso não muda o seu tratamento**: **não** recebe tradução automática, **não**
    recebe propagação automática, **não** é quarto status, **continua sob `C-A1-ST4`** e **sob
    `SP4`/`SP5`**, e **permanece pendente de mapeamento explícito futuro** no nível dos
    fragmentos emitíveis. **EXTRAIR `PARCIAL` NÃO É RESOLVER `PARCIAL`.**
    **Relação correta com `C-A5-X2`.** Aquela regra registrou **duas** matérias abertas: **1.**
    a **propagação do status**; e **2.** o **mapeamento concreto de `PARCIAL`**. Após
    `SP1`–`SP7`, a **propagação** ficou **fechada semanticamente** e o **mapeamento de
    `PARCIAL` continua ABERTO**. **A gramática física do rótulo é uma lacuna SEPARADA** e não é
    nenhuma das duas: esta entrega **NÃO esgota `C-A5-X2`**, **NÃO fecha "a segunda metade" de
    `C-A5-X2`** e **NÃO resolve `PARCIAL`**. **`C-A5-X2` não é reescrita retroativamente**, e
    **`C-A5-X3`** e **`C-A5-X4`** permanecem **literais e inalteradas**.
    **Relação com `C8`.** A norma diz **somente** que a gramática se aplica a uma linha **já
    estruturalmente reconhecida** como cabeçalho `## Rxx`. **Não** se decide aqui se uma futura
    função chama `ler_unidades_marcadas`, se chama `C8` primeiro, se faz caminhada local, se
    usa composição, se usa invariante, nem qualquer **ordem concreta entre módulos**. **`C8`
    permanece inalterado** — `src/casa77_sdr/response_markdown_units.py` **não foi tocado** —,
    e os seus auxiliares internos de cabeçalho continuam **detalhes técnicos existentes**,
    **não** norma nova.
    **Evidência do corpus — evidência, não norma.** Consulta **estritamente read-only** ao
    blob `3bfb2e9fd18bac016e1dbe2c963ff916ceb0c96c`, **reverificada mecanicamente** e **sem
    reproduzir conteúdo comercial**: **30** cabeçalhos `## Rxx`; **30/30 conformes a `G2`**;
    **0** divergentes; **0** títulos contendo o separador literal; **exatamente 60**
    ocorrências de `U+2014` nos cabeçalhos `Rxx` — **duas por cabeçalho**; **0** ocorrências de
    `U+002D` ou `U+2013` nesses cabeçalhos; e **quatro** rótulos físicos distintos:
    `APROVADO`, `AGUARDA APROVAÇÃO`, `APROVADO com handoff obrigatório` e `PARCIAL`. Esses
    fatos são **EVIDÊNCIA DE COMPATIBILIDADE, NÃO FONTE NORMATIVA**: **não** são a origem da
    regra, **não** autorizam alteração de `knowledge/respostas-aprovadas.md` — **não
    alterado** — e **não** substituem `C-3`, `C-A1-ST`, `C-A5` ou `SP1`–`SP7`. **`G2` não foi
    adaptada ao corpus**: o corpus foi conferido **contra** `G2`.
    **Normas preservadas literalmente.** **`C-1`–`C-15`**, **`C-A1-ST`**, **`C-A5`**,
    **`MT1`–`MT12`** e **`SP1`–`SP7`** **não foram reescritos, renumerados, substituídos nem
    duplicados em versão concorrente**; **`C-3`** continua com **três** status e **sem
    quarto**; **`C-2d`** e **`C-2i`** continuam literais; e **`C-11`** continua colocando a
    autoridade de status em `knowledge/respostas-aprovadas.md`.
    **Estado corrente preservado.** O **último commit funcional aprovado continua
    `4b6ea8ca00c171275d75ea17c4414011a4f1a835`** — da **C11**, que **continua a última entrega
    funcional** — e a **baseline funcional continua `3404 passed`** em **Python 3.14.5**;
    **nenhuma suíte foi executada nesta entrega**. Continuam: **`C` ARBITRADA / NÃO
    MATERIALIZADA**; **`C-A5` MATERIALIZADA no corpus** e **`C-A5-M2` ATIVA**;
    `knowledge/indice-respostas-aprovadas.yaml` **INEXISTENTE**; a **bijeção física NÃO
    EXECUTADA**; a **autoridade de status NÃO MIGRADA** (**C-11**);
    **`C-A1-ST6`–`C-A1-ST10` NÃO satisfeitas**. **ARBITRAR A GRAMÁTICA FÍSICA DO RÓTULO NÃO É
    EXTRAIR O RÓTULO, NÃO É CANONICALIZAR STATUS, NÃO É RESOLVER `PARCIAL`, NÃO É MIGRAR
    AUTORIDADE E NÃO É MATERIALIZAR `C`.**
    **Efeito exato sobre a C12.** **A C12 FUNCIONAL DE EXTRAÇÃO DO RÓTULO PASSA A SER
    PLANEJÁVEL, SUJEITA A PLANEJAMENTO TÉCNICO E AUDITORIA SEPARADOS.** Ela **não** está
    pronta, **não** foi escolhida e **não** foi iniciada; **nenhum módulo, função, exceção ou
    mensagem é nomeado**, **nenhuma implementação é planejada** e **nenhuma subetapa é
    criada**.
    **Relação com os itens anteriores.** **Os itens 87 a 95 permanecem corretos como registro
    do momento em que foram escritos.** Este item 96 **não os reescreve**; ele registra o
    estado **posterior**. Em particular, o **item 95** continua correto ao registrar que a
    **extração física / gramática do rótulo do cabeçalho** estava **ABERTA** quando foi
    escrito — ela vem a ser fechada **aqui**, por este item, que é **documental** e **não
    funcional**.

97. **A DÉCIMA SEGUNDA MICROENTREGA FUNCIONAL DE `C` — A EXTRAÇÃO DETERMINÍSTICA DO RÓTULO
    LITERAL DE STATUS DO CABEÇALHO `Rxx` — ESTÁ INTEGRADA À `main` PELO PR #113.**
    **ESTE ITEM 97 É REGISTRO HISTÓRICO DOCUMENTAL. NÃO É "SUBETAPA 97", NÃO É `E12` NEM
    `E13`, NÃO É IDENTIFICADOR NORMATIVO DE `C`, NÃO É NOVA MICROENTREGA FUNCIONAL E NÃO CRIA
    A 3B.8** — a **3B.8 continua INEXISTENTE**, e a **3B.7 continua a última subetapa
    numerada**. Ele registra **somente** a reconciliação documental pós-merge da décima
    segunda microentrega funcional, **já integrada** quando este item foi escrito.
    **Integração.** **PR #113** — **commit funcional
    `798beb31fd0dc4fed34aa7b20d397abcd2ef8c2b`** (`feat: add deterministic Rxx header label
    extraction`, **sem body, sem trailer**), **parent único
    `6940bf32525c028982838bf27ac3cc067adf3581`**, **merge commit
    `eae7b5098b248cefb42b3a82569fc0575fd6fee0`** (merge commit **normal**, dois parents:
    `6940bf3252…` e `798beb31fd…`; **zero squash, zero rebase, zero auto-merge**), branch de
    origem `feat/c-header-label-extraction`, **preservada**. **A `main` passou de
    `6940bf32525c028982838bf27ac3cc067adf3581` para
    `eae7b5098b248cefb42b3a82569fc0575fd6fee0`.** Merge realizado **sob autorização humana
    explícita**, protegido por `--match-head-commit`; a PR foi aberta **não-draft**, com
    `mergeable = MERGEABLE`, `mergeStateStatus = CLEAN` e `autoMergeRequest = null`.
    **Escopo.** **Dois arquivos novos, e nenhum outro**:
    `src/casa77_sdr/response_header_labels.py` — **+299 / −0**, blob
    **`f8a8e6d6e4a0a03eea4069fd24bcc9eb38b5c06f`** — e
    `tests/test_response_header_labels.py` — **+1532 / −0**, blob
    **`eb097b250c3ecc56597878b951e12bf1afdadc72`**. Total: **2 arquivos, +1831 / −0**.
    **Zero arquivo preexistente alterado**: **zero `docs/**`**, **zero `knowledge/**`**
    (corpus preservado no blob `3bfb2e9fd18bac016e1dbe2c963ff916ceb0c96c`), **zero
    `prompts/**`**, **zero `CLAUDE.md`**, **zero `src/casa77_sdr/__init__.py`**, **zero
    `response_markdown_units.py`** (blob `3c99d89aa0028f673548f5cc932ec166d592cd7f`
    preservado), **zero `response_status.py`** (blob
    `ceeb24cca6356f55e835c9f594a18875fcb1d8db` preservado), **zero
    `response_emittable_text.py`** (blob `ff811210cc59f9c50b7f019d1d6798af9083439f`
    preservado), **zero teste preexistente** e **zero configuração**.
    **Fronteira entregue.** Módulo `casa77_sdr.response_header_labels`;
    `extrair_rotulos_de_cabecalho(texto: str) -> tuple[tuple[str, str], ...]`, com
    **`__all__ = ["CabecalhoRxxInvalido", "extrair_rotulos_de_cabecalho"]`** — exatamente dois
    nomes. `CabecalhoRxxInvalido` deriva **diretamente de `Exception`**. **Sem DTO, sem
    dataclass, sem `Enum`**; **não** é exportada por `casa77_sdr/__init__.py`. Cada elemento
    do retorno é o par **`(Rxx, rotulo_literal)`** de um cabeçalho físico `## Rxx`, **em ordem
    física do documento**; o título **não** aparece na saída. Documento vazio ou sem `Rxx`
    devolve `tuple()`, o que **não afirma nada** sobre o corpus real. **O retorno é `tuple`,
    nunca `dict`**, e **nenhuma unicidade global de `Rxx` é imposta**.
    **C8 primeiro — e exclusivamente como portão estrutural.** A **primeira** operação
    funcional é `ler_unidades_marcadas(texto)`, chamada como **expressão solta**; **nenhum
    tipo é validado localmente antes disso**. Tipo não-`str`, subclasse de `str` e toda
    violação estrutural de `C-A5` **continuam pertencendo a C8**, e
    `RepresentacaoMarcadaInvalida` **propaga intacta** — **zero `try`/`except`**, **zero
    *wrapper***, **zero reclassificação**, **zero enriquecimento**, **`__cause__`/`__context__`
    inalterados** (a produção não contém nenhum nó `Try`/`ExceptHandler`, provado por AST).
    Com uma violação `G2` **anterior** e uma estrutural **posterior** no mesmo documento, **a
    estrutural vence**, porque o portão de C8 é **integral e anterior** — **decisão técnica de
    composição, não norma nova de `C`**.
    **ZERO INVARIANTE LOCAL × C8.** O **resultado de C8 NÃO é armazenado nem comparado**: a
    única chamada ao leitor é um `ast.Expr`, sem `Assign`, `Return` ou argumento; a produção
    **não contém** `set`, `Counter`, `zip`, `sorted`, `RuntimeError` nem a mensagem
    `invariante_estrutural`. A razão é técnica: C8 devolve **somente tokens `<Rxx>/<id>`** e
    **não expõe fronteiras físicas de seção**; com seções homônimas, **nenhum conjunto,
    contagem ou compressão por `Rxx` provaria correspondência 1:1 entre cabeçalhos**. Por isso
    **nenhuma equivalência entre tokens de C8 e cabeçalhos C12 é afirmada** — a caminhada
    local da C12, feita **só depois do sucesso do portão**, é **mínima** e serve **apenas** para
    localizar os cabeçalhos `## Rxx` já pertencentes ao domínio estrutural aceito: `##` na
    **coluna 0**, **exatamente um** espaço, `R`, **exatamente dois dígitos ASCII** e, em
    seguida, espaço ou fim de linha. **Nenhum helper privado de C8 é importado**, **nenhum
    vira API pública** e **C8 não foi modificado**.
    **`G2` materializada — a norma de `docs/07` não foi reaberta.** Forma
    **`## Rxx — <titulo> — <rotulo>`**, separador literal **`U+0020 U+2014 U+0020`** (SPACE +
    EM DASH + SPACE). Aplicada ao trecho que segue `## Rxx`, em ordem fixa: **1.** o separador
    precisa ocorrer **imediatamente após `Rxx`** — sua ausência **nessa posição** é
    **`separador_ausente: cabecalho`**, o que cobre a linha sem separador algum, `-`
    (`U+002D`), `–` (`U+2013`), traço de figura, barra horizontal, traços duplos, `U+00A0`
    em torno do traço e espaçamento divergente (`GR2.7`, `GR2.8`); **2.** o separador precisa
    ocorrer **exatamente duas vezes**, contadas **inclusive quando sobrepostas** — uma linha
    como `A — — B`, decomponível de mais de uma forma, é recusada como
    **`cardinalidade_de_separador: cabecalho`** em vez de resolvida por inferência (`GR2.1`,
    `GR2.5`, `GR2.6`); **3.** título vazio → **`segmento_vazio: titulo`** (`GR2.2`); **4.**
    título com espaço `U+0020` ou tab `U+0009` de borda → **`branco_de_borda: titulo`**
    (`GR2.4`); **5.** rótulo vazio → **`segmento_vazio: rotulo`** (`GR2.3`); **6.** rótulo
    com branco de borda → **`branco_de_borda: rotulo`** (`GR2.4`). **Zero `strip`, `lstrip`,
    `rstrip`, normalização, colapso de espaços, inferência ou tolerância implícita** (`GR2.9`);
    o rótulo é **literal e opaco**, e a fronteira **não decide pertença a `ST1`–`ST3`**
    (`GR2.10`, `GR3`). Fora dessas condições, título e rótulo são **opacos**: conteúdo interno
    que não forme o separador literal — espaços internos, `-`, `–`, EM DASH sem espaço em
    ambos os lados, `U+00A0`, tab interno — é **preservado tal como está**.
    **Categorias técnicas privadas e fechadas** — **quatro**, e **não** identificadores
    normativos de `C`: `separador_ausente`, `cardinalidade_de_separador`, `segmento_vazio` e
    `branco_de_borda`; **localizadores fechados**: `cabecalho`, `titulo` e `rotulo`; **seis
    mensagens alcançáveis**, `<categoria>: <localizador>`, **nunca** ecoando `Rxx`, título,
    rótulo, conteúdo, caractere ofensor, `repr`, tipo concreto, número de linha, posição,
    índice, tamanho ou cardinalidade numérica. **Fail-closed**: os cabeçalhos são percorridos
    em ordem física, a **primeira** violação encerra e **nada é devolvido parcialmente**.
    `GR4` cumprida: nome de exceção, mensagens, módulo, função e assinatura foram decididos
    **pelo mandato técnico da C12**, **não** pela arbitragem.
    **Política de linhas — a estrutural de C8.** Divisão **exclusivamente por `LF`**, com
    remoção de **no máximo um `CR` terminal** por segmento; **sem `splitlines()`** e **sem
    *universal newline***. `LF` e `CRLF` são **estruturalmente equivalentes** e produzem o
    **mesmo resultado**; **`CR` residual** (dois `CR` antes do `LF`) permanece **conteúdo
    literal do rótulo**; `U+2028`, `U+2029`, `U+0085`, `VT` e `FF` permanecem **conteúdo**;
    `U+00A0` **não** é espaço ASCII nem tab e **não** é branco de borda. A política `MT8` da
    C11 **não** foi importada para cabeçalhos. **Nenhum caractere é normalizado.**
    **Homônimos.** Se C8 aceitar duas seções físicas com o mesmo `Rxx`, a C12 devolve **dois
    pares**, na ordem física — **não recusa, não deduplica, não sobrescreve, não usa `dict`**.
    A unicidade global **não pertence a esta fronteira** e **nenhuma regra nova foi criada**.
    **`PARCIAL`.** É **extraído literalmente** por `G2`, como qualquer outro rótulo, e devolvido
    **tal como está** — `("Rxx", "PARCIAL")`. A C12 **não importa `response_status`**, **não
    chama `canonicalizar_status`**, **não traduz**, **não propaga**, **não mapeia** e **não
    resolve** `PARCIAL`, que **continua sob `C-A1-ST4`** e **sob `SP4`/`SP5`**. O teste
    prova, **separadamente e sem tocar a produção**, que `canonicalizar_status("PARCIAL")`
    continua recusando. **EXTRAIR `PARCIAL` NÃO É RESOLVER `PARCIAL`.** O **mapeamento concreto
    de `PARCIAL` permanece ABERTO**.
    **Pureza.** Importa **apenas** `__future__` e `ler_unidades_marcadas`: **zero I/O**,
    **zero *filesystem***, **zero `open`**, **zero `pathlib`**, **zero YAML**, **zero rede**,
    **zero LLM**, **zero relógio**, **zero calendário**, **zero *locale***, **zero variável de
    ambiente**, **zero banco**, **zero cache**, **zero logging**, **zero estado mutável de
    módulo**, **zero `global`/`nonlocal`**, **zero `assert`**, **zero regex**, **zero
    `unicodedata`**, **zero `dict`**, **zero `strip`/`splitlines`**, **zero import de
    `response_status`, `response_emittable_text`, `response_index`, `response_index_tokens`,
    `response_correspondence`, `response_bijection` ou `response_equivalence`**, **zero
    referência a `knowledge/**`** — tudo provado por AST/inspeção. A entrada **não é
    alterada**. Fixtures de teste **sintéticas** — **zero conteúdo real de fragmento aprovado,
    zero dado comercial, zero PII, zero segredo**; os únicos rótulos citados no teste são os
    quatro rótulos físicos já registrados como evidência no item 96.
    **Testes.** **`299 passed`** no direcionado (114 funções de teste, parametrizadas) e
    **`3703 passed`** na suíte completa, **ambos sob `-W error`**, em **Python 3.14.5** —
    **zero failures, zero errors, zero warnings**. Baseline pré-implementação **`3404
    passed`**; delta **+299**, com **`3404 + 299 = 3703`**; **nenhum teste preexistente foi
    alterado ou removido**. Os testes canônicos da entrega foram executados no **`.venv` do
    projeto**, também em Python 3.14.5 — **nenhuma alteração de ambiente, dependência ou
    configuração**; `git diff --check` limpo. **Estes números são evidência da entrega
    funcional C12**; **nenhum `pytest` foi executado nesta reconciliação**. **Não há CI remoto
    configurado**: a PR #113 e o merge commit possuem **zero *statuses***, **zero
    *check-runs*** e **zero *workflow runs*** — **AUSÊNCIA DE CI/CHECKS — NÃO FALHA DE CI**.
    **Responsabilidades preservadas — a C12 NÃO:** canonicaliza status; implementa a
    propagação `SP1`–`SP7`; resolve `PARCIAL`; cria índice; executa a bijeção física; cria
    *bindings*; implementa *placeholder*; implementa `caminho_yaml`; implementa `hora`;
    resolve **C-7**; executa equivalência; renderiza; integra *runtime*; migra autoridade.
    **C8 continua o único juiz estrutural** (intacto); **`canonicalizar_status` continua a
    única tradução das três linhas `C-A1-ST1`–`C-A1-ST3`** (intacto); **C11 continua a
    extração do texto emitível** (intacta).
    **Estado corrente.** **C12 É AGORA A ÚLTIMA ENTREGA FUNCIONAL INTEGRADA.** Commit
    funcional corrente: **`798beb31fd0dc4fed34aa7b20d397abcd2ef8c2b`**; merge:
    **`eae7b5098b248cefb42b3a82569fc0575fd6fee0`**; baseline funcional registrada: **`3703
    passed`** em **Python 3.14.5**. A **C11** — commit `4b6ea8ca00c171275d75ea17c4414011a4f1a835`,
    merge `ceecd638131899974ce43b4685b254bf01d7bbad`, baseline `3404 passed` — passa a
    **histórico anterior**, com o **item 94 preservado** sem reescrita. **EXTRAIR O RÓTULO NÃO
    É CANONICALIZAR STATUS, NÃO É PROPAGAR STATUS, NÃO É RESOLVER `PARCIAL` E NÃO É
    MATERIALIZAR `C`.** O sucesso da C12 afirma **somente** que cada cabeçalho `Rxx` do texto
    recebido satisfaz `G2` e produziu o seu rótulo literal; ele **não** prova que o texto seja
    o corpus oficial, que o corpus esteja completo ou aprovado, que as seções `Rxx` sejam
    fisicamente únicas, nem afirma coisa alguma sobre status canônico, propagação, `PARCIAL`,
    índice real, *bindings*, `ASSERTIVA`, equivalência `C-15`, bijeção física ou
    `C-A1-ST6`–`C-A1-ST10`. Continuam, portanto: **`C` ARBITRADA / NÃO MATERIALIZADA**;
    **`C-A5` MATERIALIZADA no corpus** e **`C-A5-M2` ATIVA**;
    `knowledge/indice-respostas-aprovadas.yaml` **INEXISTENTE**; a **bijeção física do corpus
    real NÃO EXECUTADA**; a **autoridade de status NÃO MIGRADA** — o Markdown continua a
    autoridade (**C-11**); **`C-A1-ST6`–`C-A1-ST10` NÃO satisfeitas**; a **propagação
    `SP1`–`SP7` NÃO IMPLEMENTADA**; **`PARCIAL` NÃO RESOLVIDO**; e **ABERTAS** o mapeamento
    concreto de `PARCIAL`, a sintaxe de *placeholder*, a gramática de `caminho_yaml`, o
    formato `hora` e **C-7**.
    **Próxima ação.** **C13 NÃO FOI ESCOLHIDA, NÃO FOI PLANEJADA E NÃO FOI INICIADA** —
    **nenhuma pendência é eleita** por este item, **nenhuma arquitetura ou decisão técnica
    nova é criada** e **nenhuma subetapa é criada**. A escolha da próxima ação funcional exige
    **planejamento separado**, após a integração desta reconciliação.
    **Relação com os itens anteriores.** **Os itens 87 a 96 permanecem corretos como registro
    do momento em que foram escritos.** Este item 97 **não os reescreve**; ele registra o
    estado **posterior**. Em particular, o **item 94** continua correto ao registrar a C11
    como a última entrega funcional **à época**; o **item 95** continua correto ao registrar
    que a gramática do cabeçalho estava **ABERTA** quando foi escrito; e o **item 96**
    continua correto ao registrar que a C12 funcional era **planejável, não escolhida e não
    iniciada** quando foi escrito — ela veio a ser **esta**, registrada aqui.

98. **A DÉCIMA TERCEIRA MICROENTREGA FUNCIONAL DE `C` — A PROPAGAÇÃO PURA E DETERMINÍSTICA DE
    STATUS `ST1`–`ST3` AOS FRAGMENTOS JÁ ASSOCIADOS — ESTÁ INTEGRADA À `main` PELO PR #115.**
    **ESTE ITEM 98 É REGISTRO HISTÓRICO DOCUMENTAL. NÃO É "SUBETAPA 98", NÃO É `E13` NEM
    `E14`, NÃO É IDENTIFICADOR NORMATIVO DE `C`, NÃO É NOVA MICROENTREGA FUNCIONAL E NÃO CRIA
    A 3B.8** — a **3B.8 continua INEXISTENTE**, e a **3B.7 continua a última subetapa
    numerada**. Ele registra **somente** a reconciliação documental pós-merge da décima
    terceira microentrega funcional, **já integrada** quando este item foi escrito.
    **Integração.** **PR #115** — **commit funcional
    `cbf3e379c9b6697cd502b6a7a0bd3e9bb76c1a27`** (`feat: add deterministic response status
    propagation`, **sem body, sem trailer**), **parent único
    `3329f558e9f46ea21f9eb1067d70902fcc8dec22`**, **merge commit
    `50c1d5e681a11923c443c1f117de5751ea846cdd`** (merge commit **normal**, dois parents:
    `3329f558e9…` e `cbf3e379c9…`; **zero squash, zero rebase, zero auto-merge**), branch de
    origem `feat/c-status-propagation`, **preservada**. **A `main` passou de
    `3329f558e9f46ea21f9eb1067d70902fcc8dec22` para
    `50c1d5e681a11923c443c1f117de5751ea846cdd`.** A PR foi aberta **não-draft**, com
    `mergeable = true` e `mergeable_state = clean`, e **`autoMergeRequest = null`**.
    **Escopo.** **Dois arquivos novos, e nenhum outro**:
    `src/casa77_sdr/response_status_propagation.py` — **+195 / −0**, blob
    **`cb5668efaaa5522a378946e32bb17c032fda78a3`** — e
    `tests/test_response_status_propagation.py` — **+1567 / −0**, blob
    **`24da2fdbfe99ec9e073bcb093254db3b567f866c`**. Total: **2 arquivos, +1762 / −0**.
    **Zero arquivo preexistente alterado**: **zero `docs/**`**, **zero `knowledge/**`**
    (corpus preservado no blob `3bfb2e9fd18bac016e1dbe2c963ff916ceb0c96c`), **zero
    `prompts/**`**, **zero `CLAUDE.md`**, **zero configuração**, **zero
    `src/casa77_sdr/__init__.py`**, **zero `src/casa77_sdr/response_status.py`**, **zero C8**,
    **zero C11**, **zero C12** e **zero teste preexistente**.
    **Contrato.** Módulo `casa77_sdr.response_status_propagation`; fronteira pública única
    **`propagar_status(rotulo: str, fragmentos: Sequence[str]) -> tuple[tuple[str, str],
    ...]`** e exceção **`PropagacaoInvalida`**; **`__all__` com exatamente dois nomes** —
    `["PropagacaoInvalida", "propagar_status"]` —, **sem export no package root**. A exceção
    deriva **diretamente de `Exception`** e **não tem relação de herança com
    `StatusNaoCanonicalizavel`** — nem ancestral, nem descendente. **Saída**: um par
    **`(fragmento_opaco, status_canonico)`** por elemento recebido, **na ordem da entrada**;
    sequência vazia com rótulo válido devolve `tuple()`, o que afirma **somente** que nada foi
    recebido, e **não** que um `Rxx` real possa não ter fragmentos.
    **Natureza pura.** A C13 **NÃO recebe Markdown**, **NÃO chama C8**, **NÃO chama C11**,
    **NÃO chama C12**, **NÃO localiza `Rxx`**, **NÃO localiza cabeçalho ou marcador**, **NÃO
    resolve contenção física**, **NÃO resolve homônimos** e **NÃO compõe nem decompõe
    identidade**. **A ASSOCIAÇÃO CORRETA ENTRE RÓTULO E FRAGMENTOS É PRÉ-CONDIÇÃO DO
    CHAMADOR** (`SP1`): um retorno bem-sucedido **não** prova a origem do rótulo, a existência
    do `Rxx`, o pertencimento dos fragmentos, a completude, a proveniência, a contenção física
    nem a validade da identidade. Importa **apenas** `__future__`,
    `collections.abc.Sequence` e `canonicalizar_status` — **zero I/O**, **zero
    *filesystem***, **zero Markdown**, **zero YAML**, **zero índice**, **zero rede**, **zero
    LLM**, **zero relógio**, **zero calendário**, **zero *locale***, **zero variável de
    ambiente**, **zero banco**, **zero cache**, **zero logging**, **zero estado mutável de
    módulo**, **zero `global`/`nonlocal`**, **zero normalização**, **zero coerção**, **zero
    `dict`**, **zero `zip`**, **zero regex**, **zero `assert`**; a entrada **não é alterada**.
    **Canonicalização.** A **primeira** operação funcional é **`canonicalizar_status(rotulo)`**
    e **nenhuma** validação de `fragmentos` a precede — com rótulo **e** fragmentos inválidos,
    **o rótulo falha primeiro**, decisão técnica local de determinismo, **não** norma nova. A
    tradução continua **exclusivamente** pelas três regras arbitradas — **`ST1`**, **`ST2`** e
    **`ST3`** —, **sem tabela local** e **sem nenhuma quarta tradução**; o sufixo de handoff de
    `ST3` **não é transportado**. **`StatusNaoCanonicalizavel` propaga intacta**: zero
    `try`/`except`, zero *wrapper*, zero reclassificação, zero enriquecimento de mensagem, zero
    `raise from`, `__cause__` e `__context__` **inalterados**.
    **Propagação.** **Todos** os fragmentos fornecidos naquela chamada recebem **o mesmo**
    status canônico. O status **NÃO depende** de posição, ordem, índice, token, `id`,
    conteúdo, quantidade ou redação — a sequência recebida determina **apenas** quais tokens
    aparecem e em que ordem são devolvidos. **`SP3` materializada por construção**, o que
    preserva literalmente **`C-A5-I5`** e **`C-A5-M6`**.
    **Tokens opacos.** Os fragmentos são **`str` opacas**: a C13 **não valida** `Rxx`, `id`, o
    separador `/`, gramática, unicidade, cobertura ou cardinalidade, e **não compõe nem
    decompõe** token algum. **Duplicidades são preservadas** — tokens repetidos produzem pares
    repetidos —, **sem dedup**, **sem `dict`**, **sem `zip`**, **sem agrupamento por `Rxx`** e
    **sem pareamento por posição**.
    **`PropagacaoInvalida`.** **Categoria técnica privada e única**: `tipo_invalido`.
    **Localizadores fechados**: `fragmentos` e `fragmentos.item`. Mensagem
    `<categoria>: <localizador>`, **nunca** ecoando token, rótulo, conteúdo, `repr`, tipo
    concreto, índice, posição, tamanho ou cardinalidade. **Essa exceção julga somente a forma
    mínima do argumento `fragmentos` — ela NÃO julga identidade.** *Fail-closed*: a validação
    percorre **toda** a entrada antes da montagem, e **nada é devolvido parcialmente**.
    **`PARCIAL`.** **Continua NÃO RESOLVIDO.** `canonicalizar_status` continua recusando-o, e
    a C13 **não captura**, **não traduz**, **não propaga**, **não mapeia** e **não converte**.
    A recusa por `StatusNaoCanonicalizavel` é **somente daquela invocação** — a fronteira
    **não conhece documento algum**, e **nenhuma política de documento inteiro é registrada
    aqui**.
    **Testes.** **Baseline anterior `3703 passed`**; **direcionado da C13 `397 passed`**;
    **regressão completa `4100 passed`** — delta **+397**, **`3703 + 397 = 4100`** —, em
    **Python 3.14.5**, sob **`-W error`**, com **zero failures, zero errors e zero warnings**
    e **nenhum teste preexistente alterado ou removido**. **Estes números são evidência da
    ENTREGA FUNCIONAL C13, e NÃO desta reconciliação: NENHUM `pytest` FOI EXECUTADO AQUI**,
    porque **zero código, zero teste e zero `knowledge/**` mudaram**.
    **Checks.** A PR #115 possui **zero *combined statuses*** e **zero *workflow runs***, e o
    merge commit `50c1d5e681a11923c443c1f117de5751ea846cdd` **também não possui CI ou
    checks** — **AUSÊNCIA DE CI/CHECKS — NÃO FALHA DE CI**. Nenhum CI foi criado por esta
    reconciliação.
    **Limites após a C13.** **`C` continua ARBITRADA / NÃO MATERIALIZADA**; o **índice físico
    continua INEXISTENTE**; a **bijeção física continua NÃO EXECUTADA**; a **autoridade de
    status continua NÃO MIGRADA** (**C-11**); **`C-A1-ST6`–`C-A1-ST10` continuam NÃO
    satisfeitas**; a **composição documental de C13 com C8/C12 continua NÃO IMPLEMENTADA**; e
    continuam **ABERTOS** o mapeamento concreto de `PARCIAL`, a sintaxe de *placeholder*, a
    gramática de `caminho_yaml`, o formato `hora` e **C-7**. A **3B.8 continua INEXISTENTE**.
    **PROPAGAR STATUS NÃO É LER MARKDOWN, NÃO É COMPOR C8/C11/C12, NÃO É RESOLVER `PARCIAL` E
    NÃO É MATERIALIZAR `C`.**
    **Última entrega funcional.** **A C13 É AGORA A ÚLTIMA ENTREGA FUNCIONAL INTEGRADA**, com
    **commit funcional corrente `cbf3e379c9b6697cd502b6a7a0bd3e9bb76c1a27`** e **baseline
    `4100 passed` em Python 3.14.5**. A **C12 passa a histórico imediatamente anterior**, com
    o seu registro **preservado**.
    **C14.** **C14 NÃO FOI ESCOLHIDA, NÃO FOI PLANEJADA E NÃO FOI INICIADA.** **Nenhuma
    pendência é eleita aqui** — nem `PARCIAL`, nem a composição documental, nem o índice, nem
    a bijeção, nem qualquer outro residual —, **nenhuma nomenclatura nova é criada** e
    **nenhuma subetapa é criada**. A escolha da próxima ação funcional exige **planejamento
    separado**, após a integração desta reconciliação.
    **Relação com os itens anteriores.** **Os itens 87 a 97 permanecem corretos como registro
    do momento em que foram escritos.** Este item 98 **não os reescreve**; ele registra o
    estado **posterior**. Em particular, o **item 97** continua correto ao registrar a C12
    como a última entrega funcional **à época** e ao registrar que a C13 **não havia sido
    escolhida, planejada ou iniciada** quando foi escrito — ela veio a ser **esta**, registrada
    aqui.

99. **A PRESENTE ENTREGA É EXCLUSIVAMENTE A MICRO-ARBITRAGEM DOCUMENTAL DO MAPEAMENTO FÍSICO
    DE STATUS POR FRAGMENTO SOB `PARCIAL`.**
    **ESTE ITEM 99 É REGISTRO HISTÓRICO DOCUMENTAL. NÃO É "SUBETAPA 99", NÃO É `E14`, NÃO É
    IDENTIFICADOR NORMATIVO DE `C`, NÃO É MICROENTREGA FUNCIONAL E NÃO CRIA A 3B.8** — a
    **3B.8 continua INEXISTENTE**, e a **3B.7 continua a última subetapa numerada**. Ele
    registra **somente** esta micro-arbitragem documental.
    **Escopo.** **Dois arquivos documentais, e nenhum outro**:
    `docs/07-arquitetura-motor-respostas.md` — novo bloco **"Mapeamento físico de status por
    fragmento sob `PARCIAL`"**, inserido **imediatamente após** o bloco da gramática física
    `G2` do cabeçalho `Rxx` — e este documento. **Zero `src/**`**, **zero `tests/**`**, **zero
    `knowledge/**`** (corpus preservado no blob
    `3bfb2e9fd18bac016e1dbe2c963ff916ceb0c96c`), **zero `prompts/**`**, **zero `CLAUDE.md`**,
    **zero configuração**. **Nenhum `pytest` foi executado**, porque **zero código e zero teste
    mudaram**.
    **Rótulos locais.** **`PM1`**–**`PM12`** são **locais daquele bloco**, existem só para
    referência interna e **não** são etapa, subetapa, `Exx` nem nomenclatura normativa de `C`;
    eles **não criam a 3B.8**. Nenhum módulo, função, assinatura, exceção ou mensagem é
    decidido — isso pertence a **futura materialização técnica**.
    **Forma física arbitrada.** A declaração é a **linha física própria**
    `<!-- status-fragmento: <valor> -->`, imediatamente **acima** do marcador `C-A5`
    `<!-- fragmento: <id> -->`, que continua imediatamente acima da primeira linha do bloco de
    citação. Envelope **EXATO** — prefixo `<!-- status-fragmento: `, `<valor>`, sufixo ` -->`
    —, **nada antes e nada depois**, **zero `strip`**, **zero normalização**, **zero tolerância
    implícita** (`PM1`); **zero linha física** entre declaração e marcador, e a declaração
    **nunca** entre marcador e bloco (`PM2`) — **`C-A5-I1`** e **`C-A5-I2`** preservados
    **literalmente**.
    **Associação, não identidade.** A declaração associa-se ao marcador válido da linha
    seguinte por **adjacência estrutural status → marcador** (`PM3`). Isso **NÃO** é
    identidade, **NÃO** é parte do token, **NÃO** é parte do `id` e **NÃO** é posição usada
    para **definir** identidade — **`C-A5-I5`** permanece **intacto**. A identidade continua
    **exclusivamente** `<Rxx>/<id>` (**`C-A5-T1`**, **`C-A5-T2`**), e a declaração **não
    contém, não duplica, não cria e não altera `id`**.
    **Vocabulário — decisão `V1`, status canônico direto** (`PM4`). `<valor>` é **EXATAMENTE
    UM** dos **três** valores de **`C-3`**: `APROVADO`, `AGUARDA_APROVACAO` ou `BLOQUEADO`.
    **Sem quarto valor**; **`PARCIAL` é INVÁLIDO como valor**. Os rótulos físicos de
    `ST1`–`ST3` **não** são usados nesse campo, **`canonicalizar_status` NÃO é chamado** e
    **nenhuma tabela de tradução é criada** — o campo já carrega o status canônico. Comparação
    futura **literal**, com **tipo e forma fechados**: **zero `strip`**, **zero caixa**, **zero
    `NFC`**, **zero coerção**. **`BLOQUEADO` é representável por fragmento**, o que **não** o
    torna, por si só, `E09` nem `pendencia_impeditiva` — **C-12** permanece literal, e o
    consumo pertence a **S2-D8**, que **continua ABERTA**.
    **Cardinalidade e *fail-closed*.** Sob cabeçalho `G2` rotulado `PARCIAL`, **cada**
    fragmento emitível tem **EXATAMENTE UMA** declaração válida (`PM5`): **nenhuma** é
    *fail-closed*, **duas ou mais** são *fail-closed*, **sem inferência** e **sem valor
    padrão** — preservando `C-3`, para o qual **fragmento sem status é erro de contrato, nunca
    `APROVADO` implícito**. São **conceitualmente inválidos** (`PM6`): declaração ausente,
    órfã, múltipla, fora de seção `Rxx`, sem marcador válido imediatamente seguinte, com linha
    em branco intercalada, com valor fora de `C-3`, com `PARCIAL` como valor, com *whitespace*
    divergente, com conteúdo adicional, ou com envelope divergente que deixe o marcador sem a
    declaração obrigatória. **Quase-declaração**: uma linha que **não** satisfaça o envelope
    exato **permanece conteúdo comum** — o mesmo padrão de `C-A5`/`C8` —, mas, se disso
    resultar marcador **sem** a declaração obrigatória, **`PM5` falha por declaração
    ausente**, e **nenhuma intenção é inferida**.
    **Proibição sob `ST1`–`ST3`** (`PM7`). Sob rótulo pertencente a `C-A1-ST1`, `C-A1-ST2` ou
    `C-A1-ST3`, a declaração é **PROIBIDA**, **mesmo** quando o valor explícito coincidiria com
    o status propagado: `SP2`/`SP3` já definem **propagação uniforme**, e admitir a declaração
    criaria **duas fontes concorrentes ou redundantes** dentro da autoridade Markdown,
    comprometendo **`SP6`**. Forma divergente é *fail-closed*.
    **Autoridade e não emissão.** A declaração vive na **autoridade Markdown vigente** e é a
    **fonte explícita** do status do fragmento sob `PARCIAL` (`PM8`); o **futuro índice**
    poderá armazená-la **por fragmento** conforme **`C-2i`**, e **isso NÃO migra autoridade** —
    até `C-A1-ST6`–`C-A1-ST10` integralmente satisfeitas, `knowledge/respostas-aprovadas.md`
    **continua a autoridade de status** (**C-11**). `status-fragmento` **NÃO** é fragmento
    emitível, **NÃO** é nota comercial, **NÃO** é instrução emitível, **NÃO** recebe *binding*,
    **NÃO** recebe `ASSERTIVA`, **NÃO** pode ser emitido ao interessado e **NÃO** entra na
    bijeção (`PM9`) — **`C-2m`–`C-2p`** e **`C-A5-U4`** preservados.
    **Política de linha** (`PM10`). Reutiliza **integralmente** a política estrutural de
    `C8`/`C12`: divisão **exclusivamente por `LF`**, **no máximo um `CR` terminal** removido por
    segmento, **sem `splitlines()`**, **sem *universal newline***. **Nenhuma terceira política
    é criada**, e o envelope precisa **permanecer literal**.
    **Significado físico de `PARCIAL`** (`PM11`). **No Markdown vigente, o rótulo físico
    `PARCIAL` ativa o regime de STATUS EXPLICITAMENTE DECLARADO POR FRAGMENTO**: **não**
    aplicar propagação automática do cabeçalho; **exigir** uma declaração para **cada**
    fragmento; e **resolver cada fragmento individualmente** por valor de `C-3` explícito.
    `PARCIAL` **NÃO** é status canônico, **NÃO** é armazenado no `Rxx` do índice, **NÃO** é
    armazenado no fragmento, **NÃO** é convertido em quarto status, **NÃO** exige dois ou mais
    status distintos, **NÃO** exige mistura de status e **NÃO** exige cardinalidade mínima de
    dois fragmentos: uma seção rotulada `PARCIAL` pode ter **um** fragmento ou **vários**,
    **todos com o mesmo status** ou **com status distintos**. **ISSO NÃO DEFINE UMA FUNÇÃO
    GERAL DE AGREGAÇÃO DE STATUS DE `Rxx`, E NENHUMA FUNÇÃO AGREGADORA GERAL FOI CRIADA.**
    **Relação com `C-3`.** **`C-3` permanece literal e não é reescrita.** O `Rxx` **continua
    sem status armazenado** (**C-2d**); **`PARCIAL` nunca é valor armazenado**; e os **únicos
    status armazenáveis pertencem aos fragmentos** e são os três de `C-3` (**C-2i**). **Nenhum
    campo de "status agregado do `Rxx`" é criado ou definido.** O rótulo físico, histórico e de
    Markdown `PARCIAL` é **o sinal de que aquela seção exige status explícito por fragmento**,
    conforme **`C-A1-ST4`** — e **não** o resultado de uma nova função computacional de
    agregação.
    **`C-A1-P2` preservada.** Nota interna **não** é fragmento, **não** recebe status, **não**
    bloqueia automaticamente fragmento e **não** determina automaticamente o valor da
    declaração. **Nada é inferido** — nem `APROVADO`, nem `AGUARDA_APROVACAO`, nem `BLOQUEADO`
    — a partir de nota interna, de `null`, de conteúdo, de posição ou de contexto.
    **Evidência estrutural — EVIDÊNCIA NÃO É NORMA.** Consulta **estritamente read-only** ao
    blob `3bfb2e9fd18bac016e1dbe2c963ff916ceb0c96c`, **sem reproduzir conteúdo comercial**:
    **30** cabeçalhos `## Rxx`; **exatamente 1** com rótulo físico `PARCIAL` — o **`R28`**, já
    citado por `C-A1-P2` —, contendo **exatamente 1** marcador `C-A5`; **37** marcadores
    `C-A5` no total, **37/37** imediatamente seguidos pela primeira linha do bloco, **sem linha
    em branco**; e **0** ocorrências de `status-fragmento` em todo o corpus — os **37**
    comentários HTML existentes são **exatamente** os 37 marcadores, de modo que o portador de
    `PM1` **não colide com nada existente**. Esses fatos **sustentam compatibilidade
    estrutural**, mas **NÃO** são a origem da regra, **NÃO** autorizam alteração de
    `knowledge/respostas-aprovadas.md` — que **não foi alterado** — e **NÃO** substituem `C-3`,
    `C-A1-ST`, `C-A1-P`, `C-A5`, `SP1`–`SP7` ou `GR1`–`GR7`. **NENHUM STATUS REAL FOI ATRIBUÍDO
    AO `R28` NEM A QUALQUER OUTRO FRAGMENTO.**
    **Norma estrutural × corpus real.** A **norma estrutural** fica **FECHADA** quanto a
    portador, posição, associação, vocabulário, cardinalidade, *fail-closed*, proibição sob
    `ST1`–`ST3` e significado físico de `PARCIAL`. O **corpus real continua NÃO RESOLVIDO**:
    **nenhum status real de fragmento é atribuído por esta entrega**. Portanto, **`PARCIAL`
    CONTINUA NÃO RESOLVIDO NO CORPUS ATÉ APLICAÇÃO HUMANA EXPLÍCITA DOS STATUS POR
    FRAGMENTO**, e a **composição documental com `C8`/`C12`/`C13` continua NÃO IMPLEMENTADA**.
    **Limites** (`PM12`). Esta arbitragem **NÃO** atribui status real, **NÃO** altera
    `knowledge/**`, **NÃO** altera `C8`, `C11`, `C12` ou `C13`, **NÃO** implementa *parser*,
    **NÃO** implementa a próxima entrega funcional, **NÃO** cria índice, **NÃO** executa a
    bijeção física, **NÃO** satisfaz `C-A1-ST6`–`C-A1-ST10`, **NÃO** migra autoridade, **NÃO**
    resolve *binding*, *placeholder*, `caminho_yaml` ou **C-7**, **NÃO** cria a **3B.8** e
    **NÃO** materializa `C`. **ARBITRAR A REPRESENTAÇÃO FÍSICA DO STATUS POR FRAGMENTO NÃO É
    ATRIBUIR STATUS, NÃO É ALTERAR O CORPUS, NÃO É IMPLEMENTAR PARSER, NÃO É RESOLVER `PARCIAL`
    E NÃO É MATERIALIZAR `C`.**
    **Marco funcional inalterado.** **A C13 CONTINUA A ÚLTIMA ENTREGA FUNCIONAL INTEGRADA** —
    **commit funcional `cbf3e379c9b6697cd502b6a7a0bd3e9bb76c1a27`**, **merge
    `50c1d5e681a11923c443c1f117de5751ea846cdd`** —, com **baseline `4100 passed`** em **Python
    3.14.5**. Esta entrega **não cria marco funcional** e **não recebe numeração de subetapa**.
    **C14.** **C14 NÃO FOI ESCOLHIDA, NÃO FOI PLANEJADA E NÃO FOI INICIADA.** **Nenhuma
    pendência é eleita aqui**, **nenhuma nomenclatura nova é criada** e **nenhuma subetapa é
    criada**. A escolha da próxima ação funcional exige **planejamento separado**, após a
    integração desta entrega.
    **Relação com os itens anteriores.** **Os itens 87 a 98 permanecem corretos como registro
    do momento em que foram escritos.** Este item 99 **não os reescreve**; ele registra o
    estado **posterior**. Em particular, o **item 98** continua correto ao registrar a C13 como
    a última entrega funcional — **ela continua sendo** —, e o **item 97** continua correto ao
    registrar que a **representação física do mapeamento de `PARCIAL` estava ABERTA** quando foi
    escrito: é **esta** entrega que a fecha **estruturalmente**, **sem** resolvê-la no corpus.

100. **A PRESENTE ENTREGA É EXCLUSIVAMENTE O REGISTRO DA DECISÃO HUMANA DE STATUS
     `R28/F1 = APROVADO`.**
     **ESTE ITEM 100 É REGISTRO HISTÓRICO DOCUMENTAL. NÃO É "SUBETAPA 100", NÃO É `E14`, NÃO É
     IDENTIFICADOR NORMATIVO DE `C`, NÃO É MICROENTREGA FUNCIONAL E NÃO CRIA A 3B.8** — a
     **3B.8 continua INEXISTENTE**, e a **3B.7 continua a última subetapa numerada**. Ele
     registra **exclusivamente** a decisão humana `R28/F1 = APROVADO`, **aprovada e ainda não
     aplicada**.
     **Escopo.** **Dois arquivos documentais, e nenhum outro**:
     `docs/07-arquitetura-motor-respostas.md` — **registro posterior**, claramente separado,
     dentro do bloco **"Mapeamento físico de status por fragmento sob `PARCIAL`"** — e este
     documento. **Zero `src/**`**, **zero `tests/**`**, **zero `knowledge/**`**, **zero
     `prompts/**`**, **zero `CLAUDE.md`**, **zero configuração**. **Nenhum `pytest` foi
     executado**, porque **zero código e zero teste mudaram**.
     **`PM1`–`PM12` inalteradas.** O registro **NÃO** cria `PM13`, **NÃO** renumera, **NÃO**
     reinterpreta e **NÃO** altera nenhuma das doze regras, que permanecem **literais**. Ele
     também **não** altera `C-3`, `C-A1-P2`, `C-A1-ST`, `C-A5`, `SP1`–`SP7` ou `GR1`–`GR7`.
     **A decisão.** **Existe decisão humana explícita** de que o status canônico do fragmento
     emitível **`R28/F1`** é **`APROVADO`**. O valor pertence ao **vocabulário fechado de
     `C-3`** (`C-3a`). A identidade `R28/F1` é a identidade canônica de `C-A5-T1` / `C-A5-T2`
     — conferida **estruturalmente e read-only** no blob
     `3bfb2e9fd18bac016e1dbe2c963ff916ceb0c96c`: a seção `## R28` existe, o seu rótulo físico
     de cabeçalho é `PARCIAL` e ela contém **exatamente 1** marcador `C-A5`, de `id` `F1`.
     **Nenhuma inferência foi utilizada.** A decisão é **humana e deliberada**: **NÃO** foi
     inferida de nota interna, **NÃO** foi inferida de `null`, **NÃO** foi inferida de
     conteúdo, **NÃO** foi inferida do rótulo físico `PARCIAL` do cabeçalho, **NÃO** foi
     inferida de posição ou contexto e **NÃO** foi escolhida por ferramenta ou modelo algum —
     exatamente o que **`C-A1-P2`** e **`PM11`** exigem: sob `PARCIAL`, o status é **declarado
     por ato humano explícito**, nunca derivado.
     **Aprovada, ainda NÃO aplicada.** `knowledge/respostas-aprovadas.md` **NÃO foi alterado**
     e permanece **byte-a-byte** no blob `3bfb2e9fd18bac016e1dbe2c963ff916ceb0c96c`; **nenhuma
     linha `<!-- status-fragmento: APROVADO -->` foi inserida**; **nenhum cabeçalho, fragmento
     ou nota foi alterado**; e o corpus continua com **0** ocorrências de `status-fragmento`.
     **Enquanto não aplicada, o corpus continua mecanicamente sem a declaração obrigatória de
     `PM5`** para aquele fragmento: uma verificação estrutural de `PM5` sobre o corpus atual
     **falharia por declaração ausente**, e isso é o **comportamento correto** — **DECIDIR NÃO
     É APLICAR**.
     **Forma futura decorrente da decisão.** A aplicação física, quando executada por **entrega
     própria**, deverá usar **exatamente** `<!-- status-fragmento: APROVADO -->`,
     **imediatamente antes** do marcador `C-A5` de `R28/F1`, com **zero linha física** entre
     ambos (`PM1`, `PM2`). **Essa linha é SOMENTE a forma futura decorrente da decisão, e NÃO
     uma alteração executada nesta entrega.**
     **Significado estrito.** `APROVADO` significa **somente** o **status canônico de `C-3` do
     fragmento emitível `R28/F1`**. A decisão **NÃO** resolve nota interna, **NÃO** altera
     `null`, **NÃO** aprova dado comercial, **NÃO** elimina handoff, **NÃO** autoriza emissão
     sem as demais validações, **NÃO** decide **S2-D8**, **NÃO** cria `E09`, **NÃO** elimina
     `E09`, **NÃO** resolve *binding*, **NÃO** resolve `ASSERTIVA`, **NÃO** resolve **C-8** e
     **NÃO** satisfaz **`C-A1-ST8`** isoladamente — `C-A1-ST8` exige o status de **todos** os
     fragmentos resolvidos, e **`C-A4-G8`** continua valendo: **cobertura estrutural não é
     emissibilidade**.
     **Precisão sobre a pendência de `PARCIAL`.** **Antes** desta entrega: **status humano não
     decidido e não aplicado**. **Depois** desta entrega: **status humano DECIDIDO
     (`APROVADO`), com a declaração `PM` AINDA NÃO APLICADA ao corpus**. Portanto **o corpus
     continua estruturalmente NÃO RESOLVIDO até a aplicação física da declaração**.
     **Marco funcional inalterado.** **A C13 continua a última entrega funcional integrada** —
     **commit funcional `cbf3e379c9b6697cd502b6a7a0bd3e9bb76c1a27`**, **merge
     `50c1d5e681a11923c443c1f117de5751ea846cdd`** —, com **baseline `4100 passed`** em **Python
     3.14.5**. Esta entrega **não cria marco funcional** e **não recebe numeração de subetapa**.
     **`C` continua ARBITRADA / NÃO MATERIALIZADA**; o **índice físico continua INEXISTENTE**;
     a **bijeção física continua NÃO EXECUTADA**; a **autoridade de status continua NÃO
     MIGRADA** (**C-11**); e **`C-A1-ST6`–`C-A1-ST10` continuam NÃO satisfeitas**.
     **C14.** **C14 NÃO FOI INICIADA.** Esta entrega **não planeja C14**, **não implementa
     C14**, **não escolhe assinatura**, **não cria módulo** e **não cria teste**. Nenhuma
     pendência é eleita aqui, e a escolha da próxima ação funcional exige **planejamento
     separado**.
     **Relação com os itens anteriores.** **Os itens 87 a 99 permanecem corretos como registro
     do momento em que foram escritos.** Este item 100 **não os reescreve**; ele registra o
     estado **posterior**. Em particular, o **item 99** continua correto ao registrar que
     **nenhum status real havia sido atribuído** quando foi escrito, e ao registrar que a
     resolução do corpus dependeria de **aplicação humana explícita**: esta entrega é a
     **decisão** humana, e **não** a sua aplicação.

101. **A PRESENTE ENTREGA É EXCLUSIVAMENTE O FECHAMENTO DA LACUNA NORMATIVA PRÉ-C14 — O
     REGIME EXCLUSIVO DE `status-fragmento` SOB `PARCIAL`.**
     **ESTE ITEM 101 É REGISTRO HISTÓRICO DOCUMENTAL. NÃO É "SUBETAPA 101", NÃO É `E14`, NÃO É
     IDENTIFICADOR NORMATIVO DE `C`, NÃO É MICROENTREGA FUNCIONAL E NÃO CRIA A 3B.8** — a
     **3B.8 continua INEXISTENTE**, e a **3B.7 continua a última subetapa numerada**. Ele
     registra **somente** o fechamento desta lacuna pré-C14.
     **Escopo.** **Dois arquivos documentais, e nenhum outro**:
     `docs/07-arquitetura-motor-respostas.md` — **registro posterior**, claramente separado, no
     bloco **"Regime exclusivo de `status-fragmento` sob `PARCIAL`"**, escrito **depois** de
     `PM1`–`PM12` e do registro da decisão humana de `R28/F1` — e este documento. **Zero
     `src/**`**, **zero `tests/**`**, **zero `knowledge/**`**, **zero `prompts/**`**, **zero
     `CLAUDE.md`**, **zero configuração**. **Nenhum `pytest` foi executado**, porque **zero
     código e zero teste mudaram**.
     **A lacuna fechada.** **O comportamento de uma linha que satisfaz EXATAMENTE o envelope de
     `PM1` dentro de uma seção `Rxx` cujo cabeçalho satisfaz `G2`, mas cujo rótulo literal NÃO
     é `PARCIAL`.**
     **A decisão.** **`status-fragmento` é PERMITIDO EXCLUSIVAMENTE sob cabeçalho `G2` cujo
     rótulo literal seja EXATAMENTE `PARCIAL`.** Sob **qualquer outro** rótulo literal, **a
     presença de uma linha que satisfaça exatamente o envelope de `PM1` é *FAIL-CLOSED***.
     **Consequências por regime.** Sob **`PARCIAL`**: **`PM5`** e **`PM11`** permanecem
     **literais** — **exatamente uma** declaração válida por fragmento emitível, com **nenhuma**
     e com **duas ou mais** sendo *fail-closed*. Sob **`ST1`–`ST3`**: **`PM7` permanece
     literal**, e continua sendo **caso particular com fundamento próprio** — `SP2`/`SP3` já
     propagam uniformemente, e `SP6` seria comprometido. Sob **qualquer outro rótulo `G2`
     válido**: a declaração é **igualmente proibida** por este registro. **Fora de seção
     `Rxx`**: **`PM6` permanece literal e aplicável**.
     **Fundamento normativo — exaustivo.** Apenas **`PM8`** — a declaração é **fonte explícita
     do status do fragmento *sob `PARCIAL`***, e somente ali — e **`PM11`** — é o **rótulo
     físico `PARCIAL` que ATIVA** o regime de status explicitamente declarado por fragmento, de
     modo que **fora dele não há regime a ativar** e uma declaração seria **segunda fonte de
     status sem regime que a autorize**. **A composição atual do corpus NÃO é fundamento**: o
     corpus é **evidência**, jamais origem de norma.
     **`G2` e `SP5` preservados.** Um rótulo fora de `ST1`–`ST3` e de `PARCIAL` **continua
     podendo satisfazer `G2`**, **continua literal e opaco** (**`GR2.10`**, **`GR3`**), **não**
     se torna gramaticalmente inválido, **não** recebe tradução automática, **não** recebe
     propagação automática, **não** é corrigido, **não** é normalizado e **não** é inferido — e
     **o seu status permanece NÃO RESOLVIDO conforme `SP5`**, que continua sendo o comportamento
     **arbitrado**, não uma lacuna. **Este registro proíbe SOMENTE a presença de
     `status-fragmento` nesse regime**, e nada mais.
     **Quatro cláusulas de precisão.** **1. Ausência.** A **ausência** de `status-fragmento` sob
     rótulo não-`PARCIAL` **NÃO é erro** desta regra nem de `PM5` — cuja obrigatoriedade vale
     **somente** sob `PARCIAL` —, e o status permanece **não resolvido por `SP5`**. **2.
     Envelope exato.** A regra alcança **exclusivamente** a linha que satisfaça **exatamente**
     `PM1`; toda **quase-declaração** — indentação, *whitespace* divergente, conteúdo antes ou
     depois, envelope incompleto, tab, ou qualquer outra divergência — **permanece conteúdo
     comum** e, **sob rótulo não-`PARCIAL`, não gera erro `PM` por si só**. **3. Rótulo
     desconhecido.** A regra **NÃO** torna inválido um rótulo desconhecido: **`GR2.10`**,
     **`GR3`** e **`SP5`** são **preservados** — o proibido ali é **a declaração**, não **o
     rótulo**. **4. Conteúdo emitível.** Uma linha iniciada por `>` **não satisfaz `PM1`** e
     **não pertence** a esta regra; nada aqui toca o bloco de citação, o texto emitível ou
     `MT3`–`MT11`.
     **`PM1`–`PM12` inalteradas, e `PM13` não existe.** O registro **não** cria rótulo local
     novo, **não** renumera, **não** reinterpreta e **não** altera nenhuma das doze regras. Em
     particular, **`PM7` não é alterado nem absorvido**: ele continua sendo o **caso particular
     de `ST1`–`ST3`**, com **fundamento próprio**.
     **Nenhum detalhe técnico é norma.** Não são definidos — e não podem ser lidos deste
     registro — módulo, função, assinatura, exceção, categorias técnicas, localizadores,
     mensagens, precedência interna de validação, tipo de erro interno, estratégia de
     importação, inspeção de árvore sintática ou arquivos futuros. **Tudo isso pertence a
     mandato técnico próprio**, ainda **não** emitido.
     **Corpus inalterado.** `knowledge/respostas-aprovadas.md` permanece **byte-a-byte** no blob
     `3bfb2e9fd18bac016e1dbe2c963ff916ceb0c96c`; **nenhuma linha `<!-- status-fragmento:
     APROVADO -->` foi inserida**; a decisão humana **`R28/F1 = APROVADO` continua DECIDIDA e
     AINDA NÃO APLICADA**; e **`PARCIAL` continua NÃO RESOLVIDO no corpus**.
     **Marco funcional inalterado.** **A C13 continua a última entrega funcional integrada** —
     **commit funcional `cbf3e379c9b6697cd502b6a7a0bd3e9bb76c1a27`**, **merge
     `50c1d5e681a11923c443c1f117de5751ea846cdd`** —, com **baseline `4100 passed`** em **Python
     3.14.5**. Esta entrega **não cria marco funcional** e **não recebe numeração de subetapa**.
     **`C` continua ARBITRADA / NÃO MATERIALIZADA**; o **índice físico continua INEXISTENTE**;
     a **bijeção física continua NÃO EXECUTADA**; a **autoridade de status continua NÃO
     MIGRADA** (**C-11**); e **`C-A1-ST6`–`C-A1-ST10` continuam NÃO satisfeitas**.
     **C14.** **C14 CONTINUA NÃO INICIADA FUNCIONALMENTE.** Esta entrega **não implementa
     C14**, **não cria módulo**, **não cria teste** e **não fixa API como norma** — ela **apenas
     elimina a lacuna normativa que bloqueava o mandato técnico**.
     **Relação com os itens anteriores.** **Os itens 87 a 100 permanecem corretos como registro
     do momento em que foram escritos.** Este item 101 **não os reescreve**; ele registra o
     estado **posterior**. Em particular, o **item 99** continua correto ao registrar
     `PM1`–`PM12` como arbitradas, e o **item 100** continua correto ao registrar `R28/F1` como
     **decidido e não aplicado** — o que **continua verdadeiro** após esta entrega.

102. **A DÉCIMA QUARTA MICROENTREGA FUNCIONAL DE `C` — O LEITOR/VALIDADOR DETERMINÍSTICO DE
     STATUS POR FRAGMENTO SOB `PARCIAL` — ESTÁ INTEGRADA À `main` PELO PR #120.**
     **ESTE ITEM 102 É REGISTRO HISTÓRICO DOCUMENTAL. NÃO É "SUBETAPA 102", NÃO É `E14` NEM
     `E15`, NÃO É NOVO IDENTIFICADOR NORMATIVO DE `C`, NÃO É NOVA MICROENTREGA FUNCIONAL E NÃO
     CRIA A 3B.8** — a **3B.8 continua INEXISTENTE**, e a **3B.7 continua a última subetapa
     numerada**. Ele registra **somente** a reconciliação documental pós-merge da décima quarta
     microentrega funcional, **já integrada** quando este item foi escrito.
     **Integração.** **PR #120** — **commit funcional
     `75025cc07c8d95f998c61f7516bf3db82bc9c06f`** (`feat: add deterministic fragment status
     reader`, **sem body, sem trailer**), **parent
     `ca5952ba7e883767319f20af4d090635eeab3663`**; **correção posterior NÃO FUNCIONAL
     `ca4ec54bc8c1324cc93baf2b7500fa4a04b3f298`** (`fix: align C14 residual CR documentation`);
     **merge commit `e8db60d95c104993d657de32b80e749dee8003ef`** (merge commit **normal**, dois
     parents: `ca5952ba7e…` e `ca4ec54bc8…`; **zero squash, zero rebase, zero auto-merge**),
     branch de origem `feat/c14-fragment-status-reader`, **preservada**. **A `main` passou de
     `ca5952ba7e883767319f20af4d090635eeab3663` para
     `e8db60d95c104993d657de32b80e749dee8003ef`.**
     **Escopo.** **Dois arquivos novos, e nenhum outro**:
     `src/casa77_sdr/response_fragment_status.py` — **+484 / −0** — e
     `tests/test_response_fragment_status.py` — **+1723 / −0**. Total: **2 arquivos, +2207 /
     −0**. **Zero arquivo preexistente alterado**: **zero `docs/**`**, **zero `knowledge/**`**
     (corpus preservado no blob `3bfb2e9fd18bac016e1dbe2c963ff916ceb0c96c`), **zero
     `prompts/**`**, **zero `CLAUDE.md`**, **zero configuração** e **zero teste preexistente**.
     **Contrato.** Módulo `casa77_sdr.response_fragment_status`; fronteira pública única
     **`extrair_status_por_fragmento(texto: str) -> tuple[tuple[str, str], ...]`** e exceção
     **`DeclaracaoDeStatusInvalida`**; **`__all__` com exatamente dois nomes**, **sem export no
     package root**. A exceção deriva **diretamente de `Exception`** e **não tem parentesco**
     com `RepresentacaoMarcadaInvalida`, `CabecalhoRxxInvalido`, `StatusNaoCanonicalizavel` ou
     `BijecaoInvalida`. **Imports de produção — exatamente dois**: `__future__` e
     `extrair_rotulos_de_cabecalho`.
     **`C12` primeiro, `C8` transitivo.** A **primeira** operação funcional é
     `extrair_rotulos_de_cabecalho(texto)`, chamada **uma única vez**; como a C12 já executa
     `ler_unidades_marcadas(texto)` como o seu próprio portão, a ordem entre fronteiras é
     **`C8` → `C12` → `C14`** **sem** segunda chamada a C8, e o módulo **não importa**
     `response_markdown_units`. `RepresentacaoMarcadaInvalida` e `CabecalhoRxxInvalido`
     **propagam intactas** — zero `try`/`except`, zero *wrapper*, zero reclassificação, zero
     `raise from`, `__cause__`/`__context__` inalterados —, e uma falha estrutural ou `G2`
     **fisicamente posterior vence** uma violação `PM` anterior.
     **Caminhada física local e invariante × `C12`.** A C12 devolve `(Rxx, rotulo_literal)` mas
     **não expõe a fronteira física da seção**, e `Rxx` homônimos são possíveis; por isso o
     contexto físico da seção corrente — `Rxx` **e** rótulo — é mantido linha a linha, **sem
     `zip`, sem `dict`, sem agrupamento por `Rxx`, sem pareamento por posição, sem cardinalidade
     e sem dedup**. Antes de **qualquer** retorno de sucesso, a sequência local de
     `(Rxx, rotulo_literal)` é comparada **inteira** com o retorno guardado da C12; divergência
     é **defeito interno** e produz `RuntimeError("invariante_estrutural")`, **nunca** a exceção
     pública.
     **Regime exclusivo.** A declaração é aceita **se e somente se** `rotulo_literal ==
     "PARCIAL"`. Os três rótulos físicos de `C-A1-ST1`–`C-A1-ST3` **não** são carregados
     localmente, e **não** há import de `response_status` nem de `response_status_propagation`.
     **Valores aceitos**, exatamente três: **`APROVADO`**, **`AGUARDA_APROVACAO`** e
     **`BLOQUEADO`** — **`PARCIAL` é inválido como valor**, e não há tolerância de caixa,
     normalização, `strip`, coerção, *alias* ou tradução.
     **Cinco mensagens fechadas.** `valor_invalido: declaracao`; `declaracao_fora_de_secao:
     declaracao`; `declaracao_proibida: declaracao`; `declaracao_orfa: declaracao`; e
     `declaracao_ausente: marcador`. Duas declarações consecutivas fazem **a primeira** ser
     órfã, e **nenhuma categoria `declaracao_multipla` foi criada**. As mensagens **nunca**
     ecoam `Rxx`, `id`, token, valor, rótulo, conteúdo, linha, índice, cardinalidade, `repr` ou
     tipo concreto. A ordem local é **fixa** — valor → seção → regime → marcador seguinte —, de
     modo que `valor_invalido` vence `declaracao_proibida` e `declaracao_fora_de_secao`, o
     regime é julgado **antes** da relação física, a **primeira violação em ordem física
     encerra** e **nada é devolvido parcialmente**. A **ausência** de declaração sob rótulo
     não-`PARCIAL` **não é erro**, e **quase-declaração permanece conteúdo comum**.
     **Saída.** Um par **`(token_canonico, status_canonico)`** por fragmento sob `PARCIAL` com
     declaração válida, com **ordem física, duplicidades e tokens homônimos preservados** —
     zero `dict`, `set`, dedup, `sorted` ou agrupamento; documento válido sem seção `PARCIAL`
     devolve `tuple()`.
     **Pureza.** Importa **apenas** `__future__` e `extrair_rotulos_de_cabecalho` — **zero
     I/O**, ***filesystem***, `open`, `pathlib`, YAML, JSON, rede, LLM, relógio, calendário,
     *locale*, variável de ambiente, banco, cache, logging, regex, `unicodedata`, estado mutável
     de módulo, `global`/`nonlocal`, `assert`, `dict`, `set`, `zip`, `sorted`, `splitlines`,
     `strip`, normalização e coerção. A política de linha é **exatamente** a de `C8`/`C12`,
     repetida por `PM10`, e a entrada **não é alterada**.
     **Os dois commits da PR #120.** O segundo, `ca4ec54bc8c1324cc93baf2b7500fa4a04b3f298`, foi
     **exclusivamente uma correção de docstring** sobre o `CR` residual: a redação anterior
     afirmava que um `CR` residual tornaria a linha **incapaz** de ser cabeçalho, declaração ou
     marcador, o que é **falso** e já era contrariado por teste explícito da C12 — a redação
     corrente registra que ele **permanece conteúdo literal, não é removido nem normalizado, e
     o seu efeito depende das respectivas gramáticas**. Esse commit tem **zero lógica
     alterada** e **zero teste alterado**, a baseline permaneceu **`4343 passed`**, e ele **NÃO
     é nova entrega funcional**.
     **Testes.** **Baseline anterior `4100 passed`**; **direcionado da C14 `243 passed`**;
     **vizinhança `201 passed`** (C8) e **`299 passed`** (C12); **regressão completa `4343
     passed`** — delta **+243**, **`4100 + 243 = 4343`** —, em **Python 3.14.5**, sob **`-W
     error`**, com **zero failures, zero errors e zero warnings** e **nenhum teste preexistente
     alterado ou removido**. **Estes números são evidência da ENTREGA FUNCIONAL C14, e NÃO desta
     reconciliação: NENHUM `pytest` FOI EXECUTADO AQUI**, porque **zero código, zero teste e
     zero `knowledge/**` mudaram**.
     **Checks.** A PR #120 e o merge commit `e8db60d95c104993d657de32b80e749dee8003ef` possuem
     **zero *combined statuses*** e **zero *workflow runs*** — **AUSÊNCIA DE CI/CHECKS — NÃO
     FALHA DE CI**. Nenhum CI foi criado por esta reconciliação.
     **Corpus e `R28/F1`.** **`R28/F1 = APROVADO` continua DECIDIDO HUMANAMENTE / AINDA NÃO
     APLICADO AO CORPUS.** `knowledge/respostas-aprovadas.md` permanece **byte-a-byte** no blob
     `3bfb2e9fd18bac016e1dbe2c963ff916ceb0c96c`; **nenhuma linha `<!-- status-fragmento:
     APROVADO -->` foi inserida**; e o corpus continua com **zero** ocorrências de
     `status-fragmento`. **A EXISTÊNCIA DA C14 NÃO SIGNIFICA QUE O CORPUS ESTEJA RESOLVIDO**:
     sobre o corpus atual, uma verificação de `PM5` **falharia por declaração ausente**, que é o
     **comportamento correto**.
     **Limites após a C14.** **`C` continua ARBITRADA / NÃO MATERIALIZADA**; **não** foram
     realizados a **aplicação física de `R28/F1`**, o **índice físico**, a **bijeção física
     real**, a **composição completa de status**, a **migração de autoridade** (**C-11**), a
     satisfação de **`C-A1-ST6`–`C-A1-ST10`**, os ***bindings***, a **`ASSERTIVA`**, nem as
     demais pendências registradas — *placeholder*, `caminho_yaml`, `hora` e **C-7** continuam
     **ABERTOS**. A **3B.8 continua INEXISTENTE**. **LER O STATUS DECLARADO NÃO É APLICAR
     STATUS, NÃO É ALTERAR O CORPUS, NÃO É RESOLVER `PARCIAL` NELE E NÃO É MATERIALIZAR `C`.**
     **Última entrega funcional.** **A C14 É AGORA A ÚLTIMA ENTREGA FUNCIONAL INTEGRADA**, com
     **commit funcional corrente `75025cc07c8d95f998c61f7516bf3db82bc9c06f`** e **baseline
     `4343 passed` em Python 3.14.5**. A **C13 passa a histórico imediatamente anterior**, com o
     seu registro **preservado**.
     **Próxima ação.** **AINDA NÃO EXECUTADA: aplicar fisicamente a decisão humana
     `R28/F1 = APROVADO` ao corpus, sob validação da C14, em entrega própria e auditada.** Nada
     disso é feito aqui, e `knowledge/**` **não foi alterado**.
     **Relação com os itens anteriores.** **Os itens 87 a 101 permanecem corretos como registro
     do momento em que foram escritos.** Este item 102 **não os reescreve**; ele registra o
     estado **posterior**. Em particular, o **item 100** continua correto ao registrar `R28/F1`
     como **decidido e não aplicado** — o que **continua verdadeiro** —, e o **item 101**
     continua correto ao registrar que a lacuna normativa pré-C14 fora fechada **sem**
     implementar C14: é **esta** entrega que a implementa.

103. **A DECISÃO HUMANA `R28/F1 = APROVADO` ESTÁ FISICAMENTE APLICADA AO CORPUS E INTEGRADA À
     `main` PELO PR #122.**
     **ESTE ITEM 103 É REGISTRO HISTÓRICO DOCUMENTAL. NÃO É "SUBETAPA 103", NÃO É `C15`, NÃO É
     `E15`, NÃO É IDENTIFICADOR NORMATIVO E NÃO CRIA A 3B.8** — a **3B.8 continua
     INEXISTENTE**, e a **3B.7 continua a última subetapa numerada**. Ele registra **somente** a
     aplicação física integrada de `R28/F1`.
     **Integração.** **PR #122** — **commit `77f8119488f0dc568721ca159fc13d3acd9f234d`**
     (`knowledge: apply R28 F1 fragment status`, **sem body, sem trailer**), **parent
     `7cb6e9f1b4c09361905a08312d83b77eb441e3f7`**, **merge commit
     `f3c35a4c738c9ab2e4343a3c012833144b514ca1`** (merge commit **normal**, dois parents:
     `7cb6e9f1b4…` e `77f8119488…`), branch de origem `knowledge/apply-r28-f1-status`. **A
     `main` passou de `7cb6e9f1b4c09361905a08312d83b77eb441e3f7` para
     `f3c35a4c738c9ab2e4343a3c012833144b514ca1`.**
     **Escopo.** **Um único arquivo**: `knowledge/respostas-aprovadas.md`, com **exatamente
     `+1 / −0`**. O corpus passou do blob **`3bfb2e9fd18bac016e1dbe2c963ff916ceb0c96c`** para
     **`3a30fe764b80902227fdefb9282f3916650e4f17`**. **Zero `src/**`**, **zero `tests/**`**,
     **zero `docs/**`**, **zero `prompts/**`**, **zero `CLAUDE.md`**, **zero
     `knowledge/casa77.yaml`** e **zero configuração**.
     **A alteração física.** A **única** linha adicionada é
     `<!-- status-fragmento: APROVADO -->`, colocada **imediatamente antes** do marcador `C-A5`
     `<!-- fragmento: F1 -->` da seção `R28`, com **zero linha física** entre ambas. **Nada mais
     foi tocado**: cabeçalho `R28`, marcador `F1`, bloco emitível, notas internas e todos os
     demais `Rxx` permanecem **inalterados**; **zero remoção**; e **nenhum dado comercial novo**
     foi versionado — a única informação nova é a **declaração estrutural de status já
     humanamente aprovada**.
     **`PM1`, `PM2` e `PM5` satisfeitas.** O envelope é **exato** (`PM1`); a declaração ocupa a
     **linha imediatamente anterior** ao marcador, preservando **`C-A5-I1`** e **`C-A5-I2`**
     (`PM2`); e a seção, cujo rótulo literal é **exatamente `PARCIAL`**, passa a ter **exatamente
     uma** declaração válida para o seu único fragmento emitível (`PM5`). A associação
     permanece **adjacência estrutural status → marcador** (`PM3`), **nunca identidade**: o
     token continua `<Rxx>/<id>`.
     **A decisão não foi inferida.** Ela é o **ato humano explícito** já registrado no **item
     documental 100** — **não** derivada de nota interna, de `null`, de conteúdo, de posição, do
     rótulo físico `PARCIAL` nem por ferramenta ou modelo algum —, e o valor pertence ao
     **vocabulário fechado de `C-3`** (`C-3a`).
     **Validação pela C14 sobre o corpus real**, registrada como evidência da PR #122: **`C8`
     passou — 37 tokens**; **`C12` passou — 30 cabeçalhos, 1 rotulado `PARCIAL`**; **`C14`
     passou**, com resultado **`(("R28/F1", "APROVADO"),)`**. Antes da aplicação, a C14 sobre o
     corpus falhava com `declaracao_ausente: marcador` — **o comportamento correto**. Nenhum
     código foi modificado para viabilizar a validação, e **nenhum teste persistente contra o
     corpus real foi criado**.
     **Testes.** **Direcionado da C14 `243 passed`**; **regressão completa `4343 passed`**; em
     **Python 3.14.5**, sob **`-W error`**, com **zero failures, zero errors e zero warnings** e
     **nenhum teste ajustado** para acomodar a alteração. **NENHUM `pytest` FOI EXECUTADO NESTA
     RECONCILIAÇÃO**, porque **zero código, zero teste e zero `knowledge/**` mudaram aqui**.
     **Limites — o que a aplicação NÃO faz.** Ela **NÃO** cria o índice físico, **NÃO** executa
     a bijeção física, **NÃO** migra a autoridade de status (**C-11**), **NÃO** completa a
     composição de status, **NÃO** resolve *bindings*, **NÃO** resolve `ASSERTIVA`, **NÃO**
     resolve *placeholder*, **NÃO** resolve `caminho_yaml`, **NÃO** resolve `hora`, **NÃO**
     resolve **C-7**, **NÃO** resolve automaticamente nota interna ou `null` — **`C-A1-P2`
     permanece literal** — e **NÃO materializa `C` integralmente**. **`C` continua ARBITRADA /
     NÃO MATERIALIZADA.**
     **`C-A1-ST6`–`C-A1-ST10`.** **Nenhuma delas é declarada satisfeita por causa desta
     aplicação.** Em particular, **`C-A1-ST8` exige o status de TODOS os fragmentos
     resolvidos**, e a evidência atual cobre **um** fragmento: a validação de `R28/F1` **não é
     extrapolada** para cobertura global de status, o que exigiria **prova própria**. **`C-A4-G8`
     continua valendo**: cobertura estrutural **não** é emissibilidade.
     **Última entrega funcional de código.** **A C14 continua sendo a última microentrega
     funcional de código integrada** — commit funcional
     `75025cc07c8d95f998c61f7516bf3db82bc9c06f`, merge
     `e8db60d95c104993d657de32b80e749dee8003ef`, **baseline `4343 passed` em Python 3.14.5**. A
     **PR #122 é a aplicação física, no corpus, de decisão humana já arbitrada**, e **NÃO é
     renomeada como "C15"**: **nenhuma numeração funcional nova foi criada**.
     **Próxima ação.** A antiga próxima ação — *aplicar fisicamente `R28/F1`* — **está
     CUMPRIDA** e deixa de constar. A **próxima ação técnica requer definição e auditoria da
     próxima pendência de `C` após a aplicação física de `R28/F1`**, e **essa pendência NÃO foi
     eleita nem iniciada** nesta entrega.
     **Relação com os itens anteriores.** **Os itens 87 a 102 permanecem corretos como registro
     do momento em que foram escritos.** Este item 103 **não os reescreve**; ele registra o
     estado **posterior**. Em particular, o **item 100** continua correto ao registrar `R28/F1`
     como **decidido e ainda não aplicado à época**, e o **item 102** continua correto ao
     registrar que, **naquele momento**, o corpus não continha declaração e uma verificação de
     `PM5` falharia por declaração ausente — **é esta entrega que aplica a decisão**, e as duas
     afirmações permanecem verdadeiras **como registro daquele momento**.

104. **A ASSOCIAÇÃO FÍSICA DETERMINÍSTICA DE SEÇÃO E FRAGMENTOS ESTÁ INTEGRADA À `main` PELO
     PR #124.**
     **ESTE ITEM 104 É REGISTRO HISTÓRICO DOCUMENTAL. NÃO É "SUBETAPA 104", NÃO É `C15`, NÃO É
     `E15`, NÃO É IDENTIFICADOR NORMATIVO E NÃO CRIA A 3B.8** — a **3B.8 continua
     INEXISTENTE**, e a **3B.7 continua a última subetapa numerada**. Ele registra **somente** a
     integração funcional da PR #124.
     **Integração.** **PR #124** — **commit funcional
     `0e41165406c3a9261a1fcc8d0f9c600b0469e730`** (`feat: add deterministic response section
     membership`, **sem body, sem trailer**), **parent
     `c62c6b024116cf2f2718bebe465c33f365fb8db2`**, **merge commit
     `ecaf0a2b3a594f8fedd10f708461ad2eeb18e086`** (merge commit **normal**, dois parents:
     `c62c6b0241…` e `0e41165406…`; **zero squash, zero rebase, zero auto-merge**), branch de
     origem `feat/c-section-membership`, **preservada**. **A `main` passou de
     `c62c6b024116cf2f2718bebe465c33f365fb8db2` para
     `ecaf0a2b3a594f8fedd10f708461ad2eeb18e086`.**
     **Escopo.** **Dois arquivos novos, e nenhum outro**:
     `src/casa77_sdr/response_section_membership.py` — **+371 / −0** — e
     `tests/test_response_section_membership.py` — **+1269 / −0**. Total: **2 arquivos, +1640 /
     −0**. **Zero arquivo preexistente alterado**: **zero `docs/**`**, **zero `knowledge/**`**
     (corpus preservado no blob `3a30fe764b80902227fdefb9282f3916650e4f17`), **zero
     `prompts/**`**, **zero `CLAUDE.md`**, **zero configuração**, **zero dependência** e **zero
     teste preexistente**.
     **Contrato.** Módulo `casa77_sdr.response_section_membership`; fronteira pública única
     **`associar_fragmentos_a_secao(texto: str) -> tuple[tuple[str, str, tuple[str, ...]],
     ...]`**; **`__all__` com exatamente um nome** — `["associar_fragmentos_a_secao"]`; **sem
     exceção pública nova** (o módulo **não declara classe alguma**); **sem export no package
     root**; **sem DTO** e **sem dataclass**. **Imports de produção — exatamente dois**:
     `__future__` e `extrair_rotulos_de_cabecalho`.
     **Saída.** `(Rxx, rotulo_literal, tokens)`, **uma entrada por INSTÂNCIA FÍSICA** de seção
     `## Rxx`, na **ordem física do documento**, com os tokens canônicos `<Rxx>/<id>` **daquela
     instância**, na ordem física em que aparecem. Documento vazio ou sem `## Rxx` devolve
     `tuple()`.
     **Homônimos.** **Seções `Rxx` homônimas permanecem instâncias físicas distintas**: entradas
     **separadas**, ordem física preservada, **tokens textualmente repetidos preservados** —
     **zero consolidação por valor de `Rxx`, zero deduplicação, zero agrupamento**. **A posição
     da entrada é apenas ordem de leitura, jamais identidade** (**`C-A5-I5`**).
     **`C12` primeiro, `C8` transitivo.** A **primeira** operação funcional é
     `extrair_rotulos_de_cabecalho(texto)`, chamada **uma única vez**; como a C12 já executa
     `ler_unidades_marcadas(texto)` como o seu próprio portão, a ordem é **`C8` → `C12` → esta
     fronteira**, **sem segunda chamada direta a `C8`**, e o módulo **não importa**
     `response_markdown_units`. `RepresentacaoMarcadaInvalida` e `CabecalhoRxxInvalido`
     **propagam intactas** — zero `try`/`except`, zero *wrapper*, zero reclassificação, zero
     `raise from`, `__cause__`/`__context__` inalterados —, e uma falha estrutural ou `G2`
     **fisicamente posterior vence** qualquer anomalia local anterior; **nada é devolvido
     parcialmente**. **Nenhum julgamento estrutural é refeito**: marcador inválido, bloco sem
     marcador, marcador fora de seção, `id` fora da gramática, `id` duplicado e seção sem unidade
     **continuam sendo de `C8`**.
     **Caminhada física local e invariante × `C12`.** A caminhada é **mínima e compatível com
     `C8`** — ATX só na coluna 0; níveis 1 e 2 encerram a seção `##`; `##` não-`Rxx` deixa zero
     seção em escopo; `## Rxx` válido abre nova instância; níveis 3–6 não encerram; linha `>`
     nunca é cabeçalho —, na **mesma política de linha** (divisão exclusivamente por `LF`, no
     máximo um `CR` terminal por segmento, sem `splitlines()`, sem *universal newline*, sem
     normalização). Antes de **qualquer** retorno de sucesso, a sequência local de
     `(Rxx, rotulo_literal)` de **todas** as instâncias é comparada **inteira** com o retorno
     guardado da C12; divergência é **defeito interno** e produz
     **`RuntimeError("invariante_estrutural")`**, **nunca** exceção pública — **sem `zip`, sem
     `dict`, sem agrupamento, sem dedup e sem cardinalidade como prova de identidade**.
     **Zero semântica de status.** O módulo **não importa** `response_status`,
     `response_status_propagation` nem `response_fragment_status`; **não** canonicaliza, **não**
     traduz rótulo, **não** decide `ST1`–`ST3`, **não** interpreta `PARCIAL`, **não** lê
     `status-fragmento`, **não** propaga, **não** aplica, **não** resolve status e **não** decide
     `SP5`. O **`rotulo_literal` é completamente opaco** nesta fronteira.
     **Equivalência estrutural com `C8` — EVIDÊNCIA DE TESTE, NÃO NORMA NOVA.** Nos casos
     sintéticos válidos exercitados, o *flatten* dos tokens da nova fronteira **coincide com a
     saída de `ler_unidades_marcadas(texto)`**. Cobertura sintética: **uma seção**; **várias
     seções**; **múltiplos fragmentos**; **homônimos**; **tokens repetidos**; **`H3`–`H6`**;
     **`LF`**; **`CRLF`**; **documento sem `Rxx`**; e **bloco fora de seção**. Essa equivalência
     é **verificada nos testes** e **não** é convertida em norma.
     **Testes.** **Baseline anterior `4343 passed`**; **direcionado novo `134 passed`**;
     **vizinhanças `201 passed`** (C8), **`299 passed`** (C12) e **`243 passed`** (C14), todas
     **inalteradas**; **regressão completa `4477 passed`** — delta **+134**, **`4343 + 134 =
     4477`** —, em **Python 3.14.5**, sob **`-W error`**, com **zero failures, zero errors e
     zero warnings** e **nenhum teste preexistente alterado ou removido**. **Estes números são
     evidência da ENTREGA FUNCIONAL do PR #124, e NÃO desta reconciliação: NENHUM `pytest` FOI
     EXECUTADO AQUI**, porque **zero código, zero teste e zero `knowledge/**` mudaram**.
     **Checks.** A PR #124 e o merge commit `ecaf0a2b3a594f8fedd10f708461ad2eeb18e086` possuem
     **zero *statuses*** e **zero *workflow runs*** — **AUSÊNCIA DE CI/CHECKS — NÃO FALHA DE
     CI**. Nenhum CI foi criado por esta reconciliação.
     **Limites.** A PR #124 **NÃO**: compõe status completo; resolve `SP5`; canonicaliza status;
     propaga status; interpreta `PARCIAL`; cria índice; executa a bijeção física real;
     implementa *bindings*; implementa `ASSERTIVA`; define *placeholder*; define `caminho_yaml`;
     define `hora`; resolve **C-7**; cria *renderer*; integra *runtime*; migra autoridade;
     satisfaz automaticamente **`C-A1-ST6`–`C-A1-ST10`**; nem cria a **3B.8**. **ASSOCIAR
     FRAGMENTOS À SEÇÃO NÃO É COMPOR STATUS E NÃO É MATERIALIZAR `C`** — **`C` continua
     ARBITRADA / NÃO MATERIALIZADA**.
     **`R28/F1`.** **`R28/F1 = APROVADO` continua fisicamente APLICADO na `main`**: o corpus
     `knowledge/respostas-aprovadas.md` permanece **byte-a-byte** no blob
     `3a30fe764b80902227fdefb9282f3916650e4f17`, e **a PR #124 não alterou `knowledge/**`**.
     **`SP5`.** **A MICRO-ARBITRAGEM SOBRE O COMPORTAMENTO DA FUTURA COMPOSIÇÃO TOTAL DIANTE DE
     `SP5` CONTINUA NÃO RESPONDIDA.** A PR #124 **não** a responde, **não** escolhe
     *fail-closed*, **não** escolhe omissão e **não** escolhe representação explícita de
     ausência — e **este item também não a resolve**.
     **Entrega funcional mais recente.** **A associação física de seção e fragmentos é agora a
     ENTREGA FUNCIONAL DE CÓDIGO MAIS RECENTE INTEGRADA**, com **commit funcional corrente
     `0e41165406c3a9261a1fcc8d0f9c600b0469e730`** e **baseline `4477 passed` em Python 3.14.5**.
     A **C14 passa a histórico funcional imediatamente anterior**, com o seu registro
     **preservado**. **Ela NÃO recebe denominação `C15`** e **nenhuma numeração funcional nova
     foi criada**.
     **Próxima ação.** **Requer auditoria da pendência seguinte após a integração da associação
     física, observando que a composição completa de status continua BLOQUEADA pela
     micro-arbitragem de `SP5`.** **Nenhuma implementação é eleita** e **nenhum planejamento
     adicional é iniciado** neste item.
     **Relação com os itens anteriores.** **Os itens 87 a 103 permanecem corretos como registro
     do momento em que foram escritos.** Este item 104 **não os reescreve**; ele registra o
     estado **posterior**. Em particular, o **item 102** continua correto ao registrar a C14
     como a última entrega funcional **à época**, e o **item 103** continua correto ao registrar
     `R28/F1` como **aplicado** — o que **continua verdadeiro**.

105. **O COMPORTAMENTO DA FUTURA COMPOSIÇÃO TOTAL DE STATUS DIANTE DE `SP5` ESTÁ DECIDIDO
     DOCUMENTALMENTE — FAIL-CLOSED, COM ZERO RETORNO PARCIAL.**
     **ESTE ITEM 105 É REGISTRO DOCUMENTAL. NÃO É "SUBETAPA 105", NÃO É `C15`, NÃO É `E15`, NÃO
     É IDENTIFICADOR NORMATIVO E NÃO CRIA A 3B.8** — a **3B.8 continua INEXISTENTE**, e a
     **3B.7 continua a última subetapa numerada**. Ele registra **exclusivamente** esta
     micro-arbitragem.
     **Escopo da entrega.** **EXCLUSIVAMENTE DOCUMENTAL / NORMATIVA**: **dois arquivos** —
     `docs/07-arquitetura-motor-respostas.md` e `docs/00-estado-atual.md`. **Zero `src/**`,
     zero `tests/**`, zero `knowledge/**`, zero `prompts/**`, zero `CLAUDE.md`, zero
     configuração e zero dependência.** **Nenhum compositor foi implementado**, e **nenhum
     módulo, função, assinatura, exceção ou mensagem foi decidido.**
     **A decisão.** Quando uma **futura fronteira cujo contrato seja resolver e devolver o
     status de TODOS os fragmentos emitíveis do documento** encontrar fragmento pertencente a
     seção cujo rótulo literal **satisfaça `G2`** mas **não** pertença às traduções automáticas
     de `ST1`–`ST3` e **não** seja `PARCIAL`, o fragmento **permanece NÃO RESOLVIDO por `SP5`**
     e a **composição total FALHA FECHADA**. Ela **não devolve resultado parcial**, **não omite
     silenciosamente** o fragmento, **não** o devolve com **marcador ou valor de ausência**,
     **não cria valor sentinela**, **não cria quarto status**, **não converte** o rótulo e
     **não torna** o cabeçalho `G2` inválido.
     **A invariante.** **UM RETORNO BEM-SUCEDIDO DA FUTURA COMPOSIÇÃO TOTAL NÃO PODE COEXISTIR
     COM FRAGMENTO NÃO RESOLVIDO POR ESSE RAMO DE `SP5`** — sucesso total e fragmento não
     resolvido são **mutuamente exclusivos** naquela fronteira.
     **Alternativas rejeitadas.** **1. Omissão silenciosa — REJEITADA**: a composição **não
     pode** deixar o fragmento não resolvido fora da saída e ainda declarar sucesso. **2.
     Representação explícita de ausência em retorno bem-sucedido — REJEITADA**: **`None`**,
     **sentinela**, **quarto valor**, **status especial** ou estrutura de "não resolvido"
     **coexistindo com sucesso total** não substituem status pertencente a **`C-3`**. Esta
     segunda rejeição vale **para a fronteira de composição TOTAL de status**, e **não impede**
     que **outras APIs futuras, com OUTRO contrato**, representem estado não resolvido de outra
     forma.
     **`SP5` permanece semanticamente INTACTA.** Rótulo fora de `ST1`–`ST3` **não produz
     propagação automática**; a **ausência de tradução não é corrigida, normalizada nem
     inferida**; o rótulo desconhecido que satisfaça `G2` **continua gramaticalmente válido**,
     **literal** e **opaco** (**`GR2.10`**, **`GR3`**); e o seu status **permanece NÃO
     RESOLVIDO** — **comportamento arbitrado**, jamais lacuna. `SP1`–`SP7` permanecem
     **inalteradas** e **`SP8` não existe**.
     **`PARCIAL` continua EXPRESSAMENTE FORA deste ramo.** Ele permanece sob **`C-A1-ST4`**,
     **`SP4`**, **`PM1`–`PM12`**, o **regime exclusivo de `status-fragmento`** e a **C14**. Na
     composição total futura, os fragmentos sob `PARCIAL` são resolvidos **exclusivamente**
     pelas **declarações explícitas válidas** de `status-fragmento`, **sem propagação
     automática**; se houver **violação do contrato já materializado da C14** — incluindo
     **valor inválido**, **declaração órfã** ou **ausência da declaração obrigatória** —, as
     **falhas já existentes da C14 continuam prevalecendo segundo a sua precedência própria**.
     **Nenhuma semântica nova de `PARCIAL` foi criada.**
     **Nenhuma exceção concreta foi desenhada.** **Nome de classe**, **mensagem**,
     **categorias**, **localizadores**, **herança**, a escolha entre **propagar exceção
     existente** ou **criar exceção nova** e a **precedência exata entre falhas de composição
     ainda não desenhadas** **continuam NÃO DECIDIDOS** — pertencem a **planejamento técnico
     próprio e posterior**.
     **Relação com `C-A1-ST8`.** **`C-A1-ST8` continua literal — status de TODOS os fragmentos
     resolvidos — e ESTA ARBITRAGEM NÃO O SATISFAZ.** Ela garante **somente** que uma futura
     composição total **não declare sucesso** enquanto houver fragmento não resolvido pelo ramo
     desconhecido de `SP5`; a satisfação de `ST8` continuará exigindo **execução e auditoria
     próprias** sobre os insumos canônicos pertinentes.
     **Evidência estrutural do corpus — NÃO fundamento normativo.** No corpus canônico vigente
     `knowledge/respostas-aprovadas.md`, **inalterado** e byte-a-byte no blob
     `3a30fe764b80902227fdefb9282f3916650e4f17`, há **30** seções `Rxx`: **25** com rótulo de
     `C-A1-ST1`, **2** de `C-A1-ST2`, **2** de `C-A1-ST3`, **1** `PARCIAL` e **0** com outro
     rótulo `G2` válido. **ESSA DISTRIBUIÇÃO É EVIDÊNCIA DO CORPUS ATUAL E NÃO FUNDAMENTO
     NORMATIVO DA ARBITRAGEM**: a regra **permanece válida** ainda que um **futuro corpus
     aprovado** contenha outro rótulo `G2` válido.
     **Testes.** **NENHUM `pytest` FOI EXECUTADO NESTA ENTREGA**, porque **zero código, zero
     teste e zero `knowledge/**` mudaram**. A **baseline registrada permanece `4477 passed` /
     Python 3.14.5**, sob **`-W error`**, **evidência da entrega funcional do PR #124** — e
     **nenhuma execução nova é alegada aqui**.
     **Limites.** Esta arbitragem **NÃO**: implementa composição total; transforma em resolvido
     o status que permanece **NÃO RESOLVIDO por `SP5`**;
     canonicaliza status; propaga status; interpreta `PARCIAL`; cria índice; executa a bijeção
     física; implementa *bindings*; implementa `ASSERTIVA`; define *placeholder*; define
     `caminho_yaml`; define `hora`; resolve **C-7**; migra a autoridade de status (**C-11**);
     satisfaz **`C-A1-ST6`**–**`C-A1-ST10`**; nem cria a **3B.8**. **`C` CONTINUA ARBITRADA /
     NÃO MATERIALIZADA.**
     **Próxima ação.** **Após a integração desta arbitragem, retornar ao Claude Desktop para
     produzir o plano técnico fechado da composição total de status.** **A implementação NÃO
     está pronta** e **não é declarada pronta antes da integração desta decisão**.
     **Relação com os itens anteriores.** **Os itens 87 a 104 permanecem corretos como registro
     do momento em que foram escritos.** Este item 105 **não os reescreve**; ele registra o
     estado **posterior**. Em particular, o **item 104** continua correto ao registrar que, **à
     época**, a micro-arbitragem do comportamento da futura composição total diante de `SP5`
     **continuava NÃO RESPONDIDA** — **é este item que a responde** —, e continua correto ao
     registrar a associação física de seção e fragmentos como a **entrega funcional de código
     mais recente**, o que **continua verdadeiro**.

106. **A COMPOSIÇÃO TOTAL DETERMINÍSTICA DE STATUS DOS FRAGMENTOS EMITÍVEIS ESTÁ INTEGRADA À
     `main` PELO PR #127.**
     **ESTE ITEM 106 É REGISTRO HISTÓRICO DOCUMENTAL. NÃO É "SUBETAPA 106", NÃO É `C15`, NÃO É
     `E15`, NÃO É IDENTIFICADOR NORMATIVO E NÃO CRIA A 3B.8** — a **3B.8 continua INEXISTENTE**,
     e a **3B.7 continua a última subetapa numerada**. Ele registra **exclusivamente** a
     integração funcional da PR #127.
     **Integração.** **PR #127** — **commit funcional
     `24d2b0fef6a08c26e751f8eb8bb70943b30c0339`** (`feat: add total fragment status
     composition`, **sem body, sem trailer**), **parent
     `9ace0f5e4782e21c590aa8631f637017b3995809`**, **merge commit
     `00c45e9b95f233bc7aa0f9666e090208994fb190`** (merge commit **normal**, dois parents:
     `9ace0f5e47…` e `24d2b0fef6…`; **zero squash, zero rebase, zero auto-merge**), branch de
     origem `feat/total-fragment-status-composition`, **preservada**. **A `main` passou de
     `9ace0f5e4782e21c590aa8631f637017b3995809` para
     `00c45e9b95f233bc7aa0f9666e090208994fb190`.**
     **Escopo.** **Dois arquivos novos** — `src/casa77_sdr/response_status_composition.py`
     (**+234**) e `tests/test_response_status_composition.py` (**+1606**) —, **2 arquivos,
     +1840 / −0**, **zero arquivo preexistente alterado**, **zero `docs/**`**, **zero
     `knowledge/**`**, **zero `prompts/**`**, **zero `CLAUDE.md`**, **zero configuração**, **zero
     dependência** e **zero alteração de `casa77_sdr/__init__.py`**.
     **Contrato.** Módulo `casa77_sdr.response_status_composition`, com a fronteira pública única
     **`compor_status_dos_fragmentos(texto: str) -> tuple[tuple[str, str], ...]`** e **`__all__`
     de exatamente um nome** — `["compor_status_dos_fragmentos"]`. **Um único parâmetro**, **sem
     default**; **nenhuma classe**; **nenhuma exceção pública nova**; **nenhum DTO**; **nenhum
     dataclass**; **nenhum Enum**; **nenhum export pelo package root**. A fronteira é **pura e
     determinística**, recebe o **texto já em memória** — **a origem correta do texto é
     pré-condição do chamador** — e não tem **I/O**, ***filesystem***, YAML, JSON, rede, LLM nem
     **conhecimento comercial**.
     **Saída.** Um par `(token_canonico, status_canonico)` por **OCORRÊNCIA FÍSICA** de fragmento
     emitível, na **ordem física do documento**, **preservando duplicidades** e **sem
     deduplicar, agrupar ou reordenar**. Documento vazio ou sem `## Rxx` devolve `tuple()`. O
     status pertence **exclusivamente** ao vocabulário fechado de **`C-3`** — **nunca** `None`,
     sentinela, marcador de ausência, quarto valor ou valor padrão.
     **`ST1`–`ST3`.** Resolvidos **exclusivamente** por `propagar_status`. **A C13 permanece a
     autoridade da propagação e da tradução**, **nenhuma tabela foi duplicada** e os três rótulos
     físicos de `C-A1-ST1`–`C-A1-ST3` **não** são carregados no módulo novo.
     **`PARCIAL`.** Resolvido **exclusivamente** por `extrair_status_por_fragmento`. **A C14
     permanece a autoridade do status explicitamente declarado**, e **A ASSOCIAÇÃO TOKEN/STATUS
     SOB `PARCIAL` É HERDADA DO CONTRATO DA C14**, jamais reimplementada: a composição **não**
     refaz `PM`, **não** interpreta `status-fragmento` localmente e **não** faz segunda caminhada.
     **`SP5` — rótulo `G2` desconhecido.** Continua **`G2` válido**, **literal**, **opaco**, **sem
     tradução automática** e com **status NÃO RESOLVIDO por `SP5`**. Na composição total ele
     **FALHA FECHADA** via `StatusNaoCanonicalizavel`, que **sobe intacta** — classe, mensagem,
     `__cause__` e `__context__` inalterados, **sem `try`/`except`, sem *wrapper*, sem
     reclassificação e sem `raise from`**. **Zero retorno parcial**, **zero omissão silenciosa**,
     **zero `None`**, **zero sentinela**, **zero quarto status**, e **o cabeçalho não se torna
     inválido**. **A ARBITRAGEM FAIL-CLOSED DE `SP5` ESTÁ MATERIALIZADA NESTA FRONTEIRA.**
     **Ordem funcional.** **1.** `associar_fragmentos_a_secao(texto)`, **uma vez**; **2.**
     `extrair_status_por_fragmento(texto)`, **uma vez e INCONDICIONALMENTE**; **3.** `I1`; **4.**
     caminhada pelas instâncias físicas; **5.** consumo do fluxo da C14 sob `PARCIAL`; **6.**
     `propagar_status` nos demais rótulos; **7.** `I2`; **8.** `I3`; **9.** retorno. A C14 **não**
     é preguiçosa e **não** é invertida com a associação física.
     **Precedência.** `C8` → `C12` → `C14`/`PM` → `I1` → `SP5` → `I2`/`I3`. **Uma falha `PM`
     fisicamente posterior vence um rótulo `SP5` anterior**, porque a C14 é portão integral e
     percorre o documento **inteiro antes** da caminhada local. Todas as exceções públicas das
     dependências — `RepresentacaoMarcadaInvalida`, `CabecalhoRxxInvalido`,
     `DeclaracaoDeStatusInvalida` e `StatusNaoCanonicalizavel` — **sobem intactas**.
     **Invariantes internos.** **`I1`** compara **inteira** a sequência de tokens do retorno da
     C14 com as ocorrências `PARCIAL` esperadas pela associação física: ela prova
     **compatibilidade de cobertura e de ordem**, e **NÃO reprova nem redefine a associação
     interna token/status já produzida pela C14**. **`I2`** compara **inteira** a sequência de
     tokens da saída com todas as ocorrências físicas esperadas: **nada omitido**, **nada
     inventado**, **ordem física preservada**. **`I3`** confere que **todo status pertence a
     `C-3`** — `APROVADO`, `AGUARDA_APROVACAO`, `BLOQUEADO`. Falha em `I1`, `I2` ou `I3` produz
     **`RuntimeError("invariante_estrutural")`** — **defeito interno**, **nunca** exceção pública,
     e **único `raise` originado pelo módulo**.
     **Homônimos.** A suíte cobre **seções homônimas**, **tokens textualmente repetidos**, **duas
     instâncias `PARCIAL` homônimas com o MESMO token textual e status DIFERENTES**, **três
     instâncias `PARCIAL` homônimas com status distintos** e a **mistura `PARCIAL` + `ST1`
     homônimas**. **Zero deduplicação**, **zero agrupamento por `Rxx`**, **ordem física
     preservada**, e **a posição do par é apenas ordem de leitura, jamais identidade**
     (**`C-A5-I5`**).
     **Pureza.** Imports de produção: **apenas** `__future__` e as três fronteiras
     (`associar_fragmentos_a_secao`, `extrair_status_por_fragmento`, `propagar_status`) — **zero
     I/O**, ***filesystem***, `open`, `pathlib`, YAML, JSON, rede, LLM, relógio, calendário,
     *locale*, variável de ambiente, banco, cache, logging, regex, `unicodedata`, `try`,
     `except`, `raise from`, `zip`, `dict`, `set`, `sorted`, `reversed`, `map`, `filter`, estado
     mutável de módulo, `global`/`nonlocal`, `assert`, normalização e coerção. A entrada **não é
     alterada**. C8 e C12 **não** são importados diretamente, e `response_status` **não** é
     importado.
     **Testes.** **Baseline anterior `4477 passed`**; **direcionado novo `117 passed`**;
     **vizinhanças `134 passed`** (associação física), **`243 passed`** (C14), **`397 passed`**
     (C13), **`299 passed`** (C12) e **`201 passed`** (C8), todas **inalteradas**; **regressão
     completa `4594 passed`** — delta **+117**, **`4477 + 117 = 4594`** —, em **Python 3.14.5**,
     sob **`-W error`**, com **zero failures, zero errors e zero warnings** e **nenhum teste
     preexistente alterado ou removido**. **A suíte é inteiramente SINTÉTICA** e **nenhum teste
     persistente contra o corpus foi criado**. **Estes números são evidência da ENTREGA FUNCIONAL
     do PR #127, e NÃO desta reconciliação: NENHUM `pytest` FOI EXECUTADO AQUI**, porque **zero
     código, zero teste e zero `knowledge/**` mudaram**.
     **Evidência read-only do corpus — NÃO É TESTE E NÃO É NORMA.** A fronteira foi executada
     **uma vez**, de forma **read-only e não persistente**, contra
     `knowledge/respostas-aprovadas.md` — **inalterado** e byte-a-byte no blob
     `3a30fe764b80902227fdefb9282f3916650e4f17` —, devolvendo **37 pares**, **37 tokens
     distintos**, com agregados **`APROVADO`: 35** e **`AGUARDA_APROVACAO`: 2**. **Nenhum
     conteúdo comercial é reproduzido**; **o corpus não foi alterado**; e essa evidência **NÃO
     satisfaz automaticamente `C-A1-ST8`** e **NÃO migra a autoridade de status**.
     **Checks.** A PR #127 e o merge commit `00c45e9b95f233bc7aa0f9666e090208994fb190` possuem
     **zero *statuses*** e **zero *workflow runs*** — **AUSÊNCIA DE CI/CHECKS — NÃO FALHA DE
     CI**. Nenhum CI foi criado por esta reconciliação.
     **`C-A1-ST8` NÃO É DECLARADA SATISFEITA.** A composição materializa a **fronteira técnica**
     capaz de resolver o status total **do texto recebido**. **`ST8` continua exigindo prova e
     auditoria próprias** sobre os insumos canônicos e **dentro dos gates de migração**
     (`C-A1-ST6`–`C-A1-ST10`), e **essa decisão não é antecipada aqui**.
     **Limites.** A PR #127 **NÃO**: satisfaz `C-A1-ST8`; cria índice; executa a bijeção física
     real; implementa *bindings*; implementa `ASSERTIVA`; define *placeholder*; define
     `caminho_yaml`; define `hora`; resolve **C-7**; cria *renderer*; integra *runtime*; migra a
     autoridade de status; satisfaz automaticamente **`C-A1-ST6`**, **`C-A1-ST7`**,
     **`C-A1-ST8`**, **`C-A1-ST9`** ou **`C-A1-ST10`**; nem cria a **3B.8**. **A autoridade de
     status continua NÃO MIGRADA** (**`C-11`**). **COMPOR STATUS NÃO É MATERIALIZAR `C`** — **`C`
     continua ARBITRADA / NÃO MATERIALIZADA**.
     **Entrega funcional mais recente.** **A composição total de status é agora a ENTREGA
     FUNCIONAL DE CÓDIGO MAIS RECENTE INTEGRADA**, com **commit funcional corrente
     `24d2b0fef6a08c26e751f8eb8bb70943b30c0339`** e **baseline `4594 passed` em Python 3.14.5**.
     A **associação física determinística de seção e fragmentos (PR #124) passa a histórico
     funcional imediatamente anterior**, com o seu registro **preservado**. **Ela NÃO recebe
     denominação `C15`** e **nenhuma numeração funcional nova foi criada**.
     **Próxima ação.** **Após a integração desta reconciliação, auditar a pendência seguinte de
     `C` a partir do estado canônico atualizado.** **Nenhuma implementação é eleita** neste item,
     e **não** se afirma que a próxima ação seja `ST8`, o índice, *placeholder*, `caminho_yaml`,
     `hora`, **C-7**, *bindings*, `ASSERTIVA` ou *renderer* — a eleição pertence a **etapa
     posterior**, conforme a governança.
     **Relação com os itens anteriores.** **Os itens 87 a 105 permanecem corretos como registro
     do momento em que foram escritos.** Este item 106 **não os reescreve**; ele registra o
     estado **posterior**. Em particular, o **item 104** continua correto ao registrar a
     associação física como a entrega funcional mais recente **à época**, e o **item 105**
     continua correto ao registrar a micro-arbitragem de `SP5` como **decidida documentalmente** —
     o que **continua verdadeiro**, e cuja decisão *fail-closed* **é agora materializada em
     código** por esta entrega.

107. **A GRAMÁTICA DE `caminho_yaml` ESTÁ ARBITRADA DOCUMENTALMENTE — ALTERNATIVA `A2`.**
     **ESTE ITEM 107 É REGISTRO DOCUMENTAL. NÃO É "SUBETAPA 107", NÃO É `C15`, NÃO É `E15`, NÃO
     É IDENTIFICADOR NORMATIVO E NÃO CRIA A 3B.8** — a **3B.8 continua INEXISTENTE**, e a
     **3B.7 continua a última subetapa numerada**. Ele registra **exclusivamente** a arbitragem
     documental da gramática de `caminho_yaml`. **`C-A6` NÃO EXISTE.**
     **Escopo da entrega.** **EXCLUSIVAMENTE DOCUMENTAL / NORMATIVA**: **dois arquivos** —
     `docs/07-arquitetura-motor-respostas.md` e `docs/00-estado-atual.md`. **Zero `src/**`, zero
     `tests/**`, zero `knowledge/**`, zero `prompts/**`, zero `CLAUDE.md`, zero configuração e
     zero dependência.** **Nenhum parser é implementado**, **nenhum resolver é implementado**,
     **nenhum índice é criado**, **nenhum *binding* é materializado** e **nenhum módulo, função,
     assinatura, exceção, mensagem ou API é decidido**.
     **Posição do bloco.** `docs/07` §2.3, **imediatamente antes** de
     `## 3. Comparação técnica — Opção A × Opção B`, sob o cabeçalho exato
     **"Micro-arbitragem documental da gramática de caminho_yaml"**. Os rótulos locais
     **`CY1`–`CY14`** existem **somente** como rastreabilidade interna do bloco e **NÃO são
     normativos fora dele**.
     **Decisão central — alternativa `A2`.** `caminho_yaml` **permanece semanticamente uma
     `str`**, e a gramática governa **essa `str`, DEPOIS do parsing YAML**. Existem **exatamente
     duas** formas semânticas: a **ABSOLUTA**, **sem marcador**, cuja raiz é o **mapeamento raiz
     de `knowledge/casa77.yaml` já carregado**, **permitida fora de `itera_sobre` e também
     dentro** de fragmento que o possua; e a **RELATIVA**, marcada por **`@` exatamente na
     posição inicial**, cuja raiz é o **item corrente** da coleção percorrida por `itera_sobre`,
     **permitida somente** em *binding* de fragmento que **declare** `itera_sobre` — **relativo
     sem `itera_sobre` é *FAIL-CLOSED* estrutural**. **A forma é sempre explícita na própria
     `str`**, e **o contexto jamais transforma silenciosamente absoluto em relativo**.
     **`C-4h` × `C-A1-S2` — ambas preservadas.** **`C-4h` permanece literal**: os *bindings* do
     item **PODEM** usar caminho relativo. **`C-A1-S2` disciplina** a disponibilidade e a
     semântica dos relativos durante a iteração, mas **NÃO torna todos os *bindings*
     obrigatoriamente relativos** — **absolutos e relativos podem coexistir** num mesmo fragmento
     com `itera_sobre`. **`C-A1-S1` permanece literal**: **seleção posicional continua
     PROIBIDA**.
     **Gramática.** `caminho ::= caminho_absoluto | caminho_relativo`; `caminho_absoluto ::=
     segmento ( "." segmento )*`; `caminho_relativo ::= "@" ( "." segmento )*`; `segmento ::=
     chave seletor?`; `seletor ::= "[" chave "=" literal "]"`; **chave** é `NOME` **exceto se
     composta exclusivamente por dígitos**; **literal** é `NOME`; `NOME` é um ou mais caracteres
     de `A-Z`, `a-z`, `0-9` e `_`. **Alfabeto semântico permitido, e nada além**: `A-Z`, `a-z`,
     `0-9`, `_`, `.`, `[`, `]`, `=` e `@`.
     **Canonicalidade semântica.** ***Whitespace* PROIBIDO**; **aspas como caracteres do valor
     PROIBIDAS**; ***escape* inexistente**; **Unicode não ASCII PROIBIDO**; **caixa
     significativa**; **zero normalização, `casefold`, coerção e tolerância**. São **inválidos**:
     `.` final; segmento vazio; seletor vazio; chave seletora vazia; literal vazio; **`@` fora da
     posição inicial**; e **dois seletores no mesmo segmento**.
     **YAML físico × valor semântico.** Como **`@` não pode iniciar um *plain scalar* YAML**, um
     caminho relativo **deverá ser serializado com *quoting*** no futuro arquivo do índice — por
     exemplo, de forma **sintética**, `caminho_yaml: "@.campo_exemplo"`. **As aspas pertencem à
     serialização YAML** e **NÃO** pertencem à `str` nem à gramática. **Aspas simples × duplas
     NÃO foram decididas**: ambas são apenas serialização quando produzem **a mesma `str`**.
     **Literal seletor é sempre `str`.** **Restrição normativa DELIBERADA do MVP**: conteúdo em
     `[A-Za-z0-9_]+`, **zero inferência** de inteiro, boolean, `null` ou outro tipo YAML, com
     comparação futura **literal, por `str`, sem coerção**.
     **Serialização dos identificadores no YAML comercial.** Um identificador estrutural usado
     por `caminho_yaml` **DEVE resultar em `str` depois do parsing** de `knowledge/casa77.yaml`.
     Se um futuro identificador introduzido por **`MD-18`** tiver conteúdo que, escrito como
     *plain scalar*, seja lido pelo *loader* como **número**, **boolean**, **`null`** ou outro
     tipo **não-`str`**, ele **DEVERÁ ser serializado com *quoting***. Exemplo **apenas
     sintético**: um identificador semântico `"2026"` precisa **permanecer `str`**, e não virar
     inteiro. **As aspas não fazem parte do identificador semântico.**
     **`knowledge/casa77.yaml` NÃO foi alterado** e **nenhum identificador novo foi criado**.
     **Chave exclusivamente numérica.** Uma chave YAML textual `"123"` **NÃO é semanticamente uma
     posição**; ainda assim, **a gramática do MVP deliberadamente NÃO a torna endereçável** —
     **chave composta apenas de dígitos é forma inválida**. Motivos, e apenas estes: **fechamento
     conservador**, **auditabilidade estática** e **compatibilidade com a materialização vigente
     de `C-A1-S1` em `E1`**. **Não se escreve nem se lê daqui que "chave numérica = posição".**
     **Seletor.** Forma `[chave=literal]`, **no máximo um por segmento**, permitido em **caminho
     absoluto**, **caminho relativo** e **`itera_sobre` absoluto**. **Proibidos**: `[0]`,
     posição, `first`, `last`, *fallback*, busca parcial, *substring*, similaridade e inferência.
     Resolução: **zero *matches* → *FAIL-CLOSED***; **um → continua**; **mais de um →
     *FAIL-CLOSED***.
     **`@` isolado.** É **caminho relativo válido** e significa **o próprio item corrente**,
     mantendo **expressável** a futura iteração sobre coleção de escalares. **Não se afirma que o
     corpus atual utilize esse caso.**
     **`itera_sobre` — mínimo inseparável.** É `str`; usa a **forma ABSOLUTA** da mesma
     gramática-base; **`@` é PROIBIDO** nele; precisa **resolver para coleção**; admite
     **seletores estruturais**; **mapa, escalar ou `null` como terminal é *FAIL-CLOSED*
     estrutural**; **não é `C-7`**; e **o item atual torna-se a raiz dos *bindings* relativos**.
     **NÃO foram decididos**: ordem; coleção vazia; composição textual; repetição de
     *placeholder*; propagação de erro entre itens; execução operacional.
     **Três responsabilidades distintas, nenhuma implementada.** **Parser da gramática** — sem
     acessar o YAML factual — valida sintaxe, alfabeto, absoluto × relativo, seletor,
     canonicalidade e chave numérica não endereçável. **Validação estrutural do índice** — sem
     ler o YAML factual — valida que o **relativo só ocorre em fragmento com `itera_sobre`** e
     que **`@` é proibido no próprio `itera_sobre`**. **Resolver** — contra o YAML **já
     carregado** — valida existência da chave, tipo intermediário, seletor sobre lista, **zero /
     um / múltiplos *matches*** e `itera_sobre` terminando em coleção.
     **Terminal.** Ao alcançar o nó terminal, a **resolução é SUCESSO** e o **valor é devolvido
     como está** — escalar, lista, mapa ou `null`. A **admissibilidade posterior** pertence a
     **`C-5`**, **`C-6`** e **`C-7`**, e **nenhum juiz adicional de tipo terminal foi criado**.
     **`C-7` preservada, NÃO reaberta e NÃO materializada.** **Chave inexistente ≠ `null`**;
     **atravessar `null` no meio é falha estrutural**; **terminal `null` significa caminho
     resolvido**, e o tratamento pertence a **`C-7`**; **zero ou múltiplos *matches* são falha de
     caminho**; a estrutura `pendente` pertence a **`C-7`** **somente após** resolução
     apropriada; e **o resolver não lê chaves irmãs por conveniência**.
     **`ASSERTIVA` / `RENDERIZADO` e `RUNTIME_AUTORITATIVO`.** A **mesma** gramática vale para
     `RENDERIZADO` e `ASSERTIVA` de origem `YAML`, com a diferença ocorrendo **depois da
     resolução** — **nenhuma gramática paralela**. **`RUNTIME_AUTORITATIVO` continua PROIBINDO
     `caminho_yaml`** e usando **apenas** `fato_runtime`.
     **`E1` inalterado.** `src/casa77_sdr/response_index.py` **continua INALTERADO**: `E1` valida
     a **estrutura básica** e **parte** da proibição posicional, e **NÃO fecha a gramática
     completa**. A futura materialização **poderá subsumir logicamente** parte dessas validações,
     mas **nesta entrega nada foi removido, nada foi alterado, nenhum teste foi tocado e nenhuma
     responsabilidade foi migrada**.
     **Categorias de *FAIL-CLOSED* — apenas CONCEITUAIS.** **Sintaxe**: forma inválida;
     referência não endereçável/posicional. **Estrutura do índice**: relativo sem `itera_sobre`;
     `@` em `itera_sobre`. **Resolução**: segmento inexistente; tipo estrutural incompatível;
     zero *match*; múltiplos *matches*; `itera_sobre` que não resolve para coleção. **NÃO foram
     definidos** classe Python, exceção concreta, mensagem, herança, função, módulo, API nem
     precedência técnica concreta.
     **Exemplos SINTÉTICOS.** Todos os exemplos do bloco usam **nomes e identificadores
     INVENTADOS** — `bloco_exemplo.colecao_exemplo[id=item_exemplo].campo_exemplo`, `@.campo_exemplo`,
     `@` —, e **nenhum identificador, valor, preço, capacidade, horário ou condição comercial
     real de `knowledge/casa77.yaml` é reproduzido**.
     **Evidência estrutural sanitizada do *snapshot* — EVIDÊNCIA, NÃO NORMA.** O YAML vigente é
     **compatível** com a gramática; há **5** coleções de mapas, das quais **4** possuem
     **identificador estrutural utilizável** e **1 não possui**; há **12** listas de escalares; e
     **nenhum *binding* aprovado atual exige `itera_sobre`**. **Nenhum valor, identificador real,
     preço, capacidade, horário ou condição comercial foi registrado**, e **o *snapshot* não
     altera norma**.
     **Testes.** **NENHUM `pytest` FOI EXECUTADO NESTA ENTREGA**, porque **zero código, zero
     teste e zero `knowledge/**` mudaram**. A **baseline registrada permanece `4594 passed` /
     Python 3.14.5**, sob **`-W error`**, **evidência da entrega funcional do PR #127** — e
     **nenhuma execução nova é alegada aqui**. A **entrega funcional de código mais recente
     continua sendo a composição total de status** (PR #127).
     **Estado após esta micro-arbitragem.** **Gramática de `caminho_yaml` = ARBITRADA
     DOCUMENTALMENTE / NÃO MATERIALIZADA**; **índice físico INEXISTENTE**; **parser
     INEXISTENTE**; **resolver INEXISTENTE**; ***placeholder* ABERTO**; **`hora` = pendência
     separada**; **`C-7` NÃO MATERIALIZADA**; **`C-A1-ST6`–`C-A1-ST10` NÃO satisfeitas**;
     **`C-11` NÃO migrada**; **`C` continua ARBITRADA / NÃO MATERIALIZADA**; **3B.8 INEXISTENTE**.
     **Próxima ação.** **Retornar ao GPT para auditoria da micro-arbitragem integrada à PR antes
     de qualquer planejamento técnico posterior.** **Nenhuma implementação foi eleita**, e
     ***placeholder*, parser, resolver, índice, `C-7` e `hora` NÃO foram iniciados**.
     **Relação com os itens anteriores.** **Os itens 87 a 106 permanecem corretos como registro
     do momento em que foram escritos.** Este item 107 **não os reescreve**; ele registra o
     estado **posterior**. Em particular, todos os registros anteriores que afirmam que a
     **gramática de `caminho_yaml` estava ABERTA** — inclusive **`C-A5-X3`**, **`GR7`** e
     **`PM12`** em `docs/07`, e as atualizações datadas e itens antigos deste documento —
     **permanecem corretos para o momento em que foram escritos** e **não foram alterados**.

108. **O PARSER PURO DA GRAMÁTICA DE `caminho_yaml` ESTÁ INTEGRADO À `main` PELO PR #131.**
     **ESTE ITEM 108 É REGISTRO DOCUMENTAL. NÃO É "SUBETAPA 108", NÃO É `C15`, NÃO É `E15`, NÃO
     É `C-A6`, NÃO É IDENTIFICADOR NORMATIVO E NÃO CRIA A 3B.8** — a **3B.8 continua
     INEXISTENTE**, e a **3B.7 continua a última subetapa numerada**. Ele registra
     **exclusivamente** a integração funcional da PR #131.
     **Integração.** **PR #131** — **commit funcional
     `cee95ebb6a725c3b91595589591fefa650d64196`** (`feat: add caminho_yaml parser`, **sem body,
     sem trailer**), **parent `51fa44c4a9f5b65505f7668c1ce05e8b8f97dd68`**, **merge commit
     `6ae5cd829bb6eb9f4acfc60a061ee9b7e6d36180`** (merge commit **normal**, dois parents:
     `51fa44c4a9f5b65505f7668c1ce05e8b8f97dd68` e
     `cee95ebb6a725c3b91595589591fefa650d64196`; **zero squash, zero rebase, zero auto-merge**),
     branch de origem `feat/caminho-yaml-parser`, **preservada**. **A `main` passou de
     `51fa44c4a9f5b65505f7668c1ce05e8b8f97dd68` para
     `6ae5cd829bb6eb9f4acfc60a061ee9b7e6d36180`.**
     **Escopo.** **Dois arquivos novos** — `src/casa77_sdr/response_yaml_path.py` (**+330**) e
     `tests/test_response_yaml_path.py` (**+1007**) —, **2 arquivos, +1337 / −0**, **zero
     arquivo preexistente alterado**, **zero `docs/**`**, **zero `knowledge/**`**, **zero
     `prompts/**`**, **zero `CLAUDE.md`**, **zero configuração**, **zero dependência**, **zero
     alteração de `casa77_sdr/__init__.py`** e **zero alteração de
     `src/casa77_sdr/response_index.py`**.
     **API.** Módulo `casa77_sdr.response_yaml_path`. Fronteira pública
     **`analisar_caminho_yaml(caminho: str) -> tuple[bool, tuple[tuple[str, tuple[str, str] | None], ...]]`**,
     com **um único parâmetro** e **sem default**. **Exceção pública única
     `CaminhoYamlInvalido`**. **`__all__` de exatamente dois nomes** —
     `["CaminhoYamlInvalido", "analisar_caminho_yaml"]`. **Sem DTO**, **sem dataclass**, **sem
     `NamedTuple`**, **sem `Enum`** e **sem export pelo package root**.
     **Retorno estruturado.** `(relativo, segmentos)` — a **decomposição imutável já
     validada** —, com `relativo` **`False`** para **absoluto** e **`True`** para **relativo**, e
     `segmentos` como `tuple` de pares `(chave, seletor)`, sendo `seletor` igual a **`None`** ou
     ao par `(chave_seletora, literal)`. A saída contém **somente `bool`, `str`, `tuple` e
     `None`** — **zero `dict`**, **zero `list`**, **zero estrutura mutável**. A decomposição
     permite que a futura validação contextual e o futuro resolver a consumam **sem reparsear a
     gramática**.
     **Gramática materializada.** **Absoluto sem marcador**, com raiz no mapeamento raiz do
     YAML; **relativo marcado por `@`** exatamente na posição inicial, com raiz no item corrente
     de `itera_sobre`; **`@` isolado devolve `(True, ())`**, sem inventar segmento; **seletor
     `[chave=literal]`, no máximo um por segmento**; **chave exclusivamente numérica é NÃO
     ENDEREÇÁVEL** — tanto **chave de segmento** quanto **chave seletora** —, **sem** que isso
     afirme que "chave numérica = posição"; e **literal seletor exclusivamente numérico é
     PERMITIDO**, porque o literal é **sempre semanticamente uma `str`** (**`CY7`**). A entrada é
     exigida como **`str` exata**: **subclasse de `str` é recusada antes de qualquer leitura**.
     **Canonicalidade estrita** recusa `str` vazia, *whitespace*, aspas, `\`, `/`, `-`, `:`,
     `*`, Unicode não ASCII, `.` inicial, `.` final, `..`, segmento vazio, seletor vazio, chave
     seletora vazia, literal vazio, `=` ausente, `[` sem `]`, `]` sem abertura, conteúdo após `]`
     no mesmo segmento, **dois seletores no mesmo segmento**, **`@` fora da primeira posição** e
     `@@`.
     **Falhas.** **Três** categorias fechadas — **`tipo_invalido`**, **`forma_invalida`** e
     **`chave_nao_enderecavel`** — e **seis** localizadores semânticos fechados — **`caminho`**,
     **`segmento`**, **`seletor`**, **`chave`**, **`chave_seletora`** e **`literal`**. A
     mensagem tem a forma **`<categoria>: <localizador>`** e **não ecoa o conteúdo recebido**:
     zero caminho bruto, fragmento da entrada, caractere ofensor, `repr`, tipo concreto,
     posição, índice, *offset*, comprimento ou cardinalidade. **Precedência fixa** — decisão
     técnica local, **não** identificador normativo novo de `C`: tipo da entrada → caminhada da
     esquerda para a direita → por chave sintaticamente completa, **forma antes de
     endereçabilidade** → a **primeira** violação encerra → **zero acumulação** → **zero retorno
     parcial**.
     **Pureza.** Import único `from __future__ import annotations` — **zero `re`**, `unicodedata`,
     YAML, JSON, I/O, *filesystem*, `open`, `pathlib`, `os`, `locale`, rede, LLM, relógio,
     calendário, variável de ambiente, aleatoriedade, banco, cache, logging, dependência interna,
     dependência externa, `try`/`except`, `raise from`, `eval`/`exec`, `assert`,
     `global`/`nonlocal`, `dict`, `set` e **estado mutável de módulo**. **Zero fato comercial**:
     o módulo **não lê YAML**, **não lê índice** e **não conhece dado comercial algum**; a
     entrada **não é alterada** e chamadas repetidas produzem **exatamente** o mesmo resultado.
     **Alcance exato — SOMENTE a linha 1 de `CY13`.** **Linha 1 — parser da gramática =
     MATERIALIZADA**, via `src/casa77_sdr/response_yaml_path.py`. **Linha 2 — validação
     estrutural contextual = NÃO MATERIALIZADA**: **ainda não existe** componente que valide
     **relativo somente em fragmento com `itera_sobre`** nem **`@` proibido no próprio
     `itera_sobre`**. **Linha 3 — resolver = NÃO MATERIALIZADA**: **ainda não existe**
     componente que percorra o YAML, resolva chaves, execute seletores, determine **zero / um /
     múltiplos *matches*** ou devolva terminal factual.
     **Testes.** **Baseline anterior `4594 passed`**; **direcionado novo `147 passed`**;
     **regressão completa `4741 passed`** — delta **+147**, **`4594 + 147 = 4741`** —, em
     **Python 3.14.5**, sob **`-W error`**, com **zero failures, zero errors e zero warnings** e
     **nenhum teste preexistente alterado, removido ou pulado**. **As proveniências são
     distintas**: a **baseline `4594 passed` foi medida ANTES de qualquer edição, sobre a base
     `51fa44c4a9f5b65505f7668c1ce05e8b8f97dd68`** — ela **NÃO** foi reexecutada no head
     funcional imediatamente antes do merge —, enquanto o **direcionado `147 passed`** e a
     **suíte completa `4741 passed`** foram medidos **sobre a implementação funcional da PR
     #131**, isto é, sobre os bytes que vieram a ser exatamente os blobs integrados, e **foram
     reexecutados com os mesmos números imediatamente antes do merge**. **A suíte é
     inteiramente SINTÉTICA** e **nenhum teste lê o corpus versionado**. **Estes números são
     evidência da ENTREGA FUNCIONAL do PR #131, e NÃO
     desta reconciliação: NENHUM `pytest` FOI EXECUTADO AQUI**, porque **zero código, zero teste
     e zero `knowledge/**` mudaram**.
     **Checks.** A PR #131 e o merge commit `6ae5cd829bb6eb9f4acfc60a061ee9b7e6d36180` possuem
     **zero *statuses*** e **zero *workflow runs*** — **AUSÊNCIA DE CI/CHECKS — NÃO FALHA DE
     CI**. Nenhum CI foi criado por esta reconciliação.
     **Limites.** A PR #131 **NÃO**: implementa a validação contextual de `itera_sobre`;
     implementa o resolver; lê YAML; cria índice; executa a bijeção física; implementa
     *bindings*; implementa `ASSERTIVA`; define *placeholder*; define `hora`; resolve **C-7**;
     cria *renderer*; integra *runtime*; migra a autoridade de status; satisfaz
     **`C-A1-ST6`**–**`C-A1-ST10`**; nem cria `C15`, `E15`, `C-A6` ou a **3B.8**. **`C-7`
     continua NÃO MATERIALIZADA** e **não foi reaberta**;
     `knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE**; ***placeholder*
     continua ABERTO**; **`hora` continua pendência normativa separada**; **`C-11` NÃO migrou** e
     a **autoridade de status continua no Markdown aprovado**. **ANALISAR O CAMINHO NÃO É
     RESOLVER E NÃO É MATERIALIZAR `C`** — **`C` continua ARBITRADA / NÃO MATERIALIZADA**.
     **Entrega funcional mais recente.** **O parser puro de `caminho_yaml` é agora a ENTREGA
     FUNCIONAL DE CÓDIGO MAIS RECENTE INTEGRADA**, com **commit funcional corrente
     `cee95ebb6a725c3b91595589591fefa650d64196`** e **baseline `4741 passed` em Python 3.14.5**.
     A **composição total de status (PR #127) passa a histórico funcional imediatamente
     anterior**, com o seu registro **preservado**. **Ela NÃO recebe denominação `C15`** e
     **nenhuma numeração funcional nova foi criada**.
     **Próxima ação.** **Retornar ao GPT após a integração desta reconciliação para nova
     auditoria e priorização.** **Nenhuma próxima microentrega técnica é eleita** neste item, e
     **não** se afirma que a próxima entrega será a **validação contextual**, o **resolver**,
     ***placeholder***, **`hora`**, **`C-7`** ou o **índice**.
     **Relação com os itens anteriores.** **Os itens 87 a 107 permanecem corretos como registro
     do momento em que foram escritos.** Este item 108 **não os reescreve**; ele registra o
     estado **posterior**. Em particular, o **item 106** continua correto ao registrar a
     composição total de status como a entrega funcional mais recente **à época**, e o **item
     107** continua correto ao registrar a gramática de `caminho_yaml` como **arbitrada
     documentalmente com parser inexistente naquele momento** — o que **continua verdadeiro como
     registro daquele momento**, e cuja **linha 1 de `CY13` é agora materializada em código** por
     esta entrega.

## Arbitragens

Decisões de governança. Não criam marco funcional nem código. A coluna Decisão informa o
estado de ciclo de vida de cada arbitragem, incluindo a evidência de integração quando ela
já alcançou a `main`.

| # | Arbitragem | Decisão | Evidência |
|---|---|---|---|
| S2-D8 | **Contrato de detecção e classificação de pendências, e de cobertura de resposta aprovada** (`docs/07-arquitetura-motor-respostas.md` §2.2, §4.4, §4.4.1, §5, §6.3, §7, §8.2 e §12, item 10; `docs/06-maquina-de-estados.md` §1.2, §1.3, §2.2, §3, §4.3, §9 e §11) | **ARBITRADA / NÃO MATERIALIZADA.** Fecha **documentalmente** o contrato do produtor de `E09`, de `pendencia_impeditiva` e de `resposta_aprovada_disponivel`, em **dois eixos** — **A**, de qualificação, e **B**, de resposta. **Não cria componente, estado, evento, transição, condição, critério, ação, efeito paralelo, inércia, pendência nem subetapa**, e **não implementa código nem altera testes** — `src/`, `tests/`, `knowledge/` e `prompts/` permanecem **fora** dela. **Não cria marco funcional.** **Não materializa AJ2**, **não materializa C** e **não fecha `N-b-RES2`**, que **continua ABERTO**. As condições **2** e **4** de `docs/07` §4.4 passam a ter **produtor conceitual**; a **condição 8 continua NÃO ATRIBUÍDA**. Escopo abaixo | **INTEGRADA À `main` pelo PR #59** — commit documental `6bbd1185d3a31cc3b307ce3c7c2abe67085e7c66`, merge `eff50138ce9e10ff71f34920077b843bbc201264`, branch de origem `docs/arbitragem-s2-d8`. Entrega **exclusivamente documental**, em `docs/00-estado-atual.md`, `docs/06-maquina-de-estados.md` e `docs/07-arquitetura-motor-respostas.md` — **673 adições, 36 remoções**. Base: `111e5c31826ba839ff4e0599b45bc98d34620128`. **A integração documental não materializa S2-D8** |
| AJ2 | **Origem semântica do assunto de `PerguntaComercial`** (`docs/07-arquitetura-motor-respostas.md` §6.3, §8.2 e §12, item 20) | **ARBITRADA / MATERIALIZADA na fronteira determinística.** Micro-arbitragem **exclusivamente documental** que **ESTENDE FORMALMENTE N-b**: `PerguntaComercial` passa conceitualmente de **dois** para **três** campos, com **`assunto`** obrigatório do enum fechado **`AssuntoComercial`** (**54** valores). **Não cria componente, estado, evento, transição, condição, critério, pendência nem subetapa**, e **não implementa código nem altera testes** — `src/`, `tests/`, `knowledge/` e `prompts/` permanecem **fora** dela. **Não cria marco funcional.** **À época da arbitragem o delta NÃO estava materializado** e o **PR #55 era o último funcional**; o delta foi **materializado depois**, pelo **PR #61**, na **fronteira determinística** (`docs/07` §6.3, **M-AJ2-1**–**M-AJ2-9**). Escopo abaixo | **INTEGRADA À `main` pelo PR #58** — commit documental `2dea157abee04407791ade56017b6fe159e91c74`, merge `111e5c31826ba839ff4e0599b45bc98d34620128`, branch de origem `docs/aj2-assunto-pergunta-comercial`. Entrega **exclusivamente documental**, em `docs/07-arquitetura-motor-respostas.md` (§6.3, §8.2 e §12, item 20) e `docs/00-estado-atual.md` — **402 adições, 18 remoções**. Base: `89458bb7efea23d8f7889a0b5ab076a1d0c7f130`. **Aquela integração era documental e não materializava o delta.** **MATERIALIZAÇÃO FUNCIONAL POSTERIOR pelo PR #61** — commit funcional `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`, merge `5a722a5cc648149330362434694e7e76a40c1b57`, branch `feat/materializar-aj2-assunto`, **762 adições / 28 remoções**, baseline **`1215 passed`** / Python 3.14.5 |
| C-A1 | **Fechamento do contrato de materialização de C** (`docs/07-arquitetura-motor-respostas.md` §2.3 e §12, item 19) | **ARBITRADA DOCUMENTALMENTE.** Micro-arbitragem **exclusivamente documental** e **posterior** a **C**, que **refina a leitura futura** do contrato de materialização: equivalência de *template* **`C-15a`–`C-15e`**, refinamentos de **C-6** (`inteiro_agrupado`, `simbolo_moeda`, `hora`), **convenção final do formato `lista`**, preservação de **C-5** com **sete rejeições explícitas**, **proibição de seleção posicional** em coleção, **unidade de bijeção no fragmento emitível**, **canonicalização e migração de status**, **prioridade de modelagem**, regra de **prosa não duplicada**, **auditoria obrigatória de consumidores**, alvos de modelo **`MD-1`–`MD-18`** — com **`MD-3`** e **`MD-16`** **REMOVIDOS** — e a matriz **`G1`–`G14`**. **`C-1`–`C-14` permanecem registro histórico e não são reescritas.** **Não cria componente, responsabilidade, condição, estado, evento, transição, ação, critério, enum, erro, cenário nem subetapa**, e **não implementa código nem altera testes** — `src/`, `tests/`, `knowledge/` e `prompts/` permanecem **fora** dela. **Não cria marco funcional.** **Não cria o índice, não altera o YAML, não converte respostas em *templates* e não muda status real.** **C permanece ARBITRADA / NÃO MATERIALIZADA**; **C-A2** fica **ABERTA**. Escopo abaixo. **`C-A1-M4` — auditoria read-only de consumidores — foi EXECUTADA e APROVADA depois**, contra `origin/main` `118054575e7f7560a1c37ca430bdedd15eddc817`, **sem executar alvo `MD` algum** (Próxima ação, itens 36 e 37) | Entrega **exclusivamente documental**, em `docs/07-arquitetura-motor-respostas.md` (§2.3 e §12, item 19) e `docs/00-estado-atual.md`. Branch de origem: `docs/arbitragem-c-a1`. Base: `4ba1cdfe4397e90692efdec06357cb079e44ca8a`. **Evidência de `C-A1-M4`**: relatório sanitizado **não versionado**, fora do repositório, SHA-256 `cdca7d40ce672c924bf2f13318f51e2a6dd87990abe56c159b1de747bbc51e1e` |
| C-A2 | **Fatos e conteúdo humanos residuais da materialização de C** (`docs/07-arquitetura-motor-respostas.md` §2.3, bloco **"Micro-arbitragem C-A2"**, e §12, item 19 — nota temporal) | **ARBITRADA DOCUMENTALMENTE.** Micro-arbitragem **exclusivamente documental** e **posterior** a **C** e a **C-A1**. **Fecha** os **fatos humanos `A1`–`A4`**; **registra estruturalmente** o **conteúdo humano `B1`–`B16`** como **APROVADO HUMANAMENTE / AINDA NÃO APLICADO**, **sem o corpo literal de texto algum**; fixa a **decisão `B16`** — `R05` passa a ter os fragmentos `F1`, `F2` e `F3`, **permanecendo um único `Rxx`** —; refina o *binding* com **`origem` OBRIGATÓRIA**, **sem valor padrão**, do vocabulário fechado **`YAML`** / **`RUNTIME_AUTORITATIVO`**, **ausência = FAIL-CLOSED** e **exatamente um referente**; fecha o **vocabulário runtime** (`consulta_calendario_valida`, `data_disponivel`) **somente por `ASSERTIVA`**; registra o **escopo do fato runtime**; fecha a tabela **`MD-1`–`MD-20`** — **`MD-1` SUPERADO**, **`MD-3`/`MD-16` REMOVIDOS**, **`MD-18` GENERALIZADO**, **`MD-19`/`MD-20` NOVOS**, **`MD-20` MÍNIMO** —; e enumera **`FE-1`–`FE-14`**, com **`FE-11` dividida** em **`FE-11a`** e **`FE-11b`**. **`C-1`–`C-14` e todo o bloco `C-A1` permanecem registro histórico e não são reescritos.** **Não cria componente, responsabilidade, estado, evento, transição, condição de ciclo, motivo de `E09`, critério, enum, erro, cenário nem subetapa**, e **não implementa código nem altera testes** — `src/`, `tests/`, `knowledge/` e `prompts/` permanecem **fora** dela. **Não cria marco funcional.** **Não aplica texto algum, não executa alvo `MD`, não aplica `FE` e não escolhe provedor de calendário.** **C permanece ARBITRADA / NÃO MATERIALIZADA.** Escopo abaixo | **ENTREGA 1 — documental**, em `docs/07-arquitetura-motor-respostas.md` (§2.3 e §12, item 19) e `docs/00-estado-atual.md`. Branch de origem: `docs/arbitragem-c-a2`. Base: `a60c57dbf029913a623ad87bb24795fe333cdc3f`. **INTEGRADA À `main` pelo PR #64** — commit `294a11a1c170815063764f1d49ae0d831b72d359`, merge `25b867f1c6cb4d2d00cd49ea60361c82a6e98f6f`. **A ENTREGA 2 — aplicação do conteúdo e das `FE` — foi executada depois**, em entrega própria, na branch `docs/aplicar-conteudo-c-a2`: **conteúdo B APLICADO à fonte de respostas**, **corpus 37 fragmentos / 30 `Rxx`**, **`FE-1`–`FE-10`, `FE-11a` e `FE-12`–`FE-14` APLICADAS** e **`FE-11b` RETIDA atrás de `C-A1-M4`**, **sem alterar `knowledge/casa77.yaml`**, **sem executar alvo `MD`** e **sem materializar C**. **A ENTREGA 2 está INTEGRADA À `main` pelo PR #65** — commit `c2883d2fad32638d1e15a616a2b37f577abf3e42`, merge `fbe768a14457241245c73f4cbe8ef93e869e7fb3`, **seis** arquivos, **219 adições / 74 remoções**. **Documental/comportamental**: **não altera `src/` nem `tests/`** e **não cria marco funcional** |
| C-A5 | **Identidade física do fragmento emitível** (`docs/07-arquitetura-motor-respostas.md` §2.3, bloco **"Micro-arbitragem C-A5"**) | **ARBITRADA DOCUMENTALMENTE / NÃO MATERIALIZADA.** Micro-arbitragem **exclusivamente documental** e **posterior** a **C**, **C-A1**, **C-A2**, **C-A3** e **C-A4**, que fecha **exclusivamente** a matéria antes explicitamente **não decidida** — a **identidade física do fragmento** — e **nenhuma outra**. Fixa: a **unidade emitível física futura** como **bloco de citação contíguo** dentro de `## Rxx` (**`C-A5-U`**); o **marcador** `<!-- fragmento: <id> -->` na **linha imediatamente anterior** ao bloco, a **gramática fechada do `id`** (**`F`** + inteiro decimal ASCII maior que zero, sem zero à esquerda), a **unicidade apenas dentro do `Rxx`** — **preservando literalmente `C-2h`** — e a **identidade declarada, nunca derivada** (**`C-A5-I`**); a **identidade canônica `<Rxx>/<id>`**, **derivada e nunca armazenada**, **sem campo novo** no futuro índice (**`C-A5-T`**); a **ativação diferida** (**`C-A5-M`**); e os **limites e falhas futuras** (**`C-A5-X`**). **`C-1`–`C-15`, `C-A1`, `C-A2`, `C-A3` e `C-A4` permanecem registro histórico e não são reescritos.** **ARBITRA A REPRESENTAÇÃO FUTURA E NÃO A APLICA AO CORPUS ATUAL**: **zero marcador inserido**, **zero `id` atribuído**, **zero tabela dos 37 produzida ou aprovada**, **`knowledge/**` intacto**, **ausência de marcador NÃO é erro** e **nenhum bloco existente fica fail-closed**. **Não cria componente, responsabilidade, condição, evento, estado, transição, ação, erro, cenário, status, formato, predicado nem subetapa**, **não implementa código nem altera testes** e **não cria marco funcional** — **a 3B.8 continua inexistente**. **Não decide** propagação de status ao fragmento, mapeamento de `PARCIAL`, sintaxe de *placeholder*, gramática de `caminho_yaml`, formato `hora` nem **C-7**. **C permanece ARBITRADA / NÃO MATERIALIZADA** e a **autoridade de status não migra** (**C-11**). Escopo abaixo | Entrega **exclusivamente documental**, em `docs/07-arquitetura-motor-respostas.md` (§2.3, bloco **"Micro-arbitragem C-A5"**, **puramente aditivo**) e `docs/00-estado-atual.md` (item **87**). Branch de origem: `docs/c-a5-identidade-fragmento`. Base: `1d19ed1e5a9469f3c9ad86fb63146a9657bd2a1d`. **Evidência estrutural read-only**: **30 `Rxx`**, **37 blocos**, **24 com um fragmento**, **6 multi-fragmento**, **zero comentário HTML** e **zero marcador aplicado** — **COMPATIBILIDADE ESTRUTURAL 37/37**, com **MAPEAMENTO DE IDENTIDADE NÃO PRODUZIDO / NÃO APROVADO** e **`R09` em PENDÊNCIA DE MAPEAMENTO HUMANO**. **NENHUM `pytest` executado**; baseline **`2707 passed`** preservada como a última confirmada anteriormente |
| C | **Contrato do índice estruturado de respostas aprovadas** (`docs/07-arquitetura-motor-respostas.md` §2.3 e §12, item 19) | **ARBITRADA / NÃO MATERIALIZADA.** Fecha **documentalmente** o contrato do futuro índice `knowledge/indice-respostas-aprovadas.yaml`, **sem criá-lo** e **sem criar componente, estado, evento, transição, condição, critério, pendência ou subetapa**. **Não implementa código, não converte `knowledge/respostas-aprovadas.md`, não remove status do Markdown e não altera `knowledge/`, `src/` ou `tests/`** — esses diretórios permanecem **fora** desta arbitragem. **Não cria marco funcional.** A **materialização do índice permanece futura** e **não é autorizada** por ela. **PRIMEIRA MICROENTREGA FUNCIONAL POSTERIOR — `E1`**: o **validador estrutural fail-closed** do **futuro** índice foi **materializado e integrado depois**, pelo **PR #84**, em `src/casa77_sdr/response_index.py`. **`E1` NÃO materializa `C`**: ela valida a **forma** de uma estrutura já parseada, **sem criar o índice**, **sem loader**, **sem ler `knowledge/**`**, **sem converter o Markdown**, **sem bindings reais**, **sem bijeção 37/37**, **sem C-15**, **sem renderizar** e **sem avaliar `ASSERTIVA` contra dados reais**. **SEGUNDA MICROENTREGA FUNCIONAL POSTERIOR — carregador *fail-closed***: integrado pelo **PR #86**, em `src/casa77_sdr/response_index_load.py`, expondo `IndiceIlegivel` e `carregar_indice(path)`. Ele **lê e recusa** um artefato **explicitamente apontado** — UTF-8, `yaml.SafeLoader`, chave duplicada recusada —, **delega toda a forma** a `validar_indice` e **não conhece caminho implícito** para o índice. **Carregar também NÃO materializa `C`.** **TERCEIRA MICROENTREGA FUNCIONAL POSTERIOR — comparador determinístico de equivalência textual de `C-15b`**: integrado pelo **PR #89**, em `src/casa77_sdr/response_equivalence.py`, expondo `EquivalenciaNaoDeterminavel` e `sao_textualmente_equivalentes(...)` sobre **duas `str` já em representação canônica** — **sem analisar Markdown**, **sem I/O** e **sem conhecer o índice**. **Comparar também NÃO materializa `C`.** **QUARTA MICROENTREGA FUNCIONAL POSTERIOR — formatadores determinísticos de apresentação pura de `C-6`**: integrada pelo **PR #91**, em `src/casa77_sdr/response_format.py`, expondo `FormatoInaplicavel` e as cinco funções puras de **`inteiro`**, **`inteiro_agrupado`**, **`simbolo_moeda`**, **`texto`** e **`lista`**. Elas **recebem valores já resolvidos**, devolvem **apresentação pura** e **não leem fonte alguma, não fazem I/O, não consultam *locale* e não conhecem consumidor**; o formato **`hora` NÃO foi materializado** e sua lacuna normativa **continua ABERTA**. **Formatar também NÃO materializa `C`.** **QUINTA MICROENTREGA FUNCIONAL POSTERIOR — avaliador determinístico booleano de `ASSERTIVA`**: integrada pelo **PR #93**, em `src/casa77_sdr/response_assertion.py`, expondo `AssertivaNaoAvaliavel` e `avaliar_assertiva(predicado, valor)` sobre o vocabulário fechado **`EH_VERDADEIRO`**/**`EH_FALSO`** e um **valor já resolvido**. Ela julga **somente o domínio booleano estrito**: valor fora dele é **NÃO AVALIÁVEL** e **nunca vira assertiva falsa**, **sem coerção e sem *truthiness***. Essa recusa é **delimitação técnica fail-closed daquela microentrega**, e **não** expansão de **`C-7`**; **nenhum domínio futuro de `ASSERTIVA` foi arbitrado**. **Avaliar também NÃO materializa `C`**, e **nenhum consumidor foi integrado.** **SEXTA MICROENTREGA FUNCIONAL POSTERIOR — verificador determinístico da correspondência bijetiva de `C-A1-B3` / `C-A1-B4`**: integrada pelo **PR #95**, em `src/casa77_sdr/response_bijection.py`, expondo `BijecaoInvalida` e `validar_bijecao(fragmentos_indice, unidades_markdown, correspondencias)` sobre **três domínios já fornecidos pelo chamador** — tokens opacos `str` **exata** e pares `tuple` **exata** de dois lados, comparados por **igualdade nativa exata de `str`**, **sem normalização, sem coerção, sem *parsing* e sem I/O**, **fail-closed** e com **precedência determinística**. Ela **não extrai fragmentos do índice**, **não extrai unidades do Markdown**, **não define identidade física de fragmento**, **não lê índice real**, **não prova completude dos domínios**, **não executa a bijeção física do corpus real** e **não satisfaz `C-A1-ST7` isoladamente** — **a completude dos domínios é pré-condição do chamador**. **Verificar a bijeção também NÃO materializa `C`**, e **nenhum consumidor foi integrado.** **SÉTIMA MICROENTREGA FUNCIONAL POSTERIOR — canonicalizador determinístico de rótulo de status já extraído**: integrada pelo **PR #97**, em `src/casa77_sdr/response_status.py`, expondo `StatusNaoCanonicalizavel` e `canonicalizar_status(rotulo)` sobre um **rótulo já extraído**. Ela traduz **somente as três linhas com tradução automática arbitrada** em `C-A1-ST1`–`C-A1-ST3` — `APROVADO` → `APROVADO`, `AGUARDA APROVAÇÃO` → `AGUARDA_APROVACAO` e `APROVADO com handoff obrigatório` → `APROVADO`, **sem transportar o sufixo de handoff** (C-2f, C-5.1) —, exigindo `str` **exata** (**subclasse recusada**), com **comparação literal**, **zero normalização**, **zero coerção**, **zero I/O** e validação **fail-closed** de precedência fixa. **`PARCIAL` continua sem tradução automática** e **continua exigindo mapeamento explícito no nível dos fragmentos emitíveis** (**C-A1-ST4**); **`BLOQUEADO` não recebeu mapeamento inventado** (**C-A1-ST5** trata de **nota interna**, que não cria fragmento nem status). Ela **não extrai rótulo nem fragmento do Markdown, não cria identidade física de fragmento, não cria nem lê o índice real, não resolve *bindings*, não executa a bijeção física, não prova completude do corpus, não satisfaz `C-A1-ST6`–`C-A1-ST10` e não migra a autoridade de status** — `knowledge/respostas-aprovadas.md` **continua a autoridade** (**C-11**). **Canonicalizar status também NÃO materializa `C`**, e **nenhum consumidor foi integrado.** **`C` permanece ARBITRADA / NÃO MATERIALIZADA** e o índice `knowledge/indice-respostas-aprovadas.yaml` **permanece INEXISTENTE**. Escopo abaixo | Entrega **exclusivamente documental**, em `docs/07-arquitetura-motor-respostas.md` (§2.3 e §12, item 19) e `docs/00-estado-atual.md`. Branch de origem: `docs/arbitragem-c-indice-respostas`. **MICROENTREGA FUNCIONAL POSTERIOR `E1` pelo PR #84** — commit funcional `02f1dd6621c31b90789c646bd8826e685f9ee019`, merge `95ed2ce4e9c54f9bdfb7b3f820e6f9e065cde24e`, branch `feat/c-e1-response-index-validator`, **dois arquivos novos**, **1343 adições / 0 remoções**, baseline **`1374 passed`** / Python 3.14.5. **Aquela integração materializa `E1`, NÃO `C`**. **SEGUNDA MICROENTREGA FUNCIONAL POSTERIOR pelo PR #86** — commit funcional `b2b11e2465c7f332747a806c80b629e995f0f5a6`, merge `9bf68b8fece9ea66c74509490ddf6e02a0aa6f31`, branch `feat/c-response-index-loader`, **três arquivos**, **1086 adições / 5 remoções**, baseline **`1436 passed`** / Python 3.14.5. **Aquela integração materializa o CARREGADOR, NÃO `C`** |
| AJ1 | **Representação e canonicalização determinística de N-b** (`docs/07-arquitetura-motor-respostas.md` §6.3, §8.2 e §12) | **APROVADA — INTEGRADA À MAIN.** Micro-arbitragem **exclusivamente documental** que fecha a **representação/canonicalização** da `Interpretacao` **antes** de qualquer materialização em código, **sem criar componente, estado, evento, transição, critério, campo, erro, cenário ou subetapa**. Aprovada pelo GPT e **integrada à `main`** pelo **PR #53** (**MERGED**). **AJ1 não reabriu N-b, não a implementou, não tornou a etapa 4 funcional e não criou produtor LLM** — seu contrato foi **materializado depois**, na parte determinística, pelo **PR #55**. **N-b permanece ARBITRADA e PARCIALMENTE MATERIALIZADA.** Escopo resumido abaixo | PR #53 — commit documental `d1137cf67c42eae37ec8e837a56350da6c7fbabe`, merge `2e9df1f4dfcd11903d410ba7a42ba12d86eb2b15`, branch de origem `docs/nb-aj1-canonicalizacao`. Alterou **exclusivamente** `docs/07-arquitetura-motor-respostas.md` — **156 adições, 1 remoção** |
| N-b | **Contrato global da interpretação da etapa 4** — a `Interpretacao` (`docs/07-arquitetura-motor-respostas.md` §6.3) | **APROVADA — INTEGRADA À MAIN.** Fecha **documentalmente** o contrato da **saída da etapa 4**, **sem criar componente, estado, evento, transição, critério ou campo**. Arbitragem documental **aprovada pelo GPT** e **integrada à `main`** pelo **PR #51** (**MERGED**). **Não implementa código** e **não cria marco funcional.** **ARBITRADA e PARCIALMENTE MATERIALIZADA**: a **fronteira determinística** foi integrada pelo **PR #55** (`src/casa77_sdr/interpretation.py`); o **produtor não determinístico / LLM**, **N-b-RES2** e a **integração operacional da etapa 4** continuam pendentes, e o `OrquestradorMotor` continua não implementado. Escopo resumido abaixo | PR #51 — commit documental `6f1cb6fe5ef12096117f1292225a761af5889025`, merge `85dbc709799f30c59a458c3ea8725fc072a15364`, branch de origem `docs/arbitragem-nb-interpretacao`. Alterou **exclusivamente** `docs/07-arquitetura-motor-respostas.md` — **365 adições, 8 remoções** |
| N-a | **Política de produção do conjunto elegível da etapa 3** (`docs/07-arquitetura-motor-respostas.md`) | **APROVADA — INTEGRADA À MAIN.** Fecha **documentalmente** a política de elegibilidade e recência que a etapa 3 aplica sobre os registros recuperados, **sem criar componente, estado, evento, transição ou critério**. Arbitragem documental **aprovada pelo GPT** e **integrada à `main`** pelo **PR #31** (**MERGED**). **Não implementa código**, **não implementa a persistência**, **não implementa o `OrquestradorMotor`** e **não cria marco funcional.** Escopo abaixo. | PR #31 — commit documental `43774af58877e3de3ecfda32cf0384a9fd047693`, merge `e8425410a7ced47c8d186bfceeea1cdd70f73b0c`, branch de origem `docs/arbitragem-na-contexto-elegivel`; alterações **exclusivamente** em `docs/07` (`+247 / -12`: §5 etapas 3 e 13, §6.2 subseção N-a completa, §7.1 S9–S11 e classe I, §12 item 11 e novo item 18) |
| R-I | **Projeção do identificador validado** para a etapa 5 (`docs/07-arquitetura-motor-respostas.md`) | **APROVADA — INTEGRADA À MAIN.** Micro-arbitragem que fixa `id_atendimento_validado` como **insumo próprio e opaco** do `ResolvedorIdentidade`, com pré-condições estruturais **P-I1–P-I5**, obrigações do produtor **N-I-1–N-I-4** e a fronteira parcial **N-a-F1** — **sem criar estado, evento, transição, critério ou campo de saída**. Arbitragem documental **aprovada pelo GPT** e **integrada à `main`** pelo **PR #27** (**MERGED**). **Não implementa código** e **não cria marco funcional.** Escopo abaixo. | PR #27 — commit documental `713f473c9b9fcae75f73aa0ffadc84dd31e81caa`, merge `4bb202e0bb68f67a8d66e487d85ec7978ea8cd95`, branch de origem `docs/ri-identificador-validado`; alterações **exclusivamente** em `docs/07` (`+117 / -9`: §4.1 linha do componente, §5 etapa 5, §6.1.1 N7 + N-I-1–N-I-4, §6.2 projeção + N-a-F1, §7.1 insumos, assinatura, P-I1–P-I5, efeito sobre a cascata, saída auditável e classes de erro, §8.2 R-I-K1–R-I-K15, §12) |
| R-H | **Fronteira do conjunto H / takeover humano** na resolução de identidade (`docs/07-arquitetura-motor-respostas.md`) | **APROVADA — INTEGRADA À MAIN.** Micro-arbitragem que fixa `ids_em_atendimento_humano` como **entrada própria e separada** do conjunto elegível, **fora** da política N-a, **sem criar estado, evento ou transição**. Arbitragem documental **aprovada pelo GPT** e **integrada à `main`** pelo **PR #25** (**MERGED**). **Não implementa código** e **não cria marco funcional.** Escopo abaixo. | PR #25 — commit documental `24835a8d6cca50a6f783c8b831ca2c924d2177a9`, merge `96a8ff98611fb9de75540ea98adad94166c65e8b`, branch de origem `docs/rh-fronteira-conjunto-h`; alterações **exclusivamente** em `docs/07` (§5 tabela de componentes, §5 etapas 3 e 5, §6.2 + regras H1–H6, §6.3, §7.1 insumos e assinatura conceitual, R5-P0, §7.1 classes de erro, §8.1, §8.2 cenários K-H1–K-H8) |
| R | Contrato de **resolução de identidade** do `ResolvedorIdentidade`, anterior à `MaquinaEstados` (`docs/06-maquina-de-estados.md` × `docs/07-arquitetura-motor-respostas.md`) | **APROVADA — INTEGRADA À MAIN.** Materializa o critério técnico de "mesmo evento × nova solicitação" (T36/T37), que até então era declarado futuro, **sem criar estado, evento ou transição**. Arbitragem documental **aprovada pelo GPT** e **integrada à `main`** pelo **PR #23** (**MERGED**). **Não implementa código** e **não cria marco funcional.** Escopo abaixo. | PR #23 — commit documental `6c848ea8d45e7f6e412cdd297e9ca68c1fa75a21`, merge `aeb446656fd11b91bb61164f29f9adca6959d4df`, branch de origem `docs/arbitragem-resolvedor-identidade`; alterações em `docs/06` (nota da §3, §4.5, §5 regra 12) e `docs/07` (§4.1, §5, §6.1.1, §6.2, §6.3, §6.4, §6.5, §7.1, §8.1, §8.2, §9, §12) |
| S3 | Arbitragem residual da `MaquinaEstados` (`docs/06-maquina-de-estados.md` × `docs/07-arquitetura-motor-respostas.md`) | **APROVADA — INTEGRADA À MAIN.** Fecha as ambiguidades residuais posteriores à S2 sem redesenhar a máquina: materialização de T04, precedência entre classes de `E08`, `T09 > T04`, `T32 > T35`, contrato semântico de ações, condição estruturada de T35, fronteira temporal da resposta aprovada e `CondicoesCiclo`. Arbitragem documental **aprovada pelo GPT** e **integrada à `main`** pelo **PR #18** (**MERGED**). **Não implementa código** e **não cria marco funcional.** Escopo abaixo. | PR #18 — head integrado `40841a3ef6ef00b83313d41e95c52c4f6c1045a8`, merge `ac49758771efe00596e27a9d8eec034d4c85df04`; commit documental principal `541aa765ac0e956620e3a78c19b38c0d24a40885`, a partir da branch `docs/s3-arbitragem-residual-maquina-estados`; alterações em `docs/06` (notas da §3, §4.2, §11) e `docs/07` (§4.1, §4.4, §4.5, §5) |
| A | Fronteira de Qualificação entre `docs/05-roadmap.md` e `docs/07-arquitetura-motor-respostas.md` | **ARBITRADA** (S1): o `Qualificador` permanece componente do motor e sua implementação pertence à Etapa 3B; a antiga Etapa 4 deixa de ser aberta como etapa autônoma e é absorvida pela 3B; as etapas 5 a 10 mantêm a numeração; o `Qualificador` precede a `MaquinaEstados`. O `Qualificador` foi **implementado na 3B.5** (PR #14) e a `MaquinaEstados` foi **implementada na 3B.6** (PR #21); a precedência entre os dois foi respeitada na ordem de entrega. | reconciliação documental de `docs/05`, `docs/07` §8.4/§9 e deste documento |
| S2 | Semântica de ciclo da `MaquinaEstados` (`docs/06-maquina-de-estados.md` × `docs/07-arquitetura-motor-respostas.md`) | **APROVADA — INTEGRADA À MAIN.** Arbitragem documental **aprovada pelo GPT** na auditoria da entrega e **integrada à `main`** pelo **PR #16** (**MERGED**), a partir da branch `docs/s2-arbitragem-maquina-estados`. **Não implementa código** e **não cria marco funcional.** Escopo abaixo. | PR #16 — head integrado `e4746d8b350b65388672ecfb5233a558031ff352`, merge `1a719546b922e0a89d30912de745046eb11849d9`; núcleo documental no commit `0be5a022d2b30b5cfa2bca501e77c06bed501419` — `docs/06` (§1.1, §2.2, §3, §4.1–§4.5, §9, §10, §11) e `docs/07` (§4.1, §5, §7.2, §8.1, §9, §12) |

### Arbitragem S2-D8 — escopo arbitrado, NÃO materializado

Arbitragem sobre o **contrato de detecção e classificação de pendências** e sobre a
**determinação de cobertura de resposta aprovada**, ambas **antes da etapa 7** do pipeline.
Entrega **exclusivamente documental**, materializada em
`docs/07-arquitetura-motor-respostas.md` §4.4.1 — com reflexos em §2.2, §4.4, §5, §6.3, §7,
§8.2 e §12, item 10 — e em `docs/06-maquina-de-estados.md` §1.2, §1.3, §2.2, §3, §4.3, §9 e
§11.

Contrato aprovado:

| # | Item |
|---|---|
| 1 | **Dois eixos.** **A — qualificação**: "existe indisponibilidade válida na base que impede a classificação do evento **neste ciclo**?" — **independente** de `PerguntaComercial`. **B — resposta**: "existe cobertura aprovada e emitível para os assuntos **efetivamente consultados**?" — consome **somente** consulta `ALTA` e **nunca** usa o texto como chave semântica |
| 2 | **`Q1` — decisão do MVP.** Os campos exigidos **estruturalmente** pelo carregador continuam **pré-requisitos da base** e **não** viram pendência de S2-D8. Logo `knowledge.py`, `rules.py`, `qualification.py` e `state_machine.py` **não mudam**. No schema atual, `pendencia_impeditiva = True` **pode ser legitimamente inalcançável** — e isso **não elimina a condição 2** |
| 3 | **`Q2` — não autorizada e não recomendada para o MVP.** Permanece futura |
| 4 | **Regra impeditiva `IMP-1`–`IMP-4`**, com o invariante `pendencia_impeditiva == True` ⇒ `Qualificacao.resultado == INDEFINIDO`. **`E09` impeditivo + `DADOS_INCOMPLETOS` nunca é caminho normal** |
| 5 | **Ordem conceitual determinística** anterior à etapa 7: regras → qualificação **provisória** → eixo A → eixo B → composição e `E09` → qualificação **final** → primeira chamada da `MaquinaEstados`. O `Qualificador` continua **função pura** |
| 6 | **`R2` — mapa de grupos de cobertura**, registrado **FORA de C**: `AssuntoComercial` → **0..N grupos**, cada grupo com **1..N alternativas**; alternativa é **referência estrutural**, sem texto, valor, status, *binding*, caminho ou predicado duplicados. **Conjunção entre grupos, disjunção dentro do grupo.** `ASSUNTO_NAO_CLASSIFICADO` tem **zero grupos** |
| 7 | **Fragmento emitível agora**: `APROVADO` + *bindings* resolvendo para valor disponível + conferência de consistência verdadeira. `AGUARDA_APROVACAO` e `BLOQUEADO` **não habilitam**; **nenhuma emissão parcial** |
| 8 | **Regra de lacuna real**: fragmento não emitível só produz causa se deixar um **grupo inteiro descoberto**. Alternativa bloqueada em grupo já coberto **não cria lacuna, `E09` nem handoff** |
| 9 | **Classe I** (base **não avaliável**) → bloqueio **antes da etapa 7**, `MaquinaEstados` não executa, condições 2 e 4 = `None`, **zero `E09`**, alerta pelo caminho já existente. **Não é quinto caso de negócio.** **Classe II** (base **avaliável e divergente**) → fragmento sempre bloqueado, erro sempre registrado, alerta sempre emitido; o ciclo **pode continuar** havendo cobertura segura alternativa |
| 10 | **Motivos de `E09`: exatamente DOIS** — `CAMPO_INDISPONIVEL` e `SEM_RESPOSTA_APROVADA_EMITIVEL`. **Nenhum terceiro.** `E09` é a **união A ∪ B**, **um por ciclo**, com motivos **deduplicados e canonicalizados**; caso misto pode carregar ambos. **Nenhum motivo carrega texto livre, PII ou valor comercial** |
| 11 | **`pendencias_resposta` contém perguntas do interessado**, nunca motivos técnicos. Decisão **por assunto**; texto é **conteúdo persistido**. Pergunta `BAIXA` não entra; duplicatas preservadas; **causa exclusiva do eixo A NÃO cria pergunta** |
| 12 | **`F4-B` — reconciliação normativa limitada** de `docs/07` §2.2. **F1–F6 e F4(a)–F4(d) preservadas**; refina **somente** a consequência conversacional: divergência **sem cobertura segura** → **R03 + handoff**; divergência **coberta integralmente** por alternativa aprovada e íntegra do mesmo grupo → **resposta segura prossegue**, com **zero `E09` fabricado** e **zero handoff** causado por ela |
| 13 | **Produtor conceitual** para as condições **2** e **4** de `docs/07` §4.4 — **sem componente concreto**: não é o `CarregadorYaml`, não é o `ValidadorYaml`, não é o `SeletorFatos` e não é o `Qualificador`. A **condição 8 continua NÃO ATRIBUÍDA** (**S3-D1**) |
| 14 | **Pré-condição de integração de `N-b-RES2`**: um futuro produtor de `E06` não pode entregar combinação incoerente à `MaquinaEstados`. A responsabilidade continua **integralmente em `N-b-RES2`**, que **continua ABERTO** |
| 15 | **Cenários documentais próprios `D8-K1`–`D8-K30`** (`docs/07` §8.2), em **namespace separado**: `K-Nb-1`–`K-Nb-51` **não são alterados**. **Nenhum teste Python é criado** |
| 16 | **Fronteira preservada**: `docs/07` §4.1 com **14** componentes, §2 com **nove** responsabilidades, §4.4 com **oito** condições, `IntencaoConversacional` com **11** valores, `AssuntoComercial` com **54**, `ProjecaoInterpretacao` com **sete** campos, `AcaoMaquina` com **20** códigos, erros `E-Nb-1`–`E-Nb-19` e cenários `K-Nb-1`–`K-Nb-51` |

O que esta arbitragem **NÃO** faz: implementar código; alterar `src/`, `tests/`,
`knowledge/`, `prompts/`, `CLAUDE.md`, `docs/04`, `docs/05` ou `docs/08`; criar
`knowledge/indice-respostas-aprovadas.yaml`; criar o **mapa de cobertura**; criar módulo de
S2-D8; criar `AssuntoComercial` em Python; escolher produtor LLM; implementar o
`OrquestradorMotor`; **materializar AJ2**; **materializar C**; fechar **`N-b-RES2`**;
alterar **C-12**, que **permanece literal**; resolver `S3-D1`, `E4`, `E1`, `E3`, `B`,
`S2-D5`, `S2-D7`, `R10`, `R13`, `R17`, `R20`, `Q53` ou `Q54`; escolher a próxima
implementação funcional; ou criar a **3B.8**, que **continua não existindo**. A
**materialização de S2-D8 não é autorizada** por esta entrega, e **nenhum teste foi
executado** nela.

**Ordem futura — somente registro, sem execução e sem autorização.**

| # | Passo | Observação |
|---|---|---|
| 1 | materializar **AJ2** | pode ocorrer **em paralelo** com 2 |
| 2 | materializar **C** | pode ocorrer **em paralelo** com 1 |
| 3 | materializar o **mapa de cobertura R2** | depois de 1 e 2 |
| 4 | materializar **S2-D8** | depois de 3 |

**`N-b-RES2`** pode avançar **após AJ2** e **em paralelo** com 2–4. O **`OrquestradorMotor`**
depende, **entre outros**, de: **S2-D8 materializada**; **`N-b-RES2`**; o **produtor não
determinístico**; **E4**; o **limiar/configuração**; e a **integração da etapa 13**. **`Q2`
continua futura e não recomendada para o MVP.** **Nenhum desses passos é autorizado ou
escolhido aqui** — a decisão pertence à orquestração/auditoria posterior do GPT.

### Arbitragem AJ2 — escopo arbitrado e MATERIALIZADO na fronteira determinística

Micro-arbitragem sobre a **origem semântica do assunto** de `PerguntaComercial`: de onde
vem, e com que garantias, a informação de **sobre o que** o interessado consultou. A
**arbitragem** foi entrega **exclusivamente documental**, em
`docs/07-arquitetura-motor-respostas.md` §6.3, com reflexo em §8.2 e registro em §12,
item 20 — integrada pelo **PR #58**.

**AJ2 ESTENDE FORMALMENTE N-b.** O contrato vigente da etapa 4 mudou documentalmente ali.

**O delta foi MATERIALIZADO depois, pelo PR #61** — commit funcional
`4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`, merge
`5a722a5cc648149330362434694e7e76a40c1b57` — em `src/casa77_sdr/interpretation.py`, com
testes em `tests/test_interpretation.py` e registro factual **`M-AJ2-1`–`M-AJ2-9`** em
`docs/07` §6.3. **O contrato arbitrado, a materialização determinística e o futuro produtor
semântico continuam três coisas distintas**: o produtor não determinístico **não** foi
implementado, a **interpretação real de texto livre** não existe e a **segmentação
semântica** de consulta composta **não** é feita pela fronteira, que apenas **recebe,
valida e preserva** itens **já segmentados**.

**Nota temporal.** O quadro de contrato abaixo e a frase "o que esta micro-arbitragem NÃO
faz" descrevem a **arbitragem AJ2 à época do PR #58** e permanecem **corretos como registro
histórico** — inclusive quando dizem que a materialização não estava autorizada **por ela**.
Ela de fato não autorizava; a autorização veio depois, em mandato próprio, e produziu o
**PR #61**.

Contrato aprovado:

| # | Item |
|---|---|
| 1 | `PerguntaComercial` passa de **dois** para **três** campos: `texto`, `confianca` e **`assunto`** obrigatório, **sem confiança própria**; cardinalidade da coleção continua **0..N** |
| 2 | **`AssuntoComercial`** — vocabulário conceitual fechado de **54** valores: **53 específicos + `ASSUNTO_NAO_CLASSIFICADO`**. **Nenhum 55º membro** |
| 3 | A categoria cobre **consultas comerciais** — pergunta, pedido informacional e solicitação de material —, **sem** absorver os sinais dedicados `pedido_de_humano`, `INTERESSE_EM_VISITA`, `INTERESSE_CONFIRMAR_DISPONIBILIDADE` e `EXCECAO_SOLICITADA`, que **permanecem autoritativos** |
| 4 | **`ASSUNTO_NAO_CLASSIFICADO`** é **valor legítimo de totalidade** — **não** é erro, **não** é confiança `BAIXA`, **não** é ausência e **não** é `TrechoAmbiguo`. **Nunca escolher "o mais próximo"** |
| 5 | **`N-b-Q7`–`N-b-Q12`**: um assunto por item, segmentação de consulta composta, preservação textual, totalidade sem aproximação, duplicatas permitidas e **o assunto não atravessa** para a projeção nem produz condição |
| 6 | **`E-Nb-5` ampliado** para `assunto` ausente ou fora do vocabulário. A lista permanece **`E-Nb-1`–`E-Nb-19`** — **sem nenhum código novo**. `ASSUNTO_NAO_CLASSIFICADO` **não** gera `E-Nb-5` |
| 7 | Cenários passam de `K-Nb-1`–`K-Nb-40` para **`K-Nb-1`–`K-Nb-51`**, com `K-Nb-40` **complementado**. **Nenhum teste Python é criado** |
| 8 | **Fronteira preservada**: `IntencaoConversacional` continua com **11** valores, `ProjecaoInterpretacao` com **sete** campos, §4.1 com **14** componentes, §2 com **nove** responsabilidades, e as condições **2**, **4** e **8** de §4.4 continuam **NÃO ATRIBUÍDAS** |

O que esta micro-arbitragem **NÃO** faz: implementar `AssuntoComercial`; materializar AJ2 em
Python; alterar `src/`, `tests/`, `knowledge/`, `prompts/`, `docs/06`, `docs/05`, `docs/08`
ou `CLAUDE.md`; **antecipar S2-D8** — `ASSUNTO_NAO_CLASSIFICADO` **não implica** ausência de
`Rxx`, `resposta_aprovada_disponivel = false`, `E09`, `pendencia_impeditiva`, `R03` nem
handoff; mapear `assunto` → `Rxx` ou → fragmento; materializar **C**; escolher LLM, modelo,
fornecedor, SDK, API ou JSON Schema; resolver `Q53`/`Q54`; resolver `R10`, `R13`, `R17` ou
`R20`; escolher a próxima implementação funcional; ou criar a **3B.8**, que **continua não
existindo**. A **materialização do delta AJ2 não é autorizada** por ela.

**Impacto FUTURO em `tests/`, verificado mecanicamente** e **sem nenhuma alteração agora**:
`tests/test_interpretation.py` tem **2098** linhas e **132** funções `test_*`.
**Exigem edição direta: 16 funções — 15 testes + 1 auxiliar**, assim compostas: **13**
testes que constroem `PerguntaComercial`; **1** auxiliar que também a constrói
(`_combinacoes_para_propriedade`); e **2** testes cujas **asserções passam a ser falsas**
sem construírem a estrutura — `test_pergunta_comercial_tem_dois_campos` e
`test_superficie_publica_e_exatamente_a_declarada`. **Afetados indiretamente, sem edição
própria: 3 testes** que dependem do auxiliar, conjunto **disjunto** do anterior. **Total
amplo: 19 funções — 18 testes + 1 auxiliar.** As duas métricas são registradas
separadamente: **"exige edição" não se confunde com "afetado indiretamente"**. **A
quantidade de funções NOVAS de pytest não é estimada**: a parametrização é decisão futura
de materialização.

### Micro-arbitragem C-A1 — contrato de materialização de C fechado

Micro-arbitragem **exclusivamente documental** e **posterior** a **C**, sobre **como** a
futura materialização do índice deve proceder. Entrega materializada em
`docs/07-arquitetura-motor-respostas.md` §2.3 — bloco **"Micro-arbitragem C-A1"** — com
registro em §12, item 19.

**C-A1 refina a leitura futura de C. Ela não reabre C, não a implementa e não reescreve
`C-1`–`C-14`**, que permanecem **registro histórico** da arbitragem original.

Contrato aprovado:

| # | Item |
|---|---|
| 1 | **`C-15` — equivalência de *template***: *placeholder* sem nova aprovação exige **vínculo explícito ao fato afirmado** e **equivalência textual do fragmento inteiro**; normalização **NFC** e quebras suaves do mesmo parágrafo viram **um espaço**; **proibido** `casefold`, *trim* semântico, remoção de pontuação, paráfrase e tolerância aproximada; **sem equivalência → FAIL-CLOSED**; o índice **não** guarda valor, *snapshot*, *hash* nem versão congelada, e **não** recebe metadado de "origem da aprovação" |
| 2 | **Refinamentos de C-6, sem formato novo**: `inteiro_agrupado` com convenção **única e determinística**, sem arredondamento nem cálculo; `simbolo_moeda` com **tabela fechada** e **falha** para código não suportado, **sem inferir moeda** e **sem leitura implícita**; `hora` com **`HH:MM`** geral e **`Hh` apenas quando os minutos são `00`** |
| 3 | **Convenção final do formato `lista`** (refinamento de C-6f): zero itens **falha**; um item; dois itens unidos por conjunção; três ou mais com vírgulas e conjunção final. **Sem prefixo ou sufixo por item**, sem filtragem, reordenação, flexão ou paráfrase |
| 4 | **C-5 permanece fechado** em `EH_VERDADEIRO`/`EH_FALSO`, com **sete rejeições explícitas**: predicado para `null`; comparação com literal; igualdade entre caminhos **dentro de C**; conversão de caixa; pluralização; numeral por extenso; prefixo linguístico por item. A **igualdade entre caminhos** pertence ao futuro `ValidadorConsistenciaBase` |
| 5 | **Seleção posicional é PROIBIDA**, dentro e fora de iteração. Fora de `itera_sobre`, selecionar um item exige **identificador estrutural estável e não comercial**, que **não depende da posição** |
| 6 | **Unidade de bijeção é o fragmento emitível**, não o `Rxx` agregado. Notas e instruções internas ficam **fora da bijeção**: sem status, sem *binding*, sem `ASSERTIVA` |
| 7 | **Canonicalização de status** sem quarto valor, com o **sufixo de handoff fora de C** e **`PARCIAL` sem tradução automática**; **`BLOQUEADO` em nota interna não cria fragmento nem status**; a **autoridade do status** só migra sob **cinco condições** cumulativas |
| 8 | **Prioridade de modelagem**: atomizar o dado → `ASSERTIVA` sobre fato atômico → `RENDERIZADO` → só então decisão humana de conteúdo. **Não alterar redação apenas para facilitar implementação** |
| 9 | **Prosa não duplicada**: campo narrativo **não** pode virar segunda fonte factual paralela ao campo atômico |
| 10 | **Auditoria read-only de consumidores em todo o repositório** é **obrigatória** antes de qualquer alteração física de estrutura em `knowledge/casa77.yaml` |
| 11 | **Alvos de modelo `MD-1`–`MD-18`**, com finalidade, `G` correspondente, `Rxx` atingidos, se substituem ou adicionam representação, condição humana quando houver e obrigação de auditoria. **`MD-3` REMOVIDO / NÃO ARBITRADO**; **`MD-16` REMOVIDO / NÃO NECESSÁRIO PARA C**. **São alvos, não alterações autorizadas** |
| 12 | **Matriz `G1`–`G14`** com destino, mecanismo, `Rxx` atingidos e resultado projetado. **`G9`, `G11`, `G12` e `G13` ficam RESOLVIDOS por C-A1**; **`G14`** é **dívida estrutural NÃO BLOQUEADORA**, com o campo **não realocado** aqui |

**Contagens PROJETADAS de fragmentos — não estado físico atual.** Total: **35** fragmentos
emitíveis. Representáveis no contrato **original**: **7**. Após os refinamentos normativos de
C-A1, **sem** alterar o YAML e **sem** decisão humana: **11**. Após C-A1 mais os alvos de
modelo e as confirmações factuais: **29**. Residuais dependentes de **C-A2**: **6** —
**29 + 6 = 35**. No nível `Rxx`, no cenário futuro projetado: **24** integralmente
materializáveis, **4** parcialmente e **2** integralmente bloqueados — **24 + 4 + 2 = 30**.

O que esta micro-arbitragem **NÃO** faz: criar `knowledge/indice-respostas-aprovadas.yaml`;
alterar `knowledge/casa77.yaml`, `knowledge/respostas-aprovadas.md` ou
`knowledge/informacoes-pendentes.md`; converter respostas em *templates*; mudar status real;
implementar renderizador, carregador ou validador; executar qualquer alvo **`MD-x`**;
materializar **C**, **R2** ou **S2-D8**; resolver **`N-b-RES2`**; implementar produtor LLM ou
`OrquestradorMotor`; alterar `src/`, `tests/`, `docs/06`, `docs/05`, `docs/08`, `prompts/` ou
`CLAUDE.md`; executar testes; escolher a próxima implementação funcional; ou criar a
**3B.8**, que **continua não existindo**. **Nenhuma pergunta foi enviada ao responsável comercial** e
**nenhuma decisão comercial foi tomada.**

**Evidência.** A base factual é uma **auditoria read-only** de
`knowledge/respostas-aprovadas.md` contra `knowledge/casa77.yaml`, cujo relatório
**sanitizado** é identificado pelo SHA-256
`c0cf81d6e1a93c8ba19ed5a1863c93be4f1c37954702a8e94720a8a6b4ec79b0`. Ele **não é versionado**,
**vive fora do repositório** e **não contém fonte comercial nova**.

### Micro-arbitragem C-A2 — fatos e conteúdo humanos residuais (ENTREGA 1, documental)

Micro-arbitragem **exclusivamente documental** e **posterior** a **C** e a **C-A1**, sobre os
**fatos humanos** e o **conteúdo humano** que C-A1 enumerou e **não resolveu**. Entrega
materializada em `docs/07-arquitetura-motor-respostas.md` §2.3 — bloco **"Micro-arbitragem
C-A2"** — com **nota temporal** em §12, item 19.

**C-A2 refina a leitura futura de C. Ela não reabre C, não a implementa e não reescreve
`C-1`–`C-14` nem o bloco `C-A1`**, que permanecem **registro histórico**. A regra temporal
aplicada é explícita: **o texto histórico continua correto para o momento em que foi
escrito**, e C-A2 é **refinamento posterior da leitura futura**.

**Esta é a ENTREGA 1, e ela é DOCUMENTAL.** **Nenhum texto aprovado foi aplicado.**

Contrato aprovado:

| # | Item |
|---|---|
| 1 | **`A1`–`A4` = FECHADAS**, conforme arbitragem normativa registrada em `docs/07` §2.3, bloco **"Micro-arbitragem C-A2"**. **Os enunciados substantivos dos quatro fatos não são duplicados aqui**: `docs/00` registra **estado**, não regra comercial ou operacional |
| 2 | Os **limites do que `A4` NÃO autoriza** são **normativos** e vivem **exclusivamente** em `docs/07` §2.3 |
| 3 | **Registro ESTRUTURAL do conteúdo humano `B1`–`B16`** — alvo, mecanismo previsto, alvos `MD`, `FE` relacionada e observação estrutural. **`docs/07` não é fonte paralela de redação comercial**: **nenhum corpo literal**, preço, percentual, prazo, quantidade ou condição é reproduzido. A **fonte do texto continua sendo `knowledge/respostas-aprovadas.md`** |
| 4 | **`B1` / `R11` `F2`** é **texto já aprovado anteriormente**: **nenhuma nova redação**, resíduo **apenas de modelagem** (`MD-5`). **`B2`–`B15`** e **`B16-A`/`B16-B`** são **APROVADOS HUMANAMENTE / AINDA NÃO APLICADOS** |
| 5 | **Decisão `B16`** — `R05` passa a ter os fragmentos **`F1`**, **`F2`** e **`F3`**, **permanecendo um único `Rxx`**: **bijeção por fragmento** e **múltiplos fragmentos por `Rxx` já suportados**, preservando os **30 `Rxx`**. **O papel de cada fragmento é normativo e vive em `docs/07` §2.3** |
| 6 | **Não se afirma** que um `Rxx` diferente **obrigatoriamente** produziria grupo **R2** diferente ou `E09` espúrio. **R2 continua arbitragem própria**, e **seus grupos não são derivados automaticamente da identidade do `Rxx`** |
| 7 | **`C-A2-RT` — origem explícita**: o *binding* declara **`origem`**, de vocabulário **fechado** — **`YAML`** ou **`RUNTIME_AUTORITATIVO`**. **`origem` é OBRIGATÓRIA**, **sem valor padrão**; **ausência NÃO é lida como `YAML`** e vale **índice estruturalmente inválido / FAIL-CLOSED**. `YAML` exige `caminho_yaml` e **proíbe** `fato_runtime`; `RUNTIME_AUTORITATIVO` exige `fato_runtime` e **proíbe** `caminho_yaml`. **Exatamente um referente** |
| 8 | **Vocabulário runtime fechado** — `consulta_calendario_valida` e `data_disponivel`, ambos **booleanos**. Origem runtime aceita **somente `ASSERTIVA`**, com **`RENDERIZADO` proibido**, **somente `EH_VERDADEIRO`/`EH_FALSO`**, **nenhum predicado novo**, **nenhum valor, *snapshot*, *hash* ou versionamento** no índice e **nenhum provedor de calendário escolhido** |
| 9 | **Escopo do fato runtime** — registrado e fechado; **detalhes normativos em `docs/07` §2.3** |
| 10 | **`MD-15′` é POLÍTICA**, e **não é `ASSERTIVA`-gatilho**. **C valida consistência; C não decide candidatura nem disponibilidade.** **Nenhum terceiro motivo de `E09`** é criado. **Detalhes normativos em `docs/07` §2.3** |
| 11 | **Refinamentos normativos de leitura** de **P2**, **P8**, **F1**, **F3**, **C-5b** e da definição geral de **`ASSERTIVA`**. **Preservados**: **`F4`/`F4-B` permanecem literais**; **`C-12` permanece literal**; e **o LLM nunca decide**. **Detalhes normativos em `docs/07` §2.3** |
| 12 | **Tabela `MD` final refinada até `MD-20`** — **`MD-1` SUPERADO / NÃO NECESSÁRIO PARA C**; **`MD-3`** e **`MD-16` REMOVIDOS**; **`MD-6`**, **`MD-15′`** e **`MD-17`** mantidos, com **`A2`**, **`A4`** e **`A3`** satisfeitas; **`MD-14`** mantido; **`MD-18` GENERALIZADO**; **`MD-19` NOVO**; **`MD-20` NOVO e MÍNIMO**. **Todos** continuam sujeitos a **`C-A1-M4`**. **Detalhes normativos em `docs/07` §2.3** |
| 13 | **Efeitos futuros `FE-1`–`FE-14`**, todos **PLANEJADOS / NÃO APLICADOS**, com arquivo-alvo e entrega registrados. **`FE-11` é DIVIDIDA**: **`FE-11a`** — instrução interna, `knowledge/respostas-aprovadas.md`, **Entrega 2**, **não altera o YAML** — e **`FE-11b`** — `knowledge/casa77.yaml`, **RETIDA atrás de `C-A1-M4`** e **fora da Entrega 2** |

**Contagens — três eixos distintos.** **ESTADO FÍSICO ATUAL**: **35** fragmentos emitíveis e
**30** `Rxx`, **inalterados**. **CONTEÚDO APROVADO**: **16** novas unidades textuais no lote
— `B2`–`B15` mais `R05` `F2` e `R05` `F3`; **`B1` não é texto novo**. **CONTEÚDO APLICADO
nesta Entrega 1**: **0**. **MATERIALIZAÇÃO DE C hoje**: **0** fragmentos estruturalmente
materializados. **APÓS a futura Entrega 2**: **37** fragmentos e **30** `Rxx`. A hipótese de
**37/37** é **condicional** à aplicação do conteúdo, a **`C-A1-M4`**, aos alvos **`MD`**
necessários e à validação **`C-8`/`C-15`/`C-A1`** — e **não é resultado alcançado**.

O que esta micro-arbitragem **NÃO** faz: criar `knowledge/indice-respostas-aprovadas.yaml`;
alterar `knowledge/casa77.yaml`, `knowledge/respostas-aprovadas.md` ou
`knowledge/informacoes-pendentes.md`; **aplicar qualquer texto aprovado**; alterar `docs/02`,
`docs/03`, `docs/04`, `docs/05`, `docs/06`, `docs/08`, `prompts/`, `CLAUDE.md`, `src/` ou
`tests/`; converter respostas em *templates*; mudar status real; **executar qualquer alvo
`MD-x`**; **aplicar qualquer `FE`**; materializar **C**, **R2** ou **S2-D8**; resolver
**`N-b-RES2`**; **escolher provedor de calendário**; criar índice, condição de ciclo, motivo
de `E09`, evento, estado ou transição; implementar produtor LLM ou `OrquestradorMotor`;
executar testes; escolher a próxima implementação funcional; ou criar a **3B.8**, que
**continua não existindo**.

**Próxima entrega — futura ENTREGA 2, NÃO iniciada e NÃO concluída.** Arquivos
comportamentais previstos: `knowledge/respostas-aprovadas.md`, `docs/02-fluxo-comercial.md`,
`docs/03-regras-de-conversa.md`, `docs/04-handoff-humano.md` e
`prompts/prompt-sistema-bot.md`. **`FE-11a` está incluída**; **`FE-11b` fica fora**. Ela só
pode ser iniciada **após auditoria e merge desta Entrega 1**, e **deverá atualizar
`docs/00-estado-atual.md` na mesma entrega ou possuir reconciliação documental imediatamente
vinculada**.

**Nota temporal — ENTREGA 2, posterior.** O parágrafo acima registra o estado **à época da
Entrega 1** e **permanece correto como registro histórico**. A **Entrega 1 foi auditada e
integrada à `main`** pelo **PR #64** — commit `294a11a1c170815063764f1d49ae0d831b72d359`,
merge `25b867f1c6cb4d2d00cd49ea60361c82a6e98f6f` —, e **a ENTREGA 2 foi então executada**
sobre exatamente os cinco arquivos comportamentais previstos, mais este documento na **mesma
entrega**, conforme exigido. **`FE-1`–`FE-10`, `FE-11a` e `FE-12`–`FE-14` = APLICADAS**;
**`FE-11b` continua RETIDA atrás de `C-A1-M4`**. **Conteúdo B = APLICADO À FONTE DE
RESPOSTAS.** **Corpus: 37 fragmentos / 30 `Rxx`.** **`knowledge/casa77.yaml` não foi
alterado**, **nenhum alvo `MD` foi executado** e **C continua ARBITRADA / NÃO
MATERIALIZADA**. Detalhe nos itens **32** e **33** da Próxima ação.

### Arbitragem C — escopo arbitrado, NÃO materializado

Arbitragem sobre o **contrato do índice estruturado que liga cada `Rxx` aos campos de
`knowledge/casa77.yaml`**. Entrega **exclusivamente documental**, materializada em
`docs/07-arquitetura-motor-respostas.md` §2.3 e registrada em §12, item 19.

**Nota temporal — micro-arbitragem C-A1, posterior.** O contrato aprovado abaixo descreve a
**arbitragem C à época do PR #57** e permanece **correto como registro histórico**:
`C-1`–`C-14` **não são reescritas**. Depois dela, **C-A1** (§2.3, item 27 da Próxima ação)
**refina a leitura futura** do contrato de **materialização** — equivalência de *template*,
refinamentos de C-6, convenção do formato `lista`, proibição de seleção posicional, unidade
de bijeção, canonicalização e migração de status, prioridade de modelagem, alvos **`MD-x`** e
matriz **`G1`–`G14`** — **sem criar o índice**, **sem alterar o YAML** e **sem materializar
C**. **C continua ARBITRADA / NÃO MATERIALIZADA**, e **C-A2** fica **ABERTA** para os fatos
(`A1`–`A4`) e o conteúdo (`B1`–`B6`) humanos residuais.

**Nota temporal adicional — micro-arbitragem C-A2, posterior.** O parágrafo acima registra o
estado **à época de C-A1** e **permanece correto como registro histórico**. Depois dele,
**C-A2** passa a **ARBITRADA DOCUMENTALMENTE** (seção própria acima; `docs/07` §2.3, bloco
"Micro-arbitragem C-A2"): os fatos **`A1`–`A4` ficam FECHADOS** e o **conteúdo humano** é
registrado como **APROVADO HUMANAMENTE / AINDA NÃO APLICADO**, **estendido de `B1`–`B6` para
`B1`–`B16`**. **Nada foi aplicado**, e **C continua ARBITRADA / NÃO MATERIALIZADA**.

**Nota temporal adicional — primeira microentrega funcional `E1`, posterior (PR #84).** Os
parágrafos acima registram o estado **anterior a qualquer código de `C`** e **permanecem
corretos como registro histórico**. Depois deles, a **`E1`** foi **materializada e integrada
à `main`** pelo **PR #84** — commit funcional `02f1dd6621c31b90789c646bd8826e685f9ee019`,
merge `95ed2ce4e9c54f9bdfb7b3f820e6f9e065cde24e` —, criando **exclusivamente** o **validador
estrutural fail-closed** do **futuro** índice, em `src/casa77_sdr/response_index.py` e
`tests/test_response_index.py`. **`E1` valida a FORMA de uma estrutura já parseada; ela NÃO
cria o índice, NÃO o lê, NÃO implementa loader e NÃO lê `knowledge/**`.** Portanto **`E1`
está MATERIALIZADA e INTEGRADA**, o índice `knowledge/indice-respostas-aprovadas.yaml`
**continua INEXISTENTE** e **`C`, como entrega completa do índice estruturado, continua
ARBITRADA / NÃO MATERIALIZADA**. **`E1` materializada NÃO é `C` materializada.** Não confundir
esta microentrega com a **pendência homônima `E1`** — conversa × atendimento × lead —, que é
**anterior, distinta e continua ABERTA**.

**Nota temporal adicional — segunda microentrega funcional, posterior (PR #86).** Depois da
`E1`, o **carregador *fail-closed*** do futuro índice foi **materializado e integrado à `main`**
pelo **PR #86** — commit funcional `b2b11e2465c7f332747a806c80b629e995f0f5a6`, merge
`9bf68b8fece9ea66c74509490ddf6e02a0aa6f31` —, em `src/casa77_sdr/response_index_load.py` e
`tests/test_response_index_load.py`, com correção localizada em `tests/test_response_index.py`.
**Sem nomenclatura normativa `E2`.** Ele expõe **`IndiceIlegivel`** e
**`carregar_indice(path: str | Path)`**, lê **somente em UTF-8** e **somente para leitura**,
analisa **exclusivamente** com `yaml.SafeLoader`, **recusa chave duplicada** *fail-closed*,
**delega integralmente** a forma a `validar_indice` — com **`IndiceInvalido` propagando
intacta** — e **não normaliza, não completa e não inventa valor padrão**. **O caminho é sempre
explícito**: ele **não conhece caminho padrão, descoberta, glob ou variável de ambiente**, e
portanto **não descobre o arquivo nem resolve automaticamente o caminho canônico** — quem
carrega **informa o caminho**. **CARREGAR NÃO É MATERIALIZAR `C`**: o índice
`knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE** e **`C`, como entrega
completa do índice estruturado, continua ARBITRADA / NÃO MATERIALIZADA**. A mesma entrega
**removeu** de `tests/test_response_index.py` o teste `test_indice_real_continua_inexistente`,
porque a inexistência do índice era **evidência temporária da `E1`**, não invariante
permanente — **a remoção não criou o índice**.

**Nota temporal adicional — terceira e quarta microentregas funcionais, posteriores (PR #89 e
PR #91).** Depois do carregador, o **comparador determinístico de equivalência textual de
`C-15b`** foi **materializado e integrado à `main`** pelo **PR #89** — commit funcional
`23e3fa727eb1457cd98a0e0e6f36580dade2ab00`, merge
`76531de7d3f4257d84b5a1f9498d8666c4e60030` —, em
`src/casa77_sdr/response_equivalence.py`; e os **formatadores determinísticos de apresentação
pura de `C-6`** foram **materializados e integrados** pelo **PR #91** — commit funcional
`7d8dd8617eb5cd8c346e67496c3631feafe97f4f`, merge
`d15201b0a84bca332b09e0d5e623736605663962` —, em `src/casa77_sdr/response_format.py`. **Sem
nomenclatura normativa `E2`, `E3` ou `E4`.** O comparador julga a equivalência de **duas `str`
já em representação canônica**, **sem analisar Markdown** e **sem I/O**. Os formatadores
materializam **cinco** dos seis formatos do vocabulário fechado de `C-6` — **`inteiro`**,
**`inteiro_agrupado`**, **`simbolo_moeda`**, **`texto`** e **`lista`** —, como **funções puras
sobre valores já resolvidos**: eles **não resolvem *binding***, **não leem `caminho_yaml`**,
**não consultam `knowledge/**`**, **não consultam *locale***, **não conhecem *template*,
*placeholder*, Markdown, *renderer* nem consumidor**, e **nenhum chamador real existe**. O
formato **`hora` NÃO foi materializado**: `C-A1-F3` fixa `HH:MM` e `Hh`, mas **não existe
regra arbitrada** que escolha mecanicamente entre eles, e essa **lacuna continua ABERTA**.
**COMPARAR NÃO É MATERIALIZAR `C`** e **FORMATAR NÃO É MATERIALIZAR `C`**: o índice
`knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE**, **nenhum *template*,
*binding* físico ou `ASSERTIVA` física foi criado**, a **bijeção física 37/37 não foi
executada**, a **autoridade de status não migrou** e **`C`, como entrega completa do índice
estruturado, continua ARBITRADA / NÃO MATERIALIZADA**.

**Nota temporal adicional — quinta microentrega funcional, posterior (PR #93).** Depois dos
formatadores, o **avaliador determinístico booleano de `ASSERTIVA`** foi **materializado e
integrado à `main`** pelo **PR #93** — commit funcional
`efa903816b5dc1dafbce8161f6424abdf41f2ca6`, merge
`353e1b42d6c8b31d649f59b151184811ef51462e` —, em `src/casa77_sdr/response_assertion.py`.
**Sem nomenclatura normativa `E2`, `E3`, `E4` ou `E5`.** Ele expõe **`AssertivaNaoAvaliavel`**
e **`avaliar_assertiva(predicado: str, valor: object) -> bool`**, sobre o vocabulário
**fechado** de C-5 — **`EH_VERDADEIRO`** e **`EH_FALSO`**, sem terceiro (**C-5g**, **C-5h**,
**C-A1-R**) — e um **valor já resolvido pelo chamador**. Ele julga **apenas o domínio
booleano estrito**: **valor não booleano é NÃO AVALIÁVEL**, levanta `AssertivaNaoAvaliavel` e
**nunca é convertido em assertiva falsa**, **sem *truthiness***, **sem `bool(...)`**, **sem
coerção**, **sem *parsing***, **sem normalização** e **sem *fallback***. Essa recusa é
**delimitação técnica fail-closed daquela microentrega**, e **não** expansão normativa de
**`C-7`**, que trata **especificamente** de `null` e `pendente`; **nenhum domínio futuro
adicional de `ASSERTIVA` foi arbitrado**, e **ampliá-lo exigiria contrato posterior
explícito**. O módulo **não resolve referente**, **não lê `caminho_yaml`**, **não conhece a
origem do fato nem o fato de runtime**, **não faz I/O**, **não conhece índice, Markdown,
*template*, *placeholder* ou *renderer*** e **não decide candidatura, disponibilidade,
handoff ou `E09`** — **`ASSERTIVA` permanece consistency-only** (**C-5i**–**C-5q**,
**C-A2-NR7**). **AVALIAR `ASSERTIVA` NÃO É MATERIALIZAR `C`**: o índice
`knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE**, **nenhum *template*,
*binding* físico ou `ASSERTIVA` física foi criado**, **nenhum fragmento real foi validado**,
**nenhum consumidor foi integrado** e **`C`, como entrega completa do índice estruturado,
continua ARBITRADA / NÃO MATERIALIZADA**.

**Nota temporal adicional — sexta microentrega funcional, posterior (PR #95).** Depois do
avaliador, o **verificador determinístico da correspondência bijetiva de `C-A1-B3` /
`C-A1-B4`** foi **materializado e integrado à `main`** pelo **PR #95** — commit funcional
`bdd0b2acc415ab6307c7c8da2adbad15f42cb75f`, merge
`b06c0a43bd2f96b8712638e99c55edfe2fb2f99f` —, em `src/casa77_sdr/response_bijection.py`.
**Sem nomenclatura normativa `E2`, `E3`, `E4`, `E5` ou `E6`.** Ele expõe
**`BijecaoInvalida`** e **`validar_bijecao(fragmentos_indice, unidades_markdown,
correspondencias) -> None`**, e julga **uma única coisa**: se a relação recebida é
**bijetiva entre os dois domínios recebidos** — a unidade continua sendo o **fragmento
emitível** (`C-A1-B1`) e notas/instruções internas permanecem **fora da bijeção**
(`C-A1-B2`). **Os três domínios chegam prontos**: fragmentos e unidades são **tokens
opacos** `str` **exata** — subclasse de `str` **recusada** —, cada item da relação é
`tuple` **exata** de **exatamente dois lados** — subclasse de `tuple` **recusada** —, a
comparação usa **igualdade nativa exata de `str`**, **sem normalização**, **sem coerção**,
**sem *parsing*** e **sem I/O**, a validação é **fail-closed** com **precedência
determinística**, e **três domínios vazios são bijeção trivial válida somente sobre os
domínios fornecidos**. O módulo **não extrai fragmentos do índice**, **não extrai unidades
do Markdown**, **não decide o que é unidade emitível**, **não define identidade física de
fragmento**, **não cria identificadores**, **não lê índice real**, **não prova completude
dos dois domínios**, **não executa a bijeção física do corpus real**, **não satisfaz
`C-A1-ST7` isoladamente**, **não migra autoridade de status** (`C-A1-ST6`–`C-A1-ST10`) e
**não integra consumidor**. **A completude correta dos dois domínios é pré-condição do
chamador.** **VERIFICAR A BIJEÇÃO NÃO É MATERIALIZAR `C`**: o índice
`knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE**, **nenhum fragmento
real foi validado**, a **bijeção física 37/37 não foi executada**, a **autoridade de status
não migrou**, **nenhum consumidor foi integrado** e **`C`, como entrega completa do índice
estruturado, continua ARBITRADA / NÃO MATERIALIZADA**.

**Nota temporal adicional — sétima microentrega funcional, posterior (PR #97).** Depois do
verificador da bijeção, o **canonicalizador determinístico de rótulo de status já extraído**
foi **materializado e integrado à `main`** pelo **PR #97** — commit funcional
`4749efa74d5684b52b4f457176710ba6e212c627`, merge
`8c67e13808da59dbace413fce33c2c22280e69a3` —, em `src/casa77_sdr/response_status.py`.
**Sem nomenclatura normativa `E2`–`E7`.** Ele expõe **`StatusNaoCanonicalizavel`** e
**`canonicalizar_status(rotulo: str) -> str`**, e traduz **somente as três linhas com
tradução automática arbitrada** em **`C-A1-ST1`**–**`C-A1-ST3`**: `APROVADO` → `APROVADO`;
`AGUARDA APROVAÇÃO` → `AGUARDA_APROVACAO`; `APROVADO com handoff obrigatório` → `APROVADO`,
com o **sufixo de handoff NÃO transportado**, por ser instrução operacional fora de `C`
(**C-2f**, **C-5.1**). **Nenhuma quarta tradução é criada**, e **`BLOQUEADO` nunca é
produzido como imagem** — ele pertence a **`C-3`**, mas **nenhuma linha de `C-A1-ST` o
produz automaticamente a partir de um rótulo simples**. **O rótulo chega já extraído**: **a
origem correta do rótulo é pré-condição do chamador**. O tipo precisa ser `str` **exata** —
**subclasse de `str` é recusada antes de qualquer consulta à tabela** —, a **comparação é
literal**, **sem `strip`, `lower`, `upper`, `casefold`, `NFC`, `NFD`, `unicodedata`, colapso
de espaços, substituição de espaço inquebrável ou tolerância de acento e de caixa**, e a
validação é **fail-closed**, com precedência fixa **tipo → pertença → retorno**, categorias
técnicas privadas **`tipo_invalido`** e **`rotulo_nao_mapeado`**, localizador único
**`rotulo`** e mensagem que **nunca ecoa** o rótulo, o conteúdo, o `repr`, o tipo concreto,
um comprimento ou um índice. **`PARCIAL` continua SEM tradução automática** e **continua
exigindo mapeamento explícito no nível dos fragmentos emitíveis** (**C-A1-ST4**), **não
implementado por esta entrega**; **`BLOQUEADO` não recebeu mapeamento automático inventado**,
porque **C-A1-ST5** trata de `BLOQUEADO` **em nota interna**, que **não cria fragmento** e
**não cria status**, e esta fronteira **não recebe esse contexto**. O módulo **não extrai
rótulo do Markdown**, **não extrai fragmento**, **não decide emissibilidade**, **não define
identidade física de fragmento**, **não cria nem lê o índice real**, **não resolve
*bindings***, **não faz I/O**, **não executa a bijeção física** e **não prova completude do
corpus**. **CANONICALIZAR STATUS NÃO É MATERIALIZAR `C`**: o índice
`knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE**, **nenhum *template*,
*binding* físico ou `ASSERTIVA` física foi criado**, **o canonicalizador não valida fragmentos reais**,
**nenhum consumidor foi integrado**, **`C-A1-ST6`–`C-A1-ST10` NÃO foram satisfeitas**, **a
autoridade de status NÃO migrou** — `knowledge/respostas-aprovadas.md` **continua a
autoridade** (**C-11**) e o status **não é removido do Markdown** — e **`C`, como entrega
completa do índice estruturado, continua ARBITRADA / NÃO MATERIALIZADA**.

Contrato aprovado:

| # | Item |
|---|---|
| 1 | **índice estruturado futuro** — nome aprovado `knowledge/indice-respostas-aprovadas.yaml`, **não criado** |
| 2 | **fragmentos emitíveis** — `Rxx` → fragmentos; notas e instruções internas **não** são fragmentos, **não** recebem status nem *bindings* e **não** podem ser emitidas |
| 3 | ***binding* `RENDERIZADO`** — caminho YAML explícito, *placeholder* obrigatório, formato fechado; o valor vem **sempre** do YAML carregado e **nunca** é armazenado no índice |
| 4 | ***binding* `ASSERTIVA`** — predicado obrigatório do vocabulário fechado `EH_VERDADEIRO`/`EH_FALSO`, sem *placeholder* e sem formato; **consistency-only**, inclusive sobre campo relacionado a handoff — **nenhuma política de handoff é duplicada no índice** e **não existe campo `handoff_obrigatorio`** |
| 5 | **status fechado** — `APROVADO`, `AGUARDA_APROVACAO`, `BLOQUEADO`; **sem valor padrão** e **sem `PARCIAL`** |
| 6 | **fontes autoritativas** — a autoridade do **status** só migra para o índice **depois** da materialização e da bijeção validadas; **até lá o status NÃO sai do Markdown** |
| 7 | **anti-drift** — formatos de **apresentação pura**, sem função customizada, sem cálculo e **sem leitura implícita de campo adicional**; o símbolo monetário exige *binding* explícito |
| 8 | **bloqueio de transformação semântica** — se o texto aprovado exigir transformação semântica para corresponder ao YAML, a materialização é **BLOQUEADA** |
| 9 | **separação C × S2-D8** — C **não** mapeia pergunta para `Rxx`, **não** determina `resposta_aprovada_disponivel` nem `pendencia_impeditiva`, **não** confirma `E09` e **não** atribui produtor |

O que esta arbitragem **NÃO** faz: criar o índice; converter
`knowledge/respostas-aprovadas.md` em *templates*; remover status do Markdown; implementar
*parser*, *renderer* ou validador; alterar `knowledge/`, `src/`, `tests/`, `docs/06`,
`docs/05`, `docs/08`, `prompts/` ou `CLAUDE.md`; decidir `R10`, `R20`, `R13` ou `R17` —
todos **registrados e não decididos** —; resolver **S2-D8**; escolher a próxima
implementação funcional; criar a **3B.8**, que **continua não existindo**. A
**materialização do índice não é autorizada** por esta entrega.

### Arbitragem N-b — escopo aprovado e integrado à `main`

Arbitragem sobre o **contrato global da `Interpretacao` da etapa 4**. Entrega
**exclusivamente documental**: alterou somente `docs/07-arquitetura-motor-respostas.md`.
**Zero componente, estado, evento, transição, critério ou campo novo** — a tabela de
componentes de `docs/07` §4.1 permanece com **14**, e §2 com **nove** responsabilidades.
**Resumo**; o detalhe normativo vive em `docs/07` §6.3 e **não é duplicado aqui**.

| # | Decisão |
|---|---|
| N-b-a | **A `Interpretacao` relata o que foi lido.** Não classifica compatibilidade, não decide handoff, não resolve identidade, não qualifica, não escolhe pacote, não consulta e não recebe o YAML. **Não produz** `Exx`, `Txx`, `Rxx`, qualificação, violação, estado, pendência nem `motivo_encerramento`. |
| N-b-b | **As oito categorias de §6.3 são preservadas**: `intencoes_detectadas`, `dados_extraidos`, `correcoes`, `perguntas_comerciais`, `pedido_de_humano`, `referencias_evento_anterior`, `confianca_global` e `trechos_ambiguos`. |
| N-b-c | **`IntencaoConversacional`** é vocabulário conceitual **fechado em 11 valores**, na partição **A1 (6 derivados)**, **A2 (2 autônomos)** e **B (3 autônomos)**. Os seis códigos **A1** são **derivações determinísticas** dentro da fronteira da etapa 4; o **payload dedicado é a fonte autoritativa**. |
| N-b-d | **Consistência cruzada** sobre os **seis pares de representação dupla**, com **bi-implicação obrigatória** e confiança do código derivado **calculada**, não declarada. Divergência é **erro de contrato**. |
| N-b-e | **Confiança binária** — `ALTA` \| `BAIXA` —, **sem threshold numérico**, obrigatória onde o contrato a exige e **proibida** onde ele a proíbe. `BAIXA` é **ausência para consumo estruturado**, com **uma única exceção** explicitada em `docs/07` §6.3. |
| N-b-f | **Derivação determinística** da `Interpretacao` para a `ProjecaoInterpretacao`, que **permanece com sete campos**. Nenhum texto conversacional e nenhuma PII atravessam para o `ResolvedorIdentidade`. |
| N-b-g | **Condição 5 de §4.4** — `interesse_confirmar_disponibilidade` — ganha **produtor** e **função total**. É a **única** condição de `CondicoesCiclo` que N-b atribui: as condições **2**, **4** e **8** permanecem **NÃO ATRIBUÍDAS**. |
| N-b-h | **Modo degradado**: sem produtor, **não existe `Interpretacao`** — e **ausência não é interpretação vazia** —, não existe projeção, a etapa 5 não executa e a condição 5 é `None`. **Nenhum gatilho de alerta novo** é criado. |
| N-b-i | **Lista fechada de erros de contrato E-Nb-1–E-Nb-19**, que **bloqueiam na fronteira da etapa 4** e **nunca** viram `Identidade.AMBIGUA`. |
| N-b-j | **Cenários K-Nb-1–K-Nb-40** documentados em `docs/07` §8.2, **sem criar ou alterar teste algum**. |
| N-b-k | **Fronteira conceitual do produtor de interpretação da etapa 4**, dentro do **limite único de LLM** de §4.2 e §9 — **fronteira funcional, não componente novo**. **Fornecedor, modelo, SDK, API, biblioteca e formato de transporte não são escolhidos.** |

**A arbitragem N-b não implementou nada por si.** **À época do PR #51**,
nenhum arquivo de `src/`, `tests/`, `knowledge/` ou `prompts/` foi criado ou alterado e
**nenhum tipo Python foi criado**. **Estado atual**: a **parte determinística** do contrato
foi **materializada e integrada pelo PR #55**, em `src/casa77_sdr/interpretation.py`.
Continuam **não implementados** o **produtor não determinístico / LLM** e a **interpretação
real de texto livre** — o **bot não interpreta texto livre** e **nenhuma mensagem real pode
ser testada via LLM** —, a **integração operacional da etapa 4** e o **`OrquestradorMotor`**;
o **pipeline não está integrado**.
**N-b permanece aberta como IMPLEMENTAÇÃO PARCIAL.**

**O que a N-b NÃO resolve.** Permanecem **abertas**, sem alteração: **S2-D8**, **E4**,
**S3-D1**, **B**, **C**, **E1**, **E3**, **S2-D5**, **S2-D7**, a **confirmação física do
handoff**, o **retorno do controle ao bot após `atendimento_humano` sem `E14`/T34**, a
**unicidade geral de `id_atendimento` entre candidatos não identificados**, a
**integração operacional da etapa 13**, a **persistência operacional não volátil**, o
**destino do alerta operacional**, o **valor numérico do limiar** e seu **mecanismo de
carga**. **C continua separada** e **não** é declarada pré-requisito de **S2-D8**. Fica
registrada como **residual explícito de integração**, **sem identificador de pendência
novo**, a **transformação posterior dos sinais interpretados em eventos `Exx`**.

### Micro-arbitragem AJ1 — escopo aprovado e integrado à `main`

Micro-arbitragem sobre a **representação e a canonicalização determinística de N-b**.
Entrega **exclusivamente documental**: alterou somente
`docs/07-arquitetura-motor-respostas.md` — **156 adições, 1 remoção**. **Zero componente,
estado, evento, transição, critério, campo, intenção, erro, cenário ou subetapa novo.**
**Resumo**; o detalhe normativo vive em `docs/07` §6.3, §8.2 e §12 e **não é duplicado
aqui**.

| # | Decisão |
|---|---|
| AJ1-a | **`A1` não é entrada semântica independente do produtor não determinístico.** Os seis códigos **A1** nunca recebem valor semântico próprio vindo do LLM. |
| AJ1-b | **Presença `A1` é derivada** do payload autoritativo (N-b-X2, N-b-X4) e **confiança `A1` é calculada** por **N-b-X3** (N-b-G6b). A confiança calculada **pode ser armazenada** na `Interpretacao` canônica **para auditabilidade** — **armazenada não significa declarada**. |
| AJ1-c | O **slot de intenções autônomas** aceita **exatamente cinco** códigos: `INTERESSE_EM_VISITA`, `EXCECAO_SOLICITADA`, `INTERESSE_CONFIRMAR_DISPONIBILIDADE`, `CONTINUIDADE_DE_EVENTO_DECLARADA` e `EVENTO_NOVO_DECLARADO`. |
| AJ1-d | **Precedência `E-Nb-3` × `E-Nb-5`**: código **A1** no slot autônomo **com** confiança declarada → **`E-Nb-3`**; **sem** confiança → **`E-Nb-5`**. Ambos **rejeitados antes da canonicalização** — isso **não** torna `A1` entrada válida. |
| AJ1-e | **Classificação dos 19 erros**, sem remover, renomear ou acrescentar código: **recebíveis/runtime**; **invariantes internos da canonicalização**; e **`E-Nb-19` como invariante estrutural do módulo**. `E-Nb-13` é **invariante/program error** da derivação. |
| AJ1-f | **Alcance de prova**: **K-Nb-18** é **estrutural** (pós-condição/propriedade, sem exigir exceção por entrada externa); **K-Nb-34** permanece **recebível**, resolvido em `E-Nb-3`; **K-Nb-39** é **parcialmente local** e **parcialmente dependente de orquestração**. |
| AJ1-g | **`E-Nb-19`** será provado **estruturalmente** — superfície pública, tipos de retorno, campos, produtores e a **condição 5 como única condição produzida**. Fechamento de imports é **apenas evidência complementar de pureza**. |
| AJ1-h | **Condição 5 preservada**: ela **já possuía produtor conceitualmente atribuído** por N-b; a futura implementação apenas o **materializa**. As condições **2**, **4** e **8** continuam as **únicas NÃO ATRIBUÍDAS**. |
| AJ1-i | **`FormatoEvento`** de `qualification.py` **poderá ser reutilizado por import** na futura materialização — vocabulário fechado, cadeia de imports pura, sem ciclo, sem YAML. **Não move**, **não redeclara** o enum e **não** transforma a etapa 4 em produtora de `Qualificacao`. |
| AJ1-j | **`N-b-RES1` é regra fechada** — a etapa 4 **não emite `Exx`**; **`N-b-RES2` é o residual explícito ABERTO** da transformação posterior para **eventos confirmados**; **`N-b-RES3` é a classificação fechada** desse residual. |

**A micro-arbitragem AJ1 não implementou nada por si.** Ela **não implementou a
`Interpretacao`**, **não tornou a etapa 4 funcional**, **não criou produtor LLM**, **não
criou componente** e **não criou subetapa** — seu contrato foi **materializado depois**, na
parte determinística, pelo **PR #55**. Continuam válidos: `IntencaoConversacional` com
**11** valores; erros **E-Nb-1–E-Nb-19**; cenários **K-Nb-1–K-Nb-40**; `docs/07` §4.1 com
**14** componentes; §2 com **nove** responsabilidades. **N-b permanece aberta como
IMPLEMENTAÇÃO PARCIAL**: o **produtor não determinístico / LLM**, **N-b-RES2** e a
**integração operacional da etapa 4** continuam pendentes.

**O que a AJ1 NÃO resolve.** Permanecem **abertas**, sem alteração: **N-b-RES2**,
**S2-D8**, **S3-D1**, **E4**, **B**, **C**, **E1**, **E3**, **S2-D5**, **S2-D7**, o
`DetectorHandoff`, o `SeletorFatos`, o `ValidadorConsistenciaBase`, o `ValidadorResposta`,
o `OrquestradorMotor`, a **integração operacional da etapa 13**, a **persistência
operacional não volátil**, o **tratamento operacional dos bloqueios** (S4, S5), o **destino
do alerta operacional** e o **valor numérico do limiar** com seu **mecanismo de carga**.
**Fornecedor, modelo, SDK, API, biblioteca, formato de transporte e JSON Schema continuam
não escolhidos.**

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

**A arbitragem N-a não implementou nada por si.** **À época do PR #31**, N-a não existia em código, `src/casa77_sdr/persistence.py` **não foi alterado por aquela arbitragem** e o campo `instante_ultima_transicao` ainda não havia sido implementado. **Estado atual**: as materializações vieram depois, em entregas funcionais próprias — o **transporte e a validação da representação** do campo, pelo **PR #33** (`docs/07` §6.2, M-T1–M-T6); a **produção determinística de E**, com classificação e recência, pelo **PR #36** (M-E1–M-E6); e o conjunto **H**, o `havia_estado_esperado`, o **produtor N-I** e o ***wiring* da fronteira etapa 3 → identidade/etapa 5**, pelo **PR #38** (M-C1–M-C8). **A integração N-a permanece PARCIAL**: a **decisão** do marco veio pelo **PR #47** (M-DT1–M-DT7) e a **aplicação com a escrita**, como **fronteira chamável**, pelo **PR #49** (M-AE1–M-AE7), mas a **integração operacional da etapa 13 no pipeline** permanece pendente — **N-a-T3–N-a-T7 não estão operacionalmente concluídas** —, o **tratamento operacional dos bloqueios** (S4, S5) e o **destino do alerta** continuam pendentes, a **etapa 3 não está inteiramente implementada**, o `OrquestradorMotor` **continua não implementado** e **nenhuma subetapa 3B.8 foi criada, escolhida ou autorizada**.

**O que a N-a NÃO resolve.** Permanecem **abertas**, sem alteração: **E4**, **N-b** — **arbitrada** depois pelo **PR #51**, e aberta **apenas como implementação** —, **S2-D8**, **S3-D1**, **B**, **C**, **E1**, **E3**, **S2-D5**, **S2-D7**, a **confirmação física do handoff**, o **retorno do controle ao bot após `atendimento_humano` sem `E14`/T34** e a **unicidade geral de `id_atendimento` entre candidatos não identificados**. Ficam registradas como **pendências abertas da própria N-a** o **valor numérico do limiar temporal** e o **mecanismo concreto de carga** da configuração — `docs/07` §12, item 18.

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
Permanecem igualmente abertas, sem alteração: **N-b** — **arbitrada** depois pelo **PR #51**, e aberta **apenas como implementação** —, **E4, S2-D8, S3-D1, E1, E3, B, C, S2-D5,
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
alteração: **N-b** — **arbitrada** depois pelo **PR #51**, e aberta **apenas como implementação** —, **E4, S2-D8, S3-D1, E1, E3, B, C, S2-D5, S2-D7**, a **confirmação física do
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
| C | Contrato estruturado, legível por máquina, ligando as respostas aprovadas (`Rxx`) aos campos do YAML. **ARBITRADA / NÃO MATERIALIZADA.** **CONTRATO: ARBITRADO** — o contrato documental estruturado do futuro índice está **fechado e aprovado** em `docs/07` §2.3, registrado em `docs/07` §12, item 19. **MATERIALIZAÇÃO: NÃO EXISTE** — o arquivo `knowledge/indice-respostas-aprovadas.yaml` **continua inexistente**; `knowledge/respostas-aprovadas.md` **permanece Markdown** e foi **atualizado apenas como fonte de redação aprovada pela Entrega 2**, **sem conversão em *template* ou índice**; **nenhum status foi removido do Markdown**; e não há *renderer*, *template* físico nem *binding* físico. **A partir do PR #84 existe um VALIDADOR ESTRUTURAL** — a microentrega **`E1`**, `src/casa77_sdr/response_index.py` —, que valida a **forma** de uma estrutura já parseada que pretende ser o índice, **sem criar o índice**, **sem lê-lo**, **sem loader** e **sem ler `knowledge/**`. **A partir do PR #86 existe também um CARREGADOR *fail-closed*** — `src/casa77_sdr/response_index_load.py` —, que lê e recusa um artefato **explicitamente apontado**, delegando toda a forma ao validador. **A partir do PR #89 existe também um COMPARADOR de equivalência textual** — `src/casa77_sdr/response_equivalence.py` —, que julga a equivalência de `C-15b` entre **duas `str` já em representação canônica**, **sem analisar Markdown**, **sem I/O** e **sem conhecer o índice**. **A partir do PR #91 existem também os FORMATADORES determinísticos de `C-6`** — `src/casa77_sdr/response_format.py` —, que materializam **cinco** dos seis formatos do vocabulário fechado — **`inteiro`**, **`inteiro_agrupado`**, **`simbolo_moeda`**, **`texto`** e **`lista`** — como **funções puras sobre valores já resolvidos**; o formato **`hora` NÃO foi materializado** e sua **lacuna normativa continua ABERTA**. **A partir do PR #93 existe também o AVALIADOR determinístico booleano de `ASSERTIVA`** — `src/casa77_sdr/response_assertion.py` —, que julga um **predicado do vocabulário fechado** sobre um **valor já resolvido**, **apenas no domínio booleano estrito**; valor fora dele é **NÃO AVALIÁVEL** e **nunca vira assertiva falsa**, e essa recusa é **delimitação técnica fail-closed daquela microentrega**, **não** expansão de **`C-7`**. **A partir do PR #95 existe também o VERIFICADOR determinístico da correspondência bijetiva de `C-A1-B3` / `C-A1-B4`** — `src/casa77_sdr/response_bijection.py` —, que julga se uma relação **já fornecida pelo chamador** é **bijetiva entre dois domínios também já fornecidos**, sobre **tokens opacos** `str` **exata** e pares `tuple` **exata**, por **igualdade nativa exata de `str`**, **sem normalização, sem coerção, sem *parsing* e sem I/O**; ele **não extrai fragmentos, não extrai unidades, não define identidade física de fragmento, não lê índice real, não prova completude dos domínios, não executa a bijeção física do corpus real e não satisfaz `C-A1-ST7` isoladamente** — **a completude dos domínios é pré-condição do chamador**. **A partir do PR #97 existe também o CANONICALIZADOR determinístico de rótulo de status** — `src/casa77_sdr/response_status.py` —, que traduz um **rótulo já extraído** para o status canônico de `C-3` **somente** nas três linhas com tradução automática arbitrada em `C-A1-ST1`–`C-A1-ST3`, com `str` **exata**, **comparação literal**, **zero normalização** e **fail-closed**; **`PARCIAL` continua sem tradução automática** (**C-A1-ST4**, que exige mapeamento explícito por fragmento emitível) e **`BLOQUEADO` não recebeu mapeamento inventado** (**C-A1-ST5**, nota interna). Ele **não extrai rótulo nem fragmento, não cria identidade física de fragmento, não lê índice real, não satisfaz `C-A1-ST6`–`C-A1-ST10` e não migra a autoridade de status**. **Nenhum dos sete materializa C**: o validador confere a forma de algo que **ainda não existe**; o carregador só sabe **ler** esse algo **quando o caminho lhe é dado explicitamente** — `carregar_indice(...)` recebe o caminho como argumento, **sem caminho implícito ou padrão, sem descobrir o arquivo e sem resolver automaticamente o caminho canônico**; o comparador **recebe as duas `str` prontas**; os formatadores **recebem o valor já resolvido**; o avaliador **recebe predicado e valor já prontos**; o verificador **recebe os três domínios já prontos**; e o canonicalizador **recebe o rótulo já extraído** — todos **sem resolver *binding***, **sem ler `caminho_yaml`**, **sem consultar `knowledge/**`** e **sem consumidor integrado**. **Essa atualização de conteúdo NÃO materializa C.** **C continua aberta SOMENTE quanto à materialização.** **S2-D8 é pendência separada**, também **ARBITRADA / NÃO MATERIALIZADA** desde a arbitragem S2-D8 (`docs/07` §4.4.1), e também aberta **somente quanto à materialização** | **materializar** o índice `knowledge/indice-respostas-aprovadas.yaml` pelo contrato de `docs/07` §2.3 — **agora refinado por C-A1**, que fecha equivalência de *template*, formatos, convenção de `lista`, seleção em coleção, unidade de bijeção, migração de status e os alvos `MD-x` — e, só então, implementar `ValidadorConsistenciaBase` e, em cascata, `SeletorFatos` e `ValidadorResposta`. **`C-A2` está ARBITRADA DOCUMENTALMENTE**: os fatos `A1`–`A4` ficam **FECHADOS** e o conteúdo humano `B1`–`B16` foi **APROVADO HUMANAMENTE** e, pela **Entrega 2**, **APLICADO À FONTE DE RESPOSTAS** — **corpus 37 fragmentos / 30 `Rxx`**, com **`FE-1`–`FE-14` APLICADAS** — incluindo **`FE-11a` = APLICADA / RECONCILIADA** e **`FE-11b` = APLICADA / MATERIALIZADA POR REMOÇÃO** (PR #77 e PR #78), de modo que a leitura anterior de **`FE-11b` RETIDA atrás de `C-A1-M4`** permanece correta **somente como registro histórico** e **não** descreve o estado corrente. **GATES DE `C-A2` — ESTADO CORRENTE**: **`C-A2-N9` = CUMPRIDA**; **`C-A2-N10` = CUMPRIDA**; **`C-A2-N11` = CUMPRIDA — 16/16**; **`C-A2-N12` = CUMPRIDA** — a validação `C-8` / `C-15` / `C-A1` foi **reexecutada integralmente**, de forma **estritamente read-only**, contra `bd9687c69ddf7db9306363d5de4cf74072b5a134`, com **37/37 fragmentos emitíveis** em **12 eixos**, **444/444 resultados** (**265 `PASS`**, **179 `N/A`**), **0 `FAIL-CLOSED`**, **0 `NÃO DETERMINÁVEL`** e **0 `DIVERGÊNCIA DE BASE`**. **NADA DISSO MATERIALIZA C**: **`C` continua ARBITRADA / NÃO MATERIALIZADA**; `knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE**; **nenhuma resposta foi convertida em *template* físico**; **nenhum *binding* físico foi materializado**; **nenhuma `ASSERTIVA` física foi materializada**; **nenhum status saiu do Markdown** e **a autoridade de status continua no Markdown aprovado** (**`C-11`**); e **`knowledge/casa77.yaml` não foi alterado**. **GRAMÁTICA DE `caminho_yaml` = ARBITRADA DOCUMENTALMENTE / NÃO MATERIALIZADA**, na alternativa **`A2`** (`docs/07` §2.3, bloco **"Micro-arbitragem documental da gramática de caminho_yaml"**): **`str` depois do parsing**, **absoluto sem marcador** e **relativo marcado por `@`**, com **`C-4h`, `C-A1-S1` e `C-A1-S2` preservadas**. **ESTADO CORRENTE DE `CY13`**: **linha 1 — parser da gramática = MATERIALIZADA** pelo **PR #131**, em `src/casa77_sdr/response_yaml_path.py` (`analisar_caminho_yaml`, exceção `CaminhoYamlInvalido`, três categorias e seis localizadores fechados, decomposição imutável, **zero YAML** e **zero I/O**); **linha 2 — validação estrutural contextual = NÃO MATERIALIZADA** (**ainda não existe** componente que valide **relativo somente em fragmento com `itera_sobre`** nem **`@` proibido no próprio `itera_sobre`**); **linha 3 — resolver = NÃO MATERIALIZADA** (**ainda não existe** componente que percorra o YAML, resolva chaves, execute seletores, determine **zero / um / múltiplos *matches*** ou devolva terminal factual). A leitura anterior de **parser INEXISTENTE** permanece correta **somente como registro histórico** e **não** descreve o estado corrente. **O índice físico `knowledge/indice-respostas-aprovadas.yaml` continua INEXISTENTE** e **`src/casa77_sdr/response_index.py` continua INALTERADO**. **Continuam ABERTAS ou PENDENTES, sem decisão aqui**: a **sintaxe de *placeholder*** (**ABERTA**), o **formato `hora`** (**pendência separada**) e **`C-7`** (**NÃO MATERIALIZADA**, e **não reaberta**). **`C-A1-ST6`–`C-A1-ST10` continuam NÃO satisfeitas**, **`C-11` NÃO migrou** e **`C` continua ARBITRADA / NÃO MATERIALIZADA**. **PRÓXIMA AÇÃO**: **retornar ao GPT após a integração desta reconciliação para nova auditoria e priorização** — **nenhuma próxima microentrega técnica foi eleita**, e **não** se afirma que será a **validação contextual**, o **resolver**, ***placeholder***, **`hora`**, **`C-7`** ou o **índice** |

As pendências **B e C permanecem inalteradas** pelas arbitragens S2, S3, R, R-H e R-I e
pela implementação funcional da **3B.7** (PR #29). **B continua integralmente aberta.**
**C teve apenas o CONTRATO arbitrado**, em entrega documental posterior (`docs/07` §2.3): ela passa a **ARBITRADA / NÃO MATERIALIZADA** e **continua aberta como materialização**. **Nada foi implementado, convertido ou criado** por essa arbitragem. **S2-D8 teve o CONTRATO arbitrado depois**, em entrega documental própria (`docs/07` §4.4.1): ela passa igualmente a **ARBITRADA / NÃO MATERIALIZADA** e **continua aberta somente como materialização** — também sem nada implementado, convertido ou criado. **`C-12` permanece literal e inalterada**, e o status `BLOQUEADO` de um fragmento continua **não sendo**, por si só, `E09` nem `pendencia_impeditiva`: ele é um fato sobre a base, que S2-D8 passa a **consumir** — pelas regras de **fragmento emitível** e de **lacuna real** — sem que C o determine.

### Pendências da arbitragem S2 — não bloqueadoras da 3B.6

Prefixo `S2-` obrigatório: estas pendências **não** têm relação com a arbitragem
comercial `D1`–`D8` já registrada no histórico deste documento.

| # | Pendência | Situação |
|---|---|---|
| S2-D5 | Mensagem conversacional recebida enquanto o estado é `aguardando_confirmacao_disponibilidade`, **antes** de `E16`. Hoje o caso é inalcançável enquanto a integração de calendário está pendente (I17 de `docs/06`). Resolver na **Etapa 6**. | **não bloqueia** a 3B.6 |
| S2-D7 | `E13` a partir de estado **diferente** de `encaminhado_humano`. Hoje não existe produtor nem interface operacional para esse caminho. Resolver na **Etapa 5**. | **não bloqueia** a 3B.6 |
| S2-D8 | Contrato de detecção e classificação de pendências: detectar campo `null`/`pendente` relevante e ausência de resposta aprovada, classificar impeditiva × acessória, fornecer os identificadores técnicos ao `Qualificador` e confirmar `E09`. **Ampliada pela S3**: o mesmo produtor também fornece a condição estruturada **`resposta_aprovada_disponivel`** (T10, T17, T28), determinada **antes da etapa 7** — saída **distinta** de `E09` e **não** sua negação; só o status APROVADO habilita. **Nenhum componente concreto foi escolhido** — não é o `CarregadorYaml`, não é o `ValidadorYaml`, não é o `SeletorFatos` e não é o `Qualificador`. **ARBITRADA / NÃO MATERIALIZADA.** **CONTRATO: ARBITRADO** — os **dois eixos** (A, de qualificação; B, de resposta), **`Q1`**, **`IMP-1`–`IMP-4`**, a **ordem conceitual anterior à etapa 7**, o mapa **R2** de grupos de cobertura, **fragmento emitível** e **lacuna real**, **Classe I × Classe II**, os **dois** motivos de `E09` e a reconciliação **F4-B** estão fechados em `docs/07` §4.4.1 e registrados em `docs/07` §12, item 10. **MATERIALIZAÇÃO: NÃO EXISTE** — **nenhum módulo, nenhum mapa de cobertura e nenhum arquivo de `src/`, `tests/`, `knowledge/` ou `prompts/`**. **S2-D8 continua aberta SOMENTE quanto à materialização.** As condições **2** e **4** de `docs/07` §4.4 passam a ter **produtor conceitual**; a **condição 8 continua NÃO ATRIBUÍDA** (**S3-D1**). Detalhe em `docs/06` §11. | **não bloqueia** a `MaquinaEstados`/3B.6; **bloqueia** o `OrquestradorMotor` e a integração completa |
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
| N-a | Política de **elegibilidade e recência** que produz o conjunto elegível da etapa 3. **Especificação documental: ARBITRADA / CONCLUÍDA** pelo **PR #31**. **Materialização temporal parcial: IMPLEMENTADA** pelo **PR #33** — transporte e validação de `instante_ultima_transicao` em `src/casa77_sdr/persistence.py` (`docs/07` §6.2, M-T1–M-T6). **Produção determinística de E: IMPLEMENTADA** pelo **PR #36** — `src/casa77_sdr/eligibility.py` (`docs/07` §6.2, M-E1–M-E6). **Conjunto H, `havia_estado_esperado`, produtor N-I e *wiring* da fronteira etapa 3 → identidade/etapa 5: IMPLEMENTADOS** pelo **PR #38** — `src/casa77_sdr/context.py` (`docs/07` §6.2, M-C1–M-C8). **Decisão, aplicação e escrita do marco: MATERIALIZADAS** — a **decisão pura** e a **composição decisória das 0–3 chamadas** pelo **PR #47** (`src/casa77_sdr/transition_marker.py`, `docs/07` §6.2, M-DT1–M-DT7), e a **aplicação com a escrita**, como **fronteira chamável**, pelo **PR #49** (`src/casa77_sdr/transition_marker_write.py`, `docs/07` §6.2, M-AE1–M-AE7). **Integração N-a: PARCIAL / NÃO CONCLUÍDA** — continua **não integrada** a **etapa 13 no pipeline** (montagem completa do `RegistroAtendimento`, decisão de se a etapa 13 executa, escolha entre criar e gravar, geração de `id_atendimento`, criação operacional, marcação de idempotência e preservação de pendente), de modo que **N-a-T3–N-a-T7 não estão operacionalmente concluídas**; continuam pendentes o **tratamento operacional dos bloqueios** (S4, S5) e o **destino do alerta operacional**; a **etapa 3 inteira** e a **integração do pipeline** também **não** estão concluídas. O tratamento de `SEM_CANDIDATO_ELEGIVEL` na integração **não** é parte dela: é a **E4**, pendência distinta e **ainda aberta** | **especificação resolvida**; **campo temporal, produção de E, projeções de identidade, decisão do marco e aplicação/escrita materializados**; a **integração** ainda depende da **integração operacional da etapa 13**, do **tratamento dos bloqueios**, do **destino do alerta** e do **valor/mecanismo do limiar** (linha abaixo) |
| Limiar temporal de recência | **Valor numérico** do limiar e **mecanismo concreto de carga** da configuração. **Aberta pelo PR #31** (`docs/07` §12, item 18). **Nenhum número foi definido** e **nenhuma tecnologia, variável de ambiente, arquivo ou serviço foi escolhido**. **Não é dado comercial** — não entra em `knowledge/casa77.yaml`; depende de aprovação específica de Douglas Bianchi e de decisão operacional | **não bloqueia** a 3B.6, a 3B.7, a **produção determinística de E** (PR #36) nem a **montagem das projeções de identidade da etapa 3** (PR #38) — ambas recebem o limiar como argumento explícito; **bloqueia** a **integração operacional de N-a no pipeline** e, por consequência, o `OrquestradorMotor` |
| N-b | Contrato global da **interpretação**: quem produz a projeção estruturada consumida pelo resolvedor (`intencao_identidade`, referências, confianças binárias) e com que garantias. **Especificação documental: ARBITRADA / CONCLUÍDA** pelo **PR #51** — contrato global da `Interpretacao` da etapa 4 (`docs/07` §6.3), com as oito categorias preservadas, `IntencaoConversacional` fechada em **11** valores, derivação determinística para a `ProjecaoInterpretacao`, **condição 5** de §4.4, consistência cruzada, regras de confiança, modo degradado, **E-Nb-1–E-Nb-19**, **K-Nb-1–K-Nb-40** e a **fronteira conceitual do produtor**. **IMPLEMENTAÇÃO: PARCIAL** — a **fronteira determinística** foi materializada e integrada pelo **PR #55** em `src/casa77_sdr/interpretation.py` (canonicalização, `A1` derivado, confiança por N-b-X3, projeção e condição 5); continuam pendentes o **produtor não determinístico / LLM**, a **interpretação real de texto livre** e a **integração operacional da etapa 4**, e a **transformação posterior dos sinais interpretados em eventos confirmados** (**N-b-RES2**) permanece como **residual explícito aberto de integração**, **sem identificador de pendência novo**. **ESTENDIDA DOCUMENTALMENTE POR AJ2**, posterior: `PerguntaComercial` ganha o campo **`assunto`** (`AssuntoComercial`, **54** valores), `E-Nb-5` é ampliado — a lista continua **E-Nb-1–E-Nb-19** — e os cenários passam a **K-Nb-1–K-Nb-51**. **Esse delta foi MATERIALIZADO pelo PR #61**, em entrega funcional própria — `AssuntoComercial`, o terceiro campo de `PerguntaComercial`, a ampliação de `E-Nb-5` e os cenários `K-Nb-41`–`K-Nb-51` (`docs/07` §6.3, **M-AJ2-1**–**M-AJ2-9**). A implementação do **PR #55** continua sendo registro correto do contrato **anterior a AJ2**, que **não possuía `assunto`** | **especificação resolvida** e **delta AJ2 materializado** na fronteira determinística; **não bloqueia** a 3B.6; a **implementação de N-b continua PARCIAL** — faltam o **produtor não determinístico / LLM**, a **interpretação real de texto livre**, **`N-b-RES2`** e a **integração operacional da etapa 4** —, e por isso continua **bloqueando** a integração completa e o `OrquestradorMotor` |
| E1 | Distinção entre as entidades **conversa × atendimento × lead**. Já registrada como aberta desde a etapa de modelo de dados; a arbitragem R **não** a resolve. **COLISÃO DE RÓTULO — ATENÇÃO**: esta pendência **`E1`** é **anterior e inteiramente distinta** da microentrega funcional **`E1`** de `C` — o validador estrutural do futuro índice, integrado pelo **PR #84**. **O PR #84 NÃO resolve, NÃO reduz e NÃO toca esta pendência**, que **continua integralmente ABERTA**. Onde este documento cita a microentrega, ela aparece sempre como **`E1`** em contexto explícito de `C`. | **não bloqueia** a 3B.6; **não resolvida pelo PR #84** |
| E3 | **Evento novo declarado durante atendimento ativo.** Hoje o resultado é **conservador** — `AMBIGUA` / `AMBIGUIDADE_DIVERGENCIA_EM_ATENDIMENTO_ATIVO`. **Nenhuma transição nova foi aprovada** para abrir atendimento paralelo. | **não bloqueia** a 3B.6 |
| E4 | Tratamento de **`SEM_CANDIDATO_ELEGIVEL`** pelo `OrquestradorMotor`. O resultado existe e é auditável, mas o que o orquestrador faz com ele **não está decidido**; enquanto aberta, o resultado encerra o ciclo sem transição e **não autoriza avanço de integração**. | **não bloqueia** a 3B.6; **bloqueia** o `OrquestradorMotor` |
| Unicidade geral de `id_atendimento` | **Questão residual aberta pelo PR #27.** A R-I exige unicidade **apenas do ID explicitamente identificado** e **apenas** quando `veredito == ENCONTRADO` (P-I5). **Não foi decidido** se IDs duplicados entre candidatos **não identificados** constituem erro geral de contrato. **Nenhuma regra global de unicidade foi estabelecida**, e nada é corrigido silenciosamente. **Confirmado na implementação da 3B.7**: `src/casa77_sdr/identity.py` valida a unicidade somente do ID identificado, e há teste provando que dois candidatos não identificados com o mesmo `id_atendimento` **não** falham. | **não bloqueia** a 3B.6 nem a 3B.7; **continua ABERTA** |
| Retorno do controle ao bot | Não existe hoje **transição inversa de T31** que devolva o canal ao atendimento automático sem passar por `E14`/T34. **Nenhum evento ou transição foi criado** para isso. | **não bloqueia** a 3B.6 nem a arbitragem R |

## Pendências que não bloqueiam

- Itens pendentes da base: ver `knowledge/informacoes-pendentes.md` (fonte única das
  lacunas; não replicar aqui).

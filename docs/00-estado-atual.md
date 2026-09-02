# 00 — Estado Atual do Projeto

Documento de estado: registra etapa, subetapa, PRs, commits, testes e próxima ação.
**Não contém dado comercial.** Preço, capacidade, tipo de evento, horário, restrição e
qualquer outra condição vivem exclusivamente em `knowledge/casa77.yaml`.

Atualizado em: 2026-09-02 (**reconciliação documental após o merge do PR #95**). A **PR #95**
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
| Último commit **funcional** aprovado | `bdd0b2acc415ab6307c7c8da2adbad15f42cb75f` |
| Merge correspondente na `main` | `b06c0a43bd2f96b8712638e99c55edfe2fb2f99f` |
| Última **entrega funcional** concluída | **Sexta microentrega funcional de `C` — verificador determinístico da correspondência bijetiva de `C-A1-B3` / `C-A1-B4` sobre domínios já fornecidos pelo chamador**, em `src/casa77_sdr/response_bijection.py` (**PR #95** — commit funcional `bdd0b2acc415ab6307c7c8da2adbad15f42cb75f`, merge `b06c0a43bd2f96b8712638e99c55edfe2fb2f99f`, branch de origem `feat/c-response-bijection`, título `feat: add deterministic response bijection validator`). **Sem nomenclatura normativa `E2`, `E3`, `E4`, `E5` ou `E6`.** **Inclui**: **`BijecaoInvalida`** e **`validar_bijecao(fragmentos_indice: Sequence[str], unidades_markdown: Sequence[str], correspondencias: Sequence[tuple[str, str]]) -> None`** como **fronteira pública única** — **`__all__` com exatamente dois nomes**, **três parâmetros**, **sem default** e **sem parâmetro de modo, tolerância, origem, caminho ou configuração**. **Os três domínios chegam prontos**: a função julga **somente** se a relação recebida é **total, injetiva e sobrejetiva nos dois sentidos** entre os domínios recebidos. **Tokens opacos**: fragmento e unidade são `str` **não interpretadas** — sem formato `Rxx`, gramática, prefixo, separador, `UUID`, número ou posição exigidos —, comparadas por **igualdade nativa exata de `str`**, **sem `strip`, `casefold`, `lower`, `upper`, `NFC` ou normalização de espécie alguma**; **token é `str` exata** e **subclasse de `str` é recusada** nos dois domínios e nos dois lados de cada par, porque poderia redefinir `__eq__`/`__hash__`. **Relação como sequência explícita de pares, nunca `Mapping`**: cada item é obrigatoriamente **`tuple` exata de exatamente dois elementos** — **subclasse de `tuple` recusada**, **`list` de dois elementos recusada** —; `str`, `bytes` e `bytearray` **não** são contêineres válidos para nenhum dos três argumentos. **Zero normalização, zero coerção, zero *parsing*, zero I/O**; entradas **não alteradas**. **Precedência fixa**: tipo dos três argumentos → tipo dos tokens de `fragmentos_indice` → tipo dos tokens de `unidades_markdown` → tipo e forma dos itens da relação → tipo de origem e destino de cada par → duplicidade em `fragmentos_indice` → duplicidade em `unidades_markdown` → origem repetida → destino repetido → origem desconhecida → destino desconhecido → fragmento sem par → unidade sem par; cada etapa percorre **toda** a entrada antes da seguinte, a **primeira violação encerra** e **nada é acumulado** (**P5**). **Categorias técnicas privadas e fechadas**, que **não** são identificadores normativos de `C`: `tipo_invalido`, `estrutura_invalida`, `duplicidade`, `referencia_desconhecida` e `cobertura_incompleta`; **localizadores fechados**: `fragmentos_indice`, `unidades_markdown`, `correspondencias`, `correspondencias.item`, `correspondencias.origem` e `correspondencias.destino`. A mensagem tem a forma `<categoria>: <localizador>` e **nunca** ecoa o token recebido, o conteúdo, o `repr`, o tipo concreto, um índice numérico, um tamanho ou uma cardinalidade; **sem `__cause__`** e **sem `__context__`**. **Três domínios vazios são bijeção trivial válida** e devolvem `None` — afirmação **restrita aos domínios fornecidos**. **Limite da garantia**: retorno bem-sucedido significa **somente** que a relação fornecida é bijetiva sobre os domínios fornecidos — **não** que o índice real esteja completo, que o Markdown tenha sido integralmente extraído, que a bijeção física do corpus real tenha ocorrido, que `C-A1-ST7` esteja satisfeita no sistema, nem que a autoridade de status possa migrar; **a completude correta dos dois domínios é pré-condição do chamador**. **NÃO inclui**: **extração de fragmentos do índice**; **extração de unidades do Markdown**; a **decisão do que é unidade emitível**; a **identidade física de fragmento**; a **criação de identificadores**; a **leitura do índice real**; a **prova de completude dos domínios**; a **execução da bijeção física do corpus real**; a **satisfação de `C-A1-ST7`**; a **migração de autoridade de status**; a **integração de consumidor**; a **criação do índice real**; **R2**; **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**; **LLM**; e a **3B.8**. **VERIFICAR A BIJEÇÃO NÃO É MATERIALIZAR `C`** |
| Entrega funcional **anterior** | **Quinta microentrega funcional de `C` — avaliador determinístico booleano de `ASSERTIVA` sobre valor já resolvido**, em `src/casa77_sdr/response_assertion.py` (**PR #93** — commit funcional `efa903816b5dc1dafbce8161f6424abdf41f2ca6`, merge `353e1b42d6c8b31d649f59b151184811ef51462e`, branch de origem `feat/c-response-assertion`, título `feat: add deterministic assertion evaluator`). **Sem nomenclatura normativa `E2`, `E3`, `E4` ou `E5`.** **Inclui**: **`AssertivaNaoAvaliavel`** e **`avaliar_assertiva(predicado: str, valor: object) -> bool`** como **fronteira pública única** — **`__all__` com exatamente dois nomes**, **dois parâmetros**, **sem default** e **sem parâmetro de modo, estilo, origem, caminho ou configuração**. **Predicados suportados**, do vocabulário fechado de C-5: **`EH_VERDADEIRO`** e **`EH_FALSO`** — **nenhum terceiro** (**C-5g**, **C-5h**, **C-A1-R**). **Matriz avaliável, exaustiva**: `EH_VERDADEIRO` + `True` → `True`; `EH_VERDADEIRO` + `False` → `False`; `EH_FALSO` + `False` → `True`; `EH_FALSO` + `True` → `False`. **Domínio materializado**: **somente `bool` estrito já resolvido**; **qualquer valor fora dele é NÃO AVALIÁVEL** e levanta `AssertivaNaoAvaliavel` — **`0` não é `False`**, **`1` não é `True`**, e o valor **nunca** é convertido em assertiva falsa; **sem *truthiness***, **sem `bool(...)`**, **sem coerção**, **sem comparação com `1`/`0`**, **sem leitura de `"true"`/`"false"`**, **sem *parsing***, **sem normalização** e **sem *fallback***; `__bool__` e `__eq__` customizados **não** são consultados. **Predicado inválido**: não-`str` ou fora do vocabulário → **fail-closed** por `AssertivaNaoAvaliavel`, **sem `upper`**, **sem `strip`** e **sem tolerância de caixa**. **Precedência fixa**: **1.** tipo do predicado; **2.** valor do predicado; **3.** domínio do valor; **4.** avaliação — a **primeira violação encerra** e **nada é acumulado**. **Categorias técnicas privadas e fechadas**, que **não** são identificadores normativos de `C`: `tipo_invalido` e `valor_invalido`; **localizadores fechados**: `predicado` e `valor`. A mensagem tem a forma `<categoria>: <localizador>` e **nunca** ecoa o predicado, o valor, o tipo concreto, `repr`, conteúdo, índice, tamanho ou deslocamento; **sem `__cause__`** e **sem `__context__`**. **NÃO inclui**: a **criação do índice real**; a **gramática ou o resolvedor de `caminho_yaml`**; a **origem do referente** e o **fato de runtime**; **calendário**; **analisador ou extrator de Markdown**; *template*, *placeholder* ou *binding* físico; ***renderer***; **formatos**; a **bijeção física 37/37**; a **canonicalização ou migração de status**; a **integração de consumidor**; **R2**; **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**; **LLM**; e a **3B.8**. **Esta entrega NÃO declara que todo domínio futuro de `ASSERTIVA` seja booleano**, e **ampliar o domínio exige contrato posterior explícito**. **AVALIAR `ASSERTIVA` NÃO É MATERIALIZAR `C`** |
| Entrega funcional **anterior a essa** | **Quarta microentrega funcional de `C` — formatadores determinísticos de apresentação pura de `C-6`**, em `src/casa77_sdr/response_format.py` (**PR #91** — commit funcional `7d8dd8617eb5cd8c346e67496c3631feafe97f4f`, merge `d15201b0a84bca332b09e0d5e623736605663962`, branch de origem `feat/c-response-formatters`, título `feat: add deterministic response formatters`). **Sem nomenclatura normativa `E2`, `E3` ou `E4`.** **Inclui**: **`FormatoInaplicavel`**; e as **cinco** funções puras **`formatar_inteiro(valor: int) -> str`**, **`formatar_inteiro_agrupado(valor: int) -> str`**, **`formatar_simbolo_moeda(codigo: str) -> str`**, **`formatar_texto(valor: str) -> str`** e **`formatar_lista(itens: Sequence[str]) -> str`** — **`__all__` com exatamente seis nomes**, **um parâmetro por função**, **sem default** e **sem parâmetro de estilo, padrão ou variante**. **`inteiro`** (C-6a): decimal do **mesmo** inteiro, **`int` estrito**, **`bool` recusado**, **sem coerção** de `float`, `Decimal` ou texto numérico, **sem agrupar, sem arredondar, sem zero acrescentado**, sinal preservado. **`inteiro_agrupado`** (C-6b, `C-A4-F1`): mesmo inteiro, agrupamento **da direita para a esquerda** em grupos de **três dígitos** unidos por **`.`**, **sem casa decimal, sem arredondamento, sem cálculo, sem zero para completar grupo**, sinal **preservado e não agrupado**, **sem *locale*** e **sem delegar ao `format` da linguagem** — o agrupamento é montado **dígito a dígito**. **`simbolo_moeda`** (C-6c, `C-A4-F2`): **tabela fechada** com **um único código**, devolvendo **somente o símbolo**, **sem whitespace antes ou depois**, **sem `upper`, sem `strip`, sem tolerância de caixa**, **sem inferir moeda** e **sem ler campo adicional**; código não suportado **FALHA**. **`texto`** (C-6e): **identidade exata**, devolvendo **a mesma `str`** — **sem NFC, sem `strip`, sem `casefold`, sem colapso de espaço, sem dobra de quebra e sem ajuste de pontuação**; a `str` vazia continua vazia. **`lista`** (C-6f, `C-A1-L`): **zero itens FALHA**; um item devolve o próprio item; dois unidos por ` e `; três ou mais com `, ` entre os anteriores e ` e ` antes do último; **ordem, cardinalidade e conteúdo literal preservados**, **sem filtrar, ordenar, flexionar, parafrasear ou prefixar** — **inclusive o item vazio, que o contrato não proíbe e que NÃO é filtrado**; **`str` não é contêiner válido** e cada item precisa ser `str`; a **entrada não é mutada**, nem no caminho de falha. **Categorias técnicas privadas e fechadas**, que **não** são identificadores normativos de `C`: `tipo_invalido` e `valor_invalido`; **localizadores fechados**: `valor`, `codigo`, `itens` e `itens.item`. **Fail-closed na primeira violação**, sem acumular, com mensagem de **categoria e localizador** que **nunca** ecoa o valor, o item, o código ou o conteúdo textual recebido, **sem `__cause__`** e **sem `__context__`**. **NÃO inclui**: o formato **`hora`** (C-6d), **expressamente fora**; a **criação do índice real**; **analisador ou extrator de Markdown**; *template*, *placeholder* ou *binding* físico; ***renderer***; a **avaliação de `ASSERTIVA`**; a **bijeção física 37/37**; a **integração de consumidor**; a **migração de autoridade de status**; **R2**; **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**; **calendário**; **LLM**; e a **3B.8**. **FORMATAR NÃO É MATERIALIZAR `C`** |
| Entrega funcional **anterior a essa (2)** | **Terceira microentrega funcional de `C` — comparador determinístico de equivalência textual de `C-15b`**, em `src/casa77_sdr/response_equivalence.py` (**PR #89** — commit funcional `23e3fa727eb1457cd98a0e0e6f36580dade2ab00`, merge `76531de7d3f4257d84b5a1f9498d8666c4e60030`, branch de origem `feat/c-response-equivalence`). **Sem nomenclatura normativa `E2` ou `E3`.** **Inclui**: **`EquivalenciaNaoDeterminavel`**; **`sao_textualmente_equivalentes(aprovado: str, renderizado: str) -> bool`** como **fronteira pública única**, sobre **duas `str` já em representação canônica** (D1); **tipo não-`str` → `TypeError`**, verificado **antes** da canonicidade; **violação de canonicidade → `EquivalenciaNaoDeterminavel`**, que **NÃO é `False`** (D6-A) e obriga o chamador a **parar ou escalar**; validação de **`aprovado` antes de `renderizado`**, com **primeira violação encerrando** e nada acumulado; **NFC antes da dobra**; **`LF` isolado → exatamente um `U+0020`** (D3); **`\n\n` preservado literalmente** (D4); **três ou mais `LF` recusados**; **`CR`, `CRLF`, `U+2028`, `U+2029`, `U+0085`, `U+000B` e `U+000C` recusados**, **sem converter `CRLF`** (D5); **`LF` de borda recusado**; **branco adjacente a `LF` recusado** (D7); **igualdade final exata**, **sem `strip`, sem `casefold`, sem *fuzzy* e sem transformação semântica**; e a **`str` vazia permanecendo canônica**. **Categorias técnicas privadas**, fechadas e **que não são identificadores normativos de `C`**: `terminador_proibido`, `quebra_na_borda`, `sequencia_de_quebras_excessiva` e `branco_adjacente_a_quebra`; a mensagem carrega **categoria e lado** — com localizador `inicio`/`fim`/`antes`/`depois` quando aplicável — e **nunca** o texto recebido, o caractere ofensor, deslocamento, índice ou comprimento, **sem `__cause__`**. **NÃO inclui**: a **criação do índice real**; **analisador ou extrator de Markdown**; *templates* ou *bindings* físicos; ***renderer***; **formatos**; a **integração de consumidor**; a **bijeção física 37/37**; a **migração de autoridade de status**; **R2**; **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**; **calendário**; **LLM**; e a **3B.8**. **COMPARAR NÃO É MATERIALIZAR `C`** |
| Entrega funcional **anterior a essa (3)** | **Segunda microentrega funcional de `C` — carregador *fail-closed* do futuro índice de respostas aprovadas**, em `src/casa77_sdr/response_index_load.py` (**PR #86** — commit funcional `b2b11e2465c7f332747a806c80b629e995f0f5a6`, merge `9bf68b8fece9ea66c74509490ddf6e02a0aa6f31`, branch de origem `feat/c-response-index-loader`). **Sem nomenclatura normativa `E2`.** **Inclui**: **`IndiceIlegivel`**; **`carregar_indice(path: str | Path)`** como **fronteira pública única**, com **caminho sempre explícito** — **sem caminho padrão, descoberta automática, glob ou variável de ambiente**; leitura **somente em UTF-8** e **somente leitura**; análise baseada **exclusivamente** em `yaml.SafeLoader`, via subclasse privada que **altera apenas a construção de mapeamento**; **rejeição *fail-closed* de chave YAML duplicada**, por mapeamento e em qualquer nível; a **taxonomia fechada de ilegibilidade** — `arquivo_ausente`, `leitura_falhou`, `codificacao_invalida`, `sintaxe_invalida` e `chave_duplicada` —, com mensagem de **categoria e caminho** que **não ecoa o conteúdo do arquivo** e **causa técnica encadeada em `__cause__`**; a **separação estrita entre artefato ilegível e estrutura inválida**; a **delegação integral** da validação estrutural a `validar_indice(...)`, com **`IndiceInvalido` propagando intacta**, sem captura, reembalagem, tradução de categoria ou duplicação de regra; e **zero normalização, zero valor padrão e zero *fallback*** após a análise. **Também remove** de `tests/test_response_index.py` o teste `test_indice_real_continua_inexistente`. **NÃO inclui**: a **criação do índice real**; a **conversão do Markdown**; *templates* ou *bindings* físicos; a **bijeção 37/37**; **C-15**; **renderização**; **aplicação de formatos**; **avaliação de `ASSERTIVA` contra dados reais**; **R2**; **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**; **calendário**; **LLM**; e a **3B.8**. **Sem numeração oficial de subetapa**: não é a 3B.8, que **não existe**. **Carregar não é materializar `C`** |
| Entrega funcional **anterior a essa (4)** | **`E1` — validador estrutural do futuro índice de respostas aprovadas**, em `src/casa77_sdr/response_index.py` (**PR #84** — commit funcional `02f1dd6621c31b90789c646bd8826e685f9ee019`, merge `95ed2ce4e9c54f9bdfb7b3f820e6f9e065cde24e`, branch de origem `feat/c-e1-response-index-validator`). **Primeira microentrega funcional de `C`.** **Inclui**: **`IndiceInvalido`**; **`validar_indice(indice: object) -> None`**; **schema estrutural fechado**; **vocabulários fechados** de status, mecanismo, origem, formato, predicado e fato runtime; **exclusividade `YAML` × `RUNTIME_AUTORITATIVO`**; **`RUNTIME_AUTORITATIVO` somente com `ASSERTIVA`**; as **regras estruturais de `RENDERIZADO`** (*placeholder* + formato) e de **`ASSERTIVA`** (predicado); **fail-closed na primeira violação**; **rejeição de seleção numericamente posicional**; e a **proteção contra índices posicionais mesmo após seletores textuais encadeados**. **NÃO inclui**: a **criação do índice real**; **loader**; **leitura de `knowledge/**` pelo módulo**; **conversão do Markdown**; **bindings reais**; a **bijeção 37/37**; **C-15**; **renderização**; **aplicação de formatos**; **avaliação de `ASSERTIVA` contra dados reais**; **R2**; **S2-D8**; **`N-b-RES2`**; o **`OrquestradorMotor`**; **calendário**; **LLM**; e a **3B.8**. **Sem numeração oficial de subetapa**: não é a 3B.8, que **não existe**. **`E1` materializada NÃO é `C` materializada** |
| Entrega funcional **anterior a essa (5)** | **Materialização funcional do delta AJ2** — o **assunto** de `PerguntaComercial` na **fronteira determinística** da etapa 4, em `src/casa77_sdr/interpretation.py` (**PR #61** — commit funcional `4c3db56e2a8d0de0b0f24d1f783c3be2387c5382`, merge `5a722a5cc648149330362434694e7e76a40c1b57`, branch de origem `feat/materializar-aj2-assunto`). **Inclui**: **`AssuntoComercial`** como vocabulário fechado de **54** membros — **53 específicos + `ASSUNTO_NAO_CLASSIFICADO`** —, na **ordem documental** de `docs/07` §6.3; **`PerguntaComercial` com três campos** — `texto`, `confianca` e **`assunto`** —, o assunto **obrigatório** e **sem confiança própria**; a **ampliação de `E-Nb-5`** para assunto **ausente** (AJ2-X1) e **fora do vocabulário** (AJ2-X2), com **tipo runtime incompatível** continuando `TypeError` **sem código**; a validação nos **dois caminhos** — canonicalização e `Interpretacao` construída diretamente —, com a **precedência histórica** dos erros N-b/AJ1 **preservada**; e os cenários **`K-Nb-41`–`K-Nb-51`**. **Preserva**: a `ProjecaoInterpretacao` de **sete** campos — o assunto **não atravessa** —, **`IntencaoConversacional` com 11** valores, **N-b-X3** inalterada, a **condição 5** como única condição de §4.4 materializada, a lista **`E-Nb-1`–`E-Nb-19`** sem vigésimo código e o **não-export** pelo `casa77_sdr/__init__.py`. **NÃO inclui**: o **produtor não determinístico / LLM**; a **interpretação real de texto livre**; a **segmentação semântica** de consulta composta — que precisa chegar **já segmentada** do futuro produtor; **N-b-RES2**; a **integração operacional da etapa 4**; e o **`OrquestradorMotor`**. **Sem numeração oficial de subetapa**: não é a 3B.8, que **não existe** |
| Entrega funcional **anterior a essa (6)** | **Materialização da parte DETERMINÍSTICA de N-b** — a fronteira determinística da interpretação da etapa 4, em `src/casa77_sdr/interpretation.py` (PR #55). **Inclui**: a **canonicalização determinística** da `Interpretacao`; **`A1` derivado** dos payloads autoritativos; a **confiança `A1` calculada** por **N-b-X3**; a **projeção** para a `ProjecaoInterpretacao` **já existente**, de sete campos; a **condição 5** de `docs/07` §4.4 como função total; e a **validação de canonicidade** exigida também de uma `Interpretacao` construída diretamente. **NÃO inclui**: o **produtor não determinístico / LLM**; a **interpretação de texto livre**; **N-b-RES2**; a **integração operacional da etapa 4**; e o **`OrquestradorMotor`**. **Sem numeração oficial de subetapa**: não é a 3B.8, que **não existe** |
| Entrega funcional **anterior a essa (7)** | **Aplicação e escrita do marco temporal como fronteira chamável** — `criar_com_marco_de_transicao(...)` e `gravar_com_marco_de_transicao(...)` (`src/casa77_sdr/transition_marker_write.py`, PR #49 — commit `d621a2c7…`, merge `f82da69f…`). Também **sem numeração de subetapa** |
| Entrega funcional **anterior a essa (8)** | Decisão determinística do marco temporal — `decidir_instante_ultima_transicao(...)` e a **composição decisória das 0–3 `DecisaoMaquina`** do ciclo (PR #47 — commit `b2f9f74d…`, merge `dd5a4cc7…`). Também **sem numeração de subetapa** |
| Entrega funcional **anterior a essa (9)** | Materialização em runtime da projeção `transicoes_que_mudaram_estado` na `MaquinaEstados` / `DecisaoMaquina` (PR #44 — commit `2da532f1…`, merge `048a5483…`). Também **sem numeração de subetapa** |
| Entrega funcional **anterior a essa (10)** | Montagem determinística das projeções de identidade da etapa 3 — fronteira **etapa 3 → identidade/etapa 5** (PR #38 — commit `f312eaa5…`, merge `10810506…`). Também **sem numeração de subetapa** |
| Entrega funcional **anterior a essa (11)** | Implementação funcional da política N-a — produção determinística do conjunto elegível **E** (PR #36 — commit `51fae0d1…`, merge `383c5668…`). Também **sem numeração de subetapa** |
| Entrega funcional **anterior a essa (12)** | Evolução temporal do contrato de persistência operacional — `instante_ultima_transicao` (PR #33 — commit `0350e4ec…`, merge `1256628e…`). Também **sem numeração de subetapa** |
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
| Base da reconciliação **pós-PR #95** | `b06c0a43bd2f96b8712638e99c55edfe2fb2f99f` — HEAD da `main` verificado **antes** desta reconciliação |
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

**Baseline funcional corrente: `2446 passed` / Python 3.14.5.**

**Execuções pós-merge da PR #95, registro desta entrega** (2026-09-02, Python 3.14.5) —
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

**Baseline funcional atual: `2446 passed`.** Baseline anterior integrado: **`2162 passed`**
— delta **+284**, correspondente **exatamente** ao arquivo direcionado **novo**
`tests/test_response_bijection.py`; **nenhum teste preexistente foi alterado** pela PR #95. O
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

Existem agora **catorze entregas funcionais posteriores à 3B.7 e SEM numeração oficial de
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
pelo **PR #95**.
**Nenhuma das seis materializa `C`**: o índice `knowledge/indice-respostas-aprovadas.yaml`
**continua inexistente**, o carregador **não conhece caminho implícito** para ele, o
comparador **opera sobre `str` que lhe são entregues**, sem analisar Markdown e sem I/O, os
formatadores **recebem valores já resolvidos**, sem consultar fonte alguma, o avaliador
**recebe predicado e valor já prontos**, julgando **apenas o domínio booleano estrito**, e o
verificador **recebe os três domínios já prontos**, julgando **apenas se a relação é bijetiva
entre eles** — em todos os casos **sem consumidor integrado**. O formato **`hora` continua NÃO
MATERIALIZADO**.
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

1. A **sexta microentrega funcional de `C`** — o **verificador determinístico da
   correspondência bijetiva de `C-A1-B3` / `C-A1-B4` sobre domínios já fornecidos pelo
   chamador**, em `src/casa77_sdr/response_bijection.py` — está **funcionalmente concluída e
   integrada à `main`** pelo **PR #95** (**MERGED**). Ela **não recebeu numeração de
   subetapa** e **não criou nomenclatura normativa `E2`, `E3`, `E4`, `E5` ou `E6`**. A
   **entrega funcional anterior** é a **quinta microentrega — o avaliador determinístico
   booleano de `ASSERTIVA`** (PR #93), que permanece integrada. **A entrega funcional mais
   recente é a do PR #95.** **Nenhuma das seis microentregas materializa `C`**: o índice
   `knowledge/indice-respostas-aprovadas.yaml` **continua INEXISTENTE** e **`C` continua
   ARBITRADA / NÃO MATERIALIZADA como entrega completa**. **VERIFICAR A BIJEÇÃO NÃO É
   MATERIALIZAR `C`**: o verificador **recebe os três domínios já prontos** — fragmentos do
   índice, unidades emitíveis do Markdown e a relação entre eles, todos como **tokens opacos**
   `str` **exata** e pares `tuple` **exata** de dois lados —, julga **somente se a relação é
   bijetiva entre os domínios recebidos**, por **igualdade nativa exata de `str`**, **sem
   normalização, sem coerção, sem *parsing* e sem I/O**, de forma **fail-closed** e com
   **precedência determinística**; **três domínios vazios são bijeção trivial válida somente
   sobre os domínios fornecidos**. A função **não extrai fragmentos do índice**, **não extrai
   unidades do Markdown**, **não decide o que é unidade emitível**, **não define identidade
   física de fragmento**, **não cria identificadores**, **não lê índice real**, **não prova
   completude dos dois domínios**, **não executa a bijeção física do corpus real**, **não
   satisfaz `C-A1-ST7` isoladamente**, **não migra autoridade de status** e **não integra
   consumidor**. **A completude correta dos dois domínios permanece pré-condição do
   chamador.** O formato **`hora` continua NÃO MATERIALIZADO**, por **lacuna normativa ainda
   não arbitrada** sobre a escolha mecânica entre `HH:MM` e `Hh` (`C-A1-F3`) — **e esta
   reconciliação não a arbitra**.
2. Commit funcional atual: `bdd0b2acc415ab6307c7c8da2adbad15f42cb75f`. Merge
   correspondente: `b06c0a43bd2f96b8712638e99c55edfe2fb2f99f`.
3. Baseline funcional atual: **`2446 passed`**, com **`284 passed`** no teste direcionado de
   `tests/test_response_bijection.py`, em **Python 3.14.5** — **zero failures e zero
   errors**, e **zero warnings** sob `-W error`. Baseline anterior integrado: **`2162
   passed`**; delta **+284**, correspondente exatamente ao arquivo direcionado **novo**,
   **sem alteração de teste preexistente**. As **quatro execuções** — **`284`** e **`2446`**,
   ambas também sob `-W error` — foram **medidas após o merge, sobre a `main` integrada**, e
   **reexecutadas nesta reconciliação depois da edição**, com os mesmos resultados; os
   **blobs integrados coincidem com os blobs staged auditados** — ver a seção **Testes**.
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
| C | **Contrato do índice estruturado de respostas aprovadas** (`docs/07-arquitetura-motor-respostas.md` §2.3 e §12, item 19) | **ARBITRADA / NÃO MATERIALIZADA.** Fecha **documentalmente** o contrato do futuro índice `knowledge/indice-respostas-aprovadas.yaml`, **sem criá-lo** e **sem criar componente, estado, evento, transição, condição, critério, pendência ou subetapa**. **Não implementa código, não converte `knowledge/respostas-aprovadas.md`, não remove status do Markdown e não altera `knowledge/`, `src/` ou `tests/`** — esses diretórios permanecem **fora** desta arbitragem. **Não cria marco funcional.** A **materialização do índice permanece futura** e **não é autorizada** por ela. **PRIMEIRA MICROENTREGA FUNCIONAL POSTERIOR — `E1`**: o **validador estrutural fail-closed** do **futuro** índice foi **materializado e integrado depois**, pelo **PR #84**, em `src/casa77_sdr/response_index.py`. **`E1` NÃO materializa `C`**: ela valida a **forma** de uma estrutura já parseada, **sem criar o índice**, **sem loader**, **sem ler `knowledge/**`**, **sem converter o Markdown**, **sem bindings reais**, **sem bijeção 37/37**, **sem C-15**, **sem renderizar** e **sem avaliar `ASSERTIVA` contra dados reais**. **SEGUNDA MICROENTREGA FUNCIONAL POSTERIOR — carregador *fail-closed***: integrado pelo **PR #86**, em `src/casa77_sdr/response_index_load.py`, expondo `IndiceIlegivel` e `carregar_indice(path)`. Ele **lê e recusa** um artefato **explicitamente apontado** — UTF-8, `yaml.SafeLoader`, chave duplicada recusada —, **delega toda a forma** a `validar_indice` e **não conhece caminho implícito** para o índice. **Carregar também NÃO materializa `C`.** **TERCEIRA MICROENTREGA FUNCIONAL POSTERIOR — comparador determinístico de equivalência textual de `C-15b`**: integrado pelo **PR #89**, em `src/casa77_sdr/response_equivalence.py`, expondo `EquivalenciaNaoDeterminavel` e `sao_textualmente_equivalentes(...)` sobre **duas `str` já em representação canônica** — **sem analisar Markdown**, **sem I/O** e **sem conhecer o índice**. **Comparar também NÃO materializa `C`.** **QUARTA MICROENTREGA FUNCIONAL POSTERIOR — formatadores determinísticos de apresentação pura de `C-6`**: integrada pelo **PR #91**, em `src/casa77_sdr/response_format.py`, expondo `FormatoInaplicavel` e as cinco funções puras de **`inteiro`**, **`inteiro_agrupado`**, **`simbolo_moeda`**, **`texto`** e **`lista`**. Elas **recebem valores já resolvidos**, devolvem **apresentação pura** e **não leem fonte alguma, não fazem I/O, não consultam *locale* e não conhecem consumidor**; o formato **`hora` NÃO foi materializado** e sua lacuna normativa **continua ABERTA**. **Formatar também NÃO materializa `C`.** **QUINTA MICROENTREGA FUNCIONAL POSTERIOR — avaliador determinístico booleano de `ASSERTIVA`**: integrada pelo **PR #93**, em `src/casa77_sdr/response_assertion.py`, expondo `AssertivaNaoAvaliavel` e `avaliar_assertiva(predicado, valor)` sobre o vocabulário fechado **`EH_VERDADEIRO`**/**`EH_FALSO`** e um **valor já resolvido**. Ela julga **somente o domínio booleano estrito**: valor fora dele é **NÃO AVALIÁVEL** e **nunca vira assertiva falsa**, **sem coerção e sem *truthiness***. Essa recusa é **delimitação técnica fail-closed daquela microentrega**, e **não** expansão de **`C-7`**; **nenhum domínio futuro de `ASSERTIVA` foi arbitrado**. **Avaliar também NÃO materializa `C`**, e **nenhum consumidor foi integrado.** **SEXTA MICROENTREGA FUNCIONAL POSTERIOR — verificador determinístico da correspondência bijetiva de `C-A1-B3` / `C-A1-B4`**: integrada pelo **PR #95**, em `src/casa77_sdr/response_bijection.py`, expondo `BijecaoInvalida` e `validar_bijecao(fragmentos_indice, unidades_markdown, correspondencias)` sobre **três domínios já fornecidos pelo chamador** — tokens opacos `str` **exata** e pares `tuple` **exata** de dois lados, comparados por **igualdade nativa exata de `str`**, **sem normalização, sem coerção, sem *parsing* e sem I/O**, **fail-closed** e com **precedência determinística**. Ela **não extrai fragmentos do índice**, **não extrai unidades do Markdown**, **não define identidade física de fragmento**, **não lê índice real**, **não prova completude dos domínios**, **não executa a bijeção física do corpus real** e **não satisfaz `C-A1-ST7` isoladamente** — **a completude dos domínios é pré-condição do chamador**. **Verificar a bijeção também NÃO materializa `C`**, e **nenhum consumidor foi integrado.** **`C` permanece ARBITRADA / NÃO MATERIALIZADA** e o índice `knowledge/indice-respostas-aprovadas.yaml` **permanece INEXISTENTE**. Escopo abaixo | Entrega **exclusivamente documental**, em `docs/07-arquitetura-motor-respostas.md` (§2.3 e §12, item 19) e `docs/00-estado-atual.md`. Branch de origem: `docs/arbitragem-c-indice-respostas`. **MICROENTREGA FUNCIONAL POSTERIOR `E1` pelo PR #84** — commit funcional `02f1dd6621c31b90789c646bd8826e685f9ee019`, merge `95ed2ce4e9c54f9bdfb7b3f820e6f9e065cde24e`, branch `feat/c-e1-response-index-validator`, **dois arquivos novos**, **1343 adições / 0 remoções**, baseline **`1374 passed`** / Python 3.14.5. **Aquela integração materializa `E1`, NÃO `C`**. **SEGUNDA MICROENTREGA FUNCIONAL POSTERIOR pelo PR #86** — commit funcional `b2b11e2465c7f332747a806c80b629e995f0f5a6`, merge `9bf68b8fece9ea66c74509490ddf6e02a0aa6f31`, branch `feat/c-response-index-loader`, **três arquivos**, **1086 adições / 5 remoções**, baseline **`1436 passed`** / Python 3.14.5. **Aquela integração materializa o CARREGADOR, NÃO `C`** |
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
| C | Contrato estruturado, legível por máquina, ligando as respostas aprovadas (`Rxx`) aos campos do YAML. **ARBITRADA / NÃO MATERIALIZADA.** **CONTRATO: ARBITRADO** — o contrato documental estruturado do futuro índice está **fechado e aprovado** em `docs/07` §2.3, registrado em `docs/07` §12, item 19. **MATERIALIZAÇÃO: NÃO EXISTE** — o arquivo `knowledge/indice-respostas-aprovadas.yaml` **continua inexistente**; `knowledge/respostas-aprovadas.md` **permanece Markdown** e foi **atualizado apenas como fonte de redação aprovada pela Entrega 2**, **sem conversão em *template* ou índice**; **nenhum status foi removido do Markdown**; e não há *renderer*, *template* físico nem *binding* físico. **A partir do PR #84 existe um VALIDADOR ESTRUTURAL** — a microentrega **`E1`**, `src/casa77_sdr/response_index.py` —, que valida a **forma** de uma estrutura já parseada que pretende ser o índice, **sem criar o índice**, **sem lê-lo**, **sem loader** e **sem ler `knowledge/**`. **A partir do PR #86 existe também um CARREGADOR *fail-closed*** — `src/casa77_sdr/response_index_load.py` —, que lê e recusa um artefato **explicitamente apontado**, delegando toda a forma ao validador. **A partir do PR #89 existe também um COMPARADOR de equivalência textual** — `src/casa77_sdr/response_equivalence.py` —, que julga a equivalência de `C-15b` entre **duas `str` já em representação canônica**, **sem analisar Markdown**, **sem I/O** e **sem conhecer o índice**. **A partir do PR #91 existem também os FORMATADORES determinísticos de `C-6`** — `src/casa77_sdr/response_format.py` —, que materializam **cinco** dos seis formatos do vocabulário fechado — **`inteiro`**, **`inteiro_agrupado`**, **`simbolo_moeda`**, **`texto`** e **`lista`** — como **funções puras sobre valores já resolvidos**; o formato **`hora` NÃO foi materializado** e sua **lacuna normativa continua ABERTA**. **A partir do PR #93 existe também o AVALIADOR determinístico booleano de `ASSERTIVA`** — `src/casa77_sdr/response_assertion.py` —, que julga um **predicado do vocabulário fechado** sobre um **valor já resolvido**, **apenas no domínio booleano estrito**; valor fora dele é **NÃO AVALIÁVEL** e **nunca vira assertiva falsa**, e essa recusa é **delimitação técnica fail-closed daquela microentrega**, **não** expansão de **`C-7`**. **A partir do PR #95 existe também o VERIFICADOR determinístico da correspondência bijetiva de `C-A1-B3` / `C-A1-B4`** — `src/casa77_sdr/response_bijection.py` —, que julga se uma relação **já fornecida pelo chamador** é **bijetiva entre dois domínios também já fornecidos**, sobre **tokens opacos** `str` **exata** e pares `tuple` **exata**, por **igualdade nativa exata de `str`**, **sem normalização, sem coerção, sem *parsing* e sem I/O**; ele **não extrai fragmentos, não extrai unidades, não define identidade física de fragmento, não lê índice real, não prova completude dos domínios, não executa a bijeção física do corpus real e não satisfaz `C-A1-ST7` isoladamente** — **a completude dos domínios é pré-condição do chamador**. **Nenhum dos seis materializa C**: o validador confere a forma de algo que **ainda não existe**; o carregador só sabe **ler** esse algo **quando o caminho lhe é dado explicitamente** — `carregar_indice(...)` recebe o caminho como argumento, **sem caminho implícito ou padrão, sem descobrir o arquivo e sem resolver automaticamente o caminho canônico**; o comparador **recebe as duas `str` prontas**; os formatadores **recebem o valor já resolvido**; o avaliador **recebe predicado e valor já prontos**; e o verificador **recebe os três domínios já prontos** — todos **sem resolver *binding***, **sem ler `caminho_yaml`**, **sem consultar `knowledge/**`** e **sem consumidor integrado**. **Essa atualização de conteúdo NÃO materializa C.** **C continua aberta SOMENTE quanto à materialização.** **S2-D8 é pendência separada**, também **ARBITRADA / NÃO MATERIALIZADA** desde a arbitragem S2-D8 (`docs/07` §4.4.1), e também aberta **somente quanto à materialização** | **materializar** o índice `knowledge/indice-respostas-aprovadas.yaml` pelo contrato de `docs/07` §2.3 — **agora refinado por C-A1**, que fecha equivalência de *template*, formatos, convenção de `lista`, seleção em coleção, unidade de bijeção, migração de status e os alvos `MD-x` — e, só então, implementar `ValidadorConsistenciaBase` e, em cascata, `SeletorFatos` e `ValidadorResposta`. **`C-A2` está ARBITRADA DOCUMENTALMENTE**: os fatos `A1`–`A4` ficam **FECHADOS** e o conteúdo humano `B1`–`B16` foi **APROVADO HUMANAMENTE** e, pela **Entrega 2**, **APLICADO À FONTE DE RESPOSTAS** — **corpus 37 fragmentos / 30 `Rxx`**, com **`FE-1`–`FE-10`, `FE-11a` e `FE-12`–`FE-14` APLICADAS** e **`FE-11b` RETIDA atrás de `C-A1-M4`**. **A aplicação do conteúdo NÃO materializa C**: o índice continua inexistente, nenhuma resposta virou *template*, nenhum status saiu do Markdown, **`knowledge/casa77.yaml` não foi alterado** e **nenhum alvo `MD` foi executado** |

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

"""Composição total e determinística do status de todos os fragmentos emitíveis.

`C-A1-ST8` exige o status de **todos** os fragmentos resolvidos, e o bloco
**"Comportamento da futura composição total de status diante de `SP5`"** de
`docs/07` arbitrou o que essa fronteira faz quando um fragmento permanece **não
resolvido**: ela **falha fechada**, **sem devolver resultado parcial**. Este
módulo materializa **exatamente** essa fronteira — e **nada mais**.

**O que ela devolve.** Um par `(token_canonico, status_canonico)` por
**ocorrência física** de fragmento emitível, na **ordem física do documento**.
Documento vazio, ou sem nenhuma seção `## Rxx`, devolve `tuple()`. O status
pertence **exclusivamente** ao vocabulário fechado de `C-3` — `APROVADO`,
`AGUARDA_APROVACAO`, `BLOQUEADO` —, **sem quarto valor**, **sem sentinela**,
**sem `None`** e **sem valor padrão**.

**O texto chega pronto.** A função **não** abre arquivo, **não** conhece
caminho, **não** decide de onde o texto veio e **não** verifica que ele seja o
corpus oficial. A entrada é uma `str` já em memória. **A origem correta do texto
é pré-condição do chamador** e não é verificável nesta fronteira sem
transformá-la em carregador — que ela deliberadamente não é.

**Três autoridades, nenhuma reimplementada.** A **partição física** é da
associação de seção e fragmentos: `(Rxx, rotulo_literal, tokens_da_instancia)`,
por **instância física**, em ordem física. A **tradução de `ST1`–`ST3`** é de
`propagar_status` (`SP1`–`SP3`), que por sua vez delega a `canonicalizar_status`;
**nenhuma tabela local de rótulo para status existe aqui**, e os três rótulos
físicos de `C-A1-ST1`–`C-A1-ST3` **não** são carregados neste módulo. O **status
declarado sob `PARCIAL`** é da `C14`, cujo retorno é consumido **como veio**;
nada aqui interpreta `status-fragmento`, e **não existe segunda caminhada `PM`**.

**`SP5` — rótulo `G2` válido sem tradução automática.** Um rótulo que não
pertença a `ST1`–`ST3` e não seja `PARCIAL` **continua gramaticalmente válido**,
**literal** e **opaco**: esta fronteira **não** o converte, **não** o normaliza,
**não** o infere e **não** torna o cabeçalho `G2` inválido. Ele é entregue a
`propagar_status`, e a `StatusNaoCanonicalizavel` resultante sobe **intacta** —
**sem `try`/`except`, sem *wrapper*, sem reclassificação, sem enriquecimento de
mensagem, sem `raise from`, sem tocar em `__cause__` ou `__context__`**. **Essa
é a falha fechada arbitrada**, e **nenhuma exceção pública nova é criada** para
ela. Não há retorno parcial, omissão silenciosa, marcador de ausência, sentinela
nem quarto status: **um retorno bem-sucedido desta fronteira não pode coexistir
com fragmento não resolvido por esse ramo de `SP5`**.

**Ordem funcional fixa.** **1.** `associar_fragmentos_a_secao(texto)`, chamada
**uma única vez**; **2.** `extrair_status_por_fragmento(texto)`, chamada **uma
única vez** e **INCONDICIONALMENTE**, mesmo que nenhuma seção seja `PARCIAL`;
**3.** `I1`; **4.** caminhada pelas instâncias físicas, na ordem devolvida pela
associação; **5.** sob `PARCIAL`, consumo sequencial do fluxo da `C14`; **6.**
sob qualquer outro rótulo, `propagar_status`; **7.** `I2`; **8.** `I3`; **9.**
retorno. A `C14` **não** é preguiçosa e **não** é invertida com a associação.

**Precedência, que decorre dessa ordem e não é norma nova.** `C8`
(`RepresentacaoMarcadaInvalida`) → `C12` (`CabecalhoRxxInvalido`) → `C14`/`PM`
(`DeclaracaoDeStatusInvalida`) → `I1` → `SP5` (`StatusNaoCanonicalizavel`) →
`I2`/`I3`. Como `C8` e `C12` são portões integrais da associação, e a `C14`
percorre o documento **inteiro** antes da caminhada local, **uma violação `PM`
fisicamente posterior vence um rótulo desconhecido de `SP5` anterior**. Todas as
exceções públicas das dependências sobem **intactas**.

**Homônimos e tokens repetidos.** Instâncias homônimas de `Rxx` são **entradas
distintas** e produzem pares **separados**, na ordem física, ainda que os seus
tokens sejam **textualmente idênticos** e os seus status **diferentes**. Nada é
agrupado por `Rxx`, deduplicado, reordenado ou consolidado, e **a posição do par
é apenas ordem de leitura, jamais identidade** (`C-A5-I5`).

**A associação token/status sob `PARCIAL` é HERDADA, nunca reimplementada.** A
`C14` já garante, por contrato, os seus pares na **ordem física** — inclusive
para seções homônimas, tokens textualmente repetidos e status divergentes. O
consumo sequencial do fluxo apenas **preserva** essa ordem: o cursor **não é
identidade**, **não cria token**, **não decide status** e **não repareia** coisa
alguma. `I1` verifica **compatibilidade de cobertura e de ordem** entre o fluxo
da `C14` e as ocorrências `PARCIAL` esperadas pela partição física — e **NÃO**
prova, por si, a associação interna token/status que a `C14` já produziu.

**Pureza.** Fora as três fronteiras importadas, o módulo não importa nada:
**zero I/O**, **zero *filesystem***, **zero `open`**, **zero `pathlib`**, **zero
Markdown**, **zero YAML**, **zero JSON**, **zero rede**, **zero LLM**, **zero
relógio**, **zero calendário**, **zero *locale***, **zero variável de
ambiente**, **zero banco**, **zero cache**, **zero logging**, **zero regex**,
**zero `unicodedata`**, **zero estado mutável de módulo**, **zero `global`**,
**zero `nonlocal`**, **zero `assert`**, **zero `dict`**, **zero `set`**, **zero
`zip`**, **zero `sorted`**, **zero `reversed`**, **zero `map`**, **zero
`filter`**, **zero `try`**, **zero `except`**, **zero `raise from`**, **zero
normalização**, **zero coerção**. A entrada **não é alterada**.

**COMPOR STATUS NÃO É MATERIALIZAR `C`.** Um retorno bem-sucedido afirma
**somente** que, no texto recebido, cada ocorrência física de fragmento emitível
tem status resolvido pela autoridade que lhe corresponde. Ele **não** prova que
o texto seja o corpus oficial, que o corpus esteja completo ou aprovado, que as
seções `Rxx` sejam globalmente únicas, e **não** afirma coisa alguma sobre
índice, bijeção física, *bindings*, `ASSERTIVA`, *placeholder*, `caminho_yaml`,
`hora`, `C-7`, equivalência `C-15` ou migração de autoridade. **`C-A1-ST8` NÃO é
declarada satisfeita**: ela exige o status de todos os fragmentos **do corpus**,
o que depende de execução e auditoria próprias sobre os insumos canônicos. A
autoridade de status é externa a esta fronteira, que não a decide nem a migra
(`C-11`); e ela, isoladamente, não materializa `C` nem prova a integração
completa de `C`.
"""

from __future__ import annotations

from casa77_sdr.response_section_membership import associar_fragmentos_a_secao
from casa77_sdr.response_fragment_status import extrair_status_por_fragmento
from casa77_sdr.response_status_propagation import propagar_status

__all__ = ["compor_status_dos_fragmentos"]


# Defeito interno: divergencia entre as fronteiras compostas. Nao e invalidez do
# documento, e por isso nao usa — nem cria — excecao publica.
_INVARIANTE_ESTRUTURAL = "invariante_estrutural"

# Unica regra de regime desta fronteira: so este rotulo literal e resolvido pelo
# fluxo da `C14`. Os tres rotulos fisicos de `C-A1-ST1`-`C-A1-ST3` **nao** sao
# carregados aqui, e nao existe tabela local de rotulo para status.
_ROTULO_DO_REGIME = "PARCIAL"

# Vocabulario fechado de `C-3`, usado **exclusivamente** por `I3` para conferir
# o que as dependencias devolveram. E uma `tuple`, e nao um mapa: nada aqui
# traduz rotulo, e nada pode ser mutado em tempo de execucao.
_STATUS_CANONICOS = ("APROVADO", "AGUARDA_APROVACAO", "BLOQUEADO")


def compor_status_dos_fragmentos(texto: str) -> tuple[tuple[str, str], ...]:
    """Resolve o status de **todos** os fragmentos emitíveis de `texto`.

    Devolve um par `(token_canonico, status_canonico)` por **ocorrência física**
    de fragmento emitível, na **ordem física do documento**, **preservando
    duplicidades** e **sem deduplicar, agrupar ou reordenar**. Um documento
    vazio, ou sem nenhuma seção `## Rxx`, devolve `tuple()`; isso **não** afirma
    que o corpus real esteja vazio, incompleto ou completo.

    O status pertence **exclusivamente** ao vocabulário fechado de `C-3` —
    `APROVADO`, `AGUARDA_APROVACAO`, `BLOQUEADO`. **Nunca** `None`, sentinela,
    marcador de ausência, quarto valor ou valor padrão.

    Sob rótulo de `C-A1-ST1`–`C-A1-ST3`, o status vem **exclusivamente** de
    `propagar_status` (`SP2`/`SP3`): todos os fragmentos daquela instância
    recebem **o mesmo** status canônico, sem exceção por posição, ordem, índice,
    redação, conteúdo, quantidade ou `id`. Sob `PARCIAL`, o status vem
    **exclusivamente** das declarações explícitas lidas pela `C14`, consumidas
    na ordem física em que ela as devolveu — **nenhuma propagação automática** e
    **nenhuma interpretação local de `status-fragmento`**.

    Sob **qualquer outro rótulo `G2` válido**, o status **permanece NÃO
    RESOLVIDO por `SP5`** e a composição **FALHA FECHADA**:
    `StatusNaoCanonicalizavel` sobe **intacta** de `propagar_status`, com classe,
    mensagem, `__cause__` e `__context__` inalterados. **Nada é devolvido
    parcialmente**, o fragmento **não** é omitido, **não** recebe marcador de
    ausência e o cabeçalho `G2` **não** se torna inválido.

    A ordem de execução é **fixa**: **1.** `associar_fragmentos_a_secao(texto)`;
    **2.** `extrair_status_por_fragmento(texto)`, **incondicional**; **3.**
    `I1`; **4.** caminhada pelas instâncias físicas; **5.** consumo do fluxo da
    `C14` sob `PARCIAL`; **6.** `propagar_status` sob qualquer outro rótulo;
    **7.** `I2`; **8.** `I3`; **9.** retorno.

    `RepresentacaoMarcadaInvalida` (`C8`), `CabecalhoRxxInvalido` (`C12`),
    `DeclaracaoDeStatusInvalida` (`C14`) e `StatusNaoCanonicalizavel` (`SP5`)
    propagam **intactas**. Como a `C14` percorre o documento **inteiro** antes da
    caminhada local, **uma violação `PM` fisicamente posterior vence um rótulo
    desconhecido de `SP5` anterior**.

    Levanta `RuntimeError("invariante_estrutural")` — **defeito interno**, não
    invalidez do documento — quando `I1`, `I2` ou `I3` não valem. **Esse é o
    único `raise` originado por este módulo**, e **nenhuma exceção pública nova é
    definida** por esta fronteira.

    **COMPOR STATUS NÃO É MATERIALIZAR `C`** e **NÃO satisfaz `C-A1-ST8`**: o
    sucesso afirma somente o que o texto recebido diz, e a autoridade de status
    é externa a esta fronteira (`C-11`).
    """
    # **1. Particao fisica.** A associacao roda `C12`, que por sua vez roda `C8`
    # como o seu proprio portao: quando esta linha retorna, estrutura `C-A5` e
    # gramatica `G2` ja estao satisfeitas no documento inteiro.
    instancias = associar_fragmentos_a_secao(texto)

    # **2. Fluxo declarado, INCONDICIONAL.** A `C14` e chamada mesmo sem nenhuma
    # secao `PARCIAL`: e assim que uma violacao `PM` fisicamente posterior vence
    # um rotulo desconhecido de `SP5` anterior. Torna-la preguicosa inverteria a
    # precedencia arbitrada.
    declaracoes = extrair_status_por_fragmento(texto)

    # `P` — ocorrencias `PARCIAL` esperadas pela particao fisica, em ordem.
    esperadas_sob_parcial = tuple(
        token
        for _, rotulo, tokens in instancias
        if rotulo == _ROTULO_DO_REGIME
        for token in tokens
    )

    # **3. `I1` — alinhamento do fluxo `PARCIAL`.** Comparacao **integral** de
    # sequencia. Ela prova **compatibilidade de cobertura e de ordem** entre o
    # fluxo da `C14` e as ocorrencias esperadas; ela **nao** prova, por si, a
    # associacao interna token/status que a `C14` ja produziu — essa e herdada
    # do contrato dela.
    if tuple(token for token, _ in declaracoes) != esperadas_sob_parcial:
        raise RuntimeError(_INVARIANTE_ESTRUTURAL)

    pares: list[tuple[str, str]] = []
    # Cursor de **consumo** do fluxo ja alinhado por `I1`. Ele nao e identidade,
    # nao cria token, nao decide status e nao repareia: apenas preserva a ordem
    # fisica em que a `C14` devolveu os seus proprios pares.
    consumidas = 0

    # **4. Caminhada pelas instancias fisicas, na ordem da particao.**
    for _, rotulo, tokens in instancias:
        if rotulo == _ROTULO_DO_REGIME:
            # **5. `PARCIAL`** — consumo do fluxo da `C14`, par a par.
            for _ in tokens:
                pares.append(declaracoes[consumidas])
                consumidas += 1
            continue
        # **6. Qualquer outro rotulo** — a traducao e inteiramente de `SP2`/`SP3`,
        # e um rotulo sem traducao automatica falha fechado aqui, intacto.
        pares.extend(propagar_status(rotulo, tokens))

    # `F` — todas as ocorrencias fisicas esperadas, na ordem da particao.
    esperadas = tuple(
        token for _, _, tokens in instancias for token in tokens
    )

    # **7. `I2` — cobertura.** Comparacao **integral** de sequencia: nenhuma
    # ocorrencia esperada foi omitida ou inventada, e a ordem fisica foi
    # preservada.
    if tuple(token for token, _ in pares) != esperadas:
        raise RuntimeError(_INVARIANTE_ESTRUTURAL)

    # **8. `I3` — vocabulario.** Todo status produzido pertence aos tres valores
    # canonicos de `C-3`. Nenhum quarto valor, nenhum `None`, nenhuma sentinela.
    for _, status in pares:
        if status not in _STATUS_CANONICOS:
            raise RuntimeError(_INVARIANTE_ESTRUTURAL)

    # **9. Retorno.**
    return tuple(pares)

"""Associação física determinística entre instância de seção `Rxx` e fragmentos.

`C-A5-U2` fixa que a unidade emitível **vive dentro** de uma seção `## Rxx`, e
`C-A5-T1`/`C-A5-T2` fixam a identidade canônica `<Rxx>/<id>`. `C8` devolve
**apenas** esses tokens, em ordem física, mas **não expõe a fronteira física de
cada seção**; `C12` devolve **apenas** `(Rxx, rotulo_literal)` por cabeçalho, mas
**não** diz quais fragmentos vivem em qual instância. Este módulo entrega
**exatamente essa associação que falta** — e **nada mais**.

**O que ela devolve.** Uma entrada por **instância física** de `## Rxx`, na ordem
física do documento: `(Rxx, rotulo_literal, tokens)`, onde `tokens` são os
tokens canônicos dos fragmentos emitíveis **daquela instância**, na ordem física
em que aparecem. Documento vazio, ou sem nenhuma seção `## Rxx`, devolve
`tuple()`.

**Seções homônimas são instâncias físicas distintas.** Duas seções fisicamente
homônimas produzem **duas entradas separadas**, na ordem física, ainda que os
seus tokens sejam **textualmente idênticos**. Nada é consolidado por valor de
`Rxx`, nada é deduplicado e nada é agrupado. **A posição da entrada é apenas
ordem de leitura — ela NÃO é identidade** (`C-A5-I5`).

**O texto chega pronto.** A função **não** abre arquivo, **não** conhece
caminho, **não** decide de onde o texto veio e **não** verifica que ele seja o
corpus oficial. A entrada é uma `str` já em memória. **A origem correta do texto
é pré-condição do chamador** e não é verificável nesta fronteira sem
transformá-la em carregador — que ela deliberadamente não é.

**`C12` é o portão, e `C8` é satisfeito transitivamente.** A **primeira**
operação funcional é `extrair_rotulos_de_cabecalho(texto)`. Aquela fronteira já
executa `ler_unidades_marcadas(texto)` como o seu próprio primeiro portão, de
modo que a ordem é **`C8` → `C12` → esta fronteira** sem que este módulo chame
`C8` uma segunda vez — ele **não importa** `response_markdown_units`. Tipo da
entrada e estrutura de `C-A5` pertencem **inteiramente** a `C8`; a gramática `G2`
pertence **inteiramente** a `C12`. `RepresentacaoMarcadaInvalida` e
`CabecalhoRxxInvalido` sobem **intactas** — sem `try`/`except`, sem *wrapper*,
sem reclassificação, sem enriquecimento, sem `raise from` e sem tocar em
`__cause__` ou `__context__`. Como os dois portões percorrem o documento
**integralmente antes**, uma falha estrutural ou `G2` **fisicamente posterior
vence** qualquer anomalia local anterior, e **nada é devolvido parcialmente**.

**Nenhum julgamento estrutural é refeito aqui.** Marcador inválido, bloco sem
marcador, marcador fora de seção, `id` fora da gramática, `id` duplicado e seção
sem unidade **continuam sendo de `C8`**: esta fronteira **não** cria categoria
local para nenhum deles e **não** define exceção pública nova. A caminhada local
apenas **reconhece** o marcador exato de `C-A5-I1` com `id` conforme a `C-A5-I3`
e deriva o token `<Rxx>/<id>` — **sem** usar posição, ordem ou conteúdo como
identidade, **sem** gerar `UUID` ou *hash*, **sem** criar ou alterar `id` e
**sem** deduplicar token.

**Caminhada física local, mínima e compatível com `C8`.** Cabeçalho ATX é
reconhecido **somente na coluna 0**; níveis **1 e 2 encerram** a seção `##`
corrente; um `##` que **não** seja `Rxx` deixa **zero** seção em escopo; um
`## Rxx` válido **abre nova instância física**; níveis **3 a 6 não encerram** a
seção; e uma linha iniciada por `>` pertence à lógica de bloco, **nunca** é
cabeçalho. **Isto não é um novo parser Markdown**: é o mínimo necessário para
manter o contexto físico da instância corrente.

**Política de linha — a estrutural de `C8`/`C12`.** O texto é dividido
**exclusivamente** por `LF`; de cada segmento é removido **no máximo um** `CR`
terminal. `LF` e `CRLF` são estruturalmente equivalentes; um `CR` residual
permanece **conteúdo literal** — ele **não** é removido nem normalizado, e o seu
efeito sobre cabeçalho ou marcador é determinado pelas **respectivas
gramáticas**; `U+2028`, `U+2029`, `U+0085`, `VT`, `FF` e `U+00A0` permanecem
conteúdo. `splitlines()` **não** é usado, *universal newline* **não** é aplicado
e **nenhum** caractere é normalizado.

**Invariante local × `C12`.** A caminhada local constrói a sua **própria**
sequência física de `(Rxx, rotulo_literal)` de **todas** as instâncias e a
compara, **inteira**, com o retorno guardado de `C12` **antes de qualquer retorno
de sucesso**. Divergência é **defeito interno**, não invalidez do documento, e
produz `RuntimeError("invariante_estrutural")` — **nunca** uma exceção pública.
Essa comparação **verifica consistência entre duas caminhadas**: ela **não**
pareia por posição entre saídas independentes, **não** usa `zip`, **não** usa
`dict`, **não** agrupa por `Rxx`, **não** deduplica e **não** trata cardinalidade
como prova de identidade.

**Zero semântica de status.** Esta fronteira é **exclusivamente de contenção e
associação física**. Ela **não** importa `response_status`,
`response_status_propagation` nem `response_fragment_status`; **não**
canonicaliza status, **não** traduz rótulo, **não** decide pertença a
`ST1`–`ST3`, **não** interpreta `PARCIAL`, **não** lê `status-fragmento`,
**não** propaga, **não** aplica, **não** resolve status, **não** decide `SP5` e
**não** cria quarto valor de `C-3`. O `rotulo_literal` é **completamente opaco**
aqui: ele é transportado tal como `C12` o entregou.

**Pureza.** Fora `extrair_rotulos_de_cabecalho`, o módulo não importa nada:
**zero I/O**, **zero *filesystem***, **zero `open`**, **zero `pathlib`**, **zero
YAML**, **zero JSON**, **zero rede**, **zero LLM**, **zero relógio**, **zero
calendário**, **zero *locale***, **zero variável de ambiente**, **zero banco**,
**zero cache**, **zero logging**, **zero regex**, **zero `unicodedata`**, **zero
estado mutável de módulo**, **zero `global`/`nonlocal`**, **zero `assert`**,
**zero `dict`**, **zero `set`**, **zero `zip`**, **zero `sorted`**, **zero
`splitlines`**, **zero `strip`**, **zero normalização**, **zero coerção**. A
entrada **não é alterada**.

**ASSOCIAR FRAGMENTOS À SEÇÃO NÃO É COMPOR STATUS E NÃO É MATERIALIZAR `C`.** Um
retorno bem-sucedido afirma **somente** qual fragmento vive em qual instância
física de seção, e qual é o rótulo literal daquela instância. Ele **não** prova
que o texto seja o corpus oficial, que o corpus esteja completo ou aprovado, que
as seções `Rxx` sejam globalmente únicas, nem afirma coisa alguma sobre status,
propagação `SP1`–`SP7`, `PARCIAL`, índice, bijeção física, *bindings*,
`ASSERTIVA`, *placeholder*, `caminho_yaml`, `hora`, `C-7`, equivalência `C-15`,
migração de autoridade de status ou `C-A1-ST6`–`C-A1-ST10`. A autoridade de
status é externa a esta fronteira, que não a decide nem a migra (`C-11`); e ela,
isoladamente, não materializa `C` nem prova a integração completa de `C`.
"""

from __future__ import annotations

from casa77_sdr.response_header_labels import extrair_rotulos_de_cabecalho

__all__ = ["associar_fragmentos_a_secao"]


# Defeito interno: divergencia entre a caminhada local e o retorno de `C12`.
# Nao e invalidez do documento, e por isso nao usa — nem cria — excecao publica.
_INVARIANTE_ESTRUTURAL = "invariante_estrutural"

# Envelope do marcador de `C-A5-I1`, em duas metades exatas.
_PREFIXO_MARCADOR = "<!-- fragmento: "
_SUFIXO_MARCADOR = " -->"

# Gramatica fechada do `id` de `C-A5-I3` e forma fechada do `Rxx`.
_INICIAL_DO_ID = "F"
_DIGITOS_ASCII = "0123456789"
_ZERO = "0"
_INICIAL_DO_RXX = "R"
_TAMANHO_DO_RXX = 3

# Separador normativo do token canonico (`C-A5-T2`).
_SEPARADOR_DE_TOKEN = "/"

# Separador literal de `G2`: SPACE + EM DASH (`U+2014`) + SPACE.
_SEPARADOR_G2 = " — "

# Sintaxe fisica reconhecida por esta caminhada, na politica de `C8`/`C12`.
_CERQUILHA = "#"
_NIVEL_MAXIMO_ATX = 6
_NIVEL_DOCUMENTO = 1
_NIVEL_SECAO = 2
_ESPACO = " "
_QUEBRA = "\n"
_RETORNO = "\r"

# Deslocamento do trecho `G2` na linha de cabecalho: `##`, o unico espaco
# obrigatorio e os tres caracteres do `Rxx`.
_INICIO_DO_RESTO = _NIVEL_SECAO + 1 + _TAMANHO_DO_RXX


def associar_fragmentos_a_secao(
    texto: str,
) -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    """Associa cada fragmento emitível à sua instância física de seção `Rxx`.

    Devolve **uma entrada por instância física** de `## Rxx`, na **ordem física
    do documento**: `(Rxx, rotulo_literal, tokens)`. `tokens` é a `tuple` dos
    tokens canônicos `<Rxx>/<id>` dos fragmentos **daquela instância**, na ordem
    física em que aparecem. Um documento vazio, ou sem nenhuma seção `## Rxx`,
    devolve `tuple()`; isso **não** afirma que o corpus real esteja vazio,
    incompleto ou completo.

    **Seções homônimas produzem entradas SEPARADAS**, preservadas na ordem
    física, ainda que os seus tokens sejam **textualmente repetidos**: nada é
    consolidado por valor de `Rxx`, deduplicado ou agrupado. **A posição da
    entrada é apenas ordem de leitura, jamais identidade** (`C-A5-I5`).

    A **primeira** operação é `extrair_rotulos_de_cabecalho(texto)`, que por sua
    vez executa `ler_unidades_marcadas(texto)` como o seu próprio portão: a
    ordem é **`C8` → `C12` → esta fronteira**, e `C8` **não** é chamado uma
    segunda vez aqui. `RepresentacaoMarcadaInvalida` e `CabecalhoRxxInvalido`
    propagam **intactas** — nada é capturado, relançado, reclassificado ou
    enriquecido —, e como os dois portões percorrem o documento integralmente
    antes, uma falha estrutural ou `G2` **fisicamente posterior vence** qualquer
    anomalia local anterior. **Nada é devolvido parcialmente.**

    **Nenhuma exceção pública é definida por esta fronteira.** Marcador inválido,
    bloco sem marcador, marcador fora de seção, `id` fora da gramática, `id`
    duplicado e seção sem unidade **continuam sendo julgados por `C8`**.

    Levanta `RuntimeError("invariante_estrutural")` — **defeito interno**, não
    invalidez do documento — se a sequência de `(Rxx, rotulo_literal)` construída
    pela caminhada local divergir, inteira, do retorno guardado de `C12`.

    **ASSOCIAR FRAGMENTOS À SEÇÃO NÃO É COMPOR STATUS E NÃO É MATERIALIZAR `C`.**
    O `rotulo_literal` é **opaco** aqui: nada nesta fronteira o traduz,
    canonicaliza, interpreta ou usa para decidir regime — nem sequer distingue
    `PARCIAL` de qualquer outro rótulo.
    """
    # **Portao integral e anterior.** `C12` roda o portao `C8` antes de aplicar
    # `G2`, de modo que estrutura e gramatica ja estao satisfeitas quando a
    # caminhada local comeca. O retorno e **guardado** porque aqui existe
    # invariante local a verificar.
    rotulos_de_c12 = extrair_rotulos_de_cabecalho(texto)

    linhas = _linhas(texto)
    instancias: list[tuple[str, str | None, tuple[str, ...]]] = []

    secao: str | None = None
    rotulo: str | None = None
    tokens: list[str] = []

    for posicao in range(len(linhas)):
        linha = linhas[posicao]

        nivel = _nivel_do_cabecalho(linha)
        if nivel == _NIVEL_DOCUMENTO or nivel == _NIVEL_SECAO:
            if secao is not None:
                instancias.append((secao, rotulo, tuple(tokens)))
            secao = _rxx_do_cabecalho(linha) if nivel == _NIVEL_SECAO else None
            rotulo = _rotulo_de_g2(linha) if secao is not None else None
            tokens = []
            continue
        if nivel:
            # Niveis 3 a 6 nao encerram a secao `##` corrente.
            continue

        if secao is None:
            # Fora de `## Rxx` nao ha instancia fisica a que associar. Marcador
            # valido fora de secao ja e *fail-closed* em `C8`, e bloco fora de
            # `Rxx` ja e ignorado la; nada e rejulgado aqui.
            continue

        identificador = _identificador_marcado(linha)
        if identificador is None:
            continue
        tokens.append(f"{secao}{_SEPARADOR_DE_TOKEN}{identificador}")

    if secao is not None:
        instancias.append((secao, rotulo, tuple(tokens)))

    # **Invariante local x `C12`, antes de qualquer sucesso.** As duas caminhadas
    # independentes precisam ter visto as mesmas instancias, na mesma ordem
    # fisica, com os mesmos rotulos. Nada aqui pareia por posicao: as sequencias
    # sao comparadas **inteiras**.
    cabecalhos = tuple((rxx, literal) for rxx, literal, _ in instancias)
    if cabecalhos != rotulos_de_c12:
        raise RuntimeError(_INVARIANTE_ESTRUTURAL)

    return tuple(instancias)


def _linhas(texto: str) -> tuple[str, ...]:
    """Divide `texto` **somente** por `LF` e tira **no máximo um** `CR` final.

    Mesma política estrutural de `C8`/`C12`: `splitlines()` não é usado e
    *universal newline* não é aplicado, de modo que `U+2028`, `U+2029`,
    `U+0085`, `VT` e `FF` continuam conteúdo da linha, e um segundo `CR` antes
    do `LF` permanece como `CR` residual dentro dela.
    """
    return tuple(
        linha[:-1] if linha.endswith(_RETORNO) else linha
        for linha in texto.split(_QUEBRA)
    )


def _nivel_do_cabecalho(linha: str) -> int:
    """Nível ATX de `linha`, ou `0` quando ela não é cabeçalho aqui.

    Exige início na **coluna 0**, de um a seis `#` e, em seguida, **espaço ou
    fim de linha**. Cabeçalho indentado, `Setext` e sete ou mais `#` devolvem
    `0` — são conteúdo comum, exatamente como em `C8`.
    """
    if not linha.startswith(_CERQUILHA):
        return 0
    nivel = 0
    for caractere in linha:
        if caractere != _CERQUILHA:
            break
        nivel += 1
    if nivel > _NIVEL_MAXIMO_ATX:
        return 0
    resto = linha[nivel:]
    if resto and not resto.startswith(_ESPACO):
        return 0
    return nivel


def _rxx_do_cabecalho(linha: str) -> str | None:
    """`Rxx` aberto por um cabeçalho de nível 2, ou `None` quando não há.

    O token precisa vir **imediatamente** após o único espaço que segue os dois
    `#`, ser `R` seguido de **exatamente dois dígitos ASCII** e terminar em
    espaço ou fim de linha. Qualquer outra forma deixa **zero `Rxx` em escopo**,
    exatamente como em `C8`.
    """
    corpo = linha[_NIVEL_SECAO:]
    if not corpo.startswith(_ESPACO):
        return None
    corpo = corpo[1:]
    if len(corpo) < _TAMANHO_DO_RXX:
        return None
    if corpo[0] != _INICIAL_DO_RXX:
        return None
    for caractere in corpo[1:_TAMANHO_DO_RXX]:
        if caractere not in _DIGITOS_ASCII:
            return None
    if len(corpo) > _TAMANHO_DO_RXX and corpo[_TAMANHO_DO_RXX] != _ESPACO:
        return None
    return corpo[:_TAMANHO_DO_RXX]


def _rotulo_de_g2(linha: str) -> str | None:
    """Rótulo literal da linha de cabeçalho, ou `None` se a forma não for `G2`.

    `C12` já aceitou o documento inteiro quando esta função roda, de modo que a
    forma `G2` está satisfeita e o rótulo devolvido coincide com o dela. O
    `None` existe como **rede de defeito interno**: ele faz a sequência local
    divergir da de `C12` e cair no invariante, em vez de inventar um rótulo.
    """
    resto = linha[_INICIO_DO_RESTO:]
    ocorrencias = _ocorrencias_do_separador(resto)
    if len(ocorrencias) != 2 or ocorrencias[0] != 0:
        return None
    titulo = resto[len(_SEPARADOR_G2) : ocorrencias[1]]
    literal = resto[ocorrencias[1] + len(_SEPARADOR_G2) :]
    if not titulo or not literal:
        return None
    return literal


def _ocorrencias_do_separador(resto: str) -> tuple[int, ...]:
    """Posições de **todas** as ocorrências do separador literal de `G2`.

    A contagem admite sobreposição, como em `C12`: contá-las evita escolher, por
    inferência, qual decomposição seria "a" forma `G2`.
    """
    posicoes: list[int] = []
    for inicio in range(len(resto) - len(_SEPARADOR_G2) + 1):
        if resto[inicio : inicio + len(_SEPARADOR_G2)] == _SEPARADOR_G2:
            posicoes.append(inicio)
    return tuple(posicoes)


def _identificador_marcado(linha: str) -> str | None:
    """`id` do marcador `C-A5` de `linha`, ou `None` quando ela não é um.

    O envelope é o de `C-A5-I1` e o `id` obedece a `C-A5-I3`. Como `C8` já
    aceitou o documento, um envelope com `id` fora da gramática não chega até
    aqui; a conferência permanece por completude, e devolve `None` em vez de
    levantar — julgar o marcador é de `C8`, nunca desta fronteira.
    """
    if len(linha) < len(_PREFIXO_MARCADOR) + len(_SUFIXO_MARCADOR):
        return None
    if not linha.startswith(_PREFIXO_MARCADOR):
        return None
    if not linha.endswith(_SUFIXO_MARCADOR):
        return None
    identificador = linha[len(_PREFIXO_MARCADOR) : len(linha) - len(_SUFIXO_MARCADOR)]
    if not _id_conforme(identificador):
        return None
    return identificador


def _id_conforme(identificador: str) -> bool:
    """Diz se `identificador` obedece à gramática fechada de `C-A5-I3`.

    `F` seguido de inteiro decimal **ASCII** maior que zero e **sem zero à
    esquerda**. Dígito decimal de outro sistema de escrita **não** é dígito
    aqui.
    """
    if len(identificador) < 2:
        return False
    if identificador[0] != _INICIAL_DO_ID:
        return False
    digitos = identificador[1:]
    if digitos[0] == _ZERO:
        return False
    for caractere in digitos:
        if caractere not in _DIGITOS_ASCII:
            return False
    return True

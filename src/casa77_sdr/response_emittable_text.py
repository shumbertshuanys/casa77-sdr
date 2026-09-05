"""Extração determinística do texto emitível canônico da representação marcada.

`C-A5-U1` fixa a **unidade física** — a sequência maximal de linhas iniciadas
por `>` — e `MT1` a preserva **literal**. `MT2` separa **reconhecimento
estrutural** de **conversão textual**: um bloco pode ser estruturalmente
reconhecido e, ainda assim, ser **recusado** aqui. `MT3`–`MT11` fecham **como**
esse bloco vira uma `str` do domínio canônico `D1`–`D7`, ou é recusado
*fail-closed*. Este módulo materializa **exatamente** essa conversão e devolve,
para cada unidade, o par `(<Rxx>/<id>, texto canônico)`.

**O texto chega pronto.** A função **não** abre arquivo, **não** conhece
caminho, **não** decide de onde o texto veio e **não** verifica que ele seja o
corpus oficial. A entrada é uma `str` já em memória. **A origem correta do texto
é pré-condição do chamador** e não é verificável nesta fronteira sem
transformá-la em carregador — que ela deliberadamente não é.

**`C8` é o juiz estrutural único.** A **primeira** operação funcional da
fronteira é `ler_unidades_marcadas(texto)`. Tipo não-`str`, subclasse de `str` e
qualquer violação de `C-A5` pertencem **integralmente** àquele leitor:
`RepresentacaoMarcadaInvalida` sobe **intacta** — sem `try`/`except`, sem
*wrapper*, sem reclassificação, sem enriquecimento e sem tocar em `__cause__` ou
`__context__`. **Nada é validado localmente antes desse portão**, e a caminhada
local **não decide de novo** se o documento satisfaz `C-A5`: ela apenas
**localiza fisicamente** as mesmas unidades **já declaradas** e **deriva de
novo** o token a partir do `Rxx` do cabeçalho e do `id` do marcador
(`C-A5-T1`, `C-A5-T2`), **jamais** por posição, ordem, índice, `zip` ou conteúdo
(`C-A5-I5`). Com **ambas** as espécies de violação presentes, a estrutural vence,
porque o portão de `C8` é **integral e anterior**: isso é **decisão técnica de
composição**, e **não** norma nova de `C`.

**Invariante entre as duas caminhadas.** Antes de devolver **qualquer** par, a
sequência de tokens localizada aqui é comparada com a sequência devolvida por
`C8`. Divergência é **defeito interno de consistência**, não entrada textual
inválida, e levanta `RuntimeError("invariante_estrutural")` — mensagem **muda**,
sem token, sem `Rxx`, sem `id`, sem conteúdo, sem posição e sem cardinalidade. A
comparação **verifica** as duas caminhadas; ela **não** atribui identidade por
posição.

**Proveniência do terminador — local desta fronteira.** O texto é dividido
**exclusivamente** por `LF`, e de cada segmento é preservada a evidência física
de **ter sido ou não seguido** pelo `LF` que o dividiu. `splitlines()` **não** é
usado, *universal newline* **não** é aplicado, e não há `StringIO`, arquivo ou
qualquer mecanismo cuja política varie conforme o ambiente (`MT8`). Um `CR`
terminal pertence a um `CRLF` **somente** quando o segmento termina em `\\r`
**e** foi efetivamente seguido pelo `\\n`; nesse caso aquele **único** `CR` é
removido e o terminador canônico correspondente é `LF`. Um segmento que termina
em `\\r` **sem** `LF` seguinte é **`CR` isolado** e é **recusado** — e isso vale
mesmo quando `C8`, pela sua própria política de linha, reconheceu o bloco:
**estruturalmente reconhecido ≠ textualmente válido** (`MT2`). **EOF não é
terminador proibido**: a última linha física pode terminar direto no fim do
texto.

**Bloco fora de `## Rxx` está fora do domínio.** Por `C-A5-U2` a unidade vive
**dentro** de uma seção `Rxx`; um bloco fora de qualquer seção é **ignorado
integralmente**, sem par e sem validação de `MT` alguma — exatamente como `C8` o
ignora. Marcador `C-A5` inválido, ou válido fora de `Rxx`, já foi recusado por
`C8` antes de chegar aqui.

**Unicidade global não é criada aqui.** Se `C8` aceitar duas seções físicas
homônimas que produzam o mesmo `<Rxx>/<id>`, esta fronteira devolve **dois
pares** com o mesmo token, na ordem física. Recusar isso seria criar uma falha
nova. A unicidade global pertence a fronteiras posteriores.

**Extrair não é comparar.** O módulo **não** importa e **não** chama o
comparador de equivalência: ele **não** aplica `NFC`, **não** converte quebra
suave em `U+0020`, **não** decide equivalência, **não** devolve `bool` e **não**
renderiza *template*. `MT9` é explícita: **extrator produz representação
canônica; comparador normaliza a quebra suave** (`D3`). As duas
responsabilidades **não se fundem**.

Falha textual é **fail-closed** e imediata: dentro de cada unidade, em ordem
física, valem **1.** o terminador; **2.** a forma do prefixo; **3.** o branco
antes do terminador; **4.** a regra das linhas vazias internas; **5.** a
montagem. A **primeira** violação encerra e **nada é devolvido parcialmente**
(`MT11`). A mensagem carrega **categoria e localizador**, nunca o conteúdo, o
token, o `Rxx`, o `id`, o caractere ofensor, o `repr`, o tipo concreto, um
número de linha, um índice, um tamanho ou uma cardinalidade. A entrada **não é
alterada**.

**EXTRAIR TEXTO CANÔNICO NÃO É MATERIALIZAR `C`.** Um retorno bem-sucedido
significa **somente** que cada bloco declarado do texto recebido satisfaz
`MT3`–`MT11` e produziu uma `str` do domínio `D1`–`D7`. Ele **não** prova que o
texto seja o corpus oficial, que o corpus esteja completo ou aprovado, que as
seções `Rxx` sejam fisicamente únicas, nem afirma coisa alguma sobre status,
propagação de status, `PARCIAL`, índice real, *bindings*, `ASSERTIVA`,
equivalência `C-15`, bijeção física, migração de autoridade de status ou
`C-A1-ST6`–`C-A1-ST10`. O índice continua inexistente, a autoridade de status
continua em `knowledge/respostas-aprovadas.md` (`C-11`) e **`C` continua
ARBITRADA / NÃO MATERIALIZADA**.
"""

from __future__ import annotations

from casa77_sdr.response_markdown_units import ler_unidades_marcadas

__all__ = ["TextoEmitivelInvalido", "extrair_textos_emitiveis"]


class TextoEmitivelInvalido(Exception):
    """O bloco declarado não satisfaz a convenção textual de `MT3`–`MT11`.

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **o
    que** está errado e o localizador diz **em que espécie de construção** —
    nunca o conteúdo, o token, o `Rxx`, o `id`, o caractere ofensor, o `repr`, o
    tipo concreto, um número de linha, um índice ou uma quantidade.

    Ela é **textual**, nunca estrutural: a invalidez estrutural da representação
    marcada continua sendo `RepresentacaoMarcadaInvalida`, levantada por `C8`
    antes desta fronteira executar coisa alguma.
    """


# Categorias tecnicas privadas e fechadas. Elas nomeiam o impedimento textual e
# **nao** sao identificadores normativos novos: `MT12` deixou a taxonomia para o
# mandato tecnico, e esta e a taxonomia dele. Sao **quatro**, e nao existe uma
# quinta categoria de entrada.
_PREFIXO_INVALIDO = "prefixo_invalido"
_LINHA_VAZIA_INVALIDA = "linha_vazia_invalida"
_TERMINADOR_PROIBIDO = "terminador_proibido"
_BRANCO_ANTES_DO_TERMINADOR = "branco_antes_do_terminador"

# Localizadores fechados. Eles nomeiam **a especie de construcao** onde o
# impedimento esta, jamais a sua posicao no documento.
_LINHA = "linha"
_UNIDADE = "unidade"

# Sintaxe fisica reconhecida por esta fronteira.
_QUEBRA = "\n"
_RETORNO = "\r"
_ESPACO = " "
_TABULACAO = "\t"
_CITACAO = ">"
_CERQUILHA = "#"
_VAZIO = ""

# Prefixo estrutural **exato** de `MT3`: `>` mais **um** espaco ASCII. Sao dois
# caracteres, removidos por fatiamento — nunca por `strip`, `lstrip`, regex
# permissiva, CommonMark ou normalizacao generica.
_PREFIXO_DE_CONTEUDO = "> "

# Brancos recusados imediatamente apos o prefixo (`MT4`) e imediatamente antes
# do terminador (`MT10`).
_BRANCOS = (_ESPACO, _TABULACAO)

# Terminadores nao autorizados dentro de uma unidade emitivel (`MT8`). O `CR`
# aparece aqui porque, depois de removido o `CR` **do par** `CRLF`, nenhum `CR`
# pode permanecer: nem isolado no fim do texto, nem residual, nem interno.
_TERMINADORES_PROIBIDOS = (
    _RETORNO,
    "\u2028",
    "\u2029",
    "\u0085",
    "\u000b",
    "\u000c",
)

# Forma fechada do cabecalho ATX e do `Rxx`, na mesma politica do leitor de
# `C8`. Ela existe aqui **somente para localizar** as unidades ja declaradas.
_NIVEL_MAXIMO_ATX = 6
_NIVEL_DOCUMENTO = 1
_NIVEL_SECAO = 2
_INICIAL_DO_RXX = "R"
_TAMANHO_DO_RXX = 3
_DIGITOS_ASCII = "0123456789"

# Envelope do marcador de `C-A5-I1`, em duas metades exatas.
_PREFIXO_DO_MARCADOR = "<!-- fragmento: "
_SUFIXO_DO_MARCADOR = " -->"

# Gramatica fechada do `id` de `C-A5-I3`.
_INICIAL_DO_ID = "F"
_ZERO = "0"

# Separador normativo do token canonico (`C-A5-T2`).
_SEPARADOR = "/"

# Mensagem **muda** do defeito interno de consistencia entre esta fronteira e o
# seu portao `C8`. Ela nao e entrada textual invalida e nao e categoria de
# `TextoEmitivelInvalido`.
_INVARIANTE = "invariante_estrutural"


def extrair_textos_emitiveis(texto: str) -> tuple[tuple[str, str], ...]:
    """Devolve os pares `(<Rxx>/<id>, texto canônico)` de `texto`.

    A tupla vem na **ordem física do documento** e contém **exatamente um** par
    por unidade emitível declarada. Um documento vazio, ou sem nenhuma seção
    `## Rxx`, devolve `tuple()`; isso **não** afirma que o corpus real esteja
    vazio, incompleto ou completo.

    A **primeira** operação é `ler_unidades_marcadas(texto)`. Tipo da entrada e
    estrutura de `C-A5` pertencem **inteiramente** a esse leitor, e a sua
    `RepresentacaoMarcadaInvalida` propaga **intacta** — nada é capturado,
    relançado, reclassificado ou enriquecido aqui. **Só depois** desse portão o
    texto é percorrido localmente para localizar as mesmas unidades, derivar de
    novo o token a partir do `Rxx` e do `id` **declarados** (`C-A5-T1`,
    `C-A5-T2`) e converter o bloco conforme `MT3`–`MT11`. A caminhada local
    **não** rejulga `C-A5`.

    Antes de devolver **qualquer** par, a sequência de tokens localizada é
    comparada com a devolvida por `C8`; divergência levanta
    `RuntimeError("invariante_estrutural")`, que representa **defeito interno**
    de consistência e **não** entrada textual inválida.

    A conversão segue `MT3` — prefixo **exatamente `> `**, dois caracteres, com
    conteúdo **não vazio** e **sem** whitespace adicional —, `MT5`–`MT7` — a
    linha vazia interna é **`>` sozinho**, uma só, nunca em borda e nunca
    consecutiva, projetando **exatamente `\\n\\n`** —, `MT8` — `LF` e `CRLF`
    aceitos como terminador físico, `CR` isolado e terminadores exóticos
    recusados, **nenhum `CR` na saída**, e **EOF sem terminador é válido** —,
    `MT9` — duas linhas de conteúdo consecutivas projetam **exatamente um
    `LF`**, que **não** é convertido em espaço — e `MT10` — espaço ou tab
    imediatamente antes do terminador é **recusado, nunca corrigido**.

    Levanta `TextoEmitivelInvalido` com quatro categorias fechadas:
    `prefixo_invalido: linha`, `terminador_proibido: linha`,
    `branco_antes_do_terminador: linha` e `linha_vazia_invalida: unidade`. A
    ordem local, dentro de cada unidade e em ordem física, é fixa: terminador,
    prefixo, branco terminal e, ao fim, a regra das linhas vazias. A **primeira**
    violação encerra e **nada é devolvido parcialmente** (`MT11`).

    Blocos `>` **fora** de qualquer `## Rxx` estão fora do domínio de `C-A5-U2`
    e são **ignorados integralmente**, sem par e sem validação textual. Se `C8`
    aceitar seções `Rxx` homônimas, dois pares podem trazer o **mesmo** token,
    na ordem física: a unicidade global **não** é decidida aqui.

    **EXTRAIR TEXTO CANÔNICO NÃO É VALIDAR EQUIVALÊNCIA E NÃO É MATERIALIZAR
    `C`.** O sucesso afirma **apenas** que os blocos declarados do texto dado
    satisfazem `MT3`–`MT11` — nada sobre a origem do texto, a completude ou a
    aprovação do corpus, status, `PARCIAL`, índice real, *bindings*,
    `ASSERTIVA`, equivalência `C-15`, bijeção física ou
    `C-A1-ST6`–`C-A1-ST10`.
    """
    # **Portao integral e anterior.** Nenhuma validacao local acontece antes
    # disto: tipo exato, subclasse de `str` e estrutura de `C-A5` sao de `C8`, e
    # a sua excecao sobe intacta.
    tokens_c8 = ler_unidades_marcadas(texto)

    fisicas = _linhas_fisicas(texto)
    estruturais = tuple(_estrutural(bruto) for bruto, _ in fisicas)

    tokens_localizados: list[str] = []
    pares: list[tuple[str, str]] = []

    secao: str | None = None
    posicao = 0
    while posicao < len(estruturais):
        linha = estruturais[posicao]

        if linha.startswith(_CITACAO):
            # Fora de `## Rxx` o bloco esta fora do dominio de `C-A5-U2` e e
            # ignorado inteiro, sem par e sem validacao textual. Dentro de
            # `Rxx`, um bloco sem marcador valido imediatamente antes ja foi
            # recusado por `C8`.
            posicao = _fim_do_bloco(estruturais, posicao)
            continue

        nivel = _nivel_do_cabecalho(linha)
        if nivel in (_NIVEL_DOCUMENTO, _NIVEL_SECAO):
            secao = _rxx_do_cabecalho(linha) if nivel == _NIVEL_SECAO else None
            posicao += 1
            continue
        if nivel:
            # Niveis 3 a 6 nao encerram a secao `##` corrente.
            posicao += 1
            continue

        identificador = _envelope(linha)
        if identificador is None or not _id_conforme(identificador):
            posicao += 1
            continue
        if secao is None:
            # Marcador valido fora de `Rxx` ja foi recusado por `C8`.
            posicao += 1
            continue

        inicio = posicao + 1
        if inicio >= len(estruturais) or not estruturais[inicio].startswith(_CITACAO):
            # Marcador sem bloco imediatamente seguinte ja foi recusado por
            # `C8`.
            posicao += 1
            continue

        fim = _fim_do_bloco(estruturais, inicio)

        # O token e derivado **somente** do `Rxx` declarado no cabecalho e do
        # `id` declarado no marcador (`C-A5-I5`, `C-A5-T1`, `C-A5-T2`).
        token = f"{secao}{_SEPARADOR}{identificador}"
        tokens_localizados.append(token)
        pares.append((token, _texto_da_unidade(fisicas[inicio:fim])))
        posicao = fim

    if tuple(tokens_localizados) != tokens_c8:
        # Defeito interno de consistencia entre esta fronteira e o seu portao.
        # A mensagem e deliberadamente muda.
        raise RuntimeError(_INVARIANTE)

    return tuple(pares)


def _linhas_fisicas(texto: str) -> tuple[tuple[str, bool], ...]:
    """Segmentos de `texto` com a evidência física do `LF` que os dividiu.

    A divisão é **exclusivamente** por `LF`. Cada elemento é
    `(conteudo_bruto_do_segmento, seguido_por_lf)`: todo segmento anterior ao
    último foi seguido pelo `LF` da divisão, e o último só foi seguido por `LF`
    quando o texto **efetivamente termina** em `\\n`. Nenhum `CR` é removido
    aqui — a proveniência precisa chegar **intacta** à validação de `MT8`.
    """
    segmentos = texto.split(_QUEBRA)
    anteriores = tuple((segmento, True) for segmento in segmentos[:-1])
    if segmentos[-1] == _VAZIO:
        return anteriores
    return anteriores + ((segmentos[-1], False),)


def _estrutural(bruto: str) -> str:
    """Visão estrutural do segmento, na mesma política de linha do leitor.

    Remove **no máximo um** `CR` terminal, exatamente como `C8` faz, para que a
    localização de cabeçalhos, marcadores e blocos coincida com a dele. Esta
    visão **não** é usada para validar `MT8`: aquela validação consome a
    evidência física original, e é por isso que um `CR` isolado no fim do texto
    pode ser estruturalmente aceito por `C8` e ainda assim recusado aqui
    (`MT2`).
    """
    return bruto[:-1] if bruto.endswith(_RETORNO) else bruto


def _fim_do_bloco(estruturais: tuple[str, ...], inicio: int) -> int:
    """Índice logo após a sequência maximal de linhas `>` iniciada em `inicio`."""
    fim = inicio
    while fim < len(estruturais) and estruturais[fim].startswith(_CITACAO):
        fim += 1
    return fim


def _texto_da_unidade(linhas: tuple[tuple[str, bool], ...]) -> str:
    """Converte as linhas físicas de uma unidade em `str` do domínio `D1`–`D7`.

    A ordem é fixa e fail-closed: por linha, em ordem física, **1.** o
    terminador (`MT8`), **2.** a forma do prefixo (`MT3`, `MT4`) e **3.** o
    branco imediatamente antes do terminador (`MT10`); depois, sobre a unidade
    inteira, **4.** a regra das linhas vazias (`MT5`–`MT7`); e só então **5.** a
    montagem. A primeira violação encerra e nada é montado.
    """
    classificadas: list[tuple[bool, str]] = []
    for bruto, seguido_por_lf in linhas:
        resto = _sem_terminador(bruto, seguido_por_lf)

        if resto == _CITACAO:
            classificadas.append((True, _VAZIO))
            continue

        if not resto.startswith(_PREFIXO_DE_CONTEUDO):
            raise _invalido(_PREFIXO_INVALIDO, _LINHA)
        conteudo = resto[len(_PREFIXO_DE_CONTEUDO) :]
        if not conteudo or conteudo[0] in _BRANCOS:
            raise _invalido(_PREFIXO_INVALIDO, _LINHA)
        if conteudo[-1] in _BRANCOS:
            raise _invalido(_BRANCO_ANTES_DO_TERMINADOR, _LINHA)

        classificadas.append((False, conteudo))

    _exigir_linhas_vazias_validas(classificadas)

    pedacos: list[str] = []
    for indice, (vazia, conteudo) in enumerate(classificadas):
        if indice:
            # Cada fronteira fisica entre linhas projeta **exatamente um** `LF`
            # (`MT9`); a linha vazia interna nada acrescenta, de modo que a sua
            # vizinhanca projeta **exatamente** `\n\n` (`MT5`, `D4`).
            pedacos.append(_QUEBRA)
        if not vazia:
            pedacos.append(conteudo)
    return _VAZIO.join(pedacos)


def _sem_terminador(bruto: str, seguido_por_lf: bool) -> str:
    """Conteúdo da linha sem o `CR` do par `CRLF`, recusando `MT8`.

    O `CR` terminal pertence a um `CRLF` **somente** quando o segmento termina
    em `\\r` **e** foi efetivamente seguido pelo `\\n` da divisão; nesse caso
    aquele **único** `CR` é removido e o terminador canônico é `LF`. Terminar em
    `\\r` **sem** `LF` seguinte é **`CR` isolado** e é recusado. `EOF` sem
    terminador **não** é terminador proibido.
    """
    resto = bruto[:-1] if seguido_por_lf and bruto.endswith(_RETORNO) else bruto
    for proibido in _TERMINADORES_PROIBIDOS:
        if proibido in resto:
            raise _invalido(_TERMINADOR_PROIBIDO, _LINHA)
    return resto


def _exigir_linhas_vazias_validas(classificadas: list[tuple[bool, str]]) -> None:
    """Aplica `MT5`–`MT7` sobre a unidade inteira, sem colapsar nem corrigir.

    Linha `>` na **borda inicial** ou na **borda final** faria a saída começar
    ou terminar em `LF` (`D7`); **duas ou mais** consecutivas produziriam três
    ou mais `LF` (`D4`, `D7`). Ambos são recusados.
    """
    if classificadas[0][0] or classificadas[-1][0]:
        raise _invalido(_LINHA_VAZIA_INVALIDA, _UNIDADE)
    anterior_vazia = False
    for vazia, _ in classificadas:
        if vazia and anterior_vazia:
            raise _invalido(_LINHA_VAZIA_INVALIDA, _UNIDADE)
        anterior_vazia = vazia


def _nivel_do_cabecalho(linha: str) -> int:
    """Nível ATX de `linha`, ou `0` quando ela não é cabeçalho aqui.

    Mesma política parcial do leitor de `C8`: início na **coluna 0**, de um a
    seis `#` e, em seguida, **espaço ou fim de linha**. Cabeçalho indentado,
    `Setext` e sete ou mais `#` devolvem `0`.
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
    """`Rxx` **declarado** por um cabeçalho de nível 2, ou `None` quando não há."""
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


def _envelope(linha: str) -> str | None:
    """Conteúdo interno do envelope de `C-A5-I1`, ou `None` se não houver um."""
    if len(linha) < len(_PREFIXO_DO_MARCADOR) + len(_SUFIXO_DO_MARCADOR):
        return None
    if not linha.startswith(_PREFIXO_DO_MARCADOR):
        return None
    if not linha.endswith(_SUFIXO_DO_MARCADOR):
        return None
    return linha[len(_PREFIXO_DO_MARCADOR) : len(linha) - len(_SUFIXO_DO_MARCADOR)]


def _id_conforme(identificador: str) -> bool:
    """Diz se `identificador` obedece à gramática fechada de `C-A5-I3`."""
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


def _invalido(categoria: str, localizador: str) -> TextoEmitivelInvalido:
    return TextoEmitivelInvalido(f"{categoria}: {localizador}")

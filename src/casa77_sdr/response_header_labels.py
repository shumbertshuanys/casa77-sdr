"""Extração determinística do rótulo literal de status do cabeçalho `Rxx`.

O bloco **"Gramática física do rótulo de status no cabeçalho `Rxx`"** de
`docs/07` arbitrou a forma física `G2`:

```text
## Rxx — <titulo> — <rotulo>
```

com o **separador literal** de **três caracteres** `U+0020 U+2014 U+0020` —
SPACE + EM DASH + SPACE — ocorrendo **exatamente duas vezes** (`GR2.1`),
título e rótulo **não vazios** (`GR2.2`, `GR2.3`), nenhum deles começando ou
terminando com espaço ASCII `U+0020` ou tab `U+0009` (`GR2.4`), `-` e `–`
**não** equivalentes ao separador (`GR2.7`), espaçamento divergente **não
corrigido** (`GR2.8`), `strip`, normalização, colapso, inferência e tolerância
implícita **proibidos** (`GR2.9`) e rótulo **literal/opaco** (`GR2.10`, `GR3`).
Este módulo materializa **exatamente** essa gramática e devolve, para cada
cabeçalho `Rxx` estruturalmente reconhecido, o par `(Rxx, rotulo_literal)`.

**O texto chega pronto.** A função **não** abre arquivo, **não** conhece
caminho, **não** decide de onde o texto veio e **não** verifica que ele seja o
corpus oficial. A entrada é uma `str` já em memória. **A origem correta do texto
é pré-condição do chamador** e não é verificável nesta fronteira sem
transformá-la em carregador — que ela deliberadamente não é.

**`C8` é o portão estrutural único — e somente isso.** A **primeira** operação
funcional da fronteira é `ler_unidades_marcadas(texto)`. Tipo não-`str`,
subclasse de `str` e qualquer violação de `C-A5` pertencem **integralmente**
àquele leitor: `RepresentacaoMarcadaInvalida` sobe **intacta** — sem
`try`/`except`, sem *wrapper*, sem reclassificação, sem enriquecimento e sem
tocar em `__cause__` ou `__context__`. **Nada é validado localmente antes desse
portão.** O resultado do leitor **não é guardado nem comparado**: `C8` devolve
somente tokens `<Rxx>/<id>` e **não expõe fronteiras físicas de seção**, de
modo que, com seções homônimas, nenhum conjunto, contagem ou compressão por
`Rxx` provaria correspondência 1:1 entre cabeçalhos — **não existe invariante
local × `C8` aqui**. Só depois do sucesso do portão a caminhada local localiza
os cabeçalhos `Rxx` já pertencentes ao domínio estrutural aceito.

**Política de linha — a estrutural de `C8`.** O texto é dividido
**exclusivamente** por `LF`; de cada segmento é removido **no máximo um** `CR`
terminal. `LF` e `CRLF` são estruturalmente equivalentes; um `CR` residual
permanece **conteúdo literal**; `U+2028`, `U+2029`, `U+0085`, `VT` e `FF`
permanecem conteúdo; `U+00A0` **não** é espaço ASCII nem tab. `splitlines()`
**não** é usado, *universal newline* **não** é aplicado e **nenhum** caractere é
normalizado. A política `MT8` de `C11` **não** é importada para cabeçalhos.

**Reconhecimento local do cabeçalho — deliberadamente mínimo.** A caminhada
reproduz **somente** o necessário para localizar um cabeçalho `Rxx` no domínio
já existente: linha iniciada na **coluna 0** por `##` seguido de **exatamente
um** espaço, `R`, **exatamente dois dígitos ASCII** e, em seguida, espaço ou fim
de linha. Nenhum *helper* privado de `C8` é importado e nenhum vira API pública.

**Aplicação de `G2` ao resto da linha.** Após `## Rxx`, valem em ordem fixa:
**1.** o separador literal precisa ocorrer **imediatamente** após `Rxx` — sua
ausência **nessa posição** é `separador_ausente: cabecalho`, o que cobre tanto
a linha sem separador algum quanto `-`, `–`, variantes Unicode e espaçamento
divergente; **2.** o separador literal precisa ocorrer **exatamente duas
vezes**, contadas **inclusive quando sobrepostas** — uma sequência como
`A — — B`, decomponível de mais de uma forma, é recusada como
`cardinalidade_de_separador: cabecalho` em vez de resolvida por inferência;
**3.** título vazio — `segmento_vazio: titulo`; **4.** título com espaço ou tab
de borda — `branco_de_borda: titulo`; **5.** rótulo vazio — `segmento_vazio:
rotulo`; **6.** rótulo com espaço ou tab de borda — `branco_de_borda: rotulo`.
Fora dessas condições, título e rótulo são **opacos**: qualquer conteúdo
interno que não forme o separador literal é preservado tal como está.

**Precedência entre cabeçalhos e entre fronteiras.** Os cabeçalhos são
percorridos em ordem física; a **primeira** violação encerra e **nada é
devolvido parcialmente**. Como o portão `C8` roda **integralmente antes**, uma
falha estrutural posterior no documento **vence** uma falha `G2` fisicamente
anterior — decisão técnica de composição, **não** norma nova de `C`.

**Homônimos não são deduplicados.** Se `C8` aceitar duas seções físicas com o
mesmo `Rxx`, esta fronteira devolve **dois pares**, na ordem física. Não há
`dict`, sobrescrita, recusa ou unicidade global — essa unicidade pertence a
fronteiras posteriores.

**`PARCIAL` é extraído literalmente e continua não resolvido.** O rótulo
`PARCIAL` é fisicamente extraível por `G2` como qualquer outro e é devolvido
**tal como está**. Este módulo **não** importa a fronteira de canonicalização
de status, **não** a chama, **não** traduz, **não** propaga, **não** mapeia e
**não** decide pertença a `ST1`–`ST3`. **EXTRAIR `PARCIAL` NÃO É RESOLVER
`PARCIAL`.**

Falha `G2` é **fail-closed** e imediata. A mensagem carrega **categoria e
localizador**, nunca o `Rxx`, o título, o rótulo, o conteúdo, o caractere
ofensor, o `repr`, o tipo concreto, um número de linha, um índice, um tamanho
ou uma cardinalidade numérica. A entrada **não é alterada**.

**EXTRAIR O RÓTULO NÃO É CANONICALIZAR STATUS E NÃO É MATERIALIZAR `C`.** Um
retorno bem-sucedido significa **somente** que cada cabeçalho `Rxx` do texto
recebido satisfaz `G2` e produziu o seu rótulo literal. Ele **não** prova que o
texto seja o corpus oficial, que o corpus esteja completo ou aprovado, que as
seções `Rxx` sejam fisicamente únicas, nem afirma coisa alguma sobre status
canônico, propagação `SP1`–`SP7`, mapeamento de `PARCIAL`, índice, bijeção
física, *bindings*, *placeholder*, `caminho_yaml`, `hora`, `C-7`, equivalência
`C-15`, migração de autoridade de status ou `C-A1-ST6`–`C-A1-ST10`. A
autoridade de status continua no Markdown aprovado (`C-11`) e **`C` continua
ARBITRADA / NÃO MATERIALIZADA**.
"""

from __future__ import annotations

from casa77_sdr.response_markdown_units import ler_unidades_marcadas

__all__ = ["CabecalhoRxxInvalido", "extrair_rotulos_de_cabecalho"]


class CabecalhoRxxInvalido(Exception):
    """Um cabeçalho `Rxx` estruturalmente reconhecido não satisfaz `G2`.

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **o
    que** está errado e o localizador diz **em que segmento** do cabeçalho —
    nunca o `Rxx`, o título, o rótulo, o conteúdo, o caractere ofensor, o
    `repr`, o tipo concreto, um número de linha, um índice ou uma quantidade.

    Ela é **gramatical**, nunca estrutural: a invalidez estrutural da
    representação marcada continua sendo `RepresentacaoMarcadaInvalida`,
    levantada por `C8` antes desta fronteira executar coisa alguma.
    """


# Categorias tecnicas privadas e fechadas. Elas nomeiam as quatro especies de
# impedimento de `GR4` e **nao** sao identificadores normativos novos de `C`.
_SEPARADOR_AUSENTE = "separador_ausente"
_CARDINALIDADE_DE_SEPARADOR = "cardinalidade_de_separador"
_SEGMENTO_VAZIO = "segmento_vazio"
_BRANCO_DE_BORDA = "branco_de_borda"

# Localizadores fechados. Eles nomeiam **o segmento** do cabecalho onde o
# impedimento esta, jamais a sua posicao no documento.
_CABECALHO = "cabecalho"
_TITULO = "titulo"
_ROTULO = "rotulo"

# Separador literal de `G2`: SPACE + EM DASH (`U+2014`) + SPACE. Tres
# caracteres exatos; nada e equivalente a ele.
_SEPARADOR = " — "

# Brancos de borda recusados por `GR2.4`: espaco ASCII e tab. `U+00A0` nao
# pertence a este par, deliberadamente.
_ESPACO = " "
_TABULACAO = "\t"
_BRANCOS = (_ESPACO, _TABULACAO)

# Forma fechada do cabecalho `## Rxx`, na mesma politica do leitor de `C8`.
# Ela existe aqui **somente para localizar** os cabecalhos ja aceitos.
_ABERTURA_DE_SECAO = "## "
_INICIAL_DO_RXX = "R"
_TAMANHO_DO_RXX = 3
_DIGITOS_ASCII = "0123456789"

# Politica estrutural de linha de `C8`.
_QUEBRA = "\n"
_RETORNO = "\r"


def extrair_rotulos_de_cabecalho(texto: str) -> tuple[tuple[str, str], ...]:
    """Devolve os pares `(Rxx, rotulo_literal)` dos cabeçalhos `Rxx` de `texto`.

    A tupla vem na **ordem física do documento** e contém **exatamente um** par
    por cabeçalho `## Rxx` estruturalmente reconhecido; o título **não** aparece
    na saída. Um documento vazio, ou sem nenhuma seção `## Rxx`, devolve
    `tuple()`; isso **não** afirma que o corpus real esteja vazio, incompleto ou
    completo. Seções homônimas produzem **múltiplos pares**, preservados na
    ordem física — não há `dict`, deduplicação nem unicidade global.

    A **primeira** operação é `ler_unidades_marcadas(texto)`, usada
    **exclusivamente como portão estrutural**. Tipo da entrada e estrutura de
    `C-A5` pertencem **inteiramente** a esse leitor, e a sua
    `RepresentacaoMarcadaInvalida` propaga **intacta** — nada é capturado,
    relançado, reclassificado ou enriquecido aqui. O que o leitor devolve **não
    é guardado nem comparado**: não existe invariante local × `C8`. **Só
    depois** desse portão o texto é percorrido localmente para localizar os
    cabeçalhos `Rxx` e aplicar `G2` a cada um.

    Levanta `CabecalhoRxxInvalido` com quatro categorias fechadas e, por
    cabeçalho, em ordem fixa: `separador_ausente: cabecalho` — o separador
    literal não ocorre imediatamente após `Rxx`, o que inclui `-`, `–`,
    variantes Unicode e espaçamento divergente; `cardinalidade_de_separador:
    cabecalho` — o separador literal não ocorre exatamente duas vezes,
    contadas inclusive quando sobrepostas; `segmento_vazio: titulo`;
    `branco_de_borda: titulo`; `segmento_vazio: rotulo`; `branco_de_borda:
    rotulo`. A **primeira** violação, em ordem física, encerra e **nada é
    devolvido parcialmente**. Como `C8` roda integralmente antes, uma falha
    estrutural posterior vence uma falha `G2` anterior.

    O rótulo devolvido é **literal e opaco**: `PARCIAL` volta como `PARCIAL`,
    `APROVADO com handoff obrigatório` volta inteiro, e nada aqui decide
    pertença a `ST1`–`ST3`, traduz, canonicaliza, propaga ou resolve.

    **EXTRAIR O RÓTULO NÃO É CANONICALIZAR STATUS E NÃO É MATERIALIZAR `C`.**
    O sucesso afirma **apenas** que os cabeçalhos `Rxx` do texto dado satisfazem
    `G2` — nada sobre a origem do texto, a completude ou a aprovação do corpus,
    status canônico, `PARCIAL`, índice, bijeção física, *bindings*,
    equivalência `C-15` ou `C-A1-ST6`–`C-A1-ST10`.
    """
    # **Portao integral e anterior.** Nenhuma validacao local acontece antes
    # disto: tipo exato, subclasse de `str` e estrutura de `C-A5` sao de `C8`,
    # e a sua excecao sobe intacta. O resultado **nao** e guardado: `C8` nao
    # expoe fronteiras de secao, e nenhum invariante local e afirmado aqui.
    ler_unidades_marcadas(texto)

    pares: list[tuple[str, str]] = []
    for linha in _linhas(texto):
        rxx = _rxx_do_cabecalho(linha)
        if rxx is None:
            continue
        resto = linha[len(_ABERTURA_DE_SECAO) + _TAMANHO_DO_RXX :]
        pares.append((rxx, _rotulo_g2(resto)))
    return tuple(pares)


def _linhas(texto: str) -> tuple[str, ...]:
    """Divide `texto` **somente** por `LF` e tira **no máximo um** `CR` final.

    Mesma política estrutural do leitor de `C8`: `splitlines()` não é usado e
    *universal newline* não é aplicado, de modo que `U+2028`, `U+2029`,
    `U+0085`, `VT` e `FF` continuam conteúdo da linha, e um segundo `CR` antes
    do `LF` permanece como `CR` residual dentro da linha.
    """
    return tuple(
        linha[:-1] if linha.endswith(_RETORNO) else linha
        for linha in texto.split(_QUEBRA)
    )


def _rxx_do_cabecalho(linha: str) -> str | None:
    """`Rxx` **declarado** por um cabeçalho `## Rxx`, ou `None` quando não há.

    Reproduz **somente** o necessário do domínio estrutural de `C8`: `##` na
    coluna 0 seguido de **exatamente um** espaço, `R`, **exatamente dois
    dígitos ASCII** e, em seguida, espaço ou fim de linha. Qualquer outra forma
    — nível diferente, indentação, espaçamento extra, dígito não ASCII — **não
    é cabeçalho `Rxx`** aqui, exatamente como não é lá.
    """
    if not linha.startswith(_ABERTURA_DE_SECAO):
        return None
    corpo = linha[len(_ABERTURA_DE_SECAO) :]
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


def _rotulo_g2(resto: str) -> str:
    """Rótulo literal do trecho que segue `## Rxx`, conforme `G2`.

    `resto` é tudo o que vem após `Rxx` na linha estrutural. A ordem é fixa e
    fail-closed: **1.** o separador literal na posição imediatamente após
    `Rxx`; **2.** exatamente duas ocorrências do separador, contadas inclusive
    quando sobrepostas; **3.** título não vazio; **4.** título sem branco de
    borda; **5.** rótulo não vazio; **6.** rótulo sem branco de borda. A
    primeira violação encerra.
    """
    ocorrencias = _ocorrencias_do_separador(resto)
    if not ocorrencias or ocorrencias[0] != 0:
        raise _invalido(_SEPARADOR_AUSENTE, _CABECALHO)
    if len(ocorrencias) != 2:
        raise _invalido(_CARDINALIDADE_DE_SEPARADOR, _CABECALHO)

    # Quando a segunda ocorrencia se sobrepoe a primeira nao existe texto entre
    # elas, e a fatia devolve a `str` vazia — o titulo e vazio, sem inferencia.
    titulo = resto[len(_SEPARADOR) : ocorrencias[1]]
    rotulo = resto[ocorrencias[1] + len(_SEPARADOR) :]

    if not titulo:
        raise _invalido(_SEGMENTO_VAZIO, _TITULO)
    if titulo[0] in _BRANCOS or titulo[-1] in _BRANCOS:
        raise _invalido(_BRANCO_DE_BORDA, _TITULO)
    if not rotulo:
        raise _invalido(_SEGMENTO_VAZIO, _ROTULO)
    if rotulo[0] in _BRANCOS or rotulo[-1] in _BRANCOS:
        raise _invalido(_BRANCO_DE_BORDA, _ROTULO)
    return rotulo


def _ocorrencias_do_separador(resto: str) -> tuple[int, ...]:
    """Posições de **todas** as ocorrências do separador literal em `resto`.

    A contagem admite sobreposição: em `A — — B` há duas ocorrências que
    compartilham um espaço. Contá-las evita escolher, por inferência, qual das
    decomposições possíveis seria "a" forma `G2` — a linha é recusada.
    """
    posicoes: list[int] = []
    for inicio in range(len(resto) - len(_SEPARADOR) + 1):
        if resto[inicio : inicio + len(_SEPARADOR)] == _SEPARADOR:
            posicoes.append(inicio)
    return tuple(posicoes)


def _invalido(categoria: str, localizador: str) -> CabecalhoRxxInvalido:
    return CabecalhoRxxInvalido(f"{categoria}: {localizador}")

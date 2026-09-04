"""Leitura determinística das identidades da representação marcada `C-A5`.

`C-A5` arbitrou a **identidade física do fragmento emitível**: a unidade é o
**bloco de citação contíguo** (`C-A5-U1`), ela **vive dentro de uma seção
`## Rxx`** (`C-A5-U2`), ela **existe se e somente se** estiver **imediatamente
precedida por marcador válido** (`C-A5-U3`, `C-A5-I2`), o marcador tem a forma
`<!-- fragmento: <id> -->` (`C-A5-I1`), o `id` obedece a gramática fechada `F`
seguido de inteiro decimal ASCII maior que zero e sem zero à esquerda
(`C-A5-I3`), a unicidade do `id` é **local ao respectivo `Rxx`** (`C-A5-I4`,
C-2h) e a identidade canônica é o token derivado `<Rxx>/<id>` (`C-A5-T1`,
`C-A5-T2`). Este módulo **lê essa representação** e devolve **apenas** esses
tokens.

**O texto chega pronto.** A função **não** abre arquivo, **não** conhece
caminho, **não** decide de onde o texto veio e **não** verifica que ele seja o
corpus oficial. A entrada é uma `str` já em memória. **A origem correta do texto
é pré-condição do chamador** e não é verificável nesta fronteira sem
transformá-la em carregador — que ela deliberadamente não é.

**Só identidade, nunca conteúdo.** A saída carrega **exclusivamente** tokens
`<Rxx>/<id>`. O módulo **não** extrai o texto emitível do bloco, **não** lê
status, **não** propaga status de cabeçalho, **não** mapeia `PARCIAL`, **não**
cria índice, **não** lê índice, **não** resolve *binding*, **não** avalia
`ASSERTIVA`, **não** renderiza, **não** normaliza `C-15` e **não** executa a
bijeção física. O token é **derivado, nunca armazenado** (`C-A5-T5`).

**Política de linha — local a esta fronteira.** O texto é dividido
**exclusivamente** por `LF`; de cada linha resultante é removido **no máximo
um** `CR` terminal. Assim `LF` e `CRLF` representam a **mesma** abstração de
linha, e o mesmo documento nas duas terminações produz **resultado idêntico**.
Terminação mista **não é diagnosticada** aqui. `splitlines()` **não** é usado e
o modo *universal newline* **não** é aplicado: `U+2028`, `U+2029`, `U+0085`,
`VT` e `FF` permanecem **conteúdo normal** da `str`, jamais separadores. Nenhum
outro caractere é normalizado. **Esta decisão é local deste leitor e não altera
`C-15`.**

**Delimitação de seção — deliberadamente parcial.** Não há parser Markdown
aqui. Reconhece-se **somente** cabeçalho ATX que comece na **coluna 0** com um a
seis `#` seguidos de **espaço ou fim de linha**; cabeçalho **indentado não é
reconhecido**. Nível 1 encerra a seção `##` corrente e deixa **zero `Rxx` em
escopo**; nível 2 encerra a seção anterior e abre `Rxx` **apenas** quando o
primeiro token após o único espaço obrigatório for `R` seguido de **exatamente
dois dígitos ASCII** e, em seguida, espaço ou fim de linha; um `##` não-`Rxx`
deixa **zero `Rxx` em escopo**; níveis 3 a 6 **não** encerram a seção `##`
corrente. Uma linha iniciada por `>` pertence **primeiro** à lógica de bloco e
**nunca** é cabeçalho. **Não** são interpretados: `Setext`, *code fence*, bloco
`HTML`, código indentado ou qualquer outra construção de Markdown — texto que
apenas **pareça** cabeçalho ou marcador dentro dessas construções é lido como o
que ele fisicamente é.

**Reconhecimento do marcador em dois estágios.** Primeiro o **envelope**: a
linha precisa ser **exatamente** o prefixo `<!-- fragmento: `, um conteúdo
interno de `id` — **inclusive vazio** — e o sufixo ` -->`, **sem nada antes ou
depois**. Por isso `<!-- fragmento:F1 -->` e `<!-- fragmento: F1 --> extra`
**não são marcadores**, ao passo que o envelope com conteúdo interno vazio **é**
candidato e cai na gramática inválida. Depois a **gramática** do `id`
(`C-A5-I3`). Um quase-marcador que falhe o envelope é **conteúdo comum**, não
marcador defeituoso.

**Bloco de citação fora de `## Rxx` está fora do domínio desta fronteira.** Por
`C-A5-U2` a unidade vive **dentro** de uma seção `Rxx`; um bloco não marcado que
esteja fora de qualquer seção **não é automaticamente unidade emitível**, e por
isso é **ignorado estruturalmente** — o bloco maximal inteiro é saltado, sem
token, sem erro e sem leitura do seu conteúdo. Dentro de uma seção `Rxx`, ao
contrário, um bloco sem marcador válido continua **fail-closed**; e um
**marcador `C-A5` válido fora de `Rxx` também continua fail-closed**.

**Unicidade global não é garantida, e isso é deliberado.** A função **não**
verifica a unicidade física das seções `## Rxx`: duas seções com o mesmo `Rxx`
são lidas como duas seções, cada uma com o seu próprio espaço de `id`. Se ambas
produzirem o mesmo `<Rxx>/<id>`, a tupla devolvida **pode conter token global
repetido**. Recusar isso seria criar uma falha nova, fora de `C-A5-X1`. A
unicidade que **é** verificada é a de `C-A5-I4`: **`id` não repetido dentro da
mesma seção**. O módulo **não** importa e **não** chama `response_bijection`
para suprir essa não-garantia.

**`C-A5-I6` é norma externa vigente, não verificada aqui.** `C-A5-I6` proíbe
**reutilizar** um `id` dentro do mesmo `Rxx` **mesmo após a remoção** daquele
fragmento. A função **respeita** essa norma e **não a prova**: um único
*snapshot* não contém histórico. Ela **não** consulta `Git`, **não** cria
armazenamento, **não** guarda estado entre chamadas e **não** compara com
qualquer estado anterior. Ausência de erro aqui **não** é prova de ausência de
reutilização histórica.

Falha é **fail-closed** e imediata: a **primeira** violação em ordem física
encerra, e **nada é acumulado** (P5). A mensagem carrega **categoria e
localizador**, nunca o `id` recebido, o `Rxx` recebido, o texto do corpus, o
conteúdo comercial, o `repr`, o tipo concreto, um número de linha, um índice, um
tamanho ou uma cardinalidade. A entrada **não é alterada**.

**LER A REPRESENTAÇÃO MARCADA NÃO É MATERIALIZAR `C`.** Um retorno
bem-sucedido significa **somente** que o texto recebido está na representação
marcada de `C-A5`. Ele **não** prova que o texto seja o corpus oficial, que o
corpus esteja completo, que o corpus esteja aprovado, que as seções `Rxx` sejam
fisicamente únicas, nem que `C-A5-I6` tenha sido respeitada historicamente; e
**não** afirma coisa alguma sobre status, propagação de status, `PARCIAL`, texto
emitível, índice real, *bindings*, `ASSERTIVA`, equivalência `C-15`, bijeção
física, migração de autoridade de status ou `C-A1-ST6`–`C-A1-ST10`. O índice
continua inexistente, a autoridade de status continua em
`knowledge/respostas-aprovadas.md` (`C-11`) e **`C` continua ARBITRADA / NÃO
MATERIALIZADA**.
"""

from __future__ import annotations

__all__ = ["RepresentacaoMarcadaInvalida", "ler_unidades_marcadas"]


class RepresentacaoMarcadaInvalida(Exception):
    """O texto recebido não está na representação marcada de `C-A5`.

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **o
    que** está errado e o localizador diz **onde** estruturalmente — nunca o
    `id` recebido, o `Rxx` recebido, o conteúdo, o `repr`, o tipo concreto, um
    número de linha, um índice ou uma quantidade.

    Levantá-la significa que o texto **não** satisfaz a representação marcada.
    Não levantá-la significa apenas o oposto disso: **nada** é afirmado sobre a
    origem do texto, sobre o corpus real ou sobre a materialização de `C`.
    """


# Categorias tecnicas privadas e fechadas. Elas nomeiam o impedimento e **nao**
# sao identificadores normativos novos de `C`. As sete redacoes de `C-A5-X1`
# ficam cobertas por seis categorias estruturais: `marcador orfao` e `marcador
# sem bloco imediatamente seguinte` sao **mecanicamente indistinguiveis** nesta
# fronteira — um marcador valido nao seguido imediatamente de bloco e, ao mesmo
# tempo, orfao — e por isso compartilham `marcador_sem_bloco`. **Nao existem
# "sete categorias tecnicas C-A5".**
_TIPO_INVALIDO = "tipo_invalido"
_BLOCO_SEM_MARCADOR = "bloco_sem_marcador"
_MARCADOR_SEM_BLOCO = "marcador_sem_bloco"
_MARCADOR_FORA_DE_SECAO = "marcador_fora_de_secao"
_ID_FORA_DA_GRAMATICA = "id_fora_da_gramatica"
_ID_DUPLICADO = "id_duplicado"
_SECAO_SEM_UNIDADE = "secao_sem_unidade"

# Localizadores estruturais fechados. Eles nomeiam **a especie de construcao**
# onde o impedimento esta, jamais a sua posicao no documento.
_TEXTO = "texto"
_BLOCO = "bloco"
_MARCADOR = "marcador"
_SECAO = "secao"

# Envelope do marcador de `C-A5-I1`, em duas metades exatas.
_PREFIXO = "<!-- fragmento: "
_SUFIXO = " -->"

# Gramatica fechada do `id` de `C-A5-I3` e forma fechada do `Rxx`.
_INICIAL_DO_ID = "F"
_DIGITOS_ASCII = "0123456789"
_ZERO = "0"
_INICIAL_DO_RXX = "R"
_TAMANHO_DO_RXX = 3

# Separador normativo do token canonico (`C-A5-T2`).
_SEPARADOR = "/"

# Sintaxe fisica reconhecida por esta fronteira.
_CERQUILHA = "#"
_NIVEL_MAXIMO_ATX = 6
_NIVEL_DOCUMENTO = 1
_NIVEL_SECAO = 2
_ESPACO = " "
_CITACAO = ">"
_QUEBRA = "\n"
_RETORNO = "\r"


def ler_unidades_marcadas(texto: str) -> tuple[str, ...]:
    """Devolve os tokens `<Rxx>/<id>` da representação marcada de `texto`.

    A tupla vem na **ordem física do documento** e contém **exatamente um**
    token por par marcador/bloco válido — nenhum par é processado duas vezes.
    Um documento vazio, ou sem nenhuma seção `## Rxx`, devolve `tuple()`; isso
    **não** afirma que o corpus real esteja vazio, incompleto ou completo.

    `texto` precisa ser do tipo `str` **exatamente** — uma subclasse de `str` é
    recusada como `tipo_invalido`, **antes** de qualquer leitura. A razão é
    técnica: uma subclasse pode redefinir `__eq__`, `__hash__`, `startswith` ou
    `__getitem__` e, com isso, decidir por conta própria o que o documento diz.
    A entrada também **não** é convertida: não há `str(...)`, `repr` nem coerção
    de espécie alguma.

    A varredura é **determinística e em ordem de documento**. Antes dela, **1.**
    o tipo exato da entrada. Durante, **2.** a estrutura física, linha a linha.
    Dentro de um candidato a marcador a ordem é fixa: **1.** o envelope; **2.**
    a gramática do `id`; **3.** o escopo `Rxx`; **4.** a existência de bloco
    **imediatamente** seguinte; **5.** a duplicidade do `id` dentro da seção. Um
    bloco alcançado **dentro de uma seção `Rxx`** sem marcador válido
    imediatamente anterior é *fail-closed*, e o encerramento de uma seção `Rxx`
    sem nenhuma unidade válida também. Um bloco **fora** de qualquer `Rxx` está
    fora do domínio de `C-A5-U2` e é **ignorado inteiro**, sem token e sem erro
    — mas um **marcador válido fora de `Rxx` continua fail-closed**. A
    **primeira** violação encerra e **nada é acumulado**.

    Levanta `RepresentacaoMarcadaInvalida` cobrindo as **sete redações** de
    `C-A5-X1`: bloco destinado à emissão sem marcador válido
    (`bloco_sem_marcador`); marcador órfão e marcador sem bloco imediatamente
    seguinte — **mecanicamente o mesmo caso aqui** (`marcador_sem_bloco`);
    marcador fora de `Rxx` (`marcador_fora_de_secao`); `id` fora da gramática
    (`id_fora_da_gramatica`); `id` repetido no mesmo `Rxx` (`id_duplicado`); e
    `Rxx` sem unidade emitível (`secao_sem_unidade`). **Nenhum caso é resolvido
    por inferência** e **nenhuma oitava falha é criada**.

    **Não há garantia de unicidade global dos tokens**: a função não verifica a
    unicidade física das seções `## Rxx`, de modo que duas seções homônimas
    podem produzir o mesmo `<Rxx>/<id>` na tupla. **`C-A5-I6` é respeitada como
    norma externa e não é provada aqui**: não há histórico, `Git`, armazenamento
    nem estado entre chamadas.

    **LER A REPRESENTAÇÃO MARCADA NÃO É MATERIALIZAR `C`.** O sucesso afirma
    **apenas** a conformidade estrutural do texto dado — nada sobre a origem do
    texto, a completude ou a aprovação do corpus, status, `PARCIAL`, texto
    emitível, índice real, *bindings*, `ASSERTIVA`, equivalência `C-15`, bijeção
    física ou `C-A1-ST6`–`C-A1-ST10`.
    """
    if type(texto) is not str:
        raise _invalida(_TIPO_INVALIDO, _TEXTO)

    linhas = _linhas(texto)
    tokens: list[str] = []

    secao: str | None = None
    ids_da_secao: set[str] = set()
    unidades_da_secao = 0

    posicao = 0
    while posicao < len(linhas):
        linha = linhas[posicao]

        if linha.startswith(_CITACAO):
            if secao is None:
                # Fora de `## Rxx` o bloco esta fora do dominio de `C-A5-U2`:
                # ele nao e automaticamente unidade emitivel, nao produz token
                # e nao e interpretado. O bloco maximal e ignorado inteiro.
                fora_do_dominio = posicao
                while fora_do_dominio < len(linhas) and linhas[
                    fora_do_dominio
                ].startswith(_CITACAO):
                    fora_do_dominio += 1
                posicao = fora_do_dominio
                continue
            # Um par valido consome o seu bloco inteiro adiante; chegar aqui
            # significa que este bloco nao tem marcador valido imediatamente
            # antes dele.
            raise _invalida(_BLOCO_SEM_MARCADOR, _BLOCO)

        nivel = _nivel_do_cabecalho(linha)
        if nivel in (_NIVEL_DOCUMENTO, _NIVEL_SECAO):
            if secao is not None and unidades_da_secao == 0:
                raise _invalida(_SECAO_SEM_UNIDADE, _SECAO)
            secao = _rxx_do_cabecalho(linha) if nivel == _NIVEL_SECAO else None
            ids_da_secao = set()
            unidades_da_secao = 0
            posicao += 1
            continue
        if nivel:
            # Niveis 3 a 6 nao encerram a secao `##` corrente.
            posicao += 1
            continue

        identificador = _envelope(linha)
        if identificador is None:
            posicao += 1
            continue

        if not _id_conforme(identificador):
            raise _invalida(_ID_FORA_DA_GRAMATICA, _MARCADOR)
        if secao is None:
            raise _invalida(_MARCADOR_FORA_DE_SECAO, _MARCADOR)

        inicio_do_bloco = posicao + 1
        if inicio_do_bloco >= len(linhas):
            raise _invalida(_MARCADOR_SEM_BLOCO, _MARCADOR)
        if not linhas[inicio_do_bloco].startswith(_CITACAO):
            raise _invalida(_MARCADOR_SEM_BLOCO, _MARCADOR)

        if identificador in ids_da_secao:
            raise _invalida(_ID_DUPLICADO, _MARCADOR)

        ids_da_secao.add(identificador)
        unidades_da_secao += 1
        tokens.append(f"{secao}{_SEPARADOR}{identificador}")

        fim_do_bloco = inicio_do_bloco
        while fim_do_bloco < len(linhas) and linhas[fim_do_bloco].startswith(_CITACAO):
            fim_do_bloco += 1
        posicao = fim_do_bloco

    if secao is not None and unidades_da_secao == 0:
        raise _invalida(_SECAO_SEM_UNIDADE, _SECAO)

    return tuple(tokens)


def _linhas(texto: str) -> tuple[str, ...]:
    """Divide `texto` **somente** por `LF` e tira **no máximo um** `CR` final.

    `splitlines()` não é usado e *universal newline* não é aplicado: nenhum
    outro caractere é reconhecido como quebra, de modo que `U+2028`, `U+2029`,
    `U+0085`, `VT` e `FF` continuam sendo conteúdo da linha. Dois `CR` antes do
    `LF` deixam, portanto, um `CR` residual **dentro** da linha — o que torna a
    linha incapaz de ser marcador ou cabeçalho, deliberadamente.
    """
    return tuple(
        linha[:-1] if linha.endswith(_RETORNO) else linha
        for linha in texto.split(_QUEBRA)
    )


def _nivel_do_cabecalho(linha: str) -> int:
    """Nível ATX de `linha`, ou `0` quando ela não é cabeçalho aqui.

    Exige início na **coluna 0**, de um a seis `#` e, em seguida, **espaço ou
    fim de linha**. Cabeçalho indentado, `Setext` e sete ou mais `#` devolvem
    `0` — são conteúdo comum para esta fronteira.
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
    espaço ou fim de linha. Qualquer outra forma — inclusive espaçamento extra —
    deixa **zero `Rxx` em escopo**, o que é *fail-closed* para os marcadores que
    venham depois.
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


def _envelope(linha: str) -> str | None:
    """Conteúdo interno do envelope de `C-A5-I1`, ou `None` se não houver um.

    Devolver a `str` vazia significa candidato **com `id` vazio** — que existe e
    cai na gramática inválida. Devolver `None` significa que a linha **não é
    marcador**: ela é conteúdo comum, e não um marcador defeituoso.
    """
    if len(linha) < len(_PREFIXO) + len(_SUFIXO):
        return None
    if not linha.startswith(_PREFIXO):
        return None
    if not linha.endswith(_SUFIXO):
        return None
    return linha[len(_PREFIXO) : len(linha) - len(_SUFIXO)]


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


def _invalida(categoria: str, localizador: str) -> RepresentacaoMarcadaInvalida:
    return RepresentacaoMarcadaInvalida(f"{categoria}: {localizador}")

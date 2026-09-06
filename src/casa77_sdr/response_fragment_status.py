"""Leitura determinística do status declarado por fragmento sob `PARCIAL`.

Os blocos **"Mapeamento físico de status por fragmento sob `PARCIAL`"** e
**"Regime exclusivo de `status-fragmento` sob `PARCIAL`"** de `docs/07`
arbitraram a forma física da declaração e o seu regime:

```text
<!-- status-fragmento: <valor> -->
<!-- fragmento: <id> -->
> conteúdo
```

`PM1` fixa o **envelope exato** — prefixo `<!-- status-fragmento: `, valor,
sufixo ` -->`, **nada antes e nada depois**. `PM2` exige a declaração na **linha
imediatamente anterior** ao marcador `C-A5`, com **zero linha física** entre
ambos, e **nunca** entre marcador e bloco. `PM3` faz dela **adjacência
estrutural status → marcador**, jamais identidade: a identidade continua sendo
**exclusivamente** `<Rxx>/<id>` (`C-A5-T1`, `C-A5-T2`). `PM4` fecha o valor no
vocabulário canônico de `C-3`. `PM5` torna a declaração **obrigatória, exatamente
uma por fragmento emitível**, sob `PARCIAL`. E o **regime exclusivo** arbitrado
depois torna a declaração **proibida sob qualquer outro rótulo literal**. Este
módulo materializa **exatamente** isso.

**O texto chega pronto.** A função **não** abre arquivo, **não** conhece
caminho, **não** decide de onde o texto veio e **não** verifica que ele seja o
corpus oficial. A entrada é uma `str` já em memória. **A origem correta do texto
é pré-condição do chamador** e não é verificável nesta fronteira sem
transformá-la em carregador — que ela deliberadamente não é.

**`C12` é o portão, e `C8` é satisfeito transitivamente.** A **primeira**
operação funcional é `extrair_rotulos_de_cabecalho(texto)`. Aquela fronteira já
executa `ler_unidades_marcadas(texto)` como o seu próprio primeiro portão, de
modo que a ordem entre fronteiras é **`C8` → `C12` → `C14`** sem que este módulo
chame `C8` uma segunda vez — ele **não importa** `response_markdown_units`.
Tipo da entrada e estrutura de `C-A5` pertencem **inteiramente** a `C8`; a
gramática `G2` do cabeçalho pertence **inteiramente** a `C12`. As duas exceções
sobem **intactas** — sem `try`/`except`, sem *wrapper*, sem reclassificação, sem
enriquecimento e sem tocar em `__cause__` ou `__context__`. Como os dois portões
percorrem o documento **integralmente antes**, uma falha estrutural ou `G2`
**fisicamente posterior vence** uma violação `PM` anterior — decisão técnica de
composição, **não** norma nova.

**Caminhada física local, porque `C12` não expõe instância de seção.** `C12`
devolve `(Rxx, rotulo_literal)`, mas **não** expõe a fronteira física de cada
seção. Como seções `Rxx` **homônimas** são fisicamente possíveis aqui, é
**proibido** associar rótulo a marcador por `zip`, por posição entre saídas
independentes, por `dict`, por agrupamento por `Rxx`, por cardinalidade ou por
deduplicação. Por isso a caminhada local mantém o **contexto físico da seção
corrente** — `Rxx` **e** rótulo — enquanto percorre as linhas, e cada marcador é
julgado **dentro da sua própria seção física**.

**Invariante local × `C12`.** A caminhada local constrói a sua **própria**
sequência física de `(Rxx, rotulo_literal)` e a compara, **inteira**, com o
retorno guardado de `C12` **antes de qualquer retorno de sucesso**. Divergência
é **defeito interno**, não invalidez do documento, e produz
`RuntimeError("invariante_estrutural")`. Essa comparação **verifica consistência
entre duas caminhadas**: ela **não** atribui rótulo por posição, **não** usa
`zip`, **não** cria identidade de instância e **não** transforma posição em
identidade.

**Política de linha — a estrutural de `C8`/`C12`, repetida em `PM10`.** O texto é
dividido **exclusivamente** por `LF`; de cada segmento é removido **no máximo
um** `CR` terminal. `LF` e `CRLF` são estruturalmente equivalentes; um `CR`
residual permanece **conteúdo literal** — ele **não** é removido nem
normalizado, e o seu efeito sobre cabeçalho, declaração ou marcador é
determinado pelas **respectivas gramáticas**; `U+2028`, `U+2029`, `U+0085`,
`VT`, `FF` e `U+00A0` permanecem conteúdo. `splitlines()` **não** é usado,
*universal newline* **não** é aplicado e **nenhum** caractere é normalizado.

**Regime, e uma única regra de regime.** A declaração é aceita **se e somente
se** o rótulo literal da seção física corrente for **exatamente** `PARCIAL`. Os
três rótulos físicos de `C-A1-ST1`–`C-A1-ST3` **não** são carregados localmente
para decidir regime, e este módulo **não** importa `response_status` nem
`response_status_propagation`: a decisão é **uma comparação literal com
`PARCIAL`**, e todo o resto cai na proibição.

**Fail-closed, com cinco categorias fechadas.** `valor_invalido: declaracao`;
`declaracao_fora_de_secao: declaracao`; `declaracao_proibida: declaracao`;
`declaracao_orfa: declaracao`; `declaracao_ausente: marcador`. Dentro da `C14`,
quando uma linha satisfaz `PM1`, a ordem é **fixa**: **1.** valor (`PM4`);
**2.** existência de seção `Rxx`; **3.** regime; **4.** marcador imediatamente
seguinte. A **primeira** violação, em ordem física, encerra, e **nada é devolvido
parcialmente**. A mensagem carrega **categoria e localizador**, nunca o `Rxx`, o
`id`, o token, o valor recebido, o rótulo, o conteúdo, um número de linha, um
índice, uma cardinalidade, o `repr` ou o tipo concreto.

**Quase-declaração permanece conteúdo comum.** Uma linha que **não** satisfaça
exatamente o envelope de `PM1` — indentada, com *whitespace* divergente, com
conteúdo antes ou depois, com envelope incompleto, com tab ou com `CR` residual —
**não** é declaração defeituosa: é conteúdo. Sob rótulo não-`PARCIAL` isso **não
gera erro algum**; sob `PARCIAL`, se deixar um marcador sem a declaração
obrigatória, a falha é **do marcador** — `declaracao_ausente: marcador`.

**A ausência sob não-`PARCIAL` não é erro.** Fora do regime `PARCIAL` não há
declaração a exigir: o status daquela seção permanece **não resolvido**, o que é
o comportamento arbitrado, e **não** uma lacuna a fechar aqui.

**LER O STATUS DECLARADO NÃO É MATERIALIZAR `C`.** Um retorno bem-sucedido
significa **somente** que, no texto recebido, cada fragmento emitível sob uma
seção rotulada `PARCIAL` carrega exatamente uma declaração válida, e devolve o
par `(token, status)` de cada um. Ele **não** prova que o texto seja o corpus
oficial, que o corpus esteja completo ou aprovado, que as seções `Rxx` sejam
fisicamente únicas, nem afirma coisa alguma sobre propagação `SP1`–`SP7`,
resolução de `PARCIAL` no corpus, índice, bijeção física, *bindings*,
*placeholder*, `caminho_yaml`, `hora`, `C-7`, equivalência `C-15`, migração de
autoridade de status ou `C-A1-ST6`–`C-A1-ST10`. A autoridade de status continua
no Markdown aprovado (`C-11`) e **`C` continua ARBITRADA / NÃO MATERIALIZADA**.
"""

from __future__ import annotations

from casa77_sdr.response_header_labels import extrair_rotulos_de_cabecalho

__all__ = ["DeclaracaoDeStatusInvalida", "extrair_status_por_fragmento"]


class DeclaracaoDeStatusInvalida(Exception):
    """Uma declaração `status-fragmento` viola a fronteira `PM` desta leitura.

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **o
    que** está errado e o localizador diz **em que construção** — nunca o `Rxx`,
    o `id`, o token, o valor recebido, o rótulo, o conteúdo, um número de linha,
    um índice, uma quantidade, o `repr` ou o tipo concreto.

    Ela é **da fronteira `PM`**, nunca estrutural nem gramatical: a invalidez
    estrutural da representação marcada continua sendo
    `RepresentacaoMarcadaInvalida`, e a invalidez do cabeçalho continua sendo
    `CabecalhoRxxInvalido` — ambas levantadas **antes** desta fronteira
    percorrer coisa alguma.
    """


# Categorias tecnicas privadas e fechadas. Elas nomeiam o impedimento e **nao**
# sao identificadores normativos novos de `C`.
_VALOR_INVALIDO = "valor_invalido"
_DECLARACAO_FORA_DE_SECAO = "declaracao_fora_de_secao"
_DECLARACAO_PROIBIDA = "declaracao_proibida"
_DECLARACAO_ORFA = "declaracao_orfa"
_DECLARACAO_AUSENTE = "declaracao_ausente"

# Localizadores fechados. Eles nomeiam **a especie de construcao** onde o
# impedimento esta, jamais a sua posicao no documento.
_DECLARACAO = "declaracao"
_MARCADOR = "marcador"

# Defeito interno: divergencia entre a caminhada local e o retorno de `C12`.
# Nao e invalidez do documento, e por isso nao usa a excecao publica.
_INVARIANTE_ESTRUTURAL = "invariante_estrutural"

# Envelope de `PM1`, em duas metades exatas.
_PREFIXO_DECLARACAO = "<!-- status-fragmento: "
_SUFIXO_DECLARACAO = " -->"

# Envelope do marcador de `C-A5-I1`, em duas metades exatas.
_PREFIXO_MARCADOR = "<!-- fragmento: "
_SUFIXO_MARCADOR = " -->"

# Vocabulario fechado de `PM4`: os tres status canonicos de `C-3`. E uma
# `tuple`, e nao um mapa: a fronteira nao precisa de hash, nao traduz e nada
# aqui pode ser mutado em tempo de execucao. `PARCIAL` **nao** figura.
_VALORES_CANONICOS = ("APROVADO", "AGUARDA_APROVACAO", "BLOQUEADO")

# Unica regra de regime: so este rotulo literal admite declaracao.
_ROTULO_DO_REGIME = "PARCIAL"

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

# Nenhuma linha do documento ocupa esta posicao; ela marca "sem declaracao
# pendente" sem recorrer a um segundo sinalizador.
_NENHUMA_LINHA = -1


def extrair_status_por_fragmento(texto: str) -> tuple[tuple[str, str], ...]:
    """Devolve os pares `(token, status)` declarados sob seções `PARCIAL`.

    A tupla vem na **ordem física do documento** e contém **exatamente um** par
    por fragmento emitível que viva sob uma seção cujo rótulo literal seja
    **exatamente** `PARCIAL`. O token é `<Rxx>/<id>` (`C-A5-T1`, `C-A5-T2`) e o
    status é um dos três valores canônicos de `C-3` **declarados literalmente**.
    Um documento vazio, sem seção `Rxx`, ou sem nenhuma seção `PARCIAL`, devolve
    `tuple()`; isso **não** afirma que o corpus real esteja vazio, incompleto ou
    completo. Seções homônimas produzem **tokens repetidos**, preservados na
    ordem física — não há `dict`, `set`, `sorted`, deduplicação, agrupamento por
    `Rxx` nem unicidade global.

    A **primeira** operação é `extrair_rotulos_de_cabecalho(texto)`, que por sua
    vez executa `ler_unidades_marcadas(texto)` como o seu próprio primeiro
    portão: a ordem é **`C8` → `C12` → `C14`**, e `C8` **não** é chamado uma
    segunda vez aqui. `RepresentacaoMarcadaInvalida` e `CabecalhoRxxInvalido`
    propagam **intactas** — nada é capturado, relançado, reclassificado ou
    enriquecido. Como os dois portões percorrem o documento integralmente antes,
    uma falha estrutural ou `G2` **fisicamente posterior vence** uma violação
    `PM` anterior.

    Levanta `DeclaracaoDeStatusInvalida` com cinco categorias fechadas:
    `valor_invalido: declaracao` — o valor não é um dos três de `C-3`, o que
    inclui `PARCIAL`, variantes de caixa, valor vazio e espaçamento divergente;
    `declaracao_fora_de_secao: declaracao` — declaração exata fora de qualquer
    seção `Rxx`; `declaracao_proibida: declaracao` — declaração exata sob rótulo
    diferente de `PARCIAL`, o que inclui os rótulos físicos de
    `C-A1-ST1`–`C-A1-ST3` e qualquer outro rótulo `G2` válido;
    `declaracao_orfa: declaracao` — declaração exata sem marcador `C-A5` válido
    na linha **imediatamente** seguinte, o que cobre a linha em branco
    intercalada, o conteúdo intercalado, a declaração no fim do documento e duas
    declarações consecutivas, caso em que **a primeira** é a órfã;
    `declaracao_ausente: marcador` — sob `PARCIAL`, um marcador `C-A5` válido sem
    declaração válida imediatamente anterior. Quando uma linha satisfaz `PM1`, a
    ordem é **fixa**: **1.** valor; **2.** seção; **3.** regime; **4.** marcador
    seguinte — de modo que `valor_invalido` vence `declaracao_proibida` e
    `declaracao_fora_de_secao`, e o regime é julgado **antes** da relação
    física. A **primeira** violação, em ordem física, encerra e **nada é
    devolvido parcialmente**.

    Uma **quase-declaração** — que não satisfaça exatamente o envelope de `PM1` —
    **permanece conteúdo comum**: sob rótulo não-`PARCIAL` ela não gera erro
    algum, e sob `PARCIAL` a falha resultante é **do marcador**
    (`declaracao_ausente: marcador`), nunca dela. A **ausência** de declaração
    sob rótulo não-`PARCIAL` **não é erro**.

    Levanta `RuntimeError("invariante_estrutural")` — **defeito interno**, não
    invalidez do documento — se a sequência de `(Rxx, rotulo_literal)` construída
    pela caminhada local divergir, inteira, do retorno guardado de `C12`.

    **LER O STATUS DECLARADO NÃO É MATERIALIZAR `C`.** O sucesso afirma **apenas**
    o que foi declarado no texto dado — nada sobre a origem do texto, a
    completude ou a aprovação do corpus, a resolução de `PARCIAL` no corpus real,
    propagação `SP1`–`SP7`, índice, bijeção física, *bindings*, equivalência
    `C-15` ou `C-A1-ST6`–`C-A1-ST10`.
    """
    # **Portao integral e anterior.** `C12` roda o portao `C8` antes de aplicar
    # `G2`, de modo que estrutura e gramatica ja estao satisfeitas quando a
    # caminhada local comeca. O retorno e **guardado** — ao contrario do que
    # `C12` faz com `C8` — porque aqui existe invariante local a verificar.
    rotulos_de_c12 = extrair_rotulos_de_cabecalho(texto)

    linhas = _linhas(texto)
    cabecalhos: list[tuple[str, str | None]] = []
    pares: list[tuple[str, str]] = []

    secao: str | None = None
    rotulo: str | None = None
    valor_pendente = ""
    linha_coberta = _NENHUMA_LINHA

    for posicao in range(len(linhas)):
        linha = linhas[posicao]

        nivel = _nivel_do_cabecalho(linha)
        if nivel == _NIVEL_DOCUMENTO or nivel == _NIVEL_SECAO:
            secao = _rxx_do_cabecalho(linha) if nivel == _NIVEL_SECAO else None
            rotulo = _rotulo_de_g2(linha) if secao is not None else None
            if secao is not None:
                cabecalhos.append((secao, rotulo))
            continue
        if nivel:
            # Niveis 3 a 6 nao encerram a secao `##` corrente.
            continue

        valor = _valor_declarado(linha)
        if valor is not None:
            _exigir_declaracao_valida(valor, secao, rotulo)
            seguinte = posicao + 1
            if seguinte >= len(linhas):
                raise _invalida(_DECLARACAO_ORFA, _DECLARACAO)
            if _identificador_marcado(linhas[seguinte]) is None:
                raise _invalida(_DECLARACAO_ORFA, _DECLARACAO)
            valor_pendente = valor
            linha_coberta = seguinte
            continue

        identificador = _identificador_marcado(linha)
        if identificador is None:
            continue
        if secao is None or rotulo != _ROTULO_DO_REGIME:
            continue
        if linha_coberta != posicao:
            raise _invalida(_DECLARACAO_AUSENTE, _MARCADOR)
        pares.append(
            (f"{secao}{_SEPARADOR_DE_TOKEN}{identificador}", valor_pendente)
        )

    # **Invariante local x `C12`, antes de qualquer sucesso.** As duas
    # caminhadas independentes precisam ter visto os mesmos cabecalhos, na mesma
    # ordem fisica, com os mesmos rotulos. Nada aqui pareia por posicao: as
    # sequencias sao comparadas **inteiras**.
    if tuple(cabecalhos) != rotulos_de_c12:
        raise RuntimeError(_INVARIANTE_ESTRUTURAL)

    return tuple(pares)


def _exigir_declaracao_valida(
    valor: str, secao: str | None, rotulo: str | None
) -> None:
    """Aplica, em ordem fixa, valor, existência de seção e regime.

    A ordem é normativa desta fronteira: `valor_invalido` vence
    `declaracao_fora_de_secao` e `declaracao_proibida`, e o **regime** é julgado
    **antes** da relação física com o marcador.
    """
    if valor not in _VALORES_CANONICOS:
        raise _invalida(_VALOR_INVALIDO, _DECLARACAO)
    if secao is None:
        raise _invalida(_DECLARACAO_FORA_DE_SECAO, _DECLARACAO)
    if rotulo != _ROTULO_DO_REGIME:
        raise _invalida(_DECLARACAO_PROIBIDA, _DECLARACAO)


def _linhas(texto: str) -> tuple[str, ...]:
    """Divide `texto` **somente** por `LF` e tira **no máximo um** `CR` final.

    Mesma política estrutural de `C8`/`C12`, repetida por `PM10`: `splitlines()`
    não é usado e *universal newline* não é aplicado, de modo que `U+2028`,
    `U+2029`, `U+0085`, `VT` e `FF` continuam conteúdo da linha, e um segundo
    `CR` antes do `LF` permanece como `CR` residual dentro dela.
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
    rotulo = resto[ocorrencias[1] + len(_SEPARADOR_G2) :]
    if not titulo or not rotulo:
        return None
    return rotulo


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


def _valor_declarado(linha: str) -> str | None:
    """Valor interno do envelope de `PM1`, ou `None` se a linha não for uma.

    Devolver a `str` vazia significa declaração **com valor vazio** — que existe
    e cai em `valor_invalido`. Devolver `None` significa que a linha **não é
    declaração**: ela é conteúdo comum, e não uma declaração defeituosa. A
    guarda de comprimento impede que prefixo e sufixo se sobreponham, de modo
    que `<!-- status-fragmento: -->` **não** é declaração de valor vazio.
    """
    if len(linha) < len(_PREFIXO_DECLARACAO) + len(_SUFIXO_DECLARACAO):
        return None
    if not linha.startswith(_PREFIXO_DECLARACAO):
        return None
    if not linha.endswith(_SUFIXO_DECLARACAO):
        return None
    return linha[len(_PREFIXO_DECLARACAO) : len(linha) - len(_SUFIXO_DECLARACAO)]


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


def _invalida(categoria: str, localizador: str) -> DeclaracaoDeStatusInvalida:
    return DeclaracaoDeStatusInvalida(f"{categoria}: {localizador}")

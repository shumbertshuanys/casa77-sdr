"""Derivação determinística do domínio canônico de tokens do lado do índice.

`C-A5-T1` fixa a identidade canônica do fragmento emitível como `<Rxx>/<id>`,
com `/` por separador normativo (`C-A5-T2`); `C-A5-T3` garante a decomposição
unívoca porque **`Rxx` tem forma fechada** (C-2b) e **o `id` tem forma fechada**
(`C-A5-I3`), e nenhum dos dois admite `/`; `C-A5-T4` estabelece que essa
identidade **será o token dos dois domínios físicos** de `C-A1-B3` / `C-A1-B4`;
e `C-A5-T5` determina que o token é **derivado, nunca armazenado** — o futuro
índice mantém **o `Rxx`** e **`fragmentos[].id`** separadamente, sem campo novo.
Este módulo produz **um** desses domínios: o do **lado do índice**.

**A estrutura chega pronta.** A função recebe uma estrutura Python **já em
memória** — a mesma espécie de entrada de `validar_indice`. Ela **não** abre
arquivo, **não** conhece caminho, **não** lê YAML, **não** cria o índice e
**não** verifica que a estrutura recebida seja o índice real. **A origem
correta da estrutura é pré-condição do chamador.**

**Só identidade, nunca conteúdo.** A saída carrega **exclusivamente** tokens
`<Rxx>/<id>`, compostos em tempo de execução. Nada é gravado na estrutura
recebida, nada é persistido e nenhum campo novo é criado — a estrutura **não é
alterada**.

**Ordem.** A tupla preserva a ordem das listas `respostas` e `fragmentos`
recebidas. Isso é **decisão técnica determinística de saída**, para que a
fronteira seja reprodutível; **não** é significado normativo novo de
identidade, e a identidade continua **declarada, nunca derivada de posição**
(`C-A5-I5`, `C-A5-M6`).

**Esta função NÃO substitui `validar_indice`.** Ela **não** valida o contrato
inteiro de `C-2`: **não** julga `status`, `bindings`, `itera_sobre`,
*placeholder*, `caminho_yaml`, `formato`, `predicado`, mecanismo, origem, fato
runtime, nem chaves desconhecidas fora da projeção que precisa ler. Ela lê
**apenas a projeção mínima** necessária para compor tokens com segurança:
a raiz, `respostas`, o `id` de cada resposta e o `id` de cada fragmento.
`src/casa77_sdr/response_index.py` continua sendo a fronteira que valida a
**forma** do índice, e **não é alterado, importado nem chamado** aqui. As duas
fronteiras são **independentes e complementares**: aquela confere a estrutura;
esta compõe a identidade canônica.

**Política de tipo — decisão técnica local.** Para **contêineres**, a semântica
é compatível com `response_index.py`: `dict` e subclasses, `list` e subclasses
são aceitos; **nenhuma regra de tipo exato é criada para contêiner**. Para os
**componentes da identidade** — o `Rxx` da resposta e o `id` do fragmento — a
exigência é `str` **exata**, e **subclasse de `str` é recusada**. A razão é
técnica: uma subclasse pode redefinir `__eq__`, `__hash__` ou `__str__` e, com
isso, decidir por conta própria quando dois identificadores são o mesmo, ou o
que a composição `<Rxx>/<id>` produz — a semântica de identidade deixaria de
ser decidida aqui. **Essa recusa é defesa local desta fronteira**: ela **não**
altera `C-2`, **não** altera `C-A5`, **não** altera `validar_indice` e **não**
torna retroativamente inválido nada que `response_index.py` aceite.

**`C-A5-I3` aplicada ao `id` do índice.** O `fragmentos[].id` precisa obedecer
à gramática fechada de `C-A5-I3` — **`F`** seguido de inteiro decimal **ASCII**
maior que zero e **sem zero à esquerda** —, porque é **esse** `id` que compõe a
identidade canônica de `C-A5-T1` cuja decomposição unívoca `C-A5-T3` garante
justamente pela forma fechada do componente. Isso **não cria regra nova**: é a
aplicação da gramática já arbitrada ao componente já designado. `response_index`
exige apenas `str` não vazia para esse campo, e **continua correto no seu
próprio escopo** — a forma fechada é requisito **da composição do token**, não
uma correção da validação estrutural.

**Unicidade.** O `Rxx` é único **globalmente** (C-2a); o `id` de fragmento é
único **somente dentro do respectivo `Rxx`** (`C-A5-I4`, C-2h), de modo que
`F1` repetido entre `Rxx` distintos é **válido**. Uma resposta precisa ter **ao
menos um** fragmento (C-2c).

Falha é **fail-closed** e imediata: a **primeira** violação encerra, e **nada é
acumulado** (P5). A mensagem carrega **categoria e localizador estrutural**,
nunca o `Rxx` recebido, o `id` recebido, o valor, o conteúdo, o `repr`, o tipo
concreto, uma posição, um tamanho ou uma cardinalidade. As categorias são
**privadas, fechadas e mínimas**, e **não** são identificadores normativos
novos de `C`.

**DERIVAR O DOMÍNIO NÃO É MATERIALIZAR `C`.** Um retorno bem-sucedido significa
**somente** que foi possível derivar um domínio canônico de identidades a partir
da projeção lida. Ele **não** prova que o índice real exista — ele **continua
INEXISTENTE** —, que a estrutura recebida seja o índice oficial, que ela seja
integralmente válida (isso é de `validar_indice`), que `C-A1-ST6` esteja
satisfeita, que a bijeção física tenha sido executada, que `C-A1-ST7` esteja
satisfeita, nem que a autoridade de status tenha migrado
(`C-A1-ST6`–`C-A1-ST10` continuam **NÃO satisfeitas**). Esta fronteira produz
**apenas o produtor de um domínio**: ela **não** cria a relação de
correspondência, **não** chama `validar_bijecao` e **não** executa a bijeção.
`C` continua **ARBITRADA / NÃO MATERIALIZADA**.
"""

from __future__ import annotations

__all__ = ["ProjecaoDeIdentidadeInvalida", "derivar_tokens_do_indice"]


class ProjecaoDeIdentidadeInvalida(Exception):
    """A projeção lida não permite derivar o domínio canônico de identidades.

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **o
    que** impede a derivação e o localizador diz **onde** estruturalmente —
    nunca o `Rxx` recebido, o `id` recebido, o valor, o conteúdo, o `repr`, o
    tipo concreto, uma posição ou uma quantidade.

    Levantá-la significa que **a identidade não pôde ser composta com
    segurança**. Não levantá-la significa apenas o oposto disso: **nada** é
    afirmado sobre a validade integral do índice, sobre a existência do índice
    real ou sobre a bijeção.
    """


# Categorias tecnicas privadas, fechadas e minimas. Elas nomeiam o impedimento
# e **nao** sao identificadores normativos novos de `C`. O vocabulario e um
# subconjunto deliberado do ja usado por `response_index.py`, para nao
# introduzir taxonomia paralela.
_TIPO_INVALIDO = "tipo_invalido"
_CAMPO_AUSENTE = "campo_ausente"
_VALOR_INVALIDO = "valor_invalido"
_DUPLICIDADE = "duplicidade"

# Localizadores estruturais fechados. Eles nomeiam **a especie de construcao**
# onde o impedimento esta, jamais a sua posicao na lista.
_INDICE = "indice"
_RESPOSTAS = "respostas"
_RESPOSTA = "respostas.item"
_RESPOSTA_ID = "respostas.item.id"
_FRAGMENTOS = "respostas.item.fragmentos"
_FRAGMENTO = "respostas.item.fragmentos.item"
_FRAGMENTO_ID = "respostas.item.fragmentos.item.id"

# Campos da projecao minima. Nenhum outro campo e lido.
_CAMPO_RESPOSTAS = "respostas"
_CAMPO_ID = "id"
_CAMPO_FRAGMENTOS = "fragmentos"

# Separador normativo do token canonico (`C-A5-T2`).
_SEPARADOR = "/"

# Formas fechadas dos dois componentes.
_INICIAL_DO_RXX = "R"
_TAMANHO_DO_RXX = 3
_INICIAL_DO_ID = "F"
_DIGITOS_ASCII = "0123456789"
_ZERO = "0"


def derivar_tokens_do_indice(indice: object) -> tuple[str, ...]:
    """Devolve os tokens `<Rxx>/<id>` derivados da projeção de `indice`.

    A tupla vem na **ordem das listas recebidas** — `respostas` e, dentro de
    cada uma, `fragmentos` — e contém **exatamente um** token por fragmento.
    `{"respostas": []}` devolve `tuple()`; isso **não** afirma que o índice real
    esteja vazio, incompleto ou completo — ele **continua INEXISTENTE**.

    A **projeção mínima** lida, e nada além dela, é: a raiz é mapeamento; existe
    `respostas`; `respostas` é lista; cada resposta é mapeamento; existe `id`;
    o `Rxx` é `str` **exata** e satisfaz a forma fechada de **C-2b** — `R`
    seguido de **exatamente dois dígitos ASCII** —; o `Rxx` é único
    **globalmente** (**C-2a**); existe `fragmentos`; `fragmentos` é lista e
    **não é vazia** (**C-2c**); cada fragmento é mapeamento; existe `id`; o
    `id` é `str` **exata** e satisfaz a gramática fechada de **`C-A5-I3`** —
    `F` seguido de inteiro decimal ASCII maior que zero e sem zero à esquerda;
    e o `id` é único **dentro do respectivo `Rxx`** (**`C-A5-I4`**, **C-2h**),
    de modo que `F1` repetido entre `Rxx` distintos é **válido**.

    **Nada mais é julgado.** `status`, `bindings`, `itera_sobre`, *placeholder*,
    `caminho_yaml`, `formato`, `predicado`, mecanismo, origem, fato runtime e
    chaves desconhecidas **não** são verificados aqui: isso é de
    `validar_indice`, que esta função **não substitui, não importa e não
    chama**. Uma estrutura com `status` inválido ou `bindings` malformados pode,
    portanto, produzir tokens normalmente — e isso **não** afirma que ela seja
    um índice válido.

    A ordem de validação é **fixa** e a varredura é em ordem de documento:
    raiz, `respostas`, e então, por resposta, `id` antes de `fragmentos`, e,
    por fragmento, tipo antes de gramática antes de duplicidade. A **primeira**
    violação levanta `ProjecaoDeIdentidadeInvalida` e **nada é acumulado**.

    **Tipos.** Contêineres aceitam subclasses — `dict` e `list` por
    `isinstance`, como em `response_index.py`. Os **componentes da identidade**
    exigem `str` **exata**: subclasse de `str` é recusada como `tipo_invalido`,
    porque poderia redefinir `__eq__`, `__hash__` ou `__str__` e decidir sozinha
    a identidade ou a composição. Essa recusa é **local desta fronteira** e
    **não** altera `C-2`, `C-A5` ou `validar_indice`.

    A estrutura recebida **não é alterada**: nada é gravado nela, nenhum token é
    armazenado e nenhum campo novo é criado (**`C-A5-T5`**).

    **DERIVAR O DOMÍNIO NÃO É MATERIALIZAR `C`.** O sucesso afirma **apenas**
    que um domínio canônico de identidades pôde ser derivado da projeção lida —
    nada sobre a existência ou a validade integral do índice real, sobre
    `C-A1-ST6`, sobre a execução da bijeção física, sobre `C-A1-ST7` ou sobre a
    migração da autoridade de status.
    """
    if not isinstance(indice, dict):
        raise _invalida(_TIPO_INVALIDO, _INDICE)
    if _CAMPO_RESPOSTAS not in indice:
        raise _invalida(_CAMPO_AUSENTE, _RESPOSTAS)

    respostas = indice[_CAMPO_RESPOSTAS]
    if not isinstance(respostas, list):
        raise _invalida(_TIPO_INVALIDO, _RESPOSTAS)

    tokens: list[str] = []
    rxx_vistos: set[str] = set()

    for resposta in respostas:
        if not isinstance(resposta, dict):
            raise _invalida(_TIPO_INVALIDO, _RESPOSTA)
        if _CAMPO_ID not in resposta:
            raise _invalida(_CAMPO_AUSENTE, _RESPOSTA_ID)

        rxx = resposta[_CAMPO_ID]
        if type(rxx) is not str:
            raise _invalida(_TIPO_INVALIDO, _RESPOSTA_ID)
        if not _e_rxx(rxx):
            raise _invalida(_VALOR_INVALIDO, _RESPOSTA_ID)
        if rxx in rxx_vistos:
            raise _invalida(_DUPLICIDADE, _RESPOSTA_ID)
        rxx_vistos.add(rxx)

        if _CAMPO_FRAGMENTOS not in resposta:
            raise _invalida(_CAMPO_AUSENTE, _FRAGMENTOS)
        fragmentos = resposta[_CAMPO_FRAGMENTOS]
        if not isinstance(fragmentos, list):
            raise _invalida(_TIPO_INVALIDO, _FRAGMENTOS)
        # C-2c: um `Rxx` tem um ou mais fragmentos.
        if not fragmentos:
            raise _invalida(_VALOR_INVALIDO, _FRAGMENTOS)

        ids_da_resposta: set[str] = set()
        for fragmento in fragmentos:
            if not isinstance(fragmento, dict):
                raise _invalida(_TIPO_INVALIDO, _FRAGMENTO)
            if _CAMPO_ID not in fragmento:
                raise _invalida(_CAMPO_AUSENTE, _FRAGMENTO_ID)

            identificador = fragmento[_CAMPO_ID]
            if type(identificador) is not str:
                raise _invalida(_TIPO_INVALIDO, _FRAGMENTO_ID)
            if not _e_id_de_fragmento(identificador):
                raise _invalida(_VALOR_INVALIDO, _FRAGMENTO_ID)
            # `C-A5-I4` / C-2h: a unicidade do `id` e local ao `Rxx`.
            if identificador in ids_da_resposta:
                raise _invalida(_DUPLICIDADE, _FRAGMENTO_ID)
            ids_da_resposta.add(identificador)

            tokens.append(f"{rxx}{_SEPARADOR}{identificador}")

    return tuple(tokens)


def _e_rxx(identificador: str) -> bool:
    """Diz se `identificador` obedece à forma fechada `Rxx` de **C-2b**.

    `R` seguido de **exatamente dois dígitos ASCII**, sem impor faixa numérica.
    Dígito decimal de outro sistema de escrita **não** é dígito aqui — a forma
    precisa ser fechada para que `C-A5-T3` garanta a decomposição unívoca.
    """
    if len(identificador) != _TAMANHO_DO_RXX:
        return False
    if identificador[0] != _INICIAL_DO_RXX:
        return False
    for caractere in identificador[1:]:
        if caractere not in _DIGITOS_ASCII:
            return False
    return True


def _e_id_de_fragmento(identificador: str) -> bool:
    """Diz se `identificador` obedece à gramática fechada de **`C-A5-I3`**.

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


def _invalida(categoria: str, localizador: str) -> ProjecaoDeIdentidadeInvalida:
    return ProjecaoDeIdentidadeInvalida(f"{categoria}: {localizador}")

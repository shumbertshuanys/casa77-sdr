"""Aplicabilidade determinística de pacote — qual faixa comporta o evento.

Esta fronteira responde **uma** pergunta, e só ela: **qual das duas faixas de
pacote é aplicável ao que se sabe do evento neste ciclo?** Ela é **pura**,
**determinística** e **estrutural**.

**Duas autoridades distintas, nunca confundidas.** `capacidade` define o
**limite de capacidade sentada**, a **capacidade máxima** e, por consequência,
**quando o formato passa a ser determinante**. `precos.pacotes[*].limite_convidados`
define **qual pacote comporta a quantidade**. A obrigatoriedade do formato
**nunca** é deduzida dos pacotes, e o alcance de um pacote **nunca** é deduzido
da capacidade: cada fato vem da sua própria autoridade, e o alinhamento entre as
duas é **conferido**, não presumido.

**Ordem fixa da decisão**, e é dela que vem o determinismo:

1. convidados **ausentes** ou com confiança **diferente de `ALTA`** →
   `INDETERMINADO`;
2. convidados **acima da capacidade máxima** → `NENHUM_APLICAVEL`;
3. convidados **até a capacidade sentada** → `FAIXA_INFERIOR`;
4. **acima da capacidade sentada e até a máxima**, com formato **ausente** ou de
   confiança **diferente de `ALTA`** → `INDETERMINADO`;
5. a **mesma faixa**, com formato **confiável** → `FAIXA_SUPERIOR`.

**`SENTADO` na faixa superior continua `FAIXA_SUPERIOR`.** A pergunta aqui é
**qual pacote comporta a quantidade**, não se o formato pedido é comercialmente
recomendável: a **ressalva** pertence à **qualificação** e ao **handoff**, e
**não** a esta fronteira.

***Fail-closed* da base.** Antes de qualquer decisão, a forma é conferida
**mecanicamente**: `capacidade.convidados_sentados` e `capacidade.formato_coquetel`
inteiros exatos e ordenados; `precos.pacotes` com **exatamente dois** pacotes,
cada um com `codigo` textual não vazio e `limite_convidados` **inteiro exato**,
**nunca `bool`**; limites **distintos**; o **menor** coincidindo com a fronteira
inferior vigente da capacidade e o **maior** com a capacidade máxima vigente. Se
as **duas faixas** não puderem ser estabelecidas **inequivocamente**, a fronteira
**fecha** com exceção própria: **nenhum terceiro pacote é inventado** e **nada é
generalizado silenciosamente**.

**Pureza.** Zero I/O, *filesystem*, rede, LLM, relógio, ambiente, *logging*,
*cache* e mutação de entrada. **`knowledge/**` não é aberto**: a base chega
**já carregada** pelo chamador.

**Escopo.** Ela **não conhece `Rxx`**, **não conhece `AssuntoComercial`**, **não
escolhe *witness***, **não decide cobertura**, **não emite texto** e **não
produz condição de ciclo**. O consumo do seu veredito — o *gate* **D8-G** —
pertence a **S2-D8**.

**Zero valor comercial no código.** Nenhum preço, capacidade ou limite vigente
aparece aqui como literal: tudo é lido da base recebida, por caminho estrutural.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from casa77_sdr.identity import Confianca
from casa77_sdr.interpretation import DadosExtraidos

__all__ = [
    "AplicabilidadeNaoAvaliavel",
    "AplicabilidadePacote",
    "decidir_aplicabilidade_de_pacote",
]


class AplicabilidadePacote(StrEnum):
    """Vocabulário **fechado** do veredito — **quatro** valores, e só eles.

    `FAIXA_INFERIOR` — a quantidade cabe no pacote de **menor** limite.

    `FAIXA_SUPERIOR` — a quantidade **excede** o menor limite, **cabe** no maior
    e o **formato é confiável**.

    `INDETERMINADO` — falta o que decide: a quantidade, a confiança dela, ou o
    formato na faixa em que ele é determinante. **Não é negativa**, e **não é
    ausência de pacote**: é **ainda não se sabe**.

    `NENHUM_APLICAVEL` — a quantidade **excede a capacidade máxima**, e **nenhum**
    pacote a comporta.
    """

    FAIXA_INFERIOR = "FAIXA_INFERIOR"
    FAIXA_SUPERIOR = "FAIXA_SUPERIOR"
    INDETERMINADO = "INDETERMINADO"
    NENHUM_APLICAVEL = "NENHUM_APLICAVEL"


class AplicabilidadeNaoAvaliavel(Exception):
    """A entrada ou a base **não permitem sequer decidir** a faixa.

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **o
    que** está errado e o localizador diz **em que caminho estrutural** — nunca
    o valor recebido, o limite, a capacidade, o `repr` ou o tipo concreto.

    Ela é **falha técnica**, não veredito comercial: `INDETERMINADO` **não** é o
    seu substituto, e **nenhum resultado parcial** é devolvido.
    """


# Categorias fechadas. Nenhuma delas descreve valor.
_TIPO_INVALIDO = "tipo_invalido"
_CAMPO_AUSENTE = "campo_ausente"
_VALOR_INVALIDO = "valor_invalido"
_COMBINACAO_INVALIDA = "combinacao_invalida"

# Caminhos estruturais da base. Eles nomeiam **onde**, jamais **quanto**.
_DADOS = "dados"
_DADOS_CONVIDADOS = "dados.convidados"
_BASE = "base"
_CAPACIDADE = "capacidade"
_SENTADOS = "capacidade.convidados_sentados"
_COQUETEL = "capacidade.formato_coquetel"
_PRECOS = "precos"
_PACOTES = "precos.pacotes"
_PACOTE_CODIGO = "precos.pacotes.item.codigo"
_PACOTE_LIMITE = "precos.pacotes.item.limite_convidados"

# Chaves ja vigentes na base comercial. Nenhum valor e declarado aqui.
_CHAVE_CAPACIDADE = "capacidade"
_CHAVE_SENTADOS = "convidados_sentados"
_CHAVE_COQUETEL = "formato_coquetel"
_CHAVE_PRECOS = "precos"
_CHAVE_PACOTES = "pacotes"
_CHAVE_CODIGO = "codigo"
_CHAVE_LIMITE = "limite_convidados"

# O MVP tem **duas** faixas. Um terceiro pacote exige nova arbitragem.
_PACOTES_ESPERADOS = 2


def decidir_aplicabilidade_de_pacote(
    dados: object,
    base: object,
) -> AplicabilidadePacote:
    """Decide a faixa aplicável a partir do que se sabe do evento.

    `dados` é o `DadosExtraidos` da interpretação; `base` é a base comercial
    **já carregada** pelo chamador. Esta fronteira **não abre arquivo algum**,
    **não chama LLM** e **não muta** nenhuma das duas entradas.

    Devolve um dos **quatro** valores de `AplicabilidadePacote`, pela ordem fixa
    documentada no módulo. Levanta `AplicabilidadeNaoAvaliavel` quando a entrada
    ou a base são estruturalmente inviáveis — **sem resultado parcial**, e
    **nunca** devolvendo `INDETERMINADO` no lugar de uma falha técnica.

    **DECIDIR A FAIXA NÃO É DECIDIR COBERTURA.** Qual fragmento responde à
    consulta pertence a **S2-D8**; a ressalva comercial sobre formato pertence à
    qualificação e ao handoff.
    """
    if type(dados) is not DadosExtraidos:
        raise _nao_avaliavel(_TIPO_INVALIDO, _DADOS)

    sentados, maximo = _faixas_da_base(base)

    convidados = dados.convidados
    if convidados is None or dados.confianca_convidados is not Confianca.ALTA:
        # 1. Sem quantidade confiavel nao ha faixa: nem inferior, nem superior.
        return AplicabilidadePacote.INDETERMINADO
    if type(convidados) is not int or type(convidados) is bool:
        raise _nao_avaliavel(_TIPO_INVALIDO, _DADOS_CONVIDADOS)

    if convidados > maximo:
        # 2. Acima da capacidade maxima nenhum pacote comporta a quantidade.
        return AplicabilidadePacote.NENHUM_APLICAVEL
    if convidados <= sentados:
        # 3. Ate a capacidade sentada, a faixa inferior comporta.
        return AplicabilidadePacote.FAIXA_INFERIOR

    # 4./5. Entre as duas fronteiras, o **formato** e que decide — e por isso
    # ele precisa ser confiavel. `SENTADO` aqui continua FAIXA_SUPERIOR: a
    # ressalva comercial pertence a qualificacao, nao a esta fronteira.
    if dados.formato is None or dados.confianca_formato is not Confianca.ALTA:
        return AplicabilidadePacote.INDETERMINADO
    return AplicabilidadePacote.FAIXA_SUPERIOR


def _faixas_da_base(base: object) -> tuple[int, int]:
    """Estabelece as **duas** fronteiras, conferindo as duas autoridades.

    Devolve `(capacidade_sentada, capacidade_maxima)`. A conferência é
    **estrutural**: nenhum valor é copiado para o código, e o alinhamento entre
    `capacidade` e `precos.pacotes` é **provado**, não presumido.
    """
    if not isinstance(base, dict):
        raise _nao_avaliavel(_TIPO_INVALIDO, _BASE)

    capacidade = _exigir_mapeamento(base, _CHAVE_CAPACIDADE, _CAPACIDADE)
    sentados = _exigir_inteiro(capacidade, _CHAVE_SENTADOS, _SENTADOS)
    maximo = _exigir_inteiro(capacidade, _CHAVE_COQUETEL, _COQUETEL)
    if sentados >= maximo:
        # Sem duas fronteiras ordenadas nao existem duas faixas.
        raise _nao_avaliavel(_COMBINACAO_INVALIDA, _CAPACIDADE)

    precos = _exigir_mapeamento(base, _CHAVE_PRECOS, _PRECOS)
    pacotes = precos.get(_CHAVE_PACOTES)
    if pacotes is None:
        raise _nao_avaliavel(_CAMPO_AUSENTE, _PACOTES)
    if not isinstance(pacotes, list):
        raise _nao_avaliavel(_TIPO_INVALIDO, _PACOTES)
    if len(pacotes) != _PACOTES_ESPERADOS:
        # Nem terceiro pacote, nem pacote unico: o MVP tem **duas** faixas, e
        # generalizar aqui seria arbitrar sem mandato.
        raise _nao_avaliavel(_VALOR_INVALIDO, _PACOTES)

    limites: list[int] = []
    for pacote in pacotes:
        if not isinstance(pacote, dict):
            raise _nao_avaliavel(_TIPO_INVALIDO, _PACOTES)
        codigo = pacote.get(_CHAVE_CODIGO)
        if codigo is None:
            raise _nao_avaliavel(_CAMPO_AUSENTE, _PACOTE_CODIGO)
        if not isinstance(codigo, str):
            raise _nao_avaliavel(_TIPO_INVALIDO, _PACOTE_CODIGO)
        if not codigo:
            raise _nao_avaliavel(_VALOR_INVALIDO, _PACOTE_CODIGO)
        limites.append(_exigir_inteiro(pacote, _CHAVE_LIMITE, _PACOTE_LIMITE))

    if limites[0] == limites[1]:
        # Limites iguais nao separam faixa alguma.
        raise _nao_avaliavel(_VALOR_INVALIDO, _PACOTE_LIMITE)
    if min(limites) != sentados or max(limites) != maximo:
        # As duas autoridades precisam concordar sobre onde ficam as fronteiras.
        raise _nao_avaliavel(_COMBINACAO_INVALIDA, _PACOTES)

    return sentados, maximo


def _exigir_mapeamento(onde: dict[str, Any], chave: str, caminho: str) -> dict[str, Any]:
    valor = onde.get(chave)
    if valor is None:
        raise _nao_avaliavel(_CAMPO_AUSENTE, caminho)
    if not isinstance(valor, dict):
        raise _nao_avaliavel(_TIPO_INVALIDO, caminho)
    return valor


def _exigir_inteiro(onde: dict[str, Any], chave: str, caminho: str) -> int:
    """Inteiro **exato** e positivo. `bool` é `int` em Python, e aqui não passa."""
    valor = onde.get(chave)
    if valor is None:
        raise _nao_avaliavel(_CAMPO_AUSENTE, caminho)
    if type(valor) is not int or type(valor) is bool:
        raise _nao_avaliavel(_TIPO_INVALIDO, caminho)
    if valor <= 0:
        raise _nao_avaliavel(_VALOR_INVALIDO, caminho)
    return valor


def _nao_avaliavel(categoria: str, localizador: str) -> AplicabilidadeNaoAvaliavel:
    return AplicabilidadeNaoAvaliavel(f"{categoria}: {localizador}")

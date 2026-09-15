"""`ValidadorResposta` — o *gate* final de integridade textual da emissão.

Esta fronteira recebe o **texto candidato** e a **`RespostaMontada`** já
produzida por `montar_resposta_final` (§4.1.6) e responde **uma única
pergunta**: o texto candidato é **literalmente** o texto daquela montagem?

    aprovado  ⟺  texto_candidato == montada.texto

**`P4`, materializado.** Nesta arquitetura, a **forma canônica autorizada** é
`RespostaMontada.texto` — derivada exclusivamente dos fragmentos autorizados a
montante, dos fatos materializados desses fragmentos e da montagem
determinística. Logo a prova final é a **igualdade literal**. Esta fronteira
**não revalida fatos comerciais** e **não reabre seleção**: toda a autoridade
textual **já está incorporada** na `RespostaMontada` que ela recebe.

**Zero normalização.** Nada de `strip`, `lstrip`, `rstrip`, `lower`, `upper`,
`casefold`, normalização Unicode, expressão regular, `replace`, comparação
aproximada, correção de pontuação ou correção de espaço. Uma diferença de **um
único caractere** reprova.

**A comparação é sempre entre duas `str` exatas.** Isso é validado **antes**, e
não é zelo supérfluo: `str.__eq__` devolve `NotImplemented` diante do que não é
`str`, e Python então pergunta ao **outro** operando. Um `texto` de outro tipo
poderia, com um `__eq__` próprio, **decidir sozinho** o veredito desta fronteira
— o que seria uma aprovação silenciosa. Forma estrutural inválida **fecha**.

**Zero redação.** Ela **não** cria texto, **não** corrige texto, **não** devolve
versão corrigida, **não** escolhe fragmento e **não** produz *fallback*.

**Zero decisão comercial.** Ela não conhece YAML, preço, capacidade, pacote,
status, *binding*, **R2**, *witness*, ação, estado, evento ou handoff.

**Pureza.** **Zero I/O**, **zero *filesystem***, **zero rede**, **zero LLM**,
**zero YAML**, **zero índice**, **zero status**, **zero estado**, **zero
relógio**, **zero logging**, **zero *cache*** e **zero mutação** de qualquer
entrada.

***Fail-closed*, sem resultado parcial.** Entrada estrutural inválida sai como
`ValidacaoRespostaNaoAvaliavel`, com mensagem **exclusivamente estrutural** —
sem nada do conteúdo recebido.

**Zero vazamento.** Nenhum DTO de resultado carrega o texto candidato ou
`montada.texto`; nenhuma exceção inclui texto; nenhum `repr` inclui o corpo da
resposta.

**Escopo isolado.** Materializar esta fronteira **não** integra a etapa 10
*end-to-end*, **não** implementa o `OrquestradorMotor`, **não** implementa
**S2-D8**/`R2`, **não** decide `E15` nem `E12`, **não** resolve as superfícies
conversacionais sem fragmento aprovado e **não** emite mensagem alguma.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from casa77_sdr.response_assembly import RespostaMontada

__all__ = [
    "MotivoValidacaoResposta",
    "ResultadoValidacaoResposta",
    "ValidacaoRespostaNaoAvaliavel",
    "validar_resposta_final",
]


class MotivoValidacaoResposta(Enum):
    """Vocabulário **fechado** do veredito desta fronteira.

    São **dois** motivos, e apenas dois: a emissão é a forma canônica, ou não é.
    Nenhum deles carrega conteúdo — eles nomeiam o **veredito**, nunca a
    diferença encontrada. Um membro novo **exige nova arbitragem**.
    """

    APROVADO = "aprovado"
    TEXTO_DIVERGENTE = "texto_divergente"


@dataclass(frozen=True, slots=True)
class ResultadoValidacaoResposta:
    """O veredito, e nada além dele.

    `aprovado` é `True` **se e somente se** `motivo` for
    `MotivoValidacaoResposta.APROVADO`. **Nenhum texto** — candidato, montado ou
    corrigido — entra aqui: o resultado é seguro para log.
    """

    aprovado: bool
    motivo: MotivoValidacaoResposta


class ValidacaoRespostaNaoAvaliavel(Exception):
    """Erro de contrato **próprio** desta fronteira.

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **o
    que** está errado e o localizador diz **em que posição da chamada** — nunca
    o texto candidato, o texto montado, um token, o `Rxx`, o fragmento, um
    *binding*, o referente, um valor, um comprimento, uma posição, um índice, o
    `repr` ou o tipo concreto.

    Ela cobre **apenas** a forma estrutural das entradas. Texto **divergente**
    não é erro de contrato: é um **veredito normal**, devolvido como
    `TEXTO_DIVERGENTE`.
    """


# Categoria privada e fechada. Ela nomeia o impedimento e **nao** e vocabulario
# normativo novo: nenhum enum publico e criado para ela.
_TIPO_INVALIDO = "tipo_invalido"

# Localizadores estruturais fechados. Nomeiam a **posicao da chamada**, jamais o
# conteudo recebido.
_TEXTO_CANDIDATO = "texto_candidato"
_MONTADA = "montada"
_MONTADA_TEXTO = "montada.texto"


def validar_resposta_final(
    texto_candidato: object,
    montada: object,
) -> ResultadoValidacaoResposta:
    """Prova que o texto candidato **é** a forma canônica da montagem recebida.

    `montada` é a `RespostaMontada` **já produzida** por `montar_resposta_final`
    (§4.1.6). Esta fronteira **não abre arquivo algum**, **não consulta o
    índice**, **não reavalia a autorização** e **não chama LLM**.

    A ordem é **fixa**: **1.** o tipo exato de `texto_candidato`; **2.** o tipo
    exato de `montada`; **3.** a **comparação literal**; **4.** o
    `ResultadoValidacaoResposta`. A forma estrutural de `montada.texto` é
    exigida junto do passo 2 — ver abaixo.

    Devolve `aprovado=True` com `MotivoValidacaoResposta.APROVADO` quando os
    dois textos são **idênticos**; caso contrário, `aprovado=False` com
    `TEXTO_DIVERGENTE` — **qualquer** diferença basta, inclusive de espaço,
    quebra de linha, pontuação, caixa ou ponto de código Unicode. **Nada é
    normalizado** antes da comparação, e **nenhum texto corrigido é devolvido**.

    Levanta `ValidacaoRespostaNaoAvaliavel` com `tipo_invalido`
    (`texto_candidato`, `montada`, `montada.texto`). **Subclasse não é forma
    canônica.** **Nada é capturado** aqui: exceção de outra fronteira, se
    houvesse, atravessaria intacta.

    A exigência sobre **`montada.texto`** integra o *fail-closed* estrutural
    (**VR-7**) e é indispensável: `str.__eq__` devolve `NotImplemented` diante
    do que não é `str`, e Python então consulta o **outro** operando; um `texto`
    de outro tipo poderia, com um `__eq__` próprio, **forçar a aprovação**.

    **VALIDAR NÃO É DECIDIR O QUE DIZER, NEM CORRIGIR.** O que pode ser dito já
    foi decidido pela cadeia determinística a montante; o que fazer diante de um
    bloqueio pertence à etapa 12, fora desta fronteira.
    """
    if type(texto_candidato) is not str:
        raise _nao_avaliavel(_TIPO_INVALIDO, _TEXTO_CANDIDATO)
    if type(montada) is not RespostaMontada:
        raise _nao_avaliavel(_TIPO_INVALIDO, _MONTADA)
    # Forma estrutural invalida fecha **antes** da comparacao (VR-7). Sem esta
    # guarda, um `texto` que nao seja `str` exata receberia a comparacao
    # **refletida** e decidiria por conta propria o veredito. **P5: falha
    # fecha.**
    if type(montada.texto) is not str:
        raise _nao_avaliavel(_TIPO_INVALIDO, _MONTADA_TEXTO)

    # Regra unica, entre **duas `str` exatas** ja provadas acima. Zero
    # normalizacao: comparar e comparar.
    if texto_candidato == montada.texto:
        return ResultadoValidacaoResposta(
            True, MotivoValidacaoResposta.APROVADO
        )

    # Bloquear NAO e corrigir: nenhum texto substituto e devolvido, sugerido ou
    # calculado. O desfecho pertence a etapa 12.
    return ResultadoValidacaoResposta(
        False, MotivoValidacaoResposta.TEXTO_DIVERGENTE
    )


def _nao_avaliavel(
    categoria: str,
    localizador: str,
) -> ValidacaoRespostaNaoAvaliavel:
    return ValidacaoRespostaNaoAvaliavel(f"{categoria}: {localizador}")

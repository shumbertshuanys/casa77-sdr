"""Produtor determinístico de `E14` + `motivo_encerramento` (**S3-D1**).

Materializa a lacuna que `docs/07` §4.4 mantinha sem produtor: a **condição 8**
de `CondicoesCiclo`, `motivo_encerramento`, e o evento `E14` que a acompanha —
ambos **originados da interpretação do interessado**.

Ele acontece **depois da etapa 4** e **fora dela**. `N-b-RES1` permanece
intocada: a etapa 4 continua **proibida de emitir `Exx`** e de produzir
`motivo_encerramento` (N-b-G2, E-Nb-19), e termina em `Interpretacao`. Esta
fronteira **não é** o 15º componente de `docs/07` §4.1, **não é** etapa nova,
**não cria** evento, motivo, estado, transição, ação, condição ou pendência
nova, e **não é** o `OrquestradorMotor`. §4.1 permanece com **14** componentes e
§2 com **nove** responsabilidades.

**Saída fechada em `E14`**, e em nenhum outro evento:

| Sinal `ALTA` | `MotivoEncerramento` |
|---|---|
| `DESINTERESSE_DECLARADO` | `SEM_INTERESSE` |
| `CONTATO_POR_ENGANO` | `ENGANO` |
| `MENSAGEM_NAO_SOLICITADA` | `SPAM` |
| `ACEITACAO_DE_INCOMPATIBILIDADE` | `INCOMPATIBILIDADE_ACEITA` — **somente** com `ResultadoQualificacao.INCOMPATIVEL` |

**Somente confiança `ALTA` conta.** `BAIXA` **não entra** no conjunto de sinais
considerados — a regra "`BAIXA` = ausência para consumo estruturado" (N-b-D7,
N-b-Q2) vale aqui **sem exceção** — e **não impede** que um único sinal `ALTA`
diferente resolva.

**Conflito é fail-closed.** Com **dois ou mais** sinais `ALTA` o resultado é
`None`: nada é ordenado, ranqueado, somado ou escolhido como "o mais forte", e a
**ordem canônica de `intencoes_detectadas` não é precedência** (AJ1-A1e).
Encerrar a conversa é irreversível para o ciclo; diante de sinais contraditórios
a fronteira **não encerra**.

**A incompatibilidade é um *gate*, não um motivo.** `INCOMPATIBILIDADE_ACEITA`
exige **cumulativamente** o sinal semântico explícito de aceitação, com confiança
`ALTA`, **e** `ResultadoQualificacao.INCOMPATIVEL`. Estar incompatível não basta;
silêncio, ausência de contestação e ausência de pedido humano **não** são
aceitação. Nenhum outro campo de `Qualificacao` é lido: a função recebe
**apenas** o `ResultadoQualificacao`, nunca o objeto completo, e **nenhum fato
persistido novo** é criado.

**Esta fronteira é agnóstica ao estado.** Ela **não recebe** `Estado` nem
`SituacaoTakeover` e **não** cria regra nova de supressão de `E14`: o contrato
vigente da `MaquinaEstados` continua prevalecendo — em `encaminhado_humano` o
`E14` é consumido por **T32**, em `atendimento_humano` por **T34**, e nada disso
altera a regra de **zero resposta automática** em *takeover*. S3-D1 apenas
**produz** o evento interpretado; **a máquina decide a transição**.

**`E14` × `E18` → `N3` é preservado literalmente.** Esta fronteira **não conhece
`E18`**, **não recebe `motivos_handoff`** e **não chama** o `DetectorHandoff`.
Quando o resultado for combinado com `E18`, **T35 não entra**, o motivo **não é
ecoado** e `E14` é tratado segundo **N3** — pelo contrato vigente da máquina,
sem precedência nova.

O módulo é **puro e determinístico**: zero I/O, filesystem, rede, relógio, YAML,
`knowledge/**`, LLM, SDK, persistência, logging, cache, retry ou *sleep*. Ele
**não lê texto** da mensagem, **não recebe** `Estado`, `SituacaoTakeover`,
contexto, `CondicoesCiclo`, `motivos_handoff`, cobertura ou `dict[str, Any]`, e
**não muta** as entradas. Este módulo continua **somente** produzindo o
encerramento: projetar o `E14` na primeira agregação é feito pela **composição
dos insumos da primeira decisão** (`docs/07` §4.1.9). A coordenação completa
permanece do **`OrquestradorMotor` futuro**, que continua **ausente**.
"""

from __future__ import annotations

from dataclasses import dataclass

from casa77_sdr.identity import Confianca
from casa77_sdr.interpretation import (
    IntencaoConversacional,
    Interpretacao,
    _validar_interpretacao_canonica,
)
from casa77_sdr.qualification import ResultadoQualificacao
from casa77_sdr.state_machine import Evento, MotivoEncerramento

__all__ = ["EncerramentoInterpretado", "decidir_encerramento"]


#: Bijeção fechada **sinal → motivo**. É um **mapeamento**, não uma ordem: a
#: decisão só chega aqui quando existe **exatamente um** sinal `ALTA`, de modo
#: que nenhuma posição desta estrutura estabelece precedência sobre outra.
_MOTIVO_POR_SINAL: dict[IntencaoConversacional, MotivoEncerramento] = {
    IntencaoConversacional.DESINTERESSE_DECLARADO: MotivoEncerramento.SEM_INTERESSE,
    IntencaoConversacional.CONTATO_POR_ENGANO: MotivoEncerramento.ENGANO,
    IntencaoConversacional.MENSAGEM_NAO_SOLICITADA: MotivoEncerramento.SPAM,
    IntencaoConversacional.ACEITACAO_DE_INCOMPATIBILIDADE: (
        MotivoEncerramento.INCOMPATIBILIDADE_ACEITA
    ),
}


@dataclass(frozen=True)
class EncerramentoInterpretado:
    """O encerramento já decidido: **um** evento e **um** motivo estruturado.

    **Invariante**: `evento is Evento.E14`. Qualquer outro evento é rejeitado na
    construção — a estrutura não é um portador genérico de evento, e **nenhum
    segundo evento** existe nesta fronteira.

    A política de tipo é a do projeto: **tipo runtime incompatível** levanta
    `TypeError`; **invariante de valor inválido** levanta `ValueError`. Nenhuma
    exceção pública nova é criada.
    """

    evento: Evento
    motivo: MotivoEncerramento

    def __post_init__(self) -> None:
        if not isinstance(self.evento, Evento):
            raise TypeError("evento precisa ser um Evento")
        if not isinstance(self.motivo, MotivoEncerramento):
            raise TypeError("motivo precisa ser um MotivoEncerramento")
        if self.evento is not Evento.E14:
            raise ValueError(
                "EncerramentoInterpretado só representa Evento.E14"
            )


def decidir_encerramento(
    interpretacao: Interpretacao,
    resultado_qualificacao: ResultadoQualificacao,
) -> EncerramentoInterpretado | None:
    """Decide o encerramento a partir dos sinais já interpretados.

    Função pura e total sobre entrada válida: sem I/O, sem rede, sem relógio, sem
    persistência, sem LLM e sem mutação dos argumentos. Ela **não lê o texto** da
    mensagem — decide **exclusivamente** pelos códigos de
    `intencoes_detectadas` e pela confiança de cada um.

    A `Interpretacao` é **verificada como canônica válida** antes de qualquer
    decisão. `Interpretacao` é uma estrutura pública e pode ser construída
    diretamente; `isinstance` prova apenas o tipo, **não** a validade. A
    verificação **reutiliza** a validação já existente da fronteira N-b —
    nenhum validador paralelo é criado e nenhuma regra é copiada. Entrada
    inválida **bloqueia**: **nenhuma saída parcial** é produzida. A validação da
    `Interpretacao` corre **antes** da verificação de tipo do resultado de
    qualificação.

    Seja `S` o conjunto dos quatro sinais de encerramento cuja confiança seja
    `ALTA`:

    * `|S| == 0` → `None`;
    * `|S| == 1` → avalia o único sinal;
    * `|S| >= 2` → `None`, **fail-closed**.

    `None` é resultado legítimo: significa que **nenhum encerramento foi
    decidido neste ciclo**, não que a interpretação seja inválida.

    :raises TypeError: `interpretacao` que não é uma `Interpretacao`, ou
        `resultado_qualificacao` que não é um `ResultadoQualificacao`.
    :raises ValueError: erro de contrato `E-Nb-*` na `Interpretacao` recebida.
    """
    validada = _validar_interpretacao_canonica(interpretacao)
    if not isinstance(resultado_qualificacao, ResultadoQualificacao):
        raise TypeError(
            "resultado_qualificacao precisa ser um ResultadoQualificacao"
        )

    sinais = frozenset(
        item.codigo
        for item in validada.intencoes_detectadas
        if item.codigo in _MOTIVO_POR_SINAL and item.confianca is Confianca.ALTA
    )
    if len(sinais) != 1:
        return None

    (sinal,) = sinais
    # *Gate* cumulativo: o sinal semântico de aceitação só encerra quando a
    # qualificação determinística já concluiu pela incompatibilidade. O LLM
    # relata a postura da mensagem; ele **não** decide que existe
    # incompatibilidade, e esta fronteira não a recalcula.
    if (
        sinal is IntencaoConversacional.ACEITACAO_DE_INCOMPATIBILIDADE
        and resultado_qualificacao is not ResultadoQualificacao.INCOMPATIVEL
    ):
        return None

    return EncerramentoInterpretado(
        evento=Evento.E14, motivo=_MOTIVO_POR_SINAL[sinal]
    )

"""Composição dos insumos da primeira decisão do ciclo (`docs/07` §4.1.9).

Materializa as duas montagens que faltavam entre os **produtores já
materializados** e a **`MaquinaEstados`**: **agregar** os eventos confirmados por
produtores distintos e **montar** os oito campos de `CondicoesCiclo`.

O escopo é a **primeira chamada** da máquina num **ciclo iniciado por nova
mensagem do interessado** — o ciclo que já passou pela idempotência, não foi
encerrado como duplicata e chegou à **etapa 7** de `docs/07` §5. Ficam **fora**
desta fronteira: as **chamadas posteriores de fechamento do ciclo**, que reentram
com `E15` ou `E12` **depois do efeito real**; o **ciclo operacional próprio** de
`E13`; e o **retorno da integração de calendário**, `E16`.

Ela **compõe saídas já decididas** e nada mais. Ela **não chama** produtor algum,
**não chama** `decidir(...)`, **não recebe** `Estado` nem `Qualificacao`, **não
executa** o pipeline, **não resolve precedência** e **não produz efeito externo**.
Ela **não é** o 15º componente de §4.1 — §4.1 permanece com **14** componentes —,
**não é** etapa nova e **não é** o `OrquestradorMotor`, que continua **ausente**:
coordenar o pipeline e chamar a máquina seguem sendo dele.

**`E01` é obrigatório.** Uma execução válida desta fronteira é, por definição, um
ciclo que recebeu mensagem. `e01_confirmado` permanece **parâmetro explícito**
para que a fronteira **não fabrique o fato**: `False` é rejeitado como execução
inválida, e **nenhuma entrada válida produz tupla vazia**.

**Domínios fechados por slot**, verificados sem deduplicação silenciosa:

| Slot | Domínio |
|---|---|
| `eventos_interpretacao` | `E02`, `E03`, `E04`, `E05`, `E06`, `E10` |
| `eventos_internos` | `E07`, `E08`, `E09` |
| `handoff` | aporta `E18` |
| `encerramento` | aporta `E14` |
| `e01_confirmado` | aporta `E01` |

`E11`, `E12`, `E13`, `E15`, `E16` e `E17` **não são admitidos**: `E11`/`E17`
continuam **reduzidos a `E18`** pelo `DetectorHandoff` (`docs/06` §2.1); `E12` só
existe depois do resumo efetivamente gerado; `E13` chega em ciclo operacional
próprio; `E15` só depois da resposta comercial efetivamente concluída; e `E16` é
retorno da integração de calendário.

**A ordem da saída é a ordem de declaração do enum `Evento`.** Ela existe
**apenas para auditabilidade**: **ordem da tupla ≠ precedência semântica**. A
precedência permanece **exclusivamente** nas famílias **C0–C11** dentro da
`MaquinaEstados` (`docs/06` §4.2), que **não são copiadas aqui**.

**Eventos concorrentes não são suprimidos.** `E14` + `E18`, `E08` + `E18`,
`E09` + `E18`, `E06` + `E07`, `E06` + `E09` e os quatro eventos de dado
coexistem quando confirmados. Esta fronteira **não escolhe o mais importante**;
quem decide é a máquina.

**As condições 2 e 4 vêm da mesma execução de S2-D8** e são recebidas como
**dois booleanos já determinados** — nunca o `ResultadoS2D8` inteiro, que carrega
matéria alheia a `CondicoesCiclo`, como `pendencias_resposta`. Por isso a
validação é **all-or-none**: ou ambas foram avaliadas, ou nenhuma foi.

**`None`, `False` e `()` são distintos e nunca coagidos.** `False` significa
*avaliado e falso*; `None`, *não avaliado neste ciclo*; `()`, *coleção sem
elemento*. A única exceção é `motivos_handoff`, cujo contrato histórico já usa
`()` para ausência — e para o qual **nenhum `None` é inventado**.

**Esta fronteira valida somente o que ela própria compõe**: tipos, `E01`
obrigatório, domínio por slot, duplicatas e o par all-or-none de S2-D8. As
coerências semânticas — `E18` × `motivos_handoff`, `E14` × motivo sob T35, `E09`
× `pendencia_impeditiva`, `E06` × resposta disponível, `E07` × mutação e
qualificação positiva, `E07` × `E09` impeditiva, `E08` × `INCOMPATIVEL` e
`Identidade.AMBIGUA` — permanecem **exclusivamente** em `state_machine.py` e
**não são reimplementadas** aqui.

O módulo é **puro e determinístico**: zero I/O, filesystem, rede, relógio, YAML,
`knowledge/**`, LLM, SDK, persistência, logging, cache, retry, *sleep*, variável
de ambiente e aleatoriedade; ele **não muta** as entradas.
"""

from __future__ import annotations

from casa77_sdr.closure_decision import EncerramentoInterpretado
from casa77_sdr.handoff_detection import DeteccaoHandoff
from casa77_sdr.state_machine import CondicoesCiclo, Evento, Identidade

__all__ = [
    "agregar_eventos_primeira_decisao",
    "montar_condicoes_ciclo",
]


#: Domínio fechado do slot de eventos derivados da `Interpretacao` (`RES2-5`).
_DOMINIO_INTERPRETACAO: frozenset[Evento] = frozenset(
    {Evento.E02, Evento.E03, Evento.E04, Evento.E05, Evento.E06, Evento.E10}
)

#: Domínio fechado do slot de eventos internos do ciclo (`CIE-7`).
_DOMINIO_INTERNOS: frozenset[Evento] = frozenset(
    {Evento.E07, Evento.E08, Evento.E09}
)

#: Ordem **canônica** da saída — a ordem de declaração do enum `Evento`.
#: Auditabilidade apenas; **não** é precedência.
_ORDEM_CANONICA: tuple[Evento, ...] = tuple(Evento)


def _validar_slot(
    eventos: object, dominio: frozenset[Evento], nome: str
) -> tuple[Evento, ...]:
    """Valida um slot de eventos contra o seu domínio fechado.

    Tipo estrutural incompatível é `TypeError`; evento fora do domínio ou
    repetido dentro do slot é `ValueError`. **Nenhuma deduplicação silenciosa**
    acontece: uma colisão é erro de contrato do chamador, não ruído a esconder.
    """
    if not isinstance(eventos, tuple):
        raise TypeError(f"{nome} precisa ser uma tupla")
    vistos: set[Evento] = set()
    for evento in eventos:
        if not isinstance(evento, Evento):
            raise TypeError(f"cada item de {nome} precisa ser um Evento")
        if evento not in dominio:
            raise ValueError(f"{evento.value} não pertence ao domínio de {nome}")
        if evento in vistos:
            raise ValueError(f"{evento.value} repetido em {nome}")
        vistos.add(evento)
    return eventos


def agregar_eventos_primeira_decisao(
    e01_confirmado: bool,
    eventos_interpretacao: tuple[Evento, ...],
    eventos_internos: tuple[Evento, ...],
    handoff: DeteccaoHandoff | None,
    encerramento: EncerramentoInterpretado | None,
) -> tuple[Evento, ...]:
    """Une os eventos confirmados por produtores distintos, sem suprimir nenhum.

    Função pura e total sobre entradas válidas: sem I/O, sem rede, sem relógio,
    sem persistência, sem LLM e sem mutação dos argumentos. Ela **não chama**
    produtor algum — recebe o que eles já decidiram.

    `e01_confirmado` é **obrigatório e explícito**: `True` aporta `Evento.E01`;
    `False` é **execução inválida** nesta fronteira, porque a primeira decisão de
    um ciclo de nova mensagem pressupõe a mensagem. Nenhuma entrada válida
    devolve tupla vazia.

    A saída sai em **ordem canônica** do enum, **sem duplicata**, e essa ordem é
    **auditoria, não precedência**.

    :raises TypeError: `e01_confirmado` que não é `bool`, slot que não é tupla,
        item que não é `Evento`, ou `handoff`/`encerramento` de tipo incompatível.
    :raises ValueError: `e01_confirmado is False`, evento fora do domínio do seu
        slot, duplicata interna, ou duplicata global na projeção final.
    """
    if not isinstance(e01_confirmado, bool):
        raise TypeError("e01_confirmado precisa ser booleano")
    if not e01_confirmado:
        raise ValueError(
            "a primeira decisão de um ciclo de nova mensagem exige E01 confirmado"
        )

    da_interpretacao = _validar_slot(
        eventos_interpretacao, _DOMINIO_INTERPRETACAO, "eventos_interpretacao"
    )
    internos = _validar_slot(eventos_internos, _DOMINIO_INTERNOS, "eventos_internos")

    if handoff is not None and not isinstance(handoff, DeteccaoHandoff):
        raise TypeError("handoff precisa ser uma DeteccaoHandoff ou None")
    if encerramento is not None and not isinstance(
        encerramento, EncerramentoInterpretado
    ):
        raise TypeError("encerramento precisa ser um EncerramentoInterpretado ou None")

    projetados: list[Evento] = [Evento.E01]
    projetados.extend(da_interpretacao)
    projetados.extend(internos)
    if encerramento is not None:
        projetados.append(encerramento.evento)
    if handoff is not None:
        projetados.append(handoff.evento)

    # Pós-condição defensiva: impossível sob os domínios corretos, e por isso
    # mesmo verificada. `set` nunca é usado para **esconder** a colisão.
    if len(projetados) != len(set(projetados)):
        raise ValueError("evento duplicado na agregação da primeira decisão")

    confirmados = set(projetados)
    return tuple(evento for evento in _ORDEM_CANONICA if evento in confirmados)


def _validar_condicao_booleana(valor: object, nome: str) -> bool | None:
    if valor is not None and not isinstance(valor, bool):
        raise TypeError(f"{nome} precisa ser booleano ou None")
    return valor  # type: ignore[return-value]


def montar_condicoes_ciclo(
    insumo_qualificacao_atualizado: bool | None,
    pendencia_impeditiva: bool | None,
    handoff: DeteccaoHandoff | None,
    resposta_aprovada_disponivel: bool | None,
    interesse_confirmar_disponibilidade: bool | None,
    calendario_integrado: bool | None,
    identidade: Identidade | None,
    encerramento: EncerramentoInterpretado | None,
) -> CondicoesCiclo:
    """Monta as **oito** condições de `docs/07` §4.4, e nenhuma nona.

    Função pura e total sobre entradas válidas. Cada condição chega **já
    decidida** pelo seu produtor: a fronteira **transporta**, nunca recalcula,
    nunca lê configuração, ambiente, YAML ou calendário, e nunca inventa `False`
    onde o chamador informou `None`.

    As condições **2** e **4** vêm da **mesma execução de S2-D8** e por isso são
    validadas em conjunto: `None`/`None` ou `bool`/`bool`. Uma avaliada e a outra
    não é **erro de contrato**, não um estado representável.

    `motivos_handoff` é projetado do detector como `tuple[str, ...]`, preservando
    a **ordem** e a **ausência de duplicata** que ele já garante, e sem
    transportar `MotivoHandoff` como tipo para a máquina. `motivo_encerramento`
    vem do `EncerramentoInterpretado` e **não é suprimido** quando há `E18`
    concomitante: `E14` × `E18` continua sendo resolvido pela máquina, por **N3**.

    :raises TypeError: condição booleana que não é `bool | None`, `identidade`
        que não é `Identidade | None`, ou `handoff`/`encerramento` de tipo
        incompatível.
    :raises ValueError: apenas uma das condições **2** e **4** avaliada.
    """
    condicao_1 = _validar_condicao_booleana(
        insumo_qualificacao_atualizado, "insumo_qualificacao_atualizado"
    )
    condicao_2 = _validar_condicao_booleana(
        pendencia_impeditiva, "pendencia_impeditiva"
    )
    condicao_4 = _validar_condicao_booleana(
        resposta_aprovada_disponivel, "resposta_aprovada_disponivel"
    )
    condicao_5 = _validar_condicao_booleana(
        interesse_confirmar_disponibilidade, "interesse_confirmar_disponibilidade"
    )
    condicao_6 = _validar_condicao_booleana(
        calendario_integrado, "calendario_integrado"
    )

    if (condicao_2 is None) is not (condicao_4 is None):
        raise ValueError(
            "pendencia_impeditiva e resposta_aprovada_disponivel vêm da mesma "
            "execução de S2-D8: ou ambas são avaliadas, ou nenhuma é"
        )

    if identidade is not None and not isinstance(identidade, Identidade):
        raise TypeError("identidade precisa ser uma Identidade ou None")
    if handoff is not None and not isinstance(handoff, DeteccaoHandoff):
        raise TypeError("handoff precisa ser uma DeteccaoHandoff ou None")
    if encerramento is not None and not isinstance(
        encerramento, EncerramentoInterpretado
    ):
        raise TypeError("encerramento precisa ser um EncerramentoInterpretado ou None")

    motivos_handoff = (
        () if handoff is None else tuple(motivo.value for motivo in handoff.motivos)
    )

    return CondicoesCiclo(
        insumo_qualificacao_atualizado=condicao_1,
        pendencia_impeditiva=condicao_2,
        motivos_handoff=motivos_handoff,
        resposta_aprovada_disponivel=condicao_4,
        interesse_confirmar_disponibilidade=condicao_5,
        calendario_integrado=condicao_6,
        identidade=identidade,
        motivo_encerramento=None if encerramento is None else encerramento.motivo,
    )

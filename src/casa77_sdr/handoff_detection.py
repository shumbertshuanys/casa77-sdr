"""`DetectorHandoff` — produtor determinístico de `E18` e dos motivos de handoff.

Materializa o produtor que `docs/06` §9 atribui aos **gatilhos 3–10** de
`docs/04-handoff-humano.md`: ele reconhece os sinais **já interpretados** e emite
**um** `E18` carregando **todos** os motivos reconhecidos.

Ele acontece **depois da etapa 4** e **fora dela**. `N-b-RES1` permanece intocada:
a etapa 4 continua **proibida de emitir `Exx`** (N-b-G2, E-Nb-19) e termina em
`Interpretacao`. Esta fronteira **não é** o 15º componente de `docs/07` §4.1,
**não é** etapa nova, **não cria** evento, estado, transição, ação, condição ou
pendência nova, e **não é** o `OrquestradorMotor`. §4.1 permanece com **14**
componentes e §2 com **nove** responsabilidades.

**`docs/04` é a autoridade dos gatilhos.** Nenhum gatilho é criado, removido ou
reinterpretado aqui: este módulo apenas **reconhece** os que já existem.

**Saída fechada em `E18`**, e em nenhum outro evento:

| Sinal | `MotivoHandoff` | Gatilho de `docs/04` |
|---|---|---|
| `pedido_de_humano` verdadeiro | `PEDIDO_HUMANO` | 9 |
| `EXCECAO_SOLICITADA` | `EXCECAO_SOLICITADA` | 3 (contestação de regra) |
| `PEDIDO_DE_CONDICAO_ESPECIAL` | `PEDIDO_DESCONTO` | 3 |
| `PEDIDO_DE_CONFIRMACAO_DE_VISITA` | `CONFIRMACAO_VISITA` | 4, ramo **visita** |
| `PEDIDO_DE_RESERVA` | `CONFIRMACAO_RESERVA` | 4, ramo **reserva** |
| `INTENCAO_DE_CONTRATAR` | `CONTRATACAO` | 5 |
| `PEDIDO_DE_CANCELAMENTO` | `CANCELAMENTO` | 6 |
| `PEDIDO_DE_ALTERACAO_DE_DATA` | `ALTERACAO_DATA` | 7 |
| `ASSUNTO_JURIDICO_OU_CONTRATUAL` | `INTERPRETACAO_CONTRATUAL` | 8 |
| `RECLAMACAO_OU_TOM_HOSTIL` | `RECLAMACAO_OU_TOM_HOSTIL` | 10 |

**`ALTA` confirma; `BAIXA` não confirma** — com a **única exceção vigente** de
`pedido_de_humano` (N-b-PH3), que é sinal efetivo tanto em `ALTA` quanto em
`BAIXA`. Essa exceção **não é estendida por analogia** a nenhum outro sinal:
`EXCECAO_SOLICITADA` e os oito códigos de **AJ4** exigem `ALTA`.

**Disponibilidade de data fica fora desta fronteira.** O gatilho 4 de `docs/04`
separa **três** matérias, e só duas são handoff: **visita** e **reserva**.
**Disponibilidade** continua decidida pelas **condições 5 e 6** de §4.4 e pelas
transições **T14/T15/T25** — este módulo **não a conhece**. Interesse **simples**
em visita continua `INTERESSE_EM_VISITA` → `E10` → **T16**, e **não** é handoff.

**Os gatilhos 1–2 e 11–12 não passam por aqui.** Os gatilhos **1–2** chegam à
máquina como **`E09`**, produzidos a partir das causas de **S2-D8**, e **não são
reemitidos como `E18`** (`docs/06` §9). Os gatilhos **11–12** são materializados
por **transições** da §3 — T08, T13, T21, T40 —, não por detecção. Por isso
`informacao_pendente` **não** pertence ao vocabulário deste detector: ele
permanece registrável no **resumo e na auditoria** do caminho de pendência.

**`E11` e `E17` permanecem conceituais**: eles não entram na máquina, e o caminho
único de handoff obrigatório continua sendo `E18` (`docs/06` §2.1).

**Multiplicidade sem precedência.** Vários sinais na mesma `Interpretacao`
produzem **um único** `E18` com **vários motivos**, deduplicados de forma estável
e em **ordem canônica**. A ordem existe **apenas para auditabilidade** e **não
estabelece precedência semântica** (AJ1-A1e): nenhum "motivo principal" é
escolhido, e nenhum motivo derrota outro.

O módulo é **puro e determinístico**: zero I/O, filesystem, rede, relógio, YAML,
`knowledge/**`, LLM, SDK, persistência, logging, cache, retry ou *sleep*. Ele
**não lê o texto** da mensagem, **não usa palavra-chave, regex, score de
sentimento ou contagem**, e **não recebe** `Qualificacao`, `Estado`,
`SituacaoTakeover`, `CondicoesCiclo`, contexto, cobertura ou `dict[str, Any]`.
Ele **não constrói `CondicoesCiclo`**: projetar os motivos para a máquina —
`tuple(motivo.value for motivo in deteccao.motivos)` — é papel do
**`OrquestradorMotor` futuro**, que continua **ausente**.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from casa77_sdr.identity import Confianca
from casa77_sdr.interpretation import (
    IntencaoConversacional,
    Interpretacao,
    _validar_interpretacao_canonica,
)
from casa77_sdr.state_machine import Evento

__all__ = ["MotivoHandoff", "DeteccaoHandoff", "detectar_handoff"]


class MotivoHandoff(StrEnum):
    """Vocabulário **fechado** dos motivos de `E18` produzidos por esta fronteira.

    São exatamente os motivos que `docs/06` §2.1 enumera para os **gatilhos 3–10**
    de `docs/04`. **Nenhum motivo novo é criado** e **nenhum gatilho é inventado**.

    `informacao_pendente` **não** pertence a este vocabulário: os gatilhos **1–2**
    chegam como `E09` e **não são reemitidos** como `E18` (`docs/06` §9).

    A ordem de declaração é a **ordem canônica** da saída e existe **apenas para
    auditabilidade**: ela **não** estabelece precedência semântica alguma.
    """

    PEDIDO_HUMANO = "pedido_humano"
    EXCECAO_SOLICITADA = "excecao_solicitada"
    PEDIDO_DESCONTO = "pedido_desconto"
    CONFIRMACAO_VISITA = "confirmacao_visita"
    CONFIRMACAO_RESERVA = "confirmacao_reserva"
    CONTRATACAO = "contratacao"
    CANCELAMENTO = "cancelamento"
    ALTERACAO_DATA = "alteracao_data"
    INTERPRETACAO_CONTRATUAL = "interpretacao_contratual"
    RECLAMACAO_OU_TOM_HOSTIL = "reclamacao_ou_tom_hostil"


#: Ordem **canônica** dos motivos na saída — a ordem de declaração do enum.
#: Auditabilidade apenas; **não** é precedência.
_ORDEM_CANONICA: tuple[MotivoHandoff, ...] = tuple(MotivoHandoff)

#: Bijeção fechada **código autônomo → motivo**, para os sinais que exigem `ALTA`.
#: `pedido_de_humano` fica **fora** deste mapa porque a sua fonte autoritativa é o
#: **payload booleano**, não um código autônomo (AJ4, N-b-X1).
_MOTIVO_POR_CODIGO: dict[IntencaoConversacional, MotivoHandoff] = {
    IntencaoConversacional.EXCECAO_SOLICITADA: MotivoHandoff.EXCECAO_SOLICITADA,
    IntencaoConversacional.PEDIDO_DE_CONDICAO_ESPECIAL: MotivoHandoff.PEDIDO_DESCONTO,
    IntencaoConversacional.PEDIDO_DE_CONFIRMACAO_DE_VISITA: (
        MotivoHandoff.CONFIRMACAO_VISITA
    ),
    IntencaoConversacional.PEDIDO_DE_RESERVA: MotivoHandoff.CONFIRMACAO_RESERVA,
    IntencaoConversacional.INTENCAO_DE_CONTRATAR: MotivoHandoff.CONTRATACAO,
    IntencaoConversacional.PEDIDO_DE_CANCELAMENTO: MotivoHandoff.CANCELAMENTO,
    IntencaoConversacional.PEDIDO_DE_ALTERACAO_DE_DATA: MotivoHandoff.ALTERACAO_DATA,
    IntencaoConversacional.ASSUNTO_JURIDICO_OU_CONTRATUAL: (
        MotivoHandoff.INTERPRETACAO_CONTRATUAL
    ),
    IntencaoConversacional.RECLAMACAO_OU_TOM_HOSTIL: (
        MotivoHandoff.RECLAMACAO_OU_TOM_HOSTIL
    ),
}


@dataclass(frozen=True)
class DeteccaoHandoff:
    """O handoff já detectado: **um** evento e os motivos que o sustentam.

    **Invariantes**: `evento is Evento.E18`; `motivos` **não vazio**, composto
    **somente** de `MotivoHandoff`, **sem duplicata** e em **ordem canônica**.
    Construí-la com outro evento, sem motivo ou com motivo repetido é rejeitado —
    a estrutura não é um portador genérico de evento.

    A política de tipo é a do projeto: **tipo runtime incompatível** levanta
    `TypeError`; **invariante de valor inválido** levanta `ValueError`. Nenhuma
    exceção pública nova é criada.
    """

    evento: Evento
    motivos: tuple[MotivoHandoff, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.evento, Evento):
            raise TypeError("evento precisa ser um Evento")
        if not isinstance(self.motivos, tuple):
            raise TypeError("motivos precisa ser uma tupla")
        for motivo in self.motivos:
            if not isinstance(motivo, MotivoHandoff):
                raise TypeError("cada motivo precisa ser um MotivoHandoff")
        if self.evento is not Evento.E18:
            raise ValueError("DeteccaoHandoff só representa Evento.E18")
        if not self.motivos:
            raise ValueError("DeteccaoHandoff exige ao menos um motivo")
        if len(set(self.motivos)) != len(self.motivos):
            raise ValueError("motivos não admite duplicata")
        posicao = {motivo: indice for indice, motivo in enumerate(_ORDEM_CANONICA)}
        if list(self.motivos) != sorted(self.motivos, key=lambda m: posicao[m]):
            raise ValueError("motivos precisa estar em ordem canônica")


def detectar_handoff(interpretacao: Interpretacao) -> DeteccaoHandoff | None:
    """Reconhece os gatilhos 3–10 de `docs/04` sobre uma `Interpretacao` canônica.

    Função **total** sobre entrada válida e pura: sem I/O, sem rede, sem relógio,
    sem persistência, sem LLM e sem mutação do argumento. Ela **não lê o texto** da
    mensagem — decide **exclusivamente** pelo booleano `pedido_de_humano` e pelos
    códigos de `intencoes_detectadas`, com a confiança de cada um.

    A `Interpretacao` é **verificada como canônica válida** antes de qualquer
    produção. `Interpretacao` é uma estrutura pública e pode ser construída
    diretamente; `isinstance` prova apenas o tipo, **não** a validade. A
    verificação **reutiliza** a validação já existente da fronteira N-b — nenhum
    validador paralelo é criado e nenhuma regra é copiada. Entrada inválida
    **bloqueia**: **nenhuma saída parcial** é produzida.

    **`ALTA` confirma; `BAIXA` não confirma**, com a **única exceção vigente** de
    `pedido_de_humano` (N-b-PH3): verdadeiro é sinal efetivo em `ALTA` **e** em
    `BAIXA`. Nenhuma outra exceção existe.

    Vários sinais produzem **um único** `E18` com **vários motivos**, sem
    duplicata e em ordem canônica — **sem** motivo principal e **sem**
    precedência.

    `None` é resultado legítimo: significa que **nenhum gatilho de handoff foi
    reconhecido neste ciclo**, não que a interpretação seja inválida.

    :raises TypeError: valor que não é uma `Interpretacao`.
    :raises ValueError: erro de contrato `E-Nb-*` na `Interpretacao` recebida.
    """
    validada = _validar_interpretacao_canonica(interpretacao)

    motivos: set[MotivoHandoff] = set()

    # Exceção única de N-b-PH3: o payload booleano é autoritativo (N-b-X1), e
    # `BAIXA` **não** o reduz a ausência. Ela não é estendida por analogia.
    if validada.pedido_de_humano:
        motivos.add(MotivoHandoff.PEDIDO_HUMANO)

    for item in validada.intencoes_detectadas:
        motivo = _MOTIVO_POR_CODIGO.get(item.codigo)
        if motivo is not None and item.confianca is Confianca.ALTA:
            motivos.add(motivo)

    if not motivos:
        return None

    return DeteccaoHandoff(
        evento=Evento.E18,
        motivos=tuple(motivo for motivo in _ORDEM_CANONICA if motivo in motivos),
    )

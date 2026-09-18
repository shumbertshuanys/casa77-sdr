"""Produtor determinístico de eventos derivados da `Interpretacao` (`N-b-RES2`).

Materializa o **residual explícito de integração** que `N-b-RES2` mantinha sem
produtor concreto: a transformação dos **sinais já interpretados** em **eventos
confirmados** do vocabulário `E01`–`E18` de `docs/06` §2.

Ele acontece **depois da etapa 4** e **fora dela**. `N-b-RES1` permanece
intocada: a etapa 4 continua **proibida de emitir `Exx`**, e o produtor não
determinístico continua terminando em `Interpretacao`. Esta fronteira **não é**
o 15º componente de `docs/07` §4.1, **não é** etapa nova, **não cria evento
novo**, **não é** extensão da etapa 4 e **não é** o `OrquestradorMotor`. §4.1
permanece com **14** componentes e §2 com **nove** responsabilidades.

**Saída fechada em seis eventos**, e nenhum outro:

| Evento | Sinal autoritativo |
|---|---|
| `E02` | `dados_extraidos.tipo_evento` |
| `E03` | `dados_extraidos.data_nomeada` |
| `E04` | `dados_extraidos.convidados` |
| `E05` | `dados_extraidos.formato` |
| `E06` | ao menos uma `PerguntaComercial` de confiança `ALTA` |
| `E10` | `INTERESSE_EM_VISITA` com confiança `ALTA` |

**`ALTA` confirma; `BAIXA` não confirma.** A regra "`BAIXA` = ausência para
consumo estruturado" (N-b-D7, N-b-Q2) vale aqui **sem exceção**: a exceção única
de `pedido_de_humano` (N-b-PH3) pertence ao caminho do `DetectorHandoff` e
**não** atravessa esta fronteira.

**O que esta fronteira nunca produz.** `E01`, `E07`, `E08`, `E09`, `E11`, `E12`,
`E13`, `E14`, `E15`, `E16`, `E17` e `E18`. Em particular: `E11` e `E17`
continuam **reduzidos a `E18` pelo `DetectorHandoff`** (`docs/06` §2.1, §9);
as **causas** de `E09` pertencem a **S2-D8**, e confirmá-lo é do **produtor
determinístico posterior de `E07`/`E08`/`E09`** (`docs/07` §6.3,
`CIE-1`–`CIE-10`), já materializado; `E07`/`E08` pertencem à qualificação e ao
ciclo; `E14` permanece em **`S3-D1`**.

O módulo é **puro e determinístico**: zero I/O, rede, relógio, YAML,
`knowledge/**`, LLM, SDK, persistência, logging, cache, retry ou *sleep*. Ele
**não recebe** `Qualificacao`, `Estado`, `CondicoesCiclo`, resultado de S2-D8 ou
contexto global, e **não produz** condição, qualificação, ação, resposta,
*handoff* ou persistência, e **não agrega** eventos: a sua saída é **consumida**
pela **composição dos insumos da primeira decisão** (`docs/07` §4.1.9), que une
as saídas dos produtores. Coordenar o pipeline continua sendo papel do
**`OrquestradorMotor` futuro**, que continua **ausente**.
"""

from __future__ import annotations

from casa77_sdr.identity import Confianca
from casa77_sdr.interpretation import (
    IntencaoConversacional,
    Interpretacao,
    _validar_interpretacao_canonica,
)
from casa77_sdr.state_machine import Evento

__all__ = ["produzir_eventos_da_interpretacao"]


#: Ordem **canônica** da saída. Existe **apenas para auditabilidade** e **não
#: estabelece precedência semântica** alguma — exatamente como a ordem de
#: `intencoes_detectadas` (AJ1-A1e). Ela é independente da ordem dos itens da
#: entrada.
_ORDEM_CANONICA: tuple[Evento, ...] = (
    Evento.E02,
    Evento.E03,
    Evento.E04,
    Evento.E05,
    Evento.E06,
    Evento.E10,
)

#: Os quatro **eventos de dado** e o campo autoritativo de cada um (N-b-X1).
_EVENTO_POR_CAMPO: tuple[tuple[str, Evento], ...] = (
    ("tipo_evento", Evento.E02),
    ("data_nomeada", Evento.E03),
    ("convidados", Evento.E04),
    ("formato", Evento.E05),
)


def produzir_eventos_da_interpretacao(
    interpretacao: Interpretacao,
) -> tuple[Evento, ...]:
    """Converte os sinais de uma `Interpretacao` canônica em eventos confirmados.

    Função pura e total sobre entrada válida: sem I/O, sem rede, sem relógio,
    sem persistência, sem LLM e sem mutação do argumento.

    A `Interpretacao` é **verificada como canônica válida** antes de qualquer
    produção. `Interpretacao` é uma estrutura pública e pode ser construída
    diretamente; `isinstance` prova apenas o tipo, **não** a validade. A
    verificação **reutiliza** a validação já existente da fronteira N-b —
    nenhum validador paralelo é criado e nenhuma regra é copiada. Entrada
    inválida **bloqueia**: **nenhuma saída parcial** é produzida.

    Cada evento é produzido **no máximo uma vez**, e `E06` é produzido **uma
    única vez** qualquer que seja o número de `PerguntaComercial` de confiança
    `ALTA` — independentemente do assunto de cada uma, inclusive
    `ASSUNTO_NAO_CLASSIFICADO`. **Cobertura não é consultada**: `R2` e S2-D8
    ficam fora desta fronteira.

    Tupla **vazia** é resultado legítimo: significa que nenhum sinal foi
    confirmado neste ciclo, não que a interpretação seja inválida.

    :raises TypeError: valor que não é uma `Interpretacao`.
    :raises ValueError: erro de contrato `E-Nb-*` na `Interpretacao` recebida.
    """
    validada = _validar_interpretacao_canonica(interpretacao)

    confirmados: set[Evento] = set()

    dados = validada.dados_extraidos
    for campo, evento in _EVENTO_POR_CAMPO:
        if (
            getattr(dados, campo) is not None
            and getattr(dados, f"confianca_{campo}") is Confianca.ALTA
        ):
            confirmados.add(evento)

    # `E06` é **um** evento, nunca um por pergunta (doc 06 §2). O filtro único
    # de efetividade continua sendo a confiança (N-b-Q2, N-b-Q3).
    if any(
        pergunta.confianca is Confianca.ALTA
        for pergunta in validada.perguntas_comerciais
    ):
        confirmados.add(Evento.E06)

    # `E10` vem do **código autônomo**, jamais de texto, palavra-chave ou
    # assunto: inferir visita a partir de texto seria reinterpretar a mensagem.
    if any(
        item.codigo is IntencaoConversacional.INTERESSE_EM_VISITA
        and item.confianca is Confianca.ALTA
        for item in validada.intencoes_detectadas
    ):
        confirmados.add(Evento.E10)

    return tuple(evento for evento in _ORDEM_CANONICA if evento in confirmados)

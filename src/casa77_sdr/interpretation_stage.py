"""Fronteira operacional da cadeia N-b (`docs/07` §6.3, `EN4-1`–`EN4-12`).

Materializa a **junta física** entre a **etapa 4** — a produção da
`Interpretacao` canônica — e os **três consumidores determinísticos** que já
existiam e já eram chamados separadamente: a **projeção para a identidade**, a
**condição 5** de `docs/07` §4.4 e o **produtor de eventos derivados**
(`N-b-RES2`).

Ela **compõe chamadas já aprovadas** e nada mais. Ela **não copia regra**,
**não revalida** entrada, **não canonicaliza** de novo e **não decide** nada: as
validações vivem, intactas, dentro de cada fronteira chamada.

**Uma chamada ao produtor por invocação.** Cada invocação bem formada de
`executar_interpretacao_do_ciclo(...)` executa `interpretar_mensagem(...)`
**exatamente uma vez** e, por consequência, provoca **no máximo uma** chamada ao
`ProdutorTextoEstruturado`. Não há laço, retry, *fallback*, cache nem fila em
torno dela.

Essa garantia é **local à invocação**. A unicidade **por ciclo** continua
dependendo da coordenação futura: **o `OrquestradorMotor` deverá invocar esta
fronteira no máximo uma vez por ciclo de nova mensagem.** Enquanto ele não
existir, nada aqui impede que um chamador a invoque duas vezes — e este módulo
**não é** o `OrquestradorMotor`, **não é** etapa nova, **não é** subetapa e
**não é** o 15º componente de §4.1, que permanece com **14**.

**A mesma `Interpretacao` atravessa as três derivações.** A instância devolvida
pela única chamada da etapa 4 é a que chega a `projetar_para_identidade(...)`, a
`decidir_interesse_confirmar_disponibilidade(...)` e a
`produzir_eventos_da_interpretacao(...)`, e é a que fica no DTO para os
consumidores posteriores reutilizarem. **Nenhuma segunda interpretação da mesma
mensagem é produzida.**

**Ordem canônica**: `interpretar_mensagem` → `projetar_para_identidade` →
`decidir_interesse_confirmar_disponibilidade` →
`produzir_eventos_da_interpretacao` → DTO. A produção da `Interpretacao`
**antes** das derivações é **obrigatória**; a ordem relativa entre as **três
derivações** é **operacional e auditável**, e **não** expressa precedência
semântica.

**Co-locação física não redefine a etapa 4.** `produzir_eventos_da_interpretacao`
continua sendo **`N-b-RES2`**: fronteira **posterior à etapa 4 e fora dela**.
**`N-b-G2`**, **`N-b-RES1`**, **`N-b-RES3`** e **`RES2-1`**–**`RES2-12`**
permanecem literais — a etapa 4 **continua não emitindo `Exx`**. O que este
módulo faz é **encadear fisicamente** produção e derivação num único artefato
operacional. **Produzir não é consumir**: o coordenador futuro pode **descartar**
os eventos se o ciclo terminar antes da etapa 7.

**Sem `Interpretacao`, nada é derivado.** Se `interpretar_mensagem(...)`
levantar `FalhaProdutorInterpretacao`, a exceção **propaga intacta**: nenhuma
derivação é chamada, **nenhum DTO é construído** e **nenhum campo `None` é
fabricado**. **`N-b-M1`**/**`N-b-M2`** continuam valendo — sem `Interpretacao` a
etapa 5 não executa e o ciclo **não alcança** as etapas 6 e 7. Em particular,
`montar_condicoes_ciclo(...)` **não é chamada** com uma condição 5 ausente.
`decidir_interesse_confirmar_disponibilidade(None) is None` continua contrato da
função existente, e **não é exercido por este caminho**.

Erros de contrato — `TypeError` e os `E-Nb-*` como `ValueError` — também
**propagam intactos**: não são capturados, não viram
`FalhaProdutorInterpretacao`, não viram ausência silenciosa, não viram
`Identidade.AMBIGUA` e **não produzem DTO parcial**. **Nenhuma taxonomia nova.**

A dependência é o **protocolo** `ProdutorTextoEstruturado`, nunca um adaptador
concreto: este módulo **não cria cliente**, **não lê ambiente**, **não lê
`.env`**, **não escolhe** fornecedor, modelo, SDK ou credencial e **não lê o
prompt do filesystem** — `prompt_sistema` chega como **argumento explícito**, e
o mecanismo de carga permanece fora do escopo.

**Fora desta fronteira**, e pertencentes ao pipeline coordenado pelo
`OrquestradorMotor` futuro: `detectar_handoff`, `decidir_encerramento`,
`atualizar_dados_atendimento`, `decidir_pendencias_e_cobertura`,
`produzir_eventos_internos_ciclo`, `agregar_eventos_primeira_decisao`,
`montar_condicoes_ciclo`, a resolução de identidade e `decidir`. A
`Interpretacao` fica no DTO **justamente** para que esses consumidores
posteriores reutilizem **o mesmo objeto**.

Salvo a chamada ao produtor feita **dentro** de `interpretar_mensagem`, o módulo
é **puro**: zero filesystem, rede direta, relógio, aleatoriedade, YAML,
`knowledge/**`, persistência, logging, cache, retry, fila, *sleep*, SDK,
variável de ambiente, emissão, alerta e chamada à máquina.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from casa77_sdr.identity import ProjecaoInterpretacao
from casa77_sdr.interpretation import (
    Interpretacao,
    decidir_interesse_confirmar_disponibilidade,
    projetar_para_identidade,
)
from casa77_sdr.interpretation_events import produzir_eventos_da_interpretacao
from casa77_sdr.interpretation_llm import (
    ProdutorTextoEstruturado,
    interpretar_mensagem,
)
from casa77_sdr.state_machine import Evento

__all__ = [
    "ArtefatosInterpretacao",
    "executar_interpretacao_do_ciclo",
]


@dataclass(frozen=True, slots=True)
class ArtefatosInterpretacao:
    """Os quatro artefatos de uma única interpretação da mensagem.

    `interpretacao` e `projecao_identidade` ficam **fora do `repr`** por
    carregarem matéria de runtime: o primeiro transporta texto conversacional e
    PII; o segundo, o tipo e a data nominais do evento. O `repr` do DTO expõe
    **somente** os eventos confirmados e o booleano da condição 5 — nenhum nome,
    contato, pergunta comercial, trecho ambíguo, tipo nominal ou data nominal.
    """

    interpretacao: Interpretacao = field(repr=False)
    projecao_identidade: ProjecaoInterpretacao = field(repr=False)
    eventos_interpretacao: tuple[Evento, ...]
    interesse_confirmar_disponibilidade: bool


def executar_interpretacao_do_ciclo(
    mensagem: str,
    *,
    produtor: ProdutorTextoEstruturado,
    prompt_sistema: str,
) -> ArtefatosInterpretacao:
    """Mensagem normalizada → os quatro artefatos da cadeia N-b.

    Executa `interpretar_mensagem(...)` **exatamente uma vez** e entrega a
    **mesma instância** de `Interpretacao` às três derivações, na ordem
    canônica. **Zero retry**, zero *fallback*, zero cache e zero fila.

    A garantia de chamada única é **por invocação desta fronteira**. Invocá-la
    no máximo uma vez por ciclo de nova mensagem é obrigação do
    `OrquestradorMotor` futuro, que **continua ausente**.

    Nenhuma regra é copiada e nada é revalidado aqui: a canonicidade da
    `Interpretacao`, a projeção, a condição 5 e o mapeamento de eventos
    permanecem sob as fronteiras já aprovadas.

    :raises FalhaProdutorInterpretacao: **nenhuma `Interpretacao` neste ciclo** —
        a exceção **propaga intacta**, nenhuma derivação executa e **nenhum DTO
        é construído**. Sem `Interpretacao`, a etapa 5 não executa (N-b-M1).
    :raises TypeError: tipo runtime incompatível, propagado intacto.
    :raises ValueError: erro de contrato `E-Nb-*`, propagado intacto.
    """
    interpretacao = interpretar_mensagem(
        mensagem,
        produtor=produtor,
        prompt_sistema=prompt_sistema,
    )

    projecao = projetar_para_identidade(interpretacao)
    interesse = decidir_interesse_confirmar_disponibilidade(interpretacao)
    eventos = produzir_eventos_da_interpretacao(interpretacao)

    return ArtefatosInterpretacao(
        interpretacao=interpretacao,
        projecao_identidade=projecao,
        eventos_interpretacao=eventos,
        interesse_confirmar_disponibilidade=interesse,
    )

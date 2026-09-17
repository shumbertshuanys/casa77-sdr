"""Produtor determinístico dos eventos internos do ciclo — `E07`, `E08`, `E09`.

Materializa a fronteira que `docs/06` §2.2 e `docs/07` §4.4.1 mantinham **sem
produtor concreto**: a transformação de resultados **já estruturados** da
qualificação e de **S2-D8** nos três eventos internos do vocabulário `E01`–`E18`
de `docs/06` §2.

Ela acontece **depois** da qualificação e **depois** de S2-D8, e **fora de
ambas**. Nenhuma das duas muda: `qualification.py` e `coverage_decision.py`
permanecem as autoridades das suas próprias fronteiras, e **S2-D8 continua não
criando nem confirmando `E09`** (**D8-E8**) — ela produz as **causas**, e esta
fronteira apenas as converte em evento. Esta fronteira **não é** o 15º
componente de `docs/07` §4.1, **não é** etapa nova, **não é** o agregador e
**não é** o `OrquestradorMotor`. §4.1 permanece com **14** componentes e §2 com
**nove** responsabilidades.

**Saída fechada em três eventos**, e nenhum outro:

| Evento | Condição necessária e suficiente |
|---|---|
| `E07` | `insumo_qualificacao_atualizado is True` **e** resultado `QUALIFICADO` ou `QUALIFICADO_COM_RESSALVA` |
| `E08` | resultado `INCOMPATIVEL` |
| `E09` | `resultado_s2d8.causas_e09` **não vazio** |

**`E07` não é decidido aqui.** A **mutação efetiva** de um insumo de
`DadosQualificacao` é fato da etapa apropriada (`docs/06` §4.1): esta fronteira
**recebe** esse booleano já decidido e **não compara** dado anterior com atual.
`False` não confirma, e o sinal precisa ser um `bool` **real** — inteiro, texto
ou `None` **não** são aceitos como substituto silencioso.

**`E08` não é recalculado aqui.** A `Qualificacao` recebida é a saída estruturada
da fronteira de qualificação. Esta fronteira **não relê YAML**, **não recalcula
incompatibilidade**, **não cria `Violacao`** e **não interpreta valor comercial**.
A **escolha entre as classes** de violação — **T05/T22** × **T06/T23** — continua
na `MaquinaEstados` (`docs/06` §3), e **nenhum sinal adicional** de
"incompatibilidade detectada" é criado.

**`E09` é confirmado pelas causas, e só por elas.** As `causas_e09` são a
**evidência autoritativa** de S2-D8. Não basta `resposta_aprovada_disponivel is
False`, e não basta `pendencia_impeditiva is True`: **sem causa correspondente
não existe `E09`**. As causas **não são reconstruídas, deduplicadas nem
reinterpretadas** aqui — `MotivoE09` e `ClassificacaoPendencia` continuam
pertencendo a S2-D8, que já é a autoridade de **A ∪ B**, da deduplicação, da
canonicalização, de **impeditiva × acessória** e dos metadados estruturados.
Qualquer quantidade de causas confirma **um único** `E09` (`docs/06` §2.2,
regra 2).

`IMPEDITIVA` **pertence ao contrato** e a sua inalcançabilidade sob **`Q1`** é
propriedade de `Q1`, **não** deste produtor: nada aqui exige que a causa seja
acessória.

**A ordem da saída é `E07`, `E08`, `E09`.** Ela existe **apenas para
auditabilidade** e **não estabelece precedência semântica** alguma — a
precedência continua sendo das famílias **C0–C11** da `MaquinaEstados`
(`docs/06` §4.2). `E07` e `E08` **não coexistem**, porque os seus resultados de
qualificação são mutuamente exclusivos; mas **nenhuma exclusão artificial** é
criada entre `E07` e um `E09` acessório, nem entre `E08` e um `E09` acessório.
Quem decide consumo e precedência é a máquina.

**O que esta fronteira nunca produz.** `E01`, `E02`–`E06`, `E10`, `E11`, `E12`–
`E16`, `E17` e `E18`. Ela **não agrega** a saída de `N-b-RES2`, de **S3-D1** ou
do **`DetectorHandoff`**; **não monta `CondicoesCiclo`**; **não transporta
`causas_e09`** para a máquina — elas continuam sendo metadado de auditoria a
montante (**D8-E8**) —; **não chama `decidir(...)`**; e **não executa ação,
seleção de fato, composição de texto ou persistência**.

O módulo é **puro e determinístico**: zero I/O, filesystem, rede, relógio, YAML,
`knowledge/**`, LLM, SDK, persistência, logging, cache, retry ou *sleep*; ele
**não muta** as entradas. Unir os eventos de **produtores distintos** e montar as
condições do ciclo é papel do **`OrquestradorMotor` futuro**, que continua
**ausente**.
"""

from __future__ import annotations

from casa77_sdr.coverage_decision import ResultadoS2D8
from casa77_sdr.qualification import Qualificacao, ResultadoQualificacao
from casa77_sdr.state_machine import Evento

__all__ = ["produzir_eventos_internos_ciclo"]


#: Ordem **canônica** da saída. Existe **apenas para auditabilidade** e **não
#: estabelece precedência semântica** alguma: a precedência é das famílias
#: C0–C11 da `MaquinaEstados` (`docs/06` §4.2).
_ORDEM_CANONICA: tuple[Evento, ...] = (Evento.E07, Evento.E08, Evento.E09)

#: Os dois resultados que tornam `E07` confirmável (`docs/06` §2.2, ramo b).
#: `INCOMPATIVEL` confirma `E08`; `DADOS_INCOMPLETOS` e `INDEFINIDO` não
#: confirmam nenhum dos dois.
_RESULTADOS_POSITIVOS: frozenset[ResultadoQualificacao] = frozenset(
    {
        ResultadoQualificacao.QUALIFICADO,
        ResultadoQualificacao.QUALIFICADO_COM_RESSALVA,
    }
)


def produzir_eventos_internos_ciclo(
    qualificacao: Qualificacao,
    insumo_qualificacao_atualizado: bool,
    resultado_s2d8: ResultadoS2D8,
) -> tuple[Evento, ...]:
    """Converte qualificação e resultado de S2-D8 em `E07`, `E08` e `E09`.

    Função pura e total sobre entradas válidas: sem I/O, sem rede, sem relógio,
    sem persistência, sem LLM e sem mutação dos argumentos.

    Ela **recebe fatos já decididos** e não os recalcula: a `Qualificacao` vem da
    fronteira de qualificação, o booleano de mutação vem da etapa que compara o
    contexto recuperado (`docs/06` §4.1) e as causas vêm de S2-D8.

    Tupla **vazia** é resultado legítimo: significa que nenhum dos três eventos
    foi confirmado neste ciclo, não que a entrada seja inválida. Cada evento
    aparece **no máximo uma vez**, em ordem canônica — que é auditoria, **não**
    precedência.

    :raises TypeError: `qualificacao` que não é uma `Qualificacao`,
        `insumo_qualificacao_atualizado` que não é um `bool` real, ou
        `resultado_s2d8` que não é um `ResultadoS2D8`.
    """
    if not isinstance(qualificacao, Qualificacao):
        raise TypeError("qualificacao precisa ser uma Qualificacao")
    # `bool` real: `isinstance` já rejeita `int`, `str` e `None`, e a rejeição é
    # deliberada — `None` significa "não avaliado neste ciclo" (`docs/06` §4.1)
    # e **não** equivale a verdadeiro.
    if not isinstance(insumo_qualificacao_atualizado, bool):
        raise TypeError("insumo_qualificacao_atualizado precisa ser booleano")
    if not isinstance(resultado_s2d8, ResultadoS2D8):
        raise TypeError("resultado_s2d8 precisa ser um ResultadoS2D8")
    if not isinstance(qualificacao.resultado, ResultadoQualificacao):
        raise TypeError("o resultado da qualificação precisa ser ResultadoQualificacao")
    if not isinstance(resultado_s2d8.causas_e09, tuple):
        raise TypeError("causas_e09 precisa ser uma tupla")

    confirmados: set[Evento] = set()

    # `E07` exige **as duas** condições no mesmo ciclo (`docs/06` §2.2, ramo a
    # e ramo b). A mutação não é inferida aqui.
    if insumo_qualificacao_atualizado and qualificacao.resultado in _RESULTADOS_POSITIVOS:
        confirmados.add(Evento.E07)

    # `E08` lê a classificação já calculada; a classe da violação — T05/T22 ×
    # T06/T23 — continua sendo decidida pela `MaquinaEstados`.
    if qualificacao.resultado is ResultadoQualificacao.INCOMPATIVEL:
        confirmados.add(Evento.E08)

    # `E09` vem das **causas**, jamais de `resposta_aprovada_disponivel` ou de
    # `pendencia_impeditiva` isoladamente. Qualquer quantidade de causas
    # confirma **um** evento (`docs/06` §2.2, regra 2).
    if resultado_s2d8.causas_e09:
        confirmados.add(Evento.E09)

    return tuple(evento for evento in _ORDEM_CANONICA if evento in confirmados)

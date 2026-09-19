"""Primitiva única de **emissibilidade estrutural** de um fragmento.

**`D8-F` continua sendo UMA norma** (`docs/07` §4.4.1). O que existe aqui é
**uma implementação compartilhada** dela: dada a **fotografia** já recebida de
um fragmento **que já é candidato**, esta fronteira responde a **uma** pergunta
e nada mais —

> este fragmento está **emitível agora**?

**O que ela NÃO conhece.** `AssuntoComercial`, `PerguntaComercial`, `CausaE09`,
`MotivoE09`, `R2`, grupo, ***witness***, cobertura, pendência, evento, máquina,
ação e *handoff* **não entram aqui**. Ela **não** produz `E09`, **não**
classifica **impeditiva × acessória** e **não** decide cobertura: tudo isso
continua pertencendo a **S2-D8** (§4.4.3), que é quem projeta os impedimentos
devolvidos daqui em causas estruturadas.

**Candidatura ≠ emissibilidade.** Os *gates* de candidatura — **`D8-G`**, de
preço, e o de **`R05`** (**`D8P-11`**) — **não** vivem aqui. Eles correm
**antes**, em S2-D8, porque são eles que decidem quais grupos são **aplicáveis**
(**`D8-L4`**). Esta fronteira recebe **somente** token que **já é candidato**.

**Pureza.** **Zero I/O**, ***filesystem***, YAML, `knowledge/**`, rede, LLM,
relógio, calendário, ambiente, *logging*, *cache* e mutação de entrada. Todas as
estruturas chegam **carregadas e já conferidas** pelo chamador: o rótulo de
status, a divergência de **Classe II**, os caminhos de **`C-7`** e os pares de
**`ASSERTIVA` de runtime** com o valor já resolvido.

**Ordem fixa das causas.** **`D8-F1`** (status) → **Classe II** (**`D8-CII`**)
→ **`C-7`**, na **ordem física recebida** → **`ASSERTIVA` de runtime**. Ela
existe para que a sequência de impedimentos seja **determinística** —
**nenhuma ordenação lexical** é aplicada, e **nenhuma deduplicação** acontece
aqui: deduplicar é decisão de quem projeta as causas (**`D8-E4`**).

**Sem exceção própria.** Esta fronteira é **total** sobre a fotografia recebida
e **não valida forma**: a conferência já foi feita a montante. A única exceção
que pode atravessá-la é `AssertivaNaoAvaliavel`, da fronteira de origem, e ela
atravessa **intacta** — exatamente como antes da extração.
"""

from __future__ import annotations

from dataclasses import dataclass

from casa77_sdr.response_assertion import avaliar_assertiva

__all__ = [
    "FotografiaFragmento",
    "ImpedimentoEmissao",
    "ResultadoEmissibilidade",
    "avaliar_emissibilidade",
]

# Rotulo canonico de `C-3` que **habilita** a emissao (D8-F1). `AGUARDA_APROVACAO`
# e `BLOQUEADO` nao habilitam (D8-F4). A **autoridade** do vocabulario de status
# continua no indice, e a sua validacao continua em S2-D8: aqui ele e apenas
# comparado.
_APROVADO = "APROVADO"


@dataclass(frozen=True, slots=True)
class ImpedimentoEmissao:
    """**Um** motivo estrutural pelo qual o fragmento **não** é emitível agora.

    Ele tem **exatamente uma** variação, e ela é o `caminho_yaml`:

    - **sem caminho** (`None`) — status não emitível, divergência de Classe II
      ou `ASSERTIVA` de runtime falsa;
    - **com caminho** — um `ReferenteIndisponivel` de **`C-7`**, carregando o
      caminho **literal já conferido a montante**, transportado **sem nova
      resolução e sem reinterpretação**.

    **Ele não é vocabulário comercial.** Não é `MotivoE09`, não é
    `ClassificacaoPendencia`, não carrega `AssuntoComercial`, valor de campo,
    texto de pergunta, PII ou `Rxx`. Traduzi-lo em causa — e classificá-la — é
    matéria de **S2-D8**.
    """

    caminho_yaml: str | None = None


@dataclass(frozen=True, slots=True)
class FotografiaFragmento:
    """Tudo o que se precisa saber de **um** fragmento candidato, já resolvido.

    `status` é o rótulo canônico de `C-3` **já conferido**. `divergente` diz se
    o token consta dos `tokens_divergentes` do `ValidadorConsistenciaBase` —
    **qualquer** `Divergencia`, inclusive `FORMATO_INAPLICAVEL` (**`D8-CII1`**,
    **`D8-CII3`**); ela **não é reavaliada aqui** (**`R2F-12`**).
    `referentes_indisponiveis` são os caminhos de **`C-7`**, na **ordem física
    recebida**. `assertivas_runtime` são os pares `(predicado, valor)` de
    **`ASSERTIVA` de runtime**, com o **valor de fato já resolvido** pelo
    chamador a partir da fotografia factual autoritativa.

    **Runtime é fotografia recebida, nunca consulta** (**`D8P-10`**): esta
    fronteira **não** consulta calendário, **não** escolhe provedor e **não**
    afirma verdade operacional própria.
    """

    status: str
    divergente: bool = False
    referentes_indisponiveis: tuple[str, ...] = ()
    assertivas_runtime: tuple[tuple[str, bool], ...] = ()


@dataclass(frozen=True, slots=True)
class ResultadoEmissibilidade:
    """O veredito de **`D8-F`** sobre um fragmento, e nada além disso.

    São **dois** desfechos, e **não existe um terceiro**: **zero impedimentos**
    é *emitível*; **um ou mais** é *não emitível*. **Não há emissão parcial**
    (**`D8-F6`**) e **não há resultado parcial**.
    """

    impedimentos: tuple[ImpedimentoEmissao, ...] = ()

    @property
    def emitivel(self) -> bool:
        """`True` **somente** quando nenhum impedimento foi coletado."""
        return not self.impedimentos


def avaliar_emissibilidade(
    fotografia: FotografiaFragmento,
) -> ResultadoEmissibilidade:
    """Aplica **`D8-F`** e **`D8-CII`** a **um** fragmento já candidato.

    A ordem é **fixa**: **`D8-F1`** (status) → **Classe II** → **`C-7`**, na
    ordem física recebida → **`ASSERTIVA` de runtime**.

    **Status não emitível faz curto-circuito**: ali o fragmento **sequer é
    aprovado**, e o veredito é **único** — divergência, `C-7` e runtime **não
    são avaliados**. Fora desse caso, **todas** as causas estruturais são
    coletadas (**`D8-E4`**): vários `ReferenteIndisponivel` produzem **um
    impedimento por referente**, e divergência somada a `C-7` produz **os
    dois**.

    `avaliar_assertiva` é **reutilizada**, sem avaliador ou predicado paralelo
    (**`D8P-10`**); `AssertivaNaoAvaliavel` **atravessa intacta**.

    **AVALIAR EMISSIBILIDADE NÃO É DECIDIR COBERTURA.** Quem escolhe o
    ***witness***, quem declara um grupo descoberto e quem produz causa é
    **S2-D8**.
    """
    if fotografia.status != _APROVADO:
        # D8-F1/D8-F4: `AGUARDA_APROVACAO` e `BLOQUEADO` nao habilitam, e o
        # veredito para aqui — nada mais e avaliado.
        return ResultadoEmissibilidade((ImpedimentoEmissao(),))

    impedimentos: list[ImpedimentoEmissao] = []

    if fotografia.divergente:
        # D8-CII: qualquer divergencia ja conferida bloqueia o fragmento. Nao
        # existe quarta condicao de D8-F aqui (R2F-12).
        impedimentos.append(ImpedimentoEmissao())

    for caminho in fotografia.referentes_indisponiveis:
        # D8-F2/D8-F3 pela via de `C-7`. O caminho e **transportado**, nunca
        # resolvido de novo nem reinterpretado.
        impedimentos.append(ImpedimentoEmissao(caminho))

    for predicado, valor in fotografia.assertivas_runtime:
        # D8-F3 sobre a fotografia recebida.
        if not avaliar_assertiva(predicado, valor):
            impedimentos.append(ImpedimentoEmissao())

    return ResultadoEmissibilidade(tuple(impedimentos))

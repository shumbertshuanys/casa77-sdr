"""Resumo determinístico de *handoff* — `docs/04-handoff-humano.md`.

Monta o texto entregue ao responsável comercial no formato de "Conteúdo do
resumo entregue", na ordem fixa dos onze rótulos. É **material interno**, nunca
mensagem ao interessado.

Decisões de M2 (ruling T5):

- **Pacote aplicável** aparece **somente** pelo `codigo` do pacote lido da base,
  ou "não determinado". **Nenhum valor de preço** é lido, copiado ou formatado
  aqui: o código não conhece `valor` nem `hora_adicional`.
- **Histórico** é a mensagem normalizada **do ciclo corrente**; a transcrição
  completa fica para depois do M2.
- **Perguntas em aberto** são as perguntas não respondidas do ciclo (`P5`).

**Saneamento.** Nome, contato, tipo, data, perguntas e mensagem vêm do
interessado (via LLM) e são preservados literalmente a montante. **Todo** valor
interpolado passa por `_sanear`: caractere de controle/formato (categoria
Unicode `C*`) e separador de linha/parágrafo (`Zl`/`Zp`) viram espaço, e
sequências de espaço colapsam — nenhum valor forja uma linha `Rótulo: valor`.
Dentro de um item de lista, o separador `;` vira `,`, para que nenhum item
forje outro.

Sem I/O, sem relógio, sem LLM, sem mutação de entrada.
"""

from __future__ import annotations

import unicodedata
from typing import Any

from casa77_sdr.pricing_applicability import AplicabilidadePacote
from casa77_sdr.qualification import DadosQualificacao, Qualificacao

__all__ = [
    "NAO_DETERMINADO",
    "NAO_INFORMADO",
    "codigo_pacote_aplicavel",
    "montar_resumo_handoff",
]

#: Rótulos fixos de `docs/04` para valor ausente.
NAO_INFORMADO = "não informado"
NAO_DETERMINADO = "não determinado"

_SEPARADOR_LISTA = "; "
_SEPARADOR_NEUTRO = ","


def codigo_pacote_aplicavel(
    aplicabilidade: AplicabilidadePacote, base: dict[str, Any]
) -> str | None:
    """O `codigo` do pacote da faixa decidida, ou `None` quando não há faixa.

    `FAIXA_INFERIOR` é o pacote de **menor** `limite_convidados`;
    `FAIXA_SUPERIOR`, o de **maior** — a mesma leitura estrutural de
    `pricing_applicability`, que já conferiu a forma da base ao decidir a faixa.
    """
    if aplicabilidade is AplicabilidadePacote.FAIXA_INFERIOR:
        return min(base["precos"]["pacotes"], key=_limite)["codigo"]
    if aplicabilidade is AplicabilidadePacote.FAIXA_SUPERIOR:
        return max(base["precos"]["pacotes"], key=_limite)["codigo"]
    return None


def montar_resumo_handoff(
    *,
    dados: DadosQualificacao,
    qualificacao: Qualificacao,
    codigo_pacote: str | None,
    motivos: tuple[str, ...],
    perguntas_em_aberto: tuple[str, ...],
    historico: str,
) -> str:
    """Monta o resumo, uma linha por rótulo de `docs/04`, unidas por `\\n`."""
    atendimento = dados.atendimento
    linhas = (
        ("Lead", _ou_nao_informado(dados.nome)),
        ("Contato", _ou_nao_informado(dados.contato)),
        ("Tipo de evento", _ou_nao_informado(atendimento.tipo_evento)),
        ("Data pretendida", _ou_nao_informado(atendimento.data_nomeada)),
        ("Convidados", _ou_nao_informado(atendimento.convidados)),
        ("Formato", _ou_nao_informado(None if dados.formato is None else dados.formato.value)),
        ("Pacote aplicável", NAO_DETERMINADO if codigo_pacote is None else _sanear(codigo_pacote)),
        ("Classificação", _sanear(qualificacao.resultado.value)),
        ("Motivo do handoff", _lista(motivos)),
        ("Perguntas em aberto", _lista(perguntas_em_aberto)),
        ("Histórico", _sanear(historico)),
    )
    return "\n".join(f"{rotulo}: {valor}" for rotulo, valor in linhas)


def _limite(pacote: dict[str, Any]) -> int:
    return pacote["limite_convidados"]


def _ou_nao_informado(valor: object) -> str:
    if valor is None:
        return NAO_INFORMADO
    return _sanear(str(valor)) or NAO_INFORMADO


def _lista(itens: tuple[str, ...]) -> str:
    """Itens saneados, sem o separador dentro de item algum, unidos por `; `."""
    saneados = (_sanear(item.replace(";", _SEPARADOR_NEUTRO)) for item in itens)
    return _SEPARADOR_LISTA.join(item for item in saneados if item) or NAO_INFORMADO


def _sanear(valor: str) -> str:
    """Uma linha só: controle/formato e separadores de linha viram espaço."""
    limpo = "".join(" " if _quebra_ou_controle(c) else c for c in valor)
    return " ".join(limpo.split())


def _quebra_ou_controle(caractere: str) -> bool:
    categoria = unicodedata.category(caractere)
    return categoria.startswith("C") or categoria in ("Zl", "Zp")

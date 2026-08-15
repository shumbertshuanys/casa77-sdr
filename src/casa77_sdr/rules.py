"""Regras comerciais determinísticas (3B.2).

Este módulo detecta exclusivamente as três violações objetivas de
`docs/02-fluxo-comercial.md` §6, comparando os dados do atendimento contra a
base carregada em tempo de execução:

1. tipo de evento nominalmente presente em `eventos.nao_aceitos`;
2. data nominal presente em `eventos.datas_nao_aceitas`;
3. convidados estritamente acima de `capacidade.formato_coquetel`.

Nenhum valor comercial existe neste módulo (invariante I06): listas e limites
vêm sempre da base carregada. Ausência de dado nunca gera violação (I09).
Lista vazia de violações significa somente que nenhuma das três violações
objetivas desta subetapa foi detectada — nunca que o evento é aceito,
compatível ou qualificado, nem que uma data está permitida ou disponível.
A classificação final pertence a componentes posteriores.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class MotivoViolacao(StrEnum):
    """Motivos enumerados das violações objetivas desta subetapa."""

    TIPO_NAO_ACEITO = "tipo_nao_aceito"
    DATA_NAO_ACEITA = "data_nao_aceita"
    CONVIDADOS_ACIMA_DA_CAPACIDADE = "convidados_acima_da_capacidade"


@dataclass(frozen=True)
class DadosAtendimento:
    """Dados do atendimento avaliados pelas regras desta subetapa.

    Todos os campos são opcionais: campo ausente significa apenas que a regra
    correspondente não é avaliada (I09). `data_nomeada` é o valor nominal
    estruturado já fornecido à camada de regras — este módulo não interpreta
    texto livre nem calcula calendário.
    """

    tipo_evento: str | None = None
    data_nomeada: str | None = None
    convidados: int | None = None


@dataclass(frozen=True)
class Violacao:
    """Uma violação objetiva, com motivo enumerado e campo de origem (I04).

    `valor_informado` preserva o valor exatamente como recebido no contrato,
    nunca a forma normalizada usada na comparação.
    """

    motivo: MotivoViolacao
    campo_yaml: str
    valor_informado: str | int


def _normalizar(texto: str) -> str:
    """Chave de igualdade nominal: somente caixa, espaços e acentos.

    Nada semântico acontece aqui — sinônimo, aproximação ou palavra-chave são
    papel da interpretação futura, nunca desta regra.
    """
    sem_acentos = "".join(
        caractere
        for caractere in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(caractere)
    )
    return " ".join(sem_acentos.casefold().split())


def _consta_na_lista(valor: str, itens: Any, campo: str) -> bool:
    """Igualdade nominal normalizada entre `valor` e os itens de `campo`.

    Tipo inesperado dentro da base é erro de programa, nunca comportamento
    comercial: a estrutura é garantida pelo carregador, e o conteúdo precisa
    ser string para a comparação nominal fazer sentido.
    """
    if not isinstance(itens, list):
        raise TypeError(f"Campo {campo} da base deve ser lista, e não {_nome_do_tipo(itens)}")
    chave = _normalizar(valor)
    for item in itens:
        if not isinstance(item, str):
            raise TypeError(f"Item de {campo} deve ser string, e não {_nome_do_tipo(item)}")
        if _normalizar(item) == chave:
            return True
    return False


def _nome_do_tipo(valor: Any) -> str:
    if valor is None:
        return "nulo"
    return type(valor).__name__


def avaliar_regras(dados: DadosAtendimento, base: dict[str, Any]) -> list[Violacao]:
    """Avalia as três regras objetivas contra a base carregada.

    Função pura: sem I/O, sem rede, sem mutação de `dados` ou de `base`.
    A saída tem ordem determinística — tipo, data, convidados — e no máximo
    uma violação por regra, independentemente de itens duplicados na base ou
    da ordem das chaves do YAML (I19).
    """
    violacoes: list[Violacao] = []

    if dados.tipo_evento is not None and _consta_na_lista(
        dados.tipo_evento, base["eventos"]["nao_aceitos"], "eventos.nao_aceitos"
    ):
        violacoes.append(
            Violacao(
                motivo=MotivoViolacao.TIPO_NAO_ACEITO,
                campo_yaml="eventos.nao_aceitos",
                valor_informado=dados.tipo_evento,
            )
        )

    if dados.data_nomeada is not None and _consta_na_lista(
        dados.data_nomeada, base["eventos"]["datas_nao_aceitas"], "eventos.datas_nao_aceitas"
    ):
        violacoes.append(
            Violacao(
                motivo=MotivoViolacao.DATA_NAO_ACEITA,
                campo_yaml="eventos.datas_nao_aceitas",
                valor_informado=dados.data_nomeada,
            )
        )

    if dados.convidados is not None:
        limite = base["capacidade"]["formato_coquetel"]
        if isinstance(limite, bool) or not isinstance(limite, int):
            raise TypeError(
                "Campo capacidade.formato_coquetel da base deve ser número inteiro, "
                f"e não {_nome_do_tipo(limite)}"
            )
        if dados.convidados > limite:
            violacoes.append(
                Violacao(
                    motivo=MotivoViolacao.CONVIDADOS_ACIMA_DA_CAPACIDADE,
                    campo_yaml="capacidade.formato_coquetel",
                    valor_informado=dados.convidados,
                )
            )

    return violacoes

"""Qualificador determinístico (3B.5).

Este módulo calcula `resultado_qualificacao` — o atributo do lead que responde
"o evento é compatível?" (doc 06 §1.2) — a partir de dados já estruturados, das
violações objetivas já calculadas pela 3B.2 e das pendências impeditivas já
classificadas por outra camada.

Ele **não** interpreta texto, **não** recalcula regras comerciais, **não**
detecta pendência na base, **não** escolhe pacote, **não** decide handoff e
**não** transiciona estado: classificação e transição são eixos separados
(doc 06 §1.2), e `qualificado_com_ressalva` é classificação determinística, não
a decisão humana que dela decorre.

Nenhum valor comercial existe aqui (I06): os limites de capacidade são lidos da
base recebida a cada chamada. Ausência de dado nunca produz `incompativel`
(I09); `incompativel` sempre carrega as violações com o campo do YAML de origem
(I04); `dados_incompletos` sempre carrega os campos ausentes (I05); e
`indefinido` sempre referencia os itens pendentes recebidos (I10).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from casa77_sdr.rules import DadosAtendimento, Violacao


class FormatoEvento(StrEnum):
    """Formato do evento, como vocabulário técnico fechado.

    Sem sinônimo e sem normalização semântica: converter "jantar sentado" em
    `SENTADO` é papel da interpretação futura, que deve entregar o dado já
    estruturado.
    """

    SENTADO = "sentado"
    COQUETEL = "coquetel"


class ResultadoQualificacao(StrEnum):
    """Os cinco resultados oficiais de `docs/02-fluxo-comercial.md` §6 (I07)."""

    DADOS_INCOMPLETOS = "dados_incompletos"
    QUALIFICADO = "qualificado"
    QUALIFICADO_COM_RESSALVA = "qualificado_com_ressalva"
    INCOMPATIVEL = "incompativel"
    INDEFINIDO = "indefinido"


class MotivoQualificacao(StrEnum):
    """Motivo técnico enumerado da decisão.

    É rastreabilidade para auditoria, não texto de conversa: nunca contém valor
    comercial, dado pessoal ou trecho da mensagem do interessado.
    """

    CAMPOS_OBRIGATORIOS_AUSENTES = "campos_obrigatorios_ausentes"
    VIOLACAO_OBJETIVA = "violacao_objetiva"
    PENDENCIA_IMPEDITIVA = "pendencia_impeditiva"
    FORMATO_SENTADO_ACIMA_CAPACIDADE_SENTADA = (
        "formato_sentado_acima_capacidade_sentada"
    )
    COMPATIVEL = "compativel"


@dataclass(frozen=True)
class DadosQualificacao:
    """Dados avaliados pela qualificação, por composição.

    `atendimento` continua sendo o contrato da 3B.2 e permanece a única origem
    de tipo, data e convidados — a composição existe justamente para não
    duplicar esses campos nem inflar `rules.py` com responsabilidade de
    qualificação.
    """

    atendimento: DadosAtendimento
    nome: str | None = None
    contato: str | None = None
    formato: FormatoEvento | None = None


@dataclass(frozen=True)
class Qualificacao:
    """Resultado da qualificação, com a evidência que o sustenta.

    `campos_ausentes` traz nomes técnicos de campo, nunca os valores;
    `violacoes` repassa integralmente os objetos recebidos, preservando o campo
    do YAML de origem; `pendencias_impeditivas` traz identificadores técnicos,
    nunca a pergunta bruta. Nome e contato do interessado não aparecem em
    nenhum desses campos.
    """

    resultado: ResultadoQualificacao
    motivo: MotivoQualificacao
    campos_ausentes: tuple[str, ...] = ()
    violacoes: tuple[Violacao, ...] = ()
    pendencias_impeditivas: tuple[str, ...] = ()


def qualificar(
    dados: DadosQualificacao,
    violacoes: tuple[Violacao, ...],
    pendencias_impeditivas: tuple[str, ...],
    base: dict[str, Any],
) -> Qualificacao:
    """Classifica o lead nos cinco resultados oficiais.

    Função pura: sem I/O, sem rede, sem relógio, sem persistência, sem LLM e
    sem mutação de `dados`, `violacoes`, `pendencias_impeditivas` ou `base`.

    O contrato inteiro é validado antes de qualquer classificação, para que
    defeito de programa nunca se disfarce de resultado comercial. Em seguida
    vale a precedência do doc 06 §4 e §5:

    1. violação objetiva → `incompativel` (nunca sobrescrita por dados
       completos, I20);
    2. campo obrigatório ausente → `dados_incompletos` (I09, doc 02 §6);
    3. dados completos com pendência impeditiva → `indefinido` (I10);
    4. faixa que exige formato, com formato sentado →
       `qualificado_com_ressalva`;
    5. demais casos completos e compatíveis → `qualificado`.

    A ordem dos passos 7 e 8 do doc 06 §4 descreve a sequência de verificações
    do ciclo, não uma precedência que faria `indefinido` prevalecer sobre falta
    de dado: `dados_incompletos` é o resultado inicial enquanto faltar campo
    obrigatório, e `indefinido` só cabe quando os dados necessários já existem
    e é a pendência da base que impede a classificação.
    """
    _validar_violacoes(violacoes)
    _validar_pendencias(pendencias_impeditivas)
    sentados, coquetel = _limites_de_capacidade(base)

    atendimento = dados.atendimento
    ausentes: list[str] = []
    if _texto_ausente(dados.nome, "nome"):
        ausentes.append("nome")
    if _texto_ausente(dados.contato, "contato"):
        ausentes.append("contato")
    if _texto_ausente(atendimento.tipo_evento, "tipo_evento"):
        ausentes.append("tipo_evento")
    if _texto_ausente(atendimento.data_nomeada, "data_nomeada"):
        ausentes.append("data_nomeada")
    convidados_ausente = _convidados_ausente(atendimento.convidados)
    if convidados_ausente:
        ausentes.append("convidados")
    _validar_formato(dados.formato)

    convidados = atendimento.convidados
    exige_formato = (
        not convidados_ausente
        and convidados is not None
        and sentados < convidados <= coquetel
    )
    if exige_formato and dados.formato is None:
        ausentes.append("formato")

    if not violacoes and convidados is not None and convidados > coquetel:
        # Integração incoerente: a 3B.2 sempre produz violação nesse caso, e
        # fabricar uma aqui — ou classificar sem ela — transformaria a ausência
        # da saída obrigatória em falso positivo comercial.
        raise ValueError(
            "Incoerência entre os dados recebidos e as violações informadas: "
            "convidados acima do limite de capacidade sem violação correspondente"
        )

    if violacoes:
        return Qualificacao(
            resultado=ResultadoQualificacao.INCOMPATIVEL,
            motivo=MotivoQualificacao.VIOLACAO_OBJETIVA,
            violacoes=violacoes,
        )

    if ausentes:
        return Qualificacao(
            resultado=ResultadoQualificacao.DADOS_INCOMPLETOS,
            motivo=MotivoQualificacao.CAMPOS_OBRIGATORIOS_AUSENTES,
            campos_ausentes=tuple(ausentes),
        )

    if pendencias_impeditivas:
        return Qualificacao(
            resultado=ResultadoQualificacao.INDEFINIDO,
            motivo=MotivoQualificacao.PENDENCIA_IMPEDITIVA,
            pendencias_impeditivas=pendencias_impeditivas,
        )

    if exige_formato and dados.formato is FormatoEvento.SENTADO:
        return Qualificacao(
            resultado=ResultadoQualificacao.QUALIFICADO_COM_RESSALVA,
            motivo=MotivoQualificacao.FORMATO_SENTADO_ACIMA_CAPACIDADE_SENTADA,
        )

    return Qualificacao(
        resultado=ResultadoQualificacao.QUALIFICADO,
        motivo=MotivoQualificacao.COMPATIVEL,
    )


def _texto_ausente(valor: Any, campo: str) -> bool:
    """Distingue ausência de invalidade em campo textual.

    `None` e texto em branco são ausência — condição normal de coleta. Valor de
    outro tipo é defeito de contrato de quem montou os dados.
    """
    if valor is None:
        return True
    if not isinstance(valor, str):
        raise TypeError(f"O campo '{campo}' deve ser texto quando informado")
    return not valor.strip()


def _convidados_ausente(valor: Any) -> bool:
    """Ausência, invalidade e negativo em `convidados`.

    Não existe mínimo aprovado de convidados: zero é valor válido e não é
    recusado por regra comercial inventada aqui.
    """
    if valor is None:
        return True
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise TypeError("O campo 'convidados' deve ser número inteiro quando informado")
    if valor < 0:
        raise ValueError("O campo 'convidados' não pode ser negativo")
    return False


def _validar_formato(valor: Any) -> None:
    """Exige o vocabulário fechado; string livre não é convertida."""
    if valor is not None and not isinstance(valor, FormatoEvento):
        raise TypeError("O campo 'formato' deve ser um FormatoEvento quando informado")


def _validar_violacoes(violacoes: Any) -> None:
    if not isinstance(violacoes, tuple):
        raise TypeError("As violações devem ser uma tupla")
    for item in violacoes:
        if not isinstance(item, Violacao):
            raise TypeError("Cada violação recebida deve ser uma Violacao")


def _validar_pendencias(pendencias: Any) -> None:
    """Identificadores técnicos opacos: não são interpretados nem normalizados."""
    if not isinstance(pendencias, tuple):
        raise TypeError("As pendências impeditivas devem ser uma tupla")
    for item in pendencias:
        if not isinstance(item, str):
            raise TypeError("Cada pendência impeditiva deve ser um identificador textual")
        if not item.strip():
            raise ValueError("Pendência impeditiva não pode ser um identificador vazio")


def _limites_de_capacidade(base: Any) -> tuple[int, int]:
    """Lê os dois limites de capacidade da base recebida.

    O carregador continua sendo o validador primário da base; esta conferência
    existe para que uma base malformada falhe como erro de programa, e nunca
    como classificação comercial silenciosa.
    """
    if not isinstance(base, dict):
        raise TypeError("A base deve ser um mapeamento")

    capacidade = base.get("capacidade")
    if capacidade is None:
        raise ValueError("Campo obrigatório ausente na base: capacidade")
    if not isinstance(capacidade, dict):
        raise TypeError("O campo capacidade da base deve ser um mapeamento")

    sentados = _limite_inteiro(capacidade, "convidados_sentados")
    coquetel = _limite_inteiro(capacidade, "formato_coquetel")
    if sentados > coquetel:
        raise ValueError(
            "Faixas de capacidade incoerentes na base: "
            "capacidade.convidados_sentados acima de capacidade.formato_coquetel"
        )
    return sentados, coquetel


def _limite_inteiro(capacidade: dict[str, Any], campo: str) -> int:
    if campo not in capacidade:
        raise ValueError(f"Campo obrigatório ausente na base: capacidade.{campo}")
    valor = capacidade[campo]
    # `bool` é subclasse de `int` em Python e não serve como limite aqui.
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise TypeError(
            f"O campo capacidade.{campo} da base deve ser número inteiro"
        )
    return valor

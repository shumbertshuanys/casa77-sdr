"""Testes das regras comerciais determinísticas (3B.2).

Fixtures usam valores artificiais, claramente fictícios e sem relação com a
operação real. Quando o YAML real é usado, o valor comercial é lido
dinamicamente do arquivo carregado — nunca copiado como constante do teste.

Nome e docstring dos casos de não-correspondência expressam somente que a
regra objetiva não encontrou correspondência na lista nominal carregada —
nunca que o evento é aceito, compatível ou que a data é permitida.
"""

from __future__ import annotations

import ast
import copy
from pathlib import Path
from typing import Any

from casa77_sdr.knowledge import load_knowledge
from casa77_sdr.rules import (
    DadosAtendimento,
    MotivoViolacao,
    Violacao,
    avaliar_regras,
)

RAIZ = Path(__file__).resolve().parents[1]
YAML_REAL = RAIZ / "knowledge" / "casa77.yaml"
MODULO_REGRAS = RAIZ / "src" / "casa77_sdr" / "rules.py"


def base_ficticia() -> dict[str, Any]:
    """Base mínima com valores artificiais, não comerciais."""
    return {
        "eventos": {
            "aceitos": ["tipo-comum"],
            "nao_aceitos": ["tipo proibido", "cerimônia vetada"],
            "datas_nao_aceitas": ["data bloqueada", "véspera fictícia"],
        },
        "capacidade": {"convidados_sentados": 7, "formato_coquetel": 9},
    }


# 1. Tipo bloqueado — fixture artificial


def test_tipo_bloqueado_na_fixture() -> None:
    violacoes = avaliar_regras(
        DadosAtendimento(tipo_evento="tipo proibido"), base_ficticia()
    )

    assert violacoes == [
        Violacao(
            motivo=MotivoViolacao.TIPO_NAO_ACEITO,
            campo_yaml="eventos.nao_aceitos",
            valor_informado="tipo proibido",
        )
    ]


# 2. Tipo bloqueado — valor lido dinamicamente do YAML real


def test_tipo_bloqueado_lido_dinamicamente_do_yaml_real() -> None:
    base = load_knowledge(YAML_REAL)
    tipo_real = base["eventos"]["nao_aceitos"][0]

    violacoes = avaliar_regras(DadosAtendimento(tipo_evento=tipo_real), base)

    assert [v.motivo for v in violacoes] == [MotivoViolacao.TIPO_NAO_ACEITO]
    assert violacoes[0].campo_yaml == "eventos.nao_aceitos"
    assert violacoes[0].valor_informado == tipo_real


# 3. Tipo sem correspondência na lista carregada


def test_tipo_sem_correspondencia_na_lista_gera_zero_violacao() -> None:
    """Zero violação significa só ausência de correspondência nominal."""
    violacoes = avaliar_regras(
        DadosAtendimento(tipo_evento="tipo ausente da lista"), base_ficticia()
    )

    assert violacoes == []


# 4–6. Normalização textual (caixa, espaços, acentos)


def test_normalizacao_de_caixa() -> None:
    violacoes = avaliar_regras(
        DadosAtendimento(tipo_evento="TIPO Proibido"), base_ficticia()
    )

    assert [v.motivo for v in violacoes] == [MotivoViolacao.TIPO_NAO_ACEITO]


def test_normalizacao_de_espacos() -> None:
    violacoes = avaliar_regras(
        DadosAtendimento(tipo_evento="  tipo   proibido  "), base_ficticia()
    )

    assert [v.motivo for v in violacoes] == [MotivoViolacao.TIPO_NAO_ACEITO]


def test_normalizacao_de_acentos() -> None:
    """"cerimonia vetada" sem acento corresponde a "cerimônia vetada"."""
    violacoes = avaliar_regras(
        DadosAtendimento(tipo_evento="cerimonia vetada"), base_ficticia()
    )

    assert [v.motivo for v in violacoes] == [MotivoViolacao.TIPO_NAO_ACEITO]


def test_termo_parecido_mas_nao_igual_nao_corresponde() -> None:
    """Igualdade nominal estrita: substring não corresponde."""
    violacoes = avaliar_regras(
        DadosAtendimento(tipo_evento="proibido"), base_ficticia()
    )

    assert violacoes == []


# 7. Data nominal bloqueada — fixture


def test_data_nominal_bloqueada_na_fixture() -> None:
    violacoes = avaliar_regras(
        DadosAtendimento(data_nomeada="data bloqueada"), base_ficticia()
    )

    assert violacoes == [
        Violacao(
            motivo=MotivoViolacao.DATA_NAO_ACEITA,
            campo_yaml="eventos.datas_nao_aceitas",
            valor_informado="data bloqueada",
        )
    ]


# 8. Data nominal bloqueada — valor lido dinamicamente do YAML real


def test_data_nominal_bloqueada_lida_dinamicamente_do_yaml_real() -> None:
    base = load_knowledge(YAML_REAL)
    data_real = base["eventos"]["datas_nao_aceitas"][0]

    violacoes = avaliar_regras(DadosAtendimento(data_nomeada=data_real), base)

    assert [v.motivo for v in violacoes] == [MotivoViolacao.DATA_NAO_ACEITA]
    assert violacoes[0].campo_yaml == "eventos.datas_nao_aceitas"
    assert violacoes[0].valor_informado == data_real


# 9. Data nominal sem correspondência na lista carregada


def test_data_nominal_sem_correspondencia_gera_zero_violacao() -> None:
    """Zero violação não afirma data permitida nem disponível."""
    violacoes = avaliar_regras(
        DadosAtendimento(data_nomeada="data ausente da lista"), base_ficticia()
    )

    assert violacoes == []


# 10–11. Convidados no limite e acima do limite, lidos em tempo de teste


def test_convidados_exatamente_no_limite_lido_gera_zero_violacao() -> None:
    base = base_ficticia()
    limite = base["capacidade"]["formato_coquetel"]

    assert avaliar_regras(DadosAtendimento(convidados=limite), base) == []


def test_convidados_acima_do_limite_lido_gera_violacao() -> None:
    base = base_ficticia()
    limite = base["capacidade"]["formato_coquetel"]

    violacoes = avaliar_regras(DadosAtendimento(convidados=limite + 1), base)

    assert violacoes == [
        Violacao(
            motivo=MotivoViolacao.CONVIDADOS_ACIMA_DA_CAPACIDADE,
            campo_yaml="capacidade.formato_coquetel",
            valor_informado=limite + 1,
        )
    ]


def test_convidados_acima_do_limite_do_yaml_real_lido_dinamicamente() -> None:
    base = load_knowledge(YAML_REAL)
    limite = base["capacidade"]["formato_coquetel"]

    violacoes = avaliar_regras(DadosAtendimento(convidados=limite + 1), base)

    assert [v.motivo for v in violacoes] == [
        MotivoViolacao.CONVIDADOS_ACIMA_DA_CAPACIDADE
    ]


# 12–13. Ausência de dado nunca é violação (I09)


def test_todos_os_campos_none_gera_zero_violacoes() -> None:
    assert avaliar_regras(DadosAtendimento(), base_ficticia()) == []


def test_ausencia_parcial_avalia_somente_a_regra_do_dado_presente() -> None:
    base = base_ficticia()
    limite = base["capacidade"]["formato_coquetel"]

    violacoes = avaliar_regras(DadosAtendimento(convidados=limite + 1), base)

    assert [v.motivo for v in violacoes] == [
        MotivoViolacao.CONVIDADOS_ACIMA_DA_CAPACIDADE
    ]


# 14–15. Múltiplas violações e ordem determinística


def test_multiplas_violacoes() -> None:
    base = base_ficticia()
    limite = base["capacidade"]["formato_coquetel"]

    violacoes = avaliar_regras(
        DadosAtendimento(tipo_evento="tipo proibido", convidados=limite + 1),
        base,
    )

    assert [v.motivo for v in violacoes] == [
        MotivoViolacao.TIPO_NAO_ACEITO,
        MotivoViolacao.CONVIDADOS_ACIMA_DA_CAPACIDADE,
    ]
    assert all(v.campo_yaml and v.motivo for v in violacoes)


def test_ordem_deterministica_tipo_data_convidados() -> None:
    base = base_ficticia()
    limite = base["capacidade"]["formato_coquetel"]

    violacoes = avaliar_regras(
        DadosAtendimento(
            tipo_evento="tipo proibido",
            data_nomeada="data bloqueada",
            convidados=limite + 1,
        ),
        base,
    )

    assert [v.motivo for v in violacoes] == [
        MotivoViolacao.TIPO_NAO_ACEITO,
        MotivoViolacao.DATA_NAO_ACEITA,
        MotivoViolacao.CONVIDADOS_ACIMA_DA_CAPACIDADE,
    ]


# 16. A base carregada não é mutada


def test_base_nao_mutada() -> None:
    base = base_ficticia()
    antes = copy.deepcopy(base)

    avaliar_regras(
        DadosAtendimento(
            tipo_evento="tipo proibido",
            data_nomeada="data bloqueada",
            convidados=base["capacidade"]["formato_coquetel"] + 1,
        ),
        base,
    )

    assert base == antes


# 17. valor_informado preserva o valor original recebido


def test_valor_informado_preserva_valor_original() -> None:
    violacoes = avaliar_regras(
        DadosAtendimento(tipo_evento="  TIPO Proibido "), base_ficticia()
    )

    assert violacoes[0].valor_informado == "  TIPO Proibido "


# 18. Itens duplicados na lista da base não duplicam a violação


def test_itens_duplicados_na_lista_nao_duplicam_violacao() -> None:
    base = base_ficticia()
    base["eventos"]["nao_aceitos"] = ["tipo repetido", "tipo repetido"]

    violacoes = avaliar_regras(
        DadosAtendimento(tipo_evento="tipo repetido"), base
    )

    assert len(violacoes) == 1


# 19. Zero hardcode comercial em rules.py (invariante I06)


def test_regras_nao_tem_constante_comercial() -> None:
    """Nenhum valor comercial do YAML real existe como literal no módulo.

    Nomes de campos do schema, valores do enum técnico de motivos e textos
    técnicos internos não são valores comerciais e permanecem permitidos.
    """
    base = load_knowledge(YAML_REAL)

    inteiros_comerciais = {
        base["capacidade"]["convidados_sentados"],
        base["capacidade"]["formato_coquetel"],
    }
    for pacote in base["precos"]["pacotes"]:
        inteiros_comerciais.update(
            valor
            for valor in pacote.values()
            if isinstance(valor, int) and not isinstance(valor, bool)
        )

    textos_comerciais = {
        texto.casefold()
        for texto in (
            list(base["eventos"]["aceitos"])
            + list(base["eventos"]["nao_aceitos"])
            + list(base["eventos"]["datas_nao_aceitas"])
        )
    }

    arvore = ast.parse(MODULO_REGRAS.read_text(encoding="utf-8"))
    literais_int = set()
    literais_str = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Constant):
            if isinstance(no.value, bool):
                continue
            if isinstance(no.value, int):
                literais_int.add(no.value)
            elif isinstance(no.value, str):
                literais_str.add(no.value.casefold())

    assert not (literais_int & inteiros_comerciais)
    assert not (literais_str & textos_comerciais)


# 20. Nenhum import de LLM, rede ou calendário em rules.py


def test_regras_sem_import_de_llm_rede_ou_calendario() -> None:
    permitidos = {"__future__", "unicodedata", "dataclasses", "enum", "typing"}
    proibidos = {
        "datetime",
        "calendar",
        "time",
        "zoneinfo",
        "http",
        "urllib",
        "socket",
        "requests",
        "anthropic",
        "openai",
    }

    arvore = ast.parse(MODULO_REGRAS.read_text(encoding="utf-8"))
    importados = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            importados.update(alias.name.split(".")[0] for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            importados.add(no.module.split(".")[0])

    assert importados <= permitidos
    assert not (importados & proibidos)

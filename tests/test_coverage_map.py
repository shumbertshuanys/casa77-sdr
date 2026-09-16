"""Testes da validação estrutural do mapa de grupos de cobertura — `R2`.

Todo mapa usado aqui é **sintético**: os `Rxx`, os fragmentos e os agrupamentos
são inventados para exercitar a **forma**, e **nenhum deles é o mapeamento
aprovado**. Nenhum teste escreve em `knowledge/**` e nenhum valor comercial
aparece como conteúdo ou como expectativa. O **conteúdo real** do mapa é
auditado em `tests/test_mapa_cobertura_corpus.py`, e não aqui.

Os `AssuntoComercial` empregados são membros reais do enum de **AJ2** porque o
vocabulário é reutilizado, nunca duplicado — mas a **associação** entre um
assunto e um `Rxx`/`Fxx` é **conteúdo aprovado**, decidido fora destes testes.

A prova de que a fronteira não conhece LLM, rede, relógio, `filesystem` e
conteúdo de mapa é feita sobre a **AST do módulo de produção**, seguindo o
precedente de `test_response_index.py`.
"""

from __future__ import annotations

import ast
import copy
from pathlib import Path
from typing import Any

import pytest

from casa77_sdr.coverage_map import (
    MapaCoberturaInvalido,
    conferir_referencias,
    validar_mapa_cobertura,
)
from casa77_sdr.interpretation import AssuntoComercial
from casa77_sdr.response_index_tokens import ProjecaoDeIdentidadeInvalida

RAIZ = Path(__file__).resolve().parents[1]
MODULO = RAIZ / "src" / "casa77_sdr" / "coverage_map.py"
MODULO_INIT = RAIZ / "src" / "casa77_sdr" / "__init__.py"

PRECO = AssuntoComercial.PRECO_LOCACAO.value
NAO_CLASSIFICADO = AssuntoComercial.ASSUNTO_NAO_CLASSIFICADO.value


# Fixtures sinteticos — nenhum deles e mapa aprovado.


def alternativa(rxx: str = "R09", fragmento: str = "F1") -> dict[str, Any]:
    return {"rxx": rxx, "fragmento": fragmento}


def grupo(*alternativas: dict[str, Any]) -> dict[str, Any]:
    return {"alternativas": list(alternativas) or [alternativa()]}


def assunto(
    nome: str = PRECO, *grupos: dict[str, Any]
) -> dict[str, Any]:
    return {"assunto": nome, "grupos": list(grupos)}


def mapa(*assuntos: dict[str, Any]) -> dict[str, Any]:
    """Mapa **cru**, possivelmente parcial — usado para exercitar recusas."""
    return {"assuntos": list(assuntos)}


VALORES_CANONICOS = [membro.value for membro in AssuntoComercial]
POSICAO_NAO_CLASSIFICADO = VALORES_CANONICOS.index(NAO_CLASSIFICADO)


def total(*itens: dict[str, Any]) -> dict[str, Any]:
    """Mapa **total**: os 54 assuntos, na ordem canônica, com zero grupos.

    Os itens declarados substituem o seu homônimo. É a forma mínima válida — e
    **semanticamente vazia**: nenhuma associação real de cobertura existe aqui.
    """
    declarados = {item["assunto"]: item for item in itens}
    return {
        "assuntos": [
            declarados.get(valor, assunto(valor)) for valor in VALORES_CANONICOS
        ]
    }


def total_sem(ausente: str) -> dict[str, Any]:
    """Mapa total **menos um** assunto — inválido pela totalidade."""
    return {
        "assuntos": [
            assunto(valor) for valor in VALORES_CANONICOS if valor != ausente
        ]
    }


def indice(*pares: tuple[str, tuple[str, ...]]) -> dict[str, Any]:
    """Índice **sintético** reduzido à projeção de identidade que o domínio usa."""
    return {
        "respostas": [
            {
                "id": rxx,
                "fragmentos": [{"id": fid} for fid in fragmentos],
            }
            for rxx, fragmentos in pares
        ]
    }


INDICE_PADRAO = indice(("R09", ("F1", "F2")), ("R14", ("F1",)))


def categoria_de(erro: pytest.ExceptionInfo[MapaCoberturaInvalido]) -> str:
    return str(erro.value).split(":", 1)[0]


def localizador_de(erro: pytest.ExceptionInfo[MapaCoberturaInvalido]) -> str:
    return str(erro.value).split(": ", 1)[1]


# 1. Raiz


def test_mapa_total_minimo_e_valido() -> None:
    """Os 54 assuntos, todos com `grupos: []`: válido e semanticamente vazio."""
    assert validar_mapa_cobertura(total()) is None


def test_raiz_valida_completa() -> None:
    estrutura = total(assunto(PRECO, grupo(alternativa("R09", "F1"))))

    assert validar_mapa_cobertura(estrutura) is None


@pytest.mark.parametrize(
    "raiz", [None, [], "assuntos", 0, 1.5, True, (), set(), object()]
)
def test_raiz_nao_mapeamento(raiz: object) -> None:
    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura(raiz)

    assert str(erro.value) == "tipo_invalido: <raiz>"


def test_raiz_sem_assuntos() -> None:
    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura({})

    assert str(erro.value) == "campo_ausente: <raiz>"


def test_raiz_com_chave_desconhecida() -> None:
    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura({"assuntos": [], "versao": 1})

    assert str(erro.value) == "campo_desconhecido: <raiz>"


@pytest.mark.parametrize("valor", [None, {}, "x", 0, ()])
def test_assuntos_nao_lista(valor: object) -> None:
    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura({"assuntos": valor})

    assert str(erro.value) == "tipo_invalido: assuntos"


# 2. Item de assunto


@pytest.mark.parametrize("item", [None, [], "preco_locacao", 0])
def test_item_de_assunto_nao_mapeamento(item: object) -> None:
    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura({"assuntos": [item]})

    assert str(erro.value) == "tipo_invalido: assuntos[0]"


def test_item_de_assunto_sem_grupos_e_campo_ausente() -> None:
    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura({"assuntos": [{"assunto": PRECO}]})

    assert str(erro.value) == "campo_ausente: assuntos[0]"


def test_item_de_assunto_sem_assunto_e_campo_ausente() -> None:
    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura({"assuntos": [{"grupos": []}]})

    assert str(erro.value) == "campo_ausente: assuntos[0]"


@pytest.mark.parametrize("extra", ["priority", "texto", "status", "rxx"])
def test_item_de_assunto_com_campo_extra(extra: str) -> None:
    item = assunto(PRECO)
    item[extra] = "x"

    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura({"assuntos": [item]})

    assert str(erro.value) == "campo_desconhecido: assuntos[0]"


@pytest.mark.parametrize("valor", [None, 0, [], {}, True])
def test_assunto_de_tipo_invalido(valor: object) -> None:
    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura({"assuntos": [{"assunto": valor, "grupos": []}]})

    assert str(erro.value) == "tipo_invalido: assuntos[0].assunto"


def test_membro_do_enum_nao_e_forma_fisica_do_assunto() -> None:
    """`StrEnum` é subclasse de `str`: a forma física do mapa é texto puro."""
    item = {"assunto": AssuntoComercial.PRECO_LOCACAO, "grupos": []}

    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura({"assuntos": [item]})

    assert str(erro.value) == "tipo_invalido: assuntos[0].assunto"


@pytest.mark.parametrize(
    "valor",
    ["", "PRECO_LOCACAO", "preco", "preco_locacao ", "assunto_inexistente"],
)
def test_assunto_fora_do_vocabulario(valor: str) -> None:
    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura({"assuntos": [{"assunto": valor, "grupos": []}]})

    assert str(erro.value) == "valor_invalido: assuntos[0].assunto"


def test_todos_os_54_assuntos_sao_aceitos() -> None:
    estrutura = mapa(*(assunto(membro.value) for membro in AssuntoComercial))

    assert validar_mapa_cobertura(estrutura) is None


def test_assunto_duplicado_e_recusado() -> None:
    """R2-1 fala de **um** mapeamento por assunto."""
    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura(mapa(assunto(PRECO), assunto(PRECO)))

    assert str(erro.value) == "duplicidade: assuntos[1].assunto"


@pytest.mark.parametrize("valor", [None, {}, "x", 0])
def test_grupos_nao_lista(valor: object) -> None:
    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura({"assuntos": [{"assunto": PRECO, "grupos": valor}]})

    assert str(erro.value) == "tipo_invalido: assuntos[0].grupos"


# 3. R2-1 — totalidade do vocabulario, e zero grupos declarado explicitamente


def test_assunto_com_zero_grupos_declarado_e_valido() -> None:
    estrutura = total()

    assert validar_mapa_cobertura(estrutura) is None
    assert estrutura["assuntos"][0]["grupos"] == []


def test_mapa_vazio_e_invalido() -> None:
    """Ausência deixou de ser silêncio aceitável: a declaração é obrigatória."""
    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura(mapa())

    assert str(erro.value) == "campo_ausente: assuntos.item"


def test_mapa_com_53_dos_54_assuntos_e_invalido() -> None:
    estrutura = total_sem(PRECO)

    assert len(estrutura["assuntos"]) == 53
    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura(estrutura)

    assert str(erro.value) == "campo_ausente: assuntos.item"


@pytest.mark.parametrize("ausente", VALORES_CANONICOS)
def test_qualquer_assunto_ausente_invalida(ausente: str) -> None:
    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura(total_sem(ausente))

    assert categoria_de(erro) == "campo_ausente"


def test_mensagem_da_totalidade_nao_diz_qual_assunto_falta() -> None:
    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura(total_sem(PRECO))

    assert PRECO not in str(erro.value)


def test_ordem_dos_assuntos_nao_e_julgada() -> None:
    estrutura = {"assuntos": [assunto(valor) for valor in VALORES_CANONICOS[::-1]]}

    assert validar_mapa_cobertura(estrutura) is None


def test_assunto_com_varios_grupos_e_valido() -> None:
    estrutura = total(
        assunto(PRECO, grupo(alternativa("R09", "F1")), grupo(alternativa("R14", "F1")))
    )

    assert validar_mapa_cobertura(estrutura) is None


# 4. R2-6 — ASSUNTO_NAO_CLASSIFICADO


def test_assunto_nao_classificado_presente_com_zero_grupos_e_valido() -> None:
    estrutura = total()

    assert validar_mapa_cobertura(estrutura) is None
    assert estrutura["assuntos"][POSICAO_NAO_CLASSIFICADO] == {
        "assunto": NAO_CLASSIFICADO,
        "grupos": [],
    }


def test_assunto_nao_classificado_com_grupo_e_recusado() -> None:
    estrutura = total(
        assunto(NAO_CLASSIFICADO, grupo(alternativa("R09", "F1")))
    )

    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura(estrutura)

    assert str(erro.value) == (
        f"combinacao_invalida: assuntos[{POSICAO_NAO_CLASSIFICADO}].grupos"
    )


def test_assunto_nao_classificado_ausente_e_invalido_pela_totalidade() -> None:
    """R2-6 exige que ele exista, declarado, com zero grupos."""
    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura(total_sem(NAO_CLASSIFICADO))

    assert str(erro.value) == "campo_ausente: assuntos.item"


# 5. Grupo


@pytest.mark.parametrize("valor", [None, [], "x", 0])
def test_grupo_nao_mapeamento(valor: object) -> None:
    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura({"assuntos": [{"assunto": PRECO, "grupos": [valor]}]})

    assert str(erro.value) == "tipo_invalido: assuntos[0].grupos[0]"


def test_grupo_sem_alternativas_e_campo_ausente() -> None:
    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura({"assuntos": [{"assunto": PRECO, "grupos": [{}]}]})

    assert str(erro.value) == "campo_ausente: assuntos[0].grupos[0]"


@pytest.mark.parametrize("extra", ["priority", "assunto", "rxx", "peso"])
def test_grupo_com_campo_extra(extra: str) -> None:
    corpo = grupo(alternativa("R09", "F1"))
    corpo[extra] = 1

    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura(mapa(assunto(PRECO, corpo)))

    assert str(erro.value) == "campo_desconhecido: assuntos[0].grupos[0]"


@pytest.mark.parametrize("valor", [None, {}, "x", 0])
def test_alternativas_nao_lista(valor: object) -> None:
    estrutura = mapa(assunto(PRECO, {"alternativas": valor}))

    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura(estrutura)

    assert str(erro.value) == "tipo_invalido: assuntos[0].grupos[0].alternativas"


def test_grupo_com_zero_alternativas_e_recusado() -> None:
    """R2-2: o grupo tem 1..N alternativas."""
    estrutura = mapa(assunto(PRECO, {"alternativas": []}))

    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura(estrutura)

    assert str(erro.value) == "valor_invalido: assuntos[0].grupos[0].alternativas"


def test_grupo_com_varias_alternativas_e_valido() -> None:
    estrutura = total(
        assunto(
            PRECO,
            grupo(alternativa("R09", "F1"), alternativa("R09", "F2")),
        )
    )

    assert validar_mapa_cobertura(estrutura) is None


# 6. Alternativa


@pytest.mark.parametrize("valor", [None, [], "R09/F1", 0])
def test_alternativa_nao_mapeamento(valor: object) -> None:
    estrutura = mapa(assunto(PRECO, {"alternativas": [valor]}))

    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura(estrutura)

    assert str(erro.value) == "tipo_invalido: assuntos[0].grupos[0].alternativas[0]"


def test_alternativa_aceita_somente_rxx_e_fragmento() -> None:
    estrutura = total(assunto(PRECO, grupo({"rxx": "R09", "fragmento": "F1"})))

    assert validar_mapa_cobertura(estrutura) is None


@pytest.mark.parametrize(
    "parcial", [{"rxx": "R09"}, {"fragmento": "F1"}, {}]
)
def test_alternativa_incompleta(parcial: dict[str, Any]) -> None:
    estrutura = mapa(assunto(PRECO, {"alternativas": [parcial]}))

    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura(estrutura)

    assert str(erro.value) == "campo_ausente: assuntos[0].grupos[0].alternativas[0]"


@pytest.mark.parametrize(
    "extra",
    [
        "priority",
        "texto",
        "status",
        "binding",
        "caminho_yaml",
        "predicado",
        "formato",
        "valor",
    ],
)
def test_alternativa_com_campo_extra_e_recusada(extra: str) -> None:
    """R2-3: o mapa referencia; ele não copia o que vive no índice ou no YAML."""
    corpo = alternativa("R09", "F1")
    corpo[extra] = "x"

    estrutura = mapa(assunto(PRECO, {"alternativas": [corpo]}))

    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura(estrutura)

    assert str(erro.value) == (
        "campo_desconhecido: assuntos[0].grupos[0].alternativas[0]"
    )


@pytest.mark.parametrize("campo", ["rxx", "fragmento"])
@pytest.mark.parametrize("valor", [None, 0, [], {}, True])
def test_componente_de_tipo_invalido(campo: str, valor: object) -> None:
    corpo = alternativa("R09", "F1")
    corpo[campo] = valor

    estrutura = mapa(assunto(PRECO, {"alternativas": [corpo]}))

    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura(estrutura)

    assert str(erro.value) == (
        f"tipo_invalido: assuntos[0].grupos[0].alternativas[0].{campo}"
    )


@pytest.mark.parametrize("campo", ["rxx", "fragmento"])
@pytest.mark.parametrize("valor", ["", "R09/F1", "a/b"])
def test_componente_vazio_ou_com_separador(campo: str, valor: str) -> None:
    corpo = alternativa("R09", "F1")
    corpo[campo] = valor

    estrutura = mapa(assunto(PRECO, {"alternativas": [corpo]}))

    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura(estrutura)

    assert str(erro.value) == (
        f"valor_invalido: assuntos[0].grupos[0].alternativas[0].{campo}"
    )


def test_subclasse_de_str_nao_e_componente_valido() -> None:
    class Identificador(str):
        pass

    corpo = {"rxx": Identificador("R09"), "fragmento": "F1"}
    estrutura = mapa(assunto(PRECO, {"alternativas": [corpo]}))

    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura(estrutura)

    assert categoria_de(erro) == "tipo_invalido"


# 7. Fragmento de lacuna nao e alternativa


def test_r03_f1_recusado_como_alternativa() -> None:
    estrutura = mapa(assunto(PRECO, grupo(alternativa("R03", "F1"))))

    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura(estrutura)

    assert str(erro.value) == (
        "combinacao_invalida: assuntos[0].grupos[0].alternativas[0]"
    )


def test_r03_f1_recusado_mesmo_acompanhado() -> None:
    estrutura = mapa(
        assunto(PRECO, grupo(alternativa("R09", "F1"), alternativa("R03", "F1")))
    )

    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura(estrutura)

    assert localizador_de(erro).endswith("alternativas[1]")


@pytest.mark.parametrize(
    "corpo", [("R03", "F2"), ("R30", "F1"), ("R031", "F1")]
)
def test_apenas_r03_f1_e_proibido(corpo: tuple[str, str]) -> None:
    estrutura = total(assunto(PRECO, grupo(alternativa(*corpo))))

    assert validar_mapa_cobertura(estrutura) is None


# 8. Duplicidade NAO antecipada (SF-D4-9 pertence a jusante)


def test_alternativa_repetida_no_mesmo_grupo_e_aceita() -> None:
    estrutura = total(
        assunto(PRECO, grupo(alternativa("R09", "F1"), alternativa("R09", "F1")))
    )

    assert validar_mapa_cobertura(estrutura) is None


def test_mesma_alternativa_em_grupos_distintos_e_aceita() -> None:
    estrutura = total(
        assunto(PRECO, grupo(alternativa("R09", "F1")), grupo(alternativa("R09", "F1")))
    )

    assert validar_mapa_cobertura(estrutura) is None


def test_mesma_alternativa_em_assuntos_distintos_e_aceita() -> None:
    estrutura = total(
        assunto(PRECO, grupo(alternativa("R09", "F1"))),
        assunto(
            AssuntoComercial.CAPACIDADE_MAXIMA_E_FORMATO.value,
            grupo(alternativa("R09", "F1")),
        ),
    )

    assert validar_mapa_cobertura(estrutura) is None


# 9. Ordem preservada e zero mutacao


def test_validacao_nao_altera_a_estrutura() -> None:
    estrutura = total(
        assunto(
            PRECO,
            grupo(alternativa("R14", "F1"), alternativa("R09", "F2")),
            grupo(alternativa("R09", "F1")),
        ),
    )
    antes = copy.deepcopy(estrutura)

    validar_mapa_cobertura(estrutura)

    assert estrutura == antes


def test_conferencia_nao_altera_estrutura_nem_indice() -> None:
    estrutura = total(assunto(PRECO, grupo(alternativa("R09", "F1"))))
    indice_local = copy.deepcopy(INDICE_PADRAO)
    antes_mapa = copy.deepcopy(estrutura)
    antes_indice = copy.deepcopy(indice_local)

    conferir_referencias(estrutura, indice_local)

    assert estrutura == antes_mapa
    assert indice_local == antes_indice


def test_ordem_fisica_das_listas_e_preservada() -> None:
    """A ordem declarada é o desempate de SF-D4; nada aqui a reordena."""
    estrutura = total(
        assunto(
            PRECO,
            grupo(alternativa("R14", "F1"), alternativa("R09", "F2")),
            grupo(alternativa("R09", "F1")),
        )
    )

    validar_mapa_cobertura(estrutura)
    conferir_referencias(estrutura, INDICE_PADRAO)

    grupos = estrutura["assuntos"][0]["grupos"]
    assert [
        (alt["rxx"], alt["fragmento"])
        for corpo in grupos
        for alt in corpo["alternativas"]
    ] == [("R14", "F1"), ("R09", "F2"), ("R09", "F1")]


# 10. Determinismo


def test_validacao_e_deterministica_no_sucesso() -> None:
    estrutura = total(assunto(PRECO, grupo(alternativa("R09", "F1"))))

    assert validar_mapa_cobertura(estrutura) is None
    assert validar_mapa_cobertura(estrutura) is None


def test_mensagem_de_erro_e_deterministica() -> None:
    estrutura = mapa(assunto(PRECO, {"alternativas": []}))

    mensagens = []
    for _ in range(3):
        with pytest.raises(MapaCoberturaInvalido) as erro:
            validar_mapa_cobertura(estrutura)
        mensagens.append(str(erro.value))

    assert len(set(mensagens)) == 1


def test_primeira_violacao_encerra_sem_acumular() -> None:
    estrutura = mapa(
        assunto(PRECO, {"alternativas": []}),
        assunto("assunto_inexistente", grupo()),
    )

    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura(estrutura)

    assert localizador_de(erro).startswith("assuntos[0]")


# 11. Conferencia de referencias


def test_referencia_valida_contra_indice_sintetico() -> None:
    estrutura = total(
        assunto(PRECO, grupo(alternativa("R09", "F1")), grupo(alternativa("R14", "F1")))
    )

    assert conferir_referencias(estrutura, INDICE_PADRAO) is None


def test_referencia_pendurada_por_fragmento_inexistente() -> None:
    estrutura = total(assunto(PRECO, grupo(alternativa("R09", "F7"))))

    with pytest.raises(MapaCoberturaInvalido) as erro:
        conferir_referencias(estrutura, INDICE_PADRAO)

    assert str(erro.value) == (
        "referencia_pendurada: assuntos[0].grupos[0].alternativas[0]"
    )


def test_referencia_pendurada_por_rxx_inexistente() -> None:
    estrutura = total(assunto(PRECO, grupo(alternativa("R77", "F1"))))

    with pytest.raises(MapaCoberturaInvalido) as erro:
        conferir_referencias(estrutura, INDICE_PADRAO)

    assert categoria_de(erro) == "referencia_pendurada"


def test_referencia_pendurada_aponta_a_alternativa_exata() -> None:
    pendurada = AssuntoComercial.CAPACIDADE_MAXIMA_E_FORMATO.value
    estrutura = total(
        assunto(PRECO, grupo(alternativa("R09", "F1"))),
        assunto(
            pendurada,
            grupo(alternativa("R09", "F1"), alternativa("R14", "F9")),
        ),
    )
    posicao = VALORES_CANONICOS.index(pendurada)

    with pytest.raises(MapaCoberturaInvalido) as erro:
        conferir_referencias(estrutura, INDICE_PADRAO)

    assert localizador_de(erro) == (
        f"assuntos[{posicao}].grupos[0].alternativas[1]"
    )


def test_conferencia_revalida_a_forma_antes_de_percorrer() -> None:
    with pytest.raises(MapaCoberturaInvalido) as erro:
        conferir_referencias({"assuntos": [{"assunto": PRECO}]}, INDICE_PADRAO)

    assert categoria_de(erro) == "campo_ausente"


def test_mapa_total_sem_alternativa_alguma_confere() -> None:
    assert conferir_referencias(total(), INDICE_PADRAO) is None


def test_projecao_de_identidade_invalida_propaga_intacta() -> None:
    """Defeito **da projeção de identidade** não é defeito do mapa.

    Isto **não** prova `D8-CI2`: a validação estrutural integral do índice
    pertence à cadeia de S2-D8 e deve reutilizar `validar_indice`.
    """
    estrutura = total(assunto(PRECO, grupo(alternativa("R09", "F1"))))

    with pytest.raises(ProjecaoDeIdentidadeInvalida):
        conferir_referencias(estrutura, {"respostas": "nao-e-lista"})


def test_defeito_fora_da_projecao_de_identidade_nao_e_julgado_aqui() -> None:
    """A fronteira confere **existência**, não validade do índice.

    O índice abaixo tem `status` fora do vocabulário, *binding* deformado e
    chave desconhecida — defeitos que **`validar_indice` recusaria** e que
    `derivar_tokens_do_indice` **não lê**. Aqui eles passam, e é correto: quem
    exige a validação integral é `D8-CI2`, na cadeia de S2-D8.
    """
    indice_deformado = {
        "respostas": [
            {
                "id": "R09",
                "fragmentos": [
                    {
                        "id": "F1",
                        "status": "STATUS_INEXISTENTE",
                        "bindings": "nao-e-lista",
                        "campo_desconhecido": 1,
                    }
                ],
            }
        ]
    }
    estrutura = total(assunto(PRECO, grupo(alternativa("R09", "F1"))))

    assert conferir_referencias(estrutura, indice_deformado) is None


def test_fragmento_homonimo_em_rxx_distinto_nao_confunde() -> None:
    estrutura = total(assunto(PRECO, grupo(alternativa("R14", "F2"))))

    with pytest.raises(MapaCoberturaInvalido) as erro:
        conferir_referencias(estrutura, INDICE_PADRAO)

    assert categoria_de(erro) == "referencia_pendurada"


# 12. RUNTIME_AUTORITATIVO e itera_sobre NAO invalidam a referencia


INDICE_COM_RUNTIME_E_ITERACAO: dict[str, Any] = {
    "respostas": [
        {
            "id": "R09",
            "fragmentos": [
                {
                    "id": "F1",
                    "status": "APROVADO",
                    "bindings": [
                        {
                            "nome": "disponivel",
                            "mecanismo": "ASSERTIVA",
                            "origem": "RUNTIME_AUTORITATIVO",
                            "fato": "data_disponivel",
                            "predicado": "EH_VERDADEIRO",
                        }
                    ],
                },
                {
                    "id": "F2",
                    "status": "APROVADO",
                    "itera_sobre": "pacotes",
                    "bindings": [],
                },
            ],
        }
    ]
}


def test_alternativa_com_binding_runtime_autoritativo_e_valida() -> None:
    estrutura = total(assunto(PRECO, grupo(alternativa("R09", "F1"))))

    assert validar_mapa_cobertura(estrutura) is None
    assert conferir_referencias(estrutura, INDICE_COM_RUNTIME_E_ITERACAO) is None


def test_alternativa_para_fragmento_com_itera_sobre_e_valida() -> None:
    estrutura = total(assunto(PRECO, grupo(alternativa("R09", "F2"))))

    assert validar_mapa_cobertura(estrutura) is None
    assert conferir_referencias(estrutura, INDICE_COM_RUNTIME_E_ITERACAO) is None


# 13. Mensagem nao carrega conteudo


@pytest.mark.parametrize(
    "estrutura",
    [
        {"assuntos": [{"assunto": "assunto_secreto", "grupos": []}]},
        {"assuntos": [{"assunto": PRECO, "grupos": [{"alternativas": []}]}]},
    ],
)
def test_mensagem_nao_reproduz_o_valor_recebido(estrutura: dict[str, Any]) -> None:
    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura(estrutura)

    assert "assunto_secreto" not in str(erro.value)
    assert PRECO not in str(erro.value)


def test_mensagem_de_referencia_pendurada_nao_nomeia_rxx() -> None:
    estrutura = total(assunto(PRECO, grupo(alternativa("R77", "F9"))))

    with pytest.raises(MapaCoberturaInvalido) as erro:
        conferir_referencias(estrutura, INDICE_PADRAO)

    assert "R77" not in str(erro.value)
    assert "F9" not in str(erro.value)


def test_mensagem_tem_categoria_e_localizador() -> None:
    with pytest.raises(MapaCoberturaInvalido) as erro:
        validar_mapa_cobertura(None)

    assert str(erro.value).count(": ") == 1


def test_excecao_deriva_de_exception() -> None:
    assert issubclass(MapaCoberturaInvalido, Exception)


# 14. Isolamento estrutural — provado sobre a AST do modulo


def _arvore(caminho: Path) -> ast.Module:
    return ast.parse(caminho.read_text(encoding="utf-8"))


def _modulos_importados(caminho: Path) -> set[str]:
    importados: set[str] = set()
    for no in ast.walk(_arvore(caminho)):
        if isinstance(no, ast.Import):
            importados.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module is not None:
            importados.add(no.module)
    return importados


def _codigo_sem_prosa(caminho: Path) -> str:
    """A **superfície executável** do módulo, sem prosa.

    *Docstrings* saem: a negativa em prosa do próprio módulo — que **nomeia** o
    que ele não faz — não pode ser contada como se ele conhecesse a matéria.
    """
    arvore = _arvore(caminho)
    portadores = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    for no in ast.walk(arvore):
        if not isinstance(no, portadores):
            continue
        corpo = no.body
        primeiro = corpo[0] if corpo else None
        if (
            isinstance(primeiro, ast.Expr)
            and isinstance(primeiro.value, ast.Constant)
            and isinstance(primeiro.value.value, str)
        ):
            no.body = corpo[1:] or [ast.Pass()]
    return ast.unparse(arvore)


def test_importa_somente_o_necessario() -> None:
    assert _modulos_importados(MODULO) == {
        "__future__",
        "typing",
        "casa77_sdr.interpretation",
        "casa77_sdr.response_index_tokens",
    }


@pytest.mark.parametrize(
    "proibido",
    [
        "yaml",
        "pathlib",
        "os",
        "io",
        "re",
        "json",
        "logging",
        "datetime",
        "time",
        "random",
        "socket",
        "urllib",
        "http",
        "subprocess",
        "casa77_sdr.coverage_map_load",
        "casa77_sdr.response_index",
        "casa77_sdr.response_index_load",
        "casa77_sdr.response_index_status",
        "casa77_sdr.response_yaml_resolve",
        "casa77_sdr.response_format",
        "casa77_sdr.response_assertion",
        "casa77_sdr.fact_selection",
        "casa77_sdr.response_composition",
        "casa77_sdr.emission_projection",
        "casa77_sdr.response_assembly",
        "casa77_sdr.response_validation",
        "casa77_sdr.state_machine",
        "casa77_sdr.qualification",
        "casa77_sdr.knowledge",
        "casa77_sdr.persistence",
    ],
)
def test_nao_importa_fronteira_proibida(proibido: str) -> None:
    assert proibido not in _modulos_importados(MODULO)


@pytest.mark.parametrize(
    "termo",
    [
        "open(",
        "read_text",
        "write_text",
        "Path(",
        "glob",
        "environ",
        "now(",
        "today(",
        "sleep(",
        "request",
        "sorted(",
        "reverse",
        ".sort(",
    ],
)
def test_superficie_executavel_nao_toca_io_relogio_nem_ordenacao(
    termo: str,
) -> None:
    assert termo not in _codigo_sem_prosa(MODULO)


def test_nao_menciona_caminho_de_knowledge_no_codigo() -> None:
    assert "knowledge" not in _codigo_sem_prosa(MODULO)


# 15. Zero conteudo de mapa embutido


def test_codigo_nao_cita_nenhum_assunto_especifico() -> None:
    """Nenhum mapeamento real `AssuntoComercial → Rxx/Fxx` foi inventado."""
    codigo = _codigo_sem_prosa(MODULO)
    especificos = [
        membro.value
        for membro in AssuntoComercial
        if membro is not AssuntoComercial.ASSUNTO_NAO_CLASSIFICADO
    ]

    assert [valor for valor in especificos if valor in codigo] == []


def test_unico_rxx_citado_e_a_proibicao_do_fragmento_de_lacuna() -> None:
    codigo = _codigo_sem_prosa(MODULO)
    literais = {
        no.value
        for no in ast.walk(ast.parse(codigo))
        if isinstance(no, ast.Constant) and isinstance(no.value, str)
    }

    suspeitos = {
        valor
        for valor in literais
        if len(valor) == 3 and valor[0] == "R" and valor[1:].isdigit()
    }
    assert suspeitos == {"R03"}


def test_modulo_nao_declara_vocabulario_paralelo_de_assunto() -> None:
    codigo = _codigo_sem_prosa(MODULO)

    assert "class AssuntoComercial" not in codigo
    assert "Enum" not in codigo


def test_nao_e_exportado_pelo_init() -> None:
    codigo = MODULO_INIT.read_text(encoding="utf-8")

    assert "coverage_map" not in codigo
    assert "validar_mapa_cobertura" not in codigo
    assert "conferir_referencias" not in codigo


def test_api_publica_e_minima() -> None:
    from casa77_sdr import coverage_map

    assert coverage_map.__all__ == [
        "MapaCoberturaInvalido",
        "conferir_referencias",
        "validar_mapa_cobertura",
    ]


def test_mapa_fisico_existe_e_e_um_arquivo() -> None:
    """O artefato aprovado existe; o seu conteúdo é provado no teste de corpus."""
    assert (RAIZ / "knowledge" / "mapa-cobertura.yaml").is_file()

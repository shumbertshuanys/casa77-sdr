"""Testes da aplicabilidade determinística de pacote.

As fixtures unitárias são **numéricas e sintéticas**: `7` e `13` são escolhidos
por serem pequenos e inequivocamente artificiais, e um teste próprio prova
**mecanicamente** que eles **não** coincidem com a capacidade ou com os limites
vigentes de `knowledge/casa77.yaml`. **Nenhum valor comercial atual aparece
aqui como literal ou como expectativa.**

O único teste que abre a base real faz **comparação estrutural** — que a base
vigente satisfaz a forma exigida e que as faixas se alinham —, **sem reafirmar
os valores** como expectativa.
"""

from __future__ import annotations

import ast
import copy
from pathlib import Path
from typing import Any

import pytest
import yaml

from casa77_sdr.identity import Confianca
from casa77_sdr.interpretation import DadosExtraidos
from casa77_sdr.pricing_applicability import (
    AplicabilidadeNaoAvaliavel,
    AplicabilidadePacote,
    decidir_aplicabilidade_de_pacote,
)
from casa77_sdr.qualification import FormatoEvento

RAIZ = Path(__file__).resolve().parents[1]
MODULO = RAIZ / "src" / "casa77_sdr" / "pricing_applicability.py"
MODULO_INIT = RAIZ / "src" / "casa77_sdr" / "__init__.py"
BASE_REAL = RAIZ / "knowledge" / "casa77.yaml"

ALTA = Confianca.ALTA
BAIXA = Confianca.BAIXA

# Fronteiras **sinteticas**. Nao sao, e nao podem ser, os valores vigentes.
SENTADOS = 7
MAXIMO = 13


def base_de(
    *,
    sentados: Any = SENTADOS,
    maximo: Any = MAXIMO,
    pacotes: Any = None,
    capacidade: Any = None,
    precos: Any = None,
) -> dict[str, Any]:
    """Base **sintética** com a mesma forma estrutural da base comercial."""
    if pacotes is None:
        pacotes = [
            {"codigo": "sintetico_inferior", "limite_convidados": sentados},
            {"codigo": "sintetico_superior", "limite_convidados": maximo},
        ]
    if capacidade is None:
        capacidade = {
            "convidados_sentados": sentados,
            "formato_coquetel": maximo,
            "existe_minimo_convidados": False,
        }
    if precos is None:
        precos = {"moeda": "BRL", "pacotes": pacotes}
    return {"capacidade": capacidade, "precos": precos}


def dados(
    *,
    convidados: Any = None,
    confianca_convidados: Any = None,
    formato: Any = None,
    confianca_formato: Any = None,
) -> DadosExtraidos:
    return DadosExtraidos(
        convidados=convidados,
        confianca_convidados=confianca_convidados,
        formato=formato,
        confianca_formato=confianca_formato,
    )


def decidir(**ajustes: Any) -> AplicabilidadePacote:
    return decidir_aplicabilidade_de_pacote(dados(**ajustes), base_de())


def categoria_de(erro: pytest.ExceptionInfo[Any]) -> str:
    return str(erro.value).split(":", 1)[0]


# --------------------------------------------------------------------------
# 1. Vocabulario


def test_vocabulario_tem_exatamente_quatro_valores() -> None:
    assert [membro.name for membro in AplicabilidadePacote] == [
        "FAIXA_INFERIOR",
        "FAIXA_SUPERIOR",
        "INDETERMINADO",
        "NENHUM_APLICAVEL",
    ]


# --------------------------------------------------------------------------
# 2. Quantidade ausente ou pouco confiavel


def test_convidados_ausentes() -> None:
    assert decidir() is AplicabilidadePacote.INDETERMINADO


def test_convidados_com_confianca_baixa() -> None:
    resultado = decidir(convidados=SENTADOS, confianca_convidados=BAIXA)

    assert resultado is AplicabilidadePacote.INDETERMINADO


def test_convidados_sem_confianca_declarada() -> None:
    resultado = decidir(convidados=SENTADOS)

    assert resultado is AplicabilidadePacote.INDETERMINADO


# --------------------------------------------------------------------------
# 3. Faixa inferior


def test_limite_inferior_exato() -> None:
    resultado = decidir(convidados=SENTADOS, confianca_convidados=ALTA)

    assert resultado is AplicabilidadePacote.FAIXA_INFERIOR


def test_abaixo_da_fronteira_inferior() -> None:
    resultado = decidir(convidados=SENTADOS - 1, confianca_convidados=ALTA)

    assert resultado is AplicabilidadePacote.FAIXA_INFERIOR


def test_faixa_inferior_ignora_o_formato() -> None:
    """Abaixo da fronteira, o formato não muda a faixa."""
    for formato in (None, FormatoEvento.SENTADO, FormatoEvento.COQUETEL):
        resultado = decidir(
            convidados=SENTADOS,
            confianca_convidados=ALTA,
            formato=formato,
            confianca_formato=ALTA if formato else None,
        )

        assert resultado is AplicabilidadePacote.FAIXA_INFERIOR


# --------------------------------------------------------------------------
# 4. Faixa superior e o papel do formato


def test_faixa_superior_com_formato_confiavel() -> None:
    resultado = decidir(
        convidados=SENTADOS + 1,
        confianca_convidados=ALTA,
        formato=FormatoEvento.COQUETEL,
        confianca_formato=ALTA,
    )

    assert resultado is AplicabilidadePacote.FAIXA_SUPERIOR


def test_faixa_superior_sem_formato_e_indeterminado() -> None:
    resultado = decidir(convidados=SENTADOS + 1, confianca_convidados=ALTA)

    assert resultado is AplicabilidadePacote.INDETERMINADO


def test_faixa_superior_com_formato_baixa_e_indeterminado() -> None:
    resultado = decidir(
        convidados=SENTADOS + 1,
        confianca_convidados=ALTA,
        formato=FormatoEvento.COQUETEL,
        confianca_formato=BAIXA,
    )

    assert resultado is AplicabilidadePacote.INDETERMINADO


def test_faixa_superior_com_sentado_continua_faixa_superior() -> None:
    """A ressalva comercial pertence à qualificação, não a esta fronteira."""
    resultado = decidir(
        convidados=SENTADOS + 1,
        confianca_convidados=ALTA,
        formato=FormatoEvento.SENTADO,
        confianca_formato=ALTA,
    )

    assert resultado is AplicabilidadePacote.FAIXA_SUPERIOR


def test_capacidade_maxima_exata() -> None:
    resultado = decidir(
        convidados=MAXIMO,
        confianca_convidados=ALTA,
        formato=FormatoEvento.COQUETEL,
        confianca_formato=ALTA,
    )

    assert resultado is AplicabilidadePacote.FAIXA_SUPERIOR


# --------------------------------------------------------------------------
# 5. Acima da capacidade maxima


def test_acima_da_maxima() -> None:
    resultado = decidir(convidados=MAXIMO + 1, confianca_convidados=ALTA)

    assert resultado is AplicabilidadePacote.NENHUM_APLICAVEL


def test_acima_da_maxima_ignora_o_formato() -> None:
    resultado = decidir(
        convidados=MAXIMO + 1,
        confianca_convidados=ALTA,
        formato=FormatoEvento.COQUETEL,
        confianca_formato=ALTA,
    )

    assert resultado is AplicabilidadePacote.NENHUM_APLICAVEL


def test_quantidade_pouco_confiavel_precede_a_capacidade() -> None:
    """A ordem é fixa: sem confiança não se chega a `NENHUM_APLICAVEL`."""
    resultado = decidir(convidados=MAXIMO + 1, confianca_convidados=BAIXA)

    assert resultado is AplicabilidadePacote.INDETERMINADO


# --------------------------------------------------------------------------
# 6. Fail-closed da entrada


@pytest.mark.parametrize("valor", [object(), None, {}, "dados"])
def test_dados_de_tipo_invalido(valor: object) -> None:
    with pytest.raises(AplicabilidadeNaoAvaliavel) as erro:
        decidir_aplicabilidade_de_pacote(valor, base_de())

    assert str(erro.value) == "tipo_invalido: dados"


@pytest.mark.parametrize("valor", [True, 7.0, "7", [7]])
def test_convidados_de_tipo_invalido(valor: object) -> None:
    with pytest.raises(AplicabilidadeNaoAvaliavel) as erro:
        decidir(convidados=valor, confianca_convidados=ALTA)

    assert str(erro.value) == "tipo_invalido: dados.convidados"


# --------------------------------------------------------------------------
# 7. Fail-closed da base


@pytest.mark.parametrize("valor", [None, [], "base", 0])
def test_base_de_tipo_invalido(valor: object) -> None:
    with pytest.raises(AplicabilidadeNaoAvaliavel) as erro:
        decidir_aplicabilidade_de_pacote(dados(), valor)

    assert str(erro.value) == "tipo_invalido: base"


def test_capacidade_ausente() -> None:
    base = base_de()
    del base["capacidade"]

    with pytest.raises(AplicabilidadeNaoAvaliavel) as erro:
        decidir_aplicabilidade_de_pacote(dados(), base)

    assert str(erro.value) == "campo_ausente: capacidade"


@pytest.mark.parametrize(
    ("chave", "caminho"),
    [
        ("convidados_sentados", "capacidade.convidados_sentados"),
        ("formato_coquetel", "capacidade.formato_coquetel"),
    ],
)
@pytest.mark.parametrize("valor", [True, 7.0, "7", None])
def test_capacidade_de_estrutura_invalida(
    chave: str, caminho: str, valor: object
) -> None:
    base = base_de()
    base["capacidade"][chave] = valor

    with pytest.raises(AplicabilidadeNaoAvaliavel) as erro:
        decidir_aplicabilidade_de_pacote(dados(), base)

    assert caminho in str(erro.value)


def test_capacidade_nao_ordenada() -> None:
    base = base_de()
    base["capacidade"]["convidados_sentados"] = MAXIMO
    base["capacidade"]["formato_coquetel"] = MAXIMO

    with pytest.raises(AplicabilidadeNaoAvaliavel) as erro:
        decidir_aplicabilidade_de_pacote(dados(), base)

    assert str(erro.value) == "combinacao_invalida: capacidade"


def test_pacotes_ausentes() -> None:
    base = base_de()
    del base["precos"]["pacotes"]

    with pytest.raises(AplicabilidadeNaoAvaliavel) as erro:
        decidir_aplicabilidade_de_pacote(dados(), base)

    assert str(erro.value) == "campo_ausente: precos.pacotes"


@pytest.mark.parametrize("quantidade", [0, 1, 3])
def test_numero_de_pacotes_diferente_de_dois(quantidade: int) -> None:
    """Nem pacote único, nem terceiro pacote: o MVP tem **duas** faixas."""
    pacotes = [
        {"codigo": f"sintetico_{i}", "limite_convidados": SENTADOS + i}
        for i in range(quantidade)
    ]

    with pytest.raises(AplicabilidadeNaoAvaliavel) as erro:
        decidir_aplicabilidade_de_pacote(dados(), base_de(pacotes=pacotes))

    assert str(erro.value) == "valor_invalido: precos.pacotes"


def test_limites_duplicados() -> None:
    pacotes = [
        {"codigo": "a", "limite_convidados": SENTADOS},
        {"codigo": "b", "limite_convidados": SENTADOS},
    ]

    with pytest.raises(AplicabilidadeNaoAvaliavel) as erro:
        decidir_aplicabilidade_de_pacote(dados(), base_de(pacotes=pacotes))

    assert str(erro.value) == "valor_invalido: precos.pacotes.item.limite_convidados"


def test_faixas_nao_alinhadas_com_a_capacidade() -> None:
    """As duas autoridades precisam concordar sobre onde ficam as fronteiras."""
    pacotes = [
        {"codigo": "a", "limite_convidados": SENTADOS + 1},
        {"codigo": "b", "limite_convidados": MAXIMO},
    ]

    with pytest.raises(AplicabilidadeNaoAvaliavel) as erro:
        decidir_aplicabilidade_de_pacote(dados(), base_de(pacotes=pacotes))

    assert str(erro.value) == "combinacao_invalida: precos.pacotes"


@pytest.mark.parametrize("valor", [None, "", 0, []])
def test_codigo_de_pacote_invalido(valor: object) -> None:
    pacotes = [
        {"codigo": valor, "limite_convidados": SENTADOS},
        {"codigo": "b", "limite_convidados": MAXIMO},
    ]

    with pytest.raises(AplicabilidadeNaoAvaliavel) as erro:
        decidir_aplicabilidade_de_pacote(dados(), base_de(pacotes=pacotes))

    assert "precos.pacotes.item.codigo" in str(erro.value)


@pytest.mark.parametrize("valor", [True, 7.0, "7", None])
def test_limite_de_pacote_invalido(valor: object) -> None:
    pacotes = [
        {"codigo": "a", "limite_convidados": valor},
        {"codigo": "b", "limite_convidados": MAXIMO},
    ]

    with pytest.raises(AplicabilidadeNaoAvaliavel) as erro:
        decidir_aplicabilidade_de_pacote(dados(), base_de(pacotes=pacotes))

    assert "precos.pacotes.item.limite_convidados" in str(erro.value)


def test_falha_de_base_nunca_vira_indeterminado() -> None:
    """`INDETERMINADO` é veredito comercial, não substituto de falha técnica."""
    base = base_de()
    del base["precos"]["pacotes"]

    with pytest.raises(AplicabilidadeNaoAvaliavel):
        decidir_aplicabilidade_de_pacote(
            dados(convidados=SENTADOS, confianca_convidados=ALTA), base
        )


# --------------------------------------------------------------------------
# 8. Pureza, determinismo e imutabilidade


def test_entradas_nao_sao_mutadas() -> None:
    base = base_de()
    entrada = dados(convidados=SENTADOS + 1, confianca_convidados=ALTA)
    antes = copy.deepcopy(base)

    decidir_aplicabilidade_de_pacote(entrada, base)

    assert base == antes


def test_decisao_e_deterministica() -> None:
    entrada = dados(convidados=SENTADOS + 1, confianca_convidados=ALTA)
    base = base_de()

    assert decidir_aplicabilidade_de_pacote(
        entrada, base
    ) is decidir_aplicabilidade_de_pacote(entrada, base)


def _arvore() -> ast.Module:
    return ast.parse(MODULO.read_text(encoding="utf-8"))


def _modulos_importados() -> set[str]:
    importados: set[str] = set()
    for no in ast.walk(_arvore()):
        if isinstance(no, ast.Import):
            importados.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module is not None:
            importados.add(no.module)
    return importados


def _codigo_sem_prosa() -> str:
    arvore = _arvore()
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
    assert _modulos_importados() == {
        "__future__",
        "enum",
        "typing",
        "casa77_sdr.identity",
        "casa77_sdr.interpretation",
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
        "casa77_sdr.knowledge",
        "casa77_sdr.coverage_map",
        "casa77_sdr.coverage_decision",
        "casa77_sdr.state_machine",
        "casa77_sdr.rules",
    ],
)
def test_nao_importa_fronteira_proibida(proibido: str) -> None:
    assert proibido not in _modulos_importados()


@pytest.mark.parametrize(
    "termo",
    ["open(", "read_text", "Path(", "environ", "now(", "sleep(", "request"],
)
def test_superficie_executavel_e_pura(termo: str) -> None:
    assert termo not in _codigo_sem_prosa()


def test_codigo_nao_conhece_rxx_nem_assunto() -> None:
    codigo = _codigo_sem_prosa()

    assert "Rxx" not in codigo
    assert "AssuntoComercial" not in codigo
    assert "fragmento" not in codigo


def test_nao_e_exportado_pelo_init() -> None:
    codigo = MODULO_INIT.read_text(encoding="utf-8")

    assert "pricing_applicability" not in codigo


# --------------------------------------------------------------------------
# 9. Zero valor comercial copiado


def _base_real() -> dict[str, Any]:
    return yaml.safe_load(BASE_REAL.read_text(encoding="utf-8"))


def test_fixtures_sinteticas_nao_reproduzem_valores_vigentes() -> None:
    """Prova mecânica de que nada da base vigente foi copiado para os testes."""
    base = _base_real()
    vigentes = {
        base["capacidade"]["convidados_sentados"],
        base["capacidade"]["formato_coquetel"],
        *(p["limite_convidados"] for p in base["precos"]["pacotes"]),
    }

    assert SENTADOS not in vigentes
    assert MAXIMO not in vigentes


def test_modulo_nao_carrega_numero_comercial() -> None:
    """Nenhum inteiro da base vigente aparece como literal no módulo."""
    base = _base_real()
    vigentes = {
        base["capacidade"]["convidados_sentados"],
        base["capacidade"]["formato_coquetel"],
        *(p["limite_convidados"] for p in base["precos"]["pacotes"]),
    }
    literais = {
        no.value
        for no in ast.walk(ast.parse(_codigo_sem_prosa()))
        if isinstance(no, ast.Constant) and type(no.value) is int
    }

    assert literais & vigentes == set()


def test_base_vigente_satisfaz_a_forma_exigida() -> None:
    """Comparação **estrutural** com a base real, sem expectativa literal."""
    base = _base_real()
    capacidade = base["capacidade"]
    pacotes = base["precos"]["pacotes"]
    limites = [p["limite_convidados"] for p in pacotes]

    assert len(pacotes) == 2
    assert all(type(limite) is int for limite in limites)
    assert len(set(limites)) == 2
    assert min(limites) == capacidade["convidados_sentados"]
    assert max(limites) == capacidade["formato_coquetel"]
    assert capacidade["convidados_sentados"] < capacidade["formato_coquetel"]


def test_base_vigente_decide_as_tres_faixas() -> None:
    """Sobre a base real, as três faixas continuam alcançáveis."""
    base = _base_real()
    sentados = base["capacidade"]["convidados_sentados"]
    maximo = base["capacidade"]["formato_coquetel"]

    assert (
        decidir_aplicabilidade_de_pacote(
            dados(convidados=sentados, confianca_convidados=ALTA), base
        )
        is AplicabilidadePacote.FAIXA_INFERIOR
    )
    assert (
        decidir_aplicabilidade_de_pacote(
            dados(
                convidados=maximo,
                confianca_convidados=ALTA,
                formato=FormatoEvento.COQUETEL,
                confianca_formato=ALTA,
            ),
            base,
        )
        is AplicabilidadePacote.FAIXA_SUPERIOR
    )
    assert (
        decidir_aplicabilidade_de_pacote(
            dados(convidados=maximo + 1, confianca_convidados=ALTA), base
        )
        is AplicabilidadePacote.NENHUM_APLICAVEL
    )

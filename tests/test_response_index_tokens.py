"""Testes do derivador determinístico do domínio canônico de tokens do índice.

A fronteira produz **identidade** e nada mais: os tokens `<Rxx>/<id>` de
`C-A5-T1`, compostos a partir do `Rxx` da resposta e do `fragmentos[].id`, na
ordem das listas recebidas. Estes testes provam a projeção mínima, a forma
fechada de **C-2b** para o `Rxx`, a gramática fechada de **`C-A5-I3`** para o
`id`, a unicidade global do `Rxx` (**C-2a**) e a unicidade **local ao `Rxx`** do
`id` (**`C-A5-I4`**, **C-2h**), a política de tipo, a precedência fixa, o
silêncio da mensagem de erro, a pureza do módulo de produção e o determinismo —
e **não** transformam em norma a substituição de `validar_indice`, a validação
de `status`/`bindings`, a existência do índice real, a execução da bijeção ou a
satisfação de `C-A1-ST6`–`C-A1-ST10`, que estão **fora** desta fronteira.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import casa77_sdr
from casa77_sdr.response_index_tokens import (
    ProjecaoDeIdentidadeInvalida,
    derivar_tokens_do_indice,
)

# ---------------------------------------------------------------------------
# Apoio
# ---------------------------------------------------------------------------

RAIZ = Path(__file__).resolve().parent.parent

CAMINHO_PRODUCAO = RAIZ / "src" / "casa77_sdr" / "response_index_tokens.py"
CODIGO_PRODUCAO = CAMINHO_PRODUCAO.read_text(encoding="utf-8")
ARVORE_PRODUCAO = ast.parse(CODIGO_PRODUCAO)

CATEGORIAS = ("tipo_invalido", "campo_ausente", "valor_invalido", "duplicidade")
LOCALIZADORES = (
    "indice",
    "respostas",
    "respostas.item",
    "respostas.item.id",
    "respostas.item.fragmentos",
    "respostas.item.fragmentos.item",
    "respostas.item.fragmentos.item.id",
)


def fragmento(identificador, **extras):
    """Fragmento com o `id` dado e, opcionalmente, campos fora da projeção."""
    corpo = {"id": identificador}
    corpo.update(extras)
    return corpo


def resposta(rxx, *ids, **extras):
    corpo = {"id": rxx, "fragmentos": [fragmento(i) for i in ids]}
    corpo.update(extras)
    return corpo


def indice(*respostas):
    return {"respostas": list(respostas)}


def categoria_de(erro) -> str:
    return str(erro.value).split(":")[0]


class IdPermissivo(str):
    """Subclasse de `str` que sequestra a igualdade e o hash.

    Ela se declara igual a qualquer coisa. Se a fronteira compusesse o token
    antes de conferir o tipo, esta subclasse decidiria sozinha quando dois
    identificadores são o mesmo — exatamente o que a recusa por tipo exato
    impede.
    """

    def __eq__(self, outro: object) -> bool:
        return True

    def __ne__(self, outro: object) -> bool:
        return False

    def __hash__(self) -> int:
        return 0


class IdSimples(str):
    """Subclasse de `str` que não redefine coisa alguma."""


class MapaDerivado(dict):
    """Subclasse de `dict` — deve ser aceita como contêiner."""


class ListaDerivada(list):
    """Subclasse de `list` — deve ser aceita como contêiner."""


def _docstrings(arvore: ast.AST) -> set[int]:
    ids: set[int] = set()
    for no in ast.walk(arvore):
        if isinstance(
            no, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            corpo = getattr(no, "body", [])
            if (
                corpo
                and isinstance(corpo[0], ast.Expr)
                and isinstance(corpo[0].value, ast.Constant)
                and isinstance(corpo[0].value.value, str)
            ):
                ids.add(id(corpo[0].value))
    return ids


IDS_DOCSTRING = _docstrings(ARVORE_PRODUCAO)


def _nomes_usados() -> set[str]:
    nomes: set[str] = set()
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.Name):
            nomes.add(no.id)
        elif isinstance(no, ast.Attribute):
            nomes.add(no.attr)
    return nomes


NOMES_PRODUCAO = _nomes_usados()


def _constantes_de_codigo() -> list[str]:
    return [
        no.value
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.Constant)
        and isinstance(no.value, str)
        and id(no) not in IDS_DOCSTRING
    ]


# ---------------------------------------------------------------------------
# A. Caminho feliz e ordem
# ---------------------------------------------------------------------------


def test_uma_resposta_um_fragmento():
    assert derivar_tokens_do_indice(indice(resposta("R01", "F1"))) == ("R01/F1",)


def test_varias_respostas():
    dados = indice(resposta("R01", "F1"), resposta("R02", "F1"), resposta("R03", "F1"))
    assert derivar_tokens_do_indice(dados) == ("R01/F1", "R02/F1", "R03/F1")


def test_varios_fragmentos():
    dados = indice(resposta("R05", "F1", "F2", "F3"))
    assert derivar_tokens_do_indice(dados) == ("R05/F1", "R05/F2", "R05/F3")


def test_ordem_das_listas_e_preservada():
    dados = indice(resposta("R09", "F2", "F1"), resposta("R01", "F1"))
    assert derivar_tokens_do_indice(dados) == ("R09/F2", "R09/F1", "R01/F1")


def test_mesmo_id_em_rxx_distintos_e_valido():
    dados = indice(resposta("R01", "F1"), resposta("R02", "F1"))
    assert derivar_tokens_do_indice(dados) == ("R01/F1", "R02/F1")


def test_retorno_e_tupla_de_str_exata():
    tokens = derivar_tokens_do_indice(indice(resposta("R01", "F1")))
    assert type(tokens) is tuple
    for token in tokens:
        assert type(token) is str


def test_separador_e_a_barra():
    (token,) = derivar_tokens_do_indice(indice(resposta("R07", "F10")))
    assert token == "R07/F10"
    assert token.count("/") == 1


def test_respostas_vazias_devolve_tupla_vazia():
    assert derivar_tokens_do_indice({"respostas": []}) == ()


def test_id_de_dois_digitos_e_aceito():
    assert derivar_tokens_do_indice(indice(resposta("R30", "F12"))) == ("R30/F12",)


def test_contadores_grandes_de_rxx_sao_aceitos():
    assert derivar_tokens_do_indice(indice(resposta("R99", "F1"))) == ("R99/F1",)


def test_r00_e_aceito_porque_c2b_nao_impoe_faixa():
    assert derivar_tokens_do_indice(indice(resposta("R00", "F1"))) == ("R00/F1",)


# ---------------------------------------------------------------------------
# B. Raiz e `respostas`
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "invalido",
    [None, 0, 1, True, 3.5, "respostas", b"{}", [], (), set(), object()],
)
def test_raiz_nao_mapeamento_e_recusada(invalido):
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice(invalido)
    assert str(erro.value) == "tipo_invalido: indice"


def test_respostas_ausente():
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice({})
    assert str(erro.value) == "campo_ausente: respostas"


@pytest.mark.parametrize("invalido", [None, 0, "R01", {}, (), set(), object()])
def test_respostas_nao_lista(invalido):
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice({"respostas": invalido})
    assert str(erro.value) == "tipo_invalido: respostas"


@pytest.mark.parametrize("invalido", [None, 0, "R01", [], (), object()])
def test_resposta_nao_mapeamento(invalido):
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice({"respostas": [invalido]})
    assert str(erro.value) == "tipo_invalido: respostas.item"


# ---------------------------------------------------------------------------
# C. `Rxx` — C-2a / C-2b
# ---------------------------------------------------------------------------


def test_rxx_ausente():
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice({"respostas": [{"fragmentos": [{"id": "F1"}]}]})
    assert str(erro.value) == "campo_ausente: respostas.item.id"


@pytest.mark.parametrize("invalido", [None, 1, True, 3.5, b"R01", ["R01"], object()])
def test_rxx_nao_str(invalido):
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice(indice(resposta(invalido, "F1")))
    assert str(erro.value) == "tipo_invalido: respostas.item.id"


def test_rxx_subclasse_permissiva_e_recusada_por_tipo():
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice(indice(resposta(IdPermissivo("R01"), "F1")))
    assert str(erro.value) == "tipo_invalido: respostas.item.id"


def test_rxx_subclasse_simples_tambem_e_recusada():
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice(indice(resposta(IdSimples("R01"), "F1")))
    assert str(erro.value) == "tipo_invalido: respostas.item.id"


def test_str_normal_com_o_mesmo_conteudo_da_subclasse_e_aceita():
    assert derivar_tokens_do_indice(indice(resposta(str("R01"), "F1"))) == ("R01/F1",)


@pytest.mark.parametrize(
    "rxx",
    [
        "",
        "R",
        "R1",
        "R001",
        "r01",
        "RXX",
        "R0a",
        "R01 ",
        " R01",
        "R-1",
        "R01/",
        "01",
        "R¹²",
        "R١٢",
        "R０１",
    ],
)
def test_rxx_fora_da_forma_fechada(rxx):
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice(indice(resposta(rxx, "F1")))
    assert str(erro.value) == "valor_invalido: respostas.item.id"


def test_rxx_duplicado_globalmente_e_recusado():
    dados = indice(resposta("R01", "F1"), resposta("R01", "F2"))
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice(dados)
    assert str(erro.value) == "duplicidade: respostas.item.id"


def test_rxx_duplicado_nao_precisa_ser_adjacente():
    dados = indice(resposta("R01", "F1"), resposta("R02", "F1"), resposta("R01", "F2"))
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice(dados)
    assert categoria_de(erro) == "duplicidade"


# ---------------------------------------------------------------------------
# D. `fragmentos` — C-2c
# ---------------------------------------------------------------------------


def test_fragmentos_ausente():
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice({"respostas": [{"id": "R01"}]})
    assert str(erro.value) == "campo_ausente: respostas.item.fragmentos"


@pytest.mark.parametrize("invalido", [None, 0, "F1", {}, (), set(), object()])
def test_fragmentos_nao_lista(invalido):
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice({"respostas": [{"id": "R01", "fragmentos": invalido}]})
    assert str(erro.value) == "tipo_invalido: respostas.item.fragmentos"


def test_fragmentos_vazio_e_recusado():
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice({"respostas": [{"id": "R01", "fragmentos": []}]})
    assert str(erro.value) == "valor_invalido: respostas.item.fragmentos"


@pytest.mark.parametrize("invalido", [None, 0, "F1", [], (), object()])
def test_fragmento_nao_mapeamento(invalido):
    dados = {"respostas": [{"id": "R01", "fragmentos": [invalido]}]}
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice(dados)
    assert str(erro.value) == "tipo_invalido: respostas.item.fragmentos.item"


# ---------------------------------------------------------------------------
# E. `fragmentos[].id` — `C-A5-I3` / `C-A5-I4` / C-2h
# ---------------------------------------------------------------------------


def test_id_de_fragmento_ausente():
    dados = {"respostas": [{"id": "R01", "fragmentos": [{}]}]}
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice(dados)
    assert str(erro.value) == "campo_ausente: respostas.item.fragmentos.item.id"


@pytest.mark.parametrize("invalido", [None, 1, True, 3.5, b"F1", ["F1"], object()])
def test_id_de_fragmento_nao_str(invalido):
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice(indice(resposta("R01", invalido)))
    assert str(erro.value) == "tipo_invalido: respostas.item.fragmentos.item.id"


def test_id_de_fragmento_subclasse_permissiva_e_recusada():
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice(indice(resposta("R01", IdPermissivo("F1"))))
    assert str(erro.value) == "tipo_invalido: respostas.item.fragmentos.item.id"


def test_id_de_fragmento_subclasse_simples_tambem_e_recusada():
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice(indice(resposta("R01", IdSimples("F1"))))
    assert str(erro.value) == "tipo_invalido: respostas.item.fragmentos.item.id"


@pytest.mark.parametrize("identificador", ["F1", "F2", "F3", "F9", "F10", "F99", "F100"])
def test_id_conforme_c_a5_i3_e_aceito(identificador):
    assert derivar_tokens_do_indice(indice(resposta("R01", identificador))) == (
        f"R01/{identificador}",
    )


@pytest.mark.parametrize(
    "identificador",
    [
        "",
        "F",
        "F0",
        "F01",
        "F010",
        "f1",
        "F-1",
        "F+1",
        "F1x",
        "F 1",
        "F1.0",
        "1",
        "1F",
        "FF1",
        "G1",
        "F1/",
        "F¹",
        "F١",
        "F１",
    ],
)
def test_id_fora_da_gramatica_c_a5_i3(identificador):
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice(indice(resposta("R01", identificador)))
    assert str(erro.value) == "valor_invalido: respostas.item.fragmentos.item.id"


def test_id_duplicado_dentro_do_mesmo_rxx():
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice(indice(resposta("R01", "F1", "F1")))
    assert str(erro.value) == "duplicidade: respostas.item.fragmentos.item.id"


def test_id_duplicado_nao_precisa_ser_adjacente():
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice(indice(resposta("R01", "F1", "F2", "F1")))
    assert categoria_de(erro) == "duplicidade"


def test_unicidade_do_id_e_local_ao_rxx():
    dados = indice(resposta("R01", "F1", "F2"), resposta("R02", "F2", "F1"))
    assert derivar_tokens_do_indice(dados) == (
        "R01/F1",
        "R01/F2",
        "R02/F2",
        "R02/F1",
    )


# ---------------------------------------------------------------------------
# F. Contêineres — subclasses aceitas
# ---------------------------------------------------------------------------


def test_subclasse_de_dict_e_aceita_na_raiz():
    dados = MapaDerivado({"respostas": [resposta("R01", "F1")]})
    assert derivar_tokens_do_indice(dados) == ("R01/F1",)


def test_subclasse_de_list_e_aceita_em_respostas():
    dados = {"respostas": ListaDerivada([resposta("R01", "F1")])}
    assert derivar_tokens_do_indice(dados) == ("R01/F1",)


def test_subclasse_de_dict_e_aceita_na_resposta_e_no_fragmento():
    dados = {
        "respostas": [
            MapaDerivado(
                {
                    "id": "R01",
                    "fragmentos": ListaDerivada([MapaDerivado({"id": "F1"})]),
                }
            )
        ]
    }
    assert derivar_tokens_do_indice(dados) == ("R01/F1",)


# ---------------------------------------------------------------------------
# G. Limites — a fronteira nao substitui `validar_indice`
# ---------------------------------------------------------------------------


def test_status_invalido_nao_e_julgado():
    dados = indice(
        {
            "id": "R01",
            "fragmentos": [{"id": "F1", "status": "PARCIAL"}],
        }
    )
    assert derivar_tokens_do_indice(dados) == ("R01/F1",)


def test_status_ausente_nao_e_julgado():
    assert derivar_tokens_do_indice(indice(resposta("R01", "F1"))) == ("R01/F1",)


def test_bindings_invalidos_nao_sao_julgados():
    dados = indice(
        {
            "id": "R01",
            "fragmentos": [{"id": "F1", "bindings": "isto nao e uma lista"}],
        }
    )
    assert derivar_tokens_do_indice(dados) == ("R01/F1",)


def test_itera_sobre_posicional_nao_e_julgado():
    dados = indice(
        {"id": "R01", "fragmentos": [{"id": "F1", "itera_sobre": "colecao[0]"}]}
    )
    assert derivar_tokens_do_indice(dados) == ("R01/F1",)


def test_chaves_desconhecidas_nao_transformam_em_validar_indice():
    dados = {
        "respostas": [
            {
                "id": "R01",
                "fragmentos": [{"id": "F1", "campo_inventado": 123}],
                "outro_campo": [1, 2, 3],
            }
        ],
        "campo_de_topo_desconhecido": {"qualquer": "coisa"},
    }
    assert derivar_tokens_do_indice(dados) == ("R01/F1",)


def test_nao_importa_nem_chama_validar_indice():
    assert "validar_indice" not in NOMES_PRODUCAO
    assert "validar_bijecao" not in NOMES_PRODUCAO
    assert "ler_unidades_marcadas" not in NOMES_PRODUCAO
    assert "carregar_indice" not in NOMES_PRODUCAO


# ---------------------------------------------------------------------------
# H. Precedencia — primeira violacao encerra
# ---------------------------------------------------------------------------


def test_tipo_da_raiz_precede_tudo():
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice([resposta("R01", "F1")])
    assert categoria_de(erro) == "tipo_invalido"


def test_rxx_precede_fragmentos():
    dados = {"respostas": [{"id": "r01", "fragmentos": []}]}
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice(dados)
    assert str(erro.value) == "valor_invalido: respostas.item.id"


def test_tipo_do_rxx_precede_a_forma():
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice(indice(resposta(IdSimples("nao e rxx"), "F1")))
    assert categoria_de(erro) == "tipo_invalido"


def test_forma_do_id_precede_a_duplicidade():
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice(indice(resposta("R01", "F0", "F0")))
    assert categoria_de(erro) == "valor_invalido"


def test_resposta_anterior_prevalece_sobre_posterior():
    dados = indice(resposta("R01", "F0"), resposta("r02", "F1"))
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice(dados)
    assert str(erro.value) == "valor_invalido: respostas.item.fragmentos.item.id"


def test_fragmentos_vazio_precede_defeito_da_resposta_seguinte():
    dados = {
        "respostas": [
            {"id": "R01", "fragmentos": []},
            {"id": "R02", "fragmentos": [{"id": "F0"}]},
        ]
    }
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice(dados)
    assert str(erro.value) == "valor_invalido: respostas.item.fragmentos"


# ---------------------------------------------------------------------------
# I. Mensagem — forma fechada e sem eco
# ---------------------------------------------------------------------------

CASOS_DE_FALHA = (
    "nao e mapeamento",
    {},
    {"respostas": "nao e lista"},
    {"respostas": ["nao e mapeamento"]},
    {"respostas": [{"fragmentos": [{"id": "F1"}]}]},
    {"respostas": [{"id": 12345, "fragmentos": [{"id": "F1"}]}]},
    {"respostas": [{"id": "SEGREDO", "fragmentos": [{"id": "F1"}]}]},
    {"respostas": [{"id": "R01"}]},
    {"respostas": [{"id": "R01", "fragmentos": "nao e lista"}]},
    {"respostas": [{"id": "R01", "fragmentos": []}]},
    {"respostas": [{"id": "R01", "fragmentos": ["nao e mapeamento"]}]},
    {"respostas": [{"id": "R01", "fragmentos": [{}]}]},
    {"respostas": [{"id": "R01", "fragmentos": [{"id": 999}]}]},
    {"respostas": [{"id": "R01", "fragmentos": [{"id": "SEGREDO"}]}]},
    {"respostas": [{"id": "R01", "fragmentos": [{"id": "F1"}, {"id": "F1"}]}]},
    {
        "respostas": [
            {"id": "R01", "fragmentos": [{"id": "F1"}]},
            {"id": "R01", "fragmentos": [{"id": "F1"}]},
        ]
    },
)


@pytest.mark.parametrize("caso", CASOS_DE_FALHA)
def test_mensagem_tem_categoria_e_localizador(caso):
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice(caso)
    mensagem = str(erro.value)
    categoria, _, localizador = mensagem.partition(": ")
    assert categoria in CATEGORIAS
    assert localizador in LOCALIZADORES
    assert mensagem == f"{categoria}: {localizador}"


@pytest.mark.parametrize("caso", CASOS_DE_FALHA)
def test_mensagem_nao_ecoa_valor_recebido(caso):
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice(caso)
    mensagem = str(erro.value)
    for vazamento in ("SEGREDO", "R01", "F1", "12345", "999", "nao e", "/"):
        assert vazamento not in mensagem


@pytest.mark.parametrize("caso", CASOS_DE_FALHA)
def test_mensagem_nao_ecoa_numero_nem_tipo(caso):
    with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
        derivar_tokens_do_indice(caso)
    mensagem = str(erro.value)
    assert not any(caractere.isdigit() for caractere in mensagem)
    for tipo in ("int", "str", "list", "dict", "NoneType", "object"):
        assert tipo not in mensagem


def test_excecao_deriva_apenas_de_exception():
    assert ProjecaoDeIdentidadeInvalida.__bases__ == (Exception,)


def test_excecao_nao_e_parente_de_outro_erro_do_projeto():
    from casa77_sdr.response_bijection import BijecaoInvalida
    from casa77_sdr.response_index import IndiceInvalido
    from casa77_sdr.response_markdown_units import RepresentacaoMarcadaInvalida
    from casa77_sdr.response_status import StatusNaoCanonicalizavel

    for outra in (
        BijecaoInvalida,
        IndiceInvalido,
        RepresentacaoMarcadaInvalida,
        StatusNaoCanonicalizavel,
    ):
        assert not issubclass(ProjecaoDeIdentidadeInvalida, outra)
        assert not issubclass(outra, ProjecaoDeIdentidadeInvalida)


# ---------------------------------------------------------------------------
# J. Pureza do modulo de producao
# ---------------------------------------------------------------------------


def test_nao_e_exportado_pelo_pacote():
    assert "derivar_tokens_do_indice" not in casa77_sdr.__all__
    assert "ProjecaoDeIdentidadeInvalida" not in casa77_sdr.__all__
    assert not hasattr(casa77_sdr, "derivar_tokens_do_indice")
    assert not hasattr(casa77_sdr, "ProjecaoDeIdentidadeInvalida")


def test_all_do_modulo_e_fechado():
    from casa77_sdr import response_index_tokens

    assert response_index_tokens.__all__ == [
        "ProjecaoDeIdentidadeInvalida",
        "derivar_tokens_do_indice",
    ]


def test_imports_sao_fechados_em_future():
    importados = [no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.Import)]
    de_modulo = [
        no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.ImportFrom)
    ]
    assert importados == []
    assert [no.module for no in de_modulo] == ["__future__"]


def test_nao_importa_nada_do_proprio_pacote():
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.ImportFrom):
            assert not (no.module or "").startswith("casa77_sdr")
        if isinstance(no, ast.Import):  # pragma: no cover - lista ja e vazia
            for alias in no.names:
                assert not alias.name.startswith("casa77_sdr")


def test_nao_ha_import_dentro_de_funcao():
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for interno in ast.walk(no):
                assert not isinstance(interno, (ast.Import, ast.ImportFrom))


def test_nao_ha_io_nem_filesystem():
    proibidos = {
        "open",
        "read",
        "read_text",
        "read_bytes",
        "write",
        "write_text",
        "write_bytes",
        "Path",
        "pathlib",
        "os",
        "io",
        "sys",
        "stdin",
        "stdout",
        "stderr",
        "input",
        "print",
        "glob",
        "listdir",
        "shutil",
        "tempfile",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_yaml_nem_serializacao_externa():
    proibidos = {"yaml", "safe_load", "load", "json", "loads", "dumps", "pickle"}
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_rede_processo_nem_llm():
    proibidos = {
        "socket",
        "requests",
        "urllib",
        "urlopen",
        "http",
        "httpx",
        "subprocess",
        "Popen",
        "git",
        "prompt",
        "completions",
        "sqlite3",
        "connect",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_relogio_calendario_locale_nem_ambiente():
    proibidos = {
        "time",
        "monotonic",
        "datetime",
        "date",
        "now",
        "utcnow",
        "today",
        "calendar",
        "locale",
        "setlocale",
        "getenv",
        "environ",
        "zoneinfo",
        "random",
        "uuid",
        "hashlib",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_normalizacao_de_texto():
    proibidos = {
        "unicodedata",
        "normalize",
        "casefold",
        "lower",
        "upper",
        "strip",
        "lstrip",
        "rstrip",
        "expandtabs",
        "splitlines",
        "translate",
        "encode",
        "decode",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_execucao_dinamica():
    proibidos = {"eval", "exec", "compile", "__import__", "importlib", "globals"}
    assert not proibidos & NOMES_PRODUCAO


def test_categorias_e_localizadores_sao_fechados():
    from casa77_sdr import response_index_tokens

    publicos = set(response_index_tokens.__all__)
    constantes = set(_constantes_de_codigo()) - publicos
    candidatas = {
        constante
        for constante in constantes
        if constante.islower() and " " not in constante
    }
    assert candidatas == set(CATEGORIAS) | set(LOCALIZADORES) | {
        "id",
        "fragmentos",
        "respostas",
    }


def test_a_docstring_declara_os_limites():
    docstring = ast.get_docstring(ARVORE_PRODUCAO) or ""
    for exigido in (
        "DERIVAR O DOMÍNIO NÃO É MATERIALIZAR",
        "NÃO substitui `validar_indice`",
        "C-A1-ST6",
        "C-A5-I3",
        "C-A5-T5",
        "INEXISTENTE",
    ):
        assert exigido in docstring


# ---------------------------------------------------------------------------
# K. Determinismo e ausencia de efeito
# ---------------------------------------------------------------------------

DADOS_ESTAVEIS = {
    "respostas": [
        {"id": "R01", "fragmentos": [{"id": "F1"}]},
        {"id": "R05", "fragmentos": [{"id": "F1"}, {"id": "F2"}, {"id": "F3"}]},
    ]
}


def test_chamadas_repetidas_devolvem_o_mesmo_resultado():
    assert derivar_tokens_do_indice(DADOS_ESTAVEIS) == derivar_tokens_do_indice(
        DADOS_ESTAVEIS
    )


def test_a_estrutura_recebida_nao_e_alterada():
    import copy

    dados = copy.deepcopy(DADOS_ESTAVEIS)
    antes = copy.deepcopy(dados)
    derivar_tokens_do_indice(dados)
    assert dados == antes


def test_nenhum_token_e_gravado_na_estrutura():
    import copy

    dados = copy.deepcopy(DADOS_ESTAVEIS)
    derivar_tokens_do_indice(dados)
    for item in dados["respostas"]:
        assert set(item) == {"id", "fragmentos"}
        for frag in item["fragmentos"]:
            assert set(frag) == {"id"}


def test_nao_ha_estado_entre_chamadas():
    primeiro = indice(resposta("R01", "F1"))
    segundo = indice(resposta("R01", "F1"))
    assert derivar_tokens_do_indice(primeiro) == ("R01/F1",)
    assert derivar_tokens_do_indice(segundo) == ("R01/F1",)
    assert derivar_tokens_do_indice(primeiro) == ("R01/F1",)


def test_falha_repetida_devolve_a_mesma_mensagem():
    caso = {"respostas": [{"id": "R01", "fragmentos": []}]}
    mensagens = set()
    for _ in range(3):
        with pytest.raises(ProjecaoDeIdentidadeInvalida) as erro:
            derivar_tokens_do_indice(caso)
        mensagens.add(str(erro.value))
    assert len(mensagens) == 1


# ---------------------------------------------------------------------------
# L. O indice real continua inexistente
# ---------------------------------------------------------------------------


def test_o_indice_real_continua_inexistente():
    assert not (RAIZ / "knowledge" / "indice-respostas-aprovadas.yaml").exists()


def test_a_forma_do_dominio_e_compativel_com_o_lado_do_markdown():
    # Os dois lados de `C-A1-B3` / `C-A1-B4` usam o mesmo token `<Rxx>/<id>`
    # (`C-A5-T4`). Isto confere **apenas a forma**; nenhuma bijeção é executada
    # aqui, e nenhuma correspondência real é construída.
    tokens = derivar_tokens_do_indice(DADOS_ESTAVEIS)
    for token in tokens:
        rxx, separador, identificador = token.partition("/")
        assert separador == "/"
        assert len(rxx) == 3 and rxx[0] == "R" and rxx[1:].isascii()
        assert identificador[0] == "F" and identificador[1:].isascii()

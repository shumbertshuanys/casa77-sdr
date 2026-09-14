"""Montagem canônica de uma emissão — `ResultadoComposicao` → `RespostaMontada`.

Esta suíte exercita a fronteira sobre **textos e tokens sintéticos**. **Zero
valor comercial** é reproduzido: nenhum preço, capacidade, horário, prazo,
percentual, quantidade ou frase aprovada aparece no código — nem o corpo textual
de fragmento algum. Nenhuma consulta ao corpus é necessária nem feita.
"""

from __future__ import annotations

import ast
import copy
import re
from pathlib import Path

import pytest

from casa77_sdr.response_assembly import (
    MontagemRespostaNaoAvaliavel,
    RespostaMontada,
    montar_resposta_final,
)
from casa77_sdr.response_composition import (
    OrigemValor,
    ResultadoComposicao,
    TextoEmitivel,
)

RAIZ = Path(__file__).resolve().parents[1]
MODULO_MF = RAIZ / "src" / "casa77_sdr" / "response_assembly.py"

SEPARADOR = "\n\n"

# Identificadores **sintéticos**: `Rxx` fora do corpus vigente, usados apenas
# como referência estrutural opaca. A fronteira não consulta o índice.
A = "R97/F1"
B = "R98/F1"
C = "R99/F2"

# Textos **sintéticos e opacos**. Não são texto aprovado nem o imitam.
TA = "alfa"
TB = "bravo"
TC = "charlie"


def _emitivel(
    token: str,
    texto: str,
    origens: tuple[OrigemValor, ...] = (),
) -> TextoEmitivel:
    rxx, fragmento_id = token.split("/")
    return TextoEmitivel(token, rxx, fragmento_id, origens, texto)


def _composicao(*pares: tuple[str, str]) -> ResultadoComposicao:
    return ResultadoComposicao(
        textos_emitiveis=tuple(_emitivel(token, texto) for token, texto in pares)
    )


def _categoria(excecao: MontagemRespostaNaoAvaliavel) -> str:
    return str(excecao).split(":", 1)[0]


# ---------------------------------------------------------------------------
# MF-T1 — uma unidade


def test_mf_t1_uma_unidade_sai_literalmente_igual() -> None:
    montada = montar_resposta_final(_composicao((A, TA)))

    assert montada.texto == TA
    assert montada.tokens == (A,)


def test_mf_t1_uma_unidade_nao_ganha_separador() -> None:
    montada = montar_resposta_final(_composicao((A, TA)))

    assert SEPARADOR not in montada.texto


def test_mf_t1_devolve_o_tipo_canonico() -> None:
    assert type(montar_resposta_final(_composicao((A, TA)))) is RespostaMontada


# ---------------------------------------------------------------------------
# MF-T2 — duas unidades


def test_mf_t2_duas_unidades_unidas_pelo_separador() -> None:
    montada = montar_resposta_final(_composicao((A, TA), (B, TB)))

    assert montada.texto == TA + SEPARADOR + TB


def test_mf_t2_separador_nao_aparece_nas_pontas() -> None:
    montada = montar_resposta_final(_composicao((A, TA), (B, TB)))

    assert not montada.texto.startswith("\n")
    assert not montada.texto.endswith("\n")


def test_mf_t2_exatamente_uma_ocorrencia_entre_duas_unidades() -> None:
    montada = montar_resposta_final(_composicao((A, TA), (B, TB)))

    assert montada.texto.count(SEPARADOR) == 1
    assert "\n\n\n" not in montada.texto


def test_mf_t2_equivale_ao_join_canonico() -> None:
    composicao = _composicao((A, TA), (B, TB))

    montada = montar_resposta_final(composicao)

    assert montada.texto == SEPARADOR.join(
        item.texto for item in composicao.textos_emitiveis
    )


# ---------------------------------------------------------------------------
# MF-T3 — três unidades preservam a ordem


def test_mf_t3_tres_unidades_preservam_a_ordem() -> None:
    montada = montar_resposta_final(_composicao((A, TA), (B, TB), (C, TC)))

    assert montada.texto == TA + SEPARADOR + TB + SEPARADOR + TC


def test_mf_t3_ordem_recebida_nao_e_reordenada() -> None:
    """A ordem de saída é a **recebida**, jamais a lexical."""
    montada = montar_resposta_final(_composicao((C, TC), (A, TA), (B, TB)))

    assert montada.texto == TC + SEPARADOR + TA + SEPARADOR + TB
    assert montada.tokens == (C, A, B)


def test_mf_t3_cardinalidade_preservada() -> None:
    montada = montar_resposta_final(_composicao((A, TA), (B, TB), (C, TC)))

    assert montada.texto.count(SEPARADOR) == 2
    assert len(montada.tokens) == 3


def test_mf_t3_textos_identicos_nao_sao_deduplicados() -> None:
    """Dois tokens distintos com o **mesmo** texto produzem **duas** unidades."""
    montada = montar_resposta_final(_composicao((A, TA), (B, TA)))

    assert montada.texto == TA + SEPARADOR + TA
    assert montada.tokens == (A, B)


# ---------------------------------------------------------------------------
# MF-T4 — proveniência: tokens na mesma ordem dos textos


def test_mf_t4_tokens_na_mesma_ordem_dos_textos() -> None:
    composicao = _composicao((B, TB), (C, TC), (A, TA))

    montada = montar_resposta_final(composicao)

    assert montada.tokens == tuple(
        item.token for item in composicao.textos_emitiveis
    )


def test_mf_t4_tokens_e_uma_tupla_de_str_exatas() -> None:
    montada = montar_resposta_final(_composicao((A, TA), (B, TB)))

    assert type(montada.tokens) is tuple
    for token in montada.tokens:
        assert type(token) is str


def test_mf_t4_nenhum_token_acrescentado_ou_removido() -> None:
    montada = montar_resposta_final(_composicao((A, TA), (B, TB), (C, TC)))

    assert montada.tokens == (A, B, C)


# ---------------------------------------------------------------------------
# MF-T5 — cardinalidade zero fecha


def test_mf_t5_zero_unidades_fecha() -> None:
    with pytest.raises(MontagemRespostaNaoAvaliavel) as erro:
        montar_resposta_final(ResultadoComposicao(textos_emitiveis=()))

    assert _categoria(erro.value) == "cardinalidade_vazia"


def test_mf_t5_zero_unidades_nao_devolve_texto_vazio() -> None:
    """Composição sem unidades **não** é emissão vazia: é erro de contrato."""
    with pytest.raises(MontagemRespostaNaoAvaliavel):
        montar_resposta_final(ResultadoComposicao(textos_emitiveis=()))


def test_mf_t5_fronteira_nao_conhece_sem_emissao() -> None:
    assert "SEM_EMISSAO" not in _codigo_sem_prosa(MODULO_MF)


# ---------------------------------------------------------------------------
# MF-T6 — tipo inválido da composição


@pytest.mark.parametrize(
    "invalida",
    [
        None,
        (),
        (_emitivel(A, TA),),
        [],
        "",
        0,
        {"textos_emitiveis": ()},
        object(),
    ],
    ids=[
        "nulo",
        "tupla_vazia",
        "tupla_de_emitiveis",
        "lista",
        "texto",
        "inteiro",
        "dicionario",
        "objeto",
    ],
)
def test_mf_t6_composicao_de_tipo_invalido_fecha(invalida: object) -> None:
    with pytest.raises(MontagemRespostaNaoAvaliavel) as erro:
        montar_resposta_final(invalida)

    assert str(erro.value) == "tipo_invalido: composicao"


def test_mf_t6_subclasse_de_composicao_nao_e_forma_canonica() -> None:
    class Derivada(ResultadoComposicao):
        pass

    derivada = Derivada(textos_emitiveis=(_emitivel(A, TA),))

    with pytest.raises(MontagemRespostaNaoAvaliavel) as erro:
        montar_resposta_final(derivada)

    assert str(erro.value) == "tipo_invalido: composicao"


# ---------------------------------------------------------------------------
# MF-T7 — `textos_emitiveis` não-tupla


@pytest.mark.parametrize(
    "colecao",
    [
        [_emitivel(A, TA)],
        None,
        _emitivel(A, TA),
        "",
        {A: TA},
        iter(()),
    ],
    ids=["lista", "nulo", "emitivel", "texto", "dicionario", "gerador"],
)
def test_mf_t7_colecao_nao_tupla_fecha(colecao: object) -> None:
    composicao = ResultadoComposicao(textos_emitiveis=colecao)

    with pytest.raises(MontagemRespostaNaoAvaliavel) as erro:
        montar_resposta_final(composicao)

    assert str(erro.value) == "tipo_invalido: composicao.textos_emitiveis"


def test_mf_t7_colecao_nao_tupla_precede_a_cardinalidade() -> None:
    """Lista **vazia** fecha por tipo, não por cardinalidade."""
    with pytest.raises(MontagemRespostaNaoAvaliavel) as erro:
        montar_resposta_final(ResultadoComposicao(textos_emitiveis=[]))

    assert _categoria(erro.value) == "tipo_invalido"


# ---------------------------------------------------------------------------
# MF-T8 — item não canônico


@pytest.mark.parametrize(
    "item",
    [
        None,
        (A, TA),
        TA,
        0,
        object(),
        {"token": A, "texto": TA},
    ],
    ids=["nulo", "tupla", "texto", "inteiro", "objeto", "dicionario"],
)
def test_mf_t8_item_nao_canonico_fecha(item: object) -> None:
    composicao = ResultadoComposicao(textos_emitiveis=(item,))

    with pytest.raises(MontagemRespostaNaoAvaliavel) as erro:
        montar_resposta_final(composicao)

    assert str(erro.value) == "tipo_invalido: composicao.textos_emitiveis.item"


def test_mf_t8_item_invalido_no_fim_tambem_fecha() -> None:
    composicao = ResultadoComposicao(
        textos_emitiveis=(_emitivel(A, TA), _emitivel(B, TB), None)
    )

    with pytest.raises(MontagemRespostaNaoAvaliavel) as erro:
        montar_resposta_final(composicao)

    assert str(erro.value) == "tipo_invalido: composicao.textos_emitiveis.item"


# ---------------------------------------------------------------------------
# MF-T9 — subclasse de `TextoEmitivel`


def test_mf_t9_subclasse_de_emitivel_nao_e_forma_canonica() -> None:
    class Derivado(TextoEmitivel):
        pass

    derivado = Derivado(A, "R97", "F1", (), TA)
    composicao = ResultadoComposicao(textos_emitiveis=(derivado,))

    with pytest.raises(MontagemRespostaNaoAvaliavel) as erro:
        montar_resposta_final(composicao)

    assert str(erro.value) == "tipo_invalido: composicao.textos_emitiveis.item"


# ---------------------------------------------------------------------------
# MF-T10 — `token` não é `str` exata


class _TokenDerivado(str):
    pass


@pytest.mark.parametrize(
    "token",
    [None, 0, (), _TokenDerivado(A)],
    ids=["nulo", "inteiro", "tupla", "subclasse_de_str"],
)
def test_mf_t10_token_nao_str_exata_fecha(token: object) -> None:
    emitivel = TextoEmitivel(token, "R97", "F1", (), TA)
    composicao = ResultadoComposicao(textos_emitiveis=(emitivel,))

    with pytest.raises(MontagemRespostaNaoAvaliavel) as erro:
        montar_resposta_final(composicao)

    assert str(erro.value) == "tipo_invalido: composicao.textos_emitiveis.item"


# ---------------------------------------------------------------------------
# MF-T11 — `texto` não é `str` exata


class _TextoDerivado(str):
    pass


@pytest.mark.parametrize(
    "texto",
    [None, 0, (), _TextoDerivado(TA)],
    ids=["nulo", "inteiro", "tupla", "subclasse_de_str"],
)
def test_mf_t11_texto_nao_str_exata_fecha(texto: object) -> None:
    emitivel = TextoEmitivel(A, "R97", "F1", (), texto)
    composicao = ResultadoComposicao(textos_emitiveis=(emitivel,))

    with pytest.raises(MontagemRespostaNaoAvaliavel) as erro:
        montar_resposta_final(composicao)

    assert str(erro.value) == "tipo_invalido: composicao.textos_emitiveis.item"


# ---------------------------------------------------------------------------
# MF-T12 — token duplicado


def test_mf_t12_token_duplicado_adjacente_fecha() -> None:
    with pytest.raises(MontagemRespostaNaoAvaliavel) as erro:
        montar_resposta_final(_composicao((A, TA), (A, TB)))

    assert str(erro.value) == "duplicidade: composicao.textos_emitiveis.item"


def test_mf_t12_token_duplicado_nao_adjacente_fecha() -> None:
    with pytest.raises(MontagemRespostaNaoAvaliavel) as erro:
        montar_resposta_final(_composicao((A, TA), (B, TB), (A, TC)))

    assert str(erro.value) == "duplicidade: composicao.textos_emitiveis.item"


def test_mf_t12_duplicidade_nao_e_corrigida_em_silencio() -> None:
    """Repetição **não** vira deduplicação: ela fecha."""
    with pytest.raises(MontagemRespostaNaoAvaliavel):
        montar_resposta_final(_composicao((A, TA), (A, TA)))


# ---------------------------------------------------------------------------
# MF-T13 — zero mutação das entradas


def test_mf_t13_entrada_nao_e_mutada() -> None:
    composicao = _composicao((A, TA), (B, TB), (C, TC))
    antes = copy.deepcopy(composicao)

    montar_resposta_final(composicao)

    assert composicao == antes


def test_mf_t13_entrada_nao_e_mutada_quando_fecha() -> None:
    composicao = ResultadoComposicao(
        textos_emitiveis=(_emitivel(A, TA), None)
    )
    antes = copy.deepcopy(composicao)

    with pytest.raises(MontagemRespostaNaoAvaliavel):
        montar_resposta_final(composicao)

    assert composicao == antes


def test_mf_t13_tupla_de_saida_nao_e_a_de_entrada() -> None:
    composicao = _composicao((A, TA), (B, TB))

    montada = montar_resposta_final(composicao)

    assert montada.tokens is not composicao.textos_emitiveis


# ---------------------------------------------------------------------------
# MF-T14 — determinismo


def test_mf_t14_chamadas_repetidas_produzem_o_mesmo_resultado() -> None:
    composicao = _composicao((C, TC), (A, TA), (B, TB))

    primeira = montar_resposta_final(composicao)
    segunda = montar_resposta_final(composicao)

    assert primeira == segunda
    assert primeira.texto == segunda.texto


def test_mf_t14_composicoes_equivalentes_produzem_o_mesmo_resultado() -> None:
    primeira = montar_resposta_final(_composicao((A, TA), (B, TB)))
    segunda = montar_resposta_final(_composicao((A, TA), (B, TB)))

    assert primeira == segunda
    assert primeira.texto == segunda.texto


# ---------------------------------------------------------------------------
# MF-T15 — quebra de linha já presente não é normalizada


def test_mf_t15_texto_terminado_em_quebra_nao_e_normalizado() -> None:
    montada = montar_resposta_final(_composicao((A, "A\n"), (B, "B")))

    assert montada.texto == "A\n\n\nB"


def test_mf_t15_texto_iniciado_por_quebra_nao_e_normalizado() -> None:
    montada = montar_resposta_final(_composicao((A, "A"), (B, "\nB")))

    assert montada.texto == "A\n\n\nB"


def test_mf_t15_quebra_interna_permanece_literal() -> None:
    montada = montar_resposta_final(_composicao((A, "A\nB"), (B, "C")))

    assert montada.texto == "A\nB\n\nC"


def test_mf_t15_unidade_de_texto_vazio_permanece_vazia() -> None:
    """Texto vazio é conteúdo recebido, não ausência de unidade."""
    montada = montar_resposta_final(_composicao((A, ""), (B, TB)))

    assert montada.texto == SEPARADOR + TB
    assert montada.tokens == (A, B)


# ---------------------------------------------------------------------------
# MF-T16 — espaços permanecem literais


def test_mf_t16_espaco_final_permanece() -> None:
    montada = montar_resposta_final(_composicao((A, "alfa  "), (B, TB)))

    assert montada.texto == "alfa  " + SEPARADOR + TB


def test_mf_t16_espaco_inicial_permanece() -> None:
    montada = montar_resposta_final(_composicao((A, TA), (B, "  bravo")))

    assert montada.texto == TA + SEPARADOR + "  bravo"


def test_mf_t16_tabulacao_e_espaco_nao_sao_convertidos() -> None:
    montada = montar_resposta_final(_composicao((A, "\talfa"), (B, TB)))

    assert montada.texto == "\talfa" + SEPARADOR + TB


# ---------------------------------------------------------------------------
# MF-T17 — conteúdo semelhante a *placeholder* permanece literal


def test_mf_t17_placeholder_no_conteudo_nao_e_reinterpretado() -> None:
    montada = montar_resposta_final(_composicao((A, "{{algo}}"), (B, TB)))

    assert montada.texto == "{{algo}}" + SEPARADOR + TB


def test_mf_t17_chaves_soltas_permanecem_literais() -> None:
    montada = montar_resposta_final(_composicao((A, "{alfa}"), (B, "}}x{{")))

    assert montada.texto == "{alfa}" + SEPARADOR + "}}x{{"


def test_mf_t17_texto_que_contem_o_separador_permanece_literal() -> None:
    montada = montar_resposta_final(_composicao((A, "a\n\nb"), (B, TB)))

    assert montada.texto == "a\n\nb" + SEPARADOR + TB


# ---------------------------------------------------------------------------
# MF-T18 — `repr` não carrega o texto


def test_mf_t18_repr_nao_contem_o_texto() -> None:
    montada = montar_resposta_final(_composicao((A, TA), (B, TB)))

    assert TA not in repr(montada)
    assert TB not in repr(montada)
    assert "texto" not in repr(montada)


def test_mf_t18_repr_contem_os_tokens() -> None:
    """Tokens são identificadores estruturais: eles podem aparecer."""
    montada = montar_resposta_final(_composicao((A, TA), (B, TB)))

    assert A in repr(montada)
    assert B in repr(montada)


def test_mf_t18_dto_e_frozen_e_slots() -> None:
    montada = montar_resposta_final(_composicao((A, TA)))

    with pytest.raises(Exception):
        montada.texto = TB  # type: ignore[misc]
    assert not hasattr(montada, "__dict__")


# ---------------------------------------------------------------------------
# MF-T19 / MF-T20 — isolamento estrutural


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

    *Docstrings* e comentários saem: a negativa em prosa do próprio módulo — que
    **nomeia** o que ele não faz — não pode ser contada como se ele conhecesse a
    matéria. O que resta é o código que de fato roda.
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


def test_mf_t19_importa_somente_o_necessario() -> None:
    assert _modulos_importados(MODULO_MF) == {
        "__future__",
        "dataclasses",
        "casa77_sdr.response_composition",
    }


@pytest.mark.parametrize(
    "proibido",
    [
        "casa77_sdr.response_index",
        "casa77_sdr.response_index_load",
        "casa77_sdr.response_index_status",
        "casa77_sdr.response_index_tokens",
        "casa77_sdr.emission_projection",
        "casa77_sdr.fact_selection",
        "casa77_sdr.response_placeholder",
        "casa77_sdr.response_format",
        "casa77_sdr.response_yaml_resolve",
        "casa77_sdr.response_consistency",
        "casa77_sdr.state_machine",
        "casa77_sdr.interpretation",
        "casa77_sdr.qualification",
        "casa77_sdr.persistence",
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
        "textwrap",
        "unicodedata",
    ],
)
def test_mf_t20_nao_importa_fronteira_proibida(proibido: str) -> None:
    assert proibido not in _modulos_importados(MODULO_MF)


def test_mf_t20_nao_abre_arquivo_nem_consulta_corpus() -> None:
    chamados: set[str] = set()
    for no in ast.walk(_arvore(MODULO_MF)):
        if not isinstance(no, ast.Call):
            continue
        alvo = no.func
        if isinstance(alvo, ast.Name):
            chamados.add(alvo.id)
        elif isinstance(alvo, ast.Attribute):
            chamados.add(alvo.attr)

    for proibido in (
        "open",
        "read_text",
        "carregar_indice",
        "validar_indice",
        "consultar_status",
        "derivar_tokens_do_indice",
        "decompor_template",
        "safe_load",
        "sorted",
        "strip",
        "rstrip",
        "lstrip",
        "replace",
        "format",
        "format_map",
        "lower",
        "upper",
        "casefold",
        "normalize",
        "compile",
        "sub",
        "now",
        "today",
        "getenv",
    ):
        assert proibido not in chamados


def test_mf_t20_superficie_publica_e_minima() -> None:
    import casa77_sdr.response_assembly as modulo

    assert sorted(modulo.__all__) == [
        "MontagemRespostaNaoAvaliavel",
        "RespostaMontada",
        "montar_resposta_final",
    ]


def test_mf_t20_nao_conhece_vocabulario_de_montante_nem_de_jusante() -> None:
    """Nenhum objeto de domínio alheio é nomeado na fronteira.

    A prova de que `knowledge/**` não é **acessado** é a de AST, acima; aqui o
    que se verifica é ausência de **vocabulário** — e por isso a negativa em
    prosa do próprio módulo não é contada.
    """
    fonte = _codigo_sem_prosa(MODULO_MF).casefold()

    for termo in (
        "PerguntaComercial",
        "AssuntoComercial",
        "AcaoMaquina",
        "MaquinaEstados",
        "ValidadorResposta",
        "OrquestradorMotor",
        "PlanoEmissao",
        "E15",
        "E12",
        "handoff",
        "qualificacao",
        "yaml",
    ):
        assert termo.casefold() not in fonte


def test_mf_t20_separador_e_constante_literal() -> None:
    """`PC-3` é literal: o separador não é derivado, escolhido nem configurado."""
    import casa77_sdr.response_assembly as modulo

    assert modulo._SEPARADOR == SEPARADOR


# ---------------------------------------------------------------------------
# MF-T21 — exceções não vazam conteúdo


_FORMA_CANONICA = re.compile(
    r"^(tipo_invalido|duplicidade|cardinalidade_vazia): "
    r"(composicao|composicao\.textos_emitiveis|composicao\.textos_emitiveis\.item)$"
)


def _fecha(chamada: object) -> MontagemRespostaNaoAvaliavel:
    with pytest.raises(MontagemRespostaNaoAvaliavel) as erro:
        montar_resposta_final(chamada)
    return erro.value


@pytest.mark.parametrize(
    "chamada",
    [
        None,
        ResultadoComposicao(textos_emitiveis=()),
        ResultadoComposicao(textos_emitiveis=[_emitivel(A, TA)]),
        ResultadoComposicao(textos_emitiveis=(None,)),
        ResultadoComposicao(
            textos_emitiveis=(_emitivel(A, TA), _emitivel(A, TB))
        ),
    ],
    ids=[
        "composicao_invalida",
        "cardinalidade_vazia",
        "colecao_invalida",
        "item_invalido",
        "duplicidade",
    ],
)
def test_mf_t21_mensagem_tem_forma_canonica(chamada: object) -> None:
    assert _FORMA_CANONICA.match(str(_fecha(chamada))) is not None


@pytest.mark.parametrize(
    "chamada",
    [
        ResultadoComposicao(textos_emitiveis=(_emitivel(A, TA), None)),
        ResultadoComposicao(
            textos_emitiveis=(_emitivel(A, TA), _emitivel(A, TB))
        ),
    ],
    ids=["item_invalido", "duplicidade"],
)
def test_mf_t21_mensagem_nao_ecoa_token_nem_texto(chamada: object) -> None:
    mensagem = str(_fecha(chamada))

    for conteudo in (A, B, C, TA, TB, TC, "R97", "F1"):
        assert conteudo not in mensagem


def test_mf_t21_excecao_e_propria_da_fronteira() -> None:
    erro = _fecha(None)

    assert type(erro) is MontagemRespostaNaoAvaliavel
    assert isinstance(erro, Exception)


# ---------------------------------------------------------------------------
# MF-T22 — nenhum resultado parcial


def test_mf_t22_erro_no_ultimo_item_nao_produz_parcial() -> None:
    """Dois itens válidos antes do inválido **não** viram resposta."""
    composicao = ResultadoComposicao(
        textos_emitiveis=(_emitivel(A, TA), _emitivel(B, TB), None)
    )

    with pytest.raises(MontagemRespostaNaoAvaliavel):
        montar_resposta_final(composicao)


def test_mf_t22_duplicidade_no_fim_nao_produz_parcial() -> None:
    composicao = _composicao((A, TA), (B, TB), (A, TC))

    with pytest.raises(MontagemRespostaNaoAvaliavel):
        montar_resposta_final(composicao)


def test_mf_t22_nada_e_capturado_na_fronteira() -> None:
    for no in ast.walk(_arvore(MODULO_MF)):
        assert not isinstance(no, (ast.Try, ast.ExceptHandler))


def test_mf_t22_saida_e_completa_ou_inexistente() -> None:
    """Sucesso carrega **todas** as unidades; fracasso não carrega nenhuma."""
    montada = montar_resposta_final(_composicao((A, TA), (B, TB), (C, TC)))

    assert len(montada.tokens) == 3
    assert montada.texto.count(SEPARADOR) == 2

"""`ValidadorResposta` — gate final de integridade textual da emissão canônica.

Esta suíte exercita a fronteira sobre **textos sintéticos**. **Zero valor
comercial** é reproduzido: nenhum preço, capacidade, horário, prazo, percentual,
quantidade ou frase aprovada aparece no código — nem o corpo textual de fragmento
algum. **Nenhum arquivo de `knowledge/` é aberto.**
"""

from __future__ import annotations

import ast
import copy
import re
from pathlib import Path

import pytest

from casa77_sdr.response_assembly import RespostaMontada
from casa77_sdr.response_validation import (
    MotivoValidacaoResposta,
    ResultadoValidacaoResposta,
    ValidacaoRespostaNaoAvaliavel,
    validar_resposta_final,
)

RAIZ = Path(__file__).resolve().parents[1]
MODULO_VR = RAIZ / "src" / "casa77_sdr" / "response_validation.py"

# Identificadores **sintéticos**: `Rxx` fora do corpus vigente, usados apenas
# como referência estrutural opaca. A fronteira não os lê.
A = "R97/F1"
B = "R98/F1"

# Textos **sintéticos e opacos**. Não são texto aprovado nem o imitam.
TA = "alfa"
TB = "bravo"
MONTADO = TA + "\n\n" + TB


def _montada(texto: str = MONTADO, tokens: tuple[str, ...] = (A, B)) -> RespostaMontada:
    return RespostaMontada(tokens, texto)


def _rejeita(candidato: str) -> ResultadoValidacaoResposta:
    return validar_resposta_final(candidato, _montada())


# ---------------------------------------------------------------------------
# VR-T1 — textos iguais aprovam


def test_vr_t1_textos_iguais_aprovam() -> None:
    resultado = validar_resposta_final(MONTADO, _montada())

    assert resultado.aprovado is True
    assert resultado.motivo is MotivoValidacaoResposta.APROVADO


def test_vr_t1_uma_unica_unidade_aprova() -> None:
    resultado = validar_resposta_final(TA, _montada(TA, (A,)))

    assert resultado == ResultadoValidacaoResposta(
        True, MotivoValidacaoResposta.APROVADO
    )


def test_vr_t1_texto_vazio_identico_aprova() -> None:
    """Vazio contra vazio é igualdade: a fronteira não julga conteúdo."""
    assert validar_resposta_final("", _montada("", (A,))).aprovado is True


def test_vr_t1_devolve_o_tipo_canonico() -> None:
    assert type(validar_resposta_final(MONTADO, _montada())) is ResultadoValidacaoResposta


def test_vr_t1_aprovado_equivale_ao_motivo() -> None:
    aprovado = validar_resposta_final(MONTADO, _montada())
    rejeitado = validar_resposta_final(MONTADO + "x", _montada())

    for r in (aprovado, rejeitado):
        assert r.aprovado is (r.motivo is MotivoValidacaoResposta.APROVADO)


# ---------------------------------------------------------------------------
# VR-T2 — um caractere diferente


@pytest.mark.parametrize(
    "candidato",
    ["alfa\n\nbrava", "alfo\n\nbravo", "alfa\n\nbrav", "alfa\n\nbravoo"],
    ids=["ultimo", "do_meio", "a_menos", "a_mais"],
)
def test_vr_t2_um_caractere_diferente_rejeita(candidato: str) -> None:
    resultado = _rejeita(candidato)

    assert resultado.aprovado is False
    assert resultado.motivo is MotivoValidacaoResposta.TEXTO_DIVERGENTE


# ---------------------------------------------------------------------------
# VR-T3 — espaço inicial diferente


@pytest.mark.parametrize(
    "candidato",
    [" " + MONTADO, "  " + MONTADO, "\t" + MONTADO],
    ids=["um_espaco", "dois_espacos", "tabulacao"],
)
def test_vr_t3_espaco_inicial_diferente_rejeita(candidato: str) -> None:
    resultado = _rejeita(candidato)

    assert resultado.aprovado is False
    assert resultado.motivo is MotivoValidacaoResposta.TEXTO_DIVERGENTE


# ---------------------------------------------------------------------------
# VR-T4 — espaço final diferente


@pytest.mark.parametrize(
    "candidato",
    [MONTADO + " ", MONTADO + "  ", MONTADO + "\t"],
    ids=["um_espaco", "dois_espacos", "tabulacao"],
)
def test_vr_t4_espaco_final_diferente_rejeita(candidato: str) -> None:
    resultado = _rejeita(candidato)

    assert resultado.aprovado is False
    assert resultado.motivo is MotivoValidacaoResposta.TEXTO_DIVERGENTE


# ---------------------------------------------------------------------------
# VR-T5 — newline diferente


@pytest.mark.parametrize(
    "candidato",
    ["alfa\nbravo", "alfa\n\n\nbravo", MONTADO + "\n", "\n" + MONTADO],
    ids=["uma", "tres", "final", "inicial"],
)
def test_vr_t5_newline_diferente_rejeita(candidato: str) -> None:
    resultado = _rejeita(candidato)

    assert resultado.aprovado is False
    assert resultado.motivo is MotivoValidacaoResposta.TEXTO_DIVERGENTE


# ---------------------------------------------------------------------------
# VR-T6 — "\n" versus "\r\n"


def test_vr_t6_crlf_no_separador_rejeita() -> None:
    resultado = _rejeita("alfa\r\n\r\nbravo")

    assert resultado.aprovado is False
    assert resultado.motivo is MotivoValidacaoResposta.TEXTO_DIVERGENTE


def test_vr_t6_crlf_dentro_da_unidade_rejeita() -> None:
    montada = _montada("alfa\nbravo", (A,))

    resultado = validar_resposta_final("alfa\r\nbravo", montada)

    assert resultado.aprovado is False
    assert resultado.motivo is MotivoValidacaoResposta.TEXTO_DIVERGENTE


def test_vr_t6_cr_solitario_rejeita() -> None:
    resultado = _rejeita("alfa\r\rbravo")

    assert resultado.aprovado is False


# ---------------------------------------------------------------------------
# VR-T7 — caixa diferente


@pytest.mark.parametrize(
    "candidato",
    ["Alfa\n\nbravo", "alfa\n\nBravo", "ALFA\n\nBRAVO", "alfA\n\nbravo"],
    ids=["inicial", "segunda", "tudo", "final"],
)
def test_vr_t7_caixa_diferente_rejeita(candidato: str) -> None:
    resultado = _rejeita(candidato)

    assert resultado.aprovado is False
    assert resultado.motivo is MotivoValidacaoResposta.TEXTO_DIVERGENTE


# ---------------------------------------------------------------------------
# VR-T8 — pontuação diferente


@pytest.mark.parametrize(
    "candidato",
    ["alfa\n\nbravo.", "alfa,\n\nbravo", "alfa!\n\nbravo", "alfa\n\nbravo?"],
    ids=["ponto", "virgula", "exclamacao", "interrogacao"],
)
def test_vr_t8_pontuacao_diferente_rejeita(candidato: str) -> None:
    resultado = _rejeita(candidato)

    assert resultado.aprovado is False
    assert resultado.motivo is MotivoValidacaoResposta.TEXTO_DIVERGENTE


# ---------------------------------------------------------------------------
# VR-T9 — Unicode visualmente semelhante, texto distinto


@pytest.mark.parametrize(
    "par",
    [
        # Pontos de codigo escritos como *escape*: nenhum editor os normaliza.
        ("á", "á"),        # NFC x NFD do mesmo grafema
        ("alfa", "alfa​"),       # espaco de largura zero
        ("alfa", "alfa "),       # espaco nao separavel
        ("alfa-x", "alfa‐x"),    # hifen ASCII x hifen tipografico
        ("alfa", "﻿alfa"),       # BOM
        ("alfa", "аlfa"),        # 'a' cirilico homoglifo
    ],
    ids=["nfc_x_nfd", "zero_width", "nbsp", "hifen", "bom", "homoglifo"],
)
def test_vr_t9_unicode_semelhante_mas_distinto_rejeita(par: tuple[str, str]) -> None:
    montado, candidato = par

    resultado = validar_resposta_final(candidato, _montada(montado, (A,)))

    assert resultado.aprovado is False
    assert resultado.motivo is MotivoValidacaoResposta.TEXTO_DIVERGENTE


def test_vr_t9_identidade_unicode_exata_aprova() -> None:
    """O contraexemplo: o **mesmo** ponto de código aprova normalmente."""
    texto = "álfa"

    assert validar_resposta_final(texto, _montada(texto, (A,))).aprovado is True


# ---------------------------------------------------------------------------
# VR-T10 — candidato não `str`


@pytest.mark.parametrize(
    "candidato",
    [None, 0, (), [], {}, b"alfa", object(), MONTADO.encode("utf-8")],
    ids=[
        "nulo",
        "inteiro",
        "tupla",
        "lista",
        "dicionario",
        "bytes",
        "objeto",
        "bytes_do_texto",
    ],
)
def test_vr_t10_candidato_nao_str_levanta(candidato: object) -> None:
    with pytest.raises(ValidacaoRespostaNaoAvaliavel) as erro:
        validar_resposta_final(candidato, _montada())

    assert str(erro.value) == "tipo_invalido: texto_candidato"


# ---------------------------------------------------------------------------
# VR-T11 — subclasse de `str`


class _TextoDerivado(str):
    pass


def test_vr_t11_subclasse_de_str_levanta() -> None:
    with pytest.raises(ValidacaoRespostaNaoAvaliavel) as erro:
        validar_resposta_final(_TextoDerivado(MONTADO), _montada())

    assert str(erro.value) == "tipo_invalido: texto_candidato"


def test_vr_t11_subclasse_de_str_nao_vira_aprovacao_silenciosa() -> None:
    """Mesmo com conteúdo idêntico, subclasse fecha."""
    with pytest.raises(ValidacaoRespostaNaoAvaliavel):
        validar_resposta_final(_TextoDerivado(MONTADO), _montada())


# ---------------------------------------------------------------------------
# VR-T12 — `montada` não `RespostaMontada`


@pytest.mark.parametrize(
    "montada",
    [None, MONTADO, (A, B), [], {}, 0, object(), ((A, B), MONTADO)],
    ids=[
        "nulo",
        "texto",
        "tupla_de_tokens",
        "lista",
        "dicionario",
        "inteiro",
        "objeto",
        "tupla_par",
    ],
)
def test_vr_t12_montada_nao_canonica_levanta(montada: object) -> None:
    with pytest.raises(ValidacaoRespostaNaoAvaliavel) as erro:
        validar_resposta_final(MONTADO, montada)

    assert str(erro.value) == "tipo_invalido: montada"


# ---------------------------------------------------------------------------
# VR-T13 — subclasse de `RespostaMontada`


def test_vr_t13_subclasse_de_montada_nao_e_aceita() -> None:
    class Derivada(RespostaMontada):
        pass

    with pytest.raises(ValidacaoRespostaNaoAvaliavel) as erro:
        validar_resposta_final(MONTADO, Derivada((A, B), MONTADO))

    assert str(erro.value) == "tipo_invalido: montada"


def test_vr_t13_precedencia_candidato_antes_de_montada() -> None:
    with pytest.raises(ValidacaoRespostaNaoAvaliavel) as erro:
        validar_resposta_final(None, None)

    assert str(erro.value) == "tipo_invalido: texto_candidato"


# ---------------------------------------------------------------------------
# VR-7 — forma estrutural interna inválida também fecha


class _SempreIgual:
    """Objeto que afirma ser igual a **qualquer** coisa.

    `str.__eq__` devolve `NotImplemented` diante do que não é `str`, e Python
    então pergunta ao **outro** operando. Sem a validação estrutural do campo
    `texto`, este objeto decidiria sozinho o veredito da fronteira.
    """

    def __eq__(self, outro: object) -> bool:
        return True

    def __hash__(self) -> int:
        return 0


class _EqExplode:
    """Objeto cujo `__eq__` **falha ruidosamente** se for chamado."""

    def __eq__(self, outro: object) -> bool:
        raise AssertionError("o comparador externo NAO pode ser chamado")

    def __hash__(self) -> int:
        return 0


@pytest.mark.parametrize(
    "texto",
    [None, 0, (), [], b"alfa", _TextoDerivado(MONTADO)],
    ids=["nulo", "inteiro", "tupla", "lista", "bytes", "subclasse_de_str"],
)
def test_vr_7_montada_com_texto_nao_str_levanta(texto: object) -> None:
    montada = RespostaMontada((A,), texto)  # type: ignore[arg-type]

    with pytest.raises(ValidacaoRespostaNaoAvaliavel) as erro:
        validar_resposta_final(MONTADO, montada)

    assert str(erro.value) == "tipo_invalido: montada.texto"


def test_vr_7_igualdade_refletida_nao_forca_aprovacao() -> None:
    montada = RespostaMontada((A,), _SempreIgual())  # type: ignore[arg-type]

    with pytest.raises(ValidacaoRespostaNaoAvaliavel) as erro:
        validar_resposta_final("qualquer texto", montada)

    assert str(erro.value) == "tipo_invalido: montada.texto"


def test_vr_7_comparador_externo_nem_chega_a_ser_chamado() -> None:
    montada = RespostaMontada((A,), _EqExplode())  # type: ignore[arg-type]

    with pytest.raises(ValidacaoRespostaNaoAvaliavel) as erro:
        validar_resposta_final(MONTADO, montada)

    assert str(erro.value) == "tipo_invalido: montada.texto"


def test_vr_7_forma_invalida_nunca_vira_divergencia() -> None:
    """`TEXTO_DIVERGENTE` é só entre duas `str` canônicas que diferem."""
    divergente = validar_resposta_final("outra coisa", _montada())
    assert divergente.motivo is MotivoValidacaoResposta.TEXTO_DIVERGENTE

    with pytest.raises(ValidacaoRespostaNaoAvaliavel):
        validar_resposta_final(MONTADO, RespostaMontada((A,), None))  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# VR-T14 / VR-T15 — resultado `frozen` e `slots`


def test_vr_t14_resultado_e_frozen() -> None:
    resultado = validar_resposta_final(MONTADO, _montada())

    with pytest.raises(Exception):
        resultado.aprovado = False  # type: ignore[misc]
    with pytest.raises(Exception):
        resultado.motivo = MotivoValidacaoResposta.TEXTO_DIVERGENTE  # type: ignore[misc]


def test_vr_t15_resultado_e_slots() -> None:
    resultado = validar_resposta_final(MONTADO, _montada())

    assert not hasattr(resultado, "__dict__")
    with pytest.raises((AttributeError, TypeError)):
        resultado.extra = 1  # type: ignore[attr-defined]


def test_vr_t15_dto_tem_exatamente_dois_campos() -> None:
    assert set(ResultadoValidacaoResposta.__dataclass_fields__) == {
        "aprovado",
        "motivo",
    }


# ---------------------------------------------------------------------------
# VR-T16 — `repr` não carrega texto


@pytest.mark.parametrize("candidato", [MONTADO, "outra coisa"], ids=["aprova", "rejeita"])
def test_vr_t16_repr_nao_carrega_o_corpo(candidato: str) -> None:
    resultado = validar_resposta_final(candidato, _montada())

    for conteudo in (MONTADO, TA, TB, "outra coisa"):
        assert conteudo not in repr(resultado)


def test_vr_t16_resultado_nao_expoe_texto_algum() -> None:
    resultado = validar_resposta_final("outra coisa", _montada())

    for atributo in ("texto", "texto_candidato", "montada", "sugestao", "diff"):
        assert not hasattr(resultado, atributo)


# ---------------------------------------------------------------------------
# VR-T17 / VR-T18 — exceção não vaza conteúdo


_FORMA_CANONICA = re.compile(
    r"^tipo_invalido: (texto_candidato|montada|montada\.texto)$"
)


@pytest.mark.parametrize(
    "chamada",
    [
        (None, None),
        (0, None),
        (MONTADO, None),
        (MONTADO, MONTADO),
        (MONTADO, RespostaMontada((A,), None)),  # type: ignore[arg-type]
    ],
    ids=["ambos", "inteiro", "montada_nula", "montada_texto", "texto_invalido"],
)
def test_vr_t17_mensagem_tem_forma_canonica(chamada: tuple[object, object]) -> None:
    candidato, montada = chamada

    with pytest.raises(ValidacaoRespostaNaoAvaliavel) as erro:
        validar_resposta_final(candidato, montada)

    assert _FORMA_CANONICA.match(str(erro.value)) is not None


def test_vr_t17_excecao_nao_vaza_o_candidato() -> None:
    candidato = _TextoDerivado("segredo sintetico do candidato")

    with pytest.raises(ValidacaoRespostaNaoAvaliavel) as erro:
        validar_resposta_final(candidato, _montada())

    assert "segredo sintetico do candidato" not in str(erro.value)
    assert str(erro.value) == "tipo_invalido: texto_candidato"


def test_vr_t18_excecao_nao_vaza_o_texto_montado() -> None:
    montada = RespostaMontada((A,), _TextoDerivado("segredo sintetico montado"))  # type: ignore[arg-type]

    with pytest.raises(ValidacaoRespostaNaoAvaliavel) as erro:
        validar_resposta_final(MONTADO, montada)

    assert "segredo sintetico montado" not in str(erro.value)
    assert str(erro.value) == "tipo_invalido: montada.texto"


def test_vr_t18_mensagem_nao_nomeia_tipo_nem_token() -> None:
    with pytest.raises(ValidacaoRespostaNaoAvaliavel) as erro:
        validar_resposta_final(MONTADO, MONTADO)

    mensagem = str(erro.value)
    for conteudo in (MONTADO, TA, TB, A, B, "R97", "str", "RespostaMontada"):
        assert conteudo not in mensagem


# ---------------------------------------------------------------------------
# VR-T19 — determinismo


def test_vr_t19_determinismo_no_sucesso_e_na_rejeicao() -> None:
    montada = _montada()

    assert validar_resposta_final(MONTADO, montada) == validar_resposta_final(
        MONTADO, montada
    )
    assert validar_resposta_final(TA, montada) == validar_resposta_final(TA, montada)


def test_vr_t19_entradas_equivalentes_produzem_o_mesmo_veredito() -> None:
    assert validar_resposta_final(MONTADO, _montada()) == validar_resposta_final(
        MONTADO, _montada()
    )


def test_vr_t19_vocabulario_de_motivos_e_fechado() -> None:
    assert [m.name for m in MotivoValidacaoResposta] == [
        "APROVADO",
        "TEXTO_DIVERGENTE",
    ]


# ---------------------------------------------------------------------------
# VR-T20 — zero mutação


@pytest.mark.parametrize("candidato", [MONTADO, TA], ids=["aprova", "rejeita"])
def test_vr_t20_montada_nao_e_mutada(candidato: str) -> None:
    montada = _montada()
    antes = copy.deepcopy(montada)

    validar_resposta_final(candidato, montada)

    assert montada == antes
    assert montada.texto == MONTADO
    assert montada.tokens == (A, B)


def test_vr_t20_montada_nao_e_mutada_quando_levanta() -> None:
    montada = _montada()
    antes = copy.deepcopy(montada)

    with pytest.raises(ValidacaoRespostaNaoAvaliavel):
        validar_resposta_final(None, montada)

    assert montada == antes


def test_vr_t20_candidato_nao_e_reescrito_para_aprovar() -> None:
    """Um candidato que só difere por espaço **continua** rejeitado."""
    assert validar_resposta_final(MONTADO + " ", _montada()).aprovado is False


# ---------------------------------------------------------------------------
# VR-T21 / VR-T22 — isolamento estrutural


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


def test_vr_t21_imports_de_producao_sao_minimos() -> None:
    assert _modulos_importados(MODULO_VR) == {
        "__future__",
        "dataclasses",
        "enum",
        "casa77_sdr.response_assembly",
    }


def test_vr_t21_superficie_publica_e_fechada() -> None:
    import casa77_sdr.response_validation as modulo

    assert sorted(modulo.__all__) == [
        "MotivoValidacaoResposta",
        "ResultadoValidacaoResposta",
        "ValidacaoRespostaNaoAvaliavel",
        "validar_resposta_final",
    ]


def test_vr_t21_nao_exportado_pelo_init() -> None:
    import casa77_sdr

    for nome in (
        "MotivoValidacaoResposta",
        "ResultadoValidacaoResposta",
        "ValidacaoRespostaNaoAvaliavel",
        "validar_resposta_final",
    ):
        assert nome not in getattr(casa77_sdr, "__all__", ())


@pytest.mark.parametrize(
    "proibido",
    [
        "casa77_sdr.response_index",
        "casa77_sdr.response_index_load",
        "casa77_sdr.response_index_status",
        "casa77_sdr.response_composition",
        "casa77_sdr.response_consistency",
        "casa77_sdr.emission_projection",
        "casa77_sdr.fact_selection",
        "casa77_sdr.response_placeholder",
        "casa77_sdr.response_yaml_resolve",
        "casa77_sdr.state_machine",
        "casa77_sdr.transition_marker",
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
        "socket",
        "subprocess",
        "unicodedata",
    ],
    ids=lambda v: v.rsplit(".", 1)[-1],
)
def test_vr_t22_nao_importa_io_llm_nem_knowledge(proibido: str) -> None:
    assert proibido not in _modulos_importados(MODULO_VR)


def test_vr_t22_zero_llm() -> None:
    fonte = _codigo_sem_prosa(MODULO_VR).casefold()

    for proibido in ("llm", "openai", "anthropic", "httpx", "requests"):
        assert proibido not in fonte
    for modulo in _modulos_importados(MODULO_VR):
        assert "llm" not in modulo.casefold()


def test_vr_t22_nao_chama_io_corpus_nem_normalizador() -> None:
    chamados: set[str] = set()
    for no in ast.walk(_arvore(MODULO_VR)):
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
        "montar_resposta_final",
        "safe_load",
        "strip",
        "lstrip",
        "rstrip",
        "lower",
        "upper",
        "casefold",
        "replace",
        "normalize",
        "compile",
        "match",
        "sub",
        "search",
        "now",
        "today",
        "getenv",
        "sorted",
    ):
        assert proibido not in chamados


def test_vr_t22_zero_vocabulario_comercial() -> None:
    """Nenhum objeto de domínio alheio é nomeado na fronteira."""
    fonte = _codigo_sem_prosa(MODULO_VR).casefold()

    for termo in (
        "FatoAutorizado",
        "TextoEmitivel",
        "ResultadoComposicao",
        "AcaoMaquina",
        "binding",
        "witness",
        "rxx",
        "status",
        "handoff",
        "qualificacao",
        "yaml",
        "E15",
        "E12",
    ):
        assert termo.casefold() not in fonte


def test_vr_t22_nada_e_capturado() -> None:
    for no in ast.walk(_arvore(MODULO_VR)):
        assert not isinstance(no, (ast.Try, ast.ExceptHandler))

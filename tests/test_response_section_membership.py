"""Testes da associação física entre instância de seção `Rxx` e fragmentos.

A fronteira entrega **exatamente** a associação que `C8` e `C12` não expõem: uma
entrada por **instância física** de `## Rxx`, com o seu `rotulo_literal` e os
tokens canônicos dos fragmentos **daquela instância**.

Estes testes provam a ordem física, a **separação entre instâncias homônimas**, a
equivalência `LF`/`CRLF`, o escopo de seção compatível com `C8`, a propagação
intacta das exceções de `C8` e `C12`, o invariante local × `C12`, o **cruzamento
obrigatório do flatten com `C8`** e a pureza do módulo de produção — e **não**
transformam em norma qualquer semântica de status, que está **fora** desta
fronteira. **Nenhum teste toca o corpus versionado**: todos os documentos são
**sintéticos**.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

import casa77_sdr
from casa77_sdr.response_header_labels import CabecalhoRxxInvalido
from casa77_sdr.response_markdown_units import (
    RepresentacaoMarcadaInvalida,
    ler_unidades_marcadas,
)
from casa77_sdr.response_section_membership import associar_fragmentos_a_secao

# ---------------------------------------------------------------------------
# Apoio
# ---------------------------------------------------------------------------

# Separador literal de `G2`: SPACE + EM DASH + SPACE, montado por ponto de
# codigo para que o teste nao dependa da forma como este arquivo foi gravado.
SEPARADOR = " " + chr(0x2014) + " "

ROTULO_ST1 = "APROVADO"
ROTULO_ST2 = "AGUARDA APROVA" + chr(0x00C7) + chr(0x00C3) + "O"
ROTULO_ST3 = "APROVADO com handoff obrigat" + chr(0x00F3) + "rio"
ROTULO_PARCIAL = "PARCIAL"

BLOCO = "> conteudo"

CAMINHO_PRODUCAO = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "casa77_sdr"
    / "response_section_membership.py"
)
CODIGO_PRODUCAO = CAMINHO_PRODUCAO.read_text(encoding="utf-8")
ARVORE_PRODUCAO = ast.parse(CODIGO_PRODUCAO)


def cabecalho(rxx="R01", titulo="Titulo", rotulo=ROTULO_ST1):
    """Linha de cabeçalho `G2` sintética."""
    return f"## {rxx}{SEPARADOR}{titulo}{SEPARADOR}{rotulo}"


def marcador(identificador="F1"):
    """Linha de marcador `C-A5` sintética."""
    return f"<!-- fragmento: {identificador} -->"


def unidade(identificador="F1"):
    """Marcador e bloco de um fragmento emitível."""
    return (marcador(identificador), BLOCO)


def documento(*linhas, terminador="\n"):
    """Documento sintético terminado por `LF`, salvo indicação contrária."""
    return "\n".join(linhas) + terminador


def com_crlf(texto):
    """Mesmo documento com todas as quebras em `CRLF`."""
    return texto.replace("\n", "\r\n")


def achatar(resultado):
    """Flatten dos tokens — **somente nos testes**, para cruzar com `C8`."""
    return tuple(token for _, _, tokens in resultado for token in tokens)


def _docstrings(arvore):
    """Ids dos nós de constante que são docstring de módulo, classe ou função."""
    ids = set()
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


def _nomes_usados():
    nomes = set()
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.Name):
            nomes.add(no.id)
        elif isinstance(no, ast.Attribute):
            nomes.add(no.attr)
    return nomes


NOMES_PRODUCAO = _nomes_usados()


def _constantes_de_codigo():
    """Constantes `str` do módulo que **não** são docstring."""
    return [
        no.value
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.Constant)
        and isinstance(no.value, str)
        and id(no) not in IDS_DOCSTRING
    ]


# ---------------------------------------------------------------------------
# A. Sucesso e forma da saida
# ---------------------------------------------------------------------------


def test_documento_vazio_devolve_tupla_vazia():
    assert associar_fragmentos_a_secao("") == ()


def test_documento_so_com_quebra_devolve_tupla_vazia():
    assert associar_fragmentos_a_secao("\n") == ()


def test_documento_sem_rxx_devolve_tupla_vazia():
    texto = documento("# Documento", "", "texto comum", "")
    assert associar_fragmentos_a_secao(texto) == ()


def test_uma_secao_um_fragmento():
    texto = documento(cabecalho(), *unidade("F1"))
    assert associar_fragmentos_a_secao(texto) == (
        ("R01", ROTULO_ST1, ("R01/F1",)),
    )


def test_uma_secao_varios_fragmentos():
    texto = documento(cabecalho(), *unidade("F1"), *unidade("F2"), *unidade("F3"))
    assert associar_fragmentos_a_secao(texto) == (
        ("R01", ROTULO_ST1, ("R01/F1", "R01/F2", "R01/F3")),
    )


def test_varias_secoes():
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_ST1),
        *unidade("F1"),
        cabecalho("R02", rotulo=ROTULO_ST2),
        *unidade("F1"),
        *unidade("F2"),
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade("F1"),
    )
    assert associar_fragmentos_a_secao(texto) == (
        ("R01", ROTULO_ST1, ("R01/F1",)),
        ("R02", ROTULO_ST2, ("R02/F1", "R02/F2")),
        ("R28", ROTULO_PARCIAL, ("R28/F1",)),
    )


def test_ordem_fisica_e_preservada():
    texto = documento(
        cabecalho("R09"),
        *unidade("F2"),
        *unidade("F10"),
        *unidade("F1"),
        cabecalho("R02"),
        *unidade("F1"),
    )
    resultado = associar_fragmentos_a_secao(texto)
    assert [rxx for rxx, _, _ in resultado] == ["R09", "R02"]
    assert resultado[0][2] == ("R09/F2", "R09/F10", "R09/F1")


def test_ordem_nao_e_lexicografica():
    texto = documento(cabecalho("R09"), *unidade("F2"), *unidade("F10"))
    tokens = associar_fragmentos_a_secao(texto)[0][2]
    assert tokens == ("R09/F2", "R09/F10")
    assert list(tokens) != sorted(tokens)


def test_forma_da_saida_e_tripla_com_tupla_de_tokens():
    resultado = associar_fragmentos_a_secao(
        documento(cabecalho(), *unidade("F1"), *unidade("F2"))
    )
    assert isinstance(resultado, tuple)
    for entrada in resultado:
        assert type(entrada) is tuple
        assert len(entrada) == 3
        rxx, rotulo, tokens = entrada
        assert type(rxx) is str
        assert type(rotulo) is str
        assert type(tokens) is tuple
        assert all(type(token) is str for token in tokens)


def test_token_e_derivado_como_rxx_barra_id():
    resultado = associar_fragmentos_a_secao(
        documento(cabecalho("R42"), *unidade("F13"))
    )
    assert resultado[0][2] == ("R42/F13",)


def test_rotulo_literal_e_transportado_opaco():
    for rotulo in (ROTULO_ST1, ROTULO_ST2, ROTULO_ST3, ROTULO_PARCIAL, "qualquer"):
        texto = documento(cabecalho(rotulo=rotulo), *unidade("F1"))
        assert associar_fragmentos_a_secao(texto)[0][1] == rotulo


def test_entrada_nao_e_alterada():
    texto = documento(cabecalho(), *unidade("F1"))
    copia = texto[:]
    associar_fragmentos_a_secao(texto)
    assert texto == copia


def test_chamadas_repetidas_sao_deterministicas():
    texto = documento(cabecalho(), *unidade("F1"), *unidade("F2"))
    esperado = (("R01", ROTULO_ST1, ("R01/F1", "R01/F2")),)
    assert [associar_fragmentos_a_secao(texto) for _ in range(20)] == [esperado] * 20


# ---------------------------------------------------------------------------
# B. Politica de linha
# ---------------------------------------------------------------------------


def test_lf_e_crlf_sao_equivalentes():
    texto = documento(cabecalho(), *unidade("F1"), *unidade("F2"))
    assert associar_fragmentos_a_secao(texto) == associar_fragmentos_a_secao(
        com_crlf(texto)
    )


def test_terminacao_mista():
    texto = (
        cabecalho()
        + "\r\n"
        + marcador("F1")
        + "\n"
        + BLOCO
        + "\r\n"
        + marcador("F2")
        + "\n"
        + BLOCO
        + "\n"
    )
    assert associar_fragmentos_a_secao(texto) == (
        ("R01", ROTULO_ST1, ("R01/F1", "R01/F2")),
    )


def test_sem_quebra_final():
    texto = documento(cabecalho(), *unidade("F1"), terminador="")
    assert associar_fragmentos_a_secao(texto) == (
        ("R01", ROTULO_ST1, ("R01/F1",)),
    )


def test_cr_residual_no_marcador_o_torna_conteudo_comum():
    """Dois `CR` antes do `LF`: um é removido, o outro fica dentro da linha."""
    texto = (
        cabecalho()
        + "\n"
        + marcador("F1")
        + "\n"
        + BLOCO
        + "\n"
        + marcador("F2")
        + "\r\r\n"
        + BLOCO
        + "\n"
    )
    # `C8` julga a estrutura: o quase-marcador deixa um bloco sem marcador.
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        associar_fragmentos_a_secao(texto)
    assert str(erro.value) == "bloco_sem_marcador: bloco"


def test_cr_residual_no_rotulo_permanece_conteudo_do_rotulo():
    """A gramática do cabeçalho aceita a linha; o `CR` entra no rótulo."""
    texto = cabecalho() + "\r\r\n" + marcador("F1") + "\n" + BLOCO + "\n"
    resultado = associar_fragmentos_a_secao(texto)
    assert resultado == (("R01", ROTULO_ST1 + "\r", ("R01/F1",)),)


# ---------------------------------------------------------------------------
# C. Escopo de secao, compativel com C8
# ---------------------------------------------------------------------------


def test_h1_encerra_o_escopo():
    texto = documento(
        cabecalho("R01"),
        *unidade("F1"),
        "# Documento",
        "texto",
        cabecalho("R02"),
        *unidade("F1"),
    )
    assert associar_fragmentos_a_secao(texto) == (
        ("R01", ROTULO_ST1, ("R01/F1",)),
        ("R02", ROTULO_ST1, ("R02/F1",)),
    )


def test_marcador_apos_h1_falha_em_c8():
    texto = documento(
        cabecalho("R01"), *unidade("F1"), "# Documento", *unidade("F1")
    )
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        associar_fragmentos_a_secao(texto)
    assert str(erro.value) == "marcador_fora_de_secao: marcador"


def test_h2_nao_rxx_encerra_escopo_e_deixa_zero_rxx():
    texto = documento(
        cabecalho("R01"),
        *unidade("F1"),
        "## Outra secao",
        "texto",
        cabecalho("R02"),
        *unidade("F1"),
    )
    resultado = associar_fragmentos_a_secao(texto)
    assert [rxx for rxx, _, _ in resultado] == ["R01", "R02"]


def test_marcador_sob_h2_nao_rxx_falha_em_c8():
    texto = documento(
        cabecalho("R01"), *unidade("F1"), "## Outra secao", *unidade("F1")
    )
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        associar_fragmentos_a_secao(texto)
    assert str(erro.value) == "marcador_fora_de_secao: marcador"


@pytest.mark.parametrize("nivel", [3, 4, 5, 6])
def test_h3_a_h6_nao_encerram_a_secao(nivel):
    texto = documento(
        cabecalho("R01"),
        *unidade("F1"),
        "#" * nivel + " Subtitulo",
        *unidade("F2"),
    )
    assert associar_fragmentos_a_secao(texto) == (
        ("R01", ROTULO_ST1, ("R01/F1", "R01/F2")),
    )


def test_bloco_fora_de_rxx_e_ignorado():
    texto = documento(
        "# Documento",
        "> bloco fora de qualquer secao",
        "> segunda linha",
        cabecalho("R01"),
        *unidade("F1"),
    )
    assert associar_fragmentos_a_secao(texto) == (
        ("R01", ROTULO_ST1, ("R01/F1",)),
    )


def test_cabecalho_indentado_nao_e_cabecalho():
    texto = documento(
        cabecalho("R01"),
        *unidade("F1"),
        "   ## R02 nao e cabecalho",
        *unidade("F2"),
    )
    assert associar_fragmentos_a_secao(texto) == (
        ("R01", ROTULO_ST1, ("R01/F1", "R01/F2")),
    )


def test_sete_cerquilhas_nao_e_cabecalho():
    texto = documento(
        cabecalho("R01"),
        *unidade("F1"),
        "####### nao e cabecalho",
        *unidade("F2"),
    )
    assert associar_fragmentos_a_secao(texto) == (
        ("R01", ROTULO_ST1, ("R01/F1", "R01/F2")),
    )


# ---------------------------------------------------------------------------
# D. Homonimos e fronteira fisica
# ---------------------------------------------------------------------------


def test_duas_secoes_homonimas_consecutivas_sao_entradas_distintas():
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade("F1"),
        cabecalho("R28", rotulo=ROTULO_ST1),
        *unidade("F1"),
    )
    assert associar_fragmentos_a_secao(texto) == (
        ("R28", ROTULO_PARCIAL, ("R28/F1",)),
        ("R28", ROTULO_ST1, ("R28/F1",)),
    )


def test_duas_secoes_homonimas_separadas_por_outra():
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade("F1"),
        cabecalho("R05", rotulo=ROTULO_ST1),
        *unidade("F1"),
        cabecalho("R28", rotulo=ROTULO_ST2),
        *unidade("F1"),
    )
    assert associar_fragmentos_a_secao(texto) == (
        ("R28", ROTULO_PARCIAL, ("R28/F1",)),
        ("R05", ROTULO_ST1, ("R05/F1",)),
        ("R28", ROTULO_ST2, ("R28/F1",)),
    )


def test_homonimos_com_mesma_combinacao_rxx_barra_id():
    texto = documento(
        cabecalho("R28"),
        *unidade("F1"),
        cabecalho("R28"),
        *unidade("F1"),
        cabecalho("R28"),
        *unidade("F1"),
    )
    resultado = associar_fragmentos_a_secao(texto)
    assert len(resultado) == 3
    assert all(tokens == ("R28/F1",) for _, _, tokens in resultado)
    assert achatar(resultado) == ("R28/F1", "R28/F1", "R28/F1")


def test_homonimos_com_rotulos_diferentes_mantem_seus_rotulos():
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade("F1"),
        cabecalho("R28", rotulo=ROTULO_ST3),
        *unidade("F1"),
    )
    assert [rotulo for _, rotulo, _ in associar_fragmentos_a_secao(texto)] == [
        ROTULO_PARCIAL,
        ROTULO_ST3,
    ]


def test_nenhuma_consolidacao_entre_instancias_fisicas():
    """A fronteira física é preservada mesmo com tokens textualmente iguais."""
    texto = documento(
        cabecalho("R28"),
        *unidade("F1"),
        *unidade("F2"),
        cabecalho("R28"),
        *unidade("F1"),
    )
    resultado = associar_fragmentos_a_secao(texto)
    assert len(resultado) == 2
    assert resultado[0][2] == ("R28/F1", "R28/F2")
    assert resultado[1][2] == ("R28/F1",)
    # Uma consolidacao por valor de `Rxx` produziria uma unica entrada.
    assert resultado[0][2] != resultado[1][2]


def test_nenhuma_deduplicacao_de_token():
    texto = documento(
        cabecalho("R28"),
        *unidade("F1"),
        cabecalho("R28"),
        *unidade("F1"),
    )
    assert len(achatar(associar_fragmentos_a_secao(texto))) == 2


def test_a_posicao_da_entrada_nao_e_identidade():
    """Trocar a ordem física das instâncias troca a ordem, não a identidade."""
    primeiro = documento(
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade("F1"),
        cabecalho("R28", rotulo=ROTULO_ST1),
        *unidade("F1"),
    )
    segundo = documento(
        cabecalho("R28", rotulo=ROTULO_ST1),
        *unidade("F1"),
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade("F1"),
    )
    assert associar_fragmentos_a_secao(primeiro) != associar_fragmentos_a_secao(
        segundo
    )
    assert achatar(associar_fragmentos_a_secao(primeiro)) == achatar(
        associar_fragmentos_a_secao(segundo)
    )


# ---------------------------------------------------------------------------
# E. Quase-marcador
# ---------------------------------------------------------------------------


QUASE_MARCADORES = (
    "<!--fragmento: F1 -->",
    "<!-- fragmento:F1 -->",
    "<!-- fragmento : F1 -->",
    "<!-- Fragmento: F1 -->",
    " <!-- fragmento: F1 -->",
    "\t<!-- fragmento: F1 -->",
    "<!-- fragmento: F1 --> ",
    "x <!-- fragmento: F1 -->",
    "<!-- fragmento: F1 --> x",
    "<!-- fragmento: F1",
    "fragmento: F1 -->",
)


@pytest.mark.parametrize("quase", QUASE_MARCADORES)
def test_quase_marcador_sem_bloco_seguinte_e_conteudo_comum(quase):
    """Cenário em que o quase-marcador não deixa bloco emitível descoberto."""
    texto = documento(cabecalho("R01"), *unidade("F1"), quase, "texto comum")
    assert associar_fragmentos_a_secao(texto) == (
        ("R01", ROTULO_ST1, ("R01/F1",)),
    )


@pytest.mark.parametrize("quase", QUASE_MARCADORES)
def test_quase_marcador_nao_produz_token(quase):
    texto = documento(cabecalho("R01"), *unidade("F1"), quase, "texto comum")
    assert achatar(associar_fragmentos_a_secao(texto)) == ("R01/F1",)


def test_quase_marcador_antes_de_bloco_continua_falhando_em_c8():
    """Não é conteúdo inofensivo quando deixa um bloco emitível sem marcador."""
    texto = documento(
        cabecalho("R01"), *unidade("F1"), "<!-- fragmento:F2 -->", BLOCO
    )
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        associar_fragmentos_a_secao(texto)
    assert str(erro.value) == "bloco_sem_marcador: bloco"


def test_envelope_sobreposto_nao_e_marcador():
    texto = documento(
        cabecalho("R01"), *unidade("F1"), "<!-- fragmento: -->", "texto comum"
    )
    assert achatar(associar_fragmentos_a_secao(texto)) == ("R01/F1",)


# ---------------------------------------------------------------------------
# F. Cruzamento obrigatorio com C8
# ---------------------------------------------------------------------------


def _corpora_validos():
    """Corpora sintéticos **válidos** para o cruzamento com `C8`."""
    uma = documento(cabecalho("R01"), *unidade("F1"))
    varias = documento(
        cabecalho("R01", rotulo=ROTULO_ST1),
        *unidade("F1"),
        cabecalho("R02", rotulo=ROTULO_ST2),
        *unidade("F1"),
        cabecalho("R03", rotulo=ROTULO_PARCIAL),
        *unidade("F1"),
    )
    multiplos = documento(
        cabecalho("R01"), *unidade("F1"), *unidade("F2"), *unidade("F10")
    )
    homonimos = documento(
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade("F1"),
        cabecalho("R28", rotulo=ROTULO_ST1),
        *unidade("F1"),
    )
    repetidos = documento(
        cabecalho("R28"),
        *unidade("F1"),
        cabecalho("R28"),
        *unidade("F1"),
        cabecalho("R28"),
        *unidade("F1"),
    )
    subtitulos = documento(
        cabecalho("R01"),
        *unidade("F1"),
        "### Sub",
        *unidade("F2"),
        "###### Sub profundo",
        *unidade("F3"),
    )
    return (
        ("uma secao", uma),
        ("varias secoes", varias),
        ("multiplos fragmentos", multiplos),
        ("homonimos", homonimos),
        ("tokens repetidos", repetidos),
        ("subtitulos h3-h6", subtitulos),
    )


CORPORA_VALIDOS = _corpora_validos()


@pytest.mark.parametrize("nome, texto", CORPORA_VALIDOS)
def test_flatten_coincide_com_c8_em_lf(nome, texto):
    assert achatar(associar_fragmentos_a_secao(texto)) == ler_unidades_marcadas(texto)


@pytest.mark.parametrize("nome, texto", CORPORA_VALIDOS)
def test_flatten_coincide_com_c8_em_crlf(nome, texto):
    convertido = com_crlf(texto)
    assert achatar(
        associar_fragmentos_a_secao(convertido)
    ) == ler_unidades_marcadas(convertido)


@pytest.mark.parametrize("nome, texto", CORPORA_VALIDOS)
def test_cardinalidade_do_flatten_coincide_com_c8(nome, texto):
    assert len(achatar(associar_fragmentos_a_secao(texto))) == len(
        ler_unidades_marcadas(texto)
    )


def test_flatten_coincide_com_c8_em_documento_sem_rxx():
    texto = documento("# Documento", "texto")
    assert achatar(associar_fragmentos_a_secao(texto)) == ler_unidades_marcadas(texto)
    assert ler_unidades_marcadas(texto) == ()


def test_flatten_coincide_com_c8_com_bloco_fora_de_secao():
    texto = documento(
        "# Documento",
        "> bloco ignorado",
        cabecalho("R01"),
        *unidade("F1"),
    )
    assert achatar(associar_fragmentos_a_secao(texto)) == ler_unidades_marcadas(texto)


# ---------------------------------------------------------------------------
# G. Falha e precedencia
# ---------------------------------------------------------------------------


def test_violacao_c_a5_propaga_intacta():
    texto = documento(cabecalho("R01"), marcador("F1"), "texto")
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        associar_fragmentos_a_secao(texto)
    assert type(erro.value) is RepresentacaoMarcadaInvalida
    assert str(erro.value) == "marcador_sem_bloco: marcador"
    assert erro.value.__cause__ is None
    assert erro.value.__context__ is None


def test_violacao_g2_propaga_intacta():
    texto = documento("## R01 - Titulo - APROVADO", *unidade("F1"))
    with pytest.raises(CabecalhoRxxInvalido) as erro:
        associar_fragmentos_a_secao(texto)
    assert type(erro.value) is CabecalhoRxxInvalido
    assert str(erro.value) == "separador_ausente: cabecalho"
    assert erro.value.__cause__ is None
    assert erro.value.__context__ is None


def test_mensagem_de_c8_e_identica_a_dele():
    texto = documento(cabecalho("R01"), marcador("F1"), "texto")
    with pytest.raises(RepresentacaoMarcadaInvalida) as direto:
        ler_unidades_marcadas(texto)
    with pytest.raises(RepresentacaoMarcadaInvalida) as pela_fronteira:
        associar_fragmentos_a_secao(texto)
    assert str(pela_fronteira.value) == str(direto.value)


def test_tipo_invalido_pertence_a_c8():
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        associar_fragmentos_a_secao(None)
    assert str(erro.value) == "tipo_invalido: texto"


def test_subclasse_de_str_e_recusada_por_c8():
    class Documento(str):
        pass

    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        associar_fragmentos_a_secao(Documento(""))
    assert str(erro.value) == "tipo_invalido: texto"


def test_secao_sem_unidade_pertence_a_c8():
    texto = documento(cabecalho("R01"), "texto", cabecalho("R02"), *unidade("F1"))
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        associar_fragmentos_a_secao(texto)
    assert str(erro.value) == "secao_sem_unidade: secao"


def test_id_duplicado_pertence_a_c8():
    texto = documento(cabecalho("R01"), *unidade("F1"), *unidade("F1"))
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        associar_fragmentos_a_secao(texto)
    assert str(erro.value) == "id_duplicado: marcador"


def test_id_fora_da_gramatica_pertence_a_c8():
    texto = documento(cabecalho("R01"), marcador("F01"), BLOCO)
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        associar_fragmentos_a_secao(texto)
    assert str(erro.value) == "id_fora_da_gramatica: marcador"


def test_falha_estrutural_posterior_vence_anomalia_anterior():
    """O portão `C8` percorre o documento inteiro antes da caminhada local."""
    texto = documento(
        cabecalho("R01"),
        *unidade("F1"),
        cabecalho("R02"),
        marcador("F1"),
        "texto",
    )
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        associar_fragmentos_a_secao(texto)
    assert str(erro.value) == "marcador_sem_bloco: marcador"


def test_falha_g2_posterior_vence_leitura_anterior():
    texto = documento(
        cabecalho("R01"),
        *unidade("F1"),
        "## R02 - Titulo - APROVADO",
        *unidade("F1"),
    )
    with pytest.raises(CabecalhoRxxInvalido):
        associar_fragmentos_a_secao(texto)


def test_nada_e_devolvido_parcialmente():
    texto = documento(
        cabecalho("R01"), *unidade("F1"), cabecalho("R02"), marcador("F1"), "texto"
    )
    with pytest.raises(RepresentacaoMarcadaInvalida):
        associar_fragmentos_a_secao(texto)


def test_nenhuma_excecao_publica_nova_foi_definida():
    from casa77_sdr import response_section_membership

    classes = [
        no
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.ClassDef)
    ]
    assert classes == []
    for nome, valor in vars(response_section_membership).items():
        if isinstance(valor, type):
            assert not issubclass(valor, BaseException)


# ---------------------------------------------------------------------------
# H. Invariante local x C12
# ---------------------------------------------------------------------------


def test_invariante_dispara_com_rotulo_divergente(monkeypatch):
    from casa77_sdr import response_section_membership

    monkeypatch.setattr(
        response_section_membership,
        "extrair_rotulos_de_cabecalho",
        lambda texto: (("R01", "OUTRO"),),
    )
    texto = documento(cabecalho("R01"), *unidade("F1"))
    with pytest.raises(RuntimeError) as erro:
        response_section_membership.associar_fragmentos_a_secao(texto)
    assert str(erro.value) == "invariante_estrutural"


def test_invariante_dispara_com_rxx_divergente(monkeypatch):
    from casa77_sdr import response_section_membership

    monkeypatch.setattr(
        response_section_membership,
        "extrair_rotulos_de_cabecalho",
        lambda texto: (("R99", ROTULO_ST1),),
    )
    texto = documento(cabecalho("R01"), *unidade("F1"))
    with pytest.raises(RuntimeError) as erro:
        response_section_membership.associar_fragmentos_a_secao(texto)
    assert str(erro.value) == "invariante_estrutural"


def test_invariante_dispara_com_cardinalidade_divergente(monkeypatch):
    from casa77_sdr import response_section_membership

    monkeypatch.setattr(
        response_section_membership,
        "extrair_rotulos_de_cabecalho",
        lambda texto: (),
    )
    texto = documento(cabecalho("R01"), *unidade("F1"))
    with pytest.raises(RuntimeError) as erro:
        response_section_membership.associar_fragmentos_a_secao(texto)
    assert str(erro.value) == "invariante_estrutural"


def test_invariante_dispara_com_ordem_divergente(monkeypatch):
    from casa77_sdr import response_section_membership

    monkeypatch.setattr(
        response_section_membership,
        "extrair_rotulos_de_cabecalho",
        lambda texto: (("R02", ROTULO_ST1), ("R01", ROTULO_ST1)),
    )
    texto = documento(
        cabecalho("R01"), *unidade("F1"), cabecalho("R02"), *unidade("F1")
    )
    with pytest.raises(RuntimeError) as erro:
        response_section_membership.associar_fragmentos_a_secao(texto)
    assert str(erro.value) == "invariante_estrutural"


def test_invariante_nunca_e_excecao_publica(monkeypatch):
    from casa77_sdr import response_section_membership

    monkeypatch.setattr(
        response_section_membership,
        "extrair_rotulos_de_cabecalho",
        lambda texto: (),
    )
    texto = documento(cabecalho("R01"), *unidade("F1"))
    with pytest.raises(RuntimeError) as erro:
        response_section_membership.associar_fragmentos_a_secao(texto)
    assert type(erro.value) is RuntimeError
    assert not isinstance(erro.value, RepresentacaoMarcadaInvalida)
    assert not isinstance(erro.value, CabecalhoRxxInvalido)
    assert erro.value.__cause__ is None
    assert erro.value.__context__ is None


def test_invariante_nao_dispara_quando_as_caminhadas_coincidem(monkeypatch):
    from casa77_sdr import response_section_membership

    monkeypatch.setattr(
        response_section_membership,
        "extrair_rotulos_de_cabecalho",
        lambda texto: (("R01", ROTULO_ST1),),
    )
    texto = documento(cabecalho("R01"), *unidade("F1"))
    assert response_section_membership.associar_fragmentos_a_secao(texto) == (
        ("R01", ROTULO_ST1, ("R01/F1",)),
    )


def test_invariante_distingue_homonimos_por_rotulo(monkeypatch):
    """Duas instâncias homônimas com rótulos trocados divergem do retorno da C12."""
    from casa77_sdr import response_section_membership

    monkeypatch.setattr(
        response_section_membership,
        "extrair_rotulos_de_cabecalho",
        lambda texto: (("R28", ROTULO_ST1), ("R28", ROTULO_PARCIAL)),
    )
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade("F1"),
        cabecalho("R28", rotulo=ROTULO_ST1),
        *unidade("F1"),
    )
    with pytest.raises(RuntimeError) as erro:
        response_section_membership.associar_fragmentos_a_secao(texto)
    assert str(erro.value) == "invariante_estrutural"


# ---------------------------------------------------------------------------
# I. Contrato publico
# ---------------------------------------------------------------------------


def test_all_tem_exatamente_um_nome():
    from casa77_sdr import response_section_membership

    assert response_section_membership.__all__ == ["associar_fragmentos_a_secao"]


def test_nao_ha_nome_publico_fora_de_all():
    from casa77_sdr import response_section_membership

    publicos = {
        nome
        for nome in vars(response_section_membership)
        if not nome.startswith("_")
        and nome not in {"annotations", "extrair_rotulos_de_cabecalho"}
    }
    assert publicos == set(response_section_membership.__all__)


def test_assinatura_tem_um_unico_parametro_sem_default():
    assinatura = inspect.signature(associar_fragmentos_a_secao)
    assert list(assinatura.parameters) == ["texto"]
    parametro = assinatura.parameters["texto"]
    assert parametro.default is inspect.Parameter.empty
    assert parametro.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD


def test_anotacao_de_retorno_e_a_arbitrada():
    assinatura = inspect.signature(associar_fragmentos_a_secao)
    assert assinatura.return_annotation == "tuple[tuple[str, str, tuple[str, ...]], ...]"


def test_nao_e_exportado_pelo_pacote():
    assert not hasattr(casa77_sdr, "associar_fragmentos_a_secao")
    assert "associar_fragmentos_a_secao" not in getattr(casa77_sdr, "__all__", [])


def test_producao_nao_declara_dto_nem_dataclass():
    proibidos = {"dataclass", "NamedTuple", "TypedDict", "Enum", "StrEnum"}
    assert not proibidos & NOMES_PRODUCAO


# ---------------------------------------------------------------------------
# J. Pureza do modulo de producao
# ---------------------------------------------------------------------------


def test_imports_sao_exatamente_os_dois_permitidos():
    assert not [no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.Import)]
    de_onde = [
        no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.ImportFrom)
    ]
    assert [no.module for no in de_onde] == [
        "__future__",
        "casa77_sdr.response_header_labels",
    ]
    importados = [alias.name for no in de_onde for alias in no.names]
    assert importados == ["annotations", "extrair_rotulos_de_cabecalho"]


def test_nao_ha_import_dentro_de_funcao():
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for interno in ast.walk(no):
                assert not isinstance(interno, (ast.Import, ast.ImportFrom))


def test_producao_nao_importa_c8_diretamente():
    de_onde = [
        no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.ImportFrom)
    ]
    modulos = [no.module for no in de_onde]
    nomes = [alias.name for no in de_onde for alias in no.names]
    assert "casa77_sdr.response_markdown_units" not in modulos
    assert "ler_unidades_marcadas" not in nomes
    assert "ler_unidades_marcadas" not in NOMES_PRODUCAO


def test_producao_nao_importa_fronteiras_de_status():
    de_onde = [
        no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.ImportFrom)
    ]
    modulos = [no.module for no in de_onde]
    nomes = [alias.name for no in de_onde for alias in no.names]
    for proibido in (
        "casa77_sdr.response_status",
        "casa77_sdr.response_status_propagation",
        "casa77_sdr.response_fragment_status",
    ):
        assert proibido not in modulos
    for proibido in (
        "canonicalizar_status",
        "propagar_status",
        "extrair_status_por_fragmento",
    ):
        assert proibido not in nomes
        assert proibido not in NOMES_PRODUCAO


def test_producao_nao_tem_semantica_de_status():
    for constante in _constantes_de_codigo():
        assert constante != ROTULO_PARCIAL
        assert constante != ROTULO_ST2
        assert constante != ROTULO_ST3
        assert "AGUARDA" not in constante
        assert "BLOQUEADO" not in constante
        assert "status-fragmento" not in constante


def test_primeira_operacao_funcional_e_c12():
    funcao = next(
        no
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.FunctionDef)
        and no.name == "associar_fragmentos_a_secao"
    )
    corpo = [no for no in funcao.body if not isinstance(no, ast.Expr)]
    primeira = corpo[0]
    assert isinstance(primeira, ast.Assign)
    assert isinstance(primeira.value, ast.Call)
    assert isinstance(primeira.value.func, ast.Name)
    assert primeira.value.func.id == "extrair_rotulos_de_cabecalho"


def test_c12_e_chamado_uma_unica_vez():
    chamadas = [
        no
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.Call)
        and isinstance(no.func, ast.Name)
        and no.func.id == "extrair_rotulos_de_cabecalho"
    ]
    assert len(chamadas) == 1


def test_nao_ha_captura_de_excecao():
    for no in ast.walk(ARVORE_PRODUCAO):
        assert not isinstance(no, (ast.Try, ast.ExceptHandler))


def test_nao_ha_raise_from():
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.Raise):
            assert no.cause is None


def test_o_unico_raise_e_o_invariante():
    lancamentos = [
        no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.Raise)
    ]
    assert len(lancamentos) == 1
    chamada = lancamentos[0].exc
    assert isinstance(chamada, ast.Call)
    assert isinstance(chamada.func, ast.Name)
    assert chamada.func.id == "RuntimeError"


def test_nao_ha_global_nem_nonlocal():
    for no in ast.walk(ARVORE_PRODUCAO):
        assert not isinstance(no, (ast.Global, ast.Nonlocal))


def test_nao_ha_assert_em_producao():
    for no in ast.walk(ARVORE_PRODUCAO):
        assert not isinstance(no, ast.Assert)


def test_nao_ha_dict_nem_conjunto_no_codigo():
    assert not [
        no
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, (ast.Dict, ast.DictComp, ast.Set, ast.SetComp))
    ]
    proibidos = {"dict", "set", "frozenset", "Counter", "defaultdict", "OrderedDict"}
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_zip_sorted_nem_similares():
    assert not {"zip", "sorted", "reversed", "map", "filter"} & NOMES_PRODUCAO


def test_nao_ha_io_nem_filesystem():
    proibidos = {
        "open",
        "read",
        "write",
        "read_text",
        "write_text",
        "Path",
        "pathlib",
        "os",
        "io",
        "StringIO",
        "shutil",
        "tempfile",
        "print",
        "input",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_yaml_json_rede_llm_nem_banco():
    proibidos = {
        "yaml",
        "json",
        "safe_load",
        "dumps",
        "pickle",
        "requests",
        "urllib",
        "socket",
        "httpx",
        "anthropic",
        "openai",
        "sqlite3",
        "subprocess",
        "threading",
        "asyncio",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_relogio_calendario_locale_ambiente_nem_logging():
    proibidos = {
        "time",
        "datetime",
        "date",
        "now",
        "utcnow",
        "monotonic",
        "calendar",
        "locale",
        "setlocale",
        "getenv",
        "environ",
        "random",
        "uuid",
        "uuid4",
        "hashlib",
        "md5",
        "sha256",
        "logging",
        "getLogger",
        "cache",
        "lru_cache",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_regex_nem_unicodedata():
    proibidos = {"re", "regex", "match", "fullmatch", "search", "sub", "unicodedata"}
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_strip_splitlines_nem_normalizacao():
    proibidos = {
        "strip",
        "lstrip",
        "rstrip",
        "splitlines",
        "lower",
        "upper",
        "casefold",
        "title",
        "capitalize",
        "normalize",
        "encode",
        "decode",
        "expandtabs",
        "translate",
        "replace",
        "format",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_a_divisao_de_linhas_e_por_lf():
    assert "\\n" in CODIGO_PRODUCAO
    assert "split" in NOMES_PRODUCAO


def test_nao_ha_execucao_dinamica():
    proibidos = {"eval", "exec", "compile", "__import__", "globals", "locals", "vars"}
    assert not proibidos & NOMES_PRODUCAO


def test_producao_nao_menciona_corpus_caminho_nem_url():
    for constante in _constantes_de_codigo():
        assert "knowledge" not in constante
        assert ".yaml" not in constante
        assert ".md" not in constante
        assert ".env" not in constante
        assert "http" not in constante
        assert "C:" not in constante
        assert "/home/" not in constante


def test_producao_declara_uma_unica_funcao_publica():
    funcoes = [
        no.name
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    assert funcoes[0] == "associar_fragmentos_a_secao"
    assert all(nome.startswith("_") for nome in funcoes[1:])


def test_nao_ha_estado_mutavel_no_modulo():
    from casa77_sdr import response_section_membership

    for nome, valor in vars(response_section_membership).items():
        if nome.startswith("__") and nome.endswith("__"):
            continue
        if nome == "annotations":
            continue
        assert not isinstance(valor, (list, dict, set, bytearray))


def test_resultado_nao_depende_de_variavel_de_ambiente(monkeypatch):
    monkeypatch.setenv("LANG", "tr_TR.UTF-8")
    monkeypatch.setenv("LC_ALL", "tr_TR.UTF-8")
    monkeypatch.setenv("PYTHONHASHSEED", "0")
    texto = documento(cabecalho("R01"), *unidade("F1"))
    assert associar_fragmentos_a_secao(texto) == (
        ("R01", ROTULO_ST1, ("R01/F1",)),
    )


# ---------------------------------------------------------------------------
# K. Limites
# ---------------------------------------------------------------------------


def test_sucesso_nao_prova_unicidade_global():
    texto = documento(
        cabecalho("R28"), *unidade("F1"), cabecalho("R28"), *unidade("F1")
    )
    resultado = associar_fragmentos_a_secao(texto)
    assert len(resultado) == 2
    assert resultado[0][2] == resultado[1][2]


def test_a_fronteira_nao_distingue_parcial_de_outro_rotulo():
    """O rótulo é opaco: `PARCIAL` não recebe tratamento algum aqui."""
    parcial = documento(cabecalho("R01", rotulo=ROTULO_PARCIAL), *unidade("F1"))
    outro = documento(cabecalho("R01", rotulo="qualquer coisa"), *unidade("F1"))
    assert associar_fragmentos_a_secao(parcial)[0][2] == (
        associar_fragmentos_a_secao(outro)[0][2]
    )


def test_a_fronteira_nao_le_declaracao_de_status():
    """Uma declaração `status-fragmento` é conteúdo comum para esta fronteira."""
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_PARCIAL),
        "<!-- status-fragmento: APROVADO -->",
        *unidade("F1"),
    )
    assert associar_fragmentos_a_secao(texto) == (
        ("R01", ROTULO_PARCIAL, ("R01/F1",)),
    )


def test_nenhum_teste_desta_suite_toca_o_corpus():
    """A suíte é sintética: nada aqui lê o corpus versionado.

    Os alvos da busca são montados por concatenação para que a própria asserção
    não os introduza no arquivo e invalide o teste.
    """
    fonte = Path(__file__).read_text(encoding="utf-8")
    assert ("respostas" + "-aprovadas") not in fonte
    assert ("casa77" + ".yaml") not in fonte
    assert ("open" + "(") not in fonte

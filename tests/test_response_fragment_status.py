"""Testes da leitura determinística do status declarado por fragmento sob `PARCIAL`.

A fronteira materializa `PM1`–`PM5` e o **regime exclusivo** arbitrado depois:
a declaração `status-fragmento` é aceita **se e somente se** o rótulo literal da
seção física corrente for **exatamente** `PARCIAL`.

Estes testes provam o envelope exato, a relação física com o marcador, o
vocabulário fechado de `C-3`, a obrigatoriedade sob `PARCIAL`, a proibição fora
dele, a precedência entre `C8`, `C12` e `C14`, o invariante local × `C12`, o
silêncio das mensagens e a pureza do módulo de produção — e **não** transformam
em norma a composição documental, a resolução de `PARCIAL` no corpus real, o
índice, a bijeção física ou a migração da autoridade de status, que estão
**fora** desta fronteira. **Nenhum teste toca `knowledge/**`**: todos os
documentos são **sintéticos**.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

import casa77_sdr
from casa77_sdr.response_fragment_status import (
    DeclaracaoDeStatusInvalida,
    extrair_status_por_fragmento,
)
from casa77_sdr.response_header_labels import CabecalhoRxxInvalido
from casa77_sdr.response_markdown_units import RepresentacaoMarcadaInvalida

# ---------------------------------------------------------------------------
# Apoio
# ---------------------------------------------------------------------------

# Separador literal de `G2`: SPACE + EM DASH + SPACE, montado por ponto de
# codigo para que o teste nao dependa da forma como este arquivo foi gravado.
SEPARADOR = " " + chr(0x2014) + " "

# Rotulos fisicos de `C-A1-ST1`-`C-A1-ST3`, tambem por ponto de codigo.
ROTULO_ST1 = "APROVADO"
ROTULO_ST2 = "AGUARDA APROVA" + chr(0x00C7) + chr(0x00C3) + "O"
ROTULO_ST3 = "APROVADO com handoff obrigat" + chr(0x00F3) + "rio"
ROTULO_PARCIAL = "PARCIAL"

VALORES = ("APROVADO", "AGUARDA_APROVACAO", "BLOQUEADO")

CATEGORIAS = (
    "valor_invalido",
    "declaracao_fora_de_secao",
    "declaracao_proibida",
    "declaracao_orfa",
    "declaracao_ausente",
)
LOCALIZADORES = ("declaracao", "marcador")

VALOR_INVALIDO = "valor_invalido: declaracao"
FORA_DE_SECAO = "declaracao_fora_de_secao: declaracao"
PROIBIDA = "declaracao_proibida: declaracao"
ORFA = "declaracao_orfa: declaracao"
AUSENTE = "declaracao_ausente: marcador"

MENSAGENS = (VALOR_INVALIDO, FORA_DE_SECAO, PROIBIDA, ORFA, AUSENTE)

BLOCO = "> conteudo"

CAMINHO_PRODUCAO = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "casa77_sdr"
    / "response_fragment_status.py"
)
CODIGO_PRODUCAO = CAMINHO_PRODUCAO.read_text(encoding="utf-8")
ARVORE_PRODUCAO = ast.parse(CODIGO_PRODUCAO)


def cabecalho(rxx="R01", titulo="Titulo", rotulo=ROTULO_PARCIAL):
    """Linha de cabeçalho `G2` sintética."""
    return f"## {rxx}{SEPARADOR}{titulo}{SEPARADOR}{rotulo}"


def declaracao(valor="APROVADO"):
    """Linha de declaração `PM1` sintética."""
    return f"<!-- status-fragmento: {valor} -->"


def marcador(identificador="F1"):
    """Linha de marcador `C-A5` sintética."""
    return f"<!-- fragmento: {identificador} -->"


def documento(*linhas, terminador="\n"):
    """Documento sintético terminado por `LF`, salvo indicação contrária."""
    return "\n".join(linhas) + terminador


def com_crlf(texto):
    """Mesmo documento com todas as quebras em `CRLF`."""
    return texto.replace("\n", "\r\n")


def unidade(identificador="F1", valor="APROVADO"):
    """Declaração, marcador e bloco de um fragmento sob `PARCIAL`."""
    return (declaracao(valor), marcador(identificador), BLOCO)


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
# A. Sucesso
# ---------------------------------------------------------------------------


def test_documento_vazio_devolve_tupla_vazia():
    assert extrair_status_por_fragmento("") == ()


def test_documento_so_com_quebra_devolve_tupla_vazia():
    assert extrair_status_por_fragmento("\n") == ()


def test_documento_sem_rxx_devolve_tupla_vazia():
    texto = documento("# Documento", "", "texto comum", "")
    assert extrair_status_por_fragmento(texto) == ()


def test_documento_sem_secao_parcial_devolve_tupla_vazia():
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_ST1),
        marcador("F1"),
        BLOCO,
        cabecalho("R02", rotulo=ROTULO_ST2),
        marcador("F1"),
        BLOCO,
    )
    assert extrair_status_por_fragmento(texto) == ()


def test_parcial_com_um_fragmento():
    texto = documento(cabecalho(), *unidade("F1", "APROVADO"))
    assert extrair_status_por_fragmento(texto) == (("R01/F1", "APROVADO"),)


def test_parcial_com_varios_fragmentos():
    texto = documento(
        cabecalho(),
        *unidade("F1", "APROVADO"),
        *unidade("F2", "BLOQUEADO"),
        *unidade("F3", "AGUARDA_APROVACAO"),
    )
    assert extrair_status_por_fragmento(texto) == (
        ("R01/F1", "APROVADO"),
        ("R01/F2", "BLOQUEADO"),
        ("R01/F3", "AGUARDA_APROVACAO"),
    )


@pytest.mark.parametrize("valor", VALORES)
def test_cada_valor_canonico_e_aceito(valor):
    texto = documento(cabecalho(), *unidade("F1", valor))
    assert extrair_status_por_fragmento(texto) == (("R01/F1", valor),)


def test_status_iguais_entre_fragmentos():
    texto = documento(
        cabecalho(),
        *unidade("F1", "BLOQUEADO"),
        *unidade("F2", "BLOQUEADO"),
    )
    pares = extrair_status_por_fragmento(texto)
    assert [status for _, status in pares] == ["BLOQUEADO", "BLOQUEADO"]


def test_status_distintos_entre_fragmentos():
    texto = documento(
        cabecalho(),
        *unidade("F1", "APROVADO"),
        *unidade("F2", "BLOQUEADO"),
    )
    pares = extrair_status_por_fragmento(texto)
    assert [status for _, status in pares] == ["APROVADO", "BLOQUEADO"]


def test_ordem_fisica_e_preservada():
    texto = documento(
        cabecalho("R09"),
        *unidade("F2", "APROVADO"),
        *unidade("F1", "BLOQUEADO"),
        cabecalho("R02"),
        *unidade("F1", "AGUARDA_APROVACAO"),
    )
    assert [token for token, _ in extrair_status_por_fragmento(texto)] == [
        "R09/F2",
        "R09/F1",
        "R02/F1",
    ]


def test_ordem_nao_e_lexicografica():
    texto = documento(
        cabecalho("R09"),
        *unidade("F2", "APROVADO"),
        *unidade("F10", "APROVADO"),
    )
    tokens = [token for token, _ in extrair_status_por_fragmento(texto)]
    assert tokens == ["R09/F2", "R09/F10"]
    assert tokens != sorted(tokens)


def test_rxx_homonimos_produzem_dois_pares():
    texto = documento(
        cabecalho("R01"),
        *unidade("F1", "APROVADO"),
        cabecalho("R01"),
        *unidade("F1", "BLOQUEADO"),
    )
    assert extrair_status_por_fragmento(texto) == (
        ("R01/F1", "APROVADO"),
        ("R01/F1", "BLOQUEADO"),
    )


def test_tokens_repetidos_nao_sao_deduplicados():
    texto = documento(
        cabecalho("R01"),
        *unidade("F1", "APROVADO"),
        cabecalho("R01"),
        *unidade("F1", "APROVADO"),
        cabecalho("R01"),
        *unidade("F1", "APROVADO"),
    )
    pares = extrair_status_por_fragmento(texto)
    assert pares == (("R01/F1", "APROVADO"),) * 3
    assert len(pares) == 3


def test_cada_secao_homonima_tem_seu_proprio_regime():
    """Uma seção homônima sob outro rótulo não contamina a seção `PARCIAL`."""
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_ST1),
        marcador("F1"),
        BLOCO,
        cabecalho("R01", rotulo=ROTULO_PARCIAL),
        *unidade("F1", "BLOQUEADO"),
    )
    assert extrair_status_por_fragmento(texto) == (("R01/F1", "BLOQUEADO"),)


def test_mistura_de_secoes_parcial_e_nao_parcial():
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_ST1),
        marcador("F1"),
        BLOCO,
        cabecalho("R02", rotulo=ROTULO_PARCIAL),
        *unidade("F1", "APROVADO"),
        cabecalho("R03", rotulo=ROTULO_ST3),
        marcador("F1"),
        BLOCO,
        cabecalho("R04", rotulo=ROTULO_PARCIAL),
        *unidade("F1", "BLOQUEADO"),
        *unidade("F2", "AGUARDA_APROVACAO"),
    )
    assert extrair_status_por_fragmento(texto) == (
        ("R02/F1", "APROVADO"),
        ("R04/F1", "BLOQUEADO"),
        ("R04/F2", "AGUARDA_APROVACAO"),
    )


def test_lf_e_crlf_produzem_o_mesmo_resultado():
    texto = documento(cabecalho(), *unidade("F1", "APROVADO"))
    assert extrair_status_por_fragmento(texto) == extrair_status_por_fragmento(
        com_crlf(texto)
    )


def test_terminacao_mista_lf_e_crlf():
    texto = (
        cabecalho()
        + "\r\n"
        + declaracao("APROVADO")
        + "\n"
        + marcador("F1")
        + "\r\n"
        + BLOCO
        + "\n"
    )
    assert extrair_status_por_fragmento(texto) == (("R01/F1", "APROVADO"),)


def test_sem_quebra_final():
    texto = documento(cabecalho(), *unidade("F1", "APROVADO"), terminador="")
    assert extrair_status_por_fragmento(texto) == (("R01/F1", "APROVADO"),)


def test_bloco_de_varias_linhas():
    texto = documento(
        cabecalho(),
        declaracao("APROVADO"),
        marcador("F1"),
        "> primeira",
        "> segunda",
        "> terceira",
    )
    assert extrair_status_por_fragmento(texto) == (("R01/F1", "APROVADO"),)


def test_secao_sob_h3_permanece_corrente():
    texto = documento(
        cabecalho(),
        "### Subtitulo",
        *unidade("F1", "APROVADO"),
    )
    assert extrair_status_por_fragmento(texto) == (("R01/F1", "APROVADO"),)


def test_entrada_nao_e_alterada():
    texto = documento(cabecalho(), *unidade("F1", "APROVADO"))
    copia = texto[:]
    extrair_status_por_fragmento(texto)
    assert texto == copia


def test_chamadas_repetidas_sao_deterministicas():
    texto = documento(cabecalho(), *unidade("F1", "APROVADO"))
    esperado = (("R01/F1", "APROVADO"),)
    assert [extrair_status_por_fragmento(texto) for _ in range(20)] == [esperado] * 20


def test_saida_e_tupla_de_pares_de_str():
    pares = extrair_status_por_fragmento(
        documento(cabecalho(), *unidade("F1", "APROVADO"))
    )
    assert isinstance(pares, tuple)
    for par in pares:
        assert type(par) is tuple
        assert len(par) == 2
        assert all(type(campo) is str for campo in par)


# ---------------------------------------------------------------------------
# B. PM1 — envelope exato e quase-declaracao
# ---------------------------------------------------------------------------


QUASE_DECLARACOES = (
    "<!--status-fragmento: APROVADO -->",
    "<!-- status-fragmento:APROVADO -->",
    "<!-- status-fragmento : APROVADO -->",
    "<!-- Status-fragmento: APROVADO -->",
    "<!-- status_fragmento: APROVADO -->",
    " <!-- status-fragmento: APROVADO -->",
    "\t<!-- status-fragmento: APROVADO -->",
    "<!-- status-fragmento: APROVADO --> ",
    "<!-- status-fragmento: APROVADO -->\t",
    "x <!-- status-fragmento: APROVADO -->",
    "<!-- status-fragmento: APROVADO --> x",
    "<!-- status-fragmento: APROVADO",
    "status-fragmento: APROVADO -->",
    "<!-- status-fragmento: APROVADO ->",
    "<!-- status-fragmento: APROVADO -->\r\r",
)


@pytest.mark.parametrize("quase", QUASE_DECLARACOES)
def test_quase_declaracao_sob_parcial_deixa_marcador_sem_declaracao(quase):
    texto = documento(cabecalho(), quase, marcador("F1"), BLOCO)
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == AUSENTE


@pytest.mark.parametrize("quase", QUASE_DECLARACOES)
def test_quase_declaracao_sob_nao_parcial_e_conteudo_comum(quase):
    texto = documento(
        cabecalho(rotulo=ROTULO_ST1), quase, marcador("F1"), BLOCO
    )
    assert extrair_status_por_fragmento(texto) == ()


@pytest.mark.parametrize("quase", QUASE_DECLARACOES)
def test_quase_declaracao_fora_de_secao_e_conteudo_comum(quase):
    texto = documento(
        quase,
        "texto",
        cabecalho(rotulo=ROTULO_ST1),
        marcador("F1"),
        BLOCO,
    )
    assert extrair_status_por_fragmento(texto) == ()


def test_envelope_sobreposto_nao_e_declaracao_de_valor_vazio():
    """`<!-- status-fragmento: -->` é curto demais para ter prefixo e sufixo."""
    texto = documento(
        cabecalho(rotulo=ROTULO_ST1),
        "<!-- status-fragmento: -->",
        marcador("F1"),
        BLOCO,
    )
    assert extrair_status_por_fragmento(texto) == ()


def test_declaracao_dentro_do_bloco_nao_existe():
    """Uma linha iniciada por `>` nunca satisfaz `PM1`."""
    texto = documento(
        cabecalho(),
        declaracao("APROVADO"),
        marcador("F1"),
        BLOCO,
        "> <!-- status-fragmento: BLOQUEADO -->",
    )
    assert extrair_status_por_fragmento(texto) == (("R01/F1", "APROVADO"),)


def test_declaracao_exata_e_reconhecida():
    texto = documento(cabecalho(), declaracao("APROVADO"), marcador("F1"), BLOCO)
    assert extrair_status_por_fragmento(texto) == (("R01/F1", "APROVADO"),)


# ---------------------------------------------------------------------------
# C. PM2 / PM3 — relacao fisica com o marcador
# ---------------------------------------------------------------------------


def test_linha_em_branco_entre_declaracao_e_marcador():
    texto = documento(cabecalho(), declaracao("APROVADO"), "", marcador("F1"), BLOCO)
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == ORFA


def test_conteudo_intercalado_entre_declaracao_e_marcador():
    texto = documento(
        cabecalho(), declaracao("APROVADO"), "texto", marcador("F1"), BLOCO
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == ORFA


def test_quase_marcador_apos_declaracao():
    texto = documento(
        cabecalho(),
        declaracao("APROVADO"),
        "<!-- fragmento:F1 -->",
        marcador("F1"),
        BLOCO,
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == ORFA


def test_declaracao_no_fim_do_documento():
    texto = documento(
        cabecalho(),
        *unidade("F1", "APROVADO"),
        declaracao("BLOQUEADO"),
        terminador="",
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == ORFA


def test_declaracao_seguida_por_cabecalho():
    texto = documento(
        cabecalho("R01"),
        *unidade("F1", "APROVADO"),
        declaracao("BLOQUEADO"),
        cabecalho("R02"),
        *unidade("F1", "APROVADO"),
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == ORFA


def test_duas_declaracoes_consecutivas_a_primeira_e_orfa():
    texto = documento(
        cabecalho(),
        declaracao("APROVADO"),
        declaracao("BLOQUEADO"),
        marcador("F1"),
        BLOCO,
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == ORFA


def test_nao_existe_categoria_de_declaracao_multipla():
    """Duas declarações não criam categoria própria: a primeira é órfã."""
    texto = documento(
        cabecalho(),
        declaracao("APROVADO"),
        declaracao("APROVADO"),
        marcador("F1"),
        BLOCO,
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert "multipla" not in str(erro.value)
    assert str(erro.value) == ORFA


def test_marcador_valido_na_linha_seguinte_e_aceito():
    texto = documento(cabecalho(), declaracao("BLOQUEADO"), marcador("F7"), BLOCO)
    assert extrair_status_por_fragmento(texto) == (("R01/F7", "BLOQUEADO"),)


def test_marcador_sem_bloco_falha_primeiro_em_c8():
    texto = documento(cabecalho(), declaracao("APROVADO"), marcador("F1"), "texto")
    with pytest.raises(RepresentacaoMarcadaInvalida):
        extrair_status_por_fragmento(texto)


def test_bloco_sem_marcador_falha_primeiro_em_c8():
    texto = documento(cabecalho(), declaracao("APROVADO"), BLOCO)
    with pytest.raises(RepresentacaoMarcadaInvalida):
        extrair_status_por_fragmento(texto)


def test_declaracao_entre_marcador_e_bloco_falha_primeiro_em_c8():
    texto = documento(
        cabecalho(), marcador("F1"), declaracao("APROVADO"), BLOCO
    )
    with pytest.raises(RepresentacaoMarcadaInvalida):
        extrair_status_por_fragmento(texto)


def test_marcador_sem_declaracao_sob_parcial():
    texto = documento(cabecalho(), marcador("F1"), BLOCO)
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == AUSENTE


def test_um_marcador_com_declaracao_e_outro_sem():
    texto = documento(
        cabecalho(),
        *unidade("F1", "APROVADO"),
        marcador("F2"),
        BLOCO,
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == AUSENTE


def test_declaracao_nao_atravessa_para_o_marcador_seguinte():
    """A adjacência é estrita: uma declaração cobre um único marcador."""
    texto = documento(
        cabecalho(),
        declaracao("APROVADO"),
        marcador("F1"),
        BLOCO,
        marcador("F2"),
        BLOCO,
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == AUSENTE


def test_a_declaracao_nao_altera_o_token():
    """A posição associa a declaração ao marcador; a identidade é `<Rxx>/<id>`."""
    texto = documento(cabecalho("R42"), *unidade("F13", "AGUARDA_APROVACAO"))
    assert extrair_status_por_fragmento(texto) == (
        ("R42/F13", "AGUARDA_APROVACAO"),
    )


# ---------------------------------------------------------------------------
# D. PM4 — vocabulario fechado
# ---------------------------------------------------------------------------


VALORES_INVALIDOS = (
    "PARCIAL",
    "aprovado",
    "Aprovado",
    "APROVADo",
    "",
    " APROVADO",
    "APROVADO ",
    "AGUARDA APROVACAO",
    "AGUARDA_APROVACAO_",
    "APROVADO com handoff",
    "BLOQUEADA",
    "APROVAD" + chr(0x00D3),
    "APROVADO\t",
    "TALVEZ",
    "None",
    "null",
)


@pytest.mark.parametrize("valor", VALORES_INVALIDOS)
def test_valor_invalido_sob_parcial(valor):
    texto = documento(cabecalho(), declaracao(valor), marcador("F1"), BLOCO)
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == VALOR_INVALIDO


def test_parcial_nao_e_valor_valido():
    texto = documento(cabecalho(), declaracao("PARCIAL"), marcador("F1"), BLOCO)
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == VALOR_INVALIDO


def test_rotulo_fisico_de_st2_como_valor_e_invalido():
    texto = documento(cabecalho(), declaracao(ROTULO_ST2), marcador("F1"), BLOCO)
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == VALOR_INVALIDO


def test_rotulo_fisico_de_st3_como_valor_e_invalido():
    texto = documento(cabecalho(), declaracao(ROTULO_ST3), marcador("F1"), BLOCO)
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == VALOR_INVALIDO


def test_variante_unicode_do_valor_e_invalida():
    decomposto = "AGUARDA_APROVAC" + chr(0x0327) + "AO"
    texto = documento(cabecalho(), declaracao(decomposto), marcador("F1"), BLOCO)
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == VALOR_INVALIDO


def test_valor_com_espaco_inquebravel_e_invalido():
    texto = documento(
        cabecalho(),
        declaracao("AGUARDA" + chr(0x00A0) + "APROVACAO"),
        marcador("F1"),
        BLOCO,
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == VALOR_INVALIDO


@pytest.mark.parametrize("valor", VALORES)
def test_exatamente_tres_valores_sao_aceitos(valor):
    texto = documento(cabecalho(), *unidade("F1", valor))
    assert extrair_status_por_fragmento(texto)[0][1] == valor


def test_nenhum_valor_e_traduzido():
    """O campo já carrega o status canônico: nada é canonicalizado aqui."""
    texto = documento(cabecalho(), *unidade("F1", "AGUARDA_APROVACAO"))
    assert extrair_status_por_fragmento(texto) == (
        ("R01/F1", "AGUARDA_APROVACAO"),
    )


# ---------------------------------------------------------------------------
# E. Regime — somente `PARCIAL`
# ---------------------------------------------------------------------------


ROTULOS_SEM_REGIME = (
    ROTULO_ST1,
    ROTULO_ST2,
    ROTULO_ST3,
    "BLOQUEADO",
    "AGUARDA_APROVACAO",
    "qualquer coisa",
    "aprovado",
    "parcial",
    "Parcial",
    "PARCIAIS",
    "PARCIAL ok",
)


@pytest.mark.parametrize("rotulo", ROTULOS_SEM_REGIME)
def test_declaracao_proibida_fora_do_regime_parcial(rotulo):
    texto = documento(
        cabecalho(rotulo=rotulo), declaracao("APROVADO"), marcador("F1"), BLOCO
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == PROIBIDA


@pytest.mark.parametrize("rotulo", ROTULOS_SEM_REGIME)
def test_ausencia_de_declaracao_fora_do_regime_e_sucesso(rotulo):
    texto = documento(cabecalho(rotulo=rotulo), marcador("F1"), BLOCO)
    assert extrair_status_por_fragmento(texto) == ()


def test_regime_e_decidido_por_igualdade_literal_com_parcial():
    assert extrair_status_por_fragmento(
        documento(cabecalho(rotulo="PARCIAL"), *unidade("F1", "APROVADO"))
    ) == (("R01/F1", "APROVADO"),)
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(
            documento(cabecalho(rotulo="PARCIAL."), *unidade("F1", "APROVADO"))
        )
    assert str(erro.value) == PROIBIDA


def test_rotulo_com_branco_de_borda_falha_antes_em_c12():
    texto = documento(
        f"## R01{SEPARADOR}Titulo{SEPARADOR}PARCIAL ",
        declaracao("APROVADO"),
        marcador("F1"),
        BLOCO,
    )
    with pytest.raises(CabecalhoRxxInvalido) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == "branco_de_borda: rotulo"


def test_uma_secao_parcial_nao_libera_a_seguinte():
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_PARCIAL),
        *unidade("F1", "APROVADO"),
        cabecalho("R02", rotulo=ROTULO_ST1),
        declaracao("APROVADO"),
        marcador("F1"),
        BLOCO,
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == PROIBIDA


def test_uma_secao_nao_parcial_nao_bloqueia_a_seguinte():
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_ST1),
        marcador("F1"),
        BLOCO,
        cabecalho("R02", rotulo=ROTULO_PARCIAL),
        *unidade("F1", "APROVADO"),
    )
    assert extrair_status_por_fragmento(texto) == (("R02/F1", "APROVADO"),)


def test_producao_nao_carrega_os_rotulos_fisicos_de_st1_st3():
    for constante in _constantes_de_codigo():
        assert constante != ROTULO_ST2
        assert constante != ROTULO_ST3
        assert "handoff" not in constante


def test_producao_nao_importa_as_fronteiras_de_status():
    de_onde = [
        no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.ImportFrom)
    ]
    modulos = [no.module for no in de_onde]
    nomes = [alias.name for no in de_onde for alias in no.names]
    for proibido in (
        "casa77_sdr.response_status",
        "casa77_sdr.response_status_propagation",
    ):
        assert proibido not in modulos
    for proibido in ("canonicalizar_status", "propagar_status"):
        assert proibido not in nomes
        assert proibido not in NOMES_PRODUCAO


# ---------------------------------------------------------------------------
# F. Escopo — declaracao fora de secao
# ---------------------------------------------------------------------------


def test_declaracao_antes_de_qualquer_secao():
    texto = documento(
        declaracao("APROVADO"),
        "texto",
        cabecalho(),
        *unidade("F1", "APROVADO"),
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == FORA_DE_SECAO


def test_declaracao_apos_h1():
    texto = documento(
        cabecalho(),
        *unidade("F1", "APROVADO"),
        "# Documento",
        declaracao("APROVADO"),
        "texto",
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == FORA_DE_SECAO


def test_declaracao_sob_h2_nao_rxx():
    texto = documento(
        "## Outra secao",
        declaracao("APROVADO"),
        "texto",
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == FORA_DE_SECAO


def test_h1_encerra_a_secao_parcial():
    texto = documento(
        cabecalho(),
        *unidade("F1", "APROVADO"),
        "# Documento",
        marcador("F1"),
        BLOCO,
    )
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == "marcador_fora_de_secao: marcador"


def test_h3_a_h6_nao_encerram_a_secao():
    for nivel in range(3, 7):
        texto = documento(
            cabecalho(),
            "#" * nivel + " Subtitulo",
            *unidade("F1", "APROVADO"),
        )
        assert extrair_status_por_fragmento(texto) == (("R01/F1", "APROVADO"),)


# ---------------------------------------------------------------------------
# G. Precedencia entre fronteiras e dentro da C14
# ---------------------------------------------------------------------------


def test_c8_falha_antes_de_uma_violacao_pm_anterior():
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_ST1),
        declaracao("APROVADO"),
        marcador("F1"),
        BLOCO,
        cabecalho("R02", rotulo=ROTULO_PARCIAL),
        marcador("F1"),
        "texto",
    )
    with pytest.raises(RepresentacaoMarcadaInvalida):
        extrair_status_por_fragmento(texto)


def test_c12_falha_antes_de_uma_violacao_pm_anterior():
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_ST1),
        declaracao("APROVADO"),
        marcador("F1"),
        BLOCO,
        "## R02 - Titulo - APROVADO",
        marcador("F1"),
        BLOCO,
    )
    with pytest.raises(CabecalhoRxxInvalido) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == "separador_ausente: cabecalho"


def test_c8_falha_antes_de_c12():
    texto = documento(
        "## R01 - Titulo - APROVADO",
        marcador("F1"),
        "texto",
    )
    with pytest.raises(RepresentacaoMarcadaInvalida):
        extrair_status_por_fragmento(texto)


def test_tipo_invalido_pertence_a_c8():
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        extrair_status_por_fragmento(None)
    assert str(erro.value) == "tipo_invalido: texto"


def test_subclasse_de_str_e_recusada_por_c8():
    class Documento(str):
        pass

    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        extrair_status_por_fragmento(Documento(""))
    assert str(erro.value) == "tipo_invalido: texto"


def test_excecao_de_c8_sobe_intacta():
    texto = documento(cabecalho(), marcador("F1"), "texto")
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert type(erro.value) is RepresentacaoMarcadaInvalida
    assert erro.value.__cause__ is None
    assert erro.value.__context__ is None
    assert not isinstance(erro.value, DeclaracaoDeStatusInvalida)


def test_excecao_de_c12_sobe_intacta():
    texto = documento("## R01 - Titulo - APROVADO", marcador("F1"), BLOCO)
    with pytest.raises(CabecalhoRxxInvalido) as erro:
        extrair_status_por_fragmento(texto)
    assert type(erro.value) is CabecalhoRxxInvalido
    assert erro.value.__cause__ is None
    assert erro.value.__context__ is None
    assert not isinstance(erro.value, DeclaracaoDeStatusInvalida)


def test_valor_invalido_vence_declaracao_proibida():
    texto = documento(
        cabecalho(rotulo=ROTULO_ST1), declaracao("PARCIAL"), marcador("F1"), BLOCO
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == VALOR_INVALIDO


def test_valor_invalido_vence_declaracao_fora_de_secao():
    texto = documento(
        declaracao("PARCIAL"),
        "texto",
        cabecalho(),
        *unidade("F1", "APROVADO"),
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == VALOR_INVALIDO


def test_valor_invalido_vence_declaracao_orfa():
    texto = documento(
        cabecalho(), declaracao("PARCIAL"), "texto", marcador("F1"), BLOCO
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == VALOR_INVALIDO


def test_fora_de_secao_vence_declaracao_orfa():
    texto = documento(
        declaracao("APROVADO"),
        "texto",
        cabecalho(),
        *unidade("F1", "APROVADO"),
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == FORA_DE_SECAO


def test_regime_e_julgado_antes_da_relacao_fisica():
    texto = documento(
        cabecalho(rotulo=ROTULO_ST1),
        declaracao("APROVADO"),
        "texto",
        marcador("F1"),
        BLOCO,
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == PROIBIDA


def test_primeira_violacao_fisica_encerra():
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_PARCIAL),
        marcador("F1"),
        BLOCO,
        cabecalho("R02", rotulo=ROTULO_ST1),
        declaracao("APROVADO"),
        marcador("F1"),
        BLOCO,
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == AUSENTE


def test_nada_e_devolvido_parcialmente():
    texto = documento(
        cabecalho("R01"),
        *unidade("F1", "APROVADO"),
        cabecalho("R02"),
        marcador("F1"),
        BLOCO,
    )
    with pytest.raises(DeclaracaoDeStatusInvalida):
        extrair_status_por_fragmento(texto)


def test_falha_e_deterministica_sob_repeticao():
    texto = documento(cabecalho(), marcador("F1"), BLOCO)
    mensagens = []
    for _ in range(20):
        with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
            extrair_status_por_fragmento(texto)
        mensagens.append(str(erro.value))
    assert mensagens == [AUSENTE] * 20


def test_sucesso_e_falha_intercalados_nao_acumulam_estado():
    bom = documento(cabecalho(), *unidade("F1", "APROVADO"))
    ruim = documento(cabecalho(), marcador("F1"), BLOCO)
    for _ in range(10):
        assert extrair_status_por_fragmento(bom) == (("R01/F1", "APROVADO"),)
        with pytest.raises(DeclaracaoDeStatusInvalida):
            extrair_status_por_fragmento(ruim)
    assert extrair_status_por_fragmento(bom) == (("R01/F1", "APROVADO"),)


# ---------------------------------------------------------------------------
# H. Invariante local x C12
# ---------------------------------------------------------------------------


def test_invariante_dispara_com_rotulo_divergente(monkeypatch):
    from casa77_sdr import response_fragment_status

    monkeypatch.setattr(
        response_fragment_status,
        "extrair_rotulos_de_cabecalho",
        lambda texto: (("R01", "APROVADO"),),
    )
    texto = documento(cabecalho(), *unidade("F1", "APROVADO"))
    with pytest.raises(RuntimeError) as erro:
        response_fragment_status.extrair_status_por_fragmento(texto)
    assert str(erro.value) == "invariante_estrutural"


def test_invariante_dispara_com_rxx_divergente(monkeypatch):
    from casa77_sdr import response_fragment_status

    monkeypatch.setattr(
        response_fragment_status,
        "extrair_rotulos_de_cabecalho",
        lambda texto: (("R99", ROTULO_PARCIAL),),
    )
    texto = documento(cabecalho(), *unidade("F1", "APROVADO"))
    with pytest.raises(RuntimeError) as erro:
        response_fragment_status.extrair_status_por_fragmento(texto)
    assert str(erro.value) == "invariante_estrutural"


def test_invariante_dispara_com_cardinalidade_divergente(monkeypatch):
    from casa77_sdr import response_fragment_status

    monkeypatch.setattr(
        response_fragment_status,
        "extrair_rotulos_de_cabecalho",
        lambda texto: (),
    )
    texto = documento(cabecalho(), *unidade("F1", "APROVADO"))
    with pytest.raises(RuntimeError) as erro:
        response_fragment_status.extrair_status_por_fragmento(texto)
    assert str(erro.value) == "invariante_estrutural"


def test_invariante_dispara_com_ordem_divergente(monkeypatch):
    from casa77_sdr import response_fragment_status

    monkeypatch.setattr(
        response_fragment_status,
        "extrair_rotulos_de_cabecalho",
        lambda texto: (("R02", ROTULO_PARCIAL), ("R01", ROTULO_PARCIAL)),
    )
    texto = documento(
        cabecalho("R01"),
        *unidade("F1", "APROVADO"),
        cabecalho("R02"),
        *unidade("F1", "APROVADO"),
    )
    with pytest.raises(RuntimeError) as erro:
        response_fragment_status.extrair_status_por_fragmento(texto)
    assert str(erro.value) == "invariante_estrutural"


def test_invariante_nao_e_declaracao_de_status_invalida(monkeypatch):
    from casa77_sdr import response_fragment_status

    monkeypatch.setattr(
        response_fragment_status,
        "extrair_rotulos_de_cabecalho",
        lambda texto: (),
    )
    texto = documento(cabecalho(), *unidade("F1", "APROVADO"))
    with pytest.raises(RuntimeError) as erro:
        response_fragment_status.extrair_status_por_fragmento(texto)
    assert type(erro.value) is RuntimeError
    assert not isinstance(erro.value, DeclaracaoDeStatusInvalida)
    assert erro.value.__cause__ is None
    assert erro.value.__context__ is None


def test_invariante_nao_dispara_quando_as_caminhadas_coincidem(monkeypatch):
    from casa77_sdr import response_fragment_status

    monkeypatch.setattr(
        response_fragment_status,
        "extrair_rotulos_de_cabecalho",
        lambda texto: (("R01", ROTULO_PARCIAL),),
    )
    texto = documento(cabecalho(), *unidade("F1", "BLOQUEADO"))
    assert response_fragment_status.extrair_status_por_fragmento(texto) == (
        ("R01/F1", "BLOQUEADO"),
    )


def test_invariante_e_verificado_antes_do_sucesso_e_nao_antes_da_falha(monkeypatch):
    """Uma violação `PM` física anterior encerra antes da comparação final."""
    from casa77_sdr import response_fragment_status

    monkeypatch.setattr(
        response_fragment_status,
        "extrair_rotulos_de_cabecalho",
        lambda texto: (),
    )
    texto = documento(cabecalho(), marcador("F1"), BLOCO)
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        response_fragment_status.extrair_status_por_fragmento(texto)
    assert str(erro.value) == AUSENTE


def test_homonimos_nao_sao_pareados_por_posicao():
    """Duas seções homônimas com rótulos distintos mantêm regimes distintos."""
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_PARCIAL),
        *unidade("F1", "APROVADO"),
        cabecalho("R01", rotulo=ROTULO_ST1),
        marcador("F1"),
        BLOCO,
        cabecalho("R01", rotulo=ROTULO_PARCIAL),
        *unidade("F1", "BLOQUEADO"),
    )
    assert extrair_status_por_fragmento(texto) == (
        ("R01/F1", "APROVADO"),
        ("R01/F1", "BLOQUEADO"),
    )


# ---------------------------------------------------------------------------
# I. Mensagens
# ---------------------------------------------------------------------------


CASOS_DE_ERRO = (
    (
        documento(cabecalho(), declaracao("PARCIAL"), marcador("F1"), BLOCO),
        VALOR_INVALIDO,
    ),
    (
        documento(declaracao("APROVADO"), "texto", cabecalho(), *unidade("F1")),
        FORA_DE_SECAO,
    ),
    (
        documento(
            cabecalho(rotulo=ROTULO_ST1),
            declaracao("APROVADO"),
            marcador("F1"),
            BLOCO,
        ),
        PROIBIDA,
    ),
    (
        documento(cabecalho(), declaracao("APROVADO"), "", marcador("F1"), BLOCO),
        ORFA,
    ),
    (documento(cabecalho(), marcador("F1"), BLOCO), AUSENTE),
)


@pytest.mark.parametrize("texto, mensagem", CASOS_DE_ERRO)
def test_mensagem_tem_categoria_e_localizador_fechados(texto, mensagem):
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert str(erro.value) == mensagem
    categoria, _, localizador = mensagem.partition(": ")
    assert categoria in CATEGORIAS
    assert localizador in LOCALIZADORES


def test_as_cinco_mensagens_sao_alcancaveis():
    alcancadas = []
    for texto, _ in CASOS_DE_ERRO:
        with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
            extrair_status_por_fragmento(texto)
        alcancadas.append(str(erro.value))
    assert sorted(alcancadas) == sorted(MENSAGENS)


def test_mapeamento_categoria_localizador_e_o_arbitrado():
    assert VALOR_INVALIDO == "valor_invalido: declaracao"
    assert FORA_DE_SECAO == "declaracao_fora_de_secao: declaracao"
    assert PROIBIDA == "declaracao_proibida: declaracao"
    assert ORFA == "declaracao_orfa: declaracao"
    assert AUSENTE == "declaracao_ausente: marcador"


def test_nenhuma_sexta_mensagem_e_produzida():
    entradas = [texto for texto, _ in CASOS_DE_ERRO]
    entradas.append(documento(cabecalho(), declaracao(""), marcador("F1"), BLOCO))
    entradas.append(
        documento(
            cabecalho(),
            *unidade("F1", "APROVADO"),
            declaracao("APROVADO"),
            terminador="",
        )
    )
    for texto in entradas:
        with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
            extrair_status_por_fragmento(texto)
        assert str(erro.value) in MENSAGENS


@pytest.mark.parametrize("texto, mensagem", CASOS_DE_ERRO)
def test_mensagem_nao_ecoa_rxx_id_token_valor_nem_rotulo(texto, mensagem):
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    saida = str(erro.value)
    for proibido in (
        "R01",
        "F1",
        "R01/F1",
        "APROVADO",
        "PARCIAL",
        "BLOQUEADO",
        "conteudo",
        "Titulo",
        "status-fragmento",
        "<!--",
    ):
        assert proibido not in saida


@pytest.mark.parametrize("texto, mensagem", CASOS_DE_ERRO)
def test_mensagem_nao_tem_linha_indice_nem_cardinalidade(texto, mensagem):
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert not any(caractere.isdigit() for caractere in str(erro.value))


@pytest.mark.parametrize("texto, mensagem", CASOS_DE_ERRO)
def test_mensagem_nao_tem_repr_nem_tipo_concreto(texto, mensagem):
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    saida = str(erro.value)
    for proibido in ("<", ">", "'", '"', "[", "]", "(", ")", "{", "}", "str"):
        assert proibido not in saida


@pytest.mark.parametrize("texto, mensagem", CASOS_DE_ERRO)
def test_excecao_da_c14_nao_tem_cause_nem_context(texto, mensagem):
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert erro.value.__cause__ is None
    assert erro.value.__context__ is None
    assert erro.value.__suppress_context__ is False


@pytest.mark.parametrize("texto, mensagem", CASOS_DE_ERRO)
def test_excecao_da_c14_carrega_um_unico_argumento(texto, mensagem):
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        extrair_status_por_fragmento(texto)
    assert erro.value.args == (mensagem,)


def test_mensagem_nao_muda_com_a_posicao_do_defeito():
    mensagens = []
    for extras in ([], ["texto"], ["texto", "outro"]):
        texto = documento(cabecalho(), *extras, marcador("F1"), BLOCO)
        with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
            extrair_status_por_fragmento(texto)
        mensagens.append(str(erro.value))
    assert mensagens == [AUSENTE] * 3


# ---------------------------------------------------------------------------
# J. Contrato publico
# ---------------------------------------------------------------------------


def test_all_tem_exatamente_dois_nomes():
    from casa77_sdr import response_fragment_status

    assert response_fragment_status.__all__ == [
        "DeclaracaoDeStatusInvalida",
        "extrair_status_por_fragmento",
    ]


def test_nao_ha_nome_publico_fora_de_all():
    from casa77_sdr import response_fragment_status

    publicos = {
        nome
        for nome in vars(response_fragment_status)
        if not nome.startswith("_")
        and nome not in {"annotations", "extrair_rotulos_de_cabecalho"}
    }
    assert publicos == set(response_fragment_status.__all__)


def test_assinatura_tem_um_unico_parametro_sem_default():
    assinatura = inspect.signature(extrair_status_por_fragmento)
    assert list(assinatura.parameters) == ["texto"]
    parametro = assinatura.parameters["texto"]
    assert parametro.default is inspect.Parameter.empty
    assert parametro.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD


def test_assinatura_nao_tem_parametro_de_contexto_ou_tolerancia():
    assinatura = inspect.signature(extrair_status_por_fragmento)
    proibidos = {
        "caminho",
        "arquivo",
        "modo",
        "tolerancia",
        "config",
        "indice",
        "rotulo",
        "rxx",
        "estrito",
    }
    assert not proibidos & set(assinatura.parameters)


def test_anotacao_de_retorno_e_tupla_de_pares():
    assinatura = inspect.signature(extrair_status_por_fragmento)
    assert assinatura.return_annotation == "tuple[tuple[str, str], ...]"


def test_excecao_deriva_diretamente_de_exception():
    assert DeclaracaoDeStatusInvalida.__bases__ == (Exception,)


def test_excecao_nao_e_subclasse_de_outro_erro_do_projeto():
    from casa77_sdr.response_bijection import BijecaoInvalida
    from casa77_sdr.response_status import StatusNaoCanonicalizavel

    for outra in (
        BijecaoInvalida,
        StatusNaoCanonicalizavel,
        CabecalhoRxxInvalido,
        RepresentacaoMarcadaInvalida,
    ):
        assert not issubclass(DeclaracaoDeStatusInvalida, outra)
        assert not issubclass(outra, DeclaracaoDeStatusInvalida)


def test_nao_e_exportado_pelo_pacote():
    assert not hasattr(casa77_sdr, "extrair_status_por_fragmento")
    assert not hasattr(casa77_sdr, "DeclaracaoDeStatusInvalida")
    assert "extrair_status_por_fragmento" not in getattr(casa77_sdr, "__all__", [])
    assert "DeclaracaoDeStatusInvalida" not in getattr(casa77_sdr, "__all__", [])


# ---------------------------------------------------------------------------
# K. Pureza do modulo de producao
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


def test_primeira_operacao_funcional_e_c12():
    funcao = next(
        no
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.FunctionDef)
        and no.name == "extrair_status_por_fragmento"
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


def test_nao_ha_global_nem_nonlocal():
    for no in ast.walk(ARVORE_PRODUCAO):
        assert not isinstance(no, (ast.Global, ast.Nonlocal))


def test_nao_ha_dict_nem_conjunto_no_codigo():
    assert not [
        no
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, (ast.Dict, ast.DictComp, ast.Set, ast.SetComp))
    ]
    proibidos = {"dict", "set", "frozenset", "Counter", "defaultdict", "OrderedDict"}
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_zip_nem_sorted():
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
        "hashlib",
        "logging",
        "getLogger",
        "cache",
        "lru_cache",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_regex_nem_unicodedata():
    proibidos = {"re", "regex", "match", "fullmatch", "search", "sub", "unicodedata"}
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_strip_nem_splitlines_nem_normalizacao():
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


def test_nao_ha_enum_nem_dataclass():
    proibidos = {"Enum", "StrEnum", "dataclass", "NamedTuple", "TypedDict"}
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_assert_em_producao():
    for no in ast.walk(ARVORE_PRODUCAO):
        assert not isinstance(no, ast.Assert)


def test_producao_nao_menciona_knowledge_caminho_nem_url():
    for constante in _constantes_de_codigo():
        assert "knowledge" not in constante
        assert ".yaml" not in constante
        assert ".md" not in constante
        assert ".env" not in constante
        assert "http" not in constante
        assert "C:" not in constante
        assert "/home/" not in constante


def test_producao_declara_uma_unica_classe():
    classes = [no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.ClassDef)]
    assert [classe.name for classe in classes] == ["DeclaracaoDeStatusInvalida"]


def test_producao_declara_uma_unica_funcao_publica():
    funcoes = [
        no.name
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    assert funcoes[0] == "extrair_status_por_fragmento"
    assert all(nome.startswith("_") for nome in funcoes[1:])


def test_nao_ha_estado_mutavel_no_modulo():
    from casa77_sdr import response_fragment_status

    for nome, valor in vars(response_fragment_status).items():
        if nome.startswith("__") and nome.endswith("__"):
            continue
        if nome == "annotations":
            continue
        assert not isinstance(valor, (list, dict, set, bytearray))


def test_o_vocabulario_privado_e_uma_tupla_de_tres():
    from casa77_sdr import response_fragment_status

    valores = response_fragment_status._VALORES_CANONICOS
    assert isinstance(valores, tuple)
    assert valores == VALORES


def test_o_rotulo_do_regime_e_parcial():
    from casa77_sdr import response_fragment_status

    assert response_fragment_status._ROTULO_DO_REGIME == "PARCIAL"


def test_o_vocabulario_nao_e_alterado_pelas_chamadas():
    from casa77_sdr import response_fragment_status

    antes = response_fragment_status._VALORES_CANONICOS
    extrair_status_por_fragmento(documento(cabecalho(), *unidade("F1")))
    with pytest.raises(DeclaracaoDeStatusInvalida):
        extrair_status_por_fragmento(documento(cabecalho(), marcador("F1"), BLOCO))
    assert response_fragment_status._VALORES_CANONICOS is antes


def test_resultado_nao_depende_de_variavel_de_ambiente(monkeypatch):
    monkeypatch.setenv("LANG", "tr_TR.UTF-8")
    monkeypatch.setenv("LC_ALL", "tr_TR.UTF-8")
    monkeypatch.setenv("PYTHONHASHSEED", "0")
    texto = documento(cabecalho(), *unidade("F1", "APROVADO"))
    assert extrair_status_por_fragmento(texto) == (("R01/F1", "APROVADO"),)


# ---------------------------------------------------------------------------
# L. Limites — o que um retorno bem-sucedido NAO afirma
# ---------------------------------------------------------------------------


def test_sucesso_nao_prova_unicidade_global():
    texto = documento(
        cabecalho("R01"),
        *unidade("F1", "APROVADO"),
        cabecalho("R01"),
        *unidade("F1", "APROVADO"),
    )
    pares = extrair_status_por_fragmento(texto)
    assert len(pares) == 2
    assert pares[0] == pares[1]


def test_sucesso_nao_afirma_nada_sobre_secoes_nao_parciais():
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_ST1),
        marcador("F1"),
        BLOCO,
        cabecalho("R02", rotulo="rotulo desconhecido"),
        marcador("F1"),
        BLOCO,
    )
    assert extrair_status_por_fragmento(texto) == ()


def test_rotulo_desconhecido_continua_valido_sem_declaracao():
    texto = documento(
        cabecalho(rotulo="rotulo desconhecido"), marcador("F1"), BLOCO
    )
    assert extrair_status_por_fragmento(texto) == ()


def test_nenhum_teste_desta_suite_toca_o_corpus():
    """A suíte é sintética: nada aqui lê o corpus versionado.

    Os alvos da busca são montados por concatenação para que a própria
    asserção não os introduza no arquivo e invalide o teste.
    """
    fonte = Path(__file__).read_text(encoding="utf-8")
    assert ("respostas" + "-aprovadas") not in fonte
    assert ("casa77" + ".yaml") not in fonte
    assert ("open" + "(") not in fonte

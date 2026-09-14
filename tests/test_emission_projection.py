"""`ProjetorEmissao` — projeção dos fragmentos destinados à emissão.

Esta suíte exercita a fronteira sobre **identificadores sintéticos** e, no fim,
sobre o **índice físico real**, apenas como *gate* das pré-condições da tabela.
**Zero valor comercial** é reproduzido: nenhum preço, capacidade, horário,
prazo, percentual, quantidade ou frase aprovada aparece no código — nem o corpo
textual de fragmento algum.
"""

from __future__ import annotations

import ast
import copy
from pathlib import Path
from typing import Any

import pytest

from casa77_sdr.emission_projection import (
    ProjecaoEmissaoNaoAvaliavel,
    projetar_fragmentos_para_emissao,
)
from casa77_sdr.response_index_load import carregar_indice
from casa77_sdr.response_index_status import consultar_status
from casa77_sdr.response_index_tokens import derivar_tokens_do_indice
from casa77_sdr.state_machine import AcaoMaquina

RAIZ = Path(__file__).resolve().parents[1]
INDICE = RAIZ / "knowledge" / "indice-respostas-aprovadas.yaml"
MODULO_PE = RAIZ / "src" / "casa77_sdr" / "emission_projection.py"
MODULO_MAQUINA = RAIZ / "src" / "casa77_sdr" / "state_machine.py"

# Cardinalidade estrutural do vocabulário fechado de §4.5 — contagem, não dado
# comercial.
TOTAL_ACOES = 20

# Identificadores **sintéticos**: `Rxx` fora do corpus vigente, usados apenas
# como referência estrutural opaca. A fronteira não consulta o índice.
A = "R97/F1"
B = "R98/F1"
C = "R99/F1"

# O único mandatório materializado nesta versão. Ele é lido da própria tabela
# privada, nunca copiado — ver `test_pe_t16`.
LACUNA = "R03/F1"


def _tabela() -> dict[AcaoMaquina, tuple[str, ...]]:
    """A tabela privada, lida da fronteira — nunca reescrita aqui."""
    import casa77_sdr.emission_projection as modulo

    return modulo._FRAGMENTOS_POR_ACAO


# Ações cuja contribuição declarada é vazia, escolhidas para cobrir **as duas**
# naturezas exigidas: textual e não textual.
ACAO_TEXTUAL_SEM_FRAGMENTO = AcaoMaquina.INFORMAR_CONDICOES_DE_VISITA
ACAO_NAO_TEXTUAL = AcaoMaquina.PREPARAR_RESUMO


# ---------------------------------------------------------------------------
# PE-T1 — somente os identificadores recebidos


def test_pe_t1_somente_recebidos_sem_contribuicao() -> None:
    resultado = projetar_fragmentos_para_emissao(
        (A,), (AcaoMaquina.RESPONDER_PERGUNTA_COMERCIAL,)
    )

    assert resultado == (A,)


def test_pe_t1_entrada_totalmente_vazia_e_sucesso_vazio() -> None:
    assert projetar_fragmentos_para_emissao((), ()) == ()


# ---------------------------------------------------------------------------
# PE-T2 — somente a lacuna


def test_pe_t2_somente_lacuna() -> None:
    resultado = projetar_fragmentos_para_emissao(
        (), (AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO,)
    )

    assert resultado == (LACUNA,)


# ---------------------------------------------------------------------------
# PE-T3 — cobertura mista


def test_pe_t3_mista_põe_a_lacuna_ao_final() -> None:
    resultado = projetar_fragmentos_para_emissao(
        (A, B), (AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO,)
    )

    assert resultado == (A, B, LACUNA)


def test_pe_t3_lacuna_fica_ao_final_mesmo_com_acoes_antes_e_depois() -> None:
    resultado = projetar_fragmentos_para_emissao(
        (A,),
        (
            AcaoMaquina.RESPONDER_PERGUNTA_COMERCIAL,
            AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO,
            AcaoMaquina.PREPARAR_RESUMO,
        ),
    )

    assert resultado == (A, LACUNA)


# ---------------------------------------------------------------------------
# PE-T4 — colisão entre as duas origens


def test_pe_t4_conflito_cross_source() -> None:
    with pytest.raises(ProjecaoEmissaoNaoAvaliavel) as erro:
        projetar_fragmentos_para_emissao(
            (LACUNA,), (AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO,)
        )

    assert str(erro.value) == "conflito_origem: fragmentos_autorizados.item"


def test_pe_t4_conflito_nao_devolve_resultado_parcial() -> None:
    resultado = None
    with pytest.raises(ProjecaoEmissaoNaoAvaliavel):
        resultado = projetar_fragmentos_para_emissao(
            (A, LACUNA, B), (AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO,)
        )

    assert resultado is None


def test_pe_t4_sem_a_acao_o_mesmo_identificador_nao_conflita() -> None:
    """O conflito é **entre as duas origens**, não uma proibição do token."""
    resultado = projetar_fragmentos_para_emissao(
        (LACUNA,), (AcaoMaquina.RESPONDER_PERGUNTA_COMERCIAL,)
    )

    assert resultado == (LACUNA,)


# ---------------------------------------------------------------------------
# PE-T5 — ações vazias


def test_pe_t5_acoes_vazias_preservam_os_recebidos() -> None:
    assert projetar_fragmentos_para_emissao((A, B, C), ()) == (A, B, C)


# ---------------------------------------------------------------------------
# PE-T6 — ações canônicas cuja contribuição é vazia


@pytest.mark.parametrize(
    "acao",
    [ACAO_TEXTUAL_SEM_FRAGMENTO, ACAO_NAO_TEXTUAL],
    ids=["textual", "nao_textual"],
)
def test_pe_t6_acao_sem_contribuicao_e_sucesso_normal(acao: AcaoMaquina) -> None:
    """Tupla vazia **não** é erro, e **não** afirma que a ação foi atendida."""
    assert projetar_fragmentos_para_emissao((A,), (acao,)) == (A,)
    assert projetar_fragmentos_para_emissao((), (acao,)) == ()


def test_pe_t6_todas_as_acoes_sem_contribuicao_sao_aceitas() -> None:
    tabela = _tabela()
    vazias = tuple(acao for acao, tokens in tabela.items() if not tokens)

    assert projetar_fragmentos_para_emissao((A,), vazias) == (A,)


# ---------------------------------------------------------------------------
# PE-T7 — ação repetida contribui uma única vez


def test_pe_t7_acao_repetida_nao_duplica_o_mandatorio() -> None:
    resultado = projetar_fragmentos_para_emissao(
        (A,),
        (
            AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO,
            AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO,
            AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO,
        ),
    )

    assert resultado == (A, LACUNA)


# ---------------------------------------------------------------------------
# PE-T8 — tipos exatos das duas entradas


@pytest.mark.parametrize(
    "entrada",
    [None, [A], {A}, A, iter((A,))],
    ids=["nulo", "lista", "conjunto", "texto", "gerador"],
)
def test_pe_t8_recebidos_precisam_ser_tupla(entrada: object) -> None:
    with pytest.raises(ProjecaoEmissaoNaoAvaliavel) as erro:
        projetar_fragmentos_para_emissao(entrada, ())

    assert str(erro.value) == "tipo_invalido: fragmentos_autorizados"


@pytest.mark.parametrize(
    "item",
    [None, 0, ("R97", "F1"), AcaoMaquina.PREPARAR_RESUMO],
    ids=["nulo", "inteiro", "tupla", "acao"],
)
def test_pe_t8_item_recebido_precisa_ser_str_exata(item: object) -> None:
    with pytest.raises(ProjecaoEmissaoNaoAvaliavel) as erro:
        projetar_fragmentos_para_emissao((item,), ())

    assert str(erro.value) == "tipo_invalido: fragmentos_autorizados.item"


def test_pe_t8_subclasse_de_str_nao_e_forma_canonica() -> None:
    class Identificador(str):
        pass

    with pytest.raises(ProjecaoEmissaoNaoAvaliavel) as erro:
        projetar_fragmentos_para_emissao((Identificador(A),), ())

    assert str(erro.value) == "tipo_invalido: fragmentos_autorizados.item"


@pytest.mark.parametrize(
    "entrada",
    [None, [AcaoMaquina.PREPARAR_RESUMO], {AcaoMaquina.PREPARAR_RESUMO}, "acoes"],
    ids=["nulo", "lista", "conjunto", "texto"],
)
def test_pe_t8_acoes_precisam_ser_tupla(entrada: object) -> None:
    with pytest.raises(ProjecaoEmissaoNaoAvaliavel) as erro:
        projetar_fragmentos_para_emissao((), entrada)

    assert str(erro.value) == "tipo_invalido: acoes"


@pytest.mark.parametrize(
    "item",
    [None, 0, "informar_lacuna_de_informacao", A],
    ids=["nulo", "inteiro", "valor_do_enum", "token"],
)
def test_pe_t8_item_de_acoes_precisa_ser_acao_canonica(item: object) -> None:
    with pytest.raises(ProjecaoEmissaoNaoAvaliavel) as erro:
        projetar_fragmentos_para_emissao((), (item,))

    assert str(erro.value) == "tipo_invalido: acoes.item"


def test_pe_t8_precedencia_recebidos_antes_de_acoes() -> None:
    """A forma dos recebidos é exigida **antes** da forma das ações."""
    with pytest.raises(ProjecaoEmissaoNaoAvaliavel) as erro:
        projetar_fragmentos_para_emissao([A], [AcaoMaquina.PREPARAR_RESUMO])

    assert str(erro.value) == "tipo_invalido: fragmentos_autorizados"


# ---------------------------------------------------------------------------
# PE-T9 — repetição no bloco recebido


def test_pe_t9_recebido_duplicado_fecha() -> None:
    with pytest.raises(ProjecaoEmissaoNaoAvaliavel) as erro:
        projetar_fragmentos_para_emissao((A, A), ())

    assert str(erro.value) == "duplicidade: fragmentos_autorizados.item"


def test_pe_t9_duplicata_nao_adjacente_tambem_fecha() -> None:
    with pytest.raises(ProjecaoEmissaoNaoAvaliavel):
        projetar_fragmentos_para_emissao((A, B, C, A), ())


# ---------------------------------------------------------------------------
# PE-T10 — ordem


def test_pe_t10_ordem_dos_recebidos_e_preservada() -> None:
    assert projetar_fragmentos_para_emissao((C, A, B), ()) == (C, A, B)


def test_pe_t10_mandatorios_seguem_a_ordem_das_acoes() -> None:
    """Com um só mandatório vigente, a prova é a sua posição terminal."""
    resultado = projetar_fragmentos_para_emissao(
        (C, A),
        (
            AcaoMaquina.PREPARAR_RESUMO,
            AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO,
        ),
    )

    assert resultado == (C, A, LACUNA)
    assert resultado[-1] == LACUNA


def test_pe_t10_nenhuma_ordenacao_lexical_e_aplicada() -> None:
    recebidos = (C, B, A)

    assert projetar_fragmentos_para_emissao(recebidos, ()) == recebidos
    assert projetar_fragmentos_para_emissao(recebidos, ()) != tuple(sorted(recebidos))


# ---------------------------------------------------------------------------
# PE-T11 — zero mutação


def test_pe_t11_nenhuma_entrada_e_mutada() -> None:
    recebidos = (A, B)
    acoes = (
        AcaoMaquina.RESPONDER_PERGUNTA_COMERCIAL,
        AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO,
    )
    copia_recebidos = copy.deepcopy(recebidos)
    copia_acoes = copy.deepcopy(acoes)
    copia_tabela = copy.deepcopy(_tabela())

    projetar_fragmentos_para_emissao(recebidos, acoes)

    assert recebidos == copia_recebidos
    assert acoes == copia_acoes
    assert _tabela() == copia_tabela


# ---------------------------------------------------------------------------
# PE-T12 — determinismo


def test_pe_t12_duas_execucoes_dao_o_mesmo_resultado() -> None:
    recebidos = (B, A)
    acoes = (AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO,)

    primeira = projetar_fragmentos_para_emissao(recebidos, acoes)
    segunda = projetar_fragmentos_para_emissao(recebidos, acoes)

    assert primeira == segunda == (B, A, LACUNA)


# ---------------------------------------------------------------------------
# PE-T13 — isolamento estrutural


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


def test_pe_t13_importa_somente_o_necessario() -> None:
    assert _modulos_importados(MODULO_PE) == {
        "__future__",
        "casa77_sdr.state_machine",
    }


@pytest.mark.parametrize(
    "proibido",
    [
        "casa77_sdr.response_index",
        "casa77_sdr.response_index_load",
        "casa77_sdr.response_index_status",
        "casa77_sdr.response_index_tokens",
        "casa77_sdr.fact_selection",
        "casa77_sdr.response_composition",
        "casa77_sdr.response_placeholder",
        "casa77_sdr.response_format",
        "casa77_sdr.response_yaml_resolve",
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
        "random",
    ],
)
def test_pe_t13_nao_importa_fronteira_proibida(proibido: str) -> None:
    assert proibido not in _modulos_importados(MODULO_PE)


def test_pe_t13_nao_abre_arquivo_nem_consulta_corpus() -> None:
    chamados: set[str] = set()
    for no in ast.walk(_arvore(MODULO_PE)):
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
        "safe_load",
        "sorted",
    ):
        assert proibido not in chamados


def test_pe_t13_superficie_publica_e_minima() -> None:
    import casa77_sdr.emission_projection as modulo

    assert sorted(modulo.__all__) == [
        "ProjecaoEmissaoNaoAvaliavel",
        "projetar_fragmentos_para_emissao",
    ]
    # A tabela é privada: ela **não** é API pública.
    assert "_FRAGMENTOS_POR_ACAO" not in modulo.__all__


def test_pe_t13_nao_conhece_vocabulario_de_montante() -> None:
    """Nenhum objeto de domínio de montante é nomeado na fronteira.

    A prova de que `knowledge/**` não é **acessado** é a de AST, acima; aqui o
    que se verifica é ausência de **vocabulário**, e por isso a negativa em
    prosa do próprio módulo não é contada.
    """
    fonte = MODULO_PE.read_text(encoding="utf-8").casefold()

    for termo in (
        "PerguntaComercial",
        "AssuntoComercial",
        "ResultadoSelecaoFatos",
        "ResultadoComposicao",
        "Transicao",
        "witness",
        "casa77.yaml",
        "indice-respostas",
    ):
        assert termo.casefold() not in fonte


# ---------------------------------------------------------------------------
# PE-T14 — a máquina permanece sem `Rxx` e sem depender do projetor


def test_pe_t14_maquina_nao_importa_o_projetor() -> None:
    assert "casa77_sdr.emission_projection" not in _modulos_importados(MODULO_MAQUINA)


def test_pe_t14_maquina_nao_contem_literal_estrutural_de_fragmento() -> None:
    """A correspondência ação → fragmento vive **fora** da máquina (§4.5)."""
    literais = [
        no.value
        for no in ast.walk(_arvore(MODULO_MAQUINA))
        if isinstance(no, ast.Constant) and isinstance(no.value, str)
    ]

    for literal in literais:
        assert "/F" not in literal
        # `Rxx` isolado: dois dígitos após `R`, na forma fechada de `C-2b`.
        for posicao in range(len(literal) - 2):
            trecho = literal[posicao : posicao + 3]
            assert not (
                trecho[0] == "R" and trecho[1].isdigit() and trecho[2].isdigit()
            )


# ---------------------------------------------------------------------------
# PE-T15 — a tabela é total


def test_pe_t15_tabela_cobre_exatamente_o_vocabulario_fechado() -> None:
    tabela = _tabela()

    assert len(AcaoMaquina) == TOTAL_ACOES
    assert set(tabela) == set(AcaoMaquina)
    assert len(tabela) == TOTAL_ACOES


def test_pe_t15_toda_entrada_e_tupla_de_str() -> None:
    for acao, tokens in _tabela().items():
        assert type(acao) is AcaoMaquina
        assert type(tokens) is tuple
        for token in tokens:
            assert type(token) is str


def test_pe_t15_tabela_e_literal_e_nao_gerada() -> None:
    """Uma 21ª ação precisa quebrar a totalidade, não ser absorvida."""
    fonte = MODULO_PE.read_text(encoding="utf-8")

    assert "for acao in AcaoMaquina" not in fonte
    assert "in AcaoMaquina}" not in fonte
    assert "dict.fromkeys" not in fonte
    # Cada ação aparece escrita literalmente na tabela.
    for acao in AcaoMaquina:
        assert f"AcaoMaquina.{acao.name}:" in fonte


# ---------------------------------------------------------------------------
# PE-T16 — exatamente uma contribuição materializada


def test_pe_t16_somente_a_lacuna_contribui() -> None:
    tabela = _tabela()
    com_token = {acao: tokens for acao, tokens in tabela.items() if tokens}

    assert list(com_token) == [AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO]
    assert com_token[AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO] == (LACUNA,)


@pytest.mark.parametrize(
    "nao_mapeado",
    ["R01/F1", "R05/F1", "R06/F1", "R08/F1", "R15/F1"],
)
def test_pe_t16_nenhum_outro_fragmento_e_mapeado(nao_mapeado: str) -> None:
    declarados = {token for tokens in _tabela().values() for token in tokens}

    assert nao_mapeado not in declarados


# ---------------------------------------------------------------------------
# PE-T17 — gate mecânico do corpus físico


@pytest.fixture(scope="module")
def indice_real() -> dict[str, Any]:
    return carregar_indice(INDICE)


def _fragmento_do_token(indice: dict[str, Any], token: str) -> dict[str, Any]:
    for resposta in indice["respostas"]:
        for fragmento in resposta["fragmentos"]:
            if f"{resposta['id']}/{fragmento['id']}" == token:
                return fragmento
    raise AssertionError("token mandatório ausente do índice físico")


def test_pe_t17_mandatorios_existem_no_dominio_canonico(
    indice_real: dict[str, Any],
) -> None:
    dominio = set(derivar_tokens_do_indice(indice_real))
    declarados = [token for tokens in _tabela().values() for token in tokens]

    assert declarados, "a tabela precisa declarar ao menos um mandatório"
    for token in declarados:
        assert token in dominio


def test_pe_t17_mandatorios_tem_rotulo_canonico_emitivel(
    indice_real: dict[str, Any],
) -> None:
    declarados = [token for tokens in _tabela().values() for token in tokens]

    for token in declarados:
        assert consultar_status(indice_real, token) == "APROVADO"


def test_pe_t17_mandatorios_nao_tem_binding_algum(
    indice_real: dict[str, Any],
) -> None:
    """Zero *binding* torna qualquer juízo factual de runtime desnecessário.

    Se um mandatório futuro ganhar `RENDERIZADO`, `ASSERTIVA` ou fato de
    runtime, este teste fica vermelho **de propósito**: a admissibilidade
    passaria a depender de decisão factual, e isso exige nova arbitragem.
    """
    declarados = [token for tokens in _tabela().values() for token in tokens]

    for token in declarados:
        fragmento = _fragmento_do_token(indice_real, token)
        assert fragmento["bindings"] == []
        assert "itera_sobre" not in fragmento


def test_pe_t17_hoje_existe_exatamente_um_mandatorio() -> None:
    declarados = [token for tokens in _tabela().values() for token in tokens]

    assert len(declarados) == 1
    assert len(set(declarados)) == 1


# ---------------------------------------------------------------------------
# PE-T18 — as mensagens não carregam conteúdo recebido


@pytest.mark.parametrize(
    ("recebidos", "acoes"),
    [
        (("R97/F1", "R97/F1"), ()),
        (("R03/F1",), (AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO,)),
        ((0,), ()),
        ((), ("informar_lacuna_de_informacao",)),
    ],
    ids=["duplicidade", "conflito", "token_invalido", "acao_invalida"],
)
def test_pe_t18_mensagens_nao_ecoam_conteudo(
    recebidos: object, acoes: object
) -> None:
    with pytest.raises(ProjecaoEmissaoNaoAvaliavel) as erro:
        projetar_fragmentos_para_emissao(recebidos, acoes)

    mensagem = str(erro.value)

    assert "R97" not in mensagem
    assert "R03" not in mensagem
    assert "lacuna" not in mensagem
    assert "informar" not in mensagem
    # Forma canônica `<categoria>: <localizador>`, e nada mais.
    categoria, _, localizador = mensagem.partition(": ")
    assert categoria in {
        "tipo_invalido",
        "duplicidade",
        "acao_sem_mapeamento",
        "conflito_origem",
    }
    assert localizador in {
        "fragmentos_autorizados",
        "fragmentos_autorizados.item",
        "acoes",
        "acoes.item",
    }

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
from casa77_sdr.fragment_emissibility import FotografiaFragmento
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

# Os três identificadores materializados nesta versão são `R03/F1`, `R05/F1` e
# `R06/F1` — os dois primeiros logo abaixo, o terceiro adiante. Eles são lidos
# da própria tabela privada, nunca copiados — ver `test_pe_t16`.
LACUNA = "R03/F1"
FALLBACK = "R05/F1"

# A ação de T15, dona da primeira dupla rota autorizada (PE-13).
ACAO_T15 = AcaoMaquina.INFORMAR_NAO_CONFIRMACAO_DE_DISPONIBILIDADE

# Variantes da mesma superfície R05 que dependem da fotografia runtime e que,
# com a ação de T15, são insumos contraditórios (PE-14).
VARIANTE_DISPONIVEL = "R05/F2"
VARIANTE_INDISPONIVEL = "R05/F3"

# A segunda dupla rota, com regra **propria**: `R06/F1` tem *bindings* de origem
# `YAML`, e por isso a rota da acao so o acrescenta com veredito da autoridade
# unica de emissibilidade (PE-15+).
VISITA = "R06/F1"
ACAO_T16 = AcaoMaquina.INFORMAR_CONDICOES_DE_VISITA

# Rotulos canonicos de `C-3` e caminhos **sinteticos**, na forma estrutural de um
# `caminho_yaml`. Nenhum conteudo do corpus e reproduzido.
APROVADO = "APROVADO"
AGUARDA = "AGUARDA_APROVACAO"
BLOQUEADO = "BLOQUEADO"
CAMINHO_A = "secao_sintetica.campo_a"
CAMINHO_B = "secao_sintetica.campo_b"

EMITIVEL = FotografiaFragmento(status=APROVADO)


def _tabela() -> dict[AcaoMaquina, tuple[str, ...]]:
    """A tabela privada, lida da fronteira — nunca reescrita aqui."""
    import casa77_sdr.emission_projection as modulo

    return modulo._FRAGMENTOS_POR_ACAO


# Ações cuja contribuição declarada é vazia, escolhidas para cobrir **as duas**
# naturezas exigidas: textual e não textual.
# `INFORMAR_CONDICOES_DE_VISITA` deixou de servir de exemplo: ela passou a ter
# contribuicao materializada (`R06/F1`). `INFORMAR_REGRA_INCOMPATIVEL` continua
# sendo exemplo **legitimo** de acao **textual** sem unidade aprovada: a
# superficie da **incompatibilidade dependente de motivo** permanece
# explicitamente aberta no item 22 de `docs/07` §12, e `PE-7` continua valendo
# sobre ela — `()` diz **somente** que esta fronteira nada acrescenta.
ACAO_TEXTUAL_SEM_FRAGMENTO = AcaoMaquina.INFORMAR_REGRA_INCOMPATIVEL
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
# PE-T19 — dupla rota fechada de `R05/F1` (PE-13)


def test_pe_t19_cenario_a_acao_completa_quando_a_cobertura_nao_trouxe() -> None:
    """Cenário A: sem cobertura, a ação de T15 é a *owner* da unidade."""
    resultado = projetar_fragmentos_para_emissao((), (ACAO_T15,))

    assert resultado == (FALLBACK,)


def test_pe_t19_cobertura_comercial_anterior_recebe_o_fallback_ao_final() -> None:
    resultado = projetar_fragmentos_para_emissao((A,), (ACAO_T15,))

    assert resultado == (A, FALLBACK)


def test_pe_t19_cenario_b_cobertura_e_owner_e_nao_duplica() -> None:
    """Cenário B: a cobertura já trouxe o token — zero erro, zero duplicata."""
    resultado = projetar_fragmentos_para_emissao((FALLBACK,), (ACAO_T15,))

    assert resultado == (FALLBACK,)
    assert resultado.count(FALLBACK) == 1


def test_pe_t19_cobertura_owner_preserva_a_posicao_original() -> None:
    """O token compartilhado **não** vai para o fim: PE-4 e PE-8 intactas."""
    recebidos = ("R04/F1", FALLBACK, "R07/F1")

    resultado = projetar_fragmentos_para_emissao(recebidos, (ACAO_T15,))

    assert resultado == recebidos


def test_pe_t19_acao_repetida_sem_cobertura_contribui_uma_vez() -> None:
    resultado = projetar_fragmentos_para_emissao(
        (), (ACAO_T15, ACAO_T15, ACAO_T15)
    )

    assert resultado == (FALLBACK,)


def test_pe_t19_acao_repetida_com_cobertura_continua_uma_ocorrencia() -> None:
    resultado = projetar_fragmentos_para_emissao(
        (FALLBACK,), (ACAO_T15, ACAO_T15)
    )

    assert resultado == (FALLBACK,)


# ---------------------------------------------------------------------------
# PE-T20 — variantes incompatíveis da superfície R05 (PE-14)


@pytest.mark.parametrize(
    "variante",
    [VARIANTE_DISPONIVEL, VARIANTE_INDISPONIVEL],
    ids=["disponivel", "indisponivel"],
)
def test_pe_t20_variante_de_runtime_com_a_acao_de_t15_fecha(variante: str) -> None:
    """T15 ordena o *fallback* de não confirmação: F2/F3 contradizem."""
    with pytest.raises(ProjecaoEmissaoNaoAvaliavel) as erro:
        projetar_fragmentos_para_emissao((variante,), (ACAO_T15,))

    assert str(erro.value) == "conflito_origem: fragmentos_autorizados.item"


@pytest.mark.parametrize(
    "variante",
    [VARIANTE_DISPONIVEL, VARIANTE_INDISPONIVEL],
    ids=["disponivel", "indisponivel"],
)
def test_pe_t20_variante_sem_a_acao_de_t15_atravessa(variante: str) -> None:
    """A incompatibilidade é **com a ação**, não uma proibição do token."""
    resultado = projetar_fragmentos_para_emissao(
        (variante,), (AcaoMaquina.RESPONDER_PERGUNTA_COMERCIAL,)
    )

    assert resultado == (variante,)


def test_pe_t20_variante_fecha_mesmo_com_o_fallback_presente() -> None:
    with pytest.raises(ProjecaoEmissaoNaoAvaliavel):
        projetar_fragmentos_para_emissao(
            (FALLBACK, VARIANTE_DISPONIVEL), (ACAO_T15,)
        )


def test_pe_t20_variante_nao_devolve_resultado_parcial() -> None:
    resultado = None
    with pytest.raises(ProjecaoEmissaoNaoAvaliavel):
        resultado = projetar_fragmentos_para_emissao(
            (A, VARIANTE_INDISPONIVEL, B), (ACAO_T15,)
        )

    assert resultado is None


# ---------------------------------------------------------------------------
# PE-T21 — a exceção de `R05/F1` não vaza (PE-10 por padrão)


def test_pe_t21_lacuna_continua_fail_closed_cross_source() -> None:
    """`R03/F1` **não** ganha dupla rota: colisão continua fechando."""
    with pytest.raises(ProjecaoEmissaoNaoAvaliavel) as erro:
        projetar_fragmentos_para_emissao(
            (LACUNA,), (AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO,)
        )

    assert str(erro.value) == "conflito_origem: fragmentos_autorizados.item"


def test_pe_t21_lacuna_fecha_mesmo_junto_da_dupla_rota_valida() -> None:
    """Uma exceção fechada convivendo com a regra geral não a contamina."""
    with pytest.raises(ProjecaoEmissaoNaoAvaliavel) as erro:
        projetar_fragmentos_para_emissao(
            (LACUNA, FALLBACK),
            (ACAO_T15, AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO),
        )

    assert str(erro.value) == "conflito_origem: fragmentos_autorizados.item"


def test_pe_t21_as_duas_rotas_convivem_quando_nao_ha_colisao() -> None:
    """Lacuna aportada pela ação e *fallback* vindo da cobertura."""
    resultado = projetar_fragmentos_para_emissao(
        (FALLBACK,),
        (ACAO_T15, AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO),
    )

    assert resultado == (FALLBACK, LACUNA)


# ---------------------------------------------------------------------------
# PE-T22 — owner de `R06/F1`, a segunda dupla rota


def test_pe_t22_acao_owner_acrescenta_quando_emitivel() -> None:
    resultado = projetar_fragmentos_para_emissao(
        (), (ACAO_T16,), fotografia_r06=EMITIVEL
    )

    assert resultado == (VISITA,)


def test_pe_t22_cobertura_comercial_anterior_recebe_a_visita_ao_final() -> None:
    resultado = projetar_fragmentos_para_emissao(
        (A,), (ACAO_T16,), fotografia_r06=EMITIVEL
    )

    assert resultado == (A, VISITA)


def test_pe_t22_cobertura_owner_nao_duplica() -> None:
    resultado = projetar_fragmentos_para_emissao(
        (VISITA,), (ACAO_T16,), fotografia_r06=EMITIVEL
    )

    assert resultado == (VISITA,)
    assert resultado.count(VISITA) == 1


def test_pe_t22_cobertura_owner_preserva_a_posicao_original() -> None:
    recebidos = (A, VISITA, B)

    resultado = projetar_fragmentos_para_emissao(
        recebidos, (ACAO_T16,), fotografia_r06=EMITIVEL
    )

    assert resultado == recebidos


def test_pe_t22_cobertura_owner_dispensa_a_fotografia() -> None:
    """A rota da cobertura **não** consulta a fotografia."""
    resultado = projetar_fragmentos_para_emissao((VISITA,), (ACAO_T16,))

    assert resultado == (VISITA,)


@pytest.mark.parametrize(
    "irrelevante",
    [None, "fotografia", 0, object()],
    ids=["nulo", "texto", "inteiro", "objeto"],
)
def test_pe_t22_cobertura_owner_ignora_fotografia_invalida(
    irrelevante: object,
) -> None:
    resultado = projetar_fragmentos_para_emissao(
        (VISITA,), (ACAO_T16,), fotografia_r06=irrelevante
    )

    assert resultado == (VISITA,)


@pytest.mark.parametrize(
    "irrelevante",
    [None, "fotografia", 0, object()],
    ids=["nulo", "texto", "inteiro", "objeto"],
)
def test_pe_t22_sem_a_acao_de_t16_a_fotografia_e_irrelevante(
    irrelevante: object,
) -> None:
    resultado = projetar_fragmentos_para_emissao(
        (A,),
        (AcaoMaquina.RESPONDER_PERGUNTA_COMERCIAL,),
        fotografia_r06=irrelevante,
    )

    assert resultado == (A,)


def test_pe_t22_acao_repetida_com_emitivel_contribui_uma_vez() -> None:
    resultado = projetar_fragmentos_para_emissao(
        (), (ACAO_T16, ACAO_T16, ACAO_T16), fotografia_r06=EMITIVEL
    )

    assert resultado == (VISITA,)


# ---------------------------------------------------------------------------
# PE-T23 — `R06/F1` não emitível: zero fragmento, sob `PE-7`


@pytest.mark.parametrize(
    "fotografia",
    [
        FotografiaFragmento(status=AGUARDA),
        FotografiaFragmento(status=BLOQUEADO),
        FotografiaFragmento(status=APROVADO, divergente=True),
        FotografiaFragmento(status=APROVADO, referentes_indisponiveis=(CAMINHO_A,)),
        FotografiaFragmento(
            status=APROVADO, referentes_indisponiveis=(CAMINHO_A, CAMINHO_B)
        ),
        FotografiaFragmento(
            status=APROVADO,
            divergente=True,
            referentes_indisponiveis=(CAMINHO_A, CAMINHO_B),
        ),
    ],
    ids=["aguarda", "bloqueado", "divergencia", "um_c7", "varios_c7", "multiplos"],
)
def test_pe_t23_nao_emitivel_nao_acrescenta_nada(
    fotografia: FotografiaFragmento,
) -> None:
    """`PE-7`: zero contribuição. Não é erro e não há substituto."""
    resultado = projetar_fragmentos_para_emissao(
        (A,), (ACAO_T16,), fotografia_r06=fotografia
    )

    assert resultado == (A,)


def test_pe_t23_nao_emitivel_com_cobertura_vazia_devolve_vazio() -> None:
    resultado = projetar_fragmentos_para_emissao(
        (), (ACAO_T16,), fotografia_r06=FotografiaFragmento(status=BLOQUEADO)
    )

    assert resultado == ()


def test_pe_t23_nao_emitivel_nao_escolhe_substituto() -> None:
    """Nem `R03/F1`, nem `R05/F1`, nem texto inventado."""
    resultado = projetar_fragmentos_para_emissao(
        (), (ACAO_T16,), fotografia_r06=FotografiaFragmento(status=AGUARDA)
    )

    assert LACUNA not in resultado
    assert FALLBACK not in resultado
    assert resultado == ()


def test_pe_t23_acao_repetida_com_nao_emitivel_continua_zero() -> None:
    resultado = projetar_fragmentos_para_emissao(
        (),
        (ACAO_T16, ACAO_T16),
        fotografia_r06=FotografiaFragmento(status=BLOQUEADO),
    )

    assert resultado == ()


def test_pe_t23_nao_emitivel_nao_impede_outras_contribuicoes() -> None:
    resultado = projetar_fragmentos_para_emissao(
        (),
        (ACAO_T16, AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO),
        fotografia_r06=FotografiaFragmento(status=BLOQUEADO),
    )

    assert resultado == (LACUNA,)


# ---------------------------------------------------------------------------
# PE-T24 — *fail-closed* da fotografia, só na rota da ação


@pytest.mark.parametrize(
    "fotografia",
    [None, "fotografia", 0, object(), FotografiaFragmento],
    ids=["ausente", "texto", "inteiro", "objeto", "classe"],
)
def test_pe_t24_acao_owner_sem_fotografia_valida_fecha(fotografia: object) -> None:
    with pytest.raises(ProjecaoEmissaoNaoAvaliavel) as erro:
        projetar_fragmentos_para_emissao((), (ACAO_T16,), fotografia_r06=fotografia)

    assert str(erro.value) == "tipo_invalido: fotografia_r06"


def test_pe_t24_subclasse_de_fotografia_nao_e_forma_canonica() -> None:
    class Derivada(FotografiaFragmento):
        pass

    with pytest.raises(ProjecaoEmissaoNaoAvaliavel) as erro:
        projetar_fragmentos_para_emissao(
            (), (ACAO_T16,), fotografia_r06=Derivada(status=APROVADO)
        )

    assert str(erro.value) == "tipo_invalido: fotografia_r06"


def test_pe_t24_fecha_sem_resultado_parcial() -> None:
    resultado = None
    with pytest.raises(ProjecaoEmissaoNaoAvaliavel):
        resultado = projetar_fragmentos_para_emissao(
            (A, B), (ACAO_T16,), fotografia_r06=None
        )

    assert resultado is None


def test_pe_t24_chamada_com_dois_argumentos_continua_valida() -> None:
    """A terceira entrada é *keyword-only* e **condicional**."""
    assert projetar_fragmentos_para_emissao((A,), ()) == (A,)


def test_pe_t24_fotografia_e_keyword_only() -> None:
    with pytest.raises(TypeError):
        projetar_fragmentos_para_emissao((), (ACAO_T16,), EMITIVEL)


# ---------------------------------------------------------------------------
# PE-T25 — a autoridade é consultada no máximo uma vez, e só quando precisa


def _espiar(monkeypatch: pytest.MonkeyPatch) -> list[FotografiaFragmento]:
    """Conta as consultas à autoridade única, sem tocar o código de produção."""
    import casa77_sdr.emission_projection as modulo

    vistas: list[FotografiaFragmento] = []
    real = modulo.avaliar_emissibilidade

    def espiao(fotografia: FotografiaFragmento):
        vistas.append(fotografia)
        return real(fotografia)

    monkeypatch.setattr(modulo, "avaliar_emissibilidade", espiao)
    return vistas


def test_pe_t25_acao_owner_avalia_exatamente_uma_vez(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    vistas = _espiar(monkeypatch)

    projetar_fragmentos_para_emissao((), (ACAO_T16,), fotografia_r06=EMITIVEL)

    assert len(vistas) == 1
    assert vistas[0] is EMITIVEL


def test_pe_t25_acao_repetida_avalia_uma_unica_vez(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    vistas = _espiar(monkeypatch)

    projetar_fragmentos_para_emissao(
        (), (ACAO_T16, ACAO_T16, ACAO_T16), fotografia_r06=EMITIVEL
    )

    assert len(vistas) == 1


def test_pe_t25_repetida_nao_emitivel_avalia_uma_unica_vez(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    vistas = _espiar(monkeypatch)

    projetar_fragmentos_para_emissao(
        (),
        (ACAO_T16, ACAO_T16),
        fotografia_r06=FotografiaFragmento(status=BLOQUEADO),
    )

    assert len(vistas) == 1


def test_pe_t25_cobertura_owner_nao_consulta_a_autoridade(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    vistas = _espiar(monkeypatch)

    projetar_fragmentos_para_emissao((VISITA,), (ACAO_T16,), fotografia_r06=EMITIVEL)

    assert vistas == []


def test_pe_t25_sem_a_acao_de_t16_nao_consulta_a_autoridade(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    vistas = _espiar(monkeypatch)

    projetar_fragmentos_para_emissao(
        (A,),
        (ACAO_T15, AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO),
        fotografia_r06=EMITIVEL,
    )

    assert vistas == []


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
# PE-T8 — tipos exatos das duas entradas base


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
    """A autoridade de emissibilidade entra; `response_assertia` **não**."""
    assert _modulos_importados(MODULO_PE) == {
        "__future__",
        "casa77_sdr.fragment_emissibility",
        "casa77_sdr.state_machine",
    }


def test_pe_t13_nao_importa_a_assertiva_diretamente() -> None:
    """A autoridade é **única**: `avaliar_assertiva` só é alcançada por ela."""
    importados = _modulos_importados(MODULO_PE)

    assert "casa77_sdr.response_assertion" not in importados
    assert "avaliar_assertiva" not in MODULO_PE.read_text(encoding="utf-8")


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


def test_pe_t16_exatamente_tres_acoes_contribuem() -> None:
    """Lacuna, *fallback* de T15 e visita — e mais nenhuma das outras 17."""
    tabela = _tabela()
    com_token = {acao: tokens for acao, tokens in tabela.items() if tokens}

    assert list(com_token) == [
        ACAO_T16,
        AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO,
        ACAO_T15,
    ]
    assert com_token[AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO] == (LACUNA,)
    assert com_token[ACAO_T15] == (FALLBACK,)
    assert com_token[ACAO_T16] == (VISITA,)


@pytest.mark.parametrize(
    "nao_mapeado",
    [
        "R01/F1",
        "R05/F2",
        "R05/F3",
        "R08/F1",
        "R15/F1",
    ],
)
def test_pe_t16_nenhum_outro_fragmento_e_mapeado(nao_mapeado: str) -> None:
    """`R05/F2` e `R05/F3` dependem do runtime; `R01`/`R15` aguardam aprovação."""
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


@pytest.mark.parametrize("token", [LACUNA, FALLBACK], ids=["lacuna", "fallback"])
def test_pe_t17_estaticos_nao_tem_binding_algum(
    indice_real: dict[str, Any], token: str
) -> None:
    """Classe **estática**: zero *binding*, logo zero juízo factual.

    Se um desses dois ganhar `RENDERIZADO`, `ASSERTIVA` ou fato de runtime,
    este teste fica vermelho **de propósito**: a admissibilidade passaria a
    depender de decisão factual, e isso exige nova arbitragem.
    """
    fragmento = _fragmento_do_token(indice_real, token)

    assert fragmento["bindings"] == []
    assert "itera_sobre" not in fragmento


def test_pe_t17_visita_e_condicionada_e_nao_depende_de_runtime(
    indice_real: dict[str, Any],
) -> None:
    """Classe **condicionada**: `R06/F1` tem *bindings*, nenhum de runtime.

    É justamente por ter *bindings* que a rota da ação **não** o acrescenta sem
    veredito. E é por **nenhum** deles ser `RUNTIME_AUTORITATIVO` que nenhuma
    fotografia factual de runtime entra nesta fronteira. Se isso mudar, este
    teste fica vermelho **de propósito**.
    """
    fragmento = _fragmento_do_token(indice_real, VISITA)

    assert fragmento["bindings"] != []
    origens = {binding["origem"] for binding in fragmento["bindings"]}
    assert "RUNTIME_AUTORITATIVO" not in origens


def test_pe_t17_hoje_existem_exatamente_tres_materializados() -> None:
    declarados = [token for tokens in _tabela().values() for token in tokens]

    assert len(declarados) == 3
    assert set(declarados) == {LACUNA, FALLBACK, VISITA}


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

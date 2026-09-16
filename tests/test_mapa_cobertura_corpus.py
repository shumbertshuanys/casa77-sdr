"""Testes de corpus do mapa de cobertura físico — `knowledge/mapa-cobertura.yaml`.

Este é o **único** teste que abre o artefato real de `R2`, e ele o faz
**somente para leitura**: nada é escrito em `knowledge/**`. As provas são
**estruturais** — contagens, referências, status e correspondência de faixa —, e
**nenhum valor comercial é reafirmado como expectativa literal**.

Ele também guarda as **contagens de não regressão** do corpus e dos vocabulários
fechados: o que muda por engano aqui falha aqui.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from casa77_sdr.coverage_decision import (
    MotivoE09,
    decidir_pendencias_e_cobertura,
)
from casa77_sdr.coverage_map import conferir_referencias, validar_mapa_cobertura
from casa77_sdr.coverage_map_load import carregar_mapa_cobertura
from casa77_sdr.identity import Confianca
from casa77_sdr.interpretation import (
    AssuntoComercial,
    DadosExtraidos,
    Interpretacao,
    IntencaoConversacional,
    PerguntaComercial,
)
from casa77_sdr.pricing_applicability import AplicabilidadePacote
from casa77_sdr.qualification import (
    MotivoQualificacao,
    Qualificacao,
    ResultadoQualificacao,
)
from casa77_sdr.response_consistency import ResultadoConsistencia
from casa77_sdr.response_index import validar_indice
from casa77_sdr.response_index_tokens import derivar_tokens_do_indice
from casa77_sdr.response_yaml_path_context import validar_caminho_de_binding
from casa77_sdr.response_yaml_resolve import resolver_caminho
from casa77_sdr.state_machine import AcaoMaquina

RAIZ = Path(__file__).resolve().parents[1]
MAPA = RAIZ / "knowledge" / "mapa-cobertura.yaml"
INDICE = RAIZ / "knowledge" / "indice-respostas-aprovadas.yaml"
BASE = RAIZ / "knowledge" / "casa77.yaml"

QUALIFICACAO = Qualificacao(
    ResultadoQualificacao.QUALIFICADO, MotivoQualificacao.COMPATIVEL
)

RUNTIME_DISPONIVEL = {
    "consulta_calendario_valida": True,
    "data_disponivel": True,
}

# Assuntos que exigem contexto proprio para serem avaliados no ciclo.
PRECO_LOCACAO = AssuntoComercial.PRECO_LOCACAO
PRECO_HORA = AssuntoComercial.PRECO_HORA_ADICIONAL
DISPONIBILIDADE = AssuntoComercial.DISPONIBILIDADE_DE_DATA
ASSUNTOS_DE_PRECO = frozenset({PRECO_LOCACAO, PRECO_HORA})


@pytest.fixture(scope="module")
def mapa() -> dict[str, Any]:
    return carregar_mapa_cobertura(MAPA)


@pytest.fixture(scope="module")
def indice() -> dict[str, Any]:
    return yaml.safe_load(INDICE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def base() -> dict[str, Any]:
    return yaml.safe_load(BASE.read_text(encoding="utf-8"))


def grupos_de(mapa: dict[str, Any], assunto: AssuntoComercial) -> list[Any]:
    for item in mapa["assuntos"]:
        if item["assunto"] == assunto.value:
            return item["grupos"]
    raise AssertionError("assunto ausente do mapa físico")


def tokens_de(grupos: list[Any]) -> list[str]:
    return [
        f"{alt['rxx']}/{alt['fragmento']}"
        for grupo in grupos
        for alt in grupo["alternativas"]
    ]


def status_por_token(indice: dict[str, Any]) -> dict[str, str]:
    return {
        f"{r['id']}/{f['id']}": f["status"]
        for r in indice["respostas"]
        for f in r["fragmentos"]
    }


def consistencia_coerente(indice: dict[str, Any]) -> ResultadoConsistencia:
    """Resultado **coerente** com o índice real: zero divergência, zero `C-7`."""
    registro: list[str] = []
    for resposta in indice["respostas"]:
        for fragmento in resposta["fragmentos"]:
            token = f"{resposta['id']}/{fragmento['id']}"
            registro.extend(
                f"{token}.{binding['nome']}"
                for binding in fragmento["bindings"]
                if binding["origem"] == "RUNTIME_AUTORITATIVO"
            )
    return ResultadoConsistencia(
        divergencias=(),
        referentes_indisponiveis=(),
        tokens_divergentes=(),
        status_por_fragmento=tuple(status_por_token(indice).items()),
        bindings_runtime_nao_avaliados=tuple(registro),
    )


def interpretacao_de(*assuntos: AssuntoComercial) -> Interpretacao:
    return Interpretacao(
        intencoes_detectadas=(),
        dados_extraidos=DadosExtraidos(),
        correcoes=(),
        perguntas_comerciais=tuple(
            PerguntaComercial(
                texto="consulta sintética", confianca=Confianca.ALTA, assunto=a
            )
            for a in assuntos
        ),
        pedido_de_humano=False,
        confianca_pedido_de_humano=None,
        referencias_evento_anterior=(),
        confianca_global=Confianca.ALTA,
        trechos_ambiguos=(),
    )


def decidir(
    mapa: dict[str, Any],
    indice: dict[str, Any],
    *assuntos: AssuntoComercial,
    aplicabilidade: Any = AplicabilidadePacote.FAIXA_INFERIOR,
    fatos_runtime: Any = None,
) -> Any:
    return decidir_pendencias_e_cobertura(
        interpretacao_de(*assuntos),
        QUALIFICACAO,
        mapa,
        indice,
        consistencia_coerente(indice),
        RUNTIME_DISPONIVEL if fatos_runtime is None else fatos_runtime,
        aplicabilidade,
    )


# --------------------------------------------------------------------------
# 1. O artefato real carrega e valida


def test_loader_real_carrega_o_mapa(mapa: dict[str, Any]) -> None:
    assert isinstance(mapa, dict)
    assert list(mapa) == ["assuntos"]


def test_validacao_estrutural_passa(mapa: dict[str, Any]) -> None:
    assert validar_mapa_cobertura(mapa) is None


def test_referencias_passam_contra_o_indice_real(
    mapa: dict[str, Any], indice: dict[str, Any]
) -> None:
    assert conferir_referencias(mapa, indice) is None


# --------------------------------------------------------------------------
# 2. Totalidade e cardinalidades da matriz ratificada


def test_totalidade_54_sobre_54(mapa: dict[str, Any]) -> None:
    declarados = [item["assunto"] for item in mapa["assuntos"]]

    assert len(declarados) == 54
    assert declarados == [membro.value for membro in AssuntoComercial]


def test_exatamente_33_assuntos_com_grupos(mapa: dict[str, Any]) -> None:
    assert sum(1 for item in mapa["assuntos"] if item["grupos"]) == 33


def test_exatamente_21_assuntos_vazios(mapa: dict[str, Any]) -> None:
    assert sum(1 for item in mapa["assuntos"] if not item["grupos"]) == 21


@pytest.mark.parametrize(
    "assunto",
    [
        AssuntoComercial.GERADOR_E_ENERGIA,
        AssuntoComercial.MOBILIARIO,
        AssuntoComercial.ASSUNTO_NAO_CLASSIFICADO,
    ],
)
def test_assuntos_declaradamente_vazios(
    mapa: dict[str, Any], assunto: AssuntoComercial
) -> None:
    assert grupos_de(mapa, assunto) == []


@pytest.mark.parametrize("proibido", ["R03/F1", "R01/F1", "R15/F1"])
def test_tokens_proibidos_nunca_aparecem(
    mapa: dict[str, Any], proibido: str
) -> None:
    todos = [
        token for item in mapa["assuntos"] for token in tokens_de(item["grupos"])
    ]

    assert proibido not in todos


def test_todo_grupo_tem_ao_menos_uma_alternativa(mapa: dict[str, Any]) -> None:
    for item in mapa["assuntos"]:
        for grupo in item["grupos"]:
            assert grupo["alternativas"]


def test_toda_alternativa_aponta_para_fragmento_aprovado(
    mapa: dict[str, Any], indice: dict[str, Any]
) -> None:
    status = status_por_token(indice)
    for item in mapa["assuntos"]:
        for token in tokens_de(item["grupos"]):
            assert status[token] == "APROVADO"


def test_toda_alternativa_pertence_ao_dominio_canonico(
    mapa: dict[str, Any], indice: dict[str, Any]
) -> None:
    dominio = set(derivar_tokens_do_indice(indice))
    for item in mapa["assuntos"]:
        for token in tokens_de(item["grupos"]):
            assert token in dominio


# --------------------------------------------------------------------------
# 3. Preco — faixas distintas, nunca substitutas


@pytest.mark.parametrize("assunto", sorted(ASSUNTOS_DE_PRECO, key=lambda a: a.value))
def test_preco_declara_dois_grupos_singleton(
    mapa: dict[str, Any], assunto: AssuntoComercial
) -> None:
    grupos = grupos_de(mapa, assunto)

    assert len(grupos) == 2
    assert [len(g["alternativas"]) for g in grupos] == [1, 1]
    assert tokens_de(grupos) == ["R09/F1", "R09/F2"]


@pytest.mark.parametrize("assunto", sorted(ASSUNTOS_DE_PRECO, key=lambda a: a.value))
def test_f1_e_f2_nunca_no_mesmo_grupo(
    mapa: dict[str, Any], assunto: AssuntoComercial
) -> None:
    for grupo in grupos_de(mapa, assunto):
        tokens = tokens_de([grupo])

        assert not ("R09/F1" in tokens and "R09/F2" in tokens)


def test_nenhum_grupo_do_mapa_junta_as_duas_faixas(mapa: dict[str, Any]) -> None:
    for item in mapa["assuntos"]:
        for grupo in item["grupos"]:
            tokens = tokens_de([grupo])

            assert not ("R09/F1" in tokens and "R09/F2" in tokens)


def limite_resolvido_de(
    indice: dict[str, Any], base: dict[str, Any], token: str
) -> Any:
    """Resolve o *binding* `limite_convidados` do fragmento, contra a base real.

    O caminho vem do **índice físico**, e a resolução **reutiliza as fronteiras
    canônicas** — a validação contextual de `CY13` e o resolver factual.
    **Nenhum parser, regex, código de pacote ou número é escrito aqui.**
    """
    rxx, fragmento_id = token.split("/")
    for resposta in indice["respostas"]:
        if resposta["id"] != rxx:
            continue
        for fragmento in resposta["fragmentos"]:
            if fragmento["id"] != fragmento_id:
                continue
            for binding in fragmento["bindings"]:
                if binding["nome"] != "limite_convidados":
                    continue
                envelope = validar_caminho_de_binding(
                    binding["caminho_yaml"],
                    fragmento_itera="itera_sobre" in fragmento,
                )
                return resolver_caminho(base, envelope)
    raise AssertionError(f"binding `limite_convidados` ausente em {token}")


def test_f1_e_f2_correspondem_as_duas_faixas_de_pacote(
    base: dict[str, Any]
) -> None:
    """Correspondência **estrutural**: menor limite ↔ F1, maior ↔ F2.

    Nenhum limite é reafirmado como expectativa literal: o que se prova é a
    **ordem** entre as duas faixas e o alinhamento com a capacidade.
    """
    limites = [p["limite_convidados"] for p in base["precos"]["pacotes"]]
    capacidade = base["capacidade"]

    assert len(limites) == 2
    assert min(limites) == capacidade["convidados_sentados"]
    assert max(limites) == capacidade["formato_coquetel"]
    assert min(limites) < max(limites)


def test_r09_f1_resolve_para_a_faixa_de_menor_limite(
    indice: dict[str, Any], base: dict[str, Any]
) -> None:
    """Prova **mecânica**: o caminho declarado em `R09/F1` alcança o menor limite.

    O valor é **resolvido** a partir do `caminho_yaml` do próprio índice, contra
    a base carregada, e comparado ao **mínimo** dos limites dos pacotes. Nenhum
    código de pacote e nenhum número comercial aparece como expectativa.
    """
    limites = [p["limite_convidados"] for p in base["precos"]["pacotes"]]

    assert limite_resolvido_de(indice, base, "R09/F1") == min(limites)


def test_r09_f2_resolve_para_a_faixa_de_maior_limite(
    indice: dict[str, Any], base: dict[str, Any]
) -> None:
    limites = [p["limite_convidados"] for p in base["precos"]["pacotes"]]

    assert limite_resolvido_de(indice, base, "R09/F2") == max(limites)


def test_as_duas_faixas_resolvem_para_valores_distintos(
    indice: dict[str, Any], base: dict[str, Any]
) -> None:
    """Sem valores distintos não existem duas faixas — e o *gate* perde sentido."""
    inferior = limite_resolvido_de(indice, base, "R09/F1")
    superior = limite_resolvido_de(indice, base, "R09/F2")

    assert type(inferior) is int
    assert type(superior) is int
    assert inferior != superior
    assert inferior < superior


def test_limite_resolvido_alinha_o_gate_com_a_capacidade(
    indice: dict[str, Any], base: dict[str, Any]
) -> None:
    """O que `D8-G` chama de faixa é o que o corpus de fato referencia.

    A ponta inferior resolvida coincide com a capacidade sentada e a superior
    com a capacidade máxima — as mesmas fronteiras que §4.4.4 usa para decidir a
    aplicabilidade. É esta igualdade que torna o *gate* verdadeiro sobre o corpus.
    """
    capacidade = base["capacidade"]

    assert (
        limite_resolvido_de(indice, base, "R09/F1")
        == capacidade["convidados_sentados"]
    )
    assert (
        limite_resolvido_de(indice, base, "R09/F2")
        == capacidade["formato_coquetel"]
    )


def test_prova_de_faixa_nao_usa_codigo_de_pacote_hardcoded() -> None:
    """Nenhum código de pacote vigente aparece como literal neste módulo."""
    import ast

    import yaml as _yaml

    codigos = {
        p["codigo"]
        for p in _yaml.safe_load(BASE.read_text(encoding="utf-8"))["precos"][
            "pacotes"
        ]
    }
    literais = {
        no.value
        for no in ast.walk(ast.parse(Path(__file__).read_text(encoding="utf-8")))
        if isinstance(no, ast.Constant) and isinstance(no.value, str)
    }

    assert literais & codigos == set()


# --------------------------------------------------------------------------
# 4. S2-D8 sobre o mapa real — assuntos cobertos


def contexto_para(assunto: AssuntoComercial) -> dict[str, Any]:
    if assunto in ASSUNTOS_DE_PRECO:
        return {"aplicabilidade": AplicabilidadePacote.FAIXA_INFERIOR}
    return {}


COBERTOS = [
    membro
    for membro in AssuntoComercial
    if membro
    not in {
        AssuntoComercial.PRECO_VARIACAO_POR_DIA_DA_SEMANA,
        AssuntoComercial.PRECO_VARIACAO_POR_TEMPORADA,
        AssuntoComercial.PRECO_SUITE_DA_NOIVA,
        AssuntoComercial.REAJUSTE_DE_PRECO,
        AssuntoComercial.PARCERIA_OU_PERMUTA,
        AssuntoComercial.MULTAS_E_PENALIDADES,
        AssuntoComercial.MOBILIARIO,
        AssuntoComercial.CLIMATIZACAO,
        AssuntoComercial.GERADOR_E_ENERGIA,
        AssuntoComercial.FORNECEDOR_RECOMENDADO,
        AssuntoComercial.RESTRICAO_VELAS,
        AssuntoComercial.RESTRICAO_DRONES,
        AssuntoComercial.PRAZO_DE_RETORNO,
        AssuntoComercial.HORARIO_DE_ATENDIMENTO,
        AssuntoComercial.MATERIAL_FOTOS,
        AssuntoComercial.MATERIAL_VIDEOS,
        AssuntoComercial.MATERIAL_PLANTA,
        AssuntoComercial.MATERIAL_PORTFOLIO,
        AssuntoComercial.MATERIAL_APRESENTACAO_COMERCIAL,
        AssuntoComercial.LINK_DE_MAPA,
        AssuntoComercial.ASSUNTO_NAO_CLASSIFICADO,
    }
]

VAZIOS = [membro for membro in AssuntoComercial if membro not in COBERTOS]


def test_particao_cobertos_vazios_bate_com_o_mapa(mapa: dict[str, Any]) -> None:
    assert len(COBERTOS) == 33
    assert len(VAZIOS) == 21
    for membro in COBERTOS:
        assert grupos_de(mapa, membro) != []
    for membro in VAZIOS:
        assert grupos_de(mapa, membro) == []


@pytest.mark.parametrize("assunto", COBERTOS, ids=lambda a: a.value)
def test_assunto_coberto_produz_witness(
    mapa: dict[str, Any], indice: dict[str, Any], assunto: AssuntoComercial
) -> None:
    resultado = decidir(mapa, indice, assunto, **contexto_para(assunto))

    assert resultado.resposta_aprovada_disponivel is True
    assert resultado.fragmentos_autorizados != ()
    assert resultado.causas_e09 == ()
    assert resultado.pendencias_resposta == ()


@pytest.mark.parametrize("assunto", VAZIOS, ids=lambda a: a.value)
def test_assunto_vazio_nao_e_respondivel(
    mapa: dict[str, Any], indice: dict[str, Any], assunto: AssuntoComercial
) -> None:
    resultado = decidir(mapa, indice, assunto)

    assert resultado.resposta_aprovada_disponivel is False
    assert resultado.fragmentos_autorizados == ()
    assert [causa.motivo for causa in resultado.causas_e09] == [
        MotivoE09.SEM_RESPOSTA_APROVADA_EMITIVEL
    ]
    assert len(resultado.pendencias_resposta) == 1


def test_disponibilidade_de_data_usa_o_caminho_de_runtime(
    mapa: dict[str, Any], indice: dict[str, Any]
) -> None:
    for fatos, esperado in (
        ({"consulta_calendario_valida": False}, "R05/F1"),
        (RUNTIME_DISPONIVEL, "R05/F2"),
        (
            {"consulta_calendario_valida": True, "data_disponivel": False},
            "R05/F3",
        ),
    ):
        resultado = decidir(
            mapa, indice, DISPONIBILIDADE, fatos_runtime=fatos
        )

        assert resultado.fragmentos_autorizados == (esperado,)
        assert resultado.causas_e09 == ()


# --------------------------------------------------------------------------
# 5. S2-D8 sobre o mapa real — preco


def test_preco_com_faixa_inferior(
    mapa: dict[str, Any], indice: dict[str, Any]
) -> None:
    resultado = decidir(
        mapa,
        indice,
        PRECO_LOCACAO,
        aplicabilidade=AplicabilidadePacote.FAIXA_INFERIOR,
    )

    assert resultado.fragmentos_autorizados == ("R09/F1",)


def test_preco_com_faixa_superior(
    mapa: dict[str, Any], indice: dict[str, Any]
) -> None:
    resultado = decidir(
        mapa,
        indice,
        PRECO_LOCACAO,
        aplicabilidade=AplicabilidadePacote.FAIXA_SUPERIOR,
    )

    assert resultado.fragmentos_autorizados == ("R09/F2",)


def test_preco_indeterminado_exige_as_duas_faixas(
    mapa: dict[str, Any], indice: dict[str, Any]
) -> None:
    resultado = decidir(
        mapa,
        indice,
        PRECO_LOCACAO,
        aplicabilidade=AplicabilidadePacote.INDETERMINADO,
    )

    assert resultado.fragmentos_autorizados == ("R09/F1", "R09/F2")


def test_preco_sem_pacote_aplicavel_descobre(
    mapa: dict[str, Any], indice: dict[str, Any]
) -> None:
    resultado = decidir(
        mapa,
        indice,
        PRECO_LOCACAO,
        aplicabilidade=AplicabilidadePacote.NENHUM_APLICAVEL,
    )

    assert resultado.resposta_aprovada_disponivel is False
    assert resultado.fragmentos_autorizados == ()
    assert [c.motivo for c in resultado.causas_e09] == [
        MotivoE09.SEM_RESPOSTA_APROVADA_EMITIVEL
    ]


def test_dois_assuntos_de_preco_deduplicam_o_witness(
    mapa: dict[str, Any], indice: dict[str, Any]
) -> None:
    """`SF-D4-9`: o mesmo token escolhido duas vezes entra uma só."""
    resultado = decidir(
        mapa,
        indice,
        PRECO_LOCACAO,
        PRECO_HORA,
        aplicabilidade=AplicabilidadePacote.FAIXA_INFERIOR,
    )

    assert resultado.fragmentos_autorizados == ("R09/F1",)
    assert resultado.resposta_aprovada_disponivel is True


# --------------------------------------------------------------------------
# 6. S2-D8 sobre o mapa real — multiplos assuntos


def test_multiplos_assuntos_preservam_a_ordem_de_primeira_ocorrencia(
    mapa: dict[str, Any], indice: dict[str, Any]
) -> None:
    resultado = decidir(
        mapa,
        indice,
        AssuntoComercial.LOCALIZACAO,
        AssuntoComercial.ESTACIONAMENTO,
    )

    assert resultado.fragmentos_autorizados == ("R13/F1", "R14/F1")


def test_assuntos_distintos_que_compartilham_fragmento_deduplicam(
    mapa: dict[str, Any], indice: dict[str, Any]
) -> None:
    resultado = decidir(
        mapa,
        indice,
        AssuntoComercial.RESTRICAO_FOGOS,
        AssuntoComercial.RESTRICAO_ANIMAIS,
    )

    assert resultado.fragmentos_autorizados == ("R23/F1",)


def test_coberto_mais_descoberto(
    mapa: dict[str, Any], indice: dict[str, Any]
) -> None:
    """D8-T4e: um coberto e outro descoberto → `True` **mais** causa."""
    resultado = decidir(
        mapa,
        indice,
        AssuntoComercial.LOCALIZACAO,
        AssuntoComercial.MOBILIARIO,
    )

    assert resultado.resposta_aprovada_disponivel is True
    assert resultado.fragmentos_autorizados == ("R13/F1",)
    assert [c.assunto for c in resultado.causas_e09] == [
        AssuntoComercial.MOBILIARIO
    ]
    assert len(resultado.pendencias_resposta) == 1


def test_assunto_com_dois_grupos_produz_dois_witnesses(
    mapa: dict[str, Any], indice: dict[str, Any]
) -> None:
    resultado = decidir(mapa, indice, AssuntoComercial.ITENS_INCLUSOS)

    assert resultado.fragmentos_autorizados == ("R12/F1", "R12/F2")


def test_zero_pergunta_sobre_o_mapa_real(
    mapa: dict[str, Any], indice: dict[str, Any]
) -> None:
    resultado = decidir(mapa, indice)

    assert resultado.resposta_aprovada_disponivel is False
    assert resultado.fragmentos_autorizados == ()
    assert resultado.causas_e09 == ()
    assert resultado.pendencia_impeditiva is False


# --------------------------------------------------------------------------
# 7. Nao regressao mecanica do corpus e dos vocabularios


def test_indice_continua_com_30_rxx(indice: dict[str, Any]) -> None:
    assert len(indice["respostas"]) == 30


def test_indice_continua_com_37_fragmentos(indice: dict[str, Any]) -> None:
    assert len(derivar_tokens_do_indice(indice)) == 37


def test_indice_continua_com_118_bindings(indice: dict[str, Any]) -> None:
    total = sum(
        len(fragmento["bindings"])
        for resposta in indice["respostas"]
        for fragmento in resposta["fragmentos"]
    )

    assert total == 118


def test_indice_continua_estruturalmente_valido(indice: dict[str, Any]) -> None:
    assert validar_indice(indice) is None


def test_vocabulario_de_assunto_continua_com_54() -> None:
    assert len(list(AssuntoComercial)) == 54


def test_vocabulario_de_intencao_continua_com_11() -> None:
    assert len(list(IntencaoConversacional)) == 11


def test_vocabulario_de_acao_continua_com_20() -> None:
    assert len(list(AcaoMaquina)) == 20


def test_componentes_e_responsabilidades_continuam() -> None:
    """§4.1 com 14 componentes e §2 com nove responsabilidades."""
    doc = (RAIZ / "docs" / "07-arquitetura-motor-respostas.md").read_text(
        encoding="utf-8"
    )

    assert "§4.1 permanece com **14**" in doc or "**14 componentes**" in doc
    assert "**nove responsabilidades**" in doc


def test_condicoes_de_ciclo_continuam_oito() -> None:
    from casa77_sdr.state_machine import CondicoesCiclo

    assert len(CondicoesCiclo.__dataclass_fields__) == 8


def test_nenhum_teste_escreve_em_knowledge() -> None:
    """Este módulo abre `knowledge/**` apenas para leitura.

    A prova é sobre a **AST**: nenhuma chamada de escrita existe aqui.
    """
    import ast

    arvore = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    escritas = {"write_text", "write_bytes", "mkdir", "unlink", "touch", "rename"}
    chamadas = {
        no.func.attr
        for no in ast.walk(arvore)
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Attribute)
    }
    nomes = {
        no.func.id
        for no in ast.walk(arvore)
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Name)
    }

    assert chamadas & escritas == set()
    assert "open" not in nomes

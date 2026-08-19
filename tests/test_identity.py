"""Testes do ResolvedorIdentidade (3B.7).

Cobre o contrato de `docs/07-arquitetura-motor-respostas.md` §7.1: os vocabulários
fechados, as pré-condições estruturais (C2, H4, H5, P-I1–P-I5), a derivação total
do `Vinculo`, a comparação exclusivamente nominal, as nove classes de candidato, a
precedência de takeover R5-P0 e a cascata determinística D0–D6 — além dos cenários
conceituais R2-K*, R3-K*, R5-K*, K-H* e R-I-K* de §8.2.

Todas as fixtures são artificiais: nenhum dado pessoal, nenhum valor comercial,
nenhuma base carregada — o resolvedor não lê a base e não faz I/O.
"""

from __future__ import annotations

import ast
import dataclasses
import inspect
from pathlib import Path

import pytest

from casa77_sdr import state_machine
from casa77_sdr.identity import (
    CandidatoAtendimento,
    ClasseCandidato,
    Comparacao,
    Confianca,
    CriterioIdentidade,
    DecisaoIdentidade,
    Estado,
    Identidade,
    IntencaoIdentidade,
    ProjecaoInterpretacao,
    ReferenciaEventoAnterior,
    SituacaoTakeover,
    VeredictoIdentificador,
    Vinculo,
    resolver_identidade,
)

MODULO_IDENTIDADE = (
    Path(__file__).resolve().parents[1] / "src" / "casa77_sdr" / "identity.py"
)


# --------------------------------------------------------------------------
# Fixtures artificiais
# --------------------------------------------------------------------------


def candidato(
    id_atendimento: str = "a1",
    estado: Estado = Estado.COLETANDO_DADOS,
    tipo: str | None = None,
    data: str | None = None,
) -> CandidatoAtendimento:
    return CandidatoAtendimento(
        id_atendimento=id_atendimento,
        estado=estado,
        tipo_evento_registrado=tipo,
        data_nomeada_registrada=data,
    )


def projecao(
    intencao: IntencaoIdentidade = IntencaoIdentidade.NAO_DISCRIMINANTE,
    referencia: ReferenciaEventoAnterior = ReferenciaEventoAnterior.SEM_REFERENCIA,
    confianca_referencia: Confianca | None = None,
    tipo: str | None = None,
    confianca_tipo: Confianca | None = None,
    data: str | None = None,
    confianca_data: Confianca | None = None,
) -> ProjecaoInterpretacao:
    return ProjecaoInterpretacao(
        intencao_identidade=intencao,
        referencia_evento_anterior=referencia,
        confianca_referencia=confianca_referencia,
        tipo_evento_extraido=tipo,
        confianca_tipo=confianca_tipo,
        data_nomeada_extraida=data,
        confianca_data=confianca_data,
    )


def resolver(
    candidatos: tuple[CandidatoAtendimento, ...] = (),
    proj: ProjecaoInterpretacao | None = None,
    veredito: VeredictoIdentificador = VeredictoIdentificador.NAO_INFORMADO,
    id_validado: str | None = None,
    havia_estado_esperado: bool = False,
    humanos: tuple[str, ...] = (),
) -> DecisaoIdentidade:
    return resolver_identidade(
        candidatos,
        proj if proj is not None else projecao(),
        veredito,
        id_validado,
        havia_estado_esperado,
        humanos,
    )


# --------------------------------------------------------------------------
# A. Vocabulário fechado
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("enumeracao", "esperado"),
    [
        (IntencaoIdentidade, 3),
        (ReferenciaEventoAnterior, 2),
        (Confianca, 2),
        (Vinculo, 4),
        (SituacaoTakeover, 3),
        (VeredictoIdentificador, 4),
        (Comparacao, 3),
        (ClasseCandidato, 4),
        (CriterioIdentidade, 12),
        (Identidade, 4),
        (Estado, 8),
    ],
)
def test_cardinalidade_dos_vocabularios_fechados(enumeracao, esperado: int) -> None:
    assert len(list(enumeracao)) == esperado


def test_estado_e_identidade_vem_da_maquina_de_estados() -> None:
    """Reuso obrigatório: os dois enums não são redeclarados aqui."""
    assert Estado is state_machine.Estado
    assert Identidade is state_machine.Identidade


def test_membros_exatos_dos_enums_locais() -> None:
    assert [m.name for m in IntencaoIdentidade] == [
        "CONTINUIDADE_DECLARADA",
        "NOVO_EVENTO_DECLARADO",
        "NAO_DISCRIMINANTE",
    ]
    assert [m.name for m in ReferenciaEventoAnterior] == [
        "COM_REFERENCIA",
        "SEM_REFERENCIA",
    ]
    assert [m.name for m in Confianca] == ["ALTA", "BAIXA"]
    assert [m.name for m in Vinculo] == [
        "DECLARA_CONTINUIDADE",
        "DECLARA_NOVO",
        "SEM_DECLARACAO",
        "DECLARACAO_CONTRADITORIA",
    ]
    assert [m.name for m in SituacaoTakeover] == [
        "SEM_TAKEOVER",
        "HUMANO_UNICO",
        "HUMANO_MULTIPLO",
    ]
    assert [m.name for m in VeredictoIdentificador] == [
        "NAO_INFORMADO",
        "ENCONTRADO",
        "NAO_ENCONTRADO",
        "INCOMPATIVEL",
    ]
    assert [m.name for m in Comparacao] == ["IGUAL", "DIFERENTE", "INDETERMINADO"]
    assert [m.name for m in ClasseCandidato] == [
        "CORROBORADO",
        "CONTRADITORIO",
        "NEUTRO",
        "EXCLUIDO",
    ]


def test_os_doze_criterios_exatos() -> None:
    assert [m.name for m in CriterioIdentidade] == [
        "PRIMEIRO_CONTATO_COMPROVADO",
        "SEM_CANDIDATO_ELEGIVEL",
        "NOVO_EVENTO_DECLARADO",
        "ANCORA_COINCIDENTE_UNICA",
        "CONTINUIDADE_DECLARADA_CANDIDATO_UNICO",
        "INERCIA_ATENDIMENTO_ATIVO",
        "TODOS_CANDIDATOS_DIVERGENTES",
        "AMBIGUIDADE_SINAIS_CONTRADITORIOS",
        "AMBIGUIDADE_DIVERGENCIA_EM_ATENDIMENTO_ATIVO",
        "AMBIGUIDADE_MULTIPLOS_COMPATIVEIS",
        "AMBIGUIDADE_MULTIPLOS_ATIVOS",
        "AMBIGUIDADE_SINAIS_INSUFICIENTES",
    ]


def test_nao_existe_criterio_identificador_validado() -> None:
    assert not hasattr(CriterioIdentidade, "IDENTIFICADOR_VALIDADO")
    assert all("IDENTIFICADOR" not in m.name for m in CriterioIdentidade)


def test_valores_dos_enums_seguem_snake_case_do_membro() -> None:
    for enumeracao in (
        IntencaoIdentidade,
        ReferenciaEventoAnterior,
        Confianca,
        Vinculo,
        SituacaoTakeover,
        VeredictoIdentificador,
        Comparacao,
        ClasseCandidato,
        CriterioIdentidade,
    ):
        for membro in enumeracao:
            assert membro.value == membro.name.lower()


# --------------------------------------------------------------------------
# B. Dataclasses
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("classe", "campos"),
    [
        (
            CandidatoAtendimento,
            [
                "id_atendimento",
                "estado",
                "tipo_evento_registrado",
                "data_nomeada_registrada",
            ],
        ),
        (
            ProjecaoInterpretacao,
            [
                "intencao_identidade",
                "referencia_evento_anterior",
                "confianca_referencia",
                "tipo_evento_extraido",
                "confianca_tipo",
                "data_nomeada_extraida",
                "confianca_data",
            ],
        ),
        (
            DecisaoIdentidade,
            [
                "identidade",
                "id_atendimento_alvo",
                "criterio",
                "candidatos_avaliados",
                "classificacao_por_candidato",
                "vinculo_declarado",
                "situacao_takeover",
                "escopo_restrito_por_identificador",
            ],
        ),
    ],
)
def test_campos_exatos_das_dataclasses(classe, campos: list[str]) -> None:
    assert [campo.name for campo in dataclasses.fields(classe)] == campos


def test_decisao_identidade_tem_exatamente_oito_campos() -> None:
    assert len(dataclasses.fields(DecisaoIdentidade)) == 8


@pytest.mark.parametrize(
    "classe", [CandidatoAtendimento, ProjecaoInterpretacao, DecisaoIdentidade]
)
def test_contratos_sao_congelados(classe) -> None:
    assert classe.__dataclass_params__.frozen is True


@pytest.mark.parametrize(
    "classe", [CandidatoAtendimento, ProjecaoInterpretacao, DecisaoIdentidade]
)
def test_contratos_nao_carregam_pii_nem_dado_comercial(classe) -> None:
    proibidos = {
        "nome",
        "telefone",
        "contato",
        "mensagem",
        "texto",
        "preco",
        "valor",
        "capacidade",
        "convidados",
        "formato",
        "email",
    }
    nomes = {campo.name for campo in dataclasses.fields(classe)}
    assert nomes.isdisjoint(proibidos)


def test_decisao_nao_ecoa_o_identificador_validado() -> None:
    nomes = {campo.name for campo in dataclasses.fields(DecisaoIdentidade)}
    assert "id_atendimento_validado" not in nomes


def test_assinatura_publica_tem_exatamente_seis_parametros() -> None:
    parametros = list(inspect.signature(resolver_identidade).parameters)
    assert parametros == [
        "candidatos",
        "projecao",
        "veredito_identificador",
        "id_atendimento_validado",
        "havia_estado_esperado",
        "ids_em_atendimento_humano",
    ]


def test_modulo_nao_importa_io_rede_relogio_nem_base() -> None:
    """Prova estrutural de pureza: o conjunto de imports é fechado."""
    arvore = ast.parse(MODULO_IDENTIDADE.read_text(encoding="utf-8"))
    modulos: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            modulos.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom):
            modulos.add(no.module or "")
    assert modulos == {
        "__future__",
        "unicodedata",
        "dataclasses",
        "enum",
        "casa77_sdr.state_machine",
    }


# --------------------------------------------------------------------------
# C. C2 e confiança binária
# --------------------------------------------------------------------------


def test_referencia_presente_sem_confianca_e_erro_de_contrato() -> None:
    with pytest.raises(ValueError):
        resolver(
            proj=projecao(referencia=ReferenciaEventoAnterior.COM_REFERENCIA),
        )


def test_tipo_presente_sem_confianca_e_erro_de_contrato() -> None:
    with pytest.raises(ValueError):
        resolver(proj=projecao(tipo="casamento"))


def test_data_presente_sem_confianca_e_erro_de_contrato() -> None:
    with pytest.raises(ValueError):
        resolver(proj=projecao(data="outubro"))


def test_confianca_baixa_no_tipo_e_tratada_como_ausencia() -> None:
    decisao = resolver(
        candidatos=(candidato("a1", tipo="casamento"),),
        proj=projecao(tipo="casamento", confianca_tipo=Confianca.BAIXA),
    )
    # Com o extraído lido como ausente, tipo e data ficam INDETERMINADO: NEUTRO.
    assert decisao.classificacao_por_candidato == (("a1", ClasseCandidato.NEUTRO),)


def test_confianca_baixa_na_data_e_tratada_como_ausencia() -> None:
    decisao = resolver(
        candidatos=(candidato("a1", tipo="casamento", data="outubro"),),
        proj=projecao(
            tipo="casamento",
            confianca_tipo=Confianca.ALTA,
            data="dezembro",
            confianca_data=Confianca.BAIXA,
        ),
    )
    # Data divergente com confiança baixa não contradiz: vira INDETERMINADO.
    assert decisao.classificacao_por_candidato == (("a1", ClasseCandidato.CORROBORADO),)


def test_confianca_baixa_na_referencia_e_tratada_como_ausencia() -> None:
    decisao = resolver(
        proj=projecao(
            intencao=IntencaoIdentidade.NAO_DISCRIMINANTE,
            referencia=ReferenciaEventoAnterior.COM_REFERENCIA,
            confianca_referencia=Confianca.BAIXA,
        ),
    )
    assert decisao.vinculo_declarado is Vinculo.SEM_DECLARACAO


def test_confianca_baixa_nao_produz_contradicao_declarada() -> None:
    decisao = resolver(
        proj=projecao(
            intencao=IntencaoIdentidade.NOVO_EVENTO_DECLARADO,
            referencia=ReferenciaEventoAnterior.COM_REFERENCIA,
            confianca_referencia=Confianca.BAIXA,
        ),
    )
    assert decisao.vinculo_declarado is Vinculo.DECLARA_NOVO


# --------------------------------------------------------------------------
# D. Vinculo — tabela total das seis combinações
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("intencao", "referencia", "esperado"),
    [
        (
            IntencaoIdentidade.CONTINUIDADE_DECLARADA,
            ReferenciaEventoAnterior.COM_REFERENCIA,
            Vinculo.DECLARA_CONTINUIDADE,
        ),
        (
            IntencaoIdentidade.CONTINUIDADE_DECLARADA,
            ReferenciaEventoAnterior.SEM_REFERENCIA,
            Vinculo.DECLARA_CONTINUIDADE,
        ),
        (
            IntencaoIdentidade.NOVO_EVENTO_DECLARADO,
            ReferenciaEventoAnterior.SEM_REFERENCIA,
            Vinculo.DECLARA_NOVO,
        ),
        (
            IntencaoIdentidade.NOVO_EVENTO_DECLARADO,
            ReferenciaEventoAnterior.COM_REFERENCIA,
            Vinculo.DECLARACAO_CONTRADITORIA,
        ),
        (
            IntencaoIdentidade.NAO_DISCRIMINANTE,
            ReferenciaEventoAnterior.COM_REFERENCIA,
            Vinculo.DECLARA_CONTINUIDADE,
        ),
        (
            IntencaoIdentidade.NAO_DISCRIMINANTE,
            ReferenciaEventoAnterior.SEM_REFERENCIA,
            Vinculo.SEM_DECLARACAO,
        ),
    ],
)
def test_vinculo_tabela_total(intencao, referencia, esperado) -> None:
    decisao = resolver(
        proj=projecao(
            intencao=intencao,
            referencia=referencia,
            confianca_referencia=(
                Confianca.ALTA
                if referencia is ReferenciaEventoAnterior.COM_REFERENCIA
                else None
            ),
        ),
    )
    assert decisao.vinculo_declarado is esperado


# --------------------------------------------------------------------------
# E. Normalização exclusivamente nominal
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("extraido", "registrado"),
    [
        ("Casamento", "casamento"),
        ("CASAMENTO", "casamento"),
        ("  casamento  ", "casamento"),
        ("casamento   grande", "casamento grande"),
        ("aniversário", "aniversario"),
        ("Aniversário", "ANIVERSARIO"),
    ],
)
def test_igualdade_nominal_por_caixa_espacos_e_acentos(extraido, registrado) -> None:
    decisao = resolver(
        candidatos=(candidato("a1", tipo=registrado),),
        proj=projecao(tipo=extraido, confianca_tipo=Confianca.ALTA),
    )
    assert decisao.classificacao_por_candidato == (("a1", ClasseCandidato.CORROBORADO),)


@pytest.mark.parametrize(
    ("extraido", "registrado"),
    [
        ("casamento", "festa de casamento"),
        ("casamento", "matrimonio"),
        ("aniversario", "aniversario infantil"),
        ("outubro", "10"),
    ],
)
def test_sem_sinonimo_similaridade_ou_score(extraido, registrado) -> None:
    decisao = resolver(
        candidatos=(candidato("a1", tipo=registrado),),
        proj=projecao(tipo=extraido, confianca_tipo=Confianca.ALTA),
    )
    assert decisao.classificacao_por_candidato == (("a1", ClasseCandidato.EXCLUIDO),)


def test_data_e_valor_nominal_sem_calendario() -> None:
    """`outubro` e `2026-10-01` são valores nominais distintos: DIFERENTE."""
    decisao = resolver(
        candidatos=(candidato("a1", tipo="casamento", data="2026-10-01"),),
        proj=projecao(
            tipo="casamento",
            confianca_tipo=Confianca.ALTA,
            data="outubro",
            confianca_data=Confianca.ALTA,
        ),
    )
    assert decisao.classificacao_por_candidato == (
        ("a1", ClasseCandidato.CONTRADITORIO),
    )


# --------------------------------------------------------------------------
# F. Classificação — as nove combinações
# --------------------------------------------------------------------------

_IGUAL = ("casamento", "casamento")
_DIFERENTE = ("casamento", "aniversario")


def _lado(comparacao: Comparacao, registrado_alternativo: str) -> tuple[str | None, str | None]:
    """Devolve (extraído, registrado) que produzem a comparação desejada."""
    if comparacao is Comparacao.IGUAL:
        return ("igual", "igual")
    if comparacao is Comparacao.DIFERENTE:
        return ("um", registrado_alternativo)
    return (None, "qualquer")


@pytest.mark.parametrize(
    ("comparacao_tipo", "comparacao_data", "classe"),
    [
        (Comparacao.IGUAL, Comparacao.IGUAL, ClasseCandidato.CORROBORADO),
        (Comparacao.IGUAL, Comparacao.INDETERMINADO, ClasseCandidato.CORROBORADO),
        (Comparacao.INDETERMINADO, Comparacao.IGUAL, ClasseCandidato.CORROBORADO),
        (Comparacao.IGUAL, Comparacao.DIFERENTE, ClasseCandidato.CONTRADITORIO),
        (Comparacao.INDETERMINADO, Comparacao.DIFERENTE, ClasseCandidato.CONTRADITORIO),
        (Comparacao.INDETERMINADO, Comparacao.INDETERMINADO, ClasseCandidato.NEUTRO),
        (Comparacao.DIFERENTE, Comparacao.IGUAL, ClasseCandidato.EXCLUIDO),
        (Comparacao.DIFERENTE, Comparacao.DIFERENTE, ClasseCandidato.EXCLUIDO),
        (Comparacao.DIFERENTE, Comparacao.INDETERMINADO, ClasseCandidato.EXCLUIDO),
    ],
)
def test_as_nove_combinacoes_de_classificacao(
    comparacao_tipo, comparacao_data, classe
) -> None:
    tipo_extraido, tipo_registrado = _lado(comparacao_tipo, "outro tipo")
    data_extraida, data_registrada = _lado(comparacao_data, "outra data")
    decisao = resolver(
        candidatos=(
            candidato("a1", tipo=tipo_registrado, data=data_registrada),
        ),
        proj=projecao(
            tipo=tipo_extraido,
            confianca_tipo=Confianca.ALTA if tipo_extraido else None,
            data=data_extraida,
            confianca_data=Confianca.ALTA if data_extraida else None,
        ),
    )
    assert decisao.classificacao_por_candidato == (("a1", classe),)


def test_somente_tipo_divergente_exclui() -> None:
    """Data divergente com tipo igual mantém o candidato no conjunto."""
    decisao = resolver(
        candidatos=(candidato("a1", tipo="casamento", data="outubro"),),
        proj=projecao(
            tipo="casamento",
            confianca_tipo=Confianca.ALTA,
            data="dezembro",
            confianca_data=Confianca.ALTA,
        ),
    )
    assert decisao.classificacao_por_candidato == (
        ("a1", ClasseCandidato.CONTRADITORIO),
    )


# --------------------------------------------------------------------------
# G. Cenários R2 — cascata D0–D6
# --------------------------------------------------------------------------


def test_r2_k1_um_ativo_sem_declaracao_sinais_indeterminados() -> None:
    decisao = resolver(candidatos=(candidato("a1", Estado.COLETANDO_DADOS),))
    assert decisao.identidade is Identidade.ATENDIMENTO_ATIVO
    assert decisao.id_atendimento_alvo == "a1"
    assert decisao.criterio is CriterioIdentidade.INERCIA_ATENDIMENTO_ATIVO


def test_r2_k2_dois_ativos_validos_sem_declaracao() -> None:
    decisao = resolver(
        candidatos=(
            candidato("a1", Estado.COLETANDO_DADOS),
            candidato("a2", Estado.RESPONDENDO_DUVIDAS),
        )
    )
    assert decisao.identidade is Identidade.AMBIGUA
    assert decisao.id_atendimento_alvo is None
    assert decisao.criterio is CriterioIdentidade.AMBIGUIDADE_MULTIPLOS_ATIVOS


def test_r2_k3_encerrado_com_tipo_e_data_coincidentes() -> None:
    decisao = resolver(
        candidatos=(
            candidato("a1", Estado.ENCERRADO, tipo="casamento", data="outubro"),
        ),
        proj=projecao(
            tipo="casamento",
            confianca_tipo=Confianca.ALTA,
            data="outubro",
            confianca_data=Confianca.ALTA,
        ),
    )
    assert decisao.identidade is Identidade.MESMA_SOLICITACAO
    assert decisao.id_atendimento_alvo == "a1"
    assert decisao.criterio is CriterioIdentidade.ANCORA_COINCIDENTE_UNICA


def test_r2_k4_dois_corroborados() -> None:
    decisao = resolver(
        candidatos=(
            candidato("a1", Estado.ENCERRADO, tipo="casamento"),
            candidato("a2", Estado.ENCERRADO, tipo="casamento"),
        ),
        proj=projecao(tipo="casamento", confianca_tipo=Confianca.ALTA),
    )
    assert decisao.identidade is Identidade.AMBIGUA
    assert decisao.criterio is CriterioIdentidade.AMBIGUIDADE_MULTIPLOS_COMPATIVEIS


def test_r2_k5_continuidade_declarada_candidato_unico_sem_ancora() -> None:
    decisao = resolver(
        candidatos=(candidato("a1", Estado.COLETANDO_DADOS),),
        proj=projecao(intencao=IntencaoIdentidade.CONTINUIDADE_DECLARADA),
    )
    assert decisao.identidade is Identidade.ATENDIMENTO_ATIVO
    assert decisao.id_atendimento_alvo == "a1"
    assert (
        decisao.criterio
        is CriterioIdentidade.CONTINUIDADE_DECLARADA_CANDIDATO_UNICO
    )


def test_r2_k6_continuidade_declarada_dois_validos_sem_ancora() -> None:
    decisao = resolver(
        candidatos=(
            candidato("a1", Estado.COLETANDO_DADOS),
            candidato("a2", Estado.ENCERRADO),
        ),
        proj=projecao(intencao=IntencaoIdentidade.CONTINUIDADE_DECLARADA),
    )
    assert decisao.identidade is Identidade.AMBIGUA
    assert decisao.criterio is CriterioIdentidade.AMBIGUIDADE_SINAIS_INSUFICIENTES


def test_r2_k7_evento_novo_declarado_sem_candidato_ativo() -> None:
    decisao = resolver(
        candidatos=(candidato("a1", Estado.ENCERRADO),),
        proj=projecao(intencao=IntencaoIdentidade.NOVO_EVENTO_DECLARADO),
    )
    assert decisao.identidade is Identidade.NOVA_SOLICITACAO
    assert decisao.id_atendimento_alvo is None
    assert decisao.criterio is CriterioIdentidade.NOVO_EVENTO_DECLARADO


def test_r2_k8_evento_novo_declarado_com_ativo_inclusive_excluido() -> None:
    decisao = resolver(
        candidatos=(candidato("a1", Estado.COLETANDO_DADOS, tipo="aniversario"),),
        proj=projecao(
            intencao=IntencaoIdentidade.NOVO_EVENTO_DECLARADO,
            tipo="casamento",
            confianca_tipo=Confianca.ALTA,
        ),
    )
    assert decisao.classificacao_por_candidato == (("a1", ClasseCandidato.EXCLUIDO),)
    assert decisao.identidade is Identidade.AMBIGUA
    assert (
        decisao.criterio
        is CriterioIdentidade.AMBIGUIDADE_DIVERGENCIA_EM_ATENDIMENTO_ATIVO
    )


# --------------------------------------------------------------------------
# G. Cenários R3
# --------------------------------------------------------------------------


def test_r3_k1_declaracao_contraditoria_decide_em_d0() -> None:
    decisao = resolver(
        candidatos=(candidato("a1", Estado.COLETANDO_DADOS),),
        proj=projecao(
            intencao=IntencaoIdentidade.NOVO_EVENTO_DECLARADO,
            referencia=ReferenciaEventoAnterior.COM_REFERENCIA,
            confianca_referencia=Confianca.ALTA,
        ),
    )
    assert decisao.vinculo_declarado is Vinculo.DECLARACAO_CONTRADITORIA
    assert decisao.identidade is Identidade.AMBIGUA
    assert decisao.criterio is CriterioIdentidade.AMBIGUIDADE_SINAIS_CONTRADITORIOS
    assert decisao.escopo_restrito_por_identificador is False


def test_r3_k2_escopo_vazio_sem_estado_esperado() -> None:
    """Fixture R-I: NAO_INFORMADO e `id_atendimento_validado` None (P-I1)."""
    decisao = resolver(
        veredito=VeredictoIdentificador.NAO_INFORMADO,
        id_validado=None,
        havia_estado_esperado=False,
    )
    assert decisao.identidade is None
    assert decisao.id_atendimento_alvo is None
    assert decisao.criterio is CriterioIdentidade.PRIMEIRO_CONTATO_COMPROVADO


def test_r3_k3_escopo_vazio_com_estado_esperado() -> None:
    """Fixture R-I: NAO_INFORMADO e `id_atendimento_validado` None (P-I1)."""
    decisao = resolver(
        veredito=VeredictoIdentificador.NAO_INFORMADO,
        id_validado=None,
        havia_estado_esperado=True,
    )
    assert decisao.identidade is None
    assert decisao.id_atendimento_alvo is None
    assert decisao.criterio is CriterioIdentidade.SEM_CANDIDATO_ELEGIVEL


def test_r3_k4_identificado_nao_corroborado_perde_para_corroborado_alheio() -> None:
    """Fixture R-I válida: ID presente, único e `havia_estado_esperado` True."""
    decisao = resolver(
        candidatos=(
            candidato("a1", Estado.COLETANDO_DADOS, tipo="aniversario"),
            candidato("a2", Estado.ENCERRADO, tipo="casamento"),
        ),
        proj=projecao(tipo="casamento", confianca_tipo=Confianca.ALTA),
        veredito=VeredictoIdentificador.ENCONTRADO,
        id_validado="a1",
        havia_estado_esperado=True,
    )
    assert decisao.identidade is Identidade.AMBIGUA
    assert decisao.criterio is CriterioIdentidade.AMBIGUIDADE_SINAIS_CONTRADITORIOS
    assert decisao.escopo_restrito_por_identificador is False
    assert decisao.candidatos_avaliados == ("a1", "a2")


def test_r3_k5_identificador_sem_conflito_restringe_o_escopo() -> None:
    """Fixture R-I válida: ID presente, único e `havia_estado_esperado` True."""
    decisao = resolver(
        candidatos=(
            candidato("a1", Estado.ENCERRADO, tipo="casamento"),
            candidato("a2", Estado.ENCERRADO, tipo="aniversario"),
        ),
        proj=projecao(tipo="casamento", confianca_tipo=Confianca.ALTA),
        veredito=VeredictoIdentificador.ENCONTRADO,
        id_validado="a1",
        havia_estado_esperado=True,
    )
    assert decisao.escopo_restrito_por_identificador is True
    assert decisao.candidatos_avaliados == ("a1",)
    assert decisao.identidade is Identidade.MESMA_SOLICITACAO
    assert decisao.criterio is CriterioIdentidade.ANCORA_COINCIDENTE_UNICA


def test_r3_k6_todos_divergentes_sem_declaracao_nenhum_ativo() -> None:
    decisao = resolver(
        candidatos=(
            candidato("a1", Estado.ENCERRADO, tipo="aniversario"),
            candidato("a2", Estado.ENCERRADO, tipo="formatura"),
        ),
        proj=projecao(tipo="casamento", confianca_tipo=Confianca.ALTA),
    )
    assert decisao.identidade is Identidade.NOVA_SOLICITACAO
    assert decisao.id_atendimento_alvo is None
    assert decisao.criterio is CriterioIdentidade.TODOS_CANDIDATOS_DIVERGENTES


@pytest.mark.parametrize(
    "veredito",
    [VeredictoIdentificador.NAO_ENCONTRADO, VeredictoIdentificador.INCOMPATIVEL],
)
def test_r3_k7_veredito_defensivo_e_erro_de_contrato(veredito) -> None:
    with pytest.raises(ValueError):
        resolver(candidatos=(candidato("a1"),), veredito=veredito, id_validado="a1")


def test_r3_k7_valor_sem_confianca_e_erro_de_contrato() -> None:
    with pytest.raises(ValueError):
        resolver(
            candidatos=(candidato("a1"),),
            proj=projecao(tipo="casamento"),
        )


# --------------------------------------------------------------------------
# H. Cenários R5 — precedência de takeover
# --------------------------------------------------------------------------


def test_r5_k1_nao_discriminante_com_referencia_preserva_a_semantica_r3() -> None:
    decisao = resolver(
        proj=projecao(
            intencao=IntencaoIdentidade.NAO_DISCRIMINANTE,
            referencia=ReferenciaEventoAnterior.COM_REFERENCIA,
            confianca_referencia=Confianca.ALTA,
        )
    )
    assert decisao.vinculo_declarado is Vinculo.DECLARA_CONTINUIDADE


def test_r5_k2_novo_com_referencia_produz_contradicao_sem_criterio_novo() -> None:
    decisao = resolver(
        candidatos=(candidato("a1"),),
        proj=projecao(
            intencao=IntencaoIdentidade.NOVO_EVENTO_DECLARADO,
            referencia=ReferenciaEventoAnterior.COM_REFERENCIA,
            confianca_referencia=Confianca.ALTA,
        ),
    )
    assert decisao.vinculo_declarado is Vinculo.DECLARACAO_CONTRADITORIA
    assert decisao.criterio is CriterioIdentidade.AMBIGUIDADE_SINAIS_CONTRADITORIOS
    assert len(list(CriterioIdentidade)) == 12


def test_r5_k3_takeover_prevalece_sobre_corroborado_alheio() -> None:
    decisao = resolver(
        candidatos=(candidato("a1", Estado.ENCERRADO, tipo="casamento"),),
        proj=projecao(tipo="casamento", confianca_tipo=Confianca.ALTA),
        humanos=("h1",),
    )
    assert decisao.situacao_takeover is SituacaoTakeover.HUMANO_UNICO
    assert decisao.identidade is None
    assert decisao.id_atendimento_alvo == "h1"
    assert decisao.criterio is None
    assert decisao.candidatos_avaliados == ()
    assert decisao.classificacao_por_candidato == ()


def test_r5_k4_takeover_prevalece_sobre_identificador_apontando_outro() -> None:
    decisao = resolver(
        candidatos=(candidato("a1", Estado.COLETANDO_DADOS),),
        veredito=VeredictoIdentificador.ENCONTRADO,
        id_validado="a1",
        havia_estado_esperado=True,
        humanos=("h1",),
    )
    assert decisao.situacao_takeover is SituacaoTakeover.HUMANO_UNICO
    assert decisao.id_atendimento_alvo == "h1"
    assert decisao.identidade is None
    assert decisao.criterio is None
    assert decisao.escopo_restrito_por_identificador is False


def test_r5_k5_humano_multiplo_nao_escolhe_alvo() -> None:
    decisao = resolver(
        candidatos=(candidato("a1", Estado.COLETANDO_DADOS),),
        humanos=("h1", "h2"),
    )
    assert decisao.situacao_takeover is SituacaoTakeover.HUMANO_MULTIPLO
    assert decisao.identidade is None
    assert decisao.id_atendimento_alvo is None
    assert decisao.criterio is None
    assert decisao.candidatos_avaliados == ()


def test_r5_k6_sem_takeover_executa_a_cascata() -> None:
    decisao = resolver(candidatos=(candidato("a1", Estado.COLETANDO_DADOS),))
    assert decisao.situacao_takeover is SituacaoTakeover.SEM_TAKEOVER
    assert decisao.criterio is CriterioIdentidade.INERCIA_ATENDIMENTO_ATIVO


def test_r5_k7_takeover_nao_exige_membro_novo_em_identidade() -> None:
    for humanos in ((), ("h1",), ("h1", "h2")):
        decisao = resolver(
            candidatos=(candidato("a1", Estado.COLETANDO_DADOS),), humanos=humanos
        )
        assert decisao.identidade is None or decisao.identidade in list(Identidade)
    assert len(list(Identidade)) == 4


# --------------------------------------------------------------------------
# I. Cenários do conjunto H
# --------------------------------------------------------------------------


def test_k_h1_h_vazio_executa_a_cascata() -> None:
    decisao = resolver(candidatos=(candidato("a1", Estado.COLETANDO_DADOS),))
    assert decisao.situacao_takeover is SituacaoTakeover.SEM_TAKEOVER
    assert decisao.identidade is Identidade.ATENDIMENTO_ATIVO


def test_k_h2_h_com_um_id() -> None:
    decisao = resolver(humanos=("h1",))
    assert decisao.situacao_takeover is SituacaoTakeover.HUMANO_UNICO
    assert decisao.id_atendimento_alvo == "h1"
    assert decisao.identidade is None
    assert decisao.criterio is None


def test_k_h3_h_com_dois_ids_distintos() -> None:
    decisao = resolver(humanos=("h1", "h2"))
    assert decisao.situacao_takeover is SituacaoTakeover.HUMANO_MULTIPLO
    assert decisao.id_atendimento_alvo is None
    assert decisao.criterio is None


def test_k_h4_elegiveis_vazio_com_h_unico_nao_e_sem_candidato_elegivel() -> None:
    decisao = resolver(candidatos=(), havia_estado_esperado=True, humanos=("h1",))
    assert decisao.situacao_takeover is SituacaoTakeover.HUMANO_UNICO
    assert decisao.criterio is None
    assert decisao.criterio is not CriterioIdentidade.SEM_CANDIDATO_ELEGIVEL


def test_k_h5_corroborado_nao_desvia_o_alvo_do_takeover() -> None:
    decisao = resolver(
        candidatos=(candidato("a1", Estado.ENCERRADO, tipo="casamento"),),
        proj=projecao(tipo="casamento", confianca_tipo=Confianca.ALTA),
        humanos=("h1",),
    )
    assert decisao.id_atendimento_alvo == "h1"


def test_k_h6_id_duplicado_em_h_e_erro_de_contrato() -> None:
    with pytest.raises(ValueError):
        resolver(humanos=("h1", "h1"))


def test_k_h7_candidato_humano_ausente_de_h_e_erro_de_contrato() -> None:
    with pytest.raises(ValueError):
        resolver(
            candidatos=(candidato("a1", Estado.ATENDIMENTO_HUMANO),),
            humanos=(),
        )


def test_k_h8_id_de_h_fora_dos_elegiveis_e_valido() -> None:
    decisao = resolver(
        candidatos=(candidato("a1", Estado.COLETANDO_DADOS),), humanos=("h1",)
    )
    assert decisao.situacao_takeover is SituacaoTakeover.HUMANO_UNICO
    assert decisao.id_atendimento_alvo == "h1"


def test_h5_e_satisfeito_quando_o_candidato_humano_esta_em_h() -> None:
    decisao = resolver(
        candidatos=(candidato("h1", Estado.ATENDIMENTO_HUMANO),), humanos=("h1",)
    )
    assert decisao.situacao_takeover is SituacaoTakeover.HUMANO_UNICO
    assert decisao.id_atendimento_alvo == "h1"


# --------------------------------------------------------------------------
# J. Cenários R-I — projeção do identificador validado
# --------------------------------------------------------------------------


def test_ri_k1_nao_informado_com_id_none_segue_fluxo_normal() -> None:
    decisao = resolver(
        candidatos=(candidato("a1", Estado.COLETANDO_DADOS),),
        veredito=VeredictoIdentificador.NAO_INFORMADO,
        id_validado=None,
    )
    assert decisao.escopo_restrito_por_identificador is False
    assert decisao.candidatos_avaliados == ("a1",)
    assert decisao.criterio is CriterioIdentidade.INERCIA_ATENDIMENTO_ATIVO


def test_ri_k2_nao_informado_com_id_presente_e_erro_de_contrato() -> None:
    with pytest.raises(ValueError):
        resolver(
            candidatos=(candidato("a1"),),
            veredito=VeredictoIdentificador.NAO_INFORMADO,
            id_validado="a1",
        )


@pytest.mark.parametrize("id_validado", [None, ""])
def test_ri_k3_encontrado_sem_id_e_erro_de_contrato(id_validado) -> None:
    with pytest.raises(ValueError):
        resolver(
            candidatos=(candidato("a1"),),
            veredito=VeredictoIdentificador.ENCONTRADO,
            id_validado=id_validado,
            havia_estado_esperado=True,
        )


def test_ri_k4_encontrado_sem_estado_esperado_e_erro_de_contrato() -> None:
    with pytest.raises(ValueError):
        resolver(
            candidatos=(candidato("a1"),),
            veredito=VeredictoIdentificador.ENCONTRADO,
            id_validado="a1",
            havia_estado_esperado=False,
        )


def test_ri_k5_encontrado_com_id_ausente_entre_outros_candidatos() -> None:
    with pytest.raises(ValueError):
        resolver(
            candidatos=(candidato("a1"), candidato("a2")),
            veredito=VeredictoIdentificador.ENCONTRADO,
            id_validado="a9",
            havia_estado_esperado=True,
        )


def test_ri_k6_encontrado_com_candidatos_vazio_e_erro_nao_sem_candidato_elegivel() -> None:
    with pytest.raises(ValueError):
        resolver(
            candidatos=(),
            veredito=VeredictoIdentificador.ENCONTRADO,
            id_validado="a1",
            havia_estado_esperado=True,
        )


def test_ri_k7_identificado_duplicado_e_erro_de_contrato() -> None:
    with pytest.raises(ValueError):
        resolver(
            candidatos=(candidato("a1"), candidato("a1")),
            veredito=VeredictoIdentificador.ENCONTRADO,
            id_validado="a1",
            havia_estado_esperado=True,
        )


def test_ri_k8_precondicao_prevalece_sobre_takeover() -> None:
    """R5-P0 não é alcançado sobre entrada malformada."""
    with pytest.raises(ValueError):
        resolver(
            candidatos=(candidato("a1"),),
            veredito=VeredictoIdentificador.ENCONTRADO,
            id_validado="a9",
            havia_estado_esperado=True,
            humanos=("h1",),
        )


def test_ri_k9_precondicao_prevalece_sobre_d0() -> None:
    """D0 não é alcançado sobre entrada malformada."""
    with pytest.raises(ValueError):
        resolver(
            candidatos=(candidato("a1"),),
            proj=projecao(
                intencao=IntencaoIdentidade.NOVO_EVENTO_DECLARADO,
                referencia=ReferenciaEventoAnterior.COM_REFERENCIA,
                confianca_referencia=Confianca.ALTA,
            ),
            veredito=VeredictoIdentificador.ENCONTRADO,
            id_validado="a9",
            havia_estado_esperado=True,
        )


def test_ri_k10_encontrado_valido_com_takeover_em_outro_atendimento() -> None:
    decisao = resolver(
        candidatos=(candidato("a1", Estado.COLETANDO_DADOS),),
        veredito=VeredictoIdentificador.ENCONTRADO,
        id_validado="a1",
        havia_estado_esperado=True,
        humanos=("h1",),
    )
    assert decisao.situacao_takeover is SituacaoTakeover.HUMANO_UNICO
    assert decisao.id_atendimento_alvo == "h1"
    assert decisao.identidade is None
    assert decisao.criterio is None


def test_ri_k11_encontrado_valido_sem_conflito_restringe() -> None:
    decisao = resolver(
        candidatos=(
            candidato("a1", Estado.COLETANDO_DADOS),
            candidato("a2", Estado.COLETANDO_DADOS),
        ),
        veredito=VeredictoIdentificador.ENCONTRADO,
        id_validado="a1",
        havia_estado_esperado=True,
    )
    assert decisao.escopo_restrito_por_identificador is True
    assert decisao.candidatos_avaliados == ("a1",)
    assert decisao.classificacao_por_candidato == (("a1", ClasseCandidato.NEUTRO),)
    assert decisao.identidade is Identidade.ATENDIMENTO_ATIVO
    assert decisao.criterio is CriterioIdentidade.INERCIA_ATENDIMENTO_ATIVO


def test_ri_k12_corroborado_alheio_vence_o_identificado_nao_corroborado() -> None:
    decisao = resolver(
        candidatos=(
            candidato("a1", Estado.COLETANDO_DADOS, tipo="aniversario"),
            candidato("a2", Estado.ENCERRADO, tipo="casamento"),
        ),
        proj=projecao(tipo="casamento", confianca_tipo=Confianca.ALTA),
        veredito=VeredictoIdentificador.ENCONTRADO,
        id_validado="a1",
        havia_estado_esperado=True,
    )
    assert decisao.identidade is Identidade.AMBIGUA
    assert decisao.criterio is CriterioIdentidade.AMBIGUIDADE_SINAIS_CONTRADITORIOS
    assert decisao.escopo_restrito_por_identificador is False


@pytest.mark.parametrize(
    "veredito",
    [VeredictoIdentificador.NAO_ENCONTRADO, VeredictoIdentificador.INCOMPATIVEL],
)
@pytest.mark.parametrize("id_validado", [None, "", "a1"])
def test_ri_k13_vereditos_defensivos_sao_erro_independentemente_do_id(
    veredito, id_validado
) -> None:
    with pytest.raises(ValueError):
        resolver(
            candidatos=(candidato("a1"),),
            veredito=veredito,
            id_validado=id_validado,
            havia_estado_esperado=True,
        )


def test_ri_k14_escopo_vazio_com_historico_conhecido() -> None:
    decisao = resolver(
        veredito=VeredictoIdentificador.NAO_INFORMADO,
        id_validado=None,
        havia_estado_esperado=True,
    )
    assert decisao.criterio is CriterioIdentidade.SEM_CANDIDATO_ELEGIVEL
    assert decisao.identidade is None


def test_ri_k15_escopo_vazio_sem_historico_conhecido() -> None:
    decisao = resolver(
        veredito=VeredictoIdentificador.NAO_INFORMADO,
        id_validado=None,
        havia_estado_esperado=False,
    )
    assert decisao.criterio is CriterioIdentidade.PRIMEIRO_CONTATO_COMPROVADO
    assert decisao.identidade is None


def test_d2_nao_restringe_quando_o_veredito_e_nao_informado() -> None:
    decisao = resolver(
        candidatos=(
            candidato("a1", Estado.COLETANDO_DADOS),
            candidato("a2", Estado.COLETANDO_DADOS),
        ),
    )
    assert decisao.escopo_restrito_por_identificador is False
    assert decisao.candidatos_avaliados == ("a1", "a2")


# --------------------------------------------------------------------------
# K. Duplicatas gerais — questão residual não decidida
# --------------------------------------------------------------------------


def test_duplicata_entre_candidatos_nao_identificados_nao_falha() -> None:
    """P-I5 exige unicidade só do ID identificado; não há regra global."""
    decisao = resolver(
        candidatos=(
            candidato("a1", Estado.COLETANDO_DADOS),
            candidato("a1", Estado.COLETANDO_DADOS),
        ),
        veredito=VeredictoIdentificador.NAO_INFORMADO,
    )
    assert decisao.criterio is CriterioIdentidade.AMBIGUIDADE_MULTIPLOS_ATIVOS
    assert decisao.candidatos_avaliados == ("a1", "a1")
    assert decisao.classificacao_por_candidato == (
        ("a1", ClasseCandidato.NEUTRO),
        ("a1", ClasseCandidato.NEUTRO),
    )


def test_duplicata_entre_nao_identificados_com_identificado_distinto_nao_falha() -> None:
    decisao = resolver(
        candidatos=(
            candidato("a1", Estado.COLETANDO_DADOS),
            candidato("a2", Estado.COLETANDO_DADOS),
            candidato("a2", Estado.COLETANDO_DADOS),
        ),
        veredito=VeredictoIdentificador.ENCONTRADO,
        id_validado="a1",
        havia_estado_esperado=True,
    )
    assert decisao.escopo_restrito_por_identificador is True
    assert decisao.candidatos_avaliados == ("a1",)


# --------------------------------------------------------------------------
# L. Determinismo
# --------------------------------------------------------------------------


def test_mesma_entrada_produz_decisao_identica() -> None:
    argumentos = dict(
        candidatos=(
            candidato("a1", Estado.COLETANDO_DADOS, tipo="casamento", data="outubro"),
            candidato("a2", Estado.ENCERRADO, tipo="aniversario"),
        ),
        proj=projecao(
            intencao=IntencaoIdentidade.CONTINUIDADE_DECLARADA,
            referencia=ReferenciaEventoAnterior.COM_REFERENCIA,
            confianca_referencia=Confianca.ALTA,
            tipo="casamento",
            confianca_tipo=Confianca.ALTA,
            data="outubro",
            confianca_data=Confianca.ALTA,
        ),
        veredito=VeredictoIdentificador.ENCONTRADO,
        id_validado="a1",
        havia_estado_esperado=True,
    )
    primeira = resolver(**argumentos)
    segunda = resolver(**argumentos)
    assert primeira == segunda


def test_os_argumentos_nao_sao_mutados() -> None:
    candidatos = (
        candidato("a1", Estado.COLETANDO_DADOS),
        candidato("a2", Estado.ENCERRADO),
    )
    humanos = ("h1",)
    copia_candidatos = tuple(candidatos)
    resolver(candidatos=candidatos, humanos=humanos)
    assert candidatos == copia_candidatos
    assert humanos == ("h1",)


# --------------------------------------------------------------------------
# M. Invariantes de saída
# --------------------------------------------------------------------------

_CASOS_SEM_TAKEOVER = [
    ((), VeredictoIdentificador.NAO_INFORMADO, None, False),
    ((), VeredictoIdentificador.NAO_INFORMADO, None, True),
    ((candidato("a1", Estado.COLETANDO_DADOS),), VeredictoIdentificador.NAO_INFORMADO, None, False),
    ((candidato("a1", Estado.ENCERRADO),), VeredictoIdentificador.NAO_INFORMADO, None, True),
    (
        (candidato("a1", Estado.COLETANDO_DADOS), candidato("a2", Estado.COLETANDO_DADOS)),
        VeredictoIdentificador.NAO_INFORMADO,
        None,
        True,
    ),
    (
        (candidato("a1", Estado.COLETANDO_DADOS),),
        VeredictoIdentificador.ENCONTRADO,
        "a1",
        True,
    ),
]


@pytest.mark.parametrize(
    ("candidatos", "veredito", "id_validado", "havia"), _CASOS_SEM_TAKEOVER
)
def test_criterio_e_obrigatorio_sem_takeover(
    candidatos, veredito, id_validado, havia
) -> None:
    decisao = resolver(
        candidatos=candidatos,
        veredito=veredito,
        id_validado=id_validado,
        havia_estado_esperado=havia,
    )
    assert decisao.situacao_takeover is SituacaoTakeover.SEM_TAKEOVER
    assert decisao.criterio is not None
    assert decisao.criterio in list(CriterioIdentidade)


@pytest.mark.parametrize(
    ("candidatos", "veredito", "id_validado", "havia"), _CASOS_SEM_TAKEOVER
)
def test_invariantes_de_identidade_e_alvo(
    candidatos, veredito, id_validado, havia
) -> None:
    decisao = resolver(
        candidatos=candidatos,
        veredito=veredito,
        id_validado=id_validado,
        havia_estado_esperado=havia,
    )
    sem_alvo = {
        CriterioIdentidade.PRIMEIRO_CONTATO_COMPROVADO,
        CriterioIdentidade.SEM_CANDIDATO_ELEGIVEL,
    }
    if decisao.criterio in sem_alvo:
        assert decisao.identidade is None
        assert decisao.id_atendimento_alvo is None
    elif decisao.identidade in (Identidade.NOVA_SOLICITACAO, Identidade.AMBIGUA):
        assert decisao.id_atendimento_alvo is None
    else:
        assert decisao.identidade in (
            Identidade.ATENDIMENTO_ATIVO,
            Identidade.MESMA_SOLICITACAO,
        )
        assert decisao.id_atendimento_alvo is not None


@pytest.mark.parametrize("humanos", [("h1",), ("h1", "h2")])
def test_criterio_e_none_somente_sob_takeover(humanos) -> None:
    decisao = resolver(
        candidatos=(candidato("a1", Estado.COLETANDO_DADOS),), humanos=humanos
    )
    assert decisao.criterio is None
    assert decisao.situacao_takeover is not SituacaoTakeover.SEM_TAKEOVER
    assert decisao.identidade is None


def test_saida_nao_carrega_texto_livre_nem_dado_pessoal() -> None:
    decisao = resolver(
        candidatos=(candidato("a1", Estado.COLETANDO_DADOS, tipo="casamento"),),
        proj=projecao(tipo="casamento", confianca_tipo=Confianca.ALTA),
    )
    textuais = [
        decisao.id_atendimento_alvo,
        *decisao.candidatos_avaliados,
        *(identificador for identificador, _ in decisao.classificacao_por_candidato),
    ]
    # Somente identificadores opacos de atendimento saem na decisão.
    assert all(valor in {"a1"} for valor in textuais if valor is not None)
    assert "casamento" not in str(decisao)


# --------------------------------------------------------------------------
# Contrato de tipos
# --------------------------------------------------------------------------


def test_candidatos_precisam_ser_tupla() -> None:
    with pytest.raises(TypeError):
        resolver_identidade(
            [candidato("a1")],  # type: ignore[arg-type]
            projecao(),
            VeredictoIdentificador.NAO_INFORMADO,
            None,
            False,
            (),
        )


def test_item_de_candidato_invalido_e_erro_de_tipo() -> None:
    with pytest.raises(TypeError):
        resolver_identidade(
            ("a1",),  # type: ignore[arg-type]
            projecao(),
            VeredictoIdentificador.NAO_INFORMADO,
            None,
            False,
            (),
        )


def test_estado_do_candidato_precisa_ser_enum() -> None:
    with pytest.raises(TypeError):
        resolver(
            candidatos=(
                CandidatoAtendimento(
                    id_atendimento="a1",
                    estado="coletando_dados",  # type: ignore[arg-type]
                    tipo_evento_registrado=None,
                    data_nomeada_registrada=None,
                ),
            )
        )


def test_projecao_invalida_e_erro_de_tipo() -> None:
    with pytest.raises(TypeError):
        resolver_identidade(
            (),
            object(),  # type: ignore[arg-type]
            VeredictoIdentificador.NAO_INFORMADO,
            None,
            False,
            (),
        )


def test_veredito_invalido_e_erro_de_tipo() -> None:
    with pytest.raises(TypeError):
        resolver(veredito="encontrado")  # type: ignore[arg-type]


def test_id_validado_precisa_ser_texto_ou_none() -> None:
    with pytest.raises(TypeError):
        resolver(veredito=VeredictoIdentificador.NAO_INFORMADO, id_validado=7)  # type: ignore[arg-type]


def test_havia_estado_esperado_nao_aceita_inteiro() -> None:
    with pytest.raises(TypeError):
        resolver(havia_estado_esperado=1)  # type: ignore[arg-type]


def test_ids_em_atendimento_humano_precisa_ser_tupla_de_texto() -> None:
    with pytest.raises(TypeError):
        resolver(humanos=["h1"])  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        resolver(humanos=(1,))  # type: ignore[arg-type]


def test_confianca_invalida_e_erro_de_tipo() -> None:
    with pytest.raises(TypeError):
        resolver(
            proj=ProjecaoInterpretacao(
                intencao_identidade=IntencaoIdentidade.NAO_DISCRIMINANTE,
                referencia_evento_anterior=ReferenciaEventoAnterior.SEM_REFERENCIA,
                confianca_referencia=None,
                tipo_evento_extraido="casamento",
                confianca_tipo="alta",  # type: ignore[arg-type]
                data_nomeada_extraida=None,
                confianca_data=None,
            )
        )


def test_erro_de_contrato_nunca_devolve_ambigua() -> None:
    """Erro de contrato não é caso de negócio: nenhuma identidade é devolvida."""
    for chamada in (
        lambda: resolver(humanos=("h1", "h1")),
        lambda: resolver(
            candidatos=(candidato("a1", Estado.ATENDIMENTO_HUMANO),), humanos=()
        ),
        lambda: resolver(
            veredito=VeredictoIdentificador.NAO_INFORMADO, id_validado="a1"
        ),
        lambda: resolver(proj=projecao(tipo="casamento")),
    ):
        with pytest.raises((TypeError, ValueError)):
            chamada()

"""Testes do qualificador determinístico (3B.5).

Bases e dados são **inteiramente artificiais**: os limites de capacidade das
fixtures são valores fictícios, sem relação com a operação real, e o YAML real
não é aberto nem lido aqui. Nenhum nome, contato ou mensagem real aparece.

Os testes provam que esta camada apenas classifica: nada aqui recalcula regra
comercial, detecta pendência na base, escolhe pacote, decide handoff ou
transiciona estado.
"""

from __future__ import annotations

import ast
import copy
from pathlib import Path
from typing import Any

import pytest

from casa77_sdr.qualification import (
    DadosQualificacao,
    FormatoEvento,
    MotivoQualificacao,
    Qualificacao,
    ResultadoQualificacao,
    qualificar,
)
from casa77_sdr.rules import DadosAtendimento, MotivoViolacao, Violacao

RAIZ = Path(__file__).resolve().parents[1]
MODULO_QUALIFICACAO = RAIZ / "src" / "casa77_sdr" / "qualification.py"

SENTADOS = 7
COQUETEL = 9


def base_ficticia(sentados: int = SENTADOS, coquetel: int = COQUETEL) -> dict[str, Any]:
    """Base mínima com limites artificiais, não comerciais."""
    return {"capacidade": {"convidados_sentados": sentados, "formato_coquetel": coquetel}}


def dados_ficticios(
    nome: Any = "nome-artificial",
    contato: Any = "contato-artificial",
    tipo_evento: Any = "tipo-artificial",
    data_nomeada: Any = "data-artificial",
    convidados: Any = 3,
    formato: Any = None,
) -> DadosQualificacao:
    """Dados completos e compatíveis por padrão; cada campo é sobrescrevível."""
    return DadosQualificacao(
        atendimento=DadosAtendimento(
            tipo_evento=tipo_evento,
            data_nomeada=data_nomeada,
            convidados=convidados,
        ),
        nome=nome,
        contato=contato,
        formato=formato,
    )


def violacao_ficticia(
    motivo: MotivoViolacao = MotivoViolacao.TIPO_NAO_ACEITO,
    campo_yaml: str = "eventos.nao_aceitos",
    valor_informado: str | int = "tipo-artificial-bloqueado",
) -> Violacao:
    return Violacao(motivo=motivo, campo_yaml=campo_yaml, valor_informado=valor_informado)


# 1. Os cinco resultados oficiais


def test_dados_completos_e_compativeis_produzem_qualificado() -> None:
    resultado = qualificar(dados_ficticios(), (), (), base_ficticia())

    assert resultado == Qualificacao(
        resultado=ResultadoQualificacao.QUALIFICADO,
        motivo=MotivoQualificacao.COMPATIVEL,
    )


def test_faixa_com_formato_sentado_produz_qualificado_com_ressalva() -> None:
    dados = dados_ficticios(convidados=SENTADOS + 1, formato=FormatoEvento.SENTADO)

    resultado = qualificar(dados, (), (), base_ficticia())

    assert resultado.resultado is ResultadoQualificacao.QUALIFICADO_COM_RESSALVA
    assert resultado.motivo is MotivoQualificacao.FORMATO_SENTADO_ACIMA_CAPACIDADE_SENTADA


def test_violacao_recebida_produz_incompativel() -> None:
    violacao = violacao_ficticia()

    resultado = qualificar(dados_ficticios(), (violacao,), (), base_ficticia())

    assert resultado.resultado is ResultadoQualificacao.INCOMPATIVEL
    assert resultado.motivo is MotivoQualificacao.VIOLACAO_OBJETIVA
    assert resultado.violacoes == (violacao,)


def test_campo_obrigatorio_ausente_produz_dados_incompletos() -> None:
    resultado = qualificar(dados_ficticios(nome=None), (), (), base_ficticia())

    assert resultado.resultado is ResultadoQualificacao.DADOS_INCOMPLETOS
    assert resultado.motivo is MotivoQualificacao.CAMPOS_OBRIGATORIOS_AUSENTES
    assert resultado.campos_ausentes == ("nome",)


def test_pendencia_impeditiva_com_dados_completos_produz_indefinido() -> None:
    """Fixture artificial: o identificador é opaco e não é conferido na base."""
    resultado = qualificar(
        dados_ficticios(), (), ("pendencia-artificial-1",), base_ficticia()
    )

    assert resultado.resultado is ResultadoQualificacao.INDEFINIDO
    assert resultado.motivo is MotivoQualificacao.PENDENCIA_IMPEDITIVA
    assert resultado.pendencias_impeditivas == ("pendencia-artificial-1",)


# 2. Ausência isolada de cada campo obrigatório


def test_contato_ausente() -> None:
    resultado = qualificar(dados_ficticios(contato=None), (), (), base_ficticia())

    assert resultado.campos_ausentes == ("contato",)


def test_tipo_evento_ausente() -> None:
    resultado = qualificar(dados_ficticios(tipo_evento=None), (), (), base_ficticia())

    assert resultado.campos_ausentes == ("tipo_evento",)


def test_data_nomeada_ausente() -> None:
    resultado = qualificar(dados_ficticios(data_nomeada=None), (), (), base_ficticia())

    assert resultado.campos_ausentes == ("data_nomeada",)


def test_convidados_ausente() -> None:
    resultado = qualificar(dados_ficticios(convidados=None), (), (), base_ficticia())

    assert resultado.campos_ausentes == ("convidados",)


def test_texto_em_branco_conta_como_ausente() -> None:
    resultado = qualificar(
        dados_ficticios(tipo_evento="   ", data_nomeada=""), (), (), base_ficticia()
    )

    assert resultado.campos_ausentes == ("tipo_evento", "data_nomeada")


def test_ausencia_de_qualquer_campo_nunca_produz_incompativel() -> None:
    for ajuste in (
        {"nome": None},
        {"contato": None},
        {"tipo_evento": None},
        {"data_nomeada": None},
        {"convidados": None},
    ):
        resultado = qualificar(dados_ficticios(**ajuste), (), (), base_ficticia())

        assert resultado.resultado is ResultadoQualificacao.DADOS_INCOMPLETOS


def test_ordem_dos_campos_ausentes_e_deterministica() -> None:
    dados = dados_ficticios(
        nome=None, contato=None, tipo_evento=None, data_nomeada=None, convidados=None
    )

    resultado = qualificar(dados, (), (), base_ficticia())

    assert resultado.campos_ausentes == (
        "nome",
        "contato",
        "tipo_evento",
        "data_nomeada",
        "convidados",
    )


# 3. Formato condicional e faixa de capacidade


def test_formato_ausente_na_faixa_entra_em_campos_ausentes() -> None:
    dados = dados_ficticios(convidados=SENTADOS + 1, formato=None)

    resultado = qualificar(dados, (), (), base_ficticia())

    assert resultado.resultado is ResultadoQualificacao.DADOS_INCOMPLETOS
    assert resultado.campos_ausentes == ("formato",)


def test_faixa_com_formato_coquetel_produz_qualificado() -> None:
    dados = dados_ficticios(convidados=SENTADOS + 1, formato=FormatoEvento.COQUETEL)

    resultado = qualificar(dados, (), (), base_ficticia())

    assert resultado.resultado is ResultadoQualificacao.QUALIFICADO


def test_abaixo_da_faixa_formato_ausente_nao_impede_qualificacao() -> None:
    dados = dados_ficticios(convidados=SENTADOS - 1, formato=None)

    resultado = qualificar(dados, (), (), base_ficticia())

    assert resultado.resultado is ResultadoQualificacao.QUALIFICADO


def test_borda_igual_a_capacidade_sentada_mantem_formato_opcional() -> None:
    dados = dados_ficticios(convidados=SENTADOS, formato=None)

    resultado = qualificar(dados, (), (), base_ficticia())

    assert resultado.resultado is ResultadoQualificacao.QUALIFICADO


def test_borda_superior_da_faixa_ainda_exige_formato() -> None:
    dados = dados_ficticios(convidados=COQUETEL, formato=None)

    resultado = qualificar(dados, (), (), base_ficticia())

    assert resultado.campos_ausentes == ("formato",)


def test_formato_sentado_abaixo_da_faixa_nao_gera_ressalva() -> None:
    dados = dados_ficticios(convidados=SENTADOS, formato=FormatoEvento.SENTADO)

    resultado = qualificar(dados, (), (), base_ficticia())

    assert resultado.resultado is ResultadoQualificacao.QUALIFICADO


def test_limites_diferentes_na_base_alteram_a_decisao() -> None:
    """Prova leitura dinâmica: o mesmo dado muda de resultado com outra base."""
    dados = dados_ficticios(convidados=SENTADOS + 1, formato=FormatoEvento.SENTADO)

    com_faixa = qualificar(dados, (), (), base_ficticia())
    fora_da_faixa = qualificar(
        dados, (), (), base_ficticia(sentados=SENTADOS + 5, coquetel=COQUETEL + 5)
    )

    assert com_faixa.resultado is ResultadoQualificacao.QUALIFICADO_COM_RESSALVA
    assert fora_da_faixa.resultado is ResultadoQualificacao.QUALIFICADO


# 4. Violações recebidas


def test_multiplas_violacoes_sao_repassadas_integralmente() -> None:
    primeira = violacao_ficticia()
    segunda = violacao_ficticia(
        motivo=MotivoViolacao.DATA_NAO_ACEITA,
        campo_yaml="eventos.datas_nao_aceitas",
        valor_informado="data-artificial-bloqueada",
    )

    resultado = qualificar(dados_ficticios(), (primeira, segunda), (), base_ficticia())

    assert resultado.resultado is ResultadoQualificacao.INCOMPATIVEL
    assert resultado.violacoes == (primeira, segunda)
    assert [v.campo_yaml for v in resultado.violacoes] == [
        "eventos.nao_aceitos",
        "eventos.datas_nao_aceitas",
    ]


def test_violacao_prevalece_sobre_campo_ausente() -> None:
    resultado = qualificar(
        dados_ficticios(nome=None, convidados=None), (violacao_ficticia(),), (), base_ficticia()
    )

    assert resultado.resultado is ResultadoQualificacao.INCOMPATIVEL
    assert resultado.campos_ausentes == ()


def test_violacao_prevalece_sobre_pendencia_impeditiva() -> None:
    resultado = qualificar(
        dados_ficticios(),
        (violacao_ficticia(),),
        ("pendencia-artificial-1",),
        base_ficticia(),
    )

    assert resultado.resultado is ResultadoQualificacao.INCOMPATIVEL
    assert resultado.pendencias_impeditivas == ()


def test_campo_ausente_prevalece_sobre_pendencia_impeditiva() -> None:
    resultado = qualificar(
        dados_ficticios(nome=None), (), ("pendencia-artificial-1",), base_ficticia()
    )

    assert resultado.resultado is ResultadoQualificacao.DADOS_INCOMPLETOS
    assert resultado.pendencias_impeditivas == ()


def test_pendencia_vazia_nao_produz_indefinido() -> None:
    resultado = qualificar(dados_ficticios(), (), (), base_ficticia())

    assert resultado.resultado is not ResultadoQualificacao.INDEFINIDO


# 5. Fail-closed de integração


def test_convidados_acima_do_limite_sem_violacao_e_incoerencia() -> None:
    """Sem a saída obrigatória da 3B.2, classificar seria falso positivo."""
    dados = dados_ficticios(convidados=COQUETEL + 1)

    with pytest.raises(ValueError):
        qualificar(dados, (), (), base_ficticia())


def test_convidados_acima_do_limite_com_violacao_produz_incompativel() -> None:
    violacao = violacao_ficticia(
        motivo=MotivoViolacao.CONVIDADOS_ACIMA_DA_CAPACIDADE,
        campo_yaml="capacidade.formato_coquetel",
        valor_informado=COQUETEL + 1,
    )

    resultado = qualificar(
        dados_ficticios(convidados=COQUETEL + 1), (violacao,), (), base_ficticia()
    )

    assert resultado.resultado is ResultadoQualificacao.INCOMPATIVEL


def test_mensagem_de_incoerencia_nao_expoe_valor_da_base() -> None:
    with pytest.raises(ValueError) as erro:
        qualificar(dados_ficticios(convidados=COQUETEL + 1), (), (), base_ficticia())

    assert str(COQUETEL) not in str(erro.value)


# 6. Erros de contrato dos dados


def test_campos_textuais_de_tipo_invalido_sao_erro_de_contrato() -> None:
    for ajuste in (
        {"nome": 1},
        {"contato": 1},
        {"tipo_evento": 1},
        {"data_nomeada": 1},
    ):
        with pytest.raises(TypeError):
            qualificar(dados_ficticios(**ajuste), (), (), base_ficticia())


def test_convidados_booleano_e_erro_de_contrato() -> None:
    with pytest.raises(TypeError):
        qualificar(dados_ficticios(convidados=True), (), (), base_ficticia())


def test_convidados_nao_inteiro_e_erro_de_contrato() -> None:
    with pytest.raises(TypeError):
        qualificar(dados_ficticios(convidados="3"), (), (), base_ficticia())


def test_convidados_negativo_e_erro_de_contrato() -> None:
    with pytest.raises(ValueError):
        qualificar(dados_ficticios(convidados=-1), (), (), base_ficticia())


def test_convidados_zero_e_valor_valido() -> None:
    """Não existe mínimo aprovado de convidados nesta camada."""
    resultado = qualificar(dados_ficticios(convidados=0), (), (), base_ficticia())

    assert resultado.resultado is ResultadoQualificacao.QUALIFICADO


def test_formato_como_texto_livre_e_erro_de_contrato() -> None:
    """Sinônimo e conversão pertencem à interpretação futura, não aqui."""
    with pytest.raises(TypeError):
        qualificar(dados_ficticios(formato="sentado"), (), (), base_ficticia())


def test_violacoes_fora_do_contrato_sao_erro() -> None:
    with pytest.raises(TypeError):
        qualificar(dados_ficticios(), [violacao_ficticia()], (), base_ficticia())
    with pytest.raises(TypeError):
        qualificar(dados_ficticios(), ("violacao-invalida",), (), base_ficticia())


def test_pendencias_fora_do_contrato_sao_erro() -> None:
    with pytest.raises(TypeError):
        qualificar(dados_ficticios(), (), ["pendencia-artificial-1"], base_ficticia())
    with pytest.raises(TypeError):
        qualificar(dados_ficticios(), (), (1,), base_ficticia())
    with pytest.raises(ValueError):
        qualificar(dados_ficticios(), (), ("   ",), base_ficticia())


# 7. Erros estruturais da base


def test_base_de_tipo_invalido_e_erro_estrutural() -> None:
    with pytest.raises(TypeError):
        qualificar(dados_ficticios(), (), (), "base-invalida")  # type: ignore[arg-type]


def test_base_sem_capacidade_e_erro_estrutural() -> None:
    with pytest.raises(ValueError):
        qualificar(dados_ficticios(), (), (), {})


def test_capacidade_de_tipo_invalido_e_erro_estrutural() -> None:
    with pytest.raises(TypeError):
        qualificar(dados_ficticios(), (), (), {"capacidade": ["7", "9"]})


def test_capacidade_com_campo_ausente_e_erro_estrutural() -> None:
    with pytest.raises(ValueError):
        qualificar(
            dados_ficticios(), (), (), {"capacidade": {"convidados_sentados": SENTADOS}}
        )


def test_limite_nao_inteiro_e_erro_estrutural() -> None:
    with pytest.raises(TypeError):
        qualificar(
            dados_ficticios(),
            (),
            (),
            {"capacidade": {"convidados_sentados": SENTADOS, "formato_coquetel": True}},
        )


def test_faixas_de_capacidade_incoerentes_sao_erro_estrutural() -> None:
    with pytest.raises(ValueError):
        qualificar(
            dados_ficticios(),
            (),
            (),
            base_ficticia(sentados=COQUETEL + 1, coquetel=COQUETEL),
        )


# 8. Pureza, determinismo e ausência de dado pessoal na saída


def test_insumos_nao_sao_mutados() -> None:
    dados = dados_ficticios(convidados=SENTADOS + 1, formato=FormatoEvento.SENTADO)
    original_dados = dados_ficticios(
        convidados=SENTADOS + 1, formato=FormatoEvento.SENTADO
    )
    violacoes = (violacao_ficticia(),)
    original_violacoes = (violacao_ficticia(),)
    pendencias = ("pendencia-artificial-1",)
    base = base_ficticia()
    original_base = copy.deepcopy(base)

    qualificar(dados, violacoes, pendencias, base)

    assert dados == original_dados
    assert violacoes == original_violacoes
    assert pendencias == ("pendencia-artificial-1",)
    assert base == original_base


def test_chamadas_repetidas_produzem_a_mesma_saida() -> None:
    dados = dados_ficticios(convidados=SENTADOS + 1, formato=FormatoEvento.SENTADO)

    primeira = qualificar(dados, (), (), base_ficticia())
    segunda = qualificar(dados, (), (), base_ficticia())

    assert primeira == segunda


def test_saida_nao_contem_nome_nem_contato() -> None:
    incompletos = qualificar(dados_ficticios(tipo_evento=None), (), (), base_ficticia())
    qualificado = qualificar(dados_ficticios(), (), (), base_ficticia())

    for resultado in (incompletos, qualificado):
        assert "nome-artificial" not in repr(resultado)
        assert "contato-artificial" not in repr(resultado)


def test_resultado_assume_somente_os_cinco_valores_oficiais() -> None:
    assert [membro.value for membro in ResultadoQualificacao] == [
        "dados_incompletos",
        "qualificado",
        "qualificado_com_ressalva",
        "incompativel",
        "indefinido",
    ]


# 9. Sem duplicação da 3B.2, sem constante comercial, sem LLM/rede/persistência


def test_qualificacao_nao_duplica_regras_nem_acessa_recurso_externo() -> None:
    permitidos = {"__future__", "dataclasses", "enum", "typing", "casa77_sdr"}
    proibidos = {
        "os",
        "io",
        "pathlib",
        "json",
        "sqlite3",
        "http",
        "urllib",
        "socket",
        "requests",
        "anthropic",
        "openai",
        "random",
        "time",
        "logging",
        "yaml",
    }

    arvore = ast.parse(MODULO_QUALIFICACAO.read_text(encoding="utf-8"))
    modulos: set[str] = set()
    importados_do_projeto: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            modulos.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            modulos.add(no.module)
            if no.module.startswith("casa77_sdr"):
                importados_do_projeto.update(alias.name for alias in no.names)

    raizes = {modulo.split(".")[0] for modulo in modulos}
    assert raizes <= permitidos
    assert not (raizes & proibidos)

    internos = {modulo for modulo in modulos if modulo.startswith("casa77_sdr")}
    assert internos <= {"casa77_sdr.rules"}
    assert importados_do_projeto <= {"DadosAtendimento", "Violacao"}

    referencias = {
        no.id for no in ast.walk(arvore) if isinstance(no, ast.Name)
    } | {no.attr for no in ast.walk(arvore) if isinstance(no, ast.Attribute)}
    assert "avaliar_regras" not in referencias

    textos = {
        no.value
        for no in ast.walk(arvore)
        if isinstance(no, ast.Constant) and isinstance(no.value, str)
    }
    assert "eventos.nao_aceitos" not in textos
    assert "eventos.datas_nao_aceitas" not in textos
    assert not [texto for texto in textos if "nao_aceit" in texto]


def test_qualificacao_nao_tem_constante_comercial() -> None:
    """Todo limite vem da base recebida (I06).

    O único literal numérico tolerado é o zero da conferência de negativo —
    limite estrutural do tipo, não quantidade comercial. Qualquer capacidade,
    faixa, preço ou duração escrita no módulo reprovaria aqui.
    """
    arvore = ast.parse(MODULO_QUALIFICACAO.read_text(encoding="utf-8"))

    numeros = {
        no.value
        for no in ast.walk(arvore)
        if isinstance(no, ast.Constant)
        and isinstance(no.value, (int, float))
        and not isinstance(no.value, bool)
    }

    assert numeros <= {0}

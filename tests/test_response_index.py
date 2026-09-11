"""Testes do validador estrutural do futuro índice de respostas aprovadas.

Nenhum teste cria `knowledge/indice-respostas-aprovadas.yaml` e nenhum teste
altera arquivo do repositório. Todos os fixtures são sintéticos: identificadores,
caminhos e nomes são inventados, e nenhum valor comercial real aparece como
expectativa. A única leitura de `knowledge/casa77.yaml` é read-only, e serve
apenas para confrontar os valores comerciais atuais contra a AST do módulo de
produção — o mesmo precedente de `test_carregador_nao_tem_constante_comercial`.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import pytest
import yaml

from casa77_sdr.response_index import IndiceInvalido, validar_indice
from casa77_sdr.response_placeholder import PlaceholderInvalido
from casa77_sdr.response_yaml_path import CaminhoYamlInvalido
from casa77_sdr.response_yaml_path_context import CaminhoYamlContextoInvalido

RAIZ = Path(__file__).resolve().parents[1]
YAML_REAL = RAIZ / "knowledge" / "casa77.yaml"
MODULO = RAIZ / "src" / "casa77_sdr" / "response_index.py"
MODULO_INIT = RAIZ / "src" / "casa77_sdr" / "__init__.py"


# Fixtures sintéticos


def binding_renderizado(**extra: Any) -> dict[str, Any]:
    binding: dict[str, Any] = {
        "nome": "quantidade_exemplo",
        "mecanismo": "RENDERIZADO",
        "origem": "YAML",
        "caminho_yaml": "bloco_exemplo.campo_exemplo",
        "placeholder": "{{quantidade_exemplo}}",
        "formato": "inteiro",
    }
    binding.update(extra)
    return binding


def binding_assertiva(**extra: Any) -> dict[str, Any]:
    binding: dict[str, Any] = {
        "nome": "condicao_exemplo",
        "mecanismo": "ASSERTIVA",
        "origem": "YAML",
        "caminho_yaml": "bloco_exemplo.flag_exemplo",
        "predicado": "EH_VERDADEIRO",
    }
    binding.update(extra)
    return binding


def binding_runtime(**extra: Any) -> dict[str, Any]:
    binding: dict[str, Any] = {
        "nome": "consulta_exemplo",
        "mecanismo": "ASSERTIVA",
        "origem": "RUNTIME_AUTORITATIVO",
        "fato_runtime": "consulta_calendario_valida",
        "predicado": "EH_VERDADEIRO",
    }
    binding.update(extra)
    return binding


def fragmento(**extra: Any) -> dict[str, Any]:
    corpo: dict[str, Any] = {
        "id": "F1",
        "status": "APROVADO",
        "bindings": [],
    }
    corpo.update(extra)
    return corpo


def resposta(**extra: Any) -> dict[str, Any]:
    corpo: dict[str, Any] = {"id": "R01", "fragmentos": [fragmento()]}
    corpo.update(extra)
    return corpo


def indice(*respostas: dict[str, Any]) -> dict[str, Any]:
    return {"respostas": list(respostas)}


def categoria_de(erro: pytest.ExceptionInfo[IndiceInvalido]) -> str:
    return str(erro.value).split(":", 1)[0]


def localizador_de(erro: pytest.ExceptionInfo[IndiceInvalido]) -> str:
    return str(erro.value).split(":", 1)[1].strip()


# 1. Estruturas válidas


def test_raiz_valida_minima() -> None:
    assert validar_indice(indice(resposta())) is None


def test_respostas_vazia_e_valida() -> None:
    """E1 valida forma; completude e bijeção pertencem à entrega seguinte."""
    assert validar_indice({"respostas": []}) is None


def test_renderizado_yaml_valido() -> None:
    corpo = indice(
        resposta(fragmentos=[fragmento(bindings=[binding_renderizado()])])
    )

    assert validar_indice(corpo) is None


def test_assertiva_yaml_valida() -> None:
    corpo = indice(
        resposta(fragmentos=[fragmento(bindings=[binding_assertiva()])])
    )

    assert validar_indice(corpo) is None


def test_assertiva_runtime_valida() -> None:
    corpo = indice(
        resposta(fragmentos=[fragmento(bindings=[binding_runtime()])])
    )

    assert validar_indice(corpo) is None


def test_itera_sobre_valido() -> None:
    corpo = indice(
        resposta(
            fragmentos=[
                fragmento(
                    itera_sobre="bloco_exemplo.colecao_exemplo",
                    bindings=[binding_renderizado()],
                )
            ]
        )
    )

    assert validar_indice(corpo) is None


@pytest.mark.parametrize(
    "predicado", ["EH_VERDADEIRO", "EH_FALSO"]
)
def test_predicados_do_vocabulario_fechado(predicado: str) -> None:
    corpo = indice(
        resposta(
            fragmentos=[
                fragmento(bindings=[binding_assertiva(predicado=predicado)])
            ]
        )
    )

    assert validar_indice(corpo) is None


@pytest.mark.parametrize(
    "formato",
    ["inteiro", "inteiro_agrupado", "simbolo_moeda", "hora", "texto", "lista"],
)
def test_formatos_do_vocabulario_fechado(formato: str) -> None:
    corpo = indice(
        resposta(
            fragmentos=[
                fragmento(bindings=[binding_renderizado(formato=formato)])
            ]
        )
    )

    assert validar_indice(corpo) is None


@pytest.mark.parametrize(
    "status", ["APROVADO", "AGUARDA_APROVACAO", "BLOQUEADO"]
)
def test_status_do_vocabulario_fechado(status: str) -> None:
    assert validar_indice(indice(resposta(fragmentos=[fragmento(status=status)]))) is None


@pytest.mark.parametrize(
    "fato", ["consulta_calendario_valida", "data_disponivel"]
)
def test_fatos_runtime_do_vocabulario_fechado(fato: str) -> None:
    corpo = indice(
        resposta(
            fragmentos=[
                fragmento(bindings=[binding_runtime(fato_runtime=fato)])
            ]
        )
    )

    assert validar_indice(corpo) is None


# 2. Raiz


@pytest.mark.parametrize("raiz", [[], "texto", 0, None, ()])
def test_raiz_nao_mapeamento(raiz: object) -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(raiz)

    assert categoria_de(erro) == "tipo_invalido"


def test_raiz_com_chave_extra() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice({"respostas": [], "versao": "0.0-teste"})

    assert categoria_de(erro) == "campo_desconhecido"


def test_raiz_sem_respostas() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice({})

    assert categoria_de(erro) == "campo_ausente"


def test_respostas_nao_lista() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice({"respostas": {}})

    assert categoria_de(erro) == "tipo_invalido"
    assert localizador_de(erro) == "respostas"


# 3. Rxx


@pytest.mark.parametrize(
    "identificador", ["R1", "R001", "r01", "X01", "R0A", "", "R01 ", "R٠١"]
)
def test_id_de_resposta_invalido(identificador: str) -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(id=identificador)))

    assert categoria_de(erro) == "valor_invalido"


def test_id_de_resposta_nao_texto() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(id=1)))

    assert categoria_de(erro) == "tipo_invalido"


def test_id_de_resposta_duplicado() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(), resposta()))

    assert categoria_de(erro) == "duplicidade"
    assert localizador_de(erro) == "respostas[1].id"


def test_resposta_nao_mapeamento() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice({"respostas": ["R01"]})

    assert categoria_de(erro) == "tipo_invalido"
    assert localizador_de(erro) == "respostas[0]"


def test_resposta_sem_fragmentos() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice({"respostas": [{"id": "R01"}]})

    assert categoria_de(erro) == "campo_ausente"
    assert localizador_de(erro) == "respostas[0].fragmentos"


def test_fragmentos_vazio_rejeitado() -> None:
    """C-2c: um `Rxx` tem um ou mais fragmentos."""
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=[])))

    assert categoria_de(erro) == "valor_invalido"
    assert localizador_de(erro) == "respostas[0].fragmentos"


def test_fragmentos_nao_lista() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos={})))

    assert categoria_de(erro) == "tipo_invalido"


@pytest.mark.parametrize(
    "chave", ["status", "titulo", "handoff_obrigatorio", "cita_fato_comercial"]
)
def test_chave_proibida_no_nivel_da_resposta(chave: str) -> None:
    """C-2d, C-2e, C-2f e C-2g: nada disso vive no nível do `Rxx`."""
    corpo = resposta()
    corpo[chave] = "APROVADO" if chave == "status" else True

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(corpo))

    assert categoria_de(erro) == "campo_desconhecido"
    assert localizador_de(erro) == f"respostas[0].{chave}"


# 4. Fragmento


def test_id_de_fragmento_duplicado_no_mesmo_rxx() -> None:
    corpo = indice(resposta(fragmentos=[fragmento(), fragmento()]))

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(corpo)

    assert categoria_de(erro) == "duplicidade"
    assert localizador_de(erro) == "respostas[0].fragmentos[1].id"


def test_mesmo_id_de_fragmento_em_rxx_diferentes_e_valido() -> None:
    """A unicidade do id de fragmento é interna ao `Rxx` (C-2h)."""
    corpo = indice(resposta(), resposta(id="R02"))

    assert validar_indice(corpo) is None


def test_fragmento_sem_status() -> None:
    corpo = fragmento()
    del corpo["status"]

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=[corpo])))

    assert categoria_de(erro) == "campo_ausente"
    assert localizador_de(erro) == "respostas[0].fragmentos[0].status"


@pytest.mark.parametrize(
    "status", ["PARCIAL", "aprovado", "APROVADO com handoff", "", "PENDENTE"]
)
def test_status_invalido(status: str) -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=[fragmento(status=status)])))

    assert categoria_de(erro) == "valor_invalido"
    assert localizador_de(erro) == "respostas[0].fragmentos[0].status"


def test_status_nao_texto() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=[fragmento(status=True)])))

    assert categoria_de(erro) == "tipo_invalido"


def test_fragmento_sem_id() -> None:
    corpo = fragmento()
    del corpo["id"]

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=[corpo])))

    assert categoria_de(erro) == "campo_ausente"


def test_id_de_fragmento_vazio() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=[fragmento(id="")])))

    assert categoria_de(erro) == "valor_invalido"


def test_bindings_ausente() -> None:
    corpo = fragmento()
    del corpo["bindings"]

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=[corpo])))

    assert categoria_de(erro) == "campo_ausente"
    assert localizador_de(erro) == "respostas[0].fragmentos[0].bindings"


def test_bindings_lista_vazia_e_valida() -> None:
    """C-2k: a lista vazia é explícita e legítima."""
    assert validar_indice(indice(resposta(fragmentos=[fragmento(bindings=[])]))) is None


def test_bindings_nao_lista() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=[fragmento(bindings={})])))

    assert categoria_de(erro) == "tipo_invalido"


def test_itera_sobre_vazio() -> None:
    corpo = fragmento(itera_sobre="")

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=[corpo])))

    assert categoria_de(erro) == "valor_invalido"


def test_itera_sobre_nao_texto() -> None:
    corpo = fragmento(itera_sobre=[])

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=[corpo])))

    assert categoria_de(erro) == "tipo_invalido"


def test_chave_desconhecida_no_fragmento() -> None:
    corpo = fragmento(texto="qualquer coisa")

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=[corpo])))

    assert categoria_de(erro) == "campo_desconhecido"
    assert localizador_de(erro) == "respostas[0].fragmentos[0].texto"


def test_fragmento_nao_mapeamento() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=["F1"])))

    assert categoria_de(erro) == "tipo_invalido"
    assert localizador_de(erro) == "respostas[0].fragmentos[0]"


# 5. Binding — forma base


def _com_binding(binding: dict[str, Any]) -> dict[str, Any]:
    return indice(resposta(fragmentos=[fragmento(bindings=[binding])]))


def test_binding_sem_nome() -> None:
    binding = binding_renderizado()
    del binding["nome"]

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding))

    assert categoria_de(erro) == "campo_ausente"
    assert localizador_de(erro) == "respostas[0].fragmentos[0].bindings[0].nome"


def test_binding_nome_duplicado_no_fragmento() -> None:
    corpo = indice(
        resposta(
            fragmentos=[
                fragmento(
                    bindings=[
                        binding_renderizado(),
                        binding_assertiva(nome="quantidade_exemplo"),
                    ]
                )
            ]
        )
    )

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(corpo)

    assert categoria_de(erro) == "duplicidade"
    assert localizador_de(erro) == "respostas[0].fragmentos[0].bindings[1].nome"


def test_binding_nome_vazio() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding_renderizado(nome="")))

    assert categoria_de(erro) == "valor_invalido"


def test_binding_sem_mecanismo() -> None:
    binding = binding_renderizado()
    del binding["mecanismo"]

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding))

    assert categoria_de(erro) == "campo_ausente"


@pytest.mark.parametrize(
    "mecanismo", ["renderizado", "ASSERCAO", "", "RENDERIZAR"]
)
def test_mecanismo_invalido(mecanismo: str) -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding_renderizado(mecanismo=mecanismo)))

    assert categoria_de(erro) == "valor_invalido"


def test_binding_sem_origem() -> None:
    """C-A2-RT4: ausência de origem não é lida como `YAML`."""
    binding = binding_renderizado()
    del binding["origem"]

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding))

    assert categoria_de(erro) == "campo_ausente"
    assert localizador_de(erro) == "respostas[0].fragmentos[0].bindings[0].origem"


@pytest.mark.parametrize("origem", ["yaml", "RUNTIME", "", "BASE"])
def test_origem_invalida(origem: str) -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding_renderizado(origem=origem)))

    assert categoria_de(erro) == "valor_invalido"


def test_chave_desconhecida_no_binding() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding_renderizado(snapshot="qualquer")))

    assert categoria_de(erro) == "campo_desconhecido"


def test_binding_nao_mapeamento() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding("nome"))

    assert categoria_de(erro) == "tipo_invalido"
    assert localizador_de(erro) == "respostas[0].fragmentos[0].bindings[0]"


# 6. Referente por origem


def test_yaml_sem_caminho() -> None:
    binding = binding_renderizado()
    del binding["caminho_yaml"]

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding))

    assert categoria_de(erro) == "campo_ausente"


def test_yaml_com_fato_runtime() -> None:
    binding = binding_assertiva(fato_runtime="data_disponivel")

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding))

    assert categoria_de(erro) == "combinacao_invalida"


def test_caminho_yaml_vazio() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding_renderizado(caminho_yaml="")))

    assert categoria_de(erro) == "valor_invalido"


def test_caminho_yaml_nao_texto() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding_renderizado(caminho_yaml=[])))

    assert categoria_de(erro) == "tipo_invalido"


def test_runtime_sem_fato_runtime() -> None:
    binding = binding_runtime()
    del binding["fato_runtime"]

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding))

    assert categoria_de(erro) == "campo_ausente"


def test_runtime_com_caminho_yaml() -> None:
    binding = binding_runtime(caminho_yaml="bloco_exemplo.campo_exemplo")

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding))

    assert categoria_de(erro) == "combinacao_invalida"


def test_runtime_com_renderizado() -> None:
    """C-A2-V4: `RENDERIZADO` sobre fato runtime é proibido."""
    binding = {
        "nome": "consulta_exemplo",
        "mecanismo": "RENDERIZADO",
        "origem": "RUNTIME_AUTORITATIVO",
        "fato_runtime": "data_disponivel",
        "placeholder": "{{consulta_exemplo}}",
        "formato": "texto",
    }

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding))

    assert categoria_de(erro) == "combinacao_invalida"


@pytest.mark.parametrize(
    "fato", ["consulta", "DATA_DISPONIVEL", "", "data_reservada"]
)
def test_fato_runtime_invalido(fato: str) -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding_runtime(fato_runtime=fato)))

    assert categoria_de(erro) == "valor_invalido"


def test_fato_runtime_nao_texto() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding_runtime(fato_runtime=1)))

    assert categoria_de(erro) == "tipo_invalido"


# 7. RENDERIZADO


def test_renderizado_sem_placeholder() -> None:
    binding = binding_renderizado()
    del binding["placeholder"]

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding))

    assert categoria_de(erro) == "campo_ausente"


def test_renderizado_sem_formato() -> None:
    binding = binding_renderizado()
    del binding["formato"]

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding))

    assert categoria_de(erro) == "campo_ausente"


def test_renderizado_com_predicado() -> None:
    binding = binding_renderizado(predicado="EH_VERDADEIRO")

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding))

    assert categoria_de(erro) == "combinacao_invalida"


def test_placeholder_vazio() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding_renderizado(placeholder="")))

    assert categoria_de(erro) == "valor_invalido"


@pytest.mark.parametrize(
    "formato", ["moeda", "INTEIRO", "", "data", "inteiro_com_ponto"]
)
def test_formato_invalido(formato: str) -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding_renderizado(formato=formato)))

    assert categoria_de(erro) == "valor_invalido"


# 8. ASSERTIVA


def test_assertiva_sem_predicado() -> None:
    binding = binding_assertiva()
    del binding["predicado"]

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding))

    assert categoria_de(erro) == "campo_ausente"


def test_assertiva_com_placeholder() -> None:
    binding = binding_assertiva(placeholder="{{condicao_exemplo}}")

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding))

    assert categoria_de(erro) == "combinacao_invalida"


def test_assertiva_com_formato() -> None:
    binding = binding_assertiva(formato="texto")

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding))

    assert categoria_de(erro) == "combinacao_invalida"


@pytest.mark.parametrize(
    "predicado", ["EH_NULO", "eh_verdadeiro", "", "VERDADEIRO"]
)
def test_predicado_invalido(predicado: str) -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding_assertiva(predicado=predicado)))

    assert categoria_de(erro) == "valor_invalido"


# 9. Seleção posicional — agora recusada pela gramática canônica de `CY13`
#
# `C-A1-S1` continua valendo, mas E1 deixou de detectar "posição" por heurística
# própria: `[0]` não tem forma de seletor e chave exclusivamente numérica não é
# endereçável (`CY9`). As duas formas viram `valor_invalido`, e a categoria
# `selecao_posicional` deixou de ser produzida — deliberadamente.


@pytest.mark.parametrize(
    "caminho",
    [
        "colecao_exemplo.0.campo_exemplo",
        "colecao_exemplo.12.campo_exemplo",
        "colecao_exemplo[0]",
        "colecao_exemplo[12].campo_exemplo",
        "bloco_exemplo.colecao_exemplo[3].item_exemplo",
    ],
)
def test_forma_posicional_em_caminho_yaml_e_valor_invalido(caminho: str) -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding_renderizado(caminho_yaml=caminho)))

    assert categoria_de(erro) == "valor_invalido"


@pytest.mark.parametrize(
    "caminho",
    ["colecao_exemplo.0.campo_exemplo", "colecao_exemplo[0].campo_exemplo"],
)
def test_forma_posicional_em_itera_sobre_e_valor_invalido(caminho: str) -> None:
    corpo = fragmento(itera_sobre=caminho)

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=[corpo])))

    assert categoria_de(erro) == "valor_invalido"
    assert localizador_de(erro) == "respostas[0].fragmentos[0].itera_sobre"


def test_selecao_posicional_nao_e_mais_categoria_de_e1() -> None:
    """A categoria foi retirada: nenhuma forma posicional a produz mais."""
    for caminho in ("colecao_exemplo[0]", "colecao_exemplo.0.campo_exemplo"):
        with pytest.raises(IndiceInvalido) as erro:
            validar_indice(
                _com_binding(binding_renderizado(caminho_yaml=caminho))
            )

        assert categoria_de(erro) != "selecao_posicional"


@pytest.mark.parametrize(
    "caminho",
    [
        "colecao_exemplo[id=teste].campo_exemplo",
        "colecao_exemplo[codigo=teste].campo_exemplo",
        "bloco_exemplo.colecao_exemplo[id=item_exemplo].quantidade_exemplo",
        "bloco_exemplo.campo_exemplo",
    ],
)
def test_seletor_textual_canonico_e_aceito(caminho: str) -> None:
    """Um seletor por segmento, com chave e literal em `NOME`, é canônico."""
    corpo = _com_binding(binding_renderizado(caminho_yaml=caminho))

    assert validar_indice(corpo) is None


@pytest.mark.parametrize(
    "caminho",
    [
        "colecao_exemplo[id=teste][0].campo_exemplo",
        "colecao_exemplo[codigo=teste][12].campo_exemplo",
        "colecao_exemplo[id=teste].subcolecao_exemplo[0].campo_exemplo",
        "colecao_exemplo[id=teste][0][codigo=outro].campo_exemplo",
        "colecao_exemplo[id=teste][1]",
        "colecao_exemplo[id=teste][999].campo_exemplo",
        "bloco_exemplo.colecao_exemplo[codigo=teste][0]",
    ],
)
def test_indice_numerico_apos_seletor_textual_e_valor_invalido(
    caminho: str,
) -> None:
    """Dois seletores no mesmo segmento já quebram a gramática canônica."""
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding_renderizado(caminho_yaml=caminho)))

    assert categoria_de(erro) == "valor_invalido"


@pytest.mark.parametrize(
    "caminho",
    [
        "colecao_exemplo[id=teste][0]",
        "colecao_exemplo[codigo=teste][12].subcolecao_exemplo",
        "colecao_exemplo[id=teste].subcolecao_exemplo[0]",
    ],
)
def test_indice_numerico_apos_seletor_textual_em_itera_sobre(
    caminho: str,
) -> None:
    corpo = fragmento(itera_sobre=caminho)

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=[corpo])))

    assert categoria_de(erro) == "valor_invalido"
    assert localizador_de(erro) == "respostas[0].fragmentos[0].itera_sobre"


@pytest.mark.parametrize(
    "caminho",
    [
        "colecao_exemplo[id=teste][codigo=outro].campo_exemplo",
        "colecao_exemplo[id=teste][codigo=outro]",
        "bloco_exemplo.colecao_exemplo[id=teste][codigo=outro].campo_exemplo",
    ],
)
def test_seletores_encadeados_no_mesmo_segmento_sao_invalidos(
    caminho: str,
) -> None:
    """`CY10`: no máximo **um** seletor por segmento — antes E1 os aceitava."""
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding_renderizado(caminho_yaml=caminho)))

    assert categoria_de(erro) == "valor_invalido"


# 9-bis. Composição com CY13 — integração, não reteste das matrizes unitárias
#
# As suítes de `response_yaml_path` e `response_yaml_path_context` continuam
# sendo a autoridade unitária da gramática e do contexto. Aqui se prova apenas
# que E1 **compõe** aquelas fronteiras: delega, traduz e encadeia a causa.


def _fragmento_iterando(caminho: str, **extra: Any) -> dict[str, Any]:
    return indice(
        resposta(
            fragmentos=[
                fragmento(
                    itera_sobre="bloco_exemplo.colecao_exemplo",
                    bindings=[binding_renderizado(caminho_yaml=caminho)],
                    **extra,
                )
            ]
        )
    )


def test_absoluto_canonico_sem_itera_sobre_e_aceito() -> None:
    corpo = _com_binding(
        binding_renderizado(caminho_yaml="bloco_exemplo.campo_exemplo")
    )

    assert validar_indice(corpo) is None


def test_absoluto_canonico_com_itera_sobre_e_aceito() -> None:
    """Iterar não proíbe endereçar a raiz do YAML."""
    assert validar_indice(_fragmento_iterando("bloco_exemplo.campo_exemplo")) is None


def test_relativo_com_itera_sobre_e_aceito() -> None:
    assert validar_indice(_fragmento_iterando("@.campo_exemplo")) is None


def test_arroba_isolado_em_binding_com_itera_sobre_e_aceito() -> None:
    """`CY11`: `@` sozinho é o próprio item corrente."""
    assert validar_indice(_fragmento_iterando("@")) is None


@pytest.mark.parametrize(
    "caminho", ["@.campo_exemplo", "@", "@.colecao_exemplo[id=teste]"]
)
def test_relativo_sem_itera_sobre_e_combinacao_invalida(caminho: str) -> None:
    """A falha é de COMBINAÇÃO entre dois campos, não do valor isolado."""
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding_renderizado(caminho_yaml=caminho)))

    assert categoria_de(erro) == "combinacao_invalida"
    assert localizador_de(erro) == (
        "respostas[0].fragmentos[0].bindings[0].caminho_yaml"
    )


def test_arroba_isolado_em_itera_sobre_e_valor_invalido() -> None:
    """`CY12`: `@` é proibido no próprio `itera_sobre`."""
    corpo = fragmento(itera_sobre="@")

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=[corpo])))

    assert categoria_de(erro) == "valor_invalido"
    assert localizador_de(erro) == "respostas[0].fragmentos[0].itera_sobre"


def test_relativo_segmentado_em_itera_sobre_e_valor_invalido() -> None:
    corpo = fragmento(itera_sobre="@.colecao_exemplo")

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=[corpo])))

    assert categoria_de(erro) == "valor_invalido"
    assert localizador_de(erro) == "respostas[0].fragmentos[0].itera_sobre"


@pytest.mark.parametrize(
    "caminho",
    [
        "bloco_exemplo.",
        ".bloco_exemplo",
        "bloco_exemplo..campo_exemplo",
        "bloco_exemplo campo",
        "bloco-exemplo",
        "bloco_exemplo.@campo",
        "@@",
        "@campo_exemplo",
        "colecao_exemplo[id=]",
        "colecao_exemplo[=teste]",
        "colecao_exemplo[id]",
        "colecao_exemplo[id=teste",
        "café",
        "bloco_exemplo.123",
        "123",
        "colecao_exemplo[123=teste]",
    ],
)
def test_gramatica_malformada_em_caminho_yaml_e_valor_invalido(
    caminho: str,
) -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding_renderizado(caminho_yaml=caminho)))

    assert categoria_de(erro) == "valor_invalido"


@pytest.mark.parametrize(
    "caminho", ["bloco_exemplo.", "bloco_exemplo 2", "bloco_exemplo.123", "@@"]
)
def test_gramatica_malformada_em_itera_sobre_e_valor_invalido(
    caminho: str,
) -> None:
    corpo = fragmento(itera_sobre=caminho)

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=[corpo])))

    assert categoria_de(erro) == "valor_invalido"
    assert localizador_de(erro) == "respostas[0].fragmentos[0].itera_sobre"


def test_literal_seletor_numerico_e_aceito() -> None:
    """`CY7`: o literal do seletor é sempre semanticamente uma `str`."""
    corpo = _com_binding(
        binding_renderizado(caminho_yaml="colecao_exemplo[id=2026]")
    )

    assert validar_indice(corpo) is None


def test_chave_exclusivamente_numerica_e_valor_invalido() -> None:
    """`CY9`: não endereçável — e E1 NÃO a classifica como 'posição'."""
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(
            _com_binding(binding_renderizado(caminho_yaml="bloco_exemplo.123"))
        )

    assert categoria_de(erro) == "valor_invalido"


@pytest.mark.parametrize(
    "caminho", ["bloco exemplo", " bloco_exemplo", "bloco_exemplo ", "bloco\texemplo"]
)
def test_canonicidade_de_whitespace_e_valor_invalido(caminho: str) -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding_renderizado(caminho_yaml=caminho)))

    assert categoria_de(erro) == "valor_invalido"


def test_subclasse_de_str_em_caminho_yaml_e_tipo_invalido() -> None:
    """Tipo EXATO: a subclasse é recusada localmente, antes da delegação."""

    class Caminho(str):
        pass

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(
            _com_binding(
                binding_renderizado(
                    caminho_yaml=Caminho("bloco_exemplo.campo_exemplo")
                )
            )
        )

    assert categoria_de(erro) == "tipo_invalido"
    assert localizador_de(erro) == (
        "respostas[0].fragmentos[0].bindings[0].caminho_yaml"
    )


def test_subclasse_de_str_em_itera_sobre_e_tipo_invalido() -> None:
    class Caminho(str):
        pass

    corpo = fragmento(itera_sobre=Caminho("bloco_exemplo.colecao_exemplo"))

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=[corpo])))

    assert categoria_de(erro) == "tipo_invalido"
    assert localizador_de(erro) == "respostas[0].fragmentos[0].itera_sobre"


def test_itera_sobre_invalido_vence_binding_invalido() -> None:
    """Precedência: o fragmento é julgado antes dos seus *bindings*."""
    corpo = fragmento(
        itera_sobre="@",
        bindings=[binding_renderizado(caminho_yaml="bloco_exemplo.")],
    )

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=[corpo])))

    assert localizador_de(erro) == "respostas[0].fragmentos[0].itera_sobre"


def test_origem_invalida_vence_caminho_invalido() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(
            _com_binding(
                binding_renderizado(origem="INVENTADA", caminho_yaml="bloco.")
            )
        )

    assert categoria_de(erro) == "valor_invalido"
    assert localizador_de(erro) == (
        "respostas[0].fragmentos[0].bindings[0].origem"
    )


def test_caminho_invalido_vence_formato_invalido() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(
            _com_binding(
                binding_renderizado(
                    caminho_yaml="bloco_exemplo.", formato="inventado"
                )
            )
        )

    assert localizador_de(erro) == (
        "respostas[0].fragmentos[0].bindings[0].caminho_yaml"
    )


def test_caminho_invalido_vence_predicado_invalido() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(
            _com_binding(
                binding_assertiva(
                    caminho_yaml="bloco_exemplo.", predicado="INVENTADO"
                )
            )
        )

    assert localizador_de(erro) == (
        "respostas[0].fragmentos[0].bindings[0].caminho_yaml"
    )


@pytest.mark.parametrize(
    "caminho", ["segredo_sintetico_no_caminho.", "@.segredo_sintetico_relativo"]
)
def test_mensagem_nao_ecoa_o_caminho_recebido(caminho: str) -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding_renderizado(caminho_yaml=caminho)))

    mensagem = str(erro.value)
    assert "segredo_sintetico" not in mensagem
    assert mensagem.count(": ") == 1


def test_causa_da_falha_gramatical_e_a_excecao_do_parser() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(
            _com_binding(binding_renderizado(caminho_yaml="bloco_exemplo."))
        )

    assert isinstance(erro.value.__cause__, CaminhoYamlInvalido)


def test_causa_da_falha_contextual_de_binding_e_a_excecao_de_contexto() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(
            _com_binding(binding_renderizado(caminho_yaml="@.campo_exemplo"))
        )

    assert isinstance(erro.value.__cause__, CaminhoYamlContextoInvalido)


def test_causa_da_falha_contextual_de_itera_sobre_e_a_excecao_de_contexto() -> None:
    corpo = fragmento(itera_sobre="@")

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=[corpo])))

    assert isinstance(erro.value.__cause__, CaminhoYamlContextoInvalido)


def test_causa_da_falha_gramatical_de_itera_sobre_e_a_excecao_do_parser() -> None:
    corpo = fragmento(itera_sobre="bloco_exemplo.")

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=[corpo])))

    assert isinstance(erro.value.__cause__, CaminhoYamlInvalido)


def test_excecoes_de_cy13_nao_atravessam_a_fronteira_publica() -> None:
    """A API pública de E1 continua levantando somente `IndiceInvalido`."""
    for corpo in (
        _com_binding(binding_renderizado(caminho_yaml="bloco_exemplo.")),
        _com_binding(binding_renderizado(caminho_yaml="@.campo_exemplo")),
        indice(resposta(fragmentos=[fragmento(itera_sobre="@")])),
    ):
        with pytest.raises(IndiceInvalido) as erro:
            validar_indice(corpo)

        assert not isinstance(erro.value, CaminhoYamlInvalido)
        assert not isinstance(erro.value, CaminhoYamlContextoInvalido)


def test_runtime_autoritativo_nao_delega_caminho() -> None:
    """Sem `caminho_yaml` não há delegação: `RUNTIME_AUTORITATIVO` é intocado."""
    corpo = _com_binding(binding_runtime())

    assert validar_indice(corpo) is None


# 10. Contrato de erro


def test_erro_e_indice_invalido() -> None:
    with pytest.raises(IndiceInvalido):
        validar_indice(None)


def test_indice_invalido_deriva_de_exception() -> None:
    assert issubclass(IndiceInvalido, Exception)


def test_mensagem_tem_categoria_e_localizador() -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=[fragmento(status="PARCIAL")])))

    mensagem = str(erro.value)
    categoria, _, localizador = mensagem.partition(":")

    assert categoria == "valor_invalido"
    assert localizador.strip() == "respostas[0].fragmentos[0].status"


def test_mensagem_nao_ecoa_o_valor_invalido() -> None:
    """A mensagem diz o que e onde, nunca o quê — o índice não vaza conteúdo."""
    segredo = "VALOR-QUE-NAO-PODE-VAZAR"
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=[fragmento(status=segredo)])))

    assert segredo not in str(erro.value)


def test_mensagem_nao_ecoa_caminho_de_valor_invalido() -> None:
    segredo = "caminho.que.nao.pode.vazar"
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(
            _com_binding(
                binding_renderizado(formato="inexistente", caminho_yaml=segredo)
            )
        )

    assert segredo not in str(erro.value)


def test_para_na_primeira_violacao() -> None:
    """Duas respostas inválidas: a mensagem aponta a primeira, não agrega."""
    corpo = indice(resposta(id="RXX"), resposta(id="RYY"))

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(corpo)

    assert localizador_de(erro) == "respostas[0].id"


# 11. Guardas de produção


def test_all_exato() -> None:
    from casa77_sdr import response_index

    assert response_index.__all__ == ["IndiceInvalido", "validar_indice"]


def test_init_nao_referencia_o_modulo() -> None:
    """E1 não é exportada pelo pacote: nada consome o validador ainda."""
    assert "response_index" not in MODULO_INIT.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "proibido",
    [
        "yaml",
        "pathlib",
        "knowledge",
        "interpretation",
        "state_machine",
        "qualification",
        "rules",
        "persistence",
        "identity",
        "context",
        "eligibility",
    ],
)
def test_modulo_nao_importa(proibido: str) -> None:
    arvore = ast.parse(MODULO.read_text(encoding="utf-8"))
    importados: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            importados.update(alias.name.split(".")[0] for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            importados.add(no.module.split(".")[0])
            importados.update(alias.name for alias in no.names)

    assert proibido not in importados


def _importados_do_modulo() -> set[str]:
    """Módulos e nomes importados por `response_index.py`, pela AST."""
    arvore = ast.parse(MODULO.read_text(encoding="utf-8"))
    importados: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            importados.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            importados.add(no.module)
            importados.update(alias.name for alias in no.names)
    return importados


def _identificadores_do_modulo() -> set[str]:
    """Nomes REALMENTE usados em código — docstring não é vocabulário."""
    arvore = ast.parse(MODULO.read_text(encoding="utf-8"))
    return {
        no.id for no in ast.walk(arvore) if isinstance(no, ast.Name)
    } | {
        no.attr for no in ast.walk(arvore) if isinstance(no, ast.Attribute)
    }


def test_modulo_importa_as_duas_fronteiras_contextuais() -> None:
    """E1 compõe `CY13` linha 2 — a única porta autorizada."""
    importados = _importados_do_modulo()

    assert "casa77_sdr.response_yaml_path_context" in importados
    assert "validar_caminho_de_binding" in importados
    assert "validar_itera_sobre" in importados


def test_modulo_importa_as_excecoes_necessarias_para_traduzir() -> None:
    importados = _importados_do_modulo()

    assert "CaminhoYamlContextoInvalido" in importados
    assert "CaminhoYamlInvalido" in importados
    assert "casa77_sdr.response_yaml_path" in importados


def test_modulo_nao_importa_nem_chama_o_parser_diretamente() -> None:
    """Uma única autoridade gramatical: E1 fala com a linha 2, não com a 1."""
    assert "analisar_caminho_yaml" not in _importados_do_modulo()
    assert "analisar_caminho_yaml" not in _identificadores_do_modulo()


def test_modulo_nao_importa_o_resolver_factual() -> None:
    """`CY13` linha 3 fica fora: E1 prova forma e contexto, nunca resolução."""
    importados = _importados_do_modulo()

    assert "casa77_sdr.response_yaml_resolve" not in importados
    assert "resolver_caminho" not in importados
    assert "resolver_itera_sobre" not in importados

    identificadores = _identificadores_do_modulo()
    assert "resolver_caminho" not in identificadores
    assert "resolver_itera_sobre" not in identificadores


@pytest.mark.parametrize(
    "legado",
    [
        "_tem_selecao_posicional",
        "_seletores",
        "_segmento_numerico",
        "_SELECAO_POSICIONAL",
    ],
)
def test_logica_legada_de_caminho_foi_removida(legado: str) -> None:
    """Zero segunda autoridade gramatical dentro de E1."""
    arvore = ast.parse(MODULO.read_text(encoding="utf-8"))
    definidos = {
        no.name
        for no in ast.walk(arvore)
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef))
    } | {
        alvo.id
        for no in ast.walk(arvore)
        if isinstance(no, ast.Assign)
        for alvo in no.targets
        if isinstance(alvo, ast.Name)
    }

    assert legado not in definidos
    assert legado not in _identificadores_do_modulo()


def test_captura_de_excecao_e_estreita() -> None:
    """Só as exceções nominais das fronteiras compostas são interceptadas.

    São as duas de `CY13` e a de `PH` — nada além delas, e nunca `except` nu.
    """
    arvore = ast.parse(MODULO.read_text(encoding="utf-8"))
    capturados: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.ExceptHandler):
            assert no.type is not None, "except nu é proibido"
            assert isinstance(no.type, ast.Name)
            capturados.add(no.type.id)

    assert capturados == {
        "_CaminhoYamlInvalido",
        "_CaminhoYamlContextoInvalido",
        "_PlaceholderInvalido",
    }


def test_toda_traducao_encadeia_a_causa() -> None:
    """`raise ... from exc` em todo `raise` dentro de `except`."""
    arvore = ast.parse(MODULO.read_text(encoding="utf-8"))
    for no in ast.walk(arvore):
        if isinstance(no, ast.ExceptHandler):
            lancamentos = [
                interno
                for interno in ast.walk(no)
                if isinstance(interno, ast.Raise)
            ]
            assert lancamentos
            for lancamento in lancamentos:
                assert lancamento.cause is not None


def test_assinatura_publica_permanece_intacta() -> None:
    """Nenhum parâmetro novo foi acrescentado à fronteira pública."""
    import inspect

    from casa77_sdr.response_index import validar_indice as publica

    assert list(inspect.signature(publica).parameters) == ["indice"]


def test_modulo_nao_abre_arquivo() -> None:
    arvore = ast.parse(MODULO.read_text(encoding="utf-8"))
    chamadas = {
        no.func.id
        for no in ast.walk(arvore)
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Name)
    }

    assert "open" not in chamadas


@pytest.mark.parametrize(
    "responsabilidade",
    [
        "S2-D8",
        "E09",
        "pendencia_impeditiva",
        "resposta_aprovada_disponivel",
        "handoff",
        "DetectorHandoff",
    ],
)
def test_modulo_nao_assume_responsabilidade_alheia(
    responsabilidade: str,
) -> None:
    """C-12: E1 valida consistência estrutural e não decide ciclo."""
    codigo = MODULO.read_text(encoding="utf-8")
    identificadores = {
        no.id
        for no in ast.walk(ast.parse(codigo))
        if isinstance(no, ast.Name)
    } | {
        no.attr
        for no in ast.walk(ast.parse(codigo))
        if isinstance(no, ast.Attribute)
    }

    assert responsabilidade not in identificadores


def test_producao_nao_tem_constante_comercial() -> None:
    """Mesmo invariante do carregador: nenhum número do YAML vive no código."""
    reais = yaml.safe_load(YAML_REAL.read_text(encoding="utf-8"))
    comerciais = {
        reais["capacidade"]["convidados_sentados"],
        reais["capacidade"]["formato_coquetel"],
    }
    for pacote in reais["precos"]["pacotes"]:
        comerciais.update(
            valor
            for valor in pacote.values()
            if isinstance(valor, int) and not isinstance(valor, bool)
        )

    arvore = ast.parse(MODULO.read_text(encoding="utf-8"))
    literais = {
        no.value
        for no in ast.walk(arvore)
        if isinstance(no, ast.Constant)
        and isinstance(no.value, int)
        and not isinstance(no.value, bool)
    }

    assert not (literais & comerciais)


def test_validacao_nao_altera_a_estrutura_recebida() -> None:
    corpo = indice(
        resposta(fragmentos=[fragmento(bindings=[binding_renderizado()])])
    )
    copia = yaml.safe_load(yaml.safe_dump(corpo))

    assert validar_indice(corpo) is None
    assert corpo == copia


# ---------------------------------------------------------------------------
# Composição E1 → PH
#
# Estes testes provam a INTEGRAÇÃO, não a gramática: a bateria completa de
# `PH4` vive em `tests/test_response_placeholder.py`, sua única autoridade.


def test_renderizado_canonico_continua_valido() -> None:
    """O par nome/*placeholder* canônico atravessa a composição."""
    corpo = _com_binding(
        binding_renderizado(
            nome="quantidade_exemplo", placeholder="{{quantidade_exemplo}}"
        )
    )

    assert validar_indice(corpo) is None


@pytest.mark.parametrize(
    "nome",
    ["A", "_a", "a_", "a__b", "1a", "a-b", "a.b", "a b", "á", "a٣"],
)
def test_nome_renderizado_fora_de_ph4(nome: str) -> None:
    """`PH4` passa a valer em E1 para `RENDERIZADO`, por delegação."""
    binding = binding_renderizado(nome=nome, placeholder="{{" + nome + "}}")

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding))

    assert categoria_de(erro) == "valor_invalido"
    assert localizador_de(erro).endswith(".nome")


def test_nome_renderizado_subclasse_de_str() -> None:
    """Tipo exato antes da delegação: a subclasse não entra na fronteira `PH`."""

    class _StrDerivada(str):
        pass

    nome = _StrDerivada("quantidade_exemplo")
    binding = binding_renderizado(
        nome=nome, placeholder="{{quantidade_exemplo}}"
    )

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding))

    assert categoria_de(erro) == "tipo_invalido"
    assert localizador_de(erro).endswith(".nome")


def test_placeholder_de_outro_nome() -> None:
    """`PH3b`: o campo explícito precisa derivar do nome deste *binding*."""
    binding = binding_renderizado(
        nome="quantidade_exemplo", placeholder="{{outro_nome}}"
    )

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding))

    assert categoria_de(erro) == "valor_invalido"
    assert localizador_de(erro).endswith(".placeholder")


@pytest.mark.parametrize(
    "placeholder",
    [
        "{quantidade_exemplo}",
        "{{ quantidade_exemplo }}",
        "{{quantidade_exemplo}",
        "quantidade_exemplo",
        "{{QUANTIDADE_EXEMPLO}}",
        "{{quantidade_exemplo}}}",
        " {{quantidade_exemplo}}",
        "{{quantidade_exemplo}} ",
    ],
)
def test_placeholder_em_forma_nao_canonica(placeholder: str) -> None:
    """E1 não sabe *por que* não é canônico: sabe que difere do derivado."""
    binding = binding_renderizado(placeholder=placeholder)

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding))

    assert categoria_de(erro) == "valor_invalido"
    assert localizador_de(erro).endswith(".placeholder")


def test_assertiva_com_nome_fora_de_ph4_continua_valida() -> None:
    """`PH4` alcança somente `RENDERIZADO`; `C-5` permanece inalterada."""
    corpo = _com_binding(binding_assertiva(nome="Condicao-Livre"))

    assert validar_indice(corpo) is None


@pytest.mark.parametrize("nome", ["Condicao-Livre", "A", "_a", "a__b", "1a"])
def test_assertiva_nao_e_julgada_por_ph4(nome: str) -> None:
    assert validar_indice(_com_binding(binding_assertiva(nome=nome))) is None


def test_excecao_de_ph_nao_atravessa_a_api_publica() -> None:
    """`PlaceholderInvalido` é traduzida, e a causa técnica é encadeada."""
    binding = binding_renderizado(nome="Nome-Invalido", placeholder="{{x}}")

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding))

    assert not isinstance(erro.value, PlaceholderInvalido)
    assert isinstance(erro.value.__cause__, PlaceholderInvalido)


def test_modulo_importa_a_fronteira_de_placeholder() -> None:
    """E1 compõe `PH` — a única autoridade da gramática de nome e forma."""
    importados = _importados_do_modulo()

    assert "casa77_sdr.response_placeholder" in importados
    assert "derivar_placeholder" in importados
    assert "PlaceholderInvalido" in importados


def test_modulo_nao_chama_o_decompositor_de_template() -> None:
    """E1 não possui *template*, e não finge possuir."""
    assert "decompor_template" not in _importados_do_modulo()
    assert "decompor_template" not in _identificadores_do_modulo()


def test_nome_renderizado_nao_executa_hash_de_subclasse() -> None:
    """O gate de tipo exato precede a unicidade, que usa `set`.

    Se a recusa dependesse de `nome in nomes_vistos`, o `__hash__` redefinido
    executaria antes — e a entrada controlaria o fluxo de E1.
    """

    class _NomeComHashExplosivo(str):
        def __hash__(self) -> int:
            raise AssertionError("nao_deveria_executar")

    binding = binding_renderizado(
        nome=_NomeComHashExplosivo("quantidade_exemplo"),
        placeholder="{{quantidade_exemplo}}",
    )

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding))

    assert categoria_de(erro) == "tipo_invalido"
    assert localizador_de(erro).endswith(".nome")


def test_placeholder_nao_controla_a_propria_comparacao() -> None:
    """A comparação usa a semântica base de `str`, não o operador do objeto.

    A subclasse tenta afirmar que `{{outro_nome}}` é igual ao canônico, e
    explodir se for comparada por desigualdade. Nenhuma das duas coisas pode
    influenciar E1.
    """

    class _PlaceholderMentiroso(str):
        def __eq__(self, outro: object) -> bool:
            return True

        def __ne__(self, outro: object) -> bool:
            raise AssertionError("nao_deveria_executar")

        def __hash__(self) -> int:
            return 0

    binding = binding_renderizado(
        nome="quantidade_exemplo",
        placeholder=_PlaceholderMentiroso("{{outro_nome}}"),
    )

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding))

    assert categoria_de(erro) == "valor_invalido"
    assert localizador_de(erro).endswith(".placeholder")


def test_nome_renderizado_nao_executa_len_de_subclasse() -> None:
    """O teste de vazio usa `str.__len__`, não o `__len__` do objeto.

    O conteúdo é válido e não vazio: a recusa vem do gate de tipo exato de
    `RENDERIZADO`, e o `__len__` redefinido nunca chega a executar.
    """

    class _NomeComLenExplosivo(str):
        def __len__(self) -> int:
            raise AssertionError("nao_deveria_executar")

    binding = binding_renderizado(
        nome=_NomeComLenExplosivo("quantidade_exemplo"),
        placeholder="{{quantidade_exemplo}}",
    )

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding))

    assert categoria_de(erro) == "tipo_invalido"
    assert localizador_de(erro).endswith(".nome")


def test_placeholder_nao_executa_len_de_subclasse() -> None:
    """O teste de vazio do *placeholder* também usa a semântica base.

    O conteúdo é não vazio e não canônico: a recusa vem da comparação literal,
    e o `__len__` redefinido nunca chega a executar.
    """

    class _PlaceholderComLenExplosivo(str):
        def __len__(self) -> int:
            raise AssertionError("nao_deveria_executar")

    binding = binding_renderizado(
        nome="quantidade_exemplo",
        placeholder=_PlaceholderComLenExplosivo("{{outro_nome}}"),
    )

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding))

    assert categoria_de(erro) == "valor_invalido"
    assert localizador_de(erro).endswith(".placeholder")

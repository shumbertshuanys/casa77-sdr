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


# 9. Seleção posicional


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
def test_selecao_posicional_em_caminho_yaml(caminho: str) -> None:
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding_renderizado(caminho_yaml=caminho)))

    assert categoria_de(erro) == "selecao_posicional"


@pytest.mark.parametrize(
    "caminho",
    ["colecao_exemplo.0.campo_exemplo", "colecao_exemplo[0].campo_exemplo"],
)
def test_selecao_posicional_em_itera_sobre(caminho: str) -> None:
    corpo = fragmento(itera_sobre=caminho)

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=[corpo])))

    assert categoria_de(erro) == "selecao_posicional"
    assert localizador_de(erro) == "respostas[0].fragmentos[0].itera_sobre"


@pytest.mark.parametrize(
    "caminho",
    [
        "colecao_exemplo[id=teste].campo_exemplo",
        "colecao_exemplo[codigo=teste].campo_exemplo",
        "bloco_exemplo.colecao_exemplo[id=item_exemplo].quantidade_exemplo",
        "bloco_exemplo.campo_exemplo",
    ],
)
def test_seletor_textual_nao_e_posicional(caminho: str) -> None:
    """E1 não julga a gramática do seletor; só recusa a forma numérica."""
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
def test_selecao_posicional_apos_seletor_textual(caminho: str) -> None:
    """O índice numérico é recusado em qualquer seletor, não só no primeiro."""
    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(_com_binding(binding_renderizado(caminho_yaml=caminho)))

    assert categoria_de(erro) == "selecao_posicional"


@pytest.mark.parametrize(
    "caminho",
    [
        "colecao_exemplo[id=teste][0]",
        "colecao_exemplo[codigo=teste][12].subcolecao_exemplo",
        "colecao_exemplo[id=teste].subcolecao_exemplo[0]",
    ],
)
def test_selecao_posicional_apos_seletor_textual_em_itera_sobre(
    caminho: str,
) -> None:
    corpo = fragmento(itera_sobre=caminho)

    with pytest.raises(IndiceInvalido) as erro:
        validar_indice(indice(resposta(fragmentos=[corpo])))

    assert categoria_de(erro) == "selecao_posicional"
    assert localizador_de(erro) == "respostas[0].fragmentos[0].itera_sobre"


@pytest.mark.parametrize(
    "caminho",
    [
        "colecao_exemplo[id=teste][codigo=outro].campo_exemplo",
        "colecao_exemplo[id=teste][codigo=outro]",
        "bloco_exemplo.colecao_exemplo[id=teste][codigo=outro].campo_exemplo",
    ],
)
def test_seletores_textuais_encadeados_nao_sao_posicionais(caminho: str) -> None:
    """Encadear seletores textuais não vira posicional: E1 não fecha gramática."""
    corpo = _com_binding(binding_renderizado(caminho_yaml=caminho))

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


def test_indice_real_continua_inexistente() -> None:
    """E1 valida a forma do índice futuro; ela não o cria."""
    assert not (RAIZ / "knowledge" / "indice-respostas-aprovadas.yaml").exists()


def test_validacao_nao_altera_a_estrutura_recebida() -> None:
    corpo = indice(
        resposta(fragmentos=[fragmento(bindings=[binding_renderizado()])])
    )
    copia = yaml.safe_load(yaml.safe_dump(corpo))

    assert validar_indice(corpo) is None
    assert corpo == copia

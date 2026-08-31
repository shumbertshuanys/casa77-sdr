"""Validação estrutural pura do futuro índice de respostas aprovadas.

Este módulo valida a **forma** de uma estrutura já parseada que pretende ser
`knowledge/indice-respostas-aprovadas.yaml` (C-1). Ele **não cria** esse arquivo,
**não o lê** e **não lê a base comercial**: não abre arquivo, não conhece caminho
e não importa carregador algum. A entrada é uma estrutura Python já em memória.

O que ele confere é o esqueleto fechado de C-2 — `Rxx` → fragmentos emitíveis →
*bindings* —, o vocabulário fechado de status (C-3), a forma de `RENDERIZADO`
(C-4) e de `ASSERTIVA` (C-5), os formatos de C-6, a origem explícita do referente
(C-A2-RT) e o vocabulário de fato runtime (C-A2-V).

Fora do escopo, deliberadamente: a existência real de qualquer caminho YAML, a
gramática completa de caminhos, a bijeção com o Markdown, a equivalência textual
de C-15, a avaliação de qualquer `ASSERTIVA`, a aplicação de qualquer formato e a
migração da autoridade de status (C-A1-ST6–ST10). Nada aqui decide candidatura,
`E09`, handoff ou condição de ciclo — C-12 permanece literal e inalterada.

Falha é **fail-closed** e imediata: a primeira violação levanta `IndiceInvalido`.
A mensagem carrega categoria e localizador estrutural, nunca o valor recebido —
o índice não é fonte de fato comercial (C-1h–C-1m, C-15e), e a mensagem de erro
tampouco.
"""

from __future__ import annotations

from typing import Any

__all__ = ["IndiceInvalido", "validar_indice"]


class IndiceInvalido(Exception):
    """Violação estrutural do índice.

    A mensagem tem a forma `<categoria>: <localizador>`. O valor recebido nunca
    é reproduzido: a categoria diz o que está errado e o localizador diz onde.
    """


# Categorias fechadas.
_TIPO_INVALIDO = "tipo_invalido"
_CAMPO_AUSENTE = "campo_ausente"
_CAMPO_DESCONHECIDO = "campo_desconhecido"
_VALOR_INVALIDO = "valor_invalido"
_DUPLICIDADE = "duplicidade"
_COMBINACAO_INVALIDA = "combinacao_invalida"
_SELECAO_POSICIONAL = "selecao_posicional"

# Vocabulários fechados.
_STATUS = frozenset({"APROVADO", "AGUARDA_APROVACAO", "BLOQUEADO"})
_MECANISMOS = frozenset({"RENDERIZADO", "ASSERTIVA"})
_ORIGENS = frozenset({"YAML", "RUNTIME_AUTORITATIVO"})
_FATOS_RUNTIME = frozenset({"consulta_calendario_valida", "data_disponivel"})
_FORMATOS = frozenset(
    {"inteiro", "inteiro_agrupado", "simbolo_moeda", "hora", "texto", "lista"}
)
_PREDICADOS = frozenset({"EH_VERDADEIRO", "EH_FALSO"})

# Conjuntos de chaves permitidas por nível. Schema fechado: nada além disto.
_CHAVES_RAIZ = frozenset({"respostas"})
_CHAVES_RESPOSTA = frozenset({"id", "fragmentos"})
_CHAVES_FRAGMENTO_OBRIGATORIAS = frozenset({"id", "status", "bindings"})
_CHAVES_FRAGMENTO = _CHAVES_FRAGMENTO_OBRIGATORIAS | frozenset({"itera_sobre"})
_CHAVES_BINDING_OBRIGATORIAS = frozenset({"nome", "mecanismo", "origem"})
_CHAVES_BINDING = _CHAVES_BINDING_OBRIGATORIAS | frozenset(
    {"caminho_yaml", "fato_runtime", "placeholder", "formato", "predicado"}
)


def validar_indice(indice: object) -> None:
    """Valida a forma de `indice`, já parseado, e devolve `None` se ela for válida.

    A estrutura recebida não é lida por caminho, não é copiada e não é alterada.
    Levanta `IndiceInvalido` na primeira violação encontrada.
    """
    _exigir_mapeamento(indice, "<raiz>")
    _exigir_chaves(indice, _CHAVES_RAIZ, frozenset({"respostas"}), "<raiz>")

    respostas = indice["respostas"]
    if not isinstance(respostas, list):
        raise _erro(_TIPO_INVALIDO, "respostas")

    ids_de_resposta: set[str] = set()
    for indice_resposta, resposta in enumerate(respostas):
        _validar_resposta(resposta, indice_resposta, ids_de_resposta)


def _validar_resposta(
    resposta: Any, posicao: int, ids_vistos: set[str]
) -> None:
    onde = f"respostas[{posicao}]"
    _exigir_mapeamento(resposta, onde)
    _exigir_chaves(resposta, _CHAVES_RESPOSTA, _CHAVES_RESPOSTA, onde)

    identificador = resposta["id"]
    if not isinstance(identificador, str):
        raise _erro(_TIPO_INVALIDO, f"{onde}.id")
    if not _e_id_de_resposta(identificador):
        raise _erro(_VALOR_INVALIDO, f"{onde}.id")
    if identificador in ids_vistos:
        raise _erro(_DUPLICIDADE, f"{onde}.id")
    ids_vistos.add(identificador)

    fragmentos = resposta["fragmentos"]
    if not isinstance(fragmentos, list):
        raise _erro(_TIPO_INVALIDO, f"{onde}.fragmentos")
    # C-2c: um `Rxx` tem um ou mais fragmentos.
    if not fragmentos:
        raise _erro(_VALOR_INVALIDO, f"{onde}.fragmentos")

    # C-A1-B1: a unidade é o fragmento, e o id só precisa ser único dentro
    # do próprio `Rxx` (C-2h).
    ids_de_fragmento: set[str] = set()
    for posicao_fragmento, fragmento in enumerate(fragmentos):
        _validar_fragmento(
            fragmento,
            f"{onde}.fragmentos[{posicao_fragmento}]",
            ids_de_fragmento,
        )


def _validar_fragmento(
    fragmento: Any, onde: str, ids_vistos: set[str]
) -> None:
    _exigir_mapeamento(fragmento, onde)
    _exigir_chaves(
        fragmento, _CHAVES_FRAGMENTO, _CHAVES_FRAGMENTO_OBRIGATORIAS, onde
    )

    identificador = fragmento["id"]
    if not isinstance(identificador, str):
        raise _erro(_TIPO_INVALIDO, f"{onde}.id")
    if not identificador:
        raise _erro(_VALOR_INVALIDO, f"{onde}.id")
    if identificador in ids_vistos:
        raise _erro(_DUPLICIDADE, f"{onde}.id")
    ids_vistos.add(identificador)

    # C-3: vocabulário fechado, sem valor padrão e sem `PARCIAL`.
    status = fragmento["status"]
    if not isinstance(status, str):
        raise _erro(_TIPO_INVALIDO, f"{onde}.status")
    if status not in _STATUS:
        raise _erro(_VALOR_INVALIDO, f"{onde}.status")

    if "itera_sobre" in fragmento:
        itera_sobre = fragmento["itera_sobre"]
        if not isinstance(itera_sobre, str):
            raise _erro(_TIPO_INVALIDO, f"{onde}.itera_sobre")
        if not itera_sobre:
            raise _erro(_VALOR_INVALIDO, f"{onde}.itera_sobre")
        if _tem_selecao_posicional(itera_sobre):
            raise _erro(_SELECAO_POSICIONAL, f"{onde}.itera_sobre")

    # C-2k: a lista existe sempre, inclusive vazia; ausência é erro de contrato.
    bindings = fragmento["bindings"]
    if not isinstance(bindings, list):
        raise _erro(_TIPO_INVALIDO, f"{onde}.bindings")

    nomes_vistos: set[str] = set()
    for posicao, binding in enumerate(bindings):
        _validar_binding(binding, f"{onde}.bindings[{posicao}]", nomes_vistos)


def _validar_binding(binding: Any, onde: str, nomes_vistos: set[str]) -> None:
    _exigir_mapeamento(binding, onde)
    _exigir_chaves(
        binding, _CHAVES_BINDING, _CHAVES_BINDING_OBRIGATORIAS, onde
    )

    nome = binding["nome"]
    if not isinstance(nome, str):
        raise _erro(_TIPO_INVALIDO, f"{onde}.nome")
    if not nome:
        raise _erro(_VALOR_INVALIDO, f"{onde}.nome")
    # C-4a / C-5a: nome único no fragmento.
    if nome in nomes_vistos:
        raise _erro(_DUPLICIDADE, f"{onde}.nome")
    nomes_vistos.add(nome)

    mecanismo = binding["mecanismo"]
    if not isinstance(mecanismo, str):
        raise _erro(_TIPO_INVALIDO, f"{onde}.mecanismo")
    if mecanismo not in _MECANISMOS:
        raise _erro(_VALOR_INVALIDO, f"{onde}.mecanismo")

    # C-A2-RT3 / C-A2-RT4: `origem` é obrigatória e nunca é presumida `YAML`.
    origem = binding["origem"]
    if not isinstance(origem, str):
        raise _erro(_TIPO_INVALIDO, f"{onde}.origem")
    if origem not in _ORIGENS:
        raise _erro(_VALOR_INVALIDO, f"{onde}.origem")

    _validar_referente(binding, onde, origem, mecanismo)
    _validar_mecanismo(binding, onde, mecanismo)


def _validar_referente(
    binding: dict[str, Any], onde: str, origem: str, mecanismo: str
) -> None:
    """C-A2-RT5, RT6 e RT7: exatamente um referente, coerente com a origem."""
    if origem == "YAML":
        if "fato_runtime" in binding:
            raise _erro(_COMBINACAO_INVALIDA, f"{onde}.fato_runtime")
        if "caminho_yaml" not in binding:
            raise _erro(_CAMPO_AUSENTE, f"{onde}.caminho_yaml")

        caminho = binding["caminho_yaml"]
        if not isinstance(caminho, str):
            raise _erro(_TIPO_INVALIDO, f"{onde}.caminho_yaml")
        if not caminho:
            raise _erro(_VALOR_INVALIDO, f"{onde}.caminho_yaml")
        if _tem_selecao_posicional(caminho):
            raise _erro(_SELECAO_POSICIONAL, f"{onde}.caminho_yaml")
        return

    # C-A2-V3 / C-A2-V4: fato runtime só sustenta `ASSERTIVA`.
    if mecanismo != "ASSERTIVA":
        raise _erro(_COMBINACAO_INVALIDA, f"{onde}.mecanismo")
    if "caminho_yaml" in binding:
        raise _erro(_COMBINACAO_INVALIDA, f"{onde}.caminho_yaml")
    if "fato_runtime" not in binding:
        raise _erro(_CAMPO_AUSENTE, f"{onde}.fato_runtime")

    fato = binding["fato_runtime"]
    if not isinstance(fato, str):
        raise _erro(_TIPO_INVALIDO, f"{onde}.fato_runtime")
    if fato not in _FATOS_RUNTIME:
        raise _erro(_VALOR_INVALIDO, f"{onde}.fato_runtime")


def _validar_mecanismo(
    binding: dict[str, Any], onde: str, mecanismo: str
) -> None:
    if mecanismo == "RENDERIZADO":
        # C-4c e C-4d: *placeholder* e formato fechado são obrigatórios.
        if "predicado" in binding:
            raise _erro(_COMBINACAO_INVALIDA, f"{onde}.predicado")
        if "placeholder" not in binding:
            raise _erro(_CAMPO_AUSENTE, f"{onde}.placeholder")
        if "formato" not in binding:
            raise _erro(_CAMPO_AUSENTE, f"{onde}.formato")

        placeholder = binding["placeholder"]
        if not isinstance(placeholder, str):
            raise _erro(_TIPO_INVALIDO, f"{onde}.placeholder")
        if not placeholder:
            raise _erro(_VALOR_INVALIDO, f"{onde}.placeholder")

        formato = binding["formato"]
        if not isinstance(formato, str):
            raise _erro(_TIPO_INVALIDO, f"{onde}.formato")
        if formato not in _FORMATOS:
            raise _erro(_VALOR_INVALIDO, f"{onde}.formato")
        return

    # C-5d, C-5e e C-5c: `ASSERTIVA` não tem *placeholder* nem formato, e o
    # predicado é obrigatório.
    if "placeholder" in binding:
        raise _erro(_COMBINACAO_INVALIDA, f"{onde}.placeholder")
    if "formato" in binding:
        raise _erro(_COMBINACAO_INVALIDA, f"{onde}.formato")
    if "predicado" not in binding:
        raise _erro(_CAMPO_AUSENTE, f"{onde}.predicado")

    predicado = binding["predicado"]
    if not isinstance(predicado, str):
        raise _erro(_TIPO_INVALIDO, f"{onde}.predicado")
    if predicado not in _PREDICADOS:
        raise _erro(_VALOR_INVALIDO, f"{onde}.predicado")


def _e_id_de_resposta(identificador: str) -> bool:
    """`Rxx` — padrão fechado de C-2b, sem impor faixa numérica."""
    prefixo, digitos = identificador[:1], identificador[1:]
    return (
        prefixo == "R"
        and len(digitos) == 2
        and digitos.isdigit()
        and digitos.isascii()
    )


def _tem_selecao_posicional(caminho: str) -> bool:
    """Detecta seleção por posição, proibida por C-A1-S1 dentro e fora de iteração.

    Reconhece as duas formas numéricas: o segmento inteiro entre pontos e o
    índice entre colchetes — este em **qualquer** seletor do segmento, não só no
    primeiro, de modo que `colecao[id=teste][0]` é tão posicional quanto
    `colecao[0]`. Um seletor textual — por identificador estrutural estável —
    não é posicional e passa; a gramática completa do seletor não é julgada
    aqui.
    """
    for segmento in caminho.split("."):
        base, _, resto = segmento.partition("[")
        if _segmento_numerico(base):
            return True
        if any(_segmento_numerico(seletor) for seletor in _seletores(resto)):
            return True
    return False


def _seletores(resto: str) -> list[str]:
    """Conteúdo de cada `[...]` do segmento, na ordem em que aparecem.

    Varre o segmento inteiro em vez de parar no primeiro colchete. Seletor sem
    fechamento encerra a varredura: forma malformada não é assunto de E1.
    """
    conteudos: list[str] = []
    while resto:
        seletor, fecha, resto = resto.partition("]")
        if not fecha:
            break
        conteudos.append(seletor)
        _, _, resto = resto.partition("[")
    return conteudos


def _segmento_numerico(segmento: str) -> bool:
    return bool(segmento) and segmento.isdigit() and segmento.isascii()


def _exigir_mapeamento(valor: object, onde: str) -> None:
    if not isinstance(valor, dict):
        raise _erro(_TIPO_INVALIDO, onde)


def _exigir_chaves(
    mapeamento: dict[str, Any],
    permitidas: frozenset[str],
    obrigatorias: frozenset[str],
    onde: str,
) -> None:
    """Schema fechado: nada além do autorizado, nada aquém do exigido.

    C-1a–C-1g fixam o que o índice contém; C-1h–C-1m e C-15e fixam o que ele
    nunca contém. Chave fora do conjunto é rejeitada em vez de ignorada.
    """
    for chave in mapeamento:
        if not isinstance(chave, str):
            raise _erro(_TIPO_INVALIDO, f"{onde}.<chave>")
        if chave not in permitidas:
            raise _erro(_CAMPO_DESCONHECIDO, f"{onde}.{chave}")
    for chave in sorted(obrigatorias):
        if chave not in mapeamento:
            raise _erro(_CAMPO_AUSENTE, f"{onde}.{chave}")


def _erro(categoria: str, localizador: str) -> IndiceInvalido:
    return IndiceInvalido(f"{categoria}: {localizador}")

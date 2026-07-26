"""Carregamento somente leitura da base de conhecimento comercial.

Este módulo lê e valida a estrutura de `knowledge/casa77.yaml`. Ele não conhece
nenhum valor comercial: valida presença e tipo dos campos, e devolve os dados
exatamente como estão no arquivo. Preço, capacidade, pacote, horário e restrição
continuam vindo do YAML em tempo de execução (docs/07 §2.2, doc 06 §5 regra 1).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class KnowledgeError(Exception):
    """Falha ao carregar ou validar a base de conhecimento.

    A mensagem identifica a categoria da falha e o campo envolvido. A causa
    técnica original, quando existe, fica encadeada em `__cause__` e não é
    exposta como texto de conversa.
    """


# Estrutura mínima exigida para o motor operar. Só caminhos e tipos — nunca
# valores comerciais.
_MAPPING = "mapeamento"
_LIST = "lista"
_NON_EMPTY_LIST = "lista não vazia"
_NON_EMPTY_STRING = "string não vazia"
_INTEGER = "número inteiro"

_REQUIRED_STRUCTURE: tuple[tuple[tuple[str, ...], str], ...] = (
    (("versao",), _NON_EMPTY_STRING),
    (("empresa",), _MAPPING),
    (("empresa", "nome"), _NON_EMPTY_STRING),
    (("eventos",), _MAPPING),
    (("eventos", "aceitos"), _LIST),
    (("capacidade",), _MAPPING),
    (("capacidade", "convidados_sentados"), _INTEGER),
    (("capacidade", "formato_coquetel"), _INTEGER),
    (("precos",), _MAPPING),
    (("precos", "moeda"), _NON_EMPTY_STRING),
    (("precos", "pacotes"), _NON_EMPTY_LIST),
    (("processo_comercial",), _MAPPING),
    (("processo_comercial", "responsavel"), _MAPPING),
    (("processo_comercial", "responsavel", "nome"), _NON_EMPTY_STRING),
)


def load_knowledge(path: str | Path) -> dict[str, Any]:
    """Carrega e valida a base de conhecimento a partir de `path`.

    Devolve os dados exatamente como lidos do arquivo, sem preencher campo
    ausente, sem valor padrão e sem conversão. Campos `null` ou `pendente`
    permanecem como estão — quem decide o que fazer com eles é a camada de
    regras, não este carregador.

    Levanta `KnowledgeError` em qualquer falha de leitura ou de estrutura.
    """
    path = Path(path)

    if not path.exists():
        raise KnowledgeError(f"Base de conhecimento não encontrada: {path}")

    try:
        texto = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise KnowledgeError(
            f"Não foi possível ler a base de conhecimento: {path}"
        ) from exc

    try:
        dados = yaml.safe_load(texto)
    except yaml.YAMLError as exc:
        raise KnowledgeError(f"Sintaxe YAML inválida em {path}: {exc}") from exc

    if not isinstance(dados, dict):
        raise KnowledgeError(
            f"A raiz de {path} deve ser um {_MAPPING}, "
            f"e não {_nome_do_tipo(dados)}"
        )

    _validar_estrutura(dados, path)
    return dados


def _validar_estrutura(dados: dict[str, Any], path: Path) -> None:
    """Confere presença e tipo de cada campo exigido, na ordem declarada.

    A ordem importa: o pai é sempre verificado antes do filho, então um campo
    aninhado nunca é consultado dentro de algo que não é mapeamento.
    """
    for caminho, tipo_esperado in _REQUIRED_STRUCTURE:
        valor = _obter(dados, caminho, path)
        _conferir_tipo(valor, tipo_esperado, caminho, path)


def _obter(dados: dict[str, Any], caminho: tuple[str, ...], path: Path) -> Any:
    atual: Any = dados
    for indice, chave in enumerate(caminho):
        if chave not in atual:
            raise KnowledgeError(
                f"Campo obrigatório ausente em {path}: {_rotulo(caminho[: indice + 1])}"
            )
        atual = atual[chave]
    return atual


def _conferir_tipo(
    valor: Any, tipo_esperado: str, caminho: tuple[str, ...], path: Path
) -> None:
    rotulo = _rotulo(caminho)

    if tipo_esperado == _MAPPING:
        if not isinstance(valor, dict):
            raise _erro_de_tipo(rotulo, _MAPPING, valor, path)

    elif tipo_esperado in (_LIST, _NON_EMPTY_LIST):
        if not isinstance(valor, list):
            raise _erro_de_tipo(rotulo, _LIST, valor, path)
        if tipo_esperado == _NON_EMPTY_LIST and not valor:
            raise KnowledgeError(
                f"Campo {rotulo} em {path} não pode ser uma lista vazia"
            )

    elif tipo_esperado == _NON_EMPTY_STRING:
        if not isinstance(valor, str):
            raise _erro_de_tipo(rotulo, "string", valor, path)
        if not valor.strip():
            raise KnowledgeError(f"Campo {rotulo} em {path} não pode ser vazio")

    elif tipo_esperado == _INTEGER:
        # `bool` é subclasse de `int` em Python e não serve como número aqui.
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise _erro_de_tipo(rotulo, _INTEGER, valor, path)


def _erro_de_tipo(
    rotulo: str, esperado: str, valor: Any, path: Path
) -> KnowledgeError:
    return KnowledgeError(
        f"Campo {rotulo} em {path} deve ser {esperado}, "
        f"e não {_nome_do_tipo(valor)}"
    )


def _rotulo(caminho: tuple[str, ...]) -> str:
    return ".".join(caminho)


def _nome_do_tipo(valor: Any) -> str:
    if valor is None:
        return "nulo"
    return type(valor).__name__

"""Carregamento fail-closed do futuro índice de respostas aprovadas.

Este módulo é a **fronteira de leitura** do arquivo que pretende ser
`knowledge/indice-respostas-aprovadas.yaml` (C-1). Ele **não cria** esse arquivo,
**não o descobre** e **não conhece caminho algum**: o caminho chega sempre por
argumento explícito. Não há caminho padrão, descoberta automática, glob ou
variável de ambiente.

A divisão de trabalho é estrita. Aqui mora apenas o que separa um artefato
**ilegível** de um artefato **legível**: existência, leitura, decodificação em
UTF-8, análise YAML segura e recusa de chave repetida no mesmo mapeamento. Toda
a **forma** — esqueleto, vocabulários, origem do referente, mecanismo e seleção
posicional — pertence a `response_index.validar_indice`, que é chamado sobre a
estrutura já analisada e cuja exceção atravessa este módulo **intacta**.

Nada é normalizado depois da análise: campo ausente não é preenchido, valor
padrão não é inventado, conteúdo não é reordenado e nulo não é completado. O que
volta é exatamente a estrutura que o analisador produziu.

Falha é **fail-closed**: nenhum caminho de erro devolve `None`, estrutura
parcial, estrutura vazia de recurso ou valor presumido. A mensagem de
`IndiceIlegivel` carrega **categoria e caminho** e nada mais — nunca o conteúdo
do arquivo, o valor recebido ou o texto bruto do analisador. A causa técnica
original, quando existe, fica encadeada em `__cause__`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from casa77_sdr.response_index import validar_indice

__all__ = ["IndiceIlegivel", "carregar_indice"]


class IndiceIlegivel(Exception):
    """O artefato não pôde ser lido ou analisado de forma segura.

    A mensagem tem a forma `<categoria>: <caminho>`. Ela diz **por que** o
    artefato é ilegível e **onde** ele estava — nunca o que havia dentro dele.
    Estrutura já analisada que viola o contrato **não** é caso desta exceção:
    isso é `IndiceInvalido`, levantada por `response_index`.
    """


# Categorias fechadas de ilegibilidade. Nenhuma delas descreve conteúdo.
_ARQUIVO_AUSENTE = "arquivo_ausente"
_LEITURA_FALHOU = "leitura_falhou"
_CODIFICACAO_INVALIDA = "codificacao_invalida"
_SINTAXE_INVALIDA = "sintaxe_invalida"
_CHAVE_DUPLICADA = "chave_duplicada"


class _ChaveDuplicada(Exception):
    """Sinal interno da análise: mesma chave duas vezes num mapeamento.

    Não deriva de `yaml.YAMLError` de propósito — é capturada antes dele para
    receber categoria própria, e nunca escapa deste módulo.
    """


class _LeitorEstrito(yaml.SafeLoader):
    """`SafeLoader` acrescido da recusa de chave repetida.

    A herança é de `yaml.SafeLoader` e o único comportamento alterado é a
    construção de mapeamento. Nenhum construtor é registrado, nenhuma tag é
    ampliada e nenhuma restrição de segurança do analisador seguro é relaxada:
    tag insegura continua sendo recusada pelo próprio `SafeLoader`.
    """

    def construct_mapping(self, node: Any, deep: bool = False) -> dict[Any, Any]:
        vistas: list[Any] = []
        for chave_node, _ in node.value:
            chave = self.construct_object(chave_node, deep=deep)
            try:
                repetida = chave in vistas
            except TypeError:
                # Chave não comparável não é assunto daqui: o `SafeLoader`
                # rejeita chave não hasheável logo adiante, como já rejeitava.
                continue
            if repetida:
                raise _ChaveDuplicada
            vistas.append(chave)
        return super().construct_mapping(node, deep=deep)


def carregar_indice(path: str | Path) -> dict[str, Any]:
    """Lê `path`, analisa o YAML e devolve a estrutura validada por C.

    O caminho é **sempre explícito** — `str` ou `Path` — e o arquivo é lido
    **somente** em UTF-8. A análise usa exclusivamente `_LeitorEstrito`, que é
    `yaml.SafeLoader` mais a recusa de chave repetida.

    A estrutura analisada é entregue a `validar_indice(...)` **sem retoque**: a
    raiz chega como o analisador a produziu, inclusive quando é `None`, lista ou
    escalar, e é o contrato de C quem a rejeita. `IndiceInvalido` **propaga
    intacta**, com categoria e localizador originais.

    Levanta `IndiceIlegivel` quando o artefato não pode ser lido ou analisado,
    e `IndiceInvalido` quando ele é legível mas não satisfaz o contrato. O
    arquivo nunca é criado, escrito, movido ou removido.
    """
    caminho = Path(path)

    try:
        texto = caminho.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise _ilegivel(_ARQUIVO_AUSENTE, caminho) from exc
    except UnicodeDecodeError as exc:
        raise _ilegivel(_CODIFICACAO_INVALIDA, caminho) from exc
    except OSError as exc:
        # Diretório no lugar do arquivo, permissão negada, dispositivo — tudo o
        # que impede a leitura cai aqui, sem distinção de conteúdo.
        raise _ilegivel(_LEITURA_FALHOU, caminho) from exc

    try:
        estrutura = yaml.load(texto, Loader=_LeitorEstrito)
    except _ChaveDuplicada as exc:
        raise _ilegivel(_CHAVE_DUPLICADA, caminho) from exc
    except yaml.YAMLError as exc:
        # O texto do analisador cita trechos do arquivo: ele fica em
        # `__cause__` e não entra na mensagem.
        raise _ilegivel(_SINTAXE_INVALIDA, caminho) from exc

    validar_indice(estrutura)
    return estrutura


def _ilegivel(categoria: str, caminho: Path) -> IndiceIlegivel:
    return IndiceIlegivel(f"{categoria}: {caminho}")

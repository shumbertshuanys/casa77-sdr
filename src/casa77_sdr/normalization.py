"""Normalização de entrada e chave de idempotência (3B.4).

Este módulo implementa o `NormalizadorEntrada` de
`docs/07-arquitetura-motor-respostas.md` §4.3 e §5 (etapas 1 e 2): recebe o
contrato comum de entrada (§6.1), com a **mensagem bruta**, e devolve a
mensagem normalizada, a chave de idempotência e a origem dessa chave.

Limite desta entrega: o normalizador **produz** a chave; ele não decide se
a mensagem é duplicada. A consulta `chave_processada` pertence à
persistência operacional e a decisão pertence à coordenação futura — por
isso nada aqui importa persistência, regras comerciais ou base de
conhecimento.

A normalização é **técnica e conservadora**: forma Unicode e espaços em
branco. Caixa, acentuação, pontuação, emoji e conteúdo semântico são
preservados, porque interpretar o que a mensagem significa é papel da
interpretação (LLM), nunca desta camada.

Função pura: sem relógio, sem I/O, sem rede, sem log, sem aleatoriedade e
sem estado global mutável. A mesma entrada com a mesma janela produz
sempre a mesma saída, inclusive entre processos — o digest é de
`hashlib`, não do `hash()` do interpretador.
"""

from __future__ import annotations

import hashlib
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum

_EPOCA_UTC = datetime(1970, 1, 1, tzinfo=timezone.utc)
_RESOLUCAO = timedelta(microseconds=1)


class MensagemVazia(Exception):
    """Mensagem sem conteúdo após a normalização técnica.

    Não é caso de negócio nem erro de contrato: é a condição do §5 etapa 1
    — mensagem vazia não é processada e não produz transição.
    """


class EntradaInvalida(Exception):
    """Entrada que viola o contrato comum de §6.1.

    Sinaliza defeito de quem montou a entrada (adaptador de canal ou
    configuração), nunca comportamento do interessado.
    """


class OrigemChave(StrEnum):
    """Origem da chave de idempotência (§4.3).

    `IDENTIFICADOR_CANAL` é a origem confiável; `COMPOSTA` é o fallback
    heurístico, e o registro dessa distinção é o que permite auditar
    depois se um veredito de duplicidade foi seguro ou aproximado.
    """

    IDENTIFICADOR_CANAL = "identificador_canal"
    COMPOSTA = "composta"


@dataclass(frozen=True)
class EntradaMensagem:
    """Contrato comum de entrada do motor (§6.1).

    O mesmo para WhatsApp, terminal e teste. `mensagem` chega **bruta**,
    exatamente como recebida: a normalização acontece dentro do motor
    (D6). O contrato **não** contém estado, qualificação nem pendências —
    o contexto é sempre recuperado da persistência, nunca recebido do
    canal (E1–E3).

    `id_mensagem_canal` e `id_atendimento` são opcionais; ausência é
    normal. `id_atendimento`, quando presente, é apenas referência para
    consulta futura (N2) e não participa da identidade da mensagem.
    """

    canal: str
    contato: str
    mensagem: str
    recebida_em: datetime
    id_mensagem_canal: str | None = None
    id_atendimento: str | None = None


@dataclass(frozen=True)
class EntradaNormalizada:
    """Saída do normalizador: texto normalizado, chave e origem da chave."""

    mensagem_normalizada: str
    chave_idempotencia: str
    origem_chave: OrigemChave


def normalizar_entrada(
    entrada: EntradaMensagem, janela_idempotencia: timedelta
) -> EntradaNormalizada:
    """Normaliza a mensagem e deriva a chave de idempotência (§4.3).

    `janela_idempotencia` é obrigatória e não tem valor padrão: a largura
    da janela é decisão de quem configura o motor, com medição, e não
    constante desta camada (§4.3, risco 3b). Ela só é usada no fallback
    composto.

    Validação do contrato antes de qualquer derivação: canal e contato
    preenchidos, mensagem com conteúdo, instante com fuso efetivo, janela
    positiva e identificadores opcionais não vazios quando fornecidos.
    Nenhuma exceção reproduz mensagem, contato ou identificador — o defeito
    é indicado pelo campo, não pelo valor.
    """
    _exigir_preenchido(entrada.canal, "canal")
    _exigir_preenchido(entrada.contato, "contato")

    if not isinstance(entrada.mensagem, str):
        raise EntradaInvalida("O campo 'mensagem' deve ser texto")
    mensagem_normalizada = _normalizar_mensagem(entrada.mensagem)
    if not mensagem_normalizada:
        raise MensagemVazia("A mensagem não tem conteúdo após a normalização técnica")

    _exigir_instante_com_fuso(entrada.recebida_em)
    _exigir_janela_positiva(janela_idempotencia)
    if entrada.id_mensagem_canal is not None:
        _exigir_preenchido(entrada.id_mensagem_canal, "id_mensagem_canal")
    if entrada.id_atendimento is not None:
        _exigir_preenchido(entrada.id_atendimento, "id_atendimento")

    if entrada.id_mensagem_canal is not None:
        origem = OrigemChave.IDENTIFICADOR_CANAL
        chave = _derivar_chave(origem, entrada.id_mensagem_canal)
    else:
        origem = OrigemChave.COMPOSTA
        balde = _balde_temporal(entrada.recebida_em, janela_idempotencia)
        chave = _derivar_chave(
            origem,
            entrada.canal,
            entrada.contato,
            str(balde),
            mensagem_normalizada,
        )

    return EntradaNormalizada(
        mensagem_normalizada=mensagem_normalizada,
        chave_idempotencia=chave,
        origem_chave=origem,
    )


def _normalizar_mensagem(mensagem: str) -> str:
    """Forma Unicode NFKC, extremidades aparadas e espaços colapsados.

    É tudo o que a normalização faz. Não há `casefold`, `lower`, remoção
    de acento, remoção de pontuação nem qualquer aproximação semântica:
    "Teste" e "teste" continuam mensagens diferentes, assim como "e" e
    "é". Reduzir isso aqui transformaria repetição humana legítima em
    silêncio e apagaria conteúdo antes da interpretação.

    Deliberadamente distinta de `rules._normalizar`, que existe para
    igualdade nominal contra a base e por isso remove caixa e acento —
    reaproveitá-la aqui seria usar uma comparação comercial como
    identidade técnica de mensagem.
    """
    return " ".join(unicodedata.normalize("NFKC", mensagem).split())


def _balde_temporal(recebida_em: datetime, janela: timedelta) -> int:
    """Índice determinístico do balde temporal, em UTC.

    Baldes fixos alinhados à época UTC, com largura igual à janela. Não
    consulta o relógio atual: o índice depende apenas do instante da
    própria mensagem, convertido para UTC, de modo que o mesmo instante
    expresso em fusos diferentes cai no mesmo balde.

    Limitação conhecida da heurística: com baldes fixos, duas mensagens
    temporalmente próximas podem cair em baldes adjacentes e produzir
    chaves distintas. Janela deslizante não pertence a esta entrega.
    """
    decorrido = (recebida_em.astimezone(timezone.utc) - _EPOCA_UTC) // _RESOLUCAO
    largura = janela // _RESOLUCAO
    return decorrido // largura


def _derivar_chave(origem: OrigemChave, *componentes: str) -> str:
    """Chave opaca `origem + digest`, com composição inequívoca.

    Cada componente entra prefixado pelo próprio comprimento em bytes, de
    modo que valor algum consegue imitar a fronteira entre componentes:
    composições diferentes nunca produzem o mesmo material, mesmo quando
    os valores contêm delimitadores. A origem entra no material e no
    prefixo, o que separa os dois modos e impede colisão entre eles.

    A chave é opaca por construção: não expõe identificador do canal,
    contato, mensagem nem horário.
    """
    material = b"".join(_bloco(parte) for parte in (origem.value, *componentes))
    return f"{origem.value}:{hashlib.sha256(material).hexdigest()}"


def _bloco(valor: str) -> bytes:
    bruto = valor.encode("utf-8")
    return f"{len(bruto)}:".encode("ascii") + bruto


def _exigir_preenchido(valor: str, campo: str) -> None:
    if not isinstance(valor, str) or not valor.strip():
        raise EntradaInvalida(f"O campo '{campo}' deve ser texto não vazio")


def _exigir_instante_com_fuso(recebida_em: datetime) -> None:
    """Exige fuso **efetivo**, não apenas `tzinfo` preenchido.

    Um `tzinfo` cujo `utcoffset()` devolve `None` não permite converter
    para UTC — e sem conversão o balde temporal deixaria de ser
    comparável entre canais.
    """
    if not isinstance(recebida_em, datetime):
        raise EntradaInvalida("O campo 'recebida_em' deve ser um instante")
    if recebida_em.tzinfo is None or recebida_em.utcoffset() is None:
        raise EntradaInvalida("O campo 'recebida_em' exige fuso horário efetivo")


def _exigir_janela_positiva(janela: timedelta) -> None:
    if not isinstance(janela, timedelta):
        raise EntradaInvalida("A janela de idempotência deve ser uma duração")
    if janela <= timedelta(0):
        raise EntradaInvalida("A janela de idempotência deve ser positiva")

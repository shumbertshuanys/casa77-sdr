"""Fronteira **agnóstica de provedor** do produtor não determinístico da etapa 4.

Materializa a parte de N-b que `src/casa77_sdr/interpretation.py` deixa fora de si
por **M-NB9** e **M-AJ2-9**: o **transporte** entre um produtor semântico de texto
livre e a fronteira determinística. O módulo faz exatamente quatro coisas:

1. **gera** o JSON Schema fechado que restringe a saída estruturada do produtor;
2. **valida estruturalmente** o payload recebido, localmente e sem confiar no
   provedor;
3. **traduz** o payload para a `EntradaInterpretacao` pré-canônica de N-b;
4. **encadeia** obrigatoriamente para `canonicalizar_interpretacao(...)`.

**O adaptador traduz; não repara.** Nenhuma incoerência semanticamente
representável é tornada coerente antes da fronteira determinística: correção de
campo ausente, com valor divergente, com confiança divergente ou repetida
**atravessa** e é julgada por `canonicalizar_interpretacao`. Toda `Interpretacao`
devolvida por este módulo atravessou aquela função — **nenhuma outra construção
de `Interpretacao` é permitida aqui**.

O módulo é **puro e agnóstico**: zero rede, zero SDK, zero fornecedor, zero
leitura de ambiente, zero filesystem, zero YAML, zero `knowledge/**`, zero
retry, zero cache, zero relógio, zero logging de texto e zero dado comercial. O
*prompt* de sistema é **recebido**, nunca lido daqui.

**Confiança permanece binária** (N-b-G7): `ALTA` | `BAIXA`, com ausência
representada por `None`. O transporte a carrega num `ConfidenceSlot` de dois
campos — `presente` e `valor` — precisamente para que **nenhuma terceira
semântica** exista: `presente = false` significa **ausência**, jamais `BAIXA`, e
o `valor` desse ramo é preenchimento estrutural sem semântica.

As **falhas do produtor** são uma família **separada** do domínio
(`FalhaProdutorInterpretacao`) e **não são reembaladas** sobre `E-Nb-*`: erro de
contrato continua `ValueError` com o código no início da mensagem, e tipo
runtime incompatível continua `TypeError` (M-NB4). Nenhuma falha carrega texto
da mensagem, payload bruto, PII ou credencial.
"""

from __future__ import annotations

import json
from dataclasses import fields
from enum import StrEnum
from typing import Any, Protocol, runtime_checkable

from casa77_sdr import interpretation as _dominio
from casa77_sdr.identity import Confianca
from casa77_sdr.interpretation import (
    AssuntoComercial,
    CorrecaoInterpretada,
    DadosExtraidos,
    EntradaInterpretacao,
    IntencaoAutonomaRecebida,
    IntencaoConversacional,
    Interpretacao,
    PerguntaComercial,
    ReferenciaAoEventoAnterior,
    TrechoAmbiguoRecebido,
    canonicalizar_interpretacao,
)
from casa77_sdr.qualification import FormatoEvento

__all__ = [
    "MotivoFalhaProdutor",
    "FalhaProdutorInterpretacao",
    "ProdutorTextoEstruturado",
    "gerar_schema_interpretacao",
    "traduzir_payload",
    "interpretar_mensagem",
]


# --------------------------------------------------------------------------
# Vocabulários — derivados mecanicamente do domínio, nunca redigitados
# --------------------------------------------------------------------------

#: Os dois valores de `Confianca` (N-b-G7).
_CONFIANCAS: tuple[str, ...] = tuple(item.value for item in Confianca)

#: Os dois valores de `FormatoEvento` (N-b-D5), reutilizado por import (AJ1-F2).
_FORMATOS: tuple[str, ...] = tuple(item.value for item in FormatoEvento)

#: Os **seis** campos de `dados_extraidos` (N-b-D1), na ordem do contrato.
#: Derivados da própria dataclass: os campos de confiança são o prefixo
#: `confianca_` e ficam de fora.
_CAMPOS: tuple[str, ...] = tuple(
    campo.name
    for campo in fields(DadosExtraidos)
    if not campo.name.startswith("confianca_")
)

#: Os **54** valores de `AssuntoComercial` (AJ2, M-AJ2-1), em ordem documental.
_ASSUNTOS: tuple[str, ...] = tuple(item.value for item in AssuntoComercial)

#: Os **cinco** códigos admissíveis no slot autônomo (AJ1-3). Derivados do
#: conjunto fechado do domínio e ordenados pela declaração do enum, para que o
#: schema não possa divergir da partição A1 / A2 / B.
_AUTONOMOS: tuple[str, ...] = tuple(
    item.value
    for item in IntencaoConversacional
    if item in _dominio._CODIGOS_AUTONOMOS
)

#: Campos de `dados_extraidos` cujo domínio de transporte é inteiro.
_CAMPOS_INTEIROS: frozenset[str] = frozenset({"convidados"})

#: Campos de `dados_extraidos` cujo domínio de transporte é vocabulário fechado.
_CAMPOS_ENUM: frozenset[str] = frozenset({"formato"})

_REF_SLOT = "#/definitions/ConfidenceSlot"


# --------------------------------------------------------------------------
# Falhas do produtor — família separada, fechada e sanitizada
# --------------------------------------------------------------------------


class MotivoFalhaProdutor(StrEnum):
    """Vocabulário **fechado** das falhas do produtor não determinístico.

    Não são erros de contrato N-b: elas significam que **nenhuma
    `Interpretacao` existe** neste ciclo (N-b-M1), não que a entrada recebida
    violou o contrato. Nenhum membro carrega texto, payload, PII ou credencial.
    """

    SEM_BLOCO_ESTRUTURADO = "sem_bloco_estruturado"
    MULTIPLOS_BLOCOS_ESTRUTURADOS = "multiplos_blocos_estruturados"
    RECUSA_DO_MODELO = "recusa_do_modelo"
    TRUNCADO = "truncado"
    JSON_INVALIDO = "json_invalido"
    PAYLOAD_FORA_DO_SCHEMA = "payload_fora_do_schema"
    TIMEOUT = "timeout"
    ERRO_DE_TRANSPORTE = "erro_de_transporte"
    ERRO_DO_PROVEDOR = "erro_do_provedor"


class FalhaProdutorInterpretacao(Exception):
    """Falha do produtor — **um motivo fechado e nada mais**.

    A exceção **não carrega** a mensagem do interessado, o payload bruto, o
    texto devolvido pelo provedor, PII, chave ou detalhe interno, e `str`/`repr`
    expõem **somente** o motivo. É o que torna §6.6 verificável sobre esta
    fronteira.
    """

    def __init__(self, motivo: MotivoFalhaProdutor) -> None:
        if not isinstance(motivo, MotivoFalhaProdutor):
            raise TypeError("motivo precisa ser um MotivoFalhaProdutor")
        super().__init__(motivo.value)
        self.motivo = motivo

    def __str__(self) -> str:
        return self.motivo.value

    def __repr__(self) -> str:
        return f"FalhaProdutorInterpretacao({self.motivo.name})"


def _falha(motivo: MotivoFalhaProdutor) -> FalhaProdutorInterpretacao:
    return FalhaProdutorInterpretacao(motivo)


# --------------------------------------------------------------------------
# Fronteira do produtor — Protocol, sem tipo de fornecedor algum
# --------------------------------------------------------------------------


@runtime_checkable
class ProdutorTextoEstruturado(Protocol):
    """Contrato do produtor não determinístico, **sem fornecedor**.

    A fronteira troca **`str`** e `FalhaProdutorInterpretacao`, nunca objeto de
    resposta de provedor: nenhum tipo de SDK atravessa este Protocol
    (N-b-F3).
    """

    def produzir(
        self,
        *,
        prompt_sistema: str,
        mensagem: str,
        schema: dict[str, Any],
    ) -> str:
        """Devolve o **texto JSON** da saída estruturada, ou levanta falha."""
        ...


# --------------------------------------------------------------------------
# JSON Schema — fechado, sem parâmetro opcional, com ConfidenceSlot por $ref
# --------------------------------------------------------------------------


def _objeto(propriedades: dict[str, Any]) -> dict[str, Any]:
    """Objeto fechado: `additionalProperties: false` e **tudo** em `required`."""
    return {
        "type": "object",
        "additionalProperties": False,
        "required": list(propriedades),
        "properties": propriedades,
    }


def _slot_confianca() -> dict[str, Any]:
    return {"$ref": _REF_SLOT}


def _nulavel(tipo: str) -> dict[str, Any]:
    return {"type": [tipo, "null"]}


def _enum_nulavel(membros: tuple[str, ...]) -> dict[str, Any]:
    return {"anyOf": [{"type": "string", "enum": list(membros)}, {"type": "null"}]}


def _valor_de_campo(campo: str) -> dict[str, Any]:
    """Domínio de transporte de cada um dos seis campos (N-b-D2–N-b-D5)."""
    if campo in _CAMPOS_ENUM:
        return _enum_nulavel(_FORMATOS)
    if campo in _CAMPOS_INTEIROS:
        return _nulavel("integer")
    return _nulavel("string")


def gerar_schema_interpretacao() -> dict[str, Any]:
    """Constrói o JSON Schema da saída estruturada do produtor.

    Propriedades da raiz: **nove**, uma por categoria de §6.3 — com a categoria
    5 representada por `pedido_de_humano` e `confianca_pedido_de_humano`
    (N-b-PH1) e **sem slot de códigos `A1`** (AJ1-1, M-NB2).

    Garantias estruturais, provadas mecanicamente em
    `tests/test_interpretation_llm.py`: **zero** parâmetro opcional — toda
    propriedade de todo objeto está em `required` —; **11** parâmetros de união,
    exatamente nas posições onde a ausência precisa ser representável;
    `additionalProperties: false` em **todo** objeto; **13** posições de
    `ConfidenceSlot`, todas por `$ref`; e **nenhuma** união em posição de
    confiança.

    Os enums são **derivados do domínio em tempo de importação** — 2 confianças,
    2 formatos, 6 campos, 54 assuntos e 5 códigos autônomos —, nunca escritos à
    mão: o schema não pode divergir do vocabulário aprovado.
    """
    dados: dict[str, Any] = {}
    for campo in _CAMPOS:
        dados[campo] = _valor_de_campo(campo)
        dados[f"confianca_{campo}"] = _slot_confianca()

    item_correcao = _objeto(
        {
            "campo": {"type": "string", "enum": list(_CAMPOS)},
            "valor_novo": {
                "anyOf": [{"type": "string"}, {"type": "integer"}, {"type": "null"}]
            },
            "confianca": _slot_confianca(),
        }
    )
    item_pergunta = _objeto(
        {
            "texto": _nulavel("string"),
            "confianca": _slot_confianca(),
            "assunto": _enum_nulavel(_ASSUNTOS),
        }
    )
    item_referencia = _objeto(
        {"texto": _nulavel("string"), "confianca": _slot_confianca()}
    )
    item_trecho = _objeto(
        {"texto": _nulavel("string"), "confianca": _slot_confianca()}
    )
    item_intencao = _objeto(
        {
            "codigo": {"type": "string", "enum": list(_AUTONOMOS)},
            "confianca": _slot_confianca(),
        }
    )

    raiz = _objeto(
        {
            "dados_extraidos": _objeto(dados),
            "correcoes": {"type": "array", "items": item_correcao},
            "perguntas_comerciais": {"type": "array", "items": item_pergunta},
            "pedido_de_humano": {"type": "boolean"},
            "confianca_pedido_de_humano": _slot_confianca(),
            "referencias_evento_anterior": {
                "type": "array",
                "items": item_referencia,
            },
            "trechos_ambiguos": {"type": "array", "items": item_trecho},
            "confianca_global": _slot_confianca(),
            "intencoes_autonomas": {"type": "array", "items": item_intencao},
        }
    )
    raiz["definitions"] = {
        "ConfidenceSlot": _objeto(
            {
                "presente": {"type": "boolean"},
                "valor": {"type": "string", "enum": list(_CONFIANCAS)},
            }
        )
    }
    return raiz


# --------------------------------------------------------------------------
# Validação estrutural local — o payload não é aceito por confiança no provedor
# --------------------------------------------------------------------------


def _exigir_objeto(valor: object, chaves: tuple[str, ...]) -> dict[str, Any]:
    if not isinstance(valor, dict):
        raise _falha(MotivoFalhaProdutor.PAYLOAD_FORA_DO_SCHEMA)
    if set(valor) != set(chaves):
        raise _falha(MotivoFalhaProdutor.PAYLOAD_FORA_DO_SCHEMA)
    return valor


def _exigir_lista(valor: object) -> list[Any]:
    if not isinstance(valor, list):
        raise _falha(MotivoFalhaProdutor.PAYLOAD_FORA_DO_SCHEMA)
    return valor


def _exigir_booleano(valor: object) -> bool:
    if not isinstance(valor, bool):
        raise _falha(MotivoFalhaProdutor.PAYLOAD_FORA_DO_SCHEMA)
    return valor


def _exigir_texto_ou_nulo(valor: object) -> str | None:
    if valor is None or isinstance(valor, str):
        return valor
    raise _falha(MotivoFalhaProdutor.PAYLOAD_FORA_DO_SCHEMA)


def _exigir_inteiro_ou_nulo(valor: object) -> int | None:
    """Inteiro JSON — **`bool` não é inteiro** e é rejeitado (N-b-D4).

    Em Python `bool` é subclasse de `int`; aceitar `True` aqui seria tratá-lo
    como inteiro, exatamente o que o contrato proíbe. A rejeição é de
    **transporte**: o valor sequer chega ao canonicalizador.
    """
    if valor is None:
        return valor
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise _falha(MotivoFalhaProdutor.PAYLOAD_FORA_DO_SCHEMA)
    return valor


def _exigir_valor_de_correcao(valor: object) -> str | int | None:
    if valor is None or isinstance(valor, str):
        return valor
    return _exigir_inteiro_ou_nulo(valor)


def _resolver_enum(valor: object, membros: tuple[str, ...]) -> str:
    """Resolve um identificador de vocabulário fechado, **sem aproximar**.

    A saída estruturada pode devolver o membro com capitalização diferente. A
    única tolerância admitida é, portanto, **correspondência única ignorando
    caixa**. *Fuzzy matching*, similaridade, prefixo, distância de edição e
    "o membro mais próximo" são proibidos: aproximar é fabricar classificação
    (N-b-Q10). Sem correspondência única, o payload **falha fechado** — e
    **nunca** vira `ASSUNTO_NAO_CLASSIFICADO`.
    """
    if not isinstance(valor, str):
        raise _falha(MotivoFalhaProdutor.PAYLOAD_FORA_DO_SCHEMA)
    alvo = valor.casefold()
    correspondentes = [membro for membro in membros if membro.casefold() == alvo]
    if len(correspondentes) != 1:
        raise _falha(MotivoFalhaProdutor.PAYLOAD_FORA_DO_SCHEMA)
    return correspondentes[0]


def _validar_slot(valor: object) -> dict[str, Any]:
    slot = _exigir_objeto(valor, ("presente", "valor"))
    _exigir_booleano(slot["presente"])
    _resolver_enum(slot["valor"], _CONFIANCAS)
    return slot


# --------------------------------------------------------------------------
# Tradução — uniforme por campo, sem reparo e sem normalização de texto
# --------------------------------------------------------------------------


def _traduzir_confianca(slot: object) -> Confianca | None:
    """`ConfidenceSlot` → `Confianca | None`.

    `presente = false` significa **ausência** (`None`) — **nunca** `BAIXA` —, e
    o `valor` desse ramo é descartado como o preenchimento estrutural que é.
    """
    validado = _validar_slot(slot)
    if not validado["presente"]:
        return None
    return Confianca(_resolver_enum(validado["valor"], _CONFIANCAS))


def _traduzir_formato(valor: object) -> object:
    """`sentado` | `coquetel` → `FormatoEvento`; qualquer outro texto fica cru.

    O ramo cru só é alcançado por `correcoes[].valor_novo`, onde o schema
    **deliberadamente** admite texto livre: preservá-lo é o que mantém
    `E-Nb-17` alcançável, em vez de o adaptador reparar o produtor. Em
    `dados_extraidos.formato` ele é inalcançável — ali o vocabulário fechado
    é exigido **antes**, no transporte (ver `_traduzir_dados`).
    """
    if not isinstance(valor, str):
        return valor
    alvo = valor.casefold()
    correspondentes = [
        membro for membro in FormatoEvento if membro.value.casefold() == alvo
    ]
    if len(correspondentes) == 1:
        return correspondentes[0]
    return valor


def _traduzir_valor(campo: str, valor: object) -> object:
    """Tradução de valor **uniforme por campo**.

    A mesma função, chaveada pelo campo, é aplicada **identicamente** a
    `dados_extraidos.<campo>` e a `correcoes[].valor_novo`. Não é preferência
    estética: `canonicalizar_interpretacao` compara os dois por **igualdade
    estrita de tipo**, de modo que traduzir `"sentado"` de um lado e deixá-lo
    `str` do outro **fabricaria um `E-Nb-17` inexistente**.

    `tipo_evento`, `data_nomeada`, `nome` e `contato` são **texto literal**:
    sem `strip`, sem normalização, sem resumo e sem paráfrase (N-b-D2, N-b-D3,
    N-b-Q9).
    """
    if valor is None:
        return None
    if campo in _CAMPOS_ENUM:
        return _traduzir_formato(valor)
    return valor


def _traduzir_dados(payload: object) -> DadosExtraidos:
    chaves = tuple(_CAMPOS) + tuple(f"confianca_{campo}" for campo in _CAMPOS)
    dados = _exigir_objeto(payload, chaves)

    argumentos: dict[str, Any] = {}
    for campo in _CAMPOS:
        bruto = dados[campo]
        if campo in _CAMPOS_INTEIROS:
            _exigir_inteiro_ou_nulo(bruto)
        elif campo in _CAMPOS_ENUM:
            # O schema restringe este campo ao vocabulário fechado. Um valor
            # fora dele é **violação de transporte**, não erro de contrato:
            # encaminhá-lo ao canonicalizador produziria `E-Nb-9` por um
            # caminho que o schema real já impede. `E-Nb-9` continua sendo
            # autoridade da Camada A, provada diretamente sobre o domínio.
            if bruto is not None:
                _resolver_enum(bruto, _FORMATOS)
        else:
            _exigir_texto_ou_nulo(bruto)
        argumentos[campo] = _traduzir_valor(campo, bruto)
        argumentos[f"confianca_{campo}"] = _traduzir_confianca(
            dados[f"confianca_{campo}"]
        )
    return DadosExtraidos(**argumentos)


def _traduzir_correcoes(payload: object) -> tuple[CorrecaoInterpretada, ...]:
    itens = _exigir_lista(payload)
    correcoes: list[CorrecaoInterpretada] = []
    for bruto in itens:
        item = _exigir_objeto(bruto, ("campo", "valor_novo", "confianca"))
        campo = _resolver_enum(item["campo"], _CAMPOS)
        valor = _exigir_valor_de_correcao(item["valor_novo"])
        correcoes.append(
            CorrecaoInterpretada(
                campo=campo,
                valor_novo=_traduzir_valor(campo, valor),  # type: ignore[arg-type]
                confianca=_traduzir_confianca(item["confianca"]),
            )
        )
    return tuple(correcoes)


def _traduzir_perguntas(payload: object) -> tuple[PerguntaComercial, ...]:
    itens = _exigir_lista(payload)
    perguntas: list[PerguntaComercial] = []
    for bruto in itens:
        item = _exigir_objeto(bruto, ("texto", "confianca", "assunto"))
        assunto_bruto = item["assunto"]
        assunto = (
            None
            if assunto_bruto is None
            else AssuntoComercial(_resolver_enum(assunto_bruto, _ASSUNTOS))
        )
        perguntas.append(
            PerguntaComercial(
                texto=_exigir_texto_ou_nulo(item["texto"]),
                confianca=_traduzir_confianca(item["confianca"]),
                assunto=assunto,
            )
        )
    return tuple(perguntas)


def _traduzir_referencias(payload: object) -> tuple[ReferenciaAoEventoAnterior, ...]:
    itens = _exigir_lista(payload)
    return tuple(
        ReferenciaAoEventoAnterior(
            texto=_exigir_texto_ou_nulo(item["texto"]),
            confianca=_traduzir_confianca(item["confianca"]),
        )
        for item in (
            _exigir_objeto(bruto, ("texto", "confianca")) for bruto in itens
        )
    )


def _traduzir_trechos(payload: object) -> tuple[TrechoAmbiguoRecebido, ...]:
    itens = _exigir_lista(payload)
    return tuple(
        TrechoAmbiguoRecebido(
            texto=_exigir_texto_ou_nulo(item["texto"]),
            confianca=_traduzir_confianca(item["confianca"]),
        )
        for item in (
            _exigir_objeto(bruto, ("texto", "confianca")) for bruto in itens
        )
    )


def _traduzir_intencoes(payload: object) -> tuple[IntencaoAutonomaRecebida, ...]:
    itens = _exigir_lista(payload)
    return tuple(
        IntencaoAutonomaRecebida(
            codigo=IntencaoConversacional(_resolver_enum(item["codigo"], _AUTONOMOS)),
            confianca=_traduzir_confianca(item["confianca"]),
        )
        for item in (
            _exigir_objeto(bruto, ("codigo", "confianca")) for bruto in itens
        )
    )


#: As **nove** propriedades da raiz do transporte, na ordem do contrato.
_CHAVES_RAIZ: tuple[str, ...] = (
    "dados_extraidos",
    "correcoes",
    "perguntas_comerciais",
    "pedido_de_humano",
    "confianca_pedido_de_humano",
    "referencias_evento_anterior",
    "trechos_ambiguos",
    "confianca_global",
    "intencoes_autonomas",
)


def traduzir_payload(payload: object) -> EntradaInterpretacao:
    """Valida estruturalmente o payload e o traduz para `EntradaInterpretacao`.

    **Não repara.** Correção de campo ausente de `dados_extraidos`, com valor
    divergente, com confiança divergente ou com campo repetido **atravessa**
    intacta e é julgada por `canonicalizar_interpretacao` — `E-Nb-17` e
    `E-Nb-7` continuam alcançáveis a partir de payload de transporte válido.
    Nenhum texto é normalizado e nenhuma duplicata é removida.

    :raises FalhaProdutorInterpretacao: payload fora do schema de transporte.
    """
    raiz = _exigir_objeto(payload, _CHAVES_RAIZ)
    return EntradaInterpretacao(
        dados_extraidos=_traduzir_dados(raiz["dados_extraidos"]),
        correcoes=_traduzir_correcoes(raiz["correcoes"]),
        perguntas_comerciais=_traduzir_perguntas(raiz["perguntas_comerciais"]),
        pedido_de_humano=_exigir_booleano(raiz["pedido_de_humano"]),
        confianca_pedido_de_humano=_traduzir_confianca(
            raiz["confianca_pedido_de_humano"]
        ),
        referencias_evento_anterior=_traduzir_referencias(
            raiz["referencias_evento_anterior"]
        ),
        trechos_ambiguos=_traduzir_trechos(raiz["trechos_ambiguos"]),
        confianca_global=_traduzir_confianca(raiz["confianca_global"]),
        intencoes_autonomas=_traduzir_intencoes(raiz["intencoes_autonomas"]),
    )


# --------------------------------------------------------------------------
# Encadeamento obrigatório — produtor → transporte → canonicalização
# --------------------------------------------------------------------------


def interpretar_mensagem(
    mensagem: str,
    *,
    produtor: ProdutorTextoEstruturado,
    prompt_sistema: str,
) -> Interpretacao:
    """Mensagem normalizada → `Interpretacao` canônica.

    Executa, nesta ordem: gera o schema; chama o produtor **uma única vez**
    (zero retry, zero *fallback*, zero cache, zero fila — N-b-M7); carrega o
    JSON; valida a estrutura localmente; traduz; e **encadeia** para
    `canonicalizar_interpretacao(...)`, a única autoridade que produz
    `Interpretacao`.

    Esta capacidade termina em `Interpretacao`. Ela **não** produz `Exx`,
    `Txx`, `Rxx`, decisão comercial, estado, *handoff*, transição nem resposta
    final, e **`N-b-RES2` permanece aberto**.

    :raises FalhaProdutorInterpretacao: nenhuma `Interpretacao` neste ciclo.
    :raises TypeError: tipo runtime incompatível na fronteira determinística.
    :raises ValueError: erro de contrato `E-Nb-*`, com o código na mensagem.
    """
    if not isinstance(mensagem, str):
        raise TypeError("a mensagem precisa ser texto")
    if not isinstance(prompt_sistema, str):
        raise TypeError("o prompt de sistema precisa ser texto")

    bruto = produtor.produzir(
        prompt_sistema=prompt_sistema,
        mensagem=mensagem,
        schema=gerar_schema_interpretacao(),
    )
    if not isinstance(bruto, str):
        raise _falha(MotivoFalhaProdutor.PAYLOAD_FORA_DO_SCHEMA)
    try:
        payload = json.loads(bruto)
    except ValueError:
        # `from None`: nem a posição do erro nem o trecho do payload escapam.
        raise _falha(MotivoFalhaProdutor.JSON_INVALIDO) from None
    return canonicalizar_interpretacao(traduzir_payload(payload))

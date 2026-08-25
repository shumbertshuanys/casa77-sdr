"""Fronteira determinística da interpretação da etapa 4 (contrato N-b / AJ1 / AJ2).

Materializa a **parte determinística** do contrato de
`docs/07-arquitetura-motor-respostas.md` §6.3 — a arbitragem **N-b**, a
micro-arbitragem **AJ1** e o **delta AJ2**. O módulo faz exatamente três coisas:

1. **canonicaliza** a entrada estruturada recebida do futuro produtor não
   determinístico, produzindo uma `Interpretacao` canônica válida **ou** um erro
   de contrato (`E-Nb-*`);
2. **projeta** a `Interpretacao` canônica para a `ProjecaoInterpretacao` de
   `identity.py`, que permanece com **sete** campos (N-b-K1–N-b-K8);
3. **produz a condição 5** de §4.4 — `interesse_confirmar_disponibilidade` —
   como função total (N-b-CD1–N-b-CD4).

**`A1` não é entrada semântica independente** (AJ1-1). O produtor não
determinístico entrega **somente** as categorias reais — `dados_extraidos`,
`correcoes`, `perguntas_comerciais`, `pedido_de_humano` com a confiança
aplicável, `referencias_evento_anterior`, `trechos_ambiguos`,
`confianca_global` — e as intenções **autônomas** dos grupos **A2** e **B**
(AJ1-2, AJ1-3). Os **seis** códigos do grupo **A1** têm **presença derivada** do
payload autoritativo (N-b-X2, N-b-X4) e **confiança calculada** por **N-b-X3**
(N-b-G6b). A confiança calculada é **armazenada** na `Interpretacao` canônica
para auditabilidade — **armazenada não é declarada** (AJ1-A1c).

O módulo é **puro e determinístico**: zero I/O, zero rede, zero relógio, zero
persistência, zero YAML, zero LLM, zero fornecedor, zero SDK, zero API, zero
cache, zero fila. Ele **não** interpreta texto livre, **não** lê contexto,
**não** avalia regra comercial e **não** produz — nem representa como saída
própria — `Exx`, `Txx`, `Rxx`, `Qualificacao`, `Violacao`, `Estado`, pendência,
`motivo_encerramento`, `CondicoesCiclo`, `DecisaoMaquina` ou
`RegistroAtendimento` (**E-Nb-19**). A **condição 5** é a **única** condição de
§4.4 **produzida aqui** — e a única **materializada** em código. As condições
**2** e **4** possuem **produtor conceitual** atribuído por **S2-D8** (§4.4.1,
eixos **A** e **B**), mas continuam **NÃO MATERIALIZADAS**: S2-D8 permanece
**ARBITRADA / NÃO MATERIALIZADA** e **nada neste módulo as produz**. A condição
**8** continua **NÃO ATRIBUÍDA** (**S3-D1**).

Erros de contrato **bloqueiam na fronteira**: nenhuma `Interpretacao` canônica é
produzida e nenhuma projeção existe. As duas famílias são **distintas**: **tipo
runtime incompatível** levanta `TypeError`, **sem** código; **violação de
contrato `E-Nb`** levanta `ValueError` com o respectivo código no **início** da
mensagem. Daí a separação entre **ausência** e **tipo**: confiança ausente onde
ela é exigida é `E-Nb-1` — e `confianca_global` ausente é `E-Nb-4` —, enquanto
uma confiança de **tipo errado** é `TypeError`. **Nenhuma exceção pública nova é
criada** (AJ1).

**Delta AJ2 materializado.** `PerguntaComercial` tem **três** campos — `texto`,
`confianca` e `assunto` —, com `assunto` **obrigatório** do vocabulário fechado
`AssuntoComercial` de **54** valores e **sem confiança própria** (N-b-Q7). A
ampliação de **`E-Nb-5`** cobre assunto **ausente** (AJ2-X1) e **fora do
vocabulário** (AJ2-X2); tipo runtime incompatível continua `TypeError` **sem
código** (M-NB4). **A lista de erros permanece `E-Nb-1`–`E-Nb-19`** e **nenhuma
exceção pública nova é criada**. O `assunto` **não atravessa** para a
`ProjecaoInterpretacao`, **não referencia `Rxx`**, **não participa de N-b-X3** e
**não produz condição** de §4.4 (N-b-Q12): seu consumo pertence a **S2-D8**, que
**continua ARBITRADA / NÃO MATERIALIZADA**. As validações de assunto correm
**depois** das validações N-b/AJ1 preexistentes, preservando a precedência
histórica dos erros.

A **ordem canônica** de `intencoes_detectadas` é **produzida** deterministicamente
por `canonicalizar_interpretacao(...)`, mas **não é exigida** de quem consome:
ela existe apenas para auditabilidade e **não estabelece precedência semântica**
(AJ1-A1e). `E-Nb-6` significa **somente código repetido**.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from casa77_sdr.identity import (
    Confianca,
    IntencaoIdentidade,
    ProjecaoInterpretacao,
    ReferenciaEventoAnterior,
)
from casa77_sdr.qualification import FormatoEvento

__all__ = [
    "IntencaoConversacional",
    "AssuntoComercial",
    "DadosExtraidos",
    "CorrecaoInterpretada",
    "PerguntaComercial",
    "ReferenciaAoEventoAnterior",
    "TrechoAmbiguo",
    "TrechoAmbiguoRecebido",
    "IntencaoAutonomaRecebida",
    "IntencaoDetectada",
    "EntradaInterpretacao",
    "Interpretacao",
    "canonicalizar_interpretacao",
    "projetar_para_identidade",
    "decidir_interesse_confirmar_disponibilidade",
]


class IntencaoConversacional(StrEnum):
    """Vocabulário conceitual **fechado em 11 valores** (N-b-c, N-b-X6).

    A ordem de declaração é a **ordem canônica** de `intencoes_detectadas` e
    existe **apenas para auditabilidade**: ela **não** estabelece precedência
    semântica alguma (AJ1-A1e).

    Partição obrigatória: **A1** — seis códigos **derivados** dos payloads
    autoritativos; **A2** — dois autônomos mapeáveis a evento; **B** — três
    autônomos não mapeáveis diretamente a evento.
    """

    # A1 — derivados (6)
    TIPO_EVENTO_INFORMADO = "tipo_evento_informado"
    DATA_INFORMADA = "data_informada"
    CONVIDADOS_INFORMADOS = "convidados_informados"
    FORMATO_INFORMADO = "formato_informado"
    PERGUNTA_COMERCIAL = "pergunta_comercial"
    PEDIDO_DE_HUMANO = "pedido_de_humano"
    # A2 — autônomos mapeáveis a evento (2)
    INTERESSE_EM_VISITA = "interesse_em_visita"
    EXCECAO_SOLICITADA = "excecao_solicitada"
    # B — autônomos não mapeáveis diretamente a evento (3)
    INTERESSE_CONFIRMAR_DISPONIBILIDADE = "interesse_confirmar_disponibilidade"
    CONTINUIDADE_DE_EVENTO_DECLARADA = "continuidade_de_evento_declarada"
    EVENTO_NOVO_DECLARADO = "evento_novo_declarado"


#: Os seis códigos **A1**, sempre derivados — nunca recebidos (AJ1-1).
_CODIGOS_A1: frozenset[IntencaoConversacional] = frozenset(
    {
        IntencaoConversacional.TIPO_EVENTO_INFORMADO,
        IntencaoConversacional.DATA_INFORMADA,
        IntencaoConversacional.CONVIDADOS_INFORMADOS,
        IntencaoConversacional.FORMATO_INFORMADO,
        IntencaoConversacional.PERGUNTA_COMERCIAL,
        IntencaoConversacional.PEDIDO_DE_HUMANO,
    }
)

#: Vocabulário fechado admissível no **slot de intenções autônomas** (AJ1-3).
_CODIGOS_AUTONOMOS: frozenset[IntencaoConversacional] = frozenset(
    {
        IntencaoConversacional.INTERESSE_EM_VISITA,
        IntencaoConversacional.EXCECAO_SOLICITADA,
        IntencaoConversacional.INTERESSE_CONFIRMAR_DISPONIBILIDADE,
        IntencaoConversacional.CONTINUIDADE_DE_EVENTO_DECLARADA,
        IntencaoConversacional.EVENTO_NOVO_DECLARADO,
    }
)


class AssuntoComercial(StrEnum):
    """Vocabulário conceitual **fechado em 54 valores** (AJ2, N-b-Q7).

    **53 assuntos específicos + `ASSUNTO_NAO_CLASSIFICADO`**, o membro de
    **totalidade**. **Nenhum 55º valor** pode ser acrescentado, e nenhum alias
    existe. A ordem de declaração é a **ordem documental** de `docs/07` §6.3.

    São **categorias semânticas**, não valores comerciais: nenhum membro carrega
    preço, capacidade, horário, prazo, condição, endereço ou texto de resposta —
    é o que torna `E-Nb-19` estruturalmente inviolável por este enum.

    **`ASSUNTO_NAO_CLASSIFICADO` é valor legítimo de totalidade** (AJ2-N1): não é
    erro, não é confiança `BAIXA`, não é ausência e não é `TrechoAmbiguo`
    (AJ2-N2–AJ2-N5). **Nunca escolher "o mais próximo"** — aproximar é fabricar
    classificação (N-b-Q10). O que se faz com ele a jusante pertence a **S2-D8**,
    que **continua ARBITRADA / NÃO MATERIALIZADA** (AJ2-C4).
    """

    # Preço e condição comercial (12)
    PRECO_LOCACAO = "preco_locacao"
    PRECO_HORA_ADICIONAL = "preco_hora_adicional"
    PRECO_VARIACAO_POR_DIA_DA_SEMANA = "preco_variacao_por_dia_da_semana"
    PRECO_VARIACAO_POR_TEMPORADA = "preco_variacao_por_temporada"
    PRECO_SUITE_DA_NOIVA = "preco_suite_da_noiva"
    DESCONTO = "desconto"
    PAGAMENTO_E_PARCELAMENTO = "pagamento_e_parcelamento"
    CAUCAO = "caucao"
    VALIDADE_DA_PROPOSTA = "validade_da_proposta"
    REAJUSTE_DE_PRECO = "reajuste_de_preco"
    PARCERIA_OU_PERMUTA = "parceria_ou_permuta"
    MULTAS_E_PENALIDADES = "multas_e_penalidades"
    # Evento, data e contratação (10)
    TIPO_DE_EVENTO = "tipo_de_evento"
    DATA_BLOQUEADA = "data_bloqueada"
    DISPONIBILIDADE_DE_DATA = "disponibilidade_de_data"
    CAPACIDADE_MAXIMA_E_FORMATO = "capacidade_maxima_e_formato"
    CAPACIDADE_MINIMA = "capacidade_minima"
    HORARIO_LIMITE_E_DURACAO = "horario_limite_e_duracao"
    MONTAGEM_E_DESMONTAGEM = "montagem_e_desmontagem"
    CONTRATACAO = "contratacao"
    CANCELAMENTO = "cancelamento"
    ALTERACAO_DE_DATA = "alteracao_de_data"
    # Espaço e estrutura (12)
    LOCALIZACAO = "localizacao"
    ESTACIONAMENTO = "estacionamento"
    ACESSIBILIDADE = "acessibilidade"
    BANHEIROS = "banheiros"
    COZINHA = "cozinha"
    SUITE_DA_NOIVA = "suite_da_noiva"
    MOBILIARIO = "mobiliario"
    CLIMATIZACAO = "climatizacao"
    ESPACO_INFANTIL = "espaco_infantil"
    COBERTURA_E_PLANO_DE_CHUVA = "cobertura_e_plano_de_chuva"
    SOM_E_ILUMINACAO = "som_e_iluminacao"
    GERADOR_E_ENERGIA = "gerador_e_energia"
    # Inclusão, fornecedor e restrição (10)
    ITENS_INCLUSOS = "itens_inclusos"
    EQUIPE_E_LIMPEZA = "equipe_e_limpeza"
    FORNECEDOR_PROPRIO = "fornecedor_proprio"
    FORNECEDOR_RECOMENDADO = "fornecedor_recomendado"
    RESTRICAO_USO_DE_AREA = "restricao_uso_de_area"
    RESTRICAO_FOGOS = "restricao_fogos"
    RESTRICAO_ANIMAIS = "restricao_animais"
    RESTRICAO_VELAS = "restricao_velas"
    RESTRICAO_DRONES = "restricao_drones"
    RESTRICAO_DECORACAO = "restricao_decoracao"
    # Processo, prazo e material (9)
    VISITA = "visita"
    PRAZO_DE_RETORNO = "prazo_de_retorno"
    HORARIO_DE_ATENDIMENTO = "horario_de_atendimento"
    MATERIAL_FOTOS = "material_fotos"
    MATERIAL_VIDEOS = "material_videos"
    MATERIAL_PLANTA = "material_planta"
    MATERIAL_PORTFOLIO = "material_portfolio"
    MATERIAL_APRESENTACAO_COMERCIAL = "material_apresentacao_comercial"
    LINK_DE_MAPA = "link_de_mapa"
    # Totalidade (1)
    ASSUNTO_NAO_CLASSIFICADO = "assunto_nao_classificado"


#: Os **seis** campos de `dados_extraidos` (N-b-D1), na ordem do contrato.
_CAMPOS_DADOS: tuple[str, ...] = (
    "tipo_evento",
    "data_nomeada",
    "convidados",
    "formato",
    "nome",
    "contato",
)

#: Pares **A–D** e **E–F** da bi-implicação: payload ⟺ código derivado (N-b-X4).
_A1_POR_CAMPO: dict[str, IntencaoConversacional] = {
    "tipo_evento": IntencaoConversacional.TIPO_EVENTO_INFORMADO,
    "data_nomeada": IntencaoConversacional.DATA_INFORMADA,
    "convidados": IntencaoConversacional.CONVIDADOS_INFORMADOS,
    "formato": IntencaoConversacional.FORMATO_INFORMADO,
}


def _erro(codigo: str, detalhe: str) -> ValueError:
    """Erro de contrato da fronteira, sempre prefixado pelo código `E-Nb-*`."""
    return ValueError(f"{codigo}: {detalhe}")


@dataclass(frozen=True)
class DadosExtraidos:
    """Os **seis** dados extraídos, cada um com sua confiança (N-b-D1–N-b-D7).

    Campo **presente** exige confiança `ALTA` | `BAIXA`; campo **ausente** tem
    confiança obrigatoriamente `None`. `tipo_evento` e `data_nomeada` são
    **texto nominal** — sem sinônimo, sem categoria comercial e **sem parsing de
    calendário**. `nome` e `contato` são **PII de runtime**: existem aqui e
    **nunca** atravessam para a `ProjecaoInterpretacao` (N-b-K8).
    """

    tipo_evento: str | None = None
    confianca_tipo_evento: Confianca | None = None
    data_nomeada: str | None = None
    confianca_data_nomeada: Confianca | None = None
    convidados: int | None = None
    confianca_convidados: Confianca | None = None
    formato: FormatoEvento | None = None
    confianca_formato: Confianca | None = None
    nome: str | None = None
    confianca_nome: Confianca | None = None
    contato: str | None = None
    confianca_contato: Confianca | None = None

    def _valor(self, campo: str) -> object:
        return getattr(self, campo)

    def _confianca(self, campo: str) -> Confianca | None:
        return getattr(self, f"confianca_{campo}")


@dataclass(frozen=True)
class CorrecaoInterpretada:
    """Retificação **explicitamente declarada** pelo interessado (N-b-C1–N-b-C5).

    Tem **três** campos e **não** carrega o valor anterior (N-b-C3): o valor
    anterior vive no contexto recuperado, que esta fronteira **não** lê.
    """

    campo: str
    valor_novo: str | int | FormatoEvento | None
    confianca: Confianca | None


@dataclass(frozen=True)
class PerguntaComercial:
    """Consulta comercial identificada — **três** campos (N-b-Q1, N-b-Q7).

    `texto` e `confianca` vêm de N-b; `assunto` é a extensão **AJ2**. O assunto é
    **obrigatório** numa interpretação válida, pertence ao enum fechado
    `AssuntoComercial` e **não possui confiança própria** — `N-b-Q2`/`N-b-Q3`
    permanecem o **filtro único** de efetividade (N-b-Q7).

    `assunto = None` representa **ausência recebida**, para que `AJ2-X1` seja
    verificável na fronteira; ela é rejeitada como `E-Nb-5`. **Exatamente um
    assunto por item** (N-b-Q8): a consulta **composta** deve chegar **já
    segmentada pelo futuro produtor semântico** em múltiplas `PerguntaComercial`,
    uma por assunto. **Este módulo não segmenta texto livre**: ele apenas
    **recebe** a representação já segmentada, **exige** um assunto por item,
    **valida** os assuntos e **preserva** cada item como recebido. O `texto` é
    **preservado literalmente** — sem `strip`, normalização, resumo ou paráfrase
    (N-b-Q9) — e **duplicatas exatas são permitidas**, sem `id`, posição,
    *offset* ou contador (N-b-Q11).

    O `assunto` **não atravessa** para a `ProjecaoInterpretacao`, **não referencia
    `Rxx`**, **não seleciona fragmento** e **não produz condição** de §4.4
    (N-b-Q12).
    """

    texto: str | None
    confianca: Confianca | None
    assunto: AssuntoComercial | None


@dataclass(frozen=True)
class ReferenciaAoEventoAnterior:
    """Menção que indica continuidade — `texto` e `confianca` (N-b-R1)."""

    texto: str | None
    confianca: Confianca | None


@dataclass(frozen=True)
class TrechoAmbiguo:
    """Trecho ambíguo **canônico**: um único campo, `texto`. **Sem confiança**.

    Declarar confiança para um trecho ambíguo é `E-Nb-3` (N-b-G6b, N-b-T5) — por
    isso a estrutura canônica sequer possui o campo. Função **exclusivamente
    diagnóstica**: não altera identidade, qualificação, evento nem bloqueio
    (N-b-T2) e **não** entra na projeção (N-b-T3).
    """

    texto: str


@dataclass(frozen=True)
class TrechoAmbiguoRecebido:
    """Trecho ambíguo **como recebido**, antes da canonicalização.

    Existe **somente** para tornar `E-Nb-3` verificável na fronteira: se o
    produtor tentar declarar `confianca`, a entrada é rejeitada e **nenhuma**
    `Interpretacao` canônica é produzida. O objeto canônico correspondente,
    `TrechoAmbiguo`, **não** possui confiança.
    """

    texto: str | None
    confianca: Confianca | None = None


@dataclass(frozen=True)
class IntencaoAutonomaRecebida:
    """Intenção **autônoma** como recebida do produtor não determinístico.

    O slot aceita **exatamente** os cinco códigos **A2/B** (AJ1-3). Apresentar
    um código **A1** aqui é rejeitado: **com** confiança declarada → `E-Nb-3`;
    **sem** confiança → `E-Nb-5` (AJ1, casos A e B). Isso **não** torna `A1`
    entrada válida — ambos bloqueiam antes da canonicalização.
    """

    codigo: IntencaoConversacional
    confianca: Confianca | None


@dataclass(frozen=True)
class IntencaoDetectada:
    """Item de `intencoes_detectadas` na `Interpretacao` canônica.

    Para os códigos **A1** a confiança é **calculada** por N-b-X3 e apenas
    **armazenada** para auditabilidade (AJ1-A1b, AJ1-A1c); para os autônomos
    **A2/B** é a confiança declarada, obrigatória quando presentes (N-b-G6).
    """

    codigo: IntencaoConversacional
    confianca: Confianca


@dataclass(frozen=True)
class EntradaInterpretacao:
    """Entrada **pré-canônica** da fronteira da etapa 4.

    Representa **o que o produtor não determinístico entrega** (AJ1-2) — e
    **somente** isso. Não existe aqui slot de códigos **A1**: eles são derivados
    (AJ1-1). Não é uma segunda `Interpretacao`, não é formato de transporte e
    **nenhum** formato de transporte é escolhido por este módulo (N-b-F3).
    """

    dados_extraidos: DadosExtraidos
    correcoes: tuple[CorrecaoInterpretada, ...]
    perguntas_comerciais: tuple[PerguntaComercial, ...]
    pedido_de_humano: bool
    confianca_pedido_de_humano: Confianca | None
    referencias_evento_anterior: tuple[ReferenciaAoEventoAnterior, ...]
    trechos_ambiguos: tuple[TrechoAmbiguoRecebido, ...]
    confianca_global: Confianca | None
    intencoes_autonomas: tuple[IntencaoAutonomaRecebida, ...]


@dataclass(frozen=True)
class Interpretacao:
    """A `Interpretacao` **canônica** — as **oito** categorias de §6.3.

    A categoria 5 é representada por dois campos, `pedido_de_humano` e
    `confianca_pedido_de_humano` (N-b-PH1). `intencoes_detectadas` contém os
    **A1 derivados** mais as **A2/B autônomas**, **sem repetição** e em **ordem
    canônica** apenas para auditabilidade (AJ1-A1d, AJ1-A1e).

    A `Interpretacao` **relata o que foi lido** (N-b-G1): não classifica
    compatibilidade, não decide handoff, não resolve identidade, não qualifica e
    não consulta a base.
    """

    intencoes_detectadas: tuple[IntencaoDetectada, ...]
    dados_extraidos: DadosExtraidos
    correcoes: tuple[CorrecaoInterpretada, ...]
    perguntas_comerciais: tuple[PerguntaComercial, ...]
    pedido_de_humano: bool
    confianca_pedido_de_humano: Confianca | None
    referencias_evento_anterior: tuple[ReferenciaAoEventoAnterior, ...]
    confianca_global: Confianca
    trechos_ambiguos: tuple[TrechoAmbiguo, ...]

    def _confianca_de(self, codigo: IntencaoConversacional) -> Confianca | None:
        for item in self.intencoes_detectadas:
            if item.codigo is codigo:
                return item.confianca
        return None


# --------------------------------------------------------------------------
# Validação de tipos — tipo runtime incompatível é TypeError, nunca negócio
# --------------------------------------------------------------------------


def _validar_tipos(entrada: object) -> EntradaInterpretacao:
    if not isinstance(entrada, EntradaInterpretacao):
        raise TypeError("entrada precisa ser uma EntradaInterpretacao")
    if not isinstance(entrada.dados_extraidos, DadosExtraidos):
        raise TypeError("dados_extraidos precisa ser um DadosExtraidos")
    _validar_colecao(entrada.correcoes, CorrecaoInterpretada, "correcoes")
    _validar_colecao(
        entrada.perguntas_comerciais, PerguntaComercial, "perguntas_comerciais"
    )
    _validar_colecao(
        entrada.referencias_evento_anterior,
        ReferenciaAoEventoAnterior,
        "referencias_evento_anterior",
    )
    _validar_colecao(
        entrada.trechos_ambiguos, TrechoAmbiguoRecebido, "trechos_ambiguos"
    )
    _validar_colecao(
        entrada.intencoes_autonomas, IntencaoAutonomaRecebida, "intencoes_autonomas"
    )
    if not isinstance(entrada.pedido_de_humano, bool):
        raise TypeError("pedido_de_humano precisa ser booleano")
    if entrada.confianca_pedido_de_humano is not None and not isinstance(
        entrada.confianca_pedido_de_humano, Confianca
    ):
        raise TypeError("confianca_pedido_de_humano precisa ser Confianca ou None")
    if entrada.confianca_global is not None and not isinstance(
        entrada.confianca_global, Confianca
    ):
        raise TypeError("confianca_global precisa ser Confianca ou None")
    return entrada


def _validar_colecao(valor: object, tipo: type, nome: str) -> None:
    if not isinstance(valor, tuple):
        raise TypeError(f"{nome} precisa ser uma tupla")
    for item in valor:
        if not isinstance(item, tipo):
            raise TypeError(f"cada item de {nome} precisa ser um {tipo.__name__}")


# --------------------------------------------------------------------------
# Erros de contrato recebíveis — provocáveis pela entrada realmente recebida
# --------------------------------------------------------------------------


def _texto_em_branco(texto: str) -> bool:
    return texto.strip() == ""


def _validar_confianca_global(entrada: EntradaInterpretacao) -> Confianca:
    """E-Nb-4 — `confianca_global` está **sempre presente** (N-b-CG1)."""
    if entrada.confianca_global is None:
        raise _erro("E-Nb-4", "confianca_global é obrigatória")
    return entrada.confianca_global


def _validar_dados_extraidos(dados: DadosExtraidos) -> None:
    """E-Nb-1, E-Nb-3, E-Nb-5, E-Nb-8 e E-Nb-9 sobre os seis campos."""
    for campo in _CAMPOS_DADOS:
        valor = dados._valor(campo)
        confianca = dados._confianca(campo)
        if valor is None:
            if confianca is not None:
                raise _erro(
                    "E-Nb-3",
                    f"confiança declarada para o campo ausente {campo!r}",
                )
            continue
        if confianca is None:
            raise _erro("E-Nb-1", f"campo {campo!r} presente sem confiança declarada")
        if not isinstance(confianca, Confianca):
            raise TypeError(f"confianca_{campo} precisa ser Confianca ou None")

    _validar_texto_nominal(dados.tipo_evento, "tipo_evento")
    _validar_texto_nominal(dados.data_nomeada, "data_nomeada")
    _validar_texto_nominal(dados.nome, "nome")
    _validar_texto_nominal(dados.contato, "contato")
    _validar_convidados(dados.convidados)
    _validar_formato(dados.formato)


def _validar_texto_nominal(valor: object, campo: str) -> None:
    """Domínio textual dos dados extraídos: `str | None`, e nada além disso.

    **`E-Nb-10` não se aplica aqui.** O contrato o define exclusivamente para
    `PerguntaComercial`, `ReferenciaAoEventoAnterior` e `TrechoAmbiguo`
    (K-Nb-12); ampliá-lo aos dados extraídos exigiria arbitragem. O valor é
    **preservado nominalmente como recebido** — sem `strip`, sem normalização e
    sem converter texto em branco para `None` (N-b-D2, N-b-D3).
    """
    if valor is None:
        return
    if not isinstance(valor, str):
        raise TypeError(f"{campo} precisa ser texto ou None")


def _validar_convidados(valor: object) -> None:
    """E-Nb-8 — inteiro **não negativo**; `bool` é inválido (N-b-D4)."""
    if valor is None:
        return
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise _erro("E-Nb-8", "convidados precisa ser inteiro não negativo, nunca bool")
    if valor < 0:
        raise _erro("E-Nb-8", "convidados não pode ser negativo")


def _validar_formato(valor: object) -> None:
    """E-Nb-9 fora de `sentado`|`coquetel`; E-Nb-5 se o valor é de outro domínio."""
    if valor is None or isinstance(valor, FormatoEvento):
        return
    if isinstance(valor, str):
        raise _erro("E-Nb-9", "formato precisa ser sentado ou coquetel")
    raise _erro("E-Nb-5", "formato recebeu valor fora do vocabulário fechado")


def _validar_pedido_de_humano(
    pedido_de_humano: bool, confianca: Confianca | None
) -> None:
    """E-Nb-1 e E-Nb-3 sobre a categoria 5 (N-b-PH1)."""
    if pedido_de_humano:
        if confianca is None:
            raise _erro(
                "E-Nb-1", "pedido_de_humano verdadeiro exige confiança declarada"
            )
        return
    if confianca is not None:
        raise _erro(
            "E-Nb-3", "pedido_de_humano falso não admite confiança declarada"
        )


def _validar_itens_com_texto(
    itens: tuple[PerguntaComercial, ...] | tuple[ReferenciaAoEventoAnterior, ...],
    nome: str,
) -> None:
    """E-Nb-10, E-Nb-2 e E-Nb-1 sobre perguntas e referências (0..N)."""
    for item in itens:
        if item.texto is None:
            if item.confianca is not None:
                raise _erro(
                    "E-Nb-2", f"confiança declarada sem valor correspondente em {nome}"
                )
            raise _erro("E-Nb-10", f"item de {nome} sem texto")
        if not isinstance(item.texto, str):
            raise TypeError(f"o texto de {nome} precisa ser texto")
        if _texto_em_branco(item.texto):
            raise _erro("E-Nb-10", f"texto vazio ou em branco em {nome}")
        if item.confianca is None:
            raise _erro("E-Nb-1", f"item de {nome} presente sem confiança declarada")
        if not isinstance(item.confianca, Confianca):
            raise TypeError(f"a confiança de {nome} precisa ser Confianca")


def _validar_assuntos(perguntas: tuple[PerguntaComercial, ...]) -> None:
    """`AJ2-X1` e `AJ2-X2` — ampliação **já arbitrada** de `E-Nb-5`.

    **A lista de erros continua `E-Nb-1`–`E-Nb-19`**: nenhum vigésimo código é
    criado (AJ2). As duas famílias vigentes são preservadas conforme **M-NB4**:

    * `assunto` **ausente** (`None`) → `E-Nb-5` (AJ2-X1, K-Nb-43);
    * `assunto` **fora do vocabulário** `AssuntoComercial` → `E-Nb-5`
      (AJ2-X2, K-Nb-42);
    * `assunto` com **tipo runtime incompatível** → `TypeError`, **sem código**
      (K-Nb-44);
    * `ASSUNTO_NAO_CLASSIFICADO` → **válido** (AJ2-N1, K-Nb-45).

    **Precedência preservada (D-AJ2-2).** Esta validação é chamada **depois** de
    todas as validações e pós-condições N-b/AJ1 preexistentes — por isso ela
    **não** vive em `_validar_tipos` nem em `_validar_itens_com_texto`. Quando uma
    entrada viola simultaneamente uma regra antiga e a regra AJ2, **a regra antiga
    prevalece**: texto ausente/vazio continua `E-Nb-10`, confiança sem valor
    continua `E-Nb-2`, valor sem confiança continua `E-Nb-1` e tipo incompatível de
    texto ou confiança continua `TypeError`.

    O assunto **não participa de N-b-X3**: a agregação de `PERGUNTA_COMERCIAL`
    continua dependendo **somente** das confianças (N-b-Q6, N-b-Q7).
    """
    for pergunta in perguntas:
        assunto = pergunta.assunto
        if assunto is None:
            raise _erro(
                "E-Nb-5", "PerguntaComercial sem assunto — o assunto é obrigatório"
            )
        if isinstance(assunto, AssuntoComercial):
            continue
        if isinstance(assunto, str):
            raise _erro(
                "E-Nb-5",
                f"assunto {assunto!r} fora do vocabulário fechado AssuntoComercial",
            )
        raise TypeError(
            "o assunto da pergunta comercial precisa ser AssuntoComercial ou None"
        )


def _validar_trechos_ambiguos(
    trechos: tuple[TrechoAmbiguoRecebido, ...],
) -> tuple[TrechoAmbiguo, ...]:
    """E-Nb-3 antes de E-Nb-10: declarar confiança aqui é proibido (N-b-T5)."""
    canonicos: list[TrechoAmbiguo] = []
    for trecho in trechos:
        if trecho.confianca is not None:
            raise _erro(
                "E-Nb-3", "trecho ambíguo não admite confiança declarada"
            )
        if trecho.texto is None:
            raise _erro("E-Nb-10", "trecho ambíguo sem texto")
        if not isinstance(trecho.texto, str):
            raise TypeError("o texto do trecho ambíguo precisa ser texto")
        if _texto_em_branco(trecho.texto):
            raise _erro("E-Nb-10", "texto vazio ou em branco em trecho ambíguo")
        canonicos.append(TrechoAmbiguo(texto=trecho.texto))
    return tuple(canonicos)


def _validar_correcoes(
    correcoes: tuple[CorrecaoInterpretada, ...], dados: DadosExtraidos
) -> None:
    """E-Nb-5, E-Nb-7 e E-Nb-17 (N-b-C1, N-b-C4)."""
    vistos: set[str] = set()
    for correcao in correcoes:
        if not isinstance(correcao.campo, str):
            raise TypeError("o campo da correção precisa ser texto")
        if correcao.campo not in _CAMPOS_DADOS:
            raise _erro(
                "E-Nb-5",
                f"identificador de campo {correcao.campo!r} fora do vocabulário fechado",
            )
        if correcao.campo in vistos:
            raise _erro("E-Nb-7", f"campo {correcao.campo!r} repetido em correcoes")
        vistos.add(correcao.campo)

        if correcao.confianca is None:
            raise _erro(
                "E-Nb-1", f"correção de {correcao.campo!r} sem confiança declarada"
            )
        if not isinstance(correcao.confianca, Confianca):
            raise TypeError("a confiança da correção precisa ser Confianca")

        # N-b-G6c: confiança declarada **sem valor correspondente** é E-Nb-2, e
        # isso precede a comparação de C4 — não é divergência (E-Nb-17), é
        # ausência do próprio valor.
        if correcao.valor_novo is None:
            raise _erro(
                "E-Nb-2",
                f"correção de {correcao.campo!r} declara confiança sem valor_novo",
            )

        valor_no_payload = dados._valor(correcao.campo)
        if valor_no_payload is None:
            raise _erro(
                "E-Nb-17",
                f"correção de {correcao.campo!r} ausente de dados_extraidos",
            )
        if not _mesmo_valor(valor_no_payload, correcao.valor_novo):
            raise _erro(
                "E-Nb-17", f"correção de {correcao.campo!r} com valor divergente"
            )
        if dados._confianca(correcao.campo) is not correcao.confianca:
            raise _erro(
                "E-Nb-17", f"correção de {correcao.campo!r} com confiança divergente"
            )


def _mesmo_valor(esquerda: object, direita: object) -> bool:
    """Igualdade estrita de domínio: `bool` nunca equivale a `int` (N-b-D4)."""
    if isinstance(esquerda, bool) is not isinstance(direita, bool):
        return False
    return type(esquerda) is type(direita) and esquerda == direita


def _validar_intencoes_autonomas(
    intencoes: tuple[IntencaoAutonomaRecebida, ...],
) -> tuple[IntencaoDetectada, ...]:
    """E-Nb-3 × E-Nb-5, E-Nb-1, E-Nb-6 e E-Nb-18 no slot autônomo (AJ1-3)."""
    vistos: set[IntencaoConversacional] = set()
    validadas: list[IntencaoDetectada] = []
    for intencao in intencoes:
        codigo = intencao.codigo
        if not isinstance(codigo, IntencaoConversacional):
            raise _erro(
                "E-Nb-5", "código fora do vocabulário fechado IntencaoConversacional"
            )
        if codigo in _CODIGOS_A1:
            # AJ1, precedência: com confiança declarada, E-Nb-3 prevalece —
            # é tentativa explícita de declarar confiança em intenção derivada,
            # o que N-b-G6b proíbe. Sem confiança, o valor está apenas fora do
            # vocabulário fechado admissível naquele slot: E-Nb-5.
            if intencao.confianca is not None:
                raise _erro(
                    "E-Nb-3",
                    f"confiança declarada para a intenção derivada {codigo.name}",
                )
            raise _erro(
                "E-Nb-5",
                f"{codigo.name} é derivado e não pertence ao slot autônomo",
            )
        if codigo not in _CODIGOS_AUTONOMOS:  # pragma: no cover - partição exaustiva
            raise _erro("E-Nb-5", f"{codigo.name} não pertence ao slot autônomo")
        if intencao.confianca is None:
            raise _erro(
                "E-Nb-1", f"intenção autônoma {codigo.name} sem confiança declarada"
            )
        if not isinstance(intencao.confianca, Confianca):
            raise TypeError("a confiança da intenção autônoma precisa ser Confianca")
        if codigo in vistos:
            raise _erro("E-Nb-6", f"intenção autônoma {codigo.name} repetida")
        vistos.add(codigo)
        validadas.append(IntencaoDetectada(codigo=codigo, confianca=intencao.confianca))

    if (
        IntencaoConversacional.CONTINUIDADE_DE_EVENTO_DECLARADA in vistos
        and IntencaoConversacional.EVENTO_NOVO_DECLARADO in vistos
    ):
        raise _erro(
            "E-Nb-18",
            "CONTINUIDADE_DE_EVENTO_DECLARADA e EVENTO_NOVO_DECLARADO são "
            "mutuamente exclusivas",
        )
    return tuple(validadas)


# --------------------------------------------------------------------------
# Derivação dos seis códigos A1 — presença pelo payload, confiança por N-b-X3
# --------------------------------------------------------------------------


def _agregar(confiancas: tuple[Confianca, ...]) -> Confianca:
    """N-b-X3 para payload 0..N: ao menos uma `ALTA` → `ALTA`; senão `BAIXA`."""
    return Confianca.ALTA if Confianca.ALTA in confiancas else Confianca.BAIXA


def _derivar_a1(
    dados: DadosExtraidos,
    perguntas: tuple[PerguntaComercial, ...],
    pedido_de_humano: bool,
    confianca_pedido_de_humano: Confianca | None,
) -> tuple[IntencaoDetectada, ...]:
    """A presença depende **somente** do payload (N-b-X2); a confiança é calculada."""
    derivados: list[IntencaoDetectada] = []
    for campo, codigo in _A1_POR_CAMPO.items():
        if dados._valor(campo) is None:
            continue
        # Confiança garantida não nula por `_validar_dados_extraidos` (E-Nb-1).
        confianca = dados._confianca(campo)
        if confianca is None:  # pragma: no cover - impossível após a validação
            raise _erro("E-Nb-1", f"campo {campo!r} presente sem confiança declarada")
        derivados.append(IntencaoDetectada(codigo=codigo, confianca=confianca))

    if perguntas:
        derivados.append(
            IntencaoDetectada(
                codigo=IntencaoConversacional.PERGUNTA_COMERCIAL,
                confianca=_agregar(
                    tuple(p.confianca for p in perguntas if p.confianca is not None)
                ),
            )
        )

    if pedido_de_humano and confianca_pedido_de_humano is not None:
        derivados.append(
            IntencaoDetectada(
                codigo=IntencaoConversacional.PEDIDO_DE_HUMANO,
                confianca=confianca_pedido_de_humano,
            )
        )
    return tuple(derivados)


def _ordenar_canonicamente(
    itens: tuple[IntencaoDetectada, ...],
) -> tuple[IntencaoDetectada, ...]:
    """Ordem de declaração do enum — **apenas** para auditabilidade (AJ1-A1e)."""
    posicao = {codigo: indice for indice, codigo in enumerate(IntencaoConversacional)}
    return tuple(sorted(itens, key=lambda item: posicao[item.codigo]))


# --------------------------------------------------------------------------
# Pós-condições — invariantes internos da canonicalização (program error)
# --------------------------------------------------------------------------


def _verificar_pos_condicoes(interpretacao: Interpretacao) -> None:
    """E-Nb-6 (ramo A1) e E-Nb-11–E-Nb-16 (AJ1).

    São **invariantes internos**, não erros recebíveis: numa canonicalização
    correta eles são **impossíveis por construção**. A verificação existe para
    que a propriedade seja demonstrável, não para transformar entrada externa em
    E-Nb-13 — nenhuma confiança **A1** independente é aceita (AJ1-13c).
    """
    codigos = [item.codigo for item in interpretacao.intencoes_detectadas]
    if len(codigos) != len(set(codigos)):
        raise _erro("E-Nb-6", "invariante interno: código repetido em intencoes_detectadas")

    presentes = set(codigos)
    dados = interpretacao.dados_extraidos

    for campo, codigo in _A1_POR_CAMPO.items():
        tem_payload = dados._valor(campo) is not None
        tem_codigo = codigo in presentes
        if tem_payload and not tem_codigo:
            raise _erro("E-Nb-11", f"invariante interno: {campo} sem o código derivado")
        if tem_codigo and not tem_payload:
            raise _erro("E-Nb-12", f"invariante interno: {codigo.name} sem o payload")
        if tem_payload and interpretacao._confianca_de(codigo) is not dados._confianca(
            campo
        ):
            raise _erro(
                "E-Nb-13",
                f"invariante interno: confiança de {codigo.name} divergente do payload",
            )

    tem_perguntas = bool(interpretacao.perguntas_comerciais)
    tem_codigo_pergunta = IntencaoConversacional.PERGUNTA_COMERCIAL in presentes
    if tem_perguntas and not tem_codigo_pergunta:
        raise _erro(
            "E-Nb-14", "invariante interno: perguntas não vazias sem PERGUNTA_COMERCIAL"
        )
    if tem_codigo_pergunta and not tem_perguntas:
        raise _erro(
            "E-Nb-15", "invariante interno: PERGUNTA_COMERCIAL com coleção vazia"
        )
    if tem_perguntas:
        esperada = _agregar(
            tuple(
                p.confianca
                for p in interpretacao.perguntas_comerciais
                if p.confianca is not None
            )
        )
        if (
            interpretacao._confianca_de(IntencaoConversacional.PERGUNTA_COMERCIAL)
            is not esperada
        ):
            raise _erro(
                "E-Nb-13",
                "invariante interno: confiança de PERGUNTA_COMERCIAL divergente da "
                "agregação de N-b-X3",
            )

    tem_codigo_humano = IntencaoConversacional.PEDIDO_DE_HUMANO in presentes
    if interpretacao.pedido_de_humano != tem_codigo_humano:
        raise _erro(
            "E-Nb-16",
            "invariante interno: pedido_de_humano e PEDIDO_DE_HUMANO divergentes",
        )
    if interpretacao.pedido_de_humano and (
        interpretacao._confianca_de(IntencaoConversacional.PEDIDO_DE_HUMANO)
        is not interpretacao.confianca_pedido_de_humano
    ):
        raise _erro(
            "E-Nb-13",
            "invariante interno: confiança de PEDIDO_DE_HUMANO divergente do payload",
        )


def _validar_interpretacao_canonica(interpretacao: object) -> Interpretacao:
    """Verifica que a `Interpretacao` recebida é **canônica válida**.

    `Interpretacao` é uma estrutura pública e pode ser construída diretamente.
    `isinstance` prova apenas o tipo, **não** a validade — e uma instância
    inválida jamais pode produzir projeção ou condição derivada (AJ1, N-b-M2).
    Os consumidores exigem, portanto, **validade estrutural**, não proveniência:
    uma `Interpretacao` montada à mão que satisfaça o contrato é aceita; não
    existe token de fábrica, sentinela nem marca de origem.

    Reaplica as regras recebíveis sobre o conteúdo já canônico e as
    pós-condições de derivação, mais o que só é verificável sobre a forma
    canônica: tipos dos itens de `intencoes_detectadas`, vocabulário do slot
    autônomo e exclusão mútua **E-Nb-18**.

    **A ordem não é exigida**: ela é apenas de auditoria (AJ1-A1e). Duas
    permutações de um mesmo conjunto válido são igualmente aceitas e produzem
    resultados idênticos.

    :raises TypeError: tipo runtime incompatível.
    :raises ValueError: erro de contrato `E-Nb-*`, com o código na mensagem.
    """
    if not isinstance(interpretacao, Interpretacao):
        raise TypeError("é exigida uma Interpretacao canônica")

    if not isinstance(interpretacao.dados_extraidos, DadosExtraidos):
        raise TypeError("dados_extraidos precisa ser um DadosExtraidos")
    _validar_colecao(interpretacao.correcoes, CorrecaoInterpretada, "correcoes")
    _validar_colecao(
        interpretacao.perguntas_comerciais, PerguntaComercial, "perguntas_comerciais"
    )
    _validar_colecao(
        interpretacao.referencias_evento_anterior,
        ReferenciaAoEventoAnterior,
        "referencias_evento_anterior",
    )
    _validar_colecao(interpretacao.trechos_ambiguos, TrechoAmbiguo, "trechos_ambiguos")
    _validar_colecao(
        interpretacao.intencoes_detectadas, IntencaoDetectada, "intencoes_detectadas"
    )
    if not isinstance(interpretacao.pedido_de_humano, bool):
        raise TypeError("pedido_de_humano precisa ser booleano")
    if interpretacao.confianca_pedido_de_humano is not None and not isinstance(
        interpretacao.confianca_pedido_de_humano, Confianca
    ):
        raise TypeError("confianca_pedido_de_humano precisa ser Confianca ou None")
    # Ausência é erro de contrato (E-Nb-4, N-b-CG1); tipo errado é erro de programa.
    if interpretacao.confianca_global is None:
        raise _erro("E-Nb-4", "confianca_global é obrigatória")
    if not isinstance(interpretacao.confianca_global, Confianca):
        raise TypeError("confianca_global precisa ser Confianca")

    _validar_dados_extraidos(interpretacao.dados_extraidos)
    _validar_pedido_de_humano(
        interpretacao.pedido_de_humano, interpretacao.confianca_pedido_de_humano
    )
    _validar_itens_com_texto(
        interpretacao.perguntas_comerciais, "perguntas_comerciais"
    )
    _validar_itens_com_texto(
        interpretacao.referencias_evento_anterior, "referencias_evento_anterior"
    )
    _validar_trechos_canonicos(interpretacao.trechos_ambiguos)
    _validar_correcoes(interpretacao.correcoes, interpretacao.dados_extraidos)
    _validar_codigos_detectados(interpretacao.intencoes_detectadas)
    _verificar_pos_condicoes(interpretacao)
    # AJ2 por último, pelo mesmo motivo de D-AJ2-2: uma `Interpretacao` construída
    # diretamente também é rejeitada quando o assunto viola o contrato, e sem
    # alterar a ordem histórica das validações anteriores.
    _validar_assuntos(interpretacao.perguntas_comerciais)
    return interpretacao


def _validar_trechos_canonicos(trechos: tuple[TrechoAmbiguo, ...]) -> None:
    """O trecho canônico tem **um** campo e ele não pode ser vazio (E-Nb-10)."""
    for trecho in trechos:
        if not isinstance(trecho.texto, str):
            raise TypeError("o texto do trecho ambíguo precisa ser texto")
        if _texto_em_branco(trecho.texto):
            raise _erro("E-Nb-10", "texto vazio ou em branco em trecho ambíguo")


def _validar_codigos_detectados(
    detectadas: tuple[IntencaoDetectada, ...],
) -> None:
    """Vocabulário, confiança e exclusão mútua.

    **A ordem NÃO é validada.** A ordem canônica existe **apenas para
    auditabilidade** e **não estabelece precedência semântica** (AJ1-A1e):
    exigi-la de quem apenas consome seria transformá-la em regra semântica.
    `canonicalizar_interpretacao(...)` continua **produzindo** a ordem canônica
    de forma determinística; os consumidores aceitam qualquer permutação de um
    conjunto semanticamente válido e produzem o mesmo resultado.

    **`E-Nb-6` significa somente código repetido** — verificado em
    `_verificar_pos_condicoes`, junto dos demais invariantes.
    """
    for item in detectadas:
        if not isinstance(item.codigo, IntencaoConversacional):
            raise _erro(
                "E-Nb-5", "código fora do vocabulário fechado IntencaoConversacional"
            )
        if item.confianca is None:
            raise _erro(
                "E-Nb-1", f"intenção {item.codigo.name} sem confiança declarada"
            )
        if not isinstance(item.confianca, Confianca):
            raise TypeError(
                f"a confiança de {item.codigo.name} precisa ser Confianca"
            )

    presentes = {item.codigo for item in detectadas}
    if (
        IntencaoConversacional.CONTINUIDADE_DE_EVENTO_DECLARADA in presentes
        and IntencaoConversacional.EVENTO_NOVO_DECLARADO in presentes
    ):
        raise _erro(
            "E-Nb-18",
            "CONTINUIDADE_DE_EVENTO_DECLARADA e EVENTO_NOVO_DECLARADO são "
            "mutuamente exclusivas",
        )


# --------------------------------------------------------------------------
# Superfície pública — canonicalizar, projetar e produzir a condição 5
# --------------------------------------------------------------------------


def canonicalizar_interpretacao(entrada: EntradaInterpretacao) -> Interpretacao:
    """Valida a entrada recebida e devolve a `Interpretacao` **canônica**.

    Executa, nesta ordem (AJ1-4): valida a entrada **realmente recebida**;
    deriva a presença dos seis códigos **A1**; calcula a confiança **A1** por
    **N-b-X3**; verifica as pós-condições; e produz uma `Interpretacao` canônica
    válida **ou** um erro de contrato.

    Erro de contrato **bloqueia na fronteira**: nenhuma `Interpretacao` é
    devolvida e nenhuma projeção existe. A entrada **não é mutada**.

    :raises TypeError: tipo runtime incompatível.
    :raises ValueError: erro de contrato `E-Nb-*`, com o código na mensagem.
    """
    validada = _validar_tipos(entrada)

    confianca_global = _validar_confianca_global(validada)
    _validar_dados_extraidos(validada.dados_extraidos)
    _validar_pedido_de_humano(
        validada.pedido_de_humano, validada.confianca_pedido_de_humano
    )
    _validar_itens_com_texto(validada.perguntas_comerciais, "perguntas_comerciais")
    _validar_itens_com_texto(
        validada.referencias_evento_anterior, "referencias_evento_anterior"
    )
    trechos = _validar_trechos_ambiguos(validada.trechos_ambiguos)
    _validar_correcoes(validada.correcoes, validada.dados_extraidos)
    autonomas = _validar_intencoes_autonomas(validada.intencoes_autonomas)

    derivadas = _derivar_a1(
        validada.dados_extraidos,
        validada.perguntas_comerciais,
        validada.pedido_de_humano,
        validada.confianca_pedido_de_humano,
    )

    interpretacao = Interpretacao(
        intencoes_detectadas=_ordenar_canonicamente(derivadas + autonomas),
        dados_extraidos=validada.dados_extraidos,
        correcoes=validada.correcoes,
        perguntas_comerciais=validada.perguntas_comerciais,
        pedido_de_humano=validada.pedido_de_humano,
        confianca_pedido_de_humano=validada.confianca_pedido_de_humano,
        referencias_evento_anterior=validada.referencias_evento_anterior,
        confianca_global=confianca_global,
        trechos_ambiguos=trechos,
    )
    _verificar_pos_condicoes(interpretacao)
    # AJ2 por último (D-AJ2-2): a precedência histórica dos erros N-b/AJ1 é
    # preservada, e o erro de assunto bloqueia antes de qualquer devolução —
    # nenhuma `Interpretacao` inválida escapa da fronteira.
    _validar_assuntos(interpretacao.perguntas_comerciais)
    return interpretacao


def projetar_para_identidade(interpretacao: Interpretacao) -> ProjecaoInterpretacao:
    """Deriva a `ProjecaoInterpretacao` de **sete** campos (N-b-K1–N-b-K8).

    Transporta valor e confiança **inclusive quando `BAIXA`**: a derivação
    **não aplica C3** — quem trata `BAIXA` como ausência é o consumidor
    `ResolvedorIdentidade` (N-b-K4, N-b-K6).

    **Nunca** atravessam: `convidados`, `formato`, `nome`, `contato`,
    `correcoes`, `perguntas_comerciais`, `pedido_de_humano`,
    `trechos_ambiguos`, `confianca_global` e as demais intenções (N-b-K8).
    Nenhum texto conversacional e nenhuma PII chegam ao resolvedor.

    A `Interpretacao` recebida é **verificada como canônica válida** antes de
    qualquer derivação: uma instância inválida **não atravessa** e **nenhuma
    projeção é produzida**.

    :raises TypeError: a projeção exige uma `Interpretacao` canônica válida.
    :raises ValueError: erro de contrato `E-Nb-*` na `Interpretacao` recebida.
    """
    interpretacao = _validar_interpretacao_canonica(interpretacao)

    referencias = interpretacao.referencias_evento_anterior
    if referencias:
        confianca_referencia: Confianca | None = _agregar(
            tuple(r.confianca for r in referencias if r.confianca is not None)
        )
        referencia = ReferenciaEventoAnterior.COM_REFERENCIA
    else:
        confianca_referencia = None
        referencia = ReferenciaEventoAnterior.SEM_REFERENCIA

    dados = interpretacao.dados_extraidos
    return ProjecaoInterpretacao(
        intencao_identidade=_derivar_intencao_identidade(interpretacao),
        referencia_evento_anterior=referencia,
        confianca_referencia=confianca_referencia,
        tipo_evento_extraido=dados.tipo_evento,
        confianca_tipo=dados.confianca_tipo_evento,
        data_nomeada_extraida=dados.data_nomeada,
        confianca_data=dados.confianca_data_nomeada,
    )


def _derivar_intencao_identidade(
    interpretacao: Interpretacao,
) -> IntencaoIdentidade:
    """N-b-K1. As duas intenções são mutuamente exclusivas; a ordem é defensiva."""
    if (
        interpretacao._confianca_de(IntencaoConversacional.EVENTO_NOVO_DECLARADO)
        is Confianca.ALTA
    ):
        return IntencaoIdentidade.NOVO_EVENTO_DECLARADO
    if (
        interpretacao._confianca_de(
            IntencaoConversacional.CONTINUIDADE_DE_EVENTO_DECLARADA
        )
        is Confianca.ALTA
    ):
        return IntencaoIdentidade.CONTINUIDADE_DECLARADA
    return IntencaoIdentidade.NAO_DISCRIMINANTE


def decidir_interesse_confirmar_disponibilidade(
    interpretacao: Interpretacao | None,
) -> bool | None:
    """Condição **5** de §4.4 como função total (N-b-CD1–N-b-CD4).

    `Interpretacao` válida com `INTERESSE_CONFIRMAR_DISPONIBILIDADE` `ALTA` →
    `True`; com `BAIXA` → `False`; com a intenção **ausente** → `False`; **sem**
    `Interpretacao` → `None`.

    `True`/`False` significam **avaliado neste ciclo**; `None` significa **não
    avaliado neste ciclo** e **não** é "falso implícito". **Ausência de
    `Interpretacao` não equivale a `Interpretacao` vazia** (N-b-G8).

    Esta é a **única** condição de §4.4 produzida por este módulo: as condições
    **2**, **4** e **8** continuam **NÃO ATRIBUÍDAS** (N-b-G3).

    Quando não é `None`, a `Interpretacao` é **verificada como canônica válida**
    antes de produzir a condição: uma instância inválida **não atravessa** e
    **nenhuma condição é derivada** dela.

    :raises TypeError: valor que não é `Interpretacao` nem `None`.
    :raises ValueError: erro de contrato `E-Nb-*` na `Interpretacao` recebida.
    """
    if interpretacao is None:
        return None
    interpretacao = _validar_interpretacao_canonica(interpretacao)
    return (
        interpretacao._confianca_de(
            IntencaoConversacional.INTERESSE_CONFIRMAR_DISPONIBILIDADE
        )
        is Confianca.ALTA
    )

"""Resolução de identidade do atendimento (3B.7).

Implementa o `ResolvedorIdentidade` de `docs/07-arquitetura-motor-respostas.md`
§7.1 — a cascata determinística **D0–D6** da arbitragem R3, a precedência de
takeover **R5-P0** da arbitragem R5, a fronteira do conjunto **H** da arbitragem
R-H e a projeção do identificador validado da arbitragem R-I.

O componente é **puro e determinístico**: zero I/O, zero rede, zero LLM, zero
leitura da base, zero relógio, zero persistência. Ele **não** calcula
elegibilidade nem recência, **não** consulta histórico, **não** interpreta texto,
**não** cria atendimento, **não** aplica transição e **não** chama a
`MaquinaEstados`. Recebe o conjunto elegível **pronto** (política N-a, aberta) e
devolve uma decisão auditável sem dado pessoal, sem dado comercial e sem texto
livre.

Erros de contrato **não** viram `Identidade.AMBIGUA`: entrada malformada levanta
`TypeError` (tipo runtime incompatível) ou `ValueError` (combinação bem tipada
mas incoerente), e **nenhuma identidade é devolvida**.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from enum import StrEnum

from casa77_sdr.state_machine import Estado, Identidade


class IntencaoIdentidade(StrEnum):
    """Projeção fechada da interpretação — exatamente três valores (doc 07 §6.3).

    As intenções genéricas `E02`–`E11` e `E17` não discriminam identidade por si
    mesmas: projetam-se em `NAO_DISCRIMINANTE`.
    """

    CONTINUIDADE_DECLARADA = "continuidade_declarada"
    NOVO_EVENTO_DECLARADO = "novo_evento_declarado"
    NAO_DISCRIMINANTE = "nao_discriminante"


class ReferenciaEventoAnterior(StrEnum):
    """Presença de referência explícita ao evento anterior (doc 07 §6.3)."""

    COM_REFERENCIA = "com_referencia"
    SEM_REFERENCIA = "sem_referencia"


class Confianca(StrEnum):
    """Confiança **binária** por campo (doc 07 §7.1, C1).

    Nenhum limiar numérico existe aqui. `BAIXA` significa **ausência** para
    efeito de identidade (C3) — não é sinal fraco a ser ponderado.
    """

    ALTA = "alta"
    BAIXA = "baixa"


class Vinculo(StrEnum):
    """Vínculo declarado — valor **total** das seis combinações (doc 07 §6.3).

    `DECLARACAO_CONTRADITORIA` é consumida por curto-circuito em D0 e **não**
    cria um 13º `CriterioIdentidade`.
    """

    DECLARA_CONTINUIDADE = "declara_continuidade"
    DECLARA_NOVO = "declara_novo"
    SEM_DECLARACAO = "sem_declaracao"
    DECLARACAO_CONTRADITORIA = "declaracao_contraditoria"


class SituacaoTakeover(StrEnum):
    """Dimensão **ortogonal** a `Identidade` (doc 07 §6.3, K1–K4).

    Derivada exclusivamente da cardinalidade de `ids_em_atendimento_humano`
    (H4), nunca de um filtro sobre os candidatos elegíveis.
    """

    SEM_TAKEOVER = "sem_takeover"
    HUMANO_UNICO = "humano_unico"
    HUMANO_MULTIPLO = "humano_multiplo"


class VeredictoIdentificador(StrEnum):
    """Resultado da validação do identificador na etapa 3 (doc 07 §6.1.1).

    Exatamente **quatro** valores. A arbitragem R-I **não** cria um quinto: o ID
    validado viaja em campo próprio, `id_atendimento_validado`.
    """

    NAO_INFORMADO = "nao_informado"
    ENCONTRADO = "encontrado"
    NAO_ENCONTRADO = "nao_encontrado"
    INCOMPATIVEL = "incompativel"


class Comparacao(StrEnum):
    """Comparação **nominal** por campo (doc 07 §7.1, P1–P4)."""

    IGUAL = "igual"
    DIFERENTE = "diferente"
    INDETERMINADO = "indeterminado"


class ClasseCandidato(StrEnum):
    """Classe de um candidato na tabela fechada das nove combinações."""

    CORROBORADO = "corroborado"
    CONTRADITORIO = "contraditorio"
    NEUTRO = "neutro"
    EXCLUIDO = "excluido"


class CriterioIdentidade(StrEnum):
    """Vocabulário fechado de **12 códigos** (doc 07 §7.1).

    **Não existe `IDENTIFICADOR_VALIDADO`**: o identificador não é razão de
    decisão — é restrição de escopo, rastreada por
    `escopo_restrito_por_identificador`.
    """

    PRIMEIRO_CONTATO_COMPROVADO = "primeiro_contato_comprovado"
    SEM_CANDIDATO_ELEGIVEL = "sem_candidato_elegivel"
    NOVO_EVENTO_DECLARADO = "novo_evento_declarado"
    ANCORA_COINCIDENTE_UNICA = "ancora_coincidente_unica"
    CONTINUIDADE_DECLARADA_CANDIDATO_UNICO = "continuidade_declarada_candidato_unico"
    INERCIA_ATENDIMENTO_ATIVO = "inercia_atendimento_ativo"
    TODOS_CANDIDATOS_DIVERGENTES = "todos_candidatos_divergentes"
    AMBIGUIDADE_SINAIS_CONTRADITORIOS = "ambiguidade_sinais_contraditorios"
    AMBIGUIDADE_DIVERGENCIA_EM_ATENDIMENTO_ATIVO = (
        "ambiguidade_divergencia_em_atendimento_ativo"
    )
    AMBIGUIDADE_MULTIPLOS_COMPATIVEIS = "ambiguidade_multiplos_compativeis"
    AMBIGUIDADE_MULTIPLOS_ATIVOS = "ambiguidade_multiplos_ativos"
    AMBIGUIDADE_SINAIS_INSUFICIENTES = "ambiguidade_sinais_insuficientes"


@dataclass(frozen=True)
class CandidatoAtendimento:
    """Um elemento do conjunto elegível fechado (doc 07 §7.1).

    Nenhum outro campo do atendimento entra: **sem nome, sem telefone, sem
    mensagem, sem preço, sem capacidade, sem número de convidados, sem
    formato**.
    """

    id_atendimento: str
    estado: Estado
    tipo_evento_registrado: str | None
    data_nomeada_registrada: str | None


@dataclass(frozen=True)
class ProjecaoInterpretacao:
    """Projeção estruturada da interpretação (doc 07 §6.3).

    O resolvedor **não recebe texto conversacional**. As confianças são `None`
    apenas para tornar verificável **C2** — valor presente sem confiança
    declarada é erro de contrato, não confiança implícita.
    """

    intencao_identidade: IntencaoIdentidade
    referencia_evento_anterior: ReferenciaEventoAnterior
    confianca_referencia: Confianca | None
    tipo_evento_extraido: str | None
    confianca_tipo: Confianca | None
    data_nomeada_extraida: str | None
    confianca_data: Confianca | None


@dataclass(frozen=True)
class DecisaoIdentidade:
    """Saída auditável da etapa 5 — exatamente **oito** campos (doc 07 §7.1).

    Não contém nome, telefone, mensagem, preço, capacidade, número de convidados
    nem formato. **Nenhum texto livre.** `id_atendimento_validado` é insumo,
    nunca saída.
    """

    identidade: Identidade | None
    id_atendimento_alvo: str | None
    criterio: CriterioIdentidade | None
    candidatos_avaliados: tuple[str, ...]
    classificacao_por_candidato: tuple[tuple[str, ClasseCandidato], ...]
    vinculo_declarado: Vinculo
    situacao_takeover: SituacaoTakeover
    escopo_restrito_por_identificador: bool


# --------------------------------------------------------------------------
# Tabelas fechadas
# --------------------------------------------------------------------------

_VINCULO: dict[tuple[IntencaoIdentidade, ReferenciaEventoAnterior], Vinculo] = {
    (
        IntencaoIdentidade.CONTINUIDADE_DECLARADA,
        ReferenciaEventoAnterior.COM_REFERENCIA,
    ): Vinculo.DECLARA_CONTINUIDADE,
    (
        IntencaoIdentidade.CONTINUIDADE_DECLARADA,
        ReferenciaEventoAnterior.SEM_REFERENCIA,
    ): Vinculo.DECLARA_CONTINUIDADE,
    (
        IntencaoIdentidade.NOVO_EVENTO_DECLARADO,
        ReferenciaEventoAnterior.SEM_REFERENCIA,
    ): Vinculo.DECLARA_NOVO,
    (
        IntencaoIdentidade.NOVO_EVENTO_DECLARADO,
        ReferenciaEventoAnterior.COM_REFERENCIA,
    ): Vinculo.DECLARACAO_CONTRADITORIA,
    (
        IntencaoIdentidade.NAO_DISCRIMINANTE,
        ReferenciaEventoAnterior.COM_REFERENCIA,
    ): Vinculo.DECLARA_CONTINUIDADE,
    (
        IntencaoIdentidade.NAO_DISCRIMINANTE,
        ReferenciaEventoAnterior.SEM_REFERENCIA,
    ): Vinculo.SEM_DECLARACAO,
}

_CLASSE: dict[tuple[Comparacao, Comparacao], ClasseCandidato] = {
    (Comparacao.IGUAL, Comparacao.IGUAL): ClasseCandidato.CORROBORADO,
    (Comparacao.IGUAL, Comparacao.INDETERMINADO): ClasseCandidato.CORROBORADO,
    (Comparacao.INDETERMINADO, Comparacao.IGUAL): ClasseCandidato.CORROBORADO,
    (Comparacao.IGUAL, Comparacao.DIFERENTE): ClasseCandidato.CONTRADITORIO,
    (Comparacao.INDETERMINADO, Comparacao.DIFERENTE): ClasseCandidato.CONTRADITORIO,
    (Comparacao.INDETERMINADO, Comparacao.INDETERMINADO): ClasseCandidato.NEUTRO,
    (Comparacao.DIFERENTE, Comparacao.IGUAL): ClasseCandidato.EXCLUIDO,
    (Comparacao.DIFERENTE, Comparacao.DIFERENTE): ClasseCandidato.EXCLUIDO,
    (Comparacao.DIFERENTE, Comparacao.INDETERMINADO): ClasseCandidato.EXCLUIDO,
}


# --------------------------------------------------------------------------
# Comparação nominal
# --------------------------------------------------------------------------


def _normalizar(texto: str) -> str:
    """Chave de igualdade nominal: somente caixa, espaços e acentos.

    Duplicação **deliberada e local** do precedente de `rules._normalizar`: o
    resolvedor não depende das regras comerciais e não lê a base. Nada semântico
    acontece aqui — sinônimo, similaridade, proximidade ou score não existem, e
    a data permanece **valor nominal** (P3).
    """
    sem_acentos = "".join(
        caractere
        for caractere in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(caractere)
    )
    return " ".join(sem_acentos.casefold().split())


def _comparar(extraido: str | None, registrado: str | None) -> Comparacao:
    """`INDETERMINADO` sempre que qualquer um dos lados estiver ausente (P1)."""
    if extraido is None or registrado is None:
        return Comparacao.INDETERMINADO
    if _normalizar(extraido) == _normalizar(registrado):
        return Comparacao.IGUAL
    return Comparacao.DIFERENTE


def _valor_efetivo(valor: str | None, confianca: Confianca | None) -> str | None:
    """Confiança `BAIXA` é **ausência**, nunca sinal fraco ponderado (C3)."""
    if valor is None:
        return None
    if confianca is Confianca.ALTA:
        return valor
    return None


def _referencia_efetiva(projecao: ProjecaoInterpretacao) -> ReferenciaEventoAnterior:
    """Referência com confiança `BAIXA` é lida como ausente (C3)."""
    if (
        projecao.referencia_evento_anterior is ReferenciaEventoAnterior.COM_REFERENCIA
        and projecao.confianca_referencia is Confianca.ALTA
    ):
        return ReferenciaEventoAnterior.COM_REFERENCIA
    return ReferenciaEventoAnterior.SEM_REFERENCIA


def _derivar_vinculo(projecao: ProjecaoInterpretacao) -> Vinculo:
    """Tabela **total** das seis combinações (doc 07 §6.3)."""
    return _VINCULO[(projecao.intencao_identidade, _referencia_efetiva(projecao))]


def _classificar(
    candidatos: tuple[CandidatoAtendimento, ...],
    projecao: ProjecaoInterpretacao,
) -> tuple[tuple[CandidatoAtendimento, ClasseCandidato], ...]:
    """Classifica cada candidato preservando a ordem de entrada."""
    tipo_extraido = _valor_efetivo(projecao.tipo_evento_extraido, projecao.confianca_tipo)
    data_extraida = _valor_efetivo(projecao.data_nomeada_extraida, projecao.confianca_data)
    return tuple(
        (
            candidato,
            _CLASSE[
                (
                    _comparar(tipo_extraido, candidato.tipo_evento_registrado),
                    _comparar(data_extraida, candidato.data_nomeada_registrada),
                )
            ],
        )
        for candidato in candidatos
    )


# --------------------------------------------------------------------------
# Validação de contrato
# --------------------------------------------------------------------------


def _validar_tipos(
    candidatos: object,
    projecao: object,
    veredito_identificador: object,
    id_atendimento_validado: object,
    havia_estado_esperado: object,
    ids_em_atendimento_humano: object,
) -> None:
    """Tipo runtime incompatível é `TypeError`, nunca caso de negócio."""
    if not isinstance(candidatos, tuple):
        raise TypeError("candidatos precisa ser uma tupla de CandidatoAtendimento")
    for candidato in candidatos:
        if not isinstance(candidato, CandidatoAtendimento):
            raise TypeError("cada candidato precisa ser um CandidatoAtendimento")
        if not isinstance(candidato.id_atendimento, str):
            raise TypeError("id_atendimento precisa ser texto")
        if not isinstance(candidato.estado, Estado):
            raise TypeError("estado do candidato precisa ser um Estado")
        if candidato.tipo_evento_registrado is not None and not isinstance(
            candidato.tipo_evento_registrado, str
        ):
            raise TypeError("tipo_evento_registrado precisa ser texto ou None")
        if candidato.data_nomeada_registrada is not None and not isinstance(
            candidato.data_nomeada_registrada, str
        ):
            raise TypeError("data_nomeada_registrada precisa ser texto ou None")

    if not isinstance(projecao, ProjecaoInterpretacao):
        raise TypeError("projecao precisa ser uma ProjecaoInterpretacao")
    if not isinstance(projecao.intencao_identidade, IntencaoIdentidade):
        raise TypeError("intencao_identidade precisa ser uma IntencaoIdentidade")
    if not isinstance(projecao.referencia_evento_anterior, ReferenciaEventoAnterior):
        raise TypeError(
            "referencia_evento_anterior precisa ser uma ReferenciaEventoAnterior"
        )
    for campo in ("confianca_referencia", "confianca_tipo", "confianca_data"):
        valor = getattr(projecao, campo)
        if valor is not None and not isinstance(valor, Confianca):
            raise TypeError(f"{campo} precisa ser uma Confianca ou None")
    for campo in ("tipo_evento_extraido", "data_nomeada_extraida"):
        valor = getattr(projecao, campo)
        if valor is not None and not isinstance(valor, str):
            raise TypeError(f"{campo} precisa ser texto ou None")

    if not isinstance(veredito_identificador, VeredictoIdentificador):
        raise TypeError(
            "veredito_identificador precisa ser um VeredictoIdentificador"
        )
    if id_atendimento_validado is not None and not isinstance(
        id_atendimento_validado, str
    ):
        raise TypeError("id_atendimento_validado precisa ser texto ou None")
    if not isinstance(havia_estado_esperado, bool):
        raise TypeError("havia_estado_esperado precisa ser booleano")
    if not isinstance(ids_em_atendimento_humano, tuple):
        raise TypeError("ids_em_atendimento_humano precisa ser uma tupla de texto")
    for identificador in ids_em_atendimento_humano:
        if not isinstance(identificador, str):
            raise TypeError("cada id de ids_em_atendimento_humano precisa ser texto")


def _validar_confianca(projecao: ProjecaoInterpretacao) -> None:
    """C2 — valor presente sem confiança declarada é erro de contrato."""
    if (
        projecao.referencia_evento_anterior is ReferenciaEventoAnterior.COM_REFERENCIA
        and projecao.confianca_referencia is None
    ):
        raise ValueError("referência presente exige confianca_referencia (C2)")
    if projecao.tipo_evento_extraido is not None and projecao.confianca_tipo is None:
        raise ValueError("tipo_evento_extraido presente exige confianca_tipo (C2)")
    if projecao.data_nomeada_extraida is not None and projecao.confianca_data is None:
        raise ValueError("data_nomeada_extraida presente exige confianca_data (C2)")


def _validar_conjunto_humano(
    candidatos: tuple[CandidatoAtendimento, ...],
    ids_em_atendimento_humano: tuple[str, ...],
) -> None:
    """H4 e H5 — coerência estrutural do conjunto H (doc 07 §6.2)."""
    if len(set(ids_em_atendimento_humano)) != len(ids_em_atendimento_humano):
        # Duplicata **não** conta como `HUMANO_MULTIPLO` (H4).
        raise ValueError("ids_em_atendimento_humano não pode conter duplicatas (H4)")
    humanos = set(ids_em_atendimento_humano)
    for candidato in candidatos:
        if (
            candidato.estado is Estado.ATENDIMENTO_HUMANO
            and candidato.id_atendimento not in humanos
        ):
            raise ValueError(
                "candidato elegível em atendimento_humano ausente de "
                "ids_em_atendimento_humano (H5)"
            )
    # A recíproca **não** é exigida: ID em H fora do conjunto elegível é válido
    # e esperado — é o que preserva a independência de H em relação a N-a.


def _validar_identificador(
    candidatos: tuple[CandidatoAtendimento, ...],
    veredito_identificador: VeredictoIdentificador,
    id_atendimento_validado: str | None,
    havia_estado_esperado: bool,
) -> None:
    """P-I1 a P-I5 — pré-condições da projeção do identificador (arbitragem R-I)."""
    if veredito_identificador is VeredictoIdentificador.NAO_INFORMADO:
        if id_atendimento_validado is not None:
            raise ValueError(
                "NAO_INFORMADO exige id_atendimento_validado None (P-I1)"
            )
        return

    if veredito_identificador in (
        VeredictoIdentificador.NAO_ENCONTRADO,
        VeredictoIdentificador.INCOMPATIVEL,
    ):
        # Bloqueio já devido na etapa 3 (N5, N6, S3); aqui é defensivo.
        raise ValueError(
            "veredito NAO_ENCONTRADO/INCOMPATIVEL não pode alcançar a etapa 5 (P-I3)"
        )

    if not id_atendimento_validado:
        raise ValueError(
            "ENCONTRADO exige id_atendimento_validado não vazio (P-I2)"
        )
    if havia_estado_esperado is not True:
        raise ValueError("ENCONTRADO exige havia_estado_esperado verdadeiro (P-I4)")

    ocorrencias = sum(
        1
        for candidato in candidatos
        if candidato.id_atendimento == id_atendimento_validado
    )
    if ocorrencias != 1:
        # Unicidade exigida **somente** do ID identificado. Duplicatas entre
        # candidatos não identificados permanecem questão residual não decidida.
        raise ValueError(
            "ENCONTRADO exige exatamente uma ocorrência do atendimento "
            "identificado no conjunto elegível (P-I5)"
        )


def _situacao_takeover(ids_em_atendimento_humano: tuple[str, ...]) -> SituacaoTakeover:
    """A cardinalidade de H define a situação (H4)."""
    if not ids_em_atendimento_humano:
        return SituacaoTakeover.SEM_TAKEOVER
    if len(ids_em_atendimento_humano) == 1:
        return SituacaoTakeover.HUMANO_UNICO
    return SituacaoTakeover.HUMANO_MULTIPLO


# --------------------------------------------------------------------------
# Cascata
# --------------------------------------------------------------------------


def _decidir(
    identidade: Identidade | None,
    alvo: str | None,
    criterio: CriterioIdentidade,
    escopo: tuple[tuple[CandidatoAtendimento, ClasseCandidato], ...],
    vinculo: Vinculo,
    escopo_restrito: bool,
) -> DecisaoIdentidade:
    """Monta a saída auditável a partir do escopo vigente no momento da decisão."""
    return DecisaoIdentidade(
        identidade=identidade,
        id_atendimento_alvo=alvo,
        criterio=criterio,
        candidatos_avaliados=tuple(
            candidato.id_atendimento for candidato, _ in escopo
        ),
        classificacao_por_candidato=tuple(
            (candidato.id_atendimento, classe) for candidato, classe in escopo
        ),
        vinculo_declarado=vinculo,
        situacao_takeover=SituacaoTakeover.SEM_TAKEOVER,
        escopo_restrito_por_identificador=escopo_restrito,
    )


def _relacao(alvo: CandidatoAtendimento) -> Identidade:
    """A relação é derivada do estado do alvo, nunca escolhida (R6)."""
    if alvo.estado is Estado.ENCERRADO:
        return Identidade.MESMA_SOLICITACAO
    return Identidade.ATENDIMENTO_ATIVO


def _cascata(
    escopo: tuple[tuple[CandidatoAtendimento, ClasseCandidato], ...],
    vinculo: Vinculo,
    veredito_identificador: VeredictoIdentificador,
    id_atendimento_validado: str | None,
    havia_estado_esperado: bool,
) -> DecisaoIdentidade:
    """Cascata determinística D0–D6. A primeira regra que decide encerra."""
    escopo_restrito = False

    # D0 — sinais contraditórios. Antes de tudo na cascata.
    if vinculo is Vinculo.DECLARACAO_CONTRADITORIA:
        return _decidir(
            Identidade.AMBIGUA,
            None,
            CriterioIdentidade.AMBIGUIDADE_SINAIS_CONTRADITORIOS,
            escopo,
            vinculo,
            escopo_restrito,
        )

    # D1 — escopo vazio. Alcançável somente com NAO_INFORMADO, por consequência
    # de P-I5: um ENCONTRADO válido exige um candidato no escopo.
    if not escopo:
        criterio = (
            CriterioIdentidade.SEM_CANDIDATO_ELEGIVEL
            if havia_estado_esperado
            else CriterioIdentidade.PRIMEIRO_CONTATO_COMPROVADO
        )
        return _decidir(None, None, criterio, escopo, vinculo, escopo_restrito)

    # D2 — o identificador restringe, nunca decide (N7). A existência e a
    # unicidade do identificado já foram garantidas por P-I5, na entrada.
    if veredito_identificador is VeredictoIdentificador.ENCONTRADO:
        indice_identificado = next(
            posicao
            for posicao, (candidato, _) in enumerate(escopo)
            if candidato.id_atendimento == id_atendimento_validado
        )
        classe_identificado = escopo[indice_identificado][1]
        corroborado_alheio = any(
            classe is ClasseCandidato.CORROBORADO
            for posicao, (_, classe) in enumerate(escopo)
            if posicao != indice_identificado
        )
        if corroborado_alheio and classe_identificado is not ClasseCandidato.CORROBORADO:
            return _decidir(
                Identidade.AMBIGUA,
                None,
                CriterioIdentidade.AMBIGUIDADE_SINAIS_CONTRADITORIOS,
                escopo,
                vinculo,
                escopo_restrito,
            )
        escopo = (escopo[indice_identificado],)
        escopo_restrito = True

    ativos = tuple(
        par for par in escopo if par[0].estado is not Estado.ENCERRADO
    )

    # D3 — evento novo declarado protege atendimento ativo, inclusive excluído.
    if vinculo is Vinculo.DECLARA_NOVO:
        if ativos:
            return _decidir(
                Identidade.AMBIGUA,
                None,
                CriterioIdentidade.AMBIGUIDADE_DIVERGENCIA_EM_ATENDIMENTO_ATIVO,
                escopo,
                vinculo,
                escopo_restrito,
            )
        return _decidir(
            Identidade.NOVA_SOLICITACAO,
            None,
            CriterioIdentidade.NOVO_EVENTO_DECLARADO,
            escopo,
            vinculo,
            escopo_restrito,
        )

    corroborados = tuple(
        par for par in escopo if par[1] is ClasseCandidato.CORROBORADO
    )

    # D4 — âncora coincidente.
    if len(corroborados) == 1:
        alvo = corroborados[0][0]
        return _decidir(
            _relacao(alvo),
            alvo.id_atendimento,
            CriterioIdentidade.ANCORA_COINCIDENTE_UNICA,
            escopo,
            vinculo,
            escopo_restrito,
        )
    if len(corroborados) >= 2:
        return _decidir(
            Identidade.AMBIGUA,
            None,
            CriterioIdentidade.AMBIGUIDADE_MULTIPLOS_COMPATIVEIS,
            escopo,
            vinculo,
            escopo_restrito,
        )

    validos = tuple(par for par in escopo if par[1] is not ClasseCandidato.EXCLUIDO)

    # D5 — continuidade declarada, sem âncora.
    if vinculo is Vinculo.DECLARA_CONTINUIDADE:
        if len(validos) == 1:
            alvo = validos[0][0]
            return _decidir(
                _relacao(alvo),
                alvo.id_atendimento,
                CriterioIdentidade.CONTINUIDADE_DECLARADA_CANDIDATO_UNICO,
                escopo,
                vinculo,
                escopo_restrito,
            )
        return _decidir(
            Identidade.AMBIGUA,
            None,
            CriterioIdentidade.AMBIGUIDADE_SINAIS_INSUFICIENTES,
            escopo,
            vinculo,
            escopo_restrito,
        )

    # D6 — sem declaração: inércia do atendimento ativo.
    if vinculo is Vinculo.SEM_DECLARACAO:
        ativos_validos = tuple(
            par for par in ativos if par[1] is not ClasseCandidato.EXCLUIDO
        )
        ativos_excluidos = tuple(
            par for par in ativos if par[1] is ClasseCandidato.EXCLUIDO
        )
        encerrados_validos = tuple(
            par
            for par in validos
            if par[0].estado is Estado.ENCERRADO
        )
        if len(ativos_validos) == 1:
            alvo = ativos_validos[0][0]
            return _decidir(
                _relacao(alvo),
                alvo.id_atendimento,
                CriterioIdentidade.INERCIA_ATENDIMENTO_ATIVO,
                escopo,
                vinculo,
                escopo_restrito,
            )
        if len(ativos_validos) >= 2:
            return _decidir(
                Identidade.AMBIGUA,
                None,
                CriterioIdentidade.AMBIGUIDADE_MULTIPLOS_ATIVOS,
                escopo,
                vinculo,
                escopo_restrito,
            )
        if ativos_excluidos:
            return _decidir(
                Identidade.AMBIGUA,
                None,
                CriterioIdentidade.AMBIGUIDADE_DIVERGENCIA_EM_ATENDIMENTO_ATIVO,
                escopo,
                vinculo,
                escopo_restrito,
            )
        if not encerrados_validos:
            return _decidir(
                Identidade.NOVA_SOLICITACAO,
                None,
                CriterioIdentidade.TODOS_CANDIDATOS_DIVERGENTES,
                escopo,
                vinculo,
                escopo_restrito,
            )
        return _decidir(
            Identidade.AMBIGUA,
            None,
            CriterioIdentidade.AMBIGUIDADE_SINAIS_INSUFICIENTES,
            escopo,
            vinculo,
            escopo_restrito,
        )

    # FECHAMENTO — o não previsto resolve em ambiguidade, jamais em continuidade
    # presumida (R7).
    return _decidir(
        Identidade.AMBIGUA,
        None,
        CriterioIdentidade.AMBIGUIDADE_SINAIS_INSUFICIENTES,
        escopo,
        vinculo,
        escopo_restrito,
    )


def resolver_identidade(
    candidatos: tuple[CandidatoAtendimento, ...],
    projecao: ProjecaoInterpretacao,
    veredito_identificador: VeredictoIdentificador,
    id_atendimento_validado: str | None,
    havia_estado_esperado: bool,
    ids_em_atendimento_humano: tuple[str, ...],
) -> DecisaoIdentidade:
    """Resolve qual atendimento a mensagem trata, a partir de insumos prontos.

    Função pura: sem I/O, sem rede, sem relógio, sem persistência, sem LLM, sem
    leitura da base e sem mutação dos argumentos. Dadas as mesmas entradas,
    produz sempre a mesma decisão.

    O `conjunto elegível` chega **pronto** da etapa 3 (política N-a, ainda
    aberta) e `ids_em_atendimento_humano` é entrada **separada**, fora de N-a.

    Ordem: pré-condições estruturais → **R5-P0** (takeover) → **D0–D6**. Entrada
    malformada nunca alcança R5-P0 nem D0.

    Erros:

    - `TypeError` — tipo runtime incompatível em qualquer argumento;
    - `ValueError` — combinação bem tipada mas incoerente: **C2** (valor sem
      confiança), **H4** (duplicata em H), **H5** (candidato humano ausente de
      H) e **P-I1–P-I5** (projeção do identificador validado).

    Erro de contrato **não** devolve `DecisaoIdentidade` e **nunca** vira
    `Identidade.AMBIGUA`.
    """
    _validar_tipos(
        candidatos,
        projecao,
        veredito_identificador,
        id_atendimento_validado,
        havia_estado_esperado,
        ids_em_atendimento_humano,
    )
    _validar_confianca(projecao)
    _validar_conjunto_humano(candidatos, ids_em_atendimento_humano)
    _validar_identificador(
        candidatos,
        veredito_identificador,
        id_atendimento_validado,
        havia_estado_esperado,
    )

    vinculo = _derivar_vinculo(projecao)
    situacao = _situacao_takeover(ids_em_atendimento_humano)

    # R5-P0 — precedência de takeover, antes da restrição por identificador e
    # antes de D0. O alvo de `HUMANO_UNICO` vem **direto de H** (H8), nunca dos
    # candidatos elegíveis; em `HUMANO_MULTIPLO` o motor não escolhe e não usa
    # recência para desempatar. O alerta operacional pertence ao futuro
    # orquestrador, não a este componente.
    if situacao is not SituacaoTakeover.SEM_TAKEOVER:
        return DecisaoIdentidade(
            identidade=None,
            id_atendimento_alvo=(
                ids_em_atendimento_humano[0]
                if situacao is SituacaoTakeover.HUMANO_UNICO
                else None
            ),
            criterio=None,
            candidatos_avaliados=(),
            classificacao_por_candidato=(),
            vinculo_declarado=vinculo,
            situacao_takeover=situacao,
            escopo_restrito_por_identificador=False,
        )

    return _cascata(
        _classificar(candidatos, projecao),
        vinculo,
        veredito_identificador,
        id_atendimento_validado,
        havia_estado_esperado,
    )

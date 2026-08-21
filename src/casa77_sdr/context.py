"""Montagem das projeções de identidade da etapa 3 (doc 07 §6.2).

Materializa a **precedência conceitual dos 14 passos** de §6.2 **no que toca à
fronteira etapa 3 → identidade/etapa 5**: lê a persistência operacional, valida
o identificador, projeta o contexto, constrói **H**, determina
`havia_estado_esperado`, delega **E** à política N-a e entrega uma projeção
mínima e fechada.

**Isto não é a etapa 3 inteira materializada.** É o *wiring* da fronteira
etapa 3 → identidade/etapa 5, e nada além disso: **N-a-T3–N-a-T7** (escrita do
marco temporal), **N-b**, **E4**, **S2-D8**, **S3-D1**, o **tratamento
operacional dos bloqueios** (S4, S5), o **destino do alerta** e o
`OrquestradorMotor` **continuam não implementados**.

Não é componente arquitetural novo: a tabela de `docs/07` §4.1 permanece com
**14** componentes e a de §2 com **nove** responsabilidades. A etapa 3 continua
**coordenada pelo `OrquestradorMotor`** (D1) — que não existe em código.

Fronteira: usa a persistência **somente para leitura**. Não cria registro, não
grava, não marca chave de idempotência, não preserva pendente, não consulta
relógio vivo, não lê YAML, não usa LLM, não usa rede, não interpreta mensagem,
não chama `resolver_identidade`, não chama a `MaquinaEstados`, não qualifica e
não decide resposta.

**E continua delegado** a `casa77_sdr.eligibility`: a política N-a não é
reimplementada aqui. **H permanece fora de N-a** (H1, H2), construído por
filtro estrutural de estado sobre o contexto integral.

As exceções aqui **apenas sinalizam**. Preservar a mensagem, emitir alerta
operacional e decidir o que o motor faz com o bloqueio (S4, S5) pertencem ao
`OrquestradorMotor`.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta

from casa77_sdr.eligibility import (
    canonicalizar_conjunto_elegivel,
    exigir_limiar_valido,
    projetar_registros,
    selecionar_conjunto_elegivel,
)
from casa77_sdr.identity import CandidatoAtendimento, VeredictoIdentificador
from casa77_sdr.persistence import (
    PersistenciaOperacional,
    RecuperacaoPorId,
    RegistroAtendimento,
    ResultadoRecuperacao,
)
from casa77_sdr.state_machine import Estado

# Mapeamento explícito do resultado da persistência para o vocabulário fechado
# da etapa 5. São enums distintos por construção: a persistência informa o que
# encontrou; o veredito é a conclusão da etapa 3 (§6.1.1, N2–N4).
_VEREDITO_POR_RESULTADO = {
    ResultadoRecuperacao.ENCONTRADO: VeredictoIdentificador.ENCONTRADO,
    ResultadoRecuperacao.NAO_ENCONTRADO: VeredictoIdentificador.NAO_ENCONTRADO,
    ResultadoRecuperacao.INCOMPATIVEL: VeredictoIdentificador.INCOMPATIVEL,
}


class IdentificadorNaoResolvido(ValueError):
    """Identificador informado, mas inexistente ou incompatível (N5, N6, S3).

    Bloqueio **da etapa 3**: nenhum atendimento é criado, nenhuma projeção é
    devolvida e o `ResolvedorIdentidade` **não é chamado** — é o que impede
    `NAO_ENCONTRADO`/`INCOMPATIVEL` de alcançarem a etapa 5 (P-I3).

    Transporta **apenas o veredito fechado**. Nunca o identificador, o canal,
    o contato, a mensagem ou qualquer dado pessoal: o bloqueio é um fato de
    contrato, não um relatório do que o contato enviou (§6.6, H3).
    """

    def __init__(self, veredito: VeredictoIdentificador) -> None:
        super().__init__(
            "O identificador informado não foi resolvido na etapa 3: "
            f"{veredito.value}"
        )
        self.veredito = veredito


class ConjuntoHumanoIncoerente(ValueError):
    """Conjunto **H** estruturalmente incoerente (H4, H5).

    Duplicata em H — que **não** conta como `HUMANO_MULTIPLO` — ou candidato
    elegível em `atendimento_humano` cujo ID não está em H. A recíproca
    **não** é erro: ID em H fora de E é esperado e preserva a independência
    de H em relação a N-a (H2, H5).
    """


class ProjecaoIdentificadorIncoerente(ValueError):
    """A etapa 3 não conseguiu produzir projeção coerente do identificador.

    É o **N-I-4**: bloqueio na etapa 3, sem chamar o `ResolvedorIdentidade`,
    sem ignorar silenciosamente o identificador e sem criar atendimento
    (N6, S3). Espelha, do lado do produtor, as pré-condições P-I1–P-I5 que o
    consumidor verifica em `identity.py`.
    """


@dataclass(frozen=True)
class ProjecoesIdentidadeEtapa3:
    """Projeção mínima e fechada da etapa 3 para a etapa 5 (§6.2).

    Exatamente os cinco insumos que o `ResolvedorIdentidade` consome. **Não**
    transporta registro bruto, canal, contato, telefone, nome, mensagem,
    qualificação, pendência, motivo, preço, capacidade nem qualquer texto
    conversacional: é a fronteira da identidade, não um modelo de dados geral
    (H3, N-a-P6).
    """

    candidatos_elegiveis: tuple[CandidatoAtendimento, ...]
    veredito_identificador: VeredictoIdentificador
    id_atendimento_validado: str | None
    havia_estado_esperado: bool
    ids_em_atendimento_humano: tuple[str, ...]


def _verificar_invariantes_de_produtor(
    projecoes: ProjecoesIdentidadeEtapa3,
) -> None:
    """Passo 12 — correspondências H4/H5 e N-I exigidas do produtor (§6.2).

    Detalhe interno da montagem: roda **antes** da canonicalização (passo 13)
    e não integra a superfície pública do pacote.

    Verificação **defensiva e final** sobre o que a etapa 3 vai entregar. Não
    reimplementa a cascata nem a defesa do consumidor: P-I1–P-I5 continuam
    sendo verificadas por `resolver_identidade`. Aqui vale a obrigação
    espelhada — **N-I é do produtor, P-I é do consumidor** (§6.1.1).
    """
    ids_humanos = projecoes.ids_em_atendimento_humano
    if len(set(ids_humanos)) != len(ids_humanos):
        raise ConjuntoHumanoIncoerente(
            "ids_em_atendimento_humano não pode conter duplicatas (H4)"
        )
    humanos = set(ids_humanos)
    for candidato in projecoes.candidatos_elegiveis:
        if (
            candidato.estado is Estado.ATENDIMENTO_HUMANO
            and candidato.id_atendimento not in humanos
        ):
            raise ConjuntoHumanoIncoerente(
                "candidato elegível em atendimento_humano ausente de "
                "ids_em_atendimento_humano (H5)"
            )

    veredito = projecoes.veredito_identificador
    if veredito is VeredictoIdentificador.NAO_INFORMADO:
        if projecoes.id_atendimento_validado is not None:
            raise ProjecaoIdentificadorIncoerente(
                "NAO_INFORMADO exige id_atendimento_validado None (N-I-1)"
            )
        return

    if veredito is not VeredictoIdentificador.ENCONTRADO:
        raise ProjecaoIdentificadorIncoerente(
            "veredito NAO_ENCONTRADO/INCOMPATIVEL não pode ser entregue à "
            "etapa 5; o bloqueio é da etapa 3 (N5, N6, S3)"
        )

    if not projecoes.id_atendimento_validado:
        raise ProjecaoIdentificadorIncoerente(
            "ENCONTRADO exige id_atendimento_validado não vazio (N-I-1)"
        )
    if projecoes.havia_estado_esperado is not True:
        raise ProjecaoIdentificadorIncoerente(
            "ENCONTRADO exige havia_estado_esperado verdadeiro (N-I-3)"
        )
    ocorrencias = sum(
        1
        for candidato in projecoes.candidatos_elegiveis
        if candidato.id_atendimento == projecoes.id_atendimento_validado
    )
    if ocorrencias != 1:
        raise ProjecaoIdentificadorIncoerente(
            "ENCONTRADO exige exatamente uma ocorrência do atendimento "
            "identificado no conjunto elegível (N-I-2)"
        )


def montar_projecoes_identidade_etapa3(
    persistencia: PersistenciaOperacional,
    *,
    canal: str,
    contato: str,
    id_atendimento_informado: str | None,
    instante_de_referencia_do_ciclo: datetime,
    limiar_recencia: timedelta | None,
) -> ProjecoesIdentidadeEtapa3:
    """Monta as projeções de identidade da etapa 3, na ordem normativa de §6.2.

    Cobre a **fronteira etapa 3 → identidade/etapa 5**, não a etapa 3 inteira.

    Nenhum argumento possui default comercial ou operacional oculto: o limiar
    chega explícito e sem valor padrão (N-a-L1–N-a-L3), e o instante de
    referência é o campo "data e hora" da entrada (§6.1, N-a-R2) — **nunca**
    relógio vivo.
    """
    # Passo 1 — validar a configuração temporal ANTES de tocar a persistência
    # (N-a-L4, N-a-L5, S10): configuração inválida não fica latente esperando o
    # primeiro `encerrado` aparecer, e nenhuma leitura acontece sob ela.
    exigir_limiar_valido(limiar_recencia)

    # Passo 2 — recuperar pelo identificador, quando fornecido (N1, N2). A
    # persistência valida a compatibilidade com canal + contato (N3) e nunca
    # expõe registro incompatível.
    recuperacao: RecuperacaoPorId | None = None
    if id_atendimento_informado is not None:
        recuperacao = persistencia.recuperar_por_id(
            id_atendimento_informado, canal, contato
        )

    # Passo 3 — consultar os registros do contato (contexto bruto, N-a-4).
    # Acontece **antes** da validação do identificador: a ordem normativa é
    # recuperar por ID → consultar contato → validar, e o bloqueio de N5 não é
    # antecipado para o passo 2.
    registros_recuperados = persistencia.consultar_por_contato(canal, contato)

    # Passo 4 — validar o identificador (§6.1.1, N3–N6).
    veredito = VeredictoIdentificador.NAO_INFORMADO
    registro_identificado: RegistroAtendimento | None = None
    if recuperacao is not None:
        veredito = _VEREDITO_POR_RESULTADO[recuperacao.resultado]
        if veredito is not VeredictoIdentificador.ENCONTRADO:
            # N5/N6/S3 — bloqueio aqui: não criar atendimento, não devolver
            # projeções e não chamar o resolvedor.
            raise IdentificadorNaoResolvido(veredito)
        registro_identificado = recuperacao.registro

    # Passos 5 e 6 — validar a integridade e projetar o contexto **integral**,
    # antes de H e antes de qualquer filtragem (N-a-P1–N-a-P6, S11).
    projetados = projetar_registros(registros_recuperados)

    # Passo 7 — construir H por filtro estrutural de estado, à parte de N-a
    # (H1, H2). Somente IDs opacos (H3).
    ids_em_atendimento_humano = tuple(
        candidato.id_atendimento
        for candidato in projetados
        if candidato.estado is Estado.ATENDIMENTO_HUMANO
    )

    # Passo 8 — `havia_estado_esperado` sobre o contexto RECUPERADO, nunca
    # sobre E: filtrar todo o histórico para fora de E não transforma o
    # contato em primeiro contato (§6.2).
    havia_estado_esperado = (
        veredito is VeredictoIdentificador.ENCONTRADO or len(registros_recuperados) > 0
    )

    # Passos 9 e 10 — classificação, recência e N-a-F1 são **delegados** à
    # política N-a; nada disso é reimplementado aqui. E sai **ainda não
    # canonicalizado**: ordenar é o passo 13, depois da verificação.
    candidatos_selecionados = selecionar_conjunto_elegivel(
        registros_recuperados,
        registro_identificado=registro_identificado,
        instante_de_referencia_do_ciclo=instante_de_referencia_do_ciclo,
        limiar_recencia=limiar_recencia,
    )

    # Passo 11 — projetar `id_atendimento_validado` (N-I-1). ID técnico
    # opaco, e somente sob `ENCONTRADO`; `NAO_INFORMADO` projeta `None`
    # (P-I1). Os demais vereditos já bloquearam no passo 4.
    id_validado = (
        registro_identificado.id_atendimento
        if registro_identificado is not None
        else None
    )

    projecoes = ProjecoesIdentidadeEtapa3(
        candidatos_elegiveis=candidatos_selecionados,
        veredito_identificador=veredito,
        id_atendimento_validado=id_validado,
        havia_estado_esperado=havia_estado_esperado,
        ids_em_atendimento_humano=ids_em_atendimento_humano,
    )

    # Passo 12 — verificar as correspondências H4/H5 e N-I aplicáveis, sobre E
    # **antes** da ordem canônica: a verificação é do conteúdo entregue, não da
    # sequência auditável.
    _verificar_invariantes_de_produtor(projecoes)

    # Passo 13 — canonicalizar E (N-a-O1–N-a-O5), só então.
    # Passo 14 — entregar as projeções à etapa 5.
    return replace(
        projecoes,
        candidatos_elegiveis=canonicalizar_conjunto_elegivel(candidatos_selecionados),
    )

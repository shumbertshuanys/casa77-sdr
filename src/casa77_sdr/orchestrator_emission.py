"""Etapas 8–12 do ciclo — da primeira decisão ao texto final validado.

Coordena, sobre a `PrimeiraDecisao` das etapas 6–7, a cadeia vigente de
`docs/07-arquitetura-motor-respostas.md` §4.1.5 e §5:

8. `ProjetorEmissao` — cobertura de S2-D8 + ações da **primeira** decisão
   (`fotografia_r06` montada por `montar_fotografia_fragmento` **somente** quando
   a ação de T16 é a *owner* de `R06/F1`, isto é, ação presente e cobertura sem o
   token — PE-15/PE-19, FF-10);
9. `SeletorFatos` + compositor determinístico;
10. **sem LLM no M2**: o texto candidato é o literal aprovado
    (`RespostaMontada.texto`) — o caminho "LLM indisponível → texto aprovado
    literal" de §5;
11. `ValidadorResposta`;
12. reprovação → **`R03` literal** (obtido pela mesma cadeia, token `R03/F1`) e
    **tentativa** de alerta operacional; nenhuma transição extra, nenhuma nova
    redação. Depois, o **fechamento**: `E15` → `E12` (doc 06 §4.2), no máximo
    **três** chamadas da `MaquinaEstados` no ciclo.

Ação sem fragmento aprovado na tabela do projetor **não produz texto**; sem
fragmento algum, `texto is None` (ruling T5). Estado `atendimento_humano` ou
`SILENCIAR_RESPOSTA_AUTOMATICA` → `texto is None`, sem fechamento. A mensagem
de encaminhamento (`R08`, ação de T27) sai em `texto_encaminhamento`, nunca em
`texto`.

**Fechamento** (ruling T5, doc 06 §2.2/§4.2):

- `E15` é confirmado quando a primeira decisão tem `RESPONDER_PERGUNTA_COMERCIAL`
  e existe texto final **validado que responde** — fragmentos de cobertura
  emitidos sem substituição por `R03`. Só reentra a partir de estado que a
  máquina admite para `E15` (T20/T21/T38 em `respondendo_duvidas`, T29 em
  `encaminhado_humano`, inércia N4 em `pronto_para_handoff`).
- `E12` é confirmado quando o estado corrente é `pronto_para_handoff` e o resumo
  foi gerado (T27). Toda ação `PREPARAR_RESUMO` leva a `pronto_para_handoff`;
  as transições de lacuna (T11/T12/T18/T19) também levam, sem essa ação, e o
  único avanço desse estado é T27 — por isso o gatilho é o estado.

Erros de contrato das fronteiras 8–11 atravessam **intactos** (*fail-closed*).
Sem I/O próprio, sem relógio, sem persistência, sem emissão.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from casa77_sdr.alerta_operacional import tentar_alerta_operacional
from casa77_sdr.emission_projection import projetar_fragmentos_para_emissao
from casa77_sdr.fact_selection import materializar_fatos_autorizados
from casa77_sdr.fragment_snapshot import montar_fotografia_fragmento
from casa77_sdr.handoff_summary import codigo_pacote_aplicavel, montar_resumo_handoff
from casa77_sdr.motor_deps import BaseMotor
from casa77_sdr.orchestrator_decision import PrimeiraDecisao, dados_para_aplicabilidade
from casa77_sdr.pricing_applicability import decidir_aplicabilidade_de_pacote
from casa77_sdr.response_assembly import RespostaMontada, montar_resposta_final
from casa77_sdr.response_composition import compor_textos_emitiveis
from casa77_sdr.response_validation import validar_resposta_final
from casa77_sdr.state_machine import AcaoMaquina, DecisaoMaquina, Estado, Evento, decidir

__all__ = ["CATEGORIA_VALIDACAO_REPROVADA", "TextoFinal", "produzir_texto_final"]

#: Categoria estrutural do alerta operacional da etapa 12.
CATEGORIA_VALIDACAO_REPROVADA = "validacao_resposta_reprovada"

# Identificadores estruturais de fragmento (os mesmos do projetor, §4.1.5).
_LACUNA = "R03/F1"
_CONDICOES_VISITA = "R06/F1"

# Ações de coleta da decisão de `E15` (T20) que entram no texto principal.
_ACOES_DE_COLETA = frozenset(
    {AcaoMaquina.RETOMAR_COLETA_SEM_REPETIR, AcaoMaquina.PERGUNTAR_PROXIMO_CAMPO_AUSENTE}
)

# Estados a partir dos quais a máquina admite `E15` (doc 06 §4.2).
_ESTADOS_QUE_ADMITEM_E15 = frozenset(
    {Estado.RESPONDENDO_DUVIDAS, Estado.ENCAMINHADO_HUMANO, Estado.PRONTO_PARA_HANDOFF}
)


@dataclass(frozen=True)
class TextoFinal:
    """Resultado das etapas 8–12.

    `texto` é `None` quando nada deve ser dito ao interessado.
    `decisoes_do_ciclo` começa **sempre** pela primeira decisão, seguida das
    decisões de `E15` e/ou `E12` quando feitas (1 a 3 no total).
    `resumo_handoff` existe quando `E12` foi confirmado.
    `texto_encaminhamento` é a mensagem de encaminhamento ao interessado (`R08`,
    `docs/04`) projetada das ações das decisões de **fechamento**. Fica
    **separada** de `texto` porque só pode ser enviada **depois** da entrega
    bem-sucedida do resumo (doc 06 §10, `docs/07` §5 etapa 14).
    """

    texto: str | None
    decisoes_do_ciclo: tuple[DecisaoMaquina, ...]
    resumo_handoff: str | None
    texto_encaminhamento: str | None = None


def produzir_texto_final(
    pd: PrimeiraDecisao,
    *,
    base_motor: BaseMotor,
    estado_inicial: Estado,
    mensagem: str,
    tentar_alerta: Callable[..., object],
    correlacao: str,
) -> TextoFinal:
    """Executa as etapas 8–12 e o fechamento `E15` → `E12`.

    `mensagem` é a mensagem normalizada do ciclo (Histórico do resumo);
    `tentar_alerta` e `correlacao` chegam explícitos do chamador para a
    tentativa de alerta da etapa 12 (sem valor padrão operacional).
    """
    primeira = pd.decisao
    if _silencio(estado_inicial, primeira):
        return TextoFinal(texto=None, decisoes_do_ciclo=(primeira,), resumo_handoff=None)

    texto, responde = _texto_validado(pd, base_motor, tentar_alerta, correlacao)

    decisoes = [primeira]
    if (
        responde
        and AcaoMaquina.RESPONDER_PERGUNTA_COMERCIAL in primeira.acoes
        and primeira.estado_final in _ESTADOS_QUE_ADMITEM_E15
    ):
        decisoes.append(
            decidir(primeira.estado_final, (Evento.E15,), pd.qualificacao, pd.condicoes)
        )
        texto = _com_coleta_do_e15(pd, decisoes[-1], texto, base_motor, tentar_alerta, correlacao)

    resumo: str | None = None
    if decisoes[-1].estado_final is Estado.PRONTO_PARA_HANDOFF:
        resumo = _resumo(pd, tuple(decisoes), base_motor, mensagem)
        decisoes.append(
            decidir(decisoes[-1].estado_final, (Evento.E12,), pd.qualificacao, pd.condicoes)
        )

    return TextoFinal(
        texto=texto,
        decisoes_do_ciclo=tuple(decisoes),
        resumo_handoff=resumo,
        texto_encaminhamento=_texto_encaminhamento(
            tuple(decisoes[1:]), base_motor, tentar_alerta, correlacao
        ),
    )


def _silencio(estado_inicial: Estado, decisao: DecisaoMaquina) -> bool:
    return (
        estado_inicial is Estado.ATENDIMENTO_HUMANO
        or decisao.estado_final is Estado.ATENDIMENTO_HUMANO
        or AcaoMaquina.SILENCIAR_RESPOSTA_AUTOMATICA in decisao.acoes
    )


def _texto_validado(
    pd: PrimeiraDecisao,
    base_motor: BaseMotor,
    tentar_alerta: Callable[..., object],
    correlacao: str,
) -> tuple[str | None, bool]:
    """Etapas 8–12. Devolve `(texto, responde_pergunta_comercial)`."""
    autorizados = pd.s2d8.fragmentos_autorizados
    projetados = _projetar(pd, base_motor, pd.decisao.acoes)
    if not projetados:
        return None, False

    # Etapas 9–10 — o candidato é o literal aprovado (sem LLM no M2).
    montada = _montar(base_motor, projetados)
    candidato = montada.texto

    # Etapas 11–12.
    if validar_resposta_final(candidato, montada).aprovado:
        return candidato, bool(autorizados)
    _alertar_reprovacao(tentar_alerta, correlacao)
    return _montar(base_motor, (_LACUNA,)).texto, False


def _com_coleta_do_e15(
    pd: PrimeiraDecisao,
    e15: DecisaoMaquina,
    texto: str | None,
    base_motor: BaseMotor,
    tentar_alerta: Callable[..., object],
    correlacao: str,
) -> str | None:
    """Retomada da coleta depois da resposta comercial (T20, decisão de `E15`).

    O critério de `E15` não muda: ele já foi confirmado sobre o texto validado
    da resposta. Aqui as ações de coleta dessa decisão entram no **texto
    principal** — reprojetado com as ações da primeira decisão mais elas, e
    validado **uma vez** como texto final. Reprovado, fica o texto já validado
    da resposta e o alerta é tentado (nenhuma nova chamada da máquina).
    """
    coleta = tuple(a for a in e15.acoes if a in _ACOES_DE_COLETA)
    if not coleta:
        return texto
    projetados = _projetar(pd, base_motor, pd.decisao.acoes + coleta)
    montada = _montar(base_motor, projetados)
    if validar_resposta_final(montada.texto, montada).aprovado:
        return montada.texto
    _alertar_reprovacao(tentar_alerta, correlacao)
    return texto


def _projetar(
    pd: PrimeiraDecisao, base_motor: BaseMotor, acoes: tuple[AcaoMaquina, ...]
) -> tuple[str, ...]:
    """Etapa 8 — `ProjetorEmissao` sobre a cobertura e as ações recebidas."""
    autorizados = pd.s2d8.fragmentos_autorizados

    # A fotografia de `R06/F1` só é montada quando a ação de T16 é a owner.
    fotografia = None
    if AcaoMaquina.INFORMAR_CONDICOES_DE_VISITA in acoes and _CONDICOES_VISITA not in autorizados:
        fotografia = montar_fotografia_fragmento(
            _CONDICOES_VISITA, base_motor.consistencia, assertivas_runtime=()
        )
    qualificacao = pd.qualificacao
    return projetar_fragmentos_para_emissao(
        autorizados,
        acoes,
        fotografia_r06=fotografia,
        # M2.1 (PE-21–PE-24): dado estruturado explícito, nunca a qualificação
        # inteira — o projetor não conhece o `Qualificador`.
        campos_ausentes=qualificacao.campos_ausentes,
        motivos_violacao=tuple(v.motivo for v in qualificacao.violacoes),
        fotografar=lambda token: montar_fotografia_fragmento(
            token, base_motor.consistencia, assertivas_runtime=()
        ),
    )


def _texto_encaminhamento(
    fechamento: tuple[DecisaoMaquina, ...],
    base_motor: BaseMotor,
    tentar_alerta: Callable[..., object],
    correlacao: str,
) -> str | None:
    """Mensagem de encaminhamento a partir das ações de `E15`/`E12`.

    PE-2 restringe a projeção do **texto principal** às ações da **primeira**
    decisão; as ações do fechamento são projetadas **à parte**, sem cobertura,
    em ordem e sem repetição (primeira ocorrência). Reprovada a validação, nada
    é enviado ao interessado — não existe substituto aprovado para o
    encaminhamento — e o alerta é tentado.

    Só a ação de encaminhamento (T27) é projetada aqui: desde o M2.1 a retomada
    de T20 tem fragmento aprovado, e ela **não** pode sair junto da mensagem de
    encaminhamento, que só é enviada depois da entrega do resumo.
    """
    acoes = tuple(
        dict.fromkeys(
            a
            for decisao in fechamento
            for a in decisao.acoes
            if a is AcaoMaquina.EMITIR_MENSAGEM_DE_ENCAMINHAMENTO
        )
    )
    projetados = projetar_fragmentos_para_emissao((), acoes)
    if not projetados:
        return None
    montada = _montar(base_motor, projetados)
    if validar_resposta_final(montada.texto, montada).aprovado:
        return montada.texto
    _alertar_reprovacao(tentar_alerta, correlacao)
    return None


def _alertar_reprovacao(tentar_alerta: Callable[..., object], correlacao: str) -> None:
    tentar_alerta_operacional(
        tentar_alerta,
        categoria=CATEGORIA_VALIDACAO_REPROVADA,
        # Nada falhou ao preservar: a mensagem do ciclo segue intacta no fluxo
        # normal (a reprovação não descarta nem altera o processamento).
        pendente_preservado=True,
        correlacao=correlacao,
    )


def _montar(base_motor: BaseMotor, tokens: tuple[str, ...]) -> RespostaMontada:
    selecao = materializar_fatos_autorizados(
        base_motor.indice, base_motor.base, base_motor.textos, tokens
    )
    return montar_resposta_final(compor_textos_emitiveis(selecao))


def _resumo(
    pd: PrimeiraDecisao,
    decisoes: tuple[DecisaoMaquina, ...],
    base_motor: BaseMotor,
    mensagem: str,
) -> str:
    dados = pd.atualizacao.dados_atualizados
    aplicabilidade = decidir_aplicabilidade_de_pacote(
        dados_para_aplicabilidade(dados), base_motor.base
    )
    return montar_resumo_handoff(
        dados=dados,
        qualificacao=pd.qualificacao,
        codigo_pacote=codigo_pacote_aplicavel(aplicabilidade, base_motor.base),
        motivos=_motivos(pd, decisoes),
        perguntas_em_aberto=tuple(p.texto for p in pd.s2d8.pendencias_resposta),
        historico=mensagem,
    )


def _motivos(pd: PrimeiraDecisao, decisoes: tuple[DecisaoMaquina, ...]) -> tuple[str, ...]:
    """Gatilhos do handoff, como identificadores técnicos, sem repetição."""
    motivos: list[str] = []
    for decisao in decisoes:
        motivos.extend(decisao.motivos_handoff)
    for causa in pd.s2d8.causas_e09:
        motivos.append(
            causa.motivo.value
            if causa.assunto is None
            else f"{causa.motivo.value} ({causa.assunto.value})"
        )
    motivos.extend(v.motivo.value for v in pd.qualificacao.violacoes)
    return tuple(dict.fromkeys(motivos))

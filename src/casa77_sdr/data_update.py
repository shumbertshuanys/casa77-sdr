"""`AtualizadorDadosAtendimento` — etapa 6 do pipeline (`docs/07` §4.1.8).

Materializa a etapa **6** de `docs/07` §5: registrar dados e correções a partir
da `Interpretacao` canônica, sobre os dados de qualificação **já vigentes**, e
produzir o sinal **`insumo_qualificacao_atualizado`** de `docs/06` §4.1 — a
**condição 1** de §4.4, que até aqui não tinha produtor concreto.

Ela acontece **depois** da etapa 4 e **depois** da etapa 5, e **fora de ambas**.
`interpretation.py` continua a autoridade da interpretação, e `qualification.py`
a da qualificação: esta fronteira **não interpreta texto**, **não qualifica**,
**não avalia regra comercial** e **não persiste**. Ela **não é** o 15º componente
de §4.1 — ela **é** o componente que §4.1 já previa, agora com nome próprio.

**Resolução da pendência `B`.** O nome `RegistroAtendimento` designava **dois
referentes**: o componente de comportamento de §4.1 e a dataclass `frozen` de
transporte de `persistence.py`. O componente comportamental passa a se chamar
**`AtualizadorDadosAtendimento`**; a dataclass **preserva** nome, semântica,
campos e exportação. Nada é renomeado no código preexistente, **nenhum alias** é
criado e **nenhuma terceira abstração** aparece: antes eram dois referentes e um
nome, agora são dois referentes e dois nomes. §4.1 permanece com **14**
componentes.

**Domínio fechado: os seis campos**, na ordem canônica de
`interpretation._CAMPOS_DADOS` — `tipo_evento`, `data_nomeada`, `convidados`,
`formato`, `nome`, `contato`. Não existe sétimo campo.

**Somente `ALTA` é efetiva.** `BAIXA` não grava, não corrige, não produz conflito
e não produz mutação. A exceção única de `pedido_de_humano` (**N-b-PH3**)
pertence ao caminho do `DetectorHandoff` e **não se aplica a dados** — nenhuma
analogia é criada.

**Política por campo**, com `Confianca.ALTA` no turno:

| Situação | Dado | `correcoes_registradas` | `campos_em_conflito` | Mutação |
|---|---|---|---|---|
| ausente no turno | preserva o vigente | — | — | não |
| presente com `BAIXA` | preserva o vigente | — | — | não |
| vigente ausente | admite o novo | se corrigido | — | **sim** |
| estritamente igual ao vigente | idempotente | se corrigido | — | não |
| diferente **com** correção explícita | **sobrescreve** | **registra** | — | **sim** |
| diferente **sem** correção explícita | **preserva o vigente** | — | **registra** | não |

A última linha materializa o contrato de §7: *"contradição sem correção
explícita → não gravar, pedir confirmação do dado"*. Esta fronteira **preserva a
evidência** do conflito; ela **não produz a pergunta** ao interessado.

**`dados_extraidos` é a única origem operacional do valor.** `correcoes` funciona
**apenas como predicado** — *este campo foi explicitamente corrigido?* —, e
`CorrecaoInterpretada.valor_novo` **nunca** é aplicado como segunda escrita. O
contrato N-b já garante que a correção esteja presente nos dados extraídos, com
o mesmo campo, o mesmo valor e a mesma confiança, sem duplicata (N-b-C4); nada
disso é revalidado aqui.

**Igualdade estrita de domínio (P-1).** A comparação reutiliza
`interpretation._mesmo_valor`: mesmo tipo e mesmo valor, com `bool` nunca
equivalendo a `int` (N-b-D4). **Nenhuma normalização** acontece — sem
`lower`/`casefold`, sem `strip`, sem remoção de acento, sem Unicode, sem
sinônimo, sem aproximação, sem regex e sem *parsing* de calendário. A etapa 6
**não corrige ruído semântico produzido a montante**.

**Mutação efetiva.** `insumo_qualificacao_atualizado` é `True` **se e somente
se** existe ao menos um dos seis campos cujo valor final admitido **difere
estritamente** do vigente. Nunca é inferida da quantidade de campos recebidos, da
existência de `dados_extraidos` ou `correcoes`, nem da confiança isolada. Quando
esta função executa o campo é sempre um `bool` real; `None` continua reservado ao
chamador futuro para o caso em que a etapa 6 **não tenha sido executada**.

**Os dois `contato` são fronteiras distintas.**
`DadosQualificacao.contato` é o dado **interpretado da conversa**, insumo da
qualificação, e pode ser atualizado por esta política.
`RegistroAtendimento.contato` é o **identificador operacional** do vínculo
persistido — `id_atendimento` × canal × contato — e **não é este dado**: ele
**não pode** ser alterado aqui, e este módulo **não importa** a persistência. A
projeção do contato interpretado para `dados_coletados` pertence à etapa 13 e
**não é implementada** nesta entrega.

O módulo é **puro e determinístico**: zero I/O, filesystem, rede, relógio, YAML,
`knowledge/**`, LLM, SDK, persistência, logging, cache, retry ou *sleep*; ele
**não muta** as entradas — `DadosQualificacao` e `DadosAtendimento` são `frozen`,
e a saída é construída como objetos novos. Ele **não produz** `Evento`,
`Qualificacao`, `Violacao`, `CondicoesCiclo`, ação, resposta ou persistência, e
**não chama** `qualificar`, `avaliar_regras`,
`produzir_eventos_internos_ciclo` nem `decidir`. Projetar a **condição 1** e
compor os insumos da primeira decisão é feito pela fronteira de **composição dos
insumos da primeira decisão** (`docs/07` §4.1.9); decidir **quando** a etapa 6
executa e coordenar o pipeline continuam sendo papel do **`OrquestradorMotor`
futuro**, que continua **ausente**.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from casa77_sdr.identity import Confianca
from casa77_sdr.interpretation import (
    Interpretacao,
    _CAMPOS_DADOS,
    _mesmo_valor,
    _validar_interpretacao_canonica,
)
from casa77_sdr.qualification import (
    DadosQualificacao,
    FormatoEvento,
)
from casa77_sdr.rules import DadosAtendimento

__all__ = [
    "ResultadoAtualizacaoDados",
    "atualizar_dados_atendimento",
]


#: Os **três** campos que vivem em `DadosQualificacao.atendimento`; os demais
#: vivem na própria `DadosQualificacao`. A ordem canônica continua sendo a de
#: `_CAMPOS_DADOS`, que este mapa **não** redeclara.
_CAMPOS_DO_ATENDIMENTO: frozenset[str] = frozenset(
    {"tipo_evento", "data_nomeada", "convidados"}
)


def _vigente(dados: DadosQualificacao, campo: str) -> object:
    """Lê o valor vigente de um dos seis campos, onde quer que ele viva."""
    if campo in _CAMPOS_DO_ATENDIMENTO:
        return getattr(dados.atendimento, campo)
    return getattr(dados, campo)


def _validar_dados_vigentes(dados: object) -> DadosQualificacao:
    """Valida estruturalmente os dados vigentes recebidos.

    As mensagens citam **somente o nome técnico do campo**: nenhum valor
    recebido, nenhum dado pessoal e nenhum trecho de conversa aparece nelas.

    Nada é normalizado aqui — texto vazio e espaço em branco são preservados
    exatamente como recebidos, coerentes com N-b-D2/N-b-D3.
    """
    if not isinstance(dados, DadosQualificacao):
        raise TypeError("dados_vigentes precisa ser um DadosQualificacao")
    if not isinstance(dados.atendimento, DadosAtendimento):
        raise TypeError("atendimento precisa ser um DadosAtendimento")

    for campo in ("tipo_evento", "data_nomeada", "nome", "contato"):
        valor = _vigente(dados, campo)
        if valor is not None and not isinstance(valor, str):
            raise TypeError(f"{campo} precisa ser texto ou None")

    convidados = dados.atendimento.convidados
    if convidados is not None:
        if isinstance(convidados, bool) or not isinstance(convidados, int):
            raise TypeError("convidados precisa ser inteiro não negativo ou None")
        if convidados < 0:
            raise ValueError("convidados não pode ser negativo")

    if dados.formato is not None and not isinstance(dados.formato, FormatoEvento):
        raise TypeError("formato precisa ser FormatoEvento ou None")

    return dados


def _campos_corrigidos(interpretacao: Interpretacao) -> frozenset[str]:
    """Os campos com **correção explícita efetiva** — `ALTA` — neste turno.

    `correcoes` é usada **apenas como predicado**: o valor operacional vem
    sempre de `dados_extraidos`, nunca de `CorrecaoInterpretada.valor_novo`.
    """
    return frozenset(
        correcao.campo
        for correcao in interpretacao.correcoes
        if correcao.confianca is Confianca.ALTA
    )


@dataclass(frozen=True, slots=True)
class ResultadoAtualizacaoDados:
    """O que a etapa 6 produz, e nada além disso.

    `dados_atualizados` fica **fora do `repr`** porque carrega PII de runtime —
    `nome` e `contato` — e texto nominal do interessado.

    `correcoes_registradas` e `campos_em_conflito` carregam **somente nomes
    técnicos de campo**, em ordem canônica de `_CAMPOS_DADOS`, sem duplicata:
    nunca o valor, nunca o texto da mensagem, nunca PII.

    `campos_em_conflito` **não é** evento, condição de `CondicoesCiclo`, ação da
    máquina, pendência comercial nem motivo de *handoff*. Ele preserva a
    evidência de que houve contradição sem correção declarada; o consumo
    conversacional pertence à integração futura.

    `insumo_qualificacao_atualizado` é sempre um `bool` real quando esta
    estrutura é produzida.
    """

    dados_atualizados: DadosQualificacao = field(repr=False)
    correcoes_registradas: tuple[str, ...] = ()
    campos_em_conflito: tuple[str, ...] = ()
    insumo_qualificacao_atualizado: bool = False


def atualizar_dados_atendimento(
    dados_vigentes: DadosQualificacao,
    interpretacao: Interpretacao,
) -> ResultadoAtualizacaoDados:
    """Aplica a política de dados e correções da etapa 6.

    Função pura e total sobre entradas válidas: sem I/O, sem rede, sem relógio,
    sem persistência, sem LLM e sem mutação dos argumentos.

    A `Interpretacao` é **verificada como canônica válida** antes de qualquer
    produção, **reutilizando** a validação já existente da fronteira N-b —
    nenhum validador paralelo é criado e nenhuma regra é copiada. Os
    `dados_vigentes` são validados estruturalmente. Entrada inválida
    **bloqueia**: **nenhuma saída parcial** é produzida.

    A fronteira **não sabe** se o atendimento veio de `ATENDIMENTO_ATIVO`, de
    **T36**, de **T37** ou de um primeiro contato: quem fornece os
    `dados_vigentes` corretos é o chamador. Dados vazios representam um
    atendimento novo sem herança; dados preenchidos representam a preservação de
    um atendimento já existente.

    Somente `dados_extraidos` e `correcoes` são consumidos da `Interpretacao`;
    todo o restante dela é **neutro** aqui.

    :raises TypeError: tipo runtime incompatível em `dados_vigentes`, em um dos
        seis campos vigentes ou em `interpretacao`.
    :raises ValueError: `convidados` vigente negativo, ou erro de contrato
        `E-Nb-*` na `Interpretacao` recebida.
    """
    vigentes = _validar_dados_vigentes(dados_vigentes)
    validada = _validar_interpretacao_canonica(interpretacao)

    extraidos = validada.dados_extraidos
    corrigidos = _campos_corrigidos(validada)

    finais: dict[str, object] = {}
    correcoes_registradas: list[str] = []
    campos_em_conflito: list[str] = []

    for campo in _CAMPOS_DADOS:
        anterior = _vigente(vigentes, campo)
        recebido = extraidos._valor(campo)
        confianca = extraidos._confianca(campo)

        # Ausente no turno, ou presente com `BAIXA`: preserva o vigente, sem
        # correção, sem conflito e sem mutação.
        if recebido is None or confianca is not Confianca.ALTA:
            finais[campo] = anterior
            continue

        corrigido = campo in corrigidos

        if anterior is None or _mesmo_valor(anterior, recebido):
            # Vigente ausente → admite; vigente estritamente igual → idempotente.
            finais[campo] = recebido
            if corrigido:
                correcoes_registradas.append(campo)
            continue

        if corrigido:
            # Correção explícita sobrescreve (§7, §4 passos 3 e 9).
            finais[campo] = recebido
            correcoes_registradas.append(campo)
            continue

        # Contradição sem correção explícita: **não gravar**, e preservar a
        # evidência para que o pedido de confirmação seja possível a jusante.
        finais[campo] = anterior
        campos_em_conflito.append(campo)

    atualizados = DadosQualificacao(
        atendimento=DadosAtendimento(
            tipo_evento=finais["tipo_evento"],  # type: ignore[arg-type]
            data_nomeada=finais["data_nomeada"],  # type: ignore[arg-type]
            convidados=finais["convidados"],  # type: ignore[arg-type]
        ),
        nome=finais["nome"],  # type: ignore[arg-type]
        contato=finais["contato"],  # type: ignore[arg-type]
        formato=finais["formato"],  # type: ignore[arg-type]
    )

    mutou = any(
        not _mesmo_valor(_vigente(vigentes, campo), finais[campo])
        for campo in _CAMPOS_DADOS
    )

    return ResultadoAtualizacaoDados(
        dados_atualizados=atualizados,
        correcoes_registradas=tuple(correcoes_registradas),
        campos_em_conflito=tuple(campos_em_conflito),
        insumo_qualificacao_atualizado=mutou,
    )

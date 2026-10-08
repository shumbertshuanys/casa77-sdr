# 00 — Estado Atual

Snapshot curto do projeto. Histórico no Git/GitHub; contratos em `docs/06` e `docs/07`;
dados comerciais só em `knowledge/casa77.yaml`.

## Onde estamos

- **Etapa macro:** 3 — Motor de respostas (em execução). Roadmap em `docs/05-roadmap.md`.
- **Marco corrente:** **M2 — primeiro teste conversacional local:** código concluído;
  validação com LLM real pendente (Victor). Plano:
  `docs/superpowers/plans/2026-10-07-orquestrador-m2.md`.
- **Marcos:** M1 runtime local parcial — **feito** · M2 — **código concluído, validação
  pendente** · M3 produção — não iniciado.

## O que já funciona (com testes)

- Base de conhecimento carregável e validada: YAML comercial, índice de respostas aprovadas,
  mapa de cobertura (54 assuntos: 33 cobertos, 21 sem cobertura → handoff).
- Normalização e idempotência da mensagem; recuperação de contexto e elegibilidade.
- Interpretação da mensagem por LLM (Anthropic) com saída estruturada e canonicalização.
- Resolução de identidade do atendimento; máquina de estados (T01–T41, 20 ações).
- Regras comerciais, qualificador, decisão de cobertura (S2-D8), aplicabilidade de pacote.
- Produtores de eventos, seleção de fatos, composição, montagem e validação da resposta.
- Persistência **em memória** com marco de transição.
- **Ciclo completo** `casa77_sdr.orchestrator.processar_mensagem` (etapas 1–14), via
  `motor_deps`, `hydration`, `orchestrator_identity`, `alerta_operacional`,
  `orchestrator_decision`, `orchestrator_emission`, `handoff_summary`, `orchestrator_persist`.
- REPL local `scripts/conversar_local.py` (precisa de `ANTHROPIC_API_KEY` no ambiente):
  `python scripts/conversar_local.py --janela-idempotencia-segundos <s>
  --limiar-recencia-dias <d> --model <modelo> --max-tokens <n> --timeout <s>`.
- Suíte: 9565 testes passando.

## O que falta

- **Validação com LLM real (Victor):** smoke de interpretação, evals em
  `evals/interpretacao` e conversas no REPL. Nunca rodaram com a API real.
- **Lacuna de produto:** 8 ações da máquina não têm texto aprovado, então o bot fica em
  silêncio nessas situações: `APRESENTAR_ATENDIMENTO_INICIAL`, `PERGUNTAR_PROXIMO_CAMPO_AUSENTE`,
  `PERGUNTAR_FORMATO`, `RETOMAR_COLETA_SEM_REPETIR`, `INFORMAR_REGRA_INCOMPATIVEL`,
  `INFORMAR_RESSALVA_DE_CAPACIDADE`, `DESPEDIR_SEM_CONTINUIDADE`, `REFORCAR_ENCAMINHAMENTO`.
  É hoje o principal bloqueador de uma conversa útil. (`EMITIR_MENSAGEM_DE_ENCAMINHAMENTO`
  já está mapeada ao texto aprovado R08/F1.)

## Bloqueadores de produção conhecidos (M3)

- Regra 5 do doc 06 §10 não é aplicada: após falha na entrega do resumo, ciclos seguintes
  prosseguem; recuperação manual via alerta + `pendente` preservado.
- Fatos de calendário fixos em "sem calendário" (`consulta_calendario_valida: False`);
  religar quando o calendário for integrado.
- Resposta degradada com LLM indisponível (N-b-M4 R03 + handoff) não é emitida: o ciclo
  preserva e alerta em silêncio.
- Reescrita por LLM da etapa 10 não é usada (só texto aprovado literal).

## Decisões pendentes (bloqueiam o M3, não o M2)

| Decisão | Dono |
|---|---|
| Persistência real (banco) | Victor |
| Destino do alerta operacional | Victor |
| Limiar de recência (valor) | Victor |
| Provedor e número do WhatsApp | Victor |
| Calendário (Google Calendar?) | Victor |
| Destino do registro de leads | Victor |
| Canal e SLA do handoff | Victor / Douglas |
| Textos aprovados para as 8 ações sem texto (lista em "O que falta") | Douglas |

Lacunas comerciais: `knowledge/informacoes-pendentes.md`.

## Questões técnicas abertas que não bloqueiam

E1 (conversa × atendimento × lead), E3 (evento novo em atendimento ativo), S2-D5, S2-D7,
unicidade geral de `id_atendimento`, retorno do controle ao bot após atendimento humano.
Detalhes em `docs/07` §12.

## Próxima ação

1. Victor roda smoke, evals e REPL com a credencial.
2. Douglas aprova os 8 textos.
3. Então planejar o M3.

# 00 — Estado Atual

Snapshot curto do projeto. Histórico no Git/GitHub; contratos em `docs/06` e `docs/07`;
dados comerciais só em `knowledge/casa77.yaml`.

## Onde estamos

- **Etapa macro:** 3 — Motor de respostas (em execução). Roadmap em `docs/05-roadmap.md`.
- **Marco corrente:** **M2.1 — conversa útil: concluído** (aguarda merge). Textos aprovados
  ligados ao motor, parágrafos contínuos, formato não perguntado, coleta retomada após cada
  resposta. Plano: `docs/superpowers/plans/2026-10-08-m2-1-conversa-util.md`.
- **Marcos:** M1 runtime local parcial — **feito** · M2 — código concluído, validação com
  LLM real pendente · **M2.1 — feito** · M3 produção — não iniciado.

## O que já funciona (com testes)

- Base de conhecimento carregável e validada: YAML comercial, índice de respostas aprovadas,
  mapa de cobertura (54 assuntos: 33 cobertos, 21 sem cobertura → handoff).
- Normalização e idempotência da mensagem; recuperação de contexto e elegibilidade.
- Interpretação da mensagem por LLM (Anthropic) com saída estruturada e canonicalização.
- Resolução de identidade do atendimento; máquina de estados (T01–T41, 20 ações).
- Regras comerciais, qualificador, decisão de cobertura (S2-D8), aplicabilidade de pacote.
- Eventos, seleção de fatos, composição, montagem e validação da resposta; persistência
  **em memória** com marco de transição.
- **Ciclo completo** `casa77_sdr.orchestrator.processar_mensagem` (etapas 1–14), via
  `motor_deps`, `hydration`, `orchestrator_identity`, `alerta_operacional`,
  `orchestrator_decision`, `orchestrator_emission`, `handoff_summary`, `orchestrator_persist`.
- REPL local com a assinatura Claude logada (sem `ANTHROPIC_API_KEY`):
  `python scripts/conversar_local.py --provedor claude-code --model sonnet --timeout 120 --janela-idempotencia-segundos 60 --limiar-recencia-dias 30`.
- Conversa útil (M2.1): saudação R01 no 1º contato; pergunta do primeiro campo ausente na
  ordem tipo de evento, data, convidados, nome (R31); o contato vem do identificador do canal
  (docs/06 §6); após resposta comercial, R32 + próxima pergunta (sem R32 na 1ª mensagem);
  ressalva R34 sem perguntar formato; R35, R15. Aceitação: `tests/test_ciclo_completo.py`.
- Suíte: 9709 testes passando.

## O que falta

- **Validação com LLM real (Victor):** smoke de interpretação, evals em
  `evals/interpretacao` e conversas no REPL. Nunca rodaram com a API real.
- **R33/F2 (horário além do limite):** ainda sem gatilho; a ressalva R34 chega ao fim da
  qualificação (T08), não no meio da coleta.
- `PERGUNTAR_FORMATO` segue sem texto, por decisão do Victor (formato não é obrigatório).
- **Lacunas conhecidas (M2.1):** R01 pergunta o tipo de evento mesmo já informado, e a 1ª
  mensagem comercial vem sem saudação (precisam de variante aprovada); o texto de capacidade
  (R33/F1, R17) repete a cada turno em `incompativel`; a confirmação R31/F5 fica adiada.

## Bloqueadores de produção conhecidos (M3)

- Regra 5 do doc 06 §10 não é aplicada: após falha na entrega do resumo, ciclos seguintes
  prosseguem; recuperação manual via alerta + `pendente`.
- Fatos de calendário fixos em "sem calendário" (`consulta_calendario_valida: False`);
  religar quando o calendário for integrado.
- Resposta degradada com LLM indisponível (N-b-M4 R03 + handoff) não é emitida: preserva e alerta.
- Reescrita por LLM da etapa 10 não é usada (só texto aprovado literal).
- Falha de `enviar_mensagem` no texto principal impede `entregar_resumo`: sem alerta nem
  `pendente`, estado `encaminhado_humano` gravado e chave marcada (handoff perdido).

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

Lacunas comerciais: `knowledge/informacoes-pendentes.md`.

## Questões técnicas abertas que não bloqueiam

E1 (conversa × atendimento × lead), E3 (evento novo em atendimento ativo), S2-D5, S2-D7, unicidade
de `id_atendimento`, retorno do controle ao bot após atendimento humano (`docs/07` §12).

## Próxima ação

1. Victor testa no REPL (`--provedor claude-code`), roda smoke e evals com a credencial.
2. Então planejar o M3.

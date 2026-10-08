# 00 — Estado Atual

Snapshot curto do projeto. Histórico no Git/GitHub; contratos em `docs/06` e `docs/07`;
dados comerciais só em `knowledge/casa77.yaml`.

## Onde estamos

- **Etapa macro:** 3 — Motor de respostas (em execução). Roadmap em `docs/05-roadmap.md`.
- **Marco corrente:** **M2 — primeiro teste conversacional local.** Plano:
  `docs/superpowers/plans/2026-10-07-orquestrador-m2.md`.
- **Marcos:** M1 runtime local parcial — **feito** · M2 — **em execução** · M3 produção —
  não iniciado.

## O que já funciona (com testes)

- Base de conhecimento carregável e validada: YAML comercial, índice de respostas aprovadas,
  mapa de cobertura (54 assuntos: 33 cobertos, 21 sem cobertura → handoff).
- Normalização e idempotência da mensagem; recuperação de contexto e elegibilidade.
- Interpretação da mensagem por LLM (Anthropic) com saída estruturada e canonicalização.
- Resolução de identidade do atendimento; máquina de estados (T01–T41, 20 ações).
- Regras comerciais, qualificador, decisão de cobertura (S2-D8), aplicabilidade de pacote.
- Produtores de eventos (interpretação, internos E07/E08/E09, handoff E18, encerramento E14)
  e montagem de `CondicoesCiclo`.
- Seleção de fatos, composição, montagem e validação da resposta final.
- Persistência **em memória** com marco de transição.
- Orquestrador recorte R1: etapas 1–3 + tratamento de bloqueio TS45.

## O que falta para o M2

Ligar as peças num ciclo único `processar_mensagem` (etapas 4–14): identidade em runtime,
decisão da máquina, emissão, persistência e envio; depois um REPL local e a primeira
execução dos evals/smoke de interpretação. Detalhe por tarefa no plano.

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
| Textos ainda sem aprovação (coleta, formato, retomada, esclarecimento, reforço de encaminhamento) | Douglas |

Lacunas comerciais: `knowledge/informacoes-pendentes.md`.

## Questões técnicas abertas que não bloqueiam

E1 (conversa × atendimento × lead), E3 (evento novo em atendimento ativo), S2-D5, S2-D7,
unicidade geral de `id_atendimento`, retorno do controle ao bot após atendimento humano.
Detalhes em `docs/07` §12.

## Próxima ação

Executar o plano do M2, começando pela Task 1 (raiz de composição).

# 00 — Estado Atual do Projeto

Documento de estado: registra etapa, subetapa, PRs, commits, testes e próxima ação.
**Não contém dado comercial.** Preço, capacidade, tipo de evento, horário, restrição e
qualquer outra condição vivem exclusivamente em `knowledge/casa77.yaml`.

Atualizado em: 2026-08-15.

## Referências

| Item | Valor |
|---|---|
| Projeto | Casa 77 SDR |
| Branch de referência | `main` |
| Último commit **funcional** aprovado | `00fd1d47da649c493af240a5393b51f02e82009b` |
| Merge correspondente na `main` | `26ab907e3b8874a2586cb7f510c287f50aee0e36` |
| Última subetapa **funcional** concluída | 3B.1 — Carregador validado do YAML (PR #3) |
| Subetapa 3B.2 | **NÃO INICIADA** |

## Histórico verificado de entregas

| Entrega | Tipo | Evidência |
|---|---|---|
| Fundação do projeto (etapa 1 — base de conhecimento) | documental | commit `6bf98ef`, direto na `main` |
| Etapa 2 — máquina de estados (`docs/06`) | documental | PR #1 (`3323105`, merge `2ec5d79`) |
| Etapa 3A — arquitetura do motor (`docs/07`) | documental | PR #2 (`03ecd5d`, merge `0a9e584`) |
| Etapa 3B.1 — carregador validado do YAML (`src/casa77_sdr/knowledge.py` + testes) | **funcional** | PR #3 (`00fd1d4`, merge `26ab907`) |
| Auditoria/reconciliação do legado n8n | saneamento/auditoria (read-only, artefatos fora do repo) | export histórico analisado; estado operacional atual do n8n não registrado como marco aprovado neste documento |
| Saneamento comercial/documental — arbitragem D1–D8 | comercial/documental | PR #4 — **ABERTO, não integrado à `main`**; estado definitivo será registrado após o merge |

O PR #4 atualiza base comercial e documentação a partir de decisões de Douglas Bianchi
(2026-08-15). Ele **não** é implementação funcional do motor e não altera o marco
funcional acima.

## Testes

Última execução real: `python -m pytest -q` sobre a branch do PR #4 em 2026-08-15 —
`48 passed`. A suíte cobre o carregador da 3B.1 (`tests/test_knowledge.py`).

## Roadmap (resumo — detalhe em `docs/05-roadmap.md`)

Etapas 1 e 2 concluídas; etapa 3 em execução (3A e 3B.1 entregues; 3B.2 não iniciada);
etapas 4 a 10 não iniciadas.

## Próxima ação

1. Decisão humana sobre o merge do PR #4.
2. Após o merge, a 3B.2 só começa com pedido específico (regra do projeto).

## Pendências que não bloqueiam

- Itens pendentes da base: ver `knowledge/informacoes-pendentes.md` (fonte única das
  lacunas; não replicar aqui).

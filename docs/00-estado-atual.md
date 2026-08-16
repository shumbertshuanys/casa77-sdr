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
| Último commit **funcional** aprovado | `24556ea0ec20173a9d58e5b7c99a5317b6b51898` |
| Merge correspondente na `main` | `d5781130c3ff402aef19728f50120cbd31474ad1` |
| Última subetapa **funcional** concluída | 3B.2 — Regras comerciais determinísticas (PR #7) |
| Subetapa 3B.2 | **CONCLUÍDA** |

## Histórico verificado de entregas

| Entrega | Tipo | Evidência |
|---|---|---|
| Fundação do projeto (etapa 1 — base de conhecimento) | documental | commit `6bf98ef`, direto na `main` |
| Etapa 2 — máquina de estados (`docs/06`) | documental | PR #1 (`3323105`, merge `2ec5d79`) |
| Etapa 3A — arquitetura do motor (`docs/07`) | documental | PR #2 (`03ecd5d`, merge `0a9e584`) |
| Etapa 3B.1 — carregador validado do YAML (`src/casa77_sdr/knowledge.py` + testes) | **funcional** | PR #3 (`00fd1d4`, merge `26ab907`) |
| Auditoria/reconciliação do legado n8n | saneamento/auditoria (read-only) | **Auditoria S0.2 concluída e aprovada em 2026-08-15.** O workflow legado atual foi verificado read-only e classificado como histórico/inativo. Matriz e conclusões sanitizadas em `docs/08-reconciliacao-legado-n8n.md` |
| Saneamento comercial/documental — arbitragem D1–D8 | comercial/documental | PR #4 — **INTEGRADO à `main`** em 2026-08-15 (head `190704e622d1c62767a38027bc19cd191583d472`, merge `954484a279ef19957c2a8bb6c2c159810da493f2`) |
| Etapa 3B.2 — regras comerciais determinísticas (`RegrasComerciais` em `src/casa77_sdr/rules.py` + testes), avaliando dados do interessado contra a base carregada pela 3B.1 | **funcional** | PR #7 (commit funcional `24556ea`, merge `d578113`) |

O PR #4 atualiza base comercial e documentação a partir de decisões de Douglas Bianchi
(2026-08-15). Ele **não** é implementação funcional do motor e não altera o marco
funcional acima.

## Testes

Última execução real: `python -m pytest -q -p no:cacheprovider` sobre a `main`
pós-merge do PR #7 em 2026-08-15 — `72 passed`. A suíte cobre o carregador/validação
da base (3B.1, `tests/test_knowledge.py`) e as regras comerciais determinísticas
(3B.2, `tests/test_rules.py`).

## Roadmap (resumo — detalhe em `docs/05-roadmap.md`)

Etapas 1 e 2 concluídas; etapa 3 em execução (3A, 3B.1 e 3B.2 entregues; próxima
subetapa funcional ainda não iniciada); etapas 4 a 10 permanecem conforme
`docs/05-roadmap.md`.

## Próxima ação

1. Definir formalmente a próxima subetapa funcional da Etapa 3B com base no grafo de
   dependências da arquitetura (`docs/07`) e nas entregas já integradas (3B.1 e 3B.2).
2. Como isso envolve desenho técnico e dependências entre componentes, o próximo passo
   deve ser planejado pelo Claude Desktop e auditado pelo GPT antes da execução.
3. Nenhuma nova subetapa funcional está iniciada até aprovação explícita desse
   planejamento.

## Pendências que não bloqueiam

- Itens pendentes da base: ver `knowledge/informacoes-pendentes.md` (fonte única das
  lacunas; não replicar aqui).

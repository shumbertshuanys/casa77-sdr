# 00 — Estado Atual do Projeto

Documento de estado: registra etapa, subetapa, PRs, commits, testes e próxima ação.
**Não contém dado comercial.** Preço, capacidade, tipo de evento, horário, restrição e
qualquer outra condição vivem exclusivamente em `knowledge/casa77.yaml`.

Atualizado em: 2026-08-16.

## Referências

| Item | Valor |
|---|---|
| Projeto | Casa 77 SDR |
| Branch de referência | `main` |
| Último commit **funcional** aprovado | `02dcb477ea893a6092d62be1a6fa02262fb0a81c` |
| Merge correspondente na `main` | `55f6ed77e32489b2d16e65dde94fbc276ac1af2b` |
| Última subetapa **funcional** concluída | 3B.5 — Qualificador determinístico (PR #14) |
| Subetapa 3B.5 | **CONCLUÍDA** |

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
| Etapa 3B.3 — persistência operacional (`src/casa77_sdr/persistence.py` + testes): contrato abstrato, implementação em memória exclusivamente para testes, idempotência, recuperação de estado, proteção do vínculo de identidade e processamento pendente | **funcional** | PR #9 (commit funcional `6efe191`, merge `9846357`) |
| Etapa 3B.4 — normalização de entrada (`src/casa77_sdr/normalization.py` + testes): contrato comum de entrada, normalização técnica conservadora e produção da chave de idempotência — origem por identificador do canal ou fallback composto, chave opaca e janela temporal parametrizada sem valor padrão | **funcional** | PR #11 (commit funcional `526591f`, merge `78c6555`) |
| Etapa 3B.5 — qualificador determinístico (`src/casa77_sdr/qualification.py` + testes): os cinco resultados oficiais a partir de contrato próprio por composição, com violações recebidas da 3B.2 em vez de recalculadas, capacidade lida dinamicamente da base e precedência determinística — sem pacote, sem handoff e sem transição de estado | **funcional** | PR #14 (commit funcional `02dcb47`, merge `55f6ed7`) |

O PR #4 atualiza base comercial e documentação a partir de decisões de Douglas Bianchi
(2026-08-15). Ele **não** é implementação funcional do motor e não altera o marco
funcional acima.

## Testes

Última execução real: `python -m pytest -q -p no:cacheprovider` sobre a `main`
pós-merge do PR #14 em 2026-08-16 — `180 passed`. A suíte cobre o carregador/validação
da base (3B.1, `tests/test_knowledge.py`), as regras comerciais determinísticas
(3B.2, `tests/test_rules.py`), a persistência operacional em memória
(3B.3, `tests/test_persistence.py`), a normalização de entrada com a chave de
idempotência (3B.4, `tests/test_normalization.py`) e a qualificação determinística
(3B.5, `tests/test_qualification.py`).

## Roadmap (resumo — detalhe em `docs/05-roadmap.md`)

Etapas 1 e 2 concluídas; etapa 3 em execução (3A, 3B.1, 3B.2, 3B.3, 3B.4 e 3B.5
entregues; próxima subetapa funcional **não iniciada**). A antiga Etapa 4 —
Qualificação — continua absorvida pela Etapa 3B conforme a arbitragem S1, e o
`Qualificador` foi **implementado na 3B.5**. A `MaquinaEstados` continua **não
implementada**. Etapas 5 a 10 permanecem futuras e com a numeração preservada, conforme
`docs/05-roadmap.md`.

## Próxima ação

1. Nenhuma nova subetapa funcional está iniciada e nenhuma numeração futura está
   aprovada.
2. A próxima entrega deve ser definida formalmente a partir do grafo de dependências da
   arquitetura (`docs/07`) no estado posterior à 3B.5.
3. Como isso envolve arquitetura e dependências entre componentes, o próximo passo deve
   ser planejado pelo Claude Desktop e auditado pelo GPT antes de qualquer execução pelo
   Claude Code.
4. A `MaquinaEstados` está arquiteturalmente desbloqueada pela conclusão do
   `Qualificador` — o que **não** significa que sua implementação esteja aprovada ou
   iniciada.
5. O planejamento deve continuar considerando explicitamente as pendências técnicas em
   aberto registradas abaixo.

## Arbitragens concluídas

Decisões de governança já tomadas. Não criam marco funcional nem código.

| # | Arbitragem | Decisão | Evidência |
|---|---|---|---|
| A | Fronteira de Qualificação entre `docs/05-roadmap.md` e `docs/07-arquitetura-motor-respostas.md` | **ARBITRADA** (S1): o `Qualificador` permanece componente do motor e sua implementação pertence à Etapa 3B; a antiga Etapa 4 deixa de ser aberta como etapa autônoma e é absorvida pela 3B; as etapas 5 a 10 mantêm a numeração; o `Qualificador` precede a `MaquinaEstados`. O `Qualificador` foi **implementado na 3B.5** (PR #14); a precedência permanece e a `MaquinaEstados` **ainda não foi iniciada**. | reconciliação documental de `docs/05`, `docs/07` §8.4/§9 e deste documento |

## Pendências técnicas em aberto

Registradas aqui como estado, não resolvidas nesta entrega.

| # | Pendência | Antes de quê precisa ser arbitrada |
|---|---|---|
| B | Colisão conceitual de nome: `RegistroAtendimento` já existe em `src/casa77_sdr/persistence.py` como dataclass de transporte, enquanto `docs/07` usa o mesmo nome para uma responsabilidade futura | implementar o componente `RegistroAtendimento` descrito em `docs/07` |
| C | Não existe contrato estruturado, legível por máquina, relacionando as respostas aprovadas (`Rxx`) aos campos do YAML | implementar `ValidadorConsistenciaBase` e, em cascata, `SeletorFatos` e `ValidadorResposta` |

## Pendências que não bloqueiam

- Itens pendentes da base: ver `knowledge/informacoes-pendentes.md` (fonte única das
  lacunas; não replicar aqui).

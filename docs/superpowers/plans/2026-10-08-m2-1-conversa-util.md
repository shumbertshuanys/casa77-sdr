# M2.1 — Conversa útil — Plano

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** O bot passa a cumprimentar, responder e continuar a coleta numa conversa natural, com os 12 textos aprovados pelo Victor em 2026-10-08, sem quebras de linha no meio de frase.

**Architecture:** Os textos entram na base aprovada (`knowledge/respostas-aprovadas.md` + `knowledge/indice-respostas-aprovadas.yaml`) pelo mesmo contrato C já vigente; o `ProjetorEmissao` (`src/casa77_sdr/emission_projection.py`) ganha o mapeamento ação → fragmento, escolhendo o fragmento por dado estruturado (campo ausente, motivo da violação). A regra de formato muda por decisão do Victor.

**Tech Stack:** Python ≥ 3.13, PyYAML, pytest.

**Spec:** `docs/07-arquitetura-motor-respostas.md` §2.3 (contrato C), §4.1.5 (PE-*), §4.5; `docs/02-fluxo-comercial.md` §4; decisões do Victor abaixo.

## Global Constraints

- Nenhum valor comercial no código ou nos textos: valores entram por *binding* `RENDERIZADO` a caminho do `knowledge/casa77.yaml` (`{{...}}`).
- Textos exatamente como aprovados (abaixo); só os marcadores `[...]` viram *bindings*.
- Suíte verde com `python -m pytest -q -W error` (baseline 9630).
- Um PR para o M2.1; merge com autorização do Victor.

## Textos aprovados (fonte: artifact https://claude.ai/artifact/3MSdWsLrMzf2MjUgxGiXHF, coleção `decisoes`)

| Ação | Situação | Texto aprovado |
|---|---|---|
| `APRESENTAR_ATENDIMENTO_INICIAL` | 1º contato | R01 existente → status APROVADO |
| `PERGUNTAR_PROXIMO_CAMPO_AUSENTE` | falta nome | Pra eu registrar certinho, qual é o seu nome? |
| idem | falta tipo de evento | Que tipo de evento você está planejando? |
| idem | falta data | Qual é a data que você tem em mente para o evento? |
| idem | falta convidados | Quantos convidados você pretende receber, mais ou menos? |
| idem | falta contato | Posso usar este número de WhatsApp para o responsável comercial falar com você? |
| `RETOMAR_COLETA_SEM_REPETIR` | voltar à coleta (seguido da pergunta do campo) | Voltando ao seu evento, pra eu completar as informações: |
| `INFORMAR_REGRA_INCOMPATIVEL` | acima da capacidade | A Casa 77 recebe até [capacidade.formato_coquetel] convidados, então para esse número de pessoas o espaço não comporta o evento. |
| idem | horário além do limite | O evento precisa terminar até as [horario_limite], mesmo com hora adicional. Esse limite não pode ser estendido. |
| `INFORMAR_RESSALVA_DE_CAPACIDADE` | só cabe coquetel | Para esse número de convidados, o evento precisa ser no formato coquetel. Com todos sentados, a casa comporta até [capacidade.convidados_sentados]. |
| `DESPEDIR_SEM_CONTINUIDADE` | sem interesse | R15 existente → status APROVADO |
| `REFORCAR_ENCAMINHAMENTO` | após handoff | Sua conversa já está com o responsável comercial, que vai falar com você para dar sequência. |

**Decisão do Victor (formato):** o bot **não pergunta** o formato. Acima de `capacidade.convidados_sentados` convidados (até `formato_coquetel`), o bot envia a ressalva de capacidade e segue; o formato **deixa de ser campo obrigatório** da qualificação. `PERGUNTAR_FORMATO` fica sem texto (silenciosa por decisão).

---

### Task 1: Texto contínuo — sem quebra de linha no meio de frase

Os blocos aprovados são escritos com quebra manual de linha no Markdown; a emissão hoje preserva essas quebras. Unir linhas de um mesmo parágrafo com espaço, preservando a separação entre parágrafos/fragmentos (`"\n\n"`, PC-3). A normalização deve acontecer **num único ponto** da cadeia (extração do texto canônico ou montagem), de modo que composição, montagem e `ValidadorResposta` continuem consistentes (validação literal sobre o mesmo texto). Atualizar contratos/testes que pinem quebras internas; registrar a decisão no PR.

- [ ] Teste que falha: a composição de `R06/F1` não contém `"\n"` interno e preserva o texto palavra por palavra.
- [ ] Implementar no ponto único; suíte verde; commit `fix: emit approved text as continuous paragraphs`.

### Task 2: Textos aprovados na base + mapeamento ação → fragmento

- [ ] R01 e R15 → APROVADO (Markdown e índice).
- [ ] Novos `Rxx` (próximos números livres) com os textos da tabela, *bindings* `RENDERIZADO` para os marcadores, registrados no índice com status APROVADO, cumprindo todos os validadores do contrato C (bijeção, correspondência, marcadores, status) e o mapa de cobertura onde aplicável.
- [ ] `emission_projection.py`: mapear cada ação da tabela ao(s) fragmento(s). Seleção determinística: `PERGUNTAR_PROXIMO_CAMPO_AUSENTE` → fragmento do **primeiro** campo de `qualificacao.campos_ausentes` (ordem já definida pelo `Qualificador`); `RETOMAR_COLETA_SEM_REPETIR` → texto de retomada **seguido** da pergunta do próximo campo; `INFORMAR_REGRA_INCOMPATIVEL` → fragmento pelo motivo da violação (capacidade / horário; tipo de evento não aceito continua R17). Nenhum `Rxx` dentro da `MaquinaEstados` (§4.5).
- [ ] Atualizar docs/07 §4.1.5 (PE-*) só no que mudou; testes de projeção, montagem e ponta a ponta.

### Task 3: Formato deixa de ser obrigatório

- [ ] `qualification.py`: remover `formato` de `campos_ausentes`; acima de `convidados_sentados` sem formato informado → não bloqueia; formato `SENTADO` acima de `convidados_sentados` continua violação.
- [ ] Garantir que, acima de `convidados_sentados`, a ação `INFORMAR_RESSALVA_DE_CAPACIDADE` é emitida (verificar na máquina de estados de onde ela vem; se depender de formato ausente, ajustar a condição mínima).
- [ ] Atualizar `docs/02-fluxo-comercial.md` §4 (regra do formato) e testes.

### Task 4: Cenário de aceitação

- [ ] `tests/test_ciclo_completo.py`: a mensagem "Ola boa noite. Muito linda a casa, tenho interesse visitar." em atendimento novo (produtor fake com interpretação equivalente: saudação + interesse em visita) produz **uma** mensagem com saudação (R01), visita (R06) e a próxima pergunta de coleta, sem `"\n"` interno a parágrafo.
- [ ] Conversa de 4 mensagens chega a `pronto_para_handoff`/`encaminhado_humano` com resumo e R08.
- [ ] Atualizar `docs/00-estado-atual.md` (≤ 80 linhas).

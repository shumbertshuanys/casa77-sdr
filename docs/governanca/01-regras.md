# Governança 01 — Regras Permanentes (v3, modo entrega)

Regras estáveis do projeto Casa 77 SDR. Não contém estado corrente nem valor comercial.

A v3 substitui o fluxo de mandato/auditoria por entrega (GPT → Claude Desktop → GPT →
Claude Code) por um ciclo **plano → execução com revisão automática → aprovação humana**.
O objetivo é entregar o produto; a documentação existe para servir ao código, não o inverso.

---

## 1. Papéis

| Quem | Faz |
|---|---|
| **Victor** (dono do projeto) | aprova cada plano de marco, autoriza merge, toma decisões de produto e de fornecedor |
| **Douglas Bianchi** | aprova textos ao cliente e qualquer dado comercial; mantém os poderes reservados (§6) |
| **Claude Code** | planeja, implementa, testa, revisa (com subagente revisor) e abre o PR |
| **GPT** (opcional) | auditoria externa **uma vez por marco**, se o Victor quiser |

## 2. Ciclo de trabalho

1. **Plano por marco** em `docs/superpowers/plans/` — tarefas pequenas, com testes. O Victor
   aprova o plano uma vez.
2. **Execução das tarefas do plano em sequência, sem pedir autorização a cada uma.** Cada
   tarefa: teste que falha → implementação → suíte verde → commit → revisão por subagente.
3. **Um PR por marco** (ou por grupo coerente de tarefas), com CI verde.
4. **Merge só com autorização explícita do Victor.**

**Parar e perguntar** somente quando:

- a decisão é **comercial** ou de **texto ao cliente** (vai para o Douglas);
- a decisão é de **fornecedor, custo ou tecnologia nova** (vai para o Victor — §5);
- há **credencial** nova, **risco de segurança** ou ação **destrutiva**;
- o plano aprovado está errado de forma que muda o resultado entregue.

Lacuna **técnica** não coberta pelo contrato existente: o executor decide a opção mais
simples compatível com §6 e registra a decisão em 1–3 linhas na descrição do PR. Não abre
arbitragem documental.

## 3. Documentação

| Arquivo | Regra |
|---|---|
| `docs/00-estado-atual.md` | **≤ 80 linhas**. Atualizado no PR que fecha um marco ou muda bloqueador. Sem histórico |
| `docs/07`, `docs/06` | referência dos contratos já vigentes. **Não crescem por microdecisão**; só mudam quando um contrato vigente muda de verdade |
| decisões técnicas novas | descrição do PR (histórico no GitHub) |
| planos | `docs/superpowers/plans/` |
| `knowledge/` | autoridade comercial — só muda com aprovação do Douglas |

Proibido: PR só de reconciliação documental, ledger, changelog manual, repetir o mesmo fato
em vários documentos.

## 4. Qualidade (não negociável)

- TDD: teste que falha antes da implementação; suíte completa verde antes de cada commit.
- CI verde (`python -m pytest -W error`, Python 3.13 e 3.14) antes do merge.
- Teste determinístico: sem retry, `sleep`, `skip`/`xfail` para esconder falha.
- "Existe" não significa "funciona": evidência é teste com saída real.
- Simplicidade de MVP: sem microsserviço, abstração prematura ou dependência desnecessária.

## 5. Tecnologia e fornecedores

Nenhuma escolha de framework, banco, provedor de WhatsApp, hospedagem, calendário, CRM ou
modelo de IA é automática. Comparar no máximo duas opções, recomendar uma, **aguardar o
Victor**.

## 6. Regras comerciais e LLM (inalteradas)

- `knowledge/casa77.yaml` é a única autoridade comercial. Ausente, `null`, `pendente` ou
  conflitante → pendência e **handoff humano**. Nunca inventar nem copiar valor comercial
  para código, prompt, teste ou documento.
- O bot **não** fecha contrato, concede desconto, confirma reserva/visita/disponibilidade,
  recebe pagamento, aprova cancelamento, altera datas, cria exceção nem muda condição.
- O LLM **não** calcula preço, escolhe pacote, valida capacidade, confirma disponibilidade
  nem decide regra comercial. Pode interpretar, extrair, classificar, redigir e resumir.

## 7. Segurança e repositório público

- Nenhum segredo, token, `.env`, credencial, dado pessoal desnecessário, webhook ou export
  bruto versionado. O repositório é tratado como público.
- Credencial nova: parar e orientar o Victor a configurá-la sem colá-la no chat.
- Serviço externo (n8n, WhatsApp, calendário): **read-only** até autorização explícita.

## 8. Git

- Branch por marco; commits pequenos com mensagem clara; merge commit normal.
- Sem `force`, `reset --hard`, `rebase`, `clean` ou `branch -D` sem autorização.
- Antes de push: sem `.env`, sem credencial, testes verdes.

## 9. Usuário

O Victor tem pouca experiência com terminal e Git. Toda ação manual pedida a ele traz: onde
executar, comando exato, resultado esperado e como confirmar. Preferir que o Claude Code
execute.

## 10. Mudança desta governança

Por PR, com aprovação do Victor.

# CLAUDE.md — Projeto Casa 77 SDR

Bot SDR que atende interessados na locação da Casa 77: responde dúvidas, informa preços e
condições aprovadas, coleta dados do evento, qualifica o lead e encaminha para Douglas
Bianchi. **Não** fecha contrato, **não** dá desconto, **não** confirma visita ou
disponibilidade sem humano.

## Como trabalhar

Regras completas: `docs/governanca/01-regras.md`. Em resumo:

1. Ler `docs/00-estado-atual.md` e o plano do marco em `docs/superpowers/plans/`.
2. Executar as tarefas do plano aprovado **em sequência, sem pedir autorização a cada uma**,
   com TDD (superpowers: `subagent-driven-development` ou `executing-plans`).
3. Suíte verde antes de cada commit: `python -m pytest -q`.
4. Lacuna técnica: escolher a opção mais simples compatível com as regras abaixo e registrar
   em 1–3 linhas na descrição do PR. **Não** abrir arbitragem nem editar `docs/07` por
   microdecisão.
5. Parar e perguntar apenas para: decisão comercial ou texto ao cliente (Douglas);
   fornecedor/tecnologia/custo (Victor); credencial; ação destrutiva; plano errado.
6. Merge só com autorização do Victor. Atualizar `docs/00-estado-atual.md` (≤ 80 linhas)
   no PR que fecha o marco.

## Regras invioláveis

- `knowledge/casa77.yaml` é a **única** fonte de preço, capacidade, horário, pacote e
  restrição. Nunca inventar, inferir ou copiar valor comercial para código, prompt, teste ou
  documento.
- Informação ausente, `null` ou `pendente` → handoff humano.
- Texto ao cliente só de `knowledge/respostas-aprovadas.md`; texto novo precisa de
  aprovação do Douglas.
- O LLM interpreta, extrai e redige; **nunca** decide preço, pacote, capacidade,
  disponibilidade ou exceção.
- Nenhum segredo, `.env` ou dado pessoal versionado.

## Onde está cada coisa

| Assunto | Arquivo |
|---|---|
| Estado e próximo passo | `docs/00-estado-atual.md` |
| Dados comerciais | `knowledge/casa77.yaml` |
| Respostas aprovadas | `knowledge/respostas-aprovadas.md` |
| Lacunas comerciais | `knowledge/informacoes-pendentes.md` |
| Conversa / handoff | `docs/03-regras-de-conversa.md`, `docs/04-handoff-humano.md` |
| Máquina de estados | `docs/06-maquina-de-estados.md` |
| Contratos do motor | `docs/07-arquitetura-motor-respostas.md` |
| Prompt de interpretação | `prompts/prompt-interpretacao.md` |

## Ambiente

Python ≥ 3.13. Instalar: `python -m pip install -e ".[dev]"`. Testes: `python -m pytest -q`.

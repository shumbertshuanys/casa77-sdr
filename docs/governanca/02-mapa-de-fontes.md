# Governança 02 — Mapa de Fontes

Onde está cada tipo de informação. Em divergência, vale a fonte desta tabela.

| Informação | Fonte |
|---|---|
| Código e estado técnico aprovado | GitHub `shumbertshuanys/casa77-sdr`, branch `main` |
| Progresso, bloqueadores, próximo passo | `docs/00-estado-atual.md` |
| Plano do marco corrente | `docs/superpowers/plans/` |
| Dados comerciais e operacionais | `knowledge/casa77.yaml` |
| Textos aprovados ao cliente | `knowledge/respostas-aprovadas.md` (+ índice `knowledge/indice-respostas-aprovadas.yaml`) |
| Lacunas comerciais | `knowledge/informacoes-pendentes.md` |
| Regras de conversa / handoff | `docs/03-regras-de-conversa.md`, `docs/04-handoff-humano.md` |
| Máquina de estados | `docs/06-maquina-de-estados.md` + `src/casa77_sdr/state_machine.py` |
| Contratos do motor | `docs/07-arquitetura-motor-respostas.md` + código e testes |
| Roadmap macro | `docs/05-roadmap.md` |
| Regras de trabalho | `docs/governanca/01-regras.md` + `CLAUDE.md` |
| Histórico e decisões técnicas | Git/GitHub (commits e descrições de PR) |

Regras:

- Código e testes na `main` prevalecem sobre documento que os descreva diferente; a
  divergência é corrigida no próximo PR que tocar o assunto.
- Comercial: `knowledge/casa77.yaml` prevalece sobre qualquer outro arquivo, conversa ou
  memória.
- Estado de serviço externo (n8n etc.) é evidência, não aprovação.

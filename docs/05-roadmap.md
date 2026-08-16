# 05 — Roadmap

Uma etapa por vez. Nenhuma etapa começa sem pedido específico.

| # | Etapa | Status | Entregável | Bloqueio |
|---|---|---|---|---|
| 1 | Organizar base de conhecimento | **Concluída** | `docs/`, `knowledge/`, `prompts/`, `tests/` | 9 itens pendentes, nenhum bloqueador |
| 2 | Definir fluxo de atendimento | **Concluída** | Fluxo detalhado e máquina de estados | Nenhum |
| 3 | Motor de respostas | **Em execução** | Camada que lê `knowledge/` e responde | Nenhum — etapa 2 aprovada e versionada |
| 4 | Qualificação | **Absorvida pela Etapa 3B — implementação pendente** | `Qualificador`: regras de classificação executáveis integradas ao motor | Nenhum — limites definidos exclusivamente em `knowledge/casa77.yaml` |
| 5 | Encaminhamento humano | Não iniciada | Geração e entrega do resumo | Canal de entrega e SLA pendentes |
| 6 | Integração de calendário | Não iniciada | Consulta de disponibilidade | Google Calendar sugerido, não confirmado |
| 7 | Integração WhatsApp | Não iniciada | Canal de mensagens | Número do bot e provedor não definidos |
| 8 | Registro de leads | Não iniciada | Persistência dos leads | Destino do registro não definido |
| 9 | Testes | Não iniciada | Execução de `tests/` | Depende de 3 a 8 |
| 10 | Publicação | Não iniciada | Ambiente em produção | Depende de 9 |

A Etapa 4 **não será aberta como etapa autônoma**: o `Qualificador` sempre foi componente
do motor em `docs/07-arquitetura-motor-respostas.md`, e a arbitragem da fronteira de
Qualificação reconciliou a posição arquitetural com o momento de implementação — ele será
entregue em uma futura subetapa funcional da Etapa 3B. A linha 4 permanece na tabela como
registro do escopo absorvido; **o `Qualificador` ainda não está implementado**. As etapas 5
a 10 mantêm a numeração.

## Estado da etapa 1

Concluída. `knowledge/casa77.yaml` v1.0 preenchido com dados de Douglas Bianchi em
2026-07-24. As 9 pendências declaradas no YAML não bloqueiam a etapa 2 — cada uma vira
handoff quando surgir na conversa. Ver `knowledge/informacoes-pendentes.md`.

## Decisões adiadas de propósito

- Linguagem, framework e hospedagem: etapa 3.
- Provedor de WhatsApp: etapa 7.
- Banco de dados ou planilha para leads: etapa 8.
- Modelo de IA: etapa 3, se necessário.

Nenhum serviço pago foi escolhido nesta etapa.

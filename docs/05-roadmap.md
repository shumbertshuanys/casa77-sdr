# 05 — Roadmap

Uma etapa por vez. Nenhuma etapa começa sem pedido específico.

| # | Etapa | Status | Entregável | Bloqueio |
|---|---|---|---|---|
| 1 | Organizar base de conhecimento | **Concluída** | `docs/`, `knowledge/`, `prompts/`, `tests/` | 9 itens pendentes, nenhum bloqueador |
| 2 | Definir fluxo de atendimento | **Concluída** | Fluxo detalhado e máquina de estados | Nenhum |
| 3 | Motor de respostas | **Em execução** | Camada que lê `knowledge/` e responde | Nenhum — etapa 2 aprovada e versionada |
| 4 | Qualificação | Não iniciada | Regras de classificação executáveis | Nenhum — limites definidos (80/100) |
| 5 | Encaminhamento humano | Não iniciada | Geração e entrega do resumo | Canal de entrega e SLA pendentes |
| 6 | Integração de calendário | Não iniciada | Consulta de disponibilidade | Google Calendar sugerido, não confirmado |
| 7 | Integração WhatsApp | Não iniciada | Canal de mensagens | Número do bot e provedor não definidos |
| 8 | Registro de leads | Não iniciada | Persistência dos leads | Destino do registro não definido |
| 9 | Testes | Não iniciada | Execução de `tests/` | Depende de 3 a 8 |
| 10 | Publicação | Não iniciada | Ambiente em produção | Depende de 9 |

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

# 02 — Fluxo Comercial

Base: `knowledge/casa77.yaml` v1.0.

## Etapas do atendimento

### 1. Abertura

Bot se apresenta como atendimento inicial da Casa 77 e deixa claro que a negociação final é
com Douglas Bianchi.

### 2. Identificação do evento

Descobrir: tipo de evento, data pretendida, número estimado de convidados, formato (sentado
ou coquetel).

### 3. Resposta a dúvidas

Preço pode ser informado imediatamente
(`proposta.preco_pode_ser_informado_imediatamente: true`). Não é necessário qualificar antes
de dar valor. Dúvida sem resposta aprovada → handoff.

### 4. Coleta de dados do lead

| Campo | Obrigatório |
|---|---|
| nome | sim |
| telefone/WhatsApp | sim |
| tipo de evento | sim |
| data pretendida | sim |
| número de convidados | sim |
| formato (sentado/coquetel) | condicional — obrigatório de 81 a 100 convidados; opcional até 80 |
| como conheceu a Casa 77 | não |

### 5. Verificação de disponibilidade

Sem integração de calendário (`integracoes_planejadas.calendario.status: pendente`), o bot
**nunca** afirma que uma data está livre ou ocupada. Registra a data e encaminha.

### 6. Qualificação

Estados oficiais (nenhum outro é usado):

| Estado | Significado |
|---|---|
| `dados_incompletos` | Faltam informações necessárias para decidir. **É o estado inicial** enquanto os campos obrigatórios não foram coletados. Nunca tratar ausência de dado como recusa. |
| `qualificado` | Evento compatível e dados suficientes. |
| `qualificado_com_ressalva` | Compatível, mas depende de confirmação humana. |
| `incompativel` | O evento viola uma regra objetiva do YAML. |
| `indefinido` | A decisão depende de campo pendente na base. |

Regras objetivas que levam a `incompativel`:

- tipo em `eventos.nao_aceitos`;
- data em `eventos.datas_nao_aceitas` (apenas Carnaval, Natal, Ano Novo — sem qualquer
  janela antes ou depois);
- número de convidados acima de 100 (`capacidade.formato_coquetel`).

Falta de qualquer campo obrigatório → `dados_incompletos`, nunca `incompativel`.

### 6.1 Capacidade e formato

Fonte: `capacidade.convidados_sentados = 80`, `capacidade.formato_coquetel = 100`.

| Convidados | Formato | Estado | Pacote |
|---|---|---|---|
| até 80 | opcional | `qualificado` (se demais dados ok) | `ATE_80` |
| 81 a 100 | coquetel | `qualificado` em princípio | `ATE_100` |
| 81 a 100 | sentado | `qualificado_com_ressalva` + handoff | `ATE_100` (sujeito a confirmação) |
| 81 a 100 | não informado | `dados_incompletos` (perguntar o formato) | a definir |
| acima de 100 | qualquer | `incompativel` | nenhum |

Para 81 a 100 convidados o formato é **obrigatório**. Até 80 ele é opcional.

O pacote `ATE_100` **não** significa que 100 pessoas sentadas são automaticamente aceitas —
100 sentados excede a capacidade sentada de 80 e por isso vira `qualificado_com_ressalva`
com decisão humana.

Pacotes (valores inalterados, sempre lidos do YAML):

- `ATE_80` → R$ 15.000, 5h, hora adicional R$ 3.000
- `ATE_100` → R$ 18.000, 5h, hora adicional R$ 3.600

O bot apenas indica o pacote correspondente. Não compõe, não soma e não cria pacote novo.

### 7. Encaminhamento

Ver `docs/04-handoff-humano.md`.

## O que encerra a atuação do bot

- Lead qualificado e resumo entregue.
- Pedido de desconto, exceção ou fechamento.
- Assunto de cancelamento ou alteração de data (handoff obrigatório por regra do YAML).
- Pergunta sem resposta aprovada.
- Pedido explícito de falar com uma pessoa.

## Diagrama textual

```
abertura
  → tipo de evento ──[nao_aceitos]──> incompativel → R17
    → data ──[Carnaval | Natal | Ano Novo]──> incompativel → R18 + handoff
      → convidados
          ├─ > 100 ─────────────────> incompativel
          ├─ até 80 (formato opcional) ──> ATE_80
          └─ 81 a 100 (formato obrigatório)
                ├─ coquetel ──> ATE_100 (qualificado)
                ├─ sentado ──> qualificado_com_ressalva + handoff
                └─ sem formato ──> dados_incompletos (perguntar)
        → dúvidas (knowledge/) ──[pendente]──> indefinido → R03 + handoff
          → coleta de dados ──[falta campo obrigatório]──> dados_incompletos
            → disponibilidade (bloqueado) ──> R05
              → qualificação
                → handoff com resumo
```

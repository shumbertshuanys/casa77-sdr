# 08 — Reconciliação do Legado n8n (Auditoria S0.2)

Registro permanente e sanitizado das conclusões da auditoria read-only S0.2,
concluída e aprovada em 2026-08-15. Este documento não contém segredo, PII, payload,
identificador operacional desnecessário nem dado comercial — valores comerciais
pertencem exclusivamente a `knowledge/casa77.yaml`.

## A. Objetivo

Auditar, em modo somente leitura, a implementação legada do produto criada
diretamente no n8n antes da governança técnica atual, e reconciliá-la com o desenho
aprovado deste repositório — sem corrigir, alterar ou executar nada.

## B. Fontes comparadas

| Fonte | Papel |
|---|---|
| GitHub `main` | **fonte técnica definitiva** (docs, knowledge, código) |
| Instância n8n (consulta read-only) | estado operacional real |
| Export histórico `n8n-casa77-mvp-v2.json` (arquivo local, não versionado) | evidência histórica auxiliar — nunca prova do estado atual |

## C. Estado operacional encontrado

Verificado diretamente por API read-only (somente operações de leitura; nenhuma
alteração foi realizada durante a auditoria):

- existe **um único workflow** relacionado à Casa 77 na instância;
- o workflow está **inativo**;
- a **entrada webhook está desabilitada**;
- **não existe receptor operacional ativo** identificado — nenhum atendimento real
  passa pelo n8n;
- o workflow **não apresentou evolução funcional recente** em relação ao legado
  auditado: as diferenças frente ao export histórico se resumem à incorporação do
  prompt em um nó próprio, à desativação da entrada e a ajustes menores de
  configuração.

Classificação operacional: **HISTÓRICO/INATIVO**.

## D. Conclusão arquitetural

O legado contém implementação antecipada de partes do produto (entrada e envio de
mensagens, registro de leads, alerta ao responsável, qualificação via LLM), mas **não
atende à arquitetura aprovada** em `docs/06-maquina-de-estados.md` e
`docs/07-arquitetura-motor-respostas.md`: as decisões comerciais e de estado são
delegadas ao LLM sem validação determinística, não há idempotência, a fonte comercial
é um prompt embutido paralelo ao YAML (e desatualizado em relação a ele), e estado
operacional e registro comercial não são separados.

Isso **não** significa que tudo deva ser descartado: há componentes reaproveitáveis
como referência (ver matriz) e outros que precisam ser substituídos pela
implementação conforme a arquitetura aprovada.

## E. Matriz consolidada

| # | Componente | Classificação |
|---|---|---|
| 1 | Entrada WhatsApp | PRESERVAR COM ADAPTAÇÃO |
| 2 | Normalização | PRESERVAR COM ADAPTAÇÃO |
| 3 | Estado | SUBSTITUIR |
| 4 | Persistência operacional | SUBSTITUIR |
| 5 | Registro comercial | PENDENTE DE DECISÃO |
| 6 | Histórico | SUBSTITUIR |
| 7 | Idempotência | SUBSTITUIR |
| 8 | Regras comerciais | SUBSTITUIR |
| 9 | Qualificação | SUBSTITUIR |
| 10 | Interpretação LLM | SUBSTITUIR |
| 11 | Redação LLM | SUBSTITUIR |
| 12 | Validação | SUBSTITUIR |
| 13 | Handoff | SUBSTITUIR |
| 14 | Alerta Douglas | PRESERVAR COM ADAPTAÇÃO |
| 15 | Calendário | PENDENTE DE DECISÃO |
| 16 | Envio WhatsApp | PRESERVAR COM ADAPTAÇÃO |
| 17 | Mídia | DESCARTAR |
| 18 | Erros/fallback | SUBSTITUIR |
| 19 | Observabilidade | SUBSTITUIR |

Consolidado: **12 SUBSTITUIR · 4 PRESERVAR COM ADAPTAÇÃO · 1 DESCARTAR ·
2 PENDENTE DE DECISÃO** (total 19).

## F. Regras de interpretação

- **PRESERVAR COM ADAPTAÇÃO** não significa copiar automaticamente o nó legado.
  Significa preservar conhecimento/configuração útil para a etapa correspondente do
  roadmap e reimplementá-lo conforme a arquitetura aprovada.
- **SUBSTITUIR** significa que a implementação legada não deve se tornar o núcleo
  aprovado — a referência é o desenho dos docs/06 e docs/07.
- **PENDENTE DE DECISÃO** significa que a escolha tecnológica ou funcional pertence à
  etapa própria do roadmap e não foi tomada nesta reconciliação.
- **DESCARTAR** aplica-se a comportamento prometido sem implementação nem aprovação
  na base de conhecimento.

## G. Segurança

Registrado de forma sanitizada, sem reprodução de qualquer valor:

- foi identificado **segredo de webhook hardcoded** no legado (nó desabilitado);
- existem **contatos comerciais hardcoded** em nós do fluxo;
- o legado **persiste PII de leads** (histórico integral de conversa e identificadores
  de contato sem mascaramento) de forma incompatível com a política de logs e dados
  sensíveis da governança atual (`docs/07` §6.6);
- **nenhuma credencial foi lida ou reproduzida** durante a auditoria;
- nenhum segredo real está ou deve ser versionado neste repositório;
- **nenhuma ação de rotação ou remoção foi executada** nesta auditoria.

## H. Destino do workflow legado

- O workflow já está inativo; **não há necessidade operacional de destruí-lo nesta
  etapa**.
- Pode permanecer temporariamente como referência histórica.
- Eventual arquivamento, remoção e rotação do segredo de webhook devem ocorrer apenas
  mediante mandato específico futuro.

## I. Consequência para o desenvolvimento

- A subetapa **3B.2 continua NÃO INICIADA**.
- A reconciliação elimina o risco de reconstrução cega do legado: o que serve de
  referência está identificado, e o que não serve está classificado.
- O planejamento futuro deve considerar apenas os componentes classificados como
  reaproveitáveis **como referência**, nunca como núcleo pronto.
- As decisões de calendário (etapa 6) e de registro comercial (etapa 8) permanecem
  nas etapas próprias do roadmap.

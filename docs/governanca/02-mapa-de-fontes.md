# Governança 02 — Mapa de Fontes

Autoridade versionada sobre **onde consultar cada tipo de informação** do projeto Casa 77 SDR
e **como resolver divergências**.

Este documento não contém estado do desenvolvimento nem dado comercial. Seu papel é indicar a
fonte correta. As regras permanentes estão em `docs/governanca/01-regras.md`.

---

## 1. Princípio

Não existe uma hierarquia universal única e ambígua. **A autoridade depende do tipo de
informação.** Consultar a fonte correta para o assunto é obrigatório antes de responder,
decidir ou executar.

---

## 2. Fonte correta por tipo de informação

| Tipo de informação | Fonte com autoridade |
|---|---|
| Estado técnico aprovado | GitHub, branch `main` |
| Progresso corrente | `docs/00-estado-atual.md`, confrontado com a `main` |
| Dados comerciais e operacionais | `knowledge/casa77.yaml` |
| Regras conversacionais | documentos especializados correspondentes |
| Handoff humano | documento especializado correspondente |
| Arquitetura | documento técnico especializado + código e testes aprovados |
| Roadmap macro | `docs/05-roadmap.md` |
| Governança | `docs/governanca/` |
| Histórico | Git e GitHub |
| Execução do Claude Code | `CLAUDE.md` + mandato atual + governança aplicável |

---

## 3. Detalhamento

### 3.1 Estado técnico aprovado — GitHub `main`

Repositório: `shumbertshuanys/casa77-sdr`.

É a fonte técnica **definitiva** para arquivos aprovados, código, testes, documentação
versionada, PRs integradas e estrutura real do projeto.

Não usar branch local, ZIP, cópia antiga ou relato de ferramenta como substituto da `main`.

### 3.2 Progresso corrente — `docs/00-estado-atual.md`

É o **snapshot operacional corrente**, sempre confrontado com a `main`. Não é histórico e não
substitui o Git.

A última entrega funcional relevante que ele registra deve existir e pertencer ao histórico da
`main`. Ela **não precisa ser igual ao `HEAD`**, porque commits exclusivamente documentais
podem ser posteriores.

### 3.3 Dados comerciais e operacionais — `knowledge/casa77.yaml`

Fonte **prevalente** para preços, capacidades, pacotes, duração, horários, condições,
restrições, formas de pagamento, eventos aceitos e demais regras comerciais estruturadas.

Em qualquer divergência comercial, **o YAML aprovado prevalece**.

Não inferir, recalcular, completar nem copiar valores para criar fonte paralela. Informação
ausente, `null`, `pendente`, não aprovada ou conflitante vira **pendência e handoff humano**.

### 3.4 Documentos especializados

Cada assunto tem seu documento. Consultar o correspondente ao tema:

- textos aprovados;
- lacunas e decisões pendentes;
- fluxo comercial e estados;
- regras conversacionais;
- handoff humano;
- arquitetura do motor de respostas;
- prompt do bot;
- testes e cenários executáveis.

O caminho vigente de cada um está no repositório; `CLAUDE.md` mantém o índice de entrada.

### 3.5 Roadmap macro — `docs/05-roadmap.md`

Visão macro de etapas. **Isoladamente não determina o estado** e não autoriza avanço de etapa.

### 3.6 Governança — `docs/governanca/`

Autoridade das regras permanentes, papéis, rotas, unidade de entrega, ciclo de PR, auditoria,
esquemas de mandato e de resposta, segurança e políticas conceituais de teste e CI.

### 3.7 Histórico — Git e GitHub

PRs, commits e diffs são a **única** autoridade histórica. Não existe arquivo paralelo de
histórico, ledger ou archive no repositório.

Merge SHA e ancestralidade são fatos deriváveis do Git.

### 3.8 Execução do Claude Code

`CLAUDE.md` é o arquivo de entrada: orienta a leitura obrigatória, define limites de execução e
aponta para as fontes, sem duplicar estado granular nem valor comercial.

A execução é regida por `CLAUDE.md` + o mandato vigente + a governança aplicável.

### 3.9 Fontes auxiliares

Ajudam a localizar contexto, mas **não determinam** estado nem dado aprovado:

- conversas anteriores e resumos de chat;
- outputs copiados;
- arquivos ZIP e exports;
- cópias locais;
- relatos de ferramenta;
- memória de assistente;
- roadmap isoladamente.

---

## 4. Consulta obrigatória por assunto

### Etapa atual, progresso ou próximos passos

1. GitHub `main`;
2. commit mais recente da `main`;
3. `docs/00-estado-atual.md`;
4. confirmação da entrega funcional registrada no histórico da `main`;
5. arquivos da entrega indicada;
6. testes ou PR correspondentes, quando necessário.

Não responder apenas por memória.

### Dados comerciais

1. `knowledge/casa77.yaml`;
2. resposta aprovada relacionada, quando existir;
3. pendências relacionadas;
4. regra de handoff.

Não usar números presentes em conversas, prompts ou instruções antigas.

### Regras de conversa

1. documento de regras conversacionais;
2. prompt do bot;
3. respostas aprovadas;
4. YAML, quando houver dado comercial envolvido.

### Handoff humano

1. documento de handoff;
2. fluxo comercial;
3. pendências;
4. YAML, quando a causa envolver dado comercial.

### Arquitetura ou implementação

1. `docs/00-estado-atual.md`;
2. documento técnico específico;
3. código relacionado;
4. testes relacionados;
5. PR ou commit da entrega anterior.

### Governança

1. `docs/governanca/01-regras.md`;
2. este documento;
3. `CLAUDE.md`, para limites de execução.

### Versionamento

1. estado local do Git;
2. branch atual;
3. diff;
4. testes;
5. `docs/00-estado-atual.md`;
6. histórico remoto da `main`.

---

## 5. Procedimento de verificação do estado

Antes de informar a etapa:

1. confirmar o repositório correto;
2. confirmar a referência `main` / `origin/main`;
3. obter o `HEAD` atual;
4. abrir `docs/00-estado-atual.md`;
5. identificar a última entrega funcional registrada;
6. confirmar que o commit existe;
7. confirmar que pertence ao histórico da `main`;
8. verificar os commits posteriores;
9. identificar se houve mudança funcional posterior;
10. comparar etapa, arquivos, testes e PR;
11. responder somente após essa conferência.

### Não é divergência por si só

- commit documental posterior;
- correção de ortografia;
- atualização de instrução sem mudança funcional;
- merge documental que não altera código, testes ou regra de negócio.

### É divergência

- código ou teste posterior não documentado;
- etapa diferente da entrega efetivamente integrada;
- commit funcional inexistente;
- commit fora do histórico da `main`;
- arquivo de estado ausente ou claramente desatualizado;
- PR, teste ou arquivo citado que não existe;
- mudança comercial não refletida na fonte correta.

---

## 6. Resolução de conflitos

### Conflito técnico

A `main` prevalece sobre cópia local, ZIP, conversa, relato de ferramenta e memória.

### Conflito de progresso

Confrontar `docs/00-estado-atual.md` com o histórico da `main`, os arquivos da entrega, os
testes e a PR. Se o documento estiver desatualizado, **não avançar** até corrigir ou auditar.

### Conflito comercial

`knowledge/casa77.yaml` prevalece. Não escolher o valor "mais recente" por aparência: confirmar
a versão aprovada.

### Conflito entre regra e implementação

Interromper a etapa e classificar o impacto como bloqueador, importante ou opcional. **Não
adaptar silenciosamente** nem a regra nem o código.

### Conflito de governança

A versão aprovada em `docs/governanca/` na `main` prevalece sobre qualquer cópia estática
externa.

---

## 7. `main` e cópias estáticas externas

A `main` é a **autoridade canônica** da governança.

As cópias adicionadas como fontes estáticas no ChatGPT e no Claude Desktop são **auxiliares** e
servem para regras operacionais, hierarquia de fontes, procedimentos estáveis e padrões de
auditoria.

Elas **não devem conter** etapa atual, commit atual, PR atual, testes atuais, pendência
temporária ou valor comercial — isso se consulta no repositório em tempo real.

Não existe mecanismo autorreferencial de SHA dentro dos arquivos canônicos. Registrar qual
versão foi copiada para uma fonte externa é **metadado externo** à fonte canônica.

Quando a governança for atualizada na `main`, substituir a versão antiga nas fontes estáticas
externas. Em divergência, **a versão aprovada na `main` prevalece**.

---

## 8. Regra de parada

Parar e informar a inconsistência, sem preencher lacuna por suposição, quando:

- não houver acesso ao repositório;
- `docs/00-estado-atual.md` não puder ser lido;
- a entrega funcional registrada não puder ser confirmada;
- os arquivos aprovados contradisserem o estado documentado;
- houver mudança funcional posterior não documentada;
- houver conflito comercial;
- houver risco de segurança;
- a ação solicitada for destrutiva e não estiver autorizada.

**Estado externo não substitui a `main`.** "Existe" não significa "funciona": presença de
arquivo não é evidência de comportamento aprovado.

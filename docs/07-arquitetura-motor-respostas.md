# 07 — Arquitetura do Motor de Respostas (Etapa 3A)

Decisão técnica documentada para o MVP. **Nenhum código, dependência, configuração ou
serviço foi criado nesta etapa.**

Base: `docs/02-fluxo-comercial.md`, `docs/03-regras-de-conversa.md`,
`docs/04-handoff-humano.md`, `docs/06-maquina-de-estados.md`, `knowledge/casa77.yaml`,
`knowledge/respostas-aprovadas.md`, `knowledge/informacoes-pendentes.md`.

> **Como no documento 06, esta arquitetura não contém constante comercial.** Preço,
> capacidade, pacote, horário, data bloqueada e condição são sempre lidos de
> `knowledge/casa77.yaml` em tempo de execução. Campos são referenciados pelo nome.

---

## 1. Princípios

| # | Princípio |
|---|---|
| P1 | O motor é **independente de canal**. WhatsApp, terminal e teste chamam a mesma função. |
| P2 | Toda decisão comercial é **determinística** e rastreável a um campo do YAML. |
| P3 | O LLM nunca decide. Ele interpreta a entrada e redige a saída, dentro de limites. |
| P4 | Nada sai sem passar por **validação final contra os fatos autorizados**. |
| P5 | **Falha fecha, não abre**: em dúvida comercial ou erro de validação, resposta segura + handoff. Nunca informação incerta. |
| P6 | Estado da conversa e `resultado_qualificacao` são eixos separados (doc 06 §1). |
| P7 | Sem fila, sem microsserviço, sem evento distribuído, sem framework web no MVP. |
| P8 | **O YAML sempre prevalece.** `knowledge/casa77.yaml` é a fonte autoritativa de todo fato comercial; `knowledge/respostas-aprovadas.md` fornece redação, não fato (§2.1). |
| P9 | Nada é enviado antes de estar registrado. A **persistência operacional** precede a emissão e é parte do motor, não da etapa 8 (§7.2, §7.3). |
| P10 | Nenhuma decisão automática é tomada sobre identidade de atendimento ou estado ausente. Em dúvida, esclarecer ou bloquear — nunca presumir. |

---

## 2. Componentes e dependências

Nove responsabilidades separadas. O termo "camada" é usado informalmente para agrupá-las,
mas **não existe hierarquia linear**: o desenho é um grafo de dependências explícitas
coordenado por um orquestrador.

| # | Responsabilidade | O que faz | Conhece regra comercial? | Conhece LLM? |
|---|---|---|---|---|
| 1 | Dados comerciais | `knowledge/casa77.yaml` e `knowledge/respostas-aprovadas.md` — arquivos de dado, sem lógica | é a fonte | não |
| 2 | Regras determinísticas | capacidade, pacote, datas, tipos, qualificação | sim, lendo o YAML | não |
| 3 | Estado da conversa | máquina do doc 06: estados, eventos, transições, ordem do §4 | só por delegação a 2 | não |
| 4 | Interpretação | mensagem livre → intenções e campos estruturados | **não** | sim |
| 5 | Redação | fatos já selecionados → texto natural | **não** | sim |
| 6 | Validação comercial | confere o rascunho contra os fatos autorizados antes de enviar | sim (comparação, não decisão) | não |
| 7 | Handoff | motivo, resumo no formato do doc 04, entrega | sim | não |
| 8 | Integrações | calendário (etapa 6), WhatsApp (etapa 7), **registro comercial de leads** (etapa 8) | não | não |
| 9 | Persistência operacional | estado, dados, qualificação, pendências, motivos, idempotência — **parte necessária do motor**, distinta do item 8 (§7.3) | não | não |

### 2.1 Regras de dependência

| # | Regra |
|---|---|
| D1 | O **`OrquestradorMotor`** coordena o pipeline (§5). Ele conhece todos os componentes; nenhum componente conhece o orquestrador. |
| D2 | Componentes determinísticos (2, 3, 6, 7) **não dependem de `src/llm`**. Nenhum deles importa, chama ou aguarda o modelo. |
| D3 | `src/llm` **não lê o YAML e não decide**. Recebe texto (extração) ou uma lista fechada de fatos (redação), e devolve estrutura ou texto. |
| D4 | A **validação** (6) recebe dois insumos: rascunho e fatos autorizados. Não lê estado, não lê mensagem, não gera texto. |
| D5 | O **handoff** (7) recebe a decisão determinística pronta. Não reavalia regra comercial e não conversa com o LLM. |
| D6 | As **integrações** (8) chamam o motor; o motor **não conhece campo específico de WhatsApp, Telegram ou qualquer outro canal**. O adaptador de canal faz apenas a **conversão de formato**: pega o payload externo e o coloca no contrato comum de entrada (§6.1), que **ainda contém a mensagem bruta**. A normalização de texto e o cálculo da chave de idempotência acontecem **dentro do motor**, no `NormalizadorEntrada`. A entrada **não** chega semanticamente normalizada. |
| D7 | **Dependência circular é proibida.** Se dois componentes precisarem um do outro, a coordenação sobe para o orquestrador. |
| D8 | Todo componente determinístico é chamável isoladamente, sem rede e sem LLM — é o que torna §8.1 possível. |
| D9 | A **persistência operacional é a única fonte autoritativa do estado** (§6.1.2). Nenhum componente aceita estado vindo do canal; o contexto é sempre recuperado, nunca recebido. |
| D10 | O `ResolvedorIdentidade` depende de **contexto recuperado e interpretação**, nessa ordem. Não é executado sobre contexto inválido (S7). |

Fluxo de dependência, sem ciclo:

```text
canal externo
   → adaptador de canal          (só converte formato; mensagem segue bruta; NÃO envia estado)
      → OrquestradorMotor
           1. NormalizadorEntrada   normaliza texto e calcula idempotência (dentro do motor)
           2. persistência operacional  ── recupera contexto ──►  ÚNICA fonte de estado
           3. interpretação (LLM)       ── sem acesso ao YAML e sem acesso ao estado
           4. ResolvedorIdentidade      ── contexto + interpretação → ativo / T36 / T37 / ambíguo
           5. estado , regras , seleção de fatos
           6. redação (LLM) , validação , handoff
           7. persistência operacional  ── grava ──►  só então emitir

regras e seleção de fatos → knowledge (YAML + respostas aprovadas)
```

A fronteira é deliberada: se o adaptador normalizasse o texto, cada canal produziria uma
normalização diferente e o mesmo teste deixaria de valer para todos. O adaptador traduz
formato; o motor decide o que o texto significa.

### 2.2 Precedência entre fontes — YAML × respostas aprovadas

| # | Regra |
|---|---|
| F1 | `knowledge/casa77.yaml` é a **fonte autoritativa de todo fato comercial**: preço, capacidade, pacote, horário, prazo, condição de pagamento, restrição, data bloqueada, tipo aceito. |
| F2 | `knowledge/respostas-aprovadas.md` fornece **redação aprovada**, não fato. Nenhum `Rxx` pode sobrescrever, complementar ou reinterpretar o YAML. |
| F3 | Toda resposta `Rxx` que contenha fato comercial é **validada contra o YAML carregado** antes de ser selecionada — não contra o YAML de quando o texto foi escrito. |
| F4 | **Divergência entre `Rxx` e YAML**: (a) a resposta não é selecionada; (b) é registrado um **erro de consistência da base**; (c) o dado divergente é bloqueado; (d) a divergência é reportada para correção humana. |
| F5 | O **YAML sempre prevalece**. Não há conciliação, média, "o mais recente" nem tentativa de harmonização — e **nunca** arbitragem pelo LLM. |
| F6 | Informação **textual sem equivalente comercial no YAML** (tom, ordem das frases, explicação de processo) continua vindo de `respostas-aprovadas.md`, desde que não contradiga o YAML. |

Exemplo concreto do problema que F1–F5 previnem: `R09` cita valores de pacote e `R11` cita a
duração e o horário limite. Se `precos.pacotes` ou `horarios` mudarem no YAML e o texto de
`respostas-aprovadas.md` não for atualizado junto, o bot passaria a repetir um valor
desatualizado com aparência de texto aprovado. Com F3–F4, essa resposta é bloqueada e a
divergência aparece como erro da base, não como conversa.

Consequência operacional: a divergência é **defeito de base de conhecimento**, não caso de
negócio. Não vira "não sei responder" silencioso — vira alerta para quem mantém os arquivos,
enquanto o interessado recebe R03 + handoff.

---

## 3. Comparação técnica — Opção A × Opção B

### Opção A — Python, aplicação modular simples

### Opção B — Node.js com TypeScript, aplicação modular simples

| Critério | Opção A — Python | Opção B — Node.js + TypeScript |
|---|---|---|
| Simplicidade para iniciante | Alta. Sem etapa de build, sem transpilação, sem escolha de módulo (ESM/CJS). Um arquivo roda direto. | Média. Exige `tsconfig`, compilação ou runner, e decisão de formato de módulo antes da primeira linha útil. |
| Leitura de YAML | Não é da biblioteca padrão; exige uma dependência (há opções maduras e amplamente usadas). Estruturas viram dicionários e listas diretamente. | Também exige uma dependência (idem). O resultado chega sem tipo até ser validado. |
| Validação estrutural do YAML | Exige biblioteca de schema, ainda não escolhida. Ecossistema maduro para isso. | Exige biblioteca de schema, ainda não escolhida. Ecossistema maduro para isso. Empate real: **o tipo estático não valida arquivo em disco**, então a validação é em execução nas duas. |
| Testes | Maduro, sintaxe curta, sem configuração para o caso simples. | Maduro, mas mais peças (runner, transform, mapeamento de caminhos). |
| Tipagem | Anotações opcionais. Estático mais fraco. | Estático mais forte. Vantagem real em refatoração grande — e é uma vantagem genuína da Opção B. |
| Tratamento de erros | Exceções claras, `try/except` explícito. | Mistura de exceções e assíncrono; `unhandled rejection` é armadilha comum para iniciante. |
| WhatsApp (etapa 7) | API oficial é HTTPS puro — indiferente à linguagem. Bibliotecas não oficiais são poucas. | Ecossistema não oficial maior (bibliotecas de sessão de navegador/socket). Vantagem só se a etapa 7 escolher rota não oficial. |
| Google Calendar (etapa 6) | SDK oficial mantido pela Google. | SDK oficial mantido pela Google. Empate. |
| Bibliotecas em geral | Excelente para dados, regras e validação. | Excelente para rede e canais. |
| Custo | Zero de licença nas duas. | Zero de licença nas duas. |
| Manutenção | Menos peças móveis para manter atualizadas. | Mais dependências de build; churn maior do ecossistema. |
| Facilidade de auditoria | Alta. O código de regra lê quase como o texto do doc 02, o que importa porque quem audita é Douglas Bianchi com apoio, não um time de engenharia. | Média. Tipos e genéricos ajudam o desenvolvedor e atrapalham o leitor não técnico. |
| Hospedagem futura | Amplamente suportada. | Amplamente suportada. Empate. |
| Risco de complexidade prematura | Baixo. | Médio. O build entra antes de existir valor. |

### Recomendação: **Opção A — Python**

Justificativa, em ordem de peso:

1. **Menor ferramental.** A Opção B cobra um custo fixo — configuração de compilador,
   formato de módulo, runner de teste — antes de a primeira regra comercial funcionar. A
   Opção A não cobra. Com um mantenedor iniciante, esse custo é o maior risco de
   travamento do projeto.
2. **Auditabilidade.** A regra de capacidade e de pacote precisa ser lida e conferida por
   quem não programa. Python é mais legível para isso.
3. **A vantagem de tipo estático da Opção B rende menos aqui do que parece.** Os dois erros
   que este projeto precisa impedir — "o YAML mudou e um campo sumiu" e "a resposta citou um
   valor que não está no YAML" — só podem ser detectados em execução, sobre um arquivo
   externo. **As duas opções precisam de validação em execução para isso**, com biblioteca
   de schema. Isso não torna Python superior nesse quesito; apenas neutraliza o principal
   argumento a favor da Opção B. A vantagem de tipo estático permanece real para refatoração.
4. **As integrações futuras não travam a escolha.** A API oficial do WhatsApp e o Google
   Calendar são HTTPS e têm SDK nas duas linguagens.

Sobre bibliotecas: nenhuma foi escolhida ou aprovada nesta etapa. Leitura de YAML, validação
de schema e execução de testes exigirão dependências em qualquer das opções; a seleção
pertence à Etapa 3B. Qualquer nome de biblioteca que apareça em discussão futura deste
documento é exemplo ilustrativo, não decisão.

Ressalva honesta: **se a etapa 7 escolher uma rota não oficial de WhatsApp**, o adaptador de
canal provavelmente será Node. Isso não invalida a decisão, porque o motor é independente de
canal (P1): o adaptador conversa com o motor por um limite simples de processo. A escolha do
canal continua adiada para a etapa 7.

Nenhum framework web é escolhido nesta etapa — o MVP não precisa de um. O motor é uma função
chamada por um adaptador; o adaptador HTTP só será necessário na etapa 7.

---

## 4. Divisão determinística × LLM

### 4.1 Somente determinístico

Preço, capacidade, pacote, horário, data bloqueada, tipo de evento aceito, formato,
qualificação, gatilho de handoff, disponibilidade e condição de pagamento **nunca** são
calculados, escolhidos ou interpretados pelo LLM.

| Componente | Responsabilidade | Entrada | Saída |
|---|---|---|---|
| `OrquestradorMotor` | coordenar as 14 etapas do pipeline na ordem correta — em especial recuperar contexto (3) antes de interpretar (4) e resolver identidade (5); decidir o que emitir; nenhuma regra comercial própria | entrada do contrato externo (§6.1) | saída (§6.5) |
| `ResolvedorIdentidade` | decidir se a mensagem pertence a atendimento ativo, a T36, a T37 — ou se é ambígua (§7.1) | contexto recuperado (§6.2) + interpretação (§6.3) | identidade resolvida ou ambígua, com o critério que a determinou |
| `CarregadorYaml` | ler `knowledge/casa77.yaml` uma vez por execução e manter em memória | caminho do arquivo | estrutura carregada + versão |
| `ValidadorYaml` | conferir presença, tipo e coerência dos campos exigidos pelas regras | estrutura carregada | válido / lista de campos faltantes |
| `ValidadorConsistenciaBase` | conferir cada `Rxx` que cita fato comercial contra o YAML carregado (F3) | respostas aprovadas + YAML | lista de divergências, com `Rxx` e campo do YAML |
| `NormalizadorEntrada` | limpar a mensagem e calcular a chave de idempotência conforme §4.3 | mensagem bruta + metadados do canal | mensagem normalizada + chave + origem da chave |
| `RegistroAtendimento` | registrar dados e correções (`E02`–`E05`), sobrescrevendo valores corrigidos | dados extraídos + estado | dados atualizados + lista de correções |
| `RegrasComerciais` | avaliar tipo, data, número de convidados e formato contra o YAML | dados + YAML | lista de violações com motivo e campo de origem |
| `Qualificador` | calcular `resultado_qualificacao` conforme doc 02 §6 e §6.1 | dados + violações + pendências | um dos cinco valores oficiais + motivo + campos ausentes |
| `MaquinaEstados` | aplicar a ordem do doc 06 §4 e a tabela de transições | estado + eventos | próximo estado único + ações obrigatórias |
| `DetectorHandoff` | reconhecer os 12 gatilhos do doc 04 e emitir `E18` com motivo | mensagem interpretada + dados + YAML | motivo(s) de handoff |
| `SeletorFatos` | escolher quais fatos aprovados podem entrar na resposta, **conferindo cada `Rxx` contra o YAML antes de selecioná-lo** (F3) | perguntas + estado + YAML + respostas aprovadas | lista fechada de fatos autorizados, ou divergência de base |
| `ValidadorResposta` | vetar rascunho com valor, promessa ou termo não autorizado | rascunho + fatos autorizados | aprovado / bloqueado + motivo |
| `Persistencia` | persistência **operacional**: gravar estado, dados, qualificação, pendências, motivos e chave de idempotência antes da emissão (P9, §7.3) | decisão final | confirmação de gravação ou falha |

`SeletorFatos` é o ponto crítico da arquitetura: é **ele**, e não o LLM, que decide o que
pode ser dito. Cada fato carrega o campo do YAML ou o código de resposta aprovada
(`R01`–`R30`) de onde veio — e, quando vem de um `Rxx` com conteúdo comercial, carrega
também o resultado da conferência contra o YAML. Um `Rxx` divergente **nunca entra na lista**
(F4): o seletor devolve divergência de base, e a resposta ao interessado passa a ser
R03 + handoff.

`ValidadorResposta` faz a checagem simétrica na saída: nenhum valor, prazo, capacidade,
horário ou condição pode aparecer no texto final sem estar na lista de fatos autorizados —
que, por construção, já é consistente com o YAML. Texto literal vindo de
`respostas-aprovadas.md` **também** passa pelo validador; ser aprovado não isenta de
conferência.

### 4.2 Somente LLM

Permitido: interpretar intenção; extrair campos da mensagem; identificar perguntas; redigir
texto natural **a partir de fatos já selecionados**; adaptar tom; resumir o atendimento.

Proibido: escolher pacote; calcular preço; validar capacidade; classificar compatibilidade;
confirmar disponibilidade; oferecer desconto; autorizar visita; criar exceção; alterar regra;
interpretar contrato.

Consequência de projeto: **o prompt de redação nunca recebe o YAML**. Recebe apenas a lista
de fatos autorizados, o tom e a instrução de não acrescentar nada. O que não está na lista
não pode aparecer no texto — e o `ValidadorResposta` confere isso depois.

### 4.3 Chave de idempotência

A idempotência do doc 06 §4 passo 1 protege contra **reprocessamento técnico** (reentrega do
canal, retentativa, reinício do motor). Ela **não** pode transformar repetição humana
legítima em silêncio.

Prioridade de composição da chave:

| # | Origem | Uso |
|---|---|---|
| 1 | **Identificador único da mensagem fornecido pelo canal** | preferencial e suficiente sozinho. É a única fonte que distingue com segurança reentrega de mensagem nova. |
| 2 | **Chave composta**, quando o canal não fornece identificador: canal + contato + janela temporal controlada + hash do conteúdo normalizado | fallback. A janela é curta e explícita, não "a conversa toda". |
| 3 | Texto normalizado isolado | **nunca é chave suficiente.** |

Regras:

- a mesma frase enviada em momentos diferentes **pode ser mensagem nova e legítima** —
  "oi?", "tem novidade?", "e aí?" se repetem naturalmente em WhatsApp;
- fora da janela temporal da chave composta, a repetição é tratada como mensagem nova;
- a saída do `NormalizadorEntrada` registra **qual das duas origens** produziu a chave, para
  que o log mostre se a decisão de duplicidade foi confiável (origem 1) ou heurística
  (origem 2);
- a janela temporal concreta é parâmetro de implementação da Etapa 3B, não constante deste
  documento.

---

## 5. Pipeline

**Catorze etapas** coordenadas pelo `OrquestradorMotor`. Uma mensagem produz **uma única
decisão final** de próximo estado (doc 06 §4).

Ordem essencial: **recuperar contexto antes de interpretar, e interpretar antes de resolver
identidade.** Decidir T36 × T37 sem contexto persistido e sem saber do que a mensagem trata é
adivinhar.

| # | Etapa | Entrada | Saída | Falha e tratamento |
|---|---|---|---|---|
| 1 | Receber e normalizar mensagem | entrada no contrato comum de §6.1, **com a mensagem bruta** | mensagem normalizada + origem do identificador | mensagem vazia → não processar, sem transição |
| 2 | Verificar idempotência | mensagem normalizada + metadados | chave de idempotência (§4.3) + veredito duplicada/nova | duplicata → encerrar o ciclo sem efeito (doc 06 §4 passo 1); sem identificador de canal → chave composta, marcada como heurística no log |
| 3 | **Recuperar contexto persistido** | canal + contato + identificador do atendimento, quando houver | contexto recuperado (§6.2): atendimento indicado quando existir, atendimentos ativos ou recentes do contato necessários à resolução, estado, dados, qualificação, pendências, motivos | atendimento indicado e **não recuperado** → erro operacional: bloquear, preservar, alertar. Estado corrompido → bloqueio (§7.1). **Nunca criar atendimento novo por não encontrar o indicado** |
| 4 | Interpretar e extrair | mensagem normalizada | intenções, campos, perguntas, referências ao evento anterior, confiança | LLM indisponível → modo degradado (§7); confiança baixa → campo **não** é registrado |
| 5 | **Resolver identidade do atendimento** | contexto recuperado (3) + interpretação (4) | atendimento ativo, mesma solicitação (T36), nova solicitação (T37) **ou ambíguo** | ambíguo → **não decidir**: pedir esclarecimento, sem herdar nem sobrescrever dado algum (§7.1); persistir o processamento pendente quando possível |
| 6 | Registrar dados e correções | campos extraídos + atendimento resolvido | dados atualizados + correções | conflito entre mensagem e estado → §7; dado incerto nunca é gravado; identidade ambígua → nada é registrado no atendimento anterior |
| 7 | Executar a ordem determinística do doc 06 §4 | dados + YAML + eventos | eventos confirmados, violações, motivos, qualificação recalculada | violação da precedência (ex.: `E07` sobre incompatibilidade) é erro de programa, não caso de negócio → bloquear envio |
| 8 | Consultar YAML e respostas aprovadas | perguntas detectadas | valores de campo e códigos `R` correspondentes | campo `null`/`pendente` → `E09`; sem resposta aprovada → gatilho 1 do doc 04 |
| 9 | Selecionar fatos permitidos — **conferindo cada `Rxx` comercial contra o YAML** (F3) | resultado de 7 e 8 | lista fechada de fatos, cada um com origem e conferência | divergência `Rxx` × YAML → o fato **não** entra na lista, registra-se erro de consistência da base e o dado divergente é bloqueado (F4); lista vazia com pergunta pendente → R03 + handoff |
| 10 | Gerar rascunho | fatos autorizados + tom + estado | texto candidato | LLM indisponível ou lento → usar o texto aprovado literal (§7) |
| 11 | Validar o rascunho | rascunho + fatos autorizados | aprovado ou bloqueado + motivo | qualquer valor, promessa ou termo fora da lista → bloqueio |
| 12 | Bloquear ou substituir | resultado de 11 | texto final seguro | substituir pelo texto aprovado literal; se não houver, R03 + handoff. Nunca reenviar ao LLM mais de uma vez |
| 13 | Persistir — **persistência operacional** (§7.3) | decisão final | estado, dados, qualificação, pendências, motivos e chave de idempotência gravados | falha de persistência → **bloquear a emissão** da resposta que depende da nova transição; preservar a mensagem para reprocessamento idempotente; alerta operacional (§7.2) |
| 14 | Emitir resposta ou handoff | texto final + decisão **já gravada** | resposta ao interessado e/ou resumo para Douglas | estado `atendimento_humano` → nada é emitido (I03); handoff não registrado → não afirmar que houve handoff (§7.2) |

Regras do pipeline:

- **a etapa 3 antecede a 4, e as duas antecedem a 5**: identidade só é resolvida com contexto
  persistido e interpretação disponíveis;
- as etapas 7 a 9 são a única origem de conteúdo comercial;
- a etapa 10 é a única que pode falhar por indisponibilidade externa sem parar o
  atendimento — todas as outras têm caminho determinístico;
- **a etapa 13 antecede a 14, sem exceção** — inclusive para resposta segura e para handoff
  (§7.2). Nunca responder um estado que não foi gravado;
- a etapa 11 roda mesmo quando o texto veio pronto de `respostas-aprovadas.md`;
- as etapas 3 e 5 podem terminar o ciclo sem produzir transição: contexto inválido bloqueia,
  identidade ambígua pede esclarecimento (§7.1);
- a etapa 4 pode rodar sobre contexto inválido **apenas para diagnóstico** — nesse caso
  nenhuma transição e nenhuma gravação comercial ocorrem (§7.1).

---

## 6. Contratos conceituais

Formatos conceituais. Sem código, sem JSON Schema, sem definição de tipo.

### 6.1 Entrada — contrato externo

| Campo | Conteúdo |
|---|---|
| identificador do canal | qual canal originou (`whatsapp`, `terminal`, `teste`) |
| identificador do contato | quem enviou, no formato do canal |
| **identificador único da mensagem** | fornecido pelo canal quando existir; é a origem preferencial da chave de idempotência (§4.3). Ausente → chave composta, marcada como heurística |
| **identificador do atendimento** | **opcional**. Quando presente, é apenas uma **referência para consulta** — ver §6.1.1 |
| mensagem | **texto bruto**, exatamente como recebido. Sem limpeza, sem recorte, sem interpretação. A normalização é responsabilidade do `NormalizadorEntrada`, dentro do motor |
| data e hora | momento do recebimento, com fuso |

Este é o **contrato comum de entrada**: o mesmo para WhatsApp, terminal e teste. O adaptador
de canal preenche esses campos a partir do payload externo e não faz nada além disso (D6).
Campo específico de um canal que não caiba aqui não entra no motor — ou vira um dos campos
acima, ou fica no adaptador.

**O contrato externo não contém estado.** Não existem aqui os campos "estado anterior",
"qualificação anterior", "pendências anteriores" nem "estado anterior era esperado?". Todos
foram removidos: o canal não é fonte de estado (E1–E5, §6.1.2). Se o adaptador enviar
qualquer um desses campos, o motor **ignora ou rejeita** — nunca os usa como contexto.

A noção de "havia estado esperado?" continua existindo, mas **internamente**, como resultado
da resolução de contexto (§6.2), não como dado confiado ao canal.

#### 6.1.1 Identificador do atendimento

| # | Regra |
|---|---|
| N1 | É **opcional**. Sua ausência é normal — o motor resolve o contexto por canal + contato. |
| N2 | Quando fornecido, é **apenas uma referência para consulta** na persistência operacional. |
| N3 | Deve ser **validado** contra canal, contato e persistência. Um identificador que aponta para atendimento de outro contato é incompatível. |
| N4 | **Não prova por si só que o atendimento existe.** Quem prova é a persistência. |
| N5 | Identificador **inexistente, incompatível ou corrompido → erro operacional** (§7.1): bloqueio, mensagem preservada, alerta. |
| N6 | O motor **nunca cria atendimento novo silenciosamente** porque o identificador não foi encontrado. |

#### 6.1.2 Fonte autoritativa do estado

| # | Regra |
|---|---|
| E1 | A **persistência operacional é a única fonte autoritativa** do estado da conversa, dos dados coletados, da qualificação, das pendências e dos motivos. |
| E2 | O **adaptador de canal não fornece** estado, qualificação, pendências nem dados já coletados. Ele fornece mensagem e identificadores. |
| E3 | Qualquer estado recebido externamente é **ignorado ou rejeitado**, nunca confiado. |
| E4 | O **`OrquestradorMotor` recupera o contexto pela persistência** (etapa 3 do pipeline), antes de interpretar e antes de resolver identidade. |
| E5 | **Falha ou divergência na recuperação bloqueia o ciclo** (§7.1). Não há caminho alternativo que siga sem contexto válido. |

Motivo: estado vindo do canal é estado que qualquer coisa entre o WhatsApp e o motor pode
alterar. Confiar nele significaria que uma reentrega antiga poderia reverter a qualificação
de um lead, ou que um payload malformado poderia apagar pendências já registradas.

### 6.2 Contexto recuperado — contrato interno

Produzido pela etapa 3, a partir da persistência operacional. Nunca vem do canal.

| Campo | Conteúdo |
|---|---|
| atendimento indicado | resultado da consulta pelo identificador de §6.1.1, quando ele foi fornecido: encontrado e compatível, não encontrado, ou incompatível |
| atendimentos do contato | atendimentos ativos ou recentes do mesmo contato **necessários à resolução de identidade** — não o histórico inteiro |
| estado da conversa | um dos oito valores do doc 06 §1.1, por atendimento recuperado |
| dados já coletados | tipo, data, convidados, formato, nome, contato |
| `resultado_qualificacao` | valor atual de cada atendimento recuperado |
| `pendencias_resposta` | perguntas em aberto |
| motivos registrados | incompatibilidade e handoff já detectados |
| **havia estado esperado?** | conclusão **interna** da resolução: o contato tem atendimento anterior conhecido? Distingue primeiro contato comprovado de estado ausente por falha (§7.1, S6) |
| integridade | contexto íntegro, ausente ou corrompido. Ausente ou corrompido quando havia estado esperado → bloqueio (E5) |

### 6.3 Interpretação (saída do LLM na etapa 4)

| Campo | Conteúdo |
|---|---|
| intenções detectadas | lista mapeável aos eventos `E02`–`E11`, `E17` |
| dados extraídos | tipo de evento, data, convidados, formato, nome, contato — cada um com confiança própria |
| correções | campos que contradizem valor já registrado |
| perguntas comerciais | perguntas identificadas, em texto |
| pedido de humano | sim/não |
| **referências ao evento anterior** | menções que indicam continuidade ("o casamento de outubro que a gente falou", "sobre aquele orçamento"), em texto, com confiança. Insumo da resolução de identidade (§7.1) |
| nível de confiança | por campo e global |
| trechos ambíguos | partes da mensagem não interpretadas com segurança |

O interpretador **não** classifica compatibilidade, **não** decide handoff e **não** resolve
identidade de atendimento. Ele apenas relata o que leu. `pedido de humano` é um sinal, não
uma decisão: quem emite `E18` é o `DetectorHandoff`. `referências ao evento anterior` também
é sinal: quem decide T36 × T37 é o `ResolvedorIdentidade`, na etapa 5.

### 6.4 Decisão determinística

| Campo | Conteúdo |
|---|---|
| estado anterior | estado de origem, **vindo do contexto recuperado** (§6.2), nunca do canal |
| eventos | eventos confirmados após a ordem do §4 |
| dados atualizados | dados do atendimento após registro e correções |
| resultado de qualificação | um dos cinco valores oficiais |
| pendências de resposta | perguntas sem resposta aprovada, com o campo pendente correspondente |
| motivo de incompatibilidade | motivo objetivo + campo do YAML violado (I04) |
| motivo de handoff | motivo enumerado do doc 06 §2.1, ou lista de motivos |
| próximo estado | decisão única (I19). Pode ser **"sem transição"** quando a etapa 3 ou a 5 termina o ciclo (contexto inválido ou identidade ambígua) |
| identidade do atendimento | atendimento ativo, mesma solicitação (T36), nova solicitação (T37) ou **ambígua**; quando ambígua, nenhum dado anterior é herdado ou sobrescrito (§7.1) |
| fatos autorizados | lista fechada; cada fato com valor, texto, origem (`campo do YAML` ou `Rxx`) e resultado da conferência contra o YAML (F3) |
| divergências de base | lista de `Rxx` em conflito com o YAML detectados neste ciclo (F4); vazia no caso normal |

### 6.5 Saída

| Campo | Conteúdo |
|---|---|
| texto | mensagem final ao interessado, já validada |
| deve responder | falso em `atendimento_humano`, em mensagem duplicada e quando a persistência falhou (§7.2) |
| deve fazer handoff | derivado do próximo estado — e só afirmado ao interessado depois de registrado (§7.2) |
| resumo para Douglas | campos do bloco de `docs/04-handoff-humano.md` |
| bloqueios | o que o validador vetou e por quê; inclui divergência de base (F4) |
| **alerta operacional** | evento destinado a quem opera, não a quem conversa: falha de persistência, contexto não recuperado, identificador de atendimento incompatível, estado corrompido, divergência de base, erro inesperado. Sai por caminho separado da conversa |
| logs mínimos | atendimento, estado anterior e final, eventos, motivos, origem de cada fato usado, veredito do validador, se o LLM foi usado, origem da chave de idempotência, como a identidade foi resolvida — sempre sanitizados conforme §6.6 |

Os logs mínimos são o que torna uma resposta auditável depois. Sem a origem de cada fato,
não é possível provar que um valor veio do YAML.

### 6.6 Política mínima de logs e dados sensíveis

| # | Regra |
|---|---|
| L1 | **Nunca** registrar token, senha, chave de API, cookie ou cabeçalho de autenticação — em nenhum nível, nem em log de depuração. |
| L2 | Telefone e identificadores pessoais são **mascarados** no log técnico. O número completo existe onde é necessário para operar, não no log. |
| L3 | Evitar mensagem completa e prompt completo quando não forem necessários. Registrar o que sustenta a auditoria: códigos, campos, estados, motivos, vereditos. |
| L4 | Registrar **somente fatos, códigos, estados e motivos** necessários para auditar a decisão — não a conversa inteira por padrão. |
| L5 | **Log técnico e resumo comercial são separados.** O resumo do doc 04 vai para Douglas Bianchi e contém dados de contato por necessidade; o log técnico não é o resumo e não deve replicá-lo. |
| L6 | Exceções são **sanitizadas antes de persistir**: remover credenciais, cabeçalhos e conteúdo pessoal do rastreamento antes de gravar. |
| L7 | **Política de retenção será definida antes da produção** (etapa 10). Até lá, o volume de log fica no mínimo necessário. |

Nenhuma ferramenta de observabilidade é escolhida nesta etapa.

---

## 7. Falhas e segurança

Princípio obrigatório:

> **Em dúvida comercial ou falha de validação, não enviar informação incerta. Usar resposta
> segura e handoff quando necessário.**

| Falha | Comportamento |
|---|---|
| YAML ausente | **Motor não inicia.** Nenhuma resposta é emitida. Erro de operação, não de conversa. |
| YAML inválido (sintaxe) | Motor não inicia. Reportar arquivo, linha e erro. |
| Campo obrigatório do YAML ausente | Motor não inicia se o campo for usado por regra estrutural (capacidade, pacotes, eventos, datas). Se for campo acessório, tratar como pendente → R03 + handoff. |
| **Divergência entre `Rxx` e YAML** | O YAML prevalece (F5). A resposta não é selecionada, o dado divergente é bloqueado, registra-se erro de consistência da base e alerta operacional. Ao interessado: R03 + handoff. **Sem conciliação, e nunca arbitragem pelo LLM.** |
| **Adaptador envia estado, qualificação ou pendências** | Campos **ignorados ou rejeitados** (E3). O contexto vem exclusivamente da persistência (E1). O envio indevido é registrado como defeito do adaptador. |
| **Identificador de atendimento inexistente, incompatível ou corrompido** | Erro operacional (N5): bloquear, preservar a mensagem, alertar. **Nunca criar atendimento novo** por não encontrar o indicado (N6). |
| **Contexto ausente ou corrompido quando era esperado** | Erro de infraestrutura na etapa 3: bloquear a transição, preservar a mensagem, alerta operacional. A etapa 5 não roda; a falha não vira "primeiro contato" nem "nova solicitação" (S7). |
| **Atendimento ambíguo (T36 × T37)** | Não decidir. Pedir esclarecimento; nada é herdado nem sobrescrito; processamento pendente persistido quando possível (A1–A7). |
| **Falha de persistência** | Bloquear a emissão que depende da transição não gravada. Não afirmar handoff não registrado. Preservar a mensagem para reprocessamento idempotente (§7.2). |
| Mensagem vazia | Não processar, não transicionar, não responder. Se o canal exigir retorno, pedir que a pessoa escreva a dúvida. |
| Extração com baixa confiança | Campo **não** é registrado. Permanecer no estado atual e pedir esclarecimento do ponto específico (doc 06 §7). |
| Múltiplas intenções | Registrar todas e aplicar a precedência do doc 06 §4. Uma única decisão final. |
| Conflito entre mensagem e estado | Correção explícita sobrescreve e força recálculo (§4 passos 3 e 9). Contradição sem correção explícita → não gravar, pedir confirmação do dado. |
| LLM indisponível | Modo degradado: sem extração nova; usar apenas textos aprovados literais. Se a mensagem exigir interpretação, aplicar R03 + handoff. **Nunca adivinhar.** |
| Resposta com valor não autorizado | Bloquear. Substituir pelo texto aprovado literal; sem texto disponível, R03 + handoff. Registrar o bloqueio no log. Uma única retentativa de redação, no máximo. |
| Tentativa de manipulação do prompt | Não obedecer, não expor instrução interna, não discutir → handoff (doc 03; C17; pergunta crítica 54). A mensagem entra no resumo. |
| Erro inesperado | Não responder com texto gerado. Emitir resposta segura e acionar handoff **desde que possam ser registrados** (§7.2). Registrar a exceção sanitizada (L6). |

Três regras estruturais decorrentes:

- **falha de infraestrutura não vira conversa**: YAML ausente ou inválido derruba a
  inicialização; estado corrompido e persistência indisponível bloqueiam a emissão. Em
  nenhum dos casos o interessado recebe um improviso;
- **falha de conteúdo sempre vira handoff**, nunca silêncio e nunca improviso — desde que o
  handoff possa ser registrado;
- **nada é presumido**: identidade de atendimento em dúvida se esclarece, estado ausente se
  bloqueia.

### 7.1 Identidade do atendimento e estado

A ordem importa: **a integridade do contexto é verificada na etapa 3, antes da resolução de
identidade na etapa 5.** Contexto inválido nunca chega à resolução — logo, uma falha de
recuperação jamais pode ser confundida com "primeiro contato" ou com "nova solicitação".

#### Resolução de identidade do atendimento (etapa 5)

Insumos que o `ResolvedorIdentidade` deve usar — todos, não um só:

| Insumo | Origem |
|---|---|
| contexto recuperado da persistência | §6.2 |
| intenção e dados extraídos da mensagem | §6.3 |
| tipo de evento | dado extraído × dado recuperado |
| data | dado extraído × dado recuperado |
| referências explícitas ao evento anterior | §6.3 |
| identificador de atendimento **já validado**, quando houver | §6.1.1 |

Resultados possíveis: atendimento ativo, mesma solicitação (T36), nova solicitação (T37), ou
**ambíguo**.

#### Ambiguidade entre T36 (mesmo evento) e T37 (nova solicitação)

Quando os insumos acima não determinam com segurança se a mensagem trata do evento anterior
ou de uma nova solicitação:

| # | Regra |
|---|---|
| A1 | **Não reutilizar nem sobrescrever** dados do atendimento anterior. |
| A2 | **Manter o atendimento anterior intacto** — não reabrir, não alterar, não encerrar. |
| A3 | Pedir **esclarecimento objetivo** sobre qual evento está sendo tratado, em uma pergunta. |
| A4 | **Não aplicar T36 nem T37** até o esclarecimento. Enquanto isso, não há transição de identidade. |
| A5 | Se o esclarecimento não for possível ou não vier, **handoff com o motivo** registrado. |
| A6 | **Nenhuma data, tipo de evento, número de convidados ou formato anterior pode ser herdado** durante a ambiguidade — nem para responder, nem para qualificar, nem para o resumo. |
| A7 | **Persistir o processamento pendente quando possível**: registrar que há um esclarecimento em aberto, para que a resposta seguinte seja interpretada como resposta a ele. |

Motivo: reabrir por padrão contamina um atendimento novo com dados comerciais antigos, o que
é exatamente o que T37 e a invariante I15 proíbem. Errar para o lado do esclarecimento custa
uma pergunta; errar para o lado da reabertura produz um lead com data e número de convidados
do evento errado.

#### Contexto ausente ou corrompido (etapa 3)

| # | Regra |
|---|---|
| S1 | Se o motor **esperava** estado existente, a ausência ou corrupção é **erro de infraestrutura**, não início de conversa. |
| S2 | **Bloquear a transição.** Nenhum evento é aplicado sobre estado desconhecido. |
| S3 | **Não criar atendimento novo silenciosamente** — inclusive quando o identificador informado não é encontrado (N5, N6). |
| S4 | **Preservar a mensagem** para reprocessamento quando o estado for recuperado. |
| S5 | **Emitir alerta operacional** — caminho separado da conversa. |
| S6 | Só iniciar como `novo` quando for **comprovadamente primeiro contato** (campo interno "havia estado esperado?" do contexto recuperado, §6.2, igual a não). |
| S7 | **A falha nunca é interpretada como primeiro contato nem como nova solicitação.** A etapa 5 não é executada sobre contexto inválido. |
| S8 | A interpretação linguística (etapa 4) **pode** rodar sobre contexto inválido **apenas para diagnóstico** — registrar o que a mensagem parecia pedir. Nenhuma transição e **nenhuma gravação comercial** ocorrem sobre estado inválido. |

Motivo: tratar estado perdido como conversa nova apaga silenciosamente o histórico, faz o bot
repetir perguntas já respondidas (violando I16) e pode entregar um resumo incompleto como se
fosse completo. É preferível o atendimento parar e alguém ser avisado.

### 7.2 Persistência e ordem de falhas

| # | Regra |
|---|---|
| Q1 | A persistência necessária ocorre **antes do envio** (etapa 13 antes da 14). |
| Q2 | Se a persistência falhar, **não enviar resposta que dependa da nova transição**. |
| Q3 | **Não afirmar ao interessado que houve handoff se o handoff não foi registrado.** Uma promessa de encaminhamento não gravada é uma promessa que o bot não pode cumprir (doc 03, "Encerramento"). |
| Q4 | **Preservar a mensagem** para reprocessamento idempotente (§4.3), de modo que a retentativa não duplique registro nem resposta. |
| Q5 | **Gerar alerta operacional** fora do fluxo de conversa, quando possível. |
| Q6 | Resposta segura e handoff **só são emitidos quando puderem ser registrados**. Não existe "resposta segura" que promete algo não gravado. |
| Q7 | **Erro de conteúdo com persistência funcionando** → resposta segura + handoff, ambos registrados. |
| Q8 | **Erro de infraestrutura que impede persistência** → bloqueio de emissão + alerta operacional. O interessado não recebe nada em vez de receber algo falso. |

Q7 e Q8 são a distinção que elimina a contradição entre "sempre responder com segurança" e
"nunca prometer o que não foi feito": o que decide é **se a gravação funcionou**, não a
gravidade do erro.

### 7.3 Dois conceitos de persistência

"Persistência" designa duas coisas diferentes neste projeto, e confundi-las produz um erro
grave: usar a Etapa 8 como justificativa para o motor emitir resposta sem gravar estado.

#### Persistência operacional do atendimento — parte necessária do motor

O que ela guarda:

| Item |
|---|
| estado da conversa (doc 06 §1.1) |
| dados já coletados |
| `resultado_qualificacao` |
| `pendencias_resposta` |
| motivo de incompatibilidade |
| motivo de handoff |
| chave de idempotência das mensagens já processadas |
| processamento pendente: mensagem preservada para reprocessamento (S4, Q4) e esclarecimento de identidade em aberto (A7) |

Regra: **é parte necessária do motor e deve existir antes de qualquer emissão real** (Q1).
Sem ela, o motor não tem como cumprir a idempotência do doc 06 §4 passo 1, não tem como
respeitar I16 (não repetir pergunta já respondida) e não tem como afirmar handoff (Q3).

#### Registro comercial de leads — Etapa 8

O que ele abrange:

| Item |
|---|
| destino definitivo do lead |
| consultas administrativas |
| histórico comercial |
| relatórios |
| retenção |
| exportação |
| integração com planilha, CRM ou banco definitivo |

Regra: continua pertencendo à **Etapa 8** e não é pré-requisito da Etapa 3B.

#### A regra que separa os dois

> A Etapa 8 define **onde o lead vive comercialmente**. Ela **não** autoriza o motor a
> emitir sem gravar estado. "Persistência é etapa 8" nunca é justificativa válida para
> violar Q1.

### 7.4 Limite autorizado para a Etapa 3B

A Etapa 3B **poderá**:

| # | Autorizado |
|---|---|
| B1 | criar o **contrato abstrato de persistência** operacional (interface conceitual: gravar, recuperar, marcar mensagem processada); |
| B2 | criar **implementação em memória somente para testes**; |
| B3 | testar falha de gravação, gravação bem-sucedida, recuperação de estado e idempotência; |
| B4 | executar o **pipeline completo em ambiente de teste**. |

A Etapa 3B **não poderá escolher silenciosamente**: SQLite, arquivo JSON, planilha, banco de
dados ou serviço externo. **Qualquer adaptador local não volátil exige decisão específica e
explícita**, fora do escopo da 3B.

Regra obrigatória sobre o repositório em memória:

| # | Regra |
|---|---|
| M1 | Repositório **em memória permite testes** — é suficiente para B1–B4. |
| M2 | Repositório em memória **não permite afirmar que o bot está pronto para operação real**. Ele perde tudo ao reiniciar: estado, idempotência e mensagens preservadas. |
| M3 | **Nenhuma resposta de canal real pode ser emitida sem persistência operacional confiável.** Em memória não é confiável para esse fim. |

---

## 8. Testabilidade

### 8.1 Testáveis sem LLM (obrigatórios)

| Componente | O que o teste prova |
|---|---|
| `CarregadorYaml` | carrega, e falha de forma explícita quando o arquivo falta ou é inválido |
| `ValidadorYaml` | detecta campo obrigatório ausente e aponta qual |
| `ValidadorConsistenciaBase` | **teste obrigatório de divergência**: com um `Rxx` citando valor diferente do YAML carregado, a divergência é detectada, o `Rxx` é reprovado, o campo do YAML em conflito é identificado e nenhum dado divergente é liberado (F3–F5) |
| `NormalizadorEntrada` | identificador do canal produz a chave; sem identificador, a chave composta é usada e marcada como heurística; a mesma frase fora da janela temporal é mensagem nova, não duplicata (§4.3) |
| `OrquestradorMotor` | executa as **14 etapas na ordem**, com **recuperação de contexto (3) antes da interpretação (4) e ambas antes da resolução de identidade (5)**; **estado enviado pelo adaptador é ignorado ou rejeitado** (E3); não emite antes de persistir (Q1); termina o ciclo sem transição em contexto inválido e em identidade ambígua |
| `ResolvedorIdentidade` | usa contexto + interpretação para decidir atendimento ativo, T36, T37 ou ambíguo; **nunca é executado sobre contexto inválido** (S7); em ambiguidade não herda dado algum (A1, A6) |
| `RegrasComerciais` | tipo não aceito, data bloqueada e excesso de convidados produzem violação com motivo (I04) |
| `MaquinaEstados` | as 37 transições do doc 06 §3 e a ordem do §4 |
| `Qualificador` | os cinco resultados oficiais, a faixa entre capacidade sentada e coquetel, e I09 (ausência de dado nunca é incompatibilidade) |
| `DetectorHandoff` | os 12 gatilhos do doc 04, cada um com o motivo correto |
| `SeletorFatos` | nada fora do YAML e das respostas aprovadas entra na lista; campo pendente vira R03; **`Rxx` divergente do YAML não é selecionado** e produz erro de consistência da base (F4) |
| `ValidadorResposta` | rascunho com valor inventado, promessa de prazo, confirmação de data ou desconto é bloqueado; texto literal de `Rxx` também é conferido |
| `Persistencia` (contrato abstrato, com implementação em memória — B1/B2) | gravação, recuperação de estado e idempotência funcionam; falha de gravação bloqueia a emissão e preserva a mensagem; nenhuma afirmação de handoff sem registro (Q2, Q3) |

Esses testes são determinísticos, rápidos e não custam nada por execução. São a rede de
segurança do produto e cobrem os 20 invariantes do doc 06 §8.

### 8.2 Testáveis com resposta simulada do LLM

Entrando com um objeto de interpretação fixo e persistência em memória, sem chamar o modelo:

- pipeline completo da etapa 1 à 14, em **ambiente de teste** (B4);
- ordem de emissão: nada é emitido antes de gravado, e falha de gravação bloqueia
  (Q1, Q2, Q8);
- os cenários `C30`–`C50` do doc 06 (`tests/cenarios-conversa.md`);
- comportamento em confiança baixa, múltiplas intenções e conflito com o estado;
- modo degradado com LLM indisponível.

Casos conceituais obrigatórios de contexto e identidade:

| # | Caso | Resultado esperado |
|---|---|---|
| K1 | O adaptador tenta enviar estado, qualificação ou pendências no contrato de entrada | Campos **rejeitados ou ignorados**; o contexto usado é exclusivamente o da persistência (E1–E3); nenhum valor externo influencia a decisão |
| K2 | Identificador de atendimento **válido** e compatível com canal e contato | Estado **recuperado da persistência** (N2, E4); nenhum dado do contrato externo é usado como estado |
| K3 | Identificador de atendimento **inexistente** (ou de outro contato) | **Bloqueio** com erro operacional, mensagem preservada, alerta emitido. **Nenhum atendimento novo criado** (N5, N6, S3) |
| K4 | Contato com atendimento encerrado envia mensagem sobre **evento diferente** | T37 é aplicado **somente após a etapa 4**, com base nos dados extraídos; nenhum dado comercial do atendimento anterior é herdado (I15) |
| K5 | Mensagem com **referência explícita ao evento anterior** ("o casamento de outubro que a gente falou") | T36: reabertura preservando os dados já registrados, decidida com contexto + interpretação |
| K6 | Contato com **vários atendimentos possíveis** e mensagem sem referência distintiva | **Ambíguo**: pergunta de esclarecimento, atendimento anterior intacto, **sem herança** de data, tipo, convidados ou formato; processamento pendente persistido (A1–A7) |
| K7 | **Contexto corrompido** quando havia estado esperado | Etapa 5 **não é executada**; transição bloqueada, mensagem preservada, alerta emitido; a falha não vira primeiro contato nem nova solicitação (S1–S8) |

### 8.3 Testáveis somente com LLM real (poucos, manuais)

- qualidade da extração em português coloquial de WhatsApp;
- naturalidade do texto;
- as 60 perguntas de `tests/perguntas-criticas.md`, como bateria de aceitação.

### 8.4 Política de testes incrementais

Testar **não** é uma etapa final. A etapa 9 consolida; ela não é a primeira execução.

| # | Regra |
|---|---|
| T1 | Toda implementação da **Etapa 3B** deve **incluir e executar** testes unitários dos componentes que criar — inclusive o `Qualificador`, cuja implementação pertence à 3B (§9). |
| T2 | As **etapas 5 a 8** também testam as próprias entregas — handoff, calendário, WhatsApp e registro de leads entregam código com teste executado. |
| T3 | A **Etapa 9** consolida: testes integrados, regressão, aceitação e cenários ponta a ponta (`tests/cenarios-conversa.md`, `tests/perguntas-criticas.md`). |
| T4 | **Nenhum código é aprovado sem a saída real dos testes correspondentes** — saída colada no relato da execução, não afirmação de que passou. |
| T5 | Testes com **LLM real** podem continuar limitados e manuais quando apropriado; não bloqueiam a entrega de componentes determinísticos. |

Consequência: cada etapa da 3B em diante fecha com dois artefatos — o código e a saída dos
seus testes.

Nenhum teste é criado ou executado nesta etapa documental.

---

## 9. Estratégia inicial de uso do LLM

| | Estratégia 1 — determinístico primeiro, LLM depois | Estratégia 2 — LLM desde o início, só extração e redação, cercado por validação |
|---|---|---|
| Velocidade de desenvolvimento | Menor. Um interpretador por palavra-chave para português livre é trabalhoso e será descartado. | Maior. A extração difícil sai de fábrica. |
| Risco de alucinação | Menor no começo, mas concentrado no final, quando o LLM entra em um sistema já grande. | Controlado desde o primeiro dia pelo `ValidadorResposta`, que é determinístico. |
| Custo | Menor no início. | Baixo: só extração e redação, mensagens curtas. |
| Facilidade de teste | Alta. | Alta também — o núcleo é testado com interpretações fixas (§8.2). |
| Qualidade conversacional | Baixa. Robô de palavra-chave frustra em WhatsApp. | Alta. |
| Experiência limitada do mantenedor | Enganosa: parece mais simples e produz duas implementações do mesmo problema. | Melhor: uma arquitetura só, do começo ao fim. |

### Recomendada: **Estratégia 2**

O risco de alucinação não é reduzido adiando o LLM — é reduzido pela camada de validação, que
existe nas duas estratégias. Adiar apenas gera trabalho jogado fora e uma segunda migração.

Ordem de construção dentro da Estratégia 2 — importa para o mantenedor iniciante:

1. componentes 1, 2, 3 e 6 (dados, regras, estado, validação) mais o `OrquestradorMotor` e o
   limite de persistência, testados com interpretações escritas à mão;
2. componente 7 (handoff e resumo);
3. redação em **modo literal**: usar o texto aprovado sem reescrita;
4. interpretação por LLM (componente 4);
5. redação natural (componente 5), ainda sujeita ao validador.

Cada passo entrega código **com a saída dos seus testes unitários** (T1/T4).

Fronteira de Qualificação, arbitrada: o `Qualificador` é componente do motor (§2, item 2) e
sua **implementação pertence à Etapa 3B**, não a uma etapa autônoma de roadmap. Dentro do
passo 1 acima, ele **precede a `MaquinaEstados`**: a máquina consome a classificação e as
condições produzidas pelas regras de qualificação (doc 06 §1.2, T08, T09, T13, T21) e não
pode duplicar essa lógica comercial. Nenhum dos dois está implementado.

O que os passos 1 a 3 entregam, com precisão:

| Afirmação correta | Afirmação incorreta |
|---|---|
| Os componentes e o pipeline funcionam **ponta a ponta em testes**, com persistência simulada em memória (B2). | "O produto funciona ponta a ponta." |
| O **modo literal** permite validar todo o fluxo **sem LLM**. | "O bot está pronto, falta só o LLM." |
| A **operação real** depende de três coisas que a 3B não entrega: persistência operacional confiável (M3), canal de entrega do handoff (etapa 5) e adaptador de canal (etapa 7). | "Falta só publicar." |
| A Etapa 3B entrega **núcleo testável**, não bot publicado. | "Etapa 3B = bot funcionando." |

O modo literal permanece disponível para sempre, como fallback de indisponibilidade (§7).

Fornecedor e modelo não são escolhidos nesta etapa. O adaptador de `src/llm/` deve isolar
essa escolha atrás de um limite único.

---

## 10. Estrutura futura sugerida

Estrutura mínima. **Nenhuma pasta foi criada.**

```text
src/
  orchestrator/   OrquestradorMotor: coordena o pipeline. Ponto de entrada único.
  config/         caminhos, variáveis de ambiente, modo de execução. Sem regra comercial.
  knowledge/      leitura e validação do YAML e das respostas aprovadas. Somente leitura.
  domain/         regras comerciais determinísticas e qualificação.
  conversation/   máquina de estados, ordem de processamento, dados do atendimento.
  llm/            adaptador de interpretação e redação. Não conhece o YAML.
  validation/     validação da resposta contra os fatos autorizados.
  handoff/        detecção de gatilho, motivo e montagem do resumo.
  persistence/    persistência operacional atrás de um limite único: contrato abstrato +
                  implementação em memória para testes. Armazenamento não volátil e
                  registro comercial de leads não pertencem à Etapa 3B (§7.3, §7.4).
tests/
```

| Pasta | Responsabilidade | Não pode |
|---|---|---|
| `src/orchestrator/` | ordem das 14 etapas, recuperação de contexto antes da interpretação e da resolução de identidade, decisão do que emitir, aplicação de Q1–Q8 | ter regra comercial própria; ser importado pelos demais componentes (D1); aceitar estado vindo do canal (D9) |
| `src/config/` | onde estão os arquivos, qual o modo de execução | conter valor comercial |
| `src/knowledge/` | **código** que lê e valida os arquivos de `knowledge/` na raiz — inclui a conferência `Rxx` × YAML (F3) — não guarda dado | escrever nos arquivos de dado |
| `src/domain/` | capacidade, pacote, datas, tipos, qualificação | ter constante comercial; depender de `src/llm` (D2) |
| `src/conversation/` | estados, transições, ordem do doc 06 §4, dados do atendimento | duplicar regra comercial; depender de `src/llm` |
| `src/llm/` | prompts de extração e redação, chamada ao provedor | receber o YAML; decidir (D3) |
| `src/validation/` | conferir rascunho contra os fatos autorizados | gerar texto; ler estado ou mensagem (D4) |
| `src/handoff/` | motivo, resumo no formato do doc 04, entrega | negociar; prometer prazo; reavaliar regra comercial (D5) |
| `src/persistence/` | contrato de persistência **operacional**: gravar, recuperar, marcar mensagem processada, sinalizar falha | decidir conteúdo; escolher SQLite, JSON, planilha, banco ou serviço externo sem decisão específica (§7.4); abrigar registro comercial de leads |
| `tests/` | testes automatizados; `tests/*.md` atuais viram casos | depender de LLM real, exceto na bateria de aceitação |

Dependência circular entre essas pastas é proibida (D7). Quando dois componentes parecerem
precisar um do outro, a coordenação sobe para `src/orchestrator/`.

Os dados continuam em `knowledge/` na raiz do repositório. `src/knowledge/` é apenas o
adaptador de leitura — a duplicação de nome é intencional e a distinção é obrigatória.

O ponto de entrada do motor é uma única chamada ao `OrquestradorMotor`
(`mensagem de entrada → decisão de saída`), sem servidor no MVP. Não há pasta de canal ainda:
o adaptador de WhatsApp é etapa 7 e será quem **chama** o motor, nunca o contrário (D6).

---

## 11. Fora do escopo desta etapa

Não foi criado, escolhido nem instalado: código, testes, `package.json`,
`requirements.txt`, biblioteca de leitura de YAML, biblioteca de schema, ferramenta de
observabilidade, banco, arquivo ou qualquer armazenamento não volátil, API, framework web,
hospedagem, provedor de IA, modelo, integração de WhatsApp, integração de calendário. Nenhum
commit e nenhum push. A Etapa 3B não foi iniciada.

---

## 12. Riscos e pendências

| # | Risco / pendência | Impacto | Onde se resolve |
|---|---|---|---|
| 1 | Rota de WhatsApp indefinida (oficial × não oficial) | pode exigir adaptador em outra linguagem | etapa 7 |
| 2 | Persistência **operacional** — contrato e implementação em memória | necessário para testar o pipeline ponta a ponta; em memória não sustenta operação real (M2, M3) | **Etapa 3B** |
| 2a | Persistência **operacional não volátil** — armazenamento mínimo para uso real | sem ela, nenhuma resposta pode ser emitida em canal real (M3). Nenhuma tecnologia escolhida | **decisão específica e explícita antes de qualquer uso real** — não é decisão da 3B nem da etapa 8 |
| 2b | **Registro comercial de leads** — destino definitivo, histórico, relatórios, exportação | não bloqueia a 3B; não pode ser usado como justificativa para emitir sem gravar estado (§7.3) | etapa 8 |
| 3 | Critério técnico de "mesmo evento × nova solicitação" (T36/T37) | enquanto indefinido, mais mensagens caem no caminho de esclarecimento de §7.1 — seguro, porém mais lento na conversa | modelo de dados, Etapa 3B |
| 3a | Destino do alerta operacional não definido | S5, Q5 e F4 exigem um canal separado da conversa; hoje não existe | etapa 5 / etapa 8 |
| 3b | Janela temporal da chave composta de idempotência (§4.3) | curta demais duplica resposta; longa demais engole repetição humana legítima | Etapa 3B, com medição |
| 3c | Divergência `Rxx` × YAML depende de mapear cada `Rxx` ao campo que ele cita | mapeamento incompleto deixa divergência passar sem detecção | Etapa 3B |
| 4 | `R01` e `R15` ainda em **AGUARDA APROVAÇÃO** | saudação e encerramento sem texto aprovado | Douglas Bianchi |
| 5 | Canal de entrega do resumo e SLA indefinidos | etapa 14 do pipeline fica sem destino | etapa 5 |
| 6 | Comportamento fora do horário de atendimento indefinido | resposta fora de horário não especificada | Douglas Bianchi |
| 7 | Precisão do validador de resposta | validador fraco deixa passar valor inventado; forte demais bloqueia texto correto | Etapa 3B, com os casos de `tests/perguntas-criticas.md` |
| 8 | Custo por conversa não medido | sem parâmetro de custo do LLM | etapa 9 |
| 9 | Política de retenção de log não definida (L7) | dado pessoal guardado sem prazo | antes da produção, etapa 10 |

Nenhuma dessas pendências bloqueia a Etapa 3B.

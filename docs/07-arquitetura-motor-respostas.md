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

### 2.3 Arbitragem C — contrato do índice estruturado de respostas aprovadas

**Estado: ARBITRADA / NÃO MATERIALIZADA.** O contrato descrito nesta seção está **fechado**
e existe **apenas documentalmente, aqui**; **nenhuma de suas materializações futuras existe
ainda** em `knowledge/`, em `src/` ou em `tests/`. Em particular, e sem atenuação:

| # | Continua verdadeiro |
|---|---|
| C-E1 | o **índice não existe** — nenhum arquivo foi criado |
| C-E2 | `knowledge/respostas-aprovadas.md` **não foi convertido** e **não foi alterado** |
| C-E3 | **nenhum renderizador** existe |
| C-E4 | **nenhum analisador do índice** existe |
| C-E5 | `ValidadorConsistenciaBase` continua **não implementado** |
| C-E6 | `SeletorFatos` continua **não implementado** |
| C-E7 | `ValidadorResposta` continua **não implementado** |
| C-E8 | **S2-D8 continua ABERTA** (doc 06 §11; §12, item 10) |
| C-E9 | **nenhuma condição de ciclo nova** foi criada (§4.4) |

**C não está implementada.** Esta seção fecha o contrato futuro; ela não o materializa.

Pendência **C**, registrada em `docs/00-estado-atual.md`: falta um contrato estruturado,
**legível por máquina**, relacionando cada `Rxx` aos campos de `knowledge/casa77.yaml`.
Esta seção **fecha esse contrato**; o **artefato que o materializa continua inexistente**.
Enquanto a materialização não existir, **F3**–**F5** (§2.2) seguem sendo política sem
mecanismo — a conferência depende de alguém reler o Markdown, que é exatamente o que §2.2
recusa como garantia.

#### C-1 — Artefato futuro aprovado

Nome aprovado para a futura materialização:

**`knowledge/indice-respostas-aprovadas.yaml`**

**Este arquivo NÃO é criado por esta arbitragem.** O nome é fixado agora para que a
materialização futura não invente um caminho alternativo nem espalhe o contrato por vários
arquivos.

| # | O índice futuro **conterá somente** |
|---|---|
| C-1a | identificadores |
| C-1b | status |
| C-1c | *bindings* |
| C-1d | caminhos YAML |
| C-1e | predicados |
| C-1f | formatos |
| C-1g | metadados estruturais permitidos |

| # | O índice futuro **NUNCA conterá** |
|---|---|
| C-1h | preço, capacidade, horário, prazo ou qualquer condição comercial |
| C-1i | endereço |
| C-1j | texto de resposta |
| C-1k | *snapshot* de valor |
| C-1l | versão congelada do YAML |
| C-1m | *hash* de valor |

A razão é a de **P8** e **F1**: qualquer valor copiado para o índice cria uma segunda fonte
de fato comercial e reintroduz, dentro do próprio mecanismo antidivergência, a divergência
que ele existe para detectar.

#### C-2 — Modelo conceitual

```text
Rxx
  └─► fragmentos emitíveis
         └─► bindings (RENDERIZADO | ASSERTIVA)
```

**`Rxx`:**

| # | Regra |
|---|---|
| C-2a | `id` obrigatório e único |
| C-2b | padrão fechado `Rxx` |
| C-2c | um ou mais fragmentos |
| C-2d | **sem status armazenado no nível do `Rxx`** |
| C-2e | sem título duplicado |
| C-2f | **sem campo `handoff_obrigatorio`** |
| C-2g | **sem campo `cita_fato_comercial`** |

**Fragmento emitível:**

| # | Regra |
|---|---|
| C-2h | `id` obrigatório e único **dentro do `Rxx`** |
| C-2i | **status obrigatório** |
| C-2j | **zero ou um** `itera_sobre` |
| C-2k | *bindings*, **inclusive lista vazia explícita** |
| C-2l | corresponde **somente** a conteúdo que **pode ser emitido ao interessado** |

**Notas e instruções internas do Markdown** — os trechos que hoje explicam origem, motivo,
aplicação ou encaminhamento:

| # | Regra |
|---|---|
| C-2m | **não são fragmentos** |
| C-2n | **não recebem status** |
| C-2o | **não recebem *bindings*** |
| C-2p | **não podem ser emitidas por acidente** |

A separação é a garantia central do modelo: hoje texto emitível e instrução operacional
convivem no mesmo `Rxx` sem marcação estrutural, e nada impede que uma instrução interna
chegue ao interessado como se fosse resposta aprovada.

#### C-3 — Status canônico

Vocabulário **fechado**:

| # | Status |
|---|---|
| C-3a | `APROVADO` |
| C-3b | `AGUARDA_APROVACAO` |
| C-3c | `BLOQUEADO` |

**Sem valor padrão.** Fragmento sem status é **erro de contrato**, nunca `APROVADO`
implícito.

**Sem `PARCIAL`.** Um `Rxx` agregado pode ser parcial apenas como **derivação** dos status
dos seus fragmentos — nunca como valor armazenado.

`R01` e `R15` permanecem **não aprovados** (§12, item 4). **Nenhum status comercial é
alterado por esta arbitragem.**

#### C-4 — *Binding* `RENDERIZADO`

Insere no texto um valor lido do YAML carregado.

| # | Regra |
|---|---|
| C-4a | nome obrigatório e único no fragmento |
| C-4b | caminho YAML **explícito** |
| C-4c | *placeholder* correspondente **obrigatório** |
| C-4d | formato **fechado** obrigatório (C-6) |
| C-4e | o valor é **sempre** obtido do YAML carregado |
| C-4f | o índice **nunca** armazena o valor |

Em iteração:

| # | Regra |
|---|---|
| C-4g | `itera_sobre` aponta para uma **coleção** |
| C-4h | os *bindings* do item podem usar **caminho relativo** |
| C-4i | **sem índice posicional** |

**Nenhuma leitura oculta de outro campo é permitida.** O que não estiver declarado como
*binding* não é lido.

#### C-5 — *Binding* `ASSERTIVA`

Não insere valor algum no texto. Declara uma condição que precisa ser verdadeira sobre o
YAML carregado para que a **redação já aprovada** continue verdadeira.

| # | Regra |
|---|---|
| C-5a | nome obrigatório e único |
| C-5b | caminho YAML **explícito** |
| C-5c | **predicado obrigatório** |
| C-5d | **sem *placeholder*** |
| C-5e | **sem formato** |
| C-5f | **não insere o valor no texto** |

Vocabulário de predicados, **fechado**:

| # | Predicado |
|---|---|
| C-5g | `EH_VERDADEIRO` |
| C-5h | `EH_FALSO` |

Significado **único** de `ASSERTIVA`:

> a redação deste fragmento é consistente **somente se** este predicado for verdadeiro sobre
> o YAML carregado.

`ASSERTIVA` **NÃO**:

| # | Não faz |
|---|---|
| C-5i | cria regra comercial |
| C-5j | altera dado |
| C-5k | produz ação (§4.5) |
| C-5l | produz evento |
| C-5m | produz handoff |
| C-5n | produz `E18` |
| C-5o | produz condição de ciclo (§4.4) |
| C-5p | decide `resposta_aprovada_disponivel` |
| C-5q | decide `pendencia_impeditiva` |

#### C-5.1 — `ASSERTIVA` sobre campo relacionado a handoff: **consistency-only**

Um campo do YAML relacionado a handoff **pode** aparecer como caminho de uma `ASSERTIVA`
**somente** quando ela serve para **conferir a veracidade de uma frase já existente do
`Rxx`**. Esse uso é **CONSISTENCY-ONLY**.

Ele **não** torna o índice fonte da política de handoff. Ele **não** pode ser usado como:

| # | Uso proibido |
|---|---|
| C-5r | gatilho |
| C-5s | produtor de `E18` |
| C-5t | produtor de handoff |
| C-5u | regra da `MaquinaEstados` |
| C-5v | condição de §4.4 |
| C-5w | substituto de `docs/04-handoff-humano.md` |
| C-5x | substituto de `docs/06-maquina-de-estados.md` |
| C-5y | substituto do próprio YAML |

O índice continua **sem campo `handoff_obrigatorio`** (C-2f). A regra correta é a **não
duplicação de política**, e não a proibição do caminho:

> **Nenhuma POLÍTICA de handoff é duplicada no índice.**

Formular a regra como "nenhum campo relacionado a handoff pode aparecer" seria **falso**:
ela impediria justamente a conferência de consistência que a pendência C existe para
viabilizar.

#### C-6 — Formatos: apresentação pura, sem dependência oculta

Vocabulário **fechado** de **apresentação pura**:

| # | Formato | Regra mínima |
|---|---|---|
| C-6a | `inteiro` | representação decimal do inteiro, **sem alterar o valor** |
| C-6b | `inteiro_agrupado` | o **mesmo** inteiro, com agrupamento visual de milhar |
| C-6c | `simbolo_moeda` | transformação **exclusivamente de apresentação** do código monetário **explicitamente recebido por *binding***. No corpus atual, `BRL` pode ser apresentado pelo símbolo correspondente. Código não suportado **falha**, e nunca é inferido |
| C-6d | `hora` | somente apresentação **da mesma hora**. **Não** introduz fuso nem cálculo. Formato incompatível **falha** |
| C-6e | `texto` | identidade: insere o valor **sem modificação** |
| C-6f | `lista` | preserva **todos** os itens e **a ordem**; somente pontuação e conjunção de apresentação. Nenhum item pode ser filtrado, reordenado ou parafraseado |

Proibido em qualquer formato: função customizada, expressão regular, recorte de string,
resumo, paráfrase, cálculo, regra específica por `Rxx`, **leitura implícita de campo
adicional**, transformação semântica e arredondamento.

**Sem dependência oculta.** Um formato composto de moeda — que devolvesse símbolo e valor
juntos — esconderia a leitura de `precos.moeda` dentro do formatador. Ele **não é
versionado**. Quando o símbolo monetário aparece no *template*, **`precos.moeda` precisa ser
um *binding* EXPLÍCITO**. Exemplo **conceitual** e futuro:

| *Placeholder* | *Binding* explícito | Formato |
|---|---|---|
| `{{moeda}}` | `precos.moeda` | `simbolo_moeda` |
| `{{valor}}` | caminho numérico correspondente | `inteiro_agrupado` |

**Nenhum formatador de valor pode buscar `precos.moeda` por conta própria.**

#### C-7 — `null` e `pendente`

**Não existe `politica_ausencia` no modelo.** C **não** atribui significado positivo a
`null` e **não** atribui significado positivo a `pendente`: a regra normativa continua
**fora** do índice, nas fontes já existentes (doc 06 §1.3, `knowledge/casa77.yaml`,
`knowledge/informacoes-pendentes.md`).

Para C, a consequência é estrutural: se um *binding* **necessário** a um fragmento que se
pretende `APROVADO` resolve para `null`, ou para uma estrutura cujo `status` seja
`pendente`, o fragmento **não pode ser tratado como materializado e aprovado** pelo novo
contrato. O caso é **bloqueado e reportado** — **sem exceção local no índice**.

#### C-8 — Apresentação pura × transformação semântica

Somente **apresentação pura** integra os formatos fechados de C-6. São **proibidos** como
formatador, entre outros: remover o CEP de um endereço; resumir uma observação; escolher
parte de uma string; parafrasear; reordenar conteúdo; omitir item de lista; traduzir uma
regra; calcular um valor; converter uma ausência em conclusão comercial.

**Se o texto aprovado exigir transformação semântica para corresponder ao YAML, a
materialização é BLOQUEADA.** A solução dependerá de fonte estruturada adequada ou de
decisão de conteúdo futura — nunca de um formatador que "quase" acerta.

#### C-9 — Conflitos já identificados

Registro **factual**, sem valores comerciais: a auditoria de planejamento identificou casos
que **não podem ser convertidos silenciosamente**. **Nenhum deles é decidido aqui.**

| `Rxx` | Natureza do conflito |
|---|---|
| `R10` | conflito entre campo `null`, observação textual e redação aprovada sobre **mínimo de convidados** (`capacidade.minimo_convidados`, `capacidade.observacao_minimo`) |
| `R20` | **mais de um campo candidato** sustenta partes distintas da frase de **retenção/entrada**; vínculo incorreto pode produzir **afirmação falsa** (`cancelamento`, `pagamento.opcoes`) |
| `R13` | a representação estruturada atual do **endereço** não é **textualmente equivalente** à redação aprovada (`localizacao.endereco_completo`) |
| `R17` | o **fragmento emitível é genérico**; a **enumeração divergente** é **NOTA INTERNA**, não texto emitível (`eventos.nao_aceitos`, `eventos.observacao_nao_aceitos`) |

Cada um é exatamente o tipo de caso que C-8 manda **bloquear** em vez de acomodar.

#### C-10 — Completude dos literais

**Não é invariante** que "nenhum fragmento contém qualquer número fora de *placeholder*":
essa formulação produziria falso positivo para identificador, nome próprio ou texto estático
que **não representa valor comercial variável**.

A regra normativa correta é:

> Todo **fato comercial ou operacional VARIÁVEL** cuja fonte seja o YAML deve ser
> **`RENDERIZADO`**, ou **coberto por `ASSERTIVA`** quando isso for necessário para provar a
> consistência da redação.

A materialização futura deverá **auditar cada fragmento emitível de todos os `Rxx`**. Nenhum
literal com origem no YAML pode permanecer silenciosamente fora desse mapeamento. **Literal
estático não derivado do YAML não ganha autoridade comercial por estar no Markdown** (§2.2,
**F2**, **F6**).

Contagens da auditoria de planejamento **não são versionadas aqui** e **não viram requisito
arquitetural**.

#### C-11 — Fontes autoritativas: estado atual × modelo futuro

Esta arbitragem **não cria o índice** e, portanto, **não cria lacuna de fonte de verdade**.

| Insumo | **ESTADO ATUAL** — vigente até a materialização | **MODELO FUTURO** — somente após materialização validada |
|---|---|---|
| texto / *template* | `knowledge/respostas-aprovadas.md` | `knowledge/respostas-aprovadas.md` |
| status | `knowledge/respostas-aprovadas.md` | `knowledge/indice-respostas-aprovadas.yaml` |
| valores | `knowledge/casa77.yaml` | `knowledge/casa77.yaml` |
| *bindings*, predicados, formatos | **não existem** | `knowledge/indice-respostas-aprovadas.yaml` |

**A migração da autoridade do STATUS só ocorre quando a materialização do índice e a bijeção
entre `Rxx` e fragmentos forem validadas.** Até lá, **o status NÃO é removido do Markdown**.

#### C-12 — Fronteira C × S2-D8

C **NÃO**:

| # | Não faz |
|---|---|
| C-12a | mapeia pergunta para `Rxx` |
| C-12b | categoriza pergunta |
| C-12c | determina `resposta_aprovada_disponivel` |
| C-12d | determina `pendencia_impeditiva` |
| C-12e | confirma `E09` |
| C-12f | atribui produtor |
| C-12g | cria `DetectorHandoff` |
| C-12h | cria condição de ciclo |

**S2-D8 permanece ABERTA** (doc 06 §11; §12, item 10). O status `BLOQUEADO` de um fragmento
**não é, por si só**, `E09` nem `pendencia_impeditiva`: ele é um fato sobre a base, não uma
decisão de ciclo. **O consumo futuro pertence à arbitragem S2-D8**, não a C.

#### C-13 — Efeito sobre F3–F5

O contrato torna **F3**–**F5** (§2.2) **implementáveis futuramente**, e **não os
implementa**:

| # | Efeito |
|---|---|
| C-13a | `RENDERIZADO` **elimina divergência de valor por construção** — o valor vem do YAML carregado, não de uma cópia no texto |
| C-13b | `ASSERTIVA` torna **verificável** uma afirmação sobre o estado do YAML que hoje só existe em prosa |
| C-13c | a falha é **localizável** conceitualmente como `Rxx` + fragmento + caminho YAML |

**Nenhum conciliador. Nenhum LLM arbitra divergência. O YAML prevalece** (**F5**, **P8**).

#### C-14 — O que C não cria

| # | Preservado sem alteração |
|---|---|
| C-14a | os **14 componentes** de §4.1 |
| C-14b | as **nove responsabilidades** arquiteturais de §2 |
| C-14c | o **pipeline de 14 etapas** (§5) |
| C-14d | todos os estados, eventos e transições do doc 06 |
| C-14e | as **oito condições** de §4.4 |
| C-14f | as **11** `IntencaoConversacional`, os erros `E-Nb-1`–`E-Nb-19` e os cenários `K-Nb-1`–`K-Nb-40` (§6.3) |
| C-14g | os **12** `CriterioIdentidade` e os **oito** campos de `DecisaoIdentidade` (§7.1) |

C **não cria** componente, estado, evento, transição, condição, critério, enum de execução,
pendência nova nem subetapa. **A 3B.8 não existe.**

**Nota temporal sobre C-14f.** A linha C-14f registra o que C preservou **no momento da
arbitragem C**, e continua correta como registro histórico. A micro-arbitragem **AJ2**,
**posterior** (§6.3), mantém as **11** `IntencaoConversacional` e os erros
**`E-Nb-1`–`E-Nb-19`**, mas **estende** a fronteira de cenários de `K-Nb-1`–`K-Nb-40` para
**`K-Nb-1`–`K-Nb-51`**. **C não é reaberta por isso** e permanece **ARBITRADA / NÃO
MATERIALIZADA**.

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
| `ResolvedorIdentidade` | decidir se a mensagem pertence a atendimento ativo, a T36, a T37 — ou se é ambígua — aplicando a cascata determinística **D0–D6** de §7.1. **Puro e determinístico**: zero I/O, zero rede, zero LLM, zero YAML, zero relógio. Não calcula elegibilidade nem recência, não consulta persistência, não interpreta texto, não cria atendimento, não persiste, não aplica transição e não altera a `MaquinaEstados` | **conjunto elegível fechado de candidatos já produzido pela etapa 3** (§6.2) + **`ids_em_atendimento_humano`** — o conjunto **H**, entrada **separada** do conjunto elegível e **fora** da política N-a (§6.2, H1–H6) + **projeção estruturada da interpretação** (§6.3) + veredito do identificador já validado (§6.1.1) + **`id_atendimento_validado`** — o **ID técnico opaco** do atendimento identificado, projetado pela etapa 3 quando o veredito é `ENCONTRADO` e `None` quando é `NAO_INFORMADO` (§6.2, arbitragem R-I) | **decisão auditável** (§7.1): `identidade`, `id_atendimento_alvo`, `criterio`, `situacao_takeover`, `candidatos_avaliados`, `classificacao_por_candidato`, `vinculo_declarado`, `escopo_restrito_por_identificador`. `identidade` pode ser `None` em **três** situações estruturalmente distintas: `PRIMEIRO_CONTATO_COMPROVADO`, `SEM_CANDIDATO_ELEGIVEL` e **`situacao_takeover != SEM_TAKEOVER`** — neste último caso porque a resolução de referente é **curto-circuitada antes de D0–D6** (R5, §7.1). As três continuam distinguíveis por campos estruturados (`criterio` e `situacao_takeover`), **sem criar quinto membro em `Identidade`**. **Nenhum texto livre na saída** |
| `CarregadorYaml` | ler `knowledge/casa77.yaml` uma vez por execução e manter em memória | caminho do arquivo | estrutura carregada + versão |
| `ValidadorYaml` | conferir presença, tipo e coerência dos campos exigidos pelas regras | estrutura carregada | válido / lista de campos faltantes |
| `ValidadorConsistenciaBase` | conferir cada `Rxx` que cita fato comercial contra o YAML carregado (F3) | respostas aprovadas + YAML | lista de divergências, com `Rxx` e campo do YAML |
| `NormalizadorEntrada` | limpar a mensagem e calcular a chave de idempotência conforme §4.3 | mensagem bruta + metadados do canal | mensagem normalizada + chave + origem da chave |
| `RegistroAtendimento` | registrar dados e correções (`E02`–`E05`), sobrescrevendo valores corrigidos | dados extraídos + estado | dados atualizados + lista de correções |
| `RegrasComerciais` | avaliar tipo, data, número de convidados e formato contra o YAML | dados + YAML | lista de violações com motivo e campo de origem |
| `Qualificador` | calcular `resultado_qualificacao` conforme doc 02 §6 e §6.1. Recebe as **pendências impeditivas já classificadas**; **não detecta pendência** (doc 06 §11 — S2-D8) | dados + violações + **pendências impeditivas já classificadas** | um dos cinco valores oficiais + motivo + campos ausentes |
| `MaquinaEstados` | aplicar a ordem do doc 06 §4/§4.2 e a tabela de transições. **Não lê o YAML** e **não fabrica eventos**: consome eventos já confirmados e condições já estruturadas | estado + eventos confirmados + `Qualificacao` + condições já estruturadas (§4.4), **incluindo `insumo_qualificacao_atualizado`** (doc 06 §4.1) | caminho percorrido + **`transicoes_que_mudaram_estado`** (§6.2, **materializada em runtime**) + **estado final único** + ações obrigatórias (§4.5) + efeitos auditáveis |
| `DetectorHandoff` | reconhecer os **gatilhos 3–10** do doc 04 e emitir `E18` com motivo (partição do doc 06 §9). **Não recebe `Qualificacao`**; não recalcula regra comercial, pendência nem qualificação | mensagem interpretada + dados + YAML | motivo(s) de handoff |
| `SeletorFatos` | escolher quais fatos aprovados podem entrar na resposta, **conferindo cada `Rxx` contra o YAML antes de selecioná-lo** (F3). **Não produz condição consumida pela `MaquinaEstados`** (§4.4): roda nas etapas 8–9, depois da primeira chamada da máquina | perguntas + estado + YAML + respostas aprovadas | lista fechada de fatos autorizados, ou divergência de base |
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

**§4.1 permanece inalterada, com 14 componentes.** A arbitragem **N-b** (§6.3) fecha o
contrato da **saída da etapa 4** sem criar componente algum: o "produtor de interpretação
da etapa 4" é **fronteira funcional** dentro do **limite único de LLM** de §4.2 e §9
(N-b-F1, N-b-F2), **não** um `Interpretador` determinístico e **não** um componente 15.

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

### 4.4 Condições de ciclo consumidas pela `MaquinaEstados`

Fronteira estrutural da máquina, arbitrada na S3. É **contrato conceitual**, não
implementação: nenhum código é criado nesta etapa.

A máquina recebe as condições **já determinadas a montante** e nunca as calcula. Nenhum
campo carrega dado pessoal (PII), texto de mensagem ou valor comercial.

| # | Condição | Forma | Produtor |
|---|---|---|---|
| 1 | `insumo_qualificacao_atualizado` | `bool \| None` (doc 06 §4.1) | etapa 6 do pipeline (§5) |
| 2 | `pendencia_impeditiva` | `bool \| None` | **não atribuído — S2-D8** (doc 06 §11) |
| 3 | `motivos_handoff` | conjunto/tupla de **identificadores textuais opacos** | `DetectorHandoff` (gatilhos 3–10, doc 06 §9) |
| 4 | `resposta_aprovada_disponivel` | `bool \| None` | **não atribuído — S2-D8** (doc 06 §11) |
| 5 | `interesse_confirmar_disponibilidade` | `bool \| None` | **fronteira da etapa 4** (arbitragem N-b, §6.3): derivada da `Interpretacao` pela **função total** N-b-CD1–N-b-CD4, abaixo. Único produtor de `CondicoesCiclo` que N-b atribui |
| 6 | `calendario_integrado` | `bool \| None` | configuração/integração avaliada a montante |
| 7 | `identidade` | resultado estruturado do `ResolvedorIdentidade` (§7.1) | `ResolvedorIdentidade` (etapa 5) |
| 8 | `motivo_encerramento` | motivo estruturado entre as **quatro** modalidades aprovadas de T35 (doc 06 §3) | **não atribuído — S3-D1** |

Onde o produtor está pendente, ele **permanece pendente**: esta seção descreve a fronteira,
não escolhe componente concreto.

**Condição 5 — função total** (arbitragem N-b, §6.3). Esta é a **única** linha da tabela acima
alterada por N-b. As demais **sete** condições permanecem exatamente como estão, e as condições
**2**, **4** e **8** continuam **NÃO ATRIBUÍDAS**.

| # | Entrada | `interesse_confirmar_disponibilidade` |
|---|---|---|
| N-b-CD1 | `Interpretacao` válida + `INTERESSE_CONFIRMAR_DISPONIBILIDADE` com confiança `ALTA` | `True` |
| N-b-CD2 | `Interpretacao` válida + `INTERESSE_CONFIRMAR_DISPONIBILIDADE` com confiança `BAIXA` | `False` |
| N-b-CD3 | `Interpretacao` válida + intenção **ausente** | `False` |
| N-b-CD4 | **Sem `Interpretacao`** — produtor indisponível ou erro de contrato na fronteira da etapa 4 | `None` |

`True`/`False` significam **avaliado neste ciclo**; `None` significa **não avaliado neste
ciclo**. `None` **não** é "falso implícito".

### 4.5 Contrato das ações da `MaquinaEstados`

As "ações obrigatórias" devolvidas pela máquina são **vocabulário técnico fechado**:

| # | Propriedade |
|---|---|
| 1 | **semânticas**, não textuais — descrevem *o que deve acontecer*, nunca *como será dito* |
| 2 | **sem referência a `Rxx`** e sem consulta a `knowledge/respostas-aprovadas.md` |
| 3 | **sem conteúdo comercial** — nenhum preço, capacidade, horário, prazo ou condição |
| 4 | **declarativas**: a máquina as **emite**, e **nunca as executa** |
| 5 | **tupla ordenada** quando o documento fixa ordem entre elas |

Cobertura obrigatória: **cada `Txx` de T01–T41 deve estar coberta por pelo menos um** dos
seguintes — um código de ação; um efeito paralelo `P1`–`P6` (doc 06 §4.3); um campo
dedicado da saída; ou uma mudança de estado suficiente por contrato.

A materialização textual autorizada continua sendo decidida pelo `SeletorFatos` e pela
redação (§4.1, §4.2), nunca pela máquina.

#### Vocabulário aprovado — `AcaoMaquina`

Contrato técnico fechado da S3, com **exatamente 20 códigos**. Nenhuma ação pode ser
acrescentada ou renomeada, e nenhuma delas cita `Rxx`.

| # | Código |
|---|---|
| 1 | `APRESENTAR_ATENDIMENTO_INICIAL` |
| 2 | `RESPONDER_PERGUNTA_COMERCIAL` |
| 3 | `PERGUNTAR_PROXIMO_CAMPO_AUSENTE` |
| 4 | `PERGUNTAR_FORMATO` |
| 5 | `RETOMAR_COLETA_SEM_REPETIR` |
| 6 | `INFORMAR_REGRA_INCOMPATIVEL` |
| 7 | `INFORMAR_RESSALVA_DE_CAPACIDADE` |
| 8 | `INFORMAR_CONDICOES_DE_VISITA` |
| 9 | `INFORMAR_LACUNA_DE_INFORMACAO` |
| 10 | `INFORMAR_NAO_CONFIRMACAO_DE_DISPONIBILIDADE` |
| 11 | `DESPEDIR_SEM_CONTINUIDADE` |
| 12 | `REFORCAR_ENCAMINHAMENTO` |
| 13 | `EMITIR_MENSAGEM_DE_ENCAMINHAMENTO` |
| 14 | `NAO_AVANCAR_COLETA` |
| 15 | `SILENCIAR_RESPOSTA_AUTOMATICA` |
| 16 | `PREPARAR_RESUMO` |
| 17 | `ENTREGAR_RESUMO` |
| 18 | `SOLICITAR_CONSULTA_CALENDARIO` |
| 19 | `REABRIR_ATENDIMENTO` |
| 20 | `ABRIR_NOVO_ATENDIMENTO` |

`DESPEDIR_SEM_CONTINUIDADE` é produzida por **T35 somente para `SEM_INTERESSE`** (doc 06
§3). Para `ENGANO`, `SPAM` e `INCOMPATIBILIDADE_ACEITA`, T35 encerra sem essa ação.

#### Pré-requisito declarativo em T27

`EMITIR_MENSAGEM_DE_ENCAMINHAMENTO` tem como **pré-requisito** `ENTREGAR_RESUMO`. A ordem
de S2.9 permanece:

| # | Momento |
|---|---|
| 1 | `E12` = resumo **efetivamente gerado** (doc 06 §2.2) |
| 2 | a `MaquinaEstados` decide T27 |
| 3 | a decisão final é **persistida** (etapa 13) |
| 4 | **tentar entregar** o resumo (etapa 14) |
| 5 | **somente após o sucesso da entrega**, emitir a mensagem de encaminhamento |

A máquina apenas **declara** as duas ações. Ela **não** entrega, **não** envia, **não**
verifica sucesso, **não** reverte estado e **não** cria retentativa, fila, contador ou
status de entrega (doc 06 §10). A representação concreta futura desse pré-requisito pode
ser um **mapeamento estático do contrato** — não implementado nesta etapa.

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
| 3 | **Recuperar contexto persistido** | canal + contato + identificador do atendimento, quando houver + **instante de referência do ciclo** — o campo "data e hora" de §6.1 — + **limiar temporal de recência**, argumento explícito de configuração operacional (§6.2, N-a-L1–N-a-L6) | contexto recuperado (§6.2), com **duas projeções distintas** para a identidade: **(A)** o **conjunto elegível fechado** do contato, produzido pela política **N-a** — **arbitrada** em §6.2, nunca o histórico inteiro; e **(B)** **`ids_em_atendimento_humano`** — o conjunto **H**, os IDs dos atendimentos recuperados cujo estado é `atendimento_humano`. **(B) não passa por N-a**: nenhuma política de elegibilidade ou recência pode remover um atendimento humano de H (H2). Além disso: estado, dados, qualificação, pendências, motivos | atendimento indicado e **não recuperado** → erro operacional: bloquear, preservar, alertar. Estado corrompido → bloqueio (§7.1). **Marco temporal exigido ausente** ou **projeção incoerente do registro recuperado** → bloqueio de **integridade** por **E5/S7** (§7.1, **S9**, **S11**); **limiar ausente, de tipo inválido ou não positivo** → bloqueio por **erro de contrato da configuração** (§7.1, **S10**) — mesmo tratamento observável, atribuição normativa distinta. **Nunca criar atendimento novo por não encontrar o indicado** |
| 4 | Interpretar e extrair — **fronteira da etapa 4** (arbitragem N-b, §6.3) | mensagem normalizada | **`Interpretacao`**: as **oito** categorias de §6.3 preservadas, com **`IntencaoConversacional`** fechada em **11** códigos (partição A1/A2/B), confiança **binária** por item e `confianca_global` sempre presente. Derivadas **deterministicamente dentro da própria fronteira**: a **projeção estruturada** consumida pela etapa 5 (N-b-K1–N-b-K7) e a condição **`interesse_confirmar_disponibilidade`** de §4.4 (N-b-CD1–N-b-CD4). **A etapa 4 não emite `Exx`, `Txx`, `Rxx`, qualificação, violação, estado, pendência nem `motivo_encerramento`** (N-b-G2) | produtor indisponível → **nenhuma `Interpretacao`** e **nenhuma projeção**; a etapa 5 não executa e `interesse_confirmar_disponibilidade = None` (N-b-M1–N-b-M8, §7). **Erro de contrato** (E-Nb-1–E-Nb-19) **bloqueia na fronteira da etapa 4**, sem projeção e **nunca** convertido em `Identidade.AMBIGUA`. Confiança `BAIXA` **não é erro**: é **ausência para consumo estruturado**, com a **única exceção** de `pedido_de_humano` (N-b-PH3, N-b-PH4) |
| 5 | **Resolver identidade do atendimento** | conjunto elegível fechado (3) + **conjunto H — `ids_em_atendimento_humano`** (3) + projeção estruturada da interpretação (4) + veredito do identificador já validado (§6.1.1) + **`id_atendimento_validado`** (3) — o **ID técnico opaco** do atendimento identificado, **obrigatório** quando o veredito é `ENCONTRADO` e **`None`** quando é `NAO_INFORMADO` (§6.1.1, §6.2; pré-condições **P-I1–P-I5** de §7.1) + `havia_estado_esperado` (§6.2) | **primeiro** `situacao_takeover` (§6.3); se `SEM_TAKEOVER`, um de **seis** resultados conceituais: `ATENDIMENTO_ATIVO`, `MESMA_SOLICITACAO` (T36), `NOVA_SOLICITACAO` (T37), `AMBIGUA`, `PRIMEIRO_CONTATO_COMPROVADO` (identidade `None`) e `SEM_CANDIDATO_ELEGIVEL` (identidade `None`) — sempre com `criterio` do vocabulário fechado de §7.1 | ambíguo → **não decidir**: pedir esclarecimento, sem herdar nem sobrescrever dado algum (§7.1, A1–A7); persistir o processamento pendente quando possível. `SEM_CANDIDATO_ELEGIVEL` → **encerra sem transição**; tratamento pelo orquestrador **bloqueado pela pendência E4**. `situacao_takeover != SEM_TAKEOVER` → **D0–D6 não executam** e a identidade **não é calculada** (R5, abaixo) |
| 6 | Registrar dados e correções | campos extraídos + atendimento resolvido | dados atualizados + correções + **sinal de mutação efetiva de insumo da qualificação** (`insumo_qualificacao_atualizado`, doc 06 §4.1) | conflito entre mensagem e estado → §7; dado incerto nunca é gravado; identidade ambígua → nada é registrado no atendimento anterior |
| 7 | Executar a ordem determinística do doc 06 §4 — **primeira decisão determinística do ciclo** | dados + eventos + avaliação comercial feita **a montante** contra o YAML (`RegrasComerciais`, `Qualificador`) + **todas as condições estruturadas de §4.4** já determinadas — `insumo_qualificacao_atualizado`, classificação de `E09`, `resposta_aprovada_disponivel`, `interesse_confirmar_disponibilidade`, `calendario_integrado`, `identidade`, `motivos_handoff` e `motivo_encerramento`. A `MaquinaEstados` recebe tudo já estruturado e **não lê o YAML** (doc 06 I23) | eventos confirmados, violações, motivos, qualificação recalculada e o **estado intermediário** resultante da **primeira chamada da `MaquinaEstados`** — caminho percorrido (uma ou mais `Txx`, doc 06 §4.2), ainda sujeito ao fechamento da etapa 12 | `E07`, `E08`, `E09` e `E18` são **recebidos/confirmados a partir das saídas determinísticas a montante**, não fabricados aqui; violação da precedência (ex.: `E07` sobre incompatibilidade) é erro de programa, não caso de negócio → bloquear envio. **O produtor concreto de `E09` não é definido nesta arquitetura — S2-D8 permanece aberta** (doc 06 §11) |
| 8 | Consultar YAML e respostas aprovadas | perguntas detectadas | valores de campo e códigos `R` correspondentes | campo `null`/`pendente` e ausência de resposta aprovada **já foram confirmados como `E09` na etapa 7** (gatilhos 1–2 do doc 04, doc 06 §9): aqui a pendência é **consultada e registrada**, nunca criada tardiamente. Esta etapa **não produz condição consumida pela etapa 7** |
| 9 | Selecionar fatos permitidos — **conferindo cada `Rxx` comercial contra o YAML** (F3) | resultado de 7 e 8 | lista fechada de fatos, cada um com origem e conferência | divergência `Rxx` × YAML → o fato **não** entra na lista, registra-se erro de consistência da base e o dado divergente é bloqueado (F4); lista vazia com pergunta pendente → R03 + handoff. **Nenhum `E09` nasce nesta etapa** e **nenhuma condição de §4.4 é produzida aqui** |
| 10 | Gerar rascunho | fatos autorizados + tom + estado | texto candidato | LLM indisponível ou lento → usar o texto aprovado literal (§7) |
| 11 | Validar o rascunho | rascunho + fatos autorizados | aprovado ou bloqueado + motivo | qualquer valor, promessa ou termo fora da lista → bloqueio |
| 12 | Bloquear ou substituir — e **fechar o ciclo determinístico** | resultado de 11 | texto final seguro + fechamento com `E15` e `E12` **pós-efeito** | substituir pelo texto aprovado literal; se não houver, R03 + handoff. Nunca reenviar ao LLM mais de uma vez. `E15` e `E12` só são confirmados **depois do efeito real** (doc 06 §2.2) e reentram na `MaquinaEstados` na ordem `E15` → `E12` (doc 06 §4.2): **no máximo duas chamadas adicionais** — uma para `E15`, uma para `E12` |
| 13 | Persistir — **persistência operacional** (§7.3) | **estado final produzido pela última chamada determinística aplicável após o fechamento da etapa 12**: o resultado da **etapa 7** quando não houver `E15` nem `E12`; o resultado **pós-`E15`** quando só houver `E15`; o resultado **pós-`E12`** quando a cadeia completa existir | estado, dados, qualificação, pendências, motivos e chave de idempotência gravados — e o **`instante_ultima_transicao`** de §6.2 (N-a-T1–N-a-T8): gravado **sempre** com o **instante de referência do ciclo**, nunca com relógio vivo, e atualizado **somente** quando o caminho decidido no ciclo contém transição que **muda** o estado. **Materialização parcial**: o **transporte e a validação da representação** do campo já existem na persistência operacional, e a **decisão** de qual valor usar — com a **composição entre as 0–3 chamadas** do ciclo — também (notas de materialização em §6.2, M-T1–M-T6 e M-DT1–M-DT7); a **aplicação** dessa decisão e a **escrita** pelo contrato da persistência existem como **fronteira chamável** (M-AE1–M-AE7). Continua **NÃO integrada** **esta etapa** no pipeline — montagem completa do registro, decisão de se ela executa, escolha entre criar e gravar, geração de `id_atendimento`, idempotência e tratamento operacional de falha permanecem futuros — e **N-a-T3–N-a-T7 não estão operacionalmente concluídas** | falha de persistência → **bloquear a emissão** da resposta que depende da nova transição; preservar a mensagem para reprocessamento idempotente; alerta operacional (§7.2) |
| 14 | Emitir resposta ou handoff | texto final + decisão **já gravada** | resposta ao interessado e/ou resumo para Douglas | **ordem de emissão obrigatória: 1. tentar a entrega do resumo; 2. somente após sucesso, emitir a mensagem de encaminhamento ao interessado** (doc 06 §10). Estado `atendimento_humano` → nada é emitido (I03); handoff não registrado → não afirmar que houve handoff (§7.2). **`deve responder = false` sempre que `situacao_takeover != SEM_TAKEOVER`** (R5, §6.5) |

Regras do pipeline:

- **a etapa 3 antecede a 4, e as duas antecedem a 5**: identidade só é resolvida com contexto
  persistido e interpretação disponíveis;
- **fronteira temporal da etapa 7**: todas as condições de §4.4 — em especial
  `resposta_aprovada_disponivel` — precisam estar **determinadas antes** da etapa 7, porque
  é ali que ocorre a primeira chamada da `MaquinaEstados`. As etapas 8 e 9 **consultam,
  conferem e selecionam** fatos e textos, mas **não produzem condição necessária a uma
  chamada que já aconteceu**;
- as etapas 7 a 9 são a única origem de conteúdo comercial;
- a etapa 10 é a única que pode falhar por indisponibilidade externa sem parar o
  atendimento — todas as outras têm caminho determinístico;
- **a etapa 13 antecede a 14, sem exceção** — inclusive para resposta segura e para handoff
  (§7.2). Nunca responder um estado que não foi gravado;
- a etapa 11 roda mesmo quando o texto veio pronto de `respostas-aprovadas.md`;
- as etapas 3 e 5 podem terminar o ciclo sem produzir transição, em **quatro** situações:
  1. **contexto inválido** — a etapa 3 bloqueia (§7.1, S1–S8);
  2. **`Identidade.AMBIGUA`** — a etapa 5 termina sem transição e aplica **A1–A7**;
  3. **`SEM_CANDIDATO_ELEGIVEL`** — a etapa 5 termina sem transição enquanto a pendência
     **E4** estiver aberta. O que acontece depois **não é decidido aqui**;
  4. **`situacao_takeover == HUMANO_MULTIPLO`** — a etapa 5 termina sem transição: **sem
     alvo**, `identidade = None`, a **`MaquinaEstados` não é chamada**, processamento
     pendente preservado, **alerta operacional** e **zero emissão automática** (R5-P0).

  **`HUMANO_UNICO` não pertence a esta lista**: ele **não** encerra sem transição. O ciclo
  prossegue e a `MaquinaEstados` é chamada com `estado = atendimento_humano` e
  `CondicoesCiclo.identidade = None`; `E01` segue por **T33**, que mantém o estado e proíbe
  qualquer resposta automática;
- a etapa 4 pode rodar sobre contexto inválido **apenas para diagnóstico** — nesse caso
  nenhuma transição e nenhuma gravação comercial ocorrem (§7.1).

**Residual de eventos `Exx` na etapa 4** (arbitragem N-b, §6.3). A etapa 4 **não emite `Exx`**
(N-b-G2, N-b-RES1). A **transformação posterior** dos sinais interpretados em **eventos
confirmados** **ainda não possui produtor concreto**: é **residual explícito de integração**
(N-b-RES2). Ele **não** é componente, **não** é linha de pendência nova e **não** é atribuído
ao `OrquestradorMotor`, ao `DetectorHandoff` nem ao `Qualificador` (N-b-RES3). **Nenhum
identificador de pendência novo é criado.**

**Precedência de takeover na etapa 5** (arbitragem R5). **Antes** da restrição por
identificador e **antes de D0**, a etapa 5 determina `situacao_takeover` (§6.3). O resultado
governa se a cascata sequer executa:

| `situacao_takeover` | Etapa 5 | `id_atendimento_alvo` | `identidade` | Consequência |
|---|---|---|---|---|
| `SEM_TAKEOVER` | executa D0–D6 normalmente | conforme a cascata | conforme a cascata | fluxo normal da R3/R5 |
| `HUMANO_UNICO` | **D0–D6 não executam** | **id do único atendimento em `atendimento_humano`** | `None` — não calculada | evidência estruturada preservada para auditoria. A futura chamada da `MaquinaEstados` recebe `estado = atendimento_humano` e `CondicoesCiclo.identidade = None`; `E01` segue por **T33**; **zero resposta automática** |
| `HUMANO_MULTIPLO` | **D0–D6 não executam** | `None` | `None` — não calculada | **a `MaquinaEstados` não é chamada**; o ciclo termina na etapa 5 **sem transição**; processamento pendente preservado; **alerta operacional**; **zero resposta automática** |

| # | Regra |
|---|---|
| W1 | Em `HUMANO_MULTIPLO` o motor **não escolhe** entre os atendimentos e **não usa recência para desempatar**. Escolher seria inventar um referente que os sinais não determinam. |
| W2 | `HUMANO_UNICO` e `HUMANO_MULTIPLO` **não são resultados do enum `Identidade`** e não são critérios de `CriterioIdentidade`. São valores de `situacao_takeover`, dimensão ortogonal (§6.3, K1). |
| W3 | Em ambos, `identidade = None` significa **"identidade não calculada por curto-circuito de takeover"** — distinto de `PRIMEIRO_CONTATO_COMPROVADO` e de `SEM_CANDIDATO_ELEGIVEL`, que são conclusões da cascata (§6.4). |

**Tratamento dos resultados da etapa 5 quando `situacao_takeover == SEM_TAKEOVER`**
(arbitragem R3). Os seis resultados conceituais e o que cada um autoriza:

| Resultado | Identidade | Tratamento |
|---|---|---|
| `ATENDIMENTO_ATIVO` | resolvida | alvo obrigatório; o ciclo segue para a etapa 6 sobre o atendimento alvo |
| `MESMA_SOLICITACAO` (T36) | resolvida | alvo obrigatório, em estado `encerrado`; reabertura preservando os dados já registrados |
| `NOVA_SOLICITACAO` (T37) | resolvida | alvo `None`; novo atendimento **sem reutilizar dado comercial** do anterior (I15) |
| `AMBIGUA` | ambígua | **não transicionar**; pedir **esclarecimento objetivo**; **nada é herdado**; **A1–A7 continuam valendo integralmente** |
| `PRIMEIRO_CONTATO_COMPROVADO` | `None` | **resultado legítimo**, não falha: nenhum atendimento anterior é alvo; compatível **futuramente** com o fluxo `NOVO`/T01, que não é acionado por esta etapa |
| `SEM_CANDIDATO_ELEGIVEL` | `None` | há **histórico anterior conhecido** e **zero candidatos elegíveis**. **Não equivale a primeiro contato**; **não autoriza chamar a `MaquinaEstados` como `NOVO`**; o tratamento de integração está **bloqueado pela pendência E4** (§12; doc 06 §4.5, G1–G7) |

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
| N7 | **O identificador validado apenas restringe o escopo da resolução a um candidato** (arbitragem R3). Ele **não estabelece continuidade** e **não substitui os demais sinais** de §7.1: o candidato identificado ainda passa integralmente pelo teste **mesma × nova × ambígua** da cascata D0–D6, inclusive quando está **encerrado**. Coerente com **N2** (é referência para consulta) e **N4** (não prova por si só). A rastreabilidade dessa restrição é o campo `escopo_restrito_por_identificador` (§7.1) — **não existe critério `IDENTIFICADOR_VALIDADO`**. **Após a validação na etapa 3, o ID opaco é projetado para a etapa 5** como `id_atendimento_validado` (§6.2), e o atendimento identificado **deve estar no conjunto elegível** conforme **N-a-F1** (§6.2). Projetar o ID **não** o transforma em decisão: ele continua apenas **restringindo o escopo** em **D2**. |

Os vereditos `NAO_ENCONTRADO` e `INCOMPATIVEL` **não chegam** à etapa 5: continuam
bloqueados anteriormente na **etapa 3**, por **N5**, **N6** e **S3**.

**Obrigações do produtor — projeção do identificador validado** (arbitragem R-I). A etapa 3
é a **única produtora** de `id_atendimento_validado` (§6.2). Estas obrigações valem **na
fronteira da etapa 3**, antes de qualquer chamada do `ResolvedorIdentidade`:

| # | Obrigação da etapa 3 |
|---|---|
| N-I-1 | Se o identificador foi fornecido e validado como `ENCONTRADO`, a etapa 3 **projeta para a etapa 5** o `id_atendimento_validado` — o **ID técnico opaco** do atendimento identificado. |
| N-I-2 | Se `ENCONTRADO`, a etapa 3 **inclui o atendimento identificado no conjunto elegível exatamente uma vez** (**N-a-F1**, §6.2). |
| N-I-3 | Se `ENCONTRADO`, a etapa 3 produz **`havia_estado_esperado = true`**: existe atendimento anterior conhecido do contato, porque ele acabou de ser encontrado e validado. |
| N-I-4 | Se a etapa 3 **não conseguir** produzir projeção coerente com N-I-1, N-I-2 ou N-I-3, ela **bloqueia na etapa 3**: mensagem **preservada** e **alerta operacional** conforme o contrato vigente (S4, S5). **Não** chamar o `ResolvedorIdentidade` com entrada incoerente; **não** ignorar silenciosamente o identificador; **não** criar atendimento novo (N6, S3). |

A verificação espelhada, já na entrada da etapa 5, são as pré-condições **P-I1–P-I5**
(§7.1). **N-I** é obrigação do **produtor**; **P-I** é pré-condição do **consumidor**.

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
| **`id_atendimento_validado`** | `str \| None` — **ID técnico opaco** do atendimento identificado, projetado para a etapa 5 quando o veredito de §6.1.1 é `ENCONTRADO`; **`None`** quando é `NAO_INFORMADO` (arbitragem R-I, N-I-1). Projeção **separada** do veredito, do **conjunto elegível** e de **H**. Não contém **PII, texto, dado comercial, data nem recência** |
| atendimentos do contato | **conjunto elegível fechado**: os atendimentos ativos ou recentes do mesmo contato **necessários à resolução de identidade** — não o histórico inteiro. O conjunto é **produzido pela etapa 3** e entregue pronto ao `ResolvedorIdentidade` |
| estado da conversa | um dos oito valores do doc 06 §1.1, por atendimento recuperado |
| dados já coletados | tipo, data, convidados, formato, nome, contato |
| `resultado_qualificacao` | valor atual de cada atendimento recuperado |
| `pendencias_resposta` | perguntas em aberto |
| motivos registrados | incompatibilidade e handoff já detectados |
| **havia estado esperado?** | conclusão **interna** da resolução: **existe atendimento anterior conhecido do contato**, *independentemente de algum deles integrar o conjunto elegível deste ciclo*. Distingue primeiro contato comprovado de estado ausente por falha (§7.1, S6) e, agora, também de `SEM_CANDIDATO_ELEGIVEL` |
| **ids em `atendimento_humano`** (conjunto **H**) | `ids_em_atendimento_humano: tuple[str, ...]` — **um ID opaco por atendimento recuperado do contato/canal cujo estado é `atendimento_humano`**. Projeção **separada** do conjunto elegível e **fora** de N-a. Ordem irrelevante. Regras H1–H6 abaixo |
| integridade | contexto íntegro, ausente ou corrompido. Ausente ou corrompido quando havia estado esperado → bloqueio (E5) |

**Fronteira do conjunto elegível** (arbitragem R3). O `ResolvedorIdentidade` **recebe o
conjunto pronto**: não calcula elegibilidade, **não calcula recência** e **não recebe o
histórico inteiro**. Passar o histórico completo como substituto da falta de política de
recência é **violação de contrato**, não simplificação — transforma em candidatos avaliados
atendimentos que a política excluiria, alterando o resultado da cascata D0–D6.

Disso decorrem combinações **válidas e distintas**:

| Combinação | Significado |
|---|---|
| `havia estado esperado?` = **sim** + **zero** candidatos elegíveis | estado válido → `SEM_CANDIDATO_ELEGIVEL`. **Não é** contexto ausente nem corrompido |
| `havia estado esperado?` = **não** + **zero** candidatos elegíveis | `PRIMEIRO_CONTATO_COMPROVADO` |
| contexto **ausente** ou **corrompido** havendo estado esperado | **bloqueio na etapa 3** por **E5/S7** — a etapa 5 nem chega a ser executada |

**N-a — política arbitrada e materializada.** A **política de elegibilidade e de recência**
que produz esse conjunto está **arbitrada documentalmente** na subseção **N-a**, adiante, e
sua **produção determinística de E** já possui **implementação pura** — ver a **nota de
materialização** ao final da subseção. Ela é executada **dentro da etapa 3**, antes da
etapa 5: o conjunto elegível continua sendo um contrato de entrada exigido do resolvedor,
**nunca um cálculo dele**.

**N-a-F1 — fronteira parcial de N-a** (arbitragem R-I). Quando
`veredito_identificador == ENCONTRADO`, o conjunto elegível produzido pela etapa 3 **deve
conter o atendimento identificado exatamente uma vez**. **Nenhuma regra de elegibilidade ou
de recência pode removê-lo naquele ciclo**: um atendimento que a própria etapa 3 acabou de
encontrar e validar não pode desaparecer do escopo que ela entrega. A obrigação do produtor
é **N-I-2** (§6.1.1); a verificação correspondente na entrada da etapa 5 é **P-I5** (§7.1).
Coerentemente, `ENCONTRADO` implica **`havia_estado_esperado = true`** (**N-I-3**, **P-I4**)
— **sem implicação inversa**: `havia_estado_esperado = true` **não** implica `ENCONTRADO`.

**N-a-F1 permanece intacta e prevalece sobre N-a.** O que estava aberto à época de R-I — a
elegibilidade dos **demais** candidatos, a definição de recência, o marco temporal, o limiar,
a composição do conjunto e a ordem de entrega — está **fechado pela arbitragem N-a**
(subseção seguinte). Continuam **abertos**: o **valor numérico** do limiar, a **consulta
concreta** à persistência, a **unicidade geral** de `id_atendimento` entre candidatos não
identificados e **E4** (§12).

#### N-a — política de produção do conjunto elegível da etapa 3 (arbitragem N-a)

**Natureza.** N-a é a **política determinística** que transforma os registros **já
recuperados** da persistência no **conjunto elegível E** entregue ao `ResolvedorIdentidade`.
É **contrato conceitual, não implementação**: nenhum arquivo de `src/` é criado ou alterado
por esta arbitragem — em particular `persistence.py` permanece **intocado** — e **nenhum
marco funcional novo é criado**.

| # | Fronteira de N-a |
|---|---|
| N-a-1 | A etapa 3 continua **coordenada pelo `OrquestradorMotor`** (D1). N-a é política **dentro** da etapa 3, **não é componente**. |
| N-a-2 | **Nenhum componente novo é criado.** A tabela de §4.1 permanece com **14 componentes** e a de §2 com **nove responsabilidades**. |
| N-a-3 | A **persistência operacional continua sendo a única fonte autoritativa do estado** (E1, D9). |
| N-a-4 | A consulta por contato devolve **contexto bruto** — os registros do par canal + contato, **sem** política de "recente", "ativo" ou "candidato". Ela **não devolve conjunto elegível**. |
| N-a-5 | N-a **não recupera, não persiste, não interpreta texto, não lê YAML, não usa LLM, não consulta relógio vivo e não resolve identidade.** |
| N-a-6 | O `ResolvedorIdentidade` **continua recebendo E pronto** e continua **não calculando elegibilidade nem recência** (§7.1). |

**Classificação dos oito estados** (doc 06 §1.1). A classificação é **fechada** e cobre os
**oito** estados, sem exceção:

| Estado | Grupo | Elegível por N-a? | Consulta recência? |
|---|---|---|---|
| `novo` | I | **sim** | **não** |
| `coletando_dados` | I | **sim** | **não** |
| `respondendo_duvidas` | I | **sim** | **não** |
| `aguardando_confirmacao_disponibilidade` | I | **sim** | **não** |
| `pronto_para_handoff` | I | **sim** | **não** |
| `encaminhado_humano` | I | **sim** | **não** |
| `atendimento_humano` | II | **não** por N-a — salvo **N-a-F1** | **não** |
| `encerrado` | III | **sim, se recente** | **sim** |

| # | Regra de classificação |
|---|---|
| N-a-E1 | **Grupo I — elegível independentemente de recência.** Para esses seis estados o **marco temporal não é consultado**: um atendimento que não está encerrado e não está sob controle humano é candidato legítimo a referente, por mais antigo que seja seu último registro. |
| N-a-E2 | **Grupo II — `atendimento_humano` fica fora de E por N-a.** Canal sob controle humano é tratado por **H**, que é fato de estado, não por elegibilidade. |
| N-a-E3 | **Exceção já vigente: N-a-F1 prevalece.** Se o atendimento em `atendimento_humano` for o **atendimento identificado** com `veredito_identificador == ENCONTRADO`, ele **integra E exatamente uma vez**. |
| N-a-E4 | **H continua independente de N-a** (H1–H6 **intactas**). Nada em N-a remove, acrescenta ou reordena H. |
| N-a-E5 | **Grupo III — somente `encerrado` consulta recência.** É o **único** estado cuja elegibilidade é condicionada ao marco temporal. |

**Recência — aplicável exclusivamente a `encerrado`.**

| # | Regra de recência |
|---|---|
| N-a-R1 | O **único marco temporal normativo do MVP** é o **`instante_ultima_transicao`**: o momento da **última transição de estado efetivamente persistida** do atendimento. Para um atendimento `encerrado`, corresponde ao **último encerramento efetivamente persistido**. |
| N-a-R2 | O instante de comparação é o **`instante_de_referencia_do_ciclo`** — o campo **"data e hora"** do contrato comum de entrada (§6.1). |
| N-a-R3 | **Nunca consultar relógio vivo** nesta política — nem na comparação, nem na gravação (N-a-T2). |
| N-a-R4 | Regra: o candidato `encerrado` é elegível quando `instante_ultima_transicao >= instante_de_referencia_do_ciclo - limiar`. |
| N-a-R5 | A borda é **inclusiva**: exatamente sobre o limiar **entra**. |
| N-a-R6 | **Nenhuma duração numérica é definida aqui** (§12). |

**Limiar temporal.** É **configuração operacional do motor**, jamais dado comercial:

| # | Regra do limiar |
|---|---|
| N-a-L1 | É uma **duração** e chega à política como **argumento explícito**. |
| N-a-L2 | **Não é dado comercial**: não pertence a `knowledge/casa77.yaml`, não é lido do YAML e **não vem do canal** (E2, E3). |
| N-a-L3 | **Não pode existir como constante literal oculta** no motor e **não possui default silencioso**. |
| N-a-L4 | Deve ser **validado explicitamente**. **Ausência, tipo inválido ou valor não positivo** são **erro de contrato → bloqueio** (§7.1, S10). |
| N-a-L5 | A validação ocorre **sempre**, **inclusive quando o ciclo não possui candidato `encerrado`**. Configuração inválida não fica latente esperando o primeiro encerrado aparecer. |
| N-a-L6 | **Nenhum mecanismo concreto de carga é escolhido**: nem variável de ambiente, nem arquivo, nem framework, nem serviço. O **valor concreto permanece pendente de aprovação específica** (§12). |

**Contrato do dado temporal.** O `RegistroAtendimento` da persistência operacional **já
transporta** o marco — ver a **nota de materialização** após N-a-T8. As regras abaixo
definem **o valor** e **o momento** da escrita. Delas, a **decisão pura** — *qual valor
usar neste ciclo* — já possui materialização (**M-DT1–M-DT7**), e a **aplicação** dessa
decisão sobre um `RegistroAtendimento` com a **escrita** pelo contrato da persistência
existem como **fronteira chamável** (**M-AE1–M-AE7**). A **integração operacional no
pipeline** — inclusive **decidir se a etapa 13 executa** e **escolher entre criar e
gravar** — **permanece pendente** e pertence ao chamador da etapa 13. `src/casa77_sdr/persistence.py`
**não foi alterado pela arbitragem N-a**: a materialização veio depois, em entrega
funcional própria.

| # | Regra do `instante_ultima_transicao` |
|---|---|
| N-a-T1 | Nome conceitual do campo: **`instante_ultima_transicao`**. |
| N-a-T2 | O valor gravado é **sempre o `instante_de_referencia_do_ciclo`** — a data/hora que **já pertence à entrada** (§6.1). **Nunca `now()`, nunca relógio vivo.** |
| N-a-T3 | **Criação**: ao criar o atendimento, `instante_ultima_transicao = instante_de_referencia_do_ciclo`. |
| N-a-T4 | **Atendimento existente**: se o **caminho efetivamente decidido no ciclo** contiver **uma ou mais transições que mudem o estado**, atualizar `instante_ultima_transicao = instante_de_referencia_do_ciclo`. |
| N-a-T5 | O teste é pelo **caminho de transições** (doc 06 §4.2), **não** pela comparação `estado_inicial != estado_final`. Portanto `encerrado` → reabertura → `encerrado` **no mesmo ciclo ATUALIZA** o marco. |
| N-a-T6 | **Ciclo sem mudança de estado não atualiza** o marco. Inclui: **duplicata idempotente**; **`AMBIGUA`** decidida antes da máquina; **`HUMANO_MULTIPLO`**; **takeover silencioso / T33** que preserva o estado; **`SEM_CANDIDATO_ELEGIVEL`**; **bloqueio**; e **qualquer transição que preserve o estado**. |
| N-a-T7 | **Múltiplas mudanças no mesmo ciclo**: um **único** instante basta — o `instante_de_referencia_do_ciclo`. Não se registra um marco por transição. |
| N-a-T8 | **Representação**: instante **com fuso**, comparável como **instante absoluto**. Nenhum tipo Python, coluna, índice ou serialização é escolhido aqui; a persistência concreta permanece futura. |

**Projeção de mudança de estado — contrato arbitrado e materialização em runtime.** As regras
**N-a-T4** e **N-a-T5** exigem saber **se o caminho decidido no ciclo mudou o estado**, e
proíbem derivar isso de `estado_inicial != estado_final`. Esta subseção **arbitra a
origem dessa informação**. **A projeção foi materializada na `MaquinaEstados`**: o campo
`transicoes_que_mudaram_estado` **existe em runtime**, é produzido **dentro** da máquina no
instante da aplicação de cada `Txx` e é devolvido por `DecisaoMaquina`. **Toda a semântica
normativa das regras 1–8 abaixo permanece exatamente como arbitrada** — nenhuma foi
alterada pela materialização.

O que **esta** materialização, isoladamente, **não** faz: ela entrega **apenas a
projeção** dentro da `MaquinaEstados`. A **composição entre as até três chamadas** do ciclo
(regra 7) e a **decisão** de qual valor de `instante_ultima_transicao` usar foram
materializadas **depois**, em entrega própria — ver **M-DT1–M-DT7** —, e a **aplicação**
com a **escrita** do marco vieram depois ainda, como **fronteira chamável**
(**M-AE1–M-AE7**). Continua **NÃO integrada** a **etapa 13** no pipeline, e o
**`OrquestradorMotor` continua NÃO implementado**.

| # | Regra da projeção `transicoes_que_mudaram_estado` |
|---|---|
| 1 | A saída conceitual da `MaquinaEstados` passa a incluir **`transicoes_que_mudaram_estado`**, de forma **`tuple[Transicao, ...]`**. Tupla **vazia** significa que **nenhuma** transição daquela chamada mudou estado. |
| 2 | **Semântica**: é a **subsequência ordenada de `caminho`** que contém exatamente as `Txx` cujo **destino diferiu do estado intermediário vigente no instante da aplicação** (doc 06 §4.2). A **pertença** é o fato auditável de "mudou estado"; a **ausência** significa que aquela `Txx` preservou o estado. |
| 3 | **Fonte autoritativa é a própria `MaquinaEstados`.** A informação **nasce dentro dela**, no mesmo ponto lógico em que a transição é aplicada. **Não** é reconstruída pelo consumidor, **não** vem de `estado_inicial != estado_final`, **não** vem de *replay* externo do caminho, **não** cria tabela paralela de origem/destino, **não** exige função pública de *replay* e **não** exige que consumidor algum conheça a estrutura interna de regras da máquina, que permanece **privada**. |
| 4 | **Classificação dinâmica, nunca estática.** **T33** aplicada em `atendimento_humano` preserva o estado e fica fora. **T35** tem origem declarada **aberta** e destino `encerrado`: **muda** o estado quando o intermediário corrente é outro e **preserva** quando esse estado já é `encerrado`. **Nenhuma regra estática do tipo "T35 sempre muda estado" é criada.** |
| 5 | **Nenhuma lista normativa paralela** das `Txx` que preservam estado é criada. A **tabela do doc 06 §3 continua sendo a fonte única** de origem, destino e condição. |
| 6 | **Caminho com múltiplas `Txx`**: cada uma é classificada contra o **estado intermediário imediatamente anterior à sua própria aplicação**. A subsequência preserva a ordem de `caminho` e pode ter **zero, uma ou várias** entradas. |
| 7 | **Composição das até três chamadas** por ciclo (doc 06 §4.2, *Limite de chamadas*): **cada chamada produz sua própria projeção**. Houve mudança **no ciclo** se, e somente se, **ao menos uma das `DecisaoMaquina` efetivamente produzidas** tiver `transicoes_que_mudaram_estado` **não vazia**. É **proibido** concatenar caminhos e fazer *replay*, comparar apenas o estado inicial da primeira chamada com o estado final da última, ou **presumir que sempre existem três chamadas**. |
| 8 | **Estado inicial igual ao final não implica ausência de mudança.** Um ciclo `encerrado` → reabertura → `encerrado` contém mudança real — é o fundamento de **N-a-T5** e o cenário **K-Na-17**. |

**Fronteira entre criação, atualização e persistência.** Os três são distintos e **nenhum
deles é implementado aqui**:

| # | Fronteira |
|---|---|
| 1 | **Criação de atendimento** — vale **N-a-T3**: `instante_ultima_transicao = instante_de_referencia_do_ciclo`. **Não existe transição anterior a detectar**, e a projeção da `MaquinaEstados` **não é pré-requisito** para inicializar o marco na criação. **Quem cria o atendimento não é atribuído por esta arbitragem.** |
| 2 | **Atualização de atendimento existente** — vale **N-a-T4/N-a-T5**, pela **regra 7** da tabela acima: se **ao menos uma** das decisões realmente produzidas no ciclo tiver a projeção **não vazia**, atualizar o marco com o `instante_de_referencia_do_ciclo`; se **todas** forem vazias, **preservar** o marco anterior. Uso **futuro** da **etapa 13** (§5). |
| 3 | **Transporte e persistência do marco** — continuam sendo o contrato já materializado em **M-T1–M-T6**. A persistência **não decide** quando o marco muda e **não consulta** esta projeção; quem decide e aplica é a fronteira de **M-DT1–M-DT7** e **M-AE1–M-AE7**, **sem alterar** `persistence.py`. |
| 4 | **N-a-T6** e **N-a-T7 permanecem íntegros**: ciclo sem mudança **não atualiza**; ciclo encerrado antes da `MaquinaEstados` **não atualiza por essa via**; e **múltiplas mudanças no mesmo ciclo continuam usando um único `instante_de_referencia_do_ciclo`**. A **cardinalidade da tupla não significa um timestamp por transição**. |

**Nota de materialização — posterior à arbitragem N-a.** As escolhas abaixo são **decisões
técnicas da implementação**, tomadas **depois** do PR #31 e **não** originárias da
arbitragem: **N-a-T8 permanece historicamente verdadeiro** — a arbitragem **não escolheu**
tipo Python, coluna, índice nem serialização.

| # | Materialização atual |
|---|---|
| M-T1 | `RegistroAtendimento` transporta `instante_ultima_transicao` com representação concreta **`datetime \| None`**, default **`None`**. |
| M-T2 | **`None` é válido no armazenamento.** A persistência não exige o marco; a exigência, quando um candidato `encerrado` precisa de recência, continua sendo **bloqueio da etapa 3** por **S9** — a validação estrutural da persistência **não substitui** a validação de integridade da etapa 3. |
| M-T3 | Valor **não-`None`** exige **fuso efetivo** — `tzinfo` presente **e** `utcoffset()` não `None` —, que é o que torna o marco comparável como instante absoluto (N-a-T8). Violação é **erro de contrato do chamador** na fronteira de escrita. |
| M-T4 | A persistência **transporta** o valor recebido: **não converte fuso**, não normaliza para UTC e não altera o instante. |
| M-T5 | **Zero relógio vivo** e **zero preenchimento automático**: a persistência não cria o marco e **não decide** quando ele muda — essa fronteira permanece intacta. A **decisão** de qual valor usar e a **aplicação/escrita** foram materializadas **fora** da persistência (M-DT1–M-DT7, M-AE1–M-AE7), que **não é alterada por elas**; a **integração operacional no pipeline** permanece pendente e pertence ao chamador da etapa 13. |
| M-T6 | **Nenhuma coluna, índice, serialização ou persistência não volátil foi escolhida.** A implementação continua sendo a em memória de §7.4 (B2, M1–M3). |

**Nota de materialização da política N-a/E — posterior à arbitragem.** A **produção
determinística do conjunto elegível** deixou de ser apenas contrato: existe hoje como
**função pura** em `src/casa77_sdr/eligibility.py`. Como M-T1–M-T6, estas são **decisões
de implementação tomadas depois** do PR #31, **não** decisões originárias da arbitragem;
**nenhuma regra normativa de N-a foi alterada**.

| # | Materialização de N-a/E |
|---|---|
| M-E1 | **Não é componente arquitetural novo.** A tabela de §4.1 permanece com **14** componentes e a de §2 com **nove** responsabilidades (N-a-1, N-a-2). O módulo é **organização de código** para uma política **interna da etapa 3**. |
| M-E2 | A função recebe os **registros já recuperados** e devolve **somente E** — `tuple[CandidatoAtendimento, ...]`. Ela **não recupera, não persiste** e **não faz I/O** (N-a-4, N-a-5). |
| M-E3 | Materializa: validação do limiar (N-a-L1–L6), projeção (N-a-P1–P6), classificação dos oito estados (N-a-E1–E5), recência exclusiva de `encerrado` (N-a-R1–R6), **N-a-F1**, preservação de duplicatas não identificadas (N-a-D2) e ordem canônica (N-a-O1–O5). |
| M-E4 | **Zero relógio vivo**, zero YAML, zero LLM, zero rede e zero conversão de fuso. Dadas as mesmas entradas, produz sempre a mesma tupla, e **não muta** os registros recebidos. |
| M-E5 | As violações são **sinalizadas por exceção** — configuração temporal inválida (S10), marco temporal ausente (S9), contexto corrompido (S11) e identificado incoerente (N-I-2/P-I5). **O tratamento operacional do bloqueio não é implementado**: preservar a mensagem e emitir alerta (S4, S5) continuam sendo do `OrquestradorMotor`. |
| M-E6 | **Permanecem fora** *desta política*: a **decisão**, a **aplicação** e a **escrita** do marco de **N-a-T3–N-a-T7** — materializadas **fora** daqui (M-DT1–M-DT7, M-AE1–M-AE7). Permanecem também fora desta política o **valor numérico do limiar**, o **mecanismo de carga** da configuração e o **`OrquestradorMotor`**. O **conjunto H**, `havia_estado_esperado`, a projeção **N-I** e a **montagem das projeções de identidade da etapa 3** foram materializados **depois**, em entrega funcional própria — ver **M-C1–M-C8** adiante. |

**Nota de materialização da montagem das projeções de identidade da etapa 3 — posterior às
anteriores.** A **produção das projeções que a etapa 3 entrega à etapa 5** deixou de ser
apenas contrato: existe hoje em `src/casa77_sdr/context.py`. **Isto não é a etapa 3 inteira
materializada**: o que existe é o *wiring* da **fronteira etapa 3 → identidade/etapa 5**. Como M-T1–M-T6 e M-E1–M-E6, estas são **decisões de
implementação tomadas depois** do PR #31, **não** decisões originárias da arbitragem;
**nenhuma regra normativa de §6.1.1, §6.2, N-a, H1–H6, N-I ou P-I foi alterada**.

| # | Materialização da montagem das projeções de identidade da etapa 3 |
|---|---|
| M-C1 | **Não é componente arquitetural novo.** A tabela de §4.1 permanece com **14** componentes e a de §2 com **nove** responsabilidades (N-a-1, N-a-2). O módulo é o ***wiring* da fronteira etapa 3 → identidade/etapa 5** — **não** a etapa 3 inteira —, que continua **coordenada pelo `OrquestradorMotor`** (D1). |
| M-C2 | A montagem usa a **persistência operacional somente para leitura** — `recuperar_por_id` e `consultar_por_contato`. Ela **não cria**, **não grava**, **não marca chave de idempotência** e **não preserva pendente** (N6, S3). |
| M-C3 | Executa a **precedência conceitual dos 14 passos** desta seção **no que toca a essa fronteira**. Em particular: o **limiar é validado antes de qualquer método da persistência** (N-a-L4, N-a-L5, S10); a ordem é **recuperar por ID → consultar contato → validar o identificador** — o bloqueio de **N5** **não** é antecipado para antes da consulta do contato; e o **passo 12 precede o passo 13** — as correspondências são verificadas sobre **E ainda não canonicalizado**, e a ordem canônica é aplicada **só depois**. |
| M-C4 | **E continua delegado** à política N-a de `eligibility.py` (M-E1–M-E6): classificação, recência, **N-a-F1** e ordem canônica **não são reimplementadas**. A política expõe a **seleção de E** (passos 9/10) e a **canonicalização** (passo 13) como operações distintas e reutilizáveis, além da validação do limiar e da projeção integral dos registros; a API que produz E já canonicalizado permanece como conveniência equivalente à composição das duas. Cada regra continua existindo em **um único lugar**. |
| M-C5 | **H permanece fora de N-a** (H1, H2): é construído por **filtro estrutural de estado** sobre a projeção **integral** do contexto recuperado, **antes e à parte** da filtragem N-a, e transporta **somente IDs opacos** (H3). |
| M-C6 | **`havia_estado_esperado` e a projeção `id_atendimento_validado` (N-I-1) agora possuem produtor em código.** `havia_estado_esperado` é calculado sobre o **contexto recuperado**, **nunca sobre E**; o ID validado é projetado **somente** sob `ENCONTRADO`, e é `None` sob `NAO_INFORMADO`. As correspondências **H4/H5** e **N-I-1–N-I-3** são verificadas no **passo 12**, antes da entrega. |
| M-C7 | As violações são **sinalizadas por exceção**: identificador não resolvido (**N5**, **N6**, **S3** — transporta **apenas o veredito fechado**, sem identificador, canal, contato, mensagem ou PII), conjunto **H** incoerente (**H4**, **H5**) e projeção do identificador incoerente (**N-I-4**). **O tratamento operacional do bloqueio não é implementado**: preservar a mensagem e emitir alerta (S4, S5) continuam sendo do `OrquestradorMotor`. |
| M-C8 | **Permanecem fora** *desta montagem*: a **decisão**, a **aplicação** e a **escrita** do marco de **N-a-T3–N-a-T7** — materializadas **fora** daqui (M-DT1–M-DT7, M-AE1–M-AE7). Permanecem também fora desta montagem **N-b**, **E4**, **S2-D8**, **S3-D1**, o **tratamento operacional dos bloqueios** (S4, S5), o **destino do alerta operacional**, o **valor numérico do limiar**, o **mecanismo concreto de carga** da configuração, a **persistência não volátil** e o **`OrquestradorMotor`**. A montagem **não chama** o `ResolvedorIdentidade`, **não chama** a `MaquinaEstados`, **não qualifica**, **não interpreta mensagem** e **não decide resposta**: **a etapa 3 não está inteiramente materializada** e a **integração completa do pipeline continua não iniciada**. |

**Nota de materialização da decisão do marco temporal — posterior às anteriores.** A
**decisão determinística** exigida por **N-a-T3–N-a-T7** — *qual valor de
`instante_ultima_transicao` usar neste ciclo* — deixou de ser apenas contrato: existe hoje
como **função pura** em `src/casa77_sdr/transition_marker.py`. Como M-T1–M-T6, M-E1–M-E6 e
M-C1–M-C8, estas são **decisões de implementação**, **não** regras novas: **nenhuma regra
normativa de N-a-T1–N-a-T8 foi alterada**.

**A distinção é normativa e não pode ser colapsada:** o que existe é a **DECISÃO**; a
**APLICAÇÃO** e a **escrita** foram materializadas **depois**, como fronteira chamável
(**M-AE1–M-AE7**); o que **continua pendente** é a **integração operacional no pipeline**
pelo chamador da etapa 13.

| # | Materialização da decisão do marco |
|---|---|
| M-DT1 | **Não é componente arquitetural novo.** A tabela de §4.1 permanece com **14** componentes e a de §2 com **nove** responsabilidades. O módulo é organização de código para uma **decisão pura**. |
| M-DT2 | A função recebe **quatro argumentos nomeados e obrigatórios** — se o ciclo cria atendimento, o `instante_de_referencia_do_ciclo`, o marco atual e as decisões efetivamente produzidas — e devolve **somente** `datetime \| None`. **Não recebe persistência**, não monta `RegistroAtendimento` e **não decide se a etapa 13 executa**. |
| M-DT3 | Materializa a decisão de **N-a-T3** (criação → instante do ciclo, **sem** exigir a projeção da máquina), de **N-a-T4/N-a-T5/N-a-T7** (atendimento existente com **ao menos uma** decisão de projeção não vazia → instante do ciclo, **inclusive** quando o estado final iguala o inicial) e de **N-a-T6** (nenhuma mudança → **preserva** o marco atual, inclusive `None`). |
| M-DT4 | **Composição das até três chamadas** conforme a regra 7: a decisão observa **exclusivamente** `transicoes_que_mudaram_estado` de cada `DecisaoMaquina`. **Zero** *replay*, **zero** concatenação de caminhos, **zero** acesso à estrutura interna de regras da máquina, **zero** comparação entre estado inicial e final e **zero** classificação estática de T35. Nenhum outro campo de `DecisaoMaquina` é lido. Mais de três decisões é erro de contrato. |
| M-DT5 | **Zero relógio vivo** e **zero aritmética temporal**: o valor devolvido é sempre **o mesmo objeto** recebido — o instante do ciclo ou o marco atual —, sem conversão de fuso, `astimezone` ou substituição de `tzinfo` (N-a-T2). A validação de **fuso efetivo** **não é duplicada**: continua nas fronteiras já existentes (`recebida_em` na normalização e M-T3 na persistência). |
| M-DT6 | **Zero persistência, zero I/O, zero rede, zero YAML e zero LLM.** O módulo **não importa** `persistence`, `context`, `eligibility` nem `identity`, e **não é exportado** na superfície pública do pacote. |
| M-DT7 | **Este módulo decide, não aplica nem escreve**: a **aplicação** sobre o `RegistroAtendimento` e a **escrita** via `criar`/`gravar` foram materializadas **depois**, fora daqui, como fronteira chamável (**M-AE1–M-AE7**). **Permanecem NÃO integradas**: a **decisão de se a etapa 13 executa**, a **criação operacional** do atendimento, a **integração do pipeline** e o **`OrquestradorMotor`**. **Nenhuma persistência não volátil foi criada.** Portanto **N-a-T3–N-a-T7 NÃO estão operacionalmente concluídas**. |

**Nota de materialização da aplicação e escrita do marco — posterior às anteriores.** A
**aplicação** da decisão sobre um `RegistroAtendimento` e a **escrita** pelo contrato
existente da persistência deixaram de ser apenas contrato: existem hoje como **fronteira
chamável** em `src/casa77_sdr/transition_marker_write.py`. Como as notas anteriores, são
**decisões de implementação**, **não** regras novas: **nenhuma regra normativa de
N-a-T1–N-a-T8, nem as regras 1–8 da projeção, foi alterada**.

**A mecânica de decisão, aplicação e escrita do marco está materializada como fronteira
chamável, mas sua integração operacional no pipeline permanece pendente.**

| # | Materialização da aplicação e escrita |
|---|---|
| M-AE1 | **Não é componente arquitetural novo.** A tabela de §4.1 permanece com **14** componentes e a de §2 com **nove** responsabilidades. O módulo é organização de código para uma fronteira mínima. |
| M-AE2 | Existem **duas funções explícitas** — uma que **cria** e outra que **grava**. A distinção **criar × gravar** é **recebida pronta** pela função escolhida: a fronteira **não deriva** a operação de nada, e **não decide** qual delas o pipeline deve usar. |
| M-AE3 | A decisão do marco é **integralmente delegada** a `decidir_instante_ultima_transicao(...)` (M-DT1–M-DT7). O módulo **não lê** `transicoes_que_mudaram_estado`, **não lê** `caminho` nem qualquer outro campo de `DecisaoMaquina`, **não compara** estado inicial com final e **não faz *replay***. A regra de decisão **não é duplicada**. |
| M-AE4 | Recebe o `RegistroAtendimento` **pronto** e altera **exclusivamente** `instante_ultima_transicao`, por `dataclasses.replace`. **Não monta** estado, dados, qualificação, pendências, motivos nem identificador, **não muta** o registro recebido e devolve **exatamente** o registro submetido à persistência. |
| M-AE5 | Escreve pelo **contrato existente** `PersistenciaOperacional.criar`/`gravar`. **`persistence.py` permanece inalterado** e continua sendo a única fronteira que valida a representação do marco (M-T3). |
| M-AE6 | **Exceções propagam intactas** — `FalhaDePersistencia`, `ValueError` de identificador já existente ou inexistente, de vínculo canal × contato divergente e de marco sem fuso efetivo, além dos erros da própria decisão. **Zero `try`/`except`**: preservar a mensagem, emitir alerta e decidir o que o motor faz com a falha (S4, S5, Q2/Q4/Q5/Q8) e o **destino do alerta** permanecem **fora**. |
| M-AE7 | **Permanecem NÃO implementados/integrados**: a **montagem completa** do registro; a **decisão de se a etapa 13 executa**; a **escolha entre criar e gravar** no pipeline; a **geração de `id_atendimento`**; a **criação operacional** do atendimento; a **marcação de idempotência**; a **preservação de pendente**; o **tratamento operacional de falha**; o **`OrquestradorMotor`**; e o **pipeline completo**. A **etapa 13 continua não integrada**. |

**Marco temporal ausente.** Se um candidato `encerrado` precisar de recência e o
`instante_ultima_transicao` estiver **ausente**, isso é **erro de integridade do contexto da
etapa 3**: **bloquear**, **preservar a mensagem**, **gerar alerta operacional** e **não
chamar o `ResolvedorIdentidade`** — fundamento **E5 / S7** e o contrato geral de integridade
(§7.1, **S9**). **Não** é classificado como **N-I-4**: N-I-4 permanece **específico à
projeção coerente do identificador validado** (§6.1.1).

**Projeção do registro recuperado em `CandidatoAtendimento`.** Exatamente quatro campos:

| Campo do candidato | Origem no registro recuperado |
|---|---|
| `id_atendimento` | `RegistroAtendimento.id_atendimento` |
| `estado` | `RegistroAtendimento.estado_conversa`, convertido para `Estado` |
| `tipo_evento_registrado` | `dados_coletados["tipo_evento"]` |
| `data_nomeada_registrada` | `dados_coletados["data_nomeada"]` |

| # | Regra de projeção |
|---|---|
| N-a-P1 | `estado_conversa` **`None`** ou **fora dos oito valores** do doc 06 §1.1 → **contexto corrompido → bloqueio** (E5/S7). |
| N-a-P2 | `tipo_evento` **ausente** da chave ou `None` → `tipo_evento_registrado = None`. |
| N-a-P3 | `data_nomeada` **ausente** da chave ou `None` → `data_nomeada_registrada = None`. |
| N-a-P4 | Valor **presente e não textual** em qualquer dos dois campos → **corrupção → bloqueio** (§7.1, S11). |
| N-a-P5 | **Zero inferência, zero fuzzy, zero LLM, zero fallback semântico, zero valor derivado de outro campo.** Ausente é ausente. |
| N-a-P6 | **Nenhum campo desnecessário é transportado**: sem nome, telefone, mensagem, preço, capacidade, convidados, formato, qualificação, pendência ou motivo. |

**Composição de E.**

| # | Regra de composição |
|---|---|
| N-a-C1 | E é formado pelos candidatos **projetados** que satisfazem a **classificação por estado** (N-a-E1–N-a-E5) e, **quando `encerrado`**, também a **recência** (N-a-R4). |
| N-a-C2 | **Depois** aplica-se **N-a-F1**: com `veredito_identificador == ENCONTRADO`, o atendimento identificado integra E **exatamente uma vez**, **independentemente de estado ou de recência**. |
| N-a-C3 | **N-a-F1 prevalece sobre N-a.** Nenhuma regra de classificação ou de recência remove o identificado do ciclo em que a própria etapa 3 acabou de encontrá-lo e validá-lo. |

**Duplicatas em E.** N-a **não cria regra global de unicidade**:

| # | Regra de duplicata |
|---|---|
| N-a-D1 | O **ID identificado** sob `ENCONTRADO` deve ocorrer **exatamente uma vez** em E. **Zero ou múltiplas** ocorrências → **bloqueio pelos contratos já vigentes**: **N-a-F1**, **N-I-2** e **P-I5**. |
| N-a-D2 | IDs **não identificados** repetidos: **não deduplicar**, **não bloquear apenas pela repetição**, **não criar unicidade global**. Todos são entregues à cascata, e as contagens de D0–D6 (`total_escopo`, `validos`, `ativos_validos`, …) permanecem válidas como estão. |
| N-a-D3 | A pendência de **unicidade geral de `id_atendimento` entre candidatos não identificados** permanece **ABERTA** (§12, item 17). |

**Ordem canônica de E.** A ordem **não possui significado semântico** para D0–D6 — a cascata
conta e classifica, não privilegia posição. Ainda assim E é canonicalizado **exclusivamente
para auditabilidade**, de modo que a mesma entrada produza sempre a mesma sequência
auditável:

| # | Regra de ordem |
|---|---|
| N-a-O1 | Chave de ordenação **estrutural**, **ascendente**: `(id_atendimento, estado, tipo_evento_registrado, data_nomeada_registrada)`. |
| N-a-O2 | **`None` precede texto** nos dois campos opcionais. |
| N-a-O3 | A canonicalização **não elimina candidato, não deduplica, não muda cardinalidade** e **não altera identidade, alvo nem critério**. |
| N-a-O4 | A canonicalização **não usa recência** e **não usa a ordem de retorno da persistência**. |
| N-a-O5 | Candidatos **indistinguíveis nos quatro campos** têm permutação **observacionalmente idêntica** nas tuplas auditáveis — não há desempate a definir. |

**Produção de H.** H é construído **a partir dos registros recuperados**, por filtro
estrutural `estado == atendimento_humano`, **antes e à parte da filtragem N-a** (H1). **N-a
nunca governa H** (H2), e **H1–H6 permanecem integralmente preservadas**.

**Precedência conceitual da etapa 3.** Ordem normativa — **nenhum loop**, **nenhum relógio
vivo**, **nenhuma decisão do LLM**:

| # | Passo |
|---|---|
| 1 | validar a **configuração temporal** — o limiar (N-a-L4, N-a-L5) |
| 2 | **recuperar pelo identificador**, quando fornecido |
| 3 | **consultar os registros do contato** |
| 4 | **validar o identificador** (§6.1.1, N3–N6) |
| 5 | **validar a integridade** do contexto recuperado |
| 6 | **projetar** os registros (N-a-P1–N-a-P6) |
| 7 | **construir H** (H1) |
| 8 | determinar **`havia_estado_esperado`** |
| 9 | aplicar **N-a** — classificação + recência |
| 10 | aplicar **N-a-F1** |
| 11 | projetar **`id_atendimento_validado`** (N-I-1) |
| 12 | verificar as correspondências **H4/H5**, **N-I** e **P-I** aplicáveis |
| 13 | **canonicalizar E** (N-a-O1–N-a-O5) |
| 14 | **entregar as projeções** à etapa 5 |

**`havia_estado_esperado` — cálculo normativo.**

```text
havia_estado_esperado =
    veredito_identificador == ENCONTRADO
    OU
    existe ao menos um registro recuperado para canal + contato
```

É calculado sobre o **contexto recuperado**, **nunca sobre E**. **Filtrar todo o histórico
para fora de E não transforma o contato em primeiro contato** — é exatamente essa separação
que mantém `SEM_CANDIDATO_ELEGIVEL` distinto de `PRIMEIRO_CONTATO_COMPROVADO` (doc 06 §4.5,
G1–G7).

**Consequências sobre a etapa 5 — a cascata não é alterada.** As situações abaixo são
**invariantes derivadas** dos contratos já vigentes. **R5-P0 não é alterado, D0–D6 não são
alterados e nenhum critério novo é criado**:

| # | Situação | Desfecho |
|---|---|---|
| N-a-X1 | contexto **inválido** | **bloqueio ANTES do `ResolvedorIdentidade`** (E5/S7) |
| N-a-X2 | integridade OK + **H ≠ vazio** | **R5-P0**; **D0–D6 não executam** |
| N-a-X3 | integridade OK + H vazio + `vinculo == DECLARACAO_CONTRADITORIA` | **D0** → `AMBIGUA` / `AMBIGUIDADE_SINAIS_CONTRADITORIOS`, **independentemente de E estar vazio** |
| N-a-X4 | integridade OK + H vazio + D0 não decidiu + **E vazio** + `havia_estado_esperado == true` | **D1** → `SEM_CANDIDATO_ELEGIVEL`. **E4 continua ABERTA** |
| N-a-X5 | integridade OK + H vazio + D0 não decidiu + **E vazio** + `havia_estado_esperado == false` | **D1** → `PRIMEIRO_CONTATO_COMPROVADO` |
| N-a-X6 | **E não vazio**, sem decisão anterior | **D2–D6** normalmente |

**Por que `encerrado` usa recência — tensão T36 / T37.** As duas alternativas simples são
inaceitáveis, e é isso que justifica a **única** condição temporal da política:

- **incluir todos os encerrados** equivale a passar **o histórico inteiro** como conjunto
  elegível — violação explícita da fronteira desta seção, que altera as contagens da cascata;
- **excluir todos os encerrados** tornaria **T36 e T37 estruturalmente inalcançáveis** nos
  cenários previstos: sem candidato encerrado no escopo, não há "mesmo evento" a reabrir nem
  "nova solicitação" a distinguir dele.

Política: **`encerrado` recente entra; `encerrado` fora do limiar sai; N-a-F1 sempre
prevalece.** **T36 e T37 são preservados sem exceção ad hoc** — o identificador validado
continua trazendo o encerrado antigo para o escopo quando o contato o informa, e a cascata
continua decidindo mesma × nova × ambígua exatamente como em §7.1.

**Cenários de conformidade — K-Na.** Registro **documental**; **nenhum teste é criado ou
alterado** por esta arbitragem, e `docs/08` permanece intocado:

| # | Cenário | Resultado normativo |
|---|---|---|
| K-Na-1 | candidato em qualquer estado do **Grupo I** | **elegível**, **sem consultar recência** (N-a-E1) |
| K-Na-2 | `encerrado` **dentro** do limiar | **elegível** (N-a-R4, N-a-R5) |
| K-Na-3 | `encerrado` **fora** do limiar | **não elegível** |
| K-Na-4 | atendimento identificado (`ENCONTRADO`) **fora** do limiar | **entra em E por N-a-F1** (N-a-C2, N-a-C3) |
| K-Na-5 | registro em `atendimento_humano` | integra **H** independentemente de integrar E (H1, H2, N-a-E2) |
| K-Na-6 | `atendimento_humano` presente em E via **N-a-F1** | **H5 satisfeita** — seu ID está em H; nenhuma incoerência |
| K-Na-7 | `encerrado` precisa de recência e **`instante_ultima_transicao` ausente** | **bloqueio por E5/S7** (S9); o resolvedor **não é chamado** |
| K-Na-8 | limiar **ausente, de tipo inválido ou não positivo** | **bloqueio** (N-a-L4), **mesmo sem candidato `encerrado`** (N-a-L5) |
| K-Na-9 | `tipo_evento` e/ou `data_nomeada` ausentes no registro | projetados como **`None`**, **sem inferência** (N-a-P2, N-a-P3, N-a-P5) |
| K-Na-10 | IDs duplicados entre candidatos **não identificados** | **preservados**; **sem bloqueio apenas pela repetição** (N-a-D2) |
| K-Na-11 | ID identificado com **zero** ou **duas ou mais** ocorrências em E | **bloqueio** por **N-I-2 / P-I5** (N-a-D1) |
| K-Na-12 | persistência devolve os mesmos registros em **ordem diferente** | **mesma ordem canônica de E** (N-a-O1, N-a-O4) |
| K-Na-13 | **H ≠ vazio** e **E vazio** | **R5-P0** — takeover; **não** D1 (N-a-X2) |
| K-Na-14 | H vazio + E vazio + **contradição declarada** | **D0** → `AMBIGUIDADE_SINAIS_CONTRADITORIOS`; **não** D1 (N-a-X3) |
| K-Na-15 | H vazio + E vazio + sem contradição + **histórico conhecido** | **`SEM_CANDIDATO_ELEGIVEL`** (N-a-X4) |
| K-Na-16 | H vazio + E vazio + sem contradição + **nenhum histórico** | **`PRIMEIRO_CONTATO_COMPROVADO`** (N-a-X5) |
| K-Na-17 | `encerrado` → estado intermediário → `encerrado` **no mesmo ciclo** | **atualizar** `instante_ultima_transicao` (N-a-T4, N-a-T5) |
| K-Na-18 | **T33** preservando `atendimento_humano` | **não atualizar** `instante_ultima_transicao` (N-a-T6) |

**O que N-a não fecha.** Permanecem **abertas**: o **valor numérico do limiar**, o
**mecanismo de carga** da configuração, a **consulta concreta** à persistência, a
**implementação** do campo temporal, a **unicidade geral** de `id_atendimento` entre
candidatos não identificados e **E4** — o tratamento de `SEM_CANDIDATO_ELEGIVEL` pelo
`OrquestradorMotor` (§12). **Nenhuma implementação é autorizada por esta arbitragem.**

#### Conjunto H — `ids_em_atendimento_humano` (arbitragem R-H)

**H é uma entrada própria e mínima do `ResolvedorIdentidade`, distinta do conjunto
elegível.** Ele **não** é o conjunto elegível, **não** é subconjunto obrigatório dele,
**não** é resultado de N-a e **não** está sujeito à política de recência.

| # | Regra |
|---|---|
| H1 | **H é produzido pela etapa 3** a partir do contexto recuperado, por **filtro estrutural de estado** — `estado == atendimento_humano`. **Não é filtro de elegibilidade.** |
| H2 | **N-a governa exclusivamente o conjunto elegível. N-a não governa H.** Nenhuma política de recência ou elegibilidade pode remover um atendimento em `atendimento_humano` de H. Um canal sob controle humano não "expira" por recência. |
| H3 | **H carrega somente identificadores opacos.** Não carrega nome, telefone, mensagem, tipo de evento, data, convidados, formato, preço, qualificação, pendência nem motivo. **Zero PII, zero texto, zero dado comercial, zero data, zero recência.** |
| H4 | **Cardinalidade define `SituacaoTakeover`**: `0` → `SEM_TAKEOVER`; `1` → `HUMANO_UNICO`; `>= 2` → `HUMANO_MULTIPLO`. **IDs duplicados em H são erro de contrato** — duplicata **não** conta como `HUMANO_MULTIPLO`. |
| H5 | **Coerência defensiva.** Se existir `CandidatoAtendimento` no conjunto elegível com `estado == atendimento_humano`, seu `id_atendimento` **deve** estar presente em H; ausência é **erro de contrato**. **A recíproca não é exigida**: um ID presente em H pode legitimamente **não** estar no conjunto elegível — isso é esperado e é justamente o que preserva a independência de H em relação a N-a. |
| H6 | **H é exclusivamente insumo da resolução de takeover.** Não entra em `CondicoesCiclo`, não chega à `MaquinaEstados`, não cria estado, evento nem transição, e **não amplia** `Identidade` nem `CriterioIdentidade`. |

A separação existe por uma razão estrutural: o conjunto elegível responde *"quais
atendimentos podem ser o referente desta mensagem?"* — pergunta que depende de política. H
responde *"o canal está sob controle humano?"* — fato de estado, que **não** pode depender
de política de recência. Fundir os dois permitiria que uma janela de recência mal calibrada
devolvesse a palavra ao bot num canal que uma pessoa está conduzindo.

### 6.3 Interpretação (saída do LLM na etapa 4)

| Campo | Conteúdo |
|---|---|
| intenções detectadas (`intencoes_detectadas`) | conjunto de códigos de **`IntencaoConversacional`** — vocabulário conceitual **fechado em 11 valores** (arbitragem N-b, adiante), na partição **A1 (6 derivados)**, **A2 (2 autônomos mapeáveis a evento)** e **B (3 autônomos não mapeáveis diretamente a evento)**. O grupo **A2** contém **exatamente dois** sinais — `INTERESSE_EM_VISITA` e `EXCECAO_SOLICITADA` —, cujas **correspondências semânticas** são, respectivamente, `E10` e `E17`. **A etapa 4 não emite `Exx`**: a transformação posterior desses sinais em evento confirmado **não possui produtor concreto** e é **residual explícito de integração** (N-b-G2, N-b-RES1–N-b-RES3) |
| dados extraídos | tipo de evento, data, convidados, formato, nome, contato — cada um com confiança própria |
| correções | campos que contradizem valor já registrado |
| perguntas comerciais | **consultas comerciais do interessado** — pergunta interrogativa, pedido informacional ou solicitação de material/informação comercial —, cada uma com texto, confiança e, **após a micro-arbitragem AJ2** (adiante), um **`AssuntoComercial`** obrigatório |
| pedido de humano | sim/não |
| **referências ao evento anterior** | menções que indicam continuidade ("o casamento de outubro que a gente falou", "sobre aquele orçamento"), em texto, com confiança. Insumo da resolução de identidade (§7.1) |
| nível de confiança | por campo e global |
| trechos ambíguos | partes da mensagem não interpretadas com segurança |

O interpretador **não** classifica compatibilidade, **não** decide handoff e **não** resolve
identidade de atendimento. Ele apenas relata o que leu. `pedido de humano` é um sinal, não
uma decisão: quem emite `E18` é o `DetectorHandoff`. `referências ao evento anterior` também
é sinal: quem decide T36 × T37 é o `ResolvedorIdentidade`, na etapa 5.

#### N-b — contrato global da interpretação da etapa 4 (arbitragem N-b)

Arbitragem **exclusivamente documental**. Fecha o contrato da **saída da etapa 4**,
conceitualmente denominada **`Interpretacao`**. **Nenhum tipo Python é criado**, nenhum JSON
Schema, nenhuma biblioteca, nenhum fornecedor, nenhum modelo, nenhum SDK, nenhuma API, nenhum
formato de transporte e nenhum arquivo ou diretório novo. **§4.1 permanece inalterada, com 14
componentes**, e §2 permanece com **nove** responsabilidades: **não** existe `Interpretador`
determinístico e **não** existe componente 15.

**Invariantes gerais.**

| # | Invariante |
|---|---|
| N-b-G1 | A `Interpretacao` **relata o que foi lido**. Ela **não** classifica compatibilidade, **não** decide handoff, **não** resolve identidade, **não** qualifica, **não** escolhe pacote, **não** consulta o YAML e **não** recebe o YAML. |
| N-b-G2 | A `Interpretacao` **não produz** `Exx`, `Txx`, `Rxx`, `Qualificacao`, `Violacao`, estado, pendência nem `motivo_encerramento`. |
| N-b-G3 | A **única** condição de `CondicoesCiclo` (§4.4) cujo produtor esta arbitragem fecha é a **condição 5**, `interesse_confirmar_disponibilidade`. As condições **2**, **4** e **8** permanecem **NÃO ATRIBUÍDAS**. |
| N-b-G4 | A `Interpretacao` **não é entrada direta** do `ResolvedorIdentidade`. O resolvedor recebe **exclusivamente** a `ProjecaoInterpretacao` já existente, com **sete** campos (§7.1). |
| N-b-G5 | `Interpretacao` → `ProjecaoInterpretacao` é **derivação pura e determinística** (N-b-K1–N-b-K7), feita **dentro da fronteira da etapa 4**. |
| N-b-G6 | Exigem confiança **declarada**: cada **campo presente** de `dados_extraidos`; cada `CorrecaoInterpretada`; cada `PerguntaComercial`; cada `ReferenciaAoEventoAnterior`; cada intenção **autônoma** dos grupos **A2** e **B**; e `pedido_de_humano == verdadeiro`. |
| N-b-G6b | **Não** declaram confiança: `trechos_ambiguos`; `confianca_global` — ela própria **é** a confiança; `pedido_de_humano == falso`, cujo `confianca_pedido_de_humano` é obrigatoriamente `None`; as intenções **derivadas** do grupo **A1**, cuja confiança é **calculada** (N-b-X3); e **campos ausentes**, cuja confiança é `None`. |
| N-b-G6c | **Confiança declarada sem valor correspondente é erro de contrato** (E-Nb-2), simétrico a **C2** de §7.1 — valor presente sem confiança declarada é erro de contrato (E-Nb-1). |
| N-b-G7 | A confiança é **binária**: `ALTA` \| `BAIXA`. **Nenhum threshold numérico** é criado. |
| N-b-G8 | **Ausência de `Interpretacao` não equivale a `Interpretacao` vazia.** São situações distintas, com consequências distintas (N-b-M1). |

**As oito responsabilidades da `Interpretacao`.** As oito categorias da tabela acima
permanecem, sem supressão nem fusão. Designação conceitual:

| # | Categoria de §6.3 | Designação conceitual |
|---|---|---|
| 1 | intenções detectadas | `intencoes_detectadas` |
| 2 | dados extraídos | `dados_extraidos` |
| 3 | correções | `correcoes` |
| 4 | perguntas comerciais | `perguntas_comerciais` |
| 5 | pedido de humano | `pedido_de_humano` |
| 6 | referências ao evento anterior | `referencias_evento_anterior` |
| 7 | nível de confiança | `confianca_global` (mais a confiança **por item**, distribuída nas demais categorias) |
| 8 | trechos ambíguos | `trechos_ambiguos` |

**`IntencaoConversacional` — vocabulário conceitual fechado com exatamente 11 valores.**
Partição obrigatória em **A1**, **A2** e **B**:

| Grupo | # | Código | Natureza |
|---|---|---|---|
| **A1 — derivados (6)** | 1 | `TIPO_EVENTO_INFORMADO` | derivado de `dados_extraidos.tipo_evento` |
| | 2 | `DATA_INFORMADA` | derivado de `dados_extraidos.data_nomeada` |
| | 3 | `CONVIDADOS_INFORMADOS` | derivado de `dados_extraidos.convidados` |
| | 4 | `FORMATO_INFORMADO` | derivado de `dados_extraidos.formato` |
| | 5 | `PERGUNTA_COMERCIAL` | derivado da coleção `perguntas_comerciais` |
| | 6 | `PEDIDO_DE_HUMANO` | derivado do booleano `pedido_de_humano` |
| **A2 — autônomos mapeáveis a evento (2)** | 7 | `INTERESSE_EM_VISITA` | autônomo |
| | 8 | `EXCECAO_SOLICITADA` | autônomo |
| **B — autônomos não mapeáveis diretamente a evento (3)** | 9 | `INTERESSE_CONFIRMAR_DISPONIBILIDADE` | autônomo; alimenta a **condição 5** de §4.4 |
| | 10 | `CONTINUIDADE_DE_EVENTO_DECLARADA` | autônomo; alimenta `intencao_identidade` |
| | 11 | `EVENTO_NOVO_DECLARADO` | autônomo; alimenta `intencao_identidade` |

Os **seis códigos do grupo A1 são derivações determinísticas dentro da fronteira da etapa 4**.
Eles **não** são classificações independentes produzidas pelo LLM: o **payload estruturado
dedicado é a fonte autoritativa**, e o código apenas o espelha.

**Consistência cruzada.**

| # | Regra |
|---|---|
| N-b-X1 | Quando um fato existe em **duas zonas** da `Interpretacao`, o **payload dedicado é autoritativo**; o código em `intencoes_detectadas` é **derivado**. |
| N-b-X2 | A **presença** do código derivado depende **somente da presença** do payload — **nunca** da confiança. |
| N-b-X3 | A **confiança** do código derivado é **calculada**, não declarada independentemente. Payload **unitário**: mesma confiança do payload. Payload **0..N**: **ao menos um `ALTA` → `ALTA`**; **não vazio e todos `BAIXA` → `BAIXA`**. |
| N-b-X4 | **Bi-implicação obrigatória**: código presente ⟺ payload presente. Violação é **erro de contrato**. |
| N-b-X5 | As **oito** responsabilidades de §6.3 permanecem; a linha `intencoes_detectadas` passa a conter códigos **derivados** e **autônomos**. |
| N-b-X6 | A partição **A1 / A2 / B** acima é **preservada** e fechada. |

**Os seis pares com representação dupla.** Para **A–F**: bi-implicação obrigatória, código
**derivado**, divergência é **erro de contrato**, e o código derivado **não acrescenta
semântica** ao payload.

| Par | Código derivado | Bi-implicação | Fonte autoritativa |
|---|---|---|---|
| A | `TIPO_EVENTO_INFORMADO` | ⟺ `dados_extraidos.tipo_evento` presente | `dados_extraidos.tipo_evento` |
| B | `DATA_INFORMADA` | ⟺ `dados_extraidos.data_nomeada` presente | `dados_extraidos.data_nomeada` |
| C | `CONVIDADOS_INFORMADOS` | ⟺ `dados_extraidos.convidados` presente | `dados_extraidos.convidados` |
| D | `FORMATO_INFORMADO` | ⟺ `dados_extraidos.formato` presente | `dados_extraidos.formato` |
| E | `PERGUNTA_COMERCIAL` | ⟺ `perguntas_comerciais` **não vazia** | coleção `perguntas_comerciais` |
| F | `PEDIDO_DE_HUMANO` | ⟺ `pedido_de_humano == verdadeiro` | `pedido_de_humano` |

**Dados extraídos — exatamente seis campos.**

| # | Regra |
|---|---|
| N-b-D1 | `dados_extraidos` tem **exatamente seis** campos: `tipo_evento`, `data_nomeada`, `convidados`, `formato`, `nome`, `contato`. |
| N-b-D2 | `tipo_evento` é o **texto nominal do interessado**. **Sem** sinônimo, **sem** categoria comercial, **sem** consulta ao YAML. |
| N-b-D3 | `data_nomeada` é **texto nominal**. **Zero parsing de calendário.** |
| N-b-D4 | `convidados` é **inteiro não negativo**. `bool` é **inválido**. |
| N-b-D5 | `formato` é vocabulário **fechado**: `sentado` \| `coquetel`. |
| N-b-D6 | `nome` e `contato` são **texto** e são **PII** (§6.6). |
| N-b-D7 | Confiança é **obrigatória** para **todo campo presente**; **campo ausente** tem confiança `None`. Confiança `BAIXA`: o campo **permanece na `Interpretacao` para diagnóstico**, mas é **não efetivo para consumo estruturado**. |
| N-b-D8 | A etapa 4 **não compara** os dados com estado ou contexto, **não grava** e **não produz** `insumo_qualificacao_atualizado` (doc 06 §4.1). |

**Correções.** `CorrecaoInterpretada` tem **três** campos: `campo`, `valor_novo`, `confianca`.

| # | Regra |
|---|---|
| N-b-C1 | `campo` é **um dos seis** de `dados_extraidos`; `valor_novo` pertence ao **mesmo domínio** do campo; `confianca` é `ALTA` \| `BAIXA`, **obrigatória**. |
| N-b-C2 | Correção significa **retificação explicitamente declarada** pelo interessado. **Contradição sem declaração explícita não é correção.** |
| N-b-C3 | A correção **não carrega o valor anterior**: o valor anterior permanece no **contexto** (§6.2). |
| N-b-C4 | Todo campo presente em `correcoes` deve **também existir** em `dados_extraidos`, com o **mesmo campo**, o **mesmo valor** e a **mesma confiança**. Divergência é **erro de contrato**. |
| N-b-C5 | A etapa 4 **relata**. A **etapa 6** é quem futuramente decide gravação e comparação (§5). |
| N-b-C6 | Esta arbitragem **não resolve a pendência B**. |

**Perguntas comerciais.** `PerguntaComercial` tinha, no contrato original de N-b, **dois**
campos: `texto` e `confianca`. A micro-arbitragem **AJ2** (adiante) **estende formalmente**
essa estrutura para **três** campos, acrescentando o `assunto` — ver **N-b-Q7**–**N-b-Q12**.
Cardinalidade **0..N** em ambos os contratos.

| # | Regra |
|---|---|
| N-b-Q1 | O `texto` é **preservado no runtime da `Interpretacao`**. Texto **vazio ou em branco** é **erro de contrato**. **Ampliação mínima por AJ2**: o `assunto` também é **preservado no runtime**, ao lado de `texto` e `confianca` (N-b-Q7). |
| N-b-Q2 | `ALTA` → pergunta **efetiva**. `BAIXA` → texto **preservado apenas para diagnóstico**. |
| N-b-Q3 | **Somente perguntas `ALTA`** entram em consumo estruturado futuro. Logo, uma pergunta `BAIXA` **não** é consumida futuramente pelo produtor de `E09`/**S2-D8** nem pelo `SeletorFatos`. |
| N-b-Q4 | Isso **não resolve** **S2-D8**, **SeletorFatos**, **C**, `Rxx` nem mapeamento YAML. |
| N-b-Q5 | `PERGUNTA_COMERCIAL` está presente em `intencoes_detectadas` **se a coleção não for vazia**, **independentemente** da efetividade de cada item. |
| N-b-Q6 | Confiança **derivada** do código: **ao menos uma `ALTA` ⇒ `ALTA`**; **todas `BAIXA` ⇒ `BAIXA`**. |

**Pedido de humano.** Campos conceituais: `pedido_de_humano: bool` e
`confianca_pedido_de_humano: ALTA | BAIXA | None`.

| # | Regra |
|---|---|
| N-b-PH1 | `pedido_de_humano == falso` ⇒ `confianca_pedido_de_humano` é obrigatoriamente `None`. `pedido_de_humano == verdadeiro` ⇒ confiança **obrigatória**. |
| N-b-PH2 | A **fonte autoritativa** é `pedido_de_humano`; `PEDIDO_DE_HUMANO` é **derivado** do booleano. |
| N-b-PH3 | `pedido_de_humano = verdadeiro` com confiança `BAIXA` **permanece sinal efetivo** para o futuro `DetectorHandoff`. |
| N-b-PH4 | N-b-PH3 é a **única exceção** à regra "`BAIXA` = ausência para consumo estruturado". A exceção **não chega à `ProjecaoInterpretacao`**, **não altera C1–C3** de identidade (§7.1), **não cria `E18`** e **não cria precedente** para nenhum outro campo. |
| N-b-PH5 | `EXCECAO_SOLICITADA` é **autônoma** e segue a regra geral: `BAIXA` = ausência para consumo estruturado. |
| N-b-PH6 | Quem emite `E18` continua sendo o `DetectorHandoff` — **não** a etapa 4 (N-b-G2). |

**Referências ao evento anterior.** `ReferenciaAoEventoAnterior` tem **dois** campos: `texto`,
`confianca`. Cardinalidade **0..N**.

| # | Regra |
|---|---|
| N-b-R1 | O `texto` é **preservado na `Interpretacao`** e **não chega ao `ResolvedorIdentidade`**. Texto **vazio ou em branco** é **erro de contrato**. |
| N-b-R2 | Coleção **vazia** ⇒ `referencia_evento_anterior = SEM_REFERENCIA` e `confianca_referencia = None`. |
| N-b-R3 | Coleção **não vazia** ⇒ `referencia_evento_anterior = COM_REFERENCIA`. |
| N-b-R4 | **Ao menos uma `ALTA`** ⇒ `confianca_referencia = ALTA`; **todas `BAIXA`** ⇒ `confianca_referencia = BAIXA`. |
| N-b-R5 | As regras **C1–C3** de §7.1 permanecem **exatamente como estão**: é o consumidor que trata `BAIXA` como ausência. |

**Trechos ambíguos.** `TrechoAmbiguo` tem **um** campo: `texto`. **Sem confiança.**
Cardinalidade **0..N**.

| # | Regra |
|---|---|
| N-b-T1 | Texto **vazio ou em branco** é **erro de contrato**. |
| N-b-T2 | Função **exclusivamente diagnóstica**: **não** altera identidade, qualificação, evento, pendência nem bloqueio. |
| N-b-T3 | **Não entra** na `ProjecaoInterpretacao`. |
| N-b-T4 | **Não logar por padrão**, **não incluir em mensagem de erro** e **não usar em exemplo versionado** (§6.6, L3, L4). |
| N-b-T5 | Declarar confiança em `trechos_ambiguos` é **erro de contrato** (N-b-G6b). |

**Confiança global.**

| # | Regra |
|---|---|
| N-b-CG1 | `confianca_global` está **sempre presente**: `ALTA` \| `BAIXA`. Ausência é **erro de contrato**. |
| N-b-CG2 | É **metadado diagnóstico**. **Não** gera alerta, **não** bloqueia, **não** altera identidade, **não** produz evento, transição, resposta nem gravação. **Não participa** da `ProjecaoInterpretacao`. |
| N-b-CG3 | Divergência entre `confianca_global` e a confiança de um campo **não é erro**, **não é alerta**, **não exige reconciliação** e **não muda comportamento**. A **confiança do campo prevalece** para consumo estruturado. |
| N-b-CG4 | **Nenhum threshold**, **nenhuma agregação** e **nenhuma derivação automática**. O uso operacional futuro está **fora do escopo** desta arbitragem. |

**Intenções autônomas.** Para `INTERESSE_EM_VISITA`, `EXCECAO_SOLICITADA`,
`INTERESSE_CONFIRMAR_DISPONIBILIDADE`, `CONTINUIDADE_DE_EVENTO_DECLARADA` e
`EVENTO_NOVO_DECLARADO`: presença/ausência; confiança `ALTA`/`BAIXA` **obrigatória** quando
presente; e **`BAIXA` = ausência para consumo estruturado, sem exceção alguma neste grupo**.
`CONTINUIDADE_DE_EVENTO_DECLARADA` e `EVENTO_NOVO_DECLARADO` são **mutuamente exclusivas**:
coexistência é **erro de contrato**.

**Condição 5 de §4.4 — função total.**

| # | Entrada | `interesse_confirmar_disponibilidade` |
|---|---|---|
| N-b-CD1 | `Interpretacao` válida + `INTERESSE_CONFIRMAR_DISPONIBILIDADE` com confiança `ALTA` | `True` |
| N-b-CD2 | `Interpretacao` válida + `INTERESSE_CONFIRMAR_DISPONIBILIDADE` com confiança `BAIXA` | `False` |
| N-b-CD3 | `Interpretacao` válida + intenção **ausente** | `False` |
| N-b-CD4 | **Sem `Interpretacao`** | `None` |

`True`/`False` significam **avaliado neste ciclo**; `None` significa **não avaliado neste
ciclo**. **Somente a linha 5** de §4.4 muda: as outras **sete** condições permanecem
exatamente como estão, e as condições **2**, **4** e **8** continuam **não atribuídas**.

**Derivação para a `ProjecaoInterpretacao`.** Tabela **total** sobre os **sete** campos de
§7.1. A derivação **não aplica C3**: ela **transporta valor e confiança**, e o consumidor
`ResolvedorIdentidade` é quem já aplica a semântica de `BAIXA` como ausência.

| # | Campo da projeção | Derivação |
|---|---|---|
| N-b-K1 | `intencao_identidade` | `EVENTO_NOVO_DECLARADO` com `ALTA` → `NOVO_EVENTO_DECLARADO`; **senão** `CONTINUIDADE_DE_EVENTO_DECLARADA` com `ALTA` → `CONTINUIDADE_DECLARADA`; **todo o resto** → `NAO_DISCRIMINANTE`. As duas intenções são **mutuamente exclusivas**; a ordem acima é apenas **defensiva**. |
| N-b-K2 | `referencia_evento_anterior` | `referencias_evento_anterior` **não vazia** → `COM_REFERENCIA`; **vazia** → `SEM_REFERENCIA`. |
| N-b-K3 | `confianca_referencia` | **ao menos uma `ALTA`** → `ALTA`; **não vazia e todas `BAIXA`** → `BAIXA`; **vazia** → `None`. |
| N-b-K4 | `tipo_evento_extraido` | transportar o **valor nominal**, **inclusive** com confiança `BAIXA`; **ausente** → `None`. |
| N-b-K5 | `confianca_tipo` | a **confiança do campo**; `None` quando o campo está ausente. |
| N-b-K6 | `data_nomeada_extraida` | transportar o **valor nominal**, **inclusive** com confiança `BAIXA`; **ausente** → `None`. |
| N-b-K7 | `confianca_data` | a **confiança do campo**; `None` quando o campo está ausente. |
| N-b-K8 | **Campos que NÃO atravessam para a identidade — lista fechada** | `convidados`, `formato`, `nome`, `contato`, `correcoes`, `perguntas_comerciais`, `pedido_de_humano`, `trechos_ambiguos`, `confianca_global` e as **demais intenções que não produzem `intencao_identidade`**. **Nenhuma pergunta, citação, nome, contato ou trecho conversacional chega ao `ResolvedorIdentidade`.** (Após **AJ2**, o `assunto`, por estar **dentro** de `perguntas_comerciais`, **também não atravessa** — N-b-Q12.) |

**Erros de contrato — lista fechada `E-Nb-1` a `E-Nb-19`.**

| # | Erro |
|---|---|
| E-Nb-1 | Valor presente **sem confiança** nas categorias que exigem confiança (N-b-G6). |
| E-Nb-2 | Confiança declarada **sem valor correspondente**. |
| E-Nb-3 | Confiança declarada **onde é proibida**: `trechos_ambiguos`; intenção **derivada** do grupo **A1**; `pedido_de_humano == falso`; campo de dado **ausente**. |
| E-Nb-4 | `confianca_global` **ausente**. |
| E-Nb-5 | Valor **fora de vocabulário fechado**: `IntencaoConversacional`; identificador de campo; `formato`. **Ampliado por AJ2**: `assunto` **ausente** ou **fora do vocabulário** `AssuntoComercial` (AJ2-X1, AJ2-X2). `ASSUNTO_NAO_CLASSIFICADO` **não** gera este erro. |
| E-Nb-6 | Código **repetido** em `intencoes_detectadas`. |
| E-Nb-7 | Campo **repetido** em `correcoes`. |
| E-Nb-8 | `convidados` **negativo**, `bool` ou **não inteiro**. |
| E-Nb-9 | `formato` fora de `sentado` \| `coquetel`. |
| E-Nb-10 | Texto **vazio ou em branco** em pergunta, referência ou trecho ambíguo. |
| E-Nb-11 | Dado **A–D** presente **sem** o código derivado correspondente. |
| E-Nb-12 | Código **A–D** presente **sem** o dado correspondente. |
| E-Nb-13 | Confiança de código **derivado divergente** do payload ou da agregação de N-b-X3. |
| E-Nb-14 | `perguntas_comerciais` **não vazia** sem `PERGUNTA_COMERCIAL`. |
| E-Nb-15 | `PERGUNTA_COMERCIAL` presente com a coleção **vazia**. |
| E-Nb-16 | `pedido_de_humano = verdadeiro` **sem** `PEDIDO_DE_HUMANO`, **ou** `PEDIDO_DE_HUMANO` presente com o booleano **falso**. |
| E-Nb-17 | Correção cujo **campo não existe** em `dados_extraidos`, ou com **valor divergente**, ou com **confiança divergente**. |
| E-Nb-18 | `CONTINUIDADE_DE_EVENTO_DECLARADA` e `EVENTO_NOVO_DECLARADO` **simultâneas**. |
| E-Nb-19 | Produção, pela etapa 4, de `Exx`, `Txx`, `Rxx`, qualificação, violação, estado, pendência, `motivo_encerramento` — ou de **qualquer condição de §4.4 além da condição 5**. |

**Tratamento.** Erro de contrato **bloqueia na fronteira da etapa 4**: **nenhuma
`ProjecaoInterpretacao`** é produzida e **a etapa 5 não executa**. Nunca converter erro de
contrato em `Identidade.AMBIGUA`. Três coisas permanecem **distintas** e não podem ser
confundidas: **erro de contrato**, **confiança `BAIXA`** e **ambiguidade linguística
legítima** — esta última é o que alimenta `trechos_ambiguos`.

**Modo degradado — produtor de interpretação indisponível.**

| # | Regra |
|---|---|
| N-b-M1 | **Nenhuma `Interpretacao`.** Ausência **não** é interpretação vazia (N-b-G8). |
| N-b-M2 | **Nenhuma `ProjecaoInterpretacao`.** A **etapa 5 não executa** e a `MaquinaEstados` **não é chamada por esse caminho**. |
| N-b-M3 | N-b **não cria gatilho de alerta novo**. Preservação e alerta seguem **somente** os contratos já vigentes de §7 e §7.2 e a coordenação futura. |
| N-b-M4 | A política atual de §7 **permanece**: sem extração nova; textos aprovados literais; se a mensagem exigir interpretação, **R03 + handoff**; **nunca adivinhar**. N-b **não escolhe** literal × `Rxx` e **não decide** a resposta final. |
| N-b-M5 | **Nada derivado de interpretação inexistente é gravado.** |
| N-b-M6 | `interesse_confirmar_disponibilidade = None` (N-b-CD4). |
| N-b-M7 | **Zero** fila, **zero** retry, **zero** cache, **zero** palavra-chave, **zero** segundo modelo e **zero** tecnologia nova. |
| N-b-M8 | A **coordenação do modo degradado** pertence ao pipeline / `OrquestradorMotor` **futuro**. Qualquer emissão continua sujeita a §7.2. |

**Fronteira do produtor.**

| # | Regra |
|---|---|
| N-b-F1 | A etapa 4 usa o **limite único de LLM já previsto** em §4.2 e §9. A designação conceitual é **"produtor de interpretação da etapa 4"**. |
| N-b-F2 | É **fronteira funcional**, **não** componente determinístico novo. **§4.1 permanece com 14 componentes**; §2 permanece com **nove** responsabilidades. |
| N-b-F3 | Fornecedor, modelo, SDK, API, biblioteca e formato de transporte **não são escolhidos**. |
| N-b-F4 | O produtor **não lê o YAML**, **não recebe o YAML**, **não decide comercial**, **não produz `Exx`/`Rxx`**, **não persiste** e **não consulta a persistência**. |
| N-b-F5 | Ele entrega **uma `Interpretacao` válida** **ou** **nada**. A derivação dos códigos **A1**, da `ProjecaoInterpretacao` e da **condição 5** é **determinística dentro da fronteira da etapa 4** e **não constitui decisão independente do LLM**. |

**Residual de eventos `Exx` — registro explícito, sem identificador novo.**

| # | Registro |
|---|---|
| N-b-RES1 | **A etapa 4 não emite `Exx`** (N-b-G2, E-Nb-19). |
| N-b-RES2 | A **transformação posterior** dos sinais interpretados em **eventos confirmados** **ainda não possui produtor concreto**. Isso é **residual explícito de integração**. |
| N-b-RES3 | O residual **não** é componente, **não** é linha de pendência nova e **não** é atribuído ao `OrquestradorMotor`, ao `DetectorHandoff` nem ao `Qualificador`. Se futuramente revelar decisão própria, exigirá **arbitragem específica**. |

**PII e texto.** No **runtime** da `Interpretacao`, `nome`, `contato`, textos de pergunta,
referência e trecho ambíguo **podem existir**. Na **`ProjecaoInterpretacao`**, `nome`,
`contato`, pergunta, referência e trecho ambíguo são **proibidos** (N-b-K8). A
**persistência** não tem seu contrato alterado por N-b. Em **log e auditoria**: PII
**mascarada**, texto **não** por padrão, e qualquer exceção segue **§6.6**. A **saída do
resolvedor** permanece com **zero PII e zero texto conversacional**. **Mensagem de erro**:
**zero PII e zero trecho real**. O repositório é **público**: **zero conversa real**, **zero
PII**, somente exemplos **genéricos ou fictícios**.

#### AJ1 — micro-arbitragem de representação e canonicalização de N-b (arbitragem AJ1)

Micro-arbitragem **exclusivamente documental**. Fecha a **representação e a canonicalização
determinística** da `Interpretacao` **antes** de qualquer materialização em código.

**AJ1 não reabre N-b**, **não implementa N-b**, **não cria componente**, **não cria
subetapa** e **não cria exceção pública nova**. Nenhum arquivo de `src/`, `tests/`,
`knowledge/` ou `prompts/` é criado ou alterado. **§4.1 permanece com 14 componentes** e §2
com **nove** responsabilidades. `IntencaoConversacional` continua com **exatamente 11**
valores; a lista de erros de contrato continua com **exatamente 19** códigos `E-Nb`; §8.2
continuava, **à época de AJ1**, com **40** cenários `K-Nb` — fronteira depois **estendida para
51** pela micro-arbitragem **AJ2**, posterior. Nenhuma intenção nova, nenhum erro novo,
nenhum cenário novo **por AJ1**. **A 3B.8 não existe** e **não é criada aqui**.

**Decisão normativa central — o que o produtor não determinístico entrega.**

| # | Decisão AJ1 |
|---|---|
| AJ1-1 | **`A1` não é entrada semântica independente do produtor não determinístico.** Os seis códigos do grupo **A1** **nunca** recebem valor semântico próprio vindo do LLM. |
| AJ1-2 | O produtor não determinístico entrega **somente**: `dados_extraidos`; `correcoes`; `perguntas_comerciais`; `pedido_de_humano` — mais a confiança correspondente quando aplicável (N-b-PH1); `referencias_evento_anterior`; `trechos_ambiguos`; `confianca_global`; e as intenções **autônomas** dos grupos **A2** e **B**. |
| AJ1-3 | O **slot de intenções autônomas** aceita **exatamente** cinco valores: `INTERESSE_EM_VISITA`, `EXCECAO_SOLICITADA`, `INTERESSE_CONFIRMAR_DISPONIBILIDADE`, `CONTINUIDADE_DE_EVENTO_DECLARADA` e `EVENTO_NOVO_DECLARADO`. |
| AJ1-4 | Dentro da fronteira da etapa 4, a camada **determinística** (a) **valida** a entrada realmente recebida; (b) **deriva** a presença dos seis códigos **A1**; (c) **calcula** a confiança **A1** por **N-b-X3**; (d) **verifica** as pós-condições; e (e) produz **uma `Interpretacao` canônica válida** **ou** um **erro de contrato**. |
| AJ1-5 | **N-b-X1, N-b-X2, N-b-X3, N-b-X4, N-b-G6b e N-b-F5 são preservadas integralmente.** O **payload dedicado continua autoritativo** (N-b-X1). |

**A1 canônico.**

| # | Regra AJ1 |
|---|---|
| AJ1-A1a | A **presença** de cada código **A1** é **derivada** do payload correspondente (N-b-X2, N-b-X4). |
| AJ1-A1b | A **confiança** de cada código **A1** é **calculada** por **N-b-X3** — nunca declarada (N-b-G6b). |
| AJ1-A1c | A confiança **A1 calculada pode ser armazenada** na `Interpretacao` canônica **para auditabilidade**. **Armazenada não significa declarada**: o valor armazenado é **resultado** da derivação, não insumo dela. |
| AJ1-A1d | `intencoes_detectadas` canônica contém **os A1 derivados mais as A2/B autônomas**, **sem repetição**. |
| AJ1-A1e | A **ordem canônica** de `intencoes_detectadas` existe **apenas para auditabilidade** e **não estabelece precedência semântica** alguma. |

**Precedência entre `E-Nb-3` e `E-Nb-5` no slot autônomo.** O slot de intenções autônomas
possui **vocabulário fechado A2/B** (AJ1-3). Tentativa de apresentar um código **A1** nesse
slot é resolvida assim:

| Caso | Situação | Erro |
|---|---|---|
| A | Código **A1** no slot autônomo **acompanhado de confiança declarada** | **`E-Nb-3` prevalece** — é tentativa explícita de **declarar confiança em intenção derivada**, o que **N-b-G6b** proíbe |
| B | Código **A1** no slot autônomo **sem confiança declarada** | **`E-Nb-5`** — valor **fora do vocabulário fechado admissível** naquele slot |

**Isso não torna `A1` entrada válida.** Ambos os casos são **rejeitados antes da
canonicalização**: nenhuma `Interpretacao` canônica é produzida.

**Clarificação de `E-Nb-5`, sem ampliar nada**: "vocabulário fechado" inclui o **vocabulário
fechado admissível para a categoria/slot em que o valor aparece**. O **vocabulário global de
`IntencaoConversacional` não é alterado** — ele continua com **11** valores.

**Classificação AJ1 dos erros `E-Nb`.** Nenhum código é removido, renomeado ou acrescentado:
a lista permanece **`E-Nb-1`–`E-Nb-19`**. A classificação abaixo descreve **de onde cada erro
pode vir**, não o que ele significa.

| Classe AJ1 | Códigos |
|---|---|
| **Recebíveis / runtime** — provocáveis pela entrada realmente recebida | `E-Nb-1`, `E-Nb-2`, `E-Nb-3`, `E-Nb-4`, `E-Nb-5`, `E-Nb-6` **somente** para **duplicação de intenção autônoma recebida**, `E-Nb-7`, `E-Nb-8`, `E-Nb-9`, `E-Nb-10`, `E-Nb-17`, `E-Nb-18` |
| **Invariantes internos / program error da canonicalização** | `E-Nb-6` **no ramo A1**, `E-Nb-11`, `E-Nb-12`, `E-Nb-13`, `E-Nb-14`, `E-Nb-15`, `E-Nb-16` |
| **Invariante estrutural do módulo** | `E-Nb-19` |

**Não se afirma que todo `E-Nb` precisa ser provocável pelo futuro LLM.** Um erro pode ser
**semanticamente válido** e, ainda assim, **impossível por construção** numa canonicalização
correta — é o caso dos invariantes internos.

**`E-Nb-13` e a confiança A1.**

| # | Fixação AJ1 |
|---|---|
| AJ1-13a | `E-Nb-13` é **invariante / program error da derivação determinística**, não erro recebível. |
| AJ1-13b | A confiança **A1 calculada internamente** deve **sempre** corresponder a **N-b-X3**. |
| AJ1-13c | **Nenhuma confiança A1 independente é aceita do produtor** — tentar declará-la é `E-Nb-3` (AJ1, caso A), não `E-Nb-13`. |

**Invariantes de bi-implicação e derivação — `E-Nb-11` a `E-Nb-16`.** Registrados como
invariantes, **semanticamente válidos mesmo sendo impossíveis** numa canonicalização correta
por construção:

| # | Invariante |
|---|---|
| `E-Nb-11` | payload **A–D** ⇒ código correspondente presente |
| `E-Nb-12` | código **A–D** ⇒ payload correspondente presente |
| `E-Nb-14` | `perguntas_comerciais` **não vazia** ⇒ `PERGUNTA_COMERCIAL` presente |
| `E-Nb-15` | `PERGUNTA_COMERCIAL` presente ⇒ `perguntas_comerciais` **não vazia** |
| `E-Nb-16` | `pedido_de_humano` verdadeiro ⟺ `PEDIDO_DE_HUMANO` presente |

**`E-Nb-19` — estratégia futura de prova estrutural.** A prova de `E-Nb-19` é **estrutural**,
sobre a superfície do futuro módulo: **superfície pública fechada**; **tipos de retorno
fechados**; **campos das estruturas fechados**; **produtores públicos fechados**; e a
**condição 5 como única condição de §4.4 produzida**. O **fechamento de imports** é
**somente evidência complementar de pureza**: **import, por si só, não prova `E-Nb-19`**.

**Condição 5 — preservada.** A **condição 5** de §4.4 **já possui produtor conceitualmente
atribuído** por N-b (N-b-G3, N-b-CD1–N-b-CD4). A futura implementação apenas **materializa**
esse produtor — **não** o cria. As condições **2**, **4** e **8** continuam as **únicas
NÃO ATRIBUÍDAS**, e **nenhuma outra condição é alterada**.

**`FormatoEvento` — decisão para a futura materialização.** É **permitido reutilizar, por
import**, o `FormatoEvento` de `src/casa77_sdr/qualification.py`, porque: é **vocabulário
técnico fechado**, **exatamente** `sentado` \| `coquetel` (N-b-D5); a **cadeia de imports é
pura**; **não cria ciclo** (D7); **não lê YAML**; e **não avalia regra comercial**.
`qualification.py` **permanece inalterado**.

| # | Fronteira |
|---|---|
| AJ1-F1 | Importar `FormatoEvento` **não** significa produzir `Qualificacao` e **não** viola `E-Nb-19`. |
| AJ1-F2 | O enum **não é movido**, **não é redeclarado** e **nenhum** `shared/domain/types` é criado. |

**Futura materialização — não autorizada por esta micro-arbitragem.** Após AJ1 integrada e
reconciliada, a candidata funcional poderá ter **lista fechada**: **criar**
`src/casa77_sdr/interpretation.py` e `tests/test_interpretation.py`; **alterar**
`docs/07-arquitetura-motor-respostas.md` **somente** para registrar a materialização.
**Nada disso é autorizado aqui**: AJ1 é documental e **N-b permanece NÃO IMPLEMENTADA**.

**Fora do escopo de AJ1.** `N-b-RES1`–`N-b-RES3` permanecem **inalteradas**: `N-b-RES1`
preserva a **proibição de a etapa 4 emitir `Exx`**; `N-b-RES2` permanece como **residual
explícito aberto** da **transformação posterior** dos sinais interpretados em **eventos
confirmados**, ainda **sem produtor concreto**; e `N-b-RES3` preserva a **classificação**
desse residual, **sem criar componente, pendência nova ou atribuição automática de
produtor**. Permanecem igualmente **abertas e inalteradas**: **S2-D8**; **S3-D1**; **E4**;
**B**; **C**; o `DetectorHandoff`; o `SeletorFatos`; o `ValidadorResposta`; o
`ValidadorConsistenciaBase`; o `OrquestradorMotor`; a integração da **etapa 13**; a escolha
de **persistência**; o **limiar**; **S4**/**S5**; e o **destino do alerta**. **Fornecedor,
modelo, SDK, API, biblioteca, formato de transporte e JSON Schema continuam não escolhidos**
(N-b-F3).

**Nota de materialização — fronteira determinística de N-b (M-NB1–M-NB9).** Registro
**factual** da entrega funcional que materializou a **parte determinística** do contrato
N-b/AJ1 em `src/casa77_sdr/interpretation.py`, com testes em
`tests/test_interpretation.py`. **Esta nota não reabre a arbitragem, não altera o contrato,
não cria componente, não cria pendência, não altera nenhum código `E-Nb` ou cenário `K-Nb`
e não cria subetapa.** §4.1 permanece com **14** componentes e §2 com **nove**
responsabilidades.

| # | Materialização |
|---|---|
| M-NB1 | **Superfície pública fechada**, com **três** produtores: `canonicalizar_interpretacao(...)` — valida a entrada recebida e devolve a `Interpretacao` **canônica** ou um erro de contrato; `projetar_para_identidade(...)` — deriva a `ProjecaoInterpretacao`; e `decidir_interesse_confirmar_disponibilidade(...)` — produz a **condição 5**. Nenhum outro produtor público existe, e **nada é exportado em `__init__.py`**. |
| M-NB2 | **`A1` não é entrada semântica** (AJ1-1): a estrutura de entrada **não possui slot de códigos `A1`**. A **presença** dos seis códigos é derivada do payload autoritativo (N-b-X2, N-b-X4) e a **confiança** é **calculada** por **N-b-X3**, sendo apenas **armazenada** na `Interpretacao` canônica para auditabilidade (AJ1-A1b, AJ1-A1c). |
| M-NB3 | A entrada da fronteira é uma representação **pré-canônica mínima** que carrega **somente** o que o produtor não determinístico entrega (AJ1-2) mais o **slot autônomo** fechado nos cinco códigos **A2/B** (AJ1-3). Ela **não é uma segunda `Interpretacao`** e **nenhum formato de transporte é escolhido** (N-b-F3). |
| M-NB4 | **Erros recebíveis** implementados na fronteira: `E-Nb-1`, `E-Nb-2`, `E-Nb-3`, `E-Nb-4`, `E-Nb-5`, `E-Nb-6` **no ramo de intenção autônoma**, `E-Nb-7`, `E-Nb-8`, `E-Nb-9`, `E-Nb-10`, `E-Nb-17` e `E-Nb-18`. A **precedência AJ1** vale: código `A1` no slot autônomo **com** confiança declarada → **`E-Nb-3`**; **sem** confiança → **`E-Nb-5`**. **Nenhuma exceção pública nova** foi criada, e as duas famílias são **distintas**: **tipo runtime incompatível** levanta **`TypeError`**, sem código; **violação de contrato `E-Nb`** levanta **`ValueError`** com o respectivo código no início da mensagem. Assim, **ausência** de confiança onde ela é exigida é `E-Nb-1` — e `confianca_global` ausente é `E-Nb-4` —, enquanto uma confiança de **tipo errado** é `TypeError`. `E-Nb-6` significa **somente código repetido**: a **ordem canônica** de `intencoes_detectadas` é **produzida** deterministicamente, mas **não é exigida** de quem consome, porque ela existe apenas para auditabilidade e não estabelece precedência semântica (AJ1-A1e). |
| M-NB5 | **Invariantes internos** — `E-Nb-6` no ramo `A1` e `E-Nb-11`–`E-Nb-16` — são verificados como **pós-condições** da canonicalização e provados como **propriedade**, não por entrada externa fabricada. **`K-Nb-18` é estrutural**: para toda `Interpretacao` canônica, a confiança `A1` **corresponde a N-b-X3** (AJ1-13a, AJ1-13b). **Nenhuma confiança `A1` independente é aceita** (AJ1-13c). |
| M-NB6 | **Projeção total** para a `ProjecaoInterpretacao` **já existente**, que permanece com **sete** campos (N-b-K1–N-b-K8). A derivação **não aplica C3** — transporta valor e confiança inclusive `BAIXA`. **Nenhuma PII e nenhum texto conversacional atravessam**: `convidados`, `formato`, `nome`, `contato`, `correcoes`, `perguntas_comerciais`, `pedido_de_humano`, `trechos_ambiguos` e `confianca_global` ficam retidos no runtime da `Interpretacao`. |
| M-NB7 | **Condição 5 materializada** como **função total** (N-b-CD1–N-b-CD4), inclusive `None` **sem `Interpretacao`**. O produtor **já estava conceitualmente atribuído** por N-b: esta entrega apenas o **materializa**. É a **única** condição de §4.4 produzida; as condições **2**, **4** e **8** continuam **NÃO ATRIBUÍDAS**. |
| M-NB8 | **`FormatoEvento` reutilizado por import** de `src/casa77_sdr/qualification.py`, que **permanece inalterado** — o enum **não foi movido nem redeclarado** e **nenhum** `shared/domain/types` foi criado (AJ1-F1, AJ1-F2). O módulo é **puro e determinístico**: zero I/O, rede, relógio, persistência, YAML, LLM, fornecedor, SDK, API, cache ou fila; não muta as entradas. **`E-Nb-19` é provado estruturalmente** — superfície pública, tipos de retorno, campos das estruturas, produtores públicos e condição 5 como única condição —, com o fechamento de imports como **evidência complementar**. |
| M-NB9 | **O que continua FORA.** O **produtor não determinístico / LLM da etapa 4 NÃO foi implementado** — não existe adaptador, fornecedor, modelo, SDK, API, JSON Schema, prompt novo nem interpretação de texto livre. **`N-b-RES2` continua ABERTO**: a transformação posterior dos sinais interpretados em **eventos confirmados** segue **sem produtor concreto**, e a etapa 4 **continua proibida de emitir `Exx`** (`N-b-RES1`), com `N-b-RES3` preservado. **A etapa 4 não está operacionalmente integrada**: nada chama esta fronteira no pipeline. O **`OrquestradorMotor` continua não implementado**. **Nenhuma subetapa foi criada — a 3B.8 não existe.** |

#### AJ2 — origem semântica do assunto de `PerguntaComercial` (arbitragem AJ2)

Micro-arbitragem **exclusivamente documental**. **AJ2 ESTENDE FORMALMENTE N-b**: o contrato
vigente da etapa 4 **muda documentalmente** a partir daqui, e a **implementação atual ainda
NÃO materializa esse delta**.

**Estado: ARBITRADA / NÃO MATERIALIZADA.** Nenhum tipo Python é criado ou alterado; nenhum
arquivo de `src/`, `tests/`, `knowledge/` ou `prompts/` é tocado. **§4.1 permanece com 14
componentes** e §2 com **nove** responsabilidades. `IntencaoConversacional` continua com
**exatamente 11** valores, a lista de erros continua **`E-Nb-1`–`E-Nb-19`** e a
`ProjecaoInterpretacao` continua com **sete** campos. **A 3B.8 não existe.**

**O problema que AJ2 fecha.** Hoje a etapa 4 entrega a consulta comercial **apenas como
texto livre**. Qualquer consumidor futuro — o produtor de **S2-D8**, o `SeletorFatos` —
precisaria **reinterpretar esse texto** para saber *sobre o que* o interessado perguntou.
Isso reintroduziria interpretação semântica fora da etapa 4, exatamente onde **P3** e
**N-b-G1** a proíbem. AJ2 fornece o **sinal semântico estruturado** que faltava — e **nada
além disso**.

**Escopo semântico da categoria `PerguntaComercial`.** A designação é técnica, não
gramatical: a categoria cobre **consultas comerciais do interessado**, inclusive **pergunta
interrogativa**, **pedido informacional** e **solicitação de material ou informação
comercial** — quando esse item precisa **futuramente** ser avaliado quanto à existência de
resposta ou conteúdo aprovado. Conceitualmente, tanto "onde fica?" quanto "manda fotos",
"manda o link do mapa" ou "manda o contrato" são consultas comerciais nesse sentido.

**Isso NÃO transforma todo pedido de ação em `PerguntaComercial`.** Os sinais dedicados
permanecem íntegros e **não são substituídos**:

| # | Regra de fronteira |
|---|---|
| AJ2-E1 | `pedido_de_humano`, `INTERESSE_EM_VISITA`, `INTERESSE_CONFIRMAR_DISPONIBILIDADE` e `EXCECAO_SOLICITADA` **continuam sendo os sinais autoritativos** de suas naturezas. |
| AJ2-E2 | Quando a mensagem contém **apenas** o sinal dedicado, **sem consulta comercial distinta**, o sinal **não precisa ser duplicado** como `PerguntaComercial`. |
| AJ2-E3 | Quando **coexistem** um sinal autônomo e uma **consulta comercial distinta**, **ambos podem coexistir** — nenhum suprime o outro. |
| AJ2-E4 | **`Q53` e `Q54` de `tests/perguntas-criticas.md` permanecem questão preexistente não resolvida.** AJ2 **não decide** sua classificação. |

##### `AssuntoComercial` — vocabulário conceitual fechado com exatamente 54 valores

`PerguntaComercial` passa **conceitualmente** de dois para **três** campos: `texto`,
`confianca` e **`assunto`**. O `assunto` é **obrigatório**, do tipo **`AssuntoComercial`**, e
**não possui confiança própria**.

Contagem: **53 específicos + 1 de totalidade**. **Nenhum 55º membro** pode ser acrescentado.

| Bloco | # | Código |
|---|---|---|
| **Preço e condição comercial** | 1 | `PRECO_LOCACAO` |
| | 2 | `PRECO_HORA_ADICIONAL` |
| | 3 | `PRECO_VARIACAO_POR_DIA_DA_SEMANA` |
| | 4 | `PRECO_VARIACAO_POR_TEMPORADA` |
| | 5 | `PRECO_SUITE_DA_NOIVA` |
| | 6 | `DESCONTO` |
| | 7 | `PAGAMENTO_E_PARCELAMENTO` |
| | 8 | `CAUCAO` |
| | 9 | `VALIDADE_DA_PROPOSTA` |
| | 10 | `REAJUSTE_DE_PRECO` |
| | 11 | `PARCERIA_OU_PERMUTA` |
| | 12 | `MULTAS_E_PENALIDADES` |
| **Evento, data e contratação** | 13 | `TIPO_DE_EVENTO` |
| | 14 | `DATA_BLOQUEADA` |
| | 15 | `DISPONIBILIDADE_DE_DATA` |
| | 16 | `CAPACIDADE_MAXIMA_E_FORMATO` |
| | 17 | `CAPACIDADE_MINIMA` |
| | 18 | `HORARIO_LIMITE_E_DURACAO` |
| | 19 | `MONTAGEM_E_DESMONTAGEM` |
| | 20 | `CONTRATACAO` |
| | 21 | `CANCELAMENTO` |
| | 22 | `ALTERACAO_DE_DATA` |
| **Espaço e estrutura** | 23 | `LOCALIZACAO` |
| | 24 | `ESTACIONAMENTO` |
| | 25 | `ACESSIBILIDADE` |
| | 26 | `BANHEIROS` |
| | 27 | `COZINHA` |
| | 28 | `SUITE_DA_NOIVA` |
| | 29 | `MOBILIARIO` |
| | 30 | `CLIMATIZACAO` |
| | 31 | `ESPACO_INFANTIL` |
| | 32 | `COBERTURA_E_PLANO_DE_CHUVA` |
| | 33 | `SOM_E_ILUMINACAO` |
| | 34 | `GERADOR_E_ENERGIA` |
| **Inclusão, fornecedor e restrição** | 35 | `ITENS_INCLUSOS` |
| | 36 | `EQUIPE_E_LIMPEZA` |
| | 37 | `FORNECEDOR_PROPRIO` |
| | 38 | `FORNECEDOR_RECOMENDADO` |
| | 39 | `RESTRICAO_USO_DE_AREA` |
| | 40 | `RESTRICAO_FOGOS` |
| | 41 | `RESTRICAO_ANIMAIS` |
| | 42 | `RESTRICAO_VELAS` |
| | 43 | `RESTRICAO_DRONES` |
| | 44 | `RESTRICAO_DECORACAO` |
| **Processo, prazo e material** | 45 | `VISITA` |
| | 46 | `PRAZO_DE_RETORNO` |
| | 47 | `HORARIO_DE_ATENDIMENTO` |
| | 48 | `MATERIAL_FOTOS` |
| | 49 | `MATERIAL_VIDEOS` |
| | 50 | `MATERIAL_PLANTA` |
| | 51 | `MATERIAL_PORTFOLIO` |
| | 52 | `MATERIAL_APRESENTACAO_COMERCIAL` |
| | 53 | `LINK_DE_MAPA` |
| **Totalidade** | 54 | `ASSUNTO_NAO_CLASSIFICADO` |

Os nomes acima são **categorias semânticas**, não valores comerciais: nenhum deles carrega
preço, capacidade, horário, prazo, condição, endereço ou texto de resposta.

##### `ASSUNTO_NAO_CLASSIFICADO` — totalidade sem aproximação

Representa **três** situações: tema legítimo **ainda não contemplado** pelo vocabulário;
**ambiguidade real** entre membros; e **impossibilidade de atribuir** membro específico com
segurança.

**Nunca escolher "o mais próximo".** Aproximar é fabricar classificação.

| # | O que `ASSUNTO_NAO_CLASSIFICADO` **é** e **não é** |
|---|---|
| AJ2-N1 | **é** valor legítimo do vocabulário |
| AJ2-N2 | **não** é erro de contrato |
| AJ2-N3 | **não** é confiança `BAIXA` |
| AJ2-N4 | **não** é ausência |
| AJ2-N5 | **não** é `TrechoAmbiguo` |

`TrechoAmbiguo` **pode coexistir** com ele, mas continua **exclusivamente diagnóstico**
(N-b-T2, N-b-T3).

**AJ2 não antecipa S2-D8.** `ASSUNTO_NAO_CLASSIFICADO` **não implica**, por si só, ausência
de `Rxx`, `resposta_aprovada_disponivel = false`, `E09`, `pendencia_impeditiva`, `R03` nem
handoff. **AJ2 não decide isso.** **S2-D8 decidirá futuramente o tratamento de
`ASSUNTO_NAO_CLASSIFICADO`.**

##### Regras de `PerguntaComercial` após AJ2 — `N-b-Q7` a `N-b-Q12`

`N-b-Q1` recebe **ampliação mínima**; `N-b-Q2`–`N-b-Q6` permanecem **inalteradas**.

| # | Regra |
|---|---|
| N-b-Q7 | `PerguntaComercial` tem **três** campos: `texto`, `confianca` e `assunto`. O `assunto` é **obrigatório**, pertence ao **enum fechado** `AssuntoComercial` e **não possui confiança própria**. A cardinalidade da coleção continua **0..N**. |
| N-b-Q8 | **Exatamente 1 assunto por `PerguntaComercial`.** Consulta **composta** é **segmentada** em múltiplas `PerguntaComercial`, uma por assunto. |
| N-b-Q9 | **Preservação textual.** O `texto` é o **trecho correspondente quando isolável** e o **texto integral quando não isolável**. **Nunca** normalizar, resumir ou parafrasear — e **nunca** exigir unicidade de texto. |
| N-b-Q10 | **Totalidade por `ASSUNTO_NAO_CLASSIFICADO`**, **sem aproximação**: o vocabulário é total porque tem o membro de totalidade, não porque cobre tudo especificamente. |
| N-b-Q11 | **Duplicatas exatas são PERMITIDAS.** Nenhum `id`, posição, *offset* ou número de ocorrência é criado, e **nenhum `E-Nb` novo** é introduzido por duplicidade. |
| N-b-Q12 | O `assunto` **não atravessa** para a `ProjecaoInterpretacao`, **não referencia `Rxx`** e **não produz condição** de §4.4. |

**Confiança.** O `assunto` **não possui confiança própria**: **`N-b-Q2`/`N-b-Q3` permanecem o
filtro único** de efetividade. Consequência direta e **válida**: uma `PerguntaComercial`
`ALTA` **pode** ter `assunto = ASSUNTO_NAO_CLASSIFICADO` — a consulta é efetiva e o tema é
que não foi classificável. **Não usar `TrechoAmbiguo` como substituto** dessa situação.

##### Erros — a lista continua `E-Nb-1` a `E-Nb-19`

**Nenhum código `E-Nb` novo é criado** — a lista **não ganha um vigésimo código**. `E-Nb-5` é
**ampliado** para incluir, além do que já cobre:

| # | Ampliação de `E-Nb-5` |
|---|---|
| AJ2-X1 | `assunto` **ausente** em uma `PerguntaComercial`. |
| AJ2-X2 | valor de `assunto` **fora do vocabulário** `AssuntoComercial`. |

`ASSUNTO_NAO_CLASSIFICADO` **NÃO gera `E-Nb-5`** — é membro legítimo (AJ2-N1).

A **família `TypeError`** vigente é **preservada** para incompatibilidade de tipo em runtime,
conforme já fixado em **M-NB4**: tipo errado levanta `TypeError` **sem código**; violação de
contrato levanta `ValueError` com o código `E-Nb`. **Nenhum formato de transporte é
escolhido** e **nenhuma representação externa é inventada** (N-b-F3).

##### Ajuste em AJ1

| # | Ajuste |
|---|---|
| AJ2-AJ1a | **AJ1-2** passa a valer com `perguntas_comerciais` cujos itens **incluem `assunto`**: cada `PerguntaComercial` entregue pelo produtor não determinístico passa a incluir o assunto. |
| AJ2-AJ1b | Na **classificação AJ1 dos erros**, registra-se **somente** que a amplitude de `E-Nb-5` passa a incluir `AssuntoComercial`. **Nenhum código muda de classe.** |

**As demais decisões de AJ1 são preservadas integralmente** — AJ1-1, AJ1-3, AJ1-4, AJ1-5, o
bloco A1 canônico, a precedência `E-Nb-3` × `E-Nb-5` no slot autônomo, `AJ1-13a`–`AJ1-13c`,
os invariantes `E-Nb-11`–`E-Nb-16`, a estratégia estrutural de `E-Nb-19` e `AJ1-F1`/`AJ1-F2`.
**Nenhum código novo.**

##### Identidade e projeção — inalteradas

A `ProjecaoInterpretacao` continua com **exatamente sete** campos e `N-b-K1`–`N-b-K8`
permanecem. **`N-b-K8` já retém `perguntas_comerciais` inteira**; como o `assunto` está
**dentro** de `perguntas_comerciais`, ele **também não atravessa** para a identidade.
`src/casa77_sdr/identity.py` **não muda**.

##### Fronteira do produtor — `N-b-F1`–`N-b-F5` preservadas

`AssuntoComercial` é **apenas classificação semântica**. Continuam valendo, sem atenuação:
**um único produtor semântico**; **uma única chamada**; **zero segundo LLM**; **zero YAML**;
**zero `knowledge/respostas-aprovadas.md`**; **zero `Rxx`**; **zero `E09`**; **zero
pendência**; **zero handoff decidido na etapa 4**; e **fornecedor, modelo, SDK, API,
biblioteca, formato de transporte e JSON Schema ainda não escolhidos** (N-b-F3).

**`E-Nb-19` — código inalterado, prova estrutural reforçada.** `AssuntoComercial` **não
contém** `Rxx`, caminho YAML, valor comercial, status, condição de ciclo, evento nem
transição. Ele é, por construção, incapaz de violar `E-Nb-19`.

##### Fronteira AJ2 × C e AJ2 × S2-D8

**C-12a–C-12h permanecem inalteradas.** Registra-se **fora de C**:

| # | Fronteira |
|---|---|
| AJ2-C1 | **C não produz `AssuntoComercial`.** |
| AJ2-C2 | `AssuntoComercial` **nasce na etapa 4**, na fronteira do produtor semântico. |
| AJ2-C3 | **AJ2 não materializa C.** C permanece **ARBITRADA / NÃO MATERIALIZADA** (§2.3). |
| AJ2-C4 | **S2-D8 decidirá futuramente** qualquer mapeamento `assunto` → `Rxx` ou `assunto` → fragmento. |

**Nota temporal sobre C-14f.** **C preservou `K-Nb-1`–`K-Nb-40` quando arbitrada**; **AJ2,
posterior, estende a fronteira para `K-Nb-1`–`K-Nb-51`**. As **11** `IntencaoConversacional`
e os erros **`E-Nb-1`–`E-Nb-19`** que C preservou **continuam os mesmos**. A história de C
**não é reescrita**: C-14f descreve corretamente o estado **no momento da arbitragem C**.

**S2-D8 continua ABERTA.** AJ2 **não arbitra** `assunto` → `Rxx`, `assunto` → fragmento,
`E09`, `pendencia_impeditiva`, `resposta_aprovada_disponivel`, composição ou deduplicação
operacional, nem o **produtor** de S2-D8. AJ2 **apenas fornece o sinal semântico estruturado
que faltava** ao futuro consumidor.

##### Cenários — a fronteira passa de `K-Nb-1`–`K-Nb-40` para `K-Nb-1`–`K-Nb-51`

Dos **40** cenários existentes: **34 permanecem literais**; **6 exigirão adaptação de
representação** numa futura materialização, porque constroem `PerguntaComercial`;
**0 são alterados semanticamente** e **0 são substituídos**. **`K-Nb-40` é complementado**
para explicitar que o **`assunto` também não atravessa** para a projeção (N-b-Q12, N-b-K8).

**Onze cenários novos**, conceituais — **nenhum teste Python é criado por esta
micro-arbitragem**:

| # | Caso | Resultado esperado |
|---|---|---|
| K-Nb-41 | `PerguntaComercial` com **assunto específico válido** e confiança `ALTA` | pergunta **efetiva** (N-b-Q2); assunto relatado; **nenhuma** condição de §4.4 produzida (N-b-Q12) |
| K-Nb-42 | `assunto` **fora do vocabulário** `AssuntoComercial` | **erro de contrato `E-Nb-5`** (AJ2-X2); **nenhuma projeção**; a etapa 5 **não executa** |
| K-Nb-43 | `assunto` **ausente** | **erro de contrato `E-Nb-5`** (AJ2-X1) |
| K-Nb-44 | `assunto` com **tipo runtime incompatível** | **política `TypeError` vigente** (M-NB4); **nenhum `E-Nb` novo** |
| K-Nb-45 | `ASSUNTO_NAO_CLASSIFICADO` com confiança `ALTA` | **válido**: pergunta efetiva com tema não classificado; **não** é erro, **não** é `BAIXA`, **não** é ausência (AJ2-N1–AJ2-N4) |
| K-Nb-46 | Pergunta `BAIXA` com **assunto válido** | texto e assunto **preservados para diagnóstico**; **não efetiva** (N-b-Q2, N-b-Q3) |
| K-Nb-47 | **Consulta composta** com dois temas distintos | **segmentada em duas** `PerguntaComercial`, uma por assunto (N-b-Q8); texto de cada uma conforme N-b-Q9 |
| K-Nb-48 | **Mesmo assunto**, textos diferentes | **válido**: duas `PerguntaComercial` distintas |
| K-Nb-49 | **Mesmo texto e mesmo assunto**, duplicados | **válido**: duplicata exata é permitida (N-b-Q11); **nenhum `E-Nb`** |
| K-Nb-50 | **Mesmo texto**, assuntos distintos | **válido**: um assunto por item (N-b-Q8), texto não exige unicidade (N-b-Q9) |
| K-Nb-51 | `ASSUNTO_NAO_CLASSIFICADO` **com** `TrechoAmbiguo` presente | **válido**: coexistem; o trecho continua **exclusivamente diagnóstico** (AJ2-N5, N-b-T2) |

Nenhum cenário `K-Nb` novo exige membro em `Identidade`, critério em `CriterioIdentidade`,
valor em `VeredictoIdentificador`, campo em `ProjecaoInterpretacao` ou componente em §4.1.

##### Impacto FUTURO em `tests/` — registro factual, sem alteração

**Nenhum arquivo de `tests/` é alterado por AJ2.** Registro do estado **verificado
mecanicamente** em `tests/test_interpretation.py` na base desta arbitragem:

| # | Medida verificada |
|---|---|
| AJ2-T1 | **2098** linhas |
| AJ2-T2 | **132** funções `test_*` |
| AJ2-T3 | **14** funções constroem `PerguntaComercial` — **13** testes **+ 1** auxiliar (`_combinacoes_para_propriedade`) |
| AJ2-T4 | **2** testes adicionais exigem edição **sem** construir `PerguntaComercial`, porque suas **asserções passam a ser falsas**: `test_pergunta_comercial_tem_dois_campos`, que fixa a lista de campos da estrutura, e `test_superficie_publica_e_exatamente_a_declarada`, que fixa a superfície pública do módulo |
| AJ2-T5 | **EXIGEM EDIÇÃO DIRETA: 16 funções — 15 testes + 1 auxiliar.** Composição: os **13** testes construtores de AJ2-T3, mais os **2** testes de asserção de AJ2-T4, mais o **1** auxiliar |
| AJ2-T6 | **AFETADOS INDIRETAMENTE, sem edição própria: 3 testes** — `test_k_nb_18_confianca_a1_sempre_corresponde_a_n_b_x3`, `test_pos_condicoes_valem_para_toda_interpretacao_canonica` e `test_intencao_detectada_sempre_tem_confianca_nao_nula` —, que dependem de `_combinacoes_para_propriedade`. **Conjunto disjunto** do de AJ2-T5 |
| AJ2-T7 | **Total amplo de funções impactadas: 19 — 18 testes + 1 auxiliar** (união de AJ2-T5 e AJ2-T6). **"Exige edição" e "afetado indiretamente" não se misturam**: as duas métricas são registradas separadamente |

**A quantidade de funções NOVAS de pytest não é estimada**: a parametrização é **decisão
futura de materialização**, não desta arbitragem.

##### AJ2 × implementação vigente — o delta NÃO está materializado

Distinção obrigatória, para que **M-NB** não seja lido como se o código já tivesse `assunto`:

| | **CONTRATO — após AJ2** | **IMPLEMENTAÇÃO — PR #55, anterior a AJ2** |
|---|---|---|
| `PerguntaComercial` | `texto`, `confianca`, **`assunto`** | `texto`, `confianca` |
| `AssuntoComercial` | vocabulário fechado de **54** valores | **não existe** |
| `E-Nb-5` | inclui `assunto` ausente e fora do vocabulário | não cobre `assunto` |
| cenários | `K-Nb-1`–`K-Nb-51` | `K-Nb-1`–`K-Nb-40` |

| # | Registro |
|---|---|
| AJ2-M1 | **O PR #55 permanece historicamente correto**: ele materializou fielmente o contrato **vigente à época**. |
| AJ2-M2 | **AJ2 ESTENDE o contrato depois dele.** |
| AJ2-M3 | **AJ2 ainda NÃO está materializada.** |
| AJ2-M4 | **`M-NB1`–`M-NB9` descrevem a implementação vigente do PR #55**, e **não** são reescritas por AJ2. |
| AJ2-M5 | O **delta AJ2** — `assunto` em `PerguntaComercial`, o enum `AssuntoComercial`, a ampliação de `E-Nb-5` e os cenários `K-Nb-41`–`K-Nb-51` — está **pendente de materialização futura**, **não autorizada** por esta micro-arbitragem. |

**Fora do escopo de AJ2.** Permanecem **abertas e inalteradas**: **S2-D8**; **S3-D1**;
**E4**; **B**; **C** — arbitrada e **não materializada** (§2.3); `N-b-RES2`; o
`DetectorHandoff`; o `SeletorFatos`; o `ValidadorResposta`; o `ValidadorConsistenciaBase`; o
`OrquestradorMotor`; a integração da **etapa 13**; a escolha de **persistência**; o
**limiar**; **S4**/**S5**; e o **destino do alerta**. As condições **2**, **4** e **8** de
§4.4 continuam **NÃO ATRIBUÍDAS**. `R10`, `R13`, `R17` e `R20` continuam **não decididos**
(C-9), e `Q53`/`Q54` continuam **não classificados** (AJ2-E4). **Nenhuma subetapa foi criada
— a 3B.8 não existe.**

#### Projeção estruturada para a identidade (arbitragem R3)

O `ResolvedorIdentidade` **não recebe esta tabela nem texto conversacional**. Ele recebe uma
**projeção própria**, estruturada e fechada, derivada dela. O campo central é
`IntencaoIdentidade`, com **exatamente três** valores e **nenhum texto livre**:

| `IntencaoIdentidade` | Significado |
|---|---|
| `CONTINUIDADE_DECLARADA` | a mensagem declara tratar do evento já conversado |
| `NOVO_EVENTO_DECLARADO` | a mensagem declara tratar de um evento diferente |
| `NAO_DISCRIMINANTE` | a mensagem não discrimina identidade |

As **intenções genéricas `E02`–`E11` e `E17` não discriminam identidade por si mesmas**:
informar data, perguntar preço ou pedir humano são compatíveis com qualquer candidato e
projetam-se em `NAO_DISCRIMINANTE`.

`IntencaoIdentidade` combina-se com `referencia_evento_anterior` (`COM_REFERENCIA` ×
`SEM_REFERENCIA`), derivando o `Vinculo` declarado. O `Vinculo` tem **exatamente quatro**
valores — `DECLARA_CONTINUIDADE`, `DECLARA_NOVO`, `SEM_DECLARACAO` e
`DECLARACAO_CONTRADITORIA` (correção C1 da arbitragem R5) — e a tabela é **total**: as seis
combinações possíveis têm valor próprio, nenhuma resulta em estado implícito.

| `IntencaoIdentidade` | `referencia_evento_anterior` | `Vinculo` |
|---|---|---|
| `CONTINUIDADE_DECLARADA` | `COM_REFERENCIA` | `DECLARA_CONTINUIDADE` |
| `CONTINUIDADE_DECLARADA` | `SEM_REFERENCIA` | `DECLARA_CONTINUIDADE` |
| `NOVO_EVENTO_DECLARADO` | `SEM_REFERENCIA` | `DECLARA_NOVO` |
| `NOVO_EVENTO_DECLARADO` | `COM_REFERENCIA` | **`DECLARACAO_CONTRADITORIA`** |
| `NAO_DISCRIMINANTE` | `COM_REFERENCIA` | `DECLARA_CONTINUIDADE` |
| `NAO_DISCRIMINANTE` | `SEM_REFERENCIA` | `SEM_DECLARACAO` |

`NOVO_EVENTO_DECLARADO` acompanhado de referência ao evento anterior é **sinal
contraditório**: a mensagem declara evento novo e simultaneamente aponta para o antigo. O
resolvedor **não escolhe um lado** — o par produz `DECLARACAO_CONTRADITORIA`, consumido por
**curto-circuito em D0** (§7.1).

A quinta linha — `NAO_DISCRIMINANTE` + `COM_REFERENCIA` → `DECLARA_CONTINUIDADE` — é a
semântica já arbitrada na R3 e **permanece inalterada**: referência ao evento anterior sem
declaração explícita de novidade é sinal de continuidade, não de contradição.

**`IntencaoIdentidade` permanece com exatamente três valores** — `CONTINUIDADE_DECLARADA`,
`NOVO_EVENTO_DECLARADO`, `NAO_DISCRIMINANTE`. Nenhum quarto valor, nenhuma renomeação: a
correção C1 amplia o `Vinculo`, **não** a intenção.

**Confiança baixa é tratada como ausência.** Um sinal com confiança baixa é projetado como
**ausente / não discriminante** para efeito de identidade — nunca como sinal fraco a ser
ponderado. **Nenhum threshold numérico novo é criado**: a confiança já é binária (§7.1).

#### `SituacaoTakeover` — contrato conceitual (arbitragem R5)

Contrato **exclusivamente documental**; nenhum arquivo de `src/` é criado por esta
arbitragem. Seja **`H`** o conjunto dos atendimentos recuperados para o contato/canal cujo
estado é **`atendimento_humano`**. **Origem formal** (arbitragem R-H): H é produzido pela
**etapa 3** e entregue ao resolvedor como **`ids_em_atendimento_humano: tuple[str, ...]`**
— entrada **separada** do conjunto elegível e **fora** da política N-a; as regras **H1–H6**
que o governam estão em **§6.2**.

| `SituacaoTakeover` | Condição |
|---|---|
| `SEM_TAKEOVER` | `quantidade(H) == 0` |
| `HUMANO_UNICO` | `quantidade(H) == 1` |
| `HUMANO_MULTIPLO` | `quantidade(H) >= 2` |

Exatamente **três** valores. Fronteiras obrigatórias:

| # | Regra |
|---|---|
| K1 | **Não é `Identidade`.** É dimensão **ortogonal**; não existe e nunca existirá `TAKEOVER_HUMANO_*` como membro de `Identidade`. |
| K2 | **Não entra em `CondicoesCiclo`** (§4.4). O contrato de condições consumidas pela `MaquinaEstados` permanece **intocado**. |
| K3 | **Não chega à `MaquinaEstados`.** A máquina continua recebendo `estado` e as condições já existentes — nada é acrescentado à sua entrada. |
| K4 | **Não cria estado**, **não cria evento** (`Exx`) e **não cria transição** (`Txx`). `atendimento_humano`, `E01`, `E13`, `E14`, T31, T33 e T34 permanecem exatamente como estão em doc 06 §3. |

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
| próximo estado | decisão única (I19). Pode ser **"sem transição"** quando a etapa 3 ou a 5 termina o ciclo, nos **quatro** casos de §5: contexto inválido, `Identidade.AMBIGUA`, `SEM_CANDIDATO_ELEGIVEL` enquanto **E4** estiver aberta, e `situacao_takeover == HUMANO_MULTIPLO`. **`HUMANO_UNICO` não está entre eles** — o ciclo segue para a máquina e resolve por T33 |
| `identidade` | `Identidade \| None` — atendimento ativo, mesma solicitação (T36), nova solicitação (T37) ou **ambígua**; `None` quando a cascata conclui `PRIMEIRO_CONTATO_COMPROVADO` ou `SEM_CANDIDATO_ELEGIVEL`, **e também** quando `situacao_takeover != SEM_TAKEOVER` e a cascata não executa (R5, tabela abaixo). Quando ambígua, nenhum dado anterior é herdado ou sobrescrito (§7.1). **`Identidade` permanece com os mesmos quatro membros** — nenhum valor novo é criado no enum |
| `id_atendimento_alvo` | `str \| None` — **qual** atendimento a decisão aponta. Separar o alvo da relação é o que permite `NOVA_SOLICITACAO` e `AMBIGUA` conviverem com alvo `None` sem ambiguidade de leitura |
| `criterio` | `CriterioIdentidade \| None` — **por que** a decisão foi essa, do vocabulário fechado de **12 códigos** de §7.1. **Obrigatório** (um dos 12) quando `situacao_takeover == SEM_TAKEOVER`, porque a cascata executou; **`None`** quando `situacao_takeover != SEM_TAKEOVER`, porque D0–D6 não executaram. **Nenhum código novo é criado para representar essa ausência** — os 12 permanecem os mesmos |
| `situacao_takeover` | `SituacaoTakeover` (§6.3) — **sempre presente**. Campo **ortogonal** a `identidade`: não amplia o enum e não entra em `CondicoesCiclo` |
| fatos autorizados | lista fechada; cada fato com valor, texto, origem (`campo do YAML` ou `Rxx`) e resultado da conferência contra o YAML (F3) |
| divergências de base | lista de `Rxx` em conflito com o YAML detectados neste ciclo (F4); vazia no caso normal |

Os demais campos de auditoria da resolução — `candidatos_avaliados`,
`classificacao_por_candidato`, `vinculo_declarado` e `escopo_restrito_por_identificador` —
estão detalhados em **§7.1**.

**Invariantes de identidade × alvo** (arbitragem R3). A combinação é fechada:

| `criterio` resolve em | `identidade` | `id_atendimento_alvo` |
|---|---|---|
| `ATENDIMENTO_ATIVO` | `ATENDIMENTO_ATIVO` | **obrigatório** |
| `MESMA_SOLICITACAO` | `MESMA_SOLICITACAO` | **obrigatório** |
| `NOVA_SOLICITACAO` | `NOVA_SOLICITACAO` | `None` |
| `AMBIGUA` | `AMBIGUA` | `None` |
| `PRIMEIRO_CONTATO_COMPROVADO` | `None` | `None` |
| `SEM_CANDIDATO_ELEGIVEL` | `None` | `None` |

Qualquer outra combinação é **erro de contrato**. E, com destaque: **`SEM_CANDIDATO_ELEGIVEL`
não autoriza automaticamente `Estado.NOVO`** — identidade `None` ali significa ausência de
alvo, não início de atendimento (doc 06 §4.5, G3/G4/G6).

**Sob takeover** (arbitragem R5), a tabela acima **não se aplica**, porque a cascata não
executou:

| `situacao_takeover` | `identidade` | `id_atendimento_alvo` | `criterio` |
|---|---|---|---|
| `HUMANO_UNICO` | `None` | id do único atendimento em `atendimento_humano` | **`None`** |
| `HUMANO_MULTIPLO` | `None` | `None` | **`None`** |

O tipo permanece **`identidade: Identidade \| None`** — **o enum não é ampliado**. Aqui,
`None` significa **"identidade não calculada por curto-circuito de takeover"**, leitura
distinta dos demais casos documentados:

| `identidade = None` porque… | Distinguido por |
|---|---|
| primeiro contato comprovado | `criterio = PRIMEIRO_CONTATO_COMPROVADO`, `situacao_takeover = SEM_TAKEOVER` |
| histórico conhecido sem candidato elegível | `criterio = SEM_CANDIDATO_ELEGIVEL`, `situacao_takeover = SEM_TAKEOVER` |
| **canal sob controle humano** | `situacao_takeover != SEM_TAKEOVER`, `criterio = None` |

`id_atendimento_alvo` é o campo já existente no contrato R3 e **é mantido** — em
`HUMANO_UNICO` ele aponta o atendimento humano, sem que isso constitua relação de identidade
resolvida.

**Matriz de obrigatoriedade de `criterio`** — fechada e exaustiva:

| Caso | `situacao_takeover` | `criterio` |
|---|---|---|
| `PRIMEIRO_CONTATO_COMPROVADO` | `SEM_TAKEOVER` | **obrigatório** — `PRIMEIRO_CONTATO_COMPROVADO` |
| `SEM_CANDIDATO_ELEGIVEL` | `SEM_TAKEOVER` | **obrigatório** — `SEM_CANDIDATO_ELEGIVEL` |
| resultado normal ou ambíguo da cascata | `SEM_TAKEOVER` | **obrigatório** — um dos 12 |
| `HUMANO_UNICO` | `HUMANO_UNICO` | **`None`** |
| `HUMANO_MULTIPLO` | `HUMANO_MULTIPLO` | **`None`** |

**Nenhum outro caso admite `criterio = None`.** Em particular, `criterio = None` com
`situacao_takeover == SEM_TAKEOVER` é **erro de contrato**: se a cascata executou, ela
decidiu, e toda decisão da cascata tem código.

### 6.5 Saída

| Campo | Conteúdo |
|---|---|
| texto | mensagem final ao interessado, já validada |
| deve responder | falso em `atendimento_humano`, em mensagem duplicada, quando a persistência falhou (§7.2) e **sempre que `situacao_takeover != SEM_TAKEOVER`** (R5) |
| deve fazer handoff | derivado do próximo estado — e só afirmado ao interessado depois de registrado (§7.2) |
| resumo para Douglas | campos do bloco de `docs/04-handoff-humano.md` |
| bloqueios | o que o validador vetou e por quê; inclui divergência de base (F4) |
| **alerta operacional** | evento destinado a quem opera, não a quem conversa: falha de persistência, contexto não recuperado, identificador de atendimento incompatível, estado corrompido, divergência de base, erro inesperado. Sai por caminho separado da conversa |
| logs mínimos | atendimento, estado anterior e final, eventos, motivos, origem de cada fato usado, veredito do validador, se o LLM foi usado, origem da chave de idempotência, como a identidade foi resolvida — sempre sanitizados conforme §6.6 |

Os logs mínimos são o que torna uma resposta auditável depois. Sem a origem de cada fato,
não é possível provar que um valor veio do YAML.

**Sob takeover — o que pode e o que não pode ser afirmado** (arbitragem R5). A âncora é
única: **`deve responder = false` sempre que `situacao_takeover != SEM_TAKEOVER`**. A partir
dela, os limites do que a saída pode declarar:

| `situacao_takeover` | Pode afirmar | **Não pode afirmar** |
|---|---|---|
| `HUMANO_UNICO` | T33 mantém `atendimento_humano`; resposta automática **silenciada**; o eventual motivo foi **preservado** quando aplicável | "Douglas recebeu"; "Douglas foi notificado"; "mensagem entregue"; qualquer afirmação de **entrega física** |
| `HUMANO_MULTIPLO` | processamento pendente **preservado**; **alerta operacional** emitido; **zero emissão automática** | "registrado para o humano"; "entregue"; "recebido"; qualquer **destinatário humano específico** |

O princípio é o mesmo já vigente em §7.2 e em doc 06 §10: **registro não é entrega**. O motor
pode afirmar o que ele próprio fez — silenciar, preservar, alertar — e nunca o que depende de
um terceiro ter recebido.

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
| Extração com baixa confiança | **Caso geral** — itens sujeitos a "`BAIXA` = ausência para consumo estruturado": o campo **não** é registrado, é tratado como **não efetivo**, e aplica-se o comportamento vigente de **permanecer no estado atual e pedir esclarecimento do ponto específico** (doc 06 §7). **Reconciliação N-b** (§6.3): confiança `BAIXA` **não é erro de contrato** — o item **permanece na `Interpretacao` para diagnóstico** e é **não efetivo para consumo estruturado** (N-b-D7, N-b-Q2). **Exceção única, fora do caso geral** — `pedido_de_humano = verdadeiro` com confiança `BAIXA` **permanece sinal efetivo** e **não é governado pela frase "permanecer no estado atual e pedir esclarecimento"**: ele segue **destinado ao futuro `DetectorHandoff`** (N-b-PH3, N-b-PH4). N-b **não emite `E18`**, **não decide transição** e **não implementa regra alguma do `DetectorHandoff`**; a exceção **não** atravessa para a projeção de identidade. |
| Múltiplas intenções | Registrar todas e aplicar a precedência do doc 06 §4. Uma única decisão final. |
| Conflito entre mensagem e estado | Correção explícita sobrescreve e força recálculo (§4 passos 3 e 9). Contradição sem correção explícita → não gravar, pedir confirmação do dado. |
| LLM indisponível | Modo degradado: sem extração nova; usar apenas textos aprovados literais. Se a mensagem exigir interpretação, aplicar R03 + handoff. **Nunca adivinhar.** **Reconciliação N-b** (§6.3, N-b-M1–N-b-M8): **não existe `Interpretacao`** — e **ausência não é `Interpretacao` vazia** (N-b-G8) —, **não existe projeção** para a etapa 5, a `MaquinaEstados` **não é chamada por esse caminho** e `interesse_confirmar_disponibilidade = None`. **Nenhum gatilho de alerta novo é criado**: preservação e alerta seguem os contratos já vigentes de §7 e §7.2. |
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
| **conjunto elegível fechado** de candidatos, já produzido pela etapa 3 | §6.2 |
| **`ids_em_atendimento_humano`** — o conjunto **H**, entrada **própria e separada**, fora de N-a | §6.2, H1–H6 |
| **projeção estruturada** da interpretação | §6.3 |
| tipo de evento | dado extraído × dado registrado no candidato |
| data | dado extraído × dado registrado no candidato |
| referências explícitas ao evento anterior | §6.3 |
| identificador de atendimento **já validado**, quando houver | §6.1.1 |
| **`id_atendimento_validado`** — **ID técnico opaco** do atendimento identificado, presente **somente** com veredito `ENCONTRADO` | §6.2, N-I-1 |
| `havia estado esperado?` | §6.2 |

Assinatura conceitual resultante — **contrato, não implementação**; nenhum arquivo de `src/`
é criado por esta arbitragem:

```text
resolver_identidade(
    candidatos,                    # conjunto elegivel fechado, segundo N-a
    projecao,                      # projecao estruturada da interpretacao
    veredito_identificador,
    id_atendimento_validado,       # str | None — ID tecnico opaco (R-I)
    havia_estado_esperado,
    ids_em_atendimento_humano,     # conjunto H — fora de N-a
)
```

`candidatos` e `ids_em_atendimento_humano` são **parâmetros distintos**. H **não** é derivado
de `candidatos`, e filtrar `candidatos` por estado **não** substitui H: um atendimento em
`atendimento_humano` pode legitimamente estar fora do conjunto elegível (H5).

`id_atendimento_validado` é o **sexto parâmetro** e também **insumo próprio**: `str | None`,
**identificador técnico opaco**, sem **PII**, sem **texto**, sem **dado comercial**, sem
**data** e sem **recência**. Ele **não** substitui o veredito, **não** substitui o conjunto
elegível e **não** é campo de saída.

**Pré-condições estruturais de entrada — P-I1 a P-I5** (arbitragem R-I). Verificadas na
**mesma fronteira conceitual de C2, H4 e H5** — sobre a **entrada**, **antes de R5-P0** e,
portanto, antes de D0–D6. Violação de qualquer uma é **erro de contrato classe II**: o
resolvedor levanta erro e **não devolve identidade alguma**; **nunca** `AMBIGUA`.

| # | Pré-condição |
|---|---|
| P-I1 | `veredito_identificador == NAO_INFORMADO` → `id_atendimento_validado` **deve ser `None`**. ID presente é **erro de contrato classe II**. |
| P-I2 | `veredito_identificador == ENCONTRADO` → `id_atendimento_validado` é **obrigatório e não vazio**. `None` ou vazio é **erro de contrato classe II**. |
| P-I3 | `veredito_identificador` igual a `NAO_ENCONTRADO` ou `INCOMPATIVEL` → **erro de contrato classe II ao alcançar a etapa 5**, **independentemente** do valor de `id_atendimento_validado`. Semântica **já existente** (N5, N6, S3), apenas preservada. |
| P-I4 | `veredito_identificador == ENCONTRADO` → **`havia_estado_esperado == true`** (N-I-3). `false` é **erro de contrato classe II**. **Não existe implicação inversa**: `havia_estado_esperado == true` **não** implica `ENCONTRADO`. |
| P-I5 | `veredito_identificador == ENCONTRADO` → existe **exatamente um** `CandidatoAtendimento` em `candidatos` cujo `id_atendimento == id_atendimento_validado` (N-I-2, N-a-F1). **Zero ocorrências** é **erro de contrato classe II**; **duas ou mais ocorrências** também. Validação **estrutural, antes de R5-P0** — **não** é guarda dentro de D2. |

P-I5 **não institui regra global de unicidade** de `id_atendimento` entre candidatos: exige
unicidade **apenas do ID identificado** e **apenas** quando o veredito é `ENCONTRADO`.
Duplicatas entre candidatos **não identificados** permanecem **questão residual não
decidida** (§12) — não são corrigidas silenciosamente aqui.

O componente é **puro e determinístico** (arbitragem R3): **zero I/O, zero rede, zero LLM,
zero YAML, zero relógio**. Ele **não** calcula elegibilidade, **não** calcula recência,
**não** consulta persistência, **não** interpreta texto, **não** cria atendimento, **não**
persiste, **não** aplica transição e **não** altera a `MaquinaEstados`. Dadas as mesmas
entradas, produz sempre a mesma decisão.

Resultados possíveis — **seis**: `ATENDIMENTO_ATIVO`, `MESMA_SOLICITACAO` (T36),
`NOVA_SOLICITACAO` (T37), `AMBIGUA`, `PRIMEIRO_CONTATO_COMPROVADO` (identidade `None`) e
`SEM_CANDIDATO_ELEGIVEL` (identidade `None`) — todos alcançados **somente quando
`situacao_takeover == SEM_TAKEOVER`**. O enum **`Identidade` permanece com quatro membros**:
os dois últimos resultados são expressos por `identidade = None` distinguidos pelo
`criterio`, não por membros novos. Sob takeover (R5-P0, adiante) a cascata **não executa** e
`identidade = None` decorre de curto-circuito, distinguido por `situacao_takeover` — também
sem membro novo.

#### Contratos locais do `ResolvedorIdentidade` (arbitragem R3)

Contratos **conceituais** — nenhum arquivo de `src/` é criado por esta arbitragem.

**`CandidatoAtendimento`** — um elemento do conjunto elegível:

| Campo | Tipo | Observação |
|---|---|---|
| `id_atendimento` | `str` | identificador do candidato |
| `estado` | `Estado` | um dos oito valores do doc 06 §1.1 |
| `tipo_evento_registrado` | `str \| None` | como **registrado** no candidato; `None` quando não coletado |
| `data_nomeada_registrada` | `str \| None` | valor **nominal** registrado; `None` quando não coletado |

Nenhum outro campo do atendimento entra: **sem nome, sem telefone, sem mensagem, sem preço,
sem capacidade, sem número de convidados, sem formato**.

**`VeredictoIdentificador`** — resultado da validação de §6.1.1:

| Valor | Significado |
|---|---|
| `NAO_INFORMADO` | identificador não foi fornecido — situação normal (N1) |
| `ENCONTRADO` | fornecido, encontrado e compatível com canal e contato |
| `NAO_ENCONTRADO` | fornecido e não encontrado |
| `INCOMPATIVEL` | fornecido e apontando para atendimento de outro contato |

O enum permanece com **exatamente quatro valores**: a arbitragem R-I **não cria um quinto**
(não existe `IDENTIFICADOR_VALIDADO` nem equivalente). O ID validado viaja em **campo
próprio** — `id_atendimento_validado` — e nunca como valor de veredito.

`NAO_ENCONTRADO` e `INCOMPATIVEL` **normalmente já foram bloqueados na etapa 3** (N5, N6,
S3). Se alcançarem a etapa 5, são **erro de contrato defensivo** — o resolvedor levanta
erro e **não devolve identidade alguma**; nunca os trata como caso de negócio.

**Projeção da interpretação** — os campos que o resolvedor recebe de §6.3:

| Campo | Domínio |
|---|---|
| `intencao_identidade` | `CONTINUIDADE_DECLARADA` \| `NOVO_EVENTO_DECLARADO` \| `NAO_DISCRIMINANTE` |
| `referencia_evento_anterior` | presente \| ausente |
| `confianca_referencia` | `ALTA` \| `BAIXA` |
| `tipo_evento_extraido` | `str \| None` |
| `confianca_tipo` | `ALTA` \| `BAIXA` |
| `data_nomeada_extraida` | `str \| None` |
| `confianca_data` | `ALTA` \| `BAIXA` |

Regras de confiança, sem nenhum limiar numérico novo:

| # | Regra |
|---|---|
| C1 | A confiança é **binária**: `ALTA` ou `BAIXA`. **Nenhum threshold numérico** é definido aqui. |
| C2 | **Valor presente sem confiança declarada é erro de contrato**, não valor com confiança implícita. |
| C3 | Confiança `BAIXA` → o campo é **tratado como ausente** para efeito de identidade. Não é sinal fraco ponderado: é ausência. |

#### Comparação nominal por candidato

A comparação é **exclusivamente nominal**. **Sem score, sem similaridade, sem sinônimo, sem
interpretação semântica e sem threshold numérico novo.** Duas comparações, cada uma com três
valores:

| Comparação | Valores |
|---|---|
| `comparacao_tipo` | `IGUAL` \| `DIFERENTE` \| `INDETERMINADO` |
| `comparacao_data` | `IGUAL` \| `DIFERENTE` \| `INDETERMINADO` |

| # | Regra |
|---|---|
| P1 | `INDETERMINADO` sempre que **qualquer um dos lados** estiver ausente — extraído ausente, registrado ausente, ou confiança `BAIXA` (C3). |
| P2 | Igualdade **nominal normalizada**, seguindo o precedente das regras de normalização já existentes: **caixa**, **espaços** e **acentos**. Nada além disso. |
| P3 | A data é comparada como **valor nominal**. O resolvedor **não parseia calendário**, não resolve um nome de mês contra uma data em formato ISO, não calcula proximidade e não usa relógio. |
| P4 | O resolvedor **não normaliza YAML nem consulta a base**: compara o que recebeu contra o que o candidato tem registrado. |

Classificação de cada candidato — tabela **fechada e exaustiva** das nove combinações:

| `comparacao_tipo` | `comparacao_data` | Classe |
|---|---|---|
| `IGUAL` | `IGUAL` | `CORROBORADO` |
| `IGUAL` | `INDETERMINADO` | `CORROBORADO` |
| `INDETERMINADO` | `IGUAL` | `CORROBORADO` |
| `IGUAL` | `DIFERENTE` | `CONTRADITORIO` |
| `INDETERMINADO` | `DIFERENTE` | `CONTRADITORIO` |
| `INDETERMINADO` | `INDETERMINADO` | `NEUTRO` |
| `DIFERENTE` | `IGUAL` | `EXCLUIDO` |
| `DIFERENTE` | `DIFERENTE` | `EXCLUIDO` |
| `DIFERENTE` | `INDETERMINADO` | `EXCLUIDO` |

**Somente tipo de evento divergente exclui** um candidato. Data divergente com tipo igual ou
indeterminado produz `CONTRADITORIO` — o candidato continua no conjunto e será tratado pela
cascata, não descartado silenciosamente.

#### Cascata determinística D0–D6

Definições sobre o **escopo corrente** `E` — inicialmente o conjunto elegível recebido:

| Símbolo | Definição |
|---|---|
| `total_escopo` | quantidade de candidatos em `E` |
| **válido** | candidato cuja classe é **diferente de `EXCLUIDO`** |
| **ativo** | candidato cujo `estado` é **diferente de `encerrado`** |
| `corroborados` | candidatos em `E` com classe `CORROBORADO` |
| `validos` | candidatos válidos em `E` |
| `ativos_validos` | candidatos válidos **e** ativos |
| `encerrados_validos` | candidatos válidos **e** encerrados |
| `ativos_excluidos` | candidatos ativos com classe `EXCLUIDO` |

**Precedência de takeover — antes de D0** (arbitragem R5). A cascata só é alcançada quando o
canal não está sob controle humano:

```text
R5-P0 — precedencia de takeover (antes da restricao por identificador e antes de D0)
    determinar situacao_takeover                 # §6.3, sobre H = ids_em_atendimento_humano
    se situacao_takeover == HUMANO_UNICO:
        identidade = None                        # nao calculada
        alvo       = o unico id de ids_em_atendimento_humano   # direto de H, nao dos candidatos
        preservar evidencia estruturada para auditoria
        NAO executar D0-D6
        # a futura chamada da MaquinaEstados recebe estado = atendimento_humano
        # e CondicoesCiclo.identidade = None; E01 segue por T33; zero emissao
    se situacao_takeover == HUMANO_MULTIPLO:
        identidade = None                        # nao calculada
        alvo       = None
        NAO executar D0-D6
        NAO chamar MaquinaEstados
        encerrar o ciclo na etapa 5 sem transicao
        preservar processamento pendente + alerta operacional; zero emissao
        # nao escolher entre os atendimentos; nao usar recencia para desempatar
    se situacao_takeover == SEM_TAKEOVER:
        prosseguir para D0
```

Consequência sobre a ambiguidade: **A1–A7 só operam quando
`situacao_takeover == SEM_TAKEOVER`**. Sob takeover, `AMBIGUA` **não é produzida pela
cascata**, simplesmente porque D0–D6 não executam — não há esclarecimento a pedir enquanto o
humano controla o canal.

Pseudocódigo normativo da cascata. A ordem **D0 → D6 é obrigatória**; a primeira regra que
decide encerra a cascata.

```text
D0 — sinais contraditorios
    se vinculo == DECLARACAO_CONTRADITORIA:      # NOVO_EVENTO_DECLARADO + COM_REFERENCIA
        identidade = AMBIGUA
        alvo       = None
        criterio   = AMBIGUIDADE_SINAIS_CONTRADITORIOS

D1 — escopo vazio
    se total_escopo == 0:
        se havia_estado_esperado == false:
            identidade = None
            alvo       = None
            criterio   = PRIMEIRO_CONTATO_COMPROVADO
        senao:
            identidade = None
            alvo       = None
            criterio   = SEM_CANDIDATO_ELEGIVEL

D2 — identificador restringe (nunca decide)
    se veredito_identificador == ENCONTRADO:
        se existe candidato FORA do identificado com classe CORROBORADO
           e o identificado NAO e CORROBORADO:
            identidade = AMBIGUA
            alvo       = None
            criterio   = AMBIGUIDADE_SINAIS_CONTRADITORIOS
        senao:
            E = { apenas o candidato identificado }
            escopo_restrito_por_identificador = true
            recalcular todos os contadores sobre E
            prosseguir para D3

D3 — evento novo declarado
    se vinculo == DECLARA_NOVO:
        se existe pelo menos um candidato ATIVO no escopo
           — inclusive se sua classe for EXCLUIDO:
            identidade = AMBIGUA
            alvo       = None
            criterio   = AMBIGUIDADE_DIVERGENCIA_EM_ATENDIMENTO_ATIVO
        senao:
            identidade = NOVA_SOLICITACAO
            alvo       = None
            criterio   = NOVO_EVENTO_DECLARADO

D4 — ancora coincidente
    se corroborados == 1:
        alvo     = o unico CORROBORADO
        criterio = ANCORA_COINCIDENTE_UNICA
    se corroborados >= 2:
        identidade = AMBIGUA
        alvo       = None
        criterio   = AMBIGUIDADE_MULTIPLOS_COMPATIVEIS
    se corroborados == 0:
        continuar

D5 — continuidade declarada, sem ancora
    se corroborados == 0 e vinculo == DECLARA_CONTINUIDADE:
        se validos == 1:
            alvo     = o unico candidato nao EXCLUIDO
            criterio = CONTINUIDADE_DECLARADA_CANDIDATO_UNICO
        senao:
            identidade = AMBIGUA
            alvo       = None
            criterio   = AMBIGUIDADE_SINAIS_INSUFICIENTES

D6 — sem declaracao: inercia do atendimento ativo
    se corroborados == 0 e vinculo == SEM_DECLARACAO:
        se ativos_validos == 1:
            alvo     = o unico ativo valido
            criterio = INERCIA_ATENDIMENTO_ATIVO
        senao se ativos_validos >= 2:
            identidade = AMBIGUA
            alvo       = None
            criterio   = AMBIGUIDADE_MULTIPLOS_ATIVOS
        senao se ativos_excluidos >= 1:
            identidade = AMBIGUA
            alvo       = None
            criterio   = AMBIGUIDADE_DIVERGENCIA_EM_ATENDIMENTO_ATIVO
        senao se encerrados_validos == 0:
            identidade = NOVA_SOLICITACAO
            alvo       = None
            criterio   = TODOS_CANDIDATOS_DIVERGENTES
        senao:
            identidade = AMBIGUA
            alvo       = None
            criterio   = AMBIGUIDADE_SINAIS_INSUFICIENTES

RELACAO — aplicada depois que um alvo foi determinado (D4, D5 ou D6)
    se estado(alvo) != encerrado:
        identidade = ATENDIMENTO_ATIVO
    senao:
        identidade = MESMA_SOLICITACAO          # T36

FECHAMENTO
    qualquer combinacao valida nao coberta acima:
        identidade = AMBIGUA
        alvo       = None
        criterio   = AMBIGUIDADE_SINAIS_INSUFICIENTES
```

**Efeito da arbitragem R-I sobre a cascata — nenhuma alteração normativa.** A cascata é
**preservada integralmente**; o que muda é apenas o que a entrada já garante antes dela:

| Ponto | Efeito |
|---|---|
| **R5-P0** | **intacto**. A precedência de takeover continua **antes** da restrição por identificador e **antes de D0**. As pré-condições **P-I1–P-I5** são verificadas **sobre a entrada**, antes de R5-P0: entrada malformada **nunca alcança** R5-P0 nem D0. |
| **D0** | **sem mudança**. |
| **D1** | **texto sem mudança**; os **dois ramos permanecem exatamente como estão**. Consequência **derivada**, não regra nova: D1 passa a ser alcançável com escopo vazio **somente** quando `veredito_identificador == NAO_INFORMADO`, porque um `ENCONTRADO` válido precisa satisfazer **P-I5**, que exige um candidato no escopo. |
| **D2** | **nenhuma guarda de pertinência é acrescentada** — a existência e a unicidade do candidato identificado já foram garantidas por **P-I5**, na entrada. Fica apenas **explícito** que "o candidato identificado" é o **único** candidato cujo `id_atendimento == id_atendimento_validado`. O teste de corroboração alheia, o ramo de ambiguidade, o ramo de restrição, o recálculo dos contadores e a passagem a D3 permanecem **inalterados**. |
| **D3–D6**, **RELACAO**, **FECHAMENTO** | **sem mudanças**. |

Leitura das decisões estruturais da cascata:

| # | Regra |
|---|---|
| R0 | **A precedência de takeover (R5-P0) vem antes de D0.** Enquanto o canal está sob controle humano, não há resolução de referente a executar. |
| R1 | **D0 vem antes de tudo na cascata.** Contradição declarada não é resolvida por contagem de candidatos. |
| R2 | **O identificador restringe, não decide** (D2, N7). Ele reduz o escopo a um candidato e a cascata continua normalmente sobre ele — inclusive podendo resultar em `AMBIGUA` ou `MESMA_SOLICITACAO`. Quando outro candidato está corroborado e o identificado não está, o conflito é **ambiguidade**, não preferência pelo identificador. |
| R3 | **D3 protege atendimento ativo.** Declarar evento novo havendo atendimento ativo no escopo — mesmo excluído por tipo divergente — é ambiguidade, não abertura automática. O caso permanece aberto como **E3**. |
| R4 | **Somente `NEUTRO`/`CONTRADITORIO`/`CORROBORADO` seguem na cascata.** `EXCLUIDO` sai de `validos`, mas ainda conta em `ativos_excluidos` (D6) — é o que impede ignorar um atendimento ativo divergente. |
| R5 | **Nenhum score.** Toda a cascata é contagem inteira sobre classes de vocabulário fechado. |
| R6 | **A relação é derivada do estado do alvo**, nunca escolhida: ativo → `ATENDIMENTO_ATIVO`; encerrado → `MESMA_SOLICITACAO`. |
| R7 | **O fechamento é conservador**: o não previsto resolve em `AMBIGUA`, jamais em continuidade presumida. |

**Nota sobre `DECLARACAO_CONTRADITORIA`** (correção C1 da R5). D0 passou a testar o
**valor total** `vinculo == DECLARACAO_CONTRADITORIA`, em vez de um predicado parcial
paralelo. Esse valor é **consumido por curto-circuito em D0** e **não cria
`CriterioIdentidade` adicional**: o critério continua sendo
`AMBIGUIDADE_SINAIS_CONTRADITORIOS`. **Os 12 códigos permanecem exatamente os mesmos** e
**nenhuma decisão D1–D6 muda** — a alteração é de representação do vínculo, não de
comportamento da cascata.

#### `CriterioIdentidade` — vocabulário fechado de 12 códigos

| # | Código | Resolve em |
|---|---|---|
| 1 | `PRIMEIRO_CONTATO_COMPROVADO` | identidade `None`, alvo `None` |
| 2 | `SEM_CANDIDATO_ELEGIVEL` | identidade `None`, alvo `None` |
| 3 | `NOVO_EVENTO_DECLARADO` | `NOVA_SOLICITACAO`, alvo `None` |
| 4 | `ANCORA_COINCIDENTE_UNICA` | alvo definido → `ATENDIMENTO_ATIVO` ou `MESMA_SOLICITACAO` |
| 5 | `CONTINUIDADE_DECLARADA_CANDIDATO_UNICO` | alvo definido → `ATENDIMENTO_ATIVO` ou `MESMA_SOLICITACAO` |
| 6 | `INERCIA_ATENDIMENTO_ATIVO` | alvo definido → `ATENDIMENTO_ATIVO` |
| 7 | `TODOS_CANDIDATOS_DIVERGENTES` | `NOVA_SOLICITACAO`, alvo `None` |
| 8 | `AMBIGUIDADE_SINAIS_CONTRADITORIOS` | `AMBIGUA`, alvo `None` |
| 9 | `AMBIGUIDADE_DIVERGENCIA_EM_ATENDIMENTO_ATIVO` | `AMBIGUA`, alvo `None` |
| 10 | `AMBIGUIDADE_MULTIPLOS_COMPATIVEIS` | `AMBIGUA`, alvo `None` |
| 11 | `AMBIGUIDADE_MULTIPLOS_ATIVOS` | `AMBIGUA`, alvo `None` |
| 12 | `AMBIGUIDADE_SINAIS_INSUFICIENTES` | `AMBIGUA`, alvo `None` |

**Não existe o critério `IDENTIFICADOR_VALIDADO`.** O identificador não é razão de decisão —
é restrição de escopo, e sua rastreabilidade é o booleano
`escopo_restrito_por_identificador`. Criar um critério com esse nome seria afirmar
continuidade provada pelo identificador, o que **N4** e **N7** proíbem.

#### Saída auditável

| Campo | Tipo | Conteúdo |
|---|---|---|
| `identidade` | `Identidade \| None` | a relação; `None` nos critérios 1 e 2, e também sob takeover (R5-P0), quando a cascata não executa |
| `id_atendimento_alvo` | `str \| None` | o alvo, quando existe |
| `criterio` | `CriterioIdentidade \| None` | **um dos 12** quando D0–D6 executaram; **`None`** quando o takeover curto-circuitou a cascata (R5-P0). `None` com `situacao_takeover == SEM_TAKEOVER` é **erro de contrato** |
| `candidatos_avaliados` | `tuple[str, ...]` | ids dos candidatos que compuseram o escopo avaliado |
| `classificacao_por_candidato` | `tuple[tuple[str, Classe], ...]` | par (id, classe) por candidato |
| `vinculo_declarado` | `Vinculo` | `DECLARA_CONTINUIDADE` \| `DECLARA_NOVO` \| `SEM_DECLARACAO` \| `DECLARACAO_CONTRADITORIA` |
| `situacao_takeover` | `SituacaoTakeover` | `SEM_TAKEOVER` \| `HUMANO_UNICO` \| `HUMANO_MULTIPLO` (§6.3). Sob takeover os demais campos de cascata ficam vazios, porque D0–D6 não executaram |
| `escopo_restrito_por_identificador` | `bool` | se D2 restringiu o escopo |

**Estabilidade da saída sob a arbitragem R-I.** A saída continua com **exatamente oito
campos** — **nenhum campo de saída novo** é criado. `id_atendimento_validado` é **insumo**,
nunca saída. `escopo_restrito_por_identificador` continua **booleano** e é `true`
**somente** quando **D2 executou efetivamente** o ramo `E = { identificado }`; é `false`
com `NAO_INFORMADO`, sob takeover, quando **D0** decidiu e no **ramo ambíguo de D2**.

A saída **não contém**: nome, telefone, mensagem completa ou qualquer trecho conversacional,
preço, capacidade, número de convidados e formato. **Nenhum texto livre.** Ela é suficiente
para reconstruir a decisão em auditoria — quais candidatos existiam, como cada um foi
classificado, que vínculo foi declarado e qual regra decidiu — sem carregar dado pessoal nem
dado comercial, coerente com §6.6.

#### Erro × ambiguidade — três classes distintas

| Classe | Situação | Comportamento |
|---|---|---|
| **I — pré-condição da etapa 3** | contexto ausente, corrompido, ou identificador inexistente/incompatível — e, pela arbitragem **N-a**, também **marco temporal exigido ausente**, **limiar temporal ausente ou inválido** e **projeção incoerente do registro recuperado** (**S9–S11**) | o `ResolvedorIdentidade` **não é executado** (S7). Bloqueio, mensagem preservada, alerta |
| **II — erro de contrato** | entrada malformada: valor presente sem confiança (C2), veredito `NAO_ENCONTRADO`/`INCOMPATIVEL` alcançando a etapa 5, combinação identidade × alvo fora dos invariantes de §6.4, **ID duplicado em `ids_em_atendimento_humano`** (H4), **violação de H5** — candidato elegível em `atendimento_humano` ausente de H — e **violação de `P-I1`, `P-I2`, `P-I4` ou `P-I5`** (arbitragem R-I); o veredito `NAO_ENCONTRADO`/`INCOMPATIVEL` já citado **é** o caso de **`P-I3`** | erro conceitual do tipo `TypeError`/`ValueError`. **Nenhuma identidade é devolvida.** Não é caso de negócio |
| **III — ambiguidade legítima** | os sinais existem mas não determinam o alvo | `Identidade.AMBIGUA`, alvo `None`, **nada herdado** (A1–A7). É resultado normal, não falha |

**`SEM_CANDIDATO_ELEGIVEL` não pertence a nenhuma das três**: não é erro, não é ambiguidade
e não é primeiro contato. É um **quarto desfecho** — resolução concluída sem alvo, com
histórico conhecido — cujo tratamento a jusante está **bloqueado pela pendência E4**
(doc 06 §4.5, G1–G7).

**A semântica de `SEM_CANDIDATO_ELEGIVEL` é preservada pela arbitragem R-I e não é
reutilizada para "identificado ausente".** Ele continua significando **histórico conhecido +
zero candidatos elegíveis** e, por **consequência** das pré-condições, só é alcançável com
`veredito_identificador == NAO_INFORMADO` (P-I2 e P-I5). Identificado **ausente** do conjunto
elegível **não** é `SEM_CANDIDATO_ELEGIVEL`: é **erro de contrato classe II** por **P-I5**.
**E4 continua aberta** (§12).

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
| S9 | **Marco temporal exigido e ausente** (arbitragem N-a): candidato `encerrado` que precisa de recência sem `instante_ultima_transicao` é **erro de integridade do contexto da etapa 3** — bloqueio, mensagem preservada, alerta operacional, `ResolvedorIdentidade` **não chamado** (§6.2, N-a-R1). **Não** é `N-I-4`, que permanece específico à projeção coerente do identificador validado. |
| S10 | **Limiar temporal ausente, de tipo inválido ou não positivo** é **erro de contrato da configuração** da etapa 3 → mesmo tratamento de bloqueio. Verificado **sempre**, inclusive quando o ciclo não possui candidato `encerrado` (§6.2, N-a-L4, N-a-L5). |
| S11 | **Projeção incoerente do registro recuperado**: `estado_conversa` `None` ou fora dos oito valores, ou `tipo_evento`/`data_nomeada` **presentes com valor não textual** → **contexto corrompido → bloqueio** (§6.2, N-a-P1, N-a-P4). |

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
| Q9 | **Geração e persistência do resumo**: o resumo é **gerado** (`E12`) antes da persistência quando necessário; a etapa 13 persiste a decisão final; a etapa 14 **tenta a entrega do resumo e só depois emite a mensagem de encaminhamento** ao interessado (doc 06 §10). `encaminhado_humano` significa handoff **registrado**, não confirmação física de recebimento. |
| Q10 | **Falha de entrega do resumo**: não reverte o estado já registrado; preserva o processamento pendente de forma **opaca**; emite alerta operacional; **não inventa** fila, retentativa, contador, status de entrega, canal nem provedor; e **não permite processar novo ciclo** que dependa do handoff como operacionalmente concluído enquanto a pendência não for resolvida. O `ProcessamentoPendente` atual **não ganha campos**. |

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
| `OrquestradorMotor` | executa as **14 etapas na ordem**, com **recuperação de contexto (3) antes da interpretação (4) e ambas antes da resolução de identidade (5)**; **estado enviado pelo adaptador é ignorado ou rejeitado** (E3); não emite antes de persistir (Q1); **termina o ciclo sem transição** nos **quatro** casos normativos — contexto inválido, `Identidade.AMBIGUA`, `SEM_CANDIDATO_ELEGIVEL` enquanto **E4** estiver aberta, e `situacao_takeover == HUMANO_MULTIPLO` (§5); e **distingue `HUMANO_UNICO`**, que **não** encerra sem transição — segue para a `MaquinaEstados` com `estado = atendimento_humano` e `identidade = None`, resolvendo por **T33** com zero emissão automática |
| `ResolvedorIdentidade` | a **cascata D0–D6 é determinística** — mesmas entradas, mesma decisão, sem relógio, sem I/O e sem LLM; **alvo único** quando a cascata resolve, com `identidade` derivada do estado do alvo; **ambiguidade segura** — `AMBIGUA` sempre com alvo `None` e **sem herdar dado algum** (A1, A6); **primeiro contato** distinguido por `havia estado esperado?` = não; **`SEM_CANDIDATO_ELEGIVEL`** produzido quando há histórico conhecido e zero candidatos elegíveis, **sem virar primeiro contato, sem virar `NOVO` e sem transição**; **o identificador apenas restringe o escopo** (N7) e nunca decide sozinho; **contexto inválido nunca é entrada normal** (S7) — é erro de contrato ou pré-condição bloqueada na etapa 3; **precedência de takeover** (R5-P0): com `situacao_takeover != SEM_TAKEOVER` a cascata **não executa**, `identidade` é `None` e nenhuma `AMBIGUA` é produzida; **o conjunto H é entrada separada** — `SituacaoTakeover` é derivada de `ids_em_atendimento_humano`, **nunca** de um filtro sobre os candidatos elegíveis, e o alvo de `HUMANO_UNICO` vem **direto de H** (§6.2, H1–H6) |
| `RegrasComerciais` | tipo não aceito, data bloqueada e excesso de convidados produzem violação com motivo (I04) |
| `MaquinaEstados` | as **41 transições** do doc 06 §3; a **ordem de avaliação** das famílias C0–C11 (§4.2), com o **caminho percorrido** auditável e **estado final único**; a **projeção `transicoes_que_mudaram_estado`** (§6.2), **materializada em runtime** — subsequência ordenada de `caminho`, classificada contra o estado intermediário do instante da aplicação; o **fechamento** `E15` → `E12` pós-efeito, o teto de **três chamadas por ciclo** e a ausência de loop; os efeitos paralelos P1–P6 (§4.3) e as inércias N1–N4 (§4.4); evento não coberto por transição, efeito paralelo ou inércia é **erro de contrato** (§4.5); a máquina **não lê o YAML** e **não fabrica eventos** |
| `Qualificador` | os cinco resultados oficiais, a faixa entre capacidade sentada e coquetel, e I09 (ausência de dado nunca é incompatibilidade); recebe pendências impeditivas já classificadas e **não as detecta** |
| `DetectorHandoff` | os **gatilhos 3–10** do doc 04, cada um com o motivo correto (partição do doc 06 §9); não recebe `Qualificacao` e não reemite os gatilhos 1–2 nem 11–12 |
| `SeletorFatos` | nada fora do YAML e das respostas aprovadas entra na lista; campo pendente vira R03; **`Rxx` divergente do YAML não é selecionado** e produz erro de consistência da base (F4) |
| `ValidadorResposta` | rascunho com valor inventado, promessa de prazo, confirmação de data ou desconto é bloqueado; texto literal de `Rxx` também é conferido |
| `Persistencia` (contrato abstrato, com implementação em memória — B1/B2) | gravação, recuperação de estado e idempotência funcionam; falha de gravação bloqueia a emissão e preserva a mensagem; nenhuma afirmação de handoff sem registro (Q2, Q3) |

Esses testes são determinísticos, rápidos e não custam nada por execução. São a rede de
segurança do produto e cobrem os 23 invariantes do doc 06 §8.

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

**Reclassificação por camada** (arbitragem R3). Os casos acima não pertencem todos ao mesmo
componente; separá-los evita exigir do resolvedor prova que é de outra etapa:

| # | Camada que o caso exercita |
|---|---|
| K1 | **pipeline / adaptador** — rejeição de estado externo, antes de qualquer resolução |
| K2 | **etapa 3 + resolvedor** — a etapa 3 recupera e valida; o resolvedor recebe o escopo restrito |
| K3 | **etapa 3** — bloqueio por identificador inexistente; **o resolvedor não é executado** |
| K4 | **resolvedor** — tipo divergente exclui o candidato; cascata resolve em `NOVA_SOLICITACAO` |
| K5 | **resolvedor** — referência ao evento anterior corrobora; cascata resolve em `MESMA_SOLICITACAO` |
| K6 | **resolvedor + ação futura do orquestrador** — o resolvedor devolve `AMBIGUA`; a pergunta de esclarecimento e a persistência do pendente (A3, A7) são do orquestrador |
| K7 | **etapa 3** — bloqueio por contexto corrompido; **o resolvedor não é executado** |

**Cenários normativos do `ResolvedorIdentidade`.** Cobertura conceitual suficiente — não é
necessário replicar fixtures, mas nenhum cenário abaixo pode ficar sem prova:

| # | Cenário | Resultado esperado |
|---|---|---|
| R2-K1 | Um candidato ativo, sem declaração, sinais indeterminados | `ATENDIMENTO_ATIVO` / `INERCIA_ATENDIMENTO_ATIVO` |
| R2-K2 | Dois candidatos ativos válidos, sem declaração | `AMBIGUA` / `AMBIGUIDADE_MULTIPLOS_ATIVOS` |
| R2-K3 | Um candidato encerrado, tipo e data coincidentes | `MESMA_SOLICITACAO` / `ANCORA_COINCIDENTE_UNICA` |
| R2-K4 | Dois candidatos corroborados | `AMBIGUA` / `AMBIGUIDADE_MULTIPLOS_COMPATIVEIS` |
| R2-K5 | Continuidade declarada, um único candidato válido, sem âncora | `CONTINUIDADE_DECLARADA_CANDIDATO_UNICO` |
| R2-K6 | Continuidade declarada, dois candidatos válidos, sem âncora | `AMBIGUA` / `AMBIGUIDADE_SINAIS_INSUFICIENTES` |
| R2-K7 | Evento novo declarado, nenhum candidato ativo no escopo | `NOVA_SOLICITACAO` / `NOVO_EVENTO_DECLARADO` |
| R2-K8 | Evento novo declarado **com** candidato ativo no escopo, inclusive `EXCLUIDO` | `AMBIGUA` / `AMBIGUIDADE_DIVERGENCIA_EM_ATENDIMENTO_ATIVO` |
| R3-K1 | `NOVO_EVENTO_DECLARADO` **com** referência ao evento anterior | `AMBIGUA` / `AMBIGUIDADE_SINAIS_CONTRADITORIOS` — decidido em **D0**, antes de qualquer contagem |
| R3-K2 | Escopo vazio e `havia estado esperado?` = **não** — fixture com `veredito_identificador = NAO_INFORMADO` e `id_atendimento_validado = None` (P-I1) | identidade `None` / `PRIMEIRO_CONTATO_COMPROVADO` |
| R3-K3 | Escopo vazio e `havia estado esperado?` = **sim** — fixture com `veredito_identificador = NAO_INFORMADO` e `id_atendimento_validado = None` (P-I1) | identidade `None` / `SEM_CANDIDATO_ELEGIVEL`; **sem transição**, **não é primeiro contato**, **não vira `NOVO`** |
| R3-K4 | Identificador `ENCONTRADO`, outro candidato `CORROBORADO`, identificado não corroborado — fixture **válida**: `id_atendimento_validado` presente, **exatamente um** candidato com esse ID e `havia_estado_esperado = true` (P-I2, P-I4, P-I5) | `AMBIGUA` / `AMBIGUIDADE_SINAIS_CONTRADITORIOS` — o identificador **não vence** a corroboração alheia |
| R3-K5 | Identificador `ENCONTRADO` sem conflito — fixture **válida**: `id_atendimento_validado` presente, **exatamente um** candidato com esse ID e `havia_estado_esperado = true` (P-I2, P-I4, P-I5) | escopo restrito ao identificado, `escopo_restrito_por_identificador = true`, cascata prossegue e **pode** resultar em `AMBIGUA` ou `MESMA_SOLICITACAO` |
| R3-K6 | Todos os candidatos com tipo divergente, sem declaração, nenhum ativo | `NOVA_SOLICITACAO` / `TODOS_CANDIDATOS_DIVERGENTES` |
| R3-K7 | Valor extraído presente **sem** confiança declarada; ou veredito `NAO_ENCONTRADO`/`INCOMPATIVEL` alcançando a etapa 5 | **erro de contrato** (classe II de §7.1): nenhuma identidade devolvida — nunca `AMBIGUA` |

Em todos os cenários acima, a saída auditável de §7.1 deve ser conferida: `criterio`
presente, `candidatos_avaliados` e `classificacao_por_candidato` coerentes com o escopo, e
**nenhum nome, telefone, texto conversacional ou dado comercial** no resultado.

**Cenários da arbitragem R5** — correção do `Vinculo` e precedência de takeover:

| # | Cenário | Resultado esperado |
|---|---|---|
| R5-K1 | `NAO_DISCRIMINANTE` + `COM_REFERENCIA` | `Vinculo = DECLARA_CONTINUIDADE` — semântica **R3 preservada**, sem regressão |
| R5-K2 | `NOVO_EVENTO_DECLARADO` + `COM_REFERENCIA` | `Vinculo = DECLARACAO_CONTRADITORIA` → **D0** → `AMBIGUA` / `AMBIGUIDADE_SINAIS_CONTRADITORIOS`. **Nenhum critério novo** é criado |
| R5-K3 | `HUMANO_UNICO` **e** outro atendimento encerrado `CORROBORADO` | **takeover prevalece**: D0–D6 não executam; `identidade = None`; alvo = o atendimento **humano**; `E01` segue por **T33**; **zero emissão**. A corroboração alheia **não** desvia o alvo |
| R5-K4 | `HUMANO_UNICO` **e** identificador apontando outro atendimento | **takeover prevalece**: `identidade = None`; alvo = o atendimento humano; **T33**. A restrição por identificador (D2) **nem chega a ser aplicada**, pois R5-P0 a antecede |
| R5-K5 | `HUMANO_MULTIPLO` | `identidade = None`; `id_atendimento_alvo = None`; **`MaquinaEstados` não é chamada**; ciclo encerra sem transição; **zero emissão**; **nenhuma alegação de entrega**, registro para humano ou destinatário específico |
| R5-K6 | `SEM_TAKEOVER` | **D0–D6 idênticos à R3**, com a única diferença sendo a representação **total** do vínculo contraditório (`DECLARACAO_CONTRADITORIA` em vez de predicado paralelo) |
| R5-K7 | Conjunto completo dos casos R5 | **Nenhum deles exige membro novo em `Identidade`** — o enum permanece com **quatro** membros; takeover é expresso por `situacao_takeover`, campo ortogonal |

**Cenários do conjunto H** (arbitragem R-H) — provam que H é entrada separada, fora de N-a:

| # | Cenário | Resultado esperado |
|---|---|---|
| K-H1 | `ids_em_atendimento_humano` **vazio** | `SEM_TAKEOVER`; cascata D0–D6 executa normalmente |
| K-H2 | H com **um** ID | `HUMANO_UNICO`; `id_atendimento_alvo` = **esse ID**; `identidade = None`; `criterio = None` |
| K-H3 | H com **dois ou mais** IDs distintos | `HUMANO_MULTIPLO`; alvo `None`; `identidade = None`; `criterio = None`; `MaquinaEstados` não é chamada |
| K-H4 | Conjunto elegível **vazio** + H com **um** ID | `HUMANO_UNICO` — **e não `SEM_CANDIDATO_ELEGIVEL`**. R5-P0 antecede D1, então o escopo vazio nem é avaliado |
| K-H5 | Candidato **`CORROBORADO`** no conjunto elegível + H com **outro** ID | **takeover prevalece**: o candidato corroborado **não** vira alvo; alvo = o ID de H |
| K-H6 | **ID duplicado** em H | **erro de contrato** (classe II) — a duplicata **não** é lida como `HUMANO_MULTIPLO` |
| K-H7 | H **vazio** + candidato elegível com `estado == atendimento_humano` | **erro de contrato** por **H5** — a etapa 3 produziu projeções incoerentes |
| K-H8 | ID presente em H e **ausente** do conjunto elegível | **válido, não é erro** — resultado esperado de N-a não governar H; o takeover continua prevalecendo |

**Cenários da arbitragem R-I** — projeção do identificador validado para a etapa 5. Provam
as pré-condições **P-I1–P-I5** e a fronteira parcial **N-a-F1**, sem criar estado, evento,
transição, critério ou campo de saída:

| # | Cenário | Resultado esperado |
|---|---|---|
| R-I-K1 | `NAO_INFORMADO` + `id_atendimento_validado = None` | **fluxo normal**, sem restrição de escopo; `escopo_restrito_por_identificador = false` |
| R-I-K2 | `NAO_INFORMADO` + `id_atendimento_validado` **presente** | **erro de contrato classe II** (P-I1) |
| R-I-K3 | `ENCONTRADO` + `id_atendimento_validado` `None` **ou vazio** | **erro de contrato classe II** (P-I2) |
| R-I-K4 | `ENCONTRADO` + `havia_estado_esperado = false` | **erro de contrato classe II** (P-I4) |
| R-I-K5 | `ENCONTRADO` + ID **ausente** de `candidatos`, **havendo outros candidatos** | **erro de contrato classe II** (P-I5) — **não** é `SEM_CANDIDATO_ELEGIVEL` |
| R-I-K6 | `ENCONTRADO` + `candidatos` **vazio** | **erro de contrato classe II** (P-I5) — **não** é `SEM_CANDIDATO_ELEGIVEL` e **não** alcança D1 |
| R-I-K7 | `ENCONTRADO` + ID com **duas ou mais** ocorrências em `candidatos` | **erro de contrato classe II** (P-I5) |
| R-I-K8 | `ENCONTRADO` **inconsistente** + `HUMANO_UNICO` | **erro de contrato classe II** por pré-condição; **R5-P0 não é alcançado** sobre entrada malformada |
| R-I-K9 | `ENCONTRADO` **inconsistente** + `DECLARACAO_CONTRADITORIA` | **erro de contrato classe II**; **D0 não é alcançado** sobre entrada malformada |
| R-I-K10 | `ENCONTRADO` **válido**, ID presente, `HUMANO_UNICO` apontando **outro** atendimento | **takeover prevalece**: alvo = **o ID de H**; `identidade = None`; `criterio = None`; D0–D6 não executam |
| R-I-K11 | `ENCONTRADO` **válido**, ID presente, **sem conflito** | **D2 restringe**: `escopo_restrito_por_identificador = true`; `candidatos_avaliados` **reduzido ao identificado** |
| R-I-K12 | `ENCONTRADO` **válido**; **outro** candidato `CORROBORADO`; identificado **não** corroborado | `AMBIGUA` / `AMBIGUIDADE_SINAIS_CONTRADITORIOS`; `escopo_restrito_por_identificador = false` |
| R-I-K13 | `NAO_ENCONTRADO` **ou** `INCOMPATIVEL` | **erro de contrato classe II** (P-I3), **independentemente** do valor de `id_atendimento_validado` |
| R-I-K14 | `NAO_INFORMADO` + escopo **vazio** + `havia_estado_esperado = true` | identidade `None` / `SEM_CANDIDATO_ELEGIVEL` |
| R-I-K15 | `NAO_INFORMADO` + escopo **vazio** + `havia_estado_esperado = false` | identidade `None` / `PRIMEIRO_CONTATO_COMPROVADO` |

Em nenhum dos casos de erro acima o resolvedor devolve `AMBIGUA` e em nenhum deles alguma
identidade é devolvida. Nenhum cenário R-I exige membro novo em `Identidade`, critério novo
em `CriterioIdentidade`, valor novo em `VeredictoIdentificador` ou campo novo na saída.

Casos conceituais obrigatórios da interpretação da etapa 4 (arbitragem N-b, §6.3).
**Cenários conceituais — nenhum teste Python é criado por esta arbitragem.**

| # | Caso | Resultado esperado |
|---|---|---|
| K-Nb-1 | `CONTINUIDADE_DE_EVENTO_DECLARADA` com confiança `ALTA` | `intencao_identidade = CONTINUIDADE_DECLARADA` (N-b-K1) |
| K-Nb-2 | `CONTINUIDADE_DE_EVENTO_DECLARADA` com confiança `BAIXA` | `intencao_identidade = NAO_DISCRIMINANTE`: `BAIXA` é **ausência** para consumo estruturado |
| K-Nb-3 | `EVENTO_NOVO_DECLARADO` com confiança `ALTA` | `intencao_identidade = NOVO_EVENTO_DECLARADO` (N-b-K1) |
| K-Nb-4 | `EVENTO_NOVO_DECLARADO` com confiança `BAIXA` | `intencao_identidade = NAO_DISCRIMINANTE` |
| K-Nb-5 | Nenhuma das duas intenções do grupo **B** ligadas à identidade | `intencao_identidade = NAO_DISCRIMINANTE` |
| K-Nb-6 | `CONTINUIDADE_DE_EVENTO_DECLARADA` e `EVENTO_NOVO_DECLARADO` **simultâneas** | **erro de contrato** `E-Nb-18`; **nenhuma projeção**; a etapa 5 **não executa** |
| K-Nb-7 | Uma referência ao evento anterior com confiança `ALTA` | `COM_REFERENCIA` + `confianca_referencia = ALTA` (N-b-R3, N-b-R4) |
| K-Nb-8 | Referências com confianças **`ALTA` e `BAIXA`** misturadas | `COM_REFERENCIA` + `confianca_referencia = ALTA` (N-b-R4) |
| K-Nb-9 | Referências **todas** com confiança `BAIXA` | `COM_REFERENCIA` + `confianca_referencia = BAIXA`; o consumidor aplica **C3** (N-b-R5) |
| K-Nb-10 | Coleção de referências **vazia** | `SEM_REFERENCIA` + `confianca_referencia = None` (N-b-R2) |
| K-Nb-11 | Referência **sem confiança declarada** | **erro de contrato** `E-Nb-1` |
| K-Nb-12 | Texto **vazio ou em branco** em pergunta, referência ou trecho ambíguo | **erro de contrato** `E-Nb-10` |
| K-Nb-13 | `tipo_evento` e `data_nomeada` presentes com confiança `ALTA` | valores **nominais transportados** com `ALTA` (N-b-K4–N-b-K7) |
| K-Nb-14 | `tipo_evento` e `data_nomeada` presentes com confiança `BAIXA` | valores **transportados mesmo assim**, com `BAIXA`: a derivação **não aplica C3** — quem aplica é o `ResolvedorIdentidade` |
| K-Nb-15 | `tipo_evento` e `data_nomeada` **ausentes** | valores e confianças `None` (N-b-K4–N-b-K7) |
| K-Nb-16 | Dado **A–D** presente **sem** o código derivado correspondente | **erro de contrato** `E-Nb-11` (N-b-X4) |
| K-Nb-17 | Código **A–D** presente **sem** o dado correspondente | **erro de contrato** `E-Nb-12` (N-b-X4) |
| K-Nb-18 | Código derivado com confiança **divergente** do payload ou da agregação | **erro de contrato** `E-Nb-13` (N-b-X3) |
| K-Nb-19 | `convidados` e `formato` válidos e presentes | relatados na `Interpretacao`; **não atravessam** para a identidade (N-b-K8) |
| K-Nb-20 | `convidados` **negativo**, `bool` ou não inteiro | **erro de contrato** `E-Nb-8` (N-b-D4) |
| K-Nb-21 | `formato` fora de `sentado` \| `coquetel` | **erro de contrato** `E-Nb-9` (N-b-D5); vocabulário fechado, `E-Nb-5` quando o valor é de outro domínio |
| K-Nb-22 | `nome` e `contato` presentes | permanecem **apenas no runtime** da `Interpretacao`; **proibidos** na projeção (N-b-K8, §6.6) |
| K-Nb-23 | Uma pergunta comercial com confiança `ALTA` | `PERGUNTA_COMERCIAL` com `ALTA`; pergunta **efetiva** (N-b-Q2, N-b-Q6) |
| K-Nb-24 | Uma única pergunta comercial com confiança `BAIXA` | `PERGUNTA_COMERCIAL` com `BAIXA`; texto **preservado para diagnóstico** e **não efetivo**: não é consumida pelo produtor de `E09`/S2-D8 nem pelo `SeletorFatos` (N-b-Q3) |
| K-Nb-25 | Perguntas com confianças **`ALTA` e `BAIXA`** misturadas | `PERGUNTA_COMERCIAL` com `ALTA` (N-b-Q6); somente as `ALTA` são efetivas |
| K-Nb-26 | `perguntas_comerciais` **não vazia** sem `PERGUNTA_COMERCIAL` | **erro de contrato** `E-Nb-14` |
| K-Nb-27 | `PERGUNTA_COMERCIAL` presente com a coleção **vazia** | **erro de contrato** `E-Nb-15` |
| K-Nb-28 | `pedido_de_humano = verdadeiro` com confiança `ALTA` | sinal **efetivo**; `PEDIDO_DE_HUMANO` presente; quem emite `E18` continua sendo o `DetectorHandoff` (N-b-PH6) |
| K-Nb-29 | `pedido_de_humano = verdadeiro` com confiança `BAIXA` | **permanece sinal efetivo** — **única exceção** à regra "`BAIXA` = ausência" (N-b-PH3, N-b-PH4). **Não** chega à projeção, **não** altera C1–C3, **não** cria `E18` e **não** cria precedente |
| K-Nb-30 | `pedido_de_humano = falso` com confiança **declarada** | **erro de contrato** `E-Nb-3` (N-b-PH1) |
| K-Nb-31 | `pedido_de_humano = verdadeiro` sem `PEDIDO_DE_HUMANO`, ou `PEDIDO_DE_HUMANO` com booleano falso | **erro de contrato** `E-Nb-16` |
| K-Nb-32 | Correção declarada explicitamente, coerente com `dados_extraidos` em campo, valor e confiança | **válida**; a etapa 4 **relata** e **não grava**; a etapa 6 decide depois (N-b-C4, N-b-C5) |
| K-Nb-33 | Correção com campo **ausente** de `dados_extraidos`, valor divergente ou confiança divergente | **erro de contrato** `E-Nb-17` |
| K-Nb-34 | Confiança declarada em `trechos_ambiguos` ou em código **derivado** do grupo **A1** | **erro de contrato** `E-Nb-3` (N-b-G6b, N-b-T5) |
| K-Nb-35 | `confianca_global = BAIXA` com campos de confiança `ALTA` | **sem efeito algum**: não é erro, não é alerta, não exige reconciliação; a **confiança do campo prevalece** (N-b-CG3) |
| K-Nb-36 | `confianca_global` **ausente** | **erro de contrato** `E-Nb-4` (N-b-CG1) |
| K-Nb-37 | Múltiplas intenções autônomas simultâneas — por exemplo `INTERESSE_EM_VISITA`, `EXCECAO_SOLICITADA` e `INTERESSE_CONFIRMAR_DISPONIBILIDADE` | **todas relatadas**, cada uma com confiança própria obrigatória; nenhuma precedência é criada aqui e **nenhuma vira `Exx`** (N-b-G2) |
| K-Nb-38 | `INTERESSE_CONFIRMAR_DISPONIBILIDADE` com `ALTA`, com `BAIXA` e **ausente**, sobre `Interpretacao` válida | condição 5 de §4.4 = `True`, `False` e `False`, respectivamente (N-b-CD1–N-b-CD3) |
| K-Nb-39 | **Modo degradado** — produtor indisponível, **sem `Interpretacao`** | condição 5 = `None` (N-b-CD4, N-b-M6); **nenhuma projeção** (N-b-M2); a etapa 5 **não executa**; a `MaquinaEstados` **não é chamada por esse caminho**; **nada é gravado** (N-b-M5); **nenhum alerta novo** é criado (N-b-M3); ausência **≠** interpretação vazia (N-b-G8) |
| K-Nb-40 | **Proteção da projeção e zero `Exx`** — `Interpretacao` completa com perguntas, nome, contato e trechos ambíguos | a `ProjecaoInterpretacao` continua com **exatamente sete** campos e **zero texto conversacional e zero PII** (N-b-K8); e a etapa 4 **não emite** `Exx`, `Txx`, `Rxx`, qualificação, violação, estado, pendência nem `motivo_encerramento` — tentativa disso é `E-Nb-19` (N-b-RES1). **Complemento AJ2**: o **`assunto` de cada pergunta também não atravessa** para a projeção (N-b-Q12, N-b-K8) |

Nenhum cenário `K-Nb` exige membro novo em `Identidade`, critério novo em
`CriterioIdentidade`, valor novo em `VeredictoIdentificador`, campo novo em
`ProjecaoInterpretacao` ou componente novo em §4.1.

**Fronteira estendida por AJ2 — `K-Nb-41` a `K-Nb-51`.** A micro-arbitragem **AJ2** (§6.3)
acrescenta **onze** cenários conceituais sobre o **`assunto`** de `PerguntaComercial`, e
**complementa `K-Nb-40`** para explicitar que o assunto **também não atravessa** para a
projeção. A lista completa dos novos cenários está em §6.3, na seção de AJ2; a fronteira
passa a ser **`K-Nb-1`–`K-Nb-51`**. Dos 40 anteriores, **34 permanecem literais**, **6
exigirão adaptação de representação** numa futura materialização, **0 mudam de sentido** e
**0 são substituídos**. **Nenhum teste Python é criado por AJ2.**

**Classificação e alcance de `K-Nb-18`, `K-Nb-34` e `K-Nb-39`** (micro-arbitragem **AJ1**,
§6.3). Os **40** cenários `K-Nb` **existentes à época de AJ1** permanecem **os mesmos**, com o
**mesmo resultado esperado**: AJ1 esclarece **como cada um se prova**, não **o que ele
afirma**. Nenhum cenário é acrescentado, removido, renumerado ou reescrito **por AJ1** — os
cenários `K-Nb-41`–`K-Nb-51` são **acrescentados depois**, pela micro-arbitragem **AJ2**.

| Cenário | Classificação AJ1 | Alcance da prova |
|---|---|---|
| `K-Nb-18` | **estrutural** da canonicalização — `E-Nb-13` é **invariante / program error** (AJ1-13a) | Provado por **pós-condição / propriedade**: para **toda** `Interpretacao` canônica, a **confiança A1 == resultado de N-b-X3** (AJ1-13b). **Não se exige** prova por exceção levantada a partir de entrada externa: nenhuma confiança **A1** independente é aceita do produtor (AJ1-13c) |
| `K-Nb-34` | **recebível / runtime** — permanece exatamente como está | Cobre **dois** casos, ambos resolvidos em **`E-Nb-3`**: (a) **confiança declarada em `trecho_ambiguo`** (N-b-T5); e (b) **tentativa de apresentar código A1 com confiança no slot de intenções autônomas** (AJ1, caso A). **Nenhuma precedência de `E-Nb-13` sobre `E-Nb-3`** é criada, e **nenhum código novo** — de erro ou de cenário — é introduzido |
| `K-Nb-39` | **parcialmente local, parcialmente futuro** | **Localmente** verificável na futura fronteira: **sem `Interpretacao`**, `interesse_confirmar_disponibilidade = None` (N-b-CD4); **ausência de `Interpretacao` ≠ `Interpretacao` válida sem sinais** (N-b-G8); e a `ProjecaoInterpretacao` **exige `Interpretacao` canônica válida** (N-b-M2). **Permanecem futuros**, dependentes de orquestração: a etapa 5 **não executar**; a `MaquinaEstados` **não ser chamada**; **nada ser gravado**; os **alertas**; e a **coordenação do modo degradado** (N-b-M3, N-b-M8) |

Consequência de método: **não** se deve afirmar cobertura das propriedades **futuras** de
`K-Nb-39` a partir de um teste isolado da fronteira da etapa 4. Elas pertencem à
**orquestração**, que **não existe** (§12, itens 10, 11, 15 e 18).

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
pode duplicar essa lógica comercial. O `Qualificador` foi **implementado na Etapa 3B.5** e a
`MaquinaEstados` foi **implementada na Etapa 3B.6**. A precedência entre os dois foi
respeitada na ordem de entrega e **permanece válida como regra de arquitetura**; a
arbitragem **S1** não é reaberta.

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

**Fronteira do produtor de interpretação da etapa 4** (arbitragem N-b, §6.3). O **limite único**
acima **cobre a etapa 4**: o "produtor de interpretação da etapa 4" é **fronteira funcional**
dentro desse limite, **não** um componente determinístico novo — **§4.1 permanece com 14
componentes** e §2 com **nove** responsabilidades (N-b-F1, N-b-F2). Fornecedor, modelo, SDK,
API, biblioteca e formato de transporte **continuam não escolhidos** (N-b-F3), e a **Estratégia
2 não é reaberta**. A derivação dos **seis códigos A1**, da `ProjecaoInterpretacao` e da
**condição 5** de §4.4 é **determinística dentro da fronteira da etapa 4** e **não constitui
decisão independente do LLM** (N-b-F5).

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
| 3 | Critério técnico de "mesmo evento × nova solicitação" (T36/T37) | **ARBITRADO** nesta entrega (arbitragem R3): cascata determinística **D0–D6**, comparação exclusivamente nominal e vocabulário fechado de 12 critérios, materializados em §7.1 e refletidos em doc 06 §3. **À época daquela arbitragem, nenhum código foi criado** e a implementação ainda não estava autorizada. **Estado atual**: o `ResolvedorIdentidade` foi **implementado depois**, na **3B.7**, e está **integrado à `main`** pelo **PR #29** — commit funcional `25ab2726e15daeb7710bc0bcce9cfe7e092ce9f4`, merge `568919f5976361fa236e46a67909366e52ee85c3` (`src/casa77_sdr/identity.py`). O item **não bloqueia** nem a especificação nem a implementação do `ResolvedorIdentidade` | **resolvido** — §7.1; **implementado** na 3B.7 |
| 3a | Destino do alerta operacional não definido | S5, Q5 e F4 exigem um canal separado da conversa; hoje não existe | etapa 5 / etapa 8 |
| 3b | Janela temporal da chave composta de idempotência (§4.3) | curta demais duplica resposta; longa demais engole repetição humana legítima | Etapa 3B, com medição |
| 3c | Divergência `Rxx` × YAML depende de mapear cada `Rxx` ao campo que ele cita | mapeamento incompleto deixa divergência passar sem detecção. O **contrato** desse mapeamento está **arbitrado** em §2.3 (pendência **C**, item 19) e **ainda não foi materializado** | Etapa 3B, sobre o contrato de §2.3 |
| 4 | `R01` e `R15` ainda em **AGUARDA APROVAÇÃO** | saudação e encerramento sem texto aprovado | Douglas Bianchi |
| 5 | Canal de entrega do resumo e SLA indefinidos; **confirmação física de entrega do resumo** | etapa 14 do pipeline fica sem destino. `encaminhado_humano` afirma handoff **registrado**, nunca recebimento confirmado (doc 06 §10) — a confirmação física permanece futura | etapa 5 |
| 6 | Comportamento fora do horário de atendimento indefinido | resposta fora de horário não especificada | Douglas Bianchi |
| 7 | Precisão do validador de resposta | validador fraco deixa passar valor inventado; forte demais bloqueia texto correto | Etapa 3B, com os casos de `tests/perguntas-criticas.md` |
| 8 | Custo por conversa não medido | sem parâmetro de custo do LLM | etapa 9 |
| 9 | Política de retenção de log não definida (L7) | dado pessoal guardado sem prazo | antes da produção, etapa 10 |
| 10 | **S2-D8** — contrato de detecção e classificação de pendências: detectar campo `null`/`pendente` relevante e ausência de resposta aprovada, classificar impeditiva × acessória, fornecer os identificadores técnicos ao `Qualificador` e confirmar `E09` | **não bloqueia** a `MaquinaEstados`, que recebe `E09` pronto; **bloqueia** o `OrquestradorMotor` e a integração completa. Nenhum componente concreto foi escolhido — não é o `CarregadorYaml` nem o `ValidadorYaml` | arbitragem específica, antes da integração do pipeline (doc 06 §11) |

| 11 | **N-a** — política de **elegibilidade e recência** que produz o conjunto elegível da etapa 3 | **ARBITRADA DOCUMENTALMENTE** (arbitragem N-a, §6.2): classificação **fechada dos oito estados**; recência aplicável **exclusivamente** a `encerrado`; `instante_ultima_transicao` como **único** marco temporal do MVP — **quando inicializado ou atualizado, recebe o `instante_de_referencia_do_ciclo` daquele ciclo**, **nunca** o relógio vivo; atualização decidida pelo **caminho de transições**; limiar como **configuração operacional validada explicitamente**; projeção do registro em `CandidatoAtendimento`; composição de E; duplicatas; **ordem canônica** só para auditabilidade; e a precedência conceitual da etapa 3 — materializados em §5, §6.2 e §7.1, com **N-a-F1**, **N-I**, **P-I**, **R5-P0**, **H1–H6** e **D0–D6** preservados. **Não é implementação**: a **arbitragem N-a** não alterou `persistence.py` e o `OrquestradorMotor` **continua não autorizado**. **Materializações posteriores**, em entregas funcionais próprias: (a) o **transporte e a validação da representação** de `instante_ultima_transicao` na persistência operacional (§6.2, M-T1–M-T6); e (b) a **produção determinística de E** — projeção, classificação dos oito estados, recência de `encerrado`, N-a-F1, duplicatas e ordem canônica — como função pura em `src/casa77_sdr/eligibility.py` (§6.2, M-E1–M-E6); e (c) a **montagem determinística das projeções de identidade da etapa 3** — leitura da persistência, validação do identificador, projeção do contexto, conjunto **H**, `havia_estado_esperado` e projeção **N-I** — em `src/casa77_sdr/context.py` (§6.2, M-C1–M-C8), que cobre a **fronteira etapa 3 → identidade/etapa 5** e **não** a etapa 3 inteira. **A integração N-a continua PARCIAL**: a **decisão determinística** exigida por **N-a-T3–N-a-T7** foi materializada em `src/casa77_sdr/transition_marker.py` (§6.2, M-DT1–M-DT7), e a **aplicação** dessa decisão com a **escrita** pelo contrato da persistência existe como **fronteira chamável** em `src/casa77_sdr/transition_marker_write.py` (§6.2, M-AE1–M-AE7). Ainda assim, **N-a-T3–N-a-T7 NÃO estão operacionalmente concluídas** — a **integração da etapa 13 no pipeline** permanece pendente, assim como o **tratamento operacional dos bloqueios** (S4, S5), o **destino do alerta** e o **`OrquestradorMotor`**. A **projeção `transicoes_que_mudaram_estado`** (§6.2) foi **ARBITRADA** e depois **materializada em runtime** na `MaquinaEstados`. Isso **não** encerra o item: a **decisão pura** e a **composição decisória entre as 0–3 chamadas** do ciclo estão materializadas em **M-DT1–M-DT7**, mas continuam **NÃO implementadas/integradas** a **montagem completa** do `RegistroAtendimento`, a **decisão de se a etapa 13 executa**, a **escolha entre criar e gravar** no pipeline, a **geração de `id_atendimento`**, a **criação operacional** do atendimento, a **marcação de idempotência**, a **preservação de pendente**, o **tratamento operacional de falha** e a **integração da etapa 13**; o **valor numérico do limiar** e o **mecanismo de carga** continuam pendentes no **item 18**, a **E4** continua **distinta e aberta** no **item 15**, e o **`OrquestradorMotor` continua fora** | **especificação resolvida** — §6.2. **Aquela arbitragem não autorizou implementação alguma** — o PR #31 foi entrega documental e, à época, N-a não existia em código. O **valor numérico do limiar** e o **mecanismo concreto de carga** da configuração são o **item 18**. **E4** é pendência **distinta e ainda aberta**, no **item 15**, e **não é resolvida aqui** |
| 12 | **N-b** — contrato global da **interpretação** da etapa 4: quem produz a projeção estruturada de §6.3 (`intencao_identidade`, referências, confianças binárias) e com que garantias | **ARBITRADA DOCUMENTALMENTE / NÃO IMPLEMENTADA** (arbitragem N-b, §6.3): o contrato da **`Interpretacao`** está **fechado** — as **oito** categorias de §6.3 preservadas; **`IntencaoConversacional`** com **exatamente 11** códigos na partição **A1 (6 derivados) / A2 (2 autônomos) / B (3 autônomos)**; consistência cruzada **N-b-X1–N-b-X6** sobre os **seis pares de representação dupla**; regras de confiança **N-b-G6/G6b/G6c**; lista fechada de erros **E-Nb-1–E-Nb-19**; modo degradado **N-b-M1–N-b-M8**; fronteira do produtor **N-b-F1–N-b-F5**; e cenários **K-Nb-1–K-Nb-40** (§8.2). **Produtor atribuído**: o "produtor de interpretação da etapa 4" é **fronteira funcional** do limite único de LLM (§4.2, §9), **não componente novo** — §4.1 permanece com **14** componentes. Passam a ter produtor a **derivação para a projeção da etapa 5** (**N-b-K1–N-b-K7**) e a **condição 5** de §4.4 (**N-b-CD1–N-b-CD4**); as condições **2**, **4** e **8** continuam **não atribuídas**. **Residual explícito**: a etapa 4 **não emite `Exx`**, e a transformação posterior dos sinais interpretados em eventos confirmados **continua sem produtor concreto** (**N-b-RES1–N-b-RES3**) — **sem identificador de pendência novo**. **Nenhum código, tipo Python, JSON Schema, biblioteca, fornecedor, modelo, SDK, API ou formato de transporte foi criado ou escolhido**. **Micro-arbitragem AJ1** (§6.3, §8.2): fecha a **representação/canonicalização determinística** de N-b — **`A1` não é entrada semântica** do produtor não determinístico, presença **derivada** e confiança **calculada** por **N-b-X3**, **precedência `E-Nb-3` × `E-Nb-5`** no slot autônomo, **classificação AJ1** dos 19 erros em recebíveis × invariantes internos × invariante estrutural, **alcance de prova** de `K-Nb-18`, `K-Nb-34` e `K-Nb-39`, estratégia estrutural de `E-Nb-19`, preservação da **condição 5** e reutilização por **import** de `FormatoEvento`. **AJ1 não reabre N-b, não a implementa, não cria componente e não cria subetapa**. **Materialização posterior, em entrega funcional própria**: a **parte determinística** do contrato — canonicalização da `Interpretacao`, derivação dos seis códigos **A1** com confiança calculada por **N-b-X3**, projeção total para a `ProjecaoInterpretacao` de **sete** campos e a **condição 5** como função total — existe em código em `src/casa77_sdr/interpretation.py` (§6.3, **M-NB1–M-NB9**). **A implementação de N-b permanece PARCIAL**: o **produtor não determinístico / LLM da etapa 4 NÃO foi implementado**, **`N-b-RES2` continua aberto**, a **etapa 4 não está operacionalmente integrada** ao pipeline e o **`OrquestradorMotor` continua fora**. **Extensão posterior por AJ2** (item 20, §6.3): o contrato de `PerguntaComercial` foi **estendido documentalmente** para incluir o **`assunto`** (`AssuntoComercial`, 54 valores), com `E-Nb-5` ampliado e cenários até `K-Nb-51`. **Esse delta NÃO está materializado** — `M-NB1`–`M-NB9` continuam descrevendo a implementação do PR #55, **anterior a AJ2**. | **especificação resolvida**; a **fronteira determinística** está **materializada** (M-NB1–M-NB9) **para o contrato anterior a AJ2**; o **delta AJ2**, o **produtor não determinístico** e a **integração** permanecem futuros, junto do `OrquestradorMotor` |
| 13 | **E1** — distinção entre as entidades **conversa × atendimento × lead** | atravessa identidade, persistência e registro de leads; hoje o motor opera com "atendimento" como unidade única | modelo de dados |
| 14 | **E3** — **evento novo declarado durante atendimento ativo** | hoje o resultado é **conservador**: `AMBIGUA` / `AMBIGUIDADE_DIVERGENCIA_EM_ATENDIMENTO_ATIVO` (D3). **Nenhuma transição nova foi aprovada** para abrir atendimento paralelo | arbitragem específica |
| 15 | **E4** — tratamento de **`SEM_CANDIDATO_ELEGIVEL`** pelo `OrquestradorMotor` | o resultado existe e é auditável, mas **o que o orquestrador faz com ele não está decidido**. Enquanto aberta, o resultado **encerra o ciclo sem transição** e **não autoriza avanço de integração** (doc 06 §4.5, G7) | arbitragem específica, antes do `OrquestradorMotor` |
| 16 | **Retorno do controle ao bot** — não existe hoje **transição inversa de T31** que devolva o canal ao atendimento automático sem passar por `E14`/T34 | uma vez em `atendimento_humano`, a saída documentada é o encerramento (T34) ou o encerramento por T32 a partir de `encaminhado_humano`. **Nenhum evento ou transição é criado por esta arbitragem** | arbitragem futura — **não bloqueia** a materialização R5 |
| 17 | **Duplicatas gerais de `id_atendimento` entre candidatos não identificados** | a arbitragem R-I exige unicidade **apenas do ID identificado** e **apenas** com `veredito_identificador == ENCONTRADO` (**P-I5**). **Não foi decidido** — e **não é decidido nesta entrega** — se IDs duplicados entre candidatos **não identificados** constituem erro geral de contrato. **Nenhuma regra global de unicidade foi adicionada** | arbitragem específica futura — **não bloqueia** nenhuma entrega já autorizada |
| 18 | **Valor numérico do limiar temporal de recência** e **mecanismo concreto de carga** da configuração (§6.2, N-a-L6) | **A política determinística já é executável**: `eligibility.py` e `context.py` **recebem o limiar como argumento explícito** e o validam (N-a-L1–N-a-L6, M-E3, M-C3). O que continua faltando é a **configuração operacional concreta** — sem ela **não há como carregar o limiar no pipeline**, e portanto continuam bloqueadas a **integração operacional de N-a** e o **`OrquestradorMotor`**. A calibragem permanece a mesma questão de sempre: curto demais descarta `encerrado` que **T36** deveria reabrir; longo demais devolve histórico antigo à cascata. **Nenhum número é definido** e **nenhuma tecnologia, variável de ambiente, arquivo ou serviço é escolhido** — nem por esta entrega nem pelas materializações posteriores. **Não é dado comercial** — não entra em `knowledge/casa77.yaml` | aprovação específica de Douglas Bianchi + decisão operacional, **antes do `OrquestradorMotor`** |
| 19 | **C** — contrato estruturado, legível por máquina, ligando cada `Rxx` aos campos de `knowledge/casa77.yaml`, e o artefato que o materializa | **ARBITRADA / NÃO MATERIALIZADA** (§2.3). **CONTRATO: ARBITRADO** — está **fechado** — artefato aprovado `knowledge/indice-respostas-aprovadas.yaml`, modelo `Rxx` → **fragmentos emitíveis**, status fechado `APROVADO`/`AGUARDA_APROVACAO`/`BLOQUEADO` sem valor padrão, *bindings* **`RENDERIZADO`** e **`ASSERTIVA`** (`EH_VERDADEIRO`/`EH_FALSO`), regra **consistency-only** para `ASSERTIVA` sobre campo relacionado a handoff, formatos de **apresentação pura** sem dependência oculta, bloqueio de **transformação semântica**, tratamento de `null`/`pendente`, fontes autoritativas em transição e a separação **C × S2-D8**. **MATERIALIZAÇÃO: NÃO EXISTE** — o **índice não foi criado**, `knowledge/respostas-aprovadas.md` **não foi convertido nem alterado**, **nenhum status foi removido do Markdown**, e `ValidadorConsistenciaBase`, `SeletorFatos` e `ValidadorResposta` continuam **não implementados**. **Nenhum componente, estado, evento, transição, condição, critério, pendência ou subetapa foi criado** — a **3B.8 não existe**. Os conflitos `R10`, `R20`, `R13` e `R17` ficam **registrados e não decididos** (C-9) | **contrato resolvido** — §2.3. A **materialização** — criar o índice, converter o Markdown em *templates* e auditar a bijeção — permanece **futura e não autorizada por esta arbitragem**, antes de `ValidadorConsistenciaBase` e, em cascata, `SeletorFatos` e `ValidadorResposta` |
| 20 | **AJ2** — **origem semântica do assunto** de `PerguntaComercial`: de onde vem, e com que garantias, a informação de **sobre o que** o interessado consultou | **ARBITRADA / NÃO MATERIALIZADA** (§6.3). **AJ2 ESTENDE FORMALMENTE N-b**: `PerguntaComercial` passa conceitualmente de **dois** para **três** campos — `texto`, `confianca` e **`assunto`** obrigatório, do enum fechado **`AssuntoComercial`** de **54** valores (53 específicos + `ASSUNTO_NAO_CLASSIFICADO`), **sem confiança própria**; **um assunto por item**, com **segmentação** de consulta composta; **preservação textual** sem normalizar, resumir ou parafrasear; **duplicatas permitidas**; e o `assunto` **não atravessa** para a projeção, **não referencia `Rxx`** e **não produz condição** de §4.4 (**N-b-Q7**–**N-b-Q12**). `E-Nb-5` é **ampliado** para `assunto` ausente ou fora do vocabulário, e a lista permanece **`E-Nb-1`–`E-Nb-19`** — **sem nenhum código novo**. Cenários passam de `K-Nb-1`–`K-Nb-40` para **`K-Nb-1`–`K-Nb-51`**. **A implementação NÃO acompanha**: o **PR #55 permanece historicamente correto** e **`M-NB1`–`M-NB9` continuam descrevendo aquela implementação**, que **ainda não possui `assunto`** (AJ2-M1–AJ2-M5). **Nenhum código, teste, componente, estado, evento, transição, condição, critério, pendência ou subetapa foi criado** — a **3B.8 não existe**. **`Q53`/`Q54` continuam não classificados** | **contrato resolvido** — §6.3. A **materialização do delta** — `assunto` em código, o enum `AssuntoComercial`, a ampliação de `E-Nb-5` e os cenários `K-Nb-41`–`K-Nb-51` — permanece **futura e não autorizada por esta micro-arbitragem**. O **consumo** do assunto pertence a **S2-D8** (item 10), que continua **ABERTA** |

**AJ1 — micro-arbitragem documental fechada** (§6.3, §8.2). AJ1 é **exclusivamente
documental** e está **fechada**: ela **não** cria pendência nova, **não** resolve pendência
alguma da tabela acima e **não** altera nenhuma linha dela além da nota registrada no
**item 12**. Em particular, permanecem **abertas e inalteradas**: **S2-D8** (item 10),
**E4** (item 15), **S3-D1**, **E1** (item 13), **E3** (item 14), **B**, **C** — esta **arbitrada documentalmente depois**, em §2.3, e **NÃO MATERIALIZADA** (item 19) —, o **valor do
limiar** e seu **mecanismo de carga** (item 18), o **destino do alerta operacional**
(item 3a) e o **`OrquestradorMotor`**.

**N-b permanece NÃO IMPLEMENTADA.** AJ1 fecha a **representação e a canonicalização** que
antecedem a materialização — não a materialização. Continua verdadeiro, sem atenuação:
**não existe produtor concreto de `Interpretacao` em código**, **a etapa 4 não é funcional**,
**nenhum arquivo de `src/` ou `tests/` foi criado ou alterado** por AJ1, **`§4.1` permanece
com 14 componentes**, **§2 permanece com nove responsabilidades**, **`IntencaoConversacional`
permanece com 11 valores**, os **erros permanecem `E-Nb-1`–`E-Nb-19`** e os **cenários
permanecem `K-Nb-1`–`K-Nb-40` à época de AJ1** — fronteira depois **estendida para
`K-Nb-1`–`K-Nb-51`** pela micro-arbitragem **AJ2**, posterior (item 20). **Nenhuma subetapa
foi criada, escolhida ou autorizada — a 3B.8 não existe.**

**Silêncio sob takeover não é decisão comercial nova** (arbitragem R5). Enquanto o canal
está sob controle humano, o silêncio automático é **consequência do contrato já existente**,
não política criada aqui:

| Fonte já vigente | O que já determina |
|---|---|
| estado `atendimento_humano` | doc 06 §1.1 |
| **T33** | `E01` em `atendimento_humano` mantém o estado e **proíbe qualquer resposta automática** — inclusive com `E18` concomitante |
| **regra 11** (doc 06 §5) | quando o humano assume (`E13`), o bot **para de responder automaticamente** |
| **I03** (doc 06 §8) | em `atendimento_humano` o bot **não emite nenhuma resposta automática** |
| `deve responder = false` | §6.5 |

A política que **seria** nova é a oposta: permitir que o bot **voltasse a falar** enquanto o
humano controla o canal. **A R5 não concede essa permissão** — ela apenas garante que a
resolução de identidade não produza um referente que contorne o silêncio já obrigatório.
**E1** permanece aberta para eventual refinamento futuro da fronteira conversa × atendimento
× lead.

Nenhuma dessas pendências bloqueia especificamente a 3B.6 / `MaquinaEstados`, que já está
implementada e integrada. **S2-D8** e **E4** bloqueiam o `OrquestradorMotor` e a
integração completa. **N-b deixou de bloquear como especificação** — está **arbitrada
documentalmente** (item 12, §6.3): o contrato da `Interpretacao`, a derivação para a projeção
da etapa 5 e a condição 5 de §4.4 estão fechados. Ela **continua bloqueando como
implementação**: **nenhum produtor concreto de `Interpretacao` existe em código**, e a
transformação de sinais interpretados em `Exx` segue como **residual explícito**
(N-b-RES1–N-b-RES3). **N-a deixou de bloquear como especificação** — está **arbitrada
documentalmente** — e deixou de existir apenas no papel: sua **materialização é parcial e
já existe em código**, pelas entregas funcionais posteriores do **transporte e validação do
marco temporal** (M-T1–M-T6), da **produção determinística de E** (M-E1–M-E6) e da
**montagem das projeções de identidade da etapa 3** (M-C1–M-C8). **A integração N-a
continua PARCIAL**: a **decisão** do marco temporal, a **composição decisória entre as 0–3
chamadas** do ciclo (M-DT1–M-DT7) e a **aplicação com escrita** como fronteira chamável
(M-AE1–M-AE7) já existem em código, mas a **integração operacional no pipeline** pela
**etapa 13** permanece pendente — **N-a-T3–N-a-T7 não estão operacionalmente
concluídas** —, assim como o **valor do limiar temporal** e
seu **mecanismo de carga** (item 18), o **tratamento operacional dos bloqueios** (S4, S5) e o
**destino do alerta operacional**. **A etapa 3 não está inteiramente implementada**, a
**integração completa do pipeline não foi iniciada** e o **`OrquestradorMotor` continua não
implementado**. **E1** e **E3** permanecem abertas sem bloquear a especificação já arbitrada;
as demais mantêm os bloqueios indicados na própria tabela.
**Nenhuma delas é resolvida por esta entrega.**

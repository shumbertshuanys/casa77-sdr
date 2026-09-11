# 07 — Arquitetura do Motor de Respostas

Documento arquitetural **vigente** do motor de respostas do Casa 77 SDR. Define
responsabilidades, contratos, dependências, fronteiras e invariantes do MVP, e é a
**autoridade arquitetural** do projeto, ao lado do código e dos testes aprovados na `main`.

Deriva de `docs/02-fluxo-comercial.md`, `docs/03-regras-de-conversa.md`,
`docs/04-handoff-humano.md`, `docs/06-maquina-de-estados.md`, `knowledge/casa77.yaml`,
`knowledge/respostas-aprovadas.md` e `knowledge/informacoes-pendentes.md`.

**Estado de implementação e progresso não vivem aqui**: vivem em `docs/00-estado-atual.md`,
confrontado com a `main`. **Histórico técnico não vive aqui**: vive no Git e no GitHub.

**Dado comercial não vive aqui.** Preço, capacidade, pacote, horário, data bloqueada e
condição são lidos de `knowledge/casa77.yaml` em tempo de execução; campos são referenciados
pelo nome.

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
negócio. Não vira "não sei responder" silencioso — vira alerta para quem mantém os arquivos.
O **desfecho conversacional** ao interessado depende de existir, ou não, cobertura aprovada e
íntegra alternativa para a mesma consulta — ver a reconciliação **F4-B**, imediatamente
abaixo.

#### RECONCILIAÇÃO NORMATIVA LIMITADA de docs/07 §2.2 pela arbitragem S2-D8

**Contrato arbitrado.** Este refinamento é **limitado à consequência conversacional de F4**.
**F1**–**F6** são **preservadas**, e **F4(a)**–**F4(d)** permanecem **literais e
inalteradas**. S2-D8 refina **somente o que o interessado recebe**, **nunca** o tratamento da
divergência em si.

| # | Invariante de F4-B — vale **sempre**, sem exceção |
|---|---|
| F4-B1 | fragmento divergente é **SEMPRE bloqueado** — F4(a), F4(c) |
| F4-B2 | o **erro de consistência da base** é **SEMPRE registrado** — F4(b) |
| F4-B3 | o **alerta** para correção humana é **SEMPRE emitido** — F4(d) |
| F4-B4 | **nenhum fato divergente é emitido**, em nenhuma hipótese |

Os **dois** desfechos possíveis ao interessado, e **somente** eles:

| # | Desfecho |
|---|---|
| F4-B5 | **(A)** a divergência deixa a consulta **sem cobertura segura** → **R03 + handoff** |
| F4-B6 | **(B)** uma **alternativa aprovada e íntegra do mesmo grupo de cobertura** (**R2**, §4.4) cobre **integralmente** a consulta → a **resposta segura aprovada prossegue**, com **zero `E09` fabricado** e **zero handoff causado por essa divergência** |

**F4-B6 não atenua F4-B1–F4-B4.** O fragmento divergente continua bloqueado, o erro
continua registrado e o alerta continua emitido; o que muda é apenas que o interessado
**não** recebe R03 quando a consulta permanece **integralmente coberta** por texto aprovado
e íntegro. Quem avalia cobertura é **S2-D8** (§4.4), **não C**: **C-12 permanece literal e
inalterada** (§2.3), e a `ASSERTIVA` continua **consistency-only** (**C-5**, **C-5.1**).

### 2.3 Arbitragem C — contrato do índice estruturado de respostas aprovadas

Esta seção **fecha o contrato** de `C` e **não o materializa**.

`C` fecha o contrato e **não autoriza, por si**, criar o índice, o renderizador, o analisador
nem implementar `ValidadorConsistenciaBase`, `SeletorFatos` ou `ValidadorResposta`. Ela
**não** converte nem altera `knowledge/respostas-aprovadas.md` e **não** cria condição de
ciclo (§4.4). **O estado de materialização vive em `docs/00-estado-atual.md`**, confrontado
com a `main`.

Pendência **C**: falta um contrato estruturado, **legível por máquina**, relacionando cada
`Rxx` aos campos de `knowledge/casa77.yaml`. Esta seção **fecha esse contrato**. Enquanto o
artefato que o materializa não existir, **F3**–**F5** (§2.2) são política sem mecanismo — a
conferência dependeria de alguém reler o Markdown, que é exatamente o que §2.2 recusa como
garantia.

**`C-P` — Precedência entre as camadas de `C`.** O contrato de `C` é lido em camadas, nesta
ordem: **`C-1`–`C-15`**, depois **`C-A1`**, **`C-A2`**, **`C-A3`**, **`C-A4`** e **`C-A5`**.
Onde uma camada posterior **refina, fecha ou substitui** matéria de camada anterior,
**prevalece a posterior**. Cada camada fecha **exclusivamente** a matéria que declara fechar
— em particular, **`C-A5` fecha exclusivamente a identidade física do fragmento emitível** —,
e matéria não declarada permanece aberta.

Esta seção enuncia **contrato**, não estado. O grau de materialização de `C`, dos seus gates
e dos seus artefatos não vive aqui: vive em `docs/00-estado-atual.md`, confrontado com a
`main`.

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

Registro **sem valores comerciais** dos casos que **não podem ser convertidos
silenciosamente**. **Nenhum deles é decidido aqui.**

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

**S2-D8 é ARBITRADA** (doc 06 §11; §12, item 10). O status `BLOQUEADO` de
um fragmento **não é, por si só**, `E09` nem `pendencia_impeditiva`: ele é um fato sobre a
base, não uma decisão de ciclo. **O consumo pertence a S2-D8**, não a C.

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
pendência nova nem subetapa.

**Precedência de C-14f × AJ2.** Na fronteira de cenários **AJ2 prevalece** sobre `C-14f`
(**`C-P`**): as **11** `IntencaoConversacional` e os erros **`E-Nb-1`–`E-Nb-19`** permanecem,
e a fronteira de cenários é **`K-Nb-1`–`K-Nb-51`** (§6.3). **C não é reaberta por isso.**

#### Micro-arbitragem C-A1 — fechamento do contrato de materialização

`C-A1` **refina** o contrato de materialização e **fecha** as decisões técnicas que faltavam,
prevalecendo sobre `C-1`–`C-15` na matéria que declara fechar (**`C-P`**). Ela **não** cria o
índice, **não** altera o YAML, **não** converte respostas em *templates*, **não** muda status
real, **não** implementa renderizador nem carregador e **não** materializa **C**, **R2** ou
**S2-D8**.

##### C-15 — *Template* e equivalência

| # | Regra |
|---|---|
| C-15a | Um **literal variável** só pode ser substituído por *placeholder* **sem nova aprovação de conteúdo** quando **as duas** condições valem: **(1)** o *binding* aponta **explicitamente** para o fato que a frase **efetivamente afirma**; e **(2)** a renderização do **fragmento inteiro** com a base atual é **textualmente equivalente** ao fragmento aprovado. **Nunca inferir vínculo por coincidência textual.** |
| C-15b | **Equivalência textual** — aplicar aos **dois lados**, e **exatamente**: normalização **Unicode NFC**; e **quebras de linha suaves do Markdown dentro do mesmo parágrafo** convertidas em **um único espaço**. **Preservar**: parágrafos reais, caixa, pontuação, conteúdo e ordem. **Proibido**: `casefold`, *trim* semântico, remoção de pontuação, paráfrase e qualquer tolerância aproximada. |
| C-15c | A **unidade de equivalência** é o **fragmento inteiro** — **nunca** um *placeholder* isolado. |
| C-15d | **Sem equivalência → FAIL-CLOSED**: o fragmento **não** é convertido em *template*. Ele é classificado para **ajuste de modelo** **ou** para **futura decisão de conteúdo**. Se a reprodução exigir **transformação semântica**, **C-8 continua aplicável**. |
| C-15e | O índice **não armazena** valor renderizado, *snapshot*, *hash* de valor nem versão congelada do YAML (C-1k–C-1m), e **não recebe metadado de "origem da aprovação"**. A rastreabilidade vem do **Markdown versionado**, do **índice versionado**, da **validação reproduzível** e do **histórico Git**. |

##### Representação canônica de entrada para C-15b

Refinamento que incide **apenas sobre a leitura de `C-15b`**, segundo a precedência `C-P`.
Ele **não renumera** `C-15a`–`C-15e`, **não os reescreve** e **não cria identificador
normativo novo**: os rótulos **D1**–**D7** abaixo são **locais deste bloco** e existem só para
referência interna. Este bloco define somente o contrato; a implementação de módulo, função, assinatura, exceção
e mensagem técnica pertence à fronteira executora correspondente.

O que ela fecha é **a representação de entrada** sobre a qual a equivalência de `C-15` será
futuramente julgada. A decisão adotada é **texto canônico já extraído**.

| # | Decisão |
|---|---|
| D1 | **Unidade de entrada.** O julgamento de equivalência de `C-15` opera sobre **duas `str` em representação canônica**: **(1)** o **fragmento aprovado já extraído** como conteúdo textual; e **(2)** a **renderização textual do mesmo fragmento**. **Nenhum DTO, dataclass ou estrutura pública nova é criado.** A unidade continua sendo o **fragmento inteiro** (`C-15c`, `C-A4-P1`). |
| D2 | **Responsabilidade.** A separação entre **estrutura Markdown** e **conteúdo textual** pertence **integralmente a uma futura fronteira de extração**, que **ainda não existe** e **não é materializada aqui**. A representação canônica **chega pronta** ao comparador. O comparador **não** analisa Markdown, **não** identifica *blockquote*, *heading*, lista, *code fence* ou indentação, **não** remove prefixo `>` e **não** extrai fragmento de documento algum. |
| D3 | **Quebra suave.** Como **convenção da representação** — e **não** como inferência de Markdown —, dentro da representação canônica um **`LF` isolado (`U+000A`), não adjacente a outro `LF`**, representa **quebra suave dentro do mesmo parágrafo**. Na normalização de `C-15b` esse `LF` é convertido em **exatamente um `U+0020`**. **Nenhum outro espaço é colapsado.** |
| D4 | **Parágrafo real.** **Exatamente dois `LF` consecutivos** (`\n\n`) são a **fronteira canônica de parágrafo real** e são **preservados literalmente** na normalização. **Três ou mais `LF` consecutivos são representação NÃO CANÔNICA**: devem ser **recusados**, **nunca** reinterpretados ou normalizados. |
| D5 | **Terminadores de linha.** A representação canônica admite **somente `LF` (`U+000A`)** como terminador estrutural. São **NÃO CANÔNICOS**: `CR` (`U+000D`), `CRLF`, `U+2028`, `U+2029`, `U+0085`, `U+000B` e `U+000C`. O futuro comparador **deve RECUSAR** esses casos e **não deve converter `CRLF` para `LF`** — qualquer adaptação de terminação de linha pertence ao **futuro produtor/extrator**. |
| D6 | **Domínio canônico e três desfechos.** **(A) NÃO DETERMINÁVEL** — houve **violação mecanicamente detectável** da representação canônica; isto **não é `False`**, e o futuro chamador **deve parar ou escalar**. **(B) NÃO EQUIVALENTE** — ambos os textos pertencem ao domínio canônico e suas normalizações **diferem**; resultado conceitual **`False`**, com a consequência de **`C-15d`**: o fragmento **não** é convertido em *template*. **(C) EQUIVALENTE** — ambos pertencem ao domínio canônico e suas normalizações são **exatamente iguais**; resultado conceitual **`True`**, e **`C-15a(2)`** fica satisfeita. |
| D7 | **Violações mecanicamente detectáveis.** São representação **NÃO CANÔNICA**: terminador proibido de **D5**; `LF` na **borda inicial** do texto; `LF` na **borda final** do texto; **espaço ou tab imediatamente antes** de `LF`; **espaço ou tab imediatamente depois** de `LF`; e **três ou mais `LF` consecutivos**. Futuramente devem resultar em **NÃO DETERMINÁVEL / recusa explícita**. |

**Nomes ainda não decididos.** Esta micro-arbitragem **não define** nome de exceção, código de
erro, taxonomia nominal nem texto de mensagem — isso pertence ao **mandato técnico posterior**.

**Limite da garantia — domínio canônico.** A equivalência definida por **`C-15b`** somente
possui **garantia semântica** quando **ambos os insumos satisfazem a representação canônica** e
quando o **fragmento aprovado foi corretamente separado da estrutura Markdown pelo produtor
responsável**. A ausência de estrutura Markdown é **parcialmente uma pré-condição do
chamador** e **não pode ser integralmente verificada pelo comparador** sem transformá-lo em
*parser* Markdown. Portanto: **fora do domínio canônico, não existe garantia de correção do
veredito de equivalência.** Futuros produtores e consumidores **devem** satisfazer essa
pré-condição **antes** de utilizar o resultado para **`C-15d`** ou para qualquer **migração de
autoridade de status** (`C-A1-ST6`–`C-A1-ST10`). Esta ressalva é **normativa e obrigatória**.

**O que a futura materialização de `C-15b` NÃO fará**: *parsing* Markdown; I/O; abrir
`knowledge/**`; extrair fragmento; renderizar *template*; resolver *binding*; ler YAML;
implementar formato; decidir candidatura de fragmento; decidir migração de status; ou
materializar **C** por si só. **Comparar NÃO é materializar C.**

**Risco arquitetural — terminação de linha.** *Checkouts* e ambientes podem materializar
terminações de linha distintas das do repositório. Esta arbitragem **não altera
`.gitattributes`**, **não decide configuração de Git** e **não afirma** que qualquer
configuração seja universal ou garantida. A adaptação, quando necessária, pertence ao
**produtor/extrator**, nunca ao comparador.

**Fora desta arbitragem**, e explicitamente **não decididos**: nome de módulo, nome de função,
assinatura final, ordem de parâmetros, taxonomia de exceção, mensagem de erro, comportamento
para tipo não-`str`, ordem entre **NFC** e a dobra de quebra suave, `hora`, gramática de
`caminho_yaml`, identidade física do fragmento, sintaxe de *placeholder*, extrator físico,
índice, *renderer*, formatos, **R2**, **S2-D8**, **`N-b-RES2`**, **`OrquestradorMotor`** e
`.gitattributes`.

##### Conversão do bloco marcado em texto canônico

Refinamento que fecha, segundo **`C-P`**, **uma única** matéria: **como um
bloco físico emitível de `C-A5-U1` é convertido deterministicamente em uma `str` do domínio
canônico `D1`–`D7`, ou recusado *fail-closed***. Ela **não** reescreve, renumera ou substitui
`D1`–`D7`, **não** cria versão concorrente deles, **não** altera `C-15`, `C-15b`, `C-A1-B`,
`C-A1-ST` ou qualquer bloco de `C-A5`, e **não** cria identificador normativo novo: os rótulos
**`MT1`**–**`MT12`** abaixo são **locais deste bloco**, existem só para referência interna e
**não** são etapa, subetapa, `Exx` nem nomenclatura normativa de `C`. Este bloco define somente o contrato; a implementação de módulo, função, assinatura, exceção
e mensagem técnica pertence à fronteira executora correspondente.

**Relação com `D1`–`D7`, preservados literalmente.** Aquele bloco define o **domínio de
chegada**; este define **como se chega nele**. **`D3`** continua sendo a convenção de
**quebra suave** — um `LF` isolado representa quebra dentro do mesmo parágrafo, e é a
**normalização de `C-15b`** que o converte em exatamente um `U+0020`. **`D4`** continua
definindo **exatamente `\n\n`** como fronteira de parágrafo real, com **três ou mais `LF`
consecutivos NÃO CANÔNICOS**. **`D5`** continua admitindo **somente `LF`** como terminador da
representação canônica, com `CR`, `CRLF`, `U+2028`, `U+2029`, `U+0085`, `U+000B` e `U+000C`
**não canônicos**, e continua determinando que **o comparador não converte `CRLF`** — a
adaptação física pertence ao **produtor/extrator**. É **exatamente essa** adaptação que
**`MT8`** fecha, **do lado do extrator**, sem tocar em `D5`.

| # | Decisão |
|---|---|
| MT1 | **Fronteira física inalterada.** `C-A5-U1` permanece **literal**: a unidade física é a **sequência maximal de linhas iniciadas por `>`**. Esta convenção **não** altera como `C-A5` ou o leitor da representação marcada reconhecem a **existência estrutural** do bloco; ela acrescenta uma validação **semântica posterior**, aplicada **somente** para obter o texto canônico. |
| MT2 | **Reconhecimento estrutural ≠ conversão textual.** Um bloco pode ser **estruturalmente reconhecido** e, ainda assim, ser **recusado** pelo futuro extrator quando a sua sintaxe textual não satisfizer esta convenção. Isso **não** torna o leitor da representação marcada incorreto: são **responsabilidades distintas**. |
| MT3 | **Linha de conteúdo — forma exata.** Uma linha física de conteúdo emitível é **exatamente** `>`, **um** espaço ASCII `U+0020` e **conteúdo não vazio**. O prefixo estrutural removido é **exatamente `> `** — **dois caracteres**. **Proibido** `lstrip`, `strip`, *parser* CommonMark, normalização genérica ou tolerância implícita. |
| MT4 | **Prefixos recusados.** São **recusados *fail-closed***, entre outras formas mecanicamente equivalentes: `>` colado ao conteúdo; `>` seguido de **dois ou mais** espaços; `>` seguido de tab; `> ` seguido de tab; `> ` **sem conteúdo**, usada como suposta linha vazia; e **qualquer** whitespace adicional entre `>` e o primeiro caractere do conteúdo. **Não reinterpretar, não corrigir, não inferir intenção.** |
| MT5 | **Linha vazia interna — forma exata.** A representação física **exata** de uma linha vazia interna é **`>` sozinho**, sem espaço, antes do terminador físico. **Uma** linha `>` entre dois grupos de conteúdo representa **uma** fronteira real de parágrafo e projeta, na `str` canônica, **exatamente `\n\n`**, conforme **`D4`**. |
| MT6 | **Múltiplas linhas vazias — recusadas.** **Duas ou mais** linhas `>` consecutivas **não** criam múltiplos parágrafos e **não** são colapsadas: são **recusadas *fail-closed***, porque a sua projeção produziria **três ou mais `LF` consecutivos**, representação proibida por **`D4`** e **`D7`**. |
| MT7 | **Linha vazia nas bordas — recusada.** Uma linha `>` **antes da primeira** linha de conteúdo, ou **depois da última**, é **recusada *fail-closed***: a saída **não pode começar nem terminar em `LF`** (**`D7`**). |
| MT8 | **Terminadores físicos aceitos.** O futuro extrator aceita **`LF`** e **`CRLF`** como terminador **físico**, tratando-os como equivalentes **somente nessa fronteira de extração**. Para `CRLF`, o `CR` **pertencente ao par** é removido e produz-se **somente o `LF` canônico** correspondente. **Isso não altera `D5`**, que continua valendo para a representação canônica: **nenhum `CR` pode permanecer na saída**. São **recusados *fail-closed***: `CR` isolado, `U+2028`, `U+2029`, `U+0085`, `U+000B`, `U+000C` e qualquer outro terminador não autorizado. **Proibido** *universal newline* implícito e **proibido** qualquer mecanismo cuja política varie conforme o ambiente. |
| MT9 | **Quebra suave.** Duas linhas físicas de conteúdo **consecutivas** pertencem ao **mesmo parágrafo**. Removidos os prefixos `> `, a fronteira física entre elas é projetada para **exatamente um `LF` (`U+000A`)** na representação canônica. O extrator **não** substitui esse `LF` por espaço: a conversão `LF` → `U+0020` pertence à **normalização de `C-15b`**, conforme **`D3`**. **Extrator produz representação canônica; comparador normaliza a quebra suave.** As duas responsabilidades **não se fundem**. |
| MT10 | **Whitespace adjacente a quebra.** Whitespace que produziria representação não canônica **não é corrigido silenciosamente**. É **recusada *fail-closed*** a linha de conteúdo com **espaço** ou **tab imediatamente antes** do terminador físico. Removido o prefixo, a saída deve satisfazer **`D7`**: **zero** espaço/tab imediatamente **antes** de `LF` e **zero** imediatamente **depois** de `LF`. O espaço obrigatório de `> ` pertence **somente** ao prefixo estrutural e é **removido**. |
| MT11 | **Dois desfechos conceituais.** **Sucesso**: produz uma `str` **não vazia** já pertencente ao domínio canônico **`D1`–`D7`**. **Falha**: recusa **explícita** e ***fail-closed***. **Nunca**: devolver texto parcialmente convertido; corrigir sintaxe; inferir intenção; aplicar CommonMark como autoridade; ou normalizar conteúdo arbitrariamente. |
| MT12 | **Taxonomia não decidida.** A taxonomia técnica concreta de exceções, o nome de módulo, o nome de função, a assinatura, a ordem de parâmetros e o texto de mensagem **não** são definidos aqui: pertencem a **mandato técnico posterior**. |

**Relação com o leitor da representação marcada.** `ler_unidades_marcadas`
(`src/casa77_sdr/response_markdown_units.py`) continua responsável **apenas** por
**reconhecimento estrutural**, **identidade** e **tokens canônicos `<Rxx>/<id>`**. A futura
fronteira de **extração textual** poderá impor a convenção estrita acima sobre um bloco **já
estruturalmente reconhecido** — responsabilidade **diferente**. **Nenhuma alteração daquele
módulo é autorizada por esta arbitragem**, e nenhuma é feita.

**O que esta arbitragem destrava — e somente isto.** Uma **futura** entrega funcional de
**extração determinística do conteúdo textual emitível**, que poderá receber a representação
marcada **já em memória** e produzir texto canônico para `C-15b` **sem inventar** regras de
prefixo, de parágrafo, de quebra suave, de terminador físico ou de recusa de sintaxe inválida.
**Essa entrega não é implementada aqui e não é escolhida aqui.**

**Risco arquitetural — terminação de linha.** *Checkouts* e ambientes podem materializar
terminações de linha distintas das do repositório. **`MT8`** fecha a política **do extrator**
diante disso; esta arbitragem **não altera `.gitattributes`**, **não decide configuração de
Git** e **não afirma** que qualquer configuração seja universal.

**Fora desta arbitragem**, e explicitamente **não decididos**: propagação de status ao
fragmento; mapeamento de `PARCIAL`; sintaxe de *placeholder*; gramática de `caminho_yaml`;
formato `hora`; **C-7**; extração do **rótulo de status**; índice físico; *bindings*;
`ASSERTIVA` física; *renderer*; execução física da bijeção; satisfação de
`C-A1-ST6`–`C-A1-ST10`; migração da autoridade de status; consumidores;
**`OrquestradorMotor`**; **R2**; **S2-D8**; **`N-b-RES2`**; e `.gitattributes`.
**CONVERTER O BLOCO MARCADO EM TEXTO CANÔNICO NÃO É MATERIALIZAR `C`.**

##### C-A1-F — Refinamentos normativos de C-6

**Nenhum formato novo é criado.** O vocabulário de C-6 permanece fechado; o que segue é
**refinamento** da sua leitura, segundo **`C-P`**.

| # | Formato | Refinamento |
|---|---|---|
| C-A1-F1 | `inteiro_agrupado` | **o mesmo inteiro**, com **uma única** convenção de agrupamento, **fechada e determinística** para o MVP. **Sem arredondamento, sem cálculo e sem alteração do valor.** |
| C-A1-F2 | `simbolo_moeda` | opera sobre uma **tabela fechada** de códigos monetários suportados pelo MVP. A entrada é **somente** o código **explicitamente recebido por *binding*** (C-6c). **Código não suportado → FALHA.** **Nunca inferir moeda** e **nunca ler outro campo implicitamente**. A tabela pertence ao **contrato/implementação do formato**, **não ao índice**. |
| C-A1-F3 | `hora` | **dois padrões fechados**: `HH:MM` — representação **geral** — e `Hh` — permitido **somente quando os minutos são `00`**. Minutos diferentes de `00` com `Hh` → **FALHA**. **Sem fuso, sem cálculo e sem arredondamento.** |
| C-A1-F3a | `hora` — **regra mecânica de escolha** | Dentro dos **dois padrões já fechados por `C-A1-F3`**, e **sobre o valor de hora já resolvido**: minutos **`00`** → **`Hh`**; minutos **diferentes de `00`** → **`HH:MM`**. A regra é **total** e **determinística** — para todo valor admissível existe exatamente uma representação. Apresentação **pura** (`C-6`, `C-8`): **não calcula, não arredonda, não converte fuso, não consulta locale e não lê campo adicional**. **`C-A1-F3` permanece literal**: os dois padrões continuam sendo os únicos admissíveis, e **`Hh` continua proibido** com minutos diferentes de `00`. **Nenhum horário concreto é fixado por esta regra** — a escolha depende exclusivamente do valor recebido. |
| C-A1-F3b | `hora` — dígitos | Em `HH:MM`, `HH` e `MM` têm exatamente dois dígitos ASCII, com zero à esquerda. Em `Hh`, `H` é a hora sem zero à esquerda — um dígito de `0` a `9`, dois de `10` a `23`. Fecha somente a quantidade de dígitos; nenhum horário concreto é fixado. |

**`C-A1-F3a` e `C-A1-F3b` fecham a matéria normativa do formato `hora`; por si sós, não
materializam `C`.** Os dois padrões de `C-A1-F3` continuam sendo os únicos admissíveis, a
escolha entre eles continua determinada pelo minuto recebido e a contagem de dígitos de cada
um está fechada. Nenhum horário concreto é fixado aqui, e nenhum índice, *placeholder* ou
consumidor é criado por esta arbitragem.

##### C-A1-L — Convenção final do formato `lista`

Refinamento de **C-6f**, **não** formato novo.

| # | Cardinalidade | Apresentação |
|---|---|---|
| C-A1-L1 | zero itens | **FALHA** |
| C-A1-L2 | um item | `A` |
| C-A1-L3 | dois itens | `A e B` |
| C-A1-L4 | três ou mais | `A, B, C e D` |

| # | Regra |
|---|---|
| C-A1-L5 | preservar **todos** os itens e a **ordem** |
| C-A1-L6 | cada item é **texto literal** |
| C-A1-L7 | **sem prefixo por item**, **sem sufixo semântico por item** |
| C-A1-L8 | **sem** filtragem, reordenação, flexão, paráfrase ou transformação semântica |

##### C-A1-R — C-5 permanece fechado

O vocabulário de predicados continua **exatamente** `EH_VERDADEIRO` e `EH_FALSO` (C-5g,
C-5h). **Nenhum predicado novo.** Ficam **explicitamente rejeitados** por C-A1:

| # | Rejeitado |
|---|---|
| C-A1-R1 | predicado para `null` |
| C-A1-R2 | comparação com literal |
| C-A1-R3 | igualdade entre dois caminhos **dentro de C** |
| C-A1-R4 | conversão de caixa |
| C-A1-R5 | pluralização |
| C-A1-R6 | numeral por extenso |
| C-A1-R7 | prefixo linguístico por item |

A **igualdade entre caminhos** continua **fora de C** e pertence ao futuro
`ValidadorConsistenciaBase`.

##### C-A1-S — Seleção em coleção

| # | Regra |
|---|---|
| C-A1-S1 | **Seleção posicional é PROIBIDA** — dentro e fora de iteração. |
| C-A1-S2 | Em `itera_sobre` (C-2j): percorre-se a coleção e os *bindings* usam **caminhos relativos**; **nenhum índice posicional**. |
| C-A1-S3 | Fora de `itera_sobre`, selecionar **exatamente um** item exige **identificador estrutural estável e não comercial**. |
| C-A1-S4 | Esse identificador **vive no YAML como metadado estrutural**; **não** é preço, **não** é condição comercial, **não** é texto de resposta; **pode** ser referenciado pelo caminho do índice; e **não pode depender da posição** do item. |
| C-A1-S5 | Se uma coleção necessária **não** tiver identificador estável, a **futura modelagem** deve **adicionar um** — **sem** transformar a coleção em mapa apenas por isso (**MD-18**). |

##### C-A1-B — Unidade de bijeção

| # | Regra |
|---|---|
| C-A1-B1 | A unidade da bijeção é o **fragmento emitível** — **não** o `Rxx` agregado. |
| C-A1-B2 | Notas e instruções internas ficam **fora da bijeção**: **sem status**, **sem *binding***, **sem `ASSERTIVA`**, e **não podem ser emitidas acidentalmente** (C-2m–C-2p). |
| C-A1-B3 | Cada fragmento do índice corresponde a **exatamente uma** unidade emitível do Markdown. |
| C-A1-B4 | Cada unidade emitível do Markdown corresponde a **exatamente um** fragmento do índice. |

##### C-A1-ST — Status e migração de autoridade

O vocabulário **C-3** permanece: `APROVADO`, `AGUARDA_APROVACAO`, `BLOQUEADO`. **Nenhum
quarto status.**

| # | Markdown | Fragmento |
|---|---|---|
| C-A1-ST1 | `APROVADO` | `APROVADO` |
| C-A1-ST2 | `AGUARDA APROVAÇÃO` | `AGUARDA_APROVACAO` |
| C-A1-ST3 | `APROVADO com handoff obrigatório` | `APROVADO` — o **sufixo de handoff** é instrução operacional e fica **fora de C** (C-2f, C-5.1) |
| C-A1-ST4 | `PARCIAL` | **não é traduzido automaticamente**; exige **mapeamento explícito no nível dos fragmentos emitíveis** |
| C-A1-ST5 | `BLOQUEADO` em **nota interna** | **não cria fragmento** e **não cria status** |

A **autoridade do status** só migra para o índice quando **as cinco** condições valem:

| # | Condição de migração |
|---|---|
| C-A1-ST6 | índice **estruturalmente válido** |
| C-A1-ST7 | **bijeção integral validada** (C-A1-B3, C-A1-B4) |
| C-A1-ST8 | status de **todos** os fragmentos resolvidos |
| C-A1-ST9 | *bindings* e `ASSERTIVA` válidos |
| C-A1-ST10 | **equivalência C-15** satisfeita **ou** nova aprovação de conteúdo obtida |

Antes disso, `knowledge/respostas-aprovadas.md` **continua a autoridade de status** (C-11).

##### Propagação do status de `Rxx` aos fragmentos

Refinamento que fecha, segundo **`C-P`**, **uma única** matéria: **como o
status de um `Rxx`, uma vez que o seu rótulo já tenha sido corretamente identificado, é
propagado aos fragmentos emitíveis daquele `Rxx`**. Ela **não** reescreve, renumera ou
substitui `C-1`–`C-15`, `C-A1-ST`, `C-A5` ou `MT1`–`MT12`, **não** cria versão concorrente
deles, **não** altera o vocabulário fechado de **`C-3`** e **não** cria identificador
normativo novo: os rótulos **`SP1`**–**`SP7`** abaixo são **locais deste bloco**, existem só
para referência interna e **não** são etapa, subetapa, `Exx` nem nomenclatura normativa de
`C`. Este bloco define somente o contrato; a implementação de módulo, função, assinatura, exceção
e mensagem técnica pertence à fronteira executora correspondente.

**Pré-condição explícita, e limite duro do escopo.** A expressão **"rótulo já corretamente
identificado"** é **pré-condição** desta arbitragem, **não** resultado dela. Esta arbitragem
**NÃO decide**: como **localizar** o rótulo na linha física do cabeçalho; **separadores** do
cabeçalho; **posição física** do rótulo; **gramática do título**; ***parsing*** de `## Rxx`;
nem **algoritmo de extração** do rótulo. **Essas matérias permanecem ABERTAS** como decisão
normativa/técnica **futura e separada** — e **não** são atribuídas por antecipação a um
futuro executor. O que segue vale **exclusivamente** para um rótulo **já** corretamente
identificado e associado ao seu `Rxx`.

A alternativa adotada é **PROPAGAÇÃO UNIFORME / FAIL-CLOSED**.

| # | Decisão |
|---|---|
| SP1 | **Escopo.** A regra opera **conceitualmente** sobre **um `Rxx`**, **os seus fragmentos emitíveis declarados** e **um rótulo de status já corretamente identificado e associado àquele `Rxx`**. Ela **não extrai coisa alguma do Markdown**, **não analisa Markdown**, **não localiza cabeçalho**, **não localiza rótulo** e **não decide de onde o rótulo veio**. |
| SP2 | **`ST1`–`ST3` — propagação uniforme.** Quando o rótulo associado ao `Rxx` for **EXATAMENTE** uma das **três** traduções automáticas já fechadas por **`C-A1-ST1`**, **`C-A1-ST2`** e **`C-A1-ST3`**, o **status canônico correspondente** é aplicado **uniformemente a TODOS os fragmentos emitíveis daquele `Rxx`**. A tradução continua sendo **exatamente** a já materializada por `canonicalizar_status(rotulo: str) -> str` (`src/casa77_sdr/response_status.py`), **sem alteração**. **Nenhuma quarta tradução é criada** e o vocabulário de **`C-3`** permanece fechado. |
| SP3 | **Sem exceção por posição ou conteúdo.** Dentro de um `Rxx` coberto por `ST1`–`ST3`, **todos** os seus fragmentos recebem **o mesmo** status canônico derivado. É **proibido** decidir status por **posição** do fragmento, **ordem**, **índice**, **redação**, **conteúdo**, **quantidade de fragmentos** ou **`id`** — o que preserva literalmente **`C-A5-I5`** e **`C-A5-M6`**. **Nenhuma exceção implícita**, e **nenhum fragmento de um mesmo `Rxx` recebe status divergente**. |
| SP4 | **`PARCIAL`.** Permanece sujeito **integralmente** a **`C-A1-ST4`**: **não** recebe tradução automática; **não** recebe propagação automática; **não** é convertido em quarto status; **não** é convertido em `APROVADO`; **não** é convertido em `AGUARDA_APROVACAO`; **não** é convertido em `BLOQUEADO`. Enquanto **não existir mapeamento explícito aprovado no nível dos fragmentos emitíveis**, **o status dos fragmentos daquele `Rxx` permanece NÃO RESOLVIDO** — ***fail-closed***, **sem inferência**. |
| SP5 | **Rótulo sem tradução automática.** Qualquer rótulo que **não** pertença às traduções automáticas de `ST1`–`ST3` **não produz status propagado automaticamente** — e isso **inclui o caso `PARCIAL`**. A **ausência de tradução não é corrigida, normalizada nem inferida**, e **não** é lacuna a ser fechada por conveniência: ela é o comportamento arbitrado. |
| SP6 | **Autoridade.** O status propagado é **DERIVADO** da autoridade Markdown vigente. Ele **não cria declaração de status adicional** no Markdown de cada fragmento — **`C-2d`** continua valendo (**sem status armazenado no nível do `Rxx`**) e o Markdown **não é alterado** por esta arbitragem. O **futuro índice** poderá **armazenar status por fragmento** conforme **`C-2i`**, e **isso NÃO migra a autoridade**: até que **`C-A1-ST6`–`C-A1-ST10`** estejam **integralmente satisfeitas**, `knowledge/respostas-aprovadas.md` **continua a autoridade de status** (**`C-11`**). |
| SP7 | **Limites.** Propagar status **NÃO**: cria índice; cria fragmento; altera identidade; extrai rótulo; resolve `PARCIAL`; executa a bijeção física; satisfaz **`ST6`**; satisfaz **`ST7`**; satisfaz **`ST8`** integralmente; satisfaz **`ST9`**; satisfaz **`ST10`**; migra a autoridade de status; nem **materializa `C`**. |

**Escopo de SP.** `SP` fecha a **semântica de propagação** sob `ST1`–`ST3`, para rótulos **já
corretamente identificados**. As demais matérias **não pertencem a SP** e são regidas pelos
respectivos contratos deste documento — em particular **`C-A1-ST4`** para `PARCIAL`, e
**`C-A5-X3`**/**`C-A5-X4`**, que permanecem **literais**.

**Limites deste bloco.** A **autoridade de status** permanece em
`knowledge/respostas-aprovadas.md` enquanto **`C-A1-ST6`–`C-A1-ST10`** não estiverem
satisfeitas (**`C-11`**). **PROPAGAR STATUS NÃO É EXTRAIR RÓTULO, NÃO É RESOLVER `PARCIAL`,
NÃO É MIGRAR AUTORIDADE E NÃO É MATERIALIZAR `C`.**

##### Gramática física do rótulo de status no cabeçalho `Rxx`

Refinamento que fecha, segundo **`C-P`**, **uma única** matéria: **qual é a
gramática física determinística do rótulo de status em um cabeçalho `Rxx`**. Ela **não**
reescreve, renumera ou substitui `C-1`–`C-15`, `C-A1-ST`, `C-A5`, `MT1`–`MT12` ou `SP1`–`SP7`,
**não** cria versão concorrente deles, **não** altera o vocabulário fechado de **`C-3`** e
**não** cria identificador normativo novo: os rótulos **`GR1`**–**`GR7`** abaixo são **locais
deste bloco**, existem só para referência interna e **não** são etapa, subetapa, `Exx` nem
nomenclatura normativa de `C`. Este bloco define somente o contrato; a implementação de módulo, função, assinatura, exceção
e mensagem técnica pertence à fronteira executora correspondente.

**Esta arbitragem NÃO arbitra propagação** — isso é `SP1`–`SP7`, já fechado —, **NÃO arbitra
`PARCIAL`**, **NÃO cria índice**, **NÃO decide ordem de chamadas entre módulos** e **NÃO
escolhe assinatura ou módulo futuro.**

A forma física completa arbitrada, chamada **`G2`** neste bloco, é:

```text
## Rxx — <titulo> — <rotulo>
```

com o **separador literal** de **três caracteres**, `U+0020 U+2014 U+0020` — **SPACE + EM
DASH + SPACE**.

| # | Decisão |
|---|---|
| GR1 | **Domínio.** A gramática aplica-se **exclusivamente** a uma linha que **já satisfaça a forma estrutural de cabeçalho `## Rxx`** reconhecida pelas regras vigentes. Ela **não define ordem de chamadas**, **não decide composição técnica** e **não altera** `C8`, `C-A5`, `C-A1-ST` ou `SP1`–`SP7`. O reconhecimento estrutural do cabeçalho **permanece exatamente como está**, e os detalhes técnicos já existentes no leitor da representação marcada continuam sendo **detalhes técnicos**, **não** norma nova. |
| GR2 | **Forma física — `G2`.** **`GR2.1`** o separador literal ocorre **EXATAMENTE DUAS VEZES** na linha. **`GR2.2`** `<titulo>` é **não vazio**. **`GR2.3`** `<rotulo>` é **não vazio**. **`GR2.4`** nem título nem rótulo podem **começar ou terminar** com **espaço ASCII `U+0020`** ou **tab `U+0009`**. **`GR2.5`** uma **terceira** ocorrência do separador literal é **inválida**. **`GR2.6`** **menos de duas** ocorrências é **inválida**. **`GR2.7`** **não são equivalentes** ao separador: `-` (`U+002D`), `–` (`U+2013`) ou qualquer outro caractere semelhante. **`GR2.8`** espaçamento divergente **não é corrigido**. **`GR2.9`** são **proibidos** `strip`, `lstrip`, `rstrip`, normalização, colapso de espaços, inferência e tolerância implícita. **`GR2.10`** o rótulo obtido é **literal/opaco**, e a gramática **NÃO decide pertença a `ST1`–`ST3`**. |
| GR3 | **Rótulo literal.** O rótulo é **literal e opaco**: **zero tradução**, **zero normalização**, **zero canonicalização**, **zero inferência**. A tradução das **três** linhas automáticas de **`C-A1-ST1`**–**`C-A1-ST3`** continua sendo responsabilidade de `canonicalizar_status(rotulo: str) -> str` (`src/casa77_sdr/response_status.py`), **não alterado por esta arbitragem**. Identificar fisicamente um rótulo **não é** canonicalizá-lo. |
| GR4 | **Fail-closed.** Forma divergente de `G2` é **recusada**, **nunca corrigida, normalizada ou inferida**. As espécies de impedimento são, **apenas conceitualmente** nesta norma: **separador ausente**; **cardinalidade de separador diferente de 2**; **segmento vazio**; e **branco de borda**. **NÃO** são definidos aqui **nome de exceção**, **mensagem**, **módulo**, **função** ou **assinatura** — isso pertence a mandato técnico posterior. |
| GR5 | **Título.** O `<titulo>` é **obrigatório para satisfazer a forma física**. Ele **não é produto da futura extração** — o que se busca extrair é o **rótulo** — e **não recebe semântica comercial nova** por esta arbitragem. |
| GR6 | **Resultado conceitual.** Uma **futura** fronteira poderá produzir uma **associação** entre o **`Rxx`** e o **`rotulo_literal`**. **Não** são fixados aqui: nome da função; assinatura; estrutura exata de retorno; exceção; mensagem; ordem de chamadas; nem composição técnica. |
| GR7 | **Limites.** Esta arbitragem fecha **SOMENTE** a **gramática física necessária para identificar deterministicamente o rótulo de status em um cabeçalho `Rxx`**. Ela **NÃO** fecha: **`PARCIAL`**; a **representação física do mapeamento de `PARCIAL`**; o **índice**; ***bindings***; ***placeholder***; **`caminho_yaml`**; **`hora`**; **C-7**; a **bijeção física**; **`C-A1-ST6`–`C-A1-ST10`**; nem a **migração de autoridade**. |

**`PARCIAL` — extraível fisicamente, ainda não resolvido.** O rótulo `PARCIAL` é
**fisicamente extraível pela mesma gramática `G2`**, exatamente como qualquer outro rótulo.
Isso **não muda coisa alguma** quanto ao seu tratamento: ele **NÃO** recebe tradução
automática, **NÃO** recebe propagação automática, **NÃO** é quarto status, **continua sob
`C-A1-ST4`** e **continua sob `SP4`/`SP5`**, permanecendo **pendente de mapeamento explícito
futuro** no nível dos fragmentos emitíveis. **EXTRAIR `PARCIAL` NÃO É RESOLVER `PARCIAL`.**

**Relação com `C-A5-X2`.** **`C-A5-X2`** delimita o escopo original de `C-A5`. **SP** rege a
**propagação** e **PM** rege a **representação estrutural de `PARCIAL`**; a **aplicação
física** e o **estado de execução** pertencem a `docs/00-estado-atual.md`.

**Limites deste bloco.** A **autoridade de status** permanece em
`knowledge/respostas-aprovadas.md` enquanto **`C-A1-ST6`–`C-A1-ST10`** não estiverem
satisfeitas (**`C-11`**). **ARBITRAR A GRAMÁTICA FÍSICA DO RÓTULO NÃO É EXTRAIR O RÓTULO,
NÃO É CANONICALIZAR STATUS, NÃO É RESOLVER `PARCIAL`, NÃO É MIGRAR AUTORIDADE E NÃO É
MATERIALIZAR `C`.**

##### Mapeamento físico de status por fragmento sob `PARCIAL`

Refinamento que fecha, segundo **`C-P`**, **uma única** matéria: **a
representação física e as regras estruturais do status explícito por fragmento quando o
cabeçalho `G2` do respectivo `Rxx` contém o rótulo `PARCIAL`**. Ela **não** reescreve,
renumera ou substitui `C-1`–`C-15`, `C-A1-ST`, `C-A1-P`, `C-A5`, `MT1`–`MT12`, `SP1`–`SP7` ou
`GR1`–`GR7`, **não** cria versão concorrente deles, **não** altera o vocabulário fechado de
**`C-3`** e **não** cria identificador normativo novo: os rótulos **`PM1`**–**`PM12`** abaixo
são **locais deste bloco**, existem só para referência interna e **não** são etapa, subetapa,
`Exx` nem nomenclatura normativa de `C`. Este bloco define somente o contrato; a implementação de módulo, função, assinatura, exceção
e mensagem técnica pertence à fronteira executora correspondente.
Este contrato **não atribui status a fragmento algum** e **não altera `knowledge/**`**.

**Esta arbitragem NÃO arbitra propagação** — isso é `SP1`–`SP7`, já fechado —, **NÃO altera a
gramática do cabeçalho** — isso é `GR1`–`GR7`, já fechado —, **NÃO altera `C8`, `C11`, `C12`
ou `C13`**, **NÃO cria índice**, **NÃO decide ordem de chamadas entre módulos** e **NÃO
escolhe assinatura ou módulo futuro.**

A forma física completa arbitrada é:

```text
<!-- status-fragmento: <valor> -->
<!-- fragmento: <id> -->
> conteúdo
```

| # | Regra |
|---|---|
| PM1 | **Portador.** A declaração é a **linha física própria** `<!-- status-fragmento: <valor> -->`. O envelope é **EXATO**: prefixo literal `<!-- status-fragmento: `, seguido de `<valor>`, seguido do sufixo literal ` -->`. **Nada antes** do prefixo e **nada depois** do sufixo na mesma linha. **Zero `strip`**, **zero normalização**, **zero tolerância implícita**: indentação, espaço adicional, tab, prefixo ou sufixo divergente **não** satisfazem o envelope. |
| PM2 | **Posição.** A declaração ocupa a **linha imediatamente anterior** ao marcador `C-A5`, com **zero linha física** entre ambos. O marcador continua ocupando a **linha imediatamente anterior à primeira linha do bloco**, com **zero linha em branco** — **`C-A5-I1`** e **`C-A5-I2`** são **preservados literalmente**. A declaração **NUNCA** fica entre o marcador e o bloco. |
| PM3 | **Associação.** A declaração associa-se ao **marcador `C-A5` válido existente na linha imediatamente seguinte**. Essa associação é **adjacência estrutural status → marcador**, e **NÃO** é: identidade; parte do token; parte do `id`; nem posição usada para **definir** identidade — **`C-A5-I5`** permanece intacto. A identidade continua **exclusivamente** `<Rxx>/<id>` (**`C-A5-T1`**, **`C-A5-T2`**). A declaração **não contém `id`**, **não duplica `id`**, **não cria identidade** e **não altera identidade**. |
| PM4 | **Vocabulário — `V1`, status canônico direto.** `<valor>` é **EXATAMENTE UM** dos **três** valores de **`C-3`**: `APROVADO`, `AGUARDA_APROVACAO` ou `BLOQUEADO`. **Sem quarto valor.** **`PARCIAL` é INVÁLIDO como valor.** Os rótulos físicos de `ST1`–`ST3` **não** são usados neste campo, **`canonicalizar_status` não é chamado** e **nenhuma tabela de tradução é criada** — o campo já carrega o status canônico. A comparação futura é **literal**, com **tipo e forma fechados**: **zero `strip`**, **zero tolerância de caixa**, **zero `NFC`**, **zero coerção**. |
| PM5 | **Cardinalidade.** Sob cabeçalho `G2` cujo rótulo seja `PARCIAL`, **cada** fragmento emitível possui **EXATAMENTE UMA** declaração física válida de `status-fragmento`. **Nenhuma** declaração é ***fail-closed***; **duas ou mais** para o mesmo marcador são ***fail-closed***. **Nenhuma inferência** e **nenhum valor padrão** — o que preserva `C-3` (**sem valor padrão**; fragmento sem status é **erro de contrato**, nunca `APROVADO` implícito). |
| PM6 | ***Fail-closed*.** São **conceitualmente inválidos**: declaração **ausente**; declaração **órfã**; **múltiplas** declarações para o mesmo marcador; declaração **fora de seção `Rxx`**; declaração **sem marcador válido imediatamente seguinte**; **linha em branco** entre declaração e marcador; **valor fora de `C-3`**; **`PARCIAL` como valor**; ***whitespace* divergente**; **conteúdo adicional** na linha; e **envelope divergente que deixe o marcador sem a declaração obrigatória**. **NÃO** são definidos aqui **classe Python**, **nome de exceção**, **mensagem técnica**, **função**, **módulo** ou **assinatura** — isso pertence a futura materialização técnica. |
| PM7 | **Proibição sob `ST1`–`ST3`.** Sob cabeçalho cujo rótulo pertença a `C-A1-ST1`, `C-A1-ST2` ou `C-A1-ST3`, a declaração `status-fragmento` é **PROIBIDA** — **mesmo** que o valor explícito coincida com o status que `SP2`/`SP3` propagariam. Razão: `SP2`/`SP3` já definem **propagação uniforme**; permitir a declaração criaria **duas fontes concorrentes ou redundantes** de status dentro da autoridade Markdown e comprometeria **`SP6`**. Forma divergente é ***fail-closed***. |
| PM8 | **Autoridade.** A declaração vive na **autoridade Markdown vigente** e é a **fonte explícita** do status do fragmento sob `PARCIAL`. O **futuro índice** poderá armazenar esse status **por fragmento** conforme **`C-2i`**, e **isso NÃO migra autoridade**: até que **`C-A1-ST6`**–**`C-A1-ST10`** estejam **integralmente satisfeitas**, `knowledge/respostas-aprovadas.md` **continua a autoridade de status** (**`C-11`**). |
| PM9 | **Não emissão.** `status-fragmento` **NÃO** é fragmento emitível, **NÃO** é nota comercial, **NÃO** é instrução emitível, **NÃO** recebe *binding*, **NÃO** recebe `ASSERTIVA` e **NÃO** pode ser emitido ao interessado. **`C-2m`**–**`C-2p`** e **`C-A5-U4`** são **preservados**. Ela também **não** é bloco de citação e, portanto, **não** entra na bijeção de **`C-A1-B3`** / **`C-A1-B4`**. |
| PM10 | **Política de linha.** Reutiliza-se **integralmente** a política estrutural já vigente em `C8`/`C12`: divisão **exclusivamente por `LF`**; **no máximo um `CR` terminal** removido por segmento; **sem `splitlines()`**; **sem *universal newline***. **Nenhuma terceira política é criada.** `CR` residual, `U+2028`, `U+2029`, `U+0085`, `VT`, `FF` e `U+00A0` **permanecem conteúdo literal** conforme a política estrutural vigente, e o **envelope precisa permanecer literal**. |
| PM11 | **Significado físico de `PARCIAL`.** **No Markdown vigente, o rótulo físico `PARCIAL` ativa o regime de STATUS EXPLICITAMENTE DECLARADO POR FRAGMENTO.** Nesta fronteira ele significa **exatamente**: **não** aplicar propagação automática do cabeçalho; **exigir** uma declaração `status-fragmento` para **cada** fragmento; e **resolver cada fragmento individualmente** por valor de `C-3` explícito. `PARCIAL` **NÃO** é status canônico, **NÃO** é armazenado no `Rxx` do índice, **NÃO** é armazenado no fragmento, **NÃO** é convertido em quarto status, **NÃO** exige dois ou mais status distintos, **NÃO** exige mistura de status e **NÃO** exige cardinalidade mínima de dois fragmentos. Uma seção fisicamente rotulada `PARCIAL` pode ter **um** fragmento ou **vários**, **todos com o mesmo status** ou **com status distintos**. **Isso NÃO define uma função geral de agregação de status de `Rxx`.** |
| PM12 | **Limites.** Esta arbitragem **NÃO**: atribui status real; altera `knowledge/**`; altera `C8`, `C11`, `C12` ou `C13`; implementa *parser*; implementa a próxima entrega funcional; cria índice; executa a bijeção física; satisfaz **`C-A1-ST6`**, **`C-A1-ST7`**, **`C-A1-ST8`**, **`C-A1-ST9`** ou **`C-A1-ST10`**; migra a autoridade de status; resolve *binding*; resolve *placeholder*; resolve `caminho_yaml`; resolve **C-7**; cria subetapa; nem **materializa `C`**. |

**Relação com `C-3`, sem reescrita.** **`C-3` permanece literal e não é reescrita.** O **modelo
futuro** continua exatamente como está: o **`Rxx` não armazena status** (**`C-2d`**);
**`PARCIAL` nunca é valor armazenado**; e os **únicos status armazenáveis pertencem aos
fragmentos** e são os **três** de `C-3` (**`C-2i`**). Esta micro-arbitragem **NÃO cria nem
define um campo de "status agregado do `Rxx`"**. O rótulo físico, histórico e de Markdown
`PARCIAL` é **o sinal de que, naquela seção, a autoridade precisa fornecer status explícito
por fragmento**, conforme **`C-A1-ST4`**. Portanto, **o rótulo físico `PARCIAL` NÃO é tratado
aqui como resultado de uma nova função computacional de agregação**, e **nenhuma função
agregadora geral é criada**. A observação de `C-3` de que um `Rxx` agregado pode ser parcial
**apenas como derivação** dos status dos seus fragmentos **permanece literal e inalterada**.

**Quase-declaração — o padrão de `C8` é preservado.** Uma linha que **não** satisfaça o
envelope exato de `PM1` **não** é automaticamente "uma declaração inválida": ela **permanece
conteúdo comum**, exatamente como uma quase-marcação permanece conteúdo comum sob `C-A5`.
Porém, **sob `PARCIAL`**, se disso resultar um marcador `C-A5` **sem** a declaração válida
obrigatória imediatamente anterior, **`PM5` falha por declaração ausente**. **Nenhuma intenção
é inferida**: a fronteira não tenta adivinhar que a linha "queria ser" uma declaração.

**`C-A1-P2` preservada.** **Nota interna continua não sendo fragmento**, continua **não
recebendo status**, continua **não bloqueando automaticamente** fragmento e continua **não
determinando automaticamente** o valor de `status-fragmento`. **Nada é inferido** — nem
`APROVADO`, nem `AGUARDA_APROVACAO`, nem `BLOQUEADO` — a partir de nota interna, de `null`, de
conteúdo, de posição ou de contexto. O valor é **declarado explicitamente por ato humano**, ou
não existe.

**`PARCIAL` — a distinção que importa.** A **norma estrutural** é **FECHADA** quanto a:
**portador**; **posição**; **associação**; **vocabulário**; **cardinalidade**;
***fail-closed***; **proibição sob `ST1`–`ST3`**; e **significado físico de `PARCIAL`**. Este
contrato **não atribui status a fragmentos do corpus**: cada status exige **declaração humana
explícita** conforme as regras desta seção. O **estado de aplicação ao corpus** pertence a
`docs/00-estado-atual.md`.

**Relação com `C-A5-X2`.** **`C-A5-X2`** delimita o escopo original de `C-A5`. **SP** rege a
**propagação** e **PM** rege a **representação estrutural de `PARCIAL`**; a **aplicação
física** e o **estado de execução** pertencem a `docs/00-estado-atual.md`.

**Limites deste bloco.** A **autoridade de status** permanece em
`knowledge/respostas-aprovadas.md` enquanto **`C-A1-ST6`–`C-A1-ST10`** não estiverem
satisfeitas (**`C-11`**). **ARBITRAR A REPRESENTAÇÃO FÍSICA DO STATUS POR FRAGMENTO NÃO É
ATRIBUIR STATUS, NÃO É ALTERAR O CORPUS, NÃO É IMPLEMENTAR PARSER, NÃO É RESOLVER `PARCIAL`
E NÃO É MATERIALIZAR `C`.**

**DECISÃO HUMANA DE STATUS DE `R28/F1`. NÃO É REGRA, NÃO É `PM13` E NÃO ALTERA
`PM1`–`PM12`.** O que segue é **registro de um ato de autoridade humana**: ele **não** cria
rótulo local novo, **não** renumera, **não** reinterpreta e **não** altera nenhuma das regras
`PM1` a `PM12`, que permanecem **literais**.

**Existe decisão humana explícita para `R28/F1`, e o valor decidido é `APROVADO`.** O valor
pertence ao **vocabulário fechado de `C-3`** (`C-3a`). A decisão é **humana e deliberada**:
ela **NÃO** foi inferida de nota interna, **NÃO** foi inferida de `null`, **NÃO** foi inferida
de conteúdo, **NÃO** foi inferida do rótulo físico `PARCIAL` do cabeçalho e **NÃO** foi
escolhida por ferramenta ou modelo algum. Isso é exatamente o que **`C-A1-P2`** e **`PM11`**
exigem: sob `PARCIAL`, o status **é declarado por ato humano explícito**, nunca derivado.

**A decisão humana e a sua aplicação física são atos distintos.** Um fragmento sob `PARCIAL`
sem a declaração obrigatória de `PM5` **falha por declaração ausente** — esse é o
comportamento correto: **decidir não é aplicar**.

**Forma decorrente da decisão.** Quando aplicada, a representação deve usar **exatamente** a
linha `<!-- status-fragmento: APROVADO -->`, **imediatamente antes** do marcador `C-A5` de
`R28/F1`, com **zero linha física** entre ambos, conforme `PM1` e `PM2`.

**O significado da decisão é estrito.** `APROVADO` significa **somente** o **status canônico
de `C-3` do fragmento emitível `R28/F1`**. A decisão **NÃO** resolve nota interna, **NÃO**
altera `null`, **NÃO** aprova dado comercial, **NÃO** elimina handoff, **NÃO** autoriza emissão
sem as demais validações, **NÃO** decide **S2-D8**, **NÃO** cria `E09`, **NÃO** elimina `E09`,
**NÃO** resolve *binding*, **NÃO** resolve `ASSERTIVA`, **NÃO** resolve **C-8** e **NÃO**
satisfaz **`C-A1-ST8`** isoladamente — `C-A1-ST8` exige o status de **todos** os fragmentos
resolvidos, e **`C-A4-G8`** continua valendo: **cobertura estrutural não é emissibilidade**.

**Limites deste registro.** **`PM1`–`PM12`**, `C-3`, `C-A1-P2`, `C-A1-ST` e `C-A5`
permanecem **literais**. **DECIDIR O STATUS NÃO É APLICAR A DECLARAÇÃO, NÃO É ALTERAR O
CORPUS E NÃO É MATERIALIZAR `C`.**

##### Regime exclusivo de `status-fragmento` sob `PARCIAL`

**NÃO CRIA `PM13`, NÃO RENUMERA, NÃO REINTERPRETA E NÃO ALTERA `PM1`–`PM12`.** Este bloco
**não** cria rótulo local novo — **`PM13` não existe** —, **não** renumera, **não**
reinterpreta e **não** altera nenhuma daquelas doze regras, que permanecem **literais**. Em
particular, **`PM7` não é alterado nem absorvido**: ele continua sendo o **caso particular de
`ST1`–`ST3`**, com **fundamento próprio** — a existência de propagação uniforme por
`SP2`/`SP3` e a preservação de `SP6`.

Ele fecha **uma única** lacuna: **o comportamento de uma linha que satisfaz EXATAMENTE o
envelope de `PM1` dentro de uma seção `Rxx` cujo cabeçalho satisfaz `G2`, mas cujo rótulo
literal NÃO é `PARCIAL`.**

**A decisão.** **`status-fragmento` é PERMITIDO EXCLUSIVAMENTE sob cabeçalho `G2` cujo rótulo
literal seja EXATAMENTE `PARCIAL`.** Sob **qualquer outro** rótulo literal, **a presença de uma
linha que satisfaça exatamente o envelope de `PM1` é *FAIL-CLOSED***.

**Fundamento normativo — exaustivo.** Apenas dois pontos o sustentam, e **nenhum outro é
autorizado**. **`PM8`**: a declaração é a **fonte explícita do status do fragmento *sob
`PARCIAL`***, e **somente** ali. **`PM11`**: é o **rótulo físico `PARCIAL` que ATIVA** o regime
de status explicitamente declarado por fragmento — fora desse regime, **não há regime a
ativar**, e uma declaração seria uma **segunda fonte de status sem regime que a autorize**. **A
composição atual do corpus NÃO é fundamento**: o corpus é **evidência**, jamais origem de
norma.

**Consequências, por regime:**

| Rótulo literal do cabeçalho `G2` | Comportamento de `status-fragmento` |
|---|---|
| `PARCIAL` | **Obrigatório.** `PM5` e `PM11` permanecem **literais**: **exatamente uma** declaração válida por fragmento emitível — nenhuma é *fail-closed*, duas ou mais são *fail-closed*. |
| `APROVADO`, `AGUARDA APROVAÇÃO` ou `APROVADO com handoff obrigatório` (`C-A1-ST1`–`C-A1-ST3`) | **Proibido.** **`PM7` permanece literal**, com o seu fundamento próprio (`SP2`/`SP3` já propagam uniformemente; `SP6` seria comprometido). |
| Qualquer outro rótulo `G2` válido | **Igualmente proibido**, por este registro. A presença de uma declaração exata é *fail-closed*. |
| Fora de seção `Rxx` | **`PM6` permanece literal e aplicável** — declaração fora de seção `Rxx` já é *fail-closed* por `PM6`. |

**`G2` e `SP5` permanecem intactos.** Um rótulo que não pertença a `ST1`–`ST3` nem seja
`PARCIAL` **continua podendo satisfazer `G2`**, **continua literal e opaco** (**`GR2.10`**,
**`GR3`**), **não se torna gramaticalmente inválido**, **não** recebe tradução automática,
**não** recebe propagação automática, **não** é corrigido, **não** é normalizado e **não** é
inferido. **O seu status permanece NÃO RESOLVIDO, conforme `SP5`** — e isso **continua sendo o
comportamento arbitrado**, não uma lacuna. **Este registro proíbe SOMENTE a presença de
`status-fragmento` nesse regime**, e **nada mais**.

**Quatro cláusulas de precisão.**

**1. Ausência não é erro desta regra.** A **ausência** de `status-fragmento` sob rótulo
não-`PARCIAL` **NÃO** é erro — nem desta regra, nem de `PM5`, cuja obrigatoriedade vale
**somente** sob `PARCIAL`. O status daquele `Rxx` permanece **não resolvido por `SP5`**, que é
o comportamento correto.

**2. Somente o envelope exato.** A regra alcança **exclusivamente** a linha que satisfaça
**exatamente** `PM1`. Uma **quase-declaração** — indentada, com *whitespace* divergente, com
conteúdo antes ou depois, com envelope incompleto, com tab, ou com qualquer outra divergência —
**permanece conteúdo comum**, exatamente como sob `C-A5`/`PM6`. **Sob rótulo não-`PARCIAL`,
isso não gera erro `PM` por si só.**

**3. Rótulo desconhecido continua válido.** Esta regra **NÃO** torna inválido um rótulo
desconhecido. **`GR2.10`**, **`GR3`** e **`SP5`** são **preservados**: o rótulo continua
literal, opaco, gramaticalmente válido e sem tradução — o que é proibido ali é **a declaração**,
não **o rótulo**.

**4. Conteúdo emitível está fora.** Uma linha iniciada por `>` **não satisfaz `PM1`** e
**não pertence a esta regra**. Nada aqui toca o bloco de citação, o texto emitível ou
`MT3`–`MT11`.

**Nenhum detalhe técnico é norma aqui.** Este registro **não** define — e **não** autoriza que
se leia dele — módulo, função, assinatura, exceção, categorias técnicas, localizadores,
mensagens, precedência interna de validação, tipo de erro interno, estratégia de importação,
inspeção de árvore sintática ou arquivos futuros. **Tudo isso pertence a mandato técnico
próprio**, ainda **não** emitido.

**Limites deste registro.** **`PM1`–`PM12`** permanecem **literais** e **`PM13` não existe**;
`G2`/`GR1`–`GR7`, `SP1`–`SP7`, `C-3`, `C-A1-ST`, `C-A1-P2` e `C-A5` permanecem **literais**.
**FECHAR A LACUNA NORMATIVA NÃO É IMPLEMENTAR VERIFICAÇÃO, NÃO É APLICAR DECLARAÇÃO, NÃO É
ALTERAR O CORPUS E NÃO É MATERIALIZAR `C`.**

##### Comportamento da futura composição total de status diante de `SP5`

**NÃO CRIA `SP8`, NÃO RENUMERA, NÃO REINTERPRETA E NÃO ALTERA `SP1`–`SP7`.** Este bloco
**não** cria rótulo local novo — **`SP8` não existe** —, **não** renumera, **não**
reinterpreta e **não** altera nenhuma das sete regras `SP`, que permanecem **literais**. Ele
**não** é etapa, subetapa, `Exx` nem identificador normativo, e **não cria subetapa**. Este
bloco define somente o contrato; a implementação de módulo, função, assinatura, exceção e
mensagem técnica pertence à fronteira executora correspondente.

Ele fecha **uma única** matéria: **o que uma FUTURA FRONTEIRA DE COMPOSIÇÃO TOTAL DE STATUS
deve fazer ao encontrar fragmento cujo status permanece NÃO RESOLVIDO pelo ramo de rótulo
desconhecido de `SP5`.**

**Escopo — o que é "composição TOTAL".** Chama-se aqui **composição total de status** uma
futura fronteira **cujo contrato seja resolver e devolver o status de TODOS os fragmentos
emitíveis do documento**. Este registro alcança **exclusivamente** essa espécie de fronteira.
Ele **não** alcança `C8`, `C12`, `C14`, a associação física de seção e fragmentos, a
canonicalização de rótulo (`SP2`) nem a propagação por `Rxx` (`SP1`–`SP3`), e **não** decide o
comportamento de qualquer fronteira futura cujo contrato seja **outro**.

**A decisão — FAIL-CLOSED NA FRONTEIRA DE COMPOSIÇÃO TOTAL.** Quando uma fronteira de
composição total encontrar fragmento pertencente a seção cujo rótulo literal **satisfaça
`G2`** mas **não** pertença às traduções automáticas de `ST1`–`ST3` e **não** seja `PARCIAL`,
ela **FALHA FECHADA**. Especificamente, ela:

**1.** **reconhece** que o status daquele fragmento permanece **NÃO RESOLVIDO por `SP5`**;
**2.** **falha fechada na fronteira de composição total**;
**3.** **não devolve resultado parcial**;
**4.** **não omite silenciosamente** o fragmento;
**5.** **não devolve** o fragmento com marcador ou valor de ausência;
**6.** **não cria valor sentinela**;
**7.** **não cria quarto status** — o vocabulário de **`C-3`** permanece **fechado em três
valores**;
**8.** **não converte** o rótulo;
**9.** **não torna** o cabeçalho `G2` inválido.

**A invariante.** **UM RETORNO BEM-SUCEDIDO DA FUTURA COMPOSIÇÃO TOTAL NÃO PODE COEXISTIR COM
FRAGMENTO NÃO RESOLVIDO POR ESSE RAMO DE `SP5`.** Sucesso total e fragmento não resolvido são
**mutuamente exclusivos** naquela fronteira. **Não existe retorno bem-sucedido contendo esse
fragmento como não resolvido**; **não existe omissão silenciosa**; e **não existe quarto
status**.

**`SP5` permanece semanticamente INTACTA.** Este registro **não** altera coisa alguma do que
`SP5` já arbitrou, e continua verdadeiro que: um rótulo fora das traduções automáticas de
`ST1`–`ST3` **não produz propagação automática**; a **ausência de tradução não é corrigida**,
**não é normalizada** e **não é inferida**; um rótulo desconhecido que satisfaça `G2`
**continua gramaticalmente válido** (**`GR2.10`**, **`GR3`**); o rótulo **continua literal e
opaco**; o seu status **permanece NÃO RESOLVIDO**; e **isso continua sendo o comportamento
arbitrado**, jamais lacuna a fechar por conveniência. **O que este registro fecha é SOMENTE o
comportamento da futura composição TOTAL diante desse estado** — e **nada mais**.

**`PARCIAL` está EXPRESSAMENTE FORA deste ramo.** Esta cláusula **NÃO** trata `PARCIAL` como
rótulo desconhecido. `PARCIAL` continua sob **`C-A1-ST4`**, **`SP4`**, **`PM1`–`PM12`**, o
**regime exclusivo de `status-fragmento`** e a **C14**, sem semântica nova. Na futura
composição total: os fragmentos sob `PARCIAL` são resolvidos **exclusivamente** pelas
**declarações explícitas válidas de `status-fragmento`**; **não** recebem propagação
automática; e, se houver **violação do contrato já materializado da C14** — incluindo **valor
inválido**, **declaração órfã** ou **ausência da declaração obrigatória** —, as **falhas já
existentes da C14 continuam prevalecendo segundo a sua precedência própria**. **Nenhuma
semântica nova de `PARCIAL` é criada aqui.**

**Alternativas REJEITADAS para a futura composição total.**

**1. Omissão silenciosa — REJEITADA.** A composição **não pode** simplesmente deixar o
fragmento não resolvido **fora da saída** e **ainda assim declarar sucesso**.

**2. Representação explícita de ausência em retorno bem-sucedido — REJEITADA.** A composição
**não deve** introduzir `None`, **sentinela**, **quarto valor**, **status especial** ou
*tuple*/estrutura de "não resolvido" **coexistindo com sucesso total**, como substituto de
status pertencente a **`C-3`**. Esta rejeição **não impede** que **outras APIs futuras, com
OUTRO contrato**, representem estado não resolvido de outra forma: a decisão vale **para a
fronteira de composição TOTAL de status**.

**A taxonomia concreta da futura exceção NÃO é decidida aqui.** Este registro fixa **apenas**
**falha pública/observável da composição total + zero retorno parcial**. Ele **não** fixa —
e **não** autoriza que se leia dele — **nome de classe de exceção**, **mensagem**,
**categorias**, **localizadores**, **herança**, se uma **exceção existente será propagada** ou
uma **nova será criada**, nem a **precedência exata** entre falhas de composição **ainda não
desenhadas**. Tudo isso pertence a **planejamento técnico próprio, posterior e ainda não
emitido**.

**Relação com `C-A1-ST8`.** **`C-A1-ST8` continua literal: status de TODOS os fragmentos
resolvidos.** **Esta arbitragem NÃO satisfaz `ST8`.** Ela garante **somente** que uma futura
composição total **não declare sucesso enquanto houver fragmento não resolvido pelo ramo
desconhecido de `SP5`**. A satisfação de `ST8` continuará **exigindo execução e auditoria
próprias** sobre os insumos canônicos pertinentes.

**A distribuição de rótulos do corpus é evidência, não fundamento normativo.** A regra acima
**permanece válida** ainda que um **futuro corpus aprovado** venha a conter outro rótulo `G2`
válido.

**Limites deste registro.** **`SP1`–`SP7`** permanecem **literais** e **`SP8` não existe**;
`G2`/`GR1`–`GR7`, `PM1`–`PM12`, o **regime exclusivo de `status-fragmento`**, `C-3`,
`C-A1-ST`, `C-A1-P2` e `C-A5` permanecem **literais**. A **autoridade de status** permanece
em `knowledge/respostas-aprovadas.md` enquanto **`C-A1-ST6`–`C-A1-ST10`** não estiverem
satisfeitas (**`C-11`**). **ARBITRAR O COMPORTAMENTO DA FUTURA COMPOSIÇÃO TOTAL NÃO É
IMPLEMENTAR COMPOSIÇÃO, NÃO É RESOLVER O STATUS QUE `SP5` MANTÉM NÃO RESOLVIDO, NÃO É
SATISFAZER `ST8`, NÃO É MIGRAR AUTORIDADE E NÃO É MATERIALIZAR `C`.**

##### C-A1-M — Prioridade de modelagem, prosa e auditoria de consumidores

| # | Regra |
|---|---|
| C-A1-M1 | **Ordem normativa de modelagem**: **1.** atomizar o dado; **2.** `ASSERTIVA` sobre fato atômico; **3.** `RENDERIZADO`; **4.** somente então, decisão humana de conteúdo. |
| C-A1-M2 | **Não alterar redação apenas para facilitar implementação.** |
| C-A1-M3 | Campos **narrativos** não podem se tornar **segunda fonte factual paralela** ao campo atômico. Havendo atomização futura: **(A)** a representação narrativa é **substituída**; **ou (B)** ela permanece **explicitamente NÃO AUTORITATIVA e NÃO CONSUMÍVEL** por *bindings* ou `ASSERTIVA`. **Nunca** manter duas fontes autoritativas do mesmo fato apenas para facilitar *template*. |
| C-A1-M4 | Antes de **qualquer** alteração física de estrutura em `knowledge/casa77.yaml`, é **obrigatória** uma **auditoria read-only de consumidores em todo o repositório**. Verificar apenas a estrutura exigida pelo carregador **não basta**. |
| C-A1-M5 | C-A1 **apenas registra alvos normativos**. **Nenhum alvo é executado** por esta entrega. |

##### C-A1-MD — Alvos futuros de modelo

**São alvos, não alterações autorizadas.** Nenhum valor concreto é escolhido aqui, e **todos**
estão sujeitos a **C-A1-M4**.

| Alvo | Finalidade | G | `Rxx` | Substitui / adiciona | Condição humana |
|---|---|---|---|---|---|
| **MD-1** | **forma de tratamento do responsável** | G1 | R03, R04, R05, R06, R07, R20, R21 | **adiciona** fato operacional próprio | **A1** |
| **MD-2** | **atomização / decomposição estrutural** de endereço e localidade | G1, G10 | R01, R13 | **substitui** a representação factual composta **ou** a torna explicitamente **não autoritativa e não consumível**. **Não** manter duas fontes autoritativas | — |
| **MD-3** | **REMOVIDO / NÃO ARBITRADO** | — | — | — | — |
| **MD-4** | atomização dos **vencimentos de pagamento** hoje representados como frases | G2, G3 | R19 | **substitui** a representação factual narrativa. **Não** resolve sozinho o numeral por extenso de `R19` | — |
| **MD-5** | atomização de **montagem / desmontagem** hoje em frases | G2, G3 | R11 `F2` | **substitui** a representação factual narrativa. **Não** resolve sozinho o numeral por extenso de `R11` `F2` | — |
| **MD-6** | política / fato atômico explícito sobre **existência ou inexistência de mínimo de convidados** | G7 | R10 | **substitui** a representação ambígua *campo nulo + observação*. **C-7 continua preservada** | **A2** |
| **MD-7′** | fato atômico geral sobre o **perfil intimista do espaço** | G2 | R16, R17 | **substitui** a representação textual como fonte autoritativa **ou** torna a prosa **não autoritativa e não consumível**. Consumido por `ASSERTIVA`; **nenhum formatador de caixa ou plural** | — |
| **MD-8** | atomização da **responsabilidade / política de toldos** | G2 | R22 | **substitui** a prosa como fonte factual | — |
| **MD-9** | atomização da **política / fato de estacionamento** | G2 | R14 | **substitui** a prosa como fonte factual | — |
| **MD-10** | atomização das afirmações necessárias de **som, iluminação cênica e gerador**, com a respectiva responsabilidade | G2 | R25 `F2` | **atomiza** o que falta, **sem duplicar** as representações autoritativas já existentes | — |
| **MD-11** | atomização da **composição da suíte da noiva** | G4 | R28 | **substitui** a pseudo-lista como fonte factual | — |
| **MD-12** | fato atômico / **fonte única** para a **recomendação de fornecedores** | G2 | R24 | **consolida**; **não** transformar uma pseudo-lista em segunda fonte | — |
| **MD-13** | atomização do **motivo de fogos** e da **regra de decoração** | G2 | R23 `F2` | **substitui** as prosas como fontes factuais | — |
| **MD-14** | **papéis de visita** — fatos de papel e relação no lugar de cópias de nome em `processo_comercial.visitas.*` | G1 | R06 | **substitui** as cópias de nome, evitando depender de igualdade entre *strings* de pessoas. **Não** é alvo de quantidade de equipe | — |
| **MD-15′** | **política operacional atômica** sobre a capacidade do bot de **confirmar disponibilidade** | G8 | R05 | **adiciona**; **não** altera `integracoes_planejadas.*.status` | **A4** |
| **MD-16** | **REMOVIDO / NÃO NECESSÁRIO PARA C** | — | — | — | — |
| **MD-17** | **retenção integral** em cancelamento | G6, G8 | R20 | **substitui** a representação numérica usada para expressar totalidade por **fato atômico booleano equivalente**; a representação narrativa **deixa de ser fonte de *binding*** | **A3** |
| **MD-18** | **identificador estrutural estável** para item de coleção **selecionado fora de iteração** | G5 | R19, R20 | **adiciona**; **preserva a lista**; **não** altera fato comercial. No corpus atual, necessário à futura **seleção da opção de pagamento**. **Nenhum valor concreto** é escolhido por C-A1 | — |

##### C-A1-G — Matriz G1–G14

`G1`–`G14` são as famílias residuais levantadas pela auditoria read-only. **Destino**,
**mecanismo**, `Rxx` atingidos e **resultado projetado**:

| G | Destino | Mecanismo | `Rxx` | Resultado projetado |
|---|---|---|---|---|
| G1 | alvos de modelo + fato humano | **MD-1** + **MD-14** (papel de visita, `R06`) + **A1** | R03, R04, R05, R06, R07, R20, R21 | representável |
| G2 | alvos de modelo sobre as **prosas** | **MD-4**, **MD-5**, **MD-8**, **MD-9**, **MD-10**, **MD-12**, **MD-13** | R11, R14, R19, R22, R23, R24, R25 | representável, com resíduo de redação em **B1**, **B4**, **B5**, **B6** |
| G3 | alvos como **pré-requisito** + conteúdo | **MD-4**, **MD-5** como pré-requisitos de atomização + **B1**, **B2**, **B4**, **B6** | R11, R12, R19, R25 | o **numeral por extenso continua sem formatador** (C-A1-R6): resíduo de **conteúdo** |
| G4 | convenção + alvo de modelo + conteúdo | **C-A1-L** + **MD-11** (`R28`) + **B2**, **B3**, **B5**, **B6** | R12, R18, R23, R25, R28 | parcialmente representável; resíduo de conteúdo |
| G5 | **regra normativa** + designação autoritativa | **C-15a** + designações explícitas (abaixo) + **MD-18** quando a seleção específica de coleção for necessária | R09, R11, R12, R19 | representável |
| G6 | regra normativa + alvo + fato humano | **C-15a** + **MD-17** + **A3** | R20 | condicionado a C-A2 |
| G7 | alvo de modelo + fato humano | **MD-6** + **A2** | R10 | condicionado a C-A2 |
| G8 | alvos + fatos humanos | `R05`: **MD-15′** + **A4** · `R20`: **MD-17** + **A3** | R05, R20 | condicionado a C-A2 |
| G9 | **RESOLVIDO por C-A1** | **C-A1-F3** | R11 | representável |
| G10 | alvo de modelo | **MD-2** | R01 | representável |
| G11 | **RESOLVIDO por C-A1** | **C-A1-ST4**; a **composição do fragmento** usa **MD-11** | R28 | mapeamento explícito por fragmento |
| G12 | **RESOLVIDO por C-A1** | **C-A1-B2** | R09 | nota fica fora da bijeção |
| G13 | **RESOLVIDO por C-A1** | **C-A1-ST5** | R13, R28 | nota não cria fragmento nem status |
| G14 | **peculiaridade estrutural NÃO BLOQUEADORA** | **C-4b** aceita o caminho explícito existente; **sem MD-16** e **sem realocação** | R25 | o campo **não é realocado** por esta entrega |

**G5 — designações autoritativas.** A designação de fonte é **regra normativa ligada a
C-15a**, **não** um alvo `MD` independente:

| # | Caso | Designação |
|---|---|---|
| C-A1-G5a | `R09` — duração do pacote | fonte é a do **próprio pacote** |
| C-A1-G5b | `R11` — duração genérica do evento | fonte é a **genérica de horários** |
| C-A1-G5c | quantidade de equipe | fonte é a **numérica estruturada de equipe**; a ocorrência **narrativa/lista deixa de ser fonte factual** (C-A1-M3) |
| C-A1-G5d | seleção específica da **opção de pagamento** | **MD-18** |

**R13 / CEP** é ocorrência da família de **recorte de string e localidade**, resolvida pelo
alvo **MD-2**. **R16 / R17** são o **residual de cobertura** da auditoria, resolvido pelo
alvo **MD-7′**.

##### C-A1-I — Status de integração × capacidade do bot

| # | Regra |
|---|---|
| C-A1-I1 | `integracoes_planejadas.*.status` representa o **status da integração**. Ele **mantém sua semântica atual** e **não é alterado**. |
| C-A1-I2 | A **capacidade operacional** — se o bot pode ou não confirmar disponibilidade — é **outro fato operacional**, e **não existe fonte autoritativa atual suficiente** para essa política específica. |
| C-A1-I3 | **MD-15′** é o alvo dessa política atômica separada, e permanece **condicionado a confirmação humana em C-A2** (**A4**). |

As duas questões técnicas antes abertas — **convenção do formato `lista`** e **seleção em
coleção** — estão **ARBITRADAS** por `C-A1` e **não** são pendências.

##### C-A1-P — Casos nomeados

| # | Caso | Registro |
|---|---|---|
| C-A1-P1 | **R09** | a **nota interna** de R09 **não integra a bijeção**, **não recebe *binding***, **não recebe `ASSERTIVA`** e **não bloqueia C**. O fato comercial que existe **somente** nessa nota permanece **NÃO EMITÍVEL** pelo bot. Criar fragmento emitível futuro exige **aprovação específica de conteúdo** — **não decidida em C-A1** |
| C-A1-P2 | **R28** | `PARCIAL` é **descrição agregada do Markdown**, **não** é quarto status de C-3 e **não** é traduzido automaticamente. O item de valor pendente é **nota interna**: não é fragmento, e o `null` daquela nota **não é *binding* do fragmento emitível** — portanto **não bloqueia automaticamente** o fragmento. O **C-8** existente no fragmento atual é **futuramente resolvível** pela atomização da composição da suíte (**MD-11**, **nunca MD-17**); a redação pode permanecer **estática** e ser provada por `ASSERTIVA` sobre fatos atômicos. **S2-D8 não é antecipada** |
| C-A1-P4 | **R20** | **(A)** o **percentual da entrada** liga-se, por **C-15a**, ao **campo correto de pagamento** — com **seleção estrutural estável** (**MD-18**) quando a seleção de item for necessária —, e **nunca** ao campo de retenção, cujo vínculo produziria **afirmação falsa**. **(B)** a **totalidade da retenção** depende de **MD-17** + **A3**: após a confirmação factual e a futura aplicação do alvo, `ASSERTIVA` `EH_VERDADEIRO` prova o **fato atômico**. **Sem comparação com literal**, **sem predicado novo** e **sem duplicar percentual e booleano como fontes autoritativas concorrentes** do mesmo conceito (C-A1-R2, C-A1-M3). Por isso **R20 não é pendência de redação** |
| C-A1-P5 | **R10** | **G7 não se resolve só com A2.** **A2** confirma o **fato humano** — existência ou inexistência de mínimo —; **MD-6** define a **futura representação atômica** que substitui a ambiguidade *campo nulo + observação*. **Sem MD-6, `R10` não compõe as contagens projetadas como materializável.** **C-7 continua preservada** |
| C-A1-P3 | **R01 / R15** | `AGUARDA_APROVACAO` é **status válido**: a aprovação do texto **não é pré-requisito** para C possuir representação estrutural. **R15** já pode ser estruturalmente representado com `AGUARDA_APROVACAO`; **R01** mantém `AGUARDA_APROVACAO` e depende apenas da futura **resolução estrutural** da sua fonte de localidade (**MD-2**) |

**Fatos e conteúdo humanos residuais.** Os fatos `A1`–`A4` e o conteúdo `B` são matéria de
**`C-A2`**, que prevalece sobre esta camada naquilo que declara fechar (**`C-P`**): os fatos
estão **fechados** em `C-A2-A` e a enumeração de conteúdo é a de `C-A2-B`. **Nem `C-A1` nem
`C-A2` são subetapa do roadmap.**

##### C-A1-X — O que C-A1 não altera

| # | Preservado sem alteração |
|---|---|
| C-A1-X1 | §4.1 com **14 componentes** |
| C-A1-X2 | §2 com **nove responsabilidades** |
| C-A1-X3 | §4.4 com **oito condições** |
| C-A1-X4 | `AssuntoComercial` com **54** valores |
| C-A1-X5 | `IntencaoConversacional` com **11** valores |
| C-A1-X6 | erros **`E-Nb-1`–`E-Nb-19`** |
| C-A1-X7 | cenários **`K-Nb-1`–`K-Nb-51`** |
| C-A1-X8 | `AcaoMaquina` com **20** códigos |
| C-A1-X9 | `CriterioIdentidade` com **12** códigos |

C-A1 **não cria** componente, responsabilidade, condição, estado, evento, transição, ação,
critério, enum, erro, cenário nem subetapa.

#### Micro-arbitragem C-A2 — fatos e conteúdo humanos residuais

`C-A2` **fecha** os fatos humanos `A1`–`A4`, **registra estruturalmente** o conteúdo humano
aprovado, **refina** o contrato de materialização para admitir **fato operacional de runtime
autoritativo** e **enumera** os efeitos futuros `FE-1`–`FE-14`. Ela **estende** a enumeração
de conteúdo para **`B1`–`B16`** e prevalece sobre as camadas anteriores naquilo que declara
fechar (**`C-P`**).

`C-A2` fecha os fatos e o conteúdo sob seu escopo; ela **não autoriza, por si**, aplicação ao
corpus, conversão de `knowledge/**`, renderizador, analisador ou alteração de dado comercial.
Ela **não** cria o índice, **não** aplica texto algum, **não** converte respostas em
*templates*, **não** muda status real, **não** escolhe provedor de calendário, **não** cria
condição de ciclo, evento, estado, motivo de `E09` nem subetapa, e **não** materializa **C**,
**R2** ou **S2-D8**.

##### C-A2-A — Fatos humanos `A1`–`A4`: FECHADOS

| # | Fato confirmado |
|---|---|
| A1 | **Tratamento emitido NÃO NOMINAL.** Literal aprovado: **"responsável comercial"**. **Nenhum nome próprio é emitido ao interessado.** Referência **puramente interna**, que **não seja fonte de emissão**, pode permanecer nominal. |
| A2 | **Não existe quantidade mínima de convidados.** |
| A3 | **Entrada = primeira parcela**; **retenção integral da entrada** — equivalente à **totalidade da primeira parcela** —; **sem devolução parcial**. O bot **pode informar a regra** e, **depois**, **deve fazer handoff** ao responsável comercial. |
| A4 | O bot **pode confirmar DISPONIBILIDADE** **somente** mediante **decisão determinística** baseada em **consulta autoritativa válida de calendário**. |

**`A4` NÃO autoriza**, em nenhuma hipótese:

| # | Não autorizado |
|---|---|
| C-A2-A4a | reserva |
| C-A2-A4b | *hold* |
| C-A2-A4c | visita |
| C-A2-A4d | contrato |
| C-A2-A4e | alteração definitiva de data |
| C-A2-A4f | pagamento |
| C-A2-A4g | exceção |

##### C-A2-B — Conteúdo humano aprovado: registro ESTRUTURAL

**`docs/07` NÃO é fonte paralela de redação comercial.** A tabela abaixo registra **somente
metadados documentais** — alvo, mecanismo previsto, alvos `MD` necessários, `FE` relacionada
e observação estrutural. Ela **não reproduz** o corpo literal dos textos aprovados e **não
contém** preço, percentual, prazo, quantidade ou condição comercial.

**A fonte do texto continua sendo `knowledge/respostas-aprovadas.md`.** Esta tabela registra
somente o **contrato estrutural**; estado de aplicação e progresso pertencem a
`docs/00-estado-atual.md`.

| B | Alvo | Conteúdo | Mecanismo previsto | `MD` | `FE` | Observação estrutural |
|---|---|---|---|---|---|---|
| B1 | `R11` `F2` | **texto já aprovado anteriormente — NÃO há nova redação** | **COMBINAÇÃO**: `RENDERIZADO` do fato numérico atomizado de antecedência de montagem; `ASSERTIVA` sobre o fato atômico do prazo de desmontagem; demais literais **estáticos** | **MD-5** | — | resíduo **exclusivamente de modelagem**. **B1 não integra o lote de novas unidades textuais aprovadas** |
| B2 | `R12` `F1` | **APROVADO HUMANAMENTE** | **COMBINAÇÃO**: `ASSERTIVA` de inclusão do uso das áreas contratadas; `ASSERTIVA` sobre mobiliário incluído; `RENDERIZADO` da quantidade de seguranças; `RENDERIZADO` da quantidade de governantas; `ASSERTIVA` para a função auxiliar de recepção; `ASSERTIVA` para limpeza/entrega inicial incluída; conectivos e redação não variável **estáticos** | **MD-19** | — | **MD-19** atomiza os três fatos ainda narrativos. As representações narrativas antigas **só perdem autoridade depois** dessa cobertura estrutural (**C-A1-M3**) |
| B3 | `R18` | **APROVADO HUMANAMENTE** | **`RENDERIZADO`**: formato `lista` sobre `eventos.datas_nao_aceitas`; **um prefixo geral estático**; **preservar todos os itens e a ordem** | — | — | **sem seleção posicional**, **sem prefixo por item**, **sem paráfrase** (**C-A1-L**, **C-A1-S1**) |
| B4 | `R19` | **APROVADO HUMANAMENTE** | **COMBINAÇÃO**: `ASSERTIVA` de modalidade integral disponível; `RENDERIZADO` da cardinalidade da opção parcelada; `RENDERIZADO` do percentual da primeira parcela; `RENDERIZADO` do percentual da segunda parcela; `ASSERTIVA` de vencimento da primeira parcela na assinatura; `RENDERIZADO` do inteiro de dias antes do evento para o segundo vencimento; `ASSERTIVA` `EH_FALSO` sobre caução | **MD-4**, **MD-18**, **MD-20** | — | os **dois percentuais possuem *bindings* separados**; **nenhuma igualdade caminho-a-caminho** (**C-A1-R3**); **MD-18** seleciona as opções por **identificador estrutural estável**; **MD-20 é MÍNIMO** e prova **somente** a disponibilidade explícita da modalidade integral necessária ao fragmento. **Não criar booleanos redundantes para todas as modalidades apenas por simetria** |
| B5 | `R23` `F1` | **APROVADO HUMANAMENTE** | **COMBINAÇÃO**: `RENDERIZADO` formato `lista` sobre `restricoes.proibido`; `ASSERTIVA` sobre o fato atômico do motivo da proibição de fogos; redação explicativa aprovada **estática** | **MD-13** | — | a nova redação **não deve depender de renderização direta** da narrativa `restricoes.fogos_motivo`. **MD-13 permanece relevante** para `R23` |
| B6 | `R25` `F1` | **APROVADO HUMANAMENTE** | **COMBINAÇÃO**: `ASSERTIVA` sobre `estrutura.cozinha.disponivel`; para **cada item** da coleção de equipamentos — selecionar por **identificador estrutural estável, nunca por posição**, `RENDERIZADO` do campo `item` e `RENDERIZADO` do campo `quantidade`; `RENDERIZADO` formato `lista` sobre `estrutura.som.rede_eletrica`; conectivos, pontuação e convenção visual de quantidade **estáticos** | **MD-18** | — | **MD-18 é GENERALIZADO**. **Preservar a coleção de equipamentos como mapeamentos** com `quantidade`/`item`/`especificacao` — **não achatar para *strings***. **Nenhuma especificação adicional é emitida** |
| B7 | `R02` | **APROVADO HUMANAMENTE** | **ESTÁTICO** | nenhum — **MD-1** é **SUPERADO / NÃO NECESSÁRIO PARA C** | **FE-8**, **FE-12** | tratamento emitido aprovado: **"responsável comercial"**. **Nenhum nome próprio é emitido ao lead** (**A1**) |
| B8 | `R03` | **APROVADO HUMANAMENTE** | **ESTÁTICO** | — | **FE-1**, **FE-9** | é a **resposta padrão de lacuna**. As **duplicatas especializadas** devem **permanecer sincronizadas** |
| B9 | `R04` | **APROVADO HUMANAMENTE** | **COMBINAÇÃO**: `ASSERTIVA` `EH_FALSO` sobre autorização de desconto pelo bot; `ASSERTIVA` `EH_FALSO` sobre desconto à vista; tratamento e encaminhamento **estáticos** | — | **FE-2** | **FE-2** elimina a resposta textual paralela de "insistência" em `docs/03` como **fonte emitível própria**. `docs/03` deve **remeter** ao comportamento aprovado de `R04`/handoff, e **não** manter um segundo texto emitível não catalogado |
| B10 | `R05` `F1` | **APROVADO HUMANAMENTE** — papel: **FALLBACK de disponibilidade** | **ESTÁTICO** | nenhum **no fragmento** — **MD-15′** é **política externa de autorização** e **NÃO é *binding* nem `ASSERTIVA` de `F1`** | **FE-3**, **FE-7**, **FE-10**, **FE-13**, **FE-14** | `F1` é usado quando **não existe confirmação segura**: ausência de fonte, falha de consulta ou resultado ambíguo. **A seleção do fallback pertence ao motor determinístico, fora de C** (**C-12**) |
| B11 | `R06` | **APROVADO HUMANAMENTE** | **COMBINAÇÃO**: `RENDERIZADO` da duração mínima; `RENDERIZADO` da duração máxima; `ASSERTIVA` sobre os fatos estruturais de papel — **quem realiza** e **quem confirma** a visita; `ASSERTIVA` `EH_FALSO` sobre `bot_pode_confirmar`; tratamento **"responsável comercial"** estático | **MD-14** | **FE-5** | **MD-14 permanece OBRIGATÓRIO.** **`A1` resolve apenas COMO o papel é chamado**; ela **não substitui** a prova estrutural de quem realiza e de quem confirma a visita |
| B12 | `R07` | **APROVADO HUMANAMENTE** | **COMBINAÇÃO**: `ASSERTIVA` `EH_FALSO` sobre `bot_pode_fechar`; `ASSERTIVA` `EH_VERDADEIRO` sobre atendimento humano obrigatório; tratamento do responsável **estático** | — | **FE-8** | **não altera poder do bot**: o **contrato continua humano** |
| B13 | `R08` | **APROVADO HUMANAMENTE** | **ESTÁTICO** | — | **FE-4**, **FE-6**, **FE-9** | **mensagem padrão de handoff**. **Sincronização especializada obrigatória** |
| B14 | `R20` | **APROVADO HUMANAMENTE** | **COMBINAÇÃO**: `ASSERTIVA` `EH_VERDADEIRO` sobre o fato atômico de **retenção integral da entrada**; handoff/tratamento **estáticos** | **MD-17** | — | **não mencionar percentual do contrato**. **MD-18 NÃO é necessário para `R20`** na redação aprovada. **`A3` está satisfeita** |
| B15 | `R21` | **APROVADO HUMANAMENTE** | **COMBINAÇÃO**: `RENDERIZADO` da antecedência mínima; `ASSERTIVA` `EH_VERDADEIRO` sobre dependência de disponibilidade; `ASSERTIVA` `EH_VERDADEIRO` sobre atendimento humano obrigatório; tratamento do responsável **estático** | — | — | **`A4` autoriza confirmar DISPONIBILIDADE**; ela **não autoriza ALTERAÇÃO definitiva de data**. O **handoff de alteração permanece obrigatório** |
| B16-A | `R05` `F2` | **APROVADO HUMANAMENTE** | `ASSERTIVA` de **origem `RUNTIME_AUTORITATIVO`** (**C-A2-RT**, **C-A2-V**) | — | **FE-3**, **FE-7**, **FE-10**, **FE-13**, **FE-14** | **consulta válida + disponível** |
| B16-B | `R05` `F3` | **APROVADO HUMANAMENTE** | `ASSERTIVA` de **origem `RUNTIME_AUTORITATIVO`** (**C-A2-RT**, **C-A2-V**) | — | **FE-3**, **FE-7**, **FE-10**, **FE-13**, **FE-14** | **consulta válida + indisponível** |

##### C-A2-B16 — Decisão `B16`: `R05` permanece um único `Rxx`

| # | Fragmento | Papel |
|---|---|---|
| C-A2-B16a | `R05` `F1` | **fallback** |
| C-A2-B16b | `R05` `F2` | **consulta válida + disponível** |
| C-A2-B16c | `R05` `F3` | **consulta válida + indisponível** |

**`R05` permanece um único `Rxx`.** Justificativa:

| # | Razão |
|---|---|
| C-A2-B16d | **mesma intenção / mesmo tema** |
| C-A2-B16e | **menor mudança no corpus** |
| C-A2-B16f | a **bijeção é por fragmento**, **não** por `Rxx` (**C-A1-B1**) |
| C-A2-B16g | **múltiplos fragmentos por `Rxx` já são suportados** (**C-2c**) |
| C-A2-B16h | **preserva os 30 `Rxx`** |
| C-A2-B16i | **minimalismo do MVP** |

**Não se afirma** — e **não pode ser derivado** desta decisão — que "um `Rxx` diferente
obrigatoriamente produziria grupo **R2** diferente ou `E09` espúrio". **R2 continua
arbitragem própria** (§4.4.1) e **seus grupos não devem ser derivados automaticamente da
identidade do `Rxx`**.

##### C-A2-RT — Origem explícita do referente

**Refinamento da leitura de C (`C-P`).** O modelo conceitual de **C-2** é **preservado**; o
que segue fixa **como o referente de um *binding* é declarado** quando o fato deixa de ser
estático e passa a ser **fato operacional de runtime autoritativo**.

| # | Regra |
|---|---|
| C-A2-RT1 | Todo *binding* declara o campo **`origem`**. |
| C-A2-RT2 | Vocabulário **fechado**: **`YAML`** e **`RUNTIME_AUTORITATIVO`**. **Nenhum terceiro valor.** |
| C-A2-RT3 | **`origem` é OBRIGATÓRIO.** **NÃO existe valor padrão.** |
| C-A2-RT4 | **Ausência de `origem` NÃO é interpretada como `YAML`.** Ausência = **índice estruturalmente inválido** → **FAIL-CLOSED** (**P5**). |
| C-A2-RT5 | Para `origem = YAML`: **`caminho_yaml` OBRIGATÓRIO**; **`fato_runtime` PROIBIDO**. |
| C-A2-RT6 | Para `origem = RUNTIME_AUTORITATIVO`: **`fato_runtime` OBRIGATÓRIO**; **`caminho_yaml` PROIBIDO**. |
| C-A2-RT7 | **Exatamente um referente** por *binding* — nem zero, nem dois. |

##### C-A2-V — Vocabulário runtime

Vocabulário **fechado inicial** de `fato_runtime`:

| # | Fato | Tipo |
|---|---|---|
| C-A2-V1 | `consulta_calendario_valida` | booleano |
| C-A2-V2 | `data_disponivel` | booleano |

Restrições da origem `RUNTIME_AUTORITATIVO`:

| # | Regra |
|---|---|
| C-A2-V3 | **somente `ASSERTIVA`** |
| C-A2-V4 | **`RENDERIZADO` PROIBIDO** sobre fato runtime |
| C-A2-V5 | **somente `EH_VERDADEIRO` / `EH_FALSO`** — **nenhum predicado novo** (**C-5g**, **C-5h**, **C-A1-R**) |
| C-A2-V6 | **nenhum valor, *snapshot*, *hash* ou versionamento de disponibilidade** é armazenado no índice (**C-1k**–**C-1m**, **C-15e**) |
| C-A2-V7 | **nenhum provedor de calendário é escolhido** |

*Bindings* previstos:

| Fragmento | Condição |
|---|---|
| `R05` `F2` | `consulta_calendario_valida` **verdadeiro** **E** `data_disponivel` **verdadeiro** |
| `R05` `F3` | `consulta_calendario_valida` **verdadeiro** **E** `data_disponivel` **falso** |
| `R05` `F1` | **sem *binding* runtime** |

##### C-A2-ESC — Escopo do fato runtime

| # | Regra |
|---|---|
| C-A2-ESC1 | O fato runtime pertence ao **ciclo corrente**. |
| C-A2-ESC2 | Pertence à **consulta corrente**. |
| C-A2-ESC3 | Pertence à **data efetivamente consultada**. |
| C-A2-ESC4 | **Não reutilizar** o resultado para **outra data**. |
| C-A2-ESC5 | **Não reutilizar** em **ciclo posterior**. |
| C-A2-ESC6 | **Ausência = FALHA** (**C-A2-RT4**). |
| C-A2-ESC7 | Durante **validação e emissão**, os fatos observados são **imutáveis no mesmo instantâneo lógico**. |

| # | Fronteira |
|---|---|
| C-A2-ESC8 | **MD-15′ é POLÍTICA.** O motor **verifica MD-15′ antes da candidatura** de `R05` `F2`/`F3`. |
| C-A2-ESC9 | **MD-15′ NÃO é `ASSERTIVA`-gatilho** — coerente com **C-5i**–**C-5q** e **C-5.1**. |
| C-A2-ESC10 | **C valida consistência.** **C não decide candidatura** e **não decide disponibilidade** — **C-12 permanece literal e inalterada**. |
| C-A2-ESC11 | **Sem consulta válida**: `R05` `F1` **+ handoff**. |
| C-A2-ESC12 | **Nenhum terceiro motivo de `E09`** é criado — permanecem **exatamente dois** (§4.4.1, **D8-E**). |

##### C-A2-NR — Refinamentos normativos

**Refinamentos da LEITURA** de **P2**, **P8**, **F1**, **F3**, **C-5b** e da **definição
geral de `ASSERTIVA`**. **Nenhum desses textos é reescrito**: onde `C-A2` refina, ela
prevalece (**`C-P`**).

| # | Regra |
|---|---|
| C-A2-NR1 | Fato comercial/operacional **ESTÁTICO** cuja fonte é a base **continua em YAML**, sem exceção. |
| C-A2-NR2 | Fato operacional de **RUNTIME**, produzido por **integração autoritativa**, **pode** ter `origem = RUNTIME_AUTORITATIVO`. |
| C-A2-NR3 | **P2** — a decisão comercial continua **determinística e rastreável**. O refinamento apenas admite que a rastreabilidade de um **fato operacional de runtime** aponte para o `fato_runtime` declarado; **nunca** para inferência do LLM. |
| C-A2-NR4 | **P8 / F1** — **o YAML continua a fonte autoritativa de todo fato comercial**. O **runtime não concorre com o YAML** e **não sobrescreve nenhum campo dele**. |
| C-A2-NR5 | **F3** — a validação contra o **YAML carregado** permanece integral para todo fato comercial; o fato runtime é avaliado **contra a consulta autoritativa do ciclo corrente**, nos limites de **C-A2-ESC**. |
| C-A2-NR6 | **C-5b** — "caminho YAML explícito" passa a ser lido como **"referente explícito"**, resolvido por **C-A2-RT5** ou **C-A2-RT6**. **Explicitude e obrigatoriedade não são atenuadas.** |
| C-A2-NR7 | **`ASSERTIVA`** continua **consistency-only**: **não cria regra comercial, não altera dado, não produz ação, evento, handoff, `E18` nem condição de ciclo, e não decide `resposta_aprovada_disponivel` ou `pendencia_impeditiva`** (**C-5i**–**C-5q**). |

**Preservado explicitamente:**

| # | Preservação |
|---|---|
| C-A2-NR8 | `eventos.datas_nao_aceitas` **continua tendo precedência** |
| C-A2-NR9 | **F4** e **F4-B** permanecem **literais e inalteradas** (§2.2) |
| C-A2-NR10 | **C-12** permanece **literal e inalterada** (§2.3) |
| C-A2-NR11 | **O LLM nunca decide** (**P3**, **F5**) |

##### C-A2-MD — Tabela `MD` final

| Alvo | Estado após C-A2 |
|---|---|
| **MD-1** | **SUPERADO / NÃO NECESSÁRIO PARA C** |
| **MD-2** | **mantido** |
| **MD-3** | **REMOVIDO** |
| **MD-4** | **mantido** |
| **MD-5** | **mantido** |
| **MD-6** | **mantido**; **`A2` satisfeita** |
| **MD-7′**–**MD-13** | **mantidos** |
| **MD-14** | **mantido e NECESSÁRIO para `R06`** |
| **MD-15′** | **mantido**; **`A4` satisfeita** |
| **MD-16** | **REMOVIDO** |
| **MD-17** | **mantido**; **`A3` satisfeita** |
| **MD-18** | **mantido e GENERALIZADO** para **identificador estrutural estável de item de coleção selecionado fora de iteração**. **Impacto atual**: **`R19`** / opções de pagamento e **`R25`** / equipamentos da cozinha |
| **MD-19** | **NOVO.** Finalidade: **atomizar, para `R12` `F1`** — **(1)** uso das áreas contratadas incluído; **(2)** governanta auxilia na recepção; **(3)** limpeza para entrega inicial incluída. **Não duplicar fontes narrativas autoritativas** (**C-A1-M3**) |
| **MD-20** | **NOVO, porém MÍNIMO.** Finalidade **EXATA**: **fato atômico booleano** que permita **provar que a modalidade de PAGAMENTO INTEGRAL está disponível**. **NÃO adicionar automaticamente booleanos de "disponibilidade" para todas as modalidades apenas por simetria** — a **opção parcelada continua provada pelos seus próprios *bindings* estruturados** |

**Todos os alvos `MD` estão sujeitos a `C-A1-M4`** — auditoria read-only de consumidores em
todo o repositório — como **pré-condição normativa** de qualquer alteração física de
`knowledge/casa77.yaml`. A tabela **define os alvos e os seus contratos**; ela **não executa**
alteração física alguma (**C-A1-M5**). O **estado de execução dos alvos** pertence a
`docs/00-estado-atual.md`.

##### C-A2-FE — Invariantes de reconciliação `FE-1`–`FE-14`

Cada `FE` é um **requisito de consistência** entre a fonte relacionada e o conteúdo humano
aprovado. Elas são **efeitos de reconciliação comportamental**, e o **estado de aplicação de
cada uma pertence a `docs/00-estado-atual.md`**.

| `FE` | Fonte relacionada | Invariante |
|---|---|---|
| **FE-1** | `docs/03-regras-de-conversa.md` | **sincronizar** o bloco literal de comportamento diante de lacuna com **`R03`/`B8`** aprovado, **removendo emissão nominal** |
| **FE-2** | `docs/03-regras-de-conversa.md` | **eliminar** o bloco textual emitível paralelo de "comportamento diante de insistência" como **resposta autônoma não catalogada**. O documento deve **instruir o fluxo** a usar **`R04`/`B9` + handoff**, **sem** manter segunda redação emitível fora de `knowledge/respostas-aprovadas.md` |
| **FE-3** | `docs/03-regras-de-conversa.md` | **substituir** a proibição **incondicional** de confirmar disponibilidade/data por **regra condicional**: com **consulta autoritativa válida** e **decisão determinística**, a disponibilidade **pode ser comunicada**; **sem confirmação segura**, **fallback + handoff**. **Preservar** a proibição de **reserva, *hold*, visita, contrato** e demais atos humanos |
| **FE-4** | `docs/04-handoff-humano.md` | **sincronizar** "Mensagem ao interessado" com **`R08`/`B13`**, usando o tratamento **não nominal "responsável comercial"** |
| **FE-5** | `docs/04-handoff-humano.md` | **reconciliar** a seção **Visitas** para **não autorizar emissão nominal**. **Preservar**: visita realizada pelo **papel estrutural definido**; **confirmação de horário humana**; **o bot não confirma visita**. Usar **"responsável comercial"** |
| **FE-6** | `docs/04-handoff-humano.md` | **reconciliar** "Regras após o handoff" para **remover instrução de reforço nominal** e usar **"responsável comercial"** quando a referência for **emitida ao lead**. Referências **puramente internas** podem permanecer nominais **se não forem fonte de emissão** |
| **FE-7** | `docs/04-handoff-humano.md` | **reconciliar** o gatilho obrigatório que hoje **agrega** "confirmação de data, visita ou reserva". **Separar**: **DISPONIBILIDADE DE DATA** — pode ser confirmada com **decisão determinística** sobre **consulta autoritativa válida**; sem confirmação segura → **handoff**. **VISITA** — continua **confirmação humana obrigatória**. **RESERVA** — continua **humana / proibida ao bot** |
| **FE-8** | `prompts/prompt-sistema-bot.md` | **reconciliar** **FUNÇÃO** e **REGRAS DE HANDOFF** para que referências **destinadas ao lead** usem **"responsável comercial"**, **sem emissão de nome próprio**. **Preservar** referências internas de identidade negativa quando **não** forem texto destinado ao lead |
| **FE-9** | `prompts/prompt-sistema-bot.md` | **sincronizar** os blocos literais **duplicados** de `R03` e `R08` com **`B8`** e **`B13`** aprovados. **Não manter variante nominal concorrente** |
| **FE-10** | `prompts/prompt-sistema-bot.md` | **reconciliar** **LIMITES DE ATUAÇÃO**, **REGRAS CONTRA INVENÇÃO** e **REGRAS DE HANDOFF** quanto à disponibilidade. Nova fronteira: o **LLM NÃO decide** disponibilidade; o resultado vem de **decisão determinística** sobre **consulta autoritativa**; com resultado válido, o bot **pode comunicar** disponibilidade; sem resultado válido, **fallback + handoff**; **reserva, *hold*, visita, contrato e alteração definitiva continuam proibidos ao bot** |
| **FE-11a** | `knowledge/respostas-aprovadas.md` | **instrução interna de `R17`**. Regra futura: **NÃO emitir literalmente `eventos.observacao_nao_aceitos`** enquanto a narrativa puder **expor identificação nominal / proveniência interna**. Enquanto **não houver representação estrutural segura do motivo**, usar **`R03` + handoff** para pedido específico desse motivo. **`FE-11a` NÃO altera o YAML** |
| **FE-11b** | `knowledge/casa77.yaml` | **base estruturada**: **reconciliar/atomizar** a narrativa para **eliminar o vetor nominal sem criar fonte factual paralela** (**C-A1-M3**). A alteração física exige **`C-A1-M4`** como **pré-condição normativa** |
| **FE-12** | `docs/02-fluxo-comercial.md` | **reconciliar §1 Abertura**: **preservar** que a **negociação final é humana**, **substituindo** identificação nominal emitida por **"responsável comercial"** |
| **FE-13** | `docs/02-fluxo-comercial.md` | **reconciliar §5 Verificação de disponibilidade**: passar de ramo **exclusivamente negativo** para **dois caminhos** — **(A)** consulta autoritativa válida + decisão determinística → comunicar **`R05` `F2`** ou **`R05` `F3`**; **(B)** ausência/falha/ambiguidade → **`R05` `F1` + handoff**. **Não escolher provedor de calendário** |
| **FE-14** | `docs/02-fluxo-comercial.md` | **reconciliar o diagrama textual**: substituir o caminho universal `disponibilidade (bloqueado) → R05` pela **bifurcação conceitual** — consulta válida → **`R05` `F2` / `R05` `F3`**; sem confirmação segura → **`R05` `F1` + handoff** |

##### C-A2-N — Gates de materialização

A materialização de `C` depende **cumulativamente** dos gates abaixo. O **estado de
cumprimento** de cada gate pertence a `docs/00-estado-atual.md`, confrontado com a `main`.

| # | Gate |
|---|---|
| C-A2-N9 | **aplicação do conteúdo** aprovado |
| C-A2-N10 | **`C-A1-M4`** — auditoria read-only de consumidores |
| C-A2-N11 | os **alvos `MD` necessários** |
| C-A2-N12 | **validação `C-8` / `C-15` / `C-A1`** |

##### C-A2-X — O que C-A2 não altera

| # | Preservado sem alteração |
|---|---|
| C-A2-X1 | §4.1 com **14 componentes** |
| C-A2-X2 | §2 com **nove responsabilidades** |
| C-A2-X3 | §4.4 com **oito condições** |
| C-A2-X4 | `AssuntoComercial` com **54** valores |
| C-A2-X5 | `IntencaoConversacional` com **11** valores |
| C-A2-X6 | `ProjecaoInterpretacao` com **sete** campos |
| C-A2-X7 | `CriterioIdentidade` com **12** códigos |
| C-A2-X8 | erros **`E-Nb-1`–`E-Nb-19`** |
| C-A2-X9 | cenários **`K-Nb-1`–`K-Nb-51`** |

C-A2 **não cria** componente, responsabilidade, estado, evento, transição, ação, critério,
enum, erro, cenário, condição de ciclo, motivo de `E09` nem subetapa.

#### Micro-arbitragem C-A3 — papel de `empresa.descricao` no contrato C

`C-A3` refina exclusivamente o papel de **`empresa.descricao`** dentro do contrato `C`,
segundo a precedência **`C-P`**. Ela **classifica normativamente um único caminho** do YAML e
**não faz mais nada**. **Nenhum byte de `knowledge/casa77.yaml` é alterado por ela.**

##### C-A3-E — Escopo fechado

| # | Regra |
|---|---|
| C-A3-E1 | O **único** caminho classificado por C-A3 é **`empresa.descricao`**. |
| C-A3-E2 | **`empresa.nome` NÃO é classificado** por C-A3. |
| C-A3-E3 | **`empresa.posicionamento` NÃO é classificado** por C-A3. |
| C-A3-E4 | **`empresa.diferenciais` NÃO é classificado** por C-A3. Ele permanece **INTACTO**, e **C-A3 não decide sua autoridade futura**. Em particular, a expressão **`"experiência intimista"` não é objeto de C-A3**. |
| C-A3-E5 | **Não há regra por prefixo `empresa.*`**, **nenhuma inferência automática por tipo de campo** e **nenhuma classe expansível automaticamente**. Qualquer outro caminho exige arbitragem própria. |
| C-A3-E6 | **O papel normativo de qualquer outro caminho do YAML permanece inalterado.** |

##### C-A3-D — Decisão central

**`empresa.descricao` é texto institucional.** Para os fins do **contrato C**:

| # | Regra |
|---|---|
| C-A3-D1 | **NÃO é fonte factual comercial ou operacional.** |
| C-A3-D2 | **NÃO pode ser referente de *binding*** do índice de C. |
| C-A3-D3 | **NÃO pode ser referente de `RENDERIZADO`.** |
| C-A3-D4 | **NÃO pode ser referente de `ASSERTIVA`.** |
| C-A3-D5 | Seu **conteúdo textual NÃO pode ser interpretado, decomposto, resumido nem inferido como fato** para C. **Nunca inferir vínculo por coincidência textual** (**C-15a**). |
| C-A3-D6 | Ela **permanece fisicamente em `knowledge/casa77.yaml` SEM QUALQUER alteração**. |
| C-A3-D7 | Essa permanência **satisfaz `C-A1-M3(B)`**: a representação narrativa fica **explicitamente NÃO AUTORITATIVA e NÃO CONSUMÍVEL** por *bindings* ou `ASSERTIVA`, **sem** se tornar segunda fonte factual paralela. |

O tratamento é **análogo** ao que **C-2m**–**C-2p** e **C-A1-B2** já fixam para notas e
instruções internas: **fora da bijeção**, **sem status**, **sem *binding***, **sem
`ASSERTIVA`**.

##### C-A3-P — Relação com P8 e F1

| # | Regra |
|---|---|
| C-A3-P1 | **P8 e F1 permanecem íntegros**: `knowledge/casa77.yaml` **continua a fonte autoritativa de todo fato comercial e operacional**. |
| C-A3-P2 | **C-A3 não abre exceção genérica ao YAML** e **não cria contradição normativa**. Ela apenas **classifica `empresa.descricao` como campo textual institucional**, e **não como campo factual para os fins de C**. |

##### C-A3-EM — Emissão

| # | Regra |
|---|---|
| C-A3-EM1 | C-A3 **NÃO declara** que `empresa.descricao` "nunca pode ser emitida pelo bot". Essa proposição seria **mais ampla que a necessidade atual**. |
| C-A3-EM2 | A decisão é **somente**: **não consumível por C** como fonte factual, *binding* ou `ASSERTIVA`. |
| C-A3-EM3 | C-A3 **não decide** eventual uso textual institucional **fora do contrato C**. |

##### C-A3-MD — Efeito sobre `MD-7′`

| # | Regra |
|---|---|
| C-A3-MD1 | **Antes de C-A3**, `empresa.descricao` representava **autoridade narrativa potencialmente paralela** ao fato de **`MD-7′`** — o fato atômico geral sobre o **perfil intimista do espaço**. |
| C-A3-MD2 | **Depois de C-A3**, o requisito **`C-A1-M3(B)`** fica **documentalmente satisfeito** para `empresa.descricao`. |
| C-A3-MD3 | Isso **remove exclusivamente o bloqueio normativo** identificado para a **futura** execução de `MD-7′`. **Nenhum outro bloqueio é removido.** |
| C-A3-MD4 | **C-A3 NÃO executa `MD-7′`**, **NÃO cria `eventos.perfil_intimista`**, **NÃO remove `eventos.perfil_ideal`**, **NÃO executa `MD-6`** e **NÃO executa `MD-14`**. |

##### C-A3-FE — Relação com `FE-11a` e `FE-11b`

| # | Regra |
|---|---|
| C-A3-FE1 | **`FE-11a` permanece intacta.** |
| C-A3-FE2 | A alteração física descrita por **`FE-11b`** exige **`C-A1-M4`** como **pré-condição normativa**. O estado de cumprimento do gate e de aplicação do efeito pertence a `docs/00-estado-atual.md`. |
| C-A3-FE3 | C-A3 **não absorve, não substitui, não antecipa e não altera** `FE-11a` ou `FE-11b`. |
| C-A3-FE4 | **`eventos.observacao_nao_aceitos` não é objeto de C-A3.** |

##### C-A3-X — O que C-A3 não cria

C-A3 **não cria**: status, enum, predicado, formato, *binding* físico, metadado YAML, *flag*
YAML, componente, responsabilidade, estado, evento, transição, condição, erro, cenário,
pendência operacional nem subetapa.

#### Micro-arbitragem C-A4 — critério de cumprimento de `C-A2-N12` e convenções de validação

`C-A4` define o **critério de cumprimento** de **`C-A2-N12`** e as **convenções de
validação**. Ela **não executa o gate** e **não materializa `C`**: **não cria o índice**, **não
cria *template* físico**, **não cria *binding* físico**, **não cria `ASSERTIVA` física**,
**não altera `knowledge/**`**, **não implementa código** e **não altera testes**, nem
materializa **R2** ou **S2-D8**. O **estado de cumprimento de `C-A2-N12`** pertence a
`docs/00-estado-atual.md`.

Ela fecha, para a **execução read-only** de `C-A2-N12`: o **critério de
cumprimento** do gate; o **vocabulário** dos resultados de validação; refinamentos
de **`inteiro_agrupado`** e da **fronteira de `simbolo_moeda`**; a **derivação
conceitual de *bindings*** onde `C-A2-B` não prescreve; o tratamento de **`R05` `F2`/`F3`**;
e a **proposição completa** como unidade de análise de `C-8`.

##### C-A4-G — Critério de cumprimento de `C-A2-N12`

| # | Regra |
|---|---|
| C-A4-G1 | **“auditoria executada completamente”** e **“`C-A2-N12` cumprida”** são **proposições distintas**. Uma **não implica automaticamente** a outra. |
| C-A4-G2 | **`C-A2-N12` = CUMPRIDA** somente quando, **CUMULATIVAMENTE**: **(A)** a validação **`C-8`** / **`C-15`** / **`C-A1`** cobriu **integralmente o universo aplicável**; **E (B)** **não resta bloqueio** que impeça que **cada um dos 37 fragmentos** do corpus **C** possua **representação estrutural** conforme o contrato **C**. |
| C-A4-G3 | auditoria completa **+** qualquer **FAIL-CLOSED impeditivo** = **EXECUTADA COMPLETAMENTE / NÃO CUMPRIDA**. |
| C-A4-G4 | auditoria completa **+** qualquer **NÃO DETERMINÁVEL residual** = **EXECUTADA COMPLETAMENTE / NÃO CUMPRIDA**. |
| C-A4-G5 | auditoria completa **+** **divergência de base** que impeça conformidade estrutural = **EXECUTADA COMPLETAMENTE / NÃO CUMPRIDA**. |
| C-A4-G6 | **`C-15d` permanece válida**: **FAIL-CLOSED continua sendo desfecho correto** da validação. **Porém** ele **não satisfaz** o gate **`C-A4-G2`** enquanto **impedir representação estrutural** do corpus. |
| C-A4-G7 | **C-A4 não declara `37/37` alcançado** e **não antecipa** resultado algum de `C-A2-N12`. |
| C-A4-G8 | **COBERTURA ESTRUTURAL ≠ EMISSIBILIDADE.** O status **`AGUARDA_APROVACAO`**, **por si só**, **não impede representação estrutural**. Isso **NÃO** significa aprovação de emissão e **NÃO** dispensa o fragmento de satisfazer **todas** as regras **`C-8`** / **`C-15`** / **`C-A1`** que incidirem sobre ele. **`C-3` e `C-A1-ST` permanecem vigentes.** **Nenhum quarto status é criado.** |

##### C-A4-VOC — Vocabulário da auditoria

Vocabulário **fechado** dos resultados de validação:

| # | Resultado |
|---|---|
| C-A4-VOC1 | `PASS` |
| C-A4-VOC2 | `FAIL-CLOSED` |
| C-A4-VOC3 | `DIVERGÊNCIA DE BASE` |
| C-A4-VOC4 | `NÃO DETERMINÁVEL` |
| C-A4-VOC5 | `N/A` |

| # | Regra |
|---|---|
| C-A4-VOC6 | **`PASS CONDICIONADO` NÃO EXISTE.** É **proibido** usá-lo como rótulo **ou como paráfrase**. |
| C-A4-VOC7 | **`N/A` só pode ser usado quando a regra realmente não incidir** sobre o par avaliado. |
| C-A4-VOC8 | **`N/A` nunca significa dispensa geral de validação.** |
| C-A4-VOC9 | **Exatamente um resultado** por par **fragmento × eixo/regra de validação** — nem zero, nem dois. |

##### C-A4-F1 — `inteiro_agrupado`: convenção fechada

**Refinamento de `C-6b` e `C-A1-F1` (`C-P`). Nenhum formato novo é criado.**

| # | Regra |
|---|---|
| C-A4-F1a | Representa **o MESMO inteiro**, em **decimal**. |
| C-A4-F1b | Agrupa **da direita para a esquerda**. |
| C-A4-F1c | Grupos de **três dígitos**. |
| C-A4-F1d | Separador visual de milhar: **`.`** |
| C-A4-F1e | **Sem casas decimais.** |
| C-A4-F1f | **Sem arredondamento.** |
| C-A4-F1g | **Sem cálculo.** |
| C-A4-F1h | **Sem alteração do valor.** |
| C-A4-F1i | **Nenhum zero é adicionado** para completar grupo. |
| C-A4-F1j | Eventual **sinal** do inteiro é **preservado**. |
| C-A4-F1k | O agrupamento aplica-se **somente aos dígitos**. |
| C-A4-F1l | Operação **puramente de apresentação**. |
| C-A4-F1m | **Sem *locale*.** |
| C-A4-F1n | **Sem biblioteca cujo resultado dependa do ambiente.** |
| C-A4-F1o | **Sem leitura implícita de campo adicional** (C-6). |

##### C-A4-F2 — `simbolo_moeda`: fronteira

| # | Regra |
|---|---|
| C-A4-F2a | **Nenhuma regra nova de espaçamento é criada.** **`C-6c` e `C-A1-F2` permanecem vigentes.** |
| C-A4-F2b | O formatador produz **somente o símbolo** correspondente ao **código monetário explicitamente recebido pelo *binding***. |
| C-A4-F2c | **Whitespace antes e depois pertence ao fragmento / *template* estático**, nunca ao formatador. |
| C-A4-F2d | A **tabela de moedas suportadas NÃO é ampliada** por C-A4. |
| C-A4-F2e | **Código não suportado continua FALHANDO.** |
| C-A4-F2f | **Moeda nunca é inferida**, e **nenhum campo adicional é lido implicitamente**. |

##### C-A4-DB — Derivação conceitual de *bindings*

| # | Regra |
|---|---|
| C-A4-DB1 | Onde **`C-A2-B`** prescreve mecanismo, a **prescrição é VINCULANTE**. |
| C-A4-DB2 | Onde **não existe** linha **`C-A2-B`** específica, `C-A2-N12` pode propor *binding* **apenas CONCEITUALMENTE** e **somente para validação read-only**. |
| C-A4-DB3 | A derivação exige **referente ÚNICO demonstrável** por: a **proposição efetivamente afirmada**; o contrato **C** / **C-A1** / **C-A2** / **C-A3**; e a **estrutura atual da base**. |
| C-A4-DB4 | **Nunca inferir vínculo por coincidência textual** (C-15a). |
| C-A4-DB5 | Havendo **dois ou mais conjuntos plausíveis** de *bindings* cuja escolha **possa alterar o veredito**: **`NÃO DETERMINÁVEL`**. **`C-A2-N12` NÃO arbitra.** |
| C-A4-DB6 | **`C-A2-RT7` permanece**: **exatamente um referente** por *binding*. |
| C-A4-DB7 | Derivação conceitual **NÃO cria**: *binding* físico, `ASSERTIVA` física, *template* físico, índice nem entrada YAML. |
| C-A4-DB8 | Qualquer **`NÃO DETERMINÁVEL` residual** impede **`C-A2-N12` = CUMPRIDA** (C-A4-G4). |

##### C-A4-NA — `R05` `F2` / `F3`

| # | Regra |
|---|---|
| C-A4-NA1 | **`R05` `F2`** e **`R05` `F3`** **não possuem** literal variável, *placeholder*, `RENDERIZADO` nem formatador. |
| C-A4-NA2 | Portanto **`C-15` = `N/A`** e **`C-8` = `N/A`** para esses fragmentos. |
| C-A4-NA3 | **`N/A` NÃO significa ausência de validação** (C-A4-VOC8). |
| C-A4-NA4 | Eles continuam **obrigatoriamente validados** por **`C-A2-RT`**, **`C-A2-V`**, **`ASSERTIVA` conceitual** e pelas regras aplicáveis de **status**, **bijeção** e **`C-A1`**. |
| C-A4-NA5 | **Nenhuma `ASSERTIVA` física é materializada.** |

##### C-A4-P — Proposição completa

| # | Regra |
|---|---|
| C-A4-P1 | Para **`C-15`**, a equivalência continua sendo julgada sobre o **fragmento inteiro**, conforme **`C-15c`**. Para **`C-8`**, havendo **fato variável / `RENDERIZADO`**, a análise deve considerar **também** se a **prosa estática que o circunda altera semanticamente a proposição factual**. |
| C-A4-P2 | **Prosa estática não pode ser usada para transformar semanticamente um fato variável** sem que **`C-8`** adjudique essa transformação. |
| C-A4-P3 | Exemplo **METODOLÓGICO**, **sem valor e sem veredito**: um **qualificador de aproximação** diante de **fato estruturado exato** **não pode ser automaticamente excluído** de **`C-8`** apenas porque está **fora do *placeholder***. |
| C-A4-P4 | **C-A4 não julga nenhum `Rxx`.** **Todo veredito pertence à execução futura de `C-A2-N12`.** |

##### C-A4-X — Não reescrita e não revogação

**C-A4 NÃO REVOGA os blocos anteriores.** **C-6**, **C-8**, **C-15**, **C-A1**, **C-A2** e
**C-A3** permanecem **vigentes**. Os **ÚNICOS refinamentos** introduzidos por `C-A4` são os
**expressamente enumerados em C-A4**, e eles prevalecem sobre as camadas anteriores apenas na
matéria que `C-A4` declara fechar (**`C-P`**).

Preservados explicitamente: **`C-15d`**; **`C-A1-ST`**; **`C-A2-RT7`**; **`C-A2-N`**;
**`C-A3`**; **`C-12`**; **`F4`** / **`F4-B`**; **`R2`**; **`S2-D8`**.

**C-A4 não cria**: índice; *template* físico; *binding* físico; `ASSERTIVA` física; status;
quarto status; formato novo; predicado novo; metadado YAML; *flag* YAML; componente;
responsabilidade; estado; evento; transição; condição de ciclo; `E09`; erro; cenário; nem
subetapa.

#### Micro-arbitragem C-A5 — identidade física do fragmento emitível

`C-A5` refina o contrato `C` quanto à **identidade física do fragmento emitível**, segundo
**`C-P`**. Ela **define a representação**; **não executa a sua aplicação física ao corpus**.

Ela fecha **exclusivamente** essa matéria, e **nenhuma outra**. Ela **não cria o índice**,
**não cria *template* físico**, **não cria *binding* físico**, **não cria `ASSERTIVA`
física**, **não altera `knowledge/**`** e **não materializa** **C**, **R2** ou **S2-D8**.

##### C-A5-U — Fronteira física futura

| # | Regra |
|---|---|
| C-A5-U1 | A **unidade emitível física futura** é um **bloco de citação contíguo**: a **sequência maximal de linhas iniciadas por `>`**, terminada pela **primeira linha que não se inicia por `>`**. |
| C-A5-U2 | A unidade **vive dentro de uma seção `## Rxx`**. |
| C-A5-U3 | **SOMENTE NA REPRESENTAÇÃO MATERIALIZADA**, conforme **C-A5-M2**: a unidade emitível **existe se e somente se** estiver **imediatamente precedida por marcador válido C-A5**. |
| C-A5-U4 | **SOMENTE NA REPRESENTAÇÃO MATERIALIZADA**: **nota**, **instrução operacional**, **comentário editorial** e **conteúdo não emitível** **não podem** ser representados como **bloco de citação emitível**. Eles permanecem **fora da bijeção**, **sem status**, **sem *binding*** e **sem `ASSERTIVA`** (**C-2m**–**C-2p**, **C-A1-B2**). **A classificação do corpus atual NÃO muda retroativamente.** |

##### C-A5-I — Identidade

| # | Regra |
|---|---|
| C-A5-I1 | **Marcador**: `<!-- fragmento: <id> -->` — **linha contendo exatamente essa estrutura**, **sem conteúdo adicional**. |
| C-A5-I2 | O marcador ocupa a **linha imediatamente anterior** à **primeira linha do bloco**. **Zero linha em branco** entre marcador e bloco. |
| C-A5-I3 | **Gramática fechada do `id`**: **`F`** seguido de **inteiro decimal ASCII maior que zero e sem zero à esquerda**. Exemplos **sintéticos** válidos: `F1`, `F2`, `F10`. Exemplos **sintéticos** inválidos: `F0`, `F01`, `f1`, `F-1`. |
| C-A5-I4 | **Unicidade do `id`**: **somente dentro do respectivo `Rxx`** — o que **preserva literalmente C-2h**. |
| C-A5-I5 | **Identidade declarada, nunca derivada.** Ela **não pode depender** de: **posição**; **ordem**; **linha**; **offset**; **índice**; **redação**; **whitespace**; **conteúdo comercial**; **hash**; **timestamp**; **UUID sem regra de governança**; **LLM**; **banco**; ou **serviço externo**. |
| C-A5-I6 | Após **C-A5-M2**, um `id` **nunca é reutilizado** dentro do mesmo `Rxx`, **mesmo após a remoção daquele fragmento**. |
| C-A5-I7 | **Reordenação, inserção, remoção ou reescrita não muda a identidade das unidades restantes.** Mudança de identidade é **ato documental explícito**. |
| C-A5-I8 | **Identidade de fragmento é distinta** do **identificador estrutural de item de coleção** do YAML de **C-A1-S3**–**C-A1-S5** / **MD-18**. **Uma não substitui nem deriva da outra.** |

##### C-A5-T — Token canônico

| # | Regra |
|---|---|
| C-A5-T1 | **Identidade canônica**: `<Rxx>/<id>`. |
| C-A5-T2 | **Separador normativo**: `/`. **Justificativa permitida e EXAUSTIVA**: **`/` não pertence à gramática de `Rxx`**; e **`/` não pertence à gramática do `id` de C-A5**. **Nenhuma outra justificativa é autorizada.** |
| C-A5-T3 | A composição é **injetiva** e a decomposição é **unívoca** porque: **`Rxx` tem forma fechada**; **o `id` tem forma fechada**; e **nenhum dos dois admite `/`**. |
| C-A5-T4 | A identidade canônica **será o token** dos **dois domínios físicos** de **C-A1-B3** / **C-A1-B4**. **Isso NÃO executa a bijeção.** |
| C-A5-T5 | O token é **derivado, nunca armazenado**. O futuro índice mantém **o `Rxx`** e **`fragmentos[].id`** **separadamente**. **Nenhum campo novo de token canônico é criado.** |

##### C-A5-M — Ativação e materialização

| # | Regra |
|---|---|
| C-A5-M1 | A **aplicação física** da representação definida por `C-A5` exige uma **entrega de materialização separada, auditada e integrada**. `C-A5`, por si, **não a ativa**. |
| C-A5-M2 | **Somente após essa materialização** a representação marcada passa a ser **obrigatória**. |
| C-A5-M3 | **Enquanto `C-A5-M2` não valer**, a **representação marcada não é obrigatória**: `knowledge/respostas-aprovadas.md` permanece na **representação física aprovada**, as unidades emitíveis documentadas continuam **reconhecidas**, a **ausência de marcador `C-A5` não é erro do corpus**, **nenhum bloco existente fica fail-closed** por `C-A5`, e a **autoridade de status permanece no Markdown** (**`C-11`**). |
| C-A5-M4 | **`C-A5` NÃO executa a aplicação física da identidade ao corpus**: ela **não insere marcador**, **não atribui `id`**, **não produz nem aprova a tabela de mapeamento** e **não decide caso individual**. |
| C-A5-M5 | A **futura aplicação exige**, **ANTES de qualquer edição do corpus**, **tabela completa e aprovada** — `Rxx` + **unidade física atual** → **`id` C-A5** — para **todas as unidades abrangidas**. **IDs de fragmento já comprometidos por documentação normativa anterior deverão ser preservados.** Os **`id` de `R09/F1` e `R09/F2`** são os **declarados na tabela `C-A5-M5`**; `C-A5` **não deriva** esses `id` por posição ou conteúdo. |
| C-A5-M6 | **Posição e ordem** podem servir **APENAS** como **localizador de evidência apresentado ao responsável humano**. Elas **jamais determinam o `id`**. |

##### C-A5-X — Falhas futuras e limites

| # | Regra |
|---|---|
| C-A5-X1 | **SOMENTE após C-A5-M2**, são **fail-closed**: **bloco destinado à emissão sem marcador válido**; **marcador órfão**; **marcador sem bloco imediatamente seguinte**; **marcador fora de `Rxx`**; **`id` fora da gramática**; **`id` repetido no mesmo `Rxx`**; e **`Rxx` sem unidade emitível quando C-2c a exige**. **Nenhum caso é resolvido por inferência.** |
| C-A5-X2 | **C-A5 NÃO decide**: a **propagação do status do cabeçalho `Rxx` aos fragmentos**; nem o **mapeamento concreto de `PARCIAL`**. **Ambos continuam ABERTOS.** |
| C-A5-X3 | **C-A5 NÃO decide**: **sintaxe de *placeholder***; **gramática de `caminho_yaml`**; **formato `hora`**; nem **C-7**. |
| C-A5-X4 | **C-A5 NÃO**: cria índice; cria *template* físico; cria *binding* físico; cria `ASSERTIVA` física; implementa extrator; implementa *renderer*; executa a bijeção física; nem migra autoridade de status. **`C-A5`, isoladamente, não satisfaz `C-A1-ST6`–`C-A1-ST10`.** |
| C-A5-X5 | **C-A5 não cria**: componente; responsabilidade; condição; evento; estado; transição; ação; erro de runtime; cenário de runtime; status; formato; predicado; nem subetapa. |

##### Escopo dos refinamentos de C-A5

**C-A5 NÃO REVOGA os blocos anteriores.** **C-2**, **C-11**, **C-15**, **C-A1**, **C-A2**,
**C-A3** e **C-A4** permanecem **vigentes**. Os **ÚNICOS refinamentos** introduzidos por
`C-A5` são os **expressamente enumerados em C-A5**, e eles prevalecem sobre as camadas
anteriores exclusivamente na **identidade física do fragmento** (**`C-P`**).

#### Registro C-A5-M5 — mapeamento humano aprovado das 37 unidades

Registro **documental** do mapeamento de identidade exigido por **`C-A5-M5`** como **gate
anterior à edição** do corpus. Ele **não reescreve `C-A5`**, **não renumera seção alguma**,
**não altera `knowledge/**`**, **não insere marcador** e **NÃO executa essa edição**.

**Aprovação humana explícita registrada:** o responsável aprovou o mapeamento de identidade
das **37 unidades físicas**, **incluindo `R23/F2` como a unidade de decoração**. Essa
aprovação **não autoriza** aplicação de marcadores, edição do corpus, criação do índice real,
extrator, *renderer*, *bindings* físicos, execução da bijeção nem migração de autoridade de
status.

**Corpus-base deste mapeamento:** `knowledge/respostas-aprovadas.md`. A tabela vale **para
esse corpus-base**; se o corpus mudar antes da aplicação, o mapeamento precisa ser
**reconferido**.

**Base da atribuição — três categorias fechadas, e nenhuma delas é ordinal:**

| Base | Significado |
|---|---|
| **PRESERVAÇÃO NORMATIVA** | o `id` já estava **comprometido por documentação normativa anterior** e é **preservado** por **`C-A5-M5`**. |
| **DECISÃO HUMANA EXPLÍCITA** | não havia `id` comprometido; o `id` foi **declarado agora pelo responsável humano** no ato de aprovação de **`C-A5-M5`**. |
| **CONFIRMAÇÃO HUMANA EXPLÍCITA** | o `id` já estava comprometido, mas **qual unidade física o portava não estava declarado**; o responsável humano **declarou o portador**. |

**Regra de leitura obrigatória (`C-A5-I5`, `C-A5-M6`).** As colunas de localizador —
`bloco 1`, `bloco 2`, `bloco 3` e os descritores de matéria — são **APENAS localizador da
evidência física atual apresentado ao responsável humano**. Elas **NÃO originaram nenhum
`id`**. **Nenhum `id` desta tabela foi derivado de posição, ordem, linha, offset, índice ou
unicidade da unidade**: em particular, **nenhum `Rxx` de fragmento único recebeu `F1` por ser
único ou primeiro**, e **nenhuma segunda unidade recebeu `F2` por vir depois**. A identidade
é **declarada** — por documentação normativa anterior ou por decisão humana registrada aqui.

##### Tabela C-A5-M5 — 37 unidades físicas atuais

| # | Rxx | localizador da unidade física atual | id | base | referência |
|---|---|---|---|---|---|
| 1 | R01 | bloco único | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 2 | R02 | bloco único | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 3 | R03 | bloco único | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 4 | R04 | bloco único | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 5 | R05 | unidade já declarada no corpus como `F1` — papel *fallback* | `F1` | PRESERVAÇÃO NORMATIVA | `C-A2-B10`, `C-A2-B16a` |
| 6 | R05 | unidade já declarada no corpus como `F2` — consulta válida + disponível | `F2` | PRESERVAÇÃO NORMATIVA | `C-A2-B16-A`, `C-A2-B16b` |
| 7 | R05 | unidade já declarada no corpus como `F3` — consulta válida + indisponível | `F3` | PRESERVAÇÃO NORMATIVA | `C-A2-B16-B`, `C-A2-B16c` |
| 8 | R06 | bloco único | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 9 | R07 | bloco único | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 10 | R08 | bloco único | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 11 | R09 | bloco 1 | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 12 | R09 | bloco 2 | `F2` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 13 | R10 | bloco único | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 14 | R11 | unidade de duração / limite de término | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 15 | R11 | unidade de montagem / desmontagem | `F2` | PRESERVAÇÃO NORMATIVA | `MD-5`, `C-A2-B1` |
| 16 | R12 | unidade de itens inclusos | `F1` | PRESERVAÇÃO NORMATIVA | `C-A2-B2`, `MD-19` |
| 17 | R12 | unidade de não incluso | `F2` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 18 | R13 | bloco único | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 19 | R14 | bloco único | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 20 | R15 | bloco único | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 21 | R16 | bloco único | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 22 | R17 | bloco único | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 23 | R18 | bloco único | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 24 | R19 | bloco único | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 25 | R20 | bloco único | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 26 | R21 | bloco único | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 27 | R22 | bloco único | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 28 | R23 | unidade de restrições / motivo de fogos | `F1` | PRESERVAÇÃO NORMATIVA | `C-A2-B5` |
| 29 | R23 | unidade de decoração | `F2` | CONFIRMAÇÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5`; leitura reconciliada abaixo |
| 30 | R24 | bloco único | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 31 | R25 | unidade de cozinha / equipamentos e rede elétrica | `F1` | PRESERVAÇÃO NORMATIVA | `C-A2-B6` |
| 32 | R25 | unidade de som / iluminação cênica / gerador | `F2` | PRESERVAÇÃO NORMATIVA | `MD-10` |
| 33 | R26 | bloco único | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 34 | R27 | bloco único | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 35 | R28 | bloco único | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 36 | R29 | bloco único | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |
| 37 | R30 | bloco único | `F1` | DECISÃO HUMANA EXPLÍCITA | aprovação `C-A5-M5` |

**Fechamento aritmético.** **37** unidades; **30** `Rxx`; **24** `Rxx` de fragmento único e
**6** multi-fragmento — `R05` = 3, `R09` = 2, `R11` = 2, `R12` = 2, `R23` = 2, `R25` = 2:
**24 + 3 + 2 + 2 + 2 + 2 + 2 = 37**. Por base: **8** por **PRESERVAÇÃO NORMATIVA**, **1** por
**CONFIRMAÇÃO HUMANA EXPLÍCITA** e **28** por **DECISÃO HUMANA EXPLÍCITA** — **8 + 1 + 28 =
37**. **Nenhuma unidade permanece sem `id` aprovado.**

**Unicidade e gramática.** Os **37** tokens canônicos derivados `<Rxx>/<id>` (**`C-A5-T1`**,
**`C-A5-T5`** — derivados, **nunca armazenados**) são **distintos dois a dois**; **nenhum
`id` se repete dentro do mesmo `Rxx`** (**`C-A5-I4`**, **C-2h**); e a repetição de **`F1`**
entre `Rxx` **distintos** é **válida**, porque a unicidade é **local ao `Rxx`**. Todos os
`id` respeitam **`C-A5-I3`**: **`F`** seguido de inteiro decimal ASCII **maior que zero** e
**sem zero à esquerda**.

##### Resolução de `R23/F2` — reconciliação de leitura, sem reescrita

A **pendência identificada no inventário read-only A1** era: **qual unidade física porta
`R23 F2`**, a partir da **leitura conjunta de `MD-13` e `C-A2-B5`** — **`MD-13`** declara
alvo `R23 F2` com escopo de modelagem que abrange **dois fatos**: o **motivo de fogos**, que
reside na unidade já fixada como `R23/F1` por **`C-A2-B5`**, e a **regra de decoração**, que
reside na outra unidade. **Os `id` de `R09/F1` e `R09/F2` são os declarados na tabela
`C-A5-M5`**, e não são derivados por posição ou conteúdo.

Decisão humana registrada: **`R23/F2` designa fisicamente a unidade de decoração.**

Reconciliação, **sem reescrever `MD-13` nem `C-A2-B5`**:

| # | Leitura |
|---|---|
| 1 | **`C-A2-B5` preserva `R23/F1`**. |
| 2 | **`MD-13` permanece vigente como contrato de modelagem.** |
| 3 | O **escopo de modelagem** de `MD-13` **pode envolver fatos relevantes a mais de um fragmento** — alvo de modelo **não é** designação de identidade física. |
| 4 | A referência de `MD-13` a `R23 F2` **NÃO desloca o motivo de fogos de `R23/F1`**. |
| 5 | Para **IDENTIDADE FÍSICA C-A5**, **`R23/F2` = unidade de decoração**. |

Isto é **clarificação de mapeamento físico**. **`MD-13` NÃO é executada**, **nenhum
conteúdo é alterado** e **nenhuma prosa é atomizada** por este registro.

##### Limites deste registro

Este mapeamento **define identidade física**; ele **não executa materialização física do
corpus**, **não migra autoridade de status** e **não substitui os gates de materialização**
definidos neste documento. Enquanto **`C-A5-M2`** não valer, a representação marcada **não é
obrigatória** (**`C-A5-M3`**), e a **autoridade de status** permanece em
`knowledge/respostas-aprovadas.md` (**`C-11`**).

---

#### Micro-arbitragem documental da gramática de caminho_yaml

Refinamento que fecha, segundo **`C-P`**, **uma única** matéria: **qual é a
gramática determinística de `caminho_yaml`**. Ela **não** reescreve, renumera ou substitui
`C-1`–`C-15`, `C-A1`, `C-A2`, `C-A5`, `MT1`–`MT12`, `SP1`–`SP7`, `G2`/`GR1`–`GR7` ou
`PM1`–`PM12`, **não** cria versão concorrente deles, **não** altera o vocabulário fechado de
**`C-3`** e **não** cria identificador normativo novo: **`C-A6` NÃO EXISTE**, e **nenhuma
subetapa é criada**. Os rótulos
**`CY1`**–**`CY14`** abaixo são **locais deste bloco**, existem **somente** como rastreabilidade
interna e **não são normativos fora desta micro-arbitragem**: não são etapa, subetapa, `Exx`,
nem nomenclatura de `C`.

Este bloco define somente o contrato; a implementação de módulo, função, assinatura, exceção
e mensagem técnica pertence à fronteira executora correspondente.
Este contrato **não cria índice**, **não materializa *binding*** e **não altera
`knowledge/**`**.

**A decisão adotada é a alternativa `A2`: `caminho_yaml` permanece semanticamente uma `str`,
com CAMINHO ABSOLUTO SEM MARCADOR e CAMINHO RELATIVO EXPLICITAMENTE MARCADO POR `@`.**

##### `CY1` — objeto arbitrado: a `str` depois do parsing

`caminho_yaml` é, **depois do parsing YAML**, uma **`str`**. Esta gramática governa **essa
`str`**, e **nada mais**. Ela **não** decide sintaxe de arquivo, estilo de serialização,
*loader*, ordem de chaves, comentários ou qualquer aspecto físico do futuro índice. **A
gramática é semântica**, não textual-de-arquivo.

##### `CY2` — as duas formas semânticas, e apenas duas

| Forma | Marcador inicial | Raiz de resolução | Onde é permitida |
|---|---|---|---|
| **Absoluta** | **nenhum** | o **mapeamento raiz** de `knowledge/casa77.yaml` **já carregado** | **fora** de `itera_sobre` **e também dentro** de fragmento que possua `itera_sobre` |
| **Relativa** | **`@`**, exatamente na posição inicial | o **item corrente** da coleção percorrida por `itera_sobre` | **somente** em *binding* de fragmento que **declare** `itera_sobre` |

Um caminho relativo em fragmento **sem** `itera_sobre` é ***FAIL-CLOSED* estrutural**.

**A forma é sempre explícita na própria `str`.** **O contexto jamais transforma silenciosamente
um caminho absoluto em relativo**, nem o contrário: não há promoção, rebaixamento, inferência
ou reinterpretação por vizinhança.

##### `CY3` — `C-4h` e `C-A1-S2` permanecem literais

**`C-4h` permanece literal**: os *bindings* do item **PODEM** usar caminho relativo. **`C-A1-S2`
disciplina a disponibilidade e a semântica dos caminhos relativos durante a iteração** — ela
**NÃO** torna todos os *bindings* de um fragmento iterado **obrigatoriamente** relativos.
Portanto, **num mesmo fragmento com `itera_sobre`, *bindings* absolutos e relativos podem
coexistir**, cada um dizendo o que é **na própria `str`**. **`C-A1-S1` (proibição de seleção
posicional) permanece literal e inalterada.**

##### `CY4` — gramática semântica

```text
caminho           ::= caminho_absoluto | caminho_relativo

caminho_absoluto  ::= segmento ( "." segmento )*
caminho_relativo  ::= "@" ( "." segmento )*

segmento          ::= chave seletor?
seletor           ::= "[" chave "=" literal "]"

chave             ::= NOME, exceto se composta exclusivamente por dígitos
literal           ::= NOME

NOME              ::= um ou mais caracteres de:
                      A-Z
                      a-z
                      0-9
                      _
```

**Alfabeto semântico permitido, e nada além**: `A-Z`, `a-z`, `0-9`, `_`, `.`, `[`, `]`, `=` e
`@`. Qualquer outro caractere na `str` torna a forma **inválida**.

##### `CY5` — canonicalidade semântica

Dentro da `str` **já parseada**: ***whitespace* PROIBIDO**; **aspas como caracteres do valor
PROIBIDAS**; ***escape* inexistente**; **Unicode não ASCII PROIBIDO**; **caixa
significativa**; **sem normalização**; **sem `casefold`**; **sem coerção**; **sem tolerância**.

São **inválidos**: `.` final (*trailing*); **segmento vazio**; **seletor vazio**; **chave
seletora vazia**; **literal vazio**; **`@` fora da posição inicial**; e **dois seletores no
mesmo segmento**.

##### `CY6` — YAML físico × valor semântico

**A gramática `CY` governa a `str` APÓS o parsing YAML.** O caractere `@` **não pode iniciar um
*plain scalar* YAML**. Logo, no **futuro** arquivo físico do índice, um caminho relativo deverá
ser serializado **com *quoting* YAML** — por exemplo, de forma **sintética**:

```yaml
caminho_yaml: "@.campo_exemplo"
```

**As aspas pertencem à serialização YAML.** Elas **NÃO** pertencem à `str` e **NÃO** pertencem à
gramática `CY`. **Nada aqui decide aspas simples × duplas como estilo canônico**: ambas são
**apenas serialização** quando produzem **a mesma `str`**.

##### `CY7` — literal seletor é sempre `str` (restrição deliberada do MVP)

**RESTRIÇÃO NORMATIVA DELIBERADA DO MVP**: o **literal seletor** é **sempre semanticamente uma
`str`**, com conteúdo em `[A-Za-z0-9_]+`. **Zero inferência** de **inteiro**, **boolean**,
**`null`** ou **qualquer outro tipo YAML**. A comparação futura é **literal**, **por `str`** e
**sem coerção**.

##### `CY8` — serialização dos identificadores no YAML comercial

Do lado da base autoritativa: **um identificador estrutural usado por `caminho_yaml` DEVE
resultar em `str` depois do parsing de `knowledge/casa77.yaml`**. Se um futuro identificador
introduzido por **`MD-18`** possuir conteúdo que, escrito como *plain scalar*, seja interpretado
pelo *loader* YAML como **número**, **boolean**, **`null`** ou **outro tipo não-`str`**, ele
**DEVERÁ ser serializado com *quoting* YAML** no arquivo factual. Exemplo **apenas sintético**:
um identificador semântico `"2026"` precisa **permanecer `str`**, e **não** virar inteiro. **As
aspas pertencem à serialização e não fazem parte do identificador semântico.**

**`knowledge/casa77.yaml` NÃO é alterado por esta entrega**, e **nenhum identificador novo é
criado aqui**.

##### `CY9` — chave exclusivamente numérica

Uma chave YAML textual `"123"` **NÃO é semanticamente uma posição**. Ainda assim, **a gramática
do MVP deliberadamente NÃO a torna endereçável**: **chave composta apenas de dígitos é forma
inválida de `caminho_yaml`**.

Os motivos são **três, e apenas estes**: **fechamento conservador**; **auditabilidade
estática**; e **compatibilidade com a materialização vigente de `C-A1-S1` em `E1`**. **Não se
escreve aqui, e não se lê daqui, que "chave numérica = posição".**

##### `CY10` — seletor

Forma: **`[chave=literal]`**, **no máximo um por segmento**. Permitido em **caminho absoluto**,
em **caminho relativo** e em **`itera_sobre` absoluto**.

**Proibidos**: `[0]`; **posição**; `first`; `last`; ***fallback***; **busca parcial**;
***substring***; **similaridade**; e **inferência** de qualquer espécie.

Resolução: **zero *matches* → *FAIL-CLOSED***; **um *match* → continua**; **mais de um *match*
→ *FAIL-CLOSED***.

##### `CY11` — `@` isolado

**`@`**, sozinho, é **caminho relativo válido** e significa **o próprio item corrente**. Isso
mantém **expressável** a futura iteração sobre **coleção de escalares**. **Não se afirma aqui
que o corpus atual utilize esse caso.**

##### `CY12` — `itera_sobre`: mínimo inseparável

Registra-se **somente** o mínimo que não se pode separar desta gramática: `itera_sobre` é uma
**`str`**; usa a **forma ABSOLUTA** da mesma gramática-base; **`@` é PROIBIDO em
`itera_sobre`**; precisa **resolver para uma coleção**; **seletores estruturais são
permitidos**; **mapa, escalar ou `null` como terminal de `itera_sobre` é *FAIL-CLOSED*
estrutural**; **isto não é `C-7`**; e **o item atual torna-se a raiz dos *bindings* relativos**.

**NÃO são decididos aqui**: **ordem**; **coleção vazia**; **composição textual**; **repetição de
*placeholder***; **propagação de erro entre itens**; e **execução operacional**.

##### `CY13` — três responsabilidades distintas

| Responsabilidade | Acessa o YAML factual? | O que valida |
|---|---|---|
| **Parser da gramática** | **não** | sintaxe; alfabeto; absoluto × relativo; seletor; canonicalidade; chave numérica **não endereçável** |
| **Validação estrutural do índice** | **não** | **relativo somente** em fragmento com `itera_sobre`; **`@` proibido no próprio `itera_sobre`** |
| **Resolver** | **sim**, contra o YAML **já carregado** | existência da chave; tipo intermediário; seletor sobre lista; **zero / um / múltiplos *matches***; `itera_sobre` terminando em **coleção** |

**Nenhuma dessas três é implementada aqui**, e **nenhuma fronteira técnica é desenhada**.

##### `CY14` — terminal, `C-7`, `ASSERTIVA` e `RUNTIME_AUTORITATIVO`

**Terminal.** Ao alcançar o nó terminal, a **resolução é SUCESSO** e o **valor é devolvido como
está** — podendo ser **escalar**, **lista**, **mapa** ou **`null`**. A **admissibilidade
posterior** pertence a **`C-5`**, **`C-6`** e **`C-7`**. **Nenhum juiz adicional de tipo
terminal é criado.**

**`C-7` é preservada, e NÃO é reaberta nem materializada**: **chave inexistente ≠ `null`**;
**atravessar `null` no meio é falha estrutural**; **terminal `null` significa caminho
resolvido**, e o tratamento pertence a **`C-7`**; **zero ou múltiplos *matches* são falha de
caminho**, não `C-7`; a estrutura `pendente` pertence a **`C-7`** **somente após** resolução
apropriada; e **o resolver não lê chaves irmãs por conveniência**.

**`ASSERTIVA` e `RENDERIZADO`.** A **mesma** gramática vale para `RENDERIZADO` de origem `YAML`
e para `ASSERTIVA` de origem `YAML`. A diferença entre os dois mecanismos ocorre **depois da
resolução**. **Não existe gramática paralela.**

**`RUNTIME_AUTORITATIVO` é preservado**: ele **PROÍBE** `caminho_yaml` e continua usando
**apenas** `fato_runtime`.

##### Relação com `E1` — nada é alterado

`E1` valida a **estrutura básica** e aplica **parte** da proibição posicional
(**`C-A1-S1`**); ele **NÃO fecha a gramática completa**. A materialização da gramática
**pode subsumir logicamente** parte dessas validações; **esta micro-arbitragem não migra
responsabilidade alguma**.

##### Categorias conceituais de *FAIL-CLOSED*

Apenas **conceituais**. **NÃO** são definidos aqui **classe Python**, **exceção concreta**,
**mensagem**, **herança**, **função**, **módulo**, **API** nem **precedência técnica concreta**.

| Camada | Espécies de impedimento |
|---|---|
| **Sintaxe** | forma inválida; referência **não endereçável / posicional** |
| **Estrutura do índice** | **relativo sem `itera_sobre`**; **`@` em `itera_sobre`** |
| **Resolução** | segmento inexistente; tipo estrutural incompatível; **zero *match***; **múltiplos *matches***; `itera_sobre` que **não resolve para coleção** |

Todas são ***FAIL-CLOSED***.

##### Exemplos — SOMENTE SINTÉTICOS

Os exemplos abaixo usam **nomes e identificadores INVENTADOS**. Eles **não reproduzem
identificador, valor, preço, capacidade, horário, condição comercial ou qualquer fato real** de
`knowledge/casa77.yaml`.

| Exemplo sintético | Forma | Leitura |
|---|---|---|
| `bloco_exemplo.campo_exemplo` | absoluta | dois segmentos a partir da raiz |
| `bloco_exemplo.colecao_exemplo[id=item_exemplo].campo_exemplo` | absoluta | seletor **estrutural**, exatamente um por segmento |
| `@.campo_exemplo` | relativa | um campo **do item corrente** |
| `@` | relativa | **o próprio item corrente** (`CY11`) |
| `bloco_exemplo.123` | **inválida** | chave **exclusivamente numérica** (`CY9`) |
| `bloco_exemplo.colecao_exemplo[0]` | **inválida** | **seleção posicional** (`C-A1-S1`, `CY10`) |
| `bloco_exemplo.@campo_exemplo` | **inválida** | **`@` fora da posição inicial** (`CY5`) |
| `bloco_exemplo.` | **inválida** | `.` final (`CY5`) |

**A gramática independe da distribuição estrutural do YAML.** Ela permanece válida qualquer
que seja a distribuição de coleções, listas e identificadores de um `knowledge/casa77.yaml`
aprovado, presente ou futuro.

##### Limites desta micro-arbitragem

| # | Limite |
|---|---|
| 1 | Ela fecha **somente a gramática de `caminho_yaml`**, e **não a materializa**. |
| 2 | Ela **não cria** o índice físico `knowledge/indice-respostas-aprovadas.yaml`. |
| 3 | A **sintaxe de *placeholder*** permanece **ABERTA**. |
| 4 | O **formato `hora`** é **matéria separada**, não decidida aqui (**`C-A1-F3`**, **`C-A1-F3a`**). |
| 5 | **`C-7` não é reaberta** por ela. |
| 6 | Ela **não satisfaz `C-A1-ST6`–`C-A1-ST10`** e **não migra a autoridade de status**, que permanece em `knowledge/respostas-aprovadas.md` (**`C-11`**). |
| 7 | **`C-A6` não existe** e **nenhuma subetapa é criada**. |

**ARBITRAR A GRAMÁTICA DE `caminho_yaml` NÃO É IMPLEMENTAR PARSER, NÃO É IMPLEMENTAR RESOLVER,
NÃO É CRIAR ÍNDICE, NÃO É RESOLVER *PLACEHOLDER*, NÃO É MATERIALIZAR `C-7`, NÃO É MIGRAR
AUTORIDADE E NÃO É MATERIALIZAR `C`.**

#### Micro-arbitragem documental da sintaxe física de *placeholder*

Refinamento que fecha, segundo **`C-P`**, **uma única** matéria: **qual é a sintaxe física
determinística do *placeholder* no *template* de um fragmento emitível**. Ela **não**
reescreve, renumera ou substitui `C-1`–`C-15`, `C-A1`–`C-A5`, `CY1`–`CY14`, `GR1`–`GR7`,
`MT1`–`MT12` ou `SP1`–`SP7`, **não** cria versão concorrente deles e **não** cria identificador
normativo novo: os rótulos **`PH1`**–**`PH12`** abaixo são **locais deste bloco**, existem só
para referência interna e **não** são etapa, subetapa, `Exx` nem nomenclatura normativa de `C`.
**`C-A6` não existe.** Este bloco define somente o contrato; a implementação de módulo, função,
assinatura, exceção e mensagem técnica pertence à fronteira executora correspondente.

##### `PH1` — objeto arbitrado

A gramática rege **os *placeholders* físicos presentes no *template* de um fragmento
emitível**, e **somente** isso.

Ela **NÃO** rege: **`caminho_yaml`** (`CY1`–`CY14`); **formato** (`C-6`); **predicado**
(`C-5g`, `C-5h`); **valor factual**; ***renderer***; nem **equivalência** (`C-15`).

##### `PH2` — forma canônica

Um *placeholder* é **exatamente**:

```text
{{nome}}
```

Isto é, a concatenação literal `"{{" + binding.nome + "}}"`. **Nenhum conteúdo adicional
entre os delimitadores** — sem espaço, sem filtro, sem formato, sem caminho, sem
qualificador, sem comentário.

##### `PH3` — o campo `placeholder` permanece explícito

| # | Regra |
|---|---|
| `PH3a` | O campo **`binding.placeholder`** **permanece OBRIGATÓRIO** para `RENDERIZADO`, exatamente como **`C-4c`** já exige. Ele **não** é removido do índice. |
| `PH3b` | O seu valor canônico é **obrigatoriamente** `derivar_placeholder(binding.nome)` — ou seja, `binding.placeholder == "{{" + binding.nome + "}}"`, por **comparação literal**. |
| `PH3c` | `binding.nome` é o **nome lógico**; `binding.placeholder` é a **representação física correspondente**. A correspondência obrigatória entre os dois **impede divergência** entre nome e representação. |
| `PH3d` | Isto **NÃO altera `C-4c`**: é o fechamento da representação física que `C-4c` já pressupunha. |

##### `PH4` — gramática do nome de *binding* `RENDERIZADO`

**Somente** para *bindings* `RENDERIZADO`:

```text
nome   ::= letra ( letra | digito )* ( "_" ( letra | digito )+ )*
letra  ::= a-z ASCII
digito ::= 0-9 ASCII
```

Consequências, todas literais: **não vazio**; **primeiro caractere em `a-z`**; **somente
`a-z`, `0-9` e `_`**; **`_` apenas interno**; **sem `_` inicial**; **sem `_` final**; **sem
`__`**; **sem maiúscula**; **sem Unicode não ASCII**; **sem espaço**; **sem tab nem LF**; e
**sem** `.`, `-`, `{`, `}`, `@`, `[`, `]`, `/`, `=` ou aspas.

**Nenhum limite artificial de tamanho é criado.**

Esta gramática **NÃO se estende** ao nome de `ASSERTIVA`.

##### `PH5` — as chaves são reservadas

No MVP, **`{` e `}` são reservados à sintaxe de *placeholder***. Fora de um *placeholder*
canônico, **`{` é inválido** e **`}` é inválido**.

**Não existe *escaping*.** **Nenhuma intenção é inferida.**

Se auditoria futura do corpus encontrar **chave literal legítima** em texto aprovado, a
conversão **daquele fragmento** **BLOQUEIA** e a matéria **volta ao GPT** — nunca se resolve
por tolerância local.

##### `PH6` — *parsing* literal

Varredura da **esquerda para a direita**. Ao encontrar `{`: **exigir** um segundo `{`;
**extrair** o conteúdo; **exigir** `}}`; **validar** o conteúdo por **`PH4`**.

Qualquer **envelope incompleto ou divergente** é ***FAIL-CLOSED***. São inválidos, entre
outros:

```text
{        }        {x}        {{x        x}}        {{}}
{{ x }}  {{X}}    {{x-y}}    {{{x}}}    {{x}}}
```

**Não há normalização e não há correção.**

##### `PH7` — cardinalidade

Para **cada** *binding* `RENDERIZADO` do fragmento, contadas as ocorrências do **seu**
*placeholder* no *template*:

| # | Ocorrências | Veredito |
|---|---|---|
| `PH7a` | **zero** | **FALHA** |
| `PH7b` | **uma** | **válida** |
| `PH7c` | **duas ou mais** | **válidas** |

**O mesmo *binding* abastece TODAS as ocorrências do mesmo *placeholder*.** É **PROIBIDO**
criar *bindings* artificiais adicionais apenas porque o mesmo fato é citado mais de uma vez no
*template*. **`C-4a` continua exigindo nome de *binding* único no fragmento.**

##### `PH8` — *placeholder* sem *binding*

Todo *placeholder* canônico presente no *template* deve corresponder a **exatamente um** nome
de *binding* `RENDERIZADO` recebido pelo consumidor. *Placeholder* sem *binding*
correspondente é ***FAIL-CLOSED***.

Um nome que pertença **apenas** a uma `ASSERTIVA` **não** satisfaz essa regra, porque
**`C-5d`** proíbe *placeholder* para `ASSERTIVA`.

##### `PH9` — normalização: nenhuma

**Proibidos**: `strip`, `lstrip`, `rstrip`, `lower`, `upper`, `casefold`, **NFC**, **NFD**,
coerção, tolerância de *whitespace* e correspondência aproximada.

**NFC continua pertencendo exclusivamente à equivalência de `C-15b`**, e **não** é reaberta
aqui.

##### `PH10` — decomposição

A fronteira executora recebe o **`template`** e a **tupla dos nomes** dos *bindings*
`RENDERIZADO` **do mesmo fragmento**. O sucesso produz uma sequência **alternada**:

```text
literal, nome, literal, nome, ..., literal
```

| # | Regra |
|---|---|
| `PH10a` | Os **nomes aparecem na ordem física de ocorrência no *template***, nunca na ordem da tupla de entrada. |
| `PH10b` | Um nome **pode aparecer mais de uma vez** na decomposição (`PH7c`). |
| `PH10c` | **Todos** os nomes fornecidos devem aparecer **pelo menos uma vez** (`PH7a`). |
| `PH10d` | **Nenhum** nome desconhecido pode aparecer (`PH8`). |
| `PH10e` | **Literais podem ser vazios** — inclusive nas extremidades e entre *placeholders* adjacentes. |

##### `PH11` — o *renderer* futuro

O futuro *renderer* consumirá a decomposição e fará **uma única passada** sobre ela.

**Valores formatados NÃO são reinterpretados como *template***. Portanto, se um valor factual
formatado contiver algo semelhante a `{{x}}`, isso **permanece texto factual literal** — e
**não** vira *placeholder*.

**O *renderer* não é implementado aqui.**

##### `PH12` — limites desta micro-arbitragem

| # | Limite |
|---|---|
| 1 | Ela **não cria** o índice físico `knowledge/indice-respostas-aprovadas.yaml`. |
| 2 | Ela **não cria** *renderer*. |
| 3 | Ela **não altera** `knowledge/**` e **não converte** `Rxx` reais. |
| 4 | Ela **não integra** `E1` e **não altera** `src/casa77_sdr/response_index.py`. |
| 5 | Ela **não resolve** *binding* factual, **não aplica `C-7`**, **não executa formato** e **não executa `C-15`**. |
| 6 | Ela **não resolve `S2-D8`**. |
| 7 | Ela **não satisfaz `C-A1-ST6`–`C-A1-ST10`** e **não migra a autoridade de status**, que permanece em `knowledge/respostas-aprovadas.md` (**`C-11`**). |
| 8 | **`C-A6` não existe** e **nenhuma subetapa é criada**. |

**ARBITRAR A SINTAXE FÍSICA DE *PLACEHOLDER* NÃO É CRIAR ÍNDICE, NÃO É IMPLEMENTAR RENDERER,
NÃO É RESOLVER BINDING, NÃO É INTEGRAR `E1`, NÃO É MIGRAR AUTORIDADE E NÃO É MATERIALIZAR
`C`.**

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

Sobre bibliotecas: a **validação de schema** exige dependência em qualquer das opções e
**continua sem escolha** — ela é a linha própria de §11. Qualquer nome de biblioteca que
apareça em discussão futura deste documento, para uma escolha ainda aberta, é exemplo
ilustrativo, não decisão.

Ressalva honesta: **se a etapa 7 escolher uma rota não oficial de WhatsApp**, o adaptador de
canal provavelmente será Node. Isso não invalida a decisão, porque o motor é independente de
canal (P1): o adaptador conversa com o motor por um limite simples de processo. A escolha do
canal continua adiada para a etapa 7.

Nenhum framework web está escolhido — o MVP não precisa de um. O motor é uma função
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

#### 4.1.1 Colisão de nome — `RegistroAtendimento` (pendência `B`)

O nome `RegistroAtendimento` designa hoje **dois referentes de natureza distinta**: nesta
§4.1, um **componente de comportamento**, que registra dados e correções (`E02`–`E05`) e
devolve dados atualizados mais a lista de correções; em `src/casa77_sdr/persistence.py`, uma
**dataclass `frozen` de transporte**, opaca, que por contrato **não interpreta** estado,
qualificação, dados, pendências nem motivos.

A colisão é de **categoria** — comportamento × registro de dado —, não de campo nem de
assinatura, e é agravada por esta §4.1 já designar `Persistencia` como o componente da
persistência operacional (§7.3).

**Pendência `B` — ABERTA.** Nenhum dos dois referentes é renomeado, unificado ou corrigido
aqui, e nada é resolvido silenciosamente.

**Onde se resolve:** arbitragem específica antes de implementar o componente
`RegistroAtendimento` desta §4.1. Não afeta a persistência operacional já contratada em §7.3
nem a fronteira de identidade de §7.1.

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
implementação: ela não cria código.

A máquina recebe as condições **já determinadas a montante** e nunca as calcula. Nenhum
campo carrega dado pessoal (PII), texto de mensagem ou valor comercial.

| # | Condição | Forma | Produtor |
|---|---|---|---|
| 1 | `insumo_qualificacao_atualizado` | `bool \| None` (doc 06 §4.1) | etapa 6 do pipeline (§5) |
| 2 | `pendencia_impeditiva` | `bool \| None` | **produtor conceitual: S2-D8, eixo A** (arbitragem S2-D8, abaixo; doc 06 §11). A **implementação concreta** pertence à composição do `OrquestradorMotor` |
| 3 | `motivos_handoff` | conjunto/tupla de **identificadores textuais opacos** | `DetectorHandoff` (gatilhos 3–10, doc 06 §9) |
| 4 | `resposta_aprovada_disponivel` | `bool \| None` | **produtor conceitual: S2-D8, eixo B** (arbitragem S2-D8, abaixo; doc 06 §11). A **implementação concreta** pertence à composição do `OrquestradorMotor` |
| 5 | `interesse_confirmar_disponibilidade` | `bool \| None` | **fronteira da etapa 4** (arbitragem N-b, §6.3): derivada da `Interpretacao` pela **função total** N-b-CD1–N-b-CD4, abaixo. Único produtor de `CondicoesCiclo` que N-b atribui |
| 6 | `calendario_integrado` | `bool \| None` | configuração/integração avaliada a montante |
| 7 | `identidade` | resultado estruturado do `ResolvedorIdentidade` (§7.1) | `ResolvedorIdentidade` (etapa 5) |
| 8 | `motivo_encerramento` | motivo estruturado entre as **quatro** modalidades aprovadas de T35 (doc 06 §3) | **não atribuído — S3-D1** |

As condições **2** e **4** têm **produtor conceitual** em **S2-D8**, mas **nenhum componente
arquitetural novo é criado por isso**: atribuir o **eixo A** e o **eixo B** diz **quem responde
a pergunta**, não **qual classe a implementa**. A condição **8** permanece **sem produtor
atribuído** em **`S3-D1`**.

**Condição 5 — função total** (arbitragem N-b, §6.3).

| # | Entrada | `interesse_confirmar_disponibilidade` |
|---|---|---|
| N-b-CD1 | `Interpretacao` válida + `INTERESSE_CONFIRMAR_DISPONIBILIDADE` com confiança `ALTA` | `True` |
| N-b-CD2 | `Interpretacao` válida + `INTERESSE_CONFIRMAR_DISPONIBILIDADE` com confiança `BAIXA` | `False` |
| N-b-CD3 | `Interpretacao` válida + intenção **ausente** | `False` |
| N-b-CD4 | **Sem `Interpretacao`** — produtor indisponível ou erro de contrato na fronteira da etapa 4 | `None` |

`True`/`False` significam **avaliado neste ciclo**; `None` significa **não avaliado neste
ciclo**. `None` **não** é "falso implícito".

**Precedência — S2-D8 sobre N-b quanto ao produtor das condições.** **S2-D8** (abaixo)
atribui **produtor conceitual** às condições **2** e **4** — respectivamente o **eixo A** e o
**eixo B** —, **sem escolher componente concreto**. A condição **8** (`motivo_encerramento`)
permanece **NÃO ATRIBUÍDA**: **S3-D1** está aberta. A tabela tem **oito** condições —
**nenhuma é criada, e nenhuma é removida**.

### 4.4.1 Arbitragem S2-D8 — detecção e classificação de pendências, e cobertura de resposta aprovada

**Contrato arbitrado.** Esta seção define a **detecção e a classificação de pendências** e a
**cobertura de resposta aprovada**, **antes da etapa 7** (§5).

| # | Limite de escopo de S2-D8 |
|---|---|
| D8-E1a | **não define** alteração de `src/`, `tests/`, `knowledge/` ou `prompts/` |
| D8-E1b | **não altera** §4.1, que tem **14 componentes**, nem §2, que tem **nove responsabilidades** |
| D8-E1c | **não altera** esta §4.4, que tem **oito condições**; **nenhuma condição nova** é criada |
| D8-E1d | **não cria** estado, evento, transição, critério, ação, efeito paralelo, inércia nem pendência nova |
| D8-E1e | **não cria subetapa** |
| D8-E1f | **não altera nem substitui** os contratos **AJ2** (§6.3) e **C** (§2.3) |
| D8-E1g | **não resolve `N-b-RES2`** (§5, §6.3) |
| D8-E1h | **não define a implementação do `OrquestradorMotor`** |
| D8-E1i | **não cria** a representação física do mapa de cobertura **R2** nem o índice físico de **C** |

#### D8-0 — o que S2-D8 decide

| # | Regra |
|---|---|
| D8-0a | S2-D8 responde **duas** perguntas distintas, em **dois eixos** semanticamente independentes: o eixo **A**, de **qualificação**, e o eixo **B**, de **resposta**. |
| D8-0b | Ela é integralmente **a montante** da etapa 7. A `MaquinaEstados` **não detecta**, **não reclassifica** e **não recalcula** pendência (doc 06 §2.2). |
| D8-0c | **Nenhum componente concreto é escolhido**: não é o `CarregadorYaml`, não é o `ValidadorYaml`, não é o `SeletorFatos`, não é o `ValidadorConsistenciaBase` e não é o `Qualificador`. |
| D8-0d | S2-D8 **não replica a precedência de qualificação**: o `Qualificador` continua **função pura** e continua sendo quem classifica (§4.1). |

#### D8-A — eixo A (qualificação)

Pergunta do eixo A:

> **"existe indisponibilidade válida na base que impede a classificação do evento NESTE
> ciclo?"**

| # | Regra |
|---|---|
| D8-A1 | O eixo A **não depende** de `PerguntaComercial` nem de `AssuntoComercial`. Ele é **semanticamente independente** da existência de consulta comercial no ciclo. |
| D8-A2 | Produz `pendencia_impeditiva` — a **condição 2** desta §4.4. |
| D8-A3 | Produz `pendencias_impeditivas`, a tupla de **identificadores técnicos** entregue ao `Qualificador` (§4.1). **Nunca** a pergunta bruta, **nunca** PII, **nunca** valor comercial. |
| D8-A4 | Produz **causa** que pode confirmar `E09` (doc 06 §2.2). |
| D8-A5 | O eixo A **não cria pergunta** em `pendencias_resposta` (doc 06 §1.3, §4.3 **P5**). |

**Regra impeditiva — `IMP-1` a `IMP-4`.** Uma indisponibilidade da base é **impeditiva**
**somente quando as quatro** condições valem no mesmo ciclo:

| # | Condição |
|---|---|
| IMP-1 | pertence ao **universo de dados determinantes da qualificação** |
| IMP-2 | é **efetivamente necessária** para classificar **ESTE** ciclo |
| IMP-3 | **nenhuma violação objetiva** já determinou `INCOMPATIVEL` |
| IMP-4 | **nenhum dado obrigatório do interessado** ainda está ausente |

| # | Invariante |
|---|---|
| D8-A6 | `pendencia_impeditiva == True` **IMPLICA** `Qualificacao.resultado == INDEFINIDO` (doc 06 §1.2, I10). |
| D8-A7 | **Nunca documentar como caminho normal** a combinação `E09` **impeditivo** + `Qualificacao == DADOS_INCOMPLETOS`: **IMP-4** a exclui por construção, e **IMP-3** exclui simetricamente a combinação com `INCOMPATIVEL`. |

**`Q1` — decisão normativa do MVP.**

| # | Decisão |
|---|---|
| Q1-a | Os campos hoje exigidos **estruturalmente** pelo carregador da base continuam **PRÉ-REQUISITOS da base** e **não** viram pendência de S2-D8. |
| Q1-b | **Não transformar em pendência S2-D8** um `null`, uma ausência ou um tipo inválido em requisito que o **carregador já rejeita**: ali o **motor não inicia** (§7), o que **não é caso de ciclo**. |
| Q1-c | Consequência direta: **nenhum arquivo de `src/` muda por S2-D8**. Em particular, `knowledge.py` **não muda**, `rules.py` **não muda**, `qualification.py` **não muda** e `state_machine.py` **não muda**. |
| Q1-d | No **schema e no corpus atuais**, `pendencia_impeditiva = True` **pode ser legitimamente inalcançável**. Isso **NÃO elimina a condição 2**: ela permanece na tabela, com produtor conceitual, e o contrato fica **preparado para evolução futura**. |
| Q1-e | A evolução **`Q2`** — **permitir que algum campo determinante da qualificação seja validamente `null`/`pendente`**, em vez de esse estado ser tratado como **falha estrutural da base** — **NÃO é autorizada agora** e **não é recomendada para o MVP**. Ela permanece **futura** e exigiria **evolução explícita dos contratos afetados** de `knowledge.py`, `rules.py` e/ou `qualification.py` **antes** de qualquer materialização. |

#### D8-B — eixo B (resposta)

Pergunta do eixo B:

> **"existe cobertura aprovada e emitível para os `AssuntoComercial` efetivamente
> consultados?"**

| # | Regra |
|---|---|
| D8-B1 | O eixo B consome **somente `PerguntaComercial` com confiança `ALTA`** (N-b-Q2, N-b-Q3, §6.3). Pergunta `BAIXA` **não entra** — nem como consulta, nem como pendência. |
| D8-B2 | O eixo B **não usa texto como chave semântica**. A chave é o **`AssuntoComercial`** (AJ2, §6.3); o `texto` é **conteúdo persistido**, jamais critério de decisão. |
| D8-B3 | Produz `resposta_aprovada_disponivel` — a **condição 4** desta §4.4. |
| D8-B4 | Produz **uma avaliação por assunto** efetivamente consultado. |
| D8-B5 | Produz **causas acessórias** que podem confirmar `E09`. |
| D8-B6 | Produz a **associação posterior** das perguntas **efetivamente não respondidas** aos itens de `pendencias_resposta` (doc 06 §1.3, §4.3 **P5**). |

#### D8-E — composição das causas e `E09`

| # | Regra |
|---|---|
| D8-E2 | `E09` é a **união das causas** do eixo **A** e do eixo **B**: **A ∪ B**. |
| D8-E3 | **No máximo um `E09` por ciclo.** Não existe `E09` múltiplo (doc 06 §4.2, consumo único). |
| D8-E4 | Avaliar **todas** as causas estruturais da lacuna; o conjunto de motivos do `E09` é a **união, deduplicada e canonicalizada**. |
| D8-E5 | Um caso **misto** pode carregar **ambos** os motivos. |
| D8-E6 | A **classificação impeditiva × acessória** que acompanha `E09` (doc 06 §2.2) continua sendo o que separa **T11/T18** de **T12/T19**. Causa do **eixo A** que satisfaça `IMP-1`–`IMP-4` é **impeditiva**; causa do **eixo B** é **acessória**. |

**Vocabulário fechado de motivos de `E09` — exatamente DOIS.** **Nenhum terceiro motivo
pode ser criado.**

| # | Motivo | Quando ocorre |
|---|---|---|
| 1 | `CAMPO_INDISPONIVEL` | um *binding* necessário resolve para `null` ou para estrutura cujo `status` é `pendente`. É a forma da **causa futura do eixo A**. Carrega o **caminho YAML**; **no eixo B carrega também o assunto** |
| 2 | `SEM_RESPOSTA_APROVADA_EMITIVEL` | alternativa ou status **não emitível** deixa um **grupo descoberto**; `ASSERTIVA` **divergente** deixa um **grupo descoberto**; **zero grupos**; **`ASSUNTO_NAO_CLASSIFICADO`** |

| # | Regra de conteúdo |
|---|---|
| D8-E7 | Nenhum motivo carrega **texto livre**, **PII** ou **valor comercial**. O **caminho YAML estrutural** é permitido; o **valor** do campo, nunca. |
| D8-E8 | Os motivos de `E09` permanecem **metadados estruturados de auditoria A MONTANTE**. Eles **NÃO integram `CondicoesCiclo`** (§4.4) e **NÃO são entrada da `MaquinaEstados`**; **nenhum campo novo é criado na máquina**. Para a máquina chegam apenas **`Evento.E09`** e a classificação já estruturada **`pendencia_impeditiva`** — além das demais condições já existentes quando aplicáveis. A máquina **não interpreta os motivos** e **não referencia nenhum `Rxx`** (doc 06 §11). |

#### R2 — mapa de grupos de cobertura (registro FORA de C)

Formalização do **mapa futuro**. Ele **não é criado aqui**, **não existe em `knowledge/`**,
**não é autorizado** por esta arbitragem e **não pertence a C**: **C-12a–C-12h permanecem
inalteradas** (§2.3).

| # | Regra |
|---|---|
| R2-1 | Cada `AssuntoComercial` mapeia para **0..N grupos de cobertura**. |
| R2-2 | Cada grupo contém **1..N alternativas**. |
| R2-3 | Uma **alternativa** é **referência estrutural** — `Rxx` + identificador de fragmento. **Sem texto**, **sem valor comercial**, **sem status duplicado**, **sem *binding* duplicado**, **sem caminho YAML duplicado** e **sem predicado duplicado**. O mapa **referencia**; ele **não copia** o que já vive no índice de C ou no YAML. |
| R2-4 | Semântica: **CONJUNÇÃO entre grupos**, **DISJUNÇÃO dentro de cada grupo**. |
| R2-5 | Um assunto é **respondível** quando **possui ao menos um grupo** e **TODOS** os seus grupos possuem **ao menos uma alternativa emitível agora**. |
| R2-6 | **`ASSUNTO_NAO_CLASSIFICADO` tem zero grupos por definição** — logo **não é respondível**, e a causa correspondente é `SEM_RESPOSTA_APROVADA_EMITIVEL`. |
| R2-7 | Referência do mapa a **fragmento inexistente** é **Classe I** (abaixo). |

#### D8-F — fragmento emitível agora

Um fragmento é **emitível agora** **somente se as três** condições valem:

| # | Condição |
|---|---|
| D8-F1 | `status = APROVADO` (**C-3**, §2.3) |
| D8-F2 | todos os *bindings* `RENDERIZADO` necessários resolvem para **valor disponível** (**C-4**, **C-7**) |
| D8-F3 | toda `ASSERTIVA` aplicável é **verdadeira** (**C-5**, **C-5.1**) |

| # | Regra |
|---|---|
| D8-F4 | `AGUARDA_APROVACAO` **não habilita**. `BLOQUEADO` **não habilita** (doc 06 §11). |
| D8-F5 | Status **ausente ou inválido** é **Classe I**. |
| D8-F6 | **Nenhuma emissão parcial de fragmento.** Ou o fragmento é emitível **inteiro**, ou **não é emitível**. |

#### D8-L — regra de lacuna real

| # | Regra |
|---|---|
| D8-L1 | Fragmento não emitível **só produz causa conversacional** se a sua indisponibilidade deixar um **GRUPO INTEIRO descoberto**. |
| D8-L2 | Alternativa bloqueada **dentro de grupo já coberto** por outra alternativa segura **não cria lacuna**, **não cria `E09`** e **não força handoff**. |
| D8-L3 | Com **dois grupos complementares**, basta **um** deles estar descoberto para a consulta **não** estar totalmente coberta. |

#### D8-CI — Classe I: base NÃO AVALIÁVEL

Situação em que a base **não permite sequer avaliar** cobertura. Exemplos, sem esgotar:

| # | Exemplo |
|---|---|
| D8-CI1 | índice de **C ausente** |
| D8-CI2 | índice **estruturalmente inválido** |
| D8-CI3 | **mapa R2 inválido** |
| D8-CI4 | **referência pendurada** — o mapa aponta para fragmento inexistente (R2-7) |
| D8-CI5 | **caminho declarado inexistente** no YAML |
| D8-CI6 | **predicado não avaliável** |

Tratamento **obrigatório**:

| # | Regra |
|---|---|
| D8-CI7 | **bloquear antes da etapa 7** |
| D8-CI8 | a `MaquinaEstados` **não executa** |
| D8-CI9 | as condições **2** e **4** de §4.4 **não são avaliadas** — `None` |
| D8-CI10 | **zero `E09`** |
| D8-CI11 | **preservar o processamento** |
| D8-CI12 | **alerta operacional pelo caminho já existente** (§7, §7.2) — **nenhum gatilho de alerta novo é criado** |
| D8-CI13 | **não criar quinto caso de negócio**: os **quatro** casos de "sem transição" de doc 06 §4.5 e de §5 **continuam quatro**. Classe I é **falha de base**, tratada pelo caminho de falha já vigente de §7 |
| D8-CI14 | **não inventar pendência comercial**: Classe I **não** vira `E09`, **não** vira `pendencia_impeditiva` e **não** vira item de `pendencias_resposta` |

#### D8-CII — Classe II: base AVALIÁVEL e DIVERGENTE

Situação em que a base **é avaliável** e a avaliação **acusa divergência** — o exemplo
canônico é uma **`ASSERTIVA` avaliável cujo resultado é falso**.

| # | Regra |
|---|---|
| D8-CII1 | o **fragmento divergente nunca é emitido** (F4-B1) |
| D8-CII2 | o **erro de consistência** é **sempre registrado** (F4-B2) |
| D8-CII3 | o **dado divergente** é **sempre bloqueado** (F4-B1) |
| D8-CII4 | o **alerta** para correção humana é **sempre emitido** (F4-B3) |
| D8-CII5 | o **ciclo pode continuar** se houver **cobertura segura alternativa** no mesmo grupo (F4-B6, D8-L2) |

**A `ASSERTIVA` continua consistency-only.** Ela **não** é produtora de `E09`, de condição
de ciclo nem de handoff (**C-5i**–**C-5q**, **C-5.1**). Quem avalia **cobertura** é S2-D8,
**depois** de receber o **resultado estrutural** da conferência.

#### D8-P — `pendencias_resposta` e a clarificação de T11/T18

| # | Regra |
|---|---|
| D8-P1 | `pendencias_resposta` contém **PERGUNTAS DO INTERESSADO**, **nunca motivos técnicos** (doc 06 §1.3). |
| D8-P2 | A **decisão semântica é por assunto**; o **texto** é **somente conteúdo persistido**, nunca chave de decisão (D8-B2). |
| D8-P3 | Para **cada `PerguntaComercial` `ALTA`** cujo assunto ficou **não respondível** pelo eixo B, **registrar aquela pergunta** em `pendencias_resposta`. |
| D8-P4 | **Duplicatas são preservadas como conteúdo** quando existirem (N-b-Q11). |
| D8-P5 | Pergunta **`BAIXA` não entra** em `pendencias_resposta`. |
| D8-P6 | **Causa exclusiva do eixo A NÃO cria pergunta.** A evidência permanece em `Qualificacao.pendencias_impeditivas` e na estrutura de auditoria/resumo, que a leva ao resumo **pela sua representação própria**. |

Consequência documental, refletida em **doc 06 §3 (T11/T18)** e em **doc 06 §4.3 (P5)**:
registrar em `pendencias_resposta` as **perguntas não respondidas do ciclo** **quando
houver causa de resposta associada**. **Nenhuma `Txx` muda**, **nenhum estado muda**,
**nenhuma guarda muda** e **nenhum `AcaoMaquina` muda**.

#### D8-N — pré-condição de integração de `N-b-RES2`

**S2-D8 NÃO confirma `E06`.** Ela registra **apenas** a pré-condição de integração:

| # | Regra |
|---|---|
| D8-N1 | Um **futuro produtor de `E06`** não pode entregar à `MaquinaEstados` combinação **incoerente**, como `E06` confirmado **+** zero `PerguntaComercial` efetiva **+** `resposta_aprovada_disponivel = False` **+** ausência de `E09`, nos estados cuja resposta é **condicionada** (doc 06 §11: T10, T17, T28). |
| D8-N2 | Essa responsabilidade continua **integralmente em `N-b-RES2`**, que permanece **ABERTO**. **Nenhum identificador de pendência novo é criado.** |

#### D8-S — modo sem `Interpretacao`

**Não existe caminho operacional "sem `Interpretacao` → eixo A avaliado → condição 2
`False`".** A arquitetura vigente já determina o contrário:

| # | Regra |
|---|---|
| D8-S1 | **Sem `Interpretacao`** não há projeção, e a **etapa 5 não executa** (N-b-M1, N-b-M2, §6.3). Logo as etapas **6** e **7** também não são alcançadas no pipeline operacional, e **S2-D8 não é invocada nesse caminho**. |
| D8-S2 | A ausência de `Interpretacao` **encerra/bloqueia o caminho antes de S2-D8**, conforme **N-b** — que **não é reaberta** por esta arbitragem. |
| D8-S3 | Nesse caminho, as condições **2** e **4** permanecem **NÃO AVALIADAS / `None`** na fronteira operacional. |
| D8-S4 | Isso **não altera** a **independência semântica do eixo A** em relação a `PerguntaComercial` (D8-A1) **quando S2-D8 é legitimamente alcançada**. |

#### D8-T2 — condição 2, regra total operacional

Vale **quando S2-D8 é legitimamente alcançada**.

| # | Situação | `pendencia_impeditiva` |
|---|---|---|
| D8-T2a | **Classe I** | `None` — e **bloqueio antes da máquina** |
| D8-T2b | eixo A avaliado, **sem impeditiva** | `False` |
| D8-T2c | campo determinante **indisponível mas não relevante ao ciclo** (falha `IMP-2`) | `False` |
| D8-T2d | violação objetiva **já determinou `INCOMPATIVEL`** (falha `IMP-3`) | `False` |
| D8-T2e | **dados do interessado incompletos** (falha `IMP-4`) | `False` |
| D8-T2f | **`IMP-1`–`IMP-4` satisfeitas** | `True` — e `Qualificacao.resultado == INDEFINIDO` (D8-A6) |
| D8-T2g | **zero `PerguntaComercial`** | **não interfere** na condição 2 (D8-A1) |

#### D8-T4 — condição 4, regra total operacional

Vale **quando S2-D8 é legitimamente alcançada**.

| # | Situação | `resposta_aprovada_disponivel` |
|---|---|---|
| D8-T4a | **Classe I** | `None` — e **bloqueio** |
| D8-T4b | `Interpretacao` **válida sem pergunta efetiva** | `False` |
| D8-T4c | **ao menos um assunto integralmente coberto** | `True` |
| D8-T4d | **perguntas efetivas e nenhum assunto coberto** | `False` |
| D8-T4e | **um assunto coberto + outro descoberto** | `True` **+ `E09`** |
| D8-T4f | **`ASSUNTO_NAO_CLASSIFICADO` isolado** | `False` **+ `E09`** |

**Esta tabela não vale para o modo sem `Interpretacao`**, porque **S2-D8 não é alcançada**
nesse caminho (D8-S1).

#### D8-C — prova de preservação de C e de N-b

Continuam **verdadeiras e inalteradas**, sem atenuação:

| # | Preservado |
|---|---|
| D8-C1 | **F1**–**F6** (§2.2), inclusive **F4(a)**–**F4(d)** — refinada apenas a **consequência conversacional**, por **F4-B** |
| D8-C2 | **C-5**, **C-5.1**, **C-8**, **C-12a**–**C-12h** e **C-13** (§2.3) |
| D8-C3 | **C-12 permanece literal**: S2-D8 **não** a altera, **não** a amplia e **não** a reinterpreta |
| D8-C4 | a `ASSERTIVA` continua **consistency-only**: **não** é produtora de `E09`, de condição nem de handoff |
| D8-C5 | **`AssuntoComercial` continua com 54 valores** e **`K-Nb-1`–`K-Nb-51`** continuam a fronteira de cenários de N-b (§6.3) |
| D8-C6 | **`IntencaoConversacional` continua com 11 valores**, **`E-Nb-1`–`E-Nb-19`** continuam a lista de erros e a `ProjecaoInterpretacao` continua com **sete** campos |
| D8-C7 | os **20** códigos de `AcaoMaquina` (§4.5), os **12** `CriterioIdentidade` e os **oito** campos de `DecisaoIdentidade` (§7.1) permanecem |

#### D8-X — fora do escopo de S2-D8

Permanecem **abertas e inalteradas**: **`N-b-RES2`**; **S3-D1**; **E4**; **E1**; **E3**;
**B**; **C** (§2.3); **S2-D5**; **S2-D7**; **R10**, **R13**, **R17** e **R20** (**C-9**);
**`Q53`**/**`Q54`** (**AJ2-E4**); o **valor do limiar** e seu **mecanismo de carga**; o
**destino do alerta operacional**; **S4**/**S5**; e o **`OrquestradorMotor`**. S2-D8 **não
cria** o índice de C, **não cria** o mapa R2, **não cria** módulo, **não cria**
`AssuntoComercial` em Python, **não escolhe** produtor LLM e **não cria subetapa**.

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
ser um **mapeamento estático do contrato**, ainda não implementado.

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
| 7 | Executar a ordem determinística do doc 06 §4 — **primeira decisão determinística do ciclo** | dados + eventos + avaliação comercial feita **a montante** contra o YAML (`RegrasComerciais`, `Qualificador`) + **todas as condições estruturadas de §4.4** já determinadas — `insumo_qualificacao_atualizado`, classificação de `E09`, `resposta_aprovada_disponivel`, `interesse_confirmar_disponibilidade`, `calendario_integrado`, `identidade`, `motivos_handoff` e `motivo_encerramento`. A `MaquinaEstados` recebe tudo já estruturado e **não lê o YAML** (doc 06 I23) | eventos confirmados, violações, motivos, qualificação recalculada e o **estado intermediário** resultante da **primeira chamada da `MaquinaEstados`** — caminho percorrido (uma ou mais `Txx`, doc 06 §4.2), ainda sujeito ao fechamento da etapa 12 | `E07`, `E08`, `E09` e `E18` são **recebidos/confirmados a partir das saídas determinísticas a montante**, não fabricados aqui; violação da precedência (ex.: `E07` sobre incompatibilidade) é erro de programa, não caso de negócio → bloquear envio. A **classificação que fundamenta `E09`** pertence ao contrato **S2-D8** (§4.4.1); a **transformação dos sinais em eventos confirmados** deve respeitar **`N-b-RES2`** (doc 06 §11) |
| 8 | Consultar YAML e respostas aprovadas | perguntas detectadas | valores de campo e códigos `R` correspondentes | campo `null`/`pendente` e ausência de resposta aprovada **já foram confirmados como `E09` na etapa 7** (gatilhos 1–2 do doc 04, doc 06 §9): aqui a pendência é **consultada e registrada**, nunca criada tardiamente. Esta etapa **não produz condição consumida pela etapa 7** |
| 9 | Selecionar fatos permitidos — **conferindo cada `Rxx` comercial contra o YAML** (F3) | resultado de 7 e 8 | lista fechada de fatos, cada um com origem e conferência | divergência `Rxx` × YAML → o fato **não** entra na lista, registra-se erro de consistência da base e o dado divergente é bloqueado (F4); lista vazia com pergunta pendente → R03 + handoff. **Nenhum `E09` nasce nesta etapa** e **nenhuma condição de §4.4 é produzida aqui** |
| 10 | Gerar rascunho | fatos autorizados + tom + estado | texto candidato | LLM indisponível ou lento → usar o texto aprovado literal (§7) |
| 11 | Validar o rascunho | rascunho + fatos autorizados | aprovado ou bloqueado + motivo | qualquer valor, promessa ou termo fora da lista → bloqueio |
| 12 | Bloquear ou substituir — e **fechar o ciclo determinístico** | resultado de 11 | texto final seguro + fechamento com `E15` e `E12` **pós-efeito** | substituir pelo texto aprovado literal; se não houver, R03 + handoff. Nunca reenviar ao LLM mais de uma vez. `E15` e `E12` só são confirmados **depois do efeito real** (doc 06 §2.2) e reentram na `MaquinaEstados` na ordem `E15` → `E12` (doc 06 §4.2): **no máximo duas chamadas adicionais** — uma para `E15`, uma para `E12` |
| 13 | Persistir — **persistência operacional** (§7.3) | **estado final produzido pela última chamada determinística aplicável após o fechamento da etapa 12**: o resultado da **etapa 7** quando não houver `E15` nem `E12`; o resultado **pós-`E15`** quando só houver `E15`; o resultado **pós-`E12`** quando a cadeia completa existir | estado, dados, qualificação, pendências, motivos e chave de idempotência gravados — e o **`instante_ultima_transicao`** de §6.2 (N-a-T1–N-a-T8): gravado **sempre** com o **instante de referência do ciclo**, nunca com relógio vivo, e atualizado **somente** quando o caminho decidido no ciclo contém transição que **muda** o estado. **Fronteiras**: o **transporte e a validação da representação** do campo pertencem à persistência operacional (§6.2, M-T1–M-T6); a **decisão** de qual valor usar, com a **composição entre as 0–3 chamadas** do ciclo, pertence a M-DT1–M-DT7; e a **aplicação** dessa decisão com a **escrita** pelo contrato da persistência é a fronteira chamável de M-AE1–M-AE7. **Fora dessas fronteiras**, e pertencente ao **chamador desta etapa** coordenado pelo `OrquestradorMotor` (D1): a montagem completa do registro, a decisão de se ela executa, a escolha entre criar e gravar, a geração de `id_atendimento`, a idempotência e o tratamento operacional de falha | falha de persistência → **bloquear a emissão** da resposta que depende da nova transição; preservar a mensagem para reprocessamento idempotente; alerta operacional (§7.2) |
| 14 | Emitir resposta ou handoff | texto final + decisão **já gravada** | resposta ao interessado e/ou resumo para Douglas | **ordem de emissão obrigatória: 1. tentar a entrega do resumo; 2. somente após sucesso, emitir a mensagem de encaminhamento ao interessado** (doc 06 §10). Estado `atendimento_humano` → nada é emitido (I03); handoff não registrado → não afirmar que houve handoff (§7.2). **`deve responder = false` sempre que `situacao_takeover != SEM_TAKEOVER`** (R5, §6.5) |

Regras do pipeline:

- **a etapa 3 antecede a 4, e as duas antecedem a 5**: identidade só é resolvida com contexto
  persistido e interpretação disponíveis;
- **fronteira temporal da etapa 7**: todas as condições de §4.4 — em especial
  `resposta_aprovada_disponivel` — precisam estar **determinadas antes** da etapa 7, porque
  é ali que ocorre a primeira chamada da `MaquinaEstados`. As etapas 8 e 9 **consultam,
  conferem e selecionam** fatos e textos, mas **não produzem condição necessária a uma
  chamada que já aconteceu**;
- **ordem conceitual determinística anterior à etapa 7** (arbitragem S2-D8, §4.4.1). Ela é
  **conceitual**, **não é implementação** e **não cria etapa nova**: o pipeline continua com
  **catorze** etapas. Dentro da fronteira que antecede a primeira chamada da
  `MaquinaEstados`, a sequência é

  1. `RegrasComerciais`;
  2. `Qualificador` com `pendencias_impeditivas = ()` → **qualificação provisória**;
  3. **eixo A** de S2-D8;
  4. **eixo B** de S2-D8;
  5. **composição das causas** e `E09` (D8-E2–D8-E5);
  6. `Qualificador` com as `pendencias_impeditivas` **classificadas pelo eixo A** →
     **qualificação final**;
  7. **primeira chamada da `MaquinaEstados`** — a etapa 7.

  O `Qualificador` continua **função pura** e **S2-D8 não replica a precedência de
  qualificação** (D8-0d): `IMP-3` e `IMP-4` apenas **leem** o que a precedência já
  determinou;
- **Classe I bloqueia antes da etapa 7** (D8-CI7–D8-CI14): base não avaliável para
  cobertura — índice de C ausente ou inválido, mapa R2 inválido, referência pendurada,
  caminho declarado inexistente ou predicado não avaliável. A `MaquinaEstados` **não
  executa**, as condições **2** e **4** permanecem **`None`**, **zero `E09`** é produzido, o
  processamento é preservado e o alerta operacional segue **pelo caminho já existente**
  (§7). **Classe I não é um quinto caso** da lista de "sem transição" abaixo, que
  **continua com quatro**: é **falha de base**, não desfecho de ciclo;
- **sem `Interpretacao`, S2-D8 não é alcançada** (D8-S1–D8-S4). A etapa 5 não executa
  (N-b-M1, N-b-M2) e, por consequência, as etapas 6 e 7 também não; as condições **2** e
  **4** permanecem **não avaliadas / `None`** na fronteira operacional. **N-b não é
  reaberta**;
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

**N-a — política arbitrada.** A política de elegibilidade e recência produz o conjunto
elegível **E** dentro da **etapa 3**; o `ResolvedorIdentidade` **recebe E pronto** e **não
calcula elegibilidade nem recência**.

**N-a-F1 — fronteira parcial de N-a** (arbitragem R-I). Quando
`veredito_identificador == ENCONTRADO`, o conjunto elegível produzido pela etapa 3 **deve
conter o atendimento identificado exatamente uma vez**. **Nenhuma regra de elegibilidade ou
de recência pode removê-lo naquele ciclo**: um atendimento que a própria etapa 3 acabou de
encontrar e validar não pode desaparecer do escopo que ela entrega. A obrigação do produtor
é **N-I-2** (§6.1.1); a verificação correspondente na entrada da etapa 5 é **P-I5** (§7.1).
Coerentemente, `ENCONTRADO` implica **`havia_estado_esperado = true`** (**N-I-3**, **P-I4**)
— **sem implicação inversa**: `havia_estado_esperado = true` **não** implica `ENCONTRADO`.

**N-a-F1 permanece intacta e prevalece sobre N-a.** A elegibilidade dos **demais**
candidatos, a definição de recência, o marco temporal, o limiar, a composição do conjunto e a
ordem de entrega estão **fechados pela arbitragem N-a** (subseção seguinte). Continuam **abertos**: o **valor numérico** do limiar, a **consulta
concreta** à persistência, a **unicidade geral** de `id_atendimento` entre candidatos não
identificados e **E4** (§12).

#### N-a — política de produção do conjunto elegível da etapa 3 (arbitragem N-a)

**Natureza.** N-a é a **política determinística** que transforma os registros **já
recuperados** da persistência no **conjunto elegível E** entregue ao `ResolvedorIdentidade`.
É **política interna da etapa 3**, **não componente arquitetural independente**.

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

**Contrato do dado temporal.** O `RegistroAtendimento` **transporta** o marco temporal. As
regras abaixo definem **o valor** e **o momento** da escrita: **M-DT** decide o valor; **M-AE**
aplica e escreve; a **decisão de executar a etapa 13**, a **escolha entre criar e gravar** e a
**coordenação no pipeline** pertencem ao **`OrquestradorMotor`**.

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

**Projeção de mudança de estado — contrato e fronteira de runtime.** As regras **N-a-T4** e
**N-a-T5** exigem saber **se o caminho decidido no ciclo mudou o estado**, e proíbem derivar
isso de `estado_inicial != estado_final`. Esta subseção **arbitra a origem dessa informação**.
A projeção é **fronteira de runtime da `MaquinaEstados`**: o campo
`transicoes_que_mudaram_estado` é produzido **dentro** da máquina, no instante da aplicação de
cada `Txx`, e devolvido por `DecisaoMaquina`.

**Ficam fora desta fronteira**: a **composição entre as até três chamadas** do ciclo (regra 7)
e a **decisão** de qual valor de `instante_ultima_transicao` usar, que pertencem a
**M-DT1–M-DT7**; a **aplicação** e a **escrita** do marco, que pertencem a **M-AE1–M-AE7**; e
a **integração da etapa 13 ao pipeline**, que pertence ao **`OrquestradorMotor`**.

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

**Fronteira entre criação, atualização e persistência.** A projeção
`transicoes_que_mudaram_estado` é a **fronteira de runtime** definida pelas regras acima. A
**composição das decisões**, a **escolha do marco** e a sua **aplicação/escrita** são
distribuídas pelas fronteiras **M-DT** e **M-AE**. A **integração dessas fronteiras ao
pipeline** pertence ao **`OrquestradorMotor`**. Os três casos abaixo são distintos:

| # | Fronteira |
|---|---|
| 1 | **Criação de atendimento** — vale **N-a-T3**: `instante_ultima_transicao = instante_de_referencia_do_ciclo`. **Não existe transição anterior a detectar**, e a projeção da `MaquinaEstados` **não é pré-requisito** para inicializar o marco na criação. **Quem cria o atendimento não é atribuído por esta arbitragem.** |
| 2 | **Atualização de atendimento existente** — vale **N-a-T4/N-a-T5**, pela **regra 7** da tabela acima: se **ao menos uma** das decisões realmente produzidas no ciclo tiver a projeção **não vazia**, atualizar o marco com o `instante_de_referencia_do_ciclo`; se **todas** forem vazias, **preservar** o marco anterior. Uso **futuro** da **etapa 13** (§5). |
| 3 | **Transporte e persistência do marco** — continuam sendo o contrato já materializado em **M-T1–M-T6**. A persistência **não decide** quando o marco muda e **não consulta** esta projeção; quem decide e aplica é a fronteira de **M-DT1–M-DT7** e **M-AE1–M-AE7**, **sem alterar** `persistence.py`. |
| 4 | **N-a-T6** e **N-a-T7 permanecem íntegros**: ciclo sem mudança **não atualiza**; ciclo encerrado antes da `MaquinaEstados` **não atualiza por essa via**; e **múltiplas mudanças no mesmo ciclo continuam usando um único `instante_de_referencia_do_ciclo`**. A **cardinalidade da tupla não significa um timestamp por transição**. |

**Contrato de implementação M-T — transporte do marco temporal.** As regras abaixo são
**decisões técnicas da fronteira de persistência**, **não** decisões da arbitragem:
**`N-a-T8` vale integralmente** — a arbitragem **não escolhe** tipo Python, coluna, índice nem
serialização.

| # | Contrato de implementação M-T |
|---|---|
| M-T1 | `RegistroAtendimento` transporta `instante_ultima_transicao` com representação concreta **`datetime \| None`**, default **`None`**. |
| M-T2 | **`None` é válido no armazenamento.** A persistência não exige o marco; a exigência, quando um candidato `encerrado` precisa de recência, continua sendo **bloqueio da etapa 3** por **S9** — a validação estrutural da persistência **não substitui** a validação de integridade da etapa 3. |
| M-T3 | Valor **não-`None`** exige **fuso efetivo** — `tzinfo` presente **e** `utcoffset()` não `None` —, que é o que torna o marco comparável como instante absoluto (N-a-T8). Violação é **erro de contrato do chamador** na fronteira de escrita. |
| M-T4 | A persistência **transporta** o valor recebido: **não converte fuso**, não normaliza para UTC e não altera o instante. |
| M-T5 | **Zero relógio vivo** e **zero preenchimento automático**: a persistência **não cria** o marco e **não decide** quando ele muda. **Fora desta fronteira**: a **decisão** de qual valor usar e a **aplicação/escrita**, que pertencem a **M-DT1–M-DT7** e **M-AE1–M-AE7** e **não alteram** a persistência; e a **integração ao pipeline**, que pertence ao **`OrquestradorMotor`**. |
| M-T6 | **Nenhuma coluna, índice, serialização ou persistência não volátil é escolhida por esta fronteira.** A implementação volátil de referência é a de §7.4 (B2, M1–M3). |

**Contrato de implementação M-E — política N-a/E.** A **produção determinística do conjunto
elegível** é implementada como **função pura** por `src/casa77_sdr/eligibility.py`. Como
`M-T1`–`M-T6`, estas são **decisões de implementação**, **não** decisões da arbitragem;
**nenhuma regra normativa de N-a é alterada por elas**.

| # | Contrato de implementação M-E |
|---|---|
| M-E1 | **Não é componente arquitetural novo.** A tabela de §4.1 permanece com **14** componentes e a de §2 com **nove** responsabilidades (N-a-1, N-a-2). O módulo é **organização de código** para uma política **interna da etapa 3**. |
| M-E2 | A função recebe os **registros já recuperados** e devolve **somente E** — `tuple[CandidatoAtendimento, ...]`. Ela **não recupera, não persiste** e **não faz I/O** (N-a-4, N-a-5). |
| M-E3 | Materializa: validação do limiar (N-a-L1–L6), projeção (N-a-P1–P6), classificação dos oito estados (N-a-E1–E5), recência exclusiva de `encerrado` (N-a-R1–R6), **N-a-F1**, preservação de duplicatas não identificadas (N-a-D2) e ordem canônica (N-a-O1–O5). |
| M-E4 | **Zero relógio vivo**, zero YAML, zero LLM, zero rede e zero conversão de fuso. Dadas as mesmas entradas, produz sempre a mesma tupla, e **não muta** os registros recebidos. |
| M-E5 | As violações são **sinalizadas por exceção** — configuração temporal inválida (S10), marco temporal ausente (S9), contexto corrompido (S11) e identificado incoerente (N-I-2/P-I5). O **tratamento operacional do bloqueio** fica **fora desta fronteira** e pertence ao `OrquestradorMotor`: preservar a mensagem e emitir alerta conforme **S4**/**S5**. |
| M-E6 | **Ficam fora desta fronteira**: a **decisão**, a **aplicação** e a **escrita** do marco de **N-a-T3–N-a-T7**, que pertencem a **M-DT1–M-DT7** e **M-AE1–M-AE7**; o **valor numérico do limiar**; o **mecanismo de carga** da configuração; e o **`OrquestradorMotor`**. O **conjunto H**, `havia_estado_esperado`, a projeção **N-I** e a **montagem das projeções de identidade da etapa 3** pertencem a **M-C1–M-C8**. |

**Contrato de implementação M-C — montagem das projeções de identidade da etapa 3.** A
**produção das projeções que a etapa 3 entrega à etapa 5** é implementada por
`src/casa77_sdr/context.py`. Esta fronteira é o *wiring* da **fronteira etapa 3 →
identidade/etapa 5**, **não** a etapa 3 inteira. Como `M-T1`–`M-T6` e `M-E1`–`M-E6`, estas são
**decisões de implementação**, **não** decisões da arbitragem; **nenhuma regra normativa de
§6.1.1, §6.2, N-a, H1–H6, N-I ou P-I é alterada por elas**.

| # | Contrato de implementação M-C |
|---|---|
| M-C1 | **Não é componente arquitetural novo.** A tabela de §4.1 permanece com **14** componentes e a de §2 com **nove** responsabilidades (N-a-1, N-a-2). O módulo é o ***wiring* da fronteira etapa 3 → identidade/etapa 5** — **não** a etapa 3 inteira —, que continua **coordenada pelo `OrquestradorMotor`** (D1). |
| M-C2 | A montagem usa a **persistência operacional somente para leitura** — `recuperar_por_id` e `consultar_por_contato`. Ela **não cria**, **não grava**, **não marca chave de idempotência** e **não preserva pendente** (N6, S3). |
| M-C3 | Executa a **precedência conceitual dos 14 passos** desta seção **no que toca a essa fronteira**. Em particular: o **limiar é validado antes de qualquer método da persistência** (N-a-L4, N-a-L5, S10); a ordem é **recuperar por ID → consultar contato → validar o identificador** — o bloqueio de **N5** **não** é antecipado para antes da consulta do contato; e o **passo 12 precede o passo 13** — as correspondências são verificadas sobre **E ainda não canonicalizado**, e a ordem canônica é aplicada **só depois**. |
| M-C4 | **E continua delegado** à política N-a de `eligibility.py` (M-E1–M-E6): classificação, recência, **N-a-F1** e ordem canônica **não são reimplementadas**. A política expõe a **seleção de E** (passos 9/10) e a **canonicalização** (passo 13) como operações distintas e reutilizáveis, além da validação do limiar e da projeção integral dos registros; a API que produz E já canonicalizado permanece como conveniência equivalente à composição das duas. Cada regra continua existindo em **um único lugar**. |
| M-C5 | **H permanece fora de N-a** (H1, H2): é construído por **filtro estrutural de estado** sobre a projeção **integral** do contexto recuperado, **antes e à parte** da filtragem N-a, e transporta **somente IDs opacos** (H3). |
| M-C6 | **`M-C6` produz `havia_estado_esperado` e a projeção `id_atendimento_validado` (N-I-1) conforme as regras abaixo.** `havia_estado_esperado` é calculado sobre o **contexto recuperado**, **nunca sobre E**; o ID validado é projetado **somente** sob `ENCONTRADO`, e é `None` sob `NAO_INFORMADO`. As correspondências **H4/H5** e **N-I-1–N-I-3** são verificadas no **passo 12**, antes da entrega. |
| M-C7 | As violações são **sinalizadas por exceção**: identificador não resolvido (**N5**, **N6**, **S3** — transporta **apenas o veredito fechado**, sem identificador, canal, contato, mensagem ou PII), conjunto **H** incoerente (**H4**, **H5**) e projeção do identificador incoerente (**N-I-4**). O **tratamento operacional do bloqueio** fica **fora desta fronteira** e pertence ao `OrquestradorMotor`: preservar a mensagem e emitir alerta conforme **S4**/**S5**. |
| M-C8 | **Ficam fora desta fronteira**: a **decisão**, a **aplicação** e a **escrita** do marco de **N-a-T3–N-a-T7**, que pertencem a **M-DT1–M-DT7** e **M-AE1–M-AE7**; **N-b**; **E4**; **S2-D8**; **S3-D1**; o **tratamento operacional dos bloqueios** (S4, S5); o **destino do alerta operacional**; o **valor numérico do limiar**; o **mecanismo concreto de carga** da configuração; a **persistência não volátil**; e o **`OrquestradorMotor`**. A montagem **não chama** o `ResolvedorIdentidade`, **não chama** a `MaquinaEstados`, **não qualifica**, **não interpreta mensagem** e **não decide resposta**: a **coordenação integral da etapa 3** pertence ao **`OrquestradorMotor`** (D1). |

**Materialização da decisão do marco temporal.** A
**decisão determinística** exigida por **N-a-T3–N-a-T7** — *qual valor de
`instante_ultima_transicao` usar neste ciclo* — é implementada como **função pura** por
`src/casa77_sdr/transition_marker.py`. Como M-T1–M-T6, M-E1–M-E6 e M-C1–M-C8, estas são
**decisões de implementação**, **não** regras novas: **nenhuma regra normativa de
N-a-T1–N-a-T8 é alterada por elas**.

**A distinção é normativa e não pode ser colapsada:** **M-DT decide**; **M-AE aplica e
escreve** (**M-AE1–M-AE7**); a **decisão de executar a etapa 13** e a **coordenação dessas
fronteiras** pertencem ao **`OrquestradorMotor`**.

| # | Contrato de implementação M-DT |
|---|---|
| M-DT1 | **Não é componente arquitetural novo.** A tabela de §4.1 permanece com **14** componentes e a de §2 com **nove** responsabilidades. O módulo é organização de código para uma **decisão pura**. |
| M-DT2 | A função recebe **quatro argumentos nomeados e obrigatórios** — se o ciclo cria atendimento, o `instante_de_referencia_do_ciclo`, o marco atual e as decisões efetivamente produzidas — e devolve **somente** `datetime \| None`. **Não recebe persistência**, não monta `RegistroAtendimento` e **não decide se a etapa 13 executa**. |
| M-DT3 | Materializa a decisão de **N-a-T3** (criação → instante do ciclo, **sem** exigir a projeção da máquina), de **N-a-T4/N-a-T5/N-a-T7** (atendimento existente com **ao menos uma** decisão de projeção não vazia → instante do ciclo, **inclusive** quando o estado final iguala o inicial) e de **N-a-T6** (nenhuma mudança → **preserva** o marco atual, inclusive `None`). |
| M-DT4 | **Composição das até três chamadas** conforme a regra 7: a decisão observa **exclusivamente** `transicoes_que_mudaram_estado` de cada `DecisaoMaquina`. **Zero** *replay*, **zero** concatenação de caminhos, **zero** acesso à estrutura interna de regras da máquina, **zero** comparação entre estado inicial e final e **zero** classificação estática de T35. Nenhum outro campo de `DecisaoMaquina` é lido. Mais de três decisões é erro de contrato. |
| M-DT5 | **Zero relógio vivo** e **zero aritmética temporal**: o valor devolvido é sempre **o mesmo objeto** recebido — o instante do ciclo ou o marco atual —, sem conversão de fuso, `astimezone` ou substituição de `tzinfo` (N-a-T2). A validação de **fuso efetivo** **não é duplicada**: continua nas fronteiras já existentes (`recebida_em` na normalização e M-T3 na persistência). |
| M-DT6 | **Zero persistência, zero I/O, zero rede, zero YAML e zero LLM.** O módulo **não importa** `persistence`, `context`, `eligibility` nem `identity`, e **não é exportado** na superfície pública do pacote. |
| M-DT7 | **Este módulo decide, não aplica nem escreve.** A **aplicação** sobre `RegistroAtendimento` e a **escrita** via `criar`/`gravar` pertencem a **M-AE1–M-AE7**. A **decisão de executar a etapa 13**, a **criação operacional** do atendimento, a **escolha entre criar e gravar** e a **coordenação no pipeline** pertencem ao **`OrquestradorMotor`**. A **persistência não volátil** fica **fora desta fronteira**. |

**Contrato de implementação M-AE — aplicação e escrita do marco.** A **aplicação** da
decisão sobre um `RegistroAtendimento` e a **escrita** pelo contrato da persistência são
implementadas como **fronteira chamável** por `src/casa77_sdr/transition_marker_write.py`.
Como as anteriores, são **decisões de implementação**, **não** regras novas: **nenhuma regra
normativa de N-a-T1–N-a-T8, nem as regras 1–8 da projeção, é alterada por elas**.

| # | Contrato de implementação M-AE |
|---|---|
| M-AE1 | **Não é componente arquitetural novo.** A tabela de §4.1 permanece com **14** componentes e a de §2 com **nove** responsabilidades. O módulo é organização de código para uma fronteira mínima. |
| M-AE2 | Existem **duas funções explícitas** — uma que **cria** e outra que **grava**. A distinção **criar × gravar** é **recebida pronta** pela função escolhida: a fronteira **não deriva** a operação de nada, e **não decide** qual delas o pipeline deve usar. |
| M-AE3 | A decisão do marco é **integralmente delegada** a `decidir_instante_ultima_transicao(...)` (M-DT1–M-DT7). O módulo **não lê** `transicoes_que_mudaram_estado`, **não lê** `caminho` nem qualquer outro campo de `DecisaoMaquina`, **não compara** estado inicial com final e **não faz *replay***. A regra de decisão **não é duplicada**. |
| M-AE4 | Recebe o `RegistroAtendimento` **pronto** e altera **exclusivamente** `instante_ultima_transicao`, por `dataclasses.replace`. **Não monta** estado, dados, qualificação, pendências, motivos nem identificador, **não muta** o registro recebido e devolve **exatamente** o registro submetido à persistência. |
| M-AE5 | `PersistenciaOperacional.criar`/`gravar` é a **fronteira de escrita**, e `persistence.py` concentra a **validação da representação do marco** (M-T3). |
| M-AE6 | **Exceções propagam intactas** — `FalhaDePersistencia`, `ValueError` de identificador já existente ou inexistente, de vínculo canal × contato divergente e de marco sem fuso efetivo, além dos erros da própria decisão. **Zero `try`/`except`**: preservar a mensagem, emitir alerta e decidir o que o motor faz com a falha (S4, S5, Q2/Q4/Q5/Q8) e o **destino do alerta** permanecem **fora**. |
| M-AE7 | **Fora desta fronteira**, e pertencentes ao **chamador da etapa 13** coordenado pelo **`OrquestradorMotor`** (D1): a **montagem completa** do registro; a **decisão de se a etapa 13 executa**; a **escolha entre criar e gravar**; a **geração de `id_atendimento`**; a **criação operacional** do atendimento; a **marcação de idempotência**; a **preservação de pendente**; e o **tratamento operacional de falha**. Esta fronteira **decide e escreve o marco**, e **nada além disso**. |

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

**Cenários de conformidade K-Na.** Os casos abaixo especificam **resultados normativos** da
política N-a:

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
| N-b-RES2 | A **transformação posterior** dos sinais interpretados em **eventos confirmados** **não possui produtor concreto**. Isso é **residual explícito de integração**. |
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

**AJ1 define a representação e a canonicalização determinística de `Interpretacao`.** Ela
**não reabre N-b**, **não cria componente** e **não altera** os vocabulários e fronteiras que
declara preservar: **§4.1 permanece com 14 componentes** e §2 com **nove** responsabilidades;
`IntencaoConversacional` permanece com **exatamente 11** valores; a lista de erros de contrato
permanece com **exatamente 19** códigos `E-Nb`; e a fronteira de cenários de §8.2 é
**`K-Nb-1`–`K-Nb-51`**, estendida por **AJ2**, que prevalece sobre AJ1 nessa fronteira.
Nenhuma intenção nova, nenhum erro novo, nenhum cenário novo **por AJ1**, e **nenhuma
exceção pública nova**. **AJ1 não cria subetapa.**

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

**Fronteira de AJ1.** AJ1 fecha **exclusivamente** a **representação e a canonicalização
determinística** de N-b.

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

**Contrato de implementação M-NB — fronteira determinística de N-b.** A **parte
determinística** do contrato N-b/AJ1 é implementada por `src/casa77_sdr/interpretation.py`,
com os cenários correspondentes em `tests/test_interpretation.py`. Este contrato **não reabre
a arbitragem, não altera o contrato, não cria componente, não cria pendência, não altera
nenhum código `E-Nb` ou cenário `K-Nb` e não cria subetapa.** §4.1 permanece com **14**
componentes e §2 com **nove** responsabilidades.

| # | Contrato de implementação M-NB |
|---|---|
| M-NB1 | **Superfície pública fechada**, com **três** produtores: `canonicalizar_interpretacao(...)` — valida a entrada recebida e devolve a `Interpretacao` **canônica** ou um erro de contrato; `projetar_para_identidade(...)` — deriva a `ProjecaoInterpretacao`; e `decidir_interesse_confirmar_disponibilidade(...)` — produz a **condição 5**. Nenhum outro produtor público existe, e **nada é exportado em `__init__.py`**. |
| M-NB2 | **`A1` não é entrada semântica** (AJ1-1): a estrutura de entrada **não possui slot de códigos `A1`**. A **presença** dos seis códigos é derivada do payload autoritativo (N-b-X2, N-b-X4) e a **confiança** é **calculada** por **N-b-X3**, sendo apenas **armazenada** na `Interpretacao` canônica para auditabilidade (AJ1-A1b, AJ1-A1c). |
| M-NB3 | A entrada da fronteira é uma representação **pré-canônica mínima** que carrega **somente** o que o produtor não determinístico entrega (AJ1-2) mais o **slot autônomo** fechado nos cinco códigos **A2/B** (AJ1-3). Ela **não é uma segunda `Interpretacao`** e **nenhum formato de transporte é escolhido** (N-b-F3). |
| M-NB4 | **Erros recebíveis** tratados pela fronteira: `E-Nb-1`, `E-Nb-2`, `E-Nb-3`, `E-Nb-4`, `E-Nb-5`, `E-Nb-6` **no ramo de intenção autônoma**, `E-Nb-7`, `E-Nb-8`, `E-Nb-9`, `E-Nb-10`, `E-Nb-17` e `E-Nb-18`. A **precedência AJ1** vale: código `A1` no slot autônomo **com** confiança declarada → **`E-Nb-3`**; **sem** confiança → **`E-Nb-5`**. A **superfície pública não adiciona exceção**, e as duas famílias são **distintas**: **tipo runtime incompatível** levanta **`TypeError`**, sem código; **violação de contrato `E-Nb`** levanta **`ValueError`** com o respectivo código no início da mensagem. Assim, **ausência** de confiança onde ela é exigida é `E-Nb-1` — e `confianca_global` ausente é `E-Nb-4` —, enquanto uma confiança de **tipo errado** é `TypeError`. `E-Nb-6` significa **somente código repetido**: a **ordem canônica** de `intencoes_detectadas` é **produzida** deterministicamente, mas **não é exigida** de quem consome, porque ela existe apenas para auditabilidade e não estabelece precedência semântica (AJ1-A1e). |
| M-NB5 | **Invariantes internos** — `E-Nb-6` no ramo `A1` e `E-Nb-11`–`E-Nb-16` — são verificados como **pós-condições** da canonicalização e provados como **propriedade**, não por entrada externa fabricada. **`K-Nb-18` é estrutural**: para toda `Interpretacao` canônica, a confiança `A1` **corresponde a N-b-X3** (AJ1-13a, AJ1-13b). **Nenhuma confiança `A1` independente é aceita** (AJ1-13c). |
| M-NB6 | **Projeção total** para a `ProjecaoInterpretacao`, que tem **sete** campos (N-b-K1–N-b-K8). A derivação **não aplica C3** — transporta valor e confiança inclusive `BAIXA`. **Nenhuma PII e nenhum texto conversacional atravessam**: `convidados`, `formato`, `nome`, `contato`, `correcoes`, `perguntas_comerciais`, `pedido_de_humano`, `trechos_ambiguos` e `confianca_global` ficam retidos no runtime da `Interpretacao`. |
| M-NB7 | **Condição 5 é produzida** como **função total** (N-b-CD1–N-b-CD4), inclusive `None` **sem `Interpretacao`**. O seu produtor conceitual é atribuído por N-b. É a **única** condição de §4.4 produzida por esta fronteira; as condições **2** e **4** têm produtor conceitual em **S2-D8** e a **8** permanece sem produtor atribuído (**`S3-D1`**). |
| M-NB8 | **`FormatoEvento` é reutilizado por import** de `src/casa77_sdr/qualification.py` e **não é redeclarado**; **nenhum** `shared/domain/types` é criado (AJ1-F1, AJ1-F2). O módulo é **puro e determinístico**: zero I/O, rede, relógio, persistência, YAML, LLM, fornecedor, SDK, API, cache ou fila; não muta as entradas. **`E-Nb-19` é provado estruturalmente** — superfície pública, tipos de retorno, campos das estruturas, produtores públicos e condição 5 como única condição —, com o fechamento de imports como **evidência complementar**. |
| M-NB9 | **Fora desta fronteira.** O **produtor não determinístico / LLM da etapa 4** pertence ao **limite único de LLM** de §4.2 e §9 — adaptador, fornecedor, modelo, SDK, API, JSON Schema, *prompt* e interpretação de texto livre **não vivem aqui**. A transformação dos sinais interpretados em **eventos confirmados** pertence a **`N-b-RES2`**, que permanece **ABERTO**; a etapa 4 é **proibida de emitir `Exx`** (`N-b-RES1`), com `N-b-RES3` preservado. A **integração operacional** da etapa 4 pertence ao **`OrquestradorMotor`** (D1). **Nenhuma subetapa é criada.** |

#### AJ2 — origem semântica do assunto de `PerguntaComercial` (arbitragem AJ2)

**AJ2 estende formalmente N-b.** O contrato da etapa 4 passa a incluir a **origem semântica
do assunto** de `PerguntaComercial`, conforme as regras abaixo, segundo a precedência
**`C-P`**.

**§4.1 permanece com 14 componentes** e §2 com **nove** responsabilidades.
`IntencaoConversacional` permanece com **exatamente 11** valores, a lista de erros permanece
**`E-Nb-1`–`E-Nb-19`** e a `ProjecaoInterpretacao` permanece com **sete** campos. **AJ2 não
cria subetapa.**

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
| AJ2-C3 | **AJ2 não altera C**, que permanece **ARBITRADA** e cujo contrato é §2.3. |
| AJ2-C4 | **S2-D8 decidirá futuramente** qualquer mapeamento `assunto` → `Rxx` ou `assunto` → fragmento. |

**Precedência sobre `C-14f`.** Na **fronteira de cenários**, **AJ2 prevalece**: ela é
**`K-Nb-1`–`K-Nb-51`** (**`C-P`**). As **11** `IntencaoConversacional` e os erros
**`E-Nb-1`–`E-Nb-19`** preservados por `C-14f` **continuam os mesmos**.

**S2-D8 é ARBITRADA.** AJ2 **não arbitra** `assunto` → `Rxx`, `assunto` → fragmento,
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

**Fora do escopo de AJ2.** AJ2 **não decide** **S2-D8**, **S3-D1**, **E4**, **B**, **C**,
**`N-b-RES2`**, o `DetectorHandoff`, o `SeletorFatos`, o `ValidadorResposta`, o
`ValidadorConsistenciaBase`, o **limiar**, **S4**/**S5** nem o **destino do alerta**. A
**coordenação dessas fronteiras** pertence aos contratos correspondentes. `R10`, `R13`, `R17`
e `R20` permanecem **não decididos** (C-9), e `Q53`/`Q54` permanecem **não classificados**
(AJ2-E4). **AJ2 não cria subetapa.**

##### Contrato de implementação M-AJ2 — delta AJ2 na fronteira determinística

O **delta AJ2** é implementado na **fronteira determinística** por
`src/casa77_sdr/interpretation.py`, com os cenários correspondentes em
`tests/test_interpretation.py`. Este contrato **não reabre AJ2, não altera o contrato, não cria
componente, não cria pendência, não cria código `E-Nb` novo, não cria cenário `K-Nb` novo e não
cria subetapa.** §4.1 permanece com **14** componentes e §2 com **nove** responsabilidades.

| # | Contrato de implementação M-AJ2 |
|---|---|
| M-AJ2-1 | **`AssuntoComercial` é** vocabulário fechado de **exatamente 54** valores — **53 específicos + `ASSUNTO_NAO_CLASSIFICADO`** —, na **ordem documental** de §6.3, **sem alias** e **sem 55º membro**. Ele pertence ao `__all__` **do módulo** e fica **fora do `__init__.py` do pacote**: **M-NB1 é preservado** — nada da fronteira é exportado pelo pacote. |
| M-AJ2-2 | **`PerguntaComercial` tem três campos** — `texto`, `confianca` e `assunto` —, nesta ordem. O `assunto` é `AssuntoComercial \| None`, **sem valor padrão** — coerente com os dois campos já existentes —, **sem confiança própria** e **sem campo auxiliar**: nenhum `id`, posição, *offset*, ocorrência, contador, `Rxx` ou fragmento existe nela (N-b-Q7, N-b-Q11). `assunto = None` representa **ausência recebida**, para que **AJ2-X1** seja verificável na fronteira. |
| M-AJ2-3 | **`E-Nb-5` cobre** `assunto` ausente e fora do vocabulário: `assunto` **ausente** → `E-Nb-5` (**AJ2-X1**, `K-Nb-43`); `assunto` **fora do vocabulário** → `E-Nb-5` (**AJ2-X2**, `K-Nb-42`); `ASSUNTO_NAO_CLASSIFICADO` → **válido** (**AJ2-N1**, `K-Nb-45`). **Tipo runtime incompatível** é `TypeError` **sem código**, pela política de **M-NB4** (`K-Nb-44`). **A lista permanece `E-Nb-1`–`E-Nb-19`** — **nenhum vigésimo código** — e a **superfície pública não adiciona exceção**. |
| M-AJ2-4 | **Precedência de validação.** A validação de `assunto` é executada **depois** de todas as validações e pós-condições **N-b/AJ1** preexistentes. Quando uma entrada viola simultaneamente uma regra antiga e a regra AJ2, **a antiga prevalece**: `E-Nb-10` para texto ausente/vazio/em branco, `E-Nb-2` para confiança sem valor, `E-Nb-1` para valor sem confiança, `E-Nb-4` para `confianca_global` ausente, `E-Nb-8`/`E-Nb-18` nas suas hipóteses e `TypeError` para texto ou confiança de tipo incompatível. **A sequência de validação anterior permanece intacta.** |
| M-AJ2-5 | **Os dois caminhos rejeitam contrato inválido**, por **uma única** função privada compartilhada — **sem superfície pública nova**: a canonicalização da entrada recebida e a **validação de canonicidade** já exigida dos consumidores públicos. Uma `Interpretacao` construída diretamente com `assunto` inválido **não atravessa** e **nenhuma projeção ou condição é derivada** dela. **Fail-closed**: erro de contrato **bloqueia na fronteira**. |
| M-AJ2-6 | **Fronteira preservada.** A `ProjecaoInterpretacao` continua com **sete** campos e o `assunto` **não atravessa** para ela (N-b-Q12, N-b-K8); `IntencaoConversacional` continua com **11** valores; a **condição 5** continua a **única** condição de §4.4 produzida por esta fronteira; as condições **2** e **4** possuem **produtor conceitual** atribuído por **S2-D8** (§4.4.1, eixos **A** e **B**) e **ficam fora desta fronteira**; a condição **8** permanece **NÃO ATRIBUÍDA** (**S3-D1**); e o `assunto` **não participa de N-b-X3**: a agregação de `PERGUNTA_COMERCIAL` continua dependendo **somente** das confianças. O `assunto` **não referencia `Rxx`**, **não seleciona fragmento** e **não produz `Exx`**. |
| M-AJ2-7 | **Cenários `K-Nb-41`–`K-Nb-51` cobertos** por testes, mais **provas estruturais**: contagem e ordem documental dos **54** valores, os **três** campos de `PerguntaComercial`, ausência do assunto na projeção, ausência de vigésimo `E-Nb`, ausência de exceção pública nova, presença no `__all__` do módulo, ausência no `__init__.py` do pacote e não participação em **N-b-X3**. **`K-Nb-1`–`K-Nb-40` não mudam de semântica**: exigem **apenas** que o terceiro campo seja fornecido. |
| M-AJ2-8 | **Preservação textual e duplicatas.** O `texto` continua **literal** — sem `strip`, normalização, resumo ou paráfrase (N-b-Q9) — e **duplicatas exatas continuam permitidas** (N-b-Q11). **Exatamente um assunto por item** (N-b-Q8) — regra **exigida e validada** aqui. **N-b-Q8 é preservado integralmente**, e a **segmentação semântica pertence ao produtor não determinístico**: a consulta composta chega **já segmentada** em múltiplas `PerguntaComercial`, uma por assunto. A fronteira determinística **recebe, valida e preserva** itens **já segmentados** e **não interpreta nem divide texto livre**. |
| M-AJ2-9 | **Fora desta fronteira.** O **produtor não determinístico / LLM da etapa 4** pertence ao **limite único de LLM** de §4.2 e §9 — nenhum fornecedor, modelo, SDK, API, JSON Schema, *prompt* ou interpretação de texto livre vive aqui. `N-b-RES2` permanece **ABERTO** e a etapa 4 é **proibida de emitir `Exx`** (`N-b-RES1`, `N-b-RES3`). O **consumo** do `assunto` pertence a **S2-D8** (§4.4.1) e o mapeamento `assunto` → `Rxx` ou → fragmento pertence ao contrato **C** (§2.3): **nenhum dos dois é decidido aqui**. A **integração operacional** pertence ao **`OrquestradorMotor`** (D1). |

##### Compatibilidade S2-D8 × N-b

Estas notas ficam **fora de AJ2** e **fora de N-b**: nenhuma regra desta §6.3 é alterada e
**N-b não é reaberta**.

| # | Nota |
|---|---|
| D8-Nb1 | **`N-b-Q12` permanece literal.** O `assunto` **não atravessa** para a `ProjecaoInterpretacao`, **não referencia `Rxx`** e **não produz condição** de §4.4. S2-D8 consome o `assunto` **fora da fronteira da etapa 4**, já na fronteira anterior à etapa 7 (§4.4.1, D8-B2) — consumir **depois** não é produzir **dentro**. |
| D8-Nb2 | **`N-b-Q2`/`N-b-Q3` continuam o filtro único de efetividade.** O eixo B de S2-D8 consome **somente** `PerguntaComercial` `ALTA`; a `BAIXA` permanece **preservada para diagnóstico** e **não entra** em consumo estruturado. |
| D8-Nb3 | **`ASSUNTO_NAO_CLASSIFICADO` continua valor legítimo** (AJ2-N1–AJ2-N5) e **não é erro**. O que S2-D8 arbitra é apenas o seu **tratamento a jusante**: **zero grupos de cobertura** (R2-6) e, por consequência, causa `SEM_RESPOSTA_APROVADA_EMITIVEL`. **AJ2-C4 é cumprida aqui**, e nada em AJ2 é reescrito. |
| D8-Nb4 | **Modo degradado — `N-b-M1`–`N-b-M8` permanecem integralmente.** Sem `Interpretacao` não existe projeção, a **etapa 5 não executa** e, por consequência, **S2-D8 não é invocada**: as condições **2** e **4** permanecem **não avaliadas / `None`** na fronteira operacional (§4.4.1, D8-S1–D8-S3). **Nenhum gatilho de alerta novo** é criado (N-b-M3). |
| D8-Nb5 | **`N-b-RES2` continua ABERTO.** S2-D8 **não confirma `E06`** e **não cria produtor de evento**: apenas registra a pré-condição de coerência de integração (§4.4.1, D8-N1, D8-N2). **Nenhum identificador de pendência novo é criado.** |
| D8-Nb6 | **Fronteira preservada**: `IntencaoConversacional` continua com **11** valores, `AssuntoComercial` com **54**, a lista de erros com **`E-Nb-1`–`E-Nb-19`**, os cenários com **`K-Nb-1`–`K-Nb-51`**, a `ProjecaoInterpretacao` com **sete** campos, §4.1 com **14** componentes e §2 com **nove** responsabilidades. |

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

**Contrato conceitual.** Seja **`H`** o conjunto dos atendimentos recuperados para o
contato/canal cujo estado é **`atendimento_humano`**. **Origem formal** (arbitragem R-H): H é produzido pela
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

Nenhuma ferramenta de observabilidade está escolhida.

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
| **Divergência entre `Rxx` e YAML** | O YAML prevalece (F5). A resposta não é selecionada, o dado divergente é bloqueado, registra-se erro de consistência da base e emite-se alerta operacional — **sempre**, sem exceção (**F4-B1**–**F4-B4**, §2.2). **Ao interessado, o desfecho depende da cobertura** (**F4-B5**/**F4-B6**, §2.2; **D8-CII**, §4.4.1): **R03 + handoff** quando a divergência deixa a consulta **sem cobertura segura**; **resposta segura aprovada** quando uma alternativa **aprovada e íntegra do mesmo grupo de cobertura** cobre **integralmente** a consulta — nesse caso **zero `E09` fabricado** e **zero handoff causado por essa divergência**. **Sem conciliação, e nunca arbitragem pelo LLM.** |
| **Base não avaliável para cobertura — Classe I** (arbitragem S2-D8, §4.4.1) | Índice de C ausente ou estruturalmente inválido, mapa de cobertura **R2** inválido, **referência pendurada**, **caminho declarado inexistente** ou **predicado não avaliável**: **bloquear antes da etapa 7**; a `MaquinaEstados` **não executa**; as condições **2** e **4** de §4.4 permanecem **não avaliadas / `None`**; **zero `E09`**; **preservar o processamento**; **alerta operacional pelo caminho já existente** — **nenhum gatilho de alerta novo é criado**. **Não é um quinto caso de negócio**: os quatro casos de "sem transição" de §5 e do doc 06 §4.5 **continuam quatro**, e **nenhuma pendência comercial é inventada** (D8-CI7–D8-CI14) |
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
| `MaquinaEstados` | as **41 transições** do doc 06 §3; a **ordem de avaliação** das famílias C0–C11 (§4.2), com o **caminho percorrido** auditável e **estado final único**; a **projeção `transicoes_que_mudaram_estado`** (§6.2) — subsequência ordenada de `caminho`, classificada contra o estado intermediário do instante da aplicação; o **fechamento** `E15` → `E12` pós-efeito, o teto de **três chamadas por ciclo** e a ausência de loop; os efeitos paralelos P1–P6 (§4.3) e as inércias N1–N4 (§4.4); evento não coberto por transição, efeito paralelo ou inércia é **erro de contrato** (§4.5); a máquina **não lê o YAML** e **não fabrica eventos** |
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
**0 são substituídos**. A **parametrização em pytest não faz parte deste contrato**.

**Classificação e alcance de `K-Nb-18`, `K-Nb-34` e `K-Nb-39`** (micro-arbitragem **AJ1**,
§6.3). AJ1 esclarece **como cada cenário se prova**, não **o que ele afirma**: nenhum cenário
é acrescentado, removido, renumerado ou reescrito **por AJ1**. Os cenários
`K-Nb-41`–`K-Nb-51` vêm de **AJ2**.

| Cenário | Classificação AJ1 | Alcance da prova |
|---|---|---|
| `K-Nb-18` | **estrutural** da canonicalização — `E-Nb-13` é **invariante / program error** (AJ1-13a) | Provado por **pós-condição / propriedade**: para **toda** `Interpretacao` canônica, a **confiança A1 == resultado de N-b-X3** (AJ1-13b). **Não se exige** prova por exceção levantada a partir de entrada externa: nenhuma confiança **A1** independente é aceita do produtor (AJ1-13c) |
| `K-Nb-34` | **recebível / runtime** — permanece exatamente como está | Cobre **dois** casos, ambos resolvidos em **`E-Nb-3`**: (a) **confiança declarada em `trecho_ambiguo`** (N-b-T5); e (b) **tentativa de apresentar código A1 com confiança no slot de intenções autônomas** (AJ1, caso A). **Nenhuma precedência de `E-Nb-13` sobre `E-Nb-3`** é criada, e **nenhum código novo** — de erro ou de cenário — é introduzido |
| `K-Nb-39` | **parte determinística / responsabilidade de orquestração** | **Parte determinística** — invariantes da fronteira da etapa 4: **sem `Interpretacao`**, `interesse_confirmar_disponibilidade = None` (N-b-CD4); **ausência de `Interpretacao` ≠ `Interpretacao` válida sem sinais** (N-b-G8); e a `ProjecaoInterpretacao` **exige `Interpretacao` canônica válida** (N-b-M2). **Responsabilidade do `OrquestradorMotor`**: a etapa 5 **não executar**; a `MaquinaEstados` **não ser chamada**; **nada ser gravado**; os **alertas**; e a **coordenação do modo degradado** (N-b-M3, N-b-M8) |

Consequência de método: **não** se deve afirmar cobertura dessas propriedades de `K-Nb-39` a
partir de um teste isolado da fronteira da etapa 4. Elas pertencem à **coordenação do
`OrquestradorMotor`** e **não são provadas por teste isolado** daquela fronteira (§12, itens
10, 11, 15 e 18).

**Cenários conceituais de S2-D8 — família própria `D8-K*`** (arbitragem S2-D8, §4.4.1).
**Namespace próprio**: os cenários de N-b **continuam `K-Nb-1`–`K-Nb-51`** e **nenhum deles
é alterado, renumerado ou substituído**. A **parametrização em pytest não faz parte deste
contrato**: os `D8-K*` são **requisitos conceituais de cenário**.

Convenções desta família: "coberto" significa **respondível** por **R2-5**; "descoberto"
significa **grupo sem alternativa emitível agora** (**D8-F1**–**D8-F6**); e toda leitura de
famílias e transições respeita o runtime real do doc 06 §4.2 — **C5 antes de C6, C6 antes
de C9, C9 antes de C10** —, com a regra de que **uma transição só se aplica quando o seu
estado de origem coincide com o estado INTERMEDIÁRIO vigente** no instante da avaliação.

| # | Cenário | Resultado esperado |
|---|---|---|
| D8-K1 | **Zero `PerguntaComercial`** no ciclo, base íntegra e nenhum campo determinante indisponível | condição **4** = `False` (D8-T4b); condição **2** = `False` (D8-T2b); **zero `E09`**; **nada** em `pendencias_resposta` |
| D8-K2 | Uma `PerguntaComercial` **`ALTA`** cujo assunto tem **todos os grupos cobertos** | condição **4** = `True` (D8-T4c); **zero `E09`**; **nada** em `pendencias_resposta` |
| D8-K3 | **Única pergunta `BAIXA`** | **não entra** no eixo B (D8-B1); **nenhuma pergunta efetiva** → condição **4** = `False` (D8-T4b); **zero `E09`** por causa dela; **nada** em `pendencias_resposta` (D8-P5) |
| D8-K4 | Assunto consultado com **zero grupos** no mapa | **não respondível** (R2-5); `E09` com motivo `SEM_RESPOSTA_APROVADA_EMITIVEL`; a **pergunta** entra em `pendencias_resposta` (D8-P3) |
| D8-K5 | **`ASSUNTO_NAO_CLASSIFICADO` isolado**, confiança `ALTA` | **zero grupos por definição** (R2-6) → condição **4** = `False` **+ `E09`** (D8-T4f), motivo `SEM_RESPOSTA_APROVADA_EMITIVEL`; a pergunta entra em `pendencias_resposta`. **Não é `E-Nb-5`** e **não é erro** (AJ2-N1–AJ2-N5) |
| D8-K6 | ***Binding* `RENDERIZADO` necessário resolve para `null`**, deixando o **único grupo** do assunto descoberto | fragmento **não emitível** (D8-F2); causa `CAMPO_INDISPONIVEL`, carregando **caminho YAML** **e** assunto; `E09`; condição **4** = `False` se esse for o único assunto consultado |
| D8-K7 | ***Binding* necessário** aponta para estrutura cujo **`status` é `pendente`** | **mesmo tratamento** de D8-K6: `CAMPO_INDISPONIVEL` (D8-F2, C-7) |
| D8-K8 | Campo da base **indisponível**, **não relacionado** a nenhum assunto consultado e **não determinante** da qualificação neste ciclo | **nenhuma causa**; condição **2** = `False` por falha de **IMP-2** (D8-T2c); condição **4** **inalterada**; **zero `E09`** |
| D8-K9 | **Múltiplas perguntas `ALTA`**, todos os assuntos cobertos | condição **4** = `True`; **zero `E09`**; **nada** em `pendencias_resposta` |
| D8-K10 | Assunto com **dois grupos complementares**, **ambos cobertos** | **respondível** (R2-4, R2-5): a **conjunção entre grupos** está satisfeita |
| D8-K11 | Assunto com **dois grupos complementares**, **um descoberto** | **não respondível** (D8-L3): a consulta **não está totalmente coberta**; `E09` com `SEM_RESPOSTA_APROVADA_EMITIVEL` |
| D8-K12 | Grupo com **duas alternativas**: uma **bloqueada**, outra **segura** | **grupo coberto** pela disjunção (R2-4): **zero lacuna**, **zero `E09`**, **zero handoff** (D8-L2) |
| D8-K13 | **Classe I** — índice de C **ausente** | **bloqueio antes da etapa 7**; a `MaquinaEstados` **não executa**; condições **2** e **4** = `None`; **zero `E09`**; processamento preservado; **alerta pelo caminho já existente** (D8-CI7–D8-CI14) |
| D8-K14 | **Classe I** — **referência pendurada**: o mapa **R2** aponta para fragmento inexistente | **idêntico a D8-K13** (R2-7) |
| D8-K15 | **Classe I** — fragmento com **status ausente ou inválido** | **idêntico a D8-K13** (D8-F5) |
| D8-K16 | **Classe II com alternativa segura** — `ASSERTIVA` avaliável **falsa** em uma alternativa; **outra alternativa aprovada e íntegra do mesmo grupo** cobre integralmente a consulta | fragmento divergente **bloqueado**, erro de consistência **registrado**, alerta **emitido** (F4-B1–F4-B3); a **resposta segura aprovada prossegue**; **zero `E09` fabricado** e **zero handoff** causado por essa divergência (F4-B6, D8-CII5) |
| D8-K17 | **Classe II sem alternativa segura** — a `ASSERTIVA` falsa deixa o **grupo descoberto** | bloqueio, registro e alerta **iguais** a D8-K16; ao interessado, **R03 + handoff** (F4-B5); `E09` com `SEM_RESPOSTA_APROVADA_EMITIVEL` |
| D8-K18 | **`E09` único com múltiplas causas** — um assunto com *binding* `null` e outro com **zero grupos** | **um único `E09`** no ciclo (D8-E3), com o conjunto de motivos **`CAMPO_INDISPONIVEL` + `SEM_RESPOSTA_APROVADA_EMITIVEL`**, **deduplicado e canonicalizado** (D8-E4, D8-E5) |
| D8-K19 | **Causa exclusiva do eixo A** — campo determinante indisponível com **IMP-1–IMP-4 satisfeitas**, **zero `PerguntaComercial`** no ciclo | condição **2** = `True` (D8-T2f); `Qualificacao.resultado == INDEFINIDO` (D8-A6); `E09` **impeditivo** com `CAMPO_INDISPONIVEL`; **nenhuma pergunta é inventada** em `pendencias_resposta` (D8-P6) — a evidência fica em `Qualificacao.pendencias_impeditivas` e segue ao resumo pela representação própria |
| D8-K20 | **Causa A + pergunta respondível** no mesmo ciclo | condição **2** = `True` e condição **4** = `True`; **um único `E09`**, **impeditivo**; a pergunta **respondida** **não** entra em `pendencias_resposta` |
| D8-K21 | **Causa B + dados do interessado incompletos** | **IMP-4 falha** → condição **2** = `False` (D8-T2e) e `Qualificacao.resultado == DADOS_INCOMPLETOS`; `E09` **acessório**; a pergunta **não respondida** entra em `pendencias_resposta` |
| D8-K22 | Tentativa de compor **`E09` impeditivo** com `DADOS_INCOMPLETOS` ou com `INCOMPATIVEL` | **caminho inexistente por construção**: **IMP-4** e **IMP-3** o excluem (D8-A7). Se aparecer, é **erro de integração**, nunca caso de negócio |
| D8-K23 | **A8-a** — `E08` de classe **handoff documentado** + `E09` **acessório** em `coletando_dados` | **C5** aplica **T05** → `pronto_para_handoff`; **C10 não consome `E09`**, porque a origem de **T12** (`coletando_dados`) já não coincide com o estado intermediário; **`E09` sobrevive por P5** |
| D8-K24 | **A8-b** — `E08` de classe **informa e aguarda** + `E09` **acessório** em `coletando_dados` | **C5** aplica **T06**, que **preserva o estado**; **C10** aplica **T12** → `pronto_para_handoff` e **consome `E09`**; **P5 não se aplica** |
| D8-K25 | **A3** — `E09` **impeditivo** + `E06` **respondível** em `coletando_dados` | **C6** aplica **T11** (com T11/T18 conforme a redação de doc 06 §3) → `pronto_para_handoff`; **C9 não consome `E06`**, porque a origem de **T10** já não coincide com o estado intermediário; **`E06` sobrevive por P3** |
| D8-K26 | **A3** em `respondendo_duvidas` | **C6** aplica **T18** → `pronto_para_handoff`; **C9 não consome `E06`** (origem de **T17** não coincide); **`E06` sobrevive por P3** |
| D8-K27 | `E08` de classe **handoff documentado** + `E09` **acessório** em `respondendo_duvidas` | **C5** aplica **T22** → `pronto_para_handoff`; **C10 não consome `E09`** (origem de **T19** não coincide); **`E09` sobrevive por P5** |
| D8-K28 | **`E06` incoerente** — `E06` confirmado **+** zero `PerguntaComercial` efetiva **+** `resposta_aprovada_disponivel = False` **+** ausência de `E09`, em estado de **resposta condicionada** | **combinação incoerente**: **bloqueio de integração**. **S2-D8 não confirma `E06`** e **não corrige** a incoerência; a responsabilidade é integralmente de **`N-b-RES2`**, que **continua ABERTO** (D8-N1, D8-N2) |
| D8-K29 | **Modo sem `Interpretacao`** | **S2-D8 NÃO é alcançada** (D8-S1): a etapa 5 não executa, as etapas 6 e 7 também não, as condições **2** e **4** permanecem **não avaliadas / `None`**, **nada é gravado** (N-b-M5) e **nenhum alerta novo** é criado (N-b-M3). **Este cenário não usa as tabelas D8-T2 e D8-T4** |
| D8-K30 | **Q1** — requisito **estrutural** do carregador ausente, `null` ou de tipo inválido | **o motor não inicia** (§7). **Não é pendência de S2-D8**, **não é `E09`**, **não é `pendencia_impeditiva`** e **não é caso de ciclo** (Q1-a, Q1-b). **`Q2` não é autorizada** (Q1-e) |

**Alcance da prova.** Estes cenários são **conceituais**. A sua automatização depende das
respectivas fronteiras de **R2**, **C**, **S2-D8** e do **`OrquestradorMotor`**. Os cenários
**D8-K23**–**D8-K27** **reutilizam o contrato da `MaquinaEstados`** e **não exigem alteração
desse contrato**.

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
pode duplicar essa lógica comercial. Essa precedência é **regra de arquitetura**; a
arbitragem **S1** não é reaberta.

O que os passos 1 a 3 entregam, com precisão:

| Afirmação correta | Afirmação incorreta |
|---|---|
| Os componentes e o pipeline funcionam **ponta a ponta em testes**, com persistência simulada em memória (B2). | "O produto funciona ponta a ponta." |
| O **modo literal** permite validar todo o fluxo **sem LLM**. | "O bot está pronto, falta só o LLM." |
| A **operação real** depende de três coisas que a 3B não entrega: persistência operacional confiável (M3), canal de entrega do handoff (etapa 5) e adaptador de canal (etapa 7). | "Falta só publicar." |
| A Etapa 3B entrega **núcleo testável**, não bot publicado. | "Etapa 3B = bot funcionando." |

O modo literal permanece disponível para sempre, como fallback de indisponibilidade (§7).

Fornecedor e modelo não estão escolhidos. O adaptador de `src/llm/` deve isolar
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

**Estrutura conceitual sugerida.** Esta seção define organização arquitetural e **não afirma estado físico de diretórios**.

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
(`mensagem de entrada → decisão de saída`), sem servidor no MVP. O **adaptador de canal**
pertence à **etapa 7** e **chama** o motor; o motor **nunca chama o adaptador** (**D6**).

---

## 11. Limites arquiteturais

Os itens abaixo permanecem **escolhas ou dependências arquiteturais ainda abertas**. Nenhuma
escolha futura é automática.

| Limite | Onde se decide |
|---|---|
| biblioteca de schema | decisão técnica futura quando necessária (§3) |
| framework web e adaptador HTTP | etapa 7 (§3, §10) |
| rota de WhatsApp — oficial × não oficial — e adaptador de canal | etapa 7 (§12, item 1) |
| integração de calendário | etapa 6 |
| armazenamento **não volátil** — banco, arquivo ou equivalente | decisão específica e explícita antes de qualquer uso real (§7.4; §12, item 2a) |
| hospedagem | etapa futura |
| provedor de IA e modelo | §9 — isolados atrás do limite único de `src/llm/` |
| ferramenta de observabilidade e política de retenção de log | §6.6; etapa 10 (§12, item 9) |

O ponto de entrada do motor permanece uma **única chamada** ao `OrquestradorMotor` (§10): o
adaptador **chama** o motor, nunca o contrário (**D6**).

---

## 12. Riscos e pendências

| # | Risco / pendência | Impacto | Onde se resolve |
|---|---|---|---|
| 1 | Rota de WhatsApp indefinida (oficial × não oficial) | pode exigir adaptador em outra linguagem | etapa 7 |
| 2 | Persistência **operacional** — contrato e implementação volátil em memória | O contrato é `PersistenciaOperacional` e a implementação volátil é `PersistenciaEmMemoria` (`src/casa77_sdr/persistence.py`). **A implementação volátil não sustenta operação real** (M2, M3): ela não sobrevive ao processo. **ARBITRADA** | **resolvido** — §7.3, §7.4. A persistência **não volátil** é o item 2a |
| 2a | Persistência **operacional não volátil** — armazenamento mínimo para uso real | sem ela, nenhuma resposta pode ser emitida em canal real (M3). Nenhuma tecnologia escolhida | **decisão específica e explícita antes de qualquer uso real** — não é decisão da 3B nem da etapa 8 |
| 2b | **Registro comercial de leads** — destino definitivo, histórico, relatórios, exportação | não bloqueia a 3B; não pode ser usado como justificativa para emitir sem gravar estado (§7.3) | etapa 8 |
| 3 | Critério técnico de "mesmo evento × nova solicitação" (T36/T37) | **ARBITRADO** (arbitragem R3): cascata determinística **D0–D6**, comparação exclusivamente nominal e vocabulário fechado de 12 critérios (§7.1; doc 06 §3). **Não bloqueia** o `ResolvedorIdentidade` | **resolvido** — §7.1 |
| 3a | Destino do alerta operacional não definido | S5, Q5 e F4 exigem um canal separado da conversa; o **destino operacional ainda não está especificado**. **ABERTA** | etapa 5 / etapa 8 |
| 3b | Janela temporal da chave composta de idempotência (§4.3) | curta demais duplica resposta; longa demais engole repetição humana legítima | Etapa 3B, com medição |
| 3c | Divergência `Rxx` × YAML depende de mapear cada `Rxx` ao campo que ele cita | mapeamento incompleto deixa divergência passar sem detecção. O **contrato** desse mapeamento é **C** (§2.3, item 19) | Etapa 3B, sobre o contrato de §2.3 |
| 4 | `R01` e `R15` ainda em **AGUARDA APROVAÇÃO** | saudação e encerramento sem texto aprovado | Douglas Bianchi |
| 5 | Canal de entrega do resumo e SLA indefinidos; **confirmação física de entrega do resumo** | etapa 14 do pipeline fica sem destino. `encaminhado_humano` afirma handoff **registrado**, nunca recebimento confirmado (doc 06 §10) — a confirmação física permanece futura | etapa 5 |
| 6 | Comportamento fora do horário de atendimento indefinido | resposta fora de horário não especificada | Douglas Bianchi |
| 7 | Precisão do validador de resposta | validador fraco deixa passar valor inventado; forte demais bloqueia texto correto | Etapa 3B, com os casos de `tests/perguntas-criticas.md` |
| 8 | Custo por conversa não medido | sem parâmetro de custo do LLM | etapa 9 |
| 9 | Política de retenção de log não definida (L7) | dado pessoal guardado sem prazo | antes da produção, etapa 10 |
| 10 | **S2-D8** — contrato de detecção e classificação de pendências: detectar campo `null`/`pendente` relevante e ausência de resposta aprovada, classificar impeditiva × acessória, fornecer os identificadores técnicos ao `Qualificador`, confirmar `E09` e fornecer a condição estruturada `resposta_aprovada_disponivel` | **ARBITRADA** (§4.4.1; doc 06 §11). Contrato fechado: **dois eixos** (**A**, de qualificação, e **B**, de resposta); **Q1** como decisão do MVP; regra impeditiva **IMP-1**–**IMP-4** com o invariante `pendencia_impeditiva == True` ⇒ `INDEFINIDO`; **ordem conceitual determinística** anterior à etapa 7 (§5); mapa **R2** de **grupos de cobertura**; **fragmento emitível** e **regra de lacuna real**; **Classe I** × **Classe II**; **exatamente dois** motivos de `E09` — `CAMPO_INDISPONIVEL` e `SEM_RESPOSTA_APROVADA_EMITIVEL`; semântica de `pendencias_resposta`; e a reconciliação **F4-B** de §2.2. As condições **2** e **4** de §4.4 têm **produtor conceitual** — os eixos **A** e **B**; a **condição 8** permanece **NÃO ATRIBUÍDA** (**S3-D1**). A `MaquinaEstados` **não depende** dela: recebe `E09` pronto | **contrato resolvido** — §4.4.1. O **artefato físico** — módulo e mapa **R2** — é requisito do `OrquestradorMotor`, depois de **AJ2** e de **C** (doc 06 §11) |

| 11 | **N-a** — política de **elegibilidade e recência** que produz o conjunto elegível da etapa 3 | **ARBITRADA** (§6.2): classificação **fechada dos oito estados**; recência aplicável **exclusivamente** a `encerrado`; `instante_ultima_transicao` como **único** marco temporal do MVP — **quando inicializado ou atualizado, recebe o `instante_de_referencia_do_ciclo` daquele ciclo**, **nunca** o relógio vivo; atualização decidida pelo **caminho de transições**; limiar como **configuração operacional validada explicitamente**; projeção do registro em `CandidatoAtendimento`; composição de E; duplicatas; **ordem canônica** só para auditabilidade; e a precedência conceitual da etapa 3 — com **N-a-F1**, **N-I**, **P-I**, **R5-P0**, **H1–H6** e **D0–D6** preservados | **contrato resolvido** — §6.2. As fronteiras de implementação são **M-T**, **M-E**, **M-C**, **M-DT** e **M-AE**; a **coordenação delas no pipeline** pertence ao `OrquestradorMotor`. O **limiar** é o item 18; **E4** é o item 15 |

| 12 | **N-b** — contrato global da **interpretação** da etapa 4: quem produz a projeção estruturada de §6.3 e com que garantias | **ARBITRADA** (§6.3): contrato da **`Interpretacao`** fechado — as **oito** categorias de §6.3; **`IntencaoConversacional`** com **exatamente 11** códigos na partição **A1 (6 derivados) / A2 (2 autônomos) / B (3 autônomos)**; consistência cruzada **N-b-X1–N-b-X6**; regras de confiança **N-b-G6/G6b/G6c**; lista fechada de erros **E-Nb-1–E-Nb-19**; modo degradado **N-b-M1–N-b-M8**; fronteira do produtor **N-b-F1–N-b-F5**; e cenários **K-Nb-1–K-Nb-51** (§8.2), fronteira estendida por **AJ2** (item 20). **Produtor atribuído**: o produtor de interpretação da etapa 4 é **fronteira funcional** do limite único de LLM (§4.2, §9), **não componente novo** — §4.1 permanece com **14** componentes. **AJ1** (§6.3, §8.2) fecha a **representação e a canonicalização determinística** de N-b. **Residual de contrato**: a etapa 4 **não emite `Exx`**, e a transformação dos sinais interpretados em **eventos confirmados** permanece **sem produtor atribuído** — **`N-b-RES2` ABERTO** (**N-b-RES1**–**N-b-RES3**) | **contrato resolvido** — §6.3. A **fronteira determinística** é **M-NB1–M-NB9** e **M-AJ2-1–M-AJ2-9**; o **produtor não determinístico / LLM** pertence a §4.2 e §9, e a **integração da etapa 4** ao `OrquestradorMotor`. **`N-b-RES2`** exige arbitragem própria |

| 13 | **E1** — distinção entre as entidades **conversa × atendimento × lead** | o contrato do motor trata **atendimento** como unidade única; a fronteira entre as três entidades **não está arbitrada**. Atravessa identidade, persistência e registro de leads. **NÃO ARBITRADA** | modelo de dados |
| 14 | **E3** — **evento novo declarado durante atendimento ativo** | o contrato vigente é **conservador**: `AMBIGUA` / `AMBIGUIDADE_DIVERGENCIA_EM_ATENDIMENTO_ATIVO` (**D3**, §7.1). Se cabe abrir atendimento paralelo **não está arbitrado**, e **nenhuma transição** existe para isso. **ABERTA** | arbitragem específica |
| 15 | **E4** — tratamento de **`SEM_CANDIDATO_ELEGIVEL`** pelo `OrquestradorMotor` | o resultado é auditável, mas **o que o orquestrador faz com ele não está arbitrado**. Enquanto aberta, o contrato manda **encerrar o ciclo sem transição** e **não autoriza avanço de integração** (doc 06 §4.5, G7). **ABERTA** | arbitragem específica, antes do `OrquestradorMotor` |
| 16 | **Retorno do controle ao bot** | **nenhuma transição inversa de T31** está especificada para devolver o canal ao atendimento automático sem passar por `E14`/T34. A partir de `atendimento_humano`, a saída especificada é o encerramento (T34); a partir de `encaminhado_humano`, T32. **ABERTA** | arbitragem futura — **não bloqueia** R5 |
| 17 | **Duplicatas gerais de `id_atendimento` entre candidatos não identificados** | a arbitragem R-I exige unicidade **apenas do ID identificado** e **apenas** com `veredito_identificador == ENCONTRADO` (**P-I5**). **Não está decidido** se IDs duplicados entre candidatos **não identificados** constituem erro geral de contrato. **Nenhuma regra global de unicidade foi adicionada** | arbitragem específica futura — **não bloqueia** nenhuma entrega já autorizada |
| 18 | **Valor numérico do limiar temporal de recência** e **mecanismo concreto de carga** da configuração (§6.2, N-a-L6) | o limiar é **argumento explícito e validado** das fronteiras que o consomem (N-a-L1–N-a-L6, M-E3, M-C3). **Nenhum número é definido** e **nenhuma tecnologia, variável de ambiente, arquivo ou serviço é escolhido**. Risco de calibração: curto demais descarta `encerrado` que **T36** deveria reabrir; longo demais devolve histórico antigo à cascata. **Não é dado comercial** — não entra em `knowledge/casa77.yaml`. **ABERTA** | aprovação específica de Douglas Bianchi + decisão operacional, **antes do `OrquestradorMotor`** |
| 19 | **C** — contrato estruturado, legível por máquina, ligando cada `Rxx` aos campos de `knowledge/casa77.yaml`, e o artefato que o materializa | **ARBITRADA** (§2.3). Contrato fechado: artefato aprovado `knowledge/indice-respostas-aprovadas.yaml`, modelo `Rxx` → **fragmentos emitíveis**, status fechado `APROVADO`/`AGUARDA_APROVACAO`/`BLOQUEADO` sem valor padrão, *bindings* **`RENDERIZADO`** e **`ASSERTIVA`** (`EH_VERDADEIRO`/`EH_FALSO`), regra **consistency-only** para `ASSERTIVA` sobre campo relacionado a handoff, formatos de **apresentação pura** sem dependência oculta, bloqueio de **transformação semântica**, tratamento de `null`/`pendente`, fontes autoritativas em transição e a separação **C × S2-D8**. As camadas são lidas por **`C-P`**: **`C-1`–`C-15`**, depois **`C-A1`**–**`C-A5`**. Os conflitos `R10`, `R20`, `R13` e `R17` permanecem **registrados e não arbitrados** (**C-9**) | **contrato resolvido** — §2.3. O **artefato físico** — o índice, os *templates* e a bijeção auditada — é **requisito** de `ValidadorConsistenciaBase` e, em cascata, de `SeletorFatos` e `ValidadorResposta` |

| 20 | **AJ2** — **origem semântica do assunto** de `PerguntaComercial`: de onde vem, e com que garantias, a informação de **sobre o que** o interessado consultou | **ARBITRADA** (§6.3). **AJ2 estende formalmente N-b**: `PerguntaComercial` tem **três** campos — `texto`, `confianca` e **`assunto`** obrigatório, do enum fechado **`AssuntoComercial`** de **54** valores (53 específicos + `ASSUNTO_NAO_CLASSIFICADO`), **sem confiança própria**; **um assunto por item**, com **segmentação** de consulta composta; **preservação textual** sem normalizar, resumir ou parafrasear; **duplicatas permitidas**; e o `assunto` **não atravessa** para a projeção, **não referencia `Rxx`** e **não produz condição** de §4.4 (**N-b-Q7**–**N-b-Q12**). `E-Nb-5` cobre `assunto` ausente ou fora do vocabulário, e a lista permanece **`E-Nb-1`–`E-Nb-19`**. Cenários: **`K-Nb-1`–`K-Nb-51`**. **`Q53`/`Q54` permanecem não classificados** | **contrato resolvido** — §6.3. Fronteiras relacionadas: **N-b** (item 12), de que AJ2 é extensão, e **S2-D8** (item 10), a quem pertence o **consumo** do assunto |
| 21 | **B** — **colisão de nome `RegistroAtendimento`**: componente de comportamento de §4.1 × dataclass `frozen` de transporte da persistência operacional | **ABERTA** (§4.1.1). Colisão de **categoria**, não de campo nem de assinatura. **Nenhum referente é renomeado ou unificado**, e nada é resolvido silenciosamente. **Não afeta** a persistência operacional de §7.3 nem a fronteira de identidade de §7.1 | arbitragem específica **antes de implementar** o componente `RegistroAtendimento` de §4.1 — §4.1.1 |


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

**Grafo de dependências.** O **`OrquestradorMotor`** depende de **S2-D8** (item 10), de
**E4** (item 15), do **produtor não determinístico de `Interpretacao`** de **N-b** (item 12),
da **configuração do limiar** de **N-a** (item 18), do **tratamento operacional dos bloqueios**
(S4, S5) e do **destino do alerta** (item 3a). A **`MaquinaEstados` não depende** de nenhuma
dessas pendências para o seu contrato já definido: ela recebe eventos confirmados e condições
já estruturadas. **E1** (item 13), **E3** (item 14), **B** (item 21), **S2-D5** e **S2-D7**
(doc 06 §12) são fronteiras abertas que **não condicionam** a especificação já arbitrada; as
demais mantêm as dependências indicadas na própria tabela.

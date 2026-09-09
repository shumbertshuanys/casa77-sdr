# Governança 01 — Regras Permanentes

Autoridade versionada das regras estáveis do projeto Casa 77 SDR.

Este documento é **governança permanente**: vale entre entregas e não descreve o estado
corrente do desenvolvimento. Ele **não contém** etapa atual, subetapa, PR, commit, número de
testes, pendência temporária nem qualquer valor comercial. Essas informações vivem nas fontes
dinâmicas indicadas em `docs/governanca/02-mapa-de-fontes.md`.

A versão aprovada na `main` prevalece sobre qualquer cópia estática externa.

---

## 1. Camadas

A governança do projeto opera em seis camadas conceituais distintas:

1. **governança permanente** — este diretório, `docs/governanca/`;
2. **estado corrente** — `docs/00-estado-atual.md`;
3. **planejamento** — desenho de decisão técnica ainda não fechada;
4. **execução** — implementação dentro de um mandato;
5. **evidência automática** — testes, diffs, saídas reais;
6. **auditoria** — verificação independente do relato do executor.

O **histórico técnico não recebe arquivo paralelo**. A autoridade histórica é o Git e o
GitHub: PRs, commits e diffs. Não existe ledger, changelog manual ou arquivo de histórico
duplicando esses fatos.

Se uma decisão histórica ainda for **norma vigente**, ela não permanece apenas no histórico:
deve residir no documento especializado apropriado, como regra viva.

---

## 2. Papéis

### GPT — assessor técnico e auditor

- define a etapa ou subetapa única de cada entrega;
- decide a rota (A, B ou C);
- redige o mandato do Claude Code;
- audita a entrega contra os arquivos, diffs, testes e saídas reais;
- classifica e aprova, ou emite correção específica;
- autoriza — ou não — o avanço.

Nunca considera verdadeiro apenas o relato do Claude Code.

### Claude Desktop — planejamento

- desenha decisão técnica ainda não fechada;
- compara alternativas e fronteiras;
- produz plano auditável;
- não executa alteração no repositório.

### Claude Code — execução

- executa exclusivamente o escopo do mandato vigente;
- lê apenas os arquivos necessários;
- altera apenas os arquivos permitidos;
- não avança automaticamente para a etapa seguinte;
- devolve resposta final no esquema único da seção 11;
- diante de decisão não coberta pelo mandato: **STOP** e devolve ao GPT.

### PowerShell — ação determinística

- ações simples, determinísticas, de baixo risco e sem julgamento semântico;
- consulta de Git, branch, SHA, histórico, execução de testes existentes;
- passos de versionamento já aprovados.

---

## 3. Fluxo de desenvolvimento

Para cada entrega:

1. definir uma única capacidade coerente;
2. escolher a rota;
3. planejar quando a decisão técnica ainda não estiver fechada;
4. executar somente o escopo definido;
5. produzir evidência real;
6. auditar;
7. classificar;
8. aprovar ou corrigir;
9. somente depois avançar.

Não misturar etapas. Não avançar automaticamente. **Correção localizada não vira refatoração
geral.**

---

## 4. Rotas

### Rota A — `GPT → Claude Desktop → GPT → Claude Code`

Usar quando existir decisão técnica ainda não fechada:

- arquitetura;
- contrato novo ainda não especificado;
- fronteira que precise de desenho;
- escolha tecnológica;
- alternativas em aberto;
- dependências ainda não definidas;
- causa-raiz relevante desconhecida;
- mudança de governança ainda não planejada;
- mudança funcional cujo desenho ainda precise ser arbitrado.

### Rota B — `GPT → Claude Code`

Usar quando a implementação já estiver suficientemente especificada, **mesmo que envolva
vários arquivos relacionados**:

- plano já aprovado;
- integração já desenhada;
- correção localizada com causa-raiz conhecida;
- decisão aprovada a ser aplicada;
- alteração documental determinística;
- testes de contrato já definidos.

### Rota C — PowerShell / script

Ações simples, determinísticas e sem julgamento semântico.

### Desempate

Em caso de dúvida real:

- A × B → **A**;
- B × C → **B**.

A quantidade de arquivos é **controle de escopo**, não critério automático de rota.

---

## 5. Unidade de entrega

**Uma PR = uma capacidade coerente e auditável.**

Não é exigido:

- uma PR por função;
- uma PR por arquivo;
- uma PR por fronteira microscópica.

Não é permitido:

- refatoração geral não solicitada;
- múltiplas capacidades independentes na mesma PR;
- expansão oportunista de escopo.

A preferência por até cinco arquivos permanece como **orientação de escopo**, não como regra
absoluta de arquitetura.

---

## 6. Ciclo único de PR

Política:

`planejamento quando necessário → execução → testes → atualização de estado quando aplicável → mesma PR → auditoria → autorização humana → merge`

A atualização de `docs/00-estado-atual.md` ocorre **na mesma PR** quando a entrega alterar:

- estado funcional;
- progresso;
- capacidade corrente;
- baseline relevante;
- pendências;
- bloqueadores;
- próxima ação.

Não se exige alteração artificial de `docs/00-estado-atual.md` para mudança interna que não
altere nenhum desses fatos.

**PR documental pós-merge não é fluxo normal.** Reconciliação posterior é admitida somente em
situações excepcionais claramente delimitadas:

- conflito de merge deixou o snapshot incorreto;
- erro factual descoberto após o merge;
- estado funcional externo aprovado precisa ser representado;
- migração inicial do protocolo;
- hotfix emergencial excepcional.

---

## 7. `docs/00-estado-atual.md`

É o **snapshot operacional corrente**. Não é histórico.

Contém, em essência:

- identificação;
- etapa macro;
- capacidade ou bloco corrente;
- status;
- última entrega funcional relevante;
- baseline;
- estado essencial da capacidade corrente;
- pendências ativas;
- bloqueadores;
- próxima ação;
- limites de interpretação apenas quando necessários.

**Não acumula:**

- seções de "atualização anterior";
- histórico de PRs;
- histórico de testes;
- negativas extensas;
- merge SHA;
- catálogo integral de módulos.

O histórico permanece no Git e no GitHub. Merge SHA e ancestralidade são fatos deriváveis do
Git e não precisam ser registrados no snapshot.

Status permitidos: `não iniciada`, `em execução`, `em auditoria`, `correção necessária`,
`aprovada`, `versionada`, `publicada`.

---

## 8. Auditoria

A auditoria é **independente do relato do Claude Code**. Verifica arquivos, diffs, testes,
Git, GitHub, PRs, commits e saídas reais.

Classificação de cada entrega:

- `APROVADA`;
- `APROVADA COM RESSALVAS`;
- `CORREÇÃO NECESSÁRIA`;
- `REJEITADA`.

Verificação obrigatória:

- escopo solicitado versus escopo executado;
- arquivos permitidos versus arquivos realmente alterados;
- caminhos, referências e duplicatas;
- valores comerciais inventados, copiados ou alterados;
- poderes reservados ao Douglas;
- `knowledge/casa77.yaml` como autoridade comercial;
- decisões comerciais determinísticas;
- LLM limitado a interpretação, extração, redação e classificação permitida;
- ausência de token, chave, senha e `.env`;
- tratamento de entradas e erros;
- testes reais e saída real;
- limites e falhas;
- complexidade adequada ao MVP;
- coerência com `docs/00-estado-atual.md`;
- coerência com o commit e a branch aprovados.

Não aprovar com erro estrutural, comercial, de segurança ou teste bloqueador.

Quando o erro for localizado, emitir correção específica — não mandar refazer a etapa inteira.

Formato da auditoria: **Veredito**, **Acertos**, **Problemas** (bloqueadores, importantes,
opcionais), **Impacto**, **Próxima ação** e, quando houver execução a fazer, **Prompt para o
Claude Code**.

---

## 9. Vocabulário de evidência

Distinguir sempre os estados de uma entrega:

`implementada` ≠ `testada` ≠ `aprovada` ≠ `versionada` ≠ `publicada`.

Distinguir sempre a qualidade da informação:

`verificado` ≠ `inferido` ≠ `informado` ≠ `histórico` ≠ `não verificável`.

**"Existe" não significa "funciona".** A presença de um arquivo, função ou rota não é evidência
de comportamento correto; evidência é teste real com saída real.

Os quatro princípios de disciplina de evidência:

- **"Existe" não significa "funciona".**
- **"Executou uma vez" não significa "está pronto para produção".**
- **"Está no n8n" não significa "está aprovado".**
- **"Está documentado" não significa "está implementado".**

São exemplos de disciplina de evidência, e não regra sobre um fornecedor específico: valem
para qualquer serviço, ferramenta ou artefato equivalente.

---

## 10. Esquema único de mandato ao Claude Code

Todo mandato contém, nesta ordem:

1. **contexto**;
2. **prestate**;
3. **leitura obrigatória**;
4. **arquivos permitidos para alteração**;
5. **tarefa**;
6. **regras obrigatórias**;
7. **fora do escopo**;
8. **validação**;
9. **critérios de parada**;
10. **resposta final**.

Evitar comandos vagos como "continue", "faça tudo" ou "decida o necessário".

---

## 11. Esquema único de resposta do Claude Code

Toda resposta final contém, no mínimo:

1. **prestate**;
2. **arquivos lidos**;
3. **arquivos criados**;
4. **arquivos alterados**;
5. **implementação e decisões realizadas**;
6. **comandos executados**;
7. **testes e saída real**;
8. **diff e escopo**;
9. **pendências e riscos**;
10. **confirmação de STOP e de que não avançou**.

Este é o **contrato único**. Não criar contratos concorrentes de resposta em outros arquivos.

---

## 12. Git e merge

- Versionamento e merge exigem **autorização humana** explícita.
- `git add .` não é padrão: versionar arquivos específicos, após auditoria.
- Nenhuma operação destrutiva sem autorização específica — `force`, `reset`, `rebase`,
  `clean`, `restore`, `branch -D` ou equivalente.
- Antes de ação destrutiva: explicar o impacto, confirmar a pasta, indicar ponto de retorno,
  preferir a opção reversível e obter autorização explícita.
- **Merge commit normal é o padrão do projeto.** Squash e rebase não são padrão enquanto a
  governança depender de commit funcional identificável.
- Antes de push ou publicação relevante, verificar `.gitignore`, ausência de `.env`, ausência
  de credenciais, arquivos temporários, branch correta, remoto correto, diff final e testes.

---

## 13. Tecnologias e arquitetura

**Nenhuma escolha tecnológica é automática** — framework, banco de dados, provedor de
WhatsApp, hospedagem, modelo de IA, ferramenta de calendário ou CRM.

Quando a escolha for necessária, comparar **no máximo duas alternativas**, avaliando:

- simplicidade;
- custo;
- documentação;
- manutenção;
- segurança;
- integração;
- crescimento esperado;
- **adequação ao MVP**.

Em seguida, **recomendar uma opção clara** e **aguardar aprovação antes de implementar**.

Evitar microsserviços, arquitetura excessiva, abstrações prematuras, dependências
desnecessárias e automação sem valor para o MVP.

A lógica comercial não fica espalhada pelo código: preços, capacidades, horários e restrições
são carregados de fonte estruturada.

---

## 14. Uso de LLM

O LLM **não pode**:

- calcular preços;
- escolher pacotes;
- validar capacidade;
- confirmar disponibilidade;
- oferecer descontos;
- autorizar visitas;
- fechar contratos;
- interpretar regras contratuais;
- criar exceções;
- alterar condições comerciais.

Essas decisões são **determinísticas**, apoiadas em regras e dados estruturados.

O LLM **pode**: interpretar intenção, extrair dados, classificar texto quando a regra
permitir, redigir respostas, adaptar linguagem, resumir leads e preparar handoff.

Dado comercial é validado antes do envio.

---

## 15. Regras comerciais e poderes reservados

O bot é informativo, consultivo e qualificativo. O responsável humano é **Douglas Bianchi**,
que mantém as decisões humanas reservadas.

O bot **não pode**:

- fechar contrato;
- conceder desconto;
- confirmar reserva;
- confirmar visita definitivamente;
- receber pagamento;
- aprovar cancelamento;
- alterar datas;
- criar exceções;
- modificar condição comercial.

`knowledge/casa77.yaml` é a **autoridade comercial**. Informação ausente, `null`, `pendente`,
não aprovada ou conflitante vira **pendência e handoff humano**.

Nunca inventar preço, capacidade, horário, desconto, disponibilidade ou condição. Nunca copiar
valor comercial para instrução, prompt, código, teste ou outro documento como fonte paralela.

---

## 16. Segurança

- Não solicitar nem expor segredo, token, chave, `.env` ou credencial.
- Não incluir credencial em prompt, log, commit ou documento.
- Quando uma credencial nova for necessária: **STOP** — e **não** pedir ao usuário que cole o
  segredo.
- Não copiar dado pessoal desnecessário.
- Tratar erro técnico sem expor detalhe interno ao usuário final.
- Manter rastreabilidade suficiente para auditoria.
- Interromper a entrega diante de risco de vazamento ou de alteração comercial indevida.

---

## 17. Repositório público

O repositório é tratado como **potencialmente público**.

Nenhum arquivo versionado pode conter segredo, token, credencial, `.env`, payload bruto, log,
dado pessoal desnecessário, URL administrativa, webhook, export bruto ou informação interna
desnecessária.

---

## 18. n8n, legado e serviços externos

- **Estado externo não substitui a `main`.** O que não está aprovado na `main` não é estado
  técnico do projeto.
- Legado exige **auditoria read-only antes de substituição**.
- **Acesso a serviço externo não significa autorização para escrever nele.**
- Mudança externa aprovada deve ter **representação versionada suficiente** no repositório.
- Export bruto de n8n não é publicado sem sanitização e aprovação.

### 18.1 Estado externo é evidência operacional, não aprovação

A existência de código, workflow, automação, banco, configuração ou integração em serviço
externo **não significa automaticamente**:

- arquitetura aprovada;
- implementação correta;
- funcionalidade validada;
- fonte de regra comercial;
- estado técnico aprovado do projeto.

A regra inversa vale igualmente: **a ausência de implementação equivalente na `main` não prova
que a funcionalidade não exista em serviço externo.**

Portanto, antes de planejar mudança que possa **duplicar**, **substituir**, **migrar** ou
**recriar** funcionalidade externa existente, o estado real desse serviço deve ser tratado como
**evidência necessária** — levantada, e não presumida em nenhuma das duas direções.

### 18.2 Taxonomia do legado

Após auditoria read-only de componente anterior à governança atual e ainda não reconciliado com
a `main`, classificar explicitamente em **exatamente uma** categoria:

- `PRESERVAR`;
- `PRESERVAR COM ADAPTAÇÃO`;
- `MIGRAR`;
- `SUBSTITUIR`;
- `DESCARTAR`;
- `PENDENTE DE DECISÃO`.

**Nenhum componente legado é substituído automaticamente sem essa reconciliação.**

### 18.3 Read-only é o padrão externo

**Acesso a serviço externo não equivale a autorização de escrita.** O padrão é `READ-ONLY` até
existir **mandato explícito autorizando escrita**.

Sem autorização específica, não **criar**, **editar**, **excluir**, **ativar**, **desativar**,
**executar**, **enviar**, **publicar**, **migrar** nem **alterar configuração**.

Se uma informação necessária não puder ser obtida por operação seguramente read-only,
classificá-la como `NÃO VERIFICÁVEL` e devolver ao GPT. **Não improvisar mutação para descobrir
estado.**

### 18.4 Representação versionada de estado externo

Mudança funcional aprovada em serviço externo deve possuir **representação versionada
suficiente** no GitHub — suficiente para permitir, conforme aplicável:

- auditoria;
- entendimento;
- reconstrução;
- rastreabilidade;
- comparação futura.

Isso **não** significa publicar segredo, publicar credencial, publicar export bruto, nem
necessariamente armazenar representação integral do serviço.

A representação pode ser documentação, configuração sanitizada, especificação, código ou outro
artefato apropriado.

---

## 19. Testes — política conceitual

### Unitários

Preferencialmente sintéticos, isolados e determinísticos.

### Integração e contrato

Podem consultar `knowledge/casa77.yaml` **quando o objetivo for validar a integração com a
fonte canônica**.

Nunca:

- duplicar valores comerciais como fonte paralela;
- inventar expectativa comercial;
- alterar o YAML apenas para acomodar um teste.

### Anti-flakiness

Teste verde deve ser **determinístico e reproduzível**.

Não mascarar falha por:

- retry;
- `sleep` arbitrário;
- `skip` ou `xfail` usado para esconder regressão;
- alteração indevida do teste para aceitar implementação incorreta.

---

## 20. CI — princípios

A CI existe para produzir **evidência automática e reproduzível**, não para substituir a
auditoria.

Princípios:

- verde só com determinismo;
- falha não é silenciada;
- a suíte reflete o comportamento aprovado;
- ausência de CI não autoriza afirmar que algo está testado.

Os detalhes mecânicos serão definidos na futura etapa de CI e scripts.

---

## 21. Perfil do usuário em ações manuais

O usuário tem pouca experiência com programação, terminal, Git, GitHub, APIs, banco de dados e
publicação.

Toda instrução manual informa:

- onde executar;
- o comando exato;
- o resultado esperado;
- como confirmar que funcionou;
- o erro comum e a correção;
- quando parar e retornar o output.

Passos sequenciais. Não presumir conhecimento técnico.

---

## 22. Regra de parada

**STOP** diante de divergência material, e informe a inconsistência sem preencher lacuna por
suposição, quando:

- não houver acesso ao repositório;
- `docs/00-estado-atual.md` não puder ser lido;
- o commit funcional registrado não puder ser confirmado;
- os arquivos aprovados contradisserem o estado documentado;
- houver mudança funcional posterior não documentada;
- houver conflito comercial;
- houver risco de segurança;
- for necessária uma credencial nova;
- a ação solicitada for destrutiva e não estiver autorizada;
- a decisão necessária não estiver coberta pelo mandato.

Não determinar estado por memória, conversa anterior, ZIP, cópia local antiga ou inferência.

---

## 23. Cópias estáticas externas

A `main` é a **autoridade canônica** desta governança. As cópias usadas como fontes estáticas
no ChatGPT e no Claude Desktop são **auxiliares**.

Em divergência, **a versão aprovada na `main` prevalece**.

Não existe mecanismo autorreferencial de SHA dentro dos próprios arquivos canônicos. Se for
desejável registrar qual versão foi copiada para uma fonte externa, esse registro é **metadado
externo** à fonte canônica.

---

## 24. Atualização desta governança

Este arquivo contém regras estáveis. Não registrar aqui etapa atual, commit atual, PR atual,
número atual de testes, pendência temporária ou valor comercial.

Mudança estrutural de regra segue a rota apropriada — mudança de governança ainda não planejada
é **Rota A** — e é versionada na `main` como qualquer outra capacidade.

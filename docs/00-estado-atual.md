# 00 — Estado Atual do Projeto

Casa 77 SDR. Este arquivo é o **snapshot operacional corrente**: etapa, capacidade corrente,
última entrega funcional, baseline, pendências, bloqueadores e próxima ação.

Não é histórico, changelog, ledger nem catálogo de PRs ou commits.

| Assunto | Autoridade |
|---|---|
| Estado técnico definitivo | GitHub, branch `main` |
| Histórico técnico | Git e GitHub — PRs, commits, diffs |
| Dados comerciais e operacionais | `knowledge/casa77.yaml` |
| Regras permanentes e mapa de fontes | `docs/governanca/` |

**Não contém dado comercial.** Preço, capacidade, horário, pacote, condição e restrição vivem
exclusivamente em `knowledge/casa77.yaml`.

---

## 1. Posição atual

- Etapa macro: **Etapa 3 — Motor de respostas — em execução**.
- Última subetapa numerada concluída: **3B.7** (`ResolvedorIdentidade`,
  `src/casa77_sdr/identity.py`).
- O trabalho corrente está no **bloco de materialização de `C`**, composto por microentregas
  funcionais **sem numeração de subetapa**. **Não existe subetapa `3B.8`.**
- Etapa 4 permanece **absorvida pela Etapa 3B**; etapas 5 a 10 permanecem futuras
  (`docs/05-roadmap.md`).

---

## 2. Última entrega funcional relevante

**PR #137** — commit funcional `3b8c59d33c59120701c52073bfd5984c76cea9fc`.

Integração das **linhas 1 e 2 de `CY13` a `E1`** (`src/casa77_sdr/response_index.py`), que
deixou de manter autoridade própria sobre `caminho_yaml` e passou a delegar. A **linha 3**
permanece materializada como **fronteira isolada**, não integrada a `E1`.

---

## 3. Baseline funcional

Último **baseline funcional verificado** — evidência da entrega funcional acima, **não** uma
execução desta atualização:

- Python **3.14.5**;
- **`5262 passed`**, sob **`-W error`**;
- zero failures, zero errors, zero warnings.

Não há CI configurada no repositório: ausência de CI, não falha de CI.

---

## 4. Estado essencial da capacidade corrente — `C`

- **Contrato de `C`: ARBITRADO** (`docs/07` §2.3; registrado em `docs/07` §12, item 19).
- **`C` ainda NÃO está materializada integralmente.**
- O índice físico `knowledge/indice-respostas-aprovadas.yaml` **não existe**.
- A **autoridade de status ainda não migrou** para o índice: continua em
  `knowledge/respostas-aprovadas.md` (`C-11`).
- `CY13`:
  - **linha 1** — parser da gramática de `caminho_yaml`
    (`src/casa77_sdr/response_yaml_path.py`): materializada e integrada a `E1`
    **indiretamente**, através da linha 2;
  - **linha 2** — validação estrutural contextual
    (`src/casa77_sdr/response_yaml_path_context.py`): materializada e integrada a `E1`;
  - **linha 3** — resolver factual (`src/casa77_sdr/response_yaml_resolve.py`): materializada
    como **fronteira isolada**, **não integrada** a `E1`. `E1` não recebe raiz factual e não lê
    `knowledge/casa77.yaml`.
- Formato **`hora`**: regra mecânica **arbitrada** (`docs/07` §2.3, `C-A1-F3a`), mas
  **materialização funcional ausente** — `formatar_hora` ainda não existe em
  `src/casa77_sdr/response_format.py`.
- **`C-7`** ainda **não materializada** e não reaberta.
- **Sintaxe física de *placeholder*** continua **aberta**.
- **`C-A1-ST6`–`C-A1-ST10`** continuam **não satisfeitas** integralmente.

Existem fronteiras determinísticas já materializadas em torno de `C` — validador estrutural,
carregador *fail-closed*, comparador de equivalência, formatadores, avaliador de `ASSERTIVA`,
verificador de bijeção e canonicalizador de rótulo de status. **Nenhuma delas materializa `C`**:
todas recebem insumos prontos e nenhuma resolve *binding*, lê o índice ou consulta
`knowledge/**`. O catálogo dos módulos vive no código; o contrato vive em `docs/07` §2.3.

---

## 5. Pendências ativas

| Pendência | Situação atual | Impacto / bloqueio | Fonte |
|---|---|---|---|
| **B** — colisão conceitual de nome `RegistroAtendimento` | aberta; nenhum referente renomeado ou unificado | bloqueia implementar o componente `RegistroAtendimento` | `docs/07` §4.1.1, §12 item 21 |
| **C** — índice estruturado `Rxx` × YAML | contrato arbitrado / não materializado | requisito de `ValidadorConsistenciaBase` e, em cascata, de `SeletorFatos` e `ValidadorResposta`; **também pré-requisito da materialização de S2-D8**, e por isso bloqueia **indiretamente** o `OrquestradorMotor` e a integração completa enquanto essa dependência não estiver satisfeita | `docs/07` §2.3, §12 itens 19 e 10 |
| **S2-D5** — mensagem conversacional em `aguardando_confirmacao_disponibilidade` antes de `E16` | aberta; resolver na Etapa 6 | não bloqueia | `docs/06` §12 |
| **S2-D7** — `E13` a partir de estado diferente de `encaminhado_humano` | aberta; resolver na Etapa 5 | não bloqueia | `docs/06` §12 |
| **S2-D8** — detecção e classificação de pendências e cobertura de resposta aprovada | contrato arbitrado / não materializado; nenhum módulo nem mapa `R2` | bloqueia o `OrquestradorMotor` e a integração completa | `docs/07` §4.4.1, §12 item 10; `docs/06` §11 |
| **S3-D1** — produtor da condição `motivo_encerramento` | produtor **não atribuído** | impede completar a **condição 8 de `CondicoesCiclo`** e os fluxos que dependem dela na integração completa | `docs/07` §4.4, §12 item 10 |
| **E1** — conversa × atendimento × lead | não arbitrada; atravessa identidade, persistência e registro de leads | não bloqueia a especificação vigente | `docs/07` §12 item 13 |
| **E3** — evento novo durante atendimento ativo | aberta; contrato vigente é conservador (`AMBIGUA`) | não bloqueia | `docs/07` §12 item 14 |
| **E4** — tratamento de `SEM_CANDIDATO_ELEGIVEL` | aberta; o ciclo encerra sem transição | bloqueia o `OrquestradorMotor` | `docs/07` §12 item 15 |
| **N-a** — integração operacional residual | especificação concluída e fronteiras `M-T`/`M-E`/`M-C`/`M-DT`/`M-AE` materializadas; integração da etapa 13 no pipeline pendente, com bloqueios S4/S5 sem tratamento operacional | bloqueia o pipeline completo | `docs/07` §6.2, §12 item 11 |
| **Limiar temporal de recência** | valor numérico e mecanismo de carga indefinidos; não é dado comercial | bloqueia a integração operacional de `N-a` e o `OrquestradorMotor` | `docs/07` §12 item 18 |
| **N-b** — produtor não determinístico / LLM, `N-b-RES2` e integração da etapa 4 | contrato arbitrado; fronteira determinística materializada; produtor real, interpretação de texto livre, `N-b-RES2` e integração pendentes | bloqueia o `OrquestradorMotor` e a integração completa | `docs/07` §6.3, §12 item 12 |
| **Unicidade geral de `id_atendimento`** | não decidida entre candidatos não identificados | não bloqueia o bloco corrente de materialização de `C` | `docs/07` §12 item 17 |
| **Retorno do controle ao bot** | não existe transição inversa de `T31` | não bloqueia | `docs/07` §12 item 16 |
| **Persistência operacional não volátil** | contrato arbitrado; implementação volátil não sustenta operação real; nenhuma tecnologia escolhida | bloqueia qualquer uso em canal real | `docs/07` §7.3, §7.4, §12 item 2a |
| **Destino do alerta operacional** | canal separado da conversa exigido por S5, Q5 e F4; destino não especificado | bloqueia o `OrquestradorMotor` | `docs/07` §12 item 3a |
| **Confirmação física de entrega do handoff** | `encaminhado_humano` afirma handoff registrado, nunca recebimento confirmado | não bloqueia; futura da Etapa 5 | `docs/06` §10; `docs/07` §12 item 5 |

Pendências comerciais e lacunas da base **não são replicadas aqui**:
`knowledge/informacoes-pendentes.md` é a fonte única.

---

## 6. Bloqueadores da integração completa

Bloqueiam o `OrquestradorMotor` e o pipeline completo:

- **S2-D8** — materialização do produtor de pendências e de cobertura;
- **C** — materialização do índice e dos artefatos necessários à cascata de validação e como
  pré-requisito de **S2-D8**;
- **S3-D1** — produtor de `motivo_encerramento` ainda não atribuído; impede completar a
  **condição 8 de `CondicoesCiclo`** e os fluxos que dependem dela;
- **E4** — tratamento de `SEM_CANDIDATO_ELEGIVEL`;
- **N-b** — produtor não determinístico, `N-b-RES2` e integração da etapa 4;
- **N-a** — integração operacional da etapa 13, tratamento dos bloqueios S4/S5 e destino do
  alerta operacional;
- **limiar temporal** — valor e mecanismo de carga.

Bloqueia o **uso real** em canal, à parte da integração: **persistência operacional não
volátil**.

**Não são bloqueadores** — abertas, porém sem condicionar a integração vigente: **B**, **E1**,
**E3**, **S2-D5**, **S2-D7**, unicidade geral de `id_atendimento` e retorno do controle ao bot.

A `MaquinaEstados` **não depende** dessas pendências para o contrato já definido: recebe
eventos confirmados e condições já estruturadas.

---

## 7. Próxima ação

A próxima microentrega funcional ainda não está eleita. A priorização volta ao GPT após a
conclusão da migração de governança v2.

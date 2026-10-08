# OrquestradorMotor completo (M2) — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ligar as peças já versionadas do motor num ciclo único `processar_mensagem(...)` que vai da mensagem recebida à resposta emitida, liberando o **M2 — primeiro teste conversacional local**.

**Architecture:** O recorte `R1` (`orchestrator.py`, etapas 1–3 + TS45) é preservado. Cada grupo de etapas ganha um módulo coordenador próprio e pequeno (5 / 6–7 / 8–12 / 13), e `orchestrator.py` ganha a função pública `processar_mensagem` que os encadeia e executa a etapa 14. Todas as dependências externas (persistência, produtor LLM, alerta, envio, entrega de resumo, configuração temporal) chegam por uma raiz de composição explícita — zero default operacional no código.

**Tech Stack:** Python ≥ 3.13, PyYAML, `anthropic`, pytest. Nenhuma dependência nova.

**Spec:** `docs/07-arquitetura-motor-respostas.md` §5 (pipeline de 14 etapas), §4.1.10 (`OMR1`), §4.4/§4.4.1 (condições e ordem pré-etapa 7), §6.3 (`CN4-1`–`CN4-12`, `EN4`, `RES2`), §7.1 (`TS45`, `E4`, R3/R5, A1–A7), §7.2 (falhas de persistência); `docs/06-maquina-de-estados.md` §4, §4.2, §4.5, §10; `docs/00-estado-atual.md` §7 (bloqueadores do M2).

---

## Global Constraints

- Python `>=3.13`; dependências limitadas a `PyYAML>=6.0` e `anthropic>=1.0` (`pyproject.toml`).
- Nenhum valor comercial (preço, capacidade, horário, pacote) no código: a única origem é `knowledge/casa77.yaml`.
- Zero default operacional: `janela_idempotencia`, `limiar_recencia`, `tentar_alerta`, `enviar_mensagem`, `entregar_resumo` chegam **explícitos** do chamador.
- Nenhum relógio vivo: o instante do ciclo é `EntradaMensagem.recebida_em`.
- Captura de exceções **por classe nomeada**; nunca `except Exception` fora da tentativa de alerta isolada (padrão de `_tentar_alerta_operacional`).
- Fail-closed: entrada estrutural inválida bloqueia; sem resultado parcial.
- **A etapa 13 antecede a 14 sem exceção.** Nunca emitir um estado não gravado.
- `deve responder = false` sempre que `situacao_takeover != SEM_TAKEOVER` ou estado `atendimento_humano`.
- Interpretação chamada **no máximo uma vez por ciclo** (`CN4`), e o mesmo `ArtefatosInterpretacao` é reutilizado.
- Suíte completa: `python -m pytest -q` deve continuar verde ao fim de cada tarefa (baseline: 9468 testes).

## Review Focus

1. **Mensagem duplicada** (mesmo `id_mensagem_canal` reenviado pelo canal) → zero efeito, zero resposta. Teste na Task 7.
2. **LLM indisponível** (`FalhaProdutorInterpretacao`) → nenhuma resposta inventada; pendente preservado e alerta tentado. Teste na Task 3.
3. **Falha de persistência na etapa 13** → nenhuma mensagem emitida; pendente preservado; alerta. Teste na Task 6.
4. **Mensagem durante `atendimento_humano`** (Douglas assumiu) → o bot fica em silêncio. Teste na Task 7.
5. **Pergunta sobre informação `pendente` no YAML** → nunca inventa: resposta segura (R03) + handoff. Teste na Task 5.

---

## Estrutura de arquivos

| Arquivo | Responsabilidade |
|---|---|
| `src/casa77_sdr/motor_deps.py` (novo) | `BaseMotor` (YAML, índice, mapa, textos, consistência carregados uma vez) e `DependenciasMotor` (raiz de composição) |
| `src/casa77_sdr/hydration.py` (novo) | `RegistroAtendimento` ⇄ (`Estado`, `DadosQualificacao`) |
| `src/casa77_sdr/orchestrator_identity.py` (novo) | etapas 4–5 + desfechos terminais `AMBIGUA`, `SEM_CANDIDATO_ELEGIVEL` (E4), `HUMANO_MULTIPLO`, falha de interpretação |
| `src/casa77_sdr/orchestrator_decision.py` (novo) | etapas 6–7: regras → qualificação provisória → S2-D8 → eventos → qualificação final → `decidir` |
| `src/casa77_sdr/orchestrator_emission.py` (novo) | etapas 8–12: projeção → fatos → composição → montagem → validação → substituição/R03 |
| `src/casa77_sdr/orchestrator_persist.py` (novo) | etapa 13: criar/gravar com marco de transição + marcar chave |
| `src/casa77_sdr/orchestrator.py` (modificar) | `processar_mensagem` + etapa 14; mantém `coordenar_etapas_1_a_3` intacto |
| `scripts/conversar_local.py` (novo) | REPL local do M2 com Anthropic real |
| `tests/test_<módulo>.py` | um arquivo de teste por módulo novo; `tests/test_ciclo_completo.py` para ponta a ponta |

### Tipos compartilhados (definidos nas tasks indicadas; os nomes são contrato entre tasks)

```python
# motor_deps.py (Task 1)
@dataclass(frozen=True)
class BaseMotor:
    base: dict[str, Any]                 # load_knowledge("knowledge/casa77.yaml")
    indice: dict[str, Any]               # carregar_indice("knowledge/indice-respostas-aprovadas.yaml")
    mapa: dict[str, Any]                 # carregar_mapa_cobertura("knowledge/mapa-cobertura.yaml")
    textos: dict[str, str]               # token "Rxx/Fy" -> template, de respostas-aprovadas.md
    consistencia: ResultadoConsistencia  # validar_consistencia_base(indice, base, textos)

@dataclass(frozen=True)
class DependenciasMotor:
    base_motor: BaseMotor
    persistencia: PersistenciaOperacional
    produtor: ProdutorTextoEstruturado
    prompt_sistema: str
    janela_idempotencia: timedelta
    limiar_recencia: timedelta
    calendario_integrado: bool
    tentar_alerta: Callable[..., object]
    enviar_mensagem: Callable[[str, str, str], None]   # (canal, contato, texto)
    entregar_resumo: Callable[[str], None]             # (resumo) -> levanta em falha

# hydration.py (Task 2)
@dataclass(frozen=True)
class AtendimentoHidratado:
    id_atendimento: str | None   # None => atendimento novo (será criado na etapa 13)
    estado: Estado
    dados: DadosQualificacao
    marco_atual: datetime | None

# orchestrator_identity.py (Task 3)
class DesfechoTerminal(StrEnum):
    INTERPRETACAO_INDISPONIVEL = "interpretacao_indisponivel"
    AMBIGUA = "ambigua"
    SEM_CANDIDATO_ELEGIVEL = "sem_candidato_elegivel"
    HUMANO_MULTIPLO = "humano_multiplo"

@dataclass(frozen=True)
class AlvoDoCiclo:
    artefatos: ArtefatosInterpretacao
    decisao_identidade: DecisaoIdentidade
    atendimento: AtendimentoHidratado

# orchestrator_decision.py (Task 4)
@dataclass(frozen=True)
class PrimeiraDecisao:
    decisao: DecisaoMaquina
    qualificacao: Qualificacao
    s2d8: ResultadoS2D8
    atualizacao: ResultadoAtualizacaoDados

# orchestrator_emission.py (Task 5)
@dataclass(frozen=True)
class TextoFinal:
    texto: str | None            # None => nada a dizer ao interessado
    decisoes_do_ciclo: tuple[DecisaoMaquina, ...]   # 1 a 3 chamadas (7, E15, E12)
    resumo_handoff: str | None

# orchestrator.py (Task 7)
class DesfechoCiclo(StrEnum):
    IGNORADA = "ignorada"            # vazia, duplicada ou bloqueio TS45
    TERMINAL_IDENTIDADE = "terminal_identidade"
    BLOQUEADA_PERSISTENCIA = "bloqueada_persistencia"
    RESPONDIDA = "respondida"
    SILENCIOSA = "silenciosa"        # atendimento humano / nada a emitir

@dataclass(frozen=True)
class ResultadoCiclo:
    desfecho: DesfechoCiclo
    texto_emitido: str | None
    estado_final: Estado | None
```

---

### Task 0: Arrumação do repositório (sem código)

**Files:** nenhum arquivo de código.

- [ ] **Step 1:** Revisar o PR #178 (`gh pr diff 178`) e fazer merge: `gh pr merge 178 --merge`.
- [ ] **Step 2:** `git checkout main && git pull`.
- [ ] **Step 3:** (feito na governança v3) `AGENTS.md` aponta para `CLAUDE.md`.
- [ ] **Step 4:** Remover o worktree obsoleto, depois de confirmar que nada nele é necessário: `git worktree remove ../casa77-sdr-vr-clean --force` e `git branch -D feat/c-response-validation-clean`.
- [ ] **Step 5:** Criar a branch de trabalho: `git checkout -b feat/orquestrador-m2`.
- [ ] **Step 6:** `python -m pytest -q` → esperado `9468 passed`.

---

### Task 1: Raiz de composição — `BaseMotor` e `DependenciasMotor`

**Files:**
- Create: `src/casa77_sdr/motor_deps.py`
- Test: `tests/test_motor_deps.py`

**Interfaces:**
- Consumes: `load_knowledge`, `carregar_indice`, `carregar_mapa_cobertura`, `validar_mapa_cobertura`, `conferir_referencias`, `validar_indice`, `extrair_textos_emitiveis`, `validar_consistencia_base`.
- Produces: `BaseMotor`, `DependenciasMotor` (campos acima), `carregar_base_motor(raiz: Path) -> BaseMotor`.

- [ ] **Step 1: Teste que falha**

```python
from pathlib import Path
from casa77_sdr.motor_deps import BaseMotor, carregar_base_motor

RAIZ = Path(__file__).resolve().parents[1]

def test_carrega_base_real_sem_erro():
    bm = carregar_base_motor(RAIZ)
    assert isinstance(bm, BaseMotor)
    assert bm.textos, "textos aprovados não podem ser vazios"
    assert all("/" in token for token in bm.textos)
    assert bm.consistencia is not None

def test_raiz_inexistente_falha_fechado(tmp_path):
    import pytest
    with pytest.raises(Exception):
        carregar_base_motor(tmp_path)
```

- [ ] **Step 2:** `python -m pytest tests/test_motor_deps.py -v` → FAIL (`ModuleNotFoundError`).
- [ ] **Step 3: Implementação mínima**

```python
def carregar_base_motor(raiz: Path) -> BaseMotor:
    k = raiz / "knowledge"
    base = load_knowledge(k / "casa77.yaml")
    indice = carregar_indice(k / "indice-respostas-aprovadas.yaml")
    validar_indice(indice)
    mapa = carregar_mapa_cobertura(k / "mapa-cobertura.yaml")
    validar_mapa_cobertura(mapa)
    conferir_referencias(mapa, indice)
    textos = dict(extrair_textos_emitiveis((k / "respostas-aprovadas.md").read_text(encoding="utf-8")))
    consistencia = validar_consistencia_base(indice, base, textos)
    return BaseMotor(base, indice, mapa, textos, consistencia)
```

  Antes de escrever, confirmar em `tests/test_indice_respostas_aprovadas_corpus.py` e `tests/test_mapa_cobertura_corpus.py` como o corpus real já é carregado — **reutilizar exatamente essa sequência** se diferir da acima.
- [ ] **Step 4:** `python -m pytest tests/test_motor_deps.py -v` → PASS; `python -m pytest -q` → verde.
- [ ] **Step 5:** `git add src/casa77_sdr/motor_deps.py tests/test_motor_deps.py && git commit -m "feat: add motor composition root"`

---

### Task 2: Hidratação do atendimento

**Files:**
- Create: `src/casa77_sdr/hydration.py`
- Test: `tests/test_hydration.py`

**Interfaces:**
- Consumes: `RegistroAtendimento`, `Estado`, `DadosQualificacao`, `DadosAtendimento`, `FormatoEvento`.
- Produces: `AtendimentoHidratado`, `hidratar(registro: RegistroAtendimento | None) -> AtendimentoHidratado`, `desidratar(at: AtendimentoHidratado, *, id_atendimento: str, canal: str, contato: str, decisao: DecisaoMaquina, qualificacao: Qualificacao, s2d8: ResultadoS2D8) -> RegistroAtendimento`.

Chaves de `dados_coletados`: `tipo_evento`, `data_nomeada`, `convidados`, `nome`, `contato`, `formato` (valor de `FormatoEvento`). Antes de fixá-las, conferir em `tests/test_persistence.py` e `tests/test_context.py` se já existe convenção; se existir, ela prevalece.

- [ ] **Step 1: Testes que falham**

```python
from casa77_sdr.hydration import hidratar
from casa77_sdr.state_machine import Estado

def test_sem_registro_e_atendimento_novo():
    at = hidratar(None)
    assert at.id_atendimento is None
    assert at.estado is Estado.NOVO
    assert at.dados.atendimento.convidados is None
    assert at.marco_atual is None

def test_registro_existente_preserva_estado_e_dados(registro_coletando):
    at = hidratar(registro_coletando)
    assert at.estado is Estado.COLETANDO_DADOS
    assert at.dados.atendimento.convidados == 80
    assert at.id_atendimento == registro_coletando.id_atendimento

def test_estado_desconhecido_falha_fechado(registro_coletando):
    import dataclasses, pytest
    ruim = dataclasses.replace(registro_coletando, estado_conversa="inventado")
    with pytest.raises(ValueError):
        hidratar(ruim)

def test_ida_e_volta_preserva_dados(registro_coletando, decisao_coletando, qualificacao, s2d8_vazio):
    at = hidratar(registro_coletando)
    reg = desidratar(at, id_atendimento=at.id_atendimento, canal="whatsapp", contato="5527999",
                     decisao=decisao_coletando, qualificacao=qualificacao, s2d8=s2d8_vazio)
    assert hidratar(reg).dados == at.dados
```

  As fixtures (`registro_coletando` etc.) ficam no próprio arquivo de teste, construídas com valores sintéticos (nunca dados comerciais reais).
- [ ] **Step 2:** rodar → FAIL.
- [ ] **Step 3:** implementar `hidratar`/`desidratar` (conversão pura, sem I/O; `Estado(registro.estado_conversa)` levanta `ValueError` para valor inválido).
- [ ] **Step 4:** rodar → PASS; suíte verde.
- [ ] **Step 5:** `git commit -m "feat: add attendance hydration"`

---

### Task 3: Etapas 4–5 — interpretação única + identidade + desfechos terminais

**Files:**
- Create: `src/casa77_sdr/orchestrator_identity.py`
- Test: `tests/test_orchestrator_identity.py`

**Interfaces:**
- Consumes: `executar_interpretacao_do_ciclo`, `FalhaProdutorInterpretacao`, `resolver_identidade`, `ProjecoesIdentidadeEtapa3`, `hidratar`, `DependenciasMotor`, `EntradaMensagem`, `EntradaNormalizada`.
- Produces: `DesfechoTerminal`, `AlvoDoCiclo`, `coordenar_etapas_4_e_5(entrada, entrada_normalizada, projecoes, deps) -> AlvoDoCiclo | DesfechoTerminal`.

Regras (ler §5 tabela da etapa 5 e §7.1 `E4-1`–`E4-14`, A1–A7, R5 antes de implementar):

| Situação | Efeitos | Retorno |
|---|---|---|
| `FalhaProdutorInterpretacao` | preservar pendente → tentar alerta → **não** marcar chave (reprocessável); confirmar contra N-b-M1–M8 | `INTERPRETACAO_INDISPONIVEL` |
| `HUMANO_MULTIPLO` | preservar → alertar → marcar chave; zero máquina; zero emissão | `HUMANO_MULTIPLO` |
| `SEM_CANDIDATO_ELEGIVEL` | contrato E4: preservar → alertar → marcar chave; zero emissão | `SEM_CANDIDATO_ELEGIVEL` |
| `AMBIGUA` | sem transição; nada herdado; A1–A7 | `AMBIGUA` (a Task 7 decide a mensagem de esclarecimento) |
| `HUMANO_UNICO` | prossegue com `estado = ATENDIMENTO_HUMANO`, `identidade = None` | `AlvoDoCiclo` |
| `NOVA_SOLICITACAO` / `PRIMEIRO_CONTATO_COMPROVADO` | `hidratar(None)` — nada herdado (I15) | `AlvoDoCiclo` |
| `ATENDIMENTO_ATIVO` / `MESMA_SOLICITACAO` | `hidratar(persistencia.recuperar_por_id(alvo, ...))` | `AlvoDoCiclo` |

- [ ] **Step 1: Testes que falham** — um por linha da tabela, mais:

```python
def test_interpretacao_chamada_exatamente_uma_vez(deps_fake, entrada, normalizada, projecoes_vazias):
    coordenar_etapas_4_e_5(entrada, normalizada, projecoes_vazias, deps_fake)
    assert deps_fake.produtor.chamadas == 1

def test_llm_indisponivel_preserva_e_alerta_sem_marcar_chave(deps_produtor_falha, entrada, normalizada, projecoes_vazias):
    r = coordenar_etapas_4_e_5(entrada, normalizada, projecoes_vazias, deps_produtor_falha)
    assert r is DesfechoTerminal.INTERPRETACAO_INDISPONIVEL
    assert deps_produtor_falha.persistencia.recuperar_pendentes()
    assert deps_produtor_falha.alertas[-1]["categoria"] == "FalhaProdutorInterpretacao"
    assert not deps_produtor_falha.persistencia.chave_processada(normalizada.chave_idempotencia)
```

  Produtor fake: reutilizar o padrão de produtor simulado de `tests/test_interpretation_stage.py` (contador de chamadas + payload fixo).
- [ ] **Step 2:** rodar → FAIL.
- [ ] **Step 3:** implementar. Reaproveitar a ordem preservar→alertar→marcar de `orchestrator._tratar_bloqueio_ts45` (extrair um helper `_preservar_alertar_marcar` em `orchestrator.py` se preciso — conta como um dos 5 arquivos).
- [ ] **Step 4:** rodar → PASS; suíte verde.
- [ ] **Step 5:** `git commit -m "feat: coordinate pipeline stages 4 and 5"`

---

### Task 4: Etapas 6–7 — primeira decisão da máquina

**Files:**
- Create: `src/casa77_sdr/orchestrator_decision.py`
- Test: `tests/test_orchestrator_decision.py`

**Interfaces:**
- Consumes: `AlvoDoCiclo`, `BaseMotor`, `atualizar_dados_atendimento`, `avaliar_regras`, `qualificar`, `decidir_aplicabilidade_de_pacote`, `decidir_pendencias_e_cobertura`, `produzir_eventos_internos_ciclo`, `detectar_handoff`, `decidir_encerramento`, `agregar_eventos_primeira_decisao`, `montar_condicoes_ciclo`, `decidir`.
- Produces: `PrimeiraDecisao`, `decidir_primeira_chamada(alvo: AlvoDoCiclo, *, base_motor: BaseMotor, calendario_integrado: bool, e01_confirmado: bool) -> PrimeiraDecisao`.

Ordem obrigatória (§5, "ordem conceitual determinística anterior à etapa 7"):

```python
atualizacao = atualizar_dados_atendimento(alvo.atendimento.dados, alvo.artefatos.interpretacao)        # etapa 6
violacoes = tuple(avaliar_regras(atualizacao.dados_atualizados.atendimento, bm.base))                  # 1
q_prov = qualificar(atualizacao.dados_atualizados, violacoes, (), bm.base)                             # 2
aplic = decidir_aplicabilidade_de_pacote(atualizacao.dados_atualizados, bm.base)
s2d8 = decidir_pendencias_e_cobertura(alvo.artefatos.interpretacao, q_prov, bm.mapa, bm.indice,
                                      bm.consistencia, fatos_runtime, aplic)                           # 3–5
q_final = qualificar(atualizacao.dados_atualizados, violacoes, s2d8.pendencias_impeditivas, bm.base)   # 6
internos = produzir_eventos_internos_ciclo(q_final, atualizacao.insumo_qualificacao_atualizado, s2d8)
handoff = detectar_handoff(alvo.artefatos.interpretacao)
enc = decidir_encerramento(alvo.artefatos.interpretacao, q_final.resultado)
eventos = agregar_eventos_primeira_decisao(e01_confirmado, alvo.artefatos.eventos_interpretacao, internos, handoff, enc)
condicoes = montar_condicoes_ciclo(atualizacao.insumo_qualificacao_atualizado, s2d8.pendencia_impeditiva, handoff,
                                   s2d8.resposta_aprovada_disponivel, alvo.artefatos.interesse_confirmar_disponibilidade,
                                   calendario_integrado, alvo.decisao_identidade.identidade, enc)
decisao = decidir(alvo.atendimento.estado, eventos, q_final, condicoes)                                # 7
```

  `fatos_runtime`: ler o docstring de `coverage_decision.py` linhas 50–75 e montar a fotografia a partir de `atualizacao.dados_atualizados`. `e01_confirmado`: verdadeiro quando o atendimento é novo (doc 06 §2 — confirmar).
- [ ] **Step 1: Testes que falham** — com produtor fake e base real (`carregar_base_motor`):
  - primeira mensagem "Oi, quero alugar para um aniversário" em atendimento novo → `decisao.estado_final` sai de `NOVO` e `AcaoMaquina.APRESENTAR_ATENDIMENTO_INICIAL in decisao.acoes`;
  - mensagem com pedido explícito de humano → `decisao.motivos_handoff` não vazio;
  - Classe I (mapa inválido) → exceção propaga, `decidir` não é chamado (monkeypatch contador).
- [ ] **Step 2:** rodar → FAIL. **Step 3:** implementar. **Step 4:** PASS + suíte verde.
- [ ] **Step 5:** `git commit -m "feat: coordinate pipeline stages 6 and 7"`

---

### Task 5: Etapas 8–12 — da decisão ao texto final validado

**Files:**
- Create: `src/casa77_sdr/orchestrator_emission.py`
- Test: `tests/test_orchestrator_emission.py`

**Interfaces:**
- Consumes: `PrimeiraDecisao`, `BaseMotor`, `projetar_fragmentos_para_emissao`, `montar_fotografia_fragmento`, `materializar_fatos_autorizados`, `compor_textos_emitiveis`, `montar_resposta_final`, `validar_resposta_final`, `decidir`.
- Produces: `TextoFinal`, `produzir_texto_final(pd: PrimeiraDecisao, *, base_motor: BaseMotor, estado_inicial: Estado, condicoes: CondicoesCiclo) -> TextoFinal`.

Decisões de MVP (registrar no PR):
- **Etapa 10 sem LLM no M2**: o texto candidato é o literal aprovado (`RespostaMontada.texto`) — caminho já autorizado em §5 ("LLM indisponível → usar o texto aprovado literal"). Redação por LLM fica para depois do M2.
- **Etapa 12**: se a validação reprovar ou não houver fragmento para as ações → R03 + handoff (§5, etapa 12). Re-entrada de `E15`/`E12` na máquina: no máximo duas chamadas extras, na ordem `E15` → `E12` (doc 06 §2.2, §4.2) — ler esses parágrafos antes de implementar.
- Estado `ATENDIMENTO_HUMANO` ou `AcaoMaquina.SILENCIAR_RESPOSTA_AUTOMATICA` em `acoes` → `TextoFinal(texto=None, ...)`.
- `fotografia_r06`: montar com `montar_fotografia_fragmento` somente quando `R06/F1` estiver nos fragmentos autorizados (§4.4.6).

- [ ] **Step 1: Testes que falham**
  - ação `APRESENTAR_ATENDIMENTO_INICIAL` → `texto` não vazio e igual, byte a byte, à composição dos fragmentos aprovados;
  - **Review Focus 5**: pergunta sobre assunto com `grupos: []` no mapa (ex.: um dos 21 vazios) → texto é o R03 e `resumo_handoff` não é `None`;
  - estado `ATENDIMENTO_HUMANO` → `texto is None`;
  - validação reprovada (monkeypatch `validar_resposta_final` → `aprovado=False`) → substitui por R03, sem nova chamada ao LLM.
- [ ] **Step 2–4:** FAIL → implementar → PASS + suíte verde.
- [ ] **Step 5:** `git commit -m "feat: coordinate pipeline stages 8 to 12"`

---

### Task 6: Etapa 13 — persistência do ciclo

**Files:**
- Create: `src/casa77_sdr/orchestrator_persist.py`
- Test: `tests/test_orchestrator_persist.py`

**Interfaces:**
- Consumes: `desidratar`, `criar_com_marco_de_transicao`, `gravar_com_marco_de_transicao`, `PersistenciaOperacional`, `FalhaDePersistencia`.
- Produces: `persistir_ciclo(*, deps, alvo, primeira, texto_final, entrada, entrada_normalizada, gerar_id: Callable[[], str]) -> bool` (`True` gravado; `False` bloqueado).

Regras: atendimento novo → `criar_com_marco_de_transicao` com `id_atendimento = gerar_id()` (injetado; teste usa contador determinístico); existente → `gravar_com_marco_de_transicao(marco_atual=alvo.atendimento.marco_atual)`. Sucesso → `marcar_chave_processada`. `FalhaDePersistencia` → preservar pendente → alertar → **não** marcar → `False` (§7.2).

- [ ] **Step 1: Testes que falham**
  - atendimento novo é criado com o id gerado e o estado de `decisoes_do_ciclo[-1].estado_final`;
  - `instante_ultima_transicao` = `entrada.recebida_em` quando houve mudança de estado e inalterado quando não houve;
  - **Review Focus 3**: persistência fake que levanta `FalhaDePersistencia` em `gravar` → retorno `False`, pendente preservado, alerta tentado, chave **não** marcada.
- [ ] **Step 2–4:** FAIL → implementar → PASS + suíte verde.
- [ ] **Step 5:** `git commit -m "feat: persist pipeline cycle (stage 13)"`

---

### Task 7: `processar_mensagem` + etapa 14 — ciclo ponta a ponta

**Files:**
- Modify: `src/casa77_sdr/orchestrator.py` (acrescentar; não alterar `coordenar_etapas_1_a_3`)
- Test: `tests/test_ciclo_completo.py`

**Interfaces:**
- Consumes: todas as anteriores.
- Produces: `DesfechoCiclo`, `ResultadoCiclo`, `processar_mensagem(entrada: EntradaMensagem, deps: DependenciasMotor, *, gerar_id: Callable[[], str]) -> ResultadoCiclo`.

Etapa 14: se há `resumo_handoff` → `deps.entregar_resumo(resumo)`; **somente após sucesso** emitir a mensagem de encaminhamento (doc 06 §10). Falha na entrega → não afirmar handoff ao interessado. `AMBIGUA` → mensagem de esclarecimento **apenas se existir texto aprovado** para ela; senão silêncio + alerta (não inventar texto — registrar como superfície sem unidade aprovada).

- [ ] **Step 1: Testes que falham** (`PersistenciaEmMemoria` + produtor fake roteirizado + `enviar_mensagem` que grava numa lista):
  - conversa de 3 mensagens (saudação → tipo de evento e convidados → nome) produz 3 respostas e o estado avança até `PRONTO_PARA_HANDOFF` ou `COLETANDO_DADOS`, conforme a máquina;
  - **Review Focus 1**: reenviar a mesma `EntradaMensagem` → `DesfechoCiclo.IGNORADA`, zero envio adicional;
  - **Review Focus 4**: atendimento gravado em `atendimento_humano` → `SILENCIOSA`, zero envio;
  - handoff: `entregar_resumo` levanta → nenhuma mensagem de encaminhamento enviada;
  - nada é enviado antes de a etapa 13 gravar (persistência fake registra a ordem das chamadas).
- [ ] **Step 2–4:** FAIL → implementar → PASS + suíte verde.
- [ ] **Step 5:** `git commit -m "feat: add end-to-end processar_mensagem cycle"`

---

### Task 8: REPL local do M2 + execução dos evals

**Files:**
- Create: `scripts/conversar_local.py`
- Modify: `README` não existe — instruções vão no docstring do script.

- [ ] **Step 1:** Script que monta `DependenciasMotor` com `PersistenciaEmMemoria`, `AdaptadorAnthropic` (chave em `ANTHROPIC_API_KEY`), `prompt_sistema` de `prompts/prompt-interpretacao.md`, `tentar_alerta`/`entregar_resumo` imprimindo em `stderr`, `enviar_mensagem` imprimindo em `stdout`, e `janela_idempotencia`/`limiar_recencia` **obrigatórios via argumentos de linha de comando** (sem default — o valor do limiar continua decisão aberta).
- [ ] **Step 2:** Rodar o smoke existente: `python scripts/smoke_interpretacao.py` e os evals de `evals/interpretacao/` — registrar resultado.
- [ ] **Step 3:** Rodar 5 conversas de `tests/cenarios-conversa.md` no REPL e anotar divergências.
- [ ] **Step 4:** `git commit -m "feat: add local conversation REPL for M2"`

---

### Task 9: Fechamento do M2

- [ ] Atualizar `docs/00-estado-atual.md` **uma única vez**: M2 liberado, o que ficou de fora (redação LLM, superfícies sem texto aprovado, decisões de M3).
- [ ] `superpowers:requesting-code-review` sobre a branch inteira.
- [ ] `superpowers:finishing-a-development-branch` → PR único `feat/orquestrador-m2`.

---

## Depois do M2 — trilha para o M3 (planos separados)

Cada item vira um plano próprio **depois** da decisão correspondente. Sugestões para andar rápido:

| Frente | Decisão pendente | Sugestão |
|---|---|---|
| Persistência real | tecnologia | SQLite local → Postgres no Render (implementa `PersistenciaOperacional`) |
| Alerta operacional | destino | e-mail ou WhatsApp para o Douglas (mesma função `tentar_alerta`) |
| Limiar de recência | valor | 30 dias, configurável por variável de ambiente |
| Handoff (Etapa 5) | canal e SLA | resumo por WhatsApp/e-mail para o Douglas |
| WhatsApp (Etapa 7) | provedor e número | Meta WhatsApp Cloud API (oficial) ou Z-API (mais simples) |
| Calendário (Etapa 6) | confirmar Google | Google Calendar só leitura; até lá `calendario_integrado=False` |
| Leads (Etapa 8) | destino | mesma base da persistência + exportação para planilha |
| Textos faltantes | aprovação do Douglas | coleta, formato, retomada, esclarecimento de `AMBIGUA`, reforço de encaminhamento |
| Publicação (Etapa 10) | hospedagem | Render (webhook do WhatsApp → `processar_mensagem`) |

## Processo

Este plano segue a governança v3 (`docs/governanca/01-regras.md`): tarefas executadas em
sequência sem autorização por tarefa, revisão por subagente, um PR para o M2,
`docs/00-estado-atual.md` atualizado só na Task 9 e merge com autorização do Victor.

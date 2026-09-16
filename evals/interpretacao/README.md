# Evals semânticos — produtor de interpretação da etapa 4

**O que isto é:** uma bateria **manual** de mensagens fictícias para observar a
qualidade de **interpretação** do produtor não determinístico da etapa 4.

**O que isto não é:** não é teste, não é CI, não é *gate* de PR e **não é
aprovação**. O resultado é **evidência operacional**
(`docs/governanca/01-regras.md` §9 e §18.1).

---

## As três classes, separadas

| Classe | Onde roda | Chama o modelo? | O que prova | O que **não** prova |
|---|---|---|---|---|
| **Contrato — determinístico** | CI, obrigatório (`tests/`) | não | forma, tradução, *fail-closed*, alcançabilidade dos `E-Nb`, montagem da chamada, blocos e `stop_reason` | qualidade de interpretação |
| **Evals semânticos** | manual, fora da CI (este diretório) | **sim** | acerto de extração, segmentação e classificação em pt-BR coloquial, inclusive sob adversário | nada de forma; **não é aprovação** |
| **Smoke operacional** | manual, fora da CI (`scripts/smoke_interpretacao.py`) | sim | que a chamada real funciona fim a fim **uma vez** | nem forma nem qualidade |

Confundi-las é o erro que este arquivo existe para impedir. *Structured output*
prova **forma**, não **verdade semântica**: uma classificação errada é
**contratualmente válida** e atravessa a fronteira determinística. Só o eval a
observa.

---

## O que os evals cobrem

`casos.yaml` traz **22** mensagens fictícias, em duas frentes:

- **adversariais** — ignorar instruções; JSON injetado; schema injetado;
  tentativa de forçar confiança `ALTA`; falsa instrução de sistema; texto
  legítimo misturado com injeção; tentativa de forçar assunto; tentativa de
  induzir preço, pacote e disponibilidade;
- **semânticas ordinárias** — ambiguidade intencional; perguntas compostas;
  correção explícita; contradição **sem** declaração; pedido de humano;
  continuidade; evento novo; exceção; visita; disponibilidade; tema sem
  categoria; mensagem sem conteúdo extraível.

O campo `observar` de cada caso é o que o **auditor humano** confere. Não existe
gabarito automático, e **nenhum limiar de aprovação foi arbitrado** — inventar
um aqui transformaria evidência em aprovação.

---

## Pré-requisitos

1. **Aprovação humana** para consumir tokens: cada caso é **uma chamada real**.
2. Credencial da Anthropic provisionada **no ambiente do operador**, fora deste
   repositório. Ela **nunca** é versionada, **nunca** entra na CI, **nunca** é
   colada em conversa e **nunca** é impressa por este runner.
3. `model`, `max_tokens` e `timeout` são **decisão operacional** e chegam por
   argumento: o runner não tem valor padrão para nenhum deles.

## Como rodar

```powershell
python evals/interpretacao/run_evals.py --model <modelo> --max-tokens <n> --timeout <s>
```

Um subconjunto:

```powershell
python evals/interpretacao/run_evals.py --model <modelo> --max-tokens <n> --timeout <s> --caso EV-01 --caso EV-12
```

`max_tokens` precisa caber o JSON inteiro: subdimensioná-lo produz
**truncamento**, que o adaptador trata como falha fechada — e truncamento
aparece no relatório como falha do produtor, não como erro de interpretação.

## Como ler o relatório

O runner imprime, por caso: a mensagem, o **desfecho** (`Interpretacao`
produzida, falha do produtor ou erro de contrato), a projeção legível da
estrutura e a lista `observar`.

Código de saída `0` significa **a bateria terminou**, nunca "passou". `1`
significa que a própria execução falhou — SDK ausente ou credencial não
resolvida.

## Limites

- Nada é gravado em disco. Copie o relatório se quiser arquivá-lo — **sem** PII
  e **sem** conversa real.
- Estas mensagens são **fictícias**. O repositório é público: nenhuma conversa
  real, nenhum dado pessoal e nenhum valor comercial entram aqui.
- `knowledge/casa77.yaml` permanece a autoridade comercial e **não** é lido por
  estes evals, pelo prompt ou pelo produtor.
- O risco observado aqui — **extração ou classificação semanticamente errada,
  induzida ou espontânea** — é risco de **modelo** e permanece **aberto**. Ele
  não é fechável por teste determinístico.

"""Smoke manual do produtor de interpretação da etapa 4 — **uma chamada real**.

**Execução exclusivamente manual, por decisão humana.** Não é teste, não roda em
CI, não é coletado pelo pytest e **não prova qualidade nem contrato**: ele prova
apenas que a chamada real funciona **fim a fim uma vez**.

Usa o **mesmo** schema, o **mesmo** prompt e o **mesmo** adaptador da produção —
`src/casa77_sdr/interpretation_llm.py` e
`src/casa77_sdr/interpretation_anthropic.py` —, sem caminho paralelo.

**Segurança.** A credencial é resolvida pelo **próprio SDK**, a partir do
ambiente do operador. Este script **não** lê variável de credencial diretamente,
**não** imprime chave, **não** pede que a chave seja colada, **não** persiste
nada e **não** imprime a mensagem enviada sem redação. Se a credencial não
existir, ele falha claramente e para.

Procedimento manual documentado em `evals/interpretacao/README.md`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from casa77_sdr.interpretation_anthropic import AdaptadorAnthropic  # noqa: E402
from casa77_sdr.interpretation_llm import (  # noqa: E402
    FalhaProdutorInterpretacao,
    interpretar_mensagem,
)

PROMPT = RAIZ / "prompts" / "prompt-interpretacao.md"

#: Mensagem fictícia e genérica. Zero PII, zero conversa real, zero valor
#: comercial. É o padrão justamente para que o smoke não exija texto real.
MENSAGEM_PADRAO = "oi, queria saber como funciona para um aniversário em maio"


def _redigir(texto: str) -> str:
    """Só o comprimento atravessa para a saída — nunca o conteúdo."""
    return f"<mensagem de {len(texto)} caracteres, conteúdo não impresso>"


def main() -> int:
    analisador = argparse.ArgumentParser(
        description=(
            "Faz UMA chamada real ao provedor e relata o desfecho. "
            "Consome tokens. Não prova qualidade nem contrato."
        )
    )
    analisador.add_argument("--model", required=True, help="identificador do modelo")
    analisador.add_argument("--max-tokens", required=True, type=int)
    analisador.add_argument("--timeout", required=True, type=float)
    analisador.add_argument(
        "--mensagem",
        default=MENSAGEM_PADRAO,
        help="mensagem fictícia a interpretar; nunca use conversa real",
    )
    argumentos = analisador.parse_args()

    try:
        import anthropic
    except ImportError:
        print("SDK `anthropic` não instalado.", file=sys.stderr)
        return 1

    try:
        cliente = anthropic.Anthropic()
    except Exception:
        print(
            "Credencial da Anthropic ausente ou inválida no ambiente do operador. "
            "Provisione-a fora deste repositório — ela não deve ser colada aqui, "
            "versionada nem adicionada à CI.",
            file=sys.stderr,
        )
        return 1

    produtor = AdaptadorAnthropic(
        cliente,
        model=argumentos.model,
        max_tokens=argumentos.max_tokens,
        timeout=argumentos.timeout,
    )

    print(f"modelo:    {argumentos.model}")
    print(f"mensagem:  {_redigir(argumentos.mensagem)}")

    try:
        interpretacao = interpretar_mensagem(
            argumentos.mensagem,
            produtor=produtor,
            prompt_sistema=PROMPT.read_text(encoding="utf-8"),
        )
    except FalhaProdutorInterpretacao as falha:
        print(f"desfecho:  FALHA DO PRODUTOR ({falha})")
        return 1
    except (ValueError, TypeError) as erro:
        print(f"desfecho:  ERRO DE CONTRATO ({erro})")
        return 1

    print("desfecho:  Interpretacao produzida")
    print(
        "intenções: "
        + (
            ", ".join(
                f"{item.codigo.value}={item.confianca.value}"
                for item in interpretacao.intencoes_detectadas
            )
            or "(nenhuma)"
        )
    )
    print(f"confiança global: {interpretacao.confianca_global.value}")
    print(f"perguntas: {len(interpretacao.perguntas_comerciais)}")
    print(f"correções: {len(interpretacao.correcoes)}")
    print("Nada foi persistido. Este smoke não prova qualidade nem contrato.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

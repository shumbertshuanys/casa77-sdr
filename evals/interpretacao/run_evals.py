"""Runner dos evals semânticos do produtor de interpretação da etapa 4.

**Execução exclusivamente manual, por decisão humana.** Este arquivo não é
coletado pelo pytest (`testpaths = ["tests"]`), não roda em CI, não bloqueia PR
e **não emite veredito**: ele apenas **relata** o que o modelo devolveu, caso a
caso, para leitura humana.

Ele **não define limiar de aprovação** e **não devolve PASS/FAIL global** —
nenhum limiar foi arbitrado, e inventar um transformaria evidência operacional
em aprovação, o que `docs/governanca/01-regras.md` §9 e §18.1 proíbem. O código
de saída é `0` quando a bateria terminou de rodar e `1` apenas quando a própria
execução falhou.

**Consome tokens reais.** Cada caso é uma chamada. Rodar exige decisão
operacional explícita.

A credencial é resolvida pelo **próprio SDK**, a partir do ambiente do operador.
Este script **não** lê, **não** imprime, **não** persiste e **não** pede
credencial alguma, e **nada** é gravado em disco.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

import yaml  # noqa: E402

from casa77_sdr.interpretation import Interpretacao  # noqa: E402
from casa77_sdr.interpretation_anthropic import AdaptadorAnthropic  # noqa: E402
from casa77_sdr.interpretation_llm import (  # noqa: E402
    FalhaProdutorInterpretacao,
    interpretar_mensagem,
)

CASOS = Path(__file__).resolve().parent / "casos.yaml"
PROMPT = RAIZ / "prompts" / "prompt-interpretacao.md"


def _relatar(interpretacao: Interpretacao) -> list[str]:
    """Projeção legível da `Interpretacao`, para leitura humana."""
    dados = interpretacao.dados_extraidos
    linhas = [
        "  intenções:      "
        + (
            ", ".join(
                f"{item.codigo.value}={item.confianca.value}"
                for item in interpretacao.intencoes_detectadas
            )
            or "(nenhuma)"
        ),
        "  dados:          "
        + (
            ", ".join(
                f"{campo}={dados._valor(campo)!r}/{getattr(dados, f'confianca_{campo}')}"
                for campo in (
                    "tipo_evento",
                    "data_nomeada",
                    "convidados",
                    "formato",
                    "nome",
                    "contato",
                )
                if dados._valor(campo) is not None
            )
            or "(nenhum)"
        ),
        "  correções:      "
        + (
            ", ".join(
                f"{item.campo}→{item.valor_novo!r}/{item.confianca.value}"
                for item in interpretacao.correcoes
            )
            or "(nenhuma)"
        ),
        "  perguntas:      "
        + (
            " | ".join(
                f"[{item.assunto.value}/{item.confianca.value}] {item.texto!r}"
                for item in interpretacao.perguntas_comerciais
            )
            or "(nenhuma)"
        ),
        f"  pedido humano:  {interpretacao.pedido_de_humano}"
        f" ({interpretacao.confianca_pedido_de_humano})",
        "  referências:    "
        + (
            " | ".join(
                f"[{item.confianca.value}] {item.texto!r}"
                for item in interpretacao.referencias_evento_anterior
            )
            or "(nenhuma)"
        ),
        "  trechos ambíg.: "
        + (
            " | ".join(repr(item.texto) for item in interpretacao.trechos_ambiguos)
            or "(nenhum)"
        ),
        f"  confiança glob.:{interpretacao.confianca_global.value}",
    ]
    return linhas


def main() -> int:
    analisador = argparse.ArgumentParser(
        description=(
            "Roda a bateria de evals semânticos. Consome tokens reais. "
            "Produz relatório, nunca veredito."
        )
    )
    analisador.add_argument("--model", required=True, help="identificador do modelo")
    analisador.add_argument("--max-tokens", required=True, type=int)
    analisador.add_argument("--timeout", required=True, type=float)
    analisador.add_argument(
        "--caso", action="append", default=None, help="roda apenas os ids indicados"
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
        # A credencial é resolvida pelo SDK a partir do ambiente do operador.
        # Nunca a imprimimos e nunca pedimos que ela seja colada.
        print(
            "Credencial da Anthropic ausente ou inválida no ambiente. "
            "Provisione-a fora deste repositório e rode novamente.",
            file=sys.stderr,
        )
        return 1

    prompt = PROMPT.read_text(encoding="utf-8")
    casos = yaml.safe_load(CASOS.read_text(encoding="utf-8"))["casos"]
    if argumentos.caso:
        escolhidos = set(argumentos.caso)
        casos = [caso for caso in casos if caso["id"] in escolhidos]

    produtor = AdaptadorAnthropic(
        cliente,
        model=argumentos.model,
        max_tokens=argumentos.max_tokens,
        timeout=argumentos.timeout,
    )

    print(f"# Relatório de evals — {len(casos)} caso(s), modelo {argumentos.model}")
    print("# Evidência operacional. NÃO é aprovação. NÃO existe limiar.\n")

    for caso in casos:
        print(f"## {caso['id']} — {caso['familia']}")
        print(f"  mensagem:       {caso['mensagem']!r}")
        try:
            interpretacao = interpretar_mensagem(
                caso["mensagem"], produtor=produtor, prompt_sistema=prompt
            )
        except FalhaProdutorInterpretacao as falha:
            print(f"  desfecho:       FALHA DO PRODUTOR ({falha})")
        except (ValueError, TypeError) as erro:
            print(f"  desfecho:       ERRO DE CONTRATO ({erro})")
        else:
            print("  desfecho:       Interpretacao produzida")
            for linha in _relatar(interpretacao):
                print(linha)
        print("  observar:")
        for item in caso["observar"]:
            print(f"    - {item}")
        print()

    print("# Fim. Nenhum veredito é emitido por este script.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

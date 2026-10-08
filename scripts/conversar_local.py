"""REPL local do M2 — conversa com o motor completo e o produtor Anthropic real.

**Uso manual, por decisão humana.** Cada mensagem é **uma chamada real** ao
provedor e consome tokens. Não é teste, não roda em CI e não prova qualidade.

    python scripts/conversar_local.py --janela-idempotencia-segundos <s> \\
        --limiar-recencia-dias <d> --model <modelo> --max-tokens <n> --timeout <s>

`--janela-idempotencia-segundos` e `--limiar-recencia-dias` são **obrigatórios e
sem default**: o valor do limiar continua decisão aberta do projeto.

O REPL é o adaptador de canal: o relógio vivo (`datetime.now`) e os
identificadores (`uuid4`) pertencem a ele, não ao motor. A persistência é **em
memória** — nada sobrevive ao fim do processo.

Saídas: `Bot: <texto>` em stdout; alertas, resumo ao responsável e linhas de
status (`[desfecho=… estado=…]`) em stderr. Sai em EOF, `sair` ou Ctrl+C.

**Segurança.** A credencial é resolvida pelo **próprio SDK**, a partir do
ambiente do operador. Este script **não** lê variável de credencial, **não**
imprime chave e **não** pede que ela seja colada. Se faltar, falha claramente.
Use apenas mensagens fictícias: o repositório é público.
"""

from __future__ import annotations

import argparse
import sys
import uuid
from collections.abc import Callable, Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from casa77_sdr.motor_deps import DependenciasMotor, carregar_base_motor  # noqa: E402
from casa77_sdr.normalization import EntradaMensagem  # noqa: E402
from casa77_sdr.orchestrator import (  # noqa: E402
    DesfechoCiclo,
    processar_mensagem,
)
from casa77_sdr.persistence import PersistenciaEmMemoria  # noqa: E402

PROMPT = RAIZ / "prompts" / "prompt-interpretacao.md"


def _novo_id() -> str:
    return uuid.uuid4().hex


def conversar(
    linhas: Iterator[str],
    escrever: Callable[[str], None],
    deps: DependenciasMotor,
    *,
    canal: str,
    contato: str,
) -> None:
    """Laço do REPL: uma linha = um ciclo; status vai a `escrever`."""
    for linha in linhas:
        texto = linha.strip()
        if texto.lower() == "sair":
            return
        if not texto:
            continue
        entrada = EntradaMensagem(
            canal=canal,
            contato=contato,
            mensagem=texto,
            recebida_em=datetime.now(UTC),
            id_mensagem_canal=_novo_id(),
            id_atendimento=None,
        )
        resultado = processar_mensagem(entrada, deps, gerar_id=_novo_id)
        estado = resultado.estado_final.value if resultado.estado_final else None
        escrever(f"  [desfecho={resultado.desfecho.value} estado={estado}]")
        if resultado.desfecho is DesfechoCiclo.SILENCIOSA:
            escrever("  (bot sem texto aprovado para esta situação)")


def _linhas_do_terminal() -> Iterator[str]:
    while True:
        try:
            yield input("Você: ")
        except EOFError:
            return


def main() -> int:
    analisador = argparse.ArgumentParser(
        description="REPL local do M2. Chamadas reais ao provedor; consome tokens."
    )
    analisador.add_argument("--janela-idempotencia-segundos", required=True, type=float)
    analisador.add_argument("--limiar-recencia-dias", required=True, type=float)
    analisador.add_argument("--model", required=True, help="identificador do modelo")
    analisador.add_argument("--max-tokens", required=True, type=int)
    analisador.add_argument("--timeout", required=True, type=float)
    analisador.add_argument("--contato", default="contato-local")
    analisador.add_argument("--canal", default="local")
    argumentos = analisador.parse_args()

    try:
        import anthropic
    except ImportError:
        print("SDK `anthropic` não instalado.", file=sys.stderr)
        return 1

    cliente = anthropic.Anthropic()
    # Presença apenas — o valor da credencial nunca é lido nem impresso.
    if (
        cliente.api_key is None
        and cliente.auth_token is None
        and cliente.custom_auth is None
    ):
        print(
            "Credencial da Anthropic não encontrada. Configure a variável de "
            "ambiente ANTHROPIC_API_KEY no seu ambiente (fora deste repositório) "
            "e rode de novo. Não cole a chave aqui, não a versione e não a "
            "adicione à CI.",
            file=sys.stderr,
        )
        return 1

    from casa77_sdr.interpretation_anthropic import AdaptadorAnthropic

    produtor = AdaptadorAnthropic(
        cliente,
        model=argumentos.model,
        max_tokens=argumentos.max_tokens,
        timeout=argumentos.timeout,
    )

    def tentar_alerta(**campos: object) -> None:
        print(
            f"[ALERTA] categoria={campos.get('categoria')} "
            f"pendente_preservado={campos.get('pendente_preservado')} "
            f"correlacao={campos.get('correlacao')}",
            file=sys.stderr,
        )

    def enviar_mensagem(canal: str, contato: str, texto: str) -> None:
        print(f"Bot: {texto}")

    def entregar_resumo(resumo: str) -> None:
        print(f"[RESUMO PARA O RESPONSÁVEL]\n{resumo}", file=sys.stderr)

    deps = DependenciasMotor(
        base_motor=carregar_base_motor(RAIZ),
        persistencia=PersistenciaEmMemoria(),
        produtor=produtor,
        prompt_sistema=PROMPT.read_text(encoding="utf-8"),
        janela_idempotencia=timedelta(seconds=argumentos.janela_idempotencia_segundos),
        limiar_recencia=timedelta(days=argumentos.limiar_recencia_dias),
        calendario_integrado=False,
        tentar_alerta=tentar_alerta,
        enviar_mensagem=enviar_mensagem,
        entregar_resumo=entregar_resumo,
    )

    def escrever_status(linha: str) -> None:
        print(linha, file=sys.stderr)

    try:
        conversar(
            _linhas_do_terminal(),
            escrever_status,
            deps,
            canal=argumentos.canal,
            contato=argumentos.contato,
        )
    except KeyboardInterrupt:
        print("", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

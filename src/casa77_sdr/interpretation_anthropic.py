"""Adaptador **Anthropic** do produtor não determinístico da etapa 4.

**Único módulo do projeto que importa `anthropic`.** Ele implementa o
`ProdutorTextoEstruturado` de `interpretation_llm.py` e nada mais: monta uma
chamada, seleciona o bloco de texto e devolve uma `str`. Ele **não** conhece
`Interpretacao`, **não** traduz payload, **não** canonicaliza, **não** decide
nada comercial e **não** lê `knowledge/**`.

**Zero retry.** O SDK da Anthropic reexecuta a chamada por padrão; aqui o
comportamento é desligado explicitamente com `max_retries=0`, porque
**N-b-M7** exige zero retry, zero *fallback*, zero cache e zero fila: uma
chamada, um *timeout*, um desfecho.

**Nenhum segredo é lido aqui.** O cliente do SDK é **injetado** — o adaptador
não constrói cliente, não lê `os.environ`, não lê `ANTHROPIC_API_KEY`, não toca
o filesystem e não faz logging da mensagem nem do payload. Onde a credencial
vive é decisão do operador, na raiz de composição.

**Nenhum tipo do SDK vaza**: a fronteira troca `str` e
`FalhaProdutorInterpretacao`, nunca objeto de resposta do provedor.

`model`, `max_tokens` e `timeout` são **injetados e validados**: o domínio não
contém esses valores, e `claude-sonnet-5` é o valor **recomendado para a raiz de
composição**, não uma constante deste módulo.
"""

from __future__ import annotations

from typing import Any

import anthropic

from casa77_sdr.interpretation_llm import (
    FalhaProdutorInterpretacao,
    MotivoFalhaProdutor,
)

__all__ = ["AdaptadorAnthropic"]

#: `stop_reason` que autorizam a leitura do conteúdo. Vocabulário **fechado**:
#: qualquer outro valor — inclusive um futuro valor novo do provedor — falha
#: fechada, em vez de ampliar silenciosamente o contrato.
_STOP_REASON_CONCLUSIVO: frozenset[str] = frozenset({"end_turn", "stop_sequence"})

#: `stop_reason` com desfecho próprio e nomeado.
_STOP_REASON_DE_FALHA: dict[str, MotivoFalhaProdutor] = {
    "refusal": MotivoFalhaProdutor.RECUSA_DO_MODELO,
    "max_tokens": MotivoFalhaProdutor.TRUNCADO,
}


def _falha(motivo: MotivoFalhaProdutor) -> FalhaProdutorInterpretacao:
    return FalhaProdutorInterpretacao(motivo)


class AdaptadorAnthropic:
    """Produtor de texto estruturado sobre a Messages API da Anthropic.

    Implementa `ProdutorTextoEstruturado` estruturalmente — sem herdar do
    `Protocol` e sem que nenhum tipo do SDK apareça na assinatura pública.
    """

    def __init__(
        self,
        cliente: Any,
        *,
        model: str,
        max_tokens: int,
        timeout: float,
    ) -> None:
        if not isinstance(model, str) or not model.strip():
            raise ValueError("model precisa ser um identificador de modelo não vazio")
        if isinstance(max_tokens, bool) or not isinstance(max_tokens, int):
            raise TypeError("max_tokens precisa ser inteiro")
        if max_tokens <= 0:
            raise ValueError("max_tokens precisa ser positivo")
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
            raise TypeError("timeout precisa ser numérico")
        if timeout <= 0:
            raise ValueError("timeout precisa ser positivo")

        self._cliente = cliente
        self._model = model
        self._max_tokens = max_tokens
        self._timeout = float(timeout)

    # ----------------------------------------------------------------
    # Montagem da chamada
    # ----------------------------------------------------------------

    def montar_argumentos(
        self,
        *,
        prompt_sistema: str,
        mensagem: str,
        schema: dict[str, Any],
    ) -> dict[str, Any]:
        """Monta o dicionário de argumentos da chamada, **sem executá-la**.

        Existe como superfície própria para que a auditoria possa **inspecionar
        o que é enviado** sem rede: presença e forma de `output_config.format`,
        `thinking` desabilitado, turno único de usuário e **ausência** de
        `temperature`, `top_p`, `top_k`, `tools`, *streaming*, *citations*,
        *prefill*, cache e histórico conversacional.

        A mensagem do interessado é o **único** conteúdo do turno `user`, e o
        prompt de sistema declara que esse conteúdo é **dado, nunca instrução**.
        """
        return {
            "model": self._model,
            "max_tokens": self._max_tokens,
            "thinking": {"type": "disabled"},
            "system": prompt_sistema,
            "messages": [{"role": "user", "content": mensagem}],
            "output_config": {
                "format": {"type": "json_schema", "schema": schema}
            },
        }

    # ----------------------------------------------------------------
    # Execução
    # ----------------------------------------------------------------

    def produzir(
        self,
        *,
        prompt_sistema: str,
        mensagem: str,
        schema: dict[str, Any],
    ) -> str:
        """Uma chamada, um desfecho. Devolve o **texto JSON** da saída.

        :raises FalhaProdutorInterpretacao: qualquer desfecho que não seja um
            único bloco de texto sob `stop_reason` conclusivo.
        """
        argumentos = self.montar_argumentos(
            prompt_sistema=prompt_sistema, mensagem=mensagem, schema=schema
        )
        resposta = self._chamar(argumentos)
        self._verificar_stop_reason(resposta)
        return self._selecionar_texto(resposta)

    def _chamar(self, argumentos: dict[str, Any]) -> Any:
        try:
            cliente = self._cliente.with_options(
                max_retries=0, timeout=self._timeout
            )
            return cliente.messages.create(**argumentos)
        except anthropic.APITimeoutError:
            # `from None` em todos os ramos: nenhuma mensagem do provedor,
            # nenhum payload e nenhuma credencial atravessam a fronteira.
            raise _falha(MotivoFalhaProdutor.TIMEOUT) from None
        except anthropic.APIConnectionError:
            raise _falha(MotivoFalhaProdutor.ERRO_DE_TRANSPORTE) from None
        except anthropic.APIStatusError:
            raise _falha(MotivoFalhaProdutor.ERRO_DO_PROVEDOR) from None
        except anthropic.AnthropicError:
            raise _falha(MotivoFalhaProdutor.ERRO_DO_PROVEDOR) from None

    @staticmethod
    def _verificar_stop_reason(resposta: Any) -> None:
        """`stop_reason` **primeiro**, conteúdo depois.

        Nunca fazer *parsing* de um payload que o `stop_reason` já invalidou:
        recusa e truncamento chegam com status 200 e tokens cobrados, e
        aproveitar payload parcial é proibido.
        """
        stop_reason = getattr(resposta, "stop_reason", None)
        motivo = _STOP_REASON_DE_FALHA.get(stop_reason)  # type: ignore[arg-type]
        if motivo is not None:
            raise _falha(motivo)
        if stop_reason not in _STOP_REASON_CONCLUSIVO:
            raise _falha(MotivoFalhaProdutor.ERRO_DO_PROVEDOR)

    @staticmethod
    def _selecionar_texto(resposta: Any) -> str:
        """Seleciona **o** bloco `text` — nunca `content[0]`.

        Blocos de outros tipos são **ignorados** para seleção: nunca
        concatenados, nunca inspecionados e nunca logados. Zero bloco de texto
        e mais de um bloco de texto são desfechos **distintos**, ambos fechados:
        escolher o maior, o último ou concatenar seria inventar conteúdo.
        """
        conteudo = getattr(resposta, "content", None)
        if not isinstance(conteudo, (list, tuple)):
            raise _falha(MotivoFalhaProdutor.SEM_BLOCO_ESTRUTURADO)
        blocos = [
            bloco for bloco in conteudo if getattr(bloco, "type", None) == "text"
        ]
        if not blocos:
            raise _falha(MotivoFalhaProdutor.SEM_BLOCO_ESTRUTURADO)
        if len(blocos) > 1:
            raise _falha(MotivoFalhaProdutor.MULTIPLOS_BLOCOS_ESTRUTURADOS)
        texto = getattr(blocos[0], "text", None)
        if not isinstance(texto, str):
            raise _falha(MotivoFalhaProdutor.SEM_BLOCO_ESTRUTURADO)
        return texto

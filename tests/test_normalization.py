"""Testes da normalização de entrada e da chave de idempotência (3B.4).

Fixtures totalmente artificiais: canais, contatos, identificadores e
mensagens claramente fictícios, sem dado pessoal real, sem valor comercial
e sem relação com a operação real.

Os testes provam que esta camada apenas normaliza e deriva a chave: nada
aqui consulta persistência, decide duplicidade, aplica transição ou
interpreta o que a mensagem significa.
"""

from __future__ import annotations

import ast
import inspect
from datetime import datetime, timedelta, timezone, tzinfo
from pathlib import Path

import pytest

from casa77_sdr.normalization import (
    EntradaInvalida,
    EntradaMensagem,
    MensagemVazia,
    OrigemChave,
    normalizar_entrada,
)

RAIZ = Path(__file__).resolve().parents[1]
MODULO_NORMALIZACAO = RAIZ / "src" / "casa77_sdr" / "normalization.py"

JANELA = timedelta(minutes=5)
INSTANTE = datetime(2020, 1, 1, 12, 0, tzinfo=timezone.utc)


def entrada_ficticia(**ajustes: object) -> EntradaMensagem:
    """Entrada artificial; `ajustes` sobrescreve campos por palavra-chave."""
    campos: dict[str, object] = {
        "canal": "canal-teste",
        "contato": "contato-fake-1",
        "mensagem": "Mensagem artificial de teste",
        "recebida_em": INSTANTE,
        "id_mensagem_canal": None,
        "id_atendimento": None,
    }
    campos.update(ajustes)
    return EntradaMensagem(**campos)  # type: ignore[arg-type]


class FusoSemDeslocamento(tzinfo):
    """`tzinfo` presente cujo deslocamento é indefinido — fuso não efetivo."""

    def utcoffset(self, dt: datetime | None) -> timedelta | None:
        return None

    def dst(self, dt: datetime | None) -> timedelta | None:
        return None

    def tzname(self, dt: datetime | None) -> str | None:
        return None


# 1. Identificador do canal presente — origem confiável


def test_id_do_canal_produz_origem_identificador_canal() -> None:
    resultado = normalizar_entrada(
        entrada_ficticia(id_mensagem_canal="id-canal-fake-1"), JANELA
    )

    assert resultado.origem_chave is OrigemChave.IDENTIFICADOR_CANAL


def test_mesmo_id_do_canal_com_texto_diferente_produz_a_mesma_chave() -> None:
    """O identificador do canal é suficiente sozinho: o texto não o altera."""
    primeira = normalizar_entrada(
        entrada_ficticia(
            id_mensagem_canal="id-canal-fake-1", mensagem="Primeira redação"
        ),
        JANELA,
    )
    segunda = normalizar_entrada(
        entrada_ficticia(
            id_mensagem_canal="id-canal-fake-1", mensagem="Redação completamente outra"
        ),
        JANELA,
    )

    assert primeira.chave_idempotencia == segunda.chave_idempotencia
    assert primeira.mensagem_normalizada != segunda.mensagem_normalizada


def test_mesmo_id_do_canal_com_horario_diferente_produz_a_mesma_chave() -> None:
    primeira = normalizar_entrada(
        entrada_ficticia(id_mensagem_canal="id-canal-fake-1"), JANELA
    )
    segunda = normalizar_entrada(
        entrada_ficticia(
            id_mensagem_canal="id-canal-fake-1",
            recebida_em=datetime(2021, 6, 30, 23, 45, tzinfo=timezone.utc),
        ),
        JANELA,
    )

    assert primeira.chave_idempotencia == segunda.chave_idempotencia


def test_ids_do_canal_diferentes_produzem_chaves_diferentes() -> None:
    primeira = normalizar_entrada(
        entrada_ficticia(id_mensagem_canal="id-canal-fake-1"), JANELA
    )
    segunda = normalizar_entrada(
        entrada_ficticia(id_mensagem_canal="id-canal-fake-2"), JANELA
    )

    assert primeira.chave_idempotencia != segunda.chave_idempotencia


# 2. Fallback composto — origem heurística


def test_id_ausente_produz_origem_composta() -> None:
    resultado = normalizar_entrada(entrada_ficticia(), JANELA)

    assert resultado.origem_chave is OrigemChave.COMPOSTA


def test_mesmo_balde_mesmo_canal_contato_e_mensagem_produz_a_mesma_chave() -> None:
    primeira = normalizar_entrada(entrada_ficticia(), JANELA)
    segunda = normalizar_entrada(
        entrada_ficticia(recebida_em=datetime(2020, 1, 1, 12, 4, tzinfo=timezone.utc)),
        JANELA,
    )

    assert primeira.chave_idempotencia == segunda.chave_idempotencia


def test_balde_temporal_diferente_produz_chave_diferente() -> None:
    """Fora da janela, a mesma frase é mensagem nova, não duplicata."""
    primeira = normalizar_entrada(entrada_ficticia(), JANELA)
    segunda = normalizar_entrada(
        entrada_ficticia(recebida_em=datetime(2020, 1, 1, 12, 7, tzinfo=timezone.utc)),
        JANELA,
    )

    assert primeira.chave_idempotencia != segunda.chave_idempotencia


def test_mesmo_instante_em_fusos_diferentes_produz_a_mesma_chave() -> None:
    """O balde é calculado em UTC: o fuso de origem não muda a identidade."""
    em_utc = normalizar_entrada(entrada_ficticia(), JANELA)
    em_outro_fuso = normalizar_entrada(
        entrada_ficticia(
            recebida_em=datetime(
                2020, 1, 1, 9, 0, tzinfo=timezone(timedelta(hours=-3))
            )
        ),
        JANELA,
    )

    assert em_utc.chave_idempotencia == em_outro_fuso.chave_idempotencia


def test_contatos_diferentes_produzem_chaves_diferentes() -> None:
    primeira = normalizar_entrada(entrada_ficticia(), JANELA)
    segunda = normalizar_entrada(entrada_ficticia(contato="contato-fake-2"), JANELA)

    assert primeira.chave_idempotencia != segunda.chave_idempotencia


def test_canais_diferentes_produzem_chaves_diferentes() -> None:
    primeira = normalizar_entrada(entrada_ficticia(), JANELA)
    segunda = normalizar_entrada(entrada_ficticia(canal="canal-teste-2"), JANELA)

    assert primeira.chave_idempotencia != segunda.chave_idempotencia


def test_id_atendimento_nao_influencia_a_chave_composta() -> None:
    """O identificador do atendimento é referência de consulta, não identidade."""
    sem_id = normalizar_entrada(entrada_ficticia(), JANELA)
    com_id = normalizar_entrada(
        entrada_ficticia(id_atendimento="atendimento-fake-1"), JANELA
    )

    assert sem_id.chave_idempotencia == com_id.chave_idempotencia


# 3. Normalização técnica e conservadora


def test_diferencas_apenas_de_espaco_produzem_a_mesma_normalizacao_e_chave() -> None:
    primeira = normalizar_entrada(entrada_ficticia(), JANELA)
    segunda = normalizar_entrada(
        entrada_ficticia(mensagem="  Mensagem   artificial\tde\nteste  "), JANELA
    )

    assert primeira.mensagem_normalizada == segunda.mensagem_normalizada
    assert primeira.chave_idempotencia == segunda.chave_idempotencia


def test_equivalencia_nfkc_produz_a_mesma_normalizacao_e_chave() -> None:
    """Formas compatíveis convergem: `ﬁ` (U+FB01) e `fi` são o mesmo texto."""
    composta = normalizar_entrada(entrada_ficticia(mensagem="Teste ﬁnal"), JANELA)
    simples = normalizar_entrada(entrada_ficticia(mensagem="Teste final"), JANELA)

    assert composta.mensagem_normalizada == simples.mensagem_normalizada
    assert composta.chave_idempotencia == simples.chave_idempotencia


def test_normalizacao_preserva_caixa_acento_pontuacao_e_emoji() -> None:
    bruta = "  Olá,  ÁRVORE!!  Tudo   certo? 🎉  "

    resultado = normalizar_entrada(entrada_ficticia(mensagem=bruta), JANELA)

    assert resultado.mensagem_normalizada == "Olá, ÁRVORE!! Tudo certo? 🎉"


def test_mensagens_que_diferem_apenas_por_caixa_continuam_diferentes() -> None:
    maiuscula = normalizar_entrada(entrada_ficticia(mensagem="Teste"), JANELA)
    minuscula = normalizar_entrada(entrada_ficticia(mensagem="teste"), JANELA)

    assert maiuscula.mensagem_normalizada != minuscula.mensagem_normalizada
    assert maiuscula.chave_idempotencia != minuscula.chave_idempotencia


def test_mensagens_que_diferem_por_acento_continuam_diferentes() -> None:
    com_acento = normalizar_entrada(entrada_ficticia(mensagem="avó"), JANELA)
    sem_acento = normalizar_entrada(entrada_ficticia(mensagem="avo"), JANELA)

    assert com_acento.mensagem_normalizada != sem_acento.mensagem_normalizada
    assert com_acento.chave_idempotencia != sem_acento.chave_idempotencia


# 4. Mensagem sem conteúdo


def test_mensagem_vazia_e_recusada() -> None:
    with pytest.raises(MensagemVazia):
        normalizar_entrada(entrada_ficticia(mensagem=""), JANELA)


def test_mensagem_somente_com_espacos_e_recusada() -> None:
    with pytest.raises(MensagemVazia):
        normalizar_entrada(entrada_ficticia(mensagem="   \t\n  "), JANELA)


# 5. Contrato inválido


def test_instante_sem_fuso_e_recusado() -> None:
    with pytest.raises(EntradaInvalida):
        normalizar_entrada(
            entrada_ficticia(recebida_em=datetime(2020, 1, 1, 12, 0)), JANELA
        )


def test_instante_com_fuso_sem_deslocamento_efetivo_e_recusado() -> None:
    """`tzinfo` preenchido não basta: sem `utcoffset` não há conversão para UTC."""
    sem_deslocamento = datetime(2020, 1, 1, 12, 0, tzinfo=FusoSemDeslocamento())

    with pytest.raises(EntradaInvalida):
        normalizar_entrada(entrada_ficticia(recebida_em=sem_deslocamento), JANELA)


def test_janela_zero_e_recusada() -> None:
    with pytest.raises(EntradaInvalida):
        normalizar_entrada(entrada_ficticia(), timedelta(0))


def test_janela_negativa_e_recusada() -> None:
    with pytest.raises(EntradaInvalida):
        normalizar_entrada(entrada_ficticia(), timedelta(minutes=-5))


def test_canal_vazio_e_recusado() -> None:
    with pytest.raises(EntradaInvalida):
        normalizar_entrada(entrada_ficticia(canal="   "), JANELA)


def test_contato_vazio_e_recusado() -> None:
    with pytest.raises(EntradaInvalida):
        normalizar_entrada(entrada_ficticia(contato=""), JANELA)


def test_id_do_canal_vazio_quando_fornecido_e_recusado() -> None:
    """Ausente é normal; presente e vazio é defeito de contrato."""
    with pytest.raises(EntradaInvalida):
        normalizar_entrada(entrada_ficticia(id_mensagem_canal="  "), JANELA)


def test_id_do_atendimento_vazio_quando_fornecido_e_recusado() -> None:
    with pytest.raises(EntradaInvalida):
        normalizar_entrada(entrada_ficticia(id_atendimento=""), JANELA)


def test_excecoes_nao_reproduzem_mensagem_contato_nem_identificador() -> None:
    with pytest.raises(EntradaInvalida) as erro_contato:
        normalizar_entrada(entrada_ficticia(contato="   "), JANELA)
    with pytest.raises(MensagemVazia) as erro_mensagem:
        normalizar_entrada(
            entrada_ficticia(
                mensagem="   ", contato="contato-fake-1", id_atendimento="atendimento-fake-1"
            ),
            JANELA,
        )

    assert "contato-fake-1" not in str(erro_contato.value)
    assert "contato-fake-1" not in str(erro_mensagem.value)
    assert "atendimento-fake-1" not in str(erro_mensagem.value)


# 6. Composição inequívoca e opacidade da chave


def test_composicao_resiste_a_ambiguidade_de_delimitadores() -> None:
    """Concatenação ingênua colidiria; o prefixo de comprimento impede isso."""
    primeira = normalizar_entrada(
        entrada_ficticia(canal="canal-teste|x", contato="y-fake"), JANELA
    )
    segunda = normalizar_entrada(
        entrada_ficticia(canal="canal-teste", contato="x|y-fake"), JANELA
    )

    assert primeira.chave_idempotencia != segunda.chave_idempotencia


def test_chave_composta_nao_expoe_contato_nem_mensagem() -> None:
    mensagem = "Mensagem artificial reconhecivel"

    resultado = normalizar_entrada(entrada_ficticia(mensagem=mensagem), JANELA)

    assert "contato-fake-1" not in resultado.chave_idempotencia
    assert "canal-teste" not in resultado.chave_idempotencia
    assert mensagem not in resultado.chave_idempotencia
    assert "2020" not in resultado.chave_idempotencia


def test_chave_por_identificador_nao_expoe_o_id_bruto() -> None:
    resultado = normalizar_entrada(
        entrada_ficticia(id_mensagem_canal="id-canal-fake-1"), JANELA
    )

    assert "id-canal-fake-1" not in resultado.chave_idempotencia
    assert "contato-fake-1" not in resultado.chave_idempotencia


def test_origem_da_chave_e_distinguivel_no_valor_da_chave() -> None:
    """Domínios separados impedem colisão entre os dois modos."""
    por_identificador = normalizar_entrada(
        entrada_ficticia(id_mensagem_canal="id-canal-fake-1"), JANELA
    )
    composta = normalizar_entrada(entrada_ficticia(), JANELA)

    assert por_identificador.chave_idempotencia.startswith(
        f"{OrigemChave.IDENTIFICADOR_CANAL.value}:"
    )
    assert composta.chave_idempotencia.startswith(f"{OrigemChave.COMPOSTA.value}:")
    assert por_identificador.chave_idempotencia != composta.chave_idempotencia


# 7. Pureza e determinismo


def test_entrada_nao_e_mutada() -> None:
    entrada = entrada_ficticia(mensagem="  Texto   com  espaços  ")
    original = entrada_ficticia(mensagem="  Texto   com  espaços  ")

    normalizar_entrada(entrada, JANELA)

    assert entrada == original


def test_chamadas_repetidas_produzem_exatamente_a_mesma_saida() -> None:
    entrada = entrada_ficticia()

    primeira = normalizar_entrada(entrada, JANELA)
    segunda = normalizar_entrada(entrada, JANELA)

    assert primeira == segunda


def test_janela_de_idempotencia_nao_tem_valor_padrao() -> None:
    """A largura da janela é decisão de configuração, não desta camada."""
    parametro = inspect.signature(normalizar_entrada).parameters["janela_idempotencia"]

    assert parametro.default is inspect.Parameter.empty


# 8. Sem persistência, regras, base, rede, filesystem ou LLM


def test_normalizacao_sem_import_proibido() -> None:
    permitidos = {
        "__future__",
        "dataclasses",
        "datetime",
        "enum",
        "hashlib",
        "unicodedata",
    }
    proibidos = {
        "casa77_sdr",
        "random",
        "secrets",
        "time",
        "logging",
        "os",
        "io",
        "pathlib",
        "sqlite3",
        "json",
        "http",
        "urllib",
        "socket",
        "requests",
        "anthropic",
        "openai",
    }

    arvore = ast.parse(MODULO_NORMALIZACAO.read_text(encoding="utf-8"))
    nomes = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            nomes.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            nomes.add(no.module)

    raizes = {nome.split(".")[0] for nome in nomes}
    assert raizes <= permitidos
    assert not (raizes & proibidos)
    assert not [nome for nome in nomes if "persistence" in nome or "rules" in nome]
    assert not [nome for nome in nomes if "knowledge" in nome]

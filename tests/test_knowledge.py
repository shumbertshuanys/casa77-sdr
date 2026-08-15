"""Testes do carregador da base de conhecimento.

Nenhum teste altera `knowledge/casa77.yaml`. Os casos de erro usam arquivos
temporários do pytest. Os valores comerciais reais nunca aparecem como
expectativa fixa: o que se testa é estrutura, tipo e ausência de constante
comercial no código.
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import Any

import pytest
import yaml

from casa77_sdr.knowledge import KnowledgeError, load_knowledge

RAIZ = Path(__file__).resolve().parents[1]
YAML_REAL = RAIZ / "knowledge" / "casa77.yaml"
MODULO_CARREGADOR = RAIZ / "src" / "casa77_sdr" / "knowledge.py"

CAMINHOS_OBRIGATORIOS: tuple[tuple[str, ...], ...] = (
    ("versao",),
    ("empresa",),
    ("empresa", "nome"),
    ("eventos",),
    ("eventos", "aceitos"),
    ("eventos", "nao_aceitos"),
    ("eventos", "datas_nao_aceitas"),
    ("capacidade",),
    ("capacidade", "convidados_sentados"),
    ("capacidade", "formato_coquetel"),
    ("precos",),
    ("precos", "moeda"),
    ("precos", "pacotes"),
    ("processo_comercial",),
    ("processo_comercial", "responsavel"),
    ("processo_comercial", "responsavel", "nome"),
)


def base_minima() -> dict[str, Any]:
    """Estrutura mínima válida com valores inventados, não comerciais."""
    return {
        "versao": "0.0-teste",
        "empresa": {"nome": "Espaço de Teste"},
        "eventos": {
            "aceitos": ["tipo-a", "tipo-b"],
            "nao_aceitos": ["tipo-vetado-teste"],
            "datas_nao_aceitas": ["data-bloqueada-teste"],
        },
        "capacidade": {"convidados_sentados": 7, "formato_coquetel": 9},
        "precos": {
            "moeda": "XTS",
            "pacotes": [{"codigo": "PACOTE_TESTE", "valor": 123}],
        },
        "processo_comercial": {"responsavel": {"nome": "Responsável de Teste"}},
    }


def escrever_yaml(tmp_path: Path, dados: Any) -> Path:
    destino = tmp_path / "base.yaml"
    destino.write_text(
        yaml.safe_dump(dados, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    return destino


def sem_caminho(dados: dict[str, Any], caminho: tuple[str, ...]) -> dict[str, Any]:
    """Cópia da estrutura sem o campo indicado."""
    copia = yaml.safe_load(yaml.safe_dump(dados, allow_unicode=True))
    alvo = copia
    for chave in caminho[:-1]:
        alvo = alvo[chave]
    del alvo[caminho[-1]]
    return copia


def definir(
    dados: dict[str, Any], caminho: tuple[str, ...], valor: Any
) -> dict[str, Any]:
    """Cópia da estrutura com o campo indicado substituído."""
    copia = yaml.safe_load(yaml.safe_dump(dados, allow_unicode=True))
    alvo = copia
    for chave in caminho[:-1]:
        alvo = alvo[chave]
    alvo[caminho[-1]] = valor
    return copia


# 1. Estrutura mínima válida


def test_carrega_estrutura_minima_valida(tmp_path: Path) -> None:
    esperado = base_minima()
    caminho = escrever_yaml(tmp_path, esperado)

    dados = load_knowledge(caminho)

    assert dados == esperado


def test_aceita_caminho_como_texto(tmp_path: Path) -> None:
    caminho = escrever_yaml(tmp_path, base_minima())

    assert load_knowledge(str(caminho)) == base_minima()


# 2. YAML real do repositório


def test_carrega_yaml_real() -> None:
    dados = load_knowledge(YAML_REAL)

    assert isinstance(dados, dict)
    assert isinstance(dados["versao"], str) and dados["versao"].strip()
    assert isinstance(dados["empresa"]["nome"], str)
    assert isinstance(dados["eventos"]["aceitos"], list)
    assert isinstance(dados["capacidade"]["convidados_sentados"], int)
    assert isinstance(dados["capacidade"]["formato_coquetel"], int)
    assert isinstance(dados["precos"]["moeda"], str)
    assert isinstance(dados["precos"]["pacotes"], list) and dados["precos"]["pacotes"]
    assert isinstance(dados["processo_comercial"]["responsavel"]["nome"], str)


def test_yaml_real_preserva_campos_pendentes() -> None:
    """Campo `null` continua `null` — o carregador não completa lacuna."""
    dados = load_knowledge(YAML_REAL)
    cru = yaml.safe_load(YAML_REAL.read_text(encoding="utf-8"))

    assert dados["materiais"] == cru["materiais"]
    assert dados["estrutura"]["suite_noiva"]["valor"] is cru["estrutura"][
        "suite_noiva"
    ]["valor"]


# 3. Falha de leitura do arquivo


def test_arquivo_inexistente(tmp_path: Path) -> None:
    ausente = tmp_path / "nao-existe.yaml"

    with pytest.raises(KnowledgeError) as erro:
        load_knowledge(ausente)

    assert "não encontrada" in str(erro.value)
    assert str(ausente) in str(erro.value)


def test_conteudo_nao_decodificavel_em_utf8(tmp_path: Path) -> None:
    """Bytes inválidos em UTF-8 viram `KnowledgeError`, não erro cru."""
    arquivo = tmp_path / "bytes-invalidos.yaml"
    arquivo.write_bytes(b"\xff\xfe\xfa")

    with pytest.raises(KnowledgeError) as erro:
        load_knowledge(arquivo)

    assert "Não foi possível ler" in str(erro.value)
    assert str(arquivo) in str(erro.value)
    assert isinstance(erro.value.__cause__, UnicodeDecodeError)


# 4. Sintaxe inválida


def test_sintaxe_yaml_invalida(tmp_path: Path) -> None:
    caminho = tmp_path / "quebrado.yaml"
    caminho.write_text("versao: '1.0\n  empresa: [\n", encoding="utf-8")

    with pytest.raises(KnowledgeError) as erro:
        load_knowledge(caminho)

    assert "Sintaxe YAML inválida" in str(erro.value)
    assert erro.value.__cause__ is not None


def test_recusa_tag_python_insegura(tmp_path: Path) -> None:
    """`safe_load` não instancia objeto arbitrário vindo do arquivo."""
    caminho = tmp_path / "inseguro.yaml"
    caminho.write_text(
        "versao: !!python/object/apply:os.system ['echo oi']\n", encoding="utf-8"
    )

    with pytest.raises(KnowledgeError) as erro:
        load_knowledge(caminho)

    assert "Sintaxe YAML inválida" in str(erro.value)


# 5. Raiz que não é mapeamento


@pytest.mark.parametrize("conteudo", ["- um\n- dois\n", "apenas um texto\n", ""])
def test_raiz_nao_e_mapeamento(tmp_path: Path, conteudo: str) -> None:
    caminho = tmp_path / "raiz.yaml"
    caminho.write_text(conteudo, encoding="utf-8")

    with pytest.raises(KnowledgeError) as erro:
        load_knowledge(caminho)

    assert "A raiz" in str(erro.value)
    assert "mapeamento" in str(erro.value)


# 6. Campo obrigatório ausente


@pytest.mark.parametrize("caminho", CAMINHOS_OBRIGATORIOS, ids=".".join)
def test_campo_obrigatorio_ausente(tmp_path: Path, caminho: tuple[str, ...]) -> None:
    arquivo = escrever_yaml(tmp_path, sem_caminho(base_minima(), caminho))

    with pytest.raises(KnowledgeError) as erro:
        load_knowledge(arquivo)

    assert "Campo obrigatório ausente" in str(erro.value)
    assert ".".join(caminho) in str(erro.value)


# 7. Campo com tipo incorreto


@pytest.mark.parametrize(
    ("caminho", "valor", "esperado"),
    [
        (("empresa",), "texto no lugar de mapeamento", "mapeamento"),
        (("eventos", "aceitos"), {"a": 1}, "lista"),
        (("capacidade", "convidados_sentados"), "sete", "número inteiro"),
        (("capacidade", "formato_coquetel"), 9.5, "número inteiro"),
        (("capacidade", "convidados_sentados"), True, "número inteiro"),
        (("precos", "pacotes"), {"codigo": "X"}, "lista"),
        (("empresa", "nome"), 123, "string"),
        (("processo_comercial", "responsavel"), ["lista"], "mapeamento"),
    ],
)
def test_campo_com_tipo_incorreto(
    tmp_path: Path, caminho: tuple[str, ...], valor: Any, esperado: str
) -> None:
    arquivo = escrever_yaml(tmp_path, definir(base_minima(), caminho, valor))

    with pytest.raises(KnowledgeError) as erro:
        load_knowledge(arquivo)

    mensagem = str(erro.value)
    assert ".".join(caminho) in mensagem
    assert esperado in mensagem


# 8. String obrigatória vazia


@pytest.mark.parametrize(
    "caminho",
    [("versao",), ("empresa", "nome"), ("precos", "moeda"), ("processo_comercial", "responsavel", "nome")],
    ids=".".join,
)
@pytest.mark.parametrize("vazio", ["", "   "])
def test_string_obrigatoria_vazia(
    tmp_path: Path, caminho: tuple[str, ...], vazio: str
) -> None:
    arquivo = escrever_yaml(tmp_path, definir(base_minima(), caminho, vazio))

    with pytest.raises(KnowledgeError) as erro:
        load_knowledge(arquivo)

    assert "não pode ser vazio" in str(erro.value)
    assert ".".join(caminho) in str(erro.value)


# 9. Lista obrigatória vazia


def test_pacotes_lista_vazia(tmp_path: Path) -> None:
    arquivo = escrever_yaml(tmp_path, definir(base_minima(), ("precos", "pacotes"), []))

    with pytest.raises(KnowledgeError) as erro:
        load_knowledge(arquivo)

    assert "lista vazia" in str(erro.value)
    assert "precos.pacotes" in str(erro.value)


def test_lista_opcionalmente_vazia_e_aceita(tmp_path: Path) -> None:
    """`eventos.aceitos` só precisa ser lista; vazia é problema de conteúdo."""
    arquivo = escrever_yaml(tmp_path, definir(base_minima(), ("eventos", "aceitos"), []))

    assert load_knowledge(arquivo)["eventos"]["aceitos"] == []


# 10. O carregador não altera nada


def test_nao_altera_os_dados_carregados() -> None:
    cru = yaml.safe_load(YAML_REAL.read_text(encoding="utf-8"))

    dados = load_knowledge(YAML_REAL)

    assert dados == cru
    assert set(dados) == set(cru)


def test_nao_escreve_no_arquivo_real() -> None:
    conteudo = YAML_REAL.read_bytes()
    antes = hashlib.sha256(conteudo).hexdigest()

    load_knowledge(YAML_REAL)

    assert hashlib.sha256(YAML_REAL.read_bytes()).hexdigest() == antes


def test_nao_preenche_campo_ausente_opcional(tmp_path: Path) -> None:
    """O carregador devolve apenas o que estava no arquivo."""
    minima = base_minima()
    arquivo = escrever_yaml(tmp_path, minima)

    dados = load_knowledge(arquivo)

    assert set(dados) == set(minima)
    assert "pagamento" not in dados
    assert "horarios" not in dados


# 11. Os números comerciais vêm do arquivo, não do código


def test_valores_comerciais_vem_do_arquivo(tmp_path: Path) -> None:
    """Valores arbitrários no arquivo aparecem intactos na saída."""
    inventado = base_minima()
    inventado["capacidade"]["convidados_sentados"] = 3
    inventado["capacidade"]["formato_coquetel"] = 4
    inventado["precos"]["pacotes"] = [{"codigo": "UNICO", "valor": 1}]
    arquivo = escrever_yaml(tmp_path, inventado)

    dados = load_knowledge(arquivo)

    assert dados["capacidade"]["convidados_sentados"] == 3
    assert dados["capacidade"]["formato_coquetel"] == 4
    assert dados["precos"]["pacotes"] == [{"codigo": "UNICO", "valor": 1}]


def test_carregador_nao_tem_constante_comercial() -> None:
    """Invariante I06: nenhum valor comercial do YAML existe no código."""
    reais = load_knowledge(YAML_REAL)
    comerciais = {
        reais["capacidade"]["convidados_sentados"],
        reais["capacidade"]["formato_coquetel"],
    }
    for pacote in reais["precos"]["pacotes"]:
        comerciais.update(
            valor
            for chave, valor in pacote.items()
            if isinstance(valor, int) and not isinstance(valor, bool)
        )

    arvore = ast.parse(MODULO_CARREGADOR.read_text(encoding="utf-8"))
    literais = {
        no.value
        for no in ast.walk(arvore)
        if isinstance(no, ast.Constant)
        and isinstance(no.value, int)
        and not isinstance(no.value, bool)
    }

    assert not (literais & comerciais)

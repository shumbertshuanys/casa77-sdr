"""Testes da fronteira de leitura do futuro mapa de grupos de cobertura — `R2`.

Nenhum teste cria `knowledge/mapa-cobertura.yaml` e nenhum teste altera arquivo
do repositório: todo artefato lido nasce em `tmp_path`. Os *fixtures* são
**sintéticos** — os `Rxx` e os fragmentos são inventados — e **nenhuma
associação real de cobertura** aparece como conteúdo ou como expectativa.

A prova de que o carregador não abre fonte comercial paralela, não conhece
caminho padrão e não carrega mapa embutido é feita sobre a **AST do módulo de
produção**, seguindo o precedente de `test_response_index_load.py`.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from casa77_sdr.coverage_map import MapaCoberturaInvalido
from casa77_sdr.coverage_map_load import (
    MapaCoberturaIlegivel,
    carregar_mapa_cobertura,
)
from casa77_sdr.interpretation import AssuntoComercial

RAIZ = Path(__file__).resolve().parents[1]
MODULO = RAIZ / "src" / "casa77_sdr" / "coverage_map_load.py"
MODULO_INIT = RAIZ / "src" / "casa77_sdr" / "__init__.py"
MAPA_RESERVADO = RAIZ / "knowledge" / "mapa-cobertura.yaml"

PRECO = AssuntoComercial.PRECO_LOCACAO.value

VALORES_CANONICOS = [membro.value for membro in AssuntoComercial]

# `assuntos: []` **carrega** como YAML, mas o contrato estrutural o recusa: a
# totalidade de R2-1 exige os 54 valores declarados.
MAPA_VAZIO = "assuntos: []\n"


def yaml_total(blocos: dict[str, str] | None = None) -> str:
    """YAML de um mapa **total** — os 54 assuntos, por padrão com zero grupos.

    `blocos` substitui o trecho `grupos:` de um assunto específico. O conteúdo
    é **sintético**: nenhuma associação real de cobertura existe aqui.
    """
    blocos = blocos or {}
    linhas = ["assuntos:"]
    for valor in VALORES_CANONICOS:
        linhas.append(f"  - assunto: {valor}")
        linhas.append(blocos.get(valor, "    grupos: []"))
    return "\n".join(linhas) + "\n"


UM_GRUPO = """    grupos:
      - alternativas:
          - rxx: R09
            fragmento: F1"""

DOIS_GRUPOS = """    grupos:
      - alternativas:
          - rxx: R14
            fragmento: F1
          - rxx: R09
            fragmento: F2
      - alternativas:
          - rxx: R09
            fragmento: F1"""

MAPA_TOTAL = yaml_total()
MAPA_COM_GRUPO = yaml_total({PRECO: UM_GRUPO})


def escrever(tmp_path: Path, conteudo: str, nome: str = "mapa.yaml") -> Path:
    destino = tmp_path / nome
    destino.write_text(conteudo, encoding="utf-8")
    return destino


def categoria_de(erro: pytest.ExceptionInfo[MapaCoberturaIlegivel]) -> str:
    return str(erro.value).split(":", 1)[0]


# 1. Leitura bem-sucedida


def test_carrega_mapa_total(tmp_path: Path) -> None:
    caminho = escrever(tmp_path, MAPA_TOTAL)

    carregado = carregar_mapa_cobertura(caminho)

    assert [item["assunto"] for item in carregado["assuntos"]] == VALORES_CANONICOS
    assert all(item["grupos"] == [] for item in carregado["assuntos"])


def test_carrega_mapa_com_grupo(tmp_path: Path) -> None:
    caminho = escrever(tmp_path, MAPA_COM_GRUPO)

    carregado = carregar_mapa_cobertura(caminho)

    assert len(carregado["assuntos"]) == 54
    assert carregado["assuntos"][VALORES_CANONICOS.index(PRECO)] == {
        "assunto": PRECO,
        "grupos": [{"alternativas": [{"rxx": "R09", "fragmento": "F1"}]}],
    }


def test_aceita_caminho_como_str(tmp_path: Path) -> None:
    caminho = escrever(tmp_path, MAPA_TOTAL)

    assert len(carregar_mapa_cobertura(str(caminho))["assuntos"]) == 54


def test_leitura_e_deterministica(tmp_path: Path) -> None:
    caminho = escrever(tmp_path, MAPA_COM_GRUPO)

    assert carregar_mapa_cobertura(caminho) == carregar_mapa_cobertura(caminho)


def test_ordem_fisica_declarada_e_preservada(tmp_path: Path) -> None:
    caminho = escrever(tmp_path, yaml_total({PRECO: DOIS_GRUPOS}))

    carregado = carregar_mapa_cobertura(caminho)
    grupos = carregado["assuntos"][VALORES_CANONICOS.index(PRECO)]["grupos"]

    assert [
        (alt["rxx"], alt["fragmento"])
        for grupo in grupos
        for alt in grupo["alternativas"]
    ] == [("R14", "F1"), ("R09", "F2"), ("R09", "F1")]


def test_arquivo_nao_e_alterado_pela_leitura(tmp_path: Path) -> None:
    caminho = escrever(tmp_path, MAPA_COM_GRUPO)
    antes = caminho.read_bytes()

    carregar_mapa_cobertura(caminho)

    assert caminho.read_bytes() == antes


# 2. Ilegibilidade


def test_arquivo_ausente(tmp_path: Path) -> None:
    with pytest.raises(MapaCoberturaIlegivel) as erro:
        carregar_mapa_cobertura(tmp_path / "inexistente.yaml")

    assert categoria_de(erro) == "arquivo_ausente"


def test_diretorio_no_lugar_do_arquivo(tmp_path: Path) -> None:
    diretorio = tmp_path / "mapa.yaml"
    diretorio.mkdir()

    with pytest.raises(MapaCoberturaIlegivel) as erro:
        carregar_mapa_cobertura(diretorio)

    assert categoria_de(erro) == "leitura_falhou"


def test_bytes_que_nao_sao_utf8(tmp_path: Path) -> None:
    caminho = tmp_path / "bytes-invalidos.yaml"
    caminho.write_bytes(b"assuntos: \xff\xfe\n")

    with pytest.raises(MapaCoberturaIlegivel) as erro:
        carregar_mapa_cobertura(caminho)

    assert categoria_de(erro) == "codificacao_invalida"


def test_utf8_com_acento_e_lido(tmp_path: Path) -> None:
    """UTF-8 estrito: texto acentuado atravessa, outra codificação não."""
    caminho = escrever(tmp_path, MAPA_TOTAL + "# ação e não\n")

    assert len(carregar_mapa_cobertura(caminho)["assuntos"]) == 54


def test_latin1_e_recusado(tmp_path: Path) -> None:
    caminho = tmp_path / "latin1.yaml"
    caminho.write_bytes("assuntos: []\n# ação\n".encode("latin-1"))

    with pytest.raises(MapaCoberturaIlegivel) as erro:
        carregar_mapa_cobertura(caminho)

    assert categoria_de(erro) == "codificacao_invalida"


def test_sintaxe_yaml_invalida(tmp_path: Path) -> None:
    caminho = escrever(tmp_path, "assuntos: [\n  - assunto: x\n")

    with pytest.raises(MapaCoberturaIlegivel) as erro:
        carregar_mapa_cobertura(caminho)

    assert categoria_de(erro) == "sintaxe_invalida"


def test_tag_insegura_e_recusada(tmp_path: Path) -> None:
    caminho = escrever(
        tmp_path,
        "assuntos: !!python/object/apply:os.system ['echo oi']\n",
    )

    with pytest.raises(MapaCoberturaIlegivel) as erro:
        carregar_mapa_cobertura(caminho)

    assert categoria_de(erro) == "sintaxe_invalida"


# 3. Chave YAML duplicada, em cada nivel


def test_chave_duplicada_na_raiz(tmp_path: Path) -> None:
    caminho = escrever(tmp_path, MAPA_VAZIO + "assuntos: []\n")

    with pytest.raises(MapaCoberturaIlegivel) as erro:
        carregar_mapa_cobertura(caminho)

    assert categoria_de(erro) == "chave_duplicada"


def test_chave_duplicada_dentro_do_assunto(tmp_path: Path) -> None:
    caminho = escrever(
        tmp_path,
        f"""assuntos:
  - assunto: {PRECO}
    assunto: {PRECO}
    grupos: []
""",
    )

    with pytest.raises(MapaCoberturaIlegivel) as erro:
        carregar_mapa_cobertura(caminho)

    assert categoria_de(erro) == "chave_duplicada"


def test_chave_duplicada_dentro_da_alternativa(tmp_path: Path) -> None:
    caminho = escrever(
        tmp_path,
        f"""assuntos:
  - assunto: {PRECO}
    grupos:
      - alternativas:
          - rxx: R09
            rxx: R14
            fragmento: F1
""",
    )

    with pytest.raises(MapaCoberturaIlegivel) as erro:
        carregar_mapa_cobertura(caminho)

    assert categoria_de(erro) == "chave_duplicada"


# 4. A forma e julgada por coverage_map, e a excecao atravessa intacta


def test_arquivo_vazio_cai_no_contrato_estrutural(tmp_path: Path) -> None:
    caminho = escrever(tmp_path, "")

    with pytest.raises(MapaCoberturaInvalido) as erro:
        carregar_mapa_cobertura(caminho)

    assert str(erro.value) == "tipo_invalido: <raiz>"


def test_raiz_lista_cai_no_contrato_estrutural(tmp_path: Path) -> None:
    caminho = escrever(tmp_path, "- assuntos: []\n")

    with pytest.raises(MapaCoberturaInvalido) as erro:
        carregar_mapa_cobertura(caminho)

    assert str(erro.value) == "tipo_invalido: <raiz>"


def test_grupo_sem_alternativa_cai_no_contrato_estrutural(tmp_path: Path) -> None:
    caminho = escrever(
        tmp_path,
        f"""assuntos:
  - assunto: {PRECO}
    grupos:
      - alternativas: []
""",
    )

    with pytest.raises(MapaCoberturaInvalido) as erro:
        carregar_mapa_cobertura(caminho)

    assert str(erro.value) == "valor_invalido: assuntos[0].grupos[0].alternativas"


def test_campo_extra_cai_no_contrato_estrutural(tmp_path: Path) -> None:
    caminho = escrever(
        tmp_path,
        f"""assuntos:
  - assunto: {PRECO}
    grupos:
      - alternativas:
          - rxx: R09
            fragmento: F1
            priority: 1
""",
    )

    with pytest.raises(MapaCoberturaInvalido) as erro:
        carregar_mapa_cobertura(caminho)

    assert "campo_desconhecido" in str(erro.value)


def test_invalido_nao_e_escondido_como_ilegivel(tmp_path: Path) -> None:
    caminho = escrever(tmp_path, "assuntos: {}\n")

    with pytest.raises(MapaCoberturaInvalido):
        carregar_mapa_cobertura(caminho)


def test_lista_vazia_carrega_mas_falha_na_totalidade(tmp_path: Path) -> None:
    """O YAML é legível; quem o recusa é o contrato estrutural, não o leitor."""
    caminho = escrever(tmp_path, MAPA_VAZIO)

    with pytest.raises(MapaCoberturaInvalido) as erro:
        carregar_mapa_cobertura(caminho)

    assert str(erro.value) == "campo_ausente: assuntos.item"


def test_mapa_parcial_carrega_mas_falha_na_totalidade(tmp_path: Path) -> None:
    parcial = yaml_total().replace(f"  - assunto: {PRECO}\n    grupos: []\n", "")
    caminho = escrever(tmp_path, parcial)

    with pytest.raises(MapaCoberturaInvalido) as erro:
        carregar_mapa_cobertura(caminho)

    assert str(erro.value) == "campo_ausente: assuntos.item"


# 5. Excecoes


def test_ilegivel_deriva_de_exception() -> None:
    assert issubclass(MapaCoberturaIlegivel, Exception)


def test_ilegivel_nao_se_confunde_com_invalido() -> None:
    assert not issubclass(MapaCoberturaIlegivel, MapaCoberturaInvalido)
    assert not issubclass(MapaCoberturaInvalido, MapaCoberturaIlegivel)


def test_mensagem_tem_categoria_e_caminho(tmp_path: Path) -> None:
    ausente = tmp_path / "inexistente.yaml"

    with pytest.raises(MapaCoberturaIlegivel) as erro:
        carregar_mapa_cobertura(ausente)

    assert str(erro.value) == f"arquivo_ausente: {ausente}"


def test_mensagem_nao_reproduz_o_conteudo(tmp_path: Path) -> None:
    caminho = escrever(tmp_path, "assuntos: [\n  - assunto: segredo_comercial\n")

    with pytest.raises(MapaCoberturaIlegivel) as erro:
        carregar_mapa_cobertura(caminho)

    assert "segredo_comercial" not in str(erro.value)


def test_causa_tecnica_fica_encadeada(tmp_path: Path) -> None:
    caminho = escrever(tmp_path, "assuntos: [\n")

    with pytest.raises(MapaCoberturaIlegivel) as erro:
        carregar_mapa_cobertura(caminho)

    assert erro.value.__cause__ is not None


def test_causa_de_arquivo_ausente_e_filenotfound(tmp_path: Path) -> None:
    with pytest.raises(MapaCoberturaIlegivel) as erro:
        carregar_mapa_cobertura(tmp_path / "inexistente.yaml")

    assert isinstance(erro.value.__cause__, FileNotFoundError)


# 6. Isolamento estrutural — provado sobre a AST do modulo


def _arvore(caminho: Path) -> ast.Module:
    return ast.parse(caminho.read_text(encoding="utf-8"))


def _modulos_importados(caminho: Path) -> set[str]:
    importados: set[str] = set()
    for no in ast.walk(_arvore(caminho)):
        if isinstance(no, ast.Import):
            importados.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module is not None:
            importados.add(no.module)
    return importados


def _codigo_sem_prosa(caminho: Path) -> str:
    arvore = _arvore(caminho)
    portadores = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    for no in ast.walk(arvore):
        if not isinstance(no, portadores):
            continue
        corpo = no.body
        primeiro = corpo[0] if corpo else None
        if (
            isinstance(primeiro, ast.Expr)
            and isinstance(primeiro.value, ast.Constant)
            and isinstance(primeiro.value.value, str)
        ):
            no.body = corpo[1:] or [ast.Pass()]
    return ast.unparse(arvore)


def test_importa_somente_o_necessario() -> None:
    assert _modulos_importados(MODULO) == {
        "__future__",
        "pathlib",
        "typing",
        "yaml",
        "casa77_sdr.coverage_map",
    }


@pytest.mark.parametrize(
    "proibido",
    [
        "casa77_sdr.knowledge",
        "casa77_sdr.interpretation",
        "casa77_sdr.response_index",
        "casa77_sdr.response_index_load",
        "casa77_sdr.response_index_tokens",
        "casa77_sdr.state_machine",
        "os",
        "io",
        "json",
        "logging",
        "datetime",
        "time",
        "random",
        "socket",
        "urllib",
        "http",
        "subprocess",
    ],
)
def test_nao_importa_fronteira_proibida(proibido: str) -> None:
    assert proibido not in _modulos_importados(MODULO)


@pytest.mark.parametrize(
    "termo",
    [
        "glob",
        "rglob",
        "iterdir",
        "walk",
        "environ",
        "getenv",
        "cwd(",
        "home(",
        "write_text",
        "write_bytes",
        "mkdir",
        "touch",
        "unlink",
        "rename",
    ],
)
def test_carregador_nao_descobre_nem_escreve(termo: str) -> None:
    """§5.5: sem caminho implícito, descoberta, glob ou escrita."""
    assert termo not in _codigo_sem_prosa(MODULO)


def test_usa_somente_o_analisador_seguro() -> None:
    codigo = _codigo_sem_prosa(MODULO)

    assert "SafeLoader" in codigo
    assert "unsafe_load" not in codigo
    assert "full_load" not in codigo
    assert "Loader=yaml.Loader" not in codigo


def test_codigo_nao_embute_caminho_do_mapa() -> None:
    """§5.5: nenhum caminho padrão que faça parecer que o artefato existe."""
    codigo = _codigo_sem_prosa(MODULO)

    assert "mapa-cobertura" not in codigo
    assert "knowledge" not in codigo


def test_codigo_nao_embute_conteudo_de_mapa() -> None:
    codigo = _codigo_sem_prosa(MODULO)
    especificos = [
        membro.value
        for membro in AssuntoComercial
        if membro is not AssuntoComercial.ASSUNTO_NAO_CLASSIFICADO
    ]

    assert [valor for valor in especificos if valor in codigo] == []
    assert "assuntos" not in codigo


def test_nao_e_exportado_pelo_init() -> None:
    codigo = MODULO_INIT.read_text(encoding="utf-8")

    assert "coverage_map_load" not in codigo
    assert "carregar_mapa_cobertura" not in codigo


def test_api_publica_e_minima() -> None:
    from casa77_sdr import coverage_map_load

    assert coverage_map_load.__all__ == [
        "MapaCoberturaIlegivel",
        "carregar_mapa_cobertura",
    ]


# 7. O artefato reservado continua ausente


def test_mapa_reservado_nao_existe_no_repositorio() -> None:
    assert not MAPA_RESERVADO.exists()


def test_caminho_reservado_falha_como_arquivo_ausente() -> None:
    """Passar o caminho reservado não faz o artefato existir."""
    with pytest.raises(MapaCoberturaIlegivel) as erro:
        carregar_mapa_cobertura(MAPA_RESERVADO)

    assert categoria_de(erro) == "arquivo_ausente"

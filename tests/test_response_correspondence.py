"""Testes da composição determinística da correspondência canônica em memória.

A fronteira **compõe** três fronteiras já existentes — o derivador do domínio do
índice, o leitor da representação marcada e o verificador da bijeção — e **não
cria juiz, contrato, exceção, categoria ou identidade nova**. Estes testes
provam a ordem fixa das chamadas, a relação **diagonal por identidade** (nunca
por posição ou ordem, **`C-A5-I5`**), a chamada única do verificador, a
propagação **intacta** das três exceções, a ausência de validação local, a
pureza do módulo de produção e as garantias negativas — e **não** transformam em
norma a proveniência dos insumos, a existência do índice físico, a validade
integral do índice por `validar_indice`, a execução da bijeção física 37/37 ou a
satisfação de `C-A1-ST6`–`C-A1-ST10`, que estão **fora** desta fronteira.
"""

from __future__ import annotations

import ast
import copy
from pathlib import Path

import pytest

import casa77_sdr
from casa77_sdr import response_correspondence
from casa77_sdr.response_bijection import BijecaoInvalida
from casa77_sdr.response_correspondence import validar_correspondencia_canonica
from casa77_sdr.response_index_tokens import ProjecaoDeIdentidadeInvalida
from casa77_sdr.response_markdown_units import RepresentacaoMarcadaInvalida

# ---------------------------------------------------------------------------
# Apoio
# ---------------------------------------------------------------------------

RAIZ = Path(__file__).resolve().parent.parent

CAMINHO_PRODUCAO = RAIZ / "src" / "casa77_sdr" / "response_correspondence.py"
CODIGO_PRODUCAO = CAMINHO_PRODUCAO.read_text(encoding="utf-8")
ARVORE_PRODUCAO = ast.parse(CODIGO_PRODUCAO)

FRONTEIRAS = (
    "derivar_tokens_do_indice",
    "ler_unidades_marcadas",
    "validar_bijecao",
)

MODULOS_PERMITIDOS = {
    "__future__",
    "casa77_sdr.response_bijection",
    "casa77_sdr.response_index_tokens",
    "casa77_sdr.response_markdown_units",
}


def indice(*pares):
    """Estrutura candidata do índice: `(rxx, [ids])` por resposta."""
    return {
        "respostas": [
            {"id": rxx, "fragmentos": [{"id": i} for i in ids]} for rxx, ids in pares
        ]
    }


def markdown(*pares):
    """Markdown na representação marcada: `(rxx, [ids])` por seção."""
    linhas = []
    for rxx, ids in pares:
        linhas.append(f"## {rxx} — titulo")
        for identificador in ids:
            linhas.append(f"<!-- fragmento: {identificador} -->")
            linhas.append("> corpo")
    return "\n".join(linhas) + "\n" if linhas else ""


def _nomes_usados() -> set[str]:
    nomes: set[str] = set()
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.Name):
            nomes.add(no.id)
        elif isinstance(no, ast.Attribute):
            nomes.add(no.attr)
    return nomes


NOMES_PRODUCAO = _nomes_usados()


class Registrador:
    """Substitui as três fronteiras públicas e registra a ordem das chamadas."""

    def __init__(self, dominio_indice, dominio_markdown):
        self.dominio_indice = dominio_indice
        self.dominio_markdown = dominio_markdown
        self.ordem: list[str] = []
        self.argumentos: list[tuple] = []

    def c9(self, indice_recebido):
        self.ordem.append("c9")
        self.argumentos.append(("c9", indice_recebido))
        return self.dominio_indice

    def c8(self, texto_recebido):
        self.ordem.append("c8")
        self.argumentos.append(("c8", texto_recebido))
        return self.dominio_markdown

    def c6(self, fragmentos, unidades, correspondencias):
        self.ordem.append("c6")
        self.argumentos.append(("c6", fragmentos, unidades, correspondencias))
        return None

    def instalar(self, monkeypatch):
        monkeypatch.setattr(
            response_correspondence, "derivar_tokens_do_indice", self.c9
        )
        monkeypatch.setattr(response_correspondence, "ler_unidades_marcadas", self.c8)
        monkeypatch.setattr(response_correspondence, "validar_bijecao", self.c6)


# ---------------------------------------------------------------------------
# A. Caminho feliz
# ---------------------------------------------------------------------------


def test_mesmos_tokens_mesma_ordem():
    dados = indice(("R01", ["F1"]), ("R05", ["F1", "F2"]))
    texto = markdown(("R01", ["F1"]), ("R05", ["F1", "F2"]))
    assert validar_correspondencia_canonica(dados, texto) is None


def test_mesmos_tokens_em_ordens_fisicas_diferentes():
    dados = indice(("R05", ["F2", "F1"]), ("R01", ["F1"]))
    texto = markdown(("R01", ["F1"]), ("R05", ["F1", "F2"]))
    assert validar_correspondencia_canonica(dados, texto) is None


def test_ordem_invertida_dos_dois_lados():
    dados = indice(("R30", ["F1"]), ("R02", ["F3", "F1"]))
    texto = markdown(("R02", ["F1", "F3"]), ("R30", ["F1"]))
    assert validar_correspondencia_canonica(dados, texto) is None


def test_um_unico_par():
    assert (
        validar_correspondencia_canonica(
            indice(("R01", ["F1"])), markdown(("R01", ["F1"]))
        )
        is None
    )


def test_dominio_grande_com_ids_repetidos_entre_rxx():
    pares = tuple((f"R{n:02d}", ["F1"]) for n in range(1, 31))
    assert validar_correspondencia_canonica(indice(*pares), markdown(*pares)) is None


def test_ambos_os_dominios_vazios():
    # Bijecao trivial valida. Isso afirma **apenas** isso: nada sobre o corpus
    # real, o indice fisico ou `C-A1-ST7`.
    assert validar_correspondencia_canonica({"respostas": []}, "") is None


# ---------------------------------------------------------------------------
# B. Divergencia entre os dois dominios
# ---------------------------------------------------------------------------


def test_token_no_markdown_ausente_no_indice():
    dados = indice(("R01", ["F1"]))
    texto = markdown(("R01", ["F1"]), ("R02", ["F1"]))
    with pytest.raises(BijecaoInvalida):
        validar_correspondencia_canonica(dados, texto)


def test_token_no_indice_ausente_no_markdown():
    dados = indice(("R01", ["F1"]), ("R02", ["F1"]))
    texto = markdown(("R01", ["F1"]))
    with pytest.raises(BijecaoInvalida):
        validar_correspondencia_canonica(dados, texto)


def test_fragmento_a_mais_no_mesmo_rxx():
    dados = indice(("R05", ["F1", "F2", "F3"]))
    texto = markdown(("R05", ["F1", "F2"]))
    with pytest.raises(BijecaoInvalida):
        validar_correspondencia_canonica(dados, texto)


def test_identidades_disjuntas():
    dados = indice(("R01", ["F1"]))
    texto = markdown(("R02", ["F1"]))
    with pytest.raises(BijecaoInvalida):
        validar_correspondencia_canonica(dados, texto)


def test_duplicidade_global_no_markdown_por_rxx_homonimos():
    # O leitor da representacao marcada **nao** garante unicidade global: duas
    # secoes `## R01` produzem o mesmo token duas vezes. Quem recusa e o
    # verificador da bijecao.
    dados = indice(("R01", ["F1"]))
    texto = markdown(("R01", ["F1"]), ("R01", ["F1"]))
    with pytest.raises(BijecaoInvalida):
        validar_correspondencia_canonica(dados, texto)


def test_indice_vazio_com_markdown_nao_vazio():
    with pytest.raises(BijecaoInvalida):
        validar_correspondencia_canonica({"respostas": []}, markdown(("R01", ["F1"])))


def test_markdown_vazio_com_indice_nao_vazio():
    with pytest.raises(BijecaoInvalida):
        validar_correspondencia_canonica(indice(("R01", ["F1"])), "")


# ---------------------------------------------------------------------------
# C. Exceções propagadas intactas
# ---------------------------------------------------------------------------


def test_indice_inadequado_para_o_derivador():
    with pytest.raises(ProjecaoDeIdentidadeInvalida):
        validar_correspondencia_canonica("nao e mapeamento", markdown(("R01", ["F1"])))


def test_markdown_invalido_para_o_leitor():
    with pytest.raises(RepresentacaoMarcadaInvalida):
        validar_correspondencia_canonica(
            indice(("R01", ["F1"])),
            "## R01 — titulo\n> bloco sem marcador\n",
        )


def test_ambos_invalidos_o_lado_do_indice_falha_primeiro():
    with pytest.raises(ProjecaoDeIdentidadeInvalida):
        validar_correspondencia_canonica(42, 42)


@pytest.mark.parametrize("invalido", [None, 0, 1, True, 3.5, b"{}", [], (), object()])
def test_indice_de_tipo_invalido_nao_vira_typeerror(invalido):
    with pytest.raises(ProjecaoDeIdentidadeInvalida):
        validar_correspondencia_canonica(invalido, markdown(("R01", ["F1"])))


@pytest.mark.parametrize("invalido", [None, 0, 1, True, 3.5, b"md", [], (), object()])
def test_markdown_de_tipo_invalido_nao_vira_typeerror(invalido):
    with pytest.raises(RepresentacaoMarcadaInvalida):
        validar_correspondencia_canonica(indice(("R01", ["F1"])), invalido)


def test_subclasse_de_str_no_markdown_e_recusada_pelo_leitor():
    class TextoDerivado(str):
        pass

    with pytest.raises(RepresentacaoMarcadaInvalida):
        validar_correspondencia_canonica(
            indice(("R01", ["F1"])), TextoDerivado(markdown(("R01", ["F1"])))
        )


@pytest.mark.parametrize(
    "argumentos,esperada",
    [
        (("nao e mapeamento", markdown(("R01", ["F1"]))), ProjecaoDeIdentidadeInvalida),
        (
            (indice(("R01", ["F1"])), "## R01 — t\n> sem marcador\n"),
            RepresentacaoMarcadaInvalida,
        ),
        ((indice(("R01", ["F1"])), markdown(("R02", ["F1"]))), BijecaoInvalida),
    ],
)
def test_excecao_sobe_sem_reclassificacao(argumentos, esperada):
    with pytest.raises(esperada) as erro:
        validar_correspondencia_canonica(*argumentos)
    assert type(erro.value) is esperada
    assert erro.value.__cause__ is None
    assert erro.value.__context__ is None


def test_nenhuma_excecao_nova_e_exportada():
    assert response_correspondence.__all__ == ["validar_correspondencia_canonica"]
    publicos = [
        nome for nome in vars(response_correspondence) if not nome.startswith("_")
    ]
    for nome in publicos:
        valor = getattr(response_correspondence, nome)
        assert not (isinstance(valor, type) and issubclass(valor, BaseException))


# ---------------------------------------------------------------------------
# D. Insumos nao sao alterados
# ---------------------------------------------------------------------------

DADOS_ESTAVEIS = indice(("R01", ["F1"]), ("R05", ["F1", "F2"]))
TEXTO_ESTAVEL = markdown(("R01", ["F1"]), ("R05", ["F1", "F2"]))


def test_insumos_nao_sao_alterados_no_sucesso():
    dados = copy.deepcopy(DADOS_ESTAVEIS)
    antes = copy.deepcopy(dados)
    texto = str(TEXTO_ESTAVEL)
    validar_correspondencia_canonica(dados, texto)
    assert dados == antes
    assert texto == TEXTO_ESTAVEL


@pytest.mark.parametrize(
    "estrutura,texto,esperada",
    [
        ({"respostas": [{"id": "r01", "fragmentos": [{"id": "F1"}]}]}, None, None),
        (None, "## R01 — t\n> sem marcador\n", RepresentacaoMarcadaInvalida),
        (None, None, BijecaoInvalida),
    ],
)
def test_insumos_nao_sao_alterados_nos_caminhos_de_excecao(estrutura, texto, esperada):
    if estrutura is None:
        estrutura = copy.deepcopy(DADOS_ESTAVEIS)
    if texto is None:
        texto = markdown(("R09", ["F1"]))
    antes_estrutura = copy.deepcopy(estrutura)
    antes_texto = str(texto)
    with pytest.raises(Exception):
        validar_correspondencia_canonica(estrutura, texto)
    assert estrutura == antes_estrutura
    assert texto == antes_texto


def test_o_caminho_de_excecao_do_derivador_nao_altera_a_estrutura():
    estrutura = {"respostas": [{"id": "r01", "fragmentos": [{"id": "F1"}]}]}
    antes = copy.deepcopy(estrutura)
    with pytest.raises(ProjecaoDeIdentidadeInvalida):
        validar_correspondencia_canonica(estrutura, markdown(("R01", ["F1"])))
    assert estrutura == antes


# ---------------------------------------------------------------------------
# E. Ordem, relacao diagonal e chamada unica
# ---------------------------------------------------------------------------


def test_ordem_das_chamadas_e_c9_c8_c6(monkeypatch):
    registrador = Registrador(("R01/F1", "R05/F2"), ("R05/F2", "R01/F1"))
    registrador.instalar(monkeypatch)
    response_correspondence.validar_correspondencia_canonica({"respostas": []}, "")
    assert registrador.ordem == ["c9", "c8", "c6"]


def test_a_relacao_e_exatamente_diagonal_e_na_ordem_do_derivador(monkeypatch):
    registrador = Registrador(("R05/F2", "R01/F1", "R30/F1"), ("R01/F1",))
    registrador.instalar(monkeypatch)
    response_correspondence.validar_correspondencia_canonica({"respostas": []}, "")
    (_, _, _, correspondencias) = registrador.argumentos[-1]
    assert correspondencias == (
        ("R05/F2", "R05/F2"),
        ("R01/F1", "R01/F1"),
        ("R30/F1", "R30/F1"),
    )


def test_a_relacao_e_tupla_de_tuplas_exatas_de_str(monkeypatch):
    registrador = Registrador(("R01/F1",), ("R01/F1",))
    registrador.instalar(monkeypatch)
    response_correspondence.validar_correspondencia_canonica({"respostas": []}, "")
    (_, _, _, correspondencias) = registrador.argumentos[-1]
    assert type(correspondencias) is tuple
    for par in correspondencias:
        assert type(par) is tuple
        assert len(par) == 2
        assert type(par[0]) is str and type(par[1]) is str
        assert par[0] is par[1]


def test_a_relacao_nao_e_pareada_por_posicao(monkeypatch):
    # Se a relacao fosse posicional, o par seria ("R01/F1", "R30/F1").
    registrador = Registrador(("R01/F1", "R30/F1"), ("R30/F1", "R01/F1"))
    registrador.instalar(monkeypatch)
    response_correspondence.validar_correspondencia_canonica({"respostas": []}, "")
    (_, _, _, correspondencias) = registrador.argumentos[-1]
    assert correspondencias == (("R01/F1", "R01/F1"), ("R30/F1", "R30/F1"))


def test_os_dominios_sao_repassados_sem_alteracao(monkeypatch):
    registrador = Registrador(("R01/F1",), ("R01/F1",))
    registrador.instalar(monkeypatch)
    response_correspondence.validar_correspondencia_canonica({"respostas": []}, "")
    (_, fragmentos, unidades, _) = registrador.argumentos[-1]
    assert fragmentos is registrador.dominio_indice
    assert unidades is registrador.dominio_markdown


def test_os_insumos_chegam_intactos_as_fronteiras(monkeypatch):
    registrador = Registrador((), ())
    registrador.instalar(monkeypatch)
    estrutura = {"respostas": []}
    texto = "qualquer coisa"
    response_correspondence.validar_correspondencia_canonica(estrutura, texto)
    assert registrador.argumentos[0] == ("c9", estrutura)
    assert registrador.argumentos[1] == ("c8", texto)


def test_verificador_e_chamado_exatamente_uma_vez(monkeypatch):
    registrador = Registrador(("R01/F1",), ("R01/F1",))
    registrador.instalar(monkeypatch)
    response_correspondence.validar_correspondencia_canonica({"respostas": []}, "")
    assert registrador.ordem.count("c6") == 1


def test_verificador_nao_e_chamado_se_o_derivador_falhar(monkeypatch):
    registrador = Registrador((), ())

    def c9_que_falha(_):
        registrador.ordem.append("c9")
        raise ProjecaoDeIdentidadeInvalida("tipo_invalido: indice")

    registrador.instalar(monkeypatch)
    monkeypatch.setattr(
        response_correspondence, "derivar_tokens_do_indice", c9_que_falha
    )
    with pytest.raises(ProjecaoDeIdentidadeInvalida):
        response_correspondence.validar_correspondencia_canonica({"respostas": []}, "")
    assert registrador.ordem == ["c9"]
    assert "c8" not in registrador.ordem
    assert "c6" not in registrador.ordem


def test_verificador_nao_e_chamado_se_o_leitor_falhar(monkeypatch):
    registrador = Registrador((), ())

    def c8_que_falha(_):
        registrador.ordem.append("c8")
        raise RepresentacaoMarcadaInvalida("tipo_invalido: texto")

    registrador.instalar(monkeypatch)
    monkeypatch.setattr(response_correspondence, "ler_unidades_marcadas", c8_que_falha)
    with pytest.raises(RepresentacaoMarcadaInvalida):
        response_correspondence.validar_correspondencia_canonica({"respostas": []}, "")
    assert registrador.ordem == ["c9", "c8"]
    assert "c6" not in registrador.ordem


def test_o_retorno_do_verificador_e_repassado_como_none(monkeypatch):
    registrador = Registrador(("R01/F1",), ("R01/F1",))
    registrador.instalar(monkeypatch)
    resultado = response_correspondence.validar_correspondencia_canonica(
        {"respostas": []}, ""
    )
    assert resultado is None


# ---------------------------------------------------------------------------
# F. Nao substitui `validar_indice`
# ---------------------------------------------------------------------------


def test_estrutura_nao_integralmente_valida_pode_passar():
    # `status` fora do vocabulario fechado e `bindings` ausentes: o indice
    # **nao** e integralmente valido, mas as identidades coincidem — e esta
    # fronteira julga **somente** as identidades.
    from casa77_sdr.response_index import IndiceInvalido, validar_indice

    estrutura = {
        "respostas": [
            {"id": "R01", "fragmentos": [{"id": "F1", "status": "PARCIAL"}]}
        ]
    }
    with pytest.raises(IndiceInvalido):
        validar_indice(estrutura)
    assert (
        validar_correspondencia_canonica(estrutura, markdown(("R01", ["F1"]))) is None
    )


def test_campos_desconhecidos_nao_impedem_a_correspondencia():
    estrutura = {
        "respostas": [
            {
                "id": "R01",
                "fragmentos": [{"id": "F1", "campo_inventado": 1}],
                "outro": [1, 2],
            }
        ],
        "topo_desconhecido": "x",
    }
    assert (
        validar_correspondencia_canonica(estrutura, markdown(("R01", ["F1"]))) is None
    )


def test_o_modulo_nao_importa_nem_chama_validar_indice():
    assert "validar_indice" not in NOMES_PRODUCAO
    assert "carregar_indice" not in NOMES_PRODUCAO


# ---------------------------------------------------------------------------
# G. Superficie publica e pureza
# ---------------------------------------------------------------------------


def test_all_tem_exatamente_um_nome():
    assert response_correspondence.__all__ == ["validar_correspondencia_canonica"]
    assert len(response_correspondence.__all__) == 1


def test_nao_e_exportado_pelo_pacote():
    assert "validar_correspondencia_canonica" not in casa77_sdr.__all__
    assert not hasattr(casa77_sdr, "validar_correspondencia_canonica")


def test_assinatura_publica():
    import inspect

    assinatura = inspect.signature(validar_correspondencia_canonica)
    parametros = list(assinatura.parameters)
    assert parametros == ["indice", "texto_markdown"]
    for nome in parametros:
        assert assinatura.parameters[nome].default is inspect.Parameter.empty


def test_imports_restritos_as_tres_fronteiras_publicas():
    importados = [no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.Import)]
    assert importados == []
    de_modulo = [
        no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.ImportFrom)
    ]
    assert {no.module for no in de_modulo} == MODULOS_PERMITIDOS
    nomes = {
        alias.name
        for no in de_modulo
        if no.module != "__future__"
        for alias in no.names
    }
    assert nomes == set(FRONTEIRAS)


def test_nao_ha_import_dentro_de_funcao():
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for interno in ast.walk(no):
                assert not isinstance(interno, (ast.Import, ast.ImportFrom))


def test_nao_ha_try_except():
    for no in ast.walk(ARVORE_PRODUCAO):
        assert not isinstance(no, (ast.Try, ast.ExceptHandler, ast.Raise))


def test_nao_ha_io_nem_filesystem():
    proibidos = {
        "open",
        "read",
        "read_text",
        "read_bytes",
        "write",
        "write_text",
        "write_bytes",
        "Path",
        "pathlib",
        "os",
        "io",
        "sys",
        "input",
        "print",
        "glob",
        "listdir",
        "shutil",
        "tempfile",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_yaml_rede_nem_llm():
    proibidos = {
        "yaml",
        "safe_load",
        "json",
        "loads",
        "dumps",
        "pickle",
        "socket",
        "requests",
        "urllib",
        "urlopen",
        "http",
        "httpx",
        "subprocess",
        "Popen",
        "prompt",
        "completions",
        "sqlite3",
        "connect",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_relogio_calendario_locale_ambiente_nem_cache():
    proibidos = {
        "time",
        "monotonic",
        "datetime",
        "date",
        "now",
        "utcnow",
        "today",
        "calendar",
        "locale",
        "setlocale",
        "getenv",
        "environ",
        "zoneinfo",
        "random",
        "uuid",
        "hashlib",
        "lru_cache",
        "cache",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_normalizacao_nem_execucao_dinamica():
    proibidos = {
        "unicodedata",
        "normalize",
        "casefold",
        "lower",
        "upper",
        "strip",
        "encode",
        "decode",
        "zip",
        "sorted",
        "eval",
        "exec",
        "compile",
        "__import__",
        "importlib",
        "globals",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_estado_mutavel_de_modulo():
    for no in ARVORE_PRODUCAO.body:
        if isinstance(no, ast.Assign):
            for alvo in no.targets:
                assert getattr(alvo, "id", None) == "__all__"
            assert isinstance(no.value, (ast.List, ast.Tuple))
            for elemento in no.value.elts:
                assert isinstance(elemento, ast.Constant)


def _sem_quebras(texto: str) -> str:
    """Colapsa o espaçamento para que a busca não dependa da quebra de linha."""
    return " ".join(texto.split())


def test_a_docstring_declara_as_garantias_negativas():
    docstring = _sem_quebras(ast.get_docstring(ARVORE_PRODUCAO) or "")
    for exigido in (
        "NÃO É EXECUTAR A BIJEÇÃO FÍSICA E NÃO É MATERIALIZAR",
        "continua INEXISTENTE",
        "C-A1-ST6",
        "validar_indice",
        "C-A5-I5",
        "C-A5-T5",
    ):
        assert exigido in docstring


def test_a_docstring_da_funcao_declara_as_garantias_negativas():
    funcoes = [
        no
        for no in ARVORE_PRODUCAO.body
        if isinstance(no, ast.FunctionDef)
        and no.name == "validar_correspondencia_canonica"
    ]
    assert len(funcoes) == 1
    docstring = _sem_quebras(ast.get_docstring(funcoes[0]) or "")
    for exigido in (
        "NÃO É EXECUTAR A BIJEÇÃO FÍSICA E NÃO É MATERIALIZAR",
        "continua INEXISTENTE",
        "C-A1-ST6",
    ):
        assert exigido in docstring


# ---------------------------------------------------------------------------
# H. Determinismo
# ---------------------------------------------------------------------------


def test_chamadas_repetidas_dao_o_mesmo_resultado():
    for _ in range(3):
        assert validar_correspondencia_canonica(DADOS_ESTAVEIS, TEXTO_ESTAVEL) is None


def test_falha_repetida_continua_falhando_igual():
    dados = indice(("R01", ["F1"]))
    texto = markdown(("R02", ["F1"]))
    for _ in range(3):
        with pytest.raises(BijecaoInvalida):
            validar_correspondencia_canonica(dados, texto)


def test_nao_ha_estado_entre_chamadas():
    assert validar_correspondencia_canonica(DADOS_ESTAVEIS, TEXTO_ESTAVEL) is None
    with pytest.raises(BijecaoInvalida):
        validar_correspondencia_canonica(indice(("R01", ["F1"])), "")
    assert validar_correspondencia_canonica(DADOS_ESTAVEIS, TEXTO_ESTAVEL) is None


# ---------------------------------------------------------------------------
# I. O indice fisico continua inexistente
# ---------------------------------------------------------------------------


def test_o_indice_fisico_continua_inexistente():
    assert not (RAIZ / "knowledge" / "indice-respostas-aprovadas.yaml").exists()


def test_o_sucesso_nao_prova_proveniencia():
    # Uma estrutura e um Markdown **sinteticos** — que nao sao o indice nem o
    # corpus oficiais — passam. Isso e exatamente a garantia negativa: o
    # sucesso afirma somente a bijetividade entre os dois insumos dados.
    dados = indice(("R42", ["F7"]))
    texto = markdown(("R42", ["F7"]))
    assert validar_correspondencia_canonica(dados, texto) is None

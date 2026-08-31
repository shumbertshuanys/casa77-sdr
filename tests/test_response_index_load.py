"""Testes da fronteira de leitura do futuro índice de respostas aprovadas.

Nenhum teste cria `knowledge/indice-respostas-aprovadas.yaml` e nenhum teste
altera arquivo do repositório: todo artefato lido nasce em `tmp_path`. Os
fixtures são sintéticos — identificadores, caminhos e nomes são inventados — e
nenhum valor comercial real aparece como expectativa ou como conteúdo.

A prova de que o carregador não abre fonte comercial paralela e não redefine o
vocabulário de C é feita sobre a **AST do módulo de produção**, seguindo o
precedente de `test_response_index.py`.
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import Any

import pytest
import yaml

from casa77_sdr.response_index import IndiceInvalido
from casa77_sdr.response_index_load import IndiceIlegivel, carregar_indice

RAIZ = Path(__file__).resolve().parents[1]
MODULO = RAIZ / "src" / "casa77_sdr" / "response_index_load.py"
MODULO_INIT = RAIZ / "src" / "casa77_sdr" / "__init__.py"
YAML_REAL = RAIZ / "knowledge" / "casa77.yaml"


# Fixtures sintéticos — YAML escrito à mão, para exercitar o analisador de fato.


def escrever(tmp_path: Path, conteudo: str, nome: str = "indice.yaml") -> Path:
    destino = tmp_path / nome
    destino.write_text(conteudo, encoding="utf-8")
    return destino


INDICE_MINIMO = """\
respostas:
  - id: R01
    fragmentos:
      - id: fragmento_exemplo
        status: APROVADO
        bindings: []
"""

INDICE_SEM_RESPOSTAS = "respostas: []\n"

INDICE_COMPLETO = """\
respostas:
  - id: R01
    fragmentos:
      - id: fragmento_exemplo
        status: APROVADO
        itera_sobre: colecao_exemplo[id=item_exemplo]
        bindings:
          - nome: quantidade_exemplo
            mecanismo: RENDERIZADO
            origem: YAML
            caminho_yaml: bloco_exemplo.campo_exemplo
            placeholder: "{{quantidade_exemplo}}"
            formato: inteiro
          - nome: condicao_exemplo
            mecanismo: ASSERTIVA
            origem: YAML
            caminho_yaml: bloco_exemplo.flag_exemplo
            predicado: EH_VERDADEIRO
      - id: outro_fragmento_exemplo
        status: AGUARDA_APROVACAO
        bindings:
          - nome: consulta_exemplo
            mecanismo: ASSERTIVA
            origem: RUNTIME_AUTORITATIVO
            fato_runtime: consulta_calendario_valida
            predicado: EH_FALSO
  - id: R02
    fragmentos:
      - id: fragmento_bloqueado_exemplo
        status: BLOQUEADO
        bindings: []
"""


# 1. Caminhos positivos


def test_carrega_indice_minimo(tmp_path: Path) -> None:
    caminho = escrever(tmp_path, INDICE_MINIMO)

    assert carregar_indice(caminho) == {
        "respostas": [
            {
                "id": "R01",
                "fragmentos": [
                    {
                        "id": "fragmento_exemplo",
                        "status": "APROVADO",
                        "bindings": [],
                    }
                ],
            }
        ]
    }


def test_aceita_caminho_como_path(tmp_path: Path) -> None:
    caminho = escrever(tmp_path, INDICE_MINIMO)

    assert isinstance(caminho, Path)
    assert carregar_indice(caminho)["respostas"][0]["id"] == "R01"


def test_aceita_caminho_como_texto(tmp_path: Path) -> None:
    caminho = escrever(tmp_path, INDICE_MINIMO)

    assert carregar_indice(str(caminho))["respostas"][0]["id"] == "R01"


def test_lista_de_respostas_vazia_e_valida(tmp_path: Path) -> None:
    """C-2: o índice sem resposta alguma é estruturalmente válido."""
    caminho = escrever(tmp_path, INDICE_SEM_RESPOSTAS)

    assert carregar_indice(caminho) == {"respostas": []}


def test_carrega_indice_com_multiplos_fragmentos_e_bindings(
    tmp_path: Path,
) -> None:
    caminho = escrever(tmp_path, INDICE_COMPLETO)

    indice = carregar_indice(caminho)
    respostas = indice["respostas"]

    assert [resposta["id"] for resposta in respostas] == ["R01", "R02"]
    assert len(respostas[0]["fragmentos"]) == 2
    assert respostas[0]["fragmentos"][0]["itera_sobre"] == (
        "colecao_exemplo[id=item_exemplo]"
    )


@pytest.mark.parametrize(
    "status", ["APROVADO", "AGUARDA_APROVACAO", "BLOQUEADO"]
)
def test_aceita_cada_status_do_vocabulario(tmp_path: Path, status: str) -> None:
    caminho = escrever(
        tmp_path,
        f"""\
respostas:
  - id: R01
    fragmentos:
      - id: fragmento_exemplo
        status: {status}
        bindings: []
""",
    )

    assert carregar_indice(caminho)["respostas"][0]["fragmentos"][0][
        "status"
    ] == status


def test_aceita_binding_renderizado(tmp_path: Path) -> None:
    caminho = escrever(tmp_path, INDICE_COMPLETO)

    binding = carregar_indice(caminho)["respostas"][0]["fragmentos"][0][
        "bindings"
    ][0]

    assert binding["mecanismo"] == "RENDERIZADO"
    assert binding["origem"] == "YAML"
    assert binding["formato"] == "inteiro"


def test_aceita_assertiva_com_origem_yaml(tmp_path: Path) -> None:
    caminho = escrever(tmp_path, INDICE_COMPLETO)

    binding = carregar_indice(caminho)["respostas"][0]["fragmentos"][0][
        "bindings"
    ][1]

    assert binding["mecanismo"] == "ASSERTIVA"
    assert binding["origem"] == "YAML"
    assert binding["caminho_yaml"] == "bloco_exemplo.flag_exemplo"


def test_aceita_assertiva_com_origem_runtime(tmp_path: Path) -> None:
    caminho = escrever(tmp_path, INDICE_COMPLETO)

    binding = carregar_indice(caminho)["respostas"][0]["fragmentos"][1][
        "bindings"
    ][0]

    assert binding["origem"] == "RUNTIME_AUTORITATIVO"
    assert binding["fato_runtime"] == "consulta_calendario_valida"


def test_aceita_bindings_vazia(tmp_path: Path) -> None:
    """C-2k: a lista existe sempre, e vazia continua válida."""
    caminho = escrever(tmp_path, INDICE_MINIMO)

    assert carregar_indice(caminho)["respostas"][0]["fragmentos"][0][
        "bindings"
    ] == []


def test_aceita_itera_sobre(tmp_path: Path) -> None:
    caminho = escrever(
        tmp_path,
        """\
respostas:
  - id: R01
    fragmentos:
      - id: fragmento_exemplo
        status: APROVADO
        itera_sobre: bloco_exemplo.colecao_exemplo
        bindings: []
""",
    )

    fragmento = carregar_indice(caminho)["respostas"][0]["fragmentos"][0]

    assert fragmento["itera_sobre"] == "bloco_exemplo.colecao_exemplo"


# 2. Ilegibilidade — leitura e análise


def categoria_de(erro: pytest.ExceptionInfo[IndiceIlegivel]) -> str:
    return str(erro.value).split(":", 1)[0]


def test_arquivo_inexistente(tmp_path: Path) -> None:
    with pytest.raises(IndiceIlegivel) as erro:
        carregar_indice(tmp_path / "nao-existe.yaml")

    assert categoria_de(erro) == "arquivo_ausente"


def test_arquivo_inexistente_nao_cria_arquivo(tmp_path: Path) -> None:
    """I1: falhar ao ler nunca materializa um arquivo vazio."""
    ausente = tmp_path / "nao-existe.yaml"

    with pytest.raises(IndiceIlegivel):
        carregar_indice(ausente)

    assert not ausente.exists()
    assert list(tmp_path.iterdir()) == []


def test_diretorio_no_lugar_do_arquivo(tmp_path: Path) -> None:
    diretorio = tmp_path / "indice.yaml"
    diretorio.mkdir()

    with pytest.raises(IndiceIlegivel) as erro:
        carregar_indice(diretorio)

    assert categoria_de(erro) == "leitura_falhou"


def test_conteudo_nao_decodificavel_em_utf8(tmp_path: Path) -> None:
    caminho = tmp_path / "bytes-invalidos.yaml"
    caminho.write_bytes(b"respostas: \xff\xfe\n")

    with pytest.raises(IndiceIlegivel) as erro:
        carregar_indice(caminho)

    assert categoria_de(erro) == "codificacao_invalida"
    assert isinstance(erro.value.__cause__, UnicodeDecodeError)


def test_sintaxe_yaml_invalida(tmp_path: Path) -> None:
    caminho = escrever(tmp_path, "respostas: [\n  - id: R01\n")

    with pytest.raises(IndiceIlegivel) as erro:
        carregar_indice(caminho)

    assert categoria_de(erro) == "sintaxe_invalida"


def test_recusa_tag_python_insegura(tmp_path: Path) -> None:
    """O analisador seguro recusa construir objeto Python arbitrário."""
    caminho = escrever(
        tmp_path,
        "respostas: !!python/object/apply:os.system ['echo oi']\n",
    )

    with pytest.raises(IndiceIlegivel) as erro:
        carregar_indice(caminho)

    assert categoria_de(erro) == "sintaxe_invalida"


def test_arquivo_vazio_falha_estruturalmente(tmp_path: Path) -> None:
    """Vazio é analisável: vira `None` e é o contrato de C que o rejeita."""
    caminho = escrever(tmp_path, "")

    with pytest.raises(IndiceInvalido) as erro:
        carregar_indice(caminho)

    assert str(erro.value) == "tipo_invalido: <raiz>"


# 3. Chave duplicada em cada nível


def test_chave_duplicada_na_raiz(tmp_path: Path) -> None:
    caminho = escrever(tmp_path, INDICE_MINIMO + "respostas: []\n")

    with pytest.raises(IndiceIlegivel) as erro:
        carregar_indice(caminho)

    assert categoria_de(erro) == "chave_duplicada"


def test_chave_duplicada_dentro_de_resposta(tmp_path: Path) -> None:
    caminho = escrever(
        tmp_path,
        """\
respostas:
  - id: R01
    id: R02
    fragmentos:
      - id: fragmento_exemplo
        status: APROVADO
        bindings: []
""",
    )

    with pytest.raises(IndiceIlegivel) as erro:
        carregar_indice(caminho)

    assert categoria_de(erro) == "chave_duplicada"


def test_chave_duplicada_dentro_de_fragmento(tmp_path: Path) -> None:
    caminho = escrever(
        tmp_path,
        """\
respostas:
  - id: R01
    fragmentos:
      - id: fragmento_exemplo
        status: APROVADO
        status: BLOQUEADO
        bindings: []
""",
    )

    with pytest.raises(IndiceIlegivel) as erro:
        carregar_indice(caminho)

    assert categoria_de(erro) == "chave_duplicada"


def test_chave_duplicada_dentro_de_binding(tmp_path: Path) -> None:
    caminho = escrever(
        tmp_path,
        """\
respostas:
  - id: R01
    fragmentos:
      - id: fragmento_exemplo
        status: APROVADO
        bindings:
          - nome: quantidade_exemplo
            nome: outro_nome_exemplo
            mecanismo: RENDERIZADO
            origem: YAML
            caminho_yaml: bloco_exemplo.campo_exemplo
            placeholder: "{{quantidade_exemplo}}"
            formato: inteiro
""",
    )

    with pytest.raises(IndiceIlegivel) as erro:
        carregar_indice(caminho)

    assert categoria_de(erro) == "chave_duplicada"


def test_chave_duplicada_nao_e_confundida_com_sintaxe(tmp_path: Path) -> None:
    """A duplicidade tem categoria própria, distinta de sintaxe inválida."""
    caminho = escrever(tmp_path, "respostas: []\nrespostas: []\n")

    with pytest.raises(IndiceIlegivel) as erro:
        carregar_indice(caminho)

    assert categoria_de(erro) == "chave_duplicada"
    assert categoria_de(erro) != "sintaxe_invalida"


def test_chaves_iguais_em_mapeamentos_irmaos_sao_validas(
    tmp_path: Path,
) -> None:
    """A recusa é por mapeamento, não global: `id` repete entre fragmentos."""
    caminho = escrever(
        tmp_path,
        """\
respostas:
  - id: R01
    fragmentos:
      - id: fragmento_um_exemplo
        status: APROVADO
        bindings: []
      - id: fragmento_dois_exemplo
        status: APROVADO
        bindings: []
""",
    )

    assert len(carregar_indice(caminho)["respostas"][0]["fragmentos"]) == 2


# 4. Delegação real para o validador de E1


def test_status_invalido_delega_para_e1(tmp_path: Path) -> None:
    caminho = escrever(
        tmp_path,
        """\
respostas:
  - id: R01
    fragmentos:
      - id: fragmento_exemplo
        status: PARCIAL
        bindings: []
""",
    )

    with pytest.raises(IndiceInvalido) as erro:
        carregar_indice(caminho)

    assert str(erro.value) == (
        "valor_invalido: respostas[0].fragmentos[0].status"
    )


def test_origem_ausente_delega_para_e1(tmp_path: Path) -> None:
    caminho = escrever(
        tmp_path,
        """\
respostas:
  - id: R01
    fragmentos:
      - id: fragmento_exemplo
        status: APROVADO
        bindings:
          - nome: quantidade_exemplo
            mecanismo: RENDERIZADO
            caminho_yaml: bloco_exemplo.campo_exemplo
            placeholder: "{{quantidade_exemplo}}"
            formato: inteiro
""",
    )

    with pytest.raises(IndiceInvalido) as erro:
        carregar_indice(caminho)

    assert str(erro.value) == (
        "campo_ausente: respostas[0].fragmentos[0].bindings[0].origem"
    )


def test_renderizado_sem_formato_delega_para_e1(tmp_path: Path) -> None:
    caminho = escrever(
        tmp_path,
        """\
respostas:
  - id: R01
    fragmentos:
      - id: fragmento_exemplo
        status: APROVADO
        bindings:
          - nome: quantidade_exemplo
            mecanismo: RENDERIZADO
            origem: YAML
            caminho_yaml: bloco_exemplo.campo_exemplo
            placeholder: "{{quantidade_exemplo}}"
""",
    )

    with pytest.raises(IndiceInvalido) as erro:
        carregar_indice(caminho)

    assert str(erro.value) == (
        "campo_ausente: respostas[0].fragmentos[0].bindings[0].formato"
    )


def test_assertiva_com_placeholder_delega_para_e1(tmp_path: Path) -> None:
    caminho = escrever(
        tmp_path,
        """\
respostas:
  - id: R01
    fragmentos:
      - id: fragmento_exemplo
        status: APROVADO
        bindings:
          - nome: condicao_exemplo
            mecanismo: ASSERTIVA
            origem: YAML
            caminho_yaml: bloco_exemplo.flag_exemplo
            predicado: EH_VERDADEIRO
            placeholder: "{{condicao_exemplo}}"
""",
    )

    with pytest.raises(IndiceInvalido) as erro:
        carregar_indice(caminho)

    assert str(erro.value) == (
        "combinacao_invalida: respostas[0].fragmentos[0].bindings[0].placeholder"
    )


def test_runtime_com_renderizado_delega_para_e1(tmp_path: Path) -> None:
    caminho = escrever(
        tmp_path,
        """\
respostas:
  - id: R01
    fragmentos:
      - id: fragmento_exemplo
        status: APROVADO
        bindings:
          - nome: consulta_exemplo
            mecanismo: RENDERIZADO
            origem: RUNTIME_AUTORITATIVO
            fato_runtime: consulta_calendario_valida
            placeholder: "{{consulta_exemplo}}"
            formato: texto
""",
    )

    with pytest.raises(IndiceInvalido) as erro:
        carregar_indice(caminho)

    assert str(erro.value) == (
        "combinacao_invalida: respostas[0].fragmentos[0].bindings[0].mecanismo"
    )


def test_resposta_duplicada_delega_para_e1(tmp_path: Path) -> None:
    caminho = escrever(
        tmp_path,
        """\
respostas:
  - id: R01
    fragmentos:
      - id: fragmento_exemplo
        status: APROVADO
        bindings: []
  - id: R01
    fragmentos:
      - id: outro_fragmento_exemplo
        status: APROVADO
        bindings: []
""",
    )

    with pytest.raises(IndiceInvalido) as erro:
        carregar_indice(caminho)

    assert str(erro.value) == "duplicidade: respostas[1].id"


def test_selecao_posicional_delega_para_e1(tmp_path: Path) -> None:
    caminho = escrever(
        tmp_path,
        """\
respostas:
  - id: R01
    fragmentos:
      - id: fragmento_exemplo
        status: APROVADO
        bindings:
          - nome: quantidade_exemplo
            mecanismo: RENDERIZADO
            origem: YAML
            caminho_yaml: colecao_exemplo[id=teste][0].campo_exemplo
            placeholder: "{{quantidade_exemplo}}"
            formato: inteiro
""",
    )

    with pytest.raises(IndiceInvalido) as erro:
        carregar_indice(caminho)

    assert str(erro.value) == (
        "selecao_posicional: respostas[0].fragmentos[0].bindings[0].caminho_yaml"
    )


@pytest.mark.parametrize("raiz", ["- respostas", "42", "texto_solto", "null"])
def test_raiz_nao_mapeamento_chega_ao_validador(
    tmp_path: Path, raiz: str
) -> None:
    """Raiz inválida não é filtrada aqui: a regra de E1 é que a rejeita."""
    caminho = escrever(tmp_path, f"{raiz}\n")

    with pytest.raises(IndiceInvalido) as erro:
        carregar_indice(caminho)

    assert str(erro.value) == "tipo_invalido: <raiz>"


def test_indice_invalido_nao_e_reembalado_como_ilegivel(
    tmp_path: Path,
) -> None:
    caminho = escrever(
        tmp_path,
        """\
respostas:
  - id: R01
    fragmentos: []
""",
    )

    with pytest.raises(IndiceInvalido) as erro:
        carregar_indice(caminho)

    assert not isinstance(erro.value, IndiceIlegivel)
    assert erro.value.__cause__ is None
    assert str(erro.value) == "valor_invalido: respostas[0].fragmentos"


# 5. Invariantes negativos e segurança


def test_nao_altera_o_arquivo_lido(tmp_path: Path) -> None:
    """I1: leitura pura — o artefato sai byte a byte como entrou."""
    caminho = escrever(tmp_path, INDICE_COMPLETO)
    antes = hashlib.sha256(caminho.read_bytes()).hexdigest()

    carregar_indice(caminho)

    assert hashlib.sha256(caminho.read_bytes()).hexdigest() == antes


def test_nao_altera_o_arquivo_quando_falha(tmp_path: Path) -> None:
    caminho = escrever(tmp_path, INDICE_MINIMO + "respostas: []\n")
    antes = hashlib.sha256(caminho.read_bytes()).hexdigest()

    with pytest.raises(IndiceIlegivel):
        carregar_indice(caminho)

    assert hashlib.sha256(caminho.read_bytes()).hexdigest() == antes


@pytest.mark.parametrize(
    "conteudo",
    [
        "respostas: [\nSENTINELA_NAO_DEVE_VAZAR\n",
        "respostas: []\nrespostas: [SENTINELA_NAO_DEVE_VAZAR]\n",
        "respostas: !!python/object/apply:os.system ['SENTINELA_NAO_DEVE_VAZAR']\n",
    ],
)
def test_mensagem_nao_ecoa_conteudo_do_arquivo(
    tmp_path: Path, conteudo: str
) -> None:
    """A mensagem carrega categoria e caminho — nunca o que havia dentro."""
    caminho = escrever(tmp_path, conteudo)

    with pytest.raises(IndiceIlegivel) as erro:
        carregar_indice(caminho)

    assert "SENTINELA_NAO_DEVE_VAZAR" not in str(erro.value)


def test_causa_tecnica_fica_encadeada(tmp_path: Path) -> None:
    caminho = escrever(tmp_path, "respostas: [\n")

    with pytest.raises(IndiceIlegivel) as erro:
        carregar_indice(caminho)

    assert erro.value.__cause__ is not None


def test_nao_preenche_campo_ausente_opcional(tmp_path: Path) -> None:
    """I5: `itera_sobre` ausente continua ausente — sem valor padrão."""
    caminho = escrever(tmp_path, INDICE_MINIMO)

    fragmento = carregar_indice(caminho)["respostas"][0]["fragmentos"][0]

    assert "itera_sobre" not in fragmento
    assert set(fragmento) == {"id", "status", "bindings"}


def test_preserva_a_ordem_produzida_pelo_analisador(tmp_path: Path) -> None:
    """I5: nada é reordenado depois da análise."""
    caminho = escrever(tmp_path, INDICE_COMPLETO)

    fragmento = carregar_indice(caminho)["respostas"][0]["fragmentos"][0]

    assert list(fragmento) == ["id", "status", "itera_sobre", "bindings"]


# 6. Provas estruturais sobre o módulo de produção


def arvore_do_modulo() -> ast.Module:
    return ast.parse(MODULO.read_text(encoding="utf-8"))


def modulos_importados() -> set[str]:
    importados: set[str] = set()
    for no in ast.walk(arvore_do_modulo()):
        if isinstance(no, ast.Import):
            importados.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            importados.add(no.module)
    return importados


def test_nao_importa_o_carregador_da_base_comercial() -> None:
    """I2: nenhuma fonte comercial paralela entra por aqui."""
    assert "casa77_sdr.knowledge" not in modulos_importados()


def test_importa_apenas_o_validador_de_e1_do_pacote() -> None:
    """I3 e I4: a única dependência interna é o validador estrutural."""
    internos = {
        nome
        for nome in modulos_importados()
        if nome.startswith("casa77_sdr")
    }

    assert internos == {"casa77_sdr.response_index"}


def test_nao_menciona_a_base_comercial() -> None:
    codigo = MODULO.read_text(encoding="utf-8")

    assert "casa77.yaml" not in codigo
    assert "respostas-aprovadas.md" not in codigo


def test_nao_redefine_vocabulario_fechado_de_e1() -> None:
    """I3: status, mecanismo, origem, formato e predicado vivem só em E1."""
    codigo = MODULO.read_text(encoding="utf-8")
    reservados = (
        "APROVADO",
        "AGUARDA_APROVACAO",
        "BLOQUEADO",
        "RENDERIZADO",
        "ASSERTIVA",
        "RUNTIME_AUTORITATIVO",
        "EH_VERDADEIRO",
        "EH_FALSO",
        "inteiro_agrupado",
        "simbolo_moeda",
        "consulta_calendario_valida",
        "data_disponivel",
    )

    for termo in reservados:
        assert termo not in codigo


def test_nao_declara_colecao_de_vocabulario() -> None:
    """Nenhum `frozenset`/`set` de constantes é declarado no carregador."""
    chamadas = {
        no.func.id
        for no in ast.walk(arvore_do_modulo())
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Name)
    }

    assert "frozenset" not in chamadas
    for no in ast.walk(arvore_do_modulo()):
        assert not isinstance(no, ast.Set)


def test_nao_tem_constante_comercial() -> None:
    """I2: nenhum número da base autoritativa vive no código do carregador.

    Segue o precedente de `test_carregador_nao_tem_constante_comercial`: os
    valores comerciais são **derivados da fonte autoritativa** em tempo de
    teste, nunca copiados para cá. A prova é de ausência de valor comercial
    hardcoded — literal numérico de qualquer espécie continua permitido.
    """
    reais = yaml.safe_load(YAML_REAL.read_text(encoding="utf-8"))
    comerciais = {
        reais["capacidade"]["convidados_sentados"],
        reais["capacidade"]["formato_coquetel"],
    }
    for pacote in reais["precos"]["pacotes"]:
        comerciais.update(
            valor
            for valor in pacote.values()
            if isinstance(valor, int) and not isinstance(valor, bool)
        )

    literais = {
        no.value
        for no in ast.walk(arvore_do_modulo())
        if isinstance(no, ast.Constant)
        and isinstance(no.value, int)
        and not isinstance(no.value, bool)
    }

    assert not (literais & comerciais)


def identificadores_do_codigo() -> set[str]:
    """Nomes e atributos realmente usados — docstring e comentário ficam fora.

    A prova precisa olhar o **código**, não a prosa: o módulo cita `glob` na
    docstring exatamente para negá-lo, e uma varredura textual leria isso como
    violação.
    """
    arvore = arvore_do_modulo()
    usados: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Name):
            usados.add(no.id)
        elif isinstance(no, ast.Attribute):
            usados.add(no.attr)
    return usados


def test_nao_abre_arquivo_para_escrita() -> None:
    """I1: nenhuma escrita, criação, movimentação ou remoção."""
    usados = identificadores_do_codigo()
    proibidos = {
        "write_text",
        "write_bytes",
        "open",
        "mkdir",
        "unlink",
        "rename",
        "replace",
        "touch",
        "rmtree",
        "safe_dump",
        "dump",
    }

    assert usados & proibidos == set()


def test_parser_e_exclusivamente_seguro() -> None:
    """§9: o analisador parte de `SafeLoader` e nada mais é ampliado."""
    codigo = MODULO.read_text(encoding="utf-8")

    assert "yaml.SafeLoader" in codigo
    for inseguro in (
        "yaml.Loader",
        "yaml.FullLoader",
        "yaml.UnsafeLoader",
        "unsafe_load",
        "full_load",
        "add_constructor",
        "add_multi_constructor",
    ):
        assert inseguro not in codigo


def test_leitor_deriva_de_safeloader() -> None:
    import yaml

    from casa77_sdr import response_index_load

    leitor = response_index_load._LeitorEstrito

    assert issubclass(leitor, yaml.SafeLoader)
    assert not issubclass(leitor, yaml.UnsafeLoader)


def test_load_recebe_o_leitor_estrito() -> None:
    """Se `yaml.load` for usado, o `Loader` é a subclasse privada."""
    for no in ast.walk(arvore_do_modulo()):
        if not isinstance(no, ast.Call):
            continue
        alvo = no.func
        if not (isinstance(alvo, ast.Attribute) and alvo.attr == "load"):
            continue
        loaders = [
            palavra.value
            for palavra in no.keywords
            if palavra.arg == "Loader"
        ]
        assert loaders, "yaml.load sem Loader explícito"
        for loader in loaders:
            assert isinstance(loader, ast.Name)
            assert loader.id == "_LeitorEstrito"


def test_api_publica_e_fechada() -> None:
    from casa77_sdr import response_index_load

    assert response_index_load.__all__ == ["IndiceIlegivel", "carregar_indice"]


def test_indice_ilegivel_deriva_de_exception() -> None:
    assert issubclass(IndiceIlegivel, Exception)


def test_indice_ilegivel_nao_se_confunde_com_indice_invalido() -> None:
    assert not issubclass(IndiceIlegivel, IndiceInvalido)
    assert not issubclass(IndiceInvalido, IndiceIlegivel)


def test_nao_e_exportado_pelo_init() -> None:
    codigo = MODULO_INIT.read_text(encoding="utf-8")

    assert "response_index_load" not in codigo
    assert "carregar_indice" not in codigo


# 7. Fronteiras preservadas pela entrega


def test_carregador_nao_conhece_caminho_padrao() -> None:
    """§6: sem caminho implícito, descoberta, glob ou variável de ambiente."""
    usados = identificadores_do_codigo()
    descoberta = {
        "glob",
        "rglob",
        "iterdir",
        "walk",
        "environ",
        "getenv",
        "cwd",
        "home",
        "expanduser",
    }

    assert usados & descoberta == set()
    assert not {"os", "glob"} & modulos_importados()


def test_carregar_indice_exige_caminho_explicito() -> None:
    import inspect

    assinatura = inspect.signature(carregar_indice)
    parametros = list(assinatura.parameters.values())

    assert len(parametros) == 1
    assert parametros[0].default is inspect.Parameter.empty


def test_devolve_a_estrutura_do_analisador(tmp_path: Path) -> None:
    """I5: o que volta é o objeto produzido pela análise, sem cópia retocada."""
    import yaml

    caminho = escrever(tmp_path, INDICE_COMPLETO)
    esperado: Any = yaml.safe_load(INDICE_COMPLETO)

    assert carregar_indice(caminho) == esperado

"""Persistência operacional (3B.3) — contrato abstrato + implementação em memória.

Este módulo define o limite de persistência operacional autorizado por
`docs/07-arquitetura-motor-respostas.md` §7.3/§7.4 (B1/B2): um contrato
abstrato mínimo e uma implementação volátil em memória, exclusiva para
testes da arquitetura (M1). A implementação em memória perde tudo ao
reiniciar e **não** sustenta operação real (M2, M3).

A persistência é infraestrutura de estado, nunca camada de decisão:

- não cria atendimento em consulta (N6);
- não calcula, valida nem interpreta valor comercial;
- armazena estado da conversa e resultado de qualificação como dados
  opacos, sem transformação semântica;
- não executa transição, não resolve identidade (T36/T37), não decide
  handoff nem emissão.

Ela apenas informa sucesso, dados recuperados ou falha explícita aos
consumidores futuros. Chave de idempotência chega pronta e opaca — hash,
janela temporal e composição pertencem ao futuro `NormalizadorEntrada`.
"""

from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class FalhaDePersistencia(Exception):
    """Falha explícita de gravação.

    Distinta, por construção, de "não encontrado": ausência de registro é
    resultado normal de consulta (`ResultadoRecuperacao.NAO_ENCONTRADO`);
    esta exceção sinaliza que uma operação de escrita não foi concluída.
    """


class ResultadoRecuperacao(StrEnum):
    """Vereditos possíveis da recuperação por identificador (§6.1.1)."""

    ENCONTRADO = "encontrado"
    NAO_ENCONTRADO = "nao_encontrado"
    INCOMPATIVEL = "incompativel"


@dataclass(frozen=True)
class RegistroAtendimento:
    """Registro transportado pela persistência sem interpretação.

    Estado da conversa, resultado de qualificação, dados coletados,
    pendências e motivos são opacos: nenhum enum, validação ou
    transformação semântica acontece aqui — os valores pertencem aos
    componentes que os produzem e consomem.
    """

    id_atendimento: str
    canal: str
    contato: str
    estado_conversa: str | None = None
    dados_coletados: dict[str, Any] = field(default_factory=dict)
    resultado_qualificacao: str | None = None
    pendencias_resposta: tuple[str, ...] = ()
    motivo_incompatibilidade: str | None = None
    motivos_handoff: tuple[str, ...] = ()


@dataclass(frozen=True)
class RecuperacaoPorId:
    """Resultado da recuperação por identificador.

    `registro` só é preenchido quando o veredito é ENCONTRADO: um registro
    incompatível com canal ou contato nunca vaza na resposta pública.
    """

    resultado: ResultadoRecuperacao
    registro: RegistroAtendimento | None = None


@dataclass(frozen=True)
class ProcessamentoPendente:
    """Mensagem ou processamento preservado de forma opaca para retentativa.

    A persistência não reprocessa, não interpreta e não decide quando
    reenviar — apenas preserva e devolve (S4, Q4, A7).
    """

    canal: str
    contato: str
    conteudo: str


class PersistenciaOperacional(ABC):
    """Contrato abstrato da persistência operacional (B1).

    Toda implementação fornece exatamente estas operações; nenhuma delas
    cria atendimento implicitamente, calcula valor ou interpreta conteúdo.
    """

    @abstractmethod
    def criar(self, registro: RegistroAtendimento) -> None:
        """Cria explicitamente um registro novo.

        Identificador já existente é erro do chamador (`ValueError`), nunca
        substituição silenciosa.
        """

    @abstractmethod
    def gravar(self, registro: RegistroAtendimento) -> None:
        """Substitui explicitamente um registro existente.

        Identificador inexistente é erro do chamador (`ValueError`):
        gravação nunca cria atendimento (N6).
        """

    @abstractmethod
    def recuperar_por_id(
        self, id_atendimento: str, canal: str, contato: str
    ) -> RecuperacaoPorId:
        """Recupera por identificador, validando compatibilidade com canal + contato.

        Nunca cria registro; incompatível não expõe dados (N3–N6).
        """

    @abstractmethod
    def consultar_por_contato(
        self, canal: str, contato: str
    ) -> tuple[RegistroAtendimento, ...]:
        """Devolve os registros armazenados do par canal + contato.

        Sem política de "recente", "ativo" ou "candidato": relevância é
        responsabilidade de outra camada.
        """

    @abstractmethod
    def chave_processada(self, chave: str) -> bool:
        """Informa se a chave de idempotência (opaca, já pronta) foi marcada."""

    @abstractmethod
    def marcar_chave_processada(self, chave: str) -> None:
        """Marca explicitamente a chave de idempotência como processada."""

    @abstractmethod
    def preservar_pendente(self, pendente: ProcessamentoPendente) -> None:
        """Preserva um processamento pendente, de forma opaca."""

    @abstractmethod
    def recuperar_pendentes(self) -> tuple[ProcessamentoPendente, ...]:
        """Devolve os processamentos pendentes preservados, sem interpretá-los."""


class PersistenciaEmMemoria(PersistenciaOperacional):
    """Implementação volátil em memória, exclusiva para testes (B2, M1).

    Somente RAM: sem arquivo, sem banco, sem rede, sem processo externo.
    Não é confiável para operação real (M2, M3) — perde estado,
    idempotência e pendentes ao reiniciar.

    `simular_falha_de_gravacao`, quando ativo, faz `criar` e `gravar`
    falharem com `FalhaDePersistencia` sem alterar nada — falha específica
    e controlada dessas duas operações de escrita, para teste (B3). O
    mecanismo de pendentes é separado e não é coberto por essa simulação;
    nada aqui afirma que uma indisponibilidade total preserva dados.

    Cópias defensivas na entrada e na saída impedem que mutação externa de
    `dados_coletados` altere silenciosamente o estado interno.
    """

    def __init__(self) -> None:
        self._registros: dict[str, RegistroAtendimento] = {}
        self._chaves_processadas: set[str] = set()
        self._pendentes: list[ProcessamentoPendente] = []
        self.simular_falha_de_gravacao = False

    def criar(self, registro: RegistroAtendimento) -> None:
        if self.simular_falha_de_gravacao:
            raise FalhaDePersistencia(
                f"Falha simulada ao criar o registro {registro.id_atendimento}"
            )
        if registro.id_atendimento in self._registros:
            raise ValueError(
                f"Registro {registro.id_atendimento} já existe; "
                "criação nunca substitui silenciosamente"
            )
        self._registros[registro.id_atendimento] = copy.deepcopy(registro)

    def gravar(self, registro: RegistroAtendimento) -> None:
        if self.simular_falha_de_gravacao:
            raise FalhaDePersistencia(
                f"Falha simulada ao gravar o registro {registro.id_atendimento}"
            )
        if registro.id_atendimento not in self._registros:
            raise ValueError(
                f"Registro {registro.id_atendimento} não existe; "
                "gravação nunca cria atendimento"
            )
        self._registros[registro.id_atendimento] = copy.deepcopy(registro)

    def recuperar_por_id(
        self, id_atendimento: str, canal: str, contato: str
    ) -> RecuperacaoPorId:
        armazenado = self._registros.get(id_atendimento)
        if armazenado is None:
            return RecuperacaoPorId(resultado=ResultadoRecuperacao.NAO_ENCONTRADO)
        if armazenado.canal != canal or armazenado.contato != contato:
            return RecuperacaoPorId(resultado=ResultadoRecuperacao.INCOMPATIVEL)
        return RecuperacaoPorId(
            resultado=ResultadoRecuperacao.ENCONTRADO,
            registro=copy.deepcopy(armazenado),
        )

    def consultar_por_contato(
        self, canal: str, contato: str
    ) -> tuple[RegistroAtendimento, ...]:
        return tuple(
            copy.deepcopy(registro)
            for registro in self._registros.values()
            if registro.canal == canal and registro.contato == contato
        )

    def chave_processada(self, chave: str) -> bool:
        return chave in self._chaves_processadas

    def marcar_chave_processada(self, chave: str) -> None:
        self._chaves_processadas.add(chave)

    def preservar_pendente(self, pendente: ProcessamentoPendente) -> None:
        self._pendentes.append(pendente)

    def recuperar_pendentes(self) -> tuple[ProcessamentoPendente, ...]:
        return tuple(self._pendentes)

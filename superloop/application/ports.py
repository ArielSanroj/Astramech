"""Superloop ports (SUPERLOOP.md §4.2) — interfaces que la application necesita."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..domain.entities import (
    Producto, Snapshot, DecisionRecomendada, RegistroCanonicoEntry, Aprendizaje,
)


class FuenteDeDatos(ABC):
    @abstractmethod
    def observar(self, producto: Producto) -> Snapshot: ...


class RegistroCanonico(ABC):
    @abstractmethod
    def upsert(self, entry: RegistroCanonicoEntry) -> None: ...
    @abstractmethod
    def get(self, producto_id: str) -> RegistroCanonicoEntry | None: ...
    @abstractmethod
    def list_productos(self) -> list[Producto]: ...


class DecisionLedger(ABC):
    @abstractmethod
    def registrar(self, decision: DecisionRecomendada) -> str: ...
    @abstractmethod
    def ultimos_aprendizajes(self, producto_id: str, limit: int = 5) -> list[Aprendizaje]: ...
    @abstractmethod
    def actualizar_aprobacion(self, decision_id: str, estado: str, aprobador: str | None) -> None: ...


class CanalDePropuesta(ABC):
    @abstractmethod
    def proponer(self, business_card: dict[str, Any], evidence_pack: dict[str, Any]) -> None: ...


class EjecutorDeAcciones(ABC):
    """ORCHESTRATE — SIEMPRE gated (R1)."""
    @abstractmethod
    def ejecutar(self, decision: dict[str, Any]) -> dict[str, Any]: ...


class ProveedorDeTiempo(ABC):
    @abstractmethod
    def ahora(self) -> str: ...


class ProveedorDeIdentidad(ABC):
    @abstractmethod
    def nuevo_id(self, prefijo: str) -> str: ...

"""Objeto permanente: Representante de la marca (entrevista de satisfacción)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Representante:
    """Uno de los 3 representantes que realizan la entrevista de satisfacción."""

    id: int
    ocupado: bool = False
    invitado_actual_id: int | None = None

    def ocupar(self, invitado_id: int) -> None:
        self.ocupado = True
        self.invitado_actual_id = invitado_id

    def liberar(self) -> None:
        self.ocupado = False
        self.invitado_actual_id = None

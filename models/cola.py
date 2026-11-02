"""Objeto permanente: Cola FIFO genérica, con soporte opcional de abandono."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class Cola:
    """Cola FIFO de invitados esperando un recurso.

    Se usa tanto para la cola de acreditación como para la de entrevista.
    Si `tiempo_paciencia` está definido, un invitado que espera más de ese
    tiempo sin ser atendido abandona la cola (evento de abandono).
    """

    nombre: str
    tiempo_paciencia: float | None = None
    _elementos: deque[int] = field(default_factory=deque)

    def encolar(self, invitado_id: int) -> None:
        self._elementos.append(invitado_id)

    def desencolar(self) -> int | None:
        if not self._elementos:
            return None
        return self._elementos.popleft()

    def quitar(self, invitado_id: int) -> None:
        """Quita un invitado puntual de la cola (usado al abandonar por espera)."""
        self._elementos.remove(invitado_id)

    @property
    def cantidad(self) -> int:
        return len(self._elementos)

    def __contains__(self, invitado_id: int) -> bool:
        return invitado_id in self._elementos

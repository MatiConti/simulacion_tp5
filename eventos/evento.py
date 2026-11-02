"""Objeto Evento: una entrada del calendario de eventos (FEL)."""
from __future__ import annotations

from dataclasses import dataclass, field

from .tipo_evento import TipoEvento


@dataclass(order=True)
class Evento:
    """Un evento futuro programado en el calendario de eventos.

    Ordenable por `tiempo` para que el calendario (heap) lo procese en el
    orden correcto; el resto de los campos no participa en la comparación.
    """

    tiempo: float
    tipo: TipoEvento = field(compare=False)
    invitado_id: int | None = field(default=None, compare=False)
    cancelado: bool = field(default=False, compare=False)

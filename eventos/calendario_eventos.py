"""Calendario de eventos futuros (FEL): próximos eventos ordenados por tiempo."""
from __future__ import annotations

import heapq

from .evento import Evento
from .tipo_evento import TipoEvento


class CalendarioEventos:
    """Lista de eventos futuros (FEL), siempre devuelve el de menor tiempo.

    La cancelación es lógica (lazy deletion): se marca el evento como
    cancelado y se descarta al extraerlo, en vez de reconstruir el heap.
    Se usa, por ejemplo, para cancelar el evento de abandono de un invitado
    cuando lo alcanza a atender un representante antes de los 5 minutos.
    """

    def __init__(self) -> None:
        self._heap: list[Evento] = []

    def programar(self, evento: Evento) -> None:
        heapq.heappush(self._heap, evento)

    def proximo(self) -> Evento | None:
        while self._heap:
            evento = heapq.heappop(self._heap)
            if not evento.cancelado:
                return evento
        return None

    def cancelar(self, invitado_id: int, tipo: TipoEvento) -> None:
        """Marca como cancelado el próximo evento pendiente que coincida."""
        for evento in self._heap:
            if (
                not evento.cancelado
                and evento.invitado_id == invitado_id
                and evento.tipo is tipo
            ):
                evento.cancelado = True
                return

    def proximo_nombre(self) -> str:
        """Nombre y hora del próximo evento pendiente, para mostrar en la GUI."""
        activos = [e for e in self._heap if not e.cancelado]
        if not activos:
            return ""
        e = min(activos)
        sufijo = f" #{e.invitado_id}" if e.invitado_id is not None else ""
        return f"{e.tipo.value}{sufijo} (t={e.tiempo:.2f})"

    @property
    def vacio(self) -> bool:
        return all(e.cancelado for e in self._heap)

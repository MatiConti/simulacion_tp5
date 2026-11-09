"""Representa una fila del vector de estado (una iteración de la simulación)."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FilaVectorEstado:
    """Estado completo del sistema en el instante en que ocurrió un evento.

    Se arma una instancia por cada evento procesado durante la simulación y
    es lo que se muestra/exporta como vector de estado. Todo queda aplanado a
    diccionarios para que sea directo mostrarlo en la tabla.

    Los RND y tiempos generados aparecen solo en la fila en la que se
    generaron (en las demás quedan vacíos); las horas de los próximos eventos
    se arrastran mientras el evento siga pendiente.
    """

    numero_fila: int
    hora_simulada: float
    nombre_evento: str
    invitado_evento_id: int | None = None
    proximo_evento: str = ""
    es_fila_final: bool = False

    # Eventos de llegada: {"rnd", "tiempo", "proxima"}
    llegada_auto: dict = field(default_factory=dict)
    llegada_peaton: dict = field(default_factory=dict)

    # Objetos permanentes
    operarios: dict[int, dict] = field(default_factory=dict)
    representantes: dict[int, dict] = field(default_factory=dict)
    colas: dict[str, int] = field(default_factory=dict)

    # Objetos temporales presentes en el sistema en este instante
    invitados: dict[int, dict] = field(default_factory=dict)

    # Variables auxiliares (acumuladores, contadores)
    acumuladores: dict[str, float] = field(default_factory=dict)

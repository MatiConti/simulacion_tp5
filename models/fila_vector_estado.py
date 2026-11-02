"""Representa una fila del vector de estado (una iteración de la simulación)."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FilaVectorEstado:
    """Estado completo del sistema en el instante en que ocurrió un evento.

    Se arma una instancia por cada evento procesado durante la simulación y
    es lo que se muestra/exporta como vector de estado.
    """

    numero_fila: int
    hora_simulada: float
    nombre_evento: str
    proximos_eventos: list[str] = field(default_factory=list)

    # Estado de los objetos permanentes y temporales en este instante, ya
    # aplanado a diccionarios para que sea directo mostrarlo en la tabla.
    operarios: dict[int, dict] = field(default_factory=dict)
    representantes: dict[int, dict] = field(default_factory=dict)
    invitados: dict[int, dict] = field(default_factory=dict)

    # Variables auxiliares (acumuladores, contadores)
    acumuladores: dict[str, float] = field(default_factory=dict)

    # Números aleatorios usados para las variables aleatorias de este evento,
    # para trazabilidad (consigna: mostrar el RND usado en cada caso).
    numeros_aleatorios: dict[str, float] = field(default_factory=dict)

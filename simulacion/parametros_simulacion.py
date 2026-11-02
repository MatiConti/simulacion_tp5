"""Parámetros configurables de la simulación.

Todos los valores marcados en rojo en el enunciado del modelo son
parametrizables; acá están con su valor por defecto (el del enunciado).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ParametrosSimulacion:
    # Condición de corte (consigna general del TP)
    tiempo_max: float = 480.0        # X: tiempo a simular (minutos)
    iteraciones_max: int = 100_000   # N: tope de filas del vector de estado

    # Invitados con auto: llegan cada 5 +/- 2 minutos (uniforme)
    llegada_auto_min: float = 3.0
    llegada_auto_max: float = 7.0
    cantidad_operarios: int = 3
    media_tiempo_acreditacion: float = 2.0   # exponencial
    tiempo_estacionar: float = 3.0           # fijo

    # Invitados peatonales
    entre_llegadas_peaton: float = 2.5       # fijo

    # Sala de degustación
    media_permanencia_sala: float = 20.0     # exponencial

    # Entrevista de satisfacción
    cantidad_representantes: int = 3
    paciencia_entrevista: float = 5.0        # abandono si espera más de esto
    p_con_auto: int = 100
    p_peaton: int = 70
    h_integracion: float = 0.1               # paso de Euler
    minutos_por_unidad_integracion: float = 10.0

    # Generador congruencial mixto (consigna general del TP)
    semilla: int = 1234
    constante_multiplicativa: int = 1714
    constante_aditiva: int = 1221
    modulo: int = 3922

    # Visualización del vector de estado (parámetros i, j de la consigna)
    filas_a_mostrar: int = 100       # i
    hora_inicio_vista: float = 0.0   # j

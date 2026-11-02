"""Integración numérica por el método de Euler.

Se usa para la duración de la entrevista de satisfacción: se integra
dD/dt = P/5 desde D=0 hasta que D alcanza el valor de P (ver SUPUESTOS.md,
punto 4), con paso h parametrizable. No es una variable aleatoria: P queda
determinado por el tipo de invitado.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PasoIntegracion:
    """Un paso de la integración, para poder mostrarlo en la interfaz."""

    t: float
    d: float


def integrar_duracion_entrevista(p: int, h: float = 0.1) -> tuple[float, list[PasoIntegracion]]:
    """Integra dD/dt = P/5 por Euler hasta que D alcanza P.

    Devuelve (t_final, pasos): t_final es la duración de la entrevista en
    unidades de integración (1 unidad = 10 min), y pasos es el detalle
    paso a paso de la integración para mostrar/exportar.
    """
    t = 0.0
    d = 0.0
    tasa = p / 5
    pasos = [PasoIntegracion(t=t, d=d)]
    while d < p:
        d += tasa * h
        t += h
        pasos.append(PasoIntegracion(t=t, d=d))
    return t, pasos

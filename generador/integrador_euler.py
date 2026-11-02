"""Integración numérica por el método de Euler.

Se usa para la duración de la entrevista de satisfacción: se integra
dD/dt = P/5 desde D=0 hasta que D alcanza el valor de P (ver SUPUESTOS.md,
punto 4), con paso h parametrizable. No es una variable aleatoria: P queda
determinado por el tipo de invitado.
"""
from __future__ import annotations

from dataclasses import dataclass

# Tolerancia para comparar D con P: sumar h muchas veces acumula error de
# redondeo (p. ej. 50 pasos de 1.4 dan 69.99999999 en vez de 70), y sin
# tolerancia se haría un paso de más.
_TOLERANCIA = 1e-9


@dataclass
class PasoIntegracion:
    """Un paso de la integración, para poder mostrarlo en la interfaz.

    Cada fila es la del método de Euler: t, D, la derivada evaluada en ese
    punto y el D del paso siguiente.
    """

    t: float
    d: float
    derivada: float
    d_siguiente: float


def integrar_duracion_entrevista(p: float, h: float = 0.1) -> tuple[float, list[PasoIntegracion]]:
    """Integra dD/dt = P/5 por Euler (D_{n+1} = D_n + h * P/5) hasta que D >= P.

    Devuelve (t_final, pasos): t_final es la duración de la entrevista en
    unidades de integración (1 unidad = 10 min por defecto), y pasos es el
    detalle paso a paso de la integración para mostrar/exportar.
    """
    if h <= 0:
        raise ValueError("El paso h debe ser positivo")
    if p <= 0:
        return 0.0, [PasoIntegracion(t=0.0, d=0.0, derivada=0.0, d_siguiente=0.0)]

    derivada = p / 5
    n = 0
    d = 0.0
    pasos: list[PasoIntegracion] = []
    while d < p - _TOLERANCIA:
        d_siguiente = d + h * derivada
        # t se calcula como n*h (no sumando h) para no acumular error.
        pasos.append(PasoIntegracion(t=round(n * h, 10), d=d, derivada=derivada, d_siguiente=d_siguiente))
        d = d_siguiente
        n += 1
    pasos.append(PasoIntegracion(t=round(n * h, 10), d=d, derivada=derivada, d_siguiente=d))
    return round(n * h, 10), pasos

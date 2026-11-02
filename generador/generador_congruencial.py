"""Generador de números pseudoaleatorios U[0,1) — congruencial mixto.

Parámetros fijados por la consigna del TP: semilla=1234, constante
multiplicativa=1714, constante aditiva=1221, módulo=3922. Es un único
generador compartido por todas las variables aleatorias del sistema (no se
usa el generador propio del lenguaje de programación).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GeneradorCongruencial:
    semilla: int = 1234
    constante_multiplicativa: int = 1714
    constante_aditiva: int = 1221
    modulo: int = 3922
    _x: int = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._x = self.semilla

    def siguiente(self) -> float:
        """Devuelve el próximo número pseudoaleatorio en [0, 1)."""
        self._x = (self.constante_multiplicativa * self._x + self.constante_aditiva) % self.modulo
        return self._x / self.modulo

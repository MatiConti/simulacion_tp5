"""Variable aleatoria con distribución uniforme, sobre el generador compartido."""
from __future__ import annotations

from .generador_congruencial import GeneradorCongruencial


class DistribucionUniforme:
    """Genera valores U(minimo, maximo), p. ej. entre llegadas con auto (5 +/- 2)."""

    def __init__(self, generador: GeneradorCongruencial, minimo: float, maximo: float) -> None:
        self.generador = generador
        self.minimo = minimo
        self.maximo = maximo

    def generar(self) -> tuple[float, float]:
        """Devuelve (valor_generado, rnd_usado)."""
        rnd = self.generador.siguiente()
        valor = self.minimo + rnd * (self.maximo - self.minimo)
        return valor, rnd

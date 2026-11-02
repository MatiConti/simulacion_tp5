"""Variable aleatoria exponencial negativa, por el método de la transformada
inversa, sobre el generador compartido."""
from __future__ import annotations

import math

from .generador_congruencial import GeneradorCongruencial


class DistribucionExponencial:
    """Genera valores exponenciales, p. ej. tiempo de acreditación o permanencia en sala."""

    def __init__(self, generador: GeneradorCongruencial, media: float) -> None:
        self.generador = generador
        self.media = media

    def generar(self) -> tuple[float, float]:
        """Devuelve (valor_generado, rnd_usado)."""
        rnd = self.generador.siguiente()
        valor = -self.media * math.log(1 - rnd)
        return valor, rnd

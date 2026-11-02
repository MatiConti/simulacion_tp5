"""Generador de números aleatorios, variables aleatorias e integración numérica."""

from .generador_congruencial import GeneradorCongruencial
from .distribucion_uniforme import DistribucionUniforme
from .distribucion_exponencial import DistribucionExponencial
from .integrador_euler import PasoIntegracion, integrar_duracion_entrevista

__all__ = [
    "GeneradorCongruencial",
    "DistribucionUniforme",
    "DistribucionExponencial",
    "PasoIntegracion",
    "integrar_duracion_entrevista",
]

"""Objetos (permanentes y temporales) del sistema de simulación.

Todos los objetos identificados en el análisis viven en este paquete, un
archivo por clase:

- `Invitado` (objeto temporal)
- `Operario`, `Representante` (objetos permanentes, recursos con servidores)
- `Cola` (objeto permanente, usado para acreditación y entrevista)
- `FilaVectorEstado` (una fila del vector de estado de la simulación)
"""

from .invitado import EstadoInvitado, Invitado, TipoInvitado
from .operario import Operario
from .representante import Representante
from .cola import Cola
from .fila_vector_estado import FilaVectorEstado

__all__ = [
    "Invitado",
    "TipoInvitado",
    "EstadoInvitado",
    "Operario",
    "Representante",
    "Cola",
    "FilaVectorEstado",
]

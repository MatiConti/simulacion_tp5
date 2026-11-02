"""Variables auxiliares (acumuladores) usadas para responder los objetivos del TP."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Acumuladores:
    maximo_tiempo_en_sala: float = 0.0
    cantidad_invitados_a_entrevista: int = 0
    cantidad_abandonos_entrevista: int = 0
    cantidad_entrevistas_completas: int = 0

    def registrar_tiempo_en_sala(self, tiempo: float) -> None:
        if tiempo > self.maximo_tiempo_en_sala:
            self.maximo_tiempo_en_sala = tiempo

    @property
    def porcentaje_abandono_entrevista(self) -> float:
        if self.cantidad_invitados_a_entrevista == 0:
            return 0.0
        return 100 * self.cantidad_abandonos_entrevista / self.cantidad_invitados_a_entrevista

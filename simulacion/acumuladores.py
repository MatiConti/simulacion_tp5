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
    def cantidad_retirados(self) -> int:
        """Invitados que ya se fueron del predio (con o sin encuesta)."""
        return self.cantidad_abandonos_entrevista + self.cantidad_entrevistas_completas

    @property
    def porcentaje_abandono_entrevista(self) -> float:
        """% de invitados retirados que se fueron sin responder la encuesta.

        El denominador son los que ya se retiraron: los que al cortar la
        simulación siguen esperando o en entrevista todavía no tienen resultado.
        """
        if self.cantidad_retirados == 0:
            return 0.0
        return 100 * self.cantidad_abandonos_entrevista / self.cantidad_retirados

"""Objeto permanente: Operario de portón (acreditación)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Operario:
    """Uno de los 3 operarios que acreditan invitados en el portón de ingreso.

    Acredita un invitado/coche por vez. Se usa para calcular el tiempo
    ocioso promedio pedido como objetivo de la simulación.
    """

    id: int
    ocupado: bool = False
    invitado_actual_id: int | None = None
    hora_fin_acreditacion: float | None = None
    tiempo_ocioso_acumulado: float = 0.0
    hora_ultimo_cambio_estado: float = 0.0

    def ocupar(self, invitado_id: int, hora_actual: float, hora_fin: float) -> None:
        if not self.ocupado:
            self.tiempo_ocioso_acumulado += hora_actual - self.hora_ultimo_cambio_estado
        self.ocupado = True
        self.invitado_actual_id = invitado_id
        self.hora_fin_acreditacion = hora_fin
        self.hora_ultimo_cambio_estado = hora_actual

    def liberar(self, hora_actual: float) -> None:
        self.ocupado = False
        self.invitado_actual_id = None
        self.hora_fin_acreditacion = None
        self.hora_ultimo_cambio_estado = hora_actual

    def cerrar_ocio(self, hora_actual: float) -> None:
        """Suma el período ocioso en curso hasta `hora_actual` (fin de simulación)."""
        if not self.ocupado:
            self.tiempo_ocioso_acumulado += hora_actual - self.hora_ultimo_cambio_estado
            self.hora_ultimo_cambio_estado = hora_actual

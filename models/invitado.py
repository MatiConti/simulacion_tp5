"""Objeto temporal: Invitado."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TipoInvitado(Enum):
    CON_AUTO = "con_auto"
    PEATON = "peaton"


class EstadoInvitado(Enum):
    ESPERANDO_ACREDITACION = "esperando_acreditacion"
    ACREDITANDOSE = "acreditandose"
    ESTACIONANDO = "estacionando"
    EN_SALA_DEGUSTACION = "en_sala_degustacion"
    ESPERANDO_ENTREVISTA = "esperando_entrevista"
    EN_ENTREVISTA = "en_entrevista"
    RETIRADO_CON_ENCUESTA = "retirado_con_encuesta"
    RETIRADO_SIN_ENCUESTA = "retirado_sin_encuesta"


@dataclass
class Invitado:
    """Un invitado al evento de degustación.

    P (usado en dD/dt = P/5 para la duración de la entrevista) queda
    determinado por el tipo de invitado: 100 si llegó con auto, 70 si
    llegó como peatón (ver SUPUESTOS.md, punto 4).
    """

    id: int
    tipo: TipoInvitado
    hora_llegada: float
    estado: EstadoInvitado = EstadoInvitado.ESPERANDO_ACREDITACION

    # Timestamps de cada etapa (se completan a medida que avanza en el sistema)
    hora_inicio_acreditacion: float | None = None
    hora_fin_acreditacion: float | None = None
    hora_fin_estacionamiento: float | None = None
    hora_inicio_sala: float | None = None
    hora_fin_sala: float | None = None
    hora_llegada_cola_entrevista: float | None = None
    hora_inicio_entrevista: float | None = None
    hora_fin_entrevista: float | None = None

    @property
    def p(self) -> int:
        """Valor de P usado en dD/dt = P/5 para la duración de la entrevista."""
        return 100 if self.tipo is TipoInvitado.CON_AUTO else 70

    @property
    def tiempo_en_sala(self) -> float | None:
        """Permanencia en la sala de degustación, una vez que la abandonó."""
        if self.hora_inicio_sala is None or self.hora_fin_sala is None:
            return None
        return self.hora_fin_sala - self.hora_inicio_sala

    @property
    def tiempo_espera_entrevista(self) -> float | None:
        """Tiempo esperado en la cola de entrevista hasta ser atendido."""
        if self.hora_llegada_cola_entrevista is None or self.hora_inicio_entrevista is None:
            return None
        return self.hora_inicio_entrevista - self.hora_llegada_cola_entrevista

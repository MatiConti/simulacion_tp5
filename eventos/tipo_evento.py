"""Enum con los tipos de evento del sistema."""
from enum import Enum


class TipoEvento(Enum):
    LLEGADA_INVITADO_AUTO = "llegada_invitado_auto"
    FIN_ACREDITACION = "fin_acreditacion"
    FIN_ESTACIONAMIENTO = "fin_estacionamiento"
    LLEGADA_INVITADO_PEATON = "llegada_invitado_peaton"
    FIN_PERMANENCIA_SALA = "fin_permanencia_sala"
    FIN_ENTREVISTA = "fin_entrevista"
    ABANDONO_ENTREVISTA = "abandono_entrevista"

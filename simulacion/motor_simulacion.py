"""Motor de simulación: reloj + procesamiento de eventos (vector de estado)."""
from __future__ import annotations

from typing import Callable

from eventos import CalendarioEventos, Evento, TipoEvento
from generador import (
    DistribucionExponencial,
    DistribucionUniforme,
    GeneradorCongruencial,
    PasoIntegracion,
    integrar_duracion_entrevista,
)
from models import Cola, EstadoInvitado, FilaVectorEstado, Invitado, Operario, Representante, TipoInvitado

from .acumuladores import Acumuladores
from .parametros_simulacion import ParametrosSimulacion


class MotorSimulacion:
    def __init__(self, parametros: ParametrosSimulacion) -> None:
        self.parametros = parametros

        self.generador = GeneradorCongruencial(
            semilla=parametros.semilla,
            constante_multiplicativa=parametros.constante_multiplicativa,
            constante_aditiva=parametros.constante_aditiva,
            modulo=parametros.modulo,
        )
        self.dist_entre_llegadas_auto = DistribucionUniforme(
            self.generador, parametros.llegada_auto_min, parametros.llegada_auto_max
        )
        self.dist_acreditacion = DistribucionExponencial(self.generador, parametros.media_tiempo_acreditacion)
        self.dist_permanencia_sala = DistribucionExponencial(self.generador, parametros.media_permanencia_sala)

        self.calendario = CalendarioEventos()
        self.cola_acreditacion = Cola(nombre="acreditacion")
        self.cola_entrevista = Cola(nombre="entrevista", tiempo_paciencia=parametros.paciencia_entrevista)
        self.operarios = [Operario(id=i + 1) for i in range(parametros.cantidad_operarios)]
        self.representantes = [Representante(id=i + 1) for i in range(parametros.cantidad_representantes)]

        self.invitados: dict[int, Invitado] = {}
        self.integraciones: dict[int, list[PasoIntegracion]] = {}
        self._siguiente_id_invitado = 1

        self.reloj = 0.0
        self.acumuladores = Acumuladores()
        self.filas: list[FilaVectorEstado] = []
        self.motivo_corte: str = ""

    # -- ejecución principal -------------------------------------------------

    def ejecutar(self, debe_detenerse: Callable[[], bool] | None = None) -> list[FilaVectorEstado]:
        self._programar_primera_llegada_auto()
        self._programar_primera_llegada_peaton()

        numero_fila = 0
        while True:
            if debe_detenerse is not None and debe_detenerse():
                self.motivo_corte = "detenido_por_usuario"
                break
            if numero_fila >= self.parametros.iteraciones_max:
                self.motivo_corte = "iteraciones_max"
                break
            evento = self.calendario.proximo()
            if evento is None:
                self.motivo_corte = "sin_mas_eventos"
                break
            if evento.tiempo > self.parametros.tiempo_max:
                self.motivo_corte = "tiempo_max"
                break
            self.reloj = evento.tiempo
            numeros_aleatorios = self._procesar_evento(evento)
            numero_fila += 1
            self.filas.append(self._construir_fila(numero_fila, evento, numeros_aleatorios))

        self._cerrar_acumuladores_tiempo_ocioso()
        return self.filas

    @property
    def tiempo_ocioso_promedio_operarios(self) -> float:
        return sum(o.tiempo_ocioso_acumulado for o in self.operarios) / len(self.operarios)

    def _cerrar_acumuladores_tiempo_ocioso(self) -> None:
        for operario in self.operarios:
            if not operario.ocupado:
                operario.tiempo_ocioso_acumulado += self.reloj - operario.hora_ultimo_cambio_estado
                operario.hora_ultimo_cambio_estado = self.reloj

    # -- despacho de eventos ---------------------------------------------------

    def _procesar_evento(self, evento: Evento) -> dict[str, float]:
        manejador = {
            TipoEvento.LLEGADA_INVITADO_AUTO: self._manejar_llegada_invitado_auto,
            TipoEvento.FIN_ACREDITACION: self._manejar_fin_acreditacion,
            TipoEvento.FIN_ESTACIONAMIENTO: self._manejar_fin_estacionamiento,
            TipoEvento.LLEGADA_INVITADO_PEATON: self._manejar_llegada_invitado_peaton,
            TipoEvento.FIN_PERMANENCIA_SALA: self._manejar_fin_permanencia_sala,
            TipoEvento.FIN_ENTREVISTA: self._manejar_fin_entrevista,
            TipoEvento.ABANDONO_ENTREVISTA: self._manejar_abandono_entrevista,
        }[evento.tipo]
        return manejador(evento)

    def _nuevo_invitado(self, tipo: TipoInvitado) -> Invitado:
        invitado = Invitado(id=self._siguiente_id_invitado, tipo=tipo, hora_llegada=self.reloj)
        self.invitados[invitado.id] = invitado
        self._siguiente_id_invitado += 1
        return invitado

    # -- llegada con auto / acreditación / estacionamiento ----------------------

    def _programar_primera_llegada_auto(self) -> None:
        delta, _ = self.dist_entre_llegadas_auto.generar()
        self.calendario.programar(Evento(tiempo=delta, tipo=TipoEvento.LLEGADA_INVITADO_AUTO))

    def _manejar_llegada_invitado_auto(self, evento: Evento) -> dict[str, float]:
        invitado = self._nuevo_invitado(TipoInvitado.CON_AUTO)
        numeros: dict[str, float] = {}

        delta, rnd_llegada = self.dist_entre_llegadas_auto.generar()
        numeros["entre_llegadas_auto"] = rnd_llegada
        self.calendario.programar(Evento(tiempo=self.reloj + delta, tipo=TipoEvento.LLEGADA_INVITADO_AUTO))

        operario = next((o for o in self.operarios if not o.ocupado), None)
        if operario is not None:
            rnd_acreditacion = self._iniciar_acreditacion(operario, invitado)
            numeros["tiempo_acreditacion"] = rnd_acreditacion
        else:
            invitado.estado = EstadoInvitado.ESPERANDO_ACREDITACION
            self.cola_acreditacion.encolar(invitado.id)

        return numeros

    def _iniciar_acreditacion(self, operario: Operario, invitado: Invitado) -> float:
        operario.ocupar(invitado.id, self.reloj)
        invitado.estado = EstadoInvitado.ACREDITANDOSE
        invitado.hora_inicio_acreditacion = self.reloj
        duracion, rnd = self.dist_acreditacion.generar()
        self.calendario.programar(
            Evento(tiempo=self.reloj + duracion, tipo=TipoEvento.FIN_ACREDITACION, invitado_id=invitado.id)
        )
        return rnd

    def _manejar_fin_acreditacion(self, evento: Evento) -> dict[str, float]:
        invitado = self.invitados[evento.invitado_id]
        operario = next(o for o in self.operarios if o.invitado_actual_id == invitado.id)
        operario.liberar(self.reloj)

        invitado.estado = EstadoInvitado.ESTACIONANDO
        invitado.hora_fin_acreditacion = self.reloj
        self.calendario.programar(
            Evento(
                tiempo=self.reloj + self.parametros.tiempo_estacionar,
                tipo=TipoEvento.FIN_ESTACIONAMIENTO,
                invitado_id=invitado.id,
            )
        )

        numeros: dict[str, float] = {}
        siguiente_id = self.cola_acreditacion.desencolar()
        if siguiente_id is not None:
            siguiente = self.invitados[siguiente_id]
            numeros["tiempo_acreditacion"] = self._iniciar_acreditacion(operario, siguiente)
        return numeros

    def _manejar_fin_estacionamiento(self, evento: Evento) -> dict[str, float]:
        invitado = self.invitados[evento.invitado_id]
        invitado.hora_fin_estacionamiento = self.reloj
        return self._ingresar_a_sala(invitado)

    # -- llegada peatonal / sala de degustación ---------------------------------

    def _programar_primera_llegada_peaton(self) -> None:
        self.calendario.programar(
            Evento(tiempo=self.parametros.entre_llegadas_peaton, tipo=TipoEvento.LLEGADA_INVITADO_PEATON)
        )

    def _manejar_llegada_invitado_peaton(self, evento: Evento) -> dict[str, float]:
        invitado = self._nuevo_invitado(TipoInvitado.PEATON)
        self.calendario.programar(
            Evento(
                tiempo=self.reloj + self.parametros.entre_llegadas_peaton,
                tipo=TipoEvento.LLEGADA_INVITADO_PEATON,
            )
        )
        return self._ingresar_a_sala(invitado)

    def _ingresar_a_sala(self, invitado: Invitado) -> dict[str, float]:
        invitado.estado = EstadoInvitado.EN_SALA_DEGUSTACION
        invitado.hora_inicio_sala = self.reloj
        duracion, rnd = self.dist_permanencia_sala.generar()
        self.calendario.programar(
            Evento(tiempo=self.reloj + duracion, tipo=TipoEvento.FIN_PERMANENCIA_SALA, invitado_id=invitado.id)
        )
        return {"permanencia_sala": rnd}

    def _manejar_fin_permanencia_sala(self, evento: Evento) -> dict[str, float]:
        invitado = self.invitados[evento.invitado_id]
        invitado.hora_fin_sala = self.reloj
        self.acumuladores.registrar_tiempo_en_sala(invitado.tiempo_en_sala)

        invitado.estado = EstadoInvitado.ESPERANDO_ENTREVISTA
        invitado.hora_llegada_cola_entrevista = self.reloj
        self.acumuladores.cantidad_invitados_a_entrevista += 1

        representante = next((r for r in self.representantes if not r.ocupado), None)
        if representante is not None:
            self._iniciar_entrevista(representante, invitado)
        else:
            self.cola_entrevista.encolar(invitado.id)
            self.calendario.programar(
                Evento(
                    tiempo=self.reloj + self.parametros.paciencia_entrevista,
                    tipo=TipoEvento.ABANDONO_ENTREVISTA,
                    invitado_id=invitado.id,
                )
            )
        return {}

    # -- entrevista de satisfacción ----------------------------------------------

    def _iniciar_entrevista(self, representante: Representante, invitado: Invitado) -> None:
        representante.ocupar(invitado.id)
        invitado.estado = EstadoInvitado.EN_ENTREVISTA
        invitado.hora_inicio_entrevista = self.reloj

        duracion_unidades, pasos = integrar_duracion_entrevista(invitado.p, self.parametros.h_integracion)
        self.integraciones[invitado.id] = pasos
        duracion_min = duracion_unidades * self.parametros.minutos_por_unidad_integracion
        self.calendario.programar(
            Evento(tiempo=self.reloj + duracion_min, tipo=TipoEvento.FIN_ENTREVISTA, invitado_id=invitado.id)
        )

    def _manejar_fin_entrevista(self, evento: Evento) -> dict[str, float]:
        invitado = self.invitados[evento.invitado_id]
        representante = next(r for r in self.representantes if r.invitado_actual_id == invitado.id)
        representante.liberar()

        invitado.estado = EstadoInvitado.RETIRADO_CON_ENCUESTA
        invitado.hora_fin_entrevista = self.reloj
        self.acumuladores.cantidad_entrevistas_completas += 1

        siguiente_id = self.cola_entrevista.desencolar()
        if siguiente_id is not None:
            self.calendario.cancelar(siguiente_id, TipoEvento.ABANDONO_ENTREVISTA)
            self._iniciar_entrevista(representante, self.invitados[siguiente_id])
        return {}

    def _manejar_abandono_entrevista(self, evento: Evento) -> dict[str, float]:
        invitado = self.invitados[evento.invitado_id]
        self.cola_entrevista.quitar(invitado.id)
        invitado.estado = EstadoInvitado.RETIRADO_SIN_ENCUESTA
        self.acumuladores.cantidad_abandonos_entrevista += 1
        return {}

    # -- vector de estado ---------------------------------------------------------

    def _construir_fila(self, numero_fila: int, evento: Evento, numeros_aleatorios: dict[str, float]) -> FilaVectorEstado:
        invitados_activos = {
            inv.id: self._invitado_a_dict(inv)
            for inv in self.invitados.values()
            if inv.estado not in (EstadoInvitado.RETIRADO_CON_ENCUESTA, EstadoInvitado.RETIRADO_SIN_ENCUESTA)
            or inv.id == evento.invitado_id
        }
        return FilaVectorEstado(
            numero_fila=numero_fila,
            hora_simulada=self.reloj,
            nombre_evento=evento.tipo.value,
            proximos_eventos=self.calendario.proximos_nombres(),
            operarios={o.id: {"ocupado": o.ocupado, "tiempo_ocioso_acumulado": o.tiempo_ocioso_acumulado} for o in self.operarios},
            representantes={r.id: {"ocupado": r.ocupado} for r in self.representantes},
            invitados=invitados_activos,
            acumuladores={
                "maximo_tiempo_en_sala": self.acumuladores.maximo_tiempo_en_sala,
                "cantidad_abandonos_entrevista": self.acumuladores.cantidad_abandonos_entrevista,
                "porcentaje_abandono_entrevista": self.acumuladores.porcentaje_abandono_entrevista,
                "cola_acreditacion": self.cola_acreditacion.cantidad,
                "cola_entrevista": self.cola_entrevista.cantidad,
            },
            numeros_aleatorios=numeros_aleatorios,
        )

    @staticmethod
    def _invitado_a_dict(invitado: Invitado) -> dict:
        return {
            "tipo": invitado.tipo.value,
            "estado": invitado.estado.value,
            "hora_llegada": invitado.hora_llegada,
            "p": invitado.p,
        }

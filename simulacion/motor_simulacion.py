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

NOMBRE_EVENTO_INICIO = "inicializacion"
NOMBRE_EVENTO_FIN = "fin_simulacion (X)"


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
        # Invitados que siguen en el sistema: se recorren en cada fila del
        # vector de estado, así que no conviene recorrer todos los históricos.
        self.invitados_activos: dict[int, Invitado] = {}
        self.integraciones: dict[int, list[PasoIntegracion]] = {}
        self._siguiente_id_invitado = 1

        # Próximas llegadas (para mostrarlas en el vector de estado)
        self.proxima_llegada_auto: float | None = None
        self.proxima_llegada_peaton: float | None = None

        self.reloj = 0.0
        self.acumuladores = Acumuladores()
        self.filas: list[FilaVectorEstado] = []
        self.motivo_corte: str = ""

        # Lo generado en el evento actual (se vuelca en la fila y se limpia)
        self._generado_llegada_auto: tuple[float, float] | None = None
        self._generado_acreditacion: dict[int, tuple[float, float]] = {}

    # -- ejecución principal -------------------------------------------------

    def ejecutar(self, debe_detenerse: Callable[[], bool] | None = None) -> list[FilaVectorEstado]:
        self._programar_proxima_llegada_auto()
        self._programar_proxima_llegada_peaton()
        self.filas.append(self._construir_fila(0, NOMBRE_EVENTO_INICIO, None))

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
            self._procesar_evento(evento)
            numero_fila += 1
            self.filas.append(self._construir_fila(numero_fila, evento.tipo.value, evento.invitado_id))

        if self.motivo_corte == "tiempo_max":
            # Fila del instante X (consigna): el reloj avanza hasta X sin
            # procesar ningún evento nuevo.
            self.reloj = self.parametros.tiempo_max
            self._cerrar_acumuladores_tiempo_ocioso()
            self.filas.append(self._construir_fila(numero_fila + 1, NOMBRE_EVENTO_FIN, None))
        else:
            # Cortó por N (o se detuvo): la última fila es la del último evento,
            # que ya tiene el ocio calculado hasta ese instante.
            self._cerrar_acumuladores_tiempo_ocioso()
        self.filas[-1].es_fila_final = True
        return self.filas

    @property
    def tiempo_ocioso_promedio_operarios(self) -> float:
        return sum(o.tiempo_ocioso_acumulado for o in self.operarios) / len(self.operarios)

    @property
    def porcentaje_ocio_operarios(self) -> float:
        if self.reloj <= 0:
            return 0.0
        return 100 * self.tiempo_ocioso_promedio_operarios / self.reloj

    def _cerrar_acumuladores_tiempo_ocioso(self) -> None:
        for operario in self.operarios:
            operario.cerrar_ocio(self.reloj)

    # -- despacho de eventos ---------------------------------------------------

    def _procesar_evento(self, evento: Evento) -> None:
        manejador = {
            TipoEvento.LLEGADA_INVITADO_AUTO: self._manejar_llegada_invitado_auto,
            TipoEvento.FIN_ACREDITACION: self._manejar_fin_acreditacion,
            TipoEvento.FIN_ESTACIONAMIENTO: self._manejar_fin_estacionamiento,
            TipoEvento.LLEGADA_INVITADO_PEATON: self._manejar_llegada_invitado_peaton,
            TipoEvento.FIN_PERMANENCIA_SALA: self._manejar_fin_permanencia_sala,
            TipoEvento.FIN_ENTREVISTA: self._manejar_fin_entrevista,
            TipoEvento.ABANDONO_ENTREVISTA: self._manejar_abandono_entrevista,
        }[evento.tipo]
        manejador(evento)

    def _nuevo_invitado(self, tipo: TipoInvitado) -> Invitado:
        p = self.parametros.p_con_auto if tipo is TipoInvitado.CON_AUTO else self.parametros.p_peaton
        invitado = Invitado(id=self._siguiente_id_invitado, tipo=tipo, hora_llegada=self.reloj, p=p)
        self.invitados[invitado.id] = invitado
        self.invitados_activos[invitado.id] = invitado
        self._siguiente_id_invitado += 1
        return invitado

    def _retirar(self, invitado: Invitado, estado: EstadoInvitado) -> None:
        invitado.estado = estado
        self.invitados_activos.pop(invitado.id, None)

    # -- llegada con auto / acreditación / estacionamiento ----------------------

    def _programar_proxima_llegada_auto(self) -> None:
        delta, rnd = self.dist_entre_llegadas_auto.generar()
        self._generado_llegada_auto = (rnd, delta)
        self.proxima_llegada_auto = self.reloj + delta
        self.calendario.programar(Evento(tiempo=self.proxima_llegada_auto, tipo=TipoEvento.LLEGADA_INVITADO_AUTO))

    def _manejar_llegada_invitado_auto(self, evento: Evento) -> None:
        invitado = self._nuevo_invitado(TipoInvitado.CON_AUTO)
        self._programar_proxima_llegada_auto()

        operario = next((o for o in self.operarios if not o.ocupado), None)
        if operario is not None:
            self._iniciar_acreditacion(operario, invitado)
        else:
            invitado.estado = EstadoInvitado.ESPERANDO_ACREDITACION
            self.cola_acreditacion.encolar(invitado.id)

    def _iniciar_acreditacion(self, operario: Operario, invitado: Invitado) -> None:
        duracion, rnd = self.dist_acreditacion.generar()
        operario.ocupar(invitado.id, self.reloj, self.reloj + duracion)
        self._generado_acreditacion[operario.id] = (rnd, duracion)
        invitado.estado = EstadoInvitado.ACREDITANDOSE
        invitado.hora_inicio_acreditacion = self.reloj
        self.calendario.programar(
            Evento(tiempo=self.reloj + duracion, tipo=TipoEvento.FIN_ACREDITACION, invitado_id=invitado.id)
        )

    def _manejar_fin_acreditacion(self, evento: Evento) -> None:
        invitado = self.invitados[evento.invitado_id]
        operario = next(o for o in self.operarios if o.invitado_actual_id == invitado.id)
        operario.liberar(self.reloj)

        invitado.estado = EstadoInvitado.ESTACIONANDO
        invitado.hora_fin_acreditacion = self.reloj
        invitado.hora_fin_estacionamiento = self.reloj + self.parametros.tiempo_estacionar
        self.calendario.programar(
            Evento(
                tiempo=invitado.hora_fin_estacionamiento,
                tipo=TipoEvento.FIN_ESTACIONAMIENTO,
                invitado_id=invitado.id,
            )
        )

        siguiente_id = self.cola_acreditacion.desencolar()
        if siguiente_id is not None:
            self._iniciar_acreditacion(operario, self.invitados[siguiente_id])

    def _manejar_fin_estacionamiento(self, evento: Evento) -> None:
        self._ingresar_a_sala(self.invitados[evento.invitado_id])

    # -- llegada peatonal / sala de degustación ---------------------------------

    def _programar_proxima_llegada_peaton(self) -> None:
        self.proxima_llegada_peaton = self.reloj + self.parametros.entre_llegadas_peaton
        self.calendario.programar(Evento(tiempo=self.proxima_llegada_peaton, tipo=TipoEvento.LLEGADA_INVITADO_PEATON))

    def _manejar_llegada_invitado_peaton(self, evento: Evento) -> None:
        invitado = self._nuevo_invitado(TipoInvitado.PEATON)
        self._programar_proxima_llegada_peaton()
        self._ingresar_a_sala(invitado)

    def _ingresar_a_sala(self, invitado: Invitado) -> None:
        duracion, rnd = self.dist_permanencia_sala.generar()
        invitado.estado = EstadoInvitado.EN_SALA_DEGUSTACION
        invitado.hora_inicio_sala = self.reloj
        invitado.rnd_permanencia_sala = rnd
        invitado.tiempo_permanencia_sala = duracion
        self.calendario.programar(
            Evento(tiempo=self.reloj + duracion, tipo=TipoEvento.FIN_PERMANENCIA_SALA, invitado_id=invitado.id)
        )

    def _manejar_fin_permanencia_sala(self, evento: Evento) -> None:
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
            invitado.hora_limite_espera = self.reloj + self.parametros.paciencia_entrevista
            self.calendario.programar(
                Evento(
                    tiempo=invitado.hora_limite_espera,
                    tipo=TipoEvento.ABANDONO_ENTREVISTA,
                    invitado_id=invitado.id,
                )
            )

    # -- entrevista de satisfacción ----------------------------------------------

    def _iniciar_entrevista(self, representante: Representante, invitado: Invitado) -> None:
        invitado.estado = EstadoInvitado.EN_ENTREVISTA
        invitado.hora_inicio_entrevista = self.reloj
        invitado.hora_limite_espera = None

        duracion_unidades, pasos = integrar_duracion_entrevista(invitado.p, self.parametros.h_integracion)
        self.integraciones[invitado.id] = pasos
        duracion_min = duracion_unidades * self.parametros.minutos_por_unidad_integracion
        representante.ocupar(invitado.id, duracion_min, self.reloj + duracion_min)
        self.calendario.programar(
            Evento(tiempo=self.reloj + duracion_min, tipo=TipoEvento.FIN_ENTREVISTA, invitado_id=invitado.id)
        )

    def _manejar_fin_entrevista(self, evento: Evento) -> None:
        invitado = self.invitados[evento.invitado_id]
        representante = next(r for r in self.representantes if r.invitado_actual_id == invitado.id)
        representante.liberar()

        invitado.hora_fin_entrevista = self.reloj
        self._retirar(invitado, EstadoInvitado.RETIRADO_CON_ENCUESTA)
        self.acumuladores.cantidad_entrevistas_completas += 1

        siguiente_id = self.cola_entrevista.desencolar()
        if siguiente_id is not None:
            self.calendario.cancelar(siguiente_id, TipoEvento.ABANDONO_ENTREVISTA)
            self._iniciar_entrevista(representante, self.invitados[siguiente_id])

    def _manejar_abandono_entrevista(self, evento: Evento) -> None:
        invitado = self.invitados[evento.invitado_id]
        self.cola_entrevista.quitar(invitado.id)
        self._retirar(invitado, EstadoInvitado.RETIRADO_SIN_ENCUESTA)
        self.acumuladores.cantidad_abandonos_entrevista += 1

    # -- vector de estado ---------------------------------------------------------

    def _ocio_hasta_ahora(self, operario: Operario) -> float:
        """Ocio acumulado incluyendo el período libre en curso."""
        if operario.ocupado:
            return operario.tiempo_ocioso_acumulado
        return operario.tiempo_ocioso_acumulado + (self.reloj - operario.hora_ultimo_cambio_estado)

    def _construir_fila(self, numero_fila: int, nombre_evento: str, invitado_evento_id: int | None) -> FilaVectorEstado:
        invitados = {inv.id: self._invitado_a_dict(inv) for inv in self.invitados_activos.values()}
        # El invitado que se retira en este evento se muestra en su última fila.
        if invitado_evento_id is not None and invitado_evento_id not in invitados:
            invitados[invitado_evento_id] = self._invitado_a_dict(self.invitados[invitado_evento_id])

        llegada_auto = {"rnd": None, "tiempo": None, "proxima": self.proxima_llegada_auto}
        if self._generado_llegada_auto is not None:
            llegada_auto["rnd"], llegada_auto["tiempo"] = self._generado_llegada_auto

        operarios = {}
        for o in self.operarios:
            rnd, tiempo = self._generado_acreditacion.get(o.id, (None, None))
            operarios[o.id] = {
                "estado": "ocupado" if o.ocupado else "libre",
                "invitado": o.invitado_actual_id,
                "rnd": rnd,
                "tiempo": tiempo,
                "fin": o.hora_fin_acreditacion,
                "ocio": self._ocio_hasta_ahora(o),
            }

        self._generado_llegada_auto = None
        self._generado_acreditacion = {}

        ac = self.acumuladores
        return FilaVectorEstado(
            numero_fila=numero_fila,
            hora_simulada=self.reloj,
            nombre_evento=nombre_evento,
            invitado_evento_id=invitado_evento_id,
            proximo_evento=self.calendario.proximo_nombre(),
            llegada_auto=llegada_auto,
            llegada_peaton={"proxima": self.proxima_llegada_peaton},
            operarios=operarios,
            representantes={
                r.id: {
                    "estado": "ocupado" if r.ocupado else "libre",
                    "invitado": r.invitado_actual_id,
                    "duracion": r.duracion_entrevista,
                    "fin": r.hora_fin_entrevista,
                }
                for r in self.representantes
            },
            colas={"acreditacion": self.cola_acreditacion.cantidad, "entrevista": self.cola_entrevista.cantidad},
            invitados=invitados,
            acumuladores={
                "maximo_tiempo_en_sala": ac.maximo_tiempo_en_sala,
                "cantidad_invitados_a_entrevista": ac.cantidad_invitados_a_entrevista,
                "cantidad_entrevistas_completas": ac.cantidad_entrevistas_completas,
                "cantidad_abandonos_entrevista": ac.cantidad_abandonos_entrevista,
                "porcentaje_abandono_entrevista": ac.porcentaje_abandono_entrevista,
                "ocio_total_operarios": sum(op["ocio"] for op in operarios.values()),
            },
        )

    @staticmethod
    def _invitado_a_dict(invitado: Invitado) -> dict:
        en_sala = invitado.estado is EstadoInvitado.EN_SALA_DEGUSTACION
        return {
            "tipo": invitado.tipo.value,
            "estado": invitado.estado.value,
            "hora_llegada": invitado.hora_llegada,
            "p": invitado.p,
            "fin_estacionamiento": invitado.hora_fin_estacionamiento
            if invitado.estado is EstadoInvitado.ESTACIONANDO
            else None,
            "hora_inicio_sala": invitado.hora_inicio_sala,
            "rnd_sala": invitado.rnd_permanencia_sala if en_sala else None,
            "tiempo_sala": invitado.tiempo_permanencia_sala if en_sala else None,
            "fin_sala": (invitado.hora_inicio_sala + invitado.tiempo_permanencia_sala) if en_sala else None,
            "hora_llegada_cola_entrevista": invitado.hora_llegada_cola_entrevista,
            "limite_espera": invitado.hora_limite_espera
            if invitado.estado is EstadoInvitado.ESPERANDO_ENTREVISTA
            else None,
        }

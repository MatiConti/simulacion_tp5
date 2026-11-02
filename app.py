"""Punto de entrada de la aplicación (Streamlit)."""
import threading
import time

import streamlit as st

from gui.estilos import aviso, encabezado_app, inyectar_css, seccion, tarjetas_kpi
from gui.exportador_excel import bytes_vector_estado
from gui.panel_parametros import panel_parametros
from gui.tabla_integracion import renderizar_tabla_integracion
from gui.tabla_vector_estado import armar_filas_con_separadores, renderizar_tabla
from simulacion import MotorSimulacion

st.set_page_config(page_title="Degustación — Simulación", layout="wide")
inyectar_css()
encabezado_app(
    "Simulación de degustación — bodega y embutidos",
    "Líneas de espera: acreditación en el portón y entrevista de satisfacción",
)

simulando = st.session_state.get("simulando", False)

with st.sidebar:
    st.markdown("### 🍷 Degustación C")
    st.caption("TP5 · Simulación · Grupo 6")
    parametros = panel_parametros(disabled=simulando)
    parametros_validos = parametros.llegada_auto_min <= parametros.llegada_auto_max
    if not parametros_validos:
        st.error("El mínimo entre llegadas con auto no puede ser mayor que el máximo.")
    columna_simular, columna_detener = st.columns([1, 1])
    with columna_simular:
        simular = st.button(
            "Simular", type="primary", use_container_width=True, disabled=simulando or not parametros_validos
        )
    with columna_detener:
        detener = st.button("Detener simulación", use_container_width=True, disabled=not simulando)

if detener and simulando:
    st.session_state["evento_detener"].set()

if simular and not simulando:
    motor_en_curso = MotorSimulacion(parametros)
    evento_detener = threading.Event()
    hilo = threading.Thread(target=motor_en_curso.ejecutar, kwargs={"debe_detenerse": evento_detener.is_set})
    hilo.start()
    st.session_state["simulando"] = True
    st.session_state["motor_en_curso"] = motor_en_curso
    st.session_state["evento_detener"] = evento_detener
    st.session_state["hilo"] = hilo
    st.session_state["parametros_en_curso"] = parametros
    st.rerun()

if simulando:
    hilo = st.session_state["hilo"]
    if hilo.is_alive():
        aviso("Simulando… los parámetros quedan bloqueados hasta que toques <b>Detener simulación</b>.")
        time.sleep(0.3)
        st.rerun()
    else:
        # El hilo ya terminó (solo o porque lo detuviste), pero los parámetros
        # siguen bloqueados hasta que vos mismo confirmes con "Detener simulación".
        motor_en_curso = st.session_state["motor_en_curso"]
        st.session_state["motor"] = motor_en_curso
        st.session_state["filas"] = motor_en_curso.filas
        st.session_state["parametros"] = st.session_state["parametros_en_curso"]
        if detener:
            st.session_state["simulando"] = False
            st.rerun()
        else:
            aviso(
                "Simulación lista. Tocá <b>Detener simulación</b> para poder "
                "volver a cambiar los parámetros."
            )

motor = st.session_state.get("motor")
filas = st.session_state.get("filas")
parametros_usados = st.session_state.get("parametros")

if motor is None:
    aviso("Configurá los parámetros en la barra lateral y presioná <b>Simular</b> para empezar.")
else:
    acumuladores = motor.acumuladores

    _ETIQUETAS_MOTIVO_CORTE = {
        "tiempo_max": "se alcanzó el tiempo máximo a simular (X)",
        "iteraciones_max": "se alcanzó el máximo de iteraciones (N)",
        "sin_mas_eventos": "no quedaban más eventos por procesar",
        "detenido_por_usuario": "se detuvo manualmente",
    }

    columna_resultados, columna_integracion = st.columns([1, 1])

    with columna_resultados:
        with seccion("resultados", "Resultados de la simulación", numero=1, altura=480):
            st.caption(
                f"Corte de la simulación: **{_ETIQUETAS_MOTIVO_CORTE.get(motor.motivo_corte, motor.motivo_corte)}** "
                f"(lo que ocurrió primero entre X e N)."
            )
            tarjetas_kpi(
                [
                    (
                        "Máximo tiempo en sala",
                        f"{acumuladores.maximo_tiempo_en_sala:.2f}",
                        "min",
                        "sobre todos los invitados",
                    ),
                    (
                        "Abandono sin encuesta",
                        f"{acumuladores.porcentaje_abandono_entrevista:.2f}",
                        "%",
                        f"{acumuladores.cantidad_abandonos_entrevista} de {acumuladores.cantidad_retirados} invitados retirados",
                    ),
                    (
                        "Tiempo ocioso promedio operarios",
                        f"{motor.tiempo_ocioso_promedio_operarios:.2f}",
                        "min",
                        f"{motor.porcentaje_ocio_operarios:.1f}% del tiempo simulado · {len(motor.operarios)} operarios",
                    ),
                    ("Filas generadas", f"{len(filas)}", "", f"{len(motor.invitados)} invitados simulados"),
                ]
            )

    with columna_integracion:
        with seccion(
            "integracion",
            "Integración numérica — duración de la entrevista",
            "Pasos de la integración de Euler (dD/dt = P/5) para el invitado elegido",
            numero=3,
            altura=480,
        ):
            ids_con_entrevista = sorted(motor.integraciones.keys())
            if ids_con_entrevista:
                invitado_id = st.selectbox(
                    "Invitado",
                    ids_con_entrevista,
                    format_func=lambda i: f"Invitado {i} ({motor.invitados[i].tipo.value}, P={motor.invitados[i].p:g})",
                )
                pasos = motor.integraciones[invitado_id]
                invitado = motor.invitados[invitado_id]
                duracion_unidades = pasos[-1].t
                st.caption(
                    f"P = {invitado.p:g}, h = {parametros_usados.h_integracion:g} — la integración corta cuando D ≥ P. "
                    f"Duración: {duracion_unidades:g} unidades × {parametros_usados.minutos_por_unidad_integracion:g} min "
                    f"= {duracion_unidades * parametros_usados.minutos_por_unidad_integracion:g} min "
                    f"(entrevista iniciada en t = {invitado.hora_inicio_entrevista:.2f})."
                )
                renderizar_tabla_integracion(pasos)
            else:
                st.caption("Todavía ningún invitado llegó a la entrevista en esta simulación.")

    caja_vector = seccion(
        "vector",
        "Vector de estado",
        "Encabezado anclado, scroll fluido y selección de fila persistente",
        numero=2,
    )
    with caja_vector:
        columna_j, columna_i, columna_boton = st.columns([1, 1, 1])
        with columna_j:
            hora_j = st.number_input(
                "Mostrar desde la hora (j)", min_value=0.0, value=float(parametros_usados.hora_inicio_vista)
            )
        with columna_i:
            cantidad_i = st.number_input(
                "Cantidad de filas (i)", min_value=1, value=int(parametros_usados.filas_a_mostrar), step=1
            )
        bloque_inicial = [f for f in filas if f.hora_simulada >= hora_j][: int(cantidad_i)]
        filas_vista = armar_filas_con_separadores([bloque_inicial, [filas[-1]]] if filas else [bloque_inicial])
        filas_exportar = [f for f in filas_vista if f is not None]
        ids_vista = {i for f in filas_exportar for i in f.invitados}
        integraciones_vista = {i: pasos for i, pasos in motor.integraciones.items() if i in ids_vista}
        with columna_boton:
            st.write("")
            st.download_button(
                "Exportar a Excel",
                data=bytes_vector_estado(filas_exportar, integraciones_vista),
                file_name="vector_estado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="boton_exportar_excel",
            )

        st.caption(
            "Se muestran i filas desde la hora j y, al final (resaltada), la fila del instante X. "
            "El Excel exporta esas mismas filas y las integraciones de Euler de los invitados que aparecen."
        )
        renderizar_tabla(filas_vista)

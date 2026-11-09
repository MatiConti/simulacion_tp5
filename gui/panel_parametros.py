"""Panel de parámetros editables (barra lateral de Streamlit)."""
from __future__ import annotations

import streamlit as st

from simulacion import ParametrosSimulacion


def panel_parametros(disabled: bool = False) -> ParametrosSimulacion:
    st.markdown("### Parámetros de la simulación")

    st.markdown("**Condición de corte**")
    tiempo_max = st.number_input("Tiempo a simular X (min)", min_value=1.0, value=480.0, disabled=disabled)
    iteraciones_max = st.number_input(
        "Máx. iteraciones N", min_value=1, max_value=100_000, value=100_000, step=1, disabled=disabled
    )

    st.markdown("**Invitados con auto**")
    llegada_auto_min = st.number_input("Entre llegadas — mín (min)", min_value=0.0, value=3.0, disabled=disabled)
    llegada_auto_max = st.number_input("Entre llegadas — máx (min)", min_value=0.0, value=7.0, disabled=disabled)
    st.caption("Distribución: Uniforme(mín, máx)")
    cantidad_operarios = st.number_input("Cantidad de operarios", min_value=1, value=3, step=1, disabled=disabled)
    media_tiempo_acreditacion = st.number_input(
        "Media tiempo de acreditación (min)", min_value=0.01, value=2.0, disabled=disabled
    )
    st.caption("Distribución: Exponencial negativa")
    tiempo_estacionar = st.number_input("Tiempo de estacionar (min)", min_value=0.0, value=3.0, disabled=disabled)
    st.caption("Constante — no es variable aleatoria")

    st.markdown("**Invitados peatonales**")
    entre_llegadas_peaton = st.number_input(
        "Entre llegadas peatón (min)", min_value=0.01, value=2.5, disabled=disabled
    )
    st.caption("Constante — no es variable aleatoria")

    st.markdown("**Sala de degustación**")
    media_permanencia_sala = st.number_input(
        "Media permanencia en sala (min)", min_value=0.01, value=20.0, disabled=disabled
    )
    st.caption("Distribución: Exponencial negativa")

    st.markdown("**Entrevista de satisfacción**")
    cantidad_representantes = st.number_input(
        "Cantidad de representantes", min_value=1, value=3, step=1, disabled=disabled
    )
    paciencia_entrevista = st.number_input(
        "Paciencia máx. en cola (min)", min_value=0.0, value=5.0, disabled=disabled
    )
    p_con_auto = st.number_input("P (con estacionamiento)", min_value=0, value=100, step=1, disabled=disabled)
    p_peaton = st.number_input("P (peatonal)", min_value=0, value=70, step=1, disabled=disabled)
    h_integracion = st.number_input(
        "Paso de integración h (Euler)", min_value=0.001, value=0.1, format="%.3f", disabled=disabled
    )
    minutos_por_unidad_integracion = st.number_input(
        "Minutos por unidad de integración", min_value=0.01, value=10.0, disabled=disabled
    )
    st.caption("Constante — integración numérica de Euler (dD/dt = P/5), no es variable aleatoria")

    return ParametrosSimulacion(
        tiempo_max=tiempo_max,
        iteraciones_max=int(iteraciones_max),
        llegada_auto_min=llegada_auto_min,
        llegada_auto_max=llegada_auto_max,
        cantidad_operarios=int(cantidad_operarios),
        media_tiempo_acreditacion=media_tiempo_acreditacion,
        tiempo_estacionar=tiempo_estacionar,
        entre_llegadas_peaton=entre_llegadas_peaton,
        media_permanencia_sala=media_permanencia_sala,
        cantidad_representantes=int(cantidad_representantes),
        paciencia_entrevista=paciencia_entrevista,
        p_con_auto=int(p_con_auto),
        p_peaton=int(p_peaton),
        h_integracion=h_integracion,
        minutos_por_unidad_integracion=minutos_por_unidad_integracion,
    )

"""Tabla compacta de los pasos de integración de Euler (t, D).

Se renderiza con `st.iframe` (mismo mecanismo que `tabla_vector_estado.py`):
un documento HTML aislado con su propio `overflow-y: auto`, para que el
encabezado (`position: sticky`) quede anclado de forma confiable, sin
depender del contenedor de Streamlit que lo rodea.
"""
from __future__ import annotations

from html import escape

import streamlit as st

from generador import PasoIntegracion

_MARINO = "#0b2545"
_BORDE = "#c8d6ea"
_TEXTO = "#10233f"


def renderizar_tabla_integracion(pasos: list[PasoIntegracion], altura: int = 280) -> None:
    filas_html = "".join(
        f"<tr><td>{escape(f'{paso.t:.3f}')}</td><td>{escape(f'{paso.d:.3f}')}</td></tr>" for paso in pasos
    )
    html = f"""
<!doctype html>
<html><head><meta charset="utf-8">
<style>
  html, body {{ height: 100%; margin: 0; overflow: hidden; font-family: Arial, sans-serif; }}
  .contenedor-integracion {{ height: 100%; overflow-y: auto; border: 1px solid {_BORDE};
    border-radius: 10px; box-sizing: border-box; }}
  table.tabla-integracion {{ border-collapse: separate; border-spacing: 0; font-size: 13px;
    width: 100%; font-variant-numeric: tabular-nums; }}
  table.tabla-integracion th, table.tabla-integracion td {{ padding: 4px 14px;
    border-bottom: 1px solid #e3eaf4; text-align: right; }}
  table.tabla-integracion thead th {{ position: sticky; top: 0; background: {_MARINO};
    color: #ffffff; font-weight: 600; z-index: 1; }}
  table.tabla-integracion tbody td {{ color: {_TEXTO}; background: #ffffff; }}
  table.tabla-integracion tbody tr:nth-child(even) td {{ background: #f4f8fd; }}
</style></head>
<body>
  <div class="contenedor-integracion">
    <table class="tabla-integracion">
      <thead><tr><th>t</th><th>D</th></tr></thead>
      <tbody>{filas_html}</tbody>
    </table>
  </div>
</body></html>
"""
    st.iframe(html, height=altura)

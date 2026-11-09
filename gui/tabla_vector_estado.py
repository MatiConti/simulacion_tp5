"""Tabla HTML del vector de estado.

Se renderiza dentro de un iframe (st.iframe) con su propio HTML/CSS/JS: el
encabezado (dos niveles: objeto y atributo) queda anclado con
`position: sticky`, el scroll es nativo del navegador (sin parpadeos) y la
selección de fila se resuelve con JavaScript puro del lado del cliente, sin
volver a ejecutar el script de Streamlit — por eso no se pierde al hacer scroll.
"""
from __future__ import annotations

from html import escape

import streamlit as st

from models import FilaVectorEstado

from .columnas_vector import Columna, calcular_columnas, grupos_consecutivos, texto_celda

_MARINO = "#0b2545"
_MARINO_2 = "#173a68"
_AZUL = "#1d5fbf"
_TEXTO = "#10233f"
_BORDE = "#c8d6ea"


def _fila_separador_html(cantidad_columnas: int) -> str:
    return "<tr class=\"separador\"><td>⋮</td>" + "<td></td>" * (cantidad_columnas - 1) + "</tr>"


def _construir_html(filas: list[FilaVectorEstado | None], columnas: list[Columna]) -> str:
    # Cada grupo alterna clase para que se distinga dónde empieza y termina.
    grupos = grupos_consecutivos(columnas)
    encabezado_grupos = "".join(
        f'<th colspan="{n}" class="g{k % 2}">{escape(g)}</th>' for k, (g, n) in enumerate(grupos)
    )
    clases_columna: list[str] = []
    for k, (_, n) in enumerate(grupos):
        clases_columna += [f"g{k % 2}" + (" inicio" if j == 0 else "") for j in range(n)]
    encabezado_columnas = "".join(
        f'<th class="{cl}">{escape(c.nombre)}</th>' for c, cl in zip(columnas, clases_columna)
    )

    filas_html = []
    for fila in filas:
        if fila is None:
            filas_html.append(_fila_separador_html(len(columnas)))
            continue
        celdas = "".join(
            f'<td class="{cl}">{escape(texto_celda(c, fila))}</td>' for c, cl in zip(columnas, clases_columna)
        )
        clase_fila = ' class="final"' if fila.es_fila_final else ""
        filas_html.append(f'<tr{clase_fila} onclick="seleccionarFila(this)">{celdas}</tr>')
    cuerpo = "".join(filas_html)

    return f"""
<!doctype html>
<html><head><meta charset="utf-8">
<style>
  html, body {{ height: 100%; margin: 0; overflow: hidden; font-family: Arial, sans-serif; }}
  .contenedor-vector {{ overflow: auto; border: 1px solid {_BORDE};
    border-radius: 10px; background: #ffffff; height: 100%; box-sizing: border-box; }}
  table.vector {{ border-collapse: separate; border-spacing: 0; font-size: 12px; margin-bottom: 1px;
    white-space: nowrap; font-variant-numeric: tabular-nums; }}
  table.vector th, table.vector td {{ padding: 4px 9px; border-right: 1px solid #e3eaf4;
    border-bottom: 1px solid #e3eaf4; }}
  table.vector thead th {{ position: sticky; text-align: center; color: #ffffff;
    font-weight: 600; z-index: 2; }}
  table.vector thead tr.grupos th {{ top: 0; }}
  table.vector thead th.g0 {{ background: {_MARINO}; }}
  table.vector thead th.g1 {{ background: {_MARINO_2}; }}
  table.vector th.inicio, table.vector td.inicio {{ border-left: 2px solid {_BORDE}; }}
  table.vector tbody td {{ background: #ffffff; color: {_TEXTO}; text-align: right; cursor: pointer; }}
  table.vector tbody tr:nth-child(even) td {{ background: #f4f8fd; }}
  table.vector tbody tr:hover td {{ background: #e3eefb; }}
  table.vector tbody tr.final td {{ background: #fff4d6; font-weight: 600; }}
  table.vector tbody tr.seleccionada td {{ background: {_AZUL} !important; color: #ffffff; }}
  table.vector tbody tr.separador td {{ background: #eef2f8; color: {_TEXTO}; text-align: center;
    font-weight: 700; cursor: default; }}
</style></head>
<body>
  <div class="contenedor-vector">
    <table class="vector">
      <thead>
        <tr class="grupos">{encabezado_grupos}</tr>
        <tr class="columnas">{encabezado_columnas}</tr>
      </thead>
      <tbody>{cuerpo}</tbody>
    </table>
  </div>
  <script>
    // La segunda fila del encabezado se ancla justo debajo de la primera.
    var alto = document.querySelector("tr.grupos").getBoundingClientRect().height;
    document.querySelectorAll("tr.columnas th").forEach(function (th) {{ th.style.top = alto + "px"; }});

    function seleccionarFila(fila) {{
      if (fila.classList.contains("separador")) return;
      fila.parentElement.querySelectorAll("tr.seleccionada").forEach(function (f) {{
        f.classList.remove("seleccionada");
      }});
      fila.classList.add("seleccionada");
    }}
  </script>
</body></html>
"""


def armar_filas_con_separadores(bloques: list[list[FilaVectorEstado]]) -> list[FilaVectorEstado | None]:
    """Concatena bloques de filas (ya ordenados), evitando duplicados y marcando
    con `None` los huecos entre bloques no contiguos (se renderiza como separador)."""
    resultado: list[FilaVectorEstado | None] = []
    vistas: set[int] = set()
    anterior: int | None = None
    for bloque in bloques:
        for fila in sorted(bloque, key=lambda f: f.numero_fila):
            if fila.numero_fila in vistas:
                continue
            if anterior is not None and fila.numero_fila > anterior + 1:
                resultado.append(None)
            resultado.append(fila)
            vistas.add(fila.numero_fila)
            anterior = fila.numero_fila
    return resultado


def renderizar_tabla(filas: list[FilaVectorEstado | None], altura: int = 520) -> None:
    columnas = calcular_columnas([f for f in filas if f is not None])
    st.iframe(_construir_html(filas, columnas), height=altura)

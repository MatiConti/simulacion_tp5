"""Tabla HTML del vector de estado.

Se renderiza dentro de un iframe (st.iframe) con su propio HTML/CSS/JS: el
encabezado queda anclado con `position: sticky`, el scroll es nativo del
navegador (sin parpadeos) y la selección de fila se resuelve con JavaScript
puro del lado del cliente, sin volver a ejecutar el script de Streamlit —
por eso no se pierde al hacer scroll.
"""
from __future__ import annotations

from html import escape

import streamlit as st

from models import FilaVectorEstado

COLUMNAS_FIJAS = ["Fila", "Hora", "Evento", "Próximos eventos"]

_MARINO = "#0b2545"
_AZUL = "#1d5fbf"
_TEXTO = "#10233f"
_BORDE = "#c8d6ea"


def _calcular_columnas(filas: list[FilaVectorEstado | None]) -> list[tuple[str, str]]:
    ids_operarios: set[int] = set()
    ids_representantes: set[int] = set()
    ids_invitados: set[int] = set()
    claves_rnd: set[str] = set()
    for fila in filas:
        if fila is None:
            continue
        ids_operarios.update(fila.operarios.keys())
        ids_representantes.update(fila.representantes.keys())
        ids_invitados.update(fila.invitados.keys())
        claves_rnd.update(fila.numeros_aleatorios.keys())

    columnas: list[tuple[str, str]] = [("fija", c) for c in COLUMNAS_FIJAS]
    columnas += [("operario", str(i)) for i in sorted(ids_operarios)]
    columnas += [("representante", str(i)) for i in sorted(ids_representantes)]
    columnas += [("invitado", str(i)) for i in sorted(ids_invitados)]
    columnas += [("rnd", c) for c in sorted(claves_rnd)]
    return columnas


def _etiqueta_columna(grupo: str, clave: str) -> str:
    return {
        "fija": clave,
        "operario": f"Operario {clave}",
        "representante": f"Representante {clave}",
        "invitado": f"Invitado {clave}",
        "rnd": f"RND {clave}",
    }[grupo]


def _estado_servidor(info: dict | None) -> str:
    if info is None:
        return ""
    return "ocupado" if info["ocupado"] else "libre"


def _valor_celda(fila: FilaVectorEstado, grupo: str, clave: str) -> str:
    if grupo == "fija":
        if clave == "Fila":
            return str(fila.numero_fila)
        if clave == "Hora":
            return f"{fila.hora_simulada:.2f}"
        if clave == "Evento":
            return fila.nombre_evento
        if clave == "Próximos eventos":
            return "; ".join(fila.proximos_eventos)
        return ""
    if grupo == "operario":
        return _estado_servidor(fila.operarios.get(int(clave)))
    if grupo == "representante":
        return _estado_servidor(fila.representantes.get(int(clave)))
    if grupo == "invitado":
        info = fila.invitados.get(int(clave))
        return info["estado"] if info else ""
    if grupo == "rnd":
        valor = fila.numeros_aleatorios.get(clave)
        return f"{valor:.4f}" if valor is not None else ""
    return ""


def _fila_separador_html(cantidad_columnas: int) -> str:
    fila_puntos = "<tr class=\"separador\"><td>⋮</td>" + "<td></td>" * (cantidad_columnas - 1) + "</tr>"
    return fila_puntos * 3


def _construir_html(filas: list[FilaVectorEstado | None], columnas: list[tuple[str, str]]) -> str:
    encabezados = "".join(f"<th>{escape(_etiqueta_columna(g, c))}</th>" for g, c in columnas)
    filas_html = []
    for fila in filas:
        if fila is None:
            filas_html.append(_fila_separador_html(len(columnas)))
            continue
        celdas = "".join(f"<td>{escape(_valor_celda(fila, g, c))}</td>" for g, c in columnas)
        filas_html.append(f'<tr onclick="seleccionarFila(this)">{celdas}</tr>')
    cuerpo = "".join(filas_html)

    return f"""
<!doctype html>
<html><head><meta charset="utf-8">
<style>
  html, body {{ height: 100%; margin: 0; overflow: hidden; font-family: Arial, sans-serif; }}
  .contenedor-vector {{ overflow-y: auto; overflow-x: auto; border: 1px solid {_BORDE};
    border-radius: 10px; background: #ffffff; height: 100%; box-sizing: border-box; }}
  table.vector {{ margin-bottom: 1px; }}
  table.vector {{ border-collapse: separate; border-spacing: 0; font-size: 12px;
    white-space: nowrap; font-variant-numeric: tabular-nums; width: 100%; }}
  table.vector th, table.vector td {{ padding: 4px 9px; border-right: 1px solid #e3eaf4;
    border-bottom: 1px solid #e3eaf4; }}
  table.vector thead th {{ position: sticky; top: 0; text-align: center; color: #ffffff;
    font-weight: 600; background: {_MARINO}; z-index: 1; }}
  table.vector tbody td {{ background: #ffffff; color: {_TEXTO}; text-align: right; cursor: pointer; }}
  table.vector tbody tr:nth-child(even) td {{ background: #f4f8fd; }}
  table.vector tbody tr:hover td {{ background: #e3eefb; }}
  table.vector tbody tr.seleccionada td {{ background: {_AZUL} !important; color: #ffffff; }}
  table.vector tbody tr.separador td {{ background: #eef2f8; color: {_TEXTO}; text-align: center;
    font-weight: 700; cursor: default; }}
</style></head>
<body>
  <div class="contenedor-vector">
    <table class="vector">
      <thead><tr>{encabezados}</tr></thead>
      <tbody>{cuerpo}</tbody>
    </table>
  </div>
  <script>
    function seleccionarFila(fila) {{
      var filas = fila.parentElement.querySelectorAll("tr");
      filas.forEach(function (f) {{ f.classList.remove("seleccionada"); }});
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


def renderizar_tabla(filas: list[FilaVectorEstado | None], altura: int = 480) -> None:
    columnas = _calcular_columnas(filas)
    html_tabla = _construir_html(filas, columnas)
    st.iframe(html_tabla, height=altura)
